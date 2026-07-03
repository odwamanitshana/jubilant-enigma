# Task 04 — Schema v2: unique key, timestamps, and idempotent upsert loads

**Depends on:** Task 03
**Blocks:** Tasks 05, 07, 08, 09

## Problem

`wardrobe_items` has no unique constraint and no timestamps, so re-running the pipeline duplicates every product. The pipeline must become idempotent: re-ingesting the same scrape updates existing rows instead of inserting duplicates.

There is also schema duplication: `wardrobe-db/sql/schema.sql` and `wardrobe-db/sql/migrations/001_create_wardrobe_items_table.sql` contain the same `CREATE TABLE` statement and can drift.

## Requirements

### Migration

1. Create `wardrobe-db/sql/migrations/002_wardrobe_items_constraints.sql` that:
   - Adds `product_key CHAR(64) NOT NULL` — a SHA-256 hex digest of the normalized `products_href` (lowercased, trailing-slash-stripped). A hash column is used because `products_href` is `TEXT` and MySQL cannot put a full unique index on unbounded TEXT.
   - Adds `UNIQUE KEY uq_wardrobe_items_product_key (product_key)`.
   - Adds `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`.
   - Adds `updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`.
   - Adds `last_seen_at TIMESTAMP NULL` — set by the pipeline on every run in which the product appears in a source file.
   - Adds secondary indexes to support upcoming query patterns: `(main_category)`, `(gender)`, `(price_pkr)`, `(occasion)`, `(season)`.
   - Handles pre-existing rows: backfill `product_key` from `products_href` before adding the unique constraint, and delete duplicate rows (keep lowest `id`) so the constraint can be applied. Use SQL only; the migration must run via the `mysql` CLI.
2. Update `wardrobe-db/sql/schema.sql` to reflect the full post-migration schema. From now on `schema.sql` is documentation of current state; migrations are the change mechanism (this convention is stated in `tasks/README.md`).
3. Update `wardrobe-db/sql/seeds/seed_wardrobe_items.sql` so seed rows include valid `product_key` values (any distinct 64-char hex strings are fine for seeds).

### Pipeline

4. In `ETL/pipeline.py`:
   - Compute `product_key` during transform: `hashlib.sha256(normalized_href.encode()).hexdigest()`, where `normalized_href` is `products_href` stripped, lowercased, with any trailing `/` removed. Rows with empty `products_href` get a key derived from `product_name + image_url_src` as a fallback, and a warning is logged.
   - Change the INSERT built in Task 03 to `INSERT ... ON DUPLICATE KEY UPDATE`, updating all product attribute columns plus `last_seen_at = CURRENT_TIMESTAMP`. Do not update `created_at`.
   - Deduplicate the DataFrame on `product_key` before load (keep last occurrence), logging how many in-batch duplicates were dropped. MySQL's `executemany` with ON DUPLICATE KEY can error on intra-batch duplicate keys, so this is required for correctness, not just hygiene.

## Out of scope

- Brand extraction (Task 07) and price history (Task 08).
- Normalizing the table into brands/categories — single-table design stays for now.

## Acceptance criteria

- [ ] Migration 002 runs cleanly via `run_migrations.sh` on both an empty table and a table pre-populated with duplicate `products_href` rows.
- [ ] `schema.sql` matches the actual post-migration schema (verify with `SHOW CREATE TABLE wardrobe_items`).
- [ ] Running the pipeline twice on the same CSV yields the same row count as running it once, with `updated_at`/`last_seen_at` refreshed on the second run.
- [ ] In-batch duplicate `products_href` rows collapse to one row, with a log line reporting the drop count.
- [ ] Seeds still load without constraint violations.
- [ ] Document the double-run idempotency verification (commands + row counts) in the PR description.
