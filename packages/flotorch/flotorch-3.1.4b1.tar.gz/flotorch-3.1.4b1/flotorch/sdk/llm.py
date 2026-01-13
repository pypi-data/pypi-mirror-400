from typing import List, Dict, Tuple,Optional, Tuple, Union, Any

from flotorch.sdk.utils.llm_utils import invoke, async_invoke, parse_llm_response, LLMResponse
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import (
    Error, ObjectCreation, LLMRequest, LLMResponse
)
logger = get_logger()

# tracing
import json
from opentelemetry.trace import get_current_span, StatusCode
from flotorch.sdk.flotracer.manager import FloTorchTracingManager
from flotorch.sdk.flotracer.config import FloTorchFramework
from flotorch.sdk.utils.common_utils import initialize_tracing_manager, fetch_traces_from_api
from flotorch.sdk.flotracer.constants import *
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error


logger = get_logger()

class FlotorchLLM:
    def __init__(self, model_id: str, api_key: str, base_url: str, tracing_manager: Optional[FloTorchTracingManager] = None, tracer_config: Optional[Dict[str, Any]] = None):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.tracing_manager = tracing_manager
        # Initialize tracing if enabled at sdk level
        if not self.tracing_manager:
            self.tracing_manager = initialize_tracing_manager(
                base_url=base_url,
                api_key=api_key,
                tracer_config=tracer_config or {},
                framework=FloTorchFramework.FLOTORCH_SDK
            )
        # Log object creation
        logger.info(ObjectCreation(class_name="FlotorchLLM", extras={"baseurl":base_url,"model_id": model_id}))

    def _set_llm_request_attributes(self, span, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, **kwargs):
        """Set common LLM request attributes on a span."""
        # Safety check: ensure span is recording
        try:
            if not span or not span.is_recording():
                return
            request_attrs = {
                # Core GenAI attributes (required)
                GEN_AI_SYSTEM: GEN_AI_SYSTEM_FLOTORCH,
                GEN_AI_OPERATION_NAME: GEN_AI_OPERATION_CHAT,
                GEN_AI_REQUEST_MODEL: self.model_id,
                GEN_AI_TOKEN_TYPE: GEN_AI_TOKEN_TYPE_TOKENS,
                
                # Request context
                GEN_AI_REQUEST_MESSAGE_COUNT: len(messages or []),
            }
            span.set_attributes(request_attrs)
            
            # REQUEST PARAMETERS (GenAI Core Attributes)
            request_params = {}
            if 'temperature' in kwargs:
                request_params["gen_ai.request.temperature"] = kwargs['temperature']
            if 'max_tokens' in kwargs:
                request_params["gen_ai.request.max_tokens"] = kwargs['max_tokens']
            if 'top_p' in kwargs:
                request_params["gen_ai.request.top_p"] = kwargs['top_p']
            if 'top_k' in kwargs:
                request_params["gen_ai.request.top_k"] = kwargs['top_k']
            if 'frequency_penalty' in kwargs:
                request_params["gen_ai.request.frequency_penalty"] = kwargs['frequency_penalty']
            if 'presence_penalty' in kwargs:
                request_params["gen_ai.request.presence_penalty"] = kwargs['presence_penalty']
            if 'stop' in kwargs:
                request_params["gen_ai.request.stop_sequences"] = str(kwargs['stop'])
            if 'seed' in kwargs:
                request_params["gen_ai.request.seed"] = kwargs['seed']
            
            if request_params:
                span.set_attributes(request_params)
            
            self._add_llm_events(span, messages, "message")
            if tools:
                span.set_attribute("gen_ai.request.tools_count", len(tools))
                span.set_attribute("gen_ai.request.tools", str(tools))
        except Exception as e:
            logger.error(Error(operation="Warning: Failed to set LLM attributes", error=e))

    def _set_llm_response_attributes(self, span, parsed_response):
        """Set common LLM response attributes on a span."""
        # Safety check: ensure span is recording
        if not span or not span.is_recording():
            return

        metadata = parsed_response.metadata
        raw_response = metadata.get('raw_response', {})
        choices = raw_response.get('choices', [])

        response_attrs = {
            # Core GenAI attributes (required)
            GEN_AI_RESPONSE_MODEL: raw_response.get('model', self.model_id),
            GEN_AI_RESPONSE_SUCCESS: True,
            GEN_AI_RESPONSE_ID: raw_response.get('id', ''),
            GEN_AI_OUTPUT_TYPE: GEN_AI_OUTPUT_TYPE_TEXT,
            GEN_AI_TOKEN_TYPE: GEN_AI_TOKEN_TYPE_TOKENS,
            
            # Response context
            GEN_AI_CONVERSATION_ID: metadata.get('sessionUid', ''),
            GEN_AI_REQUEST_CHOICE_COUNT: len(choices),
        }
        finish_reasons = []
        for choice in choices:
            f_reason = choice.get('finish_reason')
            if f_reason:
                finish_reasons.append(f_reason)
        response_attrs[GEN_AI_RESPONSE_FINISH_REASONS] = finish_reasons
        
        # Add response content
        parsed_resp_content = parsed_response.content
        # Add events
        self._add_llm_events(span, choices, "choice")
        
        # TOKEN USAGE ATTRIBUTES (GenAI Core Attributes)
        response_attrs[GEN_AI_USAGE_INPUT_TOKENS] = metadata.get('inputTokens')
        response_attrs[GEN_AI_USAGE_OUTPUT_TOKENS] = metadata.get('outputTokens')
        response_attrs[GEN_AI_USAGE_TOTAL_TOKENS] = metadata.get('totalTokens')

        span.set_attributes(response_attrs)
        span.set_status(StatusCode.OK)

    def _create_context_aware_span(self, span_name):
        """Create LLM span for CrewAI context."""
        try:
            custom_span = self.tracing_manager.start_span_with_context(span_name)
            return custom_span
        except Exception as e:
            logger.error(Error(operation="Failed to create context-aware span", error=e))
        return None

    def _get_or_create_current_span(self, span_name):
        """Get current span or create a new one if needed."""
        # Check if we're in CrewAI context
        if self.tracing_manager and self.tracing_manager.framework in [
            FloTorchFramework.FLOTORCH_CREWAI, 
            FloTorchFramework.FLOTORCH_SDK
        ]:
            return self._create_context_aware_span(span_name)
        elif self.tracing_manager and self.tracing_manager.framework == FloTorchFramework.FLOTORCH_ADK:
            # below code is for adk tracing
            current_span = get_current_span()
            # If we're in framework context (there's already a span), use it
            if current_span and current_span.is_recording():
                try:
                    self.tracing_manager.update_mapping_callback(current_span)
                except Exception:
                    pass
                return current_span
        
        return None

    def _log_tracing_details(self, current_span):
        """Log tracing details."""
        try:
            span_context = current_span.get_span_context()
            span_id = span_context.span_id
            # Check if we're in SDK context for trace ID printing
            if self.tracing_manager.framework == FloTorchFramework.FLOTORCH_SDK:
                trace_id = span_context.trace_id
                if trace_id not in self.tracing_manager.tracer_ids:
                    self.tracing_manager.tracer_ids.add(trace_id)
                if self.tracing_manager.should_log_span(current_span):
                    logger.info("TRACES: =========START=========")
                    logger.info(f"TRACES: 🔧 LLM: {self.model_id} [TRACE_ID: {trace_id:016x}]")
                    logger.info(f"TRACES: 🔧 LLM: {self.model_id} [SPAN_ID: {span_id:016x}]")
                    logger.info("TRACES: =========END=========")
                    logger.info(f"👀 View here on HTTP GET request:\n{self.base_url}/v1/traces/{trace_id:016x}\n🔑 access code: Your API Key")
            else:
                if self.tracing_manager.should_log_span(current_span):
                    logger.info(f"TRACES: 🔧 LLM: {self.model_id} [SPAN_ID: {span_id:016x}]")
        except Exception as e:
            pass

    def _should_trace(self) -> bool:
        """Check if tracing should be performed."""
        try:
            return self.tracing_manager.config.enabled
        except Exception as e:
            return False
    
    def invoke(
        self,
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None, 
        response_format=None, 
        extra_body: Optional[Dict] = None, 
        **kwargs
    ) -> Union[LLMResponse, Tuple[LLMResponse, Any]]:

        #log llm_request
        logger.info(
                LLMRequest(model=self.model_id, messages=messages, tools=tools)
            )
        try:
            if self._should_trace():
                current_span = self._get_or_create_current_span(f"call_llm: {self.model_id}")
                if current_span and current_span.is_recording():
                    self._set_llm_request_attributes(current_span, messages, tools, **kwargs)
            # Extract return_headers before passing to invoke
            return_headers = kwargs.pop('return_headers', False)
            response = invoke(messages, self.model_id, self.api_key, self.base_url, tools=tools, response_format=response_format, extra_body=extra_body, return_headers=return_headers, **kwargs)
            if return_headers:
                response_body, response_headers = response
            else:
                response_body = response

            # Log response details
            tool_calls = response_body.get('choices', [{}])[0].get('message', {}).get('tool_calls', [])
            usage = response_body.get('usage', {})

            # Determine if this is likely a final response (no tool calls and has content)
            parsed_response = parse_llm_response(response_body)
            if self._should_trace():
                self._set_llm_response_attributes(current_span, parsed_response)
                self._log_tracing_details(current_span)

            is_final_response = bool(not tool_calls and parsed_response.content.strip())
            logger.info(
                LLMResponse(
                    model=self.model_id,
                    content=parsed_response.content,
                    tool_calls=tool_calls,
                    usage=usage,
                    is_final_response=is_final_response,
                ))
            if self._should_trace():
                self.tracing_manager.end_span_with_context(current_span)
            
            if return_headers:
                return parsed_response, response_headers
            else:
                return parsed_response
        except Exception as e:
            logger.error(
                Error(operation="FlotorchLLM.invoke", error=e)
            )
            raise

    async def ainvoke(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, response_format=None, extra_body: Optional[Dict] = None, **kwargs) -> LLMResponse:
        """
        Invoke LLM with individual parameters instead of a complete payload.
        Creates the payload internally from the provided parameters.
        """
        # Log request details
        logger.info(
            LLMRequest(model=self.model_id, messages=messages, tools=tools, request_type='async')
        )
        try:
            # tracing related code
            if self._should_trace():
                current_span = self._get_or_create_current_span(f"call_llm: {self.model_id}")
                if current_span and current_span.is_recording():
                    self._set_llm_request_attributes(current_span, messages, tools, **kwargs)
            # Extract return_headers before passing to async_invoke
            return_headers = kwargs.pop('return_headers', False)
            # Use the utility function that handles payload creation
            response = await async_invoke(messages, self.model_id, self.api_key, self.base_url, tools=tools, response_format=response_format, extra_body=extra_body, **kwargs)
            if return_headers:
                response_body, response_headers = response
            else:
                response_body = response
            parsed_response = parse_llm_response(response_body)

            if self._should_trace():
                self._set_llm_response_attributes(current_span, parsed_response)
                self._log_tracing_details(current_span)

            # Log response details
            tool_calls = response_body.get('choices', [{}])[0].get('message', {}).get('tool_calls', [])
            usage = response_body.get('usage', {})
            
            # Determine if this is likely a final response (no tool calls and has content)
            is_final_response = bool(not tool_calls and parsed_response.content.strip())
            logger.info(
                LLMResponse(
                    model=self.model_id,
                    content=parsed_response.content,
                    tool_calls=tool_calls,
                    usage=usage,
                    is_final_response=is_final_response,
                    request_type='async',
                )
            )

            if self._should_trace():
                self.tracing_manager.end_span_with_context(current_span)
            if return_headers:
                return parsed_response, response_headers
            else:
                return parsed_response
        except Exception as e:
            logger.error(Error(operation="FLotorchLLM.ainvoke", error=e))
            raise

    def _add_llm_events(self, span, data, event_type="message"):
        """Add LLM events to span with flexible event types for both request and response.
        
        Args:
            span: OpenTelemetry span
            data: List of items to create events for (messages, choices, etc.)
            event_type: Type of event ("message", "choice")
        """
        if not data:
            return None     
        try:
            if event_type == "message":
                last_message = data[-1]
                role = last_message.get('role', 'unknown')
                content = last_message.get('content', '')
                resp = {}
                base_attrs = {
                    GEN_AI_SYSTEM: GEN_AI_SYSTEM_FLOTORCH,
                    MESSAGE_INDEX: len(data) - 1,
                    MESSAGE_ROLE: role,
                    MESSAGE_CONTENT: content[:1000] if content else ""
                }
                
                # Add role-specific attributes
                if role == MESSAGE_ROLE_ASSISTANT:
                    tool_calls = last_message.get('tool_calls', [])
                    if tool_calls:
                        base_attrs[MESSAGE_TOOL_CALLS] = json.dumps(tool_calls)
                elif role == MESSAGE_ROLE_TOOL:
                    tool_call_id = last_message.get('tool_call_id', '')
                    base_attrs[TOOL_CALL_ID] = tool_call_id

                
                # Get event type and add event
                event_type_name = ROLE_TO_EVENT_TYPE_MAPPING.get(role, 'unknown')
                base_attrs["type"] = event_type_name
                self.tracing_manager.add_trace_event(
                    span,
                    f"event_{event_type_name}",
                    base_attrs
                )

            elif event_type == "choice":
                # Handle choice events (for response phase) - all choices
                for i, item in enumerate(data):
                    message = item.get('message', {})
                    role = message.get('role', '')
                    
                    choice_attrs = {
                        GEN_AI_SYSTEM: GEN_AI_SYSTEM_FLOTORCH,
                        CHOICE_INDEX: i,
                        CHOICE_FINISH_REASON: item.get('finish_reason', ''),
                        MESSAGE_ROLE: role
                    }
                    
                    # Add content if present
                    if 'content' in message and message['content']:
                        choice_attrs[MESSAGE_CONTENT] = message['content'][:1000]
                    
                    # Add tool calls if present
                    if 'tool_calls' in message and message['tool_calls']:
                        choice_attrs[MESSAGE_TOOL_CALLS] = json.dumps(message['tool_calls'])
                    choice_attrs["type"] = EVENT_TYPE_CHOICE
                    # Create choice event using constant
                    self.tracing_manager.add_trace_event(
                        span,
                        "event_choice",
                        choice_attrs
                    )
                    
        except Exception as e:
            logger.error(Error(operation=f"Failed to add events", error=e))

    def get_traces(self, tracer_ids: Union[set, list, str] = None) -> list[dict]:
        """
        Get traces from the API for the given tracer IDs.
        
        Args:
            tracer_ids: Single trace ID (str), list of trace IDs, or set of trace IDs or None
            
        Returns:
            List of trace dictionaries from the API
            
        Raises:
            ValueError: If base_url or api_key is not provided
        """
        results = fetch_traces_from_api(self.tracing_manager.tracer_ids,tracer_ids, self.base_url, self.api_key)
        
        return json.dumps(results, ensure_ascii=False)
