import logging
from typing import Optional
from bs4 import BeautifulSoup

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int, parse_condo_fee
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

class ImogestaoScraper(AgencyScraper):
    """
    Base scraper for Imobiliárias using the Imogestão platform (Server-Side Rendered HTML).
    """
    BASE_URL: str
    
    DEFAULT_PARAMS: dict[str, str] = {
        "pretensao": "comprar",
        "cidade": "4218707" 
    }

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        page = 1

        while page <= self.max_pages:
            logger.info("[%s] Fetching page %d", self.name, page)
            html = self._fetch_page(page, query)
            
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.find_all("div", class_="block-imovel-box")

            if not cards:
                logger.info("[%s] Empty page %d — stopping.", self.name, page)
                break

            for card in cards:
                prop = self._normalize(card)
                if prop is not None:
                    properties.append(prop)

            next_page_link = soup.find("a", class_="page-link", string=str(page + 1))
            next_arrow = soup.find("a", class_="page-link", string="›")
            
            if not next_page_link and not next_arrow:
                logger.info("[%s] End of pagination reached at page %d.", self.name, page)
                break

            page += 1

        logger.info("[%s] Done. %d properties collected.", self.name, len(properties))
        return properties

    def _fetch_page(self, page: int, query: SearchQuery) -> Optional[str]:
        params = dict(self.DEFAULT_PARAMS)
        params["pagina"] = str(page)

        if query.min_price:
            params["valor_min"] = f"{query.min_price:_.0f}".replace("_", ".")
        if query.max_price:
            params["valor_max"] = f"{query.max_price:_.0f}".replace("_", ".")

        try:
            return self.client.get(f"{self.BASE_URL}/imoveis", params=params)
        except Exception as exc:
            logger.error("[%s] Failed to fetch page %d: %s", self.name, page, exc)
            return None

    def _normalize(self, card: BeautifulSoup) -> Optional[Property]:
        try:
            link_tag = card.find("a")
            if not link_tag:
                return None
            
            url = link_tag.get("href")
            if url and url.startswith("//"):
                url = "https:" + url
            elif url and url.startswith("/"):
                url = self.BASE_URL + url

            foto_div = card.find("div", class_="foto-imovel")
            image_url = None
            if foto_div and "style" in foto_div.attrs:
                style = foto_div["style"]
                if "url(" in style:
                    image_url = style.split("url('")[1].split("')")[0]
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url

            valor_div = card.find("div", class_="valor")
            price = parse_price(valor_div.text) if valor_div else None

            tipo_h3 = card.find("h3")
            property_type = tipo_h3.text.strip() if tipo_h3 else "Imóvel"

            local_h4 = card.find("h4")
            neighborhood, city = None, None
            if local_h4:
                parts = local_h4.text.split(",")
                if len(parts) >= 2:
                    neighborhood = parts[0].strip()
                    city = parts[1].strip()
                else:
                    city = parts[0].strip()

            title = f"{property_type} em {neighborhood}" if neighborhood else property_type

            bedrooms, bathrooms, parking, area = None, None, None, None
            info_ul = card.find("ul", class_="info-curta")
            
            if info_ul:
                for li in info_ul.find_all("li"):
                    li_text = li.text.strip()
                    li_html = str(li)
                    
                    if "fa-bed" in li_html:
                        bedrooms = safe_int(li_text)
                    elif "fa-shower" in li_html:
                        bathrooms = safe_int(li_text)
                    elif "fa-car" in li_html:
                        parking = safe_int(li_text)
                    elif "fa-object-group" in li_html:
                        area = parse_area(li_text)

            return Property(
                agency=self.name,
                title=title,
                url=url,
                price=price,
                area=area,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking=parking,
                condo_fee=parse_condo_fee(None, card.get_text(separator=" ")),
                neighborhood=neighborhood,
                city=city,
                image_url=image_url
            )
        except Exception as exc:
            logger.warning("[%s] Failed to parse card: %s", self.name, exc)
            return None