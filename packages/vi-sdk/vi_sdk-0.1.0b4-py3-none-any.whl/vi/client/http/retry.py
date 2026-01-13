#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   retry.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   HTTP retry strategy configuration and handler.
"""

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from enum import Enum
from typing import Any, Protocol, TypeVar

import httpx
from vi.client.errors import (
    ViNetworkError,
    ViRateLimitError,
    ViServerError,
    ViTimeoutError,
)

T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry backoff strategies.

    Attributes:
        EXPONENTIAL: Pure exponential backoff without jitter.
            Formula: base_delay * (2 ** attempt)
            Use case: Predictable retry timing, testing

        EXPONENTIAL_FULL_JITTER: Exponential backoff with full jitter.
            Formula: random(0, base_delay * (2 ** attempt))
            Use case: Production systems with many clients (prevents thundering herd)
            Recommended by AWS: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

        EXPONENTIAL_EQUAL_JITTER: Exponential backoff with equal jitter.
            Formula: base_delay * (2 ** attempt) / 2 + random(0, base_delay * (2 ** attempt) / 2)
            Use case: Balance between predictability and jitter

        LINEAR: Linear backoff with optional jitter.
            Formula: base_delay * attempt
            Use case: Gradual increase without exponential growth

    """

    EXPONENTIAL = "exponential"
    EXPONENTIAL_FULL_JITTER = "exponential_full_jitter"
    EXPONENTIAL_EQUAL_JITTER = "exponential_equal_jitter"
    LINEAR = "linear"


@dataclass
class RetryConfig:
    """Configuration for HTTP request retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts for non-rate-limit errors. Defaults to 3.
        max_rate_limit_retries: Maximum number of retry attempts for rate limit errors (429).
            Defaults to 20. Set to a higher value for operations that can tolerate longer waits.
        base_delay: Base delay in seconds for calculating backoff. Defaults to 1.0.
        max_delay: Maximum delay in seconds between retries. Defaults to 60.0.
        strategy: Retry backoff strategy. Defaults to EXPONENTIAL_FULL_JITTER.
        respect_retry_after: Whether to respect HTTP Retry-After header. Defaults to True.
        jitter_factor: Jitter randomization factor (0.0 to 1.0). Defaults to 1.0.
            Only used with LINEAR strategy to add randomness.

    Example:
        ```python
        # Conservative retry for critical operations
        config = RetryConfig(
            max_retries=5,
            max_rate_limit_retries=30,
            base_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL_EQUAL_JITTER,
        )

        # Aggressive retry for bulk operations
        config = RetryConfig(
            max_retries=10,
            max_rate_limit_retries=50,
            base_delay=0.5,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_FULL_JITTER,
        )
        ```

    """

    max_retries: int = 3
    max_rate_limit_retries: int = 20
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_FULL_JITTER
    respect_retry_after: bool = True
    jitter_factor: float = 1.0

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.max_rate_limit_retries < 0:
            raise ValueError("max_rate_limit_retries must be non-negative")
        if self.base_delay <= 0:
            raise ValueError("base_delay must be positive")
        if self.max_delay <= 0:
            raise ValueError("max_delay must be positive")
        if self.base_delay > self.max_delay:
            raise ValueError("base_delay must be less than or equal to max_delay")
        if not 0.0 <= self.jitter_factor <= 1.0:
            raise ValueError("jitter_factor must be between 0.0 and 1.0")


class ResponseProtocol(Protocol):
    """Protocol for HTTP response objects."""

    @property
    def headers(self) -> dict[str, str]:
        """Response headers."""


