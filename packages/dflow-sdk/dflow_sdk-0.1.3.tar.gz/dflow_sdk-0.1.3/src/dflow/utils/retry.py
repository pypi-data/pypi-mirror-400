"""Retry utilities with exponential backoff."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from .http import DFlowApiError

T = TypeVar("T")


def default_should_retry(error: Exception, attempt: int) -> bool:
    """Default retry condition: retry on rate limits (429) or server errors (5xx).

    Args:
        error: The exception that was raised
        attempt: The current attempt number (0-indexed)

    Returns:
        True if the operation should be retried
    """
    if isinstance(error, DFlowApiError):
        # Retry on rate limit (429) or server errors (5xx)
        return error.status_code == 429 or error.status_code >= 500

    # Retry on connection errors
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    return False


def _calculate_delay(
    attempt: int,
    initial_delay_ms: int,
    max_delay_ms: int,
    backoff_multiplier: float,
) -> float:
    """Calculate delay with exponential backoff and jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        initial_delay_ms: Initial delay in milliseconds
        max_delay_ms: Maximum delay in milliseconds
        backoff_multiplier: Multiplier for exponential backoff

    Returns:
        Delay in seconds
    """
    exponential_delay = initial_delay_ms * (backoff_multiplier**attempt)
    delay_with_cap = min(exponential_delay, max_delay_ms)
    # Add jitter (0-25% of delay) to prevent thundering herd
    jitter = delay_with_cap * random.random() * 0.25
    return (delay_with_cap + jitter) / 1000  # Convert to seconds


def with_retry(
    fn: Callable[[], T],
    max_retries: int = 3,
    initial_delay_ms: int = 1000,
    max_delay_ms: int = 30000,
    backoff_multiplier: float = 2.0,
    should_retry: Callable[[Exception, int], bool] | None = None,
) -> T:
    """Execute a function with automatic retry on failure using exponential backoff.

    Example:
        >>> from dflow.utils import with_retry
        >>>
        >>> # Basic usage
        >>> markets = with_retry(lambda: dflow.markets.get_markets())
        >>>
        >>> # With custom options
        >>> events = with_retry(
        ...     lambda: dflow.events.get_events(limit=100),
        ...     max_retries=5,
        ...     initial_delay_ms=500,
        ... )

    Args:
        fn: The function to execute
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay_ms: Initial delay in milliseconds before first retry (default: 1000)
        max_delay_ms: Maximum delay in milliseconds between retries (default: 30000)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        should_retry: Function to determine if an error should trigger a retry

    Returns:
        The result of the function

    Raises:
        The last error if all retries are exhausted
    """
    import time

    retry_check = should_retry or default_should_retry
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            last_error = e

            # Check if we should retry
            if attempt < max_retries and retry_check(e, attempt):
                delay = _calculate_delay(
                    attempt, initial_delay_ms, max_delay_ms, backoff_multiplier
                )
                time.sleep(delay)
                continue

            # No more retries, raise the error
            raise

    # This should never be reached, but satisfies type checker
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected state in retry loop")


async def with_retry_async(
    fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    initial_delay_ms: int = 1000,
    max_delay_ms: int = 30000,
    backoff_multiplier: float = 2.0,
    should_retry: Callable[[Exception, int], bool] | None = None,
) -> T:
    """Execute an async function with automatic retry using exponential backoff.

    Example:
        >>> from dflow.utils import with_retry_async
        >>>
        >>> markets = await with_retry_async(
        ...     lambda: async_client.markets.get_markets()
        ... )

    Args:
        fn: The async function to execute
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay_ms: Initial delay in milliseconds before first retry (default: 1000)
        max_delay_ms: Maximum delay in milliseconds between retries (default: 30000)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        should_retry: Function to determine if an error should trigger a retry

    Returns:
        The result of the function

    Raises:
        The last error if all retries are exhausted
    """
    retry_check = should_retry or default_should_retry
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await fn()
        except Exception as e:
            last_error = e

            # Check if we should retry
            if attempt < max_retries and retry_check(e, attempt):
                delay = _calculate_delay(
                    attempt, initial_delay_ms, max_delay_ms, backoff_multiplier
                )
                await asyncio.sleep(delay)
                continue

            # No more retries, raise the error
            raise

    # This should never be reached, but satisfies type checker
    if last_error:
        raise last_error
    raise RuntimeError("Unexpected state in retry loop")


def create_retryable(
    fn: Callable[..., T],
    max_retries: int = 3,
    initial_delay_ms: int = 1000,
    max_delay_ms: int = 30000,
    backoff_multiplier: float = 2.0,
    should_retry: Callable[[Exception, int], bool] | None = None,
) -> Callable[..., T]:
    """Create a retryable version of a function.

    Example:
        >>> from dflow.utils import create_retryable
        >>>
        >>> get_markets_with_retry = create_retryable(
        ...     dflow.markets.get_markets,
        ...     max_retries=5,
        ... )
        >>>
        >>> markets = get_markets_with_retry(limit=50)

    Args:
        fn: The function to wrap
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay_ms: Initial delay in milliseconds before first retry
        max_delay_ms: Maximum delay in milliseconds between retries
        backoff_multiplier: Multiplier for exponential backoff
        should_retry: Function to determine if an error should trigger a retry

    Returns:
        A wrapped function with automatic retry
    """

    def wrapper(*args, **kwargs) -> T:
        return with_retry(
            lambda: fn(*args, **kwargs),
            max_retries=max_retries,
            initial_delay_ms=initial_delay_ms,
            max_delay_ms=max_delay_ms,
            backoff_multiplier=backoff_multiplier,
            should_retry=should_retry,
        )

    return wrapper
