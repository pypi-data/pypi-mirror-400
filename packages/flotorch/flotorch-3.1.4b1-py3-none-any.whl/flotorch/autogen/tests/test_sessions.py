"""Test cases for FlotorchAutogenSession class.

This module contains comprehensive tests for the FlotorchAutogenSession class,
covering initialization, message handling, state management, and error scenarios.
"""

from unittest.mock import AsyncMock, patch

import pytest

from flotorch.autogen.sessions import FlotorchAutogenSession
from flotorch.autogen.sessions import FlotorchAutogenSessionConfig
from flotorch.autogen.tests.test_data.sessions_test_data import (
    ADD_MESSAGE_TEST_DATA,
    AUTOGEN_TO_FLOTORCH_TEST_DATA,
    FLOTORCH_TO_AUTOGEN_TEST_DATA,
    GET_MESSAGES_TEST_DATA,
    SAMPLE_USER_MESSAGE,
)


class TestFlotorchAutogenSessionInit:
    """Test constructor initialization."""

    @patch('flotorch.autogen.sessions.FlotorchAsyncSession')
    def test_init_with_custom_parameters(self, mock_flotorch_session):
        """Test initialization with custom parameters."""
        mock_session = AsyncMock()
        mock_flotorch_session.return_value = mock_session

        instance = FlotorchAutogenSession(
            base_url="https://custom.flotorch.com",
            api_key="custom-key-123",
            uid="test-uid",
            recent_messages_max=100
        )
        assert instance.uid == "test-uid"
        assert instance.api_key == "custom-key-123"
        assert instance.base_url == "https://custom.flotorch.com"
        assert instance.recent_messages_max == 100
        assert instance._initialized is False
        assert instance._messages_cache == []

    @patch('flotorch.autogen.sessions.FlotorchAsyncSession')
    def test_init_with_defaults(self, mock_flotorch_session):
        """Test initialization with default parameters."""
        mock_session = AsyncMock()
        mock_flotorch_session.return_value = mock_session

        with patch.dict('os.environ', {
            'FLOTORCH_API_KEY': 'test-key',
            'FLOTORCH_BASE_URL': 'https://test.com'
        }):
            instance = FlotorchAutogenSession()
        assert instance.uid is None
        assert instance.api_key == 'test-key'
        assert instance.base_url == 'https://test.com'
        assert instance.recent_messages_max == 50

    def test_init_requires_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Flotorch API key is required"):
                FlotorchAutogenSession()


class TestAutogenToFlotorchConversion:
    """Test _autogen_to_flotorch_event method."""

    @pytest.mark.parametrize(
        "test_id,autogen_message,expected_flotorch_event",
        AUTOGEN_TO_FLOTORCH_TEST_DATA,
        ids=[data[0] for data in AUTOGEN_TO_FLOTORCH_TEST_DATA]
    )
    def test_autogen_to_flotorch_conversion(self, session_instance, test_id,
                                            autogen_message,
                                            expected_flotorch_event):
        """Test conversion from AutoGen messages to Flotorch events."""
        result = session_instance._autogen_to_flotorch_event(autogen_message)
        assert result == expected_flotorch_event


class TestFlotorchToAutogenConversion:
    """Test _flotorch_to_autogen_message method."""

    @pytest.mark.parametrize(
        "test_id,flotorch_event,expected_autogen_message",
        FLOTORCH_TO_AUTOGEN_TEST_DATA,
        ids=[data[0] for data in FLOTORCH_TO_AUTOGEN_TEST_DATA]
    )
    def test_flotorch_to_autogen_conversion(self, session_instance, test_id,
                                            flotorch_event,
                                            expected_autogen_message):
        """Test conversion from Flotorch events to AutoGen messages."""
        result = session_instance._flotorch_to_autogen_message(flotorch_event)
        if expected_autogen_message is None:
            assert result is None
        else:
            assert result.content == expected_autogen_message.content
            # Check if source attribute exists before comparing
            if hasattr(result, 'source') and hasattr(expected_autogen_message, 'source'):
                assert result.source == expected_autogen_message.source


class TestAddMessage:
    """Test add_message method."""

    @pytest.mark.parametrize(
        "test_id,message,should_fail,expected_error",
        ADD_MESSAGE_TEST_DATA,
        ids=[data[0] for data in ADD_MESSAGE_TEST_DATA]
    )
    @pytest.mark.asyncio
    async def test_add_message_scenarios(self, session_instance_with_uid,
                                         test_id, message, should_fail,
                                         expected_error):
        """Test add_message with various scenarios."""
        if should_fail:
            session_instance_with_uid.flotorch_session.add_event.side_effect = \
                expected_error("API Error")
            with pytest.raises(expected_error):
                await session_instance_with_uid.add_message(message)
        else:
            await session_instance_with_uid.add_message(message)
            session_instance_with_uid.flotorch_session.add_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_caches_message(self, session_instance_with_uid):
        """Test that add_message caches the message locally."""
        await session_instance_with_uid.add_message(SAMPLE_USER_MESSAGE)
        assert len(session_instance_with_uid._messages_cache) == 1
        assert session_instance_with_uid._messages_cache[0] == SAMPLE_USER_MESSAGE

    @pytest.mark.asyncio
    async def test_get_messages_respects_cache_limit(self, session_instance_with_uid):
        """Test that get_messages respects the cache limit."""
        session_instance_with_uid.recent_messages_max = 2
        
        # Add 3 messages
        for i in range(3):
            message = SAMPLE_USER_MESSAGE
            await session_instance_with_uid.add_message(message)
        
        # Cache should have all 3 messages
        assert len(session_instance_with_uid._messages_cache) == 3
        
        # But get_messages should only return the last 2
        messages = await session_instance_with_uid.get_messages()
        assert len(messages) == 2


