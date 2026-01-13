#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   results.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Result wrappers for simplified asset upload and download result handling.
"""

from pathlib import Path

from vi.api.resources.datasets.assets.responses import AssetIngestionSession
from vi.api.resources.managers.results import DownloadResult, UploadResult


class AssetUploadResult(UploadResult):
    """Simplified wrapper for asset upload results.

    Provides simple access to upload statistics across one or more
    ingestion sessions (batches), hiding complexity of batch processing.

    Attributes:
        sessions: List of underlying ingestion session responses

    Examples:
        ```python
        result = client.assets.upload(dataset_id="id", paths="./images/")
        print(f"Uploaded: {result.total_succeeded}/{result.total_files}")
        print(result.summary())
        ```

    """

    def __init__(self, sessions: list[AssetIngestionSession]):
        """Initialize upload result wrapper.

        Args:
            sessions: List of asset ingestion sessions from upload operation

        """
        self.sessions = sessions
        self.start_time = sessions[0].metadata.time_created if sessions else None
        self.end_time = sessions[-1].metadata.last_updated if sessions else None

    @property
    def total_files(self) -> int:
        """Total number of files in upload operation."""
        return sum(s.status.progressCount.total for s in self.sessions)

    @property
    def total_succeeded(self) -> int:
        """Total number of successfully uploaded files."""
        return sum(s.status.progressCount.succeeded for s in self.sessions)

    @property
    def total_failed(self) -> int:
        """Total number of failed uploads."""
        return sum(s.status.progressCount.errored for s in self.sessions)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage (0-100)."""
        if self.total_files == 0:
            return 0.0
        return (self.total_succeeded / self.total_files) * 100

    @property
    def failed_files(self) -> dict[str, str]:
        """Dictionary mapping failed filenames to error messages."""
        failures = {}
        for session in self.sessions:
            for event in session.status.events:
                if hasattr(event, "files"):  # Error event
                    for filename, error in event.files.items():
                        failures[filename] = error.value
        return failures

    @property
    def is_complete(self) -> bool:
        """Check if all uploads completed (succeeded or failed)."""
        return self.total_succeeded + self.total_failed == self.total_files

    @property
    def session_ids(self) -> list[str]:
        """List of ingestion session IDs."""
        return [s.asset_ingestion_session_id for s in self.sessions]

    def summary(self) -> str:
        """Return formatted summary of upload results.

        Returns:
            Multi-line string with upload statistics and status

        Example:
            ```python
            print(result.summary())
            # ✓ Upload Complete
            #   Total: 100 files
            #   Succeeded: 98
            #   Failed: 2
            #   Success Rate: 98.0%
            #   Duration: 45.2s
            #
            #   Failed files:
            #     • corrupted.jpg: ECORRUPT
            #     • invalid.png: EBADMIME
            ```

        """
        icon = "✓" if self.total_failed == 0 else "⚠"
        status = "Upload Complete" if self.is_complete else "Upload In Progress"

        summary = f"""
{icon} {status}
  Total: {self.total_files} files
  Succeeded: {self.total_succeeded}
  Failed: {self.total_failed}
  Success Rate: {self.success_rate:.1f}%
  Duration: {self.duration_seconds:.1f}s
"""

        if self.failed_files:
            summary += "\n  Failed files:\n"
            for filename, error in self.failed_files.items():
                summary += f"    • {filename}: {error}\n"

        if len(self.sessions) > 1:
            summary += (
                f"\n  Batches: {len(self.sessions)} "
                "(auto-batched for optimal performance)\n"
            )

        return summary

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"AssetUploadResult(total={self.total_files}, "
            f"succeeded={self.total_succeeded}, "
            f"failed={self.total_failed})"
        )

    def __iter__(self):
        """Iterate over underlying ingestion sessions."""
        return iter(self.sessions)

    def __len__(self):
        """Return number of ingestion sessions (batches)."""
        return len(self.sessions)

    def __getitem__(self, index):
        """Access specific ingestion session by index."""
        return self.sessions[index]


class AssetDownloadResult(DownloadResult):
    """Simplified wrapper for asset download results.

    Provides enhanced access to download information with helper methods
    for inspecting downloaded assets.

    Attributes:
        dataset_id: Dataset ID of downloaded assets
        count: Number of assets downloaded
        save_dir: Directory path where assets were saved

    Examples:
        ```python
        result = client.assets.download(dataset_id="id", save_dir="./assets/")
        print(f"Downloaded: {result.count} assets")
        print(result.summary())
        ```

    """

    def __init__(self, dataset_id: str, count: int, save_dir: str):
        """Initialize asset download result.

        Args:
            dataset_id: Dataset ID of downloaded assets
            count: Number of assets downloaded
            save_dir: Directory path where assets were saved

        """
        self.dataset_id = dataset_id
        self.count = count
        self.save_dir = save_dir

    @property
    def save_path(self) -> Path:
        """Path object for save directory."""
        return Path(self.save_dir)

    @property
    def size_mb(self) -> float:
        """Total size of downloaded assets in MB (if available)."""
        try:
            total_size = sum(
                f.stat().st_size for f in self.save_path.rglob("*") if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

    @property
    def file_list(self) -> list[Path]:
        """List of all downloaded asset files."""
        try:
            return [f for f in self.save_path.rglob("*") if f.is_file()]
        except Exception:
            return []

    def summary(self) -> str:
        """Return formatted summary of download results.

        Returns:
            Multi-line string with download statistics and location

        Example:
            ```python
            print(result.summary())
            # ✓ Asset Download Complete
            #   Dataset: dataset_abc123
            #   Assets: 150 files
            #   Location: /home/user/.datature/vi/assets/dataset_abc123/
            #   Total Size: 245.8 MB
            ```

        """
        summary = f"""
✓ Asset Download Complete
  Dataset: {self.dataset_id}
  Assets: {self.count} files
  Location: {self.save_dir}
"""

        # Try to calculate size
        size = self.size_mb
        if size > 0:
            summary += f"  Total Size: {size:.1f} MB\n"

        return summary

    def info(self) -> None:
        """Display rich information about downloaded assets.

        Shows formatted details including file listing (first 10 files).

        Example:
            ```python
            result = client.assets.download(dataset_id="id")
            result.info()  # Shows detailed download information
            ```

        """
        files = self.file_list
        size = self.size_mb

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      Asset Download Information                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 DOWNLOAD SUMMARY:
   Dataset ID:     {self.dataset_id}
   Assets:         {self.count} files
   Total Size:     {size:.2f} MB
   Location:       {self.save_dir}

📁 FILES: (showing first 10)
"""
        for i, file_path in enumerate(files[:10], 1):
            relative_path = file_path.relative_to(self.save_path)
            file_size = file_path.stat().st_size / 1024  # KB
            info_text += f"   {i}. {relative_path} ({file_size:.1f} KB)\n"

        if len(files) > 10:
            info_text += f"   ... and {len(files) - 10} more files\n"

        info_text += """
💡 QUICK ACTIONS:
   List files:     list(result.save_path.rglob("*"))
   Load dataset:   from vi.dataset.loaders import ViDataset
                   dataset = ViDataset(result.save_dir)
"""
        print(info_text)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"AssetDownloadResult(dataset_id='{self.dataset_id}', "
            f"count={self.count}, save_dir='{self.save_dir}')"
        )
