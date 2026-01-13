"""Tests for LangChain LLM Utilities."""

from unittest.mock import Mock
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage, FunctionMessage
)
from langchain_core.tools import tool
from flotorch.langchain.utils.llm_utils import (
    convert_messages_to_dicts, 
    convert_tools_to_format,
    parse_flotorch_response_bind_tools,
    parse_flotorch_response_bind_functions, 
    _extract_raw_message
)


class TestConvertMessages:
    """Test convert_messages_to_dicts()."""

    def test_all_basic_message_types(self):
        """Test SystemMessage, HumanMessage, AIMessage conversion."""
        messages = [
            SystemMessage(content="Sys"),
            HumanMessage(content="User"),
            AIMessage(content="AI")
        ]
        result = convert_messages_to_dicts(messages)
        assert ([m["role"] for m in result] ==
                ["system", "user", "assistant"])
        assert [m["content"] for m in result] == ["Sys", "User", "AI"]

    def test_ai_message_with_tool_calls(self):
        """Test AIMessage with tool_calls."""
        msg = AIMessage(
            content="Tool",
            tool_calls=[{"id": "1", "name": "calc", "args": {"x": 5}}]
        )
        result = convert_messages_to_dicts([msg])
        assert result[0]["role"] == "assistant"
        assert result[0]["tool_calls"][0]["function"]["name"] == "calc"

    def test_ai_message_with_function_call(self):
        """Test AIMessage with legacy function_call."""
        msg = AIMessage(
            content="",
            additional_kwargs={
                "function_call": {"name": "search", "arguments": "{}"}
            }
        )
        result = convert_messages_to_dicts([msg])
        assert result[0]["tool_calls"][0]["function"]["name"] == "search"

    def test_tool_message(self):
        """Test ToolMessage conversion."""
        msg = ToolMessage(
            content="Result", tool_call_id="call_1", name="calc"
        )
        result = convert_messages_to_dicts([msg])
        assert result[0]["role"] == "tool"
        assert result[0]["tool_call_id"] == "call_1"

    def test_function_message(self):
        """Test FunctionMessage conversion."""
        msgs = [
            AIMessage(content="", additional_kwargs={
                "function_call": {"name": "search", "arguments": "{}"}
            }),
            FunctionMessage(content="Results", name="search")
        ]
        result = convert_messages_to_dicts(msgs)
        assert result[1]["role"] == "tool"
        assert result[1]["name"] == "search"

    def test_unhandled_message_type(self):
        """Test unhandled message type fallback."""
        unknown_msg = Mock(content="Unknown")
        result = convert_messages_to_dicts([unknown_msg])
        assert result[0]["role"] == "user"


class TestConvertTools:
    """Test convert_tools_to_format()."""

    def test_simple_tool(self):
        """Test basic tool conversion."""
        @tool
        def calculator(expr: str) -> str:
            """Calculate."""
            return "42"

        result = convert_tools_to_format([calculator])
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "calculator"

    def test_tool_with_typed_params(self):
        """Test tool with typed parameters."""
        @tool
        def func(a: int, b: float, c: bool) -> str:
            """Test."""
            return ""

        props = convert_tools_to_format([func])[0]["function"][
            "parameters"]["properties"]
        assert props["a"]["type"] == "integer"
        assert props["b"]["type"] == "number"
        assert props["c"]["type"] == "boolean"

    def test_dict_tool(self):
        """Test tool in dict format."""
        tool_dict = {"type": "function", "function": {"name": "custom"}}
        assert convert_tools_to_format([tool_dict])[0] == tool_dict

    def test_tool_with_pydantic_args_schema(self):
        """Test tool with Pydantic args_schema."""
        from pydantic import BaseModel, Field

        class SearchInput(BaseModel):
            query: str = Field(description="Search query")

        @tool(args_schema=SearchInput)
        def search(query: str) -> str:
            """Search."""
            return "results"

        result = convert_tools_to_format([search])
        assert "parameters" in result[0]["function"]


class TestHelpers:
    """Test helper functions."""

    def test_extract_raw_message(self):
        """Test _extract_raw_message."""
        response = Mock(
            content="",
            metadata={
                "raw_response": {"choices": [{"message": {"content": "x"}}]}
            }
        )
        result = _extract_raw_message(response)
        assert result["content"] == "x"

    def test_extract_raw_message_no_metadata(self):
        """Test _extract_raw_message without metadata."""
        response = Mock(content="", metadata={})
        assert _extract_raw_message(response) is None


class TestParseBindTools:
    """Test parse_flotorch_response_bind_tools()."""

    def test_simple_text(self):
        """Test simple text response."""
        response = Mock(content="Text", metadata={})
        result = parse_flotorch_response_bind_tools(response)
        assert isinstance(result, AIMessage)
        assert result.content == "Text"

    def test_with_tool_calls(self):
        """Test response with tool calls."""
        response = Mock(
            content="Tool",
            metadata={
                "raw_response": {"choices": [{"message": {
                    "content": "Tool",
                    "tool_calls": [{
                        "id": "1",
                        "function": {"name": "calc", "arguments": '{"x": 5}'}
                    }]
                }}]}
            }
        )
        result = parse_flotorch_response_bind_tools(response)
        assert result.tool_calls[0]["name"] == "calc"
        assert result.tool_calls[0]["args"]["x"] == 5

    def test_multiple_tool_calls(self):
        """Test multiple tool calls."""
        response = Mock(
            content="",
            metadata={
                "raw_response": {"choices": [{"message": {
                    "content": "",
                    "tool_calls": [
                        {"id": "1", "function": {
                            "name": "tool1", "arguments": "{}"
                        }},
                        {"id": "2", "function": {
                            "name": "tool2", "arguments": "{}"
                        }}
                    ]
                }}]}
            }
        )
        result = parse_flotorch_response_bind_tools(response)
        assert len(result.tool_calls) == 2

    def test_exception_handling(self):
        """Test exception handling."""
        response = Mock(content="Fallback", metadata=None)
        result = parse_flotorch_response_bind_tools(response)
        assert isinstance(result, AIMessage)
        assert result.content == "Fallback"


