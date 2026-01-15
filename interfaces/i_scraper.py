from abc import ABC, abstractmethod
from typing import List
from domain.imovel import Imovel

class IScraper(ABC):
    
    @abstractmethod
    def buscar_imoveis(self) -> List[Imovel]:
        """
        Método abstrato que deve ser implementado por todas as imobiliárias.
        Deve retornar uma lista de objetos Imovel.
        """
        pass