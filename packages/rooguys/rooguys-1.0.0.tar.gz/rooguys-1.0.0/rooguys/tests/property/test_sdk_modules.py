"""
Property-Based Tests for Python SDK Modules
Feature: sdk-documentation-update
Validates: Requirements 3.1, 4.5, 6.1-6.3

Tests batch validation, email validation, and filter construction using Hypothesis.
"""

from hypothesis import given, settings, assume
from hypothesis import strategies as st
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
import re

from rooguys.client import Rooguys, EventsResource, UsersResource, LeaderboardsResource
from rooguys.errors import ValidationError
from rooguys.tests.utils.generators import (
    api_key_strategy,
    event_name_strategy,
    user_id_strategy,
    properties_strategy,
)


# ============================================================================
# Strategies for property-based testing
# ============================================================================

# Email strategies
valid_email_strategy = st.from_regex(
    r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]{0,253}\.[a-zA-Z]{2,}$',
    fullmatch=True
)

# Invalid emails that should fail validation
# Note: Empty string passes through because email validation only runs if email is truthy
invalid_email_strategy = st.one_of(
    st.just('invalid'),
    st.just('no@domain'),
    st.just('@nodomain.com'),
    st.just('spaces in@email.com'),
    st.just('missing.domain@'),
    st.just('double@@at.com'),
    st.text(min_size=1, max_size=50).filter(lambda s: '@' not in s and len(s.strip()) > 0),
)

# Batch size strategies
valid_batch_size_strategy = st.integers(min_value=1, max_value=100)
invalid_batch_size_strategy = st.integers(min_value=101, max_value=500)

# Leaderboard filter strategies
persona_strategy = st.sampled_from(['Competitor', 'Explorer', 'Achiever', 'Socializer', None])
level_strategy = st.integers(min_value=1, max_value=100)
date_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31),
    timezones=st.just(timezone.utc)
)


# ============================================================================
# Property 4: Batch Event Validation
# Validates: Requirements 3.1, 3.2
# ============================================================================

@given(batch_size=valid_batch_size_strategy)
@settings(max_examples=100)
def test_batch_events_valid_size_accepted(batch_size):
    """
    Property 4: Batch Event Validation
    
    For any array of events with length between 1 and 100, the SDK SHALL
    make exactly one API request without throwing a validation error.
    
    Validates: Requirements 3.1, 3.2
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'results': [{'status': 'queued'}] * batch_size}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create batch of events
        events = [
            {'event_name': f'event_{i}', 'user_id': f'user_{i}'}
            for i in range(batch_size)
        ]
        
        # Act - should not raise
        client.events.track_batch(events)
        
        # Assert - exactly one request was made
        assert mock_session.request.call_count == 1


@given(batch_size=invalid_batch_size_strategy)
@settings(max_examples=100)
def test_batch_events_exceeds_limit_throws_validation_error(batch_size):
    """
    Property 4: Batch Event Validation
    
    For any array of events with length exceeding 100, the SDK SHALL
    throw a ValidationError before making an API request.
    
    Validates: Requirements 3.1, 3.2
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create batch of events exceeding limit
        events = [
            {'event_name': f'event_{i}', 'user_id': f'user_{i}'}
            for i in range(batch_size)
        ]
        
        # Act & Assert
        try:
            client.events.track_batch(events)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert e.code == 'BATCH_SIZE_EXCEEDED'
            # No API request should have been made
            assert mock_session.request.call_count == 0


def test_batch_events_empty_array_throws_validation_error():
    """
    Property 4: Batch Event Validation (edge case)
    
    For an empty array of events, the SDK SHALL throw a ValidationError.
    
    Validates: Requirements 3.1
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act & Assert
        try:
            client.events.track_batch([])
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert e.code == 'INVALID_BATCH_SIZE'
            assert mock_session.request.call_count == 0


# ============================================================================
# Property 5: Timestamp Validation
# Validates: Requirements 3.5, 3.6
# ============================================================================

@given(days_ago=st.integers(min_value=0, max_value=6))
@settings(max_examples=100)
def test_timestamp_within_7_days_accepted(days_ago):
    """
    Property 5: Timestamp Validation
    
    For any custom timestamp within 7 days of now, the SDK SHALL
    include it in the request body without throwing an error.
    
    Validates: Requirements 3.5, 3.6
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'status': 'queued'}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create timestamp within valid range
        timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Act - should not raise
        client.events.track('test_event', 'user_123', {}, {'timestamp': timestamp})
        
        # Assert - request was made with timestamp
        call_args = mock_session.request.call_args
        assert 'timestamp' in call_args.kwargs['json']


