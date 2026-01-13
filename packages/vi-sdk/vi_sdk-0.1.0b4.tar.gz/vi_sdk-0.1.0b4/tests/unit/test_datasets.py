#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_datasets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for datasets API operations.
"""

from unittest.mock import Mock, patch

import pytest
from tests.conftest import VALID_DATASET_ID, VALID_ORGANIZATION_ID
from vi.api.pagination import PaginatedResponse
from vi.api.resources.datasets import responses
from vi.api.resources.datasets.datasets import Dataset
from vi.api.resources.datasets.results import DatasetDownloadResult
from vi.api.resources.datasets.types import DatasetExportSettings
from vi.api.responses import Pagination
from vi.api.types import PaginationParams
from vi.client.errors import ViInvalidParameterError, ViOperationError


@pytest.mark.unit
@pytest.mark.dataset
class TestDatasetResource:
    """Test Dataset resource."""

    @pytest.fixture
    def dataset(self, mock_auth, mock_requester):
        """Create Dataset instance."""
        return Dataset(mock_auth, mock_requester)

    def test_list_datasets(self, dataset, mock_requester):
        """Test listing datasets."""
        mock_dataset = Mock(spec=responses.Dataset)
        mock_dataset.dataset_id = VALID_DATASET_ID
        mock_dataset.name = "Test Dataset"

        mock_response = Pagination(items=[mock_dataset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = dataset.list()

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].dataset_id == VALID_DATASET_ID

    def test_list_datasets_with_pagination(self, dataset, mock_requester):
        """Test listing datasets with pagination params."""
        mock_dataset = Mock(spec=responses.Dataset)
        mock_response = Pagination(items=[mock_dataset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        pagination = PaginationParams(page_size=10)
        result = dataset.list(pagination=pagination)

        assert isinstance(result, PaginatedResponse)
        mock_requester.get.assert_called_once()

    def test_list_datasets_with_dict_pagination(self, dataset, mock_requester):
        """Test listing datasets with dict pagination params."""
        mock_dataset = Mock(spec=responses.Dataset)
        mock_response = Pagination(items=[mock_dataset], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        pagination_dict = {"page_size": 10}
        result = dataset.list(pagination=pagination_dict)

        assert isinstance(result, PaginatedResponse)

    def test_get_dataset(self, dataset, mock_requester):
        """Test getting a dataset by ID."""
        mock_dataset = Mock(spec=responses.Dataset)
        mock_dataset.dataset_id = VALID_DATASET_ID
        mock_dataset.name = "Test Dataset"

        mock_requester.get.return_value = mock_dataset

        result = dataset.get(VALID_DATASET_ID)

        assert isinstance(result, responses.Dataset)
        assert result.dataset_id == VALID_DATASET_ID
        mock_requester.get.assert_called_once()

    def test_get_dataset_invalid_id(self, dataset):
        """Test getting dataset with invalid ID."""
        with pytest.raises(ViInvalidParameterError):
            dataset.get("")

    def test_delete_dataset(self, dataset, mock_requester):
        """Test deleting a dataset."""
        mock_deleted = Mock(spec=responses.DeletedDataset)
        mock_requester.delete.return_value = mock_deleted

        result = dataset.delete(VALID_DATASET_ID)

        assert result == mock_deleted
        mock_requester.delete.assert_called_once()

    def test_create_export(self, dataset, mock_requester):
        """Test creating dataset export."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.dataset_export_id = "export_123"

        mock_requester.post.return_value = mock_export

        result = dataset.create_export(VALID_DATASET_ID)

        assert isinstance(result, responses.DatasetExport)
        mock_requester.post.assert_called_once()

    def test_create_export_with_settings(self, dataset, mock_requester):
        """Test creating dataset export with settings."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_requester.post.return_value = mock_export

        export_settings = DatasetExportSettings()
        result = dataset.create_export(
            VALID_DATASET_ID, export_settings=export_settings
        )

        assert isinstance(result, responses.DatasetExport)

    def test_create_export_with_dict_settings(self, dataset, mock_requester):
        """Test creating dataset export with dict settings."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_requester.post.return_value = mock_export

        export_settings_dict = {"format": "vi_jsonl"}
        result = dataset.create_export(
            VALID_DATASET_ID, export_settings=export_settings_dict
        )

        assert isinstance(result, responses.DatasetExport)

    def test_get_export(self, dataset, mock_requester):
        """Test getting dataset export."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.dataset_export_id = "export_123"

        mock_requester.get.return_value = mock_export

        result = dataset.get_export(VALID_DATASET_ID, "export_123")

        assert isinstance(result, responses.DatasetExport)
        mock_requester.get.assert_called_once()

    def test_list_exports(self, dataset, mock_requester):
        """Test listing dataset exports."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_response = Pagination(items=[mock_export], next_page=None, prev_page=None)

        mock_requester.get.return_value = mock_response

        result = dataset.list_exports(VALID_DATASET_ID)

        assert isinstance(result, Pagination)
        assert len(result.items) == 1

    def test_get_deletion_operation(self, dataset, mock_requester):
        """Test getting deletion operation."""
        mock_deleted = Mock(spec=responses.DeletedDataset)
        mock_requester.get.return_value = mock_deleted

        result = dataset.get_deletion_operation(VALID_DATASET_ID)

        assert isinstance(result, responses.DeletedDataset)

    def test_bulk_delete_assets(self, dataset, mock_requester):
        """Test bulk deleting assets."""
        mock_session = Mock(spec=responses.BulkAssetDeletionSession)
        mock_session.delete_many_assets_session_id = "session_123"

        mock_requester.post.return_value = mock_session

        with patch.object(dataset, "wait_until_done", return_value=mock_session):
            result = dataset.bulk_delete_assets(VALID_DATASET_ID)

            assert isinstance(result, responses.BulkAssetDeletionSession)
            mock_requester.post.assert_called_once()

    def test_bulk_delete_assets_with_filter(self, dataset, mock_requester):
        """Test bulk deleting assets with filter."""
        mock_session = Mock(spec=responses.BulkAssetDeletionSession)
        mock_session.delete_many_assets_session_id = "session_123"

        mock_requester.post.return_value = mock_session

        with patch.object(dataset, "wait_until_done", return_value=mock_session):
            result = dataset.bulk_delete_assets(
                VALID_DATASET_ID, filter_criteria="status:active"
            )

            assert isinstance(result, responses.BulkAssetDeletionSession)

    def test_get_bulk_asset_deletion_session(self, dataset, mock_requester):
        """Test getting bulk asset deletion session."""
        mock_session = Mock(spec=responses.BulkAssetDeletionSession)
        mock_requester.get.return_value = mock_session

        result = dataset.get_bulk_asset_deletion_session(
            VALID_DATASET_ID, "session_123"
        )

        assert isinstance(result, responses.BulkAssetDeletionSession)


