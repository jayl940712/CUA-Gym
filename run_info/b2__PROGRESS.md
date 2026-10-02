# WebArena task batch 2 — 200 new verified tasks

Target: 50 each for gitlab / reddit / shopping / shopping_admin, at
5 easy / 20 medium / 25 hard per site. No duplicates of
`webarena_08_18_batch_200/` (read-only snapshot of batch 1).

## Phase 1 — Preflight

Run 2026-08-19. All checks green; nothing was unfixable.

| # | Check | Result |
|---|---|---|
| 1 | Five hub ports answer | `8000 200`, `8001 200`, `8002 200`, `8003 200`, `8004 200` |
| 2 | State API round-trip on a scratch sid | `GET /go?sid=preflight-check-1` returned `initial_state` / `current_state` / `state_diff` with `state_diff == {}` |
| 3 | `python3 -c "import requests, playwright"` | ok |
| 4 | `python3 -m playwright install chromium` | ran, idempotent, no output |
| 5 | `python3 -m pytest tests/ -q` | **24 passed in 0.17s** |
| 6 | `.env` endpoints reachable | all five of `http://136.83.9.30:800X/` return 200 from this host — **no `output/endpoints.json` needed**, the batch runner uses `.env` as-is |
| 7 | Batch-1 inventories | `output/batch1_inventory/{gitlab,reddit,shopping,shopping_admin}.txt`, **50 lines each** |
| 8 | Gate scripts present | `scripts/preflight_bundles.py` (still carries `js_literal_names()`) and `scripts/detect_flaky.py` both run |

### Harness changes made in Phase 1 (deliberate, minimal, outside `./hub/`)

Batch 2 adds contract checks that batch 1 did not have. Two changes, both in
`scripts/`:

1. **`scripts/preflight_bundles.py` extended** with the batch-2 difficulty
   contract and prior-batch id reservation:
   - `difficulty` must be one of easy/medium/hard and must agree between
     `task_instruction.json` and `task.json` `metadata.difficulty`;
   - a `hard` bundle must carry `metadata.hard_criteria` with >= 2 entries drawn
     from the five criteria in TASK2.md 2c;
   - a `hard` bundle's `reward.py` must declare a module-level
     `COMPONENT_WEIGHTS` table whose numeric leaves sum to exactly 1.0
     (read out of the AST, not executed);
   - `--prior-batch <dir>` reserves every task_id under an earlier batch, so a
     batch-2 bundle that reuses a batch-1 id fails the gate;
   - `--difficulty-split E:M:H` checks the mix per root directory (`1:4:5` for a
     10-task batch, `5:20:25` for a finished site).
   The existing `js_literal_names()` AST check is untouched and still runs.
2. **`scripts/near_dup_scan.py` added** — stopworded Jaccard overlap of each new
   bundle's instruction + success_criteria against all 50 batch-1 bundles for
   the same site. It flags candidate pairs only; every flagged pair is read
   against the four TASK2.md 2b duplicate tests and adjudicated in writing
   below. Sanity-checked by scanning batch 1 against itself: 50/50 flagged.

### Note on the reference bundle

TASK2.md 2 cites `output/task_generation/gitlab-workflows/gitlab_triage_backlog_001/`
as the structural exemplar. `output/` was emptied when batch 1 was snapshotted,
so that bundle now lives at
`webarena_08_18_batch_200/task_generation/gitlab-workflows/gitlab_triage_backlog_001/`.
It is read from there as read-only reference; nothing in the snapshot is modified.

## Phase 2 — Topic split

Batch 1 took the broad single-area cuts of each mock, so batch 2's topics are
organised by the *shape* of the work rather than by which page it happens on.
Each line states why the topic is not a re-slice of a batch-1 slug.

### gitlab (batch-1 slugs spent: issue_lifecycle, merge_requests, labels_milestones, repo_project_config, people_groups)

| Slug | Shape | Why it is not a re-slice |
|---|---|---|
| `identity_prefs_tokens` | personal-settings surface | Batch 1's `people_groups` touched profile name/bio/status, follows and todos only. This topic is the `ui.*` surface batch 1 never wrote to at all: `ui.preferences`, `ui.notificationLevels`, `ui.emails`, `ui.sshKeys`, `ui.accessTokens`, `ui.feedToken`, 2FA, and `snippets` — different state keys, different handlers, zero batch-1 coverage. |
| `derived_triage_sweeps` | derived-target | The instruction names a *property*, never the entity; the agent must compute which issue/MR/project matches from a list view. Batch 1's issue/MR tasks all name their target outright (`issue "Tm Theme Editor"`, `!1178`, `!36`). |
| `audit_writeback_reports` | audit-and-writeback | Read a computed fact out of the UI and record that exact value somewhere observable (snippet body, milestone description, issue description). No batch-1 gitlab task requires reading a value back out of the UI as ground truth. |
| `cross_area_release_chains` | cross-area chain with ordering | A single flow that spans repo + milestone + label + issue + MR where a later step consumes an earlier step's result. Batch 1's chains stayed inside one area (`theme_regression_chain_009` is issues-only; `redesign_wrapup_009` is labels/milestones-only). |
| `constraint_preserving_migration` | create-then-retire + exclusion | Stand up a replacement, move dependents onto it, decommission the original, while a named neighbour must stay byte-identical and is scored. `fork_and_retire_010` retires a project but scores nothing untouched and imposes no migration of dependents. |

### reddit (spent: submissions, comments_moderation, forums, voting_subscriptions, account_messaging)

| Slug | Shape | Why it is not a re-slice |
|---|---|---|
| `derived_target_curation` | derived-target | Batch 1 has exactly three derived-target reddit tasks (`ml_lowest_scored_010`, `deeplearning_spotlight_009`, `most_discussed_recap_010`), all in one forum family and all single-mutation. This topic makes the derivation the organising principle across forums, comments, subscriptions and block lists — those three are named to the author as explicitly off-limits. |
| `crosspost_migration` | create-then-retire | Stand up a destination forum, republish content into it, retire the original submission and re-point subscriptions. Batch 1's `merge_philosophy_009` edits sidebars of two existing forums; nothing in batch 1 moves content between forums with the source retired. |
| `audit_writeback_digest` | audit-and-writeback | Compute a fact from the UI (a netScore, a count, a username) and write that exact string into a submission body, comment or biography. |
| `constraint_preserving_moderation` | exclusion constraint | Act on one comment/submission while a named sibling must remain byte-identical, and the reward scores the sibling. No batch-1 reddit reward scores an untouched neighbour. |
| `reversal_end_state` | reversal / idempotence | Do, partially undo, and land on an end state that differs from both the start and the fully-applied state. Batch 1's round-trip tasks (`flip_iss_downvote_004`, `retract_psbattle_005`) are single-surface retractions; these span votes + subscriptions + hidden forums + block list in one flow. |

### shopping (spent: cart, wishlist_compare, checkout_orders, account_addresses, reviews_contact)

| Slug | Shape | Why it is not a re-slice |
|---|---|---|
| `derived_target_shopping` | derived-target | The product/order to act on is stated as a property (cheapest line, only item under a threshold, largest historical order) and must be computed. Batch 1's two lookup tasks (`priciest_cart_line_009`, `invoice_for_biggest_pending_010`) are named to the author as off-limits. |
| `basket_migration_chains` | cross-area chain | A single flow that moves an item across compare -> wishlist -> cart -> order in a required order, where each step consumes the previous. Batch 1's cart/wishlist tasks stay within one collection or make a single hop. |
| `audit_writeback_shopping` | audit-and-writeback | Compute a value from the storefront (an order total, a line count) and write it verbatim into a review body or contact message, with the exact string as ground truth. |
| `constraint_preserving_account` | exclusion constraint | Change one address/account/newsletter field while a named neighbouring record must stay byte-identical, scored. |
| `reorder_amend_chains` | ordering-dependent chain | Reorder a historical order, then amend the resulting cart (drop a line, change a qty, add one item) to land a specific end state that is neither the original order nor a fresh cart. Batch 1's two reorder tasks reorder-then-buy without amendment scoring. |

