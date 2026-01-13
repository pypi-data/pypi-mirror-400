#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   consts.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK assets constants module.
"""

DEFAULT_ASSET_SOURCE_CLASS = "managed"
DEFAULT_ASSET_SOURCE_PROVIDER = "datature"
DEFAULT_ASSET_SOURCE_ID = "transient"
MAX_UPLOAD_BATCH_SIZE = 5000
MAX_PARALLEL_BATCHES = 5  # API rate limit: 10 sessions per 10min
MAX_PARALLEL_FILE_SPEC_WORKERS = (
    8  # Workers for parallel file spec generation within each batch
)
FILE_SPEC_PARALLEL_THRESHOLD = 10  # Minimum files to use parallel processing

DOWNLOAD_PROGRESS_UPDATE_FREQUENCY = 16
DOWNLOAD_MAX_RETRIES = 5
DOWNLOAD_RETRY_BACKOFF_BASE = 2
DOWNLOAD_RETRY_MAX_BACKOFF = 30  # Maximum backoff time in seconds

SUPPORTED_IMAGE_EXTENSIONS = [
    ".avif",
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".jfif",
    ".jp2",
    ".j2k",
    ".png",
    ".tiff",
    ".tif",
    ".webp",
]

SUPPORTED_VIDEO_EXTENSIONS = [
    ".3gp",
    ".3gpp",
    ".asf",
    ".avi",
    ".f4v",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".movie",
    ".mp4",
    ".mpg",
    ".ogg",
    ".ogv",
    ".qt",
    ".rm",
    ".rmv",
    ".webm",
    ".wmv",
]

# TODO: Add support for video extensions
SUPPORTED_ASSET_FILE_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS

SUPPORTED_IMAGE_MIME_TYPES = [
    "image/avif",
    "image/bmp",
    "image/gif",
    "image/heic",
    "image/heif",
    "image/jpeg",
    "image/jp2",
    "image/tiff",
    "image/webp",
]

SUPPORTED_VIDEO_MIME_TYPES = [
    "video/3gpp",
    "video/x-msvideo",
    "video/x-ms-asf",
    "video/mp4",
    "video/x-flv",
    "video/x-m4v",
    "video/matroska",
    "video/mpeg",
    "video/quicktime",
    "video/ogg",
    "application/vnd.rn-realmedia",
    "video/webm",
]

IMAGE_EXTENSION_TO_MIME_TYPE_MAP = {
    ".avif": "image/avif",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".jfif": "image/jpeg",
    ".jp2": "image/jp2",
    ".j2k": "image/jp2",
    ".png": "image/png",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".webp": "image/webp",
}

VIDEO_EXTENSION_TO_MIME_TYPE_MAP = {
    ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
    ".avi": "video/x-msvideo",
    ".asf": "video/x-ms-asf",
    ".wmv": "video/x-ms-asf",
    ".f4v": "video/mp4",
    ".flv": "video/x-flv",
    ".m4v": "video/x-m4v",
    ".mkv": "video/matroska",
    ".mp4": "video/mp4",
    ".mpg": "video/mpeg",
    ".mov": "video/quicktime",
    ".movie": "video/quicktime",
    ".qt": "video/quicktime",
    ".ogg": "video/ogg",
    ".ogv": "video/ogg",
    ".rm": "application/vnd.rn-realmedia",
    ".rmv": "application/vnd.rn-realmedia",
    ".webm": "video/webm",
}

# TODO: Add support for video extensions
ASSET_FILE_EXTENSION_TO_MIME_TYPE_MAP = {**IMAGE_EXTENSION_TO_MIME_TYPE_MAP}
