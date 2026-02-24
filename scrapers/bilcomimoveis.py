"""
scrapers/bilcomimoveis.py
Scraper for Bilcom Imóveis (https://bilcomimoveis.com.br).
"""

import logging
from typing import Any

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://bilcomimoveis.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"
PAGE_SIZE = 21
CITY_SLUG = "tubarao-sc"

class BilcomImoveisScraper(AgencyScraper):
    """
    Scraper for Bilcom Imóveis — Tubarão/SC.
    Hits the Tecimob JSON API.
    """
    name = "bilcomimoveis"

    _HEADERS = {
        "x-domain": "bilcomimoveis.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }

    def __init__(self, config: AgencyConfig | None = None, client: HttpClient | None = None) -> None:
        super().__init__(config=config, client=client)
        self.client._session.headers.update(self._HEADERS)

    def scrape(self) -> list[Property]:
        properties: list[Property] = []
        page = 1
        total_pages = 1

        while page <= min(total_pages, self.max_pages):
            offset = (page - 1) * PAGE_SIZE + 1
            logger.info("[%s] Fetching page %d (offset=%d)", self.name, page, offset)
            
            data = self._fetch_page(offset)
            if not data: break

            if page == 1:
                pagination = data.get("meta", {}).get("pagination", {})
                total_pages = pagination.get("total_pages", 1)

            listings = data.get("data", [])
            for raw in listings:
                prop = self._normalize(raw)
                if prop: properties.append(prop)
            page += 1

        return properties

    def _fetch_page(self, offset: int) -> dict[str, Any] | None:
        params = {
            "custom_query": "card",
            "sort": "-is_price_shown,by_calculated_price,id",
            "offset": offset,
            "limit": PAGE_SIZE,
            "filter[transaction]": 1,
            "filter[by_neighborhood_or_city_slug]": CITY_SLUG,
            "include": "subtype.type,user",
            "with_title": "true",
        }
        resp = self.client._session.get(API_ENDPOINT, params=params)
        resp.raise_for_status()
        return resp.json()

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        try:
            slug = raw.get("url")
            if not slug: return None
            
            # Use total_area or primary_area [cite: 423]
            areas = raw.get("areas") or {}
            area_block = areas.get("total_area") or areas.get("primary_area") or {}
            
            # Map address parts using helper format similar to Sittuar
            address_fmt = (raw.get("address") or {}).get("formatted", "")
            neighborhood = address_fmt.split(" - ")[0] if " - " in address_fmt else None

            return Property(
                agency=self.name,
                title=raw.get("title_formatted", "").strip(),
                url=f"{BASE_URL}/comprar/{slug}",
                price=parse_price(raw.get("price")),
                area=parse_area(area_block.get("value")),
                bedrooms=safe_int((raw.get("rooms", {}).get("bedroom") or {}).get("value")),
                bathrooms=safe_int((raw.get("rooms", {}).get("bathroom") or {}).get("value")),
                parking=safe_int((raw.get("rooms", {}).get("garage") or {}).get("value")),
                neighborhood=neighborhood,
                city="Tubarão" # Hardcoded as per filter context
            )
        except Exception as e:
            logger.warning("[%s] Normalization error: %s", self.name, e)
            return None