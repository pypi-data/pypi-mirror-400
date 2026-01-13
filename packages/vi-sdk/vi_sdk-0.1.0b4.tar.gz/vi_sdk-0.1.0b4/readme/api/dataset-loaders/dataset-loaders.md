---
title: "Dataset Loaders API Reference"
excerpt: "Load and iterate through locally downloaded datasets"
category: "api-reference"
---

# Dataset Loaders API Reference

Complete API reference for local dataset loading. Load and iterate through locally downloaded datasets with ease.

---

## ViDataset Class

The main class for loading and accessing downloaded datasets.

### Constructor

```python
from vi.dataset.loaders import ViDataset

dataset = ViDataset("/path/to/dataset")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str \| Path` | Path to the downloaded dataset directory |

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `training` | `ViDatasetTraining` | Access training split |
| `validation` | `ViDatasetValidation` | Access validation split |
| `dump` | `ViDatasetDump` | Access dump split |

---

### Methods

#### info()

Get dataset information.

```python
info = dataset.info()
print(f"Name: {info.name}")
print(f"Total assets: {info.total_assets}")
print(f"Total annotations: {info.total_annotations}")
```

**Returns:** `ViDatasetInfo`

---

## Dataset Protocol

ViDataset implements the standard dataset protocol for ML framework integration.

### Length Protocol

```python
# Get total number of samples
print(f"Dataset size: {len(dataset)}")
```

### Indexing Protocol

```python
# Access by index
asset, annotations = dataset[0]   # First sample
asset, annotations = dataset[-1]  # Last sample
```

### Iteration Protocol

```python
# Iterate through all samples
for asset, annotations in dataset:
    print(f"Processing {asset.filename}")
```

---

## Dataset Split Classes

### ViDatasetSplit (Base)

Base class for dataset splits.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `assets` | `AssetCollection` | Collection of assets |
| `annotations` | `AnnotationCollection` | Collection of annotations |

**Methods:**

#### iter_pairs()

Iterate through asset-annotation pairs.

```python
for asset, annotations in dataset.training.iter_pairs():
    print(f"Asset: {asset.filename}")
    print(f"Annotations: {len(annotations)}")
```

**Returns:** `Iterator[tuple[Asset, list[Annotation]]]`

#### visualize()

Generate visualized images with annotations.

```python
for image in dataset.training.visualize():
    image.show()  # Display
    # Or save
    image.save("visualization.png")
```

**Returns:** `Iterator[PIL.Image]`

---

### ViDatasetTraining

Training split access.

```python
# Access training data
for asset, annotations in dataset.training.iter_pairs():
    train_on(asset, annotations)
```

---

### ViDatasetValidation

Validation split access.

```python
# Access validation data
for asset, annotations in dataset.validation.iter_pairs():
    validate_on(asset, annotations)
```

---

### ViDatasetDump

Dump split access (all data).

```python
# Access all data
for asset, annotations in dataset.dump.iter_pairs():
    process(asset, annotations)
```

---

## Type Classes

### Image (ViAsset)

Represents an image asset in the dataset.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `filename` | `str` | Image filename |
| `filepath` | `Path` | Full path to image file |
| `width` | `int` | Image width in pixels |
| `height` | `int` | Image height in pixels |
| `asset_id` | `str \| None` | Asset ID (if available) |

**Example:**

```python
for asset, _ in dataset.training.iter_pairs():
    print(f"File: {asset.filename}")
    print(f"Path: {asset.filepath}")
    print(f"Size: {asset.width}x{asset.height}")
```

---

### ViAnnotation

Represents an annotation.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `annotation_id` | `str \| None` | Annotation ID |
| `caption` | `str \| None` | Caption text |
| `grounded_phrases` | `list[GroundedPhrase] \| None` | Grounded phrases |
| `contents` | `PhraseGrounding \| Vqa` | Annotation contents |

**Example:**

```python
for _, annotations in dataset.training.iter_pairs():
    for ann in annotations:
        if ann.caption:
            print(f"Caption: {ann.caption}")
        if ann.grounded_phrases:
            for phrase in ann.grounded_phrases:
                print(f"  {phrase.phrase}: {phrase.bbox}")
```

---

### PhraseGrounding

Phrase grounding annotation contents.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `caption` | `str` | The caption text |
| `grounded_phrases` | `list[GroundedPhrase]` | List of grounded phrases |

---

### Vqa

VQA annotation contents.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `interactions` | `list[VqaInteraction]` | Question-answer pairs |

---

## Information Classes

### ViDatasetInfo

Dataset information.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Dataset name |
| `dataset_id` | `str` | Dataset ID |
| `total_assets` | `int` | Total number of assets |
| `total_annotations` | `int` | Total number of annotations |
| `splits` | `dict[str, ViDatasetSplitInfo]` | Split information |

---

### ViDatasetSplitInfo

Split information.

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `assets` | `int` | Number of assets in split |
| `annotations` | `int` | Number of annotations in split |

---

## Examples

### Load and Explore

```python
from vi.dataset.loaders import ViDataset

# Load dataset
dataset = ViDataset("./data/dataset_abc123")

# Get info
info = dataset.info()
print(f"Dataset: {info.name}")
print(f"Training: {info.splits['training'].assets} assets")
print(f"Validation: {info.splits['validation'].assets} assets")
```

### PyTorch Integration

```python
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms

class ViTorchDataset(Dataset):
    def __init__(self, vi_split, transform=None):
        self.pairs = list(vi_split.iter_pairs())
        self.transform = transform

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        asset, annotations = self.pairs[idx]
        image = Image.open(asset.filepath).convert('RGB')

        if self.transform:
            image = self.transform(image)

        caption = annotations[0].caption if annotations else ""
        return image, caption

# Create dataloader
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

torch_dataset = ViTorchDataset(dataset.training, transform=transform)
dataloader = DataLoader(torch_dataset, batch_size=32, shuffle=True)

for images, captions in dataloader:
    # Train your model
    pass
```

### Visualization

```python
# Visualize all training samples
for image in dataset.training.visualize():
    image.show()

# Save visualizations
for i, image in enumerate(dataset.training.visualize()):
    image.save(f"vis_{i}.png")
```

---

## See Also

- [Dataset Loaders Guide](vi-sdk-dataset-loaders) - Comprehensive guide
- [Datasets API](vi-sdk-datasets-api) - Downloading datasets
- [Assets API](vi-sdk-assets-api) - Asset operations
- [Inference API](vi-sdk-api-inference) - Inference API reference
