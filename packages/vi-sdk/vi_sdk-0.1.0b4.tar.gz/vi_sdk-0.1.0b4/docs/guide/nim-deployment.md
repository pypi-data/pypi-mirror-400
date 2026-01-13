# NIM Deployment

Deploy and run NVIDIA NIM containers with fine-tuned models from Datature Vi.

## Overview

The Vi SDK provides tools for deploying NVIDIA NIM (NVIDIA Inference Microservices) containers, allowing you to:

- Deploy NIM containers with pre-trained base models
- Load fine-tuned custom weights from Datature Vi
- Run inference on images with OpenAI-compatible APIs
- Manage container lifecycle (start, stop, monitor)

!!! info "Currently Supported"
    **NIM Images:** `cosmos-reason1-7b`

    **Task Types:**

    - **Phrase Grounding**: Detect and locate objects with bounding boxes
    - **Visual Question Answering (VQA)**: Answer questions about images

    More NIM images and task types will be supported in future releases.

!!! warning "LoRA Adapter Limitation"
    Models trained on Vi with LoRA adapters will only use the **full base model weights** when deployed with NIM. NVIDIA NIM does not currently support PEFT (Parameter-Efficient Fine-Tuning) adapters, so **LoRA adapter weights are not utilized**. Only models trained with full fine-tuning will reflect their training in NIM deployments.

## Prerequisites

### Hardware Requirements

- NVIDIA GPU with CUDA support (GPU memory requirements vary by model)
- Docker with NVIDIA Container Toolkit installed

### Software Requirements

Install the SDK with NIM deployment dependencies:

```bash
pip install vi-sdk[nim]
```

This installs key dependencies including:

- `docker` - Docker SDK for Python
- `openai` - OpenAI Python client
- `httpx` - HTTP client
- `rich` - Terminal formatting

### NVIDIA NGC API Key

You need an NVIDIA NGC API key to pull NIM images from the NVIDIA Container Registry.

!!! tip "Get Your NGC API Key"
    Navigate to [https://org.ngc.nvidia.com/setup/api-keys](https://org.ngc.nvidia.com/setup/api-keys) to generate a Personal API Key. You'll need to be a member of an NGC organization to create one.

Set the API key as an environment variable:

```bash
export NGC_API_KEY="nvapi-..."
```

Or pass it directly in the configuration.

## Quick Start

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

# Deploy with base model (uses NGC_API_KEY environment variable)
deployer = NIMDeployer()
result = deployer.deploy()

print(f"Container running on port {result.port}")
print(f"Available models: {result.available_models}")

# Run inference
from vi.deployment.nim import NIMPredictor

predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="phrase-grounding"
)

result = predictor(source="image.jpg", stream=False)
print(f"Caption: {result.caption}")
for phrase in result.grounded_phrases:
    print(f"  {phrase.phrase}: {phrase.bbox}")
```

## Deployment

### Basic Deployment

Deploy with default settings using environment variables:

```python
from vi.deployment.nim import NIMDeployer

# Uses NGC_API_KEY environment variable
deployer = NIMDeployer()
result = deployer.deploy()

print(f"Container ID: {result.container_id}")
print(f"Container name: {result.container_name}")
print(f"Port: {result.port}")
```

### Custom Configuration

Configure deployment with `NIMConfig`:

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

config = NIMConfig(
    nvidia_api_key="nvapi-...",  # NGC API key
    image_name="cosmos-reason1-7b",  # NIM image
    tag="latest",  # Image tag
    port=8000,  # Port to expose
    shm_size="32GB",  # Shared memory size
    max_model_len=8192,  # Maximum model context length
    stream_logs=True,  # Stream container logs during startup
)

deployer = NIMDeployer(config)
result = deployer.deploy()
```

### Deploy with Custom Weights

Deploy with fine-tuned models from Datature Vi:

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

# Using explicit credentials
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    secret_key="your-vi-secret-key",
    organization_id="your-org-id",
    run_id="your-run-id",  # Run ID from Datature Vi
    ckpt="best",  # Optional: checkpoint to use
)

deployer = NIMDeployer(config)
result = deployer.deploy()

print(f"Serving model: {result.served_model_name}")
```

Using environment variables for Vi credentials:

```bash
export DATATURE_VI_SECRET_KEY="your-secret-key"
export DATATURE_VI_ORGANIZATION_ID="your-org-id"
export NGC_API_KEY="nvapi-..."
```

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

# Vi credentials loaded from environment variables
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    run_id="your-run-id",  # Model will be downloaded
)

deployer = NIMDeployer(config)
result = deployer.deploy()
```

### Quiet Mode

Suppress console output for scripts and CI/CD:

```python
# No console output
deployer = NIMDeployer(config, quiet=True)
result = deployer.deploy()
```

### Container Management Options

```python
config = NIMConfig(
    nvidia_api_key="nvapi-...",

    # Reuse existing container if it's already running
    use_existing_container=True,  # Default: True

    # Automatically stop and remove existing container
    auto_kill_existing_container=False,  # Default: False

    # Force re-pull image even if it exists locally
    force_pull=False,  # Default: False

    # Local cache directory for NIM
    local_cache_dir="~/.cache/nim",  # Default: ~/.cache/nim
)
```

