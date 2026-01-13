import os
import asyncio
import time
import json
from typing import Any, Dict, List, Optional, cast

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from flotorch.langchain.llm import FlotorchLangChainLLM
from flotorch.sdk.utils.http_utils import http_get
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error, ObjectCreation

logger = get_logger()
from pydantic import Field, create_model

from flotorch.sdk.utils.validation_utils import validate_data_against_schema


def _run_async_safe(coro):
    """Safely run async code, handling both new and existing event loops."""
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, create a task in a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)


def sanitize_agent_name(name: str) -> str:
    """Sanitize agent name to be a valid identifier."""

    import re
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)

    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = f"agent_{sanitized}"
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')

    if not sanitized:
        sanitized = "agent"

    return sanitized


def schema_to_pydantic_model(name: str, schema: Dict[str, Any]):
    """Create a minimal Pydantic model from a JSON schema dict.

    Only supports primitive field types used in simple structured outputs.
    """
    properties = schema.get("properties", {}) or {}
    fields: Dict[str, Any] = {}
    for prop, prop_schema in properties.items():
        field_type = str
        t = (prop_schema or {}).get("type")
        if t == "integer":
            field_type = int
        elif t == "number":
            field_type = float
        elif t == "boolean":
            field_type = bool
        description = (prop_schema or {}).get("description", "")
        fields[prop] = (field_type, Field(description=description))
    return create_model(name, **fields)


