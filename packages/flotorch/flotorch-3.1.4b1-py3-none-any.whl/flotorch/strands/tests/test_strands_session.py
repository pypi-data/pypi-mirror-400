"""Test cases for FlotorchStrandsSession class."""

import os
import pytest
from unittest.mock import patch, Mock

from flotorch.sdk.utils.http_utils import APIError
from flotorch.strands.tests.test_data.session_test_data import (
    CREATE_SESSION_TEST_DATA,
    READ_SESSION_TEST_DATA,
    CREATE_AGENT_TEST_DATA,
    READ_AGENT_TEST_DATA,
    UPDATE_AGENT_TEST_DATA,
    CREATE_MESSAGE_TEST_DATA,
    READ_MESSAGE_TEST_DATA,
    UPDATE_MESSAGE_TEST_DATA,
    LIST_MESSAGES_TEST_DATA
)


class TestFlotorchStrandsSessionInit:
    """Test constructor initialization."""

    @patch('flotorch.strands.session.FlotorchSession')
    def test_init_with_custom_parameters(self, mock_flotorch_session):
        """Test initialization with custom parameters."""
        from flotorch.strands.session import FlotorchStrandsSession
        instance = FlotorchStrandsSession(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com",
            app_name="my_strands_app", user_id="user_456"
        )
        assert (instance.api_key == "custom-key-123" and
                instance.base_url == "https://custom.flotorch.com" and
                instance.app_name == "my_strands_app" and
                instance.user_id == "user_456")
        mock_flotorch_session.assert_called_once_with(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com"
        )

    @patch('flotorch.strands.session.FlotorchSession')
    @patch.dict('os.environ', {'FLOTORCH_API_KEY': '',
                'FLOTORCH_BASE_URL': ''}, clear=False)
    def test_init_missing_credentials(self, mock_flotorch_session):
        """Test initialization fails without credentials."""
        from flotorch.strands.session import FlotorchStrandsSession
        with pytest.raises(ValueError,
                           match="FLOTORCH_API_KEY and "
                           "FLOTORCH_BASE_URL are required"):
            FlotorchStrandsSession(api_key=None, base_url=None,
                                   app_name="test_app",
                                   user_id="test_user")


class TestFlotorchStrandsSessionCreateSession:
    """Test create_session function."""

    @pytest.mark.parametrize(
        "test_name,has_custom_state,should_fail,expected_exception",
        CREATE_SESSION_TEST_DATA
    )
    def test_create_session_parametrized(
        self,
        strands_session,
        mock_session_client,
        mock_strands_session_obj,
        test_name,
        has_custom_state,
        should_fail,
        expected_exception
    ):
        """Test create_session with various scenarios."""
        if has_custom_state:
            custom_state = {"custom_key": "custom_value"}
            result = strands_session.create_session(
                mock_strands_session_obj, state=custom_state
            )
            assert (mock_session_client.create.call_args.kwargs["state"]
                    == custom_state)
        else:
            result = strands_session.create_session(
                mock_strands_session_obj
            )
            assert ("session_type" in
                    mock_session_client.create.call_args.kwargs["state"])
        mock_session_client.create.assert_called_once()
        assert result == mock_strands_session_obj

    def test_create_session_calls_sdk_correctly(
        self,
        strands_session,
        mock_session_client,
        mock_strands_session_obj,
        test_data
    ):
        """Test create_session calls SDK correctly."""
        strands_session.create_session(mock_strands_session_obj)
        mock_session_client.create.assert_called_once()
        call_args = mock_session_client.create.call_args
        assert (call_args.kwargs["app_name"] == test_data["app_name"] and
                call_args.kwargs["user_id"] == test_data["user_id"] and
                call_args.kwargs["uid"] ==
                mock_strands_session_obj.session_id)


