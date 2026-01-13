import asyncio
import os
import time
import uuid
import weakref
from collections.abc import Sequence
from typing import Any, Dict, List, Optional


def _run_async_safe(coro):
    """Safely run async code, handling both new and existing event loops."""
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)

# Global registry to keep track of ToolsProxy instances and their managers
_TOOLS_PROXY_REGISTRY = {}

from langchain.agents import Tool, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import Field, create_model

from langchain.output_parsers import PydanticOutputParser

from langchain_mcp_adapters.client import MultiServerMCPClient

from flotorch.langchain.llm import FlotorchLangChainLLM
from flotorch.sdk.utils.http_utils import http_get
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error, ObjectCreation

logger = get_logger()
from flotorch.sdk.utils.validation_utils import validate_data_against_schema
from dotenv import load_dotenv
load_dotenv()

def sanitize_agent_name(name: str) -> str:
    """
    Sanitize agent name to be a valid identifier.
    
    Replaces invalid characters with underscores and ensures it starts with a 
    letter or underscore.
    """
    import re
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = f"agent_{sanitized}"
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "agent"
    
    return sanitized


def schema_to_pydantic_model(name: str, schema: Dict[str, Any]):
    """
    Create a minimal Pydantic model from a JSON schema dict.

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


class FlotorchLangChainAgent:
    """
    Flotorch LangChain Agent manager that builds and returns only a LangChain agent
    using create_openai_functions_agent. No AgentExecutor or external memory/session.
    """

    def __init__(
        self,
        agent_name: str,
        enable_memory: bool = False,
        custom_tools: Optional[List[Tool]] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.agent_name = agent_name
        self.enable_memory = enable_memory
        self.custom_tools = custom_tools or []
        self.base_url = base_url or os.environ.get("FLOTORCH_BASE_URL")
        self.api_key = api_key or os.environ.get("FLOTORCH_API_KEY")

        # Holds the currently active tool list used to build the agent
        self._tools: List[Tool] = []

        self.config = self._fetch_agent_config(agent_name)
        self._agent = _run_async_safe(self._build_agent_from_config(self.config))
        self._last_reload = time.time()

        # Log object creation
        logger.info(
            ObjectCreation(
                class_name="FlotorchLangChainAgent",
                extras={
                    'agent_name': agent_name,
                    'base_url': self.base_url,
                    'has_custom_tools': bool(custom_tools),
                    'sync_enabled': self.config.get("syncEnabled", False)
                }
            )
        )

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("base_url is required")
        if not self.api_key:
            raise ValueError("api_key is required")
        url = f"{self.base_url.rstrip('/')}/v1/agents/{agent_name}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        return http_get(url, headers=headers)

    # ---------------------- MCP TOOL BUILDER -------------------
    def _make_tool_sync(self, tool):
        """Make async MCP tool compatible with LangGraph's sync execution."""
        from langchain_core.tools import StructuredTool
        import asyncio
        
        def sync_wrapper(**kwargs):
            try:
                result = _run_async_safe(tool.ainvoke(kwargs))
                return result
            except Exception as e:
                raise
        
        return StructuredTool(
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
            func=sync_wrapper
        )
        
    async def _build_mcp_tools(self, tool_cfg) -> List[BaseTool]:
        """Build MCP tools using MultiServerMCPClient."""
        try:
            cfg = tool_cfg.get("config", {})
            tool_name = tool_cfg.get("name", "mcp_tool")
            headers = dict(cfg.get("headers", {}))
            transport = cfg.get("transport", "streamable_http")
            proxy_url = f"{self.base_url}/v1/mcps/{tool_cfg['name']}/proxy"  

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
            
            tools = await client.get_tools(server_name=tool_name)
            
            # filtered_tools = self._filter_mcp_tools(tools, tool_cfg)
            
            wrapped_tools = []
            for tool in tools:
                wrapped_tool = self._make_tool_sync(tool)
                wrapped_tools.append(wrapped_tool)
            
            return wrapped_tools

        except Exception as e:
            logger.error(Error(operation="FlotorchLangChainAgent._build_mcp_tools", error=e))
            return []


    def _filter_mcp_tools(self, all_tools: List[BaseTool], tool_cfg) -> List[BaseTool]:
        """Filter MCP tools based on configuration."""
        filtered_tools = []
        tool_name = sanitize_agent_name(tool_cfg.get("name"))

        if tool_name:
            # Match tool name to config (avoid collisions)
            for tool in all_tools:
                if getattr(tool, 'name', None) == tool_name:
                    filtered_tools.append(tool)
        else:
            # If no specific name, use all tools
            filtered_tools = all_tools

        return filtered_tools


    async def _build_tools(self, config) -> List[BaseTool]:
        tools = []
        # Custom tools always included
        if self.custom_tools:
            tools.extend(self.custom_tools)

        # Build MCP tools using langchain-mcp-adapters
        # Each tool manages its own session lifecycle
        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                
                try:
                    mcp_tools = await self._build_mcp_tools(tool_cfg)
                    tools.extend(mcp_tools)
                except Exception as e:
                    logger.error(Error(operation="FlotorchLangChainAgent._build_tools", error=e))
                    logger.warning(f"MCP tool '{tool_cfg.get('name', 'unknown')}' skipped due to error")

        return tools



    async def _build_agent_from_config(self, config):
        # Build prompt from config goal and systemPrompt, include input and agent_scratchpad
        messages: List[Any] = []
        goal_text = config.get("goal")
        if goal_text:
            messages.append(("system", goal_text))
        system_prompt = config.get("systemPrompt")
        if system_prompt:
            messages.append(("system", system_prompt))

        # Optional structured output via config["outputSchema"]
        output_schema = config.get("outputSchema")
        parser: Optional[PydanticOutputParser] = None
        if isinstance(output_schema, dict) and output_schema.get("properties"):
            try:
                model = schema_to_pydantic_model("OutputSchema", output_schema)
                parser = PydanticOutputParser(pydantic_object=model)
                messages.append(("system", "{format_instructions}"))
            except Exception:
                parser = None

        # Add chat history placeholder for proper message flow
        messages.append(("placeholder", "{chat_history}"))
        
        # Human input and agent scratchpad
        messages.append(("human", "{input}"))
        messages.append(("assistant","Sessions-Memory Data: {history}"))
        if self.enable_memory:
            messages.append(("assistant","Longterm-Memory Data: {longterm_history}"))
        messages.append(("placeholder", "{agent_scratchpad}"))

        prompt = ChatPromptTemplate.from_messages(messages)
        if parser is not None:
            prompt = prompt.partial(format_instructions=parser.get_format_instructions())

        llm_params = config.get("llm", {})
        model_name = llm_params.get("callableName")
        llm = FlotorchLangChainLLM(
            model_id=model_name,
            api_key=self.api_key,
            base_url=self.base_url,
        )

        tools = await self._build_tools(config)
        if not tools:
            # Ensure at least one function for create_openai_functions_agent
            try:
                def _noop_tool(input: str = "") -> str:
                    return ""

                tools = tools + [
                    Tool(
                        name="noop",
                        func=_noop_tool,
                        description="No-op tool when no tools are configured.",
                    )
                ]
            except Exception:
                pass

        # Store the tools used for this agent so callers can retrieve them
        self._tools = tools

        agent = create_openai_functions_agent(llm, tools, prompt)
        
        return agent

    def get_agent(self):
        return AgentProxy(self)

    def get_tools(self) -> List[Tool]:
        """Return the currently active tool list used to build the agent."""
        return ToolsProxy(self)

    def _get_synced_agent(self):
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._agent

        sync_interval = self.config.get('syncInterval', 60)
        now = time.time()
        elapsed_time = now - self._last_reload
        if elapsed_time > sync_interval:
            logger.info(f"Sync started for agent '{self.agent_name}' - reload interval ({sync_interval}s) passed")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    tools = _run_async_safe(self._build_tools(self.config))
                    self._tools = tools
                    self._agent = _run_async_safe(self._build_agent_from_config(self.config))
                    logger.info(f"Sync completed - agent '{self.agent_name}' successfully reloaded with new configuration")
                else:
                    logger.info(f"Sync completed - agent '{self.agent_name}' configuration unchanged")
            except Exception as e:
                logger.warning(f"Failed to reload agent config for '{self.agent_name}'. Using previous agent. Reason: {str(e)}")
            finally:
                self._last_reload = now
        return self._agent

    def _get_synced_tools(self):
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._agent

        sync_interval = self.config.get('syncInterval', 60)
        now = time.time()
        elapsed_time = now - self._last_reload
        if elapsed_time > sync_interval:
            logger.info(f"Sync started for agent '{self.agent_name}' - reload interval ({sync_interval}s) passed")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    tools = _run_async_safe(self._build_tools(self.config))
                    self._tools = tools
                    self._agent = _run_async_safe(self._build_agent_from_config(self.config))
                    logger.info(f"Sync completed - agent '{self.agent_name}' successfully reloaded with new configuration")
                else:
                    logger.info(f"Sync completed - agent '{self.agent_name}' configuration unchanged")
            except Exception as e:
                logger.warning(f"Failed to reload agent config for '{self.agent_name}'. Using previous agent. Reason: {str(e)}")
            finally:
                self._last_reload = now
        return self._tools

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


