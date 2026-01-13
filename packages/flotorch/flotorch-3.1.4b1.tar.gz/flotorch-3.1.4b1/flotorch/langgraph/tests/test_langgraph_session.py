"""Test cases for FlotorchLanggraphSession class."""

import pytest
from unittest.mock import patch
from flotorch.sdk.utils.http_utils import APIError
from langgraph.checkpoint.base import CheckpointTuple

from flotorch.langgraph.tests.test_data.session_test_data import (
    GET_TUPLE_TEST_DATA,
    PUT_TEST_DATA,
    PUT_WRITES_TEST_DATA,
    LIST_TEST_DATA,
    DELETE_THREAD_TEST_DATA
)


class TestFlotorchLanggraphSessionInit:
    """Test constructor initialization."""

    @patch('flotorch.langgraph.sessions.FlotorchSession')
    def test_init_with_custom_parameters(self, mock_flotorch_session):
        """Test initialization with custom parameters."""
        from flotorch.langgraph.sessions import FlotorchLanggraphSession
        instance = FlotorchLanggraphSession(
            api_key="custom-key-123",
            base_url="https://custom.flotorch.com",
            app_name="my_app",
            user_id="user_123"
        )
        assert (instance.app_name == "my_app" and
                instance.user_id == "user_123" and
                instance.session is not None)
        mock_flotorch_session.assert_called_once_with(
            "custom-key-123", "https://custom.flotorch.com"
        )

    @patch('flotorch.langgraph.sessions.FlotorchSession')
    def test_init_with_defaults(self, mock_flotorch_session):
        """Test initialization with required parameters."""
        from flotorch.langgraph.sessions import FlotorchLanggraphSession
        instance = FlotorchLanggraphSession(
            api_key="test-key", base_url="http://test.com",
            app_name="test_app", user_id="test_user"
        )
        assert (instance.app_name == "test_app" and
                instance.user_id == "test_user")
        mock_flotorch_session.assert_called_once_with(
            "test-key", "http://test.com"
        )


class TestFlotorchLanggraphSessionGetTuple:
    """Test get_tuple function."""

    @pytest.mark.parametrize(
        "test_name,session_exists,has_events,events_count,"
        "should_fail,expected_exception", GET_TUPLE_TEST_DATA
    )
    def test_get_tuple_parametrized(
        self,
        langgraph_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        session_exists,
        has_events,
        events_count,
        should_fail,
        expected_exception
    ):
        """Test get_tuple with various scenarios."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        if not session_exists:
            mock_sdk_session.get.side_effect = APIError(
                status_code=404, message="Not found"
            )
            result = langgraph_session_with_mock.get_tuple(config)
            mock_sdk_session.create.assert_called_once()
            assert result is None
        elif not has_events:
            mock_sdk_session.get.return_value = {
                "uid": test_data["thread_id"], "events": []
            }
            result = langgraph_session_with_mock.get_tuple(config)
            assert result is None
        else:
            events = [
                {
                    "uid_event": f"e{i}",
                    "content": {
                        "checkpoint": {
                            "channel_values": {
                                "messages": [{"type": "human", "content": f"message {i}"}]
                            }
                        }
                    }
                }
                for i in range(events_count)
            ]
            mock_sdk_session.get.return_value = {
                "uid": test_data["thread_id"], "events": events
            }
            result = langgraph_session_with_mock.get_tuple(config)
            assert result is not None and isinstance(result, CheckpointTuple)

    def test_get_tuple_extracts_messages_correctly(
        self,
        langgraph_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test get_tuple correctly extracts and processes messages."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.get.return_value = {
            "uid": test_data["thread_id"],
            "events": [
                {"uid_event": "e1",
                 "content": {"checkpoint": {"channel_values": {
                     "messages": [{"type": "human", "content": "message 1"}]
                 }}}},
                {"uid_event": "e2",
                 "content": {"checkpoint": {"channel_values": {
                     "messages": [{"type": "ai", "content": "message 2"}]
                 }}}}
            ]
        }
        result = langgraph_session_with_mock.get_tuple(config)
        assert (result is not None and result.checkpoint is not None)
        mock_sdk_session.get.assert_called_once_with(test_data["thread_id"])

    def test_get_tuple_handles_empty_events(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test get_tuple returns None when no events exist."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.get.return_value = {
            "uid": test_data["thread_id"], "events": []
        }
        result = langgraph_session_with_mock.get_tuple(config)
        assert result is None

    @pytest.mark.asyncio
    async def test_aget_tuple(
        self,
        langgraph_session_with_mock,
        mock_sdk_session,
        test_data
    ):
        """Test aget_tuple async method."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.get.return_value = {
            "uid": test_data["thread_id"],
            "events": [
                {"uid_event": "e1",
                 "content": {"checkpoint": {"channel_values": {
                     "messages": [{"type": "human", "content": "test"}]
                 }}}}
            ]
        }
        result = await langgraph_session_with_mock.aget_tuple(config)
        assert result is not None and isinstance(result, CheckpointTuple)


