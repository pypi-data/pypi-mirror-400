# Asset Upload and Download

This example demonstrates how to upload and download assets using the Vi SDK.

## Overview

Learn how to:

- Upload individual images
- Upload folders of images in batches
- List and filter assets
- Download assets
- Track upload/download progress

## Source Code

[View full source on GitHub](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/examples/02_asset_upload_download.py)

## Code Walkthrough

### 1. Initialize the Client

```python
import vi

client = vi.Client(
    secret_key="YOUR_DATATURE_VI_SECRET_KEY",
    organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
)
```

### 2. Upload a Single Image

```python
# Upload a single image file
# Note: upload() returns an AssetUploadResult wrapper with statistics
result = client.assets.upload(
    dataset_id=dataset_id,
    paths="path/to/image.jpg",
    wait_until_done=True,
)

# Access convenient properties
print(f"✓ Uploaded: {result.total_succeeded} assets")
print(f"Failed: {result.total_failed}")
print(result.summary())  # Rich formatted output
```

### 3. Upload a Folder of Images

```python
# Upload all images in a folder
# Large uploads are automatically split into batches
result = client.assets.upload(
    dataset_id=dataset_id,
    paths="./images/",  # Path to folder
    wait_until_done=True,
)

# Access aggregated statistics
print(f"Total files: {result.total_files}")
print(f"Succeeded: {result.total_succeeded}")
print(f"Failed: {result.total_failed}")
print(f"Success rate: {result.success_rate:.1f}%")
print(result.summary())  # Rich formatted output
```

### 4. List Assets

```python
from vi.api.types import PaginationParams

# List assets with pagination
pagination = PaginationParams(page_size=10)
assets = client.assets.list(
    dataset_id=dataset_id,
    pagination=pagination
)

for asset in assets.items:
    print(f"Filename: {asset.filename}")
    print(f"ID: {asset.asset_id}")
    print(f"Size: {asset.metadata.width}x{asset.metadata.height}")
    print(f"File size: {asset.metadata.file_size:,} bytes")
    print(f"Annotations: {asset.metadata.annotations.total}")
```

### 5. Get Asset with Download URL

```python
# Get asset with download URL
asset_with_content = client.assets.get(
    dataset_id=dataset_id,
    asset_id=asset_id,
    contents=True  # Include download URL
)

if asset_with_content.contents and asset_with_content.contents.asset:
    download_url = asset_with_content.contents.asset.url
    expiry = asset_with_content.contents.asset.expiry
    print(f"Download URL expires at: {expiry}")
```

### 6. Download All Assets

```python
from pathlib import Path

# Download all assets from a dataset
download_dir = Path("./downloaded_assets")

downloaded = client.assets.download(
    dataset_id=dataset_id,
    save_dir=download_dir,
    overwrite=False,  # Skip existing files
    show_progress=True,
)

print(f"Downloaded to: {downloaded.save_dir}")
```

### 7. Filter Assets

```python
# Find large assets (>1MB)
large_assets = []

for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        if asset.metadata.file_size > 1024 * 1024:  # 1MB
            large_assets.append(asset)

print(f"Found {len(large_assets)} large assets")
```

## Running the Example

### Prerequisites

```bash
# Install Vi SDK
pip install vi-sdk

# Prepare some sample images
mkdir sample_images
# Add some .jpg or .png files to sample_images/
```

### Execute

```bash
python3 02_asset_upload_download.py
```

## Expected Output

