"""Tests for FlotorchLangChainLLM.

This module tests the FlotorchLangChainLLM class including initialization,
_generate, bind_tools, bind, and helper methods.
"""

import pytest
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from flotorch.langchain.llm import FlotorchLangChainLLM
from flotorch.langchain.tests.conftest import MockLLMResponse
from flotorch.langchain.tests.test_data.llm_test_data import (
    INIT_DATA, GENERATE_DATA
)


class TestInit:
    """Test FlotorchLangChainLLM initialization."""

    @pytest.mark.parametrize(
        "data",
        INIT_DATA,
        ids=[d["id"] for d in INIT_DATA]
    )
    def test_init_sets_attributes(self, data):
        """Test that __init__ sets all instance attributes correctly."""
        with patch('flotorch.langchain.llm.FlotorchLLM'):
            llm = FlotorchLangChainLLM(**data["params"])

            for attr, expected_value in data["expected"].items():
                actual_value = getattr(llm, attr)
                assert actual_value == expected_value

    def test_init_creates_flotorch_llm_instance(self):
        """Test that FlotorchLLM instance is created with correct params."""
        with patch('flotorch.langchain.llm.FlotorchLLM') as mock_llm_class:
            llm = FlotorchLangChainLLM(
                model_id="gpt-4",
                api_key="my-key",
                base_url="https://api.com"
            )

            mock_llm_class.assert_called_once_with(
                "gpt-4",
                "my-key",
                "https://api.com"
            )
            assert llm._llm == mock_llm_class.return_value


class TestGenerate:
    """Test FlotorchLangChainLLM _generate method."""

    @pytest.mark.parametrize(
        "data",
        GENERATE_DATA,
        ids=[d["id"] for d in GENERATE_DATA]
    )
    def test_generate_with_scenarios(
        self,
        langchain_llm_instance,
        mock_langchain_llm,
        data
    ):
        """Test _generate method with different scenarios."""
        mock_langchain_llm.invoke.return_value = MockLLMResponse(
            content=data["mock_response_content"],
            metadata=data["mock_response_metadata"]
        )

        if data["binding_type"]:
            langchain_llm_instance._binding_type = data["binding_type"]
            langchain_llm_instance._tools = (
                [{"name": "test_tool"}] if data["has_tools"] else None
            )

        result = langchain_llm_instance._generate(
            [HumanMessage(content="Test")],
            stop=data["stop_sequences"]
        )

        assert result.generations is not None
        assert len(result.generations) == 1
        mock_langchain_llm.invoke.assert_called_once()

    def test_generate_invokes_underlying_llm(
        self, langchain_llm_instance, mock_langchain_llm
    ):
        """Test that _generate invokes the underlying FlotorchLLM."""
        langchain_llm_instance._generate([HumanMessage(content="Test")])
        mock_langchain_llm.invoke.assert_called_once()

    def test_generate_converts_messages(
        self, langchain_llm_instance, mock_langchain_llm
    ):
        """Test that _generate converts messages correctly."""
        messages = [
            SystemMessage(content="System"),
            HumanMessage(content="User"),
            AIMessage(content="Assistant")
        ]

        langchain_llm_instance._generate(messages)

        call_kwargs = mock_langchain_llm.invoke.call_args.kwargs
        assert len(call_kwargs["messages"]) == 3
        assert call_kwargs["messages"][0]["role"] == "system"

    def test_generate_handles_exceptions(
        self, langchain_llm_instance, mock_langchain_llm
    ):
        """Test that _generate properly handles and raises exceptions."""
        mock_langchain_llm.invoke.side_effect = Exception("LLM error")
        with pytest.raises(Exception) as exc_info:
            langchain_llm_instance._generate([HumanMessage(content="Test")])
        assert "LLM error" in str(exc_info.value)


class TestAsyncGenerate:
    """Test FlotorchLangChainLLM _agenerate method."""

    @pytest.mark.asyncio
    async def test_agenerate_invokes_underlying_llm(
        self, langchain_llm_instance_async, mock_langchain_llm_async
    ):
        """Test that _agenerate invokes underlying FlotorchLLM.ainvoke."""
        mock_langchain_llm_async.ainvoke.return_value = MockLLMResponse(
            "Response", {}
        )
        result = await langchain_llm_instance_async._agenerate(
            [HumanMessage(content="Test")]
        )
        mock_langchain_llm_async.ainvoke.assert_called_once()
        assert result.generations is not None

    @pytest.mark.asyncio
    async def test_agenerate_handles_exceptions(
        self, langchain_llm_instance_async, mock_langchain_llm_async
    ):
        """Test that _agenerate handles and raises exceptions."""
        mock_langchain_llm_async.ainvoke.side_effect = Exception(
            "Async LLM error"
        )
        with pytest.raises(Exception) as exc_info:
            await langchain_llm_instance_async._agenerate(
                [HumanMessage(content="Test")]
            )
        assert "Async LLM error" in str(exc_info.value)


class TestBindTools:
    """Test FlotorchLangChainLLM bind_tools method."""

    def test_bind_tools_creates_new_instance(self, langchain_llm_instance):
        """Test that bind_tools creates a new LLM instance."""
        @tool
        def calculator(expr: str) -> str:
            """Calculate."""
            return "42"

        new_llm = langchain_llm_instance.bind_tools([calculator])

        assert new_llm is not langchain_llm_instance
        assert isinstance(new_llm, FlotorchLangChainLLM)

    def test_bind_tools_sets_tools_attribute(self, langchain_llm_instance):
        """Test that bind_tools sets _tools attribute on new instance."""
        @tool
        def calculator(expr: str) -> str:
            """Calculate."""
            return "42"

        new_llm = langchain_llm_instance.bind_tools([calculator])

        assert hasattr(new_llm, '_tools')
        assert len(new_llm._tools) > 0
        assert new_llm._binding_type == "bind_tools"


