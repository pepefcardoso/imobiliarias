import pandas as pd
from config.settings import AppConfig
from infrastructure.selenium_client import SeleniumClient
from services.scraper_manager import ScraperManager
from factories.scraper_factory import ScraperFactory
from services.logger import StructuredLogger
from repositories.imovel_repository import ImovelRepository
from services.agregador_use_case import AgregadorUseCase
from services.data_exporter import DataExporter
from parsers.keyon_parser import KeyOnParser
from parsers.qualalugar_parser import QualAlugarParser
from parsers.bilcom_parser import BilcomParser

def configurar_scrapers(manager: ScraperManager, logger: StructuredLogger):
    client = SeleniumClient(headless=True)
    factory = ScraperFactory(client, logger)

    ScraperFactory.register(
        key='keyon', 
        parser_cls=KeyOnParser, 
        wait_selector="div.card", 
        source_name="KeyOn"
    )
    
    ScraperFactory.register(
        key='qualalugar', 
        parser_cls=QualAlugarParser, 
        wait_selector=None, 
        source_name="QualAlugar"
    )

    ScraperFactory.register(
        key='bilcom', 
        parser_cls=BilcomParser, 
        wait_selector="address",
        source_name="Bilcom"
    )

    for key, config in AppConfig.SCRAPERS.items():
        if config.enabled:
            try:
                logger.info(f"Configurando scraper: {config.name}")
                scraper = factory.create_scraper(key, config.url)
                manager.adicionar_scraper(scraper)
            except ValueError as e:
                logger.error(f"Erro na configuração do scraper '{key}':", exc=e)

def executar_agregador() -> pd.DataFrame:
    """
    Ponto de entrada (Composition Root).
    """
    logger = StructuredLogger()
    manager = ScraperManager()
    repository = ImovelRepository()
    
    configurar_scrapers(manager, logger)

    use_case = AgregadorUseCase(manager, repository, logger)
    
    lista_imoveis = use_case.executar()
    
    return DataExporter.para_dataframe(lista_imoveis)

if __name__ == "__main__":
    df_resultado = executar_agregador()
    
    if not df_resultado.empty:
        print("\n--- Resultados Unificados (Terminal) ---")
        cols_desejadas = ["Imobiliaria", "Bairro", "Preco", "Titulo"]
        cols_finais = [c for c in cols_desejadas if c in df_resultado.columns]
        print(df_resultado[cols_finais])
        
        # DataExporter.exportar_csv(lista_imoveis, "imoveis.csv") 
    else:
        print("Nenhum resultado encontrado.")