class RetryHandler:
    """Handles retry backoff calculation with jitter and Retry-After support.

    This class implements various retry strategies to prevent thundering herd problems
    and respect server-side retry signals.

    Example:
        ```python
        config = RetryConfig(
            max_retries=5,
            strategy=RetryStrategy.EXPONENTIAL_FULL_JITTER,
            respect_retry_after=True,
        )
        handler = RetryHandler(config)

        for attempt in range(config.max_retries + 1):
            try:
                response = make_request()
                break
            except RateLimitError as e:
                if attempt < config.max_retries:
                    backoff = handler.calculate_backoff(attempt, response)
                    time.sleep(backoff)
        ```

    """

    def __init__(self, config: RetryConfig):
        """Initialize retry handler.

        Args:
            config: Retry configuration.

        """
        self.config = config

    def calculate_backoff(
        self,
        attempt: int,
        retry_after_header: str | None = None,
    ) -> float:
        """Calculate backoff time for the given attempt.

        Args:
            attempt: Current attempt number (0-indexed).
            retry_after_header: Optional Retry-After header value from the server.

        Returns:
            Backoff time in seconds, capped at max_delay.

        Example:
            ```python
            # Without Retry-After (use strategy)
            backoff = handler.calculate_backoff(attempt=2)

            # With Retry-After header value
            backoff = handler.calculate_backoff(attempt=2, retry_after_header="60")
            ```

        """
        # Check Retry-After header first if enabled and provided
        if self.config.respect_retry_after and retry_after_header is not None:
            retry_after = self._parse_retry_after(retry_after_header)
            if retry_after is not None:
                return min(retry_after, self.config.max_delay)

        # Calculate base backoff using selected strategy
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            backoff = self._exponential_backoff(attempt)
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_FULL_JITTER:
            backoff = self._exponential_full_jitter(attempt)
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_EQUAL_JITTER:
            backoff = self._exponential_equal_jitter(attempt)
        elif self.config.strategy == RetryStrategy.LINEAR:
            backoff = self._linear_backoff(attempt)
        else:
            # Fallback to exponential with full jitter
            backoff = self._exponential_full_jitter(attempt)

        # Cap at max_delay
        return min(backoff, self.config.max_delay)

    def _parse_retry_after(self, retry_after_value: str) -> float | None:
        """Parse Retry-After header value.

        The Retry-After header can be in two formats:
        1. Delay-seconds: A non-negative integer (e.g., "120")
        2. HTTP-date: An HTTP date (e.g., "Wed, 21 Oct 2025 07:28:00 GMT")

        Args:
            retry_after_value: Retry-After header value string.

        Returns:
            Retry delay in seconds, or None if value is invalid.

        """
        if not retry_after_value:
            return None

        # Try parsing as integer (delay-seconds format)
        try:
            return float(retry_after_value)
        except ValueError:
            pass

        # Try parsing as HTTP date
        try:
            retry_date = parsedate_to_datetime(retry_after_value)
            now = datetime.now(retry_date.tzinfo)
            delay = (retry_date - now).total_seconds()
            return max(0.0, delay)  # Ensure non-negative
        except (ValueError, TypeError):
            pass

        return None

    def _exponential_backoff(self, attempt: int) -> float:
        """Pure exponential backoff without jitter.

        Formula: base_delay * (2 ** attempt)
        """
        capped_attempt = min(attempt, 30)
        return self.config.base_delay * (2**capped_attempt)

    def _exponential_full_jitter(self, attempt: int) -> float:
        """Exponential backoff with full jitter.

        Formula: random(0, base_delay * (2 ** attempt))

        This is the recommended strategy by AWS for preventing thundering herd.
        Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        """
        capped_attempt = min(attempt, 30)
        base = self.config.base_delay * (2**capped_attempt)
        return random.uniform(0, base)

    def _exponential_equal_jitter(self, attempt: int) -> float:
        """Exponential backoff with equal jitter.

        Formula: base / 2 + random(0, base / 2)
        where base = base_delay * (2 ** attempt)

        This provides a balance between predictability and randomization.
        """
        capped_attempt = min(attempt, 30)
        base = self.config.base_delay * (2**capped_attempt)
        return base / 2 + random.uniform(0, base / 2)

    def _linear_backoff(self, attempt: int) -> float:
        """Linear backoff with optional jitter.

        Formula: base_delay * attempt * (1 + jitter_factor * random(-1, 1))
        """
        base = self.config.base_delay * (attempt + 1)
        if self.config.jitter_factor > 0:
            jitter = base * self.config.jitter_factor * random.uniform(-1, 1)
            return max(0, base + jitter)
        return base


