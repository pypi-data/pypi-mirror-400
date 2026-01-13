# Training and Downloading Models

Learn how to work with models, training runs, and download trained models for inference.

## Overview

The Vi SDK provides tools for:

- Listing training runs
- Getting run details and status
- Listing models from training runs
- Downloading trained models
- Working with model checkpoints
- Managing model metadata

## Training Runs

### Listing Runs

```python
import vi

client = vi.Client()

# List all training runs
runs = client.runs.list()

for run in runs.items:
    print(f"🏃 Run ID: {run.run_id}")
    print(f"   Created: {run.metadata.time_created}")

    # Check status
    if run.status.conditions:
        latest = run.status.conditions[-1]
        print(f"   Status: {latest.condition.value}")
```

### Iterate All Pages

```python
# Automatic pagination
for page in client.runs.list():
    for run in page.items:
        print(f"Processing run: {run.run_id}")
```

### Custom Page Size

```python
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=50)
runs = client.runs.list(pagination=pagination)
```

### Getting Run Details

```python
run = client.runs.get("run_abc123")

print(f"Run ID: {run.run_id}")
print(f"Owner: {run.owner}")
print(f"Created: {run.metadata.time_created}")

# Flow information
if run.spec.flow:
    print(f"Flow: {run.spec.flow.name}")

# Status conditions
for condition in run.status.conditions:
    print(f"Condition: {condition.condition.value}")
    print(f"Status: {condition.status.value}")
    print(f"Message: {condition.message}")
```

## Listing Models

### List Models for a Run

```python
# Get models from a training run
models = client.models.list("run_abc123")

for model in models.items:
    print(f"📦 Model ID: {model.model_id}")
    print(f"   Epoch: {model.spec.epoch}")

    # Evaluation metrics
    if model.spec.evaluation_metrics:
        print(f"   Metrics: {model.spec.evaluation_metrics}")
```

### Get Model Details

```python
# Get a specific checkpoint
model = client.models.get(
    run_id_or_link="run_abc123",
    ckpt="ckpt_10"
)

print(f"Model ID: {model.model_id}")
print(f"Epoch: {model.spec.epoch}")
print(f"Evaluation metrics: {model.spec.evaluation_metrics}")
print(f"Created: {model.metadata.time_created}")
```

## Downloading Models

### Download Latest Model

```python
# Download the latest checkpoint
downloaded = client.get_model(
    run_id="run_abc123"
)

print(f"✓ Model downloaded!")
print(f"Model path: {downloaded.model_path}")
print(f"Adapter path: {downloaded.adapter_path}")
print(f"Config: {downloaded.run_config_path}")
```

### Download Specific Checkpoint

```python
# Download a specific checkpoint
downloaded = client.get_model(
    run_id="run_abc123",
    ckpt="epoch_10"  # Specific checkpoint name
)
```

### Custom Save Location

```python
from pathlib import Path

# Save to custom directory
save_dir = Path("./my_models")
save_dir.mkdir(exist_ok=True)

downloaded = client.get_model(
    run_id="run_abc123",
    save_path=save_dir
)
```

### Download Without Progress

```python
# For CI/CD environments
downloaded = client.get_model(
    run_id="run_abc123",
    save_path="./models"
)
```

## Model Structure

Downloaded models have the following structure:

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

## Working with Downloaded Models

### Load for Inference

```python
from vi.inference import ViModel

# Load model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="run_abc123",
    device_map="auto",  # Automatically distribute across devices
    attn_implementation="flash_attention_2"  # Use flash attention if available
)

# Run inference
result = model(
    source="test.jpg",
    user_prompt="Describe this image"
)

print(result.caption)
```

!!! info "Supported Models and Tasks"
    **Currently Supported Models:**

    - Qwen2.5-VL (Qwen2_5_VLForConditionalGeneration)
    - InternVL 3.5 (InternVLForConditionalGeneration)
    - Cosmos Reason1 (Qwen2_5_VLForConditionalGeneration)
    - NVILA

    **Supported Task Types:**

    - **Visual Question Answering (VQA)**: User prompt is required in the form of a question
    - **Phrase Grounding**: User prompt is optional

    More models and task types will be supported in future releases.

See: [Inference Guide](inference.md)

## Managing Models

### List All Available Models

```python
def list_all_models():
    """List all models from all runs."""
    all_models = []

    # Get all runs
    for run_page in client.runs.list():
        for run in run_page.items:
            try:
                # Get models for this run
                models = client.models.list(run.run_id)
                all_models.extend(models.items)
            except Exception as e:
                print(f"Failed to list models for {run.run_id}: {e}")

    return all_models

models = list_all_models()
print(f"Found {len(models)} total models")
```

### Find Best Model

```python
def find_best_model(run_id, metric_name="accuracy"):
    """Find model with best metric value."""
    models = client.models.list(run_id)

    best_model = None
    best_value = float('-inf')

    for model in models.items:
        if not model.spec.evaluation_metrics:
            continue

        metric_value = model.spec.evaluation_metrics.get(metric_name, 0)
        if metric_value > best_value:
            best_value = metric_value
            best_model = model

    return best_model, best_value

# Usage
best, value = find_best_model("run_abc123", "accuracy")
if best:
    print(f"Best model: {best.model_id}")
    print(f"Accuracy: {value}")
```

### Download Multiple Models

