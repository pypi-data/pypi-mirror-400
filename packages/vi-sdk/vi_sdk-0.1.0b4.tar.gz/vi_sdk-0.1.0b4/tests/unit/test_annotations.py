#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_annotations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for annotations API operations.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tests.conftest import VALID_ANNOTATION_ID, VALID_ASSET_ID, VALID_DATASET_ID
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.annotations import responses
from vi.api.resources.datasets.annotations.annotations import Annotation
from vi.api.resources.datasets.annotations.results import AnnotationUploadResult
from vi.api.responses import DeletedResource, Pagination
from vi.client.errors import ViInvalidParameterError, ViOperationError


@pytest.mark.unit
@pytest.mark.annotation
class TestAnnotationResource:
    """Test suite for Annotation resource basic operations."""

    @pytest.fixture
    def annotation(self, mock_auth: Mock, mock_requester: Mock) -> Annotation:
        """Create an Annotation instance for testing.

        Args:
            mock_auth: Mock authentication object.
            mock_requester: Mock HTTP requester.

        Returns:
            Configured annotation resource instance.

        """
        return Annotation(mock_auth, mock_requester)

    def test_list_annotations(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test listing annotations for a dataset.

        Verifies that the list method correctly retrieves and paginates
        annotations for a given dataset ID and asset ID.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_annotation = Mock(spec=responses.Annotation)
        mock_annotation.annotation_id = VALID_ANNOTATION_ID

        mock_response = Pagination(
            items=[mock_annotation], next_page=None, prev_page=None
        )
        mock_requester.get.return_value = mock_response

        result = annotation.list(VALID_DATASET_ID, VALID_ASSET_ID)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].annotation_id == VALID_ANNOTATION_ID

    def test_list_annotations_invalid_dataset_id(self, annotation: Annotation) -> None:
        """Test listing annotations with invalid dataset ID.

        Verifies that attempting to list annotations with an empty
        dataset ID raises a ViInvalidParameterError.

        Args:
            annotation: Annotation resource fixture.

        """
        with pytest.raises(ViInvalidParameterError):
            annotation.list("", VALID_ASSET_ID)

    def test_get_annotation(self, annotation: Annotation, mock_requester: Mock) -> None:
        """Test retrieving a single annotation by ID.

        Verifies that the get method correctly retrieves an annotation
        using its dataset ID, asset ID, and annotation ID.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_annotation = Mock(spec=responses.Annotation)
        mock_annotation.annotation_id = VALID_ANNOTATION_ID

        mock_requester.get.return_value = mock_annotation

        result = annotation.get(VALID_DATASET_ID, VALID_ASSET_ID, VALID_ANNOTATION_ID)

        assert isinstance(result, responses.Annotation)
        assert result.annotation_id == VALID_ANNOTATION_ID

    def test_get_annotation_invalid_ids(self, annotation: Annotation) -> None:
        """Test getting annotation with invalid IDs.

        Verifies that attempting to get an annotation with empty
        dataset ID or annotation ID raises ViInvalidParameterError.

        Args:
            annotation: Annotation resource fixture.

        """
        with pytest.raises(ViInvalidParameterError):
            annotation.get("", VALID_ASSET_ID, VALID_ANNOTATION_ID)

        with pytest.raises(ViInvalidParameterError):
            annotation.get(VALID_DATASET_ID, VALID_ASSET_ID, "")

    def test_delete_annotation(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test deleting an annotation.

        Verifies that the delete method correctly removes an annotation
        and returns a DeletedResource confirmation.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_requester.delete.return_value = {"data": ""}

        result = annotation.delete(
            VALID_DATASET_ID, VALID_ASSET_ID, VALID_ANNOTATION_ID
        )

        assert isinstance(result, DeletedResource)
        assert result.id == VALID_ANNOTATION_ID
        assert result.deleted is True

    def test_delete_annotation_invalid_ids(self, annotation: Annotation) -> None:
        """Test deleting annotation with invalid IDs.

        Verifies that attempting to delete an annotation with an empty
        dataset ID raises ViInvalidParameterError.

        Args:
            annotation: Annotation resource fixture.

        """
        with pytest.raises(ViInvalidParameterError):
            annotation.delete("", VALID_ASSET_ID, VALID_ANNOTATION_ID)


@pytest.mark.unit
@pytest.mark.annotation
class TestAnnotationUpload:
    """Test suite for annotation upload functionality."""

    @pytest.fixture
    def annotation(self, mock_auth: Mock, mock_requester: Mock) -> Annotation:
        """Create an Annotation instance for testing.

        Args:
            mock_auth: Mock authentication object.
            mock_requester: Mock HTTP requester.

        Returns:
            Configured annotation resource instance.

        """
        return Annotation(mock_auth, mock_requester)

    def test_upload_single_file(
        self, annotation: Annotation, test_json_file: Path
    ) -> None:
        """Test uploading a single annotation file.

        Verifies that a single annotation file can be uploaded to a
        dataset and returns an AnnotationUploadResult.

        Args:
            annotation: Annotation resource fixture.
            test_json_file: Test JSON file fixture.

        """
        mock_session = Mock(spec=responses.AnnotationImportSession)
        mock_session.annotation_import_session_id = "session_123"

        with patch(
            "vi.api.resources.datasets.annotations.annotations.AnnotationUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = mock_session

            with patch.object(annotation, "wait_until_done", return_value=mock_session):
                result = annotation.upload(VALID_DATASET_ID, test_json_file)

                assert isinstance(result, AnnotationUploadResult)

    def test_upload_multiple_files(
        self, annotation: Annotation, test_json_file: Path
    ) -> None:
        """Test uploading multiple annotation files.

        Verifies that multiple annotation files can be uploaded in a
        single operation and returns an AnnotationUploadResult.

        Args:
            annotation: Annotation resource fixture.
            test_json_file: Test JSON file fixture.

        """
        mock_session = Mock(spec=responses.AnnotationImportSession)

        with patch(
            "vi.api.resources.datasets.annotations.annotations.AnnotationUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = mock_session

            with patch.object(annotation, "wait_until_done", return_value=mock_session):
                result = annotation.upload(
                    VALID_DATASET_ID, [test_json_file, test_json_file]
                )

                assert isinstance(result, AnnotationUploadResult)

    def test_upload_from_folder(self, annotation: Annotation, tmp_path: Path) -> None:
        """Test uploading annotations from a folder.

        Verifies that annotations can be uploaded from a directory path
        and returns an AnnotationUploadResult.

        Args:
            annotation: Annotation resource fixture.
            tmp_path: Temporary directory fixture.

        """
        mock_session = Mock(spec=responses.AnnotationImportSession)

        with patch(
            "vi.api.resources.datasets.annotations.annotations.AnnotationUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = mock_session

            with patch.object(annotation, "wait_until_done", return_value=mock_session):
                result = annotation.upload(VALID_DATASET_ID, tmp_path)

                assert isinstance(result, AnnotationUploadResult)

    def test_upload_without_wait(
        self, annotation: Annotation, test_json_file: Path
    ) -> None:
        """Test uploading without waiting for completion.

        Verifies that annotation upload can be initiated without waiting
        for the import session to complete (async mode).

        Args:
            annotation: Annotation resource fixture.
            test_json_file: Test JSON file fixture.

        """
        mock_session = Mock(spec=responses.AnnotationImportSession)

        with patch(
            "vi.api.resources.datasets.annotations.annotations.AnnotationUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = mock_session

            result = annotation.upload(
                VALID_DATASET_ID, test_json_file, wait_until_done=False
            )

            assert isinstance(result, AnnotationUploadResult)

    def test_upload_invalid_dataset_id(
        self, annotation: Annotation, test_json_file: Path
    ) -> None:
        """Test upload with invalid dataset ID.

        Verifies that attempting to upload annotations with an empty
        dataset ID raises ViInvalidParameterError.

        Args:
            annotation: Annotation resource fixture.
            test_json_file: Test JSON file fixture.

        """
        with pytest.raises(ViInvalidParameterError):
            annotation.upload("", test_json_file)


@pytest.mark.unit
@pytest.mark.annotation
class TestAnnotationEdgeCases:
    """Test suite for annotation edge cases and error handling."""

    @pytest.fixture
    def annotation(self, mock_auth: Mock, mock_requester: Mock) -> Annotation:
        """Create an Annotation instance for testing.

        Args:
            mock_auth: Mock authentication object.
            mock_requester: Mock HTTP requester.

        Returns:
            Configured annotation resource instance.

        """
        return Annotation(mock_auth, mock_requester)

    def test_list_invalid_response(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test list with invalid response format.

        Verifies that the list method raises ViOperationError when the API
        returns an invalid response format.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            annotation.list(VALID_DATASET_ID, VALID_ASSET_ID)

    def test_get_invalid_response(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test get with invalid response format.

        Verifies that the get method raises ViOperationError when the API
        returns an invalid response format.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            annotation.get(VALID_DATASET_ID, VALID_ASSET_ID, VALID_ANNOTATION_ID)

    def test_delete_invalid_response(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test delete with invalid response format.

        Verifies that the delete method raises ViOperationError when the API
        returns an unexpected response format.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_requester.delete.return_value = {"data": "unexpected"}

        with pytest.raises(ViOperationError):
            annotation.delete(VALID_DATASET_ID, VALID_ASSET_ID, VALID_ANNOTATION_ID)

    def test_list_empty_annotations(
        self, annotation: Annotation, mock_requester: Mock
    ) -> None:
        """Test listing when no annotations exist.

        Verifies that the list method correctly handles an empty result
        set and returns an empty PaginatedResponse.

        Args:
            annotation: Annotation resource fixture.
            mock_requester: Mock HTTP requester fixture.

        """
        mock_response: Pagination[Mock] = Pagination(
            items=[], next_page=None, prev_page=None
        )
        mock_requester.get.return_value = mock_response

        result = annotation.list(VALID_DATASET_ID, VALID_ASSET_ID)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
