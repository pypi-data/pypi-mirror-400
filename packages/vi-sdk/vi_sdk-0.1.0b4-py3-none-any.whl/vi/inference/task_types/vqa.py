#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   vqa.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK visual question answering assistant type module.
"""

from pydantic import BaseModel, Field
from vi.inference.task_types.assistant import PredictionResponse, TaskAssistant


class VQAPair(BaseModel):
    """Visual question answering pair object.

    Used for VQA task type which is currently supported for Qwen2.5-VL models.
    User prompt is required in the form of a question.

    Attributes:
        question: The question text (minimum 1 character).
        answer: The answer text (minimum 1 character).

    """

    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class VQA(BaseModel):
    """Visual question answering object.

    VQA is one of the two currently supported task types for Qwen2.5-VL models.
    User prompt is required in the form of a question. More task types will be
    supported in future releases.

    Attributes:
        interactions: List of question-answer pairs (minimum 1 pair).

    """

    interactions: list[VQAPair] = Field(..., min_length=1)


class VQAAnswer(BaseModel):
    """Visual question answering answer object.

    Attributes:
        answer: The answer text (minimum 1 character).

    """

    answer: str = Field(..., min_length=1)


class VQAAssistant(TaskAssistant):
    """Structured model output for visual question answering.

    VQA is one of the two currently supported task types for Qwen2.5-VL models.
    When using VQA, a user prompt is required in the form of a question.

    Attributes:
        vqa: The VQA result containing interactions.

    """

    vqa: VQAAnswer


class VQAResponse(PredictionResponse):
    """VQA response object.

    Attributes:
        result: The VQA answer result.

    """

    result: VQAAnswer
