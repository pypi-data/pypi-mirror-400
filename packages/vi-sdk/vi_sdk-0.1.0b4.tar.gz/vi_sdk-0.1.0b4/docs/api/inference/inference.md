# Inference API

Complete API reference for model inference. Load fine-tuned models and perform predictions with structured outputs.

!!! info "Currently Supported"
    **Models:**

    - Qwen2.5-VL
    - InternVL 3.5
    - Cosmos Reason1
    - NVILA

    **Task Types:**

    - **Visual Question Answering (VQA)**: User prompt is required in the form of a question
    - **Phrase Grounding**: User prompt is optional

    More models and task types will be supported in future releases.

## ViModel (Recommended)

### ViModel

::: vi.inference.ViModel
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Model Loader

### ViLoader

::: vi.inference.ViLoader
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Predictors

### ViPredictor

::: vi.inference.ViPredictor
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
      show_signature: true
      show_signature_annotations: true
      separate_signature: true
      merge_init_into_class: true
      members_order: source
      group_by_category: true

## Task Types

### Visual Question Answering (VQA)

#### VQA

::: vi.inference.task_types.vqa.VQA
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

#### VQAAssistant

::: vi.inference.task_types.vqa.VQAAssistant
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

#### VQAPair

::: vi.inference.task_types.vqa.VQAPair
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

### Phrase Grounding

#### PhraseGrounding

::: vi.inference.task_types.phrase_grounding.PhraseGrounding
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

#### PhraseGroundingAssistant

::: vi.inference.task_types.phrase_grounding.PhraseGroundingAssistant
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

#### GroundedPhrase

::: vi.inference.task_types.phrase_grounding.GroundedPhrase
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

## See Also

- [User Guide: Inference](../../guide/inference.md)
- [Models API](../resources/models.md)
- [Dataset Loaders](../dataset-loaders/dataset-loaders.md)
- [NIM Deployment](../deployment/nim.md)
