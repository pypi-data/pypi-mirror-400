"""
OpenJobs HTTP Utilities - Resilient HTTP requests with retry logic
"""

import logging

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# Default headers for all requests
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _should_retry(exception: BaseException) -> bool:
    """
    Determine if an exception should trigger a retry.

    Retries on:
    - Connection errors
    - Timeouts
    - Chunked encoding errors
    - Rate limits (429)
    - Server errors (500, 502, 503, 504)
    """
    if isinstance(exception, (
        requests.ConnectionError,
        requests.Timeout,
        requests.exceptions.ChunkedEncodingError
    )):
        return True

    if isinstance(exception, requests.HTTPError):
        if exception.response is not None:
            return exception.response.status_code in RETRYABLE_STATUS_CODES

    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(_should_retry),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def fetch_with_retry(url: str, headers: dict = None, timeout: int = 15) -> requests.Response:
    """
    Fetch URL with automatic retry on transient failures.

    Retries up to 3 times with exponential backoff (2s, 4s, 8s) on:
    - Connection errors
    - Timeouts
    - Rate limits (429)
    - Server errors (500, 502, 503, 504)

    Args:
        url: URL to fetch
        headers: Optional headers dict (defaults to DEFAULT_HEADERS)
        timeout: Request timeout in seconds (default 15)

    Returns:
        Response object

    Raises:
        requests.RequestException: After all retries exhausted
    """
    if headers is None:
        headers = DEFAULT_HEADERS

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def fetch_json_with_retry(url: str, headers: dict = None, timeout: int = 15) -> dict:
    """
    Fetch URL and parse JSON with automatic retry.

    Args:
        url: URL to fetch
        headers: Optional headers dict
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON as dict, or empty dict on failure
    """
    try:
        response = fetch_with_retry(url, headers=headers, timeout=timeout)
        return response.json()
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        logger.warning(f"HTTP {status} fetching {url}")
        return {}
    except requests.RequestException as e:
        logger.warning(f"Request failed for {url}: {e}")
        return {}
    except ValueError as e:
        logger.warning(f"JSON decode error for {url}: {e}")
        return {}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(_should_retry),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def post_with_retry(url: str, json: dict = None, headers: dict = None, timeout: int = 60) -> requests.Response:
    """
    POST to URL with automatic retry on transient failures.

    Args:
        url: URL to POST to
        json: JSON body to send
        headers: Optional headers dict
        timeout: Request timeout in seconds (default 60)

    Returns:
        Response object

    Raises:
        requests.RequestException: After all retries exhausted
    """
    if headers is None:
        headers = DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"

    response = requests.post(url, json=json, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def post_json_with_retry(url: str, json_body: dict = None, headers: dict = None, timeout: int = 60) -> dict:
    """
    POST to URL and parse JSON response with automatic retry.

    Args:
        url: URL to POST to
        json_body: JSON body to send
        headers: Optional headers dict
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON as dict, or empty dict on failure
    """
    try:
        response = post_with_retry(url, json=json_body, headers=headers, timeout=timeout)
        return response.json()
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        logger.warning(f"HTTP {status} POSTing to {url}")
        return {}
    except requests.RequestException as e:
        logger.warning(f"POST request failed for {url}: {e}")
        return {}
    except ValueError as e:
        logger.warning(f"JSON decode error for {url}: {e}")
        return {}
