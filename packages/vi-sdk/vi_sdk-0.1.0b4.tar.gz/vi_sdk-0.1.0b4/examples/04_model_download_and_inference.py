#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   04_model_download_and_inference.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Model download and inference example.

Model Download and Inference Example.

This example demonstrates:
- Listing training runs
- Downloading trained models
- Loading models for inference (currently supports Qwen2.5-VL and NVILA)
- Running predictions with vision-language models
- Batch inference operations (including folder support)
- Structured output generation

Supported Models:
    - Qwen2.5-VL: Vision-language model for multimodal tasks
    - NVILA: Vision-language model for multimodal tasks

Supported Tasks:
    - Visual Question Answering (VQA): Requires user prompt
    - Phrase Grounding: User prompt is optional

Requirements:
    - Vi SDK installed: pip install vi-sdk[inference]
    - Valid API credentials
    - A completed training run with exported model

Usage:
    python3 04_model_download_and_inference.py
"""

from pathlib import Path

from vi.inference import ViModel


def main():
    """Demonstrate model download and inference operations."""
    # Initialize model with credentials and run ID
    print("📡 Initializing ViModel...")
    model = ViModel(
        secret_key="YOUR_DATATURE_VI_SECRET_KEY",
        organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
        run_id="YOUR_RUN_ID",  # Replace with your actual run ID
        attn_implementation="eager",  # Use flash attention if available
        device_map="auto",  # Automatically distribute across devices
        low_cpu_mem_usage=True,
    )

    print("   ✓ Model loaded successfully!")
    if hasattr(model.loader, "metadata"):
        print(f"   Model name: {model.loader.metadata.get('model_name', 'Unknown')}")
        print(f"   Model size: {model.loader.metadata.get('model_size', 'Unknown')}")

    # Check for test images
    sample_images_dir = Path("./samples")

    if not sample_images_dir.exists() or not list(sample_images_dir.glob("*.jpg")):
        print("\n⚠️  No test images found for inference demo.")
        print("   Download a dataset first to get test images.")
        print("\n✅ Model loading demonstration completed!")
        return

    # Run inference on test images
    test_images = list(sample_images_dir.glob("*.jpg"))[:3]  # First 3 images

    print(f"\n🔮 Running inference on {len(test_images)} test image(s)...")

    for i, image_path in enumerate(test_images, 1):
        print(f"\n   Image {i}: {image_path.name}")

        # Example 1: Visual Question Answering (VQA)
        # Note: VQA requires a user prompt
        print("      Task: Visual Question Answering (VQA)")
        result, error = model(
            source=str(image_path),
            user_prompt="What is in this image?",
            generation_config={"max_new_tokens": 1024},
        )

        if error is None:
            if hasattr(result, "caption"):
                print(f"      Caption: {result.caption[:100]}")
            else:
                print(f"      Result: {str(result)[:100]}")
        else:
            print(f"      ✗ VQA failed: {error}")

        # Example 2: Phrase grounding
        # Note: For Phrase Grounding, user prompt is optional
        # If not provided, the model uses its default prompt
        print("\n      Task: Phrase grounding")
        result, error = model(
            source=str(image_path),
            generation_config={"max_new_tokens": 1024},
        )

        if error is None:
            if hasattr(result, "grounded_phrases"):
                print(f"      Found {len(result.grounded_phrases)} phrases")
                for phrase in result.grounded_phrases[:3]:
                    print(f"         - {phrase.phrase}")
            else:
                print("      No grounded phrases found")
        else:
            print(f"      ✗ Phrase grounding failed: {error}")

    # Batch inference example using native batch support
    print("\n📊 Batch inference example with native batch support...")

    # Convert paths to strings for batch inference
    image_paths = [str(p) for p in test_images]

    # Use native batch inference with progress tracking
    batch_results = model(
        source=image_paths,
        user_prompt="What is in this image?",
        generation_config={"max_new_tokens": 1024},
        show_progress=True,
    )

    # Process results
    successful = 0
    failed = 0
    for image_path, (result, error) in zip(image_paths, batch_results):
        image_name = Path(image_path).name
        print(f"      {image_name}: ", end="")
        if error is None:
            print("✓ Success")
            successful += 1
        else:
            print(f"✗ {error}")
            failed += 1

    print(
        f"   ✓ Processed {len(batch_results)} images ({successful} successful, {failed} failed)"
    )

    # Folder batch inference example
    print("\n📁 Folder batch inference example...")
    print("   Processing entire folder directly...")

    # Process entire folder at once
    folder_results = model(
        source=str(sample_images_dir),  # Pass folder path directly
        user_prompt="What is in this image?",
        generation_config={"max_new_tokens": 1024},
        show_progress=True,
        recursive=False,  # Set to True to search subdirectories
    )

    # Process results
    folder_successful = 0
    folder_failed = 0
    for result, error in folder_results:
        if error is None:
            folder_successful += 1
        else:
            folder_failed += 1

    print(
        f"   ✓ Processed folder: {folder_successful} successful, {folder_failed} failed"
    )

    # Mixed source example: files + folders
    print("\n🔀 Mixed source example (files + folders)...")
    mixed_results = model(
        source=[
            str(test_images[0]),  # Single file
            str(sample_images_dir),  # Entire folder
        ],
        user_prompt="Describe briefly",
        generation_config={"max_new_tokens": 512},
        show_progress=True,
    )

    print(f"   ✓ Processed {len(mixed_results)} images from mixed sources")

    # Model information
    print("\n📋 Model Information:")
    if hasattr(model.loader, "metadata"):
        print(f"   Metadata: {model.loader.metadata}")
    print("   Model loaded: ViModel instance ready for inference")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Model inference completed!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - Test images processed: {len(batch_results)}")
    print(f"   - Successful inferences: {successful}")
    print(f"   - Failed inferences: {failed}")
    print(
        f"   - Folder processed: {folder_successful} successful, {folder_failed} failed"
    )
    print(f"   - Mixed sources: {len(mixed_results)} total images")
    print("\n💡 Next steps:")
    print("   - Integrate inference into your application")
    print("   - Fine-tune prompts for your use case")
    print("   - Use native batch inference for large datasets")
    print("   - Process entire folders with recursive=True")
    print("   - Mix files and folders in the same call")
    print("   - Deploy model to production")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:  # noqa: BLE001
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
