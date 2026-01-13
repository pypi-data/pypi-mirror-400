"""Test data for FlotorchStrandsModel tests.

Test data matches actual SDK response format for Strands agents.
Based on Strands agent flow with streaming and structured output.
"""

# Test data for initialization
INIT_DATA = [
    {
        "id": "basic_init",
        "params": {
            "model_id": "flotorch/openai:latest",
            "api_key": "test-key",
            "base_url": "https://api.flotorch.cloud"
        },
        "expected": {
            "model_id": "flotorch/openai:latest",
            "api_key": "test-key",
            "base_url": "https://api.flotorch.cloud"
        }
    },
    {
        "id": "different_model",
        "params": {
            "model_id": "openai/gpt-4o-mini",
            "api_key": "another-key",
            "base_url": "https://qa-gateway.flotorch.cloud"
        },
        "expected": {
            "model_id": "openai/gpt-4o-mini",
            "api_key": "another-key",
            "base_url": "https://qa-gateway.flotorch.cloud"
        }
    },
]

# Test data for stream method
STREAM_DATA = [
    {
        "id": "simple_text_response",
        "mock_response_content": "Python is a programming language.",
        "mock_response_metadata": {
            "inputTokens": "104",
            "outputTokens": "61",
            "totalTokens": "165",
            "raw_response": {}
        },
        "has_tools": False,
        "has_system_prompt": False,
        "expected_events_count": 5  # messageStart, contentBlockStart, contentBlockDelta, contentBlockStop, messageStop
    },
    {
        "id": "with_tools",
        "mock_response_content": "The result is 15.",
        "mock_response_metadata": {
            "inputTokens": "120",
            "outputTokens": "50",
            "totalTokens": "170",
            "raw_response": {}
        },
        "has_tools": True,
        "has_system_prompt": False,
        "expected_events_count": 5
    },
    {
        "id": "with_system_prompt",
        "mock_response_content": "I can help with that!",
        "mock_response_metadata": {
            "inputTokens": "100",
            "outputTokens": "40",
            "totalTokens": "140",
            "raw_response": {}
        },
        "has_tools": False,
        "has_system_prompt": True,
        "expected_events_count": 5
    },
]

# Test data for structured output
STRUCTURED_OUTPUT_DATA = [
    {
        "id": "simple_structured_output",
        "mock_response_content": '{"Answer": "Python is a programming language"}',
        "mock_response_metadata": {
            "raw_response": {}
        },
        "output_field": "Answer",
        "expected_value": "Python is a programming language"
    },
    {
        "id": "complex_structured_output",
        "mock_response_content": '{"result": "Success", "confidence": 0.95}',
        "mock_response_metadata": {
            "raw_response": {}
        },
        "output_field": "result",
        "expected_value": "Success"
    },
]

