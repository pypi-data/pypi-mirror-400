"""Tests for FlotorchStrandsModel."""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field

from flotorch.strands.llm import FlotorchStrandsModel
from flotorch.strands.tests.test_data.llm_test_data import (
    INIT_DATA, STREAM_DATA
)


class TestInit:
    """Test FlotorchStrandsModel initialization."""

    @pytest.mark.parametrize(
        "data", INIT_DATA, ids=[d["id"] for d in INIT_DATA]
    )
    def test_init_sets_attributes(self, data):
        """Test that __init__ sets all instance attributes correctly."""
        with patch('flotorch.strands.llm.FlotorchLLM'):
            llm = FlotorchStrandsModel(**data["params"])
            assert (llm.config["model_id"] == data["expected"]["model_id"]
                    and llm.config["api_key"] == data["expected"]["api_key"]
                    and llm.config["base_url"] ==
                    data["expected"]["base_url"])

    def test_init_creates_flotorch_llm_instance(self):
        """Test that FlotorchLLM instance is created."""
        with patch('flotorch.strands.llm.FlotorchLLM') as mock_llm_class:
            llm = FlotorchStrandsModel(
                model_id="flotorch/openai:latest",
                api_key="my-key",
                base_url="https://api.flotorch.cloud"
            )
            mock_llm_class.assert_called_once_with(
                model_id="flotorch/openai:latest",
                api_key="my-key",
                base_url="https://api.flotorch.cloud"
            )
            assert llm.flotorch_llm == mock_llm_class.return_value

    def test_init_requires_api_key(self, monkeypatch):
        """Test initialization fails without api_key."""
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        monkeypatch.delenv("FLOTORCH_GATEWAY_URL", raising=False)
        with pytest.raises(ValueError, match="API key must be provided"):
            FlotorchStrandsModel(
                model_id="test-model", base_url="https://test.com"
            )

    def test_init_requires_base_url(self, monkeypatch):
        """Test initialization fails without base_url."""
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        monkeypatch.delenv("FLOTORCH_GATEWAY_URL", raising=False)
        with pytest.raises(ValueError, match="Base URL must be provided"):
            FlotorchStrandsModel(model_id="test-model", api_key="test-key")

    def test_init_gets_api_key_from_env(self, monkeypatch):
        """Test initialization gets API key from environment."""
        monkeypatch.setenv("FLOTORCH_API_KEY", "env-key")
        monkeypatch.setenv("FLOTORCH_GATEWAY_URL", "https://env-url.com")
        with patch('flotorch.strands.llm.FlotorchLLM') as mock_llm:
            llm = FlotorchStrandsModel(model_id="test-model")
            assert (llm.config["api_key"] == "env-key" and
                    llm.config["base_url"] == "https://env-url.com")

    def test_init_gets_base_url_from_env(self, monkeypatch):
        """Test initialization gets base URL from environment."""
        monkeypatch.setenv("FLOTORCH_API_KEY", "env-key")
        monkeypatch.setenv("FLOTORCH_GATEWAY_URL", "https://env-url.com")
        with patch('flotorch.strands.llm.FlotorchLLM') as mock_llm:
            llm = FlotorchStrandsModel(model_id="test-model")
            assert llm.config["base_url"] == "https://env-url.com"


