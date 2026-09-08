import logging
from functools import lru_cache

from config.settings import settings
from services.aggregator import Aggregator

from .registry import SCRAPER_REGISTRY

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_aggregator() -> Aggregator:
    config_by_name = {cfg.name: cfg for cfg in settings.agencies}
    scrapers = []
    for name, scraper_cls in SCRAPER_REGISTRY.items():
        if name not in config_by_name:
            logger.warning("Scraper %r sem AgencyConfig — pulando.", name)
            continue
        scrapers.append(scraper_cls(config=config_by_name[name]))
    return Aggregator(scrapers=scrapers, concurrent=True, max_workers=settings.max_workers)