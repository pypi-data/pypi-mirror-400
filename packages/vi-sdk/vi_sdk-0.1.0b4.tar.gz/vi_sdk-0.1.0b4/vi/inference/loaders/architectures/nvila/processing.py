#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   processing.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA processing module.
"""

import re
from typing import cast

import numpy as np
from PIL.Image import Image
from transformers import image_transforms, image_utils
from transformers.feature_extraction_utils import BatchFeature
from transformers.image_utils import ImageInput
from transformers.models.qwen2 import Qwen2Tokenizer, Qwen2TokenizerFast
from transformers.models.siglip import SiglipImageProcessor, SiglipImageProcessorFast
from transformers.processing_utils import (
    ProcessingKwargs,
    ProcessorMixin,
    Unpack,
    VideosKwargs,
)
from transformers.tokenization_utils_base import BatchEncoding, TextInput
from transformers.video_utils import VideoInput, VideoMetadata, make_batched_videos


class NVILALiteProcessorKwargs(ProcessingKwargs, total=False):
    """Keyword arguments for NVILALite processor.

    This class defines the processing keyword arguments specific to NVILALite,
    extending the base ProcessingKwargs with NVILALite-specific options.

    Attributes:
        _defaults: Default values for processing arguments

    """

    _defaults = {}  # type: ignore


class NVILALiteProcessor(ProcessorMixin):
    """NVILALite processor for multimodal text, image, and video processing.

    This processor handles the preprocessing of multimodal inputs for NVILALite models.
    It combines a SigLIP image processor with a Qwen2 tokenizer to process text, images,
    and videos into a unified format suitable for the model.

    The processor supports:
    - Text processing with special media tokens
    - Image processing with dynamic tiling for variable aspect ratios
    - Video processing with frame sampling
    - Batch processing of mixed input types

    Attributes:
        attributes: List of processor component names
        image_processor_class: Class for image processing
        tokenizer_class: Class for tokenization
        _auto_class: Auto processor class
        image_processor: SigLIP image processor instance
        tokenizer: Qwen2 tokenizer instance
        image_token: Special token for images
        video_token: Special token for videos
        image_token_id: Token ID for image token
        video_token_id: Token ID for video token

    """

    attributes = [
        "image_processor",
        "tokenizer",
    ]
    image_processor_class: str = "AutoImageProcessor"
    tokenizer_class: str = "AutoTokenizer"
    _auto_class: str = "AutoProcessor"

    def __init__(
        self,
        image_processor: SiglipImageProcessor | SiglipImageProcessorFast,
        tokenizer: Qwen2Tokenizer | Qwen2TokenizerFast,
        chat_template: str | None = None,
        **kwargs,
    ):
        """Initialize the NVILALite processor.

        Args:
            image_processor: SigLIP image processor for vision processing
            tokenizer: Qwen2 tokenizer for text processing
            chat_template: Optional chat template for conversation formatting
            **kwargs: Additional arguments passed to parent class

        """
        super().__init__(
            image_processor,
            tokenizer,
            chat_template=chat_template,
            **kwargs,
        )

        self.image_processor: SiglipImageProcessor | SiglipImageProcessorFast
        self.tokenizer: Qwen2Tokenizer | Qwen2TokenizerFast

        self.image_token = (
            "<image>"
            if not hasattr(tokenizer, "image_token")
            else tokenizer.image_token
        )
        self.video_token = (
            "<vila/video>"
            if not hasattr(tokenizer, "video_token")
            else tokenizer.video_token
        )

        self.image_token_id = (
            tokenizer.image_token_id
            if getattr(tokenizer, "image_token_id", None)
            else tokenizer.convert_tokens_to_ids(self.image_token)
        )
        self.video_token_id = (
            tokenizer.video_token_id
            if getattr(tokenizer, "video_token_id", None)
            else tokenizer.convert_tokens_to_ids(self.video_token)
        )

    def __call__(
        self,
        *,
        text: TextInput | list[TextInput],
        images: ImageInput | None = None,
        videos: VideoInput | None = None,
        **kwargs: Unpack[NVILALiteProcessorKwargs],
    ) -> BatchFeature:
        """Process multimodal inputs into model-ready format.

        This method processes text, images, and videos into a unified BatchFeature
        that can be directly fed to the NVILALite model. It handles normalization,
        preprocessing, and tokenization of all input types.

        Args:
            text: Text input(s) to process
            images: Optional image input(s) to process
            videos: Optional video input(s) to process
            **kwargs: Additional processing arguments

        Returns:
            BatchFeature containing processed inputs ready for the model

        """
        normalized_text, normalized_images, normalized_videos = self._normalize_inputs(
            text=text,
            images=images,
            videos=videos,
        )

        images_inputs, image_token_padding_strategy = (
            self._preprocess_images(
                normalized_images,
                **kwargs,
            )
            if len(normalized_images) > 0
            else (BatchFeature(), [])
        )

        videos_inputs, video_token_padding_strategy = (
            self._preprocess_videos(
                normalized_videos,
                **kwargs,
            )
            if len(normalized_videos) > 0
            else (BatchFeature(), [])
        )

        text_inputs = self._preprocess_text(
            normalized_text,
            image_token_padding_strategy=image_token_padding_strategy,
            video_token_padding_strategy=video_token_padding_strategy,
            **kwargs,
        )

        return BatchFeature(
            {
                **text_inputs,
                **images_inputs,
                **videos_inputs,
            }
        )

    def batch_decode(self, *args, **kwargs) -> list[str]:
        """Decode token IDs back to text strings.

        Args:
            *args: Arguments passed to tokenizer batch_decode
            **kwargs: Keyword arguments passed to tokenizer batch_decode

        Returns:
            List of decoded text strings

        """
        return self.tokenizer.batch_decode(*args, **kwargs)

    def _normalize_inputs(
        self,
        *,
        text: TextInput | list[TextInput],
        images: ImageInput | None,
        videos: VideoInput | None,
    ) -> tuple[list[str], list[Image], list[list[Image]]]:
        """Normalize and standardize input formats.

        This method converts various input formats into standardized lists of
        strings, PIL Images, and video frames for consistent processing.

        Args:
            text: Text input(s) to normalize
            images: Image input(s) to normalize
            videos: Video input(s) to normalize

        Returns:
            Tuple of (normalized_text, normalized_images, normalized_videos)

        """
        if isinstance(text, list):
            normalized_text = text
        else:
            normalized_text = [text]

        if images is not None and images != []:
            image_flat_list = cast(list, image_utils.make_flat_list_of_images(images))
            normalized_images = [
                cast(Image, image_transforms.to_pil_image(image))
                for image in image_flat_list
            ]
        else:
            normalized_images = []

        if videos is not None and videos != []:
            video_list = cast(list[list], make_batched_videos(videos))
            normalized_videos = [
                [cast(Image, image_transforms.to_pil_image(image)) for image in video]
                for video in video_list
            ]
        else:
            normalized_videos = []

        return normalized_text, normalized_images, normalized_videos

    def _preprocess_images(
        self,
        images: list[Image],
        **kwargs: Unpack[NVILALiteProcessorKwargs],
    ) -> tuple[BatchFeature, list[list[int]]]:
        """Preprocess images for the model.

        This method handles image preprocessing including dynamic tiling for
        variable aspect ratios and conversion to RGB format. For single images,
        it applies dynamic preprocessing to create multiple tiles.

        Args:
            images: List of PIL Images to process
            **kwargs: Additional processing arguments

        Returns:
            Tuple of (processed_image_features, padding_strategy)

        Raises:
            AssertionError: If image processor size is not square for single image processing

        """
        merged_kwargs = self._merge_kwargs(
            NVILALiteProcessorKwargs,  # type: ignore
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )

        images = [image.convert("RGB") for image in images]

        if len(images) == 1:
            assert (
                self.image_processor.size["height"]
                == self.image_processor.size["width"]
            ), (
                f"Image processor size must be square for dynamic preprocessing. "
                f"Got height={self.image_processor.size['height']}, "
                f"width={self.image_processor.size['width']}"
            )

            image_tiles = dynamic_preprocess(
                images[0],
                min_num=1,
                max_num=12,
                image_size=self.image_processor.size["height"],
            )

            pixel_values = self.image_processor(
                image_tiles,
                **merged_kwargs["images_kwargs"],
            )["pixel_values"]

            images_inputs = BatchFeature(
                {
                    "pixel_values": pixel_values,
                }
            )

            padding_strategy = [[121] * len(image_tiles)]

        else:
            pixel_values = self.image_processor(
                images,
                **merged_kwargs["images_kwargs"],
            )["pixel_values"]

            images_inputs = BatchFeature(
                {
                    "pixel_values": pixel_values,
                }
            )

            padding_strategy = [[121]] * len(images)

        return images_inputs, padding_strategy

    def _preprocess_text(
        self,
        text: list[str],
        *,
        image_token_padding_strategy: list[list[int]],
        video_token_padding_strategy: list[list[int]],
        **kwargs: Unpack[NVILALiteProcessorKwargs],
    ) -> BatchEncoding:
        """Preprocess text with media token padding.

        This method processes text inputs and handles padding of media tokens
        (image and video tokens) based on the number of tiles/frames.
        It also handles special line feed token replacements for NVILA compatibility.

        Args:
            text: List of text strings to process
            image_token_padding_strategy: Padding strategy for image tokens
            video_token_padding_strategy: Padding strategy for video tokens
            **kwargs: Additional processing arguments

        Returns:
            BatchEncoding containing tokenized text with proper media token padding

        Raises:
            AssertionError: If media token counts don't match padding strategies

        """
        # Pad media tokens.
        assert isinstance(self.tokenizer.image_token, str), (
            f"Image token must be a string, got {type(self.tokenizer.image_token)}"
        )
        assert isinstance(self.tokenizer.video_token, str), (
            f"Video token must be a string, got {type(self.tokenizer.video_token)}"
        )

        for media_token, padding_strategy in (
            (self.tokenizer.image_token, image_token_padding_strategy),
            (self.tokenizer.video_token, video_token_padding_strategy),
        ):
            media_token_count = sum([s.count(media_token) for s in text])
            assert media_token_count == len(padding_strategy), (
                f"Mismatch between media token '{media_token}' count in text ({media_token_count}) "
                f"and padding strategy length ({len(padding_strategy)})"
            )

            # Pad to number of tiles.
            pad_lens = [len(x) for x in padding_strategy]
            text = [
                re.sub(
                    rf"({re.escape(media_token)})",
                    lambda _: media_token * pad_lens.pop(0),
                    s,
                )
                for s in text
            ]

            # HACK: NVILA mistakenly suffixes line feeds to some media tokens.
            if (
                len(image_token_padding_strategy) == 1
                and media_token == self.tokenizer.image_token
            ):
                image_token = self.tokenizer.image_token
                assert isinstance(image_token, str), (
                    f"Image token must be a string, got {type(image_token)}"
                )

                text = [
                    re.sub(rf"({re.escape(image_token)})", r"\1\n", s) for s in text
                ]

            # Pad to number of features.
            pad_lens = [y for x in padding_strategy for y in x]
            pad_lens = [x + 1 for x in pad_lens]  # Reserve for lf ending.
            text = [
                re.sub(
                    rf"({re.escape(media_token)})",
                    lambda _: media_token * pad_lens.pop(0),
                    s,
                )
                for s in text
            ]

        merged_kwargs = self._merge_kwargs(
            NVILALiteProcessorKwargs,  # type: ignore
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )

        text_inputs = self.tokenizer(
            text=text,
            **merged_kwargs["text_kwargs"],
        )

        # Replace last token id of every image tile with lf token id.
        lf_token_id = self.tokenizer.encode("\n")[0]
        assert isinstance(self.tokenizer.image_token_id, int), (
            f"Image token ID must be an integer, got {type(self.tokenizer.image_token_id)}"
        )
        assert isinstance(self.tokenizer.video_token_id, int), (
            f"Video token ID must be an integer, got {type(self.tokenizer.video_token_id)}"
        )

        input_ids = text_inputs.input_ids

        for media_token_id, padding_strategy in [
            (self.tokenizer.image_token_id, image_token_padding_strategy),
            (self.tokenizer.video_token_id, video_token_padding_strategy),
        ]:
            pad_lens = [y for x in padding_strategy for y in x]

            for i in range(len(input_ids)):
                j = 0
                while j < len(input_ids[i]):
                    if input_ids[i][j] != media_token_id:
                        j += 1
                        continue

                    j += pad_lens.pop(0)
                    input_ids[i][j] = lf_token_id

                    j += 1

        return text_inputs

    def _preprocess_videos(
        self,
        videos: list[list[Image]],
        **kwargs: Unpack[NVILALiteProcessorKwargs],
    ) -> tuple[BatchFeature, list[list[int]]]:
        """Preprocess videos for the model.

        This method handles video preprocessing including frame sampling and
        conversion to RGB format. It flattens all video frames for batch processing.

        Args:
            videos: List of video sequences (each video is a list of PIL Images)
            **kwargs: Additional processing arguments

        Returns:
            Tuple of (processed_video_features, padding_strategy)

        """
        merged_kwargs = self._merge_kwargs(
            NVILALiteProcessorKwargs,  # type: ignore
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )

        # Support sampling frames.
        if merged_kwargs["videos_kwargs"].get("do_sample_frames"):
            videos = [
                self._sample_frames(
                    video,
                    **merged_kwargs["videos_kwargs"],
                )
                for video in videos
            ]

        videos = [[image.convert("RGB") for image in video] for video in videos]

        frames = [image for video in videos for image in video]
        pixel_values_videos = self.image_processor(
            frames,
            **merged_kwargs["images_kwargs"],
        )["pixel_values"]

        videos_inputs = BatchFeature(
            {
                "pixel_values_videos": pixel_values_videos,
            }
        )

        padding_strategy = [[121] * len(video) for video in videos]

        return videos_inputs, padding_strategy

    def _sample_frames(
        self,
        video: list[Image],
        **kwargs: Unpack[VideosKwargs],
    ) -> list[Image]:
        """Sample frames from a video sequence.

        This method samples frames from a video based on either a fixed number
        of frames or a target FPS. It supports both uniform sampling and
        FPS-based sampling with video metadata.

        Args:
            video: List of video frames (PIL Images)
            **kwargs: Video processing arguments including fps, num_frames, video_metadata

        Returns:
            List of sampled video frames

        Raises:
            NotImplementedError: If neither fps nor num_frames is provided, or if video_metadata is invalid

        """
        fps = kwargs.get("fps")
        num_frames = kwargs.get("num_frames")

        if num_frames is not None and fps is None:
            indices = np.round(np.linspace(0, len(video) - 1, num_frames)).astype(int)

            return [video[i] for i in indices]

        elif num_frames is None and fps is not None:
            video_metadata = kwargs.get("video_metadata")

            if isinstance(video_metadata, VideoMetadata):
                total_num_frames = video_metadata.total_num_frames
                duration = video_metadata.duration

            elif isinstance(video_metadata, dict):
                total_num_frames = video_metadata.get("total_num_frames")
                duration = video_metadata.get("duration")

                assert total_num_frames is not None, (
                    "Video metadata must contain 'total_num_frames' when using fps-based sampling"
                )
                assert duration is not None, (
                    "Video metadata must contain 'duration' when using fps-based sampling"
                )

            else:
                raise NotImplementedError

            indices = np.round(
                np.linspace(0, total_num_frames - 1, int(fps * duration))
            ).astype(int)

            return [video[i] for i in indices]

        else:
            raise NotImplementedError


# NOTE: The following functions are directly copied from VILA codebase.
# https://github.com/NVlabs/VILA


def dynamic_preprocess(
    image: Image,
    min_num: int,
    max_num: int,
    image_size: int,
    use_thumbnail: bool = True,
) -> list[Image]:
    """Dynamically preprocess an image into multiple tiles.

    This function processes a single image into multiple tiles based on its
    aspect ratio. It finds the optimal tiling configuration and splits the
    image accordingly. Optionally adds a thumbnail version.

    Args:
        image: Input PIL Image to process
        min_num: Minimum number of tiles to create
        max_num: Maximum number of tiles to create
        image_size: Target size for each tile
        use_thumbnail: Whether to include a thumbnail version

    Returns:
        List of processed image tiles

    """
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = {
        (i, j)
        for n in range(min_num, max_num + 1)
        for i in range(1, n + 1)
        for j in range(1, n + 1)
        if i * j <= max_num and i * j >= min_num
    }
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size
    )

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size,
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks, (
        f"Number of processed image tiles ({len(processed_images)}) "
        f"must match expected blocks ({blocks})"
    )
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images


def find_closest_aspect_ratio(
    aspect_ratio: float,
    target_ratios: list[tuple[int, int]],
    width: int,
    height: int,
    image_size: int,
) -> tuple[int, int]:
    """Find the closest aspect ratio from target ratios.

    This function finds the target aspect ratio that best matches the input
    image's aspect ratio, considering both ratio similarity and area coverage.

    Args:
        aspect_ratio: Input image aspect ratio (width/height)
        target_ratios: List of valid (width, height) ratio tuples
        width: Input image width
        height: Input image height
        image_size: Target tile size

    Returns:
        Tuple of (target_width, target_height) for optimal tiling

    """
    best_ratio_diff = float("inf")
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio
