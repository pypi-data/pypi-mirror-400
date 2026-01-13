#!/usr/bin/env python3
"""
CrewAI-specific event listener for OpenTelemetry tracing

This module provides CrewAI-specific event listener implementations that use the common tracing module.
Based on CrewAI event system: https://docs.crewai.com/en/concepts/event-listener
"""

from typing import Any, Dict, Optional
from datetime import datetime, timezone
from opentelemetry import trace
from opentelemetry.trace import Span,Status, StatusCode
from flotorch.sdk.flotracer.manager import FloTorchTracingManager
from flotorch.sdk.flotracer.config import GenAIOperationName, GenAISystem, GenAIOutputType
from flotorch.sdk.flotracer.constants import *
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error


logger = get_logger()


from crewai.events import BaseEventListener, crewai_event_bus
from crewai.events.types.crew_events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent
)
from crewai.events.types.agent_events import (
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent
)
from crewai.events.types.task_events import (
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent
)
from crewai.events.types.tool_usage_events import (
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
    ToolUsageErrorEvent
)
from crewai.events.types.llm_events import (
    LLMCallStartedEvent,
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
    LLMStreamChunkEvent
)
from crewai.events.types.memory_events import (
    MemoryQueryStartedEvent,
    MemoryQueryCompletedEvent,
    MemoryQueryFailedEvent,
    MemorySaveStartedEvent,
    MemorySaveCompletedEvent,
    MemorySaveFailedEvent,
    MemoryRetrievalStartedEvent,
    MemoryRetrievalCompletedEvent
)


