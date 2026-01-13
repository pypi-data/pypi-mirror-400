#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK flows links module.
"""

import re

from vi.client.http.links import LinkBuilder, ResourceLinkParser

FLOW_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/flows/(?P<flow_id>[^/]+)$"
)


class FlowLinkParser(ResourceLinkParser):
    """Parse a flow link."""

    _organization_id: str

    def __init__(self, organization_id: str):
        """Initialize the flow link parser.

        Args:
            organization_id: Organization ID for constructing flow links.

        """
        self._organization_id = organization_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("flows")
            .build()
        )

    def __call__(self, flow_id_or_link: str = "") -> str:
        """Parse the flow link.

        Args:
            flow_id_or_link: Flow ID or full link path.

        Returns:
            The parsed flow link path.

        """
        if FLOW_LINK_RE.match(flow_id_or_link):
            return flow_id_or_link

        return LinkBuilder(self._base_link).add_segment(flow_id_or_link).build()
