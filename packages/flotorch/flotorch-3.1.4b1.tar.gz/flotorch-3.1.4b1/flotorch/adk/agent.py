import os
import sys
import json
import re
from typing import cast, Optional, Tuple, Union
from flotorch.adk.utils.warning_utils import SuppressOutput
from flotorch.adk.llm import FlotorchADKLLM
from google.adk.agents import LlmAgent
from google.adk.tools import preload_memory, load_memory
from typing import Any, Dict
from dotenv import load_dotenv
from pydantic import create_model, Field
import httpx
import inspect
import time
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, SseConnectionParams
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error, ObjectCreation
from flotorch.sdk.utils.http_utils import http_get
from flotorch.sdk.utils.validation_utils import validate_data_against_schema
#tracing
from flotorch.sdk.flotracer.config import FloTorchFramework
from flotorch.adk.instrumentation.callbacks import FloTorchADKCallbacks
from flotorch.sdk.flotracer.manager import FloTorchTracingManager
from flotorch.sdk.utils.common_utils import initialize_tracing_manager, fetch_traces_from_api

logger = get_logger()

load_dotenv()


def sanitize_name(name: str) -> str:
    """
    Sanitize agent name to be a valid identifier.
    Replaces invalid characters with underscores and ensures it starts with a letter or underscore.
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


def schema_to_pydantic_model(name: str, schema: dict):
    """
    Dynamically create a Pydantic model from a JSON schema dict.
    If only one property, use its name (capitalized) plus 'Input' or 'Output' as the model name.
    Otherwise, use the provided name.
    Now respects 'required' fields from the schema.
    """
    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))  # Get required fields

    if len(properties) == 1:
        prop_name = next(iter(properties))
        if name.lower().startswith("input"):
            model_name = f"{prop_name.capitalize()}Input"
        elif name.lower().startswith("output"):
            model_name = f"{prop_name.capitalize()}Output"
        else:
            model_name = f"{prop_name.capitalize()}Schema"
    else:
        model_name = name
    fields = {}
    for prop, prop_schema in properties.items():
        field_type = str  # Default to string
        if prop_schema.get("type") == "integer":
            field_type = int
        elif prop_schema.get("type") == "number":
            field_type = float
        elif prop_schema.get("type") == "boolean":
            field_type = bool
        elif prop_schema.get("type") == "object":
            field_type = dict
        description = prop_schema.get("description", "")
        # Check if field is required
        if prop in required_fields:
            fields[prop] = (field_type, Field(..., description=description))  # Required field
        else:
            fields[prop] = (Optional[field_type], Field(default=None, description=description))  # Optional field

    return create_model(model_name, **fields)


def remove_curly_braces(text: str) -> str:
    """Remove all curly braces {} from the given text using regex."""
    return re.sub(r'[{}]', '', text)

class FlotorchADKAgent:
    """
    Manager/config class for Flotorch agent. Builds LlmAgent from config on demand.
    Supports on-demand config reload based on interval in config['sync'].

    Args:
        agent_name: Name of the agent
        enable_memory: Enable memory functionality
        custom_tools: List of custom user-defined tools to add to the agent
        base_url: Optional base URL for the API. Falls back to FLOTORCH_BASE_URL env var
        api_key: Optional API key for authentication. Falls back to FLOTORCH_API_KEY env var

    Usage:
        flotroch = FlotorchADKClient("agent-one", enable_memory=True, custom_tools=[my_tool])
        agent = flotroch.get_agent()
    """

    def __init__(self, agent_name: str, enable_memory: bool = False, custom_tools: list = None, base_url: str = None,
                 api_key: str = None, tracer_config: Optional[Dict[str, Any]] = None,
                 tracing_manager: Optional[FloTorchTracingManager] = None):
        self.agent_name = agent_name
        self.enable_memory = enable_memory
        self.custom_tools = custom_tools or []

        # Store base_url and api_key, using environment variables as fallback
        self.base_url = base_url or os.environ.get("FLOTORCH_BASE_URL")
        self.api_key = api_key or os.environ.get("FLOTORCH_API_KEY")

        if tracing_manager is not None:
            self.tracing_manager = tracing_manager
        else:
            self.tracing_manager = initialize_tracing_manager(
                base_url=base_url,
                api_key=api_key,
                tracer_config=tracer_config or {},
                framework=FloTorchFramework.FLOTORCH_ADK
            )

        self.config = self._fetch_agent_config(agent_name)
        # Initialize ADK-specific tracing callbacks
        if self.tracing_manager:
            self.tracing_callbacks = FloTorchADKCallbacks(self.tracing_manager, self.agent_name)
            self.tracing_manager.set_mapping_callback(self.tracing_callbacks.set_agent_mapping)
        else:
            self.tracing_callbacks = None
        self._agent = self._build_agent_from_config(self.config)
        self._last_reload = time.time()

        # Log object creation
        logger.info(
            ObjectCreation(
                class_name="FlotorchADKAgent",
                extras={
                    'agent_name': self.agent_name,
                    'memory_enabled': self.enable_memory,
                    'base_url': self.base_url
                }
            )
        )
        logger.info(f"FlotorchADKAgent created: '{self.agent_name}' with memory={'enabled' if self.enable_memory else 'disabled'}")

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch agent config from API.
        """
        if not self.base_url:
            error_msg = "base_url is required to fetch agent configuration"
            logger.error(Error(operation="FlotorchADKAgent._fetch_agent_config", error=ValueError(error_msg)))
            raise ValueError(error_msg)

        if not self.api_key:
            error_msg = "api_key is required to fetch agent configuration"
            logger.error(Error(operation="FlotorchADKAgent._fetch_agent_config", error=ValueError(error_msg)))
            raise ValueError(error_msg)

        # Construct the API URL
        url = f"{self.base_url.rstrip('/')}/v1/agents/{agent_name}"

        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Fetch the agent configuration from the API
            response = http_get(url, headers=headers)
            return response
        except Exception as e:
            logger.error(Error(operation="FlotorchADKAgent._fetch_agent_config", error=e))
            raise e

    def _build_tools(self, config: Dict[str, Any]):
        tools = []

        # Add memory tools if memory is enabled
        if self.enable_memory:
            tools.append(preload_memory)  # Automatic memory loading (preprocessor)
            # tools.append(load_memory)     # Manual memory search (function tool)

        # Add MCP tools with improved error handling
        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                mcp_conf = tool_cfg["config"]
                proxy_url = f"{self.base_url}/v1/mcps/{tool_cfg['name']}/proxy"
                try:
                    # Build connection params with better defaults
                    headers = dict(mcp_conf.get("headers", {}))
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"

                    # Use custom silence context manager to suppress ALL output
                    with SuppressOutput():
                        if mcp_conf.get("transport") == "HTTP_STREAMABLE":
                            conn_params = StreamableHTTPConnectionParams(
                                url=proxy_url,
                                headers=headers,
                                timeout=mcp_conf.get("timeout", 30_000) / 1000.0,  # 30s timeout
                                sse_read_timeout=mcp_conf.get("sse_read_timeout", 300_000) / 1000.0,  # 300s (5min) timeout
                                terminate_on_close=False  # Always False to prevent async issues
                            )
                        elif mcp_conf.get("transport") == "HTTP_SSE":
                            conn_params = SseConnectionParams(
                                url=proxy_url,
                                headers=headers,
                                timeout=mcp_conf.get("timeout", 30_000) / 1000.0,  # 30s timeout
                                sse_read_timeout=mcp_conf.get("sse_read_timeout", 300_000) / 1000.0  # 300s (5min) timeout
                            )

                        # Create toolset with error handling
                        tool_name = sanitize_name(tool_cfg["name"]) 
                        toolset = MCPToolset(
                            connection_params=conn_params,
                            # tool_filter=[tool_name]                 # enable if need tools filtering

                        )
                        tools.append(toolset)

                except Exception as e:
                    # Log warning for failed tool creation and skip
                    logger.warning(f"Failed to create MCP tool '{tool_cfg.get('name', 'unknown')}': {str(e)}")
                    continue

        # Add custom user-defined tools
        if self.custom_tools:
            tools.extend(self.custom_tools)

        return tools

    def _build_agent_from_config(self, config):
        llm = FlotorchADKLLM(
            model_id=config["llm"]["callableName"],
            api_key=self.api_key,
            base_url=self.base_url,
            tracing_manager=self.tracing_manager
        )
        tools = self._build_tools(config)
        input_schema = None
        output_schema = None
        if "inputSchema" in config and config["inputSchema"] is not None:
            input_schema = schema_to_pydantic_model("InputSchema", config["inputSchema"])
        if "outputSchema" in config and config["outputSchema"] is not None:
            output_schema = schema_to_pydantic_model("OutputSchema", config["outputSchema"])

        input_schema_dict = config.get("inputSchema")
        agent_params = self._prepare_agent_parameters_dict(config, llm, tools, input_schema, output_schema, input_schema_dict)
        agent = LlmAgent(
            **agent_params
        )
        return agent

    def before_agent_callback_validator(self, callback_context, input_schema_dict):
        """Validate input before agent processing."""
        try:
            input_data = self._extract_input_from_callback_context(callback_context)
            if not input_data:
                return None
            is_valid = validate_data_against_schema(input_data, input_schema_dict)
            if not is_valid:
                error_msg = f"Input schema validation failed: data does not match the required schema. schema configured: {input_schema_dict}"
                logger.warning(f"Input validation failed for agent '{self.agent_name}': {error_msg}")
                return self._create_callback_error_response(error_msg)

        except Exception as e:
            logger.error(Error(operation="FlotorchADKAgent.before_agent_callback", error=e))
            return self._create_callback_error_response(f"Callback error: {e}")

        return None

    def _prepare_agent_parameters_dict(self, config, llm, tools, input_schema, output_schema, input_schema_dict=None):
        """Prepare agent parameters as a dictionary"""
        comp_params = {
            "name":sanitize_name(config["name"]),
            "model":llm,
            "instruction":remove_curly_braces(config["systemPrompt"]),
            "description":remove_curly_braces(config.get("goal", "")),
            "tools":tools,
            "input_schema":input_schema,
            "output_schema":output_schema
        }
        if self.tracing_manager:
            # Create merged before_agent_callback that runs both tracing and validation
            def merged_before_agent_callback(callback_context):
                """Merged callback that runs tracing first, then validation."""
                # Then, run validation callback if input schema is defined
                if input_schema_dict:
                    validation_result = self.before_agent_callback_validator(callback_context, input_schema_dict)
                    if not validation_result:
                        return validation_result

                return self.tracing_callbacks.before_agent_callback(callback_context)
                
            
            comp_params.update({
                "before_agent_callback":merged_before_agent_callback,
                "after_agent_callback":self.tracing_callbacks.after_agent_callback,
                "before_model_callback":self.tracing_callbacks.before_model_callback,
                "after_model_callback":self.tracing_callbacks.after_model_callback,
                "before_tool_callback":self.tracing_callbacks.before_tool_callback,
                "after_tool_callback":self.tracing_callbacks.after_tool_callback
            })
        elif input_schema_dict:
            # If no tracing but we have input schema, just use validation callback
            def before_agent_callback(callback_context):
                return self.before_agent_callback_validator(callback_context, input_schema_dict)

            comp_params.update({
                "before_agent_callback":before_agent_callback
            })
        return comp_params

    def get_agent(self):
        return cast(LlmAgent, AgentProxy(self))

    def _get_synced_agent(self) -> LlmAgent:
        # Check if sync is enabled and interval has passed
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._agent

        sync_interval = self.config.get('syncInterval', 1000000)
        now = time.time()
        elapsed_time = now - self._last_reload
        
        if elapsed_time > sync_interval:
            logger.info(f"Sync started for agent '{self.agent_name}' - reload interval ({sync_interval}s) passed")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    self._agent = self._build_agent_from_config(self.config)
                    logger.info(f"Sync completed - agent '{self.agent_name}' successfully reloaded with new configuration")
                else:
                    logger.info(f"Sync completed - agent '{self.agent_name}' configuration unchanged")
            except Exception as e:
                logger.warning(f"Failed to reload agent config for '{self.agent_name}'. Using previous agent. Reason: {str(e)}")
            finally:
                self._last_reload = now
        return self._agent

    def _extract_input_from_callback_context(self, callback_context) -> Optional[Any]:
        """Extract user input JSON string from ADK CallbackContext."""

        def try_parse(text):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        try:
            user_content = getattr(
                getattr(callback_context, "_invocation_context", None),
                "user_content",
                None,
            )
            if not user_content:
                user_content = getattr(callback_context, "user_content", None)

            parts = getattr(user_content, "parts", []) if user_content else []
            if parts and hasattr(parts[0], "text"):
                return try_parse(parts[0].text)

        except Exception:
            pass  # Swallow exceptions, return None gracefully

        return None

    @staticmethod
    def _create_callback_error_response(error_message: str) -> dict:
        """Return ADK-compatible error response object."""
        return {
            "parts": [{"text": f"{error_message}."}],
            "role": "system",
        }

    def get_tracer_ids(self, cast_to_list: bool = True) -> list:
        """Get the tracer ids"""
        tracer_ids = (self.tracing_manager and self.tracing_manager.tracer_ids) or []
        if cast_to_list:
            return list(tracer_ids)
        else:
            return tracer_ids

    def get_traces(self, additional_tracer_ids: Union[set, list, str] = None) -> str:
        """
        Get traces from the API for the given tracer IDs.
        
        Args:
            tracer_ids: Single trace ID (str), list of trace IDs, or set of trace IDs
            
        Returns:
            List of trace dictionaries from the API
            
        Raises:
            ValueError: If base_url or api_key is not provided
        """
        # Fetch traces using the common utility function
        results = fetch_traces_from_api(
            existing_tracer_ids=self.get_tracer_ids(cast_to_list=False),
            additional_tracer_ids=additional_tracer_ids,
            base_url=self.base_url, api_key=self.api_key
        )
        
        return json.dumps(results, ensure_ascii=False)

    def get_latest_config(self):
        """
        Get the latest config from the API.
        """
        sync_enabled = self.config.get('syncEnabled', False)
        if sync_enabled:
            sync_interval = self.config.get('syncInterval', 1000000)
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


class AgentProxy(LlmAgent):
    def __init__(self, manager: "FlotorchADKAgent"):
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

    def get_tracer_ids(self):
        """Get tracer IDs from the manager"""
        return self._manager.get_tracer_ids()

    def get_traces(self, additional_tracer_ids: Union[set[str], list[str], str] = None):
        """Get traces from the manager"""
        return self._manager.get_traces(additional_tracer_ids=additional_tracer_ids)

# Usage:
# Warning suppressions are automatically applied when importing this module.
# To disable: set environment variable FLOTORCH_NO_AUTO_SUPPRESS=1
# flotroch = FlotorchADKClient("agent-one", enable_memory=True)
# agent = flotroch.get_agent()
# memory_service = FlotorchMemoryService(...)  # Create your memory service
# runner = Runner(agent=agent, memory_service=memory_service, ...)  # Pass memory service to runner
# Now use agent as a normal LlmAgent with memory support!