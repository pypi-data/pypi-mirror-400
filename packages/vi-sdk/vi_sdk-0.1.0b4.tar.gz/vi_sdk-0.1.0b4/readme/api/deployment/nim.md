---
title: "NIM Deployment API Reference"
excerpt: "NVIDIA NIM container deployment and inference API"
category: "api-reference"
---

# NIM Deployment API Reference

Complete API reference for NVIDIA NIM container deployment and inference.

> ℹ️ **Currently Supported**
>
> **NIM Images:** `cosmos-reason1-7b`
>
> **Task Types:**
>
> - **Phrase Grounding**: Detect and locate objects with bounding boxes
> - **Visual Question Answering (VQA)**: Answer questions about images
>
> More NIM images and task types will be supported in future releases.

> ⚠️ **LoRA Adapter Limitation**
>
> Models trained on Vi with LoRA adapters will only use the **full base model weights** when deployed with NIM. NVIDIA NIM does not currently support PEFT adapters, so LoRA adapter weights are not utilized.

---

## NIMDeployer

Manages NVIDIA NIM container deployment lifecycle.

### Constructor

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

# Default deployment (uses NGC_API_KEY env var)
deployer = NIMDeployer()

# With custom config
config = NIMConfig(nvidia_api_key="nvapi-...", port=8000)
deployer = NIMDeployer(config)

# Quiet mode (no console output)
deployer = NIMDeployer(config, quiet=True)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `config` | `NIMConfig \| None` | Deployment configuration | `None` |
| `quiet` | `bool` | Suppress console output | `False` |

---

### deploy()

Deploy a NIM container with optional custom weights.

```python
result = deployer.deploy()

print(f"Container ID: {result.container_id}")
print(f"Container name: {result.container_name}")
print(f"Port: {result.port}")
print(f"Served model: {result.served_model_name}")
print(f"Available models: {result.available_models}")
```

**Returns:** `NIMDeploymentResult`

**Raises:**

| Exception | Description |
|-----------|-------------|
| `InvalidConfigError` | Configuration is invalid |
| `ContainerExistsError` | Container exists and not configured to reuse/kill |
| `ModelIncompatibilityError` | Model incompatible with container |
| `APIError` | Docker operations fail |

---

### stop()

*classmethod*

Stop a running NIM container.

```python
from vi.deployment.nim import NIMDeployer

success = NIMDeployer.stop("cosmos-reason1-7b")

if success:
    print("Container stopped")
else:
    print("Container not found")

# Quiet mode
NIMDeployer.stop("cosmos-reason1-7b", quiet=True)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `container_name` | `str` | Container name or ID | Required |
| `quiet` | `bool` | Suppress console output | `False` |

**Returns:** `bool` - True if stopped, False if not found

---

## NIMPredictor

Predictor for running inference on NIM containers.

### Constructor

```python
from vi.deployment.nim import NIMPredictor

predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="phrase-grounding",
    port=8000
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model_name` | `str` | Name of the NIM model | Required |
| `task_type` | `str` | Task type (`"phrase-grounding"`, `"vqa"`) | Required |
| `port` | `int` | Port where NIM service runs | `8000` |

---

### __call__()

Run inference on an image.

```python
# Non-streaming
result = predictor(
    source="image.jpg",
    user_prompt="Describe this image",
    stream=False,
    sampling_params=None
)

# Streaming
gen = predictor(source="image.jpg", stream=True)
for token in gen:
    print(token, end="", flush=True)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `source` | `str` | Path to the input image | Required |
| `user_prompt` | `str \| None` | Custom prompt | `None` |
| `stream` | `bool` | Stream the response | `False` |
| `sampling_params` | `NIMSamplingParams \| None` | Sampling configuration | `None` |

**Returns:**

- Non-streaming: `PredictionResponse` (task-specific result)
- Streaming: `Generator[str, None, PredictionResponse]`

---

## NIMConfig

Configuration for NIM deployment.

### Constructor

```python
from vi.deployment.nim import NIMConfig

config = NIMConfig(
    nvidia_api_key="nvapi-...",
    image_name="cosmos-reason1-7b",
    tag="latest",
    port=8000,
    shm_size="32GB",
    max_model_len=8192,
    local_cache_dir=None,
    use_existing_container=True,
    auto_kill_existing_container=False,
    stream_logs=True,
    force_pull=False,
    secret_key=None,
    organization_id=None,
    run_id=None,
    ckpt=None,
    model_save_path="~/.vi/models",
    served_model_name=None,
    overwrite=False
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `nvidia_api_key` | `str` | NGC API key | Required |
| `image_name` | `str` | NIM image name | `"cosmos-reason1-7b"` |
| `tag` | `str` | Image tag | `"latest"` |
| `port` | `int` | Port to expose | `8000` |
| `shm_size` | `str` | Shared memory size | `"32GB"` |
| `max_model_len` | `int` | Maximum model context | `8192` |
| `local_cache_dir` | `str \| None` | Local cache directory | `~/.cache/nim` |
| `use_existing_container` | `bool` | Reuse existing container | `True` |
| `auto_kill_existing_container` | `bool` | Auto-remove existing | `False` |
| `stream_logs` | `bool` | Stream container logs | `True` |
| `force_pull` | `bool` | Force image re-pull | `False` |
| `secret_key` | `str \| None` | Vi SDK secret key | `None` |
| `organization_id` | `str \| None` | Vi organization ID | `None` |
| `run_id` | `str \| None` | Run ID for custom weights | `None` |
| `ckpt` | `str \| None` | Checkpoint identifier | `None` |
| `model_save_path` | `str \| Path` | Model save directory | `~/.vi/models` |
| `served_model_name` | `str \| None` | Name to serve model as | `None` |
| `overwrite` | `bool` | Re-download existing model | `False` |

---

## NIMSamplingParams

Sampling parameters for NIM model generation.

### Constructor

```python
from vi.deployment.nim import NIMSamplingParams

