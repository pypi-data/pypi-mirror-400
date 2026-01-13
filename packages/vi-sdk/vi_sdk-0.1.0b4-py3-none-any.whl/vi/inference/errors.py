#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   errors.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference-specific errors module.
"""

from vi.client.errors import ViError, ViErrorCode


class ViModelConfigurationError(ViError):
    """Raised when model configuration is invalid or incomplete.

    This typically occurs when:
    - Required model components are missing (processor, compiler)
    - Model architecture is incompatible
    - Configuration files are corrupt or missing
    """

    def __init__(
        self,
        message: str = "Model configuration error",
        component: str | None = None,
        **kwargs,
    ):
        """Initialize model configuration error.

        Args:
            message: Error message
            component: Missing or invalid component (e.g., "processor", "compiler")
            **kwargs: Additional error context

        """
        # Build detailed suggestion based on component
        suggestions = []

        if component == "processor":
            suggestions.extend(
                [
                    "This usually means one of the following:",
                    "  1. You're using a non-Datature pretrained model without fine-tuning",
                    "     → Solution: Use a Datature fine-tuned model with run_id parameter",
                    "  2. The model download was incomplete or corrupted",
                    "     → Solution: Delete cached model and re-download:",
                    "       rm -rf ~/.datature/vi/models/<run_id>",
                    "       Then run your code again",
                    "  3. Model files are missing required components",
                    "     → Solution: Verify model export includes all required files",
                ]
            )

        elif component == "compiler":
            suggestions.extend(
                [
                    "This predictor requires xgrammar for structured output generation.",
                    "",
                    "Solutions:",
                    "  1. Install xgrammar:",
                    "     pip install xgrammar",
                    "  2. Use a Datature fine-tuned model (includes compiler):",
                    "     model = ViModel(run_id='your-run-id', ...)",
                    "  3. For pretrained models, implement a custom predictor without xgrammar",
                ]
            )

        elif component == "metadata":
            suggestions.extend(
                [
                    "The model is missing required metadata (task_type, system_prompt, etc.).",
                    "",
                    "Solutions:",
                    "  1. Use a Datature fine-tuned model with complete run configuration:",
                    "     model = ViModel(run_id='your-run-id', ...)",
                    "  2. Re-export your model from Datature with full configuration",
                    "  3. Verify run.json exists in model directory and contains 'task_type'",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Common solutions:",
                    "  1. Verify you're using a Datature fine-tuned model:",
                    "     model = ViModel(run_id='your-run-id', ...)",
                    "  2. Re-download the model with overwrite=True",
                    "  3. Check model directory contains all required files:",
                    "     - config.json (HuggingFace config)",
                    "     - run.json (Datature config)",
                    "     - model weights files",
                ]
            )

        suggestions.extend(
            [
                "",
                "Supported Models:",
                "  - Qwen2.5-VL (fine-tuned with Datature)",
                "  - NVILA (fine-tuned with Datature)",
                "  - Cosmos Reason1 (fine-tuned with Datature)",
                "  - InternVL 3.5 (fine-tuned with Datature)",
                "",
                "For more help: https://vi.developers.datature.com/docs/vi-sdk-inference",
            ]
        )

        kwargs.setdefault("error_code", ViErrorCode.VALIDATION_FAILED)
        kwargs.setdefault("suggestion", "\n".join(suggestions))

        super().__init__(message, **kwargs)


class ViModelLoadError(ViError):
    """Raised when model loading fails.

    This can occur due to:
    - Out of memory (model too large for available RAM/VRAM)
    - Missing dependencies
    - Incompatible hardware
    - Corrupted model files
    """

    def __init__(
        self,
        message: str = "Failed to load model",
        reason: str | None = None,
        **kwargs,
    ):
        """Initialize model load error.

        Args:
            message: Error message
            reason: Specific reason for failure (e.g., "out_of_memory", "dependency")
            **kwargs: Additional error context

        """
        suggestions = []

        if reason == "out_of_memory":
            suggestions.extend(
                [
                    "The model is too large for available memory.",
                    "",
                    "Solutions:",
                    "  1. Use smaller model size:",
                    "     - Check model size with ViModel.inspect(run_id='...')",
                    "     - Use a smaller variant of the model",
                    "  2. Enable memory-efficient loading:",
                    "     model = ViModel(..., low_cpu_mem_usage=True, device_map='auto')",
                    "  3. Use quantization to reduce memory:",
                    "     model = ViModel(..., load_in_8bit=True)  # or load_in_4bit=True",
                    "  4. Free up memory before loading:",
                    "     - Close other applications",
                    "     - Clear GPU cache: torch.cuda.empty_cache()",
                    "  5. Use a machine with more RAM/VRAM",
                ]
            )

        elif reason == "dependency":
            suggestions.extend(
                [
                    "Required dependencies are missing or incompatible.",
                    "",
                    "Solutions:",
                    "  1. Install inference dependencies:",
                    "     pip install vi-sdk[inference]",
                    "  2. For Qwen models, install qwen-specific packages:",
                    "     pip install qwen-vl-utils xgrammar",
                    "  3. Verify PyTorch is installed with CUDA support:",
                    "     pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118",
                    "  4. Check installed packages:",
                    "     pip list | grep -E '(torch|transformers|xgrammar|qwen)'",
                ]
            )

        elif reason == "hardware":
            suggestions.extend(
                [
                    "Model requires hardware or features not available on this system.",
                    "",
                    "Solutions:",
                    "  1. Check GPU availability:",
                    "     import torch",
                    "     print(torch.cuda.is_available())",
                    "  2. Use CPU-only mode (slower):",
                    "     model = ViModel(..., device_map='cpu')",
                    "  3. Verify CUDA version compatibility",
                    "  4. Try on a system with compatible hardware",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Common solutions:",
                    "  1. Check model is properly downloaded:",
                    "     - Use ViModel.inspect() to verify model exists",
                    "     - Re-download with overwrite=True if corrupted",
                    "  2. Verify dependencies:",
                    "     pip install vi-sdk[inference]",
                    "  3. Check available resources:",
                    "     - Free memory: df -h (disk) and free -h (RAM)",
                    "     - GPU status: nvidia-smi",
                    "  4. Enable verbose logging for more details:",
                    "     import logging",
                    "     logging.basicConfig(level=logging.DEBUG)",
                ]
            )

        suggestions.extend(
            [
                "",
                "For more help: https://vi.developers.datature.com/docs/vi-sdk-inference",
            ]
        )

        kwargs.setdefault("error_code", ViErrorCode.OPERATION_FAILED)
        kwargs.setdefault("suggestion", "\n".join(suggestions))

        super().__init__(message, **kwargs)


class ViInferenceError(ViError):
    """Raised when inference fails during execution.

    This can occur due to:
    - Invalid input (corrupted image, wrong format)
    - Missing required parameters (e.g., user_prompt for VQA)
    - Model runtime errors
    - Output parsing failures
    """

    def __init__(
        self,
        message: str = "Inference failed",
        reason: str | None = None,
        **kwargs,
    ):
        """Initialize inference error.

        Args:
            message: Error message
            reason: Specific reason for failure
            **kwargs: Additional error context

        """
        suggestions = []

        if reason == "missing_prompt":
            suggestions.extend(
                [
                    "VQA models require a user prompt (question).",
                    "",
                    "Solutions:",
                    "  1. Provide a user_prompt parameter:",
                    "     result = model(source='image.jpg', user_prompt='What is in this image?')",
                    "  2. Check model task type:",
                    "     info = ViModel.inspect(run_id='...')",
                    "     print(info.task_type)  # Should show 'VQA' or 'phrase_grounding'",
                    "  3. For phrase grounding, user_prompt is optional:",
                    "     result = model(source='image.jpg')  # Uses default prompt",
                ]
            )

        elif reason == "invalid_image":
            suggestions.extend(
                [
                    "The provided image is invalid, corrupted, or in an unsupported format.",
                    "",
                    "Solutions:",
                    "  1. Verify image file exists and is readable:",
                    "     from pathlib import Path",
                    "     print(Path('image.jpg').exists())",
                    "  2. Check image format is supported:",
                    "     - Supported: JPEG, PNG, GIF, BMP, TIFF",
                    "     - Try converting to JPEG/PNG if unsure",
                    "  3. Verify image is not corrupted:",
                    "     from PIL import Image",
                    "     Image.open('image.jpg').verify()",
                    "  4. Check file permissions",
                ]
            )

        elif reason == "output_parsing":
            suggestions.extend(
                [
                    "Model generated output but parsing failed.",
                    "",
                    "This can happen if:",
                    "  - Model output format is unexpected",
                    "  - xgrammar constraints are too restrictive",
                    "  - Model is not properly fine-tuned for structured output",
                    "",
                    "Solutions:",
                    "  1. Check model is a Datature fine-tuned model:",
                    "     info = ViModel.inspect(run_id='...')",
                    "  2. Try with more relaxed generation parameters:",
                    "     result = model(source='image.jpg', max_new_tokens=2048)",
                    "  3. Report issue to Datature support with model run_id",
                ]
            )

        else:
            suggestions.extend(
                [
                    "Common solutions:",
                    "  1. Verify input parameters are correct:",
                    "     - source: valid image path or URL",
                    "     - user_prompt: clear question (for VQA) or None (for phrase grounding)",
                    "  2. Check image is valid:",
                    "     from PIL import Image",
                    "     Image.open('image.jpg').show()",
                    "  3. Try with default parameters first:",
                    "     result = model(source='image.jpg', user_prompt='Describe this image')",
                    "  4. Enable verbose mode for detailed errors:",
                    "     import logging",
                    "     logging.basicConfig(level=logging.DEBUG)",
                ]
            )

        suggestions.extend(
            [
                "",
                "For more help: https://vi.developers.datature.com/docs/vi-sdk-inference",
            ]
        )

        kwargs.setdefault("error_code", ViErrorCode.OPERATION_FAILED)
        kwargs.setdefault("suggestion", "\n".join(suggestions))

        super().__init__(message, **kwargs)


def wrap_configuration_error(
    original_error: Exception, component: str | None = None
) -> ViModelConfigurationError:
    """Wrap an exception into ViModelConfigurationError with context.

    Args:
        original_error: The original exception
        component: Component that failed (e.g., "processor", "compiler")

    Returns:
        Wrapped error with actionable suggestions

    """
    return ViModelConfigurationError(
        message=str(original_error),
        component=component,
        details={"original_error": type(original_error).__name__},
    )


def wrap_load_error(
    original_error: Exception, reason: str | None = None
) -> ViModelLoadError:
    """Wrap an exception into ViModelLoadError with context.

    Args:
        original_error: The original exception
        reason: Reason for failure (e.g., "out_of_memory", "dependency")

    Returns:
        Wrapped error with actionable suggestions

    """
    # Try to detect reason from error message
    error_msg = str(original_error).lower()

    if reason is None:
        if "out of memory" in error_msg or "oom" in error_msg:
            reason = "out_of_memory"
        elif "no module" in error_msg or "import" in error_msg:
            reason = "dependency"
        elif "cuda" in error_msg or "gpu" in error_msg:
            reason = "hardware"

    return ViModelLoadError(
        message=str(original_error),
        reason=reason,
        details={"original_error": type(original_error).__name__},
    )


def wrap_inference_error(
    original_error: Exception, reason: str | None = None
) -> ViInferenceError:
    """Wrap an exception into ViInferenceError with context.

    Args:
        original_error: The original exception
        reason: Reason for failure

    Returns:
        Wrapped error with actionable suggestions

    """
    # Try to detect reason from error message
    error_msg = str(original_error).lower()

    if reason is None:
        if "prompt" in error_msg or "required" in error_msg:
            reason = "missing_prompt"
        elif "image" in error_msg or "cannot identify" in error_msg:
            reason = "invalid_image"
        elif "parse" in error_msg or "decode" in error_msg:
            reason = "output_parsing"

    return ViInferenceError(
        message=str(original_error),
        reason=reason,
        details={"original_error": type(original_error).__name__},
    )
