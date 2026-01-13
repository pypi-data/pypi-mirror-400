#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK models types module.
"""

from vi.api.types import PaginationParams, QueryParamsMixin, ViStruct


class ModelListParams(ViStruct, QueryParamsMixin):
    """Model list params."""

    pagination: PaginationParams

    _FIELD_MAPPINGS = {
        "pagination.page_token": "pageToken",
        "pagination.page_size": "pageSize",
    }
