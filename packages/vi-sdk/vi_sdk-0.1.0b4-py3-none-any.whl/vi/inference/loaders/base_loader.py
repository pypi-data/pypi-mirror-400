#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   base_loader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK base loader module.
"""

import json
from abc import ABC
from typing import Any

import msgspec
from vi.api.resources.flows.responses import FlowSpec
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.config.base_config import ViGenerationConfig
from vi.inference.task_types.consts import TASK_TYPE_TO_SYSTEM_PROMPT_MAP, TaskType


class BaseLoader(ABC):
    """Base class for model loaders with common interface.

    Abstract base class defining the interface for loading models from various
    sources. Provides a common structure for model loader implementations to
    ensure consistent behavior across different model types.

    Attributes:
        model: The loaded model instance.
        processor: The processor for input preprocessing (optional).
        compiler: The compiler for structured outputs (optional).
        metadata: Dictionary containing model metadata.

    """

    _model: Any
    _processor: Any | None = None
    _compiler: Any | None = None
    _generation_config: ViGenerationConfig | None = None
    _generation_config_class: type[ViGenerationConfig] = ViGenerationConfig
    _metadata: dict[str, Any]

    def __init__(self) -> None:
        """Initialize base loader with empty metadata dictionary."""
        self._metadata = {}

    @property
    def model(self) -> Any:
        """Get the loaded model instance."""
        return self._model

    @property
    def processor(self) -> Any | None:
        """Get the model processor for input preprocessing, if available."""
        return self._processor

    @property
    def compiler(self) -> Any | None:
        """Get the compiler for structured output generation, if available."""
        return self._compiler

    @property
    def generation_config(self) -> ViGenerationConfig | None:
        """Get the generation config."""
        return self._generation_config

    @property
    def metadata(self) -> dict[str, Any]:
        """Get model metadata."""
        return self._metadata

    def _load_generation_config_from_run_json(
        self, model_meta: ModelDownloadResult
    ) -> None:
        """Load generation config from run.json."""
        if not model_meta.run_config_path:
            return

        with open(model_meta.run_config_path, encoding="utf-8") as f:
            config_data = json.loads(f.read())
            flow_spec = msgspec.convert(config_data["spec"]["flow"], type=FlowSpec)

            model_block = next(
                (block for block in flow_spec.blocks if "model" in block.block),
                None,
            )
            if model_block:
                self._generation_config = msgspec.convert(
                    model_block.settings["evaluation"],
                    type=self._generation_config_class,
                )

    def _load_metadata_from_run_json(self, model_meta: ModelDownloadResult) -> None:
        """Load Datature Vi training metadata from run.json.

        Args:
            model_meta: Model metadata containing path to run.json.

        Raises:
            FileNotFoundError: If run.json doesn't exist.
            ValueError: If configuration format is invalid.

        """
        if not model_meta.run_config_path:
            self._metadata["task_type"] = "generic"
            self._metadata["system_prompt"] = ""
            return

        with open(model_meta.run_config_path, encoding="utf-8") as f:
            config_data = json.loads(f.read())
            flow_spec = msgspec.convert(config_data["spec"]["flow"], type=FlowSpec)

            # Extract task type first (needed for default system prompt)
            task_type = None
            dataset_block = next(
                (block for block in flow_spec.blocks if "dataset" in block.block),
                None,
            )
            if dataset_block:
                task_type = dataset_block.settings["projectKind"]
                self._metadata["task_type"] = task_type

            # Extract system prompt
            system_prompt_block = next(
                (block for block in flow_spec.blocks if "system-prompt" in block.block),
                None,
            )
            if system_prompt_block:
                self._metadata["system_prompt"] = system_prompt_block.settings[
                    "systemPrompt"
                ]
            else:
                # Use default system prompt based on task type
                default_prompt = self._get_default_system_prompt(task_type)
                self._metadata["system_prompt"] = default_prompt

            # Extract model configuration
            model_block = next(
                (block for block in flow_spec.blocks if "model" in block.block),
                None,
            )
            if model_block:
                self._metadata["model_name"] = model_block.settings["architecture"][
                    "name"
                ]
                self._metadata["model_size"] = model_block.settings["architecture"][
                    "size"
                ]

                self._metadata["quantization_enabled"] = model_block.settings[
                    "quantization"
                ]["enabled"]

                self._metadata["quantization_type"] = str(
                    model_block.settings["quantization"].get("type", "nf4")
                ).lower()

                # Parse compute precision
                self._metadata["compute_precision_type"] = str(
                    model_block.settings["compute"].get("precisionType", "bfloat16")
                ).lower()

    def _get_default_system_prompt(self, task_type: str | None) -> str:
        """Get default system prompt based on task type.

        Args:
            task_type: The task type string (e.g., "phrase-grounding", "vqa").

        Returns:
            Default system prompt string, or empty string if no default exists.

        """
        if not task_type:
            return ""

        try:
            task_enum = TaskType(task_type)
            default_prompt = TASK_TYPE_TO_SYSTEM_PROMPT_MAP.get(task_enum)
            return default_prompt if default_prompt else ""
        except (ValueError, KeyError):
            return ""
