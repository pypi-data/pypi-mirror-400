#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_requester.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for HTTP requester module.
"""

import json
from unittest.mock import Mock, patch

import httpx
import pytest
from vi.client.errors import (
    ViNetworkError,
    ViNotFoundError,
    ViRateLimitError,
    ViServerError,
    ViTimeoutError,
)
from vi.client.http.requester import Requester
from vi.client.http.retry import RetryConfig, RetryStrategy


@pytest.mark.unit
@pytest.mark.network
class TestRequesterInitialization:
    """Test Requester initialization."""

    def test_init_with_defaults(self, mock_auth: Mock) -> None:
        """Test initialization with default parameters.

        Args:
            mock_auth: Mock authentication object fixture.

        """
        requester = Requester(mock_auth, "https://api.test.com")
        assert requester._auth == mock_auth
        assert requester._base_url == "https://api.test.com"
        assert requester._max_retries > 0

    def test_init_with_custom_retries(self, mock_auth):
        """Test initialization with custom max retries."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=5)
        assert requester._max_retries == 5

    def test_init_with_custom_timeout(self, mock_auth):
        """Test initialization with custom timeout."""
        timeout = httpx.Timeout(10.0)
        requester = Requester(mock_auth, "https://api.test.com", timeout=timeout)
        assert requester._timeout == timeout

    def test_base_url_trailing_slash_removal(self, mock_auth):
        """Test that trailing slash is removed from base URL."""
        requester = Requester(mock_auth, "https://api.test.com/")
        assert requester._base_url == "https://api.test.com"


@pytest.mark.unit
@pytest.mark.network
class TestRequesterHeaders:
    """Test Requester header generation."""

    def test_get_headers(self, mock_auth):
        """Test header generation."""
        requester = Requester(mock_auth, "https://api.test.com")
        headers = requester._get_headers()

        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert "Authorization" in headers
        assert "Organization-Id" in headers


@pytest.mark.unit
@pytest.mark.network
class TestRequesterBuildLink:
    """Test URL building."""

    def test_build_link_simple(self, mock_auth):
        """Test building simple URL."""
        requester = Requester(mock_auth, "https://api.test.com")
        url = requester._build_link("/datasets")
        assert url == "https://api.test.com/datasets"

    def test_build_link_without_leading_slash(self, mock_auth):
        """Test building URL without leading slash."""
        requester = Requester(mock_auth, "https://api.test.com")
        url = requester._build_link("datasets")
        assert url == "https://api.test.com/datasets"

    def test_build_link_with_params(self, mock_auth):
        """Test building URL with query parameters."""
        requester = Requester(mock_auth, "https://api.test.com")
        url = requester._build_link("/datasets", params={"page": 1, "limit": 10})
        assert "page=1" in url
        assert "limit=10" in url

    def test_build_link_with_none_params(self, mock_auth):
        """Test building URL with None parameter values."""
        requester = Requester(mock_auth, "https://api.test.com")
        url = requester._build_link("/datasets", params={"page": 1, "optional": None})
        assert "page=1" in url
        assert "optional" not in url

    def test_build_link_with_boolean_params(self, mock_auth):
        """Test building URL with boolean parameters."""
        requester = Requester(mock_auth, "https://api.test.com")
        url = requester._build_link(
            "/datasets", params={"active": True, "archived": False}
        )
        assert "active=true" in url
        assert "archived=false" in url


@pytest.mark.unit
@pytest.mark.network
class TestRequesterHandleResponse:
    """Test response handling."""

    def test_handle_successful_json_response(self, mock_auth, create_mock_response):
        """Test handling successful JSON response."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(200, {"data": "success"})

        result = requester._handle_response(mock_response)
        assert result == {"data": "success"}

    def test_handle_successful_text_response(self, mock_auth, create_mock_response):
        """Test handling successful non-JSON response."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(200)
        mock_response.json.side_effect = json.JSONDecodeError("", "", 0)
        mock_response.text = "Plain text response"

        result = requester._handle_response(mock_response)
        assert result["data"] == "Plain text response"

    def test_handle_404_error(self, mock_auth, create_mock_response):
        """Test handling 404 error."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(404, {"message": "Not found"})

        with pytest.raises(ViNotFoundError):
            requester._handle_response(mock_response)

    def test_handle_500_error(self, mock_auth, create_mock_response):
        """Test handling 500 error."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(500, {"message": "Server error"})

        with pytest.raises(ViServerError):
            requester._handle_response(mock_response)

    def test_handle_429_error(self, mock_auth, create_mock_response):
        """Test handling rate limit error."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(429, {"message": "Rate limit exceeded"})

        with pytest.raises(ViRateLimitError):
            requester._handle_response(mock_response)

    def test_handle_error_without_json(self, mock_auth, create_mock_response):
        """Test handling error response without JSON."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(500)
        mock_response.json.side_effect = json.JSONDecodeError("", "", 0)
        mock_response.text = "Internal Server Error"

        with pytest.raises(ViServerError):
            requester._handle_response(mock_response)


