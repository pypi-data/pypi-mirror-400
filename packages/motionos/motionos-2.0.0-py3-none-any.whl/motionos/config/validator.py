"""
MotionOS SDK - Configuration Validator

Eager validation of configuration with detailed error messages.
"""

import re
from typing import Tuple, Optional
from motionos.config.defaults import (
    API_KEY_PREFIX_SECRET,
    API_KEY_PREFIX_PUBLISHABLE,
    MIN_API_KEY_LENGTH,
)


class ConfigurationError(Exception):
    """Configuration validation error."""
    
    def __init__(self, message: str, field: str, code: str = "invalid_configuration"):
        super().__init__(message)
        self.field = field
        self.code = code


def validate_api_key(api_key: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate API key format and determine its type.
    
    Returns:
        Tuple of (is_valid, key_type, error_message)
    """
    if not api_key:
        return False, "unknown", "API key is required"
    
    if not isinstance(api_key, str):
        return False, "unknown", "API key must be a string"
    
    trimmed = api_key.strip()
    
    if len(trimmed) == 0:
        return False, "unknown", "API key cannot be empty"
    
    if len(trimmed) < MIN_API_KEY_LENGTH:
        return False, "unknown", f"API key too short (minimum {MIN_API_KEY_LENGTH} characters)"
    
    # Determine key type by prefix
    if trimmed.startswith(API_KEY_PREFIX_SECRET):
        return True, "secret", None
    
    if trimmed.startswith(API_KEY_PREFIX_PUBLISHABLE):
        return True, "publishable", None
    
    return False, "unknown", f"API key must start with '{API_KEY_PREFIX_SECRET}' or '{API_KEY_PREFIX_PUBLISHABLE}'"


def validate_project_id(project_id: str) -> None:
    """Validate project ID format."""
    if not project_id:
        raise ConfigurationError("Project ID is required", "project_id")
    
    if not isinstance(project_id, str):
        raise ConfigurationError("Project ID must be a string", "project_id")
    
    trimmed = project_id.strip()
    
    if len(trimmed) == 0:
        raise ConfigurationError("Project ID cannot be empty", "project_id")
    
    # UUID format validation
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, trimmed, re.IGNORECASE):
        raise ConfigurationError(
            "Project ID must be a valid UUID format (e.g., 123e4567-e89b-12d3-a456-426614174000)",
            "project_id"
        )


def validate_timeout(timeout: float, field_name: str = "timeout") -> None:
    """Validate timeout value."""
    if not isinstance(timeout, (int, float)):
        raise ConfigurationError(f"{field_name} must be a number", field_name)
    
    if timeout <= 0:
        raise ConfigurationError(f"{field_name} must be positive", field_name)
    
    if timeout > 120:
        raise ConfigurationError(f"{field_name} cannot exceed 120 seconds", field_name)


def validate_retry_attempts(attempts: int) -> None:
    """Validate retry attempts."""
    if not isinstance(attempts, int):
        raise ConfigurationError("retry.attempts must be an integer", "retry.attempts")
    
    if attempts < 0 or attempts > 10:
        raise ConfigurationError("retry.attempts must be between 0 and 10", "retry.attempts")


def validate_configuration(config) -> None:
    """
    Validate full SDK configuration.
    
    Performs eager validation - raises on ANY invalid configuration.
    """
    # Validate API key
    is_valid, key_type, error = validate_api_key(config.api_key)
    if not is_valid:
        raise ConfigurationError(error or "Invalid API key", "api_key", "invalid_api_key")
    
    # Validate project ID
    validate_project_id(config.project_id)
    
    # Validate timeout config if provided
    if config.timeout is not None:
        validate_timeout(config.timeout.ingest, "timeout.ingest")
        validate_timeout(config.timeout.retrieve, "timeout.retrieve")
        validate_timeout(config.timeout.default, "timeout.default")
    
    # Validate retry config if provided
    if config.retry is not None:
        validate_retry_attempts(config.retry.attempts)
    
    # Validate simulation config if provided
    if config.simulation is not None:
        if not isinstance(config.simulation.enabled, bool):
            raise ConfigurationError(
                "simulation.enabled must be explicitly set to True or False",
                "simulation.enabled"
            )
        
        if config.simulation.error_rate is not None:
            if config.simulation.error_rate < 0 or config.simulation.error_rate > 1:
                raise ConfigurationError(
                    "simulation.error_rate must be between 0 and 1",
                    "simulation.error_rate"
                )


def is_operation_allowed(
    operation: str,  # 'read' or 'write'
    key_type: str,
) -> Tuple[bool, Optional[str]]:
    """
    Check if operation is allowed for key type.
    
    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Publishable keys can only read
    if key_type == "publishable" and operation == "write":
        return False, "Publishable keys can only perform read operations. Use a secret key for writes."
    
    return True, None


def get_key_type(api_key: str) -> str:
    """Get the type of an API key."""
    is_valid, key_type, _ = validate_api_key(api_key)
    return key_type if is_valid else "unknown"
