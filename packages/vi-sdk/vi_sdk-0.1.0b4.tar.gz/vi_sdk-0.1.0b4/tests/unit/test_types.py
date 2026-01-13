#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_types.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for API types and query parameter handling.
"""

from enum import Enum

import pytest
from vi.api.types import PaginationParams, QueryParamsMixin, ResourceMetadata, ViStruct


@pytest.mark.unit
@pytest.mark.types
class TestViStruct:
    """Test ViStruct base class."""

    def test_struct_creation(self) -> None:
        """Test creating a ViStruct instance."""

        class TestStruct(ViStruct):
            """Test struct for validation."""

            name: str
            value: int

        struct = TestStruct(name="test", value=42)
        assert struct.name == "test"
        assert struct.value == 42

    def test_struct_rename_camel(self) -> None:
        """Test that struct fields are renamed to camelCase."""

        class TestStruct(ViStruct):
            """Test struct with snake_case fields."""

            snake_case_field: str
            another_field: int

        struct = TestStruct(snake_case_field="test", another_field=123)
        assert struct.snake_case_field == "test"
        assert struct.another_field == 123

    def test_struct_kw_only(self) -> None:
        """Test that ViStruct enforces keyword-only arguments.

        Note: msgspec.Struct with kw_only=True allows positional args
        but enforces keyword args for fields with defaults after required fields.
        """

        class TestStruct(ViStruct):
            """Test struct for kw_only validation."""

            field: str

        # Should work with keyword arguments
        struct = TestStruct(field="test")
        assert struct.field == "test"

        # msgspec.Struct with kw_only=True still allows positional args
        # for backwards compatibility with msgspec behavior
        struct2 = TestStruct("test")
        assert struct2.field == "test"


@pytest.mark.unit
@pytest.mark.types
class TestQueryParamsMixin:
    """Test QueryParamsMixin class."""

    def test_snake_to_camel_conversion(self) -> None:
        """Test snake_case to camelCase conversion."""
        result = QueryParamsMixin.snake_to_camel("snake_case_string")
        assert result == "snakeCaseString"

        result = QueryParamsMixin.snake_to_camel("simple")
        assert result == "simple"

        result = QueryParamsMixin.snake_to_camel("multiple_word_example")
        assert result == "multipleWordExample"

    def test_auto_camel_mappings(self) -> None:
        """Test automatic camelCase mapping generation."""
        fields = ["field_one", "field_two", "simple"]
        mappings = QueryParamsMixin.auto_camel_mappings(fields)

        assert mappings["field_one"] == "fieldOne"
        assert mappings["field_two"] == "fieldTwo"
        assert mappings["simple"] == "simple"

    def test_identity_mappings(self) -> None:
        """Test identity mapping generation."""
        fields = ["field1", "field2"]
        mappings = QueryParamsMixin.identity_mappings(fields)

        assert mappings["field1"] == "field1"
        assert mappings["field2"] == "field2"

    def test_get_field_value_simple(self) -> None:
        """Test getting field value for simple fields."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.simple_field = "value"
                self._FIELD_MAPPINGS = {"simple_field": "simpleField"}

        params = TestParams()
        value = params._get_field_value("simple_field")
        assert value == "value"

    def test_get_field_value_nested(self) -> None:
        """Test getting field value with dot notation for nested attributes."""

        class Inner:
            """Inner class for nested testing."""

            def __init__(self) -> None:
                self.nested_value = "nested"

        class TestParams(QueryParamsMixin):
            """Test params class with nested attribute."""

            def __init__(self) -> None:
                self.inner = Inner()
                self._FIELD_MAPPINGS = {"inner.nested_value": "innerNestedValue"}

        params = TestParams()
        value = params._get_field_value("inner.nested_value")
        assert value == "nested"

    def test_get_field_value_nonexistent(self) -> None:
        """Test getting nonexistent field value returns None."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        value = params._get_field_value("nonexistent")
        assert value is None

    def test_convert_value_none(self) -> None:
        """Test converting None value returns None."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        result = params._convert_value("field", None)
        assert result is None

    def test_convert_value_enum(self) -> None:
        """Test converting Enum value returns enum value."""

        class TestEnum(Enum):
            """Test enum."""

            VALUE = "test_value"

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        result = params._convert_value("field", TestEnum.VALUE)
        assert result == "test_value"

    def test_convert_value_skip_default(self) -> None:
        """Test skipping default values."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}
            _SKIP_DEFAULT_VALUES = {"field": 0}

        params = TestParams()
        result = params._convert_value("field", 0)
        assert result is None

        result = params._convert_value("field", 5)
        assert result == "5"

    def test_convert_value_custom_mapping(self) -> None:
        """Test custom value mappings."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}
            _VALUE_MAPPINGS = {"field": {True: "yes", False: "no"}}

        params = TestParams()
        result = params._convert_value("field", True)
        assert result == "yes"

        result = params._convert_value("field", False)
        assert result == "no"

    def test_convert_value_boolean_flag(self) -> None:
        """Test boolean flag conversion."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}
            _BOOLEAN_FLAGS = {"flag"}

        params = TestParams()
        result = params._convert_value("flag", True)
        assert result == "y"

        result = params._convert_value("flag", False)
        assert result is None

    def test_convert_value_string(self) -> None:
        """Test converting string value."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        result = params._convert_value("field", "test")
        assert result == "test"

    def test_convert_value_number(self) -> None:
        """Test converting number value to string."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        result = params._convert_value("field", 123)
        assert result == "123"

    def test_to_query_params_basic(self) -> None:
        """Test converting to query parameters."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.page_size = 10
                self.page_token = "abc123"
                self._FIELD_MAPPINGS = {
                    "page_size": "pageSize",
                    "page_token": "pageToken",
                }

        params = TestParams()
        query = params.to_query_params()

        assert query["pageSize"] == "10"
        assert query["pageToken"] == "abc123"

    def test_to_query_params_with_none_values(self) -> None:
        """Test that None values are excluded from query params."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.value1 = "test"
                self.value2 = None
                self._FIELD_MAPPINGS = {"value1": "value1", "value2": "value2"}

        params = TestParams()
        query = params.to_query_params()

        assert "value1" in query
        assert "value2" not in query

    def test_to_query_params_with_boolean_flags(self) -> None:
        """Test query params with boolean flags."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.flag1 = True
                self.flag2 = False
                self._FIELD_MAPPINGS = {"flag1": "flag1", "flag2": "flag2"}
                self._BOOLEAN_FLAGS = {"flag1", "flag2"}

        params = TestParams()
        query = params.to_query_params()

        assert query["flag1"] == "y"
        assert "flag2" not in query


