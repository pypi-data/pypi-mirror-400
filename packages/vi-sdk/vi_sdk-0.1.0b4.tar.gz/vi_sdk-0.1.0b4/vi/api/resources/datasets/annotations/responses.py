#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations responses module.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from msgspec import field
from vi.api.responses import ConditionStatus, ResourceMetadata, ViResponse


class Whole(ViResponse):
    """Whole annotation reference.

    Attributes:
        id: Unique identifier of the whole annotation this part belongs to.

    """

    id: str


class Roles(Enum):
    """Annotation roles."""

    CAPTION = "Caption"
    PHRASE_GROUNDING_BOUNDING_BOX = "PhraseGroundingBoundingBox"


class ThisPart(ViResponse):
    """Object that this part belongs to.

    Attributes:
        role: The role type of this annotation part (Caption, PhraseGroundingBoundingBox, etc.).

    """

    role: Roles


class AnnotationAggregation(ViResponse):
    """Annotation aggregation.

    Attributes:
        whole: Reference to the complete annotation.
        this_part: Information about this specific part's role.

    """

    whole: Whole
    this_part: ThisPart


class Caption(ViResponse, tag_field="kind"):
    """Caption content variant.

    Attributes:
        contents: The caption text content.

    """

    contents: str = ""


class PhraseGroundingBoundingBox(ViResponse, tag_field="kind"):
    """Phrase grounding bounding box content variant.

    Attributes:
        bound: List of 4 coordinate pairs [x, y] defining the bounding box corners.
        target: Tuple of (start_index, end_index) indicating the phrase span in text.

    """

    bound: list[list[float]]  # 4 coordinate pairs
    target: tuple[int, int]  # start and end index


AnnotationContent = Caption | PhraseGroundingBoundingBox


class AnnotationSpec(ViResponse):
    """Annotation spec.

    Attributes:
        bound_type: Type of boundary (e.g., 'box', 'polygon', 'point').
        tag: Tag identifier associated with this annotation.
        aggregation: Aggregation information linking parts to whole.
        contents: The annotation content (Caption or PhraseGroundingBoundingBox).

    """

    bound_type: str
    tag: int
    aggregation: AnnotationAggregation
    contents: AnnotationContent


