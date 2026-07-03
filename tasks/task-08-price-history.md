# Task 08 — Price history tracking

**Depends on:** Tasks 04, 07
**Blocks:** nothing (enables future deal-alert features)

## Problem

Each scrape overwrite loses the previous price (Task 04 upsert updates `price_pkr` in place). Price-over-time is the foundation for "price dropped" collections and comparison features — a core value proposition of comparable products (TrendCompare shows hourly price freshness).

## Requirements

1. Migration `005_create_price_history.sql`:

   ```sql
   CREATE TABLE price_history (
       id BIGINT PRIMARY KEY AUTO_INCREMENT,
       product_key CHAR(64) NOT NULL,
       price_pkr INT NOT NULL,
       discount_pct TINYINT NOT NULL DEFAULT 0,
       recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       KEY idx_price_history_product (product_key, recorded_at)
   );
   ```

   Update `schema.sql`. (No foreign key to `wardrobe_items.product_key` — keep tables decoupled so history survives catalog row deletions; note this decision in a SQL comment.)
2. Pipeline change: after upserting a batch into `wardrobe_items`, insert a `price_history` row for each product whose price **changed or is new**:
   - Before loading a file, fetch current `(product_key, price_pkr, discount_pct)` for the file's product keys in one query (chunk the `IN` list at 1000 keys).
   - Compare in Python; insert history rows only for new keys or changed price/discount. Use `executemany` batching consistent with Task 03.
   - Log: `Price history: N new products, N price changes recorded, N unchanged`.
3. First-ever sight of a product records its initial price (so every product has at least one history row after its first load).
4. Add unit tests for the change-detection function (pure function comparing current-DB map vs incoming rows, returning rows to insert). No DB needed for the tests; the DB fetch is a thin wrapper.

## Out of scope

- API exposure of history (extend Task 09 later).
- Alerts/notifications.
- Backfilling history for rows loaded before this task (initial prices will be captured on each product's next appearance in a scrape).

## Acceptance criteria

- [ ] Migration 005 applies cleanly; `schema.sql` updated with the new table.
- [ ] Loading a file twice with identical prices creates exactly one history row per product.
- [ ] Editing a price in the source CSV and re-running adds exactly one new history row for that product only.
- [ ] Change-detection unit tests pass without a DB.
- [ ] Include the two-run verification queries and outputs in the PR description.
