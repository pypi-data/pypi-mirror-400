# Examples

This section contains practical, hands-on examples demonstrating how to use the Vi SDK effectively. Each example is a complete, runnable Python script that showcases specific features and workflows.

## Getting Started

### Prerequisites

Before running the examples, ensure you have:

1. **Installed Vi SDK with all features:**
   ```bash
   pip install vi-sdk[all]
   ```

2. **Set up your credentials:**
   ```bash
   export DATATURE_VI_SECRET_KEY="your-secret-key"
   export DATATURE_VI_ORGANIZATION_ID="your-organization-id"
   ```

## Available Examples

### 1. Basic Dataset Operations
Learn the fundamentals of working with datasets in Vi SDK.

- [View Example](basic-dataset-operations.md)
- Topics: Client initialization, listing datasets, creating exports, downloading datasets

### 2. Asset Upload and Download
Master asset management operations.

- [View Example](asset-upload-download.md)
- Topics: Single/batch uploads, asset listing, filtering, downloading

### 3. Dataset Loader and Training
Prepare data for model training using the ViDataset loader.

- [View Example](dataset-loader-training.md)
- Topics: Loading datasets, accessing splits, iterating data, visualization

### 4. Model Download and Inference
Download trained models and run inference.

- [View Example](model-download-inference.md)
- Topics: Model downloading, loading for inference, running predictions

### 5. Annotation Workflows
Work with different annotation types.

- [View Example](annotation-workflows.md)
- Topics: Creating annotations, phrase grounding, VQA, batch operations

## Complete Workflow

For a typical end-to-end workflow, run the examples in order:

```bash
# 1. Download a dataset
python3 01_basic_dataset_operations.py

# 2. Upload new assets
python3 02_asset_upload_download.py

# 3. Prepare data for training
python3 03_dataset_loader_training.py

# 4. Download and run inference with a trained model
python3 04_model_download_and_inference.py

# 5. Work with annotations
python3 05_annotation_workflows.py
```

## Common Patterns

### Error Handling

```python
from vi import ViError, ViNotFoundError, ViAuthenticationError

try:
    dataset = client.datasets.get("dataset-id")
except ViNotFoundError:
    print("Dataset not found")
except ViAuthenticationError:
    print("Authentication failed")
except ViError as e:
    print(f"Error: {e.error_code} - {e.message}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
```

### Pagination

```python
from vi.api.types import PaginationParams

# Iterate all pages automatically
for page in client.datasets.list():
    for dataset in page.items:
        process(dataset)

# Or iterate all items
datasets = client.datasets.list()
for dataset in datasets.all_items():
    process(dataset)

# Custom page size
pagination = PaginationParams(page_size=50)
datasets = client.datasets.list(pagination=pagination)
```

### Progress Tracking

```python
# With progress bar (default)
dataset = client.get_dataset(
    dataset_id="dataset-id",
    show_progress=True
)

# Without progress bar (for scripts/CI)
dataset = client.get_dataset(
    dataset_id="dataset-id",
    show_progress=False
)
```

## Best Practices

### 1. Use Virtual Environments

```bash
python3 -m venv vi-env
source vi-env/bin/activate  # Linux/macOS
pip install vi-sdk[all]
```

### 2. Secure Your Credentials

Never hardcode credentials:

```python
# ❌ Bad
client = vi.Client(secret_key="sk_live_123...")

# ✅ Good
import os
client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
)
```

### 3. Enable Logging for Debugging

```python
from vi.logging import LoggingConfig, LogLevel

config = LoggingConfig(
    level=LogLevel.DEBUG,
    enable_console=True,
    enable_file=True
)

client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID"),
    logging_config=config
)
```

### 4. Use Efficient Iteration

```python
# ✅ Efficient - streaming, low memory
for asset, annotations in dataset.training.iter_pairs():
    process(asset, annotations)

# ❌ Less efficient - loads all at once
all_data = list(dataset.training.iter_pairs())
for asset, annotations in all_data:
    process(asset, annotations)
```

## Troubleshooting

### "No datasets found"

Make sure you have datasets in your organization on Datature Vi.

### Authentication errors

1. Verify your credentials are correct
2. Check environment variables are set
3. Ensure your API key hasn't been revoked

### Import errors

```bash
# Install all dependencies
pip install vi-sdk[all]

# Or install specific features
pip install vi-sdk[inference]  # For inference
```

## Getting Help

- **Documentation**: Browse the full API reference and user guides
- **GitHub Issues**: [Report bugs or request features](https://github.com/datature/Vi-SDK/issues)
- **Email Support**: developers@datature.io

## Source Code

All example scripts are available in the [examples directory](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) of the Vi SDK repository.
