"""
MotionOS SDK - Types Package

Central hub for all type definitions.
Re-exports all types from submodules for easy importing.
"""

# Common types
from motionos.types.common import (
    Logger,
    OperationType,
    EnvironmentType,
    ApiKeyType,
    ApiKeyRole,
    HttpMethod,
)

# Configuration types
from motionos.types.config import (
    SDK_VERSION,
    BASE_URL,
    TimeoutConfig,
    RetryConfig,
    TelemetryConfig,
    SimulationConfig,
    SDKConfiguration,
    ResolvedConfiguration,
    SDKConfigInfo,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY,
)

# Memory types
from motionos.types.memory import (
    MemoryScope,
    MemoryType,
    MemoryEdge,
    IngestOptions,
    IngestInput,
    IngestResult,
    MemoryItem,
    BatchIngestOptions,
    BatchIngestResultItem,
    BatchIngestResult,
    MemoryLimits,
    MEMORY_LIMITS,
)

# Retrieval types
from motionos.types.retrieval import (
    RetrievalIntent,
    RetrievalFormat,
    PolicyPreset,
    ScoringWeights,
    PolicyConfig,
    RetrieveFilters,
    RetrieveOptions,
    RetrieveInput,
    RetrievalMeta,
    RetrievalResult,
    DomainInfo,
    PolicyInfo,
    RetrievalLimits,
    RETRIEVAL_LIMITS,
)

# Timeline types
from motionos.types.timeline import (
    TimelineDirection,
    TimelineEdgeType,
    TimelineWalkOptions,
    TimelineNode,
    TimelineEdge,
    TimelineWalkResult,
    ValidityResult,
    LineageVersion,
    LineageResult,
    VersionInfo,
    RollbackOptions,
    RollbackResult,
    TimelineLimits,
    TIMELINE_LIMITS,
)

# Explanation types
from motionos.types.explanation import (
    SelectionSignal,
    ImpactLevel,
    SelectionFactor,
    SelectionExplanation,
    QueryAnalysis,
    RetrievalExplanation,
    ConfidenceThresholds,
    CONFIDENCE_THRESHOLDS,
)

# Backward compatibility alias
SDKConfig = SDKConfiguration

__all__ = [
    # Common
    "Logger",
    "OperationType",
    "EnvironmentType",
    "ApiKeyType",
    "ApiKeyRole",
    "HttpMethod",
    # Config
    "SDK_VERSION",
    "BASE_URL",
    "TimeoutConfig",
    "RetryConfig",
    "TelemetryConfig",
    "SimulationConfig",
    "SDKConfiguration",
    "SDKConfig",  # Alias
    "ResolvedConfiguration",
    "SDKConfigInfo",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRY",
    # Memory
    "MemoryScope",
    "MemoryType",
    "MemoryEdge",
    "IngestOptions",
    "IngestInput",
    "IngestResult",
    "MemoryItem",
    "BatchIngestOptions",
    "BatchIngestResultItem",
    "BatchIngestResult",
    "MemoryLimits",
    "MEMORY_LIMITS",
    # Retrieval
    "RetrievalIntent",
    "RetrievalFormat",
    "PolicyPreset",
    "ScoringWeights",
    "PolicyConfig",
    "RetrieveFilters",
    "RetrieveOptions",
    "RetrieveInput",
    "RetrievalMeta",
    "RetrievalResult",
    "DomainInfo",
    "PolicyInfo",
    "RetrievalLimits",
    "RETRIEVAL_LIMITS",
    # Timeline
    "TimelineDirection",
    "TimelineEdgeType",
    "TimelineWalkOptions",
    "TimelineNode",
    "TimelineEdge",
    "TimelineWalkResult",
    "ValidityResult",
    "LineageVersion",
    "LineageResult",
    "VersionInfo",
    "RollbackOptions",
    "RollbackResult",
    "TimelineLimits",
    "TIMELINE_LIMITS",
    # Explanation
    "SelectionSignal",
    "ImpactLevel",
    "SelectionFactor",
    "SelectionExplanation",
    "QueryAnalysis",
    "RetrievalExplanation",
    "ConfidenceThresholds",
    "CONFIDENCE_THRESHOLDS",
]
