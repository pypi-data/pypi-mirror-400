"""
MotionOS SDK - Timeline Client

Provides timeline and version operations.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from motionos.types.timeline import TIMELINE_LIMITS
from motionos.errors.base import ValidationError


@dataclass
class TimelineWalkOptions:
    """Options for timeline walk."""
    version_id: str
    direction: str = "backward"
    max_depth: int = 5
    max_results: int = 20
    edge_types: Optional[List[str]] = None


def validate_walk_options(options: Dict[str, Any]) -> None:
    """Validate timeline walk options."""
    if not options.get("version_id"):
        raise ValidationError("version_id is required", "version_id")
    
    if not isinstance(options.get("version_id"), str):
        raise ValidationError("version_id must be a string", "version_id")
    
    direction = options.get("direction")
    if direction is not None:
        valid_directions = ["backward", "forward", "both"]
        if direction not in valid_directions:
            raise ValidationError(
                f"Invalid direction: {direction}. Valid: {', '.join(valid_directions)}",
                "direction"
            )
    
    max_depth = options.get("max_depth")
    if max_depth is not None:
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ValidationError("max_depth must be a positive integer", "max_depth")
        if max_depth > TIMELINE_LIMITS.MAX_MAX_DEPTH:
            raise ValidationError(
                f"max_depth cannot exceed {TIMELINE_LIMITS.MAX_MAX_DEPTH}",
                "max_depth"
            )
    
    max_results = options.get("max_results")
    if max_results is not None:
        if not isinstance(max_results, int) or max_results < 1:
            raise ValidationError("max_results must be a positive integer", "max_results")
        if max_results > TIMELINE_LIMITS.MAX_MAX_RESULTS:
            raise ValidationError(
                f"max_results cannot exceed {TIMELINE_LIMITS.MAX_MAX_RESULTS}",
                "max_results"
            )


def validate_rollback_options(options: Dict[str, Any]) -> None:
    """Validate rollback options."""
    if not options.get("memory_id"):
        raise ValidationError("memory_id is required", "memory_id")
    
    if not options.get("version_id"):
        raise ValidationError("version_id is required", "version_id")


def normalize_walk_options(options: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize walk options with defaults."""
    return {
        **options,
        "direction": options.get("direction", "backward"),
        "max_depth": options.get("max_depth", TIMELINE_LIMITS.DEFAULT_MAX_DEPTH),
        "max_results": options.get("max_results", TIMELINE_LIMITS.DEFAULT_MAX_RESULTS),
        "edge_types": options.get("edge_types", ["version", "cause", "supersedes"]),
    }


class TimelineWalkOptionsBuilder:
    """Builder for timeline walk options."""
    
    def __init__(self, version_id: str):
        self._options: Dict[str, Any] = {"version_id": version_id}
    
    def backward(self) -> "TimelineWalkOptionsBuilder":
        """Walk backward (find causes)."""
        self._options["direction"] = "backward"
        return self
    
    def forward(self) -> "TimelineWalkOptionsBuilder":
        """Walk forward (find effects)."""
        self._options["direction"] = "forward"
        return self
    
    def both(self) -> "TimelineWalkOptionsBuilder":
        """Walk both directions."""
        self._options["direction"] = "both"
        return self
    
    def with_max_depth(self, depth: int) -> "TimelineWalkOptionsBuilder":
        """Set max depth."""
        self._options["max_depth"] = depth
        return self
    
    def with_max_results(self, results: int) -> "TimelineWalkOptionsBuilder":
        """Set max results."""
        self._options["max_results"] = results
        return self
    
    def with_edge_types(self, types: List[str]) -> "TimelineWalkOptionsBuilder":
        """Filter by edge types."""
        self._options["edge_types"] = types
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the options."""
        validate_walk_options(self._options)
        return normalize_walk_options(self._options)


def walk_from(version_id: str) -> TimelineWalkOptionsBuilder:
    """Create a walk options builder."""
    return TimelineWalkOptionsBuilder(version_id)


class TimelineClient:
    """
    Timeline operations client.
    
    Provides methods for walking timelines, checking validity,
    and managing version lineage.
    """
    
    def __init__(self, http_client):
        """Initialize with an HTTP client."""
        self._http = http_client
    
    async def walk(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Walk timeline edges from a version."""
        validate_walk_options(options)
        normalized = normalize_walk_options(options)
        # Actual HTTP call would happen here
        raise NotImplementedError("Implement with actual HTTP client")
    
    async def check_validity(self, version_id: str) -> Dict[str, Any]:
        """Check if a version is still valid."""
        if not version_id:
            raise ValidationError("version_id is required", "version_id")
        raise NotImplementedError("Implement with actual HTTP client")
    
    async def get_lineage(self, version_id: str) -> Dict[str, Any]:
        """Get lineage (ancestors and descendants)."""
        if not version_id:
            raise ValidationError("version_id is required", "version_id")
        raise NotImplementedError("Implement with actual HTTP client")
    
    async def list_versions(self, memory_id: str) -> List[Dict[str, Any]]:
        """List all versions of a memory."""
        if not memory_id:
            raise ValidationError("memory_id is required", "memory_id")
        raise NotImplementedError("Implement with actual HTTP client")
    
    async def rollback(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback to a specific version."""
        validate_rollback_options(options)
        raise NotImplementedError("Implement with actual HTTP client")


def is_version_obsolete(validity: Dict[str, Any]) -> bool:
    """Check if a version is obsolete."""
    return not validity.get("is_valid", True) or len(validity.get("superseded_by", [])) > 0


def get_latest_valid_version(lineage: Dict[str, Any]) -> str:
    """Get the latest valid version from a lineage."""
    return lineage.get("current_version", lineage.get("version_id", ""))


def is_rollback_safe(lineage: Dict[str, Any], target_version_id: str) -> bool:
    """Check if rollback is safe (version is in lineage)."""
    all_versions = []
    for ancestor in lineage.get("ancestors", []):
        all_versions.append(ancestor.get("version_id"))
    for descendant in lineage.get("descendants", []):
        all_versions.append(descendant.get("version_id"))
    all_versions.append(lineage.get("version_id"))
    return target_version_id in all_versions
