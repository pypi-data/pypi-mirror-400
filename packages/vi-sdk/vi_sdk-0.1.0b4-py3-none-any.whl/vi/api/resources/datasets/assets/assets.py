#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   assets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets module.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.assets import responses
from vi.api.resources.datasets.assets.downloader import AssetDownloader
from vi.api.resources.datasets.assets.links import AssetLinkParser
from vi.api.resources.datasets.assets.results import (
    AssetDownloadResult,
    AssetUploadResult,
)
from vi.api.resources.datasets.assets.types import (
    AssetGetParams,
    AssetListParams,
    AssetSortCriterion,
)
from vi.api.resources.datasets.assets.uploader import AssetUploader
from vi.api.resources.datasets.links import DatasetLinkParser
from vi.api.resources.datasets.responses import Dataset as DatasetResponse
from vi.api.resources.datasets.utils.helper import build_dataset_id
from vi.api.responses import Condition, ConditionStatus, DeletedResource, Pagination
from vi.api.types import PaginationParams
from vi.client.errors import ViOperationError
from vi.client.rest.resource import RESTResource
from vi.client.validation import (
    validate_directory_path,
    validate_id_param,
    validate_pagination_params,
    validate_sort_params,
)
from vi.consts import DEFAULT_ASSET_DIR
from vi.utils.graceful_exit import graceful_exit

DEFAULT_BATCH_SIZE = 1000