### Stop Container

Stop a running NIM container:

```python
from vi.deployment.nim import NIMDeployer

# Stop by container name
success = NIMDeployer.stop("cosmos-reason1-7b")

if success:
    print("Container stopped successfully")
else:
    print("Container not found")

# Quiet mode
NIMDeployer.stop("cosmos-reason1-7b", quiet=True)
```

## Running Inference

### NIMPredictor

Use `NIMPredictor` to run inference on images:

```python
from vi.deployment.nim import NIMPredictor

# Create predictor for phrase grounding
predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="phrase-grounding",
    port=8000  # Port where NIM service is running
)

# Non-streaming inference
result = predictor(source="image.jpg", stream=False)

print(f"Caption: {result.caption}")
for phrase in result.grounded_phrases:
    print(f"  {phrase.phrase}: {phrase.bbox}")
```

### Streaming Inference

Stream tokens as they are generated:

```python
# Streaming inference
gen = predictor(source="image.jpg", stream=True)

# Print tokens as they arrive
for token in gen:
    print(token, end="", flush=True)

# Final result is returned by the generator
# (Access via StopIteration value or assign during iteration)
```

### VQA (Visual Question Answering)

```python
predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="vqa",
    port=8000
)

result = predictor(
    source="image.jpg",
    user_prompt="What objects are visible in this image?",
    stream=False
)

print(f"Answer: {result.caption}")
```

### Custom Prompts

Override the default prompt:

```python
result = predictor(
    source="image.jpg",
    user_prompt="Identify and locate all people in this image",
    stream=False
)
```

### Sampling Parameters

Control model generation with `NIMSamplingParams`:

```python
from vi.deployment.nim import NIMPredictor, NIMSamplingParams

# Create custom sampling configuration
params = NIMSamplingParams(
    temperature=0.7,  # Lower = more deterministic
    top_p=0.9,  # Nucleus sampling
    top_k=50,  # Top-k sampling
    max_tokens=1024,  # Maximum output tokens
    seed=42,  # For reproducibility
)

result = predictor(
    source="image.jpg",
    stream=False,
    sampling_params=params
)
```

### Guided Decoding

Constrain model output with guided decoding:

```python
# Constrain to specific choices
params = NIMSamplingParams(
    temperature=0.2,
    guided_choice=["yes", "no", "maybe"]
)

result = predictor(
    source="image.jpg",
    user_prompt="Is there a person in this image?",
    stream=False,
    sampling_params=params
)

# Or use JSON schema for structured output
params = NIMSamplingParams(
    guided_json={
        "type": "object",
        "properties": {
            "objects": {"type": "array", "items": {"type": "string"}},
            "count": {"type": "integer"}
        }
    }
)

# Or use regex pattern
params = NIMSamplingParams(
    guided_regex=r"^(cat|dog|bird)$"
)
```

## Configuration Reference

### NIMConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `nvidia_api_key` | str | - | NGC API key (required) |
| `image_name` | str | `"cosmos-reason1-7b"` | NIM image name |
| `tag` | str | `"latest"` | Image tag |
| `port` | int | `8000` | Port to expose |
| `shm_size` | str | `"32GB"` | Shared memory size |
| `max_model_len` | int | `8192` | Maximum model context length |
| `local_cache_dir` | str | `~/.cache/nim` | Local cache directory |
| `use_existing_container` | bool | `True` | Reuse existing container |
| `auto_kill_existing_container` | bool | `False` | Auto-remove existing container |
| `stream_logs` | bool | `True` | Stream logs during startup |
| `force_pull` | bool | `False` | Force image re-pull |
| `secret_key` | str | `None` | Vi SDK secret key |
| `organization_id` | str | `None` | Vi organization ID |
| `run_id` | str | `None` | Run ID for custom weights |
| `ckpt` | str | `None` | Checkpoint identifier |
| `model_save_path` | str | `~/.vi/models` | Model save directory |
| `served_model_name` | str | `None` | Name to serve model as |
| `overwrite` | bool | `False` | Re-download existing model |

### NIMSamplingParams

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | `1.0` | Sampling temperature (0.0 = deterministic) |
| `top_p` | float | `1.0` | Nucleus sampling threshold |
| `top_k` | int | `50` | Top-k sampling parameter |
| `min_p` | float | `0.0` | Minimum probability threshold |
| `presence_penalty` | float | `0.0` | Penalty for token presence |
| `frequency_penalty` | float | `0.0` | Penalty for token frequency |
| `repetition_penalty` | float | `1.05` | Penalty for repetition |
| `max_tokens` | int | `1024` | Maximum tokens to generate |
| `min_tokens` | int | `0` | Minimum tokens before stop |
| `stop` | str/list | `None` | Stop sequences |
| `seed` | int | `None` | Random seed |
| `ignore_eos` | bool | `False` | Ignore end-of-sequence token |
| `logprobs` | int | `None` | Number of log probabilities |
| `guided_json` | str/dict | `None` | JSON schema for output |
| `guided_regex` | str | `None` | Regex pattern for output |
| `guided_choice` | list | `None` | Valid output choices |
| `guided_grammar` | str | `None` | Grammar for output |