```
📡 Initializing Vi SDK client...

📊 Finding a dataset to work with...
   ✓ Using dataset: My Dataset (dataset_xyz789)

🎨 Creating 5 sample images...
   ✓ Created: sample_001.jpg
   ✓ Created: sample_002.jpg
   ✓ Created: sample_003.jpg
   ✓ Created: sample_004.jpg
   ✓ Created: sample_005.jpg

📤 Uploading single image...
   ✓ Uploaded: 1 assets
   Failed: 0

   Asset Upload Summary
   ━━━━━━━━━━━━━━━━━━━━
   Total Files:     1
   Succeeded:       1
   Failed:          0
   Success Rate:    100.0%

📤 Uploading folder of images...
   ✓ Upload complete!
   Total files: 5
   Succeeded: 5
   Failed: 0
   Success rate: 100.0%

📋 Listing assets in dataset...
   Found 10 assets (first page):

   1. sample_001.jpg
      ID: asset_001
      Size: 800x600
      File size: 45,678 bytes
      Annotations: 0
      Upload status: completed

⬇️  Downloading all assets from dataset...
   ✓ Assets downloaded successfully!
   Location: ./downloaded_assets
   Total files: 150

✅ Asset operations completed!
```

## Next Steps

- Learn about [dataset loaders](dataset-loader-training.md) for training preparation
- Explore [annotation workflows](annotation-workflows.md) for labeling assets
- Check out [basic dataset operations](basic-dataset-operations.md)

## Key Concepts

### Upload Result

Each upload operation returns an `AssetUploadResult` wrapper that aggregates statistics from all batches:

```python
result = client.assets.upload(...)

# Access aggregated statistics
print(f"Total: {result.total_files}")
print(f"Succeeded: {result.total_succeeded}")
print(f"Failed: {result.total_failed}")
print(f"Success rate: {result.success_rate:.1f}%")

# Get rich formatted output
print(result.summary())

# Access underlying sessions if needed
for session in result.sessions:
    print(f"Batch: {session.asset_ingestion_session_id}")
```

### Asset Metadata

Each asset has associated metadata:

- **Dimensions**: Width and height
- **File size**: Size in bytes
- **Upload status**: Processing state
- **Annotations**: Count of associated annotations

### Pagination

Assets are returned in pages. Iterate through all pages:

```python
# Automatic pagination
for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        process(asset)

# Or use all_items()
all_assets = client.assets.list(dataset_id=dataset_id)
for asset in all_assets.all_items():
    process(asset)
```

## Tips

!!! tip "Batch Uploads"
    For large batch uploads, upload entire directories. Files are automatically batched:
    ```python
    result = client.assets.upload(
        dataset_id=dataset_id,
        paths="./large_folder/",
        wait_until_done=True
    )
    # Access aggregated statistics
    print(f"✓ Uploaded {result.total_succeeded} assets across {len(result.sessions)} batch(es)")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(result.summary())  # Rich formatted output
    ```

!!! tip "Progress Tracking"
    Monitor upload progress:
    ```python
    result = client.assets.upload(
        dataset_id=dataset_id,
        paths=paths,
        wait_until_done=True  # Blocks until complete
    )
    # Check results
    if result.total_failed > 0:
        print(f"⚠️ {result.total_failed} files failed to upload")
        # Access failed file paths
        if result.failed_files:
            for failed_file in result.failed_files:
                print(f"  - {failed_file}")
    ```

!!! tip "File Formats"
    Supported image formats include:
    - JPEG (.jpg, .jpeg)
    - PNG (.png)
    - Other formats as supported by your organization

!!! warning "File Size Limits"
    Check your organization's file size limits before uploading very large images.

## Common Use Cases

### Bulk Upload from Directory

```python
import os

# Upload all images from a directory recursively
for root, dirs, files in os.walk("./images"):
    image_files = [
        os.path.join(root, f) for f in files
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if image_files:
        result = client.assets.upload(
            dataset_id=dataset_id,
            paths=root,
            wait_until_done=True
        )
        print(f"✓ Uploaded {result.total_succeeded} files from {root}")
```

### Download Specific Assets

```python
# Download only specific assets
asset_ids = ["asset_001", "asset_002", "asset_003"]

for asset_id in asset_ids:
    asset = client.assets.get(
        dataset_id=dataset_id,
        asset_id=asset_id,
        contents=True
    )
    # Download using the URL in asset.contents.asset.url
```

### Filter by Dimensions

```python
# Find square images
square_assets = []

for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        if asset.metadata.width == asset.metadata.height:
            square_assets.append(asset)
```
