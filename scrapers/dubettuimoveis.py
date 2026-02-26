"""
scrapers/dubettuimoveis.py

Scraper for Dubettu Imóveis (https://www.dubettuimoveis.com.br).

Strategy: Direct JSON API — no browser automation required.

The site is powered by the Imobzi SaaS backend.
Listings are fetched via a GET request to:

    https://api2.imobzi.app/v1/ac-wejt21830leut/site2/search/properties

Key request details:
  - Query   availability=buy
  - Query   search_type=properties_map
  - Query   city=Tubarão
  - Query   order=lower_value&direction=asc
  - Query   with_listing_broker_count=true&with_photos=true
  - Query   cursor=<pagination_token>   (absent on first request)

Pagination:
  The response includes a `cursor` field (JWT token) inside the nested
  `properties` object. Pass it as `?cursor=<token>` on subsequent requests.
  Stop when `cursor` is absent or the `properties` list is empty.

Price/area/rooms are returned as raw numbers (floats/ints), so no string
parsing is required — safe_float/safe_int are used only as a safety net.
"""

import logging
from typing import Any
from urllib.parse import urlencode

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import safe_float, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.dubettuimoveis.com.br"
API_ENDPOINT = "https://api2.imobzi.app/v1/ac-wejt21830leut/site2/search/properties"

# Fixed query parameters — filters are intentionally broad so every available
# for-sale listing in Tubarão is captured. Filtering happens at the API layer.
_BASE_PARAMS: dict[str, Any] = {
    "order": "lower_value",
    "direction": "asc",
    "availability": "buy",
    "search_type": "properties_map",
    "city": "Tubarão",
    "value_max": 300_000_000,
    "value_min": 100_000,
    "bedroom_gte": 1,
    "garage_gte": 1,
    "bathroom_gte": 1,
    "with_listing_broker_count": "true",
    "with_photos": "true",
}


class DubettuImoveisScraper(AgencyScraper):
    """
    Scraper for Dubettu Imóveis — Tubarão/SC.

    Hits the Imobzi JSON API used by the site's frontend.
    No JavaScript rendering required.

    Config example (config/settings.py):
        AgencyConfig(
            name="dubettuimoveis",
            url="https://www.dubettuimoveis.com.br",
            use_browser=False,
            max_pages=20,
        )
    """

    name = "dubettuimoveis"

    _HEADERS = {
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }

    def __init__(
        self,
        config: AgencyConfig | None = None,
        client: HttpClient | None = None,
    ) -> None:
        super().__init__(config=config, client=client)
        self.client._session.headers.update(self._HEADERS)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Property]:
        """
        Fetches all buy listings for Tubarão from the Dubettu / Imobzi API.

        Paginates via cursor token up to self.max_pages.
        Returns a list of normalized Property objects.
        """
        properties: list[Property] = []
        cursor: str | None = None
        page = 0

        while page < self.max_pages:
            page += 1
            logger.info("[%s] Fetching page %d (cursor=%s)", self.name, page, cursor or "—")

            data = self._fetch_page(cursor)
            if data is None:
                break

            # The API nests everything under a "properties" key
            wrapper: dict = data.get("properties", {})
            listings: list[dict] = wrapper.get("properties", [])

            if not listings:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for raw in listings:
                prop = self._normalize(raw)
                if prop is not None:
                    properties.append(prop)

            # Advance cursor; stop if absent (last page)
            cursor = wrapper.get("cursor")
            if not cursor:
                logger.info("[%s] No cursor returned — end of results.", self.name)
                break

        logger.info("[%s] Done. %d properties collected.", self.name, len(properties))
        return properties

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, cursor: str | None) -> dict[str, Any] | None:
        """
        GETs a single page from the API and returns parsed JSON.

        Raises on HTTP/network errors so the Aggregator can handle them.
        """
        params: dict[str, Any] = dict(_BASE_PARAMS)
        if cursor:
            params["cursor"] = cursor

        try:
            resp = self.client._session.get(
                API_ENDPOINT,
                params=params,
                timeout=self.config.timeout or 30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("[%s] Failed to fetch page (cursor=%s): %s", self.name, cursor, exc)
            raise

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        """
        Maps a single raw Imobzi listing dict to a normalized Property.

        Returns None (with a warning) if a required field is missing.

        Raw field reference (from API response):
          raw["sale_value"]     230000.0    (float, already numeric)
          raw["useful_area"]    46.0        (float, m²)
          raw["area"]           46.0        (float, total area)
          raw["bedroom"]        2           (int)
          raw["bathroom"]       1           (int)
          raw["garage"]         1           (int)
          raw["neighborhood"]   "Monte Castelo"
          raw["city"]           "Tubarão"
          raw["site_url"]       "/imovel/apartamento-2-quartos-..."
          raw["site_title"]     "Apartamento Torre Castelo a venda!"
        """
        try:
            site_url: str = raw.get("site_url", "")
            if not site_url:
                logger.warning(
                    "[%s] Skipping listing %s — no site_url",
                    self.name,
                    raw.get("code") or raw.get("db_id"),
                )
                return None

            title: str = (raw.get("site_title") or "").strip()
            full_url = BASE_URL + site_url

            # Price: already a float in the API response
            price = safe_float(raw.get("sale_value"))

            # Area: prefer useful_area (net internal area); fall back to area
            area = safe_float(raw.get("useful_area") or raw.get("area")) or None
            # Treat 0.0 as missing (some listings have area=0)
            if area == 0.0:
                area = None

            bedrooms = safe_int(raw.get("bedroom"))
            bathrooms = safe_int(raw.get("bathroom"))
            parking = safe_int(raw.get("garage"))

            neighborhood: str | None = raw.get("neighborhood") or None
            city: str | None = raw.get("city") or None

            return Property(
                agency=self.name,
                title=title,
                url=full_url,
                price=price,
                area=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking=parking,
                neighborhood=neighborhood,
                city=city,
            )

        except Exception as exc:
            logger.warning(
                "[%s] Failed to normalize listing %s: %s",
                self.name,
                raw.get("code") or raw.get("db_id"),
                exc,
            )
            return None