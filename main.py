from scrapers import KeyOnScraper
from services.scraper_manager import ScraperManager

def main():
    print("--- Sistema de Busca de Imóveis ---")

    manager = ScraperManager()

    url_pesquisa = "https://www.keyonimoveis.com.br/aluguel/apartamento/tubarao/todos-os-bairros/todos-os-condominios/1-banheiros+1-quartos+1-vagas?valor_max=2.000,00&area_min=40&pagina=1"
    
    manager.adicionar_scraper(KeyOnScraper(url_pesquisa))

    print("Executando pesquisas...")
    resultados = manager.executar_todos()

    if resultados:
        df = manager.exportar_para_tabela(resultados)
        
        import pandas as pd
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        
        print("\nResultados Unificados:")
        print(df)
        
        # df.to_excel("resultados_imoveis.xlsx", index=False)
        # print("\nArquivo 'resultados_imoveis.xlsx' salvo com sucesso!")
    else:
        print("Nenhum imóvel encontrado.")

if __name__ == "__main__":
    main()