---
title: "Installation"
excerpt: "Install the Vi SDK and its dependencies"
category: "getting-started"
---

# Installation

This guide will help you install the Vi SDK and its dependencies.

---

## Requirements

- Python 3.10 or higher
- pip (Python package installer)
- Internet connection for API access

---

## Basic Installation

The simplest way to install Vi SDK is using pip:

```bash
pip install vi-sdk
```

This installs the core SDK with all essential features for:

- Dataset management
- Asset operations
- Annotation workflows
- Model operations
- API client functionality

---

## Installation with Optional Features

Vi SDK provides several optional feature sets that can be installed as needed:

### Inference Support

For running inference with vision-language models (Qwen2.5-VL, InternVL 3.5, Cosmos Reason1, NVILA, etc.):

```bash
pip install vi-sdk[inference]
```

This includes:

- `transformers` - Hugging Face Transformers for model loading
- `torch` - PyTorch for deep learning
- `xgrammar` - Structured output generation
- `accelerate` - Model acceleration utilities
- `bitsandbytes` - Quantization support

### All Features

To install everything:

```bash
pip install vi-sdk[all]
```

This includes all optional dependencies for the complete Vi SDK experience.

---

## Installation from Source

For development or to use the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/datature/Vi-SDK.git
cd Vi-SDK/pypi/vi-sdk

# Install in development mode
pip install -e .

# Or install with all features
pip install -e .[all]
```

---

## Virtual Environment (Recommended)

We strongly recommend using a virtual environment to avoid dependency conflicts.

### Using venv

```bash
# Create virtual environment
python3 -m venv vi-env

# Activate (Linux/macOS)
source vi-env/bin/activate

# Activate (Windows)
vi-env\Scripts\activate

# Install Vi SDK
pip install vi-sdk[all]
```

### Using conda

```bash
# Create conda environment
conda create -n vi-env python=3.10

# Activate environment
conda activate vi-env

# Install Vi SDK
pip install vi-sdk[all]
```

### Using uv

```bash
# Create uv virtual environment
uv venv vi-env

# Activate environment
source vi-env/bin/activate  # Linux/macOS
# or
vi-env\Scripts\activate  # Windows

# Install Vi SDK
uv pip install vi-sdk[all]
```

---

## Verifying Installation

Verify that Vi SDK is installed correctly:

```python
import vi

print(f"Vi SDK version: {vi.__version__}")
print("Installation successful!")
```

You should see output similar to:

```
Vi SDK version: 0.1.0b0
Installation successful!
```

---

## GPU Support (for Inference)

If you plan to use the inference features with GPU acceleration:

### CUDA (NVIDIA GPUs)

```bash
# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Then install Vi SDK with inference
pip install vi-sdk[inference]
```

### MPS (Apple Silicon)

PyTorch automatically detects and uses MPS on Apple Silicon Macs with macOS 12.3+:

```bash
pip install vi-sdk[inference]
```

### CPU Only

If you don't have a GPU or prefer CPU-only inference:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install vi-sdk[inference]
```

---

## Troubleshooting

### Common Issues

#### ImportError: No module named 'vi'

**Solution:** Ensure Vi SDK is installed in the correct Python environment:

```bash
python -m pip install vi-sdk
```

#### Version Conflicts

If you encounter dependency conflicts:

```bash
# Create a fresh environment
python -m venv fresh-env
source fresh-env/bin/activate  # or appropriate activation command

# Install Vi SDK
pip install vi-sdk[all]
```

#### SSL Certificate Errors

If you see SSL errors during installation:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org vi-sdk
```

#### Permission Errors

On Linux/macOS, if you see permission errors:

```bash
# Use --user flag
pip install --user vi-sdk

# Or use a virtual environment (recommended)
python -m venv vi-env
source vi-env/bin/activate
pip install vi-sdk
```

---

## Platform-Specific Notes

### Linux

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3-pip python3-virtualenv
```

### macOS

Install Python using Homebrew:

```bash
brew install python@3.10
```

### Windows

Download Python from [python.org](https://www.python.org/downloads/)

Ensure "Add Python to PATH" is checked during installation.

---

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade vi-sdk
```

To upgrade with all features:

```bash
pip install --upgrade vi-sdk[all]
```

---

## Uninstalling

To uninstall Vi SDK:

```bash
pip uninstall vi-sdk
```

---

## Next Steps

Now that you have Vi SDK installed:

1. **[Quickstart Guide](vi-sdk-quickstart)** - Get started with basic operations
2. **[Authentication](vi-sdk-authentication)** - Set up your API credentials
3. **[Configuration](vi-sdk-configuration)** - Configure logging and other settings

---

## Getting Help

If you encounter issues not covered here:

- Check our [GitHub Issues](https://github.com/datature/Vi-SDK/issues)
- Email [developers@datature.io](mailto:developers@datature.io)
