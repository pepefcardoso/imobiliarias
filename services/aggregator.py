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
        """
        Executa a recolha em todos os scrapers passando a query do utilizador,
        e aplica o filtro de segurança final (Safety Net) antes de devolver os resultados.
        """
        if self.concurrent:
            properties = self._collect_concurrent(query)
        else:
            properties = self._collect_sequential(query)
            
        return self._apply_strict_filters(properties, query)

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
                    
            filtered.append(p)
            
        logger.info(
            "[aggregator] Safety Net filtering applied: %d in -> %d out",
            len(properties),
            len(filtered)
        )
            
        return filtered