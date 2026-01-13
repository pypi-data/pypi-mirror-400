#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   pagination.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Pagination that works both as single page and generator.
"""

from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

from vi.api.types import PaginationParams
from vi.logging.logger import get_logger

T = TypeVar("T")
logger = get_logger("api.pagination")


class PaginatedResponse(Generic[T]):
    """A paginated response that can work both as a single page and as a generator.

    This class wraps a Pagination object and provides additional functionality
    for automatic pagination while maintaining compatibility with existing code.

    When accessed normally, it behaves like a regular Pagination object.
    When iterated over, it automatically fetches subsequent pages.

    Example:
        # Get just the first page
        page = client.datasets.list()
        print(f"First page has {len(page.items)} items")

        # Iterate over all pages
        for page in client.datasets.list():
            print(f"Page has {len(page.items)} items")

        # Iterate over all items across pages
        for item in client.datasets.list().items():
            print(f"Item: {item.name}")

    """

    def __init__(
        self,
        items: list[T],
        next_page: str | None = None,
        prev_page: str | None = None,
        list_method: Callable[..., "PaginatedResponse[T]"] | None = None,
        method_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the paginated response.

        Creates a new paginated response object containing a page of results
        with optional navigation to subsequent pages.

        Args:
            items: List of items in the current page.
            next_page: URL token for the next page of results. None if this
                is the last page.
            prev_page: URL token for the previous page of results. None if
                this is the first page.
            list_method: Method to call to fetch subsequent pages. Required
                for automatic pagination iteration. None for single-page responses.
            method_kwargs: Dictionary of keyword arguments to pass to list_method
                when fetching subsequent pages. Defaults to empty dict.

        Example:
            ```python
            # Typically created by SDK methods, not directly
            response = client.datasets.list()

            # Access current page items
            for item in response.items:
                print(item.name)

            # Iterate through all pages
            for page in response:
                print(f"Page has {len(page.items)} items")
            ```

        Note:
            This class is typically instantiated by SDK methods rather than
            created directly by users. It provides automatic pagination when
            iterating over results.

        """
        self._items = items
        self.next_page = next_page
        self.prev_page = prev_page
        self._list_method = list_method
        self._method_kwargs = method_kwargs or {}

        logger.debug(
            "Created paginated response",
            items_count=len(items),
            has_next_page=bool(next_page),
            has_list_method=bool(list_method),
        )

    @property
    def items(self) -> list[T]:
        """Get the items in the current page.

        Returns:
            List of items contained in the current page of results.

        Example:
            ```python
            response = client.datasets.list()

            # Access items in first page
            for dataset in response.items:
                print(f"Dataset: {dataset.name}")

            # Check how many items in current page
            print(f"Page contains {len(response.items)} items")
            ```

        See Also:
            - `all_items()`: Iterator over all items across all pages

        """
        return self._items

    def __iter__(self) -> Iterator["PaginatedResponse[T]"]:
        """Iterate over all pages starting from this one.

        Yields:
            Each page of results as a PaginatedResponse object.

        Example:
            ```python
            # Iterate through all pages
            for page in client.datasets.list():
                print(f"Page has {len(page.items)} items")
                for dataset in page.items:
                    print(f"  - {dataset.name}")
            ```

        See Also:
            - `all_items()`: Iterate over individual items instead of pages
            - `pages()`: Alias for this method

        """
        if not self._list_method:
            # If no list method provided, just yield this page
            yield self
            return

        logger.debug("Starting pagination iteration")

        # Yield the current page first
        yield self

        # Continue with subsequent pages if there's a next_page
        current_next_page = self.next_page

        while current_next_page:
            # Update pagination params for next iteration
            current_kwargs = self._method_kwargs.copy()
            original_pagination = current_kwargs.get("pagination", PaginationParams())

            if isinstance(original_pagination, dict):
                original_pagination = PaginationParams(**original_pagination)
            elif original_pagination is None:
                original_pagination = PaginationParams()

            # Create new PaginationParams with updated token (structs are immutable)
            pagination = PaginationParams(
                page_token=current_next_page, page_size=original_pagination.page_size
            )
            current_kwargs["pagination"] = pagination

            try:
                logger.debug(
                    "Fetching next page",
                    page_token=current_next_page,
                    page_size=pagination.page_size,
                )

                # Make the API call for the next page
                next_page_response = self._list_method(**current_kwargs)

                if not isinstance(next_page_response, PaginatedResponse):
                    logger.error(
                        f"Expected PaginatedResponse, got {type(next_page_response)}"
                    )
                    break

                logger.debug(
                    "Fetched next page",
                    items_count=len(next_page_response.items),
                    has_next_page=bool(next_page_response.next_page),
                )

                yield next_page_response

                # Update for next iteration
                current_next_page = next_page_response.next_page

            except Exception as e:
                logger.error(f"Error during pagination: {e}")
                raise

    def all_items(self) -> Iterator[T]:
        """Iterate over all items across all pages.

        Automatically fetches and yields items from all available pages,
        handling pagination transparently. This is the recommended way to
        iterate over large result sets.

        Yields:
            Individual items from all pages in sequence.

        Example:
            ```python
            # Iterate over all datasets across all pages
            for dataset in client.datasets.list().all_items():
                print(f"Dataset: {dataset.name}")

            # Convert all items to list (use with caution for large result sets)
            all_datasets = list(client.datasets.list().all_items())
            print(f"Total datasets: {len(all_datasets)}")
            ```

        Note:
            This method makes additional API calls to fetch subsequent pages
            as needed. For very large result sets, consider processing items
            page by page to reduce memory usage.

        Warning:
            Converting the entire iterator to a list with `list()` will fetch
            all pages and load all items into memory. Use carefully with large
            result sets.

        See Also:
            - `items`: Access items in current page only
            - `pages()`: Iterate over pages rather than individual items

        """
        logger.debug("Starting item iteration across pages")

        for page in self:
            yield from page.items

    def pages(self) -> Iterator["PaginatedResponse[T]"]:
        """Iterate over all pages (alias for __iter__).

        Returns:
            Iterator over PaginatedResponse pages, starting from the current page.

        Example:
            ```python
            # Same as using for page in response
            for page in client.datasets.list().pages():
                print(f"Processing page with {len(page.items)} items")
            ```

        See Also:
            - `__iter__()`: The underlying iteration implementation
            - `all_items()`: Iterate over items instead of pages

        """
        return iter(self)

    # Provide compatibility methods to make it work like Pagination
    def __len__(self) -> int:
        """Return the number of items in the current page."""
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        """Get an item by index from the current page."""
        return self._items[index]

    def __bool__(self) -> bool:
        """Return True if there are items in the current page."""
        return bool(self._items)

    def __repr__(self) -> str:
        """Return a string representation of the paginated response."""
        return f"PaginatedResponse(items={len(self._items)}, next_page={bool(self.next_page)})"
