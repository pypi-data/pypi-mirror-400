"""
MotionOS SDK - Runtime Package

Platform detection, environment-specific adapters, and runtime utilities.
"""

from motionos.runtime.detection import (
    RuntimeEnvironment,
    RuntimeCapabilities,
    detect_runtime,
    get_runtime_info,
    is_serverless,
    is_async_context,
)
from motionos.runtime.adapters import (
    get_default_timeout,
    get_default_retry,
    create_platform_config,
)
from motionos.runtime.restrictions import (
    is_operation_allowed,
    get_allowed_operations,
)
