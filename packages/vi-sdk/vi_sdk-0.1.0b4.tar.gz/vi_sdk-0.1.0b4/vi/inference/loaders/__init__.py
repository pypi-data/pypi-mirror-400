#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   __init__.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK loaders init module.
"""

from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.loaders.loader_registry import LoaderRegistry

__all__ = ["BaseLoader", "LoaderRegistry"]


def __getattr__(name: str):
    """Lazy load concrete loader classes to avoid eager dependency checks.

    This prevents check_imports from running until a loader is actually used.
    """
    if name == "DeepSeekOCRLoader":
        from vi.inference.loaders.architectures.deepseekocr import DeepSeekOCRLoader

        return DeepSeekOCRLoader

    if name == "NVILALoader":
        from vi.inference.loaders.architectures.nvila import NVILALoader

        return NVILALoader

    if name == "Qwen25VLLoader":
        from vi.inference.loaders.architectures.qwen25vl import Qwen25VLLoader

        return Qwen25VLLoader

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
