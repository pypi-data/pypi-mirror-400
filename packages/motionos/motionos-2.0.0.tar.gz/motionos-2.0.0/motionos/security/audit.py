"""
MotionOS SDK - Security Audit

Auditing of exposed methods and security verification.
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass


OperationCategory = Literal["read", "write", "timeline", "admin", "internal"]
KeyType = Literal["secret", "publishable", "any"]


@dataclass
class OperationDefinition:
    """Operation definition for audit."""
    name: str
    category: OperationCategory
    description: str
    required_key_type: KeyType
    allowed_in_browser: bool = False  # Always False for Python (server-side)


# Audited SDK operations - these are the ONLY operations exposed
AUDITED_OPERATIONS: Dict[str, OperationDefinition] = {
    # READ operations
    "retrieve": OperationDefinition(
        name="retrieve",
        category="read",
        description="Retrieve memories based on query",
        required_key_type="any",
    ),
    "health": OperationDefinition(
        name="health",
        category="read",
        description="Check service health",
        required_key_type="any",
    ),
    "list_domains": OperationDefinition(
        name="list_domains",
        category="read",
        description="List available domains",
        required_key_type="any",
    ),
    "list_policies": OperationDefinition(
        name="list_policies",
        category="read",
        description="List available policies",
        required_key_type="any",
    ),
    
    # WRITE operations
    "ingest": OperationDefinition(
        name="ingest",
        category="write",
        description="Ingest new memory",
        required_key_type="secret",
    ),
    "batch_ingest": OperationDefinition(
        name="batch_ingest",
        category="write",
        description="Batch ingest memories",
        required_key_type="secret",
    ),
    
    # TIMELINE operations
    "walk_timeline": OperationDefinition(
        name="walk_timeline",
        category="timeline",
        description="Walk timeline graph",
        required_key_type="secret",
    ),
    "check_validity": OperationDefinition(
        name="check_validity",
        category="timeline",
        description="Check version validity",
        required_key_type="secret",
    ),
    "get_lineage": OperationDefinition(
        name="get_lineage",
        category="timeline",
        description="Get version lineage",
        required_key_type="secret",
    ),
    "list_versions": OperationDefinition(
        name="list_versions",
        category="timeline",
        description="List memory versions",
        required_key_type="secret",
    ),
    "rollback": OperationDefinition(
        name="rollback",
        category="timeline",
        description="Rollback to version",
        required_key_type="secret",
    ),
}


# Operations that are NEVER exposed (admin/internal)
BLOCKED_OPERATIONS = [
    # User management
    "create_user",
    "delete_user",
    "update_user",
    "list_users",
    
    # Session management
    "create_session",
    "validate_session",
    "refresh_session",
    
    # Billing
    "get_billing",
    "update_subscription",
    
    # Database operations
    "direct_db_query",
    "raw_query",
    "supabase_query",
    
    # Admin operations
    "create_project",
    "delete_project",
    "rotate_keys",
    
    # Internal engine operations
    "engine_direct",
    "bypass_api",
]


def get_operation_definition(name: str) -> Optional[OperationDefinition]:
    """Get operation definition."""
    return AUDITED_OPERATIONS.get(name)


def is_audited_operation(name: str) -> bool:
    """Check if an operation is audited and allowed."""
    return name in AUDITED_OPERATIONS


def is_blocked_operation(name: str) -> bool:
    """Check if an operation is explicitly blocked."""
    return name in BLOCKED_OPERATIONS


def get_allowed_operations(key_type: str) -> List[str]:
    """Get all allowed operations for a key type."""
    result = []
    for name, op in AUDITED_OPERATIONS.items():
        if op.required_key_type == "any" or op.required_key_type == key_type:
            result.append(name)
    return result


def generate_security_audit() -> Dict[str, List[str]]:
    """Generate security audit report."""
    ops = AUDITED_OPERATIONS
    
    return {
        "audited_operations": list(ops.keys()),
        "blocked_operations": BLOCKED_OPERATIONS.copy(),
        "read_operations": [n for n, o in ops.items() if o.category == "read"],
        "write_operations": [n for n, o in ops.items() if o.category == "write"],
        "timeline_operations": [n for n, o in ops.items() if o.category == "timeline"],
    }
