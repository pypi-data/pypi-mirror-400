#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   console_utils.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Console utilities for redirecting output to Rich formatting.
"""

import logging
import queue
import sys
import threading
import time
import warnings
from contextlib import contextmanager
from io import StringIO

from rich import print as rprint
from rich.console import Console

# Third-party library loggers
TARGET_LOGGERS = [
    "transformers",
    "accelerate",
    "torch",
    "bitsandbytes",
    "peft",
    "xgrammar",
]

# Configuration for non-blocking output
_FLUSH_INTERVAL_SECONDS = 0.1  # Flush every 100ms
_MAX_BATCH_SIZE = 50  # Max lines to batch before forcing flush


class _WarningCaptureHandler:
    """Custom warning handler that captures warnings to a buffer."""

    def __init__(
        self,
        warnings_buffer: list[str],
        output_queue: "queue.Queue[tuple[str, str]] | None" = None,
    ):
        self.warnings_buffer = warnings_buffer
        self.output_queue = output_queue

    def __call__(
        self,
        message: str | Warning,
        category: type[Warning],
        filename: str,
        lineno: int,
        _file=None,
        _line: str | None = None,
    ):
        """Capture warning to buffer or queue for async output."""
        warning_msg = f"{filename}:{lineno}: {category.__name__}: {message}"
        if self.output_queue is not None:
            self.output_queue.put(("warning", warning_msg))
        else:
            self.warnings_buffer.append(warning_msg)


class RichLogHandler(logging.Handler):
    """Custom logging handler that redirects log messages to rich.print."""

    def __init__(self, output_queue: "queue.Queue[tuple[str, str]] | None" = None):
        """Initialize the Rich log handler with optional queue for async output.

        Args:
            output_queue: Optional queue for non-blocking output. If None, uses buffering.

        """
        super().__init__()
        self.log_buffer: list[tuple[str, str]] = []
        self.output_queue = output_queue

    def emit(self, record: logging.LogRecord):
        """Capture log records to buffer or queue.

        Args:
            record: The log record to capture.

        """
        try:
            msg = self.format(record)
            if self.output_queue is not None:
                self.output_queue.put((record.levelname.lower(), msg))
            else:
                self.log_buffer.append((record.levelname, msg))
        except Exception:
            self.handleError(record)

    def flush_to_rich(self):
        """Flush captured log messages to rich.print.

        Outputs buffered log messages with appropriate colors and icons.
        """
        for level, msg in self.log_buffer:
            _print_styled(level.lower(), msg)
        self.log_buffer.clear()


def _print_styled(level: str, msg: str, console: Console | None = None):
    """Print message with appropriate Rich styling.

    Args:
        level: Log level or message type (info, warning, error, debug, stdout, stderr)
        msg: Message content
        console: Optional Rich console to use (defaults to rprint)

    """
    output_fn = console.print if console else rprint
    if level == "warning":
        output_fn(f"[yellow]⚠ {msg}[/yellow]")
    elif level == "error":
        output_fn(f"[red]✗ {msg}[/red]")
    elif level == "info":
        output_fn(f"[blue]ℹ {msg}[/blue]")
    elif level == "debug":
        output_fn(f"[dim]🐛 {msg}[/dim]")
    elif level in ("stdout", "stderr"):
        output_fn(msg)
    else:
        output_fn(f"[dim]{level}:[/dim] {msg}")


class _StreamCapture:
    """Captures stream output and queues it for async processing."""

    def __init__(
        self,
        stream_name: str,
        output_queue: "queue.Queue[tuple[str, str]] | None" = None,
    ):
        """Initialize stream capture.

        Args:
            stream_name: Name of the stream (e.g., "stdout", "stderr")
            output_queue: Optional queue for non-blocking output

        """
        self.stream_name = stream_name
        self.output_queue = output_queue
        self.buffer = StringIO()
        self._line_buffer = ""

    def write(self, text: str):
        """Write text to queue or buffer.

        Args:
            text: Text to write

        """
        if not text:
            return

        if self.output_queue is not None:
            # Non-blocking mode: accumulate into line buffer
            self._line_buffer += text

            # When we have complete lines, queue them
            while "\n" in self._line_buffer:
                line, self._line_buffer = self._line_buffer.split("\n", 1)
                if line.strip():
                    self.output_queue.put((self.stream_name, line))
        else:
            # Buffer mode for later flush
            self.buffer.write(text)

    def flush(self):
        """Flush any pending output."""
        # Flush any remaining partial line
        if self.output_queue is not None and self._line_buffer.strip():
            self.output_queue.put((self.stream_name, self._line_buffer.rstrip()))
            self._line_buffer = ""

    def get_buffered_content(self) -> str:
        """Get buffered content.

        Returns:
            Buffered content as string

        """
        return self.buffer.getvalue()


class _AsyncOutputProcessor:
    """Background thread that processes queued output and flushes to Rich console."""

    def __init__(
        self,
        output_queue: "queue.Queue[tuple[str, str]]",
        rich_console: Console,
    ):
        self.output_queue = output_queue
        self.rich_console = rich_console
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._pending_items: list[tuple[str, str]] = []

    def start(self):
        """Start the background output processor."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background processor and flush remaining output."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

        # Final flush of any remaining items
        self._flush_all_remaining()

    def _run(self):
        """Process background output."""
        last_flush_time = time.monotonic()

        while not self._stop_event.is_set():
            try:
                # Non-blocking get with short timeout
                item = self.output_queue.get(timeout=_FLUSH_INTERVAL_SECONDS / 2)
                self._pending_items.append(item)
            except queue.Empty:
                pass

            current_time = time.monotonic()
            should_flush = len(self._pending_items) >= _MAX_BATCH_SIZE or (
                self._pending_items
                and current_time - last_flush_time >= _FLUSH_INTERVAL_SECONDS
            )

            if should_flush:
                self._flush_batch()
                last_flush_time = current_time

    def _flush_batch(self):
        """Flush the current batch of pending items to the console."""
        if not self._pending_items:
            return

        # Collect items to flush
        items_to_flush = self._pending_items[:]
        self._pending_items.clear()

        # Group consecutive same-type messages for cleaner output
        for level, msg in items_to_flush:
            _print_styled(level, msg, self.rich_console)

    def _flush_all_remaining(self):
        """Flush all remaining items from queue and pending list."""
        # Drain queue
        while True:
            try:
                item = self.output_queue.get_nowait()
                self._pending_items.append(item)
            except queue.Empty:
                break

        # Flush everything
        self._flush_batch()


