from typing import List
from interfaces.i_scraper import IScraper
from domain.scraper_result import ScraperResult

class ScraperManager:
    def __init__(self):
        self.scrapers: List[IScraper] = []

    def adicionar_scraper(self, scraper: IScraper):
        self.scrapers.append(scraper)

    def executar_todos(self) -> List[ScraperResult]:
        """
        Executa todos os scrapers e retorna uma lista de ScraperResults.
        Não faz mais a consolidação dos imóveis aqui.
        """
        resultados_gerais = []
        
        for scraper in self.scrapers:
            try:
                resultado = scraper.buscar_imoveis()
                resultados_gerais.append(resultado)
                
            except Exception as e:
                print(f"Erro crítico ao executar um scraper: {e}")
                
        return resultados_gerais