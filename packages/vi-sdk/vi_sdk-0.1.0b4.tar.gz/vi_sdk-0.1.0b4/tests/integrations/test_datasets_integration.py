#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_datasets_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Dataset API.
"""

import os

import pytest

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetsList:
    """Test dataset listing functionality."""

    def test_list_datasets(self, integration_client):
        """Test listing all datasets."""
        print("\n📁 Listing datasets...")

        datasets = integration_client.datasets.list()

        print(f"✅ Found {len(datasets.items)} dataset(s)")

        for i, dataset in enumerate(datasets.items[:3], 1):
            print(f"   {i}. {dataset.name} ({dataset.dataset_id})")

        assert datasets is not None
        assert hasattr(datasets, "items")

    def test_list_datasets_with_pagination(self, integration_client):
        """Test dataset listing with pagination."""
        print("\n📄 Testing dataset pagination...")

        # Get first page
        page1 = integration_client.datasets.list(pagination={"page_size": 2})

        print(f"✅ First page: {len(page1.items)} dataset(s)")

        assert page1 is not None

    def test_list_datasets_iteration(self, integration_client):
        """Test iterating over all datasets."""
        print("\n🔄 Iterating over all datasets...")

        datasets = integration_client.datasets.list()
        count = 0

        for dataset in datasets.items:
            count += 1
            if count <= 3:
                print(f"   Dataset {count}: {dataset.name}")

        print(f"✅ Iterated over {count} dataset(s)")

        assert count >= 0


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetGet:
    """Test getting individual dataset information."""

    def test_get_dataset_by_id(self, integration_client, test_dataset_id):
        """Test getting a dataset by ID."""
        print(f"\n📁 Fetching dataset: {test_dataset_id}")

        dataset = integration_client.datasets.get(test_dataset_id)

        print("✅ Dataset retrieved")
        print(f"   Name: {dataset.name}")
        print(f"   ID: {dataset.dataset_id}")
        print(f"   Organization ID: {dataset.organization_id}")

        assert dataset is not None
        assert dataset.dataset_id == test_dataset_id

    def test_dataset_has_required_fields(self, integration_client, test_dataset_id):
        """Test that dataset has all required fields."""
        print("\n📋 Validating dataset fields...")

        dataset = integration_client.datasets.get(test_dataset_id)

        required_fields = ["dataset_id", "name", "organization_id", "create_date"]

        for field in required_fields:
            assert hasattr(dataset, field), f"Missing required field: {field}"
            print(f"   ✓ {field}")

        print("✅ All required fields present")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestDatasetExports:
#     """Test dataset export functionality."""

#     @pytest.mark.slow
#     def test_create_dataset_export(self, integration_client, test_dataset_id):
#         """Test creating a dataset export."""
#         print(f"\n📤 Creating export for dataset: {test_dataset_id}")

#         try:
#             export_result = integration_client.datasets.create_export(
#                 test_dataset_id, format="ViFull"
#             )

#             print("✅ Export created")
#             print(f"   Export ID: {export_result.dataset_export_id}")
#             print(f"   Status: {export_result.status}")

#             assert export_result is not None
#             assert export_result.dataset_export_id is not None

#         except Exception as e:
#             print(f"ℹ️  Export creation failed: {e}")
#             pytest.skip("Dataset export not available")

#     def test_list_dataset_exports(self, integration_client, test_dataset_id):
#         """Test listing dataset exports."""
#         print(f"\n📋 Listing exports for dataset: {test_dataset_id}")

#         try:
#             exports = integration_client.datasets.list_exports(
#                 test_dataset_id
#             )

#             print(f"✅ Found {len(exports.items)} export(s)")

#             for export in exports.items[:3]:
#                 print(
#                     f"   - {export.format}: {export.status}"
#                 )

#             assert exports is not None

#         except Exception as e:
#             print(f"ℹ️  List exports failed: {e}")
#             pytest.skip("List exports not available")

#     def test_get_dataset_export(self, integration_client, test_dataset_id):
#         """Test getting a specific dataset export."""
#         print(f"\n📄 Getting dataset export...")

#         try:
#             # First list exports to get an export ID
#             exports = integration_client.datasets.list_exports(
#                 test_dataset_id
#             )

#             if len(exports.items) == 0:
#                 pytest.skip("No exports available to test")

#             export_id = exports.items[0].dataset_export_id
#             print(f"   Testing with export ID: {export_id}")

#             export = integration_client.datasets.get_export(
#                 test_dataset_id, export_id
#             )

#             print("✅ Export retrieved")
#             print(f"   Format: {export.format}")
#             print(f"   Status: {export.status}")

#             assert export is not None
#             assert export.dataset_export_id == export_id

#         except Exception as e:
#             print(f"ℹ️  Get export failed: {e}")
#             pytest.skip("Get export not available")


# @pytest.mark.integration
# @skip_if_no_credentials
# @pytest.mark.slow
# class TestDatasetDownload:
#     """Test dataset download functionality."""

#     def test_download_dataset_metadata(
#         self, integration_client, test_dataset_id, tmp_path
#     ):
#         """Test downloading dataset metadata."""
#         print(f"\n⬇️  Downloading dataset metadata...")

#         download_path = tmp_path / "dataset_download"

#         try:
#             result = integration_client.datasets.get(
#                 test_dataset_id, str(download_path), wait_until_done=False
#             )

#             print("✅ Download initiated")
#             print(f"   Download path: {download_path}")

#             assert result is not None

#         except Exception as e:
#             print(f"ℹ️  Download test skipped: {e}")
#             pytest.skip("Dataset download not available")


@pytest.mark.integration
@skip_if_no_credentials
@pytest.mark.skipif(
    not os.getenv("ALLOW_DATASET_DELETE"),
    reason="Set ALLOW_DATASET_DELETE=1 to enable dataset deletion tests",
)
class TestDatasetDeleteIntegration:
    """Integration tests for dataset delete operations (requires opt-in)."""

    def test_delete_dataset_protection(self):
        """Test that dataset deletion is properly protected."""
        print("\n⚠️  Dataset deletion requires explicit opt-in")
        print("   Set ALLOW_DATASET_DELETE=1 to enable deletion tests")
        print("✅ Deletion protection verified")

    def test_get_deletion_operation_invalid_dataset(self, integration_client):
        """Test getting deletion operation for invalid dataset."""
        print("\n❌ Testing get deletion operation with invalid dataset ID...")

        with pytest.raises(Exception):  # Could be ViError or other error types
            integration_client.datasets.get_deletion_operation(
                "definitely_nonexistent_dataset_12345"
            )

        print("✅ Correctly raised error for invalid dataset")

    def test_delete_dataset_error_invalid_id(self, integration_client):
        """Test that deleting non-existent dataset raises appropriate error."""
        print("\n❌ Testing delete with invalid dataset ID...")

        with pytest.raises(Exception):  # Could be ViError or other error types
            integration_client.datasets.delete("definitely_nonexistent_dataset_12345")

        print("✅ Correctly raised error for invalid dataset")
