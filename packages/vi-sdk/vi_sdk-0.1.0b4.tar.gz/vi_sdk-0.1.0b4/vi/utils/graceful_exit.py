#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   graceful_exit.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK graceful exit utilities.
"""

import signal
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


class GracefulExit:
    """Handle graceful exit on keyboard interrupt."""

    def __init__(self, message: str = "Operation cancelled by user"):
        """Initialize the graceful exit handler.

        Args:
            message: Message to display when interrupted.

        """
        self.message = message
        self.exit_now = False
        self.original_sigint = None

    def signal_handler(self, _signum: int, _frame: Any) -> None:
        """Handle SIGINT signal gracefully.

        Args:
            _signum: Signal number.
            _frame: Current stack frame.

        """
        self.exit_now = True
        # Restore original handler and re-raise to let KeyboardInterrupt propagate naturally
        if self.original_sigint:
            signal.signal(signal.SIGINT, self.original_sigint)
        raise KeyboardInterrupt()

    def __enter__(self):
        """Enter the context manager.

        Returns:
            Self for use in with statements.

        """
        self.original_sigint = signal.signal(signal.SIGINT, self.signal_handler)
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Exit the context manager.

        Args:
            _exc_type: Exception type.
            _exc_val: Exception value.
            _exc_tb: Exception traceback.

        """
        # Restore original handler if not already restored by signal_handler
        if (
            self.original_sigint
            and signal.getsignal(signal.SIGINT) == self.signal_handler
        ):
            signal.signal(signal.SIGINT, self.original_sigint)


@contextmanager
def graceful_exit(
    message: str = "Operation cancelled by user",
) -> Generator[GracefulExit, None, None]:
    """Context manager for graceful keyboard interrupt handling.

    Args:
        message: Message to display when interrupted

    Example:
        with graceful_exit("Download cancelled by user") as handler:
            for i in range(100):
                if handler.exit_now:
                    break
                # Do work...
                time.sleep(0.1)

    """
    handler = GracefulExit(message)
    with handler:
        yield handler
