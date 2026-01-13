#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK model links module.
"""

import re

from vi.client.http.links import LinkBuilder, ResourceLinkParser

MODEL_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/runs/(?P<run_id>[^/]+)/runOutputs"
    r"(?:/(?P<ckpt>[^/]+))?(?:\?contents=y)?$"
)


class ModelLinkParser(ResourceLinkParser):
    """Parse a model link."""

    _organization_id: str

    def __init__(self, organization_id: str):
        """Initialize the model link parser.

        Args:
            organization_id: Organization ID for constructing model links.

        """
        self._organization_id = organization_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("runs")
            .build()
        )

    def __call__(
        self, run_id_or_link: str, ckpt: str | None = None, contents: bool = False
    ) -> str:
        """Parse the model link.

        Args:
            run_id_or_link: Run ID or full link path.
            ckpt: Optional checkpoint identifier.
            contents: Whether to include contents query parameter.

        Returns:
            The parsed model link path.

        """
        if MODEL_LINK_RE.match(run_id_or_link):
            return run_id_or_link

        builder = (
            LinkBuilder(self._base_link)
            .add_segment(run_id_or_link)
            .add_segment("outputs")
        )

        if ckpt:
            builder.add_segment(ckpt)

        builder.add_param("intent", "sdkLocalDeploy")

        if contents:
            builder.add_param("contents", True)

        return builder.build()
