"""Test data for AutoGen agent tests.

This module provides sample configurations and mock objects for testing
the FlotorchAutogenAgent class.
"""


# Base minimal configuration for testing
MINIMAL_CONFIG = {
    "uid": "test-uid",
    "name": "test-agent",
    "version": "1",
    "systemPrompt": "Test system prompt",
    "syncEnabled": False,
    "syncInterval": 1000,
    "inputSchema": None,
    "outputSchema": None,
    "tools": [],
    "llm": {"callableName": "test-model"}
}

# Configuration with output schema for structured output testing
CONFIG_WITH_OUTPUT_SCHEMA = {
    **MINIMAL_CONFIG,
    "outputSchema": {
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "score": {"type": "number"}
        }
    }
}

# Configuration with input schema for structured input testing
CONFIG_WITH_INPUT_SCHEMA = {
    **MINIMAL_CONFIG,
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "context": {"type": "string"}
        }
    }
}

# Configuration with both input and output schemas
CONFIG_WITH_BOTH_SCHEMAS = {
    **CONFIG_WITH_INPUT_SCHEMA,
    **CONFIG_WITH_OUTPUT_SCHEMA
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
    "systemPrompt": "Modified system prompt",
    "version": "2"
}

# Configuration with MCP tools
CONFIG_WITH_MCP_TOOLS = {
    **MINIMAL_CONFIG,
    "tools": [
        {
            "type": "MCP",
            "name": "test-mcp-sse",
            "config": {
                "transport": "HTTP_SSE",
                "headers": {}
            }
        },
        {
            "type": "MCP",
            "name": "test-mcp-stream",
            "config": {
                "transport": "HTTP_STREAMABLE",
                "headers": {}
            }
        }
    ]
}

# Test data for schema conversion
SCHEMA_TO_PYDANTIC_DATA = [
    {
        "id": "single_property_input",
        "name": "InputSchema",
        "schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "User query"}
            }
        },
        "expected_model_name": "QueryInput"
    },
    {
        "id": "single_property_output",
        "name": "OutputSchema",
        "schema": {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "Result"}
            }
        },
        "expected_model_name": "ResultOutput"
    },
    {
        "id": "multiple_properties",
        "name": "TestSchema",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name"},
                "age": {"type": "integer", "description": "Age"},
                "active": {"type": "boolean", "description": "Active status"}
            }
        },
        "expected_model_name": "TestSchema"
    },
    {
        "id": "number_types",
        "name": "NumberSchema",
        "schema": {
            "type": "object",
            "properties": {
                "score": {"type": "number", "description": "Score"},
                "count": {"type": "integer", "description": "Count"}
            }
        },
        "expected_model_name": "NumberSchema"
    }
]

# Test data for agent initialization
AGENT_INIT_DATA = [
    {
        "id": "basic_init",
        "params": {
            "agent_name": "test-agent",
            "base_url": "https://test.com",
            "api_key": "test-key"
        },
        "expected": {
            "agent_name": "test-agent",
            "base_url": "https://test.com",
            "api_key": "test-key"
        }
    },
    {
        "id": "with_memory",
        "params": {
            "agent_name": "test-agent",
            "memory": ["mock_memory"],
            "base_url": "https://test.com",
            "api_key": "test-key"
        },
        "expected": {
            "agent_name": "test-agent",
            "memory": ["mock_memory"]
        }
    },
    {
        "id": "with_custom_tools",
        "params": {
            "agent_name": "test-agent",
            "custom_tools": ["mock_tool1", "mock_tool2"],
            "base_url": "https://test.com",
            "api_key": "test-key"
        },
        "expected": {
            "agent_name": "test-agent",
            "custom_tools": ["mock_tool1", "mock_tool2"]
        }
    },
    {
        "id": "with_model_context",
        "params": {
            "agent_name": "test-agent",
            "model_context": "mock_context",
            "base_url": "https://test.com",
            "api_key": "test-key"
        },
        "expected": {
            "agent_name": "test-agent",
            "model_context": "mock_context"
        }
    }
]

# Test data for API URL construction
API_URL_DATA = [
    {
        "id": "basic_url",
        "agent_name": "my-agent",
        "base_url": "https://api.test.com",
        "expected_url": "https://api.test.com/v1/agents/my-agent"
    },
    {
        "id": "url_with_trailing_slash",
        "agent_name": "my-agent",
        "base_url": "https://api.test.com/",
        "expected_url": "https://api.test.com/v1/agents/my-agent"
    },
    {
        "id": "complex_agent_name",
        "agent_name": "my-complex-agent-name",
        "base_url": "https://api.test.com",
        "expected_url": "https://api.test.com/v1/agents/my-complex-agent-name"
    }
]

# Test data for sync functionality
SYNC_TEST_DATA = [
    {
        "id": "sync_disabled",
        "config": MINIMAL_CONFIG,
        "time_elapsed": 100,
        "should_sync": False
    },
    {
        "id": "sync_enabled_interval_not_passed",
        "config": CONFIG_WITH_SYNC,
        "time_elapsed": 5,
        "should_sync": False
    },
    {
        "id": "sync_enabled_interval_passed",
        "config": CONFIG_WITH_SYNC,
        "time_elapsed": 15,
        "should_sync": True
    }
]

