"""
MotionOS SDK - Common Types

Shared types used across multiple modules.
"""

from typing import Literal, Protocol, Any, Optional
from enum import Enum


class Logger(Protocol):
    """Protocol for custom loggers."""
    
    def log(self, *args: Any) -> None: ...
    def error(self, *args: Any) -> None: ...
    def warn(self, *args: Any) -> None: ...
    def debug(self, *args: Any) -> None: ...


class OperationType(str, Enum):
    """Operation types for request routing."""
    INGEST = "ingest"
    RETRIEVE = "retrieve"
    ROLLBACK = "rollback"
    TIMELINE = "timeline"
    OTHER = "other"


class EnvironmentType(str, Enum):
    """Runtime environment types."""
    SYNC = "sync"
    ASYNC = "async"
    SERVERLESS = "serverless"


class ApiKeyType(str, Enum):
    """API key types."""
    SECRET = "secret"
    PUBLISHABLE = "publishable"
    UNKNOWN = "unknown"


class ApiKeyRole(str, Enum):
    """API key role permissions."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    INGEST_ONLY = "ingest_only"


# Type aliases
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
