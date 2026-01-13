#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   auth.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK authentication module.
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

from vi.client.errors import ViConfigurationError, ViErrorCode, ViInvalidParameterError
from vi.client.validation import validate_secret_key


class Authentication(ABC):
    """Abstract base class for Vi API authentication.

    All authentication methods must inherit from this class and implement
    the get_headers() method to provide authentication headers for HTTP requests.

    Attributes:
        organization_id: The organization identifier for the authenticated session.

    See Also:
        - SecretKeyAuth: Concrete implementation using secret key authentication

    """

    organization_id: str

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for HTTP requests.

        Returns:
            Dictionary of HTTP headers including authentication credentials.

        Example:
            >>> auth = SecretKeyAuth(secret_key="...", organization_id="...")
            >>> headers = auth.get_headers()
            >>> print(headers.keys())
            dict_keys(['X-Secret-Key', 'X-Organization-Id'])

        """


class SecretKeyAuth(Authentication):
    """Secret key authentication for Vi API.

    This class handles authentication using a secret key and organization ID.
    Credentials can be provided in three ways (in order of precedence):
    1. Direct parameters
    2. Configuration file
    3. Environment variables

    The secret key must start with 'dtvi_' and the organization ID must be
    a valid UUID format.

    Attributes:
        secret_key: The API secret key for authentication
        organization_id: The organization identifier

    Examples:
        Direct credentials:

        >>> auth = SecretKeyAuth(
        ...     secret_key="dtvi_your_secret_key",
        ...     organization_id="your_organization_id",
        ... )

        From environment variables:

        >>> import os
        >>> os.environ["DATATURE_VI_SECRET_KEY"] = "dtvi_your_key"
        >>> os.environ["DATATURE_VI_ORGANIZATION_ID"] = "your_org_id"
        >>> auth = SecretKeyAuth()  # Auto-loads from environment

        From config file:

        >>> auth = SecretKeyAuth(config_file="~/datature/vi/config.json")

    Note:
        The config file should be a JSON file with 'secret_key' and
        'organization_id' fields.

    See Also:
        - Authentication: Base class
        - Client: Uses this class for authentication

    """

    def __init__(
        self,
        secret_key: str | None = None,
        organization_id: str | None = None,
        config_file: str | Path | None = None,
    ):
        """Initialize secret key authentication.

        Attempts to load credentials in the following order:
        1. Direct parameters (secret_key, organization_id)
        2. Configuration file (if config_file provided)
        3. Environment variables (DATATURE_VI_SECRET_KEY, DATATURE_VI_ORGANIZATION_ID)

        Args:
            secret_key: Your Vi API secret key. Must start with 'dtvi_'.
                If None, attempts to load from config_file or environment variables.
            organization_id: Your organization UUID.
                If None, attempts to load from config_file or environment variables.
            config_file: Path to JSON configuration file containing 'secret_key'
                and 'organization_id'. Can be relative or absolute path.

        Raises:
            ViConfigurationError: If secret_key or organization_id is missing,
                invalid, or if config_file cannot be read.

        Examples:
            With direct parameters:

            >>> auth = SecretKeyAuth(
            ...     secret_key="dtvi_abc123...", organization_id="org-uuid-123"
            ... )

            With config file:

            >>> # Config file: {"secret_key": "dtvi_...", "organization_id": "org-..."}
            >>> auth = SecretKeyAuth(config_file="~/datature/vi/config.json")

            With environment variables:

            >>> # After setting DATATURE_VI_SECRET_KEY and DATATURE_VI_ORGANIZATION_ID
            >>> auth = SecretKeyAuth()

        """
        # If config file is provided, load from it first
        if config_file is not None:
            config_data = self._load_from_config(config_file)
            secret_key = secret_key or config_data.get("secret_key")
            organization_id = organization_id or config_data.get("organization_id")

        # If either credential is still None, try environment variables
        if secret_key is None or organization_id is None:
            env_secret_key = os.getenv("DATATURE_VI_SECRET_KEY")
            env_organization_id = os.getenv("DATATURE_VI_ORGANIZATION_ID")

            secret_key = secret_key or env_secret_key
            organization_id = organization_id or env_organization_id

        if not secret_key:
            raise ViConfigurationError(
                "API key is required",
                error_code=ViErrorCode.MISSING_REQUIRED_FIELD,
                suggestion=(
                    "Provide secret_key parameter, set `DATATURE_VI_SECRET_KEY` "
                    "environment variable, or use a config file"
                ),
            )

        if not organization_id:
            raise ViConfigurationError(
                "Organization ID is required",
                error_code=ViErrorCode.MISSING_REQUIRED_FIELD,
                suggestion=(
                    "Provide organization_id parameter, set `DATATURE_VI_ORGANIZATION_ID` "
                    "environment variable, or use a config file"
                ),
            )

        try:
            validate_secret_key(
                secret_key, param_name="secret_key", organization_id=organization_id
            )
        except ViInvalidParameterError as e:
            raise ViConfigurationError(
                e.message, error_code=e.error_code, suggestion=e.suggestion
            ) from e

        self.secret_key = secret_key
        self.organization_id = organization_id

    def _load_from_config(self, config_file: str | Path) -> dict[str, str]:
        """Load credentials from a config file.

        Args:
            config_file: Path to JSON config file

        Returns:
            Dictionary containing credentials

        Raises:
            ViConfigurationError: If config file is invalid or missing required fields

        """
        config_path = Path(config_file).expanduser().resolve()

        if not config_path.exists():
            raise ViConfigurationError(
                f"Config file not found: {config_path}",
                suggestion="Make sure the config file path is correct",
            )

        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ViConfigurationError(
                f"Invalid JSON in config file: {e}",
                suggestion="Make sure the config file contains valid JSON",
            ) from e
        except Exception as e:
            raise ViConfigurationError(
                f"Error reading config file: {e}",
                suggestion="Make sure you have permission to read the config file",
            ) from e

        return config_data

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for HTTP requests.

        Returns:
            Dictionary of headers to include in requests

        """
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Organization-Id": self.organization_id,
        }

    def __repr__(self) -> str:
        """Developer-friendly representation (hides sensitive data)."""
        # Show prefix (dtvi_) + first 6 chars for security (industry standard like AWS, Stripe)
        masked_key = (
            f"{self.secret_key[:11]}..." if len(self.secret_key) > 11 else "***"
        )

        return (
            f"SecretKeyAuth("
            f"secret_key='{masked_key}', "
            f"organization_id='{self.organization_id}')"
        )

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"SecretKeyAuth for organization {self.organization_id}"
