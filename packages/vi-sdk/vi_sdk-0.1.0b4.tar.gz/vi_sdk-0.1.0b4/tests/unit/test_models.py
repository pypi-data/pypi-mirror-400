#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_models.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for models API operations.
"""

from unittest.mock import Mock, patch

import pytest
from tests.conftest import VALID_MODEL_ID, VALID_RUN_ID
from vi.api.pagination import PaginatedResponse
from vi.api.resources.models import responses
from vi.api.resources.models.models import Model
from vi.api.resources.models.results import ModelDownloadResult
from vi.api.responses import Pagination
from vi.client.errors import ViInvalidParameterError


@pytest.mark.unit
@pytest.mark.model
class TestModelResource:
    """Test Model resource."""

    @pytest.fixture
    def model(self, mock_auth, mock_requester):
        """Create Model instance."""
        return Model(mock_auth, mock_requester)

    def test_init(self, model):
        """Test model initialization."""
        assert model._link_parser is not None

    def test_list_models(self, model, mock_requester):
        """Test listing models."""
        mock_model = Mock(spec=responses.Model)
        mock_model.model_id = VALID_MODEL_ID
        mock_model.run_id = VALID_RUN_ID

        mock_response = Pagination(items=[mock_model], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = model.list(VALID_RUN_ID)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 1
        assert result.items[0].model_id == VALID_MODEL_ID

    def test_list_models_invalid_run_id(self, model):
        """Test listing models with invalid run ID."""
        with pytest.raises(ViInvalidParameterError):
            model.list("")

    def test_get_model(self, model, mock_requester):
        """Test getting a model by ID."""
        mock_model = Mock(spec=responses.Model)
        mock_model.model_id = VALID_MODEL_ID
        mock_model.run_id = VALID_RUN_ID

        mock_response = Pagination(items=[mock_model], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = model.get(VALID_RUN_ID)

        assert isinstance(result, responses.Model)
        assert result.run_id == VALID_RUN_ID

    def test_get_model_with_checkpoint(self, model, mock_requester):
        """Test getting model with specific checkpoint."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID
        mock_model.checkpoint = "best"

        mock_response = Pagination(items=[mock_model], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = model.get(VALID_RUN_ID, ckpt="best")

        assert isinstance(result, responses.Model)

    def test_get_model_with_contents(self, model, mock_requester):
        """Test getting model with contents."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID

        mock_response = Pagination(items=[mock_model], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = model.get(VALID_RUN_ID, contents=True)

        assert isinstance(result, responses.Model)

    def test_get_model_no_models_found(self, model, mock_requester):
        """Test getting model when no models found."""
        mock_response = Pagination(items=[], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        with pytest.raises(ValueError) as exc_info:
            model.get(VALID_RUN_ID)
        assert "No models found" in str(exc_info.value)

    def test_get_model_invalid_run_id(self, model):
        """Test getting model with invalid run ID."""
        with pytest.raises(ViInvalidParameterError):
            model.get("")


@pytest.mark.unit
@pytest.mark.model
class TestModelDownload:
    """Test model download functionality."""

    @pytest.fixture
    def model(self, mock_auth, mock_requester):
        """Create Model instance."""
        return Model(mock_auth, mock_requester)

    def test_download_model(self, model, tmp_path):
        """Test downloading a model."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID
        mock_model.status = Mock()
        mock_model.status.contents = Mock()
        mock_model.status.contents.download_url = Mock()
        mock_model.status.contents.download_url.url = "https://test.com/model.zip"

        mock_downloaded = Mock(spec=ModelDownloadResult)

        with patch.object(model, "get", return_value=mock_model):
            with patch(
                "vi.api.resources.models.models.ModelDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = mock_downloaded

                result = model.download(VALID_RUN_ID, save_dir=tmp_path)

                assert isinstance(result, ModelDownloadResult)
                model.get.assert_called_once()

    def test_download_model_with_checkpoint(self, model, tmp_path):
        """Test downloading model with specific checkpoint."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID
        mock_model.checkpoint = "best"
        mock_model.status = Mock()
        mock_model.status.contents = Mock()
        mock_model.status.contents.download_url = Mock()
        mock_model.status.contents.download_url.url = "https://test.com/model.zip"

        mock_downloaded = Mock(spec=ModelDownloadResult)

        with patch.object(model, "get", return_value=mock_model):
            with patch(
                "vi.api.resources.models.models.ModelDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = mock_downloaded

                result = model.download(VALID_RUN_ID, ckpt="best", save_dir=tmp_path)

                assert isinstance(result, ModelDownloadResult)
                model.get.assert_called_with(VALID_RUN_ID, "best", contents=True)

    def test_download_model_default_path(self, model):
        """Test downloading model to default path."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID
        mock_model.status = Mock()
        mock_model.status.contents = Mock()
        mock_model.status.contents.download_url = Mock()
        mock_model.status.contents.download_url.url = "https://test.com/model.zip"

        mock_downloaded = Mock(spec=ModelDownloadResult)

        with patch.object(model, "get", return_value=mock_model):
            with patch(
                "vi.api.resources.models.models.ModelDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = mock_downloaded

                result = model.download(VALID_RUN_ID)

                assert isinstance(result, ModelDownloadResult)

    def test_download_model_without_progress(self, model, tmp_path):
        """Test downloading model without progress display."""
        mock_model = Mock(spec=responses.Model)
        mock_model.run_id = VALID_RUN_ID
        mock_model.status = Mock()
        mock_model.status.contents = Mock()
        mock_model.status.contents.download_url = Mock()
        mock_model.status.contents.download_url.url = "https://test.com/model.zip"

        mock_downloaded = Mock(spec=ModelDownloadResult)

        with patch.object(model, "get", return_value=mock_model):
            with patch(
                "vi.api.resources.models.models.ModelDownloader"
            ) as mock_downloader:
                mock_downloader.return_value.download.return_value = mock_downloaded

                result = model.download(
                    VALID_RUN_ID, show_progress=False, save_dir=tmp_path
                )

                assert isinstance(result, ModelDownloadResult)

    def test_download_model_invalid_run_id(self, model, tmp_path):
        """Test downloading model with invalid run ID."""
        with pytest.raises(ViInvalidParameterError):
            model.download("", save_dir=tmp_path)


@pytest.mark.unit
@pytest.mark.model
class TestModelEdgeCases:
    """Test edge cases for models."""

    @pytest.fixture
    def model(self, mock_auth, mock_requester):
        """Create Model instance."""
        return Model(mock_auth, mock_requester)

    def test_list_invalid_response(self, model, mock_requester):
        """Test list with invalid response."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            model.list(VALID_RUN_ID)

    def test_get_invalid_response_type(self, model, mock_requester):
        """Test get with invalid response type (not Pagination or Model)."""
        mock_requester.get.return_value = {"invalid": "response"}

        with pytest.raises(ValueError):
            model.get(VALID_RUN_ID)

    def test_get_model_returns_latest(self, model, mock_requester):
        """Test that get returns the latest model from list."""
        mock_model1 = Mock(spec=responses.Model)
        mock_model1.run_id = VALID_RUN_ID
        mock_model1.checkpoint = "epoch_1"

        mock_model2 = Mock(spec=responses.Model)
        mock_model2.run_id = VALID_RUN_ID
        mock_model2.checkpoint = "epoch_2"

        # Last item should be returned
        mock_response = Pagination(
            items=[mock_model1, mock_model2], next_page=None, prev_page=None
        )
        mock_requester.get.return_value = mock_response

        result = model.get(VALID_RUN_ID)

        assert result == mock_model2  # Should return last item

    def test_list_empty_models(self, model, mock_requester):
        """Test listing with no models."""
        mock_response = Pagination(items=[], next_page=None, prev_page=None)
        mock_requester.get.return_value = mock_response

        result = model.list(VALID_RUN_ID)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
