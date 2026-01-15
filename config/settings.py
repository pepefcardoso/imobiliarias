from dataclasses import dataclass
from typing import Dict

@dataclass
class ScraperConfig:
    name: str
    url: str
    enabled: bool = True

class AppConfig:
    """
    Centraliza as configurações da aplicação.
    No futuro, estes valores podem vir de variáveis de ambiente (.env).
    """
    
    SCRAPERS: Dict[str, ScraperConfig] = {
        'keyon': ScraperConfig(
            name='KeyOn',
            url="https://www.keyonimoveis.com.br/aluguel/apartamento/tubarao/todos-os-bairros/todos-os-condominios/1-banheiros+1-quartos+1-vagas?valor_max=2.000,00&area_min=40&pagina=1",
            enabled=True
        ),
        'qualalugar': ScraperConfig(
            name='QualAlugar',
            url="https://www.qualalugar.net/imoveis/para-alugar/apartamento+casa/brasil?area=40--10000000&precolocacao=500--2000&dormitorios=1--2--3&vagas=1--2--3&banheiros=1--2--3&propertySubtypes=346&propertySubtypes=19&propertySubtypes=325&propertySubtypes=169&finalidade=1&order=mais_relevantes",
            enabled=True
        )
    }