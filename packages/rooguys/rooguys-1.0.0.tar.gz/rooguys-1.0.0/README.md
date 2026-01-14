# Rooguys Python SDK

The official Python SDK for the Rooguys Gamification API.

## Installation

```bash
pip install rooguys
```

## Initialization

```python
from rooguys import Rooguys

client = Rooguys('YOUR_API_KEY')

# With options
client = Rooguys('YOUR_API_KEY', {
    'base_url': 'https://api.rooguys.com/v1',
    'timeout': 20,
    # Rate limit handling
    'on_rate_limit_warning': lambda info: print(f"Rate limit: {info['remaining']}/{info['limit']}"),
    'auto_retry': True,
    'max_retries': 3,
    'retry_delay': 1.0,
})
```

### Features

- Event tracking (`events.track`)
- Batch event tracking (`events.track_batch`)
- User management (`users.create`, `users.update`, `users.create_batch`)
- User search (`users.search`)
- Field selection for user profiles
- Leaderboard filters (persona, level range, date range)
- "Around me" leaderboard view (`leaderboards.get_around_user`)
- Health check endpoints
- Rate limit handling with auto-retry
- Typed exception classes

## Usage Examples

### Events

#### Track a Single Event

```python
response = client.events.track(
    event_name='level-completed',
    user_id='user_123',
    properties={'difficulty': 'hard', 'score': 1500},
    options={
        'include_profile': True,
        'idempotency_key': 'unique-request-id'
    }
)

print(f"Event status: {response['status']}")
if response.get('profile'):
    print(f"Updated points: {response['profile']['points']}")
```

#### Track Events with Custom Timestamp

```python
from datetime import datetime, timedelta

# Track historical events (up to 7 days in the past)
response = client.events.track(
    event_name='purchase',
    user_id='user_123',
    properties={'amount': 99.99},
    options={'timestamp': datetime(2024, 1, 15, 10, 30, 0)}
)
```

#### Batch Event Tracking

```python
# Track up to 100 events in a single request
response = client.events.track_batch([
    {'event_name': 'page-view', 'user_id': 'user_123', 'properties': {'page': '/home'}},
    {'event_name': 'button-click', 'user_id': 'user_123', 'properties': {'button': 'signup'}},
    {'event_name': 'purchase', 'user_id': 'user_456', 'properties': {'amount': 50}},
], options={'idempotency_key': 'batch-123'})

# Check individual results
for result in response['results']:
    if result['status'] == 'queued':
        print(f"Event {result['index']} queued successfully")
    else:
        print(f"Event {result['index']} failed: {result.get('error')}")
```

### Users

#### Create a New User

```python
user = client.users.create({
    'user_id': 'user_123',
    'display_name': 'John Doe',
    'email': 'john@example.com',
    'metadata': {'plan': 'premium'}
})
```

#### Update User Profile

```python
# Partial update - only sends provided fields
updated = client.users.update('user_123', {
    'display_name': 'Johnny Doe',
    'metadata': {'plan': 'enterprise'}
})
```

#### Batch User Creation

```python
response = client.users.create_batch([
    {'user_id': 'user_1', 'display_name': 'User One', 'email': 'one@example.com'},
    {'user_id': 'user_2', 'display_name': 'User Two', 'email': 'two@example.com'},
    # ... up to 100 users
])
```

#### Get User Profile with Field Selection

```python
# Only fetch specific fields
user = client.users.get('user_123', options={
    'fields': ['points', 'level', 'badges']
})
```

#### Search Users

```python
results = client.users.search('john', options={
    'page': 1,
    'limit': 20
})

for user in results['users']:
    print(f"{user['display_name']}: {user['points']} points")
```

#### Access Enhanced Profile Data

```python
user = client.users.get('user_123')

# Activity summary
if user.get('activity_summary'):
    print(f"Last active: {user['activity_summary']['last_event_at']}")
    print(f"Total events: {user['activity_summary']['event_count']}")
    print(f"Days active: {user['activity_summary']['days_active']}")

# Streak information
if user.get('streak'):
    print(f"Current streak: {user['streak']['current_streak']} days")
    print(f"Longest streak: {user['streak']['longest_streak']} days")

# Inventory summary
if user.get('inventory'):
    print(f"Items owned: {user['inventory']['item_count']}")
    print(f"Active effects: {', '.join(user['inventory']['active_effects'])}")
```

