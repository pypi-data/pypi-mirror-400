"""Test cases for FlotorchLangChainSession class."""

import pytest
from unittest.mock import patch

from flotorch.langchain.tests.test_data.session_test_data import (
    LOAD_MEMORY_VARIABLES_TEST_DATA,
    SAVE_CONTEXT_TEST_DATA,
    CLEAR_TEST_DATA,
    EXTRACT_TEXT_LINES_TEST_DATA,
)


class TestFlotorchLangChainSessionInit:
    """Test initialization."""

    @patch('flotorch.langchain.session.FlotorchSession')
    def test_init_custom_parameters(self, mock_flotorch_session):
        from flotorch.langchain.session import FlotorchLangChainSession
        
        instance = FlotorchLangChainSession(
            api_key="key-789",
            base_url="https://test.cloud",
            app_name="app",
            user_id="user"
        )
        
        assert instance.api_key == "key-789"
        assert instance.base_url == "https://test.cloud"
        assert instance.user_id == "user"
        assert instance.memory_key == "history"
        assert instance._session_id is None

    @patch('flotorch.langchain.session.FlotorchSession')
    def test_init_defaults(self, mock_flotorch_session):
        from flotorch.langchain.session import FlotorchLangChainSession
        
        instance = FlotorchLangChainSession(
            api_key="key",
            base_url="https://test.cloud"
        )
        
        assert instance.user_id == "default_user"
        assert instance.memory_key == "history"


class TestFlotorchLangChainSessionMemoryVariables:
    """Test memory_variables property."""

    def test_memory_variables(self, session_instance):
        assert session_instance.memory_variables == ["history"]


class TestFlotorchLangChainSessionLoadMemoryVariables:
    """Test load_memory_variables."""

    @pytest.mark.parametrize("test_name,inputs,events,expected", LOAD_MEMORY_VARIABLES_TEST_DATA)
    def test_load_memory_parametrized(
        self,
        session_instance_with_id,
        mock_session_client,
        test_name,
        inputs,
        events,
        expected,
        capsys
    ):
        mock_session_client.get_events.return_value = events
        result = session_instance_with_id.load_memory_variables(inputs)
        
        assert result == {"history": expected}

    def test_load_memory_creates_session(self, session_instance, mock_session_client):
        session_instance._session_id = None
        mock_session_client.get_events.return_value = []
        
        session_instance.load_memory_variables({"input": "Test"})
        
        mock_session_client.create.assert_called_once()

    def test_load_memory_reverses_events(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        mock_session_client.get_events.return_value = [
            {"author": "assistant", "content": {"parts": [{"text": "Second"}]}},
            {"author": "user", "content": {"parts": [{"text": "First"}]}},
        ]
        
        result = session_instance_with_id.load_memory_variables({"input": "Test"})
        
        assert result["history"] == "user: First\nassistant: Second"

    def test_load_memory_handles_errors(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        mock_session_client.get_events.side_effect = Exception("Error")
        
        result = session_instance_with_id.load_memory_variables({"input": "Test"})
        
        assert result == {"history": ""}


class TestFlotorchLangChainSessionSaveContext:
    """Test save_context."""

    @pytest.mark.parametrize("test_name,inputs,outputs", SAVE_CONTEXT_TEST_DATA)
    def test_save_context_parametrized(
        self,
        session_instance_with_id,
        mock_session_client,
        test_name,
        inputs,
        outputs,
        capsys
    ):
        session_instance_with_id.save_context(inputs, outputs)
        
        assert mock_session_client.add_event.call_count == 2
        user_call, assistant_call = mock_session_client.add_event.call_args_list
        
        assert user_call.kwargs["author"] == "user"
        assert assistant_call.kwargs["author"] == "assistant"
        assert assistant_call.kwargs["turn_complete"] is True

    def test_save_context_creates_session(
        self,
        session_instance,
        mock_session_client
    ):
        session_instance._session_id = None
        session_instance.save_context({"input": "Test"}, {"output": "Response"})
        
        mock_session_client.create.assert_called_once()

    def test_save_context_unique_invocation_ids(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        session_instance_with_id.save_context({"input": "Test"}, {"output": "Resp"})
        
        user_call, assistant_call = mock_session_client.add_event.call_args_list
        
        assert user_call.kwargs["invocation_id"] != assistant_call.kwargs["invocation_id"]

    def test_save_context_handles_errors(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        mock_session_client.add_event.side_effect = Exception("Error")
        
        session_instance_with_id.save_context({"input": "Test"}, {"output": "Resp"})


class TestFlotorchLangChainSessionClear:
    """Test clear."""

    @pytest.mark.parametrize("test_name,session_id,should_delete", CLEAR_TEST_DATA)
    def test_clear_parametrized(
        self,
        session_instance,
        mock_session_client,
        test_name,
        session_id,
        should_delete
    ):
        session_instance._session_id = session_id
        session_instance.clear()
        
        if should_delete:
            mock_session_client.delete.assert_called_once_with(session_id)
        else:
            mock_session_client.delete.assert_not_called()
        
        assert session_instance._session_id is None

    def test_clear_handles_errors(self, session_instance_with_id, mock_session_client):
        mock_session_client.delete.side_effect = Exception("Error")
        session_instance_with_id.clear()
        
        assert session_instance_with_id._session_id is None

    def test_clear_multiple_calls(self, session_instance_with_id, mock_session_client):
        session_instance_with_id.clear()
        session_instance_with_id.clear()
        
        assert mock_session_client.delete.call_count == 1


class TestFlotorchLangChainSessionEnsureSession:
    """Test _ensure_session."""

    def test_ensure_session_creates_new(self, session_instance, mock_session_client):
        session_instance._session_id = None
        
        session_id = session_instance._ensure_session()
        
        mock_session_client.create.assert_called_once()
        assert session_id == "test-session-456"

    def test_ensure_session_reuses_existing(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        mock_session_client.get.return_value = {"uid": "existing-session-456"}
        
        session_id = session_instance_with_id._ensure_session()
        
        mock_session_client.get.assert_called_once()
        mock_session_client.create.assert_not_called()
        assert session_id == "existing-session-456"

    def test_ensure_session_handles_invalid(
        self,
        session_instance_with_id,
        mock_session_client
    ):
        mock_session_client.get.side_effect = Exception("Not found")
        
        session_id = session_instance_with_id._ensure_session()
        
        mock_session_client.create.assert_called_once()
        assert session_id == "test-session-456"


class TestFlotorchLangChainSessionExtractTextLines:
    """Test _extract_text_lines_from_events."""

    @pytest.mark.parametrize("test_name,events,expected", EXTRACT_TEXT_LINES_TEST_DATA)
    def test_extract_parametrized(self, test_name, events, expected, capsys):
        from flotorch.langchain.session import FlotorchLangChainSession
        
        result = FlotorchLangChainSession._extract_text_lines_from_events(events)
        
        assert result == expected

    def test_extract_multiple_parts(self):
        from flotorch.langchain.session import FlotorchLangChainSession
        
        events = [
            {
                "author": "user",
                "content": {
                    "parts": [{"text": "P1"}, {"text": "P2"}]
                }
            }
        ]
        
        result = FlotorchLangChainSession._extract_text_lines_from_events(events)
        
        assert result == ["user: P1", "user: P2"]

    def test_extract_strips_whitespace(self):
        from flotorch.langchain.session import FlotorchLangChainSession
        
        events = [{"author": "user", "text": "  Text  "}]
        result = FlotorchLangChainSession._extract_text_lines_from_events(events)
        
        assert result == ["user: Text"]

