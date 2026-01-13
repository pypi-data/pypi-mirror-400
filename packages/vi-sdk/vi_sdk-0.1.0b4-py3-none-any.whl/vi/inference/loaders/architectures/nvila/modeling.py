#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   modeling.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA modeling module.
"""

import contextlib
import math

import einops
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from transformers import Qwen2ForCausalLM, SiglipVisionModel
from transformers.configuration_utils import PretrainedConfig
from transformers.generation.utils import GenerationMixin
from transformers.modeling_outputs import (
    BaseModelOutputWithPooling,
    CausalLMOutputWithPast,
)
from transformers.modeling_utils import PreTrainedModel

from .configuration import NVILALiteConfig

MM_HIDDEN_SIZE = 1152


@contextlib.contextmanager
def _temporary_torch_dtype(dtype: torch.dtype):
    """Context manager to temporarily set torch default dtype.

    Args:
        dtype: The dtype to set as default temporarily.

    Yields:
        None - control is yielded back to the caller.

    """
    original_dtype = torch.get_default_dtype()
    torch.set_default_dtype(dtype)
    try:
        yield
    finally:
        torch.set_default_dtype(original_dtype)


class NVILALiteMultiModalProjectorDownsampleBlock(nn.Module):
    """Downsampling block for multimodal projector.

    This block downsamples vision features by reshaping them into a 3x3 grid pattern
    and concatenating the features. It handles padding to ensure the sequence length
    is divisible by 3.

    The downsampling process:
    1. Reshapes input from (batch, seq_len, hidden) to (batch, sqrt(seq_len), sqrt(seq_len), hidden)
    2. Pads dimensions to make them divisible by 3
    3. Reshapes into 3x3 blocks and concatenates features
    4. Returns features with 9x the original hidden size
    """

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass through the downsampling block.

        Args:
            x: Input tensor of shape (batch_size, sequence_length, hidden_size)

        Returns:
            Downsampled features of shape (batch_size, new_sequence_length, 9 * hidden_size)

        """
        batch_size, sequence_length, hidden_size = x.shape

        feat_size = math.isqrt(sequence_length)

        features = x.reshape(batch_size, feat_size, feat_size, hidden_size)

        pad_after = (3 - feat_size % 3) % 3
        if pad_after > 0:
            features = F.pad(features, (0, 0, 0, pad_after, 0, pad_after))
            feat_size = feat_size + pad_after

        features = features.reshape(
            batch_size, feat_size // 3, 3, feat_size // 3, 3, hidden_size
        )
        features = features.permute(0, 1, 3, 2, 4, 5).contiguous()
        features = features.reshape(batch_size, -1, 9 * hidden_size)

        return features


