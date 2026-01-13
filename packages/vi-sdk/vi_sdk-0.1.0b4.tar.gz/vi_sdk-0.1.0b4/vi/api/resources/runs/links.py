#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK run links module.
"""

import re

from vi.client.http.links import LinkBuilder, ResourceLinkParser

RUN_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/runs/(?P<run_id>[^/]+)$"
)


class RunLinkParser(ResourceLinkParser):
    """Parse a run link."""

    _organization_id: str

    def __init__(self, organization_id: str):
        """Initialize the run link parser.

        Args:
            organization_id: Organization ID for constructing run links.

        """
        self._organization_id = organization_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("runs")
            .build()
        )

    def __call__(self, run_id_or_link: str = "") -> str:
        """Parse the run link.

        Args:
            run_id_or_link: Run ID or full link path.

        Returns:
            The parsed run link path.

        """
        if RUN_LINK_RE.match(run_id_or_link):
            return run_id_or_link

        return LinkBuilder(self._base_link).add_segment(run_id_or_link).build()
