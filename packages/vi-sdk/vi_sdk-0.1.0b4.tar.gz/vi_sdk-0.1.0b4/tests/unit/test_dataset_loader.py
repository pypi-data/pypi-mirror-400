#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_dataset_loader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for dataset loader module.
"""

import json
from collections import OrderedDict

import pytest

from tests.conftest import VALID_DATASET_NAME, VALID_ORGANIZATION_ID
from vi.client.errors import ViError
from vi.dataset.loaders import loader
from vi.dataset.loaders.loader import ViDataset


@pytest.mark.unit
@pytest.mark.loader
class TestViDatasetLoader:
    """Test ViDataset loader."""

    def test_from_dir_with_valid_dataset(self, mock_dataset_dir):
        """Test loading dataset from directory."""
        print(f"mock_dataset_dir: {mock_dataset_dir}")
        dataset = ViDataset(mock_dataset_dir)

        assert dataset.metadata.name == VALID_DATASET_NAME
        assert dataset.metadata.organization_id == VALID_ORGANIZATION_ID
        assert dataset.dump.base_dir is not None

    def test_from_dir_with_nonexistent_directory(self, tmp_path):
        """Test loading from nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"

        # The ViDataset constructor will treat this as a dataset ID since the path doesn't exist
        # This will trigger an API call which will fail
        with pytest.raises(ViError):
            ViDataset(nonexistent)

    def test_from_dir_with_file_instead_of_directory(self, test_image_file):
        """Test loading from file instead of directory."""
        with pytest.raises(FileNotFoundError):
            ViDataset(test_image_file)

    def test_from_dir_without_metadata(self, tmp_path):
        """Test loading dataset without metadata file."""
        dataset_dir = tmp_path / "dataset_no_metadata"
        dataset_dir.mkdir()
        dump_dir = dataset_dir / "dump"
        dump_dir.mkdir()
        (dump_dir / "dump.jsonl").write_text(json.dumps({"asset_id": "asset1"}) + "\n")

        # Should create default metadata
        dataset = ViDataset(dataset_dir)
        assert dataset.metadata.name == "dataset_no_metadata"
        assert dataset.metadata.organization_id == "unknown"

    def test_from_dir_with_invalid_metadata(self, tmp_path):
        """Test loading dataset with invalid metadata JSON."""
        dataset_dir = tmp_path / "dataset_invalid_metadata"
        dataset_dir.mkdir()
        (dataset_dir / "metadata.json").write_text("{ invalid json }")

        with pytest.raises(ViError):
            ViDataset(dataset_dir)

    def test_from_id(self, mock_dataset_dir, monkeypatch):
        """Test loading dataset from ID."""
        # Mock the DEFAULT_DATASET_EXPORT_DIR
        monkeypatch.setattr(
            loader, "DEFAULT_DATASET_EXPORT_DIR", mock_dataset_dir.parent
        )

        # Use a valid dataset ID that matches the pattern
        valid_dataset_id = "test_dataset_123"

        # This will try to download the dataset, which will fail since it doesn't exist
        with pytest.raises(ViError):
            ViDataset(valid_dataset_id)

    def test_info(self, mock_dataset_dir):
        """Test getting dataset info."""
        dataset = ViDataset(mock_dataset_dir)
        info = dataset.info()

        assert info.name == VALID_DATASET_NAME
        assert info.organization_id == VALID_ORGANIZATION_ID
        assert info.total_assets >= 0
        assert info.total_annotations >= 0
        assert "dump" in info.splits


@pytest.mark.unit
@pytest.mark.loader
class TestViDatasetValidation:
    """Test dataset validation."""

    def test_validation_with_dump_split(self, tmp_path):
        """Test validation with dump split."""
        dataset_dir = tmp_path / "dataset_with_dump"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": VALID_DATASET_NAME,
            "organizationId": VALID_ORGANIZATION_ID,
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        # Create dump split with matching assets and annotations
        dump_dir = dataset_dir / "dump"
        dump_dir.mkdir()
        (dump_dir / "dump.jsonl").write_text(json.dumps({"asset_id": "asset1"}) + "\n")

        # Should not raise
        dataset = ViDataset(dataset_dir)
        assert dataset.dump.base_dir is not None

    def test_validation_with_train_valid_splits(self, tmp_path):
        """Test validation with training and validation splits."""
        dataset_dir = tmp_path / "dataset_with_splits"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": VALID_DATASET_NAME,
            "organizationId": VALID_ORGANIZATION_ID,
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        # Create training split
        train_dir = dataset_dir / "training"
        train_dir.mkdir()
        (train_dir / "training.jsonl").write_text(
            json.dumps({"asset_id": "asset1"}) + "\n"
        )

        # Create validation split
        valid_dir = dataset_dir / "validation"
        valid_dir.mkdir()
        (valid_dir / "validation.jsonl").write_text(
            json.dumps({"asset_id": "asset2"}) + "\n"
        )

        # Should not raise
        dataset = ViDataset(dataset_dir)
        assert dataset.training.base_dir is not None
        assert dataset.validation.base_dir is not None

    def test_validation_with_no_splits(self, tmp_path):
        """Test validation fails with no valid splits."""
        dataset_dir = tmp_path / "dataset_no_splits"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": VALID_DATASET_NAME,
            "organizationId": VALID_ORGANIZATION_ID,
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        # No split directories created
        with pytest.raises(ViError) as exc_info:
            ViDataset(dataset_dir)
        assert "at least one" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.loader
