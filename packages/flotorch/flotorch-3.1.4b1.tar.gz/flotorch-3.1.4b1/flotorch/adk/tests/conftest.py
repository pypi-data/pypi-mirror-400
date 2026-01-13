"""Pytest fixtures for ADK tests."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from flotorch.adk.llm import FlotorchADKLLM
from flotorch.adk.memory import FlotorchMemoryService
from flotorch.adk.sessions import FlotorchADKSession
from flotorch.adk.tests.test_data.agent_test_data import MINIMAL_CONFIG


class MockAIMessage:
    """Mock AI message response for testing."""
    def __init__(self, content: str, metadata: dict = None):
        self.content = content
        self.metadata = metadata or {"raw_response": {}}


@pytest.fixture
def test_data():
    """Common test data for ADK tests."""
    return {
        "api_key": "test_key",
        "base_url": "http://test",
        "app_name": "test_app",
        "user_id": "test_user",
        "session_id": "test_session_123"
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
        "last_update_time": 1234567890
    }
    mock_client.add_event.return_value = {
        "uid": "e1",
        "invocationId": "inv1",
        "author": "user"
    }
    mock_client.get_events.return_value = []
    mock_client.delete.return_value = {"status": "deleted"}
    return mock_client


@pytest.fixture
def adk_session(test_data):
    """Create FlotorchADKSession instance."""
    return FlotorchADKSession(
        api_key=test_data["api_key"],
        base_url=test_data["base_url"]
    )


@pytest.fixture
def adk_session_with_mock(adk_session, mock_sdk_session, monkeypatch):
    """Create FlotorchADKSession with mocked SDK session."""
    # Mock the underlying SDK FlotorchSession
    monkeypatch.setattr(adk_session, "_flotorch_session", mock_sdk_session)
    return adk_session


# Memory Service Fixtures

@pytest.fixture
def mock_memory_client():
    """Create mock FlotorchMemory client with default responses.
    
    Returns:
        Mock: Configured mock client for memory operations
    """
    mock_client = Mock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    return mock_client


@pytest.fixture
def memory_service_instance(mock_memory_client, monkeypatch):
    """Create FlotorchMemoryService with mocked memory client.
    
    Args:
        mock_memory_client: Mocked memory client fixture
        monkeypatch: Pytest monkeypatch fixture
        
    Returns:
        FlotorchMemoryService: Instance with mocked dependencies
    """
    instance = FlotorchMemoryService(
        name="test_provider",
        api_key="test-api-key",
        base_url="https://test.flotorch.com"
    )
    monkeypatch.setattr(instance, "_memory", mock_memory_client)
    return instance


# LLM Fixtures

@pytest.fixture
def mock_adk_llm():
    """Create mock FlotorchLLM instance for ADK.
    
    Returns:
        AsyncMock: FlotorchLLM mock with default ainvoke response
    """
    mock = AsyncMock()
    mock.ainvoke.return_value = Mock(
        content="test response",
        metadata={"raw_response": {}}
    )
    return mock


@pytest.fixture
def adk_llm_instance(mock_adk_llm):
    """Create FlotorchADKLLM instance with mocked FlotorchLLM.
    
    Args:
        mock_adk_llm: Mocked FlotorchLLM fixture
        
    Returns:
        FlotorchADKLLM: Instance with mocked LLM dependency
    """
    with patch('flotorch.adk.llm.FlotorchLLM', return_value=mock_adk_llm):
        llm = FlotorchADKLLM(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com"
        )
        llm._llm = mock_adk_llm
    return llm


# Agent Fixtures

@pytest.fixture
def agent_test_data():
    """Common test data for ADK Agent tests."""
    return {
        "agent_name": "test-agent",
        "api_key": "test-api-key-123",
        "base_url": "https://test.flotorch.com"
    }


@pytest.fixture
def mock_agent_deps():
    """Mock all external dependencies for ADK agent testing.
    
    Provides comprehensive mocking environment for FlotorchADKAgent:
    - HTTP requests (config fetching)
    - FlotorchADKLLM
    - Google ADK LlmAgent
    - Time module (for sync testing)
    
    Returns:
        dict: Dictionary containing all mocked objects
    """
    with patch('flotorch.adk.agent.http_get') as http_mock, \
         patch('flotorch.adk.agent.FlotorchADKLLM') as llm_mock, \
         patch('flotorch.adk.agent.LlmAgent') as agent_mock, \
         patch('flotorch.adk.agent.time') as time_mock:
        
        # Configure default return values
        http_mock.return_value = MINIMAL_CONFIG
        
        # Mock LLM
        mock_llm_instance = Mock()
        llm_mock.return_value = mock_llm_instance
        
        # Mock Agent
        mock_agent_instance = Mock()
        mock_agent_instance.name = "test_agent"
        mock_agent_instance.description = "Test description"
        agent_mock.return_value = mock_agent_instance
        
        # Mock time
        time_mock.time.return_value = 1000.0
        
        yield {
            'http_get': http_mock,
            'llm': llm_mock,
            'llm_instance': mock_llm_instance,
            'agent': agent_mock,
            'agent_instance': mock_agent_instance,
            'time': time_mock
        }