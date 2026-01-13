import logging
import sys
import inspect
import os
from typing import Optional


FLOTORCH_LOGGER_NAME = "flotorch"


def str_to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


# ANSI color codes
_RESET = "\033[0m"
_COLOR_RED = "\033[31m"
_COLOR_YELLOW = "\033[33m"
_COLOR_CYAN = "\033[36m"
_COLOR_MAGENTA = "\033[35m"
_COLOR_GREEN = "\033[32m"
_COLOR_BLUE = "\033[34m"

# Try enabling Windows ANSI support (best-effort)
try:
    import colorama  # type: ignore

    colorama.just_fix_windows_console()
except Exception:
    pass


class _CategoryColorFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: Optional[str] = None, use_colors: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_colors = use_colors

    def _category_color(self, logger_name: str) -> str:
        if logger_name.startswith("flotorch.sdk.llm"):
            return _COLOR_CYAN
        if logger_name.startswith("flotorch.sdk.session"):
            return _COLOR_MAGENTA
        if logger_name.startswith("flotorch.sdk.memory") or logger_name.startswith(
            "flotorch.sdk.vector"
        ):
            return _COLOR_GREEN
        if logger_name.startswith("flotorch.sdk.utils.http_utils"):
            return _COLOR_BLUE
        return ""

    def _pick_color(self, record: logging.LogRecord, line: str) -> str:
        # Level-first: ERROR/WARNING override everything
        if record.levelno >= logging.ERROR:
            return _COLOR_RED
        if record.levelno >= logging.WARNING:
            return _COLOR_YELLOW

        # Special highlight for tool call/response/result
        if "Tool Call:" in line or "Tool Response:" in line or "[Tool Result:" in line:
            return _COLOR_YELLOW

        # INFO/DEBUG: category-based
        return self._category_color(record.name or "")

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        if not self.use_colors:
            return formatted

        # Only color if stdout is a TTY (avoid polluting file logs etc.)
        if not sys.stdout.isatty():
            return formatted

        if "\n" in formatted:
            lines = formatted.split("\n")
            colored_lines = []
            in_tool_response = False
            
            # Patterns that indicate the start of a new log section
            log_section_prefixes = (
                "LLM Request", "LLM Response", "User Query:", "System Prompt:",
                "Final Response:", "Response Content:", "Tool Call:", "Tool Response:",
                "Session", "Memory", "VectorStore", "HTTP"
            )
            
            for line in lines:
                # Check if this line starts a new log section
                starts_new_section = any(line.strip().startswith(prefix) for prefix in log_section_prefixes)
                
                # Check if this line contains tool response/result indicators
                has_tool_indicator = "Tool Response:" in line or "[Tool Result:" in line
                
                if has_tool_indicator:
                    in_tool_response = True
                    color = _COLOR_YELLOW
                # Check if we're still in a tool response block
                elif in_tool_response:
                    # If we hit a new log section, stop coloring tool response
                    if starts_new_section:
                        in_tool_response = False
                        color = self._pick_color(record, line)
                    else:
                        # Continue coloring as part of tool response
                        color = _COLOR_YELLOW
                else:
                    # Normal color picking
                    color = self._pick_color(record, line)
                
                if color:
                    colored_lines.append(f"{color}{line}{_RESET}")
                else:
                    colored_lines.append(line)
            return "\n".join(colored_lines)

        color = self._pick_color(record, formatted)
        if not color:
            return formatted

        return f"{color}{formatted}{_RESET}"


def _get_base_logger() -> logging.Logger:
    """
    Get the dedicated Flotorch logger, independent of user/root config.
    """
    logger = logging.getLogger(FLOTORCH_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    # Critical for independence: do NOT bubble up into root/user handlers
    logger.propagate = False
    return logger


def _suppress_external_noise() -> None:
    """
    Optional: tame very chatty third-party loggers that Flotorch uses internally.
    This *does* touch those loggers globally; remove if you want zero interference.
    """
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("google_adk").setLevel(logging.ERROR)
    logging.getLogger("google_adk.google.adk.tools.base_authenticated_tool").setLevel(
        logging.ERROR
    )
    # Configure logging to suppress AutoGen logs while keeping Flotorch logs
    logging.getLogger("autogen_core").setLevel(logging.WARNING)
    logging.getLogger("autogen_agentchat").setLevel(logging.WARNING)
    logging.getLogger("autogen_ext").setLevel(logging.WARNING)

    for name in ("litellm", "LiteLLM"):
        noisy_logger = logging.getLogger(name)
        noisy_logger.setLevel(logging.ERROR)
        noisy_logger.propagate = False


def configure_console_logger() -> logging.Logger:
    """
    Configure the Flotorch logger for console output only.
    This is independent of user/root configuration and other providers.
    """
    base_logger = _get_base_logger()

    # Remove any existing handlers (file, old console, etc.)
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        _CategoryColorFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    base_logger.addHandler(handler)

    _suppress_external_noise()
    return base_logger


# Backwards-compatible name if you were using configure_logger()
configure_logger = configure_console_logger


def configure_file_logger(log_file: str = "file.log") -> logging.Logger:
    """
    Configure the Flotorch logger for file output only (no console).
    Independent from user/root and other Flotorch providers.
    """
    base_logger = _get_base_logger()

    # Ensure directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    abs_log_file = os.path.abspath(log_file)

    # Remove all existing handlers (console or old file)
    for h in list(base_logger.handlers):
        base_logger.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass

    file_handler = logging.FileHandler(abs_log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    base_logger.addHandler(file_handler)

    _suppress_external_noise()
    return base_logger


def find_caller_module() -> str:
    """
    Find the module name of the actual caller by walking the call stack.

    Typical stack when using FlotorchLogger:
      - Frame 0: find_caller_module (here)
      - Frame 1: provider.log / wrapper
      - Frame 2: FlotorchLogger._log
      - Frame 3: FlotorchLogger.info/error/etc
      - Frame 4: Actual caller (e.g., flotorch.sdk.llm)
    """
    frame = inspect.currentframe()
    try:
        caller_frame = frame
        for _ in range(4):
            if caller_frame is None:
                return "unknown"
            caller_frame = caller_frame.f_back

        if caller_frame and hasattr(caller_frame, "f_globals"):
            module_name = caller_frame.f_globals.get("__name__", "unknown")
            if module_name:
                return module_name
    except Exception:
        pass
    finally:
        # Break reference cycle
        del frame

    return "unknown"
