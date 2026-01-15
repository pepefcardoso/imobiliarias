from abc import ABC, abstractmethod
from typing import Any

class IPipelineStep(ABC):
    """
    Define um contrato para uma etapa única de processamento.
    """
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass