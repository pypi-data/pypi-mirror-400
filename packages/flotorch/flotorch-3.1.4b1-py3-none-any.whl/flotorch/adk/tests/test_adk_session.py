"""Test cases for FlotorchADKSession class."""

import time
from unittest.mock import patch

import pytest
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.sessions.session import Session
from google.genai import types

from flotorch.adk.tests.test_data.session_test_data import (
    CREATE_SESSION_TEST_DATA,
    DELETE_SESSION_TEST_DATA,
    GET_SESSION_TEST_DATA,
    LIST_SESSIONS_TEST_DATA,
    APPEND_EVENT_TEST_DATA,
)


class TestFlotorchADKSessionInit:
    """Test constructor initialization."""
    
    @patch('flotorch.adk.sessions.FlotorchSession')
    def test_init_with_custom_parameters(self, mock_flotorch_session):
        """Test initialization with custom parameters."""
        from flotorch.adk.sessions import FlotorchADKSession
        
        instance = FlotorchADKSession(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com"
        )
               
        assert instance._flotorch_session is not None
        assert isinstance(instance.user_state, dict)
        assert isinstance(instance.app_state, dict)
               
        mock_flotorch_session.assert_called_once_with(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com"
        )
    
    @patch('flotorch.adk.sessions.FlotorchSession')
    def test_init_with_defaults(self, mock_flotorch_session):
        """Test initialization with required parameters."""
        from flotorch.adk.sessions import FlotorchADKSession
        
        instance = FlotorchADKSession(
            api_key="test-key",
            base_url="http://test.com"
        )
        
        assert instance._flotorch_session is not None
        assert isinstance(instance.user_state, dict)
        assert isinstance(instance.app_state, dict)
        
        mock_flotorch_session.assert_called_once_with(
            api_key="test-key",
            base_url="http://test.com"
        )


