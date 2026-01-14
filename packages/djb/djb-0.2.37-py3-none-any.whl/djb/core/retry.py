"""
Retry utilities with exponential backoff.

This module provides retry logic for operations that may fail transiently,
such as network requests, API calls, and command execution.

Example:
    from djb.core.retry import retry, RetryExhausted

    # As a decorator
    @retry(max_attempts=3, initial_delay=1.0, exceptions=(ConnectionError,))
    def fetch_data():
        return requests.get("https://api.example.com/data")

    # As a context manager
    with retry(max_attempts=3, initial_delay=1.0) as attempt:
        while attempt():
            response = requests.get("https://api.example.com/data")
            if response.ok:
                break

    # Manual retry loop
    for attempt in retry_attempts(max_attempts=3, initial_delay=1.0):
        try:
            result = some_flaky_operation()
            break
        except TransientError:
            if attempt.is_last:
                raise
            attempt.sleep()
"""

from __future__ import annotations

import functools
import random
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generator, TypeVar

from djb.core.exceptions import DjbError
from djb.core.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

T = TypeVar("T")


class RetryExhausted(DjbError):
    """All retry attempts failed.

    Raised when the maximum number of retries is reached without success.

    Attributes:
        attempts: Number of attempts made
        last_exception: The last exception that was caught
    """

    def __init__(self, attempts: int, last_exception: Exception | None = None) -> None:
        self.attempts = attempts
        self.last_exception = last_exception
        msg = f"All {attempts} retry attempts failed"
        if last_exception:
            msg += f": {last_exception}"
        super().__init__(msg)


@dataclass
class RetryAttempt:
    """Information about a single retry attempt.

    Attributes:
        number: Current attempt number (1-indexed)
        max_attempts: Total number of attempts allowed
        delay: Delay before next attempt (in seconds)
    """

    number: int
    max_attempts: int
    delay: float

    @property
    def is_last(self) -> bool:
        """True if this is the last allowed attempt."""
        return self.number >= self.max_attempts

    def sleep(self) -> None:
        """Sleep for the calculated delay before the next attempt."""
        if not self.is_last and self.delay > 0:
            time.sleep(self.delay)


def calculate_delay(
    attempt: int,
    initial_delay: float,
    backoff_factor: float,
    max_delay: float,
    jitter: bool,
) -> float:
    """Calculate the delay for a given attempt.

    Uses exponential backoff: delay = initial_delay * (backoff_factor ** attempt)

    Args:
        attempt: Current attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each subsequent attempt
        max_delay: Maximum delay in seconds
        jitter: If True, add random jitter (0-50% of delay)

    Returns:
        Delay in seconds
    """
    delay = initial_delay * (backoff_factor**attempt)
    delay = min(delay, max_delay)

    if jitter:
        # Add 0-50% random jitter to prevent thundering herd
        delay = delay * (1 + random.random() * 0.5)

    return delay


def retry_attempts(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> Generator[RetryAttempt, None, None]:
    """Generate retry attempts with exponential backoff.

    Yields RetryAttempt objects that provide attempt information and a sleep method.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for each subsequent attempt (default: 2.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        jitter: Add random jitter to prevent thundering herd (default: True)

    Yields:
        RetryAttempt objects for each attempt

    Example:
        for attempt in retry_attempts(max_attempts=3):
            try:
                result = some_operation()
                break
            except TransientError:
                if attempt.is_last:
                    raise
                logger.warning(f"Attempt {attempt.number} failed, retrying...")
                attempt.sleep()
    """
    for i in range(max_attempts):
        delay = calculate_delay(i, initial_delay, backoff_factor, max_delay, jitter)
        yield RetryAttempt(number=i + 1, max_attempts=max_attempts, delay=delay)


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying a function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for each subsequent attempt (default: 2.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        jitter: Add random jitter to prevent thundering herd (default: True)
        exceptions: Tuple of exception types to catch and retry (default: (Exception,))

    Returns:
        Decorated function

    Raises:
        RetryExhausted: If all attempts fail

    Example:
        @retry(max_attempts=3, initial_delay=0.5, exceptions=(ConnectionError, TimeoutError))
        def fetch_url(url: str) -> str:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in retry_attempts(
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                max_delay=max_delay,
                jitter=jitter,
            ):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt.is_last:
                        logger.debug(f"Retry exhausted after {attempt.number} attempts: {e}")
                        raise RetryExhausted(attempt.number, e) from e
                    logger.debug(
                        f"Attempt {attempt.number}/{max_attempts} failed: {e}. "
                        f"Retrying in {attempt.delay:.2f}s..."
                    )
                    attempt.sleep()

            # Should not reach here, but satisfy type checker
            raise RetryExhausted(max_attempts, last_exception)

        return wrapper

    return decorator


@contextmanager
def retry_context(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> Generator[Callable[[], bool], None, None]:
    """Context manager for manual retry loops.

    Yields a callable that returns True while there are attempts remaining.
    Call it in a while loop to control the retry logic.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for each subsequent attempt (default: 2.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        jitter: Add random jitter to prevent thundering herd (default: True)

    Yields:
        Callable that returns True while attempts remain

    Example:
        with retry_context(max_attempts=3) as attempt:
            while attempt():
                try:
                    result = some_operation()
                    break
                except TransientError:
                    pass  # Will retry automatically
    """
    attempt_gen = retry_attempts(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        backoff_factor=backoff_factor,
        max_delay=max_delay,
        jitter=jitter,
    )
    current_attempt: RetryAttempt | None = None
    exhausted = False

    def next_attempt() -> bool:
        nonlocal current_attempt, exhausted

        # Sleep after previous attempt (if any)
        if current_attempt is not None and not current_attempt.is_last:
            current_attempt.sleep()

        try:
            current_attempt = next(attempt_gen)
            return True
        except StopIteration:
            exhausted = True
            return False

    yield next_attempt
