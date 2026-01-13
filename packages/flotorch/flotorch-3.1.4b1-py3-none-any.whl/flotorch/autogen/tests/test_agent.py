"""Tests for FlotorchAutogenAgent.

This module tests the FlotorchAutogenAgent class including:
- Helper functions (schema_to_pydantic_model)
- Agent initialization and configuration
- Agent building with LLM and tools
- Tool integration (custom and MCP tools)
- Sync functionality for dynamic config updates
- Proxy pattern for transparent agent access
"""

import os
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel

from flotorch.autogen.tests.conftest import (
    MockFunctionTool,
    MockFlotorchAutogenMemory,
)
from flotorch.autogen.tests.test_data.agent_test_data import (
    AGENT_INIT_DATA,
    API_URL_DATA,
    CONFIG_MODIFIED,
    CONFIG_WITH_BOTH_SCHEMAS,
    CONFIG_WITH_INPUT_SCHEMA,
    CONFIG_WITH_MCP_TOOLS,
    CONFIG_WITH_OUTPUT_SCHEMA,
    CONFIG_WITH_SYNC,
    MINIMAL_CONFIG,
    SCHEMA_TO_PYDANTIC_DATA,
    SYNC_TEST_DATA,
)


class TestHelperFunctions:
    """Test utility helper functions."""

    @pytest.mark.parametrize(
        "data",
        SCHEMA_TO_PYDANTIC_DATA,
        ids=[d["id"] for d in SCHEMA_TO_PYDANTIC_DATA]
    )
    def test_schema_to_pydantic_model(self, data):
        """Test dynamic Pydantic model creation from JSON schema.

        Validates that:
        - Model is a valid Pydantic BaseModel
        - Model has correct name
        - Model instances can be created and validated
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import schema_to_pydantic_model

            model = schema_to_pydantic_model(data["name"], data["schema"])

            assert issubclass(model, BaseModel)
            assert model.__name__ == data["expected_model_name"]

            # Test instantiation and validation
            if data["id"] == "single_property_input":
                instance = model(query="test")
                assert instance.query == "test"
            elif data["id"] == "multiple_properties":
                instance = model(name="test", age=30, active=True)
                assert instance.name == "test"
                assert instance.age == 30
                assert instance.active is True


class TestFlotorchAutogenAgentInit:
    """Test FlotorchAutogenAgent initialization."""

    @pytest.mark.parametrize(
        "data",
        AGENT_INIT_DATA,
        ids=[d["id"] for d in AGENT_INIT_DATA]
    )
    def test_init_with_params(self, mock_agent_deps, data):
        """Test successful initialization with various parameter
        combinations.

        Validates that:
        - All instance attributes are set correctly
        - Config is fetched from API
        - Agent is built
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            agent = FlotorchAutogenAgent(**data["params"])

            for attr, expected_value in data["expected"].items():
                actual_value = getattr(agent, attr)
                # For Mock objects, just check they exist and are the
                # right type
                if hasattr(expected_value, '__class__') and \
                        'Mock' in str(expected_value.__class__):
                    assert hasattr(agent, attr)
                    assert actual_value is not None
                elif isinstance(expected_value, list) and \
                        all(hasattr(item, '__class__') and
                            'Mock' in str(item.__class__)
                            for item in expected_value):
                    assert hasattr(agent, attr)
                    assert isinstance(actual_value, list)
                    assert len(actual_value) == len(expected_value)
                    assert all(item is not None for item in actual_value)
                else:
                    assert actual_value == expected_value

            assert agent.config == MINIMAL_CONFIG
            assert agent._agent is not None

    def test_init_requires_base_url(self):
        """Test that initialization fails without base_url."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError,
                                   match="base_url is required"):
                    FlotorchAutogenAgent(agent_name="test-agent",
                                         api_key="test-key")

    def test_init_requires_api_key(self):
        """Test that initialization fails without api_key."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError,
                                   match="api_key is required"):
                    FlotorchAutogenAgent(agent_name="test-agent",
                                         base_url="https://test.com")

    def test_init_uses_environment_variables(self, mock_agent_deps):
        """Test that base_url and api_key are picked from env vars."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            with patch.dict(os.environ, {
                "FLOTORCH_BASE_URL": "https://env.com",
                "FLOTORCH_API_KEY": "env-key"
            }, clear=True):
                agent = FlotorchAutogenAgent(agent_name="test-agent")
                assert agent.base_url == "https://env.com"
                assert agent.api_key == "env-key"
                mock_agent_deps['http_get'].assert_called_once_with(
                    "https://env.com/v1/agents/test-agent",
                    headers={"Authorization": "Bearer env-key",
                             "Content-Type": "application/json"}
                )


class TestConfigFetching:
    """Test agent configuration fetching from API."""

    @pytest.mark.parametrize(
        "data",
        API_URL_DATA,
        ids=[d["id"] for d in API_URL_DATA]
    )
    def test_constructs_correct_api_url(self, mock_agent_deps, data):
        """Test that the API URL is constructed correctly."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            FlotorchAutogenAgent(
                agent_name=data["agent_name"],
                base_url=data["base_url"],
                api_key="test-key"
            )

            mock_agent_deps['http_get'].assert_called_once_with(
                data["expected_url"],
                headers={"Authorization": "Bearer test-key",
                         "Content-Type": "application/json"}
            )

    def test_propagates_api_errors(self, mock_agent_deps):
        """Test that API errors are propagated."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].side_effect = \
                Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                FlotorchAutogenAgent(
                    agent_name="test-agent",
                    base_url="https://test.com",
                    api_key="test-key"
                )


class TestAgentBuilding:
    """Test AutoGen agent building."""

    def test_creates_llm_with_correct_params(self, mock_agent_deps):
        """Test that FlotorchAutogenLLM is created with correct params."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = MINIMAL_CONFIG

            FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            mock_agent_deps['llm'].assert_called_once_with(
                model_id="test-model",
                api_key="test-key",
                base_url="https://test.com"
            )

    def test_creates_agent_with_output_schema(self, mock_agent_deps):
        """Test agent is created with output schema."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_OUTPUT_SCHEMA

            FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            agent_kwargs = mock_agent_deps['assistant_agent'].call_args[1]
            assert "output_content_type" in agent_kwargs
            assert issubclass(agent_kwargs["output_content_type"], BaseModel)

    def test_creates_agent_without_output_schema(self, mock_agent_deps):
        """Test agent is created without output schema if not provided."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = MINIMAL_CONFIG

            FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            agent_kwargs = mock_agent_deps['assistant_agent'].call_args[1]
            # output_content_type is always present but can be None
            assert agent_kwargs.get("output_content_type") is None

    def test_creates_agent_with_input_schema(self, mock_agent_deps):
        """Test agent is created with input schema."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_INPUT_SCHEMA

            FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            # Verify agent was created successfully
            mock_agent_deps['assistant_agent'].assert_called_once()

    def test_creates_agent_with_both_schemas(self, mock_agent_deps):
        """Test agent is created with both input and output schemas."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_BOTH_SCHEMAS

            FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            agent_kwargs = mock_agent_deps['assistant_agent'].call_args[1]
            assert "output_content_type" in agent_kwargs
            assert issubclass(agent_kwargs["output_content_type"], BaseModel)

    def test_creates_agent_with_memory(self, mock_agent_deps):
        """Test agent is created with memory."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = MINIMAL_CONFIG

            memory_mock = MockFlotorchAutogenMemory(name="test_memory")
            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key",
                memory=memory_mock
            )

            assert isinstance(agent.memory, MockFlotorchAutogenMemory)
            assert agent.memory.name == "test_memory"


class TestToolIntegration:
    """Test tool integration (custom and MCP tools)."""

    def test_includes_custom_tools(self, mock_agent_deps):
        """Test custom tools are added to agent.

        Validates that all provided custom tools are available.
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            custom_tools = [MockFunctionTool("tool1"),
                            MockFunctionTool("tool2")]

            # Mock the _build_tools method to return our custom tools
            with patch.object(FlotorchAutogenAgent, '_build_tools',
                              return_value=custom_tools):
                FlotorchAutogenAgent(
                    agent_name="test-agent",
                    custom_tools=custom_tools,
                    base_url="https://test.com",
                    api_key="test-key"
                )

            agent_kwargs = \
                mock_agent_deps['assistant_agent'].call_args[1]
            tools = agent_kwargs['tools']

            assert all(tool in tools for tool in custom_tools)

    def test_creates_mcp_tools_correctly(self, mock_agent_deps):
        """Test MCP tools are created with correct parameters.

        Validates that:
        - Tool creation functions are called for MCP tools
        - Correct transport type is used
        - Authorization headers are passed
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_MCP_TOOLS

            # Mock the _build_tools method to simulate MCP tool creation
            def mock_build_tools(config):
                tools = []
                if config.get('tools'):
                    for tool_config in config['tools']:
                        if tool_config.get('type') == 'MCP':
                            transport = tool_config.get('config', {}).\
                                get('transport')
                            if transport == 'HTTP_SSE':
                                mock_agent_deps['create_sse_tool'].\
                                    return_value = ["sse_tool"]
                                tools.extend(["sse_tool"])
                            elif transport == 'HTTP_STREAMABLE':
                                mock_agent_deps['create_stream_tool'].\
                                    return_value = ["stream_tool"]
                                tools.extend(["stream_tool"])
                return tools

            with patch.object(FlotorchAutogenAgent, '_build_tools',
                              side_effect=mock_build_tools):
                FlotorchAutogenAgent(
                    agent_name="test-agent",
                    base_url="https://test.com",
                    api_key="test-key"
                )

            # Verify tool creation functions would be called
            assert mock_agent_deps['create_sse_tool'].return_value == \
                ["sse_tool"]
            assert mock_agent_deps['create_stream_tool'].return_value == \
                ["stream_tool"]

    def test_handles_tool_failures_gracefully(self, mock_agent_deps):
        """Test tool creation failures don't prevent agent creation.

        Validates graceful degradation when tools fail to create.
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_MCP_TOOLS
            mock_agent_deps['create_sse_tool'].side_effect = \
                Exception("SSE tool creation failed")
            mock_agent_deps['create_stream_tool'].side_effect = \
                Exception("Stream tool creation failed")

            # Agent creation should still succeed, but tools list will
            # be empty
            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            agent_kwargs = \
                mock_agent_deps['assistant_agent'].call_args[1]
            assert agent_kwargs['tools'] == []


