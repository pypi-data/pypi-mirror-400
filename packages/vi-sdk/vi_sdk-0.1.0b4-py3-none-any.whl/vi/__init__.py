#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   __init__.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK init module.
"""

from vi.api.client import ViClient as Client
from vi.client.errors import (
    ViAuthenticationError,
    ViConfigurationError,
    ViConflictError,
    ViDownloadError,
    ViError,
    ViErrorCode,
    ViFileTooLargeError,
    ViInvalidFileFormatError,
    ViInvalidParameterError,
    ViNetworkError,
    ViNotFoundError,
    ViOperationError,
    ViPermissionError,
    ViRateLimitError,
    ViServerError,
    ViTimeoutError,
    ViUploadError,
    ViValidationError,
)
from vi.logging import LoggingConfig, configure_logging, get_logger

__all__ = [
    "Client",
    "ViError",
    "ViErrorCode",
    "ViAuthenticationError",
    "ViNotFoundError",
    "ViRateLimitError",
    "ViServerError",
    "ViNetworkError",
    "ViValidationError",
    "ViDownloadError",
    "ViConflictError",
    "ViTimeoutError",
    "ViConfigurationError",
    "ViPermissionError",
    "ViOperationError",
    "ViUploadError",
    "ViInvalidParameterError",
    "ViFileTooLargeError",
    "ViInvalidFileFormatError",
    "LoggingConfig",
    "configure_logging",
    "get_logger",
]
