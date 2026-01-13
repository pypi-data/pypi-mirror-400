# Working with Datasets

Learn how to manage computer vision datasets on the Datature Vi platform.

## Overview

Datasets are the foundation of your computer vision projects. The Vi SDK provides comprehensive tools for:

- Creating and managing datasets
- Listing and filtering datasets
- Downloading datasets with assets and annotations
- Creating and managing dataset exports
- Bulk operations on datasets

## Core Concepts

### Dataset Structure

A dataset in Vi contains:

- **Assets**: Images or other media files
- **Annotations**: Labels and annotations for those assets
- **Metadata**: Information about the dataset (tags, statistics, etc.)
- **Splits**: Training and validation splits

### Dataset Types

Vi supports multiple dataset types:

- **Phrase Grounding**: Images with captions and grounded phrases
- **VQA**: Visual question answering datasets

## Listing Datasets

### List All Datasets

```python
import vi

client = vi.Client()

# List datasets (first page)
datasets = client.datasets.list()

for dataset in datasets.items:
    print(f"📊 {dataset.name}")
    print(f"   ID: {dataset.dataset_id}")
    print(f"   Type: {dataset.type.value}")
    print(f"   Assets: {dataset.statistic.asset_total}")
    print(f"   Annotations: {dataset.statistic.annotation_total}")
```

### Iterate All Pages

```python
# Automatic pagination
for page in client.datasets.list():
    for dataset in page.items:
        print(f"Dataset: {dataset.name}")
```

### Custom Page Size

```python
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=50)
datasets = client.datasets.list(pagination=pagination)

print(f"Got {len(datasets.items)} datasets")
```

## Getting Dataset Details

### Get Specific Dataset

```python
dataset = client.datasets.get("dataset_abc123")

print(f"Name: {dataset.name}")
print(f"Owner: {dataset.owner}")
print(f"Type: {dataset.type.value}")
print(f"Content: {dataset.content.value}")
print(f"Created: {dataset.create_date}")
print(f"Assets: {dataset.statistic.asset_total}")
print(f"Annotations: {dataset.statistic.annotation_total}")
```

### Access Dataset Statistics

```python
dataset = client.datasets.get("dataset_abc123")

stats = dataset.statistic
print(f"Total assets: {stats.asset_total}")
print(f"Total annotations: {stats.annotation_total}")
print(f"Annotated assets: {stats.asset_annotated}")

# Tag distribution
for tag_name, tag_count in stats.tags_count.items():
    print(f"Tag '{tag_name}': {tag_count} annotations")
```

## Creating Dataset Exports

### Create New Export

```python
from vi.api.resources.datasets.types import (
    DatasetExportSettings,
    DatasetExportFormat,
    DatasetExportOptions
)

# Configure export settings
export_settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_FULL,  # Full dataset with assets
    options=DatasetExportOptions(
        normalized=True,  # Normalize coordinates
        split_ratio=0.7   # 70% train, 30% validation
    )
)

# Create export
export = client.datasets.create_export(
    dataset_id="dataset_abc123",
    export_settings=export_settings
)

print(f"Export ID: {export.dataset_export_id}")
print(f"Format: {export.spec.format.value}")
```

### List Existing Exports

```python
exports = client.datasets.list_exports("dataset_abc123")

for export in exports.items:
    print(f"Export ID: {export.dataset_export_id}")
    print(f"Format: {export.spec.format.value}")
    print(f"Created: {export.metadata.time_created}")

    if export.status.download_url:
        print(f"Status: Ready")
    else:
        print(f"Status: Processing")
```

### Get Export Status

```python
export = client.datasets.get_export(
    dataset_id="dataset_abc123",
    dataset_export_id="export_xyz789"
)

# Check if ready
if export.status.download_url:
    print(f"✓ Export ready!")
    print(f"Download URL expires: {export.status.download_url.expires_at}")
else:
    print(f"⏳ Export still processing...")
```

## Downloading Datasets

### Basic Download

```python
# Simple download
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    save_dir="./data"
)

print(f"Downloaded to: {dataset.save_dir}")
```

