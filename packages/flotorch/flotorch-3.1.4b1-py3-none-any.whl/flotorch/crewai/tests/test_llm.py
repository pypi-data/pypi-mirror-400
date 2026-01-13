"""Tests for FlotorchCrewAILLM.

This module tests the FlotorchCrewAILLM class including initialization,
call method with various contexts, and helper methods.
"""

import pytest
from unittest.mock import patch

from flotorch.crewai.llm import FlotorchCrewAILLM
from flotorch.crewai.tests.conftest import MockLLMResponse
from flotorch.crewai.tests.test_data.llm_test_data import (
    INIT_DATA,
     CALL_DATA
)


class TestInit:
    """Test FlotorchCrewAILLM initialization."""

    @pytest.mark.parametrize(
        "data",
        INIT_DATA,
        ids=[d["id"] for d in INIT_DATA]
    )
    def test_init_sets_attributes(self, data):
        """Test that __init__ sets all instance attributes correctly."""
        with patch('flotorch.crewai.llm.FlotorchLLM'):
            llm = FlotorchCrewAILLM(**data["params"])

            for attr, expected_value in data["expected"].items():
                actual_value = getattr(llm, attr)
                assert actual_value == expected_value

    def test_init_creates_flotorch_llm_instance(self):
        """Test that FlotorchLLM instance is created with correct params."""
        with patch('flotorch.crewai.llm.FlotorchLLM') as mock_llm_class:
            llm = FlotorchCrewAILLM(
                model_id="gpt-4",
                api_key="my-key",
                base_url="https://api.com"
            )

            mock_llm_class.assert_called_once_with(
                "gpt-4",
                "my-key",
                "https://api.com"
            )
            assert llm.llm == mock_llm_class.return_value


class TestCall:
    """Test FlotorchCrewAILLM call method."""

    @pytest.mark.parametrize(
        "data",
        CALL_DATA,
        ids=[d["id"] for d in CALL_DATA]
    )
    def test_call_with_scenarios(
        self,
        llm_instance,
        mock_llm,
        mock_task_with_output_pydantic,
        data
    ):
        """Test call method with different scenarios."""
        mock_llm.invoke.return_value = MockLLMResponse(
            data["mock_response"]
        )

        call_kwargs = {"messages": data["messages"]}

        if data["from_task"] == "has_pydantic":
            call_kwargs["from_task"] = mock_task_with_output_pydantic
        elif data["from_task"]:
            call_kwargs["from_task"] = data["from_task"]

        if data["from_agent"]:
            call_kwargs["from_agent"] = data["from_agent"]

        result = llm_instance.call(**call_kwargs)

        assert result == data["expected"]
        mock_llm.invoke.assert_called_once()

    def test_call_invokes_underlying_llm(self, llm_instance, mock_llm):
        """Test that call invokes the underlying FlotorchLLM."""
        llm_instance.call("test message")

        mock_llm.invoke.assert_called_once()

    def test_call_returns_response_content(self, llm_instance, mock_llm):
        """Test that call returns the content from LLM response."""
        expected_content = "custom response content"
        mock_llm.invoke.return_value = MockLLMResponse(expected_content)

        result = llm_instance.call("test")

        assert result == expected_content

    def test_call_handles_llm_exceptions(self, llm_instance, mock_llm):
        """Test that call properly handles and wraps exceptions."""
        mock_llm.invoke.side_effect = Exception("LLM error")

        with pytest.raises(Exception) as exc_info:
            llm_instance.call("test")

        assert "FlotorchCrewaiLLM error" in str(exc_info.value)


class TestHelpers:
    """Test helper methods."""

    def test_supports_function_calling_returns_true(self, llm_instance):
        """Test supports_function_calling returns True."""
        result = (
            llm_instance.supports_function_calling()
            if callable(llm_instance.supports_function_calling)
            else llm_instance.supports_function_calling
        )
        assert result is True

    def test_supports_stop_words_returns_true(self, llm_instance):
        """Test supports_stop_words returns True."""
        result = (
            llm_instance.supports_stop_words()
            if callable(llm_instance.supports_stop_words)
            else llm_instance.supports_stop_words
        )
        assert result is True
