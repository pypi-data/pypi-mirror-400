---
title: "Dataset Loaders"
excerpt: "Load and iterate through downloaded datasets for training"
category: "guide"
---

# Dataset Loaders

Learn how to load and iterate through downloaded datasets for training and evaluation.

---

## Overview

Dataset loaders provide efficient access to your downloaded datasets for:

- Training machine learning models
- Data exploration and analysis
- Visualization
- Data preprocessing
- Custom data pipelines

---

## Quick Start

```python
from vi.dataset.loaders import ViDataset

# Load downloaded dataset
dataset = ViDataset("./data/dataset_abc123")

# Iterate training data
for asset, annotations in dataset.training.iter_pairs():
    print(f"Asset: {asset.filename}")
    print(f"Annotations: {len(annotations)}")
```

---

## Loading Datasets

### Load from Directory

```python
from vi.dataset.loaders import ViDataset

# Load dataset
dataset = ViDataset("/path/to/dataset")

# Get dataset information
info = dataset.info()
print(f"Name: {info.name}")
print(f"Total assets: {info.total_assets}")
print(f"Total annotations: {info.total_annotations}")
```

### Download and Load

```python
import vi
from vi.dataset.loaders import ViDataset

# Initialize client
client = vi.Client()

# Download dataset
downloaded = client.get_dataset(
    dataset_id="dataset_abc123",
    save_dir="./data"
)

# Load with ViDataset
dataset = ViDataset(downloaded.save_dir)
```

---

## Accessing Splits

Datasets are divided into splits:

- **training**: Training data
- **validation**: Validation data
- **dump**: Other data

### Get Split Information

```python
# Training split
print(f"Training assets: {len(dataset.training.assets)}")
print(f"Training annotations: {len(dataset.training.annotations)}")

# Validation split
print(f"Validation assets: {len(dataset.validation.assets)}")
print(f"Validation annotations: {len(dataset.validation.annotations)}")
```

---

## Dataset Protocol

ViDataset implements the standard dataset protocol, enabling seamless integration with ML frameworks and training pipelines.

### Basic Dataset Protocol

```python
from vi.dataset import ViDataset

# Load dataset
dataset = ViDataset("dataset_abc123")

# Training loop
for asset, annotations in dataset:
    print(f"Processing {asset.filename}")
```

### Dataset Protocol Methods

```python
# Length protocol
print(f"Dataset size: {len(dataset)}")

# Indexing protocol
asset, annotations = dataset[0]  # First sample
asset, annotations = dataset[-1]  # Last sample

# Iteration protocol
for asset, annotations in dataset:
    print(f"Processing {asset.filename}")
```

---

## Iterating Assets

### Iterate Assets Only

```python
# Iterate through assets
for asset in dataset.training.assets.items:
    print(f"Filename: {asset.filename}")
    print(f"Path: {asset.filepath}")
    print(f"Size: {asset.width}x{asset.height}")
```

### Access Asset Data

```python
# Load image data
from PIL import Image

for asset in dataset.training.assets.items:
    # Open image
    image = Image.open(asset.filepath)

    # Process image
    print(f"Image mode: {image.mode}")
    print(f"Image size: {image.size}")
```

---

## Iterating Annotations

### Iterate Annotations Only

```python
# Iterate through annotations (returns list of annotations per asset)
for annotations in dataset.training.annotations.items:
    for annotation in annotations:
        # Access caption
        if annotation.caption:
            print(f"Caption: {annotation.caption}")

        # Access grounded phrases
        if annotation.grounded_phrases:
            for phrase in annotation.grounded_phrases:
                print(f"  - {phrase.phrase}: {phrase.bbox}")
```

---

## Iterating Asset-Annotation Pairs

### Basic Iteration

```python
# Iterate pairs together
for asset, annotations in dataset.training.iter_pairs():
    print(f"\nAsset: {asset.filename}")
    print(f"Number of annotations: {len(annotations)}")

    # Process each annotation
    for annotation in annotations:
        if annotation.caption:
            print(f"  Caption: {annotation.caption}")
```

### Training Loop Example

