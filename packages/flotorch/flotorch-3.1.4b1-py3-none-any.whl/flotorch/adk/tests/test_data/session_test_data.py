"""Test data for ADK session parametrized tests."""

# ==================== CREATE SESSION TEST DATA ====================

CREATE_SESSION_TEST_DATA = [
    # Format: (test_name, session_id, state, should_fail, expected_exception)
    (
        "valid_with_session_id",
        "session-123",
        {"key": "value"},
        False,
        None
    ),
    (
        "valid_without_session_id",
        None,  # Auto-generated
        {},
        False,
        None
    ),
    (
        "with_initial_state",
        "session-456",
        {"setting1": "value1", "setting2": "value2"},
        False,
        None
    ),
    (
        "with_empty_state",
        "session-789",
        {},
        False,
        None
    ),
]


# ==================== GET SESSION TEST DATA ====================

GET_SESSION_TEST_DATA = [
    # Format: (test_name, session_exists, events_count, has_state, should_fail, expected_exception)
    (
        "existing_session_with_events",
        True,
        3,
        True,
        False,
        None
    ),
    (
        "existing_session_without_events",
        True,
        0,
        False,
        False,
        None
    ),
    (
        "session_not_found",
        False,
        0,
        False,
        False,
        None
    ),
    (
        "session_with_multiple_events",
        True,
        5,
        True,
        False,
        None
    ),
]


# ==================== LIST SESSIONS TEST DATA ====================

LIST_SESSIONS_TEST_DATA = [
    # Format: (test_name, sessions_count, should_fail, expected_exception)
    (
        "multiple_sessions",
        3,
        False,
        None
    ),
    (
        "single_session",
        1,
        False,
        None
    ),
    (
        "no_sessions",
        0,
        False,
        None
    ),
    (
        "many_sessions",
        10,
        False,
        None
    ),
]


# ==================== DELETE SESSION TEST DATA ====================

DELETE_SESSION_TEST_DATA = [
    # Format: (test_name, session_exists, should_fail, expected_exception)
    (
        "delete_existing_session",
        True,
        False,
        None
    ),
    (
        "delete_non_existent_session",
        False,
        False,
        None
    ),
    (
        "delete_with_api_error",
        True,
        True,
        Exception
    ),
]


# ==================== APPEND EVENT TEST DATA ====================

APPEND_EVENT_TEST_DATA = [
    # Format: (test_name, session_exists, has_content, has_state_delta, state_delta, should_fail, expected_exception)
    (
        "append_event_basic",
        True,
        False,
        False,
        {},
        False,
        None
    ),
    (
        "append_event_with_content",
        True,
        True,
        False,
        {},
        False,
        None
    ),
    (
        "append_event_with_app_state",
        True,
        False,
        True,
        {"app:setting": "value1"},
        False,
        None
    ),
    (
        "append_event_with_user_state",
        True,
        False,
        True,
        {"user:preference": "value2"},
        False,
        None
    ),
    (
        "append_event_with_mixed_state",
        True,
        True,
        True,
        {"app:key1": "val1", "user:key2": "val2"},
        False,
        None
    ),
    (
        "append_event_session_not_found",
        False,
        False,
        False,
        {},
        False,
        None
    ),
]


