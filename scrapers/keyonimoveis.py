import logging
import unicodedata
from typing import Any, Optional
from bs4 import BeautifulSoup

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://keyonimoveis.com.br"


class KeyOnImoveisScraper(AgencyScraper):
    name = "keyonimoveis"

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        page = 1

        while page <= self.max_pages:
            logger.info("[%s] A procurar a página %d", self.name, page)
            html = self._fetch_page(page, query)
            
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            
            cards = soup.find_all("a", class_="loop-property-archive")

            if not cards:
                logger.info("[%s] Nenhum imóvel encontrado na página %d — a parar.", self.name, page)
                break

            for card in cards:
                prop = self._normalize(card)
                if prop is not None:
                    properties.append(prop)

            page += 1

        logger.info("[%s] Concluído. %d imóveis recolhidos.", self.name, len(properties))
        return properties

    def _fetch_page(self, page: int, query: SearchQuery) -> Optional[str]:
        """
        Traduz o nosso SearchQuery genérico para os parâmetros do FacetWP usados pela KeyOn.
        """
        params: dict[str, Any] = {}

        if query.city:
            city_clean = ''.join(
                c for c in unicodedata.normalize('NFD', query.city) 
                if unicodedata.category(c) != 'Mn'
            ).lower()
            params["_property_location"] = city_clean.replace(" ", "-")

        if query.min_price or query.max_price:
            min_p = f"{query.min_price:.2f}" if query.min_price else "0.00"
            max_p = f"{query.max_price:.2f}" if query.max_price else "999999999.00"
            params["_property_price"] = f"{min_p},{max_p}"

        if query.min_bedrooms:
            params["_property_bedroom"] = f"{query.min_bedrooms}-999"

        if query.min_bathrooms:
            params["_property_bathroom"] = f"{query.min_bathrooms}-999"

        if page > 1:
            params["_paged"] = page

        try:
            return self.client.get(f"{BASE_URL}/comprar/", params=params)
        except Exception as exc:
            logger.error("[%s] Falha ao aceder à página %d: %s", self.name, page, exc)
            return None

    def _normalize(self, card: BeautifulSoup) -> Optional[Property]:
        """
        Extrai os dados do HTML do card e converte num objeto Property estandardizado.
        """
        try:
            url = card.get("href")
            if not url:
                return None

            img_tag = card.find("img")
            image_url = None
            if img_tag:
                image_url = img_tag.get("data-src") or img_tag.get("src")

            texts = card.find_all("p")
            title = texts[0].text.strip() if len(texts) > 0 else "Imóvel"
            price_raw = texts[1].text.strip() if len(texts) > 1 else None
            price = parse_price(price_raw)

            neighborhood = None
            city = None
            title_parts = [p.strip() for p in title.split("-")]
            if len(title_parts) >= 3:
                city = title_parts[-2]
                neighborhood = title_parts[-1]
            elif len(title_parts) == 2:
                city = title_parts[-1]

            area = None
            numeric_amenities = []
            
            feature_divs = card.find_all("div", class_="flex items-center gap-1")
            for f_div in feature_divs:
                text_val = f_div.text.strip()
                if not text_val:
                    continue
                    
                if "m²" in text_val.lower() or "m2" in text_val.lower():
                    area = parse_area(text_val)
                else:
                    val = safe_int(text_val)
                    if val is not None:
                        numeric_amenities.append(val)

            bedrooms = numeric_amenities[0] if len(numeric_amenities) > 0 else None
            bathrooms = numeric_amenities[1] if len(numeric_amenities) > 1 else None
            parking = numeric_amenities[2] if len(numeric_amenities) > 2 else None

            return Property(
                agency=self.name,
                title=title,
                url=url,
                price=price,
                area=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking=parking,
                neighborhood=neighborhood,
                city=city,
                image_url=image_url
            )

        except Exception as exc:
            logger.warning("[%s] Falha a normalizar o card: %s", self.name, exc)
            return None
