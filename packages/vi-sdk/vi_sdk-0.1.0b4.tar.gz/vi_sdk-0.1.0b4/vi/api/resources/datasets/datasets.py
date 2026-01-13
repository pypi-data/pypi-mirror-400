#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   datasets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK datasets module.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import msgspec
from rich.progress import SpinnerColumn, TimeElapsedColumn
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets import responses
from vi.api.resources.datasets.downloader import DatasetDownloader
from vi.api.resources.datasets.links import DatasetLinkParser
from vi.api.resources.datasets.results import DatasetDownloadResult
from vi.api.resources.datasets.types import (
    BulkAssetDeletionSession,
    BulkAssetDeletionSpec,
    DatasetExportFormat,
    DatasetExportSettings,
    DatasetExportSpec,
    DatasetListParams,
)
from vi.api.resources.datasets.utils.helper import build_dataset_id
from vi.api.responses import Condition, ConditionStatus, Pagination
from vi.api.types import PaginationParams
from vi.client.errors import ViOperationError
from vi.client.http.requester import Authentication, Requester
from vi.client.rest.resource import RESTResource
from vi.client.validation import (
    validate_directory_path,
    validate_id_param,
    validate_pagination_params,
)
from vi.consts import DEFAULT_ANNOTATION_EXPORT_DIR, DEFAULT_DATASET_EXPORT_DIR
from vi.utils.progress import ViProgress


