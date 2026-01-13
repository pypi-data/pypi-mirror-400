#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   conftest.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Shared fixtures for unit tests (mocks and test data).
"""

import json
from unittest.mock import Mock

import httpx
import pytest
from tests.conftest import (
    VALID_ANNOTATION_ID,
    VALID_ASSET_ID,
    VALID_DATASET_ID,
    VALID_DATASET_NAME,
    VALID_MODEL_ID,
    VALID_ORGANIZATION_ID,
    VALID_RUN_ID,
    VALID_SECRET_KEY,
)
from vi.client.http.requester import Requester
from vi.client.http.retry import RetryConfig

# ==============================================================================
# Mock Credentials and Config Fixtures
# ==============================================================================


@pytest.fixture
def valid_credentials():
    """Create valid test credentials."""
    return {
        "secret_key": VALID_SECRET_KEY,
        "organization_id": VALID_ORGANIZATION_ID,
    }


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / ".datature"
    config_data = {
        "secret_key": VALID_SECRET_KEY,
        "organization_id": VALID_ORGANIZATION_ID,
    }
    config_path.write_text(json.dumps(config_data))
    return config_path


@pytest.fixture
def invalid_config_file(tmp_path):
    """Create an invalid config file."""
    config_path = tmp_path / ".datature"
    config_path.write_text("INVALID_CONTENT\n")
    return config_path


# ==============================================================================
# Mock Authentication and HTTP Fixtures
# ==============================================================================


@pytest.fixture
def mock_auth():
    """Mock authentication object."""
    mock = Mock()
    mock._secret_key = VALID_SECRET_KEY
    mock._organization_id = VALID_ORGANIZATION_ID
    mock.secret_key = VALID_SECRET_KEY
    mock.organization_id = VALID_ORGANIZATION_ID
    # Mock get_headers to return a proper dict
    mock.get_headers.return_value = {
        "Authorization": f"Bearer {VALID_SECRET_KEY}",
        "Organization-Id": VALID_ORGANIZATION_ID,
    }
    return mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client."""
    mock = Mock()
    mock.get = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock.post = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock.put = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock.delete = Mock(return_value=Mock(status_code=204, json=lambda: {}))
    return mock


@pytest.fixture
def mock_requester():
    """Mock Requester object."""
    mock = Mock(spec=Requester)
    mock.get = Mock(return_value={})
    mock.post = Mock(return_value={})
    mock.put = Mock(return_value={})
    mock.delete = Mock(return_value={})
    mock._retry_config = RetryConfig()
    return mock


# ==============================================================================
# Mock Response Fixtures
# ==============================================================================


@pytest.fixture
def mock_dataset_response():
    """Mock dataset response."""
    return {
        "dataset_id": VALID_DATASET_ID,
        "name": "Test Dataset",
        "organization_id": VALID_ORGANIZATION_ID,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_asset_response():
    """Mock asset response."""
    return {
        "asset_id": VALID_ASSET_ID,
        "dataset_id": VALID_DATASET_ID,
        "name": "test_image.jpg",
        "file_type": "image/jpeg",
        "file_size": 1024,
        "created_at": "2024-01-01T00:00:00Z",
        "statistic": {
            "width": 640,
            "height": 480,
            "format": "JPEG",
        },
    }


@pytest.fixture
def mock_annotation_response():
    """Mock annotation response."""
    return {
        "annotation_id": VALID_ANNOTATION_ID,
        "asset_id": VALID_ASSET_ID,
        "dataset_id": VALID_DATASET_ID,
        "labels": [],
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_run_response():
    """Mock run response."""
    return {
        "run_id": VALID_RUN_ID,
        "name": "Test Run",
        "organization_id": VALID_ORGANIZATION_ID,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_model_response():
    """Mock model response."""
    return {
        "model_id": VALID_MODEL_ID,
        "run_id": VALID_RUN_ID,
        "organization_id": VALID_ORGANIZATION_ID,
        "checkpoint": "latest",
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_pagination_response():
    """Mock pagination response."""
    return {
        "items": [],
        "page": 1,
        "page_size": 10,
        "total": 0,
        "next_page": None,
        "prev_page": None,
    }


# ==============================================================================
# Mock Dataset Directory Fixture
# ==============================================================================


@pytest.fixture
def mock_dataset_dir(tmp_path):
    """Create a mock dataset directory structure."""
    dataset_dir = tmp_path / "test_dataset"
    dataset_dir.mkdir()

    # Create metadata with all required fields
    metadata = {
        "name": VALID_DATASET_NAME,
        "organizationId": VALID_ORGANIZATION_ID,
        "exportDir": str(dataset_dir),
        "createdAt": 1704067200,  # Unix timestamp
    }

    (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

    # Create dump directory
    dump_dir = dataset_dir / "dump"
    dump_dir.mkdir()

    # Create a dummy dump.jsonl file
    (dump_dir / "dump.jsonl").write_text(json.dumps({"asset_id": "asset1"}) + "\n")

    return dataset_dir


# ==============================================================================
# Environment Fixtures
# ==============================================================================


@pytest.fixture
def clean_environment(monkeypatch):
    """Clean environment variables."""
    env_vars = [
        "DATATURE_VI_SECRET_KEY",
        "DATATURE_VI_ORGANIZATION_ID",
        "DATATURE_VI_API_ENDPOINT",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def env_with_credentials(monkeypatch):
    """Set environment variables with test credentials."""
    monkeypatch.setenv("DATATURE_VI_SECRET_KEY", VALID_SECRET_KEY)
    monkeypatch.setenv("DATATURE_VI_ORGANIZATION_ID", VALID_ORGANIZATION_ID)


@pytest.fixture(autouse=True, scope="function")
def setup_test_env(monkeypatch):
    """Automatically set environment variables for all tests."""
    # Set default environment variables for all tests
    monkeypatch.setenv("DATATURE_VI_SECRET_KEY", VALID_SECRET_KEY)
    monkeypatch.setenv("DATATURE_VI_ORGANIZATION_ID", VALID_ORGANIZATION_ID)


# ==============================================================================
# Mock Network Error Fixtures
# ==============================================================================


@pytest.fixture
def mock_network_error():
    """Mock network error."""
    return ConnectionError("Network error")


@pytest.fixture
def mock_timeout_error():
    """Mock timeout error."""
    return httpx.TimeoutException("Request timed out")


@pytest.fixture
def mock_http_error_responses():
    """Mock HTTP error responses."""
    return {
        400: {"error": "Bad Request", "message": "Invalid parameters"},
        401: {"error": "Unauthorized", "message": "Authentication failed"},
        403: {"error": "Forbidden", "message": "Access denied"},
        404: {"error": "Not Found", "message": "Resource not found"},
        429: {"error": "Too Many Requests", "message": "Rate limit exceeded"},
        500: {"error": "Internal Server Error", "message": "Server error"},
        502: {"error": "Bad Gateway", "message": "Bad gateway"},
        503: {"error": "Service Unavailable", "message": "Service unavailable"},
    }


@pytest.fixture
def create_mock_response():
    """Create mock responses."""

    def _create_response(status_code=200, json_data=None, headers=None):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json = Mock(return_value=json_data or {})
        mock_response.headers = headers or {}
        mock_response.text = json.dumps(json_data or {})
        # Add elapsed attribute for response timing
        mock_elapsed = Mock()
        mock_elapsed.total_seconds = Mock(return_value=0.1)
        mock_response.elapsed = mock_elapsed
        return mock_response

    return _create_response
