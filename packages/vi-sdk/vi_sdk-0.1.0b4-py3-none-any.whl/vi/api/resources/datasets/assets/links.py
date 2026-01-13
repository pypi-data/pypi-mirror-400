#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK asset links module.
"""

import re

from vi.api.resources.datasets.utils.helper import build_dataset_id
from vi.client.http.links import LinkBuilder, ResourceLinkParser

ASSET_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/datasets/(?P=organization_id)_"
    r"(?P<dataset_id>[^/]+)/assets(?:/(?P<asset_id>[^/]+))?$"
)

ASSET_INGESTION_SESSION_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/datasets/(?P=organization_id)_"
    r"(?P<dataset_id>[^/]+)/assetSources"
    r"/(?P<asset_source_class>[^/]+)/(?P<asset_source_provider>[^/]+)/"
    r"(?P<asset_source_id>[^/]+)/assetIngestionSessions(?:/(?P<asset_ingestion_session_id>[^/]+))?$"
)


class AssetLinkParser(ResourceLinkParser):
    """Parse an asset link."""

    _organization_id: str
    _dataset_id: str

    def __init__(self, organization_id: str, dataset_id: str):
        """Initialize the asset link parser.

        Args:
            organization_id: Organization ID for constructing asset links.
            dataset_id: Dataset ID for constructing asset links.

        """
        self._organization_id = organization_id
        self._dataset_id = dataset_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("datasets")
            .add_segment(build_dataset_id(self._organization_id, self._dataset_id))
            .add_segment("assets")
            .build()
        )

    def __call__(self, asset_id_or_link: str = "") -> str:
        """Parse the asset link.

        Args:
            asset_id_or_link: Asset ID or full link path.

        Returns:
            The parsed asset link path.

        """
        if ASSET_LINK_RE.match(asset_id_or_link):
            return asset_id_or_link

        return LinkBuilder(self._base_link).add_segment(asset_id_or_link).build()


class AssetIngestionSessionLinkParser(ResourceLinkParser):
    """Parse an asset ingestion session link."""

    _organization_id: str
    _dataset_id: str
    _asset_source_class: str
    _asset_source_provider: str
    _asset_source_id: str

    def __init__(
        self,
        organization_id: str,
        dataset_id: str,
        asset_source_class: str,
        asset_source_provider: str,
        asset_source_id: str,
    ):
        """Initialize the asset ingestion session link parser.

        Args:
            organization_id: Organization ID.
            dataset_id: Dataset ID.
            asset_source_class: Asset source class identifier.
            asset_source_provider: Asset source provider identifier.
            asset_source_id: Asset source ID.

        """
        self._organization_id = organization_id
        self._dataset_id = dataset_id
        self._asset_source_class = asset_source_class
        self._asset_source_provider = asset_source_provider
        self._asset_source_id = asset_source_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("datasets")
            .add_segment(build_dataset_id(self._organization_id, self._dataset_id))
            .add_segment("assetSources")
            .add_segment(self._asset_source_class)
            .add_segment(self._asset_source_provider)
            .add_segment(self._asset_source_id)
            .add_segment("assetIngestionSessions")
            .build()
        )

    def __call__(self, asset_ingestion_session_id_or_link: str = "") -> str:
        """Parse the asset ingestion session link.

        Args:
            asset_ingestion_session_id_or_link: Session ID or full link path.

        Returns:
            The parsed asset ingestion session link path.

        """
        if ASSET_INGESTION_SESSION_LINK_RE.match(asset_ingestion_session_id_or_link):
            return asset_ingestion_session_id_or_link

        return (
            LinkBuilder(self._base_link)
            .add_segment(asset_ingestion_session_id_or_link)
            .build()
        )
