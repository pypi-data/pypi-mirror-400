"""Test cases for FlotorchMemoryService class (ADK).

This module contains comprehensive unit tests for the FlotorchMemoryService
class, covering initialization, add_session_to_memory, and search_memory operations.
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flotorch.adk.tests.test_data.memory_test_data import (
    ADD_SESSION_TEST_DATA,
    CONTENT_EXTRACTION_TEST_DATA,
    ROLE_EXTRACTION_TEST_DATA,
    SEARCH_MEMORY_TEST_DATA,
)

def create_mock_session(session_id, user_id, app_name, messages):
    """Helper to create mock session with events.
    
    Args:
        session_id: Session ID
        user_id: User ID
        app_name: App name
        messages: List of dicts with 'role' and 'content'
        
    Returns:
        Mock session object with events
    """
    mock_session = Mock()
    mock_session.id = session_id
    mock_session.user_id = user_id
    mock_session.app_name = app_name
    mock_session.created_at = datetime.now(timezone.utc)

    mock_events = []
    for msg in messages:
        event = Mock()
        event.role = msg["role"]
        event.content = Mock()
        event.content.role = msg["role"]
        event.content.parts = [Mock(text=msg["content"])]
        event.author = msg["role"]
        mock_events.append(event)

    mock_session.events = mock_events
    return mock_session


class TestMemoryServiceInit:
    """Test initialization of FlotorchMemoryService."""

    @patch('flotorch.adk.memory.FlotorchMemory')
    def test_init_with_all_parameters(self, mock_memory):
        """Test initialization with all custom parameters."""
        from flotorch.adk.memory import FlotorchMemoryService

        instance = FlotorchMemoryService(
            name="custom_provider",
            api_key="custom-key",
            base_url="https://custom.flotorch.com"
        )

        assert instance._name == "custom_provider"
        assert instance._api_key == "custom-key"
        assert instance._base_url == "https://custom.flotorch.com"

        mock_memory.assert_called_once_with(
            api_key="custom-key",
            base_url="https://custom.flotorch.com",
            provider_name="custom_provider"
        )

    @patch('flotorch.adk.memory.FlotorchMemory')
    def test_init_with_minimal_parameters(self, mock_memory):
        """Test initialization with only required parameters."""
        from flotorch.adk.memory import FlotorchMemoryService

        instance = FlotorchMemoryService(
            name="test_provider",
            api_key="test-key",
            base_url="https://test.flotorch.com"
        )

        assert instance._name == "test_provider"
        assert instance._api_key == "test-key"
        assert instance._base_url == "https://test.flotorch.com"

    @patch('flotorch.adk.memory.FlotorchMemory')
    def test_init_missing_api_key(self, mock_memory, monkeypatch):
        """Test initialization without API key raises error."""
        from flotorch.adk.memory import FlotorchMemoryService
        monkeypatch.delenv('FLOTORCH_API_KEY', raising=False)
        with pytest.raises(ValueError, match="FLOTORCH_API_KEY"):
            FlotorchMemoryService(name="test", base_url="https://test.com")

    @patch('flotorch.adk.memory.FlotorchMemory')
    def test_init_missing_base_url(self, mock_memory, monkeypatch):
        """Test initialization without base URL raises error."""
        from flotorch.adk.memory import FlotorchMemoryService
        monkeypatch.delenv('FLOTORCH_BASE_URL', raising=False)
        with pytest.raises(ValueError, match="FLOTORCH_BASE_URL"):
            FlotorchMemoryService(name="test", api_key="test-key")


class TestRoleExtraction:
    """Test role extraction and mapping functionality."""

    @pytest.mark.parametrize(
        "test_name,input_role,expected_role",
        ROLE_EXTRACTION_TEST_DATA
    )
    def test_map_role_to_flotorch(self, memory_service_instance, test_name, input_role, expected_role):
        """Test role mapping from ADK to Flotorch format."""
        result = memory_service_instance._map_role_to_flotorch(input_role)
        assert result == expected_role

    def test_extract_role_from_content(self, memory_service_instance):
        """Test extracting role from event.content."""
        mock_event = Mock()
        mock_event.content = Mock()
        mock_event.content.role = "model"

        result = memory_service_instance._extract_role(mock_event)
        assert result == "assistant"

    def test_extract_role_from_event_directly(self, memory_service_instance):
        """Test extracting role from event directly."""
        mock_event = Mock()
        mock_event.content = None
        mock_event.role = "user"

        result = memory_service_instance._extract_role(mock_event)
        assert result == "user"

    def test_extract_role_from_author(self, memory_service_instance):
        """Test extracting role from author field."""
        mock_event = Mock()
        mock_event.content = None
        mock_event.role = None
        mock_event.author = "agent"

        result = memory_service_instance._extract_role(mock_event)
        assert result == "assistant"

    def test_extract_role_fallback(self, memory_service_instance):
        """Test role extraction fallback to 'user'."""
        mock_event = Mock()
        mock_event.content = None
        mock_event.role = None
        mock_event.author = None

        result = memory_service_instance._extract_role(mock_event)
        assert result == "user"


class TestContentExtraction:
    """Test content extraction functionality."""

    @pytest.mark.parametrize(
        "test_name,mock_event_data,expected_text",
        CONTENT_EXTRACTION_TEST_DATA
    )
    def test_extract_content_text_various_formats(
        self,
        memory_service_instance,
        test_name,
        mock_event_data,
        expected_text
    ):
        """Test content extraction from various event formats."""
        mock_event = Mock()

        if "content" in mock_event_data:
            if isinstance(mock_event_data["content"], dict) and "parts" in mock_event_data["content"]:
                mock_event.content = Mock()
                mock_event.content.parts = []
                for part_data in mock_event_data["content"]["parts"]:
                    part = Mock()
                    part.text = part_data["text"]
                    mock_event.content.parts.append(part)
                mock_event.text = None
            elif isinstance(mock_event_data["content"], str):
                mock_event.content = mock_event_data["content"]
                mock_event.text = None
            else:
                mock_event.content = mock_event_data["content"]
                mock_event.text = None
        elif "text" in mock_event_data:
            mock_event.text = mock_event_data["text"]
            mock_event.content = None
        else:
            mock_event.content = None
            mock_event.text = None

        result = memory_service_instance._extract_content_text(mock_event)
        assert result == expected_text


class TestTimestampExtraction:
    """Test timestamp extraction functionality."""

    def test_get_timestamp_from_session(self, memory_service_instance):
        """Test extracting timestamp from session."""
        mock_session = Mock()
        mock_session.created_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = memory_service_instance._get_timestamp(mock_session)
        assert "2024-01-01T12:00:00" in result
        assert "+" in result or "Z" in result.replace("+00:00", "Z")

    def test_get_timestamp_adds_timezone_if_missing(self, memory_service_instance):
        """Test timestamp gets timezone added if missing."""
        mock_session = Mock()
        mock_session.created_at = datetime(2024, 1, 1, 12, 0, 0)    

        result = memory_service_instance._get_timestamp(mock_session)
        assert "2024-01-01T12:00:00" in result

    def test_get_timestamp_fallback_to_current_time(self, memory_service_instance):
        """Test timestamp falls back to current time."""
        mock_session = Mock()
        mock_session.created_at = None

        result = memory_service_instance._get_timestamp(mock_session)
        assert "T" in result
        assert len(result) > 19  


class TestAddSessionToMemory:
    """Test add_session_to_memory functionality."""

    @pytest.mark.parametrize(
        "test_name,session_id,user_id,app_name,messages,should_fail,expected_exception",
        ADD_SESSION_TEST_DATA
    )
    @pytest.mark.asyncio
    async def test_add_session_with_various_scenarios(
        self,
        memory_service_instance,
        mock_memory_client,
        test_name,
        session_id,
        user_id,
        app_name,
        messages,
        should_fail,
        expected_exception
    ):
        """Test add_session_to_memory with parametrized scenarios."""
        mock_session = create_mock_session(session_id, user_id, app_name, messages)

        if should_fail:
            mock_memory_client.add.side_effect = Exception("API Error")
            await memory_service_instance.add_session_to_memory(mock_session)
            mock_memory_client.add.assert_called_once()
        else:
            await memory_service_instance.add_session_to_memory(mock_session)
            mock_memory_client.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_session_extracts_messages_correctly(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test that add_session correctly extracts and formats messages."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "model", "content": "Hi there!"}
        ]
        mock_session = create_mock_session("test_session", "test_user", "test_app", messages)

        await memory_service_instance.add_session_to_memory(mock_session)

        call_args = mock_memory_client.add.call_args
        messages = call_args.kwargs["messages"]

        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"  
        assert messages[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_add_session_includes_correct_metadata(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test that add_session includes correct metadata."""
        mock_session = create_mock_session("test_session", "test_user", "test_app", [])

        await memory_service_instance.add_session_to_memory(mock_session)

        call_args = mock_memory_client.add.call_args
        metadata = call_args.kwargs["metadata"]

        assert metadata["source"] == "adk_session"
        assert metadata["importance"] == 0.5
        assert metadata["category"] == "conversation"
        assert "adk" in metadata["tags"]
        assert "session" in metadata["tags"]

    @pytest.mark.asyncio
    async def test_add_session_fallback_to_messages_attribute(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test that add_session falls back to messages if events is None."""
        mock_session = Mock()
        mock_session.id = "test_session"
        mock_session.user_id = "test_user"
        mock_session.app_name = "test_app"
        mock_session.created_at = datetime.now(timezone.utc)
        mock_session.events = None

        message = Mock()
        message.role = "user"
        message.content = Mock()
        message.content.parts = [Mock(text="Test")]
        mock_session.messages = [message]

        await memory_service_instance.add_session_to_memory(mock_session)

        mock_memory_client.add.assert_called_once()


class TestSearchMemory:
    """Test search_memory functionality."""

    @pytest.mark.parametrize(
        "test_name,app_name,user_id,query,api_response,expected_count,should_fail,expected_exception",
        SEARCH_MEMORY_TEST_DATA
    )
    @pytest.mark.asyncio
    async def test_search_memory_with_various_scenarios(
        self,
        memory_service_instance,
        mock_memory_client,
        test_name,
        app_name,
        user_id,
        query,
        api_response,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test search_memory with parametrized scenarios."""
        if should_fail:
            mock_memory_client.search.side_effect = Exception("API Error")
            result = await memory_service_instance.search_memory(
                app_name=app_name,
                user_id=user_id,
                query=query
            )
            assert len(result.memories) == 0
        else:
            mock_memory_client.search.return_value = api_response
            result = await memory_service_instance.search_memory(
                app_name=app_name,
                user_id=user_id,
                query=query
            )

            assert len(result.memories) == expected_count

    @pytest.mark.asyncio
    async def test_search_memory_calls_api_with_correct_params(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory calls API with correct parameters."""
        mock_memory_client.search.return_value = {"data": []}

        await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="test query"
        )

        mock_memory_client.search.assert_called_once_with(
            userId="test_user",
            appId="test_app",
            sessionId=None,
            categories=None,
            query="test query",
            page=1,
            limit=10
        )

    @pytest.mark.asyncio
    async def test_search_memory_extracts_text_with_priority(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory prioritizes memory > content > text fields."""
        mock_memory_client.search.return_value = {
            "data": [
                {"memory": "from memory field", "timestamp": "2024-01-01T00:00:00Z"},
                {"content": "from content field", "timestamp": "2024-01-01T00:00:00Z"},
                {"text": "from text field", "timestamp": "2024-01-01T00:00:00Z"},
            ]
        }

        result = await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="test"
        )

        assert len(result.memories) == 3
        mem0_text = str(result.memories[0].content.parts[0].text)
        mem1_text = str(result.memories[1].content.parts[0].text)
        mem2_text = str(result.memories[2].content.parts[0].text)
        assert "from memory field" in mem0_text
        assert "from content field" in mem1_text
        assert "from text field" in mem2_text

    @pytest.mark.asyncio
    async def test_search_memory_extracts_from_messages_array(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory extracts content from messages array."""
        mock_memory_client.search.return_value = {
            "data": [
                {
                    "messages": [{"content": "from messages array"}],
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        result = await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="test"
        )

        assert len(result.memories) == 1
        memory_text = str(result.memories[0].content.parts[0].text)
        assert "from messages array" in memory_text

    @pytest.mark.asyncio
    async def test_search_memory_returns_empty_for_no_results(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory returns empty response when no results."""
        mock_memory_client.search.return_value = {"data": []}

        result = await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="nonexistent"
        )

        assert len(result.memories) == 0

    @pytest.mark.asyncio
    async def test_search_memory_skips_items_without_content(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory skips items with no extractable content."""
        mock_memory_client.search.return_value = {
            "data": [
                {
                    "memory": "Valid content",
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                {"other_field": "No content field"},
                {
                    "memory": "Another valid",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }

        result = await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="test"
        )

        assert len(result.memories) == 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_add_session_with_empty_events(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test add_session handles empty events list."""
        mock_session = create_mock_session("test", "user", "app", [])
        await memory_service_instance.add_session_to_memory(mock_session)
        assert mock_memory_client.add.call_args.kwargs["messages"] == []

    @pytest.mark.asyncio
    async def test_search_memory_handles_missing_timestamp(
        self,
        memory_service_instance,
        mock_memory_client
    ):
        """Test search_memory handles missing timestamp fields."""
        mock_memory_client.search.return_value = {
            "data": [{"memory": "Content without timestamp"}]
        }
        result = await memory_service_instance.search_memory(
            app_name="test_app",
            user_id="test_user",
            query="test"
        )
        assert len(result.memories) == 1
        assert result.memories[0].timestamp is None

    def test_extract_role_exception(self, memory_service_instance):
        """Test extract_role handles exception."""
        mock_event = Mock()
        mock_event.content = Mock()
        mock_event.content.role = Mock(side_effect=Exception("Error"))
        result = memory_service_instance._extract_role(mock_event)
        assert result == "user"

    def test_extract_content_with_direct_text(self, memory_service_instance):
        """Test content extraction from direct text attribute."""
        mock_event = Mock()
        mock_event.content = None
        mock_event.text = "Direct text"
        result = memory_service_instance._extract_content_text(mock_event)
        assert result == "Direct text"

    def test_extract_content_exception(self, memory_service_instance):
        """Test content extraction handles exception."""
        mock_event = Mock()
        mock_event.content = Mock()
        mock_event.content.parts = Mock(side_effect=Exception("Error"))
        result = memory_service_instance._extract_content_text(mock_event)
        assert result == "Content extraction error"

    def test_get_timestamp_exception(self, memory_service_instance):
        """Test timestamp extraction handles exception."""
        from unittest.mock import PropertyMock
        mock_session = Mock()
        property_mock = PropertyMock(side_effect=Exception("Error"))
        type(mock_session).created_at = property_mock
        result = memory_service_instance._get_timestamp(mock_session)
        
        assert isinstance(result, str) and "T" in result


class TestVectorMemoryService:
    """Test FlotorchADKVectorMemoryService."""

    @patch('flotorch.adk.memory.FlotorchVectorStore')
    def test_vector_init_with_vectorstore(self, mock_vectorstore):
        """Test init with vectorstore_id."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        service = FlotorchADKVectorMemoryService(
            api_key="key",
            base_url="url",
            vectorstore_id="vs123"
        )
        assert service.vectorstore_id == "vs123"
        assert service.vector_store is not None

    @patch('flotorch.adk.memory.FlotorchVectorStore')
    def test_vector_init_without_vectorstore(self, mock_vectorstore):
        """Test init without vectorstore_id."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        service = FlotorchADKVectorMemoryService(
            api_key="key",
            base_url="url",
            vectorstore_id=None
        )
        assert service.vector_store is None

    @pytest.mark.asyncio
    @patch('flotorch.adk.memory.FlotorchVectorStore')
    async def test_vector_search_memory(self, mock_vectorstore):
        """Test vector search_memory."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        mock_vs = Mock()
        search_result = {"data": [{"content": [{"text": "result"}]}]}
        mock_vs.search.return_value = search_result
        service = FlotorchADKVectorMemoryService(
            api_key="key",
            base_url="url",
            vectorstore_id="vs1"
        )
        service.vector_store = mock_vs
        result = await service.search_memory("test", knn=5)
        assert len(result.memories) > 0

    @pytest.mark.asyncio
    async def test_vector_search_memory_exception(self):
        """Test vector search_memory handles exception."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        cls = FlotorchADKVectorMemoryService
        service = cls.__new__(cls)
        service.vector_store = Mock()
        service.vector_store.search.side_effect = Exception("Error")
        result = await service.search_memory("test")
        assert len(result.memories) == 0

    @pytest.mark.asyncio
    async def test_vector_search_without_vectorstore(self):
        """Test _search_vector_store without vectorstore."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        cls = FlotorchADKVectorMemoryService
        service = cls.__new__(cls)
        service.vector_store = None
        result = await service._search_vector_store("test")
        assert result == []

    @pytest.mark.asyncio
    async def test_add_session_to_memory_pass(self):
        """Test add_session_to_memory does nothing."""
        from flotorch.adk.memory import FlotorchADKVectorMemoryService
        cls = FlotorchADKVectorMemoryService
        service = cls.__new__(cls)
        await service.add_session_to_memory(Mock())  

