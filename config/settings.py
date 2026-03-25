"""
config/settings.py

Centralised runtime configuration for the aggregator.

All agency URLs, timeouts, client flags, and scraper limits live here.
No scraper or infrastructure module should hard-code configuration values.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgencyConfig:
    name: str
    url: str
    use_browser: bool = False
    max_pages: int = 10
    timeout: Optional[int] = None

@dataclass
class Settings:
    request_timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    max_pages: int = 10
    max_workers: int = 10
    agencies: list[AgencyConfig] = field(default_factory=list)

settings = Settings(
    request_timeout=30,
    max_pages=10,
    agencies=[
        AgencyConfig(
            name="keyonimoveis",
            url="https://www.keyonimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="sittuarimoveis",
            url="https://www.sittuarimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="bilcomimoveis",
            url="https://bilcomimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="bitimoveis",
            url="https://bitimoveis.com",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="imobiliariaaqui",
            url="https://imobiliariaaqui.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="larroydimoveis",
            url="https://larroydimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="imobiliariaacacia",
            url="https://imobiliariaacacia.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="vendimoveis",
            url="https://vendimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="loteazul",
            url="https://loteazul.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="correbens",
            url="https://correbens.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="moradaimoveis",
            url="https://moradaimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="conquistalarimoveis",
            url="https://conquistalarimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="pauloemayer",
            url="https://pauloemayer.com",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="litoralsulimoveis",
            url="https://litoralsulimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="juliocorretor",
            url="https://juliocorretor.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="imobicasa",
            url="https://imobicasa.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="citymoveis",
            url="https://citymoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="conquistaimoveis",
            url="https://conquistaimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="carlosmarques",
            url="https://carlosmarquescorretor.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="rfnegocios",
            url="https://www.rodneifrancaimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="dubettuimoveis",
            url="https://www.dubettuimoveis.com.br",
            use_browser=False,
            max_pages=20,
        ),
        AgencyConfig(
            name="chavesnamao",
            url="https://www.chavesnamao.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="iata",
            url="https://iata.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="oppenheimimoveis",
            url="https://oppenheimimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="felixmarques",
            url="https://felixmarques.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="residesulimoveis",
            url="https://residesulimoveis.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="moradaimoveistb",
            url="https://moradaimoveistb.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="imobiliariaconquista",
            url="https://imobiliariaconquista.log.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="vendelar",
            url="https://www.vendelar.com.br",
            use_browser=False,
            max_pages=10,
        ),
        AgencyConfig(
            name="imobiliariatubarao",
            url="https://imobiliariatubarao.com.br",
            use_browser=False,
            max_pages=10,
        ),
    ],
)