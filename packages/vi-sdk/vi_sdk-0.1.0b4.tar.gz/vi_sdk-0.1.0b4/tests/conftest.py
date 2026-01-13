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
@Desc    :   Shared pytest configuration and fixtures for all tests.
"""

import json
from pathlib import Path

import pytest

try:
    from PIL import Image, ImageDraw

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==============================================================================
# Load Test Configuration
# ==============================================================================


def load_test_config():
    """Load test configuration from .test_config.json if it exists."""
    config_path = Path(__file__).parent / ".test_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load .test_config.json: {e}")
    return {}


TEST_CONFIG = load_test_config()


# ==============================================================================
# Test Data Constants (Available to All Tests)
# ==============================================================================

# Load from config file, fallback to defaults
VALID_SECRET_KEY = TEST_CONFIG.get("credentials", {}).get(
    "secret_key", "dtvi_" + "x" * 98
)  # 103 characters total
VALID_ORGANIZATION_ID = TEST_CONFIG.get("credentials", {}).get(
    "organization_id", "a" * 36
)  # 36 characters

# Resource IDs
VALID_DATASET_ID = TEST_CONFIG.get("test_resources", {}).get(
    "dataset_id", "dataset_123"
)
VALID_DATASET_NAME = TEST_CONFIG.get("test_resources", {}).get(
    "dataset_name", "Flickr30K"
)
VALID_DATASET_PATH = TEST_CONFIG.get("test_resources", {}).get(
    "dataset_path", "~/.datature/vi/datasets/Flickr30K"
)
VALID_ASSET_ID = TEST_CONFIG.get("test_resources", {}).get("asset_id", "asset_456")
VALID_ANNOTATION_ID = TEST_CONFIG.get("test_resources", {}).get(
    "annotation_id", "annotation_789"
)
VALID_RUN_ID = TEST_CONFIG.get("test_resources", {}).get("run_id", "run_012")
VALID_MODEL_ID = TEST_CONFIG.get("test_resources", {}).get("model_id", "model_345")
VALID_FLOW_ID = TEST_CONFIG.get("test_resources", {}).get("flow_id", "flow_123")

INVALID_SECRET_KEY_SHORT = "dtvi_short"
INVALID_SECRET_KEY_NO_PREFIX = "x" * 103
INVALID_ORGANIZATION_ID_SHORT = "short"


# ==============================================================================
# Shared Test Configuration Fixture
# ==============================================================================


@pytest.fixture
def test_config():
    """Provide access to test configuration."""
    return TEST_CONFIG


# ==============================================================================
# Shared File and Directory Fixtures
# ==============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files."""
    return tmp_path


@pytest.fixture
def test_image_file(tmp_path):
    """Create a realistic test image file (640x480 PNG)."""
    if PIL_AVAILABLE:
        # Create a 640x480 RGB image
        img = Image.new("RGB", (640, 480), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Add some visual content
        # Draw a gradient background
        for y in range(480):
            color = int(255 * (y / 480))
            draw.rectangle(
                [(0, y), (640, y + 1)], fill=(color, 200 - color // 2, 255 - color)
            )

        # Draw some shapes
        draw.rectangle([50, 50, 200, 200], outline=(255, 0, 0), width=3)
        draw.ellipse(
            [250, 100, 450, 300], fill=(0, 255, 0), outline=(0, 128, 0), width=2
        )
        draw.polygon(
            [(500, 50), (550, 150), (450, 150)], fill=(0, 0, 255), outline=(0, 0, 128)
        )

        # Add text
        try:
            draw.text((200, 350), "Test Image 640x480", fill=(0, 0, 0))
        except Exception:
            pass  # Skip if font not available

        image_path = tmp_path / "test_image.png"
        img.save(image_path, "PNG")
        return image_path

    # Fallback to minimal PNG if PIL not available
    image_path = tmp_path / "test_image.png"
    # Create a minimal valid PNG file
    png_data = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR"  # IHDR chunk
        b"\x00\x00\x00\x01\x00\x00\x00\x01"  # 1x1 image
        b"\x08\x02\x00\x00\x00\x90wS\xde"  # Rest of IHDR
        b"\x00\x00\x00\x00IEND\xaeB`\x82"  # IEND chunk
    )
    image_path.write_bytes(png_data)
    return image_path


@pytest.fixture
def test_image_small(tmp_path):
    """Create a minimal 1x1 test image (for fast tests)."""
    image_path = tmp_path / "test_image_small.png"
    # PNG signature + minimal IHDR chunk
    png_data = (
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR"  # IHDR chunk
        b"\x00\x00\x00\x01\x00\x00\x00\x01"  # 1x1 image
        b"\x08\x02\x00\x00\x00\x90wS\xde"  # Rest of IHDR
        b"\x00\x00\x00\x00IEND\xaeB`\x82"  # IEND chunk
    )
    image_path.write_bytes(png_data)
    return image_path


@pytest.fixture
def test_images_batch(tmp_path):
    """Create a batch of test images for bulk upload testing."""
    if PIL_AVAILABLE:
        images = []
        for i in range(5):
            # Create 320x240 images with different colors
            img = Image.new("RGB", (320, 240))
            draw = ImageDraw.Draw(img)

            # Different color for each image
            colors = [
                (255, 100, 100),  # Red
                (100, 255, 100),  # Green
                (100, 100, 255),  # Blue
                (255, 255, 100),  # Yellow
                (255, 100, 255),  # Magenta
            ]

            draw.rectangle([0, 0, 320, 240], fill=colors[i])
            draw.text((120, 110), f"Image {i + 1}", fill=(0, 0, 0))

            image_path = tmp_path / f"test_image_{i + 1}.png"
            img.save(image_path, "PNG")
            images.append(image_path)

        return images

    # Fallback: create minimal images
    images = []
    png_data = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    for i in range(5):
        image_path = tmp_path / f"test_image_{i + 1}.png"
        image_path.write_bytes(png_data)
        images.append(image_path)
    return images


@pytest.fixture
def test_json_file(tmp_path):
    """Create a test JSON file."""
    json_path = tmp_path / "test.json"
    json_data = {"key": "value", "number": 123}
    json_path.write_text(json.dumps(json_data))
    return json_path


@pytest.fixture
def test_large_file(tmp_path):
    """Create a large test file (10 MB)."""
    file_path = tmp_path / "large_file.bin"
    # Create 10 MB file
    with open(file_path, "wb") as f:
        f.write(b"0" * (10 * 1024 * 1024))
    return file_path
