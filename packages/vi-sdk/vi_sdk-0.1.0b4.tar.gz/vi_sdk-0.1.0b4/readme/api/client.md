---
title: "Client API Reference"
excerpt: "Main entry point to the Vi platform"
category: "api-reference"
---

# Client API Reference

The `Client` class is your main entry point to the Vi platform. It provides access to all resources and handles authentication, requests, and logging.

---

## Initialization

The client can be initialized in several ways:

### Method 1: Direct Credentials

```python
import vi

client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id"
)
```

### Method 2: Environment Variables

```python
import os
import vi

client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
)
```

### Method 3: Configuration File

```python
import vi

client = vi.Client(
    config_file="~/datature/vi/config.json"
)
```

### Method 4: With Logging Configuration

```python
import vi
from vi.logging import LoggingConfig, LogLevel

logging_config = LoggingConfig(
    level=LogLevel.INFO,
    enable_console=True
)

client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    logging_config=logging_config
)
```

---

## Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `secret_key` | `str \| None` | Vi API secret key | `None` |
| `organization_id` | `str \| None` | Organization identifier | `None` |
| `config_file` | `str \| Path \| None` | Path to JSON config file | `None` |
| `endpoint` | `str` | API endpoint URL | Environment variable or default |
| `logging_config` | `LoggingConfig \| None` | Logging configuration | `None` |

---

## Convenience Methods

### get_dataset

Download a dataset with a single method call.

```python
downloaded = client.get_dataset(
    dataset_id="your-dataset-id",
    save_dir="./data",
    overwrite=False,
    show_progress=True
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `dataset_export_id` | `str \| None` | Specific export ID | `None` |
| `annotations_only` | `bool` | Download only annotations | `False` |
| `export_settings` | `DatasetExportSettings \| dict` | Export configuration | `None` |
| `save_dir` | `Path \| str` | Save directory | Required |
| `overwrite` | `bool` | Overwrite existing files | `False` |
| `show_progress` | `bool` | Show progress bars | `True` |

**Returns:** `DatasetDownloadResult`

**Example:**

```python
# Download with default settings
dataset = client.get_dataset(
    dataset_id="abc123",
    save_dir="./data"
)

