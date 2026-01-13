"""
MotionOS SDK - Ingest Validator

Validates ingestion options and normalizes metadata.
"""

from typing import Dict, Any, List, Optional
from motionos.types.memory import MEMORY_LIMITS
from motionos.errors.base import ValidationError


# Valid memory types
VALID_MEMORY_TYPES = [
    "decision",
    "note",
    "event",
    "observation",
    "instruction",
    "preference",
    "fact",
    "episode",
]

# Valid memory scopes
VALID_SCOPES = ["project", "agent", "global"]

# Valid edge types
VALID_EDGE_TYPES = ["causes", "follows", "relates", "supersedes"]


def validate_raw_text(raw_text) -> None:
    """Validate raw text content."""
    if raw_text is None:
        raise ValidationError("raw_text is required", "raw_text")
    
    if not isinstance(raw_text, str):
        raise ValidationError("raw_text must be a string", "raw_text")
    
    if len(raw_text.strip()) == 0:
        raise ValidationError("raw_text cannot be empty", "raw_text")
    
    if len(raw_text) > MEMORY_LIMITS.MAX_TEXT_LENGTH:
        raise ValidationError(
            f"raw_text too long (max {MEMORY_LIMITS.MAX_TEXT_LENGTH} characters, got {len(raw_text)})",
            "raw_text"
        )


def validate_summary(summary) -> None:
    """Validate summary."""
    if summary is None:
        return
    
    if not isinstance(summary, str):
        raise ValidationError("summary must be a string", "summary")
    
    if len(summary) > MEMORY_LIMITS.MAX_SUMMARY_LENGTH:
        raise ValidationError(
            f"summary too long (max {MEMORY_LIMITS.MAX_SUMMARY_LENGTH} characters)",
            "summary"
        )


def validate_tags(tags) -> None:
    """Validate tags."""
    if tags is None:
        return
    
    if not isinstance(tags, list):
        raise ValidationError("tags must be a list", "tags")
    
    if len(tags) > MEMORY_LIMITS.MAX_TAGS:
        raise ValidationError(
            f"Too many tags (max {MEMORY_LIMITS.MAX_TAGS}, got {len(tags)})",
            "tags"
        )
    
    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            raise ValidationError(f"tags[{i}] must be a string", f"tags[{i}]")
        if len(tag) > MEMORY_LIMITS.MAX_TAG_LENGTH:
            raise ValidationError(
                f"tags[{i}] too long (max {MEMORY_LIMITS.MAX_TAG_LENGTH} characters)",
                f"tags[{i}]"
            )


def validate_memory_type(memory_type) -> None:
    """Validate memory type."""
    if memory_type is None:
        return
    
    if not isinstance(memory_type, str):
        raise ValidationError("type must be a string", "type")
    
    if memory_type not in VALID_MEMORY_TYPES:
        raise ValidationError(
            f"Invalid type: {memory_type}. Valid types: {', '.join(VALID_MEMORY_TYPES)}",
            "type"
        )


def validate_scope(scope) -> None:
    """Validate memory scope."""
    if scope is None:
        return
    
    if not isinstance(scope, str):
        raise ValidationError("scope must be a string", "scope")
    
    if scope not in VALID_SCOPES:
        raise ValidationError(
            f"Invalid scope: {scope}. Valid scopes: {', '.join(VALID_SCOPES)}",
            "scope"
        )


def validate_source(source) -> None:
    """Validate source."""
    if source is None:
        return
    
    if not isinstance(source, str):
        raise ValidationError("source must be a string", "source")
    
    if len(source) > MEMORY_LIMITS.MAX_SOURCE_LENGTH:
        raise ValidationError(
            f"source too long (max {MEMORY_LIMITS.MAX_SOURCE_LENGTH} characters)",
            "source"
        )


def validate_score(value, field_name: str) -> None:
    """Validate score value (0-1)."""
    if value is None:
        return
    
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if value < 0 or value > 1:
        raise ValidationError(f"{field_name} must be between 0 and 1", field_name)


def validate_edges(edges) -> None:
    """Validate edges."""
    if edges is None:
        return
    
    if not isinstance(edges, list):
        raise ValidationError("edges must be a list", "edges")
    
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValidationError(f"edges[{i}] must be a dict", f"edges[{i}]")
        
        if "to" not in edge or not isinstance(edge["to"], str):
            raise ValidationError(
                f"edges[{i}].to is required and must be a string",
                f"edges[{i}].to"
            )
        
        if "type" not in edge or not isinstance(edge["type"], str):
            raise ValidationError(
                f"edges[{i}].type is required and must be a string",
                f"edges[{i}].type"
            )
        
        if edge["type"] not in VALID_EDGE_TYPES:
            raise ValidationError(
                f"Invalid edge type: {edge['type']}. Valid types: {', '.join(VALID_EDGE_TYPES)}",
                f"edges[{i}].type"
            )


def validate_ingest_options(options: Dict[str, Any]) -> None:
    """Validate full ingest options."""
    # Required: raw_text
    validate_raw_text(options.get("raw_text"))
    
    # Optional fields
    validate_summary(options.get("summary"))
    validate_tags(options.get("tags"))
    validate_memory_type(options.get("type"))
    validate_scope(options.get("scope"))
    validate_source(options.get("source"))
    validate_score(options.get("importance"), "importance")
    validate_score(options.get("frequency"), "frequency")
    validate_score(options.get("recency"), "recency")
    validate_edges(options.get("edges"))


def normalize_ingest_options(
    options: Dict[str, Any],
    defaults: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Normalize ingest options with defaults."""
    defaults = defaults or {}
    return {
        **options,
        "agent_id": options.get("agent_id") or defaults.get("agent_id", "default-agent"),
        "scope": options.get("scope") or defaults.get("scope", "global"),
        "tags": options.get("tags") or [],
    }


def calculate_payload_size(options: Dict[str, Any]) -> int:
    """Calculate approximate payload size."""
    import json
    size = 0
    size += len(options.get("raw_text", ""))
    size += len(options.get("summary", ""))
    size += len(json.dumps(options.get("tags", [])))
    size += len(json.dumps(options.get("edges", [])))
    return size


def is_payload_within_limits(options: Dict[str, Any]) -> bool:
    """Check if payload is within limits."""
    raw_text = options.get("raw_text", "")
    return len(raw_text) <= MEMORY_LIMITS.MAX_TEXT_LENGTH
