"""Test data for FlotorchAutogenMemory functions.

This module contains parametrized test data for query, add, and update_context
functions of the FlotorchAutogenMemory class.
"""

from autogen_core.memory import MemoryContent, MemoryMimeType

# ============================================================================
# QUERY TEST DATA
# ============================================================================

QUERY_TEST_DATA = [
    (
        "empty_results",
        "test query",
        {"data": []},
        0,  # No memories returned
        False,
        None
    ),
    (
        "single_memory_with_content",
        "what is the weather",
        {
            "object": "agent.memory.list",
            "data": [
                {
                    "id": "mem-123",
                    "content": "The weather is sunny",
                    "metadata": {"source": "adk_session"}
                }
            ]
        },
        1,
        False,
        None
    ),
    (
        "multiple_memories",
        "user preferences",
        {
            "object": "agent.memory.list",
            "data": [
                {"id": "mem-1", "content": "User likes Python"},
                {"id": "mem-2", "content": "User prefers dark mode"},
                {"id": "mem-3", "content": "User timezone is PST"}
            ]
        },
        3,
        False,
        None
    ),
    (
        "memory_without_content_field",
        "test",
        {
            "data": [
                {"id": "mem-1", "content": "Valid memory"},
                {"id": "mem-2", "other_field": "Invalid"},
                {"id": "mem-3", "content": ""}  # Empty content
            ]
        },
        1,  # Only one valid
        False,
        None
    ),
    (
        "api_failure",
        "test query",
        None,  # Will trigger exception
        0,
        True,
        Exception
    ),
]

# ============================================================================
# ADD TEST DATA
# ============================================================================

ADD_TEST_DATA = [
    (
        "simple_text_content",
        MemoryContent(content="User said hello", mime_type=MemoryMimeType.TEXT),
        False,
        None
    ),
    (
        "long_content",
        MemoryContent(
            content="This is a very long memory content that contains multiple sentences and a lot of information " * 10,
            mime_type=MemoryMimeType.TEXT
        ),
        False,
        None
    ),
    (
        "empty_content",
        MemoryContent(content="", mime_type=MemoryMimeType.TEXT),
        False,
        None  # Should not fail, just stores empty
    ),
    (
        "special_characters_content",
        MemoryContent(
            content="Content with special chars: @#$%^&*(){}[]<>?/\\|~`",
            mime_type=MemoryMimeType.TEXT
        ),
        False,
        None
    ),
    (
        "api_failure",
        MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT),
        True,
        Exception
    ),
]

# ============================================================================
# UPDATE_CONTEXT TEST DATA
# ============================================================================

UPDATE_CONTEXT_TEST_DATA = [
    (
        "empty_messages",
        [],
        {"data": []},
        False,  # No context update
        False,
        None
    ),
    (
        "single_message_with_memories",
        ["What is Python?"],
        {
            "data": [
                {"id": "mem-1", "content": "Python is a programming language"}
            ]
        },
        True,  # Should add to context
        False,
        None
    ),
    (
        "multiple_messages_uses_last",
        ["First message", "Second message", "What is AI?"],
        {
            "data": [
                {"id": "mem-1", "content": "AI is artificial intelligence"}
            ]
        },
        True,
        False,
        None
    ),
    (
        "no_memories_found",
        ["Test query"],
        {"data": []},
        False,  # "No memories found" shouldn't be added to context
        False,
        None
    ),
    (
        "multiple_memories_formatted",
        ["Tell me about the user"],
        {
            "data": [
                {"id": "mem-1", "content": "User name is John"},
                {"id": "mem-2", "content": "User likes coding"},
                {"id": "mem-3", "content": "User is from NYC"}
            ]
        },
        True,
        False,
        None
    ),
]

# ============================================================================
# DEDUPLICATION TEST DATA
# ============================================================================

DEDUPLICATION_TEST_DATA = [
    (
        "same_content_same_hash",
        [
            MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)
        ],
        [
            MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)
        ],
        True  # Should be same hash
    ),
    (
        "different_content_different_hash",
        [
            MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT)
        ],
        [
            MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)
        ],
        False  # Should be different hash
    ),
    (
        "different_order_same_hash",
        [
            MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)
        ],
        [
            MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT)
        ],
        True  # Sorted before hashing, so same hash
    ),
    (
        "empty_results",
        [],
        [],
        True  # Both empty should have same hash
    ),
]