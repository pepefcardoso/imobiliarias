from abc import ABC, abstractmethod
from domain.scraper_result import ScraperResult

class IParser(ABC):
    @abstractmethod
    def parse(self, html_content: str) -> ScraperResult:
        """
        Transforma HTML bruto em um ScraperResult (imóveis + erros).
        """
        pass