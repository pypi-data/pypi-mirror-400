#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   path_utils.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Path resolution and validation utilities for inference.
"""

from collections.abc import Sequence
from pathlib import Path

# Supported image file extensions
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tiff",
    ".tif",
    ".webp",
}


def resolve_and_validate_path(path: str | Path) -> Path:
    """Resolve and validate a single file path.

    Performs automatic path resolution including:
    - Converting relative paths to absolute paths
    - Expanding user paths (~)
    - Expanding environment variables
    - Checking if the file exists

    Args:
        path: File path as string or Path object.

    Returns:
        Resolved absolute Path object.

    Raises:
        FileNotFoundError: If the file does not exist at the resolved path.
        ValueError: If the path is empty or invalid.

    Example:
        ```python
        # Relative path
        path = resolve_and_validate_path("./image.jpg")

        # User path
        path = resolve_and_validate_path("~/pictures/image.jpg")

        # Already absolute
        path = resolve_and_validate_path("/home/user/image.jpg")
        ```

    """
    if not path:
        raise ValueError("Path cannot be empty")

    # Convert to Path object if string
    path_obj = Path(path)

    # Expand user path (~) and environment variables
    path_obj = path_obj.expanduser()

    # Resolve to absolute path (also resolves symlinks and '..')
    try:
        resolved_path = path_obj.resolve(strict=False)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path '{path}': {e}") from e

    # Check if file exists
    if not resolved_path.exists():
        raise FileNotFoundError(
            f"File not found: '{path}'\n"
            f"Resolved to: '{resolved_path}'\n"
            f"Please check that the file exists and the path is correct."
        )

    # Check if it's a file (not a directory)
    if not resolved_path.is_file():
        raise ValueError(
            f"Path is not a file: '{path}'\n"
            f"Resolved to: '{resolved_path}'\n"
            f"Please provide a path to an image file."
        )

    return resolved_path


def resolve_and_validate_paths(
    paths: Sequence[str | Path],
) -> list[Path]:
    """Resolve and validate multiple file paths.

    Applies path resolution and validation to a list of paths. If any path
    is invalid or doesn't exist, provides detailed error information.

    Args:
        paths: Sequence of file paths as strings or Path objects.

    Returns:
        List of resolved absolute Path objects.

    Raises:
        FileNotFoundError: If any file does not exist.
        ValueError: If any path is empty or invalid.

    Example:
        ```python
        # Batch of paths
        paths = resolve_and_validate_paths(
            ["./image1.jpg", "~/pictures/image2.jpg", "/absolute/path/image3.jpg"]
        )

        for path in paths:
            print(f"Resolved: {path}")
        ```

    """
    if not paths:
        raise ValueError("Paths sequence cannot be empty")

    resolved_paths: list[Path] = []
    errors: list[tuple[int, str | Path, Exception]] = []

    for idx, path in enumerate(paths):
        try:
            resolved_path = resolve_and_validate_path(path)
            resolved_paths.append(resolved_path)
        except (FileNotFoundError, ValueError) as e:
            errors.append((idx, path, e))

    # If there are any errors, raise with detailed information
    if errors:
        error_messages = [
            f"  [{idx}] '{path}': {type(error).__name__}: {error}"
            for idx, path, error in errors
        ]
        raise FileNotFoundError(
            f"Failed to resolve {len(errors)} of {len(paths)} paths:\n"
            + "\n".join(error_messages)
        )

    return resolved_paths


def resolve_directory_to_images(
    directory: str | Path,
    recursive: bool = False,
) -> list[Path]:
    """Resolve a directory path to a list of image file paths.

    Scans a directory for image files and returns their absolute paths.
    Supports common image formats (JPEG, PNG, BMP, GIF, TIFF, WebP).

    Args:
        directory: Directory path as string or Path object.
        recursive: If True, recursively search subdirectories. Defaults to False.

    Returns:
        List of resolved absolute Path objects for image files found.

    Raises:
        FileNotFoundError: If the directory does not exist.
        ValueError: If the path is not a directory or no images found.

    Example:
        ```python
        # Get all images in a folder
        images = resolve_directory_to_images("./my_images/")

        # Recursively search subdirectories
        images = resolve_directory_to_images("./dataset/", recursive=True)
        ```

    """
    if not directory:
        raise ValueError("Directory path cannot be empty")

    # Convert to Path object
    dir_path = Path(directory)

    # Expand user path and resolve
    dir_path = dir_path.expanduser()
    try:
        resolved_dir = dir_path.resolve(strict=False)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid directory path '{directory}': {e}") from e

    # Check if directory exists
    if not resolved_dir.exists():
        raise FileNotFoundError(
            f"Directory not found: '{directory}'\n"
            f"Resolved to: '{resolved_dir}'\n"
            f"Please check that the directory exists and the path is correct."
        )

    # Check if it's a directory
    if not resolved_dir.is_dir():
        raise ValueError(
            f"Path is not a directory: '{directory}'\n"
            f"Resolved to: '{resolved_dir}'\n"
            f"Please provide a path to a directory containing images."
        )

    # Find image files
    image_files: list[Path] = []

    if recursive:
        # Recursively search all subdirectories
        for ext in IMAGE_EXTENSIONS:
            image_files.extend(resolved_dir.rglob(f"*{ext}"))
            image_files.extend(resolved_dir.rglob(f"*{ext.upper()}"))
    else:
        # Only search immediate directory
        for ext in IMAGE_EXTENSIONS:
            image_files.extend(resolved_dir.glob(f"*{ext}"))
            image_files.extend(resolved_dir.glob(f"*{ext.upper()}"))

    # Remove duplicates and sort
    image_files = sorted(set(image_files))

    if not image_files:
        raise ValueError(
            f"No image files found in directory: '{directory}'\n"
            f"Resolved to: '{resolved_dir}'\n"
            f"Supported formats: {', '.join(sorted(IMAGE_EXTENSIONS))}\n"
            f"Recursive search: {recursive}"
        )

    return image_files


def resolve_sources_to_paths(
    sources: str | Path | Sequence[str | Path],
    recursive: bool = False,
) -> list[Path]:
    """Resolve source(s) to a list of validated image paths.

    Handles three input types:
    1. Single file path → Returns [resolved_path]
    2. Directory path → Returns list of all images in directory
    3. List of paths (files/directories) → Returns list of all resolved images

    Args:
        sources: Can be:
            - Single file path (str or Path)
            - Directory path (str or Path)
            - List of file/directory paths
        recursive: If True, recursively search subdirectories when
            processing directory paths. Defaults to False.

    Returns:
        List of resolved absolute Path objects for all image files.

    Raises:
        FileNotFoundError: If any file/directory does not exist.
        ValueError: If any path is invalid or no images found.

    Example:
        ```python
        # Single file
        paths = resolve_sources_to_paths("./image.jpg")
        # Returns: [Path("/abs/path/to/image.jpg")]

        # Directory
        paths = resolve_sources_to_paths("./my_images/")
        # Returns: [Path("/abs/.../img1.jpg"), Path("/abs/.../img2.jpg"), ...]

        # Mixed list
        paths = resolve_sources_to_paths(["./image.jpg", "./folder/", "~/pic.png"])
        # Returns: All resolved image paths

        # Recursive directory search
        paths = resolve_sources_to_paths("./dataset/", recursive=True)
        # Returns: All images including subdirectories
        ```

    """
    if not sources:
        raise ValueError("Sources cannot be empty")

    resolved_paths: list[Path] = []

    # Handle single source (string or Path)
    if isinstance(sources, (str, Path)):
        source_path = Path(sources).expanduser().resolve(strict=False)

        # Check if it exists
        if not source_path.exists():
            raise FileNotFoundError(
                f"Source not found: '{sources}'\nResolved to: '{source_path}'"
            )

        # If it's a directory, get all images
        if source_path.is_dir():
            resolved_paths = resolve_directory_to_images(
                source_path, recursive=recursive
            )
        # If it's a file, validate and add
        else:
            resolved_paths = [resolve_and_validate_path(sources)]

    # Handle sequence of sources
    else:
        errors: list[tuple[int, str | Path, Exception]] = []

        for idx, source in enumerate(sources):
            try:
                source_path = Path(source).expanduser().resolve(strict=False)

                if not source_path.exists():
                    raise FileNotFoundError(f"Source not found: '{source}'")

                # If directory, expand to images
                if source_path.is_dir():
                    dir_images = resolve_directory_to_images(
                        source_path, recursive=recursive
                    )
                    resolved_paths.extend(dir_images)
                # If file, validate and add
                else:
                    resolved_paths.append(resolve_and_validate_path(source))

            except (FileNotFoundError, ValueError) as e:
                errors.append((idx, source, e))

        # If there are any errors, raise with detailed information
        if errors:
            error_messages = [
                f"  [{idx}] '{path}': {type(error).__name__}: {error}"
                for idx, path, error in errors
            ]
            raise FileNotFoundError(
                f"Failed to resolve {len(errors)} of {len(sources)} sources:\n"
                + "\n".join(error_messages)
            )

    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for path in resolved_paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)

    return unique_paths
