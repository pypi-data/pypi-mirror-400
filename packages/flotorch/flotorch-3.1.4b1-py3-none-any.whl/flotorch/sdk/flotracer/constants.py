"""
OpenTelemetry GenAI Constants for FloTorch Gateway

This module contains constants used in OpenTelemetry GenAI tracing,
following the official semantic conventions.
Reference: https://opentelemetry.io/docs/specs/semconv/gen-ai/
"""

# ============================================================================
# GENAI SYSTEMS
# ============================================================================

GEN_AI_SYSTEM_FLOTORCH = "flotorch"

# ============================================================================
# MESSAGE ROLES
# ============================================================================

MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_ASSISTANT = "assistant"
MESSAGE_ROLE_TOOL = "tool"
MESSAGE_ROLE_SYSTEM = "system"

# ============================================================================
# EVENT TYPES
# ============================================================================

EVENT_TYPE_USER_MESSAGE = "gen_ai.user.message"
EVENT_TYPE_ASSISTANT_MESSAGE = "gen_ai.assistant.message"
EVENT_TYPE_TOOL_MESSAGE = "gen_ai.tool.message"
EVENT_TYPE_SYSTEM_MESSAGE = "gen_ai.system.message"
EVENT_TYPE_CHOICE = "gen_ai.choice"

# ============================================================================
# ATTRIBUTE KEYS (just the ones we're using)
# ============================================================================

GEN_AI_SYSTEM = "gen_ai.system"
MESSAGE_INDEX = "message.index"
MESSAGE_ROLE = "message.role"
MESSAGE_CONTENT = "message.content"
MESSAGE_TOOL_CALLS = "message.tool_calls"
CHOICE_INDEX = "choice.index"
CHOICE_FINISH_REASON = "choice.finish_reason"
TOOL_CALL_ID = "tool.call.id"

# ============================================================================
# ROLES
# ============================================================================

USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"
TOOL_ROLE = "tool"
SYSTEM_ROLE = "system"

# ============================================================================
# ROLE TO EVENT TYPE MAPPING
# ============================================================================

ROLE_TO_EVENT_TYPE_MAPPING = {
    MESSAGE_ROLE_USER: EVENT_TYPE_USER_MESSAGE,
    MESSAGE_ROLE_ASSISTANT: EVENT_TYPE_ASSISTANT_MESSAGE,
    MESSAGE_ROLE_TOOL: EVENT_TYPE_TOOL_MESSAGE,
    MESSAGE_ROLE_SYSTEM: EVENT_TYPE_SYSTEM_MESSAGE
}


# Attribute keys
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_REQUEST_MESSAGE_COUNT = "gen_ai.request.message_count"
GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature"
GEN_AI_REQUEST_TOP_P = "gen_ai.request.top_p"
GEN_AI_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens"
GEN_AI_REQUEST_STOP_SEQUENCES = "gen_ai.request.stop_sequences"
GEN_AI_REQUEST_TOOLS_COUNT = "gen_ai.request.tools_count"
GEN_AI_REQUEST_TOOLS = "gen_ai.request.tools"

GEN_AI_RESPONSE_MODEL = "gen_ai.response.model"
GEN_AI_RESPONSE_SUCCESS = "gen_ai.response.success"
GEN_AI_RESPONSE_ID = "gen_ai.response.id"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"
GEN_AI_RESPONSE_CONTENT_LENGTH = "gen_ai.response.content_length"
GEN_AI_RESPONSE_CONTENT = "gen_ai.response.content"

GEN_AI_CONVERSATION_ID = "gen_ai.conversation.id"
GEN_AI_REQUEST_CHOICE_COUNT = "gen_ai.request.choice.count"
GEN_AI_TOKEN_TYPE = "gen_ai.token.type"
GEN_AI_OUTPUT_TYPE = "gen_ai.output.type"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens"

# Additional GenAI Core Attributes
GEN_AI_REQUEST_SEED = "gen_ai.request.seed"
GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons"

# Values
GEN_AI_SYSTEM_FLOTORCH = "flotorch"
GEN_AI_OPERATION_CHAT = "chat"
GEN_AI_OUTPUT_TYPE_TEXT = "text"
GEN_AI_TOKEN_TYPE_TOKENS = "tokens"

# Event attribute keys already used in your code
MESSAGE_INDEX = "message.index"
MESSAGE_ROLE = "message.role"
MESSAGE_CONTENT = "message.content"
MESSAGE_TOOL_CALLS = "message.tool_calls"
CHOICE_INDEX = "choice.index"
CHOICE_FINISH_REASON = "choice.finish_reason"
TOOL_CALL_ID = "tool.call.id"

# Event types (names)
EVENT_TYPE_USER_MESSAGE = "gen_ai.user.message"
EVENT_TYPE_ASSISTANT_MESSAGE = "gen_ai.assistant.message"
EVENT_TYPE_TOOL_MESSAGE = "gen_ai.tool.message"
EVENT_TYPE_SYSTEM_MESSAGE = "gen_ai.system.message"
EVENT_TYPE_CHOICE = "gen_ai.choice"

# Roles
MESSAGE_ROLE_USER = "user"
MESSAGE_ROLE_ASSISTANT = "assistant"
MESSAGE_ROLE_TOOL = "tool"
MESSAGE_ROLE_SYSTEM = "system"

GEN_AI_AGENT_NAME = "gen_ai.agent.name"
GEN_AI_USER_ID = "gen_ai.user.id"


# LOG

LOG_ERROR = "error"
LOG_WARNING = "warning"
LOG_INFO = "info"