### Download with Custom Settings

```python
from vi.api.resources.datasets.types import DatasetExportSettings

# Custom export configuration
from vi.api.resources.datasets.types import DatasetExportOptions

settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_FULL,
    options=DatasetExportOptions(
        normalized=True,
        split_ratio=0.8  # 80-20 split
    )
)

dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    export_settings=settings,
    save_dir="./data",
    overwrite=True,  # Overwrite if exists
    show_progress=True  # Show progress bars
)
```

### Download Annotations Only

```python
# Download only annotations (no assets)
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    annotations_only=True,
    save_dir="./annotations"
)
```

### Download Specific Export

```python
# Use existing export
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    dataset_export_id="export_xyz789",
    save_dir="./data"
)
```

### Download Without Progress Bars

```python
# For scripts/CI environments
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    show_progress=False
)
```

## Working with Downloaded Datasets

### Load Dataset

```python
from vi.dataset.loaders import ViDataset

# Load downloaded dataset
dataset = ViDataset("./data/dataset_abc123")

# Get information
info = dataset.info()
print(f"Name: {info.name}")
print(f"Total assets: {info.total_assets}")
print(f"Total annotations: {info.total_annotations}")
```

### Iterate Training Data

```python
# Iterate through training split
for asset, annotations in dataset.training.iter_pairs():
    print(f"Asset: {asset.filename}")
    print(f"Size: {asset.width}x{asset.height}")
    print(f"Annotations: {len(annotations)}")

    # Process data
    image = load_image(asset.filepath)
    train_model(image, annotations)
```

See: [Dataset Loaders Guide](dataset-loaders.md)

## Bulk Operations

### Delete Multiple Assets

```python
# Delete assets matching criteria
response = client.datasets.bulk_delete_assets(
    dataset_id="dataset_abc123",
    filter_criteria='{"status": "error"}',  # Delete errored assets
    strict_query=True
)

print(f"Deletion session: {response.delete_many_assets_session_id}")
```

### Get Deletion Status

```python
status = client.datasets.get_bulk_asset_deletion_session(
    dataset_id="dataset_abc123",
    delete_many_assets_session_id="session_id"
)

# Check conditions
for condition in status.status.conditions:
    print(f"{condition.condition}: {condition.status.value}")
```

## Deleting Datasets

### Delete Dataset

```python
# Delete entire dataset
deleted = client.datasets.delete("dataset_abc123")

print(f"Dataset ID: {deleted.dataset_id}")
print(f"Deletion initiated")
```

### Check Deletion Status

```python
deletion_status = client.datasets.get_deletion_operation(
    "dataset_abc123"
)

for condition in deletion_status.status.conditions:
    print(f"{condition.condition}: {condition.status.value}")
```

## Best Practices

### 1. Use Pagination Efficiently

```python
# ✅ Good - iterate as you go
for page in client.datasets.list():
    for dataset in page.items:
        process(dataset)

# ❌ Bad - load all at once
all_datasets = []
for page in client.datasets.list():
    all_datasets.extend(page.items)
```

### 2. Cache Downloaded Datasets

```python
from pathlib import Path

def get_or_download_dataset(dataset_id, save_dir="./data"):
    """Download dataset if not already cached."""
    dataset_path = Path(save_dir) / dataset_id

    if dataset_path.exists():
        print(f"Using cached dataset at {dataset_path}")
        return {"save_dir": str(dataset_path)}

    return client.get_dataset(
        dataset_id=dataset_id,
        save_dir=save_dir,
        overwrite=False
    )
```

### 3. Handle Download Errors

```python
from vi import ViError, ViDownloadError

try:
    dataset = client.get_dataset("dataset_abc123")
except ViDownloadError as e:
    print(f"Download failed: {e.message}")
    # Check disk space, retry, or use cached version
except ViError as e:
    print(f"Error: {e.error_code}")
```

### 4. Verify Dataset Integrity

