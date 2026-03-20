import json
import logging
import re
import unicodedata
from typing import Any, Optional

from config.settings import AgencyConfig
from core.models import Property, SearchQuery
from core.parsing_utils import parse_area, parse_price, safe_int
from infrastructure.http_client import HttpClient
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.chavesnamao.com.br"

class ChavesNaMaoScraper(AgencyScraper):
    name = "chavesnamao"

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        super().__init__(config=config, client=client)
        self.client._session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Host": "www.chavesnamao.com.br",
            "Referer": BASE_URL,
        })

    def scrape(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        page = 1
        
        while page <= self.max_pages:
            logger.info("[%s] A extrair a página %d", self.name, page)
            
            url, params = self._build_url_and_params(query, page)
            
            try:
                html = self.client.get(url, params=params)
                
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
                if not match:
                    logger.warning("[%s] Bloco de dados JSON não encontrado na página %d.", self.name, page)
                    break
                    
                data = json.loads(match.group(1))
                
                listings = []
                try:
                    page_props = data.get("props", {}).get("pageProps", {})
                    listings = page_props.get("initialState", {}).get("search", {}).get("result", [])
                    if not listings:
                        listings = page_props.get("imoveis", [])
                except Exception as e:
                    logger.error("[%s] Erro a navegar no JSON: %s", self.name, e)
                    break
                    
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

    def _build_url_and_params(self, query: SearchQuery, page: int) -> tuple[str, dict]:
        """
        Traduz os critérios de busca (SearchQuery) para o formato do ChavesNaMao.
        """
        base = f"{BASE_URL}/imoveis/a-venda"
        
        cidade = "sc-tubarao"
        if query.city:
            cidade_limpa = ''.join(c for c in unicodedata.normalize('NFD', query.city) if unicodedata.category(c) != 'Mn').lower()
            cidade_limpa = cidade_limpa.replace(' ', '-')
            cidade = f"sc-{cidade_limpa}"
            
        url = f"{base}/{cidade}"
        
        if query.min_bedrooms:
            if query.min_bedrooms == 1:
                url += "/1-quarto"
            elif query.min_bedrooms >= 5:
                url += "/5-ou-mais-quartos"
            else:
                url += f"/{query.min_bedrooms}-quartos"
                
        filtros = []
        if query.min_price: filtros.append(f"pmin:{int(query.min_price)}")
        if query.max_price: filtros.append(f"pmax:{int(query.max_price)}")
        if query.min_area: filtros.append(f"amin:{int(query.min_area)}")
        if query.max_area: filtros.append(f"amax:{int(query.max_area)}")
        if query.min_bathrooms: filtros.append(f"ban:{int(query.min_bathrooms)}")
        if query.min_parking: filtros.append(f"gar:{int(query.min_parking)}")
        
        params = {}
        if filtros:
            params["filtro"] = ",".join(filtros)
        
        if page > 1:
            params["pg"] = page
            
        return url, params

    def _normalize(self, raw: dict[str, Any]) -> Optional[Property]:
        """
        Mapeia um único imóvel do JSON para a tua estrutura 'Property'.
        """
        try:
            link = raw.get("link", "")
            full_url = link if link.startswith("http") else f"{BASE_URL}{link}"
            if not full_url or full_url == BASE_URL:
                return None
            
            price = raw.get("preco") or raw.get("valorVenda")
            area = raw.get("areaUtil") or raw.get("areaTotal")
            
            return Property(
                agency=self.name,
                title=raw.get("titulo", "Imóvel em destaque").strip(),
                url=full_url,
                price=parse_price(price),
                area=parse_area(area),
                bedrooms=safe_int(raw.get("quartos")),
                bathrooms=safe_int(raw.get("banheiros")),
                parking=safe_int(raw.get("vagas")),
                neighborhood=raw.get("bairro") or raw.get("bairroNome"),
                city=raw.get("cidade") or raw.get("cidadeNome"),
            )
        except Exception as exc:
            logger.warning("[%s] Erro ao tentar normalizar um imóvel: %s", self.name, exc)
            return None