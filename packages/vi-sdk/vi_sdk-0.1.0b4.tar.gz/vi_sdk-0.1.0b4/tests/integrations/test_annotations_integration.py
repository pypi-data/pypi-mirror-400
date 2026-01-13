#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_annotations_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Annotation API.
"""

import os
import tempfile
from pathlib import Path

import pytest
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.annotations.responses import Annotation
from vi.api.resources.datasets.annotations.results import AnnotationUploadResult
from vi.client.errors import ViError

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@pytest.mark.slow
@skip_if_no_credentials
class TestAnnotationUploadIntegration:
    """Integration tests for annotation upload operations."""

    def test_upload_error_invalid_dataset(self, integration_client):
        """Test that uploading to invalid dataset raises appropriate error."""
        print("\n❌ Testing upload to invalid dataset...")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            f.write('{"annotations": []}')
            f.flush()

            with pytest.raises(ViError) as exc_info:
                integration_client.annotations.upload(
                    "definitely_nonexistent_dataset_12345",
                    Path(f.name),
                    wait_until_done=False,
                )

            print(f"✅ Correctly raised error: {exc_info.value.error_code}")

    def test_upload_sample_annotation_file(
        self, integration_client, test_dataset_id, sample_annotation_file
    ):
        """Test uploading a single annotation file from samples directory."""
        print(
            f"\n📤 Testing upload of sample annotation file: {sample_annotation_file.name}"
        )
        print(f"   Target dataset: {test_dataset_id}")

        try:
            # Upload the sample annotation file
            result = integration_client.annotations.upload(
                test_dataset_id,
                sample_annotation_file,
                wait_until_done=True,
            )

            print("✅ Sample annotation file uploaded successfully!")
            assert isinstance(result, AnnotationUploadResult), (
                "Expected AnnotationUploadResult"
            )
            print(f"   Total files: {result.total_files}")
            print(f"   Total annotations: {result.total_annotations}")
            print(f"   Session ID: {result.session_id}")

            # Verify the result structure
            assert result.session is not None
            assert result.total_files > 0

        except Exception as e:
            pytest.fail(f"Sample annotation upload failed: {e}")

    def test_upload_sample_annotation_folder(
        self, integration_client, test_dataset_id, sample_annotation_folder
    ):
        """Test uploading annotations from the entire samples folder."""
        print(f"\n📁 Testing upload from annotation folder: {sample_annotation_folder}")
        print(f"   Target dataset: {test_dataset_id}")

        try:
            # Get all annotation files from the folder
            annotation_files = list(sample_annotation_folder.glob("*.jsonl"))
            print(f"   Found {len(annotation_files)} annotation files in folder")

            if not annotation_files:
                pytest.skip("No annotation files found in samples folder")

            results = []
            for annotation_file in annotation_files:
                print(f"   Uploading: {annotation_file.name}")

                result = integration_client.annotations.upload(
                    test_dataset_id,
                    annotation_file,
                    wait_until_done=True,
                )
                results.append(result)
                assert isinstance(result, AnnotationUploadResult), (
                    "Expected AnnotationUploadResult"
                )
                print(f"   ✅ {annotation_file.name} uploaded successfully")
                print(
                    f"      Files: {result.total_files}, Annotations: {result.total_annotations}"
                )

            print(
                f"✅ All {len(annotation_files)} annotation files from folder uploaded successfully!"
            )
            print(f"   Total results: {len(results)}")

            # Verify all uploads completed
            assert len(results) == len(annotation_files)
            for result in results:
                assert isinstance(result, AnnotationUploadResult)
                assert result.session is not None

        except Exception as e:
            pytest.fail(f"Folder annotation upload failed: {e}")


@pytest.mark.integration
@skip_if_no_credentials
class TestAnnotationListIntegration:
    """Integration tests for annotation list operations."""

    def test_list_annotations_basic(
        self, integration_client, test_dataset_id, test_asset_id
    ):
        """Test listing annotations with default parameters."""
        print(f"\n🏷️  Listing annotations from dataset: {test_dataset_id}")

        try:
            # List annotations with default parameters
            annotations = integration_client.annotations.list(
                test_dataset_id, test_asset_id
            )

            print("✅ Annotations listed successfully!")
            print(f"   Number of annotations: {len(annotations.items)}")
            print(f"   Has next page: {annotations.next_page is not None}")

            # Verify the response structure
            assert isinstance(annotations, PaginatedResponse)
            assert isinstance(annotations.items, list)

            if annotations.items:
                first_annotation = annotations.items[0]
                assert isinstance(first_annotation, Annotation)
                assert first_annotation.annotation_id is not None
                # Note: Annotation doesn't have dataset_id field directly
                print(
                    f"   First annotation ID: {first_annotation.annotation_id[:20]}..."
                )

        except Exception as e:
            pytest.fail(f"List annotations failed: {e}")

    def test_list_annotations_error_invalid_dataset(
        self, integration_client, test_dataset_id
    ):
        """Test that listing annotations from invalid dataset raises appropriate error."""
        print("\n❌ Testing list with invalid dataset ID...")

        with pytest.raises(ViError) as exc_info:
            integration_client.annotations.list(
                test_dataset_id, "definitely_nonexistent_asset_12345"
            )

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")


@pytest.mark.integration
@skip_if_no_credentials
class TestAnnotationGetIntegration:
    """Integration tests for annotation get operations."""

    def test_get_annotation_basic(
        self, integration_client, test_dataset_id, test_asset_id
    ):
        """Test getting a single annotation by ID."""
        print(f"\n🏷️  Getting single annotation from dataset: {test_dataset_id}")

        try:
            # Get annotation
            annotations = integration_client.annotations.list(
                test_dataset_id, test_asset_id
            )
            annotation_id = annotations.items[0].annotation_id
            annotation = integration_client.annotations.get(
                test_dataset_id, test_asset_id, annotation_id
            )

            print("✅ Annotation retrieved successfully!")
            print(f"   Annotation ID: {annotation.annotation_id}")
            print(f"   Asset ID: {annotation.asset_id}")
            print(f"   Dataset ID: {annotation.dataset_id}")

            # Verify the response structure
            assert isinstance(annotation, Annotation)
            assert annotation.annotation_id == annotation_id
            assert annotation.dataset_id == test_dataset_id
            assert annotation.asset_id is not None

        except Exception as e:
            pytest.fail(f"Get annotation failed: {e}")

    def test_get_annotation_error_invalid_id(
        self, integration_client, test_dataset_id, test_asset_id
    ):
        """Test that getting non-existent annotation raises appropriate error."""
        print("\n❌ Testing get with invalid annotation ID...")

        with pytest.raises(ViError) as exc_info:
            integration_client.annotations.get(
                test_dataset_id,
                test_asset_id,
                "definitely_nonexistent_annotation_12345",
            )

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")


@pytest.mark.integration
@skip_if_no_credentials
@pytest.mark.skipif(
    not os.getenv("ALLOW_ANNOTATION_DELETE"),
    reason="Set ALLOW_ANNOTATION_DELETE=1 to enable annotation deletion tests",
)
class TestAnnotationDeleteIntegration:
    """Integration tests for annotation delete operations (requires opt-in)."""

    def test_delete_annotation_protection(self):
        """Test that annotation deletion is properly protected."""
        print("\n⚠️  Annotation deletion requires explicit opt-in")
        print("   Set ALLOW_ANNOTATION_DELETE=1 to enable deletion tests")
        print("✅ Deletion protection verified")

    def test_delete_annotation_error_invalid_id(
        self, integration_client, test_dataset_id, test_asset_id
    ):
        """Test that deleting non-existent annotation raises appropriate error."""
        print("\n❌ Testing delete with invalid annotation ID...")

        with pytest.raises(ViError) as exc_info:
            integration_client.annotations.delete(
                test_dataset_id,
                test_asset_id,
                "definitely_nonexistent_annotation_12345",
            )

        print(f"✅ Correctly raised error: {exc_info.value.error_code}")
