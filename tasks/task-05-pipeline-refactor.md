# Task 05 — Pipeline refactor: shared config, robust paths, exit codes, discount parsing

**Depends on:** Tasks 03, 04
**Blocks:** Tasks 06, 07

## Problem

`ETL/pipeline.py` has several maintainability defects:

- The column list is defined twice: `expected_columns` dict in `transform_data()` and `expected_columns` list in `load_data()`. They can drift.
- Data paths are relative to the process CWD (`../data/raw`, `../data/processed`), so the script only works when run from inside `ETL/`.
- `main()` catches all exceptions and returns normally, so schedulers/CI cannot detect failure (exit code is always 0).
- A comment says "Validate URLs" but the code only does `fillna('')`.
- `discount` is stored as a raw string like `"10%"`, unusable for filtering or sorting.
- `df.fillna(expected_columns)` mixes dtypes (int default for `price_pkr`, strings elsewhere) which can behave unpredictably.

## Requirements

1. **Single source of column truth.** Create a module-level structure (e.g. `COLUMNS: dict[str, ColumnSpec]` or an ordered dict of `{name: default}` plus a derived `COLUMN_ORDER` list) used by both transform and load. The INSERT statement's column list must be generated from it.
2. **Robust paths.** Resolve `data/raw` and `data/processed` relative to the repository root using `Path(__file__).resolve().parent.parent / "data" / "raw"`. Allow override via env vars `RAW_DATA_DIR` and `PROCESSED_DATA_DIR`.
3. **Exit codes.** `main()` returns an int; `sys.exit(main())` at the bottom. Return non-zero on: missing env vars, missing data dir, DB connection failure, or any file failing to process. Per-file failures should be logged and counted, then reflected in the exit code after all files are attempted (process remaining files rather than aborting on the first bad file).
4. **Real URL validation.** In transform, validate `products_href` and `image_url_src` with `urllib.parse.urlparse`: scheme must be `http`/`https` and netloc non-empty. Invalid URLs are replaced with `''` and counted in a warning log. (Quarantining rows is Task 06.)
5. **Discount parsing.** Add a numeric `discount_pct` column (`TINYINT` semantics, 0–100) parsed from strings like `"10%"`, `"10 %"`, `"Rs. 200 off"` (non-percentage forms → 0). Keep the original `discount` string column. This requires a small migration `003_add_discount_pct.sql` adding `discount_pct TINYINT NOT NULL DEFAULT 0` and an update to `schema.sql`, following the migration conventions in `tasks/README.md`.
6. **Explicit NA handling.** Replace the single `df.fillna(expected_columns)` with per-column filling driven by the shared column config, so numeric and text columns are handled with correct dtypes.
7. Keep the file processing flow (extract → transform → save processed CSV → load) and all existing log message styles intact. This is a refactor plus two focused features (validation, discount), not a rewrite.

## Acceptance criteria

- [ ] Exactly one definition of the column set exists in `pipeline.py`; grep for `expected_columns` finds at most one construct.
- [ ] `python ETL/pipeline.py` works when invoked from the repo root, from `ETL/`, and from an unrelated directory (given env vars set).
- [ ] `echo $?` after a run with a missing data dir is non-zero; after a fully successful run it is 0.
- [ ] `discount_pct` is populated: `"15%"` → 15, `"invalid"` → 0, empty → 0.
- [ ] Rows with `products_href` values like `"not a url"` or `"ftp://x"` end up with `''` and a warning naming the count.
- [ ] Migration 003 applies cleanly and `schema.sql` is updated.
