"""
Property-Based Test: Response Parsing Round-Trip
Feature: sdk-documentation-update, Property 2: Response Parsing Round-Trip
Validates: Requirements 2.1, 2.3, 2.4, 2.5

Tests that any valid API response in the format { success: true, data: {...}, request_id: "..." }
is parsed correctly and all fields are preserved.
"""

from hypothesis import given, settings, assume
from hypothesis import strategies as st
from unittest.mock import Mock, patch

from rooguys.http_client import (
    parse_response_body,
    extract_rate_limit_info,
    extract_request_id,
    HttpClient,
    ApiResponse,
)
from rooguys.tests.utils.generators import api_key_strategy


# Strategy for generating valid request IDs
request_id_strategy = st.text(
    alphabet='abcdefghijklmnopqrstuvwxyz0123456789-',
    min_size=1,
    max_size=36
)

# Strategy for generating pagination data
pagination_strategy = st.fixed_dictionaries({
    'page': st.integers(min_value=1, max_value=1000),
    'limit': st.integers(min_value=1, max_value=100),
    'total': st.integers(min_value=0, max_value=100000),
    'totalPages': st.integers(min_value=0, max_value=1000),
})

# Strategy for generating nested data structures
nested_data_strategy = st.recursive(
    st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(max_size=100),
    ),
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=5),
    ),
    max_leaves=20
)


@given(
    data=nested_data_strategy,
    request_id=st.one_of(st.none(), request_id_strategy),
    pagination=st.one_of(st.none(), pagination_strategy),
)
@settings(max_examples=100)
def test_standardized_response_parsing_round_trip(data, request_id, pagination):
    """
    Property 2: Response Parsing Round-Trip
    
    For any valid API response in the format { success: true, data: {...}, request_id: "..." },
    parsing then serializing the response SHALL produce an equivalent data structure
    with all fields preserved.
    
    Validates: Requirements 2.1, 2.3, 2.4, 2.5
    """
    # Arrange: Create a standardized response
    response_body = {
        'success': True,
        'data': data,
    }
    if request_id is not None:
        response_body['request_id'] = request_id
    if pagination is not None:
        response_body['pagination'] = pagination
    
    # Act: Parse the response
    parsed = parse_response_body(response_body)
    
    # Assert: All fields are preserved
    assert parsed['data'] == data
    assert parsed['request_id'] == request_id
    assert parsed['pagination'] == pagination


@given(
    data=nested_data_strategy,
)
@settings(max_examples=100)
def test_legacy_response_parsing_preserves_data(data):
    """
    Property: Legacy response format is preserved
    
    For any response without the standardized format, the entire response
    body should be returned as-is.
    
    Validates: Requirements 2.1
    """
    # Arrange: Create a legacy response (no 'success' field)
    assume(not isinstance(data, dict) or 'success' not in data)
    
    # Act: Parse the response
    parsed = parse_response_body(data)
    
    # Assert: Data is preserved
    assert parsed['data'] == data


@given(
    limit=st.integers(min_value=1, max_value=10000),
    remaining=st.integers(min_value=0, max_value=10000),
    reset=st.integers(min_value=0, max_value=2147483647),
)
@settings(max_examples=100)
def test_rate_limit_header_extraction(limit, remaining, reset):
    """
    Property 11: Rate Limit Header Extraction
    
    For any API response with rate limit headers, the SDK SHALL extract and expose
    rateLimit.limit, rateLimit.remaining, and rateLimit.reset with correct numeric values.
    
    Validates: Requirements 7.1
    """
    # Arrange: Create headers with rate limit info
    headers = {
        'X-RateLimit-Limit': str(limit),
        'X-RateLimit-Remaining': str(remaining),
        'X-RateLimit-Reset': str(reset),
    }
    
    # Act: Extract rate limit info
    rate_limit = extract_rate_limit_info(headers)
    
    # Assert: Values are correctly extracted
    assert rate_limit.limit == limit
    assert rate_limit.remaining == remaining
    assert rate_limit.reset == reset


@given(
    limit=st.integers(min_value=1, max_value=10000),
    remaining=st.integers(min_value=0, max_value=10000),
    reset=st.integers(min_value=0, max_value=2147483647),
)
@settings(max_examples=100)
def test_rate_limit_header_extraction_lowercase(limit, remaining, reset):
    """
    Property: Rate limit headers are extracted regardless of case
    
    Validates: Requirements 7.1
    """
    # Arrange: Create headers with lowercase names
    headers = {
        'x-ratelimit-limit': str(limit),
        'x-ratelimit-remaining': str(remaining),
        'x-ratelimit-reset': str(reset),
    }
    
    # Act: Extract rate limit info
    rate_limit = extract_rate_limit_info(headers)
    
    # Assert: Values are correctly extracted
    assert rate_limit.limit == limit
    assert rate_limit.remaining == remaining
    assert rate_limit.reset == reset


