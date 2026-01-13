"""Tests for Strands LLM Utilities (flotorch/strands/utils/strands_utils.py)."""

import json
from unittest.mock import Mock

from flotorch.strands.utils.strands_utils import (
    convert_strands_messages_to_flotorch,
    convert_strands_tools_to_flotorch,
    convert_flotorch_response_to_strands_stream,
    extract_tool_calls_from_flotorch_response,
    create_strands_tool_result,
    log_strands_integration
)


class TestConvertStrandsMessagesToFlotorch:
    """Test convert_strands_messages_to_flotorch()."""

    def test_simple_text_message(self):
        """Test converting simple text message."""
        messages = [
            {"role": "user", "content": [{"text": "Hello, world!"}]}
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello, world!"

    def test_multiple_messages(self):
        """Test converting multiple messages."""
        messages = [
            {"role": "user", "content": [{"text": "First message"}]},
            {"role": "assistant", "content": [{"text": "Response"}]},
            {"role": "user", "content": [{"text": "Second message"}]}
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert len(result) == 3
        assert result[0]["content"] == "First message"
        assert result[1]["content"] == "Response"
        assert result[2]["content"] == "Second message"

    def test_message_with_multiple_text_blocks(self):
        """Test message with multiple content blocks."""
        messages = [
            {"role": "user", "content": [{"text": "Part 1 "}, {"text": "Part 2"}]}
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert len(result) == 1
        assert result[0]["content"] == "Part 1 Part 2"

    def test_message_with_tool_use(self):
        """Test message with tool use block."""
        messages = [
            {
                "role": "assistant",
                "content": [{
                    "toolUse": {
                        "name": "multiply",
                        "input": {"a": 5, "b": 3}
                    }
                }]
            }
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert len(result) == 1
        assert "multiply" in result[0]["content"]
        assert '{"a": 5, "b": 3}' in result[0]["content"]

    def test_message_with_tool_result(self):
        """Test message with tool result block."""
        messages = [
            {
                "role": "user",
                "content": [{
                    "toolResult": {
                        "toolUseId": "123",
                        "content": "15"
                    }
                }]
            }
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert len(result) == 1
        assert "Tool Result" in result[0]["content"]
        assert "15" in result[0]["content"]

    def test_empty_messages(self):
        """Test converting empty message list."""
        messages = []
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert result == []

    def test_message_with_empty_content(self):
        """Test message with empty content is skipped."""
        messages = [
            {"role": "user", "content": []}
        ]
        
        result = convert_strands_messages_to_flotorch(messages)
        
        assert result == []


class TestConvertStrandsToolsToFlotorch:
    """Test convert_strands_tools_to_flotorch()."""

    def test_simple_tool(self):
        """Test converting simple tool specification."""
        tool_specs = [{
            "name": "multiply",
            "description": "Multiply two numbers",
            "inputSchema": {
                "json": {
                    "properties": {
                        "a": {"type": "integer"},
                        "b": {"type": "integer"}
                    },
                    "required": ["a", "b"],
                    "type": "object"
                }
            }
        }]
        
        result = convert_strands_tools_to_flotorch(tool_specs)
        
        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "multiply"
        assert result[0]["function"]["description"] == "Multiply two numbers"
        assert "parameters" in result[0]["function"]

    def test_multiple_tools(self):
        """Test converting multiple tool specifications."""
        tool_specs = [
            {
                "name": "add",
                "description": "Add numbers",
                "inputSchema": {"json": {"properties": {}, "type": "object"}}
            },
            {
                "name": "multiply",
                "description": "Multiply numbers",
                "inputSchema": {"json": {"properties": {}, "type": "object"}}
            }
        ]
        
        result = convert_strands_tools_to_flotorch(tool_specs)
        
        assert len(result) == 2
        assert result[0]["function"]["name"] == "add"
        assert result[1]["function"]["name"] == "multiply"

    def test_tool_without_description(self):
        """Test tool without description defaults to empty string."""
        tool_specs = [{
            "name": "test_tool",
            "inputSchema": {"json": {"properties": {}, "type": "object"}}
        }]
        
        result = convert_strands_tools_to_flotorch(tool_specs)
        
        assert result[0]["function"]["description"] == ""

    def test_empty_tool_list(self):
        """Test converting empty tool list."""
        tool_specs = []
        
        result = convert_strands_tools_to_flotorch(tool_specs)
        
        assert result == []


class TestConvertFlotorchResponseToStrandsStream:
    """Test convert_flotorch_response_to_strands_stream()."""

    def test_text_response(self):
        """Test converting simple text response."""
        flotorch_response = Mock()
        flotorch_response.content = "Hello, world!"
        flotorch_response.metadata = {"raw_response": {}}
        
        result = convert_flotorch_response_to_strands_stream(flotorch_response)
        
        assert len(result) > 0
        assert result[0] == {"messageStart": {"role": "assistant"}}
        assert "messageStop" in result[-1]

    def test_response_with_tool_calls(self):
        """Test converting response with tool calls."""
        flotorch_response = Mock()
        flotorch_response.content = ""
        flotorch_response.metadata = {
            "raw_response": {
                "choices": [{
                    "message": {
                        "tool_calls": [{
                            "id": "call_123",
                            "function": {
                                "name": "multiply",
                                "arguments": '{"a": 5, "b": 3}'
                            }
                        }]
                    }
                }]
            }
        }
        
        result = convert_flotorch_response_to_strands_stream(flotorch_response)
        
        assert len(result) > 0
        # Should contain tool use event
        tool_events = [e for e in result if "contentBlockStart" in e]
        assert len(tool_events) > 0


class TestExtractToolCallsFromFlotorchResponse:
    """Test extract_tool_calls_from_flotorch_response()."""

    def test_extract_single_tool_call(self):
        """Test extracting single tool call."""
        metadata = {
            "raw_response": {
                "choices": [{
                    "message": {
                        "tool_calls": [{
                            "id": "call_1",
                            "function": {
                                "name": "add",
                                "arguments": '{"a": 10, "b": 20}'
                            }
                        }]
                    }
                }]
            }
        }
        content = ""
        response = Mock(metadata=metadata, content=content)
        
        result = extract_tool_calls_from_flotorch_response(response)
        
        assert len(result) == 1
        assert result[0]["toolUseId"] == "call_1"
        assert result[0]["name"] == "add"
        assert result[0]["input"] == {"a": 10, "b": 20}

    def test_extract_multiple_tool_calls(self):
        """Test extracting multiple tool calls."""
        metadata = {
            "raw_response": {
                "choices": [{
                    "message": {
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "function": {"name": "add", "arguments": '{"a": 1, "b": 2}'}
                            },
                            {
                                "id": "call_2",
                                "function": {"name": "multiply", "arguments": '{"a": 3, "b": 4}'}
                            }
                        ]
                    }
                }]
            }
        }
        content = ""
        response = Mock(metadata=metadata, content=content)
        
        result = extract_tool_calls_from_flotorch_response(response)
        
        assert len(result) == 2
        assert result[0]["name"] == "add"
        assert result[1]["name"] == "multiply"

    def test_no_tool_calls(self):
        """Test response without tool calls."""
        metadata = {"raw_response": {}}
        content = "Simple text"
        response = Mock(metadata=metadata, content=content)
        
        result = extract_tool_calls_from_flotorch_response(response)
        
        assert result == []

    def test_invalid_json_arguments(self):
        """Test handling invalid JSON in tool arguments."""
        metadata = {
            "raw_response": {
                "choices": [{
                    "message": {
                        "tool_calls": [{
                            "id": "call_1",
                            "function": {
                                "name": "test",
                                "arguments": "invalid json"
                            }
                        }]
                    }
                }]
            }
        }
        content = ""
        response = Mock(metadata=metadata, content=content)
        
        result = extract_tool_calls_from_flotorch_response(response)
        
        assert isinstance(result, list)


class TestCreateStrandsToolResult:
    """Test create_strands_tool_result()."""

    def test_create_simple_tool_result(self):
        """Test creating simple tool result."""
        result = create_strands_tool_result("tool_123", "Result content")
        
        assert "toolResult" in result
        assert result["toolResult"]["toolUseId"] == "tool_123"
        assert result["toolResult"]["content"] == "Result content"

    def test_create_tool_result_with_dict_content(self):
        """Test creating tool result with dict content."""
        dict_result = {"data": [1, 2, 3], "status": "success"}
        
        result = create_strands_tool_result("tool_456", dict_result)
        
        assert result["toolResult"]["toolUseId"] == "tool_456"
        assert result["toolResult"]["content"] == dict_result


class TestLogStrandsIntegration:
    """Test log_strands_integration()."""

    def test_log_with_info_level(self):
        """Test logging with info level."""
        log_strands_integration("Test message", level="info")

    def test_log_with_default_level(self):
        """Test logging with default level."""
        log_strands_integration("Default message")

