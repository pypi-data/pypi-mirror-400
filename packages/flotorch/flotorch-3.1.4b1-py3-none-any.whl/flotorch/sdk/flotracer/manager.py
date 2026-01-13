# ============================================================================
# CORE TRACING MANAGER
# ============================================================================
import os
import json
import logging
from typing import Any, Dict, List, Optional
from contextvars import ContextVar

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHTTPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Span, SpanKind
from flotorch.sdk.flotracer.config import (
    TracingConfig,
    FloTorchFramework,
    GenAISystem,
    GenAIEventType,
    FilteringSpanProcessor,
    CleanErrorSpanProcessor
)
import flotorch.sdk.flotracer.config as TRACE_DEFAULTS
from flotorch.sdk.flotracer.constants import *
# Import OpenTelemetry built-in sampling
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import Error

logger = get_logger()

class FloTorchTracingManager:
    """Manages OpenTelemetry tracing for FloTorch Gateway"""
    
    def __init__(self, config: Dict[str, Any], framework: FloTorchFramework):
        self.config = self.tracer_config(config)
        self.agent_config = config
        self.update_mapping_callback = None  # Callback function for updating span mappings
        self.framework = framework  # Set framework directly
        # Context variable for managing span hierarchy
        self.current_span_var = ContextVar('flotorch_current_span', default=None)
        self.parent_span = None
        if self.config.enabled and self.config.endpoint:
            self._setup_sampler()
            self._setup_tracer()
            self.tracer_ids = set()
            self._instrument_httpx()

    def _instrument_httpx(self):
        """Instrument httpx client to propagate trace context to gateway"""
        try:
            HTTPXClientInstrumentor().instrument()
            logger.info("HTTPX instrumentation enabled for trace propagation")
        except Exception as e:
            logger.warning(f"Warning: Failed to instrument httpx: {e}")

    def set_mapping_callback(self, callback_func):
        """Set the callback function for updating span mappings"""
        self.update_mapping_callback = callback_func
    
    def _setup_sampler(self):
        """Initialize the sampling strategy using OpenTelemetry built-in sampler"""
        if self.config.sampling_enabled:
            try:
                # Use OpenTelemetry's built-in probabilistic sampler
                self.sampler = TraceIdRatioBased(self.config.sampling_rate)
            except Exception as e:
                logger.error(Error(operation="Warning: Failed to setup sampler", errror=e))
                self.sampler = None

    def add_trace_event(self, span: Span, name: str, attributes: Dict[str, Any] = None):
        """Add an event to a span"""
        if span and self.config.enabled:
            try:
                span.add_event(name, attributes or {})
            except Exception as e:
                logger.error(Error(operation="Warning: Failed to add event '{name}'",error=e))
    
    def _setup_tracer(self):
        """Initialize the OpenTelemetry tracer"""
        try:
            existing_provider = trace.get_tracer_provider()
            from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider
            
            if isinstance(existing_provider, SDKTracerProvider):
                provider = existing_provider
                logger.debug(f"Reusing existing TracerProvider for service '{self.config.service_name}'")
                self.tracer = trace.get_tracer(self.config.service_name)
                return
            else:
                resource = Resource.create({
                    "service.name": self.config.service_name,
                    "service.version": self.config.service_version,
                })
                
                provider = TracerProvider(resource=resource, sampler=self.sampler)
            
            # Create OTLP exporter with clock skew handling
            # Choose exporter based on protocol
            if self.config.protocol.lower() in ["https"]:
                # HTTP/HTTPS exporter
                if self.config.auth_token:
                    headers = {"Authorization": "Bearer " + self.config.auth_token}
                else:
                    headers = None
                exporter = OTLPHTTPSpanExporter(
                    endpoint=self.config.endpoint,
                    timeout=self.config.timeout,
                    headers=headers
                )
            else:
                # gRPC exporter (default)
                if self.config.auth_token:
                    # For gRPC, use lowercase metadata keys
                    headers = {"authorization": "Bearer " + self.config.auth_token}
                else:
                    headers = None
                
                exporter = OTLPSpanExporter(
                    endpoint=self.config.endpoint,
                    insecure=self.config.insecure,
                    timeout=self.config.timeout,
                    headers=headers
                )
            
            
            # Configure clock skew handling (suppress warnings if enabled)
            if self.config.log_level == "ERROR":
                logging.getLogger("opentelemetry.sdk.trace.export").setLevel(logging.ERROR)
                logging.getLogger("opentelemetry.sdk.trace").setLevel(logging.ERROR)
            
            # Use FilteringSpanProcessor for ADK context, CleanErrorSpanProcessor for others
            if self.framework == FloTorchFramework.FLOTORCH_ADK:
                span_processor = FilteringSpanProcessor(exporter)
            else:
                span_processor = CleanErrorSpanProcessor(exporter)
            
            if self.framework == FloTorchFramework.FLOTORCH_CREWAI:
                # This is to disable the default crewai tracer provider
                # this function is used to set the tracer provider only once
                # so we are overriding and when the set_tracer_provider is called
                # it will set the tracer provider to the one we are passing
                # If crewai updates this variable or function we need to update this code
                trace._TRACER_PROVIDER_SET_ONCE = trace.Once()
                
                # Disable CrewAI's native tracing system programmatically
                # This prevents CrewAI's TraceCollectionListener from being set up
                # which stops the "Execution Traces" prompts
                os.environ['CREWAI_TRACING_ENABLED'] = 'false'
            
            provider.add_span_processor(span_processor)
            # Set global tracer provider
            trace.set_tracer_provider(provider)
            logger.debug(f"Created and set new TracerProvider for service '{self.config.service_name}'")
            
            # Create tracer
            self.tracer = trace.get_tracer(self.config.service_name)
            
        except Exception as e:
            logger.error(Error(operation="Warning: Failed to setup tracing", error=e))
            self.tracer = None
    
    def create_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, **kwargs) -> Optional[Span]:
        """Create a new span"""
        if not self.tracer:
            return None
        
        try:
            return self.tracer.start_span(name, kind=kind, **kwargs)
        except Exception as e:
            logger.error(Error(operation="Warning: Failed to create span '{name}'", error=e))
            return None
    
    def add_event(self, span: Span, name: str, attributes: Dict[str, Any] = None):
        """Add an event to a span"""
        if span and self.config.enabled:
            try:
                span.add_event(name, attributes or {})
            except Exception as e:
                logger.error(Error(operation=f"Warning: Failed to add event '{name}'",error=e))
    
    def set_attributes(self, span: Span, attributes: Dict[str, Any]):
        """Set attributes on a span"""
        if span and self.config.enabled:
            try:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            except Exception as e:
                logger.error(Error(operation="Warning: Failed to set attributes", error=e))
    
    def add_user_message_event(self, span: Span, content: str, message_index: int = 0):
        """Add a user message event to a span"""
        if span and self.config.enabled:
            attributes = {
                "gen_ai.system": GenAISystem.FLOTORCH.value,
                "message.index": message_index,
                "message.role": "user",
                "message.content": content[:1000] if content else ""
            }
            self.add_event(span, GenAIEventType.USER_MESSAGE.value, attributes)
    
    def add_assistant_message_event(self, span: Span, content, message_index: int = 0, 
                                  tool_calls: List[Dict] = None):
        """Add an assistant message event to a span"""
        if span and self.config.enabled:
            # Handle both string and Content objects
            if hasattr(content, 'parts') and content.parts:
                # It's a Content object, extract text from parts
                content_text = content.parts[0].text if content.parts[0].text else ""
            elif isinstance(content, str):
                # It's already a string
                content_text = content
            else:
                # Fallback
                content_text = str(content) if content else ""
            
            attributes = {
                "gen_ai.system": GenAISystem.FLOTORCH.value,
                "message.index": message_index,
                "message.role": "assistant",
                "message.content": content_text[:1000] if content_text else "",
                "message.tool_calls": json.dumps(tool_calls) if tool_calls else ""
            }
            self.add_event(span, GenAIEventType.ASSISTANT_MESSAGE.value, attributes)
    
    def should_log_span(self, span: Span) -> bool:
        """Check if span info should be printed based on sampling decision"""
        if not span:
            return False
        
        span_context = span.get_span_context()
        return span_context.is_valid and span_context.trace_flags.sampled
    
    def start_span_with_context(self, name: str, **kwargs) -> Optional[Span]:
        """Start a new span with proper context management for hierarchy"""
        if not self.tracer:
            return None
        
        try:
            # Get current span from context
            parent_span = self.current_span_var.get()
            
            # Create context with parent span
            ctx = trace.set_span_in_context(parent_span) if parent_span else None
            
            # Start new span
            span = self.tracer.start_span(name, context=ctx, **kwargs)
            
            # Set new span in context
            token = self.current_span_var.set(span)
            
            # Store token for later cleanup
            span._flotorch_token = token
            
            return span
        except Exception as e:
            logger.error(Error(operation=f"Warning: Failed to start span '{name}'", error=e))
            return None
    
    def end_span_with_context(self, span: Span):
        """End span and restore previous context"""
        if span:
            try:
                # End the span
                span.end()
                
                # Restore previous context
                if hasattr(span, '_flotorch_token'):
                    self.current_span_var.reset(span._flotorch_token)
            except Exception as e:
                logger.warning(f"Warning: Failed to end span: {e}")
    
    def get_current_span_from_context(self) -> Optional[Span]:
        """Get current span from context variable or parent span (for distributed tracing)."""
        span = self.current_span_var.get()
        if span:
            return span
        return self.parent_span
    
    def force_flush(self, timeout_millis: int = 5000) -> bool:
        """
        Force flush all pending spans to the OTLP collector immediately.
        Returns True if flush succeeded, False otherwise.
        """
        try:
            from opentelemetry import trace
            provider = trace.get_tracer_provider()
            provider.force_flush(timeout_millis=timeout_millis)
        except Exception as e:
            logger.error(Error(operation="ERROR: Failed to force flush spans", error=e))

    def tracer_config(self, custom_tracer_config: Optional[Dict[str, Any]] = None) -> TracingConfig:
        """Create tracing configuration from environment variables"""
        resp = TracingConfig(
            enabled=custom_tracer_config.get("enabled", TRACE_DEFAULTS.TRACING_ENABLED),
            endpoint=custom_tracer_config.get("endpoint", ''),
            auth_token=custom_tracer_config.get("auth_token"),
            protocol=custom_tracer_config.get("protocol", TRACE_DEFAULTS.TRACING_PROTOCOL),
            service_name=custom_tracer_config.get("service_name", TRACE_DEFAULTS.TRACING_SERVICE_NAME),
            log_level=custom_tracer_config.get("log_level", TRACE_DEFAULTS.TRACING_LOG_LEVEL),
            enable_plugins_llm_tracing=custom_tracer_config.get("enable_plugins_llm_tracing", TRACE_DEFAULTS.TRACING_ENABLE_PLUGINS_LLM_TRACING),
            sampling_enabled=custom_tracer_config.get("sampling_enabled", TRACE_DEFAULTS.TRACING_SAMPLING_ENABLED),
            sampling_rate=custom_tracer_config.get("sampling_rate", TRACE_DEFAULTS.TRACING_SAMPLING_RATE),
        )
        return resp