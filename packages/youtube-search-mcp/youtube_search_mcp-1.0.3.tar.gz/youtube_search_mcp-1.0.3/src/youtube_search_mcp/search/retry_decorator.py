"""Retry decorator with exponential backoff for async operations."""

import asyncio
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from ..utils.logger import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Async retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        @async_retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(NetworkError,))
        async def fetch_data():
            # This will retry up to 3 times on NetworkError
            ...
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # This should never be reached, but just in case
            raise RuntimeError(f"{func.__name__} retry logic failed unexpectedly")

        return wrapper

    return decorator
