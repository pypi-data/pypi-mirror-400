"""
MotionOS SDK - Security Validation

Input validation and sanitization for security.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import re

from motionos.security.audit import get_operation_definition, is_blocked_operation


@dataclass
class SecurityValidation:
    """Security validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str]


def validate_operation(
    operation: str,
    key_type: str,
) -> SecurityValidation:
    """Validate an operation before execution."""
    errors: List[str] = []
    warnings: List[str] = []
    
    # Check if operation is blocked
    if is_blocked_operation(operation):
        errors.append(f"Operation '{operation}' is not available in the SDK.")
        return SecurityValidation(valid=False, errors=errors, warnings=warnings)
    
    # Get operation definition
    op_def = get_operation_definition(operation)
    if not op_def:
        warnings.append(f"Unknown operation '{operation}'. Proceeding with caution.")
    else:
        # Check key type requirement
        if op_def.required_key_type != "any" and op_def.required_key_type != key_type:
            errors.append(
                f"Operation '{operation}' requires a {op_def.required_key_type} key. "
                f"You are using a {key_type} key."
            )
    
    return SecurityValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_api_key_format(api_key: str) -> SecurityValidation:
    """Validate API key format (doesn't verify with server)."""
    errors: List[str] = []
    warnings: List[str] = []
    
    if not api_key:
        errors.append("API key is required.")
        return SecurityValidation(valid=False, errors=errors, warnings=warnings)
    
    if not isinstance(api_key, str):
        errors.append("API key must be a string.")
        return SecurityValidation(valid=False, errors=errors, warnings=warnings)
    
    # Check prefix
    is_secret = api_key.startswith("sb_secret_")
    is_publishable = api_key.startswith("sb_publishable_")
    
    if not is_secret and not is_publishable:
        errors.append(
            'Invalid API key format. Keys must start with "sb_secret_" or "sb_publishable_".'
        )
    
    # Check length
    if len(api_key) < 20:
        errors.append("API key appears to be truncated or invalid.")
    
    # Check for placeholders
    placeholders = ["xxx", "your-api-key", "placeholder", "test-key", "example"]
    for placeholder in placeholders:
        if placeholder in api_key.lower():
            warnings.append("API key appears to be a placeholder value.")
            break
    
    return SecurityValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_project_id_format(project_id: str) -> SecurityValidation:
    """Validate project ID format."""
    errors: List[str] = []
    warnings: List[str] = []
    
    if not project_id:
        errors.append("Project ID is required.")
        return SecurityValidation(valid=False, errors=errors, warnings=warnings)
    
    if not isinstance(project_id, str):
        errors.append("Project ID must be a string.")
        return SecurityValidation(valid=False, errors=errors, warnings=warnings)
    
    # Check format
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    slug_pattern = r"^[a-z0-9][a-z0-9-]*[a-z0-9]$"
    
    if not re.match(uuid_pattern, project_id, re.I) and not re.match(slug_pattern, project_id, re.I):
        warnings.append("Project ID format may be invalid. Expected UUID or project slug.")
    
    return SecurityValidation(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def sanitize_text_input(input_text: str) -> str:
    """Sanitize text input (remove potential injection vectors)."""
    if not input_text:
        return ""
    
    # Remove null bytes
    result = input_text.replace("\x00", "")
    
    # Remove control characters except newlines and tabs
    result = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", result)
    
    # Trim whitespace
    return result.strip()


def check_input_security(input_text: str) -> Tuple[bool, List[str]]:
    """Check for potential security issues in input."""
    issues: List[str] = []
    
    # Check for extremely long input
    if len(input_text) > 1_000_000:
        issues.append("Input exceeds maximum safe length (1MB).")
    
    # Check for binary data
    if re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", input_text):
        issues.append("Input contains binary/control characters.")
    
    return (len(issues) == 0, issues)
