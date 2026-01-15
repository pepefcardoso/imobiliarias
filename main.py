import pandas as pd
from scrapers import KeyOnScraper
from services.scraper_manager import ScraperManager

URL_KEYON_PADRAO = "https://www.keyonimoveis.com.br/aluguel/apartamento/tubarao/todos-os-bairros/todos-os-condominios/1-banheiros+1-quartos+1-vagas?valor_max=2.000,00&area_min=40&pagina=1"

def configurar_scrapers(manager: ScraperManager):
    """
    Centraliza a configuração de quais imobiliárias serão pesquisadas.
    Aqui é fácil adicionar novas imobiliárias (ex: ImobiliariaBScraper).
    """
    manager.adicionar_scraper(KeyOnScraper(URL_KEYON_PADRAO))

def executar_agregador() -> pd.DataFrame:
    """
    Função principal que orquestra todo o processo usando a arquitetura do projeto.
    Retorna um DataFrame pandas pronto para uso.
    """
    print("--- Iniciando Orquestrador de Pesquisas ---")
    
    manager = ScraperManager()
    
    configurar_scrapers(manager)

    print("Executando scrapers...")
    resultados = manager.executar_todos()

    print(f"Total de imóveis agregados: {len(resultados)}")

    if resultados:
        return manager.exportar_para_tabela(resultados)
    else:
        return pd.DataFrame()

if __name__ == "__main__":
    df_resultado = executar_agregador()
    
    if not df_resultado.empty:
        print("\n--- Resultados Unificados (Terminal) ---")
        print(df_resultado)
        # df_resultado.to_excel("resultados.xlsx")
    else:
        print("Nenhum resultado encontrado.")