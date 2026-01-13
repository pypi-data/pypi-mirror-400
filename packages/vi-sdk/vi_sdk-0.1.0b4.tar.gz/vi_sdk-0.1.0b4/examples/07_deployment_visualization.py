#!/usr/bin/env python3

"""Example script demonstrating NIM deployment visualization.

This example shows how to use the deployment visualization functions
to visualize predictions from NIMPredictor on images.
"""

from pathlib import Path

from vi.deployment.nim import NIMPredictor
from vi.inference.utils.visualize import visualize_prediction


def example_nim_phrase_grounding_visualization():
    """Visualize NIM phrase grounding predictions."""
    print("Example: NIM Phrase Grounding Visualization")
    print("=" * 50)

    # Create NIM predictor
    predictor = NIMPredictor(
        model_name="cosmos-reason1-7b",
        task_type="phrase-grounding",
        port=8000,  # Default NIM port
    )

    # Run inference (without streaming for visualization)
    image_path = "path/to/your/image.jpg"
    prediction = predictor(source=image_path, stream=False)

    # Visualize the prediction
    visualized_image = visualize_prediction(
        image_path=Path(image_path),
        prediction=prediction,
    )

    # Display the result
    visualized_image.show()

    # Or save it
    visualized_image.save("nim_phrase_grounding_visualization.png")
    print("Visualization saved to nim_phrase_grounding_visualization.png")


def example_nim_vqa_visualization():
    """Visualize NIM VQA predictions."""
    print("\nExample: NIM VQA Visualization")
    print("=" * 50)

    # Create NIM predictor with VQA task type
    predictor = NIMPredictor(
        model_name="cosmos-reason1-7b",
        task_type="vqa",
        port=8000,
    )

    # Run inference with a question
    image_path = "path/to/your/image.jpg"
    question = "What objects are visible in this image?"
    prediction = predictor(source=image_path, user_prompt=question, stream=False)

    # Visualize the prediction
    visualized_image = visualize_prediction(
        image_path=Path(image_path),
        prediction=prediction,
    )

    # Display the result
    visualized_image.show()

    # Or save it
    visualized_image.save("nim_vqa_visualization.png")
    print("Visualization saved to nim_vqa_visualization.png")


def example_nim_with_custom_port():
    """Visualize NIM predictions with custom port."""
    print("\nExample: NIM with Custom Port")
    print("=" * 50)

    # Create NIM predictor with custom port
    predictor = NIMPredictor(
        model_name="cosmos-reason1-7b",
        task_type="phrase-grounding",
        port=8080,  # Custom port
    )

    # Run inference
    image_path = "path/to/your/image.jpg"
    prediction = predictor(source=image_path, stream=False)

    # Visualize the prediction
    visualized_image = visualize_prediction(
        image_path=Path(image_path),
        prediction=prediction,
    )

    # Display and save
    visualized_image.show()
    visualized_image.save("nim_custom_port_visualization.png")
    print("Visualization saved to nim_custom_port_visualization.png")


def example_batch_visualization():
    """Batch visualize multiple images."""
    print("\nExample: Batch Visualization")
    print("=" * 50)

    # Create NIM predictor
    predictor = NIMPredictor(
        model_name="cosmos-reason1-7b",
        task_type="phrase-grounding",
        port=8000,
    )

    # Process multiple images
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg",
    ]

    for i, image_path in enumerate(image_paths):
        print(f"Processing image {i + 1}/{len(image_paths)}: {image_path}")

        # Run inference
        prediction = predictor(source=image_path, stream=False)

        # Visualize and save
        visualized_image = visualize_prediction(
            image_path=Path(image_path),
            prediction=prediction,
        )
        output_path = f"nim_batch_visualization_{i + 1}.png"
        visualized_image.save(output_path)
        print(f"  Saved: {output_path}")


if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_nim_phrase_grounding_visualization()
    # example_nim_vqa_visualization()
    # example_nim_with_custom_port()
    # example_batch_visualization()

    print("\nNote: Update the model_name, port, and image_path before running.")
    print("Make sure your NIM service is running on the specified port.")
    print("\nSupported task types for visualization:")
    print("  - phrase-grounding: Visualize bounding boxes and captions")
    print("  - vqa: Visualize questions and answers")
