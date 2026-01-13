"""
MotionOS SDK - Runtime Detection

Comprehensive platform and runtime detection for Python.
"""

import os
import sys
import asyncio
from typing import Optional, TypedDict
from dataclasses import dataclass
from enum import Enum


class RuntimeEnvironment(str, Enum):
    """Supported runtime environments."""
    STANDARD = "standard"
    AWS_LAMBDA = "aws-lambda"
    GOOGLE_CLOUD_FUNCTIONS = "google-cloud-functions"
    AZURE_FUNCTIONS = "azure-functions"
    JUPYTER = "jupyter"
    IPYTHON = "ipython"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    UNKNOWN = "unknown"


@dataclass
class RuntimeCapabilities:
    """Runtime capabilities."""
    has_async: bool
    has_env: bool
    has_fs: bool
    is_serverless: bool
    max_execution_time: Optional[int]  # milliseconds, None = unlimited
    supports_streaming: bool


@dataclass 
class RuntimeInfo:
    """Full runtime information."""
    environment: RuntimeEnvironment
    capabilities: RuntimeCapabilities
    python_version: str
    platform: str
    is_async_context: bool


def detect_runtime() -> RuntimeEnvironment:
    """Detect the current runtime environment."""
    
    # AWS Lambda
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return RuntimeEnvironment.AWS_LAMBDA
    
    # Google Cloud Functions
    if os.environ.get("FUNCTION_NAME") and os.environ.get("GCP_PROJECT"):
        return RuntimeEnvironment.GOOGLE_CLOUD_FUNCTIONS
    
    # Azure Functions
    if os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT"):
        return RuntimeEnvironment.AZURE_FUNCTIONS
    
    # Kubernetes
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return RuntimeEnvironment.KUBERNETES
    
    # Docker
    if _is_docker():
        return RuntimeEnvironment.DOCKER
    
    # Jupyter
    if _is_jupyter():
        return RuntimeEnvironment.JUPYTER
    
    # IPython
    if _is_ipython():
        return RuntimeEnvironment.IPYTHON
    
    # Standard Python
    return RuntimeEnvironment.STANDARD


def _is_docker() -> bool:
    """Check if running in Docker."""
    # Check for .dockerenv
    if os.path.exists("/.dockerenv"):
        return True
    
    # Check cgroups
    try:
        with open("/proc/1/cgroup", "r") as f:
            return "docker" in f.read()
    except (IOError, FileNotFoundError):
        pass
    
    return False


def _is_jupyter() -> bool:
    """Check if running in Jupyter."""
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            return "zmqshell" in str(type(ipython))
    except (ImportError, NameError):
        pass
    return False


def _is_ipython() -> bool:
    """Check if running in IPython."""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except (ImportError, NameError):
        return False


def is_async_context() -> bool:
    """Check if we're currently in an async context."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def get_runtime_capabilities(env: RuntimeEnvironment) -> RuntimeCapabilities:
    """Get capabilities for a runtime environment."""
    base = RuntimeCapabilities(
        has_async=True,
        has_env=True,
        has_fs=True,
        is_serverless=False,
        max_execution_time=None,
        supports_streaming=True,
    )
    
    if env == RuntimeEnvironment.AWS_LAMBDA:
        return RuntimeCapabilities(
            has_async=True,
            has_env=True,
            has_fs=True,  # /tmp available
            is_serverless=True,
            max_execution_time=900000,  # 15 min
            supports_streaming=False,  # Limited streaming
        )
    
    if env == RuntimeEnvironment.GOOGLE_CLOUD_FUNCTIONS:
        return RuntimeCapabilities(
            has_async=True,
            has_env=True,
            has_fs=True,
            is_serverless=True,
            max_execution_time=540000,  # 9 min
            supports_streaming=False,
        )
    
    if env == RuntimeEnvironment.AZURE_FUNCTIONS:
        return RuntimeCapabilities(
            has_async=True,
            has_env=True,
            has_fs=True,
            is_serverless=True,
            max_execution_time=600000,  # 10 min
            supports_streaming=False,
        )
    
    return base


def get_runtime_info() -> RuntimeInfo:
    """Get full runtime information."""
    env = detect_runtime()
    capabilities = get_runtime_capabilities(env)
    
    return RuntimeInfo(
        environment=env,
        capabilities=capabilities,
        python_version=sys.version,
        platform=sys.platform,
        is_async_context=is_async_context(),
    )


def is_serverless() -> bool:
    """Check if running in a serverless environment."""
    env = detect_runtime()
    return env in (
        RuntimeEnvironment.AWS_LAMBDA,
        RuntimeEnvironment.GOOGLE_CLOUD_FUNCTIONS,
        RuntimeEnvironment.AZURE_FUNCTIONS,
    )


def is_interactive() -> bool:
    """Check if running in interactive mode (Jupyter/IPython)."""
    env = detect_runtime()
    return env in (RuntimeEnvironment.JUPYTER, RuntimeEnvironment.IPYTHON)
