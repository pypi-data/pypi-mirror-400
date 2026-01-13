---
title: "Inference API Reference"
excerpt: "Load models and perform predictions with structured outputs"
category: "api-reference"
---

# Inference API Reference

Complete API reference for model inference. Load fine-tuned models and perform predictions with structured outputs.

> ℹ️ **Currently Supported**
>
> **Models:**
>
> - Qwen2.5-VL
> - InternVL 3.5
> - Cosmos Reason1
> - NVILA
>
> **Task Types:**
>
> - **Visual Question Answering (VQA)**: User prompt is required in the form of a question
> - **Phrase Grounding**: User prompt is optional
>
> More models and task types will be supported in future releases.

---

## ViModel (Recommended)

The `ViModel` class provides a unified interface for loading models and running inference.

### Constructor

```python
from vi.inference import ViModel

model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    device_map="auto",
    attn_implementation="flash_attention_2",
    dtype="float16",
    load_in_8bit=False,
    load_in_4bit=False
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `secret_key` | `str` | Vi API secret key | Required |
| `organization_id` | `str` | Organization identifier | Required |
| `run_id` | `str` | Run ID for the trained model | Required |
| `device_map` | `str` | Device mapping strategy | `"auto"` |
| `attn_implementation` | `str` | Attention implementation | `None` |
| `dtype` | `str` | Data type for model | `None` |
| `load_in_8bit` | `bool` | Enable 8-bit quantization | `False` |
| `load_in_4bit` | `bool` | Enable 4-bit quantization | `False` |
| `low_cpu_mem_usage` | `bool` | Optimize CPU memory | `True` |

---

### __call__

Run inference on images.

```python
# Single image
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image"
)

# Multiple images
results = model(
    source=["image1.jpg", "image2.jpg"],
    user_prompt="Describe this image",
    show_progress=True
)

# Folder
results = model(
    source="./images/",
    user_prompt="Describe this image",
    recursive=True
)
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `source` | `str \| list[str]` | Image path(s) or folder | Required |
| `user_prompt` | `str \| list[str]` | Prompt(s) for inference | `None` |
| `generation_config` | `dict` | Generation parameters | `None` |
| `show_progress` | `bool` | Show progress bar | `True` |
| `recursive` | `bool` | Search folders recursively | `False` |

**Returns:**

- Single image: `tuple[Result, Error]`
- Multiple images: `list[tuple[Result, Error]]`

---

### Generation Config Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_new_tokens` | `int` | `512` | Maximum tokens to generate |
| `temperature` | `float` | `1.0` | Sampling temperature |
| `top_p` | `float` | `1.0` | Nucleus sampling threshold |
| `top_k` | `int` | `50` | Top-k sampling parameter |
| `do_sample` | `bool` | `True` | Use sampling vs greedy |
| `repetition_penalty` | `float` | `1.0` | Penalty for repeating tokens |

**Example:**

```python
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image",
    generation_config={
        "max_new_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9
    }
)
```

---

## Task Types

### Visual Question Answering (VQA)

VQA requires a user prompt in the form of a question.

```python
result, error = model(
    source="image.jpg",
    user_prompt="What color is the car in this image?"
)

if error is None:
    print(f"Answer: {result.caption}")
```

**Result Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `caption` | `str` | Generated answer |

---

### Phrase Grounding

Phrase Grounding detects and locates objects. User prompt is optional.

```python
# With custom prompt
result, error = model(
    source="image.jpg",
    user_prompt="Identify all objects"
)

# Without prompt (uses default)
result, error = model(source="image.jpg")

if error is None and hasattr(result, 'grounded_phrases'):
    for phrase in result.grounded_phrases:
        print(f"Phrase: {phrase.phrase}")
        print(f"BBox: {phrase.bbox}")
```

**Result Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `caption` | `str` | Generated caption |
| `grounded_phrases` | `list[GroundedPhrase]` | List of grounded phrases |

**GroundedPhrase Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `phrase` | `str` | The detected phrase |
| `bbox` | `list[float]` | Normalized bounding box `[x_min, y_min, x_max, y_max]` |

---

## Batch Processing Examples

### Process Multiple Images

```python
images = ["image1.jpg", "image2.jpg", "image3.jpg"]

results = model(
    source=images,
    user_prompt="Describe this image",
    show_progress=True
)

for image, (result, error) in zip(images, results):
    if error is None:
        print(f"{image}: {result.caption}")
    else:
        print(f"{image} failed: {error}")
```

### Process Folder

```python
results = model(
    source="./images/",
    user_prompt="What's in this image?",
    recursive=True,
    show_progress=True
)

for result, error in results:
    if error is None:
        print(f"Caption: {result.caption}")
```

### Different Prompts Per Image

```python
images = ["car.jpg", "person.jpg", "building.jpg"]
prompts = [
    "What color is the car?",
    "How many people?",
    "What type of building?"
]

results = model(
    source=images,
    user_prompt=prompts,
    show_progress=True
)
```

---

## Memory Optimization

### 8-bit Quantization

```python
model = ViModel(
    secret_key="...",
    organization_id="...",
    run_id="...",
    load_in_8bit=True,
    device_map="auto"
)
```

### 4-bit Quantization

```python
model = ViModel(
    secret_key="...",
    organization_id="...",
    run_id="...",
    load_in_4bit=True,
    device_map="auto"
)
```

### Half Precision (FP16)

```python
model = ViModel(
    secret_key="...",
    organization_id="...",
    run_id="...",
    dtype="float16",
    device_map="auto"
)
```

---

## Error Handling

```python
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image"
)

if error is not None:
    if isinstance(error, FileNotFoundError):
        print("Image not found")
    elif "out of memory" in str(error):
        print("GPU out of memory")
        torch.cuda.empty_cache()
    else:
        print(f"Error: {error}")
else:
    print(f"Result: {result.caption}")
```

---

## See Also

- [Inference Guide](vi-sdk-inference) - Detailed inference guide
- [NIM Deployment Guide](vi-sdk-nim-deployment) - Deploy NIM containers
- [NIM Deployment API](vi-sdk-api-nim) - NIM API reference
- [Models Guide](vi-sdk-models) - Downloading models
- [Dataset Loaders](vi-sdk-api-dataset-loaders) - Loading data for inference
