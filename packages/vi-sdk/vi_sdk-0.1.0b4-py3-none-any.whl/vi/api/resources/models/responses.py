#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK models responses module.
"""

from datetime import datetime

from msgspec import field
from vi.api.responses import ResourceMetadata, ViResponse


class ModelSpec(ViResponse):
    """Model spec.

    Attributes:
        kind: Model kind identifier.
        epoch: Training epoch number if applicable.
        evaluation_metrics: Dictionary of evaluation metrics (accuracy, loss, etc.).

    """

    kind: str
    epoch: int | None = None
    evaluation_metrics: dict | None = None


class ModelDownloadUrl(ViResponse):
    """Model download URL.

    Attributes:
        url: Pre-signed URL for downloading the model.
        expires_at: Unix timestamp when the download URL expires.

    """

    url: str
    expires_at: int


class ModelContents(ViResponse):
    """Model contents.

    Attributes:
        download_url: Download URL information for accessing the model files.

    """

    download_url: ModelDownloadUrl


class ModelStatus(ViResponse):
    """Model status.

    Attributes:
        observed_generation: Generation number of the observed state.
        conditions: List of condition dictionaries tracking model lifecycle.
        storage_object: Storage location identifier for the model files.
        contents: Model contents including download URLs when available.

    """

    observed_generation: int
    conditions: list[dict]
    storage_object: str
    contents: ModelContents | None = None


class Model(ViResponse):
    """Model response.

    Attributes:
        kind: Resource kind identifier.
        run_id: ID of the training run that produced this model.
        metadata: Resource metadata including timestamps.
        spec: Model specification including epoch and evaluation metrics.
        status: Current status of the model including download availability.
        self_link: API link to this model resource.
        etag: Entity tag for caching and concurrency control.
        organization_id: Organization ID.
        model_id: Unique model identifier (mapped from runOutputId).

    """

    kind: str
    run_id: str
    metadata: ResourceMetadata
    spec: ModelSpec
    status: ModelStatus
    self_link: str
    etag: str
    organization_id: str = field(name="workspaceId")
    model_id: str = field(name="runOutputId")

    def info(self) -> None:
        """Display rich information about this model.

        Shows a formatted summary of the model including epoch, metrics,
        and download availability in an easy-to-read format.

        Example:
            ```python
            model = client.models.get(run_id_or_link="run_abc123")
            model.info()
            ```

        """
        created_str = datetime.fromtimestamp(
            self.metadata.time_created / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            Model Information                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Model ID:       {self.model_id}
   Run ID:         {self.run_id}
   Organization:   {self.organization_id}
   Kind:           {self.spec.kind}

📊 TRAINING:
   Epoch:          {self.spec.epoch if self.spec.epoch is not None else "N/A"}

📈 METRICS:
   {self._format_metrics()}

📅 DATES:
   Created:        {created_str}

💾 STORAGE:
   Storage Object: {self.status.storage_object}
   Download Ready: {"Yes" if self.status.contents else "No"}

💡 QUICK ACTIONS:
   Download: client.models.download(run_id_or_link="{self.run_id}")
   Get Run:  client.runs.get(run_id="{self.run_id}")
"""
        print(info_text)

    def _format_metrics(self) -> str:
        """Format evaluation metrics for display."""
        if not self.spec.evaluation_metrics:
            return "   No metrics available"

        metrics_lines = []
        for key, value in self.spec.evaluation_metrics.items():
            if isinstance(value, (int, float)):
                metrics_lines.append(
                    f"{key}: {value:.4f}"
                    if isinstance(value, float)
                    else f"{key}: {value}"
                )
            else:
                metrics_lines.append(f"{key}: {value}")

        return (
            "   " + "\n   ".join(metrics_lines)
            if metrics_lines
            else "   No metrics available"
        )