```python
from PIL import Image
import torch
from torch.utils.data import Dataset

class ViTorchDataset(Dataset):
    """Wrap ViDataset for PyTorch."""

    def __init__(self, vi_dataset_split, transform=None):
        self.split = vi_dataset_split
        self.pairs = list(vi_dataset_split.iter_pairs())
        self.transform = transform

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        asset, annotations = self.pairs[idx]

        # Load image
        image = Image.open(asset.filepath).convert('RGB')

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        # Get caption (first annotation)
        caption = annotations[0].caption if annotations else ""

        return image, caption

# Usage with PyTorch
from torch.utils.data import DataLoader
from torchvision import transforms

# Create transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

# Create dataset and dataloader
torch_dataset = ViTorchDataset(dataset.training, transform=transform)
dataloader = DataLoader(torch_dataset, batch_size=32, shuffle=True)

# Training loop
for batch_images, batch_captions in dataloader:
    # Your training code here
    pass
```

---

## Working with Annotations

### Caption Annotations

```python
for asset, annotations in dataset.training.iter_pairs():
    for annotation in annotations:
        if annotation.caption:
            print(f"Caption: {annotation.caption}")
```

### Grounded Phrase Annotations

```python
for asset, annotations in dataset.training.iter_pairs():
    for annotation in annotations:
        if annotation.grounded_phrases:
            print(f"\nAsset: {asset.filename}")
            for phrase in annotation.grounded_phrases:
                print(f"  Phrase: {phrase.phrase}")
                print(f"  BBox: {phrase.bbox}")

                # Convert normalized bbox to pixel coordinates
                x_min, y_min, x_max, y_max = phrase.bbox
                pixel_bbox = [
                    int(x_min * asset.width),
                    int(y_min * asset.height),
                    int(x_max * asset.width),
                    int(y_max * asset.height)
                ]
                print(f"  Pixel BBox: {pixel_bbox}")
```

---

## Visualization

### Visualize Single Asset

```python
# Visualize all samples in the split
for image in dataset.training.visualize():
    image.show()  # Display the annotated image

# Or save to disk
for i, image in enumerate(dataset.training.visualize()):
    image.save(f"visualization_{i}.png")
```

### Visualize with Bounding Boxes

```python
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

def visualize_grounded_phrases(asset, annotations):
    """Visualize image with grounded phrases."""
    # Load image
    image = Image.open(asset.filepath)
    draw = ImageDraw.Draw(image)

    # Draw bounding boxes
    for annotation in annotations:
        if not annotation.grounded_phrases:
            continue

        for phrase in annotation.grounded_phrases:
            # Convert normalized to pixel coordinates
            x_min = phrase.bbox[0] * asset.width
            y_min = phrase.bbox[1] * asset.height
            x_max = phrase.bbox[2] * asset.width
            y_max = phrase.bbox[3] * asset.height

            # Draw rectangle
            draw.rectangle(
                [(x_min, y_min), (x_max, y_max)],
                outline='red',
                width=3
            )

            # Draw text
            draw.text(
                (x_min, y_min - 10),
                phrase.phrase,
                fill='red'
            )

    # Display
    plt.figure(figsize=(12, 8))
    plt.imshow(image)
    plt.axis('off')
    plt.title(f"{asset.filename}")
    plt.show()

# Usage
for asset, annotations in dataset.training.iter_pairs():
    visualize_grounded_phrases(asset, annotations)
    break  # Just show first one
```

### Create Dataset Overview

```python
import matplotlib.pyplot as plt
from PIL import Image

def show_dataset_samples(dataset_split, n_samples=9):
    """Show grid of sample images."""
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.flatten()

    pairs = list(dataset_split.iter_pairs())[:n_samples]

    for idx, (asset, annotations) in enumerate(pairs):
        if idx >= len(axes):
            break

        # Load and display image
        image = Image.open(asset.filepath)
        axes[idx].imshow(image)
        axes[idx].axis('off')

        # Add caption if available
        if annotations and annotations[0].caption:
            caption = annotations[0].caption[:50] + "..."
            axes[idx].set_title(caption, fontsize=8)

    plt.tight_layout()
    plt.show()

# Show training samples
show_dataset_samples(dataset.training)
```

---

## Data Statistics

### Count Annotations by Type

```python
def count_annotation_types(dataset_split):
    """Count different annotation types."""
    counts = {
        'captions': 0,
        'grounded_phrases': 0,
        'bboxes': 0
    }

    for _, annotations in dataset_split.iter_pairs():
        for annotation in annotations:
            if annotation.caption:
                counts['captions'] += 1
            if annotation.grounded_phrases:
                counts['grounded_phrases'] += len(annotation.grounded_phrases)

    return counts

# Get counts
train_counts = count_annotation_types(dataset.training)
print(f"Training set:")
for key, value in train_counts.items():
    print(f"  {key}: {value}")
```

