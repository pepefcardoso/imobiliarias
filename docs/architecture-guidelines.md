## 1. Architectural Philosophy

This project is an **On-Demand Search Engine** for real estate, not a simple crawler or a complex domain-driven application.

Primary goal:

> Receive user search criteria, translate them into agency-specific requests, aggregate real-time results, and provide a unified, filtered response.

Guiding principles:

- **Search as a Router:** The system acts as a translator between a standard query and 30–40 different website "dialects."
- **On-Demand Execution:** Scraping is triggered by user action, not by background schedules.
- **Local Fallback Filtering:** Since external filters are inconsistent, the core system must perform a final programmatic validation of all results.
- **AI-Ready Design:** Code patterns must be explicit and documented to allow AI agents to generate new scrapers with 100% compatibility.

---

## 2. High-Level Architecture

System Flow:
**User Input (UI)** → **SearchQuery Object** → **Aggregator (Parallel Execution)** → **Scrapers (Query Translation)** → **Post-Processing (Local Filtering)** → **Unified Table (API)**

We avoid:

- Persistent Databases (for now).
- Complex Caching (until performance demands it).
- Heavyweight Pipeline Abstractions.

---

## 3. Folder Structure

```text
project/
│
├── core/
│   ├── models.py          # Property and SearchQuery models
│   └── parsing_utils.py   # Shared logic for data cleaning
│
├── scrapers/
│   ├── base.py            # Abstract Base Class for all scrapers
│   ├── agency_a.py        # Specific implementation
│   └── ...
│
├── services/
│   └── aggregator.py      # Orchestrates the search and final filtering
│
├── infrastructure/
│   ├── http_client.py     # Fast, static requests
│   └── browser_client.py  # Slow, JS-rendered requests
│
├── api/
│   └── main.py            # FastAPI endpoints
│
├── config/
│   └── settings.py        # Agency URLs and timeouts
│
└── tests/

```

---

## 4. Core Layer (Stable)

### models.py

The core models define the contract for the entire system.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchQuery:
    min_price: Optional[float]
    max_price: Optional[float]
    min_bedrooms: int    # Rule: Result must be >= this value
    min_bathrooms: int   # Rule: Result must be >= this value
    city: Optional[str]

@dataclass
class Property:
    agency: str
    title: str
    price: Optional[float]
    area: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    parking: Optional[int]
    neighborhood: Optional[str]
    city: Optional[str]
    url: str

```

---

## 5. Scrapers Layer (The Translators)

### Base Scraper

Every scraper must receive the `SearchQuery` and return a list of `Property`.

```python
from abc import ABC, abstractmethod
from core.models import Property, SearchQuery

class AgencyScraper(ABC):
    name: str

    @abstractmethod
    def scrape(self, query: SearchQuery) -> list[Property]:
        """
        1. Translate query to site-specific URL/Parameters.
        2. Fetch and parse results.
        3. Return normalized Property list.
        """
        pass

```

### The "Inconsistency" Strategy

When a site handles filters differently, the scraper must follow this hierarchy:

1. **Native Filter:** Use the site's search engine to reduce data volume (e.g., if user wants 3 bedrooms, tell the site to show 3).
2. **Broad Search:** If the site cannot filter by "greater than," the scraper brings the closest matches.
3. **Local Fallback:** The Scraper/Aggregator will perform the final check (e.g., $Bedrooms \ge 3$) before returning the data.

---

## 6. Services Layer

### aggregator.py

The Aggregator manages the lifecycle of a search request.

```python
from concurrent.futures import ThreadPoolExecutor

class Aggregator:
    def __init__(self, scrapers):
        self.scrapers = scrapers

    def search(self, query: SearchQuery):
        all_properties = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Run all scrapers in parallel for speed
            results = executor.map(lambda s: s.scrape(query), self.scrapers)
            for property_list in results:
                all_properties.extend(property_list)

        # FINAL FILTERING (Safety Net)
        return self._apply_strict_filters(all_properties, query)

    def _apply_strict_filters(self, properties, query):
        return [
            p for p in properties
            if (p.bedrooms or 0) >= query.min_bedrooms
            and (p.bathrooms or 0) >= query.min_bathrooms
            # ... and price/city checks
        ]

```

---

## 7. Scalability & Error Handling

- **Concurrency:** Use `ThreadPoolExecutor`. Even if agencies are scraped "one by one" logically, running them in parallel is mandatory to keep UI response times acceptable.
- **Isolation:** A failure in `agency_a.py` must never prevent `agency_b.py` from returning results.
- **Timeout:** Every scraper must have a hard timeout (e.g., 15 seconds).

---

## 8. Anti-Overengineering Rules

- **No DB:** Do not add SQLAlchemy or Mongo unless we start tracking price history.
- **No Complex UI:** A paginated table is the goal. No complex state management or "saved searches" yet.
