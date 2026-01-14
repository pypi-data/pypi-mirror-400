import unittest
from unittest.mock import MagicMock, patch
from rooguys import Rooguys

class TestRooguys(unittest.TestCase):
    def setUp(self):
        self.client = Rooguys('test-api-key')

    @patch('requests.Session.request')
    def test_track_event(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'queued', 'message': 'ok'}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.client.events.track('test_event', 'user_1')

        self.assertEqual(result['status'], 'queued')
        mock_request.assert_called_with(
            method='POST',
            url='https://api.rooguys.com/v1/event',
            json={
                'event_name': 'test_event',
                'user_id': 'user_1',
                'properties': {}
            },
            params={},
            timeout=10
        )

    @patch('requests.Session.request')
    def test_get_user(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {'user_id': 'user_1', 'points': 100}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.client.users.get('user_1')

        self.assertEqual(result['user_id'], 'user_1')
        self.assertEqual(result['points'], 100)
        mock_request.assert_called_with(
            method='GET',
            url='https://api.rooguys.com/v1/user/user_1',
            json=None,
            params=None,
            timeout=10
        )

    @patch('requests.Session.request')
    def test_get_global_leaderboard(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {'rankings': []}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.client.leaderboards.get_global()

        self.assertEqual(result['rankings'], [])
        mock_request.assert_called_with(
            method='GET',
            url='https://api.rooguys.com/v1/leaderboard',
            json=None,
            params={'timeframe': 'all-time', 'page': 1, 'limit': 50},
            timeout=10
        )

if __name__ == '__main__':
    unittest.main()