### Leaderboards

#### Global Leaderboard with Filters

```python
from datetime import datetime

leaderboard = client.leaderboards.get_global(
    timeframe='weekly',
    page=1,
    limit=10,
    options={
        'persona': 'competitor',
        'min_level': 5,
        'max_level': 20,
        'start_date': datetime(2024, 1, 1),
        'end_date': datetime(2024, 1, 31)
    }
)

# Access cache metadata
if leaderboard.get('cache_metadata'):
    print(f"Cached at: {leaderboard['cache_metadata']['cached_at']}")
    print(f"TTL: {leaderboard['cache_metadata']['ttl']}s")

# Rankings include percentile
for entry in leaderboard['rankings']:
    print(f"#{entry['rank']} {entry['user_id']}: {entry['points']} pts (top {entry.get('percentile')}%)")
```

#### Custom Leaderboard with Filters

```python
custom_lb = client.leaderboards.get_custom(
    'leaderboard_id',
    page=1,
    limit=10,
    options={
        'persona': 'achiever',
        'min_level': 10
    }
)
```

#### "Around Me" View

```python
# Get entries around a specific user
around_me = client.leaderboards.get_around_user(
    'leaderboard_id',
    'user_123',
    range_size=5  # 5 entries above and below
)

for entry in around_me['rankings']:
    marker = '→' if entry['user_id'] == 'user_123' else ' '
    print(f"{marker} #{entry['rank']} {entry['user_id']}: {entry['points']}")
```

#### Get User Rank with Percentile

```python
rank = client.leaderboards.get_user_rank('leaderboard_id', 'user_123')

print(f"Rank: #{rank['rank']}")
print(f"Score: {rank['points']}")
print(f"Percentile: top {rank.get('percentile')}%")
```

### Health Checks

```python
# Full health check
health = client.health.check()
print(f"Status: {health['status']}")
print(f"Version: {health.get('version')}")

# Quick availability check
is_ready = client.health.is_ready()
if is_ready:
    print('API is ready')
```

### Aha Score

```python
# Declare user activation milestone (1-5)
result = client.aha.declare('user_123', 4)
print(result['message'])

# Get user's aha score
score = client.aha.get_user_score('user_123')
print(f"Current Score: {score['data']['current_score']}")
print(f"Status: {score['data']['status']}")
```

## API Reference

### Events

| Method | Description |
|--------|-------------|
| `track(event_name, user_id, properties=None, options=None)` | Track a single event |
| `track_batch(events, options=None)` | Track multiple events (max 100) |

### Users

| Method | Description |
|--------|-------------|
| `create(user_data)` | Create a new user |
| `update(user_id, user_data)` | Update user profile (partial update) |
| `create_batch(users)` | Create multiple users (max 100) |
| `get(user_id, options=None)` | Get user profile with optional field selection |
| `search(query, options=None)` | Search users with pagination |
| `get_bulk(user_ids)` | Get multiple user profiles |
| `get_badges(user_id)` | Get user's badges |
| `get_rank(user_id, timeframe='all-time')` | Get user's global rank |
| `submit_answers(user_id, questionnaire_id, answers)` | Submit questionnaire answers |

### Leaderboards

| Method | Description |
|--------|-------------|
| `get_global(timeframe='all-time', page=1, limit=50, options=None)` | Get global leaderboard with filters |
| `list(page=1, limit=50, search=None)` | List all leaderboards |
| `get_custom(leaderboard_id, page=1, limit=50, search=None, options=None)` | Get custom leaderboard with filters |
| `get_user_rank(leaderboard_id, user_id)` | Get user's rank in leaderboard |
| `get_around_user(leaderboard_id, user_id, range_size=5)` | Get entries around a user |

### Badges

| Method | Description |
|--------|-------------|
| `list(page=1, limit=50, active_only=False)` | List all badges |

### Levels

| Method | Description |
|--------|-------------|
| `list(page=1, limit=50)` | List all levels |

### Questionnaires

| Method | Description |
|--------|-------------|
| `get(slug)` | Get questionnaire by slug |
| `get_active()` | Get active questionnaire |

