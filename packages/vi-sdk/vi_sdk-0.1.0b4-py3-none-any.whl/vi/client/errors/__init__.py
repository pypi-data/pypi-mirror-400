#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   __init__.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK errors init module.
"""

from .base_error import ViError, ViErrorCode
from .errors import (
    ViAuthenticationError,
    ViConfigurationError,
    ViConflictError,
    ViDownloadError,
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
    create_error_from_response,
)

__all__ = [
    "ViError",
    "ViErrorCode",
    "ViAuthenticationError",
    "ViNotFoundError",
    "ViRateLimitError",
    "ViServerError",
    "ViNetworkError",
    "ViConflictError",
    "ViValidationError",
    "ViDownloadError",
    "ViConfigurationError",
    "ViPermissionError",
    "ViOperationError",
    "ViUploadError",
    "ViTimeoutError",
    "ViInvalidParameterError",
    "ViFileTooLargeError",
    "ViInvalidFileFormatError",
    "create_error_from_response",
]
