#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   progress.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Custom progress bar with integrated console redirection.
"""

import sys
from typing import Any

from rich.console import Console
from rich.progress import Progress
from vi.utils.console_utils import redirect_console

try:
    from IPython import get_ipython
except ImportError:
    get_ipython = None


def _is_jupyter_environment() -> bool:
    """Check if running in a Jupyter environment.

    Returns:
        True if in Jupyter, False otherwise.

    """
    try:
        ipython = get_ipython()
        if ipython is None:
            return False

        # Check if it's a ZMQInteractiveShell (Jupyter) or TerminalInteractiveShell (IPython)
        shell_class = ipython.__class__.__name__
        return shell_class == "ZMQInteractiveShell"

    except (ImportError, NameError):
        return False


class ViProgress(Progress):
    """Enhanced progress bar that automatically redirects console output to Rich formatting.

    This class combines Rich's Progress functionality with automatic console redirection,
    ensuring that all stdout, stderr, and logging output during progress operations
    is captured and displayed using Rich formatting.

    When used as a context manager, captured output from external libraries is displayed
    in real-time on new lines without disrupting the progress spinner.

    Console redirection uses a non-blocking background thread to process output,
    minimizing performance impact on the main thread operations.
    """

    def __init__(
        self,
        *args: Any,
        redirect_console_output: bool = False,
        **kwargs: Any,
    ):
        """Initialize ViProgress with optional console redirection.

        Args:
            *args: Arguments passed to Rich Progress
            redirect_console_output: Whether to enable console redirection (default: False).
                When True, stdout/stderr/logging output is captured and displayed
                asynchronously in a background thread without blocking the main thread.
                This is useful during model loading but typically not needed during inference.
            **kwargs: Keyword arguments passed to Rich Progress

        Note:
            Console redirection is disabled by default for performance. Enable it
            only when you need to capture output from external libraries (e.g.,
            during model loading with transformers).

        """
        if "console" not in kwargs:
            # Only force Jupyter output when actually in a Jupyter environment
            is_jupyter = _is_jupyter_environment()
            kwargs["console"] = Console(
                file=sys.stderr, force_terminal=not is_jupyter, force_jupyter=is_jupyter
            )

        self._redirect_console = redirect_console_output
        self._console_context = None
        super().__init__(*args, **kwargs)

    def __enter__(self):
        """Enter context manager and set up console redirection."""
        # Start the progress display
        progress_instance = super().__enter__()

        # Set up console redirection with non-blocking async output to our console
        if self._redirect_console:
            self._console_context = redirect_console(rich_console=self.console)
            self._console_context.__enter__()

        return progress_instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and clean up console redirection."""
        # Clean up console redirection first (will flush remaining output)
        if self._redirect_console and self._console_context is not None:
            self._console_context.__exit__(exc_type, exc_val, exc_tb)

        # Then stop the progress display
        return super().__exit__(exc_type, exc_val, exc_tb)
