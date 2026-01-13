#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   vi_loader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK auto loader module.
"""

import json
from pathlib import Path
from typing import Any

import msgspec
from vi.api.resources.flows.responses import FlowSpec
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.loaders.loader_registry import LoaderRegistry


class _ViLoaderFactory:
    """Factory for automatically loading models based on architecture detection.

    Detects model architecture from configuration files and automatically selects
    the appropriate loader. Supports HuggingFace models, local models, and
    Datature Vi fine-tuned models.

    !!! note "Recommended Usage"
        For most use cases, prefer using `ViModel` which handles client initialization
        and model downloading automatically:

        ```python
        from vi.inference import ViModel

        # Recommended: Use ViModel for Datature Vi models
        model = ViModel(
            secret_key="your-secret-key",
            organization_id="your-organization-id",
            run_id="your-run-id",
        )
        ```

    Detection Strategy:
        1. Check run.json for Datature Vi models (if present)
        2. Check config.json for model_type field
        3. Check config.json for architectures field
        4. Attempt pattern matching on model path/name
        5. Raise error if detection fails

    Example:
        ```python
        from vi.inference.loaders import ViLoader

        # Load Datature model from metadata
        model_meta = client.get_model(run_id="my-run")
        loader = ViLoader(model_meta=model_meta)

        # Load from local path (auto-detect)
        loader = ViLoader(pretrained_model_name_or_path="./my_model")

        # Load from HuggingFace (auto-detect)
        loader = ViLoader(pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct")

        # Load with explicit loader selection
        loader = ViLoader(
            pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct",
            loader_key="qwen25vl",
        )

        # Alternative explicit methods (still available)
        loader = ViLoader.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
        loader = ViLoader.from_model_meta(model_meta)
        ```

    Note:
        This factory supports both HuggingFace-compatible models and custom
        non-HuggingFace models. For non-HuggingFace models, implement a custom
        loader and register it with LoaderRegistry.

    """

    def __call__(
        self,
        model_meta: ModelDownloadResult | None = None,
        pretrained_model_name_or_path: str | None = None,
        loader_key: str | None = None,
        **kwargs: Any,
    ) -> BaseLoader:
        """Create a loader instance with automatic architecture detection.

        This is the primary way to create loaders. Supports both HuggingFace models
        and Datature Vi fine-tuned models with automatic architecture detection.

        Args:
            model_meta: Model metadata containing paths and configuration.
                Use this for Datature Vi fine-tuned models.
            pretrained_model_name_or_path: Model identifier or path. Can be:
                - HuggingFace model name (e.g., "Qwen/Qwen2.5-VL-7B-Instruct")
                - Local directory path containing model files
                - Any path with standard HuggingFace structure (config.json, etc.)
            loader_key: Optional explicit loader to use (e.g., "qwen25vl").
                If provided, skips automatic detection.
            **kwargs: Additional arguments passed to the loader:
                - attn_implementation: Attention implementation ("eager",
                  "flash_attention_2", "sdpa")
                - device_map: Device mapping ("auto", "cpu", "cuda", or dict)
                - low_cpu_mem_usage: Use low CPU memory mode (bool)
                - trust_remote_code: Trust remote code (bool)
                - max_threads: Max threads for operations (int)

        Returns:
            Loaded model instance ready for inference.

        Raises:
            ValueError: If neither model_meta nor pretrained_model_name_or_path is provided,
                or if model architecture cannot be detected or is not supported.
            FileNotFoundError: If local model path doesn't exist.
            ImportError: If required dependencies for the model are not installed.

        Example:
            ```python
            # Load from HuggingFace (auto-detect)
            loader = ViLoader(
                pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct"
            )

            # Load from local path (auto-detect)
            loader = ViLoader(pretrained_model_name_or_path="./my_model")

            # Load with explicit loader selection
            loader = ViLoader(
                pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct",
                loader_key="qwen25vl",
                trust_remote_code=True,
                device_map="auto",
            )

            # Load Datature model from metadata
            model_meta = client.get_model(run_id="my-run")
            loader = ViLoader(model_meta=model_meta)

            # Access loaded components
            print(f"Model: {loader.model}")
            print(f"Metadata: {loader.metadata}")
            ```

        Note:
            For HuggingFace models that aren't cached locally, the first call
            will download the model. Subsequent calls will use the cached version.

        """
        if model_meta and not pretrained_model_name_or_path:
            return self.from_model_meta(
                model_meta=model_meta,
                loader_key=loader_key,
                **kwargs,
            )

        if pretrained_model_name_or_path and not model_meta:
            return self.from_pretrained(
                pretrained_model_name_or_path=pretrained_model_name_or_path,
                loader_key=loader_key,
                **kwargs,
            )

        raise ValueError(
            "Either model_meta or pretrained_model_name_or_path must be provided"
        )

    def from_pretrained(
        self,
        pretrained_model_name_or_path: str,
        loader_key: str | None = None,
        **kwargs: Any,
    ) -> BaseLoader:
        """Load a model from pretrained path with automatic architecture detection.

        Args:
            pretrained_model_name_or_path: Model identifier or path. Can be:
                - HuggingFace model name (e.g., "Qwen/Qwen2.5-VL-7B-Instruct")
                - Local directory path containing model files
                - Any path with standard HuggingFace structure (config.json, etc.)
            loader_key: Optional explicit loader to use (e.g., "qwen25vl").
                If provided, skips automatic detection.
            **kwargs: Additional arguments passed to the loader:
                - attn_implementation: Attention implementation
                  ("eager", "flash_attention_2", "sdpa")
                - device_map: Device mapping ("auto", "cpu", "cuda", or dict)
                - low_cpu_mem_usage: Use low CPU memory mode (bool)
                - trust_remote_code: Trust remote code (bool)
                - max_threads: Max threads for operations (int)

        Returns:
            Loaded model instance ready for inference.

        Raises:
            ValueError: If model architecture cannot be detected or is not supported.
            FileNotFoundError: If local model path doesn't exist.
            ImportError: If required dependencies for the model are not installed.

        Example:
            ```python
            # Auto-detect from HuggingFace
            loader = ViLoader.from_pretrained(
                "Qwen/Qwen2.5-VL-7B-Instruct", trust_remote_code=True, device_map="auto"
            )

            # Auto-detect from local path
            loader = ViLoader.from_pretrained(
                "./models/my_finetuned_qwen", attn_implementation="flash_attention_2"
            )

            # Explicit loader selection
            loader = ViLoader.from_pretrained(
                "Qwen/Qwen2.5-VL-7B-Instruct",
                loader_key="qwen25vl",
                low_cpu_mem_usage=True,
            )

            # Access loaded components
            print(f"Model: {loader.model}")
            print(f"Metadata: {loader.metadata}")
            ```

        Note:
            For HuggingFace models that aren't cached locally, the first call
            will download the model. Subsequent calls will use the cached version.

        """
        model_meta = ModelDownloadResult(
            model_path=pretrained_model_name_or_path,
            adapter_path=None,
            run_config_path=None,
        )
        return self.from_model_meta(
            model_meta=model_meta, loader_key=loader_key, **kwargs
        )

    def from_model_meta(
        self,
        model_meta: ModelDownloadResult,
        loader_key: str | None = None,
        **kwargs: Any,
    ) -> BaseLoader:
        """Load a model from metadata with automatic architecture detection.

        Args:
            model_meta: Model metadata containing:
                - model_path: Path to model directory or HuggingFace identifier
                - adapter_path: Optional path to PEFT adapter
                - run_config_path: Optional path to Datature run.json
            loader_key: Optional explicit loader to use (e.g., "qwen25vl").
                If provided, skips automatic detection.
            **kwargs: Additional arguments passed to the loader.

        Returns:
            Loaded model instance ready for inference.

        Raises:
            ValueError: If model architecture cannot be detected or is not supported.
            FileNotFoundError: If local model files don't exist.
            ImportError: If required dependencies for the model are not installed.

        Example:
            ```python
            from vi.api.resources.models.results import ModelDownloadResult

            # Load Datature fine-tuned model
            model_meta = ModelDownloadResult(
                model_path="./models/run_123/model_full",
                adapter_path="./models/run_123/model_adapter",
                run_config_path="./models/run_123/model_full/run.json",
            )
            loader = ViLoader.from_model_meta(model_meta)

            # Load pretrained model
            model_meta = ModelDownloadResult(
                model_path="Qwen/Qwen2.5-VL-7B-Instruct",
                adapter_path=None,
                run_config_path=None,
            )
            loader = ViLoader.from_model_meta(model_meta, trust_remote_code=True)
            ```

        """
        # Auto-detect loader if not explicitly provided
        if loader_key is None:
            loader_key = self._detect_loader(model_meta)

        # Get loader class from registry
        loader_class = LoaderRegistry.get_loader(loader_key=loader_key)

        # Instantiate and return loader
        # Note: overwrite is used in the download phase, not passed to loader
        return loader_class(model_meta, **kwargs)

    def _detect_loader(self, model_meta: ModelDownloadResult) -> str:
        """Detect appropriate loader from model configuration.

        Detection order:
            1. Check for Datature run.json (highest priority for fine-tuned models)
            2. Check config.json for model_type field
            3. Check config.json for architectures field
            4. Pattern matching on model path/name
            5. Raise error if no match found

        Args:
            model_meta: Model metadata to analyze.

        Returns:
            Loader key (e.g., "qwen25vl") for the detected model architecture.

        Raises:
            ValueError: If model architecture cannot be detected.
            FileNotFoundError: If config files are missing.

        """
        # Strategy 1: Check for Datature run.json
        if model_meta.run_config_path and Path(model_meta.run_config_path).exists():
            try:
                loader_key = self._detect_from_datature_config(model_meta)
                if loader_key:
                    return loader_key
            except Exception:  # noqa: S110
                pass  # Fall through to other detection methods

        # Strategy 2: Check standard config.json
        config_path = Path(model_meta.model_path) / "config.json"

        # For HuggingFace Hub models, config might not exist locally yet
        # In that case, try pattern matching on the model name
        if not config_path.exists():
            loader_key = self._detect_from_model_name(model_meta.model_path)
            if loader_key:
                return loader_key

            raise ValueError(
                f"Could not find config.json at {config_path} and could not "
                f"detect model type from path '{model_meta.model_path}'. "
                f"For HuggingFace models, this file will be downloaded on first load. "
                f"Please specify loader_key explicitly or ensure the model path is correct."
            )

        # Load and analyze config.json
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.loads(f.read())

            # Strategy 2a: Check model_type field
            model_type = config.get("model_type")
            if model_type:
                if LoaderRegistry.is_registered(model_type=model_type):
                    loader_class = LoaderRegistry.get_loader(model_type=model_type)
                    loader_key = LoaderRegistry.get_loader_key(loader_class)
                    if loader_key:
                        return loader_key

            # Strategy 2b: Check architectures field
            architectures = config.get("architectures", [])
            for arch in architectures:
                if LoaderRegistry.is_registered(architecture=arch):
                    loader_class = LoaderRegistry.get_loader(architecture=arch)
                    loader_key = LoaderRegistry.get_loader_key(loader_class)
                    if loader_key:
                        return loader_key

        except (json.JSONDecodeError, OSError) as e:  # noqa: PERF203
            raise ValueError(
                f"Failed to parse config.json at {config_path}: {e}"
            ) from e

        # Strategy 3: Pattern matching on model path
        loader_key = self._detect_from_model_name(model_meta.model_path)
        if loader_key:
            return loader_key

        # If we get here, detection failed
        raise ValueError(
            f"Could not detect model architecture from {model_meta.model_path}. "
            f"Supported model types: {LoaderRegistry.list_model_types()}. "
            f"Supported architectures: {LoaderRegistry.list_architectures()}. "
            f"Please specify loader_key explicitly using one of: {LoaderRegistry.list_loaders()}"
        )

    def _detect_from_datature_config(
        self, model_meta: ModelDownloadResult
    ) -> str | None:
        """Detect loader from Datature run.json configuration.

        Args:
            model_meta: Model metadata with run_config_path.

        Returns:
            Loader key if detected, None otherwise.

        """
        if not model_meta.run_config_path:
            return None

        try:
            with open(model_meta.run_config_path, encoding="utf-8") as f:
                config = json.loads(f.read())

            flow_spec = msgspec.convert(config["spec"]["flow"], type=FlowSpec)

            model_block = next(
                (block for block in flow_spec.blocks if "model" in block.block),
                None,
            )
            if model_block:
                return model_block.settings["architecture"]["name"]

        except Exception:  # noqa: S110
            pass

        return None

    def _detect_from_model_name(self, model_path: str) -> str | None:
        """Detect loader from model path/name pattern matching.

        Args:
            model_path: Model path or HuggingFace identifier.

        Returns:
            Loader key if detected, None otherwise.

        """
        model_path_lower = model_path.lower()

        # Pattern matching for known models
        if "qwen" in model_path_lower and (
            "vl" in model_path_lower or "2.5" in model_path_lower
        ):
            return "qwen25vl"

        if "nvila" in model_path_lower:
            return "nvila"

        if "deepseek" in model_path_lower and "ocr" in model_path_lower:
            return "deepseekocr"

        return None

    def list_available_loaders(self) -> list[str]:
        """List all available loader keys.

        Returns:
            List of registered loader keys.

        Example:
            ```python
            loaders = ViLoader.list_available_loaders()
            print(f"Available loaders: {loaders}")
            # Output: Available loaders: ['qwen25vl', ...]
            ```

        """
        return LoaderRegistry.list_loaders()

    def list_supported_model_types(self) -> list[str]:
        """List all supported model types from config.json.

        Returns:
            List of model_type values that can be automatically detected.

        Example:
            ```python
            types = ViLoader.list_supported_model_types()
            print(f"Supported model types: {types}")
            # Output: Supported model types: ['qwen2_5_vl', ...]
            ```

        """
        return LoaderRegistry.list_model_types()

    def list_supported_architectures(self) -> list[str]:
        """List all supported architecture names from config.json.

        Returns:
            List of architecture names that can be automatically detected.

        Example:
            ```python
            archs = ViLoader.list_supported_architectures()
            print(f"Supported architectures: {archs}")
            # Output: ['Qwen2_5_VLForConditionalGeneration', ...]
            ```

        """
        return LoaderRegistry.list_architectures()


ViLoader: _ViLoaderFactory = _ViLoaderFactory()
