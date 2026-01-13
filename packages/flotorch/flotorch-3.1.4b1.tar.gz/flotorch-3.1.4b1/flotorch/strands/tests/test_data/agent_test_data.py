"""Test data for Strands agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchStrandsAgent class.
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

# Configuration with MCP tools (Strands-specific feature)
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
                "timeout": 10000
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
]


class MockTool:
    """Mock tool for testing."""
    
    def __init__(self, name: str = "test_tool"):
        self.name = name
    
    def __repr__(self):
        return f"MockTool(name='{self.name}')"


class MockMCPTool:
    """Mock MCP tool for testing."""
    
    def __init__(self, name: str = "test_mcp_tool"):
        self.name = name


class MockAgent:
    """Mock Strands Agent for testing."""
    
    def __init__(self):
        self.tool_registry = MockToolRegistry()
        self._output_schema = None
    
    def __call__(self, prompt, **kwargs):
        return {"response": f"Mock response to: {prompt}"}
    
    def structured_output(self, schema, prompt, **kwargs):
        class MockResponse:
            def __init__(self, data):
                self.data = data
            def model_dump(self):
                return self.data
        return MockResponse({"Answer": f"Structured response to: {prompt}"})


class MockToolRegistry:
    """Mock tool registry for testing."""
    
    def __init__(self):
        self.registry = {}
    
    def register_tool(self, tool):
        tool_name = getattr(tool, 'name', str(tool))
        if tool_name in self.registry:
            raise ValueError(f"Tool name '{tool_name}' already exists. Cannot register tools with exact same name.")
        self.registry[tool_name] = tool


class MockMCPClient:
    """Mock MCP Client for testing."""
    
    def __init__(self, tools=None):
        self.tools = tools or [MockMCPTool("mcp_tool_1"), MockMCPTool("mcp_tool_2")]
        self.entered = False
        self.exited = False
    
    def __enter__(self):
        self.entered = True
        return self
    
    def __exit__(self, *args):
        self.exited = True
        return False
    
    def list_tools_sync(self):
        return self.tools

