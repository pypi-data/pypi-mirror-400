#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   logger.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Enhanced logger for Vi SDK with structured logging capabilities.
"""

import inspect
import logging
import threading
import time
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

from vi.logging.config import LoggingConfig
from vi.logging.handlers import StructuredLogHandler


class ViLogger:
    """Enhanced logger for Vi SDK with structured logging capabilities."""

    def __init__(self, name: str, config: LoggingConfig | None = None):
        self.name = name
        self._logger = logging.getLogger(f"vi.{name}")
        self._config = config or LoggingConfig()

        # Context tracking with thread-safe lock
        self._context: dict[str, Any] = {}
        self._context_lock = threading.Lock()

    def _log_with_context(
        self, level: int, message: str, extra: dict[str, Any] | None = None, **kwargs
    ):
        """Log a message with current context."""
        log_extra = {}

        # Add current context (thread-safe copy)
        with self._context_lock:
            if self._context:
                log_extra.update(self._context)

        # Add provided extra fields
        if extra:
            log_extra.update(extra)

        # Add any additional kwargs
        log_extra.update(kwargs)

        self._logger.log(level, message, extra=log_extra)

    def debug(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log a debug message."""
        self._log_with_context(logging.DEBUG, message, extra, **kwargs)

    def info(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log an info message."""
        self._log_with_context(logging.INFO, message, extra, **kwargs)

    def warning(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log a warning message."""
        self._log_with_context(logging.WARNING, message, extra, **kwargs)

    def error(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log an error message."""
        self._log_with_context(logging.ERROR, message, extra, **kwargs)

    def critical(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log a critical message."""
        self._log_with_context(logging.CRITICAL, message, extra, **kwargs)

    def exception(self, message: str, extra: dict[str, Any] | None = None, **kwargs):
        """Log an exception with traceback."""
        log_extra = extra or {}
        log_extra.update(kwargs)
        self._logger.exception(message, extra=log_extra)

    def set_context(self, **context):
        """Set context fields that will be included in all subsequent logs."""
        with self._context_lock:
            self._context.update(context)

    def clear_context(self):
        """Clear all context fields."""
        with self._context_lock:
            self._context.clear()

    def remove_context(self, *keys):
        """Remove specific context fields."""
        with self._context_lock:
            for key in keys:
                self._context.pop(key, None)

    @contextmanager
    def context(self, **context):
        """Temporary context manager for adding context fields."""
        with self._context_lock:
            original_context = self._context.copy()
            self._context.update(context)
        try:
            yield
        finally:
            with self._context_lock:
                self._context = original_context

    @contextmanager
    def operation(self, operation_name: str, **context):
        """Context manager for tracking operations with timing."""
        operation_id = str(uuid4())
        start_time = time.time()

        # Set operation context
        operation_context = {
            "operation_id": operation_id,
            "operation_name": operation_name,
            **context,
        }

        with self.context(**operation_context):
            self.info(f"Starting operation: {operation_name}")

            try:
                yield operation_id
                duration = time.time() - start_time
                self.info(
                    f"Operation completed: {operation_name}",
                    duration_ms=round(duration * 1000, 2),
                    status="success",
                )
            except Exception as e:
                duration = time.time() - start_time
                self.error(
                    f"Operation failed: {operation_name}",
                    duration_ms=round(duration * 1000, 2),
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                raise

    def log_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: Any | None = None,
        **context,
    ):
        """Log an HTTP request."""
        if not self._config.log_requests:
            return

        log_data = {
            "event_type": "http_request",
            "http_method": method,
            "url": url,
            **context,
        }

        if self._config.log_request_headers and headers:
            # Filter out sensitive headers
            safe_headers = {
                k: v
                for k, v in headers.items()
                if k.lower() not in ("authorization", "x-api-key", "cookie")
            }
            log_data["request_headers"] = safe_headers

        if self._config.log_request_body and body is not None:
            # Truncate large bodies
            body_str = str(body)
            if len(body_str) > self._config.max_request_body_size:
                body_str = body_str[: self._config.max_request_body_size] + "..."
            log_data["request_body"] = body_str

        self.debug("HTTP request", extra=log_data)

    def log_response(
        self,
        status_code: int,
        headers: dict[str, str] | None = None,
        body: Any | None = None,
        duration_ms: float | None = None,
        **context,
    ):
        """Log an HTTP response."""
        if not self._config.log_responses:
            return

        log_data = {
            "event_type": "http_response",
            "status_code": status_code,
            **context,
        }

        if duration_ms is not None:
            log_data["duration_ms"] = duration_ms

        if self._config.log_response_headers and headers:
            log_data["response_headers"] = headers

        if self._config.log_response_body and body is not None:
            # Truncate large bodies
            body_str = str(body)
            if len(body_str) > self._config.max_response_body_size:
                body_str = body_str[: self._config.max_response_body_size] + "..."
            log_data["response_body"] = body_str

        # Choose log level based on status code
        if status_code >= 500:
            self.error("HTTP response", extra=log_data)
        elif status_code >= 400:
            self.warning("HTTP response", extra=log_data)
        else:
            self.debug("HTTP response", extra=log_data)

    def log_error(self, error: Exception, operation: str | None = None, **context):
        """Log an error with structured information."""
        error_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context,
        }

        if operation:
            error_data["operation"] = operation

        # Add error details if available
        if hasattr(error, "error_code"):
            error_data["error_code"] = str(error.error_code)

        if hasattr(error, "status_code"):
            error_data["status_code"] = error.status_code

        if hasattr(error, "details"):
            error_data["error_details"] = error.details

        self.error("Error occurred", extra=error_data)


def get_logger(name: str, config: LoggingConfig | None = None) -> ViLogger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name (typically module name)
        config: Optional logging configuration

    Returns:
        ViLogger instance

    """
    return ViLogger(name, config)


def get_module_logger(config: LoggingConfig | None = None) -> ViLogger:
    """Get a logger for the calling module."""
    frame = inspect.currentframe().f_back
    module_name = frame.f_globals.get("__name__", "unknown")

    # Remove 'vi.' prefix if present
    if module_name.startswith("vi."):
        module_name = module_name[3:]

    return get_logger(module_name, config)


def configure_logging(config: LoggingConfig | None = None) -> LoggingConfig:
    """Configure logging settings.

    Args:
        config: Logging configuration. If None, uses default configuration.

    Returns:
        The configured logging configuration.

    """
    if config is None:
        config = LoggingConfig()

    # Configure Python's logging system
    root_logger = logging.getLogger("vi")
    root_logger.setLevel(config.level.level_int)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler if enabled
    if config.enable_console:
        console_handler = StructuredLogHandler(config)
        root_logger.addHandler(console_handler)

    # Add file handler if enabled
    if config.enable_file and config.log_file_path:
        file_handler = StructuredLogHandler(config, log_to_file=True)
        root_logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False

    return config
