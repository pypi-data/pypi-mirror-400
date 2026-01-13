"""
MotionOS SDK - Retry Strategy

Configurable retry strategies with exponential backoff.
"""

from typing import Optional, Callable, Any, List
from dataclasses import dataclass, field
import random

from motionos.errors.base import MotionOSError, RateLimitError


@dataclass
class RetryOptions:
    """Retry configuration options."""
    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    multiplier: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.25
    should_retry: Optional[Callable[[Exception, int], bool]] = None
    on_retry: Optional[Callable[[Exception, int, int], None]] = None


# HTTP methods that are safe to retry
IDEMPOTENT_METHODS = ["GET", "HEAD", "OPTIONS", "PUT", "DELETE"]

# Operations that are safe to retry
IDEMPOTENT_OPERATIONS = [
    "retrieve",
    "get",
    "list",
    "check",
    "validate",
    "query",
    "search",
]

# Operations that should never be retried automatically
NON_IDEMPOTENT_OPERATIONS = [
    "ingest",
    "create",
    "insert",
    "post",
]


class RetryStrategy:
    """Retry strategy class with exponential backoff."""
    
    def __init__(self, options: Optional[RetryOptions] = None):
        self.options = options or RetryOptions()
    
    def get_delay(self, attempt: int, error: Optional[Exception] = None) -> int:
        """Get the delay for a retry attempt in milliseconds."""
        # Check if error has specific retry-after hint
        if isinstance(error, RateLimitError) and error.retry_after_ms:
            return min(error.retry_after_ms, self.options.max_delay_ms)
        
        # Calculate exponential backoff
        delay = self.options.base_delay_ms * (self.options.multiplier ** attempt)
        
        # Cap at max delay
        delay = min(delay, self.options.max_delay_ms)
        
        # Add jitter
        if self.options.jitter:
            jitter_range = delay * self.options.jitter_factor
            delay = delay + (random.random() * jitter_range * 2 - jitter_range)
            delay = max(0, round(delay))
        
        return int(delay)
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Check if an error should be retried."""
        # Check max retries
        if attempt >= self.options.max_retries:
            return False
        
        # Use custom condition if provided
        if self.options.should_retry:
            return self.options.should_retry(error, attempt)
        
        # Default: check if error is retryable
        if isinstance(error, MotionOSError):
            return error.retryable
        
        # Network errors are typically retryable
        error_message = str(error).lower()
        return any(x in error_message for x in [
            "network",
            "timeout",
            "connection",
            "reset",
            "refused",
        ])
    
    def is_idempotent(self, operation: str, method: Optional[str] = None) -> bool:
        """Check if an operation is idempotent (safe to retry)."""
        # Check HTTP method
        if method and method.upper() in IDEMPOTENT_METHODS:
            return True
        
        # Check operation name
        op_lower = operation.lower()
        
        # Explicitly non-idempotent
        if any(op in op_lower for op in NON_IDEMPOTENT_OPERATIONS):
            return False
        
        # Idempotent operations
        return any(op in op_lower for op in IDEMPOTENT_OPERATIONS)
    
    def on_retry(self, error: Exception, attempt: int, delay_ms: int) -> None:
        """Handle retry event."""
        if self.options.on_retry:
            self.options.on_retry(error, attempt, delay_ms)
    
    def with_options(self, **kwargs) -> "RetryStrategy":
        """Create a copy with modified options."""
        new_options = RetryOptions(
            max_retries=kwargs.get("max_retries", self.options.max_retries),
            base_delay_ms=kwargs.get("base_delay_ms", self.options.base_delay_ms),
            max_delay_ms=kwargs.get("max_delay_ms", self.options.max_delay_ms),
            multiplier=kwargs.get("multiplier", self.options.multiplier),
            jitter=kwargs.get("jitter", self.options.jitter),
            jitter_factor=kwargs.get("jitter_factor", self.options.jitter_factor),
            should_retry=kwargs.get("should_retry", self.options.should_retry),
            on_retry=kwargs.get("on_retry", self.options.on_retry),
        )
        return RetryStrategy(new_options)


class RetryStrategies:
    """Preset retry strategies."""
    
    @staticmethod
    def none() -> RetryStrategy:
        """No retries."""
        return RetryStrategy(RetryOptions(max_retries=0))
    
    @staticmethod
    def default() -> RetryStrategy:
        """Default retry strategy."""
        return RetryStrategy()
    
    @staticmethod
    def aggressive() -> RetryStrategy:
        """Aggressive retry for critical operations."""
        return RetryStrategy(RetryOptions(
            max_retries=5,
            base_delay_ms=500,
            max_delay_ms=60000,
        ))
    
    @staticmethod
    def conservative() -> RetryStrategy:
        """Conservative retry for non-critical operations."""
        return RetryStrategy(RetryOptions(
            max_retries=2,
            base_delay_ms=2000,
            max_delay_ms=10000,
        ))
    
    @staticmethod
    def fast() -> RetryStrategy:
        """Fast retry with minimal delays."""
        return RetryStrategy(RetryOptions(
            max_retries=3,
            base_delay_ms=100,
            max_delay_ms=1000,
            multiplier=1.5,
        ))


class RetryExhaustedError(MotionOSError):
    """Retry exhaustion error."""
    
    def __init__(
        self,
        attempts: int,
        last_error: Optional[Exception] = None,
        request_id: Optional[str] = None,
    ):
        message = f"Retry exhausted after {attempts} attempts"
        super().__init__(message, "retry_exhausted", None, request_id)
        self.attempts = attempts
        self.last_error = last_error
