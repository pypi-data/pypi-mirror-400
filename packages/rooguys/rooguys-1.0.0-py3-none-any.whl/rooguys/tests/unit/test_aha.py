"""Unit tests for Aha Score resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures.responses import mock_responses, mock_errors


class TestAhaResource:
    """Test Aha Score resource methods"""

    def setup_method(self):
        """Set up test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_declare_with_valid_value(self, mock_request):
        """Test declaring aha score with valid value"""
        mock_request.return_value = mock_success_response(
            mock_responses['aha_declaration_response']
        )

        result = self.client.aha.declare('user123', 4)

        call_args = mock_request.call_args
        assert call_args[1]['json']['user_id'] == 'user123'
        assert call_args[1]['json']['value'] == 4
        # The response doesn't have a 'data' field, so result is the full response
        # (legacy format handling)
        assert result == mock_responses['aha_declaration_response']

    @patch('requests.Session.request')
    def test_declare_with_value_1(self, mock_request):
        """Test declaring aha score with minimum value"""
        mock_request.return_value = mock_success_response(
            mock_responses['aha_declaration_response']
        )

        result = self.client.aha.declare('user123', 1)

        call_args = mock_request.call_args
        assert call_args[1]['json']['value'] == 1
        # The response doesn't have a 'data' field, so result is the full response
        assert result == mock_responses['aha_declaration_response']

    @patch('requests.Session.request')
    def test_declare_with_value_5(self, mock_request):
        """Test declaring aha score with maximum value"""
        mock_request.return_value = mock_success_response(
            mock_responses['aha_declaration_response']
        )

        result = self.client.aha.declare('user123', 5)

        call_args = mock_request.call_args
        assert call_args[1]['json']['value'] == 5
        # The response doesn't have a 'data' field, so result is the full response
        assert result == mock_responses['aha_declaration_response']

    def test_declare_with_value_0_raises_error(self):
        """Test declaring aha score with value 0 raises ValueError"""
        with pytest.raises(ValueError, match='Aha score value must be an integer between 1 and 5'):
            self.client.aha.declare('user123', 0)

    def test_declare_with_value_6_raises_error(self):
        """Test declaring aha score with value 6 raises ValueError"""
        with pytest.raises(ValueError, match='Aha score value must be an integer between 1 and 5'):
            self.client.aha.declare('user123', 6)

    def test_declare_with_negative_value_raises_error(self):
        """Test declaring aha score with negative value raises ValueError"""
        with pytest.raises(ValueError, match='Aha score value must be an integer between 1 and 5'):
            self.client.aha.declare('user123', -1)

    def test_declare_with_non_integer_raises_error(self):
        """Test declaring aha score with non-integer raises ValueError"""
        with pytest.raises(ValueError, match='Aha score value must be an integer between 1 and 5'):
            self.client.aha.declare('user123', 3.5)

    def test_declare_with_string_raises_error(self):
        """Test declaring aha score with string raises ValueError"""
        with pytest.raises(ValueError, match='Aha score value must be an integer between 1 and 5'):
            self.client.aha.declare('user123', '3')

    @patch('requests.Session.request')
    def test_declare_handles_api_error(self, mock_request):
        """Test declaring aha score handles API error"""
        mock_request.return_value = mock_error_response(
            400, 'Validation failed', mock_errors['aha_value_error'].get('details')
        )

        with pytest.raises(RooguysApiError):
            self.client.aha.declare('user123', 3)

    @patch('requests.Session.request')
    def test_get_user_score_success(self, mock_request):
        """Test getting user aha score successfully"""
        # The SDK extracts the 'data' field from standardized responses
        mock_request.return_value = mock_success_response(
            mock_responses['aha_score_response']
        )

        result = self.client.aha.get_user_score('user123')

        call_args = mock_request.call_args
        assert '/users/user123/aha' in call_args[1]['url']
        # Result is the data portion of the response
        assert result['user_id'] == 'user123'

    @patch('requests.Session.request')
    def test_get_user_score_parses_all_fields(self, mock_request):
        """Test getting user aha score parses all fields correctly"""
        # The SDK extracts the 'data' field from standardized responses
        mock_request.return_value = mock_success_response(
            mock_responses['aha_score_response']
        )

        result = self.client.aha.get_user_score('user123')

        # Result is the data portion of the response
        assert result['user_id'] == 'user123'
        assert result['current_score'] == 75
        assert result['declarative_score'] == 80
        assert result['inferred_score'] == 70
        assert result['status'] == 'activated'

    @patch('requests.Session.request')
    def test_get_user_score_preserves_history(self, mock_request):
        """Test getting user aha score preserves history structure"""
        mock_request.return_value = mock_success_response(
            mock_responses['aha_score_response']
        )

        result = self.client.aha.get_user_score('user123')

        # Result is the data portion of the response
        assert result['history'] == {
            'initial': 50,
            'initial_date': '2024-01-01T00:00:00Z',
            'previous': 70,
        }

    @patch('requests.Session.request')
    def test_get_user_score_handles_404(self, mock_request):
        """Test getting user aha score handles 404 error"""
        mock_request.return_value = mock_error_response(
            404, mock_errors['not_found_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.aha.get_user_score('nonexistent')

        assert exc_info.value.status_code == 404

    @patch('requests.Session.request')
    def test_get_user_score_handles_null_scores(self, mock_request):
        """Test getting user aha score handles null declarative and inferred scores"""
        response_with_nulls = {
            'user_id': 'user123',
            'current_score': 0,
            'declarative_score': None,
            'inferred_score': None,
            'status': 'not_started',
            'history': {
                'initial': None,
                'initial_date': None,
                'previous': None,
            },
        }
        
        mock_request.return_value = mock_success_response(response_with_nulls)

        result = self.client.aha.get_user_score('user123')

        assert result['declarative_score'] is None
        assert result['inferred_score'] is None
        assert result['history']['initial'] is None
