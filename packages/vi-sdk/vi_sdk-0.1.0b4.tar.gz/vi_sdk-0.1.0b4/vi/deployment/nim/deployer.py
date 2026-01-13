#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   deployer.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Main NIM deployer class for container lifecycle management.
"""

import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import docker
import docker.errors
from docker.errors import APIError
from msgspec import Struct
from vi.api.client import ViClient
from vi.api.resources.models.results import ModelDownloadResult
from vi.consts import (
    DEFAULT_ADAPTER_DIR_NAME,
    DEFAULT_MODEL_DIR_NAME,
    DEFAULT_RUN_CONFIG_FILE_NAME,
)
from vi.deployment.nim.config import NIMConfig
from vi.deployment.nim.exceptions import (
    ContainerExistsError,
    InvalidConfigError,
    ModelIncompatibilityError,
)
from vi.deployment.nim.utils import (
    ConsoleUI,
    LayerProgress,
    format_bytes,
    get_available_models,
    get_status_color,
    stream_container_logs,
    wait_for_service_ready,
)

# Constants
API_KEY_PREFIX = "nvapi-"
DEFAULT_NIM_REGISTRY = "nvcr.io/nim/nvidia"
SUPPORTED_MODEL_IMAGES = ["cosmos-reason1-7b"]
DEFAULT_SERVICE_TIMEOUT = 600  # 10 minutes


class NIMDeploymentResult(Struct, kw_only=True):
    """Result of NIM container deployment.

    Attributes:
        container_id: The Docker container ID.
        container_name: The name of the running container.
        served_model_name: The name the model is served as (if using custom weights).
        port: The port the container is exposed on.
        available_models: List of model IDs available in the container.

    """

    container_id: str
    container_name: str
    served_model_name: str | None
    port: int
    available_models: list[str] | None = None


class NIMDeployer:
    """Manages NVIDIA NIM container deployment lifecycle.

    This class handles the complete lifecycle of NIM container deployment including:
    - Image pulling from NVIDIA Container Registry
    - Container creation and configuration
    - Service readiness monitoring
    - Container cleanup

    Environment Variables:
        NGC_API_KEY: NVIDIA NGC API key (if config not provided)
        DATATURE_VI_SECRET_KEY: Datature Vi secret key (if not in config)
        DATATURE_VI_ORGANIZATION_ID: Datature Vi organization ID (if not in config)

    Attributes:
        config: The deployment configuration.

    Example:
        ```python
        from vi.deployment.nim import NIMDeployer, NIMConfig

        # Create deployer with default config (uses NGC_API_KEY env var)
        deployer = NIMDeployer()

        # Or with custom config
        config = NIMConfig(
            nvidia_api_key="nvapi-...",
            port=8080,
            stream_logs=False,
        )
        deployer = NIMDeployer(config)

        # Deploy with verbose output (default)
        result = deployer.deploy()
        print(f"Container running on port {result.port}")

        # No console output
        deployer = NIMDeployer(config, quiet=True)
        result = deployer.deploy()
        ```

    """

    def __init__(
        self,
        config: NIMConfig | None = None,
        quiet: bool = False,
    ):
        """Initialize NIM deployer.

        Args:
            config: Deployment configuration. If None, uses default configuration
                with nvidia_api_key from environment variable NGC_API_KEY.
            quiet: If True, suppresses all console output. Defaults to False.

        Raises:
            InvalidConfigError: If config is None and NGC_API_KEY env var is not set.

        """
        # Use default config if none provided
        if config is None:
            api_key = os.environ.get("NGC_API_KEY")
            if not api_key:
                raise InvalidConfigError(
                    "No config provided and NGC_API_KEY environment variable not set. "
                    "Either provide a NIMConfig or set NGC_API_KEY environment variable."
                )
            config = NIMConfig(nvidia_api_key=api_key)

        self.config = config
        self._ui = ConsoleUI(quiet=quiet)

    @contextmanager
    def _docker_client(self):
        """Context manager for Docker client lifecycle.

        Yields:
            docker.DockerClient: A Docker client instance.

        """
        client = docker.from_env()
        try:
            yield client
        finally:
            client.close()

    def _validate_config(self) -> None:
        """Validate deployment configuration.

        Raises:
            InvalidConfigError: If configuration is invalid.

        """
        if not self.config.nvidia_api_key.startswith(API_KEY_PREFIX):
            raise InvalidConfigError(
                f"API key must start with '{API_KEY_PREFIX}'. "
                f"Expected format: {API_KEY_PREFIX}..."
            )

        if self.config.image_name not in SUPPORTED_MODEL_IMAGES:
            raise InvalidConfigError(
                f"Unsupported image '{self.config.image_name}'. "
                f"Supported images: {', '.join(SUPPORTED_MODEL_IMAGES)}"
            )

    def _login_to_registry(self, client: docker.DockerClient) -> None:
        """Login to NVIDIA Container Registry.

        Args:
            client: Docker client instance.

        Raises:
            APIError: If login fails.

        """
        try:
            client.login(
                username="$oauthtoken",
                password=self.config.nvidia_api_key,
                registry="nvcr.io",
            )
        except APIError as e:
            raise APIError(f"Failed to authenticate with nvcr.io: {e}") from e

    def _check_image_exists(self, client: docker.DockerClient, image_name: str) -> bool:
        """Check if an image exists locally.

        Args:
            client: Docker client instance.
            image_name: Full image name to check.

        Returns:
            True if image exists locally, False otherwise.

        """
        try:
            client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False
        except docker.errors.APIError:
            # If API error, assume image doesn't exist
            return False

    def _pull_image(self, client: docker.DockerClient, image_name: str) -> None:
        """Pull NIM image from registry with progress tracking.

        Skips pulling if image exists locally and force_pull is False.

        Args:
            client: Docker client instance.
            image_name: Full image name to pull.

        Raises:
            APIError: If image pull fails.

        """
        # Check if image exists and skip pull if not forcing
        if not self.config.force_pull and self._check_image_exists(client, image_name):
            self._ui.show_success(
                f"Image {image_name} already exists locally (skipping pull)"
            )
            self._ui.show_info(
                "Use force_pull=True in NIMConfig to re-pull the image\n"
            )
            return

        self._ui.show_info(f"Pulling image: {image_name}\n")

        try:
            layers: dict[str, LayerProgress] = {}
            layer_tasks: dict[str, Any] = {}

            with self._ui.progress_context() as progress:
                for line in client.api.pull(image_name, stream=True, decode=True):
                    layer_id = line.get("id")
                    status = line.get("status", "")
                    progress_detail = line.get("progressDetail", {})
                    current = progress_detail.get("current", 0)
                    total = progress_detail.get("total", 0)

                    # Handle layer-specific progress
                    if layer_id:
                        # Initialize layer if new
                        if layer_id not in layers:
                            layers[layer_id] = LayerProgress(layer_id)
                            if total > 0:
                                layer_tasks[layer_id] = progress.add_task(
                                    f"[dim]{layer_id:>12}[/dim] {status}",
                                    total=total,
                                )
                            else:
                                layer_tasks[layer_id] = progress.add_task(
                                    f"[dim]{layer_id:>12}[/dim] {status}",
                                    total=100,
                                    completed=0,
                                )

                        # Update layer progress
                        layer = layers[layer_id]
                        layer.update(status, current, total)

                        # Update the progress bar for this layer
                        if layer_id in layer_tasks:
                            color = get_status_color(status)
                            speed_str = ""
                            if layer.speed > 0 and "downloading" in status.lower():
                                speed_str = f" @ {format_bytes(int(layer.speed))}/s"

                            size_str = ""
                            if layer.total > 0:
                                size_str = (
                                    f" ({format_bytes(layer.current)}/"
                                    f"{format_bytes(layer.total)})"
                                )

                            desc_text = f"{layer_id:>12} {status}{size_str}{speed_str}"
                            description = (
                                f"[dim]{layer_id:>12}[/dim] [{color}]{status}[/{color}]"
                                f"{size_str}{speed_str}{' ' * max(0, 80 - len(desc_text))}"
                            )

                            if layer.total > 0:
                                progress.update(
                                    layer_tasks[layer_id],
                                    completed=layer.current,
                                    total=layer.total,
                                    description=description,
                                )
                            else:
                                progress.update(
                                    layer_tasks[layer_id],
                                    completed=0,
                                    total=100,
                                    description=description,
                                )

            self._ui.show_success(f"Successfully pulled {image_name}\n")

            # Display summary
            total_size = sum(
                layer.total for layer in layers.values() if layer.total > 0
            )
            self._ui.show_info("Summary:")
            self._ui.show_info(f"  Total layers: {len(layers)}")
            self._ui.show_info(f"  Total size: {format_bytes(total_size)}")

            # Verify the image was pulled
            client.images.get(image_name)

        except APIError as e:
            raise APIError(f"Failed to pull image {image_name}: {e}") from e

    def _setup(self) -> str:
        """Set up NVIDIA NIM by pulling the model image.

        This method:
        1. Validates the configuration
        2. Authenticates with NVIDIA Container Registry
        3. Pulls the specified NIM image

        Returns:
            The full image name that was pulled.

        Raises:
            InvalidConfigError: If configuration is invalid.
            APIError: If Docker operations fail.

        """
        with self._docker_client() as client:
            with self._ui.progress_context() as progress:
                # Step 1: Validate inputs
                validate_task = progress.add_task("[cyan]Validating inputs...", total=2)
                self._validate_config()
                progress.advance(validate_task)
                progress.advance(validate_task)
                progress.update(
                    validate_task, description="[green]✓ Validation complete"
                )

                # Step 2: Login to registry
                login_task = progress.add_task(
                    "[cyan]Authenticating with nvcr.io...", total=1
                )
                self._login_to_registry(client)
                progress.advance(login_task)
                progress.update(
                    login_task, description="[green]✓ Successfully authenticated"
                )

            # Step 3: Pull image (outside progress context for detailed layer progress)
            full_image = (
                f"{DEFAULT_NIM_REGISTRY}/{self.config.image_name}:{self.config.tag}"
            )
            self._pull_image(client, full_image)

            return full_image

    def _get_container_name(self, image_name: str) -> str:
        """Derive container name from image name.

        Args:
            image_name: Full image name.

        Returns:
            Container name derived from image.

        """
        return image_name.split("/")[-1].split(":")[0]

    def _get_existing_container(
        self, client: docker.DockerClient, container_name: str
    ) -> docker.models.containers.Container | None:
        """Get existing container by name.

        Args:
            client: Docker client instance.
            container_name: Name of container to find.

        Returns:
            Container object if found, None otherwise.

        """
        try:
            return client.containers.get(container_name)
        except docker.errors.NotFound:
            return None

    def _reuse_container(
        self,
        container: docker.models.containers.Container,
        container_name: str,
        custom_weights_path: str | None,
        served_model_name: str | None,
    ) -> NIMDeploymentResult:
        """Reuse an existing container.

        Args:
            container: Existing container object.
            container_name: Name of the container.
            custom_weights_path: Path to custom weights.
            served_model_name: Model name being served.

        Returns:
            Deployment result for existing container.

        """
        self._ui.show_info(f"Using existing container '{container_name}'")
        self._ui.show_info(f"Container ID: {container.id}")
        self._ui.show_info(f"Container name: {container_name}")
        self._ui.show_info(f"Status: {container.status}")

        if custom_weights_path:
            self._ui.show_info(f"Custom weights: {custom_weights_path}")
        if served_model_name:
            self._ui.show_info(f"Served model name: {served_model_name}")

        # Check if service is ready
        available_models = None
        if container.status == "running":
            self._ui.show_info("Checking if NIM service is ready...")

            if wait_for_service_ready(self.config.port, timeout=30):
                self._ui.show_success("NIM service is ready")
                available_models = get_available_models(self.config.port)
            else:
                self._ui.show_warning("Could not confirm service readiness")

        return NIMDeploymentResult(
            container_id=container.id,
            container_name=container_name,
            served_model_name=served_model_name,
            port=self.config.port,
            available_models=available_models,
        )

    def _remove_container(self, container: docker.models.containers.Container) -> None:
        """Stop and remove a container.

        Args:
            container: Container to remove.

        Raises:
            APIError: If removal fails.

        """
        container_name = container.name
        self._ui.show_warning(
            f"Stopping and removing existing container '{container_name}'..."
        )

        try:
            container.stop()
            container.remove()
            self._ui.show_success(f"Container '{container_name}' removed\n")
        except APIError as e:
            # Handle concurrent removal
            if "removal of container" in str(e) and "already in progress" in str(e):
                self._ui.show_warning(
                    f"Container '{container_name}' is already being removed. Waiting..."
                )
                self._wait_for_removal(container_name)
            else:
                raise

    def _wait_for_removal(self, container_name: str) -> None:
        """Wait for container removal to complete.

        Args:
            container_name: Name of container being removed.

        Raises:
            APIError: If timeout waiting for removal.

        """
        max_wait = 30
        waited = 0

        with self._docker_client() as client:
            while waited < max_wait:
                try:
                    client.containers.get(container_name)
                    time.sleep(0.5)
                    waited += 0.5
                except docker.errors.NotFound:
                    self._ui.show_success(f"Container '{container_name}' removed\n")
                    return

        # Timeout
        raise APIError(
            f"Timeout waiting for container '{container_name}' removal after {max_wait} seconds. "
            f"Please manually remove: docker rm -f {container_name}"
        )

    def _create_container(
        self,
        client: docker.DockerClient,
        image_name: str,
        container_name: str,
        custom_weights_path: str | None,
        served_model_name: str | None,
    ) -> docker.models.containers.Container:
        """Create and start a new container.

        Args:
            client: Docker client instance.
            image_name: Full image name to run.
            container_name: Name for the container.
            custom_weights_path: Optional path to custom weights.
            served_model_name: Optional model name to serve.

        Returns:
            Created container object.

        Raises:
            APIError: If container creation fails.

        """
        # Prepare environment variables
        environment = {
            "NGC_API_KEY": self.config.nvidia_api_key,
            "NIM_MAX_MODEL_LEN": self.config.max_model_len,
        }

        if served_model_name:
            environment["NIM_SERVED_MODEL_NAME"] = served_model_name

        if custom_weights_path:
            environment["NIM_MODEL_NAME"] = custom_weights_path

        # Prepare volume mounts
        volumes = {}

        # Set up cache directory
        local_cache_dir = self.config.local_cache_dir
        if local_cache_dir is None:
            local_cache_dir = str(Path.home() / ".cache" / "nim")
            Path(local_cache_dir).mkdir(parents=True, exist_ok=True)

        volumes[local_cache_dir] = {"bind": "/opt/nim/.cache", "mode": "rw"}

        # Mount custom weights if provided
        if custom_weights_path:
            volumes[custom_weights_path] = {
                "bind": custom_weights_path,
                "mode": "ro",
            }

        # Get current user ID
        user_id = os.getuid()

        # Create container
        self._ui.show_info(f"Creating container '{container_name}'...")

        container = client.containers.run(
            image=image_name,
            name=container_name,
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ],
            shm_size=self.config.shm_size,
            environment=environment,
            volumes=volumes,
            user=str(user_id),
            ports={f"{self.config.port}/tcp": self.config.port},
            detach=True,
            remove=True,
            stdin_open=True,
            tty=True,
        )

        self._ui.show_success(
            f"Container '{container_name}' started (ID: {container.short_id})"
        )

        return container

    def _wait_for_ready(
        self,
        container: docker.models.containers.Container,
        container_name: str,
        custom_weights_path: str | None,
        served_model_name: str | None,
    ) -> NIMDeploymentResult:
        """Wait for NIM service to be ready.

        Args:
            container: Docker container object.
            container_name: Name of the container.
            custom_weights_path: Path to custom weights.
            served_model_name: Model name being served.

        Returns:
            Deployment result with container information.

        """
        # Stream container logs if requested
        log_stream_active = None
        if self.config.stream_logs:
            self._ui.show_info("\nContainer logs:")
            self._ui.show_info("─" * 80)

            log_stream_active = threading.Event()
            log_stream_active.set()

            log_thread = threading.Thread(
                target=stream_container_logs,
                args=(container, log_stream_active, self._ui.console),
                daemon=True,
            )
            log_thread.start()

        # Wait for NIM service to be ready
        self._ui.show_info("\n⏳ Waiting for NIM service to be ready...")

        available_models = None
        if wait_for_service_ready(self.config.port, timeout=DEFAULT_SERVICE_TIMEOUT):
            self._ui.show_success("NIM service is ready")

            # Fetch available models
            self._ui.show_info("Fetching available models...")
            available_models = get_available_models(self.config.port)
        else:
            self._ui.show_warning("Service readiness check timed out")
            self._ui.show_warning(
                "NIM service may still be initializing. "
                "The container is running but the service might need more time to start."
            )
            self._ui.show_warning(f"Check container logs: docker logs {container_name}")

        # Stop log streaming
        if self.config.stream_logs and log_stream_active is not None:
            log_stream_active.clear()
            time.sleep(0.5)
            self._ui.show_info("─" * 80 + "\n")

        self._ui.show_success(f"Container is running on port {self.config.port}")
        self._ui.show_info(f"Container ID: {container.id}")
        self._ui.show_info(f"Container name: {container_name}")

        if custom_weights_path:
            self._ui.show_info(f"Custom weights: {custom_weights_path}")
        if served_model_name:
            self._ui.show_info(f"Served model name: {served_model_name}")
        if available_models:
            self._ui.show_info(f"Available models: {', '.join(available_models)}")

        return NIMDeploymentResult(
            container_id=container.id,
            container_name=container_name,
            served_model_name=served_model_name,
            port=self.config.port,
            available_models=available_models,
        )

    def _run(
        self,
        image_name: str,
        custom_weights_path: str | None = None,
        served_model_name: str | None = None,
    ) -> NIMDeploymentResult:
        """Run a NIM container with the specified configuration.

        Args:
            image_name: Full Docker image path to run.
            custom_weights_path: Optional path to custom model weights.
            served_model_name: Optional name to serve the model as.

        Returns:
            Deployment result with container information.

        Raises:
            ContainerExistsError: If container exists and not configured to reuse/kill.
            APIError: If Docker operations fail.

        """
        with self._docker_client() as client:
            container_name = self._get_container_name(image_name)

            # Check for existing container
            existing = self._get_existing_container(client, container_name)

            if existing:
                if self.config.use_existing_container:
                    return self._reuse_container(
                        existing, container_name, custom_weights_path, served_model_name
                    )

                if self.config.auto_kill_existing_container:
                    self._ui.show_warning(
                        "auto_kill_existing_container is enabled. "
                        "Any existing container with conflicting name will be removed.\n"
                    )
                    self._remove_container(existing)
                else:
                    raise ContainerExistsError(container_name)

            # Create and start container
            container = self._create_container(
                client,
                image_name,
                container_name,
                custom_weights_path,
                served_model_name,
            )

            # Monitor and wait for readiness
            return self._wait_for_ready(
                container, container_name, custom_weights_path, served_model_name
            )

    def _download_model(self) -> ModelDownloadResult:
        """Download model from Datature Vi platform.

        Uses custom weights configuration from self.config.

        Returns:
            Model download result with paths.

        """
        model_dir = (
            Path(self.config.model_save_path)
            / self.config.run_id
            / DEFAULT_MODEL_DIR_NAME
        )

        # Check if model already exists
        if model_dir.exists() and not self.config.overwrite:
            adapter_dir = model_dir.parent / DEFAULT_ADAPTER_DIR_NAME
            run_config_path = model_dir / DEFAULT_RUN_CONFIG_FILE_NAME

            return ModelDownloadResult(
                model_path=str(model_dir),
                adapter_path=str(adapter_dir) if adapter_dir.exists() else None,
                run_config_path=(
                    str(run_config_path) if run_config_path.exists() else None
                ),
            )

        client_kwargs = {}
        if self.config.secret_key is not None:
            client_kwargs["secret_key"] = self.config.secret_key
        if self.config.organization_id is not None:
            client_kwargs["organization_id"] = self.config.organization_id

        client = ViClient(**client_kwargs)

        return client.get_model(
            run_id=self.config.run_id,
            ckpt=self.config.ckpt,
            save_path=str(self.config.model_save_path),
            overwrite=self.config.overwrite,
        )

    def deploy(self) -> NIMDeploymentResult:
        """Complete deployment: setup image + download model + run container.

        This is the main entry point for full NIM deployment. It handles:
        1. Pulling the NIM image from NVIDIA Container Registry
        2. (Optional) Downloading custom model weights from Datature Vi (if run_id is provided)
        3. Starting the container with appropriate configuration
        4. Monitoring service readiness

        Returns:
            Deployment result with container information.

        Raises:
            InvalidConfigError: If configuration is invalid.
            ContainerExistsError: If container exists and not configured to reuse/kill.
            ModelIncompatibilityError: If custom model is incompatible with container.
            APIError: If Docker operations fail.

        Example:
            ```python
            from vi.deployment.nim import NIMDeployer, NIMConfig

            # Deploy with custom weights (explicit credentials)
            config = NIMConfig(
                nvidia_api_key="nvapi-...",
                secret_key="your-key",
                organization_id="your-org",
                run_id="your-run-id",
            )
            deployer = NIMDeployer(config)
            result = deployer.deploy()
            print(f"Deployed on port {result.port}")
            print(f"Serving model: {result.served_model_name}")

            # Deploy with custom weights (using environment variables)
            # Set DATATURE_VI_SECRET_KEY and DATATURE_VI_ORGANIZATION_ID environment variables
            config = NIMConfig(
                nvidia_api_key="nvapi-...",
                run_id="your-run-id",  # Vi credentials loaded from env
            )
            deployer = NIMDeployer(config)
            result = deployer.deploy()

            # Deploy with default model (no custom weights)
            config = NIMConfig(nvidia_api_key="nvapi-...")
            deployer = NIMDeployer(config)
            result = deployer.deploy()
            ```

        """
        # Step 1: Pull the NIM image
        full_image = self._setup()

        # Step 2: Download model if run_id is provided
        custom_weights_path = None
        served_model_name = None

        if self.config.run_id:
            model_meta = self._download_model()
            custom_weights_path = model_meta.model_path

            # Default served_model_name to image_name when using custom weights
            served_model_name = self.config.served_model_name or self.config.image_name

        # Step 3: Run the container
        try:
            return self._run(full_image, custom_weights_path, served_model_name)
        except APIError as e:
            # Provide context if model incompatibility is likely
            error_msg = str(e)
            if custom_weights_path and any(
                keyword in error_msg.lower()
                for keyword in ["model", "architecture", "incompatible"]
            ):
                self._ui.show_warning("\nContainer failed to start with custom weights")
                self._ui.show_warning(
                    "This may indicate model incompatibility with the container."
                )
                self._ui.show_warning(
                    f"Container '{self.config.image_name}' only supports specific "
                    "model architectures. Visit "
                    "https://docs.nvidia.com/nim/vision-language-models/latest/support-matrix.html"
                    " for more information."
                )
                raise ModelIncompatibilityError(
                    self.config.image_name, details=error_msg
                ) from e
            raise

    @classmethod
    def stop(cls, container_name: str, quiet: bool = False) -> bool:
        """Stop a NIM container.

        Args:
            container_name: Name or ID of the container to stop.
            quiet: If True, suppresses console output. Defaults to False.

        Returns:
            True if container was successfully stopped and removed, False if not found.

        Raises:
            docker.errors.DockerException: If Docker operations fail.

        Example:
            ```python
            # No need to initialize deployer
            success = NIMDeployer.stop("cosmos-reason1-7b")
            if success:
                print("Container stopped successfully")

            # Or with quiet mode
            NIMDeployer.stop("cosmos-reason1-7b", quiet=True)
            ```

        """
        ui = ConsoleUI(quiet=quiet)
        client = docker.from_env()
        try:
            try:
                container = client.containers.get(container_name)
                ui.show_info(f"Stopping container '{container_name}'...")
                container.stop()
                ui.show_success(f"Container '{container_name}' stopped")
                return True
            except docker.errors.NotFound:
                ui.show_warning(f"Container '{container_name}' not found")
                return False
        finally:
            client.close()
