from typing import List
import pandas as pd
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
        return self._imoveis

    def to_dataframe(self) -> pd.DataFrame:
        """Converte os dados armazenados para Pandas DataFrame."""
        if not self._imoveis:
            return pd.DataFrame()
        
        dados = [i.to_dict() for i in self._imoveis]
        return pd.DataFrame(dados)

    def exportar_csv(self, nome_arquivo: str):
        """Salva os dados num arquivo CSV."""
        df = self.to_dataframe()
        if not df.empty:
            df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
            
    def exportar_excel(self, nome_arquivo: str):
        """Salva os dados num arquivo Excel."""
        df = self.to_dataframe()
        if not df.empty:
            df.to_excel(nome_arquivo, index=False)