# Vi SDK Examples

This directory contains practical examples demonstrating how to use the Vi SDK effectively.

## Getting Started

### Prerequisites

1. Install Vi SDK with all features:
   ```bash
   pip install vi-sdk[all]
   ```

2. Set up your credentials:
   ```bash
   export DATATURE_VI_SECRET_KEY="your-secret-key"
   export DATATURE_VI_ORGANIZATION_ID="your-organization-id"
   ```

3. (Optional) Create a config file at `~/datature/vi/config.json`:
   ```json
   {
     "secret_key": "your-secret-key",
     "organization_id": "your-organization-id"
   }
   ```

## Examples

### Basic Operations

#### 1. Basic Dataset Operations
**File:** [`01_basic_dataset_operations.py`](01_basic_dataset_operations.py)

Learn the fundamentals:
- Initializing the client
- Listing datasets
- Getting dataset details
- Creating and downloading dataset exports

```bash
python3 01_basic_dataset_operations.py
```

**Topics covered:**
- Client initialization
- Organization info
- Dataset listing and pagination
- Export creation
- Dataset download

---

#### 2. Asset Upload and Download
**File:** [`02_asset_upload_download.py`](02_asset_upload_download.py)

Master asset operations:
- Uploading single images
- Batch uploading folders
- Listing and filtering assets
- Downloading assets

```bash
python3 02_asset_upload_download.py
```

**Topics covered:**
- Single file upload
- Folder upload
- Progress tracking
- Asset listing with pagination
- Asset filtering
- Bulk download

---

#### 3. Dataset Loader and Training Preparation
**File:** [`03_dataset_loader_training.py`](03_dataset_loader_training.py)

Prepare data for training:
- Loading datasets with ViDataset
- Accessing splits (training/validation)
- Iterating through data pairs
- Data visualization
- Training data preparation

```bash
python3 03_dataset_loader_training.py
```

**Topics covered:**
- Dataset loading
- Split information
- Efficient iteration
- Annotation types (phrase grounding, VQA)
- Data formatting for training
- Visualization

---

#### 4. Model Download and Inference
**File:** [`04_model_download_and_inference.py`](04_model_download_and_inference.py)

Train and use models:
- Downloading trained models
- Loading models for inference
- Running predictions
- Batch inference
- Structured output generation

```bash
python3 04_model_download_and_inference.py
```

**Topics covered:**
- Model download
- ViModel initialization
- Single and batch inference
- Folder-based batch inference
- Recursive directory processing
- Mixed file and folder sources
- Error handling in inference
- Generation configuration

---

#### 5. Annotation Workflows
**File:** [`05_annotation_workflows.py`](05_annotation_workflows.py)

Work with annotations:
- Creating annotations
- Phrase grounding annotations
- VQA (Visual Question Answering) annotations
- Batch annotation operations
- Annotation import/export

```bash
python3 05_annotation_workflows.py
```

**Topics covered:**
- Creating phrase grounding annotations
- Creating VQA annotations
- Bulk annotation operations
- Exporting annotations
- Importing annotations

---

#### 6. Inference Visualization
**File:** [`06_inference_visualization.py`](06_inference_visualization.py)

Visualize model predictions:
- Visualizing phrase grounding predictions
- Visualizing VQA predictions
- Visualizing generic responses
- Saving visualizations to disk

```bash
python3 06_inference_visualization.py
```

**Topics covered:**
- Loading models for visualization
- Rendering bounding boxes on images
- Displaying Q&A panels
- Saving visualizations as images
- Working with different task types

---

#### 7. NIM Deployment Visualization
**File:** [`07_deployment_visualization.py`](07_deployment_visualization.py)

Visualize NIM deployment predictions:
- NIM predictor visualization
- Batch visualization of multiple images
- Custom port configuration
- Working with deployed models

```bash
python3 07_deployment_visualization.py
```

**Topics covered:**
- NIM predictor setup
- Visualizing NIM predictions
- Batch image processing
- Custom deployment configurations

---

## Example Workflows

### Complete Dataset Pipeline

```bash
# 1. List and download datasets
python3 01_basic_dataset_operations.py

# 2. Upload new assets to dataset
python3 02_asset_upload_download.py

# 3. Load and prepare for training
python3 03_dataset_loader_training.py

# 4. Run inference with trained models
python3 04_model_download_and_inference.py

# 5. Work with annotations
python3 05_annotation_workflows.py
```

### Data Preparation for Training

```python
from vi.dataset.loaders import ViDataset

# Load dataset
dataset = ViDataset("./data/your-dataset-id")

# Prepare training data
for asset, annotations in dataset.training.iter_pairs():
    # Your training code here
    image = load_image(asset.filepath)

    for annotation in annotations:
        if hasattr(annotation.contents, 'caption'):
            # Phrase grounding
            caption = annotation.contents.caption
            phrases = annotation.contents.grounded_phrases
            # Train on phrase grounding

        elif hasattr(annotation.contents, 'interactions'):
            # VQA
            qa_pairs = annotation.contents.interactions
            # Train on VQA
```

