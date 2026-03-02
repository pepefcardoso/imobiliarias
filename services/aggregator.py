import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, TimeoutError
from typing import Optional

from config.settings import settings
from core.models import Property
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

    def collect(self) -> list[Property]:
        if self.concurrent:
            return self._collect_concurrent()
        return self._collect_sequential()

    def _collect_sequential(self) -> list[Property]:
        properties: list[Property] = []

        for scraper in self.scrapers:
            batch = self._run_scraper(scraper)
            properties.extend(batch)

        logger.info(
            "[aggregator] Done (sequential). %d scraper(s), %d property(ies) total.",
            len(self.scrapers),
            len(properties),
        )
        return properties

    def _collect_concurrent(self) -> list[Property]:
        properties: list[Property] = []
        future_to_scraper: dict[Future, AgencyScraper] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for scraper in self.scrapers:
                future = executor.submit(scraper.scrape)
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

    def _run_scraper(self, scraper: AgencyScraper) -> list[Property]:
        start = time.perf_counter()
        try:
            batch = scraper.scrape()
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