"""
scrapers/keyonimoveis.py

Scraper for Key On Imóveis (https://www.keyonimoveis.com.br).

Strategy: Direct JSON API — no browser automation required.

The site loads listings via a POST to /retornar-imoveis-disponiveis,
returning structured JSON. This is significantly faster and more reliable
than HTML scraping or Playwright.

Pagination: controlled via `numeropagina` in the POST body.
Total count is returned in `quantidade`; page size is fixed at PAGE_SIZE.
"""

import logging
import math
from typing import Any

from config.settings import AgencyConfig
from core.models import Property
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.keyonimoveis.com.br"
API_ENDPOINT = f"{BASE_URL}/retornar-imoveis-disponiveis"

# Number of listings the API returns per page.
# Matches the `numeroregistros` param sent in the POST body.
PAGE_SIZE = 20

# City code for Tubarão/SC as used by the Unsoft backend.
CITY_CODE = 2
CITY_NAME = "Tubarão"
CITY_STATE = "SC"
CITY_URL = "tubarao"
CITY_STATE_URL = "sc"


class KeyOnImoveisScraper(AgencyScraper):
    """
    Scraper for Key On Imóveis — Tubarão/SC.

    Hits the internal JSON API used by the site's frontend.
    No JavaScript rendering required.

    Config example (config/settings.py):
        AgencyConfig(
            name="keyonimoveis",
            url="https://www.keyonimoveis.com.br",
            use_browser=False,
            max_pages=10,
        )
    """

    name = "keyonimoveis"

    # Headers required to be accepted by the Unsoft backend.
    # The server checks X-Requested-With to identify XHR calls.
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
        # Merge required headers into the shared session
        self.client._session.headers.update(self._HEADERS)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Property]:
        """
        Fetches all sale listings for Tubarão from the Key On API.

        Paginates automatically up to self.max_pages.
        Returns a list of normalized Property objects.
        """
        properties: list[Property] = []
        page = 1
        total_pages = 1  # Will be updated after the first response

        while page <= min(total_pages, self.max_pages):
            logger.info(
                "[%s] Fetching page %d/%d", self.name, page, total_pages
            )

            data = self._fetch_page(page)
            if data is None:
                break

            # Update total pages after the first successful response
            if page == 1:
                total = data.get("quantidade", 0)
                total_pages = math.ceil(total / PAGE_SIZE) if total else 1
                logger.info(
                    "[%s] %d listings found across %d page(s)",
                    self.name,
                    total,
                    total_pages,
                )

            listing_batch = data.get("lista", [])
            if not listing_batch:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for raw in listing_batch:
                prop = self._normalize(raw)
                if prop is not None:
                    properties.append(prop)

            page += 1

        logger.info(
            "[%s] Done. %d properties collected.", self.name, len(properties)
        )
        return properties

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_page(self, page: int) -> dict[str, Any] | None:
        """
        POSTs to the API for a single page and returns the parsed JSON.

        Returns None if the request fails or the response is not valid JSON.
        """
        payload = self._build_payload(page)
        try:
            data = self.client._session.post(
                API_ENDPOINT,
                data=payload,
                timeout=self.config.timeout or 30,
            )
            data.raise_for_status()
            return data.json()
        except Exception as exc:
            # Let the Aggregator handle retries/logging at a higher level,
            # but log here so individual page failures are traceable.
            logger.error(
                "[%s] Failed to fetch page %d: %s", self.name, page, exc
            )
            raise

    def _build_payload(self, page: int) -> dict[str, Any]:
        """
        Constructs the form-encoded POST body for a given page.

        All parameters are derived from the AgencyConfig URL and the
        known Tubarão city constants. Filter values are left open
        (no price/area/bedroom constraints) so every available listing
        is collected. Filtering is left to the API layer.
        """
        return {
            "finalidade": "venda",
            "codigounidade": "",
            "codigocondominio": 0,
            "codigoproprietario": 0,
            "codigocaptador": 0,
            "codigosimovei": 0,
            "codigocidade": CITY_CODE,
            "codigoregiao": 0,
            # Neighbourhood: "all" — represented as empty values with the
            # sentinel nomeUrl the API recognises.
            "bairros[0][cidade]": "",
            "bairros[0][codigo]": "",
            "bairros[0][estado]": "",
            "bairros[0][estadoUrl]": "",
            "bairros[0][nome]": "Todos",
            "bairros[0][nomeUrl]": "todos-os-bairros",
            "bairros[0][regiao]": "",
            "endereco": "",
            "edificio": "",
            # No minimum bedroom/bathroom/parking filters → capture all
            "numeroquartos": 0,
            "numerovagas": 0,
            "numerobanhos": 0,
            "numerosuite": 0,
            "numerovaranda": 0,
            "numeroelevador": 0,
            # No price/area filters → capture all
            "valorde": 0,
            "valorate": 0,
            "areade": 0,
            "areaate": 0,
            "areaexternade": 0,
            "areaexternaate": 0,
            "extras": "",
            "destaque": 0,
            "opcaoimovel": 0,
            # Pagination
            "numeropagina": page,
            "numeroregistros": PAGE_SIZE,
            "ordenacao": "dataatualizacaodesc",
            # City object
            "cidades[codigo]": CITY_CODE,
            "cidades[nome]": CITY_NAME,
            "cidades[estado]": CITY_STATE,
            "cidades[nomeUrl]": CITY_URL,
            "cidades[estadoUrl]": CITY_STATE_URL,
            # Condominium: all
            "condominio[codigo]": 0,
            "condominio[nome]": "",
            "condominio[nomeUrl]": "todos-os-condominios",
        }

    def _normalize(self, raw: dict[str, Any]) -> Property | None:
        """
        Maps a single raw API listing dict to a normalized Property.

        Returns None and logs a warning if a required field is missing
        or the listing cannot be processed.
        """
        try:
            codigo = raw.get("codigo")
            url_amigavel = raw.get("url_amigavel", "")

            # Prefer the explicit public URL if the API already provides it;
            # fall back to constructing it from slug + ID (the standard pattern).
            url_publica: str = raw.get("urlpublica") or ""
            if not url_publica and url_amigavel and codigo:
                url_publica = f"{BASE_URL}/imovel/{url_amigavel}/{codigo}"

            if not url_publica:
                logger.warning(
                    "[%s] Skipping listing %s — could not determine URL",
                    self.name,
                    codigo,
                )
                return None

            # area: prefer areaprincipal (internal area in m²)
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
            logger.warning(
                "[%s] Failed to normalize listing %s: %s",
                self.name,
                raw.get("codigo"),
                exc,
            )
            return None