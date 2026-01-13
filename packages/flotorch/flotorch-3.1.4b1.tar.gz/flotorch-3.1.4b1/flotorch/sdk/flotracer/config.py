#!/usr/bin/env python3
"""
OpenTelemetry GenAI Semantic Conventions for FloTorch Gateway

This module implements the official OpenTelemetry semantic conventions for Generative AI systems.
Reference: https://opentelemetry.io/docs/specs/semconv/gen-ai/

The gateway acts as a generic proxy, so provider-specific attributes are generalized
while maintaining compatibility with the official conventions.

============================================================================
OPENTELEMETRY SPAN STRUCTURE
============================================================================

OpenTelemetry spans have two main components for storing data:

1. SPAN ATTRIBUTES (Key-Value Pairs)
   - Purpose: Store metadata and context about the span
   - Characteristics: Low cardinality, used for filtering/grouping/correlation
   - Examples: gen_ai.system, gen_ai.operation.name, gen_ai.request.model
   - Best Practice: Keep cardinality low, avoid sensitive data, use for metrics

2. SPAN EVENTS (Detailed Content)
   - Purpose: Store actual input/output content and detailed information
   - Characteristics: Can contain larger payloads, can store sensitive data
   - Examples: gen_ai.user.message, gen_ai.assistant.message, gen_ai.tool.message
   - Best Practice: Can be disabled for privacy/security, use for debugging

This separation allows for:
- Efficient querying via attributes
- Detailed analysis via events
- Privacy control by disabling event content
- Performance optimization by keeping attributes lightweight
"""

import os
import time
from urllib.parse import urljoin
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from contextvars import ContextVar

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHTTPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode, SpanKind

# Import OpenTelemetry built-in sampling
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

TRACING_ENDPOINT = "observability/v1/traces"
TRACING_ENABLED = False
TRACING_PROTOCOL = "https"
TRACING_LOG_LEVEL = "ERROR"
TRACING_SAMPLING_ENABLED = True
TRACING_SAMPLING_RATE = 0.02
TRACING_ENABLE_PLUGINS_LLM_TRACING = False
TRACING_SERVICE_NAME = "flotorch-gateway"
TRACING_SERVICE_VERSION = "1.0.0"


class FloTorchFramework(str, Enum):
    """FloTorch framework types"""
    FLOTORCH_ADK = "flotorch_adk"
    FLOTORCH_CREWAI = "flotorch_crewai"
    FLOTORCH_LANGGRAPH = "flotorch_langgraph"
    FLOTORCH_AUTOGEN = "flotorch_autogen"
    FLOTORCH_SDK = "flotorch_sdk"

class GenAISystem(str, Enum):
    """Well-known GenAI systems"""
    ANTHROPIC = "anthropic"
    AWS_BEDROCK = "aws.bedrock"
    FLOTORCH = "flotorch"  # Custom FloTorch system

class GenAIOperationName(str, Enum):
    """Well-known GenAI operation names"""
    CHAT = "chat"
    CREATE_AGENT = "create_agent"
    EMBEDDINGS = "embeddings"
    EXECUTE_TOOL = "execute_tool"
    GENERATE_CONTENT = "generate_content"
    INVOKE_AGENT = "invoke_agent"
    TEXT_COMPLETION = "text_completion"

class GenAIOutputType(str, Enum):
    """GenAI output types"""
    IMAGE = "image"
    JSON = "json"
    SPEECH = "speech"
    TEXT = "text"

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class TracingConfig:
    """Configuration for OpenTelemetry tracing with session management and sampling"""
    # Core tracing configuration
    enabled: bool = False
    endpoint: str = ""
    auth_token: str = ""
    protocol: str = "https"
    log_level: str = "ERROR"
    service_name: str = "flotorch-gateway"
    service_version: str = "1.0.0"
    insecure: bool = False
    timeout: int = 25
    sampling_enabled: bool = True
    sampling_rate: float = .02
    enable_plugins_llm_tracing: bool = False


# ============================================================================
# GENAI EVENT TYPES
# ============================================================================

class GenAIEventType(str, Enum):
    """GenAI event types"""
    USER_MESSAGE = "gen_ai.user.message"
    ASSISTANT_MESSAGE = "gen_ai.assistant.message"
    TOOL_MESSAGE = "gen_ai.tool.message"
    SYSTEM_MESSAGE = "gen_ai.system.message"
    CHOICE = "gen_ai.choice"


# ============================================================================
# CUSTOM SPAN PROCESSOR FOR CLEAN ERROR HANDLING
# ============================================================================

class CleanErrorSpanProcessor(BatchSpanProcessor):
    """Custom span processor that shows clean error messages for export failures"""
    
    def on_end(self, span):
        try:
            super().on_end(span)
        except Exception as e:
            print(f"⚠️  Tracing Export Failed: {type(e).__name__}")


# ============================================================================
# CUSTOM SPAN PROCESSOR FOR FILTERING
# ============================================================================

_parent_trace_ids = set()

def register_parent_trace_id(trace_id: str):
    """Register a parent trace ID for distributed tracing context."""
    _parent_trace_ids.add(trace_id)

def _get_scope_name(span) -> Optional[str]:
    """Helper to safely get scope name from span"""
    try:
        if hasattr(span, 'instrumentation_scope'):
            return getattr(span.instrumentation_scope, 'name', None)
    except Exception:
        pass
    return None

class FilteringSpanProcessor(CleanErrorSpanProcessor):
    """Custom span processor that filters out spans marked as non-exportable and shows clean error messages"""
    
    def on_end(self, span):
        """Override on_end to filter spans before processing"""
        if hasattr(span, 'attributes') and span.attributes:
            export_flag = span.attributes.get("flotorch.export")
            if export_flag is False:
                return
        
        try:
            span_context = span.get_span_context()
            trace_id = span_context.trace_id
            trace_id_hex = f"{trace_id:032x}"
            scope_name = _get_scope_name(span)
            
            if scope_name == "opentelemetry.instrumentation.httpx":
                if _parent_trace_ids and trace_id_hex not in _parent_trace_ids:
                    return
            
            if scope_name == "gcp.vertex.agent":
                if _parent_trace_ids and trace_id_hex not in _parent_trace_ids:
                    return
        except Exception:
            pass
        
        super().on_end(span)