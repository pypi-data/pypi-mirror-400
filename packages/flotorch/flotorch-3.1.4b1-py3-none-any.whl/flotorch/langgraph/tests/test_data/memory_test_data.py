"""Test data for FlotorchStore functions.

This module contains parametrized test data for get, put, search operations.
"""

# Test data for GET operations
GET_TEST_DATA = [
    (
        "get_by_uuid_success",
        "123e4567-e89b-12d3-a456-426614174000",
        ("users", "alice"),
        {
            "data": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content": '{"text": "User preference stored"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00",
                "metadata": {}
            }
        },
        True,  # should_succeed
        False,  # should_fail
        None
    ),
    (
        "get_by_key_success",
        "user_preference",
        ("users", "alice"),
        {
            "data": [
                {
                    "id": "mem-123",
                    "content": "Prefers dark mode",
                    "createdAt": "2024-01-01T00:00:00",
                    "updatedAt": "2024-01-01T00:00:00",
                    "metadata": {
                        "tags": ["user_preference"],
                        "langgraph_key": "user_preference",
                        "langgraph_namespace": ["users", "alice"]
                    }
                }
            ]
        },
        True,
        False,
        None
    ),
    (
        "get_not_found",
        "nonexistent_key",
        ("users", "bob"),
        {"data": []},
        False,
        False,
        None
    ),
    (
        "get_api_failure",
        "some_key",
        ("users", "alice"),
        None,
        False,
        True,
        Exception
    ),
]

# Test data for PUT operations
PUT_TEST_DATA = [
    (
        "put_new_value",
        "preference_key",
        ("users", "alice"),
        {"theme": "dark"},
        None,
        False,  # is_delete
        False,  # should_fail
        None
    ),
    (
        "put_complex_nested_json",
        "config_key",
        ("apps", "myapp"),
        {
            "settings": {
                "ui": {"theme": "dark", "language": "en"},
                "features": ["feature1", "feature2"],
                "limits": {"max": 100, "min": 0}
            }
        },
        None,
        False,
        False,
        None
    ),
    (
        "delete_by_uuid",
        "123e4567-e89b-12d3-a456-426614174000",
        ("users", "alice"),
        None,
        None,
        True,  # is_delete
        False,  # should_fail
        None
    ),
    (
        "delete_by_key",
        "old_preference",
        ("users", "alice"),
        None,
        {"data": [{"id": "mem-to-delete"}]},
        True,  # is_delete
        False,  # should_fail
        None
    ),
]

# Test data for SEARCH operations
SEARCH_TEST_DATA = [
    (
        "search_with_results",
        "user preferences",
        ("users",),
        10,
        {
            "data": [
                {
                    "id": "mem-1",
                    "content": '{"preference": "dark mode"}',
                    "createdAt": "2024-01-01T00:00:00",
                    "updatedAt": "2024-01-01T00:00:00",
                    "importance": 0.8,
                    "metadata": {"langgraph_namespace": ["users"], "langgraph_key": "pref1"}
                },
                {
                    "id": "mem-2",
                    "content": '{"preference": "notifications on"}',
                    "createdAt": "2024-01-02T00:00:00",
                    "updatedAt": "2024-01-02T00:00:00",
                    "importance": 0.6,
                    "metadata": {"langgraph_namespace": ["users"], "langgraph_key": "pref2"}
                }
            ]
        },
        2,
        False,
        None
    ),
    (
        "search_no_results",
        "nonexistent query",
        ("users",),
        5,
        {"data": []},
        0,
        False,
        None
    ),
    (
        "search_empty_query",
        "",
        ("users",),
        5,
        {"data": []},
        0,
        False,
        None
    ),
    (
        "search_api_failure",
        "test query",
        ("users",),
        10,
        None,
        0,
        True,
        Exception
    ),
]

# Test data for UUID validation
UUID_VALIDATION_TEST_DATA = [
    ("valid_uuid_lowercase", "123e4567-e89b-12d3-a456-426614174000", True),
    ("valid_uuid_uppercase", "123E4567-E89B-12D3-A456-426614174000", True),
    ("valid_uuid_mixed", "123e4567-E89B-12d3-A456-426614174000", True),
    ("invalid_not_uuid", "my_custom_key", False),
    ("invalid_empty_string", "", False),
    ("invalid_malformed_uuid", "123e4567-e89b-12d3-426614174000", False),
]

# Test data for data conversion
DATA_CONVERSION_TEST_DATA = [
    (
        "valid_json_content",
        {
            "id": "mem-1",
            "content": '{"key": "value", "number": 42}',
            "createdAt": "2024-01-01T10:00:00",
            "updatedAt": "2024-01-01T12:00:00"
        },
        {"key": "value", "number": 42},
    ),
    (
        "plain_text_content",
        {
            "id": "mem-2",
            "content": "Plain text content",
            "createdAt": "2024-01-01T10:00:00",
            "updatedAt": "2024-01-01T12:00:00"
        },
        {"text": "Plain text content"},
    ),
    (
        "empty_content",
        {
            "id": "mem-3",
            "content": "",
            "createdAt": "2024-01-01T10:00:00",
            "updatedAt": "2024-01-01T12:00:00"
        },
        {},
    ),
    (
        "unicode_content",
        {
            "id": "mem-4",
            "content": '{"message": "Hello World"}',
            "createdAt": "2024-01-01T10:00:00",
            "updatedAt": "2024-01-01T12:00:00"
        },
        {"message": "Hello World"},
    ),
]
