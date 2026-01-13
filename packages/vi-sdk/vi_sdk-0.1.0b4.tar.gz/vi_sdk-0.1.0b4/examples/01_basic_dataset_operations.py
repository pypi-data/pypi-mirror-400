#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   01_basic_dataset_operations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Basic dataset operations example.

This example demonstrates fundamental dataset operations:
- Initializing the client
- Listing datasets
- Getting dataset details
- Creating dataset exports
- Downloading datasets

Requirements:
    - Vi SDK installed: pip install vi-sdk
    - Valid API credentials (set as environment variables or in config file)

Usage:
    python3 01_basic_dataset_operations.py
"""

from pathlib import Path

import vi
from vi.api.resources.datasets.types import DatasetExportFormat, DatasetExportSettings


def main():
    """Run basic dataset operations."""
    # Initialize client
    print("📡 Initializing Vi SDK client...")
    client = vi.Client(
        secret_key="YOUR_DATATURE_VI_SECRET_KEY",
        organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
    )

    # Get organization info
    print("\n🏢 Organization Info:")
    org = client.organizations.info()
    print(f"   Name: {org.name}")
    print(f"   ID: {org.organization_id}")
    print(f"   Datasets: {len(org.datasets)}")

    # List all datasets
    print("\n📊 Listing datasets:")
    datasets_response = client.datasets.list()

    if not datasets_response.items:
        print("   No datasets found!")
        print("\n💡 Tip: Create a dataset on Datature Vi first.")
        return

    # Display first 5 datasets
    for i, dataset in enumerate(datasets_response.items[:5], 1):
        print(f"\n   {i}. {dataset.name}")
        print(f"      ID: {dataset.dataset_id}")
        print(f"      Type: {dataset.type.value}")
        print(f"      Assets: {dataset.statistic.asset_total}")
        print(f"      Annotations: {dataset.statistic.annotation_total}")
        print(f"      Created: {dataset.create_date}")

    # Select first dataset for detailed operations
    selected_dataset = datasets_response.items[0]
    dataset_id = selected_dataset.dataset_id

    print(f"\n🎯 Selected dataset: {selected_dataset.name}")

    # Get detailed dataset information
    print(f"\n📋 Getting detailed info for '{selected_dataset.name}'...")
    dataset_details = client.datasets.get(dataset_id)

    print(f"   Owner: {dataset_details.owner}")
    print(f"   Content Type: {dataset_details.content.value}")
    print(f"   Localization: {dataset_details.localization.value}")
    print(f"   Is Locked: {dataset_details.is_locked}")
    print(f"   Last Accessed: {dataset_details.last_accessed}")

    # Display tag information if available
    if dataset_details.tags:
        print("\n   Tags:")
        for tag_name, tag_id in dataset_details.tags.items():
            print(f"      - {tag_name} (ID: {tag_id})")

    # List dataset exports
    print(f"\n📦 Listing exports for '{selected_dataset.name}'...")
    exports = client.datasets.list_exports(dataset_id)

    if exports.items:
        print(f"   Found {len(exports.items)} export(s):")
        for export in exports.items:
            print(f"      - Export ID: {export.dataset_export_id}")
            print(f"        Format: {export.spec.format.value}")
            print(f"        Created: {export.metadata.time_created}")
            if export.status.download_url:
                print("        Status: Ready for download")
            else:
                print("        Status: Processing...")
    else:
        print("   No exports found.")

    # Create a new export
    print(f"\n🔄 Creating new export for '{selected_dataset.name}'...")

    export_settings = DatasetExportSettings(
        format=DatasetExportFormat.VI_FULL  # Full dataset with assets and annotations
    )

    new_export = client.datasets.create_export(
        dataset_id=dataset_id, export_settings=export_settings
    )

    print("   ✓ Export created!")
    print(f"   Export ID: {new_export.dataset_export_id}")

    # Download the dataset
    print(f"\n⬇️  Downloading dataset '{selected_dataset.name}'...")
    save_dir = Path("./data")
    save_dir.mkdir(exist_ok=True)

    try:
        downloaded = client.get_dataset(
            dataset_id=dataset_id,
            save_dir=save_dir,
            overwrite=False,  # Skip if already exists
            show_progress=True,
        )

        print("\n   ✓ Dataset downloaded successfully!")
        print(f"   Location: {downloaded.save_dir}")

        # List downloaded files
        dataset_path = Path(downloaded.save_dir)
        if dataset_path.exists():
            print("\n   📁 Downloaded structure:")
            for split_dir in ["dump", "training", "validation"]:
                split_path = dataset_path / split_dir
                if split_path.exists():
                    print(f"      {split_dir}/")
                    if (split_path / "assets").exists():
                        asset_count = len(list((split_path / "assets").glob("*")))
                        print(f"         assets/ ({asset_count} files)")
                    if (split_path / "annotations").exists():
                        print("         annotations/")

    except Exception as e:
        print(f"   ✗ Download failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Basic dataset operations completed!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   - Explore asset operations: 02_asset_upload_download.py")
    print("   - Work with annotations: 03_annotation_workflows.py")
    print("   - Load datasets for training: 04_dataset_loader.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise
