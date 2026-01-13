#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   visualize.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset visualizer module.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from vi.dataset.loaders.types.annotations import (
    PhraseGrounding,
    ViAnnotation,
    Vqa,
    VqaPair,
)

DEFAULT_FONT = ImageFont.load_default()


def visualize_image_with_annotations(
    image_path: Path | str,
    image_width: int,
    image_height: int,
    annotations: list[ViAnnotation],
) -> Image.Image:
    """Visualize an image with annotations overlaid.

    Renders annotations on top of an image including bounding boxes, labels,
    phrase grounding results, and VQA interactions. Supports multiple annotation
    types and automatically handles text wrapping and font sizing.

    Args:
        image_path: Path to the image file to visualize.
        image_width: Original width of the image in pixels.
        image_height: Original height of the image in pixels.
        annotations: List of ViAnnotation objects to render on the image.

    Returns:
        PIL Image object with annotations rendered as overlays.

    Raises:
        ValueError: If annotation type is not supported.
        FileNotFoundError: If the image file cannot be found.

    Example:
        ```python
        from vi.dataset.loaders.utils.visualize import visualize_image_with_annotations
        from pathlib import Path

        # Visualize image with annotations
        image = visualize_image_with_annotations(
            source=Path("./image.jpg"),
            image_width=1920,
            image_height=1080,
            annotations=annotation_list,
        )

        # Display the result
        image.show()

        # Save the visualization
        image.save("annotated_image.png")
        ```

    Note:
        This function supports phrase grounding and VQA annotation types.
        Other annotation types will raise a ValueError. The function
        automatically scales annotations to match the loaded image size.

    See Also:
        - `ViDatasetSplit.visualize()`: Higher-level visualization method
        - `visualize_phrase_grounding()`: Phrase grounding specific visualization
        - `visualize_vqa()`: VQA specific visualization

    """
    image = Image.open(image_path)

    for annotation in annotations:
        if isinstance(annotation.contents, PhraseGrounding):
            image = visualize_phrase_grounding(
                image, image_width, image_height, annotation.contents
            )
        elif isinstance(annotation.contents, Vqa):
            image = visualize_vqa(image, annotation.contents.interactions)
        else:
            raise ValueError(
                f"Unsupported annotation type: {type(annotation.contents)}"
            )

    return image


def _wrap_text(
    text: str, font: ImageFont.ImageFont = DEFAULT_FONT, max_width: int = 300
) -> list[str]:
    """Wrap text to fit within max_width using the given font.

    Args:
        text: The text to wrap.
        font: The font to use for measuring text width.
        max_width: Maximum width in pixels.

    Returns:
        List of text lines that fit within the max width.

    """
    # Create a temporary image to measure text
    temp_img = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    # Split text into words
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        text_width = temp_draw.textlength(test_line, font=font)

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Single word is too long, force it on its own line
                lines.append(word)

    if current_line:
        lines.append(current_line)

    return lines


def _calculate_optimal_font_size(
    interactions: list[VqaPair],
    max_width: int,
    max_height: int,
    min_font_size: int = 8,
    max_font_size: int = 16,
) -> tuple[ImageFont.ImageFont, int]:
    """Calculate optimal font size for VQA interactions.

    Args:
        interactions: List of VQA interaction pairs.
        max_width: Maximum width for text in pixels.
        max_height: Maximum height for text in pixels.
        min_font_size: Minimum allowed font size.
        max_font_size: Maximum allowed font size.

    Returns:
        Tuple of (font, line_height) for rendering.

    """
    # Try different font sizes from largest to smallest
    for font_size in range(max_font_size, min_font_size - 1, -1):
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
            )
        except OSError:
            font = DEFAULT_FONT

        line_height = font_size + 5  # Add some spacing
        total_height = 20  # Top padding

        # Check if all Q&A pairs fit with this font size
        fits = True
        for interaction in interactions:
            question_text = f"Q: {interaction.question}"
            answer_text = f"A: {interaction.answer}"

            # Wrap question and answer
            question_lines = _wrap_text(
                question_text, font, max_width - 20
            )  # Account for padding
            answer_lines = _wrap_text(answer_text, font, max_width - 20)

            total_height += len(question_lines) * line_height
            total_height += len(answer_lines) * line_height
            total_height += 10  # Spacing between Q&A pairs

            if total_height > max_height:
                fits = False
                break

        if fits:
            return font, line_height

    # If nothing fits, return minimum font size
    try:
        min_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", min_font_size
        )
    except OSError:
        min_font = DEFAULT_FONT
    return min_font, min_font_size + 5


