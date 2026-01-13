#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK flows types module.
"""

from vi.api.types import PaginationParams, QueryParamsMixin, ViStruct


class FlowListParams(ViStruct, QueryParamsMixin):
    """Flow list params."""

    pagination: PaginationParams
