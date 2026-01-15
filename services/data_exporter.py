import pandas as pd
from typing import List
from domain.imovel import Imovel

class DataExporter:
    """
    Serviço responsável por converter e exportar dados de domínio
    para formatos de análise (DataFrame, CSV, Excel).
    Isola a dependência do Pandas da camada de repositório.
    """

    @staticmethod
    def para_dataframe(imoveis: List[Imovel]) -> pd.DataFrame:
        if not imoveis:
            return pd.DataFrame()
        return pd.DataFrame([i.to_dict() for i in imoveis])

    @staticmethod
    def exportar_csv(imoveis: List[Imovel], nome_arquivo: str):
        df = DataExporter.para_dataframe(imoveis)
        if not df.empty:
            df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')

    @staticmethod
    def exportar_excel(imoveis: List[Imovel], nome_arquivo: str):
        df = DataExporter.para_dataframe(imoveis)
        if not df.empty:
            df.to_excel(nome_arquivo, index=False)