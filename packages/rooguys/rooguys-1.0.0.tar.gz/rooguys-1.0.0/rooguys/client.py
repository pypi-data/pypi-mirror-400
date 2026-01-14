"""
Rooguys SDK Client
Main client class and resource modules for interacting with the Rooguys API
"""

from typing import Optional, Dict, List, Any, Callable
from urllib.parse import quote
from datetime import datetime, timedelta, timezone

from .http_client import HttpClient, RateLimitInfo, ApiResponse
from .errors import (
    RooguysError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
)


# Re-export for backward compatibility
RooguysApiError = RooguysError


class Rooguys:
    """
    Main Rooguys SDK client
    
    Example:
        client = Rooguys('your-api-key')
        
        # Track an event
        result = client.events.track('purchase', 'user123', {'amount': 99.99})
        
        # Get user profile
        profile = client.users.get('user123')
    """
    
    def __init__(self, api_key: str, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the Rooguys client
        
        Args:
            api_key: Your Rooguys API key
            options: Optional configuration:
                - base_url: API base URL (default: https://api.rooguys.com/v1)
                - timeout: Request timeout in seconds (default: 10)
                - on_rate_limit_warning: Callback when rate limit is at 80%
                - auto_retry: Enable auto-retry for rate-limited requests
                - max_retries: Maximum number of retries (default: 3)
                - retry_delay: Base delay between retries in seconds (default: 1.0)
        """
        options = options or {}
        
        self._http_client = HttpClient(
            api_key=api_key,
            base_url=options.get('base_url', 'https://api.rooguys.com/v1'),
            timeout=options.get('timeout', 10),
            on_rate_limit_warning=options.get('on_rate_limit_warning'),
            auto_retry=options.get('auto_retry', False),
            max_retries=options.get('max_retries', 3),
            retry_delay=options.get('retry_delay', 1.0),
        )
        
        # For backward compatibility
        self.api_key = api_key
        self.base_url = self._http_client.base_url
        self.timeout = self._http_client.timeout
    
    @property
    def session(self):
        """Access to the underlying requests session (for backward compatibility)"""
        return self._http_client.session
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Any:
        """
        Make an API request (backward compatible method)
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: Request body
            params: Query parameters
            idempotency_key: Idempotency key for POST requests
        
        Returns:
            Response data (unwrapped from ApiResponse)
        """
        response = self._http_client.request(
            method=method,
            path=endpoint,
            body=data,
            params=params,
            idempotency_key=idempotency_key,
        )
        return response.data
    
    def _request_with_metadata(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> ApiResponse:
        """
        Make an API request and return full response with metadata
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            data: Request body
            params: Query parameters
            idempotency_key: Idempotency key for POST requests
        
        Returns:
            ApiResponse with data, request_id, rate_limit, and pagination
        """
        return self._http_client.request(
            method=method,
            path=endpoint,
            body=data,
            params=params,
            idempotency_key=idempotency_key,
        )

    @property
    def events(self):
        """Events resource for tracking user events"""
        return EventsResource(self)

    @property
    def users(self):
        """Users resource for user profile operations"""
        return UsersResource(self)

    @property
    def leaderboards(self):
        """Leaderboards resource for ranking operations"""
        return LeaderboardsResource(self)

    @property
    def badges(self):
        """Badges resource for badge operations"""
        return BadgesResource(self)

    @property
    def levels(self):
        """Levels resource for level operations"""
        return LevelsResource(self)

    @property
    def questionnaires(self):
        """Questionnaires resource for questionnaire operations"""
        return QuestionnairesResource(self)

    @property
    def aha(self):
        """Aha resource for aha moment score operations"""
        return AhaResource(self)
    
    @property
    def health(self):
        """Health resource for API health checks"""
        return HealthResource(self)


class Resource:
    """Base class for API resources"""
    
    def __init__(self, client: Rooguys):
        self.client = client


class EventsResource(Resource):
    """Events resource for tracking user events"""
    
    def track(
        self,
        event_name: str,
        user_id: str,
        properties: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Track a single event
        
        Args:
            event_name: Name of the event
            user_id: User identifier
            properties: Event properties
            options: Additional options:
                - include_profile: Include user profile in response
                - timestamp: Custom timestamp (ISO 8601 string or datetime)
                - idempotency_key: Idempotency key for deduplication
        
        Returns:
            Event tracking response
        """
        properties = properties or {}
        options = options or {}
        params = {}
        
        if options.get('include_profile'):
            params['include_profile'] = 'true'
        
        body = {
            'event_name': event_name,
            'user_id': user_id,
            'properties': properties
        }
        
        # Add custom timestamp if provided
        if options.get('timestamp'):
            timestamp = options['timestamp']
            # Validate timestamp is not more than 7 days in the past
            self._validate_timestamp(timestamp)
            if hasattr(timestamp, 'isoformat'):
                timestamp = timestamp.isoformat()
            body['timestamp'] = timestamp
        
        return self.client._request(
            'POST',
            '/events',  # Updated to new route
            body,
            params=params,
            idempotency_key=options.get('idempotency_key')
        )
    
    @staticmethod
    def _validate_timestamp(timestamp) -> None:
        """
        Validate that timestamp is not more than 7 days in the past
        
        Args:
            timestamp: Timestamp to validate (datetime or ISO 8601 string)
        
        Raises:
            ValidationError: If timestamp is more than 7 days in the past
        """
        if timestamp is None:
            return
        
        # Convert string to datetime if needed
        if isinstance(timestamp, str):
            try:
                # Parse ISO 8601 format
                if timestamp.endswith('Z'):
                    timestamp = timestamp[:-1] + '+00:00'
                ts = datetime.fromisoformat(timestamp)
            except ValueError:
                raise ValidationError(
                    'Invalid timestamp format',
                    code='INVALID_TIMESTAMP'
                )
        elif hasattr(timestamp, 'timestamp'):
            ts = timestamp
        else:
            raise ValidationError(
                'Invalid timestamp format',
                code='INVALID_TIMESTAMP'
            )
        
        # Ensure timezone-aware comparison
        now = datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        seven_days_ago = now - timedelta(days=7)
        if ts < seven_days_ago:
            raise ValidationError(
                'Timestamp cannot be more than 7 days in the past',
                code='TIMESTAMP_TOO_OLD'
            )
    
    def track_batch(
        self,
        events: List[Dict],
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Track multiple events in a single request
        
        Args:
            events: List of events, each with:
                - event_name: Name of the event
                - user_id: User identifier
                - properties: Event properties (optional)
                - timestamp: Custom timestamp (optional)
            options: Additional options:
                - idempotency_key: Idempotency key for deduplication
        
        Returns:
            Batch tracking response with individual status for each event
        
        Raises:
            ValidationError: If events array is empty or exceeds 100 items,
                           or if any timestamp is more than 7 days in the past
        """
        options = options or {}
        
        # Validate batch size
        if not events:
            raise ValidationError(
                'Events array cannot be empty',
                code='INVALID_BATCH_SIZE'
            )
        
        if len(events) > 100:
            raise ValidationError(
                'Batch size cannot exceed 100 events',
                code='BATCH_SIZE_EXCEEDED'
            )
        
        # Validate timestamps for each event
        for event in events:
            if 'timestamp' in event and event['timestamp'] is not None:
                self._validate_timestamp(event['timestamp'])
        
        return self.client._request(
            'POST',
            '/events/batch',
            {'events': events},
            idempotency_key=options.get('idempotency_key')
        )


class UsersResource(Resource):
    """Users resource for user profile operations"""
    
    def get(
        self,
        user_id: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Get user profile
        
        Args:
            user_id: User identifier
            options: Additional options:
                - fields: List of fields to include in response
        
        Returns:
            User profile data
        """
        options = options or {}
        params = {}
        
        # Add field selection if provided
        if options.get('fields'):
            params['fields'] = ','.join(options['fields'])
        
        return self.client._request(
            'GET',
            f'/user/{quote(user_id, safe="")}',
            params=params
        )

    def get_bulk(self, user_ids: List[str]) -> Dict:
        """
        Get multiple user profiles
        
        Args:
            user_ids: List of user identifiers
        
        Returns:
            Bulk users response
        """
        return self.client._request('POST', '/users/bulk', {'user_ids': user_ids})

    def get_badges(self, user_id: str) -> Dict:
        """
        Get user's earned badges
        
        Args:
            user_id: User identifier
        
        Returns:
            User badges data
        """
        return self.client._request('GET', f'/user/{quote(user_id, safe="")}/badges')

    def get_rank(self, user_id: str, timeframe: str = 'all-time') -> Dict:
        """
        Get user's rank
        
        Args:
            user_id: User identifier
            timeframe: Timeframe for ranking (all-time, weekly, monthly)
        
        Returns:
            User rank data
        """
        return self.client._request(
            'GET',
            f'/user/{quote(user_id, safe="")}/rank',
            params={'timeframe': timeframe}
        )

    def submit_answers(
        self,
        user_id: str,
        questionnaire_id: str,
        answers: List[Dict]
    ) -> Dict:
        """
        Submit questionnaire answers for a user
        
        Args:
            user_id: User identifier
            questionnaire_id: Questionnaire identifier
            answers: List of answers
        
        Returns:
            Submission response
        """
        return self.client._request(
            'POST',
            f'/user/{quote(user_id, safe="")}/answers',
            {
                'questionnaire_id': questionnaire_id,
                'answers': answers
            }
        )
    
    def create(self, user_data: Dict) -> Dict:
        """
        Create a new user
        
        Args:
            user_data: User data including:
                - user_id: User identifier (required)
                - display_name: Display name (optional)
                - email: Email address (optional)
                - metadata: Additional metadata (optional)
        
        Returns:
            Created user profile
        
        Raises:
            ValidationError: If email format is invalid
            ConflictError: If user already exists
        """
        # Client-side email validation
        if 'email' in user_data and user_data['email']:
            email = user_data['email']
            if not self._is_valid_email(email):
                raise ValidationError(
                    'Invalid email format',
                    code='INVALID_EMAIL',
                    field_errors=[{'field': 'email', 'message': 'Invalid email format'}]
                )
        
        return self.client._request('POST', '/users', user_data)
    
    def update(self, user_id: str, user_data: Dict) -> Dict:
        """
        Update an existing user
        
        Args:
            user_id: User identifier
            user_data: Fields to update (partial update supported):
                - display_name: Display name
                - email: Email address
                - metadata: Additional metadata
        
        Returns:
            Updated user profile
        
        Raises:
            ValidationError: If email format is invalid
            NotFoundError: If user doesn't exist
        """
        # Client-side email validation
        if 'email' in user_data and user_data['email']:
            email = user_data['email']
            if not self._is_valid_email(email):
                raise ValidationError(
                    'Invalid email format',
                    code='INVALID_EMAIL',
                    field_errors=[{'field': 'email', 'message': 'Invalid email format'}]
                )
        
        # Only send provided fields (partial update)
        update_data = {k: v for k, v in user_data.items() if v is not None}
        
        return self.client._request(
            'PATCH',
            f'/users/{quote(user_id, safe="")}',
            update_data
        )
    
    def create_batch(self, users: List[Dict]) -> Dict:
        """
        Create multiple users in a single request
        
        Args:
            users: List of user data objects
        
        Returns:
            Batch creation response
        
        Raises:
            ValidationError: If batch is empty or exceeds 100 users
        """
        if not users:
            raise ValidationError(
                'Users array cannot be empty',
                code='INVALID_BATCH_SIZE'
            )
        
        if len(users) > 100:
            raise ValidationError(
                'Batch size cannot exceed 100 users',
                code='BATCH_SIZE_EXCEEDED'
            )
        
        return self.client._request('POST', '/users/batch', {'users': users})
    
    def search(
        self,
        query: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Search for users
        
        Args:
            query: Search query
            options: Additional options:
                - page: Page number (default: 1)
                - limit: Results per page (default: 50)
        
        Returns:
            Paginated search results
        """
        options = options or {}
        params = {
            'q': query,
            'page': options.get('page', 1),
            'limit': options.get('limit', 50),
        }
        
        return self.client._request('GET', '/users/search', params=params)
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class LeaderboardsResource(Resource):
    """Leaderboards resource for ranking operations"""
    
    def get_global(
        self,
        timeframe: str = 'all-time',
        page: int = 1,
        limit: int = 50,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Get global leaderboard
        
        Args:
            timeframe: Timeframe (all-time, weekly, monthly)
            page: Page number
            limit: Results per page
            options: Additional filter options:
                - persona: Filter by persona
                - min_level: Minimum level filter
                - max_level: Maximum level filter
                - start_date: Start date filter (ISO 8601)
                - end_date: End date filter (ISO 8601)
        
        Returns:
            Leaderboard data with rankings
        """
        options = options or {}
        params = {
            'timeframe': timeframe,
            'page': page,
            'limit': limit,
        }
        
        # Add optional filters
        if options.get('persona'):
            params['persona'] = options['persona']
        if options.get('min_level') is not None:
            params['minLevel'] = options['min_level']
        if options.get('max_level') is not None:
            params['maxLevel'] = options['max_level']
        if options.get('start_date'):
            start_date = options['start_date']
            if hasattr(start_date, 'isoformat'):
                start_date = start_date.isoformat()
            params['startDate'] = start_date
        if options.get('end_date'):
            end_date = options['end_date']
            if hasattr(end_date, 'isoformat'):
                end_date = end_date.isoformat()
            params['endDate'] = end_date
        
        return self.client._request(
            'GET',
            '/leaderboards/global',  # Updated to new route
            params=params
        )

    def list(
        self,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None
    ) -> Dict:
        """
        List all leaderboards
        
        Args:
            page: Page number
            limit: Results per page
            search: Search query
        
        Returns:
            Paginated list of leaderboards
        """
        params = {'page': page, 'limit': limit}
        if search:
            params['search'] = search
        return self.client._request('GET', '/leaderboards', params=params)

    def get_custom(
        self,
        leaderboard_id: str,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Get custom leaderboard
        
        Args:
            leaderboard_id: Leaderboard identifier
            page: Page number
            limit: Results per page
            search: Search query
            options: Additional filter options
        
        Returns:
            Leaderboard data with rankings
        """
        options = options or {}
        params = {'page': page, 'limit': limit}
        
        if search:
            params['search'] = search
        
        # Add optional filters
        if options.get('persona'):
            params['persona'] = options['persona']
        if options.get('min_level') is not None:
            params['minLevel'] = options['min_level']
        if options.get('max_level') is not None:
            params['maxLevel'] = options['max_level']
        if options.get('start_date'):
            start_date = options['start_date']
            if hasattr(start_date, 'isoformat'):
                start_date = start_date.isoformat()
            params['startDate'] = start_date
        if options.get('end_date'):
            end_date = options['end_date']
            if hasattr(end_date, 'isoformat'):
                end_date = end_date.isoformat()
            params['endDate'] = end_date
        
        return self.client._request(
            'GET',
            f'/leaderboard/{leaderboard_id}',
            params=params
        )

    def get_user_rank(self, leaderboard_id: str, user_id: str) -> Dict:
        """
        Get user's rank in a leaderboard
        
        Args:
            leaderboard_id: Leaderboard identifier
            user_id: User identifier
        
        Returns:
            User rank data
        """
        return self.client._request(
            'GET',
            f'/leaderboard/{leaderboard_id}/user/{user_id}/rank'
        )
    
    def get_around_user(
        self,
        leaderboard_id: str,
        user_id: str,
        range_size: int = 5
    ) -> Dict:
        """
        Get leaderboard entries around a user
        
        Args:
            leaderboard_id: Leaderboard identifier
            user_id: User identifier
            range_size: Number of entries above and below user
        
        Returns:
            Leaderboard entries around the user
        """
        return self.client._request(
            'GET',
            f'/leaderboard/{leaderboard_id}/around/{user_id}',
            params={'range': range_size}
        )


class BadgesResource(Resource):
    """Badges resource for badge operations"""
    
    def list(
        self,
        page: int = 1,
        limit: int = 50,
        active_only: bool = False
    ) -> Dict:
        """
        List all badges
        
        Args:
            page: Page number
            limit: Results per page
            active_only: Only return active badges
        
        Returns:
            Paginated list of badges
        """
        return self.client._request('GET', '/badges', params={
            'page': page,
            'limit': limit,
            'active_only': str(active_only).lower()
        })


class LevelsResource(Resource):
    """Levels resource for level operations"""
    
    def list(self, page: int = 1, limit: int = 50) -> Dict:
        """
        List all levels
        
        Args:
            page: Page number
            limit: Results per page
        
        Returns:
            Paginated list of levels
        """
        return self.client._request('GET', '/levels', params={
            'page': page,
            'limit': limit
        })


class QuestionnairesResource(Resource):
    """Questionnaires resource for questionnaire operations"""
    
    def get(self, slug: str) -> Dict:
        """
        Get questionnaire by slug
        
        Args:
            slug: Questionnaire slug
        
        Returns:
            Questionnaire data
        """
        return self.client._request('GET', f'/questionnaire/{slug}')

    def get_active(self) -> Dict:
        """
        Get active questionnaire
        
        Returns:
            Active questionnaire data
        """
        return self.client._request('GET', '/questionnaire/active')


class AhaResource(Resource):
    """Aha resource for aha moment score operations"""
    
    def declare(self, user_id: str, value: int) -> Dict:
        """
        Declare aha moment score for a user
        
        Args:
            user_id: User identifier
            value: Score value (1-5)
        
        Returns:
            Declaration response
        
        Raises:
            ValueError: If value is not between 1 and 5
        """
        # Validate value is between 1 and 5
        if not isinstance(value, int) or value < 1 or value > 5:
            raise ValueError('Aha score value must be an integer between 1 and 5')
        
        return self.client._request('POST', '/aha/declare', {
            'user_id': user_id,
            'value': value
        })

    def get_user_score(self, user_id: str) -> Dict:
        """
        Get user's aha moment score
        
        Args:
            user_id: User identifier
        
        Returns:
            User's aha score data
        """
        return self.client._request('GET', f'/users/{quote(user_id, safe="")}/aha')


class HealthResource(Resource):
    """Health resource for API health checks"""
    
    def check(self) -> Dict:
        """
        Check API health status
        
        Returns:
            Health status including service status and version
        """
        return self.client._request('GET', '/health')
    
    def is_ready(self) -> bool:
        """
        Quick availability check
        
        Returns:
            True if API is ready, False otherwise
        """
        try:
            result = self.check()
            return result.get('status') == 'ok' or result.get('status') == 'healthy'
        except Exception:
            return False
