#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   downloader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK downloader module.
"""

import asyncio
import concurrent.futures
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
from rich.progress import (
    BarColumn,
    DownloadColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from vi.api.resources.managers.utils.progress import (
    AsyncProgressManager,
    ChunkState,
    DownloadManifest,
)
from vi.api.resources.utils import get_chunk_size
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress

# Progress update frequency - update every N chunks to reduce lock contention
PROGRESS_UPDATE_FREQUENCY = 16
# Manifest save frequency - save every N chunks to reduce I/O overhead
MANIFEST_SAVE_FREQUENCY = 50
STREAM_BUFFER_SIZE = 256 * 1024


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

    def __init__(
        self, show_progress: bool = True, overwrite: bool = False, http2: bool = True
    ):
        """Initialize ResourceDownloader with parallel download and resume support.

        Configures the HTTP client with appropriate timeouts, redirects, and connection
        limits optimized for parallel downloads. The number of workers is automatically
        scaled based on CPU count, with a maximum of 64 concurrent connections.

        Args:
            show_progress: Whether to display progress bars during download operations.
                Defaults to True.
            overwrite: Whether to overwrite existing files. If False, existing files
                will be skipped. Defaults to False.
            http2: Whether to enable HTTP/2 protocol. HTTP/2 can be faster but may
                have connection stability issues with some servers. If experiencing
                disconnection errors, try setting to False. Defaults to True.

        """
        self._show_progress = show_progress
        self._overwrite = overwrite
        self._max_workers = min(max((os.cpu_count() or 4) * 2, 8), 64)

        # More conservative connection limits to avoid overwhelming servers
        max_connections = min(self._max_workers * 2, 50)
        max_keepalive = min(self._max_workers, 10)

        self._http_client = httpx.Client(
            timeout=Timeout(
                connect=CLIENT_CONSTS.REQUEST_CONNECT_TIMEOUT_SECONDS,
                read=CLIENT_CONSTS.REQUEST_READ_TIMEOUT_SECONDS,
                write=CLIENT_CONSTS.REQUEST_WRITE_TIMEOUT_SECONDS,
                pool=CLIENT_CONSTS.REQUEST_POOL_TIMEOUT_SECONDS,
            ),
            follow_redirects=True,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive,
            ),
            http2=http2,
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
        with graceful_exit(f"{description} cancelled by user") as handler:
            # Check if we're already in an event loop (e.g., Jupyter notebook)
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, use asyncio.run()
                asyncio.run(
                    self._download_file_async(
                        url, file_path, handler, description, chunk_size
                    )
                )
            else:
                # Running loop exists (e.g., Jupyter), run in executor
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self._download_file_async(
                            url, file_path, handler, description, chunk_size
                        ),
                    )
                    future.result()

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

            # Create async progress manager
            progress_manager = AsyncProgressManager(
                progress_bar=progress, progress_task=task, file_path=file_path
            )

            # Start async progress and manifest workers
            await progress_manager.start()

            try:
                # Download with concurrency limit and HTTP/2 support
                async with httpx.AsyncClient(
                    timeout=self._http_client.timeout,
                    follow_redirects=True,
                    http2=True,  # Enable HTTP/2 for better multiplexing
                ) as client:
                    semaphore = asyncio.Semaphore(max_workers)

                    # Create tasks explicitly so we can cancel them
                    tasks = [
                        asyncio.create_task(
                            self._download_chunk_async(
                                chunk_id,
                                url,
                                file_path,
                                manifest,
                                handler,
                                client,
                                semaphore,
                                progress_manager,
                                chunk_size,
                            )
                        )
                        for chunk_id in incomplete_chunks
                    ]

                    # Cancellation watcher that polls handler.exit_now
                    async def cancellation_watcher():
                        while not handler.exit_now:
                            await asyncio.sleep(0.1)
                        # Cancel all download tasks
                        for task in tasks:
                            task.cancel()

                    watcher = asyncio.create_task(cancellation_watcher())

                    try:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                    finally:
                        watcher.cancel()
                        try:
                            await watcher
                        except asyncio.CancelledError:
                            pass

                # Save any pending updates
                await progress_manager.save_manifest(manifest)

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
                        progress.update(
                            task,
                            completed=manifest.total_size,
                            description=f"✓ {description} complete!",
                            refresh=True,
                        )

            finally:
                # Stop async workers
                await progress_manager.stop()

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
        # Create async progress manager for manifest saves only
        progress_manager = AsyncProgressManager(file_path=file_path)
        await progress_manager.start()

        try:
            # Download with concurrency limit and HTTP/2 support
            async with httpx.AsyncClient(
                timeout=self._http_client.timeout,
                follow_redirects=True,
                http2=True,  # Enable HTTP/2 for better multiplexing
            ) as client:
                semaphore = asyncio.Semaphore(max_workers)

                # Create tasks explicitly so we can cancel them
                tasks = [
                    asyncio.create_task(
                        self._download_chunk_no_progress_async(
                            chunk_id,
                            url,
                            file_path,
                            manifest,
                            handler,
                            client,
                            semaphore,
                            progress_manager,
                            chunk_size,
                        )
                    )
                    for chunk_id in incomplete_chunks
                ]

                # Cancellation watcher that polls handler.exit_now
                async def cancellation_watcher():
                    while not handler.exit_now:
                        await asyncio.sleep(0.1)
                    # Cancel all download tasks
                    for task in tasks:
                        task.cancel()

                watcher = asyncio.create_task(cancellation_watcher())

                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                finally:
                    watcher.cancel()
                    try:
                        await watcher
                    except asyncio.CancelledError:
                        pass

            # Save final state
            await progress_manager.save_manifest(manifest)

        finally:
            await progress_manager.stop()

    async def _download_chunk_async(
        self,
        chunk_id: int,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        handler,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        progress_manager: AsyncProgressManager,
        chunk_size: int = STREAM_BUFFER_SIZE,
    ) -> bool:
        """Download a single chunk with async progress tracking and manifest saves.

        Args:
            chunk_id: ID of the chunk to download.
            url: URL to download from.
            file_path: Path to save the file.
            manifest: Download manifest tracking progress.
            handler: Graceful exit handler.
            client: HTTP client for the request.
            semaphore: Semaphore for limiting concurrency.
            progress_manager: Async progress manager for non-blocking updates.
            chunk_size: Size of chunks to read.

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

                        bytes_downloaded = 0
                        async for data in response.aiter_bytes(chunk_size=chunk_size):
                            if handler.exit_now:
                                return False

                            f.write(data)
                            checksum.update(data)
                            bytes_downloaded += len(data)

                            # Queue progress update asynchronously
                            if bytes_downloaded >= (
                                chunk_size * PROGRESS_UPDATE_FREQUENCY
                            ):
                                await progress_manager.update_progress(bytes_downloaded)
                                bytes_downloaded = 0  # Reset counter after update

                    # Update progress for any remaining bytes
                    if bytes_downloaded > 0:
                        await progress_manager.update_progress(bytes_downloaded)

                    # Mark chunk complete - create new ChunkState and update manifest
                    manifest.chunks[chunk_id] = ChunkState(
                        start=chunk.start,
                        end=chunk.end,
                        completed=True,
                        crc32c=checksum.hexdigest(),
                    )

                    # Queue manifest save asynchronously
                    if chunk_id % MANIFEST_SAVE_FREQUENCY == 0:
                        await progress_manager.save_manifest(manifest)

                    return True

            except Exception:
                return False

    async def _download_chunk_no_progress_async(
        self,
        chunk_id: int,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        handler,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        progress_manager: AsyncProgressManager,
        chunk_size: int = STREAM_BUFFER_SIZE,
    ) -> bool:
        """Download a single chunk without progress tracking but with async manifest saves.

        Args:
            chunk_id: ID of the chunk to download.
            url: URL to download from.
            file_path: Path to save the file.
            manifest: Download manifest tracking progress.
            handler: Graceful exit handler.
            client: HTTP client for the request.
            semaphore: Semaphore for limiting concurrency.
            progress_manager: Async progress manager for manifest saves.
            chunk_size: Size of chunks to read.

        Returns:
            True if download succeeded, False otherwise.

        """
        async with semaphore:
            if handler.exit_now:
                return False

            chunk = manifest.chunks[chunk_id]
            headers = {"Range": f"bytes={chunk.start}-{chunk.end}"}

            try:
                # Stream response
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

                    # Mark chunk complete - create new ChunkState and update manifest
                    manifest.chunks[chunk_id] = ChunkState(
                        start=chunk.start,
                        end=chunk.end,
                        completed=True,
                        crc32c=checksum.hexdigest(),
                    )

                    # Queue manifest save asynchronously
                    if chunk_id % MANIFEST_SAVE_FREQUENCY == 0:
                        await progress_manager.save_manifest(manifest)

                    return True

            except Exception:
                return False

    async def _download_chunk(
        self,
        chunk_id: int,
        url: str,
        file_path: Path,
        manifest: DownloadManifest,
        handler,
        client: httpx.AsyncClient,
        save_lock: threading.Lock,
        semaphore: asyncio.Semaphore,
        chunk_size: int = STREAM_BUFFER_SIZE,
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
            handler: Graceful exit handler.
            client: HTTP client for the request.
            save_lock: Lock for saving manifest.
            semaphore: Semaphore for limiting concurrency.
            chunk_size: Size of chunks to read.
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

                        bytes_downloaded = 0
                        async for data in response.aiter_bytes(chunk_size=chunk_size):
                            if handler.exit_now:
                                return False

                            f.write(data)
                            checksum.update(data)
                            bytes_downloaded += len(data)

                            # Update progress less frequently to reduce lock contention
                            if (
                                progress_lock is not None
                                and progress_bar is not None
                                and bytes_downloaded
                                >= (chunk_size * PROGRESS_UPDATE_FREQUENCY)
                            ):
                                with progress_lock:
                                    progress_bar.update(
                                        progress_task, advance=bytes_downloaded
                                    )
                                    bytes_downloaded = 0  # Reset counter after update

                # Update progress for any remaining bytes
                if (
                    progress_lock is not None
                    and progress_bar is not None
                    and bytes_downloaded > 0
                ):
                    with progress_lock:
                        progress_bar.update(progress_task, advance=bytes_downloaded)

                # Mark chunk complete - create new ChunkState and update manifest
                manifest.chunks[chunk_id] = ChunkState(
                    start=chunk.start,
                    end=chunk.end,
                    completed=True,
                    crc32c=checksum.hexdigest(),
                )

                # Save manifest less frequently to reduce I/O overhead
                if chunk_id % MANIFEST_SAVE_FREQUENCY == 0:
                    with save_lock:
                        self._save_manifest(file_path, manifest)

                return True

            except Exception:
                return False
