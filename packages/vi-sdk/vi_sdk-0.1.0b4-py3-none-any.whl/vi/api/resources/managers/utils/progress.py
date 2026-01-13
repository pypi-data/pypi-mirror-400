#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   progress.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK progress manager module.
"""

import asyncio
from pathlib import Path

import msgspec
from msgspec import Struct


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


class AsyncProgressManager:
    """Async progress manager for non-blocking progress updates and manifest saves.

    Manages progress updates and manifest saves asynchronously to avoid blocking
    the main download threads. Uses queues to batch operations and reduce overhead.
    """

    def __init__(
        self, progress_bar=None, progress_task=None, file_path: Path | None = None
    ):
        self.progress_bar = progress_bar
        self.progress_task = progress_task
        self.file_path = file_path
        self.progress_queue: asyncio.Queue[int] = asyncio.Queue()
        self.manifest_queue: asyncio.Queue[DownloadManifest] = asyncio.Queue()
        self._running = False
        self._tasks: list[asyncio.Task] = []

    async def start(self):
        """Start the async progress and manifest save tasks."""
        self._running = True
        if self.progress_bar is not None:
            self._tasks.append(asyncio.create_task(self._progress_worker()))
        if self.file_path is not None:
            self._tasks.append(asyncio.create_task(self._manifest_worker()))

    async def stop(self):
        """Stop the async tasks and flush remaining operations."""
        self._running = False
        # Flush remaining operations
        if self.progress_bar is not None:
            await self.progress_queue.put(-1)  # Signal to stop
        if self.file_path is not None:
            # Create a dummy manifest to signal stop
            dummy_manifest = DownloadManifest(
                url="", total_size=0, chunk_size=0, chunks={}, output_path=""
            )
            await self.manifest_queue.put(dummy_manifest)  # Signal to stop

        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def update_progress(self, bytes_advanced: int):
        """Queue a progress update."""
        if self.progress_bar is not None:
            await self.progress_queue.put(bytes_advanced)

    async def save_manifest(self, manifest: DownloadManifest):
        """Queue a manifest save operation."""
        if self.file_path is not None:
            await self.manifest_queue.put(manifest)

    async def _progress_worker(self):
        """Worker task with batched updates for smooth progress."""
        while self._running:
            try:
                # Collect all pending updates without blocking
                total_bytes = 0
                update_count = 0

                # Drain queue in batches
                while not self.progress_queue.empty() and update_count < 100:
                    try:
                        bytes_advanced = self.progress_queue.get_nowait()
                        if bytes_advanced == -1:  # Stop signal
                            # Apply any pending updates first
                            if total_bytes > 0 and self.progress_bar is not None:
                                self.progress_bar.update(
                                    self.progress_task, advance=total_bytes
                                )
                            return

                        total_bytes += bytes_advanced
                        update_count += 1
                    except asyncio.QueueEmpty:
                        break

                # Apply batched update if we have any
                if total_bytes > 0 and self.progress_bar is not None:
                    self.progress_bar.update(self.progress_task, advance=total_bytes)

                # Update UI at consistent intervals (50ms = 20 FPS)
                await asyncio.sleep(0.05)

            except Exception:
                continue

    async def _manifest_worker(self):
        """Worker task for processing manifest saves."""
        while self._running:
            try:
                # Wait for manifest saves with timeout
                manifest = await asyncio.wait_for(
                    self.manifest_queue.get(), timeout=0.1
                )
                if manifest.url == "":  # Stop signal (dummy manifest)
                    break

                # Save manifest atomically
                await self._save_manifest_async(manifest)

            except asyncio.TimeoutError:
                continue
            except Exception:
                # Log error but continue
                continue

    async def _save_manifest_async(self, manifest: DownloadManifest):
        """Async manifest save operation."""
        if self.file_path is None:
            return

        manifest_path = self.file_path.with_suffix(self.file_path.suffix + ".manifest")
        temp_path = manifest_path.with_suffix(".manifest.tmp")

        # Write to temp file
        temp_path.write_bytes(msgspec.json.encode(manifest))
        # Atomically replace
        temp_path.replace(manifest_path)
