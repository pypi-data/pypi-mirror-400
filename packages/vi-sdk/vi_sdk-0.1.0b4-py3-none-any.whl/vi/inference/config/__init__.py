#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   __init__.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK config init module.
"""

from vi.inference.config.base_config import ViGenerationConfig
from vi.inference.config.deepseekocr import DeepSeekOCRGenerationConfig
from vi.inference.config.nvila import NVILAGenerationConfig
from vi.inference.config.qwen25vl import Qwen25VLGenerationConfig

__all__ = [
    "ViGenerationConfig",
    "DeepSeekOCRGenerationConfig",
    "NVILAGenerationConfig",
    "Qwen25VLGenerationConfig",
]
