#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   uploader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets uploader module.
"""

import os
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

import httpx
import msgspec
from rich.progress import BarColumn, TaskID, TimeElapsedColumn
from vi.api.resources.datasets.assets import consts, responses
from vi.api.resources.datasets.assets.links import AssetIngestionSessionLinkParser
from vi.api.resources.datasets.assets.types import (
    AssetUploadFileSpec,
    AssetUploadSession,
    AssetUploadSpec,
    BatchConfig,
)
from vi.api.resources.datasets.utils.helper import calculate_crc32c_and_detect_mime
from vi.api.resources.managers import ResourceUploader
from vi.client.errors import ViInvalidParameterError, ViValidationError
from vi.client.http.retry import RetryExecutor, RetryHandler
from vi.client.validation import validate_id_param
from vi.logging import get_logger
from vi.utils.graceful_exit import GracefulExit, graceful_exit
from vi.utils.progress import ViProgress


class AssetUploadProgressTracker:
    """Thread-safe progress tracker for asset uploads."""

    def __init__(self, progress: ViProgress, task: TaskID, total_assets: int):
        self.progress = progress
        self.task = task
        self.total_assets = total_assets
        self.completed_count = 0
        self._lock = Lock()

    def update_success(self, files_completed: int):
        """Update progress for successful uploads."""
        with self._lock:
            self.completed_count += files_completed
            self.progress.update(
                self.task,
                description=f"Uploaded {self.completed_count} / {self.total_assets} assets...",
                advance=files_completed,
            )

    def update_error(self, files_completed: int):
        """Update progress for failed uploads."""
        with self._lock:
            self.completed_count += files_completed
            self.progress.update(
                self.task,
                description=(
                    f"Uploading {self.completed_count}"
                    f"/ {self.total_assets} assets... (error occurred)"
                ),
                advance=files_completed,
            )

    def finish_cancelled(self):
        """Update progress for cancelled uploads."""
        self.progress.update(self.task, description="✗ Upload cancelled")


class ParallelBatchProcessor:
    """Handles parallel processing of upload batches.

    This class manages the execution of multiple upload batches in parallel while
    respecting the configured parallelism limits. It implements dynamic batch
    submission to ensure only a limited number of batches are active at once.

    Attributes:
        uploader: The AssetUploader instance that owns this processor
        config: Batch configuration containing upload parameters
        progress: Progress display for tracking upload status
        handler: Graceful exit handler for cancellation support
        logger: Logger for this processor

    """

    def __init__(
        self,
        uploader: "AssetUploader",
        config: BatchConfig,
        progress: ViProgress,
        handler: GracefulExit,
    ):
        """Initialize the parallel batch processor.

        Args:
            uploader: The AssetUploader instance
            config: Configuration for batch uploads
            progress: Progress tracker for UI updates
            handler: Handler for graceful cancellation

        """
        self.uploader = uploader
        self.config = config
        self.progress = progress
        self.handler = handler
        self.logger = get_logger("assets.uploader.parallel")

    def process_batches(
        self,
        batches: list[list[str]],
        max_parallel: int,
    ) -> list[responses.AssetIngestionSession]:
        """Process batches with controlled parallelism.

        Args:
            batches: List of file path batches
            max_parallel: Maximum number of batches to process in parallel

        Returns:
            List of successful ingestion session responses

        """
        total_batches = len(batches)
        session_responses = []

        executor = ThreadPoolExecutor(max_workers=max_parallel)
        try:
            future_to_batch = {}
            batch_iter = enumerate(batches, start=1)

            # Submit initial batches
            self._submit_initial_batches(
                executor,
                batch_iter,
                future_to_batch,
                min(max_parallel, total_batches),
                total_batches,
            )

            # Process completions and submit new batches
            while future_to_batch:
                if self.handler.exit_now:
                    self._cancel_all_batches(future_to_batch)
                    # Abort any in-progress HTTP requests by closing the requester's client
                    # This will cause blocked threads to immediately raise an exception
                    try:
                        self.uploader._requester.close()
                    except Exception:
                        pass  # Ignore errors during emergency shutdown
                    break

                try:
                    session_response = self._wait_for_next_completion(
                        future_to_batch, batch_iter, executor, total_batches
                    )

                    if session_response:
                        session_responses.append(session_response)
                except TimeoutError:
                    # No future completed within timeout, loop again to check exit_now
                    continue

        finally:
            # Ensure executor is shut down immediately and don't wait for workers
            executor.shutdown(wait=False, cancel_futures=True)

        return session_responses

    def _submit_initial_batches(
        self,
        executor: ThreadPoolExecutor,
        batch_iter: enumerate,
        future_to_batch: dict,
        count: int,
        total_batches: int,
    ):
        """Submit the initial wave of batches for processing.

        This submits up to `count` batches to the thread pool executor to begin
        parallel processing. This is the first step in the dynamic submission strategy.

        Args:
            executor: Thread pool executor for parallel processing
            batch_iter: Iterator over (batch_idx, batch_paths) tuples
            future_to_batch: Dictionary mapping futures to batch indices
            count: Number of initial batches to submit
            total_batches: Total number of batches (for progress tracking)

        """
        for _ in range(count):
            try:
                batch_idx, batch_paths = next(batch_iter)
                future = self._submit_batch(
                    executor, batch_idx, batch_paths, total_batches
                )
                future_to_batch[future] = batch_idx
            except StopIteration:
                break

    def _submit_batch(
        self,
        executor: ThreadPoolExecutor,
        batch_idx: int,
        batch_paths: list[str],
        total_batches: int,
    ):
        """Submit a single batch for processing.

        Args:
            executor: Thread pool executor
            batch_idx: Index of this batch (1-based)
            batch_paths: List of file paths in this batch
            total_batches: Total number of batches

        Returns:
            Future representing the batch processing task

        """
        return executor.submit(
            self.uploader.process_single_batch,
            config=self.config,
            batch_file_paths=batch_paths,
            batch_idx=batch_idx,
            total_batches=total_batches,
            progress=self.progress,
            handler=self.handler,
        )

    def _wait_for_next_completion(
        self,
        future_to_batch: dict,
        batch_iter: enumerate,
        executor: ThreadPoolExecutor,
        total_batches: int,
    ) -> responses.AssetIngestionSession | None:
        """Wait for the next batch to complete and submit a new one if available.

        This implements the dynamic submission strategy: as soon as one batch completes,
        a new batch is submitted to keep the thread pool fully utilized.

        Args:
            future_to_batch: Dictionary mapping futures to batch indices
            batch_iter: Iterator over remaining batches
            executor: Thread pool executor
            total_batches: Total number of batches

        Returns:
            The asset ingestion session response from the completed batch,
            or None if no batches completed (shouldn't happen)

        Raises:
            Exception: If the batch processing fails, all remaining batches are
                cancelled and the exception is re-raised

        """
        # Use timeout in as_completed to allow checking for cancellation
        for future in as_completed(future_to_batch, timeout=0.1):
            # Check for cancellation before processing result
            if self.handler.exit_now:
                return None

            batch_idx = future_to_batch[future]

            try:
                session_response = future.result()
                del future_to_batch[future]

                # Submit next batch if available
                self._submit_next_batch(
                    executor, batch_iter, future_to_batch, total_batches
                )

                return session_response

            except Exception as e:
                self.logger.error(
                    f"Batch {batch_idx} failed: {e}. Cancelling remaining batches."
                )
                self._cancel_all_batches(future_to_batch)
                future_to_batch.clear()
                raise

        return None

    def _submit_next_batch(
        self,
        executor: ThreadPoolExecutor,
        batch_iter: enumerate,
        future_to_batch: dict,
        total_batches: int,
    ):
        """Submit the next batch if one is available.

        This is called after a batch completes to maintain the desired level of
        parallelism. If no more batches are available, this does nothing.

        Args:
            executor: Thread pool executor
            batch_iter: Iterator over remaining batches
            future_to_batch: Dictionary mapping futures to batch indices
            total_batches: Total number of batches

        """
        try:
            batch_idx, batch_paths = next(batch_iter)
            future = self._submit_batch(executor, batch_idx, batch_paths, total_batches)
            future_to_batch[future] = batch_idx
        except StopIteration:
            pass

    def _cancel_all_batches(self, future_to_batch: dict):
        """Cancel all pending batches.

        This is called when a user cancels the upload or when a batch fails.
        All futures in the provided dictionary are cancelled.

        Args:
            future_to_batch: Dictionary of futures to cancel

        """
        for future in future_to_batch:
            future.cancel()


class AssetUploader(ResourceUploader):
    """Uploader for assets with parallel batch processing support."""

    _link_parser: AssetIngestionSessionLinkParser | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = get_logger("assets.uploader")
        # Initialize retry executor with the requester's retry handler
        self._retry_executor = RetryExecutor(
            RetryHandler(self._requester._retry_config)
        )

    def upload(
        self,
        dataset_id: str,
        paths: Path | str | Sequence[Path | str],
        failure_mode: str = "FailAfterOne",
        on_asset_overwritten: str = "RemoveLinkedResource",
        asset_source_class: str = consts.DEFAULT_ASSET_SOURCE_CLASS,
        asset_source_provider: str = consts.DEFAULT_ASSET_SOURCE_PROVIDER,
        asset_source_id: str = consts.DEFAULT_ASSET_SOURCE_ID,
        show_progress: bool = True,
    ) -> list[responses.AssetIngestionSession]:
        """Upload assets to the dataset with automatic batching and parallelization.

        Args:
            dataset_id: ID of the dataset to upload to
            paths: File path(s) to upload - can be single path or list of paths
            failure_mode:
                How to handle failures ("FailAfterOne" or "FailAfterAll"), default is "FailAfterOne"
            on_asset_overwritten:
                Action when asset exists ("RemoveLinkedResource" or
                "KeepLinkedResource"), default is "RemoveLinkedResource"
            asset_source_class: Source class for assets
            asset_source_provider: Source provider for assets
            asset_source_id: Source ID for assets
            show_progress: Whether to display progress bars during upload

        Returns:
            List of asset ingestion session responses

        Raises:
            ViInvalidParameterError: If parameters are invalid
            ViValidationError: If no valid files found

        """
        # Validate and prepare
        self._validate_upload_params(dataset_id, failure_mode, on_asset_overwritten)
        file_paths = self._collect_file_paths(paths)
        batches = self._split_into_batches(file_paths, consts.MAX_UPLOAD_BATCH_SIZE)

        # Create configuration
        config = BatchConfig(
            dataset_id=dataset_id,
            failure_mode=failure_mode,
            on_asset_overwritten=on_asset_overwritten,
            asset_source_class=asset_source_class,
            asset_source_provider=asset_source_provider,
            asset_source_id=asset_source_id,
        )

        # Process batches
        with graceful_exit("Upload cancelled by user") as handler:
            if show_progress:
                with self._create_progress_display() as progress:
                    if len(batches) > 1 and consts.MAX_PARALLEL_BATCHES > 1:
                        return self._process_batches_parallel(
                            batches, config, progress, handler
                        )

                    return self._process_batches_sequential(
                        batches, config, progress, handler
                    )
            else:
                # No progress display - use None as progress indicator
                if len(batches) > 1 and consts.MAX_PARALLEL_BATCHES > 1:
                    return self._process_batches_parallel(
                        batches, config, None, handler
                    )

                return self._process_batches_sequential(batches, config, None, handler)

    def _validate_upload_params(
        self, dataset_id: str, failure_mode: str, on_asset_overwritten: str
    ):
        """Validate upload parameters.

        Ensures all required parameters are valid before starting the upload process.
        Raises appropriate exceptions for invalid values.

        Args:
            dataset_id: The dataset ID to validate
            failure_mode: The failure handling mode to validate
            on_asset_overwritten: The overwrite handling mode to validate

        Raises:
            ViInvalidParameterError: If any parameter is invalid

        """
        validate_id_param(dataset_id, "dataset_id")

        if failure_mode not in ["FailAfterOne", "FailAfterAll"]:
            raise ViInvalidParameterError(
                "failure_mode",
                f"Invalid failure_mode '{failure_mode}'. Must be 'FailAfterOne' or 'FailAfterAll'",
            )

        if on_asset_overwritten not in ["RemoveLinkedResource", "KeepLinkedResource"]:
            raise ViInvalidParameterError(
                "on_asset_overwritten",
                f"Invalid on_asset_overwritten '{on_asset_overwritten}'. "
                "Must be 'RemoveLinkedResource' or 'KeepLinkedResource'",
            )

    def _collect_file_paths(
        self, paths: Path | str | Sequence[Path | str]
    ) -> list[str]:
        """Collect all file paths from the provided input.

        Parses the input paths (which can be files, directories, or lists of either)
        and collects all valid asset files for upload.

        Args:
            paths: Single path, directory, or sequence of paths to collect files from

        Returns:
            List of absolute file paths ready for upload

        Raises:
            ViValidationError: If no valid files are found

        """
        file_paths = self._parse_asset_paths(paths)
        if not file_paths:
            raise ViValidationError(
                "No valid files found to upload",
                suggestion="Check that the provided paths exist and contain supported file formats",
            )
        return file_paths

    def _split_into_batches(
        self, file_paths: list[str], batch_size: int
    ) -> list[list[str]]:
        """Split file paths into batches of specified size.

        Divides the file list into batches according to the specified batch size
        to respect API limits and optimize parallel processing.

        Args:
            file_paths: List of file paths to split
            batch_size: Maximum number of files per batch

        Returns:
            List of batches, where each batch is a list of file paths

        """
        return [
            file_paths[i : i + batch_size]
            for i in range(0, len(file_paths), batch_size)
        ]

    def _create_progress_display(self) -> ViProgress:
        """Create the progress bar display for upload tracking.

        Returns:
            Configured ViProgress instance for displaying upload progress

        """
        return ViProgress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.2f}%",
            TimeElapsedColumn(),
            transient=True,
        )

    def _process_batches_parallel(
        self,
        batches: list[list[str]],
        config: BatchConfig,
        progress: ViProgress,
        handler: GracefulExit,
    ) -> list[responses.AssetIngestionSession]:
        """Process multiple batches in parallel with controlled concurrency.

        Uses the ParallelBatchProcessor to execute batches concurrently while
        respecting the MAX_PARALLEL_BATCHES limit. Implements dynamic batch
        submission to maximize throughput.

        Args:
            batches: List of file path batches to process
            config: Batch configuration
            progress: Progress tracker
            handler: Graceful exit handler

        Returns:
            List of successful ingestion session responses

        """
        processor = ParallelBatchProcessor(self, config, progress, handler)
        max_parallel = min(consts.MAX_PARALLEL_BATCHES, len(batches))
        return processor.process_batches(batches, max_parallel)

    def _process_batches_sequential(
        self,
        batches: list[list[str]],
        config: BatchConfig,
        progress: ViProgress,
        handler: GracefulExit,
    ) -> list[responses.AssetIngestionSession]:
        """Process batches one at a time in sequence.

        Used when there's only one batch or when parallel processing is disabled.
        Processes each batch completely before moving to the next.

        Args:
            batches: List of file path batches to process
            config: Batch configuration
            progress: Progress tracker
            handler: Graceful exit handler

        Returns:
            List of successful ingestion session responses

        """
        session_responses = []
        total_batches = len(batches)

        for batch_idx, batch_paths in enumerate(batches, start=1):
            session_response = self.process_single_batch(
                config=config,
                batch_file_paths=batch_paths,
                batch_idx=batch_idx,
                total_batches=total_batches,
                progress=progress,
                handler=handler,
            )

            if session_response is None:
                break  # Cancelled

            session_responses.append(session_response)

        return session_responses

    def process_single_batch(
        self,
        config: BatchConfig,
        batch_file_paths: list[str],
        batch_idx: int,
        total_batches: int,
        progress: ViProgress,
        handler: GracefulExit,
    ) -> responses.AssetIngestionSession | None:
        """Process a single batch (preparation + upload).

        Args:
            config: Batch configuration
            batch_file_paths: List of file paths in this batch
            batch_idx: Index of this batch (1-based)
            total_batches: Total number of batches
            progress: Progress tracker
            handler: Graceful exit handler

        Returns:
            Asset ingestion session response or None if cancelled

        """
        # Early cancellation check
        if handler.exit_now:
            return None

        batch_info = (
            f" (batch {batch_idx}/{total_batches})" if total_batches > 1 else ""
        )

        # Step 1: Prepare assets
        session_response = self._prepare_batch(
            config, batch_file_paths, batch_info, progress, handler
        )

        if session_response is None:
            return None  # Cancelled

        # Step 2: Upload assets
        self._upload_batch(
            batch_file_paths,
            session_response.status.assets,
            batch_info,
            progress,
            handler,
        )

        return session_response

    def _prepare_batch(
        self,
        config: BatchConfig,
        file_paths: list[str],
        batch_info: str,
        progress: ViProgress | None,
        handler: GracefulExit,
    ) -> responses.AssetIngestionSession | None:
        """Prepare a batch for upload by generating metadata and creating a session.

        This performs two main steps:
        1. Generate file specifications (MIME type, CRC32C, etc.) for each file
        2. Create an ingestion session via API with the generated specs

        Args:
            config: Batch configuration with upload parameters
            file_paths: List of file paths in this batch
            batch_info: Batch identifier string for progress display
            progress: Progress tracker (None if progress display is disabled)
            handler: Graceful exit handler

        Returns:
            Asset ingestion session response, or None if cancelled

        Raises:
            ValueError: If the API returns an invalid response

        """
        prep_task = None
        if progress:
            prep_task = progress.add_task(
                f"Preparing assets{batch_info}...",
                total=len(file_paths) + 1,
            )

        try:
            # Generate file specs
            assets = self._generate_file_specs(
                file_paths, batch_info, progress, prep_task, handler
            )

            if assets is None:
                return None  # Cancelled

            # Check for cancellation before making API call
            if handler.exit_now:
                return None

            # Create ingestion session
            if progress and prep_task is not None:
                progress.update(
                    prep_task, description=f"Creating ingestion session{batch_info}..."
                )

            session = self._create_ingestion_session(config, assets, handler)

            if progress and prep_task is not None:
                progress.update(prep_task, completed=len(file_paths) + 1)
            return session

        except KeyboardInterrupt:
            # Propagate KeyboardInterrupt from within HTTP request to signal cancellation
            return None
        finally:
            if progress and prep_task is not None:
                progress.remove_task(prep_task)

    def _generate_file_specs(
        self,
        file_paths: list[str],
        batch_info: str,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> list[AssetUploadFileSpec] | None:
        """Generate file specifications for all files in the batch.

        For each file, generates metadata including:
        - File size and name
        - MIME type
        - CRC32C checksum
        - Asset kind (Image/Video/MedicalImage)

        This is the most time-consuming part of preparation as it reads
        each file to calculate checksums. Uses parallel processing for
        batches larger than FILE_SPEC_PARALLEL_THRESHOLD.

        Args:
            file_paths: List of file paths to generate specs for
            batch_info: Batch identifier for progress display
            progress: Progress tracker (None if progress display is disabled)
            task: Progress task ID (None if progress display is disabled)
            handler: Graceful exit handler

        Returns:
            List of file specifications, or None if cancelled

        """
        # Use parallel processing for larger batches to maximize throughput
        if len(file_paths) >= consts.FILE_SPEC_PARALLEL_THRESHOLD:
            return self._generate_file_specs_parallel(
                file_paths, batch_info, progress, task, handler
            )

        # Sequential processing for small batches (less overhead)
        return self._generate_file_specs_sequential(
            file_paths, batch_info, progress, task, handler
        )

    def _generate_file_specs_sequential(
        self,
        file_paths: list[str],
        batch_info: str,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> list[AssetUploadFileSpec] | None:
        """Generate file specifications sequentially (used for small batches).

        Args:
            file_paths: List of file paths to generate specs for
            batch_info: Batch identifier for progress display
            progress: Progress tracker (None if progress display is disabled)
            task: Progress task ID (None if progress display is disabled)
            handler: Graceful exit handler

        Returns:
            List of file specifications, or None if cancelled

        """
        assets = []
        total_files = len(file_paths)

        for idx, file_path in enumerate(file_paths, start=1):
            if handler.exit_now:
                return None  # Cancelled

            if progress and task is not None:
                progress.update(
                    task,
                    description=f"Preparing assets{batch_info}... ({idx}/{total_files})",
                    advance=1,
                )

            file_spec = self._generate_asset_file_spec(file_path)
            if file_spec is not None:
                assets.append(file_spec)

        return assets

    def _generate_file_specs_parallel(
        self,
        file_paths: list[str],
        batch_info: str,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> list[AssetUploadFileSpec] | None:
        """Generate file specifications in parallel (used for large batches).

        Uses a ThreadPoolExecutor to process multiple files concurrently,
        significantly improving throughput for I/O-bound operations like
        reading files for CRC32C calculation.

        Args:
            file_paths: List of file paths to generate specs for
            batch_info: Batch identifier for progress display
            progress: Progress tracker (None if progress display is disabled)
            task: Progress task ID (None if progress display is disabled)
            handler: Graceful exit handler

        Returns:
            List of file specifications, or None if cancelled

        """
        assets: list[AssetUploadFileSpec] = []
        completed_count = 0
        total_files = len(file_paths)
        lock = Lock()

        def process_file(file_path: str) -> AssetUploadFileSpec | None:
            """Process a single file and update progress.

            Note: KeyboardInterrupt is allowed to propagate from file operations
            to ensure immediate cancellation when user presses Ctrl+C.
            """
            nonlocal completed_count

            # Check if cancellation was requested
            if handler.exit_now:
                return None

            file_spec = self._generate_asset_file_spec(file_path)

            # Thread-safe progress update
            with lock:
                completed_count += 1
                if progress and task is not None:
                    progress.update(
                        task,
                        description=f"Preparing assets{batch_info}... ({completed_count}/{total_files})",
                        advance=1,
                    )

            return file_spec

        executor = ThreadPoolExecutor(max_workers=consts.MAX_PARALLEL_FILE_SPEC_WORKERS)
        try:
            # Submit all files for processing
            futures = {executor.submit(process_file, path): path for path in file_paths}

            # Collect results as they complete with periodic cancellation checks
            remaining_futures = set(futures.keys())
            while remaining_futures:
                if handler.exit_now:
                    # Cancel remaining futures
                    for f in remaining_futures:
                        f.cancel()
                    return None

                try:
                    # Check for completed futures with short timeout
                    for future in as_completed(remaining_futures, timeout=0.1):
                        remaining_futures.discard(future)
                        try:
                            file_spec = future.result()
                            if file_spec is not None:
                                # Thread-safe append
                                with lock:
                                    assets.append(file_spec)
                        except Exception as e:
                            file_path = futures[future]
                            self._logger.error(
                                f"Error processing file {file_path}: {e}"
                            )
                            # Continue processing other files
                        break  # Process one future at a time to check handler.exit_now
                except TimeoutError:
                    # No futures completed in timeout period, loop again to check exit_now
                    continue

        finally:
            # Ensure executor shuts down immediately without waiting
            executor.shutdown(wait=False, cancel_futures=True)

        return assets

    def _create_ingestion_session(
        self,
        config: BatchConfig,
        assets: list[AssetUploadFileSpec],
        handler: GracefulExit | None = None,
    ) -> responses.AssetIngestionSession:
        """Create an asset ingestion session via API.

        Sends the file specifications to the API to create an ingestion session.
        The API responds with signed URLs for uploading each asset.

        Args:
            config: Batch configuration
            assets: List of file specifications
            handler: Optional graceful exit handler for cancellation support

        Returns:
            Asset ingestion session with upload URLs

        Raises:
            ValueError: If the API response is invalid
            KeyboardInterrupt: If cancellation was requested before making the request

        """
        # Final cancellation check before making the HTTP request
        if handler and handler.exit_now:
            raise KeyboardInterrupt(
                "Upload cancelled before creating ingestion session"
            )

        self._link_parser = AssetIngestionSessionLinkParser(
            self._auth.organization_id,
            config.dataset_id,
            config.asset_source_class,
            config.asset_source_provider,
            config.asset_source_id,
        )

        upload_session = AssetUploadSession(
            spec=AssetUploadSpec(
                assets=assets,
                failure_mode=config.failure_mode,
                on_asset_overwritten=config.on_asset_overwritten,
            )
        )

        response = self._requester.post(
            self._link_parser(),
            response_type=responses.AssetIngestionSession,
            json_data=msgspec.to_builtins(upload_session, str_keys=True),
        )

        if not isinstance(response, responses.AssetIngestionSession):
            raise ValueError(f"Invalid response {response} with type {type(response)}")

        return response

    def _upload_batch(
        self,
        file_paths: list[str],
        assets_for_upload: list[responses.AssetForUpload],
        batch_info: str,
        progress: ViProgress | None,
        handler: GracefulExit,
    ):
        """Upload all assets in a batch using their signed URLs.

        Performs the actual file uploads using the signed URLs provided by the
        ingestion session. Uses parallel threads for efficient upload.

        Args:
            file_paths: List of file paths to upload
            assets_for_upload: List of asset upload info with signed URLs
            batch_info: Batch identifier for progress display
            progress: Progress tracker (None if progress display is disabled)
            handler: Graceful exit handler

        """
        upload_task = None
        if progress:
            upload_task = progress.add_task(
                f"Uploading assets{batch_info}...",
                total=len(assets_for_upload),
            )

        try:
            self._upload_assets_parallel(
                file_paths, assets_for_upload, progress, upload_task, handler
            )
        finally:
            if progress and upload_task is not None:
                progress.remove_task(upload_task)

    def _upload_assets_parallel(
        self,
        file_paths: list[str],
        assets_for_upload: list[responses.AssetForUpload],
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ):
        """Upload assets in parallel using thread pool."""
        # Match file paths to assets
        matched_paths = self._match_file_paths_to_assets(file_paths, assets_for_upload)

        if not matched_paths:
            return

        # Create progress tracker only if progress is enabled
        progress_tracker = None
        if progress and task is not None:
            progress_tracker = AssetUploadProgressTracker(
                progress, task, len(matched_paths)
            )

        # Upload in parallel
        executor = ThreadPoolExecutor(max_workers=self._max_workers)
        try:
            futures = {
                executor.submit(
                    self._upload_single_asset_with_progress,
                    path,
                    asset.upload,
                    progress_tracker,
                    handler,
                ): path
                for path, asset in matched_paths
            }

            # Wait for completion with periodic cancellation checks
            remaining_futures = set(futures.keys())
            while remaining_futures:
                if handler.exit_now:
                    if progress_tracker:
                        progress_tracker.finish_cancelled()
                    for f in remaining_futures:
                        f.cancel()
                    break

                try:
                    # Check for completed futures with short timeout
                    for future in as_completed(remaining_futures, timeout=0.1):
                        remaining_futures.discard(future)
                        try:
                            future.result()
                        except (
                            OSError,
                            httpx.HTTPStatusError,
                            httpx.TimeoutException,
                            httpx.NetworkError,
                        ):
                            pass  # Error already logged by progress tracker
                        break  # Process one future at a time to check handler.exit_now
                except TimeoutError:
                    # No futures completed in timeout period, loop again to check exit_now
                    continue

        finally:
            # Ensure executor shuts down immediately without waiting
            executor.shutdown(wait=False, cancel_futures=True)

    def _match_file_paths_to_assets(
        self,
        file_paths: list[str],
        assets: list[responses.AssetForUpload],
    ) -> list[tuple[str, responses.AssetForUpload]]:
        """Match file paths to their corresponding asset upload information.

        The API returns asset upload info with filenames. This method matches
        those filenames back to the original file paths for uploading.

        Args:
            file_paths: List of original file paths
            assets: List of asset upload info from the API

        Returns:
            List of (file_path, asset_upload_info) tuples ready for upload

        """
        matched = []
        for asset in assets:
            for path in file_paths:
                if os.path.basename(path) == asset.metadata.filename:
                    matched.append((path, asset))
                    break
        return matched

    def _upload_single_asset_with_progress(
        self,
        file_path: str,
        signed_url_info: responses.Contents,
        progress_tracker: AssetUploadProgressTracker | None,
        handler: GracefulExit,
    ) -> bool:
        """Upload a single asset with progress tracking and retry logic.

        Args:
            file_path: Path to the file to upload
            signed_url_info: Signed URL and headers for upload
            progress_tracker: Optional progress tracker for UI updates
            handler: Graceful exit handler for cancellation

        Returns:
            True if upload successful, False if cancelled

        Raises:
            Exception: If upload fails after retries

        """
        if handler.exit_now:
            return False

        try:
            # Use RetryExecutor for consistent retry behavior with exponential backoff
            self._retry_executor.execute(
                operation=lambda: self._upload_single_asset(file_path, signed_url_info),
                operation_name=f"Upload {os.path.basename(file_path)}",
                max_retries=3,
                logger=self._logger,
                context_info={"file": os.path.basename(file_path)},
            )
            if progress_tracker:
                progress_tracker.update_success(1)
            return True
        except (
            OSError,
            httpx.HTTPStatusError,
            httpx.TimeoutException,
            httpx.NetworkError,
        ):
            if progress_tracker:
                progress_tracker.update_error(1)
            raise

    def _upload_single_asset(self, file_path: str, signed_url_info: responses.Contents):
        """Upload a file using signed URL.

        This is the actual upload operation without retry logic.
        Retries are handled by the caller using RetryExecutor.

        Args:
            file_path: Path to the file to upload
            signed_url_info: Signed URL and headers for upload

        Raises:
            httpx.HTTPStatusError: If upload fails
            OSError: If file cannot be read

        """
        with open(file_path, "rb") as f:
            response = self._get_upload_http_client().put(
                signed_url_info.url,
                content=f,
                headers=signed_url_info.headers,
            )
            response.raise_for_status()

    def _parse_asset_paths(self, paths: Path | str | Sequence[Path | str]) -> list[str]:
        """Parse and expand asset paths into a list of file paths.

        Handles various input formats:
        - Single file path -> returns list with one file
        - Directory path -> returns all supported files in directory (recursive)
        - List of paths -> processes each and combines results

        Args:
            paths: Single path, directory, or sequence of paths

        Returns:
            List of absolute file paths

        Raises:
            ViInvalidParameterError: If a path doesn't exist or isn't a file/directory

        """
        path_list = [paths] if isinstance(paths, (str, Path)) else list(paths)
        file_paths = []

        for path_item in path_list:
            path = Path(path_item).expanduser().resolve()

            if path.is_file():
                file_paths.append(str(path))
            elif path.is_dir():
                file_paths.extend(self._scan_directory(path))
            else:
                raise ViInvalidParameterError(
                    "paths",
                    f"Invalid path: {path_item}. Path must be a file or directory",
                )

        return file_paths

    def _scan_directory(self, directory: Path) -> list[str]:
        """Scan directory recursively for supported asset files.

        Searches the directory and all subdirectories for files with supported
        extensions (images, videos, etc.).

        Args:
            directory: Path to directory to scan

        Returns:
            List of absolute paths to supported files found

        """
        return [
            str(file_path)
            for file_path in directory.glob("**/*")
            if file_path.is_file()
            and file_path.suffix.lower() in consts.SUPPORTED_ASSET_FILE_EXTENSIONS
        ]

    def _generate_asset_file_spec(
        self, asset_path: Path | str
    ) -> AssetUploadFileSpec | None:
        """Generate complete file specification for a single asset.

        Analyzes the file to extract all required metadata:
        - File size and name
        - MIME type (from extension or file content)
        - CRC32C checksum (for integrity verification)
        - Asset kind (Image/Video/MedicalImage)

        Args:
            asset_path: Path to the asset file

        Returns:
            Complete file specification ready for upload, or None if the file
            should be skipped (e.g., MIME type validation fails)

        Raises:
            ValueError: If MIME type is valid but asset kind is unsupported

        """
        asset_path = Path(asset_path).expanduser().resolve()

        # Get basic file metadata
        size = os.stat(asset_path).st_size
        filename = asset_path.name
        ext = asset_path.suffix.lower()

        # Get expected MIME type from extension
        mime_from_ext = consts.ASSET_FILE_EXTENSION_TO_MIME_TYPE_MAP.get(ext)
        if not mime_from_ext:
            self._logger.warning(
                f"Skipping {asset_path}: Unknown file extension '{ext}'"
            )
            return None

        # Calculate CRC32C and detect MIME type in a single file pass (optimization)
        crc32c_value, mime_from_content = calculate_crc32c_and_detect_mime(asset_path)

        # Validate MIME type from file content
        if not mime_from_content:
            self._logger.warning(
                f"Skipping {asset_path}: Unable to detect MIME type from file content"
            )
            return None

        # Verify that extension-based MIME matches content-detected MIME
        mime_base_ext = mime_from_ext.split("/")[0]
        mime_base_content = mime_from_content.split("/")[0]

        if mime_base_ext != mime_base_content:
            self._logger.warning(
                f"Skipping {asset_path}: MIME type mismatch - "
                f"extension suggests '{mime_from_ext}' but content is '{mime_from_content}'"
            )
            return None

        # Determine asset kind and return spec
        kind = self._determine_asset_kind(mime_from_ext)

        return AssetUploadFileSpec(
            filename=filename,
            mime=mime_from_ext,
            size=size,
            crc32c=crc32c_value,
            kind=kind,
        )

    def _determine_asset_kind(self, mime_type: str) -> str:
        """Determine the asset kind from its MIME type.

        Maps MIME types to asset kinds:
        - image/* -> "Image"
        - video/* -> "Video"
        - application/dicom -> "MedicalImage"

        Args:
            mime_type: The MIME type string

        Returns:
            Asset kind string

        Raises:
            ValueError: If the MIME type is not supported

        """
        if mime_type.startswith("image/"):
            return "Image"
        if mime_type.startswith("video/"):
            return "Video"
        if mime_type == "application/dicom":
            return "MedicalImage"
        raise ValueError(f"Unsupported MIME type: {mime_type}")

    def get_asset_ingestion_session(
        self,
        dataset_id: str,
        asset_ingestion_session_id: str,
        asset_source_class: str = consts.DEFAULT_ASSET_SOURCE_CLASS,
        asset_source_provider: str = consts.DEFAULT_ASSET_SOURCE_PROVIDER,
        asset_source_id: str = consts.DEFAULT_ASSET_SOURCE_ID,
    ) -> responses.AssetIngestionSession:
        """Get an asset ingestion session by ID."""
        self._link_parser = AssetIngestionSessionLinkParser(
            self._auth.organization_id,
            dataset_id,
            asset_source_class,
            asset_source_provider,
            asset_source_id,
        )

        response = self._requester.get(
            self._link_parser(asset_ingestion_session_id),
            response_type=responses.AssetIngestionSession,
        )

        if not isinstance(response, responses.AssetIngestionSession):
            raise ValueError(f"Invalid response {response} with type {type(response)}")

        return response
