"""
MotionOS SDK - Retry Executor

Executes operations with retry logic.
"""

import asyncio
from typing import TypeVar, Callable, Awaitable, Optional

from motionos.retry.strategy import RetryStrategy, RetryOptions, RetryExhaustedError


T = TypeVar("T")


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    options: Optional[RetryOptions] = None,
) -> T:
    """Execute an operation with retry logic."""
    opts = options or RetryOptions()
    strategy = RetryStrategy(opts)
    last_error: Optional[Exception] = None
    
    for attempt in range(opts.max_retries + 1):
        try:
            return await operation()
        except Exception as error:
            last_error = error
            
            if not strategy.should_retry(error, attempt):
                raise
            
            delay = strategy.get_delay(attempt, error)
            strategy.on_retry(error, attempt, delay)
            await asyncio.sleep(delay / 1000)  # Convert to seconds
    
    raise RetryExhaustedError(opts.max_retries + 1, last_error)


def with_retry_sync(
    operation: Callable[[], T],
    options: Optional[RetryOptions] = None,
) -> T:
    """Execute a synchronous operation with retry logic."""
    import time
    
    opts = options or RetryOptions()
    strategy = RetryStrategy(opts)
    last_error: Optional[Exception] = None
    
    for attempt in range(opts.max_retries + 1):
        try:
            return operation()
        except Exception as error:
            last_error = error
            
            if not strategy.should_retry(error, attempt):
                raise
            
            delay = strategy.get_delay(attempt, error)
            strategy.on_retry(error, attempt, delay)
            time.sleep(delay / 1000)  # Convert to seconds
    
    raise RetryExhaustedError(opts.max_retries + 1, last_error)


async def with_idempotent_retry(
    operation: Callable[[], Awaitable[T]],
    operation_name: str,
    options: Optional[RetryOptions] = None,
) -> T:
    """Execute an idempotent operation with retry logic."""
    strategy = RetryStrategy(options)
    
    if not strategy.is_idempotent(operation_name):
        # Non-idempotent operations execute once without retry
        return await operation()
    
    return await with_retry(operation, options)


async def with_timeout(
    operation: Callable[[], Awaitable[T]],
    timeout_ms: int,
    message: str = "Operation timed out",
) -> T:
    """Execute an operation with a timeout."""
    try:
        return await asyncio.wait_for(
            operation(),
            timeout=timeout_ms / 1000,  # Convert to seconds
        )
    except asyncio.TimeoutError:
        raise TimeoutError(message) from None


async def with_retry_and_timeout(
    operation: Callable[[], Awaitable[T]],
    options: Optional[RetryOptions] = None,
    timeout_ms: int = 30000,
) -> T:
    """Execute an operation with both retry and timeout."""
    async def timed_operation() -> T:
        return await with_timeout(operation, timeout_ms)
    
    return await with_retry(timed_operation, options)


class RetryContext:
    """Retry context for tracking retry state."""
    
    def __init__(
        self,
        attempt: int,
        max_attempts: int,
        elapsed_ms: int,
        strategy: RetryStrategy,
    ):
        self.attempt = attempt
        self.max_attempts = max_attempts
        self.elapsed_ms = elapsed_ms
        self.strategy = strategy


async def with_retry_context(
    operation: Callable[[RetryContext], Awaitable[T]],
    options: Optional[RetryOptions] = None,
) -> T:
    """Execute with full retry context."""
    import time
    
    opts = options or RetryOptions()
    strategy = RetryStrategy(opts)
    max_attempts = opts.max_retries + 1
    start_time = time.time()
    last_error: Optional[Exception] = None
    
    for attempt in range(max_attempts):
        context = RetryContext(
            attempt=attempt,
            max_attempts=max_attempts,
            elapsed_ms=int((time.time() - start_time) * 1000),
            strategy=strategy,
        )
        
        try:
            return await operation(context)
        except Exception as error:
            last_error = error
            
            if not strategy.should_retry(error, attempt):
                raise
            
            delay = strategy.get_delay(attempt, error)
            strategy.on_retry(error, attempt, delay)
            await asyncio.sleep(delay / 1000)
    
    raise RetryExhaustedError(max_attempts, last_error)
