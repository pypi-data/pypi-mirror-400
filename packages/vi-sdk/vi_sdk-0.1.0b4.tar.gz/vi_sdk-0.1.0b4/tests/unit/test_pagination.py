#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_pagination.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for pagination functionality.
"""

import pytest
from vi.api.pagination import PaginatedResponse
from vi.api.types import PaginationParams


class _MultiPageMock:
    """Mock list method that returns multiple pages."""

    def __init__(self, page1_items, page2_items, page3_items):
        self.page1_items = page1_items
        self.page2_items = page2_items
        self.page3_items = page3_items

    def __call__(self, **kwargs):
        pagination = kwargs.get("pagination")
        if pagination and pagination.page_token == "token_2":
            return PaginatedResponse(items=self.page2_items, next_page="token_3")
        elif pagination and pagination.page_token == "token_3":
            return PaginatedResponse(items=self.page3_items, next_page=None)
        return PaginatedResponse(items=self.page1_items, next_page="token_2")


class _TwoPageMock:
    """Mock list method that returns two pages."""

    def __init__(self, page1_items, page2_items):
        self.page1_items = page1_items
        self.page2_items = page2_items

    def __call__(self, **kwargs):
        pagination = kwargs.get("pagination")
        if pagination and pagination.page_token == "token_2":
            return PaginatedResponse(items=self.page2_items, next_page=None)
        return PaginatedResponse(items=self.page1_items, next_page="token_2")


class _PaginationParamsCheckMock:
    """Mock that checks pagination params are preserved."""

    def __init__(self, expected_page_size: int):
        self.expected_page_size = expected_page_size

    def __call__(self, **kwargs):
        pagination = kwargs.get("pagination")
        assert pagination.page_size == self.expected_page_size
        return PaginatedResponse(items=[], next_page=None)


class _ErrorMock:
    """Mock that raises an error."""

    def __call__(self, **kwargs):
        raise ValueError("API error")


class _InvalidResponseMock:
    """Mock that returns an invalid response type."""

    def __call__(self, **kwargs):
        return {"items": []}


class _NeverCalledMock:
    """Mock that should never be called."""

    def __call__(self, **kwargs):
        raise AssertionError("Should not fetch next page")


class _EmptyResponseMock:
    """Mock that returns an empty response."""

    def __call__(self, **kwargs):
        return PaginatedResponse(items=[], next_page=None)


@pytest.mark.unit
@pytest.mark.pagination
class TestPaginatedResponse:
    """Test PaginatedResponse class."""

    def test_init_basic(self):
        """Test basic initialization."""
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        response = PaginatedResponse(items=items)

        assert response.items == items
        assert response.next_page is None
        assert response.prev_page is None

    def test_init_with_pagination(self):
        """Test initialization with pagination links."""
        items = [{"id": "1"}]
        response = PaginatedResponse(
            items=items,
            next_page="next_token_123",
            prev_page="prev_token_456",
        )

        assert response.next_page == "next_token_123"
        assert response.prev_page == "prev_token_456"

    def test_len(self):
        """Test __len__ method."""
        items = [{"id": str(i)} for i in range(5)]
        response = PaginatedResponse(items=items)
        assert len(response) == 5

    def test_getitem(self):
        """Test __getitem__ method."""
        items = [{"id": str(i)} for i in range(5)]
        response = PaginatedResponse(items=items)
        assert response[0] == {"id": "0"}
        assert response[2] == {"id": "2"}
        assert response[-1] == {"id": "4"}

    def test_bool_with_items(self):
        """Test __bool__ with items."""
        items = [{"id": "1"}]
        response = PaginatedResponse(items=items)
        assert bool(response) is True

    def test_bool_empty(self):
        """Test __bool__ with no items."""
        response = PaginatedResponse(items=[])
        assert bool(response) is False

    def test_repr(self):
        """Test __repr__ method."""
        items = [{"id": str(i)} for i in range(3)]
        response = PaginatedResponse(items=items, next_page="token")
        repr_str = repr(response)
        assert "PaginatedResponse" in repr_str
        assert "items=3" in repr_str
        assert "next_page=True" in repr_str


@pytest.mark.unit
@pytest.mark.pagination
class TestPaginatedResponseIteration:
    """Test PaginatedResponse iteration."""

    def test_iterate_single_page(self):
        """Test iterating over single page."""
        items = [{"id": str(i)} for i in range(5)]
        response = PaginatedResponse(items=items)

        pages = list(response)
        assert len(pages) == 1
        assert pages[0].items == items

    def test_iterate_multiple_pages(self):
        """Test iterating over multiple pages."""
        # Create mock list method that returns subsequent pages
        page1_items = [{"id": "1"}, {"id": "2"}]
        page2_items = [{"id": "3"}, {"id": "4"}]
        page3_items = [{"id": "5"}]

        mock_list_method = _MultiPageMock(page1_items, page2_items, page3_items)

        response = PaginatedResponse(
            items=page1_items,
            next_page="token_2",
            list_method=mock_list_method,
            method_kwargs={},
        )

        pages = list(response)
        assert len(pages) == 3
        assert pages[0].items == page1_items
        assert pages[1].items == page2_items
        assert pages[2].items == page3_items

    def test_all_items(self):
        """Test all_items iterator."""
        page1_items = [{"id": "1"}, {"id": "2"}]
        page2_items = [{"id": "3"}, {"id": "4"}]

        mock_list_method = _TwoPageMock(page1_items, page2_items)

        response = PaginatedResponse(
            items=page1_items,
            next_page="token_2",
            list_method=mock_list_method,
            method_kwargs={},
        )

        all_items = list(response.all_items())
        assert len(all_items) == 4
        assert all_items[0] == {"id": "1"}
        assert all_items[3] == {"id": "4"}

    def test_pages_method(self):
        """Test pages() method."""
        items = [{"id": "1"}]
        response = PaginatedResponse(items=items)

        pages_iter = response.pages()
        pages = list(pages_iter)
        assert len(pages) == 1
        assert pages[0].items == items

    def test_iteration_without_list_method(self):
        """Test iteration when no list method provided."""
        items = [{"id": "1"}]
        response = PaginatedResponse(items=items, next_page="token", list_method=None)

        pages = list(response)
        # Should only return current page since no list method
        assert len(pages) == 1


@pytest.mark.unit
@pytest.mark.pagination
class TestPaginatedResponseEdgeCases:
    """Test edge cases for pagination."""

    def test_empty_items(self):
        """Test with empty items list."""
        response = PaginatedResponse(items=[])
        assert len(response) == 0
        assert not list(response.all_items())

    def test_single_item(self):
        """Test with single item."""
        items = [{"id": "1"}]
        response = PaginatedResponse(items=items)
        assert len(response) == 1
        assert response[0] == {"id": "1"}

    def test_large_page(self):
        """Test with large page."""
        items = [{"id": str(i)} for i in range(1000)]
        response = PaginatedResponse(items=items)
        assert len(response) == 1000
        assert response[500] == {"id": "500"}

    def test_pagination_params_preserved(self):
        """Test that pagination params are preserved across pages."""
        page1_items = [{"id": "1"}]

        mock_list_method = _PaginationParamsCheckMock(expected_page_size=50)

        response = PaginatedResponse(
            items=page1_items,
            next_page="token",
            list_method=mock_list_method,
            method_kwargs={"pagination": PaginationParams(page_size=50)},
        )

        # Trigger pagination
        list(response)

    def test_error_during_pagination(self):
        """Test error handling during pagination."""
        page1_items = [{"id": "1"}]

        mock_list_method = _ErrorMock()

        response = PaginatedResponse(
            items=page1_items,
            next_page="token",
            list_method=mock_list_method,
            method_kwargs={},
        )

        # Should raise the error
        with pytest.raises(ValueError):
            list(response)

    def test_invalid_response_type(self):
        """Test handling of invalid response type from list method."""
        page1_items = [{"id": "1"}]

        mock_list_method = _InvalidResponseMock()

        response = PaginatedResponse(
            items=page1_items,
            next_page="token",
            list_method=mock_list_method,
            method_kwargs={},
        )

        # Should handle gracefully
        pages = list(response)
        # Should only have first page
        assert len(pages) == 1

    def test_none_next_page_stops_iteration(self):
        """Test that None next_page stops iteration."""
        items = [{"id": "1"}]

        mock_list_method = _NeverCalledMock()

        response = PaginatedResponse(
            items=items,
            next_page=None,  # No next page
            list_method=mock_list_method,
            method_kwargs={},
        )

        pages = list(response)
        assert len(pages) == 1  # Only first page

    def test_pagination_with_dict_params(self):
        """Test pagination with dictionary params."""
        page1_items = [{"id": "1"}]

        mock_list_method = _EmptyResponseMock()

        # Pass dict instead of PaginationParams
        response = PaginatedResponse(
            items=page1_items,
            next_page="token",
            list_method=mock_list_method,
            method_kwargs={"pagination": {"page_size": 10}},
        )

        pages = list(response)
        assert len(pages) == 2  # First page + fetched page

    def test_multiple_iteration_cycles(self):
        """Test multiple iteration cycles over same response."""
        items = [{"id": str(i)} for i in range(3)]
        response = PaginatedResponse(items=items)

        # First iteration
        pages1 = list(response)
        assert len(pages1) == 1

        # Second iteration
        pages2 = list(response)
        assert len(pages2) == 1

        # Results should be consistent
        assert pages1[0].items == pages2[0].items
