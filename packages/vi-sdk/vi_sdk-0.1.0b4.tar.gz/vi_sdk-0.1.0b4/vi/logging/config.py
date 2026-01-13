#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   config.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Logging configuration for Vi SDK.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from vi.consts import DEFAULT_LOG_DIR


class LogLevel(Enum):
    """Log levels supported by Vi SDK."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"

    @property
    def level_int(self) -> int:
        """Get the integer value for the log level.

        Returns:
            The integer log level value.

        """
        return getattr(logging, self.value)


class LogFormat(Enum):
    """Log formats supported by Vi SDK."""

    JSON = "json"
    PLAIN = "plain"
    PRETTY = "pretty"


@dataclass
class LoggingConfig:
    """Configuration for Vi SDK logging.

    This class provides structured logging to various output formats.

    Attributes:
        level: Log level to use.
        format: Log format to use.
        enable_console: Whether to log to console.
        enable_file: Whether to log to file.
        log_file_path: Path to log file.
        include_timestamp: Whether to include timestamp in log.
        include_level: Whether to include log level in log.
        include_logger_name: Whether to include logger name in log.
        include_thread_info: Whether to include thread info in log.
        include_process_info: Whether to include process info in log.
        log_requests: Whether to log requests.
        log_responses: Whether to log responses.
        log_request_headers: Whether to log request headers.
        log_response_headers: Whether to log response headers.
        log_request_body: Whether to log request body.
        log_response_body: Whether to log response body.
        max_log_size: Maximum size of log file.
        max_request_body_size: Maximum size of request body to log.
        max_response_body_size: Maximum size of response body to log.
        respect_environment: Whether to respect environment variables.
        extra_fields: Extra fields to include in log.

    """

    # Basic logging configuration
    level: LogLevel = field(default_factory=lambda: LogLevel.DEBUG)
    format: LogFormat = field(default_factory=lambda: LogFormat.JSON)

    # Output configuration
    enable_console: bool = False  # Console logging is now opt-in
    enable_file: bool = True  # File logging is now default
    log_file_path: str | None = None  # Will be auto-generated if None

    # Structured logging options
    include_timestamp: bool = True
    include_level: bool = True
    include_logger_name: bool = True
    include_thread_info: bool = False
    include_process_info: bool = False

    # SDK-specific logging
    log_requests: bool = True
    log_responses: bool = False  # Can contain sensitive data
    log_request_headers: bool = False  # Can contain auth tokens
    log_response_headers: bool = False
    log_request_body: bool = False  # Can contain sensitive data
    log_response_body: bool = False  # Can be large

    # Performance and filtering
    max_log_size: int = 1024 * 1024  # 1MB default
    max_request_body_size: int = 1024  # 1KB for request body logging
    max_response_body_size: int = 1024  # 1KB for response body logging

    # Environment-based overrides
    respect_environment: bool = True

    # Additional context
    extra_fields: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Apply environment-based configuration overrides and set up log file path."""
        if self.respect_environment:
            self._apply_environment_overrides()

        # Auto-generate log file path if not provided and file logging is enabled
        if self.enable_file and self.log_file_path is None:
            self.log_file_path = self._generate_log_file_path()

    def _apply_environment_overrides(self):
        """Apply configuration from environment variables.

        Reads various VI_* environment variables to override configuration.
        """
        # Log level
        env_level = os.getenv("VI_LOG_LEVEL", "").upper()
        if env_level and hasattr(LogLevel, env_level):
            self.level = LogLevel[env_level]

        # Log format
        env_format = os.getenv("VI_LOG_FORMAT", "").lower()
        if env_format and hasattr(LogFormat, env_format.upper()):
            self.format = LogFormat(env_format)

        # Boolean flags
        bool_env_vars = {
            "VI_ENABLE_CONSOLE": "enable_console",
            "VI_ENABLE_FILE": "enable_file",
            "VI_LOG_REQUESTS": "log_requests",
            "VI_LOG_RESPONSES": "log_responses",
            "VI_LOG_REQUEST_HEADERS": "log_request_headers",
            "VI_LOG_RESPONSE_HEADERS": "log_response_headers",
            "VI_LOG_REQUEST_BODY": "log_request_body",
            "VI_LOG_RESPONSE_BODY": "log_response_body",
        }

        for env_var, attr_name in bool_env_vars.items():
            env_value = os.getenv(env_var, "").lower()
            if env_value in ("true", "1", "yes", "on"):
                setattr(self, attr_name, True)
            elif env_value in ("false", "0", "no", "off"):
                setattr(self, attr_name, False)

        # File logging
        log_file = os.getenv("VI_LOG_FILE")
        if log_file:
            self.enable_file = True
            self.log_file_path = log_file

        # Numeric values
        max_log_size = os.getenv("VI_MAX_LOG_SIZE")
        if max_log_size and max_log_size.isdigit():
            self.max_log_size = int(max_log_size)

    def _generate_log_file_path(self) -> str:
        """Generate a timestamped log file path in the user's home directory.

        Returns:
            The generated log file path string.

        """
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[
            :-3
        ]  # Include milliseconds

        # Create log file path
        log_file = DEFAULT_LOG_DIR / f"{timestamp}.log"

        return str(log_file)
