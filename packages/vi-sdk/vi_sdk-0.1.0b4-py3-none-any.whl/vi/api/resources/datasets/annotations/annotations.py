#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   annotations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations module.
"""

from collections.abc import Sequence
from pathlib import Path

from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.annotations import responses
from vi.api.resources.datasets.annotations.links import AnnotationLinkParser
from vi.api.resources.datasets.annotations.results import AnnotationUploadResult
from vi.api.resources.datasets.annotations.types import AnnotationListParams
from vi.api.resources.datasets.annotations.uploader import AnnotationUploader
from vi.api.responses import Condition, ConditionStatus, DeletedResource, Pagination
from vi.api.types import PaginationParams
from vi.client.errors import ViOperationError
from vi.client.rest.resource import RESTResource
from vi.client.validation import validate_id_param, validate_pagination_params


class Annotation(RESTResource):
    """Annotation resource for managing annotations within datasets.

    This class provides methods to list, retrieve, upload, and delete annotations
    associated with assets in datasets. Annotations contain labeling information
    such as bounding boxes, polygons, classifications, and metadata.

    Example:
        ```python
        import vi

        client = vi.Client()
        annotations = client.annotations

        # List annotations in a dataset
        annotation_list = annotations.list(
            dataset_id="dataset_abc123", asset_id="asset_xyz789"
        )
        for annotation in annotation_list.items:
            print(f"Annotation: {annotation.id} for asset {annotation.asset_id}")

        # Get a specific annotation
        annotation = annotations.get(
            dataset_id="dataset_abc123",
            asset_id="asset_xyz789",
            annotation_id="annotation_xyz789",
        )
        print(f"Annotation type: {annotation.type}")

        # Upload annotations from file
        from pathlib import Path

        result = annotations.upload(
            dataset_id="dataset_abc123", paths=Path("./annotations.json")
        )
        print(f"Upload session: {result.session_id}")
        ```

    Note:
        Annotations are always associated with specific assets within a dataset.
        All fetching operations require a dataset_id parameter and an asset_id parameter
        to specify which dataset and asset to operate on.

    See Also:
        - [Annotation Guide](../../guide/annotations.md): Complete guide to annotation management and uploads
        - `Asset`: Related asset resource
        - `Dataset`: Parent dataset resource

    """

    _uploader: AnnotationUploader | None = None
    _link_parser: AnnotationLinkParser | None = None

    def list(
        self,
        dataset_id: str,
        asset_id: str,
        pagination: PaginationParams | dict = PaginationParams(),
    ) -> PaginatedResponse[responses.Annotation]:
        """List all annotations for a specific asset.

        Retrieves a paginated list of all annotations associated with a specific
        asset within a dataset. Each annotation contains labeling information
        including bounding boxes, polygons, classifications, and metadata.

        Args:
            dataset_id: The unique identifier of the dataset containing the annotations.
            asset_id: The unique identifier of the asset containing the annotations.
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a `PaginationParams` object or a dict with pagination settings.
                Defaults to `PaginationParams()` (first page, default page size).

        Returns:
            PaginatedResponse containing Annotation objects with navigation support.
            Each Annotation contains the annotation data, asset association, and metadata.

        Raises:
            ViNotFoundError: If the dataset doesn't exist.
            ViValidationError: If the dataset_id format is invalid or pagination
                parameters are invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # List all annotations for a specific asset with default pagination
            annotations = client.annotations.list(
                dataset_id="dataset_abc123", asset_id="asset_xyz789"
            )

            # Iterate through annotations
            for annotation in annotations.items:
                print(f"Annotation {annotation.annotation_id}:")
                print(f"  Asset: {annotation.asset_id}")
                print(f"  Tag: {annotation.spec.tag}")
                print(f"  Bound type: {annotation.spec.bound_type}")

            # Iterate through all pages
            for annotation in annotations.all_items():
                print(f"Processing annotation: {annotation.annotation_id}")

            # Custom pagination
            annotations = client.annotations.list(
                dataset_id="dataset_abc123",
                asset_id="asset_xyz789",
                pagination={"page_size": 50, "page": 2},
            )

            # Get annotation count
            total_annotations = len(list(annotations.all_items()))
            print(f"Total annotations: {total_annotations}")
            ```

        Note:
            Large datasets may contain thousands of annotations. The response
            is paginated to handle large result sets efficiently. Use the
            pagination methods to iterate through all annotations.

        See Also:
            - `get()`: Retrieve a specific annotation
            - `upload()`: Upload new annotations
            - `PaginatedResponse`: Pagination utilities

        """
        validate_id_param(dataset_id, "dataset_id")

        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        self._link_parser = AnnotationLinkParser(
            self._auth.organization_id, dataset_id, asset_id
        )

        annotation_params = AnnotationListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(),
            params=annotation_params.to_query_params(),
            response_type=Pagination[responses.Annotation],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={
                    "dataset_id": dataset_id,
                    "asset_id": asset_id,
                    "pagination": pagination,
                },
            )

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get(
        self, dataset_id: str, asset_id: str, annotation_id: str
    ) -> responses.Annotation:
        """Get detailed information about a specific annotation.

        Retrieves comprehensive information about an annotation including its
        geometry, labels, metadata, and associated asset information.

        Args:
            dataset_id: The unique identifier of the dataset containing the annotation.
            asset_id: The unique identifier of the asset containing the annotation.
            annotation_id: The unique identifier of the annotation to retrieve.

        Returns:
            Annotation object containing all annotation data including geometry,
            labels, confidence scores, metadata, and asset association.

        Raises:
            ViNotFoundError: If the dataset or annotation doesn't exist.
            ViValidationError: If dataset_id or annotation_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Get a specific annotation
            annotation = client.annotations.get(
                dataset_id="dataset_abc123",
                asset_id="asset_xyz789",
                annotation_id="annotation_xyz789",
            )

            print(f"Annotation ID: {annotation.id}")
            print(f"Associated Asset: {annotation.asset_id}")
            print(f"Type: {annotation.type}")
            print(f"Labels: {annotation.labels}")

            # Access geometry information
            if hasattr(annotation, "geometry"):
                print(f"Geometry: {annotation.geometry}")

            # Access confidence scores
            if hasattr(annotation, "confidence"):
                print(f"Confidence: {annotation.confidence}")

            # Access metadata
            if hasattr(annotation, "metadata"):
                print(f"Metadata: {annotation.metadata}")
            ```

        Note:
            The annotation object structure varies depending on the annotation
            type (bounding box, polygon, classification, etc.). Check the
            annotation type to understand available fields.

        See Also:
            - `list()`: List all annotations in a dataset
            - `delete()`: Delete an annotation
            - `upload()`: Upload new annotations

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(annotation_id, "annotation_id")

        self._link_parser = AnnotationLinkParser(
            self._auth.organization_id, dataset_id, asset_id
        )

        response = self._requester.get(
            self._link_parser(annotation_id),
            response_type=responses.Annotation,
        )

        if isinstance(response, responses.Annotation):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def delete(
        self, dataset_id: str, asset_id: str, annotation_id: str
    ) -> DeletedResource:
        """Delete an annotation by ID.

        Permanently removes an annotation from the dataset. This operation cannot
        be undone. The annotation data including geometry, labels, and metadata
        will be permanently deleted.

        Args:
            dataset_id: The unique identifier of the dataset containing the annotation.
            asset_id: The unique identifier of the asset containing the annotation.
            annotation_id: The unique identifier of the annotation to delete.

        Returns:
            DeletedResource object confirming the deletion with the annotation ID
            and deletion status.

        Raises:
            ViNotFoundError: If the dataset or annotation doesn't exist.
            ViValidationError: If dataset_id or annotation_id format is invalid.
            ViPermissionError: If user lacks permission to delete the annotation.
            ViOperationError: If the deletion fails or API returns unexpected response.

        Example:
            ```python
            # Delete a specific annotation
            result = client.annotations.delete(
                dataset_id="dataset_abc123",
                asset_id="asset_xyz789",
                annotation_id="annotation_xyz789",
            )
            print(f"Deleted annotation: {result.id}")

            # Safe deletion with error handling
            try:
                result = client.annotations.delete(
                    dataset_id="dataset_abc123",
                    asset_id="asset_xyz789",
                    annotation_id="annotation_xyz789",
                )
                print("Annotation deleted successfully")
            except ViNotFoundError:
                print("Annotation not found or already deleted")
            except ViPermissionError:
                print("Permission denied - cannot delete annotation")
            ```

        Warning:
            This operation is permanent and cannot be undone. All annotation
            data including geometry, labels, confidence scores, and metadata
            will be permanently deleted from the platform.

        Note:
            Deleting an annotation does not affect the associated asset. Only
            the annotation data is removed while the asset remains in the dataset.

        See Also:
            - `get()`: Verify annotation exists before deletion
            - `list()`: List annotations to find IDs for deletion
            - [Annotation Guide](../../guide/annotations.md#deletion): Best practices for annotation deletion

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(annotation_id, "annotation_id")

        self._link_parser = AnnotationLinkParser(
            self._auth.organization_id, dataset_id, asset_id
        )

        response = self._requester.delete(self._link_parser(annotation_id))

        if isinstance(response, dict) and response.get("data") == "":
            return DeletedResource(id=annotation_id, deleted=True)

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def upload(
        self,
        dataset_id: str,
        paths: Path | str | Sequence[Path | str],
        wait_until_done: bool = True,
        show_progress: bool = True,
    ) -> AnnotationUploadResult:
        """Upload annotation files to a dataset.

        Uploads annotation files containing labeling information to associate with
        assets in a dataset. Supports various annotation formats including JSON,
        COCO, YOLO, and custom formats. The upload process includes validation,
        parsing, and association with existing assets.

        Args:
            dataset_id: The unique identifier of the dataset to upload annotations to.
            paths: Path(s) to annotation files to upload. Can be:
                - Single file path (Path or str)
                - List of file paths (Sequence[Path | str])
                - Directory path (uploads all annotation files in directory)
            wait_until_done: Whether to wait for annotation processing to complete
                before returning. If True, returns when all annotations are processed.
                If False, returns immediately after upload starts. Defaults to True.
            show_progress: Whether to display progress bars during upload with file
                counts and status. Set to False for non-interactive environments.
                Defaults to True.

        Returns:
            AnnotationUploadResult: Simplified result wrapper with import statistics.
            Use result.summary() for formatted output, access result.total_annotations
            for counts, or access result.session for underlying session object.

        Raises:
            FileNotFoundError: If specified files or directories don't exist.
            ViValidationError: If dataset_id is invalid or annotation format is unsupported.
            ViUploadError: If upload fails due to network or server issues.
            ViPermissionError: If user lacks permission to upload annotations.

        Example:
            ```python
            from pathlib import Path

            # Upload a single annotation file (simple)
            result = client.annotations.upload(
                dataset_id="dataset_abc123",
                paths=Path("./annotations.json"),
            )
            print(f"Imported: {result.total_annotations} annotations")
            print(result.summary())  # Rich formatted summary

            # Upload multiple annotation files
            result = client.annotations.upload(
                dataset_id="dataset_abc123",
                paths=[
                    Path("./coco_annotations.json"),
                    Path("./yolo_labels.txt"),
                    Path("./custom_annotations.json"),
                ],
            )

            # Upload entire directory of annotation files
            result = client.annotations.upload(
                dataset_id="dataset_abc123",
                paths=Path("./annotation_files/"),
            )

            # Upload without waiting (async)
            result = client.annotations.upload(
                dataset_id="dataset_abc123",
                paths=Path("./large_annotation_set/"),
                wait_until_done=False,
            )
            print(f"Import started: {result.annotation_import_session_id}")
            # Check status later with wait_until_done()
            ```

        Note:
            - Supported formats: JSON, COCO JSON, YOLO TXT, CSV, XML
            - Annotations are automatically associated with existing assets by filename
            - Invalid annotations are skipped with error reporting
            - Large annotation sets are processed in batches
            - Directory uploads are recursive and include subdirectories

        Warning:
            Ensure annotation files reference existing assets in the dataset.
            Annotations for non-existent assets will be skipped and reported
            as errors in the import session.

        See Also:
            - `wait_until_done()`: Monitor upload progress
            - `list()`: View uploaded annotations
            - [Annotation Guide](../../guide/annotations.md): Supported formats and best practices

        """
        validate_id_param(dataset_id, "dataset_id")

        if not self._uploader:
            self._uploader = AnnotationUploader(self._requester, self._auth)

        upload_response = self._uploader.upload(
            dataset_id, paths, show_progress=show_progress
        )

        if wait_until_done:
            completed_session = self.wait_until_done(
                dataset_id, upload_response.annotation_import_session_id
            )
            return AnnotationUploadResult(completed_session)

        return AnnotationUploadResult(upload_response)

    def wait_until_done(
        self, dataset_id: str, annotation_import_session_id: str
    ) -> responses.AnnotationImportSession:
        """Wait until an annotation import session completes.

        Polls an annotation import session until it reaches a terminal state
        (completed, failed, or canceled). Uses intelligent backoff strategy
        to avoid excessive API calls while providing timely updates on import progress.

        Args:
            dataset_id: The unique identifier of the dataset containing the annotations.
            annotation_import_session_id: The unique identifier of the import session
                to monitor, typically returned from `upload()`.

        Returns:
            AnnotationImportSession object containing the final import status,
            processed annotation count, failed count, and detailed error information.

        Raises:
            ViNotFoundError: If the dataset or import session doesn't exist.
            ViValidationError: If dataset_id or session_id format is invalid.
            ViOperationError: If the import session fails.
            ViTimeoutError: If the session doesn't complete within timeout period.

        Example:
            ```python
            # Upload annotations without waiting
            session = client.annotations.upload(
                dataset_id="dataset_abc123",
                paths=Path("./annotations.json"),
                wait_until_done=False,
            )
            print(f"Import started: {session.annotation_import_session_id}")

            # Wait for completion separately
            completed_session = client.annotations.wait_until_done(
                dataset_id="dataset_abc123",
                annotation_import_session_id=session.annotation_import_session_id,
            )
            print(f"Import completed")
            print(f"Status: {completed_session.status}")
            print(f"File status: {completed_session.status.files.status_count}")
            print(
                f"Annotation status: {completed_session.status.annotations.status_count}"
            )
            ```

        Note:
            This method uses exponential backoff to poll the session status,
            starting with short intervals and gradually increasing to avoid
            excessive API calls. The default timeout is 30 minutes.

        Warning:
            For very large annotation import sessions (thousands of files),
            this method may block for extended periods. Consider running in
            a background thread for interactive applications.

        See Also:
            - `upload()`: Upload annotations and optionally wait for completion
            - `get_import_session()`: Check session status without waiting
            - [Annotation Guide](../../guide/annotations.md): Import troubleshooting

        """
        validate_id_param(dataset_id, "dataset_id")
        validate_id_param(annotation_import_session_id, "annotation_import_session_id")

        if not self._uploader:
            self._uploader = AnnotationUploader(self._requester, self._auth)

        return self._waiter.wait_until_done(
            lambda: self._uploader.get_annotation_import_session(
                dataset_id, annotation_import_session_id
            ),
            condition=Condition.ALL,
            status=ConditionStatus.REACHED,
        )

    def help(self) -> None:
        """Display helpful information about using the Annotation resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on annotations
            client.annotations.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        Annotation Resource - Quick Help                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List annotations for an asset:
    annotations = client.annotations.list(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789"
    )
    for ann in annotations.items:
        print(ann.annotation_id, ann.spec.tag)

  List with custom pagination:
    annotations = client.annotations.list(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789",
        pagination={"page_size": 100}
    )

  Get a specific annotation:
    annotation = client.annotations.get(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789",
        annotation_id="ann_123"
    )
    annotation.info()  # Show detailed information

  Upload annotations:
    result = client.annotations.upload(
        dataset_id="dataset_abc123",
        paths="./annotations.json"
    )

  Upload multiple annotation files:
    result = client.annotations.upload(
        dataset_id="dataset_abc123",
        paths=["./coco.json", "./yolo.txt"]
    )

  Delete an annotation:
    client.annotations.delete(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789",
        annotation_id="ann_123"
    )

📖 AVAILABLE METHODS:

  • list(dataset_id, asset_id, pagination=...)  - List annotations with pagination
  • get(dataset_id, asset_id, ann_id)           - Get a specific annotation
  • upload(dataset_id, paths, ...)              - Upload annotation files
  • delete(dataset_id, asset_id, ann_id)        - Delete an annotation
  • wait_until_done(dataset_id, session_id)     - Wait for upload completion

💡 TIPS:

  • Annotations are always linked to specific assets
  • Upload supports JSON and JSONL formats
  • Directory uploads are processed recursively
  • Check annotation.info() for detailed inspection
  • Use wait_until_done=False for async uploads

⚡ SUPPORTED FORMATS:

  Annotations: JSON and JSONL

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-annotations

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
