"""Test data for FlotorchAutogenLLM tests.

This module provides comprehensive test scenarios for FlotorchAutogenLLM
including initialization, create method with various contexts, and helper
methods.
"""

from unittest.mock import Mock

from autogen_core import FunctionCall
from autogen_core.models import AssistantMessage, UserMessage
from pydantic import BaseModel


class SimpleOutputSchema(BaseModel):
    """Simple Pydantic schema for testing response formats."""

    result: str
    score: float


# Test data for initialization scenarios
INIT_DATA = [
    {
        "id": "basic_flotorch_model",
        "params": {
            "model_id": "flotorch/flotorch-model",
            "api_key": "test-key",
            "base_url": "https://test.com"
        },
        "expected": {
            "_total_usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }
    },
    {
        "id": "gpt4_model",
        "params": {
            "model_id": "gpt-4",
            "api_key": "gpt-key",
            "base_url": "https://api.openai.com"
        },
        "expected": {
            "_total_usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }
    },
    {
        "id": "claude_model",
        "params": {
            "model_id": "claude-3-sonnet",
            "api_key": "claude-key",
            "base_url": "https://api.anthropic.com"
        },
        "expected": {
            "_total_usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }
    }
]


# Test data for create method scenarios
CREATE_DATA = [
    {
        "id": "simple_conversation",
        "messages": [UserMessage(content="Hello, how are you?", source="user")],
        "tools": None,
        "json_output": None,
        "mock_response": {
            "content": ("Hello! I'm doing well, thank you for asking. "
                       "How can I assist you today?"),
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "content": ("Hello! I'm doing well, thank you for "
                                      "asking. How can I assist you today?")
                        }
                    }],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 18}
                },
                "inputTokens": 12,
                "outputTokens": 18
            }
        },
        "expected_content": ("Hello! I'm doing well, thank you for asking. "
                           "How can I assist you today?"),
        "expected_finish_reason": "stop",
        "expected_usage": {"prompt_tokens": 12, "completion_tokens": 18}
    },
    {
        "id": "function_call_weather",
        "messages": [UserMessage(content="What's the weather in London?",
                                  source="user")],
        "tools": [Mock(schema={
            "name": "get_weather",
            "description": "Get current weather for a city"
        })],
        "json_output": None,
        "mock_response": {
            "content": [FunctionCall(
                id="call_weather_123",
                name="get_weather",
                arguments='{"city": "London"}'
            )],
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "tool_calls": [{
                                "id": "call_weather_123",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"city": "London"}'
                                }
                            }]
                        }
                    }],
                    "usage": {"prompt_tokens": 18, "completion_tokens": 12}
                },
                "inputTokens": 18,
                "outputTokens": 12
            }
        },
        "expected_content_type": list,
        "expected_finish_reason": "function_calls",
        "expected_usage": {"prompt_tokens": 18, "completion_tokens": 12}
    },
    {
        "id": "json_structured_output",
        "messages": [UserMessage(content="Analyze the sentiment of this text: 'I love this product!'", source="user")],
        "tools": None,
        "json_output": SimpleOutputSchema,
        "mock_response": {
            "content": '{"result": "positive", "score": 0.92}',
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "content": '{"result": "positive", "score": 0.92}'
                        }
                    }],
                    "usage": {"prompt_tokens": 25, "completion_tokens": 8}
                },
                "inputTokens": 25,
                "outputTokens": 8
            }
        },
        "expected_content": '{"result": "positive", "score": 0.92}',
        "expected_finish_reason": "stop",
        "expected_usage": {"prompt_tokens": 25, "completion_tokens": 8}
    },
    {
        "id": "multi_turn_conversation",
        "messages": [
            UserMessage(content="What is Python?", source="user"),
            AssistantMessage(content="Python is a programming language.", source="assistant"),
            UserMessage(content="What are its main features?", source="user")
        ],
        "tools": None,
        "json_output": None,
        "mock_response": {
            "content": ("Python's main features include: 1) Simple and readable syntax, "
                       "2) Object-oriented programming, 3) Extensive standard library, "
                       "4) Cross-platform compatibility, 5) Dynamic typing, "
                       "6) Interpreted language, and 7) Strong community support."),
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "content": ("Python's main features include: 1) Simple and readable syntax, "
                                      "2) Object-oriented programming, 3) Extensive standard library, "
                                      "4) Cross-platform compatibility, 5) Dynamic typing, "
                                      "6) Interpreted language, and 7) Strong community support.")
                        }
                    }],
                    "usage": {"prompt_tokens": 35, "completion_tokens": 45}
                },
                "inputTokens": 35,
                "outputTokens": 45
            }
        },
        "expected_content": ("Python's main features include: 1) Simple and readable syntax, "
                           "2) Object-oriented programming, 3) Extensive standard library, "
                           "4) Cross-platform compatibility, 5) Dynamic typing, "
                           "6) Interpreted language, and 7) Strong community support."),
        "expected_finish_reason": "stop",
        "expected_usage": {"prompt_tokens": 35, "completion_tokens": 45}
    },
    {
        "id": "empty_messages",
        "messages": [],
        "tools": None,
        "json_output": None,
        "mock_response": {
            "content": "",
            "metadata": {
                "raw_response": {
                    "choices": [{"message": {"content": ""}}],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0}
                },
                "inputTokens": 0,
                "outputTokens": 0
            }
        },
        "expected_content": "",
        "expected_finish_reason": "stop",
        "expected_usage": {"prompt_tokens": 0, "completion_tokens": 0}
    },
    {
        "id": "complex_function_call",
        "messages": [UserMessage(content="Book a flight from New York to London for tomorrow", source="user")],
        "tools": [
            Mock(schema={"name": "search_flights", "description": "Search for available flights"}),
            Mock(schema={"name": "book_flight", "description": "Book a specific flight"})
        ],
        "json_output": None,
        "mock_response": {
            "content": [FunctionCall(
                id="call_flight_456",
                name="search_flights",
                arguments=('{"origin": "New York", "destination": "London", '
                          '"date": "2024-01-16"}')
            )],
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "tool_calls": [{
                                "id": "call_flight_456",
                                "function": {
                                    "name": "search_flights",
                                    "arguments": ('{"origin": "New York", '
                                                '"destination": "London", '
                                                '"date": "2024-01-16"}')
                                }
                            }]
                        }
                    }],
                    "usage": {"prompt_tokens": 28, "completion_tokens": 15}
                },
                "inputTokens": 28,
                "outputTokens": 15
            }
        },
        "expected_content_type": list,
        "expected_finish_reason": "function_calls",
        "expected_usage": {"prompt_tokens": 28, "completion_tokens": 15}
    }
]


