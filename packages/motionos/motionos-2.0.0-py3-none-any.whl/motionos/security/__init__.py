"""
MotionOS SDK - Security Package

Security auditing, validation, and boundary enforcement.
"""

from motionos.security.audit import (
    AUDITED_OPERATIONS,
    BLOCKED_OPERATIONS,
    is_audited_operation,
    is_blocked_operation,
    get_allowed_operations,
    KeyType as ApiKeyType,
)
from motionos.security.boundaries import (
    SECURITY_BOUNDARIES,
    is_allowed_endpoint,
    validate_endpoint,
    verify_security_boundaries,
)
from motionos.security.validation import (
    validate_operation,
    validate_api_key_format,
    validate_api_key_format as validate_api_key,
    sanitize_text_input,
)
