"""Test data for autogen sessions function parametrized tests."""

from autogen_core import FunctionCall
from autogen_core.models import (
    UserMessage,
    SystemMessage,
    AssistantMessage,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
)

# Sample message for testing (used in test_sessions.py)
SAMPLE_USER_MESSAGE = UserMessage(content="Hi my name is Ashok", source="user")

# Test data for _autogen_to_flotorch_event method
AUTOGEN_TO_FLOTORCH_TEST_DATA = [
    (
        "user_message_string_content",
        UserMessage(content="Hi my name is Ashok", source="user"),
        ("user", {"message": "Hi my name is Ashok"})
    ),
    (
        "system_message_string_content",
        SystemMessage(content="You are a helpful assistant", source="system"),
        ("system", {"message": "You are a helpful assistant"})
    ),
    (
        "assistant_message_string_content",
        AssistantMessage(content="Hello, Ashok! How can I assist you today?",
                         source="FlotorchAssistant"),
        ("assistant", {"message": "Hello, Ashok! How can I assist you today?"})
    ),
    (
        "assistant_message_with_tool_calls",
        AssistantMessage(
            content=[FunctionCall(
                id="call_123",
                name="calculate",
                arguments='{"expression": "21+213"}'
            )],
            source="FlotorchAssistant"
        ),
        ("assistant", {
            "tool_calls": [{
                "id": "call_123",
                "function": {
                    "name": "calculate",
                    "arguments": '{"expression": "21+213"}'
                }
            }]
        })
    ),
    (
        "function_execution_result_message",
        FunctionExecutionResultMessage(
            content=[FunctionExecutionResult(
                call_id="call_123",
                name="calculate",
                content="234",
                is_error=False
            )],
            source="tool"
        ),
        ("tool", {
            "tool_outputs": [{
                "tool_call_id": "call_123",
                "name": "calculate",
                "output": "234",
                "is_error": False
            }]
        })
    ),
]

# Test data for _flotorch_to_autogen_message method
FLOTORCH_TO_AUTOGEN_TEST_DATA = [
    (
        "user_event_with_message",
        {
            "author": "user",
            "content": {"message": "Hi my name is Ashok"},
            "timestamp": 1640995200000
        },
        UserMessage(content="Hi my name is Ashok", source="user")
    ),
    (
        "system_event_with_message",
        {
            "author": "system",
            "content": {"message": "You are a helpful assistant"},
            "timestamp": 1640995200000
        },
        SystemMessage(content="You are a helpful assistant", source="system")
    ),
    (
        "assistant_event_with_message",
        {
            "author": "assistant",
            "content": {"message": "Hello, Ashok! How can I assist you today?"},
            "timestamp": 1640995200000
        },
        AssistantMessage(content="Hello, Ashok! How can I assist you today?",
                         source="assistant")
    ),
    (
        "assistant_event_with_tool_calls",
        {
            "author": "assistant",
            "content": {
                "tool_calls": [{
                    "id": "call_123",
                    "function": {
                        "name": "calculate",
                        "arguments": '{"expression": "21+213"}'
                    }
                }]
            },
            "timestamp": 1640995200000
        },
        AssistantMessage(
            content=[FunctionCall(id="call_123", name="calculate",
                                  arguments='{"expression": "21+213"}')],
            source="assistant"
        )
    ),
    (
        "tool_event_with_outputs",
        {
            "author": "tool",
            "content": {
                "tool_outputs": [{
                    "tool_call_id": "call_123",
                    "name": "calculate",
                    "output": "234",
                    "is_error": False
                }]
            },
            "timestamp": 1640995200000
        },
        FunctionExecutionResultMessage(
            content=[FunctionExecutionResult(
                call_id="call_123",
                name="calculate",
                content="234",
                is_error=False
            )],
            source="tool"
        )
    ),
    (
        "event_without_author",
        {
            "content": {"message": "No author"},
            "timestamp": 1640995200000
        },
        None
    ),
    (
        "event_with_empty_content",
        {
            "author": "user",
            "content": {},
            "timestamp": 1640995200000
        },
        UserMessage(content="", source="user")
    ),
    (
        "unknown_author_event",
        {
            "author": "unknown",
            "content": {"message": "Unknown author"},
            "timestamp": 1640995200000
        },
        None
    ),
]

# Test data for add_message method
ADD_MESSAGE_TEST_DATA = [
    (
        "valid_user_message",
        UserMessage(content="Hi my name is Ashok", source="user"),
        False,
        None
    ),
    (
        "valid_assistant_message",
        AssistantMessage(content="Hello, Ashok! How can I assist you today?",
                         source="FlotorchAssistant"),
        False,
        None
    ),
    (
        "message_with_tool_calls",
        AssistantMessage(
            content=[FunctionCall(
                id="call_123",
                name="calculate",
                arguments='{"expression": "21+213"}',
            )],
            source="FlotorchAssistant"
        ),
        False,
        None
    ),
    (
        "message_without_author_conversion",
        UserMessage(content="valid message", source="user"),
        False,
        None
    ),
    (
        "api_failure_scenario",
        UserMessage(content="test message", source="user"),
        True,
        Exception
    ),
]

# Test data for get_messages method
GET_MESSAGES_TEST_DATA = [
    (
        "empty_cache",
        [],
        50,
        0
    ),
    (
        "cache_with_few_messages",
        [
            UserMessage(content="Message 1", source="user"),
            AssistantMessage(content="Response 1", source="assistant")
        ],
        50,
        2
    ),
    (
        "cache_exceeding_limit",
        [
            UserMessage(content=f"Message {i}", source="user")
            for i in range(60)
        ],
        50,
        50
    ),
    (
        "cache_exactly_at_limit",
        [
            UserMessage(content=f"Message {i}", source="user")
            for i in range(50)
        ],
        50,
        50
    ),
]

# Test data for initialization scenarios
INITIALIZATION_TEST_DATA = [
    (
        "new_session_creation",
        None,
        False,
        None
    ),
    (
        "existing_session_loading",
        "existing-session-123",
        False,
        None
    ),
    (
        "session_creation_failure",
        None,
        True,
        RuntimeError
    ),
    (
        "session_loading_failure",
        "invalid-session-123",
        True,
        RuntimeError
    ),
]

# Test data for state management
STATE_MANAGEMENT_TEST_DATA = [
    (
        "save_state_with_uid",
        {"uid": "test-session-123", "base_url": "https://test.com"},
        {
            "uid": "test-session-123",
            "base_url": "https://test.com",
            "provider": "flotorch.autogen.sessions.FlotorchAutogenSession"}
    ),
    (
        "save_state_without_uid",
        {"uid": None, "base_url": "https://test.com"},
        {
            "uid": None,
            "base_url": "https://test.com", 
            "provider": "flotorch.autogen.sessions.FlotorchAutogenSession"}
    ),
    (
        "load_state_valid",
        {"uid": "test-session-123", "base_url": "https://test.com"},
        False,
        None
    ),
    (
        "load_state_invalid",
        {"invalid": "data"},
        True,
        ValueError
    ),
]
