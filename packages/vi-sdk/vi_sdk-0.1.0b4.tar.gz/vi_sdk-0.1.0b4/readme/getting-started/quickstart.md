---
title: "Quickstart Guide"
excerpt: "Get started with Vi SDK in under 5 minutes"
category: "getting-started"
---

# Quickstart Guide

Get started with Vi SDK in under 5 minutes! This guide covers the essential operations you'll use most often.

---

## Prerequisites

Before you begin, make sure you have:

1. ✅ Installed Vi SDK (`pip install vi-sdk[all]`)
2. ✅ A Datature account with API access
3. ✅ Your secret key and organization ID

> 📘 **New to Datature?**
>
> If you don't have an account yet, sign up at [vi.datature.com](https://vi.datature.com)

---

## Initialize the Client

First, create a client instance to interact with the Vi platform:

```python
import vi

# Initialize with credentials
client = vi.Client(
    secret_key="your-secret-key-here",
    organization_id="your-organization-id-here"
)

print(f"Connected to organization: {client.organizations.id}")

# Explore what's available
client.help()  # Shows common operations and examples
```

> 💡 **Discover Features**
>
> The SDK has built-in help methods to discover available operations:
>
> ```python
> # Quick reference for all operations
> client.help()
>
> # Help for specific resources
> client.datasets.help()
> client.assets.help()
>
> # Inspect any object for detailed information
> asset.info()  # Shows rich details about an asset
> dataset.info()  # Shows dataset statistics
> ```

> 💡 **Environment Variables**
>
> For better security, use environment variables:
>
> ```bash
> export DATATURE_VI_SECRET_KEY="your-secret-key"
> export DATATURE_VI_ORGANIZATION_ID="your-organization-id"
> ```
>
> Then:
>
> ```python
> import os
> import vi
>
> client = vi.Client(
>     secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
>     organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
> )
> ```

---

## List Your Datasets

View all datasets in your organization:

```python
# Direct iteration (simplest)
for dataset in client.datasets:
    print(f"📊 {dataset.name}")
    print(f"   ID: {dataset.dataset_id}")
    print(f"   Assets: {dataset.statistic.asset_total}")
    print(f"   Annotations: {dataset.statistic.annotation_total}")
```

> 💡 **Manual Pagination**
>
> For manual page-by-page iteration:
>
> ```python
> # Iterate page by page
> for page in client.datasets.list():
>     for dataset in page.items:
>         print(f"Dataset: {dataset.name}")
> ```

> 📝 **Dataset Info**
>
> Use `.info()` to see detailed information about any dataset:
>
> ```python
> dataset = client.datasets.get("your-dataset-id")
> dataset.info()  # Shows rich formatted details
> ```

---

## Download a Dataset

Download a complete dataset with assets and annotations:

```python
# Download dataset
result = client.get_dataset(
    dataset_id="your-dataset-id",
    save_dir="./data"
)

# Show summary
print(result.summary())

# Access download details
print(f"Total size: {result.size_mb:.1f} MB")
print(f"Splits: {', '.join(result.splits)}")

# Show detailed information
result.info()
```

The dataset will be saved to `./data/your-dataset-id/` with the following structure:

```
your-dataset-id/
├── metadata.json
├── dump/
│   ├── annotations/
│   │   └── annotations.jsonl
│   └── assets/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── training/
│   └── ...
└── validation/
    └── ...
```

---

## Load Dataset for Training

Use the dataset loader to prepare data for training:

```python
from vi.dataset.loaders import ViDataset

# Load dataset
dataset = ViDataset("./data/your-dataset-id")

# Get dataset info
info = dataset.info()
print(f"📊 Dataset: {info.name}")
print(f"   Total assets: {info.total_assets}")
print(f"   Total annotations: {info.total_annotations}")
print(f"   Training: {info.splits['training'].assets} assets")
print(f"   Validation: {info.splits['validation'].assets} assets")

# Iterate through training data
for asset, annotations in dataset.training.iter_pairs():
    print(f"\n🖼️  {asset.filename}")
    print(f"   Size: {asset.width}x{asset.height}")

    for ann in annotations:
        if hasattr(ann.contents, 'caption'):
            # Phrase grounding annotation
            print(f"   📝 Caption: {ann.contents.caption}")
            print(f"      Phrases: {len(ann.contents.grounded_phrases)}")
        elif hasattr(ann.contents, 'interactions'):
            # VQA annotation
            print(f"   💬 Q&A pairs: {len(ann.contents.interactions)}")
```

---

## Upload Assets

Upload images to an existing dataset:

```python
# Upload a single image (simple)
result = client.assets.upload(
    dataset_id="your-dataset-id",
    paths="path/to/image.jpg"
)
print(f"✓ Uploaded: {result.total_succeeded} assets")
print(result.summary())  # Shows detailed upload summary

# Upload a folder of images
result = client.assets.upload(
    dataset_id="your-dataset-id",
    paths="path/to/images/",
    wait_until_done=True  # Wait for processing to complete
)
print(f"✓ Uploaded: {result.total_succeeded}/{result.total_files} assets")
print(f"Success rate: {result.success_rate:.1f}%")

# View detailed summary
print(result.summary())
```

