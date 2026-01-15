from abc import ABC, abstractmethod
from typing import Optional

class IHttpClient(ABC):
    @abstractmethod
    def fetch(self, url: str, wait_selector: Optional[str] = None) -> str:
        """
        Responsável por buscar o conteúdo bruto (HTML) de uma URL.
        :param wait_selector: Seletor CSS (ex: '.card') para aguardar antes de retornar.
        """
        pass