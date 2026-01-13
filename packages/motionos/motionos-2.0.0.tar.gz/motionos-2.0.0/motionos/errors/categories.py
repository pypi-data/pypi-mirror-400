"""
MotionOS SDK - Error Categories

Error code definitions and categorization.
"""

from typing import List, Dict

# All possible SDK error codes
ERROR_CODES = [
    # Authentication
    "invalid_api_key",
    "unauthorized",
    # Permission
    "forbidden",
    "project_mismatch",
    # Rate limiting
    "rate_limited",
    # Validation
    "invalid_request",
    "bad_payload",
    "validation_error",
    # Engine
    "engine_unavailable",
    "ingest_failed",
    "retrieve_failed",
    "rollback_failed",
    # Timeout
    "timeout",
    "engine_timeout",
    # Network
    "network_error",
    # Not found
    "not_found",
    # Unknown
    "unknown_error",
]

# Error category groupings
ERROR_CATEGORIES: Dict[str, List[str]] = {
    "AUTHENTICATION": ["invalid_api_key", "unauthorized"],
    "PERMISSION": ["forbidden", "project_mismatch"],
    "RATE_LIMIT": ["rate_limited"],
    "VALIDATION": ["invalid_request", "bad_payload", "validation_error"],
    "ENGINE": ["engine_unavailable", "ingest_failed", "retrieve_failed", "rollback_failed"],
    "TIMEOUT": ["timeout", "engine_timeout"],
    "NETWORK": ["network_error"],
    "NOT_FOUND": ["not_found"],
    "UNKNOWN": ["unknown_error"],
}

# Errors that are safe to retry
RETRYABLE_ERRORS: List[str] = [
    "network_error",
    "timeout",
    "engine_timeout",
    "engine_unavailable",
    "rate_limited",
]

# Server error code to SDK error code mapping
SERVER_ERROR_MAP: Dict[str, str] = {
    # Authentication
    "invalid_api_key": "invalid_api_key",
    "missing_api_key": "invalid_api_key",
    "unauthorized": "invalid_api_key",
    # Permission
    "forbidden": "forbidden",
    "project_mismatch": "project_mismatch",
    # Rate limiting
    "rate_limited": "rate_limited",
    # Validation
    "bad_payload": "invalid_request",
    "invalid_request": "invalid_request",
    "validation_error": "invalid_request",
    # Engine
    "ingest_failed": "engine_unavailable",
    "retrieve_failed": "engine_unavailable",
    "rollback_failed": "engine_unavailable",
    "engine_error_500": "engine_unavailable",
    "engine_error_504": "timeout",
    "engine_timeout": "timeout",
    "engine_unavailable": "engine_unavailable",
    "go_engine_disabled": "engine_unavailable",
    # Not found
    "not_found": "not_found",
}

# HTTP status to error code mapping
HTTP_STATUS_MAP: Dict[int, str] = {
    400: "invalid_request",
    401: "invalid_api_key",
    403: "forbidden",
    404: "not_found",
    429: "rate_limited",
    500: "engine_unavailable",
    502: "engine_unavailable",
    503: "engine_unavailable",
    504: "timeout",
}


def normalize_error_code(server_code: str) -> str:
    """Get SDK error code from server error code."""
    return SERVER_ERROR_MAP.get(server_code, "unknown_error")


def get_error_category(code: str) -> str:
    """Get error category for a given error code."""
    for category, codes in ERROR_CATEGORIES.items():
        if code in codes:
            return category
    return "UNKNOWN"


def is_retryable_code(code: str) -> bool:
    """Check if an error code is retryable."""
    return code in RETRYABLE_ERRORS