class TestStreamMethod:
    """Test stream method for conversational responses."""

    @pytest.mark.parametrize(
        "data", STREAM_DATA, ids=[d["id"] for d in STREAM_DATA]
    )
    @pytest.mark.asyncio
    async def test_stream_with_scenarios(
        self, strands_llm_instance, mock_flotorch_llm, data
    ):
        """Test stream method with different scenarios."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content=data["mock_response_content"],
            metadata=data["mock_response_metadata"]
        )
        messages = [{"role": "user", "content": [{"text": "test"}]}]
        tool_specs = [{
            "name": "multiply",
            "description": "Multiply two numbers",
            "inputSchema": {"json": {"properties": {}, "type": "object"}}
        }] if data["has_tools"] else None
        system_prompt = (
            "You are helpful" if data["has_system_prompt"] else None
        )
        events = []
        async for event in strands_llm_instance.stream(
            messages=messages,
            tool_specs=tool_specs,
            system_prompt=system_prompt
        ):
            events.append(event)
        assert (len(events) == data["expected_events_count"] and
                mock_flotorch_llm.ainvoke.called)

    @pytest.mark.asyncio
    async def test_stream_invokes_underlying_llm(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test that stream invokes the underlying FlotorchLLM."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content="Response", metadata={"raw_response": {}}
        )
        messages = [{"role": "user", "content": [{"text": "Test"}]}]
        async for _ in strands_llm_instance.stream(messages=messages):
            pass
        mock_flotorch_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_stream_converts_tools(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test that stream converts tools correctly."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content="Response", metadata={"raw_response": {}}
        )
        messages = [{"role": "user", "content": [{"text": "Test"}]}]
        tools = [{
            "name": "add",
            "description": "Add numbers",
            "inputSchema": {"json": {"properties": {}, "type": "object"}}
        }]
        async for _ in strands_llm_instance.stream(
            messages=messages, tool_specs=tools
        ):
            pass
        call_kwargs = mock_flotorch_llm.ainvoke.call_args.kwargs
        assert "tools" in call_kwargs and call_kwargs["tools"] is not None

    @pytest.mark.asyncio
    async def test_stream_handles_exceptions(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test that stream properly handles exceptions."""
        mock_flotorch_llm.ainvoke.side_effect = Exception("API Error")
        messages = [{"role": "user", "content": [{"text": "Test"}]}]
        events = []
        async for event in strands_llm_instance.stream(messages=messages):
            events.append(event)
        assert len(events) > 0 and "messageStop" in events[-1]


class TestStructuredOutput:
    """Test structured_output method."""

    @pytest.mark.asyncio
    async def test_structured_output_basic(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test basic structured output."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content='{"Answer": "test answer"}',
            metadata={"raw_response": {}}
        )

        class TestOutput(BaseModel):
            Answer: str = Field(description="The answer")

        messages = [{"role": "user", "content": [{"text": "test"}]}]
        results = []
        async for result in strands_llm_instance.structured_output(
            output_model=TestOutput, prompt=messages
        ):
            results.append(result)
        assert len(results) > 0
        if "output" in results[0]:
            assert isinstance(results[0]["output"], TestOutput)

    @pytest.mark.asyncio
    async def test_structured_output_with_system_prompt(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test structured_output with system prompt."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content='{"Answer": "test"}', metadata={"raw_response": {}}
        )

        class TestOutput(BaseModel):
            Answer: str = Field(description="The answer")

        messages = [{"role": "user", "content": [{"text": "test"}]}]
        async for _ in strands_llm_instance.structured_output(
            output_model=TestOutput,
            prompt=messages,
            system_prompt="You are helpful"
        ):
            pass
        mock_flotorch_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_structured_output_handles_parse_errors(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test structured_output handles JSON parse errors."""
        mock_flotorch_llm.ainvoke.return_value = Mock(
            content="invalid json", metadata={"raw_response": {}}
        )

        class TestOutput(BaseModel):
            Answer: str = Field(description="The answer")

        messages = [{"role": "user", "content": [{"text": "test"}]}]
        results = []
        async for result in strands_llm_instance.structured_output(
            output_model=TestOutput, prompt=messages
        ):
            results.append(result)
        assert len(results) > 0 and "error" in results[0]

    @pytest.mark.asyncio
    async def test_structured_output_handles_api_exception(
        self, strands_llm_instance, mock_flotorch_llm
    ):
        """Test structured_output raises exception on API error."""
        mock_flotorch_llm.ainvoke.side_effect = Exception("API Error")

        class TestOutput(BaseModel):
            Answer: str = Field(description="The answer")

        messages = [{"role": "user", "content": [{"text": "test"}]}]
        with pytest.raises(Exception, match="API Error"):
            async for _ in strands_llm_instance.structured_output(
                output_model=TestOutput, prompt=messages
            ):
                pass