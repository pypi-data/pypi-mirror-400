"""
MotionOS SDK - Type Definitions

Type hints and data structures for the MotionOS SDK.
"""

from typing import TypedDict, Optional, List, Union, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime


# Ingest types
IngestInput = Union[str, "IngestOptions"]


class IngestOptions(TypedDict, total=False):
    """Options for ingesting memory."""

    raw_text: str
    summary: Optional[str]
    agent_id: Optional[str]
    scope: Optional[str]
    type: Optional[str]
    tags: Optional[List[str]]
    source: Optional[str]
    event_time: Optional[Union[str, datetime]]
    edges: Optional[List[Dict[str, Any]]]
    importance: Optional[float]
    frequency: Optional[float]
    recency: Optional[float]


@dataclass
class IngestResult:
    """Result from ingest operation."""

    id: str
    summary: str
    version_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Intelligence Types
# ============================================================================

class PolicyConfig(TypedDict, total=False):
    """Policy configuration for retrieval."""
    
    preset: Optional[str]  # 'default', 'decision', 'timeline', 'audit'
    auto_detect: Optional[bool]  # Enable intent auto-detection
    weights: Optional[Dict[str, float]]  # Custom weight overrides


@dataclass
class SelectionExplanation:
    """Explanation for why an item was selected."""
    
    item_id: str
    final_score: float
    rank: int
    dominant_signal: str
    top_reasons: List[Dict[str, Any]]
    summary: str


@dataclass
class QueryAnalysis:
    """Analysis of the retrieval query."""
    
    original_query: str
    detected_intent: str
    intent_confidence: float
    key_terms: List[str]


@dataclass
class RetrievalExplanation:
    """Full explanation of retrieval decisions."""
    
    query_analysis: QueryAnalysis
    policy_used: str
    policy_reason: str
    total_considered: int
    total_returned: int
    total_suppressed: int
    selections: List[SelectionExplanation]
    overall_confidence: float
    confidence_factors: List[str]
    summary: str


# Retrieve types
RetrieveInput = Union[str, "RetrieveOptions"]


class RetrieveOptions(TypedDict, total=False):
    """Options for retrieving memory."""

    query: Optional[str]
    agent_id: Optional[str]
    scope: Optional[str]
    mode: Literal["inject", "raw"]
    limit: Optional[int]
    tags: Optional[List[str]]
    types: Optional[List[str]]
    source: Optional[str]
    after_time: Optional[Union[str, datetime]]
    before_time: Optional[Union[str, datetime]]
    latest_only: Optional[bool]
    timeline_version_id: Optional[str]
    # Intelligence features
    policy: Optional[PolicyConfig]
    domain: Optional[str]  # 'contact_center', 'agent_dev', 'product_planning'
    explain: Optional[bool]  # Return detailed explanation


@dataclass
class MemoryItem:
    """A single memory item."""

    id: str
    summary: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str = ""
    updated_at: str = ""
    score: float = 0.0


@dataclass
class RetrievalResult:
    """Result from retrieve operation."""

    context: str
    items: List[MemoryItem]
    reasoning: str
    meta: Dict[str, Any]
    # Intelligence features
    policy_used: Optional[str] = None
    explanation: Optional[RetrievalExplanation] = None
    confidence: Optional[float] = None


# Rollback types
@dataclass
class RollbackOptions:
    """Options for rollback operation."""

    memory_id: str
    version_id: str


@dataclass
class RollbackResult:
    """Result from rollback operation."""

    ok: bool


# Batch ingest types
@dataclass
class BatchIngestOptions:
    """Options for batch ingest operation."""

    items: List[IngestOptions]
    chunk_size: Optional[int] = None


@dataclass
class BatchIngestResultItem:
    """Result item from batch ingest."""

    id: Optional[str] = None
    error: Optional[Exception] = None


@dataclass
class BatchIngestResult:
    """Result from batch ingest operation."""

    results: List[BatchIngestResultItem]


# Version types
@dataclass
class VersionInfo:
    """Version information for a memory."""

    id: str
    memory_id: str
    version: int
    content: str
    summary: str
    created_at: str


# ============================================================================
# Timeline Types
# ============================================================================

class TimelineWalkOptions(TypedDict, total=False):
    """Options for timeline edge walking."""
    
    version_id: str  # Required: starting version
    direction: Literal["backward", "forward", "both"]
    max_depth: Optional[int]
    max_results: Optional[int]
    edge_types: Optional[List[str]]


@dataclass
class TimelineWalkNode:
    """A node in a timeline walk result."""
    
    version_id: str
    chunk_id: str
    summary: str
    content: str
    created_at: str
    depth: int
    decay_score: float
    is_obsolete: bool = False
    is_superseded: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineEdge:
    """An edge in a timeline walk result."""
    
    from_version_id: str
    to_version_id: str
    edge_type: str
    depth: int


@dataclass
class TimelineWalkResult:
    """Result from timeline walk operation."""
    
    start_version_id: str
    nodes: List[TimelineWalkNode]
    edges: List[TimelineEdge]
    depth: int
    total_visited: int
    truncated: bool = False


@dataclass
class ValidityResult:
    """Result from version validity check."""
    
    version_id: str
    is_valid: bool
    reason: str
    superseded_by: List[str]
    latest_in_chain: str
    confidence_score: float
    age_hours: float


@dataclass
class LineageAncestor:
    """Ancestor in lineage result."""
    
    version_id: str
    version: int
    summary: str
    created_at: str
    is_root: bool = False
    is_current: bool = False


@dataclass
class LineageDescendant:
    """Descendant in lineage result."""
    
    version_id: str
    version: int
    summary: str
    created_at: str
    is_current: bool = False


@dataclass
class LineageResult:
    """Result from lineage query."""
    
    version_id: str
    ancestors: List[LineageAncestor]
    descendants: List[LineageDescendant]
    root_version: str
    current_version: str


@dataclass
class DomainInfo:
    """Information about an available domain."""
    
    name: str
    description: str
    default_policy: str
    type_priorities: List[str]
    semantic_endpoints_count: int


@dataclass
class PolicyInfo:
    """Information about an available policy preset."""
    
    name: str
    description: str
    rules: List[str]
    priority: int


# Config types
@dataclass
class TimeoutConfig:
    """Timeout configuration."""

    ingest: float
    retrieve: float
    default: float


@dataclass
class RetryConfig:
    """Retry configuration."""

    attempts: int
    backoff_ms: float


@dataclass
class SDKConfig:
    """SDK configuration."""

    base_url: str
    project_id: str
    timeout: TimeoutConfig
    retry: RetryConfig
    debug: bool
    sdk_version: str

