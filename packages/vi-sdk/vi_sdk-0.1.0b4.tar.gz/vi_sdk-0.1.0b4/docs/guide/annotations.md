# Working with Annotations

Learn how to create, manage, and work with annotations in your datasets.

## Overview

Annotations are labels and metadata attached to your assets. The Vi SDK supports:

- Uploading annotations in various formats
- Listing and filtering annotations
- Downloading annotations
- Working with different annotation types (captions, bounding boxes, etc.)
- Bulk annotation operations

## Annotation Types

### Phrase Grounding

Text with bounding box locations:

```json
{
  "asset_id": "asset_123",
  "contents": {
    "caption": "A cat sitting on a couch",
    "grounded_phrases": [
      {
        "phrase": "cat",
        "bound": [0.1, 0.2, 0.5, 0.7]
      },
      {
        "phrase": "couch",
        "bound": [0.6, 0.2, 0.9, 0.7]
      }
    ]
  }
}
```

### VQA

Question and answer pairs:

```json
{
  "asset_id": "asset_123",
  "contents": {
    "question": "What is the cat doing?",
    "answer": "Sitting on a couch"
  }
}
```

## Uploading Annotations

### Upload from File

```python
import vi

client = vi.Client()

# Upload annotations from JSONL file
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="annotations.jsonl",
    wait_until_done=True
)

print(f"✓ Upload complete!")
print(f"Session ID: {result.session_id}")
print(f"Total annotations: {result.total_annotations}")
print(result.summary())  # Rich formatted output
```

### Upload Folder

```python
# Upload all JSONL files in folder
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="./annotations/",
    wait_until_done=True
)
print(f"✓ Imported: {result.total_annotations} annotations")
print(result.summary())
```

### Upload Without Waiting

```python
# Start upload and return immediately
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="annotations.jsonl",
    wait_until_done=False
)
# Get session ID to check status later
session_id = result.session_id
```

### Check Upload Status

```python
# Wait for upload to complete
status = client.annotations.wait_until_done(
    dataset_id="dataset_abc123",
    annotation_import_session_id=session_id
)

print(f"Total annotations: {status.status.annotations.status_count}")
print(f"Files processed: {status.status.files.page_count}")
```

## Listing Annotations

### List All Annotations

```python
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

for annotation in annotations.items:
    print(f"📝 Annotation ID: {annotation.annotation_id}")
    print(f"   Asset ID: {annotation.asset_id}")
    print(f"   Type: {annotation.type}")
```

### Iterate All Pages

```python
# Automatic pagination
for page in client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
):
    for annotation in page.items:
        print(f"Processing: {annotation.annotation_id}")
```

### Custom Page Size

```python
from vi.api.types import PaginationParams

pagination = PaginationParams(page_size=100)
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    pagination=pagination
)
```

## Filtering Annotations

### Filter by Asset

```python
# Get annotations for specific asset
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)
```

### Filter by Tag

```python
# Get annotations with specific tag
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    metadata_query='tag == "person"'
)
```

## Getting Annotation Details

### Get Single Annotation

```python
annotation = client.annotations.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)

print(f"Annotation ID: {annotation.annotation_id}")
print(f"Asset ID: {annotation.asset_id}")
print(f"Type: {annotation.type}")
print(f"Data: {annotation.data}")
```

## Downloading Annotations

### Download All Annotations

```python
# Download as part of dataset
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    save_dir="./data"
)

# Annotations are in {save_dir}/training/annotations/
# and {save_dir}/validation/annotations/
```

### Download Only Annotations

```python
# Download annotations without assets
dataset = client.get_dataset(
    dataset_id="dataset_abc123",
    annotations_only=True,
    save_dir="./annotations"
)
```

## Deleting Annotations

### Delete Single Annotation

```python
deleted = client.annotations.delete(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)

print(f"Deleted: {deleted.deleted}")
```

### Delete Multiple Annotations

```python
# Get annotations to delete
annotations_to_delete = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    metadata_query='tag == "outdated"'
)

# Delete each one
for annotation in annotations_to_delete.items:
    try:
        client.annotations.delete(
            dataset_id="dataset_abc123",
            asset_id=annotation.asset_id,
            annotation_id=annotation.annotation_id
        )
        print(f"✓ Deleted {annotation.annotation_id}")
    except Exception as e:
        print(f"✗ Failed: {e}")
```

## Working with Annotation Formats

### Vi JSONL Format

```python
# Example annotation in Vi format
annotation = {
    "asset_id": "asset_123",
    "caption": "A red car on the street",
    "grounded_phrases": [
        {
            "phrase": "red car",
            "bbox": [0.2, 0.3, 0.6, 0.8]  # [x_min, y_min, x_max, y_max] normalized
        }
    ]
}

# Save to JSONL
import json
with open("annotations.jsonl", "w") as f:
    json.dump(annotation, f)
    f.write("\n")
```

### Converting from COCO

```python
def coco_to_vi(coco_annotation, asset_id, image_width, image_height):
    """Convert COCO annotation to Vi format."""
    x, y, w, h = coco_annotation["bbox"]

    return {
        "asset_id": asset_id,
        "bboxes": [{
            "tag": coco_annotation["category_name"],
            "bbox": [
                x / image_width,
                y / image_height,
                (x + w) / image_width,
                (y + h) / image_height
            ]
        }]
    }
```

### Creating Annotations Programmatically

