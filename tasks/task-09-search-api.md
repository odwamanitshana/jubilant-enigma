# Task 09 — Search and filter API (FastAPI)

**Depends on:** Tasks 04, 07
**Blocks:** Task 10

## Problem

The catalog is only reachable via raw SQL. Every user-facing feature (search, brand comparison, outfit engine, future frontend) needs a read API. Comparable products expose search across brand, price, occasion, and category as their core interaction (TrendCompare: "lawn suits under 5,000"; AuraFit: occasion collections).

## Requirements

### Stack and layout

1. New top-level package `api/`:

   ```
   api/
   ├── main.py          # FastAPI app factory + routes
   ├── db.py            # connection pooling (mysql-connector pooling or SQLAlchemy)
   ├── schemas.py       # Pydantic response models
   └── queries.py       # SQL builders (parameterized only, no string interpolation of user input)
   ```

2. Dependencies: `fastapi`, `uvicorn`. Add to `requirements.txt`. Reuse the existing `.env` DB config keys.

### Endpoints (all read-only, JSON)

3. `GET /health` → `{"status": "ok"}` plus a DB connectivity check.
4. `GET /items` with query params:
   - `q` — free-text match against `product_name` and `work_details` (SQL `LIKE %q%` is acceptable at this stage; note FULLTEXT as a future optimization in a comment)
   - `brand`, `main_category`, `gender`, `occasion`, `season`, `color`, `fabric` — exact-match filters (all optional, combinable)
   - `min_price`, `max_price` — bounds on `price_pkr`
   - `min_discount` — bound on `discount_pct`
   - `sort` — one of `price_asc`, `price_desc`, `newest` (by `created_at`), `discount_desc`; default `newest`
   - `page` (default 1), `page_size` (default 20, max 100)
   - Response: `{"items": [...], "total": int, "page": int, "page_size": int}`. `total` from `SELECT COUNT(*)` with the same filters.
5. `GET /items/{product_key}` → single item or 404.
6. `GET /brands` → list of `{brand, item_count, min_price, max_price}` aggregates.
7. `GET /facets` → distinct values with counts for `main_category`, `occasion`, `season`, `gender`, `color`, `fabric` (for building filter UIs). Cap each facet list at 50 values ordered by count.

### Quality

8. All user input goes through parameterized queries — build WHERE clauses from a whitelist of allowed filter columns. Reject unknown `sort` values with 422 (FastAPI enum/Literal handles this).
9. Pydantic response models for items (exclude `web_scraper_start_url`; include everything else plus `product_key`).
10. Tests in `api/tests/`: use FastAPI's `TestClient` with the query layer faked/mocked, covering: pagination math, filter combination (WHERE clause builder unit tests), sort whitelist, 404 on missing item. DB-integration tests are optional; if included, skip them automatically when `DB_HOST` is unreachable.
11. README section: how to run (`uvicorn api.main:app --reload`), with 3–4 example curl requests (e.g. `curl 'localhost:8000/items?occasion=formal&max_price=5000&sort=price_asc'`).

## Acceptance criteria

- [ ] `uvicorn api.main:app` starts and `/health` returns 200 with a live DB.
- [ ] `/items?brand=khaadi&max_price=5000&sort=price_asc` returns only matching rows, sorted, paginated, with correct `total`.
- [ ] Combining every filter param in one request works and returns 200.
- [ ] No f-string/`%`-interpolated user input anywhere in SQL (verify by inspection of `queries.py`).
- [ ] `pytest api/tests` passes without a live database.
- [ ] OpenAPI docs at `/docs` render all endpoints with typed params.
