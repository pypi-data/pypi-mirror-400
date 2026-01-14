"""
Rooguys SDK HTTP Client
Handles standardized response format, rate limit headers, and error mapping
"""

import time
import requests
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from .errors import (
    RooguysError,
    RateLimitError,
    map_status_to_error,
)


@dataclass
class RateLimitInfo:
    """Rate limit information extracted from response headers"""
    limit: int
    remaining: int
    reset: int  # Unix timestamp when limit resets


@dataclass
class ApiResponse:
    """API response wrapper with metadata"""
    data: Any
    request_id: Optional[str]
    rate_limit: RateLimitInfo
    pagination: Optional[Dict[str, Any]] = None


def extract_rate_limit_info(headers: Dict[str, str]) -> RateLimitInfo:
    """
    Extract rate limit information from response headers
    
    Args:
        headers: Response headers (case-insensitive dict from requests)
    
    Returns:
        RateLimitInfo with limit, remaining, and reset values
    """
    def get_header(name: str) -> Optional[str]:
        # requests.Response.headers is case-insensitive
        return headers.get(name) or headers.get(name.lower())
    
    limit_str = get_header('X-RateLimit-Limit') or '1000'
    remaining_str = get_header('X-RateLimit-Remaining') or '1000'
    reset_str = get_header('X-RateLimit-Reset') or '0'
    
    try:
        limit = int(limit_str)
    except (ValueError, TypeError):
        limit = 1000
    
    try:
        remaining = int(remaining_str)
    except (ValueError, TypeError):
        remaining = 1000
    
    try:
        reset = int(reset_str)
    except (ValueError, TypeError):
        reset = 0
    
    return RateLimitInfo(limit=limit, remaining=remaining, reset=reset)


def extract_request_id(headers: Dict[str, str], body: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Extract request ID from response headers or body
    
    Args:
        headers: Response headers
        body: Response body
    
    Returns:
        Request ID string or None
    """
    # Try headers first
    header_request_id = headers.get('X-Request-Id') or headers.get('x-request-id')
    if header_request_id:
        return header_request_id
    
    # Fall back to body
    if body:
        return body.get('request_id') or body.get('requestId')
    
    return None


def parse_response_body(body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse standardized API response format
    Handles both new format { success: true, data: {...} } and legacy format
    
    Args:
        body: Response body
    
    Returns:
        Parsed response with data and metadata
    """
    if body is None:
        return {
            'data': None,
            'pagination': None,
            'request_id': None,
        }
    
    # If body is not a dict, return as-is (legacy format)
    if not isinstance(body, dict):
        return {
            'data': body,
            'pagination': None,
            'request_id': None,
        }
    
    # New standardized format
    if isinstance(body.get('success'), bool):
        if body['success']:
            # If there's a 'data' field, extract it
            if 'data' in body:
                return {
                    'data': body.get('data'),
                    'pagination': body.get('pagination'),
                    'request_id': body.get('request_id'),
                }
            # Otherwise, return the full body (legacy format with success flag)
            return {
                'data': body,
                'pagination': body.get('pagination'),
                'request_id': body.get('request_id'),
            }
        # Error response in standardized format
        return {
            'error': body.get('error'),
            'request_id': body.get('request_id'),
        }
    
    # Legacy format - return as-is
    return {
        'data': body,
        'pagination': body.get('pagination') if isinstance(body, dict) else None,
        'request_id': None,
    }


class HttpClient:
    """HTTP Client class for making API requests"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://api.rooguys.com/v1',
        timeout: int = 10,
        on_rate_limit_warning: Optional[Callable[[RateLimitInfo], None]] = None,
        auto_retry: bool = False,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize HTTP client
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            on_rate_limit_warning: Callback when rate limit is at 80%
            auto_retry: Enable auto-retry for rate-limited requests
            max_retries: Maximum number of retries
            retry_delay: Base delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.on_rate_limit_warning = on_rate_limit_warning
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json',
        })
    
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        _retry_count: int = 0
    ) -> ApiResponse:
        """
        Make an HTTP request with optional auto-retry for rate limits
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API endpoint path
            params: Query parameters
            body: Request body
            headers: Additional headers
            idempotency_key: Idempotency key for POST requests
            _retry_count: Current retry attempt (internal use)
        
        Returns:
            ApiResponse with data and metadata
        
        Raises:
            RooguysError: On API errors
        """
        url = f"{self.base_url}{path}"
        
        # Build request headers
        request_headers = dict(headers or {})
        
        # Add idempotency key if provided
        if idempotency_key:
            request_headers['X-Idempotency-Key'] = idempotency_key
        
        # Filter out None values from params
        filtered_params = {}
        if params:
            for key, value in params.items():
                if value is not None:
                    filtered_params[key] = value
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=body,
                params=filtered_params if filtered_params else None,
                headers=request_headers if request_headers else None,
                timeout=self.timeout
            )
            
            # Extract rate limit info
            rate_limit = extract_rate_limit_info(dict(response.headers))
            
            # Check for rate limit warning (80% consumed)
            if rate_limit.remaining < rate_limit.limit * 0.2 and self.on_rate_limit_warning:
                self.on_rate_limit_warning(rate_limit)
            
            # Parse response body
            try:
                response_body = response.json()
            except ValueError:
                response_body = {}
            
            request_id = extract_request_id(dict(response.headers), response_body)
            
            # Handle error responses
            if not response.ok:
                error = map_status_to_error(
                    response.status_code,
                    response_body,
                    request_id,
                    dict(response.headers)
                )
                
                # Auto-retry for rate limit errors if enabled
                if (
                    self.auto_retry and 
                    isinstance(error, RateLimitError) and 
                    _retry_count < self.max_retries
                ):
                    time.sleep(error.retry_after)
                    return self.request(
                        method, path, params, body, headers, 
                        idempotency_key, _retry_count + 1
                    )
                
                raise error
            
            # Parse successful response
            parsed = parse_response_body(response_body)
            
            # Check for error in standardized format
            if 'error' in parsed and parsed['error']:
                raise map_status_to_error(400, {'error': parsed['error']}, request_id, {})
            
            return ApiResponse(
                data=parsed.get('data'),
                request_id=request_id or parsed.get('request_id'),
                rate_limit=rate_limit,
                pagination=parsed.get('pagination'),
            )
        
        except requests.exceptions.Timeout:
            raise RooguysError('Request timeout', code='TIMEOUT', status_code=408)
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                # This shouldn't happen since we handle response.ok above
                raise
            raise RooguysError(str(e) or 'Network error', code='NETWORK_ERROR', status_code=0)
    
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ApiResponse:
        """Convenience method for GET requests"""
        return self.request('GET', path, params=params, **kwargs)
    
    def post(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ApiResponse:
        """Convenience method for POST requests"""
        return self.request('POST', path, body=body, **kwargs)
    
    def put(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ApiResponse:
        """Convenience method for PUT requests"""
        return self.request('PUT', path, body=body, **kwargs)
    
    def patch(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ApiResponse:
        """Convenience method for PATCH requests"""
        return self.request('PATCH', path, body=body, **kwargs)
    
    def delete(
        self,
        path: str,
        **kwargs
    ) -> ApiResponse:
        """Convenience method for DELETE requests"""
        return self.request('DELETE', path, **kwargs)
