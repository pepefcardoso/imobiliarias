from abc import ABC, abstractmethod
from domain.scraper_result import ScraperResult

class IScraper(ABC):
    @abstractmethod
    def buscar_imoveis(self) -> ScraperResult:
        """
        Executa a busca e retorna um ScraperResult contendo imóveis e erros encontrados.
        """
        pass