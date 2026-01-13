"""
MotionOS SDK - Memory Types

Types for memory ingestion operations.
"""

from dataclasses import dataclass, field
from typing import TypedDict, Optional, List, Union, Dict, Any, Literal
from datetime import datetime


# Memory scope types
MemoryScope = Literal["project", "agent", "global"]

# Memory type hints
MemoryType = Literal[
    "decision", "note", "event", "observation",
    "instruction", "preference", "fact", "episode"
]


class MemoryEdge(TypedDict, total=False):
    """Edge definition for causal relationships."""
    to: str  # Target version/memory ID
    type: str  # Edge type: 'causes', 'follows', 'relates', 'supersedes'


class IngestOptions(TypedDict, total=False):
    """Full ingest options object."""
    
    # Required
    raw_text: str
    
    # Optional
    summary: Optional[str]
    agent_id: Optional[str]
    scope: Optional[str]
    type: Optional[str]
    tags: Optional[List[str]]
    source: Optional[str]
    event_time: Optional[Union[str, datetime]]
    edges: Optional[List[MemoryEdge]]
    importance: Optional[float]
    frequency: Optional[float]
    recency: Optional[float]


# Ingest input - accepts string or options dict
IngestInput = Union[str, IngestOptions]


@dataclass
class IngestResult:
    """Result of an ingest operation."""
    
    id: str
    summary: str
    version_id: Optional[str] = None
    deduplicated: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MemoryItem:
    """Memory item representation."""
    
    id: str
    summary: str
    content: str
    score: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    version_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchIngestOptions(TypedDict, total=False):
    """Batch ingest options."""
    items: List[IngestOptions]
    chunk_size: int
    continue_on_error: bool


@dataclass
class BatchIngestResultItem:
    """Individual batch result item."""
    index: int
    id: Optional[str] = None
    error: Optional[Exception] = None


@dataclass
class BatchIngestResult:
    """Batch ingest result."""
    results: List[BatchIngestResultItem]
    success_count: int = 0
    failure_count: int = 0


# Memory validation limits
class MemoryLimits:
    MAX_TEXT_LENGTH = 100_000
    MAX_TAGS = 32
    MAX_TAG_LENGTH = 64
    MAX_SUMMARY_LENGTH = 1000
    MAX_SOURCE_LENGTH = 256


MEMORY_LIMITS = MemoryLimits()
