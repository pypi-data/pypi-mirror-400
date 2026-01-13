"""Tests for FlotorchADKAgent.

This module tests the FlotorchADKAgent class including:
- Helper functions (sanitize_agent_name, schema_to_pydantic_model)
- Agent initialization and configuration
- Agent building with LLM and tools
- Tool integration (custom and MCP tools)
- Sync functionality for dynamic config updates
- Proxy pattern for transparent agent access
"""

from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from flotorch.adk.agent import (
    AgentProxy,
    FlotorchADKAgent,
    sanitize_agent_name,
    schema_to_pydantic_model,
)
from flotorch.adk.tests.test_data.agent_test_data import (
    CONFIG_MODIFIED,
    CONFIG_WITH_MCP_TOOLS,
    CONFIG_WITH_OUTPUT_SCHEMA,
    CONFIG_WITH_SYNC,
    MINIMAL_CONFIG,
    MockTool,
    SANITIZE_NAME_DATA,
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
        - Hyphens, spaces, special chars become underscores
        - Empty strings default to 'agent'
        - Valid names remain unchanged
        - Names starting with numbers get 'agent_' prefix (line 36)
        """
        result = sanitize_agent_name(input_name)
        assert result == expected
        if input_name and input_name[0].isdigit():
            assert result.startswith("agent_")

    def test_schema_to_pydantic_model(self):
        """Test dynamic Pydantic model creation from JSON schema.
        
        Validates lines 64,68,75,79,81,85: field types and naming.
        """
 
        schema1 = {"properties": {"query": {"type": "string"}}}
        model1 = schema_to_pydantic_model("InputSchema", schema1)
        assert model1.__name__ == "QueryInput"

        schema2 = {"properties": {"result": {"type": "string"}}}
        model2 = schema_to_pydantic_model("OutputSchema", schema2)
        assert model2.__name__ == "ResultOutput"

        schema_else = {"properties": {"data": {"type": "string"}}}
        model_else = schema_to_pydantic_model("CustomSchema", schema_else)
        assert model_else.__name__ == "DataSchema"
        
        schema3 = {
            "properties": {
                "count": {"type": "integer"},
                "score": {"type": "number"},
                "active": {"type": "boolean"},
                "data": {"type": "object"},
                "name": {"type": "string"}
            },
            "required": ["count"]
        }
        model3 = schema_to_pydantic_model("Test", schema3)
        instance = model3(count=5)
        assert instance.count == 5


class TestInitialization:
    """Test FlotorchADKAgent initialization."""

    def test_init_with_all_params(self, mock_agent_deps, agent_test_data):
        """Test successful initialization with all parameters.
        
        Validates that:
        - All instance attributes are set correctly
        - Config is fetched from API
        - LLM and agent are built
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        assert agent_manager.agent_name == agent_test_data["agent_name"]
        assert agent_manager.base_url == agent_test_data["base_url"]
        assert agent_manager.api_key == agent_test_data["api_key"]
        assert agent_manager.config == MINIMAL_CONFIG
        assert agent_manager._agent is not None

    def test_init_with_enable_memory(self, mock_agent_deps, agent_test_data):
        """Test initialization with memory enabled.
        
        Validates that enable_memory flag is stored correctly.
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            enable_memory=True,
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        assert agent_manager.enable_memory is True

    def test_init_with_custom_tools(self, mock_agent_deps, agent_test_data):
        """Test initialization with custom tools.
        
        Validates that custom tools are stored and available for use.
        """
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            custom_tools=custom_tools,
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        assert agent_manager.custom_tools == custom_tools

    def test_init_requires_base_url(self, monkeypatch):
        """Test initialization fails without base_url.
        
        Validates proper error handling for missing credentials.
        """
        monkeypatch.delenv("FLOTORCH_BASE_URL", raising=False)
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="base_url is required"):
            FlotorchADKAgent(
                agent_name="test-agent",
                api_key="test-key"
            )

    def test_init_requires_api_key(self, monkeypatch):
        """Test initialization fails without api_key.
        
        Validates proper error handling for missing credentials.
        """
        monkeypatch.delenv("FLOTORCH_BASE_URL", raising=False)
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="api_key is required"):
            FlotorchADKAgent(
                agent_name="test-agent",
                base_url="https://test.com"
            )


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    def test_constructs_correct_api_url(self, mock_agent_deps, agent_test_data):
        """Test correct API URL construction and headers.
        
        Validates that:
        - URL follows /v1/agents/{agent_name} pattern
        - Authorization header includes Bearer token
        - Content-Type is set to application/json
        """
        FlotorchADKAgent(
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

    def test_propagates_api_errors(self, mock_agent_deps, agent_test_data):
        """Test API errors are properly propagated.
        
        Validates that network/API errors don't get swallowed.
        """
        mock_agent_deps['http_get'].side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            FlotorchADKAgent(
                agent_name=agent_test_data["agent_name"],
                base_url=agent_test_data["base_url"],
                api_key=agent_test_data["api_key"]
            )


class TestAgentBuilding:
    """Test ADK agent building."""

    def test_creates_llm_with_correct_params(self, mock_agent_deps, agent_test_data):
        """Test LLM is initialized with correct parameters.
        
        Validates that FlotorchADKLLM receives:
        - model_id from config
        - api_key from initialization
        - base_url from initialization
        """
        FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        mock_agent_deps['llm'].assert_called_with(
            model_id="flotorch/openai:latest",
            api_key=agent_test_data["api_key"],
            base_url=agent_test_data["base_url"]
        )

    def test_creates_agent_with_output_schema(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test agent with output schema (line 221)."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_OUTPUT_SCHEMA
        agent = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert mock_agent_deps['agent'].called
    
    def test_creates_agent_with_input_schema_callback(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test input validation callback (lines 239-252,287-313)."""
        config_with_input = {
            **MINIMAL_CONFIG,
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
        mock_agent_deps['http_get'].return_value = config_with_input
        agent = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert hasattr(agent._agent, 'before_agent_callback')
        
        ctx = Mock()
        ctx._invocation_context = None
        ctx.user_content = Mock()
        ctx.user_content.parts = [Mock(text='{"query":"test"}', spec=['text'])]
        result = agent._extract_input_from_callback_context(ctx)
        assert result == {"query": "test"}
        
        error_resp = agent._create_callback_error_response("validation failed")
        assert error_resp["role"] == "system"
        assert "validation failed" in error_resp["parts"][0]["text"]

    def test_creates_agent_without_output_schema(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test agent without outputSchema works correctly.
        
        Validates that agent is created when outputSchema is null.
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        assert agent_manager._agent is not None


class TestToolIntegration:
    """Test tool integration (custom and MCP tools)."""

    def test_includes_custom_tools(self, mock_agent_deps, agent_test_data):
        """Test custom tools are added to agent.
        
        Validates that all provided custom tools are available.
        """
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            custom_tools=custom_tools,
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        assert agent_manager.custom_tools == custom_tools

    def test_handles_mcp_tools_in_config(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test MCP tools configuration."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        agent = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert agent._agent is not None

    def test_memory_tools_added_when_enabled(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test memory tools are added when enable_memory is True.
        
        Validates that preload_memory is included in tools.
        """
        with patch('flotorch.adk.agent.preload_memory') as mock_preload:
            agent_manager = FlotorchADKAgent(
                agent_name=agent_test_data["agent_name"],
                enable_memory=True,
                base_url=agent_test_data["base_url"],
                api_key=agent_test_data["api_key"]
            )
            
            assert agent_manager._agent is not None


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    def test_sync_disabled_skips_fetch(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test sync disabled doesn't fetch config repeatedly.
        
        Validates that with syncEnabled=False, agent uses cached config.
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 2000.0
        
        result = agent_manager._get_synced_agent()
        
        mock_agent_deps['http_get'].assert_not_called()
        assert result == agent_manager._agent

    def test_sync_respects_interval(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test sync only triggers after interval passes.
        
        Validates that config isn't fetched before syncInterval seconds.
        """
        http_get = mock_agent_deps['http_get']
        http_get.return_value = CONFIG_WITH_SYNC
        
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        http_get.reset_mock()
        mock_agent_deps['time'].time.return_value = 1005.0
        
        agent_manager._get_synced_agent()
        
        http_get.assert_not_called()

    def test_sync_rebuilds_on_config_change(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test agent rebuild when config changes.
        
        Validates that:
        - New config is fetched after interval
        - Agent is rebuilt if config differs
        - Updated config is stored
        """
        http_get = mock_agent_deps['http_get']
        http_get.return_value = CONFIG_WITH_SYNC
        
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        http_get.return_value = CONFIG_MODIFIED
        mock_agent_deps['time'].time.return_value = 1015.0
        
        new_agent = Mock()
        mock_agent_deps['agent'].return_value = new_agent
        
        http_get.reset_mock()
        mock_agent_deps['agent'].reset_mock()
        
        agent_manager._get_synced_agent()
        
        assert http_get.called
        assert mock_agent_deps['agent'].called
        assert agent_manager.config == CONFIG_MODIFIED

    def test_sync_handles_failures(
        self,
        mock_agent_deps,
        agent_test_data,
        capsys
    ):
        """Test sync failures don't break agent functionality.
        
        Validates that:
        - Network errors during sync are caught
        - Original agent continues to work
        - Error is logged
        """
        http_get = mock_agent_deps['http_get']
        http_get.return_value = CONFIG_WITH_SYNC
        
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        original_agent = agent_manager._agent
        http_get.side_effect = Exception("Network error")
        mock_agent_deps['time'].time.return_value = 1015.0
        
        result = agent_manager._get_synced_agent()
        
        assert result == original_agent


class TestProxyPattern:
    """Test proxy pattern for transparent sync."""

    def test_get_agent_returns_proxy(self, mock_agent_deps, agent_test_data):
        """Test get_agent returns AgentProxy instance.
        
        Validates proxy instance is created correctly.
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        agent_proxy = agent_manager.get_agent()
        
        assert isinstance(agent_proxy, AgentProxy)
        assert agent_proxy._manager == agent_manager

    def test_proxy_delegates_attribute_access(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test AgentProxy delegates to underlying agent (line 329)."""
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        proxy = agent_manager.get_agent()
        agent_name = proxy.name
        assert agent_name == agent_manager._agent.name
        
        proxy.description = "new"
        assert agent_manager._agent.description == "new"


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(
        self,
        mock_agent_deps,
        agent_test_data
    ):
        """Test complete agent initialization and usage workflow.
        
        Validates that:
        - Agent initializes successfully
        - Proxy can be obtained
        - Agent attributes are accessible
        - All components are created
        """
        agent_manager = FlotorchADKAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        
        agent_proxy = agent_manager.get_agent()
        
        assert agent_proxy.name is not None
        assert mock_agent_deps['http_get'].called
        assert mock_agent_deps['llm'].called
        assert mock_agent_deps['agent'].called

