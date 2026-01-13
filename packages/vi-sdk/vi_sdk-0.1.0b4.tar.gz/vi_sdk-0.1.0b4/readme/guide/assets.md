---
title: "Managing Assets"
excerpt: "Upload, download, and manage assets in your datasets"
category: "guide"
---

# Managing Assets

Learn how to upload, download, and manage assets (images and media files) in your datasets.

---

## Overview

Assets are the media files (images, videos, etc.) in your datasets. The Vi SDK provides powerful tools for:

- Uploading single files or entire folders
- Concurrent batch uploads for speed
- Downloading assets efficiently
- Listing and filtering assets
- Managing asset metadata
- Bulk operations

---

## Supported File Formats

### Images

Vi supports all major image formats:

- JPEG (`.jpg`, `.jpeg`, `.jfif`)
- PNG (`.png`)
- TIFF (`.tiff`, `.tif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- HEIF/HEIC (`.heif`, `.heic`)
- AVIF (`.avif`)
- JPEG 2000 (`.jp2`, `.j2k`)
- GIF (`.gif`)

---

## Uploading Assets

### Upload Single File

```python
import vi

client = vi.Client()

# Upload one image
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="path/to/image.jpg",
    wait_until_done=True
)

print(f"✓ Upload complete!")
print(f"Uploaded: {result.total_succeeded} assets")
print(result.summary())  # Shows detailed upload summary
```

### Upload Multiple Files

```python
# List of files
files = [
    "image1.jpg",
    "image2.jpg",
    "image3.jpg"
]

result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths=files,
    wait_until_done=True
)

print(f"Uploaded {result.total_succeeded} assets")
print(result.summary())  # Shows detailed upload summary
```

### Upload Entire Folder

```python
# Upload all images in a folder (recursive)
# Large folders are automatically split into batches for optimal performance
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    wait_until_done=True
)

print(f"Uploaded {result.total_succeeded}/{result.total_files} assets")
print(f"Success rate: {result.success_rate:.1f}%")
print(result.summary())  # Shows detailed upload summary
```

### Upload Without Waiting

```python
# Start upload and return immediately
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    wait_until_done=False  # Don't wait for completion
)

# Access session IDs for later status checks
print(f"Started {len(result.sessions)} batch(es)")
for session_id in result.session_ids:
    print(f"  Session: {session_id}")
```

### Check Upload Status

```python
# For async uploads (wait_until_done=False), check status later
for session_id in result.session_ids:
    status = client.assets.wait_until_done(
        dataset_id="dataset_abc123",
        asset_ingestion_session_id=session_id
    )
    print(f"Batch {session_id}:")
    print(f"  Total: {status.status.progressCount.total}")
    print(f"  Succeeded: {status.status.progressCount.succeeded}")
    print(f"  Failed: {status.status.progressCount.errored}")
```

---

## Upload Options

> 📘 **Batched Uploads**
>
> The SDK automatically splits large uploads into batches of 10000 files each. The `upload()` method returns an `AssetUploadResult` wrapper that aggregates statistics across all batches, providing convenient access to total counts and success rates. Access underlying batch sessions via `result.sessions` if needed.

### Failure Mode

Control how upload failures are handled:

```python
# Stop after first failure
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    failure_mode="FailAfterOne"  # Stop on first error
)

# Continue after failures (non-default)
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    failure_mode="FailAfterAll"  # Process all files instead of stopping on first error
)
```

### Asset Overwrite Behavior

```python
# Remove linked resources when overwriting (default)
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    on_asset_overwritten="RemoveLinkedResource"
)

# Keep linked resources
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    on_asset_overwritten="KeepLinkedResource"
)
```

---

## Listing Assets

### List All Assets

```python
# Get first page
assets = client.assets.list(
    dataset_id="dataset_abc123"
)

for asset in assets.items:
    print(f"📷 {asset.filename}")
    print(f"   ID: {asset.asset_id}")
    print(f"   Size: {asset.metadata.width}x{asset.metadata.height}")
