#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK API responses module.
"""

import re
from enum import Enum
from typing import Generic, TypeVar

from msgspec import Struct, field

T = TypeVar("T")


class ViResponse(Struct, rename="camel", kw_only=True, omit_defaults=True):
    """Base class for all Vi API responses."""

    @staticmethod
    def _sanitize_dataset_id(dataset_id: str) -> str:
        """Sanitize dataset_id by stripping organization_id prefix if present.

        Dataset IDs from API responses are in format: {organization_id}_{dataset_id}
        This method extracts just the dataset_id part.

        Args:
            dataset_id: The dataset ID potentially containing organization ID prefix

        Returns:
            The sanitized dataset ID without organization ID prefix

        """
        if "_" in dataset_id:
            # Split on underscore and take the last part (dataset_id)
            return dataset_id.split("_")[-1]
        return dataset_id


class Pagination(ViResponse, Generic[T]):
    """Generic structure for paginated responses, providing navigation to other pages.

    Attributes:
        next_page: URL to the next page of results.
        prev_page: URL to the previous page of results.
        items: List of data items on the current page.

    """

    next_page: str | None = None
    prev_page: str | None = None
    items: list[T] = field(default_factory=list)


class Condition(Enum):
    """Condition response."""

    FINISHED = "Finished"
    STARTED = "Started"
    ALL = "All"

    @classmethod
    def _missing_(cls, value: str):
        """Create a new enum member for unknown values.

        Args:
            value: The string value to create an enum member for.

        Returns:
            A new Condition enum member with the value.

        """
        new_member = object.__new__(cls)
        new_member._name_ = cls._pascal_to_snake(value)
        new_member._value_ = value
        return new_member

    @staticmethod
    def _pascal_to_snake(name: str) -> str:
        """Convert PascalCase to snake_case.

        Args:
            name: The PascalCase string to convert.

        Returns:
            The converted snake_case string.

        """
        s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
        s2 = re.sub("([A-Z])([A-Z][a-z])", r"\1_\2", s1)
        return s2


class ConditionStatus(Enum):
    """Condition status response."""

    WAITING = "Waiting"
    REACHED = "Reached"
    FAILED_REACH = "FailedReach"


class ResourceCondition(ViResponse):
    """Resource condition response.

    Attributes:
        condition: The condition of the resource.
        status: The status of the condition.
        last_transition_time: The time the condition last transitioned.
        reason: The reason for the condition.
        message: The message of the condition.

    """

    condition: Condition
    status: ConditionStatus
    last_transition_time: int
    reason: str | None = None
    message: str | None = None


class ResourceMetadata(ViResponse):
    """Resource metadata response.

    Attributes:
        time_created: The time the resource was created.
        last_updated: The time the resource was last updated.
        generation: The generation of the resource.
        attributes: The attributes of the resource.

    """

    time_created: int
    last_updated: int
    generation: int
    attributes: dict[str, str]


class User(ViResponse):
    """User response.

    Attributes:
        workspace_role: The role of the user in the workspace.
        datasets: The datasets the user has access to.

    """

    workspace_role: str
    datasets: dict[str, str]

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset IDs.

        Removes organization ID prefixes from all dataset IDs in the datasets dict.
        """
        self.datasets = {
            self._sanitize_dataset_id(dataset): role
            for dataset, role in self.datasets.items()
        }


class DeletedResource(ViResponse):
    """Deleted resource response.

    Attributes:
        id: The ID of the deleted resource.
        deleted: Whether the resource was deleted.

    """

    id: str
    deleted: bool = True
