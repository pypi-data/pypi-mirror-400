#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   errors.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK errors module.
"""

import json

from httpx import Response
from vi.client.errors.base_error import ViError, ViErrorCode


class ViAuthenticationError(ViError):
    """Raised when authentication fails.

    Usually indicates invalid API key or expired credentials.
    """

    def __init__(self, message: str = "Authentication failed", **kwargs):
        organization_id = kwargs.get("organization_id", "YOUR_ORGANIZATION_ID")
        kwargs.setdefault("error_code", ViErrorCode.AUTHENTICATION_FAILED)
        kwargs.setdefault(
            "suggestion",
            (
                "Check your API key is correct and hasn't expired. "
                "You can generate a new API key in Datature Vi at "
                f"https://vi.datature.com/org/{organization_id}/settings/secret-keys"
            ),
        )
        super().__init__(message, **kwargs)


class ViNotFoundError(ViError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.RESOURCE_NOT_FOUND)
        kwargs.setdefault(
            "suggestion",
            (
                "Verify the resource ID is correct and you have access to it. "
                "Use the `list` method to see available resources."
            ),
        )
        super().__init__(message, **kwargs)


class ViRateLimitError(ViError):
    """Raised when API rate limits are exceeded.

    Includes information about when to retry.
    """

    def __init__(self, message: str = "API rate limit exceeded", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.RATE_LIMIT_EXCEEDED)
        kwargs.setdefault(
            "suggestion",
            (
                "You're making requests too quickly. "
                "Wait a few seconds before retrying, or implement exponential backoff. "
                "Check the 'Retry-After' header for recommended wait time."
            ),
        )
        super().__init__(message, **kwargs)


class ViServerError(ViError):
    """Raised when the Vi server encounters an error.

    Usually indicates a temporary issue on Vi's side.
    """

    def __init__(self, message: str = "Server error", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.SERVER_ERROR)
        kwargs.setdefault(
            "suggestion",
            (
                "This is likely a temporary issue on Vi's servers. "
                "Please try again in a few moments. If the problem persists, "
                "contact us at developers@datature.io with the error code and timestamp."
            ),
        )
        super().__init__(message, **kwargs)


class ViNetworkError(ViError):
    """Raised when network connectivity issues occur.

    Could be timeout, connection refused, DNS issues, etc.
    """

    def __init__(self, message: str = "Network error", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.NETWORK_ERROR)
        kwargs.setdefault(
            "suggestion",
            (
                "Check your internet connection and try again. If you're behind a "
                "corporate firewall, you may need to configure proxy settings. For timeout "
                "issues, consider increasing the timeout value in your client configuration."
            ),
        )
        super().__init__(message, **kwargs)


class ViConflictError(ViError):
    """Raised when a conflict occurs."""

    def __init__(self, message: str = "Resource conflict", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.RESOURCE_CONFLICT)
        kwargs.setdefault(
            "suggestion",
            (
                "The resource you're trying to create already exists or conflicts with "
                "existing data. Check for duplicate names or IDs. If the problem persists, "
                "contact us at developers@datature.io"
            ),
        )
        super().__init__(message, **kwargs)


class ViValidationError(ViError):
    """Raised when request parameters are invalid.

    Includes details about what validation failed.
    """

    def __init__(self, message: str = "Validation failed", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.VALIDATION_FAILED)
        kwargs.setdefault(
            "suggestion",
            (
                "Check the API documentation at https://vi.developers.datature.com/docs/vi-sdk "
                "for the correct parameter format and values. "
                "Review the 'details' field for specific validation errors."
            ),
        )
        super().__init__(message, **kwargs)


class ViDownloadError(ViError):
    """Raised when download fails.

    Could be network issues, insufficient disk space, corrupt files, etc.
    """

    def __init__(self, message: str = "Download failed", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.DOWNLOAD_FAILED)
        kwargs.setdefault(
            "suggestion",
            (
                "Check you have sufficient disk space and the download URL is accessible. "
                "Verify file permissions in the target directory. "
                "Try downloading to a different location. "
                "If the problem persists, contact us at developers@datature.io"
            ),
        )
        super().__init__(message, **kwargs)


class ViConfigurationError(ViError):
    """Raised when SDK configuration is invalid.

    Usually during client initialization.
    """

    def __init__(self, message: str = "Invalid configuration", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.CONFIGURATION_ERROR)
        kwargs.setdefault(
            "suggestion",
            (
                "Check your configuration file format and required fields. "
                "Ensure API endpoints and credentials are correctly set. "
                "Refer to the setup documentation at "
                "https://vi.developers.datature.com/docs/vi-sdk-getting-started"
            ),
        )
        super().__init__(message, **kwargs)


class ViPermissionError(ViError):
    """Raised when user lacks permissions for an operation."""

    def __init__(self, message: str = "Permission denied", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.PERMISSION_DENIED)
        kwargs.setdefault(
            "suggestion",
            (
                "You don't have permission to perform this operation. "
                "Contact your Vi workspace owner to request access. "
                "Check your role and permissions in your Vi workspace."
            ),
        )
        super().__init__(message, **kwargs)


class ViOperationError(ViError):
    """Raised when an operation fails."""

    def __init__(self, message: str = "Operation failed", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.OPERATION_FAILED)
        kwargs.setdefault(
            "suggestion",
            (
                "The requested operation could not be completed. "
                "Please try again. If the problem persists, contact us at developers@datature.io "
                "with the error code and operation details."
            ),
        )
        super().__init__(message, **kwargs)


class ViUploadError(ViError):
    """Raised when file upload fails."""

    def __init__(self, message: str = "Upload failed", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.UPLOAD_FAILED)
        kwargs.setdefault(
            "suggestion",
            (
                "Check your internet connection and file permissions. "
                "Ensure the file format is supported and not corrupted. "
                "Verify you have sufficient storage quota."
            ),
        )
        super().__init__(message, **kwargs)


class ViTimeoutError(ViError):
    """Raised when operations timeout."""

    def __init__(self, message: str = "Operation timed out", **kwargs):
        kwargs.setdefault("error_code", ViErrorCode.TIMEOUT_ERROR)
        kwargs.setdefault(
            "suggestion",
            (
                "The operation took longer than expected. "
                "Try increasing the timeout value or check your network connection. "
                "For large operations, consider breaking them into smaller chunks."
            ),
        )
        super().__init__(message, **kwargs)


class ViInvalidParameterError(ViValidationError):
    """Raised when a specific parameter is invalid."""

    def __init__(self, parameter_name: str, message: str | None = None, **kwargs):
        if message is None:
            message = f"Invalid parameter: {parameter_name}"
        kwargs.setdefault("error_code", ViErrorCode.INVALID_PARAMETER)
        kwargs.setdefault(
            "suggestion",
            (
                f"Check the value and format of parameter '{parameter_name}'. "
                "Refer to the API documentation for valid values and formats."
            ),
        )
        super().__init__(message, **kwargs)


class ViFileTooLargeError(ViValidationError):
    """Raised when uploaded file exceeds size limits."""

    def __init__(self, file_size: int, max_size: int, **kwargs):
        message = f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes"
        kwargs.setdefault("error_code", ViErrorCode.FILE_TOO_LARGE)
        kwargs.setdefault("details", {"file_size": file_size, "max_size": max_size})
        kwargs.setdefault(
            "suggestion",
            (
                "Reduce the file size or compress the file before uploading. "
                "Consider splitting large files into smaller chunks."
            ),
        )
        super().__init__(message, **kwargs)


class ViInvalidFileFormatError(ViValidationError):
    """Raised when file format is not supported."""

    def __init__(
        self, file_format: str, supported_formats: list[str] | None = None, **kwargs
    ):
        message = f"Unsupported file format: {file_format}"
        if supported_formats:
            message += f". Supported formats: {', '.join(supported_formats)}"
        kwargs.setdefault("error_code", ViErrorCode.INVALID_FILE_FORMAT)
        kwargs.setdefault(
            "details",
            {"file_format": file_format, "supported_formats": supported_formats or []},
        )
        kwargs.setdefault(
            "suggestion",
            (
                "Convert your file to a supported format before uploading. "
                "Check the documentation for the complete list of supported formats."
            ),
        )
        super().__init__(message, **kwargs)


# Error mapping for HTTP status codes
ERROR_CODE_MAP = {
    400: ViValidationError,
    401: ViAuthenticationError,
    403: ViAuthenticationError,
    404: ViNotFoundError,
    409: ViConflictError,
    429: ViRateLimitError,
    500: ViServerError,
    502: ViServerError,
    503: ViServerError,
    504: ViServerError,
}


def create_error_from_response(
    response: Response,
    status_code: int | None = None,
    message: str | None = None,
) -> ViError:
    """Create appropriate error from HTTP response.

    Args:
        response: HTTP response object (for status, message, headers)
        status_code: Optional HTTP status code (extracted from response if not provided)
        message: Optional error message (extracted from response if not provided)

    Returns:
        Appropriate ViError subclass with HTTP-based error code

    Note:
        If status_code or message are not provided, they will be extracted from
        the response object. The following headers are extracted and stored:
        - Retry-After: Used for retry timing
        - x-cloud-trace-context: GCP trace ID for request tracking

    """
    # Extract organization_id from "/workspaces/organization_id/xxx" URL format
    try:
        parts = str(response.url).split("/workspaces/")
        if len(parts) > 1:
            organization_id = parts[1].split("/")[0]
        else:
            organization_id = "YOUR_ORGANIZATION_ID"
    except Exception:
        organization_id = "YOUR_ORGANIZATION_ID"

    # Extract status code from response if not provided
    if status_code is None:
        status_code = response.status_code

    # Extract message from response if not provided
    if message is None:
        try:
            error_data = response.json()
            message = error_data.get(
                "message", error_data.get("error", f"HTTP {status_code} error")
            )
        except (json.JSONDecodeError, AttributeError):
            message = f"HTTP {status_code}:\n{getattr(response, 'text', str(response))}"

    # Extract Retry-After header if present (only need the value, not whole response)
    retry_after = None
    trace_id = None
    if hasattr(response, "headers"):
        retry_after = response.headers.get("Retry-After")
        # Extract trace ID from GCP's x-cloud-trace-context header
        # Format: TRACE_ID or TRACE_ID/SPAN_ID;o=TRACE_TRUE
        trace_context = response.headers.get("x-cloud-trace-context")
        if trace_context:
            # Extract just the trace ID part (before any slash)
            trace_id = trace_context.split("/")[0]

    error_class = ERROR_CODE_MAP.get(status_code, ViError)
    # Use the HTTP-based error code system
    error_code = ViErrorCode.from_http_status(status_code)
    return error_class(
        message=message,
        status_code=status_code,
        error_code=error_code,
        retry_after=retry_after,
        trace_id=trace_id,
        organization_id=organization_id,
    )
