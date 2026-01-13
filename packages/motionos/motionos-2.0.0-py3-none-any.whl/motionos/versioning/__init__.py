"""
MotionOS SDK - Versioning Package

Version management, feature detection, and compatibility layers.
"""

from motionos.versioning.version import (
    SDK_VERSION,
    parse_version,
    compare_versions,
    is_compatible,
    get_version_headers,
    get_version_info,
)
from motionos.versioning.features import (
    is_feature_available,
    update_feature_availability,
    get_feature_info,
    with_feature_check,
)
from motionos.versioning.deprecation import (
    warn_deprecated,
    deprecated,
    is_deprecated,
)
