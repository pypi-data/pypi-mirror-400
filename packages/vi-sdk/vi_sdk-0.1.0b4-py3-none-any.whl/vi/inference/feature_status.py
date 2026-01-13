#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   feature_status.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Feature status tracking for Vi SDK loaders and predictors.
"""

import os
from enum import Enum

from msgspec import Struct


class FeatureStatus(str, Enum):
    """Status of a loader or predictor feature."""

    STABLE = "stable"
    """Production-ready feature with full support."""

    EXPERIMENTAL = "experimental"
    """Feature is functional but API may change. Use with caution."""

    PREVIEW = "preview"
    """Feature in preview - limited availability, not for production."""

    COMING_SOON = "coming_soon"
    """Feature implemented but not yet available for use."""

    DEPRECATED = "deprecated"
    """Feature is deprecated and will be removed in a future version."""


class LoaderMetadata(Struct, kw_only=True):
    """Metadata for a loader registration.

    Attributes:
        module: Python module path containing the loader class.
        class_name: Name of the loader class.
        status: Current feature status (defaults to STABLE).
        message: Optional message to display when loader is accessed.
        available_from: Version when feature will become available/stable.
        deprecated_in: Version when feature was deprecated.
        removed_in: Version when deprecated feature will be removed.

    """

    module: str
    class_name: str
    status: FeatureStatus = FeatureStatus.STABLE
    message: str | None = None
    available_from: str | None = None
    deprecated_in: str | None = None
    removed_in: str | None = None


class PredictorMetadata(Struct, kw_only=True):
    """Metadata for a predictor registration.

    Attributes:
        module: Python module path containing the predictor class.
        class_name: Name of the predictor class.
        status: Current feature status (defaults to STABLE).
        message: Optional message to display when predictor is accessed.
        available_from: Version when feature will become available/stable.
        deprecated_in: Version when feature was deprecated.
        removed_in: Version when deprecated feature will be removed.

    """

    module: str
    class_name: str
    status: FeatureStatus = FeatureStatus.STABLE
    message: str | None = None
    available_from: str | None = None
    deprecated_in: str | None = None
    removed_in: str | None = None


def should_allow_unreleased_features() -> bool:
    r"""Check if unreleased features should be enabled.

    Checks the VI_ENABLE_UNRELEASED_FEATURES environment variable.
    This is useful for internal testing and development.

    Returns:
        True if unreleased features should be enabled, False otherwise.

    """
    return os.environ.get("VI_ENABLE_UNRELEASED_FEATURES", "0").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
