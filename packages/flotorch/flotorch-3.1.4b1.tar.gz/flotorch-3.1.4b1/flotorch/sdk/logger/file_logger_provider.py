import logging
from .utils.logger_utils import configure_file_logger, find_caller_module
from .logger_provider import LoggerProvider

class FileLoggerProvider(LoggerProvider):
    """
    Logger provider that logs messages to a file.
    """

    def __init__(self, name: str = "default", log_file: str = "file.log"):
        """
        Initialize the file logger provider.
        
        Args:
            name (str): Logger name (for compatibility, not used for file logging).
            log_file (str): Path to the log file. Defaults to "file.log".
        """
        self.log_file = log_file
        # Configure logging but don't store a logger instance
        # We'll get a logger dynamically based on the caller
        configure_file_logger(log_file)

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

