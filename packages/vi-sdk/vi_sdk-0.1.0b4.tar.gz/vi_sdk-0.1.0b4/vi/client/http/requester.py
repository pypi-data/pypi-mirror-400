#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   requester.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK requester module.
"""

import json
import logging
import time
from typing import Any
from urllib.parse import urlencode, urljoin

import httpx
import msgspec
import vi.client.consts as CLIENT_CONSTS
from vi.api.responses import ViResponse
from vi.client.auth import Authentication
from vi.client.errors import create_error_from_response
from vi.client.http.retry import RetryConfig, RetryExecutor, RetryHandler
from vi.logging.logger import get_logger
from vi.version import get_user_agent

# Use structured logger instead of basic logging
logger = get_logger("client.http.requester")

# Keep httpx logger quiet
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


class Requester:
    """Simple, reliable HTTP client for Vi API.

    Features:
    - Automatic retry with exponential backoff and jitter
    - Retry-After header support
    - Configurable retry strategies
    - Proper error handling with helpful messages
    - Request/response logging
    - Sensible timeouts
    - Clean resource management
    - Connection pooling with configurable limits
    """

    def __init__(
        self,
        auth: Authentication,
        base_url: str,
        timeout: httpx.Timeout | None = None,
        max_retries: int | None = None,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        retry_config: RetryConfig | None = None,
    ):
        """Initialize Requester.

        Args:
            auth: Authentication instance
            base_url: Base URL for all requests
            timeout: Request timeout in seconds. If None, uses default timeouts.
            max_retries: Maximum number of retry attempts. Defaults to 3.
                Note: If retry_config is provided, this parameter is ignored.
            max_connections: Maximum number of concurrent connections. Defaults to 100.
            max_keepalive_connections: Maximum number of keep-alive connections. Defaults to 20.
            retry_config: Retry configuration. If None, uses default configuration.

        """
        self._auth = auth
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout or httpx.Timeout(
            connect=CLIENT_CONSTS.REQUEST_CONNECT_TIMEOUT_SECONDS,
            read=CLIENT_CONSTS.REQUEST_READ_TIMEOUT_SECONDS,
            write=CLIENT_CONSTS.REQUEST_WRITE_TIMEOUT_SECONDS,
            pool=CLIENT_CONSTS.REQUEST_POOL_TIMEOUT_SECONDS,
        )
        self._limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )

        # Initialize retry configuration
        if retry_config is None:
            # Use max_retries if provided, otherwise use default
            max_retries_value = max_retries or CLIENT_CONSTS.REQUEST_MAX_RETRIES
            self._retry_config = RetryConfig(max_retries=max_retries_value)
        else:
            self._retry_config = retry_config

        self._retry_handler = RetryHandler(self._retry_config)
        self._retry_executor = RetryExecutor(self._retry_handler)
        self._max_retries = self._retry_config.max_retries
        self._closed = False

        # Create httpx client with sensible defaults
        self._client = httpx.Client(
            timeout=self._timeout,
            limits=self._limits,
            headers=self._get_headers(),
            follow_redirects=True,
        )

        logger.debug(
            "Requester initialized",
            base_url=self._base_url,
            max_retries=self._max_retries,
            retry_strategy=self._retry_config.strategy.value,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )

    def __enter__(self):
        """Context manager entry.

        Returns:
            Self for use in with statements.

        Raises:
            RuntimeError: If requester is already closed.

        Example:
            ```python
            with Requester(auth, base_url) as requester:
                response = requester.get("/endpoint")
                # Automatic cleanup on exit
            ```

        """
        if self._closed:
            raise RuntimeError("Cannot use closed requester in context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        Returns:
            False to propagate any exception that occurred.

        """
        self.close()
        return False

    def close(self) -> None:
        """Close the HTTP client and release all resources.

        This method is idempotent and can be called multiple times safely.
        After calling close(), the requester should not be used for new requests.

        The method closes the underlying httpx client, which releases:
        - All open HTTP connections
        - Connection pool resources
        - Any pending requests

        Examples:
            Manual cleanup:

            ```python
            requester = Requester(auth, base_url)
            try:
                response = requester.get("/endpoint")
            finally:
                requester.close()
            ```

            Using context manager (recommended):

            ```python
            with Requester(auth, base_url) as requester:
                response = requester.get("/endpoint")
                # Automatic cleanup
            ```

        Note:
            It is safe to call this method multiple times. Subsequent calls
            will be no-ops if the requester is already closed.

        """
        # Return early if already closed (idempotent)
        if self._closed:
            return

        # Close the httpx client
        if hasattr(self, "_client") and self._client is not None:
            try:
                self._client.close()
                logger.debug("Requester closed and resources released")
            except Exception as e:  # noqa: BLE001
                # Log but suppress exceptions during cleanup
                logger.debug(f"Exception during requester cleanup: {e}")

        # Mark as closed
        self._closed = True

    def __del__(self):
        """Cleanup on deletion.

        Ensures resources are released even if close() was not called explicitly.
        Exceptions are suppressed to prevent issues during interpreter shutdown.
        """
        try:
            self.close()
        except Exception:  # noqa: BLE001
            # Suppress exceptions during cleanup - critical for __del__
            # as the interpreter may be in an inconsistent state
            pass

    @property
    def is_closed(self) -> bool:
        """Check if the requester has been closed.

        Returns:
            True if the requester is closed, False otherwise.

        Example:
            ```python
            requester = Requester(auth, base_url)
            print(requester.is_closed)  # False
            requester.close()
            print(requester.is_closed)  # True
            ```

        """
        return self._closed

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": get_user_agent(),
        }

        # Add authentication headers
        headers.update(self._auth.get_headers())

        return headers

    def _build_link(self, path: str, params: dict[str, Any] | None = None) -> str:
        """Build complete URL with query parameters."""
        if not path.startswith("/"):
            path = "/" + path

        url = urljoin(self._base_url, path)

        if params:
            # Filter out None values and convert to strings
            clean_params = {}
            for key, value in params.items():
                if value is not None:
                    if isinstance(value, bool):
                        clean_params[key] = str(value).lower()
                    else:
                        clean_params[key] = str(value)

            if clean_params:
                url += "?" + urlencode(clean_params)

        return url

    def _handle_response(
        self,
        response: httpx.Response,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Handle HTTP response and raise appropriate errors.

        Args:
            response: The HTTP response object
            response_type: Expected response type for successful responses
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            Parsed response for successful requests, None for ignored error codes

        Raises:
            ViError: For error status codes not in ignore_error_codes list

        """
        logger.debug(
            f"HTTP {response.status_code} {response.request.method} {response.url} "
            f"({response.elapsed.total_seconds():.2f}s)"
        )

        # Handle successful responses
        if 200 <= response.status_code < 300:
            try:
                if response_type:
                    return msgspec.json.decode(response.text, type=response_type)
                return response.json()
            except json.JSONDecodeError:
                # Return text response wrapped in dict if not JSON
                return {
                    "data": response.text,
                    "content_type": response.headers.get("content-type"),
                }

        # Check if this error code should be ignored
        if ignore_error_codes and response.status_code in ignore_error_codes:
            logger.debug(
                f"Ignoring error status code {response.status_code} "
                f"(in ignore_error_codes list: {ignore_error_codes})"
            )
            return None

        # Extract trace ID for logging
        trace_context = response.headers.get("x-cloud-trace-context")
        trace_id = trace_context.split("/")[0] if trace_context else None

        # Log error with trace ID if available
        log_context = {
            "status_code": response.status_code,
            "method": response.request.method,
            "url": str(response.url),
        }
        if trace_id:
            log_context["trace_id"] = trace_id

        logger.error("Request failed", **log_context)

        error = create_error_from_response(response=response)
        raise error

    def _request_with_retry(
        self,
        method: str,
        url: str,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
        **kwargs,
    ) -> ViResponse | dict | None:
        """Make request with retry logic using RetryExecutor.

        Rate limit errors are retried up to max_rate_limit_retries times (default: 20).
        Other errors (timeout, network, server) respect max_retries limit.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            response_type: Expected response type for successful responses
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)
            **kwargs: Additional arguments to pass to httpx request

        Returns:
            Parsed response for successful requests, None for ignored error codes

        Raises:
            RuntimeError: If the requester has been closed.
            ViError: For errors not in ignore_error_codes list after all retry attempts

        """
        # Check if requester is closed
        if self._closed:
            raise RuntimeError(
                "Cannot make requests with a closed requester. "
                "Create a new requester or client instance."
            )

        # Log the request
        logger.log_request(method, url, headers=kwargs.get("headers"))

        # Use RetryExecutor for consistent retry behavior
        return self._retry_executor.execute(
            operation=lambda: self._make_request(
                method, url, response_type, ignore_error_codes, **kwargs
            ),
            operation_name=f"{method} {url}",
            max_retries=self._max_retries,
            logger=logger,
            context_info={"method": method, "url": url},
        )

    def _make_request(
        self,
        method: str,
        url: str,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
        **kwargs,
    ) -> ViResponse | dict | None:
        """Make a single HTTP request without retry logic.

        This is the actual request operation. Retries are handled by
        the caller using RetryExecutor.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            response_type: Expected response type for successful responses
            ignore_error_codes: List of HTTP status codes to ignore
            **kwargs: Additional arguments to pass to httpx request

        Returns:
            Parsed response for successful requests, None for ignored error codes

        Raises:
            ViError: For HTTP errors
            httpx.HTTPStatusError: For HTTP errors
            httpx.TimeoutException: For timeout errors
            httpx.NetworkError: For network errors

        """
        attempt_start = time.time_ns()

        logger.debug(f"Making {method} request to {url}")

        response = self._client.request(method, url, timeout=self._timeout, **kwargs)

        # Calculate timing
        attempt_duration = (time.time_ns() - attempt_start) / 1e6

        # Log the response
        logger.log_response(
            response.status_code,
            headers=dict(response.headers),
            duration_ms=attempt_duration,
        )

        return self._handle_response(response, response_type, ignore_error_codes)

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Make GET request.

        Args:
            path: API endpoint path
            params: Query parameters
            response_type: Response type
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            ViResponse, dict, or None (if error code was ignored)

        """
        url = self._build_link(path, params)
        return self._request_with_retry(
            "GET",
            url,
            response_type=response_type,
            ignore_error_codes=ignore_error_codes,
        )

    def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Make POST request.

        Args:
            path: API endpoint path
            json_data: JSON body data
            params: Query parameters
            response_type: Response type
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            ViResponse, dict, or None (if error code was ignored)

        """
        url = self._build_link(path, params)
        return self._request_with_retry(
            "POST",
            url,
            json=json_data,
            response_type=response_type,
            ignore_error_codes=ignore_error_codes,
        )

    def put(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Make PUT request.

        Args:
            path: API endpoint path
            json_data: JSON body data
            params: Query parameters
            response_type: Response type
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            ViResponse, dict, or None (if error code was ignored)

        """
        url = self._build_link(path, params)
        return self._request_with_retry(
            "PUT",
            url,
            json=json_data,
            response_type=response_type,
            ignore_error_codes=ignore_error_codes,
        )

    def patch(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Make PATCH request.

        Args:
            path: API endpoint path
            json_data: JSON body data
            params: Query parameters
            response_type: Response type
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            ViResponse, dict, or None (if error code was ignored)

        """
        url = self._build_link(path, params)
        return self._request_with_retry(
            "PATCH",
            url,
            json=json_data,
            response_type=response_type,
            ignore_error_codes=ignore_error_codes,
        )

    def delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        response_type: type[ViResponse] | type[dict] | None = None,
        ignore_error_codes: list[int] | None = None,
    ) -> ViResponse | dict | None:
        """Make DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters
            response_type: Response type
            ignore_error_codes: List of HTTP status codes to ignore (return None instead of raising)

        Returns:
            ViResponse, dict, or None (if error code was ignored)

        """
        url = self._build_link(path, params)
        return self._request_with_retry(
            "DELETE",
            url,
            response_type=response_type,
            ignore_error_codes=ignore_error_codes,
        )
