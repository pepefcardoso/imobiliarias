from typing import List
import pandas as pd
from interfaces.i_scraper import IScraper

class ScraperManager:
    def __init__(self):
        self.scrapers: List[IScraper] = []

    def adicionar_scraper(self, scraper: IScraper):
        self.scrapers.append(scraper)

    def executar_todos(self):
        todos_imoveis = []
        
        for scraper in self.scrapers:
            try:
                imoveis = scraper.buscar_imoveis()
                todos_imoveis.extend(imoveis)
            except Exception as e:
                print(f"Erro ao processar um scraper: {e}")

        return todos_imoveis

    def exportar_para_tabela(self, lista_imoveis):
        dados = [i.to_dict() for i in lista_imoveis]
        df = pd.DataFrame(dados)
        return df