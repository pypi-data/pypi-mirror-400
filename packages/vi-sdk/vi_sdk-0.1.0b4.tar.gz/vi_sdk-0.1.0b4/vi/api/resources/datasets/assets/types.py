#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets types module.
"""

from enum import Enum
from typing import Any

from vi.api.types import PaginationParams, QueryParamsMixin, ViStruct

AssetCustomMetadata = dict[str, str | int | float | bool]


class SortOrder(Enum):
    """Sort order enum."""

    ASC = "asc"
    DESC = "desc"


class SortCriterion(Enum):
    """Asset sort criterion enum."""

    DEFAULT = "default"
    ASSET_ID = "assetId"
    FILENAME = "filename"
    LAST_MODIFIED_CONTENTS = "lastModified.contents"
    METADATA_FILE_SIZE = "metadata.fileSize"


class AssetSortCriterion(ViStruct):
    """Asset sort criterion with order."""

    criterion: SortCriterion
    order: SortOrder = SortOrder.ASC


class AssetListParams(ViStruct, QueryParamsMixin):
    """Asset list params struct."""

    pagination: PaginationParams | None = None
    filter: str | dict[str, Any] | None = None
    contents: bool | None = None
    sort_by: AssetSortCriterion | None = None
    metadata_query: str | None = None
    rule_query: str | None = None
    page_after: bool | None = None
    strict_query: bool | None = None

    # Configuration for direct mapping
    _FIELD_MAPPINGS = {
        "pagination.page_token": "p",
        "pagination.page_size": "s",
        "sort_by.order": "o",
        "sort_by.criterion": "sortBy",
        **QueryParamsMixin.identity_mappings(["filter", "contents"]),
        **QueryParamsMixin.auto_camel_mappings(
            ["metadata_query", "rule_query", "page_after", "strict_query"]
        ),
    }

    _BOOLEAN_FLAGS = {"contents", "page_after", "strict_query"}
    _SKIP_DEFAULT_VALUES = {"sort_by.order": SortOrder.ASC}
    _VALUE_MAPPINGS = {"sort_by.order": {SortOrder.DESC: "d"}}


class AssetGetParams(ViStruct, QueryParamsMixin):
    """Asset get params struct."""

    contents: bool | None = None

    # Configuration for direct mapping
    _FIELD_MAPPINGS = {
        "contents": "contents",
    }

    _BOOLEAN_FLAGS = {"contents"}


class AssetUploadFileSpec(ViStruct):
    """Asset upload item struct."""

    filename: str
    mime: str | None
    size: int
    crc32c: int | None = None
    custom_metadata: AssetCustomMetadata | None = None
    kind: str = "Image"


class AssetUploadSpec(ViStruct):
    """Asset upload spec struct."""

    assets: list[AssetUploadFileSpec]
    kind: str = "Upload"
    failure_mode: str = "FailAfterOne"
    on_asset_overwritten: str = "RemoveLinkedResource"


class AssetUploadSession(ViStruct):
    """Asset upload struct."""

    spec: AssetUploadSpec


class BatchConfig(ViStruct):
    """Configuration for batch upload."""

    dataset_id: str
    failure_mode: str
    on_asset_overwritten: str
    asset_source_class: str
    asset_source_provider: str
    asset_source_id: str
