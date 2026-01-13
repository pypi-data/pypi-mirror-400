"""Pytest fixtures for CrewAI tests.

This module provides reusable fixtures for testing CrewAI components
including sessions, memory storage, and LLM integration.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel, Field

from flotorch.crewai.sessions import FlotorchCrewAISession
from flotorch.crewai.memory import FlotorchMemoryStorage
from flotorch.crewai.llm import FlotorchCrewAILLM
from flotorch.crewai.tests.test_data.agent_test_data import MINIMAL_CONFIG

class MockLLMResponse:
    """Mock LLM response object for testing."""

    def __init__(self, content: str):
        """Initialize mock response.

        Args:
            content: Response content string
        """
        self.content = content


class SampleTaskSchema(BaseModel):
    """Sample Pydantic schema for task output testing."""

    result: str = Field(description="Result")
    score: float = Field(description="Score")


@pytest.fixture
def mock_session_client():
    """Create mock FlotorchSession client with default responses.

    Returns:
        Mock: Configured mock session client
    """
    mock_client = Mock()
    mock_client.create.return_value = {"uid": "test-session-123"}
    mock_client.get.return_value = {"uid": "test-session-123"}
    mock_client.add_event.return_value = {"success": True}
    mock_client.get_events.return_value = []
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def session_instance(mock_session_client, monkeypatch):
    """Create FlotorchCrewAISession instance with mocked client.

    Args:
        mock_session_client: Mocked session client fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlotorchCrewAISession: Instance with mocked dependencies
    """
    instance = FlotorchCrewAISession(
        base_url="https://test.flotorch.com",
        api_key="test-api-key",
        app_name="test_app",
        user_id="test_user"
    )
    monkeypatch.setattr(instance, "_session_client", mock_session_client)
    return instance


@pytest.fixture
def session_instance_with_id(session_instance):
    """Create session instance with pre-existing session_id.

    Args:
        session_instance: Base session instance fixture

    Returns:
        FlotorchCrewAISession: Instance with session_id set
    """
    session_instance._session_id = "existing-session-123"
    return session_instance


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
def memory_instance(mock_memory_client, monkeypatch):
    """Create FlotorchMemoryStorage instance with mocked client.

    Args:
        mock_memory_client: Mocked memory client fixture
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        FlotorchMemoryStorage: Instance with mocked dependencies
    """
    instance = FlotorchMemoryStorage(
        name="test_memory",
        api_key="test-api-key",
        base_url="https://test.flotorch.com",
        user_id="test_user",
        app_id="test_app"
    )
    monkeypatch.setattr(instance, "_memory", mock_memory_client)
    return instance


@pytest.fixture
def mock_task_with_output_pydantic():
    """Create mock task with output_pydantic schema.

    Returns:
        Mock: Task with output_pydantic set to SampleTaskSchema
    """
    task = Mock()
    task.output_json = None
    task.output_pydantic = SampleTaskSchema
    return task


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
    """Create FlotorchCrewAILLM instance with mocked FlotorchLLM.

    Args:
        mock_llm: Mocked FlotorchLLM fixture

    Returns:
        FlotorchCrewAILLM: Instance with mocked LLM dependency
    """
    with patch('flotorch.crewai.llm.FlotorchLLM', return_value=mock_llm):
        llm = FlotorchCrewAILLM(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com"
        )
        llm.llm = mock_llm
    return llm


# Agent test fixtures

@pytest.fixture
def mock_agent_deps():
    """Mock all external dependencies for agent testing.
    
    Provides comprehensive mocking environment for FlotorchCrewAIAgent:
    - HTTP requests (config fetching)
    - CrewAI Agent and Task classes
    - FlotorchCrewAILLM
    - MCPServerAdapter (prevents connection attempts)
    - Time module (for sync testing)
    
    Returns:
        dict: Mocked objects with keys:
            - http_get: HTTP request mock
            - agent: CrewAI Agent class mock
            - task: CrewAI Task class mock
            - llm: FlotorchCrewAILLM mock
            - mcp: MCPServerAdapter mock
            - time: Time module mock
    """
    with patch('flotorch.crewai.agent.http_get') as http_mock, \
         patch('flotorch.crewai.agent.Agent') as agent_mock, \
         patch('flotorch.crewai.agent.Task') as task_mock, \
         patch('flotorch.crewai.agent.FlotorchCrewAILLM') as llm_mock, \
         patch('flotorch.crewai.agent.MCPServerAdapter') as mcp_mock, \
         patch('flotorch.crewai.agent.time') as time_mock:
        
        # Import test data here to avoid circular imports
        
        # Configure default return values
        http_mock.return_value = MINIMAL_CONFIG
        agent_mock.return_value = Mock(role="test-role", tools=[])
        task_mock.return_value = Mock(description="test-desc")
        llm_mock.return_value = Mock()
        time_mock.time.return_value = 1000.0
        
        # Prevent MCP connection attempts
        mcp_adapter = Mock(tools=[])
        mcp_mock.return_value = mcp_adapter
        
        yield {
            'http_get': http_mock,
            'agent': agent_mock,
            'task': task_mock,
            'llm': llm_mock,
            'mcp': mcp_mock,
            'time': time_mock
        }