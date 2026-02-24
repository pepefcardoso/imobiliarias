"""
config/settings.py

Centralised runtime configuration for the aggregator.

All agency URLs, timeouts, client flags, and scraper limits live here.
No scraper or infrastructure module should hard-code configuration values.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgencyConfig:
    """Per-agency runtime configuration."""

    name: str
    url: str
    use_browser: bool = False
    max_pages: int = 10
    timeout: Optional[int] = None  # Override global timeout when set


@dataclass
class Settings:
    """
    Global application settings.

    All values have safe defaults. Override them as needed per environment.
    """

    # ------------------------------------------------------------------
    # HTTP / browser behaviour
    # ------------------------------------------------------------------

    request_timeout: int = 30
    """Default request timeout in seconds (HTTP and browser navigation)."""

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    """User-agent string sent in every request."""

    # ------------------------------------------------------------------
    # Scraper defaults
    # ------------------------------------------------------------------

    max_pages: int = 10
    """Global maximum number of pages to scrape per agency."""

    # ------------------------------------------------------------------
    # Concurrency (optional, not enabled by default)
    # ------------------------------------------------------------------

    max_workers: int = 10
    """Maximum number of concurrent threads when concurrency is enabled."""

    # ------------------------------------------------------------------
    # Agency registry
    # ------------------------------------------------------------------

    agencies: list[AgencyConfig] = field(default_factory=list)
    """
    List of agencies to scrape.

    Example:
        agencies=[
            AgencyConfig(name="bilcom", url="https://bilcom.com.br/imoveis"),
            AgencyConfig(name="example_js", url="https://js-agency.com/listings", use_browser=True),
        ]
    """


# ---------------------------------------------------------------------------
# Singleton — import and use this object everywhere
# ---------------------------------------------------------------------------

settings = Settings(
    request_timeout=30,
    max_pages=10,
    agencies=[
        # Register agencies here as scrapers are implemented.
        # AgencyConfig(name="bilcom", url="https://bilcom.com.br/imoveis"),
    ],
)