### shopping_admin (spent: order_processing, catalog_products, customers_content, marketing_promotions, stores_system)

| Slug | Shape | Why it is not a re-slice |
|---|---|---|
| `attribute_architecture` | cross-area chain | Attribute -> attribute set -> product using that set -> category containing it, in dependency order. Batch 1's `care_instructions_attribute_and_set` creates an attribute and a set and stops there; nothing in batch 1 builds a product or category on top of one. |
| `derived_target_admin` | derived-target | The order/product/customer/review to act on is computed from a grid (largest pending order, only product under a stock threshold, the customer with no orders). Every batch-1 admin task names its target by increment id or SKU. |
| `audit_writeback_admin` | audit-and-writeback | Read a dashboard/report/grid number and record it exactly in a CMS block, CMS page or order comment. |
| `constraint_preserving_admin` | exclusion constraint | Edit one catalog/marketing/content entity while a named neighbour stays byte-identical and is scored. |
| `retire_and_migrate_admin` | create-then-retire | Stand up a replacement rule/page/group, migrate dependents onto it, retire the original, with the rubric refusing rename-in-place. Batch 1's `vip_wholesale_group_migration` and `replace_h20_cart_rule` are named to the author as off-limits, and the remaining eight must use different entity families. |

### Batch log

- 2026-08-19 — Phase 1 complete, all 8 checks green. Harness: extended
  `scripts/preflight_bundles.py` (difficulty contract, `hard_criteria`,
  `COMPONENT_WEIGHTS` sum, `--prior-batch` id reservation, `--difficulty-split`)
  and added `scripts/near_dup_scan.py`. Wrote `output/AUTHOR_BRIEF.md` (binding
  brief pasted-by-reference into every author prompt) and the four
  `output/batch1_inventory/<site>.txt` files (50 lines each). Launched Phase 2
  wave 1 (4 concurrent authors): `gitlab/identity_prefs_tokens`,
  `reddit/derived_target_curation`, `shopping/derived_target_shopping`,
  `shopping_admin/attribute_architecture`. Running total 0/200.
- 2026-08-19 — Concurrency policy updated in TASK2.md at the user's direction:
  **Phase 2 authoring stays at 4** concurrent `task-author` agents (so a lesson
  from one batch can reach later prompts), **Phase 3 verification runs at 12**
  (`--concurrency 12`). Wave 1 relaunched with the same four topics, now also
  pointing authors at the schema-v2 reference bundle at
  `webarena_08_18_batch_200/task_generation/gitlab-workflows/gitlab_triage_backlog_001/`.
  Running total 0/200.
