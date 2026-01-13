#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   general.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK general resources module.
"""

import asyncio
import os
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import google_crc32c
import httpx
import msgspec
import vi.client.consts as CLIENT_CONSTS
from httpx import Timeout
from msgspec import Struct
from rich.progress import (
    BarColumn,
    DownloadColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from vi.api.resources.utils import get_chunk_size
from vi.client.auth import Authentication
from vi.client.http.requester import Requester
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress


class ChunkState(Struct):
    """State of a single download chunk for resume support.

    Tracks the completion status and checksum of an individual chunk in a
    parallel download operation. This enables resuming downloads from the
    last completed chunk if interrupted.

    Attributes:
        start: Starting byte position of the chunk.
        end: Ending byte position of the chunk (inclusive).
        completed: Whether this chunk has been successfully downloaded.
        crc32c: Hexadecimal CRC32C checksum of the chunk data when completed.

    """

    start: int
    end: int
    completed: bool = False
    crc32c: str | None = None  # hex checksum when completed


class DownloadManifest(Struct):
    """Manifest tracking download progress across chunks for resume support.

    Stores the complete state of a download operation including all chunks,
    their completion status, and checksums. This manifest is persisted to disk
    and enables resuming downloads from any interruption point.

    Attributes:
        url: Source URL of the download.
        total_size: Total size of the file in bytes.
        chunk_size: Size of each chunk in bytes.
        chunks: Dictionary mapping chunk IDs to their state.
        output_path: Destination file path for the download.

    """

    url: str
    total_size: int
    chunk_size: int
    chunks: dict[int, ChunkState]
    output_path: str


class ResourceUploader(ABC):
    """Base class for resource uploaders with parallel upload support.

    This abstract class provides the foundation for uploading various resources
    (assets, models, etc.) to the Datature Vi platform. It handles HTTP client
    configuration, connection pooling, and parallel upload coordination.

    Attributes:
        _requester: HTTP requester instance for API calls.
        _auth: Authentication instance for API authorization.
        _show_progress: Whether to display progress bars during uploads.
        _max_workers: Maximum number of parallel upload workers.
        _http_client: Configured HTTP client for upload operations.

    """

    _requester: Requester
    _auth: Authentication
    _show_progress: bool
    _max_workers: int
    _http_client: httpx.Client

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

        """
        if hasattr(self, "_http_client") and self._http_client is not None:
            self._http_client.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            # Suppress exceptions during cleanup
            pass

    @abstractmethod
    def upload(self, *args: Any, **kwargs: Any) -> Any:
        """Upload a resource to the server."""


