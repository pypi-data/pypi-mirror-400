#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets responses module.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from msgspec import field
from vi.api.resources.datasets.assets.types import AssetCustomMetadata
from vi.api.responses import ResourceCondition, ResourceMetadata, ViResponse


class AssetGenerations(ViResponse):
    """Asset generations response.

    Attributes:
        asset: URL or path to the full-size asset.
        thumbnail: URL or path to the thumbnail version.

    """

    asset: str
    thumbnail: str


class AssetAnnotations(ViResponse):
    """Asset annotations response.

    Attributes:
        with_tag: Dictionary mapping tag names to their counts for this asset.
        total: Total number of annotations on this asset.

    """

    with_tag: dict[str, int]
    total: int


class AssetDimensions(ViResponse):
    """Asset dimensions response.

    Attributes:
        height: Height of the asset in pixels.
        width: Width of the asset in pixels.
        depth: Depth dimension for 3D assets, None for 2D assets.

    """

    height: int
    width: int
    depth: int | None = None


class AssetPixelRatio(ViResponse):
    """Asset pixel ratio response.

    Attributes:
        height: Height pixel ratio.
        width: Width pixel ratio.
        depth: Depth pixel ratio for 3D assets, None for 2D assets.

    """

    height: int
    width: int
    depth: int | None = None


class AssetHash(ViResponse):
    """Asset hash response.

    Attributes:
        algorithm: The hashing algorithm used (e.g., 'sha256', 'md5').
        contents: The computed hash value as a hexadecimal string.

    """

    algorithm: str
    contents: str


class AssetMetadata(ViResponse):
    """Asset metadata response.

    Attributes:
        generations: Asset generation URLs (full-size and thumbnail).
        inserted_by: User ID who uploaded the asset.
        annotations: Annotation statistics for this asset.
        frames: Number of frames for video assets.
        cohorts: List of cohort IDs this asset belongs to.
        file_size: Size of the asset file in bytes.
        height: Height of the asset in pixels.
        width: Width of the asset in pixels.
        mime_type: MIME type of the asset (e.g., 'image/jpeg').
        source: Source identifier for the asset.
        status: Current processing status of the asset.
        upload_status: Upload completion status.
        visibility: Visibility setting for the asset.
        user_defined: Dictionary of user-defined metadata fields.
        custom_metadata: Custom metadata object.
        dimensions: Detailed dimension information.
        pixel_ratio: Pixel ratio information.
        comments: Number of comments on this asset.
        custom_metadata_count: Count of custom metadata entries.
        hash: Hash information for integrity verification.
        contents_from: Source of the asset contents.
        frames_change: Dictionary tracking frame changes for video assets.
        time_created: Unix timestamp of asset creation.
        last_updated: Unix timestamp of last update.
        contents_last_updated: Unix timestamp of last contents update.

    """

    generations: AssetGenerations
    inserted_by: str
    annotations: AssetAnnotations
    frames: int
    cohorts: list[str]
    file_size: int
    height: int
    width: int
    mime_type: str
    source: str
    status: str
    upload_status: str
    visibility: str
    user_defined: dict[str, Any]
    custom_metadata: AssetCustomMetadata
    dimensions: AssetDimensions
    pixel_ratio: AssetPixelRatio
    comments: int
    custom_metadata_count: int
    hash: AssetHash
    contents_from: str
    frames_change: dict[str, int]
    time_created: int
    last_updated: int
    contents_last_updated: int


class Contents(ViResponse):
    """Contents response.

    Attributes:
        url: Pre-signed URL for accessing the content.
        expiry: Unix timestamp when the URL expires.
        headers: Optional HTTP headers to include in requests.
        method: Optional HTTP method to use (e.g., 'GET', 'POST').

    """

    url: str
    expiry: int
    headers: dict[str, str] | None = None
    method: str | None = None


