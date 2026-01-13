#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotation links module.
"""

import re

from vi.api.resources.datasets.utils.helper import build_dataset_id
from vi.client.http.links import LinkBuilder, ResourceLinkParser

ANNOTATION_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/datasets/(?P=organization_id)_"
    r"(?P<dataset_id>[^/]+)/annotations(?:/(?P<annotation_id>[^/]+))?$"
)

ANNOTATION_IMPORT_SESSION_LINK_RE = re.compile(
    r"^/workspaces/(?P<organization_id>[^/]+)/datasets/(?P=organization_id)_"
    r"(?P<dataset_id>[^/]+)/annotationImportSessions(?:/"
    r"(?P<annotation_import_session_id>[^/]+))?$"
)


class AnnotationLinkParser(ResourceLinkParser):
    """Parse an annotation link."""

    _organization_id: str
    _dataset_id: str
    _asset_id: str

    def __init__(self, organization_id: str, dataset_id: str, asset_id: str):
        """Initialize the annotation link parser.

        Args:
            organization_id: Organization ID for constructing annotation links.
            dataset_id: Dataset ID for constructing annotation links.
            asset_id: Asset ID for constructing annotation links.

        """
        self._organization_id = organization_id
        self._dataset_id = dataset_id
        self._asset_id = asset_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("datasets")
            .add_segment(build_dataset_id(self._organization_id, self._dataset_id))
            .add_segment("assets")
            .add_segment(self._asset_id)
            .add_segment("annotations")
            .build()
        )

    def __call__(self, annotation_id_or_link: str = "") -> str:
        """Parse the annotation link.

        Args:
            annotation_id_or_link: Annotation ID or full link path.

        Returns:
            The parsed annotation link path.

        """
        if ANNOTATION_LINK_RE.match(annotation_id_or_link):
            return annotation_id_or_link

        return LinkBuilder(self._base_link).add_segment(annotation_id_or_link).build()


class AnnotationImportSessionLinkParser(ResourceLinkParser):
    """Parse an annotation import session link."""

    _organization_id: str
    _dataset_id: str

    def __init__(self, organization_id: str, dataset_id: str):
        """Initialize the annotation import session link parser.

        Args:
            organization_id: Organization ID.
            dataset_id: Dataset ID.

        """
        self._organization_id = organization_id
        self._dataset_id = dataset_id
        self._base_link = (
            LinkBuilder("/workspaces")
            .add_segment(self._organization_id)
            .add_segment("datasets")
            .add_segment(build_dataset_id(self._organization_id, self._dataset_id))
            .add_segment("annotationImportSessions")
            .build()
        )

    def __call__(self, annotation_import_session_id_or_link: str = "") -> str:
        """Parse the annotation import session link.

        Args:
            annotation_import_session_id_or_link: Session ID or full link path.

        Returns:
            The parsed annotation import session link path.

        """
        if ANNOTATION_IMPORT_SESSION_LINK_RE.match(
            annotation_import_session_id_or_link
        ):
            return annotation_import_session_id_or_link

        return (
            LinkBuilder(self._base_link)
            .add_segment(annotation_import_session_id_or_link)
            .build()
        )
