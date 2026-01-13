#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   messages.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference messages module.
"""

from typing import Literal

import msgspec
from msgspec import Struct


class TextContent(Struct, kw_only=True):
    """Text content in a message."""

    text: str
    type: Literal["text"] = "text"


class ImageContent(Struct, kw_only=True):
    """Image content in a message (for local model inference)."""

    image: str
    type: Literal["image"] = "image"


class ImageURLContent(Struct, kw_only=True):
    """Image URL content in a message (for API-based inference)."""

    image_url: dict[str, str]
    type: Literal["image_url"] = "image_url"


class ChatMessage(Struct, kw_only=True):
    """A single message in a chat conversation.

    The content field can be either:
    - A string (for system/assistant messages)
    - A list of content objects (for user messages with multimodal content)
    """

    role: Literal["system", "user", "assistant"]
    content: str | list[TextContent | ImageContent | ImageURLContent]


def create_system_message(text: str) -> dict:
    """Create a system message with text content.

    Args:
        text: The system prompt text.

    Returns:
        Dictionary representing a system message with string content.

    """
    message = ChatMessage(role="system", content=text)
    return msgspec.to_builtins(message)


def create_user_message_with_image(image_path: str, text: str) -> dict:
    """Create a user message with image and text content.

    Args:
        image_path: Path to the image file.
        text: The user prompt text.

    Returns:
        Dictionary representing a user message with image and text content.

    """
    message = ChatMessage(
        role="user",
        content=[
            ImageContent(image=image_path),
            TextContent(text=text),
        ],
    )
    return msgspec.to_builtins(message)


def create_user_message_with_image_url(image_url: str, text: str) -> dict:
    """Create a user message with image URL and text content.

    Useful for API-based services that accept base64-encoded images or URLs.

    Args:
        image_url: URL or data URI of the image (e.g., "data:image/jpeg;base64,...").
        text: The user prompt text.

    Returns:
        Dictionary representing a user message with image URL and text content.

    """
    message = ChatMessage(
        role="user",
        content=[
            ImageURLContent(image_url={"url": image_url}),
            TextContent(text=text),
        ],
    )
    return msgspec.to_builtins(message)
