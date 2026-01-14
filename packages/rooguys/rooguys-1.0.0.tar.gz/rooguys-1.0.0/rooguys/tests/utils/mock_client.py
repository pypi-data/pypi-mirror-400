"""Mock HTTP client utilities for testing"""
from unittest.mock import MagicMock
from typing import Dict, Any, Optional, List


def create_mock_session():
    """Create a mock requests.Session for testing"""
    session = MagicMock()
    session.request = MagicMock()
    session.headers = {}
    return session


def mock_success_response(data: Dict[str, Any], status_code: int = 200, headers: Optional[Dict[str, str]] = None):
    """Create a mock successful response"""
    response = MagicMock()
    response.status_code = status_code
    response.ok = True
    response.json.return_value = data
    response.raise_for_status = MagicMock()
    
    # Set up headers
    default_headers = {
        'X-RateLimit-Limit': '1000',
        'X-RateLimit-Remaining': '999',
        'X-RateLimit-Reset': '1704067200',
    }
    if headers:
        default_headers.update(headers)
    response.headers = default_headers
    
    return response


def mock_error_response(
    status_code: int,
    message: str,
    details: Optional[List[Dict]] = None,
    headers: Optional[Dict[str, str]] = None
):
    """Create a mock error response"""
    import requests
    
    response = MagicMock()
    response.status_code = status_code
    response.ok = False  # Important: set ok to False for error responses
    
    error_data = {'error': message}
    if details:
        error_data['details'] = details
    
    response.json.return_value = error_data
    
    # Set up headers
    default_headers = {
        'X-RateLimit-Limit': '1000',
        'X-RateLimit-Remaining': '999',
        'X-RateLimit-Reset': '1704067200',
    }
    if headers:
        default_headers.update(headers)
    response.headers = default_headers
    
    # Create HTTPError
    error = requests.exceptions.HTTPError(message)
    error.response = response
    response.raise_for_status.side_effect = error
    
    return response


def mock_network_error(message: str = 'Network error'):
    """Create a mock network error"""
    import requests
    return requests.exceptions.RequestException(message)


def mock_timeout_error():
    """Create a mock timeout error"""
    import requests
    return requests.exceptions.Timeout('Request timed out')
