"""
infrastructure/http_client.py

Simple HTTP client for fetching static HTML pages and JSON endpoints.
Wraps the `requests` library with timeout, user-agent, and error handling.

Rules:
- No scraping logic here
- No parsing logic here
- Raise meaningful exceptions
"""

import logging
from typing import Any, Optional

import requests
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from config.settings import settings

logger = logging.getLogger(__name__)


class HttpClientError(Exception):

class HttpTimeoutError(HttpClientError):

class HttpStatusError(HttpClientError):
    def __init__(self, status_code: int, url: str) -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} received for URL: {url}")


class HttpConnectionError(HttpClientError):

class HttpClient:
    """
    Thin wrapper around `requests` for fetching static HTML or JSON endpoints.

    Prefer this client over the BrowserClient whenever the page does not
    require JavaScript rendering.

    Usage:
        client = HttpClient()
        html = client.get("https://agency.com/listings")
        data = client.get_json("https://agency.com/api/listings")
    """

    def __init__(
        self,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self._timeout = timeout or settings.request_timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": user_agent or settings.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )
        if headers:
            self._session.headers.update(headers)

    def get(self, url: str, params: Optional[dict[str, Any]] = None) -> str:
        """
        Performs a GET request and returns the response body as a string.

        Args:
            url:    Absolute URL to fetch.
            params: Optional query parameters dict.

        Returns:
            Response body as a decoded string.

        Raises:
            HttpTimeoutError:    If the request exceeds the configured timeout.
            HttpStatusError:     If the server returns a 4xx or 5xx status code.
            HttpConnectionError: If a network-level error occurs.
        """
        response = self._request("GET", url, params=params)
        return response.text

    def get_json(self, url: str, params: Optional[dict[str, Any]] = None) -> Any:
        """
        Performs a GET request and returns the response body parsed as JSON.

        Args:
            url:    Absolute URL to fetch.
            params: Optional query parameters dict.

        Returns:
            Parsed JSON (dict, list, etc.).

        Raises:
            HttpTimeoutError:    If the request exceeds the configured timeout.
            HttpStatusError:     If the server returns a 4xx or 5xx status code.
            HttpConnectionError: If a network-level error occurs.
            ValueError:          If the response body is not valid JSON.
        """
        response = self._request("GET", url, params=params)
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError(f"Response from {url} is not valid JSON: {exc}") from exc

    def close(self) -> None:
        """Closes the underlying requests session and releases resources."""
        self._session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Response:
        logger.debug("HTTP %s → %s (timeout=%ss)", method, url, self._timeout)
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                timeout=self._timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
        except Timeout as exc:
            logger.warning("Timeout fetching %s: %s", url, exc)
            raise HttpTimeoutError(f"Request timed out after {self._timeout}s: {url}") from exc
        except HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else 0
            logger.warning("HTTP %s error for %s: %s", status_code, url, exc)
            raise HttpStatusError(status_code, url) from exc
        except ConnectionError as exc:
            logger.warning("Connection error for %s: %s", url, exc)
            raise HttpConnectionError(f"Could not connect to {url}: {exc}") from exc
        except RequestException as exc:
            logger.warning("Request error for %s: %s", url, exc)
            raise HttpClientError(f"Unexpected request error for {url}: {exc}") from exc

        logger.debug("HTTP %s ← %s %s (%s bytes)", method, response.status_code, url, len(response.content))
        return response