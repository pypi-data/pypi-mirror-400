"""Test cases for FlotorchCrewAISession class."""

import pytest
from unittest.mock import  patch

from flotorch.crewai.tests.test_data.sessions_test_data import (
    SAVE_FUNCTION_TEST_DATA,
    SEARCH_FUNCTION_TEST_DATA
)


class TestFlotorchCrewAISessionInit:
    """Test constructor initialization."""

    @patch('flotorch.crewai.sessions.FlotorchSession')
    def test_init_with_custom_parameters(self, mock_flotorch_session):
        """Test initialization with custom parameters."""
        from flotorch.crewai.sessions import FlotorchCrewAISession
        
        instance = FlotorchCrewAISession(
            base_url="https://custom.flotorch.com",
            api_key="custom-key-123",
            app_name="my_app",
            user_id="user_123"
        )
        
        assert instance._base_url == "https://custom.flotorch.com"
        assert instance._api_key == "custom-key-123"
        assert instance._app_name == "my_app"
        assert instance._user_id == "user_123"
        assert instance._session_id is None
        
        mock_flotorch_session.assert_called_once_with(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com"
        )

    @patch('flotorch.crewai.sessions.FlotorchSession')
    def test_init_with_defaults(self, mock_flotorch_session):
        """Test initialization with default parameters."""
        from flotorch.crewai.sessions import FlotorchCrewAISession
        
        instance = FlotorchCrewAISession()
        
        assert instance._base_url is None
        assert instance._api_key is None
        assert instance._app_name == "crewai_session_app"
        assert instance._user_id == "crewai_user"
        assert instance._session_id is None


