#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   nvila.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA predictor module.
"""

from qwen_vl_utils import process_vision_info
from rich import print as rprint
from vi.inference.messages import create_system_message, create_user_message_with_image
from vi.inference.predictors.hf import HFPredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=["torch", "xgrammar", "qwen_vl_utils"],
        dependency_group="nvila",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

# NOTE: This import must be after check_imports since the config depends on torch
from vi.inference.config.nvila import NVILAGenerationConfig


@PredictorRegistry.register(
    predictor_key="nvila",
    loader_types=["NVILALoader"],
)
class NVILAPredictor(HFPredictor[NVILAGenerationConfig]):
    """NVILA predictor for vision-language tasks.

    Handles NVILA-specific preprocessing, inference, and output parsing for
    vision-language tasks. Works with Datature Vi fine-tuned models that
    include structured output generation via xgrammar.

    Supported task types:
        - Visual Question Answering (VQA): User prompt is required in the form of a question
        - Phrase Grounding: User prompt is optional (uses default prompt if not provided)

    Example:
        ```python
        from vi.inference.loaders import ViLoader
        from vi.inference.predictors import NVILAPredictor

        # Load model and create predictor
        loader = ViLoader.from_pretrained("Efficient-Large-Model/NVILA-8B")
        predictor = NVILAPredictor(loader)

        # Run inference
        result = predictor(
            source="image.jpg", user_prompt="What objects are in this image?"
        )
        print(result)
        ```

    Note:
        This predictor is designed for Datature Vi fine-tuned models with
        processor and xgrammar compiler. For pretrained models without these
        components, you'll need to implement a custom predictor.

    """

    def get_generation_config_class(self) -> type[NVILAGenerationConfig]:
        """Return the generation config class for NVILA models.

        Returns:
            NVILAGenerationConfig class.

        """
        return NVILAGenerationConfig

    def _prepare_inputs(
        self,
        source: str,
        effective_prompt: str,
        system_prompt: str,
    ) -> dict:
        """Prepare model inputs from image source and prompts.

        Uses qwen_vl_utils for NVILA models (compatible with Qwen format).

        Args:
            source: Path to image file.
            effective_prompt: User prompt to use.
            system_prompt: System prompt (may include CoT suffix).

        Returns:
            Dictionary of model inputs ready for generation.

        """
        messages = [
            create_system_message(system_prompt),
            create_user_message_with_image(source, effective_prompt),
        ]

        input_text = self._loader.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, _ = process_vision_info(messages)

        inputs = self._loader.processor(
            text=[input_text], images=image_inputs, padding=True, return_tensors="pt"
        ).to(self._loader.model.device)

        return inputs
