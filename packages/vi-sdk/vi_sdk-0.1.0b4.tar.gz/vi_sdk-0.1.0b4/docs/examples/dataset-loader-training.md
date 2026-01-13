# Dataset Loader and Training

This example demonstrates how to use the ViDataset loader to prepare data for model training.

## Overview

Learn how to:

- Load datasets with the ViDataset loader
- Access different splits (training, validation, dump)
- Iterate through asset-annotation pairs
- Visualize annotations
- Prepare data for training pipelines

## Source Code

[View full source on GitHub](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/examples/03_dataset_loader_training.py)

## Code Walkthrough

### 1. Load a Dataset

```python
from pathlib import Path
from vi.dataset import ViDataset

# Load dataset from directory (downloaded previously)
dataset_dir = Path("./data/dataset_xyz789")
dataset = ViDataset(dataset_dir)
```

### 2. Get Dataset Information

```python
# Retrieve dataset information
info = dataset.info()

print(f"Name: {info.name}")
print(f"Organization: {info.organization_id}")
print(f"Total Assets: {info.total_assets}")
print(f"Total Annotations: {info.total_annotations}")

# Display split information
for split_name, split_info in info.splits.items():
    print(f"{split_name}: {split_info.assets} assets, {split_info.annotations} annotations")
```

### 3. Iterate Through Training Data

```python
# Iterate through training split
for asset, annotations in dataset.training.iter_pairs():
    print(f"Asset: {asset.filename}")
    print(f"  Type: {asset.type}")
    print(f"  Dimensions: {asset.width}x{asset.height}")
    print(f"  Path: {asset.filepath}")

    print(f"  Annotations: {len(annotations)}")
    for ann in annotations:
        print(f"    - ID: {ann.id}, Category: {ann.category}")
```

### 4. Handle Different Annotation Types

```python
# Process phrase grounding annotations
for asset, annotations in dataset.training.iter_pairs():
    for ann in annotations:
        if hasattr(ann.contents, "caption"):
            # Phrase grounding
            caption = ann.contents.caption
            phrases = ann.contents.grounded_phrases

            print(f"Caption: {caption}")
            for phrase in phrases:
                print(f"  Phrase: '{phrase.phrase}'")
                print(f"  Tokens: [{phrase.start_token_index}, {phrase.end_token_index}]")
                print(f"  Bounding boxes: {len(phrase.bounds)}")

        elif hasattr(ann.contents, "interactions"):
            # VQA (Visual Question Answering)
            for qa in ann.contents.interactions:
                print(f"  Q: {qa.question}")
                print(f"  A: {qa.answer}")
```

### 5. Prepare Training Data

```python
import json

# Convert to training format
training_data = []

for asset, annotations in dataset.training.iter_pairs():
    for ann in annotations:
        if hasattr(ann.contents, "caption"):
            # Phrase grounding format
            training_example = {
                "image_path": asset.filepath,
                "image_size": (asset.width, asset.height),
                "caption": ann.contents.caption,
                "phrases": [
                    {
                        "text": p.phrase,
                        "bbox": p.bounds[0] if p.bounds else None,
                        "tokens": (p.start_token_index, p.end_token_index),
                    }
                    for p in ann.contents.grounded_phrases
                ],
            }
            training_data.append(training_example)

# Save training data
with open("training_data.json", "w") as f:
    json.dump(training_data, f, indent=2)
```

### 6. Visualize Annotations

```python
from pathlib import Path

# Generate and save visualizations
visualization_dir = Path("./visualizations")
visualization_dir.mkdir(exist_ok=True)

for i, image in enumerate(dataset.training.visualize()):
    output_path = visualization_dir / f"training_viz_{i+1}.png"
    image.save(output_path)

    if i >= 10:  # Save first 10
        break
```

### 7. Batch Processing

```python
# Process data in batches
batch_size = 8
batch = []

for asset, annotations in dataset.training.iter_pairs():
    batch.append((asset, annotations))

    if len(batch) == batch_size:
        # Process batch
        process_batch(batch)
        batch = []

# Process remaining items
if batch:
    process_batch(batch)
```

## Running the Example

### Prerequisites

```bash
# Install Vi SDK
pip install vi-sdk

# Download a dataset first
python3 01_basic_dataset_operations.py
```

### Execute

```bash
python3 03_dataset_loader_training.py
```

## Expected Output