class TestFlotorchCrewAISessionSave:
    """Test save function."""

    @pytest.mark.parametrize(
        "test_name,value,metadata,should_fail,expected_exception",
        SAVE_FUNCTION_TEST_DATA
    )
    def test_save_parametrized(
        self,
        session_instance,
        mock_session_client,
        test_name,
        value,
        metadata,
        should_fail,
        expected_exception
    ):
        """Test save with various scenarios."""
        if should_fail:
            mock_session_client.add_event.side_effect = Exception("API Error")
            with pytest.raises(expected_exception):
                session_instance.save(value, metadata)
        else:
            session_instance.save(value, metadata)
            
            mock_session_client.add_event.assert_called_once()
            call_args = mock_session_client.add_event.call_args
            
            assert call_args.kwargs["author"] == "user"
            assert call_args.kwargs["content"]["parts"][0]["text"] == str(value)
            
            if metadata and isinstance(metadata, dict):
                assert call_args.kwargs["grounding_metadata"] == metadata
            else:
                assert call_args.kwargs["grounding_metadata"] is None

    def test_save_creates_session_when_none(
        self,
        session_instance,
        mock_session_client
    ):
        """Test save creates new session when session_id is None."""
        session_instance._session_id = None
        session_instance.save("test", {"key": "value"})
        
        mock_session_client.create.assert_called_once_with(
            app_name="test_app",
            user_id="test_user"
        )
        mock_session_client.add_event.assert_called_once()

    def test_save_reuses_existing_session(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test save reuses existing session_id if valid."""
        session_instance_with_id.save("test", {"key": "value"})
        
        mock_session_client.get.assert_called_once_with(
            uid="existing-session-123"
        )
        mock_session_client.create.assert_not_called()
        
        call_args = mock_session_client.add_event.call_args
        assert call_args.kwargs["uid"] == "existing-session-123"

    def test_save_creates_new_on_invalid_session(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test save creates new session if existing is invalid."""
        mock_session_client.get.side_effect = Exception("Session not found")
        
        session_instance_with_id.save("test", {"key": "value"})
        
        mock_session_client.get.assert_called_once()
        mock_session_client.create.assert_called_once()

    def test_save_generates_unique_invocation_ids(
        self,
        session_instance,
        mock_session_client
    ):
        """Test each save generates unique invocation_id."""
        session_instance.save("first", {})
        first_invocation = mock_session_client.add_event.call_args.kwargs[
            "invocation_id"
        ]
        
        mock_session_client.reset_mock()
        
        session_instance.save("second", {})
        second_invocation = mock_session_client.add_event.call_args.kwargs[
            "invocation_id"
        ]
        
        assert first_invocation != second_invocation


class TestFlotorchCrewAISessionSearch:
    """Test search function."""

    @pytest.mark.parametrize(
        "test_name,query,limit,events,expected_count,should_fail,expected_exception",
        SEARCH_FUNCTION_TEST_DATA
    )
    def test_search_parametrized(
        self,
        session_instance_with_id,
        mock_session_client,
        test_name,
        query,
        limit,
        events,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test search with various scenarios."""
        if should_fail:
            mock_session_client.get_events.side_effect = Exception("API Error")
            with pytest.raises(
                expected_exception,
                match="Failed to fetch session events"
            ):
                session_instance_with_id.search(query, limit)
        else:
            mock_session_client.get_events.return_value = events
            results = session_instance_with_id.search(query, limit)
            
            assert len(results) == expected_count
            
            if expected_count > 0:
                for result in results:
                    assert "content" in result
                    assert "metadata" in result
                    assert isinstance(result["content"], str)
                    assert isinstance(result["metadata"], dict)

    def test_search_without_session_id(
        self,
        session_instance,
        mock_session_client
    ):
        """Test search returns empty when session_id is None."""
        session_instance._session_id = None
        results = session_instance.search("test query", 10)
        
        assert results == []
        mock_session_client.get_events.assert_not_called()

    def test_search_calls_get_events_correctly(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search calls get_events with correct session_id."""
        mock_session_client.get_events.return_value = []
        session_instance_with_id.search("test", 10)
        
        mock_session_client.get_events.assert_called_once_with(
            "existing-session-123"
        )

    def test_search_extracts_content_and_metadata(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search correctly extracts event data."""
        mock_session_client.get_events.return_value = [
            {
                "content": {"parts": [{"text": "Test message"}]},
                "groundingMetadata": {"key": "value"}
            }
        ]
        
        results = session_instance_with_id.search("test", 10)
        
        assert len(results) == 1
        assert results[0]["content"] == "Test message"
        assert results[0]["metadata"] == {"key": "value"}

    def test_search_handles_final_answer_format(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search extracts text after Final Answer marker."""
        mock_session_client.get_events.return_value = [
            {
                "content": {
                    "parts": [{
                        "text": "Thought: thinking\nFinal Answer: Result"
                    }]
                },
                "groundingMetadata": {}
            }
        ]
        
        results = session_instance_with_id.search("test", 10)
        
        assert len(results) == 1
        assert results[0]["content"] == "Result"

    def test_search_handles_direct_text_field(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search handles events with direct text field."""
        mock_session_client.get_events.return_value = [
            {"text": "Direct text", "groundingMetadata": {"type": "direct"}}
        ]
        
        results = session_instance_with_id.search("test", 10)
        
        assert len(results) == 1
        assert results[0]["content"] == "Direct text"
        assert results[0]["metadata"] == {"type": "direct"}

    def test_search_skips_events_without_text(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search skips events with no extractable text."""
        mock_session_client.get_events.return_value = [
            {"content": {"parts": [{"text": "Valid"}]}},
            {"content": {"parts": []}},
            {"content": {"parts": [{"data": "no text"}]}},
            {"content": {}},
            {}
        ]
        
        results = session_instance_with_id.search("test", 10)
        
        assert len(results) == 1
        assert results[0]["content"] == "Valid"

    def test_search_handles_missing_metadata(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test search handles events without groundingMetadata."""
        mock_session_client.get_events.return_value = [
            {"content": {"parts": [{"text": "No metadata"}]}}
        ]
        
        results = session_instance_with_id.search("test", 10)
        
        assert len(results) == 1
        assert results[0]["metadata"] == {}


class TestFlotorchCrewAISessionReset:
    """Test reset function."""

    def test_reset_deletes_and_clears(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test reset calls delete and clears session_id."""
        assert session_instance_with_id._session_id == "existing-session-123"
        
        session_instance_with_id.reset()
        
        mock_session_client.delete.assert_called_once_with(
            "existing-session-123"
        )
        assert session_instance_with_id._session_id is None

    def test_reset_without_session_id(
        self,
        session_instance,
        mock_session_client
    ):
        """Test reset does nothing when session_id is None."""
        session_instance._session_id = None
        
        session_instance.reset()
        
        mock_session_client.delete.assert_not_called()
        assert session_instance._session_id is None

    def test_reset_handles_delete_failure(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test reset clears session_id even if delete fails."""
        mock_session_client.delete.side_effect = Exception("Delete failed")
        
        session_instance_with_id.reset()
        
        mock_session_client.delete.assert_called_once()
        assert session_instance_with_id._session_id is None

    def test_reset_multiple_calls(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        """Test reset can be called multiple times safely."""
        session_instance_with_id.reset()
        assert session_instance_with_id._session_id is None
        
        mock_session_client.reset_mock()
        
        session_instance_with_id.reset()
        mock_session_client.delete.assert_not_called()
        assert session_instance_with_id._session_id is None
