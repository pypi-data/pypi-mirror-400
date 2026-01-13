"""
MotionOS SDK - Security Utilities

Enforces secure usage patterns, particularly around API key usage
in different environments.
"""

from typing import Tuple, Optional, Literal


ApiKeyType = Literal["secret", "publishable", "unknown"]


def validate_api_key(api_key: str) -> Tuple[bool, ApiKeyType, Optional[str]]:
    """
    Validate API key format and determine type.

    Args:
        api_key: The API key to validate

    Returns:
        Tuple of (is_valid, key_type, error_message)
        Key types: 'secret', 'publishable', 'unknown'
    """
    if not api_key or not isinstance(api_key, str):
        return False, "unknown", "API key is required and must be a string"

    trimmed = api_key.strip()

    if trimmed.startswith("sb_secret_"):
        return True, "secret", None

    if trimmed.startswith("sb_publishable_"):
        return True, "publishable", None

    return (
        False,
        "unknown",
        'API key must start with "sb_secret_" or "sb_publishable_"',
    )


def validate_operation(
    operation: str,
    key_type: ApiKeyType,
    environment: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Check if an operation is allowed with the given key type.

    Args:
        operation: Operation type ('ingest', 'retrieve', 'rollback')
        key_type: Type of API key ('secret', 'publishable')
        environment: Environment type ('browser', 'node', 'server') - optional

    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Ingest and rollback require secret keys
    if operation in ("ingest", "rollback"):
        if key_type == "publishable":
            return (
                False,
                "Publishable keys are read-only. "
                "Use a secret key for write operations (ingest/rollback). "
                "See: https://docs.motionos.ai/security",
            )
        if key_type == "secret":
            return True, None
        return False, "Invalid API key type for write operation"

    # Retrieve is allowed with any key type
    if operation == "retrieve":
        return True, None

    return False, f"Unknown operation: {operation}"

