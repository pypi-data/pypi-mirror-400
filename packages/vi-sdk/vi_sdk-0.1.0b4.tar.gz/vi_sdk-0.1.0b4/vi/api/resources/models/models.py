#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   models.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK models module.
"""

from pathlib import Path

from vi.api.pagination import PaginatedResponse
from vi.api.resources.models import responses
from vi.api.resources.models.downloader import ModelDownloader
from vi.api.resources.models.links import ModelLinkParser
from vi.api.resources.models.results import ModelDownloadResult
from vi.api.resources.models.types import ModelListParams
from vi.api.responses import Pagination
from vi.api.types import PaginationParams
from vi.client.auth import Authentication
from vi.client.http.requester import Requester
from vi.client.rest.resource import RESTResource
from vi.client.validation import validate_id_param, validate_pagination_params
from vi.consts import DEFAULT_MODEL_DIR


class Model(RESTResource):
    """Model resource for managing trained models from training runs.

    This class provides methods to list, retrieve, and download trained models
    that are produced by training runs. Models represent the trained weights
    and artifacts that can be used for inference or further training.

    Example:
        ```python
        import vi

        client = vi.Client()
        models = client.models

        # List models from a training run
        model_list = models.list(run_id_or_link="run_abc123")
        for model in model_list.items:
            print(f"Model: {model.model_id} (epoch: {model.spec.epoch})")

        # Get the latest model from a run
        model = models.get(run_id_or_link="run_abc123")
        if model.spec.evaluation_metrics:
            print(f"Model metrics: {model.spec.evaluation_metrics}")

        # Download a model for inference
        from pathlib import Path

        result = models.download(
            run_id_or_link="run_abc123", save_dir=Path("./my_models")
        )
        print(f"Model downloaded to: {result.save_dir}")
        ```

    Note:
        Models are always associated with specific training runs. All operations
        require a run_id_or_link parameter to specify which training run to
        retrieve models from.

    See Also:
        - [Model Guide](../../guide/models.md): Complete guide to training and managing models
        - [`Run`](../../api/resources/runs.md): Training run resource
        - [`Flow`](../../api/resources/flows.md): Training workflow resource

    """

    _link_parser: ModelLinkParser

    def __init__(self, auth: Authentication, requester: Requester):
        """Initialize the Model resource.

        Args:
            auth: Authentication instance containing credentials.
            requester: HTTP requester instance for making API calls.

        """
        super().__init__(auth, requester)
        self._link_parser = ModelLinkParser(auth.organization_id)

    def list(
        self,
        run_id_or_link: str,
        pagination: PaginationParams | dict = PaginationParams(),
    ) -> PaginatedResponse[responses.Model]:
        """List all models from a training run.

        Retrieves a paginated list of all model checkpoints produced by a specific
        training run. Models are ordered by checkpoint number, with the latest
        checkpoint appearing last.

        Args:
            run_id_or_link: The unique identifier or link of the training run
                to retrieve models from.
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a `PaginationParams` object or a dict with pagination settings.
                Defaults to `PaginationParams()` (first page, default page size).

        Returns:
            PaginatedResponse containing Model objects with navigation support.
            Each Model contains checkpoint information, metrics, and download links.

        Raises:
            ViNotFoundError: If the training run doesn't exist.
            ViValidationError: If the run_id_or_link format is invalid or pagination
                parameters are invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # List all models from a training run with default pagination
            models = client.models.list(run_id_or_link="run_abc123")

            # Iterate through model checkpoints
            for model in models.items:
                print(f"Model {model.model_id}:")
                print(f"  Epoch: {model.spec.epoch}")
                if model.spec.evaluation_metrics:
                    print(f"  Metrics: {model.spec.evaluation_metrics}")
                print(f"  Created: {model.metadata.time_created}")

            # Get the latest model (last in list)
            if models.items:
                latest_model = models.items[-1]
                print(f"Latest model: {latest_model.model_id}")

            # Iterate through all model checkpoints across pages
            for model in models.all_items():
                print(f"Processing model: {model.model_id}")

            # Custom pagination
            models = client.models.list(
                run_id_or_link="run_abc123", pagination={"page_size": 50, "page": 2}
            )
            ```

        Note:
            Models are ordered by checkpoint number. The latest trained model
            checkpoint appears last in the list. Use `get()` without a checkpoint
            parameter to directly retrieve the latest model.

        See Also:
            - `get()`: Retrieve a specific model checkpoint
            - `download()`: Download a model for inference
            - `Run.list()`: List training runs

        """
        validate_id_param(run_id_or_link, "run_id_or_link")

        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        model_params = ModelListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(run_id_or_link),
            params=model_params.to_query_params(),
            response_type=Pagination[responses.Model],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={
                    "run_id_or_link": run_id_or_link,
                    "pagination": pagination,
                },
            )

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def get(
        self, run_id_or_link: str, ckpt: str | None = None, contents: bool = False
    ) -> responses.Model:
        """Get a specific model checkpoint from a training run.

        Retrieves detailed information about a model checkpoint including metrics,
        training configuration, and optionally download links. If no checkpoint
        is specified, returns the latest (most recent) model checkpoint.

        Args:
            run_id_or_link: The unique identifier or link of the training run.
            ckpt: The specific checkpoint identifier to retrieve. If None,
                retrieves the latest checkpoint from the run. Defaults to None.
            contents: Whether to include download links and file contents in
                the response. Set to True when planning to download the model.
                Defaults to False.

        Returns:
            Model object containing checkpoint information, training metrics,
            configuration, and optionally download links if contents=True.

        Raises:
            ViNotFoundError: If the training run or checkpoint doesn't exist.
            ViValidationError: If the run_id_or_link format is invalid.
            ViOperationError: If no models are found for the run.

        Example:
            ```python
            # Get the latest model from a training run
            model = client.models.get(run_id_or_link="run_abc123")
            print(f"Model ID: {model.model_id}")
            print(f"Epoch: {model.spec.epoch}")
            if model.spec.evaluation_metrics:
                print(f"Metrics: {model.spec.evaluation_metrics}")

            # Get a specific checkpoint
            model = client.models.get(run_id_or_link="run_abc123", ckpt="checkpoint_50")
            if model.spec.evaluation_metrics:
                print(f"Checkpoint 50 metrics: {model.spec.evaluation_metrics}")

            # Get model with download contents
            model = client.models.get(run_id_or_link="run_abc123", contents=True)
            print(f"Download URL: {model.status.contents.download_url.url}")
            print(f"Model size: {model.status.contents.file_size} bytes")
            ```

        Note:
            When contents=False, download links are not included in the response,
            making the request faster. Set contents=True only when you need to
            download the model or access file information.

        See Also:
            - `list()`: List all model checkpoints
            - `download()`: Download a model checkpoint
            - [Model Guide](../../guide/models.md): Understanding model checkpoints

        """
        validate_id_param(run_id_or_link, "run_id_or_link")

        response = self._requester.get(
            self._link_parser(run_id_or_link, ckpt, contents),
            response_type=Pagination[responses.Model],
        )

        if isinstance(response, Pagination):
            if not response.items:
                raise ValueError(f"No models found for run_id_or_link {run_id_or_link}")

            return response.items[-1]

        if isinstance(response, responses.Model):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def download(
        self,
        run_id_or_link: str,
        ckpt: str | None = None,
        save_dir: Path | str = DEFAULT_MODEL_DIR,
        overwrite: bool = False,
        show_progress: bool = True,
    ) -> ModelDownloadResult:
        """Download a trained model to local storage for inference or deployment.

        Downloads a model checkpoint from a training run including weights, configuration,
        and metadata files. The downloaded model can be used for inference, fine-tuning,
        or deployment to production environments.

        Args:
            run_id_or_link: The unique identifier or link of the training run
                containing the model to download.
            ckpt: The specific checkpoint identifier to download. If None,
                downloads the latest (best) checkpoint from the run. Defaults to None.
            save_dir: Directory where the model will be saved. The model is saved
                in a subdirectory named with the run ID. Defaults to ~/.datature/vi/models/.
            overwrite: Whether to overwrite existing model files. If False, existing
                files are skipped. If True, files are re-downloaded. Defaults to False.
            show_progress: Whether to display download progress bar with transfer
                speed and completion percentage. Set to False for non-interactive
                environments. Defaults to True.

        Returns:
            ModelDownloadResult wrapper containing download information and helper
            methods. Use `.summary()` to see download statistics or `.info()` for
            detailed information about the downloaded model.

        Raises:
            ViNotFoundError: If the training run or checkpoint doesn't exist.
            ViValidationError: If the run_id_or_link format is invalid.
            ViDownloadError: If download fails due to network issues.
            PermissionError: If unable to write to save_dir.
            OSError: If insufficient disk space for download.

        Example:
            ```python
            from pathlib import Path

            # Download the latest model from a training run
            result = client.models.download(run_id_or_link="run_abc123")
            print(result.summary())

            # Access download details
            print(f"Model path: {result.model_path}")
            print(f"Has adapter: {result.has_adapter}")
            print(f"Total size: {result.size_mb:.1f} MB")

            # Show detailed information
            result.info()

            # Download a specific checkpoint
            result = client.models.download(
                run_id_or_link="run_abc123",
                ckpt="checkpoint_50",
                save_dir=Path("./production_models"),
            )

            # Download without progress (for scripts)
            result = client.models.download(
                run_id_or_link="run_abc123", show_progress=False, overwrite=True
            )

            # Use downloaded model for inference
            from vi.inference import ViModel

            model = ViModel(
                secret_key="your-secret-key",
                organization_id="your-organization-id",
                run_id="run_abc123",
            )
            result = model(source="test.jpg", user_prompt="Describe this image")
            ```

        Note:
            - Downloaded models include weights, configuration, and metadata
            - Models are saved in format: save_dir/run_id/{model_full, model_adapter}
            - Large models may take several minutes to download
            - The latest checkpoint is typically the best performing model

        Warning:
            Ensure sufficient disk space before downloading. Model files can
            range from hundreds of MB to several GB depending on the architecture.

        See Also:
            - `get()`: Get model information before downloading
            - `list()`: List available model checkpoints
            - [Model Guide](../../guide/models.md): Using downloaded models for inference
            - [Inference Guide](../../guide/inference.md): Loading and running inference

        """
        validate_id_param(run_id_or_link, "run_id_or_link")

        model = self.get(run_id_or_link, ckpt, contents=True)
        run_id = model.run_id

        # Check if model has contents and download URL
        if not model.status:
            raise ValueError(
                f"Model {run_id} does not have a status. "
                "The model may not be ready for download yet."
            )

        if not model.status.contents:
            raise ValueError(
                f"Model {run_id} does not have contents available. "
                "The model may still be training or has not been exported yet."
            )

        if not model.status.contents.download_url:
            raise ValueError(
                f"Model {run_id} does not have a download URL available. "
                "The model export may still be in progress or has failed. "
                "Please check the model status on Datature Vi."
            )

        downloader = ModelDownloader(show_progress=show_progress, overwrite=overwrite)

        return downloader.download(
            run_id=run_id,
            download_url=model.status.contents.download_url.url,
            save_dir=save_dir,
        )

    def help(self) -> None:
        """Display helpful information about using the Model resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on models
            client.models.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          Model Resource - Quick Help                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List models from a training run:
    models = client.models.list(run_id_or_link="run_abc123")
    for model in models.items:
        print(f"{model.model_id}: epoch {model.spec.epoch}")

  List with custom pagination:
    models = client.models.list(
        run_id_or_link="run_abc123",
        pagination={"page_size": 50}
    )

  Get the latest model:
    model = client.models.get(run_id_or_link="run_abc123")
    model.info()  # Show detailed information

  Get a specific checkpoint:
    model = client.models.get(
        run_id_or_link="run_abc123",
        ckpt="checkpoint_50"
    )

  Download a model:
    result = client.models.download(
        run_id_or_link="run_abc123",
        save_dir="./my_models"
    )
    print(f"Model saved to: {result.model_path}")

  Download specific checkpoint:
    result = client.models.download(
        run_id_or_link="run_abc123",
        ckpt="checkpoint_50",
        save_dir="./models"
    )

📖 AVAILABLE METHODS:

  • list(run_id_or_link, pagination=...)  - List model checkpoints with pagination
  • get(run_id_or_link, ckpt=None)        - Get latest or specific checkpoint
  • download(run_id_or_link, ...)         - Download model for inference

💡 TIPS:

  • Models are organized by training runs
  • Latest checkpoint is usually the best model
  • Download includes weights and configuration
  • Check model.info() for metrics and details
  • Use ckpt parameter for specific checkpoints
  • Models can be large (at least several GB)

⚡ USE WITH INFERENCE:

  from vi.inference import ViModel

  model = ViModel(
      secret_key="your-key",
      organization_id="your-org",
      run_id="run_abc123"
  )
  result = model(source="image.jpg", user_prompt="Describe")

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-models

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