@contextmanager
def redirect_console(rich_console: Console | None = None):
    """Context manager to redirect stdout, stderr, and logging to rich.print.

    Captures and redirects console output from stdout, stderr, and specific
    third-party library loggers to Rich formatting for better display.

    When rich_console is provided, output is processed asynchronously in a
    background thread, making it non-blocking for the main thread. Output is
    batched and flushed periodically to minimize rendering overhead.

    Only logging messages at WARNING level and above are captured to reduce
    noise from verbose INFO and DEBUG messages.

    Args:
        rich_console: Optional Rich Console for real-time output. If provided,
            output is displayed asynchronously via a background thread.
            If None, output is buffered and displayed at the end.

    Yields:
        None - control is yielded back to the caller.

    """
    # Store original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_showwarning = warnings.showwarning

    # Create output queue for async processing (if using rich_console)
    output_queue: queue.Queue[tuple[str, str]] | None = None
    processor: _AsyncOutputProcessor | None = None

    if rich_console is not None:
        output_queue = queue.Queue()
        processor = _AsyncOutputProcessor(output_queue, rich_console)

    # Create capture objects
    stdout_capture = _StreamCapture("stdout", output_queue)
    stderr_capture = _StreamCapture("stderr", output_queue)
    warnings_buffer: list[str] = []

    # Custom warning handler
    custom_showwarning = _WarningCaptureHandler(warnings_buffer, output_queue)

    # Set up logging capture (only WARNING and above)
    rich_handler = RichLogHandler(output_queue)
    rich_handler.setLevel(logging.WARNING)

    # Get root logger and capture its current handlers and level
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    logger_states = {}
    for logger_name in TARGET_LOGGERS:
        logger = logging.getLogger(logger_name)
        logger_states[logger_name] = {
            "handlers": logger.handlers[:],
            "level": logger.level,
            "propagate": logger.propagate,
        }

    try:
        # Start background processor if using async mode
        if processor is not None:
            processor.start()

        # Redirect stdout and stderr to our capture objects
        sys.stdout = stdout_capture  # type: ignore[assignment]
        sys.stderr = stderr_capture  # type: ignore[assignment]
        warnings.showwarning = custom_showwarning

        # Add our rich handler to root logger (WARNING and above only)
        root_logger.addHandler(rich_handler)
        if root_logger.level < logging.WARNING:
            root_logger.setLevel(logging.WARNING)

        # Configure specific loggers to use our handler (WARNING and above only)
        for logger_name in TARGET_LOGGERS:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.addHandler(rich_handler)
            logger.setLevel(logging.WARNING)
            logger.propagate = False

        yield

    finally:
        # Flush any remaining stream content before cleanup
        stdout_capture.flush()
        stderr_capture.flush()

        # Restore original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        warnings.showwarning = original_showwarning

        # Restore logging configuration
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

        # Restore specific loggers
        for logger_name, state in logger_states.items():
            logger = logging.getLogger(logger_name)
            logger.handlers = state["handlers"]
            logger.setLevel(state["level"])
            logger.propagate = state["propagate"]

        # Stop background processor (will flush remaining items)
        if processor is not None:
            processor.stop()

        # If we're in buffered mode (no rich_console), print captured content now
        if rich_console is None:
            stdout_content = stdout_capture.get_buffered_content()
            stderr_content = stderr_capture.get_buffered_content()

            # Print captured content using rich.print if there's any content
            if stdout_content.strip():
                for line in stdout_content.strip().split("\n"):
                    if line.strip():  # Only print non-empty lines
                        rprint(line)

            if stderr_content.strip():
                for line in stderr_content.strip().split("\n"):
                    if line.strip():  # Only print non-empty lines
                        rprint(line)

            if warnings_buffer:
                for warning in warnings_buffer:
                    rprint(f"[yellow]warning:[/yellow] {warning}")

            # Flush any captured log messages
            rich_handler.flush_to_rich()
