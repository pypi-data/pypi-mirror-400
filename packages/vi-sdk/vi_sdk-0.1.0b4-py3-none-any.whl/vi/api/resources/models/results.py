#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   results.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Result wrapper for simplified model download result handling.
"""

from pathlib import Path

from vi.api.resources.managers.results import DownloadResult


class ModelDownloadResult(DownloadResult):
    """Simplified wrapper for model download results.

    Provides enhanced access to download information with helper methods
    for inspecting downloaded models.

    Attributes:
        model_path: Path to downloaded model directory
        adapter_path: Path to adapter directory (if available)
        run_config_path: Path to run configuration file (if available)

    Examples:
        ```python
        result = client.models.download(run_id="run_123")
        print(f"Model path: {result.model_path}")
        print(result.summary())
        ```

    """

    def __init__(
        self,
        model_path: str,
        adapter_path: str | None = None,
        run_config_path: str | None = None,
    ):
        """Initialize model download result.

        Args:
            model_path: Path to downloaded model directory
            adapter_path: Path to adapter directory (if available)
            run_config_path: Path to run configuration file (if available)

        """
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.run_config_path = run_config_path

    @property
    def model_dir(self) -> Path:
        """Path object for model directory."""
        return Path(self.model_path)

    @property
    def has_adapter(self) -> bool:
        """Check if adapter is available."""
        return self.adapter_path is not None

    @property
    def has_config(self) -> bool:
        """Check if run configuration is available."""
        return self.run_config_path is not None

    @property
    def size_mb(self) -> float:
        """Total size of downloaded model in MB."""
        try:
            total_size = sum(
                f.stat().st_size
                for f in self.model_dir.parent.rglob("*")
                if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

    @property
    def file_list(self) -> list[Path]:
        """List of all downloaded model files."""
        try:
            return [f for f in self.model_dir.parent.rglob("*") if f.is_file()]
        except Exception:
            return []

    def summary(self) -> str:
        """Return formatted summary of download results.

        Returns:
            Multi-line string with download statistics and paths

        Example:
            ```python
            print(result.summary())
            # ✓ Model Download Complete
            #   Model Path: ~/.datature/vi/models/run_abc123/model_full/
            #   Adapter: ✓ Available
            #   Config: ✓ Available
            #   Total Size: 4.2 GB
            ```

        """
        size = self.size_mb

        summary = f"""
✓ Model Download Complete
  Model Path: {self.model_path}
  Adapter: {"✓ Available" if self.has_adapter else "✗ Not available"}
  Config: {"✓ Available" if self.has_config else "✗ Not available"}
"""

        if size > 0:
            if size > 1024:
                summary += f"  Total Size: {size / 1024:.2f} GB\n"
            else:
                summary += f"  Total Size: {size:.1f} MB\n"

        return summary

    def info(self) -> None:
        """Display rich information about downloaded model.

        Shows formatted details including file listing and usage examples.

        Example:
            ```python
            result = client.models.download(run_id="run_123")
            result.info()  # Shows detailed download information
            ```

        """
        size = self.size_mb
        files = self.file_list

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      Model Download Information                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 DOWNLOAD SUMMARY:
   Model Path:     {self.model_path}
   Adapter:        {f"{self.adapter_path}" if self.has_adapter else "Not available"}
   Config:         {f"{self.run_config_path}" if self.has_config else "Not available"}
   Total Size:     {size:.2f} MB ({size / 1024:.2f} GB)
   Files:          {len(files)} files

📁 STRUCTURE:
"""
        for file_path in files[:10]:
            try:
                relative_path = file_path.relative_to(self.model_dir.parent)
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                info_text += f"   • {relative_path} ({file_size:.1f} MB)\n"
            except Exception:
                pass

        if len(files) > 10:
            info_text += f"   ... and {len(files) - 10} more files\n"

        info_text += """
💡 QUICK ACTIONS:
   Load for inference:
     from vi.inference import ViModel
     model = ViModel(run_id="your-run-id")
     result, error = model(source="image.jpg", user_prompt="Describe")

   Inspect model:
     from vi.inference import ViModel
     info = ViModel.inspect(run_id="your-run-id")
     print(info)
"""
        print(info_text)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"ModelDownloadResult(model_path='{self.model_path}', "
            f"has_adapter={self.has_adapter}, has_config={self.has_config})"
        )