### Aha Score

| Method | Description |
|--------|-------------|
| `declare(user_id, value)` | Declare aha score (1-5) |
| `get_user_score(user_id)` | Get user's aha score |

### Health

| Method | Description |
|--------|-------------|
| `check()` | Get full health status |
| `is_ready()` | Quick availability check (returns bool) |

## Error Handling

The SDK provides typed exception classes for different error scenarios:

```python
from rooguys import Rooguys
from rooguys.errors import (
    RooguysError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError
)

try:
    client.users.create({'user_id': 'user_123', 'email': 'invalid-email'})
except ValidationError as e:
    print(f'Validation failed: {e.message}')
    print(f'Field errors: {e.field_errors}')
    print(f'Error code: {e.code}')
except AuthenticationError as e:
    print('Invalid API key')
except NotFoundError as e:
    print('Resource not found')
except ConflictError as e:
    print('Resource already exists')
except RateLimitError as e:
    print(f'Rate limited. Retry after {e.retry_after} seconds')
except ServerError as e:
    print(f'Server error: {e.message}')
except RooguysError as e:
    # Catch-all for any Rooguys error
    print(f'Error: {e.message}')
    print(f'Request ID: {e.request_id}')
```

### Exception Types

| Exception Class | HTTP Status | Description |
|-----------------|-------------|-------------|
| `ValidationError` | 400 | Invalid input data |
| `AuthenticationError` | 401 | Invalid or missing API key |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Resource already exists |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ServerError` | 500+ | Server-side error |

### Exception Properties

All exceptions inherit from `RooguysError` and include:
- `message: str` - Human-readable error message
- `code: str` - Machine-readable error code (e.g., `INVALID_EMAIL`, `USER_NOT_FOUND`)
- `request_id: Optional[str]` - Unique request identifier for debugging
- `status_code: int` - HTTP status code

`ValidationError` also includes:
- `field_errors: Optional[List[Dict[str, str]]]` - List of `{'field': ..., 'message': ...}` for field-level errors

`RateLimitError` also includes:
- `retry_after: int` - Seconds until rate limit resets

### Converting Exceptions to Dict

```python
try:
    client.users.get('unknown_user')
except RooguysError as e:
    error_dict = e.to_dict()
    # {
    #     'name': 'NotFoundError',
    #     'message': 'User not found',
    #     'code': 'USER_NOT_FOUND',
    #     'request_id': 'req_abc123',
    #     'status_code': 404
    # }
```

## Rate Limiting

The SDK provides built-in rate limit handling:

```python
def on_rate_limit_warning(info):
    print(f"Rate limit: {info['remaining']}/{info['limit']} remaining")
    print(f"Resets at: {info['reset']}")

client = Rooguys('YOUR_API_KEY', {
    # Get notified when 80% of rate limit is consumed
    'on_rate_limit_warning': on_rate_limit_warning,
    
    # Automatically retry rate-limited requests
    'auto_retry': True,
    'max_retries': 3,
    'retry_delay': 1.0  # Base delay in seconds (exponential backoff)
})
```

### Rate Limit Info Structure

```python
{
    'limit': 1000,      # Total requests allowed
    'remaining': 950,   # Requests remaining
    'reset': 1704067200 # Unix timestamp when limit resets
}
```

## Testing

```bash
pytest                           # Run all tests
pytest --cov=rooguys             # Run with coverage
pytest --cov=rooguys --cov-report=html  # Generate HTML coverage report
```

The SDK maintains >90% test coverage with:
- Unit tests for all API methods
- Property-based tests using Hypothesis
- Exception handling validation
- Rate limit handling tests

### Property-Based Testing

The SDK uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing:

```python
from hypothesis import given, settings
import hypothesis.strategies as st

@given(
    user_id=st.text(min_size=1, max_size=255),
    event_name=st.text(min_size=1, max_size=100)
)
@settings(max_examples=100)
def test_event_tracking_request_construction(user_id, event_name):
    """Property: Event tracking constructs valid HTTP requests"""
    # Test implementation
```

## Requirements

- Python 3.8 or higher
- `requests` library (automatically installed)

## License

MIT
