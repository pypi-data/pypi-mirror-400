#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   downloader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets downloader module.
"""

import time
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from httpx import RemoteProtocolError, TimeoutException
from rich.progress import BarColumn, TimeElapsedColumn
from vi.api.resources.consts import SMALL_FILE_DOWNLOAD_CHUNK_SIZE
from vi.api.resources.datasets.assets import consts
from vi.api.resources.managers import ResourceDownloader
from vi.client.errors import ViError
from vi.consts import DEFAULT_ASSET_DIR
from vi.utils.progress import ViProgress


class AssetBatchDownloadProgressTracker:
    """Progress tracker for batch asset downloads with real-time updates.

    Tracks and displays progress across multiple batches of asset downloads,
    providing users with detailed status including current batch number,
    files downloaded, and completion status.

    """

    def __init__(self, progress, task, total_assets: int, total_batches: int):
        """Initialize the progress tracker.

        Args:
            progress: Rich progress bar instance for display updates.
            task: Task ID in the progress bar to update.
            total_assets: Total number of assets across all batches.
            total_batches: Total number of batches to process.

        """
        self.progress = progress
        self.task = task
        self.total_assets = total_assets
        self.total_batches = total_batches
        self.downloaded_count = 0
        self.batch_count = 0

    def start_batch(self):
        """Increment batch counter and update progress display."""
        self.batch_count += 1
        self._update_description()

    def update(self, files_completed: int):
        """Update progress with number of newly completed files.

        Args:
            files_completed: Number of files that have completed downloading.

        """
        self.downloaded_count += files_completed
        self.progress.update(self.task, advance=files_completed)
        self._update_description()

    def _update_description(self):
        """Update progress bar description with current download status."""
        self.progress.update(
            self.task,
            description=(
                f"Downloading {self.downloaded_count} / {self.total_assets}"
                f" assets (batch {self.batch_count} / {self.total_batches})"
            ),
        )

    def finish_success(self):
        """Mark download as successfully completed with success indicator."""
        self.progress.update(
            self.task,
            description=(
                f"✓ Downloaded {self.downloaded_count} / {self.total_assets}"
                f" assets complete!"
            ),
            completed=self.total_assets,
        )

    def finish_cancelled(self):
        """Mark download as cancelled with cancellation indicator."""
        self.progress.update(self.task, description="✗ Download cancelled")


class AssetDownloader(ResourceDownloader):
    """Download dataset assets with parallel downloads and batch processing.

    Downloads asset files (images, videos, etc.) from the Datature Vi platform
    using concurrent workers for optimal performance. Processes assets in batches
    to handle large datasets efficiently while managing memory usage.

    Inherits parallel download capabilities from ResourceDownloader but uses
    a different strategy optimized for many small files rather than few large files.

    """

    def download(
        self,
        dataset_id: str,
        url_batches: Iterator[list[str]],
        save_dir: Path | str = DEFAULT_ASSET_DIR,
        handler=None,
        total_assets: int = 0,
        total_batches: int = 0,
        show_progress: bool = True,
    ) -> None:
        """Download multiple batches of assets with concurrent workers.

        Processes assets in batches using parallel workers to download multiple
        files simultaneously. Supports progress tracking across batches and
        graceful cancellation via interrupt signals.

        Args:
            dataset_id: Unique identifier of the dataset.
            url_batches: Iterator yielding lists of pre-signed URLs to download.
                Each list is processed as a batch.
            save_dir: Base directory where assets will be saved. Assets are
                saved in a subdirectory named after the dataset_id. Defaults
                to ~/.datature/vi/assets/.
            handler: Graceful exit handler for interrupt detection. Optional.
            total_assets: Total number of assets across all batches for progress
                calculation. Required for progress display.
            total_batches: Total number of batches to process for progress
                calculation. Required for progress display.
            show_progress: Whether to display progress bars during download.
                Defaults to True.

        Raises:
            InterruptedError: If download is cancelled by user via signal.
            ViError: If network errors or permission issues occur during download.

        Example:
            ```python
            from vi.api.resources.datasets.assets.downloader import AssetDownloader
            from pathlib import Path

            # Create downloader with progress display
            downloader = AssetDownloader(show_progress=True, overwrite=False)

            # Prepare URL batches (typically from paginated API response)
            url_batches = [
                ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
                ["https://example.com/img3.jpg", "https://example.com/img4.jpg"],
            ]

            # Download assets
            downloader.download(
                dataset_id="dataset_abc",
                url_batches=iter(url_batches),
                save_dir=Path("./assets"),
                total_assets=4,
                total_batches=2,
            )
            ```

        Note:
            If overwrite=False, existing files are skipped automatically.
            The downloader uses ThreadPoolExecutor with worker count based on
            CPU cores for optimal parallel performance.

        See Also:
            - `ResourceDownloader`: Base class with download infrastructure
            - [Asset Guide](../../guide/assets.md): Asset download best practices

        """
        if show_progress and total_assets > 0:
            self._download_batches_with_progress(
                dataset_id, url_batches, save_dir, handler, total_assets, total_batches
            )
        else:
            self._download_batches_simple(dataset_id, url_batches, save_dir, handler)

    def _download_batches_with_progress(
        self,
        dataset_id: str,
        url_batches: Iterator[list[str]],
        save_dir: Path | str,
        handler,
        total_assets: int,
        total_batches: int,
    ) -> None:
        """Download batches with real-time progress tracking and status updates.

        Creates a progress bar showing download status including current batch,
        files completed, and time elapsed. Updates progress as each file completes.

        Args:
            dataset_id: Unique identifier of the dataset.
            url_batches: Iterator yielding lists of URLs to download.
            save_dir: Directory where assets will be saved.
            handler: Graceful exit handler for interrupt detection.
            total_assets: Total number of assets for progress calculation.
            total_batches: Total number of batches for progress display.

        Raises:
            InterruptedError: If download is cancelled by user.

        """
        with ViProgress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.2f}%",
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Downloading 0 / {total_assets} assets",
                total=total_assets,
            )

            progress_tracker = AssetBatchDownloadProgressTracker(
                progress, task, total_assets, total_batches
            )

            try:
                for batch_urls in url_batches:
                    progress_tracker.start_batch()

                    self._download_single_batch(
                        dataset_id,
                        batch_urls,
                        save_dir,
                        handler,
                        progress_callback=progress_tracker.update,
                    )

            except InterruptedError:
                progress_tracker.finish_cancelled()
                raise

            progress_tracker.finish_success()

    def _download_batches_simple(
        self,
        dataset_id: str,
        url_batches: Iterator[list[str]],
        save_dir: Path | str,
        handler,
    ) -> None:
        """Download batches without progress tracking for silent operation.

        Processes all batches sequentially without any UI updates. Useful for
        background operations or when progress display is disabled.

        Args:
            dataset_id: Unique identifier of the dataset.
            url_batches: Iterator yielding lists of URLs to download.
            save_dir: Directory where assets will be saved.
            handler: Graceful exit handler for interrupt detection.

        """
        for batch_urls in url_batches:
            self._download_single_batch(dataset_id, batch_urls, save_dir, handler)

    def _download_single_batch(
        self,
        dataset_id: str,
        download_urls: list[str],
        save_dir: Path | str = DEFAULT_ASSET_DIR,
        handler=None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> None:
        """Download a single batch of assets using concurrent workers.

        Submits download tasks to a thread pool executor and waits for completion.
        Handles cancellation, errors, and optional progress callbacks for each
        completed file.

        Args:
            dataset_id: Unique identifier of the dataset.
            download_urls: List of pre-signed URLs to download in this batch.
            save_dir: Directory where assets will be saved.
            handler: Graceful exit handler for interrupt detection. Optional.
            progress_callback: Optional callback function invoked after each
                successful download. Receives the number of completed files (1).

        Raises:
            InterruptedError: If download is cancelled by user.
            ViError: If network errors or file system issues occur.

        """
        absolute_save_path = (Path(save_dir) / dataset_id).resolve()
        absolute_save_path.mkdir(parents=True, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_url = {
                executor.submit(
                    self._download_file_worker, url, absolute_save_path, handler
                ): url
                for url in download_urls
            }

            for future in as_completed(future_to_url):
                if handler and handler.exit_now:
                    for f in future_to_url:
                        f.cancel()
                    raise InterruptedError("Download cancelled by user")

                try:
                    future.result()

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(1)

                except RemoteProtocolError as e:
                    raise ViError(
                        e,
                        suggestion=(
                            "Server connection was interrupted. This can happen with unstable "
                            "network connections or when using HTTP/2 with many concurrent downloads. "
                            "Try: (1) Check your internet connection, (2) Use http2=False parameter "
                            "to switch to HTTP/1.1 for better stability, or (3) Reduce concurrent "
                            "downloads by setting fewer workers"
                        ),
                    ) from e
                except TimeoutException as e:
                    raise ViError(
                        e,
                        suggestion=(
                            "Download timed out. Check your internet connection and try again. "
                            "For large files or slow connections, consider increasing timeout values"
                        ),
                    ) from e
                except Exception as e:
                    raise ViError(
                        e,
                        suggestion=(
                            "Check your internet connection and ensure you have "
                            "write permissions to the target directory"
                        ),
                    ) from e

    def _download_file_worker(
        self, download_url: str, file_path: Path, handler=None
    ) -> None:
        """Worker function for downloading a single asset file.

        Extracts the filename from the URL, streams the file in chunks, and
        saves it to disk. Skips download if file already exists and overwrite
        is disabled. Supports interrupt detection for graceful cancellation.

        Implements retry logic with exponential backoff for transient network
        errors like server disconnections.

        Args:
            download_url: Pre-signed URL to download from.
            file_path: Directory where the file will be saved.
            handler: Graceful exit handler for interrupt detection. Optional.

        Raises:
            InterruptedError: If download is cancelled during streaming.

        """
        filename = download_url.split("/")[-1].split("?")[0]
        target_file = file_path / filename

        if target_file.exists() and not self._overwrite:
            return

        # Retry logic for transient network errors
        for attempt in range(consts.DOWNLOAD_MAX_RETRIES):
            try:
                with self._http_client.stream("GET", download_url) as response:
                    response.raise_for_status()

                    with open(target_file, "wb") as f:
                        for chunk in response.iter_bytes(
                            chunk_size=SMALL_FILE_DOWNLOAD_CHUNK_SIZE
                        ):
                            if handler and handler.exit_now:
                                raise InterruptedError("Download cancelled by user")
                            f.write(chunk)

                # Download successful, exit retry loop
                return

            except (RemoteProtocolError, TimeoutException):
                # Clean up partial file on error
                if target_file.exists():
                    target_file.unlink()

                # If this was the last attempt, re-raise the exception
                if attempt == consts.DOWNLOAD_MAX_RETRIES - 1:
                    raise

                # Exponential backoff with cap to prevent excessive waits
                backoff_time = min(
                    consts.DOWNLOAD_RETRY_BACKOFF_BASE**attempt,
                    consts.DOWNLOAD_RETRY_MAX_BACKOFF,
                )
                time.sleep(backoff_time)
