#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   handlers.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Log handlers for Vi SDK structured logging.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import TextIO

from vi.logging.config import LoggingConfig
from vi.logging.formatters import get_formatter


class StructuredLogHandler(logging.Handler):
    """Structured log handler that supports both console and file output.

    This handler formats logs according to the configured format and
    outputs them to the appropriate destination.
    """

    def __init__(
        self,
        config: LoggingConfig,
        log_to_file: bool = False,
        stream: TextIO | None = None,
    ):
        """Initialize the structured log handler.

        Args:
            config: Logging configuration.
            log_to_file: Whether to log to file instead of console.
            stream: Optional output stream (defaults to stderr for console).

        """
        super().__init__()
        self.config = config
        self.log_to_file = log_to_file

        # Set up the formatter
        self.setFormatter(get_formatter(config))

        # Set up the output stream or file
        if log_to_file and config.log_file_path:
            # Use rotating file handler for file output
            self.file_handler = RotatingFileHandler(
                config.log_file_path,
                maxBytes=config.max_log_size,
                backupCount=5,
                encoding="utf-8",
            )
            self.file_handler.setFormatter(self.formatter)
        else:
            # Use console output
            self.stream = stream or sys.stderr
            self.file_handler = None

    def emit(self, record: logging.LogRecord):
        """Emit a log record.

        Args:
            record: The log record to emit.

        """
        try:
            if self.file_handler:
                # Delegate to file handler
                self.file_handler.emit(record)
            else:
                # Handle console output
                msg = self.format(record)
                self.stream.write(msg + "\n")
                self.stream.flush()
        except (OSError, ValueError):
            self.handleError(record)

    def close(self):
        """Close the handler."""
        if self.file_handler:
            self.file_handler.close()
        super().close()


class BufferedHandler(logging.Handler):
    """Buffered handler for high-throughput logging scenarios.

    This handler buffers log records and flushes them in batches
    to improve performance in high-volume logging scenarios.
    """

    def __init__(self, config: LoggingConfig, buffer_size: int = 100):
        """Initialize the buffered handler.

        Args:
            config: Logging configuration.
            buffer_size: Number of records to buffer before flushing.

        """
        super().__init__()
        self.config = config
        self.buffer_size = buffer_size
        self.buffer = []

        # Set up the underlying handler
        self.target_handler = StructuredLogHandler(config)
        self.setFormatter(self.target_handler.formatter)

    def emit(self, record: logging.LogRecord):
        """Buffer a log record.

        Args:
            record: The log record to buffer.

        """
        self.buffer.append(record)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        """Flush buffered records."""
        if not self.buffer:
            return

        try:
            for record in self.buffer:
                self.target_handler.emit(record)
            self.buffer.clear()
        except Exception:
            # If flushing fails, we still need to clear the buffer
            # to prevent memory leaks
            self.buffer.clear()
            raise

    def close(self):
        """Close the handler and flush remaining records."""
        self.flush()
        self.target_handler.close()
        super().close()
