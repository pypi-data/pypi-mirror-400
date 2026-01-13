#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   results.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Base classes for operation results (upload/download) with common functionality.
"""

from abc import ABC, abstractmethod


class OperationResult(ABC):
    """Base class for all operation results.

    Provides common interface for upload and download operations,
    including summary generation and string representations.

    """

    @abstractmethod
    def summary(self) -> str:
        """Return formatted summary of operation results.

        Returns:
            Multi-line string with operation statistics and status

        """

    def info(self) -> None:
        """Display detailed information about the operation result.

        Prints a rich formatted output with all relevant details.

        """
        print(self.summary())

    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.summary()


class UploadResult(OperationResult):
    """Base class for upload operation results.

    Adds timing functionality common to all upload operations.

    Attributes:
        start_time: Timestamp when upload started (in milliseconds)
        end_time: Timestamp when upload ended (in milliseconds)

    """

    start_time: int | None = None
    end_time: int | None = None

    @property
    def duration_seconds(self) -> float:
        """Total duration of operation in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) / 1000  # Convert ms to seconds
        return 0.0


class DownloadResult(OperationResult):
    """Base class for download operation results.

    Provides common interface for download operations with path management.

    """
