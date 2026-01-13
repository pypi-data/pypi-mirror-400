"""
MotionOS SDK - Error Factory

Creates appropriate error instances from various sources.
"""

import re
from typing import Any, Optional, Dict, Union
from motionos.errors.base import (
    MotionOSError,
    AuthenticationError,
    ForbiddenError,
    ProjectMismatchError,
    RateLimitError,
    ValidationError,
    EngineUnavailableError,
    TimeoutError,
    NetworkError,
    NotFoundError,
)
from motionos.errors.categories import (
    normalize_error_code,
    HTTP_STATUS_MAP,
    is_retryable_code,
    RETRYABLE_ERRORS,
)


def is_motionos_error(error: Any) -> bool:
    """Check if an error is a MotionOSError."""
    return isinstance(error, MotionOSError)


def is_retryable(error: Any) -> bool:
    """Check if an error is retryable."""
    if isinstance(error, MotionOSError):
        return error.retryable
    return False


def sanitize_error_message(message: str) -> str:
    """Sanitize error message to remove internal details."""
    if not message:
        return "An error occurred"
    
    # Remove stack traces
    message = re.sub(r'File ".*", line \d+', '', message)
    # Remove internal paths
    message = re.sub(r'/[^\s]+\.(py|js):\d+', '', message)
    # Clean up common patterns
    message = re.sub(r'failed to connect.*', 'Connection failed', message, flags=re.IGNORECASE)
    message = re.sub(r'database.*error', 'Storage error', message, flags=re.IGNORECASE)
    message = re.sub(r'timeout.*exceeded', 'Request timeout', message, flags=re.IGNORECASE)
    
    return message.strip() or "An error occurred"


def create_typed_error(
    message: str,
    code: str,
    http_status: Optional[int] = None,
    request_id: Optional[str] = None,
) -> MotionOSError:
    """Create the appropriate error class for a given code."""
    
    if code in ("invalid_api_key", "unauthorized"):
        return AuthenticationError(message, request_id)
    
    if code == "forbidden":
        return ForbiddenError(message, request_id)
    
    if code == "project_mismatch":
        return ProjectMismatchError(message, request_id)
    
    if code == "rate_limited":
        return RateLimitError(message, request_id)
    
    if code in ("invalid_request", "bad_payload", "validation_error"):
        return ValidationError(message, None, request_id)
    
    if code in ("engine_unavailable", "ingest_failed", "retrieve_failed", "rollback_failed"):
        return EngineUnavailableError(message, request_id)
    
    if code in ("timeout", "engine_timeout"):
        return TimeoutError(message, 0, request_id)
    
    if code == "network_error":
        return NetworkError(message, request_id)
    
    if code == "not_found":
        return NotFoundError(message, request_id)
    
    return MotionOSError(message, code, http_status, request_id)


def create_motionos_error(
    source: Any,
    default_code: str = "unknown_error",
    http_status: Optional[int] = None,
) -> MotionOSError:
    """
    Create a MotionOSError from various sources.
    
    Handles:
    - Server response dicts
    - Exception objects
    - String messages
    - Unknown errors
    """
    # Already a MotionOSError
    if isinstance(source, MotionOSError):
        return source
    
    message = "An error occurred"
    code = default_code
    request_id: Optional[str] = None
    status = http_status
    
    # Handle dict sources (server responses)
    if isinstance(source, dict):
        if "message" in source:
            message = str(source["message"])
        elif "error" in source and isinstance(source["error"], str):
            message = source["error"]
        
        if "error" in source and isinstance(source["error"], str):
            code = normalize_error_code(source["error"])
        elif "code" in source:
            code = normalize_error_code(str(source["code"]))
        
        if "request_id" in source:
            request_id = str(source["request_id"])
        
        if code == "unknown_error" and "status" in source:
            status = int(source["status"])
            code = HTTP_STATUS_MAP.get(status, code)
    
    # Handle string sources
    elif isinstance(source, str):
        message = source
    
    # Handle Exception instances
    elif isinstance(source, Exception):
        message = str(source)
        
        # Check for specific error types
        if "timeout" in message.lower():
            code = "timeout"
        elif "network" in message.lower() or "connection" in message.lower():
            code = "network_error"
    
    # Use HTTP status for code if still unknown
    if code == "unknown_error" and status:
        code = HTTP_STATUS_MAP.get(status, code)
    
    # Sanitize message
    message = sanitize_error_message(message)
    
    return create_typed_error(message, code, status, request_id)


def create_timeout_error(timeout_ms: int, request_id: Optional[str] = None) -> TimeoutError:
    """Create a timeout error."""
    return TimeoutError(f"Request timeout after {timeout_ms}ms", timeout_ms, request_id)


def create_network_error(message: str = "Network error", request_id: Optional[str] = None) -> NetworkError:
    """Create a network error."""
    return NetworkError(sanitize_error_message(message), request_id)


def create_validation_error(
    message: str,
    field: Optional[str] = None,
    request_id: Optional[str] = None,
) -> ValidationError:
    """Create a validation error."""
    return ValidationError(message, field, request_id)
