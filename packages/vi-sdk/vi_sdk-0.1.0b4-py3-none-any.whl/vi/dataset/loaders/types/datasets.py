#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   datasets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset loaders datasets types module.
"""

from collections.abc import Generator
from pathlib import Path

from msgspec import field
from PIL import Image
from vi.dataset.loaders.types.annotations import ViAnnotation, ViAnnotations
from vi.dataset.loaders.types.assets import ViAsset, ViAssets
from vi.dataset.loaders.types.base import ViDatasetLoaderStruct
from vi.dataset.loaders.utils.visualize import visualize_image_with_annotations

TRAINING_SPLIT_NAME = "training"
VALIDATION_SPLIT_NAME = "validation"
DUMP_SPLIT_NAME = "dump"


class ViDatasetMetadata(ViDatasetLoaderStruct):
    """Dataset metadata struct.

    Attributes:
        name: Display name of the dataset.
        organization_id: ID of the organization owning the dataset.
        export_dir: Local directory path where the dataset was exported.
        created_at: Unix timestamp when the dataset was created.
        license: License information (dict or string).

    """

    name: str
    organization_id: str
    export_dir: str
    created_at: int
    license: dict | str | None = None


class ViDatasetSplit(ViDatasetLoaderStruct):
    """Dataset split struct.

    Attributes:
        base_dir: Base directory path containing the split subdirectories.
        assets: Assets container for this split.
        annotations: Annotations container for this split.
        split_name: Name of the split (training, validation, dump).

    """

    base_dir: Path | None
    assets: ViAssets = field(default_factory=lambda: ViAssets(assets_dir=None))
    annotations: ViAnnotations = field(
        default_factory=lambda: ViAnnotations(annotations_dir=None)
    )
    split_name: str = ""

    def __post_init__(self):
        """Initialize the dataset split by setting up assets and annotations paths."""
        if self.base_dir is None:
            return

        if self.split_name == "":
            raise ValueError("Split name is required")

        self.assets = (
            ViAssets(assets_dir=self.base_dir / self.split_name / "images")
            if (self.base_dir / self.split_name / "images").exists()
            else ViAssets(assets_dir=None)
        )

        self.annotations = (
            ViAnnotations(
                annotations_dir=self.base_dir / self.split_name / "annotations"
            )
            if (self.base_dir / self.split_name / "annotations").exists()
            else ViAnnotations(annotations_dir=None)
        )

    def iter_pairs(self) -> Generator[tuple[ViAsset, list[ViAnnotation]], None, None]:
        """Iterate over asset-annotation pairs in the dataset split.

        Yields paired assets and their corresponding annotations for processing.
        This is the primary method for iterating through dataset samples for
        training, validation, or analysis.

        Yields:
            Tuple of (ViAsset, list[ViAnnotation]) representing each sample
            in the dataset split with its associated annotations.

        Raises:
            ValueError: If the number of assets doesn't match the number of
                annotation files, or if assets/annotations are missing.

        Example:
            ```python
            from vi.dataset.loaders import ViDataset

            # Load dataset and iterate through training pairs
            dataset = ViDataset("dataset_abc123")

            for asset, annotations in dataset.training.iter_pairs():
                print(f"Processing {asset.filename}")
                print(f"  Size: {asset.width}x{asset.height}")
                print(f"  Annotations: {len(annotations)}")

                # Process each annotation
                for annotation in annotations:
                    if hasattr(annotation, "bbox"):
                        print(f"    Bbox: {annotation.bbox}")
                    if hasattr(annotation, "label"):
                        print(f"    Label: {annotation.label}")

            # Count total samples
            total_samples = sum(1 for _ in dataset.training.iter_pairs())
            print(f"Total training samples: {total_samples}")
            ```

        Note:
            This method validates that each asset has a corresponding annotation
            file. If you need to handle missing annotations, check the lengths
            of `assets` and `annotations` properties first.

        See Also:
            - `assets`: Access assets only
            - `annotations`: Access annotations only
            - `visualize()`: Visualize asset-annotation pairs

        """
        if len(self.assets) != len(self.annotations):
            raise ValueError(
                f"Number of assets ({len(self.assets)}) does not match "
                f"number of annotations ({len(self.annotations)})"
            )

        if len(self.assets) == 0 or len(self.annotations) == 0:
            return

        yield from zip(self.assets, self.annotations)

    def visualize(self) -> Generator[Image.Image, None, None]:
        """Visualize images with annotations overlaid.

        Generates PIL Image objects with annotations drawn on top of the original
        images. Useful for visual inspection of dataset quality, annotation
        accuracy, and debugging annotation issues.

        Yields:
            PIL Image objects with annotations rendered as overlays including
            bounding boxes, polygons, labels, and other annotation types.

        Raises:
            ValueError: If asset filepaths are missing or invalid.
            FileNotFoundError: If image files cannot be found.

        Example:
            ```python
            from vi.dataset.loaders import ViDataset
            import matplotlib.pyplot as plt

            # Load dataset and visualize training samples
            dataset = ViDataset("dataset_abc123")

            # Display first 5 training samples
            for i, image in enumerate(dataset.training.visualize()):
                if i >= 5:
                    break

                plt.figure(figsize=(10, 8))
                plt.imshow(image)
                plt.title(f"Training Sample {i + 1}")
                plt.axis("off")
                plt.show()

            # Save visualizations to files
            for i, image in enumerate(dataset.validation.visualize()):
                if i >= 10:
                    break
                image.save(f"validation_sample_{i + 1}.png")

            # Create a grid of visualizations
            images = list(dataset.training.visualize())[:9]  # First 9 images
            fig, axes = plt.subplots(3, 3, figsize=(15, 15))
            for i, (ax, img) in enumerate(zip(axes.flat, images)):
                ax.imshow(img)
                ax.set_title(f"Sample {i + 1}")
                ax.axis("off")
            plt.tight_layout()
            plt.show()
            ```

        Note:
            This method loads and processes images in memory. For large datasets,
            consider processing in batches to avoid memory issues. The visualization
            includes all annotation types supported by the dataset.

        See Also:
            - `iter_pairs()`: Access raw asset-annotation pairs
            - `visualize_image_with_annotations()`: Low-level visualization function
            - [Dataset Loaders Guide](../../guide/dataset-loaders.md): Complete guide with visualization examples

        """
        for asset, annotations in self.iter_pairs():
            if asset.filepath is None:
                raise ValueError("Could not find asset filepath")

            yield visualize_image_with_annotations(
                Path(asset.filepath),
                asset.width,
                asset.height,
                annotations,
            )


class ViDatasetDump(ViDatasetSplit):
    """Dataset dump struct.

    Attributes:
        split_name: Automatically set to 'dump'.

    """

    split_name: str = DUMP_SPLIT_NAME


class ViDatasetTraining(ViDatasetSplit):
    """Dataset train split struct.

    Attributes:
        split_name: Automatically set to 'training'.

    """

    split_name: str = TRAINING_SPLIT_NAME


class ViDatasetValidation(ViDatasetSplit):
    """Dataset validation split struct.

    Attributes:
        split_name: Automatically set to 'validation'.

    """

    split_name: str = VALIDATION_SPLIT_NAME


class ViDatasetSplitInfo(ViDatasetLoaderStruct):
    """Dataset split info."""

    assets: int
    annotations: int


class ViDatasetInfo(ViDatasetLoaderStruct):
    """Dataset info response."""

    name: str
    organization_id: str
    created_at: str
    export_dir: str
    splits: dict[str, ViDatasetSplitInfo]
    total_assets: int
    total_annotations: int