```python
def download_models_from_runs(run_ids, save_dir="./models"):
    """Download models from multiple runs."""
    from pathlib import Path

    results = []

    for run_id in run_ids:
        try:
            downloaded = client.get_model(
                run_id=run_id,
                save_path=save_dir
            )
            results.append({
                "run_id": run_id,
                "model_path": downloaded.model_path,
                "success": True
            })
            print(f"✓ Downloaded model from {run_id}")
        except Exception as e:
            results.append({
                "run_id": run_id,
                "error": str(e),
                "success": False
            })
            print(f"✗ Failed to download from {run_id}: {e}")

    return results

# Usage
run_ids = ["run_1", "run_2", "run_3"]
results = download_models_from_runs(run_ids)
```

## Best Practices

### 1. Verify Model Download

```python
from pathlib import Path

def verify_model_download(downloaded_model):
    """Verify downloaded model has all required files."""
    # Check model directory exists
    model_path = Path(downloaded_model.model_path)
    if not model_path.exists():
        return False, "Model directory doesn't exist"

    # Check for config file
    config_file = model_path / "config.json"
    if not config_file.exists():
        return False, "Missing config.json"

    # Check for model weights
    weight_files = list(model_path.glob("*.safetensors")) + \
                   list(model_path.glob("*.bin"))
    if not weight_files:
        return False, "Missing model weights"

    return True, "Model is valid"

# Usage
downloaded = client.get_model("run_abc123")
valid, message = verify_model_download(downloaded)
if valid:
    print("✓ Model verified successfully")
else:
    print(f"✗ Verification failed: {message}")
```

### 2. Cache Downloaded Models

```python
from pathlib import Path

def get_or_download_model(run_id, save_dir="./models"):
    """Download model if not already cached."""
    model_dir = Path(save_dir) / run_id

    # Check if already downloaded
    if model_dir.exists() and (model_dir / "model_full").exists():
        print(f"Using cached model at {model_dir}")

        # Return cached model info
        return {
            "model_path": str(model_dir / "model_full"),
            "run_config_path": str(model_dir / "run_config.json"),
            "adapter_path": str(model_dir / "adapter") if (model_dir / "adapter").exists() else None
        }

    # Download
    print(f"Downloading model for {run_id}...")
    return client.get_model(run_id=run_id, save_path=save_dir)
```

### 3. Handle Download Errors

```python
from vi import ViError, ViNotFoundError, ViDownloadError

try:
    downloaded = client.get_model("run_abc123")
except ViNotFoundError as e:
    print(f"Model not found: {e.message}")
    # List available runs
    runs = client.runs.list()
except ViDownloadError as e:
    print(f"Download failed: {e.message}")
    # Check disk space, retry
except ViError as e:
    print(f"Error: {e.error_code}")
```

### 4. Monitor Training Progress

```python
import time

def wait_for_training_completion(run_id, check_interval=30, max_wait=3600):
    """Wait for training run to complete."""
    start_time = time.time()

    while time.time() - start_time < max_wait:
        run = client.runs.get(run_id)

        # Check latest condition
        if run.status.conditions:
            latest = run.status.conditions[-1]
            print(f"Status: {latest.condition.value}")

            if latest.condition.value in ["Succeeded", "Failed", "Error"]:
                return latest.condition.value

        time.sleep(check_interval)

    raise TimeoutError("Training took too long")

# Usage
status = wait_for_training_completion("run_abc123")
if status == "Succeeded":
    print("✓ Training completed successfully!")
    downloaded = client.get_model("run_abc123")
```

## Common Workflows

### Download and Evaluate

```python
def download_and_evaluate(run_id, test_dataset):
    """Download model and evaluate on test set."""
    # Download model
    downloaded = client.get_model(run_id=run_id)

    # Load for inference
    from vi.inference import ViModel

    model = ViModel(
        secret_key="your-secret-key",
        organization_id="your-organization-id",
        run_id=run_id
    )

    # Evaluate
    correct = 0
    total = 0

    for image_path, ground_truth in test_dataset:
        result, error = model(source=image_path, user_prompt="Describe this image")

        if error is None and result.caption == ground_truth:
            correct += 1
        total += 1

    accuracy = correct / total if total > 0 else 0
    print(f"Accuracy: {accuracy:.2%}")

    return accuracy
```

### Compare Multiple Models

```python
def compare_models(run_ids, test_images):
    """Compare performance of multiple models."""
    results = {}

    for run_id in run_ids:
        print(f"\nEvaluating {run_id}...")

        # Load model
        model = ViModel(
            secret_key="your-secret-key",
            organization_id="your-organization-id",
            run_id=run_id
        )

        # Run inference on test set
        predictions = []
        for image_path in test_images:
            result, error = model(source=image_path, user_prompt="Describe this image")
            if error is None:
                predictions.append(result.caption)
            else:
                predictions.append(None)  # Handle errors

        results[run_id] = predictions

    return results
```

## Troubleshooting

### Model Not Found

```python
# Check if run has models
models = client.models.list("run_abc123")

if not models.items:
    print("No models found for this run")
    print("Training may not have completed yet")
```

### Download Incomplete

If download is interrupted:

1. Delete partial download
2. Re-run download command
3. Verify using `verify_model_download()`

### Out of Disk Space

```python
import shutil

def check_disk_space(path="./models"):
    """Check available disk space."""
    usage = shutil.disk_usage(path)

    free_gb = usage.free / (1024**3)
    print(f"Free space: {free_gb:.2f} GB")

    if free_gb < 10:
        print("⚠️  Low disk space!")
        return False

    return True

# Check before downloading
if check_disk_space():
    downloaded = client.get_model("run_abc123")
```

## Performance Tips

- **Use cached models** when possible
- **Download in parallel** for multiple models
- **Verify checksums** after download
- **Clean up old models** to save space

## See Also

- [Inference Guide](inference.md) - Using downloaded models
- [Runs API Reference](../api/resources/runs.md) - Complete API documentation
- [Models API Reference](../api/resources/models.md) - Model operations
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Practical examples
