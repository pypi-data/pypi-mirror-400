#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   results.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Result wrapper for simplified dataset download result handling.
"""

from pathlib import Path

from vi.api.resources.managers.results import DownloadResult


class DatasetDownloadResult(DownloadResult):
    """Simplified wrapper for dataset download results.

    Provides enhanced access to download information with helper methods
    for inspecting downloaded datasets.

    Attributes:
        dataset_id: Dataset ID of downloaded dataset
        save_dir: Directory path where dataset was saved

    Examples:
        ```python
        result = client.datasets.download(dataset_id="id", save_dir="./data/")
        print(f"Downloaded to: {result.save_dir}")
        print(result.summary())
        ```

    """

    def __init__(self, dataset_id: str, save_dir: str):
        """Initialize dataset download result.

        Args:
            dataset_id: Dataset ID of downloaded dataset
            save_dir: Directory path where dataset was saved

        """
        self.dataset_id = dataset_id
        self.save_dir = save_dir

    @property
    def save_path(self) -> Path:
        """Path object for save directory."""
        return Path(self.save_dir)

    @property
    def size_mb(self) -> float:
        """Total size of downloaded dataset in MB."""
        try:
            total_size = sum(
                f.stat().st_size for f in self.save_path.rglob("*") if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

    @property
    def splits(self) -> list[str]:
        """List of available splits (training, validation, dump)."""
        try:
            return [
                d.name
                for d in self.save_path.iterdir()
                if d.is_dir() and d.name in ["training", "validation", "dump"]
            ]
        except Exception:
            return []

    @property
    def asset_count(self) -> dict[str, int]:
        """Count of assets per split."""
        counts = {}
        try:
            for split in self.splits:
                assets_dir = self.save_path / split / "assets"
                if assets_dir.exists():
                    counts[split] = len(list(assets_dir.iterdir()))
        except Exception:
            pass
        return counts

    @property
    def annotation_count(self) -> dict[str, int]:
        """Count of annotation files per split."""
        counts = {}
        try:
            for split in self.splits:
                annotations_dir = self.save_path / split / "annotations"
                if annotations_dir.exists():
                    counts[split] = len(list(annotations_dir.glob("*.jsonl")))
        except Exception:
            pass
        return counts

    def summary(self) -> str:
        """Return formatted summary of download results.

        Returns:
            Multi-line string with download statistics and structure

        Example:
            ```python
            print(result.summary())
            # ✓ Dataset Download Complete
            #   Dataset: dataset_abc123
            #   Location: ./data/dataset_abc123/
            #   Total Size: 1.2 GB
            #
            #   Splits:
            #     • training: 850 assets
            #     • validation: 150 assets
            ```

        """
        size = self.size_mb
        asset_counts = self.asset_count

        summary = f"""
✓ Dataset Download Complete
  Dataset: {self.dataset_id}
  Location: {self.save_dir}
"""

        if size > 0:
            if size > 1024:
                summary += f"  Total Size: {size / 1024:.2f} GB\n"
            else:
                summary += f"  Total Size: {size:.1f} MB\n"

        if asset_counts:
            summary += "\n  Splits:\n"
            for split, count in asset_counts.items():
                summary += f"    • {split}: {count} assets\n"

        return summary

    def info(self) -> None:
        """Display rich information about downloaded dataset.

        Shows formatted details including directory structure and statistics.

        Example:
            ```python
            result = client.datasets.download(dataset_id="id")
            result.info()  # Shows detailed download information
            ```

        """
        size = self.size_mb
        asset_counts = self.asset_count
        annotation_counts = self.annotation_count

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     Dataset Download Information                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 DOWNLOAD SUMMARY:
   Dataset ID:     {self.dataset_id}
   Location:       {self.save_dir}
   Total Size:     {size:.2f} MB ({size / 1024:.2f} GB)

📁 STRUCTURE:
"""
        for split in self.splits:
            assets = asset_counts.get(split, 0)
            annotations = annotation_counts.get(split, 0)
            info_text += f"""
   {split}/
     ├── assets/ ({assets} files)
     └── annotations/ ({annotations} files)
"""

        info_text += """
💡 QUICK ACTIONS:
   Load dataset:   from vi.dataset.loaders import ViDataset
                   dataset = ViDataset(result.save_dir)

   List assets:    for asset in dataset.training.assets:
                       print(asset.filename)
"""
        print(info_text)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"DatasetDownloadResult(dataset_id='{self.dataset_id}', "
            f"save_dir='{self.save_dir}')"
        )