params = NIMSamplingParams(
    temperature=1.0,
    top_p=1.0,
    top_k=50,
    min_p=0.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    repetition_penalty=1.05,
    max_tokens=1024,
    min_tokens=0,
    stop=None,
    seed=None,
    ignore_eos=False,
    logprobs=None,
    prompt_logprobs=None,
    guided_json=None,
    guided_regex=None,
    guided_choice=None,
    guided_grammar=None
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `temperature` | `float` | Sampling temperature (0.0 = deterministic) | `1.0` |
| `top_p` | `float` | Nucleus sampling threshold | `1.0` |
| `top_k` | `int` | Top-k sampling | `50` |
| `min_p` | `float` | Minimum probability threshold | `0.0` |
| `presence_penalty` | `float` | Penalty for token presence | `0.0` |
| `frequency_penalty` | `float` | Penalty for token frequency | `0.0` |
| `repetition_penalty` | `float` | Penalty for repetition | `1.05` |
| `max_tokens` | `int` | Maximum tokens to generate | `1024` |
| `min_tokens` | `int` | Minimum tokens before stop | `0` |
| `stop` | `str \| list \| None` | Stop sequences | `None` |
| `seed` | `int \| None` | Random seed | `None` |
| `ignore_eos` | `bool` | Ignore end-of-sequence | `False` |
| `logprobs` | `int \| None` | Number of log probabilities | `None` |
| `prompt_logprobs` | `int \| None` | Prompt log probabilities | `None` |
| `guided_json` | `str \| dict \| None` | JSON schema for output | `None` |
| `guided_regex` | `str \| None` | Regex pattern for output | `None` |
| `guided_choice` | `list \| None` | Valid output choices | `None` |
| `guided_grammar` | `str \| None` | Grammar for output | `None` |

---

## NIMDeploymentResult

Result of NIM container deployment.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `container_id` | `str` | Docker container ID |
| `container_name` | `str` | Name of the running container |
| `served_model_name` | `str \| None` | Name the model is served as |
| `port` | `int` | Port the container is exposed on |
| `available_models` | `list[str] \| None` | List of available model IDs |

---

## Exceptions

### NIMDeploymentError

Base exception for NIM deployment errors.

```python
from vi.deployment.nim import NIMDeploymentError

try:
    deployer.deploy()
except NIMDeploymentError as e:
    print(f"Deployment failed: {e}")
```

---

### InvalidConfigError

Raised when configuration is invalid.

```python
from vi.deployment.nim import InvalidConfigError

try:
    deployer.deploy()
except InvalidConfigError as e:
    print(f"Invalid config: {e}")
```

---

### ContainerExistsError

Raised when a container with the same name already exists.

```python
from vi.deployment.nim import ContainerExistsError

try:
    deployer.deploy()
except ContainerExistsError as e:
    print(f"Container exists: {e.container_name}")
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `container_name` | `str` | Name of the existing container |

---

### ServiceNotReadyError

Raised when NIM service fails to become ready within timeout.

```python
from vi.deployment.nim import ServiceNotReadyError

try:
    deployer.deploy()
except ServiceNotReadyError as e:
    print(f"Service not ready: {e.container_name}")
    print(f"Timeout: {e.timeout} seconds")
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `container_name` | `str` | Name of the container |
| `timeout` | `int` | Timeout value that was exceeded |

---

### ModelIncompatibilityError

Raised when a custom model is incompatible with the target container.

```python
from vi.deployment.nim import ModelIncompatibilityError

try:
    deployer.deploy()
except ModelIncompatibilityError as e:
    print(f"Model incompatible with: {e.image_name}")
    print(f"Details: {e.details}")
```

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `image_name` | `str` | Name of the container image |
| `details` | `str \| None` | Error details |

---

## Examples

### Basic Deployment

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

config = NIMConfig(nvidia_api_key="nvapi-...")
deployer = NIMDeployer(config)
result = deployer.deploy()

print(f"Running on port {result.port}")
```

### Deploy with Custom Weights

```python
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    secret_key="your-vi-key",
    organization_id="your-org-id",
    run_id="your-run-id"
)
deployer = NIMDeployer(config)
result = deployer.deploy()
```

### Run Inference

```python
from vi.deployment.nim import NIMPredictor, NIMSamplingParams

predictor = NIMPredictor(
    model_name="cosmos-reason1-7b",
    task_type="phrase-grounding",
    port=8000
)

# Simple inference
result = predictor(source="image.jpg", stream=False)

# With sampling params
params = NIMSamplingParams(temperature=0.7, max_tokens=512)
result = predictor(source="image.jpg", stream=False, sampling_params=params)
```

### Guided Decoding

```python
# Constrain output to choices
params = NIMSamplingParams(
    guided_choice=["yes", "no", "maybe"]
)
result = predictor(
    source="image.jpg",
    user_prompt="Is there a person?",
    stream=False,
    sampling_params=params
)
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NGC_API_KEY` | NVIDIA NGC API key for container registry |
| `DATATURE_VI_SECRET_KEY` | Vi SDK secret key for custom weights |
| `DATATURE_VI_ORGANIZATION_ID` | Vi organization ID for custom weights |

---

## See Also

- [NIM Deployment Guide](vi-sdk-nim-deployment) - Comprehensive guide
- [Inference Guide](vi-sdk-inference) - Local model inference
- [Inference API](vi-sdk-api-inference) - Inference API reference
