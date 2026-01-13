"""
MotionOS SDK - Authentication Headers

Builds authentication headers for API requests.
"""

from typing import Optional, Dict
from motionos.config.defaults import SDK_VERSION


def build_auth_headers(
    api_key: str,
    project_id: str,
    request_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    sdk_version: Optional[str] = None,
) -> Dict[str, str]:
    """Build authentication headers for API requests."""
    headers = {
        "x-api-key": api_key,
        "x-motionos-sdk-version": sdk_version or SDK_VERSION,
        "x-motionos-project-id": project_id,
        "Content-Type": "application/json",
    }
    
    if request_id:
        headers["x-request-id"] = request_id
    
    if agent_id:
        headers["x-motionos-agent-id"] = agent_id
    
    return headers


def extract_request_id(headers: Dict[str, str]) -> Optional[str]:
    """Extract request ID from response headers."""
    return headers.get("x-request-id") or headers.get("x-motionos-request-id")


def is_authentication_error(status_code: int) -> bool:
    """Check if response indicates authentication failure."""
    return status_code == 401


def is_permission_error(status_code: int) -> bool:
    """Check if response indicates permission error."""
    return status_code == 403


def get_safe_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Get safe headers for logging (API key masked)."""
    safe = headers.copy()
    
    if "x-api-key" in safe:
        key = safe["x-api-key"]
        if len(key) > 20:
            if key.startswith("sb_secret_"):
                prefix = "sb_secret_"
            elif key.startswith("sb_publishable_"):
                prefix = "sb_publishable_"
            else:
                prefix = ""
            content = key[len(prefix):]
            safe["x-api-key"] = f"{prefix}{content[:4]}...{content[-4:]}"
        else:
            safe["x-api-key"] = "***"
    
    return safe
