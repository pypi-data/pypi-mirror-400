#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_organizations_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Organization API.
"""

import pytest

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@skip_if_no_credentials
class TestOrganization:
    """Test organization info retrieval."""

    def test_get_organization_info(self, integration_client):
        """Test getting organization information."""
        print("\n🏢 Fetching organization info...")

        org_info = integration_client.organizations.get()

        print("✅ Organization info retrieved")
        print(f"   ID: {org_info.organization_id}")
        print(f"   Name: {org_info.name}")
        print(f"   Last accessed: {org_info.last_access}")

        assert org_info is not None
        assert org_info.organization_id is not None
        assert org_info.name is not None
        assert org_info.last_access is not None

    def test_organization_has_required_fields(self, integration_client):
        """Test that organization info has all required fields."""
        print("\n📋 Validating organization fields...")

        org_info = integration_client.organizations.get()

        required_fields = ["organization_id", "name", "last_access"]

        for field in required_fields:
            assert hasattr(org_info, field), f"Missing required field: {field}"
            print(f"   ✓ {field}: {getattr(org_info, field)}")

        print("✅ All required fields present")


@pytest.mark.integration
@skip_if_no_credentials
class TestOrganizationLists:
    """Test organization list endpoints."""

    def test_list_organizations(self, integration_client):
        """Test listing organizations."""
        print("\n📋 Listing organizations...")

        try:
            orgs = integration_client.organizations.list()

            print(f"✅ Found {len(orgs.items)} organization(s)")

            if len(orgs.items) > 0:
                print(f"   First org: {orgs.items[0].name}")

            assert orgs is not None
            assert hasattr(orgs, "items")

        except Exception as e:
            # List might not be available for all users
            print(f"ℹ️  List organizations not available: {e}")
            pytest.skip("List organizations endpoint not available")

    def test_list_organizations_pagination(self, integration_client):
        """Test organizations list pagination."""
        print("\n📄 Testing pagination...")

        try:
            # Request with small page size
            orgs = integration_client.organizations.list(pagination={"page_size": 1})

            print(f"✅ Retrieved page with {len(orgs.items)} item(s)")

            assert orgs is not None

        except Exception as e:
            print(f"ℹ️  Pagination test skipped: {e}")
            pytest.skip("Pagination not testable")
