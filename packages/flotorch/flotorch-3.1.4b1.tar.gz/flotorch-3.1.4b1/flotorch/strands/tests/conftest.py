"""Pytest fixtures for Strands tests.

This module provides reusable fixtures for testing Strands components.
Mocking only where API calls occur (FlotorchSession SDK client).
"""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def test_data():
    """Common test data for Strands tests."""
    return {
        "api_key": "test_api_key",
        "base_url": "http://test.flotorch.com",
        "app_name": "strands_test_app",
        "user_id": "strands_test_user",
        "session_id": "test_session_123",
        "agent_id": "default",
        "message_id": 0
    }


@pytest.fixture
def mock_session_client():
    """Mock the SDK FlotorchSession client (where API calls occur)."""
    mock_client = Mock()
    
    # Mock create
    mock_client.create.return_value = {
        "uid": "test_session_123",
        "appName": "strands_test_app",
        "userId": "strands_test_user"
    }
    
    # Mock get - returns Mock object with events attribute
    session_mock = Mock()
    session_mock.uid = "test_session_123"
    session_mock.events = []
    mock_client.get.return_value = session_mock
    
    # Mock add_event
    mock_client.add_event.return_value = {"uid_event": "e1"}
    
    return mock_client


@pytest.fixture
def strands_session(test_data, mock_session_client, monkeypatch):
    """Create FlotorchStrandsSession instance with mocked SDK client."""
    from flotorch.strands.session import FlotorchStrandsSession
    
    instance = FlotorchStrandsSession(
        api_key=test_data["api_key"],
        base_url=test_data["base_url"],
        app_name=test_data["app_name"],
        user_id=test_data["user_id"]
    )
    
    # Mock the SDK session client (where API calls happen)
    monkeypatch.setattr(instance, "session_client", mock_session_client)
    
    return instance


@pytest.fixture
def mock_strands_session_obj():
    """Create mock Strands Session object."""
    from strands.types.session import Session, SessionType
    return Session(
        session_id="test_session_123",
        session_type=SessionType.AGENT
    )


@pytest.fixture
def mock_strands_agent():
    """Create mock Strands SessionAgent object."""
    from strands.types.session import SessionAgent
    return SessionAgent(
        agent_id="default",
        state={},
        conversation_manager_state={
            "__name__": "SlidingWindowConversationManager",
            "removed_message_count": 0
        }
    )


# Memory Fixtures

@pytest.fixture
def memory_test_data():
    """Common test data for Strands Memory tests."""
    return {
        "api_key": "test-api-key",
        "base_url": "https://test.flotorch.com",
        "provider_name": "test-provider",
        "user_id": "test-user-15",
        "app_id": "test-app-15"
    }


@pytest.fixture
def mock_flotorch_memory():
    """Mock FlotorchMemory SDK client."""
    mock_memory = Mock()
    
    # Mock add operation
    mock_memory.add.return_value = {
        "object": "agent.memory.list",
        "data": [
            {
                "id": "test-memory-id",
                "content": "Test content"
            }
        ]
    }
    
    # Mock search operation
    mock_memory.search.return_value = {
        "object": "agent.memory.list",
        "data": []
    }
    
    return mock_memory


@pytest.fixture
def strands_memory_tool(memory_test_data, mock_flotorch_memory, monkeypatch):
    """Create FlotorchMemoryTool instance with mocked SDK."""
    from flotorch.strands.memory import FlotorchMemoryTool
    
    # Create instance
    tool = FlotorchMemoryTool(
        api_key=memory_test_data["api_key"],
        base_url=memory_test_data["base_url"],
        provider_name=memory_test_data["provider_name"],
        user_id=memory_test_data["user_id"],
        app_id=memory_test_data["app_id"]
    )
    
    # Replace the SDK memory instance with our mock
    monkeypatch.setattr(tool, "memory", mock_flotorch_memory)
    
    return tool


@pytest.fixture
def mock_tool_use():
    """Create mock ToolUse object."""
    def _create_tool_use(tool_use_id="test-tool-use-id", action="add", **kwargs):
        return {
            "toolUseId": tool_use_id,
            "name": "flotorch_memory",
            "input": {"action": action, **kwargs}
        }
    return _create_tool_use


# Agent Fixtures

@pytest.fixture
def agent_test_data():
    """Common test data for Strands Agent tests."""
    return {
        "agent_name": "test-agent",
        "api_key": "test-api-key-123",
        "base_url": "https://test.flotorch.com"
    }


@pytest.fixture
def mock_agent_deps():
    """Mock all external dependencies for Strands agent testing.
    
    Provides comprehensive mocking environment for FlotorchStrandsAgent:
    - HTTP requests (config fetching)
    - FlotorchStrandsModel (LLM)
    - Strands Agent
    - MCPClient (prevents connection attempts)
    - Time module (for sync testing)
    
    Returns:
        dict: Mocked objects
    """
    from unittest.mock import patch
    from flotorch.strands.tests.test_data.agent_test_data import MINIMAL_CONFIG, MockAgent
    
    with patch('flotorch.strands.agent.http_get') as http_mock, \
         patch('flotorch.strands.agent.FlotorchStrandsModel') as llm_mock, \
         patch('flotorch.strands.agent.Agent') as agent_mock, \
         patch('flotorch.strands.agent.MCPClient') as mcp_client_mock, \
         patch('flotorch.strands.agent.time') as time_mock:
        
        # Configure default return values
        http_mock.return_value = MINIMAL_CONFIG
        
        # Mock LLM
        mock_llm_instance = Mock()
        llm_mock.return_value = mock_llm_instance
        
        # Mock Agent with tool registry
        mock_agent_instance = MockAgent()
        agent_mock.return_value = mock_agent_instance
        
        # Mock MCP Client
        from flotorch.strands.tests.test_data.agent_test_data import MockMCPClient
        mock_mcp_instance = MockMCPClient()
        mcp_client_mock.return_value = mock_mcp_instance
        
        # Mock time
        time_mock.time.return_value = 1000.0
        
        yield {
            'http_get': http_mock,
            'llm': llm_mock,
            'llm_instance': mock_llm_instance,
            'agent': agent_mock,
            'agent_instance': mock_agent_instance,
            'mcp_client': mcp_client_mock,
            'mcp_client_instance': mock_mcp_instance,
            'time': time_mock
        }


# LLM Fixtures

@pytest.fixture
def mock_flotorch_llm():
    """Create mock FlotorchLLM instance.
    
    Returns:
        Mock: FlotorchLLM mock with ainvoke response
    """
    from unittest.mock import AsyncMock
    
    mock = AsyncMock()
    mock.ainvoke.return_value = Mock(
        content="test response",
        metadata={"raw_response": {}}
    )
    return mock


@pytest.fixture
def strands_llm_instance(mock_flotorch_llm):
    """Create FlotorchStrandsModel instance with mocked FlotorchLLM.
    
    Args:
        mock_flotorch_llm: Mocked FlotorchLLM fixture
        
    Returns:
        FlotorchStrandsModel: Instance with mocked LLM dependency
    """
    with patch('flotorch.strands.llm.FlotorchLLM', return_value=mock_flotorch_llm):
        from flotorch.strands.llm import FlotorchStrandsModel
        llm = FlotorchStrandsModel(
            model_id="flotorch/openai:latest",
            api_key="test-key",
            base_url="https://test.com"
        )
        llm.flotorch_llm = mock_flotorch_llm
    return llm