"""Test cases for FlotorchMemoryStorage class.

This module contains comprehensive unit tests for the FlotorchMemoryStorage
class, covering initialization, save, search, and reset operations.
"""

import pytest
from unittest.mock import patch

from flotorch.crewai.tests.test_data.memory_test_data import (
    SAVE_TEST_DATA,
    SEARCH_TEST_DATA,
    RESET_TEST_DATA
)


class TestMemoryStorageInit:
    """Test initialization of FlotorchMemoryStorage."""

    @patch('flotorch.crewai.memory.FlotorchMemory')
    def test_init_with_all_parameters(self, mock_memory):
        """Test initialization with all custom parameters."""
        from flotorch.crewai.memory import FlotorchMemoryStorage
        
        instance = FlotorchMemoryStorage(
            name="custom_memory",
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            user_id="user_123",
            app_id="app_456"
        )
        
        assert instance._name == "custom_memory"
        assert instance._api_key == "custom-key"
        assert instance._base_url == "https://custom.flotorch.com"
        assert instance._user_id == "user_123"
        assert instance._app_id == "app_456"
        assert instance._collection_name == "user_123_custom_memory"
        
        mock_memory.assert_called_once_with(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_memory"
        )

    @patch('flotorch.crewai.memory.FlotorchMemory')
    def test_init_with_default_ids(self, mock_memory):
        """Test initialization uses default user and app IDs."""
        from flotorch.crewai.memory import FlotorchMemoryStorage
        
        instance = FlotorchMemoryStorage(
            name="test_memory",
            api_key="test-key",
            base_url="https://test.flotorch.com"
        )
        
        assert instance._user_id == "default_user"
        assert instance._app_id == "default_app"
        assert instance._collection_name == "default_user_test_memory"

    @patch('flotorch.crewai.memory.FlotorchMemory')
    def test_init_raises_error_without_base_url(self, mock_memory):
        """Test initialization raises ValueError without base_url."""
        from flotorch.crewai.memory import FlotorchMemoryStorage
        
        with pytest.raises(ValueError, match="base_url parameter is required"):
            FlotorchMemoryStorage(name="test", api_key="key")

    @patch('flotorch.crewai.memory.FlotorchMemory')
    def test_init_raises_error_without_api_key(self, mock_memory):
        """Test initialization raises ValueError without api_key."""
        from flotorch.crewai.memory import FlotorchMemoryStorage
        
        with pytest.raises(ValueError, match="api_key parameter is required"):
            FlotorchMemoryStorage(name="test", base_url="https://test.com")