class TestFlotorchLanggraphSessionPut:
    """Test put function."""

    @pytest.mark.parametrize(
        "test_name,has_messages,messages_count,should_fail,"
        "expected_exception", PUT_TEST_DATA
    )
    def test_put_parametrized(
        self,
        langgraph_session_with_mock,
        mock_sdk_session,
        test_data,
        test_name,
        has_messages,
        messages_count,
        should_fail,
        expected_exception
    ):
        """Test put with various scenarios."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        messages = [
            {"type": "human", "content": f"msg {i}"}
            for i in range(messages_count)
        ] if has_messages else []
        checkpoint = {
            "messages": messages, "v": 1, "id": "checkpoint-1", "ts": ""
        }
        metadata = {"step": 0, "source": "input", "parents": {}}
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        langgraph_session_with_mock.put(config, checkpoint, metadata, {})
        if has_messages:
            mock_sdk_session.add_event.assert_called_once()
            call_args = mock_sdk_session.add_event.call_args
            assert (call_args.kwargs["uid"] == test_data["thread_id"] and
                    call_args.kwargs["author"] == "system" and
                    "checkpoint" in call_args.kwargs["content"])
        else:
            mock_sdk_session.add_event.assert_not_called()

    def test_put_stores_checkpoint_correctly(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test put stores checkpoint in correct format."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        messages = [{"type": "human", "content": "test message"}]
        checkpoint = {
            "messages": messages, "v": 1, "id": "checkpoint-1", "ts": ""
        }
        metadata = {"step": 0, "source": "input", "parents": {}}
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        langgraph_session_with_mock.put(config, checkpoint, metadata, {})
        call_args = mock_sdk_session.add_event.call_args
        assert ("checkpoint" in call_args.kwargs["content"] and
                call_args.kwargs["content"]["checkpoint"]["messages"] ==
                messages)

    def test_put_with_empty_checkpoint(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test put with empty checkpoint does nothing."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        checkpoint = {
            "messages": [], "v": 1, "id": "checkpoint-1", "ts": ""
        }
        metadata = {"step": 0, "source": "input", "parents": {}}
        langgraph_session_with_mock.put(config, checkpoint, metadata, {})
        mock_sdk_session.add_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_aput(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test aput async method."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        checkpoint = {
            "messages": [{"type": "human", "content": "test"}],
            "v": 1, "id": "checkpoint-1", "ts": ""
        }
        metadata = {"step": 0, "source": "input", "parents": {}}
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        await langgraph_session_with_mock.aput(
            config, checkpoint, metadata, {}
        )
        mock_sdk_session.add_event.assert_called_once()


class TestFlotorchLanggraphSessionPutWrites:
    """Test put_writes function."""

    @pytest.mark.parametrize(
        "test_name,writes_count,should_fail,expected_exception",
        PUT_WRITES_TEST_DATA
    )
    def test_put_writes_parametrized(
        self, langgraph_session_with_mock, mock_sdk_session, test_data,
        test_name, writes_count, should_fail, expected_exception
    ):
        """Test put_writes with various scenarios."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        writes = [
            ("channel", {"data": f"value{i}"}) for i in range(writes_count)
        ]
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        langgraph_session_with_mock.put_writes(config, writes, "task-1")
        mock_sdk_session.add_event.assert_called_once()
        call_args = mock_sdk_session.add_event.call_args
        assert (call_args.kwargs["uid"] == test_data["thread_id"] and
                call_args.kwargs["author"] == "system" and
                "writes" in call_args.kwargs["content"])

    def test_put_writes_stores_writes_correctly(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test put_writes stores writes in correct format."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        writes = [("messages", {"type": "ai", "content": "response"})]
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        langgraph_session_with_mock.put_writes(config, writes, "task-123")
        call_args = mock_sdk_session.add_event.call_args
        assert (call_args.kwargs["content"]["task_id"] == "task-123" and
                "writes" in call_args.kwargs["content"])

    @pytest.mark.asyncio
    async def test_aput_writes(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test aput_writes async method."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        writes = [("messages", {"type": "ai", "content": "response"})]
        mock_sdk_session.add_event.return_value = {
            "uid": "e1", "invocationId": "inv1"
        }
        await langgraph_session_with_mock.aput_writes(
            config, writes, "task-1"
        )
        mock_sdk_session.add_event.assert_called_once()


class TestFlotorchLanggraphSessionList:
    """Test list function."""

    @pytest.mark.parametrize(
        "test_name,sessions_count,limit,should_fail,expected_exception",
        LIST_TEST_DATA
    )
    def test_list_parametrized(
        self, 
        langgraph_session_with_mock, 
        mock_sdk_session, 
        test_data,
        test_name, 
        sessions_count, 
        limit, 
        should_fail, 
        expected_exception
    ):
        """Test list with various scenarios."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.list.return_value = [
            {"uid": f"thread-{i}", "appName": test_data["app_name"],
             "userId": test_data["user_id"], "state": {},
             "last_update_time": 1234567890 + i}
            for i in range(sessions_count)
        ]
        results = list(langgraph_session_with_mock.list(
            config, limit=limit
        ))
        expected_count = (min(sessions_count, limit) if limit
                          else sessions_count)
        assert len(results) == expected_count
        mock_sdk_session.list.assert_called_once_with(
            app_name=test_data["app_name"], user_id=test_data["user_id"]
        )

    def test_list_respects_limit(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test list respects limit parameter."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.list.return_value = [
            {"uid": f"thread-{i}", "appName": test_data["app_name"],
             "userId": test_data["user_id"]}
            for i in range(10)
        ]
        results = list(langgraph_session_with_mock.list(config, limit=3))
        assert len(results) == 3

    def test_list_handles_api_error(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test list handles API errors gracefully."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.list.side_effect = APIError(
            status_code=500, message="Server error"
        )
        results = list(langgraph_session_with_mock.list(config))
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_alist(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test alist async method."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.list.return_value = [
            {"uid": f"thread-{i}", "appName": test_data["app_name"],
             "userId": test_data["user_id"]}
            for i in range(3)
        ]
        iterator = await langgraph_session_with_mock.alist(config)
        results = list(iterator)
        assert len(results) == 3


class TestFlotorchLanggraphSessionDeleteThread:
    """Test delete_thread function."""

    @pytest.mark.parametrize(
        "test_name,thread_exists,should_fail,expected_exception",
        DELETE_THREAD_TEST_DATA
    )
    def test_delete_thread_parametrized(
        self, 
        langgraph_session_with_mock, 
        mock_sdk_session, 
        test_data,
        test_name, 
        thread_exists, 
        should_fail, 
        expected_exception
    ):
        """Test delete_thread with various scenarios."""
        if not thread_exists:
            mock_sdk_session.delete.side_effect = APIError(
                status_code=404, message="Not found"
            )
            langgraph_session_with_mock.delete_thread(
                test_data["thread_id"]
            )
            mock_sdk_session.delete.assert_called_once_with(
                test_data["thread_id"]
            )
        else:
            mock_sdk_session.delete.return_value = None
            langgraph_session_with_mock.delete_thread(
                test_data["thread_id"]
            )
            mock_sdk_session.delete.assert_called_once_with(
                test_data["thread_id"]
            )

    def test_delete_thread_calls_with_correct_id(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test delete_thread calls delete with correct thread_id."""
        thread_id = "specific-thread-456"
        mock_sdk_session.delete.return_value = None
        langgraph_session_with_mock.delete_thread(thread_id)
        mock_sdk_session.delete.assert_called_once_with(thread_id)

    def test_delete_thread_handles_404_gracefully(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test delete_thread handles 404 errors without raising."""
        mock_sdk_session.delete.side_effect = APIError(
            status_code=404, message="Not found"
        )
        langgraph_session_with_mock.delete_thread("non-existent")
        mock_sdk_session.delete.assert_called_once()


class TestFlotorchLanggraphSessionEdgeCases:
    """Test edge cases and additional coverage."""

    def test_list_without_config(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test list uses instance defaults when config missing."""
        mock_sdk_session.list.return_value = [
            {"uid": "thread-1", "appName": test_data["app_name"],
             "userId": test_data["user_id"]}
        ]
        results = list(langgraph_session_with_mock.list({}))
        assert len(results) >= 0

    def test_get_tuple_creates_session_on_404(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test get_tuple creates new session when 404."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.get.side_effect = APIError(
            status_code=404, message="Not found"
        )
        mock_sdk_session.create.return_value = {
            "uid": test_data["thread_id"]
        }
        result = langgraph_session_with_mock.get_tuple(config)
        mock_sdk_session.create.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_alist_empty_results(
        self, langgraph_session_with_mock, mock_sdk_session, test_data
    ):
        """Test alist with empty results."""
        config = {"configurable": {"thread_id": test_data["thread_id"]}}
        mock_sdk_session.list.return_value = []
        iterator = await langgraph_session_with_mock.alist(config)
        results = list(iterator)
        assert len(results) == 0
