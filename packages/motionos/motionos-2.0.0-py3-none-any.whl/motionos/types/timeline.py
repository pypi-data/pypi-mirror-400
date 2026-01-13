"""
MotionOS SDK - Timeline Types

Types for timeline and version operations.
"""

from dataclasses import dataclass, field
from typing import TypedDict, Optional, List, Literal


# Timeline walk direction
TimelineDirection = Literal["backward", "forward", "both"]

# Edge types in the timeline graph
TimelineEdgeType = Literal["version", "cause", "effect", "supersedes"]


class TimelineWalkOptions(TypedDict, total=False):
    """Options for timeline edge walking."""
    version_id: str  # Required: starting version
    direction: TimelineDirection
    max_depth: int
    max_results: int
    edge_types: List[str]


@dataclass
class TimelineNode:
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
    metadata: Optional[dict] = None


@dataclass
class TimelineEdge:
    """An edge in a timeline walk result."""
    from_version_id: str
    to_version_id: str
    edge_type: str
    depth: int


@dataclass
class TimelineWalkResult:
    """Result of a timeline walk operation."""
    start_version_id: str
    nodes: List[TimelineNode]
    edges: List[TimelineEdge]
    depth: int
    total_visited: int
    truncated: bool = False


@dataclass
class ValidityResult:
    """Result of a version validity check."""
    version_id: str
    is_valid: bool
    reason: str
    superseded_by: List[str]
    latest_in_chain: str
    confidence_score: float
    age_hours: float


@dataclass
class LineageVersion:
    """Version in a lineage result."""
    version_id: str
    version: int
    summary: str
    created_at: str
    is_root: bool = False
    is_current: bool = False


@dataclass
class LineageResult:
    """Result of a lineage query."""
    version_id: str
    ancestors: List[LineageVersion]
    descendants: List[LineageVersion]
    root_version: str
    current_version: str
    total_versions: int = 0


@dataclass
class VersionInfo:
    """Version information for list operations."""
    id: str
    memory_id: str
    version: int
    content: str
    summary: str
    created_at: str
    is_current: bool = False


@dataclass
class RollbackOptions:
    """Rollback options."""
    memory_id: str
    version_id: str


@dataclass
class RollbackResult:
    """Rollback result."""
    ok: bool
    current_version_id: Optional[str] = None
    message: Optional[str] = None


# Timeline operation limits
class TimelineLimits:
    DEFAULT_MAX_DEPTH = 5
    MAX_MAX_DEPTH = 20
    DEFAULT_MAX_RESULTS = 20
    MAX_MAX_RESULTS = 100


TIMELINE_LIMITS = TimelineLimits()