```

### Iterate All Pages

```python
# Automatic pagination
for page in client.assets.list(dataset_id="dataset_abc123"):
    for asset in page.items:
        print(f"Processing: {asset.filename}")
```

### Custom Page Size

```python
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=100)
assets = client.assets.list(
    dataset_id="dataset_abc123",
    pagination=pagination
)
```

### List with Download URLs

```python
# Include download URLs in response
assets = client.assets.list(
    dataset_id="dataset_abc123",
    contents=True  # Include download URLs
)

for asset in assets.items:
    if asset.contents and asset.contents.asset:
        print(f"{asset.filename}: {asset.contents.asset.url}")
```

### Sorting Assets

```python
from vi.api.resources.datasets.assets.types import (
    AssetSortCriterion,
    SortCriterion,
    SortOrder
)

# Sort by filename ascending
sort_by = AssetSortCriterion(
    criterion=SortCriterion.FILENAME,
    order=SortOrder.ASC
)

assets = client.assets.list(
    dataset_id="dataset_abc123",
    sort_by=sort_by
)

# Sort by file size descending
sort_by = AssetSortCriterion(
    criterion=SortCriterion.METADATA_FILE_SIZE,
    order=SortOrder.DESC
)

assets = client.assets.list(
    dataset_id="dataset_abc123",
    sort_by=sort_by
)
```

---

## Getting Asset Details

### Get Single Asset

```python
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

print(f"Filename: {asset.filename}")
print(f"Size: {asset.metadata.width}x{asset.metadata.height}")
print(f"File size: {asset.metadata.file_size:,} bytes")
print(f"MIME type: {asset.metadata.mime_type}")
print(f"Upload status: {asset.metadata.upload_status}")
```

### Get with Download URL

```python
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    contents=True  # Include download URL
)

if asset.contents and asset.contents.asset:
    print(f"Download URL: {asset.contents.asset.url}")
    print(f"Expires: {asset.contents.asset.expiry}")
```

---

## Downloading Assets

### Download All Assets

```python
# Download all assets in a dataset
downloaded = client.assets.download(
    dataset_id="dataset_abc123",
    save_dir="./assets"
)

print(f"Downloaded to: {downloaded.save_dir}")
```

### Download with Options

```python
downloaded = client.assets.download(
    dataset_id="dataset_abc123",
    save_dir="./assets",
    overwrite=True,  # Overwrite existing files
    show_progress=True  # Show progress bars
)
```

### Download Without Progress

```python
# For CI/CD or scripts
downloaded = client.assets.download(
    dataset_id="dataset_abc123",
    save_dir="./assets",
    show_progress=False
)
```

---

## Deleting Assets

### Delete Single Asset

```python
deleted = client.assets.delete(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

print(f"Deleted: {deleted.deleted}")
```

### Delete Multiple Assets

```python
# Get assets to delete
assets_to_delete = client.assets.list(
    dataset_id="dataset_abc123",
    filter_criteria='{"status": "error"}'
)

# Delete each one
for asset in assets_to_delete.items:
    try:
        client.assets.delete(
            dataset_id="dataset_abc123",
            asset_id=asset.asset_id
        )
        print(f"✓ Deleted {asset.filename}")
    except Exception as e:
        print(f"✗ Failed to delete {asset.filename}: {e}")
```

### Bulk Delete

```python
# Use bulk delete for efficiency
response = client.datasets.bulk_delete_assets(
    dataset_id="dataset_abc123",
    filter_criteria='{"status": "error"}',
    strict_query=True
)
```

---

## Working with Asset Metadata

### Access Basic Metadata

```python
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

metadata = asset.metadata
print(f"Width: {metadata.width}")
print(f"Height: {metadata.height}")
print(f"File size: {metadata.file_size:,} bytes")
print(f"MIME type: {metadata.mime_type}")
print(f"Frames: {metadata.frames}")
```

### Access Annotation Information

```python
annotations_info = asset.metadata.annotations
print(f"Total annotations: {annotations_info.total}")

# Annotations by tag
for tag, count in annotations_info.with_tag.items():
    print(f"Tag '{tag}': {count} annotations")
```

---

## Best Practices

### 1. Batch Upload for Speed

```python
# ✅ Good - upload entire folder at once
# SDK automatically batches files for optimal performance
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",  # Folder
    wait_until_done=True
)
print(f"✓ Uploaded: {result.total_succeeded} assets")
print(result.summary())

