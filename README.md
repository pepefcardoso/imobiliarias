# Real Estate Aggregator

A scalable property listing aggregator that collects real estate listings from 30–40 different agencies, normalizes the data into a standardized model, and exposes a unified API for consumption.

---

# Project Purpose

This project:

- Accesses multiple real estate agency websites
- Extracts property listings
- Normalizes them into a standard `Property` model
- Aggregates results
- Returns a unified list via API
- Displays data in a simple and clean UI

It is **not** a complex domain-driven system.
It is a focused, scalable data aggregation engine.

---

# Architecture Overview

System Flow:

```
Agency Website
    ↓
Scraper (isolated per agency)
    ↓
Normalization (core model)
    ↓
Aggregator
    ↓
API
    ↓
UI Table
```

The architecture is designed to:

- Scale to 30–40 agencies
- Isolate website-specific logic
- Avoid duplicated parsing code
- Avoid unnecessary abstraction layers
- Remain easy to maintain

---

# Project Structure

```
project/
│
├── core/
│   ├── models.py
│   └── parsing_utils.py
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
```

---

# Core Concepts

## Property Model

All listings are normalized into this model:

```python
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

Rules:

- Missing values → `None`
- Price → `float`
- Area → `float` (m²)
- URLs → absolute

This model is the stable center of the system.

---

## Scrapers

Each agency has its own scraper class.

Example:

```python
class ExampleAgencyScraper(AgencyScraper):
    name = "example"

    def scrape(self) -> list[Property]:
        html = self.client.get(self.url)
        return self._parse(html)
```

Each scraper:

- Is isolated
- Does not depend on other scrapers
- Returns normalized `Property` objects
- Uses shared parsing utilities

Adding a new agency:

1. Create a scraper file
2. Implement `scrape()`
3. Register it in the aggregator
4. Done

No factories.
No pipelines.
No plugin systems.

---

## Parsing Utilities

Shared normalization logic lives in:

```
core/parsing_utils.py
```

Includes:

- `parse_price`
- `parse_area`
- `safe_int`
- `safe_float`
- `build_absolute_url`
- `normalize_whitespace`

This avoids duplicated parsing logic across 40 scrapers.

---

## Aggregator

Responsible for:

- Running all scrapers
- Collecting results
- Handling scraper-level failures
- Returning aggregated list

If one scraper fails:

- It logs the error
- Other scrapers continue

Fail-soft strategy.

---

## Infrastructure

Two clients:

### HTTP Client

Used for:

- Static HTML
- JSON endpoints

### Browser Client

Used only when:

- JavaScript rendering is required

Rule:

> Prefer HTTP over browser automation.

---

# 🚀 API

Using FastAPI.

Example endpoint:

```
GET /properties
```

Returns:

```json
[
  {
    "agency": "example",
    "title": "Apartment with 3 bedrooms",
    "price": 450000.0,
    "area": 95.0,
    "bedrooms": 3,
    "bathrooms": 2,
    "parking": 1,
    "neighborhood": "Centro",
    "city": "Tubarão",
    "url": "https://..."
  }
]
```

Optional future filters:

- `city`
- `min_price`
- `max_price`
- `bedrooms`

---

# Configuration

All runtime settings are centralized in:

```
config/settings.py
```

Includes:

- Agency URLs
- Timeouts
- Max pages
- User-agent
- Browser-required flag

No hardcoded URLs inside scrapers.

---

# Testing Strategy

We test:

- Parsing utilities
- HTML fixture parsing
- Normalization logic

We do NOT:

- Test live websites in CI
- Depend on external uptime

---

# Scalability Plan (30–40 Agencies)

The architecture supports:

- Isolated scraper failures
- Optional concurrency (ThreadPoolExecutor)
- Per-scraper timeout
- Per-scraper pagination limits
- Centralized logging

No architectural changes required to scale from 5 to 40 agencies.

---

# Anti-Overengineering Policy

This project intentionally avoids:

- Repository pattern (no DB yet)
- Use case layer
- Pipeline abstraction
- Step processors
- Abstract factories
- Plugin frameworks
- Dependency injection frameworks

Complexity is introduced only when required.

---

# Future Extensions

If the project evolves to include:

- Database persistence
- Price change detection
- Historical tracking
- Scheduled scraping
- Deduplication engine

Then a repository layer and identity strategy will be introduced.

Not before.

---

# 🛠 Local Development

### Install dependencies

```
pip install -r requirements.txt
```

### Run API

```
uvicorn api.main:app --reload
```

### Access endpoint

```
http://localhost:8000/properties
```

---

# Adding a New Agency (Checklist)

- [ ] Create new scraper file in `/scrapers`
- [ ] Implement `AgencyScraper`
- [ ] Use parsing utilities
- [ ] Normalize into `Property`
- [ ] Register in aggregator
- [ ] Test manually
- [ ] Add HTML fixture test

---

# Philosophy

This system optimizes for:

> Isolating website variability
> Keeping the core stable
> Scaling horizontally by adding scrapers

Not for abstract architectural purity.

Keep it simple.
Keep it explicit.
Keep it maintainable.