- 2026-08-19 — `gitlab/identity_prefs_tokens`: **10/10 pass the gate**
  (re-run independently, not taken from the agent's self-report), split asserted
  at `--difficulty-split 1:4:5`. Near-dup scan vs batch-1 gitlab: **0/10 flagged**
  at threshold 0.45 — nothing to adjudicate. Author went beyond the brief and
  drove a real chromium replay of all ten flows twice (10/10 at 1.0, identical
  both runs), which caught one wrong-iid replay bug the offline oracle could not
  see. Measured shortcut scores: 006 rename-primary-email 0.000, 008
  drop-global-level 0.000.
  Three findings to inherit:
  * `ui.dismissedAlerts` is seeded (`src/utils/initialState.js:92`) but **never
    written** — no `setUi` writer exists anywhere in `src/`, no banner in this
    mock is dismissible. Do not build on it.
  * `ProfileKeys.addKey()` allocates `id = list.length + 1`, which collides once
    two or more SSH keys exist, and `removeKey` filters by id — so a collision
    deletes two rows. Seed exactly one key if a task touches SSH keys.
  * `resetFeedToken()` uses the mock's native `window.confirm` — replay drivers
    must accept the dialog (third confirm site found so far, after the admin
    category tree and reddit message delete).
  Author correctly refused to write an "ordered walk across three profile pages"
  requirement: the mock persists no ordering signal, so it is unscorable. It got
  the ordering property honestly instead, as a value dependency.
  Launched `gitlab/derived_triage_sweeps`. Running total 10/200.
- 2026-08-19 — `shopping/derived_target_shopping` and `reddit/derived_target_curation`
  both returned: **10/10 each pass the gate** (re-run independently), near-dup scan
  vs their batch-1 site inventories **0/10 flagged** for both. Running total 30/200.

### SYSTEMIC ISSUE 1 (batch 2) — a derived-target topic has no legitimate easy slot

Two authors, independently and without contact, wrote an "easy" task that was
really a medium, and both flagged it honestly rather than hiding it. They are
right, and the fault is in my topic assignment, not in their tasks.

TASK2.md 2c defines **easy** as "one navigation plus one mutation on an entity
named outright in the instruction... No lookup", and defines **medium** as "one
mutation gated on a lookup the agent must perform". A topic whose entire
organising principle is "the instruction states a property, never the entity"
therefore cannot produce an easy task. Both candidates had 3 success criteria —
medium by the letter of the definition.

**Resolution.** Both bundles relabelled **upward**, easy -> medium, in
`task_instruction.json` and `task.json` (with `difficulty_relabelled_from` and a
recorded reason). Relabelling *downward* to fill a slot is forbidden and was not
done; relabelling upward when the work exceeds the label is honest.

- `shopping_derived_target_shopping_compare_cheapest_cart_line_001` easy -> medium
- `reddit_derived_target_curation_bridgeport_top_post_001` easy -> medium

The three derived-target batches now ship **0 easy / 5 medium / 5 hard**, and the
easy quota moves to the other batches so each site still lands at exactly
5 easy / 20 medium / 25 hard. Per-site quota ledger:

| Site | derived batch | remaining 4 batches must supply |
|---|---|---|
| gitlab | `derived_triage_sweeps` 0:5:5 | 5 easy / 15 medium / 20 hard |
| reddit | `derived_target_curation` 0:5:5 | 5 easy / 15 medium / 20 hard |
| shopping | `derived_target_shopping` 0:5:5 | 5 easy / 15 medium / 20 hard |
| shopping_admin | (no derived batch in wave 1) | on the standard 1:4:5 per batch |

`output/AUTHOR_BRIEF.md` updated with the rule so no further author rediscovers
it. The in-flight `gitlab/derived_triage_sweeps` author was messaged mid-run and
switched to 0:5:5 before finalising.

### New mock findings from batch-2 authors (folded into AUTHOR_BRIEF.md)

- **shopping `publishInitialState()` is dead code** — exported at
  `src/utils/dataManager.js:210`, called from nowhere in `src/` (verified
  independently by grep). SCHEMA.md 2.3's claim that the app republishes a
  corrected `/go` baseline after a partial inject does **not** hold in the
  shipped tree, so after the first browser mutation `state_diff` reports
  defaulted keys as phantom changes. Inert for these 10 rewards because they all
  read `current_state` only — but a reward that diffed against `initial_state`
  would be silently wrong. Now a standing rule in the brief for every site.
- shopping order-view line items are `<strong>`, not links (`OrderViewPage.jsx`).
- reddit forum sidebars expose only `subscriberCount`, which is 0 everywhere in
  the seed; busiest/quietest derivations must route through `/forums`.
- reddit submission `url` is never rendered as text, only as the title href plus
  a domain chip.
- Third native `window.confirm` site found: gitlab `resetFeedToken()`.

Launched `reddit/crosspost_migration` and `shopping/basket_migration_chains`,
each carrying 2 easy to start repaying the quota.
- 2026-08-19 — `shopping_admin/attribute_architecture`: **10/10 pass the gate**
  (re-run independently), split 1:4:5 asserted, near-dup **0/10 flagged**.
  **Wave 1 complete: 40/200**, all four sites at 10 bundles each.
  Author drove all ten flows end to end in chromium (untouched 0.0, replay 1.0)
  plus 38 adversarial lanes scored by both `reward.py` and `nemo_reward.py`, which
  agree on every lane. Three findings folded into the brief:
  * `/admin/catalog/product/new/set/<id>/type/simple/` **does** create a product on
    a session-created attribute set (`attribute_set_id: 16` landed in `newProducts`),
    even though the form's Attribute Set select is built from the static map and
    never lists it. Default-set shortcut scores 0.75.
  * An attribute **cannot** be attached to an attribute set — set Save writes only
    the name — and there is **no attribute-set delete at all**. attribute->set->product
    chains can therefore only be by reference (name/code).
  * The category page's embedded "Products Not in Category" grid loses its keyword
    search on submit (it navigates the category route and unmounts the grid), so it
    is unusable for search across 2040 rows.
  Two honest gaps in its self-report, both acceptable and neither blocking:
  `cuagym.schemas` pydantic validation is unimportable in this repo (`resources_servers`
  is a NeMo-Gym package not vendored here) — the gate validates `WebTaskManifest`
  and the `cuagym` block directly instead; and it did not re-run each replay from a
  second fresh sid, which is exactly what Phase 3's agreement conditions enforce.
  Launched `shopping_admin/derived_target_admin` (0:5:5 per the derived-target rule).

### Per-site easy-quota ledger after wave 1

Each site must still land at 5 easy / 20 medium / 25 hard. Remaining batches:

| Site | banked (e/m/h) | remaining batches and their assigned splits |
|---|---|---|
| gitlab | 1/4/5 | derived_triage_sweeps 0:5:5, then audit_writeback 2:3:5, cross_area_release_chains 1:4:5, constraint_preserving_migration 1:4:5 |
| reddit | 0/5/5 | crosspost_migration 2:3:5 (running), audit_writeback_digest 1:4:5, constraint_preserving_moderation 1:4:5, reversal_end_state 1:4:5 |
| shopping | 0/5/5 | basket_migration_chains 2:3:5 (running), audit_writeback_shopping 1:4:5, constraint_preserving_account 1:4:5, reorder_amend_chains 1:4:5 |
| shopping_admin | 1/4/5 | derived_target_admin 0:5:5, audit_writeback_admin 2:3:5, constraint_preserving_admin 1:4:5, retire_and_migrate_admin 1:4:5 |
- 2026-08-19 — `shopping/basket_migration_chains`: **10/10 pass the gate**
  (shopping now 20/20 collectively, split verified 2 easy / 8 medium / 10 hard),
  near-dup **0/20 flagged**. Strongest flakiness evidence so far: real chromium
  replays of all ten flows run **twice from fresh sids, 20/20 runs at exactly
  1.0**. Measured shortcut scores 0.60-0.70 on the five hard tasks.
  Adjudication of the two easy tasks (I read both rather than trusting the
  label): both name the product outright, are one navigation plus one mutation,
  and carry no lookup. Each lists 3 success criteria, but criteria 2 and 3 are
  *untouched-neighbour guards*, not additional work — the work itself is a single
  mutation, so `easy` is the honest label. Both use controls batch 1 never
  touched: the Compare Products page's per-column Add to Cart
  (`ComparePage.jsx` -> `ProductGrid.AddToCartButton`) and the "Recently Ordered"
  sidebar block (`SidebarBlocks.ReorderBlock`, a different handler from the
  order-grid Reorder batch 1 uses). No invented easy was needed.
  Load-bearing finding: **a wish-list hop is invisible unless it is an endpoint.**
  `wishlist.items` carries no history, so compare -> wishlist -> cart ends
  byte-identical to "clear compare, add from the PDP" — unscorable. Every hop in
  this batch is proved by one of four devices instead: a seeded origin whose
  absence is scored, a placed order (an item's absence from the order proves it
  left the cart *before* checkout), a rebuilt record (`itemId >= 557` /
  `wishlistItemId >= 3`, unreachable by an in-place edit and visible in the cart
  row's Edit href), or carried quantity. Chains ending in an order cannot also use
  the rebuilt-record proof, since `placeOrder` empties the cart.
  Also recorded: the compare page has no Add-to-Wish-List control (that hop must
  route via the PDP); `WishlistPage.addRowToCart` silently bounces to the PDP for
  products with a required option; `moveToWishlist` drops the line's chosen
  options and no-ops when the product is already listed.
  Launched `shopping/audit_writeback_shopping` (1:4:5). Running total 50/200.
- 2026-08-19 — `gitlab/derived_triage_sweeps`: **10/10 pass the gate** (gitlab now
  20/20, split verified 1 easy / 9 medium / 10 hard), near-dup **0/20 flagged**.
  Scope correction landed: shipped 0:5:5 with no token easy task; every one of the
  ten instructions states a property and never names its target. Replays driven in
  chromium **twice from fresh sids with identical results**; shortcut probes on 009
  measured replace-instead-of-add 0.850, spray-the-runner-up 0.900, wrong entity 0.000.
  Three findings folded into the brief — all three kill derivations my own topic
  prompt had suggested, which is worth noting as a lesson about my prompts:
  * **`upvotes` is 0 on all 19,705 issues** and **`draft` is false on all 23,236
    merge requests**, so `?sort=popularity` is inert and "the only draft MR" does
    not exist.
  * **No project has `archived: true`**, and milestone due dates are near-degenerate
    (four of a11yproject's six share `2019-12-31`).
  * The MR detail page has **no to-do control** (`IssueDetail.jsx` has
    `[data-testid="sidebar-todo"]`, `MergeRequestDetail.jsx` does not).
  Rejected honestly rather than forced: "label applied to the most issues" (the
  labels page shows no counts, so it is error-prone to derive and therefore a bad
  task), "member with lowest access level" (batch-1 territory), a second
  primer/design MR-edit task (would be `gate_color_chore_010` with a lookup bolted
  on), and a snippet writeback (already used three times).
  Launched `gitlab/audit_writeback_reports` (2:3:5). Running total 60/200.
- 2026-08-19 — `reddit/crosspost_migration`: **10/10 pass the gate** (reddit now
  20/20, split verified 2 easy / 8 medium / 10 hard), near-dup **0/20 flagged**.
  Replays driven in chromium **3 independent runs, 10/10 at exactly 1.0 every
  time**. Rename-in-place measured on every hard task and refused everywhere:
  006 0.25, 007 0.20, 008 0.20, 009 0.20, 010 0.20 — with the rename given every
  advantage (title, description, sidebar and tags all set). Two of its ten need no
  injection, so their NeMo `initial_setup` is `null` and the file is correctly absent.
  Two findings folded into the brief:
  * **`forumRenames` is applied only at materialization** — a rename does *not*
    rewrite `newSubmissions[].forum`. That asymmetry is precisely what lets the
    rubric distinguish a real republication from a rename, and it will bite any
    future reward keyed off `submission.forum`.
  * **`createForum` writes tags in a second `editForum` pass**, a forum created with
    an empty Tags box has **no `tags` key at all** (not `[]`), and creation
    auto-subscribes and auto-mods the creator — so exact-set assertions on
    `subscriptions`/`moderatorOf` after a creation step must include the new forum.
  Adjudication of its one deviation, which I agree with: the second easy slot is a
  moderator stand-down rather than the "hide a retired forum" my prompt suggested,
  because a bare hide is the same primary mutation on the same entity type as
  batch-1 `reddit_voting_subscriptions_hide_jokes_003` with only the instance
  changed — i.e. a duplicate under test 2. Self-unmod is a migration primitive
  batch 1 never uses alone, so it carries the slot honestly. The author caught this
  itself rather than following my prompt into a duplicate.
  Launched `reddit/audit_writeback_digest` (1:4:5). Running total 70/200.
- 2026-08-19 — `shopping_admin/derived_target_admin`: **10/10 pass the gate**
  (shopping_admin now 20/20, split verified 1 easy / 9 medium / 10 hard), near-dup
  **0/20 flagged**. All ten driven end to end in chromium twice from fresh sids
  (0.0 untouched, 1.0 replay), 9 setups executed live, 44 adversarial lanes with
  `reward.py` and `nemo_reward.py` agreeing on every one. Two replay bugs surfaced
  only in the browser (the order view's Submit Comment has no `#submit_comment_button`;
  the document grids link **View**, not the increment id). The author tightened its
  own task 10 after finding that reordering the runner-up still collected 0.65.
  Recorded: SCHEMA.md **overstates the Tax Rule form** — it claims Save Rule writes
  `taxConfig.calculations`, but the form has only Name / Priority / Calculate Off
  Subtotal Only / Sort Order (`SystemForms.jsx:244-345`) and never links a rate.
  Running total 80/200. Launched `shopping_admin/audit_writeback_admin` (2:3:5).

### SYSTEMIC ISSUE 3 — inline JSON escapes eaten by a non-raw string literal (found, gated)

The sibling of batch 1's systemic issue 2. A fixture inlined as
`json.loads("""...""")` has its backslash escapes rewritten **by the Python parser**
before `json.loads` ever sees them. A cart-rule fixture's `conditions_serialized`
broke `json.loads` at episode time; `compile()` passed, and only executing the setup
caught it. The silent variant is worse: a fixture's `\\b` collapses to `\b`, which
JSON reads as a **backspace**, so the program compiles, the JSON still parses, and
the value is quietly wrong.

Fix (harness change, deliberate and minimal, in `scripts/preflight_bundles.py`):
added `broken_inline_json()`, which AST-walks both episode programs for
`json.loads()` calls on a string literal and

1. reports any literal that does not parse as JSON, and
2. reports any **non-raw** literal containing a backslash — read off the source
   segment, since `ast.Constant` does not record the `r` prefix.

Rather than pattern-matching the quoting, it evaluates the literal the parser
actually produced, so it catches the defect whatever caused it. Self-tested against
four cases (silent corruption, correct raw literal, no backslashes, hard parse
error) — all four behave correctly. **All 100 bundles then on disk were re-gated
under the extended check: 100/100, no regressions.** The rule and the `r"""..."""`
requirement are now in `AUTHOR_BRIEF.md` as systemic issue 3.
- 2026-08-19 — `reddit/audit_writeback_digest`: **10/10 pass the gate** (reddit now
  30/30, split verified 3 easy / 12 medium / 15 hard), near-dup **0/30 flagged**.
  3 independent chromium replay runs, 10/10 at exactly 1.0 each time. 4 of its 10
  need no injection (`initial_setup: null`, file absent). 19 adversarial attempts
  all strictly < 1.0 (009 "record 108 instead of 109" = 0.30, 008 "record 4" = 0.60).
  Four findings folded into the brief, the first of which is the real lesson of this
  topic — **an audited number only has one defensible rendering if the UI renders it
  one way**:
  * `formatScore` is ungrouped but `submissionCountLabel` groups, so a four-digit
    *forum count* has two defensible renderings while a four-digit *score* has one.
  * negative scores render with **U+2212 MINUS**, not a hyphen, so any negative
    extreme is inherently ambiguous; the author picked a thread whose minimum is
    positive rather than write an ambiguous task.
  * `ForumEditPage` unconditionally writes `tags: []` on save — note the contrast
    with `createForum`, which omits the key entirely when Tags is empty.
  * `addComment` **auto-upvotes the agent's own comment**, so "no votes cast"
    assertions must whitelist it.
  Same honest caveat as the admin batch: `WebArenaTaskRow`/`CuaGymTaskInfo` cannot be
  imported in this repo, so row validity rests on the gate plus a field-by-field
  comparison of `nemo_task.json` against the on-disk programs. Accepted.
  Launched `reddit/constraint_preserving_moderation` (1:4:5). Running total 90/200.
- 2026-08-19 — `shopping/audit_writeback_shopping`: **10/10 pass the gate**
  (shopping now 30/30, split verified 3 easy / 12 medium / 15 hard), near-dup
  **0/30 flagged**. Chromium replays twice from fresh sids, **20/20 at exactly 1.0**.
  19 hand-built wrong attempts all strictly below 1.0, and every wrong *string*
  scores 0 on its fact component (`68.50` without the dollar sign 0.0, `$122` for
  `$122.00` 0.65, a note on the runner-up row 0.0, line count instead of unit count
  0.75) — which is the property that makes an audit task worth anything.
  Two load-bearing findings folded into the brief:
  * the review form's star radios are **unclickable directly** — `Rating_5`'s Luma
    sprite label intercepts pointer events for every lower star, so a driver must
    click `label.rating-N` or use `check(..., force=True)`. This cost a real replay
    failure before it was diagnosed, and it will bite any future review task.
  * `AddressEditPage` stores an empty Company as `null`, not `""`
    (`company: form.company.trim() || null`), so a Company reward must compare
    trimmed text and must not treat `null` as an empty-string match.
  Also recorded: `ComparePage` prices resolve from the catalog at render time rather
  than from the stored compare record, and `reorder` re-prices from
  `finalPrice(product)` rather than the historical order line — so arithmetic over a
  reorder is only safe once the products are confirmed to carry no `specialPrice`,
  which the author checked before relying on it.
  Launched `shopping/constraint_preserving_account` (1:4:5). Running total 100/200 —
  halfway.
- 2026-08-19 — `gitlab/audit_writeback_reports`: **10/10 pass the gate** (gitlab now
  30/30, split verified 3 easy / 12 medium / 15 hard), near-dup **0/30 flagged**.
  Every audited number was re-read from a live chromium session and confirmed
  against the frozen-corpus derivation; replays run twice from fresh sids, 1.0 both
  times, 0 page errors. Browser-driven adversarial probes all strictly < 1.0
  (open-a-form-and-Save 0.000, `6 stars` instead of `6` 0.000, note on the quieter
  project 0.000, correct note but rewrites the neighbour 0.800, census without the
  prerequisite tag/branch 0.300).

### SYSTEMIC ISSUE 4 — a no-op save is a real state mutation (found, brief updated)

The most dangerous *reward* bug found in batch 2, and it is not site-specific.
Several save handlers write unconditionally: gitlab `ProjectSettingsGeneral.saveNaming`
always writes `topics: []` (no seeded project carries `topics`), gitlab `NewLabel`'s
edit branch always rewrites `updated_at`, and reddit `ForumEditPage` unconditionally
writes `tags: []`. So `projectEdits.<id>` / `labelEdits.<id>` / the forum record show
up in the diff **even when the agent changed nothing**.

A rubric that asks "was this record edited?" therefore pays an agent that merely
opened a form and pressed Save. This author's first cut leaked 0.2-0.4 exactly that
way and caught it only by driving the probe in a real browser — no offline oracle
would have seen it. Every single-value task in the batch now gates its preservation
components on **the recorded value itself**, which is what produces the 0.000 rows
above.

Rule added to `AUTHOR_BRIEF.md`: **never gate a component on "the record was
touched"; always gate on the value being exactly right** — and for an exclusion
constraint, on the neighbour's *values* still being exactly what they were. This is
not gateable statically (it is a semantic property of each rubric), so it is enforced
through the brief and through Phase 3's initial-lane-must-score-0.0 condition.

### Correction to my own brief

The brief previously told authors that per-label issue counts are unobtainable and
therefore a bad basis for a task. **That was wrong and is retracted.** The labels
*page* shows no counts, but `IssuesList`/`MergeRequestsList` pass
`hooks.js issuableStateCounts(rows, q, indexes)`, which re-filters with `state`
forced to `all` — so the tab badges ARE filter-aware and "how many issues carry
label L" is a readable badge. (`IssuableListBody`'s own local `counts` object is
pre-filter, which is what makes the code read the other way at first glance.) The
author checked the claim in the source instead of taking my prompt at face value.
Also new: the Branches and Tags pages carry no counts — the overview `.project-stats`
row is the only place they render; the new-issue label multi-select keeps its menu
open by design and overlays the Create issue button; the MR title is only reachable
via `[data-qa-selector="title_content"]`.

  Launched `gitlab/cross_area_release_chains` (1:4:5). Running total 110/200.
- 2026-08-19 — `shopping/constraint_preserving_account`: **10/10 pass the gate**
  (shopping now 40/40, split verified 4 easy / 16 medium / 20 hard), near-dup
  **0/40 flagged**. Chromium replays twice from fresh sids, 20/20 at exactly 1.0.
  This is the batch whose whole point is the neighbour, and it measured that
  directly: **damaged-neighbour lanes driven through the browser** score 0.55-0.85
  across all ten, every one strictly below 1.0. Shortcut lanes: repairing the wrong
  card 0.30, rewriting Trenton in place instead of creating a new record **0.00**,
  "fixing" the decoy 4-digit zip 0.25.
  Load-bearing finding behind the batch: **`saveAddress` is asymmetric** — ticking a
  default box writes `customer.default*` *and* clears that flag on every other
  record, while leaving it unticked writes `false` onto the saved record only and
  leaves the pointer alone. That is exactly what makes "the other default must not
  move" checkable. It also killed a candidate the author was honest about:
  *unticking* a default leaves `isDefaultShipping: false` on a record that
  `customer.defaultShipping` still points at, and the Address Book still renders it
  as the default — a self-contradictory end state, so no task demotes a default.
  Generation trap now in the brief: a setup docstring must not quote
  `json.loads(r"""..."""` verbatim — the inner triple quote closes the module
  docstring, and the author's first pass failed the gate with `initial_setup does
  not compile` on all ten bundles. It is a natural sentence to write while following
  systemic issue 3, so it is worth inheriting.
  Launched `shopping/reorder_amend_chains` (1:4:5, the last shopping batch).
  Running total 120/200.
- 2026-08-19 — `shopping_admin/audit_writeback_admin`: **10/10 pass the gate**
  (shopping_admin now 30/30, split verified 3 easy / 12 medium / 15 hard).
  Chromium replay of all ten, **three full runs from fresh sids**, 0.0 -> 1.0 every
  time. **50 adversarial lanes**, each scored by both `nemo_reward.py` (live `/go`)
  and `reward.py` (frozen evidence), agreeing on all 50: `191.5` for `191.50` 0.0,
  `38` for `38.00` 0.0, `$15,475.46` for `15475.46` 0.6, the *pre*-cancellation
  count 0.75, annotating the runner-up product 0.4, clearing the review queue by
  deleting instead of approving 0.2.
  Findings: `/admin/marketing/search_term/` **404s** — the grid is
  `/admin/search/term/` (caught by opening every `start_path` in a browser, and it
  was this author's original task-8 start path); the order view's **Cancel goes
  through an in-page confirm modal** (`button.action-accept`), not a native dialog,
  so a replay that clicks Cancel and moves on silently does nothing; the CMS-page and
  category forms render collapsible headers as `<div class="admin__collapsible-title">`
  (the product form uses a `<button>`) and `#page_identifier` / `#category-description`
  are not in the DOM until the section is opened; review-grid mass selection has no
  visible row checkboxes (`#reviewGrid_massaction-mass-select` -> `selectAll`).
  Rejected as unscorable, correctly: any writeback into a *customer record* derived
  from the Order Count / Order Total reports, because two seeded accounts are both
  named "Jane Smith" (entities 10 and 15) and those reports render names only; also
  "product with the most reviews" (8-way tie), Dashboard Lifetime Sales (hardcoded
  `$0.00`), and Reports > Reviews > By Customers (its Customer column is only
  populated because `hit.customer_name = c.name` falls back to the review nickname —
  `customers.json` has no `name` key).

### Near-duplicate adjudications (shopping_admin, flagged below the 0.45 gate)

The 0.45 scan reports 0/30. Dropping the threshold to 0.22 surfaces three pairs;
all three were read against the four TASK2.md 2b tests and **accepted**:

1. `attribute_architecture_fit_profile_attribute_taxonomy` vs batch-1
   `catalog_products_care_instructions_attribute_and_set` (0.26). Both create a
   product attribute, so test 2 is the live question. Batch 1 goes attribute ->
   attribute *set* and stops (`newAttributeSets`); batch 2 goes attribute ->
   *category* tagged with it (`newCategories` / `categoryOverrides`). Different
   second entity, different handler, and neither task's criteria are a subset of
   the other's. **Not a duplicate.**
2. `attribute_architecture_format_attribute_replacement` vs the same batch-1 task
   (0.28). Batch 1 creates an attribute from scratch; batch 2 *replaces* an
   existing one, which requires reading the incumbent's option values first and
   reproducing them — a create-then-retire shape batch 1 never performs.
   **Not a duplicate.**
3. `audit_writeback_admin_url_rewrite_census_search_term` vs batch-1
   `marketing_promotions_search_terms_cleanup` (0.23). The closest call of the
   three: both end in a created search term. But batch 1 dictates every field
   value, so its work is data entry; batch 2's Results value is *computed* from a
   different grid (the URL Rewrites record count) and the reward scores that
   derived number, which is precisely the audit-writeback shape. Under test 2 the
   primary work differs, not just the field value. **Not a duplicate**, and noted
   here as the pair I would re-examine first if a reviewer disagreed.

- 2026-08-19 — `reddit/constraint_preserving_moderation`: **10/10 pass the gate**
  (reddit now 40/40, split verified 4 easy / 16 medium / 20 hard), near-dup
  **0/40 flagged**. Every neighbour component is AND-gated on a primary mutation,
  so the untouched initial state still scores exactly 0.0 while the neighbour stays
  load-bearing — measured across 14 adversarial UI runs: unblock-all 0.5, +upvote
  the twin 0.65, +save the co-moderated forum 0.75, delete both copies 0.3, act on
  the wrong copy 0.0, clear-all-votes 0.35, Clear-all notifications 0.85.
  Reported honestly rather than buried: an earlier replay run scored 9/10 because
  the driver's `form button[type='submit']` selector hit the layout's own form
  instead of the comment-edit Save button — a **driver defect, not a task or reward
  defect**; fixed, then three clean runs (b, c, d) each 10/10 at exactly 1.0.
  Two findings folded into the brief, both of which turn a mock quirk into an exact
  test:
  * the forum settings and appearance forms unconditionally write `tags` /
    `backgroundImageMode` / `suggestedTheme`, **none of which exists on any seeded
    forum** — so the *absence* of those keys is an exact "this form was never saved"
    detector. This is the constructive flip side of systemic issue 4.
  * `vote()` is the only writer that can create a `submissionEdits`/`commentEdits`
    entry on an otherwise-untouched record, making "no overlay entry" an exact
    untouched test for vote tasks.
  Launched `shopping_admin/constraint_preserving_admin` (1:4:5) and
  `reddit/reversal_end_state` (1:4:5, the last reddit batch). Running total 140/200.
- 2026-08-19 — `gitlab/cross_area_release_chains`: **10/10 pass the gate** (gitlab
  now 40/40, split verified 4 easy / 16 medium / 20 hard), near-dup **0/40 flagged**
  (the author also ran its own scan at the tighter 0.35 and got 0/40). Ten different
  projects, none used twice. Chromium replay of all ten run **three times end to end
  from fresh sids**, 1.000 every time, 0 page errors.
  Every chain's later step consumes an earlier step's *value*, so the ordering is
  scorable rather than decorative — the fileOverlay key embeds the branch, the MR
  carries the allocated `milestone_id`, the branch name embeds the new issue's iid,
  the fork's `project_id` scopes the label. Measured shortcuts: notes committed to
  `master` instead of the new branch 0.300, `RELEASE.md` committed straight to
  `main` 0.700, reusing the seeded `bug` label instead of creating one 0.600, label
  and issue filed in the upstream project instead of the fork 0.300.
  **Direct confirmation that the systemic-issue-4 fix works.** The author ran a
  probe of the correct flow **plus a no-op Save on a neighbouring label**:
  `NewLabel`'s edit branch does write `labelEdits.1817` on a no-change save, and the
  rubric still paid **1.000**, because the exclusion component is gated on the
  label's title/colour/description rather than on "was it edited". That is the rule
  from systemic issue 4 verified in a browser rather than assumed.
  Two findings folded into the brief:
  * `NewFile`'s "Start a new merge request" checkbox is **inert** — `FileEditor`
    passes `startMr` but `NewFile.commit()` never uses it, so no MR is created.
  * a tag records `{name, sha, date, message}` with **no ref**, and a freshly cut
    branch shares its parent's head sha, so "the tag was cut from the new branch" is
    genuinely unobservable. The author declined to score it and scored the tag's
    name and message instead, carrying the dependency in the message — the right
    call, and reported rather than quietly asserted.
  Launched `gitlab/constraint_preserving_migration` (1:4:5, the last gitlab batch).
  Running total 150/200.
- 2026-08-19 — `shopping/reorder_amend_chains`: **10/10 pass the gate**.
  **shopping COMPLETE at 50/50**, `--difficulty-split 5:20:25` passes.
  Chromium replays twice from fresh sids, 20/20 at exactly 1.0. Near-dup 0/50 at
  0.45; notably, at the tighter 0.25 threshold **not one bundle of this batch is
  flagged**, despite it operating under the tightest non-duplication constraint in
  the project (batch 1 ships four reorder tasks and two batch-2 siblings also use
  reorder).
  **The honest part, which I am accepting as reported rather than glossing:** the
  build-by-hand shortcut is only distinguishable on **2 of the 10** tasks. The one
  trace the mock leaves is the cart `itemId` (visible in each row's Edit link), and
  `placeOrder` destroys it, so it can only be used on tasks that end in the cart.
  Tasks 007 and 010 use it and declare `shortcut_defeating` — a hand-built basket
  measures 0.80 in both. The other eight are composition tasks, declared as such in
  `GENERATION.md`, and a rollout that reaches the right composition by hand scores
  1.0 there. That is acceptable: `shortcut_defeating` is one of five hard-criteria
  and no task needs it, the end state is still deterministic with exact ground
  truth, and each of those eight satisfies >=2 other criteria. It does mean eight
  tasks are weaker than the topic name suggests, which is why it is recorded here.
  Two stronger traces were considered and rejected with reasons: a discontinued
  product (no seeded order line misses the catalog) and a catalog/order name
  mismatch (`reorder` copies `name`/`sku` from the historical line, `addToCart` from
  the catalog — but no seeded order has such a mismatch). Both would have required
  fabricating an injected order.
  Mock finding: contrary to what `productOptions.json` alone suggests, **historical
  order lines carry their chosen options and `reorder` rebuilds them**, so a
  reordered option-bearing line arrives fully configured. A historical option value
  that no longer exists in the catalog stores with `optionTypeId: null`.

### Near-duplicate adjudications (shopping)

0/50 flagged at the 0.45 gate. Lowering to 0.25 surfaces nine pairs; all were read
against the four TASK2.md 2b tests and accepted. The two worth recording:

1. `constraint_preserving_account_retire_and_recreate_trenton_008` vs batch-1
   `account_addresses_relocate_nashville_009` (**0.40 — the closest pair in the
   entire 200**). Both add an address and delete another, so test 2 is squarely in
   play. They diverge on what is *scored*: batch 1 ticks both default boxes on the
   new record, deletes San Mateo, and additionally renames the account; batch 2
   leaves both boxes unticked, deletes Trenton, and its rubric scores San Mateo
   staying **byte-identical** and both default pointers **not moving** — plus an
   explicit refusal of rewrite-in-place (measured 0.00). Neither task's criteria are
   a subset of the other's, and a scored exclusion constraint is exactly what 2b
   lists as legitimising a re-touched entity type. **Not a duplicate** — but it is
   the single pair I would replace first if a stricter standard is wanted, and it is
   named here so that choice stays available.
2. `derived_target_shopping_reorder_biggest_then_split_006` vs batch-1
   `cart_reorder_wishlist_qty_010` (0.26). Batch 1 names order 000000165; batch 2
   states a property and the agent must compute which order is largest, then act on
   the lines the reorder produced. The derivation is the shape difference, and the
   reward scores the near-miss order as untouched. **Not a duplicate.**

  Launched `shopping_admin/retire_and_migrate_admin` (1:4:5, the last admin batch).
  Running total 160/200.
- 2026-08-19 — `reddit/reversal_end_state`: **10/10 pass the gate**; reddit reaches
  50/50 and `--difficulty-split 5:20:25` passes. Two independent full chromium runs
  from fresh sids at 10/10 exactly 1.0. Untouched baseline 0.0 on all ten;
  "applied everything, undid nothing" scores 0.2-0.75 and "undid everything" scores
  0.0-0.5 — so the required third state is genuinely discriminated from both
  endpoints, which is the whole point batch 1's pure do-then-undo tasks could not
  achieve.
  Where the mock leaves a residue that survives an undo, the rubric uses it, making
  the reversal itself provable rather than only its net effect: `submissionEdits[id]`
  survives a vote retraction with the score restored; `nextCommentId` /
  `nextSubmissionId` are bumped per creation and never decremented by delete;
  `userRenames` is append-only, so a rename round trip leaves a two-entry ledger.
  Four tasks are non-shortcuttable on that basis; the other six score the stated end
  ledger exactly, and the author says plainly which is which.
  Reported as it happened rather than smoothed over: an earlier replay run was 8/10,
  both failures being **replay-driver selector defects** (`<strong>`-nested link text
  on the hidden-forums table; the biography textarea id is `user_biography_biography`),
  not task or reward defects — fixed, re-verified individually, then two clean runs.
  New findings: own-comment delete fires a native `window.confirm` (`Comment.jsx:197`),
  a fourth confirm site the brief did not list for reddit.

### Near-duplicate adjudications (reddit) — one REJECTED and sent back

0/50 flagged at the 0.45 gate. At 0.28, four pairs surface. Three are clear passes.
The fourth I am **rejecting**, against my own gate's verdict:

**REJECTED: `reddit_derived_target_curation_notification_low_score_005`** vs batch-1
`reddit_account_messaging_notification_triage_008` (0.35).

- batch 1: three notifications, exactly one is for a comment by Cactuszach — clear
  only that one with its own Clear button, do not use Clear all, leave the others.
- batch 2: four notifications, exactly one comment scores lowest — clear only that
  one with its own Clear button, do not use Clear all, leave the others, and
  downvote that comment.

Read strictly, it survives the four tests: the selection mechanism changes from a
displayed attribute to a computed extremum, and the added vote criterion means its
success criteria are not a subset of batch 1's. But the primary mutation, the
entity, the "use its own Clear button, not Clear all" constraint and the shape of
the criteria list all coincide, and the increment over batch 1 is one extra click.
That is very close to 2b's "extending a batch-1 flow with one extra trivial step
does not make it new". Similarity is triage, not verdict — and my judgement here is
that this one is a re-slice.

Action: task deleted and a replacement commissioned from a fresh author, keeping the
derivation but moving to an entity and mutation batch 1 never pairs. reddit drops to
49/50 until the replacement lands and is gated. **Replacements so far: 1.**

The three accepted reddit pairs:
1. `constraint_preserving_moderation_three_forum_config_008` vs batch-1
   `forums_appearance_monitor_log_004` (0.35). Both touch forum settings/appearance
   forms. Batch 1 changes two settings on **one** forum; batch 2 makes four writes
   across **two** forums and scores a **third** co-moderated forum staying
   byte-identical, including the absence of `tags`/`backgroundImageMode`/`suggestedTheme`.
   The scored neighbour is the shape difference. **Not a duplicate.**
2. `derived_target_curation_hidden_forum_revival_004` (0.30) — batch 1's
   `unhide_nosleep_008` unhides a named forum; batch 2 derives which hidden forum is
   busiest via `/forums` and then also subscribes. Derivation plus a second surface.
   **Not a duplicate.**
3. `audit_writeback_digest_worcester_bylines_004` (0.29) — the overlap is topical
   (forum names), not structural; batch 1 has no post-count writeback. **Not a
   duplicate.**
- 2026-08-19 — `shopping_admin/constraint_preserving_admin`: **10/10 pass the gate**
  (shopping_admin now 40/40, split verified 4 easy / 16 medium / 20 hard), near-dup
  **0/40 flagged** at 0.45. All ten driven in chromium **twice from fresh sids**
  (0.0 / 1.0 both times); 37 adversarial lanes built by mutating each task's *real
  browser* end state, with `reward.py` and `nemo_reward.py` agreeing on every lane.
  Damaged-neighbour runs measure 0.6-0.8, always strictly below 1.0, while pristine
  stays exactly 0.0 because every neighbour component is AND-gated on primary
  progress. Its strongest task uses the **two Jane Smith accounts** so that the
  near-miss *is* the protected neighbour (wrong twin = 0.0); rename-in-place on the
  supersede task = **0.0**, delete-instead-of-retire = 0.6.

### CORRECTION — a batch-2 finding I propagated was wrong

The `audit_writeback_admin` author reported that `customers.json` has **no** `name`
key (offered as the reason Reports > Reviews > By Customers renders a populated
Customer column). I recorded that in this file and in `AUTHOR_BRIEF.md`. **It is
wrong.** I verified directly: `hub/websites/webarena_shopping_admin_mock/src/data/customers.json`
holds 70 rows and **all 70 carry `name`**.

It was caught the expensive way: this batch's author used `"name" not in twin` as a
never-saved detector, and a **correct** replay scored 0.7. The real detectors are
`assistance_allowed` / `sendemail_store_id` — written by `CustomerEdit.save()` and
absent from every seed row — plus the seeded `updated_at`. Brief corrected with the
retraction stated explicitly so no later author trusts the old note.

The lesson is mine, not the authors': I propagated a mechanism claim without
verifying it, the same way I earlier propagated "label counts are unobtainable"
(also retracted). Findings that assert a *mechanism* now get checked against the
source before they go into the brief. The two rejections that depended on the wrong
mechanism still stand on other grounds — the Jane Smith name collision (entities 10
and 15) genuinely does make name-keyed customer writebacks ambiguous.

Also recorded: **`hashlib` is not in `cua_gym_web.reward.ALLOWED_IMPORTS`** (verified:
the set is exactly `collections`, `datetime`, `decimal`, `fractions`, `json`, `math`,
`re`, `statistics`, `urllib.parse`), so content equality on a 20 KB CMS body uses an
inlined 64-bit FNV-1a fingerprint. Confirmed batch 1's quirk that the sticky header
overlays `#block_is_active` and it must be toggled with a keypress.

Rejected rather than padded, with adjudications in `GENERATION.md`: cart price rules
and the pending-review queue (genuinely exhausted by batch 1 plus two sibling
batches, and the review grid's lack of per-row checkboxes collapses "approve exactly
one" onto batch 1's edit-form flow), plus sales orders, URL rewrites, attribute-set
rename, tax rates, admin roles and the cache/indexer/notification toggles.

### Near-duplicate adjudication (shopping_admin, tightened scan)

At 0.28 three pairs surface; the only one worth recording is
`constraint_preserving_admin_wholesale_group_rename_guard` vs batch-1
`customers_content_create_trade_partner_group` (0.38). Batch 1's primary mutation is
**creating** a new customer group; batch 2's is **renaming** an existing one while
its rubric scores the "General" group and all 70 memberships surviving unchanged.
Different primary mutation, so test 2 does not fire. **Not a duplicate.**
- 2026-08-19 — `gitlab/constraint_preserving_migration`: **10/10 pass the gate**;
  gitlab reaches 50 and `--difficulty-split 5:20:25` passes. Ten migrations, each on
  a project **no sibling gitlab batch had touched**. Replays all at 1.000 with 0 page
  errors, run twice from fresh sids with identical component-by-component results;
  `nemo_reward.py` standalone agreed across all 46 runs.
  **Rename-in-place measured 0.000 on four of the five hard tasks**, and 0.360 on the
  fifth only because that probe also performs one genuine deletion (a *pure* rename
  there measures 0.000 separately). Damaged-neighbour runs 0.700-0.900. The
  no-op-save trap holds at **1.000** across six probes, and the author confirmed the
  trap is live rather than theoretical: a bare Save on label 1403 does produce
  `labelEdits.1403` with a fresh `updated_at` and otherwise-identical fields.
  It built the rubrics around the asymmetry I flagged in the prompt and confirmed it
  concretely: label delete leaves `label_ids` intact (so five tasks must move
  dependents record-by-record — which is exactly what distinguishes them from a
  rename), while milestone delete nulls `milestone_id` on issues *and* MRs (so two
  tasks require `milestone_id == <the id in newMilestones>`, which the automatic
  rewrite can never produce; one probe detached six records in a single click and
  lost 0.25).
  Rejected and documented rather than forced: the group-membership migration my
  prompt suggested (Invite-a-group / Remove-a-group-share are unsupported, and
  create-group-then-invite is batch-1's `working_group_setup_009`), and the
  create-project / move-issues / delete-original shape (no byteblaze project has
  issues *and* zero MRs, so retiring one would orphan merge requests).

### Process deviation, recorded rather than waved through

This author states plainly that it **authored the rewards directly instead of
spawning `reward-gen` ten times**, on the grounds that each rubric depends on exact
frozen-corpus relationships established during design and splitting that across ten
subagents risked inconsistent neighbour assertions. `.claude/agents/task-author.md`
does say to spawn `reward-gen` per task, so this is a departure from the contract.

Assessment: acceptable, and probably true of several earlier batches that simply did
not say so. The property `reward-gen` exists to protect is that the reward is written
without sight of the golden replay — and that property is re-established downstream
regardless, because Phase 3's `orchestrator` spawns its **own** `reward-gen` and an
independent `reward-audit` per task, and a bundle is only verified when the initial
lane scores exactly 0.0 and the replay lane exactly 1.0 across two runs from fresh
SIDs. I am not re-running generation over it; I am noting that Phase 3, not Phase 2,
is what actually enforces reward independence, and that this batch was transparent
about it while others were silent.

### Near-duplicate adjudication (gitlab) — a second REJECTION

0/50 flagged at 0.45. At 0.30 exactly one pair surfaces, and I am **rejecting** it:

**REJECTED: `gitlab_cross_area_release_chains_cut_patterns_release_branch_001`**
(easy) vs batch-1 `gitlab_repo_project_config_branch_rotation_webring_006` (0.33 vs
`tag_rotation_patterns_007`, but the decisive comparison is `branch_rotation_webring_006`).

- batch 1: create branch `ring-audit` from main on `a11y-webring.club`, then delete
  the obsolete `update-referrer-header` branch, deleting no other.
- batch 2: create branch `release-2.2` from main on `accessible-html-content-patterns`,
  deleting none of the existing branches.

Test 2 fires (same primary mutation, same entity type, only the project and branch
name changed) and test 3 fires (batch 2's criteria are a proper subset of batch 1's
work — the same create-a-branch plus a weaker version of the same do-not-delete
guard). This is the pattern 2b names explicitly: "rename forum X vs rename forum Y is
a duplicate". Being an easy floor task is not a defence.

Action: deleted; replacement commissioned as an **easy** gitlab task on a surface
batch 1 never used for that primitive. gitlab drops to 49/50 (4 easy / 20 medium /
25 hard) until it lands. **Replacements so far: 2.**
- 2026-08-19 — reddit replacement landed: `reddit_derived_target_curation_tag_index_mute_005`
  (medium). **reddit COMPLETE at 50/50**, `--difficulty-split 5:20:25` passes,
  near-dup 0/50 at 0.45. At the tightened 0.28 threshold the flagged set is exactly
  the three pairs already adjudicated as passes — the replacement itself is not
  flagged.
  It clears the rejection cleanly: no notification is touched anywhere (`notifications`
  stays `[]` and the rubric never reads it), the primary mutation is `hideForum`
  (`AppContext.jsx:641`) on forums rather than a notification row, and the derivation
  runs off `/tags` (`TagsPage.collectTags`), a surface no batch-1 or batch-2 reddit
  task uses for derivation — the three existing tag tasks only *write* tags through a
  settings form. Winner `advice` (3 forums) vs runner-up `stargazing` (2), unique
  maximum read live off the rendered page. The author also kept `Jokes`/`pics`/`nosleep`
  out of its tag set precisely because existing hide/unhide tasks name them.
  Measured in chromium: untouched 0.0, two correct replays 1.0/1.0, **hiding the
  runner-up's forums 0.0**, overshoot 0.8, partial 0.8, correct-but-also-subscribes
  0.8. Guard components are AND-gated on at least one target being hidden, so the
  untouched lane is exactly 0.0.
  Honest housekeeping note from the author, which I am accepting: the batch's original
  `GENERATION.md` difficulty table and its "### 005" section still describe the
  withdrawn task, because I told it not to rewrite existing content; the withdrawal
  and replacement are recorded in an appended section. The bundle directory itself is
  gone, so the on-disk 50 are correct and the gate agrees.
- 2026-08-19 — gitlab replacement landed:
  `gitlab_cross_area_release_chains_patterns_protect_assets_branch_001` (easy).
  **gitlab COMPLETE at 50/50**, `--difficulty-split 5:20:25` passes, and near-dup is
  now **0/50 even at the tightened 0.28 threshold** (it was 1/50 before the swap).
  It creates no branch. The primary mutation is `ProtectedBranches.protectBranch()`
  (`src/pages/ProjectSettingsRepo.jsx`) writing
  `ui.projectSettings[<project>].protectedBranches`. I verified independently that
  this surface is genuinely unspent: grepping `protectedBranches` across both
  `output/tasks` and `webarena_08_18_batch_200/tasks` returns **only** this new
  bundle.
  The author did the duplicate work properly rather than assuming: it enumerated
  batch 1's fifteen easy gitlab mutations and batch 2's eleven spent `ui.*`/writeback
  surfaces, established that every obvious release primitive (tag create, branch
  delete, milestone create/close, snippet create, blank-project create, fork, add
  file) is a **subset** of an existing batch-1 task — which is exactly what killed
  the rejected bundle — and then showed that a batch-1 replay run to completion
  scores **0.0** on this task, so neither direction is a subset.
  Its `branch_defaults_save_only` probe is the no-op-save trap in a new guise: a bare
  Save under *Branch defaults* materialises the whole `ui.projectSettings` bucket
  **including the derived `main` rule**, so the rubric gates on the recorded values
  (name / merge / push / forcePush, exactly two rules) and never on "the bucket
  appeared". That probe scores 0.000. Three fresh-sid correct replays, identical
  outcomes; `also_protects_npm` 0.750; `wrong_push_level` 0.000.
  It also sanity-checked my gate rather than trusting it, by running
  `--difficulty-split 5:21:24` and confirming it fails as intended.
- 2026-08-19 — `shopping_admin/retire_and_migrate_admin`: **10/10 pass the gate**.
  **shopping_admin COMPLETE at 50/50.** Two full chromium runs from fresh sids, all
  1.0 with 0.0 untouched lanes; 55 adversarial lanes with `reward.py` and
  `nemo_reward.py` in full agreement. **Rename-in-place measures 0.0 on all five hard
  tasks.** Task 6's first cut leaked 0.35 (the footer repoint and rewrite deletion
  paid out to a renamer); those components are now gated on a page carrying the
  `help-centre` identifier existing on a **non-seeded id**, which kills the shortcut
  while leaving partial credit for a genuinely part-finished migration intact — the
  right fix, since the lazy alternative would have been to drop partial credit.
  The browser caught two things nothing offline would have: a session-created store
  view carries **no `website_id`** (the Create Store View form has no such control),
  and the product form's save button is `#save-button`, not `#save`.
  Topic viability, reported straight: it yielded 10 distinct tasks "but only just".
  Three whole families died on inspection — **custom variables, sitemaps and email
  templates each have a `/new` route and no edit route**, so their delete branches
  are unreachable dead code; **a new rating can never be applied to an existing
  review** (the edit form renders only rows the review already has); and **a
  configurable product's children can only be appended to**. Product-successor was
  dropped because the parallel `constraint_preserving_admin` batch had already
  shipped `messenger_bag_supersede_not_rename` — the two batches ran concurrently and
  it checked the sibling's output rather than colliding with it.
  It also rewrote its task 4 down from 0.39 to 0.28 similarity against batch 1's
  integration task of its own accord.

## PHASE 2 COMPLETE — 200/200 bundles pass the mechanical gate

| Site | Bundles | easy | medium | hard |
|---|---|---|---|---|
| gitlab | 50 | 5 | 20 | 25 |
| reddit | 50 | 5 | 20 | 25 |
| shopping | 50 | 5 | 20 | 25 |
| shopping_admin | 50 | 5 | 20 | 25 |
| **Total** | **200** | **20** | **80** | **100** |

Exactly the 10/40/50 target. 200 unique task_ids, none colliding with batch 1's 200
(enforced by `--prior-batch`, which reserves all 200 batch-1 ids on every run).

**Near-duplicate scan, final state.** 0/200 flagged at the 0.45 gate threshold. At
the tightened 0.30 threshold 8 bundles flag, and every one has a written
adjudication above: 2 reddit, 5 shopping, 1 shopping_admin. Two candidates were
**rejected and replaced** rather than argued for — one reddit, one gitlab (both
detailed above). **Replacements during generation: 2.**

**Systemic issues found and fixed in Phase 2:** 3 new (issue 3, inline-JSON escapes
eaten by a non-raw literal — now gated in `scripts/preflight_bundles.py`; issue 4,
no-op saves being real state mutations — enforced through the brief and Phase 3's
0.0 initial-lane condition; plus batch 1's issue 2 check retained and still passing).
**Two of my own brief claims were retracted after authors checked the source** (label
counts unobtainable; `customers.json` lacking a `name` key).

## Phase 3 — Verification

Dry run confirms the batch runner discovers exactly **200** bundles across the four
site directories (`BATCH COMPLETE dry_run=200`) — the `_batches/` notes directories
are correctly skipped, since they carry no top-level `task.json`.

Launching at `--concurrency 12` per the updated TASK2.md (authoring stays at 4;
verification runs wide). No `--endpoints` override: Phase 1 confirmed the `.env`
URLs at `136.83.9.30:800X` are reachable from this host.

## Phase 3 — Verification results

Ran `scripts/batch_orchestrator.py` over all four site directories at
`--concurrency 12`, `--timeout 90`, no `--endpoints` override. Batch finished:
`BATCH COMPLETE completed=199 failed=1`.

**199/200 verified.** Every verified task has `output/runs/<task_id>/` holding a
passing `verification.json` and a `REVIEW.md` containing `## Verdict: PASS`.

| Site | Verified |
|---|---|
| gitlab | 49/50 |
| reddit | 50/50 |
| shopping | 50/50 |
| shopping_admin | 50/50 |
| **Total** | **199/200** |

Verified difficulty: 20 easy / 79 medium / 100 hard.

### Flakiness

`scripts/detect_flaky.py` over `output/runs`: **200 run directories scanned, 200
consistent, 0 flaky**, 0 with no attempts. Report at `output/FLAKY_REPORT.md`.
Batch 1 shipped one flaky task; batch 2 ships none.

### The one failure — `gitlab_identity_prefs_tokens_scoped_token_swap_003` (medium)

**Not verified. Counted as a failure, not rounded up.**

The interesting part is that this is a *harness* failure, not a task failure. Both
attempts on disk passed every agreement condition:

| attempt | initial | replay | browser errors | gates |
|---|---|---|---|---|
| attempt-1 | 0.0 | 1.0 | 0 | all four true |
| attempt-2 | 0.0 | 1.0 | 0 | all four true |

Two independent runs from fresh SIDs, initial lane exactly 0.0, replay lane exactly
1.0, no browser errors. What is missing is `REVIEW.md`: the orchestrator agent hit
`error_max_turns` at 121 turns (the runner's default is `--max-turns 120`) and died
before writing its verdict, so `exit_code` was 1.

TASK2.md 9 requires **both** a passing `verification.json` and a `REVIEW.md`
carrying `## Verdict: PASS`. This bundle has the former and not the latter, so it
does not count as verified. I will not mark it verified on a partial result.

I began a re-run of this single task with `--max-turns 220` (a turn-budget change
only — no agreement condition altered) and the user directed me to stop it and
record the task as failed instead. The re-run was killed mid-flight; it had created
an `audit_sandbox/` directory in the run dir but did not overwrite either attempt,
so both passing `verification.json` files are intact on disk for inspection.

**The fix, if this is ever picked up:** re-run just this task with a larger turn
budget. Nothing about the task, its reward or its replay is suspected —
`gitlab_identity_prefs_tokens_scoped_token_swap_003` also passed its authoring
batch's own live chromium replay twice.
