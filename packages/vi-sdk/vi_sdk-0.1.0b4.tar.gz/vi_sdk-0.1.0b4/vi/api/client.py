#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   client.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK API client module.
"""

import os
from dataclasses import replace
from pathlib import Path

from vi.api.resources.datasets import Annotation, Asset, Dataset
from vi.api.resources.datasets.results import DatasetDownloadResult
from vi.api.resources.datasets.types import DatasetExportSettings
from vi.api.resources.flows import Flow
from vi.api.resources.models import Model
from vi.api.resources.models.results import ModelDownloadResult
from vi.api.resources.organizations import Organization
from vi.api.resources.runs import Run
from vi.client import APIClient
from vi.client.auth import SecretKeyAuth
from vi.client.consts import DATATURE_VI_API_ENDPOINT
from vi.client.http.requester import Requester, RetryConfig, httpx
from vi.consts import DEFAULT_DATASET_EXPORT_DIR, DEFAULT_MODEL_DIR
from vi.logging.config import LoggingConfig
from vi.logging.logger import configure_logging, get_logger


class ViClient(APIClient):
    """Vi platform API client for managing datasets, assets, annotations, and models.

    The ViClient is the main entry point for interacting with the Datature Vi platform.
    It handles authentication, request management, and provides access to all platform
    resources through a flat structure.

    The client implements the context manager protocol for automatic resource cleanup
    and supports connection pool configuration for high-performance workloads.

    Args:
        secret_key: Vi API secret key. Can be obtained from Datature Vi.
            If None, will attempt to load from environment variable DATATURE_VI_SECRET_KEY
            or from config file.
        organization_id: Organization identifier. If None, will attempt to load from
            environment variable DATATURE_VI_ORGANIZATION_ID or from config file.
        config_file: Path to JSON configuration file containing secret_key and
            organization_id. Example: ~/datature/vi/config.json
        endpoint: API endpoint URL. Defaults to https://api.vi.datature.com or value from
            DATATURE_VI_API_ENDPOINT environment variable.
        logging_config: Configuration for structured logging. If None, uses default
            configuration with environment variable overrides.
        max_connections: Maximum number of concurrent HTTP connections in the pool.
            Defaults to 100. Increase for high-concurrency workloads.
        max_keepalive_connections: Maximum number of keep-alive connections to maintain.
            Defaults to 20. Keep-alive connections improve performance for repeated requests.

    Attributes:
        organizations: Access to organization-level resources
        datasets: Access to dataset-level resources
        assets: Access to asset-level resources
        annotations: Access to annotation-level resources
        flows: Access to flow-level resources
        runs: Access to run-level resources
        models: Access to model-level resources

    Examples:
        Using context manager (recommended):

        >>> import vi
        >>> with vi.Client(
        ...     secret_key="sk_live_abc123...", organization_id="org_xyz789..."
        ... ) as client:
        ...     datasets = client.datasets.list()
        ...     # Automatic cleanup on exit

        Initialize with direct credentials:

        >>> import vi
        >>> client = vi.Client(
        ...     secret_key="sk_live_abc123...", organization_id="org_xyz789..."
        ... )
        >>> try:
        ...     datasets = client.datasets.list()
        ... finally:
        ...     client.close()  # Manual cleanup

        Initialize with environment variables:

        >>> import os
        >>> client = vi.Client(
        ...     secret_key=os.getenv("DATATURE_VI_SECRET_KEY"),
        ...     organization_id=os.getenv("DATATURE_VI_ORGANIZATION_ID"),
        ... )

        Initialize with config file:

        >>> client = vi.Client(config_file="path/to/config.json")

        With custom logging and connection pooling:

        >>> from vi.logging import LoggingConfig, LogLevel
        >>> logging_config = LoggingConfig(level=LogLevel.DEBUG, enable_console=True)
        >>> client = vi.Client(
        ...     secret_key="your-key",
        ...     organization_id="your-org",
        ...     logging_config=logging_config,
        ...     max_connections=200,  # Increase for high concurrency
        ...     max_keepalive_connections=50,
        ... )

    Raises:
        ViAuthenticationError: If credentials are invalid or missing.
        ViConfigurationError: If configuration is invalid.

    See Also:
        - [Authentication Guide](../getting-started/authentication.md): Complete authentication setup
        - [Configuration Guide](../getting-started/configuration.md): Advanced configuration options
        - `LoggingConfig`: Logging configuration options

    """

    organizations: Organization
    datasets: Dataset
    assets: Asset
    annotations: Annotation
    models: Model
    runs: Run
    flows: Flow

    def __init__(
        self,
        secret_key: str | None = None,
        organization_id: str | None = None,
        config_file: str | Path | None = None,
        endpoint: str | None = None,
        logging_config: LoggingConfig | None = None,
        timeout: httpx.Timeout | None = None,
        max_retries: int | None = None,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        retry_config: RetryConfig | None = None,
    ):
        """Initialize the Vi API client.

        Creates a new client instance for interacting with the Datature Vi platform.
        Credentials can be provided explicitly, loaded from environment variables,
        or read from a configuration file. The client automatically handles
        authentication, logging, and API communication.

        Args:
            secret_key: API secret key for authentication. If not provided, will
                attempt to load from DATATURE_VI_SECRET_KEY environment variable or from
                the configuration file at ~/datature/vi/config.json.
            organization_id: Organization ID for API requests. If not provided,
                will attempt to load from DATATURE_VI_ORGANIZATION_ID environment variable
                or from the configuration file.
            config_file: Path to configuration file containing credentials. Defaults
                to ~/datature/vi/config.json if not specified. The file should be JSON
                format with 'secret_key' and 'organization_id' fields.
            endpoint: API endpoint URL. Defaults to production API.
            logging_config: Custom logging configuration. If not provided, uses default
                configuration with environment-based overrides. Logs are automatically
                written to ~/.datature/vi/logs/ with timestamps.
            timeout: Timeout for HTTP requests. Defaults to 30 seconds.
            max_retries: Maximum number of retries for failed requests. Defaults to 3.
            max_connections: Maximum number of concurrent HTTP connections in the pool.
                Defaults to 100. Increase for high-concurrency workloads.
            max_keepalive_connections: Maximum number of keep-alive connections to maintain
                in the pool. Defaults to 20. Keep-alive connections improve performance
                for repeated requests.
            retry_config: Retry configuration for failed requests. Defaults to default
                retry configuration.

        Raises:
            ViConfigurationError: If credentials cannot be found or loaded from any source.
            ViAuthenticationError: If the provided credentials are invalid.
            FileNotFoundError: If a specified config_file path doesn't exist.

        Example:
            ```python
            import vi

            # Using explicit credentials
            client = vi.Client(
                secret_key="your-secret-key", organization_id="your-org-id"
            )

            # Using environment variables (DATATURE_VI_SECRET_KEY, DATATURE_VI_ORGANIZATION_ID)
            client = vi.Client()

            # Using custom config file
            client = vi.Client(config_file="./my-config.json")

            # With custom logging
            from vi.logging import LoggingConfig, LogLevel

            client = vi.Client(
                logging_config=LoggingConfig(level=LogLevel.DEBUG, enable_file=True)
            )
            ```

        Note:
            Credentials are loaded in the following priority order:
            1. Explicit parameters (secret_key, organization_id)
            2. Environment variables (DATATURE_VI_SECRET_KEY, DATATURE_VI_ORGANIZATION_ID)
            3. Configuration file (default: ~/datature/vi/config.json)

            A new log file with timestamp is created for each client instance to
            ensure proper isolation between runs.

        See Also:
            - [Authentication Guide](../getting-started/authentication.md): Complete authentication setup
            - [Configuration Guide](../getting-started/configuration.md): Advanced configuration options
            - `LoggingConfig`: Logging configuration options

        """
        # Load credentials from environment variables if not provided
        if secret_key is None:
            secret_key = os.getenv("DATATURE_VI_SECRET_KEY")
        if organization_id is None:
            organization_id = os.getenv("DATATURE_VI_ORGANIZATION_ID")
        if endpoint is None:
            endpoint = os.getenv("DATATURE_VI_API_ENDPOINT", DATATURE_VI_API_ENDPOINT)

        # Configure logging first - always create a new config to ensure fresh log file
        if logging_config is not None:
            # If user provided config, create a copy with fresh log file path
            runtime_config = replace(logging_config, log_file_path=None)
            configure_logging(runtime_config)
        else:
            # Use default configuration with environment overrides (will auto-generate log path)
            runtime_config = LoggingConfig()
            configure_logging(runtime_config)

        # Get logger for this client
        self._logger = get_logger("api.client", runtime_config or logging_config)

        # Log client initialization with log file location
        log_file_path = runtime_config.log_file_path if runtime_config else None
        self._logger.info(
            "Initializing Vi SDK client",
            endpoint=endpoint,
            has_secret_key=secret_key is not None,
            has_organization_id=organization_id is not None,
            has_config_file=config_file is not None,
            log_file_path=log_file_path,
        )

        self._auth = SecretKeyAuth(
            secret_key=secret_key,
            organization_id=organization_id,
            config_file=config_file,
        )

        # Create requester with connection pool configuration
        requester = Requester(
            auth=self._auth,
            base_url=endpoint,
            timeout=timeout,
            max_retries=max_retries,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            retry_config=retry_config,
        )

        super().__init__(requester)

    def get_model(
        self,
        run_id: str,
        ckpt: str | None = None,
        save_path: Path | str = DEFAULT_MODEL_DIR,
        overwrite: bool = False,
        show_progress: bool = True,
    ) -> ModelDownloadResult:
        """Download a trained model from a training run.

        This is a convenience method that downloads a model and returns the paths
        to the model files. The model can then be loaded for inference using the
        ViLoader class.

        Args:
            run_id: Training run identifier. Can be obtained from the platform
                or by listing runs via client.runs.list().
            ckpt: Checkpoint name to download. If None, downloads the latest
                checkpoint. Example: "epoch_10", "best_model".
            save_path: Directory to save the model. Defaults to
                ~/.datature/vi/models/. The model will be saved in a subdirectory
                named after the run_id.
            overwrite: Whether to overwrite existing model files. If False, existing
                files are skipped. If True, files are re-downloaded. Defaults to False.
            show_progress: Whether to display download progress bar. Set to False for
                non-interactive environments or CI/CD pipelines. Defaults to True.

        Returns:
            ModelDownloadResult object containing:
                - model_path: Path to the full model directory
                - adapter_path: Path to adapter directory (if available)
                - run_config_path: Path to run configuration file

        Raises:
            ViNotFoundError: If run_id or checkpoint not found.
            ViDownloadError: If download fails.
            ViPermissionError: If user lacks permission to access the model.

        Examples:
            Download latest model:

            >>> model = client.get_model(run_id="run_abc123")
            >>> print(f"Model path: {model.model_path}")
            Model path: /home/user/.datature/vi/models/run_abc123/model_full

            Download specific checkpoint:

            >>> model = client.get_model(
            ...     run_id="run_abc123", ckpt="epoch_10", save_path="./models"
            ... )

            Re-download existing model:

            >>> model = client.get_model(run_id="run_abc123", overwrite=True)

            Download without progress bar:

            >>> model = client.get_model(run_id="run_abc123", show_progress=False)

            Use for inference:

            >>> from vi.inference import ViModel
            >>>
            >>> model = ViModel(
            ...     secret_key="your-secret-key",
            ...     organization_id="your-organization-id",
            ...     run_id="run_abc123",
            ... )
            >>> result = model(source="test.jpg", user_prompt="Describe this image")

        Note:
            Large models may take time to download. Progress bars are shown
            by default. The download includes the model weights, adapter
            (if available), and configuration files needed for inference.

        See Also:
            - runs.models.download(): Lower-level download method
            - ViLoader: For loading models for inference
            - ViPredictor: For running inference

        """
        return self.models.download(run_id, ckpt, save_path, overwrite, show_progress)

    def get_dataset(
        self,
        dataset_id: str,
        dataset_export_id: str | None = None,
        annotations_only: bool = False,
        export_settings: DatasetExportSettings | dict = DatasetExportSettings(),
        save_dir: Path | str = DEFAULT_DATASET_EXPORT_DIR,
        overwrite: bool = False,
        show_progress: bool = True,
    ) -> DatasetDownloadResult:
        """Download a complete dataset with assets and annotations.

        This convenience method handles the entire dataset download workflow:
        creating an export (if needed), waiting for it to complete, and
        downloading the resulting archive. The dataset is extracted and
        organized into train/validation splits.

        Args:
            dataset_id: Dataset identifier. Can be obtained from the platform
                or by listing datasets via client.datasets.list().
            dataset_export_id: Existing export ID to download. If None, creates
                a new export with the specified export_settings.
            annotations_only: If True, downloads only annotations without assets.
                Useful for updating annotations on an existing local dataset.
                Automatically adjusts export format to VI_JSONL.
            export_settings: Export configuration as DatasetExportSettings object
                or dictionary. Controls format (VI_FULL or VI_JSONL), normalization,
                and train/validation split ratio.
            save_dir: Base directory for saving datasets. Dataset will be saved
                in a subdirectory named after the dataset_id. Defaults to
                ~/.datature/vi/datasets/
            overwrite: If True, overwrites existing dataset. If False and dataset
                exists, returns existing dataset without downloading.
            show_progress: If True, displays progress bars for download and
                extraction. Set to False for headless environments or CI/CD.

        Returns:
            DatasetDownloadResult object containing:
                - dataset_id: The dataset identifier
                - save_dir: Full path to the downloaded dataset directory

        Raises:
            ViNotFoundError: If dataset_id not found.
            ViDownloadError: If download or extraction fails.
            ViPermissionError: If user lacks permission to access dataset.
            ViValidationError: If export_settings are invalid.

        Examples:
            Basic download:

            >>> dataset = client.get_dataset(
            ...     dataset_id="dataset_abc123", save_dir="./data"
            ... )
            >>> print(f"Downloaded to: {dataset.save_dir}")
            Downloaded to: ./data/dataset_abc123

            Download with custom export settings:

            >>> from vi.api.resources.datasets.types import (
            ...     DatasetExportSettings,
            ...     DatasetExportFormat,
            ... )
            >>> settings = DatasetExportSettings(
            ...     format=DatasetExportFormat.VI_FULL, options={"split_ratio": 0.8}
            ... )
            >>> dataset = client.get_dataset(
            ...     dataset_id="dataset_abc123",
            ...     export_settings=settings,
            ...     save_dir="./data",
            ... )

            Download annotations only:

            >>> dataset = client.get_dataset(
            ...     dataset_id="dataset_abc123", annotations_only=True
            ... )

            Use existing export:

            >>> dataset = client.get_dataset(
            ...     dataset_id="dataset_abc123", dataset_export_id="export_xyz789"
            ... )

            Download without progress bars (CI/CD):

            >>> dataset = client.get_dataset(
            ...     dataset_id="dataset_abc123", show_progress=False
            ... )

            Load with ViDataset:

            >>> from vi.dataset.loaders import ViDataset
            >>> dataset = client.get_dataset(dataset_id="dataset_abc123")
            >>> loaded = ViDataset(dataset.save_dir)
            >>> for asset, annotations in loaded.training.iter_pairs():
            ...     # Process training data
            ...     pass

        Note:
            - Large datasets may take significant time to download
            - Downloaded datasets are cached; use overwrite=True to re-download
            - Dataset structure: save_dir/dataset_id/{training,validation,dump}/
            - Each split contains assets/ and annotations/ subdirectories
            - A metadata.json file is created with dataset information

        See Also:
            - ViDataset: For loading and iterating through downloaded datasets
            - datasets.download(): Lower-level download method
            - DatasetExportSettings: For configuring export format and options

        """
        if isinstance(export_settings, dict):
            export_settings = DatasetExportSettings(**export_settings)

        return self.datasets.download(
            dataset_id,
            dataset_export_id,
            annotations_only,
            export_settings,
            save_dir,
            overwrite,
            show_progress,
        )

    def close(self) -> None:
        """Close the client and release all resources.

        Closes the HTTP client, releases all connections, and cleans up
        all resources. This method is idempotent and can be called multiple
        times safely.

        Examples:
            Manual cleanup:

            ```python
            client = vi.Client(secret_key="...", organization_id="...")
            try:
                datasets = client.datasets.list()
            finally:
                client.close()
            ```

            Using context manager (recommended):

            ```python
            with vi.Client(secret_key="...", organization_id="...") as client:
                datasets = client.datasets.list()
                # Automatic cleanup on exit
            ```

        See Also:
            - Use context managers (`with` statement) for automatic cleanup
            - Call this explicitly in `finally` blocks if not using context managers

        """
        if not self._closed:
            self._logger.info("Closing Vi SDK client and releasing resources")

        # Call parent close method which handles the actual cleanup
        super().close()

        if self._closed:
            self._logger.debug("Vi SDK client closed successfully")

    def help(self) -> None:
        """Display quick reference guide for Vi SDK.

        Shows common operations, resource methods, and links to documentation.
        Perfect for discovering what's available without leaving your code.

        Example:
            ```python
            import vi

            client = vi.Client()
            client.help()  # Shows quick reference
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Vi SDK Quick Reference                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 COMMON OPERATIONS:

  List datasets (direct iteration):
    for dataset in client.datasets:
        print(dataset.name)

  List assets (with parameters):
    for asset in client.assets(dataset_id="your-dataset-id"):
        print(asset.filename)

  Upload assets:
    result = client.assets.upload(
        dataset_id="your-dataset-id",
        paths="./images/"
    )
    print(result.summary())

  Download dataset:
    dataset = client.get_dataset(
        dataset_id="your-dataset-id",
        save_dir="./data"
    )

  Run inference:
    from vi.inference import ViModel
    model = ViModel(run_id="your-run-id")
    result, error = model(source="image.jpg", user_prompt="Describe this image")

💡 DISCOVER MORE:

  Resource help (shows examples and supported operations):
    • client.datasets.help()     - Dataset operations
    • client.assets.help()        - Asset operations
    • client.annotations.help()   - Annotation operations
    • client.runs.help()          - Training runs
    • client.models.help()        - Model operations

  Inspect objects (shows rich detailed information):
    • asset.info()      - Display asset details (size, dimensions, annotations)
    • dataset.info()    - Display dataset statistics
    • run.info()        - Display training run information

📚 RESOURCES:

  Documentation:  https://vi.developers.datature.com/docs/vi-sdk
  Examples:       https://github.com/datature/Vi-SDK/tree/main/pypi/vi-sdk/examples/pypi/vi-sdk/examples

🐛 SUPPORT:

  Report bugs:    https://github.com/datature/Vi-SDK/issues
  Email:          developers@datature.io

"""
        print(help_text)
