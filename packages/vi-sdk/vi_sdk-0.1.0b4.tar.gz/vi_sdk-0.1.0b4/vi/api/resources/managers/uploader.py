#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   uploader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK uploader module.
"""

import os
from abc import ABC, abstractmethod
from threading import local
from typing import Any

import httpx
import vi.client.consts as CLIENT_CONSTS
from httpx import Timeout
from vi.client.auth import Authentication
from vi.client.http.requester import Requester


class ResourceUploader(ABC):
    """Base class for resource uploaders with parallel upload support.

    This abstract class provides the foundation for uploading various resources
    (assets, models, etc.) to the Datature Vi platform. It handles HTTP client
    configuration, connection pooling, and parallel upload coordination.

    For thread-safe parallel uploads, each thread gets its own HTTP client via
    thread-local storage to prevent connection conflicts.

    Attributes:
        _requester: HTTP requester instance for API calls.
        _auth: Authentication instance for API authorization.
        _show_progress: Whether to display progress bars during uploads.
        _max_workers: Maximum number of parallel upload workers.
        _http_client: Configured HTTP client for upload operations.
        _thread_local: Thread-local storage for per-thread HTTP clients.

    """

    _requester: Requester
    _auth: Authentication
    _show_progress: bool
    _max_workers: int
    _http_client: httpx.Client
    _thread_local: local

    def __init__(
        self, requester: Requester, auth: Authentication, show_progress: bool = True
    ):
        """Initialize ResourceUploader with parallel upload support.

        Configures the HTTP client with appropriate timeouts and connection limits
        based on the number of available CPU cores. The client is optimized for
        parallel uploads with connection pooling.

        Args:
            requester: HTTP requester instance for making authenticated API calls.
            auth: Authentication instance containing API credentials.
            show_progress: Whether to display progress bars during upload operations.
                Defaults to True.

        """
        self._requester = requester
        self._auth = auth
        self._show_progress = show_progress
        self._max_workers = min(max((os.cpu_count() or 4) * 2, 8), 32)
        self._thread_local = local()  # Thread-local storage for HTTP clients
        self._http_client = httpx.Client(
            timeout=Timeout(
                connect=CLIENT_CONSTS.REQUEST_CONNECT_TIMEOUT_SECONDS,
                read=CLIENT_CONSTS.REQUEST_READ_TIMEOUT_SECONDS,
                write=CLIENT_CONSTS.REQUEST_WRITE_TIMEOUT_SECONDS,
                pool=CLIENT_CONSTS.REQUEST_POOL_TIMEOUT_SECONDS,
            ),
            limits=httpx.Limits(
                max_connections=self._max_workers * 2,
                max_keepalive_connections=min(self._max_workers, 10),
            ),
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
        return False

    def close(self) -> None:
        """Close the HTTP client and release resources.

        This method should be called when the uploader is no longer needed
        to ensure proper cleanup of network connections and resources.
        Also closes any thread-local HTTP clients that were created.

        """
        if hasattr(self, "_http_client") and self._http_client is not None:
            self._http_client.close()

        # Close thread-local HTTP clients if any exist
        if hasattr(self, "_thread_local") and hasattr(
            self._thread_local, "http_client"
        ):
            try:
                self._thread_local.http_client.close()
            except Exception:
                pass

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            # Suppress exceptions during cleanup
            pass

    def _get_upload_http_client(self) -> httpx.Client:
        """Get or create a thread-local HTTP client for uploads.

        Each thread gets its own HTTP client to avoid conflicts when
        multiple threads try to upload resources simultaneously. This prevents
        "Bad file descriptor" errors and connection pool conflicts.

        Returns:
            Thread-local HTTP client instance with appropriate timeouts.

        """
        if not hasattr(self._thread_local, "http_client"):
            # Create a new HTTP client for this thread with the same timeout config
            self._thread_local.http_client = httpx.Client(
                timeout=Timeout(
                    connect=CLIENT_CONSTS.REQUEST_CONNECT_TIMEOUT_SECONDS,
                    read=CLIENT_CONSTS.REQUEST_READ_TIMEOUT_SECONDS,
                    write=CLIENT_CONSTS.REQUEST_WRITE_TIMEOUT_SECONDS,
                    pool=CLIENT_CONSTS.REQUEST_POOL_TIMEOUT_SECONDS,
                )
            )
        return self._thread_local.http_client

    @abstractmethod
    def upload(self, *args: Any, **kwargs: Any) -> Any:
        """Upload a resource to the server."""
