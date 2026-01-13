"""Test data for FlotorchCrewAILLM tests.

This module contains test data for FlotorchCrewAILLM initialization and
call method tests, following actual workflow patterns.
"""

from pydantic import BaseModel, Field


class SimpleOutputSchema(BaseModel):
    """Simple Pydantic schema for testing response formats."""

    result: str = Field(description="Test result")
    score: float = Field(description="Test score")


INIT_DATA = [
    {
        "id": "basic",
        "params": {
            "model_id": "gpt-4",
            "api_key": "key",
            "base_url": "https://test.com"
        },
        "expected": {
            "model": "gpt-4",
            "temperature": None,
            "stop": []
        }
    },
    {
        "id": "with_temperature",
        "params": {
            "model_id": "gpt-4",
            "api_key": "key",
            "base_url": "https://test.com",
            "temperature": 0.7
        },
        "expected": {
            "model": "gpt-4",
            "temperature": 0.7,
            "stop": []
        }
    },
]


CALL_DATA = [
    {
        "id": "simple_no_context",
        "messages": "Hello",
        "from_task": None,
        "from_agent": None,
        "mock_response": "Hi there!",
        "expected": "Hi there!"
    },
    {
        "id": "plain_text_no_pydantic",
        "messages": [{"role": "user", "content": "What is AI?"}],
        "from_task": None,
        "from_agent": None,
        "mock_response": "AI stands for Artificial Intelligence",
        "expected": "AI stands for Artificial Intelligence"
    },
    {
        "id": "with_task_pydantic",
        "messages": [{"role": "user", "content": "Test"}],
        "from_task": "has_pydantic",
        "from_agent": None,
        "mock_response": '{"result": "success", "score": 0.9}',
        "expected": '{"result": "success", "score": 0.9}'
    },
    {
        "id": "tool_action_response",
        "messages": [
            {"role": "system", "content": "You are agent"},
            {"role": "user", "content": "Analyze"}
        ],
        "from_task": "has_pydantic",
        "from_agent": None,
        "mock_response": 'Action: analyze_text\nAction Input: {"text":"sample"}',
        "expected": 'Action: analyze_text\nAction Input: {"text":"sample"}'
    },
]
