"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██
@File    :   deepseekocr.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK DeepSeekOCR predictor module.
"""

from PIL import Image
from rich import print as rprint
from vi.inference.config.deepseekocr import DeepSeekOCRGenerationConfig
from vi.inference.errors import wrap_configuration_error
from vi.inference.predictors.hf import HFPredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=["torch", "xgrammar", "transformers"],
        dependency_group="deepseekocr",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise


@PredictorRegistry.register(
    predictor_key="deepseekocr",
    loader_types=["DeepSeekOCRLoader"],
)
class DeepSeekOCRPredictor(HFPredictor[DeepSeekOCRGenerationConfig]):
    """Predictor for DeepSeekOCR vision-language models.

    Handles preprocessing, inference, and output parsing for vision-language
    tasks using DeepSeekOCR models. Works with Datature Vi fine-tuned models
    that include structured output generation via xgrammar.

    Supported task types:
        - Visual Question Answering (VQA): User prompt is required in the form of a question
        - Phrase Grounding: User prompt is optional (uses default prompt if not provided)

    Example:
        ```python
        from vi.inference.loaders import ViLoader
        from vi.inference.predictors import DeepSeekOCRPredictor

        # Load DeepSeekOCR model and create predictor
        loader = ViLoader.from_pretrained("deepseek-ai/DeepSeek-OCR")
        predictor = DeepSeekOCRPredictor(loader)

        # Run inference
        result = predictor(
            source="image.jpg", user_prompt="What text is in this image?"
        )
        print(result)
        ```

    Note:
        This predictor is designed for Datature Vi fine-tuned models with
        processor and xgrammar compiler. For pretrained models without these
        components, you'll need to implement a custom predictor.

    """

    def get_generation_config_class(self) -> type[DeepSeekOCRGenerationConfig]:
        """Return the generation config class for DeepSeekOCR models.

        Returns:
            DeepSeekOCRGenerationConfig class.

        """
        return DeepSeekOCRGenerationConfig

    def _validate_processor(self) -> None:
        """Validate that loader has a processor.

        Uses wrap_configuration_error for better error messages.

        Raises:
            AttributeError: If processor is missing or None.

        """
        if not hasattr(self._loader, "processor") or self._loader.processor is None:
            raise wrap_configuration_error(
                AttributeError(
                    "Predictor requires a loader with a processor. "
                    "The provided loader may not be properly configured."
                ),
                component="processor",
            )

    def _validate_compiler(self) -> None:
        """Validate that loader has a compiler.

        Uses wrap_configuration_error for better error messages.

        Raises:
            AttributeError: If compiler is missing or None.

        """
        if not hasattr(self._loader, "compiler") or self._loader.compiler is None:
            raise wrap_configuration_error(
                AttributeError(
                    "Predictor requires a loader with an xgrammar compiler. "
                    "This predictor is designed for Datature Vi fine-tuned models."
                ),
                component="compiler",
            )

    def _validate_metadata(self) -> None:
        """Validate that loader metadata has required fields.

        Uses wrap_configuration_error for better error messages.

        Raises:
            KeyError: If required metadata fields are missing.

        """
        if "task_type" not in self._loader.metadata:
            raise wrap_configuration_error(
                KeyError(
                    "Loader metadata missing 'task_type'. This predictor requires a "
                    "Datature Vi fine-tuned model with task type configuration."
                ),
                component="metadata",
            )

    def _prepare_inputs(
        self,
        source: str,
        effective_prompt: str,
        system_prompt: str,
    ) -> dict:
        """Prepare model inputs from image source and prompts.

        Args:
            source: Path to image file.
            effective_prompt: User prompt to use.
            system_prompt: System prompt (may include CoT suffix).

        Returns:
            Dictionary of model inputs ready for generation.

        """
        # Load image
        image = Image.open(source)

        # Create conversation format for DeepSeekOCR
        conversations = [
            {"role": "User", "content": effective_prompt},
        ]

        # Process inputs using DeepSeekOCR processor
        inputs = self._loader.processor(
            conversations=conversations,
            images=[image],
            force_batchify=True,
            system_prompt=system_prompt,
            inference_mode=True,
        ).to(self._loader.model.device)

        return inputs.to_dict()
