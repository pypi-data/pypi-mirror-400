"""Retry logic and rate limiting for pandas-airtable."""

from __future__ import annotations

import random
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from pandas_airtable.exceptions import AirtableRateLimitError
from pandas_airtable.types import RATE_LIMIT_QPS
from pandas_airtable.utils import log_retry


def retry_with_backoff[T](
    func: Callable[..., T],
    *args: Any,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> T:
    """Execute a function with exponential backoff retry logic.

    This is an outer retry loop to complement pyairtable's built-in retry
    mechanism, useful for long-running jobs that may encounter extended
    rate limiting or transient failures.

    Args:
        func: The function to execute.
        *args: Positional arguments for the function.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay in seconds between retries.
        retryable_exceptions: Tuple of exception types to retry on.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the function call.

    Raises:
        AirtableRateLimitError: If all retries are exhausted.
        Exception: If a non-retryable exception occurs.
    """
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retryable_exceptions as e:
            last_error = e

            if attempt == max_retries:
                # All retries exhausted
                raise AirtableRateLimitError(max_retries, last_error) from e

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2**attempt), max_delay)
            jitter = random.uniform(0, 0.1 * delay)
            sleep_time = delay + jitter

            log_retry(attempt + 1, max_retries, sleep_time, str(e))
            time.sleep(sleep_time)

    # This should never be reached, but for type safety
    raise AirtableRateLimitError(max_retries, last_error)


class RateLimitedExecutor:
    """Ensures operations respect Airtable's rate limit.

    Airtable enforces 5 requests per second per base. This class tracks
    request times and introduces delays when necessary to stay under the limit.
    """

    def __init__(self, qps_limit: int = RATE_LIMIT_QPS) -> None:
        """Initialize the rate limiter.

        Args:
            qps_limit: Maximum queries per second allowed.
        """
        self.qps_limit = qps_limit
        self.request_times: deque[float] = deque()
        self._window_size = 1.0  # 1 second window

    def wait_if_needed(self) -> None:
        """Block if making a request would exceed the rate limit."""
        now = time.time()

        # Remove requests older than the window
        while self.request_times and now - self.request_times[0] > self._window_size:
            self.request_times.popleft()

        # If at limit, wait until oldest request exits the window
        if len(self.request_times) >= self.qps_limit:
            wait_time = self._window_size - (now - self.request_times[0])
            if wait_time > 0:
                time.sleep(wait_time)
                # Clean up again after waiting
                now = time.time()
                while self.request_times and now - self.request_times[0] > self._window_size:
                    self.request_times.popleft()

        # Record this request
        self.request_times.append(time.time())

    def execute[T](self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute a function with rate limiting.

        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function call.
        """
        self.wait_if_needed()
        return func(*args, **kwargs)