def visualize_phrase_grounding(
    image: Image.Image,
    image_width: int,
    image_height: int,
    annotation_contents: PhraseGrounding,
) -> Image.Image:
    """Visualize phrase grounding annotations."""
    caption = annotation_contents.caption

    # Wrap caption text to fit image width
    max_caption_width = image_width - 20  # 10px padding on each side
    caption_lines = _wrap_text(caption, DEFAULT_FONT, max_caption_width)

    # Calculate required caption height
    line_height = 18  # Font size + spacing
    caption_height = len(caption_lines) * line_height + 10  # Extra padding
    new_height = image_height + caption_height

    # Create new image with white background
    new_image = Image.new("RGB", (image_width, new_height), "white")

    # Draw caption lines on top
    draw = ImageDraw.Draw(new_image)
    y_offset = 5
    for line in caption_lines:
        draw.text((10, y_offset), line, fill="black", font=DEFAULT_FONT)
        y_offset += line_height

    # Paste original image below caption
    new_image.paste(image, (0, caption_height))

    # Draw bounding boxes on the pasted image area
    for grounded_phrase in annotation_contents.grounded_phrases:
        bounds = grounded_phrase.bounds
        for xmin, ymin, xmax, ymax in bounds:
            xmin_unnorm = xmin * image_width
            ymin_unnorm = (ymin * image_height) + caption_height
            xmax_unnorm = xmax * image_width
            ymax_unnorm = (ymax * image_height) + caption_height

            # Draw bounding box
            draw.rectangle(
                (xmin_unnorm, ymin_unnorm, xmax_unnorm, ymax_unnorm),
                outline="red",
                width=2,
            )

            # Calculate available width for text within the bounding box
            box_width = xmax_unnorm - xmin_unnorm
            max_text_width = max(
                50, box_width - 10
            )  # Minimum 50px, with 5px padding on each side

            # Wrap the phrase text to fit within the box width
            phrase_lines = _wrap_text(
                grounded_phrase.phrase, DEFAULT_FONT, max_text_width
            )

            # Calculate text positioning at bottom left of box
            text_line_height = 12  # Smaller line height for box labels
            total_text_height = len(phrase_lines) * text_line_height

            # Position text at bottom left, but ensure it doesn't go below the box
            text_start_y = max(
                ymax_unnorm - total_text_height - 2,  # 2px padding from bottom
                ymin_unnorm + 2,  # Don't go above the box
            )

            # Draw each line of the wrapped phrase
            for i, line in enumerate(phrase_lines):
                text_y = text_start_y + (i * text_line_height)

                # Add semi-transparent background for better readability
                text_bbox = draw.textbbox(
                    (xmin_unnorm + 2, text_y), line, font=DEFAULT_FONT
                )
                draw.rectangle(
                    (
                        text_bbox[0] - 1,
                        text_bbox[1] - 1,
                        text_bbox[2] + 1,
                        text_bbox[3] + 1,
                    ),
                    fill=(255, 255, 255, 200),  # Semi-transparent white background
                )

                # Draw the text
                draw.text(
                    (xmin_unnorm + 2, text_y),
                    line,
                    fill="red",
                    font=DEFAULT_FONT,
                )

    return new_image


def visualize_vqa(
    image: Image.Image,
    interactions: list[VqaPair],
) -> Image.Image:
    """Visualize VQA annotations."""
    # Get original image dimensions
    original_width, original_height = image.size

    # Set panel dimensions
    panel_width = min(300, original_width // 2)  # Max 300px or half image width
    panel_height = original_height

    # Calculate optimal font and line height
    optimal_font, line_height = _calculate_optimal_font_size(
        interactions, panel_width, panel_height
    )

    # Create new image with increased width for Q&A panel
    new_width = original_width + panel_width
    new_image = Image.new("RGB", (new_width, original_height), "white")

    # Paste original image on the left
    new_image.paste(image, (0, 0))

    # Draw Q&A panel on the right
    draw = ImageDraw.Draw(new_image)

    # Draw panel background
    panel_x_start = original_width
    draw.rectangle(
        (panel_x_start, 0, new_width, original_height),
        fill=(248, 248, 248),  # Light gray background
        outline=(200, 200, 200),  # Gray border
        width=1,
    )

    # Draw questions and answers with wrapping
    y_offset = 10  # Start with some top padding
    text_x_start = panel_x_start + 10
    max_text_width = panel_width - 20  # Account for padding

    for i, interaction in enumerate(interactions):
        # Draw question with wrapping
        question_text = f"Q{i + 1}: {interaction.question}"
        question_lines = _wrap_text(question_text, optimal_font, max_text_width)

        for line in question_lines:
            if y_offset + line_height > original_height - 10:  # Check bounds
                break
            draw.text(
                (text_x_start, y_offset),
                line,
                fill="black",
                font=optimal_font,
            )
            y_offset += line_height

        # Draw answer with wrapping
        answer_text = f"A{i + 1}: {interaction.answer}"
        answer_lines = _wrap_text(answer_text, optimal_font, max_text_width)

        for line in answer_lines:
            if y_offset + line_height > original_height - 10:  # Check bounds
                break
            draw.text(
                (text_x_start, y_offset),
                line,
                fill="blue",
                font=optimal_font,
            )
            y_offset += line_height

        y_offset += 5  # Extra spacing between Q&A pairs

        # Stop if we're running out of space
        if y_offset > original_height - 30:
            break

    return new_image
