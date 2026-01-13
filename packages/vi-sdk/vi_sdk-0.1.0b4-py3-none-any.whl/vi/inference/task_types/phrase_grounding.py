#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   phrase_grounding.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK phrase grounding assistant type module.
"""

from typing import Annotated

from pydantic import BaseModel, Field
from vi.inference.task_types.assistant import (
    DEFAULT_BOUNDING_BOX_COORDINATE_RANGE,
    DEFAULT_BOUNDING_BOX_LENGTH,
    PredictionResponse,
    TaskAssistant,
)


class GroundedPhrase(BaseModel):
    """Text that has an associated bounding box.

    Used for Phrase Grounding task type which is currently supported for Qwen2.5-VL models.
    User prompt is optional for Phrase Grounding (uses default prompt if not provided).

    Attributes:
        phrase: The text phrase (minimum 1 character).
        grounding: List of bounding boxes, each with 4 coordinates
            [xmin, ymin, xmax, ymax] in range [0, 1024].

    """

    phrase: str = Field(..., min_length=1)
    grounding: list[
        Annotated[
            list[Annotated[int, Field(ge=0, le=DEFAULT_BOUNDING_BOX_COORDINATE_RANGE)]],
            Field(
                min_length=DEFAULT_BOUNDING_BOX_LENGTH,
                max_length=DEFAULT_BOUNDING_BOX_LENGTH,
            ),
        ]
    ] = Field(..., min_length=1)


class PhraseGrounding(BaseModel):
    """Phrase grounding object.

    Phrase Grounding is one of the two currently supported task types for Qwen2.5-VL models.
    User prompt is optional (uses default prompt if not provided). More task types will be
    supported in future releases.

    Attributes:
        sentence: The full sentence/caption text (minimum 1 character).
        groundings: List of grounded phrases with bounding boxes (minimum 1).

    """

    sentence: str = Field(..., min_length=1)
    groundings: list[GroundedPhrase] = Field(..., min_length=1)


class PhraseGroundingAssistant(TaskAssistant):
    """Structured model output for phrase grounding.

    Phrase Grounding is one of the two currently supported task types for Qwen2.5-VL models.
    When using Phrase Grounding, the user prompt is optional (uses default prompt if not provided).

    Attributes:
        phrase_grounding: The phrase grounding result.

    """

    phrase_grounding: PhraseGrounding = Field(...)


class PhraseGroundingResponse(PredictionResponse):
    """Phrase grounding response object.

    Attributes:
        result: The phrase grounding result.

    """

    result: PhraseGrounding
