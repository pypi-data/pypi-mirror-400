import logging
from .utils.logger_utils import configure_logger, find_caller_module
from .logger_provider import LoggerProvider

class ConsoleLoggerProvider(LoggerProvider):
    """
    Logger provider that logs messages to the console.
    """

    def __init__(self, name: str = "default"):
        # Configure logging but don't store a logger instance
        # We'll get a logger dynamically based on the caller
        configure_logger()

    def log(self, level: str, message: str) -> None:
        # Find the actual caller's module name
        module_name = find_caller_module()
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        log_level = getattr(logging, level.upper(), logging.INFO)

        logger._log(
            log_level,
            message,
            args=(),
            exc_info=None,
            extra=None,
            stacklevel=4
        )

    def get_logger(self) -> logging.Logger:
        # Return a logger for the caller's module
        module_name = find_caller_module()
        return logging.getLogger(module_name)
