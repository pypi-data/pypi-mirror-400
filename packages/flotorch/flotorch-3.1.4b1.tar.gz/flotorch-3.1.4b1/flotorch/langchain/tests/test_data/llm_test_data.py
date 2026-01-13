"""Test data for FlotorchLangChainLLM tests.

Test data matches actual SDK response format and covers both:
- LangChain: create_openai_functions_agent (uses bind)
- LangGraph: create_react_agent (uses bind_tools)
"""

# Test data for initialization
INIT_DATA = [
    {
        "id": "basic_init",
        "params": {
            "model_id": "openai/gpt-4o-mini",
            "api_key": "test-key",
            "base_url": "https://api.flotorch.cloud"
        },
        "expected": {
            "_model_id": "openai/gpt-4o-mini",
            "_temperature": 0.0
        }
    },
    {
        "id": "with_temperature",
        "params": {
            "model_id": "anthropic/claude-3-sonnet",
            "api_key": "another-key",
            "base_url": "https://qa-gateway.flotorch.cloud",
            "temperature": 0.7
        },
        "expected": {
            "_model_id": "anthropic/claude-3-sonnet",
            "_temperature": 0.7
        }
    },
]

# Test data for _generate method (matches actual SDK response format)
GENERATE_DATA = [
    {
        "id": "simple_text_response",
        "mock_response_content": "Hello, how can I help you?",
        "mock_response_metadata": {},
        "has_tools": False,
        "binding_type": None,
        "stop_sequences": None
    },
    {
        "id": "langgraph_bind_tools_with_tool_call",
        "mock_response_content": "Let me analyze that text for you",
        "mock_response_metadata": {
            "raw_response": {
                "choices": [{
                    "message": {
                        "content": "Let me analyze that text for you",
                        "tool_calls": [{
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "analyze_text",
                                "arguments": '{"text": "Hello world"}'
                            }
                        }]
                    }
                }]
            }
        },
        "has_tools": True,
        "binding_type": "bind_tools",
        "stop_sequences": None
    },
    {
        "id": "langchain_bind_functions_with_function_call",
        "mock_response_content": "Let me check the weather",
        "mock_response_metadata": {
            "raw_response": {
                "choices": [{
                    "message": {
                        "content": "Let me check the weather",
                        "tool_calls": [{
                            "id": "call_xyz456",
                            "type": "function",
                            "function": {
                                "name": "weather",
                                "arguments": '{"city": "London"}'
                            }
                        }]
                    }
                }]
            }
        },
        "has_tools": True,
        "binding_type": "bind_functions",
        "stop_sequences": None
    },
    {
        "id": "with_stop_sequences",
        "mock_response_content": "Response with stop",
        "mock_response_metadata": {},
        "has_tools": False,
        "binding_type": None,
        "stop_sequences": ["END", "STOP"]
    },
]
