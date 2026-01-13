#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   loader_registry.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK loader registry module.
"""

import importlib
import warnings
from collections.abc import Callable

from vi.inference.feature_status import (
    FeatureStatus,
    LoaderMetadata,
    should_allow_unreleased_features,
)
from vi.inference.loaders.base_loader import BaseLoader

# Loader metadata for lazy loading - maps loader_key to detailed metadata
_LOADER_METADATA: dict[str, LoaderMetadata] = {
    "qwen25vl": LoaderMetadata(
        module="vi.inference.loaders.architectures.qwen25vl",
        class_name="Qwen25VLLoader",
        status=FeatureStatus.STABLE,
    ),
    "cosmosreason1": LoaderMetadata(
        module="vi.inference.loaders.architectures.qwen25vl",
        class_name="Qwen25VLLoader",
        status=FeatureStatus.STABLE,
    ),
    "internvl35": LoaderMetadata(
        module="vi.inference.loaders.architectures.qwen25vl",
        class_name="Qwen25VLLoader",
        status=FeatureStatus.STABLE,
    ),
    "nvila": LoaderMetadata(
        module="vi.inference.loaders.architectures.nvila",
        class_name="NVILALoader",
        status=FeatureStatus.STABLE,
    ),
    "deepseekocr": LoaderMetadata(
        module="vi.inference.loaders.architectures.deepseekocr",
        class_name="DeepSeekOCRLoader",
        status=FeatureStatus.COMING_SOON,
        message="DeepSeekOCR support is coming soon. Expected availability: v0.2.0",
        available_from="v0.2.0",
    ),
    "llavanext": LoaderMetadata(
        module="vi.inference.loaders.architectures.qwen25vl",
        class_name="Qwen25VLLoader",
        status=FeatureStatus.COMING_SOON,
        message="LLaVA-NeXT support is coming soon. Expected availability: v0.2.0",
        available_from="v0.2.0",
    ),
}

# Model type to loader key mapping (for auto-detection)
_MODEL_TYPE_TO_LOADER: dict[str, str] = {
    "qwen2_5_vl": "qwen25vl",
    "internvl": "internvl35",
    "nvila": "nvila",
    "deepseek_vl_v2": "deepseekocr",
    "llava_next": "llavanext",
}

# Architecture to loader key mapping (for auto-detection)
_ARCHITECTURE_TO_LOADER: dict[str, str] = {
    "Qwen2_5_VLForConditionalGeneration": "qwen25vl",
    "InternVLForConditionalGeneration": "internvl35",
    "NVILALiteForConditionalGeneration": "nvila",
    "DeepseekOCRForCausalLM": "deepseekocr",
    "LlavaNextForConditionalGeneration": "llavanext",
}


class LoaderRegistry:
    """Registry for model loaders with plugin-style architecture.

    Allows registration and retrieval of model-specific loaders without tight
    coupling to specific implementations. New model loaders can be added by
    decorating classes with @LoaderRegistry.register().

    Supports lazy loading - loaders are only imported when actually needed,
    preventing unnecessary dependency checks at import time.

    Follows HuggingFace Transformers convention for feature maturity tracking,
    with support for experimental, preview, and coming soon features.

    Example:
        ```python
        from vi.inference.loaders import BaseLoader, LoaderRegistry


        @LoaderRegistry.register(
            loader_key="my_model",
            model_types=["my_model_type"],
            architectures=["MyModelForVision"],
        )
        class MyModelLoader(BaseLoader):
            def __init__(self, model_meta, **kwargs):
                # Model-specific loading logic
                pass
        ```

    """

    _registry: dict[str, type[BaseLoader]] = {}
    _model_type_mapping: dict[str, str] = {}
    _architecture_mapping: dict[str, str] = {}

    @classmethod
    def register(
        cls,
        loader_key: str,
        model_types: list[str] | None = None,
        architectures: list[str] | None = None,
    ) -> Callable[[type[BaseLoader]], type[BaseLoader]]:
        """Register a model loader.

        Registers a loader class with the registry, associating it with specific
        model types and architectures for automatic detection.

        Args:
            loader_key: Unique identifier for this loader (e.g., "qwen25vl").
            model_types: List of model_type values from config.json that this
                loader handles (e.g., ["qwen2_5_vl"]).
            architectures: List of architecture names from config.json that this
                loader handles (e.g., ["Qwen2_5_VLForConditionalGeneration"]).

        Returns:
            Decorator function that registers the class and returns it unchanged.

        Example:
            ```python
            @LoaderRegistry.register(
                loader_key="qwen25vl",
                model_types=["qwen2_5_vl"],
                architectures=["Qwen2_5_VLForConditionalGeneration"],
            )
            class Qwen25VLLoader(BaseLoader):
                pass
            ```

        """

        def decorator(loader_class: type[BaseLoader]) -> type[BaseLoader]:
            # Register the loader
            cls._registry[loader_key] = loader_class

            # Map model types to loader key
            if model_types:
                for model_type in model_types:
                    cls._model_type_mapping[model_type] = loader_key

            # Map architectures to loader key
            if architectures:
                for arch in architectures:
                    cls._architecture_mapping[arch] = loader_key

            return loader_class

        return decorator

    @classmethod
    def _check_feature_status(cls, loader_key: str, metadata: LoaderMetadata) -> None:
        """Check feature status and issue appropriate warnings or errors.

        Following HuggingFace Transformers convention.

        Args:
            loader_key: The loader key being accessed.
            metadata: Metadata for the loader.

        Raises:
            NotImplementedError: If feature is coming soon and not enabled via env var.
            DeprecationWarning: If feature is deprecated.

        """
        status = metadata.status
        message = metadata.message

        if status == FeatureStatus.EXPERIMENTAL:
            warnings.warn(
                f"Loader '{loader_key}' is experimental and may change in future versions. "
                f"{message or 'Use with caution in production environments.'}",
                UserWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.PREVIEW:
            warnings.warn(
                f"Loader '{loader_key}' is in preview. "
                f"{message or 'The API may change in upcoming releases.'}",
                FutureWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.COMING_SOON:
            # Check if unreleased features are enabled
            if not should_allow_unreleased_features():
                error_msg = (
                    f"Loader '{loader_key}' is not yet available for public use."
                )
                if message:
                    error_msg = f"{error_msg} {message}"
                else:
                    available_from = metadata.available_from or "TBA"
                    error_msg = (
                        f"{error_msg} Expected availability: {available_from}. "
                        "Stay tuned for updates!"
                    )
                error_msg += (
                    "\n\nFor internal testing, set environment variable: "
                    "VI_ENABLE_UNRELEASED_FEATURES=1"
                )
                raise NotImplementedError(error_msg)

            # Warn if feature is used with override
            warnings.warn(
                f"Loader '{loader_key}' is not yet released. "
                "You are using it with VI_ENABLE_UNRELEASED_FEATURES enabled. "
                "This feature may be incomplete or unstable.",
                UserWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.DEPRECATED:
            deprecated_in = metadata.deprecated_in or "unknown"
            removed_in = metadata.removed_in or "a future version"
            warnings.warn(
                f"Loader '{loader_key}' is deprecated since {deprecated_in} "
                f"and will be removed in {removed_in}. "
                f"{message or 'Please migrate to an alternative loader.'}",
                DeprecationWarning,
                stacklevel=4,
            )

    @classmethod
    def _lazy_import_loader(cls, loader_key: str) -> type[BaseLoader]:
        """Lazily import a loader class by key.

        Args:
            loader_key: The loader key to import.

        Returns:
            The loader class.

        Raises:
            ValueError: If the loader key is unknown.
            NotImplementedError: If the loader is marked as coming soon
                and unreleased features are not enabled.

        """
        if loader_key not in _LOADER_METADATA:
            raise ValueError(
                f"Unknown loader: '{loader_key}'. "
                f"Available loaders: {cls.list_loaders()}"
            )

        metadata = _LOADER_METADATA[loader_key]

        # Check feature status and issue warnings/errors
        cls._check_feature_status(loader_key, metadata)

        # Import the loader
        module_path = metadata.module
        class_name = metadata.class_name
        module = importlib.import_module(module_path)
        loader_class = getattr(module, class_name)

        # Cache in registry for subsequent calls
        cls._registry[loader_key] = loader_class

        return loader_class

    @classmethod
    def get_loader(
        cls,
        loader_key: str | None = None,
        model_type: str | None = None,
        architecture: str | None = None,
    ) -> type[BaseLoader]:
        """Get a loader class by key, model type, or architecture.

        Retrieves the appropriate loader class based on the provided identifier.
        Useful for both explicit loader selection and automatic detection.
        Loaders are imported lazily only when requested.

        Args:
            loader_key: Direct loader key (e.g., "qwen25vl").
            model_type: Model type from config.json (e.g., "qwen2_5_vl").
            architecture: Architecture name from config.json (e.g.,
                "Qwen2_5_VLForConditionalGeneration").

        Returns:
            Loader class that can be instantiated with model metadata.

        Raises:
            ValueError: If no arguments provided, multiple arguments provided,
                or if the specified loader/model/architecture is not found.

        Example:
            ```python
            # Get by loader key
            loader_class = LoaderRegistry.get_loader(loader_key="qwen25vl")

            # Get by model type
            loader_class = LoaderRegistry.get_loader(model_type="qwen2_5_vl")

            # Get by architecture
            loader_class = LoaderRegistry.get_loader(
                architecture="Qwen2_5_VLForConditionalGeneration"
            )
            ```

        """
        # Count how many arguments were provided
        args_provided = sum(
            x is not None for x in [loader_key, model_type, architecture]
        )

        if args_provided == 0:
            raise ValueError(
                "Must provide one of: loader_key, model_type, or architecture"
            )

        if args_provided > 1:
            raise ValueError(
                "Provide only one of: loader_key, model_type, or architecture"
            )

        # Resolve to loader_key
        if model_type:
            if model_type not in _MODEL_TYPE_TO_LOADER:
                raise ValueError(
                    f"No loader registered for model_type '{model_type}'. "
                    f"Supported model types: {cls.list_model_types()}"
                )
            loader_key = _MODEL_TYPE_TO_LOADER[model_type]

        if architecture:
            if architecture not in _ARCHITECTURE_TO_LOADER:
                raise ValueError(
                    f"No loader registered for architecture '{architecture}'. "
                    f"Supported architectures: {cls.list_architectures()}"
                )
            loader_key = _ARCHITECTURE_TO_LOADER[architecture]

        # Get from cache or lazy import
        if loader_key in cls._registry:
            return cls._registry[loader_key]

        return cls._lazy_import_loader(loader_key)

    @classmethod
    def list_loaders(cls, include_unreleased: bool = False) -> list[str]:
        """List all registered loader keys.

        Args:
            include_unreleased: If True, include coming soon and preview loaders.
                Defaults to False.

        Returns:
            List of loader keys that can be used with get_loader().

        Example:
            ```python
            # List stable loaders only
            available = LoaderRegistry.list_loaders()
            print(f"Available loaders: {available}")

            # List all loaders including unreleased
            all_loaders = LoaderRegistry.list_loaders(include_unreleased=True)
            ```

        """
        # Include both registered and metadata-defined loaders
        all_loaders = set(cls._registry.keys()) | set(_LOADER_METADATA.keys())

        if not include_unreleased:
            # Exclude coming soon and preview loaders
            all_loaders = {
                key
                for key in all_loaders
                if key not in _LOADER_METADATA
                or _LOADER_METADATA[key].status
                not in (FeatureStatus.COMING_SOON, FeatureStatus.PREVIEW)
            }

        return sorted(all_loaders)

    @classmethod
    def list_loaders_by_status(cls, status: FeatureStatus) -> list[str]:
        """List loaders filtered by feature status.

        Args:
            status: Feature status to filter by.

        Returns:
            List of loader keys with the specified status.

        Example:
            ```python
            from vi.inference.feature_status import FeatureStatus

            # List experimental loaders
            experimental = LoaderRegistry.list_loaders_by_status(
                FeatureStatus.EXPERIMENTAL
            )

            # List coming soon loaders
            coming_soon = LoaderRegistry.list_loaders_by_status(
                FeatureStatus.COMING_SOON
            )
            ```

        """
        return sorted(
            [
                key
                for key, metadata in _LOADER_METADATA.items()
                if metadata.status == status
            ]
        )

    @classmethod
    def get_loader_status(cls, loader_key: str) -> FeatureStatus:
        """Get the feature status of a loader.

        Args:
            loader_key: The loader key to check.

        Returns:
            Feature status of the loader.

        Raises:
            ValueError: If the loader key is unknown.

        Example:
            ```python
            from vi.inference.loaders import LoaderRegistry

            status = LoaderRegistry.get_loader_status("deepseekocr")
            print(status)  # FeatureStatus.COMING_SOON
            ```

        """
        if loader_key not in _LOADER_METADATA:
            raise ValueError(
                f"Unknown loader: '{loader_key}'. "
                f"Available loaders: {cls.list_loaders(include_unreleased=True)}"
            )

        return _LOADER_METADATA[loader_key].status

    @classmethod
    def list_model_types(cls) -> list[str]:
        """List all supported model types from config.json.

        Returns:
            List of model_type values that can be automatically detected.

        Example:
            ```python
            types = LoaderRegistry.list_model_types()
            print(f"Supported model types: {types}")
            # Output: Supported model types: ['qwen2_5_vl', 'nvila', ...]
            ```

        """
        # Include both registered and predefined mappings
        all_types = set(cls._model_type_mapping.keys()) | set(
            _MODEL_TYPE_TO_LOADER.keys()
        )
        return sorted(all_types)

    @classmethod
    def list_architectures(cls) -> list[str]:
        """List all supported architecture names from config.json.

        Returns:
            List of architecture names that can be automatically detected.

        Example:
            ```python
            archs = LoaderRegistry.list_architectures()
            print(f"Supported architectures: {archs}")
            # Output: ['Qwen2_5_VLForConditionalGeneration', ...]
            ```

        """
        # Include both registered and predefined mappings
        all_archs = set(cls._architecture_mapping.keys()) | set(
            _ARCHITECTURE_TO_LOADER.keys()
        )
        return sorted(all_archs)

    @classmethod
    def is_registered(
        cls,
        loader_key: str | None = None,
        model_type: str | None = None,
        architecture: str | None = None,
    ) -> bool:
        """Check if a loader is registered for the given identifier.

        Args:
            loader_key: Loader key to check.
            model_type: Model type to check.
            architecture: Architecture name to check.

        Returns:
            True if a loader is registered, False otherwise.

        Example:
            ```python
            if LoaderRegistry.is_registered(model_type="qwen2_5_vl"):
                print("Qwen2.5-VL is supported")
            ```

        """
        if loader_key:
            return loader_key in cls._registry or loader_key in _LOADER_METADATA
        if model_type:
            return (
                model_type in cls._model_type_mapping
                or model_type in _MODEL_TYPE_TO_LOADER
            )
        if architecture:
            return (
                architecture in cls._architecture_mapping
                or architecture in _ARCHITECTURE_TO_LOADER
            )
        return False

    @classmethod
    def get_loader_key(cls, loader_class: type[BaseLoader]) -> str | None:
        """Get the loader key for a given loader class.

        Args:
            loader_class: The loader class to look up.

        Returns:
            The loader key if found, None otherwise.

        Example:
            ```python
            from vi.inference.loaders import Qwen25VLLoader

            key = LoaderRegistry.get_loader_key(Qwen25VLLoader)
            print(key)  # Output: "qwen25vl"
            ```

        """
        # Check registered loaders first
        for key, registered_class in cls._registry.items():
            if registered_class == loader_class:
                return key

        # Check metadata for lazy-loaded loaders by class name
        class_name = loader_class.__name__
        for key, metadata in _LOADER_METADATA.items():
            if metadata.class_name == class_name:
                return key

        return None