@pytest.mark.unit
@pytest.mark.network
class TestRequesterRetryLogic:
    """Test retry logic."""

    def test_successful_request_no_retry(self, mock_auth, create_mock_response):
        """Test successful request without retry."""
        requester = Requester(mock_auth, "https://api.test.com")
        mock_response = create_mock_response(200, {"data": "success"})

        with patch.object(requester._client, "request", return_value=mock_response):
            result = requester.get("/test")
            assert result == {"data": "success"}
            # Should only be called once (no retries)
            assert requester._client.request.call_count == 1

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_retry_on_network_error(self, mock_sleep, mock_auth):
        """Test retry on network error."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=2)
        network_error = httpx.RequestError("Connection failed")

        with patch.object(
            requester._client, "request", side_effect=network_error
        ) as mock_request:
            with pytest.raises(ViNetworkError):
                requester.get("/test")

            # Should retry max_retries + 1 times
            assert mock_request.call_count == 3

    @patch("time.sleep")
    def test_retry_on_timeout(self, mock_sleep, mock_auth):
        """Test retry on timeout."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=2)
        timeout_error = httpx.TimeoutException("Request timed out")

        with patch.object(
            requester._client, "request", side_effect=timeout_error
        ) as mock_request:
            with pytest.raises(ViTimeoutError):
                requester.get("/test")

            assert mock_request.call_count == 3

    @patch("time.sleep")
    def test_retry_on_rate_limit(self, mock_sleep, mock_auth, create_mock_response):
        """Test retry on rate limit error."""
        # Set max_rate_limit_retries to match max_retries for this test
        retry_config = RetryConfig(max_retries=2, max_rate_limit_retries=2)
        requester = Requester(
            mock_auth, "https://api.test.com", retry_config=retry_config
        )
        rate_limit_response = create_mock_response(429, {"message": "Rate limit"})

        with patch.object(
            requester._client, "request", return_value=rate_limit_response
        ) as mock_request:
            with pytest.raises(ViRateLimitError):
                requester.get("/test")

            assert mock_request.call_count == 3

    @patch("time.sleep")
    def test_retry_on_server_error(self, mock_sleep, mock_auth, create_mock_response):
        """Test retry on server error."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=2)
        server_error_response = create_mock_response(500, {"message": "Server error"})

        with patch.object(
            requester._client, "request", return_value=server_error_response
        ) as mock_request:
            with pytest.raises(ViServerError):
                requester.get("/test")

            assert mock_request.call_count == 3

    @patch("time.sleep")
    def test_success_after_retry(self, mock_sleep, mock_auth, create_mock_response):
        """Test successful request after retry."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=2)
        error_response = create_mock_response(500, {"message": "Server error"})
        success_response = create_mock_response(200, {"data": "success"})

        # First call fails, second succeeds
        with patch.object(
            requester._client,
            "request",
            side_effect=[error_response, success_response],
        ) as mock_request:
            result = requester.get("/test")
            assert result == {"data": "success"}
            assert mock_request.call_count == 2

    def test_no_retry_on_client_error(self, mock_auth, create_mock_response):
        """Test that client errors don't trigger retry."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=2)
        client_error_response = create_mock_response(400, {"message": "Bad request"})

        with patch.object(
            requester._client, "request", return_value=client_error_response
        ) as mock_request:
            with pytest.raises(Exception):  # Will raise some ViError subclass
                requester.get("/test")

            # Should only be called once (no retries for client errors)
            assert mock_request.call_count == 1


@pytest.mark.unit
@pytest.mark.network
class TestRequesterMethods:
    """Test HTTP method wrappers."""

    def test_get_request(self, mock_auth, create_mock_response):
        """Test GET request."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "success"})

        with patch.object(requester._client, "request", return_value=success_response):
            result = requester.get("/test")
            assert result == {"data": "success"}
            requester._client.request.assert_called_once()
            args, kwargs = requester._client.request.call_args
            assert args[0] == "GET"

    def test_post_request(self, mock_auth, create_mock_response):
        """Test POST request."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "created"})

        with patch.object(requester._client, "request", return_value=success_response):
            result = requester.post("/test", json_data={"key": "value"})
            assert result == {"data": "created"}
            args, kwargs = requester._client.request.call_args
            assert args[0] == "POST"
            assert kwargs["json"] == {"key": "value"}

    def test_put_request(self, mock_auth, create_mock_response):
        """Test PUT request."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "updated"})

        with patch.object(requester._client, "request", return_value=success_response):
            result = requester.put("/test", json_data={"key": "new_value"})
            assert result == {"data": "updated"}
            args, kwargs = requester._client.request.call_args
            assert args[0] == "PUT"

    def test_patch_request(self, mock_auth, create_mock_response):
        """Test PATCH request."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "patched"})

        with patch.object(requester._client, "request", return_value=success_response):
            result = requester.patch("/test", json_data={"key": "patch_value"})
            assert result == {"data": "patched"}
            args, kwargs = requester._client.request.call_args
            assert args[0] == "PATCH"

    def test_delete_request(self, mock_auth, create_mock_response):
        """Test DELETE request."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "deleted"})

        with patch.object(requester._client, "request", return_value=success_response):
            result = requester.delete("/test")
            assert result == {"data": "deleted"}
            args, kwargs = requester._client.request.call_args
            assert args[0] == "DELETE"


