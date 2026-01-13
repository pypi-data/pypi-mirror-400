---
title: "Annotations API Reference"
excerpt: "Handle annotation exports, imports, and batch operations"
category: "api-reference"
---

# Annotations API Reference

Complete API reference for annotation operations. Handle annotation exports, imports, downloads, and batch operations through this resource.

---

## Annotation Resource

Access annotations through `client.annotations`.

---

## Methods

### list()

List annotations for an asset.

```python
# Basic listing
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

for annotation in annotations.items:
    print(f"ID: {annotation.annotation_id}")
    print(f"Type: {annotation.spec.bound_type}")
```

```python
# With custom pagination
from vi.api.types import PaginationParams

annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    pagination=PaginationParams(page_size=100)
)

for annotation in annotations.items:
    print(f"{annotation.annotation_id}: {annotation.spec.bound_type}")
```

```python
# Using dict for pagination
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    pagination={"page_size": 100}
)
```

```python
# Iterate through all pages
for page in client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
):
    for annotation in page.items:
        print(f"{annotation.annotation_id}: {annotation.spec.bound_type}")
```

```python
# Collect all annotations for an asset
all_annotations = list(
    client.annotations.list(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789"
    ).all_items()
)

print(f"Total annotations: {len(all_annotations)}")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `asset_id` | `str` | Asset identifier | Required |
| `pagination` | [`PaginationParams`](vi-sdk-pagination#paginationparams)` \| dict` | Pagination settings | `PaginationParams()` |

**Returns:** [`PaginatedResponse`](vi-sdk-pagination#paginatedresponse)`[`[`Annotation`](#annotation)`]`

---

### get()

Get a specific annotation.

```python
# Basic usage
annotation = client.annotations.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)

print(f"Type: {annotation.spec.bound_type}")
print(f"Content: {annotation.spec.contents}")
```

```python
# Access caption content
annotation = client.annotations.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)

if hasattr(annotation.spec.contents, 'contents'):
    # It's a Caption
    print(f"Caption: {annotation.spec.contents.contents}")
```

```python
# Access bounding box content
annotation = client.annotations.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)

if hasattr(annotation.spec.contents, 'bound'):
    # It's a PhraseGroundingBoundingBox
    print(f"Bounds: {annotation.spec.contents.bound}")
    print(f"Target span: {annotation.spec.contents.target}")
```

```python
# Display detailed information
annotation = client.annotations.get(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)
annotation.info()  # Prints formatted annotation summary
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `asset_id` | `str` | Asset identifier |
| `annotation_id` | `str` | Annotation identifier |

