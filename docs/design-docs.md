# Design Documentation

## 1. Project Overview

This system aggregates property listings from 30–40 real estate agency websites.

Core responsibilities:

1. Fetch listings from each agency
2. Extract structured property data
3. Normalize into standard model
4. Aggregate all results
5. Return as unified table (API response)

---

## 2. System Context

Actors:

- User (via UI or API)
- Real estate websites

System:

- Scraper engine
- Aggregator
- API

External dependencies:

- HTTP endpoints
- Possibly JavaScript-rendered pages

---

## 3. Data Flow

For each agency:

1. Fetch URL
2. Parse listing cards
3. Extract raw values
4. Normalize fields
5. Return list of Property

Then:

6. Aggregator merges all results
7. API returns JSON
8. UI renders table

---

## 4. Property Normalization Strategy

Challenges:

- Price formats differ
- Area may include units
- Missing fields
- Different currency formats

Normalization rules:

- Prices stored as float
- Area stored as float (m²)
- Bedrooms/bathrooms as int
- Missing values = None
- URLs must be absolute

---

## 5. Scraping Strategy

Preferred order:

1. Direct JSON API endpoint (best case)
2. Static HTML via requests
3. JavaScript-rendered page via browser automation

Avoid always using browser automation.

Performance matters with 40 agencies.

---

## 6. Pagination Handling

Each scraper is responsible for:

- Detecting pagination
- Iterating through pages
- Respecting max page limits

Global safety:

- Add max_pages config
- Add timeout per request

---

## 7. Concurrency Design (Optional Enhancement)

If needed:

- Use ThreadPoolExecutor
- One thread per scraper
- Collect results safely

Do not introduce async unless necessary.

---

## 8. Error Isolation

If one scraper fails:

- Log error
- Continue others
- Do not fail entire aggregation

Each scraper must fail independently.

---

## 9. Configuration Design

config/settings.py:

- Agency URLs
- Timeouts
- Max pages
- Use browser flag
- User agent string

Keep configuration centralized.

---

## 10. Logging Strategy

Structured logging:

- scraper name
- URL
- error message
- duration
- number of properties collected

Never use print statements.

---

## 11. Testing Strategy

Unit tests:

- Parsing utilities
- Price normalization
- Area normalization
- HTML fixture parsing

Integration tests:

- Mock HTTP client
- Validate Property output

Do not test live websites in CI.

---

## 12. UI Design

Minimal interface:

- Table view
- Sorting by price
- Filtering by city
- Filter by bedrooms

No complex UX required.

Simple React or server-rendered HTML is enough.

---

## 13. Extension Possibilities

Future features:

- Store properties in database
- Detect price changes
- Deduplicate by URL
- Track listing history
- Scheduled scraping
- Export CSV

If persistence is added:

Introduce repository layer and ID strategy.

---

## 14. Risk Assessment

Main risks:

- Website structure changes
- Anti-bot blocking
- Rate limiting
- Inconsistent data formats

Mitigation:

- Per-scraper isolation
- Logging and monitoring
- Fail-soft aggregation
- Timeouts

---

## 15. Definition of Done

Project is complete when:

- 30–40 agencies implemented
- Each returns normalized Property objects
- Aggregator merges correctly
- API returns unified JSON
- UI displays table
- Code remains simple and maintainable
- No unnecessary abstraction layers
