# Real Estate Aggregator — Project Backlog

This backlog is strictly aligned with:

- Architecture Guidelines
- Design Documentation

The system is a data aggregation engine, not a complex domain-driven application.

Goal:
Scrape 30–40 real estate agencies, normalize listings into a stable Property model, aggregate results, and expose them via API.

No unnecessary abstractions should be introduced.

---

# PHASE 1 — Enforce Correct Architecture

## 1.1 Folder Structure Alignment

Ensure the project follows the recommended structure:

project/
│
├── core/
│ ├── models.py
│ ├── parsing_utils.py
│
├── scrapers/
│ ├── base.py
│ ├── agency_x.py
│
├── services/
│ └── aggregator.py
│
├── infrastructure/
│ ├── http_client.py
│ └── browser_client.py
│
├── api/
│ └── main.py
│
├── config/
│ └── settings.py
│
└── tests/

Tasks:

- [ ] Remove unnecessary architectural layers (pipelines, factories, repositories, use cases)
- [ ] Ensure scraping logic exists only inside `scrapers/`
- [ ] Ensure infrastructure layer contains no parsing logic
- [ ] Ensure API layer contains no business logic
- [ ] Ensure core layer remains stable and minimal

---

# PHASE 2 — Core Layer (Stable and Minimal)

## 2.1 Implement Property Model

File: core/models.py

- [ ] Create `Property` dataclass
- [ ] Include required normalized fields:
  - agency
  - title
  - price (float | None)
  - area (float | None)
  - bedrooms (int | None)
  - bathrooms (int | None)
  - parking (int | None)
  - neighborhood (str | None)
  - city (str | None)
  - url
- [ ] Ensure full type hints
- [ ] Ensure model contains no parsing logic
- [ ] Ensure model is JSON serializable

---

## 2.2 Implement Parsing Utilities

File: core/parsing_utils.py

Create shared normalization helpers:

- [ ] parse_price
- [ ] parse_area
- [ ] safe_int
- [ ] safe_float
- [ ] normalize_whitespace
- [ ] build_absolute_url

Rules:

- No duplication of parsing logic inside scrapers
- All normalization must go through these utilities
- Unit tests must cover these functions

---

# PHASE 3 — Infrastructure Layer

## 3.1 HTTP Client

File: infrastructure/http_client.py

- [ ] Implement simple HTTP GET wrapper
- [ ] Add timeout support
- [ ] Add configurable user-agent
- [ ] Raise meaningful exceptions
- [ ] Do not include scraping logic

---

## 3.2 Browser Client (Only if Necessary)

File: infrastructure/browser_client.py

- [ ] Implement browser automation (Playwright or Selenium)
- [ ] Support timeout configuration
- [ ] Use only when JavaScript rendering is required
- [ ] Avoid defaulting to browser automation

---

# PHASE 4 — Scrapers Layer (Isolated Variability)

## 4.1 Base Scraper

File: scrapers/base.py

- [ ] Implement abstract base class `AgencyScraper`
- [ ] Define `name` attribute
- [ ] Define abstract method `scrape() -> list[Property]`
- [ ] Ensure no cross-dependency between scrapers

---

## 4.2 Implement Agency Scrapers (30–40 total)

For each agency:

- [ ] Create one file per agency
- [ ] Fetch data (prefer JSON endpoint if available)
- [ ] Parse listing cards
- [ ] Normalize values using parsing_utils
- [ ] Return list of `Property`
- [ ] Handle pagination
- [ ] Respect max_pages configuration
- [ ] Respect timeouts
- [ ] Raise meaningful exceptions

Progress tracking:

- [ ] Agency 1 implemented
- [ ] Agency 2 implemented
- [ ] ...
- [ ] Agency 30+ implemented

---

# PHASE 5 — Aggregator Service

File: services/aggregator.py

Responsibilities:

- Run all scrapers
- Collect results
- Isolate failures
- Return aggregated list

Tasks:

- [ ] Implement Aggregator class
- [ ] Accept list of scrapers in constructor
- [ ] Loop through scrapers
- [ ] Catch and log errors
- [ ] Continue execution if one scraper fails
- [ ] Return unified list of Property

Optional enhancement:

- [ ] Add concurrency with ThreadPoolExecutor (one thread per scraper)
- [ ] Add per-scraper timeout safety

---

# PHASE 6 — API Layer (FastAPI)

File: api/main.py

Tasks:

- [ ] Implement FastAPI application
- [ ] Create GET /properties endpoint
- [ ] Return JSON list of Property
- [ ] Add optional filters:
  - city
  - min_price
  - max_price
  - bedrooms
- [ ] Ensure API layer contains no scraping logic
- [ ] Ensure API layer contains no business logic

---

# PHASE 7 — Configuration

File: config/settings.py

Centralize:

- [ ] Agency URLs
- [ ] Request timeouts
- [ ] Max pages per scraper
- [ ] User agent string
- [ ] Browser usage flags
- [ ] Concurrency configuration

Ensure no hardcoded configuration inside scrapers.

---

# PHASE 8 — Logging

- [ ] Implement structured logging
- [ ] Include:
  - scraper name
  - URL
  - duration
  - number of properties collected
  - error message (if any)
- [ ] Remove print statements
- [ ] Ensure aggregator logs scraper failures

---

# PHASE 9 — Testing

## 9.1 Unit Tests

- [ ] Test parse_price
- [ ] Test parse_area
- [ ] Test safe_int
- [ ] Test safe_float
- [ ] Test URL normalization
- [ ] Test whitespace normalization

## 9.2 Scraper Tests

- [ ] Use saved HTML fixtures
- [ ] Mock HTTP client
- [ ] Validate normalized Property output

## 9.3 Aggregator Tests

- [ ] Mock scrapers
- [ ] Ensure failure isolation
- [ ] Ensure aggregation correctness

Rules:

- Do not test live websites in CI

---

# PHASE 10 — Minimal UI

Requirements:

- Table view
- Sorting by price
- Filter by city
- Filter by bedrooms

Tasks:

- [ ] Implement simple UI (React or server-rendered)
- [ ] Connect to GET /properties
- [ ] Render table
- [ ] Implement sorting
- [ ] Implement filtering

No complex UX.

---

# PHASE 11 — Definition of Done

Project is complete when:

- [ ] 30–40 agencies implemented
- [ ] All return normalized Property objects
- [ ] Aggregator merges correctly
- [ ] API returns unified JSON
- [ ] UI renders properties table
- [ ] Parsing utilities fully tested
- [ ] Scrapers isolated and independent
- [ ] No unnecessary abstraction layers exist
- [ ] Code remains simple and maintainable

---

# Anti-Overengineering Checklist

Before merging any PR, verify:

- No Repository pattern (unless database introduced)
- No UseCase layer
- No pipeline abstractions
- No abstract factories
- No command pattern
- No speculative complexity

Architecture must remain minimal.
