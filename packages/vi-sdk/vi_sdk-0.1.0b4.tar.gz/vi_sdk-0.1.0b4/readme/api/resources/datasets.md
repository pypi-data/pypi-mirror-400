---
title: "Datasets API Reference"
excerpt: "Dataset management, exports, downloads, and operations"
category: "api-reference"
---

# Datasets API Reference

Complete API reference for dataset operations. All dataset management, exports, downloads, and operations are handled through this resource.

---

## Dataset Resource

Access datasets through `client.datasets`.

---

## Methods

### list()

List all datasets in the organization.

```python
# Basic usage
datasets = client.datasets.list()

for dataset in datasets.items:
    print(f"{dataset.name}: {dataset.dataset_id}")
```

```python
# With custom pagination
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=50)
datasets = client.datasets.list(pagination=pagination)

# Iterate through all pages
for page in datasets:
    for dataset in page.items:
        print(f"{dataset.name}: {dataset.statistic.asset_total} assets")
```

```python
# Collect all datasets
all_datasets = list(client.datasets.list().all_items())
print(f"Total datasets: {len(all_datasets)}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams) | Pagination settings | `None` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Dataset`](#dataset)`]`

---

### get()

Get a specific dataset by ID.

```python
# Basic usage
dataset = client.datasets.get("dataset_abc123")

print(f"Name: {dataset.name}")
print(f"Assets: {dataset.statistic.asset_total}")
```

```python
# Display detailed information
dataset = client.datasets.get("dataset_abc123")
dataset.info()  # Prints formatted dataset summary
```

```python
# Access dataset statistics
dataset = client.datasets.get("dataset_abc123")

print(f"Total assets: {dataset.statistic.asset_total}")
print(f"Annotated: {dataset.statistic.asset_annotated}")
print(f"Annotations: {dataset.statistic.annotation_total}")

# Calculate annotation rate
if dataset.statistic.asset_total > 0:
    rate = dataset.statistic.asset_annotated / dataset.statistic.asset_total * 100
    print(f"Annotation rate: {rate:.1f}%")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |

**Returns:** [`Dataset`](#dataset)

---

### create_export()

Create a new dataset export.

```python
# Basic export with defaults
export = client.datasets.create_export(dataset_id="dataset_abc123")
```

```python
# Custom export settings
from vi.api.resources.datasets.types import (
    DatasetExportSettings,
    DatasetExportFormat,
    DatasetExportOptions
)

export_settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_FULL,
    options=DatasetExportOptions(
        normalized=True,
        split_ratio=0.8  # 80% training, 20% validation
    )
)

export = client.datasets.create_export(
    dataset_id="dataset_abc123",
    export_settings=export_settings
)

print(f"Export ID: {export.dataset_export_id}")
```

```python
# Export annotations only (JSONL format)
from vi.api.resources.datasets.types import (
    DatasetExportSettings,
    DatasetExportFormat
)

export_settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_JSONL
)

