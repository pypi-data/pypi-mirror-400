"""Tests for FlotorchCrewAIAgent.

This module tests the FlotorchCrewAIAgent class including:
- Helper functions (sanitize_agent_name, schema_to_pydantic_model)
- Agent initialization and configuration
- Agent and task building with LLM
- Tool integration (custom and MCP tools)
- Sync functionality for dynamic config updates
- Proxy pattern for transparent agent/task access
"""

import pytest
from unittest.mock import Mock
from pydantic import BaseModel

from flotorch.crewai.agent import (
    FlotorchCrewAIAgent,
    AgentProxy,
    TaskProxy,
    sanitize_agent_name,
    schema_to_pydantic_model
)
from flotorch.crewai.tests.test_data.agent_test_data import (
    MINIMAL_CONFIG,
    CONFIG_WITH_SCHEMA,
    CONFIG_WITH_SYNC,
    CONFIG_MODIFIED,
    SANITIZE_NAME_DATA,
    MockTool
)


class TestHelperFunctions:
    """Test utility helper functions."""

    @pytest.mark.parametrize(
        "test_id,input_name,expected",
        SANITIZE_NAME_DATA,
        ids=[data[0] for data in SANITIZE_NAME_DATA]
    )
    def test_sanitize_agent_name(self, test_id, input_name, expected):
        """Test agent name sanitization removes invalid characters.
        
        Validates that:
        - Hyphens and spaces become underscores
        - Empty strings default to 'agent'
        - Valid names remain unchanged
        """
        assert sanitize_agent_name(input_name) == expected

    def test_schema_to_pydantic_model(self):
        """Test dynamic Pydantic model creation from JSON schema.
        
        Validates that:
        - Model is a valid Pydantic BaseModel
        - Model fields match schema properties
        - Model instances can be created and validated
        """
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        model = schema_to_pydantic_model("TestModel", schema)
        
        assert issubclass(model, BaseModel)
        instance = model(name="test", age=25)
        assert instance.name == "test"
        assert instance.age == 25


class TestInitialization:
    """Test FlotorchCrewAIAgent initialization."""

    def test_init_with_all_params(self, mock_agent_deps):
        """Test successful initialization with all parameters.
        
        Validates that:
        - All instance attributes are set correctly
        - Config is fetched from API
        - Agent and task are built
        """
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.agent_name == "test-agent"
        assert agent.base_url == "https://test.com"
        assert agent.api_key == "test-key"
        assert agent.config == MINIMAL_CONFIG
        assert agent._agent is not None
        assert agent._task is not None

    def test_init_with_custom_tools(self, mock_agent_deps):
        """Test initialization with custom tools.
        
        Validates that custom tools are stored and available for use.
        """
        custom_tools = [MockTool(), MockTool("custom")]
        
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.custom_tools == custom_tools

    def test_init_requires_base_url(self):
        """Test initialization fails without base_url.
        
        Validates proper error handling for missing credentials.
        """
        with pytest.raises(ValueError, match="base_url is required"):
            FlotorchCrewAIAgent(
                agent_name="test-agent",
                api_key="test-key"
            )

    def test_init_requires_api_key(self):
        """Test initialization fails without api_key.
        
        Validates proper error handling for missing credentials.
        """
        with pytest.raises(ValueError, match="api_key is required"):
            FlotorchCrewAIAgent(
                agent_name="test-agent",
                base_url="https://test.com"
            )


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    def test_constructs_correct_api_url(self, mock_agent_deps):
        """Test correct API URL construction and headers.
        
        Validates that:
        - URL follows /v1/agents/{agent_name} pattern
        - Authorization header includes Bearer token
        - Content-Type is set to application/json
        """
        FlotorchCrewAIAgent(
            agent_name="my-agent",
            base_url="https://api.test.com",
            api_key="key123"
        )
        
        expected_url = "https://api.test.com/v1/agents/my-agent"
        expected_headers = {
            "Authorization": "Bearer key123",
            "Content-Type": "application/json"
        }
        
        mock_agent_deps['http_get'].assert_called_with(
            expected_url,
            headers=expected_headers
        )

    def test_propagates_api_errors(self, mock_agent_deps):
        """Test API errors are properly propagated.
        
        Validates that network/API errors don't get swallowed.
        """
        mock_agent_deps['http_get'].side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            FlotorchCrewAIAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )


class TestAgentBuilding:
    """Test CrewAI agent and task building."""

    def test_creates_llm_with_correct_params(self, mock_agent_deps):
        """Test LLM is initialized with correct parameters.
        
        Validates that FlotorchCrewAILLM receives:
        - model_id from config
        - api_key from initialization
        - base_url from initialization
        """
        FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['llm'].assert_called_once_with(
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com"
        )

    def test_creates_task_with_output_schema(self, mock_agent_deps):
        """Test task with outputSchema includes Pydantic model.
        
        Validates that output_pydantic is set when outputSchema exists.
        """
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SCHEMA
        
        FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        task_kwargs = mock_agent_deps['task'].call_args[1]
        assert 'output_pydantic' in task_kwargs

    def test_creates_task_without_output_schema(self, mock_agent_deps):
        """Test task without outputSchema works correctly.
        
        Validates that output_pydantic is not set when outputSchema is null.
        """
        FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        task_kwargs = mock_agent_deps['task'].call_args[1]
        assert 'output_pydantic' not in task_kwargs


