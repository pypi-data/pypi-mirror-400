#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_client_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for ViClient initialization and setup.
"""

import os

import pytest
from vi import Client
from vi.client.errors import ViAuthenticationError
from vi.logging.config import LoggingConfig, LogLevel

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@skip_if_no_credentials
class TestClientInitialization:
    """Test client initialization with real credentials."""

    def test_client_init_from_env(self, test_config):
        """Test creating client from environment variables."""
        print("\n🔧 Testing client initialization from environment...")

        # Set environment variables for this test
        secret_key = test_config.get("credentials", {}).get("secret_key")
        org_id = test_config.get("credentials", {}).get("organization_id")

        os.environ["DATATURE_VI_SECRET_KEY"] = secret_key
        os.environ["DATATURE_VI_ORGANIZATION_ID"] = org_id

        try:
            client = Client()

            print("✅ Client created successfully")
            print(f"   Organization ID: {client.organizations._auth.organization_id}")

            assert client is not None
            assert client.organizations is not None
        finally:
            # Clean up environment variables
            os.environ.pop("DATATURE_VI_SECRET_KEY", None)
            os.environ.pop("DATATURE_VI_ORGANIZATION_ID", None)

    def test_client_init_explicit_credentials(self, test_config):
        """Test creating client with explicit credentials."""
        print("\n🔧 Testing client with explicit credentials...")

        secret_key = test_config.get("credentials", {}).get("secret_key")
        org_id = test_config.get("credentials", {}).get("organization_id")

        client = Client(secret_key=secret_key, organization_id=org_id)

        print("✅ Client created with explicit credentials")

        assert client is not None

    def test_client_invalid_credentials(self):
        """Test that invalid credentials raise appropriate error."""
        print("\n❌ Testing client with invalid credentials...")

        with pytest.raises(ViAuthenticationError):
            # Use properly formatted but invalid credentials
            # API key must be 103 chars and start with 'dtvi_'
            invalid_key = "dtvi_" + "x" * 98  # 5 + 98 = 103 chars
            # Org ID must be 36 chars (UUID format)
            invalid_org = "00000000-0000-0000-0000-000000000000"

            Client(
                secret_key=invalid_key,
                organization_id=invalid_org,
            ).organizations.info()

        print("✅ Correctly raised ViAuthenticationError")

    def test_client_custom_endpoint(self, test_config):
        """Test creating client with custom API endpoint."""
        print("\n🔧 Testing client with custom endpoint...")

        endpoint = test_config.get("endpoints", {}).get(
            "api_endpoint", "https://api.vi.datature.com"
        )

        # Get credentials from config
        secret_key = test_config.get("credentials", {}).get("secret_key")
        org_id = test_config.get("credentials", {}).get("organization_id")

        client = Client(
            secret_key=secret_key,
            organization_id=org_id,
            endpoint=endpoint,
        )

        print(f"✅ Client created with custom endpoint: {endpoint}")

        assert client is not None


@pytest.mark.integration
@skip_if_no_credentials
class TestClientConnectivity:
    """Test client connectivity to API."""

    def test_client_can_connect(self, integration_client):
        """Test that client can successfully connect to API."""
        print("\n🌐 Testing API connectivity...")

        try:
            # Make a simple API call to verify connectivity
            org_info = integration_client.organizations.info()

            print("✅ Successfully connected to API")
            print(f"   Organization: {org_info.name}")

            assert org_info is not None

        except Exception as e:
            pytest.fail(f"Failed to connect to API: {e}")

    def test_client_organization_access(self, integration_client):
        """Test that client has proper organization access."""
        print("\n🏢 Testing organization access...")

        try:
            org_info = integration_client.organizations.info()

            print("✅ Organization access confirmed")
            print(f"   Organization ID: {org_info.organization_id}")
            print(f"   Name: {org_info.name}")

            assert org_info.organization_id is not None
            assert org_info.name is not None

        except Exception as e:
            pytest.fail(f"Failed to access organization: {e}")


@pytest.mark.integration
@skip_if_no_credentials
class TestClientResources:
    """Test that all client resources are accessible."""

    def test_organizations_resource_available(self, integration_client):
        """Test that organizations resource is available."""
        print("\n📦 Testing organizations resource...")

        assert integration_client.organizations is not None
        print("✅ Organizations resource available")

    def test_organizations_nested_resources(self, integration_client):
        """Test that nested resources are available."""
        print("\n📦 Testing nested resources...")

        assert integration_client.assets is not None
        print("   ✓ Assets resource available")

        assert integration_client.annotations is not None
        print("   ✓ Annotations resource available")

        assert integration_client.models is not None
        print("   ✓ Models resource available")

        print("✅ All nested resources available")


@pytest.mark.integration
@skip_if_no_credentials
class TestClientLogging:
    """Test client logging configuration."""

    def test_client_with_logging_disabled(self, test_config):
        """Test creating client with logging disabled."""
        print("\n📝 Testing client with logging disabled...")

        logging_config = LoggingConfig(enable_console=False, enable_file=False)

        secret_key = test_config.get("credentials", {}).get("secret_key")
        org_id = test_config.get("credentials", {}).get("organization_id")

        client = Client(
            secret_key=secret_key,
            organization_id=org_id,
            logging_config=logging_config,
        )

        print("✅ Client created with logging disabled")

        assert client is not None

    def test_client_with_custom_logging(self, test_config):
        """Test creating client with custom logging configuration."""
        print("\n📝 Testing client with custom logging...")

        logging_config = LoggingConfig(
            enable_console=True,
            level=LogLevel.INFO,
            log_requests=True,
            log_responses=True,
        )

        secret_key = test_config.get("credentials", {}).get("secret_key")
        org_id = test_config.get("credentials", {}).get("organization_id")

        client = Client(
            secret_key=secret_key,
            organization_id=org_id,
            logging_config=logging_config,
        )

        print("✅ Client created with custom logging")

        assert client is not None