class Annotation(ViResponse, tag_field="kind"):
    """Annotation response.

    Attributes:
        annotation_id: Unique identifier for the annotation.
        asset_id: ID of the asset this annotation belongs to.
        organization_id: Organization ID.
        dataset_id: Dataset ID this annotation belongs to.
        spec: Annotation specification including bounds and content.
        metadata: Resource metadata including timestamps.
        self_link: API link to this annotation resource.
        etag: Entity tag for caching and concurrency control.

    """

    annotation_id: str
    asset_id: str
    organization_id: str = field(name="workspaceId")
    dataset_id: str
    spec: AnnotationSpec
    metadata: ResourceMetadata
    self_link: str
    etag: str

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)

    def info(self) -> None:
        """Display rich information about this annotation.

        Shows a formatted summary of the annotation including type, bounds,
        tags, and metadata in an easy-to-read format.

        Example:
            ```python
            annotation = client.annotations.get(
                dataset_id="dataset_abc123",
                asset_id="asset_xyz789",
                annotation_id="ann_123",
            )
            annotation.info()
            ```

        """
        created_str = datetime.fromtimestamp(
            self.metadata.time_created / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        updated_str = datetime.fromtimestamp(
            self.metadata.last_updated / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Annotation Information                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Annotation ID:  {self.annotation_id}
   Asset ID:       {self.asset_id}
   Dataset ID:     {self.dataset_id}
   Organization:   {self.organization_id}

🎨 ANNOTATION DETAILS:
   Bound Type:     {self.spec.bound_type}
   Tag:            {self.spec.tag}
   Content Type:   {type(self.spec.contents).__name__}

📅 DATES:
   Created:        {created_str}
   Last Updated:   {updated_str}

💡 QUICK ACTIONS:
   Delete:  client.annotations.delete(
               dataset_id="{self.dataset_id}",
               asset_id="{self.asset_id}",
               annotation_id="{self.annotation_id}"
            )
   Show Asset:   client.assets.get(
                     dataset_id="{self.dataset_id}",
                     asset_id="{self.asset_id}"
                 )
"""
        print(info_text)


class ExportedAnnotationsDownloadUrl(ViResponse):
    """Exported annotations download URL.

    Attributes:
        url: Pre-signed URL for downloading the exported annotations.
        expires_at: Unix timestamp when the download URL expires.

    """

    url: str
    expires_at: int


class ExportedAnnotationsStatus(ViResponse):
    """Exported annotations status.

    Attributes:
        conditions: List of condition dictionaries tracking export progress.
        download_url: Download URL information once export is ready.

    """

    conditions: list[dict]
    download_url: ExportedAnnotationsDownloadUrl


class ExportedAnnotations(ViResponse):
    """Exported annotations.

    Attributes:
        kind: Resource kind identifier.
        organization_id: Organization ID.
        dataset_id: ID of the dataset whose annotations were exported.
        dataset_export_id: Unique identifier for this export operation.
        spec: Export specification dictionary with format and options.
        status: Current status of the export operation.
        metadata: Resource metadata including timestamps.

    """

    kind: str
    organization_id: str = field(name="workspaceId")
    dataset_id: str
    dataset_export_id: str
    spec: dict[str, Any]
    status: ExportedAnnotationsStatus
    metadata: ResourceMetadata

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)


class DownloadedAnnotations(ViResponse):
    """Downloaded annotation export.

    Attributes:
        export_path: Local file path where annotations were saved.
        dataset_id: ID of the dataset whose annotations were downloaded.
        export_id: Unique identifier for this export operation.

    """

    export_path: str
    dataset_id: str
    export_id: str

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)


class ConditionReason(Enum):
    """Condition reason."""

    CANCELLED_BY_USER = "CancelledByUser"
    USER_UPLOAD_ERRORED = "UserUploadErrored"


class AnnotationImportSessionCondition(ViResponse):
    """Annotation import session condition.

    Attributes:
        condition: The condition name being tracked.
        status: Current status of the condition (Waiting, Reached, FailedReach).
        last_transition_time: Unix timestamp of the last status transition.
        reason: Optional reason for the condition status.

    """

    condition: str
    status: ConditionStatus
    last_transition_time: int | float
    reason: ConditionReason | None = None


class AnnotationFileStatus(ViResponse):
    """Annotation file status.

    Attributes:
        page_count: Number of annotation file pages processed.
        total_size_bytes: Total size of annotation files in bytes.
        status_count: Dictionary mapping status names to their counts.

    """

    page_count: int
    total_size_bytes: int
    status_count: dict[str, int]


class AnnotationStatus(ViResponse):
    """Annotation status.

    Attributes:
        status_count: Dictionary mapping annotation status names to their counts.

    """

    status_count: dict[str, int]


class AnnotationImportSessionStatus(ViResponse):
    """Annotation import session status.

    Attributes:
        conditions: List of session conditions tracking import progress.
        files: Status information about imported files.
        annotations: Status information about imported annotations.
        reason: Optional reason for current status.

    """

    conditions: list[AnnotationImportSessionCondition]
    files: AnnotationFileStatus
    annotations: AnnotationStatus
    reason: str | None = None


class AnnotationImportSource(Enum):
    """Annotation import source enum."""

    UPLOADED_INDIVIDUAL_FILES = "UploadedIndividualFiles"


class FailurePolicy(Enum):
    """Failure policy enum."""

    WARN = "Warn"
    REJECT_FILE = "RejectFile"
    REJECT_SESSION = "RejectSession"


class AnnotationImportFailurePolicy(ViResponse):
    """Annotation import failure policy struct.

    Attributes:
        on_bad_annotation: Policy for handling invalid annotations (Warn, RejectFile, RejectSession).
        on_bad_file: Policy for handling corrupted or invalid files.
        on_overwritten: Policy for handling annotation overwrites.

    """

    on_bad_annotation: FailurePolicy
    on_bad_file: FailurePolicy
    on_overwritten: FailurePolicy


class AnnotationImportSpec(ViResponse):
    """Annotation import spec struct.

    Attributes:
        upload_before: Unix timestamp deadline for file uploads.
        failure_policies: Policies defining how to handle various failure scenarios.
        source: Source type of the imported annotations (default: UploadedIndividualFiles).

    """

    upload_before: int
    failure_policies: AnnotationImportFailurePolicy
    source: AnnotationImportSource = AnnotationImportSource.UPLOADED_INDIVIDUAL_FILES


class AnnotationImportSession(ViResponse, tag_field="kind"):
    """Annotation import session.

    Attributes:
        user: User ID who initiated the import.
        organization_id: Organization ID.
        dataset_id: ID of the dataset receiving the annotations.
        annotation_import_session_id: Unique identifier for this import session.
        self_link: API link to this import session resource.
        etag: Entity tag for caching and concurrency control.
        metadata: Resource metadata including timestamps.
        spec: Import specification including failure policies.
        status: Current status of the import session.

    """

    user: str
    organization_id: str = field(name="workspaceId")
    dataset_id: str
    annotation_import_session_id: str
    self_link: str
    etag: str
    metadata: ResourceMetadata
    spec: AnnotationImportSpec
    status: AnnotationImportSessionStatus

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)


class AnnotationImportFileUploadUrl(ViResponse):
    """Annotation import file upload URL.

    Attributes:
        method: HTTP method to use for upload (typically 'PUT' or 'POST').
        url: Pre-signed URL for uploading the annotation file.
        headers: HTTP headers required for the upload request.

    """

    method: str
    url: str
    headers: dict[str, str]


class AnnotationImportFilesResponse(ViResponse):
    """Annotation import files.

    Attributes:
        files: Dictionary mapping filenames to their upload URL information.

    """

    files: dict[str, AnnotationImportFileUploadUrl]