class NVILALiteMultiModalProjector(nn.Module):
    """Multimodal projector for mapping vision features to text space.

    This module projects vision features from the vision tower to the text model's
    embedding space. It consists of a downsampling block followed by a series of
    linear layers with normalization and activation functions.

    The projection pipeline:
    1. Downsample vision features using NVILALiteMultiModalProjectorDownsampleBlock
    2. Apply layer normalization
    3. Project to intermediate dimension (MM_HIDDEN_SIZE * 3)
    4. Apply GELU activation and layer normalization
    5. Project to text hidden size
    6. Apply final GELU and linear projection
    """

    def __init__(self, config: NVILALiteConfig):
        """Initialize the multimodal projector.

        Args:
            config: NVILALite configuration containing text_config with hidden_size

        """
        super().__init__()

        self.layers = nn.Sequential(
            NVILALiteMultiModalProjectorDownsampleBlock(),
            nn.LayerNorm(MM_HIDDEN_SIZE * 9),
            nn.Linear(MM_HIDDEN_SIZE * 9, MM_HIDDEN_SIZE * 3),
            nn.GELU(),
            nn.LayerNorm(MM_HIDDEN_SIZE * 3),
            nn.Linear(MM_HIDDEN_SIZE * 3, config.text_config.hidden_size),
            nn.GELU(),
            nn.Linear(config.text_config.hidden_size, config.text_config.hidden_size),
        )

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass through the multimodal projector.

        Args:
            x: Input vision features tensor

        Returns:
            Projected features in text embedding space

        """
        return self.layers(x)


class NVILALiteForConditionalGeneration(PreTrainedModel, GenerationMixin):
    """NVILALite model for conditional generation with vision and language.

    This is the main model class that combines a vision tower (SigLIP) with a
    language model (Qwen2) for multimodal conditional generation tasks. The model
    can process both images and videos through the vision tower and generate text
    responses using the language model.

    The model architecture:
    - Vision Tower: SigLIP vision model for encoding visual inputs
    - Multimodal Projector: Maps vision features to text embedding space
    - Language Model: Qwen2 causal language model for text generation

    Attributes:
        config_class: Configuration class for the model
        base_model_prefix: Prefix for the base model
        _auto_class: Auto model class identifier
        _supports_flash_attn: Whether the model supports Flash Attention
        _supports_sdpa: Whether the model supports scaled dot-product attention
        supports_gradient_checkpointing: Whether gradient checkpointing is supported

    """

    config_class: type[PretrainedConfig] = NVILALiteConfig
    base_model_prefix: str = "llm"
    _auto_class: str = "AutoModel"
    _supports_flash_attn: bool = True
    _supports_sdpa: bool = True
    supports_gradient_checkpointing: bool = True

    def __init__(self, config: NVILALiteConfig):
        """Initialize the NVILALite model.

        Args:
            config: NVILALite configuration containing vision and text configs

        """
        super().__init__(config)

        self.config: NVILALiteConfig

        with _temporary_torch_dtype(config.dtype):
            self.vision_tower = SiglipVisionModel(config.vision_config)
            self.mm_projector = NVILALiteMultiModalProjector(config)
            self.llm = Qwen2ForCausalLM(config.text_config)

        self.post_init()

    def forward(
        self,
        *,
        input_ids: Tensor | None = None,
        inputs_embeds: Tensor | None = None,
        pixel_values: Tensor | None = None,
        pixel_values_videos: Tensor | None = None,
        **kwargs,
    ) -> CausalLMOutputWithPast:
        """Forward pass for conditional generation.

        Args:
            input_ids: Token IDs for text input. Exactly one of input_ids or inputs_embeds must be provided.
            inputs_embeds: Pre-computed input embeddings. Exactly one of input_ids or inputs_embeds must be provided.
            pixel_values: Image pixel values for vision processing
            pixel_values_videos: Video pixel values for vision processing
            **kwargs: Additional arguments passed to the language model

        Returns:
            CausalLMOutputWithPast containing logits and past key values

        Raises:
            AssertionError: If both input_ids and inputs_embeds are provided or neither is provided

        """
        assert (input_ids is None) != (inputs_embeds is None), (
            "Exactly one of `input_ids` or `inputs_embeds` must be specified."
        )

        if input_ids is not None and torch.any(
            torch.isin(
                input_ids,
                torch.tensor(
                    [self.config.image_token_id, self.config.video_token_id],
                    device=input_ids.device,
                ),
            ).any()
        ):  # Prefill
            inputs_embeds = self._embed(
                input_ids=input_ids,
                pixel_values=pixel_values,
                pixel_values_videos=pixel_values_videos,
            )
            input_ids = None

        outputs = self.llm(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            **kwargs,
        )

        return outputs

    def _embed(
        self,
        *,
        input_ids: Tensor,
        pixel_values: Tensor | None,
        pixel_values_videos: Tensor | None,
    ) -> Tensor:
        """Embed input tokens and replace media tokens with vision features.

        This method processes the input tokens and replaces special media tokens
        (image_token_id, video_token_id) with corresponding vision features
        extracted from the vision tower.

        Args:
            input_ids: Token IDs containing media tokens to be replaced
            pixel_values: Image pixel values for processing
            pixel_values_videos: Video pixel values for processing

        Returns:
            Input embeddings with vision features replacing media tokens

        """
        inputs_embeds: Tensor = self.llm.model.embed_tokens(input_ids)

        for pixel_values, media_token_id in [
            (pixel_values, self.config.image_token_id),
            (pixel_values_videos, self.config.video_token_id),
        ]:
            if pixel_values is None:
                continue

            vision_features = self._encode_vision(pixel_values)
            vision_features = einops.rearrange(vision_features, "n p d -> (n p) d")

            inputs_embeds[input_ids == media_token_id] = vision_features

        return inputs_embeds

    def _encode_vision(self, pixel_values: Tensor) -> Tensor:
        """Encode vision inputs using the vision tower and projector.

        This method processes pixel values through the vision tower (SigLIP) and
        projects the resulting features to the text embedding space using the
        multimodal projector.

        Args:
            pixel_values: Input pixel values for vision processing

        Returns:
            Projected vision features in text embedding space

        Raises:
            AssertionError: If vision tower output does not contain hidden states

        """
        vision_tower_output: BaseModelOutputWithPooling = self.vision_tower(
            pixel_values,
            output_hidden_states=True,
        )
        assert vision_tower_output.hidden_states is not None, (
            "Vision tower output must contain hidden states when output_hidden_states=True"
        )

        vision_features = vision_tower_output.hidden_states[-2]

        vision_features = self.mm_projector(vision_features)

        return vision_features
