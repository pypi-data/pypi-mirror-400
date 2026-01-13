#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_organizations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for organizations API operations.
"""

from unittest.mock import Mock

import pytest
from tests.conftest import VALID_ORGANIZATION_ID
from vi import ViOperationError
from vi.api.pagination import PaginatedResponse
from vi.api.resources.organizations import responses
from vi.api.resources.organizations.organizations import Organization
from vi.api.responses import Pagination


@pytest.mark.unit
class TestOrganizationResource:
    """Test Organization resource."""

    @pytest.fixture
    def organization(self, mock_auth, mock_requester):
        """Create Organization instance."""
        return Organization(mock_auth, mock_requester)

    def test_init(self, organization, mock_auth):
        """Test organization initialization."""
        assert organization._link_parser is not None

    def test_list_organizations(self, organization, mock_requester):
        """Test listing organizations."""
        mock_org = Mock(spec=responses.Organization)
        mock_org.organization_id = VALID_ORGANIZATION_ID
        mock_org.name = "Test Org"

        mock_response = Pagination(items=[mock_org], next_page=None, prev_page=None)

        mock_requester.get.return_value = mock_response

        result = organization.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].organization_id == VALID_ORGANIZATION_ID
        mock_requester.get.assert_called_once()

    def test_list_organizations_multiple_pages(self, organization, mock_requester):
        """Test listing organizations with pagination."""
        mock_org1 = Mock(spec=responses.Organization)
        mock_org1.organization_id = "org1"

        mock_org2 = Mock(spec=responses.Organization)
        mock_org2.organization_id = "org2"

        mock_response = Pagination(
            items=[mock_org1, mock_org2], next_page="token", prev_page=None
        )

        mock_requester.get.return_value = mock_response

        result = organization.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.next_page == "token"

    def test_get_organization_info(self, organization, mock_requester, capsys):
        """Test getting organization info."""
        # Create a real Organization response object
        mock_org = responses.Organization(
            name="Test Organization",
            kind="organization",
            organization_id=VALID_ORGANIZATION_ID,
            last_access=1234567890000,  # milliseconds
            datasets=[],
            billing=responses.OrganizationBilling(
                payer="test@example.com",
                email="test@example.com",
                subscriber_id="sub_123",
                ledger=[],
                tier="free",
            ),
            users={},
            metadata=responses.OrganizationMetadata(
                create_date=1234567890000,  # milliseconds
                is_public=False,
                account_manager=None,
                sales_engineer=None,
            ),
            features={},
            lock_status=responses.OrganizationLockStatus(is_locked=False),
            self_link="/organizations/123",
            etag="etag123",
        )

        mock_requester.get.return_value = mock_org

        # info() returns None, it just prints information
        result = organization.info()

        assert result is None
        mock_requester.get.assert_called_once()

        # Verify something was printed
        captured = capsys.readouterr()
        assert "Test Organization" in captured.out
        assert VALID_ORGANIZATION_ID in captured.out

    def test_list_invalid_response(self, organization, mock_requester):
        """Test list with invalid response type."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError) as exc_info:
            organization.list()
        assert "Invalid response" in str(exc_info.value)

    def test_info_invalid_response(self, organization, mock_requester):
        """Test info with invalid response type."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError) as exc_info:
            organization.info()
        assert "Invalid response" in str(exc_info.value)


@pytest.mark.unit
class TestOrganizationEdgeCases:
    """Test edge cases for organizations."""

    @pytest.fixture
    def organization(self, mock_auth, mock_requester):
        """Create Organization instance."""
        return Organization(mock_auth, mock_requester)

    def test_list_empty_organizations(self, organization, mock_requester):
        """Test listing with no organizations."""
        mock_response = Pagination(items=[], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = organization.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0

    def test_organization_with_special_characters(
        self, organization, mock_requester, capsys
    ):
        """Test organization with special characters in name."""
        # Create a real Organization response object
        mock_org = responses.Organization(
            name="Test Org with Special Chars !@#$%",
            kind="organization",
            organization_id=VALID_ORGANIZATION_ID,
            last_access=1234567890000,  # milliseconds
            datasets=[],
            billing=responses.OrganizationBilling(
                payer="test@example.com",
                email="test@example.com",
                subscriber_id="sub_123",
                ledger=[],
                tier="free",
            ),
            users={},
            metadata=responses.OrganizationMetadata(
                create_date=1234567890000,  # milliseconds
                is_public=False,
                account_manager=None,
                sales_engineer=None,
            ),
            features={},
            lock_status=responses.OrganizationLockStatus(is_locked=False),
            self_link="/organizations/123",
            etag="etag123",
        )

        mock_requester.get.return_value = mock_org

        # info() returns None, it just prints information
        result = organization.info()

        assert result is None

        # Verify the special characters are in the output
        captured = capsys.readouterr()
        assert "Test Org with Special Chars !@#$%" in captured.out

    def test_multiple_list_calls(self, organization, mock_requester):
        """Test multiple consecutive list calls."""
        mock_org = Mock(spec=responses.Organization)
        mock_org.organization_id = VALID_ORGANIZATION_ID

        mock_response = Pagination(items=[mock_org], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result1 = organization.list()
        result2 = organization.list()

        assert len(result1.items) == len(result2.items)
        assert mock_requester.get.call_count == 2
