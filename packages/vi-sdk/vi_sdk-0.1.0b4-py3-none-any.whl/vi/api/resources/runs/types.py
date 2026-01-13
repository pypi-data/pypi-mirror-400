#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK runs types module.
"""

from vi.api.types import PaginationParams, QueryParamsMixin, ViStruct


class RunListParams(ViStruct, QueryParamsMixin):
    """Run list params."""

    pagination: PaginationParams

    _FIELD_MAPPINGS = {
        "pagination.page_token": "pageToken",
        "pagination.page_size": "pageSize",
    }
