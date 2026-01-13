#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   predictor_registry.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK predictor registry module.
"""

import importlib
import warnings
from collections.abc import Callable

from vi.inference.feature_status import (
    FeatureStatus,
    PredictorMetadata,
    should_allow_unreleased_features,
)
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.predictors.base_predictor import BasePredictor

# Predictor metadata for lazy loading - maps predictor_key to detailed metadata
_PREDICTOR_METADATA: dict[str, PredictorMetadata] = {
    "qwen25vl": PredictorMetadata(
        module="vi.inference.predictors.architectures.qwen25vl",
        class_name="Qwen25VLPredictor",
        status=FeatureStatus.STABLE,
    ),
    "nvila": PredictorMetadata(
        module="vi.inference.predictors.architectures.nvila",
        class_name="NVILAPredictor",
        status=FeatureStatus.STABLE,
    ),
    "deepseekocr": PredictorMetadata(
        module="vi.inference.predictors.architectures.deepseekocr",
        class_name="DeepSeekOCRPredictor",
        status=FeatureStatus.COMING_SOON,
        message="DeepSeekOCR support is coming soon. Expected availability: v0.2.0",
        available_from="v0.2.0",
    ),
    "llavanext": PredictorMetadata(
        module="vi.inference.predictors.architectures.qwen25vl",
        class_name="Qwen25VLPredictor",
        status=FeatureStatus.COMING_SOON,
        message="LLaVA-NeXT support is coming soon. Expected availability: v0.2.0",
        available_from="v0.2.0",
    ),
}

# Loader type to predictor key mapping (for auto-detection)
_LOADER_TYPE_TO_PREDICTOR: dict[str, str] = {
    "Qwen25VLLoader": "qwen25vl",
    "NVILALoader": "nvila",
    "DeepSeekOCRLoader": "deepseekocr",
}


class PredictorRegistry:
    """Registry for model predictors with plugin-style architecture.

    Maps loader types to appropriate predictor classes. New predictors can be
    added by decorating classes with @PredictorRegistry.register().

    Supports lazy loading - predictors are only imported when actually needed,
    preventing unnecessary dependency checks at import time.

    Example:
        ```python
        from vi.inference.predictors import BasePredictor, PredictorRegistry


        @PredictorRegistry.register(
            predictor_key="my_model", loader_types=["MyModelLoader"]
        )
        class MyModelPredictor(BasePredictor):
            def __call__(self, image_path, **kwargs):
                # Model-specific inference logic
                pass
        ```

    """

    _registry: dict[str, type[BasePredictor]] = {}
    _loader_mapping: dict[str, str] = {}

    @classmethod
    def register(
        cls,
        predictor_key: str,
        loader_types: list[str] | None = None,
    ) -> Callable[[type[BasePredictor]], type[BasePredictor]]:
        """Register a model predictor.

        Registers a predictor class with the registry, associating it with
        specific loader types for automatic selection.

        Args:
            predictor_key: Unique identifier for this predictor (e.g., "qwen25vl").
            loader_types: List of loader class names that this predictor handles
                (e.g., ["Qwen25VLLoader"]).

        Returns:
            Decorator function that registers the class and returns it unchanged.

        Example:
            ```python
            @PredictorRegistry.register(
                predictor_key="qwen25vl", loader_types=["Qwen25VLLoader"]
            )
            class Qwen25VLPredictor(BasePredictor):
                pass
            ```

        """

        def decorator(predictor_class: type[BasePredictor]) -> type[BasePredictor]:
            # Register the predictor
            cls._registry[predictor_key] = predictor_class

            # Map loader types to predictor key
            if loader_types:
                for loader_type in loader_types:
                    cls._loader_mapping[loader_type] = predictor_key

            return predictor_class

        return decorator

    @classmethod
    def _check_feature_status(
        cls, predictor_key: str, metadata: PredictorMetadata
    ) -> None:
        """Check feature status and issue appropriate warnings or errors.

        Args:
            predictor_key: The predictor key being accessed.
            metadata: Metadata for the predictor.

        Raises:
            NotImplementedError: If feature is coming soon and not enabled via env var.
            DeprecationWarning: If feature is deprecated.

        """
        status = metadata.status
        message = metadata.message

        if status == FeatureStatus.EXPERIMENTAL:
            warnings.warn(
                f"Predictor '{predictor_key}' is experimental and may change in future versions. "
                f"{message or 'Use with caution in production environments.'}",
                UserWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.PREVIEW:
            warnings.warn(
                f"Predictor '{predictor_key}' is in preview. "
                f"{message or 'The API may change in upcoming releases.'}",
                FutureWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.COMING_SOON:
            # Check if unreleased features are enabled
            if not should_allow_unreleased_features():
                error_msg = (
                    f"Predictor '{predictor_key}' is not yet available for public use."
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
                f"Predictor '{predictor_key}' is not yet released. "
                "You are using it with VI_ENABLE_UNRELEASED_FEATURES enabled. "
                "This feature may be incomplete or unstable.",
                UserWarning,
                stacklevel=4,
            )

        elif status == FeatureStatus.DEPRECATED:
            deprecated_in = metadata.deprecated_in or "unknown"
            removed_in = metadata.removed_in or "a future version"
            warnings.warn(
                f"Predictor '{predictor_key}' is deprecated since {deprecated_in} "
                f"and will be removed in {removed_in}. "
                f"{message or 'Please migrate to an alternative predictor.'}",
                DeprecationWarning,
                stacklevel=4,
            )

    @classmethod
    def _lazy_import_predictor(cls, predictor_key: str) -> type[BasePredictor]:
        """Lazily import a predictor class by key.

        Args:
            predictor_key: The predictor key to import.

        Returns:
            The predictor class.

        Raises:
            ValueError: If the predictor key is unknown.
            NotImplementedError: If the predictor is marked as coming soon
                and unreleased features are not enabled.

        """
        if predictor_key not in _PREDICTOR_METADATA:
            raise ValueError(
                f"Unknown predictor: '{predictor_key}'. "
                f"Available predictors: {cls.list_predictors()}"
            )

        metadata = _PREDICTOR_METADATA[predictor_key]

        # Check feature status and issue warnings/errors
        cls._check_feature_status(predictor_key, metadata)

        # Import the predictor
        module_path = metadata.module
        class_name = metadata.class_name
        module = importlib.import_module(module_path)
        predictor_class = getattr(module, class_name)

        # Cache in registry for subsequent calls
        cls._registry[predictor_key] = predictor_class

        return predictor_class

    @classmethod
    def get_predictor(
        cls,
        predictor_key: str | None = None,
        loader: BaseLoader | None = None,
    ) -> type[BasePredictor]:
        """Get predictor class by key or from loader instance.

        Retrieves the appropriate predictor class based on the provided identifier
        or by detecting the loader type. Predictors are imported lazily only when
        requested.

        Args:
            predictor_key: Direct predictor key (e.g., "qwen25vl").
            loader: Loader instance to find matching predictor for.

        Returns:
            Predictor class that can be instantiated with a loader.

        Raises:
            ValueError: If no arguments provided, both arguments provided,
                or if the specified predictor/loader is not found.

        Example:
            ```python
            # Get by predictor key
            predictor_class = PredictorRegistry.get_predictor(predictor_key="qwen25vl")

            # Get by loader instance
            loader = Qwen25VLLoader(model_meta)
            predictor_class = PredictorRegistry.get_predictor(loader=loader)
            ```

        """
        # Count how many arguments were provided
        args_provided = sum(x is not None for x in [predictor_key, loader])

        if args_provided == 0:
            raise ValueError("Must provide either predictor_key or loader")

        if args_provided > 1:
            raise ValueError("Provide either predictor_key or loader, not both")

        # Resolve to predictor_key
        if loader:
            loader_type = type(loader).__name__
            if loader_type not in _LOADER_TYPE_TO_PREDICTOR:
                raise ValueError(
                    f"No predictor registered for loader type '{loader_type}'. "
                    f"Supported loader types: {cls.list_loader_types()}"
                )
            predictor_key = _LOADER_TYPE_TO_PREDICTOR[loader_type]

        # Get from cache or lazy import
        if predictor_key in cls._registry:
            return cls._registry[predictor_key]

        return cls._lazy_import_predictor(predictor_key)

    @classmethod
    def list_predictors(cls, include_unreleased: bool = False) -> list[str]:
        """List all registered predictor keys.

        Args:
            include_unreleased: If True, include coming soon and preview predictors.
                Defaults to False.

        Returns:
            List of predictor keys that can be used with get_predictor().

        Example:
            ```python
            # List stable predictors only
            available = PredictorRegistry.list_predictors()
            print(f"Available predictors: {available}")

            # List all predictors including unreleased
            all_predictors = PredictorRegistry.list_predictors(include_unreleased=True)
            ```

        """
        # Include both registered and metadata-defined predictors
        all_predictors = set(cls._registry.keys()) | set(_PREDICTOR_METADATA.keys())

        if not include_unreleased:
            # Exclude coming soon and preview predictors
            all_predictors = {
                key
                for key in all_predictors
                if key not in _PREDICTOR_METADATA
                or _PREDICTOR_METADATA[key].status
                not in (FeatureStatus.COMING_SOON, FeatureStatus.PREVIEW)
            }

        return sorted(all_predictors)

    @classmethod
    def list_predictors_by_status(cls, status: FeatureStatus) -> list[str]:
        """List predictors filtered by feature status.

        Args:
            status: Feature status to filter by.

        Returns:
            List of predictor keys with the specified status.

        Example:
            ```python
            from vi.inference.feature_status import FeatureStatus

            # List experimental predictors
            experimental = PredictorRegistry.list_predictors_by_status(
                FeatureStatus.EXPERIMENTAL
            )

            # List coming soon predictors
            coming_soon = PredictorRegistry.list_predictors_by_status(
                FeatureStatus.COMING_SOON
            )
            ```

        """
        return sorted(
            [
                key
                for key, metadata in _PREDICTOR_METADATA.items()
                if metadata.status == status
            ]
        )

    @classmethod
    def get_predictor_status(cls, predictor_key: str) -> FeatureStatus:
        """Get the feature status of a predictor.

        Args:
            predictor_key: The predictor key to check.

        Returns:
            Feature status of the predictor.

        Raises:
            ValueError: If the predictor key is unknown.

        Example:
            ```python
            from vi.inference.predictors import PredictorRegistry

            status = PredictorRegistry.get_predictor_status("deepseekocr")
            print(status)  # FeatureStatus.COMING_SOON
            ```

        """
        if predictor_key not in _PREDICTOR_METADATA:
            raise ValueError(
                f"Unknown predictor: '{predictor_key}'. "
                f"Available predictors: {cls.list_predictors(include_unreleased=True)}"
            )

        return _PREDICTOR_METADATA[predictor_key].status

    @classmethod
    def list_loader_types(cls) -> list[str]:
        """List all loader types that have registered predictors.

        Returns:
            List of loader class names that have associated predictors.

        Example:
            ```python
            types = PredictorRegistry.list_loader_types()
            print(f"Supported loader types: {types}")
            # Output: ['Qwen25VLLoader', 'NVILALoader', ...]
            ```

        """
        # Include both registered and predefined mappings
        all_types = set(cls._loader_mapping.keys()) | set(
            _LOADER_TYPE_TO_PREDICTOR.keys()
        )
        return sorted(all_types)

    @classmethod
    def is_registered(
        cls,
        predictor_key: str | None = None,
        loader: BaseLoader | None = None,
    ) -> bool:
        """Check if a predictor is registered for the given identifier.

        Args:
            predictor_key: Predictor key to check.
            loader: Loader instance to check.

        Returns:
            True if a predictor is registered, False otherwise.

        Example:
            ```python
            if PredictorRegistry.is_registered(predictor_key="qwen25vl"):
                print("Qwen2.5-VL predictor is available")
            ```

        """
        if predictor_key:
            return (
                predictor_key in cls._registry or predictor_key in _PREDICTOR_METADATA
            )
        if loader:
            loader_type = type(loader).__name__
            return (
                loader_type in cls._loader_mapping
                or loader_type in _LOADER_TYPE_TO_PREDICTOR
            )
        return False