class FloTorchCrewAIEventListener(BaseEventListener):
    """CrewAI-specific event listener for OpenTelemetry tracing with enhanced spec.ts compliance
     Ensures all spans are created within the root trace context to maintain
    a single trace ID across the entire Crew execution."""

    def __init__(self, tracing_manager: FloTorchTracingManager):
        self.tracing_manager = tracing_manager
        self.spans = {}  # Store spans by span_id
        self.setup_listeners(crewai_event_bus)
        # Root span/context persisted across Crew run to keep one trace
        self._root_span = None
        self._root_context = None

    def _create_custom_span(self, span_name: str, operation: GenAIOperationName,
                           system: GenAISystem = GenAISystem.FLOTORCH, **kwargs) -> Optional[Span]:
        """Create new span with proper context management anchored to root context when needed"""
        # Prefer current hierarchical span; fall back to root context to keep one trace
        parent_span = self.tracing_manager.get_current_span_from_context()
        ctx = trace.set_span_in_context(parent_span) if parent_span else self._root_context
        # Start as current span so HTTPX instrumentation sees active context
        if ctx is not None and hasattr(self.tracing_manager, 'tracer') and self.tracing_manager.tracer:
            cm = self.tracing_manager.tracer.start_as_current_span(span_name, context=ctx)
            span = cm.__enter__()
            # Register with manager for hierarchical context
            token = self.tracing_manager.current_span_var.set(span)
            span._flotorch_token = token
            span._flotorch_cm = cm
        else:
            span = self.tracing_manager.start_span_with_context(span_name)

        if span:
            # Set core GenAI attributes
            span.set_attribute("gen_ai.operation.name", operation.value)
            span.set_attribute("gen_ai.system", system.value)

            # Add any additional attributes
            for key, value in kwargs.items():
                if value is not None:
                    span.set_attribute(key, value)

        return span

    def _add_span_attributes(self, span: Span, attributes: Dict[str, Any]):
        """Safely add attributes to span with error handling"""
        if span and span.is_recording():
            try:
                for key, value in attributes.items():
                    if value is not None:
                        span.set_attribute(key, value)
            except Exception as e:
                # Silently ignore attribute setting errors
                pass

    def _end_span_safely(self, span: Span, span_name: str, success: bool = True, error_message: str = None):
        """Safely end span with proper status and duration"""
        if span:
            try:
                if span.is_recording():
                    # Set status
                    if not success and error_message:
                        span.set_status(StatusCode.ERROR, error_message)
                        span.set_attribute("gen_ai.response.success", False)
                        span.set_attribute("gen_ai.error.message", error_message[:1000])
                    else:
                        span.set_attribute("gen_ai.response.success", True)

                    span.end()
            except Exception as e:
                # Silently ignore span ending errors
                pass

    def setup_listeners(self, crewai_event_bus):
        """Setup all event listeners for CrewAI events"""

        # ============================================================================
        # CREW EVENTS
        # ============================================================================

        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            """Called when a Crew starts execution"""
            try:
                # Simple name logic: Name or empty string
                crew_name = getattr(event, 'crew_name', '')
                span_name = f"Crew: {crew_name}"

                # Create span with context management
                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.CHAT,
                    system=GenAISystem.FLOTORCH,
                    agent_name=crew_name,  # Crew acts like an agent
                    output_type=GenAIOutputType.TEXT.value
                )

                if span:
                    # Persist root span/context to anchor future spans in same trace
                    self._root_span = span
                    try:
                        self._root_context = trace.set_span_in_context(span)
                    except Exception:
                        self._root_context = None
                    try:
                        span_context = span.get_span_context()
                        trace_id = span_context.trace_id
                        if trace_id not in self.tracing_manager.tracer_ids:
                            self.tracing_manager.tracer_ids.add(f"{trace_id:016x}")
                        if self.tracing_manager.should_log_span(span):
                            logger.info("TRACES: =========START=========")
                            logger.info(f"TRACES: 🔧 Crew: {crew_name} [TRACE_ID: {trace_id:016x}]")
                    except Exception as e:
                        logger.warning("Warning: Failed to get span context in crew_started event")
                    # Add comprehensive spec.ts compliant attributes
                    self._add_span_attributes(span, {
                        # Core GenAI attributes
                        "gen_ai.conversation.id": str(getattr(event, 'conversation_id', '')) if getattr(event, 'conversation_id', None) else None,
                        "gen_ai.output.type": GenAIOutputType.TEXT.value,
                        "gen_ai.token.type": "tokens",
                        "gen_ai.crew.name": crew_name,
                        "gen_ai.crew.description": crew_name,
                        "gen_ai.crew.id": str(getattr(event, 'crew_id', '')) if getattr(event, 'crew_id', None) else None,
                    })

            except Exception as e:
                logger.warning("Warning: Failed to set span attributes in crew_started event")

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            """Called when a Crew completes execution"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                    # Add completion attributes
                    self._add_span_attributes(span, {
                        "gen_ai.response.success": True,
                        "gen_ai.output.type": GenAIOutputType.TEXT.value,
                    })
                    span.set_status(StatusCode.OK)
                    # Print END TRACING only if span was sampled
                    if self.tracing_manager.should_log_span(span):
                        cur_span = span.get_span_context()
                        trace_id = cur_span.trace_id
                        logger.info(f"TRACES: 🔧 Agent completed [TRACE_ID: {trace_id:016x}]")
                        logger.info("=========END=========")
                        logger.info(f"👀 View here on HTTP GET request:\n{self.tracing_manager.agent_config['base_url']}/v1/traces/{trace_id:016x}\n🔑 access code: Your API Key")
                    self.tracing_manager.end_span_with_context(span)
                self._root_span = None
                self._root_context = None
            except Exception as e:
                logger.error(Error(operation="Error in crew_completed event", error=e))

        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event):
            """Called when a Crew fails to complete execution"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                    error_message = str(getattr(event, 'error', ''))

                    # Add failure attributes
                    self._add_span_attributes(span, {
                        "gen_ai.response.success": False,
                        "gen_ai.error.type": "crew_execution_error",
                        "gen_ai.error.message": error_message[:1000],
                    })

                    span.set_status(StatusCode.ERROR)
                        # End span with context management
                    self.tracing_manager.end_span_with_context(span)
                self._root_span = None
                self._root_context = None

            except Exception as e:
                logger.warning("Warning: Failed to set span attributes in crew_failed event")

        # ============================================================================
        # AGENT EVENTS
        # ============================================================================

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_started(source, event):
            """Called when an Agent starts executing a task"""
            try:
                agent_data = getattr(event, 'agent', None)
                agent_name = getattr(agent_data, 'role', '') if agent_data else ''
                span_name = f"Agent: {agent_name}"

                # Create span with context management
                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.INVOKE_AGENT,
                    system=GenAISystem.FLOTORCH,
                    agent_name=agent_name,
                    output_type=GenAIOutputType.TEXT.value
                )

                if span:
                    try:
                        span_id = span.get_span_context().span_id
                        if self.tracing_manager.should_log_span(span):
                            logger.info(f"TRACES: 🔧 Agent: {agent_name} [SPAN_ID: {span_id:016x}]")
                    except Exception as e:
                        pass
                    # Add comprehensive spec.ts compliant attributes
                    self._add_span_attributes(span, {
                        # Core GenAI agent attributes from spec.ts
                        "gen_ai.agent.name": agent_name,
                        "gen_ai.agent.id": str(getattr(agent_data, 'id', '')) if agent_data and getattr(agent_data, 'id', None) else None,
                        "gen_ai.agent.description": getattr(agent_data, 'goal', '') if agent_data else '',
                        "gen_ai.agent.goal": getattr(agent_data, 'goal', '') if agent_data else '',
                        "gen_ai.conversation.id": str(getattr(event, 'conversation_id', '')) if getattr(event, 'conversation_id', None) else None,
                        "gen_ai.output.type": GenAIOutputType.TEXT.value,
                        "gen_ai.token.type": "tokens",
                    })

            except Exception as e:
                logger.warning("Warning: Failed to set span attributes in agent_started event")

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_completed(source, event):
            """Called when an Agent completes executing a task"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                    # Add completion attributes
                    self._add_span_attributes(span, {
                        "gen_ai.response.success": True,
                        "gen_ai.output.type": GenAIOutputType.TEXT.value,
                    })
                    span.set_status(StatusCode.OK)
                    # End span with context management
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.warning("Warning: Failed to set span attributes in agent_completed event")

        # ============================================================================
        # TASK EVENTS
        # ============================================================================

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event):
            """Called when a Task starts execution"""
            try:
                task_data = getattr(event, 'task', None)
                task_name = getattr(task_data, 'name', '') if task_data else ''
                task_name = task_name or ''

                task_description = getattr(task_data, 'description', '') if task_data else ''
                span_name = f"Task: {task_name}"

                # Create span with context management
                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.CHAT,
                    system=GenAISystem.FLOTORCH,
                    output_type=GenAIOutputType.TEXT.value
                )

                if span:
                    try:
                        span_id = span.get_span_context().span_id
                        if self.tracing_manager.should_log_span(span):
                            logger.info(f"TRACES: 🔧 Task: {task_name} [SPAN_ID: {span_id:016x}]")
                    except Exception as e:
                        logger.warning("Warning: Failed to get span context")
                    # Add comprehensive spec.ts compliant attributes
                    self._add_span_attributes(span, {
                        # Core GenAI attributes
                        "gen_ai.conversation.id": str(getattr(event, 'conversation_id', '')) if getattr(event, 'conversation_id', None) else None,
                        "gen_ai.output.type": GenAIOutputType.TEXT.value,
                        "gen_ai.task.name": task_name,  # Actual task name
                        "gen_ai.task.description": task_description,  # Task description
                        "gen_ai.task.id": str(getattr(task_data, 'id', '')) if task_data and getattr(task_data, 'id', None) else None,
                    })

            except Exception as e:
                logger.error(Error(operation="Error in task_started event", error=e))

        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            """Called when a Task completes execution"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                    # Add completion attributes
                    self._add_span_attributes(span, {
                            "gen_ai.response.success": True,
                            "gen_ai.output.type": GenAIOutputType.TEXT.value,
                    })
                    span.set_status(StatusCode.OK)
                    # End span with context management
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in task_completed event", error=e))

        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event):
            """Called when a Task fails to complete execution"""
            # Get span from context vars
            span = self.tracing_manager.get_current_span_from_context()

            if span:
                error_message = str(getattr(event, 'error', ''))

                # Add failure attributes
                self._add_span_attributes(span, {
                    "gen_ai.response.success": False,
                    "gen_ai.error.type": "task_execution_error",
                    "gen_ai.error.message": error_message[:1000]
                })
                span.set_status(StatusCode.ERROR)

                # End span with context management
                self.tracing_manager.end_span_with_context(span)

        # ============================================================================
        # TOOL USAGE EVENTS
        # ============================================================================

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_started(source, event):
            """Called when a tool execution is started"""
            try:
                tool_name = getattr(event, 'tool_name', '')
                tool_class = getattr(event, 'tool_class', '')
                tool_args = getattr(event, 'tool_args', '')

                # Parse tool_args if it's a JSON string
                try:
                    import json
                    tool_input = json.loads(tool_args) if tool_args else {}
                except:
                    tool_input = tool_args
                # Create tool span using context management
                span_name = f"Tool: {tool_name}"
                span = self.tracing_manager.start_span_with_context(span_name)
                if span:
                        try:
                            span_id = span.get_span_context().span_id
                            if self.tracing_manager.should_log_span(span):
                                logger.info(f"TRACES: 🔧 Tool: {tool_name} [SPAN_ID: {span_id:016x}]")
                        except Exception as e:
                            pass
                        # Set tool-specific attributes
                        self._add_span_attributes(span, {
                            "gen_ai.operation.name": "execute_tool",
                            "gen_ai.system": GEN_AI_SYSTEM_FLOTORCH,
                            "gen_ai.tool.name": tool_name,
                            "gen_ai.tool.type": "function",
                            "gen_ai.tool.description": tool_class,
                            "gen_ai.output.type": "text",
                            "gen_ai.token.type": "tokens",
                            "gen_ai.conversation.id": str(getattr(event, 'conversation_id', '')) if getattr(event, 'conversation_id', None) else None,
                            "gen_ai.tool.args": str(tool_args) if tool_args else None,
                            "gen_ai.tool.args_length": len(str(tool_args)) if tool_args else 0
                        })

            except Exception as e:
                logger.error(Error(operation="Error in tool_started event",error=e))

        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_finished(source, event):
            """Called when a tool execution is finished"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                        tool_output = getattr(event, 'output', '')

                        # Determine output type dynamically
                        output_type = str(type(tool_output)).lower()

                        # Add tool output attributes
                        self._add_span_attributes(span, {
                            "gen_ai.tool.response": str(tool_output),
                            "gen_ai.tool.response_length": len(str(tool_output)),
                            "gen_ai.response.success": True,
                            "gen_ai.output.type": output_type
                        })
                        span.set_status(StatusCode.OK)
                        # End span with context management
                        self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in tool_finished event", error=e))

        @crewai_event_bus.on(ToolUsageErrorEvent)
        def on_tool_error(source, event):
            """Called when a tool execution encounters an error"""
            try:
                # Get span from context vars
                span = self.tracing_manager.get_current_span_from_context()

                if span:
                        error_message = str(getattr(event, 'error', ''))

                        # Add error attributes
                        self._add_span_attributes(span, {
                            "gen_ai.response.success": False,
                            "gen_ai.output.type": "text",
                            "gen_ai.error.type": "tool_execution_error",
                            "gen_ai.error.message": error_message[:1000]
                        })

                        # Set span status to error
                        try:
                            span.set_status(Status(StatusCode.ERROR, error_message))
                        except Exception:
                            pass

                        # End span with context management
                        self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in tool_error event", error=e))

        # ============================================================================
        # LLM EVENTS
        # ============================================================================

        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_started(source, event):
            """Called when an LLM call starts"""
            # Only enable CrewAI framework-level LLM tracing when plugins_llm_tracing is enabled
            # When disabled, LLM calls are traced at SDK level (FlotorchLLM)
            if not self.tracing_manager.config.enable_plugins_llm_tracing:
                return

            model_name = getattr(event, 'model', None)
            # Fallback to call_id if no model name
            if not model_name:
                call_id = getattr(event, 'call_id', None)
                model_name = call_id if call_id else "unknown_model"

            span_name = f"llm:{model_name}"

            # Create span with context management
            span = self._create_custom_span(
                span_name=span_name,
                operation=GenAIOperationName.CHAT,
                system=GenAISystem.FLOTORCH,
                model=model_name,
                output_type=GenAIOutputType.TEXT.value
            )

            # if span:
            #     # Add comprehensive spec.ts compliant attributes
            #     self._add_span_attributes(span, {
            #         # Core GenAI LLM attributes from spec.ts
            #         "gen_ai.request.model": model_name,
            #         "gen_ai.conversation.id": str(getattr(event, 'conversation_id', '')) if getattr(event, 'conversation_id', None) else None,
            #         "gen_ai.output.type": GenAIOutputType.TEXT.value,

            #         # Request parameters
            #         "gen_ai.request.temperature": getattr(event, 'temperature', None),
            #         "gen_ai.request.max_tokens": getattr(event, 'max_tokens', None),
            #         "gen_ai.request.top_p": getattr(event, 'top_p', None),

            #         # CrewAI-specific attributes
            #     })

            # Add prompt as user message event if available
            # prompt = getattr(event, 'prompt', '')
            # if prompt:
            #     self.tracing_manager.add_user_message_event(
            #         span, str(prompt), message_index=0
            #     )

        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_completed(source, event):
            """Called when an LLM call completes"""
            # Only enable CrewAI framework-level LLM tracing when plugins_llm_tracing is enabled
            # When disabled, LLM calls are traced at SDK level (FlotorchLLM)
            if not self.tracing_manager.config.enable_plugins_llm_tracing:
                return

            # Get span from context vars
            span = self.tracing_manager.get_current_span_from_context()

            if span:
                model_name = getattr(event, 'model', 'unknown')

                # Add completion attributes
                self._add_span_attributes(span, {
                    "gen_ai.response.success": True,
                    "gen_ai.response.model": model_name,
                    "gen_ai.response.id": getattr(event, 'response_id', None),
                    "gen_ai.response.finish_reasons": getattr(event, 'finish_reasons', None),

                    # Usage metrics
                    "gen_ai.usage.input_tokens": getattr(event, 'input_tokens', None),
                    "gen_ai.usage.output_tokens": getattr(event, 'output_tokens', None),
                    "gen_ai.token.type": "input" if getattr(event, 'input_tokens', None) else None,

                })

                # Add response as assistant message event
                response = getattr(event, 'response', '')
                if response:
                    response_str = str(response)
                    self._add_span_attributes(span, {
                        "crewai.llm.response_length": len(response_str)
                    })

                    # Add full response as event
                    self.tracing_manager.add_assistant_message_event(
                        span, response_str, message_index=0
                    )
                span.set_status(StatusCode.OK)
                # Print span ID for completion (ADK-style)
                try:
                    span_id = span.get_span_context().span_id
                    if self.tracing_manager.should_log_span(span):
                        logger.info(f"TRACES: 🔧 LLM: {model_name} [SPAN_ID: {span_id:016x}]")
                except Exception as e:
                    pass

                # End span with context management
                self.tracing_manager.end_span_with_context(span)

        @crewai_event_bus.on(LLMCallFailedEvent)
        def on_llm_failed(source, event):
            """Called when an LLM call fails"""
            # Only enable CrewAI framework-level LLM tracing when plugins_llm_tracing is enabled
            # When disabled, LLM calls are traced at SDK level (FlotorchLLM)
            if not self.tracing_manager.config.enable_plugins_llm_tracing:
                return

            # Get span from context vars
            span = self.tracing_manager.get_current_span_from_context()

            if span:
                error_message = str(getattr(event, 'error', ''))

                # Add failure attributes
                self._add_span_attributes(span, {
                    "gen_ai.response.success": False,
                    "gen_ai.error.type": "llm_call_error",
                    "gen_ai.error.message": error_message[:1000],
                })
                span.set_status(StatusCode.ERROR)

                # End span with context management
                self.tracing_manager.end_span_with_context(span)

        # ============================================================================
        # MEMORY EVENTS
        # ============================================================================

        @crewai_event_bus.on(MemoryQueryStartedEvent)
        def on_memory_query_started(source, event):
            """Called when a memory query begins"""
            try:
                query = getattr(event, 'query', '')
                limit = getattr(event, 'limit', 0)
                score_threshold = getattr(event, 'score_threshold', 0.0)

                span_name = f"Memory Query: {query[:50]}{'...' if len(query) > 50 else ''}"

                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.CHAT,
                    system=GenAISystem.FLOTORCH
                )

                if span:
                    # Set memory-specific attributes
                    self._add_span_attributes(span, {
                        "gen_ai.operation.name": "memory",
                        "gen_ai.operation.type": "query",
                        "gen_ai.operation.system": GEN_AI_SYSTEM_FLOTORCH,
                        "gen_ai.memory.query.text": query,
                        "gen_ai.memory.query.limit": limit,
                    })

                    # Print memory query start
                    try:
                        span_context = span.get_span_context()
                        span_id = span_context.span_id
                        logger.info(f"TRACES: 🔧 Memory Query: {query[:30]}{'...' if len(query) > 30 else ''} [SPAN_ID: {span_id:016x}]")
                    except Exception as e:
                        pass

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_query_started", error=e))

        @crewai_event_bus.on(MemoryQueryCompletedEvent)
        def on_memory_query_completed(source, event):
            """Called when a memory query completes successfully"""
            try:
                span = self.tracing_manager.get_current_span_from_context()
                if span:
                    results = getattr(event, 'results', [])
                    query_time_ms = getattr(event, 'query_time_ms', 0)

                    # Update span attributes
                    self._add_span_attributes(span, {
                        "gen_ai.memory.query.success": True,
                        "gen_ai.memory.query.results_count": len(results)
                    })
                    span.set_status(StatusCode.OK)

                    # End span
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_query_completed", error=e))

        @crewai_event_bus.on(MemoryQueryFailedEvent)
        def on_memory_query_failed(source, event):
            """Called when a memory query fails"""
            try:
                span = self.tracing_manager.get_current_span_from_context()
                if span:
                    query = getattr(event, 'query', '')
                    error = getattr(event, 'error', '')

                    # Set error attributes
                    self._add_span_attributes(span, {
                        "gen_ai.memory.query.success": False,
                        "gen_ai.memory.query.error": str(error),
                        "gen_ai.error.message": str(error),
                    })

                    # Set span status to error

                    span.set_status(Status(StatusCode.ERROR, str(error)))

                    # End span
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_query_failed", error=e))

        @crewai_event_bus.on(MemorySaveStartedEvent)
        def on_memory_save_started(source, event):
            """Called when a memory save operation begins"""
            try:
                value = getattr(event, 'value', '')
                metadata = getattr(event, 'metadata', {})
                agent_role = getattr(event, 'agent_role', '')

                span_name = f"Memory Save: {agent_role}" if agent_role else "Memory Save"

                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.CHAT,
                    system=GenAISystem.FLOTORCH
                )

                if span:
                    # Set memory-specific attributes
                    self._add_span_attributes(span, {
                        "gen_ai.operation.name": "memory",
                        "gen_ai.operation.system": GEN_AI_SYSTEM_FLOTORCH,
                        "gen_ai.operation.type": "save",
                        "gen_ai.memory.save.value": value[:500] if value else '',  # Truncate for performance
                        "gen_ai.memory.save.agent_role": agent_role,
                        "gen_ai.memory.save.status": "started"
                    })

                    try:
                        span_context = span.get_span_context()
                        span_id = span_context.span_id
                        logger.info(f"TRACES: 🔧 Memory Save: {agent_role or 'Unknown'} [SPAN_ID: {span_id:016x}]")
                    except Exception as e:
                        pass

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_save_started", error=e))

        @crewai_event_bus.on(MemorySaveCompletedEvent)
        def on_memory_save_completed(source, event):
            """Called when a memory save operation completes successfully"""
            try:
                span = self.tracing_manager.get_current_span_from_context()
                if span:
                    self._add_span_attributes(span, {
                        "gen_ai.memory.save.status": "completed"
                    })
                    span.set_status(StatusCode.OK)
                    # End span
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_save_completed", error=e))

        @crewai_event_bus.on(MemorySaveFailedEvent)
        def on_memory_save_failed(source, event):
            """Called when a memory save operation fails"""
            try:
                span = self.tracing_manager.get_current_span_from_context()
                if span:
                    agent_role = getattr(event, 'agent_role', '')
                    error = getattr(event, 'error', '')

                    # Set error attributes
                    self._add_span_attributes(span, {
                        "gen_ai.memory.save.status": "failed",
                        "gen_ai.memory.save.error": str(error),
                        "gen_ai.error.message": str(error),
                        "gen_ai.error.type": "MemorySaveError"
                    })

                    # Set span status to error
                    span.set_status(Status(StatusCode.ERROR, str(error)))

                    # End span
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_save_failed", error=e))

        @crewai_event_bus.on(MemoryRetrievalStartedEvent)
        def on_memory_retrieval_started(source, event):
            """Called when memory retrieval for a task prompt starts"""
            try:
                task_id_raw = getattr(event, 'task_id', '')
                task_id = str(task_id_raw) if task_id_raw else ''

                span_name = f"Memory Retrieval: {task_id}" if task_id else "Memory Retrieval"

                span = self._create_custom_span(
                    span_name=span_name,
                    operation=GenAIOperationName.CHAT,
                    system=GenAISystem.FLOTORCH
                )

                if span:
                    # Set memory-specific attributes
                    self._add_span_attributes(span, {
                        "gen_ai.operation.name": "memory",
                        "gen_ai.operation.system": GEN_AI_SYSTEM_FLOTORCH,
                        "gen_ai.operation.type": "retrieval",
                        "gen_ai.memory.retrieval.task_id": task_id,
                        "gen_ai.memory.retrieval.status": "started"
                    })

                    # Print memory retrieval start
                    try:
                        span_context = span.get_span_context()
                        span_id = span_context.span_id
                        logger.info(f"TRACES: 🔧 Memory Retrieval: {task_id or 'Unknown'} [SPAN_ID: {span_id:016x}]")
                    except Exception as e:
                        pass

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_retrieval_started", error=e))

        @crewai_event_bus.on(MemoryRetrievalCompletedEvent)
        def on_memory_retrieval_completed(source, event):
            """Called when memory retrieval completes successfully"""
            try:
                span = self.tracing_manager.get_current_span_from_context()
                if span:
                    # Update span attributes
                    self._add_span_attributes(span, {
                        "gen_ai.memory.retrieval.status": "completed"
                    })
                    span.set_status(StatusCode.OK)
                    # End span
                    self.tracing_manager.end_span_with_context(span)

            except Exception as e:
                logger.error(Error(operation="Error in on_memory_retrieval_completed", error=e))

