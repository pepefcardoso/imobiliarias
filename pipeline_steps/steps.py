from typing import Any
from interfaces.i_pipeline_step import IPipelineStep
from interfaces.i_http_client import IHttpClient
from interfaces.i_parser import IParser
from interfaces.i_logger import ILogger
from domain.scraper_result import ScraperResult

class FetchStep(IPipelineStep):
    """
    Passo responsável por baixar o HTML.
    Substitui a chamada direta self._client.fetch()
    """
    def __init__(self, client: IHttpClient, wait_selector: str = None):
        self.client = client
        self.wait_selector = wait_selector

    def process(self, url: str) -> str:
        html = self.client.fetch(url, wait_selector=self.wait_selector)
        if not html:
            raise Exception("HTML vazio retornado ou erro de conexão.")
        return html

class ParseStep(IPipelineStep):
    """
    Passo responsável por transformar HTML em Objetos.
    Substitui a chamada self._parser.parse()
    """
    def __init__(self, parser: IParser):
        self.parser = parser

    def process(self, html_content: str) -> ScraperResult:
        return self.parser.parse(html_content)

class LogStep(IPipelineStep):
    """
    Exemplo de passo extra: Logar o que está acontecendo sem sujar a lógica.
    """
    def __init__(self, logger: ILogger, msg: str):
        self.logger = logger
        self.msg = msg

    def process(self, data: Any) -> Any:
        self.logger.info(self.msg)
        return data