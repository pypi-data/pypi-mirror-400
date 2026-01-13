"""Test data for Strands Memory tests based on actual runtime execution."""

# Memory ADD operation test data
MEMORY_ADD_TEST_DATA = [
    (
        "add_simple_text",
        {"action": "add", "content": "User's name is Madhu."},
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "2582aa4a-d728-4cb3-b32c-a688c336c24e",
                    "content": "User Name is Madhu"
                }
            ]
        },
        "Memory stored successfully. ID: unknown",
        False,  # should_fail
        None    # expected_exception
    ),
    (
        "add_complex_info",
        {"action": "add", "content": "User scored 1000 in a test in 2010"},
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "81aedc81-40b9-4435-a7fd-e343b8c046cc",
                    "content": "User Scored 1000 in a test in 2010"
                }
            ]
        },
        "Memory stored successfully. ID: unknown",
        False,
        None
    ),
    (
        "add_missing_content",
        {"action": "add"},
        None,
        "Error: content is required for add action",
        True,  # should_fail
        ValueError
    ),
]

# Memory SEARCH operation test data
MEMORY_SEARCH_TEST_DATA = [
    (
        "search_user_name",
        {"action": "search", "query": "User's name"},
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "2582aa4a-d728-4cb3-b32c-a688c336c24e",
                    "content": "User Name is Madhu",
                    "userId": "user-id-15",
                    "appId": "app-id-15",
                    "metadata": {"tags": [], "source": "strands", "importance": 0.5},
                    "createdAt": "2025-09-24T05:35:12.846Z",
                    "updatedAt": "2025-10-13T08:00:06.005Z",
                    "score": 0.8169173466955095
                },
                {
                    "id": "81aedc81-40b9-4435-a7fd-e343b8c046cc",
                    "content": "User Scored 1000 in a test in 2010",
                    "userId": "user-id-15",
                    "appId": "app-id-15",
                    "metadata": {"tags": [], "source": "strands", "importance": 0.5},
                    "createdAt": "2025-09-30T11:30:55.032Z",
                    "updatedAt": "2025-09-30T11:30:55.092Z",
                    "score": 0.4680134290720004
                }
            ]
        },
        "Found 2 relevant memories:\n1. User Name is Madhu\n2. User Scored 1000 in a test in 2010\n",
        False,
        None
    ),
    (
        "search_no_results",
        {"action": "search", "query": "nonexistent information"},
        {
            "object": "agent.memory.list",
            "data": []
        },
        "No relevant memories found.",
        False,
        None
    ),
    (
        "search_missing_query",
        {"action": "search"},
        None,
        "Error: query is required for search action",
        True,
        ValueError
    ),
]

# Memory LIST operation test data
MEMORY_LIST_TEST_DATA = [
    (
        "list_all_memories",
        {"action": "list"},
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "2582aa4a-d728-4cb3-b32c-a688c336c24e",
                    "content": "User Name is Madhu",
                    "userId": "user-id-15",
                    "appId": "app-id-15",
                    "metadata": {"tags": [], "source": "strands", "importance": 0.5},
                    "createdAt": "2025-09-24T05:35:12.846Z",
                    "updatedAt": "2025-10-13T08:00:06.005Z"
                },
                {
                    "id": "81aedc81-40b9-4435-a7fd-e343b8c046cc",
                    "content": "User Scored 1000 in a test in 2010",
                    "userId": "user-id-15",
                    "appId": "app-id-15",
                    "metadata": {"tags": [], "source": "strands", "importance": 0.5},
                    "createdAt": "2025-09-30T11:30:55.032Z",
                    "updatedAt": "2025-09-30T11:30:55.092Z"
                }
            ]
        },
        "Total memories: 2\n1. [2582aa4a-d728-4cb3-b32c-a688c336c24e] User Name is Madhu...\n2. [81aedc81-40b9-4435-a7fd-e343b8c046cc] User Scored 1000 in a test in 2010...\n",
        False,
        None
    ),
    (
        "list_empty_memories",
        {"action": "list"},
        {
            "object": "agent.memory.list",
            "data": []
        },
        "No memories found.",
        False,
        None
    ),
]

# Invalid action test data
INVALID_ACTION_TEST_DATA = [
    (
        "invalid_action",
        {"action": "delete"},
        None,
        "Error: Invalid action: delete",
        True,
        ValueError
    ),
    (
        "missing_action",
        {},
        None,
        "Error: action parameter is required",
        True,
        ValueError
    ),
]

# Tool Result format test data
TOOL_RESULT_FORMAT_TEST_DATA = [
    (
        "success_result_format",
        {
            "toolUseId": "call_test_123",
            "status": "success",
            "content": [{"text": "Memory stored successfully. ID: unknown"}]
        },
        "success",
        "Memory stored successfully. ID: unknown"
    ),
    (
        "error_result_format",
        {
            "toolUseId": "call_test_456",
            "status": "error",
            "content": [{"text": "Error: content is required for add action"}]
        },
        "error",
        "Error: content is required for add action"
    ),
]

