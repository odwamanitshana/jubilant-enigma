# Task 02 — Project scaffolding: dependencies, license, README

**Depends on:** nothing
**Blocks:** nothing (but should land early)

## Problem

The project has no dependency manifest, so it cannot be reproducibly installed. `wardrobe-db/README.md` claims MIT licensing but no `LICENSE` file exists. The root `README.md` is two lines and does not explain how to run anything.

## Requirements

1. Add a root `requirements.txt` pinning the three runtime dependencies used by `ETL/pipeline.py` to current stable major versions:
   - `pandas`
   - `mysql-connector-python`
   - `python-dotenv`

   Pin with compatible-release specifiers (e.g. `pandas~=2.2`) rather than exact patch versions. Verify each pinned version actually installs together in a fresh virtualenv before finalizing.
2. Add `LICENSE` at the repo root containing the MIT license text. Use the repository owner's GitHub name as the copyright holder and the current year.
3. Rewrite the root `README.md` to cover:
   - What the project is (fashion catalog ETL: scraped CSVs → MySQL `wardrobe_items`).
   - Repo layout (`ETL/`, `wardrobe-db/`, expected-but-untracked `data/raw/` and `data/processed/`).
   - Setup: create virtualenv, `pip install -r requirements.txt`, configure `.env` (see `ETL/.env.example` from Task 01 — if Task 01 has not landed yet, still reference the flow), run migrations, run the pipeline.
   - The expected input CSV format: scraper columns such as `web-scraper-start-url`, `Products-href`, `Image URL-src`, `Gender`, `Category Style` (see `column_mapping` in `ETL/pipeline.py` for the full mapping).
4. Do not modify any Python or SQL logic in this task.

## Acceptance criteria

- [ ] `pip install -r requirements.txt` succeeds in a clean Python 3.10+ virtualenv, and `python -c "import pandas, mysql.connector, dotenv"` succeeds afterward.
- [ ] `LICENSE` exists at the repo root with MIT text.
- [ ] Root README contains setup, run, and data-format sections; a newcomer can go from clone to running pipeline (given a MySQL instance) using only the README.
- [ ] No changes to `ETL/pipeline.py` or files under `wardrobe-db/sql/`.
