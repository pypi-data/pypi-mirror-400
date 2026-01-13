"""
MotionOS SDK - Runtime Environment Detection

Detects the runtime environment for appropriate SDK behavior.
"""

import sys
import os
from typing import Optional
from enum import Enum


class RuntimeEnvironment(str, Enum):
    """Runtime environment types."""
    SYNC = "sync"
    ASYNC = "async"
    SERVERLESS = "serverless"
    UNKNOWN = "unknown"


class PlatformType(str, Enum):
    """Platform types."""
    CPYTHON = "cpython"
    PYPY = "pypy"
    JYTHON = "jython"
    IRONPYTHON = "ironpython"
    UNKNOWN = "unknown"


def detect_platform() -> PlatformType:
    """Detect the Python implementation/platform."""
    impl = sys.implementation.name.lower()
    
    if impl == "cpython":
        return PlatformType.CPYTHON
    elif impl == "pypy":
        return PlatformType.PYPY
    elif "jython" in impl:
        return PlatformType.JYTHON
    elif "iron" in impl:
        return PlatformType.IRONPYTHON
    
    return PlatformType.UNKNOWN


def detect_environment() -> RuntimeEnvironment:
    """
    Detect the runtime environment.
    
    Returns:
        RuntimeEnvironment enum value
    """
    # Check for AWS Lambda
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return RuntimeEnvironment.SERVERLESS
    
    # Check for Google Cloud Functions
    if os.environ.get("FUNCTION_NAME") or os.environ.get("K_SERVICE"):
        return RuntimeEnvironment.SERVERLESS
    
    # Check for Azure Functions
    if os.environ.get("WEBSITE_SITE_NAME") and os.environ.get("FUNCTIONS_WORKER_RUNTIME"):
        return RuntimeEnvironment.SERVERLESS
    
    # Check for Vercel
    if os.environ.get("VERCEL"):
        return RuntimeEnvironment.SERVERLESS
    
    # Check if running in async context
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop is not None:
                return RuntimeEnvironment.ASYNC
        except RuntimeError:
            pass  # No running loop
    except ImportError:
        pass
    
    return RuntimeEnvironment.SYNC


def is_serverless() -> bool:
    """Check if running in a serverless environment."""
    return detect_environment() == RuntimeEnvironment.SERVERLESS


def is_async_context() -> bool:
    """Check if running in an async context."""
    try:
        import asyncio
        asyncio.get_running_loop()
        return True
    except (RuntimeError, ImportError):
        return False


def get_python_version() -> str:
    """Get Python version as string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_runtime_info() -> dict:
    """
    Get comprehensive runtime information.
    
    Returns:
        Dictionary with runtime details
    """
    return {
        "python_version": get_python_version(),
        "platform": detect_platform().value,
        "environment": detect_environment().value,
        "is_serverless": is_serverless(),
        "implementation": sys.implementation.name,
        "os": os.name,
    }


def check_minimum_python_version(major: int = 3, minor: int = 8) -> bool:
    """
    Check if Python version meets minimum requirements.
    
    Args:
        major: Minimum major version (default: 3)
        minor: Minimum minor version (default: 8)
    
    Returns:
        True if version is sufficient
    """
    return sys.version_info >= (major, minor)
