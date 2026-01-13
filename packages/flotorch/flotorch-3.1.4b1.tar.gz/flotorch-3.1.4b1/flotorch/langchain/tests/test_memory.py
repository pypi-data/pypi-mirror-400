"""Test cases for FlotorchLangChainMemory class."""

import pytest
from unittest.mock import patch

from flotorch.langchain.tests.test_data.memory_test_data import (
    LOAD_MEMORY_TEST_DATA,
    SAVE_CONTEXT_TEST_DATA,
    CLEAR_TEST_DATA,
    BUILD_HISTORY_TEST_DATA,
)


class TestFlotorchLangChainMemoryInit:
    """Test initialization."""

    @patch('flotorch.langchain.memory.FlotorchMemory')
    def test_init_all_parameters(self, mock_memory):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        instance = FlotorchLangChainMemory(
            name="custom_memory",
            api_key="key-123",
            base_url="https://test.cloud",
            user_id="user_123",
            app_id="app_456"
        )
        
        assert instance.name == "custom_memory"
        assert instance.api_key == "key-123"
        assert instance.base_url == "https://test.cloud"
        assert instance.user_id == "user_123"
        assert instance.app_id == "app_456"
        assert instance.memory_key == "longterm_history"
        
        mock_memory.assert_called_once_with(
            api_key="key-123",
            base_url="https://test.cloud",
            provider_name="custom_memory"
        )

    @patch('flotorch.langchain.memory.FlotorchMemory')
    def test_init_minimal_parameters(self, mock_memory):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        instance = FlotorchLangChainMemory(
            name="memory",
            api_key="key",
            base_url="https://test.cloud"
        )
        
        assert instance.name == "memory"
        assert instance.memory_key == "longterm_history"


class TestFlotorchLangChainMemoryMemoryVariables:
    """Test memory_variables property."""

    def test_memory_variables(self, memory_instance):
        assert memory_instance.memory_variables == ["longterm_history"]


class TestFlotorchLangChainMemoryLoadMemoryVariables:
    """Test load_memory_variables."""

    @pytest.mark.parametrize(
        "test_name,inputs,api_response,expected",
        LOAD_MEMORY_TEST_DATA
    )
    def test_load_memory_parametrized(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        inputs,
        api_response,
        expected,
        capsys
    ):
        mock_memory_client.search.return_value = api_response
        
        result = memory_instance.load_memory_variables(inputs)
        
        assert result == {"longterm_history": expected}

    def test_load_memory_calls_api_correctly(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.load_memory_variables({"input": "test query"})
        
        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            limit=50,
            query="test query"
        )

    def test_load_memory_extracts_query_from_first_value(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.load_memory_variables({"custom_key": "query text"})
        
        call_args = mock_memory_client.search.call_args
        assert call_args.kwargs["query"] == "query text"

    def test_load_memory_handles_errors(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.side_effect = Exception("API Error")
        
        result = memory_instance.load_memory_variables({"input": "Test"})
        
        assert result == {"longterm_history": ""}


class TestFlotorchLangChainMemorySaveContext:
    """Test save_context."""

    @pytest.mark.parametrize(
        "test_name,inputs,outputs",
        SAVE_CONTEXT_TEST_DATA
    )
    def test_save_context_parametrized(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        inputs,
        outputs,
        capsys
    ):
        memory_instance.save_context(inputs, outputs)
        
        mock_memory_client.add.assert_called_once()
        call_args = mock_memory_client.add.call_args
        
        messages = call_args.kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_save_context_uses_correct_ids(
        self,
        memory_instance,
        mock_memory_client
    ):
        memory_instance.save_context(
            {"input": "Query"},
            {"output": "Response"}
        )
        
        call_args = mock_memory_client.add.call_args
        
        assert call_args.kwargs["userId"] == "test_user"
        assert call_args.kwargs["appId"] == "test_app"

    def test_save_context_extracts_response_key(
        self,
        memory_instance,
        mock_memory_client
    ):
        memory_instance.save_context(
            {"input": "Query"},
            {"response": "Custom response"}
        )
        
        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]
        
        assert messages[1]["content"] == "Custom response"

    def test_save_context_handles_errors(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.add.side_effect = Exception("API Error")
        
        memory_instance.save_context({"input": "Test"}, {"output": "Response"})


class TestFlotorchLangChainMemoryClear:
    """Test clear."""

    @pytest.mark.parametrize(
        "test_name,search_response,expected_deletes",
        CLEAR_TEST_DATA
    )
    def test_clear_parametrized(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        search_response,
        expected_deletes
    ):
        mock_memory_client.search.return_value = search_response
        
        memory_instance.clear()
        
        assert mock_memory_client.delete.call_count == expected_deletes

    def test_clear_searches_correctly(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.clear()
        
        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            limit=1000
        )

    def test_clear_deletes_all_items(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1"},
                {"id": "mem-2"},
                {"id": "mem-3"}
            ]
        }
        
        memory_instance.clear()
        
        assert mock_memory_client.delete.call_count == 3
        mock_memory_client.delete.assert_any_call("mem-1")
        mock_memory_client.delete.assert_any_call("mem-2")
        mock_memory_client.delete.assert_any_call("mem-3")

    def test_clear_handles_errors(
        self,
        memory_instance,
        mock_memory_client
    ):
        mock_memory_client.search.side_effect = Exception("API Error")
        
        memory_instance.clear()


class TestFlotorchLangChainMemoryBuildHistory:
    """Test _build_history_from_data."""

    @pytest.mark.parametrize(
        "test_name,data_items,expected",
        BUILD_HISTORY_TEST_DATA
    )
    def test_build_history_parametrized(
        self,
        test_name,
        data_items,
        expected,
        capsys
    ):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        result = FlotorchLangChainMemory._build_history_from_data(data_items)
        
        assert result == expected

    def test_build_history_priority_content_over_message(self):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        data_items = [{"content": "Content", "message": "Message"}]
        result = FlotorchLangChainMemory._build_history_from_data(data_items)
        
        assert result == "Content"

    def test_build_history_priority_message_over_text(self):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        data_items = [{"message": "Message", "text": "Text"}]
        result = FlotorchLangChainMemory._build_history_from_data(data_items)
        
        assert result == "Message"

    def test_build_history_handles_non_string_content(self):
        from flotorch.langchain.memory import FlotorchLangChainMemory
        
        data_items = [
            {"content": "Valid"},
            {"content": 123},
            {"content": None},
            {"content": "Also valid"}
        ]
        result = FlotorchLangChainMemory._build_history_from_data(data_items)
        
        assert result == "Valid\nAlso valid"

