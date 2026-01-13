#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   vi_model.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK auto model module.
"""

import os
from collections.abc import Generator, Sequence
from pathlib import Path
from typing import Any

from rich import print as rprint
from rich.progress import (
    BarColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from vi.api.client import ViClient
from vi.api.resources.models.results import ModelDownloadResult
from vi.client.consts import DATATURE_VI_API_ENDPOINT
from vi.consts import (
    DEFAULT_ADAPTER_DIR_NAME,
    DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_DIR_NAME,
    DEFAULT_RUN_CONFIG_FILE_NAME,
)
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.loaders.vi_loader import ViLoader
from vi.inference.model_info import ModelInfo, inspect_model_from_path
from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.predictors.vi_predictor import ViPredictor
from vi.inference.responses import Stream
from vi.inference.utils.path_utils import resolve_sources_to_paths
from vi.utils.progress import ViProgress


class ViModel:
    r"""Vi model class that automatically loads the model and predictor.

    This is the recommended way to load models and run inference. ViModel handles
    client initialization, model downloading, and prediction in a single class.

    Example:
        ```python
        from vi.inference import ViModel

        # Load model with credentials and run ID
        model = ViModel(
            secret_key="your-secret-key",
            organization_id="your-organization-id",
            run_id="your-run-id",
        )

        # Run inference with streaming (default)
        stream = model(source="image.jpg", user_prompt="Describe this image")
        for token in stream:
            print(token, end="", flush=True)
        # Get final result after streaming
        result = stream.get_final_completion()
        print(f"\nFinal result: {result}")

        # Run inference without streaming
        result, error = model(source="image.jpg", stream=False)
        if error is None:
            print(result.caption)

        # Force re-download of model even if it exists locally
        model = ViModel(
            secret_key="your-secret-key",
            organization_id="your-organization-id",
            run_id="your-run-id",
            overwrite=True,
        )
        ```

    Args:
        secret_key: Your Vi SDK secret key
        organization_id: Your organization ID
        run_id: The run ID of the trained model
        ckpt: Optional checkpoint identifier
        save_path: Directory to save downloaded model files
        pretrained_model_name_or_path: HuggingFace model name or local path
        loader_key: Optional explicit loader to use
        overwrite: If True, re-download the model even if it exists locally.
            Defaults to False.
        **kwargs: Additional arguments passed to the loader

    """

    _loader: BaseLoader
    _predictor: BasePredictor

    def __init__(
        self,
        secret_key: str | None = None,
        organization_id: str | None = None,
        endpoint: str | None = None,
        run_id: str | None = None,
        ckpt: str | None = None,
        save_path: Path | str = DEFAULT_MODEL_DIR,
        pretrained_model_name_or_path: str | None = None,
        loader_key: str | None = None,
        overwrite: bool = False,
        **kwargs: Any,
    ):
        """Initialize the model with automatic client setup and model downloading."""
        # Load credentials from environment variables if not provided
        if secret_key is None:
            secret_key = os.getenv("DATATURE_VI_SECRET_KEY")
        if organization_id is None:
            organization_id = os.getenv("DATATURE_VI_ORGANIZATION_ID")
        if endpoint is None:
            endpoint = os.getenv("DATATURE_VI_API_ENDPOINT", DATATURE_VI_API_ENDPOINT)

        if pretrained_model_name_or_path:
            self._loader = ViLoader(
                pretrained_model_name_or_path=pretrained_model_name_or_path,
                loader_key=loader_key,
                **kwargs,
            )

        elif run_id:
            model_dir = Path(save_path) / run_id / DEFAULT_MODEL_DIR_NAME
            if model_dir.exists() and not overwrite:
                adapter_dir = model_dir.parent / DEFAULT_ADAPTER_DIR_NAME
                run_config_path = model_dir / DEFAULT_RUN_CONFIG_FILE_NAME

                model_meta = ModelDownloadResult(
                    model_path=str(model_dir),
                    adapter_path=str(adapter_dir) if adapter_dir.exists() else None,
                    run_config_path=(
                        str(run_config_path) if run_config_path.exists() else None
                    ),
                )

            else:
                client = ViClient(
                    secret_key=secret_key,
                    organization_id=organization_id,
                    endpoint=endpoint,
                )

                try:
                    model_meta = client.get_model(
                        run_id=run_id,
                        ckpt=ckpt,
                        save_path=save_path,
                        overwrite=overwrite,
                    )
                except ValueError as e:
                    raise ValueError(
                        f"Failed to download model: {e}\n\n"
                        "Common reasons:\n"
                        "  - The model is still training\n"
                        "  - The model export is in progress\n"
                        "  - The model export failed\n"
                        "  - The run_id is incorrect\n\n"
                        "Please check the model status on Datature Vi and try again."
                    ) from e

                if not model_meta:
                    raise ValueError(
                        "Failed to download model: no model metadata returned.\n\n"
                        "This may indicate an issue with the model export process.\n"
                        "Please check the model status on Datature Vi and try again."
                    )

            self._loader = ViLoader(
                model_meta=model_meta,
                pretrained_model_name_or_path=pretrained_model_name_or_path,
                loader_key=loader_key,
                **kwargs,
            )

        else:
            raise AttributeError(
                "Either run_id must be provided when loading models from Datature Vi, "
                "or pretrained_model_name_or_path must be provided when "
                "loading pretrained models from HuggingFace."
            )

        self._predictor = ViPredictor(self._loader)

    def __call__(
        self,
        source: str | Path | Sequence[str | Path] | None = None,
        user_prompt: str | Sequence[str] | None = None,
        show_progress: bool = True,
        recursive: bool = False,
        **kwargs: Any,
    ) -> Any:
        r"""Call the model for single or batch inference.

        Automatically detects whether to run single or batch inference based on
        the input type. Always returns (result, error) tuples for consistent
        error handling across single and batch inference.

        Args:
            source: Image source(s) for inference. Can be:
                - Single file path (string or Path): "./image.jpg"
                - Directory path: "./images/" (processes all images in folder)
                - List of file/directory paths: ["./img1.jpg", "./folder/", ...]
            user_prompt: Text prompt for the model. Can be:
                - Single string (used for all images in batch)
                - List of strings (one per image in batch)
                - None (uses default prompt if supported by task)
            show_progress: Whether to display progress indicator. Shows a spinner
                for single inference and progress bar for batch inference. Defaults to True.
            recursive: Whether to recursively search subdirectories when
                processing directory paths. Defaults to False.
            **kwargs: Additional arguments passed to the predictor
                (e.g., max_new_tokens, temperature)

        Returns:
            - Single inference with stream=True: Stream that can be iterated for tokens.
              Use stream.get_final_completion() to get the final parsed result.
            - Single inference with stream=False: Tuple of (result, error) where error is None on success
            - Batch inference: List of (result, error) tuples

        Raises:
            ValueError: If user_prompt length doesn't match sources length (batch)
            KeyboardInterrupt: If user cancels the operation

        Example:
            ```python
            from vi.inference import ViModel

            model = ViModel(run_id="your-run")

            # Single inference with streaming (default)
            stream = model(source="image.jpg", user_prompt="Describe this image")
            for token in stream:
                print(token, end="", flush=True)
            # Get final result after streaming
            result = stream.get_final_completion()
            print(f"\nFinal result: {result}")

            # Single inference without streaming
            result, error = model(source="image.jpg", stream=False)
            if error is None:
                print(result.caption)
            else:
                print(f"Error: {error}")

            # Batch inference with list of files
            results = model(
                source=["img1.jpg", "img2.jpg", "img3.jpg"],
                user_prompt="What's in this image?",
            )
            for result, error in results:
                if error is None:
                    print(result.caption)
                else:
                    print(f"Error: {type(error).__name__}: {error}")

            # Batch inference with directory
            results = model(
                source="./my_images/",
                user_prompt="Describe this image",
            )

            # Recursive directory search
            results = model(
                source="./dataset/",
                user_prompt="What's in this?",
                recursive=True,
            )

            # Batch with different prompts per image
            results = model(
                source=["img1.jpg", "img2.jpg"],
                user_prompt=["What's the main object?", "Count the people"],
            )
            ```

        Note:
            - Single inference with stream=True returns Stream (default)
            - Single inference with stream=False returns (result, error) tuple
            - Batch inference always returns list of (result, error) tuples
            - error is None on success, Exception on failure

        """
        try:
            if source is None:
                raise ValueError("source parameter is required for inference")

            # Resolve sources to paths (handles files, directories, and lists)
            try:
                resolved_sources = resolve_sources_to_paths(source, recursive=recursive)
            except (FileNotFoundError, ValueError) as e:
                # Return as single error or list of errors depending on input type
                if isinstance(source, (list, tuple)):
                    return [(None, e) for _ in source]
                return (None, e)

            # If we got multiple paths, run batch inference
            if len(resolved_sources) > 1:
                return self._batch_inference(
                    sources=resolved_sources,
                    user_prompts=user_prompt,
                    show_progress=show_progress,
                    **kwargs,
                )

            # Single file inference
            try:
                if show_progress:
                    rprint("[cyan]Running inference...")

                result = self._predictor(
                    source=str(resolved_sources[0]),
                    user_prompt=(user_prompt if isinstance(user_prompt, str) else None),
                    **kwargs,
                )

                # Check if result is a generator (streaming mode)
                if isinstance(result, Generator):
                    return Stream(lambda: result)

                # Non-streaming mode - return (result, error) tuple
                return (result, None)
            except Exception as e:
                return (None, e)

        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Model prediction cancelled by user[/yellow]")
            raise

    def _batch_inference(
        self,
        sources: Sequence[Path],
        user_prompts: str | Sequence[str] | None = None,
        show_progress: bool = True,
        **kwargs: Any,
    ) -> list[tuple[Any | None, Exception | None]]:
        """Execute batch inference.

        Args:
            sources: List of resolved Path objects (already validated)
            user_prompts: Single prompt or list of prompts
            show_progress: Whether to show progress bar
            **kwargs: Additional predictor arguments

        Returns:
            List of (result, error) tuples for each source

        """
        # Validate inputs
        if user_prompts is not None and isinstance(user_prompts, (list, tuple)):
            if len(user_prompts) != len(sources):
                raise ValueError(
                    f"Length of user_prompts ({len(user_prompts)}) must match "
                    f"length of sources ({len(sources)})"
                )

        # Prepare prompts list
        if user_prompts is None:
            prompts_list: list[str | None] = [None] * len(sources)
        elif isinstance(user_prompts, str):
            prompts_list = [user_prompts] * len(sources)
        else:
            prompts_list = list(user_prompts)

        results: list[tuple[Any | None, Exception | None]] = []

        try:
            # Create progress bar if requested
            if show_progress:
                with ViProgress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeRemainingColumn(),
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Running batch inference ({len(results)} / {len(sources)} images)...",
                        total=len(sources),
                    )

                    for src, prompt in zip(sources, prompts_list):
                        result, error = self._run_single_prediction(
                            src, prompt, **kwargs
                        )
                        results.append((result, error))
                        progress.update(
                            task,
                            description=(
                                "[cyan]Running batch inference "
                                f"({len(results)} / {len(sources)} images)..."
                            ),
                            advance=1,
                        )

            else:
                # Process without progress bar
                for src, prompt in zip(sources, prompts_list):
                    result, error = self._run_single_prediction(src, prompt, **kwargs)
                    results.append((result, error))

        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Batch inference cancelled by user[/yellow]")
            raise

        return results

    def _run_single_prediction(
        self,
        source: Path,
        prompt: str | None,
        **kwargs: Any,
    ) -> tuple[Any | None, Exception | None]:
        """Execute a single prediction with error handling.

        Args:
            source: Path to the image file
            prompt: Optional text prompt
            **kwargs: Additional predictor arguments

        Returns:
            Tuple of (result, error) where error is None on success

        """
        try:
            if prompt is not None:
                result = self._predictor(
                    source=str(source),
                    user_prompt=prompt,
                    **kwargs,
                )
            else:
                result = self._predictor(source=str(source), **kwargs)
            return (result, None)
        except Exception as e:
            return (None, e)

    @property
    def loader(self) -> BaseLoader:
        """Get the underlying loader instance.

        Returns:
            The BaseLoader instance used by this model

        """
        return self._loader

    @property
    def predictor(self) -> BasePredictor:
        """Get the underlying predictor instance.

        Returns:
            The BasePredictor instance used by this model

        """
        return self._predictor

    @classmethod
    def inspect(
        cls,
        secret_key: str | None = None,
        organization_id: str | None = None,
        run_id: str | None = None,
        ckpt: str | None = None,
        save_path: Path | str = DEFAULT_MODEL_DIR,
        pretrained_model_name_or_path: str | None = None,
    ) -> ModelInfo:
        """Inspect model information without loading the full model.

        Quickly check model metadata, size, architecture, and capabilities before
        committing resources to load the full model. Useful for:
        - Checking if model fits in available memory
        - Verifying model architecture and task type
        - Understanding model requirements before loading

        Args:
            secret_key: Your Vi SDK secret key. If None, attempts to load from
                environment variable or config file.
            organization_id: Your organization ID. If None, attempts to load from
                environment variable or config file.
            run_id: The run ID of the trained model to inspect. Downloads model
                if not already cached locally.
            ckpt: Optional checkpoint identifier. If None, uses latest checkpoint.
            save_path: Directory where models are saved/cached. Defaults to
                ~/.datature/vi/models/
            pretrained_model_name_or_path: HuggingFace model name or local path
                to inspect. Alternative to using run_id.

        Returns:
            ModelInfo object containing model metadata without loading the model

        Raises:
            ValueError: If neither run_id nor pretrained_model_name_or_path provided
            FileNotFoundError: If model path doesn't exist
            ViAuthenticationError: If credentials are invalid

        Example:
            ```python
            from vi.inference import ViModel

            # Inspect Datature model before loading
            info = ViModel.inspect(
                secret_key="your-key",
                organization_id="your-org",
                run_id="your-run-id",
            )

            print(f"Model: {info.model_name}")
            print(f"Size: {info.size_gb:.2f} GB")
            print(f"Architecture: {info.architecture}")
            print(f"Task: {info.task_type}")

            # Decide whether to load based on requirements
            if info.size_gb < 10 and info.task_type == "VQA":
                # Load the model
                model = ViModel(
                    secret_key="your-key",
                    organization_id="your-org",
                    run_id="your-run-id",
                )
            else:
                print("Model doesn't meet requirements")

            # Inspect local model
            info = ViModel.inspect(pretrained_model_name_or_path="./path/to/model")
            print(info)
            ```

        Note:
            - This method is fast as it only reads configuration files
            - For remote models, downloads only config files (< 1 MB typically)
            - Model size is estimated from local files if available
            - For HuggingFace models, downloads model if not cached

        See Also:
            - `ViModel.__init__()`: Load model after inspection
            - `ModelInfo`: Detailed information about model metadata

        """
        try:
            if pretrained_model_name_or_path:
                # Inspect local or HuggingFace model
                model_path = Path(pretrained_model_name_or_path).expanduser().resolve()

                if not model_path.exists():
                    # Might be HuggingFace model, can't inspect without downloading
                    raise ValueError(
                        f"Model path '{pretrained_model_name_or_path}' not found. "
                        "For HuggingFace models, download them first or use run_id "
                        "for Datature models."
                    )

                return inspect_model_from_path(model_path)

            if run_id:
                # Check if model already downloaded
                model_dir = Path(save_path) / run_id / DEFAULT_MODEL_DIR_NAME

                if not model_dir.exists():
                    # Download model
                    rprint(
                        "[cyan]Model not cached locally. Downloading model...[/cyan]"
                    )
                    client = ViClient(
                        secret_key=secret_key,
                        organization_id=organization_id,
                    )

                    model_meta = client.get_model(
                        run_id=run_id, ckpt=ckpt, save_path=save_path
                    )
                    model_dir = Path(model_meta.model_path)

                # Inspect the model
                info = inspect_model_from_path(model_dir)
                info.run_id = run_id

                # Check for adapter
                adapter_dir = model_dir.parent / DEFAULT_ADAPTER_DIR_NAME
                info.adapter_available = adapter_dir.exists()

                return info

            raise ValueError(
                "Either run_id or pretrained_model_name_or_path must be provided "
                "to inspect a model."
            )

        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Model inspection cancelled by user[/yellow]")
            raise
