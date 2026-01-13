#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   base_error.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK base error module.
"""

import json
import re
from enum import Enum
from typing import Any

import msgspec


class ViErrorCode(Enum):
    """Structured error codes following industry standards.

    Uses descriptive string identifiers like AWS, Google Cloud, and OpenAI APIs.
    Each error maintains an associated HTTP status code for compatibility.
    """

    # Authentication & Authorization (4xx)
    AUTHENTICATION_FAILED = "AuthenticationFailed"
    INVALID_API_KEY = "InvalidApiKey"
    EXPIRED_CREDENTIALS = "ExpiredCredentials"
    PERMISSION_DENIED = "PermissionDenied"

    # Validation & Input (4xx)
    VALIDATION_FAILED = "ValidationFailed"
    INVALID_PARAMETER = "InvalidParameter"
    MISSING_REQUIRED_FIELD = "MissingRequiredField"
    INVALID_FILE_FORMAT = "InvalidFileFormat"
    FILE_TOO_LARGE = "FileTooLarge"

    # Resources (4xx)
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    RESOURCE_CONFLICT = "ResourceConflict"
    RESOURCE_LIMIT_EXCEEDED = "ResourceLimitExceeded"

    # Network & Connectivity (5xx)
    NETWORK_ERROR = "NetworkError"
    TIMEOUT_ERROR = "TimeoutError"
    CONNECTION_FAILED = "ConnectionFailed"

    # Server & Service (5xx)
    SERVER_ERROR = "ServerError"
    SERVICE_UNAVAILABLE = "ServiceUnavailable"
    RATE_LIMIT_EXCEEDED = "RateLimitExceeded"

    # Operations (5xx)
    OPERATION_FAILED = "OperationFailed"
    DOWNLOAD_FAILED = "DownloadFailed"
    UPLOAD_FAILED = "UploadFailed"
    CONFIGURATION_ERROR = "ConfigurationError"

    # Unknown
    UNKNOWN_ERROR = "UnknownError"

    @property
    def http_status(self) -> int:
        """Get the associated HTTP status code for this error."""
        # Map error codes to their appropriate HTTP status codes
        status_map = {
            # 4xx Client Errors
            "AuthenticationFailed": 401,
            "InvalidApiKey": 401,
            "ExpiredCredentials": 401,
            "PermissionDenied": 403,
            "ValidationFailed": 400,
            "InvalidParameter": 400,
            "MissingRequiredField": 400,
            "InvalidFileFormat": 400,
            "FileTooLarge": 413,
            "ResourceNotFound": 404,
            "ResourceConflict": 409,
            "RateLimitExceeded": 429,
            "ResourceLimitExceeded": 429,
            # 5xx Server Errors
            "NetworkError": 502,
            "ConnectionFailed": 502,
            "ServiceUnavailable": 503,
            "TimeoutError": 504,
            "ServerError": 500,
            "OperationFailed": 500,
            "DownloadFailed": 500,
            "UploadFailed": 500,
            "ConfigurationError": 500,
            "UnknownError": 500,
        }
        return status_map.get(self.value, 500)

    @classmethod
    def from_http_status(cls, status_code: int) -> "ViErrorCode":
        """Get the most appropriate error code for an HTTP status code."""
        status_map = {
            400: cls.VALIDATION_FAILED,
            401: cls.AUTHENTICATION_FAILED,
            403: cls.PERMISSION_DENIED,
            404: cls.RESOURCE_NOT_FOUND,
            409: cls.RESOURCE_CONFLICT,
            413: cls.FILE_TOO_LARGE,
            429: cls.RATE_LIMIT_EXCEEDED,
            500: cls.SERVER_ERROR,
            502: cls.NETWORK_ERROR,
            503: cls.SERVICE_UNAVAILABLE,
            504: cls.TIMEOUT_ERROR,
        }
        return status_map.get(status_code, cls.UNKNOWN_ERROR)


class ViError(Exception):
    """Base Error Class with enhanced error handling capabilities."""

    def __init__(
        self,
        message: str | Exception,
        *,
        error_code: ViErrorCode | None = None,
        status_code: int | None = None,
        suggestion: str | None = None,
        cause: Exception | None = None,
        details: dict[str, Any] | None = None,
        retry_after: str | None = None,
        trace_id: str | None = None,
        organization_id: str | None = None,
    ):
        # Handle case where an exception is passed as message
        if isinstance(message, Exception):
            cause = message
            message = str(message)
            # Auto-detect error code and suggestion based on exception type
            if error_code is None or suggestion is None:
                auto_code, auto_suggestion = self._map_exception_to_error(cause)
                error_code = error_code or auto_code
                suggestion = suggestion or auto_suggestion

        # Sanitize the message to clean up resource IDs
        if isinstance(message, str):
            message = self._sanitize_resource_id(message)

        super().__init__(message)
        self.message = message
        self.error_code = error_code or ViErrorCode.UNKNOWN_ERROR
        self.status_code = status_code
        self.suggestion = suggestion
        self.cause = cause
        self.details = details or {}
        self.retry_after = retry_after  # Store Retry-After header value for retries
        self.trace_id = (
            trace_id  # Store trace ID for request tracking (GCP: x-cloud-trace-context)
        )
        self.organization_id = organization_id

    @staticmethod
    def _map_exception_to_error(exc: Exception) -> tuple[ViErrorCode, str]:
        """Map common exception types to appropriate Vi error codes and suggestions.

        Args:
            exc: The exception to map

        Returns:
            A tuple containing the error code and suggestion

        """
        if isinstance(exc, (ConnectionError, TimeoutError)):
            return (
                ViErrorCode.NETWORK_ERROR,
                "Check your internet connection and try again. "
                "If you're behind a corporate firewall, you may need to configure proxy settings.",
            )

        if isinstance(exc, ValueError):
            return (
                ViErrorCode.VALIDATION_FAILED,
                "Check the input parameters and ensure they "
                "meet the required format and constraints.",
            )

        if isinstance(exc, FileNotFoundError):
            return (
                ViErrorCode.RESOURCE_NOT_FOUND,
                "Verify the file path exists and you have permission to access it.",
            )

        if isinstance(exc, PermissionError):
            return (
                ViErrorCode.PERMISSION_DENIED,
                "Check file permissions and ensure you have the necessary access rights.",
            )
        if isinstance(exc, OSError):
            return (
                ViErrorCode.OPERATION_FAILED,
                "Check system resources and file permissions. "
                "Ensure sufficient disk space is available.",
            )
        if isinstance(exc, (json.JSONDecodeError, msgspec.DecodeError)):
            return (
                ViErrorCode.VALIDATION_FAILED,
                "The data format is invalid. Check that the input is valid JSON "
                "or the expected format.",
            )

        return (
            ViErrorCode.UNKNOWN_ERROR,
            "An unexpected error occurred. Please try again or contact support "
            "if the issue persists.",
        )

    def __str__(self) -> str:
        """User-friendly error message."""
        parts = [f"[{self.error_code.value}] {self.message}"]

        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")

        if self.suggestion:
            parts.append(f"\n\n💡 Suggestion: {self.suggestion}")

        return " ".join(parts)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        parts = [
            f"{self.__class__.__name__}(",
            f"message={self.message!r}, ",
            f"error_code={self.error_code}, ",
            f"status_code={self.status_code}",
        ]
        if self.trace_id:
            parts.append(f", trace_id={self.trace_id!r}")
        parts.append(")")
        return "".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        result = {
            "error_code": self.error_code.value,
            "http_status": self.error_code.http_status,
            "message": self.message,
            "status_code": self.status_code,
            "suggestion": self.suggestion,
            "type": self.__class__.__name__,
        }
        if self.details:
            result["details"] = self.details
        if self.trace_id:
            result["trace_id"] = self.trace_id
        return result

    @property
    def http_status(self) -> int:
        """Get the HTTP status code from the error code."""
        return self.error_code.http_status

    def is_client_error(self) -> bool:
        """Check if this is a client error (4xx)."""
        return 400 <= self.http_status < 500

    def is_server_error(self) -> bool:
        """Check if this is a server error (5xx)."""
        return 500 <= self.http_status < 600

    def is_retryable(self) -> bool:
        """Check if this error type is generally retryable."""
        # Network errors, timeouts, and server errors are typically retryable
        # Client errors (auth, validation) are typically not retryable
        retryable_codes = {
            ViErrorCode.NETWORK_ERROR,
            ViErrorCode.TIMEOUT_ERROR,
            ViErrorCode.CONNECTION_FAILED,
            ViErrorCode.SERVER_ERROR,
            ViErrorCode.SERVICE_UNAVAILABLE,
            ViErrorCode.RATE_LIMIT_EXCEEDED,
        }
        return self.error_code in retryable_codes

    def _sanitize_resource_id(self, message: str) -> str:
        """Sanitize resource IDs in error messages.

        Replaces patterns like 'dataset {organization_id}_{dataset_id}'
        with 'dataset {dataset_id}'.

        Args:
            message: The error message to sanitize

        Returns:
            The sanitized error message

        """
        # Pattern 1: Match resource type followed by composite ID
        # e.g., "Datasets org-123_ds1" -> "dataset ds1"
        # Normalize to lowercase singular form
        # Only match if the org ID looks like a UUID or org-prefix pattern
        pattern1 = (
            r"(\w+?)s?\s+([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-"
            r"[a-f0-9]{12}|[a-z]+-[0-9]+)_([a-zA-Z0-9_-]+)"
        )

        message = re.sub(
            pattern1,
            lambda match: f"{match.group(1).lower()} {match.group(3)}",
            message,
        )

        # Pattern 2: Match standalone composite IDs (no resource type prefix)
        # e.g., "org-123_ds2" -> "ds2"
        # Only match if the prefix looks like a UUID or org-prefix pattern
        pattern2 = (
            r"\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-"
            r"[a-f0-9]{12}|[a-z]+-[0-9]+)_([a-zA-Z0-9_-]+)\b"
        )
        message = re.sub(pattern2, r"\2", message)

        return message