class TestMemoryStorageSave:
    """Test save functionality of FlotorchMemoryStorage."""

    @pytest.mark.parametrize(
        "test_name,value,metadata,should_fail,expected_exception",
        SAVE_TEST_DATA
    )
    def test_save_with_various_scenarios(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        value,
        metadata,
        should_fail,
        expected_exception
    ):
        """Test save with parametrized scenarios."""
        if should_fail:
            mock_memory_client.add.side_effect = Exception("API Error")
            with pytest.raises(expected_exception, match="Failed to save"):
                memory_instance.save(value, metadata)
        else:
            memory_instance.save(value, metadata)
            
            has_content = value or (metadata and metadata.get("messages"))
            if has_content:
                mock_memory_client.add.assert_called_once()

    def test_save_extracts_final_answer_content(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save correctly extracts Final Answer content."""
        value = "Thought: thinking\nFinal Answer: The result is 42"
        metadata = {"messages": [{"role": "user", "content": "Query"}]}
        
        memory_instance.save(value, metadata)
        
        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]
        assistant_msg = [m for m in messages if m["role"] == "assistant"][0]
        
        assert assistant_msg["content"] == "The result is 42"

    def test_save_uses_plain_value_without_marker(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save uses full value when no Final Answer marker."""
        value = "Plain response"
        metadata = {"messages": [{"role": "user", "content": "Query"}]}
        
        memory_instance.save(value, metadata)
        
        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]
        assistant_msg = [m for m in messages if m["role"] == "assistant"][0]
        
        assert assistant_msg["content"] == "Plain response"

    def test_save_extracts_last_user_message(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save extracts the last user message from metadata."""
        value = "Response"
        metadata = {
            "messages": [
                {"role": "user", "content": "First query"},
                {"role": "assistant", "content": "First response"},
                {"role": "user", "content": "Second query"}
            ]
        }
        
        memory_instance.save(value, metadata)
        
        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]
        user_msg = [m for m in messages if m["role"] == "user"][0]
        
        assert user_msg["content"] == "Second query"

    def test_save_uses_custom_user_and_app_ids(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save uses custom user_id and app_id from metadata."""
        value = "Response"
        metadata = {
            "crewai_user_id": "custom_user",
            "crewai_app_id": "custom_app",
            "messages": [{"role": "user", "content": "Query"}]
        }
        
        memory_instance.save(value, metadata)
        
        call_args = mock_memory_client.add.call_args
        
        assert call_args.kwargs["userId"] == "custom_user"
        assert call_args.kwargs["appId"] == "custom_app"

    def test_save_creates_combined_metadata(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save creates proper combined metadata."""
        value = "Response"
        metadata = {
            "custom": "value",
            "messages": [{"role": "user", "content": "Query"}]
        }
        
        memory_instance.save(value, metadata)
        
        call_args = mock_memory_client.add.call_args
        combined = call_args.kwargs["metadata"]
        
        assert combined["source"] == "crewai"
        assert combined["collection"] == "test_user_test_memory"
        assert "timestamp" in combined
        assert combined["custom"] == "value"

    def test_save_skips_empty_content(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test save skips when no meaningful content exists."""
        memory_instance.save("", {})
        
        mock_memory_client.add.assert_not_called()


class TestMemoryStorageSearch:
    """Test search functionality of FlotorchMemoryStorage."""

    @pytest.mark.parametrize(
        "test_name,query,limit,api_response,expected_count,should_fail,"
        "expected_exception",
        SEARCH_TEST_DATA
    )
    def test_search_with_various_scenarios(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        query,
        limit,
        api_response,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test search with parametrized scenarios."""
        if should_fail:
            mock_memory_client.search.side_effect = Exception("API Error")
            with pytest.raises(expected_exception, match="Failed to search"):
                memory_instance.search(query, limit)
        else:
            mock_memory_client.search.return_value = api_response
            results = memory_instance.search(query, limit)
            
            assert len(results) == expected_count
            
            if expected_count > 0:
                for result in results:
                    assert "memory" in result
                    assert "metadata" in result
                    assert "content" in result

    def test_search_calls_api_with_correct_params(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search calls API with correct parameters."""
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.search("test query", 10)
        
        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            sessionId=None,
            query="test query",
            limit=10
        )

    def test_search_adds_default_metadata_fields(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search adds default suggestions and quality fields."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "Content", "metadata": {}}
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert len(results) == 1
        assert "suggestions" in results[0]["metadata"]
        assert "quality" in results[0]["metadata"]
        assert results[0]["metadata"]["suggestions"] == []
        assert results[0]["metadata"]["quality"] == 0.5

    def test_search_preserves_existing_metadata_values(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search preserves existing suggestions and quality values."""
        mock_memory_client.search.return_value = {
            "data": [
                {
                    "id": "mem-1",
                    "memory": "Content",
                    "metadata": {
                        "suggestions": ["test"],
                        "quality": 0.9,
                        "custom": "value"
                    }
                }
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert results[0]["metadata"]["suggestions"] == ["test"]
        assert results[0]["metadata"]["quality"] == 0.9
        assert results[0]["metadata"]["custom"] == "value"

    def test_search_converts_non_dict_metadata(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search converts non-dict metadata to dict."""
        mock_memory_client.search.return_value = {
            "data": [
                {
                    "id": "mem-1",
                    "memory": "Content",
                    "metadata": "not a dict"
                }
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert isinstance(results[0]["metadata"], dict)
        assert "suggestions" in results[0]["metadata"]
        assert "quality" in results[0]["metadata"]

    def test_search_adds_content_field_for_compatibility(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search adds content field for CrewAI compatibility."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "Test content", "metadata": {}}
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert results[0]["content"] == "Test content"
        assert results[0]["memory"] == "Test content"

    def test_search_field_priority_order(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search prioritizes memory > content > text fields."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "from memory", "metadata": {}},
                {"id": "mem-2", "content": "from content", "metadata": {}},
                {"id": "mem-3", "text": "from text", "metadata": {}}
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert results[0]["memory"] == "from memory"
        assert results[1]["memory"] == "from content"
        assert results[2]["memory"] == "from text"

    def test_search_skips_items_without_content(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test search skips items with no extractable content."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "Valid", "metadata": {}},
                {"id": "mem-2", "metadata": {}},
                {"id": "mem-3", "other_field": "data"}
            ]
        }
        
        results = memory_instance.search("query", 5)
        
        assert len(results) == 1
        assert results[0]["memory"] == "Valid"


class TestMemoryStorageReset:
    """Test reset functionality of FlotorchMemoryStorage."""

    @pytest.mark.parametrize(
        "test_name,search_response,expected_deletes,should_fail,"
        "expected_exception",
        RESET_TEST_DATA
    )
    def test_reset_with_various_scenarios(
        self,
        memory_instance,
        mock_memory_client,
        test_name,
        search_response,
        expected_deletes,
        should_fail,
        expected_exception
    ):
        """Test reset with parametrized scenarios."""
        if should_fail:
            mock_memory_client.search.side_effect = Exception("API Error")
            with pytest.raises(expected_exception, match="Failed to reset"):
                memory_instance.reset()
        else:
            mock_memory_client.search.return_value = search_response
            
            memory_instance.reset()
            
            assert mock_memory_client.delete.call_count == expected_deletes

    def test_reset_searches_with_wildcard(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test reset searches with wildcard query."""
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.reset()
        
        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            sessionId=None,
            query="*",
            limit=30
        )

    def test_reset_deletes_all_found_memories(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test reset deletes all memories returned by search."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "Memory 1"},
                {"id": "mem-2", "memory": "Memory 2"},
                {"id": "mem-3", "memory": "Memory 3"}
            ]
        }
        
        memory_instance.reset()
        
        assert mock_memory_client.delete.call_count == 3
        mock_memory_client.delete.assert_any_call("mem-1")
        mock_memory_client.delete.assert_any_call("mem-2")
        mock_memory_client.delete.assert_any_call("mem-3")

    def test_reset_with_empty_memories(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test reset when no memories exist."""
        mock_memory_client.search.return_value = {"data": []}
        
        memory_instance.reset()
        
        mock_memory_client.search.assert_called_once()
        mock_memory_client.delete.assert_not_called()

    def test_reset_skips_memories_without_id(
        self,
        memory_instance,
        mock_memory_client
    ):
        """Test reset skips memories without id field."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "memory": "Has ID"},
                {"memory": "No ID"},
                {"id": "mem-2", "memory": "Has ID"}
            ]
        }
        
        memory_instance.reset()
        
        assert mock_memory_client.delete.call_count == 2
        mock_memory_client.delete.assert_any_call("mem-1")
        mock_memory_client.delete.assert_any_call("mem-2")
