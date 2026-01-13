"""Pytest fixtures for LangChain tests."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from flotorch.langchain.session import FlotorchLangChainSession
from flotorch.langchain.memory import FlotorchLangChainMemory
from flotorch.langchain.tests.test_data.agent_test_data import MINIMAL_CONFIG


@pytest.fixture
def mock_session_client():
    """Create mock FlotorchSession client."""
    mock_client = Mock()
    mock_client.create.return_value = {"uid": "test-session-456"}
    mock_client.get.return_value = {"uid": "test-session-456"}
    mock_client.add_event.return_value = {"success": True}
    mock_client.get_events.return_value = []
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def session_instance(mock_session_client, monkeypatch):
    """Create FlotorchLangChainSession with mocked client."""
    instance = FlotorchLangChainSession(
        api_key="test-api-key",
        base_url="https://test.flotorch.cloud",
        app_name="langchain_session_app",
        user_id="test_langchain_user"
    )
    monkeypatch.setattr(instance, "session_client", mock_session_client)
    return instance


@pytest.fixture
def session_instance_with_id(session_instance):
    """Create session instance with existing session_id."""
    session_instance._session_id = "existing-session-456"
    return session_instance


@pytest.fixture
def mock_memory_client():
    """Create mock FlotorchMemory client."""
    mock_client = Mock()
    mock_client.add.return_value = {"success": True}
    mock_client.search.return_value = {"data": []}
    mock_client.delete.return_value = None
    return mock_client


@pytest.fixture
def memory_instance(mock_memory_client, monkeypatch):
    """Create FlotorchLangChainMemory with mocked client."""
    instance = FlotorchLangChainMemory(
        name="test_memory",
        api_key="test-api-key",
        base_url="https://test.flotorch.cloud",
        user_id="test_user",
        app_id="test_app"
    )
    monkeypatch.setattr(instance, "memory_client", mock_memory_client)
    return instance


# Agent test fixtures


@pytest.fixture
def mock_agent_deps():
    """Mock all external dependencies for LangChain agent testing.
    
    Provides comprehensive mocking environment for FlotorchLangChainAgent:
    - HTTP requests (config fetching)
    - LangChain agent creation function
    - FlotorchLangChainLLM
    - MultiServerMCPClient (prevents connection attempts)
    - Time module (for sync testing)
    
    Returns:
        dict: Mocked objects with keys:
            - http_get: HTTP request mock
            - create_agent: create_openai_functions_agent mock
            - llm: FlotorchLangChainLLM mock
            - mcp_client: MultiServerMCPClient mock
            - time: Time module mock
    """
    with patch('flotorch.langchain.agent.http_get') as http_mock, \
         patch('flotorch.langchain.agent.create_openai_functions_agent') as create_agent_mock, \
         patch('flotorch.langchain.agent.FlotorchLangChainLLM') as llm_mock, \
         patch('flotorch.langchain.agent.MultiServerMCPClient') as mcp_client_mock, \
         patch('flotorch.langchain.agent.time') as time_mock:        
        # Configure default return values
        http_mock.return_value = MINIMAL_CONFIG
        
        # Mock the agent (Runnable)
        mock_agent = Mock()
        mock_agent.invoke = Mock(return_value={"output": "test response"})
        mock_agent.ainvoke = Mock(return_value={"output": "test async response"})
        create_agent_mock.return_value = mock_agent
        
        # Mock LLM
        llm_mock.return_value = Mock()
        
        # Mock time
        time_mock.time.return_value = 1000.0
        
        # Mock MCP client
        mock_mcp_client = Mock()
        mock_mcp_client.get_tools = Mock(return_value=[])
        mcp_client_mock.return_value = mock_mcp_client
        
        yield {
            'http_get': http_mock,
            'create_agent': create_agent_mock,
            'llm': llm_mock,
            'mcp_client': mcp_client_mock,
            'time': time_mock
        }


@pytest.fixture
def mock_langchain_tool():
    """Create a mock LangChain tool.
    
    Returns:
        Mock: A mock tool with name and description attributes
    """
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "Test tool description"
    return tool

#llm fixtures

class MockLLMResponse:
    """Mock LLM response for testing."""
    def __init__(self, content: str, metadata: dict = None):
        self.content = content
        self.metadata = metadata or {}


@pytest.fixture
def mock_langchain_llm():
    """Create mock FlotorchLLM instance for LangChain (sync).
    
    Returns:
        Mock: FlotorchLLM mock with default invoke response
    """
    mock = Mock()
    mock.invoke.return_value = Mock(
        content="test response",
        metadata={}
    )
    return mock


@pytest.fixture
def mock_langchain_llm_async():
    """Create mock FlotorchLLM instance for LangChain (async).
    
    Returns:
        AsyncMock: FlotorchLLM mock with default ainvoke response
    """
    mock = AsyncMock()
    mock.ainvoke.return_value = Mock(
        content="test async response",
        metadata={}
    )
    return mock


@pytest.fixture
def langchain_llm_instance(mock_langchain_llm):
    """Create FlotorchLangChainLLM instance with mocked FlotorchLLM (sync).
    
    Args:
        mock_langchain_llm: Mocked sync FlotorchLLM fixture
        
    Returns:
        FlotorchLangChainLLM: Instance with mocked LLM dependency
    """
    with patch('flotorch.langchain.llm.FlotorchLLM', return_value=mock_langchain_llm):
        from flotorch.langchain.llm import FlotorchLangChainLLM
        llm = FlotorchLangChainLLM(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com",
            temperature=0.7
        )
        llm._llm = mock_langchain_llm
        return llm


@pytest.fixture
def langchain_llm_instance_async(mock_langchain_llm_async):
    """Create FlotorchLangChainLLM instance with mocked FlotorchLLM (async).
    
    Args:
        mock_langchain_llm_async: Mocked async FlotorchLLM fixture
        
    Returns:
        FlotorchLangChainLLM: Instance with mocked async LLM dependency
    """
    with patch('flotorch.langchain.llm.FlotorchLLM', return_value=mock_langchain_llm_async):
        from flotorch.langchain.llm import FlotorchLangChainLLM
        llm = FlotorchLangChainLLM(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com",
            temperature=0.7
        )
        llm._llm = mock_langchain_llm_async
        return llm

