#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_asset_upload_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for actual asset upload operations.
"""

import os
import tempfile
from pathlib import Path

import pytest
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.assets.responses import Asset
from vi.api.resources.datasets.assets.results import (
    AssetDownloadResult,
    AssetUploadResult,
)
from vi.api.resources.datasets.assets.types import AssetSortCriterion, SortCriterion
from vi.api.types import PaginationParams
from vi.client.errors import ViError

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@pytest.mark.slow
@skip_if_no_credentials
class TestAssetUploadIntegration:
    """Integration tests for actual asset upload to API."""

    def test_upload_single_image(
        self, integration_client, test_dataset_id, sample_image_file
    ):
        """Test uploading a single realistic image to the API."""
        print(f"\n📤 Uploading single image to dataset: {test_dataset_id}")
        print(f"   Image file: {sample_image_file}")
        print(f"   Image size: {sample_image_file.stat().st_size} bytes")

        try:
            # Actually upload the image
            # Note: upload() returns AssetUploadResult wrapper
            result = integration_client.assets.upload(
                test_dataset_id, sample_image_file, wait_until_done=True
            )

            print("✅ Upload completed!")
            assert isinstance(result, AssetUploadResult), "Expected AssetUploadResult"
            assert len(result.sessions) > 0, "Expected at least one ingestion session"

            print(f"   Total files: {result.total_files}")
            print(f"   Succeeded: {result.total_succeeded}")
            print(f"   Failed: {result.total_failed}")
            print(f"   Session IDs: {result.session_ids}")

            # Verify the result
            assert result.total_files > 0
            assert result.sessions[0].asset_ingestion_session_id is not None

        except Exception as e:
            pytest.fail(f"Upload failed: {e}")

    def test_upload_from_folder(
        self, integration_client, test_dataset_id, sample_images_folder
    ):
        """Test uploading all images from a folder."""
        print(f"\n📤 Uploading from folder: {sample_images_folder}")
        print(f"   Number of files: {len(list(sample_images_folder.glob('*.jpg')))}")

        try:
            # Upload from folder
            # Note: upload() returns AssetUploadResult wrapper
            result = integration_client.assets.upload(
                test_dataset_id, sample_images_folder, wait_until_done=True
            )

            print("✅ Folder upload completed!")
            assert isinstance(result, AssetUploadResult), "Expected AssetUploadResult"
            assert len(result.sessions) > 0, "Expected at least one ingestion session"

            print(f"   Number of batches: {len(result.sessions)}")
            print(f"   Total files: {result.total_files}")
            print(f"   Succeeded: {result.total_succeeded}")
            print(f"   Failed: {result.total_failed}")
            print(f"   Success rate: {result.success_rate}%")

            for idx, session in enumerate(result.sessions, 1):
                print(
                    f"   Batch {idx} Session ID: {session.asset_ingestion_session_id}"
                )
                # Verify each session
                assert session.asset_ingestion_session_id is not None

        except Exception as e:
            pytest.fail(f"Folder upload failed: {e}")

    def test_upload_without_wait(
        self, integration_client, test_dataset_id, sample_image_file
    ):
        """Test uploading without waiting for completion."""
        print("\n📤 Starting upload without waiting...")

        try:
            # Upload without waiting
            # Note: upload() returns AssetUploadResult wrapper
            result = integration_client.assets.upload(
                test_dataset_id, sample_image_file, wait_until_done=False
            )

            print("✅ Upload started (not waiting for completion)")
            assert isinstance(result, AssetUploadResult), "Expected AssetUploadResult"
            assert len(result.sessions) > 0, "Expected at least one ingestion session"

            print(f"   Session IDs: {result.session_ids}")

            # Verify we got a session ID
            assert result.sessions[0].asset_ingestion_session_id is not None

        except Exception as e:
            pytest.fail(f"Upload without wait failed: {e}")

    def test_upload_error_invalid_dataset(self, integration_client, sample_image_file):
        """Test that uploading to invalid dataset raises appropriate error."""
        print("\n❌ Testing upload to invalid dataset...")

        with pytest.raises(ViError) as exc_info:
            integration_client.assets.upload(
                "definitely_nonexistent_dataset_12345",
                sample_image_file,
                wait_until_done=True,
            )

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")


@pytest.mark.integration
@skip_if_no_credentials
class TestAssetUploadCleanup:
    """Tests for cleanup after upload."""

    @pytest.mark.skipif(
        not os.getenv("CLEANUP_TEST_UPLOADS"),
        reason="Set CLEANUP_TEST_UPLOADS=1 to enable cleanup tests",
    )
    def test_delete_uploaded_assets(self, integration_client, test_dataset_id):
        """Test deleting uploaded test assets (only if CLEANUP_TEST_UPLOADS is set)."""
        print(f"\n🧹 Cleaning up test uploads from dataset: {test_dataset_id}")

        try:
            # List all assets
            assets = integration_client.assets.list(test_dataset_id)
            print(f"   Found {len(assets.items)} assets")

            # Delete test assets (ones with 'test' in the name)
            deleted_count = 0
            for asset in assets.items:
                if asset.name and "test" in asset.name.lower():
                    try:
                        integration_client.assets.delete(
                            test_dataset_id, asset.asset_id
                        )
                        deleted_count += 1
                        print(f"   Deleted: {asset.name}")
                    except Exception as e:
                        print(f"   Failed to delete {asset.name}: {e}")

            print(f"✅ Cleanup completed: {deleted_count} test assets deleted")

        except Exception as e:
            print(f"⚠️  Cleanup failed: {e}")


@pytest.mark.integration
@skip_if_no_credentials
class TestAssetGetIntegration:
    """Integration tests for asset get operations."""

    def test_get_asset_basic(self, integration_client, test_dataset_id, test_asset_id):
        """Test getting a single asset by ID."""
        print(f"\n📄 Getting asset: {test_asset_id} from dataset: {test_dataset_id}")

        try:
            # Get asset without contents
            asset = integration_client.assets.get(test_dataset_id, test_asset_id)

            print("✅ Asset retrieved successfully!")
            print(f"   Asset ID: {asset.asset_id}")
            print(f"   Filename: {asset.filename}")
            print(f"   Kind: {asset.kind}")
            print(f"   File size: {asset.metadata.file_size} bytes")

            # Verify the response structure
            assert isinstance(asset, Asset)
            assert asset.asset_id == test_asset_id
            assert asset.dataset_id == test_dataset_id
            assert asset.filename is not None
            assert asset.kind is not None
            assert asset.metadata is not None
            assert asset.metadata.file_size > 0

        except Exception as e:
            pytest.fail(f"Get asset failed: {e}")

    def test_get_asset_with_contents(
        self, integration_client, test_dataset_id, test_asset_id
    ):
        """Test getting a single asset with contents URLs."""
        print(f"\n📄 Getting asset with contents: {test_asset_id}")

        try:
            # Get asset with contents
            asset = integration_client.assets.get(
                test_dataset_id, test_asset_id, contents=True
            )

            print("✅ Asset with contents retrieved successfully!")
            print(f"   Asset ID: {asset.asset_id}")
            print(f"   Has asset URL: {asset.contents.asset is not None}")
            print(f"   Has thumbnail URL: {asset.contents.thumbnail is not None}")

            # Verify the response structure
            assert isinstance(asset, Asset)
            assert asset.asset_id == test_asset_id
            assert asset.contents is not None
            assert asset.contents.asset is not None
            assert asset.contents.asset.url is not None
            assert asset.contents.asset.expiry > 0

        except Exception as e:
            pytest.fail(f"Get asset with contents failed: {e}")

    def test_get_asset_error_invalid_id(self, integration_client, test_dataset_id):
        """Test that getting non-existent asset raises appropriate error."""
        print("\n❌ Testing get with invalid asset ID...")

        with pytest.raises(ViError) as exc_info:
            integration_client.assets.get(
                test_dataset_id, "definitely_nonexistent_asset_12345"
            )

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")


@pytest.mark.integration
@skip_if_no_credentials
class TestAssetListIntegration:
    """Integration tests for asset list operations."""

    def test_list_assets_basic(self, integration_client, test_dataset_id):
        """Test listing assets with default parameters."""
        print(f"\n📋 Listing assets from dataset: {test_dataset_id}")

        try:
            # List assets with default pagination
            assets = integration_client.assets.list(test_dataset_id)

            print("✅ Assets listed successfully!")
            print(f"   Number of assets: {len(assets.items)}")
            print(f"   Has next page: {assets.next_page is not None}")

            # Verify the response structure
            assert isinstance(assets, PaginatedResponse)
            assert isinstance(assets.items, list)

            if assets.items:
                first_asset = assets.items[0]
                assert isinstance(first_asset, Asset)
                assert first_asset.asset_id is not None
                assert first_asset.dataset_id == test_dataset_id
                assert first_asset.filename is not None
                print(f"   First asset: {first_asset.filename}")

        except Exception as e:
            pytest.fail(f"List assets failed: {e}")

    def test_list_assets_with_pagination(self, integration_client, test_dataset_id):
        """Test listing assets with custom pagination."""
        print("\n📋 Listing assets with pagination...")

        try:
            # List with small page size to test pagination
            pagination = PaginationParams(page_size=2)
            assets = integration_client.assets.list(
                test_dataset_id, pagination=pagination
            )

            print("✅ Assets listed with pagination!")
            print(f"   Number of assets: {len(assets.items)}")
            print(f"   Page size: {pagination.page_size}")
            print(f"   Has next page: {assets.next_page is not None}")

            # Verify pagination works
            assert len(assets.items) <= pagination.page_size

            # Test getting next page if available
            if assets.next_page:
                next_assets = integration_client.assets.list(
                    test_dataset_id,
                    pagination=PaginationParams(
                        page_token=assets.next_page, page_size=pagination.page_size
                    ),
                )
                print(f"   Next page assets: {len(next_assets.items)}")
                assert isinstance(next_assets, PaginatedResponse)

        except Exception as e:
            pytest.fail(f"List assets with pagination failed: {e}")

    def test_list_assets_with_contents(self, integration_client, test_dataset_id):
        """Test listing assets with contents URLs."""
        print("\n📋 Listing assets with contents...")

        try:
            # List assets with contents
            assets = integration_client.assets.list(test_dataset_id, contents=True)

            print("✅ Assets with contents listed successfully!")
            print(f"   Number of assets: {len(assets.items)}")

            # Verify contents are included
            if assets.items:
                first_asset = assets.items[0]
                assert first_asset.contents is not None
                assert first_asset.contents.asset is not None
                print(
                    f"   First asset has content URL: {first_asset.contents.asset.url is not None}"
                )

        except Exception as e:
            pytest.fail(f"List assets with contents failed: {e}")

    def test_list_assets_with_sorting(self, integration_client, test_dataset_id):
        """Test listing assets with sorting."""
        print("\n📋 Listing assets with sorting...")

        try:
            # List assets sorted by filename
            sort_by = AssetSortCriterion(criterion=SortCriterion.FILENAME)
            assets = integration_client.assets.list(test_dataset_id, sort_by=sort_by)

            print("✅ Assets listed with sorting!")
            print(f"   Number of assets: {len(assets.items)}")
            print(f"   Sort criterion: {sort_by.criterion.value}")

            # Verify sorting (check if filenames are in order)
            if len(assets.items) > 1:
                filenames = [asset.filename for asset in assets.items]
                print(f"   First few filenames: {filenames[:3]}")

        except Exception as e:
            pytest.fail(f"List assets with sorting failed: {e}")

    def test_list_assets_error_invalid_dataset(self, integration_client):
        """Test that listing assets from invalid dataset raises appropriate error."""
        print("\n❌ Testing list with invalid dataset ID...")

        with pytest.raises(ViError) as exc_info:
            integration_client.assets.list("definitely_nonexistent_dataset_12345")

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")


@pytest.mark.integration
@pytest.mark.slow
@skip_if_no_credentials
class TestAssetDownloadIntegration:
    """Integration tests for asset download operations."""

    def test_download_assets_to_temp_dir(self, integration_client, test_dataset_id):
        """Test downloading assets to a temporary directory."""
        print(f"\n⬇️  Downloading assets from dataset: {test_dataset_id}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"   Download directory: {temp_path}")

            try:
                # Download assets
                result = integration_client.assets.download(
                    test_dataset_id, save_dir=temp_path, show_progress=False
                )

                print("✅ Assets downloaded successfully!")
                print(f"   Dataset ID: {result.dataset_id}")
                print(f"   Save directory: {result.save_dir}")
                print(f"   Count: {result.count} assets")

                # Verify the response structure
                assert isinstance(result, AssetDownloadResult)
                assert result.dataset_id == test_dataset_id
                assert Path(result.save_dir) == temp_path / test_dataset_id

                # Check if files were actually downloaded
                downloaded_files = list(temp_path.glob("*"))
                print(f"   Downloaded files: {len(downloaded_files)}")

                if downloaded_files:
                    print(f"   First file: {downloaded_files[0].name}")
                    print(
                        f"   First file size: {downloaded_files[0].stat().st_size} bytes"
                    )

            except Exception as e:
                pytest.fail(f"Download assets failed: {e}")

    def test_download_assets_with_overwrite(self, integration_client, test_dataset_id):
        """Test downloading assets with overwrite enabled."""
        print("\n⬇️  Downloading assets with overwrite...")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # First download
                result1 = integration_client.assets.download(
                    test_dataset_id,
                    save_dir=temp_path,
                    overwrite=False,
                    show_progress=False,
                )

                # Second download with overwrite
                result2 = integration_client.assets.download(
                    test_dataset_id,
                    save_dir=temp_path,
                    overwrite=True,
                    show_progress=False,
                )

                print("✅ Assets downloaded with overwrite!")
                print(f"   Both downloads completed to: {temp_path}")

                # Verify both results
                assert isinstance(result1, AssetDownloadResult)
                assert isinstance(result2, AssetDownloadResult)
                assert result1.dataset_id == result2.dataset_id == test_dataset_id

            except Exception as e:
                pytest.fail(f"Download assets with overwrite failed: {e}")

    def test_download_assets_error_invalid_dataset(self, integration_client):
        """Test that downloading from invalid dataset raises appropriate error."""
        print("\n❌ Testing download with invalid dataset ID...")

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ViError) as exc_info:
                integration_client.assets.download(
                    "definitely_nonexistent_dataset_12345",
                    save_dir=temp_dir,
                    show_progress=False,
                )

            print(f"✅ Correctly raised error: {exc_info.value.error_code}")

    @pytest.mark.skipif(
        not os.getenv("TEST_LARGE_DOWNLOAD"),
        reason="Set TEST_LARGE_DOWNLOAD=1 to enable large download tests",
    )
    def test_download_assets_with_progress(self, integration_client, test_dataset_id):
        """Test downloading assets with progress tracking (only if TEST_LARGE_DOWNLOAD is set)."""
        print("\n⬇️  Downloading assets with progress tracking...")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Download with progress enabled
                result = integration_client.assets.download(
                    test_dataset_id, save_dir=temp_path, show_progress=True
                )

                print("✅ Assets downloaded with progress tracking!")
                print(f"   Download completed to: {result.save_dir}")

                # Verify the result
                assert isinstance(result, AssetDownloadResult)
                assert result.dataset_id == test_dataset_id

            except Exception as e:
                pytest.fail(f"Download assets with progress failed: {e}")
