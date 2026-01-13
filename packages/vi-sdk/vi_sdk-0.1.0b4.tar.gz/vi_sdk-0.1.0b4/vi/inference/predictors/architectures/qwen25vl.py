#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   qwen25vl.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK Qwen2.5 VL predictor module.
"""

from qwen_vl_utils import process_vision_info
from rich import print as rprint
from vi.inference.errors import wrap_configuration_error
from vi.inference.messages import create_system_message, create_user_message_with_image
from vi.inference.predictors.hf import HFPredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=["torch", "xgrammar", "qwen_vl_utils"],
        dependency_group="qwen",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

from vi.inference.config.qwen25vl import Qwen25VLGenerationConfig


@PredictorRegistry.register(
    predictor_key="qwen25vl",
    loader_types=["Qwen25VLLoader"],
)
@PredictorRegistry.register(
    predictor_key="cosmosreason1",
    loader_types=["Qwen25VLLoader"],
)
@PredictorRegistry.register(
    predictor_key="internvl35",
    loader_types=["Qwen25VLLoader"],
)
@PredictorRegistry.register(
    predictor_key="llavanext",
    loader_types=["Qwen25VLLoader"],
)
class Qwen25VLPredictor(HFPredictor[Qwen25VLGenerationConfig]):
    """Predictor for Qwen2.5-VL compatible vision-language models.

    Handles preprocessing, inference, and output parsing for vision-language
    tasks. Works with Datature Vi fine-tuned models that include structured
    output generation via xgrammar.

    Supported model architectures:
        - Qwen2.5-VL (Qwen2_5_VLForConditionalGeneration)
        - InternVL 3.5 (InternVLForConditionalGeneration)
        - Cosmos Reason1 (Qwen2_5_VLForConditionalGeneration)
        - LLaVA-NeXT (LlavaNextForConditionalGeneration)

    Supported task types:
        - Visual Question Answering (VQA): User prompt is required in the form of a question
        - Phrase Grounding: User prompt is optional (uses default prompt if not provided)

    Example:
        ```python
        from vi.inference.loaders import ViLoader
        from vi.inference.predictors import Qwen25VLPredictor

        # Load Qwen2.5-VL model and create predictor
        loader = ViLoader.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
        predictor = Qwen25VLPredictor(loader)

        # Load InternVL 3.5 model and create predictor
        loader = ViLoader.from_pretrained("OpenGVLab/InternVL3.5-8B")
        predictor = Qwen25VLPredictor(loader)

        # Load LLaVA-NeXT model and create predictor
        loader = ViLoader.from_pretrained("llava-hf/llama3-llava-next-8b-hf")
        predictor = Qwen25VLPredictor(loader)

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

    def get_generation_config_class(self) -> type[Qwen25VLGenerationConfig]:
        """Return the generation config class for Qwen2.5-VL models.

        Returns:
            Qwen25VLGenerationConfig class.

        """
        return Qwen25VLGenerationConfig

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

        Uses qwen_vl_utils for Qwen2.5-VL compatible models.

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
