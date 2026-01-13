#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   downloader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK models downloader module.
"""

import tarfile
from pathlib import Path

from rich.progress import BarColumn
from vi.api.resources.managers import ResourceDownloader
from vi.api.resources.models.results import ModelDownloadResult
from vi.consts import (
    DEFAULT_ADAPTER_DIR_NAME,
    DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_DIR_NAME,
)
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress

DEFAULT_RUN_CONFIG_FILE_NAME = "run.json"


class ModelDownloader(ResourceDownloader):
    """Download fine-tuned models with resume support and integrity validation.

    Downloads model archives from the Datature Vi platform including full model weights,
    optional adapter weights (for LoRA/QLoRA fine-tuning), and run configuration files.
    Inherits parallel download and resume capabilities from ResourceDownloader.

    The downloader automatically extracts model files into a structured directory format
    and validates the presence of required components (model weights, config files).

    """

    def download(
        self,
        run_id: str,
        download_url: str,
        save_dir: Path | str = DEFAULT_MODEL_DIR,
    ) -> ModelDownloadResult | None:
        """Download and extract a fine-tuned model from a training run.

        Downloads a model archive, extracts it, and returns paths to the model
        components. If the model already exists and overwrite=False, returns
        existing paths without re-downloading. Supports resumable downloads
        for large model files.

        Args:
            run_id: Unique identifier of the training run that produced the model.
            download_url: Pre-signed URL to download the model archive from.
            save_dir: Base directory where models are saved. The model will be
                saved in a subdirectory named after the run_id. Defaults to
                ~/.datature/vi/models/.

        Returns:
            ModelDownloadResult object containing paths to:
            - model_path: Directory with full model weights (.safetensors files)
            - adapter_path: Directory with adapter weights (if LoRA/QLoRA was used)
            - run_config_path: JSON file with training configuration and metadata
            Returns None if the download was cancelled by the user.

        Raises:
            ValueError: If the downloaded archive doesn't contain required model files
                or if extraction fails.
            PermissionError: If unable to write to the save directory.
            OSError: If insufficient disk space or network issues occur.

        Example:
            ```python
            from vi.api.resources.models.downloader import ModelDownloader
            from pathlib import Path

            # Create downloader with progress display
            downloader = ModelDownloader(show_progress=True, overwrite=False)

            # Download model
            result = downloader.download(
                run_id="run_abc123",
                download_url="https://example.com/model.tar",
                save_dir=Path("./models"),
            )

            if result is None:
                print("Download was cancelled")
            else:
                print(f"Model weights: {result.model_path}")
                print(f"Adapter weights: {result.adapter_path}")
                print(f"Run config: {result.run_config_path}")
            ```

        Note:
            If overwrite=False and a valid model already exists at the destination,
            the download is skipped and existing paths are returned immediately.
            The download can be safely interrupted and resumed later.

        See Also:
            - `ResourceDownloader`: Base class with parallel download capabilities
            - [Model Guide](../../guide/models.md): Model download and usage best practices

        """
        save_path = Path(save_dir) / run_id
        absolute_save_path = Path(save_path).resolve()

        if not self._overwrite and absolute_save_path.exists():
            try:
                model_path, adapter_path, run_config_path = self._find_model_paths(
                    absolute_save_path
                )
                return ModelDownloadResult(
                    model_path=str(model_path),
                    adapter_path=str(adapter_path) if adapter_path else None,
                    run_config_path=str(run_config_path),
                )
            except ValueError:
                pass

        result = self._download_and_extract(download_url, absolute_save_path)

        if result is None:
            return None

        model_path, adapter_path, run_config_path = result

        return ModelDownloadResult(
            model_path=str(model_path),
            adapter_path=str(adapter_path) if adapter_path else None,
            run_config_path=str(run_config_path),
        )

    def _download_and_extract(
        self, download_url: str, save_path: Path
    ) -> tuple[Path, Path | None, Path] | None:
        """Download and extract model archive with resumable downloads and cleanup.

        Downloads the model TAR archive using resumable chunk-based download,
        extracts all contents, validates the structure, and cleans up temporary
        files only after successful completion.

        Args:
            download_url: Pre-signed URL to download the model archive from.
            save_path: Directory where the model will be extracted.

        Returns:
            Tuple of (model_path, adapter_path, run_config_path) where:
            - model_path: Directory containing model weights
            - adapter_path: Directory containing adapter weights (or None if not present)
            - run_config_path: Path to run configuration JSON file
            Returns None if the download was cancelled by the user.

        Raises:
            ValueError: If the archive doesn't contain required model files.

        """
        save_path.mkdir(parents=True, exist_ok=True)

        temp_path = save_path / ".download_temp.tar"

        try:
            # Use resumable download for large model files
            self._download_file(download_url, temp_path, "Downloading model")

            model_path, adapter_path, run_config_path = self._extract_archive(
                temp_path, save_path
            )

            # Clean up ONLY on success (after extraction completes)
            if temp_path.exists():
                temp_path.unlink()

            # Clean up manifest file on success
            manifest_path = temp_path.with_suffix(temp_path.suffix + ".manifest")
            if manifest_path.exists():
                manifest_path.unlink()

            return model_path, adapter_path, run_config_path

        except ValueError as e:
            raise ValueError(f"Error extracting model: {e}") from e

    def _extract_archive(
        self, archive_path: Path, extract_to: Path
    ) -> tuple[Path, Path | None, Path]:
        """Extract TAR archive with progress tracking and cancellation support.

        Extracts all members from the TAR archive with optional progress bar
        showing extraction status. Supports graceful cancellation via signal
        handler for user interrupts.

        Args:
            archive_path: Path to the TAR archive file.
            extract_to: Directory where contents will be extracted.

        Returns:
            Tuple of (model_path, adapter_path, run_config_path) after extraction.

        """
        with graceful_exit("Model extraction cancelled by user") as handler:
            with tarfile.open(archive_path, "r:*") as tar:
                members = tar.getmembers()

                if self._show_progress:
                    with ViProgress(
                        "[progress.description]{task.description}",
                        BarColumn(),
                        "[progress.percentage]{task.percentage:>3.2f}%",
                    ) as progress:
                        task = progress.add_task("Extracting model", total=len(members))
                        for member in members:
                            if handler.exit_now:
                                progress.update(
                                    task, description="✗ Extraction cancelled"
                                )
                                break
                            tar.extract(member, extract_to)
                            progress.update(task, advance=1)
                        else:
                            progress.update(
                                task,
                                description="✓ Extraction complete!",
                                completed=len(members),
                                refresh=True,
                            )

                else:
                    for member in members:
                        if handler.exit_now:
                            break
                        tar.extract(member, extract_to)

        return self._find_model_paths(extract_to)

    def _find_model_paths(self, base_path: Path) -> tuple[Path, Path | None, Path]:
        """Find and validate model component paths in extracted directory.

        Searches for required model components (weights, config) and optional
        adapter weights in the expected directory structure. Validates that
        model weights (.safetensors files) and configuration exist.

        Args:
            base_path: Root directory of the extracted model.

        Returns:
            Tuple of (model_path, adapter_path, run_config_path) where:
            - model_path: Directory containing .safetensors model files
            - adapter_path: Directory containing adapter files (or None)
            - run_config_path: Path to run.json configuration file

        Raises:
            ValueError: If required model directory or config file is missing
                or if no .safetensors files are found.

        """
        model_path = base_path / DEFAULT_MODEL_DIR_NAME
        if not (
            model_path.exists()
            and model_path.is_dir()
            and any(p.suffix == ".safetensors" for p in model_path.iterdir())
        ):
            raise ValueError(f"Model directory {model_path} does not exist")

        adapter_path_candidate = base_path / DEFAULT_ADAPTER_DIR_NAME
        adapter_path: Path | None = (
            adapter_path_candidate
            if (adapter_path_candidate.exists() and adapter_path_candidate.is_dir())
            else None
        )

        run_config_path = model_path / DEFAULT_RUN_CONFIG_FILE_NAME
        if not (run_config_path.exists() and run_config_path.is_file()):
            raise ValueError(f"Run config file {run_config_path} does not exist")

        return model_path, adapter_path, run_config_path