@given(days_ago=st.integers(min_value=8, max_value=365))
@settings(max_examples=100)
def test_timestamp_older_than_7_days_throws_validation_error(days_ago):
    """
    Property 5: Timestamp Validation
    
    For any custom timestamp more than 7 days in the past, the SDK SHALL
    throw a ValidationError with code TIMESTAMP_TOO_OLD.
    
    Validates: Requirements 3.5, 3.6
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create timestamp older than 7 days
        timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Act & Assert
        try:
            client.events.track('test_event', 'user_123', {}, {'timestamp': timestamp})
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert e.code == 'TIMESTAMP_TOO_OLD'
            assert mock_session.request.call_count == 0


# ============================================================================
# Property 7: Email Validation
# Validates: Requirements 4.5
# ============================================================================

@given(email=valid_email_strategy)
@settings(max_examples=100)
def test_valid_email_accepted_for_user_creation(email):
    """
    Property 7: Email Validation
    
    For any valid email format, the SDK SHALL include it in the request
    without throwing a client-side validation error.
    
    Validates: Requirements 4.5
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'user_id': 'user_123', 'email': email}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act - should not raise
        client.users.create({'user_id': 'user_123', 'email': email})
        
        # Assert - request was made with email
        call_args = mock_session.request.call_args
        assert call_args.kwargs['json']['email'] == email


@given(email=invalid_email_strategy)
@settings(max_examples=100)
def test_invalid_email_throws_validation_error(email):
    """
    Property 7: Email Validation
    
    For any invalid email format, the SDK SHALL throw a ValidationError
    before making an API request.
    
    Validates: Requirements 4.5
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act & Assert
        try:
            client.users.create({'user_id': 'user_123', 'email': email})
            assert False, f"Should have raised ValidationError for email: {email}"
        except ValidationError as e:
            assert e.code == 'INVALID_EMAIL'
            assert mock_session.request.call_count == 0


@given(email=invalid_email_strategy)
@settings(max_examples=100)
def test_invalid_email_throws_validation_error_on_update(email):
    """
    Property 7: Email Validation (update)
    
    For any invalid email format in user update, the SDK SHALL throw
    a ValidationError before making an API request.
    
    Validates: Requirements 4.5
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act & Assert
        try:
            client.users.update('user_123', {'email': email})
            assert False, f"Should have raised ValidationError for email: {email}"
        except ValidationError as e:
            assert e.code == 'INVALID_EMAIL'
            assert mock_session.request.call_count == 0


# ============================================================================
# Property 8: Partial Update Construction
# Validates: Requirements 4.6
# ============================================================================

@given(
    display_name=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    metadata=st.one_of(st.none(), st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=50), max_size=5)),
)
@settings(max_examples=100)
def test_partial_update_only_includes_provided_fields(display_name, metadata):
    """
    Property 8: Partial Update Construction
    
    For any user update call with a subset of fields, the request body
    SHALL contain only the provided fields. None values SHALL NOT be included.
    
    Validates: Requirements 4.6
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'user_id': 'user_123'}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Build update data
        update_data = {}
        if display_name is not None:
            update_data['display_name'] = display_name
        if metadata is not None:
            update_data['metadata'] = metadata
        
        # Skip if no fields to update
        assume(len(update_data) > 0)
        
        # Act
        client.users.update('user_123', update_data)
        
        # Assert - request body only contains provided fields
        call_args = mock_session.request.call_args
        request_body = call_args.kwargs['json']
        
        # None values should not be in request body
        for key, value in request_body.items():
            assert value is not None, f"None value found for key: {key}"
        
        # Only provided fields should be in request body
        if display_name is not None:
            assert request_body.get('display_name') == display_name
        else:
            assert 'display_name' not in request_body
        
        if metadata is not None:
            assert request_body.get('metadata') == metadata
        else:
            assert 'metadata' not in request_body


# ============================================================================
# Property 9: Field Selection Query Construction
# Validates: Requirements 5.1
# ============================================================================

@given(
    fields=st.lists(
        st.sampled_from(['user_id', 'points', 'level', 'badges', 'persona', 'metrics', 'streak', 'inventory']),
        min_size=1,
        max_size=8,
        unique=True
    )
)
@settings(max_examples=100)
def test_field_selection_query_construction(fields):
    """
    Property 9: Field Selection Query Construction
    
    For any user profile request with a fields parameter, the SDK SHALL
    include a fields query parameter with the comma-separated list of
    requested fields.
    
    Validates: Requirements 5.1
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'user_id': 'user_123'}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act
        client.users.get('user_123', {'fields': fields})
        
        # Assert - fields query parameter is correctly constructed
        call_args = mock_session.request.call_args
        params = call_args.kwargs.get('params', {})
        
        assert 'fields' in params
        expected_fields = ','.join(fields)
        assert params['fields'] == expected_fields


# ============================================================================
# Property 10: Leaderboard Filter Query Construction
# Validates: Requirements 6.1, 6.2, 6.3
# ============================================================================

