from typing import Type, Dict, Tuple, Optional
from interfaces.i_http_client import IHttpClient
from interfaces.i_scraper import IScraper
from interfaces.i_logger import ILogger
from interfaces.i_parser import IParser
from services.pipeline import Pipeline
from pipeline_steps.steps import ParseStep
from pipeline_steps.caching_step import CachingFetchStep
from scrapers.pipeline_scraper_adapter import PipelineScraperAdapter

class ScraperFactory:
    _registry: Dict[str, Tuple[Type[IParser], Optional[str], str]] = {}

    def __init__(self, http_client: IHttpClient, logger: ILogger):
        self._client = http_client
        self._logger = logger
        self._cache_dir = "imobiliarias/cache_data"

    @classmethod
    def register(cls, key: str, parser_cls: Type[IParser], wait_selector: Optional[str], source_name: str):
        """
        Regista uma nova estratégia de scraping.
        :param key: A chave usada no settings.py (ex: 'keyon')
        :param parser_cls: A classe do parser (não a instância)
        :param wait_selector: O seletor CSS para o Selenium aguardar (ou None)
        :param source_name: Nome legível para logs
        """
        cls._registry[key] = (parser_cls, wait_selector, source_name)

    def create_scraper(self, key: str, url: str) -> IScraper:
        """
        Cria uma instância de scraper baseada na chave registada.
        """
        if key not in self._registry:
            raise ValueError(f"Scraper com a chave '{key}' não foi registado na Factory.")

        parser_cls, wait_selector, source_name = self._registry[key]

        step_fetch = CachingFetchStep(
            client=self._client,
            cache_dir=self._cache_dir,
            wait_selector=wait_selector
        )

        step_parse = ParseStep(parser_cls())

        pipeline = Pipeline([
            step_fetch,
            step_parse
        ])

        return PipelineScraperAdapter(
            pipeline=pipeline,
            initial_url=url,
            logger=self._logger,
            source_name=source_name
        )