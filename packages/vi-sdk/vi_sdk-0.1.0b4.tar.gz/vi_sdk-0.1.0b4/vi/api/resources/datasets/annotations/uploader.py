#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   uploader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations uploader module.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from pathlib import Path

import msgspec
from rich import print as rprint
from rich.progress import BarColumn, TaskID, TimeElapsedColumn
from vi.api.resources.datasets.annotations import consts, responses
from vi.api.resources.datasets.annotations.links import (
    AnnotationImportSessionLinkParser,
)
from vi.api.resources.datasets.annotations.types import (
    AnnotationImportFailurePolicy,
    AnnotationImportFileSpec,
    AnnotationImportPatchCondition,
    AnnotationImportPatchStatus,
    AnnotationImportPayload,
    AnnotationImportSession,
    AnnotationImportSource,
    AnnotationImportSpec,
)
from vi.api.resources.datasets.utils.helper import calculate_crc32c
from vi.api.resources.managers import ResourceUploader
from vi.api.responses import ConditionStatus
from vi.api.types import ResourceMetadata
from vi.client.errors import ViInvalidParameterError
from vi.utils.graceful_exit import GracefulExit, graceful_exit
from vi.utils.progress import ViProgress

UPLOAD_SESSION_TIMEOUT_SECONDS = 55 * 60  # 55 minutes


