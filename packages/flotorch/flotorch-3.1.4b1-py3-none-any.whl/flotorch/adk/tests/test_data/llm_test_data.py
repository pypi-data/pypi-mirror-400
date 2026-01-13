"""Test data for FlotorchADKLLM tests.

Test data matches actual SDK response format for ADK agents.
Based on Google ADK agent flow with custom tools.
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
            "model": "openai/gpt-4o-mini"
        }
    },
    {
        "id": "different_model",
        "params": {
            "model_id": "anthropic/claude-3-sonnet",
            "api_key": "another-key",
            "base_url": "https://qa-gateway.flotorch.cloud"
        },
        "expected": {
            "model": "anthropic/claude-3-sonnet"
        }
    },
]

# Test data for generate_content_async 
GENERATE_CONTENT_DATA = [
    {
        "id": "simple_text_response",
        "mock_response_content": "I can help you with that!",
        "mock_response_metadata": {"raw_response": {}},
        "has_tools": False,
        "has_response_schema": False,
        "expected_parts_count": 1,
        "expected_part_type": "text"
    },
    {
        "id": "calculator_tool_call",
        "mock_response_content": "",
        "mock_response_metadata": {
            "raw_response": {
                "choices": [{
                    "message": {
                        "content": "",
                        "tool_calls": [{
                            "id": "call_calc_123",
                            "type": "function",
                            "function": {
                                "name": "calculator",
                                "arguments": '{"expression": "15*7"}'
                            }
                        }]
                    }
                }]
            }
        },
        "has_tools": True,
        "has_response_schema": False,
        "expected_parts_count": 1,
        "expected_part_type": "function_call"
    },
    {
        "id": "time_tool_call",
        "mock_response_content": "",
        "mock_response_metadata": {
            "raw_response": {
                "choices": [{
                    "message": {
                        "content": "",
                        "tool_calls": [{
                            "id": "call_time_456",
                            "type": "function",
                            "function": {
                                "name": "get_current_time",
                                "arguments": '{}'
                            }
                        }]
                    }
                }]
            }
        },
        "has_tools": True,
        "has_response_schema": False,
        "expected_parts_count": 1,
        "expected_part_type": "function_call"
    },
    {
        "id": "analyze_text_tool_call",
        "mock_response_content": "",
        "mock_response_metadata": {
            "raw_response": {
                "choices": [{
                    "message": {
                        "content": "",
                        "tool_calls": [{
                            "id": "call_analyze_789",
                            "type": "function",
                            "function": {
                                "name": "analyze_text",
                                "arguments": '{"text": "Flotorch makes AI development easy!"}'
                            }
                        }]
                    }
                }]
            }
        },
        "has_tools": True,
        "has_response_schema": False,
        "expected_parts_count": 1,
        "expected_part_type": "function_call"
    },
]