@given(
    request_id=request_id_strategy,
)
@settings(max_examples=100)
def test_request_id_extraction_from_headers(request_id):
    """
    Property: Request ID is extracted from headers
    
    Validates: Requirements 2.3
    """
    # Arrange: Create headers with request ID
    headers = {'X-Request-Id': request_id}
    body = {}
    
    # Act: Extract request ID
    extracted = extract_request_id(headers, body)
    
    # Assert: Request ID is correctly extracted
    assert extracted == request_id


@given(
    request_id=request_id_strategy,
)
@settings(max_examples=100)
def test_request_id_extraction_from_body(request_id):
    """
    Property: Request ID is extracted from body when not in headers
    
    Validates: Requirements 2.3
    """
    # Arrange: Create body with request ID
    headers = {}
    body = {'request_id': request_id}
    
    # Act: Extract request ID
    extracted = extract_request_id(headers, body)
    
    # Assert: Request ID is correctly extracted
    assert extracted == request_id


@given(
    header_request_id=request_id_strategy,
    body_request_id=request_id_strategy,
)
@settings(max_examples=100)
def test_request_id_header_takes_precedence(header_request_id, body_request_id):
    """
    Property: Request ID from headers takes precedence over body
    
    Validates: Requirements 2.3
    """
    assume(header_request_id != body_request_id)
    
    # Arrange: Create both header and body with different request IDs
    headers = {'X-Request-Id': header_request_id}
    body = {'request_id': body_request_id}
    
    # Act: Extract request ID
    extracted = extract_request_id(headers, body)
    
    # Assert: Header request ID takes precedence
    assert extracted == header_request_id


@given(
    user_id=st.text(min_size=1, max_size=100),
    points=st.integers(min_value=0),
    level_name=st.text(min_size=1, max_size=50),
    level_number=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=100)
def test_nested_object_preservation_in_response(user_id, points, level_name, level_number):
    """
    Property: Nested object structures are preserved in responses
    
    Validates: Requirements 2.4
    """
    # Arrange: Create a response with nested objects
    response_body = {
        'success': True,
        'data': {
            'user_id': user_id,
            'points': points,
            'level': {
                'name': level_name,
                'level_number': level_number,
            },
        },
    }
    
    # Act: Parse the response
    parsed = parse_response_body(response_body)
    
    # Assert: Nested structure is preserved
    assert parsed['data']['user_id'] == user_id
    assert parsed['data']['points'] == points
    assert parsed['data']['level']['name'] == level_name
    assert parsed['data']['level']['level_number'] == level_number


@given(
    items=st.lists(
        st.fixed_dictionaries({
            'id': st.text(min_size=1, max_size=36),
            'name': st.text(min_size=1, max_size=100),
        }),
        min_size=0,
        max_size=20
    ),
)
@settings(max_examples=100)
def test_array_preservation_in_response(items):
    """
    Property: Arrays are preserved in responses
    
    Validates: Requirements 2.4
    """
    # Arrange: Create a response with arrays
    response_body = {
        'success': True,
        'data': {
            'items': items,
            'count': len(items),
        },
    }
    
    # Act: Parse the response
    parsed = parse_response_body(response_body)
    
    # Assert: Array is preserved
    assert parsed['data']['items'] == items
    assert len(parsed['data']['items']) == len(items)


@given(
    nullable_field=st.one_of(st.none(), st.text(max_size=50)),
)
@settings(max_examples=100)
def test_null_value_preservation_in_response(nullable_field):
    """
    Property: Null values are preserved in responses
    
    Validates: Requirements 2.5
    """
    # Arrange: Create a response with nullable fields
    response_body = {
        'success': True,
        'data': {
            'nullable_field': nullable_field,
        },
    }
    
    # Act: Parse the response
    parsed = parse_response_body(response_body)
    
    # Assert: Null value is preserved
    assert parsed['data']['nullable_field'] == nullable_field


@given(
    page=st.integers(min_value=1, max_value=1000),
    limit=st.integers(min_value=1, max_value=100),
    total=st.integers(min_value=0, max_value=100000),
    total_pages=st.integers(min_value=0, max_value=1000),
)
@settings(max_examples=100)
def test_pagination_parsing(page, limit, total, total_pages):
    """
    Property: Pagination is parsed correctly
    
    Validates: Requirements 2.4
    """
    # Arrange: Create a response with pagination
    response_body = {
        'success': True,
        'data': {'items': []},
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'totalPages': total_pages,
        },
    }
    
    # Act: Parse the response
    parsed = parse_response_body(response_body)
    
    # Assert: Pagination is preserved
    assert parsed['pagination']['page'] == page
    assert parsed['pagination']['limit'] == limit
    assert parsed['pagination']['total'] == total
    assert parsed['pagination']['totalPages'] == total_pages
