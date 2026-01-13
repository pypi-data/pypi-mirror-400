# Model Download and Inference

This example demonstrates how to download trained models and run inference using the Vi SDK.

## Overview

Learn how to:

- Download trained models from runs
- Load models for inference
- Run predictions on images
- Batch inference processing
- Generate structured outputs

## Source Code

[View full source on GitHub](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/examples/04_model_download_and_inference.py)

## Code Walkthrough

### 1. List Available Models

```python
import os
import vi

client = vi.Client(
    secret_key="YOUR_DATATURE_VI_SECRET_KEY",
    organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
)

# List runs (which contain trained models)
runs = client.runs.list()

for run in runs.items:
    print(f"Run ID: {run.run_id}")
    print(f"Status: {run.status}")
    print(f"Created: {run.time_created}")
```

### 2. Load Model for Inference

```python
from vi.inference import ViModel

# Load model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)
```

### 3. Run Single Image Inference

```python
# Run inference on a single image - returns (result, error) tuple
result, error = model(
    source="test_image.jpg",
    user_prompt="Describe this image in detail"
)

if error is None:
    print(f"Prediction: {result}")
else:
    print(f"Error: {error}")
```

### 4. Batch Inference

**Option 1: Process entire folder**

```python
# Process all images in a folder directly - much simpler!
results = model(
    source="./test_images/",  # Just pass the folder path
    user_prompt="What objects are in this image?",
    show_progress=True
)

# Process results - each is a (result, error) tuple
output = []
for result, error in results:
    if error is None:
        output.append({"prediction": str(result)})
        print(f"✓ Processed successfully")
    else:
        print(f"✗ Failed: {error}")
```

**Option 2: Process specific files**

```python
from pathlib import Path

# Process multiple images using native batch support
image_dir = Path("./test_images")
image_files = [str(p) for p in image_dir.glob("*.jpg")]

# Native batch inference with progress tracking
results = model(
    source=image_files,
    user_prompt="What objects are in this image?",
    show_progress=True
)

# Process results - each is a (result, error) tuple
output = []
for image_path, (result, error) in zip(image_files, results):
    if error is None:
        output.append({
            "image": Path(image_path).name,
            "prediction": str(result)
        })
        print(f"✓ Processed: {Path(image_path).name}")
    else:
        print(f"✗ Failed {Path(image_path).name}: {error}")
```

**Option 3: Recursive directory search**

```python
# Process all images in folder and subdirectories
results = model(
    source="./dataset/",
    user_prompt="What objects are in this image?",
    recursive=True,  # Search subdirectories recursively
    show_progress=True
)

print(f"Processed {len(results)} images across all subdirectories")
```

### 5. Custom Prompts

```python
# Different prompt types

# Visual question answering (VQA) - user prompt is required
result, error = model(
    source="image.jpg",
    user_prompt="How many people are in the image?"  # Required for VQA
)

# Visual question answering with detailed question
result, error = model(
    source="image.jpg",
    user_prompt="What is the main subject doing in this image?"  # Required for VQA
)

# Phrase grounding - user prompt is optional
result, error = model(
    source="image.jpg",
    user_prompt="Identify and locate all objects"  # Optional for Phrase Grounding
)

# Phrase grounding without custom prompt (uses default)
result, error = model(source="image.jpg")  # Uses default prompt
```

## Running the Example

### Prerequisites

```bash
# Install Vi SDK with inference support
pip install vi-sdk[inference]

# Prepare test images
mkdir test_images
# Add some images to test_images/
```

### Execute

```bash
python3 04_model_download_and_inference.py
```

## Expected Output

```
📡 Initializing Vi SDK client...

🔍 Finding trained models...
   Found 3 runs:

   1. Training Run 2025-01-15
      ID: run_xyz789
      Status: completed
      Created: 2025-01-15T10:30:00Z

⬇️  Downloading model from run_xyz789...
   ✓ Model downloaded successfully!
   Location: ./models/run_xyz789
   Model type: qwen25vl

🧠 Loading model for inference...
   ✓ Model loaded successfully!

🖼️  Running inference on test image...
   Input: test_image.jpg
   Prompt: "Describe this image"

   Prediction: "The image shows a busy city street with multiple
   cars and pedestrians. A red car is parked on the left side near
   a blue building. Several people are walking on the sidewalk..."

📊 Batch processing 5 images...
   ✓ Processed: image_001.jpg
   ✓ Processed: image_002.jpg
   ✓ Processed: image_003.jpg
   ✓ Processed: image_004.jpg
   ✓ Processed: image_005.jpg

✅ Model inference completed!

📊 Summary:
   - Images processed: 5
   - Model: qwen25vl
   - Results saved to: predictions.json
```

## Next Steps

- Learn about [annotation workflows](annotation-workflows.md)
- Explore [dataset loaders](dataset-loader-training.md) for preparing training data
- Check out [basic dataset operations](basic-dataset-operations.md)

## Key Concepts

### Model Types

Vi SDK currently supports the following models:

- **Qwen2.5-VL**: Vision-language model for multimodal tasks
- **InternVL 3.5**: Vision-language model for multimodal tasks
- **Cosmos Reason1**: Vision-language model for multimodal tasks
- **NVILA**: Vision-language model for multimodal tasks

!!! note "Future Model Support"
    More models will be supported in future releases.

