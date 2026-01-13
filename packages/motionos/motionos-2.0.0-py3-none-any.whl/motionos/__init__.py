"""
MotionOS Python SDK v2.0.0

Official Python SDK for MotionOS - Memory OS for AI Agents.
Works in Python 3.8+, supports both sync and async operations.

Usage:
    from motionos import MotionOS
    
    client = MotionOS(
        api_key="sb_secret_xxx",
        project_id="your-project-id"
    )
    
    # Store memory
    result = client.ingest("User prefers dark mode")
    
    # Retrieve context
    result = client.retrieve("user preferences")
    print(result.context)  # Ready for LLM
    
Simulation Mode:
    from motionos.simulation import MockMotionOS, Scenarios
    
    mock = MockMotionOS.create(Scenarios.happy_path())
    mock.ingest("test")  # No network calls
"""

__version__ = "2.0.0"

# ============================================================================
# Main Clients (from existing files - these still work)
# ============================================================================

from motionos.client import MotionOS
from motionos.async_client import AsyncMotionOS

# ============================================================================
# Errors (from new modular structure)
# ============================================================================

from motionos.errors.base import (
    MotionOSError,
    AuthenticationError,
    InvalidAPIKeyError,
    ForbiddenError,
    ProjectMismatchError,
    RateLimitError,
    ValidationError,
    InvalidRequestError,
    EngineUnavailableError,
    TimeoutError,
    NetworkError,
    NotFoundError,
)
from motionos.errors.factory import is_retryable, is_motionos_error

# ============================================================================
# Configuration (from new modular structure)
# ============================================================================

from motionos.config.defaults import SDK_VERSION, BASE_URL
from motionos.config.validator import ConfigurationError, validate_api_key
from motionos.config.manager import mask_api_key

# ============================================================================
# Types (re-export from new modular structure)
# ============================================================================

from motionos.types.config import (
    TimeoutConfig,
    RetryConfig,
    SimulationConfig,
    SDKConfiguration,
    SDKConfigInfo,
)
from motionos.types.memory import (
    IngestOptions,
    IngestResult,
    MemoryItem,
    BatchIngestOptions,
    BatchIngestResult,
    MEMORY_LIMITS,
)
from motionos.types.retrieval import (
    RetrievalIntent,
    RetrieveOptions,
    RetrievalResult,
    PolicyConfig,
    DomainInfo,
    PolicyInfo,
    RETRIEVAL_LIMITS,
)
from motionos.types.timeline import (
    TimelineWalkOptions,
    TimelineWalkResult,
    ValidityResult,
    LineageResult,
    VersionInfo,
    RollbackOptions,
    RollbackResult,
    TIMELINE_LIMITS,
)
from motionos.types.explanation import (
    RetrievalExplanation,
    SelectionExplanation,
    QueryAnalysis,
    CONFIDENCE_THRESHOLDS,
)

# ============================================================================
# Simulation (from new modular structure)
# ============================================================================

# Import simulation lazily to avoid circular imports
def _get_simulation():
    from motionos.simulation import MockMotionOS, Scenarios, MockData
    return MockMotionOS, Scenarios, MockData

# ============================================================================
# Utilities (from existing files)
# ============================================================================

from motionos.utils import create_client_from_env

# ============================================================================
# Type aliases for backward compatibility
# ============================================================================

IngestInput = str  # Union[str, IngestOptions]
RetrieveInput = str  # Union[str, RetrieveOptions]

# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Version
    "__version__",
    # Clients
    "MotionOS",
    "AsyncMotionOS",
    # Errors
    "MotionOSError",
    "AuthenticationError",
    "InvalidAPIKeyError",
    "ForbiddenError",
    "ProjectMismatchError",
    "RateLimitError",
    "ValidationError",
    "InvalidRequestError",
    "EngineUnavailableError",
    "TimeoutError",
    "NetworkError",
    "NotFoundError",
    "ConfigurationError",
    "is_retryable",
    "is_motionos_error",
    # Configuration
    "SDK_VERSION",
    "BASE_URL",
    "validate_api_key",
    "mask_api_key",
    "TimeoutConfig",
    "RetryConfig",
    "SimulationConfig",
    "SDKConfiguration",
    "SDKConfigInfo",
    # Memory Types
    "IngestInput",
    "IngestOptions",
    "IngestResult",
    "MemoryItem",
    "BatchIngestOptions",
    "BatchIngestResult",
    "MEMORY_LIMITS",
    # Retrieval Types
    "RetrievalIntent",
    "RetrieveInput",
    "RetrieveOptions",
    "RetrievalResult",
    "PolicyConfig",
    "DomainInfo",
    "PolicyInfo",
    "RETRIEVAL_LIMITS",
    # Timeline Types
    "TimelineWalkOptions",
    "TimelineWalkResult",
    "ValidityResult",
    "LineageResult",
    "VersionInfo",
    "RollbackOptions",
    "RollbackResult",
    "TIMELINE_LIMITS",
    # Explanation Types
    "RetrievalExplanation",
    "SelectionExplanation",
    "QueryAnalysis",
    "CONFIDENCE_THRESHOLDS",
    # Utilities
    "create_client_from_env",
]
