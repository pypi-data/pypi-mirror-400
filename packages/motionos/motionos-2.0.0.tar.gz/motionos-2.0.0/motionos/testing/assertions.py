"""
MotionOS SDK - Test Assertions

Custom assertions for SDK testing.
"""

from typing import Type, Dict, Any, Optional
from motionos.errors.base import MotionOSError


def assert_motionos_error(
    error: Exception,
    expected_code: Optional[str] = None,
) -> MotionOSError:
    """Assert that a value is a MotionOSError with specific code."""
    if not isinstance(error, MotionOSError):
        raise AssertionError(f"Expected MotionOSError but got {type(error).__name__}")
    
    if expected_code and error.code != expected_code:
        raise AssertionError(f"Expected error code '{expected_code}' but got '{error.code}'")
    
    return error


def assert_retryable(error: Exception) -> None:
    """Assert that an error is retryable."""
    if not isinstance(error, MotionOSError):
        raise AssertionError("Expected MotionOSError")
    
    if not error.retryable:
        raise AssertionError("Expected error to be retryable, but it wasn't")


def assert_not_retryable(error: Exception) -> None:
    """Assert that an error is not retryable."""
    if not isinstance(error, MotionOSError):
        raise AssertionError("Expected MotionOSError")
    
    if error.retryable:
        raise AssertionError("Expected error to not be retryable, but it was")


def assert_response_shape(
    response: Any,
    shape: Dict[str, type],
) -> None:
    """Assert response structure matches expected shape."""
    if not isinstance(response, dict):
        raise AssertionError(f"Expected dict response, got {type(response).__name__}")
    
    for key, expected_type in shape.items():
        if key not in response:
            raise AssertionError(f"Missing required field: {key}")
        
        value = response[key]
        if not isinstance(value, expected_type):
            raise AssertionError(
                f"Expected {key} to be {expected_type.__name__}, got {type(value).__name__}"
            )


async def assert_raises_async(
    fn,
    error_class: Type[Exception],
    message_contains: Optional[str] = None,
):
    """Assert async function raises specific error."""
    try:
        await fn()
        raise AssertionError(f"Expected function to raise {error_class.__name__}")
    except error_class as e:
        if message_contains and message_contains not in str(e):
            raise AssertionError(f"Expected message to contain '{message_contains}', got '{e}'")
        return e
    except Exception as e:
        raise AssertionError(f"Expected {error_class.__name__} but got {type(e).__name__}")
