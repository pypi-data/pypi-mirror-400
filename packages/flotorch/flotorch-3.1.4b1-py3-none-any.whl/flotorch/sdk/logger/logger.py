import os
from .logger_provider import LoggerProvider
from typing import Any, Optional
from .utils.models import LogModel
from .utils.logger_utils import str_to_bool

class FlotorchLogger:
    """
    Main logger class that delegates logging to a logger provider.
    """

    _instance = None  # Singleton instance
    _debug: bool = None

    def __new__(cls, provider: LoggerProvider = None):
        if cls._instance is None:
            if provider is None:
                raise ValueError("LoggerProvider must be provided for the first initialization.")
            cls._instance = super(FlotorchLogger, cls).__new__(cls)
            cls._instance.provider = provider
            cls._debug = str_to_bool(os.environ.get("FLOTORCH_DEBUG", 'false'))
    
        return cls._instance
        
    def _format(self, details: Any) -> str:
        if isinstance(details, LogModel):
            fmt = getattr(type(details), "formatter", None)
            if callable(fmt):
                return fmt(details)
            return details.model_dump_json()
        
        return str(details)
    
    def _log(self, level: str, message: str):
        self.provider.log(level, message)

    def debug(self, message: str) -> None:
        if self._debug:
            self._log("DEBUG", message)

    def info(self, details: LogModel | Any):
        if self._debug:
            message = self._format(details)   
            self._log("INFO", message)

    def warning(self, message: str) -> None:
        self._log("WARNING", message)
        
    def error(self, details: LogModel) -> None:
        message = self._format(details)
        self._log("ERROR", message)


