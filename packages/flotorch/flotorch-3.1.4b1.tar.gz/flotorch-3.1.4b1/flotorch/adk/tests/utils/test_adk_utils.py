"""Tests for ADK LLM Utilities (flotorch/adk/utils/adk_utils.py)."""

from unittest.mock import Mock

from flotorch.adk.utils.adk_utils import (
    build_messages_from_request,
    parse_function_response,
    parse_llm_response_with_tools,
    process_content_parts,
    process_session_events,
    tools_to_openai_format,
)


class TestToolsToOpenAIFormat:
    """Test tools_to_openai_format()."""

    def test_simple_tool(self):
        """Test converting simple tool with basic attributes."""
        tool = Mock()
        tool.name = "calculator"
        tool.description = "Calculate expression"
        tool.func = lambda x: x
        
        result = tools_to_openai_format([tool])
        
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "calculator"
        assert result[0]["function"]["description"] == "Calculate expression"

    def test_tool_with_input_schema(self):
        """Test tool with input_schema."""
        tool = Mock()
        tool.name = "search"
        tool.description = "Search"
        schema = Mock()
        schema.properties = {"query": Mock(), "limit": Mock()}
        schema.required = ["query"]
        tool.input_schema = schema
        tool.func = lambda x: x
        result = tools_to_openai_format([tool])
        assert "parameters" in result[0]["function"]
    
    def test_tool_with_declaration(self):
        """Test tool with _get_declaration."""
        tool = Mock()
        tool.name = "calc"
        decl = Mock()
        decl.parameters = Mock()
        prop = Mock(type=Mock(value='INTEGER'))
        decl.parameters.properties = {'x': prop}
        decl.parameters.required = ['x']
        tool._get_declaration = Mock(return_value=decl)
        result = tools_to_openai_format([tool])
        assert len(result) == 1
    
    def test_tool_exception_handling(self):
        """Test tool exception handling."""
        tool = Mock()
        tool.name.side_effect = Exception("Error")
        result = tools_to_openai_format([tool])
        # Tool conversion continues even with exceptions
        assert isinstance(result, list)


class TestParseFunctionResponse:
    """Test parse_function_response()."""

    def test_parse_with_text_content(self):
        """Test parsing response with text content."""
        response = Mock()
        response.result = Mock()
        response.result.content = [Mock(text="Result text")]
        result = parse_function_response(response)
        assert result == "Result text"

    def test_parse_dict_content(self):
        """Test parsing dict content."""
        response = {"content": [{"text": "Dict text"}]}
        result = parse_function_response(response)
        assert result == "Dict text"
        response2 = {"data": "value"}
        result2 = parse_function_response(response2)
        assert isinstance(result2, str)

    def test_parse_fallback_to_string(self):
        """Test fallback to string."""
        response = "simple string"
        result = parse_function_response(response)
        assert result == "simple string"


class TestParseLLMResponseWithTools:
    """Test parse_llm_response_with_tools()."""

    def test_parse_with_tool_calls(self):
        """Test parsing response with tool_calls."""
        data = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "call_1",
                        "function": {
                            "name": "search",
                            "arguments": '{"query": "test"}'
                        }
                    }]
                }
            }]
        }
        result = parse_llm_response_with_tools(data)
        assert len(result) == 1
        assert result[0]["type"] == "function_call"
        assert result[0]["args"]["query"] == "test"

    def test_parse_with_text_content(self):
        """Test parsing response with text."""
        data = {
            "choices": [{
                "message": {"content": "Text response"}
            }]
        }
        result = parse_llm_response_with_tools(data)
        assert result[0]["type"] == "text"

    def test_parse_with_function_call(self):
        """Test parsing legacy function_call."""
        data = {
            "choices": [{
                "message": {
                    "function_call": {
                        "name": "calc",
                        "arguments": '{"expr": "2+2"}'
                    }
                }
            }]
        }
        result = parse_llm_response_with_tools(data)
        assert result[0]["type"] == "function_call"

    def test_parse_empty_response(self):
        """Test empty response."""
        assert parse_llm_response_with_tools({}) == []


class TestProcessSessionEvents:
    """Test process_session_events()."""

    def test_process_events_with_text(self):
        """Test processing events with text."""
        event = Mock()
        event.author = "user"
        event.content = Mock()
        event.content.parts = [Mock(text="Hi", function_call=None,
                                   function_response=None)]
        result = process_session_events([event])
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hi"

    def test_process_empty_events(self):
        """Test empty events."""
        assert process_session_events([]) == []


class TestProcessContentParts:
    """Test process_content_parts()."""

    def test_process_text_part(self):
        """Test processing content with text."""
        content = Mock()
        content.role = "user"
        content.parts = [Mock(text="Hi", function_call=None,
                             function_response=None)]
        result = process_content_parts(content)
        assert result[0]["role"] == "user"

    def test_process_function_call_part(self):
        """Test processing function_call."""
        content = Mock()
        content.role = "assistant"
        part = Mock(text=None, function_response=None)
        part.function_call = Mock(id="call_1", name="calc", args={"x": 5})
        content.parts = [part]
        result = process_content_parts(content)
        assert "tool_calls" in result[0]


class TestBuildMessagesFromRequest:
    """Test build_messages_from_request()."""

    def test_build_with_system_instruction(self):
        """Test building with system instruction."""
        llm_request = Mock()
        llm_request.config = Mock(system_instruction="You are helpful")
        llm_request.contents = []
        llm_request._invocation_context = None
        result = build_messages_from_request(llm_request)
        assert result[0]["role"] == "system"

    def test_build_with_contents(self):
        """Test building from request contents."""
        llm_request = Mock()
        llm_request.config = None
        llm_request._invocation_context = None
        content = Mock()
        content.role = "user"
        content.parts = [Mock(text="Hi", function_call=None,
                             function_response=None)]
        llm_request.contents = [content]
        result = build_messages_from_request(llm_request)
        assert any(m["role"] == "user" for m in result)

    def test_build_empty_request(self):
        """Test empty request."""
        llm_request = Mock()
        llm_request.config = None
        llm_request.contents = []
        llm_request._invocation_context = None
        result = build_messages_from_request(llm_request)
        assert isinstance(result, list)

