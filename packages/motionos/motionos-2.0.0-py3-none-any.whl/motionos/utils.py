"""
MotionOS SDK - Utility Functions
"""

import os
import time
import uuid
from typing import List, TypeVar, Callable, Optional, Dict, Any
import logging

logger = logging.getLogger("motionos")


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    timestamp = int(time.time() * 1000)
    random_part = uuid.uuid4().hex[:8]
    return f"motionos-{timestamp}-{random_part}"


def exponential_backoff(attempt: int, base_delay_ms: float) -> float:
    """Calculate exponential backoff delay in seconds."""
    return (base_delay_ms / 1000.0) * (2 ** (attempt - 1))


def sanitize_for_logging(obj: Any) -> Any:
    """Sanitize object for logging (remove sensitive fields)."""
    if not isinstance(obj, dict):
        return obj

    sensitive_keys = [
        "api_key",
        "apiKey",
        "x-api-key",
        "authorization",
        "key",
        "secret",
        "password",
        "token",
    ]

    sanitized: Dict[str, Any] = {}
    for key, value in obj.items():
        key_lower = key.lower()
        if any(sk in key_lower for sk in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        else:
            sanitized[key] = value

    return sanitized


def remove_undefined(d: Dict[str, Any]) -> Dict[str, Any]:
    """Remove undefined/None values from dict."""
    return {k: v for k, v in d.items() if v is not None}


def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    """Chunk a list into smaller lists of specified size."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


T = TypeVar("T")


def create_client_from_env(**kwargs: Any) -> "MotionOS":
    """
    Create MotionOS client from environment variables.

    Reads:
    - MOTIONOS_API_KEY
    - MOTIONOS_PROJECT_ID
    - MOTIONOS_BASE_URL (optional)

    Args:
        **kwargs: Additional options to pass to MotionOS constructor

    Returns:
        Configured MotionOS instance

    Raises:
        InvalidAPIKeyError: If API key is not found in environment
        InvalidRequestError: If project ID is not found in environment
    """
    # Import here to avoid circular dependency
    from motionos.client import MotionOS
    from motionos.errors import InvalidAPIKeyError, InvalidRequestError

    api_key = os.getenv("MOTIONOS_API_KEY")
    project_id = os.getenv("MOTIONOS_PROJECT_ID")
    base_url = os.getenv("MOTIONOS_BASE_URL")

    if not api_key:
        raise InvalidAPIKeyError(
            "MOTIONOS_API_KEY environment variable is required"
        )

    if not project_id:
        raise InvalidRequestError(
            "MOTIONOS_PROJECT_ID environment variable is required"
        )

    client_options: Dict[str, Any] = {
        "api_key": api_key,
        "project_id": project_id,
        **kwargs,
    }

    if base_url:
        client_options["base_url"] = base_url

    return MotionOS(**client_options)

