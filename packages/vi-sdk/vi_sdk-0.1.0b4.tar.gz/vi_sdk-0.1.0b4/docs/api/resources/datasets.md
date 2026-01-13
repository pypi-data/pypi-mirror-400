# Datasets API

Complete API reference for dataset operations. All dataset management, exports, downloads, and asset operations are handled through this resource.

## Dataset Resource

::: vi.api.resources.datasets.Dataset
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Response Models

### Dataset

::: vi.api.resources.datasets.responses.Dataset
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Dataset Export

::: vi.api.resources.datasets.responses.DatasetExport
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Dataset Download Result

::: vi.api.resources.datasets.results.DatasetDownloadResult
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Bulk Asset Deletion Session

::: vi.api.resources.datasets.responses.BulkAssetDeletionSession
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## See Also

- [User Guide: Working with Datasets](../../guide/datasets.md)
- [Assets API](assets.md)
- [Annotations API](annotations.md)
- [Dataset Loaders](../dataset-loaders/dataset-loaders.md)