class TestToolIntegration:
    """Test tool integration (custom and MCP tools)."""

    def test_includes_custom_tools(self, mock_agent_deps):
        """Test custom tools are added to agent.
        
        Validates that all provided custom tools are available.
        """
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        
        FlotorchCrewAIAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        agent_kwargs = mock_agent_deps['agent'].call_args[1]
        tools = agent_kwargs['tools']
        
        assert all(tool in tools for tool in custom_tools)

    def test_creates_mcp_tools_correctly(self, mock_agent_deps):
        """Test MCP tools are created with correct parameters.
        
        Validates that:
        - MCPServerAdapter is called for MCP tools
        - Connection params include correct transport type
        - Authorization header is added
        """
        config_with_mcp = {
            **MINIMAL_CONFIG,
            "tools": [{
                "type": "MCP",
                "name": "test-mcp",
                "config": {
                    "transport": "HTTP_STREAMABLE",
                    "headers": {}
                }
            }]
        }
        mock_agent_deps['http_get'].return_value = config_with_mcp
        
        mcp_tool = MockTool("mcp_tool")
        mcp_adapter = Mock(tools=[mcp_tool])
        mock_agent_deps['mcp'].return_value = mcp_adapter
        
        FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert mock_agent_deps['mcp'].called
        
        conn_params = mock_agent_deps['mcp'].call_args[0][0]
        assert conn_params["transport"] == "streamable-http"
        assert "Authorization" in conn_params["headers"]

    def test_handles_mcp_failures_gracefully(self, mock_agent_deps):
        """Test MCP connection failures don't prevent agent creation.
        
        Validates graceful degradation when MCP tools fail to connect.
        """
        config_with_mcp = {
            **MINIMAL_CONFIG,
            "tools": [{
                "type": "MCP",
                "name": "failing-tool",
                "config": {
                    "transport": "HTTP_STREAMABLE",
                    "headers": {}
                }
            }]
        }
        mock_agent_deps['http_get'].return_value = config_with_mcp
        mock_agent_deps['mcp'].side_effect = Exception("Connection failed")
        
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent._agent is not None


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    def test_sync_disabled_skips_fetch(self, mock_agent_deps):
        """Test sync disabled doesn't fetch config repeatedly.
        
        Validates that with syncEnabled=False, agent uses cached config.
        """
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 2000.0
        
        result = agent._get_synced_agent()
        
        mock_agent_deps['http_get'].assert_not_called()
        assert result == agent._agent

    def test_sync_respects_interval(self, mock_agent_deps):
        """Test sync only triggers after interval passes.
        
        Validates that config isn't fetched before syncInterval seconds.
        """
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 1005.0
        
        agent._get_synced_agent()
        
        mock_agent_deps['http_get'].assert_not_called()

    def test_sync_rebuilds_on_config_change(self, mock_agent_deps):
        """Test agent/task rebuild when config changes.
        
        Validates that:
        - New config is fetched after interval
        - Agent and task are rebuilt if config differs
        - Updated config is stored
        """
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['http_get'].return_value = CONFIG_MODIFIED
        mock_agent_deps['time'].time.return_value = 1015.0
        
        new_agent = Mock(role="new-role", tools=[])
        new_task = Mock(description="new-desc")
        mock_agent_deps['agent'].return_value = new_agent
        mock_agent_deps['task'].return_value = new_task
        
        mock_agent_deps['agent'].reset_mock()
        mock_agent_deps['task'].reset_mock()
        
        agent._get_synced_agent()
        
        assert mock_agent_deps['http_get'].called
        assert mock_agent_deps['agent'].called
        assert mock_agent_deps['task'].called
        assert agent.config == CONFIG_MODIFIED

    def test_sync_handles_failures(self, mock_agent_deps, capsys):
        """Test sync failures don't break agent functionality.
        
        Validates that:
        - Network errors during sync are caught
        - Original agent continues to work
        - Warning is logged
        """
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        
        agent = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        original_agent = agent._agent
        mock_agent_deps['http_get'].side_effect = Exception("Network error")
        mock_agent_deps['time'].time.return_value = 1015.0
        
        result = agent._get_synced_agent()
        
        assert result == original_agent
        
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "Sync" in captured.out


class TestProxyPattern:
    """Test proxy pattern for transparent sync."""

    def test_agent_proxy_delegates_attributes(self, mock_agent_deps):
        """Test AgentProxy delegates to underlying agent.
        
        Validates transparent attribute access through proxy.
        """
        manager = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        proxy = manager.get_agent()
        
        assert proxy.role == manager._agent.role

    def test_task_proxy_delegates_attributes(self, mock_agent_deps):
        """Test TaskProxy delegates to underlying task.
        
        Validates transparent attribute access through proxy.
        """
        manager = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        proxy = manager.get_task()
        
        assert proxy.description == manager._task.description

    def test_proxies_return_correct_types(self, mock_agent_deps):
        """Test get_agent/get_task return correct proxy types.
        
        Validates proxy instances are created correctly.
        """
        manager = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        agent_proxy = manager.get_agent()
        task_proxy = manager.get_task()
        
        assert isinstance(agent_proxy, AgentProxy)
        assert isinstance(task_proxy, TaskProxy)


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(self, mock_agent_deps):
        """Test complete agent initialization and usage workflow.
        
        Validates that:
        - Agent initializes successfully
        - Proxies can be obtained
        - Attributes are accessible
        - All components are created
        """
        manager = FlotorchCrewAIAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        agent = manager.get_agent()
        task = manager.get_task()
        
        assert agent.role is not None
        assert task.description is not None
        assert mock_agent_deps['http_get'].called
        assert mock_agent_deps['agent'].called
        assert mock_agent_deps['task'].called
        assert mock_agent_deps['llm'].called
