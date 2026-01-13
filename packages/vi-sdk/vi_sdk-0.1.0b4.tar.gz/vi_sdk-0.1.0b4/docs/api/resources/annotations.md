# Annotations API

Complete API reference for annotation operations. Handle annotation exports, imports, downloads, and batch operations through this resource.

## Annotation Resource

::: vi.api.resources.datasets.Annotation
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Response Models

### Annotation

::: vi.api.resources.datasets.annotations.responses.Annotation
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Exported Annotations

::: vi.api.resources.datasets.annotations.responses.ExportedAnnotations
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Downloaded Annotations

::: vi.api.resources.datasets.annotations.responses.DownloadedAnnotations
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### Annotation Upload Result

::: vi.api.resources.datasets.annotations.results.AnnotationUploadResult
    options:
      show_root_heading: true
      show_source: false

### Annotation Import Session

::: vi.api.resources.datasets.annotations.responses.AnnotationImportSession
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## See Also

- [User Guide: Handling Annotations](../../guide/annotations.md)
- [Datasets API](datasets.md)
- [Assets API](assets.md)
