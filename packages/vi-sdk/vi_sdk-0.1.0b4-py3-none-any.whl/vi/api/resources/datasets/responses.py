#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK datasets responses module.
"""

from datetime import datetime
from enum import Enum

from msgspec import field
from vi.api.resources.datasets.types import (
    BulkAssetDeletionSpec,
    DatasetContent,
    DatasetLocalization,
    DatasetType,
)
from vi.api.responses import ResourceCondition, ResourceMetadata, User, ViResponse


class DatasetStatistic(ViResponse):
    """Dataset statistic response.

    Attributes:
        asset_total: Total number of assets in the dataset.
        annotation_total: Total number of annotations in the dataset.
        tags_count: Dictionary mapping tag names to their occurrence counts.
        asset_annotated: Number of assets that have been annotated.

    """

    asset_total: int
    annotation_total: int
    tags_count: dict[str, int]
    asset_annotated: int


class DatasetAccess(ViResponse):
    """Dataset access response.

    Attributes:
        is_public: Whether the dataset is publicly accessible.
        is_read_only: Whether the dataset is in read-only mode.
        is_hidden: Whether the dataset is hidden from listings.

    """

    is_public: bool | None
    is_read_only: bool | None
    is_hidden: bool | None = None


class AssetStatusDetail(ViResponse):
    """Asset status detail response.

    Attributes:
        description: Description of the asset status.
        color: Color code or name associated with this status.
        create_date: Unix timestamp of when this status was created.

    """

    description: str
    color: str
    create_date: int | None = None


class TagDetail(ViResponse):
    """Tag detail response.

    Attributes:
        description: Description or notes for the tag.
        color: Color code or name associated with this tag for visual identification.

    """

    description: str | None = None
    color: str | None = None


class Dataset(ViResponse, tag_field="kind"):
    """Dataset response.

    Attributes:
        dataset_id: Unique identifier for the dataset.
        name: Display name of the dataset.
        owner: User ID of the dataset owner.
        organization_id: Organization ID that owns this dataset.
        type: Type of dataset (e.g., image, video, text).
        content: Dataset content type and configuration.
        create_date: Unix timestamp of when the dataset was created.
        statistic: Statistical information about assets and annotations.
        users: Dictionary mapping user IDs to User objects or role strings.
        tags: Dictionary mapping tag names to counts.
        cohorts: List of cohort definitions for the dataset.
        status: Current status code of the dataset.
        last_accessed: Unix timestamp of last access to the dataset.
        is_locked: Whether the dataset is locked for editing.
        access: Access control settings for the dataset.
        preference: Dictionary of user preference settings.
        asset_statuses: Dictionary mapping status names to AssetStatusDetail objects.
        self_link: API link to this dataset resource.
        etag: Entity tag for caching and concurrency control.
        localization: Localization setting for the dataset.
        data_localization: Data localization setting for storage.
        description: Optional description of the dataset.
        tag_details: Optional dictionary mapping tag names to TagDetail objects.
        is_demo_project: Whether this is a demo/example project.
        delete_op: ID of any pending deletion operation.
        bypass_quota: Whether this dataset bypasses quota limits.

    """

    dataset_id: str
    name: str
    owner: str
    organization_id: str = field(name="workspaceId")
    type: DatasetType
    content: DatasetContent
    create_date: int
    statistic: DatasetStatistic
    users: dict[str, User | str]
    tags: dict[str, int]
    cohorts: list
    status: int
    last_accessed: int
    is_locked: bool
    access: DatasetAccess
    preference: dict[str, bool | str]
    asset_statuses: dict[str, AssetStatusDetail]
    self_link: str
    etag: str
    localization: DatasetLocalization = DatasetLocalization.DATATURE_MULTI
    data_localization: DatasetLocalization = DatasetLocalization.DATATURE_MULTI
    description: str | None = None
    tag_details: dict[str, TagDetail] | None = None
    is_demo_project: bool = False
    delete_op: str | None = None
    bypass_quota: bool = False

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)

    def info(self) -> None:
        """Display rich information about this dataset.

        Shows a formatted summary of the dataset including statistics,
        access settings, tags, and other key information in an easy-to-read format.

        Example:
            ```python
            dataset = client.datasets.get("dataset_abc123")
            dataset.info()
            ```

        """
        create_date_str = datetime.fromtimestamp(self.create_date / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        last_accessed_str = datetime.fromtimestamp(self.last_accessed / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            Dataset Information                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Name:           {self.name}
   ID:             {self.dataset_id}
   Type:           {self.type.value if hasattr(self.type, "value") else self.type}
   Organization:   {self.organization_id}

📊 STATISTICS:
   Total Assets:       {self.statistic.asset_total:,}
   Annotated Assets:   {self.statistic.asset_annotated:,}
   Total Annotations:  {self.statistic.annotation_total:,}
   Annotation Rate:    {(self.statistic.asset_annotated / self.statistic.asset_total * 100) if self.statistic.asset_total > 0 else 0:.1f}%

🏷️  TAGS ({len(self.tags)}):
   {self._format_tags()}

📅 DATES:
   Created:        {create_date_str}
   Last Accessed:  {last_accessed_str}

💾 STORAGE:
   Localization:      {self.localization.value if hasattr(self.localization, "value") else self.localization}
   Data Location:     {self.data_localization.value if hasattr(self.data_localization, "value") else self.data_localization}

📝 DESCRIPTION:
   {self.description if self.description else "None"}

💡 QUICK ACTIONS:
   Download:     client.datasets.download("{self.dataset_id}")
   List Assets:  client.assets.list("{self.dataset_id}")
"""
        print(info_text)

    def _format_tags(self) -> str:
        """Format tags dictionary for display."""
        if not self.tags:
            return "   No tags"

        # Sort tags by count (descending) and get top 10
        sorted_tags = sorted(self.tags.items(), key=lambda x: x[1], reverse=True)[:10]
        tag_lines = [f"{name}: {count:,}" for name, count in sorted_tags]

        if len(self.tags) > 10:
            tag_lines.append(f"... and {len(self.tags) - 10} more")

        return "   " + "\n   ".join(tag_lines)


