# Architecture Guidelines

## 1. Architectural Philosophy

This project is a **data aggregation system**, not a complex domain-driven application.

Primary goal:
> Scrape multiple real estate agencies, normalize listings into a standard model, aggregate results, and expose them via API.

Guiding principles:

- Keep architecture minimal and explicit
- Optimize for adding new agencies easily
- Avoid unnecessary abstraction layers
- Prefer composition over inheritance
- Avoid speculative design
- Isolate variability (scraping logic)
- Keep the core model stable

---

## 2. High-Level Architecture

System Flow:

Source Website  
→ Scraper  
→ Normalization  
→ Aggregator  
→ API  
→ UI

There is no need for:
- Repositories (unless persistence is introduced)
- Use case layers
- Complex factories
- Pipeline abstractions
- Domain services

---

## 3. Folder Structure

Recommended structure:

```

project/
│
├── core/
│   ├── models.py
│   ├── parsing_utils.py
│
├── scrapers/
│   ├── base.py
│   ├── agency_a.py
│   ├── agency_b.py
│   └── ...
│
├── services/
│   └── aggregator.py
│
├── infrastructure/
│   ├── http_client.py
│   └── browser_client.py
│
├── api/
│   └── main.py
│
├── config/
│   └── settings.py
│
└── tests/

````

---

## 4. Core Layer (Stable)

### models.py

The core model must remain stable and simple.

Example:

```python
from dataclasses import dataclass
from typing import Optional

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
````

Rules:

* No scraping logic inside models
* No formatting logic inside models
* Keep it pure and serializable

---

### parsing_utils.py

Shared helper functions:

* parse_price
* parse_area
* safe_int
* safe_float
* normalize_whitespace
* build_absolute_url

Never duplicate parsing logic inside scrapers.

---

## 5. Scrapers Layer (Isolated Variability)

### Base Scraper

```python
from abc import ABC, abstractmethod
from core.models import Property

class AgencyScraper(ABC):
    name: str

    @abstractmethod
    def scrape(self) -> list[Property]:
        pass
```

Rules:

* Each scraper file = one agency
* No cross-dependency between scrapers
* Scrapers must return normalized Property objects
* Scrapers must not know about other scrapers

---

### Adding a New Agency

Steps:

1. Create a new file in `scrapers/`
2. Implement `AgencyScraper`
3. Use parsing utilities
4. Register scraper in aggregator

That’s it.

No factories required.

---

## 6. Infrastructure Layer

Two clients:

### http_client.py

Used for static HTML or JSON endpoints.

### browser_client.py

Used only when JavaScript rendering is required.

Rules:

* Prefer HTTP client
* Use browser automation only when necessary
* Never mix scraping logic inside infrastructure

---

## 7. Services Layer

### aggregator.py

Responsible for:

* Running all scrapers
* Collecting results
* Handling errors
* Returning aggregated list

Example:

```python
class Aggregator:
    def __init__(self, scrapers):
        self.scrapers = scrapers

    def collect(self):
        properties = []
        for scraper in self.scrapers:
            try:
                properties.extend(scraper.scrape())
            except Exception as e:
                # log error
                continue
        return properties
```

Rules:

* Aggregator must not parse HTML
* Aggregator must not know scraper internals

---

## 8. API Layer

Use FastAPI.

Expose:

GET /properties

Return:

* JSON list of Property
* Optional filters (city, price range, bedrooms)

Keep it simple.

---

## 9. Error Handling Strategy

Each scraper:

* Should raise meaningful exceptions
* Should not silently swallow errors

Aggregator:

* Logs failures
* Continues execution

Never use broad `except Exception` without logging context.

---

## 10. Anti-Overengineering Rules

Do NOT introduce:

* Repository pattern (unless DB exists)
* UseCase layer
* Command pattern
* Pipeline abstractions
* Step processors
* Abstract factories

Only introduce complexity when there is a real need.

---

## 11. Scalability Considerations

With 30–40 agencies:

* Ensure each scraper is isolated
* Add timeout per scraper
* Consider concurrency using ThreadPoolExecutor
* Add per-scraper configuration

Do not prematurely optimize.

---

## 12. Code Quality Standards

* Type hints everywhere
* Black formatting
* Ruff or Flake8 linting
* Unit tests for parsing logic
* No duplicated helper logic
* No business logic inside API layer

---

## 13. Long-Term Evolution

If project evolves into:

* Persistent storage
* Historical tracking
* Change detection
* Price monitoring

Then introduce:

* Database layer
* Property identity strategy
* Diff engine
* Repository abstraction

Not before.