```
📁 Loading dataset from: ./data/dataset_xyz789

📊 Loading dataset...

📋 Dataset Information:
   Name: Training Dataset
   Organization: org_abc123
   Export Directory: ./data/dataset_xyz789
   Created: 2025-01-15T10:30:00Z
   Total Assets: 150
   Total Annotations: 300

📊 Split Information:

   TRAINING:
      Assets: 120
      Annotations: 240

   VALIDATION:
      Assets: 30
      Annotations: 60

🎓 Exploring TRAINING split:
   Total pairs: 120

   First 3 training examples:

   Example 1:
      Asset: image_001.jpg
         Type: image
         Dimensions: 1920x1080
         Path: ./data/dataset_xyz789/training/assets/image_001.jpg
      Annotations: 2
         1. ID: ann_001
            Category: object
            Type: Phrase Grounding
            Caption: A red car parked next to a blue building
            Grounded Phrases: 2
               - 'red car'
                 Tokens: [1, 2]
                 Bounds: 1 boxes

🎨 Visualizing annotations...
   ✓ Saved 10 visualizations to ./visualizations

✅ Dataset loader demonstration completed!
```

## Next Steps

- Explore [model inference](model-download-inference.md) for using trained models
- Learn about [annotation workflows](annotation-workflows.md)
- Check out [asset operations](asset-upload-download.md)

## Key Concepts

### Dataset Splits

Datasets are organized into splits:

- **training**: Data for model training
- **validation**: Data for validation during training
- **dump**: Unassigned data - if no splits were specified during dataset export

Access splits using:

```python
dataset.training
dataset.validation
dataset.dump
```

### Efficient Iteration

The loader provides efficient streaming:

```python
# Efficient - streams data
for asset, annotations in dataset.training.iter_pairs():
    process(asset, annotations)

# Less efficient - loads all at once
all_pairs = list(dataset.training.iter_pairs())
```

### Annotation Types

Vi SDK supports multiple annotation types:

#### Phrase Grounding

```python
if hasattr(ann.contents, "caption"):
    caption = ann.contents.caption
    for phrase in ann.contents.grounded_phrases:
        text = phrase.phrase
        bbox = phrase.bounds[0]
        tokens = (phrase.start_token_index, phrase.end_token_index)
```

#### Visual Question Answering (VQA)

```python
if hasattr(ann.contents, "interactions"):
    for qa in ann.contents.interactions:
        question = qa.question
        answer = qa.answer
```

## Tips

!!! tip "Memory Efficiency"
    Use `iter_pairs()` for streaming iteration to minimize memory usage:
    ```python
    for asset, annotations in dataset.training.iter_pairs():
        # Process one pair at a time
        pass
    ```

!!! tip "Direct Access"
    Access assets and annotations separately if needed:
    ```python
    # Just assets
    for asset in dataset.training.assets.items:
        process_asset(asset)

    # Just annotations
    for annotations in dataset.training.annotations.items:
        process_annotations(annotations)
    ```

!!! tip "Visualization"
    Visualizations are generated on-demand to save memory:
    ```python
    for i, image in enumerate(dataset.training.visualize()):
        if i >= 10:  # Only visualize first 10
            break
        image.show()  # or image.save(path)
    ```

## Common Use Cases

### PyTorch Dataset Integration

```python
from torch.utils.data import Dataset
from PIL import Image

class ViPyTorchDataset(Dataset):
    def __init__(self, vi_split, transform=None):
        self.vi_split = vi_split
        self.transform = transform
        self.pairs = list(vi_split.iter_pairs())

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        asset, annotations = self.pairs[idx]

        # Load image
        image = Image.open(asset.filepath)

        # Process annotations
        labels = self.process_annotations(annotations)

        if self.transform:
            image = self.transform(image)

        return image, labels

    def process_annotations(self, annotations):
        # Convert annotations to your format
        return labels

# Use with DataLoader
dataset = ViPyTorchDataset(dataset.training)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Data Augmentation

```python
from PIL import Image
import torchvision.transforms as T

transform = T.Compose([
    T.Resize((224, 224)),
    T.RandomHorizontalFlip(),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

for asset, annotations in dataset.training.iter_pairs():
    image = Image.open(asset.filepath)
    image_tensor = transform(image)
    # Train with augmented image
```

### Export to JSON

```python
import json

def export_to_json(dataset_split, output_path):
    data = []

    for asset, annotations in dataset_split.iter_pairs():
        item = {
            "image": asset.filename,
            "width": asset.width,
            "height": asset.height,
            "annotations": [
                {
                    "id": ann.id,
                    "category": ann.category,
                    "contents": str(ann.contents)
                }
                for ann in annotations
            ]
        }
        data.append(item)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

# Export training data
export_to_json(dataset.training, "training.json")
```
