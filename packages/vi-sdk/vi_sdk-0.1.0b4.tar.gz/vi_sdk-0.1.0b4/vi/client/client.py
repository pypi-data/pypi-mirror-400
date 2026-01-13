#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   client.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK API client module.
"""

from abc import ABC
from collections import ChainMap
from inspect import isclass
from typing import get_type_hints

from vi.client.auth import Authentication, SecretKeyAuth
from vi.client.errors import ViConfigurationError
from vi.client.http.factory import requester_from_url
from vi.client.http.requester import Requester
from vi.client.http.retry import RetryConfig
from vi.client.rest.resource import RESTResource


class APIClient(ABC):
    """Create a new API client.

    Subclasses need not override this constructor unless they
    intend to perform their own initialization.

    Args:
        endpoint: API endpoint URL or Requester object
            The endpoint can be a string containing the API endpoint
            URL, or an already-constructed Requester object.

            The endpoint URL may be in one of the following forms:
            - ``http://ENDPOINT``, ``https://ENDPOINT``

        retry_config: Optional retry configuration for HTTP requests.
            Configure retry behavior including strategy, max retries,
            jitter, and Retry-After header respect.

        _auto_init_resources: Whether this constructor should
            initialize the REST resource classes listed in the class
            annotations. API Client users should not set this argument,
            it is intended to be used by subclasses wishing to override
            this constructor.

    """

    _auth: Authentication
    requester: Requester
    _closed: bool

    def __init__(
        self,
        endpoint: Requester | str | None = None,
        retry_config: RetryConfig | None = None,
        _auto_init_resources: bool = True,
    ):
        self._closed = False

        if isinstance(endpoint, Requester):
            self._requester = endpoint
        else:
            endpoint_str = endpoint

            if endpoint_str is None:
                raise ViConfigurationError(
                    "Unable to get API endpoint",
                    suggestion=(
                        "Provide a valid endpoint URL or configure the "
                        "DATATURE_VI_API_ENDPOINT environment variable"
                    ),
                )

            self._auth = SecretKeyAuth()
            self._requester = requester_from_url(
                self._auth, endpoint_str, retry_config=retry_config
            )

        if _auto_init_resources:
            self._auto_init_resources()

    def __enter__(self):
        """Context manager entry.

        Returns:
            Self for use in with statements.

        Raises:
            RuntimeError: If client is already closed.

        Example:
            ```python
            with vi.Client(secret_key="...", organization_id="...") as client:
                datasets = client.datasets.list()
                # Automatic cleanup on exit
            ```

        """
        if self._closed:
            raise RuntimeError("Cannot use closed client in context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        Returns:
            False to propagate any exception that occurred.

        """
        self.close()
        return False

    def close(self) -> None:
        """Close the client and release all resources.

        This method is idempotent and can be called multiple times safely.
        After calling close(), the client should not be used for new requests.

        The method performs the following cleanup operations:
        1. Closes the HTTP client (requester) and all connections
        2. Closes any resource-specific clients that have cleanup methods
        3. Marks the client as closed to prevent further use

        Examples:
            Manual cleanup:

            ```python
            client = vi.Client(secret_key="...", organization_id="...")
            try:
                datasets = client.datasets.list()
            finally:
                client.close()
            ```

            Using context manager (recommended):

            ```python
            with vi.Client(secret_key="...", organization_id="...") as client:
                datasets = client.datasets.list()
                # Automatic cleanup
            ```

        Note:
            It is safe to call this method multiple times. Subsequent calls
            will be no-ops if the client is already closed.

        """
        # Return early if already closed (idempotent)
        if self._closed:
            return

        # Close requester and all HTTP connections
        if hasattr(self, "_requester") and self._requester is not None:
            try:
                self._requester.close()
            except Exception:  # noqa: BLE001
                # Suppress exceptions during cleanup
                pass

        # Close any resource-specific clients that have cleanup methods
        # Iterate through all attributes to find resource clients
        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue
            try:
                attr = getattr(self, attr_name)
                if hasattr(attr, "close") and callable(attr.close):
                    attr.close()
            except Exception:  # noqa: BLE001
                # Suppress exceptions during cleanup
                pass

        # Mark as closed
        self._closed = True

    def __del__(self):
        """Cleanup on deletion.

        Ensures resources are released even if close() was not called explicitly.
        Exceptions are suppressed to prevent issues during interpreter shutdown.
        """
        try:
            self.close()
        except Exception:  # noqa: BLE001
            # Suppress exceptions during cleanup - critical for __del__
            # as the interpreter may be in an inconsistent state
            pass

    @property
    def is_closed(self) -> bool:
        """Check if the client has been closed.

        Returns:
            True if the client is closed, False otherwise.

        Example:
            ```python
            client = vi.Client(secret_key="...", organization_id="...")
            print(client.is_closed)  # False
            client.close()
            print(client.is_closed)  # True
            ```

        """
        return self._closed

    def _get_all_annotations(self):
        """Get annotations for this class and all superclasses."""
        # See https://stackoverflow.com/a/72037059.
        return ChainMap(*(get_type_hints(c) for c in self.__class__.__mro__))

    def _auto_init_resources(self):
        for name, type_annot in self._get_all_annotations().items():
            # Don't overwrite existing fields
            if hasattr(self, name):
                continue

            # Only initialize if the type is a subclass of RESTResource
            if not isclass(type_annot) or not issubclass(type_annot, RESTResource):
                continue

            setattr(self, name, type_annot(self._auth, self._requester))
