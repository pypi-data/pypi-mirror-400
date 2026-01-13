#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_validation.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for validation utilities.
"""

from pathlib import Path

import pytest
from vi.client.errors import (
    ViFileTooLargeError,
    ViInvalidFileFormatError,
    ViInvalidParameterError,
)
from vi.client.validation import (
    validate_directory_path,
    validate_email,
    validate_file_path,
    validate_id_param,
    validate_list_param,
    validate_numeric_param,
    validate_pagination_params,
    validate_required_param,
    validate_sort_params,
    validate_string_param,
    validate_url,
)


def _validate_item_is_int(item):
    """Validate that an item is an integer."""
    if not isinstance(item, int):
        raise ValueError("Must be integer")


@pytest.mark.unit
@pytest.mark.validation
class TestValidateRequiredParam:
    """Test validate_required_param function."""

    def test_valid_string(self):
        """Test with valid string parameter."""
        validate_required_param("test_value", "param_name")  # Should not raise

    def test_valid_number(self):
        """Test with valid number parameter."""
        validate_required_param(123, "param_name")  # Should not raise

    def test_valid_object(self):
        """Test with valid object parameter."""
        validate_required_param({"key": "value"}, "param_name")  # Should not raise

    def test_none_value(self):
        """Test that None value raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_required_param(None, "param_name")
        assert "param_name" in str(exc_info.value)
        assert "None" in str(exc_info.value)

    def test_empty_string(self):
        """Test that empty string raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_required_param("", "param_name")
        assert "cannot be empty" in str(exc_info.value)

    def test_whitespace_string(self):
        """Test that whitespace-only string raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_required_param("   ", "param_name")
        assert "cannot be empty" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateStringParam:
    """Test validate_string_param function."""

    def test_valid_string(self):
        """Test with valid string."""
        validate_string_param("test", "param")  # Should not raise

    def test_min_length_valid(self):
        """Test minimum length constraint - valid."""
        validate_string_param("hello", "param", min_length=3)  # Should not raise

    def test_min_length_invalid(self):
        """Test minimum length constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_string_param("hi", "param", min_length=3)
        assert "at least 3 characters" in str(exc_info.value)

    def test_max_length_valid(self):
        """Test maximum length constraint - valid."""
        validate_string_param("hello", "param", max_length=10)  # Should not raise

    def test_max_length_invalid(self):
        """Test maximum length constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_string_param("hello world", "param", max_length=5)
        assert "at most 5 characters" in str(exc_info.value)

    def test_pattern_valid(self):
        """Test pattern constraint - valid."""
        validate_string_param(
            "abc123", "param", pattern=r"^[a-z0-9]+$"
        )  # Should not raise

    def test_pattern_invalid(self):
        """Test pattern constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_string_param("abc-123", "param", pattern=r"^[a-z0-9]+$")
        assert "does not match" in str(exc_info.value)

    def test_not_string_type(self):
        """Test that non-string type raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_string_param(123, "param")
        assert "must be a string" in str(exc_info.value)

    def test_optional_none(self):
        """Test optional parameter with None value."""
        validate_string_param(None, "param", required=False)  # Should not raise

    def test_required_none(self):
        """Test required parameter with None value."""
        with pytest.raises(ViInvalidParameterError):
            validate_string_param(None, "param", required=True)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateIdParam:
    """Test validate_id_param function."""

    def test_valid_id(self):
        """Test with valid ID."""
        validate_id_param("dataset_123", "dataset_id")  # Should not raise

    def test_id_with_hyphens(self):
        """Test ID with hyphens."""
        validate_id_param("dataset-123-abc", "dataset_id")  # Should not raise

    def test_id_with_underscores(self):
        """Test ID with underscores."""
        validate_id_param("dataset_123_abc", "dataset_id")  # Should not raise

    def test_id_alphanumeric_only(self):
        """Test ID with alphanumeric characters."""
        validate_id_param("dataset123ABC", "dataset_id")  # Should not raise

    def test_empty_id(self):
        """Test empty ID."""
        with pytest.raises(ViInvalidParameterError):
            validate_id_param("", "dataset_id")

    def test_id_with_special_chars(self):
        """Test ID with invalid special characters."""
        with pytest.raises(ViInvalidParameterError):
            validate_id_param("dataset@123", "dataset_id")

    def test_id_with_spaces(self):
        """Test ID with spaces."""
        with pytest.raises(ViInvalidParameterError):
            validate_id_param("dataset 123", "dataset_id")

    def test_too_long_id(self):
        """Test ID exceeding maximum length."""
        long_id = "a" * 300
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_id_param(long_id, "dataset_id")
        assert "at most 255 characters" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateFilePath:
    """Test validate_file_path function."""

    def test_existing_file(self, test_image_file):
        """Test with existing file."""
        result = validate_file_path(test_image_file, must_exist=True)
        assert result == test_image_file

    def test_nonexistent_file_must_exist(self, tmp_path):
        """Test that nonexistent file raises error when must_exist=True."""
        nonexistent = tmp_path / "nonexistent.txt"
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_file_path(nonexistent, must_exist=True)
        assert "does not exist" in str(exc_info.value)

    def test_nonexistent_file_optional(self, tmp_path):
        """Test nonexistent file when must_exist=False."""
        nonexistent = tmp_path / "nonexistent.txt"
        result = validate_file_path(nonexistent, must_exist=False)
        assert result == nonexistent

    def test_directory_instead_of_file(self, tmp_path):
        """Test that directory raises error when must_be_file=True."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_file_path(tmp_path, must_be_file=True)
        assert "must be a file, not a directory" in str(exc_info.value)

    def test_allowed_extensions_valid(self, test_image_file):
        """Test allowed extensions - valid."""
        result = validate_file_path(
            test_image_file, allowed_extensions=[".png", ".jpg"]
        )
        assert result == test_image_file

    def test_allowed_extensions_invalid(self, test_image_file):
        """Test allowed extensions - invalid."""
        with pytest.raises(ViInvalidFileFormatError) as exc_info:
            validate_file_path(test_image_file, allowed_extensions=[".jpg", ".jpeg"])
        assert ".png" in str(exc_info.value)

    def test_max_size_valid(self, test_image_file):
        """Test max size constraint - valid."""
        result = validate_file_path(test_image_file, max_size_bytes=1024 * 1024)  # 1MB
        assert result == test_image_file

    def test_max_size_invalid(self, test_large_file):
        """Test max size constraint - invalid."""
        with pytest.raises(ViFileTooLargeError) as exc_info:
            validate_file_path(test_large_file, max_size_bytes=1024)  # 1KB limit
        assert "exceeds maximum" in str(exc_info.value)

    def test_string_path_conversion(self, test_image_file):
        """Test that string path is converted to Path."""
        result = validate_file_path(str(test_image_file))
        assert isinstance(result, Path)
        assert result == test_image_file


@pytest.mark.unit
@pytest.mark.validation
class TestValidateDirectoryPath:
    """Test validate_directory_path function."""

    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        result = validate_directory_path(tmp_path, must_exist=True)
        assert result == tmp_path

    def test_nonexistent_directory_must_exist(self, tmp_path):
        """Test nonexistent directory with must_exist=True."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_directory_path(
                nonexistent, must_exist=True, create_if_missing=False
            )
        assert "does not exist" in str(exc_info.value)

    def test_nonexistent_directory_create(self, tmp_path):
        """Test creating nonexistent directory."""
        new_dir = tmp_path / "new_directory"
        result = validate_directory_path(new_dir, create_if_missing=True)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_file_instead_of_directory(self, test_image_file):
        """Test that file raises error when directory expected."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_directory_path(test_image_file)
        assert "must be a directory, not a file" in str(exc_info.value)

    def test_string_path_conversion(self, tmp_path):
        """Test that string path is converted to Path."""
        result = validate_directory_path(str(tmp_path))
        assert isinstance(result, Path)
        assert result == tmp_path


@pytest.mark.unit
@pytest.mark.validation
class TestValidateNumericParam:
    """Test validate_numeric_param function."""

    def test_valid_integer(self):
        """Test with valid integer."""
        validate_numeric_param(10, "param")  # Should not raise

    def test_valid_float(self):
        """Test with valid float."""
        validate_numeric_param(10.5, "param")  # Should not raise

    def test_min_value_valid(self):
        """Test minimum value constraint - valid."""
        validate_numeric_param(10, "param", min_value=5)  # Should not raise

    def test_min_value_invalid(self):
        """Test minimum value constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_numeric_param(3, "param", min_value=5)
        assert "at least 5" in str(exc_info.value)

    def test_max_value_valid(self):
        """Test maximum value constraint - valid."""
        validate_numeric_param(5, "param", max_value=10)  # Should not raise

    def test_max_value_invalid(self):
        """Test maximum value constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_numeric_param(15, "param", max_value=10)
        assert "at most 10" in str(exc_info.value)

    def test_zero_allowed(self):
        """Test that zero is allowed when allow_zero=True."""
        validate_numeric_param(0, "param", allow_zero=True)  # Should not raise

    def test_zero_not_allowed(self):
        """Test that zero raises error when allow_zero=False."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_numeric_param(0, "param", allow_zero=False)
        assert "cannot be zero" in str(exc_info.value)

    def test_not_numeric_type(self):
        """Test that non-numeric type raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_numeric_param("10", "param")
        assert "must be a number" in str(exc_info.value)

    def test_optional_none(self):
        """Test optional parameter with None value."""
        validate_numeric_param(None, "param", required=False)  # Should not raise


@pytest.mark.unit
@pytest.mark.validation
class TestValidateListParam:
    """Test validate_list_param function."""

    def test_valid_list(self):
        """Test with valid list."""
        validate_list_param([1, 2, 3], "param")  # Should not raise

    def test_valid_tuple(self):
        """Test with valid tuple."""
        validate_list_param((1, 2, 3), "param")  # Should not raise

    def test_valid_set(self):
        """Test with valid set."""
        validate_list_param({1, 2, 3}, "param")  # Should not raise

    def test_min_length_valid(self):
        """Test minimum length constraint - valid."""
        validate_list_param([1, 2, 3], "param", min_length=2)  # Should not raise

    def test_min_length_invalid(self):
        """Test minimum length constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_list_param([1], "param", min_length=2)
        assert "at least 2 items" in str(exc_info.value)

    def test_max_length_valid(self):
        """Test maximum length constraint - valid."""
        validate_list_param([1, 2], "param", max_length=5)  # Should not raise

    def test_max_length_invalid(self):
        """Test maximum length constraint - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_list_param([1, 2, 3, 4], "param", max_length=3)
        assert "at most 3 items" in str(exc_info.value)

    def test_item_validator_valid(self):
        """Test item validator - all items valid."""
        validator = _validate_item_is_int
        validate_list_param([1, 2, 3], "param", item_validator=validator)

    def test_item_validator_invalid(self):
        """Test item validator - invalid item."""
        validator = _validate_item_is_int
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_list_param([1, "2", 3], "param", item_validator=validator)
        assert "Invalid item at index" in str(exc_info.value)

    def test_not_list_type(self):
        """Test that non-list type raises error."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_list_param("not a list", "param")
        assert "must be a list, tuple, or set" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateEmail:
    """Test validate_email function."""

    def test_valid_email(self):
        """Test with valid email."""
        validate_email("user@example.com", "email")  # Should not raise

    def test_valid_email_with_subdomain(self):
        """Test with valid email with subdomain."""
        validate_email("user@mail.example.com", "email")  # Should not raise

    def test_valid_email_with_plus(self):
        """Test with valid email containing plus sign."""
        validate_email("user+tag@example.com", "email")  # Should not raise

    def test_invalid_email_no_at(self):
        """Test invalid email without @ symbol."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_email("userexample.com", "email")
        assert "Invalid email format" in str(exc_info.value)

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_email("user@", "email")
        assert "Invalid email format" in str(exc_info.value)

    def test_invalid_email_no_local(self):
        """Test invalid email without local part."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_email("@example.com", "email")
        assert "Invalid email format" in str(exc_info.value)

    def test_none_email(self):
        """Test that None email is allowed."""
        validate_email(None, "email")  # Should not raise


