import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.settings import AgencyConfig, settings
from core.models import Property, SearchQuery
from infrastructure.http_client import HttpClient

logger = logging.getLogger(__name__)


class AgencyScraper(ABC):
    """
    Classe base abstrata para todos os scrapers de imobiliárias.
    Define as propriedades e métodos obrigatórios que cada scraper deve implementar.
    """
    name: str

    def __init__(
        self,
        config: Optional[AgencyConfig] = None,
        client: Optional[HttpClient] = None,
    ) -> None:
        self.config: AgencyConfig = config or self._resolve_config()
        self.client: HttpClient = client or HttpClient(
            timeout=self.config.timeout or settings.request_timeout
        )

    @abstractmethod
    def scrape(self, query: SearchQuery) -> list[Property]:
        """
        Método principal que deve ser implementado por cada scraper.
        
        Recebe a 'query' (SearchQuery) com os filtros do usuário e 
        deve retornar uma lista de objetos 'Property' normalizados.
        """
        pass

    @property
    def url(self) -> str:
        return self.config.url

    @property
    def max_pages(self) -> int:
        return self.config.max_pages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} url={self.url!r}>"

    def _resolve_config(self) -> AgencyConfig:
        for agency in settings.agencies:
            if agency.name == self.name:
                return agency

        raise ValueError(
            f"No AgencyConfig found in settings.agencies for scraper name={self.name!r}. "
            "Register the agency in config/settings.py before using this scraper."
        )