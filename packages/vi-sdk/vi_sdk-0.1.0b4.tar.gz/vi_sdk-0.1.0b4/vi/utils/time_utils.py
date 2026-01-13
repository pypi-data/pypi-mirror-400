#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   time_utils.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Shared timestamp and datetime formatting utilities.
"""

from datetime import datetime, timezone
from typing import Literal

TimeFormat = Literal["date", "datetime", "datetime_full"]


def format_timestamp_ms(
    timestamp_ms: int | float,
    fmt: TimeFormat = "datetime",
) -> str:
    """Convert millisecond timestamp to formatted string.

    Args:
        timestamp_ms: Unix timestamp in milliseconds.
        fmt: Output format - "date", "datetime", or "datetime_full".

    Returns:
        Formatted timestamp string, or "N/A" if invalid.

    Example:
        ```python
        format_timestamp_ms(1698249600000, "datetime")  # "2023-10-25 12:00"
        format_timestamp_ms(1698249600000, "date")  # "2023-10-25"
        ```

    """
    formats = {
        "date": "%Y-%m-%d",
        "datetime": "%Y-%m-%d %H:%M",
        "datetime_full": "%Y-%m-%d %H:%M:%S",
    }
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime(formats[fmt])
    except (ValueError, TypeError, OSError):
        return "N/A"


def format_iso_timestamp(
    iso_str: str,
    fmt: TimeFormat = "datetime",
) -> str:
    """Convert ISO format string to formatted display string.

    Args:
        iso_str: ISO 8601 format timestamp string.
        fmt: Output format - "date", "datetime", or "datetime_full".

    Returns:
        Formatted timestamp string, or "N/A" if invalid.

    Example:
        ```python
        format_iso_timestamp("2023-10-25T12:00:00Z", "datetime")  # "2023-10-25 12:00"
        format_iso_timestamp("2023-10-25T12:00:00Z", "date")  # "2023-10-25"
        ```

    """
    formats = {
        "date": "%Y-%m-%d",
        "datetime": "%Y-%m-%d %H:%M",
        "datetime_full": "%Y-%m-%d %H:%M:%S",
    }
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime(formats[fmt])
    except (ValueError, TypeError, AttributeError):
        return "N/A"


def now_iso() -> str:
    """Get current timestamp as ISO 8601 string.

    Returns:
        Current UTC timestamp in ISO 8601 format.

    Example:
        ```python
        now_iso()  # "2023-10-25T12:00:00.123456+00:00"
        ```

    """
    return datetime.now(timezone.utc).isoformat()


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string.

    Example:
        ```python
        format_duration(65)  # "1m 5s"
        format_duration(3665)  # "1h 1m 5s"
        format_duration(0.5)  # "0.5s"
        ```

    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
