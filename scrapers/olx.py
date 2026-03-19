"""
scrapers/olx.py

Scraper para o portal OLX (Focado na região de Tubarão/SC).
Extrai dados diretamente do bloco JSON do Next.js (__NEXT_DATA__) embutido no HTML,
garantindo velocidade sem precisar carregar o DOM completo.
"""

import json
import logging
import re
from typing import Any, Optional

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.olx.com.br/imoveis/venda/estado-sc/florianopolis-e-regiao/outras-cidades/tubarao"


class OlxScraper(AgencyScraper):
    name = "olx"

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        super().__init__(config=config, client=client)
        self._HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.olx.com.br/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        }
        self.client._session.headers.update(self._HEADERS)

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        page = 1

        while page <= self.max_pages:
            logger.info("[%s] A extrair página %d", self.name, page)

            html = self._fetch_page(page, query)
            if not html:
                break

            ads = self._extract_json_data(html)
            
            if not ads:
                logger.info("[%s] Sem anúncios na página %d — a parar.", self.name, page)
                break

            for raw_ad in ads:
                prop = self._normalize(raw_ad)
                if prop is not None:
                    properties.append(prop)

            page += 1

        logger.info("[%s] Concluído. %d imóveis recolhidos.", self.name, len(properties))
        return properties

    def _fetch_page(self, page: int, query: SearchQuery) -> Optional[str]:
        params = self._build_params(page, query)
        try:
            resp = self.client._session.get(
                BASE_URL,
                params=params,
                timeout=self.config.timeout or 30,
            )
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            logger.error("[%s] Falha ao extrair a página %d: %s", self.name, page, exc)
            return None

    def _build_params(self, page: int, query: SearchQuery) -> dict[str, Any]:
        """
        Traduz a SearchQuery para os parâmetros complexos do OLX.
        O OLX usa parâmetros repetidos para seleções múltiplas (ex: ros=2&ros=3).
        """
        params: dict[str, Any] = {"sf": 1}

        if page > 1:
            params["o"] = page

        if query.min_price is not None:
            params["ps"] = int(query.min_price)
        if query.max_price is not None:
            params["pe"] = int(query.max_price)

        if query.min_area is not None:
            params["ss"] = int(query.min_area)
        if query.max_area is not None:
            params["se"] = int(query.max_area)

        if query.min_bedrooms is not None:
            params["ros"] = [i for i in range(max(1, query.min_bedrooms), 6)]
            
        if query.min_bathrooms is not None:
            params["bas"] = [i for i in range(max(1, query.min_bathrooms), 6)]
            
        if query.min_parking is not None:
            params["gsp"] = [i for i in range(max(1, query.min_parking), 6)]

        return params

    def _extract_json_data(self, html: str) -> list[dict]:
        """
        O OLX injeta os dados da página num script JSON. Extrair isso evita
        fazer parse de HTML complexo.
        """
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if not match:
            logger.warning("[%s] __NEXT_DATA__ não encontrado. O site pode ter mudado a estrutura ou ativado o anti-bot.", self.name)
            return []

        try:
            data = json.loads(match.group(1))
            return data.get("props", {}).get("pageProps", {}).get("ads", [])
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.error("[%s] Erro ao descodificar JSON do __NEXT_DATA__: %s", self.name, exc)
            return []

    def _normalize(self, raw: dict[str, Any]) -> Optional[Property]:
        if not raw.get("subject") or not raw.get("url"):
            return None

        try:
            props = {p.get("name"): p.get("value") for p in raw.get("properties", [])}
            
            location = raw.get("location", {})

            return Property(
                agency=self.name,
                title=raw.get("subject", "").strip(),
                url=raw.get("url"),
                price=parse_price(raw.get("price")),
                area=parse_area(props.get("size")),
                bedrooms=safe_int(props.get("rooms")),
                bathrooms=safe_int(props.get("bathrooms")),
                parking=safe_int(props.get("garage_spaces")),
                neighborhood=location.get("neighborhood"),
                city=location.get("municipality") or location.get("city"),
            )

        except Exception as exc:
            logger.warning("[%s] Falha ao normalizar anúncio %s: %s", self.name, raw.get("listId"), exc)
            return None