# Dataset Loaders API

Complete API reference for local dataset loading. Load and iterate through locally downloaded datasets with ease.

## ViDataset Class

::: vi.dataset.loaders.loader.ViDataset
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

## Dataset Split Classes

### ViDatasetSplit

::: vi.dataset.loaders.types.datasets.ViDatasetSplit
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3
      members:
        - iter_pairs
        - visualize

### ViDatasetTraining

::: vi.dataset.loaders.types.datasets.ViDatasetTraining
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViDatasetValidation

::: vi.dataset.loaders.types.datasets.ViDatasetValidation
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViDatasetDump

::: vi.dataset.loaders.types.datasets.ViDatasetDump
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Type Classes

### ViAsset (Image)

::: vi.dataset.loaders.types.assets.Image
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViAnnotation

::: vi.dataset.loaders.types.annotations.ViAnnotation
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### PhraseGrounding

::: vi.dataset.loaders.types.annotations.PhraseGrounding
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### VQA

::: vi.dataset.loaders.types.annotations.Vqa
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Information Classes

### ViDatasetInfo

::: vi.dataset.loaders.loader.ViDatasetInfo
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### ViDatasetSplitInfo

::: vi.dataset.loaders.loader.ViDatasetSplitInfo
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## Visualization Utilities

### visualize_image_with_annotations

::: vi.dataset.loaders.utils.visualize.visualize_image_with_annotations
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### visualize_phrase_grounding

::: vi.dataset.loaders.utils.visualize.visualize_phrase_grounding
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

### visualize_vqa

::: vi.dataset.loaders.utils.visualize.visualize_vqa
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3

## See Also

- [User Guide: Dataset Loaders](../../guide/dataset-loaders.md)
- [Datasets API](../resources/datasets.md)
- [Assets API](../resources/assets.md)
- [Inference API](../inference/inference.md)