class Asset(RESTResource):
    """Asset resource for managing assets within datasets.

    This class provides methods to list, retrieve, upload, download, and delete
    assets (images, videos, documents) within datasets. Assets are the core media
    files that contain the data to be annotated and processed.

    Example:
        ```python
        import vi

        client = vi.Client()
        assets = client.assets

        # List assets in a dataset
        asset_list = assets.list(dataset_id="dataset_abc123")
        for asset in asset_list.items:
            print(
                f"Asset: {asset.filename} ({asset.metadata.width}x{asset.metadata.height})"
            )

        # Get a specific asset
        asset = assets.get(dataset_id="dataset_abc123", asset_id="asset_xyz789")
        print(f"Asset size: {asset.metadata.file_size} bytes")

        # Upload a new asset
        from pathlib import Path

        result = assets.upload(dataset_id="dataset_abc123", paths=Path("./image.jpg"))
        print(f"Upload session: {result.asset_ingestion_session_id}")
        ```

    Note:
        Assets are always associated with a specific dataset. All operations
        require a dataset_id parameter to specify which dataset to operate on.

    See Also:
        - [Asset Guide](../../guide/assets.md): Complete guide to asset management and uploads
        - `Dataset`: Parent dataset resource
        - `Annotation`: Related annotation resource

    """

    _uploader: AssetUploader | None = None
    _link_parser: AssetLinkParser | None = None

    def list(
        self,
        dataset_id: str,
        pagination: PaginationParams | dict = PaginationParams(),
        filter_criteria: str | dict | None = None,
        contents: bool | None = None,
        sort_by: AssetSortCriterion | dict | None = None,
        metadata_query: str | None = None,
        rule_query: str | None = None,
        strict_query: bool | None = None,
        page_after: bool | None = None,
    ) -> PaginatedResponse[responses.Asset]:
        """List assets in a dataset with advanced filtering and sorting.

        Retrieves a paginated list of assets within a dataset with support for
        filtering, sorting, and metadata queries. Supports automatic pagination
        for iterating through large asset collections.

        Args:
            dataset_id: The unique identifier of the dataset containing the assets.
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a PaginationParams object or dict. Defaults to first page.
            filter_criteria: Filter criteria to select specific assets. Can be a query string
                or dict with filter conditions. None means no filtering.
            contents: Whether to include asset content metadata (file info, dimensions).
                None uses server default. Set to True for detailed content info.
            sort_by: Sorting criteria for the results. Can be AssetSortCriterion object
                or dict with sort field and order. None uses server default sorting.
            metadata_query: Query string to filter assets by metadata fields.
                Supports field-based queries like 'camera_type:aerial'.
            rule_query: Query string to filter assets by rules or conditions.
            strict_query: Whether to use strict matching for queries. When True,
                only exact matches are included. Defaults to False for fuzzy matching.
            page_after: Whether to paginate after a specific cursor. Used internally
                for cursor-based pagination. None uses offset-based pagination.

        Returns:
            PaginatedResponse containing Asset objects with navigation support.
            Each Asset contains metadata, dimensions, and file information.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If dataset_id or filter parameters are invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # List all assets with default pagination
            assets = client.assets.list(dataset_id="dataset_abc123")
            for asset in assets.items:
                print(f"{asset.filename}: {asset.width}x{asset.height}")

            # List with filtering and sorting
            assets = client.assets.list(
                dataset_id="dataset_abc123",
                filter_criteria={"file_type": "image/jpeg"},
                sort_by={"field": "upload_time", "order": "desc"},
                pagination={"page_size": 50},
            )

            # List with metadata query
            assets = client.assets.list(
                dataset_id="dataset_abc123",
                metadata_query="camera_model:Canon",
                strict_query=True,
            )

            # Iterate through all assets across pages
            assets = client.assets.list("dataset_abc123")
            for asset in assets.all_items():
                print(f"Processing: {asset.filename}")
            ```

        Note:
            Large datasets may have thousands of assets. Use pagination and
            filtering to efficiently work with specific subsets. The contents
            parameter adds detailed file information but increases response size.

        See Also:
            - `get()`: Retrieve a specific asset
            - `AssetSortCriterion`: Sorting options
            - `PaginationParams`: Pagination configuration

        """
        validate_id_param(dataset_id, "dataset_id")

        self._link_parser = AssetLinkParser(self._auth.organization_id, dataset_id)

        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        if isinstance(sort_by, dict):
            validate_sort_params(**sort_by)
            sort_by = AssetSortCriterion(**sort_by)

        asset_params = AssetListParams(
            pagination=pagination,
            filter=filter_criteria,
            contents=contents,
            sort_by=sort_by,
            metadata_query=metadata_query,
            rule_query=rule_query,
            page_after=page_after,
            strict_query=strict_query,
        )

        response = self._requester.get(
            self._link_parser(),
            params=asset_params.to_query_params(),
            response_type=Pagination[responses.Asset],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={
                    "dataset_id": dataset_id,
                    "pagination": pagination,
                    "filter": filter_criteria,
                    "contents": contents,
                    "sort_by": sort_by,
                    "metadata_query": metadata_query,
                    "rule_query": rule_query,
                    "page_after": page_after,
                    "strict_query": strict_query,
                },
            )

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get(
        self, dataset_id: str, asset_id: str, contents: bool | None = None
    ) -> responses.Asset:
        """Get detailed information about a specific asset.

        Retrieves comprehensive information about an asset including metadata,
        dimensions, file information, and optionally detailed content analysis.

        Args:
            dataset_id: The unique identifier of the dataset containing the asset.
            asset_id: The unique identifier of the asset to retrieve.
            contents: Whether to include detailed content metadata such as file
                analysis, EXIF data, and processing status. None uses server default.
                Set to True for complete asset information.

        Returns:
            Asset object containing all available information about the asset
            including filename, dimensions, file size, upload time, and metadata.

        Raises:
            ViNotFoundError: If the dataset or asset doesn't exist.
            ViValidationError: If dataset_id or asset_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Get basic asset information
            asset = client.assets.get(
                dataset_id="dataset_abc123", asset_id="asset_xyz789"
            )
            print(f"Filename: {asset.filename}")
            print(f"Size: {asset.width}x{asset.height}")
            print(f"File size: {asset.file_size} bytes")

            # Get asset with detailed content information
            asset = client.assets.get(
                dataset_id="dataset_abc123", asset_id="asset_xyz789", contents=True
            )
            print(f"MIME type: {asset.mime_type}")
            print(f"Upload time: {asset.upload_time}")
            if hasattr(asset, "exif_data"):
                print(f"Camera: {asset.exif_data.get('camera_model')}")
            ```

        Note:
            Setting contents=True provides additional metadata but increases
            response time and size. Use only when detailed information is needed.

        See Also:
            - `list()`: List multiple assets
            - `download()`: Download the asset file
            - `delete()`: Delete the asset

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(asset_id, "asset_id")

        self._link_parser = AssetLinkParser(self._auth.organization_id, dataset_id)

        asset_params = AssetGetParams(contents=contents)

        response = self._requester.get(
            self._link_parser(asset_id),
            params=asset_params.to_query_params(),
            response_type=responses.Asset,
        )

        if isinstance(response, responses.Asset):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def delete(self, dataset_id: str, asset_id: str) -> DeletedResource:
        """Delete an asset by ID.

        Permanently removes an asset from the dataset including the file and all
        associated metadata. This operation cannot be undone. Any annotations
        associated with this asset will also be deleted.

        Args:
            dataset_id: The unique identifier of the dataset containing the asset.
            asset_id: The unique identifier of the asset to delete.

        Returns:
            DeletedResource object confirming the deletion with the asset ID
            and deletion status.

        Raises:
            ViNotFoundError: If the dataset or asset doesn't exist.
            ViValidationError: If dataset_id or asset_id format is invalid.
            ViPermissionError: If user lacks permission to delete the asset.
            ViOperationError: If the deletion fails or API returns unexpected response.

        Example:
            ```python
            # Delete a specific asset
            result = client.assets.delete(
                dataset_id="dataset_abc123", asset_id="asset_xyz789"
            )
            print(f"Deleted asset: {result.id}")

            # Safe deletion with error handling
            try:
                result = client.assets.delete(
                    dataset_id="dataset_abc123", asset_id="asset_xyz789"
                )
                print("Asset deleted successfully")
            except ViNotFoundError:
                print("Asset not found or already deleted")
            except ViPermissionError:
                print("Permission denied - cannot delete asset")
            ```

        Warning:
            This operation is permanent and cannot be undone. The asset file
            and all associated annotations will be permanently deleted from
            the platform.

        Note:
            Deleting an asset will also remove all annotations associated with
            that asset. Consider downloading important annotations before deletion.

        See Also:
            - `get()`: Verify asset exists before deletion
            - `bulk_delete()`: Delete multiple assets efficiently
            - [Asset Guide](../../guide/assets.md#deletion): Best practices for asset deletion

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(asset_id, "asset_id")

        self._link_parser = AssetLinkParser(self._auth.organization_id, dataset_id)

        response = self._requester.delete(self._link_parser(asset_id))

        if isinstance(response, dict) and response.get("data") == "":
            return DeletedResource(id=asset_id, deleted=True)

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def upload(
        self,
        dataset_id: str,
        paths: Path | str | Sequence[Path | str],
        failure_mode: str = "FailAfterOne",
        on_asset_overwritten: str = "RemoveLinkedResource",
        wait_until_done: bool = True,
        show_progress: bool = True,
    ) -> AssetUploadResult:
        """Upload assets to a dataset.

        Uploads one or more asset files (currently supportsimages) to a dataset.
        Supports uploading individual files, multiple files, or entire directories.
        The upload process includes automatic file validation, progress tracking,
        and metadata extraction. Large uploads are automatically split into batches
        and processed in parallel for optimal performance.

        Args:
            dataset_id: The unique identifier of the dataset to upload assets to.
            paths: Path(s) to upload. Can be:
                - Single file path (Path or str)
                - List of file paths (Sequence[Path | str])
                - Directory path (uploads all supported files in directory)
            failure_mode:
                How to handle failures ("FailAfterOne" or "FailAfterAll"), default is "FailAfterOne"
            on_asset_overwritten:
                Action when asset exists ("RemoveLinkedResource" or
                "KeepLinkedResource"), default is "RemoveLinkedResource"
            wait_until_done: Whether to wait for upload processing to complete
                before returning. If True, returns when all assets are processed.
                If False, returns immediately after upload starts. Defaults to True.
            show_progress: Whether to display progress bars during upload with file
                counts and status. Set to False for non-interactive environments.
                Defaults to True.

        Returns:
            AssetUploadResult: Simplified result wrapper with upload statistics.
            Use result.summary() for formatted output, access result.total_succeeded
            for counts, or access result.sessions for underlying session objects.

        Raises:
            FileNotFoundError: If specified files or directories don't exist.
            ViValidationError: If dataset_id is invalid or files are unsupported.
            ViUploadError: If upload fails due to network or server issues.
            ViPermissionError: If user lacks permission to upload to the dataset.

        Example:
            ```python
            from pathlib import Path

            # Upload a single image (simple)
            result = client.assets.upload(
                dataset_id="dataset_abc123", paths=Path("./image.jpg")
            )
            print(f"Uploaded: {result.total_succeeded} assets")
            print(result.summary())  # Rich formatted summary

            # Upload multiple files
            result = client.assets.upload(
                dataset_id="dataset_abc123",
                paths=[
                    Path("./image1.jpg"),
                    Path("./image2.png"),
                    Path("./video.mp4"),
                ],
            )

            # Upload entire directory
            result = client.assets.upload(
                dataset_id="dataset_abc123", paths=Path("./my_images/")
            )
            print(f"Success rate: {result.success_rate:.1f}%")

            # Upload without waiting (async)
            result = client.assets.upload(
                dataset_id="dataset_abc123",
                paths=Path("./large_dataset/"),
                wait_until_done=False,
            )
            print(f"Upload started: {result.session_ids[0]}")

            # Upload large dataset (automatically uses parallel batches)
            result = client.assets.upload(
                dataset_id="dataset_abc123", paths=Path("./50k_images/")
            )
            print(f"Processed in {len(result.sessions)} batches")
            print(result.summary())

            # Advanced: Access underlying sessions
            for session in result.sessions:
                print(f"Session {session.asset_ingestion_session_id}")
            ```

        Note:
            - Supported formats: JPEG, PNG, GIF, BMP, TIFF, MP4, AVI, MOV, PDF
            - Large files are automatically chunked for reliable upload
            - Metadata (EXIF, file info) is automatically extracted
            - Duplicate files are detected and skipped
            - Directory uploads are recursive and include subdirectories

        Warning:
            Large directory uploads may take significant time. Consider using
            wait_until_done=False for directories with many files and monitor
            progress separately.

        See Also:
            - `get_upload_session()`: Check upload status
            - `download()`: Download uploaded assets
            - [Asset Guide](../../guide/assets.md): Best practices and upload limits

        """
        validate_id_param(dataset_id, "dataset_id")

        if not self._uploader:
            self._uploader = AssetUploader(self._requester, self._auth)

        upload_responses = self._uploader.upload(
            dataset_id,
            paths,
            failure_mode,
            on_asset_overwritten,
            show_progress=show_progress,
        )

        if wait_until_done:
            completed_sessions = []
            for upload_response in upload_responses:
                completed_session = self.wait_until_done(
                    dataset_id, upload_response.asset_ingestion_session_id
                )
                completed_sessions.append(completed_session)
            return AssetUploadResult(completed_sessions)

        return AssetUploadResult(upload_responses)

    def download(
        self,
        dataset_id: str,
        save_dir: Path | str = DEFAULT_ASSET_DIR,
        overwrite: bool = False,
        show_progress: bool = True,
        http2: bool = False,
    ) -> AssetDownloadResult:
        """Download all assets from a dataset to local storage.

        Downloads all asset files (currently supports images) from a dataset to
        a local directory. The download process is optimized with batching and
        parallel downloads for efficiency. Files are organized in a structured
        directory layout.

        Args:
            dataset_id: The unique identifier of the dataset containing assets to download.
            save_dir: Directory where assets will be saved. Assets are saved in a
                subdirectory named with the dataset_id. Defaults to ~/.datature/vi/assets/.
            overwrite: Whether to overwrite existing files. If False, existing files
                are skipped. If True, files are re-downloaded. Defaults to False.
            show_progress: Whether to display download progress bar with file counts
                and transfer speeds. Set to False for non-interactive environments.
                Defaults to True.
            http2: Whether to enable HTTP/2 protocol for downloads. HTTP/2 can be faster
                but may have connection stability issues with some servers. If experiencing
                "Server disconnected" errors, try setting to False to use HTTP/1.1 instead.
                Defaults to False.

        Returns:
            AssetDownloadResult wrapper containing download information and helper
            methods for inspecting downloaded assets. Use `.summary()` to see
            download statistics or `.info()` for detailed information.

        Raises:
            ViNotFoundError: If the dataset doesn't exist or contains no assets.
            ViValidationError: If the dataset_id format is invalid.
            PermissionError: If unable to write to save_dir.
            OSError: If insufficient disk space for download.
            ViDownloadError: If download fails due to network issues.

        Example:
            ```python
            from pathlib import Path

            # Download all assets with default settings
            result = client.assets.download(dataset_id="dataset_abc123")
            print(f"Downloaded {result.count} assets to: {result.save_dir}")
            print(result.summary())

            # Download to custom directory with detailed info
            result = client.assets.download(
                dataset_id="dataset_abc123",
                save_dir=Path("./my_assets"),
                overwrite=True,
            )
            result.info()  # Show rich download information

            # Access download details
            print(f"Total size: {result.size_mb:.1f} MB")
            print(f"Files: {len(result.file_list)}")

            # Check downloaded files
            import os

            asset_dir = Path(result.save_dir)
            files = list(asset_dir.glob("*"))
            print(f"Downloaded {len(files)} files")
            ```

        Note:
            - Downloads are performed in batches for efficiency
            - Large datasets may take significant time to download
            - Files are saved with their original filenames
            - Directory structure: save_dir/dataset_id/filename.ext
            - Graceful cancellation supported with Ctrl+C

        Warning:
            Ensure sufficient disk space before downloading. Large datasets
            with thousands of high-resolution images may require several GB
            of storage space.

        See Also:
            - `list()`: List assets before downloading
            - `get()`: Get individual asset information
            - [Asset Guide](../../guide/assets.md): Best practices for large downloads

        """
        validate_id_param(dataset_id, "dataset_id")
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        save_dir = validate_directory_path(
            save_dir, "save_dir", must_exist=False, create_if_missing=True
        )

        dataset_link_parser = DatasetLinkParser(self._auth.organization_id)
        dataset_response: DatasetResponse = self._requester.get(
            dataset_link_parser(formatted_dataset_id),
            response_type=DatasetResponse,
        )

        total_asset_count = dataset_response.statistic.asset_total
        total_batch_count = total_asset_count // DEFAULT_BATCH_SIZE + 1

        downloader = AssetDownloader(
            overwrite=overwrite, show_progress=False, http2=http2
        )

        with graceful_exit("Asset download cancelled by user") as handler:
            downloader.download(
                dataset_id=dataset_id,
                url_batches=self._generate_download_url_batches(
                    dataset_id, DEFAULT_BATCH_SIZE
                ),
                save_dir=save_dir,
                handler=handler,
                total_assets=total_asset_count,
                total_batches=total_batch_count,
                show_progress=show_progress,
            )

        return AssetDownloadResult(
            dataset_id=dataset_id,
            count=total_asset_count,
            save_dir=str(save_dir / dataset_id),
        )

    def _generate_download_url_batches(
        self, dataset_id: str, batch_size: int = DEFAULT_BATCH_SIZE
    ):
        """Generate batches of download URLs using paginated response iterator.

        Args:
            dataset_id: ID of the dataset to download assets from.
            batch_size: Number of URLs per batch.

        Yields:
            list[str]: Batch of download URLs.

        """
        pagination = PaginationParams(page_size=batch_size)
        assets_response = self.list(dataset_id, pagination=pagination, contents="y")

        # Collect URLs in batches from all pages
        batch = []
        for asset in assets_response.all_items():
            if asset.contents and asset.contents.asset:
                batch.append(asset.contents.asset.url)

            # Yield batch when it reaches the desired size
            if len(batch) >= batch_size:
                yield batch
                batch = []

        # Yield any remaining URLs in the final batch
        if batch:
            yield batch

    def wait_until_done(
        self,
        dataset_id: str,
        asset_ingestion_session_id: str,
    ) -> responses.AssetIngestionSession:
        """Wait until an asset upload/ingestion session completes.

        Polls an asset ingestion session until it reaches a terminal state
        (completed, failed, or canceled). Uses intelligent backoff strategy
        to avoid excessive API calls while providing timely updates.

        Args:
            dataset_id: The unique identifier of the dataset containing the assets.
            asset_ingestion_session_id: The unique identifier of the ingestion
                session to monitor, typically returned from `upload()`.

        Returns:
            AssetIngestionSession object containing the final session status,
            processed asset count, and any errors encountered during ingestion.

        Raises:
            ViNotFoundError: If the dataset or ingestion session doesn't exist.
            ViValidationError: If dataset_id or session_id format is invalid.
            ViOperationError: If the ingestion session fails.
            ViTimeoutError: If the session doesn't complete within timeout period.

        Example:
            ```python
            # Upload assets without waiting
            session = client.assets.upload(
                dataset_id="dataset_abc123",
                paths=Path("./images/"),
                wait_until_done=False,
            )
            print(f"Upload started: {session.asset_ingestion_session_id}")

            # Wait for completion separately
            completed_session = client.assets.wait_until_done(
                dataset_id="dataset_abc123",
                asset_ingestion_session_id=session.asset_ingestion_session_id,
            )
            print(
                f"Upload completed: {completed_session.status.progressCount.succeeded} assets"
            )
            print(f"Conditions: {completed_session.status.conditions}")

            # Handle errors
            if completed_session.status.progressCount.errored > 0:
                print(
                    f"Failed uploads: {completed_session.status.progressCount.errored}"
                )
                for event in completed_session.status.events:
                    if hasattr(event, "files"):
                        print(f"  Error: {event.files}")
            ```

        Note:
            This method uses exponential backoff to poll the session status,
            starting with short intervals and gradually increasing to avoid
            excessive API calls. The default timeout is 30 minutes.

        Warning:
            For very large upload sessions (thousands of files), this method
            may block for extended periods. Consider running in a background
            thread for interactive applications.

        See Also:
            - `upload()`: Upload assets and optionally wait for completion
            - `get_upload_session()`: Check session status without waiting

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(asset_ingestion_session_id, "asset_ingestion_session_id")

        if not self._uploader:
            self._uploader = AssetUploader(self._requester, self._auth)

        return self._waiter.wait_until_done(
            lambda: self._uploader.get_asset_ingestion_session(
                dataset_id, asset_ingestion_session_id
            ),
            condition=Condition.FINISHED,
            status=ConditionStatus.REACHED,
        )

    def help(self) -> None:
        """Display helpful information about using the Asset resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on assets
            client.assets.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           Asset Resource - Quick Help                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List assets in a dataset:
    assets = client.assets.list(dataset_id="dataset_abc123")
    for asset in assets.items:
        print(asset.filename, asset.asset_id)

  Get a specific asset:
    asset = client.assets.get(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789"
    )
    asset.info()  # Show detailed information

  Upload assets:
    result = client.assets.upload(
        dataset_id="dataset_abc123",
        paths="./images/photo.jpg"
    )

  Upload multiple assets in a folder:
    result = client.assets.upload(
        dataset_id="dataset_abc123",
        paths="./images/"
    )

  Download assets:
    result = client.assets.download(
        dataset_id="dataset_abc123",
        save_dir="./downloads"
    )

  Delete an asset:
    client.assets.delete(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789"
    )

📖 AVAILABLE METHODS:

  • list(dataset_id, ...)           - List assets with filtering/sorting
  • get(dataset_id, asset_id)       - Get a specific asset
  • upload(dataset_id, paths, ...)  - Upload one or more assets
  • download(dataset_id, ...)       - Download assets to local storage
  • delete(dataset_id, asset_id)    - Delete a single asset

💡 TIPS:

  • Use list() with filters for large datasets
  • Upload supports both single files and batches
  • Check asset.info() for detailed asset information
  • All asset operations require a dataset_id
  • Use pagination for efficient listing of large asset collections

⚡ SUPPORTED FORMATS:

  Images:  JPEG, PNG, GIF, BMP, TIFF, WebP, HEIC, HEIF, AVIF, JPEG 2000, JP2

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-assets

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