class AgentProxy(Runnable):
    def __init__(self, manager: 'FlotorchLangChainAgent'):
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
        return getattr(self._manager._get_synced_agent(), item)

    def __setattr__(self, key, value):
        if key == "_manager":
            return object.__setattr__(self, key, value)
        return setattr(self._manager._get_synced_agent(), key, value)

    def invoke(self, input: Any, config: Any | None = None, **kwargs: Any):
        if self._manager.config.get("inputSchema"):
            self._validate_input(input)
        return self._manager._get_synced_agent().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input: Any, config: Any | None = None, **kwargs: Any):
        if self._manager.config.get("inputSchema"):
            self._validate_input(input)
        return await self._manager._get_synced_agent().ainvoke(input, config=config, **kwargs)

    def _validate_input(self, input_data: Any) -> None:
        """Validate input format and schema."""
        input_schema = self._manager.config.get("inputSchema")
        # Check if input is dict with "input" key (LangChain standard format)
        if not isinstance(input_data, dict) or "input" not in input_data:
            error_msg = f"Input validation failed: LangChain expects dict with 'input' key. Received: {type(input_data)}"
            logger.warning(f"Input validation failed for agent '{self._manager.agent_name}': {error_msg}")
            raise ValueError(error_msg)

        user_data = input_data.get("input")
        is_valid = validate_data_against_schema(user_data, input_schema)

        if not is_valid:
            error_msg = f"Input schema validation failed: data does not match the required schema. schema configured: {input_schema}"
            logger.warning(f"Input validation failed for agent '{self._manager.agent_name}': {error_msg}")
            raise ValueError(error_msg)

    def get_tools(self) -> List[Tool]:
        return ToolsProxy(self._manager)


