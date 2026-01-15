from typing import List
from domain.imovel import Imovel

class ImovelRepository:
    def __init__(self):
        self._imoveis: List[Imovel] = []

    def adicionar(self, imovel: Imovel):
        """Adiciona um único imóvel ao repositório."""
        self._imoveis.append(imovel)

    def adicionar_lista(self, imoveis: List[Imovel]):
        """Adiciona uma lista de imóveis de uma só vez."""
        self._imoveis.extend(imoveis)

    def obter_todos(self) -> List[Imovel]:
        """Retorna a lista pura de objetos de domínio."""
        return self._imoveis