"""Test data for FlotorchMemoryStorage functions.

This module contains parametrized test data for save, search, and reset
functions of the FlotorchMemoryStorage class.
"""

SAVE_TEST_DATA = [
    (
        "value_with_final_answer",
        "Thought: Processing\nFinal Answer: Analysis complete",
        {
            "messages": [
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": "analyze this text"},
                {"role": "assistant", "content": "Processing..."}
            ]
        },
        False,
        None
    ),
    (
        "plain_response",
        "Plain assistant response",
        {
            "messages": [
                {"role": "user", "content": "What is 2+2?"},
                {"role": "assistant", "content": "The answer is 4"}
            ]
        },
        False,
        None
    ),
    (
        "multiple_assistant_responses",
        "Thought: Using tool\nAction: analyze\nFinal Answer: Complete",
        {
            "messages": [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "User query"},
                {"role": "assistant", "content": "First response"},
                {"role": "assistant", "content": "Second response"}
            ]
        },
        False,
        None
    ),
    (
        "multiple_user_messages",
        "Response",
        {
            "messages": [
                {"role": "user", "content": "First query"},
                {"role": "assistant", "content": "First response"},
                {"role": "user", "content": "Second query"}
            ]
        },
        False,
        None
    ),
    (
        "custom_user_app_id",
        "Final Answer: Custom IDs",
        {
            "crewai_user_id": "custom_user",
            "crewai_app_id": "custom_app",
            "messages": [{"role": "user", "content": "Query"}]
        },
        False,
        None
    ),
    (
        "empty_value",
        "",
        {"messages": [{"role": "user", "content": "Test"}]},
        False,
        None
    ),
    (
        "api_failure",
        "Test value",
        {"messages": [{"role": "user", "content": "Test"}]},
        True,
        RuntimeError
    ),
]


SEARCH_TEST_DATA = [
    (
        "no_results",
        "test query",
        5,
        {"object": "agent.memory.list", "data": []},
        0,
        False,
        None
    ),
    (
        "single_result_with_memory_field",
        "test query",
        5,
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "mem-123",
                    "memory": "John is a software engineer",
                    "metadata": {
                        "tags": [],
                        "source": "crewai",
                        "importance": 0.5
                    }
                }
            ]
        },
        1,
        False,
        None
    ),
    (
        "result_with_content_field",
        "test query",
        10,
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "mem-456",
                    "content": "User name is Alice",
                    "metadata": {"source": "crewai"}
                }
            ]
        },
        1,
        False,
        None
    ),
    (
        "multiple_results",
        "test query",
        5,
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "mem-1",
                    "memory": "First memory",
                    "metadata": {"quality": 0.8}
                },
                {
                    "id": "mem-2",
                    "content": "Second memory",
                    "metadata": {"suggestions": ["test"]}
                }
            ]
        },
        2,
        False,
        None
    ),
    (
        "result_without_content",
        "test query",
        5,
        {
            "object": "agent.memory.list",
            "data": [{"id": "mem-999", "metadata": {}}]
        },
        0,
        False,
        None
    ),
    (
        "api_failure",
        "test query",
        5,
        None,
        0,
        True,
        RuntimeError
    ),
]


RESET_TEST_DATA = [
    (
        "multiple_memories_to_delete",
        {
            "data": [
                {"id": "mem-1", "memory": "Memory 1"},
                {"id": "mem-2", "memory": "Memory 2"},
                {"id": "mem-3", "memory": "Memory 3"}
            ]
        },
        3,
        False,
        None
    ),
    (
        "single_memory_to_delete",
        {
            "data": [{"id": "mem-100", "memory": "Only memory"}]
        },
        1,
        False,
        None
    ),
    (
        "no_memories",
        {"data": []},
        0,
        False,
        None
    ),
    (
        "memories_without_id",
        {
            "data": [
                {"id": "mem-1", "memory": "Has ID"},
                {"memory": "No ID"},
                {"id": "mem-2", "memory": "Has ID"}
            ]
        },
        2,
        False,
        None
    ),
    (
        "api_failure",
        None,
        0,
        True,
        RuntimeError
    ),
]
