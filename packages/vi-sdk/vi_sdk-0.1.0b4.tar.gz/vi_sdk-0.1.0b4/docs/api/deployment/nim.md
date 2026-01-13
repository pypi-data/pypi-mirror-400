# NIM Deployment API

Complete API reference for NVIDIA NIM container deployment and inference.

!!! info "Currently Supported"
    **NIM Images:** `cosmos-reason1-7b`

    **Task Types:**

    - **Phrase Grounding**: Detect and locate objects with bounding boxes
    - **Visual Question Answering (VQA)**: Answer questions about images

    More NIM images and task types will be supported in future releases.

!!! warning "LoRA Adapter Limitation"
    Models trained on Vi with LoRA adapters will only use the **full base model weights** when deployed with NIM. NVIDIA NIM does not currently support PEFT adapters, so LoRA adapter weights are not utilized.

## NIMDeployer

### NIMDeployer

::: vi.deployment.nim.NIMDeployer
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## NIMPredictor

### NIMPredictor

::: vi.deployment.nim.NIMPredictor
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Configuration

### NIMConfig

::: vi.deployment.nim.NIMConfig
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true

### NIMSamplingParams

::: vi.deployment.nim.NIMSamplingParams
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true

## Results

### NIMDeploymentResult

::: vi.deployment.nim.NIMDeploymentResult
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true

## Exceptions

### NIMDeploymentError

::: vi.deployment.nim.NIMDeploymentError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### InvalidConfigError

::: vi.deployment.nim.InvalidConfigError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ContainerExistsError

::: vi.deployment.nim.ContainerExistsError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ServiceNotReadyError

::: vi.deployment.nim.ServiceNotReadyError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ModelIncompatibilityError

::: vi.deployment.nim.ModelIncompatibilityError
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Quick Reference

### Basic Deployment

```python
from vi.deployment.nim import NIMDeployer, NIMConfig

# Default deployment (uses NGC_API_KEY env var)
deployer = NIMDeployer()
result = deployer.deploy()

# With custom config
config = NIMConfig(
    nvidia_api_key="nvapi-...",
    port=8000,
    stream_logs=True
)
deployer = NIMDeployer(config)
result = deployer.deploy()
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

### Stop Container

```python
from vi.deployment.nim import NIMDeployer

NIMDeployer.stop("cosmos-reason1-7b")
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NGC_API_KEY` | NVIDIA NGC API key for container registry |
| `DATATURE_VI_SECRET_KEY` | Vi SDK secret key for custom weights |
| `DATATURE_VI_ORGANIZATION_ID` | Vi organization ID for custom weights |

## See Also

- [User Guide: NIM Deployment](../../guide/nim-deployment.md)
- [User Guide: Inference](../../guide/inference.md)
- [Inference API](../inference/inference.md)