class TestViDatasetEdgeCases:
    """Test edge cases for dataset loader."""

    def test_dataset_with_empty_splits(self, tmp_path):
        """Test dataset with empty split directories."""
        dataset_dir = tmp_path / "dataset_empty_splits"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": VALID_DATASET_NAME,
            "organizationId": VALID_ORGANIZATION_ID,
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        # Create empty dump directory
        dump_dir = dataset_dir / "dump"
        dump_dir.mkdir()
        (dump_dir / "dump.jsonl").write_text("")  # Empty file

        # Should load but validation warnings may occur
        dataset = ViDataset(dataset_dir)
        info = dataset.info()
        assert info.total_assets == 0

    def test_dataset_with_string_path(self, mock_dataset_dir):
        """Test loading with string path instead of Path object."""
        dataset = ViDataset(str(mock_dataset_dir))
        assert dataset.metadata.name == "Flickr30K"

    def test_dataset_with_relative_path(self, mock_dataset_dir, monkeypatch):
        """Test loading with relative path."""
        monkeypatch.chdir(mock_dataset_dir.parent)
        dataset = ViDataset(mock_dataset_dir.name)
        assert dataset.metadata.organization_id == VALID_ORGANIZATION_ID

    def test_dataset_info_multiple_calls(self, mock_dataset_dir):
        """Test calling info() multiple times."""
        dataset = ViDataset(mock_dataset_dir)

        info1 = dataset.info()
        info2 = dataset.info()

        # Should return consistent results
        assert info1.name == info2.name
        assert info1.total_assets == info2.total_assets

    def test_dataset_with_special_characters_in_name(self, tmp_path):
        """Test dataset with special characters in name."""
        dataset_dir = tmp_path / "dataset-with-special_chars.123"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": "Dataset with Special Chars!",
            "organizationId": VALID_ORGANIZATION_ID,
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        dump_dir = dataset_dir / "dump"
        dump_dir.mkdir()
        (dump_dir / "dump.jsonl").write_text(json.dumps({"asset_id": "1"}) + "\n")

        dataset = ViDataset(dataset_dir)
        assert "Special Chars" in dataset.metadata.name


