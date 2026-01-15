"""Retry policy and error handling utilities."""

from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Handles retry logic with configurable backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_seconds: int = 1,
        backoff_multiplier: float = 2.0,
    ):
        """Initialize retry policy.

        Args:
            max_attempts: Maximum number of attempts (including first try).
            backoff_seconds: Initial backoff duration in seconds.
            backoff_multiplier: Multiplier for exponential backoff.
        """
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.backoff_multiplier = backoff_multiplier

    def execute(
        self,
        func: Callable[[], T],
        on_error: Callable[[Exception, int], None] | None = None,
        on_retry: Callable[[int], None] | None = None,
    ) -> T:
        """Execute function with retry and exponential backoff.

        Args:
            func: Function to execute.
            on_error: Optional callback for error handling (called with exception and attempt number).
            on_retry: Optional callback before sleep (called with attempt number).

        Returns:
            Result from successful execution.

        Raises:
            Exception: Original exception if all retries exhausted.
        """
        last_exception = None
        current_backoff = self.backoff_seconds

        for attempt in range(self.max_attempts):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if on_error:
                    on_error(e, attempt)

                is_last_attempt = attempt == self.max_attempts - 1
                if not is_last_attempt:
                    if on_retry:
                        on_retry(attempt + 1)
                    time.sleep(current_backoff)
                    current_backoff *= self.backoff_multiplier

        # All retries exhausted
        raise last_exception
