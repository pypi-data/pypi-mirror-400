# Model-Specific Requirements

This directory contains requirement files for different model architectures. Each file defines the dependencies needed for a specific model family.

## Structure

```
requirements/
├── qwen.txt          # Qwen2.5-VL specific dependencies
├── nvila.txt         # NVILA specific dependencies
└── README.md         # This file
```

## File Format

Each requirement file follows standard pip requirements format:

```txt
# Comments explain what packages are for
package-name>=version

# Can inherit from other files
-r {model_name}.txt
```

## Adding a New Model

To add support for a new model architecture:

1. **Create requirement file**: `{model_name}.txt`
   ```txt
   # Model XYZ specific dependencies

   model-xyz-utils>=1.0.0
   custom-package>=2.0.0
   ```

2. **Register the model**: Update your loader/predictor to reference this file:
   ```python
   from vi.inference.utils.module_import import check_imports

   check_imports(
       packages=["model_xyz_utils", "custom_package"],
       dependency_group="model_name",  # Must match filename without .txt
       auto_install=True,
   )
   ```

3. **Document**: Update this README with the new models

## Current Models

### Qwen2.5-VL (`qwen.txt`)
Specific to Qwen family models:
- `qwen-vl-utils` - Qwen-specific preprocessing

### NVILA (`nvila.txt`)
Specific to NVILA family models:
- `einops` - Einops for efficient tensor operations
- `qwen-vl-utils` - Qwen-specific preprocessing

### Cosmos Reason1 (`qwen.txt`)
Cosmos Reason1 models inherit from Qwen2.5-VL.

### InternVL 3.5 (`qwen.txt`)
InternVL 3.5 models inherit from Qwen2.5-VL.

### DeepSeekOCR
DeepSeekOCR models use only the base inference requirements (torch, transformers, xgrammar) and do not require a separate requirements file.

## Usage

Users can install dependencies for specific models:

```bash
# Install only Qwen dependencies
pip install -r vi/inference/requirements/qwen.txt

# Or let the SDK auto-install when loading a model
python3 -c "from vi.inference.loaders import ViLoader; ViLoader.from_pretrained('Qwen/...')"
```

## Notes

- Files are automatically discovered by `check_imports()` function
- Dependency group name must match filename (without .txt)
- Keep version constraints compatible across models
