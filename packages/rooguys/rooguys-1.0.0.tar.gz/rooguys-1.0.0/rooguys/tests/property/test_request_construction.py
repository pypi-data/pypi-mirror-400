"""
Property-Based Test: HTTP Request Construction
Feature: sdk-testing-enhancement, Property 1: HTTP Request Construction
Validates: Requirements 1.1, 3.1

Tests that any valid SDK method call constructs correct HTTP request
with proper method, URL, headers, and body structure.
"""

from hypothesis import given, settings
from unittest.mock import Mock, patch
import json

from rooguys.client import Rooguys
from rooguys.tests.utils.generators import (
    api_key_strategy,
    event_name_strategy,
    user_id_strategy,
    properties_strategy,
    user_ids_strategy,
    timeframe_strategy,
    page_strategy,
    limit_strategy,
    aha_value_strategy,
)


@given(
    api_key=api_key_strategy,
    event_name=event_name_strategy,
    user_id=user_id_strategy,
    properties=properties_strategy,
)
@settings(max_examples=100)
def test_event_tracking_request_construction(api_key, event_name, user_id, properties):
    """Property: Event tracking constructs valid POST request"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'queued', 'message': 'Event accepted'}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.events.track(event_name, user_id, properties)
        
        # Assert
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        
        assert call_args.kwargs['method'] == 'POST'
        assert '/event' in call_args.kwargs['url']
        
        # Check body
        body = call_args.kwargs['json']
        assert body['event_name'] == event_name
        assert body['user_id'] == user_id
        assert body['properties'] == properties


@given(
    api_key=api_key_strategy,
    user_id=user_id_strategy,
)
@settings(max_examples=100)
def test_user_profile_request_construction(api_key, user_id):
    """Property: User profile fetch constructs valid GET request"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'user_id': user_id, 'points': 100}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.users.get(user_id)
        
        # Assert
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        
        from urllib.parse import quote
        assert call_args.kwargs['method'] == 'GET'
        assert f'/user/{quote(user_id, safe="")}' in call_args.kwargs['url']


@given(
    api_key=api_key_strategy,
    user_ids=user_ids_strategy,
)
@settings(max_examples=100)
def test_bulk_user_fetch_request_construction(api_key, user_ids):
    """Property: Bulk user fetch constructs valid POST request"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'users': []}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.users.get_bulk(user_ids)
        
        # Assert
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        
        assert call_args.kwargs['method'] == 'POST'
        assert '/users/bulk' in call_args.kwargs['url']
        
        # Check body
        body = call_args.kwargs['json']
        assert body['user_ids'] == user_ids


@given(
    api_key=api_key_strategy,
    timeframe=timeframe_strategy,
    page=page_strategy,
    limit=limit_strategy,
)
@settings(max_examples=100)
def test_leaderboard_request_construction(api_key, timeframe, page, limit):
    """Property: Leaderboard fetch constructs valid GET request with query params"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'rankings': [], 'page': page, 'limit': limit, 'total': 0}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.leaderboards.get_global(timeframe, page, limit)
        
        # Assert
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        
        assert call_args.kwargs['method'] == 'GET'
        assert '/leaderboard' in call_args.kwargs['url']
        
        # Check query params
        params = call_args.kwargs['params']
        assert params['timeframe'] == timeframe
        assert params['page'] == page
        assert params['limit'] == limit


@given(
    api_key=api_key_strategy,
    user_id=user_id_strategy,
    value=aha_value_strategy,
)
@settings(max_examples=100)
def test_aha_declare_request_construction(api_key, user_id, value):
    """Property: Aha score declaration constructs valid POST request"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {'success': True, 'message': 'Score declared'}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.aha.declare(user_id, value)
        
        # Assert
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        
        assert call_args.kwargs['method'] == 'POST'
        assert '/aha/declare' in call_args.kwargs['url']
        
        # Check body
        body = call_args.kwargs['json']
        assert body['user_id'] == user_id
        assert body['value'] == value


@given(
    api_key=api_key_strategy,
    user_id=user_id_strategy,
)
@settings(max_examples=100)
def test_api_key_in_headers(api_key, user_id):
    """Property: API key is included in request headers"""
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_response = Mock()
        mock_response.json.return_value = {'user_id': user_id, 'points': 100}
        mock_response.raise_for_status = Mock()
        mock_response.ok = True
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = Rooguys(api_key)
        
        # Act
        client.users.get(user_id)
        
        # Assert
        # Check that session was created with correct headers
        assert mock_session.headers['x-api-key'] == api_key
        assert mock_session.headers['Content-Type'] == 'application/json'
