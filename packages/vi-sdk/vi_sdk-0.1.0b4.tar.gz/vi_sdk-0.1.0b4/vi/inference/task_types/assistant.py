#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   assistant.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assistant type module.
"""

from msgspec import Struct
from pydantic import BaseModel

DEFAULT_BOUNDING_BOX_LENGTH = 4
DEFAULT_BOUNDING_BOX_COORDINATE_RANGE = 1024


class TaskAssistant(BaseModel):
    """Structured model output for a task.

    Base class for task-specific assistant outputs (VQA, PhraseGrounding, etc.).
    """


class PredictionResponse(Struct, kw_only=True):
    """Prediction response object.

    Base class for task-specific prediction responses (VQA, PhraseGrounding, etc.).

    Attributes:
        prompt: The user prompt used for inference.
        raw_output: The raw model output string (includes thinking and answer tags if COT enabled).
        thinking: The extracted content from <think>...</think> tags (None if not present).

    """

    prompt: str
    raw_output: str | None = None
    thinking: str | None = None


class GenericResponse(PredictionResponse):
    """Generic response object.

    Used for generic task type which is currently supported for all models.
    When JSON parsing fails or for generic tasks, result contains the full raw output
    (including thinking and answer content if COT is enabled).

    Attributes:
        result: The raw output string (may include thinking and answer content).

    """

    result: str
