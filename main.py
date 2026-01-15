import pandas as pd
from config.settings import AppConfig
from infrastructure.selenium_client import SeleniumClient
from services.scraper_manager import ScraperManager
from factories.scraper_factory import ScraperFactory
from services.logger import StructuredLogger
from repositories.imovel_repository import ImovelRepository

def configurar_scrapers(manager: ScraperManager, logger: StructuredLogger):
    client = SeleniumClient(headless=True)
    factory = ScraperFactory(client, logger)
    
    cfg_keyon = AppConfig.SCRAPERS.get('keyon')
    if cfg_keyon and cfg_keyon.enabled:
        scraper = factory.create_keyon_scraper(cfg_keyon.url)
        manager.adicionar_scraper(scraper)

    cfg_qual = AppConfig.SCRAPERS.get('qualalugar')
    if cfg_qual and cfg_qual.enabled:
        scraper = factory.create_qualalugar_scraper(cfg_qual.url)
        manager.adicionar_scraper(scraper)

def executar_agregador() -> pd.DataFrame:
    logger = StructuredLogger()
    logger.info("--- Iniciando Orquestrador de Pesquisas ---")
    
    manager = ScraperManager()
    repository = ImovelRepository()
    
    configurar_scrapers(manager, logger)

    if not manager.scrapers:
        logger.info("Aviso: Nenhum scraper ativo.")
        return pd.DataFrame()

    logger.info(f"Executando {len(manager.scrapers)} scrapers ativos...")
    
    lista_resultados = manager.executar_todos()

    total_imoveis = 0
    total_erros = 0
    
    for resultado in lista_resultados:
        if resultado.imoveis:
            repository.adicionar_lista(resultado.imoveis)
            total_imoveis += len(resultado.imoveis)
            
        if resultado.erros:
            total_erros += len(resultado.erros)
            for erro in resultado.erros:
                logger.info(f"[Erro de Extração] {erro}")

    logger.info(f"Resumo: {total_imoveis} imóveis capturados, {total_erros} erros reportados.")

    return repository.to_dataframe()

if __name__ == "__main__":
    df_resultado = executar_agregador()
    
    if not df_resultado.empty:
        print("\n--- Resultados Unificados (Terminal) ---")
        cols_desejadas = ["Imobiliaria", "Bairro", "Preco", "Titulo"]
        cols_finais = [c for c in cols_desejadas if c in df_resultado.columns]
        print(df_resultado[cols_finais])
        
    else:
        print("Nenhum resultado encontrado.")