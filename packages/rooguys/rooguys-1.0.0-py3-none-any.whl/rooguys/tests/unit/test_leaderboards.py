"""Unit tests for leaderboards resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures import mock_responses, mock_errors


class TestLeaderboardsResource:
    """Test suite for leaderboards resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_get_global_leaderboard_default_parameters(self, mock_request):
        """Should get global leaderboard with default parameters"""
        mock_request.return_value = mock_success_response(mock_responses['leaderboard_response'])

        result = self.client.leaderboards.get_global()

        assert result == mock_responses['leaderboard_response']
        assert len(result['rankings']) == 2
        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'timeframe': 'all-time', 'page': 1, 'limit': 50}

    @patch('requests.Session.request')
    def test_get_global_leaderboard_weekly(self, mock_request):
        """Should get global leaderboard with weekly timeframe"""
        mock_request.return_value = mock_success_response(mock_responses['leaderboard_response'])

        self.client.leaderboards.get_global('weekly')

        call_args = mock_request.call_args
        assert call_args[1]['params']['timeframe'] == 'weekly'

    @patch('requests.Session.request')
    def test_get_global_leaderboard_custom_pagination(self, mock_request):
        """Should get global leaderboard with custom pagination"""
        mock_request.return_value = mock_success_response(mock_responses['leaderboard_response'])

        self.client.leaderboards.get_global('all-time', 2, 25)

        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'timeframe': 'all-time', 'page': 2, 'limit': 25}

    @patch('requests.Session.request')
    def test_get_global_leaderboard_empty(self, mock_request):
        """Should handle empty leaderboard"""
        empty_leaderboard = {
            **mock_responses['leaderboard_response'],
            'rankings': [],
            'total': 0,
        }
        mock_request.return_value = mock_success_response(empty_leaderboard)

        result = self.client.leaderboards.get_global()

        assert result['rankings'] == []
        assert result['total'] == 0

    @patch('requests.Session.request')
    def test_get_global_leaderboard_invalid_timeframe(self, mock_request):
        """Should throw error for invalid timeframe"""
        mock_request.return_value = mock_error_response(
            400, mock_errors['invalid_timeframe_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.leaderboards.get_global('invalid')

        assert 'Timeframe must be one of' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_list_leaderboards(self, mock_request):
        """Should list all leaderboards"""
        mock_request.return_value = mock_success_response(
            mock_responses['leaderboards_list_response']
        )

        result = self.client.leaderboards.list()

        assert len(result['leaderboards']) == 1
        assert 'pagination' in result

    @patch('requests.Session.request')
    def test_list_leaderboards_with_search(self, mock_request):
        """Should list leaderboards with search"""
        mock_request.return_value = mock_success_response(
            mock_responses['leaderboards_list_response']
        )

        self.client.leaderboards.list(1, 50, 'top')

        call_args = mock_request.call_args
        assert call_args[1]['params']['search'] == 'top'

    @patch('requests.Session.request')
    def test_get_custom_leaderboard(self, mock_request):
        """Should get custom leaderboard by ID"""
        mock_request.return_value = mock_success_response(
            mock_responses['custom_leaderboard_response']
        )

        result = self.client.leaderboards.get_custom('lb1')

        assert 'leaderboard' in result
        assert 'rankings' in result

    @patch('requests.Session.request')
    def test_get_custom_leaderboard_not_found(self, mock_request):
        """Should throw 404 for non-existent leaderboard"""
        mock_request.return_value = mock_error_response(404, 'Leaderboard not found')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.leaderboards.get_custom('invalid_id')

        assert 'Leaderboard not found' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_get_user_rank_in_leaderboard(self, mock_request):
        """Should get user rank in custom leaderboard"""
        mock_request.return_value = mock_success_response(mock_responses['user_rank_response'])

        result = self.client.leaderboards.get_user_rank('lb1', 'user_123')

        assert result['rank'] == 42

    @patch('requests.Session.request')
    def test_get_user_rank_not_found(self, mock_request):
        """Should throw 404 for non-existent user or leaderboard"""
        mock_request.return_value = mock_error_response(404, 'Not found')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.leaderboards.get_user_rank('lb1', 'invalid_user')

        assert 'Not found' in str(exc_info.value)
