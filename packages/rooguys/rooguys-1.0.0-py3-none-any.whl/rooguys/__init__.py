"""
Rooguys SDK for Python
Official Python SDK for the Rooguys Gamification API
"""

from .client import (
    Rooguys,
    RooguysApiError,  # Backward compatibility alias
)

from .errors import (
    RooguysError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
    map_status_to_error,
)

from .http_client import (
    HttpClient,
    RateLimitInfo,
    ApiResponse,
    extract_rate_limit_info,
    extract_request_id,
    parse_response_body,
)

__all__ = [
    # Main client
    'Rooguys',
    
    # Error classes
    'RooguysError',
    'RooguysApiError',  # Backward compatibility
    'ValidationError',
    'AuthenticationError',
    'ForbiddenError',
    'NotFoundError',
    'ConflictError',
    'RateLimitError',
    'ServerError',
    'map_status_to_error',
    
    # HTTP client utilities
    'HttpClient',
    'RateLimitInfo',
    'ApiResponse',
    'extract_rate_limit_info',
    'extract_request_id',
    'parse_response_body',
]

__version__ = '0.2.0'