### Batch Asset Upload

```python
import vi

client = vi.Client()

# Upload entire folder
result = client.assets.upload(
    dataset_id="your-dataset-id",
    paths="./images/",
    wait_until_done=True
)

print(f"Uploaded: {result.total_succeeded} assets")
print(result.summary())
```

### Model Inference

```python
from vi.inference import ViModel

# Load model with credentials and run ID
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id"
)

# Run inference on single image
result, error = model(
    source="test.jpg",
    user_prompt="Describe this image"
)

# Process entire folder
results = model(
    source="./test_images/",  # Folder path
    user_prompt="Describe this image",
    recursive=True,  # Include subdirectories
    show_progress=True
)

# Process specific files
results = model(
    source=["img1.jpg", "img2.jpg", "img3.jpg"],
    user_prompt="Describe this image"
)

# Mix files and folders
results = model(
    source=["single.jpg", "./folder1/", "./folder2/"],
    user_prompt="Describe this image"
)

# Force re-download model (useful for fixing corrupted models)
model = ViModel(
    secret_key="your-secret-key",
    organization_id="your-organization-id",
    run_id="your-run-id",
    overwrite=True  # Re-download even if model exists
)
```

## Common Patterns

### Error Handling

```python
from vi import ViError, ViNotFoundError, ViAuthenticationError

try:
    dataset = client.datasets.get("dataset-id")
except ViNotFoundError:
    print("Dataset not found")
except ViAuthenticationError:
    print("Authentication failed")
except ViError as e:
    print(f"Error: {e.error_code} - {e.message}")
    if e.suggestion:
        print(f"Suggestion: {e.suggestion}")
```

### Pagination

```python
from vi.api.types import PaginationParams

# Iterate all pages automatically
for page in client.datasets.list():
    for dataset in page.items:
        process(dataset)

# Or iterate all items
datasets = client.datasets.list()
for dataset in datasets.all_items():
    process(dataset)

# Custom page size
pagination = PaginationParams(page_size=50)
datasets = client.datasets.list(pagination=pagination)
```

### Progress Tracking

```python
# With progress bar (default)
dataset = client.get_dataset(
    dataset_id="dataset-id",
    show_progress=True
)

# Without progress bar (for scripts/CI)
dataset = client.get_dataset(
    dataset_id="dataset-id",
    show_progress=False
)
```

## Tips and Best Practices

### 1. Use Virtual Environments

```bash
python3 -m venv vi-env
source vi-env/bin/activate  # Linux/macOS
# or
vi-env\Scripts\activate  # Windows

pip install vi-sdk[all]
```

### 2. Secure Your Credentials

Never hardcode credentials:

```python
# ❌ Bad
client = vi.Client(secret_key="sk_live_123...")

# ✅ Good
import os
client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID")
)
```

### 3. Enable Logging for Debugging

```python
from vi.logging import LoggingConfig, LogLevel

config = LoggingConfig(
    level=LogLevel.DEBUG,
    enable_console=True,
    enable_file=True
)

client = vi.Client(
    secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
    organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID"),
    logging_config=config
)
```

### 4. Handle Errors Gracefully

```python
from vi import ViError

try:
    # Your operations
    pass
except ViError as e:
    logger.error(f"Operation failed: {e.message}")
    # Handle error appropriately
```

### 5. Use Efficient Iteration

```python
# ✅ Efficient - streaming, low memory
for asset, annotations in dataset.training.iter_pairs():
    process(asset, annotations)

# ❌ Less efficient - loads all at once
all_data = list(dataset.training.iter_pairs())
for asset, annotations in all_data:
    process(asset, annotations)
```

## Troubleshooting

### "No datasets found"

Make sure you have datasets in your organization on Datature Vi.

### Authentication errors

1. Verify your credentials are correct
2. Check environment variables are set
3. Ensure your API key hasn't been revoked

### Import errors

```bash
# Install all dependencies
pip install vi-sdk[all]

# Or install specific features
pip install vi-sdk[inference]  # For inference
```

### Network errors

1. Check your internet connection
2. Verify the API endpoint is accessible
3. Check firewall settings

## Getting Help

- **Documentation**: https://vi.readthedocs.io
- **GitHub Issues**: https://github.com/datature/Vi-SDK/issues
- **Email Support**: support@datature.io

## Contributing

We welcome contributions! If you have an example that would help others:

1. Fork the repository
2. Add your example with clear documentation
3. Test it thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

These examples are provided under the Apache License 2.0, same as the Vi SDK.
