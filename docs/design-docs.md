## 1. Project Overview

This system is an **on-demand real estate search engine**. Instead of passively crawling, it translates user search criteria into real-time queries across 30–40 agency websites.

Core responsibilities:

1. Receive search parameters from the user (Price, Bedrooms, Bathrooms, City).
2. Execute parallel searches across multiple agencies.
3. Translate abstract filters into agency-specific URL parameters.
4. Normalize and programmatically filter results to ensure consistency.
5. Present a unified, paginated table of results.

---

## 2. System Context

**Actors:**

- **User:** Defines search criteria via the Frontend.
- **Real Estate Websites:** External sources of truth for property listings.

**System Components:**

- **UI:** A simple search form and results table.
- **API (FastAPI):** Receives search requests and triggers the Aggregator.
- **Aggregator:** Manages the lifecycle of the search, concurrency, and final filtering.
- **Scraper Engine:** Individual modules tailored to translate queries and extract data from specific sites.

---

## 3. Data Flow (On-Demand Search)

1. **User Input:** User selects filters (e.g., Bedrooms $\ge$ 2, Max Price: 500k).
2. **Query Initialization:** The API creates a `SearchQuery` object.
3. **Parallel Dispatch:** The Aggregator uses `ThreadPoolExecutor` to trigger all registered scrapers.
4. **Scraper Translation:**

- Each scraper attempts to map the `SearchQuery` to the agency's native search URL.
- If the agency's filter is "Exact Match" only, the scraper fetches the exact match or a broader list.

5. **Data Extraction:** Scrapers parse listing cards into normalized `Property` objects.
6. **Programmatic Safety Filter:** The Aggregator performs a final check on all returned properties to ensure they strictly meet the $\ge$ requirements for rooms and price ranges.
7. **Consolidation:** Results are merged into a single list and returned to the UI.

---

## 4. Search & Normalization Strategy

### The "Safety Net" Filtering

Since agencies handle filters inconsistently (e.g., some use "Exact" for bedrooms while the user wants "At least"), the system adopts a **double-filtering approach**:

- **Remote Filter:** Use the agency's website filters to minimize traffic and improve speed.
- **Local Filter:** The code explicitly re-checks every property (e.g., `if property.bedrooms >= query.min_bedrooms`) to guarantee accuracy.

### Normalization Rules

- **Prices:** Stored as `float`.
- **Area:** Stored as `float` (m²).
- **Bedrooms/Bathrooms:** Stored as `int`.
- **Missing values:** Represented as `None`.
- **URLs:** Always converted to absolute URLs before returning.

---

## 5. Scraping & Concurrency

### Execution Model

- **Concurrency:** Powered by `ThreadPoolExecutor`.
- **Resource Prioritization:**

1. Direct JSON APIs (Fastest).
2. Static HTML via `requests`/`http_client` (Efficient).
3. Browser Automation (Last resort for JS-heavy sites).

### Reliability

- Each scraper must fail independently.
- A 15-second timeout is enforced per scraper to prevent the UI from hanging.

---

## 6. UI Design

**Search Form:**

- Number of Bedrooms (Dropdown/Input: $\ge$ X).
- Number of Bathrooms (Dropdown/Input: $\ge$ X).
- Price Range (Min/Max inputs).
- City (Text/Selection).

**Results Display:**

- Unified paginated table.
- Columns: Agency, Title, Price, Area, Rooms, Neighborhood, Link.
- Simple "Sort by Price" functionality.

---

## 7. Risk Assessment & Mitigation

| Risk                          | Mitigation Strategy                                                                 |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| **Site Filter Inconsistency** | Apply programmatic $\ge$ logic after results are collected.                         |
| **IP Blocking (Anti-Bot)**    | Prioritize HTTP requests, use User-Agents, and avoid unnecessary browser rendering. |
| **Slow Performance**          | Parallelize agency requests and limit pagination depth.                             |
| **Structure Changes**         | Isolated scraper files allow for quick updates without touching the core.           |

---

## 8. Definition of Done

The project is complete when:

- [ ] Users can trigger a real-time search from the UI.
- [ ] At least 30 agencies are implemented as individual scrapers.
- [ ] The Aggregator successfully merges results in parallel using `ThreadPoolExecutor`.
- [ ] All results strictly follow the $\ge$ filter rules regardless of the source website's logic.
- [ ] The API returns a clean, unified JSON structure.
