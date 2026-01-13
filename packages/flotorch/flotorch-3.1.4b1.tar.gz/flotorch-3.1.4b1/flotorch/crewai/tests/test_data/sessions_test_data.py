"""Test data for sessions function parametrized tests."""

SAVE_FUNCTION_TEST_DATA = [
    (
        "valid_value_with_metadata",
        "Text Analysis:\n- Words: 6\n- Characters: 24",
        {
            "observation": "You are a helpful agent.",
            "user_query": "analyze text"
        },
        False,
        None
    ),
    (
        "empty_value_with_metadata",
        "",
        {"observation": "test observation", "user_query": "test query"},
        False,
        None
    ),
    (
        "value_with_empty_metadata",
        "Test message",
        {},
        False,
        None
    ),
    (
        "value_with_none_metadata",
        "Test message",
        None,
        False,
        None
    ),
    (
        "long_value_with_complex_metadata",
        "Thought: Processing\nFinal Answer: Analysis complete",
        {
            "observation": "Agent context",
            "user_query": "analyze this text",
            "context": {"step": 1, "task": "analysis"}
        },
        False,
        None
    ),
    (
        "numeric_value_converted_to_string",
        12345,
        {"type": "numeric"},
        False,
        None
    ),
    (
        "api_failure_scenario",
        "test value",
        {"test": "metadata"},
        True,
        RuntimeError
    ),
    (
        "metadata_with_special_chars",
        "special test",
        {"key@#$": "value!@#", "nested": {"data": "test"}},
        False,
        None
    ),
]


SEARCH_FUNCTION_TEST_DATA = [
    (
        "valid_query_with_events",
        "test query",
        10,
        [
            {
                "content": {"parts": [{"text": "Result 1"}]},
                "groundingMetadata": {"key": "value1"}
            },
            {
                "content": {"parts": [{"text": "Result 2"}]},
                "groundingMetadata": {"key": "value2"}
            }
        ],
        2,
        False,
        None
    ),
    (
        "empty_query_returns_empty",
        "",
        10,
        [{"content": {"parts": [{"text": "Result"}]}}],
        0,
        False,
        None
    ),
    (
        "none_query_returns_empty",
        None,
        10,
        [{"content": {"parts": [{"text": "Result"}]}}],
        0,
        False,
        None
    ),
    (
        "no_events_returns_empty",
        "test query",
        10,
        [],
        0,
        False,
        None
    ),
    (
        "events_without_text_skipped",
        "test query",
        10,
        [
            {"content": {"parts": []}},
            {"content": {"parts": [{"data": "no text"}]}},
            {"content": {}}
        ],
        0,
        False,
        None
    ),
    (
        "mixed_events_filters_valid",
        "test query",
        10,
        [
            {
                "content": {"parts": [{"text": "Valid 1"}]},
                "groundingMetadata": {"a": "b"}
            },
            {"content": {"parts": []}},
            {"text": "Valid 2"},
            {"content": {"parts": [{"data": "invalid"}]}}
        ],
        2,
        False,
        None
    ),
    (
        "event_with_final_answer",
        "test query",
        10,
        [
            {
                "content": {
                    "parts": [{
                        "text": "Thought: thinking\nFinal Answer: 42"
                    }]
                }
            }
        ],
        1,
        False,
        None
    ),
    (
        "event_with_direct_text_field",
        "test query",
        10,
        [{"text": "Direct text", "groundingMetadata": {"direct": True}}],
        1,
        False,
        None
    ),
    (
        "api_failure_raises_error",
        "test query",
        10,
        None,
        0,
        True,
        RuntimeError
    ),
    (
        "events_without_metadata",
        "test query",
        10,
        [{"content": {"parts": [{"text": "No metadata"}]}}],
        1,
        False,
        None
    )
]
