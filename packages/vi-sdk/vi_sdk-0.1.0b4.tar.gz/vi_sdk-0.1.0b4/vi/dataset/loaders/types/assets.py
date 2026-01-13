#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   assets.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK dataset loaders assets types module.
"""

from collections.abc import Generator, Iterator
from pathlib import Path

import PIL.Image as PILImage
from vi.api.resources.datasets.assets.consts import SUPPORTED_ASSET_FILE_EXTENSIONS
from vi.dataset.loaders.types.base import ViDatasetLoaderStruct


class Image(ViDatasetLoaderStruct, tag_field="type"):
    """Asset struct.

    Attributes:
        filename: Name of the image file.
        height: Image height in pixels.
        width: Image width in pixels.
        filepath: Local file path to the image if available.
        url: Remote URL to the image if available.

    """

    filename: str
    height: int
    width: int
    filepath: str | None = None
    url: str | None = None


ViAsset = Image


class ViAssets(ViDatasetLoaderStruct):
    """Assets struct.

    Attributes:
        assets_dir: Path to the directory containing asset files.

    """

    assets_dir: Path | None

    def __post_init__(self):
        """Validate assets directory exists."""
        if self.assets_dir is None:
            return
        if not self.assets_dir.exists():
            raise FileNotFoundError(f"Assets directory not found: {self.assets_dir}")
        if not self.assets_dir.is_dir():
            raise NotADirectoryError(
                f"Assets path is not a directory: {self.assets_dir}"
            )

    def __iter__(self) -> Iterator[ViAsset]:
        """Iterate over assets.

        Returns:
            Iterator of ViAsset objects.

        """
        return self.items

    def __len__(self) -> int:
        """Count supported asset files efficiently.

        Returns:
            Number of supported image files in the assets directory.

        """
        if self.assets_dir is None:
            return 0
        try:
            count = sum(
                1
                for file in self.assets_dir.iterdir()
                if file.is_file() and file.suffix in SUPPORTED_ASSET_FILE_EXTENSIONS
            )
            return count

        except OSError as e:
            raise RuntimeError(
                f"Failed to access asset directory {self.assets_dir}: {e}"
            ) from e

    @property
    def items(self) -> Generator[ViAsset, None, None]:
        """Lazily load and sort assets from the assets directory.

        Yields:
            ViAsset objects for each supported image file in the directory.

        Raises:
            RuntimeError: If unable to read the asset directory or process files.

        """
        if self.assets_dir is None:
            return
        try:
            sorted_files = sorted(
                (
                    f
                    for f in self.assets_dir.iterdir()
                    if f.is_file() and f.suffix in SUPPORTED_ASSET_FILE_EXTENSIONS
                ),
                key=lambda x: x.name,
            )

            for filepath in sorted_files:
                try:
                    with PILImage.open(filepath) as img:
                        height, width = img.size
                    yield ViAsset(filepath.name, width, height, filepath=str(filepath))
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to create ViAsset for {filepath}: {e}"
                    ) from e

        except OSError as e:
            raise RuntimeError(
                f"Failed to read asset directory {self.assets_dir}: {e}"
            ) from e