export = client.datasets.create_export(
    dataset_id="dataset_abc123",
    export_settings=export_settings
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `export_settings` | [`DatasetExportSettings`](#datasetexportsettings) | Export configuration |

**Returns:** [`DatasetExport`](#datasetexport)

---

### list_exports()

List exports for a dataset.

```python
# List all exports
exports = client.datasets.list_exports("dataset_abc123")

for export in exports.items:
    print(f"Export: {export.dataset_export_id}")
    print(f"  Format: {export.spec.format}")
```

```python
# Find ready exports with download URLs
exports = client.datasets.list_exports("dataset_abc123")

ready_exports = [
    e for e in exports.items
    if e.status.download_url is not None
]

for export in ready_exports:
    print(f"Export {export.dataset_export_id} ready: {export.status.download_url.url}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams) | Pagination settings |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`DatasetExport`](#datasetexport)`]`

---

### get_export()

Get a specific export.

```python
# Check export status
export = client.datasets.get_export(
    dataset_id="dataset_abc123",
    dataset_export_id="export_xyz789"
)

if export.status.download_url:
    print(f"Export ready: {export.status.download_url.url}")
    print(f"Expires at: {export.status.download_url.expires_at}")
else:
    print("Export still processing...")
```

```python
# Poll until export is ready
import time

def wait_for_export(dataset_id: str, export_id: str, timeout: int = 300) -> str:
    """Wait for export to be ready and return download URL."""
    start = time.time()
    while time.time() - start < timeout:
        export = client.datasets.get_export(dataset_id, export_id)
        if export.status.download_url:
            return export.status.download_url.url
        time.sleep(5)
    raise TimeoutError("Export not ready")

url = wait_for_export("dataset_abc123", "export_xyz789")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `dataset_export_id` | `str` | Export identifier |

**Returns:** [`DatasetExport`](#datasetexport)

---

### download()

Download a dataset.

```python
# Basic download
downloaded = client.datasets.download(
    dataset_id="dataset_abc123",
    save_dir="./data"
)

print(downloaded.summary())
```

```python
# Download with custom export settings
from vi.api.resources.datasets.types import (
    DatasetExportSettings,
    DatasetExportFormat,
    DatasetExportOptions
)

settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_FULL,
    options=DatasetExportOptions(
        normalized=True,
        split_ratio=0.8
    )
)

downloaded = client.datasets.download(
    dataset_id="dataset_abc123",
    export_settings=settings,
    save_dir="./data",
    show_progress=True
)

print(f"Saved to: {downloaded.save_dir}")
print(f"Size: {downloaded.size_mb:.2f} MB")
print(f"Splits: {downloaded.splits}")
```

```python
# Download annotations only
downloaded = client.datasets.download(
    dataset_id="dataset_abc123",
    save_dir="./annotations",
    annotations_only=True
)
```

```python
# Using the convenience method on client
downloaded = client.get_dataset(
    dataset_id="dataset_abc123",
    save_path="./data"
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `dataset_export_id` | `str` | Specific export ID | `None` |
| `export_settings` | [`DatasetExportSettings`](#datasetexportsettings) | Export configuration | `None` |
| `annotations_only` | `bool` | Download only annotations | `False` |
| `save_dir` | `str \| Path` | Save directory | Required |
| `overwrite` | `bool` | Overwrite existing | `False` |
| `show_progress` | `bool` | Show progress bars | `True` |

**Returns:** [`DatasetDownloadResult`](#datasetdownloadresult)

---

### delete()

Delete a dataset.

```python
# Delete a dataset
deleted = client.datasets.delete("dataset_abc123")
print(f"Deleted: {deleted.dataset_id}")
```

```python
# Delete with confirmation
dataset = client.datasets.get("dataset_abc123")
print(f"About to delete: {dataset.name}")
print(f"  Assets: {dataset.statistic.asset_total}")
print(f"  Annotations: {dataset.statistic.annotation_total}")

confirm = input("Delete? (yes/no): ")
if confirm.lower() == "yes":
    client.datasets.delete("dataset_abc123")
    print("Deleted.")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |

**Returns:** [`DeletedDataset`](#deleteddataset)

---

### bulk_delete_assets()

Bulk delete assets from a dataset.

```python
# Delete assets by status
response = client.datasets.bulk_delete_assets(
    dataset_id="dataset_abc123",
    filter_criteria='{"status": "error"}',
    strict_query=True
)
```

```python
# Delete unannotated assets
response = client.datasets.bulk_delete_assets(
    dataset_id="dataset_abc123",
    filter_criteria='{"metadata.annotations.total": 0}'
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `filter_criteria` | `str` | Filter query |
| `strict_query` | `bool` | Strict query mode |

**Returns:** [`BulkAssetDeletionSession`](#bulkassetdeletionsession)

---

## Response Types

### Dataset

Main dataset response object.

```python
from vi.api.resources.datasets.responses import Dataset
```

| Property | Type | Description |
|----------|------|-------------|
| `dataset_id` | `str` | Unique identifier |
| `name` | `str` | Dataset name |
| `owner` | `str` | Owner identifier |
| `organization_id` | `str` | Organization ID |
| `type` | [`DatasetType`](#datasettype) | Dataset type (phrase-grounding, vqa) |
| `content` | [`DatasetContent`](#datasetcontent) | Content type (Image) |
| `create_date` | `int` | Creation timestamp (Unix ms) |
| `statistic` | [`DatasetStatistic`](#datasetstatistic) | Dataset statistics |
| `users` | `dict[str, `[`User`](vi-sdk-types#user)` \| str]` | Users with access |
| `tags` | `dict[str, int]` | Tag counts |
| `status` | `int` | Status code |
| `last_accessed` | `int` | Last access timestamp |
| `is_locked` | `bool` | Lock status |
| `access` | [`DatasetAccess`](#datasetaccess) | Access settings |
| `asset_statuses` | `dict[str, `[`AssetStatusDetail`](#assetstatusdetail)`]` | Asset status definitions |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `description` | `str \| None` | Optional description |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted dataset information |

---

### DatasetStatistic

```python
from vi.api.resources.datasets.responses import DatasetStatistic
```

| Property | Type | Description |
|----------|------|-------------|
| `asset_total` | `int` | Total number of assets |
| `annotation_total` | `int` | Total number of annotations |
| `asset_annotated` | `int` | Number of annotated assets |
| `tags_count` | `dict[str, int]` | Tag distribution |

---

### DatasetAccess

```python
from vi.api.resources.datasets.responses import DatasetAccess
```

| Property | Type | Description |
|----------|------|-------------|
| `is_public` | `bool \| None` | Public accessibility |
| `is_read_only` | `bool \| None` | Read-only mode |
| `is_hidden` | `bool \| None` | Hidden from listings |

---

### AssetStatusDetail

```python
from vi.api.resources.datasets.responses import AssetStatusDetail
```

| Property | Type | Description |
|----------|------|-------------|
| `description` | `str` | Status description |
| `color` | `str` | Color code |
| `create_date` | `int \| None` | Creation timestamp |

---

### DatasetExport

```python
from vi.api.resources.datasets.responses import DatasetExport
```

| Property | Type | Description |
|----------|------|-------------|
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `dataset_export_id` | `str` | Export identifier |
| `spec` | [`DatasetExportSpec`](#datasetexportspec) | Export specification |
| `status` | [`DatasetExportStatus`](#datasetexportstatus) | Export status |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

---

### DatasetExportSpec

```python
from vi.api.resources.datasets.responses import DatasetExportSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `format` | [`DatasetExportFormat`](#datasetexportformat) | Export format |
| `options` | [`DatasetExportOptions`](#datasetexportoptions) | Export options |

---

### DatasetExportStatus

```python
from vi.api.resources.datasets.responses import DatasetExportStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[`[`ResourceCondition`](vi-sdk-types#resourcecondition)`]` | Status conditions |
| `download_url` | [`DatasetExportDownloadUrl`](#datasetexportdownloadurl)` \| None` | Download URL when ready |

---

### DatasetExportDownloadUrl

```python
from vi.api.resources.datasets.responses import DatasetExportDownloadUrl
```

| Property | Type | Description |
|----------|------|-------------|
| `url` | `str` | Download URL |
| `expires_at` | `int` | Expiration timestamp |

---

### DatasetDownloadResult

Result returned after downloading a dataset.

| Property | Type | Description |
|----------|------|-------------|
| `save_dir` | `Path` | Save directory |
| `size_mb` | `float` | Total size in MB |
| `splits` | `list[str]` | Available splits |
| `assets_count` | `int` | Number of assets |
| `annotations_count` | `int` | Number of annotations |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `summary()` | `str` | Get summary string |
| `info()` | `None` | Print detailed info |

---

### DeletedDataset

```python
from vi.api.resources.datasets.responses import DeletedDataset
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `user` | `str` | User who deleted |
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Deleted dataset ID |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `status` | [`DeletedDatasetStatus`](#deleteddatasetstatus) | Deletion status |

---

### DeletedDatasetStatus

```python
from vi.api.resources.datasets.responses import DeletedDatasetStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[`[`ResourceCondition`](vi-sdk-types#resourcecondition)`]` | Deletion conditions |

---

### BulkAssetDeletionSession

```python
from vi.api.resources.datasets.responses import BulkAssetDeletionSession
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `delete_many_assets_session_id` | `str` | Session identifier |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `spec` | [`BulkAssetDeletionSpec`](#bulkassetdeletionspec) | Deletion spec |
| `status` | [`BulkAssetDeletionStatus`](#bulkassetdeletionstatus) | Deletion status |

---

### BulkAssetDeletionSpec

```python
from vi.api.resources.datasets.types import BulkAssetDeletionSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `filter` | `str \| dict \| None` | Filter criteria |
| `metadata_query` | `str \| None` | Metadata query |
| `rule_query` | `str \| None` | Rule query |
| `strict_query` | `bool \| None` | Strict query mode |

---

### BulkAssetDeletionStatus

```python
from vi.api.resources.datasets.responses import BulkAssetDeletionStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[`[`ResourceCondition`](vi-sdk-types#resourcecondition)`]` | Deletion conditions |

---

## Request Types

### DatasetExportSettings

```python
from vi.api.resources.datasets.types import DatasetExportSettings
```

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `format` | [`DatasetExportFormat`](#datasetexportformat) | Export format | `VI_FULL` |
| `options` | [`DatasetExportOptions`](#datasetexportoptions) | Export options | `DatasetExportOptions()` |

---

### DatasetExportOptions

```python
from vi.api.resources.datasets.types import DatasetExportOptions
```

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `normalized` | `bool` | Normalize coordinates | `True` |
| `split_ratio` | `float \| None` | Train/validation split ratio | `None` |

---

## Enums

### DatasetType

```python
from vi.api.resources.datasets.types import DatasetType
```

| Value | Description |
|-------|-------------|
| `PHRASE_GROUNDING` | Phrase grounding dataset |
| `VQA` | Visual question answering dataset |

---

### DatasetContent

```python
from vi.api.resources.datasets.types import DatasetContent
```

| Value | Description |
|-------|-------------|
| `IMAGE` | Image content |

---

### DatasetExportFormat

```python
from vi.api.resources.datasets.types import DatasetExportFormat
```

| Value | Description |
|-------|-------------|
| `VI_FULL` | Full dataset with assets |
| `VI_JSONL` | JSONL format annotations |

---

## See Also

- [Working with Datasets Guide](vi-sdk-datasets) - Comprehensive guide
- [Assets API](vi-sdk-assets-api) - Asset operations
- [Annotations API](vi-sdk-annotations-api) - Annotation operations
- [Dataset Loaders](vi-sdk-api-dataset-loaders) - Loading downloaded datasets
- [Types API](vi-sdk-types) - Common types
- [Pagination API](vi-sdk-pagination) - Pagination utilities
