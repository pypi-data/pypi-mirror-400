---
title: "Models API Reference"
excerpt: "Access and download trained models from runs"
category: "api-reference"
---

# Models API Reference

Complete API reference for model operations. Access and download trained models from training runs.

---

## Model Resource

Access models through `client.models`.

---

## Methods

### list()

List models for a run.

```python
# Basic listing
models = client.models.list("run_abc123")

for model in models.items:
    print(f"Model: {model.model_id}")
    print(f"Epoch: {model.spec.epoch}")
```

```python
# With custom pagination
from vi.api.types import PaginationParams

models = client.models.list(
    run_id_or_link="run_abc123",
    pagination=PaginationParams(page_size=50)
)

for model in models.items:
    print(f"{model.model_id}")
```

```python
# Using dict for pagination
models = client.models.list(
    run_id_or_link="run_abc123",
    pagination={"page_size": 50}
)
```

```python
# List with metrics
models = client.models.list("run_abc123")

print("Available Models:")
for model in models.items:
    epoch = model.spec.epoch or "N/A"
    metrics_str = "No metrics"

    if model.spec.evaluation_metrics:
        metrics = model.spec.evaluation_metrics
        metrics_str = ", ".join(f"{k}: {v:.4f}" for k, v in metrics.items())

    print(f"  Epoch {epoch}: {metrics_str}")
```

```python
# Find best model by metric
from vi.api.resources.models.responses import Model

def find_best_model(run_id: str, metric_name: str = "accuracy") -> tuple[Model | None, float]:
    """Find model with best metric value."""
    models = client.models.list(run_id)

    best_model: Model | None = None
    best_value = float('-inf')

    for model in models.items:
        if not model.spec.evaluation_metrics:
            continue

        value = model.spec.evaluation_metrics.get(metric_name, 0)
        if value > best_value:
            best_value = value
            best_model = model

    return best_model, best_value

best, value = find_best_model("run_abc123", "accuracy")
if best:
    print(f"Best model: {best.model_id}")
    print(f"Accuracy: {value}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `run_id_or_link` | `str` | Run identifier or link | Required |
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams)` \| dict` | Pagination settings | `PaginationParams()` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Model`](#model)`]`

---

### get()

Get a specific model checkpoint.

```python
# Get latest model
model = client.models.get(run_id_or_link="run_abc123")

print(f"Model ID: {model.model_id}")
print(f"Epoch: {model.spec.epoch}")
```

```python
# Get specific checkpoint
model = client.models.get(
    run_id_or_link="run_abc123",
    ckpt="epoch_10"
)

print(f"Model ID: {model.model_id}")
print(f"Epoch: {model.spec.epoch}")
```

```python
# Access model metrics
model = client.models.get(run_id_or_link="run_abc123")

if model.spec.evaluation_metrics:
    for metric, value in model.spec.evaluation_metrics.items():
        print(f"{metric}: {value}")
```

```python
# Display detailed information
model = client.models.get(run_id_or_link="run_abc123")
model.info()  # Prints formatted model summary
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `run_id_or_link` | `str` | Run identifier | Required |
| `ckpt` | `str` | Checkpoint name | `None` (latest) |

**Returns:** [`Model`](#model)

---

### download()

Download a model.

```python
# Basic download
downloaded = client.models.download(
    run_id_or_link="run_abc123",
    save_dir="./models"
)

print(f"Model path: {downloaded.model_path}")
```

```python
# Download specific checkpoint
downloaded = client.models.download(
    run_id_or_link="run_abc123",
    ckpt="epoch_10",
    save_dir="./models"
)

print(f"Model: {downloaded.model_path}")
print(f"Config: {downloaded.run_config_path}")
```

```python
# Using the convenience method on client
downloaded = client.get_model(
    run_id="run_abc123",
    save_path="./models"
)

print(f"✓ Model downloaded!")
print(f"Model: {downloaded.model_path}")
print(f"Config: {downloaded.run_config_path}")
```

```python
# Cache downloaded models
from pathlib import Path

def get_or_download_model(run_id: str, save_dir: str = "./models") -> dict[str, str]:
    """Download model if not already cached."""
    model_dir = Path(save_dir) / run_id

    # Check cache
    if model_dir.exists() and (model_dir / "model_full").exists():
        print(f"Using cached model at {model_dir}")
        return {
            "model_path": str(model_dir / "model_full"),
            "run_config_path": str(model_dir / "run_config.json")
        }

    # Download
    return client.get_model(run_id=run_id, save_path=save_dir)

result = get_or_download_model("run_abc123")
```

```python
# Load downloaded model for inference
from vi.inference import ViModel

# Download first
downloaded = client.get_model(
    run_id="run_abc123",
    save_path="./models"
)

# Load for inference
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="run_abc123"
)

# Run inference
result, error = model(
    source="test.jpg",
    user_prompt="Describe this image"
)

if error is None:
    print(result.caption)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `run_id_or_link` | `str` | Run identifier | Required |
| `ckpt` | `str` | Checkpoint name | `None` |
| `save_dir` | `str \| Path` | Save directory | Required |

**Returns:** [`ModelDownloadResult`](#modeldownloadresult)

---

## Response Types

### Model

Main model response object.

```python
from vi.api.resources.models.responses import Model
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `run_id` | `str` | Parent run ID |
| `organization_id` | `str` | Organization ID |
| `model_id` | `str` | Unique model identifier |
| `spec` | [`ModelSpec`](#modelspec) | Model specification |
| `status` | [`ModelStatus`](#modelstatus) | Model status |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted model information |

---

### ModelSpec

```python
from vi.api.resources.models.responses import ModelSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Model kind identifier |
| `epoch` | `int \| None` | Training epoch number |
| `evaluation_metrics` | `dict \| None` | Evaluation metrics (accuracy, loss, etc.) |

---

### ModelStatus

```python
from vi.api.resources.models.responses import ModelStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `observed_generation` | `int` | Observed generation number |
| `conditions` | `list[dict]` | Status conditions |
| `storage_object` | `str` | Storage location |
| `contents` | [`ModelContents`](#modelcontents)` \| None` | Download info when available |

---

### ModelContents

```python
from vi.api.resources.models.responses import ModelContents
```

| Property | Type | Description |
|----------|------|-------------|
| `download_url` | [`ModelDownloadUrl`](#modeldownloadurl) | Download URL info |

---

### ModelDownloadUrl

```python
from vi.api.resources.models.responses import ModelDownloadUrl
```

| Property | Type | Description |
|----------|------|-------------|
| `url` | `str` | Pre-signed download URL |
| `expires_at` | `int` | Expiration timestamp |

---

### ModelDownloadResult

Result from downloading a model.

| Property | Type | Description |
|----------|------|-------------|
| `model_path` | `Path` | Path to model weights |
| `adapter_path` | `Path \| None` | Path to adapter weights (if available) |
| `run_config_path` | `Path` | Path to run configuration |

---

## Downloaded Model Structure

```
models/
└── run_abc123/
    ├── model_full/          # Full model weights
    │   ├── config.json
    │   ├── model.safetensors
    │   └── ...
    ├── adapter/             # Adapter weights (if available)
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── ...
    └── run_config.json      # Run configuration
```

---

## See Also

- [Models Guide](vi-sdk-models) - Comprehensive guide
- [Inference Guide](vi-sdk-inference) - Using models
- [Runs API](vi-sdk-runs-api) - Training runs
- [Inference API](vi-sdk-api-inference) - Inference operations
- [Types API](vi-sdk-types) - Common types
