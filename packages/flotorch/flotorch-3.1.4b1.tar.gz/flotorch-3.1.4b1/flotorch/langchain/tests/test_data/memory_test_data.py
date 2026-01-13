"""Test data for LangChain memory parametrized tests."""

LOAD_MEMORY_TEST_DATA = [
    ("no_results", {"input": "Query"}, {"data": []}, ""),
    (
        "single_result",
        {"input": "What is my name?"},
        {"data": [{"content": "User name is Alice"}]},
        "User name is Alice"
    ),
    (
        "multiple_results",
        {"input": "Tell me about myself"},
        {
            "data": [
                {"content": "User name is Bob"},
                {"content": "Lives in New York"},
                {"content": "Works as engineer"}
            ]
        },
        "User name is Bob\nLives in New York\nWorks as engineer"
    ),
    (
        "result_with_message_field",
        {"input": "Query"},
        {"data": [{"message": "Message content"}]},
        "Message content"
    ),
    (
        "result_with_text_field",
        {"input": "Query"},
        {"data": [{"text": "Text content"}]},
        "Text content"
    ),
    (
        "mixed_field_types",
        {"input": "Query"},
        {
            "data": [
                {"content": "From content"},
                {"message": "From message"},
                {"text": "From text"}
            ]
        },
        "From content\nFrom message\nFrom text"
    ),
]

SAVE_CONTEXT_TEST_DATA = [
    ("valid_input_output", {"input": "Hi"}, {"output": "Hello!"}),
    ("response_key", {"input": "Query"}, {"response": "Response"}),
    ("empty_input", {"input": ""}, {"output": "Response"}),
    ("empty_output", {"input": "Query"}, {"output": ""}),
]

CLEAR_TEST_DATA = [
    (
        "multiple_items",
        {
            "data": [
                {"id": "mem-1", "content": "Memory 1"},
                {"id": "mem-2", "content": "Memory 2"},
                {"id": "mem-3", "content": "Memory 3"}
            ]
        },
        3
    ),
    (
        "single_item",
        {"data": [{"id": "mem-100", "content": "Only memory"}]},
        1
    ),
    ("no_items", {"data": []}, 0),
    (
        "items_without_id",
        {
            "data": [
                {"id": "mem-1", "content": "Has ID"},
                {"content": "No ID"},
                {"id": "mem-2", "content": "Has ID"}
            ]
        },
        2
    ),
]

BUILD_HISTORY_TEST_DATA = [
    (
        "content_field",
        [{"content": "Line 1"}, {"content": "Line 2"}],
        "Line 1\nLine 2"
    ),
    (
        "message_field",
        [{"message": "Message text"}],
        "Message text"
    ),
    (
        "text_field",
        [{"text": "Text content"}],
        "Text content"
    ),
    (
        "mixed_fields",
        [
            {"content": "From content"},
            {"message": "From message"},
            {"text": "From text"}
        ],
        "From content\nFrom message\nFrom text"
    ),
    (
        "whitespace_trim",
        [{"content": "  Trimmed  "}],
        "Trimmed"
    ),
    ("empty_items", [], ""),
    (
        "skip_empty",
        [
            {"content": "Valid"},
            {"content": ""},
            {"content": "  "},
            {"content": "Also valid"}
        ],
        "Valid\nAlso valid"
    ),
    (
        "skip_no_content",
        [
            {"content": "Valid"},
            {"other": "field"},
            {"content": "Also valid"}
        ],
        "Valid\nAlso valid"
    ),
]

