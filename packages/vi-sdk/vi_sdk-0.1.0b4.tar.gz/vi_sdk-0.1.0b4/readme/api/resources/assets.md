---
title: "Assets API Reference"
excerpt: "Manage image uploads, downloads, and asset lifecycle"
category: "api-reference"
---

# Assets API Reference

Complete API reference for asset operations. Manage image uploads, downloads, metadata, and asset lifecycle through this resource.

---

## Asset Resource

Access assets through `client.assets`.

---

## Methods

### list()

List assets in a dataset.

```python
# Basic listing
assets = client.assets.list(dataset_id="dataset_abc123")

for asset in assets.items:
    print(f"{asset.filename}: {asset.metadata.width}x{asset.metadata.height}")
```

```python
# With pagination and sorting
from vi.api.types import PaginationParams
from vi.api.resources.datasets.assets.types import (
    AssetSortCriterion,
    SortCriterion,
    SortOrder
)

pagination = PaginationParams(page_size=100)
sort_by = AssetSortCriterion(
    criterion=SortCriterion.FILENAME,
    order=SortOrder.ASC
)

for page in client.assets.list(
    dataset_id="dataset_abc123",
    pagination=pagination,
    sort_by=sort_by
):
    for asset in page.items:
        print(f"{asset.filename}")
```

```python
# Get assets with download URLs
assets = client.assets.list(
    dataset_id="dataset_abc123",
    contents=True
)

for asset in assets.items:
    if asset.contents and asset.contents.asset:
        print(f"{asset.filename}: {asset.contents.asset.url}")
```

```python
# Filter by metadata
assets = client.assets.list(
    dataset_id="dataset_abc123",
    metadata_query='custom_field == "value"'
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams) | Pagination settings | `None` |
| `contents` | `bool` | Include download URLs | `False` |
| `sort_by` | [`AssetSortCriterion`](#assetsortcriterion) | Sorting criteria | `None` |
| `filter_criteria` | `str` | Filter query | `None` |
| `metadata_query` | `str` | Metadata query | `None` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Asset`](#asset)`]`

---

### get()

Get a specific asset.

```python
# Basic usage
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

print(f"Filename: {asset.filename}")
print(f"Size: {asset.metadata.file_size} bytes")
```

```python
# Get with download URL
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    contents=True
)

if asset.contents and asset.contents.asset:
    print(f"Download URL: {asset.contents.asset.url}")
    print(f"Expires: {asset.contents.asset.expiry}")
```

```python
# Display detailed information
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)
asset.info()  # Prints formatted asset summary
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `asset_id` | `str` | Asset identifier | Required |
| `contents` | `bool` | Include download URL | `False` |

**Returns:** [`Asset`](#asset)

---

### upload()

Upload assets to a dataset.

```python
# Upload single file
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="image.jpg",
    wait_until_done=True
)

print(f"Uploaded: {result.total_succeeded}")
```

```python
# Upload entire folder
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    wait_until_done=True
)

print(f"✓ Uploaded: {result.total_succeeded}")
print(f"✗ Failed: {result.total_failed}")
print(result.summary())
```

```python
# Upload multiple specific files
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths=["image1.jpg", "image2.png", "image3.webp"],
    wait_until_done=True
)
```

```python
# Upload with error handling
from vi import ViUploadError, ViFileTooLargeError

try:
    result = client.assets.upload(
        dataset_id="dataset_abc123",
        paths="./images/",
        wait_until_done=True
    )

    print(f"✓ Uploaded: {result.total_succeeded}")
    print(f"✗ Failed: {result.total_failed}")

    if result.failed_files:
        print("Failed files:")
        for f in result.failed_files:
            print(f"  - {f}")

except ViFileTooLargeError as e:
    print(f"File too large: {e.message}")
except ViUploadError as e:
    print(f"Upload failed: {e.message}")
```

```python
# Async upload (don't wait)
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./large_folder/",
    wait_until_done=False
)

