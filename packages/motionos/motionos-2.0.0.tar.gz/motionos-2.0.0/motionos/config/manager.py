"""
MotionOS SDK - Configuration Manager

Manages SDK configuration with normalization.
"""

from typing import Optional
from motionos.config.defaults import (
    SDK_VERSION,
    BASE_URL,
    DEFAULT_INGEST_TIMEOUT,
    DEFAULT_RETRIEVE_TIMEOUT,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_BACKOFF_MS,
    DEFAULT_MAX_BACKOFF_MS,
)
from motionos.config.validator import validate_configuration, get_key_type


def resolve_configuration(config):
    """
    Normalize and resolve configuration.
    
    Fills in defaults and validates the configuration.
    """
    from motionos.types.config import (
        ResolvedConfiguration,
        TimeoutConfig,
        RetryConfig,
        DEFAULT_TIMEOUT as TIMEOUT_CONFIG,
        DEFAULT_RETRY as RETRY_CONFIG,
    )
    
    # Validate first
    validate_configuration(config)
    
    # Get key type
    key_type = get_key_type(config.api_key)
    
    # Resolve timeout
    timeout = config.timeout if config.timeout is not None else TIMEOUT_CONFIG
    
    # Resolve retry
    retry = config.retry if config.retry is not None else RETRY_CONFIG
    
    return ResolvedConfiguration(
        api_key=config.api_key.strip(),
        project_id=config.project_id.strip(),
        base_url=BASE_URL,  # Always hardcoded
        timeout=timeout,
        retry=retry,
        debug=config.debug,
        default_agent=config.default_agent,
        telemetry=config.telemetry,
        simulation=config.simulation,
        sdk_version=SDK_VERSION,
        key_type=key_type,
    )


def get_config_info(config) -> dict:
    """Get configuration info for debugging."""
    from motionos.types.config import SDKConfigInfo
    
    key_type = get_key_type(config.api_key)
    
    return SDKConfigInfo(
        base_url=BASE_URL,
        project_id=config.project_id,
        timeout=config.timeout,
        retry=config.retry,
        debug=config.debug,
        sdk_version=SDK_VERSION,
        key_type=key_type,
        simulation_mode=config.simulation.enabled if config.simulation else False,
    )


def mask_api_key(api_key: str) -> str:
    """Mask API key for logging (never log full key)."""
    if not api_key or len(api_key) < 20:
        return "***"
    
    # Determine prefix
    if api_key.startswith("sb_secret_"):
        prefix = "sb_secret_"
    elif api_key.startswith("sb_publishable_"):
        prefix = "sb_publishable_"
    else:
        prefix = ""
    
    content = api_key[len(prefix):]
    if len(content) <= 8:
        return f"{prefix}***"
    
    return f"{prefix}{content[:4]}...{content[-4:]}"
