#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   postprocessing.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference postprocessing utilities.
"""

import json
import logging
import re

from vi.inference.task_types import (
    GenericResponse,
    PredictionResponse,
    TaskAssistant,
    consts,
)
from vi.inference.task_types.phrase_grounding import (
    GroundedPhrase,
    PhraseGrounding,
    PhraseGroundingResponse,
)
from vi.inference.task_types.vqa import VQAResponse

logger = logging.getLogger(__name__)


def filter_phrase_groundings(
    response: PhraseGroundingResponse,
    case_sensitive: bool = False,
) -> PhraseGroundingResponse:
    """Filter out phrases that are not exact substrings of the sentence.

    Removes any grounded phrases where the phrase text is not found as an
    exact substring within the sentence/caption. This helps remove garbage
    or hallucinated phrases that the model may generate.

    Args:
        response: The phrase grounding response to filter.
        case_sensitive: If True, performs case-sensitive substring matching.
            If False (default), performs case-insensitive matching.

    Returns:
        A new PhraseGroundingResponse with only valid phrases that are
        substrings of the sentence. The raw_output and thinking fields
        are preserved from the original response.

    Example:
        ```python
        from vi.inference.utils.postprocessing import filter_phrase_groundings

        result = model(source="image.jpg")
        filtered_result = filter_phrase_groundings(result)
        print(
            f"Filtered from {len(result.result.groundings)} to "
            f"{len(filtered_result.result.groundings)} phrases"
        )
        ```

    """
    sentence = response.result.sentence
    original_groundings = response.result.groundings

    if case_sensitive:
        sentence_check = sentence
        valid_groundings = [
            g for g in original_groundings if g.phrase in sentence_check
        ]
    else:
        sentence_lower = sentence.lower()
        valid_groundings = [
            g for g in original_groundings if g.phrase.lower() in sentence_lower
        ]

    filtered_count = len(original_groundings) - len(valid_groundings)
    if filtered_count > 0:
        logger.debug(
            "Filtered out %d invalid phrases (not substrings of sentence)",
            filtered_count,
        )

    # Create new response with filtered groundings
    filtered_phrase_grounding = PhraseGrounding(
        sentence=sentence,
        groundings=[
            GroundedPhrase(phrase=g.phrase, grounding=g.grounding)
            for g in valid_groundings
        ],
    )

    return PhraseGroundingResponse(
        prompt=response.prompt,
        result=filtered_phrase_grounding,
        raw_output=response.raw_output,
        thinking=response.thinking,
    )


# Compiled regex patterns for COT extraction
_THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)
_ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)
_CODE_FENCE_PATTERN = re.compile(r"^```(?:\w+)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def strip_code_fences(text: str) -> str:
    r"""Strip markdown code fences from text.

    Handles formats like:
    - ```json\\n{...}\\n```
    - ```\\n{...}\\n```

    Args:
        text: Text that may contain markdown code fences.

    Returns:
        Text with code fences stripped, or original text if no fences found.

    """
    stripped = text.strip()
    match = _CODE_FENCE_PATTERN.match(stripped)
    return match.group(1).strip() if match else text


def extract_answer_content(text: str) -> str | None:
    """Extract content inside <answer>...</answer> tags.

    Args:
        text: Text that may contain <answer> tags.

    Returns:
        Content inside <answer> tags, or None if no tags found.

    """
    match = _ANSWER_PATTERN.search(text)
    return match.group(1).strip() if match else None


def extract_think_content(text: str) -> str | None:
    """Extract content inside <think>...</think> tags.

    Args:
        text: Text that may contain <think> tags.

    Returns:
        Content inside <think> tags, or None if no tags found.

    """
    match = _THINK_PATTERN.search(text)
    return match.group(1).strip() if match else None


def extract_outside_think(text: str) -> str:
    """Extract content outside all <think>...</think> sections.

    Args:
        text: Text that may contain <think> tags.

    Returns:
        Content outside all <think> sections, concatenated together.

    """
    result = _THINK_PATTERN.sub("", text)
    return strip_code_fences(result.strip())


def extract_json_object(text: str) -> str:
    """Extract the first valid JSON object or array from text.

    Uses json.JSONDecoder.raw_decode to find and extract just the valid JSON,
    ignoring any trailing content (whitespace, garbage, etc.).

    Args:
        text: Text that may contain JSON with trailing content.

    Returns:
        The extracted JSON string, or the original text if no valid JSON found.

    """
    text = text.strip()
    if not text:
        return text

    # Find the start of JSON (first { or [)
    json_start = -1
    for i, char in enumerate(text):
        if char in "{[":
            json_start = i
            break

    if json_start == -1:
        return text

    # Try to parse JSON starting from the found position
    try:
        decoder = json.JSONDecoder()
        _, end_idx = decoder.raw_decode(text, json_start)
        return text[json_start:end_idx]
    except json.JSONDecodeError:
        return text


def extract_content(result: str) -> tuple[str, str | None]:
    """Extract JSON content and thinking from model output.

    Handles various output formats:
    - <think>...</think> tags (COT reasoning)
    - <answer>...</answer> tags (COT structured output)
    - Markdown code blocks (```json...``` or ```...```)
    - Raw JSON

    Args:
        result: Raw model output potentially containing tags or code blocks.

    Returns:
        Tuple of (json_content, thinking_content).
        thinking_content is None if no <think> tags found.

    """
    thinking = extract_think_content(result)

    # Extract JSON from <answer> tags first
    json_content = extract_answer_content(result)

    if json_content is None:
        if thinking is not None:
            # No <answer> tags but <think> tags exist - extract outside <think>
            json_content = extract_outside_think(result)
        else:
            # No COT tags at all
            json_content = result

    # Strip markdown code blocks if present
    json_content = strip_code_fences(json_content)

    # Extract just the valid JSON object, removing any trailing garbage
    json_content = extract_json_object(json_content)

    return json_content, thinking


def parse_result(
    raw_output: str,
    user_prompt: str,
    task_type: consts.TaskType,
    schema: type[TaskAssistant] | None,
) -> PredictionResponse:
    """Parse generated output into appropriate response type.

    Automatically extracts JSON from COT tags (<answer>...</answer>)
    and markdown code blocks if present. Also extracts thinking content
    from <think>...</think> tags.

    Args:
        raw_output: Raw model output (may contain COT tags or code blocks).
        user_prompt: The user prompt used for inference.
        task_type: The task type (VQA, PHRASE_GROUNDING, GENERIC).
        schema: The schema class for parsing (TaskAssistant subclass).

    Returns:
        Parsed prediction response based on task type. Includes raw_output
        and thinking fields. If parsing fails, returns GenericResponse
        with the full raw output.

    """
    json_content, thinking = extract_content(raw_output)

    # For generic task type, return raw output directly
    if task_type == consts.TaskType.GENERIC:
        return GenericResponse(
            prompt=user_prompt,
            result=raw_output,
            raw_output=raw_output,
            thinking=thinking,
        )

    # Try to parse JSON for structured task types
    try:
        if schema is None:
            raise ValueError("Schema is required for structured task types")

        assistant = schema.model_validate_json(json_content)

        if task_type == consts.TaskType.VQA:
            return VQAResponse(
                prompt=user_prompt,
                result=assistant.vqa,
                raw_output=raw_output,
                thinking=thinking,
            )

        if task_type == consts.TaskType.PHRASE_GROUNDING:
            return PhraseGroundingResponse(
                prompt=user_prompt,
                result=assistant.phrase_grounding,
                raw_output=raw_output,
                thinking=thinking,
            )

        # All known task types should be handled above
        # If we reach here, it's a programming error - new task type added without handler
        raise ValueError(f"Unhandled task type: {task_type}")

    except Exception as e:
        logger.warning(
            "Failed to parse structured output: %s. "
            "json_content (repr): %r, raw_output length: %d",
            e,
            json_content[:200] if len(json_content) > 200 else json_content,
            len(raw_output),
        )
        return GenericResponse(
            prompt=user_prompt,
            result=raw_output,
            raw_output=raw_output,
            thinking=thinking,
        )
