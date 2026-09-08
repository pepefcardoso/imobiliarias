from scrapers.base import AgencyScraper
from scrapers.bilcomimoveis import BilcomImoveisScraper
from scrapers.bitimoveis import BitImoveisScraper
from scrapers.carlosmarques import CarlosMarquesScraper
from scrapers.citymoveis import CityMoveisScraper
from scrapers.conquistalarimoveis import ConquistalarImoveisScraper
from scrapers.correbens import CorrebensScraper
from scrapers.dubettuimoveis import DubettuImoveisScraper
from scrapers.imobicasa import ImobicasaScraper
from scrapers.imobiliariaacacia import ImobiliariaAcaciaScraper
from scrapers.imobiliariaaqui import ImobiliariaAquiScraper
from scrapers.juliocorretor import JulioCorretorScraper
from scrapers.keyonimoveis import KeyOnImoveisScraper
from scrapers.larroydimoveis import LarroyImoveisScraper
from scrapers.litoralsulimoveis import LitoralSulImoveisScraper
from scrapers.loteazul import LoteAzulScraper
from scrapers.pauloemayer import PauloEMayerScraper
from scrapers.rfnegocios import RFNegociosScraper
from scrapers.sittuarimoveis import SittuarImoveisScraper
from scrapers.vendimoveis import VendimoveisScraper
from scrapers.chavesnamao import ChavesNaMaoScraper
from scrapers.iata import IataScraper
from scrapers.oppenheimimoveis import OppenheimImoveisScraper
from scrapers.felixmarques import FelixMarquesScraper
from scrapers.residesulimoveis import ResideSulImoveisScraper
from scrapers.moradaimoveistb import MoradaImoveisTbScraper
from scrapers.vendelar import VendelarScraper
from scrapers.imobiliariaconquista import ImobiliariaConquistaScraper
from scrapers.imobiliariatubarao import ImobiliariaTubaraoScraper
from scrapers.radarimoveis import RadarImoveisScraper

SCRAPER_REGISTRY: dict[str, type[AgencyScraper]] = {
    "keyonimoveis": KeyOnImoveisScraper,
    "larroydimoveis": LarroyImoveisScraper,
    "citymoveis": CityMoveisScraper,
    "sittuarimoveis": SittuarImoveisScraper,
    "bilcomimoveis": BilcomImoveisScraper,
    "bitimoveis": BitImoveisScraper,
    "imobiliariaaqui": ImobiliariaAquiScraper,
    "imobiliariaacacia": ImobiliariaAcaciaScraper,
    "vendimoveis": VendimoveisScraper,
    "loteazul": LoteAzulScraper,
    "correbens": CorrebensScraper,
    "conquistalarimoveis": ConquistalarImoveisScraper,
    "litoralsulimoveis": LitoralSulImoveisScraper,
    "juliocorretor": JulioCorretorScraper,
    "imobicasa": ImobicasaScraper,
    "carlosmarques": CarlosMarquesScraper,
    "rfnegocios": RFNegociosScraper,
    "dubettuimoveis": DubettuImoveisScraper,
    "pauloemayer": PauloEMayerScraper,
    "chavesnamao": ChavesNaMaoScraper,
    "iata": IataScraper,
    "oppenheimimoveis": OppenheimImoveisScraper,
    "felixmarques": FelixMarquesScraper,
    "residesulimoveis": ResideSulImoveisScraper,
    "imobiliariaconquista": ImobiliariaConquistaScraper,
    "moradaimoveistb": MoradaImoveisTbScraper,
    "vendelar": VendelarScraper,
    "imobiliariatubarao": ImobiliariaTubaraoScraper,
    "radarimoveis": RadarImoveisScraper,
}