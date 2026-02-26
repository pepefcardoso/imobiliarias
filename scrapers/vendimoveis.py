"""
scrapers/vendimoveis.py
Scraper para Vendimoveis (https://vendimoveis.com.br).
Estratégia: API JSON Direta (Plataforma Tecimob).
"""

import logging
from typing import Any

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://vendimoveis.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"
PAGE_SIZE = 21
CITY_SLUG = "tubarao-sc"

class VendimoveisScraper(AgencyScraper):
    """
    Scraper para Vendimoveis — Tubarão/SC.
    Consome a API JSON interna da plataforma Tecimob.
    """
    name = "vendimoveis"

    _HEADERS = {
        "x-domain": "vendimoveis.com.br",
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
            logger.info("[%s] A procurar página %d (offset=%d)", self.name, page, offset)
            
            data = self._fetch_page(offset)
            if not data: 
                break

            if page == 1:
                pagination = data.get("meta", {}).get("pagination", {})
                total_pages = pagination.get("total_pages", 1)

            listings = data.get("data", [])
            for raw in listings:
                prop = self._normalize(raw)
                if prop: 
                    properties.append(prop)
            page += 1

        return properties

    def _fetch_page(self, offset: int) -> dict[str, Any] | None:
        """Faz o pedido GET à API com os filtros de Tubarão e Venda."""
        params = {
            "custom_query": "card",
            "sort": "-is_price_shown,-calculated_price,id",
            "offset": offset,
            "limit": PAGE_SIZE,
            "filter[transaction]": 1,
            "filter[by_neighborhood_or_city_slug]": CITY_SLUG,
            "include": "subtype.type,user",
            "with_title": "true",
        }
        try:
            resp = self.client._session.get(API_ENDPOINT, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("[%s] Erro ao procurar página (offset %d): %s", self.name, offset, e)
            return None

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        """Converte o dicionário bruto da API no modelo Property."""
        try:
            slug = raw.get("url")
            if not slug: 
                return None
            
            areas = raw.get("areas") or {}
            area_block = areas.get("total_area") or areas.get("primary_area") or {}
            
            address_fmt = (raw.get("address") or {}).get("formatted", "")
            neighborhood, city = _split_address(address_fmt)

            rooms = raw.get("rooms") or {}

            return Property(
                agency=self.name,
                title=raw.get("title_formatted", "").strip(),
                url=f"{BASE_URL}/comprar/{slug}",
                price=parse_price(raw.get("price")),
                area=parse_area(area_block.get("value")),
                bedrooms=safe_int((rooms.get("bedroom") or {}).get("value")),
                bathrooms=safe_int((rooms.get("bathroom") or {}).get("value")),
                parking=safe_int((rooms.get("garage") or {}).get("value")),
                neighborhood=neighborhood,
                city=city or "Tubarão"
            )
        except Exception as e:
            logger.warning("[%s] Erro de normalização: %s", self.name, e)
            return None

def _split_address(formatted: str) -> tuple[str | None, str | None]:
    """Helper para separar bairro e cidade a partir da string formatada."""
    if not formatted:
        return None, None

    if " - " in formatted:
        left, right = formatted.split(" - ", 1)
        neighborhood = left.strip() or None
        city_part = right.strip()
    else:
        neighborhood = None
        city_part = formatted.strip()

    city = city_part.split("/")[0].strip() or None
    return neighborhood, city