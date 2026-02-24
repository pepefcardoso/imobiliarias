"""
scrapers/base.py

Abstract base class for all agency scrapers.

Rules:
- Each concrete scraper must define a `name` class attribute
- Each concrete scraper must implement `scrape() -> list[Property]`
- No cross-dependency between scrapers
- Scrapers receive their HTTP/browser client and configuration at construction time
- No parsing logic here — only the contract
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.settings import AgencyConfig, settings
from core.models import Property
from infrastructure.http_client import HttpClient

logger = logging.getLogger(__name__)


class AgencyScraper(ABC):
    """
    Abstract base class for all agency scrapers.

    Each agency gets its own concrete subclass in scrapers/<agency_name>.py.

    Subclasses must:
        1. Set the `name` class attribute (used in logging and Property.agency)
        2. Implement `scrape() -> list[Property]`
        3. Use `self.client` for HTTP requests
        4. Use `self.config` for per-agency settings (url, max_pages, timeout)
        5. Use shared utilities from `core.parsing_utils` — never duplicate logic

    Example:
        class ExampleAgencyScraper(AgencyScraper):
            name = "example"

            def scrape(self) -> list[Property]:
                html = self.client.get(self.config.url)
                return self._parse(html)
    """

    #: Unique lowercase identifier for the agency.
    #: Must be set by every concrete subclass.
    name: str

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        """
        Args:
            config: Per-agency configuration (url, max_pages, timeout, etc.).
                    If omitted, the scraper looks itself up in settings.agencies
                    by matching `self.name`.
            client: HTTP client instance to use for requests.
                    If omitted, a default HttpClient is created using the
                    agency timeout (or the global request_timeout).
        """
        self.config: AgencyConfig = config or self._resolve_config()
        self.client: HttpClient = client or HttpClient(
            timeout=self.config.timeout or settings.request_timeout
        )

    # ------------------------------------------------------------------
    # Abstract interface — must be implemented by every scraper
    # ------------------------------------------------------------------

    @abstractmethod
    def scrape(self) -> list[Property]:
        """
        Fetches and returns all normalized property listings for this agency.

        Responsibilities:
            - Fetch one or more pages from the agency website
            - Parse listing cards / JSON responses
            - Normalize raw values using core.parsing_utils helpers
            - Return a list of fully populated Property objects

        Pagination:
            Respect `self.config.max_pages` to cap the number of pages fetched.

        Error handling:
            Raise meaningful exceptions — do NOT silently swallow errors.
            The Aggregator is responsible for catching and logging failures.

        Returns:
            list[Property]: Normalized listings. Empty list if none found.
        """

    # ------------------------------------------------------------------
    # Helpers available to all scrapers
    # ------------------------------------------------------------------

    @property
    def url(self) -> str:
        """Convenience shortcut for the agency's base URL."""
        return self.config.url

    @property
    def max_pages(self) -> int:
        """Maximum pages to scrape for this agency."""
        return self.config.max_pages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} url={self.url!r}>"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_config(self) -> AgencyConfig:
        """
        Looks up this scraper's AgencyConfig from the global settings registry.

        Raises:
            ValueError: If no matching config is found in settings.agencies.
        """
        for agency in settings.agencies:
            if agency.name == self.name:
                return agency

        raise ValueError(
            f"No AgencyConfig found in settings.agencies for scraper name={self.name!r}. "
            "Register the agency in config/settings.py before using this scraper."
        )