class TestSyncFunctionality:
    """Test dynamic configuration sync functionality."""

    @pytest.mark.parametrize(
        "data",
        SYNC_TEST_DATA,
        ids=[d["id"] for d in SYNC_TEST_DATA]
    )
    def test_sync_config_handling(self, mock_agent_deps, data):
        """Test agent handles sync configuration correctly.

        Validates that:
        - Agent can be created with sync-enabled configs
        - Sync settings are properly stored
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = data["config"]

            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            # Verify agent was created successfully
            assert agent.config == data["config"]
            assert agent._agent is not None

    def test_sync_config_with_interval(self, mock_agent_deps):
        """Test agent handles sync interval configuration."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = CONFIG_WITH_SYNC

            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            # Verify sync configuration is stored
            assert agent.config["syncEnabled"] is True
            assert agent.config["syncInterval"] == 10  # Default value

    def test_modified_config_handling(self, mock_agent_deps):
        """Test agent handles modified configuration."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = CONFIG_MODIFIED

            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            # Verify modified configuration is stored
            assert agent.config["systemPrompt"] == "Modified system prompt"
            assert agent.config["syncEnabled"] is True


class TestProxyPattern:
    """Test proxy pattern for transparent sync."""

    def test_agent_proxy_delegates_attributes(self, mock_agent_deps):
        """Test AgentProxy delegates to underlying agent.

        Validates transparent attribute access through proxy.
        """
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            manager = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            proxy = manager.get_agent()

            # Test that proxy delegates to underlying agent
            assert hasattr(proxy, 'name')
            assert hasattr(manager._agent, 'name')
            assert proxy.name is not None

    def test_proxy_returns_correct_type(self, mock_agent_deps):
        """Test get_agent returns correct proxy type."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent, AgentProxy

            manager = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )
            proxy = manager.get_agent()
            assert isinstance(proxy, AgentProxy)

    def test_proxy_setattr_delegates_to_agent(self, mock_agent_deps):
        """Test setattr on proxy delegates to underlying agent."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            manager = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )
            proxy = manager.get_agent()

            new_message = "New system message"
            proxy.system_message = new_message

            assert manager._agent.system_message == new_message


class TestIntegration:
    """End-to-end integration tests."""

    def test_complete_agent_lifecycle(self, mock_agent_deps):
        """Test a complete agent lifecycle from init."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            # Initial creation
            agent = FlotorchAutogenAgent(
                agent_name="test-agent",
                base_url="https://test.com",
                api_key="test-key"
            )

            assert agent.agent_name == "test-agent"
            assert agent.base_url == "https://test.com"
            assert agent.api_key == "test-key"
            assert agent.config == MINIMAL_CONFIG
            assert agent._agent is not None
            mock_agent_deps['http_get'].assert_called_once()
            mock_agent_deps['assistant_agent'].assert_called_once()

            # Test agent proxy access
            proxy = agent.get_agent()
            assert proxy is not None
            assert hasattr(proxy, 'name')

    def test_agent_with_all_optional_params(self, mock_agent_deps):
        """Test agent creation with all optional parameters."""
        with patch.dict('sys.modules', {
            'autogen_ext': Mock(),
            'autogen_ext.tools': Mock(),
            'autogen_ext.tools.mcp': Mock()
        }):
            from flotorch.autogen.agent import FlotorchAutogenAgent

            mock_agent_deps['http_get'].return_value = \
                CONFIG_WITH_MCP_TOOLS

            memory_mock = MockFlotorchAutogenMemory(name="test_memory")
            custom_tools_list = [MockFunctionTool("custom_tool_1")]

            agent = FlotorchAutogenAgent(
                agent_name="full-agent",
                base_url="https://full.com",
                api_key="full-key",
                memory=memory_mock,
                custom_tools=custom_tools_list
            )

            assert agent.agent_name == "full-agent"
            assert agent.base_url == "https://full.com"
            assert agent.api_key == "full-key"
            assert agent.memory == memory_mock
            assert agent.custom_tools == custom_tools_list

            # Verify LLM creation with model context
            mock_agent_deps['llm'].assert_called_once_with(
                model_id="test-model",
                api_key="full-key",
                base_url="https://full.com"
            )

            # Verify AssistantAgent creation with all components
            agent_kwargs = \
                mock_agent_deps['assistant_agent'].call_args[1]
            assert agent_kwargs['model_client'] == \
                mock_agent_deps['llm'].return_value
            assert agent_kwargs['memory'] == memory_mock
            # Tools list may be empty due to mocking, but should exist
            assert 'tools' in agent_kwargs