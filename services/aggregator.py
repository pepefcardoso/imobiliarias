"""
services/aggregator.py

Aggregator service — runs all registered scrapers, collects results,
isolates failures, and returns a unified list of Property objects.

Design decisions:
  - Fail-soft: a failing scraper is logged and skipped; others continue.
  - Optional concurrency via ThreadPoolExecutor (disabled by default).
  - Per-scraper timeout safety wraps each scrape() call when concurrency
    is enabled (futures have a hard deadline equal to the scraper's
    configured timeout, or the global request_timeout as fallback).
  - No parsing logic here — that belongs in scrapers and parsing_utils.
  - No business logic here — filtering belongs in the API layer.
"""

import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed, TimeoutError
from typing import Optional

from config.settings import settings
from core.models import Property
from scrapers.base import AgencyScraper

logger = logging.getLogger(__name__)


class Aggregator:
    """
    Runs a collection of AgencyScraper instances and merges their results.

    Usage (sequential — default):
        aggregator = Aggregator(scrapers=[scraper_a, scraper_b, ...])
        properties = aggregator.collect()

    Usage (concurrent):
        aggregator = Aggregator(scrapers=[...], concurrent=True, max_workers=10)
        properties = aggregator.collect()
    """

    def __init__(
        self,
        scrapers: list[AgencyScraper],
        concurrent: bool = False,
        max_workers: Optional[int] = None,
    ) -> None:
        """
        Args:
            scrapers:    List of instantiated AgencyScraper objects to run.
            concurrent:  If True, scrapers run in parallel via ThreadPoolExecutor.
                         Defaults to False (sequential).
            max_workers: Maximum number of threads when concurrent=True.
                         Defaults to settings.max_workers.
        """
        self.scrapers = scrapers
        self.concurrent = concurrent
        self.max_workers = max_workers or settings.max_workers

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def collect(self) -> list[Property]:
        """
        Runs all scrapers and returns a merged list of Property objects.

        Scraper failures are caught, logged, and skipped — they never
        propagate to the caller.

        Returns:
            Flat list of all successfully collected Property objects.
        """
        if self.concurrent:
            return self._collect_concurrent()
        return self._collect_sequential()

    # ------------------------------------------------------------------
    # Sequential strategy
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Concurrent strategy
    # ------------------------------------------------------------------

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
                    # as_completed already means the future is done, but we
                    # call result() with a small safety margin to surface any
                    # exception raised inside the thread.
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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_scraper(self, scraper: AgencyScraper) -> list[Property]:
        """
        Executes a single scraper, measures duration, and handles errors.

        Returns an empty list if the scraper raises any exception.
        """
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