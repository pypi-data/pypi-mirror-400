from typing import TypedDict, Any, Literal, Optional

LogLevel = Literal["debug", "info", "warn", "error", "critical"]

class LogEvent(TypedDict, total=False):
    """Log event structure"""
    level: LogLevel
    message: str
    timestamp: int
    service: str
    # Allow additional fields
    __annotations__: dict[str, Any]

class SeeLogsConfig(TypedDict, total=False):
    """Configuration for SeeLogs client"""
    token: str
    service: Optional[str]
    endpoint: str
    batch_size: Optional[int]
    flush_interval: Optional[float]

class LogBatch(TypedDict):
    """Batch of logs for sending"""
    logs: list[LogEvent]

class HealthResponse(TypedDict):
    """Health check response"""
    status: str
    timestamp: str