class ToolsProxy(list):
    """
    A dynamic list that automatically syncs with the latest tools from a FlotorchLangChainAgent.
    
    This proxy ensures that AgentExecutor always has access to the most up-to-date tools,
    even when the agent configuration is dynamically updated.
    """

    def __init__(self, manager):
        """Initialize the ToolsProxy with a manager or list of tools."""
        super().__init__()
        
        if isinstance(manager, list):
            # Manager is already a list (corrupted case from LangChain)
            self.extend(manager)
            self._is_corrupted = True
            self._manager_ref = None
            self._try_recover_manager()
        elif hasattr(manager, '_get_synced_tools'):
            # Valid FlotorchLangChainAgent manager
            self._is_corrupted = False
            self._manager_ref = weakref.ref(manager) if manager else None
            # Store in global registry for recovery
            self._proxy_id = str(uuid.uuid4())
            _TOOLS_PROXY_REGISTRY[self._proxy_id] = manager
            self._refresh_tools()
        else:
            # Fallback for unknown manager types
            self._is_corrupted = True
            self._manager_ref = None

    def _try_recover_manager(self):
        """Try to recover manager from global registry."""
        if '_TOOLS_PROXY_REGISTRY' in globals() and _TOOLS_PROXY_REGISTRY:
            for proxy_id, manager in _TOOLS_PROXY_REGISTRY.items():
                if manager and hasattr(manager, '_get_synced_tools'):
                    self._manager_ref = weakref.ref(manager)
                    self._is_corrupted = False
                    self._proxy_id = proxy_id
                    return True
        return False

    def _refresh_tools(self):
        """Get fresh tools from the manager."""
        if self._is_corrupted or not self._manager_ref:
            # Try to recover manager from global registry if available
            try:
                proxy_id = object.__getattribute__(self, '_proxy_id')
                if '_TOOLS_PROXY_REGISTRY' in globals():
                    manager = _TOOLS_PROXY_REGISTRY.get(proxy_id)
                    if manager and hasattr(manager, '_get_synced_tools'):
                        self._manager_ref = weakref.ref(manager)
                        self._is_corrupted = False
                    else:
                        return
                else:
                    return
            except AttributeError:
                return
            
        manager = self._manager_ref()
        if manager and hasattr(manager, '_get_synced_tools'):
            synced_tools = manager._get_synced_tools()
            self.clear()
            self.extend(synced_tools)

    def __getitem__(self, index):
        """Get a tool by index, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().__getitem__(index)

    def __len__(self):
        """Get the number of tools, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().__len__()

    def __iter__(self):
        """Iterate over tools, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().__iter__()

    def __getattr__(self, name):
        """Refresh tools before any attribute access."""
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        self._refresh_tools()
        return super().__getattribute__(name)

    def __contains__(self, item):
        """Check if tool exists, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().__contains__(item)

    def count(self, value):
        """Count occurrences of a tool, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().count(value)

    def index(self, value, start=0, stop=None):
        """Find index of a tool, ensuring tools are up-to-date."""
        self._refresh_tools()
        return super().index(value, start, stop)