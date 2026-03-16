import logging
from typing import Any

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import safe_float, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.dubettuimoveis.com.br"
API_ENDPOINT = "https://api2.imobzi.app/v1/ac-wejt21830leut/site2/search/properties"

_BASE_PARAMS: dict[str, Any] = {
    "order": "lower_value",
    "direction": "asc",
    "availability": "buy",
    "search_type": "properties_map",
    "with_listing_broker_count": "true",
    "with_photos": "true",
}


class DubettuImoveisScraper(AgencyScraper):
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

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        cursor: str | None = None
        page = 0

        while page < self.max_pages:
            page += 1
            logger.info("[%s] Fetching page %d (cursor=%s)", self.name, page, cursor or "—")

            data = self._fetch_page(cursor, query)
            if data is None:
                break

            wrapper: dict = data.get("properties", {})
            listings: list[dict] = wrapper.get("properties", [])

            if not listings:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for raw in listings:
                prop = self._normalize(raw)
                if prop is not None:
                    properties.append(prop)

            cursor = wrapper.get("cursor")
            if not cursor:
                logger.info("[%s] No cursor — end of results.", self.name)
                break

        logger.info("[%s] Done. %d properties collected.", self.name, len(properties))
        return properties

    def _fetch_page(self, cursor: str | None, query: SearchQuery) -> dict[str, Any] | None:
        params: dict[str, Any] = dict(_BASE_PARAMS)
        if cursor:
            params["cursor"] = cursor
            
        if query.city:
            params["city"] = query.city
        if query.max_price:
            params["value_max"] = query.max_price
        if query.min_price:
            params["value_min"] = query.min_price
        
        if query.min_bedrooms:
            params["bedroom_gte"] = query.min_bedrooms
        if query.min_bathrooms:
            params["bathroom_gte"] = query.min_bathrooms
        if query.min_parking:
            params["garage_gte"] = query.min_parking
            
        if query.min_area:
            params["area_min"] = query.min_area
        if query.max_area:
            params["area_max"] = query.max_area

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
        try:
            site_url: str = raw.get("site_url", "")
            if not site_url:
                logger.warning("[%s] Skipping listing %s — no site_url", self.name, raw.get("code"))
                return None

            title: str = (raw.get("site_title") or "").strip()
            full_url = BASE_URL + site_url

            price = safe_float(raw.get("sale_value"))

            area = safe_float(raw.get("useful_area") or raw.get("area")) or None
            if area == 0.0:
                area = None

            return Property(
                agency=self.name,
                title=title,
                url=full_url,
                price=price,
                area=area,
                bedrooms=safe_int(raw.get("bedroom")),
                bathrooms=safe_int(raw.get("bathroom")),
                parking=safe_int(raw.get("garage")),
                neighborhood=raw.get("neighborhood") or None,
                city=raw.get("city") or None,
            )

        except Exception as exc:
            logger.warning(
                "[%s] Failed to normalize listing %s: %s",
                self.name,
                raw.get("code") or raw.get("db_id"),
                exc,
            )
            return None