class TestFlotorchStrandsSessionReadSession:
    """Test read_session function."""

    @pytest.mark.parametrize(
        "test_name,session_exists,should_fail,expected_exception",
        READ_SESSION_TEST_DATA
    )
    def test_read_session_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        session_exists,
        should_fail,
        expected_exception
    ):
        """Test read_session with various scenarios."""
        if not session_exists:
            mock_session_client.get.side_effect = APIError(
                status_code=404, message="Session not found"
            )
            result = strands_session.read_session(test_data["session_id"])
            assert result is None
        else:
            session_mock = Mock()
            session_mock.uid = test_data["session_id"]
            mock_session_client.get.return_value = session_mock
            result = strands_session.read_session(test_data["session_id"])
            assert result is not None

    def test_read_session_handles_404_gracefully(
        self, strands_session, mock_session_client, test_data
    ):
        """Test read_session handles 404 errors."""
        mock_session_client.get.side_effect = APIError(
            status_code=404, message="Session not found"
        )
        result = strands_session.read_session(test_data["session_id"])
        assert result is None
        mock_session_client.get.assert_called_once()

    def test_read_session_returns_none_when_no_data(
        self, strands_session, mock_session_client, test_data
    ):
        """Test read_session returns None when get returns falsy."""
        mock_session_client.get.return_value = None
        result = strands_session.read_session(test_data["session_id"])
        assert result is None

    def test_create_session_error_returns_session(
        self, strands_session, mock_session_client,
        mock_strands_session_obj
    ):
        """Test create_session returns session on error."""
        mock_session_client.create.side_effect = Exception("API Error")
        result = strands_session.create_session(mock_strands_session_obj)
        assert result == mock_strands_session_obj


class TestFlotorchStrandsSessionCreateAgent:
    """Test create_agent function."""

    @pytest.mark.parametrize(
        "test_name,agent_id,has_state,agent_type,"
        "should_fail,expected_exception",
        CREATE_AGENT_TEST_DATA
    )
    def test_create_agent_parametrized(
        self,
        strands_session,
        mock_session_client,
        mock_strands_agent,
        test_data,
        test_name,
        agent_id,
        has_state,
        agent_type,
        should_fail,
        expected_exception
    ):
        """Test create_agent with various scenarios."""
        mock_strands_agent.agent_id = agent_id
        strands_session.create_agent(test_data["session_id"],
                                      mock_strands_agent,
                                      agent_type=agent_type)
        mock_session_client.add_event.assert_called_once()
        call_args = mock_session_client.add_event.call_args
        assert (call_args.kwargs["uid"] == test_data["session_id"] and
                call_args.kwargs["author"] == "system")
        agent_data = call_args.kwargs["content"]["parts"][0]
        assert (agent_data["type"] == agent_type and
                agent_data["agent_id"] == agent_id)

    def test_create_agent_stores_conversation_state(
        self, strands_session, mock_session_client,
        mock_strands_agent, test_data
    ):
        """Test create_agent stores conversation state."""
        strands_session.create_agent(test_data["session_id"],
                                      mock_strands_agent)
        call_args = mock_session_client.add_event.call_args
        agent_data = call_args.kwargs["content"]["parts"][0]
        assert ("conversation_manager_state" in agent_data and
                agent_data["conversation_manager_state"] ==
                mock_strands_agent.conversation_manager_state)


