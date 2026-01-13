"""Tests for FlotorchStrandsAgent."""

import pytest
from unittest.mock import Mock
from pydantic import BaseModel

from flotorch.strands.agent import (
    FlotorchStrandsAgent,
    AgentProxy,
    sanitize_agent_name,
    schema_to_pydantic_model
)
from flotorch.strands.tests.test_data.agent_test_data import (
    MINIMAL_CONFIG,
    CONFIG_WITH_OUTPUT_SCHEMA,
    CONFIG_WITH_SYNC,
    CONFIG_WITH_MCP_TOOLS,
    CONFIG_MODIFIED,
    SANITIZE_NAME_DATA,
    MockTool,
    MockMCPTool
)


class TestHelperFunctions:
    """Test utility helper functions."""

    @pytest.mark.parametrize(
        "test_id,input_name,expected",
        SANITIZE_NAME_DATA,
        ids=[data[0] for data in SANITIZE_NAME_DATA]
    )
    def test_sanitize_agent_name(self, test_id, input_name, expected):
        """Test agent name sanitization."""
        result = sanitize_agent_name(input_name)
        assert result == expected

    def test_schema_to_pydantic_model(self):
        """Test dynamic Pydantic model creation from JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "Answer": {"type": "string", "description": "Response"},
                "confidence": {"type": "number", "description": "Score"}
            }
        }
        model = schema_to_pydantic_model("OutputSchema", schema)
        assert issubclass(model, BaseModel)
        instance = model(Answer="test", confidence=0.9)
        assert (instance.Answer == "test" and
                instance.confidence == 0.9)


class TestInitialization:
    """Test FlotorchStrandsAgent initialization."""

    def test_init_with_all_params(self, mock_agent_deps, agent_test_data):
        """Test successful initialization with all parameters."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert (agent_manager.agent_name == agent_test_data["agent_name"]
                and agent_manager.base_url == agent_test_data["base_url"]
                and agent_manager.api_key == agent_test_data["api_key"]
                and agent_manager.config == MINIMAL_CONFIG and
                agent_manager._llm is not None and
                agent_manager._agent is not None)

    def test_init_with_custom_tools(self, mock_agent_deps, agent_test_data):
        """Test initialization with custom tools."""
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            custom_tools=custom_tools,
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert agent_manager.custom_tools == custom_tools

    def test_init_requires_base_url(self, monkeypatch):
        """Test initialization fails without base_url."""
        monkeypatch.delenv("FLOTORCH_BASE_URL", raising=False)
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        with pytest.raises(
            ValueError, match="base_url and api_key are required"
        ):
            FlotorchStrandsAgent(
                agent_name="test-agent", api_key="test-key"
            )

    def test_init_requires_api_key(self, monkeypatch):
        """Test initialization fails without api_key."""
        monkeypatch.delenv("FLOTORCH_BASE_URL", raising=False)
        monkeypatch.delenv("FLOTORCH_API_KEY", raising=False)
        with pytest.raises(
            ValueError, match="base_url and api_key are required"
        ):
            FlotorchStrandsAgent(
                agent_name="test-agent", base_url="https://test.com"
            )


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    def test_constructs_correct_api_url(
        self, mock_agent_deps, agent_test_data
    ):
        """Test correct API URL construction and headers."""
        FlotorchStrandsAgent(
            agent_name="my-agent",
            base_url="https://api.test.com",
            api_key="key123"
        )
        mock_agent_deps['http_get'].assert_called_with(
            "https://api.test.com/v1/agents/my-agent",
            headers={
                "Authorization": "Bearer key123",
                "Content-Type": "application/json"
            }
        )

    def test_propagates_api_errors(self, mock_agent_deps, agent_test_data):
        """Test API errors are properly propagated."""
        mock_agent_deps['http_get'].side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            FlotorchStrandsAgent(
                agent_name=agent_test_data["agent_name"],
                base_url=agent_test_data["base_url"],
                api_key=agent_test_data["api_key"]
            )


