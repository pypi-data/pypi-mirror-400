#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   base.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset loaders base types module.
"""

from msgspec import Struct


class ViDatasetLoaderStruct(Struct, rename="camel", kw_only=True):
    """Base struct."""
