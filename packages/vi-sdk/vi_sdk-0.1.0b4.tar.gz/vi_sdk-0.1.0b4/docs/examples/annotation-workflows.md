# Annotation Workflows

This example demonstrates how to work with annotations in the Vi SDK.

## Overview

Learn how to:

- Create annotations
- Work with phrase grounding annotations
- Handle VQA (Visual Question Answering) annotations
- Perform batch annotation operations
- Import and export annotations

## Source Code

[View full source on GitHub](https://github.com/datature/Vi-SDK/blob/main/pypi/vi-sdk/examples/05_annotation_workflows.py)

## Code Walkthrough

### 1. List Annotations

```python
import os
import vi

client = vi.Client(
    secret_key="YOUR_DATATURE_VI_SECRET_KEY",
    organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID"
)

# List annotations for a specific asset
annotations = client.annotations.list(
    dataset_id=dataset_id,
    asset_id=asset_id
)

for ann in annotations.items:
    print(f"Annotation ID: {ann.annotation_id}")
    print(f"Category: {ann.category}")
    print(f"Created: {ann.time_created}")
```

### 2. Get Annotation Details

```python
# Get full annotation details
annotation = client.annotations.get(
    dataset_id=dataset_id,
    asset_id=asset_id,
    annotation_id=annotation_id
)

print(f"ID: {annotation.annotation_id}")
print(f"Asset: {annotation.asset_id}")
print(f"Category: {annotation.category}")

# Check annotation type
if hasattr(annotation.contents, "caption"):
    print("Type: Phrase Grounding")
    print(f"Caption: {annotation.contents.caption}")
elif hasattr(annotation.contents, "interactions"):
    print("Type: VQA")
    print(f"Q&A pairs: {len(annotation.contents.interactions)}")
```

### 3. Create Phrase Grounding Annotation

```python
from vi.api.resources.annotations.types import (
    AnnotationCreatePhraseGroundingSpecPhraseGroundingContents,
    PhraseGroundingContentsGroundedPhrase,
    PhraseGroundingContentsGroundedPhraseBound
)

# Define grounded phrases
phrases = [
    PhraseGroundingContentsGroundedPhrase(
        phrase="red car",
        start_token_index=1,
        end_token_index=2,
        bounds=[
            PhraseGroundingContentsGroundedPhraseBound(
                x=100,
                y=150,
                width=200,
                height=150
            )
        ]
    )
]

# Create annotation
contents = AnnotationCreatePhraseGroundingSpecPhraseGroundingContents(
    caption="A red car parked near a building",
    grounded_phrases=phrases
)

new_annotation = client.annotations.create(
    dataset_id=dataset_id,
    asset_id=asset_id,
    category="vehicle",
    contents=contents
)

print(f"Created annotation: {new_annotation.annotation_id}")
```

### 4. Create VQA Annotation

```python
from vi.api.resources.annotations.types import (
    AnnotationCreateVqaSpecVqaContents,
    VqaContentsInteraction
)

# Define Q&A pairs
interactions = [
    VqaContentsInteraction(
        question="What color is the car?",
        answer="The car is red"
    ),
    VqaContentsInteraction(
        question="Where is the car located?",
        answer="The car is parked near a building"
    )
]

# Create VQA annotation
contents = AnnotationCreateVqaSpecVqaContents(
    interactions=interactions
)

new_annotation = client.annotations.create(
    dataset_id=dataset_id,
    asset_id=asset_id,
    category="qa",
    contents=contents
)

print(f"Created VQA annotation: {new_annotation.annotation_id}")
```

### 5. Update Annotation

```python
# Update an existing annotation
updated = client.annotations.update(
    dataset_id=dataset_id,
    asset_id=asset_id,
    annotation_id=annotation_id,
    category="updated_category"
)

print(f"Updated: {updated.annotation_id}")
```

### 6. Delete Annotation

```python
# Delete an annotation
deleted = client.annotations.delete(
    dataset_id=dataset_id,
    asset_id=asset_id,
    annotation_id=annotation_id
)

print(f"Deleted: {deleted.deleted}")
```

### 7. Batch Process Annotations

```python
# Process all annotations in a dataset
for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        # Get annotations for this asset
        annotations = client.annotations.list(
            dataset_id=dataset_id,
            asset_id=asset.asset_id
        )

        for ann in annotations.items:
            # Process each annotation
            process_annotation(ann)
```

## Running the Example

### Prerequisites

```bash
# Install Vi SDK
pip install vi-sdk

### Execute

```bash
python3 05_annotation_workflows.py
```

## Expected Output

```
📡 Initializing Vi SDK client...

📊 Finding dataset and assets...
   ✓ Using dataset: My Dataset (dataset_xyz789)
   ✓ Found asset: image_001.jpg (asset_abc123)

📋 Listing existing annotations...
   Found 2 annotations:
   1. Annotation ID: ann_001
      Category: vehicle
      Type: Phrase Grounding
      Created: 2025-01-15T10:30:00Z

   2. Annotation ID: ann_002
      Category: qa
      Type: VQA
      Created: 2025-01-15T11:00:00Z

🎨 Creating phrase grounding annotation...
   ✓ Created annotation: ann_003
   Caption: "A red car parked near a building"
   Grounded phrases: 1

💬 Creating VQA annotation...
   ✓ Created annotation: ann_004
   Q&A pairs: 2

🔄 Updating annotation...
   ✓ Updated annotation: ann_003

🔍 Batch processing annotations across dataset...
   Processing: image_001.jpg (2 annotations)
   Processing: image_002.jpg (1 annotation)
   Processing: image_003.jpg (3 annotations)
   Total processed: 150 annotations

✅ Annotation workflows completed!
```

## Next Steps

- Learn about [dataset loaders](dataset-loader-training.md) to use annotations for training
- Explore [model inference](model-download-inference.md) to generate predictions
- Check out [asset operations](asset-upload-download.md)

## Key Concepts

### Annotation Types

Vi SDK supports multiple annotation types:

#### Phrase Grounding

Links phrases in a caption to regions in an image:

```python
{
  "caption": "A red car parked near a building",
  "grounded_phrases": [
    {
      "phrase": "red car",
      "start_token_index": 1,
      "end_token_index": 2,
      "bounds": [{"x": 100, "y": 150, "width": 200, "height": 150}]
    }
  ]
}
```

#### Visual Question Answering (VQA)

Question-answer pairs about an image:

```python
{
  "interactions": [
    {
      "question": "What color is the car?",
      "answer": "The car is red"
    }
  ]
}
```

### Annotation Structure

Each annotation has:

- **ID**: Unique identifier
- **Asset ID**: Associated asset
- **Category**: Annotation category/label
- **Contents**: Type-specific annotation data
- **Metadata**: Creation time, owner, etc.

### Bounding Boxes

Bounding boxes specify regions in images:

```python
bound = PhraseGroundingContentsGroundedPhraseBound(
    x=100,          # Left edge
    y=150,          # Top edge
    width=200,      # Width
    height=150      # Height
)
```

Coordinates are in pixels from the top-left corner.

## Tips

!!! tip "Batch Creation"
    Create multiple annotations efficiently:
    ```python
    for asset in assets:
        for phrase_data in phrase_list:
            client.annotations.create(
                dataset_id=dataset_id,
                asset_id=asset.asset_id,
                category=phrase_data["category"],
                contents=phrase_data["contents"]
            )
    ```

!!! tip "Validation"
    Validate annotation data before creation:
    ```python
    # Check bounds are within image dimensions
    if (bound.x + bound.width <= asset.width and
        bound.y + bound.height <= asset.height):
        # Valid bounds
        create_annotation()
    ```

!!! tip "Pagination"
    Use pagination for large annotation sets:
    ```python
    from vi.api.types import PaginationParams

    pagination = PaginationParams(page_size=100)
    annotations = client.annotations.list(
        dataset_id=dataset_id,
        asset_id=asset_id,
        pagination=pagination
    )
    ```

!!! warning "Asset Association"
    Annotations must be associated with valid assets in the same dataset.

## Common Use Cases

### Import Annotations from JSON

```python
import json

def import_annotations(json_file, dataset_id, client):
    with open(json_file, 'r') as f:
        data = json.load(f)

    for item in data:
        asset_id = item["asset_id"]

        for ann_data in item["annotations"]:
            # Convert JSON to annotation objects
            contents = create_contents_from_dict(ann_data["contents"])

            client.annotations.create(
                dataset_id=dataset_id,
                asset_id=asset_id,
                category=ann_data["category"],
                contents=contents
            )

import_annotations("annotations.json", dataset_id, client)
```

### Export Annotations to JSON

```python
import json

def export_annotations(dataset_id, output_file, client):
    data = []

    for page in client.assets.list(dataset_id=dataset_id):
        for asset in page.items:
            annotations = client.annotations.list(
                dataset_id=dataset_id,
                asset_id=asset.asset_id
            )

            asset_data = {
                "asset_id": asset.asset_id,
                "filename": asset.filename,
                "annotations": [
                    {
                        "id": ann.annotation_id,
                        "category": ann.category,
                        "contents": serialize_contents(ann.contents)
                    }
                    for ann in annotations.items
                ]
            }
            data.append(asset_data)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

export_annotations(dataset_id, "exported_annotations.json", client)
```

### Update Multiple Annotations

```python
# Batch update annotations by category
old_category = "vehicle"
new_category = "car"

for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        annotations = client.annotations.list(
            dataset_id=dataset_id,
            asset_id=asset.asset_id
        )

        for ann in annotations.items:
            if ann.category == old_category:
                client.annotations.update(
                    dataset_id=dataset_id,
                    asset_id=asset.asset_id,
                    annotation_id=ann.annotation_id,
                    category=new_category
                )
```

### Filter Annotations

```python
# Find all phrase grounding annotations
phrase_grounding_anns = []

for page in client.assets.list(dataset_id=dataset_id):
    for asset in page.items:
        annotations = client.annotations.list(
            dataset_id=dataset_id,
            asset_id=asset.asset_id
        )

        for ann in annotations.items:
            ann_details = client.annotations.get(
                dataset_id=dataset_id,
                asset_id=asset.asset_id,
                annotation_id=ann.annotation_id
            )

            if hasattr(ann_details.contents, "caption"):
                phrase_grounding_anns.append(ann_details)

print(f"Found {len(phrase_grounding_anns)} phrase grounding annotations")
```
