"""Test data for Strands session tests based on actual runtime execution."""

# CREATE SESSION TEST DATA
CREATE_SESSION_TEST_DATA = [
    # (test_name, has_custom_state, should_fail, expected_exception)
    ("create_with_default_state", False, False, None),
    ("create_with_custom_state", True, False, None),
]

# READ SESSION TEST DATA
READ_SESSION_TEST_DATA = [
    # (test_name, session_exists, should_fail, expected_exception)
    ("read_existing_session", True, False, None),
    ("read_non_existent_session_404", False, False, None),
]

# CREATE AGENT TEST DATA
CREATE_AGENT_TEST_DATA = [
    # (test_name, agent_id, has_state, agent_type, should_fail, expected_exception)
    ("create_agent_default", "default", True, "agent_creation", False, None),
    ("create_agent_custom", "custom_agent", True, "agent_creation", False, None),
]

# READ AGENT TEST DATA
READ_AGENT_TEST_DATA = [
    # (test_name, agent_exists, events_count, should_fail, expected_exception)
    ("read_existing_agent", True, 3, False, None),
    ("read_non_existent_agent", False, 0, False, None),
    ("read_from_empty_session", True, 0, False, None),
]

# UPDATE AGENT TEST DATA
UPDATE_AGENT_TEST_DATA = [
    # (test_name, agent_id, has_new_state, should_fail, expected_exception)
    ("update_agent_state", "default", True, False, None),
    ("update_agent_conversation_state", "default", True, False, None),
]

# CREATE MESSAGE TEST DATA
CREATE_MESSAGE_TEST_DATA = [
    # (test_name, role, content, message_id, should_fail, expected_exception)
    ("create_user_message", "user", [{"text": "my name is madhu"}], 0, False, None),
    ("create_assistant_message", "assistant", [{"text": "Nice to meet you, Madhu!"}], 1, False, None),
]

# READ MESSAGE TEST DATA
READ_MESSAGE_TEST_DATA = [
    # (test_name, message_exists, message_id, should_fail, expected_exception)
    ("read_existing_message", True, 0, False, None),
    ("read_non_existent_message", False, 999, False, None),
]

# UPDATE MESSAGE TEST DATA
UPDATE_MESSAGE_TEST_DATA = [
    # (test_name, message_id, redact, should_fail, expected_exception)
    ("update_message_redact", 1, True, False, None),
    ("update_message_normal", 2, False, False, None),
]

# LIST MESSAGES TEST DATA
LIST_MESSAGES_TEST_DATA = [
    # (test_name, total_messages, limit, offset, expected_count, should_fail, expected_exception)
    ("list_all_messages", 5, None, 0, 5, False, None),
    ("list_with_limit", 10, 5, 0, 5, False, None),
    ("list_with_offset", 10, None, 3, 7, False, None),
    ("list_with_limit_and_offset", 10, 3, 2, 3, False, None),
    ("list_empty", 0, None, 0, 0, False, None),
]