class TestFlotorchStrandsSessionReadAgent:
    """Test read_agent function."""

    @pytest.mark.parametrize(
        "test_name,agent_exists,events_count,"
        "should_fail,expected_exception",
        READ_AGENT_TEST_DATA
    )
    def test_read_agent_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        agent_exists,
        events_count,
        should_fail,
        expected_exception
    ):
        """Test read_agent with various scenarios."""
        session_mock = Mock()
        session_mock.uid = test_data["session_id"]
        if events_count == 0 or not agent_exists:
            session_mock.events = []
            mock_session_client.get.return_value = session_mock
            result = strands_session.read_agent(test_data["session_id"],
                                                 test_data["agent_id"])
            assert result is None
        else:
            agent_event = Mock()
            agent_event.author = "system"
            content = Mock()
            content.parts = [{
                "type": "agent_creation",
                "agent_id": test_data["agent_id"],
                "state": {},
                "conversation_manager_state": {"removed_message_count": 0}
            }]
            agent_event.content = content
            session_mock.events = [agent_event]
            mock_session_client.get.return_value = session_mock
            result = strands_session.read_agent(test_data["session_id"],
                                                 test_data["agent_id"])
            assert (result is not None and
                    result.agent_id == test_data["agent_id"])

    def test_read_agent_returns_latest_state(
        self, strands_session, mock_session_client, test_data
    ):
        """Test read_agent returns most recent agent state."""
        session_mock = Mock()
        event1 = Mock()
        event1.author = "system"
        content1 = Mock()
        content1.parts = [{
            "type": "agent_creation",
            "agent_id": test_data["agent_id"],
            "state": {"step": 1},
            "conversation_manager_state": {"removed_message_count": 0}
        }]
        event1.content = content1
        event2 = Mock()
        event2.author = "system"
        content2 = Mock()
        content2.parts = [{
            "type": "agent_update",
            "agent_id": test_data["agent_id"],
            "state": {"step": 2},
            "conversation_manager_state": {"removed_message_count": 1}
        }]
        event2.content = content2
        session_mock.events = [event1, event2]
        mock_session_client.get.return_value = session_mock
        result = strands_session.read_agent(test_data["session_id"],
                                             test_data["agent_id"])
        assert result is not None and result.state == {"step": 2}


class TestFlotorchStrandsSessionUpdateAgent:
    """Test update_agent function."""

    @pytest.mark.parametrize(
        "test_name,agent_id,has_new_state,should_fail,expected_exception",
        UPDATE_AGENT_TEST_DATA
    )
    def test_update_agent_parametrized(
        self,
        strands_session,
        mock_session_client,
        mock_strands_agent,
        test_data,
        test_name,
        agent_id,
        has_new_state,
        should_fail,
        expected_exception
    ):
        """Test update_agent with various scenarios."""
        mock_strands_agent.agent_id = agent_id
        if has_new_state:
            mock_strands_agent.state = {"new_key": "new_value"}
        strands_session.update_agent(test_data["session_id"],
                                      mock_strands_agent)
        mock_session_client.add_event.assert_called_once()
        call_args = mock_session_client.add_event.call_args
        assert (call_args.kwargs["uid"] == test_data["session_id"] and
                call_args.kwargs["author"] == "system")
        agent_data = call_args.kwargs["content"]["parts"][0]
        assert (agent_data["type"] == "agent_update" and
                agent_data["agent_id"] == agent_id)

    def test_update_agent_with_custom_type(
        self, strands_session, mock_session_client,
        mock_strands_agent, test_data
    ):
        """Test update_agent with custom agent_type."""
        strands_session.update_agent(test_data["session_id"],
                                      mock_strands_agent,
                                      agent_type="custom_update")
        call_args = mock_session_client.add_event.call_args
        agent_data = call_args.kwargs["content"]["parts"][0]
        assert agent_data["type"] == "custom_update"


class TestFlotorchStrandsSessionCreateMessage:
    """Test create_message function."""

    @pytest.mark.parametrize(
        "test_name,role,content,message_id,should_fail,expected_exception",
        CREATE_MESSAGE_TEST_DATA
    )
    def test_create_message_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        role,
        content,
        message_id,
        should_fail,
        expected_exception
    ):
        """Test create_message with various scenarios."""
        session_message = Mock()
        session_message.message = {"role": role, "content": content}
        session_message.message_id = message_id
        strands_session.create_message(test_data["session_id"],
                                        test_data["agent_id"],
                                        session_message)
        mock_session_client.add_event.assert_called_once()
        call_args = mock_session_client.add_event.call_args
        expected_author = "user" if role == "user" else "assistant"
        assert (call_args.kwargs["author"] == expected_author and
                call_args.kwargs["grounding_metadata"]["message_id"] ==
                message_id)

    def test_create_message_extracts_text_from_list(
        self, strands_session, mock_session_client, test_data
    ):
        """Test create_message extracts text from list content."""
        session_message = Mock()
        session_message.message = {
            "role": "user",
            "content": [{"text": "hello world"}]
        }
        session_message.message_id = 0
        strands_session.create_message(test_data["session_id"],
                                        test_data["agent_id"],
                                        session_message)
        call_args = mock_session_client.add_event.call_args
        message_data = call_args.kwargs["content"]
        assert message_data["parts"][0]["text"] == "hello world"


