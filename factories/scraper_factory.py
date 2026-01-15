from interfaces.i_http_client import IHttpClient
from interfaces.i_scraper import IScraper
from interfaces.i_logger import ILogger

from scrapers.keyon import KeyOnScraper
from scrapers.qualalugar import QualAlugarScraper
from parsers.keyon_parser import KeyOnParser
from parsers.qualalugar_parser import QualAlugarParser

class ScraperFactory:
    def __init__(self, http_client: IHttpClient, logger: ILogger):
        self._client = http_client
        self._logger = logger

    def create_keyon_scraper(self, url: str) -> IScraper:
        parser = KeyOnParser()
        return KeyOnScraper(url, self._client, parser, self._logger)

    def create_qualalugar_scraper(self, url: str) -> IScraper:
        parser = QualAlugarParser()
        return QualAlugarScraper(url, self._client, parser, self._logger)