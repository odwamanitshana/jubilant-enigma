# Task 06 — Data quality layer and pytest suite

**Depends on:** Task 05
**Blocks:** Task 11

## Problem

The pipeline has no tests and no mechanism for handling bad rows: anything that survives `fillna` defaults gets loaded, and anything that throws kills the whole file. Production ETL needs a reject/quarantine path and regression coverage for transform logic.

## Requirements

### Data quality

1. Define row-level validation rules applied after transform:
   - `product_key` non-empty (should always hold; guard anyway).
   - `price_pkr >= 0` and `price_pkr < 10_000_000` (sanity bound).
   - `product_name` not equal to the `'unknown'` default AND `products_href` non-empty — at least one of the two must carry real data, otherwise the row is unusable.
   - `gender` in `{'men', 'women', 'unisex', 'boys', 'girls'}` after lowercasing; unknown values are coerced to `'unisex'` with a counted warning (coercion, not rejection).
2. Rows failing validation are **not loaded**. They are written to `data/rejects/rejects_<original-stem>_<timestamp>.csv` with an added `reject_reason` column. Create the directory if needed; it must be covered by `.gitignore` (extend it if necessary).
3. End-of-file summary log: `Processed <file>: N extracted, N loaded, N rejected, N duplicates dropped`.
4. Rejects do not fail the run. The exit code from Task 05 stays 0 if every file processes, even with rejects; a file where 100% of rows are rejected should log an error and count as a failed file.

### Tests

5. Add `pytest` (and any needed plugins) to `requirements.txt` under a clearly commented dev section, or add a separate `requirements-dev.txt` — either is acceptable; document the choice in the README.
6. Create `ETL/tests/test_transform.py` covering at minimum:
   - Column renaming from scraper names (`Products-href` → `products_href`, etc.).
   - Missing columns added with correct defaults.
   - `price_pkr` coercion: numeric strings, garbage strings, NaN → 0, floats truncated to int.
   - Text standardization (lowercase, strip).
   - `discount_pct` parsing cases from Task 05.
   - URL validation cases from Task 05.
   - `product_key` stability: same href (with/without trailing slash, different case) → same key; different hrefs → different keys.
7. Create `ETL/tests/test_validation.py` covering each validation rule and the reject-reason labeling.
8. All tests must run without a database or network: transform and validation logic must be importable and testable in isolation. If Task 05's structure makes this awkward, extract transform/validation into functions that take and return DataFrames (they mostly already do).
9. Add a short `## Testing` section to the root README (`pytest ETL/tests`).

## Acceptance criteria

- [ ] `pytest ETL/tests` passes in a clean virtualenv with no MySQL running.
- [ ] A synthetic CSV containing 2 valid rows, 1 negative-price row, and 1 all-defaults row loads 2 rows and writes 2 rejects with distinct `reject_reason` values.
- [ ] Summary log line appears per processed file with all four counts.
- [ ] `data/rejects/` is git-ignored.
- [ ] Test count is at least 15 and covers every bullet in requirements 6–7.
