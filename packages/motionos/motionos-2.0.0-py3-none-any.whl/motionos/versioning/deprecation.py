"""
MotionOS SDK - Deprecation Utilities

Deprecation warnings and migration helpers.
"""

import warnings
import functools
from typing import Optional, Callable, TypeVar, List, Set
from dataclasses import dataclass


@dataclass
class DeprecationInfo:
    """Deprecation info."""
    feature: str
    deprecated_in: str
    removed_in: Optional[str] = None
    replacement: Optional[str] = None
    migration_guide: Optional[str] = None


# Registry of deprecated features
_deprecations: List[DeprecationInfo] = []

# Track shown warnings (to avoid spam)
_shown_warnings: Set[str] = set()


def warn_deprecated(info: DeprecationInfo) -> None:
    """Log a deprecation warning (once per feature)."""
    if info.feature in _shown_warnings:
        return
    _shown_warnings.add(info.feature)
    
    message = f"[MotionOS SDK] DEPRECATED: '{info.feature}' was deprecated in v{info.deprecated_in}"
    
    if info.removed_in:
        message += f" and will be removed in v{info.removed_in}"
    
    if info.replacement:
        message += f". Use '{info.replacement}' instead"
    
    if info.migration_guide:
        message += f". See: {info.migration_guide}"
    
    warnings.warn(message, DeprecationWarning, stacklevel=3)


F = TypeVar("F", bound=Callable)


def deprecated(info: DeprecationInfo) -> Callable[[F], F]:
    """Decorator to mark a function as deprecated."""
    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            warn_deprecated(DeprecationInfo(
                feature=info.feature or fn.__name__,
                deprecated_in=info.deprecated_in,
                removed_in=info.removed_in,
                replacement=info.replacement,
                migration_guide=info.migration_guide,
            ))
            return fn(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator


def register_deprecation(info: DeprecationInfo) -> None:
    """Register a deprecation."""
    if not any(d.feature == info.feature for d in _deprecations):
        _deprecations.append(info)


def get_deprecations() -> List[DeprecationInfo]:
    """Get all registered deprecations."""
    return _deprecations.copy()


def is_deprecated(feature: str) -> bool:
    """Check if a feature is deprecated."""
    return any(d.feature == feature for d in _deprecations)


def get_deprecation_info(feature: str) -> Optional[DeprecationInfo]:
    """Get deprecation info for a feature."""
    for d in _deprecations:
        if d.feature == feature:
            return d
    return None


def reset_deprecation_warnings() -> None:
    """Reset warnings (for testing)."""
    _shown_warnings.clear()
