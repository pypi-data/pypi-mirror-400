"""Unit tests for levels resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures import mock_responses, mock_errors


class TestLevelsResource:
    """Test suite for levels resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_list_levels_default_parameters(self, mock_request):
        """Should list levels with default parameters"""
        mock_request.return_value = mock_success_response(mock_responses['levels_list_response'])

        result = self.client.levels.list()

        assert len(result['levels']) == 2
        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'page': 1, 'limit': 50}

    @patch('requests.Session.request')
    def test_list_levels_custom_pagination(self, mock_request):
        """Should list levels with custom pagination"""
        mock_request.return_value = mock_success_response(mock_responses['levels_list_response'])

        self.client.levels.list(2, 25)

        call_args = mock_request.call_args
        assert call_args[1]['params']['page'] == 2
        assert call_args[1]['params']['limit'] == 25

    @patch('requests.Session.request')
    def test_list_levels_empty(self, mock_request):
        """Should handle empty levels list"""
        empty_response = {
            'levels': [],
            'pagination': {'page': 1, 'limit': 50, 'total': 0, 'totalPages': 0},
        }
        mock_request.return_value = mock_success_response(empty_response)

        result = self.client.levels.list()

        assert result['levels'] == []
        assert result['pagination']['total'] == 0

    @patch('requests.Session.request')
    def test_list_levels_with_all_fields(self, mock_request):
        """Should handle levels with all fields"""
        mock_request.return_value = mock_success_response(mock_responses['levels_list_response'])

        result = self.client.levels.list()

        level = result['levels'][0]
        assert 'id' in level
        assert 'name' in level
        assert 'level_number' in level
        assert 'points_required' in level
        assert 'description' in level
        assert 'icon_url' in level

    @patch('requests.Session.request')
    def test_list_levels_sorted_by_level_number(self, mock_request):
        """Should handle levels sorted by level_number"""
        mock_request.return_value = mock_success_response(mock_responses['levels_list_response'])

        result = self.client.levels.list()

        assert result['levels'][0]['level_number'] == 1
        assert result['levels'][1]['level_number'] == 2

    @patch('requests.Session.request')
    def test_list_levels_invalid_pagination(self, mock_request):
        """Should throw error for invalid pagination"""
        mock_request.return_value = mock_error_response(
            400, mock_errors['invalid_pagination_error']['message']
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.levels.list(1, 150)

        assert 'Limit must be between 1 and 100' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_list_levels_server_error(self, mock_request):
        """Should handle server error"""
        mock_request.return_value = mock_error_response(500, 'Internal server error')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.levels.list()

        assert 'Internal server error' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_list_levels_with_nullable_fields(self, mock_request):
        """Should handle levels with nullable fields"""
        levels_with_nulls = {
            'levels': [
                {
                    'id': 'level1',
                    'name': 'Bronze',
                    'level_number': 1,
                    'points_required': 0,
                    'description': None,
                    'icon_url': None,
                },
            ],
            'pagination': {'page': 1, 'limit': 50, 'total': 1, 'totalPages': 1},
        }
        mock_request.return_value = mock_success_response(levels_with_nulls)

        result = self.client.levels.list()

        assert result['levels'][0]['description'] is None
        assert result['levels'][0]['icon_url'] is None
