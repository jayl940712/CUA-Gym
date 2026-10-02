# WebArena 200-task batch — progress log

## Phase 1 — Preflight

Run 2026-08-18.

| # | Check | Result |
|---|---|---|
| 1 | All five hub ports answer (`localhost:8000-8004`) | **PASS** — all `200`. tmux session `cua-gym-hub`, 5 windows. |
| 2 | State API round-trip on scratch sid `preflight` | **PASS** — all five return `{initial_state, current_state, state_diff}` with `state_diff == {}` (8000 also returns `revision`). |
| 3 | `python3 -c "import requests, playwright"` | **PASS** |
| 4 | `python3 -m playwright install chromium` | **PASS after fix** — browser binaries were present but chromium could not launch: `libgbm.so.1: cannot open shared object file`. Fixed with `sudo apt-get install -y libgbm1 libasound2`. Chromium now launches (151.0.7922.34). |
| 5 | `python3 -m pytest tests/ -q` | **PASS** — 24 passed. |
| 6 | `.env` endpoints reachable | **PASS** — `http://136.83.9.30:800X/` all return `200` from this host. **No `output/endpoints.json` needed**; `--endpoints` is not passed anywhere. |

Extra: wrote `scripts/preflight_bundles.py` (the Phase-2 mechanical gate) and
validated it against the known-good reference bundle
`output/task_generation/gitlab-workflows/gitlab_triage_backlog_001` — passes.

### Systemic issues found and fixed
- **Missing chromium system libraries** (`libgbm.so.1`, and `libasound2`
  preemptively). Without this every `golden-browser` replay in Phase 3 would
  have failed at browser launch. Fixed by installing the system packages; no
  repo change.

## Phase 2 — Generation

Topic split (5 disjoint batches of 10 per site, 20 batches total, run 4 at a time):

| Site | Batches |
|---|---|
| gitlab | `issue_lifecycle`, `merge_requests`, `labels_milestones`, `repo_project_config`, `people_groups` |
| reddit | `submissions`, `comments_moderation`, `forums`, `voting_subscriptions`, `account_messaging` |
| shopping | `cart`, `wishlist_compare`, `checkout_orders`, `account_addresses`, `reviews_contact` |
| shopping_admin | `order_processing`, `catalog_products`, `customers_content`, `marketing_promotions`, `stores_system` |

### Batch log

