#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   05_annotation_workflows.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Annotation workflows example.

Annotation Workflows Example.

This example demonstrates:
- Uploading annotations from files
- Listing and filtering annotations
- Downloading annotations
- Creating annotations programmatically
- Validating annotation format
- Updating existing annotations

Requirements:
    - Vi SDK installed: pip install vi-sdk
    - Valid API credentials
    - A dataset with assets

Usage:
    python3 05_annotation_workflows.py
"""

import json
import os
from pathlib import Path

import vi


def create_sample_annotations(output_file: str = "sample_annotations.jsonl"):
    """Create sample annotations for demonstration."""
    print("\n📝 Creating sample annotations...")

    # Sample annotations
    annotations = [
        {
            "asset_id": "sample_asset_1",
            "caption": "A red car parked on a city street",
            "grounded_phrases": [
                {
                    "phrase": "red car",
                    "bbox": [
                        0.2,
                        0.3,
                        0.6,
                        0.7,
                    ],  # [x_min, y_min, x_max, y_max] normalized
                },
                {"phrase": "city street", "bbox": [0.0, 0.6, 1.0, 1.0]},
            ],
        },
        {
            "asset_id": "sample_asset_2",
            "caption": "A person walking a dog in a park",
            "grounded_phrases": [
                {"phrase": "person", "bbox": [0.3, 0.2, 0.5, 0.8]},
                {"phrase": "dog", "bbox": [0.5, 0.5, 0.7, 0.9]},
            ],
        },
        {
            "asset_id": "sample_asset_3",
            "caption": "A sunset over mountains with orange sky",
        },
    ]

    # Write to JSONL format
    with open(output_file, "w", encoding="utf-8") as f:
        for annotation in annotations:
            json.dump(annotation, f)
            f.write("\n")

    print(f"   ✓ Created {len(annotations)} sample annotations")
    print(f"   File: {output_file}")
    return output_file


def validate_annotation(annotation: dict) -> tuple[bool, str]:
    """Validate annotation format.

    Args:
        annotation: Annotation dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)

    """
    # Check required field
    if "asset_id" not in annotation:
        return False, "Missing required field: asset_id"

    # Validate caption if present
    if "caption" in annotation:
        if not isinstance(annotation["caption"], str):
            return False, "Caption must be a string"
        if len(annotation["caption"]) == 0:
            return False, "Caption cannot be empty"

    # Validate grounded phrases if present
    if "grounded_phrases" in annotation:
        if not isinstance(annotation["grounded_phrases"], list):
            return False, "grounded_phrases must be a list"

        for i, phrase in enumerate(annotation["grounded_phrases"]):
            # Check required fields
            if "phrase" not in phrase:
                return False, f"Phrase {i}: missing 'phrase' field"
            if "bbox" not in phrase:
                return False, f"Phrase {i}: missing 'bbox' field"

            # Validate bbox
            bbox = phrase["bbox"]
            if not isinstance(bbox, list) or len(bbox) != 4:
                return False, f"Phrase {i}: bbox must be list of 4 values"

            # Check bbox is normalized (0-1)
            if not all(0 <= coord <= 1 for coord in bbox):
                return False, f"Phrase {i}: bbox coordinates must be normalized (0-1)"

            # Check bbox is valid (min < max)
            if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
                return False, f"Phrase {i}: invalid bbox (x_min < x_max, y_min < y_max)"

    return True, "Valid"


def validate_annotations_file(file_path: str) -> tuple[int, int]:
    """Validate all annotations in a file.

    Args:
        file_path: Path to JSONL file

    Returns:
        Tuple of (valid_count, invalid_count)

    """
    print(f"\n🔍 Validating annotations in {file_path}...")

    valid_count = 0
    invalid_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                annotation = json.loads(line)
                is_valid, message = validate_annotation(annotation)

                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"   ✗ Line {line_num}: {message}")

            except json.JSONDecodeError as e:
                invalid_count += 1
                print(f"   ✗ Line {line_num}: Invalid JSON - {e}")

    print(f"\n   Valid: {valid_count}")
    print(f"   Invalid: {invalid_count}")

    return valid_count, invalid_count


def main():
    """Demonstrate annotation workflows."""
    # Initialize client
    print("📡 Initializing Vi SDK client...")
    client = vi.Client(
        secret_key="YOUR_DATATURE_VI_SECRET_KEY",
        organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
    )

    # List datasets
    print("\n📊 Listing datasets...")
    datasets = client.datasets.list()

    if not datasets.items:
        print("   ✗ No datasets found!")
        print("   💡 Create a dataset first using the platform or SDK")
        return

    # Select first dataset
    selected_dataset = datasets.items[0]
    dataset_id = selected_dataset.dataset_id

    print(f"\n🎯 Selected dataset: {selected_dataset.name}")
    print(f"   ID: {dataset_id}")

    # Create sample annotations
    annotations_file = create_sample_annotations()

    # Validate annotations before upload
    valid_count, invalid_count = validate_annotations_file(annotations_file)

    if invalid_count > 0:
        print(f"\n⚠️  Found {invalid_count} invalid annotations!")
        print("   Fix these before uploading")
        return

    print("\n✓ All annotations are valid!")

    # Check if dataset has assets
    print("\n🔍 Checking dataset assets...")
    assets = client.assets.list(dataset_id=dataset_id)

    if not assets.items:
        print("   ⚠️  No assets in dataset!")
        print("   💡 Upload assets before annotations")
        print("\n   Note: Sample annotations use placeholder asset IDs")
        print("   In production, ensure asset_ids match actual assets")

        # Don't upload if no assets
        print("\n📌 Skipping upload (no matching assets)")
    else:
        print(f"   Found {len(assets.items)} assets")

        # Update sample annotations with real asset IDs
        print("\n🔄 Updating sample annotations with real asset IDs...")
        real_annotations_file = "real_annotations.jsonl"

        with (
            open(annotations_file, "r", encoding="utf-8") as fin,
            open(real_annotations_file, "w", encoding="utf-8") as fout,
        ):
            for i, line in enumerate(fin):
                annotation = json.loads(line)
                if i < len(assets.items):
                    # Use real asset ID
                    annotation["asset_id"] = assets.items[i].asset_id
                    json.dump(annotation, fout)
                    fout.write("\n")

        print("   ✓ Updated annotations with real asset IDs")
        annotations_file = real_annotations_file

        # Upload annotations
        print("\n⬆️  Uploading annotations...")
        try:
            result = client.annotations.upload(
                dataset_id=dataset_id,
                paths=annotations_file,
                wait_until_done=True,
            )

            print("\n   ✓ Upload complete!")
            print(f"   Session ID: {result.session_id}")
            print(f"   Total annotations: {result.total_annotations}")
            print(result.summary())

        except Exception as e:
            print(f"   ✗ Upload failed: {e}")
            return

    # List annotations
    print("\n📋 Listing annotations...")
    try:
        if not assets.items:
            print("   ⚠️  No assets to list annotations for")
        else:
            # List annotations for the first asset
            sample_asset_id = assets.items[0].asset_id
            annotations_response = client.annotations.list(
                dataset_id=dataset_id, asset_id=sample_asset_id
            )

            print(
                f"   Found {len(annotations_response.items)} annotations for asset {sample_asset_id}"
            )

            # Show first few annotations
            for i, annotation in enumerate(annotations_response.items[:5], 1):
                print(f"\n   {i}. Annotation ID: {annotation.annotation_id}")
                print(f"      Asset ID: {annotation.asset_id}")

                # Show caption if available
                if hasattr(annotation, "caption") and annotation.caption:
                    print(f"      Caption: {annotation.caption[:60]}...")

                # Show grounded phrases if available
                if (
                    hasattr(annotation, "grounded_phrases")
                    and annotation.grounded_phrases
                ):
                    print(f"      Grounded phrases: {len(annotation.grounded_phrases)}")
                    for phrase in annotation.grounded_phrases[:2]:
                        if hasattr(phrase, "phrase"):
                            print(f"         - {phrase.phrase}")

    except Exception as e:
        print(f"   ✗ Failed to list annotations: {e}")

    # Download annotations
    print("\n⬇️  Downloading annotations...")
    try:
        downloaded = client.get_dataset(
            dataset_id=dataset_id,
            annotations_only=True,
            save_dir="./downloaded_annotations",
        )

        print(f"   ✓ Downloaded to: {downloaded.save_dir}")

        # Check downloaded files
        annotations_dir = Path(downloaded.save_dir) / dataset_id
        if annotations_dir.exists():
            print("\n   📁 Downloaded structure:")
            for split_dir in ["training", "validation", "dump"]:
                split_path = annotations_dir / split_dir
                if split_path.exists():
                    print(f"      {split_dir}/")
                    annotations_path = split_path / "annotations"
                    if annotations_path.exists():
                        files = list(annotations_path.glob("*.jsonl"))
                        print(f"         annotations/ ({len(files)} files)")

    except Exception as e:
        print(f"   ✗ Download failed: {e}")

    # Cleanup sample files
    print("\n🧹 Cleaning up...")
    for file in [
        annotations_file,
        "sample_annotations.jsonl",
        "real_annotations.jsonl",
    ]:
        if os.path.exists(file):
            os.remove(file)
            print(f"   ✓ Removed {file}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Annotation workflows demonstration completed!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - Dataset: {selected_dataset.name}")
    print("   - Validation: ✓ Passed")
    if assets.items:
        print("   - Upload: ✓ Completed")
        print(f"   - Annotations processed: {valid_count}")
    else:
        print("   - Upload: Skipped (no assets)")

    print("\n💡 Next steps:")
    print("   - Upload more annotations for your assets")
    print("   - Use annotations for model training")
    print("   - Download and visualize annotated data")
    print("   - Generate annotations using inference")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