### Analyze Image Sizes

```python
from collections import Counter

def analyze_image_sizes(dataset_split):
    """Analyze distribution of image sizes."""
    sizes = []

    for asset in dataset_split.assets:
        sizes.append((asset.width, asset.height))

    # Count unique sizes
    size_counts = Counter(sizes)

    print("Most common image sizes:")
    for size, count in size_counts.most_common(5):
        print(f"  {size[0]}x{size[1]}: {count} images")

    return size_counts

# Analyze
analyze_image_sizes(dataset.training)
```

---

## Best Practices

### 1. Lazy Loading

```python
# ✅ Good - iterate without loading all into memory
for asset, annotations in dataset.training.iter_pairs():
    process(asset, annotations)

# ❌ Bad - load everything at once
all_pairs = list(dataset.training.iter_pairs())  # Memory intensive
```

### 2. Efficient Image Loading

```python
from PIL import Image

# ✅ Good - load and process immediately
for asset in dataset.training.assets.items:
    image = Image.open(asset.filepath)
    processed = preprocess(image)
    train(processed)
    # Image released from memory here

# ❌ Bad - load all images
images = []
for asset in dataset.training.assets.items:
    images.append(Image.open(asset.filepath))  # Memory intensive
```

### 3. Cache Processed Data

```python
import pickle
from pathlib import Path

def cache_processed_data(dataset_split, cache_file='cache.pkl'):
    """Cache preprocessed data."""
    cache_path = Path(cache_file)

    if cache_path.exists():
        # Load from cache
        with open(cache_path, 'rb') as f:
            return pickle.load(f)

    # Process and cache
    processed_data = []
    for asset, annotations in dataset_split.iter_pairs():
        # Your preprocessing here
        processed = preprocess(asset, annotations)
        processed_data.append(processed)

    # Save cache
    with open(cache_path, 'wb') as f:
        pickle.dump(processed_data, f)

    return processed_data
```

---

## Common Workflows

### Export to COCO Format

```python
import json

def export_to_coco(dataset_split, output_file):
    """Export dataset to COCO format."""
    coco = {
        "images": [],
        "annotations": [],
        "categories": []
    }

    annotation_id = 1

    for asset in dataset_split.assets.items:
        # Add image
        coco["images"].append({
            "id": asset.asset_id if hasattr(asset, 'asset_id') else asset.filename,
            "file_name": asset.filename,
            "width": asset.width,
            "height": asset.height
        })

    # Add annotations
    for asset, annotations in dataset_split.iter_pairs():
        for annotation in annotations:
            if annotation.grounded_phrases:
                for phrase in annotation.grounded_phrases:
                    # Convert to COCO format
                    x_min, y_min, x_max, y_max = phrase.bbox
                    bbox = [
                        x_min * asset.width,
                        y_min * asset.height,
                        (x_max - x_min) * asset.width,
                        (y_max - y_min) * asset.height
                    ]

                    coco["annotations"].append({
                        "id": annotation_id,
                        "image_id": asset.asset_id,
                        "category_name": phrase.phrase,
                        "bbox": bbox
                    })
                    annotation_id += 1

    # Save
    with open(output_file, 'w') as f:
        json.dump(coco, f, indent=2)

# Usage
export_to_coco(dataset.training, "train_coco.json")
```

### Create Data Augmentation Pipeline

```python
from torchvision import transforms
from PIL import Image

# Define augmentations
augmentation_pipeline = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# Apply to dataset
for asset, annotations in dataset.training.iter_pairs():
    image = Image.open(asset.filepath)
    augmented = augmentation_pipeline(image)

    # Use augmented image for training
    train_model(augmented, annotations)
```

---

## Troubleshooting

### Dataset Not Found

```python
from pathlib import Path

dataset_path = Path("./data/dataset_abc123")
if not dataset_path.exists():
    print("Dataset not found. Downloading...")
    client.get_dataset("dataset_abc123", save_dir="./data")
```

### Missing Annotations

```python
# Check for assets without annotations
no_annotations = []

for asset, annotations in dataset.training.iter_pairs():
    if not annotations:
        no_annotations.append(asset.filename)

if no_annotations:
    print(f"Found {len(no_annotations)} assets without annotations:")
    for filename in no_annotations[:5]:
        print(f"  - {filename}")
```

---

## See Also

- [Datasets Guide](vi-sdk-datasets) - Downloading datasets
- [API Reference](vi-sdk-api-dataset-loaders) - Dataset Loaders API documentation
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Complete examples
