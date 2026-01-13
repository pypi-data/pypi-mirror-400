#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   annotations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset loaders annotations types module.
"""

import json
from collections.abc import Generator, Iterator
from pathlib import Path

import msgspec
from vi.api.resources.datasets.annotations.consts import (
    SUPPORTED_ANNOTATION_FILE_EXTENSIONS,
)
from vi.dataset.loaders.types.assets import Image
from vi.dataset.loaders.types.base import ViDatasetLoaderStruct


class GroundedPhrase(ViDatasetLoaderStruct):
    """Grounded phrase struct.

    Attributes:
        phrase: The text phrase being grounded.
        start_token_index: Starting token index of the phrase in the caption.
        end_token_index: Ending token index of the phrase in the caption.
        bounds: List of 4 coordinate pairs [x, y] defining the bounding box.

    """

    phrase: str
    start_token_index: int
    end_token_index: int
    bounds: list[list[float]]


class PhraseGrounding(ViDatasetLoaderStruct, tag_field="type"):
    """Phrase grounding struct.

    Attributes:
        caption: The full caption text.
        grounded_phrases: List of phrases with their corresponding bounding boxes.

    """

    caption: str
    grounded_phrases: list[GroundedPhrase]


class VqaPair(ViDatasetLoaderStruct):
    """VQA pairs struct.

    Attributes:
        order: The sequence order of this QA pair in the conversation.
        question: The question text.
        answer: The answer text.

    """

    order: int
    question: str
    answer: str


class Vqa(ViDatasetLoaderStruct, tag_field="type"):
    """VQA struct.

    Attributes:
        interactions: List of question-answer pairs in conversation order.

    """

    interactions: list[VqaPair]


ViAnnotationContents = PhraseGrounding | Vqa


class ViAnnotation(ViDatasetLoaderStruct):
    """Annotation struct.

    Attributes:
        id: Unique identifier for the annotation.
        asset: Image asset this annotation belongs to.
        contents: Annotation content (PhraseGrounding or VQA).
        category: Optional category label for the annotation.

    """

    id: str
    asset: Image
    contents: ViAnnotationContents
    category: str | None = None


class ViAnnotations(ViDatasetLoaderStruct):
    """Annotations struct.

    Attributes:
        annotations_dir: Path to the directory containing annotation JSONL files.

    """

    annotations_dir: Path | None

    def __post_init__(self):
        """Validate annotations directory exists."""
        if self.annotations_dir is None:
            return
        if not self.annotations_dir.exists():
            raise FileNotFoundError(
                f"Annotations directory not found: {self.annotations_dir}"
            )
        if not self.annotations_dir.is_dir():
            raise RuntimeError(
                f"Annotations path is not a directory: {self.annotations_dir}"
            )

    def __iter__(self) -> Iterator[list[ViAnnotation]]:
        """Iterate over annotation lists.

        Returns:
            Iterator of annotation lists (one list per asset).

        """
        return self.items

    def __len__(self) -> int:
        """Count lines efficiently without parsing JSON.

        Returns:
            Total number of annotation lines in all JSONL files.

        """
        if self.annotations_dir is None:
            return 0
        count = 0
        for annotation_file in self.annotations_dir.iterdir():
            if (
                annotation_file.is_file()
                and annotation_file.suffix in SUPPORTED_ANNOTATION_FILE_EXTENSIONS
            ):
                try:
                    with open(annotation_file, encoding="utf-8") as f:
                        count += sum(1 for line in f if line.strip())
                except OSError as e:
                    raise RuntimeError(
                        f"Failed to read annotations file {annotation_file}: {e}"
                    ) from e
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to read annotations file {annotation_file}: {e}"
                    ) from e

        return count

    @property
    def items(self) -> Generator[list[ViAnnotation], None, None]:
        """Lazily load and sort annotations from JSONL files.

        Yields:
            Lists of ViAnnotation objects, one list per JSONL file.

        Raises:
            RuntimeError: If unable to read or parse annotation files.

        """
        if self.annotations_dir is None:
            return
        sorted_files = sorted(
            (
                f
                for f in self.annotations_dir.iterdir()
                if f.is_file() and f.suffix in SUPPORTED_ANNOTATION_FILE_EXTENSIONS
            ),
            key=lambda x: x.name,
        )

        for annotation_file in sorted_files:
            try:
                with open(annotation_file, encoding="utf-8") as f:
                    annotations = []
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:  # Skip empty lines
                            continue

                        try:
                            annotation = msgspec.json.decode(line, type=ViAnnotation)
                            annotations.append(annotation)
                        except json.JSONDecodeError as e:
                            raise RuntimeError(
                                f"Invalid JSON on line {line_num} in {annotation_file}: {e}"
                            ) from e
                        except Exception as e:
                            raise RuntimeError(
                                f"Failed to convert data on line {line_num}"
                                f"in {annotation_file}: {e}"
                            ) from e
                    yield annotations
            except OSError as e:
                raise RuntimeError(
                    f"Failed to read annotations file {annotation_file}: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"Failed to read annotations file {annotation_file}: {e}"
                ) from e
