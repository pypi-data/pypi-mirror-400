"""
CGP SDK Retry Handler

Implements retry logic with exponential backoff and circuit breaker pattern.
"""

import time
import random
import logging
from typing import Callable, TypeVar, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


logger = logging.getLogger("acgp.transport")

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd

    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 60.0  # Seconds before trying again


@dataclass
class CircuitBreaker:
    """
    Circuit breaker to prevent repeated calls to a failing service.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is down, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """
    config: RetryConfig
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    last_failure_time: Optional[datetime] = field(default=None)
    success_count_in_half_open: int = field(default=0)

    def record_success(self) -> None:
        """Record a successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count_in_half_open += 1
            # After a few successes in half-open, close the circuit
            if self.success_count_in_half_open >= 2:
                self._close()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open reopens the circuit
            self._open()
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._open()

    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                time_since_failure = datetime.now() - self.last_failure_time
                if time_since_failure.total_seconds() >= self.config.recovery_timeout:
                    self._half_open()
                    return True
            return False

        # HALF_OPEN: allow limited requests
        return True

    def _open(self) -> None:
        """Open the circuit."""
        logger.warning("Circuit breaker OPEN - service appears down")
        self.state = CircuitState.OPEN
        self.success_count_in_half_open = 0

    def _half_open(self) -> None:
        """Set circuit to half-open for testing."""
        logger.info("Circuit breaker HALF-OPEN - testing service recovery")
        self.state = CircuitState.HALF_OPEN
        self.success_count_in_half_open = 0

    def _close(self) -> None:
        """Close the circuit (normal operation)."""
        logger.info("Circuit breaker CLOSED - service recovered")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count_in_half_open = 0


class RetryHandler:
    """
    Handles retry logic with exponential backoff.

    Usage:
        handler = RetryHandler(config)
        result = handler.execute(my_function, arg1, arg2)
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(self.config) if self.config.circuit_breaker_enabled else None

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt using exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            # Add random jitter (0.5 to 1.5 of calculated delay)
            delay = delay * (0.5 + random.random())

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception is retryable.

        Args:
            exception: The exception that was raised

        Returns:
            True if the operation should be retried
        """
        # Import here to avoid circular imports
        import httpx

        # Retry on connection errors and server errors (5xx)
        if isinstance(exception, httpx.ConnectError):
            return True
        if isinstance(exception, httpx.ConnectTimeout):
            return True
        if isinstance(exception, httpx.ReadTimeout):
            return True
        if isinstance(exception, httpx.HTTPStatusError):
            # Retry on 5xx server errors and 429 (rate limited)
            status = exception.response.status_code
            return status >= 500 or status == 429

        return False

    def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            The last exception if all retries fail
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_execute():
            raise CircuitOpenError("Circuit breaker is open - service unavailable")

        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)

                # Record success
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()

                return result

            except Exception as e:
                last_exception = e

                # Record failure
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure()

                # Check if we should retry
                if attempt < self.config.max_retries and self.should_retry(e):
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    # No more retries or non-retryable error
                    break

        # All retries exhausted
        raise last_exception


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
):
    """
    Decorator for adding retry logic to a function.

    Usage:
        @with_retry(max_retries=3)
        def my_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        handler = RetryHandler(RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
        ))

        def wrapper(*args, **kwargs) -> T:
            return handler.execute(func, *args, **kwargs)

        return wrapper
    return decorator
