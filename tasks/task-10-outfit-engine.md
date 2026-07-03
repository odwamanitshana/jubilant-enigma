# Task 10 — Rule-based outfit matching engine

**Depends on:** Task 09
**Blocks:** nothing (future AI stylist builds on this)

## Problem

The differentiating product feature is complete outfit suggestions ("clothing + matching shoes for a Mehndi under PKR 10,000"), not just item search. The schema already carries the needed dimensions: `main_category`, `occasion`, `season`, `color`, `categorize_outfit`, `shoe_color`, `shoe_style`, `gender`, `price_pkr`. A deterministic rule engine delivers this without ML, and becomes the baseline/fallback for a future AI stylist.

## Requirements

### Matching rules (module `api/outfits.py`)

1. An outfit = one **clothing item** (`main_category` indicates clothing, not shoes/accessories) + one **shoes item** (`main_category` indicates shoes). Determine category membership from the distinct values actually present in the DB; define two whitelists `CLOTHING_CATEGORIES` and `SHOE_CATEGORIES` as module constants with a comment on how to extend them.
2. Compatibility scoring between a clothing item C and shoe item S (0–100):
   - **Gender**: hard filter — must match exactly, or either side is `unisex`. Non-matching pairs are never returned.
   - **Occasion** (weight 35): exact match 35; either side `general` 20; mismatch 0.
   - **Season** (weight 25): exact match 25; either side `all-season` 15; mismatch 0.
   - **Color harmony** (weight 25): define `NEUTRAL_COLORS = {black, white, grey, gray, beige, tan, brown, cream, off-white, unknown}`. Shoe color neutral OR exact color match → 25; complementary pairs from a small `COLOR_PAIRS` table (e.g. navy↔brown, blue↔tan, green↔beige — include at least 10 pairs) → 20; otherwise 5.
   - **Style** (weight 15): `category_style` == `shoe_style` (case-insensitive substring match either direction) → 15; otherwise 5.
   - Score = sum. Pairs below `MIN_SCORE = 50` are excluded.
3. Scoring is a pure function `score_pair(clothing_row, shoe_row) -> int` — trivially unit-testable.

### Endpoint

4. `GET /outfits` with params:
   - `occasion` (required — e.g. `casual`, `formal`, `party`, `wedding`)
   - `gender` (required)
   - `season` (optional)
   - `budget_pkr` (optional — max combined `price_pkr` of the pair)
   - `brand` (optional — applies to the clothing item only)
   - `limit` (default 10, max 30)
   - Response: list of `{clothing: Item, shoes: Item, total_price_pkr, score}` sorted by score desc, then total price asc.
5. Implementation approach: fetch candidate clothing (filtered by occasion/gender/season/brand, in stock of data, capped at 200 by newest) and candidate shoes (same filters minus brand, capped at 200), score the cross product in Python, return top `limit`. This is O(40k) score calls max — fine. Leave a comment noting precomputed pair tables as the scaling path.
6. Empty-result behavior: if no pairs clear `MIN_SCORE`, relax once by including `general`-occasion candidates and rescore; if still empty return `200` with `{"outfits": [], "message": "No matching outfits found — try a different occasion or higher budget."}`. Never 404 for empty results.

### Tests

7. Unit tests for `score_pair` covering: perfect match, gender hard-filter, neutral-shoe bonus, complementary colors, all-season partials, below-threshold exclusion.
8. Endpoint tests with faked candidate fetch covering: budget filtering, sort order, the relaxation path, and the empty-result message.

## Acceptance criteria

- [ ] `GET /outfits?occasion=casual&gender=women&budget_pkr=10000` on seeded data returns scored pairs within budget, sorted by score.
- [ ] No returned pair violates the gender rule.
- [ ] `score_pair` unit tests pass and cover every scoring component.
- [ ] Empty-result path returns 200 with the guidance message.
- [ ] Endpoint appears in OpenAPI docs with typed/validated params (unknown `occasion` values are allowed — free text; missing required params → 422).