# ❌ Bad - upload files one by one
for file in files:
    client.assets.upload(
        dataset_id="dataset_abc123",
        paths=file
    )
```

### 2. Handle Upload Errors

```python
from vi import ViUploadError, ViFileTooLargeError

try:
    result = client.assets.upload(
        dataset_id="dataset_abc123",
        paths="./images/"
    )
    # Check for errors using result properties
    if result.total_failed > 0:
        print(f"⚠️  {result.total_failed} files failed to upload")
        # Access failed file paths if available
        if result.failed_files:
            for failed_file in result.failed_files:
                print(f"  - {failed_file}")
except ViFileTooLargeError as e:
    print(f"File too large: {e.message}")
    # Resize images
except ViUploadError as e:
    print(f"Upload failed: {e.message}")
    # Retry or check network
```

### 3. Verify Upload Success

```python
result = client.assets.upload(
    dataset_id="dataset_abc123",
    paths="./images/",
    wait_until_done=True
)

# Check aggregated statistics
if result.total_failed > 0:
    print(f"⚠️  {result.total_failed} uploads failed")

    # Access failed file paths
    if result.failed_files:
        print("Failed files:")
        for failed_file in result.failed_files:
            print(f"  - {failed_file}")

# Display summary
print(f"✓ Total: {result.total_succeeded} succeeded, {result.total_failed} failed")
print(f"Success rate: {result.success_rate:.1f}%")
print(result.summary())  # Rich formatted output
```

---

## Common Workflows

### Upload and Verify

```python
def upload_and_verify(dataset_id, folder_path):
    """Upload folder and verify all files succeeded."""
    # Count local files
    from pathlib import Path
    local_files = list(Path(folder_path).glob("**/*.jpg"))
    local_count = len(local_files)

    # Upload
    result = client.assets.upload(
        dataset_id=dataset_id,
        paths=folder_path,
        wait_until_done=True
    )

    # Check aggregated results
    print(f"Local files: {local_count}")
    print(f"Uploaded: {result.total_succeeded} across {len(result.sessions)} batch(es)")
    print(f"Failed: {result.total_failed}")
    print(f"Success rate: {result.success_rate:.1f}%")

    if result.total_succeeded == local_count:
        print("✓ All files uploaded successfully")
        return True
    else:
        print("✗ Some files failed to upload")
        return False
```

---

## Troubleshooting

### Upload Fails Silently

Check the ingestion session status:

```python
status = client.assets.wait_until_done(
    dataset_id="dataset_abc123",
    asset_ingestion_session_id=session_id
)

# Check for errors
if status.status.progressCount.errored > 0:
    for event in status.status.events:
        if hasattr(event, 'files'):
            print("Errors:")
            for file, error in event.files.items():
                print(f"  {file}: {error}")
```

### Asset Not Appearing

Assets may take time to process:

1. Check upload status
2. Wait a few seconds
3. Refresh asset list

### Download URL Expired

Download URLs expire after a certain time:

```python
# Get fresh download URL
asset = client.assets.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    contents=True  # Get new URL
)
```

---

## Performance Tips

- **Batch uploads**: Upload folders instead of individual files
- **Concurrent downloads**: Assets download happens in parallel automatically
- **Filter server-side**: Use query parameters instead of filtering locally
- **Cache downloads**: Check if files exist before downloading

---

## See Also

- [Datasets Guide](vi-sdk-datasets) - Managing parent datasets
- [Annotations Guide](vi-sdk-annotations) - Adding annotations to assets
- [API Reference](vi-sdk-assets-api) - Complete API documentation
