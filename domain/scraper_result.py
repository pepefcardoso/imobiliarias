from dataclasses import dataclass, field
from typing import List
from .imovel import Imovel

@dataclass
class ScraperResult:
    """
    Objeto que encapsula o resultado de uma operação de scraping/parsing.
    Contém a lista de imóveis extraídos com sucesso e uma lista de mensagens de erro.
    """
    imoveis: List[Imovel] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)