class AssetContents(ViResponse):
    """Asset contents response.

    Attributes:
        asset: Contents information for the full-size asset.
        thumbnail: Contents information for the thumbnail version.

    """

    asset: Contents | None = None
    thumbnail: Contents | None = None


class Asset(ViResponse):
    """Asset response.

    Attributes:
        asset_id: Unique identifier for the asset.
        dataset_id: ID of the dataset containing this asset.
        organization_id: Organization ID.
        filename: Original filename of the asset.
        kind: Resource kind identifier.
        owner: User ID of the asset owner.
        metadata: Comprehensive asset metadata including dimensions and statistics.
        self_link: API link to this asset resource.
        etag: Entity tag for caching and concurrency control.
        contents: Optional contents information with download URLs.

    """

    asset_id: str
    dataset_id: str
    organization_id: str = field(name="workspaceId")
    filename: str
    kind: str
    owner: str
    metadata: AssetMetadata
    self_link: str
    etag: str
    contents: AssetContents | None = None

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)

    def info(self) -> None:
        """Display rich information about this asset.

        Shows a formatted summary of the asset including dimensions,
        file information, annotations, and metadata in an easy-to-read format.

        Example:
            ```python
            asset = client.assets.get(
                dataset_id="dataset_abc123", asset_id="asset_xyz789"
            )
            asset.info()
            ```

        """
        created_str = datetime.fromtimestamp(
            self.metadata.time_created / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        updated_str = datetime.fromtimestamp(
            self.metadata.last_updated / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Format file size
        file_size_mb = self.metadata.file_size / (1024 * 1024)

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              Asset Information                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Filename:       {self.filename}
   Asset ID:       {self.asset_id}
   Dataset ID:     {self.dataset_id}
   Organization:   {self.organization_id}

📊 FILE DETAILS:
   MIME Type:      {self.metadata.mime_type}
   File Size:      {file_size_mb:.2f} MB ({self.metadata.file_size:,} bytes)
   Dimensions:     {self.metadata.width} x {self.metadata.height} px
   {"Frames:         " + str(self.metadata.frames) if self.metadata.frames > 1 else ""}

🎨 ANNOTATIONS:
   Total:          {self.metadata.annotations.total}
   Tags:           {", ".join(self.metadata.annotations.with_tag.keys()) if self.metadata.annotations.with_tag else "None"}

📅 DATES:
   Created:        {created_str}
   Last Updated:   {updated_str}
   Inserted By:    {self.metadata.inserted_by}

📋 STATUS:
   Upload Status:  {self.metadata.upload_status}
   Status:         {self.metadata.status}
   Visibility:     {self.metadata.visibility}

{"🔒 HASH:          " + self.metadata.hash.algorithm.upper() + " - " + self.metadata.hash.contents[:16] + "..." if hasattr(self.metadata, "hash") else ""}

💡 QUICK ACTIONS:
   Download:       client.assets.download(
                       dataset_id="{self.dataset_id}",
                       save_dir="./downloads"
                   )
"""
        print(info_text)


class UploadedAssetMetadata(ViResponse):
    """Uploaded asset metadata response.

    Attributes:
        kind: Resource kind identifier.
        filename: Name of the uploaded file.
        mime: MIME type of the uploaded file.
        size: File size in bytes.
        crc32c: Optional CRC32C checksum for integrity verification.
        custom_metadata: Optional custom metadata for the asset.

    """

    kind: str
    filename: str
    mime: str
    size: int
    crc32c: int | None = None
    custom_metadata: AssetCustomMetadata | None = None


class FailureMode(Enum):
    """Failure mode enum."""

    FAIL_AFTER_ONE = "FailAfterOne"
    FAIL_AFTER_ALL = "FailAfterAll"


class ResourceRetentionMode(Enum):
    """Resource retention mode enum."""

    REMOVE_LINKED_RESOURCE = "RemoveLinkedResource"
    KEEP_LINKED_RESOURCES = "KeepLinkedResources"


class AssetIngestionSessionSpec(ViResponse):
    """Asset ingestion session spec response.

    Attributes:
        kind: Resource kind identifier.
        failureMode: How to handle failures during ingestion.
        onAssetOverwritten: How to handle resource retention when assets are overwritten.
        assets: Optional list of asset metadata being ingested.

    """

    kind: str
    failureMode: FailureMode
    onAssetOverwritten: ResourceRetentionMode
    assets: list[UploadedAssetMetadata] | None = None


class AssetForUpload(ViResponse):
    """Asset for upload response.

    Attributes:
        metadata: Metadata for the asset being uploaded.
        upload: Contents information including the upload URL.

    """

    metadata: UploadedAssetMetadata
    upload: Contents


class AssetIngestionError(Enum):
    """Asset ingestion error enum."""

    EALREADY = "EALREADY"
    EBADMIME = "EBADMIME"
    EBADSIZE = "EBADSIZE"
    ECORRUPT = "ECORRUPT"
    ENOQUOTA = "ENOQUOTA"
    EOLDMETA = "EOLDMETA"
    ETIMEOUT = "ETIMEOUT"
    ERESNENT = "ERESNENT"
    EPROJECT = "EPROJECT"
    ENOASSET = "ENOASSET"
    ESEQMETA = "ESEQMETA"
    EUNKNOWN = "EUNKNOWN"


class AssetIngestionEventError(ViResponse, tag="Error", tag_field="kind"):
    """Asset ingestion event error response.

    Attributes:
        kind: Event kind identifier.
        files: Dictionary mapping filenames to their ingestion errors.
        corrections: Dictionary mapping issues to their corrections.
        time: Unix timestamp of when the error occurred.

    """

    files: dict[str, AssetIngestionError]
    corrections: dict[str, str]
    time: int


class AssetIngestionEventProgress(ViResponse, tag="Progress", tag_field="kind"):
    """Asset ingestion event progress response.

    Attributes:
        kind: Event kind identifier.
        tasks: Nested dictionary tracking progress of various tasks.

    """

    tasks: dict[str, dict[str, int]]


AssetIngestionEvent = AssetIngestionEventError | AssetIngestionEventProgress


class AssetIngestionProgressCount(ViResponse):
    """Asset ingestion progress count response.

    Attributes:
        total: Total number of assets being ingested.
        succeeded: Number of assets successfully ingested.
        errored: Number of assets that encountered errors.

    """

    total: int
    succeeded: int
    errored: int


class AssetIngestionSessionStatus(ViResponse):
    """Asset ingestion session status response.

    Attributes:
        conditions: List of resource conditions tracking ingestion progress.
        events: List of ingestion events (errors and progress updates).
        progressCount: Progress statistics for the ingestion session.
        assets: Optional list of assets being uploaded.

    """

    conditions: list[ResourceCondition]
    events: list[AssetIngestionEvent]
    progressCount: AssetIngestionProgressCount
    assets: list[AssetForUpload] | None = None


class AssetIngestionSession(ViResponse, tag_field="kind"):
    """Asset ingestion session response.

    Attributes:
        organization_id: Organization ID.
        dataset_id: ID of the dataset receiving the assets.
        asset_source_class: Classification of the asset source.
        asset_source_provider: Provider of the asset source.
        asset_source_id: Unique identifier for the asset source.
        asset_ingestion_session_id: Unique identifier for this ingestion session.
        self_link: API link to this ingestion session resource.
        etag: Entity tag for caching and concurrency control.
        metadata: Resource metadata including timestamps.
        spec: Ingestion specification including failure handling.
        status: Current status of the ingestion session.

    """

    organization_id: str = field(name="workspaceId")
    dataset_id: str
    asset_source_class: str
    asset_source_provider: str
    asset_source_id: str
    asset_ingestion_session_id: str
    self_link: str
    etag: str
    metadata: ResourceMetadata
    spec: AssetIngestionSessionSpec
    status: AssetIngestionSessionStatus

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)