@pytest.mark.unit
@pytest.mark.validation
class TestValidateUrl:
    """Test validate_url function."""

    def test_valid_http_url(self):
        """Test with valid HTTP URL."""
        validate_url("http://example.com", "url")  # Should not raise

    def test_valid_https_url(self):
        """Test with valid HTTPS URL."""
        validate_url("https://example.com", "url")  # Should not raise

    def test_valid_url_with_path(self):
        """Test with valid URL with path."""
        validate_url("https://example.com/path/to/resource", "url")

    def test_valid_url_with_query(self):
        """Test with valid URL with query parameters."""
        validate_url("https://example.com/path?key=value", "url")

    def test_invalid_url_no_protocol(self):
        """Test invalid URL without protocol."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_url("example.com", "url")
        assert "Invalid URL format" in str(exc_info.value)

    def test_invalid_url_wrong_protocol(self):
        """Test invalid URL with wrong protocol."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_url("ftp://example.com", "url")
        assert "Invalid URL format" in str(exc_info.value)

    def test_none_url(self):
        """Test that None URL is allowed."""
        validate_url(None, "url")  # Should not raise


@pytest.mark.unit
@pytest.mark.validation
class TestValidatePaginationParams:
    """Test validate_pagination_params function."""

    def test_valid_page_size(self):
        """Test with valid page size."""
        validate_pagination_params(page_size=100)  # Should not raise

    def test_valid_page_token(self):
        """Test with valid page token."""
        validate_pagination_params(page_token="123")  # Should not raise

    def test_page_size_too_small(self):
        """Test page size below minimum."""
        with pytest.raises(ViInvalidParameterError):
            validate_pagination_params(page_size=0)

    def test_page_size_too_large(self):
        """Test page size above maximum."""
        with pytest.raises(ViInvalidParameterError):
            validate_pagination_params(page_size=1001)

    def test_negative_page_size(self):
        """Test negative page size."""
        with pytest.raises(ViInvalidParameterError):
            validate_pagination_params(page_size=-1)

    def test_page_size_zero(self):
        """Test page size zero."""
        with pytest.raises(ViInvalidParameterError):
            validate_pagination_params(page_size=0)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateSortParams:
    """Test validate_sort_params function."""

    def test_valid_sort_by(self):
        """Test with valid sort_by."""
        validate_sort_params(sort_by="name")  # Should not raise

    def test_valid_sort_order_asc(self):
        """Test with valid ascending sort order."""
        validate_sort_params(sort_order="asc")  # Should not raise

    def test_valid_sort_order_desc(self):
        """Test with valid descending sort order."""
        validate_sort_params(sort_order="desc")  # Should not raise

    def test_allowed_sort_fields_valid(self):
        """Test with allowed sort fields - valid."""
        validate_sort_params(sort_by="name", allowed_sort_fields=["name", "created_at"])

    def test_allowed_sort_fields_invalid(self):
        """Test with allowed sort fields - invalid."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_sort_params(
                sort_by="invalid_field", allowed_sort_fields=["name", "created_at"]
            )
        assert "Invalid sort field" in str(exc_info.value)

    def test_invalid_sort_order(self):
        """Test with invalid sort order."""
        with pytest.raises(ViInvalidParameterError) as exc_info:
            validate_sort_params(sort_order="invalid")
        assert "Must be 'asc' or 'desc'" in str(exc_info.value)
