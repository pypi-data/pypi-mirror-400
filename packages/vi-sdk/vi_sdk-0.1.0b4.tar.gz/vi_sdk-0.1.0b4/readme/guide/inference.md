---
title: "Running Inference with Models"
excerpt: "Load models and run inference on images"
category: "guide"
---

# Running Inference with Models

Learn how to load models and run inference on images using the Vi SDK.

---

## Overview

The Vi SDK provides tools for:

- Loading trained models locally
- Running inference with vision-language models
- Visual question answering (VQA)
- Phrase grounding
- Caption generation
- Batch processing

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

## Prerequisites

Install the SDK with inference dependencies:

```bash
pip install vi-sdk[inference]
```

This installs key base dependencies for inference, including:

- `torch` and `torchvision` - PyTorch
- `transformers` - Hugging Face Transformers
- `xgrammar` - Structured output generation
- `accelerate` - Model acceleration utilities
- `bitsandbytes` - Quantization support
- `peft` - Parameter-efficient fine-tuning

---

## Quick Start

```python
from vi.inference import ViModel

# Initialize model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)

# Run inference - returns (result, error) tuple
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image"
)

if error is None:
    print(result.caption)
else:
    print(f"Inference failed: {error}")
```

---

## Loading Models

### Basic Model Loading

```python
from vi.inference import ViModel

# Load model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)
```

### Advanced Loading Options

```python
# Load with custom configuration
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    device_map="auto",  # Automatically distribute across GPUs
    attn_implementation="flash_attention_2",  # Use Flash Attention 2
    dtype="float16",  # Use FP16 for faster inference
    low_cpu_mem_usage=True,  # Optimize CPU memory usage
    load_in_8bit=False,  # 8-bit quantization
    load_in_4bit=False,  # 4-bit quantization
)
```

### Device Management

```python
import torch

# Check available devices
if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name(0)}")
    device = "cuda"
else:
    print("Using CPU")
    device = "cpu"

# Load on specific device
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    device_map=device
)
```

### Memory-Efficient Loading

```python
# For large models, use quantization
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    load_in_8bit=True,  # 8-bit quantization
    device_map="auto"
)
```

---

## Running Inference

The ViModel class handles both model loading and prediction automatically. You can call the model directly for inference.

### Visual Question Answering

Visual Question Answering (VQA) requires a user prompt in the form of a question.

```python
# Ask questions about the image (user prompt is required for VQA)
result, error = model(
    source="image.jpg",
    user_prompt="What color is the car in this image?"
)

if error is None:
    print(f"Answer: {result.caption}")
else:
    print(f"Error: {error}")
```

### Phrase Grounding

For Phrase Grounding, the user prompt is optional. If not provided, the model uses its default curated prompt to detect and locate all objects in the image.

```python
# Detect and locate objects (user prompt is optional for Phrase Grounding)
result, error = model(
    source="image.jpg",
    user_prompt="Identify and locate all people in this image"  # Optional
)

# Or without a custom prompt
result, error = model(source="image.jpg")  # Uses default prompt

if error is None and hasattr(result, 'grounded_phrases'):
    for phrase in result.grounded_phrases:
        print(f"Phrase: {phrase.phrase}")
        print(f"BBox: {phrase.bbox}")
```

### Custom Prompts

```python
# Use custom prompts for specific tasks
prompts = [
    "List all objects visible in this image",
    "Describe the scene, including lighting and atmosphere",
    "What is the main subject doing?",
    "Identify any text visible in the image"
]

for prompt in prompts:
    result, error = model(
        source="image.jpg",
        user_prompt=prompt
    )
    print(f"\nPrompt: {prompt}")
    if error is None:
        print(f"Response: {result.caption}")
    else:
        print(f"Error: {error}")
```

---

## Inference Parameters

### Generation Configuration

Control how the model generates text using the `generation_config` parameter:

```python
# Configure generation parameters using generation_config
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image",
    generation_config={
        "max_new_tokens": 256,  # Maximum tokens to generate
        "temperature": 0.7,  # Sampling temperature (0.0-1.0)
        "top_p": 0.9,  # Nucleus sampling parameter
        "do_sample": True,  # Use sampling vs greedy decoding
    }
)
```

**Common Generation Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_new_tokens` | int | 512 | Maximum number of tokens to generate |
| `temperature` | float | 1.0 | Controls randomness (0.0 = deterministic, higher = more random) |
| `top_p` | float | 1.0 | Nucleus sampling threshold |
| `top_k` | int | 50 | Top-k sampling parameter |
| `do_sample` | bool | True | Use sampling vs greedy decoding |
| `repetition_penalty` | float | 1.0 | Penalty for repeating tokens |

### Controlling Output Length

```python
# Short caption
result, error = model(
    source="image.jpg",
    user_prompt="Provide a brief caption",
    generation_config={"max_new_tokens": 50}
)

