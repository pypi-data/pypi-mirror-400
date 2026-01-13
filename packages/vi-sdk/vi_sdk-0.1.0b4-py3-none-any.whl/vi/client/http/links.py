#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   links.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK client HTTP links module.
"""

from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import quote, urlencode


class LinkBuilder:
    """Builder for constructing resource links safely.

    This class provides a fluent interface for building URL paths with
    proper handling of path segments and query parameters.

    Example:
        >>> builder = LinkBuilder("/workspaces")
        >>> link = (
        ...     builder.add_segment("org123")
        ...     .add_segment("runs")
        ...     .add_segment("run456")
        ...     .add_param("intent", "sdkLocalDeploy")
        ...     .add_param("contents", True)
        ...     .build()
        ... )
        >>> print(link)
        /workspaces/org123/runs/run456?intent=sdkLocalDeploy&contents=y

    """

    def __init__(self, base_path: str = ""):
        """Initialize the link builder.

        Args:
            base_path: Optional base path to start building from.

        """
        self._segments: list[str] = []
        self._params: dict[str, str] = {}

        if base_path:
            # Normalize and add each segment from the base path
            normalized = base_path.strip("/")
            if normalized:
                self._segments.extend(normalized.split("/"))

    def add_segment(self, segment: str, encode: bool = False) -> "LinkBuilder":
        """Add a path segment to the URL.

        Args:
            segment: The path segment to add.
            encode: Whether to URL-encode the segment. Defaults to False
                since most IDs are alphanumeric.

        Returns:
            Self for method chaining.

        """
        if segment:
            cleaned = segment.strip("/")
            if cleaned:
                if encode:
                    cleaned = quote(cleaned, safe="")
                self._segments.append(cleaned)
        return self

    def add_param(self, key: str, value: str | bool | None) -> "LinkBuilder":
        """Add a query parameter to the URL.

        Args:
            key: The parameter name.
            value: The parameter value. Booleans are converted to "y"/"n".
                None values are ignored.

        Returns:
            Self for method chaining.

        """
        if value is None:
            return self

        if isinstance(value, bool):
            self._params[key] = "y" if value else "n"
        else:
            self._params[key] = str(value)
        return self

    def build(self) -> str:
        """Build the final link string.

        Returns:
            The constructed URL path with query parameters.

        """
        path = "/" + "/".join(self._segments) if self._segments else "/"

        if self._params:
            path += "?" + urlencode(self._params)

        return path


class ResourceLinkParser(ABC):
    """Parse a resource link."""

    _base_link: str

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> str:
        """Parse the resource link.

        Args:
            *args: Positional arguments for link construction.
            **kwargs: Keyword arguments for link construction.

        Returns:
            The constructed resource link URL.

        """
