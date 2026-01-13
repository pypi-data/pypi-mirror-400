import os
from typing import Optional

from .logger import FlotorchLogger
from .console_logger_provider import ConsoleLoggerProvider
from .file_logger_provider import FileLoggerProvider
from .utils.logger_utils import str_to_bool
from dotenv import load_dotenv

load_dotenv()

def _resolve_debug(debug: Optional[bool]) -> bool:
    """
    Resolve debug flag with precedence:
    1. explicit arg
    2. env var FLOTORCH_LOG_DEBUG
    3. default False
    """
    if debug is not None:
        return debug

    env_val = os.environ.get("FLOTORCH_LOG_DEBUG")
    if env_val is not None:
        return str_to_bool(env_val)

    return False


def _resolve_provider_kind(log_provider: Optional[str]) -> str:
    """
    Resolve provider type with precedence:
    1. explicit arg
    2. env var FLOTORCH_LOG_PROVIDER
    3. default "console"
    """
    if log_provider is not None:
        return log_provider.lower().strip()

    env_kind = os.environ.get("FLOTORCH_LOG_PROVIDER")
    if env_kind is not None:
        return env_kind.lower().strip()

    return "console"


def _resolve_file_name(file_name: Optional[str]) -> str:
    """
    Resolve log file name with precedence:
    1. explicit arg
    2. env var FLOTORCH_LOG_FILE
    3. default "flotorch_logs.log"
    """
    if file_name is not None:
        return file_name

    return os.environ.get("FLOTORCH_LOG_FILE", "flotorch_logs.log")


def _build_provider(provider_kind: str, file_name: str):
    """
    Build the appropriate provider instance for the given kind.
    Providers themselves are responsible for configuring logging handlers
    in a way that is independent of root/user loggers.
    """
    if provider_kind == "file":
        return FileLoggerProvider(log_file=file_name)
    # default: console
    return ConsoleLoggerProvider()


def configure_logger(
    log_provider: Optional[str] = None,
    debug: Optional[bool] = None,
    file_name: Optional[str] = None,
) -> None:
    """
    Configure the singleton logger.

    Behavior:
      - debug flag: args > env > default False
      - provider:
          * If FlotorchLogger not yet created:
              - use args > env > default
          * If already created:
              - only change provider if log_provider or file_name is explicitly provided.
              - otherwise keep the existing provider.
    """

    # 1. Resolve debug regardless of provider changes
    resolved_debug = _resolve_debug(debug)

    # 2. Handle provider (creation and optional switching)
    if FlotorchLogger._instance is None:
        # First-time initialization: use args/env/defaults
        resolved_kind = _resolve_provider_kind(log_provider)
        resolved_file = _resolve_file_name(file_name)
        provider = _build_provider(resolved_kind, resolved_file)
        FlotorchLogger(provider)
    else:
        # Logger already exists: only change provider if explicitly requested
        if log_provider is not None or file_name is not None:
            resolved_kind = _resolve_provider_kind(log_provider)
            resolved_file = _resolve_file_name(file_name)
            provider = _build_provider(resolved_kind, resolved_file)
            FlotorchLogger._instance.provider = provider
        # else: keep the existing provider

    # 3. Apply debug flag
    FlotorchLogger._debug = resolved_debug


def get_logger() -> FlotorchLogger:
    """
    Return the global logger. If not initialized, create it using ONLY env variables
    (with defaults as fallback).
    """
    if FlotorchLogger._instance is None:
        # Resolve settings only from env + defaults
        provider_kind = _resolve_provider_kind(None)
        file_name = _resolve_file_name(None)
        debug = _resolve_debug(None)

        provider = _build_provider(provider_kind, file_name)
        FlotorchLogger(provider)
        FlotorchLogger._debug = debug

    return FlotorchLogger._instance
