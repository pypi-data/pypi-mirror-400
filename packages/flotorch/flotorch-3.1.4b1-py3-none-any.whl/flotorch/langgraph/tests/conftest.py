"""Pytest fixtures for LangGraph tests.

This module provides reusable fixtures for testing LangGraph components
including sessions, memory storage, LLM integration, and agent testing.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field


class MockLLMResponse:
    """Mock LLM response object for testing."""

    def __init__(self, content: str, metadata: dict = None):
        """Initialize mock response.

        Args:
            content: Response content string
            metadata: Optional response metadata
        """
        self.content = content
        self.metadata = metadata or {}


class SampleSchema(BaseModel):
    """Sample Pydantic schema for structured output testing."""

    result: str = Field(description="Result")
    confidence: float = Field(description="Confidence score")


# Session Fixtures

@pytest.fixture
def test_data():
    """Common test data for LangGraph tests."""
    return {
        "api_key": "test_key",
        "base_url": "http://test",
        "app_name": "test_app",
        "user_id": "test_user",
        "thread_id": "test_thread_123"
    }


@pytest.fixture
def mock_sdk_session():
    """Mock the SDK FlotorchSession client."""
    mock_client = Mock()
    mock_client.create.return_value = {
        "uid": "test-session-123",
        "appName": "test_app",
        "userId": "test_user",
        "state": {},
        "last_update_time": 1234567890
    }
    mock_client.get.return_value = {
        "uid": "test-session-123",
        "appName": "test_app",
        "userId": "test_user",
        "state": {},
        "events": [],
        "last_update_time": 1234567890
    }
    mock_client.add_event.return_value = {
        "uid": "e1",
        "invocationId": "inv1",
        "author": "user"
    }
    mock_client.get_events.return_value = []
    mock_client.list.return_value = []
    mock_client.delete.return_value = {"status": "deleted"}
    return mock_client


@pytest.fixture
def langgraph_session(test_data):
    """Create FlotorchLanggraphSession instance."""
    from flotorch.langgraph.sessions import FlotorchLanggraphSession
    return FlotorchLanggraphSession(
        api_key=test_data["api_key"],
        base_url=test_data["base_url"],
        app_name=test_data["app_name"],
        user_id=test_data["user_id"]
    )


@pytest.fixture
def langgraph_session_with_mock(
    langgraph_session, mock_sdk_session, monkeypatch
):
    """Create FlotorchLanggraphSession with mocked SDK session."""

    monkeypatch.setattr(langgraph_session, "session", mock_sdk_session)
    return langgraph_session


@pytest.fixture
def mock_session_client():
    """Create mock session client with default responses.

    Returns:
        Mock: Configured mock session client
    """
    mock_client = Mock()
    mock_client.get_session_history.return_value = Mock(messages=[])
    return mock_client


@pytest.fixture
def mock_checkpointer():
    """Create mock checkpointer for LangGraph.

    Returns:
        Mock: Configured mock checkpointer
    """
    mock = Mock()
    mock.get.return_value = None
    mock.put.return_value = None
    return mock


# Memory Fixtures

@pytest.fixture
def mock_memory_client():
    """Create mock FlotorchMemory client with default responses.

    Returns:
        Mock: Configured mock memory client
    """
    mock_client = Mock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    mock_client.get.return_value = {"data": None}
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def mock_async_memory_client():
    """Create mock async FlotorchMemory client with default responses.

    Returns:
        AsyncMock: Configured mock async memory client
    """
    from unittest.mock import AsyncMock
    
    mock_client = AsyncMock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    mock_client.get.return_value = {"data": None}
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def store_instance(mock_memory_client, mock_async_memory_client, monkeypatch):
    """Create FlotorchStore instance with mocked memory client.

    Args:
        mock_memory_client: Mocked memory client fixture
        mock_async_memory_client: Mocked async memory client fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlotorchStore: Instance with mocked dependencies
    """
    from flotorch.langgraph.memory import FlotorchStore
    
    instance = FlotorchStore(
        api_key="test-api-key",
        base_url="https://test.flotorch.com",
        provider_name="test_provider",
        userId="test_user",
        appId="test_app",
        agentId="test_agent",
        sessionId="test_session"
    )
    monkeypatch.setattr(instance, "_memory", mock_memory_client)
    monkeypatch.setattr(instance, "_async_memory", mock_async_memory_client)
    return instance


@pytest.fixture
def store_instance_no_defaults(
    mock_memory_client, mock_async_memory_client, monkeypatch
):
    """Create FlotorchStore instance without default user/app IDs.

    Args:
        mock_memory_client: Mocked memory client fixture
        mock_async_memory_client: Mocked async memory client fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlotorchStore: Instance with mocked dependencies
    """
    from flotorch.langgraph.memory import FlotorchStore
    
    instance = FlotorchStore(
        api_key="test-api-key",
        base_url="https://test.flotorch.com",
        provider_name="test_provider"
    )
    monkeypatch.setattr(instance, "_memory", mock_memory_client)
    monkeypatch.setattr(instance, "_async_memory", mock_async_memory_client)
    return instance


@pytest.fixture
def mock_store():
    """Create mock store for LangGraph memory.

    Returns:
        Mock: Configured mock store
    """
    mock = Mock()
    mock.get.return_value = []
    mock.put.return_value = None
    mock.search.return_value = []
    return mock


# LLM Fixtures

@pytest.fixture
def mock_llm():
    """Create mock FlotorchLLM instance.

    Returns:
        Mock: FlotorchLLM mock with default invoke response
    """
    mock = Mock()
    mock.invoke.return_value = MockLLMResponse("test response")
    return mock


@pytest.fixture
def llm_instance(mock_llm):
    """Create FlotorchLangChainLLM instance with mocked FlotorchLLM.

    Args:
        mock_llm: Mocked FlotorchLLM fixture

    Returns:
        FlotorchLangChainLLM: Instance with mocked LLM dependency
    """
    with patch('flotorch.langchain.llm.FlotorchLLM', return_value=mock_llm):
        from flotorch.langchain.llm import FlotorchLangChainLLM
        llm = FlotorchLangChainLLM(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com"
        )
        llm._llm = mock_llm
    return llm


# Agent Fixtures

@pytest.fixture
def mock_agent_graph_deps():
    """Mock all external dependencies for LangGraph agent testing.
    
    Provides comprehensive mocking environment for FlotorchLangGraphAgent:
    - HTTP requests (config fetching)
    - FlotorchLangChainLLM
    - create_react_agent (LangGraph)
    - MultiServerMCPClient (prevents connection attempts)
    - Time module (for sync testing)
    - asyncio (for async operations)
    
    Returns:
        dict: Mocked objects with keys:
            - http_get: HTTP request mock
            - llm: FlotorchLangChainLLM mock
            - create_react_agent: LangGraph create_react_agent mock
            - mcp_client: MultiServerMCPClient mock
            - time: Time module mock
            - asyncio_run: asyncio.run mock
    """
    with patch('flotorch.langgraph.agent.http_get') as http_mock, \
         patch('flotorch.langgraph.agent.FlotorchLangChainLLM') as llm_mock, \
         patch('flotorch.langgraph.agent.create_react_agent') as agent_mock, \
         patch('flotorch.langgraph.agent.time') as time_mock, \
         patch('flotorch.langgraph.agent.asyncio.run') as asyncio_run_mock:
        
        # Import test data here to avoid circular imports
        from flotorch.langgraph.tests.test_data.agent_test_data import (
            MINIMAL_CONFIG
        )
        
        # Configure default return values
        http_mock.return_value = MINIMAL_CONFIG
        llm_mock.return_value = Mock()
        
        # Mock agent graph (LangGraph returns a graph
        # with invoke method)
        mock_graph = Mock()
        mock_graph.invoke = Mock(return_value={"messages": ["response"]})
        agent_mock.return_value = mock_graph
        
        # Fix: Make asyncio.run properly consume the coroutine
        # to avoid warnings
        def run_coroutine(coro):
            """Properly consume coroutine to avoid 'never awaited' warnings."""
            try:
                # Close the coroutine to prevent warning
                coro.close()
            except:
                pass
            return mock_graph
        
        asyncio_run_mock.side_effect = run_coroutine
        
        time_mock.time.return_value = 1000.0
        
        yield {
            'http_get': http_mock,
            'llm': llm_mock,
            'create_react_agent': agent_mock,
            'time': time_mock,
            'asyncio_run': asyncio_run_mock
        }