@pytest.mark.unit
@pytest.mark.dataset
class TestDatasetDownload:
    """Test dataset download functionality."""

    @pytest.fixture
    def dataset(self, mock_auth, mock_requester):
        """Create Dataset instance."""
        return Dataset(mock_auth, mock_requester)

    def test_download_without_export_id(self, dataset, tmp_path):
        """Test download creates export if not provided."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.dataset_export_id = "export_123"
        mock_export.status = Mock()
        mock_export.status.download_url = Mock()
        mock_export.status.download_url.url = "https://test.com/download"
        mock_export.organization_id = VALID_ORGANIZATION_ID

        mock_downloaded = DatasetDownloadResult(
            dataset_id=VALID_DATASET_ID, save_dir=str(tmp_path / VALID_DATASET_ID)
        )

        with patch.object(dataset, "create_export", return_value=mock_export):
            with patch.object(dataset, "wait_until_done", return_value=mock_export):
                with patch(
                    "vi.api.resources.datasets.datasets.DatasetDownloader"
                ) as mock_downloader:
                    mock_downloader.return_value.download.return_value = mock_downloaded

                    result = dataset.download(VALID_DATASET_ID, save_dir=tmp_path)

                    dataset.create_export.assert_called_once()
                    assert isinstance(result, DatasetDownloadResult)
                    assert result.dataset_id == VALID_DATASET_ID

    def test_download_with_export_id(self, dataset, tmp_path):
        """Test download with existing export ID."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.status = Mock()
        mock_export.status.download_url = Mock()
        mock_export.status.download_url.url = "https://test.com/download"
        mock_export.organization_id = VALID_ORGANIZATION_ID

        mock_downloaded = DatasetDownloadResult(
            dataset_id=VALID_DATASET_ID, save_dir=str(tmp_path / VALID_DATASET_ID)
        )

        with patch.object(dataset, "wait_until_done", return_value=mock_export):
            with patch(
                "vi.api.resources.datasets.datasets.DatasetDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = mock_downloaded

                result = dataset.download(
                    VALID_DATASET_ID, dataset_export_id="export_123", save_dir=tmp_path
                )

                assert isinstance(result, DatasetDownloadResult)
                assert result.dataset_id == VALID_DATASET_ID

    def test_download_annotations_only(self, dataset, tmp_path):
        """Test downloading annotations only."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.dataset_export_id = "export_123"
        mock_export.status = Mock()
        mock_export.status.download_url = Mock()
        mock_export.status.download_url.url = "https://test.com/download"
        mock_export.organization_id = VALID_ORGANIZATION_ID

        mock_downloaded = DatasetDownloadResult(
            dataset_id=VALID_DATASET_ID, save_dir=str(tmp_path / VALID_DATASET_ID)
        )

        with patch.object(dataset, "create_export", return_value=mock_export):
            with patch.object(dataset, "wait_until_done", return_value=mock_export):
                with patch(
                    "vi.api.resources.datasets.datasets.DatasetDownloader"
                ) as mock_downloader:
                    mock_downloader.return_value.download.return_value = mock_downloaded

                    result = dataset.download(
                        VALID_DATASET_ID, annotations_only=True, save_dir=tmp_path
                    )

                    assert isinstance(result, DatasetDownloadResult)
                    assert result.dataset_id == VALID_DATASET_ID

    def test_download_no_download_url(self, dataset, tmp_path):
        """Test download fails when no download URL."""
        mock_export = Mock(spec=responses.DatasetExport)
        mock_export.dataset_export_id = "export_123"
        mock_export.status = Mock()
        mock_export.status.download_url = None

        with patch.object(dataset, "create_export", return_value=mock_export):
            with patch.object(dataset, "wait_until_done", return_value=mock_export):
                with pytest.raises(ViOperationError) as exc_info:
                    dataset.download(VALID_DATASET_ID, save_dir=tmp_path)

                assert "download URL is not available" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.dataset
class TestDatasetEdgeCases:
    """Test edge cases for datasets."""

    @pytest.fixture
    def dataset(self, mock_auth, mock_requester):
        """Create Dataset instance."""
        return Dataset(mock_auth, mock_requester)

    def test_list_invalid_response(self, dataset, mock_requester):
        """Test list with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError) as exc_info:
            dataset.list()
        assert "Invalid response" in str(exc_info.value)

    def test_get_invalid_response(self, dataset, mock_requester):
        """Test get with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            dataset.get(VALID_DATASET_ID)

    def test_create_export_invalid_response(self, dataset, mock_requester):
        """Test create export with invalid response."""
        mock_requester.post.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            dataset.create_export(VALID_DATASET_ID)

    def test_get_export_invalid_response(self, dataset, mock_requester):
        """Test get export with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            dataset.get_export(VALID_DATASET_ID, "export_123")

    def test_list_exports_invalid_response(self, dataset, mock_requester):
        """Test list exports with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ViOperationError):
            dataset.list_exports(VALID_DATASET_ID)