class TestFlotorchStrandsSessionReadMessage:
    """Test read_message function."""

    @pytest.mark.parametrize(
        "test_name,message_exists,message_id,should_fail,"
        "expected_exception",
        READ_MESSAGE_TEST_DATA
    )
    def test_read_message_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        message_exists,
        message_id,
        should_fail,
        expected_exception
    ):
        """Test read_message with various scenarios."""
        session_mock = Mock()
        session_mock.uid = test_data["session_id"]
        if message_exists:
            event = Mock()
            event.author = "user"
            content = Mock()
            content.parts = [{"text": "test message"}]
            event.content = content
            event.groundingMetadata = {
                "agent_id": test_data["agent_id"],
                "message_id": message_id,
                "role": "user"
            }
            session_mock.events = [event]
            mock_session_client.get.return_value = session_mock
            result = strands_session.read_message(
                test_data["session_id"], test_data["agent_id"], message_id
            )
            assert result is not None and result.message_id == message_id
        else:
            session_mock.events = []
            mock_session_client.get.return_value = session_mock
            result = strands_session.read_message(
                test_data["session_id"], test_data["agent_id"], message_id
            )
            assert result is None

    def test_read_message_extracts_content_correctly(
        self, strands_session, mock_session_client, test_data
    ):
        """Test read_message extracts message content correctly."""
        session_mock = Mock()
        event = Mock()
        event.author = "assistant"
        content = Mock()
        content.parts = [{"text": "Hello, user!"}]
        event.content = content
        event.groundingMetadata = {
            "agent_id": test_data["agent_id"],
            "message_id": 1,
            "role": "assistant"
        }
        session_mock.events = [event]
        mock_session_client.get.return_value = session_mock
        result = strands_session.read_message(test_data["session_id"],
                                               test_data["agent_id"], 1)
        assert (result is not None and
                (hasattr(result.message, 'content') or
                 'content' in result.message))

    def test_read_message_error_returns_none(
        self, strands_session, mock_session_client, test_data
    ):
        """Test read_message returns None on error."""
        mock_session_client.get.side_effect = Exception("API Error")
        assert strands_session.read_message(
            test_data["session_id"], test_data["agent_id"], 0
        ) is None


class TestFlotorchStrandsSessionUpdateMessage:
    """Test update_message function."""

    @pytest.mark.parametrize(
        "test_name,message_id,redact,should_fail,expected_exception",
        UPDATE_MESSAGE_TEST_DATA
    )
    def test_update_message_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        message_id,
        redact,
        should_fail,
        expected_exception
    ):
        """Test update_message with various scenarios."""
        session_message = Mock()
        session_message.message_id = message_id
        session_message.content = "updated content"
        session_message.role = "user"
        session_message.redact_message = redact
        strands_session.update_message(test_data["session_id"],
                                        test_data["agent_id"],
                                        session_message)
        mock_session_client.add_event.assert_called_once()
        call_args = mock_session_client.add_event.call_args
        assert (call_args.kwargs["uid"] == test_data["session_id"] and
                call_args.kwargs["author"] == "system")
        update_data = call_args.kwargs["content"]["parts"][0]
        assert (update_data["type"] == "message_update" and
                update_data["message_id"] == message_id and
                update_data["redact_message"] == redact)

    def test_update_message_calls_api_correctly(
        self, strands_session, mock_session_client, test_data
    ):
        """Test update_message calls add_event correctly."""
        session_message = Mock()
        session_message.message_id = 1
        session_message.content = "updated content"
        session_message.role = "user"
        session_message.redact_message = False
        strands_session.update_message(test_data["session_id"],
                                        test_data["agent_id"],
                                        session_message)
        call_args = mock_session_client.add_event.call_args
        assert (call_args.kwargs["uid"] == test_data["session_id"] and
                call_args.kwargs["author"] == "system")

    def test_update_message_error_silent(
        self, strands_session, mock_session_client, test_data
    ):
        """Test update_message handles errors silently."""
        mock_session_client.add_event.side_effect = Exception("API Error")
        session_message = Mock()
        session_message.message_id = 1
        session_message.content = "updated content"
        session_message.role = "user"
        session_message.redact_message = False
        strands_session.update_message(test_data["session_id"],
                                        test_data["agent_id"],
                                        session_message)