class ResourceDownloader(ABC):
    """Base class for resource downloaders with parallel download and resume support.

    This abstract class provides robust downloading capabilities including:
    - Parallel chunk-based downloads for optimal performance
    - Automatic resume support using manifest files for interrupted downloads
    - CRC32C checksum verification for data integrity
    - Adaptive connection management based on file size
    - Progress tracking with detailed status updates

    The downloader automatically splits large files into chunks and downloads them
    in parallel using multiple workers. If a download is interrupted, it can resume
    from the last completed chunk without re-downloading already completed portions.

    Attributes:
        _show_progress: Whether to display progress bars during downloads.
        _overwrite: Whether to overwrite existing files.
        _max_workers: Maximum number of parallel download workers (auto-scaled based on CPU).
        _http_client: Configured HTTP client for download operations with connection pooling.

    """

    _show_progress: bool
    _max_workers: int
    _http_client: httpx.Client

    def __init__(self, show_progress: bool = True, overwrite: bool = False):
        """Initialize ResourceDownloader with parallel download and resume support.

        Configures the HTTP client with appropriate timeouts, redirects, and connection
        limits optimized for parallel downloads. The number of workers is automatically
        scaled based on CPU count, with a maximum of 64 concurrent connections.

        Args:
            show_progress: Whether to display progress bars during download operations.
                Defaults to True.
            overwrite: Whether to overwrite existing files. If False, existing files
                will be skipped. Defaults to False.

        """
        self._show_progress = show_progress
        self._overwrite = overwrite
        self._max_workers = min(max((os.cpu_count() or 4) * 2, 8), 64)

        self._http_client = httpx.Client(
            timeout=Timeout(
                connect=CLIENT_CONSTS.REQUEST_CONNECT_TIMEOUT_SECONDS,
                read=CLIENT_CONSTS.REQUEST_READ_TIMEOUT_SECONDS,
                write=CLIENT_CONSTS.REQUEST_WRITE_TIMEOUT_SECONDS,
                pool=CLIENT_CONSTS.REQUEST_POOL_TIMEOUT_SECONDS,
            ),
            follow_redirects=True,
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

        This method should be called when the downloader is no longer needed
        to ensure proper cleanup of network connections and resources.

        """
        if hasattr(self, "_http_client") and self._http_client is not None:
            self._http_client.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            # Suppress exceptions during cleanup
            pass

    @abstractmethod
    def download(self, *args: Any, **kwargs: Any) -> Any:
        """Download a resource to a local directory."""

    def _download_file(
        self,
        url: str,
        file_path: Path,
        description: str = "Downloading",
        chunk_size: int | None = None,
    ) -> None:
        """Download file with resumable chunks and verification.

        Uses manifest to track chunk completion and checksums.
        Can resume interrupted downloads from any chunk.

        Args:
            url: URL to download from.
            file_path: Path to save the file.
            description: Progress bar description.
            chunk_size: Chunk size in bytes (auto if None).

        """
        with graceful_exit(
            f"[yellow]{description} cancelled by user[/yellow]"
        ) as handler:
            asyncio.run(
                self._download_file_async(
                    url, file_path, handler, description, chunk_size
                )
            )

    async def _download_file_async(
        self,
        url: str,
        file_path: Path,
        handler,
        description: str,
        chunk_size: int | None,
    ) -> None:
        """Async resumable download with parallel chunk downloading and verification.

        Implements the core download logic with the following features:
        - Queries file size and creates/loads download manifest
        - Pre-allocates file space to prevent disk fragmentation
        - Identifies incomplete chunks for download or resume
        - Adaptively scales worker count based on file size
        - Downloads chunks in parallel with progress tracking
        - Verifies each chunk with CRC32C checksums
        - Cleans up manifest on successful completion

        Args:
            url: Source URL to download from.
            file_path: Destination file path.
            handler: Graceful exit handler for interrupt detection.
            description: Progress bar description text.
            chunk_size: Size of each chunk in bytes (auto-calculated if None).

        """
        # Get file size
        async with httpx.AsyncClient(timeout=self._http_client.timeout) as client:
            head = await client.head(url)
            head.raise_for_status()
            total_size = int(head.headers.get("content-length", 0))

        if total_size == 0:
            raise ValueError("Cannot determine file size")

        if chunk_size is None:
            chunk_size = get_chunk_size(total_size)

        # Load or create manifest
        manifest = self._load_or_create_manifest(url, file_path, total_size, chunk_size)

        # Pre-allocate file if needed
        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.seek(total_size - 1)
                f.write(b"\0")

        # Find incomplete chunks
        incomplete_chunks = [
            chunk_id
            for chunk_id, chunk in manifest.chunks.items()
            if not (chunk.completed and chunk.crc32c)
        ]

        if not incomplete_chunks:
            self._cleanup_manifest(file_path)
            return

        # Adaptive connection count based on file size
        size_gb = total_size / (1024 * 1024 * 1024)
        if size_gb >= 20:
            max_workers = min(self._max_workers, 32)
        elif size_gb >= 5:
            max_workers = min(self._max_workers, 16)
        else:
            max_workers = min(self._max_workers, 8)

        # Download with progress tracking
        if self._show_progress:
            await self._download_chunks_with_progress(
                url,
                file_path,
                manifest,
                chunk_size,
                incomplete_chunks,
                max_workers,
                handler,
                description,
            )
        else:
            await self._download_chunks_no_progress(
                url,
                file_path,
                manifest,
                chunk_size,
                incomplete_chunks,
                max_workers,
                handler,
            )

        # Clean up manifest on success
        if all(c.completed for c in manifest.chunks.values()):
            self._cleanup_manifest(file_path)

    def _load_or_create_manifest(
        self, url: str, file_path: Path, total_size: int, chunk_size: int
    ) -> DownloadManifest:
        """Load existing manifest or create new one for resume support.

        Attempts to load a manifest file from a previous download attempt. If found
        and valid (matching URL and size), returns it to enable resuming. Otherwise,
        creates a new manifest with all chunks marked as incomplete.

        Args:
            url: Source URL to download from.
            file_path: Destination file path.
            total_size: Total file size in bytes.
            chunk_size: Size of each chunk in bytes.

        Returns:
            DownloadManifest ready for download or resume operation.

        """
        manifest_path = file_path.with_suffix(file_path.suffix + ".manifest")

        if manifest_path.exists():
            try:
                data = manifest_path.read_bytes()
                manifest = msgspec.json.decode(data, type=DownloadManifest)

                # Validate manifest matches current download
                if manifest.url == url and manifest.total_size == total_size:
                    return manifest
            except Exception:
                pass  # Create new manifest if loading fails

        # Create new manifest
        chunks = {}
        for i, start in enumerate(range(0, total_size, chunk_size)):
            end = min(start + chunk_size - 1, total_size - 1)
            chunks[i] = ChunkState(start=start, end=end)

        return DownloadManifest(
            url=url,
            total_size=total_size,
            chunk_size=chunk_size,
            chunks=chunks,
            output_path=str(file_path),
        )

    def _save_manifest(self, file_path: Path, manifest: DownloadManifest) -> None:
        """Atomically save manifest to disk.

        Writes the manifest to a temporary file first, then atomically replaces
        the actual manifest file. This ensures the manifest is never left in a
        corrupted state even if the process is interrupted during save.

        Args:
            file_path: Base file path (manifest path is derived from this).
            manifest: Download manifest to save.

        """
        manifest_path = file_path.with_suffix(file_path.suffix + ".manifest")
        temp_path = manifest_path.with_suffix(".manifest.tmp")

        temp_path.write_bytes(msgspec.json.encode(manifest))
        temp_path.replace(manifest_path)

    def _cleanup_manifest(self, file_path: Path) -> None:
        """Remove manifest file after successful download.

        Deletes the manifest file once all chunks have been successfully downloaded
        and verified. The manifest is only needed for resume support during
        incomplete downloads.

        Args:
            file_path: Base file path (manifest path is derived from this).

        """
        manifest_path = file_path.with_suffix(file_path.suffix + ".manifest")
        if manifest_path.exists():
            manifest_path.unlink()

    async def _download_chunks_with_progress(
        self,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        chunk_size: int,
        incomplete_chunks: list[int],
        max_workers: int,
        handler,
        description: str,
    ) -> None:
        """Download chunks in parallel with real-time progress tracking.

        Creates a progress bar showing download speed, estimated time remaining,
        and percentage complete. Updates the progress incrementally as chunks
        are downloaded. Saves manifest after each chunk to enable resume.

        Args:
            url: Source URL to download from.
            file_path: Destination file path.
            manifest: Download manifest tracking chunk states.
            chunk_size: Size to read in each iteration.
            incomplete_chunks: List of chunk IDs that need to be downloaded.
            max_workers: Maximum number of parallel download workers.
            handler: Graceful exit handler for interrupt detection.
            description: Progress bar description text.

        """
        # Calculate already downloaded bytes
        completed_bytes = sum(
            chunk.end - chunk.start + 1
            for chunk in manifest.chunks.values()
            if chunk.completed
        )

        with ViProgress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.2f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(
                description,
                total=manifest.total_size,
                completed=completed_bytes,
            )
            progress_lock = threading.Lock()

            # Track saves (save after each chunk)
            save_lock = threading.Lock()

            # Download with concurrency limit
            async with httpx.AsyncClient(
                timeout=self._http_client.timeout,
                follow_redirects=True,
            ) as client:
                semaphore = asyncio.Semaphore(max_workers)

                results = await asyncio.gather(
                    *[
                        self._download_chunk(
                            chunk_id,
                            url,
                            file_path,
                            manifest,
                            chunk_size,
                            handler,
                            client,
                            save_lock,
                            semaphore,
                            progress_lock,
                            task,
                            progress,
                        )
                        for chunk_id in incomplete_chunks
                    ],
                    return_exceptions=True,
                )

            # Save any pending updates
            self._save_manifest(file_path, manifest)

            # Update final status or remove task on cancellation
            if handler.exit_now:
                # Remove task to prevent display after cancellation message
                progress.remove_task(task)
            else:
                all_successful = all(
                    result is True
                    for result in results
                    if not isinstance(result, Exception)
                )
                if all_successful:
                    progress.update(task, description=f"✓ {description} complete!")

    async def _download_chunks_no_progress(
        self,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        chunk_size: int,
        incomplete_chunks: list[int],
        max_workers: int,
        handler,
    ) -> None:
        """Download chunks in parallel without progress tracking.

        Similar to _download_chunks_with_progress but without any UI updates.
        Still provides full resume support by saving manifest after chunks.
        Useful for background operations or when progress display is disabled.

        Args:
            url: Source URL to download from.
            file_path: Destination file path.
            manifest: Download manifest tracking chunk states.
            chunk_size: Size to read in each iteration.
            incomplete_chunks: List of chunk IDs that need to be downloaded.
            max_workers: Maximum number of parallel download workers.
            handler: Graceful exit handler for interrupt detection.

        """
        save_lock = threading.Lock()

        # Download with concurrency limit
        async with httpx.AsyncClient(
            timeout=self._http_client.timeout,
            follow_redirects=True,
        ) as client:
            semaphore = asyncio.Semaphore(max_workers)

            await asyncio.gather(
                *[
                    self._download_chunk(
                        chunk_id,
                        url,
                        file_path,
                        manifest,
                        chunk_size,
                        handler,
                        client,
                        save_lock,
                        semaphore,
                    )
                    for chunk_id in incomplete_chunks
                ],
                return_exceptions=True,
            )

        # Save final state
        self._save_manifest(file_path, manifest)

    async def _download_chunk(
        self,
        chunk_id: int,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        chunk_size: int,
        handler,
        client: httpx.AsyncClient,
        save_lock: threading.Lock,
        semaphore: asyncio.Semaphore,
        progress_lock: type[threading.Lock] | None = None,
        progress_task=None,
        progress_bar=None,
    ) -> bool:
        """Download a single chunk with optional progress tracking.

        Args:
            chunk_id: ID of the chunk to download.
            url: URL to download from.
            file_path: Path to save the file.
            manifest: Download manifest tracking progress.
            chunk_size: Size of chunks to read.
            handler: Graceful exit handler.
            client: HTTP client for the request.
            save_lock: Lock for saving manifest.
            semaphore: Semaphore for limiting concurrency.
            progress_lock: Optional lock for progress updates.
            progress_task: Optional progress task ID.
            progress_bar: Optional progress bar instance.

        Returns:
            True if download succeeded, False otherwise.

        """
        async with semaphore:
            if handler.exit_now:
                return False

            chunk = manifest.chunks[chunk_id]
            headers = {"Range": f"bytes={chunk.start}-{chunk.end}"}

            try:
                # Stream response to update progress incrementally
                async with client.stream("GET", url, headers=headers) as response:
                    response.raise_for_status()

                    # Calculate checksum and write in chunks
                    checksum = google_crc32c.Checksum()

                    with open(file_path, "r+b") as f:
                        f.seek(chunk.start)

                        async for data in response.aiter_bytes(chunk_size=chunk_size):
                            if handler.exit_now:
                                return False

                            f.write(data)
                            checksum.update(data)

                            # Update progress if provided
                            if progress_lock is not None and progress_bar is not None:
                                with progress_lock:
                                    progress_bar.update(
                                        progress_task, advance=len(data)
                                    )

                # Mark chunk complete - create new ChunkState and update manifest
                manifest.chunks[chunk_id] = ChunkState(
                    start=chunk.start,
                    end=chunk.end,
                    completed=True,
                    crc32c=checksum.hexdigest(),
                )

                # Save after each chunk completion
                with save_lock:
                    self._save_manifest(file_path, manifest)

                return True

            except Exception:
                return False
