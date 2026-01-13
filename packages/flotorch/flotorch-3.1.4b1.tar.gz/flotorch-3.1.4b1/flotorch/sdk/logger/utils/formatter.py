
import json
from typing import Optional, List, Dict,Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class LogsFormatter:
    
    @staticmethod
    def object_creation(details):
        extras = details.extras or {}
        if extras:
            params_str = ", ".join(f"{k}={v}" for k, v in extras.items())
        else:
            params_str = "no parameters"
        return f"{details.class_name} initialized with ({params_str})"
    
    @staticmethod
    def error(details):  
        operation = details.operation
        try:
            error_name = type(details.error).__name__
            error = str(details.error)
        except: 
            error_name = ''
            error = ''
        return (
            f"operation: {operation} |"
            f" type: {error_name} |"
            f" message: {error}"
               )
    
    @staticmethod
    def llm_request(details):
        """Return a human-readable summary of an LLM request."""

        messages: List[Dict[str, Any]] = details.messages or []

        user_query: Optional[str] = None
        system_prompt: Optional[str] = None
        last_assistant_idx: int = -1

        # Single pass: first system, latest user, last assistant
        for idx, msg in enumerate(messages):
            role = msg.get("role")

            if role == "system" and system_prompt is None:
                content = msg.get("content") or ""
                system_prompt = content if len(content) <= 200 else content[:200] + "..."

            if role == "user":
                content = msg.get("content") or ""
                user_query = content if len(content) <= 300 else content[:300] + "..."

            if role == "assistant":
                last_assistant_idx = idx

        tool_responses: List[str] = []
        last_tool_call_id_to_name: Dict[str, str] = {}

        # Map tool_call_id -> tool_name from the last assistant message (if any)
        if last_assistant_idx != -1:
            last_assistant_msg = messages[last_assistant_idx]
            tool_calls = last_assistant_msg.get("tool_calls") or []

            last_tool_call_id_to_name = {
                tc.get("id"): (tc.get("function") or {}).get("name")
                for tc in tool_calls
                if tc.get("id") and (tc.get("function") or {}).get("name")
            }

            # Collect matching tool responses after the last assistant message
            if last_tool_call_id_to_name:
                for msg in messages[last_assistant_idx + 1 :]:
                    if msg.get("role") != "tool":
                        continue

                    tool_call_id = msg.get("tool_call_id")
                    if tool_call_id not in last_tool_call_id_to_name:
                        continue

                    tool_name = (
                        last_tool_call_id_to_name.get(tool_call_id)
                        or msg.get("name")
                        or tool_call_id
                    )

                    tool_content = msg.get("content") or ""
                    if len(tool_content) > 200:
                        tool_content = tool_content[:200] + "..."

                    tool_responses.append(f"{tool_name}: {tool_content}")

        # Format tools info (from details.tools)
        tools_info = ""
        tool_names = [
            (tool.get("function") or {}).get("name", "unknown")
            for tool in (details.tools or [])
            if isinstance(tool.get("function"), dict)
        ]
        if tool_names:
            tools_info = f", tools=[{', '.join(tool_names)}]"

        # Build output lines
        lines: List[str] = [
            f"LLM Request ({details.request_type}) - model={details.model}, "
            f"messages_len={len(messages)}{tools_info}"
        ]
        if user_query:
            lines.append(f"User Query: {user_query}")

        for tool_response in tool_responses:
            lines.append(f"Tool Response: {tool_response}")

        if system_prompt:
            lines.append(f"System Prompt: {system_prompt}")

        return "\n".join(lines)
    
    
    @staticmethod
    def llm_response(details) -> str:
        """Return a human-readable summary of an LLM response."""

        lines: List[str] = []
        tool_call_previews: List[str] = []

        # Extract and format tool calls first
        if details.tool_calls:
            for tc in details.tool_calls:
                fn = tc.get("function") or {}
                tool_name = fn.get("name", "unknown")
                tool_args = fn.get("arguments", "")

                # Safe parse of tool arguments
                parsed_args: Optional[Dict[str, Any]] = None
                if isinstance(tool_args, str):
                    try:
                        parsed_args = json.loads(tool_args)
                    except Exception:
                        parsed_args = None
                elif isinstance(tool_args, dict):
                    parsed_args = tool_args

                # Format arguments cleanly
                if isinstance(parsed_args, dict):
                    args_str = ", ".join(f"{k}={v}" for k, v in parsed_args.items())
                else:
                    args_str = str(tool_args)

                tool_call_previews.append(f"{tool_name}({args_str})")

        # Build usage info
        usage_info = ""
        if details.usage:
            usage_info = (
                f", tokens: {details.usage.get('total_tokens', 0)} "
                f"({details.usage.get('prompt_tokens', 0)}+"
                f"{details.usage.get('completion_tokens', 0)})"
            )
        
        # Add main response line
        tool_calls_info = f", tool_calls=[{', '.join(tool_call_previews)}]" if tool_call_previews else ""
        lines.append(
            f"LLM Response ({details.request_type}) - model={details.model}{tool_calls_info}{usage_info}"
        )
        
        # Add individual tool call lines (for yellow coloring)
        for tool_call_preview in tool_call_previews:
            lines.append(f"Tool Call: {tool_call_preview}")
        
        content = (details.content or "").strip()

        if not content:
            return "\n".join(lines)

        if details.is_final_response:
            # Always include full final response
            lines.append(f"Final Response: {content[:500] + '...' if len(content) > 500 else content}")
        else:
            # For non-final responses, only include content if meaningful
            if not details.tool_calls:
                preview = content if len(content) <= 300 else content[:300] + "..."
                lines.append(f"Response Content: {preview}")

        return "\n".join(lines)

    
    @staticmethod
    def session_operation(details) -> str:
        """
        Return a readable summary of a session operation,
        with sensitive params masked.
        """

        operation = details.operation
        session_uid = getattr(details, "session_uid", None)
        params = getattr(details, "params", {}) or {}

        # Mask sensitive parameters
        safe_params = {}
        for key, value in params.items():
            key_low = key.lower()
            if any(s in key_low for s in ("key", "token", "password", "secret")):
                safe_params[key] = "***"
            else:
                safe_params[key] = value

        # Build UID string
        uid_info = f" (uid={session_uid})" if session_uid else ""

        # Build param string
        params_info = f" - {safe_params}" if safe_params else ""

        return f"Session {operation.title()} ({details.request_type}) | {uid_info} | {params_info}"

        
    
    @staticmethod
    def memory_operation(details) -> str:
        """
        Return a readable summary of a memory operation,
        masking sensitive fields and summarizing large values.
        """

        operation = details.operation
        provider = details.provider
        memory_id = getattr(details, "memory_id", None)
        params = getattr(details, "params", {}) or {}

        safe_params = {}

        for key, value in params.items():
            key_low = key.lower()

            # Mask sensitive fields
            if any(s in key_low for s in ("key", "token", "password", "secret")):
                safe_params[key] = "***"
                continue

            # Summarize messages list
            if key == "messages" and isinstance(value, list):
                safe_params[key] = f"{len(value)} messages"
                continue

            # Truncate long strings
            if isinstance(value, str) and len(value) > 100:
                safe_params[key] = value[:100] + "..."
                continue

            # Default: keep original
            safe_params[key] = value

        # Build output parts cleanly
        parts = [f"Memory {operation.title()} ({details.request_type}) [provider: {provider}]"]

        if memory_id:
            parts.append(f"id={memory_id}")

        if safe_params:
            parts.append(f" - {safe_params}")

        return " | ".join(parts)

    
    @staticmethod
    def vectorstore_operation(details) -> str:
        """
        Return a readable summary of a VectorStore operation,
        masking sensitive parameters and truncating long query strings.
        """

        operation = details.operation
        vectorstore_id = details.vectorstore_id
        params = getattr(details, "params", {}) or {}

        safe_params = {}

        for key, value in params.items():
            key_low = key.lower()

            # Mask sensitive fields
            if any(s in key_low for s in ("key", "token", "password", "secret")):
                safe_params[key] = "***"
                continue

            # Truncate long query
            if key == "query" and isinstance(value, str) and len(value) > 100:
                safe_params[key] = value[:100] + "..."
                continue

            # Default
            safe_params[key] = value

        # Build final output components cleanly
        parts = [f"VectorStore {operation.title()} ({details.request_type}) [{vectorstore_id}]"]

        if safe_params:
            parts.append(f"params={safe_params}")

        return " | ".join(parts)

    
    
    @staticmethod
    def http_request(details) -> str:
        """
        Return a readable summary of an HTTP request,
        masking sensitive fields in query parameters.
        """

        method = details.method
        url = details.url
        status_code = getattr(details, "status_code", None)
        duration = getattr(details, "duration", None)

        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        safe_query = {}
        for key, values in query_params.items():
            key_low = key.lower()

            # Sensitive param masking
            if any(s in key_low for s in ("key", "token", "password", "secret")):
                safe_query[key] = ["***"]
            else:
                safe_query[key] = values

        # Reconstruct the masked URL
        masked_query = urlencode(safe_query, doseq=True)
        masked_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            masked_query,
            parsed.fragment
        ))

        parts = [f"HTTP {method.upper()} ({details.request_type}) {masked_url}"]

        if status_code is not None:
            parts.append(f"status={status_code}")

        if duration is not None:
            parts.append(f"duration={duration:.3f}s")

        return " | ".join(parts)