import logging
import math
from typing import Any

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.keyonimoveis.com.br"
API_ENDPOINT = f"{BASE_URL}/retornar-imoveis-disponiveis"
PAGE_SIZE = 20

CITY_CODE = 2
CITY_NAME = "Tubarão"
CITY_STATE = "SC"
CITY_URL = "tubarao"
CITY_STATE_URL = "sc"


class KeyOnImoveisScraper(AgencyScraper):
    name = "keyonimoveis"

    _HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": BASE_URL,
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
        page = 1
        total_pages = 1

        while page <= min(total_pages, self.max_pages):
            logger.info("[%s] Fetching page %d/%d", self.name, page, total_pages)

            data = self._fetch_page(page, query)
            if data is None:
                break

            if page == 1:
                total = data.get("quantidade", 0)
                total_pages = math.ceil(total / PAGE_SIZE) if total else 1
                logger.info("[%s] %d listings across %d page(s)", self.name, total, total_pages)

            listing_batch = data.get("lista", [])
            if not listing_batch:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for raw in listing_batch:
                prop = self._normalize(raw)
                if prop is not None:
                    properties.append(prop)

            page += 1

        logger.info("[%s] Done. %d properties collected.", self.name, len(properties))
        return properties

    def _fetch_page(self, page: int, query: SearchQuery) -> dict[str, Any] | None:
        payload = self._build_payload(page, query)
        try:
            resp = self.client._session.post(
                API_ENDPOINT,
                data=payload,
                timeout=self.config.timeout or 30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("[%s] Failed to fetch page %d: %s", self.name, page, exc)
            raise

    def _build_payload(self, page: int, query: SearchQuery) -> dict[str, Any]:
        return {
            "finalidade": "venda",
            "codigounidade": "",
            "codigocondominio": 0,
            "codigoproprietario": 0,
            "codigocaptador": 0,
            "codigosimovei": 0,
            "codigocidade": CITY_CODE,
            "codigoregiao": 0,
            "bairros[0][cidade]": "",
            "bairros[0][codigo]": "",
            "bairros[0][estado]": "",
            "bairros[0][estadoUrl]": "",
            "bairros[0][nome]": "Todos",
            "bairros[0][nomeUrl]": "todos-os-bairros",
            "bairros[0][regiao]": "",
            "endereco": "",
            "edificio": "",
            "numeroquartos": query.min_bedrooms or 0,
            "numerovagas": query.min_parking or 0,
            "numerobanhos": query.min_bathrooms or 0,
            "numerosuite": 0,
            "numerovaranda": 0,
            "numeroelevador": 0,
            "valorde": query.min_price or 0,
            "valorate": query.max_price or 0,
            "areade": query.min_area or 0,
            "areaate": query.max_area or 0,
            "areaexternade": 0,
            "areaexternaate": 0,
            "extras": "",
            "destaque": 0,
            "opcaoimovel": 0,
            "numeropagina": page,
            "numeroregistros": PAGE_SIZE,
            "ordenacao": "dataatualizacaodesc",
            "cidades[codigo]": CITY_CODE,
            "cidades[nome]": CITY_NAME,
            "cidades[estado]": CITY_STATE,
            "cidades[nomeUrl]": CITY_URL,
            "cidades[estadoUrl]": CITY_STATE_URL,
            "condominio[codigo]": 0,
            "condominio[nome]": "",
            "condominio[nomeUrl]": "todos-os-condominios",
        }

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        try:
            codigo = raw.get("codigo")
            url_amigavel = raw.get("url_amigavel", "")
            url_publica: str = raw.get("urlpublica") or ""
            if not url_publica and url_amigavel and codigo:
                url_publica = f"{BASE_URL}/imovel/{url_amigavel}/{codigo}"

            if not url_publica:
                logger.warning("[%s] Skipping listing %s — no URL", self.name, codigo)
                return None

            area_raw = raw.get("areaprincipal") or raw.get("areainterna")

            return Property(
                agency=self.name,
                title=raw.get("titulo", "").strip(),
                url=url_publica,
                price=parse_price(raw.get("valor")),
                area=parse_area(area_raw),
                bedrooms=safe_int(raw.get("numeroquartos")),
                bathrooms=safe_int(raw.get("numerobanhos")),
                parking=safe_int(raw.get("numerovagas")),
                neighborhood=raw.get("bairro") or None,
                city=raw.get("cidade") or None,
            )

        except Exception as exc:
            logger.warning("[%s] Failed to normalize listing %s: %s", self.name, raw.get("codigo"), exc)
            return None