class Dataset(RESTResource):
    """Dataset resource for managing datasets in the Datature Vi platform.

    This class provides methods to list, retrieve, create, export, download, and delete
    datasets. Assets and annotations are accessed through the client's flat structure
    (e.g., `client.assets` and `client.annotations`).

    Example:
        ```python
        import vi

        client = vi.Client()

        # List all datasets
        datasets = client.datasets.list()
        for dataset in datasets.items:
            print(f"Dataset: {dataset.name}")

        # Get a specific dataset
        dataset = client.datasets.get("dataset_abc123")
        print(f"Dataset has {dataset.statistic.asset_total} assets")
        ```

    See Also:
        - [Dataset Guide](../../guide/datasets.md) - Comprehensive guide to working with datasets
        - [Asset API](assets.md) - Managing assets within datasets
        - [Annotation API](annotations.md) - Managing annotations within datasets

    """

    _link_parser: DatasetLinkParser

    def __init__(self, auth: Authentication, requester: Requester):
        """Initialize the Dataset resource.

        Args:
            auth: Authentication instance containing credentials.
            requester: HTTP requester instance for making API calls.

        """
        super().__init__(auth, requester)
        self._link_parser = DatasetLinkParser(auth.organization_id)

    def list(
        self, pagination: PaginationParams | dict = PaginationParams()
    ) -> PaginatedResponse[responses.Dataset]:
        """List all datasets in the organization with pagination support.

        Retrieves a paginated list of all datasets accessible to the authenticated user
        within their organization. Supports automatic pagination for iterating through
        large numbers of datasets.

        Args:
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a `PaginationParams` object or a dict with pagination settings.
                Defaults to `PaginationParams()` (first page, default page size).

        Returns:
            PaginatedResponse containing a list of Dataset objects. The response
                supports iteration over all pages and individual items.

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViValidationError: If pagination parameters are invalid.

        Example:
            ```python
            # List all datasets with default pagination
            datasets = client.datasets.list()

            # Iterate over all datasets across all pages
            for dataset in datasets.all_items():
                print(f"{dataset.name}: {dataset.statistic.asset_total} assets")

            # Access first page items
            for dataset in datasets.items:
                print(dataset.name)

            # Custom pagination
            datasets = client.datasets.list(pagination={"page_size": 50, "page": 2})
            ```

        See Also:
            - `PaginationParams`: Pagination configuration options
            - `get()`: Retrieve a specific dataset by ID

        """
        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        dataset_params = DatasetListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(),
            params=dataset_params.to_query_params(),
            response_type=Pagination[responses.Dataset],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={"pagination": pagination},
            )

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get(self, dataset_id: str) -> responses.Dataset:
        """Get detailed information about a specific dataset.

        Retrieves comprehensive information about a dataset including its
        statistics, metadata, access settings, and configuration. This is
        useful for inspecting a dataset before performing operations like
        downloading, exporting, or adding assets.

        Args:
            dataset_id: The unique identifier of the dataset to retrieve.
                Can be found via `list()` or from the Datature Vi platform.

        Returns:
            Dataset object containing all dataset information including:
                - Basic info: name, description, dataset_id
                - Statistics: asset_total, annotation_total, file_size
                - Configuration: access settings, labels, metadata schema
                - Timestamps: create_time, update_time

        Raises:
            ViNotFoundError: If the dataset doesn't exist or is not accessible.
            ViValidationError: If the dataset_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Get a specific dataset
            dataset = client.datasets.get(dataset_id="dataset_abc123")

            print(f"Dataset: {dataset.name}")
            print(f"Description: {dataset.description}")
            print(f"Total assets: {dataset.statistic.asset_total}")
            print(f"Total annotations: {dataset.statistic.annotation_total}")
            print(f"Created: {dataset.metadata.time_created}")

            # Check dataset before downloading
            dataset = client.datasets.get("dataset_abc123")
            if dataset.statistic.asset_total > 0:
                result = client.datasets.download(dataset_id="dataset_abc123")
                print(f"Downloaded {dataset.statistic.asset_total} assets")

            # Use dataset info for display
            dataset = client.datasets.get("dataset_abc123")
            dataset.info()  # Rich formatted output
            ```

        Note:
            This method returns the full dataset object with all metadata.
            For listing multiple datasets with basic info, use `list()` instead.

        See Also:
            - `list()`: List all datasets in the organization
            - `download()`: Download a dataset
            - `delete()`: Delete a dataset

        """
        validate_id_param(dataset_id, "dataset_id")
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.get(
            self._link_parser(formatted_dataset_id),
            response_type=responses.Dataset,
        )

        if isinstance(response, responses.Dataset):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get_deletion_operation(self, dataset_id: str) -> responses.DeletedDataset:
        """Get the status of a dataset deletion operation.

        Retrieves information about an ongoing or completed dataset deletion
        operation. Useful for monitoring the progress of asynchronous deletions.

        Args:
            dataset_id: The unique identifier of the dataset whose deletion
                operation status to retrieve.

        Returns:
            DeletedDataset object containing deletion status, progress, and
                metadata about the deletion operation.

        Raises:
            ViNotFoundError: If the dataset or deletion operation doesn't exist.
            ViValidationError: If the dataset_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Check deletion status
            deletion_status = client.datasets.get_deletion_operation("dataset_abc123")
            print(f"Status: {deletion_status.status}")
            print(f"Progress: {deletion_status.progress}%")
            ```

        See Also:
            - `delete()`: Delete a dataset
            - `wait_until_done()`: Wait for deletion to complete

        """
        validate_id_param(dataset_id, "dataset_id")
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.get(
            self._link_parser(f"{formatted_dataset_id}/deleteOperation"),
            response_type=responses.DeletedDataset,
        )

        if isinstance(response, responses.DeletedDataset):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def delete(self, dataset_id: str) -> responses.DeletedDataset:
        """Delete a dataset by ID.

        Permanently deletes the specified dataset including all its assets,
        annotations, and metadata. This operation is asynchronous and may take
        time for large datasets. Use `wait_until_done()` to monitor progress.

        Args:
            dataset_id: The unique identifier of the dataset to delete.

        Returns:
            DeletedDataset object containing deletion confirmation, operation ID,
                and initial status. Use this to monitor deletion progress.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If the dataset_id format is invalid.
            ViPermissionError: If user lacks permission to delete the dataset.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Delete a dataset
            result = client.datasets.delete("dataset_abc123")
            print(f"Deletion started: {result.delete_operation_id}")

            # Delete and wait for completion
            result = client.datasets.delete("dataset_abc123")
            final_result = client.datasets.wait_until_done(
                get_method=client.datasets.get_deletion_operation,
                dataset_id="dataset_abc123",
                operation_id=result.delete_operation_id,
            )
            print("Dataset deleted successfully")
            ```

        Warning:
            This operation is permanent and cannot be undone. All data
            associated with the dataset will be permanently deleted,
            including all assets, annotations, and project metadata.

        Note:
            For large datasets, deletion may take several minutes. The
            operation runs asynchronously and returns immediately. Use
            `get_deletion_operation()` to check progress.

        See Also:
            - `get_deletion_operation()`: Check deletion status
            - `wait_until_done()`: Wait for deletion to complete
            - [Dataset Guide](../../guide/datasets.md): Dataset management best practices

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.delete(
            self._link_parser(formatted_dataset_id),
            response_type=responses.DeletedDataset,
        )

        if isinstance(response, responses.DeletedDataset):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get_bulk_asset_deletion_session(
        self, dataset_id: str, delete_many_assets_session_id: str
    ) -> responses.BulkAssetDeletionSession:
        """Get the status of a bulk asset deletion session.

        Retrieves information about an ongoing or completed bulk asset deletion
        operation within a dataset. Useful for monitoring the progress of
        asynchronous bulk deletions.

        Args:
            dataset_id: The unique identifier of the dataset.
            delete_many_assets_session_id: The unique identifier of the bulk
                deletion session to retrieve.

        Returns:
            BulkAssetDeletionSession object containing deletion status, progress,
                number of assets deleted, and any errors encountered.

        Raises:
            ViNotFoundError: If the dataset or deletion session doesn't exist.
            ViValidationError: If the dataset_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Check bulk deletion status
            session = client.datasets.get_bulk_asset_deletion_session(
                dataset_id="dataset_abc123",
                delete_many_assets_session_id="session_xyz789",
            )
            print(f"Status: {session.status}")
            print(f"Assets deleted: {session.deleted_count}")
            print(f"Progress: {session.progress}%")
            ```

        See Also:
            - `bulk_delete_assets()`: Initiate bulk asset deletion
            - `wait_until_done()`: Wait for deletion to complete

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.get(
            self._link_parser(
                f"{formatted_dataset_id}/deleteManyAssetsSessions/{delete_many_assets_session_id}"
            ),
            response_type=responses.BulkAssetDeletionSession,
        )

        if isinstance(response, responses.BulkAssetDeletionSession):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def bulk_delete_assets(
        self,
        dataset_id: str,
        filter_criteria: str | dict | None = None,
        metadata_query: str | None = None,
        rule_query: str | None = None,
        strict_query: bool | None = None,
    ) -> responses.BulkAssetDeletionSession:
        """Bulk delete assets in a dataset based on filter criteria.

        Initiates an asynchronous operation to delete multiple assets matching
        the specified filter criteria. This is more efficient than deleting assets
        individually and automatically handles pagination. The operation runs in
        the background and returns immediately.

        Args:
            dataset_id: The unique identifier of the dataset containing the assets.
            filter_criteria: Filter criteria to select assets for deletion. Can be a
                query string or dict. If None, no filter is applied (use with caution).
            metadata_query: Query string to filter assets by metadata fields.
                Supports field-based queries like 'camera_type:aerial'.
            rule_query: Query string to filter assets by rules or conditions.
            strict_query: Whether to use strict matching for queries. When True,
                only exact matches are included. Defaults to False.

        Returns:
            BulkAssetDeletionSession object representing the deletion operation.
                Use this to monitor progress with `wait_until_done()`.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If the dataset_id or filter format is invalid.
            ViPermissionError: If user lacks permission to delete assets.
            ViOperationError: If the operation fails to start.

        Example:
            ```python
            # Delete all assets matching a filter
            session = client.datasets.bulk_delete_assets(
                dataset_id="dataset_abc123", filter_criteria={"tag": "to_delete"}
            )
            print(f"Deletion session: {session.session_id}")
            print(f"Status: {session.status}")

            # Delete assets by metadata query
            session = client.datasets.bulk_delete_assets(
                dataset_id="dataset_abc123",
                metadata_query="quality:low",
                strict_query=True,
            )

            # Delete and wait for completion
            session = client.datasets.bulk_delete_assets(
                dataset_id="dataset_abc123",
                filter_criteria={"status": "processing_failed"},
            )
            # Session is already completed via wait_until_done()
            print(f"Deleted {session.deleted_count} assets")
            ```

        Warning:
            Be careful with filter criteria - incorrect filters may delete
            unintended assets. Always verify the filter returns the expected
            assets before performing bulk deletion.

        Note:
            This method automatically waits for the deletion to complete by
            calling `wait_until_done()` internally. For very large deletions,
            this may take several minutes. The deletion operation is atomic
            and cannot be partially undone.

        See Also:
            - `get_bulk_asset_deletion_session()`: Check deletion status
            - `wait_until_done()`: Wait for async operations
            - [Asset Guide](../../guide/assets.md): Asset management best practices

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        bulk_delete_params = BulkAssetDeletionSession(
            spec=BulkAssetDeletionSpec(
                filter=filter_criteria,
                metadata_query=metadata_query,
                rule_query=rule_query,
                strict_query=strict_query,
            ),
        )

        session_response: responses.BulkAssetDeletionSession = self._requester.post(
            self._link_parser(f"{formatted_dataset_id}/deleteManyAssetsSessions"),
            json_data=msgspec.to_builtins(bulk_delete_params, str_keys=True),
            response_type=responses.BulkAssetDeletionSession,
        )

        bulk_delete_response = self.wait_until_done(
            self.get_bulk_asset_deletion_session,
            dataset_id,
            session_response.delete_many_assets_session_id,
        )

        return bulk_delete_response

    def create_export(
        self,
        dataset_id: str,
        export_settings: DatasetExportSettings | dict = DatasetExportSettings(),
    ) -> responses.DatasetExport:
        """Create a dataset export operation.

        Initiates an asynchronous export operation to package dataset assets and
        annotations in a specified format. The export operation runs in the
        background and can be monitored using `get_export()` or downloaded when
        ready using `download()`.

        Args:
            dataset_id: The unique identifier of the dataset to export.
            export_settings: Configuration for the export including format, split,
                and annotation settings. Can be a DatasetExportSettings object or
                dict. Defaults to DatasetExportSettings() with default values.

        Returns:
            DatasetExport object containing the export operation ID, status, and
                metadata. Use this to monitor progress and download when ready.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If the dataset_id or export_settings are invalid.
            ViPermissionError: If user lacks permission to export the dataset.
            ViOperationError: If the export operation fails to start.

        Example:
            ```python
            from vi.api.resources.datasets.types import (
                DatasetExportSettings,
                DatasetExportFormat,
            )

            # Create export with default settings
            export = client.datasets.create_export(dataset_id="dataset_abc123")
            print(f"Export ID: {export.dataset_export_id}")

            # Create export with custom settings
            export = client.datasets.create_export(
                dataset_id="dataset_abc123",
                export_settings=DatasetExportSettings(
                    format=DatasetExportFormat.VI_JSONL,
                    options=DatasetExportOptions(normalized=True, split_ratio=0.8),
                ),
            )

            # Create export using dict
            export = client.datasets.create_export(
                dataset_id="dataset_abc123",
                export_settings={"format": "VI_JSONL"},
            )
            ```

        Note:
            Export operations are asynchronous and may take several minutes for
            large datasets. Use `get_export()` to check status or `download()`
            to download when ready (which handles waiting automatically).

        See Also:
            - `get_export()`: Check export status
            - `list_exports()`: List all exports for a dataset
            - `download()`: Download completed export
            - `DatasetExportSettings`: Export configuration options

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        if isinstance(export_settings, DatasetExportSettings):
            spec = DatasetExportSpec(spec=export_settings)
        else:
            spec = DatasetExportSpec(spec=DatasetExportSettings(**export_settings))

        spec_dict = msgspec.to_builtins(spec, str_keys=True)

        with ViProgress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Creating dataset export...")

            response = self._requester.post(
                self._link_parser(f"{formatted_dataset_id}/datasetExports"),
                json_data=spec_dict,
                response_type=responses.DatasetExport,
            )
            progress.update(task, description="Export created!")

        if isinstance(response, responses.DatasetExport):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get_export(
        self, dataset_id: str, dataset_export_id: str
    ) -> responses.DatasetExport:
        """Get the status of a dataset export operation.

        Retrieves information about a specific dataset export operation including
        its current status, progress, and download URL when ready.

        Args:
            dataset_id: The unique identifier of the dataset.
            dataset_export_id: The unique identifier of the export operation.

        Returns:
            DatasetExport object containing export status, progress, format,
                and download URL when the export is ready.

        Raises:
            ViNotFoundError: If the dataset or export operation doesn't exist.
            ViValidationError: If the dataset_id or dataset_export_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Check export status
            export = client.datasets.get_export(
                dataset_id="dataset_abc123", dataset_export_id="export_xyz789"
            )
            print(f"Status: {export.status}")
            print(f"Progress: {export.progress}%")

            # Wait until export is ready
            import time

            while export.status != "completed":
                time.sleep(5)
                export = client.datasets.get_export(
                    dataset_id="dataset_abc123", dataset_export_id="export_xyz789"
                )
            print(f"Download URL: {export.download_url}")
            ```

        Note:
            Export status values typically include: "pending", "processing",
            "completed", or "failed". Check the status field to determine
            if the export is ready for download.

        See Also:
            - `create_export()`: Create a new export operation
            - `list_exports()`: List all exports
            - `download()`: Download completed export

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.get(
            self._link_parser(
                f"{formatted_dataset_id}/datasetExports/{dataset_export_id}"
            ),
            response_type=responses.DatasetExport,
        )

        if isinstance(response, responses.DatasetExport):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def list_exports(self, dataset_id: str) -> Pagination[responses.DatasetExport]:
        """List all export operations for a dataset.

        Retrieves a list of all export operations (past and present) for the
        specified dataset, including their status, format, and creation time.

        Args:
            dataset_id: The unique identifier of the dataset.

        Returns:
            Pagination object containing a list of DatasetExport objects.
                Each object represents an export operation with its status and metadata.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If the dataset_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # List all exports for a dataset
            exports = client.datasets.list_exports(dataset_id="dataset_abc123")
            for export in exports.items:
                print(f"Export {export.dataset_export_id}: {export.status}")
                print(f"  Format: {export.format}")
                print(f"  Created: {export.create_time}")

            # Find the most recent completed export
            exports = client.datasets.list_exports("dataset_abc123")
            completed = [e for e in exports.items if e.status == "completed"]
            if completed:
                latest = max(completed, key=lambda e: e.create_time)
                print(f"Latest export: {latest.dataset_export_id}")
            ```

        Note:
            Export operations are retained for a limited time (typically 7 days)
            before being automatically cleaned up. Download exports promptly to
            avoid expiration.

        See Also:
            - `create_export()`: Create a new export
            - `get_export()`: Get a specific export
            - `download()`: Download an export

        """
        formatted_dataset_id = build_dataset_id(self._auth.organization_id, dataset_id)

        response = self._requester.get(
            self._link_parser(f"{formatted_dataset_id}/datasetExports"),
            response_type=Pagination[responses.DatasetExport],
        )

        if isinstance(response, Pagination):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def download(
        self,
        dataset_id: str,
        dataset_export_id: str | None = None,
        annotations_only: bool = False,
        export_settings: DatasetExportSettings | dict = DatasetExportSettings(),
        save_dir: Path | str = DEFAULT_DATASET_EXPORT_DIR,
        overwrite: bool = False,
        show_progress: bool = True,
    ) -> DatasetDownloadResult:
        """Download a dataset with assets and annotations to local storage.

        Downloads a complete dataset including images, videos, and annotations in
        the specified format. Optionally downloads only annotations without assets.
        If no export ID is provided, creates a new export automatically. This method
        handles the full workflow: export creation, waiting for completion, and download.

        Args:
            dataset_id: The unique identifier of the dataset to download.
            dataset_export_id: The ID of an existing export operation. If None,
                creates a new export automatically. Defaults to None.
            annotations_only: If True, downloads only annotations without assets,
                significantly reducing download size and time. Defaults to False.
            export_settings: Configuration for export format and options. Only used
                if dataset_export_id is None. Defaults to DatasetExportSettings().
            save_dir: Directory where the dataset will be saved. Created if it
                doesn't exist. Defaults to ~/.datature/vi/dataset_exports/.
            overwrite: Whether to overwrite existing files in save_dir.
                Defaults to False.
            show_progress: Whether to display download progress bar. Set to False
                for non-interactive environments. Defaults to True.

        Returns:
            DatasetDownloadResult wrapper containing download information and helper
            methods. Use `.summary()` to see download statistics or `.info()` for
            detailed information about the downloaded dataset structure.

        Raises:
            ViNotFoundError: If the dataset or export doesn't exist.
            ViValidationError: If parameters are invalid.
            ViOperationError: If export creation or download fails.
            PermissionError: If unable to write to save_dir.
            OSError: If insufficient disk space.

        Example:
            ```python
            from pathlib import Path

            # Download complete dataset with default settings
            result = client.datasets.download(dataset_id="dataset_abc123")
            print(result.summary())

            # Access download details
            print(f"Dataset saved to: {result.save_dir}")
            print(f"Total size: {result.size_mb:.1f} MB")
            print(f"Splits: {', '.join(result.splits)}")

            # Download only annotations
            result = client.datasets.download(
                dataset_id="dataset_abc123",
                annotations_only=True,
                save_dir=Path("./annotations"),
            )

            # Download using existing export
            result = client.datasets.download(
                dataset_id="dataset_abc123",
                dataset_export_id="export_xyz789",
                save_dir=Path("./my_dataset"),
                overwrite=True,
            )

            # Download in JSONL format
            from vi.api.resources.datasets.types import DatasetExportFormat

            result = client.datasets.download(
                dataset_id="dataset_abc123",
                export_settings={"format": DatasetExportFormat.VI_JSONL},
                save_dir=Path("./jsonl_dataset"),
            )
            ```

        Note:
            - For large datasets, download may take several minutes.
            - The method automatically waits for export completion if needed.
            - Downloaded files are organized in a standardized directory structure.
            - Annotations-only downloads are much faster for large datasets.

        Warning:
            Ensure sufficient disk space before downloading large datasets.
            A dataset with 10,000 images may require 10-50GB of storage.

        See Also:
            - `create_export()`: Create export manually
            - `get_export()`: Check export status
            - `DatasetExportSettings`: Export configuration options
            - [Dataset Guide](../../guide/datasets.md#downloading): Best practices

        """
        # Validate parameters
        validate_id_param(dataset_id, "dataset_id")
        if dataset_export_id is not None:
            validate_id_param(dataset_export_id, "dataset_export_id")
        save_dir = validate_directory_path(
            save_dir, "save_dir", must_exist=False, create_if_missing=True
        )
        if annotations_only:
            if export_settings.format == DatasetExportFormat.VI_FULL:
                export_settings.format = DatasetExportFormat.VI_JSONL

            if save_dir == DEFAULT_DATASET_EXPORT_DIR:
                save_dir = DEFAULT_ANNOTATION_EXPORT_DIR

        if not dataset_export_id:
            dataset_export = self.create_export(
                dataset_id, export_settings=export_settings
            )

            dataset_export_id = dataset_export.dataset_export_id

        completed_export = self.wait_until_done(
            self.get_export, dataset_id, dataset_export_id
        )

        if completed_export.status.download_url is None:
            raise ViOperationError(
                "The dataset download URL is not available. The export may have failed.",
                suggestion=(
                    "Check the export status and try again, or "
                    "contact support at developers@datature.io if the issue persists"
                ),
            )

        downloader = DatasetDownloader(show_progress=show_progress, overwrite=overwrite)
        downloaded_dataset = downloader.download(
            organization_id=completed_export.organization_id,
            dataset_id=dataset_id,
            download_url=completed_export.status.download_url.url,
            save_dir=save_dir,
        )
        return DatasetDownloadResult(
            dataset_id=downloaded_dataset.dataset_id,
            save_dir=downloaded_dataset.save_dir,
        )

    def wait_until_done(
        self, callback_func: Callable[..., Any], *args: Any
    ) -> responses.DatasetExport:
        """Wait until an asynchronous operation completes.

        Polls an asynchronous operation (such as export, deletion, or processing)
        until it reaches a terminal state (completed, failed, or canceled). Uses
        intelligent backoff strategy to avoid excessive API calls.

        Args:
            callback_func: Function to call repeatedly to check operation status.
                Should return an object with a `status` field indicating progress.
            *args: Arguments to pass to callback_func on each call.

        Returns:
            The final response object from callback_func when the operation
                completes successfully.

        Raises:
            ViOperationError: If the operation fails or times out.
            ViTimeoutError: If operation doesn't complete within the timeout period.

        Example:
            ```python
            # Wait for export to complete
            export = client.datasets.create_export("dataset_abc123")
            completed = client.datasets.wait_until_done(
                client.datasets.get_export,
                "dataset_abc123",
                export.dataset_export_id,
            )
            print(f"Export completed: {completed.download_url}")

            # Wait for deletion to complete
            deletion = client.datasets.delete("dataset_abc123")
            result = client.datasets.wait_until_done(
                client.datasets.get_deletion_operation, "dataset_abc123"
            )
            print("Dataset deleted successfully")

            # Wait for bulk asset deletion
            session = client.datasets.bulk_delete_assets(
                dataset_id="dataset_abc123", filter_criteria={"tag": "to_delete"}
            )
            # Note: bulk_delete_assets already calls wait_until_done internally
            ```

        Note:
            This method uses exponential backoff to poll the operation status,
            starting with short intervals and gradually increasing to avoid
            excessive API calls. The default timeout is 30 minutes.

        Warning:
            For long-running operations, this method will block until completion.
            Consider running in a background thread for interactive applications.

        See Also:
            - `create_export()`: Create an export operation
            - `get_export()`: Check export status
            - `delete()`: Delete a dataset

        """
        return self._waiter.wait_until_done(
            lambda: callback_func(*args),
            condition=Condition.ALL,
            status=ConditionStatus.REACHED,
        )

    def help(self) -> None:
        """Display helpful information about using the Dataset resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on datasets
            client.datasets.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          Dataset Resource - Quick Help                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List all datasets:
    for dataset in client.datasets:
        print(dataset.name, dataset.dataset_id)

  Get a specific dataset:
    dataset = client.datasets.get("dataset_abc123")
    print(f"Assets: {dataset.statistic.asset_total}")

  Download a dataset:
    result = client.datasets.download(
        dataset_id="dataset_abc123",
        save_dir="./data"
    )

  Create a dataset export:
    export = client.datasets.create_export(
        dataset_id="dataset_abc123",
        export_settings={"format": "VI_JSONL"}
    )

📖 AVAILABLE METHODS:

  • list(pagination=...)            - List all datasets with pagination
  • get(dataset_id)                 - Get a specific dataset by ID
  • delete(dataset_id)              - Delete a dataset (permanent!)
  • download(dataset_id, ...)       - Download complete dataset with assets
  • create_export(dataset_id, ...)  - Create a dataset export
  • get_export(dataset_id, ...)     - Get export status
  • list_exports(dataset_id)        - List all exports for a dataset
  • bulk_delete_assets(...)         - Delete multiple assets at once

💡 TIPS:

  • Use natural iteration: `for dataset in client.datasets:`
  • Check resource info: `dataset.info()` for detailed inspection
  • All IDs can be found via list() methods
  • Use pagination for large result sets
  • Downloads are cached by default (use overwrite=True to re-download)

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-datasets

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact developers@datature.io
"""
        print(help_text)
