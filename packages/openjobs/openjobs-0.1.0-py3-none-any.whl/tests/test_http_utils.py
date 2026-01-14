"""Tests for openjobs.http_utils module."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from openjobs.http_utils import (
    fetch_with_retry,
    fetch_json_with_retry,
    post_with_retry,
    post_json_with_retry,
    _should_retry,
    DEFAULT_HEADERS,
    RETRYABLE_STATUS_CODES,
)


class TestShouldRetry:
    """Tests for _should_retry function."""

    def test_retry_on_connection_error(self):
        """Test retry on ConnectionError."""
        exc = requests.ConnectionError("Connection refused")
        assert _should_retry(exc) is True

    def test_retry_on_timeout(self):
        """Test retry on Timeout."""
        exc = requests.Timeout("Request timed out")
        assert _should_retry(exc) is True

    def test_retry_on_chunked_encoding_error(self):
        """Test retry on ChunkedEncodingError."""
        exc = requests.exceptions.ChunkedEncodingError("Chunk error")
        assert _should_retry(exc) is True

    def test_retry_on_429(self):
        """Test retry on rate limit (429)."""
        response = MagicMock()
        response.status_code = 429
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is True

    def test_retry_on_500(self):
        """Test retry on server error (500)."""
        response = MagicMock()
        response.status_code = 500
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is True

    def test_retry_on_502(self):
        """Test retry on bad gateway (502)."""
        response = MagicMock()
        response.status_code = 502
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is True

    def test_retry_on_503(self):
        """Test retry on service unavailable (503)."""
        response = MagicMock()
        response.status_code = 503
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is True

    def test_retry_on_504(self):
        """Test retry on gateway timeout (504)."""
        response = MagicMock()
        response.status_code = 504
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is True

    def test_no_retry_on_400(self):
        """Test no retry on client error (400)."""
        response = MagicMock()
        response.status_code = 400
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is False

    def test_no_retry_on_404(self):
        """Test no retry on not found (404)."""
        response = MagicMock()
        response.status_code = 404
        exc = requests.HTTPError(response=response)
        assert _should_retry(exc) is False

    def test_no_retry_on_generic_exception(self):
        """Test no retry on generic exception."""
        exc = ValueError("Some error")
        assert _should_retry(exc) is False


class TestDefaultHeaders:
    """Tests for default headers configuration."""

    def test_user_agent_present(self):
        """Test User-Agent header is set."""
        assert 'User-Agent' in DEFAULT_HEADERS
        assert 'Mozilla' in DEFAULT_HEADERS['User-Agent']

    def test_accept_header_present(self):
        """Test Accept header is set."""
        assert 'Accept' in DEFAULT_HEADERS
        assert DEFAULT_HEADERS['Accept'] == 'application/json'


class TestRetryableStatusCodes:
    """Tests for retryable status codes configuration."""

    def test_429_is_retryable(self):
        """Test 429 is in retryable codes."""
        assert 429 in RETRYABLE_STATUS_CODES

    def test_5xx_are_retryable(self):
        """Test 5xx errors are retryable."""
        assert 500 in RETRYABLE_STATUS_CODES
        assert 502 in RETRYABLE_STATUS_CODES
        assert 503 in RETRYABLE_STATUS_CODES
        assert 504 in RETRYABLE_STATUS_CODES

    def test_4xx_not_retryable(self):
        """Test 4xx errors (except 429) are not retryable."""
        assert 400 not in RETRYABLE_STATUS_CODES
        assert 401 not in RETRYABLE_STATUS_CODES
        assert 403 not in RETRYABLE_STATUS_CODES
        assert 404 not in RETRYABLE_STATUS_CODES


class TestFetchWithRetryMocked:
    """Mocked tests for fetch_with_retry."""

    @patch('openjobs.http_utils.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = fetch_with_retry('https://example.com')

        assert result == mock_response
        mock_get.assert_called_once()

    @patch('openjobs.http_utils.requests.get')
    def test_fetch_with_custom_headers(self, mock_get):
        """Test fetch with custom headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        custom_headers = {'Authorization': 'Bearer token'}
        fetch_with_retry('https://example.com', headers=custom_headers)

        mock_get.assert_called_with(
            'https://example.com',
            headers=custom_headers,
            timeout=15
        )


class TestFetchJsonWithRetryMocked:
    """Mocked tests for fetch_json_with_retry."""

    @patch('openjobs.http_utils.fetch_with_retry')
    def test_successful_json_fetch(self, mock_fetch):
        """Test successful JSON fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'key': 'value'}
        mock_fetch.return_value = mock_response

        result = fetch_json_with_retry('https://example.com')

        assert result == {'key': 'value'}

    @patch('openjobs.http_utils.fetch_with_retry')
    def test_json_fetch_http_error(self, mock_fetch):
        """Test JSON fetch with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_fetch.side_effect = requests.HTTPError(response=mock_response)

        result = fetch_json_with_retry('https://example.com')

        assert result == {}

    @patch('openjobs.http_utils.fetch_with_retry')
    def test_json_fetch_request_exception(self, mock_fetch):
        """Test JSON fetch with request exception."""
        mock_fetch.side_effect = requests.RequestException("Network error")

        result = fetch_json_with_retry('https://example.com')

        assert result == {}

    @patch('openjobs.http_utils.fetch_with_retry')
    def test_json_fetch_invalid_json(self, mock_fetch):
        """Test JSON fetch with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_fetch.return_value = mock_response

        result = fetch_json_with_retry('https://example.com')

        assert result == {}


class TestPostWithRetryMocked:
    """Mocked tests for post_with_retry."""

    @patch('openjobs.http_utils.requests.post')
    def test_successful_post(self, mock_post):
        """Test successful POST."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = post_with_retry('https://example.com', json={'data': 'test'})

        assert result == mock_response
        mock_post.assert_called_once()

    @patch('openjobs.http_utils.requests.post')
    def test_post_with_custom_headers(self, mock_post):
        """Test POST with custom headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        custom_headers = {'Authorization': 'Bearer token'}
        post_with_retry('https://example.com', headers=custom_headers)

        call_args = mock_post.call_args
        assert call_args[1]['headers'] == custom_headers


class TestPostJsonWithRetryMocked:
    """Mocked tests for post_json_with_retry."""

    @patch('openjobs.http_utils.post_with_retry')
    def test_successful_json_post(self, mock_post):
        """Test successful JSON POST."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'success'}
        mock_post.return_value = mock_response

        result = post_json_with_retry('https://example.com', json_body={'data': 'test'})

        assert result == {'result': 'success'}

    @patch('openjobs.http_utils.post_with_retry')
    def test_json_post_http_error(self, mock_post):
        """Test JSON POST with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.side_effect = requests.HTTPError(response=mock_response)

        result = post_json_with_retry('https://example.com')

        assert result == {}

    @patch('openjobs.http_utils.post_with_retry')
    def test_json_post_request_exception(self, mock_post):
        """Test JSON POST with request exception."""
        mock_post.side_effect = requests.RequestException("Network error")

        result = post_json_with_retry('https://example.com')

        assert result == {}

    @patch('openjobs.http_utils.post_with_retry')
    def test_json_post_invalid_json(self, mock_post):
        """Test JSON POST with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = post_json_with_retry('https://example.com')

        assert result == {}
