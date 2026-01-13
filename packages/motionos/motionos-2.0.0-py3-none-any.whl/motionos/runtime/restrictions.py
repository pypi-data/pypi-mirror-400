"""
MotionOS SDK - Runtime Restrictions

Enforces security restrictions based on runtime environment.
"""

from typing import List, Tuple, Optional


def is_operation_allowed(
    operation: str,
    key_type: str,
) -> Tuple[bool, Optional[str]]:
    """
    Check if an operation is allowed.
    
    Python SDK typically runs server-side, so most operations are allowed.
    
    Returns:
        Tuple of (allowed, reason) where reason is provided if not allowed.
    """
    # Python SDK is always server-side, so fewer restrictions
    # than browser JavaScript
    
    # Validate key type for operation
    write_operations = ["ingest", "rollback", "delete", "admin"]
    
    if operation in write_operations and key_type == "publishable":
        return (
            False,
            f"Operation '{operation}' requires a secret API key. Publishable keys are read-only."
        )
    
    return (True, None)


def get_allowed_operations(key_type: str) -> List[str]:
    """Get list of allowed operations for a key type."""
    read_operations = ["retrieve", "health", "list_versions", "check_validity", "get_lineage"]
    write_operations = ["ingest", "rollback"]
    admin_operations = ["admin"]
    
    if key_type == "publishable":
        return read_operations
    
    if key_type == "secret":
        return read_operations + write_operations + admin_operations
    
    return read_operations  # Default to read-only


def enforce_restrictions(operation: str, key_type: str) -> None:
    """Enforce runtime restrictions (raises on violation)."""
    allowed, reason = is_operation_allowed(operation, key_type)
    if not allowed:
        raise PermissionError(reason)


# Security reminders for different contexts
SECURITY_REMINDERS = {
    "general": [
        "Use environment variables for API keys",
        "Never commit API keys to version control",
        "Rotate keys regularly",
    ],
    "serverless": [
        "Re-authenticate on each invocation (no persistent state)",
        "Use environment variables or secrets manager for API keys",
        "Account for cold starts in timeout configuration",
    ],
    "docker": [
        "Use secrets management for API keys",
        "Never bake API keys into Docker images",
        "Use runtime environment variables or secret mounts",
    ],
}
