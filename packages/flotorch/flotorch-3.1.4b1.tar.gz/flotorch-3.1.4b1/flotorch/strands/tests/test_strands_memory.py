"""Test cases for FlotorchMemoryTool class."""

import pytest
from unittest.mock import Mock, patch
from strands.types.tools import ToolResult, ToolResultContent

from flotorch.strands.tests.test_data.memory_test_data import (
    MEMORY_ADD_TEST_DATA,
    MEMORY_SEARCH_TEST_DATA,
    MEMORY_LIST_TEST_DATA,
    INVALID_ACTION_TEST_DATA,
    TOOL_RESULT_FORMAT_TEST_DATA
)


class TestMemoryToolInit:
    """Test initialization of FlotorchMemoryTool."""

    @patch('flotorch.strands.memory.FlotorchMemory')
    def test_init_with_all_parameters(self, mock_memory):
        """Test initialization with all custom parameters."""
        from flotorch.strands.memory import FlotorchMemoryTool

        tool = FlotorchMemoryTool(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_provider",
            user_id="user_123",
            app_id="app_456"
        )

        assert tool.api_key == "custom-key"
        assert tool.base_url == "https://custom.flotorch.com"
        assert tool.provider_name == "custom_provider"
        assert tool.user_id == "user_123"
        assert tool.app_id == "app_456"

        mock_memory.assert_called_once_with(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_provider"
        )

    @patch('flotorch.strands.memory.FlotorchMemory')
    def test_init_with_default_values(self, mock_memory):
        """Test initialization with minimal required parameters."""
        from flotorch.strands.memory import FlotorchMemoryTool

        tool = FlotorchMemoryTool(
            api_key="test-key",
            base_url="https://test.flotorch.com",
            provider_name="test_provider",
            user_id="test_user",
            app_id="test_app"
        )

        assert tool.user_id == "test_user"
        assert tool.app_id == "test_app"
        mock_memory.assert_called_once()

    def test_tool_spec_structure(self):
        """Test that TOOL_SPEC has correct structure."""
        from flotorch.strands.memory import TOOL_SPEC
        
        assert TOOL_SPEC["name"] == "flotorch_memory"
        assert "description" in TOOL_SPEC
        assert "inputSchema" in TOOL_SPEC
        assert "json" in TOOL_SPEC["inputSchema"]
        
        schema = TOOL_SPEC["inputSchema"]["json"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "action" in schema["properties"]
        assert (schema["properties"]["action"]["enum"] ==
                ["add", "search", "list"])
        assert schema["required"] == ["action"]


class TestMemoryAddOperation:
    """Test ADD operation functionality."""

    @pytest.mark.parametrize(
        "test_name,tool_input,api_response,expected_text,"
        "should_fail,expected_exception",
        MEMORY_ADD_TEST_DATA
    )
    def test_add_with_various_scenarios(
        self,
        strands_memory_tool,
        mock_flotorch_memory,
        mock_tool_use,
        test_name,
        tool_input,
        api_response,
        expected_text,
        should_fail,
        expected_exception
    ):
        """Test ADD operation with parametrized scenarios."""
        if not should_fail:
            mock_flotorch_memory.add.return_value = api_response
        tool = mock_tool_use(**tool_input)
        result = strands_memory_tool._tool_func(tool)
        assert (isinstance(result, dict) and
                "toolUseId" in result and
                "status" in result and
                "content" in result)
        if should_fail:
            assert (result["status"] == "error" and
                    "Error:" in result["content"][0]["text"])
        else:
            assert (result["status"] == "success" and
                    expected_text in result["content"][0]["text"])
            mock_flotorch_memory.add.assert_called_once()
            call_kwargs = mock_flotorch_memory.add.call_args.kwargs
            assert (call_kwargs["userId"] == strands_memory_tool.user_id
                    and call_kwargs["appId"] == strands_memory_tool.app_id
                    and call_kwargs["metadata"]["source"] == "strands")

    def test_add_stores_correct_content(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test that add stores the correct content."""
        mock_flotorch_memory.add.return_value = {
            "object": "agent.memory.list",
            "data": [{"id": "test-id", "content": "Test"}]
        }
        
        tool = mock_tool_use(action="add", content="User's name is Madhu")
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "success"

        call_kwargs = mock_flotorch_memory.add.call_args.kwargs
        messages = call_kwargs["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "User's name is Madhu"


class TestMemorySearchOperation:
    """Test SEARCH operation functionality."""

    @pytest.mark.parametrize(
        "test_name,tool_input,api_response,expected_text,"
        "should_fail,expected_exception",
        MEMORY_SEARCH_TEST_DATA
    )
    def test_search_with_various_scenarios(
        self,
        strands_memory_tool,
        mock_flotorch_memory,
        mock_tool_use,
        test_name,
        tool_input,
        api_response,
        expected_text,
        should_fail,
        expected_exception
    ):
        """Test SEARCH operation with parametrized scenarios."""
        if not should_fail:
            mock_flotorch_memory.search.return_value = api_response
        
        tool = mock_tool_use(**tool_input)
        result = strands_memory_tool._tool_func(tool)

        assert isinstance(result, dict)
        assert "status" in result
        
        if should_fail:
            assert result["status"] == "error"
            assert "Error:" in result["content"][0]["text"]
        else:
            assert result["status"] == "success"
            assert expected_text == result["content"][0]["text"]
            
            mock_flotorch_memory.search.assert_called_once()
            call_kwargs = mock_flotorch_memory.search.call_args.kwargs
            assert call_kwargs["userId"] == strands_memory_tool.user_id
            assert call_kwargs["appId"] == strands_memory_tool.app_id
            assert call_kwargs["limit"] == 5

    def test_search_query_passed_correctly(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test that search query is passed correctly to SDK."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": []
        }
        
        tool = mock_tool_use(action="search", query="User's name")
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "success"

        call_kwargs = mock_flotorch_memory.search.call_args.kwargs
        assert call_kwargs["query"] == "User's name"

    def test_search_formats_multiple_results(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test that search formats multiple results correctly."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": [
                {"id": "1", "content": "First memory"},
                {"id": "2", "content": "Second memory"},
                {"id": "3", "content": "Third memory"}
            ]
        }
        
        tool = mock_tool_use(action="search", query="test")
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "success"
        response_text = result["content"][0]["text"]
        assert "Found 3 relevant memories:" in response_text
        assert "1. First memory" in response_text
        assert "2. Second memory" in response_text
        assert "3. Third memory" in response_text


class TestMemoryListOperation:
    """Test LIST operation functionality."""

    @pytest.mark.parametrize(
        "test_name,tool_input,api_response,expected_text,"
        "should_fail,expected_exception",
        MEMORY_LIST_TEST_DATA
    )
    def test_list_with_various_scenarios(
        self,
        strands_memory_tool,
        mock_flotorch_memory,
        mock_tool_use,
        test_name,
        tool_input,
        api_response,
        expected_text,
        should_fail,
        expected_exception
    ):
        """Test LIST operation with parametrized scenarios."""
        if not should_fail:
            mock_flotorch_memory.search.return_value = api_response
        
        tool = mock_tool_use(**tool_input)
        result = strands_memory_tool._tool_func(tool)

        assert isinstance(result, dict)
        assert "status" in result
        
        if should_fail:
            assert result["status"] == "error"
        else:
            assert result["status"] == "success"
            assert expected_text == result["content"][0]["text"]

    def test_list_uses_wildcard_query(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test that list uses wildcard query to get all memories."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": []
        }
        
        tool = mock_tool_use(action="list")
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "success"

        call_kwargs = mock_flotorch_memory.search.call_args.kwargs
        assert call_kwargs["query"] == "*"
        assert call_kwargs["limit"] == 20

    def test_list_formats_with_ids(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test that list formats memories with IDs."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": [
                {"id": "mem-123", "content": "Memory content 1"},
                {"id": "mem-456", "content": "Memory content 2"}
            ]
        }
        
        tool = mock_tool_use(action="list")
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "success"
        response_text = result["content"][0]["text"]
        assert "Total memories: 2" in response_text
        assert "[mem-123]" in response_text
        assert "[mem-456]" in response_text


class TestInvalidActions:
    """Test invalid action handling."""
    
    @pytest.mark.parametrize(
        "test_name,tool_input,api_response,expected_text,"
        "should_fail,expected_exception",
        INVALID_ACTION_TEST_DATA
    )
    def test_invalid_actions(
        self,
        strands_memory_tool,
        mock_tool_use,
        test_name,
        tool_input,
        api_response,
        expected_text,
        should_fail,
        expected_exception
    ):
        """Test handling of invalid actions using test data."""

        if not tool_input:
            tool = {
                "toolUseId": "test-tool-use-id",
                "name": "flotorch_memory",
                "input": {}
            }
        else:
            tool = mock_tool_use(**tool_input)
        
        result = strands_memory_tool._tool_func(tool)
        
        assert result["status"] == "error"
        assert expected_text == result["content"][0]["text"]


class TestToolResultFormat:
    """Test ToolResult format compliance."""

    @pytest.mark.parametrize(
        "test_name,expected_result,expected_status,expected_text",
        TOOL_RESULT_FORMAT_TEST_DATA
    )
    def test_result_format_structure(
        self,
        strands_memory_tool,
        mock_flotorch_memory,
        mock_tool_use,
        test_name,
        expected_result,
        expected_status,
        expected_text
    ):
        """Test that results follow ToolResult format structure."""
        if expected_status == "success":
            mock_flotorch_memory.add.return_value = {
                "object": "agent.memory.list",
                "data": [{"id": "test-id", "content": "Test"}]
            }
            tool = mock_tool_use(
                tool_use_id=expected_result["toolUseId"],
                action="add",
                content="test content"
            )
        else:
            tool = mock_tool_use(
                tool_use_id=expected_result["toolUseId"],
                action="add"
            )
        
        result = strands_memory_tool._tool_func(tool)

        assert result["toolUseId"] == expected_result["toolUseId"]
        assert result["status"] == expected_status
        assert (isinstance(result["content"], list) and
                len(result["content"]) == 1 and
                "text" in result["content"][0])
        
        if expected_status == "success":
            assert expected_text in result["content"][0]["text"]
        else:
            assert "Error:" in result["content"][0]["text"]

    def test_default_tool_use_id(
        self, strands_memory_tool, mock_flotorch_memory
    ):
        """Test default toolUseId when not provided."""
        mock_flotorch_memory.add.return_value = {
            "object": "agent.memory.list",
            "data": [{"id": "test-id", "content": "Test"}]
        }
        
        tool = {
            "name": "flotorch_memory",
            "input": {"action": "add", "content": "Test"}
        }
        result = strands_memory_tool._tool_func(tool)
        
        assert result["toolUseId"] == "default-id"
        assert result["status"] == "success"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_api_failure_handling(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test API failures are handled gracefully."""
        mock_flotorch_memory.add.side_effect = Exception("API Error")
        result = strands_memory_tool._tool_func(
            mock_tool_use(action="add", content="test")
        )
        assert (result["status"] == "error" and
                "Error:" in result["content"][0]["text"])

    def test_unicode_content(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test Unicode content handling."""
        mock_flotorch_memory.add.return_value = {
            "object": "agent.memory.list",
            "data": [{"id": "test", "content": "Test"}]
        }
        unicode_content = "User name is Madhu"
        result = strands_memory_tool._tool_func(
            mock_tool_use(action="add", content=unicode_content)
        )
        assert result["status"] == "success"
        assert (mock_flotorch_memory.add.call_args.kwargs["messages"][0]
                ["content"] == unicode_content)

    def test_long_content_truncation(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test list truncates long content correctly."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": [{"id": "mem-123", "content": "A" * 150}]
        }
        result = strands_memory_tool._tool_func(
            mock_tool_use(action="list")
        )
        assert "A" * 100 + "..." in result["content"][0]["text"]

    def test_memory_field_handling(
        self, strands_memory_tool, mock_flotorch_memory, mock_tool_use
    ):
        """Test both 'memory' and 'content' fields handled."""
        mock_flotorch_memory.search.return_value = {
            "object": "agent.memory.list",
            "data": [
                {"id": "1", "memory": "From memory"},
                {"id": "2", "content": "From content"}
            ]
        }
        result = strands_memory_tool._tool_func(
            mock_tool_use(action="search", query="test")
        )
        assert ("From memory" in result["content"][0]["text"] and
                "From content" in result["content"][0]["text"])


class TestGlobalConfigAndIntegration:
    """Test global config and Strands integration."""

    def test_global_config_update(
        self, memory_test_data, mock_flotorch_memory
    ):
        """Test global config updated on tool call."""
        from flotorch.strands.memory import FlotorchMemoryTool, _config
        
        with patch('flotorch.strands.memory.FlotorchMemory',
                   return_value=mock_flotorch_memory):
            tool = FlotorchMemoryTool(**memory_test_data)
            mock_flotorch_memory.add.return_value = {
                "object": "agent.memory.list",
                "data": [{"id": "test", "content": "test"}]
            }
            tool._tool_func({
                "toolUseId": "test-id",
                "name": "flotorch_memory",
                "input": {"action": "add", "content": "test"}
            })
            
            assert _config["user_id"] == memory_test_data["user_id"]
            assert _config["app_id"] == memory_test_data["app_id"]

    def test_strands_integration(self, strands_memory_tool):
        """Test Strands Agent integration."""
        from strands.tools.tools import PythonAgentTool
        
        assert isinstance(strands_memory_tool, PythonAgentTool)
        assert (strands_memory_tool._tool_spec["name"] ==
                "flotorch_memory")
        assert callable(strands_memory_tool._tool_func)

