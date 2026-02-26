"""
scrapers/carlosmarques.py
Scraper para Carlos Marques Corretor (https://carlosmarquescorretor.com.br).
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

BASE_URL = "https://carlosmarquescorretor.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"
PAGE_SIZE = 21
CITY_SLUG = "tubarao-sc"

class CarlosMarquesScraper(AgencyScraper):
    """
    Scraper para Carlos Marques Corretor — Tubarão/SC.
    Consome a API JSON da plataforma Tecimob.
    """
    name = "carlosmarques"

    # O cabeçalho x-domain é obrigatório para esta API identificar a imobiliária
    _HEADERS = {
        "x-domain": "carlosmarquescorretor.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }

    def __init__(self, config: AgencyConfig | None = None, client: HttpClient | None = None) -> None:
        super().__init__(config=config, client=client)
        # Injeta os headers necessários na sessão do cliente HTTP
        self.client._session.headers.update(self._HEADERS)

    def scrape(self) -> list[Property]:
        properties: list[Property] = []
        page = 1
        total_pages = 1

        while page <= min(total_pages, self.max_pages):
            # O offset é baseado em itens (ex: 1, 22, 43...)
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
            "sort": "-created_at,id",
            "offset": offset,
            "limit": PAGE_SIZE,
            "filter[transaction]": 1,  # 1 = Venda
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
        """Mapeia os dados brutos da API para o modelo Property."""
        try:
            slug = raw.get("url")
            if not slug: 
                return None
            
            # Áreas: Prefere total_area, senão usa primary_area
            areas = raw.get("areas") or {}
            area_block = areas.get("total_area") or areas.get("primary_area") or {}
            
            # Endereço: Extrai bairro e cidade do campo 'formatted' (ex: "Morrotes - Tubarão/SC")
            address_fmt = (raw.get("address") or {}).get("formatted", "")
            neighborhood, city = self._split_address(address_fmt)

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
                city=city
            )
        except Exception as e:
            logger.warning("[%s] Erro de normalização no imóvel %s: %s", self.name, raw.get("id"), e)
            return None

    def _split_address(self, formatted: str) -> tuple[str | None, str | None]:
        """Auxiliar para separar 'Bairro - Cidade/UF'."""
        if not formatted: return None, None
        
        neighborhood = None
        city = None
        
        if " - " in formatted:
            parts = formatted.split(" - ")
            neighborhood = parts[0].strip()
            city_part = parts[1]
        else:
            city_part = formatted
            
        if "/" in city_part:
            city = city_part.split("/")[0].strip()
            
        return neighborhood, city