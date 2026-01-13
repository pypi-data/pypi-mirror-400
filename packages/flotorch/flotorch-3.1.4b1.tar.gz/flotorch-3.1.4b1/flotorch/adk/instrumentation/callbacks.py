from typing import Any, Dict, Optional
from opentelemetry.trace import StatusCode, SpanKind, get_current_span, set_span_in_context

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.adk.models import LlmResponse, LlmRequest

from flotorch.sdk.flotracer.manager import FloTorchTracingManager
from flotorch.sdk.flotracer.config import GenAIOperationName, GenAISystem, FloTorchFramework
from flotorch.sdk.flotracer.constants import *
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error

logger = get_logger()

class FloTorchADKCallbacks:
    """ADK-specific callbacks for OpenTelemetry tracing (centralized)."""

    def __init__(self, tracing_manager: FloTorchTracingManager, agent_name: str = None):
        self.tracing_manager = tracing_manager
        self.agent_name = agent_name or 'agent'
        self.agent_spans = {}  # Store agent spans: {span_id: span_object}
        self.tool_agent_mapping = {}  # Store tool-agent mapping: {span_id: agent_span_id}
        self.custom_agent_spans = {}  # Store custom agent spans for distributed tracing: {adk_span_id: custom_span_object}

    def _get_agent_name(self, callback_context: CallbackContext) -> str:
        """Get agent name from stored value"""
        return getattr(callback_context, 'agent_name', self.agent_name)

    def _get_model_name(self, callback_context: CallbackContext) -> str:
        """Get model name from stored value"""
        return getattr(callback_context, 'name', 'llm')

    def _get_tool_name(self, tool: BaseTool) -> str:
        """Get tool name from tool object or use default"""
        return getattr(tool, 'name', 'tool')

    def set_agent_mapping(self, span):
        """Set mapping to agent span by traversing the mapping chain"""
        try:
            span_id = span.get_span_context().span_id
            parent_span_id = span.parent.span_id if span.parent else None
            if parent_span_id:
                key = parent_span_id
                while key in self.tool_agent_mapping:
                    if key == self.tool_agent_mapping[key]:
                        self.tool_agent_mapping[span_id] = key
                        break
                    key = self.tool_agent_mapping[key]
        except Exception as e:
            logger.warning("Warning: Failed to set agent mapping")

    def _find_agent_parent_via_mapping(self, current_span):
        """Find agent parent span using our mapping system"""
        try:
            span_id = current_span.get_span_context().span_id
            trace_id = current_span.get_span_context().trace_id
            # Check if this span has a mapping to an agent
            if span_id in self.tool_agent_mapping:
                agent_span_id = self.tool_agent_mapping[span_id]
                if agent_span_id in self.agent_spans:
                    agent_span = self.agent_spans[agent_span_id]
                    return agent_span
                logger.warning("Warning: Agent span not found")
        except Exception as e:
            logger.warning("Warning: Failed to find agent parent via mapping")
        return None

    def _create_custom_tool_span_with_context(self, tool: BaseTool, args: Dict[str, Any], tool_response: Dict[str, Any], adk_tool_span, agent_parent):
        """Create custom tool span using 'with' statement with agent as parent"""
        try:
            tool_name = self._get_tool_name(tool)
            
            # Create agent context from the agent span
            agent_context = set_span_in_context(agent_parent)
            
            # Create tool span using 'with' statement
            with self.tracing_manager.tracer.start_span(
                name=adk_tool_span.name,  # Use same name as ADK span
                kind=SpanKind.INTERNAL,
                context=agent_context
            ) as custom_tool_span:
                span_id = custom_tool_span.get_span_context().span_id
                if self.tracing_manager.should_log_span(custom_tool_span):
                    logger.info(f"🔧 TRACES: Tool: {tool_name} [SPAN_ID: {span_id:016x}]")
                
                self._set_tool_attributes(custom_tool_span, tool, args, tool_response)
                
        except Exception as e:
            logger.error(Error(operation="Warning: Failed to create custom tool span",error=e))

    def before_agent_callback(self, callback_context: CallbackContext) -> Optional[types.Content]:
        # Get the existing session ID and user ID from the invocation context
        existing_session_id = callback_context._invocation_context.session.id
        
        # Session management - use existing session ID
        if "session_id" not in callback_context.state:
            callback_context.state["session_id"] = existing_session_id

        # Get agent name from stored value
        agent_name = self._get_agent_name(callback_context)
        # Try to get the current span (ADK framework's span) and add our attributes to it
        current_span = get_current_span()
        # Only set attributes if span exists and is recording
        if current_span and current_span.is_recording():
            try:
                # Safely get agent object and extract id/description with fallbacks
                agent_obj = getattr(callback_context, 'agent', None)
                agent_id = str(getattr(agent_obj, 'id', agent_name)) if agent_obj else agent_name
                agent_description = str(getattr(agent_obj, 'description', '')) if agent_obj else ''
                
                current_span.set_attributes({
                    "gen_ai.operation.name": GenAIOperationName.INVOKE_AGENT.value,
                    "gen_ai.system": GenAISystem.FLOTORCH.value,
                    "gen_ai.conversation.id": callback_context.state["session_id"],
                    "gen_ai.agent.name": agent_name,
                    "gen_ai.agent.id": agent_id,
                    "gen_ai.datasource.id": "",
                    "gen_ai.agent.description": agent_description,
                })
            except Exception as e:
                logger.warning(f"Warning: Failed to set agent attributes: {e}")
        
        parent_span = self.tracing_manager.get_current_span_from_context()
        custom_agent_span = None
        
        if parent_span and current_span:
            try:
                adk_trace_id = current_span.get_span_context().trace_id
                parent_trace_id = parent_span.get_span_context().trace_id
                
                if adk_trace_id != parent_trace_id:
                    current_span.set_attribute("flotorch.export", False)
                    
                    from opentelemetry import trace
                    parent_context = trace.set_span_in_context(parent_span)
                    
                    custom_agent_span_cm = self.tracing_manager.tracer.start_as_current_span(
                        f"agent.{agent_name}",
                        kind=SpanKind.INTERNAL,
                        context=parent_context,
                        attributes={
                            "gen_ai.operation.name": GenAIOperationName.INVOKE_AGENT.value,
                            "gen_ai.system": GenAISystem.FLOTORCH.value,
                            "gen_ai.conversation.id": callback_context.state.get("session_id", ""),
                            "gen_ai.agent.name": agent_name,
                        }
                    )
                    custom_agent_span = custom_agent_span_cm.__enter__()
                    custom_agent_span._flotorch_cm = custom_agent_span_cm
                    
                    custom_span_id = custom_agent_span.get_span_context().span_id
                    custom_trace_id = custom_agent_span.get_span_context().trace_id
                    self.agent_spans[custom_span_id] = custom_agent_span
                    self.tool_agent_mapping[custom_span_id] = custom_span_id
                    
                    adk_span_id = current_span.get_span_context().span_id
                    self.tool_agent_mapping[adk_span_id] = custom_span_id
                    self.custom_agent_spans[adk_span_id] = custom_agent_span
                    callback_context.state['_flotorch_custom_agent_span_id'] = adk_span_id
                    
                    if self.tracing_manager.should_log_span(custom_agent_span):
                        logger.info("TRACES: =========START=========")
                        logger.info(f"TRACES:🔧 Agent: {agent_name} [TRACE_ID: {custom_trace_id:032x}]")
                else:
                    span_id = current_span.get_span_context().span_id
                    self.agent_spans[span_id] = current_span
                    self.tool_agent_mapping[span_id] = span_id
                    if adk_trace_id not in self.tracing_manager.tracer_ids:
                        self.tracing_manager.tracer_ids.add(f"{adk_trace_id:032x}")
                    if self.tracing_manager.should_log_span(current_span):
                        logger.info("TRACES: =========START=========")
                        logger.info(f"TRACES:🔧 Agent: {agent_name} [TRACE_ID: {adk_trace_id:032x}]")
            except Exception as e:
                logger.warning(f"Failed to create custom agent span: {e}")
                if current_span:
                    span_id = current_span.get_span_context().span_id
                    self.agent_spans[span_id] = current_span
                    self.tool_agent_mapping[span_id] = span_id
        elif current_span:
            try:
                span_id = current_span.get_span_context().span_id
                trace_id = current_span.get_span_context().trace_id
                self.agent_spans[span_id] = current_span
                self.tool_agent_mapping[span_id] = span_id
                if trace_id not in self.tracing_manager.tracer_ids:
                    self.tracing_manager.tracer_ids.add(f"{trace_id:032x}")
                if self.tracing_manager.should_log_span(current_span):
                    logger.info("TRACES: =========START=========")
                    logger.info(f"TRACES:🔧 Agent: {agent_name} [TRACE_ID: {trace_id:032x}]")
            except Exception as e:
                logger.warning(f"Failed to store agent span: {e}")
        
        return None

    def after_agent_callback(self, callback_context: CallbackContext) -> Optional[types.Content]:
        adk_span_id = callback_context.state.get('_flotorch_custom_agent_span_id')
        custom_agent_span = self.custom_agent_spans.pop(adk_span_id, None) if adk_span_id else None
        
        if adk_span_id and '_flotorch_custom_agent_span_id' in callback_context.state:
            try:
                del callback_context.state['_flotorch_custom_agent_span_id']
            except (KeyError, AttributeError):
                pass
        
        if custom_agent_span:
            try:
                span_id = custom_agent_span.get_span_context().span_id
                trace_id = custom_agent_span.get_span_context().trace_id
                
                self.agent_spans.pop(span_id, None)
                self.tool_agent_mapping.pop(span_id, None)
                
                custom_agent_span.set_status(StatusCode.OK)
                if hasattr(custom_agent_span, '_flotorch_cm'):
                    custom_agent_span._flotorch_cm.__exit__(None, None, None)
                else:
                    custom_agent_span.end()
                
                if self.tracing_manager.should_log_span(custom_agent_span):
                    logger.info(f"TRACES: 🔧 Agent completed [TRACE_ID: {trace_id:032x}]")
                    logger.info(f"TRACES: =========END=========")
                    logger.info(f"👀 View here on HTTP GET request:\n{self.tracing_manager.agent_config['base_url']}/v1/traces/{trace_id:032x}\n🔑 Access code: Your API Key")
            except Exception as e:
                logger.error(Error(operation="Failed to cleanup custom agent span", error=e))
        else:
            current_span = get_current_span()
            if current_span:
                try:
                    span_id = current_span.get_span_context().span_id
                    trace_id = current_span.get_span_context().trace_id
                    self.agent_spans.pop(span_id, None)
                    self.tool_agent_mapping.pop(span_id, None)
                    if self.tracing_manager.should_log_span(current_span):
                        logger.info(f"TRACES: 🔧 Agent completed [TRACE_ID: {trace_id:032x}]")
                        logger.info(f"TRACES: =========END=========")
                        logger.info(f"👀 View here on HTTP GET request:\n{self.tracing_manager.agent_config['base_url']}/v1/traces/{trace_id:032x}\n🔑 Access code: Your API Key")
                    current_span.set_status(StatusCode.OK)
                except Exception as e:
                    logger.error(Error(operation="Failed to add traces on agent completed callback", error=e))
        return None

    def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        # Get current span (ADK framework's LLM span)
        current_span = get_current_span()
        
        # Only enable ADK model tracing when SDK tracing is disabled
        if self.tracing_manager.config.enable_plugins_llm_tracing:
            # Get model name from stored value
            model_name = self._get_model_name(callback_context)
            
            # Get agent name from stored value
            agent_name = self._get_agent_name(callback_context)
            
            # Modify the current span
            if current_span:
                try:
                    # Set standard attributes (spec-compliant) on the existing ADK span
                    attributes = {
                        "gen_ai.operation.name": GenAIOperationName.CHAT.value,
                        "gen_ai.system": GenAISystem.FLOTORCH.value,
                        "gen_ai.request.model": model_name,
                        "gen_ai.agent.name": agent_name,
                        "flotorch.tracing_mode": self.tracing_manager.framework,
                        "flotorch.model_name": model_name
                    }
                    
                    # Add request content if available
                    if hasattr(llm_request, 'messages') and llm_request.messages:
                        # Get the last user message
                        user_messages = [msg for msg in llm_request.messages if msg.role == 'user']
                        if user_messages:
                            last_user_message = user_messages[-1].parts[0].text if user_messages[-1].parts else ''
                            attributes["gen_ai.request.prompt"] = last_user_message
                    
                    # Add tools info if available
                    if hasattr(llm_request, 'tools_dict') and llm_request.tools_dict:
                        attributes["gen_ai.request.tools_count"] = len(llm_request.tools_dict)
                    
                    current_span.set_attributes(attributes)
                    self.set_agent_mapping(current_span)
                    span_id = current_span.get_span_context().span_id
                    model_name = self._get_model_name(callback_context)
                    if self.tracing_manager.should_log_span(current_span):
                        logger.info(f"TRACES: 🔧 LLM: {model_name} [SPAN_ID: {span_id:016x}]")
                except Exception as e:
                    # If setting attributes fails, just continue
                    pass

        return None

    def after_model_callback(self, callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
        # Only enable ADK model tracing when SDK tracing is disabled
        if self.tracing_manager.config.enable_plugins_llm_tracing:
            current_span = get_current_span()
            # Get model name from stored value
            model_name = self._get_model_name(callback_context)
            
            # Get current span and add response attributes
            if current_span:
                try:
                    # Try to update the span name (this is now the call_llm span)
                    try:
                        current_span.update_name(f"LLM ADK: {model_name}")
                    except Exception as name_error:
                        # If update_name fails, continue with default name
                        pass
                    
                    attributes = {
                        "gen_ai.response.model": model_name,
                        "gen_ai.response.success": True
                    }
                    
                    # Add response content if available
                    if hasattr(llm_response, 'content') and llm_response.content:
                        if hasattr(llm_response.content, 'parts') and llm_response.content.parts:
                            response_text = llm_response.content.parts[0].text if llm_response.content.parts else ''
                            if response_text:  # Only set if we have actual text
                                attributes["gen_ai.response.content"] = response_text
                                attributes["gen_ai.response.content_length"] = len(response_text)
                    
                    current_span.set_attributes(attributes)
                    # Print LLM span completion only if ADK tracing is enabled
                    if self.tracing_manager.config.enable_plugins_llm_tracing:
                        span_id = current_span.get_span_context().span_id
                        if self.tracing_manager.should_log_span(current_span):
                            logger.info(f"TRACES: 🔧 LLM: {model_name} [SPAN_ID: {span_id:016x}]")
                except Exception as e:
                    # If setting attributes fails, just continue
                    pass        
        return None

    def before_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict[str, Any]]:
        current_span = get_current_span()
        if current_span:
            # Set agent mapping for tool span
            self.set_agent_mapping(current_span)
            
            # Only suppress ADK tool spans if we're in ADK context
            if self.tracing_manager.framework == FloTorchFramework.FLOTORCH_ADK:
                current_span.set_attribute("flotorch.export", False)

        return None

    def after_tool_callback(self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        # Get the current ADK tool span
        adk_tool_span = get_current_span()
        if not adk_tool_span:
            return tool_response
        
        # Find agent parent via our mapping system
        agent_parent = self._find_agent_parent_via_mapping(adk_tool_span)
        
        if agent_parent:
            # Create custom tool span using 'with' statement
            self._create_custom_tool_span_with_context(tool, args, tool_response, adk_tool_span, agent_parent)
        else:
            # Fallback: let ADK span be exported with its original parent
            adk_tool_span.set_attribute("flotorch.export", True)
            # Add tool response to the ADK span
            if tool_response:
                adk_tool_span.set_attribute("gen_ai.tool.response", str(tool_response))
        
        return tool_response

    def _set_tool_attributes(self, span, tool: BaseTool, args: Dict[str, Any], tool_response: Dict[str, Any] = None):
        """Set comprehensive tool attributes on a span (SDK pattern)."""
        # Safety check: ensure span is recording
        try:
            if not span or not span.is_recording():
                return
            
            tool_name = self._get_tool_name(tool)
            
            tool_attrs = {
                # Core GenAI attributes (required)
                GEN_AI_SYSTEM: GEN_AI_SYSTEM_FLOTORCH,
                GEN_AI_OPERATION_NAME: GenAIOperationName.EXECUTE_TOOL.value,
                GEN_AI_OUTPUT_TYPE: GEN_AI_OUTPUT_TYPE_TEXT,
                GEN_AI_TOKEN_TYPE: GEN_AI_TOKEN_TYPE_TOKENS,
                
                # Tool-specific attributes
                "gen_ai.tool.name": tool_name,
                "gen_ai.tool.type": "function",
                "gen_ai.tool.description": getattr(tool, 'description', ''),
            }
            
            # Add tool arguments
            if args:
                tool_attrs["gen_ai.tool.args"] = str(args)
                tool_attrs["gen_ai.tool.args_length"] = len(str(args))
            
            # Add tool response if available
            if tool_response:
                # Determine output type dynamically
                output_type = str(type(tool_response)).lower()
                
                tool_attrs["gen_ai.response.success"] = True
                tool_attrs["gen_ai.tool.response"] = str(tool_response)
                tool_attrs["gen_ai.tool.response_length"] = len(str(tool_response))
                tool_attrs["gen_ai.output.type"] = output_type
            
            span.set_attributes(tool_attrs)
            span.set_status(StatusCode.OK)
            
        except Exception as e:
            logger.error(Error(operation="Warning: Failed to set tool attributes", error=e))