class DatasetExportFormat(Enum):
    """Dataset export format response."""

    VI_JSONL = "ViJsonl"
    VI_FULL = "ViFull"
    VI_TFRECORD = "ViTfrecord"


class DatasetExportOptions(ViResponse):
    """Dataset export options response.

    Attributes:
        normalized: Whether coordinates should be normalized (0-1 range).
        split_ratio: Optional ratio for train/val/test split (e.g., 0.8 for 80% training).

    """

    normalized: bool
    split_ratio: float | None = None


class DatasetExportSpec(ViResponse):
    """Dataset export spec response.

    Attributes:
        format: The export format (JSONL, Full, TFRecord).
        options: Export options including normalization and split settings.

    """

    format: DatasetExportFormat
    options: DatasetExportOptions


class DatasetExportDownloadUrl(ViResponse):
    """Dataset export download URL response.

    Attributes:
        url: The download URL for the exported dataset.
        expires_at: Unix timestamp when the download URL expires.

    """

    url: str
    expires_at: int


class DatasetExportStatus(ViResponse):
    """Dataset export status response.

    Attributes:
        conditions: List of resource conditions tracking export progress.
        download_url: Download URL information once export is ready, None if still processing.

    """

    conditions: list[ResourceCondition]
    download_url: DatasetExportDownloadUrl | None = None


class DatasetExport(ViResponse, tag_field="kind"):
    """Exported dataset response.

    Attributes:
        organization_id: Organization ID that owns this export.
        dataset_id: ID of the dataset being exported.
        dataset_export_id: Unique identifier for this export operation.
        spec: Export specification including format and options.
        status: Current status of the export operation.
        metadata: Resource metadata including timestamps.
        self_link: API link to this export resource.
        etag: Entity tag for caching and concurrency control.

    """

    organization_id: str = field(name="workspaceId")
    dataset_id: str
    dataset_export_id: str
    spec: DatasetExportSpec
    status: DatasetExportStatus
    metadata: ResourceMetadata
    self_link: str
    etag: str

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset ID.

        Removes organization ID prefix from the dataset_id field.
        """
        self.dataset_id = self._sanitize_dataset_id(self.dataset_id)


class BulkAssetDeletionStatus(ViResponse):
    """Bulk asset deletion status response.

    Attributes:
        conditions: List of resource conditions tracking deletion progress.

    """

    conditions: list[ResourceCondition]


class BulkAssetDeletionSession(ViResponse):
    """Bulk asset deletion session response.

    Attributes:
        kind: The resource kind identifier.
        organization_id: Organization ID.
        dataset_id: ID of the dataset containing the assets being deleted.
        delete_many_assets_session_id: Unique identifier for this deletion session.
        self_link: API link to this deletion session resource.
        etag: Entity tag for caching and concurrency control.
        metadata: Resource metadata including timestamps.
        spec: Deletion specification including filter criteria.
        status: Current status of the deletion operation.

    """

    kind: str
    organization_id: str = field(name="workspaceId")
    dataset_id: str
    delete_many_assets_session_id: str
    self_link: str
    etag: str
    metadata: ResourceMetadata
    spec: BulkAssetDeletionSpec
    status: BulkAssetDeletionStatus


class DeletedDatasetStatus(ViResponse):
    """Deleted dataset status response.

    Attributes:
        conditions: List of resource conditions tracking deletion progress.

    """

    conditions: list[ResourceCondition]


class DeletedDataset(ViResponse):
    """Deleted dataset response.

    Attributes:
        kind: The resource kind identifier.
        user: User ID who initiated the deletion.
        organization_id: Organization ID.
        dataset_id: ID of the deleted dataset.
        self_link: API link to this deletion operation resource.
        etag: Entity tag for caching and concurrency control.

    """

    kind: str
    user: str
    organization_id: str = field(name="workspaceId")
    dataset_id: str
    self_link: str
    etag: str
    metadata: ResourceMetadata
    status: DeletedDatasetStatus