# Detailed description
result, error = model(
    source="image.jpg",
    user_prompt="Provide a detailed description",
    generation_config={"max_new_tokens": 500}
)
```

### Deterministic Inference

```python
# For reproducible results
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image",
    generation_config={
        "temperature": 0.0,  # Deterministic
        "do_sample": False  # Greedy decoding
    }
)
```

---

## Batch Inference

### Native Batch Support

The Vi SDK provides native batch inference with automatic progress tracking and error handling:

```python
from pathlib import Path

# Prepare image paths
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]

# Run batch inference - automatically handles progress and errors
results = model(
    source=image_paths,
    user_prompt="Describe this image",
    show_progress=True  # Shows progress bar (default)
)

# Process results - each item is a (result, error) tuple
for i, (result, error) in enumerate(results):
    if error is None:
        print(f"Image {i+1}: {result.caption}")
    else:
        print(f"Image {i+1} failed: {error}")
```

### Process Entire Folders

Automatically process all images in a folder:

```python
# Process all images in a folder
results = model(
    source="./my_images/",
    user_prompt="Describe this image",
    show_progress=True
)

# Process results
for result, error in results:
    if error is None:
        print(f"Caption: {result.caption}")
    else:
        print(f"Error: {error}")
```

**Supported image formats**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`, `.tif`, `.webp`

### Recursive Directory Search

Search subdirectories recursively with the `recursive` parameter:

```python
# Process all images in folder and subdirectories
results = model(
    source="./dataset/",
    user_prompt="What's in this image?",
    recursive=True,  # Search subdirectories recursively
    show_progress=True
)

print(f"Processed {len(results)} images across all subdirectories")
```

### Mix Files and Folders

You can mix individual files and folders in the same call:

```python
# Mix files and folders
results = model(
    source=[
        "./image1.jpg",        # Single file
        "./folder1/",          # All images in folder1
        "~/Pictures/photo.png", # User path
        "./dataset/",          # All images in dataset
    ],
    user_prompt="Analyze this image",
    recursive=False  # Only immediate folder contents
)
```

### Batch with Different Prompts

You can provide different prompts for each image:

```python
images = ["car.jpg", "person.jpg", "building.jpg"]
prompts = [
    "What color is the car?",
    "How many people are visible?",
    "What type of building is this?"
]

# Each image gets its own prompt
results = model(
    source=images,
    user_prompt=prompts,
    show_progress=True
)

for image, prompt, (result, error) in zip(images, prompts, results):
    if error is None:
        print(f"{image} - {prompt}: {result.caption}")
    else:
        print(f"{image} failed: {error}")
```

### Process and Save Results

```python
import json

# Process folder directly (much simpler!)
results = model(
    source="./images/",  # Just pass the folder path
    user_prompt="Describe this image",
    show_progress=True
)

# Save results
output = []
for result, error in results:
    output.append({
        "caption": result.caption if error is None else None,
        "error": str(error) if error else None
    })

with open("results.json", "w") as f:
    json.dump(output, f, indent=2)

# Summary
successful = sum(1 for _, error in results if error is None)
print(f"Processed {len(results)} images: {successful} successful, {len(results) - successful} failed")
```

---

## Working with Results

### Access Result Data

```python
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image"
)

if error is not None:
    print(f"Inference failed: {error}")
else:
    # Caption/answer
    if hasattr(result, 'caption'):
        print(f"Caption: {result.caption}")

    # Grounded phrases (if available)
    if hasattr(result, 'grounded_phrases'):
        for phrase in result.grounded_phrases:
            print(f"Phrase: {phrase.phrase}")
            print(f"BBox: {phrase.bbox}")
```

### Convert Bounding Boxes

```python
from PIL import Image

def convert_bbox_to_pixels(bbox, image_path):
    """Convert normalized bbox to pixel coordinates."""
    image = Image.open(image_path)
    width, height = image.size

    x_min, y_min, x_max, y_max = bbox

    return [
        int(x_min * width),
        int(y_min * height),
        int(x_max * width),
        int(y_max * height)
    ]

# Usage
result, error = model(source="image.jpg", user_prompt="Find all objects")
if error is None and hasattr(result, 'grounded_phrases'):
    for phrase in result.grounded_phrases:
        pixel_bbox = convert_bbox_to_pixels(phrase.bbox, "image.jpg")
        print(f"{phrase.phrase}: {pixel_bbox}")
```

### Visualize Results

