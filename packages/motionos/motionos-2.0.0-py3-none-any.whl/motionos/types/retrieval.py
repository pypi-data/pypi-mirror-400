"""
MotionOS SDK - Retrieval Types

Types for intent-based memory retrieval operations.
"""

from dataclasses import dataclass, field
from typing import TypedDict, Optional, List, Union, Dict, Any, Literal
from datetime import datetime
from enum import Enum

from motionos.types.memory import MemoryItem


class RetrievalIntent(str, Enum):
    """
    Retrieval intent types.
    
    The SDK exposes intent-based retrieval, not raw search.
    Developers express WHAT they need, not HOW to search.
    """
    EXPLORATION = "exploration"  # Broad context gathering
    ANSWER = "answer"            # Precise recall for Q&A
    DECISION = "decision"        # Authoritative memory for decisions
    TIMELINE = "timeline"        # Chronological reasoning
    INJECT = "inject"            # LLM-ready context injection


# Retrieval output format
RetrievalFormat = Literal["inject", "raw"]

# Policy preset names
PolicyPreset = Literal["default", "decision", "timeline", "audit", "exploration"]


class ScoringWeights(TypedDict, total=False):
    """Custom scoring weight overrides."""
    semantic: float   # 0-1
    recency: float    # 0-1
    importance: float # 0-1
    frequency: float  # 0-1


class PolicyConfig(TypedDict, total=False):
    """Policy configuration for retrieval."""
    preset: Optional[str]
    auto_detect: Optional[bool]
    weights: Optional[ScoringWeights]


class RetrieveFilters(TypedDict, total=False):
    """Filter configuration for retrieval."""
    tags: Optional[List[str]]
    types: Optional[List[str]]
    source: Optional[str]
    after_time: Optional[Union[str, datetime]]
    before_time: Optional[Union[str, datetime]]
    latest_only: Optional[bool]


class RetrieveOptions(TypedDict, total=False):
    """Full retrieve options object."""
    
    # Basic options
    query: Optional[str]
    agent_id: Optional[str]
    scope: Optional[str]
    format: Optional[RetrievalFormat]
    limit: Optional[int]
    
    # Filters
    filters: Optional[RetrieveFilters]
    tags: Optional[List[str]]      # Shorthand for filters.tags
    types: Optional[List[str]]     # Shorthand for filters.types
    
    # Timeline
    timeline_version_id: Optional[str]
    
    # Intent & Intelligence
    intent: Optional[RetrievalIntent]
    policy: Optional[PolicyConfig]
    domain: Optional[str]
    explain: Optional[bool]


# Retrieve input - accepts string query or options dict
RetrieveInput = Union[str, RetrieveOptions]


@dataclass
class RetrievalMeta:
    """Retrieval result metadata."""
    mode: str = "retrieval"
    format: str = "inject"
    limit: int = 5
    query: Optional[str] = None
    intent: Optional[str] = None
    policy_used: Optional[str] = None


@dataclass
class RetrievalResult:
    """Retrieval result."""
    
    # Core data
    context: str
    items: List[MemoryItem]
    reasoning: str
    meta: Dict[str, Any]
    
    # Intelligence features
    policy_used: Optional[str] = None
    explanation: Optional[Any] = None  # RetrievalExplanation
    confidence: Optional[float] = None


@dataclass
class DomainInfo:
    """Domain adapter information."""
    name: str
    description: str
    default_policy: str
    type_priorities: List[str]
    semantic_endpoints_count: int


@dataclass
class PolicyInfo:
    """Policy preset information."""
    name: str
    description: str
    rules: List[str]
    priority: int


# Retrieval validation limits
class RetrievalLimits:
    MIN_LIMIT = 1
    MAX_LIMIT = 50
    DEFAULT_LIMIT = 5
    MAX_QUERY_LENGTH = 10_000


RETRIEVAL_LIMITS = RetrievalLimits()