### Model Types

The Vi SDK currently provides ViModel for Qwen2.5-VL, InternVL 3.5, Cosmos Reason1, and NVILA models:

```python
from vi.inference import ViModel

# For Qwen2.5-VL, InternVL 3.5, Cosmos Reason1, and NVILA models
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)
```

### Task Types

The Vi SDK supports two task types:

- **Visual Question Answering (VQA)**: Requires a user prompt in the form of a question
- **Phrase Grounding**: User prompt is optional (uses default prompt if not provided)

!!! note "Future Task Support"
    More task types will be supported in future releases.

## Tips

!!! tip "GPU Acceleration"
    Models will automatically use GPU if available:
    ```python
    import torch
    print(f"CUDA available: {torch.cuda.is_available()}")

    # Model will use GPU automatically
    model = ViModel(
        secret_key="your-secret-key",
        organization_id="your-organization-id",
        run_id="your-run-id"
    )
    ```

!!! tip "Batch Processing"
    Use native batch inference for better efficiency. You can process individual files, entire folders, or mix both:
    ```python
    # Process entire folder directly
    results = model(
        source="./images/",  # Folder path
        user_prompt=prompt,
        show_progress=True,
        recursive=False  # Set to True for subdirectories
    )

    # Or process specific files
    results = model(
        source=["img1.jpg", "img2.jpg"],
        user_prompt=prompt,
        show_progress=True
    )

    # Or mix files and folders
    results = model(
        source=["img1.jpg", "./folder1/", "./folder2/"],
        user_prompt=prompt,
        show_progress=True
    )

    # Process results
    for result, error in results:
        if error is None:
            print(f"Success: {result}")
    ```

!!! tip "Custom Prompts"
    Craft prompts based on your task type:
    ```python
    # For VQA (user prompt is required - should be a question)
    prompt = "What is the main subject of this image?"
    prompt = "How many objects are visible?"
    prompt = "What color is the car in the foreground?"

    # For Phrase Grounding (user prompt is optional)
    prompt = "Identify and locate all objects"  # Optional
    # Or omit the prompt to use the default
    ```

!!! warning "Model Size"
    Large models require significant storage and memory. Ensure you have:

    - Sufficient disk space for model files
    - Adequate RAM/VRAM for inference

## Common Use Cases

### Save Predictions to JSON

```python
import json

# Process entire folder directly - much simpler!
results = model(
    source="./images/",  # Just pass the folder path
    user_prompt="Describe this image",
    show_progress=True
)

predictions = []
for result, error in results:
    predictions.append({
        "prediction": str(result) if error is None else None,
        "error": str(error) if error else None
    })

# Save results
with open("predictions.json", "w") as f:
    json.dump(predictions, f, indent=2)
```

**Or for specific files:**

```python
import json
from pathlib import Path

# Use batch inference for specific files
image_files = [str(p) for p in Path("./images").glob("*.jpg")]

results = model(
    source=image_files,
    user_prompt="Describe this image",
)

predictions = []
for image_path, (result, error) in zip(image_files, results):
    predictions.append({
        "image": str(image_path),
        "prediction": str(result) if error is None else None,
        "error": str(error) if error else None
    })

# Save results
with open("predictions.json", "w") as f:
    json.dump(predictions, f, indent=2)
```

### Error Handling

```python
# Process folder directly - errors are returned as tuples
results = model(
    source="./images/",  # Folder path
    user_prompt="Describe this image",
    show_progress=True
)

for result, error in results:
    if error is None:
        print(f"✓ Success: {result}")
    else:
        print(f"✗ Error: {error}")
```

**Or for specific files:**

```python
from pathlib import Path

# Errors are returned as tuples - no need for try/except
image_files = [str(p) for p in Path("./images").glob("*.jpg")]

results = model(
    source=image_files,
    user_prompt="Describe this image",
)

for image_path, (result, error) in zip(image_files, results):
    image_name = Path(image_path).name
    if error is None:
        print(f"✓ {image_name}: {result}")
    else:
        print(f"✗ {image_name}: {error}")
```

### Compare Multiple Models

```python
# Load multiple models
model1 = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="run_id_1"
)

model2 = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="run_id_2"
)

# Compare predictions
prompt = "What is the main object in this image?"
result1, error1 = model1(source="test.jpg", user_prompt=prompt)
result2, error2 = model2(source="test.jpg", user_prompt=prompt)

if error1 is None:
    print(f"Model 1: {result1}")
else:
    print(f"Model 1 failed: {error1}")

if error2 is None:
    print(f"Model 2: {result2}")
else:
    print(f"Model 2 failed: {error2}")
```

### Inference with Custom Parameters

Use `generation_config` to control how the model generates responses:

```python
# Different inference configurations
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)

# Basic configuration
result, error = model(
    source="image.jpg",
    user_prompt="Describe this image",
    generation_config={
        "max_new_tokens": 512,  # Control output length
        "temperature": 0.7,     # Control randomness
    }
)

# Advanced configuration
result, error = model(
    source="image.jpg",
    user_prompt="Provide a detailed description",
    generation_config={
        "max_new_tokens": 1024,
        "temperature": 0.8,
        "top_p": 0.95,
        "do_sample": True,
        "repetition_penalty": 1.2,
    }
)
```
