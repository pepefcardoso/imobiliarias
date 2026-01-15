from interfaces.i_scraper import IScraper
from domain.scraper_result import ScraperResult
from services.pipeline import Pipeline
from interfaces.i_logger import ILogger

class PipelineScraperAdapter(IScraper):
    """
    Um scraper genérico que configura e executa uma pipeline.
    Isso substitui a necessidade de criar uma classe específica para cada site
    apenas para colar código repetido.
    """
    def __init__(self, pipeline: Pipeline, initial_url: str, logger: ILogger, source_name: str):
        self.pipeline = pipeline
        self.url = initial_url
        self.logger = logger
        self.source_name = source_name

    def buscar_imoveis(self) -> ScraperResult:
        self.logger.info(f"Iniciando Pipeline para {self.source_name}...", source=self.source_name)
        
        try:
            resultado = self.pipeline.execute(self.url)
            
            if isinstance(resultado, ScraperResult):
                 self.logger.info(
                    f"Sucesso: {len(resultado.imoveis)} imóveis.", 
                    source=self.source_name
                )
                 return resultado
            else:
                return ScraperResult(erros=["A pipeline não retornou um ScraperResult válido."])

        except Exception as e:
            msg = f"Erro fatal na pipeline: {str(e)}"
            self.logger.error(msg, exc=e, source=self.source_name)
            return ScraperResult(erros=[msg])