#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   utils.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Utility functions for NIM deployment.
"""

import threading
import time
from contextlib import contextmanager
from typing import Any

import httpx
from rich.console import Console
from rich.progress import (
    BarColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from vi.utils.progress import ViProgress


def format_bytes(bytes_val: int) -> str:
    """Format bytes into human-readable format.

    Args:
        bytes_val: Number of bytes.

    Returns:
        Formatted string (e.g., "1.5 GB", "512 MB").

    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"


def get_status_color(status: str) -> str:
    """Get color for layer status.

    Args:
        status: The status string from Docker.

    Returns:
        Rich color code.

    """
    status_lower = status.lower()
    if "pull complete" in status_lower or "already exists" in status_lower:
        return "green"
    if "downloading" in status_lower:
        return "cyan"
    if "extracting" in status_lower:
        return "yellow"
    if "waiting" in status_lower:
        return "dim"
    if "verifying" in status_lower:
        return "magenta"
    return "white"


class LayerProgress:
    """Track progress for a single Docker layer."""

    def __init__(self, layer_id: str) -> None:
        """Initialize layer progress tracker.

        Args:
            layer_id: The Docker layer ID.

        """
        self.layer_id = layer_id
        self.status = "Waiting"
        self.current = 0
        self.total = 0
        self.last_update = time.time()
        self.last_bytes = 0
        self.speed = 0.0

    def update(self, status: str, current: int, total: int) -> None:
        """Update layer progress.

        Args:
            status: Current status of the layer.
            current: Current bytes downloaded/extracted.
            total: Total bytes for the layer.

        """
        now = time.time()
        if status:
            self.status = status

        if current > self.current:
            time_diff = now - self.last_update
            if time_diff > 0:
                bytes_diff = current - self.last_bytes
                self.speed = bytes_diff / time_diff
                self.last_update = now
                self.last_bytes = current

        self.current = current
        self.total = total

    def get_progress_percentage(self) -> float:
        """Get progress as percentage.

        Returns:
            Progress percentage (0-100).

        """
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100


def stream_container_logs(
    container: Any, log_stream_active: threading.Event, output_console: Console
) -> None:
    """Stream container logs to terminal.

    Args:
        container: Docker container object.
        log_stream_active: Threading event to control log streaming.
        output_console: Rich console for output.

    """
    try:
        # Get log generator
        log_generator = container.logs(stream=True, follow=True)

        for log_chunk in log_generator:
            if not log_stream_active.is_set():
                break
            try:
                # Decode and split by newlines, handling both \n and \r\n
                log_text = log_chunk.decode("utf-8")
                # Print without adding extra newlines (end="")
                if log_text:
                    # Use file write directly to avoid Rich adding newlines
                    output_console.file.write(log_text)
                    output_console.file.flush()
            except UnicodeDecodeError:
                pass
    except Exception:
        pass


def wait_for_service_ready(
    port: int, timeout: int = 600, check_interval: int = 2
) -> bool:
    """Wait for NIM service to be ready to accept requests.

    Uses the official NVIDIA NIM health check endpoint /v1/health/ready.

    Args:
        port: The port the service is running on.
        timeout: Maximum time to wait in seconds. Defaults to 600 (10 minutes).
        check_interval: Time between health checks in seconds. Defaults to 2.

    Returns:
        True if service is ready, False if timeout reached.

    """
    start_time = time.time()
    url = f"http://localhost:{port}/v1/health/ready"

    while time.time() - start_time < timeout:
        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=5.0)
                if response.status_code == 200:
                    return True
        except (
            httpx.ConnectError,
            httpx.TimeoutException,
            httpx.HTTPError,
        ):
            pass

        time.sleep(check_interval)

    return False


def get_available_models(port: int) -> list[str] | None:
    """Get list of available models from NIM service.

    Uses the official NVIDIA NIM models endpoint /v1/models.

    Args:
        port: The port the service is running on.

    Returns:
        List of model IDs if successful, None if failed.

    """
    url = f"http://localhost:{port}/v1/models"

    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Extract model IDs from the response
                if "data" in data and isinstance(data["data"], list):
                    return [model.get("id") for model in data["data"] if "id" in model]
    except (
        httpx.ConnectError,
        httpx.TimeoutException,
        httpx.HTTPError,
    ):
        pass

    return None


class ConsoleUI:
    """Console UI for deployment with optional quiet mode.

    This implementation uses the Rich library to provide colored output
    and progress bars in the terminal. When quiet mode is enabled, all
    output is suppressed.

    Attributes:
        quiet: If True, suppresses all console output.
        console: The Rich console instance (None in quiet mode).

    """

    def __init__(self, quiet: bool = False):
        """Initialize console UI.

        Args:
            quiet: If True, suppresses all console output. Defaults to False.

        """
        self.quiet = quiet
        self.console = None if quiet else Console()

    def show_info(self, message: str) -> None:
        """Display an informational message in cyan.

        Args:
            message: The message to display.

        """
        if not self.quiet:
            self.console.print(f"[cyan]{message}[/cyan]")

    def show_success(self, message: str) -> None:
        """Display a success message in green with checkmark.

        Args:
            message: The success message to display.

        """
        if not self.quiet:
            self.console.print(f"[green]✓ {message}[/green]")

    def show_error(self, message: str) -> None:
        """Display an error message in red with cross mark.

        Args:
            message: The error message to display.

        """
        if not self.quiet:
            self.console.print(f"[red]✗ {message}[/red]")

    def show_warning(self, message: str) -> None:
        """Display a warning message in yellow with warning symbol.

        Args:
            message: The warning message to display.

        """
        if not self.quiet:
            self.console.print(f"[yellow]⚠ {message}[/yellow]")

    @contextmanager
    def progress_context(self):
        """Create a progress context for tracking operations.

        In quiet mode, yields a no-op progress object.
        Otherwise, yields a Rich progress instance.

        Yields:
            Progress or _NoOpProgress: A progress tracker object.

        """
        if self.quiet:
            yield _NoOpProgress()
        else:
            with ViProgress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
            ) as progress:
                yield progress


class _NoOpProgress:
    """Minimal progress object for quiet mode."""

    def add_task(self, _description: str, **_kwargs: Any) -> int:
        """Add a task (no-op).

        Args:
            _description: Task description (ignored).
            **_kwargs: Additional arguments (ignored).

        Returns:
            A dummy task ID.

        """
        return 0

    def update(self, _task_id: int, **_kwargs: Any) -> None:
        """Update task (no-op).

        Args:
            _task_id: Task ID (ignored).
            **_kwargs: Additional arguments (ignored).

        """

    def advance(self, _task_id: int, _advance: float = 1.0) -> None:
        """Advance task (no-op).

        Args:
            _task_id: Task ID (ignored).
            _advance: Amount to advance (ignored).

        """
