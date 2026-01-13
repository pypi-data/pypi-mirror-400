"""
MotionOS SDK - Security Boundaries

Hard security boundaries that cannot be bypassed.
"""

from typing import Dict, List, Tuple, Optional


# Security boundaries - these are absolute rules
SECURITY_BOUNDARIES = {
    "SINGLE_ENTRYPOINT": True,  # SDK only communicates with Node API
    "API_KEY_AUTH_ONLY": True,  # No user sessions or OAuth
    "NO_LOCAL_STORAGE": True,   # Never cache sensitive data locally
    "SECRET_KEYS_SERVER_ONLY": True,  # Secret keys server-side only
    "NO_ADMIN_ACCESS": True,    # No admin operations in SDK
}


# Allowed external endpoints
ALLOWED_ENDPOINTS = {
    "PRODUCTION": "https://api.motionos.dev",
    "LOCAL_DEV": "http://localhost:3000",
}


def is_allowed_endpoint(url: str) -> bool:
    """Check if an endpoint is allowed."""
    return any(url.startswith(allowed) for allowed in ALLOWED_ENDPOINTS.values())


def validate_endpoint(url: str) -> Tuple[bool, Optional[str]]:
    """Validate URL doesn't attempt to access internal services."""
    # Block Supabase direct access
    if "supabase" in url or ".supabase." in url:
        return (
            False,
            "Direct Supabase access is not allowed. Use the SDK API methods.",
        )
    
    # Block internal engine access
    if "/engine/" in url and "/api/" not in url:
        return (
            False,
            "Direct engine access is not allowed. Use the SDK API methods.",
        )
    
    # Block admin endpoints
    if "/admin/" in url or "/internal/" in url:
        return (
            False,
            "Admin and internal endpoints are not accessible via SDK.",
        )
    
    return (True, None)


def get_security_headers(
    api_key: str,
    project_id: str,
    sdk_version: str,
) -> Dict[str, str]:
    """Security headers that are always included."""
    return {
        "x-api-key": api_key,
        "x-motionos-project-id": project_id,
        "x-motionos-sdk-version": sdk_version,
        "x-motionos-sdk": "python",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    }


def verify_security_boundaries(
    operation: str,
    endpoint: str,
    key_type: str,
) -> Tuple[bool, List[str]]:
    """Verify a request doesn't violate security boundaries."""
    violations: List[str] = []
    
    # Validate endpoint
    valid, error = validate_endpoint(endpoint)
    if not valid:
        violations.append(error)  # type: ignore
    
    # Check blocked operations
    blocked_patterns = ["admin", "user", "session", "billing", "supabase"]
    for pattern in blocked_patterns:
        if pattern in operation.lower():
            violations.append(f"Operation '{operation}' appears to access blocked functionality.")
    
    return (len(violations) == 0, violations)
