import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, TimeoutError
from typing import Optional

from config.settings import settings
from core.models import Property, SearchQuery
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)


class Aggregator:
    def __init__(
        self,
        scrapers: list[AgencyScraper],
        concurrent: bool = False,
        max_workers: Optional[int] = None,
    ) -> None:

        self.scrapers = scrapers
        self.concurrent = concurrent
        self.max_workers = max_workers or settings.max_workers

    def search(self, query: SearchQuery) -> list[Property]:
        if self.concurrent:
            properties = self._collect_concurrent(query)
        else:
            properties = self._collect_sequential(query)
            
        filtered = self._apply_strict_filters(properties, query)
        
        return self._deduplicate_properties(filtered)

    def _deduplicate_properties(self, properties: list[Property]) -> list[Property]:
        deduped: list[Property] = []

        for p in properties:
            if not p.source_links:
                p.source_links = [{"agency": p.agency, "url": p.url, "price": p.price}]

            is_duplicate = False
            for d in deduped:
                if (
                    (p.city or "").lower() == (d.city or "").lower() and
                    (p.neighborhood or "").lower() == (d.neighborhood or "").lower() and
                    p.bedrooms == d.bedrooms and
                    p.bathrooms == d.bathrooms and
                    p.parking == d.parking and
                    (p.business_type or "").lower() == (d.business_type or "").lower() and
                    (p.property_type or "").lower() == (d.property_type or "").lower()
                ):
                    if (self._is_within_tolerance(p.price, d.price, 0.03) and 
                        self._is_within_tolerance(p.area, d.area, 0.03)):
                        
                        d.source_links.append({"agency": p.agency, "url": p.url, "price": p.price})
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduped.append(p)

        logger.info("[aggregator] Deduplication applied: %d in -> %d out", len(properties), len(deduped))
        return deduped

    @staticmethod
    def _is_within_tolerance(val1: float | None, val2: float | None, tolerance: float) -> bool:
        """
        Verifica se dois valores numéricos estão dentro da tolerância permitida.
        Trata None de forma segura (ambos None = Match; um None = No Match).
        """
        if val1 is None and val2 is None:
            return True
        if val1 is None or val2 is None:
            return False
        if val1 == 0 and val2 == 0:
            return True
        if val1 == 0 or val2 == 0:
            return False
        
        return abs(val1 - val2) / max(val1, val2) <= tolerance

    def _collect_sequential(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []

        for scraper in self.scrapers:
            batch = self._run_scraper(scraper, query)
            properties.extend(batch)

        logger.info(
            "[aggregator] Done (sequential). %d scraper(s), %d property(ies) total.",
            len(self.scrapers),
            len(properties),
        )
        return properties

    def _collect_concurrent(self, query: SearchQuery) -> list[Property]:
        properties: list[Property] = []
        future_to_scraper: dict[Future, AgencyScraper] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for scraper in self.scrapers:
                future = executor.submit(scraper.scrape, query)
                future_to_scraper[future] = scraper

            for future in as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                per_scraper_timeout = (
                    scraper.config.timeout or settings.request_timeout
                )
                try:
                    batch: list[Property] = future.result(timeout=per_scraper_timeout)
                    logger.info(
                        "[aggregator][%s] %d property(ies) collected.",
                        scraper.name,
                        len(batch),
                    )
                    properties.extend(batch)
                except TimeoutError:
                    logger.error(
                        "[aggregator][%s] Timed out after %ds — skipping.",
                        scraper.name,
                        per_scraper_timeout,
                    )
                except Exception as exc:
                    logger.error(
                        "[aggregator][%s] Failed: %s — skipping.",
                        scraper.name,
                        exc,
                        exc_info=True,
                    )

        logger.info(
            "[aggregator] Done (concurrent, workers=%d). %d scraper(s), %d property(ies) total.",
            self.max_workers,
            len(self.scrapers),
            len(properties),
        )
        return properties

    def _run_scraper(self, scraper: AgencyScraper, query: SearchQuery) -> list[Property]:
        start = time.perf_counter()
        try:
            batch = scraper.scrape(query)
            duration = time.perf_counter() - start
            logger.info(
                "[aggregator][%s] %d property(ies) collected in %.2fs.",
                scraper.name,
                len(batch),
                duration,
            )
            return batch
        except Exception as exc:
            duration = time.perf_counter() - start
            logger.error(
                "[aggregator][%s] Failed after %.2fs: %s",
                scraper.name,
                duration,
                exc,
                exc_info=True,
            )
            return []

    def _apply_strict_filters(self, properties: list[Property], query: SearchQuery) -> list[Property]:
        """
        Safety Net: Valida programaticamente se os imóveis retornados pelos 
        scrapers realmente cumprem as condições exigidas pelo utilizador.
        """
        filtered = []
        for p in properties:
            if query.min_bedrooms is not None and (p.bedrooms or 0) < query.min_bedrooms:
                continue
            
            if query.min_bathrooms is not None and (p.bathrooms or 0) < query.min_bathrooms:
                continue
                
            if query.min_parking is not None and (p.parking or 0) < query.min_parking:
                continue
                
            if query.min_price is not None and (p.price or 0.0) < query.min_price:
                continue
            if query.max_price is not None and (p.price or float('inf')) > query.max_price:
                continue
                
            if query.min_area is not None and (p.area or 0.0) < query.min_area:
                continue
            if query.max_area is not None and (p.area or float('inf')) > query.max_area:
                continue
                
            if query.city:
                if not p.city or query.city.lower() not in p.city.lower():
                    continue

            if query.neighborhood:
                if not p.neighborhood or query.neighborhood.lower() != p.neighborhood.lower():
                    continue

            if query.business_type and p.business_type:
                if query.business_type.lower() != p.business_type.lower():
                    continue
            
            if query.property_types and p.property_type:
                matches = any(pt.lower() in p.property_type.lower() for pt in query.property_types)
                if not matches:
                    continue
                    
            filtered.append(p)
            
        logger.info(
            "[aggregator] Safety Net filtering applied: %d in -> %d out",
            len(properties),
            len(filtered)
        )
            
        return filtered