class TestAgentBuilding:
    """Test Strands agent building."""

    def test_creates_llm_with_correct_params(
        self, mock_agent_deps, agent_test_data
    ):
        """Test LLM is initialized with correct parameters."""
        FlotorchStrandsAgent(
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
        self, mock_agent_deps, agent_test_data
    ):
        """Test agent with outputSchema stores schema correctly."""
        mock_agent_deps['http_get'].return_value = (
            CONFIG_WITH_OUTPUT_SCHEMA
        )
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert agent_manager._agent._output_schema is not None

    def test_creates_agent_without_output_schema(
        self, mock_agent_deps, agent_test_data
    ):
        """Test agent without outputSchema works correctly."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert agent_manager._agent is not None


class TestToolIntegration:
    """Test tool integration (custom and MCP tools)."""

    def test_includes_custom_tools(self, mock_agent_deps, agent_test_data):
        """Test custom tools are added to agent."""
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            custom_tools=custom_tools,
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        call_kwargs = mock_agent_deps['agent'].call_args[1]
        assert call_kwargs['tools'] == custom_tools

    def test_handles_mcp_tools_in_config(
        self, mock_agent_deps, agent_test_data
    ):
        """Test MCP tools configuration is processed."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        assert (agent_manager._agent is not None and
                len(agent_manager._mcp_configs) == 1 and
                agent_manager._mcp_configs[0]["name"] ==
                "read-wiki-structure")

    def test_mcp_tools_loaded_at_runtime(
        self, mock_agent_deps, agent_test_data
    ):
        """Test MCP tools are loaded at runtime, not at build time."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        call_kwargs = mock_agent_deps['agent'].call_args[1]
        assert call_kwargs['tools'] == []


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    def test_sync_disabled_skips_fetch(
        self, mock_agent_deps, agent_test_data
    ):
        """Test sync disabled doesn't fetch config repeatedly."""
        agent_manager = FlotorchStrandsAgent(
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
        self, mock_agent_deps, agent_test_data
    ):
        """Test sync only triggers after interval passes."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['time'].time.return_value = 1005.0
        agent_manager._get_synced_agent()
        mock_agent_deps['http_get'].assert_not_called()

    def test_sync_rebuilds_on_config_change(
        self, mock_agent_deps, agent_test_data
    ):
        """Test agent rebuild when config changes."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        mock_agent_deps['http_get'].return_value = CONFIG_MODIFIED
        mock_agent_deps['time'].time.return_value = 1015.0
        new_agent = Mock()
        mock_agent_deps['agent'].return_value = new_agent
        mock_agent_deps['http_get'].reset_mock()
        mock_agent_deps['agent'].reset_mock()
        agent_manager._get_synced_agent()
        assert (mock_agent_deps['http_get'].called and
                mock_agent_deps['agent'].called and
                agent_manager.config == CONFIG_MODIFIED)

    def test_sync_handles_failures(
        self, mock_agent_deps, agent_test_data, capsys
    ):
        """Test sync failures don't break agent functionality."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        original_agent = agent_manager._agent
        mock_agent_deps['http_get'].side_effect = Exception(
            "Network error"
        )
        mock_agent_deps['time'].time.return_value = 1015.0
        result = agent_manager._get_synced_agent()
        assert result == original_agent


class TestProxyPattern:
    """Test proxy pattern for transparent sync."""

    def test_get_agent_returns_proxy(
        self, mock_agent_deps, agent_test_data
    ):
        """Test get_agent returns AgentProxy instance."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        agent_proxy = agent_manager.get_agent()
        assert (isinstance(agent_proxy, AgentProxy) and
                agent_proxy._manager == agent_manager)

    def test_proxy_delegates_attribute_access(
        self, mock_agent_deps, agent_test_data
    ):
        """Test AgentProxy delegates to underlying agent."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        proxy = agent_manager.get_agent()
        tool_registry = proxy.tool_registry
        assert tool_registry == agent_manager._agent.tool_registry

    def test_proxy_call_without_mcp_tools(
        self, mock_agent_deps, agent_test_data
    ):
        """Test proxy call without MCP tools uses regular agent call."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        proxy = agent_manager.get_agent()
        result = proxy("test prompt")
        assert result == {"response": "Mock response to: test prompt"}

    def test_proxy_call_with_structured_output(
        self, mock_agent_deps, agent_test_data
    ):
        """Test proxy call with structured output schema."""
        mock_agent_deps['http_get'].return_value = (
            CONFIG_WITH_OUTPUT_SCHEMA
        )
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        proxy = agent_manager.get_agent()
        result = proxy("test prompt")
        expected = {"Answer": "Structured response to: {'response': "
                    "'Mock response to: test prompt'}"}
        assert result == expected

    def test_proxy_call_with_mcp_tools(
        self, mock_agent_deps, agent_test_data
    ):
        """Test proxy call with MCP tools loads tools at runtime."""
        mock_agent_deps['http_get'].return_value = CONFIG_WITH_MCP_TOOLS
        from flotorch.strands.tests.test_data.agent_test_data import (
            MockMCPTool, MockMCPClient
        )
        mcp_tools = [MockMCPTool("read_wiki_structure")]
        mock_mcp = MockMCPClient(tools=mcp_tools)
        mock_agent_deps['mcp_client'].return_value = mock_mcp
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        proxy = agent_manager.get_agent()
        result = proxy("test prompt")
        assert (mock_mcp.entered and mock_mcp.exited and
                result is not None)


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(
        self, mock_agent_deps, agent_test_data
    ):
        """Test complete agent initialization and usage workflow."""
        agent_manager = FlotorchStrandsAgent(
            agent_name=agent_test_data["agent_name"],
            base_url=agent_test_data["base_url"],
            api_key=agent_test_data["api_key"]
        )
        agent_proxy = agent_manager.get_agent()
        result = agent_proxy("Hello, how are you?")
        assert (mock_agent_deps['http_get'].called and
                mock_agent_deps['llm'].called and
                mock_agent_deps['agent'].called and
                result is not None)