- 2026-08-18 — `gitlab/issue_lifecycle`: 10/10 bundles pass the mechanical gate (verified independently, not from the agent self-report). Launched `gitlab/merge_requests`.
- 2026-08-18 — `shopping/cart`: 10/10 pass the gate (independently re-run). Launched `shopping/wishlist_compare`. Running total 20/200.
- 2026-08-18 — `gitlab/merge_requests`: 10/10 pass the gate (gitlab now 20/20 collectively). Launched `gitlab/labels_milestones`. Running total 30/200.
- 2026-08-18 — `reddit/submissions`: 10/10 pass the gate. Author reported one genuine mock limitation: the `userFlag` select in SubmitPage/EditSubmissionPage has only a `(none)` option, so user flair is unreachable through the UI and no task depends on it. Launched `reddit/comments_moderation`. Running total 40/200.
- 2026-08-18 — `shopping_admin/order_processing`: 10/10 pass the gate. Wave 1 (all four sites) now complete. Author's own audit caught and fixed a reward false positive in `fulfill_order_065` (sending the order email flips `is_customer_notified` on the newest history row, which incidentally satisfied the earlier comment component; now keyed to `entity_name == "shipment"`). Launched `shopping_admin/catalog_products`. Running total 50/200.
- 2026-08-18 — `shopping/wishlist_compare`: 10/10 pass the gate (shopping now 20/20). Launched `shopping/checkout_orders`. Running total 60/200.
- 2026-08-18 — `gitlab/labels_milestones`: 10/10 pass the gate (gitlab now 30/30). Author traced all four ⚠ SCHEMA rows it used to real controls before building on them, and rejected four candidates that the mock does not actually support (group milestones are read-only rollups; no `/dashboard/labels` route; no drag-reorder handler for prioritized labels; label delete deliberately does NOT rewrite `issues[].label_ids`, unlike milestone delete). Launched `gitlab/repo_project_config`. Running total 70/200.
- 2026-08-18 — `reddit/comments_moderation`: 10/10 pass the gate (reddit now 20/20). Load-bearing finding reused downstream: `moderates()` reads only `state.moderatorOf` (AppContext.jsx:308), which is EMPTY on the pristine seed, so any task using a moderator-only route on a seeded forum must inject `moderatorOf` in `initial_setup.py` or the route 403s. Launched `reddit/forums`. Running total 80/200.
- 2026-08-18 — `shopping/checkout_orders`: 10/10 pass the gate (shopping now 30/30). Author confirmed "choose a shipping method" is NOT a real choice in this mock (CheckoutPage.jsx renders a single pre-checked Flat Rate row; /multishipping/checkout/ is unmigrated), so shipping is verified via exact flat-rate totals instead of a selection. No task asserts `cart.items`, since Place Order empties it. Launched `shopping/account_addresses`. Running total 90/200.
- 2026-08-18 — `gitlab/repo_project_config`: 10/10 pass the gate (gitlab now 40/40). Traced its three ⚠ rows (create-from-template, delete branch, delete tag) to live controls; rejected import-project (notice-only) and transfer-project (rendered `disabled`) as unsupported. Launched `gitlab/people_groups`, the last gitlab batch. Running total 100/200 — halfway.
- 2026-08-18 — `shopping_admin/catalog_products`: 10/10 pass the gate (shopping_admin now 20/20). Documented runtime dependency: the category-tree Delete goes through the mock's only native `window.confirm` (src/pages/catalog/CategoryPage.jsx:201), so the replay driver must accept that dialog. Launched `shopping_admin/customers_content`. Running total 110/200.
- 2026-08-18 — `reddit/forums`: 10/10 pass the gate (reddit now 30/30). Its live Playwright validation caught a defect the static gate could not see (see systemic issue below). Findings: `ForumDeletePage` permits deletion only when `admin || (moderates(forum) && submissionCount === 0)`, and NO seeded forum has `submissionCount === 0`, so deletable forums must be injected or created in-task. `forums` is a single state key, so setups must read the pristine seed from `/go`, patch it, and `set` the whole state.

### SYSTEMIC ISSUE 2 — JSON fixtures inlined with `json.dumps` (found, fixed, gate extended)

`json.dumps` emits bare `true` / `false` / `null` into Python source. Those are valid Python
identifiers, so the program compiles cleanly, passes every static check, and then raises
`NameError` the moment NeMo runs the episode. Found by the reddit/forums author via a live
Playwright replay; an AST scan across all bundles on disk then showed **all 10
`shopping_checkout_orders_*` bundles carried the same defect** (120/130 passing).