**Returns:** [`Annotation`](#annotation)

---

### upload()

Upload annotations to a dataset.

```python
# Upload single JSONL file
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="annotations.jsonl",
    wait_until_done=True
)

print(f"✓ Imported: {result.total_annotations}")
```

```python
# Upload folder of annotation files
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="./annotations/",
    wait_until_done=True
)

print(result.summary())
```

```python
# Upload multiple specific files
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths=["batch1.jsonl", "batch2.jsonl"],
    wait_until_done=True
)
```

```python
# Upload and verify count
def upload_and_verify(dataset_id: str, annotations_path: str) -> bool:
    """Upload annotations and verify success."""

    # Count annotations in file
    with open(annotations_path) as f:
        local_count = sum(1 for _ in f)

    # Upload
    result = client.annotations.upload(
        dataset_id=dataset_id,
        paths=annotations_path,
        wait_until_done=True
    )

    # Verify
    print(f"Local: {local_count}")
    print(f"Imported: {result.total_annotations}")

    return result.total_annotations == local_count

success = upload_and_verify("dataset_abc123", "annotations.jsonl")
```

```python
# Create annotations programmatically and upload
import json
from pathlib import Path

def create_and_upload_annotations(dataset_id: str, images_dir: str):
    """Create annotations for images and upload."""
    annotations = []

    for image_path in Path(images_dir).glob("*.jpg"):
        annotation = {
            "asset_id": image_path.stem,
            "caption": f"Image of {image_path.stem}",
            "grounded_phrases": []
        }
        annotations.append(annotation)

    # Save to JSONL
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

    return result

result = create_and_upload_annotations("dataset_abc123", "./images")
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `dataset_id` | `str` | Dataset identifier | Required |
| `paths` | `str \| list[str]` | File/folder paths | Required |
| `wait_until_done` | `bool` | Wait for completion | `True` |

**Returns:** [`AnnotationUploadResult`](#annotationuploadresult)

---

### delete()

Delete an annotation.

```python
# Delete single annotation
deleted = client.annotations.delete(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789",
    annotation_id="annotation_xyz789"
)
```

```python
# Delete all annotations for an asset
annotations = client.annotations.list(
    dataset_id="dataset_abc123",
    asset_id="asset_xyz789"
)

for annotation in annotations.items:
    client.annotations.delete(
        dataset_id="dataset_abc123",
        asset_id="asset_xyz789",
        annotation_id=annotation.annotation_id
    )
    print(f"Deleted: {annotation.annotation_id}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `asset_id` | `str` | Asset identifier |
| `annotation_id` | `str` | Annotation identifier |

**Returns:** `DeletedAnnotation`

---

### wait_until_done()

Wait for an import session to complete.

```python
# Basic usage
status = client.annotations.wait_until_done(
    dataset_id="dataset_abc123",
    annotation_import_session_id="session_id"
)

print(f"Total: {status.status.annotations.status_count}")
```

```python
# After async upload
result = client.annotations.upload(
    dataset_id="dataset_abc123",
    paths="annotations.jsonl",
    wait_until_done=False
)

# Do other work...

# Then wait for completion
status = client.annotations.wait_until_done(
    dataset_id="dataset_abc123",
    annotation_import_session_id=result.session_id
)

print(f"Import complete: {status.status.annotations.status_count}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | Dataset identifier |
| `annotation_import_session_id` | `str` | Session identifier |

**Returns:** [`AnnotationImportSession`](#annotationimportsession)

---

## Response Types

### Annotation

Main annotation response object.

```python
from vi.api.resources.datasets.annotations.responses import Annotation
```

| Property | Type | Description |
|----------|------|-------------|
| `annotation_id` | `str` | Unique identifier |
| `asset_id` | `str` | Parent asset ID |
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `spec` | [`AnnotationSpec`](#annotationspec) | Annotation specification |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `info()` | `None` | Display formatted annotation information |

---

### AnnotationSpec

```python
from vi.api.resources.datasets.annotations.responses import AnnotationSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `bound_type` | `str` | Boundary type (box, polygon, etc.) |
| `tag` | `int` | Tag identifier |
| `aggregation` | [`AnnotationAggregation`](#annotationaggregation) | Aggregation info |
| `contents` | [`AnnotationContent`](#annotationcontent) | Annotation content |

---

### AnnotationAggregation

```python
from vi.api.resources.datasets.annotations.responses import AnnotationAggregation
```

| Property | Type | Description |
|----------|------|-------------|
| `whole` | [`Whole`](#whole) | Reference to complete annotation |
| `this_part` | [`ThisPart`](#thispart) | This part's role info |

---

### Whole

```python
from vi.api.resources.datasets.annotations.responses import Whole
```

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Parent annotation ID |

---

### ThisPart

```python
from vi.api.resources.datasets.annotations.responses import ThisPart
```

| Property | Type | Description |
|----------|------|-------------|
| `role` | [`Roles`](#roles) | Part role type |

---

### AnnotationContent

Union type for annotation content variants.

```python
from vi.api.resources.datasets.annotations.responses import AnnotationContent

AnnotationContent = Caption | PhraseGroundingBoundingBox
```

---

### Caption

Caption content for annotations.

```python
from vi.api.resources.datasets.annotations.responses import Caption
```

| Property | Type | Description |
|----------|------|-------------|
| `contents` | `str` | Caption text |

---

### PhraseGroundingBoundingBox

Bounding box for phrase grounding.

```python
from vi.api.resources.datasets.annotations.responses import PhraseGroundingBoundingBox
```

| Property | Type | Description |
|----------|------|-------------|
| `bound` | `list[list[float]]` | 4 coordinate pairs `[[x1,y1], [x2,y1], [x2,y2], [x1,y2]]` |
| `target` | `tuple[int, int]` | Phrase span `(start_index, end_index)` |

---

### AnnotationUploadResult

Result from uploading annotations.

| Property | Type | Description |
|----------|------|-------------|
| `session_id` | `str` | Import session ID |
| `total_annotations` | `int` | Total annotations imported |
| `session` | [`AnnotationImportSession`](#annotationimportsession) | Session details |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `summary()` | `str` | Get summary string |

---

### AnnotationImportSession

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportSession
```

| Property | Type | Description |
|----------|------|-------------|
| `user` | `str` | Initiating user ID |
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `annotation_import_session_id` | `str` | Session identifier |
| `self_link` | `str` | API link |
| `etag` | `str` | Entity tag |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |
| `spec` | [`AnnotationImportSpec`](#annotationimportspec) | Import specification |
| `status` | [`AnnotationImportSessionStatus`](#annotationimportsessionstatus) | Session status |

---

### AnnotationImportSpec

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportSpec
```

| Property | Type | Description |
|----------|------|-------------|
| `upload_before` | `int` | Upload deadline timestamp |
| `failure_policies` | [`AnnotationImportFailurePolicy`](#annotationimportfailurepolicy) | Failure handling |
| `source` | [`AnnotationImportSource`](#annotationimportsource) | Import source type |

---

### AnnotationImportFailurePolicy

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportFailurePolicy
```

| Property | Type | Description |
|----------|------|-------------|
| `on_bad_annotation` | [`FailurePolicy`](#failurepolicy) | Bad annotation handling |
| `on_bad_file` | [`FailurePolicy`](#failurepolicy) | Bad file handling |
| `on_overwritten` | [`FailurePolicy`](#failurepolicy) | Overwrite handling |

---

### AnnotationImportSessionStatus

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportSessionStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[`[`AnnotationImportSessionCondition`](#annotationimportsessioncondition)`]` | Session conditions |
| `files` | [`AnnotationFileStatus`](#annotationfilestatus) | File status |
| `annotations` | [`AnnotationStatus`](#annotationstatus) | Annotation status |
| `reason` | `str \| None` | Status reason |

---

### AnnotationImportSessionCondition

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportSessionCondition
```

| Property | Type | Description |
|----------|------|-------------|
| `condition` | `str` | Condition name |
| `status` | [`ConditionStatus`](vi-sdk-types#conditionstatus) | Condition status |
| `last_transition_time` | `int \| float` | Transition timestamp |
| `reason` | [`ConditionReason`](#conditionreason)` \| None` | Condition reason |

---

### AnnotationFileStatus

```python
from vi.api.resources.datasets.annotations.responses import AnnotationFileStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `page_count` | `int` | Pages processed |
| `total_size_bytes` | `int` | Total size in bytes |
| `status_count` | `dict[str, int]` | Status distribution |

---

### AnnotationStatus

```python
from vi.api.resources.datasets.annotations.responses import AnnotationStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `status_count` | `dict[str, int]` | Status distribution |

---

### ExportedAnnotations

```python
from vi.api.resources.datasets.annotations.responses import ExportedAnnotations
```

| Property | Type | Description |
|----------|------|-------------|
| `kind` | `str` | Resource kind |
| `organization_id` | `str` | Organization ID |
| `dataset_id` | `str` | Dataset ID |
| `dataset_export_id` | `str` | Export identifier |
| `spec` | `dict[str, Any]` | Export specification |
| `status` | [`ExportedAnnotationsStatus`](#exportedannotationsstatus) | Export status |
| `metadata` | [`ResourceMetadata`](vi-sdk-types#resourcemetadata) | Metadata |

---

### ExportedAnnotationsStatus

```python
from vi.api.resources.datasets.annotations.responses import ExportedAnnotationsStatus
```

| Property | Type | Description |
|----------|------|-------------|
| `conditions` | `list[dict]` | Status conditions |
| `download_url` | [`ExportedAnnotationsDownloadUrl`](#exportedannotationsdownloadurl) | Download URL |

---

### ExportedAnnotationsDownloadUrl

```python
from vi.api.resources.datasets.annotations.responses import ExportedAnnotationsDownloadUrl
```

| Property | Type | Description |
|----------|------|-------------|
| `url` | `str` | Download URL |
| `expires_at` | `int` | Expiration timestamp |

---

## Enums

### Roles

```python
from vi.api.resources.datasets.annotations.responses import Roles
```

| Value | Description |
|-------|-------------|
| `CAPTION` | Caption annotation |
| `PHRASE_GROUNDING_BOUNDING_BOX` | Phrase grounding bounding box |

---

### FailurePolicy

```python
from vi.api.resources.datasets.annotations.responses import FailurePolicy
```

| Value | Description |
|-------|-------------|
| `WARN` | Log warning and continue |
| `REJECT_FILE` | Reject the file |
| `REJECT_SESSION` | Reject entire session |

---

### AnnotationImportSource

```python
from vi.api.resources.datasets.annotations.responses import AnnotationImportSource
```

| Value | Description |
|-------|-------------|
| `UPLOADED_INDIVIDUAL_FILES` | Uploaded individual files |

---

### ConditionReason

```python
from vi.api.resources.datasets.annotations.responses import ConditionReason
```

| Value | Description |
|-------|-------------|
| `CANCELLED_BY_USER` | Cancelled by user |
| `USER_UPLOAD_ERRORED` | Upload error |

---

## Annotation Formats

### Phrase Grounding Format

```json
{
  "asset_id": "asset_123",
  "caption": "A cat sitting on a couch",
  "grounded_phrases": [
    {
      "phrase": "cat",
      "bbox": [0.1, 0.2, 0.5, 0.7]
    },
    {
      "phrase": "couch",
      "bbox": [0.6, 0.2, 0.9, 0.7]
    }
  ]
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | `str` | Asset identifier (required) |
| `caption` | `str` | Caption text |
| `grounded_phrases` | `list[GroundedPhrase]` | List of grounded phrases |

**GroundedPhrase Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `phrase` | `str` | Phrase text |
| `bbox` | `list[float]` | Normalized bbox `[x_min, y_min, x_max, y_max]` |

---

### VQA Format

```json
{
  "asset_id": "asset_123",
  "contents": {
    "interactions": [
      {
        "question": "What is the cat doing?",
        "answer": "Sitting on a couch"
      }
    ]
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | `str` | Asset identifier (required) |
| `contents.interactions` | `list[Interaction]` | Q&A pairs |

**Interaction Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `question` | `str` | Question text |
| `answer` | `str` | Answer text |

---

## Coordinate System

Bounding box coordinates are normalized to `[0, 1]` range:

- `x_min`: Left edge (0 = left, 1 = right)
- `y_min`: Top edge (0 = top, 1 = bottom)
- `x_max`: Right edge
- `y_max`: Bottom edge

**Convert to Pixels:**

```python
def to_pixels(bbox: list[float], width: int, height: int) -> list[int]:
    """Convert normalized bbox to pixel coordinates."""
    x_min, y_min, x_max, y_max = bbox
    return [
        int(x_min * width),
        int(y_min * height),
        int(x_max * width),
        int(y_max * height)
    ]

# Example
bbox = [0.1, 0.2, 0.5, 0.7]
pixel_bbox = to_pixels(bbox, 1920, 1080)
# Result: [192, 216, 960, 756]
```

**Convert from Pixels:**

```python
def from_pixels(bbox: list[int], width: int, height: int) -> list[float]:
    """Convert pixel coordinates to normalized bbox."""
    x_min, y_min, x_max, y_max = bbox
    return [
        x_min / width,
        y_min / height,
        x_max / width,
        y_max / height
    ]
```

---

## See Also

- [Working with Annotations Guide](vi-sdk-annotations) - Comprehensive guide
- [Datasets API](vi-sdk-datasets-api) - Dataset operations
- [Assets API](vi-sdk-assets-api) - Asset operations
- [Types API](vi-sdk-types) - Common types
- [Pagination API](vi-sdk-pagination) - Pagination utilities
