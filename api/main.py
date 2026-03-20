"""
api/main.py

FastAPI application — exposes aggregated property listings via a REST API.

Responsibilities:
  - Wire registered scrapers to the Aggregator on startup
  - Expose GET /properties with optional query-param filters
  - Return a unified JSON list of Property objects

Rules (from architecture guidelines):
  - No scraping logic here
  - No parsing logic here
  - Filtering is query-param driven — it is the API layer's responsibility
    to narrow results before returning them to the caller

Running locally:
    uvicorn api.main:app --reload

Endpoint:
    GET https://imobiliarias.onrender.com/properties
    GET https://imobiliarias.onrender.com/properties?city=Tubar%C3%A3o&max_price=320000&min_bedrooms=1&min_bathrooms=1&min_parking=1&min_area=50
"""

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config.settings import settings
from core.models import SearchQuery
from scrapers.base import AgencyScraper
from services.aggregator import Aggregator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from scrapers.bilcomimoveis import BilcomImoveisScraper
from scrapers.bitimoveis import BitImoveisScraper
from scrapers.carlosmarques import CarlosMarquesScraper
from scrapers.citymoveis import CityMoveisScraper
from scrapers.conquistaimoveis import ConquistaImoveisScraper
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
from scrapers.moradaimoveis import MoradaImoveisScraper
from scrapers.pauloemayer import PauloEMayerScraper
from scrapers.rfnegocios import RFNegociosScraper
from scrapers.sittuarimoveis import SittuarImoveisScraper
from scrapers.vendimoveis import VendimoveisScraper
from scrapers.chavesnamao import ChavesNaMaoScraper

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
    "moradaimoveis": MoradaImoveisScraper,
    "conquistalarimoveis": ConquistalarImoveisScraper,
    "litoralsulimoveis": LitoralSulImoveisScraper,
    "juliocorretor": JulioCorretorScraper,
    "imobicasa": ImobicasaScraper,
    "conquistaimoveis": ConquistaImoveisScraper,
    "carlosmarques": CarlosMarquesScraper,
    "rfnegocios": RFNegociosScraper,
    "dubettuimoveis": DubettuImoveisScraper,
    "pauloemayer": PauloEMayerScraper,
    "chavesnamao": ChavesNaMaoScraper,
}

class _AppState:
    aggregator: Optional[Aggregator] = None


_state = _AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_by_name = {cfg.name: cfg for cfg in settings.agencies}

    scrapers: list[AgencyScraper] = []
    for name, scraper_cls in SCRAPER_REGISTRY.items():
        if name not in config_by_name:
            logger.warning(
                "[startup] Scraper %r is registered but has no AgencyConfig in settings — skipping.",
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
    neighborhood: Optional[str] = None
    city: Optional[str] = None

@app.get(
    "/properties",
    response_model=list[PropertyResponse],
    summary="List all aggregated property listings",
    description=(
        "Runs all registered scrapers, merges the results, and returns the "
        "unified list. Optional query parameters narrow the results after aggregation."
    ),
)
def get_properties(
    city: Optional[str] = Query(
        default=None,
        description="Filter by city name (case-insensitive, partial match).",
        examples=["Tubarão"],
    ),
    neighborhood: Optional[str] = Query(
        default=None,
        description="Filter by neighborhood name (case-insensitive, exact match).",
        examples=["Centro"],
    ),
    min_price: Optional[float] = Query(
        default=None,
        ge=0,
        description="Minimum listing price (inclusive).",
    ),
    max_price: Optional[float] = Query(
        default=None,
        ge=0,
        description="Maximum listing price (inclusive). Default target: 320000.",
    ),
    min_bedrooms: Optional[int] = Query(
        default=None,
        ge=0,
        description="Minimum number of bedrooms (inclusive).",
    ),
    min_bathrooms: Optional[int] = Query(
        default=None,
        ge=0,
        description="Minimum number of bathrooms (inclusive).",
    ),
    min_parking: Optional[int] = Query(
        default=None,
        ge=0,
        description="Minimum number of parking spots (inclusive).",
    ),
    min_area: Optional[float] = Query(
        default=None,
        ge=0,
        description="Minimum area in m² (inclusive). Typical minimum: 50.",
    ),
    max_area: Optional[float] = Query(
        default=None,
        ge=0,
        description="Maximum area in m² (inclusive).",
    ),
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
        max_area=max_area
    )

    properties = _state.aggregator.search(query)

    logger.info(
        "[GET /properties] query=%s → %d result(s)",
        query,
        len(properties),
    )

    return [PropertyResponse(**p.to_dict()) for p in properties]


@app.get("/health", include_in_schema=False)
def health() -> dict:
    scraper_count = len(_state.aggregator.scrapers) if _state.aggregator else 0
    return {"status": "ok", "scrapers_registered": scraper_count}

@app.get("/", include_in_schema=False)
def serve_frontend():
    """
    Quando alguém aceder ao URL principal (https://imobiliarias.onrender.com/),
    o servidor envia o ficheiro index.html.
    """
    return FileResponse("index.html")