class TestGetMessages:
    """Test get_messages method."""

    @pytest.mark.parametrize(
        "test_id,cache_messages,limit,expected_count",
        GET_MESSAGES_TEST_DATA,
        ids=[data[0] for data in GET_MESSAGES_TEST_DATA]
    )
    @pytest.mark.asyncio
    async def test_get_messages_scenarios(self, session_instance, test_id,
                                          cache_messages, limit, expected_count):
        """Test get_messages with various cache scenarios."""
        session_instance._messages_cache = cache_messages
        session_instance.recent_messages_max = limit
        
        messages = await session_instance.get_messages()
        assert len(messages) == expected_count

    @pytest.mark.asyncio
    async def test_get_messages_returns_copy(self, session_instance):
        """Test that get_messages returns a copy of the cache."""
        session_instance._messages_cache = [SAMPLE_USER_MESSAGE]
        
        messages1 = await session_instance.get_messages()
        messages2 = await session_instance.get_messages()
        
        assert messages1 == messages2
        assert messages1 is not messages2  # Different objects


class TestStateManagement:
    """Test state save and load functionality."""

    @pytest.mark.asyncio
    async def test_save_state_with_uid(self, session_instance):
        """Test save_state with uid."""
        session_instance.uid = "test-session-123"
        session_instance.base_url = "https://test.com"
        
        saved_state = await session_instance.save_state()
        expected_state = {
            "uid": "test-session-123",
            "base_url": "https://test.com",
            "recent_messages_max": 50,
            "provider": "flotorch.autogen.sessions.FlotorchAutogenSession"
        }
        assert saved_state == expected_state

    @pytest.mark.asyncio
    async def test_save_state_without_uid(self, session_instance):
        """Test save_state without uid."""
        session_instance.uid = None
        session_instance.base_url = "https://test.com"
        
        saved_state = await session_instance.save_state()
        expected_state = {
            "uid": None,
            "base_url": "https://test.com",
            "recent_messages_max": 50,
            "provider": "flotorch.autogen.sessions.FlotorchAutogenSession"
        }
        assert saved_state == expected_state

    @pytest.mark.asyncio
    async def test_load_state_valid(self, session_instance):
        """Test load_state with valid data."""
        state_data = {"uid": "test-session-123", "base_url": "https://test.com"}
        
        await session_instance.load_state(state_data)
        assert session_instance.uid == state_data["uid"]
        assert session_instance.base_url == state_data["base_url"]


class TestSessionLifecycle:
    """Test session lifecycle methods."""

    @pytest.mark.asyncio
    async def test_clear_messages(self, session_instance_with_uid):
        """Test that clear removes all messages."""
        session_instance_with_uid._messages_cache = [SAMPLE_USER_MESSAGE]
        
        await session_instance_with_uid.clear()
        assert len(session_instance_with_uid._messages_cache) == 0

    @pytest.mark.asyncio
    async def test_ensure_session_creates_new(self, session_instance):
        """Test that _ensure_session creates a new session when needed."""
        session_instance.uid = None
        session_instance.flotorch_session.create.return_value = {
            "uid": "new-session-123",
            "appName": "autogen_session_app",
            "userId": "autogen_user",
            "state": {},
            "createdAt": "2025-01-01T00:00:00.000Z",
            "updatedAt": "2025-01-01T00:00:00.000Z",
        }
        
        uid = await session_instance._ensure_session()
        assert uid == "new-session-123"
        assert session_instance.uid == "new-session-123"

    @pytest.mark.asyncio
    async def test_ensure_session_returns_existing(self, session_instance_with_uid):
        """Test that _ensure_session returns existing uid."""
        uid = await session_instance_with_uid._ensure_session()
        assert uid == session_instance_with_uid.uid


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_add_message_handles_api_errors(self, session_instance_with_uid):
        """Test that add_message handles API errors gracefully."""
        session_instance_with_uid.flotorch_session.add_event.side_effect = \
            Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            await session_instance_with_uid.add_message(SAMPLE_USER_MESSAGE)

    @pytest.mark.asyncio
    async def test_get_messages_handles_empty_cache(self, session_instance):
        """Test that get_messages handles empty cache gracefully."""
        session_instance._messages_cache = []
        messages = await session_instance.get_messages()
        assert messages == []


class TestFlotorchAutogenSessionConfig:
    """Test FlotorchAutogenSessionConfig class."""

    def test_config_creation(self):
        """Test FlotorchAutogenSessionConfig creation."""
        config = FlotorchAutogenSessionConfig(
            uid="test-uid",
            base_url="https://test.com"
        )
        assert config.uid == "test-uid"
        assert config.base_url == "https://test.com"
        assert config.provider == "flotorch.autogen.sessions.FlotorchAutogenSession"

    def test_config_with_defaults(self):
        """Test FlotorchAutogenSessionConfig with defaults."""
        config = FlotorchAutogenSessionConfig()
        assert config.uid is None
        assert config.base_url is None
        assert config.recent_messages_max == 50
        assert config.provider == "flotorch.autogen.sessions.FlotorchAutogenSession"