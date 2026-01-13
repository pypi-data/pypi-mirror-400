#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK runs responses module.
"""

from datetime import datetime

from msgspec import field
from vi.api.resources.flows.responses import FlowSpec
from vi.api.responses import ResourceCondition, ResourceMetadata, ViResponse


class RunSpec(ViResponse):
    """Run spec.

    Attributes:
        flow: Flow specification defining the training configuration.
        killed_at: Unix timestamp when the run was manually terminated, if applicable.
        training_project: Project/dataset ID used for training.

    """

    flow: FlowSpec
    killed_at: int | None = None
    training_project: str | None = None


class RunStatus(ViResponse):
    """Run status.

    Attributes:
        log: URL or path to the run's log output.
        observed_generation: Generation number of the observed state.
        conditions: List of resource conditions tracking run lifecycle.

    """

    log: str
    observed_generation: int
    conditions: list[ResourceCondition]


class Run(ViResponse, tag_field="kind"):
    """Run response.

    Attributes:
        organization_id: Organization ID.
        run_id: Unique identifier for the training run.
        spec: Run specification including flow and training project.
        status: Current status of the run including logs and conditions.
        metadata: Resource metadata including timestamps.
        self_link: API link to this run resource.
        etag: Entity tag for caching and concurrency control.

    """

    organization_id: str = field(name="workspaceId")
    run_id: str
    spec: RunSpec
    status: RunStatus
    metadata: ResourceMetadata
    self_link: str
    etag: str

    def info(self) -> None:
        """Display rich information about this training run.

        Shows a formatted summary of the run including status, configuration,
        and timing information in an easy-to-read format.

        Example:
            ```python
            run = client.runs.get(run_id="run_abc123")
            run.info()
            ```

        """
        created_str = datetime.fromtimestamp(
            self.metadata.time_created / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        updated_str = datetime.fromtimestamp(
            self.metadata.last_updated / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Determine run status from conditions
        status = "unknown"
        if self.status.conditions:
            # Get the latest condition
            latest_condition = self.status.conditions[-1]
            status = (
                latest_condition.type
                if hasattr(latest_condition, "type")
                else "unknown"
            )

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Training Run Information                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Run ID:         {self.run_id}
   Organization:   {self.organization_id}
   Status:         {status}

🔧 CONFIGURATION:
   Flow Name:      {self.spec.flow.name}
   Training Project: {self.spec.training_project if self.spec.training_project else "Not specified"}
   Schema:         {self.spec.flow.schema}

📅 TIMING:
   Created:        {created_str}
   Last Updated:   {updated_str}
   {"Killed At:      " + datetime.fromtimestamp(self.spec.killed_at / 1000).strftime("%Y-%m-%d %H:%M:%S") if self.spec.killed_at else ""}

📊 STATUS:
   Observed Generation: {self.status.observed_generation}
   Conditions:     {len(self.status.conditions)} condition(s)
   Log Available:  {"Yes" if self.status.log else "No"}

💡 QUICK ACTIONS:
   Get Models:  client.models.list(run_id_or_link="{self.run_id}")
   Download:    client.models.download(run_id_or_link="{self.run_id}")
   Delete:      client.runs.delete(run_id="{self.run_id}")
"""
        print(info_text)
