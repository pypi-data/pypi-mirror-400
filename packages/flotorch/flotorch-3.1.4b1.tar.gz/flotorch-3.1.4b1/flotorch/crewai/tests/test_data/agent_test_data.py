"""Test data for agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchCrewAIAgent class.
"""

# Base minimal configuration for testing
MINIMAL_CONFIG = {
    "uid": "test-uid",
    "name": "test-agent",
    "version": "1",
    "goal": "Test goal",
    "systemPrompt": "Test prompt",
    "syncEnabled": False,
    "syncInterval": 1000,
    "outputSchema": None,
    "tools": [],
    "llm": {"callableName": "test-model"}
}

# Configuration with output schema for structured output testing
CONFIG_WITH_SCHEMA = {
    **MINIMAL_CONFIG,
    "outputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "integer"}
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
    
    Simulates a CrewAI tool with a name attribute.
    """
    
    def __init__(self, name: str = "test_tool"):
        """Initialize mock tool.
        
        Args:
            name: Tool name identifier
        """
        self.name = name
    
    def __repr__(self):
        """Return string representation."""
        return f"MockTool(name='{self.name}')"
