"""Flotorch Memory Tool - Simple module-based tool like mem0_memory."""

from typing import Any

from strands.types.tools import ToolResult, ToolResultContent, ToolUse
from strands.tools.tools import PythonAgentTool
from flotorch.sdk.memory import FlotorchMemory
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error, ObjectCreation

logger = get_logger()

# Tool specification at module level (like mem0_memory)
TOOL_SPEC = {
    "name": "flotorch_memory",
    "description": (
        "Memory management tool for storing and retrieving information using Flotorch Memory.\n\n"
        "Actions:\n"
        "- add: Store new information (requires content)\n"
        "- search: Find relevant memories (requires query)\n"
        "- list: List all memories\n"
        "\nNote: This tool is pre-configured with user and app credentials.\n"
    ),
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform (add, search, list)",
                    "enum": ["add", "search", "list"],
                },
                "content": {
                    "type": "string",
                    "description": "Content to store (required for add action)",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (required for search action)",
                }
            },
            "required": ["action"],
        }
    },
}

MEMORY_LIMIT = 20
class FlotorchMemoryTool(PythonAgentTool):
    """Modular wrapper for Flotorch Memory Tool."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        provider_name: str,
        user_id: str,
        app_id: str
    ) -> None:
        """
        Initialize with configuration.
        
        Args:
            api_key: API key for Flotorch authentication
            base_url: Base URL for Flotorch API
            provider_name: Provider name for memory operations
            user_id: User ID for memory operations
            app_id: App ID for memory operations
        """
        # Store instance config - all parameters are required
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = provider_name
        self.user_id = user_id
        self.app_id = app_id
        
        # Initialize Flotorch Memory SDK for this instance
        self.memory = FlotorchMemory(
            api_key=self.api_key,
            base_url=self.base_url,
            provider_name=self.provider_name
        )
        
        # Log object creation
        logger.info(
            ObjectCreation(
                class_name="FlotorchMemoryTool",
                extras={
                    'base_url': self.base_url,
                    'provider_name': self.provider_name,
                    'user_id': self.user_id,
                    'app_id': self.app_id
                }
            )
        )
        
        # Create a wrapper function that uses this instance's config
        def flotorch_memory_wrapper(tool: ToolUse, **kwargs: Any) -> ToolResult:
            return self.flotorch_memory(tool, **kwargs)
        
        # Initialize the parent PythonAgentTool
        super().__init__(
            tool_name="flotorch_memory",
            tool_spec=TOOL_SPEC,
            tool_func=flotorch_memory_wrapper
        )

    def flotorch_memory(self, tool: ToolUse, **kwargs: Any) -> ToolResult:
        """
        Flotorch Memory tool function - exactly like mem0_memory pattern.
        
        Args:
            tool: Tool use object containing action and parameters
            **kwargs: Additional keyword arguments
            
        Returns:
            ToolResult containing the operation result
        """
        try:
            # Extract tool parameters
            tool_use_id = tool.get("toolUseId", "default-id")
            tool_input = tool.get("input", {})
            
            action = tool_input.get("action")
            if not action:
                raise ValueError("action parameter is required")
            
            memory = self.memory
            user_id = self.user_id
            app_id = self.app_id
            
            # Handle actions
            if action == "add":
                content = tool_input.get("content")
                if not content:
                    raise ValueError("content is required for add action")
                
                result = memory.add(
                    messages=[{"role": "user", "content": content}],
                    userId=user_id,
                    appId=app_id,
                    metadata={"source": "strands"}
                )
                
                memory_id = result.get('id')
                if memory_id:
                    response_text = f"Memory stored successfully. ID: {memory_id}"
                else:
                    response_text = "Memory storage failed - no ID returned from server"
                
            elif action == "search":
                query = tool_input.get("query")
                if not query:
                    raise ValueError("query is required for search action")
                
                result = memory.search(
                    userId=user_id,
                    appId=app_id,
                    query=query,
                    limit=MEMORY_LIMIT
                )
                
                memories = result.get('data', [])
                if not memories:
                    response_text = "No relevant memories found."
                else:
                    response_text = f"Found {len(memories)} relevant memories:\n"
                    for i, mem in enumerate(memories, 1):
                        content = mem.get('memory') or mem.get('content', '')
                        response_text += f"{i}. {content}\n"
                
            elif action == "list":
                result = memory.search(
                    userId=user_id,
                    appId=app_id,
                    query="*",
                    limit=MEMORY_LIMIT
                )
                
                memories = result.get('data', [])
                if not memories:
                    response_text = "No memories found."
                else:
                    response_text = f"Total memories: {len(memories)}\n"
                    for i, mem in enumerate(memories, 1):
                        content = mem.get('memory') or mem.get('content', '')
                        memory_id = mem.get('id', 'unknown')
                        response_text += f"{i}. [{memory_id}] {content[:100]}...\n"
                
            else:
                raise ValueError(f"Invalid action: {action}")
            
            # Return success response
            return ToolResult(
                toolUseId=tool_use_id,
                status="success",
                content=[ToolResultContent(text=response_text)]
            )
        
        except Exception as e:
            logger.error(Error(operation="FlotorchMemoryTool.flotorch_memory", error=e))
            return ToolResult(
                toolUseId=tool_use_id,
                status="error",
                content=[ToolResultContent(text=f"Error: {str(e)}")]
            )