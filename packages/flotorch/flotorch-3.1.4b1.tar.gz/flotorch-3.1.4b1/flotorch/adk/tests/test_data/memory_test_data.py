"""Test data for FlotorchMemoryService functions (ADK).

This module contains parametrized test data for add_session_to_memory and
search_memory operations.
"""


# Test data for add_session_to_memory operations
ADD_SESSION_TEST_DATA = [
    (
        "add_session_success",
        "session_001",
        "test_user",
        "test_app",
        [
            {"role": "user", "content": "My name is Vikram"},
            {"role": "model", "content": "Nice to meet you, Vikram!"}
        ],
        False,  # should_fail
        None    # expected_exception
    ),
    (
        "add_session_with_multiple_messages",
        "session_002",
        "test_user",
        "test_app",
        [
            {"role": "user", "content": "I love Python"},
            {"role": "model", "content": "Python is great!"},
            {"role": "user", "content": "I use it for AI projects"}
        ],
        False,
        None
    ),
    (
        "add_session_api_failure",
        "session_003",
        "test_user",
        "test_app",
        [{"role": "user", "content": "Test"}],
        True,  # should_fail
        Exception
    ),
]

# Test data for search_memory operations
SEARCH_MEMORY_TEST_DATA = [
    (
        "search_with_results",
        "test_app",
        "test_user",
        "What is my name",
        {
            "data": [
                {
                    "id": "mem-1",
                    "memory": "User's name is Vikram",
                    "metadata": {"source": "adk_session"},
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "mem-2",
                    "content": "Vikram works as a software engineer",
                    "metadata": {"category": "conversation"},
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        },
        2,  # expected_count
        False,  # should_fail
        None
    ),
    (
        "search_no_results",
        "test_app",
        "test_user",
        "quantum physics",
        {"data": []},
        0,
        False,
        None
    ),
    (
        "search_api_failure",
        "test_app",
        "test_user",
        "test query",
        None,
        0,
        True,
        Exception
    ),
]

# Test data for role extraction
ROLE_EXTRACTION_TEST_DATA = [
    ("model_role", "model", "assistant"),
    ("user_role", "user", "user"),
    ("assistant_role", "assistant", "assistant"),
    ("agent_role", "agent", "assistant"),
    ("bot_role", "bot", "assistant"),
    ("human_role", "human", "user"),
    ("unknown_role", "unknown", "user"),
]

# Test data for content extraction
CONTENT_EXTRACTION_TEST_DATA = [
    (
        "content_with_parts",
        {"content": {"parts": [{"text": "Hello world"}]}},
        "Hello world"
    ),
    (
        "content_with_multiple_parts",
        {"content": {"parts": [{"text": "Hello"}, {"text": "world"}]}},
        "Hello world"
    ),
    (
        "direct_text",
        {"text": "Direct text"},
        "Direct text"
    ),
    (
        "string_content",
        {"content": "String content"},
        "String content"
    ),
    (
        "no_content",
        {},
        "Content not available"
    ),
]