class FlotorchLangGraphAgent:
    """
    Flotorch LangGraph Agent manager following LangGraph standards.
    """

    def __init__(
            self,
            agent_name: str,
            custom_tools: Optional[List[BaseTool]] = None,
            base_url: Optional[str] = None,
            api_key: Optional[str] = None,
            store: Optional[Any] = None,
            checkpointer: Optional[Any] = None
    ):
        """
        Initialize the LangGraph agent with configuration loading.

        Args:
            agent_name: Name of the agent to load configuration for
            custom_tools: List of custom tools to add to the agent
            base_url: Flotorch API base URL
            api_key: Flotorch API key
            store: Pre-created memory store object (optional)
            checkpointer: Pre-created session checkpointer object (optional)

        Usage:
            client = FlotorchLangGraphAgent(
                agent_name ="langgraph",
                base_url = os.getenv("FLOTORCH_BASE_URL"),
                api_key = os.getenv("FLOTORCH_API_KEY"),
                custom_tools = tools,
                checkpointer=session,
                store=memory
            )
            agent = client.get_agent()
        """
        self.agent_name = agent_name
        self.custom_tools = custom_tools or []
        self.base_url = base_url or os.environ.get("FLOTORCH_BASE_URL")
        self.api_key = api_key or os.environ.get("FLOTORCH_API_KEY")

        if not self.base_url or not self.api_key:
            raise ValueError("base_url and api_key are required")

        self.config = self._fetch_agent_config(agent_name)
        self._llm = self._build_llm_from_config(self.config)
        self._store = store
        self._checkpointer = checkpointer
        self._last_reload = time.time()
        self._agent_graph = _run_async_safe(self._build_agent_graph_from_config(self.config))
        
        # Log object creation
        logger.info(
            ObjectCreation(
                class_name="FlotorchLangGraphAgent",
                extras={'agent_name': agent_name, 'base_url': self.base_url}
            )
        )

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Fetch agent configuration from Flotorch API."""
        if not self.base_url:
            raise ValueError("base_url is required")
        if not self.api_key:
            raise ValueError("api_key is required")
        url = f"{self.base_url.rstrip('/')}/v1/agents/{agent_name}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        return http_get(url, headers=headers)

    def _build_llm_from_config(self, config: Dict[str, Any]) -> FlotorchLangChainLLM:
        """Build LLM instance from agent configuration."""
        llm_config = config.get("llm", {})
        model_id = llm_config.get("callableName", "default-model")

        return FlotorchLangChainLLM(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def _build_mcp_tools(self, tool_cfg) -> List[BaseTool]:
        """Build MCP tools using MultiServerMCPClient."""
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            cfg = tool_cfg.get("config", {})
            tool_name = tool_cfg.get("name", "mcp_tool")
            proxy_url = f"{self.base_url}/v1/mcps/{tool_cfg['name']}/proxy"
            headers = dict(cfg.get("headers", {}))
            transport = cfg.get("transport", "streamable_http")

            if not proxy_url:
                return []

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            if transport == "HTTP_STREAMABLE":
                mcp_transport = "streamable_http"
            elif transport == "HTTP_SSE":
                mcp_transport = "sse"
            else:
                return []

            mcp_server_config = {
                tool_name: {
                    "url": proxy_url,
                    "transport": mcp_transport,
                }
            }

            if headers:
                mcp_server_config[tool_name]["headers"] = headers

            client = MultiServerMCPClient(mcp_server_config)

            if not hasattr(self, '_mcp_clients'):
                self._mcp_clients = {}
            self._mcp_clients[tool_name] = client

            try:
                tools = await client.get_tools(server_name=tool_name)
            except Exception as mcp_error:
                logger.warning(f"MCP connection failed for tool '{tool_name}': {str(mcp_error)}")
                return []

            # filtered_tools = self._filter_mcp_tools(tools, tool_cfg)

            wrapped_tools = []
            for tool in tools:
                wrapped_tool = self._make_tool_sync(tool)
                wrapped_tools.append(wrapped_tool)

            return wrapped_tools

        except Exception as e:
            logger.error(Error(operation="FlotorchLangGraphAgent._build_mcp_tools", error=e))
            return []

    def _filter_mcp_tools(self, all_tools: List[BaseTool], tool_cfg) -> List[BaseTool]:
        """Filter MCP tools based on configuration."""
        filtered_tools = []
        tool_name = sanitize_agent_name(tool_cfg.get("name"))

        if tool_name:
            for tool in all_tools:
                if getattr(tool, 'name', None) == tool_name:
                    filtered_tools.append(tool)
        else:
            filtered_tools = all_tools

        return filtered_tools

    def _make_tool_sync(self, tool):
        """Make async MCP tool compatible with LangGraph's sync execution."""
        from langchain_core.tools import StructuredTool
        import asyncio

        def sync_wrapper(**kwargs):
            try:
                result = _run_async_safe(tool.ainvoke(kwargs))
                # Tool result handled silently at SDK level
                return result
            except Exception as e:
                logger.error(Error(operation=f"FlotorchLangGraphAgent._sync_tool_call.{tool.name}", error=e))
                raise

        return StructuredTool(
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
            func=sync_wrapper
        )

    async def _build_tools(self, config) -> List[BaseTool]:
        """Build all tools including custom and MCP tools."""
        tools = []

        if self.custom_tools:
            tools.extend(self.custom_tools)

        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                try:
                    mcp_tools = await self._build_mcp_tools(tool_cfg)
                    tools.extend(mcp_tools)
                except Exception as e:
                    logger.warning(f"Failed to build MCP tool '{tool_cfg.get('name', 'unknown')}': {str(e)}")

        return tools

    async def _build_agent_graph_from_config(self, config: Dict[str, Any]) -> Any:
        """Build LangGraph agent from configuration with auto-validation."""
        system_prompt = config.get("systemPrompt", "You are a helpful assistant.")
        goal = config.get("goal", "")
        if goal:
            system_prompt += f"\n\nYour goal: {goal}"

        tools = await self._build_tools(config)

        agent_kwargs = {
            "model": self._llm,
            "tools": tools,
            "prompt": system_prompt,
        }

        output_schema = config.get("outputSchema")
        if isinstance(output_schema, dict) and output_schema.get("properties"):
            try:
                agent_kwargs['response_format'] = output_schema
            except Exception as e:
                logger.warning(f"Failed to create structured output: {str(e)}")

        if self._store:
            agent_kwargs['store'] = self._store
        if self._checkpointer:
            agent_kwargs['checkpointer'] = self._checkpointer

        agent = create_react_agent(**agent_kwargs)

        # Wrap agent with input validation if schema exists
        input_schema = config.get("inputSchema")
        if input_schema:
            agent = self._wrap_agent_with_validation(agent, input_schema)

        return agent

    def _wrap_agent_with_validation(
            self, agent: Any, input_schema: Dict[str, Any]
    ) -> Any:
        """
        Wrap agent's invoke method with input validation and transformation.

        Args:
            agent: The LangGraph agent instance
            input_schema: JSON schema for input validation

        Returns:
            Agent with wrapped invoke method
        """
        original_invoke = agent.invoke

        def validated_invoke(input_data: Any, *args, **kwargs) -> Any:
            """Validate and transform input data before invoking agent."""
            user_data = self._parse_user_input(input_data)
            is_valid = validate_data_against_schema(user_data, input_schema)
            if not is_valid:
                error_msg = f"Input schema validation failed: data does not match the required schema. schema configured: {input_schema}"
                logger.warning(f"Input validation failed for agent '{self.agent_name}': {error_msg}")
                raise ValueError(error_msg)

            # Transform to LangGraph format
            langgraph_input = self._format_for_langgraph(user_data)

            return original_invoke(langgraph_input, *args, **kwargs)

        agent.invoke = validated_invoke
        return agent

    def _parse_user_input(self, input_data: Any) -> Any:
        """
        Parse and extract actual user data from various input formats.

        Handles:
        - Direct dict: {"messages": ...}
        - String (JSON): '{"messages": ...}'

        Args:
            input_data: Raw input in any supported format

        Returns:
            Parsed user data as dict or string
        """
        if not isinstance(input_data, dict):
            raise ValueError(f"LangGraph agent expects dict input with 'messages' key, got {type(input_data)}")
        messages = input_data.get("messages")
        if not isinstance(messages, str):
            return json.dumps(messages)

        return messages

    def _format_for_langgraph(self, user_data: Any) -> Dict[str, Any]:
        """
        Format user data into proper LangGraph message format.

        Args:
            user_data: Validated user data (dict or string)

        Returns:
            Data formatted for LangGraph: {"messages": [("user", "content")]}
        """
        if isinstance(user_data, dict):
            content = json.dumps(user_data)
        elif isinstance(user_data, str):
            content = user_data
        else:
            content = str(user_data)

        return {"messages": [("user", content)]}

    def _get_synced_agent_graph(self) -> Any:
        """Get agent graph with configuration sync if enabled."""
        sync_enabled = self.config.get("syncEnabled", False)
        sync_interval = self.config.get("syncInterval", 60)
        now = time.time()

        elapsed_time = now - self._last_reload
        if sync_enabled and elapsed_time > sync_interval:
            logger.info(f"Sync started for agent '{self.agent_name}' - reload interval ({sync_interval}s) passed")

            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    self._llm = self._build_llm_from_config(self.config)
                    self._agent_graph = _run_async_safe(self._build_agent_graph_from_config(self.config))

                    logger.info(f"Sync completed - agent '{self.agent_name}' successfully reloaded with new configuration")
                else:
                    logger.info(f"Sync completed - agent '{self.agent_name}' configuration unchanged")

            except Exception as e:
                logger.warning(f"Failed to reload agent graph for '{self.agent_name}'. Using previous graph. Reason: {str(e)}")
            finally:
                self._last_reload = now

        return self._agent_graph

    def get_agent(self):
        """Get the agent graph proxy (following LangGraph standards)."""
        return cast(Any, AgentGraphProxy(self))

    def get_latest_config(self):
        """
        Get the latest config from the API.
        """
        sync_enabled = self.config.get('syncEnabled', False)
        if sync_enabled:
            sync_interval = self.config.get('syncInterval', 60)
            now = time.time()
            if now - self._last_reload > sync_interval:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    return new_config
        return self.config

    @property
    def goal(self):
        """
        Get the agent's goal configured on Flotorch API Gateway.

        Returns:
            str: The agent's goal as defined in the configuration.
        """
        current_config = self.get_latest_config()
        return current_config.get('goal', '')

    @goal.setter
    def goal(self, new_goal):
        """
        Setter for the goal property.

        Args:
            new_goal: The new goal value to set.

        Raises:
            AttributeError: Please use Flotorch APIGateway to update the goal.
        """
        raise AttributeError("Please use Flotorch APIGateway to update the goal.")

    @property
    def system_prompt(self):
        """
        Get the agent's system prompt configured on Flotorch API Gateway.

        Returns:
            str: The agent's system prompt as defined in the configuration.
        """
        current_config = self.get_latest_config()
        return current_config.get('systemPrompt', '')

    @system_prompt.setter
    def system_prompt(self, new_system_prompt):
        """Setter for the system prompt property.

        Args:
            new_system_prompt: The new system prompt value to set.

        Raises:
            AttributeError: Please use Flotorch APIGateway to update the system prompt.
        """
        raise AttributeError("Please use Flotorch APIGateway to update the system prompt.")


