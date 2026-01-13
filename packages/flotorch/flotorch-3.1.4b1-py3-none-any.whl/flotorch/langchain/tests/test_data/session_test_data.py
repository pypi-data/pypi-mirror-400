"""Test data for LangChain session parametrized tests."""

LOAD_MEMORY_VARIABLES_TEST_DATA = [
    ("empty", {"input": "Hello"}, [], ""),
    (
        "single_turn",
        {"input": "Query"},
        [
            {"author": "assistant", "content": {"parts": [{"text": "Hello!"}]}},
            {"author": "user", "content": {"parts": [{"text": "Hi Alice"}]}},
        ],
        "user: Hi Alice\nassistant: Hello!"
    ),
    (
        "direct_text",
        {"input": "Query"},
        [
            {"author": "assistant", "text": "Response"},
            {"author": "user", "text": "Direct"},
        ],
        "user: Direct\nassistant: Response"
    ),
    (
        "no_author",
        {"input": "Test"},
        [{"content": {"parts": [{"text": "Message"}]}}],
        "Message"
    ),
]


SAVE_CONTEXT_TEST_DATA = [
    ("valid", {"input": "Hi Bob"}, {"output": "Hello!"}),
    ("response_key", {"input": "Query"}, {"response": "Response"}),
    ("empty_input", {"input": ""}, {"output": "Response"}),
    ("numeric", {"input": 12345}, {"output": "Number"}),
]


CLEAR_TEST_DATA = [
    ("with_session", "existing-456", True),
    ("without_session", None, False),
]


EXTRACT_TEXT_LINES_TEST_DATA = [
    (
        "with_author",
        [{"author": "user", "content": {"parts": [{"text": "Hi"}]}}],
        ["user: Hi"]
    ),
    (
        "direct_text",
        [{"author": "assistant", "text": "Response"}],
        ["assistant: Response"]
    ),
    (
        "no_author",
        [{"content": {"parts": [{"text": "Message"}]}}],
        ["Message"]
    ),
    ("empty", [], []),
    (
        "skip_invalid",
        [
            {"author": "user", "content": {"parts": [{"text": "Valid"}]}},
            {"author": "user", "content": {"parts": []}},
        ],
        ["user: Valid"]
    ),
]

