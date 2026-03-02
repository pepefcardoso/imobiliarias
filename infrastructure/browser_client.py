"""
infrastructure/browser_client.py

Browser automation client using Playwright for JavaScript-rendered pages.

Use this client ONLY when the target page requires JavaScript execution.
Prefer HttpClient for all other cases — browser automation is slower and
heavier.

Rules:
- No scraping logic here
- No parsing logic here
- Raise meaningful exceptions
"""

import logging
from contextlib import contextmanager
from typing import Any, Generator, Optional

from config.settings import settings

logger = logging.getLogger(__name__)


class BrowserClientError(Exception):

class BrowserTimeoutError(BrowserClientError):

class BrowserNavigationError(BrowserClientError):

class BrowserClient:
    """
    Thin wrapper around Playwright for fetching JavaScript-rendered pages.

    Launches a headless Chromium instance on first use and closes it when
    the client is closed (or used as a context manager).

    Use ONLY when HttpClient is insufficient — JavaScript rendering is slow
    and resource-intensive. With 30–40 agencies, defaulting to browser
    automation would be a significant performance hit.

    Usage (context manager — recommended):
        with BrowserClient() as browser:
            html = browser.get("https://agency.com/listings")

    Usage (manual lifecycle):
        browser = BrowserClient()
        html = browser.get("https://agency.com/listings")
        browser.close()
    """

    def __init__(
        self,
        timeout_ms: Optional[int] = None,
        user_agent: Optional[str] = None,
        headless: bool = True,
    ) -> None:
        """
        Args:
            timeout_ms:  Navigation timeout in milliseconds.
                         Defaults to settings.request_timeout * 1000.
            user_agent:  Custom user-agent string.
                         Defaults to settings.user_agent.
            headless:    Run browser in headless mode. Default True.
        """
        self._timeout_ms = timeout_ms or (settings.request_timeout * 1000)
        self._user_agent = user_agent or settings.user_agent
        self._headless = headless
        self._playwright: Any = None
        self._browser: Any = None

    def get(self, url: str, wait_for: Optional[str] = None) -> str:
        """
        Navigates to *url* and returns the fully rendered HTML source.

        Args:
            url:      Absolute URL to navigate to.
            wait_for: Optional CSS selector to wait for before returning.
                      If None the client waits for the ``load`` event.

        Returns:
            Rendered HTML as a string.

        Raises:
            BrowserTimeoutError:    If navigation or element wait times out.
            BrowserNavigationError: If the page returns an HTTP error status.
            BrowserClientError:     For any other Playwright error.
        """
        with self._page() as page:
            self._navigate(page, url)

            if wait_for:
                self._wait_for_selector(page, url, wait_for)

            return page.content()

    def get_text(self, url: str, selector: str) -> str:
        """
        Navigates to *url* and returns the inner text of the first element
        matching *selector*.

        Useful for single-value extractions without downloading the full HTML.

        Raises:
            BrowserTimeoutError:    If navigation or selector wait times out.
            BrowserNavigationError: If the page returns an HTTP error status.
            BrowserClientError:     If the selector is not found.
        """
        with self._page() as page:
            self._navigate(page, url)
            self._wait_for_selector(page, url, selector)
            element = page.query_selector(selector)
            if element is None:
                raise BrowserClientError(f"Selector '{selector}' not found on {url}")
            return element.inner_text()

    def close(self) -> None:
        if self._browser is not None:
            try:
                self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def __enter__(self) -> "BrowserClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def _ensure_browser(self) -> None:
        if self._browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserClientError(
                "Playwright is not installed. "
                "Run `pip install playwright && playwright install chromium` to enable browser automation."
            ) from exc

        try:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self._headless)
            logger.debug("Playwright Chromium browser launched (headless=%s)", self._headless)
        except Exception as exc:
            raise BrowserClientError(f"Failed to launch browser: {exc}") from exc

    @contextmanager
    def _page(self) -> Generator[Any, None, None]:
        self._ensure_browser()
        context = self._browser.new_context(
            user_agent=self._user_agent,
            java_script_enabled=True,
        )
        page = context.new_page()
        page.set_default_timeout(self._timeout_ms)
        try:
            yield page
        finally:
            try:
                page.close()
                context.close()
            except Exception:
                pass

    def _navigate(self, page: Any, url: str) -> None:
        logger.debug("Browser GET → %s (timeout=%sms)", url, self._timeout_ms)
        try:
            response = page.goto(url, wait_until="load", timeout=self._timeout_ms)
        except Exception as exc:
            exc_str = str(exc).lower()
            if "timeout" in exc_str:
                raise BrowserTimeoutError(
                    f"Navigation timed out after {self._timeout_ms}ms: {url}"
                ) from exc
            raise BrowserNavigationError(f"Navigation failed for {url}: {exc}") from exc

        if response is not None and response.status >= 400:
            raise BrowserNavigationError(
                f"HTTP {response.status} received navigating to {url}"
            )

        logger.debug("Browser GET ← %s %s", response.status if response else "?", url)

    def _wait_for_selector(self, page: Any, url: str, selector: str) -> None:
        try:
            page.wait_for_selector(selector, timeout=self._timeout_ms)
        except Exception as exc:
            if "timeout" in str(exc).lower():
                raise BrowserTimeoutError(
                    f"Timed out waiting for selector '{selector}' on {url}"
                ) from exc
            raise BrowserClientError(
                f"Error waiting for selector '{selector}' on {url}: {exc}"
            ) from exc