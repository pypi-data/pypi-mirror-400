#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   vi_predictor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK auto predictor module.
"""

from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry


class _ViPredictorFactory:
    """Factory for automatically selecting predictor based on loader type.

    Analyzes the loader instance and automatically selects the appropriate
    predictor class. This provides a seamless inference experience where
    users don't need to manually match loaders to predictors.

    !!! note "Recommended Usage"
        For most use cases, prefer using `ViModel` which handles client initialization,
        model downloading, and prediction automatically:

        ```python
        from vi.inference import ViModel

        # Recommended: Use ViModel for Datature Vi models
        model = ViModel(
            secret_key="your-secret-key",
            organization_id="your-organization-id",
            run_id="your-run-id",
        )
        result = model(source="image.jpg", user_prompt="What's this?")
        ```

    Example:
        ```python
        from vi.inference.loaders import ViLoader
        from vi.inference.predictors import ViPredictor

        # Auto-select predictor for Qwen model (Datature Vi fine-tuned model)
        model_meta = client.get_model(run_id="my-run")
        loader = ViLoader(model_meta=model_meta)
        predictor = ViPredictor(loader)

        # Auto-select predictor for Qwen model (HuggingFace pretrained model)
        loader = ViLoader(pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct")
        predictor = ViPredictor(loader)

        # Or using the explicit method
        predictor = ViPredictor.from_loader(loader)

        # Run inference
        result = predictor(source="image.jpg", user_prompt="What's this?")
        ```

    Note:
        The predictor is automatically selected based on the loader's class name.
        If a predictor isn't registered for the loader type, an error is raised
        with available options.

    """

    def __call__(
        self,
        loader: BaseLoader,
        predictor_key: str | None = None,
    ) -> BasePredictor:
        """Create a predictor instance directly from a loader.

        This allows using ViPredictor(loader) as a shorthand for
        ViPredictor.from_loader(loader).

        Args:
            loader: Loaded model instance. Should have model, processor, and
                any other components required by the predictor.
            predictor_key: Optional explicit predictor to use (e.g., "qwen25vl").
                If provided, skips automatic detection.

        Returns:
            Predictor instance ready for inference.

        Example:
            ```python
            model_meta = client.get_model(run_id="my-run")
            loader = ViLoader(model_meta=model_meta)
            predictor = ViPredictor(loader)
            ```

            ```python
            loader = ViLoader(
                pretrained_model_name_or_path="Qwen/Qwen2.5-VL-7B-Instruct"
            )
            predictor = ViPredictor(loader)
            ```

        """
        return self.from_loader(
            loader=loader,
            predictor_key=predictor_key,
        )

    def from_loader(
        self,
        loader: BaseLoader,
        predictor_key: str | None = None,
    ) -> BasePredictor:
        """Create appropriate predictor for the given loader.

        This is an alternative to the primary ViPredictor() constructor.
        Prefer using ViPredictor(loader) for new code.

        Automatically detects the loader type and instantiates the matching
        predictor. Alternatively, allows explicit predictor selection.

        Args:
            loader: Loaded model instance. Should have model, processor, and
                any other components required by the predictor.
            predictor_key: Optional explicit predictor to use (e.g., "qwen25vl").
                If provided, skips automatic detection.

        Returns:
            Predictor instance ready for inference.

        Raises:
            ValueError: If no predictor is registered for the loader type.
            AttributeError: If the loader is missing required components.
            ImportError: If predictor-specific dependencies are not installed.

        Example:
            ```python
            from vi.inference.loaders import ViLoader
            from vi.inference.predictors import ViPredictor

            # Auto-detect predictor (Datature Vi fine-tuned model)
            model_meta = client.get_model(run_id="my-run")
            loader = ViLoader(model_meta=model_meta)
            predictor = ViPredictor.from_loader(loader)

            # Auto-detect predictor (HuggingFace pretrained model)
            loader = ViLoader(pretrained_model_name_or_path="path/to/model")
            predictor = ViPredictor.from_loader(loader)

            # Explicit predictor selection
            predictor = ViPredictor.from_loader(loader, predictor_key="qwen25vl")

            # Run inference
            result = predictor(source="image.jpg", user_prompt="Describe this image")
            print(result)
            ```

        Note:
            The predictor is selected based on the loader's class name
            (e.g., "Qwen25VLLoader" → "qwen25vl" predictor). This mapping
            is configured when predictors are registered with
            @PredictorRegistry.register().

        See Also:
            - `ViLoader`: Loading models with automatic detection
            - `PredictorRegistry`: Registry for managing predictors
            - [Inference Guide](../guide/inference.md): Complete workflow

        """
        # Get predictor class from registry
        if predictor_key:
            predictor_class = PredictorRegistry.get_predictor(
                predictor_key=predictor_key
            )
        else:
            predictor_class = PredictorRegistry.get_predictor(loader=loader)

        # Instantiate predictor with loader
        return predictor_class(loader)

    def list_available_predictors(self) -> list[str]:
        """List all available predictor keys.

        Returns:
            List of registered predictor keys.

        Example:
            ```python
            predictors = ViPredictor.list_available_predictors()
            print(f"Available predictors: {predictors}")
            # Output: Available predictors: ['qwen25vl', ...]
            ```

        """
        return PredictorRegistry.list_predictors()

    def list_supported_loaders(self) -> list[str]:
        """List all loader types that have registered predictors.

        Returns:
            List of loader class names with associated predictors.

        Example:
            ```python
            loaders = ViPredictor.list_supported_loaders()
            print(f"Supported loaders: {loaders}")
            # Output: Supported loaders: ['Qwen25VLLoader', ...]
            ```

        """
        return PredictorRegistry.list_loader_types()


ViPredictor: _ViPredictorFactory = _ViPredictorFactory()
