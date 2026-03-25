import json
import logging
import unicodedata
from typing import Any, Optional

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.chavesnamao.com.br"
API_URL = f"{BASE_URL}/api/realestate/listing/items/premiumList/"

class ChavesNaMaoScraper(AgencyScraper):
    name = "chavesnamao"

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        super().__init__(config=config, client=client)
        self.client._session.headers.update({
            "Accept": "application/json",
            "Host": "www.chavesnamao.com.br",
            "Referer": BASE_URL,
        })

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        page = 1
        
        while page <= self.max_pages:
            logger.info("[%s] A extrair a página %d via API", self.name, page)
            
            params = self._build_api_params(query, page)
            
            try:
                data = self.client.get_json(API_URL, params=params)
                
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.error("[%s] A API retornou um texto inesperado: %s", self.name, data[:250])
                        break
                
                if not data or not isinstance(data, dict):
                    logger.warning("[%s] Formato de dados inválido recebido da API.", self.name)
                    break

                listings = data.get("items", [])
                
                if not listings:
                    logger.info("[%s] Nenhum imóvel encontrado na página %d — a parar.", self.name, page)
                    break
                    
                for raw in listings:
                    prop = self._normalize(raw)
                    if prop is not None:
                        properties.append(prop)
                        
                page += 1
                
            except Exception as exc:
                logger.error("[%s] Erro na página %d: %s", self.name, page, exc)
                break
                
        logger.info("[%s] Concluído. %d imóveis recolhidos.", self.name, len(properties))
        return properties

    def _build_api_params(self, query: SearchQuery, page: int) -> dict:
        """
        Monta o objeto JSON 'searchParams' idêntico ao que o front-end do site envia.
        """
        cidade = "sc-tubarao"
        if query.city:
            cidade_limpa = ''.join(c for c in unicodedata.normalize('NFD', query.city) if unicodedata.category(c) != 'Mn').lower()
            cidade_limpa = cidade_limpa.replace(' ', '-')
            cidade = f"sc-{cidade_limpa}"
            
        search_params = {
            "viewport": "desktop",
            "level1": "imoveis-a-venda",
            "level2": cidade
        }
        
        if query.min_bedrooms:
            if query.min_bedrooms == 1:
                search_params["level3"] = "1-quarto"
            elif query.min_bedrooms >= 5:
                search_params["level3"] = "5-ou-mais-quartos"
            else:
                search_params["level3"] = f"{query.min_bedrooms}-quartos"
                
        filtros = []
        if query.min_price: filtros.append(f"pmin:{int(query.min_price)}")
        if query.max_price: filtros.append(f"pmax:{int(query.max_price)}")
        if query.min_area: filtros.append(f"amin:{int(query.min_area)}")
        if query.max_area: filtros.append(f"amax:{int(query.max_area)}")
        if query.min_bathrooms: filtros.append(f"ban:{int(query.min_bathrooms)}")
        if query.min_parking: filtros.append(f"gar:{int(query.min_parking)}")
        
        if filtros:
            search_params["filtro"] = ",".join(filtros)
            
        if page > 1:
            search_params["pg"] = str(page)
            
        return {"searchParams": json.dumps(search_params, separators=(',', ':'))}

    def _normalize(self, raw: dict[str, Any]) -> Optional[Property]:
        """
        Mapeia os campos exatos do novo payload JSON da API.
        """
        try:
            link = raw.get("url", "")
            if not link:
                return None
            full_url = link if link.startswith("http") else f"{BASE_URL}{link}"
            
            prices = raw.get("prices", {})
            price = prices.get("rawPrice") or prices.get("main")
            
            area_obj = raw.get("area", {})
            area = area_obj.get("useful") or area_obj.get("total")
            
            image_url = None
            pictures = raw.get("pictures", {})
            if isinstance(pictures, dict):
                partial_url = pictures.get("featured")
                if not partial_url and pictures.get("list"):
                    partial_url = pictures.get("list")[0]
                
                if partial_url:
                    if not partial_url.startswith("http"):
                        image_url = f"https://www.chavesnamao.com.br/imn/0400X0262/N/60/imoveis/{partial_url}"
                    else:
                        image_url = partial_url

            location = raw.get("location", {})
            bairro = location.get("neighborhood", {}).get("name")
            cidade = location.get("city", {}).get("name")

            bedrooms = raw.get("bedrooms", {}).get("count")
            bathrooms = raw.get("bathrooms", {}).get("count")
            parking = raw.get("garages", {}).get("count")

            return Property(
                agency=self.name,
                title=(raw.get("title") or "Imóvel em destaque").strip(),
                url=full_url,
                price=parse_price(price),
                area=parse_area(area),
                bedrooms=safe_int(bedrooms),
                bathrooms=safe_int(bathrooms),
                parking=safe_int(parking),
                neighborhood=bairro,
                city=cidade,
                image_url=image_url,
            )
        except Exception as exc:
            logger.warning("[%s] Erro ao tentar normalizar um imóvel: %s", self.name, exc)
            return None