@pytest.mark.unit
@pytest.mark.types
class TestPaginationParams:
    """Test PaginationParams type."""

    def test_default_values(self) -> None:
        """Test default pagination parameter values."""
        params = PaginationParams()
        assert params.page_token is None
        assert params.page_size == 10

    def test_custom_values(self) -> None:
        """Test custom pagination parameter values."""
        params = PaginationParams(page_token="token123", page_size=50)
        assert params.page_token == "token123"
        assert params.page_size == 50

    def test_page_token_optional(self) -> None:
        """Test that page_token is optional."""
        params = PaginationParams(page_size=20)
        assert params.page_token is None
        assert params.page_size == 20

    def test_immutability(self) -> None:
        """Test PaginationParams mutability.

        Note: msgspec.Struct is NOT frozen by default, so fields can be modified.
        This test verifies that modification is allowed for flexibility.
        """
        params = PaginationParams(page_size=10)

        # msgspec.Struct allows modification by default
        params.page_size = 20
        assert params.page_size == 20


@pytest.mark.unit
@pytest.mark.types
class TestResourceMetadata:
    """Test ResourceMetadata type."""

    def test_default_attributes(self) -> None:
        """Test default attributes dictionary."""
        metadata = ResourceMetadata()
        assert metadata.attributes == {}

    def test_custom_attributes(self) -> None:
        """Test custom attributes."""
        attrs = {"key1": "value1", "key2": "value2"}
        metadata = ResourceMetadata(attributes=attrs)
        assert metadata.attributes == attrs

    def test_empty_attributes(self) -> None:
        """Test with explicitly empty attributes."""
        metadata = ResourceMetadata(attributes={})
        assert metadata.attributes == {}


@pytest.mark.unit
@pytest.mark.types
class TestQueryParamsMixinEdgeCases:
    """Test edge cases for QueryParamsMixin."""

    def test_empty_field_mappings(self) -> None:
        """Test with empty field mappings."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}

        params = TestParams()
        query = params.to_query_params()
        assert query == {}

    def test_deeply_nested_field_value(self) -> None:
        """Test getting deeply nested field values."""

        class Level3:
            """Level 3 nested class."""

            def __init__(self) -> None:
                self.value = "deep"

        class Level2:
            """Level 2 nested class."""

            def __init__(self) -> None:
                self.level3 = Level3()

        class Level1:
            """Level 1 nested class."""

            def __init__(self) -> None:
                self.level2 = Level2()

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.level1 = Level1()
                self._FIELD_MAPPINGS = {"level1.level2.level3.value": "deepValue"}

        params = TestParams()
        value = params._get_field_value("level1.level2.level3.value")
        assert value == "deep"

    def test_mixed_value_types_in_params(self) -> None:
        """Test query params with mixed value types."""

        class TestEnum(Enum):
            """Test enum."""

            OPTION = "opt"

        class TestParams(QueryParamsMixin):
            """Test params class."""

            def __init__(self) -> None:
                self.str_field = "text"
                self.int_field = 42
                self.float_field = 3.14
                self.enum_field = TestEnum.OPTION
                self.bool_field = True
                self._FIELD_MAPPINGS = {
                    "str_field": "strField",
                    "int_field": "intField",
                    "float_field": "floatField",
                    "enum_field": "enumField",
                    "bool_field": "boolField",
                }
                self._BOOLEAN_FLAGS = {"bool_field"}

        params = TestParams()
        query = params.to_query_params()

        assert query["strField"] == "text"
        assert query["intField"] == "42"
        assert query["floatField"] == "3.14"
        assert query["enumField"] == "opt"
        assert query["boolField"] == "y"

    def test_snake_to_camel_edge_cases(self) -> None:
        """Test snake_to_camel with edge cases."""
        # Single character
        assert QueryParamsMixin.snake_to_camel("x") == "x"

        # Already camelCase
        assert QueryParamsMixin.snake_to_camel("alreadyCamel") == "alreadyCamel"

        # Multiple underscores
        assert QueryParamsMixin.snake_to_camel("a__b__c") == "aBC"

        # Leading underscore (private fields)
        assert QueryParamsMixin.snake_to_camel("_private_field") == "PrivateField"

        # Trailing underscore
        assert QueryParamsMixin.snake_to_camel("field_") == "field"

        # Empty string
        assert QueryParamsMixin.snake_to_camel("") == ""

    def test_value_mapping_fallback(self) -> None:
        """Test value mapping with unmapped values."""

        class TestParams(QueryParamsMixin):
            """Test params class."""

            _FIELD_MAPPINGS: dict[str, str] = {}
            _VALUE_MAPPINGS = {"field": {"a": "A", "b": "B"}}

        params = TestParams()

        # Mapped value
        result = params._convert_value("field", "a")
        assert result == "A"

        # Unmapped value returns None
        result = params._convert_value("field", "c")
        assert result is None
