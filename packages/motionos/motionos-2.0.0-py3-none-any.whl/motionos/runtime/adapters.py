"""
MotionOS SDK - Runtime Adapters

Platform-specific adapters for different environments.
"""

from typing import Dict, Any
from motionos.runtime.detection import detect_runtime, is_serverless, RuntimeEnvironment


def get_default_timeout() -> Dict[str, float]:
    """Get default timeout configuration for current platform."""
    env = detect_runtime()
    
    # Serverless needs conservative timeouts
    if is_serverless():
        return {
            "ingest": 10.0,
            "retrieve": 5.0,
            "default": 8.0,
        }
    
    # Standard: longer timeouts OK
    return {
        "ingest": 12.0,
        "retrieve": 6.0,
        "default": 10.0,
    }


def get_default_retry() -> Dict[str, Any]:
    """Get default retry configuration for current platform."""
    env = detect_runtime()
    
    # Serverless: fewer retries, shorter delays
    if is_serverless():
        return {
            "attempts": 2,
            "backoff_ms": 300,
            "max_backoff_ms": 3000,
        }
    
    # Standard: more generous retry
    return {
        "attempts": 3,
        "backoff_ms": 500,
        "max_backoff_ms": 10000,
    }


def create_platform_config() -> Dict[str, Any]:
    """Create platform-optimized configuration."""
    return {
        "timeout": get_default_timeout(),
        "retry": get_default_retry(),
        "environment": detect_runtime().value,
    }


def get_http_client_class():
    """Get appropriate HTTP client class for current platform."""
    env = detect_runtime()
    
    # For serverless, prefer httpx with connection pooling disabled
    # to avoid issues with frozen connections
    if is_serverless():
        try:
            import httpx
            return httpx.AsyncClient
        except ImportError:
            pass
    
    # Default: use available client
    try:
        import httpx
        return httpx.AsyncClient
    except ImportError:
        try:
            import aiohttp
            return aiohttp.ClientSession
        except ImportError:
            raise ImportError("No HTTP client available. Install httpx or aiohttp.")


def should_use_keep_alive() -> bool:
    """Check if keep-alive connections should be used."""
    # Serverless environments should not use keep-alive
    # as connections may be frozen between invocations
    return not is_serverless()


def get_connection_pool_size() -> int:
    """Get recommended connection pool size."""
    env = detect_runtime()
    
    if is_serverless():
        return 1  # Minimal pooling for serverless
    
    return 10  # Standard pooling
