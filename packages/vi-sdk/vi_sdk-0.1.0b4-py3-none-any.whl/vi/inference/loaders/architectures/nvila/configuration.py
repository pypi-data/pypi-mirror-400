#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   configuration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA configuration module.
"""

from typing import Any

from transformers.configuration_utils import PretrainedConfig
from transformers.models.qwen2 import Qwen2Config
from transformers.models.siglip import SiglipVisionConfig


class NVILALiteConfig(PretrainedConfig):
    """Configuration class for NVILA Lite model.

    This configuration class defines the architecture and parameters for the NVILA Lite
    multimodal model, which combines text and vision capabilities using Qwen2 for text
    processing and SigLIP for vision processing.

    Attributes:
        model_type: The type of model, set to "nvila".
        sub_configs: Dictionary mapping sub-configuration names to their respective
            configuration classes.
        _auto_class: The auto configuration class name.
        text_config: Configuration for the text processing component (Qwen2).
        vision_config: Configuration for the vision processing component (SigLIP).
        image_token_id: Token ID used for image tokens in the model.
        video_token_id: Token ID used for video tokens in the model.

    """

    model_type: str = "nvila"
    sub_configs: dict[str, type[PretrainedConfig]] = {
        "text_config": Qwen2Config,
        "vision_config": SiglipVisionConfig,
    }
    _auto_class: str = "AutoConfig"

    def __init__(
        self,
        *,
        text_config: dict[str, Any] | None = None,
        vision_config: dict[str, Any] | None = None,
        image_token_id: int | None = None,
        video_token_id: int | None = None,
        **kwargs,
    ):
        """Initialize NVILA Lite configuration.

        Args:
            text_config: Optional dictionary containing configuration parameters for
                the text processing component (Qwen2). If None, default Qwen2Config
                will be used.
            vision_config: Optional dictionary containing configuration parameters for
                the vision processing component (SigLIP). If None, default
                SiglipVisionConfig will be used.
            image_token_id: Token ID for image tokens. If None, defaults to -1.
            video_token_id: Token ID for video tokens. If None, defaults to -1.
            **kwargs: Additional keyword arguments passed to the parent class.

        """
        self.text_config = (
            Qwen2Config(**text_config) if text_config is not None else Qwen2Config()
        )
        self.vision_config = (
            SiglipVisionConfig(**vision_config)
            if vision_config is not None
            else SiglipVisionConfig()
        )

        self.image_token_id = image_token_id if image_token_id is not None else -1
        self.video_token_id = video_token_id if video_token_id is not None else -1

        super().__init__(**kwargs)
