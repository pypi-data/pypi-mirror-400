"""Test data for Langgraph session parametrized tests."""

import time
import uuid


# ==================== GET TUPLE TEST DATA ====================

GET_TUPLE_TEST_DATA = [
    # Format: (test_name, session_exists, has_events, events_count, should_fail, expected_exception)
    (
        "get_tuple_with_events",
        True,
        True,
        3,
        False,
        None
    ),
    (
        "get_tuple_session_not_found_creates_new",
        False,
        False,
        0,
        False,
        None
    ),
    (
        "get_tuple_no_events_returns_none",
        True,
        False,
        0,
        False,
        None
    ),
]


# ==================== PUT TEST DATA ====================

PUT_TEST_DATA = [
    # Format: (test_name, has_messages, messages_count, should_fail, expected_exception)
    (
        "put_with_messages",
        True,
        2,
        False,
        None
    ),
    (
        "put_without_messages",
        False,
        0,
        False,
        None
    ),
    (
        "put_with_single_message",
        True,
        1,
        False,
        None
    ),
]


# ==================== PUT WRITES TEST DATA ====================

PUT_WRITES_TEST_DATA = [
    # Format: (test_name, writes_count, should_fail, expected_exception)
    (
        "put_writes_single",
        1,
        False,
        None
    ),
    (
        "put_writes_multiple",
        3,
        False,
        None
    ),
]


# ==================== LIST TEST DATA ====================

LIST_TEST_DATA = [
    # Format: (test_name, sessions_count, limit, should_fail, expected_exception)
    (
        "list_multiple_sessions",
        3,
        None,
        False,
        None
    ),
    (
        "list_with_limit",
        5,
        2,
        False,
        None
    ),
    (
        "list_empty",
        0,
        None,
        False,
        None
    ),
]


# ==================== DELETE THREAD TEST DATA ====================

DELETE_THREAD_TEST_DATA = [
    # Format: (test_name, thread_exists, should_fail, expected_exception)
    (
        "delete_existing_thread",
        True,
        False,
        None
    ),
    (
        "delete_non_existent_thread",
        False,
        False,
        None
    ),
]

