"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   consts.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK resources consts module.
"""

XLARGE_FILE_DOWNLOAD_CHUNK_SIZE = (
    16 * 1024 * 1024
)  # 16 MB - optimal for very large models (>20GB) - maximum throughput
LARGE_FILE_DOWNLOAD_CHUNK_SIZE = (
    8 * 1024 * 1024
)  # 8 MB - optimal for large models (5GB-20GB) - high throughput
MEDIUM_FILE_DOWNLOAD_CHUNK_SIZE = (
    4 * 1024 * 1024
)  # 4 MB - optimal for models/datasets (100MB-5GB) - balanced throughput
SMALL_FILE_DOWNLOAD_CHUNK_SIZE = 256 * 1024  # 256 KB - good for assets and medium files
TINY_FILE_DOWNLOAD_CHUNK_SIZE = (
    64 * 1024
)  # 64 KB - for small files or memory-constrained environments
