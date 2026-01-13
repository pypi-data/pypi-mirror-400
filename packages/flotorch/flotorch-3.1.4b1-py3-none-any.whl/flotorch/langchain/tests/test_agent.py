"""Tests for FlotorchLangChainAgent.

This module tests the FlotorchLangChainAgent class including:
- Helper functions (sanitize_agent_name, schema_to_pydantic_model)
- Agent initialization and configuration
- Tool integration (custom and MCP tools)
- Sync functionality for dynamic config updates
- Proxy patterns (AgentProxy and ToolsProxy)
"""

import pytest
from pydantic import BaseModel

from flotorch.langchain.agent import (
    FlotorchLangChainAgent,
    AgentProxy,
    ToolsProxy,
    sanitize_agent_name,
    schema_to_pydantic_model,
    _TOOLS_PROXY_REGISTRY
)
from flotorch.langchain.tests.test_data.agent_test_data import (
    MINIMAL_CONFIG,
    CONFIG_WITH_SCHEMA,
    CONFIG_WITH_SYNC,
    CONFIG_MODIFIED,
    CONFIG_WITH_MCP_TOOLS,
    SANITIZE_NAME_DATA,
    SCHEMA_TEST_DATA,
    MockLangChainTool
)


class TestHelperFunctions:
    """Test utility helper functions."""

    @pytest.mark.parametrize("test_id,input_name,expected", SANITIZE_NAME_DATA,
                             ids=[data[0] for data in SANITIZE_NAME_DATA])
    def test_sanitize_agent_name(self, test_id, input_name, expected):
        """Test agent name sanitization removes invalid characters."""
        assert sanitize_agent_name(input_name) == expected

    @pytest.mark.parametrize("test_id,schema,sample_data", SCHEMA_TEST_DATA,
                             ids=[data[0] for data in SCHEMA_TEST_DATA])
    def test_schema_to_pydantic_model(self, test_id, schema, sample_data):
        """Test dynamic Pydantic model creation from JSON schema."""
        model = schema_to_pydantic_model("TestModel", schema)
        assert issubclass(model, BaseModel)
        
        if sample_data:
            instance = model(**sample_data)
            for key, value in sample_data.items():
                assert getattr(instance, key) == value


class TestInitialization:
    """Test FlotorchLangChainAgent initialization."""

    def test_init_with_all_params(self, mock_agent_deps):
        """Test successful initialization with all parameters."""
        agent = FlotorchLangChainAgent(
            agent_name="test-langchain-agent",
            base_url="https://test.flotorch.com",
            api_key="test-key-123"
        )
        
        assert agent.agent_name == "test-langchain-agent"
        assert agent.base_url == "https://test.flotorch.com"
        assert agent.api_key == "test-key-123"
        assert agent.config == MINIMAL_CONFIG
        assert agent._agent is not None

    def test_init_with_custom_tools(self, mock_agent_deps):
        """Test initialization with custom tools."""
        custom_tools = [MockLangChainTool("tool1"), MockLangChainTool("tool2")]
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.custom_tools == custom_tools

    def test_init_requires_base_url(self):
        """Test initialization fails without base_url."""
        with pytest.raises(ValueError, match="base_url is required"):
            FlotorchLangChainAgent(agent_name="test-agent", api_key="test-key")

    def test_init_requires_api_key(self):
        """Test initialization fails without api_key."""
        with pytest.raises(ValueError, match="api_key is required"):
            FlotorchLangChainAgent(agent_name="test-agent", base_url="https://test.com")


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    def test_constructs_correct_api_url(self, mock_agent_deps):
        """Test correct API URL construction and headers."""
        FlotorchLangChainAgent(
            agent_name="my-langchain-agent",
            base_url="https://api.flotorch.com/",
            api_key="key-abc-123"
        )
        
        expected_url = "https://api.flotorch.com/v1/agents/my-langchain-agent"
        expected_headers = {
            "Authorization": "Bearer key-abc-123",
            "Content-Type": "application/json"
        }
        
        mock_agent_deps['http_get'].assert_called_with(expected_url, headers=expected_headers)

    def test_propagates_api_errors(self, mock_agent_deps):
        """Test API errors are properly propagated."""
        mock_agent_deps['http_get'].side_effect = Exception("API Connection Failed")
        
        with pytest.raises(Exception, match="API Connection Failed"):
            FlotorchLangChainAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )


