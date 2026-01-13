#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations types module.
"""

import time
from enum import Enum
from typing import Annotated

from msgspec import Meta, field
from vi.api.resources.datasets.annotations.responses import (
    AnnotationImportSessionStatus,
)
from vi.api.types import PaginationParams, QueryParamsMixin, ResourceMetadata, ViStruct


class AnnotationFormat(Enum):
    """Annotation format enum."""

    JSONL = "jsonl"


class ExportSettings(ViStruct):
    """Export settings struct."""

    format: AnnotationFormat = AnnotationFormat.JSONL
    normalized: bool = True
    split_ratio: float = 0.7


class AnnotationImportSource(Enum):
    """Annotation import source enum."""

    UPLOADED_INDIVIDUAL_FILES = "UploadedIndividualFiles"


class FailurePolicy(Enum):
    """Failure policy enum."""

    WARN = "Warn"
    REJECT_FILE = "RejectFile"
    REJECT_SESSION = "RejectSession"


class AnnotationImportFailurePolicy(ViStruct):
    """Annotation import failure policy struct."""

    on_bad_annotation: FailurePolicy = FailurePolicy.REJECT_SESSION
    on_bad_file: FailurePolicy = FailurePolicy.REJECT_SESSION
    on_overwritten: FailurePolicy = FailurePolicy.REJECT_SESSION


class AnnotationImportSpec(ViStruct):
    """Annotation import spec struct."""

    upload_before: int = int((time.time() + 3600) * 1000)
    failure_policies: AnnotationImportFailurePolicy = field(
        default_factory=AnnotationImportFailurePolicy
    )
    source: AnnotationImportSource = AnnotationImportSource.UPLOADED_INDIVIDUAL_FILES


class AnnotationImportSession(ViStruct):
    """Annotation import struct."""

    spec: AnnotationImportSpec
    metadata: ResourceMetadata = field(default_factory=ResourceMetadata)


class AnnotationFileKind(Enum):
    """Annotation file kind enum."""

    UNKNOWN = "Unknown"


class AnnotationImportFileSpec(ViStruct):
    """Annotation upload metadata struct."""

    size_bytes: int
    crc32c: str
    kind: AnnotationFileKind = AnnotationFileKind.UNKNOWN


class AnnotationImportPayload(ViStruct):
    """Annotation upload payload struct."""

    files: dict[str, AnnotationImportFileSpec]


class AnnotationImportPatchCondition(ViStruct):
    """Annotation import patch condition struct."""

    conditions: Annotated[
        list[AnnotationImportSessionStatus], Meta(min_length=1, max_length=1)
    ]


class AnnotationImportPatchStatus(ViStruct):
    """Annotation import patch status struct."""

    status: AnnotationImportPatchCondition


class AnnotationListParams(ViStruct, QueryParamsMixin):
    """Annotation list params."""

    pagination: PaginationParams

    _FIELD_MAPPINGS = {
        "pagination.page_token": "pageToken",
        "pagination.page_size": "pageSize",
    }
