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
    GET http://localhost:8000/properties
    GET http://localhost:8000/properties?city=Tubar%C3%A3o&min_price=200000&max_price=500000&bedrooms=2
"""

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import settings
from scrapers.base import AgencyScraper
from services.aggregator import Aggregator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scraper registry
#
# Maps each agency name (must match AgencyConfig.name in settings.py) to its
# scraper class. Add one entry here for every implemented scraper.
#
# The API will only instantiate scrapers whose name also appears in
# settings.agencies — unregistered agencies are silently skipped at startup.
# ---------------------------------------------------------------------------

from scrapers.citymoveis import CityMoveisScraper
from scrapers.keyonimoveis import KeyOnImoveisScraper
from scrapers.larroydimoveis import LarroyImoveisScraper

SCRAPER_REGISTRY: dict[str, type[AgencyScraper]] = {
    "keyonimoveis": KeyOnImoveisScraper,
    "larroydimoveis": LarroyImoveisScraper,
    "citymoveis": CityMoveisScraper,
    # Add new scrapers here as they are implemented:
    # "sittuarimoveis": SittuariMoveisScraper,
    # "bilcomimoveis": BilcomiImoveisScraper,
    # ...
}

# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------

class _AppState:
    aggregator: Optional[Aggregator] = None


_state = _AppState()


# ---------------------------------------------------------------------------
# Lifespan — build scrapers once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Builds the Aggregator from settings + registry at startup.

    Only agencies that have both a config in settings.agencies AND a class in
    SCRAPER_REGISTRY are included. This means partially-implemented deployments
    work without errors — missing scrapers are simply not run.
    """
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

    yield  # application runs here

    logger.info("[shutdown] Application shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class PropertyResponse(BaseModel):
    """
    JSON representation of a normalized Property.

    Mirrors the Property dataclass exactly so the API contract is explicit
    and validated by Pydantic on every response.
    """

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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/properties",
    response_model=list[PropertyResponse],
    summary="List all aggregated property listings",
    description=(
        "Runs all registered scrapers, merges the results, and returns the "
        "unified list. Optional query parameters narrow the results **after** "
        "aggregation — no filters are passed to individual scrapers."
    ),
)
def get_properties(
    city: Optional[str] = Query(
        default=None,
        description="Filter by city name (case-insensitive, partial match).",
        examples=["Tubarão"],
    ),
    min_price: Optional[float] = Query(
        default=None,
        ge=0,
        description="Minimum listing price (inclusive).",
    ),
    max_price: Optional[float] = Query(
        default=None,
        ge=0,
        description="Maximum listing price (inclusive).",
    ),
    bedrooms: Optional[int] = Query(
        default=None,
        ge=0,
        description="Exact number of bedrooms.",
    ),
) -> list[PropertyResponse]:
    if _state.aggregator is None:
        # Should never happen after startup, but guard defensively.
        raise HTTPException(status_code=503, detail="Aggregator not initialised.")

    properties = _state.aggregator.collect()

    # ------------------------------------------------------------------
    # Filtering — applied here, not inside scrapers or the aggregator.
    # All comparisons are None-safe: a listing with a missing value for a
    # filtered field is excluded when the caller supplies that filter.
    # ------------------------------------------------------------------

    if city is not None:
        city_lower = city.lower()
        properties = [
            p for p in properties
            if p.city is not None and city_lower in p.city.lower()
        ]

    if min_price is not None:
        properties = [
            p for p in properties
            if p.price is not None and p.price >= min_price
        ]

    if max_price is not None:
        properties = [
            p for p in properties
            if p.price is not None and p.price <= max_price
        ]

    if bedrooms is not None:
        properties = [
            p for p in properties
            if p.bedrooms is not None and p.bedrooms == bedrooms
        ]

    logger.info(
        "[GET /properties] city=%r min_price=%s max_price=%s bedrooms=%s → %d result(s)",
        city, min_price, max_price, bedrooms, len(properties),
    )

    return [PropertyResponse(**p.to_dict()) for p in properties]


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Simple liveness probe — always returns 200 if the process is up."""
    scraper_count = len(_state.aggregator.scrapers) if _state.aggregator else 0
    return {"status": "ok", "scrapers_registered": scraper_count}