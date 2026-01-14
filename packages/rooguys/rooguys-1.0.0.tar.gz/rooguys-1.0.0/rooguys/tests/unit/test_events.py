"""Unit tests for events resource"""
import pytest
from unittest.mock import patch, MagicMock
from rooguys import Rooguys, RooguysApiError, RooguysError
from rooguys.tests.utils import (
    create_mock_session,
    mock_success_response,
    mock_error_response,
    mock_timeout_error,
)
from rooguys.tests.fixtures import mock_responses, mock_errors


class TestEventsResource:
    """Test suite for events resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')
        self.api_key = 'test-api-key'

    @patch('requests.Session.request')
    def test_track_event_with_valid_inputs(self, mock_request):
        """Should track an event with valid inputs"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        result = self.client.events.track(
            'purchase_completed',
            'user_123',
            {'amount': 50.0}
        )

        assert result == mock_responses['track_event_response']
        # Verify the request was made to the new /events endpoint
        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'POST'
        assert '/events' in call_args[1]['url']
        assert call_args[1]['json']['event_name'] == 'purchase_completed'
        assert call_args[1]['json']['user_id'] == 'user_123'
        assert call_args[1]['json']['properties'] == {'amount': 50.0}

    @patch('requests.Session.request')
    def test_track_event_with_empty_properties(self, mock_request):
        """Should track an event with empty properties"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        result = self.client.events.track('user_login', 'user_456')

        assert result == mock_responses['track_event_response']
        call_args = mock_request.call_args
        assert call_args[1]['json']['properties'] == {}

    @patch('requests.Session.request')
    def test_track_event_with_include_profile(self, mock_request):
        """Should include profile when includeProfile is true"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_with_profile_response']
        )

        result = self.client.events.track(
            'purchase_completed',
            'user_123',
            {'amount': 50.0},
            {'include_profile': True}
        )

        assert result == mock_responses['track_event_with_profile_response']
        assert 'profile' in result
        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'include_profile': 'true'}

    @patch('requests.Session.request')
    def test_track_event_with_special_characters_in_event_name(self, mock_request):
        """Should handle special characters in event name"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('user-signup_v2', 'user_123')

        call_args = mock_request.call_args
        assert call_args[1]['json']['event_name'] == 'user-signup_v2'

    @patch('requests.Session.request')
    def test_track_event_with_special_characters_in_user_id(self, mock_request):
        """Should handle special characters in user ID"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('user_login', 'user@example.com')

        call_args = mock_request.call_args
        assert call_args[1]['json']['user_id'] == 'user@example.com'

    @patch('requests.Session.request')
    def test_track_event_with_complex_nested_properties(self, mock_request):
        """Should handle complex nested properties"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        complex_properties = {
            'order': {
                'id': 'order_123',
                'items': [
                    {'sku': 'ITEM1', 'quantity': 2},
                    {'sku': 'ITEM2', 'quantity': 1},
                ],
                'total': 150.0,
            },
            'metadata': {
                'source': 'mobile_app',
                'version': '2.1.0',
            },
        }

        self.client.events.track('order_placed', 'user_123', complex_properties)

        call_args = mock_request.call_args
        assert call_args[1]['json']['properties'] == complex_properties

    @patch('requests.Session.request')
    def test_track_event_throws_error_on_400(self, mock_request):
        """Should throw error when API returns 400"""
        mock_request.return_value = mock_error_response(
            400,
            'Validation failed',
            mock_errors['validation_error']['details']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('', 'user_123')

        assert 'Validation failed' in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @patch('requests.Session.request')
    def test_track_event_throws_error_on_500(self, mock_request):
        """Should throw error when API returns 500"""
        mock_request.return_value = mock_error_response(
            500,
            'Internal server error'
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('user_login', 'user_123')

        assert 'Internal server error' in str(exc_info.value)
        assert exc_info.value.status_code == 500

    @patch('requests.Session.request')
    def test_track_event_throws_error_on_503_queue_full(self, mock_request):
        """Should throw error when API returns 503 (queue full)"""
        mock_request.return_value = mock_error_response(
            503,
            mock_errors['queue_full_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.events.track('user_login', 'user_123')

        assert 'Event queue is full' in str(exc_info.value)
        assert exc_info.value.status_code == 503

    @patch('requests.Session.request')
    def test_track_event_handles_network_timeout(self, mock_request):
        """Should handle network timeout"""
        mock_request.side_effect = mock_timeout_error()

        with pytest.raises(RooguysError) as exc_info:
            self.client.events.track('user_login', 'user_123')

        # Check for timeout-related message
        error_msg = str(exc_info.value).lower()
        assert 'timeout' in error_msg

    @patch('requests.Session.request')
    def test_track_event_with_null_values(self, mock_request):
        """Should handle properties with null values"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('user_updated', 'user_123', {
            'email': 'user@example.com',
            'phone': None,
            'address': None,
        })

        call_args = mock_request.call_args
        assert call_args[1]['json']['properties'] == {
            'email': 'user@example.com',
            'phone': None,
            'address': None,
        }

    @patch('requests.Session.request')
    def test_track_event_with_boolean_values(self, mock_request):
        """Should handle properties with boolean values"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('feature_toggled', 'user_123', {
            'feature_name': 'dark_mode',
            'enabled': True,
        })

        call_args = mock_request.call_args
        assert call_args[1]['json']['properties']['enabled'] is True

    @patch('requests.Session.request')
    def test_track_event_with_numeric_values(self, mock_request):
        """Should handle properties with numeric values"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('score_updated', 'user_123', {
            'score': 1500,
            'multiplier': 1.5,
            'rank': 42,
        })

        call_args = mock_request.call_args
        assert call_args[1]['json']['properties'] == {
            'score': 1500,
            'multiplier': 1.5,
            'rank': 42,
        }

    @patch('requests.Session.request')
    def test_track_event_with_empty_string_properties(self, mock_request):
        """Should handle empty string properties"""
        mock_request.return_value = mock_success_response(
            mock_responses['track_event_response']
        )

        self.client.events.track('form_submitted', 'user_123', {
            'name': 'John Doe',
            'comment': '',
        })

        call_args = mock_request.call_args
        assert call_args[1]['json']['properties']['comment'] == ''
