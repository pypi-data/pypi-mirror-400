"""Mock API response fixtures for testing"""

mock_responses = {
    'user_profile': {
        'user_id': 'user123',
        'points': 100,
        'persona': 'Achiever',
        'level': {
            'id': 'level1',
            'name': 'Bronze',
            'level_number': 1,
            'points_required': 0,
        },
        'next_level': {
            'id': 'level2',
            'name': 'Silver',
            'level_number': 2,
            'points_required': 500,
            'points_needed': 400,
        },
        'metrics': {
            'logins': 10,
            'purchases': 2,
        },
        'badges': [
            {
                'id': 'badge1',
                'name': 'First Steps',
                'description': 'Completed first action',
                'icon_url': 'https://example.com/badge1.png',
                'earned_at': '2024-01-01T00:00:00Z',
            },
        ],
    },
    
    'track_event_response': {
        'status': 'queued',
        'message': 'Event accepted for processing',
    },
    
    'track_event_with_profile_response': {
        'status': 'queued',
        'message': 'Event accepted for processing',
        'profile': {
            'user_id': 'user123',
            'points': 110,
            'persona': 'Achiever',
            'level': {
                'id': 'level1',
                'name': 'Bronze',
                'level_number': 1,
                'points_required': 0,
            },
            'next_level': {
                'id': 'level2',
                'name': 'Silver',
                'level_number': 2,
                'points_required': 500,
                'points_needed': 390,
            },
            'metrics': {},
            'badges': [],
        },
    },
    
    'leaderboard_response': {
        'timeframe': 'all-time',
        'page': 1,
        'limit': 50,
        'total': 100,
        'rankings': [
            {
                'rank': 1,
                'user_id': 'user1',
                'points': 1000,
                'level': {
                    'id': 'level3',
                    'name': 'Gold',
                    'level_number': 3,
                },
            },
            {
                'rank': 2,
                'user_id': 'user2',
                'points': 900,
                'level': {
                    'id': 'level2',
                    'name': 'Silver',
                    'level_number': 2,
                },
            },
        ],
    },
    
    'user_rank_response': {
        'user_id': 'user123',
        'rank': 42,
        'points': 850,
        'total_users': 1000,
    },
    
    'badges_list_response': {
        'badges': [
            {
                'id': 'badge1',
                'name': 'First Steps',
                'description': 'Completed first action',
                'icon_url': 'https://example.com/badge1.png',
                'is_active': True,
                'unlock_criteria': {
                    'metric': 'actions',
                    'value': 1,
                },
            },
        ],
        'pagination': {
            'page': 1,
            'limit': 50,
            'total': 10,
            'totalPages': 1,
        },
    },
    
    'levels_list_response': {
        'levels': [
            {
                'id': 'level1',
                'name': 'Bronze',
                'level_number': 1,
                'points_required': 0,
                'description': 'Starting level',
                'icon_url': 'https://example.com/bronze.png',
            },
            {
                'id': 'level2',
                'name': 'Silver',
                'level_number': 2,
                'points_required': 500,
                'description': 'Intermediate level',
                'icon_url': 'https://example.com/silver.png',
            },
        ],
        'pagination': {
            'page': 1,
            'limit': 50,
            'total': 5,
            'totalPages': 1,
        },
    },
    
    'questionnaire_response': {
        'id': 'questionnaire1',
        'slug': 'user-persona',
        'title': 'User Persona Quiz',
        'description': 'Determine your user persona',
        'is_active': True,
        'questions': [
            {
                'id': 'q1',
                'text': 'What motivates you?',
                'order': 1,
                'answer_options': [
                    {
                        'id': 'a1',
                        'text': 'Competition',
                        'persona_weights': {'Competitor': 1},
                    },
                    {
                        'id': 'a2',
                        'text': 'Exploration',
                        'persona_weights': {'Explorer': 1},
                    },
                ],
            },
        ],
    },
    
    'bulk_users_response': {
        'users': [
            {
                'user_id': 'user1',
                'points': 100,
                'persona': None,
                'level': None,
                'next_level': None,
                'metrics': {},
                'badges': [],
            },
            {
                'user_id': 'user2',
                'points': 200,
                'persona': 'Achiever',
                'level': {
                    'id': 'level1',
                    'name': 'Bronze',
                    'level_number': 1,
                    'points_required': 0,
                },
                'next_level': None,
                'metrics': {},
                'badges': [],
            },
        ],
    },
    
    'aha_score_response': {
        'success': True,
        'data': {
            'user_id': 'user123',
            'current_score': 75,
            'declarative_score': 80,
            'inferred_score': 70,
            'status': 'activated',
            'history': {
                'initial': 50,
                'initial_date': '2024-01-01T00:00:00Z',
                'previous': 70,
            },
        },
    },
    
    'aha_declaration_response': {
        'success': True,
        'message': 'Declarative score recorded. Calculation in progress.',
    },
    
    'answer_submission_response': {
        'status': 'accepted',
        'message': 'Answers queued for processing',
    },
    
    'leaderboards_list_response': {
        'leaderboards': [
            {
                'id': 'lb1',
                'name': 'Top Players',
                'description': 'Overall top players',
                'type': 'POINTS',
                'timeframe': 'all-time',
                'is_active': True,
                'created_at': '2024-01-01T00:00:00Z',
            },
        ],
        'pagination': {
            'page': 1,
            'limit': 50,
            'total': 5,
            'totalPages': 1,
        },
    },
    
    'custom_leaderboard_response': {
        'leaderboard': {
            'id': 'lb1',
            'name': 'Top Players',
            'description': 'Overall top players',
            'type': 'POINTS',
            'timeframe': 'all-time',
            'is_active': True,
            'created_at': '2024-01-01T00:00:00Z',
        },
        'rankings': [
            {
                'rank': 1,
                'user_id': 'user1',
                'points': 1000,
                'level': None,
            },
        ],
        'pagination': {
            'page': 1,
            'limit': 50,
            'total': 10,
            'totalPages': 1,
        },
    },
}

mock_errors = {
    'validation_error': {
        'error': 'Validation failed',
        'details': [
            {
                'field': 'user_id',
                'message': 'User ID is required',
            },
        ],
    },
    
    'not_found_error': {
        'error': 'User not found',
        'message': "User 'user123' does not exist in this project",
    },
    
    'server_error': {
        'error': 'Internal server error',
    },
    
    'queue_full_error': {
        'error': 'Service unavailable',
        'message': 'Event queue is full. Please retry later.',
    },
    
    'unauthorized_error': {
        'error': 'Unauthorized',
        'message': 'Invalid or missing API key',
    },
    
    'invalid_timeframe_error': {
        'error': 'Invalid timeframe',
        'message': 'Timeframe must be one of: all-time, weekly, monthly',
    },
    
    'invalid_pagination_error': {
        'error': 'Invalid limit parameter',
        'message': 'Limit must be between 1 and 100',
    },
    
    'aha_value_error': {
        'error': 'Validation failed',
        'details': [
            {
                'field': 'value',
                'message': 'value must be an integer between 1 and 5',
            },
        ],
    },
}
