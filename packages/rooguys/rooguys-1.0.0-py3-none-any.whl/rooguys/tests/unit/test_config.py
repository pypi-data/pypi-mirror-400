"""Unit tests for SDK configuration"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys


class TestSDKConfiguration:
    """Test suite for SDK configuration"""

    def test_initialize_with_api_key(self):
        """Should initialize with API key"""
        client = Rooguys('test-api-key')

        assert client.api_key == 'test-api-key'

    def test_use_default_base_url(self):
        """Should use default base URL when not provided"""
        client = Rooguys('test-api-key')

        assert client.base_url == 'https://api.rooguys.com/v1'

    def test_use_custom_base_url(self):
        """Should use custom base URL when provided"""
        client = Rooguys('test-api-key', {
            'base_url': 'https://custom.api.com/v1',
        })

        assert client.base_url == 'https://custom.api.com/v1'

    def test_use_default_timeout(self):
        """Should use default timeout when not provided"""
        client = Rooguys('test-api-key')

        assert client.timeout == 10

    def test_use_custom_timeout(self):
        """Should use custom timeout when provided"""
        client = Rooguys('test-api-key', {
            'timeout': 30,
        })

        assert client.timeout == 30

    def test_accept_both_base_url_and_timeout(self):
        """Should accept both baseUrl and timeout options"""
        client = Rooguys('test-api-key', {
            'base_url': 'https://staging.api.com/v1',
            'timeout': 20,
        })

        assert client.base_url == 'https://staging.api.com/v1'
        assert client.timeout == 20

    def test_handle_empty_options(self):
        """Should handle empty options object"""
        client = Rooguys('test-api-key', {})

        assert client.base_url == 'https://api.rooguys.com/v1'
        assert client.timeout == 10

    def test_handle_none_options(self):
        """Should handle None options"""
        client = Rooguys('test-api-key', None)

        assert client.base_url == 'https://api.rooguys.com/v1'
        assert client.timeout == 10

    def test_handle_localhost_base_url(self):
        """Should handle localhost base URL"""
        client = Rooguys('test-api-key', {
            'base_url': 'http://localhost:3001/v1',
        })

        assert client.base_url == 'http://localhost:3001/v1'

    def test_set_api_key_header(self):
        """Should set API key in session headers"""
        client = Rooguys('my-secret-key')

        assert client.session.headers['x-api-key'] == 'my-secret-key'

    def test_set_content_type_header(self):
        """Should set Content-Type header"""
        client = Rooguys('test-api-key')

        assert client.session.headers['Content-Type'] == 'application/json'

    def test_handle_long_api_key(self):
        """Should handle long API keys"""
        long_key = 'sk_live_' + 'a' * 100
        client = Rooguys(long_key)

        assert client.api_key == long_key
        assert client.session.headers['x-api-key'] == long_key

    def test_handle_api_key_with_special_characters(self):
        """Should handle API keys with special characters"""
        key_with_special_chars = 'sk_test_abc-123_XYZ.456'
        client = Rooguys(key_with_special_chars)

        assert client.api_key == key_with_special_chars

    @patch('requests.Session.request')
    def test_api_key_included_in_requests(self, mock_request):
        """Should include API key in all requests"""
        from rooguys.tests.utils import mock_success_response

        client = Rooguys('my-secret-key')
        mock_request.return_value = mock_success_response({'status': 'queued'})

        client.events.track('test', 'user1')

        # Verify session headers contain the API key
        assert client.session.headers['x-api-key'] == 'my-secret-key'
