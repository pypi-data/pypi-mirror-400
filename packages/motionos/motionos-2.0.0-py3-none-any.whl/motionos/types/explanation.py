"""
MotionOS SDK - Explanation Types

Types for explainability and reasoning metadata.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from enum import Enum


class SelectionSignal(str, Enum):
    """Signal types that contribute to memory selection."""
    SEMANTIC = "semantic"
    RECENCY = "recency"
    IMPORTANCE = "importance"
    FREQUENCY = "frequency"
    TYPE = "type"
    TAG = "tag"
    SOURCE = "source"
    TIMELINE = "timeline"


# Impact level type
ImpactLevel = Literal["high", "medium", "low"]


@dataclass
class SelectionFactor:
    """Contributing factor to memory selection."""
    signal: str
    impact: str  # ImpactLevel
    value: float
    contribution: float
    description: Optional[str] = None


@dataclass
class SelectionExplanation:
    """Explanation for why a specific item was selected."""
    item_id: str
    final_score: float
    rank: int
    dominant_signal: str
    top_reasons: List[SelectionFactor]
    summary: str


@dataclass
class QueryAnalysis:
    """Query analysis results."""
    original_query: str
    detected_intent: str
    intent_confidence: float
    key_terms: List[str]
    expanded_query: Optional[str] = None


@dataclass
class RetrievalExplanation:
    """Full retrieval explanation."""
    
    # Query understanding
    query_analysis: QueryAnalysis
    
    # Policy information
    policy_used: str
    policy_reason: str
    domain_used: Optional[str] = None
    
    # Selection statistics
    total_considered: int = 0
    total_returned: int = 0
    total_suppressed: int = 0
    suppression_reasons: Optional[List[str]] = None
    
    # Per-item explanations
    selections: List[SelectionExplanation] = field(default_factory=list)
    
    # Confidence
    overall_confidence: float = 0.0
    confidence_factors: List[str] = field(default_factory=list)
    
    # Human readable
    summary: str = ""
    suggestions: Optional[List[str]] = None


# Confidence thresholds
class ConfidenceThresholds:
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.3


CONFIDENCE_THRESHOLDS = ConfidenceThresholds()
