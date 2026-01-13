#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   visualize.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference visualizer module.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from vi.inference.task_types.assistant import GenericResponse, PredictionResponse
from vi.inference.task_types.phrase_grounding import (
    GroundedPhrase,
    PhraseGrounding,
    PhraseGroundingResponse,
)
from vi.inference.task_types.vqa import VQAAnswer, VQAResponse

DEFAULT_FONT = ImageFont.load_default()
BBOX_COORDINATE_RANGE = 1024  # Inference uses [0, 1024] coordinate range


def visualize_prediction(
    image_path: Path | str,
    prediction: PredictionResponse,
) -> Image.Image:
    """Visualize a prediction result on an image.

    Renders prediction results on top of an image including bounding boxes, labels,
    phrase grounding results, and VQA answers. Supports multiple prediction types
    and automatically handles text wrapping and font sizing.

    Args:
        image_path: Path to the image file to visualize.
        prediction: PredictionResponse object containing the prediction results.

    Returns:
        PIL Image object with predictions rendered as overlays.

    Raises:
        ValueError: If prediction type is not supported.
        FileNotFoundError: If the image file cannot be found.

    Example:
        ```python
        from vi.inference import ViModel
        from vi.inference.utils.visualize import visualize_prediction
        from pathlib import Path

        # Load model and run inference
        model = ViModel(run_id="your-run")
        prediction = model(source="image.jpg", stream=False)

        # Visualize the prediction
        image = visualize_prediction(
            image_path=Path("./image.jpg"),
            prediction=prediction,
        )

        # Display the result
        image.show()

        # Save the visualization
        image.save("prediction_visualization.png")
        ```

    Note:
        This function supports PhraseGroundingResponse and VQAResponse prediction
        types. GenericResponse is not supported as it indicates the model output
        could not be parsed into a structured format. The function automatically
        scales predictions from the [0, 1024] coordinate space to the image size.

    See Also:
        - `visualize_phrase_grounding()`: Phrase grounding specific visualization
        - `visualize_vqa()`: VQA specific visualization

    """
    image = Image.open(image_path)

    if isinstance(prediction, PhraseGroundingResponse):
        image = visualize_phrase_grounding(image, prediction.result)
    elif isinstance(prediction, VQAResponse):
        image = visualize_vqa(image, prediction.result, prediction.prompt)
    elif isinstance(prediction, GenericResponse):
        raise ValueError(
            f"Unsupported prediction type: {type(prediction).__name__}. "
            "GenericResponse cannot be visualized as the JSON structure could not be "
            "parsed into a supported format (PhraseGrounding or VQA). "
            "Please ensure your model output follows the expected schema."
        )
    else:
        raise ValueError(f"Unsupported prediction type: {type(prediction).__name__}")

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
    text: str,
    max_width: int,
    max_height: int,
    min_font_size: int = 8,
    max_font_size: int = 16,
) -> tuple[ImageFont.ImageFont, int]:
    """Calculate optimal font size for text rendering.

    Args:
        text: Text to render.
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

        # Wrap text and check if it fits
        lines = _wrap_text(text, font, max_width - 20)  # Account for padding
        total_height = len(lines) * line_height + 20  # Add top padding

        if total_height <= max_height:
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
    phrase_grounding: PhraseGrounding,
) -> Image.Image:
    """Visualize phrase grounding predictions on an image.

    Args:
        image: PIL Image to draw on.
        phrase_grounding: PhraseGrounding result containing sentence and groundings.

    Returns:
        PIL Image with phrase grounding visualization.

    """
    image_width, image_height = image.size
    sentence = phrase_grounding.sentence

    # Wrap sentence text to fit image width
    max_sentence_width = image_width - 20  # 10px padding on each side
    sentence_lines = _wrap_text(sentence, DEFAULT_FONT, max_sentence_width)

    # Calculate required sentence height
    line_height = 18  # Font size + spacing
    sentence_height = len(sentence_lines) * line_height + 10  # Extra padding
    new_height = image_height + sentence_height

    # Create new image with white background
    new_image = Image.new("RGB", (image_width, new_height), "white")

    # Draw sentence lines on top
    draw = ImageDraw.Draw(new_image)
    y_offset = 5
    for line in sentence_lines:
        draw.text((10, y_offset), line, fill="black", font=DEFAULT_FONT)
        y_offset += line_height

    # Paste original image below sentence
    new_image.paste(image, (0, sentence_height))

    # Draw bounding boxes on the pasted image area
    for grounded_phrase in phrase_grounding.groundings:
        _draw_grounded_phrase(
            draw, grounded_phrase, image_width, image_height, sentence_height
        )

    return new_image


def _draw_grounded_phrase(
    draw: ImageDraw.ImageDraw,
    grounded_phrase: GroundedPhrase,
    image_width: int,
    image_height: int,
    y_offset: int = 0,
) -> None:
    """Draw a grounded phrase with its bounding boxes.

    Args:
        draw: ImageDraw object to draw on.
        grounded_phrase: GroundedPhrase containing phrase text and bounding boxes.
        image_width: Width of the original image.
        image_height: Height of the original image.
        y_offset: Vertical offset to apply to all coordinates (for sentence space).

    """
    for bbox in grounded_phrase.grounding:
        # Convert from [0, 1024] coordinate space to pixel coordinates
        xmin = (bbox[0] / BBOX_COORDINATE_RANGE) * image_width
        ymin = (bbox[1] / BBOX_COORDINATE_RANGE) * image_height + y_offset
        xmax = (bbox[2] / BBOX_COORDINATE_RANGE) * image_width
        ymax = (bbox[3] / BBOX_COORDINATE_RANGE) * image_height + y_offset

        # Draw bounding box
        draw.rectangle(
            (xmin, ymin, xmax, ymax),
            outline="red",
            width=2,
        )

        # Calculate available width for text within the bounding box
        box_width = xmax - xmin
        max_text_width = max(
            50, box_width - 10
        )  # Minimum 50px, with 5px padding on each side

        # Wrap the phrase text to fit within the box width
        phrase_lines = _wrap_text(grounded_phrase.phrase, DEFAULT_FONT, max_text_width)

        # Calculate text positioning at bottom left of box
        text_line_height = 12  # Smaller line height for box labels
        total_text_height = len(phrase_lines) * text_line_height

        # Position text at bottom left, but ensure it doesn't go below the box
        text_start_y = max(
            ymax - total_text_height - 2,  # 2px padding from bottom
            ymin + 2,  # Don't go above the box
        )

        # Draw each line of the wrapped phrase
        for i, line in enumerate(phrase_lines):
            text_y = text_start_y + (i * text_line_height)

            # Add semi-transparent background for better readability
            text_bbox = draw.textbbox((xmin + 2, text_y), line, font=DEFAULT_FONT)
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
                (xmin + 2, text_y),
                line,
                fill="red",
                font=DEFAULT_FONT,
            )


def visualize_vqa(
    image: Image.Image,
    vqa_answer: VQAAnswer,
    question: str,
) -> Image.Image:
    """Visualize VQA question and answer on an image.

    Args:
        image: PIL Image to draw on.
        vqa_answer: VQAAnswer result containing the answer.
        question: The question that was asked.

    Returns:
        PIL Image with VQA visualization.

    """
    # Get original image dimensions
    original_width, original_height = image.size

    # Set panel dimensions
    panel_width = min(300, original_width // 2)  # Max 300px or half image width
    panel_height = original_height

    # Calculate optimal font and line height
    combined_text = f"Q: {question}\nA: {vqa_answer.answer}"
    optimal_font, line_height = _calculate_optimal_font_size(
        combined_text, panel_width, panel_height
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

    # Draw question and answer with wrapping
    y_offset = 10  # Start with some top padding
    text_x_start = panel_x_start + 10
    max_text_width = panel_width - 20  # Account for padding

    # Draw question with wrapping
    question_text = f"Q: {question}"
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

    y_offset += 5  # Extra spacing between Q and A

    # Draw answer with wrapping
    answer_text = f"A: {vqa_answer.answer}"
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

    return new_image
