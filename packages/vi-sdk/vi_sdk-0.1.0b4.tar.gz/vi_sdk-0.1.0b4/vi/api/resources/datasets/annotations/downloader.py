#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   downloader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations downloader module.
"""

from pathlib import Path
from zipfile import ZipFile

from rich.progress import BarColumn

from vi.api.resources.datasets.annotations import responses
from vi.api.resources.managers import ResourceDownloader
from vi.consts import DEFAULT_ANNOTATION_EXPORT_DIR
from vi.utils.progress import ViProgress


class AnnotationDownloader(ResourceDownloader):
    """Download annotation exports with resume support and validation.

    Downloads annotation archives from the Datature Vi platform in various export
    formats (COCO, YOLO, Pascal VOC, etc.). Inherits parallel download and resume
    capabilities from ResourceDownloader.

    The downloader automatically extracts annotation files from ZIP archives and
    validates their presence. Supports skipping existing downloads when overwrite
    is disabled.

    """

    def download(
        self,
        dataset_id: str,
        dataset_export_id: str,
        download_url: str,
        save_dir: Path | str = DEFAULT_ANNOTATION_EXPORT_DIR,
    ) -> responses.DownloadedAnnotations:
        """Download and extract annotation export for a dataset.

        Downloads an annotation archive in the specified export format, extracts
        all files, and returns the path to the extracted annotations. If the
        export already exists and overwrite=False, returns existing paths
        without re-downloading.

        Args:
            dataset_id: Unique identifier of the dataset.
            dataset_export_id: Unique identifier of the annotation export.
            download_url: Pre-signed URL to download the annotation archive from.
            save_dir: Base directory where annotations are saved. The annotations
                will be saved in a subdirectory named after the dataset_id.
                Defaults to ~/.datature/vi/annotations/.

        Returns:
            DownloadedAnnotations object containing:
            - export_path: Directory where annotation files are extracted
            - dataset_id: ID of the dataset
            - export_id: ID of the export

        Raises:
            PermissionError: If unable to write to the save directory.
            OSError: If insufficient disk space or network issues occur.

        Example:
            ```python
            from vi.api.resources.datasets.annotations.downloader import (
                AnnotationDownloader,
            )
            from pathlib import Path

            # Create downloader with progress display
            downloader = AnnotationDownloader(show_progress=True, overwrite=False)

            # Download annotations
            result = downloader.download(
                dataset_id="dataset_abc",
                dataset_export_id="export_123",
                download_url="https://example.com/annotations.zip",
                save_dir=Path("./annotations"),
            )

            print(f"Annotations saved to: {result.export_path}")
            ```

        Note:
            If overwrite=False and the export already exists at the destination,
            the download is skipped and existing paths are returned immediately.
            The download can be safely interrupted and resumed later.

        See Also:
            - `ResourceDownloader`: Base class with parallel download capabilities
            - [Dataset Guide](../../guide/datasets.md): Annotation export formats and usage

        """
        save_path = Path(save_dir) / dataset_id
        absolute_save_path = Path(save_path).resolve()

        if not self._overwrite and absolute_save_path.exists():
            existing_export = self._check_existing_export(absolute_save_path)
            if existing_export:
                return existing_export

        self._download_and_extract(download_url, absolute_save_path)

        return responses.DownloadedAnnotations(
            export_path=str(absolute_save_path),
            dataset_id=dataset_id,
            export_id=dataset_export_id,
        )

    def _check_existing_export(
        self, path: Path
    ) -> responses.DownloadedAnnotations | None:
        """Check if annotation export already exists at path.

        Validates whether annotation files are already present at the specified
        location to avoid redundant downloads when overwrite is disabled.

        Args:
            path: Directory path to check for existing annotations.

        Returns:
            DownloadedAnnotations object if export exists, None otherwise.

        """
        if not path.exists():
            return None

        return responses.DownloadedAnnotations(
            export_path=str(path), dataset_id=path.stem, export_id=path.stem
        )

    def _download_and_extract(self, download_url: str, save_path: Path):
        """Download and extract annotation export with cleanup.

        Downloads the annotation ZIP archive using resumable chunk-based download,
        extracts all contents, and cleans up temporary files regardless of success
        or failure to prevent disk space waste.

        Args:
            download_url: Pre-signed URL to download the annotation archive from.
            save_path: Directory where annotations will be extracted.

        """
        save_path.mkdir(parents=True, exist_ok=True)

        temp_path = save_path / ".download_temp.zip"

        try:
            self._download_file(download_url, temp_path, "Downloading annotations")
            self._extract_archive(temp_path, save_path)

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            # Clean up manifest file
            manifest_path = temp_path.with_suffix(temp_path.suffix + ".manifest")
            if manifest_path.exists():
                manifest_path.unlink()

    def _extract_archive(self, archive_path: Path, extract_to: Path) -> None:
        """Extract annotation export archive with optional progress tracking.

        Extracts all files from the ZIP archive with optional progress bar
        showing extraction status. Processes all files regardless of whether
        progress display is enabled.

        Args:
            archive_path: Path to the ZIP archive file.
            extract_to: Directory where contents will be extracted.

        """
        with ZipFile(archive_path, "r") as zip_ref:
            members = zip_ref.infolist()

            if self._show_progress:
                with ViProgress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.2f}%",
                ) as progress:
                    task = progress.add_task(
                        "Extracting annotation file(s)", total=len(members)
                    )
                    for member in members:
                        zip_ref.extract(member, extract_to)
                        progress.update(task, advance=1)

            else:
                for member in members:
                    zip_ref.extract(member, extract_to)
