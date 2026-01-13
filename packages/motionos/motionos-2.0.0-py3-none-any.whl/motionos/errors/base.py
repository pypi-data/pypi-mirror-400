"""
MotionOS SDK - Base Error Classes

Developer-friendly errors that:
- Never expose raw stack traces externally
- Always have a stable error code
- Include retryability flag
- Contain request ID for correlation
"""

from typing import Optional, Dict, Any
from motionos.errors.categories import RETRYABLE_ERRORS


class MotionOSError(Exception):
    """Base error class for all MotionOS SDK errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "unknown_error",
        http_status: Optional[int] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.request_id = request_id
        self.details = details
        self.retryable = code in RETRYABLE_ERRORS
    
    def __str__(self) -> str:
        """Sanitized string representation."""
        parts = [f"MotionOSError: {self.args[0]} ({self.code})"]
        if self.http_status:
            parts.append(f"HTTP {self.http_status}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        if self.retryable:
            parts.append("[retryable]")
        return " - ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.__class__.__name__,
            "message": str(self.args[0]),
            "code": self.code,
            "http_status": self.http_status,
            "request_id": self.request_id,
            "retryable": self.retryable,
        }


class AuthenticationError(MotionOSError):
    """Authentication error (invalid API key)."""
    
    def __init__(self, message: str = "Invalid API key", request_id: Optional[str] = None):
        super().__init__(message, "invalid_api_key", 401, request_id)


class InvalidAPIKeyError(AuthenticationError):
    """Alias for AuthenticationError."""
    pass


class ForbiddenError(MotionOSError):
    """Permission error (operation not allowed)."""
    
    def __init__(self, message: str = "Operation not allowed", request_id: Optional[str] = None):
        super().__init__(message, "forbidden", 403, request_id)


class ProjectMismatchError(MotionOSError):
    """Project mismatch error."""
    
    def __init__(self, message: str = "Project ID mismatch", request_id: Optional[str] = None):
        super().__init__(message, "project_mismatch", 403, request_id)


class RateLimitError(MotionOSError):
    """Rate limit error."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        request_id: Optional[str] = None,
        retry_after_ms: Optional[int] = None,
    ):
        super().__init__(message, "rate_limited", 429, request_id)
        self.retry_after_ms = retry_after_ms


class ValidationError(MotionOSError):
    """Validation error (invalid request)."""
    
    def __init__(
        self, 
        message: str = "Invalid request", 
        field: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, "invalid_request", 400, request_id, {"field": field} if field else None)
        self.field = field


class InvalidRequestError(ValidationError):
    """Alias for ValidationError."""
    pass


class EngineUnavailableError(MotionOSError):
    """Engine unavailable error."""
    
    def __init__(self, message: str = "Engine unavailable", request_id: Optional[str] = None):
        super().__init__(message, "engine_unavailable", 503, request_id)


class TimeoutError(MotionOSError):
    """Timeout error."""
    
    def __init__(
        self, 
        message: str = "Request timeout", 
        timeout_ms: int = 0,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, "timeout", 504, request_id, {"timeout_ms": timeout_ms})
        self.timeout_ms = timeout_ms


class NetworkError(MotionOSError):
    """Network error."""
    
    def __init__(self, message: str = "Network error", request_id: Optional[str] = None):
        super().__init__(message, "network_error", None, request_id)


class NotFoundError(MotionOSError):
    """Not found error."""
    
    def __init__(self, message: str = "Resource not found", request_id: Optional[str] = None):
        super().__init__(message, "not_found", 404, request_id)
