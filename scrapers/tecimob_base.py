"""
scrapers/tecimob_base.py

Abstract base class for all Tecimob-platform scrapers.

All agencies running on the Gerenciar Imóveis / Tecimob SaaS backend share
the same API contract. This base class encapsulates that shared logic so
each agency scraper only needs to declare:

    - name
    - BASE_URL
    - API_ENDPOINT  (api-sites or api-sites2)
    - _HEADERS      (with the correct x-domain value)
    - optionally override _build_params() for non-standard agencies

Default quality filters (matching the project's target criteria) are applied
at the API request level so unnecessary listings are never downloaded:

    filter[transaction] = 1          (for sale only)
    filter[bedroom_gte] = 1          (at least 1 bedroom)
    filter[bathroom_gte] = 1         (at least 1 bathroom)
    filter[garage_gte] = 1           (at least 1 parking spot)
    filter[total_area_gte] = 50      (at least 50 m²)
    filter[price_lte] = 320000       (up to R$ 320,000)

These defaults mirror the project's stated objective:
    "list all houses/apartments with 1+ rooms, 1+ bathrooms, 1+ garage,
     at least 50/55 sqm, priced up to 320,000 reais"

Per-agency subclasses may override these via class-level attributes if needed.
"""

import logging
from abc import abstractmethod
from typing import Any, Optional

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

PAGE_SIZE = 21
DEFAULT_MIN_BEDROOMS: int = 1
DEFAULT_MIN_BATHROOMS: int = 1
DEFAULT_MIN_PARKING: int = 1
DEFAULT_MIN_AREA: float = 50.0
DEFAULT_MAX_PRICE: float = 320_000.0
CITY_SLUG: str = "tubarao-sc"


class TecimobScraper(AgencyScraper):
    BASE_URL: str
    API_ENDPOINT: str
    _HEADERS: dict[str, str]

    city_slug: str = CITY_SLUG
    default_sort: str = "-created_at,id"
    use_city_slug_filter: bool = True

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        super().__init__(config=config, client=client)
        self.client._session.headers.update(self._HEADERS)

    def scrape(self) -> list[Property]:
        properties: list[Property] = []
        page = 1
        total_pages = 1

        while page <= min(total_pages, self.max_pages):
            offset = (page - 1) * PAGE_SIZE + 1
            logger.info("[%s] Fetching page %d/%d (offset=%d)", self.name, page, total_pages, offset)

            data = self._fetch_page(offset)
            if not data:
                break

            if page == 1:
                pagination = data.get("meta", {}).get("pagination", {})
                total_pages = pagination.get("total_pages", 1)
                total = pagination.get("total", 0)
                logger.info("[%s] %d listings across %d page(s)", self.name, total, total_pages)

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

    def _fetch_page(self, offset: int) -> dict[str, Any] | None:
        params = self._build_params(offset)
        try:
            resp = self.client._session.get(
                self.API_ENDPOINT,
                params=params,
                timeout=self.config.timeout or 30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("[%s] Failed to fetch offset=%d: %s", self.name, offset, exc)
            return None

    def _build_params(self, offset: int) -> dict[str, Any]:
        params: dict[str, Any] = {
            "custom_query": "card",
            "sort": self.default_sort,
            "offset": offset,
            "limit": PAGE_SIZE,
            "with_grouped_condos": "true",
            "filter[transaction]": 1,
            "filter[bedroom_gte]": DEFAULT_MIN_BEDROOMS,
            "filter[bathroom_gte]": DEFAULT_MIN_BATHROOMS,
            "filter[garage_gte]": DEFAULT_MIN_PARKING,
            "filter[total_area_gte]": DEFAULT_MIN_AREA,
            "filter[price_lte]": DEFAULT_MAX_PRICE,
            "include": "subtype.type,user",
            "with_title": "true",
        }
        if self.use_city_slug_filter:
            params["filter[by_neighborhood_or_city_slug]"] = self.city_slug
        return params

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        try:
            slug = raw.get("url")
            if not slug:
                return None

            areas = raw.get("areas")
            if not isinstance(areas, dict):
                areas = {}
            area_block = areas.get("total_area") or areas.get("primary_area") or {}

            address_fmt: str = (raw.get("address") or {}).get("formatted", "")
            neighborhood, city = _split_address(address_fmt)

            rooms: dict = raw.get("rooms") or {}

            return Property(
                agency=self.name,
                title=(raw.get("title_formatted") or raw.get("meta_title") or "").strip(),
                url=f"{self.BASE_URL}/imovel/{slug}",
                price=parse_price(raw.get("price") or raw.get("total_price")),
                area=parse_area(area_block.get("value")),
                bedrooms=safe_int((rooms.get("bedroom") or {}).get("value")),
                bathrooms=safe_int((rooms.get("bathroom") or {}).get("value")),
                parking=safe_int((rooms.get("garage") or {}).get("value")),
                neighborhood=neighborhood,
                city=city,
            )
        except Exception as exc:
            logger.warning("[%s] Failed to normalize listing %s: %s", self.name, raw.get("id"), exc)
            return None

def _split_address(formatted: str) -> tuple[str | None, str | None]:
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