# Basic Dataset Operations

This example demonstrates fundamental dataset operations using the Vi SDK.

## Overview

Learn how to:

- Initialize the Vi SDK client
- Get organization information
- List available datasets
- Get detailed dataset information
- Create and manage dataset exports
- Download datasets for local use

## Source Code

[View full source on GitHub](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/examples/01_basic_dataset_operations.py)

## Code Walkthrough

### 1. Initialize the Client

```python
import vi

# Initialize client with credentials from environment variables
client = vi.Client(
    secret_key="YOUR_DATATURE_VI_SECRET_KEY",
    organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
)
```

### 2. Get Organization Information

```python
# Retrieve organization details
org = client.organizations.info()
print(f"Name: {org.name}")
print(f"ID: {org.organization_id}")
print(f"Datasets: {len(org.datasets)}")
```

### 3. List Datasets

```python
# List all datasets in the organization
datasets_response = client.datasets.list()

for dataset in datasets_response.items:
    print(f"Name: {dataset.name}")
    print(f"ID: {dataset.dataset_id}")
    print(f"Type: {dataset.type.value}")
    print(f"Assets: {dataset.statistic.asset_total}")
    print(f"Annotations: {dataset.statistic.annotation_total}")
```

### 4. Get Detailed Dataset Information

```python
# Get full details for a specific dataset
dataset_details = client.datasets.get(dataset_id)

print(f"Owner: {dataset_details.owner}")
print(f"Content Type: {dataset_details.content.value}")
print(f"Localization: {dataset_details.localization.value}")
print(f"Is Locked: {dataset_details.is_locked}")

# Display tags if available
if dataset_details.tags:
    for tag_name, tag_id in dataset_details.tags.items():
        print(f"Tag: {tag_name} (ID: {tag_id})")
```

### 5. Create a Dataset Export

```python
from vi.api.resources.datasets.types import DatasetExportFormat, DatasetExportSettings

# Configure export settings
export_settings = DatasetExportSettings(
    format=DatasetExportFormat.VI_FULL  # Full dataset with assets and annotations
)

# Create the export
new_export = client.datasets.create_export(
    dataset_id=dataset_id,
    export_settings=export_settings
)

print(f"Export ID: {new_export.dataset_export_id}")
```

### 6. Download a Dataset

```python
from pathlib import Path

# Download dataset to local directory
save_dir = Path("./data")
save_dir.mkdir(exist_ok=True)

downloaded = client.get_dataset(
    dataset_id=dataset_id,
    save_dir=save_dir,
    overwrite=False,  # Skip if already exists
    show_progress=True,
)

print(f"Downloaded to: {downloaded.save_dir}")
```

## Running the Example

### Prerequisites

```bash
# Install Vi SDK
pip install vi-sdk

### Execute

```bash
python3 01_basic_dataset_operations.py
```

## Expected Output

```
📡 Initializing Vi SDK client...

🏢 Organization Info:
   Name: My Organization
   ID: org_abc123
   Datasets: 5

📊 Listing datasets:

   1. Training Dataset
      ID: dataset_xyz789
      Type: phrase_grounding
      Assets: 150
      Annotations: 300
      Created: 2025-01-15T10:30:00Z

🎯 Selected dataset: Training Dataset

📋 Getting detailed info for 'Training Dataset'...
   Owner: user@example.com
   Content Type: image
   Localization: en-US
   Is Locked: False

🔄 Creating new export for 'Training Dataset'...
   ✓ Export created!
   Export ID: export_def456

⬇️  Downloading dataset 'Training Dataset'...
   ✓ Dataset downloaded successfully!
   Location: ./data/dataset_xyz789

   📁 Downloaded structure:
      training/
         assets/ (120 files)
         annotations/
      validation/
         assets/ (30 files)
         annotations/

✅ Basic dataset operations completed!
```

## Next Steps

- Explore [asset operations](asset-upload-download.md) for uploading and managing images
- Learn about [dataset loaders](dataset-loader-training.md) for training preparation
- Check out [annotation workflows](annotation-workflows.md) for working with labels

## Key Concepts

### Dataset Types

Vi SDK supports different dataset types:

- **Phrase Grounding**: Images with captions and grounded phrases
- **VQA**: Visual Question Answering datasets
- **General**: Standard image datasets

### Export Formats

Available export formats:

- `VI_FULL`: Complete dataset with all assets and annotations
- `VI_JSONL`: Annotations only, no asset files

### Directory Structure

Downloaded datasets follow this structure:

```
data/
└── dataset_id/
    ├── training/
    │   ├── assets/
    │   └── annotations/
    ├── validation/
    │   ├── assets/
    │   └── annotations/
    └── dump/
        ├── assets/
        └── annotations/
```

## Tips

!!! tip "Pagination"
    When working with large numbers of datasets, use pagination:
    ```python
    from vi.api.types import PaginationParams

    pagination = PaginationParams(page_size=50)
    datasets = client.datasets.list(pagination=pagination)
    ```

!!! tip "Progress Tracking"
    Disable progress bars in CI/CD environments:
    ```python
    downloaded = client.get_dataset(
        dataset_id=dataset_id,
        show_progress=False  # No progress bar
    )
    ```

!!! warning "Storage"
    Datasets can be large. Ensure you have sufficient disk space before downloading.
