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
@Desc    :   Shared fixtures for integration tests.
"""

import json
import os
from pathlib import Path

import pytest
from vi import Client

# ==============================================================================
# Load Integration Test Configuration
# ==============================================================================


def load_integration_config():
    """Load integration test configuration from .test_config.json or env vars."""
    config = {}

    # Try loading from config file
    config_path = Path(__file__).parent.parent / ".test_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load .test_config.json: {e}")

    # Override with environment variables if present
    if os.getenv("DATATURE_VI_SECRET_KEY"):
        config.setdefault("credentials", {})["secret_key"] = os.getenv(
            "DATATURE_VI_SECRET_KEY"
        )

    if os.getenv("DATATURE_VI_ORGANIZATION_ID"):
        config.setdefault("credentials", {})["organization_id"] = os.getenv(
            "DATATURE_VI_ORGANIZATION_ID"
        )

    if os.getenv("DATATURE_VI_API_ENDPOINT"):
        config.setdefault("credentials", {})["endpoint"] = os.getenv(
            "DATATURE_VI_API_ENDPOINT"
        )

    # Load test resource IDs from environment
    test_resources = config.setdefault("test_resources", {})
    if os.getenv("TEST_DATASET_ID"):
        test_resources["dataset_id"] = os.getenv("TEST_DATASET_ID")
    if os.getenv("TEST_ASSET_ID"):
        test_resources["asset_id"] = os.getenv("TEST_ASSET_ID")
    if os.getenv("TEST_RUN_ID"):
        test_resources["run_id"] = os.getenv("TEST_RUN_ID")
    if os.getenv("TEST_FLOW_ID"):
        test_resources["flow_id"] = os.getenv("TEST_FLOW_ID")
    if os.getenv("TEST_ASSET_FOLDER_PATH"):
        test_resources["asset_folder_path"] = os.getenv("TEST_ASSET_FOLDER_PATH")
    if os.getenv("TEST_ANNOTATION_FOLDER_PATH"):
        test_resources["annotation_folder_path"] = os.getenv(
            "TEST_ANNOTATION_FOLDER_PATH"
        )

    return config


INTEGRATION_CONFIG = load_integration_config()


# ==============================================================================
# Skip Markers and Guards
# ==============================================================================


def has_credentials():
    """Check if credentials are available."""
    credentials = INTEGRATION_CONFIG.get("credentials", {})
    return bool(
        credentials.get("secret_key")
        and credentials.get("organization_id")
        and credentials.get("endpoint")
    )


# Marker to skip all integration tests if credentials not available
skip_if_no_credentials = pytest.mark.skipif(
    not has_credentials(),
    reason="Integration tests require credentials in .test_config.json or environment",
)


# ==============================================================================
# Client Fixtures
# ==============================================================================


@pytest.fixture(autouse=True, scope="session")
def set_integration_env_vars():
    """Set environment variables for integration testing.

    This fixture runs automatically once at the start of the test session and sets
    the credentials as environment variables so ViDataset/ViClient can pick them up.
    """
    if not has_credentials():
        yield
        return

    credentials = INTEGRATION_CONFIG.get("credentials", {})

    # Store original values
    original_env = {
        "DATATURE_VI_SECRET_KEY": os.environ.get("DATATURE_VI_SECRET_KEY"),
        "DATATURE_VI_ORGANIZATION_ID": os.environ.get("DATATURE_VI_ORGANIZATION_ID"),
        "DATATURE_VI_API_ENDPOINT": os.environ.get("DATATURE_VI_API_ENDPOINT"),
    }

    # Set environment variables from config
    if credentials.get("secret_key"):
        os.environ["DATATURE_VI_SECRET_KEY"] = credentials["secret_key"]
    if credentials.get("organization_id"):
        os.environ["DATATURE_VI_ORGANIZATION_ID"] = credentials["organization_id"]
    if credentials.get("endpoint"):
        os.environ["DATATURE_VI_API_ENDPOINT"] = credentials["endpoint"]

    yield

    # Restore original values
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)


@pytest.fixture
def integration_client():
    """Create a client with real credentials for integration testing."""
    if not has_credentials():
        pytest.skip("Integration tests require credentials")

    credentials = INTEGRATION_CONFIG.get("credentials", {})
    return Client(
        secret_key=credentials.get("secret_key"),
        organization_id=credentials.get("organization_id"),
        endpoint=credentials.get("endpoint"),
    )


@pytest.fixture
def test_config():
    """Provide access to integration test configuration."""
    return INTEGRATION_CONFIG


# ==============================================================================
# Resource ID Fixtures
# ==============================================================================


@pytest.fixture
def test_dataset_id(test_config):
    """Get test dataset ID from config."""
    dataset_id = test_config.get("test_resources", {}).get("dataset_id")
    if not dataset_id:
        pytest.skip("TEST_DATASET_ID not configured. Set it in .test_config.json")
    return dataset_id


@pytest.fixture
def test_dataset_name(test_config):
    """Get test dataset name from config."""
    dataset_name = test_config.get("test_resources", {}).get("dataset_name")
    if not dataset_name:
        pytest.skip("TEST_DATASET_NAME not configured. Set it in .test_config.json")
    return dataset_name


@pytest.fixture
def test_asset_id(test_config):
    """Get test asset ID from config."""
    asset_id = test_config.get("test_resources", {}).get("asset_id")
    if not asset_id:
        pytest.skip("TEST_ASSET_ID not configured. Set it in .test_config.json")
    return asset_id


@pytest.fixture
def test_annotation_id(test_config):
    """Get test annotation ID from config."""
    annotation_id = test_config.get("test_resources", {}).get("annotation_id")
    if not annotation_id:
        pytest.skip("TEST_ANNOTATION_ID not configured. Set it in .test_config.json")
    return annotation_id


@pytest.fixture
def test_run_id(test_config):
    """Get test run ID from config."""
    run_id = test_config.get("test_resources", {}).get("run_id")
    if not run_id:
        pytest.skip("TEST_RUN_ID not configured. Set it in .test_config.json")
    return run_id


@pytest.fixture
def test_model_id(test_config):
    """Get test model ID from config."""
    model_id = test_config.get("test_resources", {}).get("model_id")
    if not model_id:
        pytest.skip("TEST_MODEL_ID not configured. Set it in .test_config.json")
    return model_id


@pytest.fixture
def test_flow_id(test_config):
    """Get test flow ID from config."""
    flow_id = test_config.get("test_resources", {}).get("flow_id")
    if not flow_id:
        pytest.skip("TEST_FLOW_ID not configured. Set it in .test_config.json")
    return flow_id


# ==============================================================================
# Cleanup Fixtures
# ==============================================================================


@pytest.fixture
def cleanup_enabled():
    """Check if cleanup is enabled."""
    return bool(os.getenv("CLEANUP_TEST_DATA"))


@pytest.fixture
def created_assets():
    """Track assets created during tests for cleanup."""
    assets: list[str] = []
    yield assets
    # Cleanup happens in test if cleanup_enabled


@pytest.fixture
def created_annotations():
    """Track annotations created during tests for cleanup."""
    annotations: list[str] = []
    yield annotations


# ==============================================================================
# Performance Tracking
# ==============================================================================


@pytest.fixture
def performance_tracker():
    """Track performance metrics for integration tests."""
    metrics = {
        "start_time": None,
        "end_time": None,
        "duration": None,
        "requests_made": 0,
        "data_transferred": 0,
    }
    return metrics


# ==============================================================================
# Sample Image Fixtures (using real JPEG files from samples/assets)
# ==============================================================================


@pytest.fixture
def sample_image_file(test_config):
    """Provide a single sample JPEG image."""
    asset_folder_path = test_config.get("test_resources", {}).get("asset_folder_path")
    image_path = next(Path(asset_folder_path).resolve().glob("*.jpg"))
    assert image_path.exists(), f"Sample image not found: {image_path}"
    return image_path


@pytest.fixture
def sample_images_batch(test_config):
    """Provide a batch of sample JPEG images (5 images)."""
    asset_folder_path = test_config.get("test_resources", {}).get("asset_folder_path")
    images = list(Path(asset_folder_path).resolve().glob("*.jpg"))
    for img in images:
        assert img.exists(), f"Sample image not found: {img}"
    return images


@pytest.fixture
def sample_images_folder(test_config):
    """Provide the path to the sample images folder."""
    asset_folder_path = test_config.get("test_resources", {}).get("asset_folder_path")
    assert Path(asset_folder_path).exists(), (
        f"Sample images folder not found: {asset_folder_path}"
    )
    return Path(asset_folder_path)


# ==============================================================================
# SampleAnnotation Fixtures (using real JSON files from samples/annotations)
# ==============================================================================


@pytest.fixture
def sample_annotation_file(test_config):
    """Provide a single sample JSONL annotation file."""
    annotation_folder_path = test_config.get("test_resources", {}).get(
        "annotation_folder_path"
    )
    annotation_path = next(Path(annotation_folder_path).resolve().glob("*.jsonl"))
    assert annotation_path.exists(), f"Sample annotation not found: {annotation_path}"
    return annotation_path


@pytest.fixture
def sample_annotation_files_batch(test_config):
    """Provide a batch of sample JSONL annotation files."""
    annotation_folder_path = test_config.get("test_resources", {}).get(
        "annotation_folder_path"
    )
    annotations = list(Path(annotation_folder_path).resolve().glob("*.jsonl"))
    for annotation in annotations:
        assert annotation.exists(), f"Sample annotation not found: {annotation}"
    return annotations


@pytest.fixture
def sample_annotation_folder(test_config):
    """Provide the path to the sample annotation folder."""
    annotation_folder_path = test_config.get("test_resources", {}).get(
        "annotation_folder_path"
    )
    assert Path(annotation_folder_path).exists(), (
        f"Sample annotation folder not found: {annotation_folder_path}"
    )
    return Path(annotation_folder_path)
