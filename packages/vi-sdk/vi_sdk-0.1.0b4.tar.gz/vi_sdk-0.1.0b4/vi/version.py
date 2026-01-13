#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   version.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK version module.
"""

import platform
import sys

__version__ = "0.1.0b4"
__version_info__ = (0, 1, 0, "beta", 4)

# Additional version metadata
__title__ = "vi"
__description__ = "Python SDK for Datature Vi"
__url__ = "https://github.com/datature/Vi-SDK"
__author__ = "Datature"
__author_email__ = "developers@datature.io"
__license__ = "Apache-2.0"

MIN_PYTHON_VERSION = (3, 10)


def get_user_agent() -> str:
    """Get user agent string for HTTP requests.

    Returns:
        User agent string including SDK version and system information.

    """
    python_version = platform.python_version()
    system_info = f"{platform.system()}/{platform.release()}"

    return f"vi/{__version__} (Python/{python_version}; {system_info})"


def check_python_version():
    """Check if current Python version is supported.

    Raises:
        RuntimeError: If Python version is below minimum requirement.

    """
    if sys.version_info < MIN_PYTHON_VERSION:
        min_version_str = ".".join(str(v) for v in MIN_PYTHON_VERSION)
        current_version_str = ".".join(str(v) for v in sys.version_info[:2])

        raise RuntimeError(
            f"Vi SDK requires Python {min_version_str} or higher. "
            f"You are using Python {current_version_str}. "
            f"Please upgrade your Python version."
        )


# Check Python version on import
check_python_version()
