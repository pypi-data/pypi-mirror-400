#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   downloader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK datasets downloader module.
"""

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import msgspec
from rich.progress import BarColumn
from vi.api.resources.datasets.results import DatasetDownloadResult
from vi.api.resources.datasets.types import DatasetExportMetadata
from vi.api.resources.managers import ResourceDownloader
from vi.consts import DEFAULT_DATASET_EXPORT_DIR
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress


class DatasetDownloader(ResourceDownloader):
    """Download a dataset."""

    def download(
        self,
        organization_id: str,
        dataset_id: str,
        download_url: str,
        save_dir: Path | str = DEFAULT_DATASET_EXPORT_DIR,
    ) -> DatasetDownloadResult:
        """Download and extract a dataset from a URL.

        Downloads a dataset archive from the provided URL, extracts it to the
        specified directory, and creates metadata files for local access.
        Handles progress tracking, error recovery, and existing dataset detection.

        Args:
            organization_id: The organization ID that owns the dataset.
            dataset_id: The unique identifier of the dataset being downloaded.
            download_url: The URL to download the dataset archive from.
            save_dir: Directory where the dataset will be saved. The dataset
                will be saved in a subdirectory named after the dataset_id.
                Defaults to ~/.datature/vi/dataset_exports/.

        Returns:
            DatasetDownloadResult object containing the dataset ID and the path
            where the dataset was saved.

        Raises:
            PermissionError: If unable to write to the save directory.
            OSError: If insufficient disk space or network issues occur.
            ValueError: If the download URL is invalid or expired.

        Example:
            ```python
            from vi.api.resources.datasets.downloader import DatasetDownloader
            from pathlib import Path

            # Create downloader with progress display
            downloader = DatasetDownloader(show_progress=True, overwrite=False)

            # Download dataset
            result = downloader.download(
                organization_id="org_123",
                dataset_id="dataset_abc",
                download_url="https://example.com/dataset.zip",
                save_dir=Path("./downloads"),
            )

            print(f"Dataset saved to: {result.save_dir}")
            print(f"Dataset ID: {result.dataset_id}")
            ```

        Note:
            If overwrite=False and the dataset already exists, returns information
            about the existing dataset without re-downloading. The download includes
            assets, annotations, and metadata in a structured format.

        See Also:
            - `DatasetDownloader.__init__()`: Configure download behavior
            - [Dataset Guide](../../guide/datasets.md): Dataset export and download best practices

        """
        absolute_save_path = (Path(save_dir) / dataset_id).resolve()

        if not self._overwrite and absolute_save_path.exists():
            existing_dataset = self._check_existing_dataset(absolute_save_path)
            if existing_dataset:
                return existing_dataset

        self._download_and_extract(download_url, absolute_save_path)
        self._create_metadata(organization_id, dataset_id, absolute_save_path)

        return DatasetDownloadResult(
            dataset_id=dataset_id, save_dir=str(absolute_save_path)
        )

    def _check_existing_dataset(self, path: Path) -> DatasetDownloadResult | None:
        """Check if dataset already exists at path.

        Args:
            path: The path to check for existing dataset.

        Returns:
            DatasetDownloadResult object containing the dataset ID and the path
            where the dataset was saved.

        """
        if not path.exists() or not list(path.iterdir()):
            return None

        return DatasetDownloadResult(dataset_id=path.stem, save_dir=str(path))

    def _download_and_extract(self, download_url: str, save_path: Path) -> None:
        """Download and extract dataset.

        Args:
            download_url: The URL to download the dataset from.
            save_path: The path to save the dataset to.

        """
        save_path.mkdir(parents=True, exist_ok=True)

        temp_path = save_path / ".download_temp.zip"

        try:
            self._download_file(download_url, temp_path, "Downloading dataset")
            self._extract_archive(temp_path, save_path)

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            # Clean up manifest file
            manifest_path = temp_path.with_suffix(temp_path.suffix + ".manifest")
            if manifest_path.exists():
                manifest_path.unlink()

    def _extract_archive(self, archive_path: Path, extract_to: Path) -> Path:
        """Extract dataset.

        Args:
            archive_path: The path to the archive to extract.
            extract_to: The path to extract the archive to.

        Returns:
            The path to the extracted archive.

        """
        with graceful_exit("Dataset extraction cancelled by user") as handler:
            with ZipFile(archive_path, "r") as zip_ref:
                members = zip_ref.infolist()

                if self._show_progress:
                    with ViProgress(
                        "[progress.description]{task.description}",
                        BarColumn(),
                        "[progress.percentage]{task.percentage:>3.2f}%",
                    ) as progress:
                        task = progress.add_task(
                            "Extracting dataset", total=len(members)
                        )
                        for member in members:
                            if handler.exit_now:
                                progress.update(
                                    task, description="✗ Extraction cancelled"
                                )
                                break
                            zip_ref.extract(member, extract_to)
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
                        zip_ref.extract(member, extract_to)

        return extract_to

    def _create_metadata(
        self, organization_id: str, dataset_id: str, save_path: Path
    ) -> None:
        """Create metadata file.

        Args:
            organization_id: The organization ID that owns the dataset.
            dataset_id: The unique identifier of the dataset.
            save_path: The path to save the metadata to.

        """
        metadata = DatasetExportMetadata(
            name=dataset_id,
            organization_id=organization_id,
            export_dir=str(save_path),
            created_at=int(datetime.now().timestamp()),
            license=None,
        )

        with open(save_path / "metadata.json", "w", encoding="utf-8") as f:
            f.write(msgspec.json.encode(metadata).decode("utf-8"))
