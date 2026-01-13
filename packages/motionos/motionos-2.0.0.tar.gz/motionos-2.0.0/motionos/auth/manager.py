"""
MotionOS SDK - Authentication Manager

Centralized authentication handling for the SDK.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum

from motionos.config.defaults import (
    API_KEY_PREFIX_SECRET,
    API_KEY_PREFIX_PUBLISHABLE,
    MIN_API_KEY_LENGTH,
)


class ApiKeyType(str, Enum):
    """API key types."""
    SECRET = "secret"
    PUBLISHABLE = "publishable"
    UNKNOWN = "unknown"


class ApiKeyRole(str, Enum):
    """API key role permissions."""
    READ_WRITE = "read_write"
    READ_ONLY = "read_only"
    INGEST_ONLY = "ingest_only"
    UNKNOWN = "unknown"


@dataclass
class ApiKeyValidationResult:
    """Result of API key validation."""
    valid: bool
    key_type: ApiKeyType
    role: ApiKeyRole
    error: Optional[str] = None


@dataclass
class PermissionCheckResult:
    """Result of permission check."""
    allowed: bool
    reason: Optional[str] = None
    suggestion: Optional[str] = None


class AuthenticationManager:
    """
    Authentication Manager
    
    Handles all authentication-related operations:
    - API key validation and type detection
    - Role-based permission checks
    - Key masking for logging
    """
    
    def __init__(self, api_key: str, environment: str = "sync"):
        validation = self.validate_api_key(api_key)
        if not validation.valid:
            raise ValueError(validation.error or "Invalid API key")
        
        self._api_key = api_key.strip()
        self._key_type = validation.key_type
        self._role = validation.role
        self._environment = environment
    
    @staticmethod
    def validate_api_key(api_key) -> ApiKeyValidationResult:
        """Validate API key format and determine type/role."""
        if not api_key:
            return ApiKeyValidationResult(
                valid=False, 
                key_type=ApiKeyType.UNKNOWN, 
                role=ApiKeyRole.UNKNOWN,
                error="API key is required"
            )
        
        if not isinstance(api_key, str):
            return ApiKeyValidationResult(
                valid=False,
                key_type=ApiKeyType.UNKNOWN,
                role=ApiKeyRole.UNKNOWN,
                error="API key must be a string"
            )
        
        trimmed = api_key.strip()
        
        if len(trimmed) == 0:
            return ApiKeyValidationResult(
                valid=False,
                key_type=ApiKeyType.UNKNOWN,
                role=ApiKeyRole.UNKNOWN,
                error="API key cannot be empty"
            )
        
        if len(trimmed) < MIN_API_KEY_LENGTH:
            return ApiKeyValidationResult(
                valid=False,
                key_type=ApiKeyType.UNKNOWN,
                role=ApiKeyRole.UNKNOWN,
                error=f"API key too short (minimum {MIN_API_KEY_LENGTH} characters)"
            )
        
        # Determine key type and role by prefix
        if trimmed.startswith(API_KEY_PREFIX_SECRET):
            return ApiKeyValidationResult(
                valid=True,
                key_type=ApiKeyType.SECRET,
                role=ApiKeyRole.READ_WRITE
            )
        
        if trimmed.startswith(API_KEY_PREFIX_PUBLISHABLE):
            return ApiKeyValidationResult(
                valid=True,
                key_type=ApiKeyType.PUBLISHABLE,
                role=ApiKeyRole.READ_ONLY
            )
        
        return ApiKeyValidationResult(
            valid=False,
            key_type=ApiKeyType.UNKNOWN,
            role=ApiKeyRole.UNKNOWN,
            error=f"API key must start with '{API_KEY_PREFIX_SECRET}' or '{API_KEY_PREFIX_PUBLISHABLE}'"
        )
    
    @property
    def key_type(self) -> ApiKeyType:
        """Get key type."""
        return self._key_type
    
    @property
    def role(self) -> ApiKeyRole:
        """Get key role."""
        return self._role
    
    def is_operation_allowed(self, operation: str) -> PermissionCheckResult:
        """Check if operation is allowed."""
        write_operations = ["ingest", "rollback"]
        is_write = operation in write_operations
        
        # Read-only keys cannot write
        if self._role == ApiKeyRole.READ_ONLY and is_write:
            return PermissionCheckResult(
                allowed=False,
                reason="Publishable keys can only perform read operations",
                suggestion="Use a secret key for write operations like ingest or rollback"
            )
        
        return PermissionCheckResult(allowed=True)
    
    def can_perform(self, operation: str) -> bool:
        """Check if operation is allowed (shorthand)."""
        return self.is_operation_allowed(operation).allowed
    
    def get_masked_key(self) -> str:
        """Get masked API key for logging."""
        return mask_api_key(self._api_key)
    
    def get_api_key(self) -> str:
        """Get raw API key (use with caution)."""
        return self._api_key
    
    def to_debug_info(self) -> dict:
        """Get debug info (safe to log)."""
        return {
            "key_type": self._key_type.value,
            "role": self._role.value,
            "masked_key": self.get_masked_key(),
            "environment": self._environment,
        }


def validate_api_key(api_key) -> ApiKeyValidationResult:
    """Quick validation without creating a manager."""
    return AuthenticationManager.validate_api_key(api_key)


def mask_api_key(api_key: str) -> str:
    """Mask API key for logging (never log full key)."""
    if not api_key or len(api_key) < 20:
        return "***"
    
    # Determine prefix
    if api_key.startswith(API_KEY_PREFIX_SECRET):
        prefix = API_KEY_PREFIX_SECRET
    elif api_key.startswith(API_KEY_PREFIX_PUBLISHABLE):
        prefix = API_KEY_PREFIX_PUBLISHABLE
    else:
        prefix = ""
    
    content = api_key[len(prefix):]
    if len(content) <= 8:
        return f"{prefix}***"
    
    return f"{prefix}{content[:4]}...{content[-4:]}"


def get_key_type(api_key: str) -> ApiKeyType:
    """Get key type from API key string."""
    result = AuthenticationManager.validate_api_key(api_key)
    return result.key_type


def get_key_role(api_key: str) -> ApiKeyRole:
    """Get key role from API key string."""
    result = AuthenticationManager.validate_api_key(api_key)
    return result.role
