# Task 07 — Brand extraction and normalization

**Depends on:** Tasks 04, 05
**Blocks:** Tasks 08, 09

## Problem

The catalog aggregates multiple Pakistani fashion brands (Khaadi, Limelight, Gul Ahmed, Beechtree, Alkaram, Sapphire, etc.) but stores no `brand` column. Brand is recoverable from `products_href` / `web_scraper_start_url` domains. Brand is a prerequisite for price comparison, brand filtering in the API (Task 09), and per-brand price history (Task 08). Competitors (TrendCompare, AuraFit) treat brand as a first-class dimension.

## Requirements

1. Migration `004_add_brand.sql`: add `brand VARCHAR(100) NOT NULL DEFAULT 'unknown'` plus index `(brand)`. Update `schema.sql`.
2. In the pipeline transform, derive `brand` from the row's URLs:
   - Parse the domain from `products_href`, falling back to `web_scraper_start_url` if empty.
   - Map domains to canonical brand names via a module-level `BRAND_DOMAIN_MAP` dict, e.g. `khaadi.com → khaadi`, `limelight.pk → limelight`, `gulahmedshop.com → gul_ahmed`, `beechtree.pk → beechtree`, `alkaramstudio.com → alkaram`, `pk.sapphireonline.pk`/`sapphireonline.pk → sapphire`, `nishatlinen.com → nishat_linen`, `mariab.pk → maria_b`, `edenrobe.com → edenrobe`, `outfitters.com.pk → outfitters`.
   - Match on registered domain (strip `www.` and subdomains sensibly — matching the map key as a suffix of the hostname is sufficient).
   - Unmapped domains: use the second-level domain name (e.g. `somebrand` from `shop.somebrand.pk`) lowercased, and log a counted warning so new brands are discoverable from logs.
   - No URL at all: `'unknown'`.
3. Canonical brand values are lowercase snake_case. Add the derivation function to the transform module so it is covered by the Task 06 test layout; include tests for: mapped domain, `www.` prefix, subdomain, unmapped domain fallback, empty URL.
4. Add a one-off backfill script `ETL/backfill_brand.py` that updates existing DB rows using the same derivation function (`SELECT id, products_href, web_scraper_start_url` in chunks, compute, `UPDATE`). It must be idempotent and log progress. Reuse the pipeline's DB config handling.

## Acceptance criteria

- [ ] Migration 004 applies cleanly; `schema.sql` updated.
- [ ] New pipeline runs populate `brand` for every row (no NULLs; `'unknown'` allowed).
- [ ] Unit tests cover the five derivation cases listed above and pass without a DB.
- [ ] `backfill_brand.py` run against a table seeded with known URLs sets expected brand values and is safe to run twice.
- [ ] `SELECT brand, COUNT(*) FROM wardrobe_items GROUP BY brand` returns meaningful groupings on real data (include sample output in the PR description if real data is available; otherwise show seed-based output).
