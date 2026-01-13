#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   helper.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK resources utils helper module.
"""

from vi.api.resources import consts


def get_chunk_size(file_size: int) -> int:
    """Get the chunk size for a file based on its size.

    Args:
        file_size: The size of the file in bytes.

    Returns:
        The chunk size in bytes.

    """
    if file_size >= 20 * 1024 * 1024 * 1024:
        return consts.XLARGE_FILE_DOWNLOAD_CHUNK_SIZE
    if file_size >= 5 * 1024 * 1024 * 1024:
        return consts.LARGE_FILE_DOWNLOAD_CHUNK_SIZE
    if file_size >= 100 * 1024 * 1024:
        return consts.MEDIUM_FILE_DOWNLOAD_CHUNK_SIZE
    if file_size >= 10 * 1024 * 1024:
        return consts.SMALL_FILE_DOWNLOAD_CHUNK_SIZE
    return consts.TINY_FILE_DOWNLOAD_CHUNK_SIZE
