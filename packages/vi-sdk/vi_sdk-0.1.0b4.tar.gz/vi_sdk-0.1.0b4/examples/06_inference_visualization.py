#!/usr/bin/env python3

"""Example script demonstrating inference visualization.

This example shows how to use the inference visualization functions
to visualize predictions from ViModel on images.
"""

from pathlib import Path

from vi.inference import ViModel
from vi.inference.utils.visualize import visualize_prediction


def example_phrase_grounding_visualization():
    """Visualize phrase grounding predictions."""
    print("Example: Phrase Grounding Visualization")
    print("=" * 50)

    # Load model
    model = ViModel(run_id="your-run-id")

    # Run inference (without streaming for visualization)
    image_path = "path/to/your/image.jpg"
    prediction = model(source=image_path, stream=False)

    # Visualize the prediction
    visualized_image = visualize_prediction(
        image_path=Path(image_path),
        prediction=prediction,
    )

    # Display the result
    visualized_image.show()

    # Or save it
    visualized_image.save("phrase_grounding_visualization.png")
    print("Visualization saved to phrase_grounding_visualization.png")


def example_vqa_visualization():
    """Visualize VQA predictions."""
    print("\nExample: VQA Visualization")
    print("=" * 50)

    # Load model with VQA task type
    model = ViModel(run_id="your-run-id", task_type="vqa")

    # Run inference with a question
    image_path = "path/to/your/image.jpg"
    question = "What objects are visible in this image?"
    prediction = model(source=image_path, user_prompt=question, stream=False)

    # Visualize the prediction
    visualized_image = visualize_prediction(
        image_path=Path(image_path),
        prediction=prediction,
    )

    # Display the result
    visualized_image.show()

    # Or save it
    visualized_image.save("vqa_visualization.png")
    print("Visualization saved to vqa_visualization.png")


if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_phrase_grounding_visualization()
    # example_vqa_visualization()

    print("\nNote: Update the run_id and image_path before running these examples.")
    print("\nSupported task types for visualization:")
    print("  - phrase-grounding: Visualize bounding boxes and captions")
    print("  - vqa: Visualize questions and answers")
    print(
        "\nGeneric responses cannot be visualized as they indicate unparseable output."
    )