class TestParseBindFunctions:
    """Test parse_flotorch_response_bind_functions()."""

    def test_simple_text(self):
        """Test simple text response."""
        response = Mock(
            content="Text",
            metadata={
                "raw_response": {"choices": [{"message": {"content": "Text"}}]}
            }
        )
        result = parse_flotorch_response_bind_functions(response)
        assert result.content == "Text"
        assert "function_call" not in result.additional_kwargs

    def test_converts_to_function_call(self):
        """Test converts tool_calls to function_call."""
        response = Mock(
            content="Call",
            metadata={
                "raw_response": {"choices": [{"message": {
                    "content": "Call",
                    "tool_calls": [{
                        "id": "1",
                        "function": {
                            "name": "search", "arguments": '{"q": "test"}'
                        }
                    }]
                }}]}
            }
        )
        result = parse_flotorch_response_bind_functions(response)
        assert (result.additional_kwargs["function_call"]["name"] ==
                "search")
        assert isinstance(
            result.additional_kwargs["function_call"]["arguments"], str
        )

    def test_uses_first_tool_call_only(self):
        """Test only first tool call used."""
        response = Mock(
            content="",
            metadata={
                "raw_response": {"choices": [{"message": {
                    "content": "",
                    "tool_calls": [
                        {"id": "1", "function": {
                            "name": "first", "arguments": "{}"
                        }},
                        {"id": "2", "function": {
                            "name": "second", "arguments": "{}"
                        }}
                    ]
                }}]}
            }
        )
        result = parse_flotorch_response_bind_functions(response)
        assert (result.additional_kwargs["function_call"]["name"] ==
                "first")

    def test_exception_handling(self):
        """Test exception handling."""
        response = Mock(content="Fallback", metadata=None)
        result = parse_flotorch_response_bind_functions(response)
        assert isinstance(result, AIMessage)
        assert result.content == "Fallback"


class TestEdgeCases:
    """Test edge cases for coverage."""

    def test_ai_dict_args_serialization(self):
        """Test AIMessage tool_call dict args serialization."""
        import json
        msg = AIMessage(content="", tool_calls=[
            {"id": "1", "name": "fn", "args": {"key": "val"}}
        ])
        result = convert_messages_to_dicts([msg])
        args = result[0]["tool_calls"][0]["function"]["arguments"]
        assert json.loads(args) == {"key": "val"}

    def test_function_call_exception(self):
        """Test function_call exception path."""
        msg = AIMessage(content="test")
        result = convert_messages_to_dicts([msg])
        assert result[0]["content"] == "test"

    def test_function_call_non_dict_args(self):
        """Test function_call with non-dict args."""
        msg = AIMessage(content="", additional_kwargs={
            "function_call": {"name": "fn", "arguments": 123}
        })
        result = convert_messages_to_dicts([msg])
        assert "tool_calls" in result[0]

    def test_tool_with_signature(self):
        """Test tool signature inspection."""
        @tool
        def func(a: int, b: float, c: bool, d: str) -> str:
            """Tool."""
            return ""
        props = convert_tools_to_format([func])[0]["function"][
            "parameters"]["properties"]
        assert props["a"]["type"] == "integer"
        assert props["b"]["type"] == "number"
        assert props["c"]["type"] == "boolean"
        assert props["d"]["type"] == "string"

    def test_tool_dict_args_schema(self):
        """Test tool with dict args_schema."""
        @tool
        def my_tool(x: str) -> str:
            """Tool."""
            return "ok"
        my_tool.args_schema = {"type": "object", "properties": {}}
        result = convert_tools_to_format([my_tool])
        assert "parameters" in result[0]["function"]

    def test_tool_error_skip(self):
        """Test tool conversion error handling."""
        class BadTool:
            pass
        result = convert_tools_to_format([BadTool()])
        assert len(result) == 0

    def test_parse_invalid_json_args(self):
        """Test parsing with invalid JSON args."""
        response = Mock(content="", metadata={
            "raw_response": {"choices": [{"message": {
                "tool_calls": [{
                    "id": "1",
                    "function": {"name": "f", "arguments": "bad{json"}
                }]
            }}]}
        })
        result = parse_flotorch_response_bind_tools(response)
        assert isinstance(result, AIMessage)

    def test_parse_no_raw_msg(self):
        """Test parsing without raw message."""
        response = Mock(content="text", metadata={})
        result = parse_flotorch_response_bind_tools(response)
        assert result.content == "text"

    def test_bind_functions_dict_args(self):
        """Test bind_functions with dict args."""
        response = Mock(content="", metadata={
            "raw_response": {"choices": [{"message": {
                "tool_calls": [{
                    "id": "1",
                    "function": {"name": "f", "arguments": {"k": "v"}}
                }]
            }}]}
        })
        result = parse_flotorch_response_bind_functions(response)
        assert "function_call" in result.additional_kwargs

    def test_bind_functions_non_string_args(self):
        """Test bind_functions with non-string args."""
        response = Mock(content="", metadata={
            "raw_response": {"choices": [{"message": {
                "tool_calls": [{
                    "id": "1",
                    "function": {"name": "f", "arguments": 123}
                }]
            }}]}
        })
        result = parse_flotorch_response_bind_functions(response)
        assert "function_call" in result.additional_kwargs
