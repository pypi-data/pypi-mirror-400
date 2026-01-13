"""Test data for LangGraph agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchLangGraphAgent class.
"""

# Base minimal configuration for testing
MINIMAL_CONFIG = {
    "uid": "test-uid",
    "name": "test-agent",
    "version": "1",
    "goal": "Test goal",
    "systemPrompt": "You are a helpful assistant",
    "syncEnabled": False,
    "syncInterval": 1000,
    "outputSchema": None,
    "tools": [],
    "llm": {"callableName": "openai/gpt-4o-mini"}
}

# Configuration with output schema for structured output testing
CONFIG_WITH_SCHEMA = {
    **MINIMAL_CONFIG,
    "outputSchema": {
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "confidence": {"type": "number"}
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

# Test data for agent name sanitization
SANITIZE_NAME_DATA = [
    ("valid_name", "my_agent", "my_agent"),
    ("with_hyphens", "my-agent", "my_agent"),
    ("with_spaces", "my agent", "my_agent"),
    ("empty", "", "agent"),
]


class MockTool:
    """Mock tool for testing.
    
    Simulates a LangChain BaseTool with name and description attributes.
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
        return f"MockTool(name='{self.name}')"