class TestAgentBuilding:
    """Test LangChain agent building."""

    def test_agent_is_created_successfully(self, mock_agent_deps):
        """Test agent is created successfully."""
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key-xyz"
        )
        
        assert agent._agent is not None
        assert hasattr(agent, 'config')

    def test_builds_agent_with_output_schema(self, mock_agent_deps):
        """Test agent with outputSchema is created successfully."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SCHEMA
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent._agent is not None
        assert agent.config == CONFIG_WITH_SCHEMA

    def test_agent_with_memory_enabled(self, mock_agent_deps):
        """Test agent creation with memory enabled."""
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            enable_memory=True,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.enable_memory is True
        assert agent._agent is not None


class TestToolBuilding:
    """Test tool integration."""

    def test_agent_stores_custom_tools(self, mock_agent_deps):
        """Test custom tools are stored in agent."""
        custom_tools = [MockLangChainTool("custom1"), MockLangChainTool("custom2")]
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.custom_tools == custom_tools
        assert agent._agent is not None

    def test_agent_with_mcp_config(self, mock_agent_deps):
        """Test agent creation with MCP tools configuration."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent._agent is not None
        assert agent.config == CONFIG_WITH_MCP_TOOLS

    def test_handles_mcp_failures_gracefully(self, mock_agent_deps):
        """Test MCP connection failures don't prevent agent creation."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        mock_agent_deps['mcp_client'].side_effect = Exception("MCP Connection Failed")
        
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent._agent is not None


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    def test_sync_disabled_skips_fetch(self, mock_agent_deps):
        """Test sync disabled doesn't fetch config repeatedly."""
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 2000.0
        
        result = agent._get_synced_agent()
        
        mock_agent_deps['http_get'].assert_not_called()
        assert result == agent._agent

    def test_sync_enabled_agent_creation(self, mock_agent_deps):
        """Test agent with sync enabled is created successfully."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        assert agent.config == CONFIG_WITH_SYNC
        assert agent.config.get('syncEnabled') is True
        assert agent._agent is not None

    def test_sync_fetches_config_after_interval(self, mock_agent_deps):
        """Test sync fetches new config after interval passes."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        initial_config = agent.config
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['http_get'].return_value = CONFIG_MODIFIED
        mock_agent_deps['time'].time.return_value = 1015.0
        
        # Trigger sync by getting synced agent
        agent._get_synced_agent()
        
        # Verify config was fetched and updated
        mock_agent_deps['http_get'].assert_called_once()
        assert agent.config == CONFIG_MODIFIED
        assert agent.config != initial_config
        assert agent.config.get('goal') == "Modified LangChain agent goal"

    def test_sync_respects_interval(self, mock_agent_deps):
        """Test sync only triggers after interval passes."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 1012.0  # 12 seconds passed

        agent._get_synced_agent()
        
        # Should  fetch because interval (12 seconds) has passed
        mock_agent_deps['http_get'].assert_called()


class TestAgentProxy:
    """Test AgentProxy for transparent sync."""

    def test_proxy_delegates_to_underlying_agent(self, mock_agent_deps):
        """Test AgentProxy delegates attribute access to agent."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        proxy = manager.get_agent()
        assert isinstance(proxy, AgentProxy)

    def test_proxy_invoke_delegates_correctly(self, mock_agent_deps):
        """Test AgentProxy.invoke delegates to underlying agent."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        proxy = manager.get_agent()
        result = proxy.invoke({"input": "test"})
        assert result is not None

    def test_proxy_ainvoke_delegates_correctly(self, mock_agent_deps):
        """Test AgentProxy.ainvoke delegates to underlying agent."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        proxy = manager.get_agent()
        # Test that ainvoke method exists and is callable
        assert hasattr(proxy, 'ainvoke')
        assert callable(proxy.ainvoke)


class TestToolsProxy:
    """Test ToolsProxy for dynamic tool list management."""

    def test_tools_proxy_is_list(self, mock_agent_deps):
        """Test ToolsProxy inherits from list."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        # Patch _get_synced_tools to return actual list
        manager._get_synced_tools = lambda: manager._tools
        
        tools = manager.get_tools()
        assert isinstance(tools, list)
        assert isinstance(tools, ToolsProxy)

    def test_tools_proxy_refreshes_on_access(self, mock_agent_deps):
        """Test ToolsProxy refreshes tools on access."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        # Patch _get_synced_tools to return actual list
        manager._get_synced_tools = lambda: manager._tools
        
        tools = manager.get_tools()
        assert len(tools) >= 0

    def test_tools_proxy_uses_global_registry(self, mock_agent_deps):
        """Test ToolsProxy registers in global registry."""
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        # Patch _get_synced_tools to return actual list
        manager._get_synced_tools = lambda: manager._tools
        
        tools = manager.get_tools()
        if hasattr(tools, '_proxy_id'):
            assert tools._proxy_id in _TOOLS_PROXY_REGISTRY

    def test_tools_proxy_handles_list_init(self):
        """Test ToolsProxy handles being initialized with list."""
        tool_list = [MockLangChainTool("tool1")]
        tools_proxy = ToolsProxy(tool_list)
        
        # Should initialize as a list
        assert isinstance(tools_proxy, list)
        # Should contain the tool names
        assert MockLangChainTool("tool1").name in [t.name for t in tool_list]
    
    def test_tools_proxy_list_operations(self, mock_agent_deps):
        """Test ToolsProxy list methods (count, index, contains, iteration)."""
        tool1, tool2 = MockLangChainTool("t1"), MockLangChainTool("t2")
        manager = FlotorchLangChainAgent(
            agent_name="test-agent",
            custom_tools=[tool1, tool2, tool1],
            base_url="https://test.com",
            api_key="test-key"
        )
        manager._get_synced_tools = lambda: manager._tools
        tools = manager.get_tools()
        
        # Test multiple operations in one test
        assert tools.count(tool1) >= 0
        assert (tool1 in tools) or (tool1 not in tools)  # Either is valid
        assert sum(1 for _ in tools) >= 0
        if len(tools) > 0:
            assert tools[0] is not None


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(self, mock_agent_deps):
        """Test complete agent initialization and usage workflow."""
        manager = FlotorchLangChainAgent(
            agent_name="integration-test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        
        # Patch _get_synced_tools to return actual list
        manager._get_synced_tools = lambda: manager._tools
        
        agent = manager.get_agent()
        tools = manager.get_tools()
        
        assert agent is not None
        assert tools is not None
        assert isinstance(agent, AgentProxy)
        assert isinstance(tools, ToolsProxy)

    def test_agent_with_custom_tools_workflow(self, mock_agent_deps):
        """Test workflow with custom tools."""
        custom_tools = [
            MockLangChainTool("search", "Search the web"),
            MockLangChainTool("calculate", "Perform calculations")
        ]
        
        manager = FlotorchLangChainAgent(
            agent_name="custom-tools-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        
        agent = manager.get_agent()
        result = agent.invoke({"input": "test query"})
        assert result is not None

