from typing import List
from interfaces.i_logger import ILogger
from services.scraper_manager import ScraperManager
from repositories.imovel_repository import ImovelRepository
from domain.imovel import Imovel

class AgregadorUseCase:
    def __init__(self, manager: ScraperManager, repository: ImovelRepository, logger: ILogger):
        self._manager = manager
        self._repository = repository
        self._logger = logger

    def executar(self) -> List[Imovel]:
        """
        Executa o fluxo principal de monitorização.
        """
        self._logger.info("--- Iniciando Orquestrador de Pesquisas (UseCase) ---")

        if not self._manager.scrapers:
            self._logger.info("Aviso: Nenhum scraper ativo.")
            return []

        self._logger.info(f"Executando {len(self._manager.scrapers)} scrapers ativos...")

        lista_resultados = self._manager.executar_todos()

        total_imoveis = 0
        
        for resultado in lista_resultados:
            if resultado.imoveis:
                self._repository.adicionar_lista(resultado.imoveis)
                total_imoveis += len(resultado.imoveis)
            
        todos_erros = [erro for r in lista_resultados for erro in r.erros]
        total_erros = len(todos_erros)

        if todos_erros:
            self._logger.info(
                f"Foram encontrados {total_erros} erros durante a extração.", 
                lista_erros=todos_erros
            )

        self._logger.info(f"Resumo: {total_imoveis} imóveis capturados, {total_erros} erros reportados.")

        return self._repository.obter_todos()