```python
from pathlib import Path

def verify_dataset(dataset_path):
    """Verify dataset has required files."""
    path = Path(dataset_path)

    # Check for required directories
    required = ["training", "validation", "dump"]
    for split in required:
        split_path = path / split
        if not split_path.exists():
            return False

        # Check for assets and annotations
        if not (split_path / "assets").exists():
            return False
        if not (split_path / "annotations").exists():
            return False

    # Check metadata file
    if not (path / "metadata.json").exists():
        return False

    return True

# Usage
if verify_dataset("./data/dataset_abc123"):
    print("✓ Dataset is valid")
else:
    print("✗ Dataset is incomplete, re-downloading...")
    client.get_dataset("dataset_abc123", overwrite=True)
```

### 5. Monitor Export Progress

```python
import time

def wait_for_export(dataset_id, export_id, max_wait=300):
    """Wait for export to complete."""
    start_time = time.time()

    while time.time() - start_time < max_wait:
        export = client.datasets.get_export(
            dataset_id=dataset_id,
            dataset_export_id=export_id
        )

        if export.status.download_url:
            print("✓ Export ready!")
            return export

        print("⏳ Still processing...")
        time.sleep(10)

    raise TimeoutError("Export took too long")

# Usage
export = client.datasets.create_export(
    dataset_id="dataset_abc123",
    export_settings=settings
)
ready_export = wait_for_export("dataset_abc123", export.dataset_export_id)
```

## Common Workflows

### Download Multiple Datasets

```python
import concurrent.futures

def download_dataset(dataset_id):
    """Download single dataset."""
    try:
        return client.get_dataset(
            dataset_id=dataset_id,
            save_dir="./data",
            overwrite=False
        )
    except Exception as e:
        print(f"Failed to download {dataset_id}: {e}")
        return None

# Parallel download
dataset_ids = ["dataset_1", "dataset_2", "dataset_3"]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(download_dataset, dataset_id)
        for dataset_id in dataset_ids
    ]

    results = [
        future.result()
        for future in concurrent.futures.as_completed(futures)
    ]

successful = [r for r in results if r is not None]
print(f"Downloaded {len(successful)} datasets")
```

### Export and Download Pipeline

```python
def export_and_download(dataset_id, save_dir="./data"):
    """Complete export and download workflow."""
    # 1. Create export
    print(f"Creating export for {dataset_id}...")
    export = client.datasets.create_export(
        dataset_id=dataset_id,
        export_settings=DatasetExportSettings()
    )

    # 2. Download using export
    print(f"Downloading dataset...")
    dataset = client.get_dataset(
        dataset_id=dataset_id,
        dataset_export_id=export.dataset_export_id,
        save_dir=save_dir
    )

    # 3. Verify
    if verify_dataset(dataset.save_dir):
        print(f"✓ Dataset ready at {dataset.save_dir}")
        return dataset
    else:
        raise ValueError("Dataset verification failed")

# Usage
dataset = export_and_download("dataset_abc123")
```

## Troubleshooting

### Dataset Not Found

```python
from vi import ViNotFoundError

try:
    dataset = client.datasets.get("invalid_id")
except ViNotFoundError as e:
    print(f"Dataset not found: {e.message}")
    # List available datasets
    datasets = client.datasets.list()
    print("Available datasets:")
    for ds in datasets.items:
        print(f"  - {ds.name} ({ds.dataset_id})")
```

### Export Stuck Processing

If an export seems stuck:

1. Check export status
2. Create a new export
3. Contact support if issue persists

```python
# Create new export
new_export = client.datasets.create_export(
    dataset_id="dataset_abc123",
    export_settings=DatasetExportSettings()
)
```

### Download Interrupted

```python
# Resume by re-downloading (with overwrite)
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    save_dir="./data",
    overwrite=True  # Will replace partial download
)
```

## See Also

- [Assets Guide](assets.md) - Managing assets in datasets
- [Annotations Guide](annotations.md) - Working with annotations
- [Dataset Loaders Guide](dataset-loaders.md) - Loading datasets for training
- [API Reference](../api/resources/datasets.md) - Complete API documentation
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Practical examples
