#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_assets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for assets API operations.
"""

from unittest.mock import Mock, patch

import pytest
from tests.conftest import VALID_ASSET_ID, VALID_DATASET_ID
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets.assets import responses
from vi.api.resources.datasets.assets.assets import Asset
from vi.api.resources.datasets.assets.results import (
    AssetDownloadResult,
    AssetUploadResult,
)
from vi.api.resources.datasets.assets.types import (
    AssetSortCriterion,
    SortCriterion,
    SortOrder,
)
from vi.api.resources.datasets.assets.uploader import AssetUploader
from vi.api.resources.datasets.responses import Dataset as DatasetResponse
from vi.api.responses import DeletedResource, Pagination
from vi.api.types import PaginationParams
from vi.client.errors import ViInvalidParameterError, ViOperationError


@pytest.mark.unit
@pytest.mark.asset
class TestAssetResource:
    """Test Asset resource."""

    @pytest.fixture
    def asset(self, mock_auth, mock_requester):
        """Create Asset instance."""
        return Asset(mock_auth, mock_requester)

    def test_list_assets(self, asset, mock_requester):
        """Test listing assets."""
        mock_asset = Mock(spec=responses.Asset)
        mock_asset.asset_id = VALID_ASSET_ID

        mock_response = Pagination(items=[mock_asset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = asset.list(VALID_DATASET_ID)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1

    def test_list_assets_with_pagination(self, asset, mock_requester):
        """Test listing assets with pagination."""
        mock_asset = Mock(spec=responses.Asset)
        mock_response = Pagination(items=[mock_asset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        pagination = PaginationParams(page_size=10)
        result = asset.list(VALID_DATASET_ID, pagination=pagination)

        assert isinstance(result, PaginatedResponse)

    def test_list_assets_with_filter(self, asset, mock_requester):
        """Test listing assets with filter."""
        mock_asset = Mock(spec=responses.Asset)
        mock_response = Pagination(items=[mock_asset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = asset.list(VALID_DATASET_ID, filter_criteria="status:active")

        assert isinstance(result, PaginatedResponse)

    def test_list_assets_with_sort(self, asset, mock_requester):
        """Test listing assets with sort."""
        mock_asset = Mock(spec=responses.Asset)
        mock_response = Pagination(items=[mock_asset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        sort_by = AssetSortCriterion(
            criterion=SortCriterion.FILENAME, order=SortOrder.DESC
        )
        result = asset.list(VALID_DATASET_ID, sort_by=sort_by)

        assert isinstance(result, PaginatedResponse)

    def test_list_assets_invalid_dataset_id(self, asset):
        """Test listing assets with invalid dataset ID."""
        with pytest.raises(ViInvalidParameterError):
            asset.list("")

    def test_get_asset(self, asset, mock_requester):
        """Test getting an asset by ID."""
        mock_asset = Mock(spec=responses.Asset)
        mock_asset.asset_id = VALID_ASSET_ID

        mock_requester.get.return_value = mock_asset

        result = asset.get(VALID_DATASET_ID, VALID_ASSET_ID)

        assert isinstance(result, responses.Asset)
        assert result.asset_id == VALID_ASSET_ID

    def test_get_asset_with_contents(self, asset, mock_requester):
        """Test getting asset with contents."""
        mock_asset = Mock(spec=responses.Asset)
        mock_requester.get.return_value = mock_asset

        result = asset.get(VALID_DATASET_ID, VALID_ASSET_ID, contents=True)

        assert isinstance(result, responses.Asset)

    def test_get_asset_invalid_ids(self, asset):
        """Test getting asset with invalid IDs."""
        with pytest.raises(ViInvalidParameterError):
            asset.get("", VALID_ASSET_ID)

        with pytest.raises(ViInvalidParameterError):
            asset.get(VALID_DATASET_ID, "")

    def test_delete_asset(self, asset, mock_requester):
        """Test deleting an asset."""
        mock_requester.delete.return_value = {"data": ""}

        result = asset.delete(VALID_DATASET_ID, VALID_ASSET_ID)

        assert isinstance(result, DeletedResource)
        assert result.id == VALID_ASSET_ID
        assert result.deleted is True

    def test_delete_asset_invalid_ids(self, asset):
        """Test deleting asset with invalid IDs."""
        with pytest.raises(ViInvalidParameterError):
            asset.delete("", VALID_ASSET_ID)


@pytest.mark.unit
@pytest.mark.asset
class TestAssetUpload:
    """Test asset upload functionality."""

    @pytest.fixture
    def asset(self, mock_auth, mock_requester):
        """Create Asset instance."""
        return Asset(mock_auth, mock_requester)

    def test_upload_single_file(self, asset, test_image_file):
        """Test uploading a single file."""
        mock_session = Mock(spec=responses.AssetIngestionSession)
        mock_session.asset_ingestion_session_id = "session_123"

        with patch(
            "vi.api.resources.datasets.assets.assets.AssetUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = [mock_session]

            with patch.object(asset, "wait_until_done", return_value=mock_session):
                result = asset.upload(VALID_DATASET_ID, test_image_file)

                assert isinstance(result, AssetUploadResult)

    def test_upload_multiple_files(self, asset, test_image_file):
        """Test uploading multiple files."""
        mock_session = Mock(spec=responses.AssetIngestionSession)

        with patch(
            "vi.api.resources.datasets.assets.assets.AssetUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = [mock_session]

            with patch.object(asset, "wait_until_done", return_value=mock_session):
                result = asset.upload(
                    VALID_DATASET_ID, [test_image_file, test_image_file]
                )

                assert isinstance(result, AssetUploadResult)

    def test_upload_from_folder(self, asset, tmp_path):
        """Test uploading from a folder."""
        mock_session = Mock(spec=responses.AssetIngestionSession)

        with patch(
            "vi.api.resources.datasets.assets.assets.AssetUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = [mock_session]

            with patch.object(asset, "wait_until_done", return_value=mock_session):
                result = asset.upload(VALID_DATASET_ID, tmp_path)

                assert isinstance(result, AssetUploadResult)

    def test_upload_without_wait(self, asset, test_image_file):
        """Test uploading without waiting for completion."""
        mock_session = Mock(spec=responses.AssetIngestionSession)

        with patch(
            "vi.api.resources.datasets.assets.assets.AssetUploader"
        ) as mock_uploader:
            mock_uploader.return_value.upload.return_value = [mock_session]

            result = asset.upload(
                VALID_DATASET_ID, test_image_file, wait_until_done=False
            )

            assert isinstance(result, AssetUploadResult)

    def test_upload_invalid_dataset_id(self, asset, test_image_file):
        """Test upload with invalid dataset ID."""
        with pytest.raises(ViInvalidParameterError):
            asset.upload("", test_image_file)

    def test_upload_with_batching(self, asset, test_image_file):
        """Test that upload handles batching correctly when exceeding MAX_UPLOAD_BATCH_SIZE."""
        # Create multiple mock sessions for batches
        mock_session_1 = Mock(spec=responses.AssetIngestionSession)
        mock_session_1.asset_ingestion_session_id = "session_batch_1"
        mock_session_2 = Mock(spec=responses.AssetIngestionSession)
        mock_session_2.asset_ingestion_session_id = "session_batch_2"

        with patch(
            "vi.api.resources.datasets.assets.assets.AssetUploader"
        ) as mock_uploader:
            # Mock uploader returns multiple sessions (simulating batching)
            mock_uploader.return_value.upload.return_value = [
                mock_session_1,
                mock_session_2,
            ]

            with patch.object(asset, "wait_until_done") as mock_wait:
                # Mock wait_until_done to return each session in sequence
                mock_wait.side_effect = [mock_session_1, mock_session_2]

                result = asset.upload(VALID_DATASET_ID, test_image_file)

                # Should call wait_until_done twice (once per batch)
                assert mock_wait.call_count == 2
                # Should return AssetUploadResult with multiple sessions
                assert isinstance(result, AssetUploadResult)
                assert len(result.sessions) == 2
                assert result.sessions[0] == mock_session_1
                assert result.sessions[1] == mock_session_2


@pytest.mark.unit
@pytest.mark.asset
class TestAssetUploader:
    """Test AssetUploader functionality."""

    @pytest.fixture
    def uploader(self, mock_auth, mock_requester):
        """Create AssetUploader instance."""
        return AssetUploader(mock_requester, mock_auth)

    def test_split_into_batches_single_batch(self, uploader):
        """Test splitting when total is less than batch size."""
        file_paths = [f"file_{i}.jpg" for i in range(100)]
        batches = uploader._split_into_batches(file_paths, 1000)

        assert len(batches) == 1
        assert len(batches[0]) == 100
        assert batches[0] == file_paths

    def test_split_into_batches_multiple_batches(self, uploader):
        """Test splitting when total exceeds batch size."""
        file_paths = [f"file_{i}.jpg" for i in range(2500)]
        batches = uploader._split_into_batches(file_paths, 1000)

        assert len(batches) == 3
        assert len(batches[0]) == 1000
        assert len(batches[1]) == 1000
        assert len(batches[2]) == 500

    def test_split_into_batches_exact_multiple(self, uploader):
        """Test splitting when total is exact multiple of batch size."""
        file_paths = [f"file_{i}.jpg" for i in range(3000)]
        batches = uploader._split_into_batches(file_paths, 1000)

        assert len(batches) == 3
        assert all(len(batch) == 1000 for batch in batches)

    def test_split_into_batches_empty(self, uploader):
        """Test splitting empty list."""
        file_paths = []
        batches = uploader._split_into_batches(file_paths, 1000)

        assert len(batches) == 0


@pytest.mark.unit
@pytest.mark.asset
class TestAssetDownload:
    """Test asset download functionality."""

    @pytest.fixture
    def asset(self, mock_auth, mock_requester):
        """Create Asset instance."""
        return Asset(mock_auth, mock_requester)

    def test_download_assets(self, asset, tmp_path, mock_requester):
        """Test downloading assets."""
        mock_dataset = Mock(spec=DatasetResponse)
        mock_dataset.statistic = Mock()
        mock_dataset.statistic.asset_total = 10

        # Mock the requester.get to return the mock_dataset
        mock_requester.get.return_value = mock_dataset

        mock_asset = Mock(spec=responses.Asset)
        mock_asset.contents = Mock()
        mock_asset.contents.asset = Mock()
        mock_asset.contents.asset.url = "https://test.com/asset.jpg"

        with patch.object(asset, "list") as mock_list:
            mock_list.return_value = PaginatedResponse(
                items=[mock_asset], next_page=None, prev_page=None
            )

            with patch(
                "vi.api.resources.datasets.assets.assets.AssetDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = None

                with patch("vi.api.resources.datasets.assets.assets.graceful_exit"):
                    result = asset.download(VALID_DATASET_ID, save_dir=tmp_path)

                    assert isinstance(result, AssetDownloadResult)

    def test_download_assets_invalid_dataset_id(self, asset, tmp_path):
        """Test download with invalid dataset ID."""
        with pytest.raises(ViInvalidParameterError):
            asset.download("", save_dir=tmp_path)


@pytest.mark.unit
@pytest.mark.asset
class TestAssetEdgeCases:
    """Test edge cases for assets."""

    @pytest.fixture
    def asset(self, mock_auth, mock_requester):
        """Create Asset instance."""
        return Asset(mock_auth, mock_requester)

    def test_list_invalid_response(self, asset, mock_requester):
        """Test list with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            asset.list(VALID_DATASET_ID)

    def test_get_invalid_response(self, asset, mock_requester):
        """Test get with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            asset.get(VALID_DATASET_ID, VALID_ASSET_ID)

    def test_delete_invalid_response(self, asset, mock_requester):
        """Test delete with invalid response."""
        mock_requester.delete.return_value = {"data": "unexpected"}

        with pytest.raises(ViOperationError):
            asset.delete(VALID_DATASET_ID, VALID_ASSET_ID)
