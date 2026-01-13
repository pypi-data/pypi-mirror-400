"""Tests for FlotorchStore class."""

import pytest
import json
from unittest.mock import patch
from datetime import datetime
from langgraph.store.base import GetOp, PutOp, SearchOp

from flotorch.langgraph.tests.test_data.memory_test_data import (
    GET_TEST_DATA,
    PUT_TEST_DATA,
    SEARCH_TEST_DATA,
    UUID_VALIDATION_TEST_DATA,
    DATA_CONVERSION_TEST_DATA
)


class TestStoreInit:
    """Test initialization of FlotorchStore."""

    @patch('flotorch.langgraph.memory.FlotorchMemory')
    @patch('flotorch.langgraph.memory.FlotorchAsyncMemory')
    def test_init_with_all_parameters(self, mock_async_memory, mock_memory):
        """Test initialization with all custom parameters."""
        from flotorch.langgraph.memory import FlotorchStore
        instance = FlotorchStore(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_provider",
            userId="user_123",
            agentId="agent_456",
            appId="app_789",
            sessionId="session_abc"
        )
        assert (instance.api_key == "custom-key" and
                instance.base_url == "https://custom.flotorch.com" and
                instance.provider_name == "custom_provider" and
                instance.userId == "user_123" and
                instance.agentId == "agent_456" and
                instance.appId == "app_789" and
                instance.sessionId == "session_abc")
        mock_memory.assert_called_once_with(
            "custom-key", "https://custom.flotorch.com", "custom_provider")
        mock_async_memory.assert_called_once_with(
            "custom-key", "https://custom.flotorch.com", "custom_provider")

    @patch('flotorch.langgraph.memory.FlotorchMemory')
    @patch('flotorch.langgraph.memory.FlotorchAsyncMemory')
    def test_init_with_minimal_parameters(
        self, mock_async_memory, mock_memory
    ):
        """Test initialization with only required parameters."""
        from flotorch.langgraph.memory import FlotorchStore
        instance = FlotorchStore(
            api_key="test-key", base_url="https://test.flotorch.com",
            provider_name="test_provider"
        )
        assert (instance.api_key == "test-key" and
                instance.base_url == "https://test.flotorch.com" and
                instance.provider_name == "test_provider" and
                instance.userId is None and instance.agentId is None and
                instance.appId is None and instance.sessionId is None and
                instance.supports_ttl is False)


class TestNamespaceMapping:
    """Test namespace to gateway IDs mapping functionality."""

    def test_namespace_single_and_two_levels(
        self, store_instance_no_defaults
    ):
        """Test single and two level namespace mapping."""
        result = store_instance_no_defaults._namespace_to_gateway_ids(
            ("users",))
        assert result.get("appId") == "users" and "userId" not in result
        result = store_instance_no_defaults._namespace_to_gateway_ids(
            ("users", "alice"))
        assert (result.get("appId") == "users" and
                result.get("userId") == "alice")

    def test_namespace_with_class_defaults(self, store_instance):
        """Test empty namespace uses class defaults and overrides."""
        result = store_instance._namespace_to_gateway_ids(())
        assert (result["appId"] == "test_app" and
                result["userId"] == "test_user" and
                result["agentId"] == "test_agent" and
                result["sessionId"] == "test_session")
        result = store_instance._namespace_to_gateway_ids(
            ("custom_app", "custom_user"))
        assert (result["appId"] == "custom_app" and
                result["userId"] == "custom_user" and
                result["agentId"] == "test_agent" and
                result["sessionId"] == "test_session")


class TestUUIDValidation:
    """Test UUID validation functionality."""

    @pytest.mark.parametrize(
        "test_name,key,expected_result", UUID_VALIDATION_TEST_DATA
    )
    def test_is_memory_id(
        self, store_instance, test_name, key, expected_result
    ):
        """Test UUID validation with various key formats."""
        assert store_instance._is_memory_id(key) == expected_result