class TestBind:
    """Test FlotorchLangChainLLM bind method."""

    def test_bind_with_functions_creates_new_instance(
        self, langchain_llm_instance
    ):
        """Test that bind with functions creates a new LLM instance."""
        functions = [{"name": "calc", "description": "Calculate"}]

        new_llm = langchain_llm_instance.bind(functions=functions)

        assert new_llm is not langchain_llm_instance
        assert isinstance(new_llm, FlotorchLangChainLLM)

    def test_bind_sets_functions_as_tools(self, langchain_llm_instance):
        """Test that bind converts functions to tools format."""
        functions = [
            {"name": "calc", "description": "Calculate"},
            {"name": "search", "description": "Search"}
        ]

        new_llm = langchain_llm_instance.bind(functions=functions)

        assert hasattr(new_llm, '_tools')
        assert len(new_llm._tools) == 2
        assert new_llm._binding_type == "bind_functions"


class TestStructuredOutput:
    """Test FlotorchLangChainLLM structured output methods."""

    def test_with_structured_output_pydantic(
        self, langchain_llm_instance, mock_langchain_llm
    ):
        """Test with_structured_output with Pydantic schema."""
        class TestSchema(BaseModel):
            result: str = Field(description="Result")

        mock_langchain_llm.invoke.return_value = MockLLMResponse(
            '{"result": "test"}', {}
        )
        structured_llm = langchain_llm_instance.with_structured_output(
            TestSchema
        )

        from langchain_core.runnables import Runnable
        assert isinstance(structured_llm, Runnable)

    def test_parse_structured_output_valid_json(
        self, langchain_llm_instance
    ):
        """Test _parse_structured_output parses valid JSON."""
        from unittest.mock import Mock
        
        class TestSchema(BaseModel):
            result: str

        response = Mock(content='{"result": "success"}')
        parsed = langchain_llm_instance._parse_structured_output(
            response, TestSchema
        )

        assert isinstance(parsed, TestSchema)
        assert parsed.result == "success"

    def test_parse_structured_output_fallback(
        self, langchain_llm_instance
    ):
        """Test _parse_structured_output handles invalid JSON."""
        from unittest.mock import Mock
        
        class TestSchema(BaseModel):
            result: str

        response = Mock(content="not json")
        parsed = langchain_llm_instance._parse_structured_output(
            response, TestSchema
        )

        assert isinstance(parsed, TestSchema)
        assert parsed.result == "not json"


class TestHelpers:
    """Test helper methods."""

    def test_llm_type_property(self):
        """Test _llm_type property returns 'flotorch'."""
        with patch('flotorch.langchain.llm.FlotorchLLM'):
            llm = FlotorchLangChainLLM(
                model_id="gpt-4",
                api_key="key",
                base_url="https://test.com"
            )
            assert llm._llm_type == "flotorch"

    def test_prepare_extra_body_with_stop_sequences(self):
        """Test _prepare_extra_body with stop sequences."""
        result = FlotorchLangChainLLM._prepare_extra_body(stop=["END", "STOP"])

        assert "stop" in result
        assert result["stop"] == ["END", "STOP"]

    def test_prepare_extra_body_empty(self):
        """Test _prepare_extra_body with no parameters."""
        result = FlotorchLangChainLLM._prepare_extra_body()

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_identifying_params_property(self, langchain_llm_instance):
        """Test _identifying_params property returns correct values."""
        params = langchain_llm_instance._identifying_params

        assert "model_id" in params
        assert "temperature" in params
        assert "base_url" in params


class TestEdgeCases:
    """Test edge cases for coverage."""

    @pytest.mark.asyncio
    async def test_agenerate_bind_functions(
        self, langchain_llm_instance_async, mock_langchain_llm_async
    ):
        """Test _agenerate with bind_functions path."""
        langchain_llm_instance_async._binding_type = "bind_functions"
        mock_langchain_llm_async.ainvoke.return_value = MockLLMResponse(
            "Response", {}
        )
        result = await langchain_llm_instance_async._agenerate(
            [HumanMessage(content="Test")]
        )
        assert result.generations

    def test_json_schema_fallback_path(self, langchain_llm_instance):
        """Test JSON schema with non-JSON content."""
        from unittest.mock import Mock
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        resp = Mock(content="plain")
        result = langchain_llm_instance._parse_structured_output(
            resp, schema
        )
        assert result == {"x": "plain"}

    def test_pydantic_dict_input(self, langchain_llm_instance):
        """Test Pydantic parsing with dict input."""
        class M(BaseModel):
            f: str
        result = langchain_llm_instance._parse_structured_output(
            {"content": "val"}, M
        )
        assert hasattr(result, "f")

    def test_parse_error_recovery(self, langchain_llm_instance):
        """Test error recovery in parsing."""
        from unittest.mock import Mock
        class M(BaseModel):
            v: str

        with patch('json.loads', side_effect=Exception):
            result = langchain_llm_instance._parse_structured_output(
                Mock(content="x"), M
            )
            assert hasattr(result, "v")
