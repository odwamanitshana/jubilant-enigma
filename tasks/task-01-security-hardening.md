# Task 01 — Security hardening: remove committed credentials

**Depends on:** nothing
**Blocks:** Task 03

## Problem

`ETL/.env` is committed to the repository and contains real MySQL credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Anyone with repo access has the database password. There is also no `.gitignore`, so `data/`, `__pycache__/`, and future secrets are at risk of being committed.

Separately, `wardrobe-db/scripts/run_migrations.sh` hardcodes placeholder credentials (`your_username` / `your_password`) instead of reading the same environment variables the ETL uses, so there are two divergent configuration sources.

## Requirements

1. Delete `ETL/.env` from the working tree and stop tracking it in git (`git rm --cached` is not enough on its own — the file must be removed and ignored going forward).
2. Create `ETL/.env.example` with the same keys and placeholder values only:

   ```
   DB_HOST=localhost
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=wardrobe_db
   ```

3. Add a root `.gitignore` covering at minimum:
   - `.env` and `*.env` (but NOT `.env.example`)
   - `data/` (raw and processed CSVs are runtime artifacts, not source)
   - `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/`, `venv/`
   - `.DS_Store`
4. Rewrite `wardrobe-db/scripts/run_migrations.sh` to read `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` from the environment (sourcing a `.env` file if present at a documented path), and to fail with a clear error message if any are unset. Do not keep hardcoded credentials or placeholders as fallbacks for user/password/database.
5. Make the migration script iterate over all `wardrobe-db/sql/migrations/*.sql` files in filename order instead of hardcoding a single file, and use `set -euo pipefail` so failures stop the run. The script must work regardless of the caller's working directory (resolve paths relative to the script's own location).
6. Add a `## Configuration` section to the root `README.md` explaining how to create a local `.env` from `.env.example`.
7. In the PR description, note explicitly that the previously committed password must be rotated by the repo owner, since it remains in git history. (Do NOT attempt to rewrite git history in this task.)

## Out of scope

- Rewriting git history / BFG / filter-repo (owner decision).
- Secrets managers or vaults.
- Any change to `ETL/pipeline.py` logic (it already reads from the environment).

## Acceptance criteria

- [ ] `git ls-files` no longer lists `ETL/.env`.
- [ ] `ETL/.env.example` exists with placeholder values only; no real credentials anywhere in the diff.
- [ ] Root `.gitignore` exists and covers the patterns listed above; `git check-ignore ETL/.env data/raw/x.csv` succeeds for both paths.
- [ ] `run_migrations.sh` exits non-zero with a readable message when `DB_USER` is unset, and runs every file in `sql/migrations/` in order when configured.
- [ ] `bash -n wardrobe-db/scripts/run_migrations.sh` passes (valid syntax).
- [ ] README documents the `.env` setup flow.