---

## List Assets

View assets in a dataset:

```python
# Direct iteration (simplest) - use __call__ syntax for parameters
for asset in client.assets(dataset_id="your-dataset-id"):
    print(f"🖼️  {asset.filename}")
    print(f"   Size: {asset.metadata.width}x{asset.metadata.height}")

# Inspect individual asset details
first_asset = next(iter(client.assets(dataset_id="your-dataset-id")))
first_asset.info()  # Shows rich formatted asset information
```

---

## Run Inference

Use a trained model for inference:

```python
from vi.inference import ViModel

# Load model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)

# Run inference on single image - returns (result, error) tuple
result, error = model(
    source="path/to/test_image.jpg",
    user_prompt="Describe this image in detail"
)

if error is None:
    print(f"Result: {result}")
else:
    print(f"Error: {error}")

# Batch inference on specific files
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
results = model(source=images, user_prompt="Describe this image", show_progress=True)

for img, (result, error) in zip(images, results):
    if error is None:
        print(f"{img}: {result}")

# Process entire folder directly
results = model(
    source="./test_images/",  # Folder path
    user_prompt="Describe this image",
    recursive=True,  # Include subdirectories
    show_progress=True
)

for result, error in results:
    if error is None:
        print(f"Success: {result}")
```

---

## Error Handling

Always handle errors appropriately:

```python
from vi import (
    ViError,
    ViNotFoundError,
    ViAuthenticationError,
    ViValidationError
)

try:
    dataset = client.datasets.get("invalid-id")
except ViNotFoundError as e:
    print(f"❌ Dataset not found: {e.message}")
    if e.suggestion:
        print(f"💡 Suggestion: {e.suggestion}")
except ViAuthenticationError as e:
    print(f"❌ Authentication failed: {e.message}")
    print("Please check your API credentials")
except ViValidationError as e:
    print(f"❌ Validation error: {e.message}")
except ViError as e:
    print(f"❌ Error: {e.error_code} - {e.message}")
```

---

## Complete Example

Here's a complete workflow combining multiple operations:

```python
import vi
from vi.dataset.loaders import ViDataset
from vi.api.types import PaginationParams

# Initialize client
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id"
)

# 1. List and select a dataset
print("📊 Available datasets:")
datasets = client.datasets.list()
for dataset in datasets.items[:5]:  # Show first 5
    print(f"   - {dataset.name} ({dataset.dataset_id})")

# 2. Download the dataset
dataset_id = datasets.items[0].dataset_id
downloaded = client.get_dataset(
    dataset_id=dataset_id,
    save_dir="./data"
)
print(f"\n✓ Downloaded to: {downloaded.save_dir}")

# 3. Load and explore the dataset
dataset = ViDataset(downloaded.save_dir)
info = dataset.info()
print(f"\n📊 Dataset Info:")
print(f"   Name: {info.name}")
print(f"   Total assets: {info.total_assets}")
print(f"   Total annotations: {info.total_annotations}")

# 4. Iterate through training data
print(f"\n🎓 Training data (first 3):")
for i, (asset, annotations) in enumerate(dataset.training.iter_pairs()):
    if i >= 3:
        break
    print(f"   {i+1}. {asset.filename} - {len(annotations)} annotations")

# 5. Upload new assets
print(f"\n📤 Uploading new assets...")
try:
    upload_result = client.assets.upload(
        dataset_id=dataset_id,
        paths="path/to/new/images/",
        wait_until_done=True
    )
    print(f"✓ Uploaded {upload_result.total_succeeded} assets")
    print(upload_result.summary())
except Exception as e:
    print(f"❌ Upload failed: {e}")

print(f"\n✅ Workflow complete!")
```

---

## Common Operations Cheat Sheet

| Operation | Code |
|-----------|------|
| Initialize client | `client = vi.Client(secret_key, organization_id)` |
| List datasets | `client.datasets.list()` |
| Get dataset | `client.datasets.get(dataset_id)` |
| Download dataset | `client.get_dataset(dataset_id, save_dir)` |
| Upload assets | `client.assets.upload(dataset_id, paths)` |
| List assets | `client.assets.list(dataset_id)` |
| Run inference | `ViModel(secret_key, organization_id, run_id)` |
| List runs | `client.runs.list()` |

---

## Next Steps

Now that you're familiar with the basics:

- **[Authentication](vi-sdk-authentication)** - Learn about different authentication methods and best practices
- **[Configuration](vi-sdk-configuration)** - Configure logging, timeouts, and other SDK settings
- **[User Guide](vi-sdk-overview)** - Dive deeper into specific features
- **[API Reference](vi-sdk-client)** - Complete API documentation

---

## Need Help?

- 📖 [User Guide](vi-sdk-overview) - Comprehensive guides
- 💡 [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Real-world examples
- 🐛 [GitHub Issues](https://github.com/datature/Vi-SDK/issues) - Report bugs
- 📧 [Email Support](mailto:developers@datature.io) - Get help
