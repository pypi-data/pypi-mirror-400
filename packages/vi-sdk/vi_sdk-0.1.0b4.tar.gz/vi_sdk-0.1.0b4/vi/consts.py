#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   consts.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK constants module.
"""

from pathlib import Path

# Default directories for various SDK operations
DEFAULT_BASE_DIR = Path.home() / ".datature" / "vi"
DEFAULT_DATASET_EXPORT_DIR = DEFAULT_BASE_DIR / "datasets"
DEFAULT_ANNOTATION_EXPORT_DIR = DEFAULT_BASE_DIR / "annotations"
DEFAULT_ASSET_DIR = DEFAULT_BASE_DIR / "assets"
DEFAULT_MODEL_DIR = DEFAULT_BASE_DIR / "models"
DEFAULT_LOG_DIR = DEFAULT_BASE_DIR / "logs"

# Model directory structure constants
DEFAULT_ADAPTER_DIR_NAME = "model_adapter"
DEFAULT_MODEL_DIR_NAME = "model_full"
DEFAULT_RUN_CONFIG_FILE_NAME = "run.json"