class RetryExecutor:
    """Generic retry executor with exponential backoff and rate limit handling.

    This class provides a unified retry mechanism for any operation that may fail
    due to rate limits, server errors, or network issues. It supports:
    - Unlimited retries for rate limits (429)
    - Limited retries for other transient errors
    - Exponential backoff with jitter
    - Retry-After header support
    - Keyboard interrupt handling

    Example:
        ```python
        from vi.client.http.retry import RetryConfig, RetryExecutor

        config = RetryConfig(max_retries=5)
        executor = RetryExecutor(config)

        # Execute with retry
        result = executor.execute(
            operation=lambda: my_api_call(),
            operation_name="API call",
        )
        ```

    """

    def __init__(self, retry_handler: RetryHandler):
        """Initialize retry executor.

        Args:
            retry_handler: RetryHandler instance for backoff calculation

        """
        self.retry_handler = retry_handler

    def execute(
        self,
        operation: Callable[[], T],
        operation_name: str,
        max_retries: int | None = None,
        logger: Any | None = None,
        context_info: dict[str, Any] | None = None,
    ) -> T:
        """Execute an operation with retry logic.

        Rate limit errors (429) are retried up to max_rate_limit_retries times (default: 20).
        Other errors (5xx, network, timeout) respect max_retries limit.
        Client errors (4xx except 429) are not retried.

        Args:
            operation: Callable that performs the operation
            operation_name: Human-readable name for logging
            max_retries: Maximum retries for non-rate-limit errors.
                If None, uses retry_handler.config.max_retries
            logger: Optional logger for logging retry attempts
            context_info: Optional context for logging (e.g., file name, endpoint)

        Returns:
            Result from the operation

        Raises:
            Exception: If operation fails after all retry attempts

        """
        if max_retries is None:
            max_retries = self.retry_handler.config.max_retries

        max_rate_limit_retries = self.retry_handler.config.max_rate_limit_retries

        last_exception: Exception | None = None
        total_attempts = 0  # All attempts including rate limits
        non_rate_limit_attempts = 0  # Only non-rate-limit errors
        rate_limit_attempts = 0  # Only rate-limit errors

        while True:
            try:
                # Execute the operation
                return operation()

            except (ViRateLimitError, httpx.HTTPStatusError) as e:
                # Check if it's a rate limit error
                is_rate_limit = self._is_rate_limit_error(e)

                if is_rate_limit:
                    # Rate limit: retry up to max_rate_limit_retries times
                    rate_limit_attempts += 1
                    last_exception = e

                    if rate_limit_attempts <= max_rate_limit_retries:
                        retry_after = self._get_retry_after(e)

                        sleep_time = self.retry_handler.calculate_backoff(
                            rate_limit_attempts - 1, retry_after
                        )

                        if logger:
                            self._log_retry(
                                logger=logger,
                                operation_name=operation_name,
                                error_type="rate_limit",
                                attempt=rate_limit_attempts,
                                sleep_time=sleep_time,
                                context=context_info,
                                max_attempts=max_rate_limit_retries,
                            )

                        time.sleep(sleep_time)
                        total_attempts += 1
                    else:
                        # Max rate limit retries exceeded
                        if logger:
                            self._log_failure(
                                logger,
                                operation_name,
                                rate_limit_attempts,
                                context_info,
                                e,
                            )
                        raise

                else:
                    # Server error (5xx): retry with limit
                    non_rate_limit_attempts += 1
                    last_exception = e

                    if non_rate_limit_attempts <= max_retries:
                        status_code = self._get_status_code(e)
                        retry_after = self._get_retry_after(e)

                        sleep_time = self.retry_handler.calculate_backoff(
                            non_rate_limit_attempts - 1, retry_after
                        )

                        if logger:
                            self._log_retry(
                                logger=logger,
                                operation_name=operation_name,
                                error_type=f"server_error_{status_code}",
                                attempt=non_rate_limit_attempts,
                                max_attempts=max_retries,
                                sleep_time=sleep_time,
                                context=context_info,
                            )

                        time.sleep(sleep_time)
                        total_attempts += 1
                    else:
                        # Max retries exceeded
                        if logger:
                            self._log_failure(
                                logger,
                                operation_name,
                                non_rate_limit_attempts,
                                context_info,
                                e,
                            )
                        raise

            except (
                ViServerError,
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RequestError,
                ViTimeoutError,
                ViNetworkError,
            ) as e:
                # Server/network/timeout errors: retry with limit
                non_rate_limit_attempts += 1
                last_exception = e

                if non_rate_limit_attempts <= max_retries:
                    error_type = self._classify_error(e)

                    sleep_time = self.retry_handler.calculate_backoff(
                        non_rate_limit_attempts - 1
                    )

                    if logger:
                        self._log_retry(
                            logger=logger,
                            operation_name=operation_name,
                            error_type=error_type,
                            attempt=non_rate_limit_attempts,
                            max_attempts=max_retries,
                            sleep_time=sleep_time,
                            context=context_info,
                        )

                    time.sleep(sleep_time)
                    total_attempts += 1
                else:
                    # Max retries exceeded - wrap httpx exceptions in Vi exceptions
                    if logger:
                        self._log_failure(
                            logger,
                            operation_name,
                            non_rate_limit_attempts,
                            context_info,
                            e,
                        )
                    # Wrap httpx exceptions in Vi exceptions for consistent API
                    if isinstance(e, httpx.TimeoutException):
                        raise ViTimeoutError(str(e)) from e
                    elif isinstance(e, (httpx.NetworkError, httpx.RequestError)):
                        raise ViNetworkError(str(e)) from e
                    else:
                        raise

            except Exception as e:
                # Don't retry client errors (4xx, validation, auth, etc.)
                if logger:
                    logger.error(
                        f"{operation_name} failed with non-retryable error: {e}",
                        context=context_info,
                    )
                raise

        # Should never reach here, but for type safety
        if last_exception:
            raise last_exception
        raise RuntimeError(f"{operation_name} failed after all retry attempts")

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error.

        Args:
            error: Exception to check

        Returns:
            True if error is a rate limit error, False otherwise

        """
        if isinstance(error, ViRateLimitError):
            return True
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code == 429
        return False

    def _get_status_code(self, error: Exception) -> int | None:
        """Extract HTTP status code from error.

        Args:
            error: Exception to check

        Returns:
            HTTP status code, or None if not found

        """
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code
        if hasattr(error, "status_code"):
            return error.status_code
        return None

    def _get_retry_after(self, error: Exception) -> str | None:
        """Extract Retry-After header from error.

        Args:
            error: Exception to check

        Returns:
            Retry-After header value, or None if not found

        """
        if hasattr(error, "retry_after"):
            return error.retry_after
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.headers.get("Retry-After")
        return None

    def _classify_error(self, error: Exception) -> str:
        """Classify error type for logging.

        Args:
            error: Exception to check

        Returns:
            Error type string

        """
        if isinstance(error, (httpx.TimeoutException, ViTimeoutError)):
            return "timeout"
        if isinstance(error, httpx.NetworkError):
            return "network"
        if isinstance(error, ViServerError):
            return "server"
        return "unknown"

    def _log_retry(
        self,
        logger: Any,
        operation_name: str,
        error_type: str,
        attempt: int,
        sleep_time: float,
        context: dict[str, Any] | None = None,
        max_attempts: int | None = None,
    ) -> None:
        """Log retry attempt.

        Args:
            logger: Logger to use
            operation_name: Name of the operation
            error_type: Type of error
            attempt: Current attempt number
            sleep_time: Time to sleep
            context: Context to log
            max_attempts: Maximum number of attempts (-1 for unlimited)

        """
        attempt_str = (
            f"attempt {attempt}"
            if max_attempts == -1
            else f"attempt {attempt}/{max_attempts}"
        )

        message = (
            f"{operation_name} - {error_type}, "
            f"retrying in {sleep_time:.2f}s ({attempt_str})"
        )

        log_context = {
            "error_type": error_type,
            "attempt": attempt,
            "sleep_time": sleep_time,
        }
        if max_attempts:
            log_context["max_attempts"] = max_attempts
        if context:
            log_context.update(context)

        logger.warning(message, **log_context)

    def _log_failure(
        self,
        logger: Any,
        operation_name: str,
        attempts: int,
        context: dict[str, Any] | None,
        error: Exception,
    ) -> None:
        """Log final failure after all retries.

        Args:
            logger: Logger to use
            operation_name: Name of the operation
            attempts: Number of attempts
            context: Context to log
            error: Exception that caused the failure

        """
        logger.error(
            f"{operation_name} failed after {attempts} retries: {error}",
            attempts=attempts,
            context=context,
        )