@given(
    persona=persona_strategy,
    min_level=st.one_of(st.none(), level_strategy),
    max_level=st.one_of(st.none(), level_strategy),
)
@settings(max_examples=100)
def test_leaderboard_filter_query_construction(persona, min_level, max_level):
    """
    Property 10: Leaderboard Filter Query Construction
    
    For any leaderboard request with filter parameters (persona, minLevel, maxLevel),
    the SDK SHALL include the corresponding query parameters with correctly formatted values.
    
    Validates: Requirements 6.1, 6.2, 6.3
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'rankings': [], 'total': 0}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Build options
        options = {}
        if persona is not None:
            options['persona'] = persona
        if min_level is not None:
            options['min_level'] = min_level
        if max_level is not None:
            options['max_level'] = max_level
        
        # Act
        client.leaderboards.get_global('all-time', 1, 50, options)
        
        # Assert - filter parameters are correctly included
        call_args = mock_session.request.call_args
        params = call_args.kwargs.get('params', {})
        
        if persona is not None:
            assert params.get('persona') == persona
        else:
            assert 'persona' not in params
        
        if min_level is not None:
            assert params.get('minLevel') == min_level
        else:
            assert 'minLevel' not in params
        
        if max_level is not None:
            assert params.get('maxLevel') == max_level
        else:
            assert 'maxLevel' not in params


@given(
    start_date=date_strategy,
    end_date=date_strategy,
)
@settings(max_examples=100)
def test_leaderboard_date_filter_query_construction(start_date, end_date):
    """
    Property 10: Leaderboard Filter Query Construction (dates)
    
    For any leaderboard request with date filter parameters, the SDK SHALL
    include the corresponding query parameters with ISO 8601 formatted values.
    
    Validates: Requirements 6.3
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'rankings': [], 'total': 0}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Build options with date filters
        options = {
            'start_date': start_date,
            'end_date': end_date,
        }
        
        # Act
        client.leaderboards.get_global('all-time', 1, 50, options)
        
        # Assert - date parameters are correctly formatted as ISO 8601
        call_args = mock_session.request.call_args
        params = call_args.kwargs.get('params', {})
        
        assert 'startDate' in params
        assert 'endDate' in params
        
        # Verify ISO 8601 format
        assert params['startDate'] == start_date.isoformat()
        assert params['endDate'] == end_date.isoformat()


# ============================================================================
# Property 6: Idempotency Key Propagation
# Validates: Requirements 3.3, 3.4
# ============================================================================

@given(
    idempotency_key=st.text(min_size=1, max_size=64, alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_')
)
@settings(max_examples=100)
def test_idempotency_key_propagation(idempotency_key):
    """
    Property 6: Idempotency Key Propagation
    
    For any request with an idempotency key provided, the SDK SHALL include
    the X-Idempotency-Key header with the exact value provided.
    
    Validates: Requirements 3.3, 3.4
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'status': 'queued'}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act
        client.events.track('test_event', 'user_123', {}, {'idempotency_key': idempotency_key})
        
        # Assert - idempotency key header is included
        call_args = mock_session.request.call_args
        headers = call_args.kwargs.get('headers', {})
        
        assert headers.get('X-Idempotency-Key') == idempotency_key


def test_no_idempotency_key_header_when_not_provided():
    """
    Property 6: Idempotency Key Propagation (absence)
    
    For requests without an idempotency key, the X-Idempotency-Key header
    SHALL NOT be present.
    
    Validates: Requirements 3.3, 3.4
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'status': 'queued'}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Act - no idempotency key
        client.events.track('test_event', 'user_123', {})
        
        # Assert - no idempotency key header
        call_args = mock_session.request.call_args
        headers = call_args.kwargs.get('headers') or {}
        
        assert 'X-Idempotency-Key' not in headers


# ============================================================================
# Batch User Creation Validation
# Validates: Requirements 4.3
# ============================================================================

@given(batch_size=valid_batch_size_strategy)
@settings(max_examples=100)
def test_batch_users_valid_size_accepted(batch_size):
    """
    Property: Batch User Creation Validation
    
    For any array of users with length between 1 and 100, the SDK SHALL
    make exactly one API request without throwing a validation error.
    
    Validates: Requirements 4.3
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'success': True,
            'data': {'results': [{'status': 'created'}] * batch_size}
        }
        mock_response.headers = {
            'X-RateLimit-Limit': '1000',
            'X-RateLimit-Remaining': '999',
            'X-RateLimit-Reset': '1704067200',
        }
        mock_session.request.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create batch of users
        users = [
            {'user_id': f'user_{i}', 'display_name': f'User {i}'}
            for i in range(batch_size)
        ]
        
        # Act - should not raise
        client.users.create_batch(users)
        
        # Assert - exactly one request was made
        assert mock_session.request.call_count == 1


@given(batch_size=invalid_batch_size_strategy)
@settings(max_examples=100)
def test_batch_users_exceeds_limit_throws_validation_error(batch_size):
    """
    Property: Batch User Creation Validation
    
    For any array of users with length exceeding 100, the SDK SHALL
    throw a ValidationError before making an API request.
    
    Validates: Requirements 4.3
    """
    with patch('requests.Session') as mock_session_class:
        # Arrange
        mock_session = Mock()
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        client = Rooguys('test-api-key')
        
        # Create batch of users exceeding limit
        users = [
            {'user_id': f'user_{i}', 'display_name': f'User {i}'}
            for i in range(batch_size)
        ]
        
        # Act & Assert
        try:
            client.users.create_batch(users)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert e.code == 'BATCH_SIZE_EXCEEDED'
            assert mock_session.request.call_count == 0
