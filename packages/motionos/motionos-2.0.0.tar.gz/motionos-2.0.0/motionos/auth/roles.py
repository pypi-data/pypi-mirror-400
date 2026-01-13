"""
MotionOS SDK - Role-Based Access Control

Defines roles and their permissions.
"""

from enum import Enum
from typing import List, Dict
from dataclasses import dataclass


class Role(str, Enum):
    """Available roles."""
    READ_WRITE = "read_write"
    READ_ONLY = "read_only"
    INGEST_ONLY = "ingest_only"


@dataclass(frozen=True)
class RolePermissions:
    """Permission definition."""
    can_ingest: bool
    can_retrieve: bool
    can_rollback: bool
    can_list_versions: bool
    can_walk_timeline: bool
    can_check_validity: bool
    can_get_lineage: bool
    can_list_domains: bool
    can_list_policies: bool
    can_health_check: bool


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, RolePermissions] = {
    Role.READ_WRITE: RolePermissions(
        can_ingest=True,
        can_retrieve=True,
        can_rollback=True,
        can_list_versions=True,
        can_walk_timeline=True,
        can_check_validity=True,
        can_get_lineage=True,
        can_list_domains=True,
        can_list_policies=True,
        can_health_check=True,
    ),
    Role.READ_ONLY: RolePermissions(
        can_ingest=False,
        can_retrieve=True,
        can_rollback=False,
        can_list_versions=True,
        can_walk_timeline=True,
        can_check_validity=True,
        can_get_lineage=True,
        can_list_domains=True,
        can_list_policies=True,
        can_health_check=True,
    ),
    Role.INGEST_ONLY: RolePermissions(
        can_ingest=True,
        can_retrieve=False,
        can_rollback=False,
        can_list_versions=False,
        can_walk_timeline=False,
        can_check_validity=False,
        can_get_lineage=False,
        can_list_domains=False,
        can_list_policies=False,
        can_health_check=True,
    ),
}

# Operation to permission attribute mapping
OPERATION_PERMISSION_MAP = {
    "ingest": "can_ingest",
    "retrieve": "can_retrieve",
    "rollback": "can_rollback",
    "timeline": "can_walk_timeline",
    "other": "can_health_check",
}


def role_has_permission(role: Role, operation: str) -> bool:
    """Check if role has permission for operation."""
    permissions = ROLE_PERMISSIONS.get(role)
    if not permissions:
        return False
    
    permission_attr = OPERATION_PERMISSION_MAP.get(operation, "can_health_check")
    return getattr(permissions, permission_attr, False)


def get_permitted_operations(role: Role) -> List[str]:
    """Get all permitted operations for a role."""
    permitted = []
    permissions = ROLE_PERMISSIONS.get(role)
    
    if not permissions:
        return permitted
    
    if permissions.can_ingest:
        permitted.append("ingest")
    if permissions.can_retrieve:
        permitted.append("retrieve")
    if permissions.can_rollback:
        permitted.append("rollback")
    if permissions.can_walk_timeline:
        permitted.append("timeline")
    if permissions.can_health_check:
        permitted.append("other")
    
    return permitted


def get_role_from_key_type(key_type: str) -> Role:
    """Get role from API key type."""
    if key_type == "secret":
        return Role.READ_WRITE
    elif key_type == "publishable":
        return Role.READ_ONLY
    else:
        return Role.READ_ONLY  # Default to least privilege


def get_role_description(role: Role) -> str:
    """Human-readable role description."""
    descriptions = {
        Role.READ_WRITE: "Full access - can read and write memory",
        Role.READ_ONLY: "Read-only access - can retrieve but not modify memory",
        Role.INGEST_ONLY: "Ingest-only access - can add memory but not read or modify",
    }
    return descriptions.get(role, "Unknown role")