# Test data for streaming scenarios
STREAM_DATA = [
    {
        "id": "basic_streaming",
        "messages": [UserMessage(content="Write a short story about a robot", source="user")],
        "mock_response": {
            "content": "Once upon a time, in a distant future, there lived a robot named ARIA who dreamed of understanding human emotions.",
            "metadata": {
                "raw_response": {
                    "choices": [{
                        "message": {
                            "content": "Once upon a time, in a distant future, there lived a robot named ARIA who dreamed of understanding human emotions."
                        }
                    }],
                    "usage": {"prompt_tokens": 15, "completion_tokens": 25}
                },
                "inputTokens": 15,
                "outputTokens": 25
            }
        },
        "expected_content": "Once upon a time, in a distant future, there lived a robot named ARIA who dreamed of understanding human emotions.",
        "expected_finish_reason": "stop"
    }
]


# Test data for error scenarios
ERROR_DATA = [
    {
        "id": "network_error",
        "messages": [UserMessage(content="Test message", source="user")],
        "error": Exception("Network connection failed"),
        "expected_error": "Network connection failed"
    },
    {
        "id": "api_error",
        "messages": [UserMessage(content="Test message", source="user")],
        "error": Exception("API rate limit exceeded"),
        "expected_error": "API rate limit exceeded"
    },
    {
        "id": "invalid_request",
        "messages": [UserMessage(content="Test message", source="user")],
        "error": ValueError("Invalid request parameters"),
        "expected_error": "Invalid request parameters"
    }
]


# Test data for helper method scenarios
HELPER_METHOD_DATA = [
    {
        "id": "usage_tracking",
        "scenario": "accumulated_usage",
        "mock_usage": {"prompt_tokens": 100, "completion_tokens": 50},
        "expected_actual": {"prompt_tokens": 100, "completion_tokens": 50},
        "expected_total": {"prompt_tokens": 100, "completion_tokens": 50}
    },
    {
        "id": "token_counting",
        "scenario": "count_tokens",
        "messages": [UserMessage(content="Hello world", source="user")],
        "expected_count": None  # Current implementation returns None
    },
    {
        "id": "remaining_tokens",
        "scenario": "remaining_tokens",
        "messages": [UserMessage(content="Test message", source="user")],
        "expected_remaining": 1000  # Mocked super call
    }
]