class TestFlotorchADKSessionCreate:
    """Test create_session function."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_name,session_id,state,should_fail,expected_exception",
        CREATE_SESSION_TEST_DATA
    )
    async def test_create_session_parametrized(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        session_id,
        state,
        should_fail,
        expected_exception
    ):
        """Test create_session with various scenarios."""
        if should_fail:
            mock_sdk_session.create.side_effect = expected_exception("Create failed")
            with pytest.raises(expected_exception):
                await adk_session_with_mock.create_session(
                    app_name=test_data["app_name"],
                    user_id=test_data["user_id"],
                    session_id=session_id,
                    state=state
                )
        else:
            
            mock_sdk_session.create.return_value = {
                "uid": session_id or "auto-generated-id",
                "appName": test_data["app_name"],
                "userId": test_data["user_id"],
                "state": state,
                "last_update_time": 1234567890
            }
            
            session = await adk_session_with_mock.create_session(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"],
                session_id=session_id,
                state=state
            )
            
            assert isinstance(session, Session)
            assert session.app_name == test_data["app_name"]
            mock_sdk_session.create.assert_called_once()
    
    def test_create_session_generates_uuid_when_none(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test create_session generates UUID when session_id is None."""
        
        mock_sdk_session.create.return_value = {
            "uid": "auto-gen-uuid",
            "appName": test_data["app_name"],
            "userId": test_data["user_id"],
            "state": {},
            "last_update_time": 1234567890
        }
        
        session = adk_session_with_mock.create_session_sync(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"]
        )
        
        assert session.id is not None
        assert len(session.id) == 36  
    
    @pytest.mark.asyncio
    async def test_create_session_with_empty_state(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test create_session with empty state dict."""
        mock_sdk_session.create.return_value = {
            "uid": "session-empty",
            "appName": test_data["app_name"],
            "userId": test_data["user_id"],
            "state": {},
            "last_update_time": 1234567890
        }
        
        session = await adk_session_with_mock.create_session(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"],
            state={}
        )
        
        assert session.state == {}
        mock_sdk_session.create.assert_called_once()


class TestFlotorchADKSessionGet:
    """Test get_session function."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_name,session_exists,events_count,has_state,should_fail,expected_exception",
        GET_SESSION_TEST_DATA
    )
    async def test_get_session_parametrized(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        session_exists,
        events_count,
        has_state,
        should_fail,
        expected_exception
    ):
        """Test get_session with various scenarios."""
        if should_fail:
            mock_sdk_session.get.side_effect = expected_exception("Get failed")
            with pytest.raises(expected_exception):
                await adk_session_with_mock.get_session(
                    app_name=test_data["app_name"],
                    user_id=test_data["user_id"],
                    session_id=test_data["session_id"]
                )
        elif not session_exists:
            mock_sdk_session.get.return_value = None
            
            session = await adk_session_with_mock.get_session(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"],
                session_id=test_data["session_id"]
            )
            
            assert session is None
        else:
            state = {"key": "value"} if has_state else {}
            
            mock_response = {
                "uid": test_data["session_id"],
                "appName": test_data["app_name"],
                "userId": test_data["user_id"],
                "state": state,
                "last_update_time": 1234567890
            }
            if events_count > 0:
                mock_response["events"] = [
                    {
                        "uid_event": f"e{i}",
                        "invocation_id": f"inv{i}",
                        "author": "user",
                        "timestamp": 1234567890.0 + i,
                        "content": {"role": "user", "parts": [{"text": f"message {i}"}]},
                        "actions": {}
                    }
                    for i in range(events_count)
                ]
            mock_sdk_session.get.return_value = mock_response
            
            session = await adk_session_with_mock.get_session(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"],
                session_id=test_data["session_id"]
            )
            
            assert isinstance(session, Session)
            assert len(session.events) == events_count
    
    @pytest.mark.asyncio
    async def test_get_session_returns_events_correctly(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test get_session correctly returns events."""
        # Create mock data directly (like Langgraph does)
        mock_sdk_session.get.return_value = {
            "uid": test_data["session_id"],
            "appName": test_data["app_name"],
            "userId": test_data["user_id"],
            "state": {},
            "last_update_time": 1234567890,
            "events": [
                {
                    "uid_event": f"e{i}",
                    "invocation_id": f"inv{i}",
                    "author": "user",
                    "timestamp": 1234567890.0 + i,
                    "content": {"role": "user", "parts": [{"text": f"message {i}"}]},
                    "actions": {}
                }
                for i in range(3)
            ]
        }
        
        session = await adk_session_with_mock.get_session(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"],
            session_id=test_data["session_id"]
        )
        
        assert len(session.events) == 3
        mock_sdk_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_session_with_state(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test get_session returns session with state."""
        test_state = {"key1": "value1", "key2": "value2"}
        # Create mock data directly (like Langgraph does)
        mock_sdk_session.get.return_value = {
            "uid": test_data["session_id"],
            "appName": test_data["app_name"],
            "userId": test_data["user_id"],
            "state": test_state,
            "last_update_time": 1234567890
        }
        
        session = await adk_session_with_mock.get_session(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"],
            session_id=test_data["session_id"]
        )
        
        assert session.state == test_state


class TestFlotorchADKSessionList:
    """Test list_sessions function."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_name,sessions_count,should_fail,expected_exception",
        LIST_SESSIONS_TEST_DATA
    )
    async def test_list_sessions_parametrized(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        sessions_count,
        should_fail,
        expected_exception
    ):
        """Test list_sessions with various scenarios."""
        if should_fail:
            mock_sdk_session.list.side_effect = expected_exception("List failed")
            with pytest.raises(expected_exception):
                await adk_session_with_mock.list_sessions(
                    app_name=test_data["app_name"],
                    user_id=test_data["user_id"]
                )
        else:
            
            mock_sdk_session.list.return_value = [
                {
                    "uid": f"session-{i}",
                    "appName": test_data["app_name"],
                    "userId": test_data["user_id"],
                    "state": {"index": i},
                    "last_update_time": 1234567890 + i
                }
                for i in range(sessions_count)
            ]
            
            response = await adk_session_with_mock.list_sessions(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"]
            )
            
            assert response is not None
            assert len(response.sessions) == sessions_count
    
    @pytest.mark.asyncio
    async def test_list_sessions_returns_empty(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test list_sessions returns empty list when no sessions exist."""
        mock_sdk_session.list.return_value = []
        
        response = await adk_session_with_mock.list_sessions(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"]
        )
        
        assert len(response.sessions) == 0
        mock_sdk_session.list.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_sessions_returns_correct_count(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test list_sessions returns correct number of sessions."""
        
        mock_sdk_session.list.return_value = [
            {
                "uid": f"session-{i}",
                "appName": test_data["app_name"],
                "userId": test_data["user_id"],
                "state": {"index": i},
                "last_update_time": 1234567890 + i
            }
            for i in range(5)
        ]
        
        response = await adk_session_with_mock.list_sessions(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"]
        )
        
        assert len(response.sessions) == 5
        assert all(isinstance(s, Session) for s in response.sessions)


class TestFlotorchADKSessionDelete:
    """Test delete_session function."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_name,session_exists,should_fail,expected_exception",
        DELETE_SESSION_TEST_DATA
    )
    async def test_delete_session_parametrized(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        session_exists,
        should_fail,
        expected_exception
    ):
        """Test delete_session with various scenarios."""
        if not session_exists:
            mock_sdk_session.get.return_value = None
            
            await adk_session_with_mock.delete_session(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"],
                session_id=test_data["session_id"]
            )
            
            mock_sdk_session.get.assert_called_once()
        elif should_fail:
            mock_sdk_session.get.return_value = {
                "uid": test_data["session_id"],
                "state": {},
                "last_update_time": 1
            }
            mock_sdk_session.delete.side_effect = expected_exception("Delete failed")
            
            with pytest.raises(expected_exception):
                await adk_session_with_mock.delete_session(
                    app_name=test_data["app_name"],
                    user_id=test_data["user_id"],
                    session_id=test_data["session_id"]
                )
        else:
            mock_sdk_session.get.return_value = {
                "uid": test_data["session_id"],
                "state": {},
                "last_update_time": 1
            }
            mock_sdk_session.delete.return_value = {"status": "deleted"}
            
            await adk_session_with_mock.delete_session(
                app_name=test_data["app_name"],
                user_id=test_data["user_id"],
                session_id=test_data["session_id"]
            )
            
            mock_sdk_session.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_session_verifies_existence_first(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test delete_session checks if session exists before deleting."""
        mock_sdk_session.get.return_value = {
            "uid": test_data["session_id"],
            "state": {},
            "last_update_time": 1
        }
        mock_sdk_session.delete.return_value = {"status": "deleted"}
        
        await adk_session_with_mock.delete_session(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"],
            session_id=test_data["session_id"]
        )
        
        
        assert mock_sdk_session.get.call_count == 1
        assert mock_sdk_session.delete.call_count == 1


class TestFlotorchADKSessionAppendEvent:
    """Test append_event function."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_name,session_exists,has_content,has_state_delta,state_delta,should_fail,expected_exception",
        APPEND_EVENT_TEST_DATA
    )
    async def test_append_event_parametrized(
        self,
        adk_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        session_exists,
        has_content,
        has_state_delta,
        state_delta,
        should_fail,
        expected_exception
    ):
        """Test append_event with various scenarios."""
        if not session_exists:
            mock_sdk_session.get.return_value = None
        else:
            mock_sdk_session.get.return_value = {
                "uid": test_data["session_id"],
                "state": {},
                "last_update_time": 1
            }
        
        if should_fail:
            mock_sdk_session.add_event.side_effect = expected_exception("Add event failed")
        else:
            
            mock_sdk_session.add_event.return_value = {
                "uid": "e1",
                "invocationId": "inv1",
                "author": "user"
            }
        
        
        session = Session(
            app_name=test_data["app_name"],
            user_id=test_data["user_id"],
            id=test_data["session_id"],
            state={},
            last_update_time=1
        )
        
        event_kwargs = {
            "id": "e1",
            "invocation_id": "inv",
            "author": "user",
            "timestamp": time.time()
        }
        
        if has_content:
            event_kwargs["content"] = types.Content(
                role="user",
                parts=[types.Part(text="Test message")]
            )
        
        if has_state_delta:
            event_kwargs["actions"] = EventActions(state_delta=state_delta)
        
        event = Event(**event_kwargs)
        
        if should_fail:
            with pytest.raises(expected_exception):
                await adk_session_with_mock.append_event(session, event)
        else:
            returned_event = await adk_session_with_mock.append_event(session, event)
            
            assert returned_event.id == "e1"
            
            if has_state_delta:
                for key, value in state_delta.items():
                    if key.startswith("app:"):
                        state_key = key[4:]
                        app_name = test_data["app_name"]
                        assert app_name in adk_session_with_mock.app_state
                        app_state = adk_session_with_mock.app_state
                        assert app_state[app_name][state_key] == value
                    elif key.startswith("user:"):
                        state_key = key[5:]
                        app_name = test_data["app_name"]
                        user_id = test_data["user_id"]
                        assert app_name in adk_session_with_mock.user_state
                        user_state = adk_session_with_mock.user_state
                        assert user_id in user_state[app_name]
                        assert user_state[app_name][user_id][state_key] == value
