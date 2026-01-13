#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset links module.
"""

import re

from vi.client.http.links import LinkBuilder, ResourceLinkParser

DATASET_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/datasets(?:/(?P=organization_id)_"
    r"(?P<dataset_id>[^/]+))?$"
)


class DatasetLinkParser(ResourceLinkParser):
    """Parse a dataset link."""

    _organization_id: str

    def __init__(self, organization_id: str):
        """Initialize the dataset link parser.

        Args:
            organization_id: Organization ID for constructing dataset links.

        """
        self._organization_id = organization_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("datasets")
            .build()
        )

    def __call__(self, dataset_id_or_link: str = "") -> str:
        """Parse the dataset link.

        Args:
            dataset_id_or_link: Dataset ID or full link path.

        Returns:
            The parsed dataset link path.

        """
        if DATASET_LINK_RE.match(dataset_id_or_link):
            return dataset_id_or_link

        return LinkBuilder(self._base_link).add_segment(dataset_id_or_link).build()
