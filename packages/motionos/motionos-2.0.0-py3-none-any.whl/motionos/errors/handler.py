"""
MotionOS SDK - Error Handler

Converts HTTP responses and exceptions into typed SDK errors.
Never throws raw errors; always wraps them in MotionOSError subclasses.
"""

from typing import Dict, Any, Optional, TypeVar, Callable, Awaitable
from motionos.errors.base import (
    MotionOSError,
    AuthenticationError,
    ForbiddenError,
    RateLimitError,
    ValidationError,
    EngineUnavailableError,
    TimeoutError as MotionOSTimeoutError,
    NetworkError,
    NotFoundError,
    ProjectMismatchError,
)

T = TypeVar('T')


def http_response_to_error(
    status: int,
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> MotionOSError:
    """Convert an HTTP error response to a typed MotionOS error."""
    body = body or {}
    headers = headers or {}
    
    request_id = headers.get("x-request-id")
    message = body.get("message") or body.get("error") or _get_default_message(status)
    code = body.get("code")
    
    if status == 400:
        return ValidationError(message, body.get("field"), request_id)
    
    elif status == 401:
        return AuthenticationError(message, request_id)
    
    elif status == 403:
        if code == "project_mismatch":
            return ProjectMismatchError(message, request_id)
        return ForbiddenError(message, request_id)
    
    elif status == 404:
        return NotFoundError(message, request_id)
    
    elif status == 429:
        retry_after_ms = _parse_retry_after(headers.get("retry-after"))
        return RateLimitError(message, request_id, retry_after_ms)
    
    elif status in (500, 502, 503):
        return EngineUnavailableError(message, request_id)
    
    elif status == 504:
        return MotionOSTimeoutError(message, 0, request_id)
    
    else:
        return MotionOSError(message, "unknown_error", status, request_id)


def wrap_exception(error: Exception) -> MotionOSError:
    """Wrap any exception into a MotionOS error."""
    # Already a MotionOSError
    if isinstance(error, MotionOSError):
        return error
    
    error_message = str(error)
    error_type = type(error).__name__
    
    # Timeout errors
    if "timeout" in error_message.lower() or error_type in ("TimeoutError", "asyncio.TimeoutError"):
        return MotionOSTimeoutError(error_message)
    
    # Connection errors
    if any(x in error_type for x in ("ConnectionError", "ConnectionRefused", "ConnectionReset")):
        return NetworkError(error_message)
    
    if "network" in error_message.lower():
        return NetworkError(error_message)
    
    # Generic error
    return MotionOSError(
        error_message,
        "unknown_error",
        details={"original_error": error_type}
    )


async def handle_async(operation: Callable[[], Awaitable[T]]) -> T:
    """Safe error handler for async operations."""
    try:
        return await operation()
    except Exception as e:
        raise wrap_exception(e)


def handle_sync(operation: Callable[[], T]) -> T:
    """Safe error handler for sync operations."""
    try:
        return operation()
    except Exception as e:
        raise wrap_exception(e)


def _get_default_message(status: int) -> str:
    """Get default message for HTTP status."""
    messages = {
        400: "Invalid request",
        401: "Authentication required",
        403: "Access denied",
        404: "Resource not found",
        429: "Rate limit exceeded",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Request timeout",
    }
    return messages.get(status, "Unknown error")


def _parse_retry_after(value: Optional[str]) -> Optional[int]:
    """Parse Retry-After header to milliseconds."""
    if not value:
        return None
    
    # Try parsing as seconds
    try:
        seconds = int(value)
        return seconds * 1000
    except ValueError:
        pass
    
    # Try parsing as HTTP date
    from email.utils import parsedate_to_datetime
    try:
        from datetime import datetime, timezone
        retry_date = parsedate_to_datetime(value)
        now = datetime.now(timezone.utc)
        delta = (retry_date - now).total_seconds()
        return max(0, int(delta * 1000))
    except (ValueError, TypeError):
        pass
    
    return None


def is_retryable(error: Exception) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, MotionOSError):
        return error.retryable
    return False


def get_retry_delay(error: Exception) -> Optional[int]:
    """Get retry delay for an error (if applicable)."""
    if isinstance(error, RateLimitError) and error.retry_after_ms:
        return error.retry_after_ms
    if isinstance(error, MotionOSError) and error.retryable:
        return 1000  # Default 1s retry delay
    return None


def is_auth_error(error: Exception) -> bool:
    """Check if error is an authentication error."""
    return isinstance(error, AuthenticationError)


def is_permission_error(error: Exception) -> bool:
    """Check if error is a permission error."""
    return isinstance(error, ForbiddenError)


def is_rate_limit_error(error: Exception) -> bool:
    """Check if error is a rate limit error."""
    return isinstance(error, RateLimitError)


def is_validation_error(error: Exception) -> bool:
    """Check if error is a validation error."""
    return isinstance(error, ValidationError)


def is_timeout_error(error: Exception) -> bool:
    """Check if error is a timeout error."""
    return isinstance(error, MotionOSTimeoutError)


def is_network_error(error: Exception) -> bool:
    """Check if error is a network error."""
    return isinstance(error, NetworkError)


def sanitize_for_logging(error: MotionOSError) -> Dict[str, Any]:
    """Sanitize error for logging (removes sensitive data)."""
    return {
        "name": error.__class__.__name__,
        "code": error.code,
        "http_status": error.http_status,
        "request_id": error.request_id,
        "retryable": error.retryable,
        # Deliberately exclude message which might contain sensitive data
    }
