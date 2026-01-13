"""
MotionOS SDK - Error Handling

Provides normalized, developer-friendly errors with consistent error codes
matching the SDK specification.
"""

from typing import Optional, Any, Dict
import json


class MotionOSError(Exception):
    """Base exception for all MotionOS SDK errors."""

    def __init__(
        self,
        message: str,
        code: str,
        http_status: Optional[int] = None,
        details: Optional[Any] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status
        self.details = details
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [f"MotionOSError: {self.message} ({self.code})"]
        if self.http_status:
            parts.append(f"HTTP {self.http_status}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " - ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"http_status={self.http_status}, "
            f"request_id={self.request_id!r})"
        )


class InvalidAPIKeyError(MotionOSError):
    """Invalid or missing API key."""

    def __init__(self, message: str = "Invalid API key", **kwargs):
        super().__init__(message, "invalid_api_key", **kwargs)


class ProjectMismatchError(MotionOSError):
    """Project ID doesn't match API key."""

    def __init__(self, message: str = "Project ID mismatch", **kwargs):
        super().__init__(message, "project_mismatch", **kwargs)


class RateLimitError(MotionOSError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, "rate_limited", **kwargs)


class NetworkError(MotionOSError):
    """Network connection error."""

    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, "network_error", **kwargs)


class TimeoutError(MotionOSError):
    """Request timeout."""

    def __init__(self, message: str = "Request timeout", **kwargs):
        super().__init__(message, "timeout", **kwargs)


class EngineUnavailableError(MotionOSError):
    """MotionOS engine unavailable."""

    def __init__(self, message: str = "Engine unavailable", **kwargs):
        super().__init__(message, "engine_unavailable", **kwargs)


class InvalidRequestError(MotionOSError):
    """Invalid request parameters."""

    def __init__(self, message: str = "Invalid request", **kwargs):
        super().__init__(message, "invalid_request", **kwargs)


class ForbiddenError(MotionOSError):
    """Operation forbidden (e.g., write with publishable key)."""

    def __init__(self, message: str = "Operation forbidden", **kwargs):
        super().__init__(message, "forbidden", **kwargs)


class NotFoundError(MotionOSError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, "not_found", **kwargs)


# Error code mapping from server responses to SDK error classes
ERROR_CODE_MAP: Dict[str, type] = {
    "invalid_api_key": InvalidAPIKeyError,
    "missing_api_key": InvalidAPIKeyError,
    "unauthorized": InvalidAPIKeyError,
    "forbidden": ForbiddenError,
    "project_mismatch": ProjectMismatchError,
    "rate_limited": RateLimitError,
    "bad_payload": InvalidRequestError,
    "invalid_request": InvalidRequestError,
    "validation_error": InvalidRequestError,
    "ingest_failed": EngineUnavailableError,
    "retrieve_failed": EngineUnavailableError,
    "rollback_failed": EngineUnavailableError,
    "engine_error_500": EngineUnavailableError,
    "engine_error_504": TimeoutError,
    "engine_timeout": TimeoutError,
    "engine_unavailable": EngineUnavailableError,
    "go_engine_disabled": EngineUnavailableError,
    "not_found": NotFoundError,
}

# HTTP status code to error class mapping
HTTP_STATUS_MAP: Dict[int, type] = {
    401: InvalidAPIKeyError,
    403: ForbiddenError,
    404: NotFoundError,
    429: RateLimitError,
    500: EngineUnavailableError,
    503: EngineUnavailableError,
    504: TimeoutError,
}


def normalize_error_code(server_code: str) -> type:
    """Normalize server error code to SDK error class."""
    return ERROR_CODE_MAP.get(server_code, MotionOSError)


def create_motionos_error(
    source: Any,
    default_code: str = "unknown_error",
    http_status: Optional[int] = None,
) -> MotionOSError:
    """Create a MotionOSError from various error sources."""
    # If it's already a MotionOSError, return it
    if isinstance(source, MotionOSError):
        return source

    # Extract error information
    message = "An error occurred"
    error_class = MotionOSError
    details: Optional[Any] = None
    request_id: Optional[str] = None

    # Handle dict/response objects
    if isinstance(source, dict):
        if "error" in source or "message" in source:
            server_code = source.get("error", default_code)
            message = source.get("message", source.get("error", message))
            error_class = normalize_error_code(server_code)
            request_id = source.get("request_id")
            details = source.get("details")
        elif "code" in source:
            error_class = normalize_error_code(source["code"])
            message = source.get("message", message)
    elif isinstance(source, str):
        message = source
        # Try to parse as JSON
        try:
            parsed = json.loads(source)
            if isinstance(parsed, dict):
                return create_motionos_error(parsed, default_code, http_status)
        except (json.JSONDecodeError, ValueError):
            pass
    elif isinstance(source, Exception):
        message = str(source)

    # Use HTTP status if no specific error class found
    if error_class == MotionOSError and http_status:
        error_class = HTTP_STATUS_MAP.get(http_status, MotionOSError)

    # Sanitize message
    message = sanitize_error_message(message)

    return error_class(message, error_class.__name__.lower().replace("error", ""), http_status, details, request_id)


def sanitize_error_message(message: str) -> str:
    """Sanitize error messages to remove internal details."""
    if not message:
        return "An error occurred"

    # Remove stack traces and internal error details
    sanitized = message
    sanitized = sanitized.replace("failed to connect", "Connection failed")
    sanitized = sanitized.replace("database.*error", "Storage error")
    sanitized = sanitized.replace("timeout.*exceeded", "Request timeout")
    sanitized = sanitized.replace("ECONNREFUSED", "Connection refused")
    sanitized = sanitized.replace("ENOTFOUND", "Host not found")

    return sanitized.strip() or "An error occurred"


def is_retryable(error: Exception) -> bool:
    """Check if an error is retryable."""
    if not isinstance(error, MotionOSError):
        return False

    retryable_codes = [
        "network_error",
        "timeout",
        "engine_unavailable",
        "rate_limited",
    ]

    return error.code in retryable_codes

