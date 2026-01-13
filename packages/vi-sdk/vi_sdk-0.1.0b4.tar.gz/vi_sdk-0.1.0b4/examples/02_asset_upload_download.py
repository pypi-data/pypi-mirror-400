#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   02_asset_upload_download.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Asset upload and download example.

Asset Upload and Download Example.

This example demonstrates:
- Uploading individual images
- Uploading folders of images
- Batch asset uploads
- Downloading assets
- Listing and filtering assets

Requirements:
    - Vi SDK installed: pip install vi-sdk
    - Valid API credentials
    - Some test images to upload

Usage:
    python3 02_asset_upload_download.py
"""

from pathlib import Path

import vi
from PIL import Image, ImageDraw
from vi.api.types import PaginationParams


def create_sample_images(output_dir: Path, count: int = 5):
    """Create sample images for testing (requires PIL)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    created_files = []

    print(f"\n🎨 Creating {count} sample images...")
    for i in range(count):
        # Create a simple colored image with text
        img = Image.new("RGB", (800, 600), color=(50 + i * 40, 100, 150))
        draw = ImageDraw.Draw(img)

        # Add text
        text = f"Sample Image {i + 1}"
        # Use default font
        draw.text((300, 280), text, fill=(255, 255, 255))

        # Save image
        filename = f"sample_{i + 1:03d}.jpg"
        filepath = output_dir / filename
        img.save(filepath, "JPEG", quality=95)
        created_files.append(filepath)
        print(f"   ✓ Created: {filename}")

    return created_files


def main():
    """Run asset upload and download operations."""
    # Initialize client
    print("📡 Initializing Vi SDK client...")
    client = vi.Client(
        secret_key="YOUR_DATATURE_VI_SECRET_KEY",
        organization_id="YOUR_DATATURE_VI_ORGANIZATION_ID",
    )

    # Get first dataset
    print("\n📊 Finding a dataset to work with...")
    datasets = client.datasets.list()

    if not datasets.items:
        print("   ✗ No datasets found!")
        print("   💡 Create a dataset on Datature Vi first.")
        return

    dataset = datasets.items[0]
    dataset_id = dataset.dataset_id
    print(f"   ✓ Using dataset: {dataset.name} ({dataset_id})")

    # Create sample images if needed
    sample_dir = Path("./sample_images")
    sample_images = create_sample_images(sample_dir, count=5)

    if not sample_images:
        # Check if directory already has images
        if sample_dir.exists():
            sample_images = list(sample_dir.glob("*.jpg")) + list(
                sample_dir.glob("*.png")
            )

    if not sample_images:
        print("\n   ⚠️  No sample images available for upload demo.")
        print("   Skipping upload operations...")
    else:
        # Upload single image
        print("\n📤 Uploading single image...")
        try:
            upload_result = client.assets.upload(
                dataset_id=dataset_id,
                paths=str(sample_images[0]),
                wait_until_done=True,
            )

            print("   ✓ Upload complete!")
            print(f"   Uploaded: {upload_result.total_succeeded} assets")
            print(upload_result.summary())

        except Exception as e:
            print(f"   ✗ Upload failed: {e}")

        # Upload folder of images
        if len(sample_images) > 1:
            print("\n📤 Uploading folder of images...")
            try:
                upload_result = client.assets.upload(
                    dataset_id=dataset_id,
                    paths=str(sample_dir),
                    wait_until_done=True,
                )

                print("   ✓ Batch upload complete!")
                print(f"   Total: {upload_result.total_files}")
                print(f"   Succeeded: {upload_result.total_succeeded}")
                print(f"   Failed: {upload_result.total_failed}")
                print(f"   Success rate: {upload_result.success_rate:.1f}%")
                print(upload_result.summary())

            except Exception as e:
                print(f"   ✗ Batch upload failed: {e}")

    # List assets
    print("\n📋 Listing assets in dataset...")
    pagination = PaginationParams(page_size=10)

    assets = client.assets.list(dataset_id=dataset_id, pagination=pagination)

    print(f"   Found {len(assets.items)} assets (first page):")
    for i, asset in enumerate(assets.items, 1):
        print(f"\n   {i}. {asset.filename}")
        print(f"      ID: {asset.asset_id}")
        print(f"      Size: {asset.metadata.width}x{asset.metadata.height}")
        print(f"      File size: {asset.metadata.file_size:,} bytes")
        print(f"      Annotations: {asset.metadata.annotations.total}")
        print(f"      Upload status: {asset.metadata.upload_status}")

    # Get asset with download URL
    if assets.items:
        print("\n🔗 Getting download URL for first asset...")
        asset_with_content = client.assets.get(
            dataset_id=dataset_id, asset_id=assets.items[0].asset_id, contents=True
        )

        if asset_with_content.contents and asset_with_content.contents.asset:
            print("   ✓ Download URL obtained")
            print(f"   Expires at: {asset_with_content.contents.asset.expiry}")
        else:
            print("   ⚠️  No download URL available")

    # Download all assets
    print("\n⬇️  Downloading all assets from dataset...")
    download_dir = Path("./downloaded_assets")

    try:
        downloaded = client.assets.download(
            dataset_id=dataset_id,
            save_dir=download_dir,
            overwrite=False,
            show_progress=True,
        )

        print("\n   ✓ Assets downloaded successfully!")
        print(f"   Location: {downloaded.save_dir}")

        # Count downloaded files
        asset_dir = Path(downloaded.save_dir)
        if asset_dir.exists():
            file_count = len(list(asset_dir.glob("*.*")))
            print(f"   Total files: {file_count}")

    except Exception as e:
        print(f"   ✗ Download failed: {e}")

    # Iterate through all assets (pagination)
    print("\n🔄 Iterating through all assets (all pages)...")
    all_assets_count = 0

    for page in client.assets.list(dataset_id=dataset_id):
        for asset in page.items:
            all_assets_count += 1

    print(f"   Total assets across all pages: {all_assets_count}")

    # Filter assets (example: by file size)
    print("\n🔍 Finding large assets (>1MB)...")
    large_assets = []

    for page in client.assets.list(dataset_id=dataset_id):
        for asset in page.items:
            if asset.metadata.file_size > 1024 * 1024:  # 1MB
                large_assets.append(asset)

    print(f"   Found {len(large_assets)} large assets")

    # Delete an asset (optional - commented out for safety)
    # if assets.items:
    #     asset_to_delete = assets.items[-1]
    #     print(f"\n🗑️  Deleting asset: {asset_to_delete.filename}...")
    #     try:
    #         deleted = client.assets.delete(
    #             dataset_id=dataset_id,
    #             asset_id=asset_to_delete.asset_id
    #         )
    #         print(f"   ✓ Asset deleted: {deleted.deleted}")
    #     except Exception as e:
    #         print(f"   ✗ Deletion failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Asset operations completed!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - Sample images created: {len(sample_images)}")
    print(f"   - Total assets in dataset: {all_assets_count}")
    print(f"   - Assets downloaded to: {download_dir}")
    print("\n💡 Next steps:")
    print("   - Work with annotations: 03_annotation_workflows.py")
    print("   - Load datasets: 04_dataset_loader.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise
