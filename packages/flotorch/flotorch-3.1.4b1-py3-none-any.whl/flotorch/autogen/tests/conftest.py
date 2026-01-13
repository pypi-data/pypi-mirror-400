"""Pytest fixtures for AutoGen tests.

This module provides reusable fixtures for testing AutoGen components
including session mocking, LLM integration, agent testing, and instance
creation.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from autogen_core.memory import MemoryContent, MemoryQueryResult, MemoryMimeType
from autogen_core.models import UserMessage


from flotorch.autogen.sessions import (
    FlotorchAutogenSession,
    FlotorchAutogenSessionConfig,
)


class MockLLMResponse:
    """Mock LLM response object for testing."""

    def __init__(self, content=None, metadata=None):
        """Initialize mock response."""
        self.content = content or "Mock response"
        self.metadata = metadata or {
            "raw_response": {
                "choices": [{"message": {"content": self.content}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5}
            },
            "inputTokens": 10,
            "outputTokens": 5
        }

    def __await__(self):
        """Make this object awaitable."""
        async def _await():
            return self
        return _await().__await__()

    def __iter__(self):
        """Make this object iterable for async iteration."""
        return iter([self])


class MockFunctionTool:
    """Mock FunctionTool for testing."""

    def __init__(self, name: str = "test_tool"):
        """Initialize mock tool."""
        self.name = name

    def __repr__(self):
        """Return string representation."""
        return f"MockFunctionTool(name='{self.name}')"


class MockFlotorchAutogenMemory:
    """Mock FlotorchAutogenMemory for testing."""

    def __init__(self, name: str = "test_memory"):
        """Initialize mock memory."""
        self.name = name

    def __repr__(self):
        """Return string representation."""
        return f"MockFlotorchAutogenMemory(name='{self.name}')"


@pytest.fixture
def mock_flotorch_session():
    """Create mock FlotorchAsyncSession with default responses."""
    mock_session = AsyncMock()
    mock_session.create.return_value = {
        "uid": "test-session-123",
        "appName": "autogen_session_app",
        "userId": "autogen_user",
        "state": {},
        "createdAt": "2025-01-01T00:00:00.000Z",
        "updatedAt": "2025-01-01T00:00:00.000Z",
    }
    mock_session.get.return_value = {"uid": "test-session-123", "events": []}
    mock_session.add_event.return_value = {"success": True}
    mock_session.delete.return_value = None
    mock_session.extract_events = Mock(return_value=[])
    return mock_session


@pytest.fixture
def session_instance(mock_flotorch_session):
    """Create FlotorchAutogenSession instance with mocked client."""
    with patch(
        "flotorch.autogen.sessions.FlotorchAsyncSession",
        return_value=mock_flotorch_session,
    ):
        instance = FlotorchAutogenSession(
            base_url="https://test.flotorch.com",
            api_key="test-api-key"
        )
    return instance


@pytest.fixture
def session_instance_with_uid(session_instance):
    """Create session instance with pre-existing uid."""
    session_instance.uid = "existing-session-123"
    session_instance._initialized = True
    return session_instance


@pytest.fixture
def sample_session_config():
    """Create sample session config for testing."""
    return FlotorchAutogenSessionConfig(
        uid="test-session-123",
        base_url="https://test.flotorch.com"
    )


@pytest.fixture
def mock_flotorch_llm():
    """Create mock FlotorchLLM instance."""
    mock = Mock()
    mock.ainvoke.return_value = MockLLMResponse()
    return mock


@pytest.fixture
def llm_instance(mock_flotorch_llm):
    """Create FlotorchAutogenLLM instance with mocked FlotorchLLM."""
    with patch.dict('sys.modules', {
        'autogen_ext': Mock(),
        'autogen_ext.tools': Mock(),
        'autogen_ext.tools.mcp': Mock()
    }):
        from flotorch.autogen.llm import FlotorchAutogenLLM

        with patch('flotorch.autogen.llm.FlotorchLLM',
                   return_value=mock_flotorch_llm):
            llm = FlotorchAutogenLLM(
                model_id="test-model",
                api_key="test-key",
                base_url="https://test.com"
            )
            llm._llm = mock_flotorch_llm
    return llm


@pytest.fixture
def mock_session_client():
    """Create mock FlotorchAutogenSession client with default responses."""
    mock_client = Mock()
    mock_client.create.return_value = {
        "uid": "test-session-123",
        "appName": "autogen_session_app",
        "userId": "autogen_user",
        "state": {},
        "createdAt": "2025-01-01T00:00:00.000Z",
        "updatedAt": "2025-01-01T00:00:00.000Z",
    }
    mock_client.get.return_value = {"uid": "test-session-123", "events": []}
    mock_client.add_event.return_value = {"success": True}
    mock_client.delete.return_value = None
    mock_client.extract_events = Mock(return_value=[])
    return mock_client


@pytest.fixture
def mock_memory_client():
    """Create mock FlotorchAutogenMemory client with default responses."""
    mock_client = Mock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def mock_assistant_agent():
    """Create mock AssistantAgent for testing."""
    agent = Mock()
    agent.name = "test-agent"
    agent.system_message = "Test system message"
    agent.tools = []
    agent.memory = None
    agent.model_context = None
    return agent


@pytest.fixture
def mock_agent_deps():
    """Mock all external dependencies for agent testing."""
    from flotorch.autogen.tests.test_data.agent_test_data import MINIMAL_CONFIG

    with patch.dict('sys.modules', {
        'autogen_ext': Mock(),
        'autogen_ext.tools': Mock(),
        'autogen_ext.tools.mcp': Mock()
    }):
        with patch('flotorch.autogen.agent.http_get') as http_mock, \
             patch('flotorch.autogen.agent.AssistantAgent') as agent_mock, \
             patch('flotorch.autogen.agent.FlotorchAutogenLLM') as llm_mock, \
             patch('flotorch.autogen.agent.create_sse_tool') as sse_mock, \
             patch('flotorch.autogen.agent.create_stream_tool') as stream_mock, \
             patch('flotorch.autogen.agent.time') as time_mock, \
             patch('flotorch.autogen.agent.asyncio') as asyncio_mock, \
             patch('flotorch.autogen.agent.concurrent.futures') as futures_mock:

            # Configure default return values
            http_mock.return_value = MINIMAL_CONFIG
            agent_mock.return_value = Mock(
                name="test-agent", system_message="test"
            )
            llm_mock.return_value = Mock()
            time_mock.time.return_value = 1000.0

            # Configure async mocks properly
            mock_loop = Mock()
            mock_loop.run_until_complete = Mock(return_value=[])
            asyncio_mock.new_event_loop.return_value = mock_loop
            asyncio_mock.set_event_loop = Mock()
            asyncio_mock.gather = AsyncMock(return_value=[])

            # Configure thread executor mock
            executor_mock = Mock()
            future_mock = Mock()
            future_mock.result.return_value = []
            executor_mock.submit.return_value = future_mock
            futures_mock.ThreadPoolExecutor.return_value.__enter__.return_value = executor_mock

            # Configure tool creation mocks
            sse_mock.return_value = []
            stream_mock.return_value = []

            yield {
                'http_get': http_mock,
                'assistant_agent': agent_mock,
                'llm': llm_mock,
                'create_sse_tool': sse_mock,
                'create_stream_tool': stream_mock,
                'time': time_mock,
                'asyncio': asyncio_mock,
                'concurrent_futures': futures_mock
            }


@pytest.fixture
def agent_instance(mock_agent_deps):
    """Create FlotorchAutogenAgent instance with mocked dependencies."""
    with patch.dict('sys.modules', {
        'autogen_ext': Mock(),
        'autogen_ext.tools': Mock(),
        'autogen_ext.tools.mcp': Mock()
    }):
        from flotorch.autogen.agent import FlotorchAutogenAgent

        agent = FlotorchAutogenAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
    return agent

class MockChatCompletionContext:
    """Mock ChatCompletionContext for testing update_context."""
    
    def __init__(self, messages=None):
        """Initialize mock context.
        
        Args:
            messages: List of messages in the context
        """
        self.messages = messages or []
        self.added_messages = []
    
    async def get_messages(self):
        """Return messages in the context."""
        return self.messages
    
    async def add_message(self, message):
        """Record added messages."""
        self.added_messages.append(message)


@pytest.fixture
def mock_memory_client():
    """Create mock FlotorchMemory client with default responses.
    
    Returns:
        Mock: Configured mock memory client
    """
    mock_client = Mock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def autogen_memory_instance(mock_memory_client, monkeypatch):
    """Create FlotorchAutogenMemory instance with mocked client.
    
    Args:
        mock_memory_client: Mocked memory client fixture
        monkeypatch: Pytest monkeypatch fixture
    
    Returns:
        FlotorchAutogenMemory: Instance with mocked dependencies
    """
    with patch('flotorch.autogen.memory.log_object_creation'), \
         patch('flotorch.autogen.memory.log_error'):
        
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="test_memory",
            api_key="test-api-key",
            base_url="https://test.flotorch.com",
            user_id="test_user",
            app_id="test_app",
            limit=10
        )
        
        monkeypatch.setattr(instance, "_memory", mock_memory_client)
        
        return instance


@pytest.fixture
def autogen_memory_instance_with_none_ids(mock_memory_client, monkeypatch):
    """Create FlotorchAutogenMemory instance with None user_id and app_id.
    
    Args:
        mock_memory_client: Mocked memory client fixture
        monkeypatch: Pytest monkeypatch fixture
    
    Returns:
        FlotorchAutogenMemory: Instance with None IDs
    """
    with patch('flotorch.autogen.memory.log_object_creation'), \
         patch('flotorch.autogen.memory.log_error'):
        
        from flotorch.autogen.memory import FlotorchAutogenMemory
        
        instance = FlotorchAutogenMemory(
            name="test_memory",
            api_key="test-api-key",
            base_url="https://test.flotorch.com",
            user_id=None,
            app_id=None
        )
        
        monkeypatch.setattr(instance, "_memory", mock_memory_client)
        
        return instance


@pytest.fixture
def mock_chat_context_empty():
    """Create empty chat context.
    
    Returns:
        MockChatCompletionContext: Empty context
    """
    return MockChatCompletionContext(messages=[])


@pytest.fixture
def mock_chat_context_with_messages():
    """Create chat context with sample messages.
    
    Returns:
        MockChatCompletionContext: Context with messages
    """
    messages = [
        UserMessage(content="First message", source="user"),
        UserMessage(content="Second message", source="user"),
        UserMessage(content="What is the weather?", source="user")
    ]
    return MockChatCompletionContext(messages=messages)


@pytest.fixture
def sample_memory_content():
    """Create sample MemoryContent for testing.
    
    Returns:
        MemoryContent: Sample memory content
    """
    return MemoryContent(
        content="Test memory content",
        mime_type=MemoryMimeType.TEXT
    )


@pytest.fixture
def sample_memory_query_result():
    """Create sample MemoryQueryResult for testing.
    
    Returns:
        MemoryQueryResult: Sample query result with multiple memories
    """
    return MemoryQueryResult(
        results=[
            MemoryContent(content="Memory 1", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory 2", mime_type=MemoryMimeType.TEXT),
            MemoryContent(content="Memory 3", mime_type=MemoryMimeType.TEXT)
        ]
    )


@pytest.fixture
def mock_memory_content_with_content_attr():
    """Create mock object with content attribute for query testing.
    
    Returns:
        Mock: Object with content attribute
    """
    mock_obj = Mock()
    mock_obj.content = "Query from content attribute"
    return mock_obj