```python
from pathlib import Path
import json

def create_annotations(assets_dir, output_file):
    """Create annotations for images in a folder."""
    annotations = []

    for image_path in Path(assets_dir).glob("*.jpg"):
        # Your annotation logic here
        annotation = {
            "asset_id": image_path.stem,  # Filename without extension
            "caption": f"Image of {image_path.stem}",
        }
        annotations.append(annotation)

    # Save to JSONL
    with open(output_file, "w") as f:
        for annotation in annotations:
            json.dump(annotation, f)
            f.write("\n")

# Usage
create_annotations("./images", "annotations.jsonl")
```

## Best Practices

### 1. Batch Upload

```python
# ✅ Good - upload all at once
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="./annotations/",
    wait_until_done=True
)
print(f"✓ Imported: {result.total_annotations} annotations")

# ❌ Bad - upload one by one
for file in annotation_files:
    client.annotations.upload(...)
```

### 2. Validate Before Upload

```python
import json

def validate_annotation(annotation):
    """Validate annotation format."""
    if "asset_id" not in annotation:
        return False, "Missing asset_id"

    if "caption" in annotation:
        if not isinstance(annotation["caption"], str):
            return False, "Caption must be string"

    if "grounded_phrases" in annotation:
        for phrase in annotation["grounded_phrases"]:
            if "phrase" not in phrase or "bbox" not in phrase:
                return False, "Invalid grounded phrase"

            bbox = phrase["bbox"]
            if len(bbox) != 4:
                return False, "bbox must have 4 values"

            if not all(0 <= coord <= 1 for coord in bbox):
                return False, "bbox coordinates must be normalized (0-1)"

    return True, "Valid"

# Validate before upload
with open("annotations.jsonl") as f:
    for line in f:
        annotation = json.loads(line)
        valid, message = validate_annotation(annotation)
        if not valid:
            print(f"❌ Invalid annotation: {message}")
```

### 3. Handle Upload Errors

```python
from vi import ViUploadError

try:
    result = client.annotations.upload(
        dataset_id="dataset_abc123",
        paths="annotations.jsonl",
        wait_until_done=True
    )

    # Check result
    print(f"✓ Imported: {result.total_annotations} annotations")
    print(result.summary())

except ViUploadError as e:
    print(f"Upload failed: {e.message}")
```

### 4. Coordinate Normalization

```python
def normalize_bbox(bbox, image_width, image_height):
    """Normalize absolute coordinates to 0-1 range."""
    x_min, y_min, x_max, y_max = bbox

    return [
        x_min / image_width,
        y_min / image_height,
        x_max / image_width,
        y_max / image_height
    ]

# Usage
normalized = normalize_bbox([100, 200, 400, 600], 1920, 1080)
```

## Common Workflows

### Upload and Verify

```python
def upload_and_verify_annotations(dataset_id, annotations_path):
    """Upload annotations and verify success."""
    # Count annotations in file
    import json
    with open(annotations_path) as f:
        local_count = sum(1 for _ in f)

    # Upload
    result = client.annotations.upload(
        dataset_id=dataset_id,
        paths=annotations_path,
        wait_until_done=True
    )

    # Verify
    print(f"Local annotations: {local_count}")
    print(f"Imported: {result.total_annotations}")
    print(result.summary())

    return result.total_annotations == local_count
```

### Update Existing Annotations

```python
def update_annotations(dataset_id, updates):
    """Update annotations with new data."""
    # Download current annotations
    dataset = client.get_dataset(
        dataset_id=dataset_id,
        annotations_only=True
    )

    # Modify annotations locally
    # ... your update logic ...

    # Re-upload
    result = client.annotations.upload(
        dataset_id=dataset_id,
        paths="updated_annotations.jsonl",
        wait_until_done=True
    )
    print(f"✓ Updated: {result.total_annotations} annotations")

    return result
```

### Generate Annotations from Model

```python
def generate_annotations_from_model(dataset_id, model_predictor):
    """Generate annotations using a model."""
    import json

    # Get assets
    assets = []
    for page in client.assets.list(dataset_id=dataset_id):
        assets.extend(page.items)

    # Generate annotations
    annotations = []
    for asset in assets:
        # Run model prediction
        result = model_predictor(asset.filename)

        annotation = {
            "asset_id": asset.asset_id,
            "caption": result.caption,
            "grounded_phrases": [
                {
                    "phrase": phrase.text,
                    "bbox": phrase.bbox
                }
                for phrase in result.phrases
            ]
        }
        annotations.append(annotation)

    # Save to file
    output_file = "generated_annotations.jsonl"
    with open(output_file, "w") as f:
        for annotation in annotations:
            json.dump(annotation, f)
            f.write("\n")

    # Upload
    result = client.annotations.upload(
        dataset_id=dataset_id,
        paths=output_file,
        wait_until_done=True
    )
    print(f"✓ Converted and uploaded: {result.total_annotations} annotations")

    return result
```

## Troubleshooting

### Annotations Not Appearing

1. Check upload status for errors
2. Verify annotation format is correct
3. Ensure asset_ids match existing assets
4. Wait for processing to complete

### Invalid Format Errors

```python
# Check error details
status = client.annotations.wait_until_done(
    dataset_id="dataset_abc123",
    annotation_import_session_id=session_id
)

# Look at events for specific errors
for event in status.status.events:
    if hasattr(event, 'files'):
        for file, error in event.files.items():
            print(f"Error in {file}: {error}")
```

### Coordinate Issues

Ensure coordinates are normalized:

- x, y, width, height should be in range [0, 1]
- x_min < x_max, y_min < y_max
- No coordinates outside image bounds

## See Also

- [Datasets Guide](datasets.md) - Managing parent datasets
- [Assets Guide](assets.md) - Working with assets
- [API Reference](../api/resources/annotations.md) - Complete API documentation
- [Examples](https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples) - Practical examples
