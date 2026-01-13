#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_auth.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for authentication module.
"""

from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from tests.conftest import (
    INVALID_SECRET_KEY_NO_PREFIX,
    INVALID_SECRET_KEY_SHORT,
    VALID_ORGANIZATION_ID,
    VALID_SECRET_KEY,
)
from vi.client.auth import SecretKeyAuth
from vi.client.errors import ViConfigurationError


@pytest.mark.unit
@pytest.mark.auth
class TestSecretKeyAuth:
    """Test SecretKeyAuth class."""

    def test_init_with_valid_credentials(
        self, valid_credentials: dict[str, str]
    ) -> None:
        """Test initialization with valid credentials.

        Args:
            valid_credentials: Fixture providing valid secret key and organization ID.

        """
        auth = SecretKeyAuth(**valid_credentials)
        assert auth.secret_key == VALID_SECRET_KEY
        assert auth.organization_id == VALID_ORGANIZATION_ID

    def test_init_with_config_file(self, config_file: Path) -> None:
        """Test initialization from config file.

        Args:
            config_file: Fixture providing path to config file.

        """
        auth = SecretKeyAuth(config_file=config_file)
        assert auth.secret_key == VALID_SECRET_KEY
        assert auth.organization_id == VALID_ORGANIZATION_ID

    def test_init_with_environment_variables(self) -> None:
        """Test initialization from environment variables.

        Tests that SecretKeyAuth can load credentials from environment variables
        DATATURE_VI_SECRET_KEY and DATATURE_VI_ORGANIZATION_ID.

        """
        auth = SecretKeyAuth()
        assert auth.secret_key == VALID_SECRET_KEY
        assert auth.organization_id == VALID_ORGANIZATION_ID

    def test_init_with_missing_secret_key(self, clean_environment: None) -> None:
        """Test initialization fails when secret_key is missing.

        Args:
            clean_environment: Fixture that clears environment variables.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(organization_id=VALID_ORGANIZATION_ID)
        assert "API key is required" in str(exc_info.value)

    def test_init_with_missing_organization_id(self, clean_environment: None) -> None:
        """Test initialization fails when organization_id is missing.

        Args:
            clean_environment: Fixture that clears environment variables.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(secret_key=VALID_SECRET_KEY)
        assert "Organization ID is required" in str(exc_info.value)

    def test_init_with_invalid_secret_key_prefix(self) -> None:
        """Test initialization fails with invalid secret key prefix.

        Secret keys must start with 'dtvi_' prefix.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(
                secret_key=INVALID_SECRET_KEY_NO_PREFIX,
                organization_id=VALID_ORGANIZATION_ID,
            )
        assert "Secret key must start with" in str(exc_info.value)
        assert "dtvi_" in str(exc_info.value)

    def test_init_with_short_secret_key(self) -> None:
        """Test initialization fails with short secret key.

        Secret keys must be exactly 103 characters long.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(
                secret_key=INVALID_SECRET_KEY_SHORT,
                organization_id=VALID_ORGANIZATION_ID,
            )
        assert "Secret key must be exactly 103 characters" in str(exc_info.value)

    def test_init_with_nonexistent_config_file(self, tmp_path: Path) -> None:
        """Test initialization fails with non-existent config file.

        Args:
            tmp_path: Pytest fixture providing temporary directory path.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(config_file=tmp_path / "nonexistent.json")
        assert "Config file not found" in str(exc_info.value)

    def test_init_with_invalid_json_config(self, invalid_config_file: Path) -> None:
        """Test initialization fails with invalid JSON config.

        Args:
            invalid_config_file: Fixture providing path to invalid JSON file.

        """
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(config_file=invalid_config_file)
        assert "Invalid JSON" in str(exc_info.value)

    def test_get_headers(self, valid_credentials: dict[str, str]) -> None:
        """Test getting authentication headers.

        Verifies that get_headers() returns proper Authorization and Organization-Id headers.

        Args:
            valid_credentials: Fixture providing valid secret key and organization ID.

        """
        auth = SecretKeyAuth(**valid_credentials)
        headers = auth.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {VALID_SECRET_KEY}"
        assert "Organization-Id" in headers
        assert headers["Organization-Id"] == VALID_ORGANIZATION_ID

    def test_parameter_precedence_over_config(self, config_file: Path) -> None:
        """Test that explicit parameters take precedence over config file.

        Args:
            config_file: Fixture providing path to config file.

        """
        different_key = "dtvi_" + "y" * 98
        auth = SecretKeyAuth(secret_key=different_key, config_file=config_file)
        assert auth.secret_key == different_key
        assert auth.organization_id == VALID_ORGANIZATION_ID  # From config

    def test_parameter_precedence_over_env(self) -> None:
        """Test that explicit parameters take precedence over environment.

        Verifies credential loading priority: explicit params > env vars.

        """
        different_key = "dtvi_" + "z" * 98
        auth = SecretKeyAuth(secret_key=different_key)
        assert auth.secret_key == different_key
        assert auth.organization_id == VALID_ORGANIZATION_ID  # From env

    def test_config_precedence_over_env(
        self, config_file: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test that config file takes precedence over environment.

        Verifies credential loading priority: config file > env vars.

        Args:
            config_file: Fixture providing path to config file.
            monkeypatch: Pytest fixture for modifying environment.

        """
        different_key = "dtvi_" + "a" * 98
        monkeypatch.setenv("DATATURE_VI_SECRET_KEY", different_key)
        monkeypatch.setenv(
            "DATATURE_VI_ORGANIZATION_ID", "different_org_id_1234567890123456"
        )

        auth = SecretKeyAuth(config_file=config_file)
        assert auth.secret_key == VALID_SECRET_KEY  # From config
        assert auth.organization_id == VALID_ORGANIZATION_ID  # From config

    def test_repr_masks_secret_key(self, valid_credentials: dict[str, str]) -> None:
        """Test that __repr__ masks the secret key.

        For security, the repr should only show the prefix and first 6 characters
        (industry standard like AWS, Stripe).

        Args:
            valid_credentials: Fixture providing valid secret key and organization ID.

        """
        auth = SecretKeyAuth(**valid_credentials)
        repr_str = repr(auth)

        # Should show prefix (dtvi_) + first 6 chars, then mask the rest
        assert "..." in repr_str
        assert VALID_SECRET_KEY[:11] in repr_str  # dtvi_ (5) + first 6 chars = 11
        assert VALID_SECRET_KEY not in repr_str  # Full key should not be in repr

    def test_str_representation(self, valid_credentials: dict[str, str]) -> None:
        """Test __str__ representation.

        Verifies that string representation doesn't expose the secret key.

        Args:
            valid_credentials: Fixture providing valid secret key and organization ID.

        """
        auth = SecretKeyAuth(**valid_credentials)
        str_repr = str(auth)

        assert "SecretKeyAuth" in str_repr
        assert VALID_ORGANIZATION_ID in str_repr
        # Secret key should not be in string representation
        assert VALID_SECRET_KEY not in str_repr


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationEdgeCases:
    """Test edge cases for authentication."""

    def test_empty_string_credentials(self) -> None:
        """Test that empty string credentials are rejected.

        Verifies that empty strings are properly validated and rejected.

        """
        with pytest.raises(ViConfigurationError):
            SecretKeyAuth(secret_key="", organization_id=VALID_ORGANIZATION_ID)

    def test_whitespace_only_credentials(self) -> None:
        """Test that whitespace-only credentials are rejected.

        Verifies that credentials containing only whitespace are invalid.

        """
        with pytest.raises(ViConfigurationError):
            SecretKeyAuth(secret_key="   ", organization_id=VALID_ORGANIZATION_ID)

    def test_none_credentials(self, clean_environment: None) -> None:
        """Test that None credentials are rejected.

        Args:
            clean_environment: Fixture that clears environment variables.

        """
        with pytest.raises(ViConfigurationError):
            SecretKeyAuth(secret_key=None, organization_id=None)

    def test_config_file_with_missing_fields(
        self, tmp_path: Path, clean_environment: None
    ) -> None:
        """Test config file with missing required fields.

        Verifies that config files must contain both secret_key and organization_id.

        Args:
            tmp_path: Pytest fixture providing temporary directory path.
            clean_environment: Fixture that clears environment variables.

        """
        config_path = tmp_path / "incomplete_config.json"
        config_path.write_text('{"secret_key": "' + VALID_SECRET_KEY + '"}')

        with pytest.raises(ViConfigurationError):
            SecretKeyAuth(config_file=config_path)

    def test_config_file_with_empty_fields(self, tmp_path: Path) -> None:
        """Test config file with empty required fields.

        Args:
            tmp_path: Pytest fixture providing temporary directory path.

        """
        config_path = tmp_path / "empty_config.json"
        config_path.write_text('{"secret_key": "", "organization_id": ""}')

        with pytest.raises(ViConfigurationError):
            SecretKeyAuth(config_file=config_path)

    def test_partial_credentials_from_multiple_sources(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Test combining credentials from different sources.

        Verifies that credentials can be loaded from multiple sources simultaneously.

        Args:
            tmp_path: Pytest fixture providing temporary directory path.
            monkeypatch: Pytest fixture for modifying environment.

        """
        # Secret key from env, org ID from config
        config_path = tmp_path / "partial_config.json"
        config_path.write_text('{"organization_id": "' + VALID_ORGANIZATION_ID + '"}')
        monkeypatch.setenv("DATATURE_VI_SECRET_KEY", VALID_SECRET_KEY)

        auth = SecretKeyAuth(config_file=config_path)
        assert auth.secret_key == VALID_SECRET_KEY
        assert auth.organization_id == VALID_ORGANIZATION_ID

    def test_exact_length_secret_key(self) -> None:
        """Test secret key with exactly the minimum length.

        Verifies that 103-character secret keys (minimum length) are accepted.

        """
        # Exactly 103 characters
        exact_key = "dtvi_" + "x" * 98
        auth = SecretKeyAuth(
            secret_key=exact_key, organization_id=VALID_ORGANIZATION_ID
        )
        assert auth.secret_key == exact_key

    def test_exact_length_organization_id(self) -> None:
        """Test organization ID with exactly the minimum length.

        Verifies that 36-character organization IDs (minimum length) are accepted.

        """
        # Exactly 36 characters
        exact_org_id = "a" * 36
        auth = SecretKeyAuth(secret_key=VALID_SECRET_KEY, organization_id=exact_org_id)
        assert auth.organization_id == exact_org_id

    def test_longer_than_minimum_credentials(self) -> None:
        """Test credentials longer than minimum are rejected.

        Verifies that secret keys must be exactly 103 characters,
        but organization IDs can be longer than 36 characters.

        """
        long_key = "dtvi_" + "x" * 150  # Longer than 103 - should fail
        long_org_id = "a" * 50  # Longer than 36 - OK for org_id

        # Secret key must be exactly 103 characters
        with pytest.raises(ViConfigurationError) as exc_info:
            SecretKeyAuth(secret_key=long_key, organization_id=long_org_id)
        assert "Secret key must be exactly 103 characters" in str(exc_info.value)
