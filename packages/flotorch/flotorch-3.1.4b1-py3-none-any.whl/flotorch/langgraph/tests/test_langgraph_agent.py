"""Tests for FlotorchLangGraphAgent."""

import pytest
from unittest.mock import Mock
from pydantic import BaseModel

from flotorch.langgraph.agent import (
    FlotorchLangGraphAgent,
    AgentGraphProxy,
    sanitize_agent_name,
    schema_to_pydantic_model
)
from flotorch.langgraph.tests.test_data.agent_test_data import (
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
        """Test agent name sanitization."""
        assert sanitize_agent_name(input_name) == expected

    def test_schema_to_pydantic_model(self):
        """Test dynamic Pydantic model creation from JSON schema."""
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
        assert instance.name == "test" and instance.age == 25


class TestInitialization:
    """Test FlotorchLangGraphAgent initialization."""

    def test_init_with_all_params(self, mock_agent_graph_deps):
        """Test successful initialization with all parameters."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        assert (agent.agent_name == "test-agent" and
                agent.base_url == "https://test.com" and
                agent.api_key == "test-key" and
                agent.config == MINIMAL_CONFIG and
                agent._llm is not None and
                agent._agent_graph is not None)

    def test_init_with_custom_tools(self, mock_agent_graph_deps):
        """Test initialization with custom tools."""
        custom_tools = [MockTool(), MockTool("custom")]
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        assert agent.custom_tools == custom_tools

    def test_init_requires_base_url(self):
        """Test initialization fails without base_url."""
        with pytest.raises(ValueError, match="base_url and api_key"):
            FlotorchLangGraphAgent(agent_name="test-agent", api_key="test-key")

    def test_init_requires_api_key(self):
        """Test initialization fails without api_key."""
        with pytest.raises(ValueError, match="base_url and api_key"):
            FlotorchLangGraphAgent(
                agent_name="test-agent",
                base_url="https://test.com"
            )


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    def test_constructs_correct_api_url(self, mock_agent_graph_deps):
        """Test correct API URL construction and headers."""
        FlotorchLangGraphAgent(
            agent_name="my-agent",
            base_url="https://api.test.com",
            api_key="key123"
        )
        mock_agent_graph_deps['http_get'].assert_called_with(
            "https://api.test.com/v1/agents/my-agent",
            headers={
                "Authorization": "Bearer key123",
                "Content-Type": "application/json"
            }
        )

    def test_propagates_api_errors(self, mock_agent_graph_deps):
        """Test API errors are properly propagated."""
        mock_agent_graph_deps['http_get'].side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            FlotorchLangGraphAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )


class TestAgentBuilding:
    """Test LangGraph agent graph building."""

    def test_creates_llm_with_correct_params(self, mock_agent_graph_deps):
        """Test LLM is initialized with correct parameters."""
        FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        mock_agent_graph_deps['llm'].assert_called_once_with(
            model_id="openai/gpt-4o-mini",
            api_key="test-key",
            base_url="https://test.com"
        )

    def test_creates_agent_graph_with_output_schema(
        self, mock_agent_graph_deps
    ):
        """Test agent graph with outputSchema."""
        mock_agent_graph_deps['http_get'].return_value = CONFIG_WITH_SCHEMA
        FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        assert mock_agent_graph_deps['asyncio_run'].called

    def test_creates_agent_graph_without_output_schema(
        self, mock_agent_graph_deps
    ):
        """Test agent graph without outputSchema."""
        FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        assert mock_agent_graph_deps['asyncio_run'].called


class TestToolIntegration:
    """Test tool integration (custom and MCP tools)."""

    def test_includes_custom_tools(self, mock_agent_graph_deps):
        """Test custom tools are added to agent."""
        custom_tools = [MockTool("tool1"), MockTool("tool2")]
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            custom_tools=custom_tools,
            base_url="https://test.com",
            api_key="test-key"
        )
        assert agent.custom_tools == custom_tools

    def test_handles_mcp_tools_in_config(self, mock_agent_graph_deps):
        """Test MCP tools configuration is processed."""
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
        mock_agent_graph_deps['http_get'].return_value = config_with_mcp
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        assert agent._agent_graph is not None


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    def test_sync_disabled_skips_fetch(self, mock_agent_graph_deps):
        """Test sync disabled doesn't fetch config repeatedly."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        mock_agent_graph_deps['http_get'].reset_mock()
        mock_agent_graph_deps['time'].time.return_value = 2000.0
        result = agent._get_synced_agent_graph()
        mock_agent_graph_deps['http_get'].assert_not_called()
        assert result == agent._agent_graph

    def test_sync_respects_interval(self, mock_agent_graph_deps):
        """Test sync only triggers after interval passes."""
        mock_agent_graph_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        mock_agent_graph_deps['http_get'].reset_mock()
        mock_agent_graph_deps['time'].time.return_value = 1005.0
        agent._get_synced_agent_graph()
        mock_agent_graph_deps['http_get'].assert_not_called()

    def test_sync_rebuilds_on_config_change(self, mock_agent_graph_deps):
        """Test agent graph rebuild when config changes."""
        mock_agent_graph_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        mock_agent_graph_deps['http_get'].return_value = CONFIG_MODIFIED
        mock_agent_graph_deps['time'].time.return_value = 1015.0
        new_graph = Mock()
        mock_agent_graph_deps['asyncio_run'].return_value = new_graph
        mock_agent_graph_deps['http_get'].reset_mock()
        mock_agent_graph_deps['asyncio_run'].reset_mock()
        agent._get_synced_agent_graph()
        assert mock_agent_graph_deps['http_get'].called
        assert agent.config == CONFIG_MODIFIED

    def test_sync_handles_failures(self, mock_agent_graph_deps, capsys):
        """Test sync failures don't break agent functionality."""
        mock_agent_graph_deps['http_get'].return_value = CONFIG_WITH_SYNC
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        original_graph = agent._agent_graph
        mock_agent_graph_deps['http_get'].side_effect = Exception(
            "Network error"
        )
        mock_agent_graph_deps['time'].time.return_value = 1015.0
        result = agent._get_synced_agent_graph()
        assert result == original_graph


class TestProxyPattern:
    """Test proxy pattern for transparent sync."""

    def test_agent_proxy_delegates_attributes(
        self, mock_agent_graph_deps
    ):
        """Test AgentGraphProxy delegates to underlying agent graph."""
        manager = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        proxy = manager.get_agent()
        assert proxy.invoke == manager._agent_graph.invoke

    def test_proxy_returns_correct_type(self, mock_agent_graph_deps):
        """Test get_agent returns correct proxy type."""
        manager = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        agent_proxy = manager.get_agent()
        assert isinstance(agent_proxy, AgentGraphProxy)


class TestEdgeCases:
    """Minimal edge case tests for coverage."""

    @pytest.mark.asyncio
    async def test_build_mcp_tools_invalid_transport(
        self, mock_agent_graph_deps
    ):
        """Test invalid MCP transport."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        result = await agent._build_mcp_tools({
            "name": "test",
            "config": {"transport": "INVALID"}
        })
        assert result == []

    @pytest.mark.asyncio
    async def test_build_mcp_tools_exception(self, mock_agent_graph_deps):
        """Test MCP build handles exception."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        result = await agent._build_mcp_tools({
            "name": "test",
            "config": {"transport": "HTTP_STREAMABLE"}
        })
        assert isinstance(result, list)

    def test_filter_mcp_tools(self, mock_agent_graph_deps):
        """Test MCP tool filtering."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        tool = Mock()
        tool.name = "test_tool"
        result = agent._filter_mcp_tools([tool], {"name": "test-tool"})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_build_agent_with_goal(self, mock_agent_graph_deps):
        """Test agent build with goal."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        config = {**MINIMAL_CONFIG, "goal": "Help users"}
        result = await agent._build_agent_graph_from_config(config)
        assert result is not None

    @pytest.mark.asyncio
    async def test_build_agent_with_store_and_checkpointer(
        self, mock_agent_graph_deps
    ):
        """Test agent with store/checkpointer."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key",
            store=Mock(),
            checkpointer=Mock()
        )
        result = await agent._build_agent_graph_from_config(MINIMAL_CONFIG)
        assert result is not None

    def test_proxy_setattr(self, mock_agent_graph_deps):
        """Test proxy attribute setting."""
        agent = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        proxy = agent.get_agent()
        proxy.test_attr = "value"

    def test_schema_edge_cases(self):
        """Test schema helpers."""
        assert schema_to_pydantic_model(
            "Test",
            {"properties": {"x": {"type": "number"}}}
        )
        assert schema_to_pydantic_model(
            "Test",
            {"properties": {"y": {"type": "boolean"}}}
        )
        assert sanitize_agent_name("123test").startswith("agent_")

    def test_fetch_config_validation(self, mock_agent_graph_deps):
        """Test _fetch_agent_config validation."""
        agent = FlotorchLangGraphAgent(
            agent_name="test",
            base_url="https://test.com",
            api_key="key"
        )
        agent.base_url = None
        with pytest.raises(ValueError, match="base_url is required"):
            agent._fetch_agent_config("test")
        agent.base_url = "https://test.com"
        agent.api_key = None
        with pytest.raises(ValueError, match="api_key is required"):
            agent._fetch_agent_config("test")

    @pytest.mark.asyncio
    async def test_build_mcp_streamable_success(
        self, mock_agent_graph_deps
    ):
        """Test MCP with HTTP_STREAMABLE transport."""
        from unittest.mock import patch, AsyncMock
        import sys
        mock_mcp = Mock()
        mock_tool = Mock(
            name="tool",
            description="T",
            args_schema={"type": "object"},
            ainvoke=AsyncMock(return_value="ok")
        )
        mock_mcp.MultiServerMCPClient = Mock(
            return_value=Mock(get_tools=AsyncMock(
                return_value=[mock_tool]
            ))
        )
        with patch.dict(
            sys.modules,
            {
                'langchain_mcp_adapters': Mock(),
                'langchain_mcp_adapters.client': mock_mcp
            }
        ):
            agent = FlotorchLangGraphAgent(
                agent_name="test",
                base_url="https://test.com",
                api_key="key"
            )
            result = await agent._build_mcp_tools({
                "name": "test_mcp",
                "config": {
                    "transport": "HTTP_STREAMABLE",
                    "headers": {"X-Test": "val"}
                }
            })
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_build_mcp_sse_and_filter(self, mock_agent_graph_deps):
        """Test MCP SSE transport."""
        from unittest.mock import patch, AsyncMock
        import sys
        mock_mcp = Mock()
        tools = [Mock(
            name="t1",
            description="T",
            args_schema={},
            ainvoke=AsyncMock(return_value="ok")
        )]
        mock_mcp.MultiServerMCPClient = Mock(
            return_value=Mock(get_tools=AsyncMock(return_value=tools))
        )
        with patch.dict(
            sys.modules,
            {
                'langchain_mcp_adapters': Mock(),
                'langchain_mcp_adapters.client': mock_mcp
            }
        ):
            agent = FlotorchLangGraphAgent(
                agent_name="test",
                base_url="https://test.com",
                api_key="key"
            )
            result = await agent._build_mcp_tools({
                "name": "test",
                "config": {"transport": "HTTP_SSE"}
            })
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_build_agent_output_schema_error(
        self, mock_agent_graph_deps, capsys
    ):
        """Test agent build with bad output schema."""
        agent = FlotorchLangGraphAgent(
            agent_name="test",
            base_url="https://test.com",
            api_key="key"
        )
        config = {
            **MINIMAL_CONFIG,
            "outputSchema": {"properties": {"test": {}}}
        }
        result = await agent._build_agent_graph_from_config(config)
        assert result is not None

    @pytest.mark.asyncio
    async def test_build_tools_with_custom_and_mcp(
        self, mock_agent_graph_deps
    ):
        """Test _build_tools with both custom and MCP tools."""
        custom = [MockTool()]
        agent = FlotorchLangGraphAgent(
            agent_name="test",
            base_url="https://test.com",
            api_key="key",
            custom_tools=custom
        )
        config = {
            "tools": [{
                "type": "MCP",
                "name": "test",
                "config": {"transport": "INVALID"}
            }]
        }
        tools = await agent._build_tools(config)
        assert len(tools) >= 1


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(self, mock_agent_graph_deps):
        """Test complete agent initialization and usage workflow."""
        manager = FlotorchLangGraphAgent(
            agent_name="test-agent",
            base_url="https://test.com",
            api_key="test-key"
        )
        agent = manager.get_agent()
        assert agent.invoke is not None
        assert mock_agent_graph_deps['http_get'].called
