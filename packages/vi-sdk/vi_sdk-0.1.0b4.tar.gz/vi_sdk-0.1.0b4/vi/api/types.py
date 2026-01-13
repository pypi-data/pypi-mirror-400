#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK API types module.
"""

from enum import Enum
from typing import Any

from msgspec import Struct, field


class ViStruct(Struct, rename="camel", kw_only=True):
    """Base class for all Vi API structs."""


class QueryParamsMixin:
    """Mixin class for converting structs to URL query parameters."""

    # Override these in subclasses
    _FIELD_MAPPINGS: dict[str, str] = {}
    _BOOLEAN_FLAGS: set[str] = set()
    _SKIP_DEFAULT_VALUES: dict[str, Any] = {}
    _VALUE_MAPPINGS: dict[str, dict[Any, str]] = {}

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """Convert snake_case to camelCase like msgspec does.

        Args:
            snake_str: The snake_case string to convert.

        Returns:
            The converted camelCase string.

        """
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    @classmethod
    def auto_camel_mappings(cls, fields: list[str]) -> dict[str, str]:
        """Generate automatic camelCase mappings for snake_case field names.

        Args:
            fields: List of snake_case field names to generate mappings for.

        Returns:
            Dictionary mapping snake_case field names to camelCase.

        """
        return {field: cls.snake_to_camel(field) for field in fields}

    @staticmethod
    def identity_mappings(fields: list[str]) -> dict[str, str]:
        """Generate identity mappings for fields that don't change names.

        Args:
            fields: List of field names to generate identity mappings for.

        Returns:
            Dictionary mapping each field name to itself.

        """
        return {field: field for field in fields}

    def _get_field_value(self, field_name: str) -> Any:
        """Get the value of a field, handling nested attributes.

        Args:
            field_name: The field name, can use dot notation for nested attributes.

        Returns:
            The field value, or None if the field doesn't exist.

        """
        obj = self
        for part in field_name.split("."):
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return None
        return obj

    def _convert_value(self, field_name: str, value: Any) -> str | None:
        """Convert a field value to its query parameter representation.

        Args:
            field_name: The name of the field being converted.
            value: The value to convert.

        Returns:
            The string representation for query parameters, or None to skip.

        """
        if value is None:
            return None

        if isinstance(value, Enum):
            return value.value

        # Skip default values if configured
        if field_name in self._SKIP_DEFAULT_VALUES:
            if value == self._SKIP_DEFAULT_VALUES[field_name]:
                return None

        # Use custom value mappings if configured
        if field_name in self._VALUE_MAPPINGS:
            return self._VALUE_MAPPINGS[field_name].get(value)

        if field_name in self._BOOLEAN_FLAGS:
            # Boolean flags only set parameter if True
            return "y" if value else None

        # Regular fields - convert to string
        return str(value) if not isinstance(value, str) else value

    def to_query_params(self) -> dict[str, str]:
        """Convert mapped fields to URL query parameters.

        Returns:
            Dictionary of query parameter names to values.

        """
        params = {}

        for field_name, param_name in self._FIELD_MAPPINGS.items():
            value = self._get_field_value(field_name)
            converted_value = self._convert_value(field_name, value)

            if converted_value is not None:
                params[param_name] = converted_value

        return params


class PaginationParams(ViStruct):
    """Pagination params struct."""

    page_token: str | None = None
    page_size: int = 10


class ResourceMetadata(ViStruct):
    """Resource metadata struct."""

    attributes: dict[str, str] = field(default_factory=dict)
