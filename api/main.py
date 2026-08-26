import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from cachetools import TTLCache

from config.settings import settings
from core.models import SearchQuery
from scrapers.base import AgencyScraper
from services.aggregator import Aggregator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s   %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

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

class _AppState:
    aggregator: Optional[Aggregator] = None
    cache: TTLCache = TTLCache(maxsize=500, ttl=900)

_state = _AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    config_by_name = {cfg.name: cfg for cfg in settings.agencies}
    scrapers: list[AgencyScraper] = []
    for name, scraper_cls in SCRAPER_REGISTRY.items():
        if name not in config_by_name:
            logger.warning(
                "[startup] Scraper %r is registered but has no AgencyConfig in settings   skipping.",
                name,
            )
            continue
        scrapers.append(scraper_cls(config=config_by_name[name]))
        logger.info("[startup] Registered scraper: %s", name)
        
    _state.aggregator = Aggregator(
        scrapers=scrapers,
        concurrent=True,
        max_workers=settings.max_workers,
    )
    
    logger.info(
        "[startup] Aggregator ready with %d scraper(s) (concurrent, max_workers=%d).",
        len(scrapers),
        settings.max_workers,
    )
    yield
    logger.info("[shutdown] Application shutting down.")

app = FastAPI(
    title="Real Estate Aggregator",
    description=(
        "Aggregates property listings from multiple real estate agencies "
        "in Tubarão/SC and returns a unified JSON feed."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

class PropertyResponse(BaseModel):
    agency: str
    title: str
    url: str
    price: Optional[float] = None
    area: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None
    condo_fee: Optional[float] = None
    street: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    property_type: Optional[str] = None
    business_type: Optional[str] = None
    source_links: list[dict] = []

@app.get(
    "/properties",
    response_model=list[PropertyResponse],
    summary="List all aggregated property listings",
)
def get_properties(
    city: Optional[str] = Query(default=None),
    neighborhood: Optional[str] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    min_bedrooms: Optional[int] = Query(default=None, ge=0),
    min_bathrooms: Optional[int] = Query(default=None, ge=0),
    min_parking: Optional[int] = Query(default=None, ge=0),
    min_area: Optional[float] = Query(default=None, ge=0),
    max_area: Optional[float] = Query(default=None, ge=0),
    property_types: list[str] = Query(default=[]),
    business_type: Optional[str] = Query(default="venda"),
) -> list[PropertyResponse]:
    
    if _state.aggregator is None:
        raise HTTPException(status_code=503, detail="Aggregator not initialised.")
        
    query = SearchQuery(
        city=city,
        neighborhood=neighborhood,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        min_parking=min_parking,
        min_area=min_area,
        max_area=max_area,
        property_types=property_types if property_types else None,
        business_type=business_type
    )
    
    cache_key = tuple(
        (k, tuple(v) if isinstance(v, list) else v)
        for k, v in sorted(query.__dict__.items())
    )
    
    cached_response = _state.cache.get(cache_key)
    if cached_response is not None:
        logger.info("[GET /properties] CACHE HIT for query=%s", query)
        return cached_response
        
    logger.info("[GET /properties] CACHE MISS for query=%s", query)
    properties = _state.aggregator.search(query)
    response_data = [PropertyResponse(**p.to_dict()) for p in properties]
    
    _state.cache[cache_key] = response_data
    logger.info(
        "[GET /properties] query=%s   %d result(s) cached",
        query,
        len(properties),
    )
    return response_data

@app.get("/health", include_in_schema=False)
def health() -> dict:
    scraper_count = len(_state.aggregator.scrapers) if _state.aggregator else 0
    return {"status": "ok", "scrapers_registered": scraper_count}

@app.get("/style.css", include_in_schema=False)
def serve_css():
    return FileResponse("style.css")

@app.get("/script.js", include_in_schema=False)
def serve_js():
    return FileResponse("script.js")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("index.html")