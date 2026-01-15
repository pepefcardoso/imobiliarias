from interfaces.i_scraper import IScraper
from interfaces.i_http_client import IHttpClient
from interfaces.i_parser import IParser
from interfaces.i_logger import ILogger
from domain.scraper_result import ScraperResult

class KeyOnScraper(IScraper):
    def __init__(self, url: str, client: IHttpClient, parser: IParser, logger: ILogger):
        self.url = url
        self._client = client
        self._parser = parser
        self._logger = logger

    def buscar_imoveis(self) -> ScraperResult:
        self._logger.info("Iniciando busca...", source="KeyOn")
        
        try:
            html_content = self._client.fetch(self.url, wait_selector="div.card")
            
            if not html_content:
                msg = "HTML vazio retornado ou timeout."
                self._logger.info(msg, source="KeyOn")
                return ScraperResult(erros=[msg])

            self._logger.info("Processando dados...", source="KeyOn")
            
            resultado = self._parser.parse(html_content)
            
            self._logger.info(
                f"Sucesso: {len(resultado.imoveis)} imóveis encontrados. {len(resultado.erros)} erros de parsing.", 
                source="KeyOn"
            )
            return resultado
            
        except Exception as e:
            self._logger.error("Erro fatal durante busca", exc=e, source="KeyOn")
            return ScraperResult(erros=[f"Erro fatal: {str(e)}"])