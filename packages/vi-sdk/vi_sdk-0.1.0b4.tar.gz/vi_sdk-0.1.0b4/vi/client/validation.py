#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   validation.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK validation utilities.
"""

import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from vi.client.errors import (
    ViFileTooLargeError,
    ViInvalidFileFormatError,
    ViInvalidParameterError,
)

# Secret key validation constants
DEFAULT_SECRET_KEY_LENGTH = 103
DEFAULT_SECRET_KEY_PREFIX = "dtvi_"  # nosec B105


def validate_required_param(value: Any, param_name: str) -> None:
    """Validate that a required parameter is not None or empty.

    Args:
        value: The value to validate.
        param_name: Name of the parameter for error messages.

    Raises:
        ViInvalidParameterError: If value is None or empty string.

    """
    if value is None:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' is required but was None",
        )

    if isinstance(value, str) and not value.strip():
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' cannot be empty",
        )


def validate_string_param(
    value: str | None,
    param_name: str,
    min_length: int = 0,
    max_length: int | None = None,
    pattern: str | None = None,
    required: bool = True,
) -> None:
    """Validate string parameter with length and pattern constraints.

    Args:
        value: The string value to validate.
        param_name: Name of the parameter for error messages.
        min_length: Minimum allowed length.
        max_length: Maximum allowed length.
        pattern: Regex pattern the string must match.
        required: Whether the parameter is required.

    Raises:
        ViInvalidParameterError: If validation fails.

    """
    if required:
        validate_required_param(value, param_name)

    if value is None and not required:
        return

    if not isinstance(value, str):
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be a string, got {type(value).__name__}",
        )

    if len(value) < min_length:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be at least {min_length} characters long",
        )

    if max_length is not None and len(value) > max_length:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be at most {max_length} characters long",
        )

    if pattern is not None and not re.match(pattern, value):
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' does not match the required pattern: {pattern}",
        )


def validate_id_param(value: str | None, param_name: str) -> None:
    """Validate ID parameters (dataset_id, asset_id, etc.).

    Args:
        value: The ID value to validate.
        param_name: Name of the parameter for error messages.

    Raises:
        ViInvalidParameterError: If ID format is invalid.

    """
    try:
        validate_string_param(
            value, param_name, min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9_-]+$"
        )
    except ViInvalidParameterError as e:
        # Add more context-specific suggestion for IDs
        if value and not isinstance(value, str):
            raise ViInvalidParameterError(
                param_name,
                f"Parameter '{param_name}' must be a string, got {type(value).__name__}",
                suggestion=(
                    f"Make sure '{param_name}' is a string. "
                    f"Example: client.datasets.get('{param_name}='dataset_abc123')"
                ),
            ) from e

        if value and not value.strip():
            raise ViInvalidParameterError(
                param_name,
                f"Parameter '{param_name}' cannot be empty",
                suggestion=(
                    f"Provide a valid ID for '{param_name}'. "
                    "You can list available resources using the .list() method. "
                    "Example: client.datasets.list() to see available dataset IDs"
                ),
            ) from e

        if value is None:
            raise ViInvalidParameterError(
                param_name,
                f"Parameter '{param_name}' is required but was not provided",
                suggestion=(
                    f"Provide the '{param_name}' parameter. "
                    "You can find valid IDs by listing resources. "
                    "Example: datasets = client.datasets.list(); "
                    "print(datasets.items[0].dataset_id)"
                ),
            ) from e

        # Check if it's a length error by looking at the original error message
        if "at least" in str(e) or "at most" in str(e):
            # Re-raise with additional context while preserving the original message
            raise ViInvalidParameterError(
                param_name,
                e.message,  # Preserve the original message
                suggestion=(
                    f"IDs must be between 1 and 255 characters long. "
                    f"Make sure you're using a valid ID from the platform. "
                    f"Example: client.datasets.get('{param_name}='dataset_abc123')"
                ),
            ) from e

        # Invalid characters in the ID
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' contains invalid characters: '{value}'",
            suggestion=(
                "IDs can only contain letters, numbers, underscores, and hyphens. "
                "Make sure you're using the ID from the platform, not a display name. "
                f"Example valid ID: '{param_name}=dataset_abc123'"
            ),
        ) from e


def validate_file_path(
    path: Path | str,
    param_name: str = "path",
    must_exist: bool = True,
    must_be_file: bool = True,
    allowed_extensions: Sequence[str] | None = None,
    max_size_bytes: int | None = None,
) -> Path:
    """Validate file path with comprehensive checks.

    Args:
        path: The file path to validate.
        param_name: Name of the parameter for error messages.
        must_exist: Whether the file must exist.
        must_be_file: Whether the path must be a file (not directory).
        allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png']).
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        The validated Path object.

    Raises:
        ViInvalidParameterError: If path validation fails.
        ViInvalidFileFormatError: If file extension is not allowed.
        ViFileTooLargeError: If file exceeds max size.

    """
    if isinstance(path, str):
        path = Path(path).expanduser().resolve()
    elif isinstance(path, Path):
        path = path.expanduser().resolve()
    else:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be a Path or string, got {type(path).__name__}",
        )

    if must_exist and not path.exists():
        raise ViInvalidParameterError(
            param_name,
            f"File does not exist: {path}",
            suggestion=(
                "Check that the file path is correct and the file exists. "
                f"Current path: {path}. "
                "Use an absolute path or ensure your working directory is correct."
            ),
        )

    if must_be_file and path.exists() and not path.is_file():
        raise ViInvalidParameterError(
            param_name,
            f"Path must be a file, not a directory: {path}",
            suggestion=(
                "You provided a directory path, but a file path is required. "
                "If you want to upload multiple files, use the appropriate batch upload method."
            ),
        )

    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise ViInvalidFileFormatError(
            path.suffix.lower() or "no extension",
            list(allowed_extensions),
        )

    if max_size_bytes and path.exists():
        file_size = path.stat().st_size
        if file_size > max_size_bytes:
            raise ViFileTooLargeError(file_size, max_size_bytes)

    return path


def validate_directory_path(
    path: Path | str,
    param_name: str = "path",
    must_exist: bool = True,
    create_if_missing: bool = False,
) -> Path:
    """Validate directory path.

    Args:
        path: The directory path to validate.
        param_name: Name of the parameter for error messages.
        must_exist: Whether the directory must exist.
        create_if_missing: Whether to create the directory if it doesn't exist.

    Returns:
        The validated Path object.

    Raises:
        ViInvalidParameterError: If directory validation fails.

    """
    if isinstance(path, str):
        path = Path(path).expanduser().resolve()
    elif isinstance(path, Path):
        path = path.expanduser().resolve()
    else:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be a Path or string, got {type(path).__name__}",
        )

    if must_exist and not path.exists():
        if create_if_missing:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ViInvalidParameterError(
                    param_name,
                    f"Cannot create directory {path}: {e}",
                ) from e
        else:
            raise ViInvalidParameterError(
                param_name,
                f"Directory does not exist: {path}",
            )

    if path.exists() and not path.is_dir():
        raise ViInvalidParameterError(
            param_name,
            f"Path must be a directory, not a file: {path}",
        )

    return path


def validate_numeric_param(
    value: int | float | None,
    param_name: str,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    required: bool = True,
    allow_zero: bool = True,
) -> None:
    """Validate numeric parameters.

    Args:
        value: The numeric value to validate.
        param_name: Name of the parameter for error messages.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.
        required: Whether the parameter is required.
        allow_zero: Whether zero is allowed.

    Raises:
        ViInvalidParameterError: If validation fails.

    """
    if required:
        validate_required_param(value, param_name)

    if value is None and not required:
        return

    if not isinstance(value, (int, float)):
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be a number, got {type(value).__name__}",
        )

    if not allow_zero and value == 0:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' cannot be zero",
        )

    if min_value is not None and value < min_value:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be at least {min_value}, got {value}",
        )

    if max_value is not None and value > max_value:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be at most {max_value}, got {value}",
        )


def validate_list_param(
    value: Sequence[Any] | None,
    param_name: str,
    min_length: int = 0,
    max_length: int | None = None,
    required: bool = True,
    item_validator: Callable | None = None,
) -> None:
    """Validate list/sequence parameters.

    Args:
        value: The list/sequence to validate.
        param_name: Name of the parameter for error messages.
        min_length: Minimum number of items required.
        max_length: Maximum number of items allowed.
        required: Whether the parameter is required.
        item_validator: Optional callable to validate each item.

    Raises:
        ViInvalidParameterError: If validation fails.

    """
    if required:
        validate_required_param(value, param_name)

    if value is None and not required:
        return

    if not isinstance(value, (list, tuple, set)):
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must be a list, tuple, or set, got {type(value).__name__}",
        )

    if len(value) < min_length:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must have at least {min_length} items, got {len(value)}",
        )

    if max_length is not None and len(value) > max_length:
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' must have at most {max_length} items, got {len(value)}",
        )

    if item_validator:
        for i, item in enumerate(value):
            try:
                item_validator(item)
            except Exception as e:
                raise ViInvalidParameterError(
                    param_name,
                    f"Invalid item at index {i} in '{param_name}': {e}",
                ) from e


def validate_email(email: str | None, param_name: str = "email") -> None:
    """Validate email format.

    Args:
        email: The email address to validate.
        param_name: Name of the parameter for error messages.

    Raises:
        ViInvalidParameterError: If email format is invalid.

    """
    if email is None:
        return

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ViInvalidParameterError(
            param_name,
            f"Invalid email format: {email}",
        )


def validate_url(url: str | None, param_name: str = "url") -> None:
    """Validate URL format.

    Args:
        url: The URL to validate.
        param_name: Name of the parameter for error messages.

    Raises:
        ViInvalidParameterError: If URL format is invalid.

    """
    if url is None:
        return

    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(url_pattern, url):
        raise ViInvalidParameterError(
            param_name,
            f"Invalid URL format: {url}",
        )


def validate_pagination_params(
    page_size: int | None = None,
    page_token: str | None = None,
) -> None:
    """Validate pagination parameters.

    Args:
        page_size: Number of items per page (1-1000)
        page_token: Page token for cursor-based pagination

    """
    if page_size is not None:
        try:
            validate_numeric_param(page_size, "page_size", min_value=1, max_value=1000)
        except ViInvalidParameterError as e:
            raise ViInvalidParameterError(
                "page_size",
                f"Invalid page_size: {page_size}",
                suggestion=(
                    "page_size must be between 1 and 1000. "
                    "For most cases, the default page size (10) works well. "
                    "Example: client.datasets.list(pagination={'page_size': 10})"
                ),
            ) from e

    if page_token is not None:
        validate_string_param(page_token, "page_token", min_length=1)


def validate_sort_params(
    sort_by: str | None = None,
    sort_order: str | None = None,
    allowed_sort_fields: Sequence[str] | None = None,
) -> None:
    """Validate sorting parameters.

    Args:
        sort_by: Field name to sort by.
        sort_order: Sort order ('asc' or 'desc').
        allowed_sort_fields: List of allowed sort field names.

    Raises:
        ViInvalidParameterError: If validation fails.

    """
    if sort_by is not None:
        validate_string_param(sort_by, "sort_by", min_length=1)

        if allowed_sort_fields and sort_by not in allowed_sort_fields:
            raise ViInvalidParameterError(
                "sort_by",
                f"Invalid sort field '{sort_by}'. Allowed fields: {', '.join(allowed_sort_fields)}",
            )

    if sort_order is not None:
        if sort_order.lower() not in ["asc", "desc"]:
            raise ViInvalidParameterError(
                "sort_order",
                f"Invalid sort order '{sort_order}'. Must be 'asc' or 'desc'",
            )


def validate_secret_key(
    secret_key: str,
    param_name: str = "secret_key",
    organization_id: str | None = None,
) -> None:
    """Validate Vi SDK secret key format and length.

    Args:
        secret_key: The secret key to validate.
        param_name: Name of the parameter for error messages.
        organization_id: The organization ID for error messages.

    Raises:
        ViInvalidParameterError: If secret key format or length is invalid.

    Note:
        This function validates that the secret key:
        - Is not empty
        - Starts with the correct prefix (dtvi_)
        - Has the correct length (103 characters)

    """
    if not organization_id:
        organization_id = "YOUR_ORGANIZATION_ID"

    # Check if empty
    if not secret_key or not secret_key.strip():
        raise ViInvalidParameterError(
            param_name,
            f"Parameter '{param_name}' cannot be empty",
            suggestion=(
                "Provide a valid API key for use with the Vi SDK. "
                "You can generate a new API key in Datature Vi at "
                f"https://vi.datature.com/org/{organization_id}/settings/secret-keys"
            ),
        )

    # Check prefix
    if not secret_key.startswith(DEFAULT_SECRET_KEY_PREFIX):
        raise ViInvalidParameterError(
            param_name,
            f"Secret key must start with '{DEFAULT_SECRET_KEY_PREFIX}'",
            suggestion=(
                f"Valid secret keys start with '{DEFAULT_SECRET_KEY_PREFIX}'. "
                "Make sure you copied the complete key from the platform. "
                f"Example format: {DEFAULT_SECRET_KEY_PREFIX}abc123..."
            ),
        )

    # Check length
    if len(secret_key) != DEFAULT_SECRET_KEY_LENGTH:
        raise ViInvalidParameterError(
            param_name,
            f"Secret key must be exactly {DEFAULT_SECRET_KEY_LENGTH} characters "
            f"(current length: {len(secret_key)})",
            suggestion=(
                f"Secret keys are always {DEFAULT_SECRET_KEY_LENGTH} characters long. "
                "Make sure you copied the entire key without any extra spaces or characters."
            ),
        )
