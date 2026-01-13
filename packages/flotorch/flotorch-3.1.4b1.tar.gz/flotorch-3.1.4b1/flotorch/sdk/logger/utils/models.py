from pydantic import BaseModel, ConfigDict
from typing import Any, Callable, ClassVar, List, Optional, Dict
from .formatter import LogsFormatter

LogFormatter = Callable[[Any], str]


class LogModel(BaseModel):
    # Each subclass can set this
    formatter: ClassVar[Optional[LogFormatter]] = None


class ObjectCreation(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.object_creation
    class_name: str
    extras: Optional[Dict[str, Any]] = None


class Error(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.error
    model_config = ConfigDict(arbitrary_types_allowed=True)
    operation: str
    error: Exception


class LLMRequest(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.llm_request
    model: str
    messages: Optional[List[Dict[str, Any]]] = None
    request_type: str = "sync"   # or "async"
    tools: Optional[List[Dict[str, Any]]] = None


class LLMResponse(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.llm_response
    model: str
    content: str
    tool_calls: Optional[List] = None
    usage: Optional[Dict] = None
    is_final_response: bool = False
    request_type: str = "sync"   # or "async"



class SessionOperation(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.session_operation
    operation: str
    session_uid: Optional[str] = None
    params: Optional[Dict[str,Any]] = None
    request_type: str = "sync"   # or "async"



class MemoryOperation(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.memory_operation
    operation: str
    provider: str
    memory_id: Optional[str] = None
    params: Optional[Dict[str,Any]] = None
    request_type: str = "sync"   # or "async"



class VectorStoreOperation(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.vectorstore_operation
    operation: str
    vectorstore_id: str
    params: Optional[Dict[str,Any]] = None
    request_type: str = "sync"   # or "async"


class HttpRequest(LogModel):
    formatter: ClassVar[LogFormatter] = LogsFormatter.http_request
    method: str
    url: str
    status_code: Optional[int] = None
    duration: Optional[float] = None
    request_type: str = "sync"   # or "async"