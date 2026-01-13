"""Test data for LangChain agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchLangChainAgent class.
"""

# Base minimal configuration for testing
MINIMAL_CONFIG = {
    "uid": "test-uid-langchain",
    "name": "test-langchain-agent",
    "version": "1",
    "goal": "Test LangChain agent goal",
    "systemPrompt": "Test LangChain system prompt",
    "syncEnabled": False,
    "syncInterval": 1000,
    "outputSchema": None,
    "tools": [],
    "llm": {"callableName": "gpt-4"}
}

# Configuration with output schema for structured output testing
CONFIG_WITH_SCHEMA = {
    **MINIMAL_CONFIG,
    "outputSchema": {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Result text"},
            "confidence": {"type": "number", "description": "Confidence score"},
            "is_valid": {"type": "boolean", "description": "Validation flag"}
        }
    }
}

# Configuration with sync enabled for testing dynamic updates
CONFIG_WITH_SYNC = {
    **MINIMAL_CONFIG,
    "syncEnabled": True,
    "syncInterval": 10  # 10 seconds for testing
}

# Modified configuration for testing config change detection
CONFIG_MODIFIED = {
    **CONFIG_WITH_SYNC,
    "goal": "Modified LangChain agent goal",
    "systemPrompt": "Modified system prompt",
    "version": "2"
}

# Configuration with MCP tools
CONFIG_WITH_MCP_TOOLS = {
    **MINIMAL_CONFIG,
    "tools": [
        {
            "type": "MCP",
            "name": "test-mcp-tool",
            "config": {
                "transport": "HTTP_STREAMABLE",
                "headers": {"X-Custom-Header": "value"}
            }
        }
    ]
}

# Test data for agent name sanitization
SANITIZE_NAME_DATA = [
    ("valid_name", "my_langchain_agent", "my_langchain_agent"),
    ("with_hyphens", "my-langchain-agent", "my_langchain_agent"),
    ("with_spaces", "my langchain agent", "my_langchain_agent"),
    ("with_special_chars", "agent@#$%", "agent"),
    ("starts_with_number", "123agent", "agent_123agent"),
    ("consecutive_underscores", "my___agent", "my_agent"),
    ("leading_trailing_underscores", "_agent_", "agent"),
    ("empty", "", "agent"),
    ("only_special_chars", "@#$%", "agent"),
]

# Schema test data for different field types
SCHEMA_TEST_DATA = [
    (
        "simple_schema",
        {
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "age": {"type": "integer", "description": "User age"}
            }
        },
        {"name": "test", "age": 30}
    ),
    (
        "all_types_schema",
        {
            "properties": {
                "text": {"type": "string"},
                "count": {"type": "integer"},
                "score": {"type": "number"},
                "active": {"type": "boolean"}
            }
        },
        {"text": "test", "count": 5, "score": 9.5, "active": True}
    ),
    (
        "empty_properties",
        {"properties": {}},
        {}
    ),
]


class MockLangChainTool:
    """Mock LangChain tool for testing.
    
    Simulates a LangChain BaseTool with required attributes.
    """
    
    def __init__(self, name: str = "test_tool", description: str = "Test tool"):
        """Initialize mock tool.
        
        Args:
            name: Tool name identifier
            description: Tool description
        """
        self.name = name
        self.description = description
    
    def __repr__(self):
        """Return string representation."""
        return f"MockLangChainTool(name='{self.name}')"
    
    def __eq__(self, other):
        """Check equality based on name."""
        if isinstance(other, MockLangChainTool):
            return self.name == other.name
        return False

