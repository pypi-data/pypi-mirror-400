"""Test data for ADK agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchADKAgent class.
"""


# Base minimal configuration for testing
MINIMAL_CONFIG = {
    "uid": "test-uid-123",
    "name": "test-agent",
    "version": "1",
    "goal": "Test goal",
    "systemPrompt": "You are a helpful assistant",
    "syncEnabled": False,
    "syncInterval": 60,
    "inputSchema": None,
    "outputSchema": None,
    "tools": [],
    "llm": {"callableName": "flotorch/openai:latest"}
}

# Configuration with output schema for structured output testing
CONFIG_WITH_OUTPUT_SCHEMA = {
    **MINIMAL_CONFIG,
    "outputSchema": {
        "type": "object",
        "properties": {
            "Answer": {"type": "string", "description": "The response"}
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
    "goal": "Modified goal",
    "systemPrompt": "You are an updated assistant",
    "version": "2"
}

# Configuration with MCP tools (ADK-specific feature)
CONFIG_WITH_MCP_TOOLS = {
    **MINIMAL_CONFIG,
    "tools": [
        {
            "name": "read-wiki-structure",
            "description": "Get wiki structure",
            "type": "MCP",
            "config": {
                "transport": "HTTP_STREAMABLE",
                "url": "https://mcp.deepwiki.com/mcp",
                "headers": {},
                "timeout": 10000,
                "sse_read_timeout": 10000
            }
        }
    ]
}

# Test data for agent name sanitization
SANITIZE_NAME_DATA = [
    ("valid_name", "my_agent", "my_agent"),
    ("with_hyphens", "my-agent", "my_agent"),
    ("with_spaces", "my agent", "my_agent"),
    ("with_special_chars", "my@agent#123", "my_agent_123"),
    ("empty", "", "agent"),
    ("starts_with_number", "123agent", "agent_123agent"),
]


class MockTool:
    """Mock tool for testing."""
    
    def __init__(self, name: str = "test_tool"):
        self.name = name
    
    def __repr__(self):
        return f"MockTool(name='{self.name}')"

