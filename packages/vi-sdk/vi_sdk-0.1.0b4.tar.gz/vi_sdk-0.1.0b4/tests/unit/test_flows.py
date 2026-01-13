#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_flows.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for flows API operations.
"""

from unittest.mock import Mock

import pytest

from vi.api.pagination import PaginatedResponse
from vi.api.resources.flows import responses
from vi.api.resources.flows.flows import Flow
from vi.api.responses import DeletedResource, Pagination
from vi.client.errors import ViInvalidParameterError

VALID_FLOW_ID = "flow_123"


@pytest.mark.unit
@pytest.mark.flow
class TestFlowResource:
    """Test suite for Flow resource basic operations."""

    @pytest.fixture
    def flow(self, mock_auth, mock_requester):
        """Create a Flow instance for testing.

        Args:
            mock_auth: Mock authentication object
            mock_requester: Mock HTTP requester

        Returns:
            Flow: Configured flow resource instance

        """
        return Flow(mock_auth, mock_requester)

    def test_init(self, flow):
        """Test flow initialization.

        Verifies that Flow instance is properly initialized with
        required attributes like link parser.

        """
        assert flow._link_parser is not None

    def test_list_flows(self, flow, mock_requester):
        """Test listing flows.

        Verifies that the list method correctly retrieves and paginates
        flows for the organization.

        """
        mock_flow = Mock(spec=responses.Flow)
        mock_flow.flow_id = VALID_FLOW_ID
        mock_flow.name = "Test Flow"

        mock_response = Pagination(items=[mock_flow], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = flow.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].flow_id == VALID_FLOW_ID

    def test_list_flows_with_pagination(self, flow, mock_requester):
        """Test listing flows with pagination.

        Verifies that pagination is properly handled when listing flows,
        including next_page tokens for fetching additional pages.

        """
        mock_flow1 = Mock(spec=responses.Flow)
        mock_flow1.flow_id = "flow1"

        mock_flow2 = Mock(spec=responses.Flow)
        mock_flow2.flow_id = "flow2"

        mock_response = Pagination(
            items=[mock_flow1, mock_flow2], next_page="token", prev_page=None
        )
        mock_requester.get.return_value = mock_response

        result = flow.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.next_page == "token"

    def test_get_flow(self, flow, mock_requester):
        """Test retrieving a single flow by ID.

        Verifies that the get method correctly retrieves a flow
        using its flow ID with all expected attributes.

        """
        mock_flow = Mock(spec=responses.Flow)
        mock_flow.flow_id = VALID_FLOW_ID

        mock_requester.get.return_value = mock_flow

        result = flow.get(VALID_FLOW_ID)

        assert isinstance(result, responses.Flow)
        assert result.flow_id == VALID_FLOW_ID

    def test_get_flow_invalid_id(self, flow):
        """Test getting flow with invalid ID.

        Verifies that attempting to get a flow with an empty
        flow ID raises ViInvalidParameterError.

        """
        with pytest.raises(ViInvalidParameterError):
            flow.get("")

    def test_delete_flow(self, flow, mock_requester):
        """Test deleting a flow.

        Verifies that the delete method correctly removes a flow
        and returns a DeletedResource confirmation.

        """
        mock_requester.delete.return_value = {"data": ""}

        result = flow.delete(VALID_FLOW_ID)

        assert isinstance(result, DeletedResource)
        assert result.id == VALID_FLOW_ID
        assert result.deleted is True

    def test_delete_flow_invalid_id(self, flow):
        """Test deleting flow with invalid ID.

        Verifies that attempting to delete a flow with an empty
        flow ID raises ViInvalidParameterError.

        """
        with pytest.raises(ViInvalidParameterError):
            flow.delete("")


@pytest.mark.unit
@pytest.mark.flow
class TestFlowEdgeCases:
    """Test suite for flow edge cases and error handling."""

    @pytest.fixture
    def flow(self, mock_auth, mock_requester):
        """Create a Flow instance for testing.

        Args:
            mock_auth: Mock authentication object
            mock_requester: Mock HTTP requester

        Returns:
            Flow: Configured flow resource instance

        """
        return Flow(mock_auth, mock_requester)

    def test_list_invalid_response(self, flow, mock_requester):
        """Test list with invalid response format.

        Verifies that the list method raises ValueError when the API
        returns an invalid response format.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            flow.list()

    def test_get_invalid_response(self, flow, mock_requester):
        """Test get with invalid response format.

        Verifies that the get method raises ValueError when the API
        returns an invalid response format.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            flow.get(VALID_FLOW_ID)

    def test_delete_invalid_response(self, flow, mock_requester):
        """Test delete with invalid response format.

        Verifies that the delete method raises ValueError when the API
        returns an unexpected response format.

        """
        mock_requester.delete.return_value = {"data": "unexpected"}

        with pytest.raises(ValueError):
            flow.delete(VALID_FLOW_ID)

    def test_list_empty_flows(self, flow, mock_requester):
        """Test listing when no flows exist.

        Verifies that the list method correctly handles an empty result
        set and returns an empty PaginatedResponse.

        """
        mock_response = Pagination(items=[], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = flow.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0

    def test_flow_with_special_characters(self, flow, mock_requester):
        """Test flow with special characters in name.

        Verifies that flow names containing special characters
        are correctly handled and preserved.

        """
        mock_flow = Mock(spec=responses.Flow)
        mock_flow.flow_id = VALID_FLOW_ID
        mock_flow.name = "Test Flow !@#$%"

        mock_requester.get.return_value = mock_flow

        result = flow.get(VALID_FLOW_ID)

        assert result.name == "Test Flow !@#$%"
