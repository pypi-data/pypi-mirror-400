"""Test cases for FlotorchAutogenMemory class.

This module contains comprehensive unit tests for the FlotorchAutogenMemory
class, covering initialization, query, add, and update_context operations.
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from autogen_core.memory import MemoryContent, MemoryQueryResult, MemoryMimeType
from autogen_core.models import UserMessage, SystemMessage

from flotorch.autogen.tests.test_data.memory_test_data import (
    QUERY_TEST_DATA,
    ADD_TEST_DATA,
    UPDATE_CONTEXT_TEST_DATA,
    DEDUPLICATION_TEST_DATA
)


class TestAutogenMemoryInit:
    """Test initialization of FlotorchAutogenMemory."""

    @patch('flotorch.autogen.memory.FlotorchMemory')
    @patch('flotorch.autogen.memory.log_object_creation')
    def test_init_with_all_parameters(self, mock_log, mock_memory):
        """Test initialization with all custom parameters."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="custom_memory",
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            user_id="user_123",
            app_id="app_456",
            limit=25
        )
        
        assert instance._name == "custom_memory"
        assert instance._api_key == "custom-key"
        assert instance._base_url == "https://custom.flotorch.com"
        assert instance._user_id == "user_123"
        assert instance._app_id == "app_456"
        assert instance._limit == 25
        
        mock_memory.assert_called_once_with(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_memory"
        )
        
        mock_log.assert_called_once_with(
            "FlotorchMemoryService",
            provider_name="custom_memory",
            base_url="https://custom.flotorch.com"
        )

    @patch('flotorch.autogen.memory.FlotorchMemory')
    @patch('flotorch.autogen.memory.log_object_creation')
    def test_init_with_default_user_app_ids(self, mock_log, mock_memory):
        """Test initialization with None user and app IDs."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="test_memory",
            api_key="test-key",
            base_url="https://test.flotorch.com"
        )
        
        assert instance._user_id is None
        assert instance._app_id is None

    @patch('flotorch.autogen.memory.FlotorchMemory')
    @patch('flotorch.autogen.memory.log_object_creation')
    def test_init_with_env_variables(self, mock_log, mock_memory, monkeypatch):
        """Test initialization uses environment variables."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        monkeypatch.setenv("FLOTORCH_BASE_URL", "https://env.flotorch.com")
        monkeypatch.setenv("FLOTORCH_API_KEY", "env-api-key")
        
        instance = FlotorchAutogenMemory(name="test_memory")
        
        assert instance._base_url == "https://env.flotorch.com"
        assert instance._api_key == "env-api-key"

    @patch('flotorch.autogen.memory.FlotorchMemory')
    def test_init_raises_error_without_base_url(self, mock_memory, monkeypatch):
        """Test initialization raises ValueError without base_url."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        monkeypatch.delenv("FLOTORCH_BASE_URL", raising=False)
        
        with pytest.raises(ValueError, match="base_url parameter is required"):
            FlotorchAutogenMemory(name="test", api_key="key")

    @patch('flotorch.autogen.memory.FlotorchMemory')
    def test_init_raises_error_without_api_key(self, mock_memory, monkeypatch):
        """Test initialization raises ValueError without api_key."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="api_key parameter is required"):
            FlotorchAutogenMemory(name="test", base_url="https://test.com")

    @patch('flotorch.autogen.memory.FlotorchMemory')
    @patch('flotorch.autogen.memory.log_object_creation')
    def test_init_sets_default_limit(self, mock_log, mock_memory):
        """Test initialization sets default limit to 50."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="test_memory",
            api_key="test-key",
            base_url="https://test.flotorch.com"
        )
        
        assert instance._limit == 50

    @patch('flotorch.autogen.memory.FlotorchMemory')
    @patch('flotorch.autogen.memory.log_object_creation')
    def test_init_initializes_deduplication_state(self, mock_log, mock_memory):
        """Test initialization sets deduplication tracking to None."""
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="test_memory",
            api_key="test-key",
            base_url="https://test.flotorch.com"
        )
        
        assert instance._last_query is None
        assert instance._last_results_hash is None


class TestAutogenMemoryQuery:
    """Test query functionality of FlotorchAutogenMemory."""

    @pytest.mark.parametrize(
        "test_name,query_input,api_response,expected_count,should_fail,expected_exception",
        QUERY_TEST_DATA
    )
    @pytest.mark.asyncio
    async def test_query_with_various_scenarios(
        self,
        autogen_memory_instance,
        mock_memory_client,
        test_name,
        query_input,
        api_response,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test query with parametrized scenarios."""
        if should_fail:
            mock_memory_client.search.side_effect = Exception("API Error")
            with pytest.raises(expected_exception):
                await autogen_memory_instance.query(query_input)
        else:
            mock_memory_client.search.return_value = api_response
            result = await autogen_memory_instance.query(query_input)
            
            assert isinstance(result, MemoryQueryResult)
            assert len(result.results) == expected_count

    @pytest.mark.asyncio
    async def test_query_with_string_input(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query accepts string input."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test memory"}]
        }
        
        result = await autogen_memory_instance.query("test query")
        
        assert isinstance(result, MemoryQueryResult)
        assert len(result.results) == 1
        assert result.results[0].content == "Test memory"

    @pytest.mark.asyncio
    async def test_query_with_memory_content_input(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query accepts MemoryContent input."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test memory"}]
        }
        
        query_content = MemoryContent(
            content="test query",
            mime_type=MemoryMimeType.TEXT
        )
        
        result = await autogen_memory_instance.query(query_content)
        
        assert isinstance(result, MemoryQueryResult)
        mock_memory_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_with_object_having_content_attr(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_memory_content_with_content_attr
    ):
        """Test query extracts content from object with content attribute."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test memory"}]
        }
        
        result = await autogen_memory_instance.query(mock_memory_content_with_content_attr)
        
        assert isinstance(result, MemoryQueryResult)
        call_args = mock_memory_client.search.call_args
        assert "Query from content attribute" in str(call_args.kwargs["query"])

    @pytest.mark.asyncio
    async def test_query_calls_api_with_correct_params(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query calls API with correct parameters."""
        mock_memory_client.search.return_value = {"data": []}
        
        await autogen_memory_instance.query("test query")
        
        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            query="test query",
            page=1,
            limit=10
        )

    @pytest.mark.asyncio
    async def test_query_with_none_user_app_ids(
        self,
        autogen_memory_instance_with_none_ids,
        mock_memory_client
    ):
        """Test query passes None for user_id and app_id when not set."""
        mock_memory_client.search.return_value = {"data": []}
        
        await autogen_memory_instance_with_none_ids.query("test")
        
        call_args = mock_memory_client.search.call_args
        assert call_args.kwargs["userId"] is None
        assert call_args.kwargs["appId"] is None

    @pytest.mark.asyncio
    async def test_query_returns_memory_query_result(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query returns MemoryQueryResult type."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test"}]
        }
        
        result = await autogen_memory_instance.query("test")
        
        assert isinstance(result, MemoryQueryResult)
        assert hasattr(result, "results")
        assert isinstance(result.results, list)

    @pytest.mark.asyncio
    async def test_query_returns_no_memories_found_message(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query returns 'No memories found' when empty."""
        mock_memory_client.search.return_value = {"data": []}
        
        result = await autogen_memory_instance.query("test")
        
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_query_converts_api_response_to_memory_content(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query converts API response to MemoryContent objects."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "content": "Memory 1"},
                {"id": "mem-2", "content": "Memory 2"}
            ]
        }
        
        result = await autogen_memory_instance.query("test")
        
        assert len(result.results) == 2
        for memory in result.results:
            assert isinstance(memory, MemoryContent)
            assert memory.mime_type == MemoryMimeType.TEXT

    @pytest.mark.asyncio
    async def test_query_skips_memories_without_content(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query skips memories without content field."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "content": "Valid"},
                {"id": "mem-2", "other_field": "No content"},
                {"id": "mem-3", "content": ""},
                {"id": "mem-4", "content": "Also valid"}
            ]
        }
        
        result = await autogen_memory_instance.query("test")
        
        assert len(result.results) == 2
        assert result.results[0].content == "Valid"
        assert result.results[1].content == "Also valid"

    @pytest.mark.asyncio
    async def test_query_handles_api_failure(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query propagates API exceptions after logging."""
        mock_memory_client.search.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            await autogen_memory_instance.query("test")

    @pytest.mark.asyncio
    async def test_query_uses_page_and_limit_params(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test query uses page=1 and limit parameter."""
        mock_memory_client.search.return_value = {"data": []}
        
        await autogen_memory_instance.query("test")
        
        call_args = mock_memory_client.search.call_args
        assert call_args.kwargs["page"] == 1
        assert call_args.kwargs["limit"] == 10


class TestAutogenMemoryAdd:
    """Test add functionality of FlotorchAutogenMemory."""

    @pytest.mark.parametrize(
        "test_name,content,should_fail,expected_exception",
        ADD_TEST_DATA
    )
    @pytest.mark.asyncio
    async def test_add_with_various_scenarios(
        self,
        autogen_memory_instance,
        mock_memory_client,
        test_name,
        content,
        should_fail,
        expected_exception
    ):
        """Test add with parametrized scenarios."""
        if should_fail:
            mock_memory_client.add.side_effect = Exception("API Error")
            # Should not raise, just log error
            await autogen_memory_instance.add(content)
        else:
            await autogen_memory_instance.add(content)
            mock_memory_client.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_stores_content_as_user_message(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add stores content as user message."""
        content = MemoryContent(
            content="User said hello",
            mime_type=MemoryMimeType.TEXT
        )
        
        await autogen_memory_instance.add(content)
        
        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]
        
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "User said hello"

    @pytest.mark.asyncio
    async def test_add_creates_default_metadata(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add creates correct default metadata."""
        content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
        
        await autogen_memory_instance.add(content)
        
        call_args = mock_memory_client.add.call_args
        metadata = call_args.kwargs["metadata"]
        
        assert metadata["source"] == "adk_session"
        assert metadata["importance"] == 0.5
        assert metadata["category"] == "conversation"
        assert metadata["tags"] == ["adk", "session"]

    @pytest.mark.asyncio
    async def test_add_calls_api_with_correct_params(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add calls API with all required parameters."""
        content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
        
        await autogen_memory_instance.add(content)
        
        call_args = mock_memory_client.add.call_args
        
        assert "messages" in call_args.kwargs
        assert "userId" in call_args.kwargs
        assert "appId" in call_args.kwargs
        assert "metadata" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_add_uses_user_and_app_ids(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add passes correct user_id and app_id."""
        content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
        
        await autogen_memory_instance.add(content)
        
        call_args = mock_memory_client.add.call_args
        assert call_args.kwargs["userId"] == "test_user"
        assert call_args.kwargs["appId"] == "test_app"

    @pytest.mark.asyncio
    async def test_add_with_none_user_app_ids(
        self,
        autogen_memory_instance_with_none_ids,
        mock_memory_client
    ):
        """Test add passes None for user_id and app_id when not set."""
        content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
        
        await autogen_memory_instance_with_none_ids.add(content)
        
        call_args = mock_memory_client.add.call_args
        assert call_args.kwargs["userId"] is None
        assert call_args.kwargs["appId"] is None

    @pytest.mark.asyncio
    async def test_add_handles_api_failure(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add logs error but doesn't raise on API failure."""
        content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
        mock_memory_client.add.side_effect = Exception("API Error")
        
        # Should not raise exception
        await autogen_memory_instance.add(content)

    @pytest.mark.asyncio
    async def test_add_logs_error_on_failure(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test add logs error when API fails."""
        with patch('flotorch.autogen.memory.log_error') as mock_log_error:
            content = MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)
            mock_memory_client.add.side_effect = Exception("API Error")
            
            await autogen_memory_instance.add(content)
            
            mock_log_error.assert_called_once()
            call_args = mock_log_error.call_args
            assert "FlotorchMemoryService.add_session_to_memory" in call_args[0][0]


class TestAutogenMemoryUpdateContext:
    """Test update_context functionality of FlotorchAutogenMemory."""

    @pytest.mark.parametrize(
        "test_name,messages,api_response,should_add_to_context,should_fail,expected_exception",
        UPDATE_CONTEXT_TEST_DATA
    )
    @pytest.mark.asyncio
    async def test_update_context_with_various_scenarios(
        self,
        autogen_memory_instance,
        mock_memory_client,
        test_name,
        messages,
        api_response,
        should_add_to_context,
        should_fail,
        expected_exception
    ):
        """Test update_context with parametrized scenarios."""
        # Create mock context with messages
        mock_messages = [UserMessage(content=msg, source="user") for msg in messages]
        mock_context = Mock()
        mock_context.get_messages = AsyncMock(return_value=mock_messages)
        mock_context.add_message = AsyncMock()
        
        mock_memory_client.search.return_value = api_response
        
        result = await autogen_memory_instance.update_context(mock_context)
        
        if should_add_to_context:
            mock_context.add_message.assert_called_once()
        else:
            mock_context.add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_context_with_empty_messages(
        self,
        autogen_memory_instance,
        mock_chat_context_empty
    ):
        """Test update_context with empty message list."""
        result = await autogen_memory_instance.update_context(mock_chat_context_empty)
        
        assert isinstance(result.memories, MemoryQueryResult)
        assert len(result.memories.results) == 0
        assert len(mock_chat_context_empty.added_messages) == 0

    @pytest.mark.asyncio
    async def test_update_context_extracts_last_message_as_query(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context uses last message as query."""
        mock_memory_client.search.return_value = {"data": []}
        
        await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        call_args = mock_memory_client.search.call_args
        # Last message is "What is the weather?"
        assert call_args.kwargs["query"] == "What is the weather?"

    @pytest.mark.asyncio
    async def test_update_context_adds_memories_as_system_message(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context adds memories as SystemMessage."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "The weather is sunny"}]
        }
        
        await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        assert len(mock_chat_context_with_messages.added_messages) == 1
        added_msg = mock_chat_context_with_messages.added_messages[0]
        assert isinstance(added_msg, SystemMessage)

    @pytest.mark.asyncio
    async def test_update_context_formats_memories_as_numbered_list(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context formats memories as numbered list."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "content": "Memory one"},
                {"id": "mem-2", "content": "Memory two"},
                {"id": "mem-3", "content": "Memory three"}
            ]
        }
        
        await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        added_msg = mock_chat_context_with_messages.added_messages[0]
        content = added_msg.content
        
        assert "\nRelevant memories:\n" in content
        assert "1. Memory one" in content
        assert "2. Memory two" in content
        assert "3. Memory three" in content

    @pytest.mark.asyncio
    async def test_update_context_deduplicates_same_query(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context doesn't process same query twice."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test memory"}]
        }
        
        # First call
        result1 = await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        assert len(mock_chat_context_with_messages.added_messages) == 1
        
        # Second call with same context (same last message)
        result2 = await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        # Should not add another message
        assert len(mock_chat_context_with_messages.added_messages) == 1
        assert len(result2.memories.results) == 0

    @pytest.mark.asyncio
    async def test_update_context_deduplicates_same_results(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test update_context doesn't add same results twice."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test memory"}]
        }
        
        # First context with query "Query 1"
        context1 = Mock()
        context1.get_messages = AsyncMock(return_value=[UserMessage(content="Query 1", source="user")])
        context1.add_message = AsyncMock()

        result1 = await autogen_memory_instance.update_context(context1)
        assert context1.add_message.call_count == 1
        
        # Second context with different query but same results
        context2 = Mock()
        context2.get_messages = AsyncMock(return_value=[UserMessage(content="Query 2", source="user")])
        context2.add_message = AsyncMock()

        result2 = await autogen_memory_instance.update_context(context2)
        
        # Should not add to context because results hash is same
        assert context2.add_message.call_count == 0

    @pytest.mark.asyncio
    async def test_update_context_updates_tracking_state(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context updates _last_query and _last_results_hash."""
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test"}]
        }
        
        assert autogen_memory_instance._last_query is None
        assert autogen_memory_instance._last_results_hash is None
        
        await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        assert autogen_memory_instance._last_query == "What is the weather?"
        assert autogen_memory_instance._last_results_hash is not None

    @pytest.mark.asyncio
    async def test_update_context_handles_non_string_content(
        self,
        autogen_memory_instance,
        mock_memory_client
    ):
        """Test update_context handles non-string message content."""
        mock_memory_client.search.return_value = {"data": []}
        
        # Create message with non-string content
        mock_message = Mock()
        mock_message.content = {"type": "complex", "data": "value"}
        
        mock_context = Mock()
        mock_context.get_messages = AsyncMock(return_value=[mock_message])
        mock_context.add_message = AsyncMock()
        
        # Should not raise error, converts to string
        result = await autogen_memory_instance.update_context(mock_context)
        
        assert isinstance(result, Mock) or hasattr(result, 'memories')

    @pytest.mark.asyncio
    async def test_update_context_skips_when_no_results(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context doesn't add message when no memories found."""
        mock_memory_client.search.return_value = {"data": []}
        
        await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        # Should not add SystemMessage for "No memories found"
        assert len(mock_chat_context_with_messages.added_messages) == 0

    @pytest.mark.asyncio
    async def test_update_context_returns_update_context_result(
        self,
        autogen_memory_instance,
        mock_memory_client,
        mock_chat_context_with_messages
    ):
        """Test update_context returns UpdateContextResult."""
        from autogen_core.memory import UpdateContextResult
        
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-1", "content": "Test"}]
        }
        
        result = await autogen_memory_instance.update_context(mock_chat_context_with_messages)
        
        assert isinstance(result, UpdateContextResult)
        assert hasattr(result, 'memories')
        assert isinstance(result.memories, MemoryQueryResult)


class TestAutogenMemoryUtilities:
    """Test utility functions of FlotorchAutogenMemory."""

    def test_get_results_hash_with_empty_results(self, autogen_memory_instance):
        """Test _get_results_hash returns 'empty' for no results."""
        empty_result = MemoryQueryResult(results=[])
        
        hash_value = autogen_memory_instance._get_results_hash(empty_result)
        
        assert hash_value == "empty"

    def test_get_results_hash_with_single_result(self, autogen_memory_instance):
        """Test _get_results_hash generates hash for single result."""
        result = MemoryQueryResult(
            results=[MemoryContent(content="Test", mime_type=MemoryMimeType.TEXT)]
        )
        
        hash_value = autogen_memory_instance._get_results_hash(result)
        
        assert hash_value != "empty"
        assert isinstance(hash_value, int)

    def test_get_results_hash_with_multiple_results(self, autogen_memory_instance):
        """Test _get_results_hash generates hash for multiple results."""
        result = MemoryQueryResult(
            results=[
                MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT),
                MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)
            ]
        )
        
        hash_value = autogen_memory_instance._get_results_hash(result)
        
        assert hash_value != "empty"
        assert isinstance(hash_value, int)

    @pytest.mark.parametrize(
        "test_name,results1,results2,should_be_same",
        DEDUPLICATION_TEST_DATA
    )
    def test_get_results_hash_generates_same_for_identical_content(
        self,
        autogen_memory_instance,
        test_name,
        results1,
        results2,
        should_be_same
    ):
        """Test _get_results_hash generates same hash for identical content."""
        result1 = MemoryQueryResult(results=results1)
        result2 = MemoryQueryResult(results=results2)
        
        hash1 = autogen_memory_instance._get_results_hash(result1)
        hash2 = autogen_memory_instance._get_results_hash(result2)
        
        if should_be_same:
            assert hash1 == hash2
        else:
            assert hash1 != hash2

    def test_get_results_hash_generates_different_for_different_content(
        self,
        autogen_memory_instance
    ):
        """Test _get_results_hash generates different hashes for different content."""
        result1 = MemoryQueryResult(
            results=[MemoryContent(content="Memory A", mime_type=MemoryMimeType.TEXT)]
        )
        result2 = MemoryQueryResult(
            results=[MemoryContent(content="Memory B", mime_type=MemoryMimeType.TEXT)]
        )
        
        hash1 = autogen_memory_instance._get_results_hash(result1)
        hash2 = autogen_memory_instance._get_results_hash(result2)
        
        assert hash1 != hash2