class AnnotationUploader(ResourceUploader):
    """Uploader for annotation files with session-based import workflow.

    Handles the complete lifecycle of annotation imports to Datature datasets:
    1. Creates an annotation import session with configurable timeout and policies
    2. Registers annotation files and receives signed upload URLs
    3. Uploads files using the signed URLs
    4. Updates session status to reflect completion or failure

    Supports graceful cancellation via Ctrl+C (KeyboardInterrupt) at any stage,
    with proper cleanup and session status updates.

    Attributes:
        _link_parser: Parser for generating annotation import session API links.
            Initialized lazily when needed for API calls.

    Example:
        ```python
        from vi import Client

        client = Client(api_key="your-api-key")

        # Upload annotations from a directory
        session = client.datasets.annotations.upload(
            dataset_id="abc123", paths="/path/to/annotations/"
        )

        print(f"Import session: {session.annotation_import_session_id}")
        print(f"Status: {session.status.conditions}")
        ```

    Note:
        This class is typically accessed via the client's datasets.annotations
        resource, not instantiated directly.

    """

    _link_parser: AnnotationImportSessionLinkParser | None = None

    def upload(
        self,
        dataset_id: str,
        paths: Path | str | Sequence[Path | str],
        upload_timeout: int = UPLOAD_SESSION_TIMEOUT_SECONDS,
        failure_policies: AnnotationImportFailurePolicy = AnnotationImportFailurePolicy(),
        source: AnnotationImportSource = AnnotationImportSource.UPLOADED_INDIVIDUAL_FILES,
        attributes: dict[str, str] | None = None,
        show_progress: bool = True,
    ) -> responses.AnnotationImportSession:
        """Upload annotation files to a dataset.

        This method handles the complete annotation upload workflow:
        1. Creates an annotation import session
        2. Registers files with the session
        3. Uploads files using signed URLs
        4. Updates session status upon completion

        Supports graceful cancellation via Ctrl+C (KeyboardInterrupt).

        Args:
            dataset_id: ID of the dataset to upload annotations to.
            paths: File path(s) to upload. Can be:
                - Single file path (str or Path)
                - Directory path (recursively scans for annotation files)
                - List of file/directory paths
            upload_timeout: Maximum time in seconds for the upload session.
                Defaults to 55 minutes (3300 seconds).
            failure_policies: Policies for handling annotation import failures.
                Defaults to AnnotationImportFailurePolicy() with default settings.
            source: Source type of the annotations. Defaults to
                UPLOADED_INDIVIDUAL_FILES for user-uploaded files.
            attributes: Optional metadata attributes to attach to the import session.
            show_progress: Whether to display progress bars during upload.
                Defaults to True.

        Returns:
            AnnotationImportSession response containing session details, status,
            and conditions.

        Raises:
            ViInvalidParameterError: If paths are invalid or don't exist.
            KeyboardInterrupt: If user cancels the upload with Ctrl+C.
            ValueError: If no valid annotation files found or API response invalid.

        Example:
            ```python
            # Upload a single annotation file
            session = client.datasets.annotations.upload(
                dataset_id="abc123", paths="annotations.json"
            )

            # Upload directory of annotations
            session = client.datasets.annotations.upload(
                dataset_id="abc123", paths="/path/to/annotations/", show_progress=True
            )

            # Upload with custom failure policies
            from vi.api.resources.datasets.annotations.types import (
                AnnotationImportFailurePolicy,
            )

            policies = AnnotationImportFailurePolicy(
                on_asset_not_found="skip", on_invalid_annotation="fail"
            )

            session = client.datasets.annotations.upload(
                dataset_id="abc123", paths="annotations.json", failure_policies=policies
            )
            ```

        """
        annotation_file_paths = self._parse_annotation_paths(paths)

        with graceful_exit("Upload cancelled by user") as handler:
            if show_progress:
                with ViProgress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.2f}%",
                    TimeElapsedColumn(),
                    transient=True,
                ) as progress:
                    task = progress.add_task(
                        "Initializing annotation import session...",
                        total=len(annotation_file_paths) + 1,
                    )

                    return self._execute_upload(
                        dataset_id,
                        annotation_file_paths,
                        upload_timeout,
                        failure_policies,
                        source,
                        attributes,
                        progress,
                        task,
                        handler,
                    )
            else:
                return self._execute_upload(
                    dataset_id,
                    annotation_file_paths,
                    upload_timeout,
                    failure_policies,
                    source,
                    attributes,
                    None,
                    None,
                    handler,
                )

    def _execute_upload(
        self,
        dataset_id: str,
        annotation_file_paths: list[str],
        upload_timeout: int,
        failure_policies: AnnotationImportFailurePolicy,
        source: AnnotationImportSource,
        attributes: dict[str, str] | None,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> responses.AnnotationImportSession:
        """Execute the complete annotation upload workflow.

        Orchestrates the three-phase upload process:
        1. Create an annotation import session via API
        2. Register annotation files with the session
        3. Upload files using signed URLs

        Handles graceful cancellation and error recovery by patching
        the session status appropriately.

        Args:
            dataset_id: ID of the dataset to upload to.
            annotation_file_paths: List of absolute paths to annotation files.
            upload_timeout: Maximum time in seconds for the upload session.
            failure_policies: Policies for handling annotation import failures.
            source: Source type of the annotations.
            attributes: Optional metadata attributes for the import session.
            progress: Optional progress tracker for UI updates.
            task: Optional progress task ID for updating progress bars.
            handler: Graceful exit handler for cancellation support.

        Returns:
            AnnotationImportSession response with final status after upload
            completion or cancellation.

        Raises:
            KeyboardInterrupt: If user cancels during upload. Session status
                is updated before re-raising.
            ValueError: If no files added to session or API response invalid.

        """
        # Early cancellation check
        if handler.exit_now:
            raise KeyboardInterrupt("Upload cancelled by user")

        # Step 1: Create annotation import session
        session_response = self._create_annotation_import_session(
            dataset_id=dataset_id,
            upload_timeout=upload_timeout,
            failure_policies=failure_policies,
            source=source,
            attributes=attributes,
            handler=handler,
        )

        try:
            # Step 2: Add files to session
            files_response = self._add_files_to_session(
                dataset_id=dataset_id,
                annotation_import_session_id=session_response.annotation_import_session_id,
                annotation_file_paths=annotation_file_paths,
            )

            if not files_response.files:
                raise ValueError("No files added to the session")

            # Step 3: Upload files using signed URLs
            self._upload_files(
                annotation_file_paths=annotation_file_paths,
                files_response=files_response,
                progress=progress,
                task=task,
                handler=handler,
            )

            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.REACHED,
                last_transition_time=int(time.time() * 1000),
            )

        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Annotation upload cancelled by user[/yellow]")
            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.FAILED_REACH,
                last_transition_time=int(time.time() * 1000),
                reason="CancelledByUser",
            )
            # Update session status before re-raising
            self._patch_annotation_import_session(
                dataset_id, session_response.annotation_import_session_id, condition
            )
            raise

        except Exception as e:
            rprint(f"[red]Error uploading files: {e}[/red]")
            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.FAILED_REACH,
                last_transition_time=int(time.time() * 1000),
                reason="UserUploadErrored",
            )

        return self._patch_annotation_import_session(
            dataset_id, session_response.annotation_import_session_id, condition
        )

    def _parse_annotation_paths(
        self, paths: Path | str | Sequence[Path | str]
    ) -> list[str]:
        """Parse and expand annotation paths into a list of file paths.

        Handles various input formats:
        - Single file path → returns list with one file
        - Directory path → recursively scans for supported annotation files
        - List of paths → processes each and combines results

        Only includes files with extensions in SUPPORTED_ANNOTATION_FILE_EXTENSIONS.

        Args:
            paths: Single path, directory, or sequence of paths to process.

        Returns:
            List of absolute paths to annotation files.

        Raises:
            ViInvalidParameterError: If a path doesn't exist or isn't a file/directory.

        """
        if isinstance(paths, (str, Path)):
            path_list = [paths]
        else:
            path_list = paths

        annotation_file_paths = []
        for path_item in path_list:
            path = Path(path_item).expanduser().resolve()

            if path.is_file():
                annotation_file_paths.append(str(path))

            elif path.is_dir():
                for file_path in path.glob("**/*"):
                    if (
                        file_path.is_file()
                        and file_path.suffix.lower()
                        in consts.SUPPORTED_ANNOTATION_FILE_EXTENSIONS
                    ):
                        annotation_file_paths.append(str(file_path))

            else:
                raise ViInvalidParameterError(
                    "paths",
                    f"Invalid path: {path_item}. Path must be a file or directory",
                )

        return annotation_file_paths

    def get_annotation_import_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
    ) -> responses.AnnotationImportSession:
        """Retrieve an annotation import session by ID.

        Fetches the current state of an annotation import session, including
        its status, conditions, and metadata. Useful for monitoring the progress
        of annotation imports or checking their final status.

        Args:
            dataset_id: ID of the dataset containing the import session.
            annotation_import_session_id: ID of the annotation import session
                to retrieve.

        Returns:
            AnnotationImportSession response containing session details, status,
            and conditions.

        Raises:
            ValueError: If the API response is invalid or malformed.

        Example:
            ```python
            session = client.datasets.annotations.get_annotation_import_session(
                dataset_id="abc123", annotation_import_session_id="import-xyz"
            )

            print(f"Status: {session.status.conditions}")
            ```

        """
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        response = self._requester.get(
            self._link_parser(annotation_import_session_id),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _patch_annotation_import_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
        condition: responses.AnnotationImportSessionCondition,
    ) -> responses.AnnotationImportSession:
        """Update the status of an annotation import session.

        Patches the session's status by adding a condition that tracks the
        upload lifecycle (e.g., FilesInserted reached/failed).

        This is typically called after:
        - Successful file upload → condition with REACHED status
        - Upload cancellation → condition with FAILED_REACH and reason "CancelledByUser"
        - Upload error → condition with FAILED_REACH and reason "UserUploadErrored"

        Args:
            dataset_id: ID of the dataset containing the import session.
            annotation_import_session_id: ID of the session to update.
            condition: Condition object describing the status transition,
                including status (REACHED/FAILED_REACH), timestamp, and
                optional reason for failures.

        Returns:
            Updated AnnotationImportSession response with the new condition
            applied.

        Raises:
            ValueError: If the API response is invalid or malformed.

        """
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        patch_status = AnnotationImportPatchStatus(
            status=AnnotationImportPatchCondition(conditions=[condition])
        )

        response = self._requester.patch(
            self._link_parser(f"{annotation_import_session_id}/status"),
            json_data=msgspec.to_builtins(patch_status, str_keys=True),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _create_annotation_import_session(
        self,
        dataset_id: str,
        upload_timeout: int,
        failure_policies: AnnotationImportFailurePolicy,
        source: AnnotationImportSource,
        attributes: dict[str, str] | None,
        handler: GracefulExit | None = None,
    ) -> responses.AnnotationImportSession:
        """Create an annotation import session.

        Args:
            dataset_id: Dataset ID to import annotations to
            upload_timeout: Timeout in seconds for the upload
            failure_policies: Policies for handling failures
            source: Source of the annotations
            attributes: Optional metadata attributes
            handler: Optional graceful exit handler for cancellation support

        Returns:
            Annotation import session response

        Raises:
            KeyboardInterrupt: If cancellation was requested before making the request
            ValueError: If the API response is invalid

        """
        # Final cancellation check before making the HTTP request
        if handler and handler.exit_now:
            raise KeyboardInterrupt("Upload cancelled before creating import session")

        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        annotation_import_session = AnnotationImportSession(
            spec=AnnotationImportSpec(
                upload_before=int((time.time() + upload_timeout) * 1000),
                failure_policies=failure_policies,
                source=source,
            ),
            metadata=ResourceMetadata(attributes=attributes or {}),
        )

        response = self._requester.post(
            self._link_parser(),
            json_data=msgspec.to_builtins(annotation_import_session, str_keys=True),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _add_files_to_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
        annotation_file_paths: list[str],
    ) -> responses.AnnotationImportFilesResponse:
        """Register annotation files with an import session.

        Generates file specifications (size, CRC32C checksum) for each
        annotation file and registers them with the import session.
        The API responds with signed URLs for uploading each file.

        Args:
            dataset_id: ID of the dataset containing the import session.
            annotation_import_session_id: ID of the import session to add
                files to.
            annotation_file_paths: List of absolute paths to annotation files
                to register.

        Returns:
            AnnotationImportFilesResponse containing a mapping of filenames
            to their upload URLs and headers.

        Raises:
            ValueError: If the API response is invalid or malformed.

        """
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        annotation_files_for_upload = {}
        for file_path in annotation_file_paths:
            annotation_files_for_upload.update(
                {Path(file_path).name: self._generate_annotation_file_spec(file_path)}
            )

        payload = AnnotationImportPayload(files=annotation_files_for_upload)

        response = self._requester.post(
            self._link_parser(f"{annotation_import_session_id}/files"),
            json_data=msgspec.to_builtins(payload, str_keys=True),
            response_type=responses.AnnotationImportFilesResponse,
        )

        if isinstance(response, responses.AnnotationImportFilesResponse):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _upload_files(
        self,
        annotation_file_paths: list[str],
        files_response: responses.AnnotationImportFilesResponse,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> None:
        """Upload annotation files using signed URLs.

        Performs the actual file uploads using the signed URLs provided by
        the API. Uploads files sequentially with progress tracking and
        graceful cancellation support.

        Matches local file paths to their corresponding signed URLs based
        on filename and uploads each file. Checks for cancellation before
        each upload to allow responsive Ctrl+C handling.

        Args:
            annotation_file_paths: List of absolute paths to annotation files.
            files_response: Response containing signed URLs for each file.
            progress: Optional progress tracker for UI updates.
            task: Optional progress task ID for updating progress bars.
            handler: Graceful exit handler for checking cancellation requests.

        Returns:
            None. Files are uploaded as a side effect.

        Note:
            This method returns early (without error) if cancellation is
            detected, allowing the caller to handle cleanup.

        """
        filtered_file_paths = []
        for file_path in files_response.files.keys():
            matching_path = next(
                (
                    path
                    for path in annotation_file_paths
                    if os.path.basename(path) == file_path
                ),
                None,
            )
            if matching_path:
                filtered_file_paths.append(matching_path)

        # Step 3: Upload files using signed URLs
        if progress and task is not None:
            progress.update(
                task,
                description=f"Uploading 0 / {len(filtered_file_paths)} files...",
                advance=1,
            )

        for i, (file_path, file_upload_url) in enumerate(
            zip(filtered_file_paths, files_response.files.values())
        ):
            if handler.exit_now:
                if progress and task is not None:
                    progress.update(task, description="✗ Upload cancelled")
                return

            self._upload_single_file(file_path, file_upload_url)
            if progress and task is not None:
                progress.update(
                    task,
                    description=f"Uploading {i + 1} / {len(filtered_file_paths)} files...",
                    advance=1,
                )

        if progress and task is not None:
            progress.update(
                task,
                description="✓ Upload complete!",
                completed=len(filtered_file_paths),
                refresh=True,
            )

    def _upload_single_file(
        self, file_path: str, file_upload_url: responses.AnnotationImportFileUploadUrl
    ) -> None:
        """Upload a single annotation file using a signed URL.

        Performs the actual HTTP request to upload the file content to the
        signed URL provided by the API. Uses the specified HTTP method
        (typically PUT) and headers from the upload URL response.

        Args:
            file_path: Absolute path to the annotation file to upload.
            file_upload_url: Object containing the signed URL, HTTP method,
                and headers required for upload.

        Returns:
            None. File is uploaded as a side effect.

        Raises:
            httpx.HTTPStatusError: If the upload request fails with a non-2xx
                status code.
            OSError: If the file cannot be read.

        """
        with open(file_path, "rb") as f:
            upload_response = self._http_client.request(
                file_upload_url.method,
                file_upload_url.url,
                content=f,
                headers=file_upload_url.headers,
            )
            upload_response.raise_for_status()

    def _generate_annotation_file_spec(
        self, annotation_path: Path | str
    ) -> AnnotationImportFileSpec:
        """Generate file specification for an annotation file.

        Creates a file specification containing metadata required for
        registering the file with an import session:
        - File size in bytes
        - CRC32C checksum (base64 encoded) for integrity verification

        Args:
            annotation_path: Path to the annotation file. Can be relative
                or absolute; will be expanded and resolved.

        Returns:
            AnnotationImportFileSpec containing file size and CRC32C checksum.

        Raises:
            OSError: If the file cannot be accessed or read for checksum
                calculation.

        """
        annotation_path = Path(annotation_path).expanduser().resolve()
        size = annotation_path.stat().st_size

        crc32c_value = calculate_crc32c(annotation_path, base64_encoded=True)

        return AnnotationImportFileSpec(size_bytes=size, crc32c=crc32c_value)
