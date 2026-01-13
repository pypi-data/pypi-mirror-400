# Python SDK for Datature Vi

[![PyPI version](https://badge.fury.io/py/vi-sdk.svg)](https://pypi.org/project/vi-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/vi-sdk.svg)](https://pypi.org/project/vi-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python SDK for [Datature Vi](https://vi.datature.com) - a powerful platform for vision-language model training and inference.

## 🚀 Installation

```bash
pip install vi-sdk
```

For inference capabilities:
```bash
pip install vi-sdk[inference]
```

## 📖 Documentation

Visit our comprehensive documentation at [vi.developers.datature.com](https://vi.developers.datature.com/docs/vi-sdk)

## 🎯 Quick Start

```python
import vi

# Initialize client
client = vi.Client()

# List datasets
datasets = client.datasets.list()
for dataset in datasets:
    print(f"Dataset: {dataset.name}")
```

## ✨ Features

- **Dataset Management**: Create, upload, and manage datasets
- **Asset Operations**: Batch upload and download with progress tracking
- **Annotations**: JSONL format support for captions and grounding
- **Model Training**: Track runs and manage trained models
- **Inference**: Local VLM inference (Qwen2.5-VL, NVILA)
- **Dataset Loaders**: PyTorch-compatible data loading utilities

## 📝 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Development Setup

We use pre-commit hooks to ensure code quality:

```bash
# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Verify setup
uv run pre-commit run --all-files
```

📖 **Documentation:**
- [Development Guide](../../.github/DEVELOPMENT.md) - Complete development workflow
- [Pre-commit Setup](../../.github/PRE_COMMIT_SETUP.md) - Quick reference for hooks
- [Setup Summary](../../.github/SETUP_SUMMARY.md) - Overview of CI/CD improvements

## 🐛 Issues

Report issues on [GitHub Issues](https://github.com/datature/Vi-SDK/issues)
