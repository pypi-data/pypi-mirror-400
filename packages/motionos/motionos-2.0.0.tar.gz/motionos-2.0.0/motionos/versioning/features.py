"""
MotionOS SDK - Feature Detection

Server feature detection and graceful degradation.
"""

from typing import Dict, Optional, Callable, TypeVar, List
from dataclasses import dataclass
from enum import Enum


class ServerFeature(str, Enum):
    """Known server features."""
    INTENT_DETECTION = "intent_detection"
    POLICY_BASED_RETRIEVAL = "policy_based_retrieval"
    TIMELINE_WALK = "timeline_walk"
    BATCH_INGEST = "batch_ingest"
    EXPLAINABILITY = "explainability"
    DOMAIN_ADAPTERS = "domain_adapters"
    CAUSALITY_EDGES = "causality_edges"
    VALIDITY_CHECKING = "validity_checking"


@dataclass
class FeatureInfo:
    """Feature availability info."""
    name: str
    available: bool
    min_version: Optional[str] = None
    deprecated_in: Optional[str] = None
    fallback: Optional[str] = None


# Feature registry with minimum versions
FEATURE_REGISTRY: Dict[ServerFeature, Dict[str, Optional[str]]] = {
    ServerFeature.INTENT_DETECTION: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.POLICY_BASED_RETRIEVAL: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.TIMELINE_WALK: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.BATCH_INGEST: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.EXPLAINABILITY: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.DOMAIN_ADAPTERS: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.CAUSALITY_EDGES: {"min_version": "1.0.0", "deprecated_in": None},
    ServerFeature.VALIDITY_CHECKING: {"min_version": "1.0.0", "deprecated_in": None},
}

# Detected server features cache
_cached_features: Dict[ServerFeature, bool] = {}


def is_feature_available(feature: ServerFeature) -> bool:
    """Check if a feature is available."""
    if feature in _cached_features:
        return _cached_features[feature]
    return True  # Default to available


def update_feature_availability(features: Dict[ServerFeature, bool]) -> None:
    """Update feature availability from server response."""
    _cached_features.update(features)


def get_feature_info(feature: ServerFeature) -> FeatureInfo:
    """Get feature info."""
    registry = FEATURE_REGISTRY.get(feature, {})
    return FeatureInfo(
        name=feature.value,
        available=is_feature_available(feature),
        min_version=registry.get("min_version"),
        deprecated_in=registry.get("deprecated_in"),
    )


def get_all_features() -> List[FeatureInfo]:
    """Get all known features with availability."""
    return [get_feature_info(f) for f in ServerFeature]


T = TypeVar("T")


def with_feature_check(
    feature: ServerFeature,
    operation: Callable[[], T],
    fallback: Optional[Callable[[], T]] = None,
) -> T:
    """Create a feature-gated wrapper."""
    if is_feature_available(feature):
        return operation()
    
    if fallback:
        import warnings
        warnings.warn(f"Feature '{feature.value}' not available, using fallback")
        return fallback()
    
    raise RuntimeError(f"Feature '{feature.value}' is not available on this server")


def reset_feature_cache() -> None:
    """Reset feature cache (for testing)."""
    _cached_features.clear()
