#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   task_types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK task types init module.
"""

from vi.inference.task_types.assistant import (
    GenericResponse,
    PredictionResponse,
    TaskAssistant,
)

__all__ = ["TaskAssistant", "PredictionResponse", "GenericResponse"]
