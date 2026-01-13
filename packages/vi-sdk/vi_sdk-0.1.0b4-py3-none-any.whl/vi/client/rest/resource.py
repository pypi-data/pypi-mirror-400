#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   resource.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK REST resource module.
"""

from abc import ABC, abstractmethod
from collections import ChainMap
from collections.abc import Iterator
from inspect import isclass
from typing import Any

from vi.api.pagination import PaginatedResponse
from vi.api.resources.waiter import ResourceWaiter
from vi.client.auth import Authentication
from vi.client.http.requester import Requester


class RESTResource(ABC):
    """A REST resource with common functionality.

    All REST resources must implement the list() method to support
    natural iteration over resource collections.
    """

    _auth: Authentication
    _requester: Requester
    _waiter: ResourceWaiter

    def __init__(self, auth: Authentication, requester: Requester):
        """Create a REST resource.

        Args:
            auth: Authentication instance containing credentials.
            requester: HTTP requester used to make API requests for the resource.

        """
        self._auth = auth
        self._requester = requester
        self._waiter = ResourceWaiter()
        self._auto_init_resources()

    @abstractmethod
    def list(self, *args, **kwargs) -> PaginatedResponse:
        """List resources with pagination support.

        This abstract method must be implemented by all subclasses.
        It should return a PaginatedResponse that supports iteration.

        Args:
            *args: Positional arguments specific to the resource.
            **kwargs: Keyword arguments including pagination parameters.

        Returns:
            PaginatedResponse containing resource objects.

        """
        raise NotImplementedError("Subclasses must implement the list() method")

    def __call__(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        """Enable calling the resource directly to iterate over all items.

        This allows natural iteration syntax by calling the resource with arguments
        and automatically iterating through all pages.

        Args:
            *args: Positional arguments to pass to the list() method.
            **kwargs: Keyword arguments to pass to the list() method.

        Returns:
            Iterator over all resource items across all pages.

        Example:
            ```python
            # For resources with required parameters (like dataset_id)
            for asset in client.assets(dataset_id="my-dataset"):
                print(asset.filename)

            # For resources with optional parameters
            for dataset in client.datasets():
                print(dataset.name)

            # With additional filtering
            for asset in client.assets("my-dataset", contents=True):
                print(asset.filename, asset.metadata)
            ```

        Note:
            This enables Pythonic iteration over paginated resources. The method
            automatically handles pagination and yields all items across all pages.

        """
        return self.list(*args, **kwargs).all_items()

    def __iter__(self) -> Iterator[Any]:
        """Enable iteration for resources with no required parameters.

        This allows direct iteration over resources whose list() method
        has no required parameters (all parameters are optional).

        Yields:
            Individual resource objects across all pages.

        Example:
            ```python
            # For resources like datasets, organizations, runs, flows
            for dataset in client.datasets:
                print(dataset.name)

            for org in client.organizations:
                print(org.name)
            ```

        Note:
            For resources requiring parameters (like Asset, Annotation),
            use the __call__ syntax instead: client.assets(dataset_id="...")

        """
        return self.list().all_items()

    def _get_all_annotations(self):
        """Get annotations for this class and all superclasses."""
        # See https://stackoverflow.com/a/72037059.
        return ChainMap(
            *(
                c.__annotations__
                for c in self.__class__.__mro__
                if "__annotations__" in c.__dict__
            )
        )

    def _auto_init_resources(self):
        for name, type_annot in self._get_all_annotations().items():
            # Don't overwrite existing fields
            if hasattr(self, name):
                continue

            # Only initialize if the type is a subclass of RESTResource
            if not isclass(type_annot) or not issubclass(type_annot, RESTResource):
                continue
            setattr(self, name, type_annot(self._auth, self._requester))
