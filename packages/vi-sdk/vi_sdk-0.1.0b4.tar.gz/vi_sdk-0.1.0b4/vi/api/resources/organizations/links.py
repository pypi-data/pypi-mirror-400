#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK organization links module.
"""

import re

from vi.client.http.links import LinkBuilder, ResourceLinkParser

ORGANIZATION_LINK_RE = re.compile(r"^/workspaces/(?P<organization_id>[^/]+)$")


class OrganizationLinkParser(ResourceLinkParser):
    """Parse an organization link."""

    def __init__(self):
        """Initialize the organization link parser."""
        self._base_link = LinkBuilder("/workspaces").build()

    def __call__(self, organization_id_or_link: str = "") -> str:
        """Parse the organization link.

        Args:
            organization_id_or_link: Organization ID or full link path.

        Returns:
            The parsed organization link path.

        """
        if ORGANIZATION_LINK_RE.match(organization_id_or_link):
            return organization_id_or_link

        return LinkBuilder(self._base_link).add_segment(organization_id_or_link).build()