@pytest.mark.unit
@pytest.mark.loader
class TestViDatasetProtocol:
    """Test Dataset Protocol compliance."""

    def test_len_protocol(self, mock_dataset_dir):
        """Test __len__ method."""
        dataset = ViDataset(mock_dataset_dir)

        # Test that len() works
        total_length = len(dataset)
        assert total_length >= 0

        # Test that length matches sum of splits
        expected_length = sum(
            len(split.assets)
            for split in [dataset.training, dataset.validation, dataset.dump]
            if split.base_dir is not None
        )
        assert total_length == expected_length

    def test_getitem_protocol(self, mock_dataset_dir):
        """Test __getitem__ method."""
        dataset = ViDataset(mock_dataset_dir)

        if len(dataset) > 0:
            # Test valid indexing
            asset, annotations = dataset[0]
            assert asset is not None
            assert isinstance(annotations, list)

            # Test negative indexing
            if len(dataset) > 1:
                asset, annotations = dataset[-1]
                assert asset is not None

            # Test index out of range
            with pytest.raises(IndexError):
                _ = dataset[len(dataset)]

            with pytest.raises(IndexError):
                _ = dataset[-len(dataset) - 1]

    def test_iter_protocol(self, mock_dataset_dir):
        """Test __iter__ method."""
        dataset = ViDataset(mock_dataset_dir)

        # Test iteration
        count = 0
        for asset, annotations in dataset:
            assert asset is not None
            assert isinstance(annotations, list)
            count += 1

        # Test that iteration count matches length
        assert count == len(dataset)

    def test_index_cache_building(self, mock_dataset_dir):
        """Test index cache building."""
        dataset = ViDataset(mock_dataset_dir)

        # Initially cache should not be built
        assert not dataset._is_index_cache_built()  # noqa: SLF001

        # Accessing an item should build the cache
        if len(dataset) > 0:
            _ = dataset[0]
            assert dataset._is_index_cache_built()  # noqa: SLF001
            assert dataset._index_cache is not None  # noqa: SLF001

    def test_get_split_indices(self, mock_dataset_dir):
        """Test get_split_indices method."""
        dataset = ViDataset(mock_dataset_dir)

        # Test getting indices for each split
        for split_name in ["training", "validation", "dump"]:
            indices = dataset.get_split_indices(split_name)
            assert isinstance(indices, list)

            # All indices should be valid
            for idx in indices:
                assert 0 <= idx < len(dataset)

            # All indices should belong to the correct split
            for idx in indices:
                info = dataset.get_sample_info(idx)
                assert info["split"] == split_name

    def test_get_sample_info(self, mock_dataset_dir):
        """Test get_sample_info method."""
        dataset = ViDataset(mock_dataset_dir)

        if len(dataset) > 0:
            # Test valid index
            info = dataset.get_sample_info(0)
            assert "split" in info
            assert "local_index" in info
            assert "global_index" in info
            assert info["global_index"] == 0
            assert info["split"] in ["training", "validation", "dump"]
            assert isinstance(info["local_index"], int)
            assert info["local_index"] >= 0

            # Test invalid index
            with pytest.raises(IndexError):
                dataset.get_sample_info(len(dataset))

    def test_ml_framework_compatibility(self, mock_dataset_dir):
        """Test compatibility with ML framework patterns."""
        dataset = ViDataset(mock_dataset_dir)

        # Test that dataset can be used in ML framework patterns
        # (without actually importing frameworks to avoid dependency)

        # Test batch-like iteration
        batch_size = 4
        batch = []
        for i, (asset, annotations) in enumerate(dataset):
            batch.append((asset, annotations))
            if len(batch) == batch_size:
                # Process batch
                assert len(batch) == batch_size
                batch = []
            if i >= 10:  # Limit for test
                break

        # Test random access pattern
        if len(dataset) > 0:
            indices = list(range(min(5, len(dataset))))
            for idx in indices:
                asset, annotations = dataset[idx]
                assert asset is not None
                assert isinstance(annotations, list)

    def test_empty_dataset_protocol(self, tmp_path):
        """Test dataset protocol with empty dataset."""
        dataset_dir = tmp_path / "empty_dataset"
        dataset_dir.mkdir()

        # Create metadata
        metadata = {
            "name": "Empty Dataset",
            "organizationId": "test_org",
            "exportDir": str(dataset_dir),
            "createdAt": 1704067200,
        }
        (dataset_dir / "metadata.json").write_text(json.dumps(metadata))

        # Create empty dump directory
        dump_dir = dataset_dir / "dump"
        dump_dir.mkdir()
        (dump_dir / "dump.jsonl").write_text("")  # Empty file

        dataset = ViDataset(dataset_dir)

        # Test empty dataset protocol
        assert len(dataset) == 0

        # Test iteration on empty dataset
        items = list(dataset)
        assert len(items) == 0

        # Test indexing on empty dataset
        with pytest.raises(IndexError):
            dataset[0]  # noqa: B018

    def test_protocol_consistency(self, mock_dataset_dir):
        """Test that protocol methods are consistent."""
        dataset = ViDataset(mock_dataset_dir)

        # Test that __len__ and __iter__ are consistent
        iter_count = sum(1 for _ in dataset)
        assert iter_count == len(dataset)

        # Test that __getitem__ and __iter__ return same types
        if len(dataset) > 0:
            # Get first item via indexing
            indexed_asset, indexed_annotations = dataset[0]

            # Get first item via iteration
            iterated_asset, iterated_annotations = next(iter(dataset))

            # Both should return the same types
            assert isinstance(indexed_asset, type(iterated_asset))
            assert isinstance(indexed_annotations, type(iterated_annotations))


