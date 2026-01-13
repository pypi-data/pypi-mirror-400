"""
MotionOS SDK - Version Management

Semantic versioning and version headers.
"""

import re
from typing import Dict, Optional
from dataclasses import dataclass

SDK_VERSION = "2.0.0"


@dataclass
class SemanticVersion:
    """Parsed semantic version."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None


def parse_version(version: str) -> SemanticVersion:
    """Parse a semantic version string."""
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
    match = re.match(pattern, version)
    if not match:
        raise ValueError(f"Invalid version string: {version}")
    
    return SemanticVersion(
        major=int(match.group(1)),
        minor=int(match.group(2)),
        patch=int(match.group(3)),
        prerelease=match.group(4),
        build=match.group(5),
    )


def compare_versions(a: str, b: str) -> int:
    """Compare two versions. Returns: -1 if a < b, 0 if a == b, 1 if a > b."""
    va = parse_version(a)
    vb = parse_version(b)
    
    if va.major != vb.major:
        return -1 if va.major < vb.major else 1
    if va.minor != vb.minor:
        return -1 if va.minor < vb.minor else 1
    if va.patch != vb.patch:
        return -1 if va.patch < vb.patch else 1
    
    # Prerelease versions have lower precedence
    if va.prerelease and not vb.prerelease:
        return -1
    if not va.prerelease and vb.prerelease:
        return 1
    
    return 0


def is_compatible(client_version: str, server_version: str) -> bool:
    """Check if versions are compatible (same major version)."""
    client = parse_version(client_version)
    server = parse_version(server_version)
    return client.major == server.major


def get_version_headers() -> Dict[str, str]:
    """Get version headers for API requests."""
    return {
        "x-motionos-sdk-version": SDK_VERSION,
        "x-motionos-sdk": "python",
    }


def get_sdk_version() -> str:
    """Get current SDK version."""
    return SDK_VERSION


@dataclass
class VersionInfo:
    """Version info for debugging."""
    sdk: str
    sdk_language: str
    parsed: SemanticVersion


def get_version_info() -> VersionInfo:
    """Get full version info."""
    return VersionInfo(
        sdk=SDK_VERSION,
        sdk_language="python",
        parsed=parse_version(SDK_VERSION),
    )
