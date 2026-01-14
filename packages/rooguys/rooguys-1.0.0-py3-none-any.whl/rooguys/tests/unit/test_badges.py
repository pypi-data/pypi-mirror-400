"""Unit tests for badges resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures import mock_responses, mock_errors


class TestBadgesResource:
    """Test suite for badges resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_list_badges_default_parameters(self, mock_request):
        """Should list badges with default parameters"""
        mock_request.return_value = mock_success_response(mock_responses['badges_list_response'])

        result = self.client.badges.list()

        assert len(result['badges']) == 1
        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'page': 1, 'limit': 50, 'active_only': 'false'}

    @patch('requests.Session.request')
    def test_list_badges_custom_pagination(self, mock_request):
        """Should list badges with custom pagination"""
        mock_request.return_value = mock_success_response(mock_responses['badges_list_response'])

        self.client.badges.list(2, 25)

        call_args = mock_request.call_args
        assert call_args[1]['params']['page'] == 2
        assert call_args[1]['params']['limit'] == 25

    @patch('requests.Session.request')
    def test_list_only_active_badges(self, mock_request):
        """Should list only active badges"""
        mock_request.return_value = mock_success_response(mock_responses['badges_list_response'])

        self.client.badges.list(1, 50, True)

        call_args = mock_request.call_args
        assert call_args[1]['params']['active_only'] == 'true'

    @patch('requests.Session.request')
    def test_list_badges_empty(self, mock_request):
        """Should handle empty badge list"""
        empty_response = {
            'badges': [],
            'pagination': {'page': 1, 'limit': 50, 'total': 0, 'totalPages': 0},
        }
        mock_request.return_value = mock_success_response(empty_response)

        result = self.client.badges.list()

        assert result['badges'] == []
        assert result['pagination']['total'] == 0

    @patch('requests.Session.request')
    def test_list_badges_invalid_pagination(self, mock_request):
        """Should throw error for invalid pagination"""
        mock_request.return_value = mock_error_response(
            400, mock_errors['invalid_pagination_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.badges.list(1, 150)

        assert 'Limit must be between 1 and 100' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_list_badges_with_all_fields(self, mock_request):
        """Should handle badges with all fields"""
        mock_request.return_value = mock_success_response(mock_responses['badges_list_response'])

        result = self.client.badges.list()

        badge = result['badges'][0]
        assert 'id' in badge
        assert 'name' in badge
        assert 'description' in badge
        assert 'icon_url' in badge
        assert 'is_active' in badge
        assert 'unlock_criteria' in badge

    @patch('requests.Session.request')
    def test_list_badges_server_error(self, mock_request):
        """Should handle server error"""
        mock_request.return_value = mock_error_response(500, 'Internal server error')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.badges.list()

        assert 'Internal server error' in str(exc_info.value)
