import pandas as pd
from scrapers import KeyOnScraper, QualAlugarScraper
from services.scraper_manager import ScraperManager

URL_KEYON_PADRAO = "https://www.keyonimoveis.com.br/aluguel/apartamento/tubarao/todos-os-bairros/todos-os-condominios/1-banheiros+1-quartos+1-vagas?valor_max=2.000,00&area_min=40&pagina=1"
URL_QUALALUGAR_PADRAO = "https://www.qualalugar.net/imoveis/para-alugar/apartamento+casa/brasil?area=40--10000000&precolocacao=500--2000&dormitorios=1--2--3&vagas=1--2--3&banheiros=1--2--3&propertySubtypes=346&propertySubtypes=19&propertySubtypes=325&propertySubtypes=169&finalidade=1&order=mais_relevantes"

def configurar_scrapers(manager: ScraperManager):
    """
    Centraliza a configuração de quais imobiliárias serão pesquisadas.
    """
    manager.adicionar_scraper(KeyOnScraper(URL_KEYON_PADRAO))
    manager.adicionar_scraper(QualAlugarScraper(URL_QUALALUGAR_PADRAO))

def executar_agregador() -> pd.DataFrame:
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
        print(df_resultado[["Imobiliaria", "Bairro", "Preco", "Titulo"]])
    else:
        print("Nenhum resultado encontrado.")