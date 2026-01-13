---
title: "Vi SDK Documentation"
excerpt: "Python SDK for Datature Vi"
category: "getting-started"
---

# Vi SDK Documentation

**Python SDK for Datature Vi**

[![PyPI version](https://badge.fury.io/py/vi-sdk.svg)](https://badge.fury.io/py/vi-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/vi-sdk.svg)](https://pypi.org/project/vi-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## What is Vi SDK?

The **Vi SDK** is a comprehensive Python library for interacting with the Datature Vi platform. It provides a clean, intuitive API for managing computer vision datasets, annotations, training models, and performing inference with state-of-the-art vision-language models.

---

## Key Features

### Dataset Management
Upload, download, and manage datasets with ease. Support for multiple annotation formats and efficient batch operations.

### Asset Operations
Handle images and assets with concurrent upload/download, progress tracking, and automatic format detection.

### Annotation Workflows
Create, update, and manage annotations for phrase grounding, VQA, and other vision tasks.

### Model Training & Inference
Train models on Datature's infrastructure and run inference with vision-language models like Qwen2.5-VL, InternVL 3.5, Cosmos Reason1, and NVILA.

### High Performance
Built with performance in mind - concurrent operations, streaming downloads, and efficient memory usage.

### Developer Friendly
Type hints, comprehensive error handling, structured logging, and extensive documentation.

---

## Quick Example

```python
import vi

# Initialize client
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-org-id"
)

# List datasets
for page in client.datasets.list():
    for dataset in page.items:
        print(f"Dataset: {dataset.name} (ID: {dataset.dataset_id})")

# Download a dataset
dataset = client.get_dataset(
    dataset_id="your-dataset-id",
    save_dir="./data"
)

# Load dataset for training
from vi.dataset.loaders import ViDataset

dataset = ViDataset("./data/your-dataset-id")
print(f"Total assets: {dataset.info().total_assets}")

# Iterate through training split
for asset, annotations in dataset.training.iter_pairs():
    print(f"Processing: {asset.filename}")
    for annotation in annotations:
        print(f"  - {annotation.contents}")
```

---

## Installation

Install Vi SDK using pip:

```bash
pip install vi-sdk
```

For additional features:

```bash
# With inference support (Qwen2.5-VL, InternVL 3.5, Cosmos Reason1, NVILA and other models)
pip install vi-sdk[inference]

# Install all features
pip install vi-sdk[all]
```

---

## Core Concepts

### Client & Authentication

The `ViClient` is your entry point to the Vi platform. It handles authentication, request management, and provides access to all resources.

```python
import vi

# Using API key
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-org-id"
)

# Using config file
client = vi.Client(config_file="~/datature/vi/config.json")

# With custom logging
from vi.logging import LoggingConfig, LogLevel

logging_config = LoggingConfig(
    level=LogLevel.DEBUG,
    enable_console=True
)
client = vi.Client(
    secret_key="your-secret-key",
    organization_id="your-org-id",
    logging_config=logging_config
)
```

### Resource Hierarchy

Vi SDK follows the platform's resource hierarchy:

```
Organization
├── Datasets
│   ├── Assets
│   └── Annotations
├── Runs
│   └── Models
└── Flows
```

Access resources through the client:

```python
# Access organization
org = client.organizations.get()

# Access datasets
datasets = client.datasets.list()

# Access assets within a dataset
assets = client.assets.list(dataset_id="...")

# Access models from runs
models = client.models.list(run_id="...")
```

### Error Handling

Vi SDK provides comprehensive error handling with structured error codes:

```python
from vi import (
    ViError,
    ViAuthenticationError,
    ViNotFoundError,
    ViValidationError
)

try:
    dataset = client.datasets.get("invalid-id")
except ViNotFoundError as e:
    print(f"Dataset not found: {e.message}")
    print(f"Suggestion: {e.suggestion}")
except ViAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except ViError as e:
    print(f"Error: {e.error_code} - {e.message}")
```

### Pagination

Automatic pagination support for listing resources:

```python
# Iterate over all pages automatically
for page in client.datasets.list():
    for dataset in page.items:
        print(dataset.name)

# Access just the first page
first_page = client.datasets.list()
print(f"First page has {len(first_page.items)} items")

# Iterate over all items across all pages
datasets = client.datasets.list()
for dataset in datasets.all_items():
    print(dataset.name)

# Manual pagination with page size
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=50)
datasets = client.datasets.list(pagination=pagination)
```

---

## Supported Features

| Feature | Status | Documentation |
|---------|--------|---------------|
| Dataset Management | ✅ | [Guide](vi-sdk-datasets) |
| Asset Upload/Download | ✅ | [Guide](vi-sdk-assets) |
| Annotation Management | ✅ | [Guide](vi-sdk-annotations) |
| Model Training | ✅ | [Guide](vi-sdk-models) |
| Model Inference | ✅ | [Guide](vi-sdk-inference) |
| NIM Deployment | ✅ | [Guide](vi-sdk-nim-deployment) |
| Dataset Loaders | ✅ | [Guide](vi-sdk-dataset-loaders) |
| Phrase Grounding | ✅ | [Guide](vi-sdk-inference) |
| VQA (Visual Question Answering) | ✅ | [Guide](vi-sdk-inference) |
| Structured Logging | ✅ | [Guide](vi-sdk-logging) |
| Progress Tracking | ✅ | - |
| Concurrent Operations | ✅ | - |

---

## Next Steps

- **[Quickstart](vi-sdk-quickstart)** - Get up and running in 5 minutes
- **[User Guide](vi-sdk-overview)** - Comprehensive guides for all features
- **[API Reference](vi-sdk-client)** - Detailed API documentation with examples
- **[Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples)** - Real-world runnable Python examples

---

## Need Help?

- **Documentation**: You're reading it! Use the search bar to find what you need
- **GitHub Issues**: Report bugs or request features at [github.com/datature/Vi-SDK/issues](https://github.com/datature/Vi-SDK/issues)
- **Email Support**: Reach out to [developers@datature.io](mailto:developers@datature.io)
- **Community**: Join our community discussions

---

## License

Vi SDK is licensed under the Apache License 2.0. See [LICENSE](https://github.com/datature/Vi-SDK/blob/main/LICENSE) for details.
