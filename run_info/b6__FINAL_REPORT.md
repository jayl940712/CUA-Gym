# Batch 6 — 600 medium-difficulty WebArena tasks

All 600 tasks are `medium`, defined for this batch as **exactly two skills: one
retrieval (R) and one action (A)**. Enforced by
`preflight_bundles.py --medium-is-exactly-two`; a three-skill task fails the gate,
so third steps were dropped or split, never relabelled.

## Corpus

| site | tasks | style | start at `/` | retrieval-writeback |
|---|---|---|---|---|
| gitlab | 150 | 113T / 37E | 150/150 | 124 |
| reddit | 150 | 113T / 37E | 145/150 | 126 |
| shopping | 150 | 112T / 38E | 144/150 | 130 |
| shopping_admin | 150 | 112T / 38E | 137/150 | 89 |
| **total** | **600** | **450T / 150E** | **576/600 (96%)** | **469** |

450/150 is exactly the TASK4 corpus split. 244 tasks ship an `initial_setup.py`
precondition injection.

## Validation

| gate | result |
|---|---|
| Bundle gate (`preflight_bundles.py --medium-is-exactly-two`) | **600/600** |
| Empty-state probe (S9.5) | **600/600** score 0.0 on empty `current_state` |
| Verification, all five S9 conditions | **600/600** |
| Click-reachability (S6) | **600/600**, zero `goto` waivers |
| Flake re-test | 8 flagged, **24/24 clean** on re-run — convergence, not flakiness |
| NeMo export | **600/600 rows** |

Verification ran in **legacy** mode: `--mode hardened` was requested but
`CUA_GYM_ADMIN_TOKEN` is empty in `.env`, so it fell back. Batch 5 ran entirely in
legacy too (1360 legacy / 0 hardened), so this matches the accepted baseline;
batch 6 additionally got 9 runs through in hardened mode.

## Issues found and fixed during validation

1. **Verification sub-agents were being killed at a 600s background-wait ceiling**
   (`Background tasks still running after 600s; terminating`). Exit code 0, no
   verdict, so it looked like a task defect. Fixed with
   `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` plus a 45-minute task timeout; the
   affected runs then passed. Cost two orchestrator restarts, because the first
   raised ceiling (1200s) was sized without consulting the duration distribution
   (p99 1118s, max 1257s) and was still too small.

2. **Two rewards paid on the initial lane** — 0.5 and 0.4 at t=0, i.e. credit for
   doing nothing. The verification loop caught both and drove them to 0.0. Across
   all 600 runs only these two ever exhibited it.

3. **Two bundles inlined a stale reward** into `nemo_task.json` while the on-disk
   `nemo_reward.py` carried the loop's repaired version — different components and
   weights. Verification ran the on-disk file, training would have used the inlined
   one. Re-inlined from the authoritative on-disk artifacts.

4. **Three reporting bugs in the gates themselves**, all under-counting healthy
   runs because they assumed one artifact layout: non-numeric attempt labels
   (`attempt-fresh-2`, `attempt-1-legacy`, `attempt-debug4`) read as "no
   verification.json"; a run whose verdict lives only in `audit_sandbox/REVIEW.md`
   read as permanently in-flight; and round ordering. Round ordering needed both
   rules — numeric when every label is a plain `attempt-<int>` (files get rewritten
   out of order, so mtime picks a superseded round), mtime otherwise (numbers from
   different naming schemes are not comparable). Fixed in both `_b5_status.py` and
   `export_nemo_rollouts.py`.

## Ground-truth corrections

65 findings recorded in `CORRECTIONS.md` (B6-1 … B6-65), many overturning census
cells or the lane briefs themselves. The ones that changed task design most:

* reddit `commentCount` disagrees with actual comment rows in **6,475 of 8,012**
  submissions — no task may derive a comment count from either surface.
* shopping storefront search matches name/sku/url_key/description only — **never
  review bodies**; any review-text retrieval must be re-grounded on the PDP tab.
* storefront order addresses are **not editable** (`placeOrder` is the only writer);
  the benchmark's own `webarena-794` says so. A11 must target the address book.
* the field is **`special_price`**, not `specialPrice` — a reward keyed on the
  camelCase spelling reads nothing, silently.
* **689 reviews carry `rating: null`** and render with no stars, so a rating-bounded
  count over such a product has two defensible answers. Clean pool is 1,894 products,
  not 6,044.
* injected reviews always render at the **tail** of the Created-descending admin grid
  (`reviewRank()` ranks unmeasured ids as `351 + id`).
* the admin Dashboard answers "top search term" and "best seller" **on `/`**, so those
  retrievals cannot be forced; its Bestsellers tile also disagrees with the report.

Two errors of mine that lanes caught: shopping_admin lanes were briefed with the
**storefront** review-corpus figures (the admin corpus is 351 rows and clean), and a
timezone finding scoped to 12 open orders was over-generalised to all 308 (59 of
which render a day earlier than they filter).
