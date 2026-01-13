#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   helper.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK utils helper module.
"""

import struct
from base64 import b64encode
from pathlib import Path

import filetype
import google_crc32c

DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
MIME_DETECTION_BUFFER_SIZE = 8192  # 8KB buffer for MIME type detection


def calculate_crc32c(
    file_path: Path | str,
    base64_encoded: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> int | str:
    """Calculate CRC32C checksum for a file using chunked reading.

    Reads the file in chunks to avoid loading the entire file into memory,
    which is important for large files.

    Args:
        file_path: Path to the file to checksum.
        base64_encoded: Whether to return base64-encoded checksum.
        chunk_size: Size of chunks to read at a time in bytes.
            Defaults to 8MB. Smaller values use less memory but may be slower.

    Returns:
        The CRC32C checksum as integer or base64 string.

    """
    checksum = google_crc32c.Checksum()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            checksum.update(chunk)

    if base64_encoded:
        return b64encode(checksum.digest()).decode("utf-8")

    return struct.unpack(">l", checksum.digest())[0]


def calculate_crc32c_and_detect_mime(
    file_path: Path | str,
    base64_encoded: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> tuple[int | str, str | None]:
    """Calculate CRC32C checksum and detect MIME type in a single file pass.

    Optimized function that reads the file once to perform both operations:
    - Detects MIME type from the first chunk (file header)
    - Calculates CRC32C checksum from the entire file

    This avoids reading the file twice, which significantly improves performance.

    Args:
        file_path: Path to the file to process.
        base64_encoded: Whether to return base64-encoded checksum.
        chunk_size: Size of chunks to read at a time in bytes.
            Defaults to 8MB. Smaller values use less memory but may be slower.

    Returns:
        Tuple of (crc32c_checksum, mime_type):
        - crc32c_checksum: The CRC32C checksum as integer or base64 string
        - mime_type: Detected MIME type string or None if detection fails

    """
    checksum = google_crc32c.Checksum()
    mime_type = None
    first_chunk = True

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            checksum.update(chunk)

            # Detect MIME type from first chunk
            if first_chunk:
                # Use smaller buffer for MIME detection (filetype only needs ~262 bytes)
                mime_buffer = chunk[:MIME_DETECTION_BUFFER_SIZE]
                mime_guess = filetype.guess(mime_buffer)
                mime_type = mime_guess.mime if mime_guess else None
                first_chunk = False

    crc32c_result: int | str
    if base64_encoded:
        crc32c_result = b64encode(checksum.digest()).decode("utf-8")
    else:
        crc32c_result = struct.unpack(">l", checksum.digest())[0]

    return crc32c_result, mime_type


def build_dataset_id(organization_id: str, dataset_id: str) -> str:
    """Build dataset ID with organization ID prefix.

    Args:
        organization_id: The organization ID.
        dataset_id: The dataset ID.

    Returns:
        The combined dataset ID in format: {organization_id}_{dataset_id}.

    """
    return f"{organization_id}_{dataset_id}"
