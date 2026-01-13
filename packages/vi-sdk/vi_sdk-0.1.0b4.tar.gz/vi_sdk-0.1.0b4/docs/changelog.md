# Changelog

All notable changes to the Datature Vi SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Core Client
- `Client` class for API interactions
- `SecretKeyAuth` for authentication
- Automatic credential loading from environment variables or config file
- Configurable HTTP client with retry logic

#### Dataset Management
- Create, list, retrieve, and delete datasets
- Create and manage dataset exports
- Download complete datasets with assets and annotations
- Support for `VI_FULL` and `VI_JSONL` export formats

#### Asset Management
- Upload single files or entire folders
- Batch upload with concurrent connections
- List and filter assets
- Download assets individually or in bulk
- Delete assets

#### Annotation Management
- Upload annotations in JSONL format
- List annotations by dataset and asset
- Download annotations
- Support for captions and grounded phrases
- Delete annotations

#### Model Training & Inference
- List training runs and their status
- List and download trained models
- Load models for inference locally
- Vision-language model inference (Qwen2.5-VL and NVILA)
- Support for VQA and phrase grounding tasks

#### Dataset Loaders
- `ViDataset` for loading downloaded datasets
- Iterate through training, validation, and dump splits
- Access assets and annotations
- PyTorch-compatible dataset wrappers
- Visualization utilities

#### Logging
- Structured logging with JSON, plain text, and pretty formats
- File and console output
- Configurable log levels
- HTTP request/response logging
- Environment variable configuration
- Log rotation support

#### Error Handling
- Specific exception types for different error scenarios
- Retryable error detection
- Error suggestions and details
- HTTP status code mapping

### Core Features
- Pagination support for list operations
- Progress tracking for uploads and downloads
- Concurrent operations for improved performance

---

[Unreleased]: https://github.com/datature/Vi-SDK/compare/HEAD
