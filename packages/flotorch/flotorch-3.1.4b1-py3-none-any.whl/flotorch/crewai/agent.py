"""CrewAI agent management and configuration for Flotorch."""

import os
import time
import re
import json

from typing import Any, Dict, List, cast, Optional, Union

from crewai import Agent, Task
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from pydantic import BaseModel, Field, create_model

from flotorch.crewai.llm import FlotorchCrewAILLM
from flotorch.sdk.utils.http_utils import http_get
# tracing
from flotorch.crewai.instrumentation.listeners import FloTorchCrewAIEventListener
from flotorch.sdk.flotracer.config import FloTorchFramework
from flotorch.sdk.utils.common_utils import initialize_tracing_manager
from flotorch.sdk.utils.common_utils import fetch_traces_from_api
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error, ObjectCreation

load_dotenv()
logger = get_logger()

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
    """
    properties = schema.get("properties", {})
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
        description = prop_schema.get("description", "")
        fields[prop] = (field_type, Field(description=description))
    return create_model(model_name, **fields)

class FlotorchCrewAIAgent:
    """
    Manager/config class for Flotorch CrewAI agent.

    Builds CrewAI Agent from config on demand. Supports on-demand config
    reload based on interval in config['sync'].

    Usage:
        flotorch = FlotorchCrewAIAgent("agent_one")
        agent = flotorch.get_agent()
        task = flotorch.get_task()
    """

    def __init__(
        self,
        agent_name: str,
        custom_tools: List = None,
        base_url: str = None,
        api_key: str = None,
        tracer_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agent manager.

        Args:
            agent_name: Name of the agent to load.
            custom_tools: Optional list of custom tools.
            base_url: Optional base URL for the API. Falls back to FLOTORCH_BASE_URL env var
            api_key: Optional API key for authentication. Falls back to FLOTORCH_API_KEY env var
        """
        self.agent_name = agent_name
        self.custom_tools = custom_tools or []
        
        # Store base_url and api_key, using environment variables as fallback
        self.base_url = base_url or os.environ.get("FLOTORCH_BASE_URL")
        self.api_key = api_key or os.environ.get("FLOTORCH_API_KEY")

        self.config = self._fetch_agent_config(agent_name)
        self.tracing_manager = initialize_tracing_manager(
            base_url=base_url,
            api_key=api_key,
            tracer_config=tracer_config or {},
            framework=FloTorchFramework.FLOTORCH_CREWAI
        )
        # Initialize CrewAI-specific event listener if tracing is enabled
        if self.tracing_manager:
            self.event_listener = FloTorchCrewAIEventListener(self.tracing_manager)
        self._agent = self._build_agent_from_config(self.config)
        self._task = self._build_task_from_config(self.config)
        self._last_reload = time.time()
        
        # Log object creation
        logger.info(
            ObjectCreation(
                class_name="FlotorchCrewAIAgent",
                extras={'agent_name': self.agent_name}
            )
        )

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch agent config from API.
        """
        if not self.base_url:
            raise ValueError("base_url is required to fetch agent configuration")
        
        if not self.api_key:
            raise ValueError("api_key is required to fetch agent configuration")
        
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
            logger.error(Error(operation="FlotorchCrewAIAgent._fetch_agent_config", error=e))
            raise e


    def _build_agent_from_config(self, config):
        """
        Build a complete CrewAI agent from configuration with tools.
        
        Args:
            config: Agent configuration dictionary.
            
        Returns:
            Configured CrewAI Agent instance with tools.
        """
        # Build the LLM
        llm = FlotorchCrewAILLM(
            model_id=config["llm"]["callableName"],
            api_key=self.api_key,
            base_url=self.base_url,
            tracing_manager=self.tracing_manager
        )

        # Build tools using the existing method
        tools = self._build_tools(config = config)

        # Create the agent with all configuration
        agent = Agent(
            role=config["name"],
            goal=config.get("goal", ""),
            backstory=config["systemPrompt"],
            llm=llm,
            tools=tools,
            allow_delegation=False
        )
        
        return agent

    def _build_tools(self, config) -> List:
        """
        Build and return a list of all available tools.
        
        Returns:
            List of tools including custom tools and MCP tools.
        """
        all_tools = []

        # Add custom tools if provided
        if self.custom_tools:
            crewai_tools = self.custom_tools
            all_tools.extend(crewai_tools)

        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                mcp_conf = tool_cfg["config"]
                conn_params = None
                proxy_url = f"{self.base_url}/v1/mcps/{tool_cfg['name']}/proxy"
                try:
                    # Build connection params with better defaults
                    headers = dict(mcp_conf.get("headers", {}))
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"

                    if mcp_conf.get("transport") == "HTTP_STREAMABLE":
                        conn_params = {
                            "url": proxy_url,
                            "transport": "streamable-http",
                            "headers": headers
                        }
                    elif mcp_conf.get("transport") == "HTTP_SSE":
                        conn_params = {
                            "url": proxy_url,
                            "transport": "sse",
                            "headers": headers
                        }
                    
                    # Create MCP tools using the connection parameters
                    if conn_params:
                        try:
                            tool_name = sanitize_name(tool_cfg["name"])
                            adapter = MCPServerAdapter(conn_params, connect_timeout=60) # Add tool_name to it to enable tools filtering
                            all_tools.extend(list(adapter.tools))
                        except Exception:
                            continue
                            
                except Exception as e:
                    # Silently skip failed tools instead of printing warnings
                    continue

        return all_tools


    def get_agent(self):
        return cast(Agent, AgentProxy(self))


    def _get_synced_agent(self) -> Agent:
        # Check if sync is enabled and interval has passed
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._agent
            
        sync_interval = self.config.get('syncInterval', 1000000)
        now = time.time()
        if now - self._last_reload > sync_interval:
            logger.info("[Sync] Reload interval passed. Attempting to reload agent/task...")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    self._agent = self._build_agent_from_config(self.config)
                    self._task = self._build_task_from_config(self.config)
                    logger.info("[Sync] Agent successfully reloaded.")
            except Exception as e:
                logger.warning(f"[Warning] [Sync] Failed to reload agent config. Using previous agent. Reason: {e}")
            finally:
                self._last_reload = now
        return self._agent

    @property
    def goal(self):
        """Get the agent's goal from the configuration."""
        return self.config.get('goal', '')

    @goal.setter
    def goal(self, new_goal):
        """Setter for the goal property."""
        raise AttributeError("Please use Flotorch APIGateway to update the goal.")

    @property
    def system_prompt(self):
        """Get the agent's system prompt from the configuration."""
        return self.config.get('systemPrompt', '')

    @system_prompt.setter
    def system_prompt(self, new_system_prompt):
        """Setter for the system prompt property."""
        raise AttributeError("Please use Flotorch APIGateway to update the system prompt.")

    def _build_task_from_config(self, config):

        goal = config["goal"]
        if re.search(r'\{[^}]*\}', goal):
            formatted_goal = goal
        else:
            formatted_goal =goal + "\n user: {query} "

        if config.get("outputSchema"):
            output_schema = schema_to_pydantic_model(
                "OutputSchema",
                config["outputSchema"]
            )
            return Task(
                description=formatted_goal,
                agent=self._agent,
                output_pydantic=output_schema,
                expected_output=config["systemPrompt"]
            )
        else:
            return Task(
                description=formatted_goal,
                agent=self._agent,
                expected_output=config["systemPrompt"]
            )

    def _get_synced_task(self) -> Task:
        # Check if sync is enabled and interval has passed
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._task
            
        sync_interval = self.config.get('syncInterval', 1000000)
        now = time.time()
        if now - self._last_reload > sync_interval:
            logger.info("[Sync] Reload interval passed. Attempting to reload agent/task...")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    self._agent = self._build_agent_from_config(self.config)
                    self._task = self._build_task_from_config(self.config)
                    logger.info("[Sync] Task successfully reloaded.")
            except Exception as e:
                logger.warning(f"[Warning] [Sync] Failed to reload task config. Using previous task. Reason: {e}")
            finally:
                self._last_reload = now
        return self._task

    def get_task(self):
        return cast(Task, TaskProxy(self))

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data against the agent's input schema.

        Args:
            input_data: The input data to validate (dict, str, or any JSON-serializable type)

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails or no input schema is configured
        """
        from flotorch.sdk.utils.validation_utils import validate_data_against_schema

        input_schema = self.config.get("inputSchema")
        if not input_schema:
            return True

        is_valid = validate_data_against_schema(input_data, input_schema)

        if not is_valid:
            error_msg = f"Input schema validation failed: data does not match the required schema. schema configured: {input_schema}"
            logger.warning(f"Input validation failed for agent '{self.agent_name}': {error_msg}")
            raise ValueError(error_msg)

        return True

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
        Get the new config from the API.
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


class AgentProxy(Agent):
    def __init__(self, manager: "FlotorchCrewAIAgent"):
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

class TaskProxy(Task):
    def __init__(self, manager: "FlotorchCrewAIAgent"):
        self._manager = manager

    def __getattr__(self, item):
        return getattr(self._manager._get_synced_task(), item)

    def __setattr__(self, key, value):
        if key == "_manager":
            return object.__setattr__(self, key, value)
        return setattr(self._manager._get_synced_task(), key, value)