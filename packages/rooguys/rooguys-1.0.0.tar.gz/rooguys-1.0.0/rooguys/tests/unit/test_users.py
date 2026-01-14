"""Unit tests for users resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures import mock_responses, mock_errors


class TestUsersResource:
    """Test suite for users resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_get_user_profile(self, mock_request):
        """Should get a user profile"""
        mock_request.return_value = mock_success_response(mock_responses['user_profile'])

        result = self.client.users.get('user_123')

        assert result == mock_responses['user_profile']
        # The user_id in the mock response is 'user123', not 'user_123'
        assert result['user_id'] == mock_responses['user_profile']['user_id']
        assert result['points'] == 100

    @patch('requests.Session.request')
    def test_get_user_not_found(self, mock_request):
        """Should throw 404 error when user not found"""
        mock_request.return_value = mock_error_response(
            404, mock_errors['not_found_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.users.get('nonexistent_user')

        # Check that the error message contains user-related text
        error_msg = str(exc_info.value).lower()
        assert 'user' in error_msg or 'not found' in error_msg

    @patch('requests.Session.request')
    def test_get_bulk_users(self, mock_request):
        """Should get multiple user profiles"""
        mock_request.return_value = mock_success_response(mock_responses['bulk_users_response'])

        result = self.client.users.get_bulk(['user1', 'user2'])

        assert result == mock_responses['bulk_users_response']
        assert len(result['users']) == 2

    @patch('requests.Session.request')
    def test_get_bulk_empty_results(self, mock_request):
        """Should handle empty results"""
        mock_request.return_value = mock_success_response({'users': []})

        result = self.client.users.get_bulk(['nonexistent1'])

        assert result['users'] == []

    @patch('requests.Session.request')
    def test_get_user_badges(self, mock_request):
        """Should get user badges"""
        mock_request.return_value = mock_success_response(
            {'badges': mock_responses['user_profile']['badges']}
        )

        result = self.client.users.get_badges('user_123')

        assert len(result['badges']) == 1
        assert result['badges'][0]['name'] == 'First Steps'

    @patch('requests.Session.request')
    def test_get_user_rank_default_timeframe(self, mock_request):
        """Should get user rank with default timeframe"""
        mock_request.return_value = mock_success_response(mock_responses['user_rank_response'])

        result = self.client.users.get_rank('user_123')

        assert result['rank'] == 42
        call_args = mock_request.call_args
        assert call_args[1]['params']['timeframe'] == 'all-time'

    @patch('requests.Session.request')
    def test_get_user_rank_weekly(self, mock_request):
        """Should get user rank with weekly timeframe"""
        mock_request.return_value = mock_success_response(mock_responses['user_rank_response'])

        self.client.users.get_rank('user_123', 'weekly')

        call_args = mock_request.call_args
        assert call_args[1]['params']['timeframe'] == 'weekly'

    @patch('requests.Session.request')
    def test_submit_answers(self, mock_request):
        """Should submit questionnaire answers"""
        mock_request.return_value = mock_success_response(
            mock_responses['answer_submission_response']
        )

        answers = [
            {'question_id': 'q1', 'answer_option_id': 'a1'},
            {'question_id': 'q2', 'answer_option_id': 'a2'},
        ]

        result = self.client.users.submit_answers('user_123', 'questionnaire_id', answers)

        assert result['status'] == 'accepted'
        call_args = mock_request.call_args
        assert call_args[1]['json']['answers'] == answers
