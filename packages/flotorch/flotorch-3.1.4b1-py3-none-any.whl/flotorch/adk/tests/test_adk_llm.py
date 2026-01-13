"""Tests for FlotorchADKLLM.

This module tests the FlotorchADKLLM class including initialization,
generate_content_async method, and helper methods.
"""

from unittest.mock import Mock, patch

import pytest
from google.genai import types

from flotorch.adk.llm import FlotorchADKLLM
from flotorch.adk.tests.conftest import MockAIMessage
from flotorch.adk.tests.test_data.llm_test_data import INIT_DATA, GENERATE_CONTENT_DATA


class TestInit:
    """Test FlotorchADKLLM initialization."""

    @pytest.mark.parametrize(
        "data",
        INIT_DATA,
        ids=[d["id"] for d in INIT_DATA]
    )
    def test_init_sets_attributes(self, data):
        """Test that __init__ sets all instance attributes correctly."""
        with patch('flotorch.adk.llm.FlotorchLLM'):
            llm = FlotorchADKLLM(**data["params"])

            for attr, expected_value in data["expected"].items():
                actual_value = getattr(llm, attr)
                assert actual_value == expected_value

    def test_init_creates_flotorch_llm_instance(self):
        """Test that FlotorchLLM instance is created with correct params."""
        with patch('flotorch.adk.llm.FlotorchLLM') as mock_llm_class:
            llm = FlotorchADKLLM(
                model_id="openai/gpt-4o-mini",
                api_key="my-key",
                base_url="https://api.flotorch.cloud"
            )

            mock_llm_class.assert_called_once_with(
                "openai/gpt-4o-mini",
                "my-key",
                "https://api.flotorch.cloud"
            )
            assert llm._llm == mock_llm_class.return_value


class TestGenerateContentAsync:
    """Test FlotorchADKLLM generate_content_async method."""

    @pytest.mark.parametrize(
        "data",
        GENERATE_CONTENT_DATA,
        ids=[d["id"] for d in GENERATE_CONTENT_DATA]
    )
    @pytest.mark.asyncio
    async def test_generate_content_with_scenarios(
        self,
        adk_llm_instance,
        mock_adk_llm,
        data
    ):
        """Test generate_content_async method with different scenarios."""
        mock_adk_llm.ainvoke.return_value = MockAIMessage(
            content=data["mock_response_content"],
            metadata=data["mock_response_metadata"]
        )

        llm_request = Mock()
        llm_request.messages = [types.Content(role="user", parts=[types.Part(text="Test")])]
        llm_request.contents = []
        llm_request.tools_dict = {"test_tool": Mock(name="test_tool")} if data["has_tools"] else None
        llm_request.config = None

        responses = []
        async for response in adk_llm_instance.generate_content_async(llm_request):
            responses.append(response)

        assert len(responses) >= 1
        assert responses[0].content.role == "assistant"
        assert len(responses[0].content.parts) == data["expected_parts_count"]
        mock_adk_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_content_invokes_underlying_llm(self, adk_llm_instance, mock_adk_llm):
        """Test that generate_content_async invokes the underlying FlotorchLLM."""
        mock_adk_llm.ainvoke.return_value = MockAIMessage("Response", {"raw_response": {}})

        llm_request = Mock()
        llm_request.messages = [types.Content(role="user", parts=[types.Part(text="Test")])]
        llm_request.contents = []
        llm_request.tools_dict = None
        llm_request.config = None

        async for _ in adk_llm_instance.generate_content_async(llm_request):
            pass

        mock_adk_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_content_converts_tools(self, adk_llm_instance, mock_adk_llm):
        """Test that generate_content_async converts tools correctly."""
        mock_adk_llm.ainvoke.return_value = MockAIMessage("Response", {"raw_response": {}})

        llm_request = Mock()
        llm_request.messages = [types.Content(role="user", parts=[types.Part(text="Test")])]
        llm_request.contents = []
        llm_request.tools_dict = {"calculator": Mock(name="calculator")}
        llm_request.config = None

        async for _ in adk_llm_instance.generate_content_async(llm_request):
            pass

        call_kwargs = mock_adk_llm.ainvoke.call_args.kwargs
        assert "tools" in call_kwargs
        assert call_kwargs["tools"] is not None

    @pytest.mark.asyncio
    async def test_generate_content_with_response_schema(self, adk_llm_instance, mock_adk_llm):
        """Test that generate_content_async handles response_schema correctly."""
        from pydantic import BaseModel, Field
        
        class TestSchema(BaseModel):
            result: str = Field(description="Result")
        
        mock_adk_llm.ainvoke.return_value = MockAIMessage('{"result": "success"}', {"raw_response": {}})

        llm_request = Mock()
        llm_request.messages = [types.Content(role="user", parts=[types.Part(text="Test")])]
        llm_request.contents = []
        llm_request.tools_dict = None
        llm_request.config = Mock(response_schema=TestSchema)

        async for _ in adk_llm_instance.generate_content_async(llm_request):
            pass

        call_kwargs = mock_adk_llm.ainvoke.call_args.kwargs
        assert "response_format" in call_kwargs
        assert call_kwargs["response_format"] is not None

    @pytest.mark.asyncio
    async def test_generate_content_handles_exceptions(self, adk_llm_instance, mock_adk_llm):
        """Test that generate_content_async properly handles and raises exceptions."""
        mock_adk_llm.ainvoke.side_effect = Exception("API Error")

        llm_request = Mock()
        llm_request.messages = [types.Content(role="user", parts=[types.Part(text="Test")])]
        llm_request.contents = []
        llm_request.tools_dict = None
        llm_request.config = None

        responses = []
        async for response in adk_llm_instance.generate_content_async(llm_request):
            responses.append(response)

        assert len(responses) == 1
        assert responses[0].content.role == "assistant"