class AgentGraphProxy:
    """Proxy class for LangGraph agent operations (following LangGraph standards)."""

    def __init__(self, manager: FlotorchLangGraphAgent):
        self._manager = manager

    @property
    def goal(self):
        """
        Get the agent's goal configured on Flotorch API Gateway.

        Returns:
            str: The agent's goal as defined in the configuration.
        """
        return self._manager.get_latest_config().get('goal', '')

    @goal.setter
    def goal(self, new_goal):
        """
        Setter for the goal property.

        Args:
            new_goal: The new goal value to set.

        Raises:
            AttributeError: Please use Flotorch APIGateway to update the goal.
        """
        raise AttributeError(f"Please use Flotorch APIGateway to update the goal.")

    @property
    def system_prompt(self):
        """
        Get the agent's system prompt configured on Flotorch API Gateway.

        Returns:
            str: The agent's system prompt as defined in the configuration.
        """
        return self._manager.get_latest_config().get('systemPrompt', '')

    @system_prompt.setter
    def system_prompt(self, new_system_prompt):
        """
        Setter for the system prompt property.

        Args:
            new_system_prompt: The new system prompt value to set.

        Raises:
            AttributeError: Please use Flotorch APIGateway to update the system prompt.
        """
        raise AttributeError(f"Please use Flotorch APIGateway to update the system prompt.")

    def __getattr__(self, item):
        """Delegate attribute access to the underlying agent graph."""
        return getattr(self._manager._get_synced_agent_graph(), item)

    def __setattr__(self, key, value):
        """Delegate attribute setting to the underlying agent graph."""
        if key == "_manager":
            object.__setattr__(self, key, value)
        else:
            setattr(self._manager._get_synced_agent_graph(), key, value)

