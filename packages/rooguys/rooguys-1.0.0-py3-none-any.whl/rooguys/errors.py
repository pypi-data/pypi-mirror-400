"""
Rooguys SDK Error Classes
Typed exception classes for different API error scenarios
"""

from typing import Optional, Dict, List, Any


class RooguysError(Exception):
    """Base exception for all Rooguys SDK errors"""
    
    def __init__(
        self,
        message: str,
        code: str = 'UNKNOWN_ERROR',
        request_id: Optional[str] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation"""
        return {
            'name': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'request_id': self.request_id,
            'status_code': self.status_code,
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r}, status_code={self.status_code})"


class ValidationError(RooguysError):
    """
    Validation error (HTTP 400)
    Thrown when request validation fails
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'VALIDATION_ERROR',
        request_id: Optional[str] = None,
        field_errors: Optional[List[Dict[str, str]]] = None
    ):
        super().__init__(message, code, request_id, status_code=400)
        self.field_errors = field_errors
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['field_errors'] = self.field_errors
        return result


class AuthenticationError(RooguysError):
    """
    Authentication error (HTTP 401)
    Thrown when API key is invalid or missing
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'AUTHENTICATION_ERROR',
        request_id: Optional[str] = None
    ):
        super().__init__(message, code, request_id, status_code=401)


class ForbiddenError(RooguysError):
    """
    Forbidden error (HTTP 403)
    Thrown when access is denied
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'FORBIDDEN',
        request_id: Optional[str] = None
    ):
        super().__init__(message, code, request_id, status_code=403)


class NotFoundError(RooguysError):
    """
    Not found error (HTTP 404)
    Thrown when requested resource doesn't exist
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'NOT_FOUND',
        request_id: Optional[str] = None
    ):
        super().__init__(message, code, request_id, status_code=404)


class ConflictError(RooguysError):
    """
    Conflict error (HTTP 409)
    Thrown when resource already exists or state conflict
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'CONFLICT',
        request_id: Optional[str] = None
    ):
        super().__init__(message, code, request_id, status_code=409)


class RateLimitError(RooguysError):
    """
    Rate limit error (HTTP 429)
    Thrown when rate limit is exceeded
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'RATE_LIMIT_EXCEEDED',
        request_id: Optional[str] = None,
        retry_after: int = 60
    ):
        super().__init__(message, code, request_id, status_code=429)
        self.retry_after = retry_after
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['retry_after'] = self.retry_after
        return result


class ServerError(RooguysError):
    """
    Server error (HTTP 500+)
    Thrown when server encounters an error
    """
    
    def __init__(
        self,
        message: str,
        code: str = 'SERVER_ERROR',
        request_id: Optional[str] = None,
        status_code: int = 500
    ):
        super().__init__(message, code, request_id, status_code)


def map_status_to_error(
    status: int,
    error_body: Optional[Dict[str, Any]],
    request_id: Optional[str],
    headers: Optional[Dict[str, str]] = None
) -> RooguysError:
    """
    Map HTTP status code to appropriate error class
    
    Args:
        status: HTTP status code
        error_body: Error response body
        request_id: Request ID from response
        headers: Response headers
    
    Returns:
        Appropriate RooguysError subclass instance
    """
    headers = headers or {}
    error_body = error_body or {}
    
    # Extract error message from various formats
    error_obj = error_body.get('error', {})
    if isinstance(error_obj, str):
        message = error_obj
        code = 'UNKNOWN_ERROR'
        field_errors = None
    else:
        message = (
            error_obj.get('message') or 
            error_body.get('message') or 
            error_body.get('error') or 
            'An error occurred'
        )
        code = error_obj.get('code') or error_body.get('code') or 'UNKNOWN_ERROR'
        field_errors = error_obj.get('details') or error_body.get('details')
    
    if status == 400:
        return ValidationError(message, code, request_id, field_errors)
    elif status == 401:
        return AuthenticationError(message, code, request_id)
    elif status == 403:
        return ForbiddenError(message, code, request_id)
    elif status == 404:
        return NotFoundError(message, code, request_id)
    elif status == 409:
        return ConflictError(message, code, request_id)
    elif status == 429:
        retry_after_str = headers.get('retry-after') or headers.get('Retry-After') or '60'
        try:
            retry_after = int(retry_after_str)
        except (ValueError, TypeError):
            retry_after = 60
        return RateLimitError(message, code, request_id, retry_after)
    elif status >= 500:
        return ServerError(message, code, request_id, status)
    else:
        return RooguysError(message, code, request_id, status)