class TestDataConversion:
    """Test data conversion between memory and LangGraph formats."""

    @pytest.mark.parametrize(
        "test_name,memory_data,expected_value", DATA_CONVERSION_TEST_DATA
    )
    def test_memory_data_to_item(
        self,
        store_instance,
        test_name,
        memory_data,
        expected_value
    ):
        """Test conversion from memory data to LangGraph Item."""
        item = store_instance._memory_data_to_item(
            memory_data, ("users", "alice"), "test_key")
        assert (item.value == expected_value and item.key == "test_key" and
                item.namespace == ("users", "alice") and
                isinstance(item.created_at, datetime) and
                isinstance(item.updated_at, datetime))

    def test_memory_data_to_search_item(self, store_instance):
        """Test conversion from memory data to LangGraph SearchItem."""
        memory_data = {
            "id": "mem-123", "content": '{"test": "data"}',
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00", "importance": 0.8,
            "metadata": {
                "langgraph_namespace": ["users", "alice"],
                "langgraph_key": "test_key"}
        }
        search_item = store_instance._memory_data_to_search_item(memory_data)
        assert (search_item.namespace == ("users", "alice") and
                search_item.key == "test_key" and
                search_item.value == {"test": "data"} and
                search_item.score == 0.8)
        memory_data["metadata"] = {}
        op = SearchOp(namespace_prefix=("default_ns",), query="test")
        search_item = store_instance._memory_data_to_search_item(
            memory_data, op)
        assert search_item.namespace == ("default_ns",)

    def test_response_to_item_conversion(self, store_instance):
        """Test conversion from API response to Item."""
        response = {
            "data": {
                "id": "mem-123",
                "content": '{"key": "value"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        item = store_instance._response_to_item(
            response, ("users",), "test_key")
        assert (item is not None and item.value == {"key": "value"} and
                item.key == "test_key")
        assert store_instance._response_to_item(
            {}, ("users",), "test_key") is None


class TestGetOperations:
    """Test GET operation functionality."""

    @pytest.mark.parametrize(
        "test_name,key,namespace,api_response,should_succeed,"
        "should_fail,expected_exception", GET_TEST_DATA
    )
    def test_handle_get_with_various_scenarios(
        self,
        store_instance,
        mock_memory_client,
        test_name,
        key,
        namespace,
        api_response,
        should_succeed,
        should_fail,
        expected_exception
    ):
        """Test GET operation with parametrized scenarios."""
        if should_fail:
            mock_memory_client.get.side_effect = Exception("API Error")
            mock_memory_client.search.side_effect = Exception("API Error")
        else:
            if store_instance._is_memory_id(key):
                mock_memory_client.get.return_value = api_response
            else:
                mock_memory_client.search.return_value = api_response
        op = GetOp(namespace=namespace, key=key)
        result = store_instance._handle_get(op)
        if should_succeed:
            assert (result is not None and result.key == key and
                    result.namespace == namespace)
        else:
            assert result is None

    def test_get_by_uuid_vs_key(self, store_instance, mock_memory_client):
        """Test UUID keys use get() and non-UUID keys use search()."""
        uuid_key = "123e4567-e89b-12d3-a456-426614174000"
        mock_memory_client.get.return_value = {
            "data": {
                "id": uuid_key,
                "content": '{"test": "data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        op = GetOp(namespace=("users",), key=uuid_key)
        result = store_instance._handle_get(op)
        mock_memory_client.get.assert_called_once_with(uuid_key)
        assert result is not None
        mock_memory_client.reset_mock()
        mock_memory_client.search.return_value = {
            "data": [{
                "id": "mem-123", "content": "Test content",
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00",
                "metadata": {"tags": ["test_key"], "langgraph_key": "test_key"}
            }]
        }
        op = GetOp(namespace=("users",), key="test_key")
        result = store_instance._handle_get(op)
        mock_memory_client.search.assert_called_once()
        call_kwargs = mock_memory_client.search.call_args.kwargs
        assert (call_kwargs["appId"] == "users" and
                call_kwargs["limit"] == 1 and result is not None)

    def test_get_aggregates_multiple_results(
        self, store_instance, mock_memory_client
    ):
        """Test get aggregates content from multiple results."""
        mock_memory_client.search.return_value = {
            "data": [
                {"id": "mem-1", "content": "First part",
                 "createdAt": "2024-01-01T00:00:00",
                 "updatedAt": "2024-01-01T00:00:00",
                 "metadata": {"tags": ["test_key"]}},
                {"id": "mem-2", "content": "Second part",
                 "createdAt": "2024-01-01T00:00:00",
                 "updatedAt": "2024-01-01T00:00:00",
                 "metadata": {"tags": ["test_key"]}}]
        }
        op = GetOp(namespace=("users",), key="test_key")
        result = store_instance._handle_get(op)
        assert (result is not None and
                "First part" in result.value.get("text", "") and
                "Second part" in result.value.get("text", ""))

    @pytest.mark.asyncio
    async def test_handle_aget_async(
        self, store_instance, mock_async_memory_client
    ):
        """Test asynchronous GET operation."""
        uuid_key = "123e4567-e89b-12d3-a456-426614174000"
        mock_async_memory_client.get.return_value = {
            "data": {
                "id": uuid_key,
                "content": '{"test": "async data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        op = GetOp(namespace=("users",), key=uuid_key)
        result = await store_instance._handle_aget(op)
        mock_async_memory_client.get.assert_called_once_with(uuid_key)
        assert (result is not None and
                result.value == {"test": "async data"})


class TestPutOperations:
    """Test PUT operation functionality."""

    @pytest.mark.parametrize(
        "test_name,key,namespace,value,delete_response,is_delete,"
        "should_fail,expected_exception", PUT_TEST_DATA
    )
    def test_handle_put_with_various_scenarios(
        self,
        store_instance,
        mock_memory_client,
        test_name,
        key,
        namespace,
        value,
        delete_response,
        is_delete,
        should_fail,
        expected_exception
    ):
        """Test PUT operation with parametrized scenarios."""
        if should_fail:
            mock_memory_client.add.side_effect = Exception("API Error")
            mock_memory_client.delete.side_effect = Exception("API Error")
        else:
            if is_delete and not store_instance._is_memory_id(key):
                mock_memory_client.search.return_value = delete_response
        op = PutOp(namespace=namespace, key=key, value=value)
        store_instance._handle_put(op)
        if not should_fail:
            if is_delete:
                if store_instance._is_memory_id(key):
                    mock_memory_client.delete.assert_called_once_with(key)
            else:
                mock_memory_client.add.assert_called_once()

    def test_put_stores_with_correct_metadata(
        self, store_instance, mock_memory_client
    ):
        """Test put stores data with correct metadata."""
        value = {"preference": "dark_mode", "language": "en"}
        op = PutOp(
            namespace=("users", "alice"), key="settings", value=value)
        store_instance._handle_put(op)
        call_kwargs = mock_memory_client.add.call_args.kwargs
        assert (call_kwargs["appId"] == "users" and
                call_kwargs["userId"] == "alice" and
                "messages" in call_kwargs and
                call_kwargs["metadata"]["source"] == "langgraph_store" and
                call_kwargs["metadata"]["tags"] == ["settings"])
        message_content = call_kwargs["messages"][0]["content"]
        assert json.loads(message_content) == value

    def test_delete_operations(self, store_instance, mock_memory_client):
        """Test delete by UUID and by key."""
        uuid_key = "123e4567-e89b-12d3-a456-426614174000"
        op = PutOp(namespace=("users",), key=uuid_key, value=None)
        store_instance._handle_put(op)
        mock_memory_client.delete.assert_called_once_with(uuid_key)
        mock_memory_client.reset_mock()
        mock_memory_client.search.return_value = {
            "data": [{"id": "mem-to-delete"}]}
        op = PutOp(namespace=("users",), key="old_setting", value=None)
        store_instance._handle_put(op)
        mock_memory_client.search.assert_called_once()
        mock_memory_client.delete.assert_called_once_with("mem-to-delete")

    @pytest.mark.asyncio
    async def test_handle_aput_operations(
        self, store_instance, mock_async_memory_client
    ):
        """Test asynchronous PUT and DELETE operations."""
        value = {"test": "async value"}
        op = PutOp(namespace=("users",), key="test_key", value=value)
        await store_instance._handle_aput(op)
        mock_async_memory_client.add.assert_called_once()
        mock_async_memory_client.reset_mock()
        uuid_key = "123e4567-e89b-12d3-a456-426614174000"
        op = PutOp(namespace=("users",), key=uuid_key, value=None)
        await store_instance._handle_aput(op)
        mock_async_memory_client.delete.assert_called_once_with(uuid_key)


class TestSearchOperations:
    """Test SEARCH operation functionality."""

    @pytest.mark.parametrize(
        "test_name,query,namespace,limit,api_response,expected_count,"
        "should_fail,expected_exception", SEARCH_TEST_DATA
    )
    def test_handle_search_with_various_scenarios(
        self,
        store_instance,
        mock_memory_client,
        test_name,
        query,
        namespace,
        limit,
        api_response,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test SEARCH operation with parametrized scenarios."""
        if should_fail:
            mock_memory_client.search.side_effect = Exception("API Error")
        else:
            mock_memory_client.search.return_value = api_response
        op = SearchOp(namespace_prefix=namespace, query=query, limit=limit)
        results = store_instance._handle_search(op)
        assert len(results) == expected_count
        if expected_count > 0:
            for item in results:
                assert (hasattr(item, "namespace") and
                        hasattr(item, "key") and hasattr(item, "value") and
                        hasattr(item, "score"))

    def test_search_query_and_limits(
        self, store_instance, mock_memory_client
    ):
        """Test search uses semantic query and respects limits."""
        mock_memory_client.search.return_value = {"data": []}
        op = SearchOp(
            namespace_prefix=("users",), query="user preferences", limit=10)
        store_instance._handle_search(op)
        call_kwargs = mock_memory_client.search.call_args.kwargs
        assert (call_kwargs["query"] == "user preferences" and
                call_kwargs["limit"] == 10 and
                call_kwargs["appId"] == "users")
        mock_memory_client.reset_mock()
        mock_memory_client.search.return_value = {
            "data": [
                {"id": f"mem-{i}", "content": f"Content {i}",
                 "createdAt": "2024-01-01T00:00:00",
                 "updatedAt": "2024-01-01T00:00:00",
                 "importance": 0.5, "metadata": {}} for i in range(10)]
        }
        op = SearchOp(namespace_prefix=("users",), query="test", limit=3)
        results = store_instance._handle_search(op)
        assert len(results) == 3
        mock_memory_client.reset_mock()
        mock_memory_client.search.return_value = {"data": []}
        op = SearchOp(namespace_prefix=("users",), query="test", limit=None)
        store_instance._handle_search(op)
        call_kwargs = mock_memory_client.search.call_args.kwargs
        assert call_kwargs["limit"] == 20

    @pytest.mark.asyncio
    async def test_handle_asearch_async(
        self, store_instance, mock_async_memory_client
    ):
        """Test asynchronous SEARCH operation."""
        mock_async_memory_client.search.return_value = {
            "data": [{
                "id": "mem-1",
                "content": '{"test": "data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00",
                "importance": 0.7,
                "metadata": {}
            }]
        }
        op = SearchOp(
            namespace_prefix=("users",), query="test query", limit=5)
        results = await store_instance._handle_asearch(op)
        mock_async_memory_client.search.assert_called_once()
        assert len(results) == 1


class TestBatchOperations:
    """Test BATCH operation functionality."""

    def test_batch_multiple_operations(
        self, store_instance, mock_memory_client
    ):
        """Test batch processing of multiple operations."""
        mock_memory_client.get.return_value = {
            "data": {
                "id": "mem-123", "content": '{"test": "data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        ops = [
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174000"),
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174001"),
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174002"),
        ]
        results = store_instance.batch(ops)
        assert (len(results) == 3 and
                mock_memory_client.get.call_count == 3)

    def test_batch_mixed_operation_types(
        self, store_instance, mock_memory_client
    ):
        """Test batch processing with mixed operation types."""
        mock_memory_client.get.return_value = {
            "data": {
                "id": "mem-123", "content": '{"test": "data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        mock_memory_client.search.return_value = {"data": []}
        ops = [
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174000"),
            PutOp(namespace=("users",), key="key1",
                  value={"data": "test"}),
            SearchOp(namespace_prefix=("users",), query="test", limit=5),
        ]
        results = store_instance.batch(ops)
        assert (len(results) == 3 and
                mock_memory_client.get.call_count == 1 and
                mock_memory_client.add.call_count == 1 and
                mock_memory_client.search.call_count == 1)

    def test_batch_handles_individual_failures(
        self, store_instance, mock_memory_client
    ):
        """Test batch continues processing when operations fail."""
        mock_memory_client.get.side_effect = [
            {"data": {"id": "mem-1", "content": '{"test": "data"}',
                     "createdAt": "2024-01-01T00:00:00",
                     "updatedAt": "2024-01-01T00:00:00"}},
            Exception("API Error"),
            {"data": {"id": "mem-3", "content": '{"test": "data"}',
                     "createdAt": "2024-01-01T00:00:00",
                     "updatedAt": "2024-01-01T00:00:00"}},
        ]
        ops = [
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174000"),
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174001"),
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174002"),
        ]
        results = store_instance.batch(ops)
        assert (len(results) == 3 and results[0] is not None and
                results[1] is None and results[2] is not None)

    @pytest.mark.asyncio
    async def test_abatch_async_operations(
        self, store_instance, mock_async_memory_client
    ):
        """Test asynchronous batch processing."""
        mock_async_memory_client.get.return_value = {
            "data": {
                "id": "mem-123", "content": '{"test": "async data"}',
                "createdAt": "2024-01-01T00:00:00",
                "updatedAt": "2024-01-01T00:00:00"
            }
        }
        mock_async_memory_client.search.return_value = {"data": []}
        ops = [
            GetOp(namespace=("users",),
                  key="123e4567-e89b-12d3-a456-426614174000"),
            PutOp(namespace=("users",), key="key1",
                  value={"data": "test"}),
            SearchOp(namespace_prefix=("users",), query="test", limit=5),
        ]
        results = await store_instance.abatch(ops)
        assert len(results) == 3


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_malformed_json_content_handling(self, store_instance):
        """Test that malformed JSON is handled gracefully."""
        memory_data = {
            "id": "mem-bad", "content": "{invalid json}",
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00"
        }
        item = store_instance._memory_data_to_item(
            memory_data, ("users",), "test_key")
        assert isinstance(item.value, dict) and "text" in item.value

    def test_unicode_content_handling(
        self, store_instance, mock_memory_client
    ):
        """Test proper handling of Unicode content."""
        unicode_value = {"message": "Hello World", "language": "English"}
        op = PutOp(
            namespace=("users",), key="unicode_key", value=unicode_value)
        store_instance._handle_put(op)
        call_kwargs = mock_memory_client.add.call_args.kwargs
        content = call_kwargs["messages"][0]["content"]
        parsed = json.loads(content)
        assert (parsed["message"] == "Hello World" and
                parsed["language"] == "English")

    def test_empty_namespace_handling(self, store_instance_no_defaults):
        """Test operations with empty namespace."""
        result = store_instance_no_defaults._namespace_to_gateway_ids(())
        assert isinstance(result, dict)

    def test_batch_with_list_namespaces_operation(self, store_instance):
        """Test batch handles ListNamespacesOp."""
        from langgraph.store.base import ListNamespacesOp
        ops = [ListNamespacesOp(match_conditions=[], max_depth=None)]
        results = store_instance.batch(ops)
        assert len(results) == 1 and results[0] is None


class TestConvenienceFunction:
    """Test the convenience function for creating FlotorchStore."""

    @patch('flotorch.langgraph.memory.FlotorchMemory')
    @patch('flotorch.langgraph.memory.FlotorchAsyncMemory')
    def test_create_flotorch_store(self, mock_async_memory, mock_memory):
        """Test the create_flotorch_store convenience function."""
        from flotorch.langgraph.memory import create_flotorch_store
        store = create_flotorch_store(
            api_key="test-key", base_url="https://test.com",
            provider_name="test_provider", userId="user_123",
            agentId="agent_456", appId="app_789", sessionId="session_abc"
        )
        assert (store.api_key == "test-key" and
                store.base_url == "https://test.com" and
                store.provider_name == "test_provider" and
                store.userId == "user_123" and
                store.agentId == "agent_456" and
                store.appId == "app_789" and
                store.sessionId == "session_abc")
