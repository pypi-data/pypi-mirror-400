#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   loader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset loader module.
"""

from __future__ import annotations

import mmap
import os
import shutil
import threading
from collections import OrderedDict, deque
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

import msgspec
from rich import print as rprint
from vi.api.client import ViClient
from vi.client.consts import DATATURE_VI_API_ENDPOINT
from vi.client.errors import ViError, ViValidationError
from vi.consts import DEFAULT_DATASET_EXPORT_DIR
from vi.dataset.loaders.types.annotations import ViAnnotation
from vi.dataset.loaders.types.assets import ViAsset
from vi.dataset.loaders.types.datasets import (
    DUMP_SPLIT_NAME,
    TRAINING_SPLIT_NAME,
    VALIDATION_SPLIT_NAME,
    ViDatasetDump,
    ViDatasetInfo,
    ViDatasetMetadata,
    ViDatasetSplit,
    ViDatasetSplitInfo,
    ViDatasetTraining,
    ViDatasetValidation,
)
from vi.dataset.loaders.utils.warnings import (
    ASSET_ANNOTATION_MISMATCH_WARNING,
    NO_ANNOTATIONS_WARNING,
    NO_ASSETS_WARNING,
)

DEFAULT_SPLITS = [DUMP_SPLIT_NAME, VALIDATION_SPLIT_NAME, TRAINING_SPLIT_NAME]


class ViDataset:
    """Auto dataset class that automatically loads datasets from ID or path.

    This is the recommended way to load datasets. ViDataset handles automatic
    detection of whether the input is a dataset ID (for previously downloaded
    datasets) or a local path to a dataset directory. When credentials are provided,
    it can automatically download datasets from the Datature Vi platform.

    Example:
        ```python
        from vi.dataset import ViDataset

        # Load dataset by ID (from default download location)
        dataset = ViDataset("dataset_abc123")

        # Load dataset from local path
        dataset = ViDataset("/path/to/my_dataset")

        # Auto-download dataset with explicit credentials
        dataset = ViDataset(
            dataset_id="dataset_abc123",
            secret_key="your-secret-key",
            organization_id="your-organization-id",
        )

        # Auto-download using environment variables (DATATURE_VI_SECRET_KEY,
        # DATATURE_VI_ORGANIZATION_ID)
        dataset = ViDataset("dataset_abc123")

        # Access dataset information
        print(f"Dataset: {dataset.metadata.name}")
        print(f"Training assets: {len(dataset.training.assets)}")
        ```

    Args:
        dataset_id_or_path: Either a dataset ID (string) for previously downloaded
            datasets, or a path (string or Path) to a local dataset directory.
        secret_key: Your Vi SDK secret key for automatic downloading. If None,
            will attempt to load from DATATURE_VI_SECRET_KEY environment variable
            or from config file.
        organization_id: Your organization ID for automatic downloading. If None,
            will attempt to load from DATATURE_VI_ORGANIZATION_ID environment variable
            or from config file.
        save_path: Directory to save downloaded datasets. Defaults to
            ~/.datature/vi/datasets/.

    """

    metadata: ViDatasetMetadata
    dump: ViDatasetDump = ViDatasetDump(base_dir=None)
    training: ViDatasetTraining = ViDatasetTraining(base_dir=None)
    validation: ViDatasetValidation = ViDatasetValidation(base_dir=None)

    # Dataset protocol support
    _index_cache: list[tuple[str, int]] | None = None
    _total_length: int | None = None

    # Memory management and caching (thread-safe)
    _memory_cache: OrderedDict[int, tuple[ViAsset, list[ViAnnotation]]] | None = None
    _cache_lock: threading.Lock | None = None
    _memory_limit: int = 1000  # Maximum number of items to cache
    _memory_mapping: dict[str, mmap.mmap] | None = None
    _prefetch_queue: deque[int] | None = None
    _prefetch_size: int = 10
    _max_prefetch_queue_size: int = 100  # Maximum items in prefetch queue
    _cache_requests: int = 0
    _cache_hits: int = 0

    def __init__(
        self,
        dataset_id_or_path: str | Path,
        secret_key: str | None = None,
        organization_id: str | None = None,
        endpoint: str | None = None,
        save_path: Path | str = DEFAULT_DATASET_EXPORT_DIR,
        overwrite: bool = False,
        memory_limit: int = 1000,
        prefetch_size: int = 10,
        max_prefetch_queue_size: int = 100,
        enable_memory_mapping: bool = True,
    ) -> None:
        """Initialize the dataset with automatic detection of ID vs path.

        Args:
            dataset_id_or_path: Either a dataset ID or path to dataset directory.
            secret_key: Your Vi SDK secret key for automatic downloading. If None,
                will attempt to load from DATATURE_VI_SECRET_KEY environment variable.
            organization_id: Your organization ID for automatic downloading. If None,
                will attempt to load from DATATURE_VI_ORGANIZATION_ID environment variable.
            endpoint: API endpoint URL. If None, will attempt to load from
                DATATURE_VI_API_ENDPOINT environment variable or use the default.
            save_path: Directory to save downloaded datasets.
            overwrite: Whether to overwrite the dataset if it already exists.
                If True, the dataset will be re-downloaded and replaced even if it already exists.
            memory_limit: Maximum number of samples to keep in memory cache.
            prefetch_size: Number of samples to prefetch ahead of current access. Defaults to 10.
            max_prefetch_queue_size: Maximum number of items in the prefetch queue.
                Bounds memory pressure on large datasets. Defaults to 100.
            enable_memory_mapping: Whether to use memory mapping for large files.

        Raises:
            FileNotFoundError: If the dataset directory doesn't exist.
            ValueError: If the input is neither a valid dataset ID nor a valid path.
            ViError: If there are issues loading the dataset.

        """
        # Load credentials from environment variables if not provided
        if secret_key is None:
            secret_key = os.getenv("DATATURE_VI_SECRET_KEY")
        if organization_id is None:
            organization_id = os.getenv("DATATURE_VI_ORGANIZATION_ID")
        if endpoint is None:
            endpoint = os.getenv("DATATURE_VI_API_ENDPOINT", DATATURE_VI_API_ENDPOINT)

        # Convert to string for easier processing
        input_str = str(dataset_id_or_path)

        # Try to treat as path first
        potential_path = Path(input_str).expanduser().resolve()
        if potential_path.exists() and potential_path.is_dir():
            dataset_full_dir = potential_path
        else:
            # Treat as dataset ID - construct download path
            dataset_full_dir = (Path(save_path) / input_str).expanduser().resolve()

            if not dataset_full_dir.exists() or overwrite:
                shutil.rmtree(dataset_full_dir, ignore_errors=True)
                self._download_dataset(
                    dataset_id=input_str,
                    secret_key=secret_key,
                    organization_id=organization_id,
                    endpoint=endpoint,
                    save_path=save_path,
                    overwrite=overwrite,
                )

        # Load the dataset data directly
        self._load_data(dataset_full_dir)

        # Initialize memory management with thread-safe lock
        self._init_cache(
            memory_limit=memory_limit,
            prefetch_size=prefetch_size,
            max_prefetch_queue_size=max_prefetch_queue_size,
            enable_memory_mapping=enable_memory_mapping,
        )

    def _init_cache(
        self,
        memory_limit: int = 1000,
        prefetch_size: int = 10,
        max_prefetch_queue_size: int = 100,
        enable_memory_mapping: bool = True,
    ) -> None:
        """Initialize memory cache and related thread-safe structures.

        Args:
            memory_limit: Maximum number of samples to keep in memory cache.
            prefetch_size: Number of samples to prefetch ahead of current access.
            max_prefetch_queue_size: Maximum number of items in the prefetch queue.
            enable_memory_mapping: Whether to use memory mapping for large files.

        """
        self._memory_limit = memory_limit
        self._prefetch_size = prefetch_size
        self._max_prefetch_queue_size = max_prefetch_queue_size
        self._memory_cache = OrderedDict()
        self._cache_lock = threading.Lock()
        self._memory_mapping = {} if enable_memory_mapping else None
        self._prefetch_queue = deque(maxlen=max_prefetch_queue_size)
        self._cache_requests = 0
        self._cache_hits = 0

    def _download_dataset(
        self,
        dataset_id: str,
        secret_key: str | None,
        organization_id: str | None,
        endpoint: str,
        save_path: Path | str,
        overwrite: bool,
    ) -> None:
        """Download a dataset from the Datature Vi platform.

        Args:
            dataset_id: The dataset ID to download.
            secret_key: Vi SDK secret key.
            organization_id: Organization ID.
            endpoint: API endpoint URL.
            save_path: Directory to save the dataset.
            overwrite: Whether to overwrite the dataset if it already exists.
                If True, the dataset will be re-downloaded and replaced even if it already exists.

        Raises:
            ViError: If download fails.

        """
        # Initialize client (will automatically load credentials from env vars/config if None)
        client = ViClient(
            secret_key=secret_key,
            organization_id=organization_id,
            endpoint=endpoint,
        )

        # Download the dataset
        downloaded_dataset = client.get_dataset(
            dataset_id=dataset_id,
            save_dir=save_path,
            overwrite=overwrite,
            show_progress=True,
        )

        # Verify the dataset was downloaded successfully
        if not Path(downloaded_dataset.save_dir).exists():
            raise ViError(
                "Dataset download completed but directory not found",
                suggestion="Check your network connection and try again",
            )

    def _load_data(self, dataset_dir: Path) -> None:
        """Load dataset data from directory into this instance.

        Args:
            dataset_dir: Full path to the dataset directory.

        Raises:
            FileNotFoundError: If dataset directory doesn't exist.
            ValueError: If metadata files are missing or invalid.

        """
        if not dataset_dir.exists() or not dataset_dir.is_dir():
            raise FileNotFoundError(
                f"Dataset directory not found: {dataset_dir}. "
                "Make sure that you have already downloaded the dataset, and the provided "
                "dataset ID is the correct one. If you have not downloaded the dataset, "
                "you can download it using `client.get_dataset(YOUR_DATASET_ID)`."
            )

        # Load metadata from metadata.json
        metadata_path = dataset_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, encoding="utf-8") as f:
                    metadata_data = f.read()
                self.metadata = msgspec.json.decode(
                    metadata_data, type=ViDatasetMetadata
                )
            except Exception as e:
                raise ViError(
                    e,
                    suggestion=(
                        "Check that the metadata.json file is valid JSON "
                        "and has the correct format"
                    ),
                ) from e

        else:
            self.metadata = ViDatasetMetadata(
                name=dataset_dir.name,
                organization_id="unknown",
                export_dir=str(dataset_dir),
                created_at=int(datetime.now().timestamp()),
            )

        try:
            dump_dir = dataset_dir / DUMP_SPLIT_NAME
            train_dir = dataset_dir / TRAINING_SPLIT_NAME
            valid_dir = dataset_dir / VALIDATION_SPLIT_NAME

            self.dump = (
                ViDatasetDump(base_dir=dataset_dir)
                if dump_dir.exists()
                else ViDatasetDump(base_dir=None)
            )
            self.training = (
                ViDatasetTraining(base_dir=dataset_dir)
                if train_dir.exists()
                else ViDatasetTraining(base_dir=None)
            )
            self.validation = (
                ViDatasetValidation(base_dir=dataset_dir)
                if valid_dir.exists()
                else ViDatasetValidation(base_dir=None)
            )

            self._validate()

        except Exception as e:
            raise ViError(
                e,
                suggestion=(
                    "Check that the dataset directory structure is "
                    "correct and split files are valid"
                ),
            ) from e

    def info(self) -> ViDatasetInfo:
        """Get comprehensive dataset information and statistics.

        Provides a summary of the dataset including metadata, split information,
        and total counts of assets and annotations across all splits.

        Returns:
            ViDatasetInfo object containing dataset name, organization ID,
            creation date, export directory, split statistics, and total counts.

        Example:
            ```python
            from vi.dataset.loaders import ViDataset

            # Load dataset and get information
            dataset = ViDataset("dataset_abc123")
            info = dataset.info()

            # Access dataset metadata
            print(f"Dataset Name: {info.name}")
            print(f"Organization: {info.organization_id}")
            print(f"Created: {info.created_at}")
            print(f"Export Directory: {info.export_dir}")

            # Check overall statistics
            print(f"Total Assets: {info.total_assets}")
            print(f"Total Annotations: {info.total_annotations}")

            # Check split-specific statistics
            for split_name, split_info in info.splits.items():
                print(f"{split_name.title()} Split:")
                print(f"  Assets: {split_info.assets}")
                print(f"  Annotations: {split_info.annotations}")

            # Calculate ratios
            if info.total_assets > 0:
                train_ratio = info.splits["training"].assets / info.total_assets
                print(f"Training split ratio: {train_ratio:.2%}")
            ```

        Note:
            Only splits that exist in the dataset (have a base_dir) are included
            in the statistics. Empty or missing splits are excluded from counts.

        See Also:
            - `training`, `validation`, `testing`: Access individual splits
            - [Dataset Loader Guide](../../guide/dataset-loaders.md): Working with dataset information

        """
        splits_info = {}
        for split_name in DEFAULT_SPLITS:
            split = getattr(self, split_name)

            if split.base_dir is not None:
                splits_info[split_name] = ViDatasetSplitInfo(
                    assets=len(split.assets),
                    annotations=len(split.annotations),
                )

        return ViDatasetInfo(
            name=self.metadata.name,
            organization_id=self.metadata.organization_id,
            created_at=datetime.fromtimestamp(self.metadata.created_at).isoformat(),
            export_dir=self.metadata.export_dir,
            splits=splits_info,
            total_assets=sum(
                len(split.assets)
                for split in [
                    getattr(self, split_name) for split_name in DEFAULT_SPLITS
                ]
                if split.base_dir is not None
            ),
            total_annotations=sum(
                len(split.annotations)
                for split in [
                    getattr(self, split_name) for split_name in DEFAULT_SPLITS
                ]
                if split.base_dir is not None
            ),
        )

    def __len__(self) -> int:
        """Return the total number of samples in the dataset.

        Implements standard dataset protocol for compatibility with ML frameworks.

        Returns:
            Total number of samples across all splits.

        Example:
            ```python
            from vi.dataset import ViDataset

            dataset = ViDataset("dataset_abc123")
            print(f"Dataset size: {len(dataset)}")
            ```

        """
        if self._total_length is None:
            self._total_length = sum(
                len(split.assets)
                for split in [
                    getattr(self, split_name) for split_name in DEFAULT_SPLITS
                ]
                if split.base_dir is not None
            )
        return self._total_length

    def __getitem__(self, index: int) -> tuple[ViAsset, list[ViAnnotation]]:
        """Get a sample by index for dataset protocol compatibility.

        Implements standard dataset protocol for random access to samples.
        This enables seamless integration with ML frameworks.

        Args:
            index: Index of the sample to retrieve (0-based).

        Returns:
            Tuple of (ViAsset, list[ViAnnotation]) representing the sample.

        Raises:
            IndexError: If index is out of range.
            RuntimeError: If unable to load the sample.

        Example:
            ```python
            from vi.dataset import ViDataset

            dataset = ViDataset("dataset_abc123")

            # Direct indexing
            asset, annotations = dataset[0]
            ```

        """
        if not self._is_index_cache_built():
            self._build_index_cache()

        if index < 0 or index >= len(self):
            raise IndexError(
                f"Index {index} is out of range for dataset of size {len(self)}"
            )

        # Track cache requests and check cache (thread-safe)
        with self._cache_lock:
            self._cache_requests += 1

            # Check memory cache first
            if self._memory_cache is not None and index in self._memory_cache:
                # Move to end (most recently used)
                sample = self._memory_cache.pop(index)
                self._memory_cache[index] = sample
                self._cache_hits += 1
                return sample

        # Load from disk
        if self._index_cache is None:
            raise RuntimeError("Index cache not built")
        split_name, local_index = self._index_cache[index]
        split: ViDatasetSplit = getattr(self, split_name)

        try:
            # Get asset and annotations by index
            asset = list(split.assets)[local_index]
            annotations = list(split.annotations)[local_index]
            sample = (asset, annotations)

            # Add to cache and manage memory
            self._add_to_cache(index, sample)

            # Prefetch next samples
            self._prefetch_samples(index)

            return sample
        except Exception as e:
            raise RuntimeError(
                f"Failed to load sample at index {index} from {split_name} split: {e}"
            ) from e

    def __iter__(self) -> Iterator[tuple[ViAsset, list[ViAnnotation]]]:
        """Create an iterator over all samples in the dataset.

        Implements standard dataset protocol for iteration support.
        This provides a consistent interface for iterating through the dataset.

        Returns:
            Iterator yielding (ViAsset, list[ViAnnotation]) tuples.

        Example:
            ```python
            from vi.dataset import ViDataset

            dataset = ViDataset("dataset_abc123")

            # Direct iteration
            for asset, annotations in dataset:
                print(f"Processing {asset.filename}")
            ```

        """
        # Use the existing iter_pairs method for consistency
        for split_name in DEFAULT_SPLITS:
            split: ViDatasetSplit = getattr(self, split_name)
            if split.base_dir is not None:
                yield from split.iter_pairs()

    def _is_index_cache_built(self) -> bool:
        """Check if the index cache has been built.

        Returns:
            True if index cache is built, False otherwise.

        """
        return self._index_cache is not None

    def _build_index_cache(self) -> None:
        """Build index cache for efficient random access.

        Creates a mapping from global indices to (split_name, local_index) tuples.
        This enables O(1) random access to any sample in the dataset.
        """
        self._index_cache = []

        for split_name in DEFAULT_SPLITS:
            split: ViDatasetSplit = getattr(self, split_name)
            if split.base_dir is not None and len(split.assets) > 0:
                for local_index in range(len(split.assets)):
                    self._index_cache.append((split_name, local_index))

    def get_split_indices(self, split_name: str) -> list[int]:
        """Get global indices for a specific split.

        Args:
            split_name: Name of the split ('training', 'validation', 'dump').

        Returns:
            List of global indices that belong to the specified split.

        Example:
            ```python
            dataset = ViDataset("dataset_abc123")
            train_indices = dataset.get_split_indices("training")
            print(f"Training samples: {len(train_indices)}")
            ```

        """
        if not self._is_index_cache_built():
            self._build_index_cache()

        if self._index_cache is None:
            return []
        return [
            global_idx
            for global_idx, (split, _) in enumerate(self._index_cache)
            if split == split_name
        ]

    def get_sample_info(self, index: int) -> dict[str, str | int]:
        """Get metadata about a specific sample.

        Args:
            index: Global index of the sample.

        Returns:
            Dictionary containing sample metadata including split name and local index.

        """
        if not self._is_index_cache_built():
            self._build_index_cache()

        if index < 0 or index >= len(self):
            raise IndexError(
                f"Index {index} is out of range for dataset of size {len(self)}"
            )

        if self._index_cache is None:
            raise RuntimeError("Index cache not built")
        # Type assertion: we know _index_cache is not None after the check above
        index_cache = self._index_cache
        split_name, local_index = index_cache[index]
        return {"split": split_name, "local_index": local_index, "global_index": index}

    def _add_to_cache(
        self, index: int, sample: tuple[ViAsset, list[ViAnnotation]]
    ) -> None:
        """Add sample to memory cache with LRU eviction.

        Args:
            index: Index of the sample.
            sample: The sample data to cache.

        """
        with self._cache_lock:
            if self._memory_cache is None:
                return

            # Remove oldest items if cache is full
            while len(self._memory_cache) >= self._memory_limit:
                self._memory_cache.popitem(last=False)  # Remove oldest

            # Add new sample
            self._memory_cache[index] = sample

    def _prefetch_samples(self, current_index: int) -> None:
        """Prefetch upcoming samples for better performance.

        Uses a bounded queue to limit memory pressure. Only loads samples into
        cache when there's headroom (cache is not full), preventing prefetch
        from evicting recently used items.

        Args:
            current_index: Current sample index to prefetch from.

        """
        if self._prefetch_size <= 0:
            return

        if self._prefetch_queue is None:
            self._prefetch_queue = deque(maxlen=self._max_prefetch_queue_size)

        # Queue up indices to prefetch (bounded by maxlen)
        with self._cache_lock:
            for i in range(1, self._prefetch_size + 1):
                prefetch_index = current_index + i
                if prefetch_index >= len(self):
                    break

                # Only queue if not already in cache or queue
                if (
                    self._memory_cache is not None
                    and prefetch_index not in self._memory_cache
                    and prefetch_index not in self._prefetch_queue
                ):
                    # deque with maxlen automatically drops oldest items when full
                    self._prefetch_queue.append(prefetch_index)

        # Process queued items only if there's headroom in the cache
        # This prevents prefetch from evicting recently used items
        while True:
            with self._cache_lock:
                if not self._prefetch_queue or self._memory_cache is None:
                    break

                # Only prefetch if cache has headroom
                cache_headroom = self._memory_limit - len(self._memory_cache)
                if cache_headroom <= 0:
                    break

                prefetch_index = self._prefetch_queue.popleft()

                # Skip if already cached (may have been accessed since queuing)
                if prefetch_index in self._memory_cache:
                    continue

            try:
                if self._index_cache is None:
                    continue
                split_name, local_index = self._index_cache[prefetch_index]
                split: ViDatasetSplit = getattr(self, split_name)

                asset = list(split.assets)[local_index]
                annotations = list(split.annotations)[local_index]
                sample = (asset, annotations)

                # Add directly without eviction (we checked headroom)
                with self._cache_lock:
                    if self._memory_cache is not None:
                        self._memory_cache[prefetch_index] = sample
            except Exception:
                # Skip prefetch on error
                continue

    def get_batch(self, indices: list[int]) -> list[tuple[ViAsset, list[ViAnnotation]]]:
        """Get a batch of samples by indices.

        Args:
            indices: List of indices to retrieve.

        Returns:
            List of (ViAsset, list[ViAnnotation]) tuples.

        Raises:
            IndexError: If any index is out of range.

        Example:
            ```python
            dataset = ViDataset("dataset_abc123")

            # Get batch of samples
            batch = dataset.get_batch([0, 1, 2, 3])
            print(f"Batch size: {len(batch)}")

            # Use with training
            for asset, annotations in batch:
                # Process sample
                pass
            ```

        """
        if not indices:
            return []

        # Validate all indices
        for index in indices:
            if index < 0 or index >= len(self):
                raise IndexError(
                    f"Index {index} is out of range for dataset of size {len(self)}"
                )

        # Load samples
        batch = []
        for index in indices:
            sample = self[index]  # This will use caching
            batch.append(sample)

        return batch

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory usage statistics.

        Returns:
            Dictionary with memory usage information.

        """
        with self._cache_lock:
            return {
                "cached_samples": (
                    len(self._memory_cache) if self._memory_cache is not None else 0
                ),
                "memory_limit": self._memory_limit,
                "prefetch_size": self._prefetch_size,
                "prefetch_queue_size": (
                    len(self._prefetch_queue) if self._prefetch_queue is not None else 0
                ),
                "max_prefetch_queue_size": self._max_prefetch_queue_size,
                "total_samples": len(self),
                "cache_hit_ratio": (
                    self._cache_hits / max(1, self._cache_requests) * 100
                ),
            }

    def clear_cache(self) -> None:
        """Clear the memory cache to free up memory."""
        with self._cache_lock:
            if self._memory_cache is not None:
                self._memory_cache.clear()

    def set_memory_limit(self, limit: int) -> None:
        """Set the memory cache limit.

        Args:
            limit: Maximum number of samples to keep in cache.

        """
        with self._cache_lock:
            self._memory_limit = limit

            # Evict excess items if needed
            if self._memory_cache is not None:
                while len(self._memory_cache) > self._memory_limit:
                    self._memory_cache.popitem(last=False)

    def set_prefetch_queue_size(self, max_size: int) -> None:
        """Set the maximum prefetch queue size.

        Controls memory pressure by limiting how many indices can be queued
        for prefetching. Smaller values reduce memory pressure but may reduce
        prefetch effectiveness.

        Args:
            max_size: Maximum number of items in the prefetch queue.

        """
        with self._cache_lock:
            self._max_prefetch_queue_size = max_size

            # Recreate queue with new maxlen (deque doesn't support changing maxlen)
            if self._prefetch_queue is not None:
                old_items = list(self._prefetch_queue)
                self._prefetch_queue = deque(maxlen=max_size)
                # Re-add items, newer items take priority
                for item in old_items[-max_size:]:
                    self._prefetch_queue.append(item)

    @classmethod
    def _load(cls, dataset_dir: Path) -> ViDataset:
        """Load dataset from full directory.

        Args:
            dataset_dir: Full path to the dataset directory.

        Returns:
            Loaded ViDataset instance.

        Raises:
            FileNotFoundError: If dataset directory doesn't exist.
            ValueError: If metadata files are missing or invalid.

        """
        # Create instance with dummy path to avoid constructor issues
        instance = object.__new__(cls)
        instance._load_data(dataset_dir)
        instance._init_cache()
        return instance

    def _validate_split(self, split) -> None:
        """Validate a single dataset split.

        Args:
            split: The dataset split to validate.

        Raises:
            ValueError: If asset/annotation counts don't match.

        """
        num_assets = len(split.assets)
        num_annotations = len(split.annotations)

        if num_assets == 0:
            rprint(NO_ASSETS_WARNING.format(split_name=split.split_name))
        if num_annotations == 0:
            rprint(NO_ANNOTATIONS_WARNING.format(split_name=split.split_name))
        if num_assets != num_annotations:
            rprint(
                ASSET_ANNOTATION_MISMATCH_WARNING.format(
                    num_assets=num_assets,
                    num_annotations=num_annotations,
                    split_name=split.split_name,
                )
            )

    def _validate(self) -> None:
        """Validate loaded dataset.

        Checks all splits for consistency and warnings.
        """
        # Collect loaded splits
        loaded_splits = {
            split_name: getattr(self, split_name)
            for split_name in DEFAULT_SPLITS
            if getattr(self, split_name).base_dir is not None
        }

        # Check if we have valid split combinations
        has_train_valid = (
            TRAINING_SPLIT_NAME in loaded_splits
            and VALIDATION_SPLIT_NAME in loaded_splits
        )
        has_dump = DUMP_SPLIT_NAME in loaded_splits

        if has_train_valid:
            # Validate training and validation splits
            self._validate_split(loaded_splits[TRAINING_SPLIT_NAME])
            self._validate_split(loaded_splits[VALIDATION_SPLIT_NAME])
        elif has_dump:
            # Validate dump split
            self._validate_split(loaded_splits[DUMP_SPLIT_NAME])
        else:
            raise ViValidationError(
                "Dataset must have at least one training and validation split, "
                "or one dump split if no train-valid split was specified during dataset export.",
                suggestion=(
                    "Check your dataset export configuration or "
                    "ensure the correct split files are present"
                ),
            )
