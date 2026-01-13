#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   formatters.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Log formatters for Vi SDK structured logging.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from vi.logging.config import LogFormat, LoggingConfig


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, config: LoggingConfig):
        """Initialize the JSON formatter.

        Args:
            config: Logging configuration.

        """
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted log string.

        """
        log_entry = self._build_base_entry(record)

        # Add message
        if record.getMessage():
            log_entry["message"] = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        self._add_extra_fields(log_entry, record)

        # Add configured extra fields
        if self.config.extra_fields:
            log_entry.update(self.config.extra_fields)

        return json.dumps(
            log_entry, default=self._serialize_to_json, separators=(",", ":")
        )

    def _build_base_entry(self, record: logging.LogRecord) -> dict[str, Any]:
        """Build the base log entry structure.

        Args:
            record: The log record.

        Returns:
            Base log entry dictionary with timestamp, level, source, etc.

        """
        entry = {}

        if self.config.include_timestamp:
            entry["timestamp"] = datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat()

        if self.config.include_level:
            entry["level"] = record.levelname

        if self.config.include_logger_name:
            entry["logger"] = record.name

        if self.config.include_thread_info:
            entry["thread"] = {"id": record.thread, "name": record.threadName}

        if self.config.include_process_info:
            entry["process"] = {"id": record.process, "name": record.processName}

        # Add source location
        entry["source"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        return entry

    def _add_extra_fields(self, log_entry: dict[str, Any], record: logging.LogRecord):
        """Add extra fields from the log record.

        Args:
            log_entry: The log entry dictionary to add fields to.
            record: The log record containing extra fields.

        """
        # Standard fields to exclude from extras
        standard_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "getMessage",
            "exc_info",
            "exc_text",
            "stack_info",
        }

        # Add any extra fields that aren't standard
        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith("_"):
                log_entry[key] = value

    def _serialize_to_json(self, obj: Any) -> Any:
        """Serialize non-standard types to JSON.

        Args:
            obj: The object to serialize.

        Returns:
            JSON-serializable representation of the object.

        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for human-readable logs."""

    def __init__(self, config: LoggingConfig):
        """Initialize the plain text formatter.

        Args:
            config: Logging configuration.

        """
        super().__init__()
        self.config = config

        # Build format string based on config
        format_parts = []

        if config.include_timestamp:
            format_parts.append("%(asctime)s")

        if config.include_level:
            format_parts.append("[%(levelname)s]")

        if config.include_logger_name:
            format_parts.append("%(name)s")

        format_parts.append("%(message)s")

        self._format = " ".join(format_parts)

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as plain text.

        Args:
            record: The log record to format.

        Returns:
            Plain text formatted log string.

        """
        formatter = logging.Formatter(self._format)
        return formatter.format(record)


class PrettyFormatter(JSONFormatter):
    """Pretty-printed JSON formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as pretty-printed JSON.

        Args:
            record: The log record to format.

        Returns:
            Pretty-printed JSON formatted log string.

        """
        log_entry = self._build_base_entry(record)

        # Add message
        if record.getMessage():
            log_entry["message"] = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        self._add_extra_fields(log_entry, record)

        # Add configured extra fields
        if self.config.extra_fields:
            log_entry.update(self.config.extra_fields)

        return json.dumps(log_entry, default=self._serialize_to_json, indent=2)


def get_formatter(config: LoggingConfig) -> logging.Formatter:
    """Get the appropriate formatter based on configuration.

    Args:
        config: Logging configuration.

    Returns:
        The appropriate formatter instance.

    """
    if config.format == LogFormat.JSON:
        return JSONFormatter(config)
    if config.format == LogFormat.PLAIN:
        return PlainFormatter(config)
    if config.format == LogFormat.PRETTY:
        return PrettyFormatter(config)
    # Default to JSON
    return JSONFormatter(config)
