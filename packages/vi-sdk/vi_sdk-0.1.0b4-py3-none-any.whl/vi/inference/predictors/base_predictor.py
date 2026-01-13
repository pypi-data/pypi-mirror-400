#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   base_predictor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK base predictor module.
"""

from abc import ABC, abstractmethod
from typing import Any

from vi.inference.loaders.base_loader import BaseLoader


class BasePredictor(ABC):
    """Base class for model predictors with common interface.

    Abstract base class defining the interface for running model inference.
    Provides a common structure for predictor implementations to ensure
    consistent behavior across different model types and task types.

    """

    @abstractmethod
    def __init__(self, loader: BaseLoader):
        """Initialize predictor with a loaded model.

        Args:
            loader: Loaded model instance.

        """

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Run model prediction on input data.

        Executes model inference using the provided inputs and returns task-specific
        predictions. The exact signature and return type depend on the concrete
        implementation and task type (VQA, phrase grounding, etc.).

        Args:
            *args: Positional arguments for prediction (typically source, prompt).
            **kwargs: Keyword arguments for prediction (typically generation parameters).

        Returns:
            Task-specific prediction results. Format depends on the model's training task.

        """
