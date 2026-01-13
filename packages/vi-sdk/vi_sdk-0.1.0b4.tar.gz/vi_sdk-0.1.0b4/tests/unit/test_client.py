#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_client.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for client initialization and high-level methods.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from tests.conftest import VALID_DATASET_ID, VALID_RUN_ID
from vi import Client
from vi.api.resources.datasets.types import DatasetExportSettings
from vi.client.client import APIClient
from vi.client.errors import ViConfigurationError
from vi.logging.config import LoggingConfig


@pytest.mark.unit
@pytest.mark.client
class TestAPIClient:
    """Test APIClient base class."""

    def test_init_with_requester(self, mock_requester):
        """Test initialization with Requester object."""
        client = APIClient(endpoint=mock_requester, _auto_init_resources=False)
        assert client._requester == mock_requester

    def test_init_without_endpoint(self):
        """Test initialization fails without endpoint."""
        with pytest.raises(ViConfigurationError) as exc_info:
            APIClient(endpoint=None, _auto_init_resources=False)
        assert "Unable to get API endpoint" in str(exc_info.value)

    def test_auto_init_resources(self):
        """Test automatic resource initialization."""
        # This would be tested with actual ViClient subclass
        pass


@pytest.mark.unit
@pytest.mark.client
class TestViClient:
    """Test ViClient class."""

    def test_init_with_credentials(self, valid_credentials, mock_requester):
        """Test initialization with valid credentials."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)
            assert client is not None

    def test_init_with_env_vars(self, mock_requester):
        """Test initialization with environment variables."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client()
            assert client is not None

    def test_init_with_config_file(self, config_file, mock_requester):
        """Test initialization with config file."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(config_file=config_file)
            assert client is not None

    def test_init_with_custom_endpoint(self, valid_credentials, mock_requester):
        """Test initialization with custom endpoint."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials, endpoint="https://custom.api.com")
            assert client is not None

    def test_init_with_logging_config(self, valid_credentials, mock_requester):
        """Test initialization with logging configuration."""
        logging_config = LoggingConfig(
            enable_console=False, enable_file=False, log_requests=False
        )

        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials, logging_config=logging_config)
            assert client is not None

    def test_organizations_attribute(self, valid_credentials, mock_requester):
        """Test that organizations attribute is available."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)
            assert hasattr(client, "organizations")

    def test_get_model_method(self, valid_credentials, mock_requester):
        """Test get_model convenience method."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_model = Mock()
            mock_model.run_id = VALID_RUN_ID

            with patch.object(client.models, "download", return_value=mock_model):
                result = client.get_model(VALID_RUN_ID)
                assert result == mock_model

    def test_get_dataset_method(self, valid_credentials, mock_requester):
        """Test get_dataset convenience method."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_dataset = Mock()
            mock_dataset.dataset_id = VALID_DATASET_ID

            with patch.object(client.datasets, "download", return_value=mock_dataset):
                result = client.get_dataset(VALID_DATASET_ID)
                assert result == mock_dataset

    def test_get_dataset_with_export_settings(self, valid_credentials, mock_requester):
        """Test get_dataset with export settings."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_dataset = Mock()
            export_settings = DatasetExportSettings()

            with patch.object(client.datasets, "download", return_value=mock_dataset):
                _ = client.get_dataset(
                    VALID_DATASET_ID, export_settings=export_settings
                )
                client.datasets.download.assert_called_once()

    def test_get_dataset_with_dict_export_settings(
        self, valid_credentials, mock_requester
    ):
        """Test get_dataset with dict export settings."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_dataset = Mock()
            export_settings_dict = {"format": "vi_jsonl"}

            with patch.object(client.datasets, "download", return_value=mock_dataset):
                _ = client.get_dataset(
                    VALID_DATASET_ID, export_settings=export_settings_dict
                )
                client.datasets.download.assert_called_once()

    def test_get_dataset_with_save_dir(
        self, valid_credentials, mock_requester, tmp_path
    ):
        """Test get_dataset with custom save directory."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_dataset = Mock()

            with patch.object(client.datasets, "download", return_value=mock_dataset):
                _ = client.get_dataset(VALID_DATASET_ID, save_dir=tmp_path)
                client.datasets.download.assert_called_once()


@pytest.mark.unit
@pytest.mark.client
class TestClientEdgeCases:
    """Test edge cases for client."""

    def test_multiple_client_instances(self, valid_credentials, mock_requester):
        """Test creating multiple client instances."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client1 = Client(**valid_credentials)
            client2 = Client(**valid_credentials)
            assert client1 is not client2

    def test_client_with_invalid_credentials(self):
        """Test client initialization with invalid credentials."""
        with pytest.raises(ViConfigurationError):
            Client(secret_key="invalid", organization_id="short")

    def test_client_attribute_access(self, valid_credentials, mock_requester):
        """Test accessing client attributes."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)
            assert hasattr(client, "organizations")
            assert hasattr(client, "datasets")
            assert hasattr(client, "assets")
            assert hasattr(client, "annotations")
            assert hasattr(client, "flows")
            assert hasattr(client, "runs")
            assert hasattr(client, "models")

    def test_client_with_none_logging_config(self, valid_credentials, mock_requester):
        """Test client with None logging config."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials, logging_config=None)
            assert client is not None

    def test_get_model_with_checkpoint(self, valid_credentials, mock_requester):
        """Test get_model with specific checkpoint."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_model = Mock()

            with patch.object(client.models, "download", return_value=mock_model):
                _ = client.get_model(VALID_RUN_ID, ckpt="best")
                client.models.download.assert_called_with(
                    VALID_RUN_ID,
                    "best",
                    Path.home() / ".datature" / "vi" / "models",
                    False,
                    True,
                )

    def test_get_dataset_annotations_only(self, valid_credentials, mock_requester):
        """Test get_dataset with annotations_only flag."""
        with patch("vi.api.client.Requester", return_value=mock_requester):
            client = Client(**valid_credentials)

            mock_dataset = Mock()

            with patch.object(client.datasets, "download", return_value=mock_dataset):
                _ = client.get_dataset(VALID_DATASET_ID, annotations_only=True)
                client.datasets.download.assert_called_once()
