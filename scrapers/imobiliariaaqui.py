"""
scrapers/imobiliariaaqui.py

Scraper for Imobiliária Aqui (https://imobiliariaaqui.com.br).

Strategy: Direct JSON API — no browser automation required.

Uses the Tecimob/Gerenciar Imóveis shared API:
    https://api-sites2.gerenciarimoveis-cf.com.br/api/properties

Key request details (captured from HAR):
  - Header  x-domain: imobiliariaaqui.com.br  (required — identifies the tenant)
  - Header  Origin:   https://imobiliariaaqui.com.br
  - Query   filter[transaction]=1              (1 = for sale)
  - Query   filter[by_neighborhood_or_city_slug]=tubarao-sc
  - Query   custom_query=card
  - Query   include=subtype.type,user
  - Query   with_title=true
  - Query   sort=-created_at,id
  - Query   offset=<1-based item offset>
  - Query   limit=<page size>
"""

import logging
from typing import Any

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://imobiliariaaqui.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"
PAGE_SIZE = 21
CITY_SLUG = "tubarao-sc"


class ImobiliariaAquiScraper(AgencyScraper):
    """
    Scraper for Imobiliária Aqui — Tubarão/SC.

    Hits the Tecimob JSON API used by the site's frontend.
    No JavaScript rendering required.

    Config example (config/settings.py):
        AgencyConfig(
            name="imobiliariaaqui",
            url="https://imobiliariaaqui.com.br",
            use_browser=False,
            max_pages=10,
        )
    """

    name = "imobiliariaaqui"

    _HEADERS = {
        "x-domain": "imobiliariaaqui.com.br",
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
        Fetches all sale listings for Tubarão/SC from the Imobiliária Aqui API.

        Paginates automatically up to self.max_pages.
        Returns a list of normalized Property objects.
        """
        properties: list[Property] = []
        page = 1
        total_pages = 1

        while page <= min(total_pages, self.max_pages):
            offset = (page - 1) * PAGE_SIZE + 1

            logger.info(
                "[%s] Fetching page %d/%d (offset=%d)",
                self.name, page, total_pages, offset,
            )

            data = self._fetch_page(offset)
            if data is None:
                break

            if page == 1:
                pagination = data.get("meta", {}).get("pagination", {})
                total_pages = pagination.get("total_pages", 1)
                total = pagination.get("total", 0)
                logger.info(
                    "[%s] %d listings found across %d page(s)",
                    self.name, total, total_pages,
                )

            listings = data.get("data", [])
            if not listings:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for raw in listings:
                prop = self._normalize(raw)
                if prop is not None:
                    properties.append(prop)

            page += 1

        logger.info("[%s] Done. %d properties collected.", self.name, len(properties))
        return properties

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, offset: int) -> dict[str, Any] | None:
        params = {
            "custom_query": "card",
            "sort": "-created_at,id",
            "offset": offset,
            "limit": PAGE_SIZE,
            "with_grouped_condos": "true",
            "filter[transaction]": 1,
            "filter[by_neighborhood_or_city_slug]": CITY_SLUG,
            "include": "subtype.type,user",
            "with_title": "true",
        }
        try:
            resp = self.client._session.get(
                API_ENDPOINT,
                params=params,
                timeout=self.config.timeout or 30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("[%s] Failed to fetch offset=%d: %s", self.name, offset, exc)
            raise

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        try:
            slug = raw.get("url", "")
            if not slug:
                logger.warning(
                    "[%s] Skipping listing %s — no url slug",
                    self.name,
                    raw.get("reference") or raw.get("id"),
                )
                return None

            title = (raw.get("title_formatted") or raw.get("meta_title") or "").strip()
            price = parse_price(raw.get("price") or raw.get("total_price"))

            # Prefer total_area; fall back to primary_area
            areas: dict = raw.get("areas") or {}
            area_block = areas.get("total_area") or areas.get("primary_area") or {}
            area = parse_area(area_block.get("value"))

            rooms: dict = raw.get("rooms") or {}
            bedrooms = safe_int((rooms.get("bedroom") or {}).get("value"))
            bathrooms = safe_int((rooms.get("bathroom") or {}).get("value"))
            parking = safe_int((rooms.get("garage") or {}).get("value"))

            # formatted looks like "Centro - Tubarão/SC"
            address_fmt: str = (raw.get("address") or {}).get("formatted", "")
            neighborhood, city = _split_address(address_fmt)

            return Property(
                agency=self.name,
                title=title,
                url=f"{BASE_URL}/comprar/{slug}",
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
                raw.get("reference") or raw.get("id"),
                exc,
            )
            return None


# ---------------------------------------------------------------------------
# Module-level helper
# ---------------------------------------------------------------------------

def _split_address(formatted: str) -> tuple[str | None, str | None]:
    """
    Splits the formatted address string into (neighborhood, city).

    Examples
    --------
    "Centro - Tubarão/SC"   → ("Centro", "Tubarão")
    "Tubarão/SC"            → (None, "Tubarão")
    ""                      → (None, None)
    """
    if not formatted:
        return None, None

    if " - " in formatted:
        left, right = formatted.split(" - ", 1)
        neighborhood: str | None = left.strip() or None
        city_part = right.strip()
    else:
        neighborhood = None
        city_part = formatted.strip()

    city: str | None = city_part.split("/")[0].strip() or None

    return neighborhood, city