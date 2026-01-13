"""
MotionOS SDK - Configuration Types

Types for SDK configuration and initialization.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from motionos.types.common import Logger


# SDK Version - updated on each release
SDK_VERSION = "2.0.0"

# Base URL - HARDCODED per specification
BASE_URL = "https://api.digicrest.site"


@dataclass(frozen=True)
class TimeoutConfig:
    """Timeout configuration for different operation types."""
    
    ingest: float = 12.0   # 12 seconds for ingest
    retrieve: float = 6.0  # 6 seconds for retrieve
    default: float = 10.0  # 10 seconds for other operations


@dataclass(frozen=True)
class RetryConfig:
    """Retry configuration for handling transient failures."""
    
    attempts: int = 2
    backoff_ms: int = 300
    max_backoff_ms: int = 5000
    idempotent_only: bool = True


@dataclass(frozen=True)
class TelemetryConfig:
    """Telemetry configuration (opt-in)."""
    
    enabled: bool = False
    endpoint: Optional[str] = None
    sample_rate: float = 1.0


@dataclass
class SimulationConfig:
    """Simulation mode configuration for testing."""
    
    enabled: bool = True  # MUST be explicit
    latency_ms: int = 50
    error_rate: float = 0.0
    rate_limit_after: Optional[int] = None
    responses: Optional[Dict[str, Any]] = None


@dataclass
class SDKConfiguration:
    """Full SDK configuration options."""
    
    # Required
    api_key: str
    project_id: str
    
    # Optional - timeouts
    timeout: Optional[TimeoutConfig] = None
    
    # Optional - retry
    retry: Optional[RetryConfig] = None
    
    # Optional - debugging
    debug: bool = False
    logger: Optional[Logger] = None
    
    # Optional - default agent
    default_agent: Optional[str] = None
    
    # Optional - telemetry
    telemetry: Optional[TelemetryConfig] = None
    
    # Optional - simulation mode
    simulation: Optional[SimulationConfig] = None


@dataclass(frozen=True)
class ResolvedConfiguration:
    """Resolved/normalized configuration (all fields have values)."""
    
    api_key: str
    project_id: str
    base_url: str
    timeout: TimeoutConfig
    retry: RetryConfig
    debug: bool
    default_agent: Optional[str]
    telemetry: Optional[TelemetryConfig]
    simulation: Optional[SimulationConfig]
    sdk_version: str
    key_type: str


@dataclass(frozen=True)
class SDKConfigInfo:
    """SDK configuration for debugging/introspection."""
    
    base_url: str
    project_id: str
    timeout: TimeoutConfig
    retry: RetryConfig
    debug: bool
    sdk_version: str
    key_type: str
    simulation_mode: bool


# Default configurations
DEFAULT_TIMEOUT = TimeoutConfig()
DEFAULT_RETRY = RetryConfig()
