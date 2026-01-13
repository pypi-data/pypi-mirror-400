#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_errors.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for error handling and error classes.
"""

import json
from unittest.mock import Mock

import pytest
from vi.client.errors import (
    ViAuthenticationError,
    ViConfigurationError,
    ViConflictError,
    ViDownloadError,
    ViError,
    ViErrorCode,
    ViFileTooLargeError,
    ViInvalidFileFormatError,
    ViInvalidParameterError,
    ViNetworkError,
    ViNotFoundError,
    ViOperationError,
    ViPermissionError,
    ViRateLimitError,
    ViServerError,
    ViTimeoutError,
    ViUploadError,
    ViValidationError,
    create_error_from_response,
)


@pytest.mark.unit
@pytest.mark.error
class TestViErrorCode:
    """Test ViErrorCode enum."""

    def test_error_code_values(self):
        """Test that error codes have correct string values."""
        assert ViErrorCode.AUTHENTICATION_FAILED.value == "AuthenticationFailed"
        assert ViErrorCode.VALIDATION_FAILED.value == "ValidationFailed"
        assert ViErrorCode.RESOURCE_NOT_FOUND.value == "ResourceNotFound"

    def test_http_status_mapping(self):
        """Test HTTP status code mapping."""
        assert ViErrorCode.AUTHENTICATION_FAILED.http_status == 401
        assert ViErrorCode.PERMISSION_DENIED.http_status == 403
        assert ViErrorCode.RESOURCE_NOT_FOUND.http_status == 404
        assert ViErrorCode.VALIDATION_FAILED.http_status == 400
        assert ViErrorCode.SERVER_ERROR.http_status == 500
        assert ViErrorCode.RATE_LIMIT_EXCEEDED.http_status == 429

    def test_from_http_status(self):
        """Test creating error code from HTTP status."""
        assert ViErrorCode.from_http_status(401) == ViErrorCode.AUTHENTICATION_FAILED
        assert ViErrorCode.from_http_status(404) == ViErrorCode.RESOURCE_NOT_FOUND
        assert ViErrorCode.from_http_status(500) == ViErrorCode.SERVER_ERROR
        assert ViErrorCode.from_http_status(999) == ViErrorCode.UNKNOWN_ERROR


@pytest.mark.unit
@pytest.mark.error
class TestViError:
    """Test ViError base class."""

    def test_basic_error_creation(self):
        """Test creating basic error."""
        error = ViError("Test error message")
        assert str(error.message) == "Test error message"
        assert error.error_code == ViErrorCode.UNKNOWN_ERROR
        assert error.status_code is None
        assert error.suggestion is None

    def test_error_with_all_params(self):
        """Test creating error with all parameters."""
        error = ViError(
            "Test error",
            error_code=ViErrorCode.VALIDATION_FAILED,
            status_code=400,
            suggestion="Fix the input",
        )
        assert error.message == "Test error"
        assert error.error_code == ViErrorCode.VALIDATION_FAILED
        assert error.status_code == 400
        assert error.suggestion == "Fix the input"

    def test_error_from_exception(self):
        """Test creating error from exception."""
        original_error = ValueError("Invalid value")
        error = ViError(original_error)
        assert "Invalid value" in error.message
        assert error.cause == original_error

    def test_error_str_representation(self):
        """Test string representation."""
        error = ViError(
            "Test error",
            error_code=ViErrorCode.VALIDATION_FAILED,
            suggestion="Check your input",
        )
        str_repr = str(error)
        assert "[ValidationFailed]" in str_repr
        assert "Test error" in str_repr
        assert "Check your input" in str_repr

    def test_error_repr(self):
        """Test repr representation."""
        error = ViError("Test", error_code=ViErrorCode.VALIDATION_FAILED)
        repr_str = repr(error)
        assert "ViError" in repr_str
        assert "Test" in repr_str

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = ViError(
            "Test error",
            error_code=ViErrorCode.VALIDATION_FAILED,
            status_code=400,
            suggestion="Fix it",
        )
        error_dict = error.to_dict()
        assert error_dict["error_code"] == "ValidationFailed"
        assert error_dict["message"] == "Test error"
        assert error_dict["status_code"] == 400
        assert error_dict["suggestion"] == "Fix it"

    def test_to_dict_with_trace_id(self):
        """Test converting error with trace_id to dictionary."""
        error = ViError(
            "Test error",
            error_code=ViErrorCode.SERVER_ERROR,
            status_code=500,
            trace_id="def70e41ca2954b37739419434be691d",
        )
        error_dict = error.to_dict()
        assert error_dict["trace_id"] == "def70e41ca2954b37739419434be691d"
        assert error_dict["error_code"] == "ServerError"

    def test_to_dict_without_trace_id(self):
        """Test that trace_id is not included in dict when None."""
        error = ViError(
            "Test error",
            error_code=ViErrorCode.SERVER_ERROR,
            status_code=500,
        )
        error_dict = error.to_dict()
        assert "trace_id" not in error_dict

    def test_is_client_error(self):
        """Test is_client_error method."""
        error = ViError("Test", error_code=ViErrorCode.VALIDATION_FAILED)
        assert error.is_client_error() is True
        assert error.is_server_error() is False

    def test_is_server_error(self):
        """Test is_server_error method."""
        error = ViError("Test", error_code=ViErrorCode.SERVER_ERROR)
        assert error.is_server_error() is True
        assert error.is_client_error() is False

    def test_is_retryable(self):
        """Test is_retryable method."""
        retryable_error = ViError("Test", error_code=ViErrorCode.NETWORK_ERROR)
        assert retryable_error.is_retryable() is True

        non_retryable_error = ViError("Test", error_code=ViErrorCode.VALIDATION_FAILED)
        assert non_retryable_error.is_retryable() is False

    def test_sanitize_resource_id(self):
        """Test resource ID sanitization in error messages."""
        message = "dataset org-123_dataset-456 not found"
        error = ViError(message)
        assert "dataset dataset-456" in error.message
        assert "org-123" not in error.message

    def test_exception_mapping_connection_error(self):
        """Test mapping ConnectionError to ViError."""
        original = ConnectionError("Connection failed")
        error = ViError(original)
        assert error.error_code == ViErrorCode.NETWORK_ERROR
        if error.suggestion:
            assert "internet connection" in error.suggestion

    def test_exception_mapping_value_error(self):
        """Test mapping ValueError to ViError."""
        original = ValueError("Invalid value")
        error = ViError(original)
        assert error.error_code == ViErrorCode.VALIDATION_FAILED

    def test_exception_mapping_file_not_found(self):
        """Test mapping FileNotFoundError to ViError."""
        original = FileNotFoundError("File not found")
        error = ViError(original)
        assert error.error_code == ViErrorCode.RESOURCE_NOT_FOUND

    def test_exception_mapping_permission_error(self):
        """Test mapping PermissionError to ViError."""
        original = PermissionError("Access denied")
        error = ViError(original)
        assert error.error_code == ViErrorCode.PERMISSION_DENIED

    def test_exception_mapping_json_decode_error(self):
        """Test mapping JSONDecodeError to ViError."""
        original = json.JSONDecodeError("Invalid JSON", "", 0)
        error = ViError(original)
        assert error.error_code == ViErrorCode.VALIDATION_FAILED


@pytest.mark.unit
@pytest.mark.error
class TestSpecificErrors:
    """Test specific error classes."""

    def test_authentication_error(self):
        """Test ViAuthenticationError."""
        error = ViAuthenticationError("Invalid credentials")
        assert error.error_code == ViErrorCode.AUTHENTICATION_FAILED
        assert "Invalid credentials" in str(error)
        if error.suggestion:
            assert "API key" in error.suggestion

    def test_not_found_error(self):
        """Test ViNotFoundError."""
        error = ViNotFoundError("Resource not found")
        assert error.error_code == ViErrorCode.RESOURCE_NOT_FOUND
        assert "not found" in str(error).lower()

    def test_rate_limit_error(self):
        """Test ViRateLimitError."""
        error = ViRateLimitError("Too many requests")
        assert error.error_code == ViErrorCode.RATE_LIMIT_EXCEEDED
        assert "too many requests" in str(error).lower()
        if error.suggestion:
            assert "retry" in error.suggestion.lower()

    def test_server_error(self):
        """Test ViServerError."""
        error = ViServerError("Internal error")
        assert error.error_code == ViErrorCode.SERVER_ERROR
        if error.suggestion:
            assert "temporary issue" in error.suggestion.lower()

    def test_network_error(self):
        """Test ViNetworkError."""
        error = ViNetworkError("Connection failed")
        assert error.error_code == ViErrorCode.NETWORK_ERROR
        if error.suggestion:
            assert "connection" in error.suggestion.lower()

    def test_validation_error(self):
        """Test ViValidationError."""
        error = ViValidationError("Invalid input")
        assert error.error_code == ViErrorCode.VALIDATION_FAILED
        assert "Invalid input" in str(error)

    def test_download_error(self):
        """Test ViDownloadError."""
        error = ViDownloadError("Download failed")
        assert error.error_code == ViErrorCode.DOWNLOAD_FAILED
        if error.suggestion:
            assert "disk space" in error.suggestion.lower()

    def test_configuration_error(self):
        """Test ViConfigurationError."""
        error = ViConfigurationError("Invalid config")
        assert error.error_code == ViErrorCode.CONFIGURATION_ERROR

    def test_permission_error(self):
        """Test ViPermissionError."""
        error = ViPermissionError("Access denied")
        assert error.error_code == ViErrorCode.PERMISSION_DENIED

    def test_operation_error(self):
        """Test ViOperationError."""
        error = ViOperationError("Operation failed")
        assert error.error_code == ViErrorCode.OPERATION_FAILED

    def test_upload_error(self):
        """Test ViUploadError."""
        error = ViUploadError("Upload failed")
        assert error.error_code == ViErrorCode.UPLOAD_FAILED

    def test_timeout_error(self):
        """Test ViTimeoutError."""
        error = ViTimeoutError("Request timed out")
        assert error.error_code == ViErrorCode.TIMEOUT_ERROR

    def test_conflict_error(self):
        """Test ViConflictError."""
        error = ViConflictError("Resource conflict")
        assert error.error_code == ViErrorCode.RESOURCE_CONFLICT

    def test_invalid_parameter_error(self):
        """Test ViInvalidParameterError."""
        error = ViInvalidParameterError("param_name", "Invalid value")
        assert error.error_code == ViErrorCode.INVALID_PARAMETER
        assert "param_name" in str(error)

    def test_invalid_parameter_error_auto_message(self):
        """Test ViInvalidParameterError with auto-generated message."""
        error = ViInvalidParameterError("param_name")
        assert "Invalid parameter: param_name" in str(error)

    def test_file_too_large_error(self):
        """Test ViFileTooLargeError."""
        error = ViFileTooLargeError(file_size=2048, max_size=1024)
        assert error.error_code == ViErrorCode.FILE_TOO_LARGE
        assert "2048" in str(error)
        assert "1024" in str(error)
        assert error.to_dict()["details"]["file_size"] == 2048
        assert error.to_dict()["details"]["max_size"] == 1024

    def test_invalid_file_format_error(self):
        """Test ViInvalidFileFormatError."""
        error = ViInvalidFileFormatError(
            file_format=".xyz", supported_formats=[".png", ".jpg"]
        )
        assert error.error_code == ViErrorCode.INVALID_FILE_FORMAT
        assert ".xyz" in str(error)
        assert ".png" in str(error)
        assert error.to_dict()["details"]["file_format"] == ".xyz"


@pytest.mark.unit
@pytest.mark.error
class TestCreateErrorFromResponse:
    """Test create_error_from_response function."""

    def _create_mock_response(self, status_code: int, message: str):
        """Create a mock response object."""
        response = Mock()
        response.status_code = status_code
        response.json.return_value = {"message": message}
        response.text = message
        response.headers = {}
        return response

    def test_create_400_error(self):
        """Test creating error from 400 response."""
        response = self._create_mock_response(400, "Bad request")
        error = create_error_from_response(response)
        assert isinstance(error, ViValidationError)
        assert error.status_code == 400
        assert "Bad request" in str(error)

    def test_create_401_error(self):
        """Test creating error from 401 response."""
        response = self._create_mock_response(401, "Unauthorized")
        error = create_error_from_response(response)
        assert isinstance(error, ViAuthenticationError)
        assert error.status_code == 401

    def test_create_403_error(self):
        """Test creating error from 403 response."""
        response = self._create_mock_response(403, "Forbidden")
        error = create_error_from_response(response)
        assert isinstance(error, ViAuthenticationError)
        assert error.status_code == 403

    def test_create_404_error(self):
        """Test creating error from 404 response."""
        response = self._create_mock_response(404, "Not found")
        error = create_error_from_response(response)
        assert isinstance(error, ViNotFoundError)
        assert error.status_code == 404

    def test_create_409_error(self):
        """Test creating error from 409 response."""
        response = self._create_mock_response(409, "Conflict")
        error = create_error_from_response(response)
        assert isinstance(error, ViConflictError)
        assert error.status_code == 409

    def test_create_429_error(self):
        """Test creating error from 429 response."""
        response = self._create_mock_response(429, "Rate limit exceeded")
        error = create_error_from_response(response)
        assert isinstance(error, ViRateLimitError)
        assert error.status_code == 429

    def test_create_500_error(self):
        """Test creating error from 500 response."""
        response = self._create_mock_response(500, "Internal server error")
        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.status_code == 500

    def test_create_502_error(self):
        """Test creating error from 502 response."""
        response = self._create_mock_response(502, "Bad gateway")
        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.status_code == 502

    def test_create_503_error(self):
        """Test creating error from 503 response."""
        response = self._create_mock_response(503, "Service unavailable")
        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.status_code == 503

    def test_create_504_error(self):
        """Test creating error from 504 response."""
        response = self._create_mock_response(504, "Gateway timeout")
        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.status_code == 504

    def test_create_unknown_error(self):
        """Test creating error from unknown status code."""
        response = self._create_mock_response(418, "I'm a teapot")
        error = create_error_from_response(response)
        assert isinstance(error, ViError)
        assert error.status_code == 418

    def test_create_error_with_retry_after(self):
        """Test creating error from response with Retry-After header."""
        response = Mock()
        response.status_code = 429
        response.json.return_value = {"message": "Rate limit"}
        response.text = "Rate limit"
        response.headers = {"Retry-After": "60"}

        error = create_error_from_response(response)
        assert isinstance(error, ViRateLimitError)
        assert error.retry_after == "60"

    def test_create_error_with_trace_id(self):
        """Test creating error from response with x-cloud-trace-context header."""
        response = Mock()
        response.status_code = 500
        response.json.return_value = {"message": "Server error"}
        response.text = "Server error"
        response.headers = {"x-cloud-trace-context": "def70e41ca2954b37739419434be691d"}

        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.trace_id == "def70e41ca2954b37739419434be691d"

    def test_create_error_with_trace_id_and_span(self):
        """Test creating error with trace ID that includes span info."""
        response = Mock()
        response.status_code = 404
        response.json.return_value = {"message": "Not found"}
        response.text = "Not found"
        response.headers = {
            "x-cloud-trace-context": "def70e41ca2954b37739419434be691d/12345;o=1"
        }

        error = create_error_from_response(response)
        assert isinstance(error, ViNotFoundError)
        # Should extract only the trace ID part (before the slash)
        assert error.trace_id == "def70e41ca2954b37739419434be691d"

    def test_create_error_without_trace_id(self):
        """Test creating error from response without trace ID header."""
        response = Mock()
        response.status_code = 500
        response.json.return_value = {"message": "Server error"}
        response.text = "Server error"
        response.headers = {}

        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert error.trace_id is None

    def test_create_error_without_json_body(self):
        """Test creating error from response without JSON body."""
        response = Mock()
        response.status_code = 500
        response.json.side_effect = json.JSONDecodeError("", "", 0)
        response.text = "Internal Server Error"
        response.headers = {}

        error = create_error_from_response(response)
        assert isinstance(error, ViServerError)
        assert "500" in error.message


@pytest.mark.unit
@pytest.mark.error
class TestErrorEdgeCases:
    """Test error edge cases."""

    def test_error_with_empty_message(self):
        """Test error with empty message."""
        error = ViError("")
        assert error.message == ""

    def test_error_with_none_suggestion(self):
        """Test error with None suggestion."""
        error = ViError("Test", suggestion=None)
        assert error.suggestion is None
        # Should not raise when converting to string
        str(error)

    def test_error_with_very_long_message(self):
        """Test error with very long message."""
        long_message = "x" * 10000
        error = ViError(long_message)
        assert error.message == long_message

    def test_error_with_special_characters(self):
        """Test error with special characters in message."""
        special_message = "Error: \n\t\r Special chars: 你好 éàü"
        error = ViError(special_message)
        assert error.message == special_message

    def test_error_chain(self):
        """Test error chaining."""
        original = ValueError("Original error")
        chained = ViError(original)
        assert chained.cause == original
        assert "Original error" in chained.message

    def test_error_without_suggestion(self):
        """Test error without suggestion in string representation."""
        error = ViError("Test error", suggestion=None)
        str_repr = str(error)
        assert "Test error" in str_repr
        assert "Suggestion" not in str_repr

    def test_multiple_error_instantiation(self):
        """Test creating multiple error instances."""
        errors = [
            ViError(f"Error {i}", error_code=ViErrorCode.VALIDATION_FAILED)
            for i in range(100)
        ]
        assert len(errors) == 100
        assert all(e.error_code == ViErrorCode.VALIDATION_FAILED for e in errors)

    def test_error_http_status_property(self):
        """Test http_status property."""
        error = ViError("Test", error_code=ViErrorCode.VALIDATION_FAILED)
        assert error.http_status == 400

    def test_sanitize_multiple_dataset_ids(self):
        """Test sanitizing multiple dataset IDs in message."""
        message = "Datasets org-123_ds1 and org-123_ds2 not found"
        error = ViError(message)
        # First ID with resource type prefix gets sanitized to "dataset ds1"
        assert "dataset ds1" in error.message
        # Second ID without resource type prefix gets sanitized to just "ds2"
        assert "ds2" in error.message
        # Organization ID prefix should be removed
        assert "org-123" not in error.message

    def test_error_subclass_inheritance(self):
        """Test that error subclasses properly inherit."""
        error = ViAuthenticationError("Test")
        assert isinstance(error, ViError)
        assert isinstance(error, Exception)

    def test_validation_error_subclass(self):
        """Test ViValidationError subclasses."""
        # ViInvalidParameterError is a subclass of ViValidationError
        error = ViInvalidParameterError("param")
        assert isinstance(error, ViValidationError)
        assert isinstance(error, ViError)

    def test_error_details_in_dict(self):
        """Test that details are properly included in to_dict."""
        error = ViFileTooLargeError(file_size=5000, max_size=1000)
        error_dict = error.to_dict()
        # Details should be included in the dict for errors that have them
        assert "details" in error_dict
        assert error_dict["details"]["file_size"] == 5000
        assert error_dict["details"]["max_size"] == 1000
        # And the error message should also contain the details
        assert "5000" in error.message
        assert "1000" in error.message