```python
from PIL import Image, ImageDraw

def visualize_result(image_path, result, output_path="output.jpg"):
    """Visualize inference result with bounding boxes."""
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Draw grounded phrases
    if hasattr(result, 'grounded_phrases'):
        for phrase in result.grounded_phrases:
            # Convert to pixel coordinates
            width, height = image.size
            x_min = phrase.bbox[0] * width
            y_min = phrase.bbox[1] * height
            x_max = phrase.bbox[2] * width
            y_max = phrase.bbox[3] * height

            # Draw rectangle
            draw.rectangle(
                [(x_min, y_min), (x_max, y_max)],
                outline='red',
                width=3
            )

            # Draw text
            draw.text((x_min, y_min - 10), phrase.phrase, fill='red')

    # Add caption
    if hasattr(result, 'caption'):
        draw.text((10, 10), result.caption[:100], fill='white')

    # Save
    image.save(output_path)
    print(f"Saved visualization to {output_path}")

# Usage
result, error = model(source="image.jpg", user_prompt="Detect objects")
if error is None:
    visualize_result("image.jpg", result, "output.jpg")
else:
    print(f"Inference failed: {error}")
```

---

## Best Practices

### 1. Reuse Model

```python
# ✅ Good - create once, reuse
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)

for image in images:
    result, error = model(source=image, user_prompt="...")

# ❌ Bad - recreate for each image
for image in images:
    model = ViModel(...)  # Wasteful
    result, error = model(source=image, user_prompt="...")
```

### 2. Optimize Memory Usage

```python
import gc
import torch

# Clear cache periodically
for i, image in enumerate(images):
    result, error = model(source=image, user_prompt="...")

    if i % 100 == 0:
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
```

### 3. Handle Errors Gracefully

```python
for image in images:
    result, error = model(
        source=image,
        user_prompt="Describe this image"
    )

    if error is None:
        # Process successful result
        print(f"Success: {result.caption}")
    else:
        # Handle error
        if isinstance(error, FileNotFoundError):
            print(f"Image not found: {image}")
        elif "out of memory" in str(error):
            print(f"Out of memory: {image}")
            torch.cuda.empty_cache()
        else:
            print(f"Error: {error}")
```

---

## Performance Optimization

### GPU Utilization

```python
import torch

# Check GPU utilization
if torch.cuda.is_available():
    print(f"GPU Memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print(f"GPU Memory cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

### Mixed Precision

```python
# Use FP16 for faster inference
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    dtype="float16",  # Half precision
    device_map="auto"
)
```

### Quantization

```python
# Use 8-bit quantization for lower memory
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    load_in_8bit=True,  # 8-bit quantization
    device_map="auto"
)
```

---

## Common Workflows

### Dataset Annotation

```python
def annotate_dataset(image_dir, output_file, recursive=False):
    """Generate annotations for unlabeled images."""
    import json

    # Process entire folder directly
    results = model(
        source=image_dir,
        user_prompt="Describe this image concisely",
        recursive=recursive,
        show_progress=True
    )

    annotations = []
    for result, error in results:
        if error is not None:
            print(f"Skipping image: {error}")
            continue

        annotation = {
            "caption": result.caption
        }

        # Add grounded phrases if available
        if hasattr(result, 'grounded_phrases'):
            annotation["grounded_phrases"] = [
                {
                    "phrase": p.phrase,
                    "bbox": p.bbox
                }
                for p in result.grounded_phrases
            ]

        annotations.append(annotation)

    # Save annotations
    with open(output_file, 'w') as f:
        json.dump(annotations, f, indent=2)

    print(f"Generated {len(annotations)} annotations")

# Usage - process folder directly
annotate_dataset("./images", "annotations.json")
```

---

## Troubleshooting

### Out of Memory

```python
# Check for out of memory errors
result, error = model(source="large_image.jpg", user_prompt="...")

if error and "out of memory" in str(error):
    # Clear cache and retry
    torch.cuda.empty_cache()

    # Or use quantization
    model = ViModel(
        secret_key="your-secret-key",
        organization_id="your-organization-id",
        run_id="your-run-id",
        load_in_8bit=True
    )

    # Retry
    result, error = model(source="large_image.jpg", user_prompt="...")
```

### Slow Inference

1. Use GPU if available
2. Enable Flash Attention 2
3. Use FP16 precision
4. Use quantization
5. Batch similar-sized images

---

## See Also

- [Models Guide](vi-sdk-models) - Downloading models
- [NIM Deployment](vi-sdk-nim-deployment) - Deploy NVIDIA NIM containers
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Complete inference examples
- [API Reference](vi-sdk-api-inference) - Inference API documentation
