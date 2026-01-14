"""Property-based testing generators using Hypothesis"""
from hypothesis import strategies as st
import string

# User ID: 1-255 characters
user_id_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + '_-',
    min_size=1,
    max_size=255
).filter(lambda s: s.strip())

# Event name: 1-100 characters
event_name_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + '_-',
    min_size=1,
    max_size=100
).filter(lambda s: s.strip())

# Properties: JSON-serializable dictionary
properties_strategy = st.dictionaries(
    keys=st.text(min_size=1, max_size=50),
    values=st.one_of(
        st.text(),
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.booleans(),
        st.none()
    ),
    max_size=20
)

# Timeframe: one of the valid values
timeframe_strategy = st.sampled_from(['all-time', 'weekly', 'monthly'])

# Page number: 1-1000
page_strategy = st.integers(min_value=1, max_value=1000)

# Limit: 1-100
limit_strategy = st.integers(min_value=1, max_value=100)

# Aha score value: 1-5
aha_value_strategy = st.integers(min_value=1, max_value=5)

# Invalid Aha score value: outside 1-5 range
invalid_aha_value_strategy = st.one_of(
    st.integers(max_value=0),
    st.integers(min_value=6)
)

# UUID for leaderboard IDs
uuid_strategy = st.uuids().map(str)

# Slug for questionnaires
slug_strategy = st.text(
    alphabet=string.ascii_lowercase + string.digits + '-',
    min_size=1,
    max_size=100
).filter(lambda s: s and not s.startswith('-') and not s.endswith('-'))

# Array of user IDs for bulk operations
user_ids_strategy = st.lists(
    user_id_strategy,
    min_size=1,
    max_size=100
)

# Boolean for active_only filter
active_only_strategy = st.booleans()

# Search query (optional)
search_query_strategy = st.one_of(
    st.none(),
    st.text(max_size=100)
)

# Base URL
base_url_strategy = st.from_regex(
    r'https?://[a-z0-9-]+(\.[a-z0-9-]+)*(:[0-9]+)?',
    fullmatch=True
)

# Timeout in seconds
timeout_strategy = st.integers(min_value=1, max_value=60)

# API key
api_key_strategy = st.text(
    alphabet=string.ascii_letters + string.digits,
    min_size=10,
    max_size=100
)

# Questionnaire answers
questionnaire_answers_strategy = st.lists(
    st.fixed_dictionaries({
        'question_id': uuid_strategy,
        'answer_option_id': uuid_strategy,
    }),
    min_size=1,
    max_size=20
)
