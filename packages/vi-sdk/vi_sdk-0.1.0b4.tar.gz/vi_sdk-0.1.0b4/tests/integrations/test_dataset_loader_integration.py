#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_dataset_loader_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Dataset Loader with real datasets.
"""

import pytest
from tests.conftest import VALID_DATASET_ID, VALID_DATASET_PATH
from vi.client.errors import ViNotFoundError
from vi.dataset.loaders.loader import ViDataset

from .conftest import skip_if_no_credentials


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetLoader:
    """Test loading real datasets with ViDataset."""

    def test_load_dataset_by_id(self):
        """Test loading a dataset by ID."""
        print(f"\n🆔 Loading dataset by ID: {VALID_DATASET_ID}")

        dataset = ViDataset(VALID_DATASET_ID)

        print(f"✅ Dataset loaded: {dataset.metadata.name}")
        assert dataset is not None
        assert dataset.metadata.name is not None
        assert dataset.metadata.organization_id is not None

    def test_dataset_info(self):
        """Test getting dataset information."""
        print("\n📊 Getting dataset info...")

        dataset = ViDataset(VALID_DATASET_ID)
        info = dataset.info()

        print(f"   Name: {info.name}")
        print(f"   Organization ID: {info.organization_id}")
        print(f"   Total Assets: {info.total_assets}")
        print(f"   Total Annotations: {info.total_annotations}")
        print(f"   Splits: {', '.join(info.splits)}")

        assert info.name is not None
        assert info.organization_id is not None
        assert info.total_assets >= 0
        assert info.total_annotations >= 0
        assert len(info.splits) > 0

        print("✅ Dataset info retrieved successfully")

    def test_dataset_metadata_fields(self):
        """Test that dataset has correct metadata fields."""
        print("\n📋 Validating dataset metadata fields...")

        dataset = ViDataset(VALID_DATASET_ID)

        # Check required metadata fields
        assert dataset.metadata.name is not None
        print(f"   ✓ name: {dataset.metadata.name}")

        assert dataset.metadata.organization_id is not None
        print(f"   ✓ organization_id: {dataset.metadata.organization_id}")

        assert dataset.metadata.export_dir is not None
        print(f"   ✓ export_dir: {dataset.metadata.export_dir}")

        assert dataset.metadata.created_at is not None
        print(f"   ✓ created_at: {dataset.metadata.created_at}")

        print("✅ All metadata fields valid")

    def test_dataset_info_consistency(self):
        """Test that dataset info is consistent across multiple calls."""
        print("\n🔄 Testing dataset info consistency...")

        dataset = ViDataset(VALID_DATASET_ID)

        info1 = dataset.info()
        info2 = dataset.info()

        print(f"   Info 1: {info1.total_assets} assets")
        print(f"   Info 2: {info2.total_assets} assets")

        assert info1.name == info2.name
        assert info1.organization_id == info2.organization_id
        assert info1.total_assets == info2.total_assets
        assert info1.total_annotations == info2.total_annotations
        assert info1.splits == info2.splits

        print("✅ Dataset info is consistent")


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetLoaderIteration:
    """Test iterating over dataset assets and annotations."""

    def test_iterate_over_dump_split_assets(self):
        """Test iterating over assets in the dump split."""
        print("\n🔄 Iterating over dump split assets...")

        dataset = ViDataset(VALID_DATASET_ID)

        if not dataset.dump or not dataset.dump.base_dir:
            pytest.skip("Dataset does not have a dump split")

        asset_count = 0
        for asset in dataset.dump.assets.items:
            if asset_count > 5:
                break

            asset_count += 1
            print(f"   Asset {asset_count}: {asset.filename}")
            assert asset.filename is not None
            assert asset.filepath is not None

        print(f"✅ Iterated over {asset_count} asset(s)")
        assert asset_count > 0

    def test_iterate_over_dump_split_annotations(self):
        """Test iterating over annotations in the dump split."""
        print("\n🔄 Iterating over dump split annotations...")

        dataset = ViDataset(VALID_DATASET_ID)

        if not dataset.dump or not dataset.dump.base_dir:
            pytest.skip("Dataset does not have a dump split")

        annotation_count = 0
        for annotation in dataset.dump.annotations.items:
            if annotation_count > 5:
                break

            annotation_count += 1

            print(f"   Annotation {annotation_count}: {annotation}")
            assert len(annotation) > 0

        print(f"✅ Iterated over {annotation_count} annotation(s)")
        assert annotation_count >= 0

    def test_get_asset_by_index(self):
        """Test getting assets by index."""
        print("\n🔢 Getting assets by index...")

        dataset = ViDataset(VALID_DATASET_ID)

        if not dataset.dump or not dataset.dump.base_dir:
            pytest.skip("Dataset does not have a dump split")

        try:
            asset_0 = list(dataset.dump.assets.items)[0]
            print(f"   Asset 0: {asset_0.filename}")
            assert asset_0.filename is not None
            assert asset_0.filepath is not None

            asset_1 = list(dataset.dump.assets.items)[1]
            print(f"   Asset 1: {asset_1.filename}")
            assert asset_1.filename is not None
            assert asset_1.filepath is not None

            print("✅ Successfully retrieved assets by index")

        except IndexError:
            pytest.skip("Dataset does not have enough assets")

    def test_dataset_length(self):
        """Test getting dataset length."""
        print("\n📏 Getting dataset length...")

        dataset = ViDataset(VALID_DATASET_ID)

        if not dataset.dump or not dataset.dump.base_dir:
            pytest.skip("Dataset does not have a dump split")

        assets_length = len(dataset.dump.assets)
        annotations_length = len(dataset.dump.annotations)
        print(f"   Assets length: {assets_length}")
        print(f"   Annotations length: {annotations_length}")
        assert assets_length >= 0
        assert annotations_length >= 0


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetLoaderValidation:
    """Test dataset validation and error handling."""

    def test_load_with_invalid_id(self):
        """Test loading dataset with invalid ID format."""
        print("\n📂 Testing load with invalid ID...")

        with pytest.raises(ViNotFoundError):
            ViDataset("invalid-format-id")

        print("✅ Successfully caught invalid ID format")

    def test_dataset_has_valid_splits(self):
        """Test that dataset has valid splits configuration."""
        print("\n📊 Validating dataset splits...")

        dataset = ViDataset(VALID_DATASET_ID)

        # Check for dump split
        has_dump = dataset.dump and dataset.dump.base_dir is not None

        # Check for training + validation split pair
        has_training = dataset.training and dataset.training.base_dir is not None
        has_validation = dataset.validation and dataset.validation.base_dir is not None
        has_train_val = has_training and has_validation

        # Must have either dump split or training+validation splits
        assert has_dump or has_train_val, (
            "Dataset must have either a dump split "
            "or both training and validation splits"
        )

        print("✅ Dataset has valid splits configuration")


@pytest.mark.integration
@skip_if_no_credentials
class TestDatasetLoaderFromPath:
    """Test loading dataset by path."""

    def test_load_dataset_from_path(self):
        """Test loading dataset from path."""
        print(f"\n🆔 Testing load dataset from path: {VALID_DATASET_PATH}")

        # Load by path
        dataset = ViDataset(VALID_DATASET_PATH)

        print(f"✅ Dataset loaded by path: {dataset.metadata.name}")
        assert dataset is not None
        assert dataset.metadata.organization_id is not None

        info = dataset.info()
        print("   Total Assets:", info.total_assets)
        assert info.total_assets >= 0