print(f"Downloaded to: {dataset.save_dir}")
```

---

### get_model

Download a trained model by run ID.

```python
model = client.get_model(
    run_id="your-run-id",
    ckpt=None,
    save_path="./models"
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `run_id` | `str` | Run identifier | Required |
| `ckpt` | `str \| None` | Checkpoint name | `None` (uses latest) |
| `save_path` | `Path \| str` | Save directory | Required |

**Returns:** `ModelDownloadResult`

**Example:**

```python
# Download latest model
model = client.get_model(
    run_id="run_xyz789",
    save_path="./models"
)

print(f"Model path: {model.model_path}")
print(f"Adapter path: {model.adapter_path}")
print(f"Config: {model.run_config_path}")
```

---

## Resource Access

The client provides access to all platform resources through a flat structure:

### organizations

Access organization-level resources.

```python
# Get organization info (prints to console)
client.organizations.info()

# Get organization object for programmatic access
org = client.organizations.get()

# Get organization ID
org_id = client.organizations.id
```

**Type:** `Organization`

---

### datasets

Manage datasets.

```python
# List datasets
datasets = client.datasets.list()

# Get specific dataset
dataset = client.datasets.get("dataset-id")

# Download dataset
downloaded = client.datasets.download(
    dataset_id="dataset-id",
    save_dir="./data"
)
```

**Type:** `Dataset`

See: [Datasets API Reference](vi-sdk-datasets-api)

---

### assets

Manage assets within datasets.

```python
# Upload assets
result = client.assets.upload(
    dataset_id="dataset-id",
    paths="./images/"
)
print(f"Uploaded {result.total_succeeded} assets")
print(result.summary())

# List assets
assets = client.assets.list("dataset-id")

# Download assets
downloaded = client.assets.download(
    dataset_id="dataset-id",
    save_dir="./assets"
)
```

**Type:** `Asset`

See: [Assets API Reference](vi-sdk-assets-api)

---

### annotations

Manage annotations.

```python
# List annotations
annotations = client.annotations.list(
    dataset_id="dataset-id",
    asset_id="asset-id"
)

# Upload annotations
result = client.annotations.upload(
    dataset_id="dataset-id",
    paths="./annotations/"
)
print(f"✓ Imported: {result.total_annotations} annotations")
print(result.summary())
```

**Type:** `Annotation`

See: [Annotations API Reference](vi-sdk-annotations-api)

---

### runs

Manage training runs.

```python
# List runs
runs = client.runs.list()

# Get specific run
run = client.runs.get("run-id")
```

**Type:** `Run`

See: [Runs API Reference](vi-sdk-runs-api)

---

### models

Access trained models from runs.

```python
# List models for a run
models = client.models.list("run-id")

# Download model
model = client.models.download(
    run_id_or_link="run-id",
    save_dir="./models"
)
```

**Type:** `Model`

See: [Models API Reference](vi-sdk-models-api)

---

### flows

Manage workflows.

```python
# List flows
flows = client.flows.list()

# Get specific flow
flow = client.flows.get("flow-id")
```

**Type:** `Flow`

See: [Flows API Reference](vi-sdk-flows-api)

---

## Usage Examples

### Complete Workflow Example

```python
import vi
from vi.dataset.loaders import ViDataset

# Initialize client with logging
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
)

# 1. List datasets
print("Available datasets:")
for page in client.datasets.list():
    for dataset in page.items:
        print(f"- {dataset.name} ({dataset.dataset_id})")

# 2. Download a dataset
dataset = client.get_dataset(
    dataset_id="abc123",
    save_dir="./data"
)

# 3. Load with dataset loader
loaded_dataset = ViDataset(dataset.save_dir)
info = loaded_dataset.info()
print(f"Loaded {info.total_assets} assets")

# 4. Upload new assets
upload_result = client.assets.upload(
    dataset_id="abc123",
    paths="./new_images/",
    wait_until_done=True
)
print(f"Uploaded {upload_result.total_succeeded} assets")
print(upload_result.summary())

# 5. Download trained model
model = client.get_model(
    run_id="run_xyz789",
    save_path="./models"
)
print(f"Model downloaded to: {model.model_path}")
```

---

### Error Handling Example

```python
from vi import (
    ViError,
    ViAuthenticationError,
    ViNotFoundError,
    ViValidationError
)

try:
    client = vi.Client(
        secret_key="invalid-key",
        organization_id="org-id"
    )

    dataset = client.datasets.get("dataset-id")

except ViAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Suggestion: {e.suggestion}")

except ViNotFoundError as e:
    print(f"Dataset not found: {e.message}")

except ViValidationError as e:
    print(f"Validation error: {e.message}")

except ViError as e:
    print(f"Error: {e.error_code} - {e.message}")
    if e.is_retryable():
        print("This error may be temporary, consider retrying")
```

---

### Pagination Example

```python
from vi.api.types import PaginationParams

# Automatic pagination - iterate all pages
all_datasets = []
for page in client.datasets.list():
    all_datasets.extend(page.items)

print(f"Total datasets: {len(all_datasets)}")

# Custom page size
pagination = PaginationParams(page_size=50)
first_page = client.datasets.list(pagination=pagination)
print(f"First page: {len(first_page.items)} items")

# Iterate all items across pages
for dataset in client.datasets.list().all_items():
    print(f"Processing: {dataset.name}")
```

---

### Custom Endpoint Example

```python
# For enterprise or self-hosted installations
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    endpoint="https://custom-api.your-company.com"
)
```

---

## See Also

- [Authentication Guide](vi-sdk-authentication) - Detailed authentication methods
- [Configuration Guide](vi-sdk-configuration) - Client configuration options
- [Error Handling Guide](vi-sdk-error-handling) - Comprehensive error handling
- [Examples](https://github.com/datature/vi-sdk/tree/main/pypi/vi-sdk/examples) - Real-world usage examples