# Get session IDs for later status check
print(f"Session IDs: {result.session_ids}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `paths` | `str \| list[str]` | File/folder paths | Required |
| `wait_until_done` | `bool` | Wait for completion | `True` |
| `failure_mode` | [`FailureMode`](#failuremode) | Failure handling | `"FailAfterOne"` |
| `on_asset_overwritten` | [`ResourceRetentionMode`](#resourceretentionmode) | Overwrite behavior | `"RemoveLinkedResource"` |

**Returns:** [`AssetUploadResult`](#assetuploadresult)

---

### download()

Download assets from a dataset.

```python
# Basic download
downloaded = client.assets.download(
    dataset_id="dataset_abc123",
    save_dir="./assets"
)
```

```python
# Download with progress and overwrite
downloaded = client.assets.download(
    dataset_id="dataset_abc123",
    save_dir="./assets",
    overwrite=True,
    show_progress=True
)

print(f"Downloaded to: {downloaded}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `save_dir` | `str \| Path` | Save directory | Required |
| `overwrite` | `bool` | Overwrite existing | `False` |
| `show_progress` | `bool` | Show progress bars | `True` |

**Returns:** `AssetDownloadResult`

---

### delete()

Delete an asset.

```python
# Delete single asset
deleted = client.assets.delete(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)
```

```python
# Delete multiple assets
asset_ids = ["asset_1", "asset_2", "asset_3"]

for asset_id in asset_ids:
    client.assets.delete(
        dataset_id="dataset_abc123",
        asset_id=asset_id
    )
    print(f"Deleted: {asset_id}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `asset_id` | `str` | Asset identifier |

**Returns:** `DeletedAsset`

---

### wait_until_done()

Wait for an upload session to complete.

```python
# Basic usage
status = client.assets.wait_until_done(
    dataset_id="dataset_abc123",
    asset_ingestion_session_id="session_id"
)

print(f"Succeeded: {status.status.progressCount.succeeded}")
print(f"Failed: {status.status.progressCount.errored}")
```

```python
# After async upload
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    wait_until_done=False
)

# Do other work...

# Then wait for completion
for session_id in result.session_ids:
    status = client.assets.wait_until_done(
        dataset_id="dataset_abc123",
        asset_ingestion_session_id=session_id
    )
    print(f"Session {session_id}: {status.status.progressCount.succeeded} succeeded")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `asset_ingestion_session_id` | `str` | Session identifier |

**Returns:** [`AssetIngestionSession`](#assetingestionsession)

---

## Response Types

### Asset

Main asset response object.

```python
from vi.api.resources.datasets.assets.responses import Asset
```

| Property | Type | Description |
|----------|------|-------------|
| `asset_id` | `str` | Unique identifier |
| `dataset_id` | `str` | Parent dataset ID |
| `organization_id` | `str` | Organization ID |
| `filename` | `str` | Original filename |
| `kind` | `str` | Resource kind |
| `owner` | `str` | Owner identifier |
| `metadata` | [`AssetMetadata`](#assetmetadata) | Asset metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `contents` | [`AssetContents`](#assetcontents)` \| None` | Download URLs (if requested) |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted asset information |

---

### AssetMetadata

```python
from vi.api.resources.datasets.assets.responses import AssetMetadata
```

| Property | Type | Description |
|----------|------|-------------|
| `width` | `int` | Image width in pixels |
| `height` | `int` | Image height in pixels |
| `file_size` | `int` | File size in bytes |
| `mime_type` | `str` | MIME type |
| `upload_status` | `str` | Upload status |
| `status` | `str` | Processing status |
| `frames` | `int` | Number of frames |
| `visibility` | `str` | Visibility setting |
| `generations` | [`AssetGenerations`](#assetgenerations) | Asset URLs |
| `annotations` | [`AssetAnnotations`](#assetannotations) | Annotation info |
| `dimensions` | [`AssetDimensions`](#assetdimensions) | Dimension details |
| `pixel_ratio` | [`AssetPixelRatio`](#assetpixelratio) | Pixel ratio |
| `hash` | [`AssetHash`](#assethash) | File hash |
| `inserted_by` | `str` | Uploader ID |
| `cohorts` | `list[str]` | Cohort IDs |
| `user_defined` | `dict[str, Any]` | User metadata |
| `custom_metadata` | [`AssetCustomMetadata`](#assetcustommetadata) | Custom metadata |
| `comments` | `int` | Comment count |
| `time_created` | `int` | Creation timestamp |
| `last_updated` | `int` | Update timestamp |

---

### AssetGenerations

```python
from vi.api.resources.datasets.assets.responses import AssetGenerations
```

| Property | Type | Description |
|----------|------|-------------|
| `asset` | `str` | Full-size asset URL |
| `thumbnail` | `str` | Thumbnail URL |

---

### AssetAnnotations

```python
from vi.api.resources.datasets.assets.responses import AssetAnnotations
```

| Property | Type | Description |
|----------|------|-------------|
| `with_tag` | `dict[str, int]` | Tag counts |
| `total` | `int` | Total annotations |

---

### AssetDimensions

```python
from vi.api.resources.datasets.assets.responses import AssetDimensions
```

| Property | Type | Description |
|----------|------|-------------|
| `height` | `int` | Height in pixels |
| `width` | `int` | Width in pixels |
| `depth` | `int \| None` | Depth (for 3D) |

---

### AssetPixelRatio

```python
from vi.api.resources.datasets.assets.responses import AssetPixelRatio
```

| Property | Type | Description |
|----------|------|-------------|
| `height` | `int` | Height ratio |
| `width` | `int` | Width ratio |
| `depth` | `int \| None` | Depth ratio |

---

### AssetHash

```python
from vi.api.resources.datasets.assets.responses import AssetHash
```

| Property | Type | Description |
|----------|------|-------------|
| `algorithm` | `str` | Hash algorithm (e.g., 'sha256') |
| `contents` | `str` | Hash value |

---

### AssetContents

```python
from vi.api.resources.datasets.assets.responses import AssetContents
```

| Property | Type | Description |
|----------|------|-------------|
| `asset` | [`Contents`](#contents)` \| None` | Full asset URL info |
| `thumbnail` | [`Contents`](#contents)` \| None` | Thumbnail URL info |

---

### Contents

```python
from vi.api.resources.datasets.assets.responses import Contents
```

| Property | Type | Description |
|----------|------|-------------|
| `url` | `str` | Pre-signed URL |
| `expiry` | `int` | Expiration timestamp |
| `headers` | `dict[str, str] \| None` | Required headers |
| `method` | `str \| None` | HTTP method |

---

### AssetUploadResult

Aggregates results from batched uploads.

| Property | Type | Description |
|----------|------|-------------|
| `total_files` | `int` | Total files processed |
| `total_succeeded` | `int` | Successfully uploaded |
| `total_failed` | `int` | Failed uploads |
| `success_rate` | `float` | Success percentage |
| `sessions` | `list[`[`AssetIngestionSession`](#assetingestionsession)`]` | Batch sessions |
| `session_ids` | `list[str]` | Session IDs |
| `failed_files` | `list[str]` | Failed file paths |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `summary()` | `str` | Get summary string |

---

### AssetIngestionSession

```python
from vi.api.resources.datasets.assets.responses import AssetIngestionSession
```

| Property | Type | Description |
|----------|------|-------------|
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `asset_ingestion_session_id` | `str` | Session identifier |
| `asset_source_class` | `str` | Source classification |
| `asset_source_provider` | `str` | Source provider |
| `asset_source_id` | `str` | Source identifier |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `spec` | [`AssetIngestionSessionSpec`](#assetingestionsessionspec) | Session spec |
| `status` | [`AssetIngestionSessionStatus`](#assetingestionsessionstatus) | Session status |

---

### AssetIngestionSessionSpec

```python
from vi.api.resources.datasets.assets.responses import AssetIngestionSessionSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `failureMode` | [`FailureMode`](#failuremode) | Failure handling |
| `onAssetOverwritten` | [`ResourceRetentionMode`](#resourceretentionmode) | Overwrite handling |
| `assets` | `list[`[`UploadedAssetMetadata`](#uploadedassetmetadata)`] \| None` | Assets being uploaded |

---

### AssetIngestionSessionStatus

```python
from vi.api.resources.datasets.assets.responses import AssetIngestionSessionStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[`[`ResourceCondition`](vi-sdk-types#resourcecondition)`]` | Status conditions |
| `events` | `list[`[`AssetIngestionEvent`](#assetingestionevent)`]` | Ingestion events |
| `progressCount` | [`AssetIngestionProgressCount`](#assetingestionprogresscount) | Progress stats |
| `assets` | `list[`[`AssetForUpload`](#assetforupload)`] \| None` | Assets being uploaded |

---

### AssetIngestionProgressCount

```python
from vi.api.resources.datasets.assets.responses import AssetIngestionProgressCount
```

| Property | Type | Description |
|----------|------|-------------|
| `total` | `int` | Total assets |
| `succeeded` | `int` | Succeeded |
| `errored` | `int` | Errored |

---

### AssetIngestionEvent

Union type for ingestion events.

```python
AssetIngestionEvent = AssetIngestionEventError | AssetIngestionEventProgress
```

---

### UploadedAssetMetadata

```python
from vi.api.resources.datasets.assets.responses import UploadedAssetMetadata
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `filename` | `str` | File name |
| `mime` | `str` | MIME type |
| `size` | `int` | Size in bytes |
| `crc32c` | `int \| None` | CRC32C checksum |
| `custom_metadata` | [`AssetCustomMetadata`](#assetcustommetadata)` \| None` | Custom metadata |

---

### AssetForUpload

```python
from vi.api.resources.datasets.assets.responses import AssetForUpload
```

| Property | Type | Description |
|----------|------|-------------|
| `metadata` | [`UploadedAssetMetadata`](#uploadedassetmetadata) | Asset metadata |
| `upload` | [`Contents`](#contents) | Upload URL info |

---

## Request Types

### AssetSortCriterion

```python
from vi.api.resources.datasets.assets.types import AssetSortCriterion
```

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `criterion` | [`SortCriterion`](#sortcriterion) | Sort field | Required |
| `order` | [`SortOrder`](#sortorder) | Sort direction | `ASC` |

---

### AssetCustomMetadata

```python
from vi.api.resources.datasets.assets.types import AssetCustomMetadata

# Type alias
AssetCustomMetadata = dict[str, str | int | float | bool]
```

Custom metadata dictionary with string keys and primitive values.

---

## Enums

### SortCriterion

```python
from vi.api.resources.datasets.assets.types import SortCriterion
```

| Value | Description |
|-------|-------------|
| `DEFAULT` | Default sorting |
| `ASSET_ID` | Sort by asset ID |
| `FILENAME` | Sort by filename |
| `LAST_MODIFIED_CONTENTS` | Sort by last modified |
| `METADATA_FILE_SIZE` | Sort by file size |

---

### SortOrder

```python
from vi.api.resources.datasets.assets.types import SortOrder
```

| Value | Description |
|-------|-------------|
| `ASC` | Ascending order |
| `DESC` | Descending order |

---

### FailureMode

```python
from vi.api.resources.datasets.assets.responses import FailureMode
```

| Value | Description |
|-------|-------------|
| `FAIL_AFTER_ONE` | Stop on first error |
| `FAIL_AFTER_ALL` | Continue and report all errors |

---

### ResourceRetentionMode

```python
from vi.api.resources.datasets.assets.responses import ResourceRetentionMode
```

| Value | Description |
|-------|-------------|
| `REMOVE_LINKED_RESOURCE` | Remove linked annotations |
| `KEEP_LINKED_RESOURCES` | Keep linked annotations |

---

### AssetIngestionError

```python
from vi.api.resources.datasets.assets.responses import AssetIngestionError
```

| Value | Description |
|-------|-------------|
| `EALREADY` | Asset already exists |
| `EBADMIME` | Invalid MIME type |
| `EBADSIZE` | Invalid file size |
| `ECORRUPT` | Corrupted file |
| `ENOQUOTA` | Quota exceeded |
| `ETIMEOUT` | Upload timeout |
| `EUNKNOWN` | Unknown error |

---

## Supported File Formats

| Format | Extensions |
|--------|------------|
| JPEG | `.jpg`, `.jpeg`, `.jfif` |
| PNG | `.png` |
| TIFF | `.tiff`, `.tif` |
| BMP | `.bmp` |
| WebP | `.webp` |
| HEIF | `.heif`, `.heic` |
| AVIF | `.avif` |
| JPEG 2000 | `.jp2`, `.j2k` |
| GIF | `.gif` |

---

## See Also

- [Managing Assets Guide](vi-sdk-assets) - Comprehensive guide
- [Datasets API](vi-sdk-datasets-api) - Dataset operations
- [Annotations API](vi-sdk-annotations-api) - Annotation operations
- [Types API](vi-sdk-types) - Common types
- [Pagination API](vi-sdk-pagination) - Pagination utilities
