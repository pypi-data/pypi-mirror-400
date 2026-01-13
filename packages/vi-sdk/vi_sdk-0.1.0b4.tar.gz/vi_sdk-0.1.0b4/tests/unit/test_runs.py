#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_runs.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for runs API operations.
"""

from unittest.mock import Mock

import pytest

from tests.conftest import VALID_RUN_ID
from vi.api.pagination import PaginatedResponse
from vi.api.resources.runs import responses
from vi.api.resources.runs.runs import Run
from vi.api.responses import DeletedResource, Pagination
from vi.client.errors import ViInvalidParameterError


@pytest.mark.unit
@pytest.mark.run
class TestRunResource:
    """Test suite for Run resource basic operations."""

    @pytest.fixture
    def run(self, mock_auth, mock_requester):
        """Create a Run instance for testing.

        Args:
            mock_auth: Mock authentication object
            mock_requester: Mock HTTP requester

        Returns:
            Run: Configured run resource instance

        """
        return Run(mock_auth, mock_requester)

    def test_init(self, run):
        """Test run initialization.

        Verifies that Run instance is properly initialized with
        required attributes like link parser and models sub-resource.

        """
        assert run._link_parser is not None

    def test_list_runs(self, run, mock_requester):
        """Test listing runs.

        Verifies that the list method correctly retrieves and paginates
        runs for the organization.

        """
        mock_run = Mock(spec=responses.Run)
        mock_run.run_id = VALID_RUN_ID
        mock_run.name = "Test Run"

        mock_response = Pagination(items=[mock_run], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = run.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].run_id == VALID_RUN_ID

    def test_list_runs_with_pagination(self, run, mock_requester):
        """Test listing runs with pagination.

        Verifies that pagination is properly handled when listing runs,
        including next_page tokens for fetching additional pages.

        """
        mock_run1 = Mock(spec=responses.Run)
        mock_run1.run_id = "run1"

        mock_run2 = Mock(spec=responses.Run)
        mock_run2.run_id = "run2"

        mock_response = Pagination(
            items=[mock_run1, mock_run2], next_page="token", prev_page=None
        )
        mock_requester.get.return_value = mock_response

        result = run.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.next_page == "token"

    def test_get_run(self, run, mock_requester):
        """Test retrieving a single run by ID.

        Verifies that the get method correctly retrieves a run
        using its run ID with all expected attributes.

        """
        mock_run = Mock(spec=responses.Run)
        mock_run.run_id = VALID_RUN_ID
        mock_run.name = "Test Run"
        mock_run.status = "completed"

        mock_requester.get.return_value = mock_run

        result = run.get(VALID_RUN_ID)

        assert isinstance(result, responses.Run)
        assert result.run_id == VALID_RUN_ID
        assert result.status == "completed"

    def test_get_run_invalid_id(self, run):
        """Test getting run with invalid ID.

        Verifies that attempting to get a run with an empty
        run ID raises ViInvalidParameterError.

        """
        with pytest.raises(ViInvalidParameterError):
            run.get("")

    def test_delete_run(self, run, mock_requester):
        """Test deleting a run.

        Verifies that the delete method correctly removes a run
        and returns a DeletedResource confirmation.

        """
        mock_requester.delete.return_value = {"data": ""}

        result = run.delete(VALID_RUN_ID)

        assert isinstance(result, DeletedResource)
        assert result.id == VALID_RUN_ID
        assert result.deleted is True

    def test_delete_run_invalid_id(self, run):
        """Test deleting run with invalid ID.

        Verifies that attempting to delete a run with an empty
        run ID raises ViInvalidParameterError.

        """
        with pytest.raises(ViInvalidParameterError):
            run.delete("")


@pytest.mark.unit
@pytest.mark.run
class TestRunEdgeCases:
    """Test suite for run edge cases and error handling."""

    @pytest.fixture
    def run(self, mock_auth, mock_requester):
        """Create a Run instance for testing.

        Args:
            mock_auth: Mock authentication object
            mock_requester: Mock HTTP requester

        Returns:
            Run: Configured run resource instance

        """
        return Run(mock_auth, mock_requester)

    def test_list_invalid_response(self, run, mock_requester):
        """Test list with invalid response format.

        Verifies that the list method raises ValueError when the API
        returns an invalid response format.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            run.list()

    def test_get_invalid_response(self, run, mock_requester):
        """Test get with invalid response format.

        Verifies that the get method raises ValueError when the API
        returns an invalid response format.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            run.get(VALID_RUN_ID)

    def test_delete_invalid_response(self, run, mock_requester):
        """Test delete with invalid response format.

        Verifies that the delete method raises ValueError when the API
        returns an unexpected response format.

        """
        mock_requester.delete.return_value = {"data": "unexpected"}

        with pytest.raises(ValueError):
            run.delete(VALID_RUN_ID)

    def test_list_empty_runs(self, run, mock_requester):
        """Test listing when no runs exist.

        Verifies that the list method correctly handles an empty result
        set and returns an empty PaginatedResponse.

        """
        mock_response = Pagination(items=[], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = run.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0

    def test_run_with_different_statuses(self, run, mock_requester):
        """Test runs with different statuses.

        Verifies that runs can be retrieved with various status values
        (pending, running, completed, failed) and the status is preserved.

        """
        statuses = ["pending", "running", "completed", "failed"]

        for status in statuses:
            mock_run = Mock(spec=responses.Run)
            mock_run.run_id = VALID_RUN_ID
            mock_run.status = status

            mock_requester.get.return_value = mock_run

            result = run.get(VALID_RUN_ID)

            assert result.status == status
