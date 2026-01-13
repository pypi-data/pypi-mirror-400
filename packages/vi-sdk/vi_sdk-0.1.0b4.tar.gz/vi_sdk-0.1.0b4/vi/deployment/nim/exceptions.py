#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   exceptions.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Custom exceptions for NIM deployment.
"""


class NIMDeploymentError(Exception):
    """Base exception for NIM deployment errors."""


class ContainerExistsError(NIMDeploymentError):
    """Raised when a container with the same name already exists."""

    def __init__(self, container_name: str):
        """Initialize exception.

        Args:
            container_name: Name of the existing container.

        """
        self.container_name = container_name
        super().__init__(f"Container '{container_name}' already exists")


class ServiceNotReadyError(NIMDeploymentError):
    """Raised when NIM service fails to become ready within timeout."""

    def __init__(self, container_name: str, timeout: int):
        """Initialize exception.

        Args:
            container_name: Name of the container.
            timeout: Timeout value that was exceeded.

        """
        self.container_name = container_name
        self.timeout = timeout
        super().__init__(
            f"NIM service in container '{container_name}' did not become ready within {timeout} seconds"
        )


class InvalidConfigError(NIMDeploymentError):
    """Raised when configuration is invalid."""


class ModelIncompatibilityError(NIMDeploymentError):
    """Raised when a custom model is incompatible with the target container."""

    def __init__(self, image_name: str, details: str | None = None):
        """Initialize exception.

        Args:
            image_name: Name of the container image.
            details: Optional details about the error.

        """
        self.image_name = image_name
        self.details = details
        message = f"Model incompatible with container '{image_name}'"
        if details:
            message = f"{message}: {details}"
        super().__init__(message)