class TestFlotorchStrandsSessionListMessages:
    """Test list_messages function."""

    @pytest.mark.parametrize(
        "test_name,total_messages,limit,offset,expected_count,"
        "should_fail,expected_exception",
        LIST_MESSAGES_TEST_DATA
    )
    def test_list_messages_parametrized(
        self,
        strands_session,
        mock_session_client,
        test_data,
        test_name,
        total_messages,
        limit,
        offset,
        expected_count,
        should_fail,
        expected_exception
    ):
        """Test list_messages with pagination."""
        session_mock = Mock()
        events = []
        for i in range(total_messages):
            event = Mock()
            event.author = "user"
            content = Mock()
            content.parts = [{"text": f"message {i}"}]
            event.content = content
            event.groundingMetadata = {
                "agent_id": test_data["agent_id"],
                "message_id": i,
                "role": "user"
            }
            events.append(event)
        session_mock.events = events
        mock_session_client.get.return_value = session_mock
        result = strands_session.list_messages(
            test_data["session_id"], test_data["agent_id"],
            limit=limit, offset=offset
        )
        assert len(result) == expected_count

    def test_list_messages_filters_by_agent(
        self, strands_session, mock_session_client, test_data
    ):
        """Test list_messages filters by agent_id."""
        session_mock = Mock()
        event1 = Mock()
        event1.author = "user"
        content1 = Mock()
        content1.parts = [{"text": "for default"}]
        event1.content = content1
        event1.groundingMetadata = {
            "agent_id": "default",
            "message_id": 0,
            "role": "user"
        }
        event2 = Mock()
        event2.author = "user"
        content2 = Mock()
        content2.parts = [{"text": "for other"}]
        event2.content = content2
        event2.groundingMetadata = {
            "agent_id": "other_agent",
            "message_id": 1,
            "role": "user"
        }
        session_mock.events = [event1, event2]
        mock_session_client.get.return_value = session_mock
        result = strands_session.list_messages(test_data["session_id"],
                                                "default")
        assert len(result) == 1

    def test_list_messages_sorts_by_message_id(
        self, strands_session, mock_session_client, test_data
    ):
        """Test list_messages returns sorted messages."""
        session_mock = Mock()
        events = []
        for message_id in [2, 0, 3, 1]:
            event = Mock()
            event.author = "user"
            content = Mock()
            content.parts = [{"text": f"msg {message_id}"}]
            event.content = content
            event.groundingMetadata = {
                "agent_id": test_data["agent_id"],
                "message_id": message_id,
                "role": "user"
            }
            events.append(event)
        session_mock.events = events
        mock_session_client.get.return_value = session_mock
        result = strands_session.list_messages(test_data["session_id"],
                                                test_data["agent_id"])
        for i, msg in enumerate(result):
            assert msg.message_id == i

    def test_list_messages_handles_api_error(
        self, strands_session, mock_session_client, test_data
    ):
        """Test list_messages handles API errors gracefully."""
        mock_session_client.get.side_effect = Exception("API Error")
        result = strands_session.list_messages(test_data["session_id"],
                                                test_data["agent_id"])
        assert result == []
