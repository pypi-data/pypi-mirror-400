"""Unit tests for questionnaires resource"""
import pytest
from unittest.mock import patch
from rooguys import Rooguys, RooguysApiError
from rooguys.tests.utils import mock_success_response, mock_error_response
from rooguys.tests.fixtures import mock_responses


class TestQuestionnairesResource:
    """Test suite for questionnaires resource"""

    def setup_method(self):
        """Setup test client"""
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_get_questionnaire_by_slug(self, mock_request):
        """Should get questionnaire by slug"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        result = self.client.questionnaires.get('user-persona')

        assert result['slug'] == 'user-persona'
        call_args = mock_request.call_args
        assert '/questionnaire/user-persona' in call_args[1]['url']

    @patch('requests.Session.request')
    def test_get_questionnaire_not_found(self, mock_request):
        """Should throw 404 error when questionnaire not found"""
        mock_request.return_value = mock_error_response(404, 'Questionnaire not found')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.questionnaires.get('nonexistent-slug')

        assert 'Questionnaire not found' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_get_questionnaire_with_multiple_questions(self, mock_request):
        """Should handle questionnaire with multiple questions"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        result = self.client.questionnaires.get('user-persona')

        assert 'questions' in result
        assert len(result['questions']) > 0

    @patch('requests.Session.request')
    def test_get_questionnaire_with_answer_options(self, mock_request):
        """Should handle questionnaire with answer options"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        result = self.client.questionnaires.get('user-persona')

        question = result['questions'][0]
        assert 'answer_options' in question
        assert len(question['answer_options']) > 0

    @patch('requests.Session.request')
    def test_get_questionnaire_with_special_characters_in_slug(self, mock_request):
        """Should handle slug with special characters"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        self.client.questionnaires.get('user-persona-v2')

        call_args = mock_request.call_args
        assert '/questionnaire/user-persona-v2' in call_args[1]['url']

    @patch('requests.Session.request')
    def test_get_inactive_questionnaire(self, mock_request):
        """Should handle inactive questionnaire"""
        inactive_questionnaire = {
            **mock_responses['questionnaire_response'],
            'is_active': False,
        }
        mock_request.return_value = mock_success_response(inactive_questionnaire)

        result = self.client.questionnaires.get('old-questionnaire')

        assert result['is_active'] is False

    @patch('requests.Session.request')
    def test_get_active_questionnaire(self, mock_request):
        """Should get active questionnaire"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        result = self.client.questionnaires.get_active()

        assert result['is_active'] is True
        call_args = mock_request.call_args
        assert '/questionnaire/active' in call_args[1]['url']

    @patch('requests.Session.request')
    def test_get_active_questionnaire_not_found(self, mock_request):
        """Should throw 404 error when no active questionnaire"""
        mock_request.return_value = mock_error_response(
            404, 'No active questionnaire found for this project'
        )

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.questionnaires.get_active()

        assert 'No active questionnaire found' in str(exc_info.value)

    @patch('requests.Session.request')
    def test_get_active_questionnaire_with_all_fields(self, mock_request):
        """Should handle active questionnaire with all fields"""
        mock_request.return_value = mock_success_response(mock_responses['questionnaire_response'])

        result = self.client.questionnaires.get_active()

        assert 'id' in result
        assert 'slug' in result
        assert 'title' in result
        assert 'description' in result
        assert result['is_active'] is True
        assert 'questions' in result

    @patch('requests.Session.request')
    def test_get_active_questionnaire_server_error(self, mock_request):
        """Should handle server error"""
        mock_request.return_value = mock_error_response(500, 'Internal server error')

        with pytest.raises(RooguysApiError) as exc_info:
            self.client.questionnaires.get_active()

        assert 'Internal server error' in str(exc_info.value)
