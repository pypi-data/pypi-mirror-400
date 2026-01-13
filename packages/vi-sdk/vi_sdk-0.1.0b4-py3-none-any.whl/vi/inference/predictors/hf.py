#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   hf.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK base HuggingFace predictor module with shared logic.
"""

from abc import abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Generic, TypeVar

import msgspec
import torch
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.logits_processors import (
    ConditionalXGrammarLogitsProcessor,
    DebugXGrammarLogitsProcessor,
)
from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.predictors.streaming import StreamingMixin
from vi.inference.task_types import PredictionResponse, TaskAssistant, consts
from vi.inference.utils.compiler import compile_bounded_grammar
from vi.inference.utils.postprocessing import parse_result

if TYPE_CHECKING:
    import xgrammar as xgr

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1  # type: ignore[attr-defined]

# Generic type for generation config
GenerationConfigType = TypeVar("GenerationConfigType")


class HFPredictor(BasePredictor, StreamingMixin, Generic[GenerationConfigType]):
    """Base class for HuggingFace model predictors with shared logic.

    This class extracts common functionality across HuggingFace model predictors
    to reduce code duplication and improve maintainability. It handles:
    - Loader validation (processor, compiler, metadata)
    - Schema and prompt initialization
    - Grammar pre-compilation
    - Generation config handling (dict conversion, CoT mode, etc.)
    - Message preparation
    - Logits processor setup
    - Input preprocessing
    - Seed management
    - Streaming and non-streaming generation
    - Output decoding and stop string handling

    Subclasses only need to:
    1. Define their specific GenerationConfig type
    2. Implement get_generation_config_class() to return the config class
    3. Implement _prepare_inputs() for model-specific input preprocessing
    4. Optionally override validation methods for custom error handling

    """

    _loader: BaseLoader
    _schema: TaskAssistant
    _user_prompt: str | None
    _compiled_grammar: "xgr.CompiledGrammar | None"

    def __init__(self, loader: BaseLoader):
        """Initialize the HuggingFace predictor.

        Sets up the predictor with a loaded model and configures the task-specific
        schema and prompts based on the model's training task type.

        Args:
            loader: Loaded model instance. Must contain:
                - model: The loaded model
                - processor: Tokenizer and image processor
                - compiler: xgrammar compiler for structured outputs
                - metadata: Including task_type and system_prompt

        Raises:
            ImportError: If required dependencies are not installed.
            AttributeError: If the loader doesn't contain processor or compiler.
            KeyError: If required metadata fields are missing.

        """
        self._loader = loader

        # Validate loader has required components
        self._validate_processor()
        self._validate_compiler()
        self._validate_metadata()

        # Setup task-specific schema and prompts
        self._schema = consts.TASK_TYPE_TO_ASSISTANT_MAP[
            consts.TaskType(self._loader.metadata["task_type"])
        ]
        self._user_prompt = consts.TASK_TYPE_TO_USER_PROMPT_MAP[
            consts.TaskType(self._loader.metadata["task_type"])
        ]

        # Pre-compile grammar once for reuse across inference calls
        # This avoids expensive grammar compilation on every __call__
        if self._schema and self._loader.compiler:
            self._compiled_grammar = compile_bounded_grammar(
                self._loader.compiler, self._schema
            )
        else:
            self._compiled_grammar = None

    @abstractmethod
    def get_generation_config_class(self) -> type[GenerationConfigType]:
        """Return the generation config class for this predictor.

        Returns:
            The generation config class (e.g., Qwen25VLGenerationConfig, NVILAGenerationConfig).

        """

    def _validate_processor(self) -> None:
        """Validate that loader has a processor.

        Raises:
            AttributeError: If processor is missing or None.

        """
        if not hasattr(self._loader, "processor") or self._loader.processor is None:
            raise AttributeError(
                "Predictor requires a loader with a processor. "
                "The provided loader may not be properly configured."
            )

    def _validate_compiler(self) -> None:
        """Validate that loader has a compiler.

        Raises:
            AttributeError: If compiler is missing or None.

        """
        if not hasattr(self._loader, "compiler") or self._loader.compiler is None:
            raise AttributeError(
                "Predictor requires a loader with an xgrammar compiler. "
                "This predictor is designed for Datature Vi fine-tuned models."
            )

    def _validate_metadata(self) -> None:
        """Validate that loader metadata has required fields.

        Raises:
            KeyError: If required metadata fields are missing.

        """
        if "task_type" not in self._loader.metadata:
            raise KeyError(
                "Loader metadata missing 'task_type'. This predictor requires a "
                "Datature Vi fine-tuned model with task type configuration."
            )

    def _parse_result(self, raw_output: str, user_prompt: str) -> PredictionResponse:
        """Parse generated output into appropriate response type.

        Wrapper around the shared parse_result utility function.

        Args:
            raw_output: Raw model output (may contain COT tags or code blocks).
            user_prompt: The user prompt used for inference.

        Returns:
            Parsed prediction response based on task type.

        """
        task_type = consts.TaskType(self._loader.metadata["task_type"])
        return parse_result(
            raw_output=raw_output,
            user_prompt=user_prompt,
            task_type=task_type,
            schema=self._schema,
        )

    def _prepare_generation_config(
        self,
        generation_config: GenerationConfigType | dict | None,
        cot: bool,
    ) -> tuple[GenerationConfigType, bool]:
        """Prepare generation config from input.

        Handles dict conversion, loader config fallback, and CoT mode adjustments.

        Args:
            generation_config: User-provided generation config (dict, config object, or None).
            cot: Whether CoT mode is enabled.

        Returns:
            Tuple of (prepared generation config, whether user explicitly set max_new_tokens).

        """
        config_class = self.get_generation_config_class()
        user_set_max_tokens = False

        if isinstance(generation_config, dict):
            user_set_max_tokens = "max_new_tokens" in generation_config
            generation_config = config_class(**generation_config)

        elif not generation_config:
            loader_config = self._loader.generation_config
            if loader_config:
                generation_config = config_class(
                    **msgspec.structs.asdict(loader_config)
                )
            else:
                generation_config = config_class()

        else:
            # User passed a config object - assume they may have set max_new_tokens
            user_set_max_tokens = True

        generation_config.do_sample = False

        # Increase max_new_tokens for CoT mode if user didn't explicitly set it
        # CoT requires more tokens for reasoning
        if cot and not user_set_max_tokens:
            generation_config.max_new_tokens = 4096

        return generation_config, user_set_max_tokens

    def _prepare_logits_processors(
        self,
        cot: bool,
    ) -> list:
        """Prepare logits processors for generation.

        Args:
            cot: Whether to use ConditionalXGrammarLogitsProcessor (True) or
                DebugXGrammarLogitsProcessor (False).

        Returns:
            List of logits processors.

        """
        if not self._compiled_grammar:
            return []

        if cot:
            xgr_logits_processor = (
                ConditionalXGrammarLogitsProcessor.from_compiled_grammar(
                    self._compiled_grammar,
                    self._loader.processor.tokenizer,
                )
            )
        else:
            xgr_logits_processor = DebugXGrammarLogitsProcessor.from_compiled_grammar(
                self._compiled_grammar,
                self._loader.processor.tokenizer,
            )

        return [xgr_logits_processor]

    @abstractmethod
    def _prepare_inputs(
        self,
        source: str,
        effective_prompt: str,
        system_prompt: str,
    ) -> dict:
        """Prepare model inputs from image source and prompts.

        This method is model-specific and must be implemented by subclasses
        to handle different input preprocessing formats.

        Args:
            source: Path to image file.
            effective_prompt: User prompt to use.
            system_prompt: System prompt (may include CoT suffix).

        Returns:
            Dictionary of model inputs ready for generation.

        """

    def _apply_seed(self, seed: int) -> None:
        """Apply random seed for reproducibility.

        Args:
            seed: Random seed. If -1, no seed is applied (random generation).

        """
        if seed != -1:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

    def _decode_output(
        self,
        generated_ids: torch.Tensor,
        input_length: int,
        stop_strings: list[str] | None,
    ) -> str:
        """Decode model output and strip stop strings.

        Args:
            generated_ids: Generated token IDs from model.
            input_length: Length of input tokens to skip.
            stop_strings: Optional list of stop strings to strip from end.

        Returns:
            Decoded text with stop strings removed.

        """
        output_ids = generated_ids[:, input_length:]
        result_text = self._loader.processor.tokenizer.decode(
            output_ids[0], skip_special_tokens=True
        )

        # Strip stop strings if present
        if stop_strings:
            for stop_string in stop_strings:
                if result_text.endswith(stop_string):
                    result_text = result_text[: -len(stop_string)]
                    break

        return result_text

    def __call__(
        self,
        source: str,
        user_prompt: str | None = None,
        generation_config: GenerationConfigType | dict | None = None,
        stream: bool = False,
        cot: bool = False,
    ) -> PredictionResponse | Generator[str, None, PredictionResponse]:
        """Run inference on an image using a HuggingFace model.

        Processes an image and optional user prompt to generate predictions
        based on the model's training task (VQA, phrase grounding, etc.).

        Token generation is guided by xgrammar logits processors to coax the
        model toward valid structured output. Final validation is performed
        once after all tokens are generated. If validation fails, returns
        GenericResponse instead of raising an error.

        Args:
            source: Path to the image file to analyze.
            user_prompt: Optional custom prompt to override the default task
                prompt. If None, uses the task-specific prompt from training.
            generation_config: Generation configuration.
                If None, uses the generation config from the loader.
            stream: If True, returns a generator that yields tokens (as strings) as they're
                generated in real-time. The generator also returns the final PredictionResponse
                when complete. If False, waits for complete generation and returns
                the parsed PredictionResponse. Defaults to False.
            cot: If True, enables chain-of-thought mode using ConditionalXGrammarLogitsProcessor,
                which enforces <think>...</think> and <answer>...</answer> tags in the output.
                When enabled without explicitly setting max_new_tokens, automatically increases
                to 4096 (from default 1024) to accommodate reasoning tokens. Defaults to False.

        Returns:
            If stream=False: Task-specific prediction results.
            If stream=True: A generator that yields strings (tokens) as they're generated.

        Raises:
            FileNotFoundError: If the image file doesn't exist.
            ValueError: If the image format is not supported.
            RuntimeError: If model inference fails.
            ImportError: If required dependencies are not installed.

        """
        # Use provided prompt or fall back to default task prompt
        effective_prompt = user_prompt if user_prompt else self._user_prompt

        # Prepare generation config
        generation_config, _ = self._prepare_generation_config(generation_config, cot)

        # Validate required components are present
        if self._loader.compiler is None:
            raise RuntimeError(
                "Compiler not available for structured output generation"
            )

        if self._loader.processor is None:
            raise RuntimeError("Processor not available for input preprocessing")

        # Build system prompt, adding COT format instruction if enabled
        system_prompt = self._loader.metadata["system_prompt"]
        if cot:
            system_prompt = f"{system_prompt}{consts.COT_SYSTEM_PROMPT_SUFFIX}"

        # Prepare logits processors
        logits_processor = self._prepare_logits_processors(cot)

        # Prepare model inputs
        inputs = self._prepare_inputs(source, effective_prompt, system_prompt)

        # Configure generation
        generation_config.logits_processor = logits_processor
        generation_config.pad_token_id = self._loader.processor.tokenizer.eos_token_id

        # Apply seed for reproducibility
        self._apply_seed(generation_config.seed)

        # Streaming generation
        if stream:
            return self._stream_generator(
                loader=self._loader,
                inputs=inputs,
                generation_config=generation_config,
                user_prompt=effective_prompt or "",
                parse_result_fn=self._parse_result,
            )

        # Non-streaming: use streaming internally but return final output only
        # This generates tokens incrementally while displaying the complete result
        gen = self._stream_generator(
            loader=self._loader,
            inputs=inputs,
            generation_config=generation_config,
            user_prompt=effective_prompt or "",
            parse_result_fn=self._parse_result,
        )

        # Consume all tokens from the generator
        try:
            while True:
                next(gen)
        except StopIteration as e:
            # The return value from the generator is stored in e.value
            return e.value