@pytest.mark.unit
@pytest.mark.network
class TestRequesterEdgeCases:
    """Test edge cases for requester."""

    def test_close_method(self, mock_auth):
        """Test close method."""
        requester = Requester(mock_auth, "https://api.test.com")
        with patch.object(requester._client, "close") as mock_close:
            requester.close()
            mock_close.assert_called_once()

    def test_request_with_special_characters_in_url(
        self, mock_auth, create_mock_response
    ):
        """Test request with special characters in URL."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {})

        with patch.object(requester._client, "request", return_value=success_response):
            # Should handle special characters
            requester.get("/test/path-with-dash_and_underscore")

    def test_request_with_empty_json_data(self, mock_auth, create_mock_response):
        """Test POST request with empty JSON data."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {})

        with patch.object(requester._client, "request", return_value=success_response):
            _ = requester.post("/test", json_data={})
            args, kwargs = requester._client.request.call_args
            assert kwargs["json"] == {}

    def test_request_with_none_json_data(self, mock_auth, create_mock_response):
        """Test POST request with None JSON data."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {})

        with patch.object(requester._client, "request", return_value=success_response):
            _ = requester.post("/test", json_data=None)
            args, kwargs = requester._client.request.call_args
            assert kwargs["json"] is None

    def test_multiple_consecutive_requests(self, mock_auth, create_mock_response):
        """Test multiple consecutive requests."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "success"})

        with patch.object(requester._client, "request", return_value=success_response):
            for i in range(10):
                result = requester.get(f"/test/{i}")
                assert result == {"data": "success"}

            assert requester._client.request.call_count == 10

    def test_request_with_response_type(self, mock_auth, create_mock_response):
        """Test request with response type specification."""
        requester = Requester(mock_auth, "https://api.test.com")
        success_response = create_mock_response(200, {"data": "success"})

        with patch.object(requester._client, "request", return_value=success_response):
            # This would normally deserialize to a specific type
            result = requester.get("/test", response_type=dict)
            assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.network
class TestRequesterRetryConfiguration:
    """Test Requester retry configuration."""

    def test_init_with_retry_config(self, mock_auth):
        """Test initialization with custom retry config."""
        retry_config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL_EQUAL_JITTER,
        )
        requester = Requester(
            mock_auth, "https://api.test.com", retry_config=retry_config
        )

        assert requester._retry_config == retry_config
        assert requester._max_retries == 5
        assert requester._retry_handler.config == retry_config

    def test_init_with_max_retries_fallback(self, mock_auth):
        """Test that max_retries parameter works when retry_config is not provided."""
        requester = Requester(mock_auth, "https://api.test.com", max_retries=7)

        assert requester._max_retries == 7
        assert requester._retry_config.max_retries == 7

    def test_retry_config_overrides_max_retries(self, mock_auth):
        """Test that retry_config takes precedence over max_retries."""
        retry_config = RetryConfig(max_retries=5)
        requester = Requester(
            mock_auth,
            "https://api.test.com",
            max_retries=10,  # Should be ignored
            retry_config=retry_config,
        )

        assert requester._max_retries == 5

    @patch("time.sleep")
    def test_retry_with_custom_strategy(
        self, mock_sleep, mock_auth, create_mock_response
    ):
        """Test retry with custom strategy."""
        retry_config = RetryConfig(
            max_retries=2,
            base_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL,  # No jitter for predictable testing
        )
        requester = Requester(
            mock_auth, "https://api.test.com", retry_config=retry_config
        )
        error_response = create_mock_response(500, {"message": "Server error"})

        with patch.object(
            requester._client, "request", return_value=error_response
        ) as mock_request:
            with pytest.raises(ViServerError):
                requester.get("/test")

            # Should retry max_retries + 1 times
            assert mock_request.call_count == 3

            # Check that sleep was called with expected backoff times
            # For exponential: base_delay * 2^attempt
            # Attempt 0: 1.0 * 2^0 = 1.0
            # Attempt 1: 1.0 * 2^1 = 2.0
            assert mock_sleep.call_count == 2
