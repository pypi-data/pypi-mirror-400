"""Unit tests for error handling"""
import pytest
from unittest.mock import patch
import requests
from rooguys import Rooguys, RooguysApiError, RooguysError
from rooguys.tests.utils import mock_error_response, mock_timeout_error, mock_network_error
from rooguys.tests.fixtures import mock_errors


class TestErrorHandling:
    """Test suite for error handling"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_400_bad_request_error(self, mock_request):
        """Should throw error with message for 400 Bad Request"""
        mock_request.return_value = mock_error_response(400, 'Bad Request')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('test', 'user1')

        assert 'Bad Request' in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @patch('requests.Session.request')
    def test_401_unauthorized_error(self, mock_request):
        """Should throw error with message for 401 Unauthorized"""
        mock_request.return_value = mock_error_response(
            401, mock_errors['unauthorized_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.users.get('user1')

        assert 'Invalid or missing API key' in str(exc_info.value)
        assert exc_info.value.status_code == 401

    @patch('requests.Session.request')
    def test_404_not_found_error(self, mock_request):
        """Should throw error with message for 404 Not Found"""
        mock_request.return_value = mock_error_response(
            404, mock_errors['not_found_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.users.get('nonexistent')

        # Check that the error message contains user-related text
        error_msg = str(exc_info.value).lower()
        assert 'user' in error_msg or 'not found' in error_msg
        assert exc_info.value.status_code == 404

    @patch('requests.Session.request')
    def test_validation_error_with_details(self, mock_request):
        """Should include validation details in error"""
        mock_request.return_value = mock_error_response(
            400, 'Validation failed', mock_errors['validation_error']['details']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('', 'user1')

        assert 'Validation failed' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_429_rate_limit_error(self, mock_request):
        """Should throw error for 429 Too Many Requests"""
        mock_request.return_value = mock_error_response(429, 'Rate limit exceeded')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.users.get('user1')

        assert 'Rate limit exceeded' in str(exc_info.value)
        assert exc_info.value.status_code == 429

    @patch('requests.Session.request')
    def test_500_internal_server_error(self, mock_request):
        """Should throw error with message for 500 Internal Server Error"""
        mock_request.return_value = mock_error_response(500, 'Internal server error')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('test', 'user1')

        assert 'Internal server error' in str(exc_info.value)
        assert exc_info.value.status_code == 500

    @patch('requests.Session.request')
    def test_503_service_unavailable_error(self, mock_request):
        """Should throw error with message for 503 Service Unavailable"""
        mock_request.return_value = mock_error_response(
            503, mock_errors['queue_full_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('test', 'user1')

        assert 'Event queue is full' in str(exc_info.value)
        assert exc_info.value.status_code == 503

    @patch('requests.Session.request')
    def test_502_bad_gateway_error(self, mock_request):
        """Should throw error for 502 Bad Gateway"""
        mock_request.return_value = mock_error_response(502, 'Bad Gateway')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.users.get('user1')

        assert 'Bad Gateway' in str(exc_info.value)
        assert exc_info.value.status_code == 502

    @patch('requests.Session.request')
    def test_network_timeout_error(self, mock_request):
        """Should throw error for network timeout"""
        mock_request.side_effect = mock_timeout_error()

        with pytest.raises(RooguysError) as exc_info:
            self.client.events.track('test', 'user1')

        # Check for timeout-related message
        error_msg = str(exc_info.value).lower()
        assert 'timeout' in error_msg

    @patch('requests.Session.request')
    def test_connection_error(self, mock_request):
        """Should throw error for connection failure"""
        mock_request.side_effect = mock_network_error('Connection refused')

        with pytest.raises(RooguysError) as exc_info:
            self.client.users.get('user1')

        assert 'Connection refused' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_dns_lookup_failure(self, mock_request):
        """Should throw error for DNS lookup failure"""
        mock_request.side_effect = mock_network_error('Name or service not known')

        with pytest.raises(RooguysError) as exc_info:
            self.client.users.get('user1')

        assert 'Name or service not known' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_response_without_error_message(self, mock_request):
        """Should handle response without error message"""
        response = mock_error_response(500, '')
        # Override json to return empty dict
        response.json.return_value = {}
        mock_request.return_value = response

        with pytest.raises(RooguysApiError):
            self.client.events.track('test', 'user1')

    @patch('requests.Session.request')
    def test_response_with_invalid_json(self, mock_request):
        """Should handle response with invalid JSON"""
        response = mock_error_response(500, 'Internal server error')
        # Make json() raise ValueError
        response.json.side_effect = ValueError('Invalid JSON')
        mock_request.return_value = response

        with pytest.raises(RooguysApiError):
            self.client.events.track('test', 'user1')

    @patch('requests.Session.request')
    def test_error_detail_preservation(self, mock_request):
        """Should preserve error details from API response"""
        mock_request.return_value = mock_error_response(
            400,
            'Validation failed',
            [
                {'field': 'user_id', 'message': 'User ID is required'},
                {'field': 'event_name', 'message': 'Event name is required'},
            ],
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('', '')

        assert 'Validation failed' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_nested_error_details(self, mock_request):
        """Should handle errors with nested details"""
        mock_request.return_value = mock_error_response(
            400,
            'Complex validation error',
            {'errors': {'properties': {'amount': 'Must be a positive number'}}},
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('test', 'user1')

        assert 'Complex validation error' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_generic_request_exception(self, mock_request):
        """Should handle generic request exceptions"""
        mock_request.side_effect = requests.exceptions.RequestException('Generic error')

        with pytest.raises(RooguysError) as exc_info:
            self.client.users.get('user1')

        assert 'Generic error' in str(exc_info.value)
