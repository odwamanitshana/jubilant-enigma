# Task 03 — Bulk insert and batched commits in `load_data`

**Depends on:** Task 01 (so you are not working on top of committed credentials)
**Blocks:** Tasks 04, 05

## Problem

`load_data()` in `ETL/pipeline.py` inserts rows one at a time inside a `for idx, row in insert_df.iterrows()` loop, with a single commit at the very end. For catalogs of tens of thousands of rows this is orders of magnitude slower than necessary and holds one long transaction open.

## Requirements

1. Replace the per-row `cursor.execute()` loop with batched `cursor.executemany()` calls.
   - Batch size: 1000 rows, defined as a module-level constant `BATCH_SIZE` so it is easy to tune.
   - Build the list of value tuples from the DataFrame without `iterrows()` (use `itertuples(index=False)` or `df.to_numpy().tolist()` — `iterrows` is slow and loses dtypes).
2. Commit after each batch instead of once at the end. If a batch fails, roll back that batch's transaction, log the error with the batch's row range, and re-raise (keep current fail-fast behavior; partial-failure tolerance is Task 06's concern).
3. Keep the existing INSERT column list and SQL statement semantics unchanged — this task changes the execution strategy only. (Upsert semantics come in Task 04.)
4. Preserve progress logging: log every completed batch as `Inserted rows X–Y of N`.
5. Ensure NaN/NA values in the DataFrame are converted to `None` before insert (MySQL connector does not accept `nan` floats for text columns). Handle this explicitly in `load_data` rather than relying on upstream transforms.
6. Measure and log total load duration and rows/second at the end of `load_data`.

## Out of scope

- Schema changes, unique keys, upserts (Task 04).
- `LOAD DATA INFILE` (may be a future optimization; not now).
- Refactoring column definitions (Task 05).

## Acceptance criteria

- [ ] No `iterrows()` remains in `load_data`.
- [ ] Inserts execute via `executemany` in batches of `BATCH_SIZE` with a commit per batch.
- [ ] A DataFrame containing NaN in text and numeric columns loads without connector errors (NaN → NULL).
- [ ] Log output includes per-batch progress and a final duration/throughput line.
- [ ] Loading a 10,000-row synthetic DataFrame into a local MySQL completes and the table contains exactly 10,000 new rows. Document the manual verification (commands + output) in the PR description.
