#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   __init__.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK predictors init module.
"""

from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.predictors.predictor_registry import PredictorRegistry
from vi.inference.predictors.streaming import StreamingMixin

__all__ = ["BasePredictor", "PredictorRegistry", "StreamingMixin"]


def __getattr__(name: str):
    """Lazy load concrete predictor classes to avoid eager dependency checks.

    This prevents check_imports from running until a predictor is actually used.
    """
    if name == "DeepSeekOCRPredictor":
        from vi.inference.predictors.architectures.deepseekocr import (
            DeepSeekOCRPredictor,
        )

        return DeepSeekOCRPredictor

    if name == "NVILAPredictor":
        from vi.inference.predictors.architectures.nvila import NVILAPredictor

        return NVILAPredictor

    if name == "Qwen25VLPredictor":
        from vi.inference.predictors.architectures.qwen25vl import Qwen25VLPredictor

        return Qwen25VLPredictor

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