## Complete Workflow Example

```python
from vi.deployment.nim import NIMDeployer, NIMConfig, NIMPredictor, NIMSamplingParams

# Step 1: Configure deployment with custom weights
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    secret_key="your-vi-secret-key",
    organization_id="your-org-id",
    run_id="your-run-id",
    port=8000,
    stream_logs=True,
)

# Step 2: Deploy the container
deployer = NIMDeployer(config)
result = deployer.deploy()

print(f"Deployed container: {result.container_name}")
print(f"Port: {result.port}")
print(f"Served model: {result.served_model_name}")

# Step 3: Create predictor
predictor = NIMPredictor(
    model_name=result.served_model_name or "cosmos-reason1-7b",
    task_type="phrase-grounding",
    port=result.port
)

# Step 4: Run inference
params = NIMSamplingParams(temperature=0.7, max_tokens=512)
inference_result = predictor(
    source="test_image.jpg",
    stream=False,
    sampling_params=params
)

print(f"\nCaption: {inference_result.caption}")
for phrase in inference_result.grounded_phrases:
    print(f"  {phrase.phrase}: {phrase.bbox}")

# Step 5: Stop container when done
NIMDeployer.stop(result.container_name)
```

## Batch Inference

Process multiple images:

```python
from pathlib import Path

# Get all images in a folder
image_folder = Path("./images")
images = list(image_folder.glob("*.jpg"))

results = []
for image_path in images:
    result = predictor(source=str(image_path), stream=False)
    results.append({
        "image": image_path.name,
        "caption": result.caption,
        "grounded_phrases": [
            {"phrase": p.phrase, "bbox": p.bbox}
            for p in result.grounded_phrases
        ]
    })

# Save results
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Error Handling

### Deployment Errors

```python
from vi.deployment.nim import (
    NIMDeployer,
    NIMConfig,
    InvalidConfigError,
    ContainerExistsError,
    ModelIncompatibilityError,
)

config = NIMConfig(nvidia_api_key="nvapi-...")

try:
    deployer = NIMDeployer(config)
    result = deployer.deploy()
except InvalidConfigError as e:
    print(f"Configuration error: {e}")
except ContainerExistsError as e:
    print(f"Container already exists: {e.container_name}")
    print("Set use_existing_container=True or auto_kill_existing_container=True")
except ModelIncompatibilityError as e:
    print(f"Model incompatible with container: {e.image_name}")
    print(f"Details: {e.details}")
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidConfigError` | Invalid API key or config | Check NGC_API_KEY format starts with `nvapi-` |
| `ContainerExistsError` | Container already running | Use `use_existing_container=True` or stop existing |
| `ModelIncompatibilityError` | Model architecture mismatch | Check model is compatible with NIM image |
| `ServiceNotReadyError` | Service startup timeout | Increase timeout or check container logs |

## Troubleshooting

### Container Won't Start

1. Check Docker is running:
   ```bash
   docker info
   ```

2. Verify NVIDIA runtime:
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
   ```

3. Check container logs:
   ```bash
   docker logs cosmos-reason1-7b
   ```

### Service Not Ready

The service may take several minutes to initialize, especially on first run:

```python
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    stream_logs=True,  # Watch initialization progress
)
```

### Out of Memory

Reduce model context length:

```python
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    max_model_len=4096,  # Reduce from default 8192
    shm_size="16GB",  # Adjust shared memory
)
```

### Port Already in Use

Use a different port:

```python
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    port=8080,  # Use different port
)

predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="phrase-grounding",
    port=8080  # Match the config port
)
```

## Best Practices

### 1. Use Environment Variables

```python
import os

config = NIMConfig(
    nvidia_api_key=os.environ.get("NGC_API_KEY"),
    secret_key=os.environ.get("DATATURE_VI_SECRET_KEY"),
    organization_id=os.environ.get("DATATURE_VI_ORGANIZATION_ID"),
    run_id="your-run-id",
)
```

### 2. Reuse Predictor

```python
# ✅ Good - create once, reuse
predictor = NIMPredictor(model_name="cosmos-reason1-7b", task_type="phrase-grounding")

for image in images:
    result = predictor(source=image, stream=False)

# ❌ Bad - recreate for each image
for image in images:
    predictor = NIMPredictor(...)  # Wasteful
    result = predictor(source=image, stream=False)
```

### 3. Clean Up Containers

```python
# Stop container when done
try:
    # Your inference code
    pass
finally:
    NIMDeployer.stop("cosmos-reason1-7b")
```

### 4. Use Quiet Mode in Production

```python
# Suppress console output in production/CI
deployer = NIMDeployer(config, quiet=True)
```

## See Also

- [Inference Guide](inference.md) - Local model inference
- [Models Guide](models.md) - Downloading models
- [API Reference: NIM](../api/deployment/nim.md) - Complete API documentation
