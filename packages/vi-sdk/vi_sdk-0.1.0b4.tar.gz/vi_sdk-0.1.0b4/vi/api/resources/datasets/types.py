#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK datasets types module.
"""

from enum import Enum
from typing import Any

from msgspec import field

from vi.api.types import PaginationParams, QueryParamsMixin, ViStruct


class DatasetListParams(ViStruct, QueryParamsMixin):
    """Dataset list params struct."""

    pagination: PaginationParams


class DatasetType(Enum):
    """Dataset type enum."""

    PHRASE_GROUNDING = "phrase-grounding"
    VQA = "vqa"


class DatasetContent(Enum):
    """Dataset content enum."""

    IMAGE = "Image"


class DatasetLocalization(Enum):
    """Dataset localization enum."""

    DATATURE_MULTI = "Datature/Multi"


class DatasetSpec(ViStruct):
    """Dataset spec struct."""

    name: str
    owner: str
    description: str = ""
    type: DatasetType = DatasetType.PHRASE_GROUNDING
    content: DatasetContent = DatasetContent.IMAGE
    localization: DatasetLocalization = DatasetLocalization.DATATURE_MULTI
    data_localization: DatasetLocalization = DatasetLocalization.DATATURE_MULTI
    status: int = 0
    tags: dict[str, int] = field(default_factory=dict)


class DatasetExportFormat(Enum):
    """Dataset export format enum."""

    VI_JSONL = "ViJsonl"
    VI_FULL = "ViFull"


class DatasetExportOptions(ViStruct):
    """Dataset export options struct."""

    normalized: bool = True
    split_ratio: float | None = None


class DatasetExportSettings(ViStruct):
    """Export settings struct."""

    format: DatasetExportFormat = DatasetExportFormat.VI_FULL
    options: DatasetExportOptions = field(default_factory=DatasetExportOptions)


class DatasetExportSpec(ViStruct):
    """Dataset export spec struct."""

    spec: DatasetExportSettings


class DatasetExportMetadata(ViStruct):
    """Dataset export metadata struct."""

    name: str
    organization_id: str
    export_dir: str
    created_at: int
    license: str | None = None


class BulkAssetDeletionSpec(ViStruct):
    """Bulk asset deletion spec struct."""

    filter: str | dict[str, Any] | None = None
    metadata_query: str | None = None
    rule_query: str | None = None
    strict_query: bool | None = None


class BulkAssetDeletionSession(ViStruct):
    """Bulk asset deletion session struct."""

    spec: BulkAssetDeletionSpec