Fix: added a permanent `js_literal_names()` check to `scripts/preflight_bundles.py` (harness
change, deliberate and minimal — it AST-scans both episode programs for JS literals that are
read but never bound). The 10 affected bundles were sent back to their authoring agent to
re-emit with `json.loads`, with an added requirement to execute each setup program against a
live scratch sid rather than relying on `compile()`.
- 2026-08-18 — `shopping/checkout_orders` REPAIRED in place by its authoring agent: all 10 setups re-emitted with `json.loads("""…""")`, then executed against live throwaway sids (all printed `SETUP OK`, `/go` returned `state_diff == {}` and `initial_state == current_state`). Offline 0.0/1.0 discrimination unchanged. Full tree re-gated: **130/130 pass**. No task semantics changed. All remaining prompts now carry the `json.dumps` warning and require live setup execution. Launched `reddit/voting_subscriptions`. Running total 130/200.
- 2026-08-18 — `shopping/account_addresses`: 10/10 pass the gate (shopping now 40/40). Its report claimed `shopping_wishlist_compare_*` also carries raw JSON literals; checked and REJECTED — those ten setups contain no `json.dumps` and zero bare JS literals, and the gate's AST check clears them. Only checkout_orders was ever affected. Launched `shopping/reviews_contact` (last shopping batch; author told to report honestly if the topic cannot yield 10 genuinely distinct tasks rather than padding). Running total 140/200.
- 2026-08-18 — `shopping_admin/customers_content`: 10/10 pass the gate (shopping_admin now 30/30). Its group-migration chain explicitly defeats the rename shortcut (renaming Retailer -> VIP Wholesale scores 0.0). Launched `shopping_admin/marketing_promotions`. Running total 150/200.
- 2026-08-18 — `gitlab/people_groups`: 10/10 pass the gate. **gitlab COMPLETE at 50/50.** Notable: task 007 genuinely requires setup, because a request-then-withdraw pair on one project is a pure no-op that could never satisfy both reward(initial)=0 and reward(golden)=1; its setup injects a pending access-request row so the withdraw is observable. Rejected Invite-a-group, Remove-a-group-share and Import-members. Launched `shopping_admin/stores_system` (last shopping_admin batch). Running total 160/200.
- 2026-08-18 — `shopping/reviews_contact`: 10/10 pass the gate. **shopping COMPLETE at 50/50.** Author reached 10 genuinely distinct tasks without padding (4 workflow shapes, review counts 1/2/3, all five star ratings, 10 different products, 2 lookup-driven writebacks) and explicitly rejected an 11th near-duplicate plus review edit/delete (no handler exists) and the benchmark's "fill but do not submit" contact shape (writes no state). Verified in hub before designing rubrics: `submitReview` stores the star rating as a plain 1-5 Number, and the form's "summary" field is stored as `title`. Launched `reddit/account_messaging` (last batch overall). Running total 170/200.
- 2026-08-18 — `reddit/voting_subscriptions`: 10/10 pass the gate (reddit 40/50). Strongest validation of any batch: live setup execution plus real Chromium confirmation of every affordance it depends on. All four round-trip tasks assert on `current_state` only and start from an injected multi-item baseline, so no correct end state is byte-identical to its start. Running total 180/200.
- 2026-08-18 — `shopping_admin/marketing_promotions`: 10/10 pass the gate (shopping_admin 40/50). Rename-in-place shortcuts blocked on both rule tasks (catalog 0.30, cart 0.00). `applied_at` is wall-clock, so it is asserted only as "became a non-empty stamp", which also enforces create-then-apply ordering. Running total 190/200.
- 2026-08-18 — `reddit/account_messaging`: 10/10 pass the gate. **reddit COMPLETE at 50/50.** Live setup execution plus a full headless-Chromium replay of all ten flows (each scoring REWARD: 1.0), including accepting the `window.confirm` on message delete. Traps handled: no confirm-account-deletion task (writes no state); task 005 asserts the exact email string so a blank `/account` submit does not pay; task 010 scores nothing on email because its rename save resets it to null.
- 2026-08-18 — `shopping_admin/stores_system`: 10/10 pass the gate. **shopping_admin COMPLETE at 50/50.** All 10 use pristine hub state (`initial_setup: null`, no setup file), so the inlined-JSON NameError class is structurally absent. Rejected Import Tax Rates (needs a client-side CSV attached to `#import_rates_file`, which a browser-driving agent cannot produce) plus every no-op row flagged in the prompt.

### Phase 2 complete — 200/200 bundles pass the mechanical gate

| Site | Bundles |
|---|---|
| gitlab | 50 |
| reddit | 50 |
| shopping | 50 |
| shopping_admin | 50 |

200 unique task_ids, no collisions. Difficulty 60 easy / 99 medium / 41 hard.
131 bundles inject state via `initial_setup.py`; 69 run on pristine hub state.

Replaced during generation: **0 tasks discarded**. One batch (`shopping/checkout_orders`,
10 bundles) was repaired in place by its authoring agent rather than replaced — see systemic
issue 2. Individual candidate IDEAS were rejected by authors throughout (group milestones,
`/dashboard/labels`, import/transfer project, Invite-a-group, Import Tax Rates, review
edit/delete, user flair, confirm-account-deletion, and every documented no-op row); those are
recorded per batch in `output/tasks/<site>/_batches/<topic>/GENERATION.md`.

## Phase 3 — Verification

