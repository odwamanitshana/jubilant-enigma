# Task 11 — CI pipeline (GitHub Actions)

**Depends on:** Task 06 (tests must exist)
**Blocks:** nothing

## Problem

Nothing runs on push/PR, so regressions in transform logic, SQL syntax, or API contracts land silently. Every subsequent task benefits from an automated gate.

## Requirements

1. Create `.github/workflows/ci.yml` triggered on `push` to `main` and on all `pull_request` events.
2. Jobs:
   - **lint** — Python 3.11. Install `ruff`; run `ruff check .` and `ruff format --check .`. Add a minimal `ruff` config (in `pyproject.toml` or `ruff.toml`) with line length 100 and default rule set. Fix any violations in the existing codebase as part of this task (expected to be minor: line lengths, unused imports).
   - **test** — Python 3.11. `pip install -r requirements.txt` (plus dev requirements per Task 06's choice); run `pytest ETL/tests` and, if `api/tests` exists at the time of implementation, `pytest api/tests`. All tests must run without a database (this is already required by Tasks 06/09; do not add a MySQL service container).
   - **sql-check** — spin up `mysql:8` as a service container, run `wardrobe-db/scripts/run_migrations.sh` against it with env-var credentials, then load `wardrobe-db/sql/seeds/seed_wardrobe_items.sql`. This validates that migrations apply in order on a clean database.
3. Use dependency caching (`actions/setup-python` built-in pip cache) to keep runs fast.
4. Add a `ruff` entry to the dev dependencies and a `## CI` note in the README describing what runs.
5. Do not add deployment, publishing, or scheduled-scrape workflows in this task.

## Acceptance criteria

- [ ] The workflow runs on a PR and all three jobs pass on the current codebase.
- [ ] `ruff check .` passes locally after this task's cleanup commits.
- [ ] The `sql-check` job fails if a migration contains a syntax error (verify locally by temporarily breaking a migration, observing failure, then reverting — describe this check in the PR description).
- [ ] Total CI wall time under ~5 minutes with warm caches.