@pytest.mark.unit
@pytest.mark.loader
class TestViDatasetMemoryManagement:
    """Test memory management and caching features."""

    def test_memory_management_initialization(self, mock_dataset_dir):
        """Test memory management initialization."""
        dataset = ViDataset(
            mock_dataset_dir,
            memory_limit=50,
            prefetch_size=5,
            enable_memory_mapping=True,
        )

        assert dataset._memory_limit == 50  # noqa: SLF001
        assert dataset._prefetch_size == 5  # noqa: SLF001
        assert isinstance(dataset._memory_cache, OrderedDict)  # noqa: SLF001
        assert len(dataset._memory_cache) == 0  # noqa: SLF001

    def test_memory_caching(self, mock_dataset_dir):
        """Test memory caching functionality."""
        dataset = ViDataset(mock_dataset_dir, memory_limit=10)

        if len(dataset) > 0:
            # Load first sample
            sample1 = dataset[0]
            assert dataset._memory_cache is not None  # noqa: SLF001
            assert 0 in dataset._memory_cache  # noqa: SLF001
            assert len(dataset._memory_cache) == 1  # noqa: SLF001

            # Load same sample again (should hit cache)
            sample1_cached = dataset[0]
            assert sample1 == sample1_cached

            # Load multiple samples to test LRU eviction
            for i in range(min(15, len(dataset))):
                _ = dataset[i]

            # Cache should not exceed limit
            assert dataset._memory_cache is not None  # noqa: SLF001
            assert len(dataset._memory_cache) <= dataset._memory_limit  # noqa: SLF001

    def test_get_batch(self, mock_dataset_dir):
        """Test get_batch method."""
        dataset = ViDataset(mock_dataset_dir)

        if len(dataset) > 0:
            # Test valid batch
            batch_indices = list(range(min(5, len(dataset))))
            batch = dataset.get_batch(batch_indices)

            assert len(batch) == len(batch_indices)
            assert all(isinstance(sample, tuple) for sample in batch)
            assert all(len(sample) == 2 for sample in batch)

            # Test empty batch
            empty_batch = dataset.get_batch([])
            assert empty_batch == []

            # Test invalid indices
            with pytest.raises(IndexError):
                dataset.get_batch([len(dataset)])

    def test_memory_stats(self, mock_dataset_dir):
        """Test memory statistics."""
        dataset = ViDataset(mock_dataset_dir, memory_limit=20)

        stats = dataset.get_memory_stats()
        assert "cached_samples" in stats
        assert "memory_limit" in stats
        assert "prefetch_size" in stats
        assert "total_samples" in stats
        assert "cache_hit_ratio" in stats

        assert stats["memory_limit"] == 20
        assert stats["total_samples"] == len(dataset)
        assert 0 <= stats["cache_hit_ratio"] <= 1

    def test_cache_management(self, mock_dataset_dir):
        """Test cache management operations."""
        dataset = ViDataset(mock_dataset_dir, memory_limit=10)

        if len(dataset) > 0:
            # Load some samples
            for i in range(min(5, len(dataset))):
                _ = dataset[i]

            assert dataset._memory_cache is not None  # noqa: SLF001
            initial_cache_size = len(dataset._memory_cache)  # noqa: SLF001
            assert initial_cache_size > 0

            # Clear cache
            dataset.clear_cache()
            assert dataset._memory_cache is not None  # noqa: SLF001
            assert len(dataset._memory_cache) == 0  # noqa: SLF001

            # Set new memory limit
            dataset.set_memory_limit(5)
            assert dataset._memory_limit == 5  # noqa: SLF001

            # Load samples to test new limit
            for i in range(min(10, len(dataset))):
                _ = dataset[i]

            assert dataset._memory_cache is not None  # noqa: SLF001
            assert len(dataset._memory_cache) <= 5  # noqa: SLF001

    def test_prefetching(self, mock_dataset_dir):
        """Test prefetching functionality."""
        dataset = ViDataset(mock_dataset_dir, prefetch_size=3)

        if len(dataset) > 3:
            # Load first sample (should trigger prefetching)
            _ = dataset[0]

            # Check that next samples are prefetched
            # Note: This is implementation-dependent, so we just verify
            # that the prefetch mechanism doesn't cause errors
            for i in range(min(5, len(dataset))):
                _ = dataset[i]

    def test_memory_efficiency(self, mock_dataset_dir):
        """Test memory efficiency with large datasets."""
        dataset = ViDataset(mock_dataset_dir, memory_limit=5)

        if len(dataset) > 10:
            # Load many samples to test LRU eviction
            for i in range(len(dataset)):
                _ = dataset[i]

            # Cache should not exceed limit
            assert dataset._memory_cache is not None  # noqa: SLF001
            assert len(dataset._memory_cache) <= dataset._memory_limit  # noqa: SLF001

            # Most recently accessed items should be in cache
            recent_indices = list(range(max(0, len(dataset) - 5), len(dataset)))
            for idx in recent_indices:
                if idx in dataset._memory_cache:  # noqa: SLF001
                    # Verify it's the correct sample
                    cached_sample = dataset._memory_cache[idx]  # noqa: SLF001
                    direct_sample = dataset[idx]
                    assert cached_sample == direct_sample
