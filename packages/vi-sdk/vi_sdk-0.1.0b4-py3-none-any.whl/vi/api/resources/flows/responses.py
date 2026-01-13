#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK flows responses module.
"""

from datetime import datetime
from typing import Any

from msgspec import field
from vi.api.responses import ResourceMetadata, ViResponse


class FlowBlock(ViResponse):
    """Flow block.

    Attributes:
        block: Block type identifier.
        settings: Dictionary of block-specific configuration settings.
        style: Dictionary of UI/display styling information.

    """

    block: str
    settings: dict[str, Any]
    style: dict[str, Any]


class FlowSpec(ViResponse):
    """Flow spec.

    Attributes:
        name: Display name of the flow.
        schema: Schema version identifier for the flow configuration.
        tolerations: Dictionary of toleration rules for execution constraints.
        settings: Global settings for the flow execution.
        blocks: List of flow blocks defining the training pipeline.
        training_project: Project/dataset ID for training, if specified.

    """

    name: str
    schema: str
    tolerations: dict[str, list[str]]
    settings: dict[str, Any]
    blocks: list[FlowBlock]
    training_project: str | None = None


class Flow(ViResponse, tag_field="kind"):
    """Flow.

    Attributes:
        organization_id: Organization ID.
        flow_id: Unique identifier for the flow.
        spec: Flow specification including blocks and settings.
        metadata: Resource metadata including timestamps.
        self_link: API link to this flow resource.
        etag: Entity tag for caching and concurrency control.

    """

    organization_id: str = field(name="workspaceId")
    flow_id: str
    spec: FlowSpec
    metadata: ResourceMetadata
    self_link: str
    etag: str

    def info(self) -> None:
        """Display rich information about this training flow.

        Shows a formatted summary of the flow including configuration,
        blocks, and settings in an easy-to-read format.

        Example:
            ```python
            flow = client.flows.get(flow_id="flow_abc123")
            flow.info()
            ```

        """
        created_str = datetime.fromtimestamp(
            self.metadata.time_created / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        updated_str = datetime.fromtimestamp(
            self.metadata.last_updated / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         Training Flow Information                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Flow ID:        {self.flow_id}
   Name:           {self.spec.name}
   Organization:   {self.organization_id}
   Schema:         {self.spec.schema}

🔧 CONFIGURATION:
   Training Project: {self.spec.training_project if self.spec.training_project else "Not specified"}
   Flow Blocks:    {len(self.spec.blocks)} block(s)
   Tolerations:    {len(self.spec.tolerations)} rule(s)

📅 DATES:
   Created:        {created_str}
   Last Updated:   {updated_str}

🧱 BLOCKS:
   {self._format_blocks()}

💡 QUICK ACTIONS:
   Delete:      client.flows.delete(flow_id="{self.flow_id}")
   List Runs:   client.runs.list()  # Filter by flow_id
"""
        print(info_text)

    def _format_blocks(self) -> str:
        """Format flow blocks for display."""
        if not self.spec.blocks:
            return "   No blocks configured"

        block_lines = []
        for i, block in enumerate(self.spec.blocks[:5], 1):
            block_lines.append(f"{i}. {block.block}")

        if len(self.spec.blocks) > 5:
            block_lines.append(f"... and {len(self.spec.blocks) - 5} more")

        return "   " + "\n   ".join(block_lines)
