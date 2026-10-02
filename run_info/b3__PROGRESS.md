# WebArena task batch 3 — 600 new tasks, easy-weighted

Target per TASK3.md: **150 per site** (gitlab / reddit / shopping /
shopping_admin) at 120 easy / 30 medium / 0 hard, **600 total**, deduped against both
`webarena_08_18_batch_200/` and `webarena_08_19_batch_200/`.

## Phase 1 — Preflight

Run 2026-08-20. All nine checks green. Check 8 triggered a scope revision — see below.

| # | Check | Result |
|---|---|---|
| 1 | Five hub ports answer | `8000 200`, `8001 200`, `8002 200`, `8003 200`, `8004 200` |
| 2 | State API round-trips on a scratch sid | `GET /go?sid=b3-preflight` returned `initial_state` / `current_state` / `state_diff` with `state_diff == {}` |
| 3 | `python3 -c "import requests, playwright"` | ok |
| 4 | `python3 -m playwright install chromium` | ran, idempotent, no output |
| 5 | `python3 -m pytest tests/ -q` | **24 passed in 0.18s** |
| 6 | `.env` endpoint URLs reachable | all five of `http://136.83.9.30:800X/` return 200 — no `output/endpoints.json` override needed |
| 7 | Prior inventories | `output/prior_inventory/<site>.txt`, **100 lines each** (50 batch-1 + 50 batch-2) |
| 8 | **Unspent-primitive inventory** | written; see the revised assessment below |
| 9 | Harness scripts | all four parse and run; `preflight_bundles.py` still carries both `js_literal_names()` and `broken_inline_json()` |

`output/` was empty at the start of this run, as TASK3.md §2 expects.

---

## Phase 1, check 8 — supply analysis, and a correction to my own first reading

### What I measured first, and why it was the wrong unit

Cross-referencing each mock's live `/go` state keys and every dotted sub-key in
its `SCHEMA.md` observable table against a grep of all 400 prior `reward.py`
files:

| Site | top-level state keys | unspent | actionable handlers | unspent dotted sub-keys | prior tasks |
|---|---|---|---|---|---|
| gitlab | 41 | 1 | ~85 | 2 (both dead ends) | 100 |
| reddit | 22 | 1 | ~33 | 0 (real) | 100 |
| shopping | 15 | 5 | ~27 | 0 (real) | 100 |
| shopping_admin | 44 | 2 | ~62 | **0** | 100 |

At the *handler* level the mocks are close to exhausted. Every top-level key a
task could plausibly be built on is already referenced by some prior reward, and
the handful that are not are id counters (`nextIds`, `nextReviewId`,
`nextAddressId`, ...) — side effects of creating an entity, not independently
actionable. The unspent dotted sub-keys are 2 for gitlab (`ui.dismissedAlerts`,
known dead; `ui.sidebarCollapsed`, cosmetic) and effectively **0** elsewhere.

On that basis I estimated a ceiling of ~250-400 easy tasks total and stopped to
ask, per TASK3.md §2c.

### The correction

**That analysis used the wrong unit of supply, and the user was right to push
back.** The unit is not the handler; it is **handler x injected precondition**.
`initial_setup.py` can put the same control into starting states the pristine
seed never produces, and several of those reach branches that are otherwise dead
code.

The evidence is unambiguous and was already in the prior batches:

- **308 of the 400 prior bundles ship an `initial_setup.py`** — 131 in batch 1,
  177 in batch 2. Injection is already the norm, not an exception.
- The four mocks carry **~327 conditional-render / guard sites** in their JSX
  (~147 gitlab, ~112 shopping_admin, ~35 shopping, ~33 reddit). Each is a branch
  gated on state.
- Two branches are provably unreachable without injection: reddit `moderates()`
  reads only `state.moderatorOf`, **empty** on the pristine seed, so every
  moderator-only route is closed; and `ForumDeletePage` requires
  `submissionCount == 0`, which **no seeded forum satisfies**.

Neither of those is an instance variation — they change which code path runs. My
key-level count could not see any of it, because a precondition is not a key.

### Revised assessment: GO at 600

150 per site is supportable at the strict duplicate standard, with the injected
precondition as the primary novelty axis. Recorded caveats:

- **gitlab and shopping_admin have the most headroom** (~85 and ~62 handlers,
  ~147 and ~112 guard sites).
- **shopping and reddit are the tight sites** (~27 and ~33 handlers) and are the
  most likely to come in under quota. If either does, it is reported with its
  measured ceiling rather than padded.
- Injection is not a duplicate-laundering device. It earns a new task only when
  the precondition changes what the agent must do or which branch executes;
  "delete injected forum A" vs "delete injected forum B" remains a duplicate.
  This rule is written into `output/AUTHOR_BRIEF.md` §0 and every bundle must
  state its injected precondition and the branch it unlocks.
- `webarena_classifieds_mock` is deployed, already in `APP_DIRS`, and carries
  **zero** prior tasks. Out of scope for batch 3, but it is the obvious cover for
  a shortfall and is flagged rather than silently used.

Per-site detail in `output/unspent_primitives/<site>.md`.

---

## Phase 2 — Topic planning

15 disjoint topics per site are needed (60 total), on top of the 10 slugs already
spent per site. Each topic must name the handler x precondition combinations it
draws on. Planning is delegated to one agent per site (4 concurrent, the Phase 2
cap), each grounded in that mock's source and both prior batches' GENERATION.md
files.

### Batch log
- 2026-08-20 — **reddit topic plan returned: hard ceiling, far below quota.**
  Defensible number: **11 tasks (4 easy / 7 medium) across 3 topics**, not 150
  across 15. Method: enumerated the full mutation surface from `AppContext.jsx`
  plus the seven raw-`setState` pages — **42 mutation variants, all 42 already
  spent** by the 400 delivered tasks — then grepped all 76 prior reddit
  `initial_setup.py` files for what they inject. Seven state keys were never
  injected; four of those change only what a page *renders*, not what a handler
  *does*, so they yield no easy tasks. The three that change handler behaviour
  yield 4 distinct easy branches between them.
  The three viable topics: `admin_forum_teardown` (injecting `currentUser.admin`
  enters the left disjunct of `ForumDeletePage.jsx:32-34`, dead code today because
  0 of 95 seeded forums have `submissionCount == 0`); `co_moderator_standdown`
  (injecting `forums[].moderators` reaches the populated-table branch at
  `ForumModeratorsPage.jsx:87-121`, which no seeded forum carries — this directly
  reverses batch 2's "rejected as unbuildable, there is no second row to protect",
  a judgement that was correct under a no-injection assumption and wrong under
  this one); and `moderator_trash_backlog` (preseeded `visibility: "trashed"`
  makes `/trash` render for the first time).
  Source-checked rejections worth keeping: `/users` unlocks with admin but is
  useless (21,038 rows at 25/page, no count sort); `add_moderator` renders no Add
  form even for an admin; the `featured` checkbox is *omitted* from both forum
  forms rather than hidden; a preferences topic is dead because only 6 of 17
  fields are read anywhere in `src/`.
  Caveat the planner flagged itself: the `admin` and `moderators` injections are
  verified by reading the guards and measuring `src/data/`, not by driving a live
  sid. The first author on either topic must POST the setup to a throwaway sid
  before building on it.
- 2026-08-20 — **gitlab topic plan returned: 150 reachable, ~135 without reservation.**
  15 topics, each with handlers, injected preconditions cited to `file:line`, a
  non-re-slice argument against all ten spent slugs, and a task count. Two findings
  carry the plan:
  * **`ui.projectSettings` is the big unspent vein** — a 17-field bucket
    (`pages/projectSettingsStore.js:15-36`) written by ~25 handlers across seven
    settings routes, and exactly **one** of the 100 prior gitlab tasks writes it.
    Every collection in it (`mirrors`, `protectedTags`, `deployTokens`,
    `deployKeys`, `accessTokens`, `ciVariables`, `triggers`, `deployFreezes`,
    `hooks`) is `[]` pristine, so each renders only its empty state and **every
    delete/revoke branch is dead code until a setup populates it**. That vein
    alone carries 5 topics.
  * **Fifteen record fields are constant across the entire seed**, which starves
    the reversal side of every guard that reads them: `archived` false x175,
    `forked_from` absent x175, `feature_settings` absent x175, `confidential`
    false x19,705, `discussion_locked` absent, `draft` false x23,236,
    `milestones[].start_date` null x343, zero namespace memberships for byteblaze,
    and `ui.labelSubscriptions` / `prioritizedLabels` / `unsubscribed` /
    `groupLinks` absent from `initialState.js:89`. Each is one injection away from
    a branch nothing has ever reached.
  Rejected with source evidence: snippets (`Snippets.jsx` never reads
  `state.snippets`, and `NewSnippet` never writes `project_id`); boards, pipelines,
  releases and all dashboards (zero mutation handlers); ~12 hardcoded empty states
  with no populated branch in code; 4 permanently-disabled controls; and the fact
  that no reaction *removal* exists.
  Honest caveat: topics 9 (`issue_flag_reversal`) and 10 (`mr_draft_and_merge_gates`)
  are thinnest, with 5-6 branch-distinct tasks each before they start leaning on
  field variety. Bulk issuable updates on merge requests is named as the strongest
  replacement source.
- 2026-08-20 — **shopping topic plan returned: ~62 defensible, 8 topics, not 150 across 15.**
  It planned 8 rather than padding to 15, with an honest per-topic count (four at
  10, four at 6-8). Arithmetic, from source: `AppContext.jsx:645-655` exposes **20
  mutating handlers of which `clearCart` is dead** (no call site anywhere in
  `pages/` or `components/`), so 19 are reachable and **all 19 are already used**
  by the 100 delivered tasks. It found ~40 state-dependent branches, of which ~22
  are both unreachable on the pristine seed and unspent. At the ~2-3 tasks per
  branch that rule 2b allows before variants collapse into instance changes, that
  is 22 x 2.7 = ~59; 150 would need ~6.8 tasks per unspent branch.
  Two strong discoveries, both source-verified:
  * **261 out-of-stock products are invisible to every listing, search and facet**
    (`utils/catalog.js:412-413`, `:1032`, `:1154-1156`), and their PDP suppresses
    the option fields (`ProductPage.jsx:722`), the whole qty + Add to Cart block
    (`:757`) and Add to Compare (`:825`), while Add to Wish List survives and
    forces qty 1 (`:811`). 118 of them carry required options whose fields
    therefore never render. Untouched by all 400 prior tasks because no prior
    route could reach them.
  * **No prior batch on any site has ever injected `orders`.** That unlocks a
    status the seed lacks (exactly 25 complete / 9 canceled / 3 pending), a line
    price disagreeing with the catalog (`reorder` re-prices at
    `AppContext.jsx:630`, and **zero of 22,721 products carry a `specialPrice`**,
    so that branch is observationally inert today), a line name disagreeing with
    the catalog, and the 6-line case that makes `SidebarBlocks.jsx:133`'s
    `slice(0,5)` actually truncate (the seed's largest order has exactly 5 lines).
  Also: the pristine address book's sole card **has no Delete link at all**
  (`AddressBookPage.jsx:13-15, 80-84`) and its edit form swaps both default
  checkboxes for info messages (`AddressEditPage.jsx:14, 191, 203`) — so batch 1
  was right that "delete my only address" is impossible, but a dangling default
  pointer injected in setup makes it reachable and forces repair through *Add New
  Address* rather than edit.
  Traps recorded for downstream authors: three different qty policies for the same
  concept (reject / clamp / clamp-on-keystroke), so `updateCartQty`'s `qty > 0`
  filter is UI-unreachable; four success messages that fire after writing nothing;
  `AddressEditPage.jsx:11-13` has **no 404 guard** and silently renders the
  Add-New form for an unknown id; `GoPage.jsx:21`'s `initialState || state` is a
  second independent reason to read `current_state` only; `AdvancedSearchPage.jsx`
  never imports `useApp` and writes no state at all.
- 2026-08-20 — **shopping_admin topic plan returned: 15 topics, ~130 defensible.**
  "150 is not comfortable": ~124 defensible easies against a requirement of 120,
  with five topics short by 1-2. The number it stands behind is **~130 (13 topics
  x 10)**. Reaching 150 needs field-level granularity on the two catalog topics —
  precedent both delivered batches already set, but the first thing a strict
  reviewer would challenge; if that axis is disallowed the site falls to ~105.
  Its recommendation: commission all 15, brief the five short topics to report
  8-9 bundles rather than pad, and plan for 125-135 accepted.
  Findings worth keeping:
  * **`CreditMemoNewForOrder` is live dead code with an explicit invitation** —
    `CreditMemoNew.jsx:88-99` serves the refund form when `canCreditMemo(order)`,
    and the source comment says "If an injected task state ever hands an order
    real `total_paid`, the source would serve the form and so will we." Batch 1
    rejected the route as unreachable and never tried the inject.
    `orderOverrides[N].total_paid` also has three distinct refusal branches.
  * **`payment_review` is a state no seeded order has**, and it short-circuits
    eight of the nine order-view guards at once. The comment form's Status select
    is state-filtered (`OrderView.jsx:389-393`): 0 options for `pending`, 1 for
    `new`/`holded`, 2 for `processing`/`payment_review`.
  * **Widgets are the only `systemConfig` collection with a registered edit
    route** (`App.jsx:424`), and Delete renders only for a row already in state
    (`Design.jsx:529`), so on the pristine seed no widget can be deleted at all.
  * **It retracts a batch-1 claim:** newsletter templates, synonym groups and
    checkout agreements *do* have working create writers and routes; only their
    edit/delete halves are dead. That is what makes `small_entity_registry`
    viable (8 never-touched create forms).
  * **It narrows a batch-1 rejection:** `stores_system` dropped currency work as
    "the same `coreConfig` rubric", true only for `currency/options/base`; the
    rates/symbols grids write `systemConfig.currency_rates` / `currency_symbols`.
  * New dead surface: `special_from_date`, `special_to_date`, `tier_price`,
    `msrp` have no control and are absent from `buildPatch()`.

## Phase 2 topic planning complete — measured ceilings vs the 600 target

| Site | quota | defensible | optimistic | topics planned |
|---|---|---|---|---|
| gitlab | 150 | ~135 | 150 | 15 |
| shopping_admin | 150 | ~130 | 150 | 15 |
| shopping | 150 | ~62 | ~62 | 8 |
| reddit | 150 | **~11** | ~11 | 3 |
| **Total** | **600** | **~338** | **~373** | 41 |

**The binding constraint is my own duplicate rule, not the mocks.** Both the
reddit and shopping planners identified §2b **test 3** — "success criteria are a
subset of a prior task's" — as what caps them, because **320 of the 400 prior
tasks are multi-mutation**, so almost any new single-mutation task on an
already-used handler is a proper subset of some prior composite flow. Under that
reading, easy novelty can *only* come from a branch nothing has ever reached.
gitlab and shopping_admin escaped it by finding genuinely unspent veins
(`ui.projectSettings`, credit-memo refunds); reddit and shopping have no such
vein and collapse to their unreached-branch count.

Generation is paused pending a decision on how to close the ~230-task gap.

## Test 3 refined (start-state qualifier) — replanning under the corrected rule

TASK3.md §2b test 3 and `output/AUTHOR_BRIEF.md` now read: a subset counts as a
duplicate only when the task also **starts from a materially equivalent state**.
A precondition is materially different when it changes which branch executes,
which controls render, or what the agent must do — not when it merely reshuffles
values. **Test 2 is untouched**, so pure instance variation remains a duplicate.
Rationale: the old wording was written for batch 2 (50% hard tasks); against an
80%-easy batch it capped the corpus at the never-reached-branch count. Decision
taken by the user; classifieds explicitly **out** of scope.

All four planners were resumed rather than restarted, so their prior analysis is
intact.

- 2026-08-20 — **gitlab replan: ceiling raised to 150 without reservation.** The
  earlier ~135 was entirely about topics 9 and 10 running out of branch-distinct
  work; that reservation is withdrawn. Six topics firmed up (6, 8, 9, 10, 11, 12).
  Representative new preconditions, all source-verified: an injected pending todo
  flips `IssueDetail.jsx:374` from `'Add a to do'`/`appendTo` to
  `'Mark as done'`/`updateIn`, and the seed has **7 todos against 19,705 issues**,
  so pristine essentially every issue offers only the add direction; a
  pre-attached label/assignee/milestone turns sidebar work into the *removal*
  direction, where **18,762 of 19,705 issues have no assignee** pristine;
  `draft: true` on an MR whose title lacks the `Draft:` prefix makes two routes to
  the same field observably different, because `EditMergeRequest.jsx:56`
  re-derives `draft` from the title while `MergeRequestDetail.jsx:351` does not.
  The planner also volunteered **two corrections against its own earlier plan**:
  * **`merge_status` is inert** — written at `MergeRequestDetail.jsx:347` and
    `NewMergeRequest.jsx:184`, **read nowhere**; the widget branches on `mr.state`
    alone, so an injected `cannot_be_merged` does not block Merge. It had listed
    this as a topic-10 precondition and retracted it in place.
  * **No comment edit or delete exists** — `NotesTimeline.jsx` posts and nothing
    else, with no `noteEdits`/`deletedNotes` writer anywhere. It found this while
    hunting an authorship-gated branch and killed the idea rather than shipping it.
  Also recorded: the merge commit-message textarea (`:357`) calls `patch()` per
  keystroke, so rewards must score the final value and never count writes.
  Surplus held in reserve (plan stays 15 x 10): bulk issuable updates on merge
  requests, group shares via injected `groupLinks`, and to-do queue states.
- 2026-08-20 — **reddit replan: ceiling raised from 11 to ~63 (38 easy / 25 medium)
  across 10 topics.** Still well short of 150, and the planner explains why in a way
  that holds up: the 42-variant enumeration still stands (all spent), but the
  multiplier is now the number of materially distinct *precondition shapes*, and
  that set is small and enumerable — a collection is empty / holds one / holds many;
  a comment is a leaf or has children of three visibilities; a record is frozen or
  overlay; a forum is or is not deletable, moderated, subscribed, hidden. Prior
  batches used "many" and "frozen" almost exclusively, which is exactly what leaves
  room.
  Strongest new topic, `terminal_collection_states` (8 easy): every list key
  injected at **exactly one entry** so the mutation crosses an empty-state
  threshold, with a second branch flipping alongside in all eight cases —
  unsubscribing to zero restores the `FrontSidebar` "Featured forums" card and
  triggers the `/subscribed` -> `/featured` 302 (`ListingPage.jsx:137-139`);
  clearing the last notification removes the "Clear all" form itself
  (`NotificationsPage.jsx:71-81`); deleting a one-message thread hits `lastOne` and
  drops the whole thread (`MessageThreadPage.jsx:68-88`), a branch no prior message
  task ever ran; clearing a forum's last tag 404s `/tag/<n>`.
  Also a genuine find behind `tree_shape_deletes`: `hasChildComments`
  (`overlay.js:323-335`) skips only `deletedComments`, so a comment whose only child
  is preseeded *trashed* renders childless yet takes the soft-tombstone branch and
  does not decrement `commentCount`.
  **Correctness trap the new topics create, flagged by the planner and now in its
  §5.4:** topic 3.4 is built on returning keys to their pristine values, and per
  SCHEMA.md a key that returns to baseline **leaves `state_diff` entirely** — so
  every such reward must read `current_state` or it scores a correct replay 0.0.
  Delivery-shape note: at the 8-easy/2-medium ratio the easy supply binds at 38/8,
  so reddit is **4 full batches, 5 if one runs light**. It can yield roughly 15 more
  *medium* tasks than that ratio permits, so for this site the binding lever is the
  mix, not the mock.
- 2026-08-20 — **shopping replan: ceiling raised from 62 to ~105 (84 easy / 22
  medium) across 11 topics**, against 150 asked. Shortfall ~45, i.e. 4-5 batches.
  The arithmetic changed shape: under the old rule the unit was *unreached branch*
  (~22 at 2-3 each); under the corrected rule it is **handler x materially-distinct
  precondition**, and the planner counted the cells per handler — `saveAddress` 6,
  `addToCart` 5, `submitReview` 5, `placeOrder` 5, `reorder` 5, `updateCartQty` 4,
  `addToWishlist` 4 ... `setNewsletter` 1, `submitContact` 1 — **~62 cells**. Most
  yield exactly one easy; the richer ones yield two. At ~1.35/cell that is ~84 easy.
  **120 easy would need ~1.9 per cell**, and for roughly a third of them (the
  boolean and single-control cells) there is only one way to exercise the cell
  without falling to test 2. Mediums are not the constraint.
  Three topics raised because the corrected rule legitimises what it had discounted
  — notably `blocked_form_recovery` 6 -> 10, where it re-read its own list and found
  the tasks are **eight different guards in six different files**, each with its own
  message and recovery action, not one guard with field variety. And
  `prepopulated_review_log` 8 -> 10 on the strength of `ProductPage.jsx:606`:
  **16,766 products have no reviews at all**, so a first review flips the PDP out of
  "Be the first to review this product", changes the tab counter and makes
  `ProductGrid.jsx:36` start rendering stars on every tile.
  Three new topics: `paginated_collections`, `drifted_cart_lines` (injected lines
  whose stored price/name disagree with the catalog — `CartPage.jsx:149`/`:164`
  render the *stored* values and `placeOrder` writes them into `orders`, the
  cleanest "did you really buy the cart?" discriminator available), and
  `account_identity_states` (thin at 8; first to drop if a slot must go).
  **Two axes I suggested do not exist**, checked against the seed rather than
  assumed: there are **zero** required options with a single value (all 13,886
  groups carry 2-6 values, all `type: "radio"`), and there is **no compare-list
  capacity limit in the code** — `addToCompare` has only a dedupe guard, and
  Magento's real 5-item cap is not reproduced. Also newly dead: option price deltas
  (`ProductPage.jsx:744` never renders; zero groups carry a non-zero option price
  and `addToCart` ignores them anyway), and `contactSubmissions`, which is
  **write-only** — it appears at `AppContext.jsx:498` and `dataManager.js:145` and
  nowhere else, so injecting it changes no branch and is not a material precondition.
- 2026-08-20 — **shopping_admin replan: 130, and the planner declined to raise it.**
  Its answer is worth quoting in substance: the corrected test 3 buys
  **robustness, not volume** — it lets the site reach 130 on strong preconditions
  instead of reaching 130 partly on field variety. "A better 130, not a bigger
  one." It does not create new surface. That is a straight answer to a question it
  could easily have fudged, and I am taking it at face value.
  Per-topic table splits every slot by axis: **122 strong + 16 weak = 138** easies
  against 120 required. Counting all slots, 14 of 15 topics reach 8; counting only
  the strong axis, three fall short — topics 5 and 6 (the catalog product-form pair,
  5 each, because the product form has about **five** genuine guards between them,
  not ten) and topic 15 (7).
  Its recommendation, which I am adopting: **merge topics 5 and 6** into one
  `product_form_type_guards` on their ten combined strong slots, **cut topic 15**
  and fold its cache/indexer preconditions into topic 11 (which has room at 12).
  That leaves **13 topics x 10 = 130**, every one reaching 10 on the strong axis
  alone.
  Five short topics repaired with preconditions rather than field variety. Best new
  finds: an injected widget `instance_id` that *collides* with a seeded row flips
  Save from shadow-append to `update` (`Design.jsx:493-495, 536-537`) — two
  different outcomes for the same click; **downgrading a cart rule to No Coupon
  orphans its coupon row**, because `Marketing.jsx:244-258` rewrites `coupons` only
  inside the `coupon_type === 2` branch while `remove()` cascades, which is an exact
  detector for "edited the rule" vs "deleted and recreated it"; and **Apply Rules
  has a decline branch the seed cannot reach** (with both catalog rules inactive it
  writes nothing), so injecting one inactive rule makes Apply stamp exactly one and
  leaves the other scorable as untouched.
  It also replaced `currency_scope_desk` (caps at ~5 real slots) with
  `promotion_rule_conditions`, and rebuilt `review_editorial_desk` on review
  *states* the 351-row corpus lacks (`status_id: 3` — the seed has **zero**, with
  346 at `1` and 5 at `2`) after a keyword sweep showed rating *definitions* are
  spent three times over.

## Phase 2 — final planned ceilings and the delivery decision

| Site | quota | planned ceiling | topics |
|---|---|---|---|
| gitlab | 150 | **150** | 15 |
| shopping_admin | 150 | **130** | 13 (after merging 5+6 and cutting 15) |
| shopping | 150 | **~105** | 11 |
| reddit | 150 | **~63** | 10 |
| **Total** | **600** | **~448** | 49 |

**Decision, taken without further consultation per the user's instruction:**
commission every topic each plan supports and deliver ~448 rather than pad to 600.
The shortfall is a property of the four mocks, measured three different ways
(handler count, unspent state keys, handler x precondition cells), not of author
effort. Classifieds stays out of scope per the user.

One deliberate deviation from TASK3.md §5: **reddit's per-batch split will vary
from 8:2**. Its easy supply (38) binds at ~4 batches under a fixed 8:2, while it can
yield ~25 medium. Holding the ratio would throw away ~20 usable tasks, so reddit
runs mixed ratios and the 80/20 target is tracked globally instead of per batch.
The mechanical gate is invoked with the actual per-batch split for those batches.

### Batch log — Phase 2 authoring

- 2026-08-20 — `gitlab/settings_deploy_credentials`: **10/10 pass the gate** (8 easy
  / 2 medium). Replays twice per task from fresh sids, 20/20 at exactly 1.0, across
  two full regenerate-and-replay sweeps. Adversarial probes: remove-only 0.35,
  re-added with write 0.0, revoke-only 0.40, wrong token revoked 0.40, collateral
  key removal 0.0, blank username 0.0, revoked-all 0.0, and **no-op Branch-defaults
  Save 0.0** (the bucket materialises but no scored value changes — systemic issue 4
  holding).
  The author flagged three things honestly: 001-vs-008 and 004-vs-007 are its
  closest internal calls (kept apart because each pair takes opposite sides of the
  same `||` expression or requires the empty-state branch plus a scored neighbour,
  and solving one the other's way scores 0.0); **the topic is now at its ceiling**
  (three collections x {create, delete} plus four field branches and one empty-state
  return, essentially all consumed); and **the topic plan's line numbers for the
  access-token surface are wrong** — `ProjectSettingsMisc.jsx:192/195` land in the
  merge-request form, not the token table, and there is no "no scopes selected"
  rendering. It re-derived those from the real component instead of trusting the
  plan, which is exactly right.

### Near-duplicate adjudication — one REJECTION in `settings_branch_tag_protection`

The 0.30 scan flags 4 gitlab bundles against batch 2, all against the same prior
task (`gitlab_cross_area_release_chains_patterns_protect_assets_branch_001`, the
only prior bundle that writes `ui.projectSettings.*.protectedBranches`). Adjudicated
by reading the handler, not the overlap number:

- `..._unprotect_merged_csvclean_branch_001` (0.36) — **accepted.** The *removal*
  branch, which is dead code pristine because no rules exist to remove.
- `..._protect_release_tag_xlsxwriter_007` (0.32) — **accepted.** Protected *tags*,
  a different collection and a different control.
- `..._restore_default_branch_protection_imsi_008` (0.35) — **accepted.** Starts from
  a populated table with the default branch missing, so the dedupe guard
  (`rows.some(r => r.name === trimmed)`) is live rather than vacuous and
  `isDefault: trimmed === project.default_branch` takes its true branch, which the
  prior task never did.
- `..._protect_fork_branch_wildcard_buck_004` (0.38) — **REJECTED.** I checked the
  handler: `protectBranch` (`ProjectSettingsRepo.jsx:292-302`) stores `name.trim()`
  **verbatim**, with no pattern matching anywhere in the file — the only conditional
  is `isDefault`, which a wildcard never satisfies. So a wildcard rule is not a
  distinct code path; it is the same mutation on the same collection with only the
  field value changed, which test 2 forbids regardless of the batch-3 start-state
  qualifier. The "wildcards" text in the UI is placeholder copy and a help link
  (`:321`, `:327`), not behaviour. To be actioned as a replacement when that batch
  reports. **Replacements so far: 1 (pending).**
- 2026-08-20 — `gitlab/settings_branch_tag_protection`: 10 delivered, **9 accepted**.
  Replays twice from fresh sids, 20/20 clean. Adversarial probes: bare
  *Branch defaults* Save **0.00** on five tasks (the no-op-save trap holding), 009
  unprotect-only 0.00, 009 re-submit swallowed by the guard 0.00, 010 one-of-two
  0.40/0.30, 001 over-deletion 0.55. The author flagged 004 and 006 itself as its
  two weakest novelty claims rather than asserting them away, which is what let me
  adjudicate them quickly.
  **004 rejected and deleted** — `..._protect_fork_branch_wildcard_buck_004`. I read
  the handler: `protectBranch` (`ProjectSettingsRepo.jsx:292-302`) and its tag twin
  (`:415-417`) both store `name.trim()` **verbatim**, with no pattern matching
  anywhere in the file; the wildcard text is placeholder copy plus a help link. So
  the task is add-a-branch-rule with a different string on a slightly fuller table —
  same mutation, same collection, same code path as
  `gitlab_cross_area_release_chains_patterns_protect_assets_branch_001`, which also
  had a pre-existing rule to preserve. Test 2, which the batch-3 start-state
  qualifier does not touch.
  **006 accepted** on a second look. Its real distinguisher is not the wildcard: it
  removes the *only* protected tag so the section returns to its empty state
  ("No tags are protected."), which is a different branch from 005's remove-one-of-
  three-with-siblings-preserved. The wildcard is incidental to it.
  gitlab now stands at 19 bundles (15 easy / 4 medium). **Replacements so far: 1.**
- 2026-08-20 — `shopping/out_of_stock_pdp`: **10/10 pass the gate**, near-dup 0/10
  against both prior batches. Replays twice from fresh sids, 20/20 at 1.0, and the
  replays **hard-assert the branch claims** rather than assuming them — task 001
  asserts `#product-addtocart-button`, `#qty` and `a.tocompare` all count zero while
  `a.towishlist` is present; 008 and 010 assert `is_disabled()` on the out-of-stock
  Recently Ordered checkbox. That is the right way to prove a precondition topic.
  Two findings worth carrying: `ProductGrid.jsx:58-68` has **no stock check**, so
  the compare-column button is the only control that can cart an out-of-stock
  product, and `CartConfigurePage.jsx:81` renders options with **no** stock gate
  while `ProductPage.jsx:722` hides them — the same product is configurable from one
  route and not the other. Setup mechanic for later shopping batches:
  `action:"set"` shallow-merges over `createInitialData()` server-side
  (`vite.config.js:442-449`) and writes both current and baseline, so a partial
  top-level patch is safe; the order-injecting setups exploit this by posting an
  empty `set` first, reading the merged default tree back, asserting 37 orders, and
  prepending — avoiding a 60 KB inline fixture.
  **Adjudication of its self-flagged task 002** (review an out-of-stock product,
  which shares `submitReview` with ten prior `reviews_contact_*` bundles):
  **accepted.** The brief's rule counts a precondition as material when it changes
  which branch executes, **which controls render**, or what the agent must do. An
  out-of-stock PDP renders no cart form, no option fields and no compare link, so
  the agent's available surface is genuinely different. That is the same line I used
  to reject the gitlab wildcard: there, a fuller table changed neither the rendered
  controls nor the action, only the row count and the string typed.
- 2026-08-20 — `reddit/terminal_collection_states`: **10/10 pass the gate**.
  **Three full chromium replay passes** of all ten flows from fresh sids (0.00 ->
  1.00, no page errors, every time), plus a fourth pass scoring `reward.py` and
  `nemo_reward.py` side by side — identical on all ten, both lanes. Adversarial
  probes: blank Reason 0.40; **open-and-Save the settings form without clearing Tags
  0.00** (the no-op-save trap); hide instead of unsubscribe 0.00; strip all three tag
  lists 0.00; wrong thread 0.00; reply instead of delete 0.00.
  It documented its within-batch overlap instead of hiding it: 009 shares the
  `lastOne` branch with 005 and 010 shares tag-extinction with 007, in both cases
  the medium deriving its target and scoring survivors while the easy names the
  entity — and it rejected "empty all three lists" as a medium because that is a
  pure union of easies 001/002/003.
  **Near-duplicate adjudication (2 flagged vs batch 1, both accepted):**
  `..._last_hidden_forum_002` vs `reddit_voting_subscriptions_unhide_nosleep_008`
  (0.40) is the marginal call of the batch — same `unhideForum` mutation, differing
  only in that the list goes 1 -> 0 rather than 3 -> 2. Accepted because
  `Placeholder.jsx:209`'s NoEntries branch genuinely executes only in the terminal
  case, and the reward scores that end state. **This is the same test I used to
  reject the gitlab wildcard, applied consistently: does a different line of code
  actually execute?** For the wildcard, no — I read `protectBranch` and there is no
  conditional on the name at all. Here, yes. `..._last_subscription_001` (0.31) is a
  different handler entirely (unsubscribe, not unhide) and needs no argument.
  I note the weaker half of this: the empty-state render is a *consequence* of the
  action rather than something the agent sees before acting, which makes it a
  thinner claim than shopping's out-of-stock PDP, where the control set differs at
  decision time. Recorded so a reviewer can disagree with it knowingly.
- 2026-08-20 — `gitlab/settings_ci_pipeline_config`: **11/11 accepted** (9 easy / 2
  medium — the extra easy absorbs the rejected wildcard bundle). gitlab now 30
  (24 easy / 6 medium); near-dup 0/30 vs batch 1 and 3/30 vs batch 2, all three
  already adjudicated. Two replay passes, 22 replays / 44 scored runs, no variance,
  **each replay hard-asserting its precondition before acting** (row counts, absence
  of the three empty-state strings, the Token-Access box rendering unchecked, the
  git-clone radio checked, `get_by_role("button", name="Edit").count() == 0`).
  Adversarial: no-op double-*Save changes* **0.0** on five tasks despite the bucket
  materialising; delete-then-re-add-as-`Variable` shortcut **0.0**.
  Two source facts that cost it a probe run: every section on the CI/CD page renders
  **collapsed** (`ProjectSettingsCiCd` passes `defaultExpanded` on none of them), so
  instructions and replays must expand first; and the variables table's Options
  column is a literal empty `<td>`, so the topic plan's suggested `protected` /
  `masked` seeding is neither observable nor writable — rejected.
  Honest novelty note it volunteered: 002/004/005 are all "append a row to a
  populated collection", executing different lines (`:496`/`:520`/`:604`) with
  different guards and collections but genuinely similar agent behaviour — it called
  this the batch's weakest axis and said it would not add a fourth member. Accepted
  as-is; recorded so the ceiling on that shape is known.
- 2026-08-20 — `shopping_admin/order_refund_authorisation`: **10/10 pass the gate**,
  near-dup clean. **The credit-memo unlock worked** — `CreditMemoNewForOrder` goes
  live once `orderOverrides[N].total_paid` is injected, confirmed in chromium
  (`#order_creditmemo` renders, `/admin/sales/order_creditmemo/new/order_id/N/`
  serves the form), not merely in source. Five full replays from fresh sids, every
  task 0.0 -> 1.0, zero flake.
  **Second batch in a row to find the topic plan's line numbers wrong** —
  `CreditMemoNewForOrder` is at `CreditMemoNew.jsx:93-102` not `88-99`, Credit Memo
  action at `OrderView.jsx:320-330`, `Update Qty's` at `:283-287` not `:286`,
  `Refund Offline` at `:438` not `:441`. The prompt template already tells authors
  to verify rather than trust the plan; that instruction is earning its place.
  Two findings the plan did not have, both load-bearing: **all 308 seeded orders
  except 1 and 2 have `qty_invoiced: null` on every line**, and the refund form
  filters items on `num(i.qty_invoiced) > 0 || num(i.qty_refunded) > 0`
  (`CreditMemoNew.jsx:137-138`), so an injected `total_paid` **alone** yields a
  refund form with no line items — every fixture must inject the full `items` array,
  and since `orderOverrides` is a shallow merge, partial item patches are impossible.
  And **every seeded line is `qty_ordered: 1.0`**, which is exactly what makes a
  multi-unit partial refund injection-only rather than a value reshuffle.
  Two process points worth keeping: the browser caught a bug nothing offline saw (a
  line-count assertion matching nested `qty-table` rows, 6 instead of 2), and **an
  adversarial probe forced a rubric change** — the triage task's original "no memo
  for order 11 or 17" was un-loseable through the UI because those orders render no
  button, i.e. a free 0.3; it now scores "exactly one credit memo added anywhere",
  which the probe correctly loses at 0.7.
  Honest weak point it volunteered: `discounted_order_full_refund` is behaviourally
  close to `settled_order_full_refund` (both submit the form unedited), kept only on
  its executed Discount-row branch and a distinct end state — "if a reviewer
  disallows it, this topic's honest yield is 9, not 10". Accepted, and recorded so
  that call stays visible. It also deliberately spent no slot on `adjustment_negative`
  or Append Comments to keep separation from batch 1's `credit_memo_offline_order_002`
  unarguable, which cost it two slots.
- 2026-08-20 — `reddit/cross_list_membership`: **8 delivered, not 10** (6 easy /
  2 medium), all 8 accepted; reddit now 18. **This is the honest short delivery I
  asked for.** The topic plan itself rates this topic at 6+2 and says a seventh easy
  "executes the same lines as the fourth"; the author re-derived the enumeration
  against source, agreed, then **built and measured two padding candidates**
  ("subscribe to a forum I moderate", "hide a forum I'm subscribed to") and dropped
  both with the reason recorded. That is the right way to establish a ceiling —
  measure the candidate, then reject it.
  Two replay passes plus a parity pass, all 8 at 0.00 -> 1.00 with branch claims
  hard-asserted on the control (Hide-vs-Unhide label, Subscribe-vs-Unsubscribe
  label, presence/absence of the moderator Toolbox, 0-vs->0 submissions on
  `/tag/longreads`, and the **403 on `/f/Newark/edit` after the standdown**).
  Adversarial probes 0.00 on six of seven, 0.60 on the seventh.
  **Weak claim, accepted and flagged:** `..._standdown_keep_subscription_005` shares
  `moderatorOf == []` with the sibling `terminal_collection_states_last_moderated_forum_006`.
  The author could not name a differing line inside `remove()` — the novelty is which
  controls render and what the rubric scores, not a branch. It took the lesser of two
  overlaps deliberately (the alternative framing collides harder with batch 2's
  `crosspost_migration_standdown_archive_002`) and said so rather than asserting it
  clean. Accepted for consistency with the reddit-002 call, and recorded as among the
  thinnest claims in the corpus.
  Two corrections worth propagating: the plan's `AppContext.jsx:583-585` for
  `renameForum`'s list maps is **off by one** (it is `:584-586`; `:583` is the
  `forumRenames` append) — the third plan-line-number error found by an author, so
  the "verify, don't trust the plan" instruction is now clearly load-bearing. And a
  new replay hazard: the "Hide this forum" `<details>` is collapsed, so
  `inner_text()` on its submit button returns `""` and a label assertion silently
  passes vacuously — use `text_content()`. A cold browser context also renders an
  empty SPA shell for a beat, quietly emptying every table locator.
- 2026-08-20 — `shopping/dangling_default_pointers`: **7 delivered, not 10** (5 easy
  / 2 medium), all 7 accepted; shopping now 17. Second honest short delivery. Its
  supply argument: the topic reads exactly two state fields, a whole-tree grep finds
  **four read sites and one writer**, and it identified five materially distinct easy
  cells plus two medium compositions and shipped all seven. 14/14 replays at 1.0, no
  flakes, with branch claims hard-asserted (`a.action.delete` count == 1 where a
  Delete link should exist; `#primary_billing`/`#primary_shipping` count == 0 on the
  `isOnly` edit form and == 1 on the Add-New form; `.shipping-address-item.selected-item`
  count 0 -> 1). Adversarial: place-order-without-selecting 0.0, tick-both 0.0,
  edit-the-orphan-in-place 0.0, and both-roles-on-one-record **0.35** — correct
  partial credit, since it did fill the billing slot.
  Every line reference in this topic's plan section checked out — the first section
  with no plan errors.

### Refinement to my own duplicate test, adopted from this author

I have been applying "does a different line of code actually execute?" as the
operative test. This author showed it is **necessary but not sufficient**, and was
stricter than my rule required: it rejected the billing/shipping *mirrors* of two of
its own tasks even though they demonstrably execute different lines
(`AppContext.jsx:477-480` vs `:472-476`), on the grounds that "the agent's route,
controls and reasoning are identical, which is the field value changing — test 2
names it explicitly."

That is right, and it is a better rule than mine. The test is now **both halves**:
a different line must execute *and* the agent's work must differ. `scripts/_b3_prompt.py`
has been updated so every remaining batch is briefed on it, citing this example.
Note this would not have changed any earlier call — the wildcard rejection fails the
first half, and the accepted out-of-stock and terminal-collection tasks pass both.
  Its one flagged weak claim, `..._promote_entry_into_empty_shipping_slot_003`,
  is accepted: the slot being filled is **empty**, so `saveAddress` demotes no
  visible incumbent, `AddressEditPage.jsx:14`'s `isOnly` is false where a sibling
  task makes it true, and the scored end state deliberately leaves the billing
  pointer dangling — an end state no prior task reaches. It clears test 2 on the
  branch-set reading, and the author said so rather than claiming more.
- 2026-08-20 — `gitlab/settings_webhooks_monitor_packages`: **10/10 accepted**
  (8 easy / 2 medium); gitlab now 40. 20/20 replays clean across two passes, each
  hard-asserting its branch claim (DOM count 0 before Expand and 1 after for each
  collapsed section; the five integration checkboxes *checked* where the pristine
  seed renders them unchecked; the hooks empty-state text absent on a populated list
  and present after the last delete; `#error_tracking_project` `disabled`). Both
  derived targets asserted rather than assumed. 13 adversarial probes: no-op Save
  after expanding Metrics **0.00**, wrong integration retired **0.00**, delete-only
  0.30, wrong hook deleted 0.40.
  **It caught and fixed its own duplicate before shipping**: its first task 010
  combined "deactivate PagerDuty" with "clear Grafana", which its own near-dup scan
  flagged at 0.51 against its task 004, and reading the pair confirmed 004's criteria
  would have been a strict subset. Redesigned as a derived-target task that leaves
  PagerDuty alone.
  Flagged weak claim, accepted: 001 vs 003 both delete webhooks through the same
  `:1165` handler, separated only by 003 having to reach the `hooks.length === 0`
  empty-state render at `:1151-1152` that 001 must never reach — the same ground as
  the `settings_deploy_credentials` 001/008 pair, and the probes confirm mutual
  exclusivity (each scores 0.00 solved the other's way). Its own GENERATION.md §7
  says a strict reading of test 2 could still reject 003.
  **The `ui.projectSettings` vein is now confirmed narrowing by its fourth miner**:
  five write paths on this surface, one shared by four forms; eight clean easies
  existed only because those four forms are different controls in different
  directions. It honoured the append warning with exactly one pure-append easy,
  carried by three controls no prior bundle in the vein writes.
- 2026-08-20 — `shopping_admin/order_partial_fulfilment`: **10/10 accepted**
  (8 easy / 2 medium); admin now 20. Three full replay runs from fresh sids, no
  flake, every flow hard-asserting which page action renders and what the form
  prefills. Ten adversarial probes all < 1.0 with both rewards agreeing to 1e-9.
  **Second probe-forced rubric change in this site's batches**: `settled_order_awaiting_dispatch`
  originally scored "order is still Complete", which the probe showed is un-loseable
  through the UI (a Complete order renders no Edit, Cancel, Hold or Invoice, and
  `ShipmentSave`'s ternary cannot move the state), so any shipment bought a free 0.3.
  Replaced with a component the probe can lose.
  Source corrections, one of which **corrects a sibling batch**:
  * `fullyInvoiced`/`fullyShipped` walk **all** item rows including dummy
    configurable children (`InvoiceNew.jsx:377` vs `visibleItems` at `:312`), so on
    any order with a configurable line, billing everything still lands on
    `processing`. Only **19 of 308** seeded orders are dummy-free; every task
    asserting a state arm is built on one of those.
  * `Email Copy of Invoice` / `Email Copy of Shipment` are **inert** — `send_email`
    is put in the payload (`InvoiceNew.jsx:89`, `ShipmentNew.jsx:102`) and never read
    by either save handler.
  * The sibling's "every seeded line is `qty_ordered: 1.0`" is **slightly wrong**:
    6 of 1630 lines are 2.0 (4 visible). Cross-checking between batches is working.
  * Injecting `total_paid` *or* `total_refunded` alone flips `canCreditMemo` true and
    grows an unwanted Credit Memo action — relevant to every future order fixture.
  Flagged weak claim, accepted: `discounted_remainder_invoice` has the same agent
  behaviour as its easy 1 ("submit as prefilled"), differentiated by discount
  proration rather than a guard; its scored value (grand 149.60 vs the naive 182.00)
  does discriminate. Its own note says the honest yield is 9 if a reviewer disallows it.
- 2026-08-20 — `reddit/tree_shape_deletes`: **5 delivered, not 10** (3 easy /
  2 medium), all 5 accepted; reddit now 23. The most rigorous ceiling argument of the
  batch so far: it verified in source that `deleteComment` has exactly **two**
  branches and that the render/walk divergence runs in **one direction only** — a
  node can look childless and still take the soft branch (trashed child), but the
  mirror is impossible, because every rendered child comes out of `commentsFor` and
  anything `hasChildComments` skips is already gone from `materialize()`.
  It then **built two padding candidates and drove them in chromium before dropping
  them**, with measured end states: the hard-deleted-only-child shape produced
  `deletedComments ['2999301','294809']`, `commentEdits {}`, count 34->33 — shape-
  identical to a batch-1 task, "differing line leaves no trace"; and the plan's own
  easy #2 produced exactly the lines a batch-1 task already ran. Also rejected
  delete-thread on a leaf-looking node because its end state is *identical* to
  `/delete` — unscoreable, not merely duplicate.
  8 adversarial probes in parity between both rewards, including upvote-only (which
  *does* write `commentEdits`) scoring 0.00 — a direct check that the rubric is not
  gated on "was edited".
  **Weak claim, accepted and flagged as among the corpus's thinnest:**
  `..._phantom_reply_tombstone_001` is clean against batch-1 `delete_own_leaf_004`
  (identical rendering, opposite branch) but against batch-1 `soft_delete_reply_005`
  the **line-level half does not hold** — the same soft branch runs and the author
  could not name a differing line. What differs is the rendered start state (the
  subtree is absent from the DOM rather than a live `article.comment`), the agent's
  expectation, and the scored survivor. It survives on the 004 comparison; both
  readings are on the record. Accepted for consistency with earlier marginal calls.
  Running list of the three thinnest accepted claims, in case a reviewer wants to
  trim: `reddit_tree_shape_deletes_phantom_reply_tombstone_001`,
  `reddit_cross_list_membership_standdown_keep_subscription_005`, and
  `gitlab_settings_webhooks_monitor_packages_*_003` (the delete-to-empty-state twin).
  Secondary flag it volunteered: its tasks 002/003/005 all rest on
  `AppContext.jsx:518`, differing in guard position, render and scored value — "three
  tasks on one guard and I would not push it to four".
  Plan line number corrected: `collectThread` is `DeleteCommentPage.jsx:79-88`.
- 2026-08-20 — `gitlab/settings_merge_policy_and_mirrors`: **7 delivered, not 10**
  (5 easy / 2 medium), all accepted; gitlab now 47. **The `ui.projectSettings` vein
  is now formally spent** after five batches. Its argument: the surface has four
  write paths, and the main one (`ProjectSettingsMisc.jsx:129`) is a **single
  monolithic form** — one Save writes all eleven merge fields through one line, so
  splitting the merge page by field produces **zero** differing lines, which is
  exactly the failure mode the wildcard rejection named. Getting to 10 would have
  required three field-value variants of bundles already in the batch.
  It also declined to ship remove-all-mirrors-to-empty-state specifically because it
  would have been the **third** delete-vs-delete-to-empty-state instance, after I
  flagged the first two as weak. The feedback loop through the prompts is working.
  **Catch worth generalising:** `relax_squash_and_retemplate_006` initially scored
  **0.15 on its own untouched injected state**, because its gate was "the merge
  record exists" and the record is injected. Fixed to gate on "at least one requested
  change is recorded". This is a new failure mode specific to batch 3 — *injected
  state can partially satisfy a component before the agent acts* — and it is caught
  only by running the reward against your own setup output, which the workflow
  already requires. Worth watching for in every remaining precondition-heavy batch.
  One of my own prompt facts was wrong and is corrected: `ProjectSettingsMisc.jsx:122`
  passes `defaultExpanded`, so `/-/settings/merge_requests` renders **open** — only
  the `/-/settings/repository` sections are collapsed. I had generalised the CI
  sibling's finding too broadly.
  Flagged weakest: `stop_counting_skipped_pipelines_002` shares the merge form and
  the `:129` write line with two siblings; its defence is that `DEFAULT_MERGE` has
  all three merge checks `false` so the *untick* direction is unreachable on the seed
  — the mirror image of the argument used to reject turning force-push ON. Accepted;
  it is the one bundle in the batch whose argument rests on control class rather than
  a distinct handler.
- 2026-08-20 — `shopping/last_row_removal`: **6 delivered, not 10** (4 easy /
  2 medium), all accepted; shopping now 23. Ceiling argued from a closed
  enumeration: nine reachable (collection x control) removal cells exist, and
  `clearCart` is dead code with no call site.
  **It drew the sharpest line yet on the two-halves test, and in doing so validated
  an earlier call of mine.** It rejected the plan's `orders: []` easy and explained
  why it is *not* the same call as reddit's `terminal_collection_states` weakest
  task, which I accepted: there the empty state is what the agent **produces**, and
  `Placeholder.jsx:209`'s `NoEntries` fires as the direct consequence of the scored
  mutation; with `orders: []` the empty-history branches are real but are **scenery
  the agent never touches** — the differing line executes and the agent's work does
  not. That is the two-halves test applied better than I applied it, and it
  independently supports the reddit acceptance.
  It also rejected the sidebar-x and Clear All mirrors of its own tasks on a ground
  worth recording: the differing line executes, but **the reward cannot distinguish
  them**, so they would be two identical training samples. And it killed
  `moveToWishlist`'s never-executed `already === true` arm on **verifiability**
  rather than duplication — its end state is byte-identical to plain
  `removeCartItem`.
  **New replay hazard, now in the prompt template for every remaining batch:**
  `wait_until="networkidle"` is not sufficient. `AppProvider`'s boot awaits
  `fetchServerState(sid)` and the deferred `productOptions` chunk
  (`AppContext.jsx:114`) *after* the page reports idle, so a click fired at idle can
  land before the app has state — one failing run posted a single `set_current` and
  no mutation at all. Fixed with a settle delay plus `wait_for_selector`. This was a
  **driver** defect, not a task defect, and the author diagnosed it as such rather
  than loosening a reward.
  Flagged weakest: `saved_row_merged_into_cart_004` survives only because it executes
  `addToCart`'s **merge** arm (`AppContext.jsx:261-262`) rather than the push arm
  (`:264-272`). It also notes honestly that an agent adding 2 from the PDP reaches
  the same end state and correctly scores 1.0 — a goal-state rubric, stated as such
  in the instruction. And that its task 003 cannot enforce its named control, since
  from a one-entry compare list `Clear All` and `Remove Product` reach byte-identical
  end states — which is why the Clear All variant was rejected rather than shipped.
- 2026-08-20 — `shopping_admin/order_frozen_states`: **3 delivered, not 10**
  (2 easy / 1 medium), all accepted; admin now 23. Three replay passes, every flow
  hard-asserting its branch claim — the `payment_review` order's action bar is
  *exactly* `["back","guest_to_customer","send_notification"]` with each of the eight
  short-circuited button ids asserted absent from the DOM. Six adversarial probes,
  every component losable.

### The structural finding of this batch, and it revises the batch-3 thesis

Its explanation for 3-not-10 is the most important thing any author has said in this
run: **"the precondition axis here is rich; the *mutation* axis is nearly empty."**
A frozen order permits six writes and batch 1 owns five of them — Hold, Cancel, order
comment, Send Email (`fulfill_order_065` step 3) and the comment-form Status change.
Only Unhold, from cold and via the grid's dead `massUnhold`, is free.

That is the correction to the injected-precondition thesis I adopted from the user:
**injection multiplies supply only where there is an unspent mutation to pair a
precondition with.** Where 400 prior tasks have already claimed every write on a
surface, no amount of precondition variety creates a task that passes the second half
of the duplicate test. It explains the shape of this whole batch — gitlab and admin
undershooting on their most-mined surfaces while fresh surfaces still yield 10.

  Two designs changed by the audit **before** the rubric was frozen, both the
  free-credit trap the sibling batches found: "no other order changed" was
  un-loseable because a held order renders no control that can touch a neighbour;
  and a sixth injected `payment_review` decoy as the untouched arm was un-loseable
  because `massUnhold` silently filters it out (`OrdersGrid.jsx:186`). Both fixed.
  Flagged weakest: `payment_review_fraud_flag` writes the comment-form Status
  (`OrderView.jsx:417-424`), a line two batch-1 tasks already execute. What differs
  is that the option exists because of the injected state rather than agent action,
  `fraud` is choosable on 2 of 308 seeded orders, and the submit runs the
  empty-comment arm of `:401` — "a different *operand* on the same line, not a
  different line". Accepted; honest yield is 3 with it, 2 without.
  Rejections worth keeping: the "Send Email is the only surviving action on a
  `payment_review` order" easy was dropped despite being a perfect story, because the
  agent's route, control and reasoning are identical to `fulfill_order_065`'s email
  step — the same standard the refund sibling used to reject memo-email.
- 2026-08-20 — `reddit/admin_forum_teardown`: **5 delivered, not 10** (3 easy /
  2 medium), all accepted; reddit now 28. **It did the reachability check first, as
  instructed, and the unlock is real**: on a clean sid `/f/monitor/delete` renders
  403; with `currentUser.admin` injected it renders the full `confirm_deletion` form;
  submitting gives `deletedForums: [] -> ["monitor"]` and `forums` 95 -> 94. So the
  left disjunct of `ForumDeletePage.jsx:32` is genuinely dead without the injection
  and genuinely live with it — the planner's unverified claim discharged in a browser.
  Same structural cap as the frozen-orders batch: `admin` gates only four sites in
  the whole mock and only one of them mutates, so every task here is `deleteForum`,
  a handler with **no conditionals at all**. It measured the padding candidates
  rather than arguing: subscription-only, hidden-only and moderator-only teardowns
  produce three isomorphic diffs, so it folded two plan easies into one maximal
  triple-list task instead of shipping three samples of one episode.
  Plan corrections: `AppContext.jsx:600-602` is off by one (`:600` is the
  `deletedForums` push; the collateral filters are `:601`/`:602`/`:603`), and it
  retracts the plan's suggestion that a featured forum can serve as a lookup surface
  — nothing in the mock enumerates featured *forums*.
  Flagged weakest: `..._own_posts_ride_down_003` shares handler, route and all three
  form controls with its task 001; what differs is the executing merge path
  (`overlay.js:114` on `created` rather than `base` rows), the scored key set, and a
  wrong-route trap the reward charges 0.4 for. Accepted as the thinnest of its five.
- 2026-08-20 — `gitlab/member_role_boundaries`: **5 delivered, not 10** (3 easy /
  2 medium), all accepted; gitlab now 52. Two replay passes, 10/10 clean, branch
  claims hard-asserted (`aria-colcount` 8, per-row dropdown presence, `disabled` on
  the expiry input, and the exact role-menu list `['Guest','Reporter','Developer','Maintainer']`
  with Owner absent under the clamp). **Untouched injected state scored exactly 0.0
  on all five**, with the neighbour-untouched components deliberately credited only
  when the primary gate holds — the precondition failure mode explicitly guarded.
  It **rejected demotion-as-novelty even though the topic plan endorses it**, because
  `changeRole` (`MembersTable.jsx:217-219`) is one unconditional line in both
  directions, so no line differs. Also rejected assignee-picker gating after finding
  `Controls.jsx:47-62` only *orders* members and gates nothing.

### A correction to my own brief: "known-unsupported" was too absolute

Its task 003 knowingly reopens a batch-1 rejection that my brief repeated as
settled — **"Remove a group share"**. The author checked the recorded reason
(`groupLinks` is created on first use, so the tab renders only once a share exists),
saw that injection removes that obstacle entirely, drove the handler, and shipped it,
flagging the conflict rather than hiding it.

That is correct, and it is the second batch-3 reversal of a "known-unsupported"
finding — the first being reddit's "no second moderator row to protect". Both were
true under a no-injection assumption and false under batch 3's. `AUTHOR_BRIEF.md` now
splits that list: **if an entry's recorded reason is "the state never exists", treat
it as open and check it; if the reason is a missing control or a file upload, it stays
closed.** Remaining batches get the corrected list.
  Flagged weakest: `offboard_a11y_maintainer_001` shares its route and first click
  with batch-1 `people_groups_prune_and_depart_006`. The differing line is real —
  `MembersTable.jsx:224-229`, the two `updateIn` cascades, which 006's instruction
  explicitly disables — and the cascade rewrites 7 issuables carrying 55% of the
  reward. Accepted, but a strict reading of test 2 on "remove a member" could fairly
  call it near-duplicate.
- 2026-08-20 — `shopping/injected_order_records`: 3 delivered, **2 accepted**
  (0 easy / 2 medium); shopping now 25. Every replay re-runs the reward *before* the
  browser touches anything and reads 0.0 per component — the strongest guard yet
  against a fixture satisfying its own rubric, and appropriate for the batch that
  injects a whole `orders` array.
  **001 rejected.** The author put the call to me explicitly rather than deciding for
  itself: "If you hold that a newly-scoreable constraint is not 'different work', 001
  fails the second half of the operative test." I do hold that. Its argument is that
  zero of 100 seeded order lines disagree with `products.json` and zero of 22,721
  products carry a `specialPrice`, so on the seed a `reorder` line
  (`AppContext.jsx:628-630`) and an `addToCart` line (`:267-269`) are byte-identical
  apart from `itemId`/`qty` — meaning prior reorder tasks *asked* for "not from the
  product pages" and could not check it, while a drifted injected line makes the
  route scoreable for the first time. That is a real improvement, but it improves the
  **reward's discrimination**, not the agent's work: the motion is one click on
  Reorder, exactly as in the prior reorder cluster. A newly-scoreable constraint does
  not make the task new. **Replacements/rejections so far: 2.**
  002 and 003 accepted without reservation: `SidebarBlocks.jsx:133`'s `slice(0,5)` is
  dead on the seed (largest seeded order is exactly 5 lines) and forces a route the
  block cannot offer; 003 inverts it with a genuine lookup, and order lines render as
  `<strong>` rather than links so the SKU must come from the grid.
  It declined the unknown-`productId` reorder arm — the sharpest never-executed line
  in the handler — because topic 10 `drifted_cart_lines` claims it, and rejected the
  three Reorder call sites as three tasks since their end states are byte-identical
  (one training sample). It also swapped a product late because the original entity
  combination sat too close to benchmark row `webarena-440`.
- 2026-08-20 — `reddit/co_moderator_standdown`: **3 delivered, not 10** (2 easy /
  1 medium), all accepted; reddit now 31. Reachability discharged live first, as
  instructed, and the unlock holds: an injected `forums[].moderators` renders the
  populated `Username / Since / Last seen` table with exactly one Remove button (the
  self row), `/f/space/add_moderator` still 403s, and clicking Remove writes
  `["forums","moderatorOf"]`, leaves the co-mods byte-identical with their injected
  `since` values, and flips `/f/space/edit` to 403. Probe scripts kept in the batch dir.
  Cap explained from source: `ForumModeratorsPage.jsx` contains **exactly one
  mutation** (`remove(username)` at `:67-73`), there is no Add form past the `:53`
  admin guard, and `App.jsx:128-130` registers no `remove_moderator` route — and that
  single write is **already owned five times** across prior batches. This is the
  mutation-axis cap again, now measured precisely.
  Flagged weakest: `..._second_page_seat_002` shares its primary mutation with 001 and
  differs by a pager boundary (`MODS_PER_PAGE = 25`) rather than a handler. It clears
  the operative test — the Remove control is genuinely absent from the page the task
  starts on, so the agent's navigation differs — but it sits closest to test 2's line
  of the three. Accepted; named as the first to cut if this batch is trimmed.
- 2026-08-20 — `reddit/authored_history_ownership`: **1 delivered, not 7**; accepted;
  reddit now 32. It did the ownership enumeration I asked for and the answer capped it
  hard: the eight writers reachable through an `isOwn` guard (`editSubmission` x3 arms,
  `deleteSubmission`, `editComment`, `deleteComment` x2 arms, `renameUser`) are **all
  already owned, several two or three times over**, and the batch-3 sibling
  `tree_shape_deletes` landed both `deleteComment` arms *while it was designing*,
  killing three of the plan's five easy slots outright.
  **It also refuted the topic plan's central justification with measurements.** The
  plan claims a `userRenames` injection is required because "every prior target had
  zero comments". Measured off the seed: the current user already owns **46 seeded
  submissions** (27 zero-comment) and 9 comments, with two posts carrying ~100 real
  comments each — so `overlay.js:140`'s cascade branch is reachable pristine with no
  injection at all, and batch 1 simply chose zero-comment targets. That makes the
  plan's easy tasks reward-side novelty only: a different line runs, but the agent
  opens the same post and clicks the same Delete. It dropped four of them rather than
  ship the shopping-mirror shape.
  New setup mechanic worth propagating: a `set` POST is stored **verbatim**, so
  `current_state` right after setup contains only the keys posted — `currentUser` is
  absent until the browser writes. Its first setup asserted on
  `current_state["currentUser"]` and failed; the reward now treats a missing
  `currentUser` as the un-renamed baseline.
  **Accepted with a flagged caveat about fixture-only preconditions.** Its precondition
  (a `userRenames` entry whose `from` is the current user, with `currentUser` *not*
  following) is a pairing the mock cannot produce unaided, because
  `AccountPage.jsx:57-58` always renames both together. I am accepting it: the
  rendered world is self-consistent (both handles resolve, the directory is re-keyed,
  every reader copes), the replay drives it, and the scenario reads naturally as a
  migrated handle. But the general principle now on the record is that a
  **fixture-only precondition is acceptable only when the rendered world is
  self-consistent**, and it must be flagged as such — an agent should not be trained
  against a world the app could never reach. The author noted the *acquired* direction
  is equally unproducible, so this limits the whole topic, not just its framing.
- 2026-08-20 — `gitlab/project_flag_reversals`: **5 delivered, not 10** (3 easy /
  2 medium), all accepted; gitlab now 57. 10/10 replays clean, branch claims
  hard-asserted (`archive_project_link` inner text exactly `Unarchive project`;
  exactly one `toggle-label` unchecked; `issues_access_level` reporting `"10"`; the
  archived projects absent from `/dashboard/projects` and present under
  `?archived=only`). Bare-Save probes score 0.0 everywhere — the unconditional
  `topics: []` / `feature_settings` writes buy nothing.
  **The fixture-leak guard earned its place here.** Scored independently, its
  `retired_project_preserved` and `scope_respected` components leaked **0.1 and 0.2**
  from the setup itself; both were made conjunctive with the restores so every
  component reads 0.0 on the untouched fixture. This is the third batch to hit that
  failure mode and the first to quantify it.
  Count argued from a full enumeration of the eight writers to a `state.projects`
  record: six are owned end-to-end by prior tasks, and `feature_settings` yields two
  slices rather than four because visibility, request-access and features all leave
  through the same `patchProject` line on the same Save button.
  **A mock defect found, and correctly treated as unauthorable rather than worked
  around:** "Re-enable Request Access" cannot be written as a task because
  `ProjectSettingsGeneral.jsx:78` initialises `requestAccess` to `true` and the
  `useEffect` at `:99-112` never syncs it from the project — with
  `request_access_enabled: false` injected the checkbox still renders **ticked** and
  `saveVisibility` writes `true` unconditionally. The control actively misreports
  state. Also confirmed `forked_from` has **no reversal control** anywhere in the
  tree, so it stays closed under the missing-control rule and was used as a
  precondition only.
  Flagged weakest: 002 ticks a feature toggle on, the mirror of a batch-1 task
  turning one off, and `setFeature` is one unconditional line in both directions —
  the same shape as the rejected `changeRole` demotion. Kept because the unchecked
  toggle is a render no seed produces and the agent must locate a disabled feature,
  but it is the closest call in the batch.
- 2026-08-20 — `shopping_admin/review_editorial_desk`: **4 delivered, not 10**
  (3 easy / 1 medium), all accepted; admin now 27. It enumerated the surface's
  **eight writers and found six already owned**, then showed the remaining two plus
  one branch of a third yield exactly four tasks — W4/W5 being unconditional
  statements where filtering on a different status is "a different operand on the
  same line". Every scored component is losable through the UI (eight probes,
  0.0-0.7), and probe A1 confirms `ReviewEdit.save()` writes unconditionally, so the
  rubric gates on values rather than on "was edited".
  **It refuted another load-bearing plan fact by measuring the seed**: the plan
  promised an easy on "a seeded three-rating review", but **no seeded review has
  three ratings** — all 351 rows carry exactly one, `rating_id 4`. The
  multi-criterion form became injection-only instead. Line refs corrected too
  (`ReviewEdit` is `:209-421`, `save()` `:250-267`, `NewReview.save()` `:520-559`).
  That is the third topic plan whose central premise an author has overturned with
  measurement rather than accepting.
  It also ran an **independent reward audit**, which found no determinism or parity
  defect but flagged one leniency it then closed: the repost component now also
  requires the corpus to hold exactly 352 rows, after which the gate, replay and all
  probes were re-run.
  Flagged weakest: `rejected_review_purge`'s reward **physically cannot distinguish**
  the edit-page Delete from a single-row grid mass Delete, so the "different call
  site" half of its claim is unobservable in the end state. Accepted on the other
  half: the seed has zero `status_id 3` rows so the filter branch is injection-only,
  and a second rejected review must survive — which makes the prior task's
  filter-and-mass-delete approach score 0.0. A real but thin pass, and named as such.
- 2026-08-20 — `reddit/overlay_provenance`: **1 delivered, not 6** (0 easy /
  1 medium), accepted; reddit now 33. It parsed **every `json.loads` fixture in all
  133 prior reddit setups** and found 14 bundles already inject non-empty
  `newSubmissions`/`newComments` — refuting the plan's §3.8 premise that prior
  overlay mutations only ever act on records created in the same episode, and
  showing all four proposed easy cells are already owned. Of the 14 writer cells, ten
  are owned and three more fail the second half of the test because **overlay
  provenance is invisible in the DOM** — same route, control and reasoning as their
  frozen twins, differing only in which dict key receives the write. That is the
  shopping mirror precedent applied exactly.
  The one real cell is a genuine find: `removeSubmission`'s created-record arm never
  appends to `deletedSubmissions`, so `materialize()`'s `nothingRemoved` stays true
  and `mergeComments` **skips its orphan prune** — deleting an overlay post strands
  its comments, and because `UserCommentRow.jsx` renders `<CommentNav>` only inside
  `{submission && ...}` while `DeleteCommentPage.jsx` 404s on a null submission, they
  become **permanently undeletable**. Its trap run proves it: deleting the post first
  scores 0.5 and is unrecoverable.
  Flagged honestly: its individual mutations are all spent, and the novelty rests on
  the composition plus the ordering constraint. Its own words — if an auditor treats
  any composition of two spent mutations as a subset, "this task falls and the honest
  yield for `overlay_provenance` is zero". Accepted because the branch difference is
  agent-visible and changes the required order.

### Difficulty-mix steer at 162 on disk

Global mix is **73% easy / 27% medium** against the 80/20 target, because the
short-delivering topics have skewed medium (a medium composition often survives the
duplicate tests where its component easies do not). Reddit's three remaining topics
are rated 0/3/3 easy respectively, so running them would push the mix further off.
Remaining gitlab, shopping and shopping_admin batches will therefore be commissioned
**easy-heavy (9:1 or 10:0)** where their surface allows, and reddit's medium-only
topics are deprioritised rather than cut.
- 2026-08-20 — `shopping/blocked_form_recovery`: **10/10 accepted** (8 easy /
  2 medium) — the first full batch since the early waves; shopping now 35.
  20/20 replays at exactly 1.0 with full per-component payout, each hard-asserting
  its refusal string and its start-state claim. Every reward scored against its own
  setup output at **0.0 total and 0.0 per component** — no leaks.
  **It verified the plan's load-bearing claim and found it understated**: the plan
  said "eight guards in six files"; grepping every validation string in `src/**/*.jsx`
  found **13 refusal arms across 8 files**. It used ten distinct guards and
  deliberately left three unused rather than padding.
  **A real reward bug caught only by the replay**: its first cut of 001 scored 0.0 on
  a *correct* run, because `applyUpdates` walks `cart.items` in array order and
  `updateCartQty` (`AppContext.jsx:283-292`) **re-filters the whole cart on every
  call**, so an earlier row's update silently deleted the injected zero-qty row
  before its own repair landed. Fixed by ordering the invalid row first — and
  applying the same ordering to 002 turned the liability into the mechanism that
  makes its reward discriminate Remove-item from fill-in-a-number.
  **It applied my earlier rejection precedent to its own candidates**, unprompted:
  it dropped the `AccountEditPage.jsx:42` password-confirmation guard because the
  password is never persisted, so the guard would only become newly *detectable*
  without changing the agent's motion — and killed the review-rating guard on the
  same ground (different error, identical fill-four-fields-and-submit motion).
  Honest scoping note worth keeping: the refusal is **state-guaranteed in 7 of 10**,
  not all ten; in three tasks an unusually careful agent could repair everything
  before its first submit and never see the message, where what is guaranteed is the
  novel start state and the extra repair. Flagged weakest: 010 shares the `:513`
  ceiling *motion* with 003, defended on a derived entity, a second separately-scored
  guard and an exclusion component.
- 2026-08-20 — `gitlab/issue_flag_reversal`: **10/10 accepted** (8 easy / 2 medium);
  gitlab now 67. Replays twice per flow plus a third parity pass, 1.0 every run, each
  hard-asserting its render claim (sidebar reads `Confidential` and the button says
  `Turn off`; `remove due date` present before and absent after; the time-tracking
  pane pre-filled `3d`; `aria-checked="false"`; "4 of 6" -> "3 of 6").
  **The fixture-leak check caught a live 0.3 leak**: 010's `decoys_untouched` ("the
  other two are still locked") is true on the injected start state by construction,
  and was made conjunctive with both target components. Fourth batch to hit this,
  second to quantify it — the per-component check is now clearly load-bearing rather
  than ceremonial.
  It rejected the plan's own headline task ("mark the injected to-do done") after
  finding `todos.json` row 2972 is a **pending Issue to-do on 83756** and that
  batch-2's `theme_regression_chain_009` already drives that exact line on that exact
  issue — reachable pristine *and* prior art.
  Flagged weakest, in its own order: 006 is a direct mirror of a batch-2 task on the
  same control, surviving only because the two directions are genuinely different
  lines (`IssueDetail.jsx:613-616`) and `ui.unsubscribed` is absent from
  `createInitialData()`; 010 leans entirely on the corrected test 3, since its two
  mutations are what 001 and 002 do individually; and 001/002 are at handler level
  "toggle a boolean the other way", kept on the render argument the brief permits
  and asserted in the replay. It also notes 009's injection buys **determinism, not
  reachability** (1,061 seeded issues already carry `- [x]`), with its real novelty
  being that `onTaskToggle` is a handler no prior gitlab task touches.
- 2026-08-20 — `shopping_admin/small_entity_registry`: **10/10 accepted** (8 easy /
  2 medium); admin now 37. 20 replay runs, all `pre = 0.000` **checked per component**
  and `post = 1.000`, with `nemo_reward.py` matching at both ends. 14 adversarial
  probes confirmed every scored component is losable.
  **Two rubric changes came out of the probes rather than the design**: it removed an
  **un-loseable** "the four seeded conditions were not edited" component (no agreement
  edit or delete route exists anywhere in `App.jsx`, so it was 0.15 of free credit),
  and demoted a row-count gate that was zeroing all three components of a medium on a
  double-save, where the probe measured 0.0 against an intended 0.6.
  It verified the plan's retraction by **driving all eight create writers in a live
  browser** and reading the records back out of `/go`, rather than trusting the doc —
  and two adjacent source claims did not survive contact: `SitemapForm`'s generate
  branch (`Tools.jsx:1024`) is unreachable because the form passes no `extraActions`,
  and `EmailTemplateForm`'s "Convert to Plain Text" only flips a local `useState` that
  `onSave` never reads. Neither is scored.
  Its setups also refuse to run if the target collection is already non-empty, so a
  reused lane fails loudly instead of stacking rows — a good defensive habit worth
  copying.
  Flagged weakest: `website_outlet_microsite` sits close to the billing/shipping mirror
  shape — two priors already drive the store-view and store-group arms of the same
  `StoreHierarchyForm`. Judged on the right side because the entity and state key
  differ rather than only field values, and both priors are multi-step retirement
  flows against this standalone create. It also states plainly that its medium's end
  state does **not prove** `#save_and_edit` was used — an agent visiting `/new` twice
  reaches the same three rows and scores 1.0; the novelty is in the required flow, not
  a state trace.
- 2026-08-20 — `gitlab/subscription_and_priority_reversal`: **8 delivered against a
  requested 9:1** (7 easy / 1 medium), all accepted; gitlab now 75. It declined to pad
  to 9 and relabelled nothing. 16/16 replays at 1.0, per-component fixture check at
  0.0 including a medium component made conjunctive specifically so the fixture cannot
  satisfy it.
  **It substantiated the absent-key argument empirically** with a pristine-sid probe
  rather than resting on the source read: 0 remove-priority buttons, 0 priority
  badges, the prioritized empty state present, 0 Unsubscribe buttons (16 read
  Subscribe), "You do not have any subscriptions yet", own-activity unchecked. That is
  the cleanest evidence yet that these renders are unreachable on the seed.
  Rejections worth keeping: the "No other labels..." render executes the *same* append
  line as a batch-1 task and the novel render is one the agent **produces** rather than
  must find (the same distinction that decided an earlier shopping call); MR
  re-subscribe duplicates an already-accepted batch-3 sibling; and the bulk Edit-issues
  Subscriptions select writes `issues[].subscribed`, a genuinely distinct handler at
  `IssuablesList.jsx:657`, but `grep -rn "\.subscribed\b" src/` shows **nothing reads
  it** — so it is not user-visible and cannot be scored.
  Flagged weakest: 006's removal half is the same control and line as 001's, separated
  only by the append scoring 0.0 alone; 004 shares `:180` with 003, separated by the
  terminal empty state and a cross-project exclusion.
- 2026-08-20 — `shopping/prepopulated_review_log`: **3 delivered, not 10** (2 easy /
  1 medium), all accepted; shopping now 38. Replays twice from fresh sids at 1.0 plus
  22 offline adversarial states, 0 failures. It caught a **wrong-target leak in its
  own reward**: its first cut gated `prior_records_untouched` on ">=1 new review
  exists", paying 0.2 to an agent that reviewed the *wrong* row; now gated on
  `review_ok or cart_ok`.
  **It demolished the topic plan's headline claim with measurement, and this is the
  most consequential plan refutation of the run.** The plan said 16,766 products have
  no reviews so the whole first-review cascade is unspent. In fact: two of those carry
  `ratingSummary: 0` so the real figure is 16,764; **89 of them carry seeded review
  bodies or a `reviewCounts.json` entry**, so `tabCount` is already > 0 while the
  summary still reads "Be the first" (clean population 16,677); and decisively,
  **three prior batch-1 tasks already review zero-review products**
  (`pantry_audit_three_008` on 104479/104484, `thawed_delivery_005` on 104489) — so
  the topic's headline easy was spent before the topic was written. It also found the
  plan's "blended average over null-rating bodies" easy does not exist, because
  `ratingPercent()` never reads a seeded body, and that the source docstring at
  `catalog.js:573` is itself stale (claims 18 of 3,080 reviews; the corpus holds
  76,378).
  Structural cause of the cap, cleanly put: **this topic is a precondition over one
  handler.** It grepped every reference to `myReviews`, `nextReviewId`,
  `ratingPercent`, `reviewCount`, `reviewsForProduct`, `seededReviewCount` and
  `reviewRatingPercent` — `submitReview` is the only writer and every other site is a
  render, so no guard changes an *action's* outcome. Its sibling `out_of_stock_pdp`
  reached 10 because it spans seven handlers. That is the mutation-axis rule again,
  now stated as a diagnostic.
  Four of its eight rejections rest on my own precedent (the guard becomes newly
  *detectable* without changing the motion), including the 89 anomalous
  "Be the first" + `Reviews (N)` products.
  Flagged weakest: 001's route (`/review/customer/` row link, a page never rendered in
  400 prior tasks) and end state are new, but the form motion is the same four fields
  and Submit as fourteen prior review tasks. Accepted on the route-plus-end-state
  reading; a maximally strict reviewer would leave this topic at two.
- 2026-08-20 — `gitlab/milestone_date_windows`: **6 delivered against 9:1** (5 easy /
  1 medium), all accepted; gitlab now 81. 12/12 replays at exactly 1.0, per-component
  fixture check 0.0 across all 9 components. Its one true-by-construction component
  (`neighbours_left_clear` — issues #21/#30 already carry no milestone) was made
  conjunctive with both filing components **at design time**, then measured at 0.0 both
  at t=0 and on a reopen-only run. First batch to anticipate the leak rather than
  discover it.
  Strongest finding: the bulk panel at `IssuablesList.jsx:641` is **the only milestone
  picker in the app without the `state !== 'closed'` filter** that `NewIssue.jsx:51`,
  `EditIssue.jsx:47`, `IssueDetail.jsx:100` and `MergeRequestDetail.jsx:178` all carry.
  Its two strongest tasks resolve that asymmetry in mutually exclusive directions, and
  the replay asserts it directly — the issue sidebar dropdown contains **exactly**
  `["No milestone"]` while `#update_milestone_id` does list the closed milestone.
  **New replay hazard, now in the prompt template**: the sticky `header.navbar`
  overlays the issue/MR list row checkboxes — `.check()` times out and
  `.check(force=True)` **silently clicks the navbar**, so the box never toggles and the
  run posts no mutation while appearing to succeed. Focus the input and press Space.
  Its rejections are unusually well-argued — seven candidates dropped, including
  clear-the-due-date (mirror of its own 001), set-a-start-date (a batch-1 task already
  sets a 2035 start date, so the Upcoming box and badge already render), and
  delete-with-nothing-attached as a pair with 002, explicitly because two gitlab
  siblings had already rejected that exact pair shape.
  Flagged weakest, in its order: 005 takes a milestone off a merge request — genuinely
  unexercised (`IssuablesList.jsx:653` remove arm) but close to 003's reasoning; and
  002, where "the differing line carries this task; the differing work does not".
- 2026-08-20 — `gitlab/branch_tag_ref_pruning`: **3 delivered against 9:1** (2 easy /
  1 medium), all accepted; gitlab now 84. Its writer count is the whole story: the
  topic's entire mutation surface is **five call sites** (`NewBranch.jsx:44`,
  `Branches.jsx:165`, `Branches.jsx:245`, `NewTag.jsx:41`, `Tags.jsx:135`), and
  **four of the five are already spent**. It says explicitly that it trusted my
  prompt's two-halves test over the plan's "~8 easy" estimate, which was written
  against the older three-disjunct wording — and logged eleven rejected candidates,
  including two mirrors of its *own* tasks.
  Its pristine-sid probes are the best in the run: pristine `chinese-colors` renders
  four branches and clicking `delete_merged_branches_button` leaves `branchDeletions
  == {}` **and `state_diff == {}`** — a measured no-op, not an inferred one; pristine
  `SynthText` shows 0 delete-tag buttons and "Repository has no tags yet."; pristine
  `eugenp/tutorials` renders only a `Stale branches` card with `/-/branches/active`
  empty, versus three rows with setup applied.
  **Mock defect found, worth inheriting:** `dataManager.js:610-623`'s docstring claims
  the deletion list is cleared on re-create, but no caller does it — `NewBranch`/
  `NewTag` only `pushRepoOverlay`, and `undeleteRef` (`:625`) has **zero callers**. So
  re-creating a ref with a deleted ref's name writes the overlay while the ref stays
  invisible, and the duplicate guard does not fire either. Any future "restore branch
  X" / "recut deleted tag Y" task is unsolvable.
  Flagged weakest: 002's two unlocked lines are real and nameable
  (`dataManager.js:515-517`'s `extra` half of `getCommits`, and `NewTag.jsx:45`'s
  never-executed `|| head.title` operand) and the reward discriminates prior-task
  behaviour at 0.30 — but the agent's work is a prior task's form-fill plus one
  dropdown. Accepted; the author said it would not argue if bounced.
- 2026-08-20 — `shopping_admin/admin_lockout_and_profile`: **6 delivered against 9:1**
  (5 easy / 1 medium), all accepted; admin now 43. Confirms the writer-ownership cap
  again: `lockedAdminUsers` is untouched as a key, but the topic has **eight writers
  and six are already spent**. It rejected four candidates, two of which the plan
  counted toward its "8 easy slots" — including one that is **literally the
  `users_migrated` component of a prior task, down to the same injected multi-user
  fixture**.
  28 hard branch assertions in the replay, all passing on both runs; every scored
  component confirmed losable in both directions, and the medium correctly *loses* a
  half to over-application.
  **Four source claims found false by driving the writers live**, the last of which is
  a setup mechanic every future admin batch needs:
  * `MyAccount`'s "Your Password" is **decorative** — it renders `_required` but
    `save()` never reads `form.current_password`; the account saves with it empty.
  * **No password value is ever persisted** (`Tools.jsx:878-889` writes five fields and
    `modified`), so a password task would be unobservable.
  * The Locked Users grid is a **`LegacyGrid`, not an `AdminGrid`** — its first probe
    found zero checkboxes and no Actions button; the real DOM is
    `#lockedAdminsGrid_massaction-select` / `button[title=Submit]` / `input#id_<value>`.
  * **A partial `set` merges at the top level only** — posting a `systemConfig` object
    replaced it wholesale, 26 sub-keys down to 1. Its setups now read `systemConfig`
    back from `/go` and re-post it with one sub-key changed. This is a live corruption
    hazard for any admin fixture touching a nested config object.
  One constructive find hardened a rubric: `AdminUserForm.save()` re-points the seed's
  `role_id: 3` row (`parent_id` 0->1) while `MyAccount.save()` does not — verified both
  ways — which makes "do it on My Account" objectively checkable rather than a matter
  of trust.
  Flagged weakest: `widen_returns_desk_role_access` passes the different-line half
  comfortably and the different-work half only narrowly, on the absence of a create
  step and the opposite direction of travel.
- 2026-08-20 — `gitlab/file_overlay_restoration`: **9 delivered against 9:1** (8 easy /
  1 medium), all accepted; **gitlab reaches 100** (79 easy / 21 medium). It opened with
  the writer count as instructed — 5 call sites over 3 handlers plus 2 conditional arms
  inside `writeFiles`, so 7 distinct write paths — which is exactly why it reached 9
  where the five-call-site branch/tag topic reached 3. The diagnostic is now predictive
  rather than descriptive.
  18/18 replays at exactly 1.0, every isolation clause that would be true at t=0 made
  conjunctive **at design time** rather than discovered afterwards. Shortcut probe on
  004: delete-then-re-create scores **0.6**, because the tombstone forces the
  `treeAdds` append arm and `repaired_in_place` correctly pays 0.0.
  **Plan correction:** §15 claims a tombstone reaches the `RepoBlob.jsx:64-68` redirect
  with a "did not exist on" flash. **It does not** — `getRepoFile`
  (`dataManager.js:466-479`) returns `null` for a tombstone because the key *is*
  present, so the `body === undefined && !entry` guard is false; the real behaviour is
  the path leaving `getRepoTree` plus the `RepoBlob.jsx:218-222` "too large or is
  binary" arm. Every instruction and assertion was rewritten against the real
  behaviour, and it killed a candidate (a `treeOverlay` entry with no body renders the
  *same* placeholder, so it is not an observably distinct precondition).
  Flagged weakest: 008 shares 001's tombstone-restore family, differing by the licence
  dropdown that only renders once the typed name matches
  `/^licen[cs]e(\.\w+)?$/i` (`FileEditor.jsx:135-136`, asserted absent->present) and by
  the writer's input being a rendered template rather than typed text. It rejected the
  exact mirror (the `.gitignore` template entry) as a test-2 duplicate of itself.

### Running tally at 223 on disk

| site | bundles | easy | medium |
|---|---|---|---|
| gitlab | 100 | 79 | 21 |
| shopping | 47 | 35 | 12 |
| shopping_admin | 43 | 34 | 9 |
| reddit | 33 | 22 | 11 |
| **total** | **223** | **170** | **53** (76% easy) |

The easy-heavy steer is working: the mix has moved from 73% to 76% against the 80%
target, and the remaining commissions stay at 9:1.
- 2026-08-20 — `gitlab/mr_draft_and_merge_gates`: **7 delivered against 9:1** (6 easy /
  1 medium), all accepted; gitlab now 107. **It refined the writer-count diagnostic in
  a way worth keeping**: raw writer count is not the predictor — *unowned* writer count
  is. This surface has **18 distinct mutation call sites**, the widest in the gitlab
  corpus, but 10 of the 100 prior tasks are merge-request tasks and between them own
  15 of the 18; batch-3 siblings then spent the entity-type mirrors of three more while
  it worked. What remained was the reverse directions plus two controls no prior task
  drives at all, and that ceiling is seven.
  Two plan corrections verified against source: the plan asserts `merge_commit_message`
  is untouched by all 100 prior tasks — **it is wrong**, batch-1's
  `merge_token_input_006` replaces one and then merges, so that candidate was rejected.
  And `merge_status` is inert exactly as briefed, which also killed the plan's
  "merge/close an MR the setup left in draft" candidates: `draft` gates neither button,
  so **no differing line executes**.
  Pristine-sid probes again did the load-bearing work — `?draft=yes` on Mario-Level-1
  renders "Sorry, your filter produced no results" pristine against 7 unfiltered rows.
  The navbar hazard was handled as briefed: task 006 focuses each `input[data-id]`,
  presses Space, then asserts `is_checked()`.
  Flagged weakest: 005 performs the same unlock gesture as a batch-3 sibling does on an
  issue. Lines and collection genuinely differ and the precondition is unreachable
  (`discussion_locked` absent from all 23,236 rows), but the agent's route is close —
  and it notes that by the same standard it used to **reject** the awards-increment and
  task-list-checkbox mirrors, this one is borderline. Kept, objection recorded.
  Secondary: its 003 and 004 rest on *seeded* rather than injected preconditions
  (`initial_setup: null`) — still materially different start states, but a property of
  the corpus rather than of its setup.
- 2026-08-20 — `shopping/duplicate_add_merge`: **9 delivered against 9:1** (8 easy /
  1 medium), all accepted; shopping now 56. Its writer analysis explains why it beat
  the 3-of-10 outcome its sibling hit: the surface reaches only 5 of the 20 mutating
  handlers, but **`addToCart` is reached through four different controls passing
  different arguments** (PDP form, `AddToCartButton` hard-coding qty 1,
  `WishlistPage.addRowToCart`, `SidebarBlocks.jsx:166`), so handler x control x arm
  gives 8 live cells rather than 5. Useful refinement: the unit is the *cell*, not the
  handler.
  It checked the plan's "eight distinct available sites" per candidate and found two
  already taken by batch-3 siblings, and a variant it invented impossible — **0 of the
  4,884 seeded option groups are non-required**, so `WishlistPage.jsx:32-36` always
  bounces.
  **It rejected its own designed medium on measured evidence after building and
  driving it**: a duplicated comparison column, where `removeFromCompare`'s productId
  filter wipes both columns in one press. State ends correct, but `ComparePage.jsx:45`
  renders `key={p.id}`, so a duplicated productId gives React two children with the
  same key and the **DOM keeps a stale column** — 3 before, 2 rendered after. The agent
  would read a column that no longer exists. Not shippable; replaced with a wish-list
  twin-row hand-merge, which is why the batch is 8 easy rather than 9.
  **Adjudication of its flagged weakest, `twin_cart_rows_pruned_007`: accepted.** It
  admits **no differing line executes** — its primary mutation is `removeCartItem`,
  same handler as a batch-1 task. It earns the slot on the second half alone: the start
  state (two cart lines sharing a productId *and* an option key) is unreachable through
  any route because of `addToCart`'s merge guard, the two rows render identically, and
  the agent must disambiguate on the qty input name. This is the same shape as reddit's
  accepted `phantom_reply_tombstone_001` (same line, materially different rendered
  start state, different agent work), so accepting it is consistent; it is thin and is
  named as such.
  It also recorded a limitation rather than hiding it: in `move_to_wishlist_already_saved_005`
  the already-arm's effect on that one line is byte-identical to `removeCartItem`, so
  no reward can prove which control was used — a second cart row forces at least one
  genuine `moveToWishlist` call, but the branch claim on the first row is about the
  instructed path, not a provable observation.
- 2026-08-20 — `shopping_admin/widget_and_design_shelf`: **6 delivered against 9:1**
  (5 easy / 1 medium), all accepted; admin now 49. Seven writers on the surface, one
  already spent by a batch-3 sibling, six tasks shipped — a clean one-per-unspent-writer
  result. Everything else on the shelf is read-only or dead (Media Gallery decline-only,
  Themes render `readOnly disabled`, PageBuilder Templates `rows={[]}`, and
  `DesignChangeForm`'s edit/delete branches exist but `App.jsx:425` registers only `/new`).
  **Fifth plan premise falsified by measurement**: the plan's "injected row with no
  `code` falls back to a different grid URL" is false because **all 17 rows in
  `WIDGET_INSTANCES` already carry no `code`**, so every installed widget is already on
  the fallback — that easy slot evaporated. Four line refs corrected, and the Widgets
  grid is a **`LegacyGrid`, not `AdminGrid`** (second time this trap has appeared).
  **New trap not in any doc:** installed widgets store the *human label* in `type`
  (`'CMS Static Block'`), which is not one of the Type select's option **values**
  (FQCNs), so the control cold-renders on option 0 while React state still holds the
  label — an untouched select posts back the label. Every instruction names Type
  explicitly and every reward scores the FQCN.
  My `systemConfig` merge warning reproduced exactly: a bare `systemConfig` post
  collapsed **26 sub-keys to 1** while all 44 top-level keys survived. Its setups read
  it back, re-post it whole, and assert the sub-key count before printing `SETUP OK` —
  a good defensive pattern.
  The `instance_id` collision claim held and is the batch's strongest material: with id
  3 injected, Save left `widgets` at length 1 with corrected values; without it the same
  click appends. `#delete` is absent on an installed widget and present once a state row
  exists, so **on the pristine seed no widget in this app is deletable anywhere**.
  Flagged weakest: T1 rests on "different entity + handler + state key" rather than a
  precondition flipping a guard, and its shape matches seven sibling bundles from
  another topic. Kept because widgets are a genuinely unreached collection and its
  sibling task needs it as an explicit contrast.
- 2026-08-20 — `gitlab/group_namespace_ownership`: **2 delivered against 9:1** (2 easy),
  both accepted; **gitlab COMPLETE at 109 across 15 topics**. Unowned writer count 3 of
  11, and one of those three then failed the second half of the test (its dropdown
  renders in both states, so only *which* item is clicked differs), leaving 2. It
  delivered short rather than shipping members-table role reshuffles.
  **Four plan/brief claims refuted in source**, including two that would have produced
  duplicates: the plan's "a project created inside the group makes the
  `GroupSettings.jsx:69` cascade live for the first time" is false (two seeded projects
  already have group namespaces and a batch-1 task already drove the cascade), and
  "create a subgroup" is unsupported because `NewGroup.jsx` never reads `parent_id` —
  the hidden input at `:230` is inert.
  **Second correction to my own known-unsupported list, and it changes the rule's
  application.** Its task 002 reopens "Invite-a-group", which the brief recorded as
  rejected for a *missing control*. That reason is factually false: the trigger, modal,
  picker, role select, expiry field and `groupLinks` writer all exist and it drove them
  — what is missing pristine is the **permission** to see the button
  (`MembersTable.jsx:183` `canManage` is false on every group). So its true reason is
  "the state never exists", which my own rule classifies as **open**. Accepted, and the
  brief now says: when a recorded reason is itself refuted by source, classify on the
  true reason rather than the written one.
  **Tooling hazard, now in the prompt template:**
  `src/components/create/mutations.js` contains **NUL bytes** (offsets 3445, 7320), so
  plain `grep` treats it as binary and **silently matches nothing**. Several ceiling
  arguments in this run rest on "nothing reads this" greps; any such conclusion needs
  `grep -a` to be trustworthy.
- 2026-08-20 — `gitlab/fork_lineage`: **3 delivered against 9:1** (2 easy / 1 medium),
  all accepted. Note gitlab's true total is **105**, not the 109 I reported a moment
  ago — this batch's three were already on disk and counted when I gated after the
  group-namespace batch. Correcting my own arithmetic: gitlab finishes at **105 across
  15 topics**.
  Its writer count: 11 call sites reached, **10 already owned**; `forked_from` and
  `forks_count` have exactly one writer in the entire tree (`mutations.js:452`) and it
  is spent twice by batch 1. It explicitly matched itself against my calibration
  ("7 paths -> 9 bundles; 5 sites / 4 spent -> 3 bundles"), predicted the deliver-3
  regime, and delivered 3. The diagnostic is now being used predictively by the authors
  themselves.
  **Another plan claim refuted, and this one matters for a surface a sibling already
  shipped:** the cross-cutting table says `request_access_enabled: null x175` makes
  `ProjectOverview.jsx:89` "return null — whole access block". The guard is
  `if (project.request_access_enabled === false) return null`, so `null` falls
  **through** to a live Request Access branch. It does not affect this topic, and it is
  recorded for whoever authors that surface — worth noting the sibling that examined
  the same field independently concluded the control misreports state, which is
  consistent.
  Flagged weakest: 001 and 002 share their mutation verb with two sibling topics. What
  distinguishes them is that the *read* the mutation depends on is served by a
  different project — `getRepoFile`/`getBranches` resolve the base through
  `originChunk`->`originPath` while the writers key on the fork's own `full_path` — and
  the reward scores that split via the upstream-untouched clause. Accepted; a reviewer
  weighting "same control, same page" above "different resolution path" could fairly
  call 001 a near-neighbour. Its 003 is unambiguous: the only task in 400+ bundles to
  render `Forks.jsx:117`, and the only one to fork a fork.
- 2026-08-20 — `shopping/paginated_collections`: **5 delivered against 9:1** (4 easy /
  1 medium), all accepted; shopping now 52. Four live cells from three handlers, one
  supporting a second composition — five tasks. Two cells the plan promised are dead
  (one owned by a batch-3 sibling, one with no differing line).
  **It ran the measured-evidence check on its own load-bearing claim rather than
  trusting source**: the medium turns on the draft-reset at `WishlistPage.jsx:19-23`,
  so a probe typed 5 into a page-1 row, carted a page-2 row, navigated back and read
  the box — it reads `1`, and that ordering scores exactly 0.4 while the correct order
  scores 1.0. It states plainly that had the claim not survived the browser, the medium
  would have gone.
  Its pager assertions are backed by a corpus measurement: the max prior wish list
  across all 447 bundles is **5 rows**, so the wish-list pager has never been drawn
  before.
  Rejections worth keeping: order-history page 5 killed two planned easies because **no
  differing line executes** (`OrderHistoryPage.jsx:19-27` and `:63` are identical at 4
  and 5 pages, and `Toolbar.jsx:238`'s Next already renders on the pristine 37-order
  grid); the dashboard "sixth-newest order" needs no injection at all; and PDP review
  pagination is pristine-reachable because **3,551 of 22,721 products already exceed
  `REVIEWS_PER_PAGE`**.
  **Flagged weakest, accepted for consistency:** `sidebar_block_last_three_004` executes
  a genuinely unowned writer (`SidebarBlocks.jsx:75`, never run in any prior bundle),
  but the persisted end state **cannot distinguish which of the two remove controls was
  clicked** — its novelty rests on an unowned call site plus a truncated block, not on a
  reward-enforceable route. This is the same limitation I accepted in
  `duplicate_add_merge_move_to_wishlist_already_saved_005`, and it is recorded in both
  the batch notes and the bundle's `authoring_notes`.
- 2026-08-20 — `shopping_admin/config_dependency_gates`: **10 delivered** (9 easy /
  1 medium), all accepted; admin now 59. 20/20 replays at 0.0 -> 1.0 with every
  precondition hard-asserted mid-replay. Five falsified premises, two of which are
  substantive:
  * The plan's `catalog/search/opensearch/enable_auth -> 2` gate is **impossible**:
    `FIELD_DEPENDS` (`configSections.js:651-652`) names the master with **slashes**
    while the field's real `configPath()` uses an **underscore**, so the draft lookup
    is permanently undefined — verified live, setting `enable_auth` leaves the
    dependents disabled forever.
  * **`configPath()` violates its own comment**: Start Time saves to `currency_import_time`,
    not `currency/import/time`, because its name ends `[value][]` and `FIELD_NAME_RE`
    requires `[value]`. Its first reward asserted the slash path and a **correct replay
    scored 0.5** — caught by the replay, not by reading. It also found the plan's
    "21 fields under 5 masters" is really 39 under 8.

### The largest quality caveat in the batch-3 corpus, recorded plainly

**Nine of this batch's ten tasks call the same writer, `saveConfig`.** The author
flagged this itself: "a reviewer reading test 2 as 'same handler = same task' would cut
this topic to two or three." Its defence is that each task turns on a different lock
*configuration* — a different master control to find and release first, in a different
section, with different dependents and a different cold-load lock state — so the agent's
navigation and reasoning genuinely differ even though the write line does not. It also
rejected two further candidates (`admin/url`, `admin/grid`) for being identical motions
to one it kept, and dropped a standalone cache-flush easy as a field-value duplicate.

I am **accepting all ten**, because batch 3's corrected test 3 explicitly licenses
novelty from a materially different start state, and nine distinct lock structures are
materially different starts. But this is the single largest concentration of one writer
in the corpus, and if the delivered set is ever trimmed for quality **this topic is the
first place to look** — the author's own ordering is `currency_import_time_window`
first (shares a section *and* field group with a sibling), then the
`search_engine_block_swap` / `layered_nav_manual_to_improved` pair. Recorded here so the
decision stays available rather than buried in a batch note.
- 2026-08-20 — `shopping_admin/customer_account_desk`: **6 delivered against 9:1**
  (5 easy / 1 medium), all accepted; admin now 65. Unowned writer count 7 of 16 (whole
  surface confirmed **with `grep -a`**, per the NUL-byte warning), one of the seven
  rejected as a mirror — the newsletter-tab **create** branch is the same route,
  control, keystroke and reasoning as the **update** branch with only the precondition
  differing. Two more sites are unowned as *controls* but their mutation is owned
  elsewhere, which test 2 kills.
  Two more falsified plan premises: `customers[i].is_active = 0` "unlocks an inactive
  account" is **false** — no reader and no writer exists anywhere in the customer pages
  (`blankForm()` omits it, `save()`'s patch omits it, the grid declares no column, and
  the only occurrence is the literal at creation), so the precondition unlocks nothing;
  and the multi-address `default_billing` bullet is partly false because all 70 seeded
  customers already carry it and the billing summary is render-only with no writer.
  Adjacent finding worth keeping: **all 70 seeded customers are in group 1**, so
  Wholesale and Retailer are *already* deletable pristine — its injection does not make
  `CustomerGroups.jsx:65` reachable, it makes it **guarded**. That is a precise
  distinction and it is why it wrote no separate "delete the unused group" easy.
  It also reported an assert bug as its own rather than the app's:
  `get_by_role("button", name="Delete")` matched the page-header **Delete Customer**
  action until scoped to the variations grid.
  Flagged weakest: `grid_resubscribe_lapsed_record` shares route and control with a
  batch-2 task, executing a different line (`CustomerGrid.jsx:303` vs `:306`) from a
  different start with a different end shape. Kept because the record count is
  **scored**, so the two branches are distinguishable by the reward rather than by
  narration — which is the right test.
- 2026-08-20 — `shopping_admin/promotion_rule_conditions`: **3 delivered against 9:1**
  (2 easy / 1 medium), all accepted; admin now 68. Four strong cells, and it folded two
  of them into one episode because splitting would have produced tasks differing only in
  *which* rule was left inactive. Its verdict on the plan: "the claim of 9 easy slots
  does not survive contact with the source."
  Two more falsified premises: the plan's spent-coupon precondition is unusable because
  **no UI writer exists for a coupon's `usage_limit` or `times_used` anywhere in
  `src/`** (the mint block hardcodes `usage_limit: null`, and the form's Uses per Coupon
  writes to the *rule*); and its expired-rule precondition is already owned by a batch-2
  task that injects End dates on all four cart rules.
  **The orphan detector works end to end, proven adversarially:** delete-and-recreate
  rule 4 returns `nextRuleId` 4, the grid looks identical and every rule-level clause
  passes — but `coupons == []`, so the task scores **0.0**. That is exactly the
  "edited vs deleted-and-recreated" discriminator the plan promised, verified rather
  than asserted. Its decline-branch assertion is equally clean: the notice renders
  **and `state_diff == {}` after the press**, proving the branch writes nothing.
  Flagged weakest: `reissue_missing_coupon_code` overlaps a batch-1 task's lines,
  separating on an injected precondition unreachable from the seed (a Specific Coupon
  rule with an empty `coupons` collection, where the seed holds exactly one coupon row),
  on the guarded controls rendering at load rather than being revealed, and on
  `uses_per_coupon`, which no prior admin task writes. Accepted; the author said it is
  the one bundle whose rejection it would not argue with.
- 2026-08-20 — `shopping/drifted_cart_lines`: 2 delivered against 9:1, **1 accepted**;
  shopping now 53. Unowned writer count 4 of 11 cells, only one an unowned *writing* arm
  whose agent work also differs — the calibration predicted 2 and it delivered 2 rather
  than padding.
  **001 rejected, for consistency with my own earlier call.** It flips a genuinely
  never-executed conditional (`AppContext.jsx:630`'s `product ? finalPrice(product) :
  line.price` false arm, reachable only with an order line whose `productId` is absent
  from the catalogue) and the scored value is producible by that arm and nothing else.
  So it passes the *first* half of the operative test. But **the agent's motion is a
  single Reorder click**, identical to the prior reorder cluster's — it fails the second
  half. This is the arm a sibling deferred to this topic after I rejected its own 001 on
  the same ground; the author said so itself: "taking the deferral inherits the weakness
  rather than curing it." Rejecting it keeps the line I drew earlier intact.
  **Rejections/replacements so far: 3.**
  002 accepted without reservation: it drops a dead cart row before checkout, asserting
  that exactly one of four rows carries the fallback href *and* an SVG placeholder while
  the others carry `.html` hrefs and real media, and that the dead row's Edit href
  renders 404 while a live row's renders a real add-to-cart button. All three components
  are gated on the created order existing, so "the dead row is not on the order" cannot
  pass vacuously.
  It also checked the repeated-key hazard a sibling found, rather than assuming it did
  not apply: `CartPage.jsx:115` keys rows on `item.itemId` and `:154` keys option pairs
  on `optionId-optionTypeId`, its fixtures use distinct values so neither key can
  collide, and the replay asserts both the row count dropping to 3 **and** the rendered
  Order Total — so a stale DOM row would fail the run rather than pass silently.
  **Unused lead worth recording:** `Header.jsx:277`, the mini-cart qty input, is an
  **unowned control** on `updateCartQty` — it writes on every keystroke, has no Update
  button, and clamps to 1, and no prior or sibling shopping task touches the flyout. It
  produces byte-identical state to the cart form so the route cannot be scored, which is
  why it was not used here, but a control-shaped topic could spend it.
- 2026-08-20 — `shopping/account_identity_states`: **2 delivered against 9:1** (1 easy /
  1 medium), both accepted; shopping now 55. Unowned writer count 2 of a 20-cell census,
  with 18 owned or dead — every "nothing reads this" conclusion re-run with `grep -a`.
  **It found the plan's headline easy is literally a prior task**: the plan proposes
  injecting `newsletterSubscribed: true` so the footer goes inert and
  `/newsletter/manage/` becomes the only route, but batch-1's
  `account_addresses_newsletter_optout_002/initial_setup.py:24` **already injects
  exactly that**, and that bundle's own notes say "an opt-out, which the footer
  Subscribe box cannot produce". Both arms of the boolean are spent.
  **It applied the mirror precedent to itself, unprompted**, rejecting the plan's fourth
  easy because the same false arm of the same ternary executes pristine and injected —
  only the copied value differs — and rejecting the `AddressEditPage` twin of its own
  task 002 for identical agent reasoning. It also declined to poach a guard belonging to
  a sibling's topic.
  **Adjudication of its flagged 001: accepted.** It is the same control and form as a
  batch-1 task, differing by arm — the box boots checked instead of unchecked and the
  write inverts. That is the "toggle a boolean the other way" shape two gitlab siblings
  rejected, but with the qualifier those siblings themselves used: the *start render* is
  unreachable on the seed, so the agent must untick where every prior task ticks. Same
  ground as reddit's accepted terminal-collection and phantom-reply calls, so accepting
  is consistent. Recorded as thin.
  Its 002 carries a 0.7 negative control (contact-first ordering) demonstrating the
  reward discriminates the ordering dependency, which does not exist pristine.
- 2026-08-20 — `shopping/empty_address_book`: **4 delivered against 8:2** (3 easy /
  1 medium), all accepted. **shopping COMPLETE at 59 across 11 topics.**
  Its census is exact: with `addresses: []` exactly two mutating handlers are reachable,
  `deleteAddress` is **structurally unreachable** (the Delete link lives only in the
  additional-entries table, which does not render on an empty book), and of the five
  resulting cells two are already owned — one by a batch-3 sibling, one by a batch-1
  task plus another batch-3 sibling. It re-read the running list **before designing and
  again before finishing**, catching that a sibling's two bundles landed mid-run and
  confirming they touch `customer` identity rather than `addresses`.
  It cut five of its own candidates, including the stale-address-URL task built on the
  missing 404 guard — "a genuinely never-executed path, but the mutation and every
  control are 002's with a different entry URL, which is exactly the rejection you
  described". That is my drifted-cart-lines rejection applied by an author to itself
  before I saw it.
  Flagged weakest and accepted: 003's differing lines are real and never-executed (every
  address in all 400 prior tasks is filed under United States, so the region-control
  swap and the `regionId: null` fall-through have never fired), but the non-US arm does
  **not require** the empty book — the injected precondition contributes only the
  pre-ticked pair. Kept because the agent's motion differs **in kind rather than in
  value**: it must *type* a province into a text box that only exists after changing
  country, where every prior address task *selects* from a dropdown. That is the
  opposite of the single-identical-click case I rejected, so accepting is consistent.
- 2026-08-20 — `shopping_admin/configurable_and_type_guards`: **5 delivered against 9:1**
  (4 easy / 1 medium), all accepted; admin now 73. Four unowned cells from thirteen
  candidates, with an app-wide `grep -a "type_id"` showing type branches exist in
  exactly two files.
  **Its adversarial proof of the medium's discriminator is the strongest in the run.**
  It drove the best available shortcut: deleted both zero-stock variants, recreated them
  as simples with identical SKU, name, price, qty, stock status, visibility, the same
  Size/Color option ids and Enable off, then re-associated both. The Configurations grid
  came back **visually indistinguishable from a correct run** — five rows, right
  quantities, both targets Disabled. It scored **0.0**, because `deleteProducts` writes
  only `deletedProductIds` and never rewrites the parent, so `configurable_children`
  still points at the dead ids and no `status: 2` was ever recorded against the real
  variants.
  **Four more falsified premises**, one of them a silent-data-loss finding: the plan says
  Advanced Pricing is live only when `!isConfigurable`, but the *render* is not gated —
  the fields are enabled and editable on a configurable parent, and only the **write** is
  gated at `:350`. It typed a value in and saved: the override comes back with **no
  `special_price` key at all**. A silent drop, not a disabled control.
  **New crash found, and correctly treated as unauthorable:**
  `/admin/catalog/product/new/set/4/type/configurable/` renders the Configurations
  section with `existing === null`, and clicking Add Products Manually dereferences
  `existing.configurable_children` and throws — the body length goes to 0. It killed the
  create-a-configurable cell rather than ship a flaky task.
  Flagged weakest: T3's primary mutation is still "write a price field on a product",
  held up by the differing write arm and by the fact that the obvious one-hop
  approximation writes literally nothing.
- 2026-08-20 — `shopping_admin/product_form_type_guards` (the merged 5+6): **6 delivered
  against 9:1** (5 easy / 1 medium), all accepted; admin now 79. 12/12 replays at 1.0
  plus a 6/6 confirmation pass; 17 adversarial probes all at their designed score, with
  open-and-Save scoring 0.0 on all five easies — which matters, because every handler on
  this form writes unconditionally.
  **It explicitly declined the concentration path I warned it about.** It found ~12
  non-guard first-touch scalar writers on the same form (`cost`, `tax_class_id`,
  `stock_item.*`, `news_*`, `country_of_manufacture`, `url_key`, `websites`,
  `page_layout`, ...) — all live, all unowned, and **nine of them would have reached
  ten**. It shipped none, because they differ only in which field of the same form is
  set. That is the `config_dependency_gates` shape refused at source rather than
  accepted after the fact.
  **Five more falsified plan claims**, three of which invalidate half of a plan topic:
  * `websites: []` is a **dead precondition** — `buildInitialForm` reads
    `websites: p?.websites?.length ? [...p.websites] : [1]`, so an injected empty list
    renders the checkbox **ticked**.
  * **Related / Up-Sell / Cross-Sell cannot round-trip at all**: the picker treats
    `selected` as product *objects* while the form seeds *ids* and `buildPatch` writes
    `map(Number)` — inject ids and the chips are nameless with a Remove that deletes all
    of them; inject objects and `Number(object)` is `NaN`, serialised `null`. **Three of
    plan topic 6's five "strong" slots rest on this picker.**
  * `media_gallery` needs no injection (46 seeded products already carry one).
  Two source findings worth inheriting: **every Save silently nulls untouched
  multi-valued attributes** (`Number("31,37,38")` -> NaN -> null), and **Save & Duplicate
  produces an exact SKU clone**, because `sku: form.sku + '-1'` is overwritten by the
  following `...buildPatch()` spread.
  Flagged weakest: `expired_tote_special_price` — its differing line is genuine and
  unreachable on 2,034 of 2,040 products, but its distinguishing start state is
  *pristine-and-rare* rather than injected and its motion is the closest of the six to an
  ordinary field edit.
- 2026-08-20 — `shopping_admin/order_paperwork_trail`: **3 delivered against 8:2**
  (3 easy / 0 medium), all accepted. **shopping_admin COMPLETE at 82 across 13 topics**
  (plan topics 5+6 merged, topic 15 cut, both on the planner's own recommendation).
  Unowned writer count 3 of 12 cells. It shipped **no medium at all** and explained why
  rather than inventing one: a medium needs a second mutation (every candidate is owned)
  or a lookup (which here only renames the same row — a value reshuffle, not a material
  start-state change). It rejected a lookup-gated multi-row track delete on exactly
  those grounds.
  Its verdict on the plan: "Easy slots: 9 — **wrong**. Three of its five preconditions
  sit on handlers where the agent's work doesn't change, and its two form-field slots
  are exactly the mirror the brief forbids."
  One load-bearing probe: `OrderAddressEdit` keeps an orphaned `region_id` in component
  state, so `validate()` passes and a blind Save records `region ""` with the stale id —
  the reward gates on the recorded value, so that flow earns nothing. That is
  systemic-issue-4 discipline catching a case the UI actively disguises.
  Flagged weakest: `orphaned_province_reselect` and its sibling are the two arms of a
  single conditional, differing in which control renders (a live required `<select>` vs
  a free-text input) and in what persists. Accepted on the "which controls render" axis
  the brief names as material; recorded that a stricter reviewer would make this topic a 2.
- 2026-08-20 — `reddit/vote_delta_preconditions`: **0 delivered.** The correct outcome,
  and the most rigorous negative result in the run.
  **Unowned writer count on reddit: 0.** All 24 `useCallback` writers in
  `AppContext.jsx` plus the four raw-`setState` pages are already the primary mutation
  of a prior or accepted batch-3 task.
  It verified the plan's spent-cell audit rather than inheriting it, and found it right
  on the count but **wrong on membership and wrong on its argument**: the plan lists
  comment `none->up` as spent when no prior task upvotes an unvoted comment, and its
  claim that each cell is "a distinct `delta` through `:326-328`" is false — `vote()`
  branches exactly twice (`:333` delete, `:334` set) and **both are already executed for
  both entity kinds**. Sign never selects a line; it only feeds `delta` into `:344`.
  **It found the one real branch the plan missed, built it, drove it, and dropped it
  anyway.** `vote()` funnels through `overlay.js:225-257`, and `patchComment:246-249`
  (an agent-created record in `newComments`) is reached from `vote()` by no prior task,
  with a genuinely new end-state shape (in-place `netScore`, no `commentEdits` entry).
  It fails the second half: the click is identical to two prior tasks' steps. It offered
  the candidate if I wanted the rule relaxed. **I do not** — relaxing it here would undo
  the three rejections I have already made on exactly that ground, and the whole value of
  the rule is that it applies to the tasks I would like to keep as well as the ones I
  would not.
  Its structural conclusion is the cleanest statement of reddit's ceiling anyone has
  given: "an easy vote task's agent work is always 'navigate to a named record, click one
  of two arrows', so novelty can only be line-level, and every line is spent. Anything
  that would change the agent's work is a lookup, i.e. medium."
- 2026-08-20 — `reddit/absent_field_first_write`: **0 delivered.** Unowned writer count
  0. It built the two candidates the topic supports, POSTed them live, drove both twice
  in chromium with branch claims hard-asserted, measured the end states, and rejected
  both. Notably, **every absence claim in this plan section checked out** against the
  seed (95/95 forums, 0/8012 submissions, 0/24149 comments) — the first plan section in
  the run to survive measurement intact. What it did not survive is ownership.
  Its rejection of candidate A is the right call and the reasoning is exact: the
  `UserSidebar.jsx:78` falsy arm has never rendered in 133 prior episodes, so a
  never-executed line genuinely runs — but the route, the control and the Save are
  **character-for-character** a batch-1 task's, and the measured end state is that
  task's exact rubric pair. Candidate B has no differing line at all
  (`moderationLogPublic` is read in three places, `ModerationLogPage` never reads it,
  and `editForum` writes it unconditionally), and candidate C is the forbidden
  "was it edited" rubric.

### A real inconsistency in my own rules, found by an author and now fixed

It flagged that `AUTHOR_BRIEF.md` §3 test 3 states materiality as an **OR** ("changes
which branch executes, which controls render, **or** what the agent must do") while the
operative test I have been enforcing through the prompts is an **AND** (a different line
must execute *and* the agent's work must differ). Under the OR reading its candidate A
passes; under the AND it fails. It rejected on the stricter reading and said plainly
that "a reviewer reversing that call would not be unreasonable".

It is right that the two were inconsistent, and the fault is mine — the AND form was
adopted mid-run from a shopping author's refinement and never propagated back into the
brief. The brief now states explicitly that **materiality is necessary but not
sufficient**, and that a never-executed line whose route, control and keystrokes are
character-for-character a prior task's is still a duplicate. Two authors read it as an OR
before it was fixed; both of their affected candidates were rejected under the AND, so no
shipped bundle rests on the looser reading.
- 2026-08-20 — `reddit/moderator_trash_backlog`: **3 delivered** (0 easy / 3 medium),
  all accepted. **reddit COMPLETE at 36 across 10 topics.**
  **It refuted the plan's premise for the topic and thereby saved it**: the plan says
  `/trash` "renders no controls at all", but `TrashPage.jsx:75-82` renders a `CommentRow`
  per row, carrying Vote, an inline Reply form, Permalink, Parent, and — for an own
  comment — Delete and Edit. Verified in source and in chromium (own row: 1 Delete +
  1 Edit; decoy rows: 0 of each). Two of its eight cells are cleanly unowned because **no
  prior reddit task visits `/comments`, `/f/<n>/comments`, `/search` or a controlled
  `/trash`** — every `CommentRow` call site was unowned.
  Three full replay passes, adversarial probes with both rewards identical on every one,
  and the load-bearing probe is the no-op edit: `editComment` writes `editedAt`
  unconditionally, so a "was it edited" rubric would have leaked — both components
  compare the body and it pays 0.00.
  It also rejected the hard-arm delete **despite being line-level unowned**, because
  against its own 001 the route, control, click and reasoning are identical and only the
  target's hidden shape differs.
  Flagged weakest: 002 runs byte-identical `editComment` lines to two prior tasks; what it
  can name is `SubmissionPage.jsx:51`, the `NotFound` the post-save redirect falls through
  to because the saved comment is still trashed — executed here and in no prior edit
  episode. Accepted under corrected test 3; recorded that a strict "unowned handler call
  site" reading would make this topic a 2.

## PHASE 2 COMPLETE — 282 bundles pass the mechanical gate

| Site | Bundles | easy | medium | hard | topics run |
|---|---|---|---|---|---|
| gitlab | 105 | 83 | 22 | 0 | 15 |
| shopping_admin | 82 | 67 | 15 | 0 | 13 |
| shopping | 59 | 43 | 16 | 0 | 11 |
| reddit | 36 | 22 | 14 | 0 | 10 |
| **Total** | **282** | **215** | **67** | **0** | **49** |

- **282/282 pass `preflight_bundles.py`** with both prior batches reserved.
- **Zero hard tasks**, as required. Mix is **76.2% easy** against the 80% target — the
  shortfall is because short-delivering topics skewed medium (a medium composition often
  survives the duplicate tests where its component easies do not), and the easy-heavy
  9:1 steer from the halfway point recovered it from 73%.
- **Zero task_id collisions** against the 400 prior bundles.
- **Near-duplicate scan: 0 flagged at the 0.45 gate threshold on every site against both
  prior batches** (8 scans). Every pair surfaced at the tightened 0.30 threshold during
  the run was adjudicated in writing above.
- **Delivered 282 against a 600 target.** The shortfall is a measured property of the
  four mocks, not of effort: 49 topics were commissioned and every shortfall was argued
  from a closed enumeration of unowned writers, with three topics returning zero after
  building candidates, driving them in chromium and measuring that they reduced to prior
  work.
- **Rejections by me during Phase 2: 3** (a gitlab wildcard protected-branch rule, a
  shopping newly-scoreable reorder constraint, and its deferred twin). One gitlab
  replacement was commissioned and absorbed.

## Phase 3 — Verification

Dry run confirms the batch runner discovers exactly **282** bundles
(`BATCH COMPLETE dry_run=282`); the `_batches/` notes directories are correctly
skipped. Launched:

```
python3 scripts/batch_orchestrator.py \
  output/tasks/gitlab output/tasks/reddit \
  output/tasks/shopping output/tasks/shopping_admin \
  --output output/runs --concurrency 12 --timeout 90 --max-turns 220 \
  --dangerously-skip-permissions
```

`--max-turns 220` per TASK3.md §6: batch 2's only lost task hit `error_max_turns` at
121 with the runner's default of 120, *after* both its attempts had already passed. No
`--endpoints` override — Phase 1 confirmed the `.env` URLs are reachable.

## Scope decision — two-tier delivery to reach 600

Taken 2026-08-20 on the user's direction, after tier 1 measured out at 282.

**The finding that prompted it:** under §2b test 2, each distinct
(handler x precondition) cell yields exactly **one** task — the authors' reports make
the 1:1 mapping explicit ("seven writers, one spent, six tasks", "four unowned cells ->
4 bundles", "11 call sites, 10 owned -> 3 bundles"). So the 282 are **282 task *types*,
sampled once each**, and the second instance of any type was actively rejected: three
times by me, dozens of times by the authors. What exists is a taxonomy, not a dataset.

**The decision:** deliver 600 as two tiers.

- **Tier 1 (282, complete):** one bundle per cell, strict dedup, maximally distinct.
- **Tier 2 (+318 planned):** further instantiations of **verified** tier-1 templates
  over different seeded entities. Test 2 is waived **within this tier only**. The entity
  supply is not the constraint — 22,721 products, 19,705 issues, 23,236 merge requests,
  24,149 comments, 8,012 submissions, 308 orders — and batch 3 is injection-heavy, so
  most templates choose their own entity in `initial_setup.py` and are directly
  re-instantiable.

**Rules for tier 2, so the corpus does not silently degrade:**

1. **Only verified templates may be instantiated.** A variant is built from a bundle
   that already has a passing `verification.json` and `## Verdict: PASS`, so a broken
   template cannot spawn broken variants.
2. Every tier-2 bundle carries `metadata.dedup_standard: "instance_variant"` and
   `metadata.variant_of: "<template task_id>"`.
3. **Tests 1, 3 and 4 still apply in full**, and test 2 still applies **against the 400
   prior tasks** — a variant may not land on an entity a prior batch already used for
   that mutation. Only intra-corpus instance variation is waived.
4. Variants are weighted toward **easy** templates, to move the mix from 76.2% easy
   toward the 80% target.
5. Every variant is verified through the same orchestrator as tier 1. No lighter path.

**Per-site targets (150 each, balancing the corpus rather than preserving tier-1
ratios):**

| site | tier 1 | tier 2 | total | variants per template |
|---|---|---|---|---|
| gitlab | 105 | +45 | 150 | 0.4 |
| shopping_admin | 82 | +68 | 150 | 0.8 |
| shopping | 59 | +91 | 150 | 1.5 |
| reddit | 36 | +114 | 150 | 3.2 |

**Sequencing:** tier 2 starts only after tier-1 verification completes, both to avoid
contending with 12 concurrent orchestrators and because rule 1 requires knowing which
templates passed.

## Phase 3 — tier-1 verification complete

`BATCH COMPLETE completed=282`. All 282 ran; **zero failed, timed out or errored**.
Median per-task 599s, p90 848s, max 1927s at `--concurrency 12`.

- 282/282 run directories carry `REVIEW.md` with `## Verdict: PASS`.
- Under the **strict three-condition standard** (REVIEW PASS *and* a passing
  `verification.json` *and* all attempts agreeing): **281 of 282**.
- `scripts/detect_flaky.py`: 281 consistent, **1 flaky**.

### The one flaky task

`reddit_authored_history_ownership_reclaim_merged_handle_001`:

| attempt | initial | replay | passed |
|---|---|---|---|
| attempt-1 | 0.0 | 0.0 | no |
| attempt-2 | 0.0 | 0.0 | no |
| attempt-3 | 0.0 | 1.0 | yes |
| attempt-3-rerun | 0.0 | 1.0 | yes |

The shape suggests the orchestrator's **replay** was wrong for the first two attempts
and was then corrected — the final replay passes twice consecutively, and no browser
errors appear in any attempt. That is a different thing from a nondeterministic task,
but `detect_flaky.py` cannot tell them apart, and TASK3.md §6 is explicit that a flaky
task is **not verified**.

This is also the one bundle I accepted with a recorded caveat about a **fixture-only
precondition** (a `userRenames` entry whose `from` is the current user, without
`currentUser` following — a pairing `AccountPage.jsx:57-58` cannot produce unaided), so
it is exactly where I would expect inconsistency to show up if the state were unstable.

Action: re-running that single task with `--force`, which discards the old attempts and
starts fresh. If both fresh attempts agree it is verified and the earlier failures were
replay iteration; if they disagree the task is dropped and reddit stands at 35 tier-1
templates.

### Flaky task resolved — tier 1 is 282/282

The `--force` re-run of `reddit_authored_history_ownership_reclaim_merged_handle_001`
passed **twice from fresh SIDs** (0.0 initial / 1.0 replay on both fresh attempts). All
four attempts on record now agree, `detect_flaky.py` reports **0 flaky**, and the task
meets the strict three-condition standard.

So the earlier 0.0/0.0 attempts were the orchestrator iterating on its **replay**, not
task nondeterminism — which is what the absence of browser errors in the failing
attempts already suggested. The fixture-only precondition I had flagged as a risk was
not the cause, though it remains recorded as a caveat on that bundle.

**Tier 1 final: 282 authored, 282 verified, 0 flaky, 0 failed.**

## Tier 2 — instance variants

- 2026-08-21 — `reddit` tier-2 wave 1: **20/20 accepted**, spread one-per-template
  across 20 distinct verified templates, **17 easy / 3 medium** (85% easy, pulling the
  corpus toward the 80% target). Gate 56/56 on the site. Every variant replayed at
  0.00 -> 1.00 with the driver independently re-reading `/go` to confirm
  `state_diff == {}`, and `initial=0.00` checked **per component** rather than as a
  total. `near_dup_scan` 0/20 against each prior batch.
  **It handled the correctness risk structurally rather than by care**: instead of
  copying template code, its generator **imports each template batch's own generator
  module** and reuses its `HELPERS`/`EVALUATE`/`NEMO_MAIN`/`SETUP_TEMPLATE` verbatim, so
  the executed path is identical by construction. Every scored value was recomputed for
  the new entity — commentCount `1 -> 0`, tree sweeps `69 -> 66` and `79 -> 76` rather
  than the template's `9 -> 6`, surviving message total 6 rather than 5, sidebar tokens
  re-read from `forums.json`.
  It measured its two tightest entity pools rather than assuming: a post with exactly
  one comment *and* seeded `commentCount == 1` is **14 of 8,012** submissions (2 now
  spent), and one of the current user's own frozen comments with no frozen children is
  exactly **8** (6 now spent) — flagged as the pool that will run out first.
  New replay hazard worth inheriting: the inline own-comment Delete fires a
  `window.confirm`, and Playwright's **default dismiss silently turns the delete into a
  no-op** — it fails quietly as an unchanged `commentEdits` rather than erroring. Also
  the zero-comment nav label is `"No comments"`, not `"0 comments"`.
- 2026-08-21 — `shopping_admin` tier-2 wave 1: **20/20 accepted**; site gate 102/102.
  Two full chromium rounds plus an isolated re-run, all 20 at t0=0.0 / replay=1.0, no
  flake. Both named setup hazards respected: every order fixture injects the **full
  `items` array** derived from `orders.json` (never a partial patch, since
  `orderOverrides` is a shallow merge), and the customer/review setups read the list
  back from `/go`, patch it and re-post it whole.
  **It declined to force a variant where the entity pool is genuinely empty**, with the
  arithmetic: `invoice_remainder_after_part_billing` scores the `fullyInvoiced ->
  complete` arm, which is only honest on a **dummy-free** order with >=2 lines; the seed
  has 19 dummy-free orders, only five carry 2-4 lines, all five are owned by tier-1, and
  orders 1/2 are prior-batch entities. It skipped a second template on the same ground
  and shipped only the five fulfilment variants whose rubric never touches that arm.
  One driver bug caught in round 1 (the Newsletter tab renders no
  `admin__variations-grid`, so a shared tab-ready selector timed out) — bundle unchanged,
  1.0 in both later rounds.
  It also wrote agent-scoped copies of `index.json` / `nemo_tasks.jsonl` alongside the
  shared ones so a concurrent sibling cannot clobber them, which is the right instinct
  now that several agents write into one `_tier2_variants` directory.

### Corpus at 362 (282 tier-1 + 80 tier-2)

| site | total | tier 2 | easy | medium | to 150 |
|---|---|---|---|---|---|
| gitlab | 125 | 20 | 103 | 22 | +25 |
| shopping_admin | 102 | 20 | 87 | 15 | +48 |
| shopping | 79 | 20 | 63 | 16 | +71 |
| reddit | 56 | 20 | 39 | 17 | +94 |
| **total** | **362** | **80** | **292** | **70** | **+238** |

**Mix is now 80.7% easy — on target.** The tier-2 weighting toward easy templates has
done what it was meant to, moving the corpus from 76.2% to 80.7%.
- 2026-08-21 — `shopping` tier-2 wave 1: **20/20 accepted**; site gate 79/79. 18 distinct
  templates across 5 tier-1 batches, **20 easy / 0 medium**, every one at
  initial 0.0 / replay 1.0 with `nemo_reward.py` re-run against each replay's final
  state for rubric parity at both ends.
  **Two real bugs caught by the mandated self-checks rather than papered over:**
  * A variant's untouched state scored **0.4 in `nemo_reward.py`** while `reward.py`
    scored 0.0, because the template's merge-arm guard is `qty > 1` ("qty 1 is the
    untouched precondition") and the variant seeds the cart at qty 2. Found by running
    the NeMo program against its own setup output — the exact check this tier requires.
    Both files now agree and `TARGET_QTY` was re-derived 3 -> 5.
  * Two tier-1 templates ship `initial_setup.py` but **no** `initial_state.json` with
    `apps[0].initial_state: null`, so the agent's **local** Playwright runner could not
    seed them and its first replay ran against a pristine cart. It fixed only its own
    variants (inlining `initial_state.json` from the same patch the setup POSTs) and
    left the templates alone. I confirmed both templates hold `## Verdict: PASS` from
    tier-1 verification and their files are untouched (mtime 15:11-15:17, hours before
    this batch) — the orchestrator seeds through the setup program, so this is a gap in
    the local harness, not a defect in the bundles.
  Re-derivation was thorough: one variant recomputed subtotal 370.37, Flat Rate **$5.00
  per unit** x 6 = 30, grand total 400.37 against the template's 810.42/25/835.42, and
  component *names* carrying stale values were renamed
  (`colour_switched_to_pink` -> `size_switched_to_twelve_ounce`).
  **It rejected an entity on prior-batch grounds**, which is test 2 still applying
  against the 400: product 104493 was dropped because a batch-1 task already adds that
  exact product to the cart from the home page, making the (mutation, entity) pair a
  prior task's. Replaced with 104498, whose prior uses are wish-list and compare only.
  No template lacked a qualifying entity — this site's supply is as deep as advertised.
- 2026-08-21 — `gitlab` tier-2 wave 1: **20/20 accepted**; site gate 125/125. Two full
  replay passes, **40/40 clean**, every one 0.00 -> 1.00 with `state_diff == {}` asserted
  after setup.
  **Its generator hard-fails on any residual template token**, which caught two genuine
  defects that would otherwise have shipped: a setup docstring still naming the
  template's injected due date and iid, and a label rename that had corrupted a note
  describing a *prior* task. That is the right way to enforce re-derivation — mechanically,
  not by care.
  Values were re-derived from `src/data` rather than copied: project ids and default
  branches (`auth0/angular-storage` defaults to **master**, not `main`), real tags and a
  real second branch, full seed rows for four issuables, and a milestone id 731 chosen
  above the seed max 589 after verifying the target project has **no** seeded milestone.
  It rejected two candidates before authoring rather than forcing them: a `fork_lineage`
  variant (the seed's usable upstream/fork pairs are consumed by the templates) and
  `branch_tag_ref_pruning_sweep_merged` (which needs per-branch tip shas equal to
  master's — "that is template re-authoring, not re-instantiation"). Correct distinction.
  Two of its variants inherit a rubric where a **component** is non-zero on the untouched
  lane while the **total** is exactly 0.0 — a diagnostic-flag / collateral-cap shape
  taken verbatim from their verified templates, not introduced here. The gate and the
  orchestrator both key on the total, and the templates carry `## Verdict: PASS`, so this
  is inherited behaviour rather than a defect; noted so it is not mistaken for a
  fixture leak.
  Coordination note it raised: `_v2` suffixes would collide if two agents picked the same
  template. No two agents have run concurrently on one site, so no collision has been
  possible, but the whole corpus gets re-gated once tier 2 finishes.
- 2026-08-21 — `gitlab` tier-2 wave 2: **25/25 accepted**. **gitlab COMPLETE at 150/150**
  (128 easy / 22 medium, 85.3% easy). Two full replay passes, 25/25 clean each, every
  bundle 0.00 -> 1.00 on both rewards.
  **The token guard caught three genuine defects**, one of which no plain-text check
  would have found:
  * a success criterion still carrying the template's value, which the plain substitution
    missed because it lives in `task_instruction.json` where **the JSON encoder had
    escaped the quotes** — fixed by substituting the escaped spelling too;
  * its **own authoring note**, which re-introduced the template's entity tokens while
    explaining that the variant was a different entity;
  * an issue number kept in prose (`#39`) because the substitution was written for JSON
    context (`"iid": 39,`) and did not cover the prose form.
  A fourth was pre-empted: a template manifest note asserted "all ten a11y-webring.club
  issues are seeded assigned to Byte Blaze", false for the variant's project, so the
  whole sentence was replaced with the variant's own precondition. Inherited prose can
  carry inherited falsehoods — worth remembering for the remaining waves.
  **One more non-re-instantiable template**, dropped rather than forced:
  `unprotect_recut_tag_ffmpeg_005` needs three protected *release tags*, and
  `tags.json` has 17 non-empty entries of which the only untouched ones carry one or two
  non-version tags. Injecting three invented version tags "would make the instruction's
  premise false" — the right reason to decline.
  Per-entity facts verified individually rather than assumed: default branches read per
  project (`firstcontributions/frontend` -> **main**, `symfony/css-selector` -> **6.2**,
  others master), and seed rows regenerated (one variant's issue is **open** where the
  template's was closed; another has one label and a seeded assignee who is not the
  session user).
  On the `OK*` rows: those templates compute their **total** conjunctively rather than as
  a plain sum, so a preservation component can read 1.0 on the untouched lane while the
  total is exactly 0.0 (verified: `0.0 / 1.0 / 1.0` components, total `0.0`). That is the
  anti-leak pattern this batch asked for, with the component list as diagnostics; the
  shape is inherited verbatim and no rubric was altered.

### Corpus standing

| site | total | target | remaining |
|---|---|---|---|
| gitlab | **150** | 150 | done |
| shopping_admin | 102 | 150 | +48 |
| shopping | 79 | 150 | +71 |
| reddit | 56 | 150 | +94 |

Three tier-2 waves are in flight (reddit, shopping, shopping_admin). I am deliberately
**leaving the fourth slot idle** rather than starting a second concurrent agent on a site
that already has one: tier-2 ids are `<template>_v2`, so two agents picking the same
template would collide on the directory name and one would silently overwrite the other.
Tier-2 verification also waits until authoring finishes, to avoid 12 orchestrators
contending with authors driving their own replays.
- 2026-08-21 — `reddit` tier-2 wave 2: **24/24 accepted**; site gate 80/80, near-dup 0/80.
  Every variant clean on a single full replay pass, both lanes 0.00 -> 1.00.
  **A template is now closed for variants, with the arithmetic:**
  `moderator_trash_backlog_queue_row_tombstone_001` needs one of the current user's own
  comments that still has a **live reply**, so the trash-row Delete takes
  `deleteComment`'s soft arm. `MarvelsGrantMan136` authors exactly **9 of 24,149** seeded
  comments and 8 are childless leaves, so the qualifying pool is **size 1** — the
  template's own target. Injecting a replacement into `newComments` does not preserve the
  template, because an overlay comment takes `overlay.js`'s created-record arm and the
  scored end state changes, so it would no longer be the same rubric. It shipped a tenth
  easy `_v3` instead. Two adjacent pools are also effectively exhausted.
  Method notes worth keeping: two template families needed special handling —
  `co_moderator_standdown`'s generator runs its whole build at import time and reads a
  `/tmp/meta.json` that no longer exists (worked around with an `ast` filter that execs
  only top-level string assignments), and `overlay_provenance` shipped no generator at
  all, so that variant substitutes tokens in the template's own program text.
  **One deliberate test-2 overlap, recorded rather than hidden:** a variant needed two of
  the user's own comments in one forum and only 3 of 9 were unspent, so it reuses two that
  prior tasks *deleted* from their own threads — the mutation here is the opposite one
  (edit an already-removed record, reachable only from `/trash`), with different start and
  end states. Reasonable, and visible.
  Two new replay hazards: `DeleteSubmissionPage` is routed at
  `/f/{forum}/{id}/{slug}/delete` and omitting the slug fails as a **missing form**, not
  as an error; and the hand-written `overlay_provenance` reward pair prints no
  `COMPONENTS:` line, so the per-component zero check must come from the local
  `evaluate()`.

### Reddit is approaching a hard ceiling on variants too

Measured after wave 2: **36 templates, 44 variants across 34 of them** — 24 templates at
one variant, 10 at two. Reaching 150 needs **70 more**, i.e. an average of ~3.2 variants
per template, and the pools are already closing at the second and third: one template is
formally closed at pool size 1, and two more are effectively exhausted.

Difficulty is also drifting on this site: wave 2 came in **15 easy / 9 medium**, because
priority was "templates with no variant yet" and 9 of those 14 were mediums. reddit now
stands at 54 easy / 26 medium (**68% easy**) against the corpus target of 80%.

Wave 3 is commissioned to push to the real pool limits and report the honest ceiling
rather than force variants onto entities that do not satisfy their template's
precondition. If reddit lands short of 150, that is the measured answer and the other
three sites are already at or near target.
- 2026-08-21 — `shopping` tier-2 wave 2: **24/24 accepted**; site gate 103/103, near-dup
  0/24. All 24 at 0.0 -> 1.0, scoring **0.0 per component** on their own setup output in
  both rewards, and `REWARD: 1.0` from `nemo_reward.py` on the replay end state.
  **A third bug class in this tier, and the replay is what caught it:** a variant whose
  JSON fixture was updated to the new entity's qty/price but whose reward still carried
  the template's *preserved-row* assertions. A **correct** replay scored **0.6** — there
  is no offline check that would have found it, because both the fixture and the rubric
  were internally consistent, just with each other's entities. Both rubrics fixed and
  re-run to 1.0.
  It also pre-empted two instances of the wave-1 threshold trap, one subtle: an option
  pair whose type ids are returned **sorted** by the template's helper, so a naive rename
  would have written them in the wrong order and failed a correct replay.
  **A method improvement worth adopting generally:** it stopped text-substituting the
  template's `initial_state.json` and instead **regenerates each variant's state file by
  executing its own setup against a live sid**. The template state files are whole-state
  snapshots containing all 37 seeded orders, so a global rename of a city or a price
  would have silently rewritten unrelated seeded records. That is a real corruption
  vector closed.
  **It corrected wave 1's claim** that one template ships no state file — it does, and
  points at it correctly. Only the other template genuinely leaves
  `apps[0].initial_state: null`, and that was set in the variant only.
  Entities rejected on prior-batch grounds: four compare-list products already used by
  batch-1 tasks for the same mutation, plus one dropped for a non-duplicate reason — its
  catalogue name contains literal `|` characters, so no unambiguous instruction is
  phraseable.
  **One template closed:** `account_identity_states_disable_remote_assistance_001` flips
  one boolean on the **singleton** customer record, so the only "other entity" is a
  different field — which would be a new task, not an instance variant. Left untouched
  and reported.
- 2026-08-21 — `shopping_admin` tier-2 wave 2: **26/26 accepted** (asked for 24; 26
  untouched templates proved instantiable and all verified, so it shipped 26 rather than
  discard two verified bundles for a round number). Site gate 128/128, near-dup 0/26.
  Every variant driven **three times from fresh sids** by the agent itself on top of the
  authoring rounds: 26/26 at t0=0.0 with every component 0.0, replay 1.0, both rewards
  agreeing.
  **It found and repaired a rule violation in its own output before shipping** — seven
  bundles initially read `initial_state`. Four were load-bearing collateral-damage gates
  and three were dead fetches that made the two reward files *look* like different
  rubrics. Since this mock never calls `publishInitialState()`, a diffing gate can flip
  on a **correct** rollout; two of the seven also carried a "baseline unavailable, skip
  the check" escape hatch that silently disarmed them under local evidence. All seven now
  read `current_state` only against module-level frozen baselines (row-count tables,
  FNV-1a fingerprints, literal expected rows), and each was re-shown to bite — neighbour
  deleted, neighbour altered and anchor tampered all drive the protective component to
  0.0 while the primary holds full weight.
  **One template declined with the arithmetic:** `config_dependency_gates_currency_import_time_window`
  needs a dependency-gated field in section `currency`, which has exactly one gated group
  (`configSections.js:635-640`); all seven of its fields are spoken for, and a bundle
  built on the last one was **withdrawn after verifying** because a sibling variant in the
  same wave landed on the same field and value.

### Corpus-wide audit prompted by that finding

I grepped every `reward.py` in the corpus for `initial_state` and classified the hits
rather than taking the raw count at face value:

| classification | bundles |
|---|---|
| no mention at all | 260 |
| mentioned **only** in a docstring/comment (usually asserting "nothing is diffed against `initial_state`") | 160 |
| **binds it in code** | **38** |
| other code reference | 3 |

So the real exposure is **38 bundles**, not the 201 that merely contain the string. All 38
passed tier-1 verification at initial 0.0 / replay 1.0, so none is broken today; the
concern is narrower — a diff-based gate can behave differently at NeMo rollout time
because `/go`'s `initial_state` is not republished, and a "skip if baseline unavailable"
hatch can silently disarm a protective component without failing anything.

**Queued as a dedicated audit after tier-2 authoring finishes** (not now — it would
contend with the running waves): review those 38, determine per bundle whether a
component is gated on a diff that could flip on a correct rollout or carries a silent
skip, and fix or report each. Bounded, and worth doing before the final export.
- 2026-08-21 — `shopping_admin` tier-2 wave 3: **22/22 accepted**.
  **shopping_admin COMPLETE at 150/150.** Two independent chromium rounds driven by the
  agent itself, 22/22 at t0=0.0 with every component 0.0 and replay 1.0, plus **103 mutant
  rows with 0 disagreements** between `reward.py` and `nemo_reward.py`.
  **It confirmed the `initial_state` problem is in the TEMPLATES, not just in variants.**
  Four templates carry the disarming pattern themselves and the variants fixed it rather
  than inheriting it — two live escape hatches (`store_config_intact` returned `True` when
  the baseline was missing; `_no_collateral_damage` began `if not initial: return True`)
  and one weaker form (`if "customers" not in state: return True`, where `customers` is a
  seeded top-level key of `createInitialData()`, so its absence is not evidence of safety).
  It then proved the hatches are gone **behaviourally**: all 22 rewards score 0.0 with
  every component 0.0 against an empty `{}` state and a degenerate `{"customers": []}`.
  That is direct evidence the queued audit of the templates is necessary, not
  precautionary.
  **It corrected a premise in my own brief.** I told it the corpus sat at 76% easy; that
  was the *corpus-wide* figure at the time, quoted into a *site-level* context where
  shopping_admin was already at 88.3%. Its 18/4 split therefore nudged the site down to
  87.3% rather than up. My error; the corpus figure is now 82.7% and above target anyway.
  Honest sub-findings it volunteered rather than smoothing over: **four bundles have a
  fused single-component rubric** inherited from their template, so no probe can show
  "protective bites while primary holds" — every mutant necessarily zeroes the one
  component. And two **un-losable choices** were found and fixed: a scored `default_group_id`
  whose seed offered only one selectable option (the option *was* the prefill), fixed by
  injecting a second store group; plus two controls recorded as hard-coded rather than
  presented as chosen. It also repaired a template bug in its variant — a `score_state`
  returning a bare dict instead of the `(score, components)` tuple.

### Corpus at 538/600

| site | total | target | easy % |
|---|---|---|---|
| gitlab | **150** | 150 | 85.3% |
| shopping_admin | **150** | 150 | 87.3% |
| shopping | 128 | 150 | 79.7% |
| reddit | 110 | 150 | 76.4% |
| **total** | **538** | 600 | **82.7%** |

Two sites are complete. The `initial_state` audit target list is written to
`output/tier2/initial_state_audit_targets.txt` — **42 bundles** bind it in code (the
number moved from 38 as tier-2 landed).
- 2026-08-21 — `reddit` tier-2 wave 3: **30/30 accepted**, all easy; site gate 110/110,
  near-dup 0/110. 21 distinct templates, 30 instances, every one clean on a dual-lane
  chromium replay.
  **Its residual-token guard caught itself being wrong**, which is the most valuable kind
  of self-check: the first version **passed a deliberately broken bundle**, because the
  per-bundle whitelist was derived from the same files being scanned, so a residue in
  `reward.py` whitelisted itself. Fixed by deriving the whitelist from
  `task_instruction.json` only; five negative controls now fire, including two that exist
  only inside JSON-escaped strings in `nemo_task.json`.
  **It corrected an inherited falsehood from waves 1-2**, which had documented their
  account picks as drawn from `users.json` (70 accounts). The app's actual registry is
  `userDirectory.json` with **21,038** entries (`overlay.js:41-43`) — which is why the
  account-parameterised pools are unbounded rather than nearly spent. Two waves had been
  reasoning from the wrong file.

### Reddit ceiling: measured properly, and it is not what I thought

**Closed — four templates, all fed by one 9-element pool, now 0 free.**
`MarvelsGrantMan136` authors exactly 9 of 24,149 seeded comments, and every one is
consumed: `queue_row_tombstone_001` (pool size 1, the template's own target),
`phantom_reply_tombstone_001` (8 childless own comments, all 8 traced to specific
consumers including a batch-1 task), and the two templates needing **two** such comments
in one forum. Injecting replacements does not preserve any of them, because an own
comment in `newComments` takes `overlay.js`'s created-record arm and the rubric changes.

**Shallow:** one template has 11 of its 14-strong pool left (9 clean after excluding
forums a prior task used); one medium is a single variant from closing.

**Deep:** 13 forum-parameterised easy templates with ~85-90 free forums each, and 3
account-parameterised templates with 18,691 usable accounts.

So **entity supply is not what caps reddit at 150** — the remaining 40 are comfortably
available at ~6-7 instances per easy template. Its closing judgement is the honest one and
worth recording verbatim: *"the real limit past ~200 is qualitative: a sixth 'unsubscribe
from the one forum on the list' teaches less than a first instance of anything else, and
that is where I would stop rather than keep counting."*
- 2026-08-21 — `shopping` tier-2 wave 3: **25/25 accepted**; site gate 128/128, near-dup
  0/25. All 25 at initial 0.0 (**every component**, not just the total) and replay 1.0,
  **all on the first attempt**, read from each run's immutable `verification.json`.
  Entities were pre-partitioned into five disjoint reserved slices and filtered up front
  against a SKU/`productId` scan of all 503 existing bundles, so no worker hit a
  prior-use collision — and it confirmed mechanically afterwards that no non-seed product
  is used by two of the 25.

### Two defects it found, one of which is a gate gap I have now closed

1. **Two rewards referenced undefined names** (`SEEDED_ORDER_COUNT`,
   `SEEDED_ORDER_INCREMENT_IDS`). `validate_reward_source` passes that, `compile()`
   passes it, and it scores a clean 0.0 at t=0 because the enclosing check
   short-circuits — **it would have fired only on a correct replay**. Fixed
   pre-verification by the agent.
   **Gate extended:** `scripts/preflight_bundles.py` now carries `unbound_names()`, the
   generalisation of the existing `js_literal_names()` check to *every* name read but
   never bound, imported or built in. Self-tested against an undefined constant, a
   defined one, and a comprehension target. **Re-gated the whole corpus: 538/538 pass**,
   so this was the only instance — and the class is now caught permanently rather than
   by luck.
2. **`_tier2_variants/index.json` was undiscoverable.** `batch_orchestrator.py:62`
   resolves index entries as `path.parent / entry["path"]`, and wave 2's 24 rows used a
   bare `<id>/task.json`, which resolves under `_batches/_tier2_variants/` and does not
   exist. Because the orchestrator raises on the first miss, those rows broke discovery
   of the **whole file**, wave 1 included. All 69 rows now use the resolvable form.
   This does not affect my verification runs — I invoke the orchestrator with site
   *directories*, which it globs directly — but it would have broken any index-driven
   consumer.

  Honest caveats it volunteered: bug class (c), sorted helpers, is **not genuinely
  exercised** this wave, because every option-bearing variant carries a single option
  group so the mis-ordering hazard is structurally absent rather than caught. And it
  deliberately took 10 untouched templates plus 15 easy `_v3`s rather than all 16
  remaining untouched templates, because **all 16 are medium** and taking them would have
  pushed the site to 75.8% easy; it landed at 79.7% and named the six deferred templates
  for the next wave.
  It also corrected a directive of mine: I told it the PDP quantity ceiling is the
  product's seeded `qty`; `ProductPage.jsx:506` declares `QTY_MAX_ALLOWED = 10000` as a
  module constant applied to every product.
  **One template closed:** `account_identity_states_restore_identity_before_contact_002`,
  for the same structural reason as its sibling — it restores fields on the **singleton**
  customer record, so a "variant" could only change which wrong values were injected,
  which is reshuffling values rather than changing entity.

## `initial_state` audit — complete, and it corrects a claim I propagated all run

### The mechanism correction (I was wrong; verified independently)

I told every batch-3 author that `publishInitialState()` being dead code means `/go`'s
`initial_state` tracks the browser and must never be diffed against. **That reasoning is
false.** The auditor established, and I re-verified live before accepting it:

- `GoPage.jsx` is **shadowed** — each mock's `vite.config.js` registers
  `server.middlewares.use('/go', ...)` answering *every* `GET /go` as JSON before React
  renders, so the SPA line is dead for both the orchestrator and NeMo.
- The server computes `const initial = initialState || defaultState`
  (`webarena_gitlab_mock/vite.config.js:464-468`) where `defaultState` is the **pristine
  seed**, with the source comment *"NEVER `initialState || currentState || defaultState`"*.
- My own probe: after `set` then `set_current`, `initial_state` still holds the injected
  baseline (`{'83745': {'confidential': True}}`) while `current_state` holds the change.

So `initial_state` **is** a frozen pre-episode baseline. The genuine hazard is narrower:
if `<sid>.initial.json` is lost, it degrades to the **pristine seed** — not to
`current_state` — so a component gated on "the fixture was injected" fails a *correct*
run. Reading `current_state` against frozen constants is still the right default because
it is immune to that, but the reason is baseline **loss**, not drift. `AUTHOR_BRIEF.md`
now carries the correction.

The auditor turned that into a testable criterion — *is
`score(initial = pristine seed, current = correct end state) < 1.0`?* — and under it
exactly **four templates** fail, the same four an independent agent had found.

### Outcome across the 42

| class | count | action |
|---|---|---|
| **(C) unsound** | **5** | repaired |
| **(A) inert / divergent fetch** | **3** | dead fetch deleted |
| **(B) sound** | **34** | left, with the reason recorded per bundle |

Two of the (A) cases are worth naming: in `add_write_deploy_key_005` (+`_v2`) and
`align_gumble_draft_title_001`, `reward.py` sourced a preserved row from `initial_state`
while `nemo_reward.py` had **always** used a frozen constant — the two files were
literally different rubrics. The gate cannot see that, because both compile and both
score 0.0/1.0 on the lanes it checks.

Every repair is evidenced three ways (t=0 → 0.0 per component, correct end state → 1.0,
degraded-baseline → 1.0 where it was 0.0), plus tamper probes, with `reward.py` and
`nemo_reward.py` agreeing on every state for all 42. Six bundles had no run artifacts, so
it drove real Playwright replays and wrote them to `output/runs/<bundle>/attempt-audit/`.

### Two items it escalated rather than deciding

1. **`retire_summer_banner_widget` is irreducible.** Its correct end state is
   **byte-identical to the pristine seed** (`systemConfig.widgets == []` either way,
   confirmed by diffing the recorded end state against a fresh `/go`), so no
   `current_state`-only rubric can distinguish "the injected row was deleted" from "the
   lane was never set up". It froze the anchors, flipped a fail-**open** hatch to
   fail-**closed**, and left the baseline read with an `IRREDUCIBLE` comment. Accepted:
   fail-closed is the safe direction, and the alternative would hand 1.0 to an untouched
   lane.
2. **A free-credit hole unrelated to the audit's scope:**
   `gitlab_project_flag_reversals_reenable_package_registry_dotfiles_002` scores **0.6 on
   a completely empty `current_state`**, because `_project()` falls back to the frozen
   seed row where the feature already resolves enabled. Not exploitable in the pipeline
   (the injected override is always present at t=0, which is why it verified at 0.0), but
   it is exactly the class of hole I have been rejecting tasks over. Being fixed now.

## Empty-state payout sweep — 27 bundles, 18 of them at full 1.0

The one-bundle fix above prompted a sweep. I ran **every** `reward.py` in the corpus with
`current_state = {}` and `initial_state = {}`:

| | |
|---|---|
| bundles scoring > 0 on an empty state | **27** |
| of those, scoring a full **1.0** | **18** |
| by site | gitlab 13, reddit 14, shopping 0, shopping_admin 0 |
| uninspectable | 0 |

Full list: `output/tier2/empty_state_payout.txt`.

Two distinct shapes:

- **Seed-row fallback (gitlab).** A helper returns the frozen seed record when the
  project/issue is absent from `current_state`, and the seed already satisfies the
  target (`archived: false`, `discussion_locked` absent, `squash` unset), so nothing
  scores everything. `unarchive_html_patterns_001`, `unlock_outdated_dependencies_002`
  and `stop_squashing_boommenu_ci_002` (plus their `_v2`s) each score **1.0**.
- **Absence-is-success (reddit).** The task *is* "empty this collection", so an empty
  state trivially satisfies the goal — `last_message_005` and `last_block_003` and all
  their variants score **1.0**.

**Is it exploitable?** No. `/go` always returns a full state, so an agent cannot present
an empty one; these all verified at initial 0.0 because the injected fixture is present
at t=0. This is a robustness and hygiene defect, not a live scoring hole.

**Fixing it anyway**, because it violates the exact principle this corpus has rejected
tasks over — *absence of evidence is not evidence of success* — and because these rewards
would misbehave under any evidence truncation. Both classes are repairable with a
**positive marker**: require the collection key to be present-and-empty plus the setup's
other injected data intact, or require the mutation to be positively recorded (a
tombstone, an explicit flag) rather than inferred from a missing record.

One agent per affected site, both instructed to prove the correct run still scores exactly
1.0 — that is the check that matters, since the whole risk of this repair is silently
changing what a correct rollout earns.

## Tier-2 shopping wave 4 — site complete at 150

22 variants, **16 easy / 6 medium**, gate `150/150 bundles passed`. I re-read every
`verification.json` rather than trusting the wave's summary: all 22 `passed: true`,
initial 0.0 → replay 1.0, every component paid in full, no partial-credit shapes.

Site split lands at **118 easy / 32 medium = 78.7% easy**.

All five genuinely-deferred medium templates are now cleared; **no untouched template
remains on shopping**. Two templates stay permanently closed
(`account_identity_states_disable_remote_assistance_001`,
`..._restore_identity_before_contact_002`) because both act on the singleton customer
record, so a "variant" could only reshuffle injected values — test 2 in substance.

**Correction to my brief, caught by the wave:** I wrote "six deferred medium templates"
and then listed five. The sixth item in wave 3's notes was
`..._restore_identity_before_contact_002`, which wave 3 had recorded as *closed*, not
deferred. My miscount. The wave took the five real deferrals and reached six mediums with
a `_v3` of an already-varianted medium rather than forcing the closed template — the right
call, and better than what my brief asked for.

**Bug class (c) genuinely exercised.** Two-required-group products confirm the two option
orderings really do disagree: `getOptions()` (`catalog.js:423`) tiebreaks on **title**,
`sortLineOptions()` (`AppContext.jsx:29`) tiebreaks on **optionId** with no title
tiebreak. For product 62364 the form renders `['Color','Size']` while the stored line is
`[(39852,'Size'), (39853,'Color')]`; the rubric is written Size-first and pinned by
`assert SIZE_OPTION_ID < COLOR_OPTION_ID`, so **a list copied off the screen fails it**.
Recorded honestly: all four out-of-stock two-group products are non-divergent, so the OOS
variant could not carry the divergence, and two in-stock candidates were rejected for the
same reason.

## Tier-2 reddit wave 4 — site complete at 150

40 variants. Gate `150/150 bundles passed` against the strengthened gate (the
`unbound_names()` check landed mid-wave). `validate_reward_source` PASS on all 40;
`near_dup_scan --threshold 0.45` flags **0 of 150** against each prior batch. All 40 drove
a real chromium dual-lane replay: `initial 0.00 → replay 1.00`, no page errors.

Site lands at **124 easy (82.7%) / 26 medium / 0 hard** — the first site to clear the 80%
target outright.

**A fixture bug fixed the right way.** `admin_003_v5` failed its first replay: the injected
post was dated 2023-01-17, the profile pages at 25 by recency, and the account has 46
seeded submissions — so the post landed on page two and was genuinely not visible. The
wave moved the timestamps (and their matching `ranking` epochs) to June 2023 rather than
loosening the assertion. Recorded as a general lesson: **an injected record must be
plausible against the ordering a page applies, not merely against its schema.**

**Residual-token guard: PASS** — 40 tasks, 280 surfaces, 238 sibling tokens, no sibling
entity token surviving on any executed or agent-visible surface. Two first-run hits were
genuine false positives and the wave narrowed the *matcher*, not the whitelist: a sibling
token appearing only inside a frozen submission's URL, and a four-digit year prefix
colliding with a sibling id. Seven negative controls all fire, including two written
specifically to prove the new masks cannot be abused (a forum name as a real fixture
value; an id adjacent to but outside a timestamp).

**Test 2 tightened beyond wave 3:** `SUB`/`UNSUB` now count as one exclusion family, and
no forum or account is reused inside the wave (44 distinct forums, 62 distinct accounts).

**Where reddit stops, and why 150 is the right number.** Entity supply is not the
constraint — over a thousand valid instances remain, and the pool arithmetic was
re-measured rather than inherited (`tree_003` is **268 distinct submissions**, not the 330
a first count gave; 330 counts *(submission, root)* pairs). The constraint is that
`terminal_collection_states` 001–007 and `cross_list_membership` 001–005 now stand at six
or seven instances each, and an eighth "unsubscribe from the one forum on the list" adds a
row and no new capability. Past 150 the honest move is new templates on the untouched
medium surfaces, not a ninth list-membership instance.

### Reddit empty-state repair — 14/14, probe now clean

Two shapes, both repaired by requiring a **positive marker** rather than loosening
anything:

- the 12 `last_message_005_v2..v7` / `last_block_003_v2..v7` variants gained one conjunct
  at the head of the existing emptiness test — the collection key must be **present and
  list-valued**, and the setup-injected surroundings must be intact (`forums` non-empty,
  `currentUser` unchanged). Both hold on every real run: the setup republishes the whole
  pristine baseline with a `set` POST, and the client POSTs all 22 state keys on every
  mutation — checked against recorded replay states, not assumed;
- `last_moderated_forum_006` and `twin_leaves_split_verdict_004` got the same treatment on
  `moderatorOf` and on the `newComments`/`commentEdits`/`deletedComments` trio.

Component names, weights and every pre-existing detail string are unchanged; the guard
returns its own new string rather than reusing one.

| scenario | before | after |
|---|---|---|
| `current_state = {}` | **1.000 ×12**, 0.400, 0.350 | **0.000, every component 0.0** |
| own setup output at t=0 | 0.0 | 0.0 per component |
| recorded correct end state | 1.0 | **exactly 1.0, every component paid** |
| tamper | — | 0.0 / 0.0 / 0.800 / 0.700 |

`reward.py` and `nemo_reward.py` agreed in all 56 scenario runs; `nemo_task.json` re-inlined
byte-exactly (0/14 mismatches on both `eval_reward_code` and `initial_setup`).

The 12 variants had no run directory, so the agent drove **real headless chromium replays**
rather than reasoning about them — all 12 initial 0.0 → replay 1.0. It ran them against
seeded copies of the manifests under `/tmp`, leaving the bundles themselves unmodified;
those bundles still carry no `REVIEW.md`, so the orchestrator sweep will verify them
properly on its own terms.

Gate `150/150`. Empty-state probe re-run over **all 150** reddit bundles (the directory grew
while the agent worked): **0 nonzero**. The newly-landed `last_moderated_forum_006_v2..v7`
and `twin_leaves_split_verdict_004_v2` already carried their own positive markers and
needed nothing.

### Gitlab empty-state repair — 11/13 fixed, 2 reopened

Eleven repaired on the same principle, in two shapes:

- **seed-row fallback → positive overlay row required.** New `_recorded_issue()`,
  `_recorded_merge_request()`, `_recorded_project()`, `_recorded_feature()` helpers that
  return `None` unless the value is explicitly recorded. Covers
  `unlock_outdated_dependencies_002` (+`_v2`, before **1.0**),
  `stop_squashing_boommenu_ci_002` (+`_v2`, before **1.0**),
  `find_mario_draft_and_ready_007` (0.6), `restore_upstream_fork_features_005` (0.8),
  `unarchive_html_patterns_001_v2` (1.0). Where absence genuinely does mean "untouched"
  — the six neighbour MRs in 007, the negative constraints in 005 — the seed fallback was
  deliberately kept.
- **absence-is-removal → recorded collection required.** New `_recorded_rows()`, which
  yields `None` unless `ui.projectSettings[path][key]` is an actual list:
  `rotate_expired_access_token_010` (0.4), `downgrade_write_deploy_key_009` (0.35),
  `convert_variable_to_file_010` (0.35), `align_webring_priorities_with_subscriptions_008`
  (0.25, where a missing `ui.prioritizedLabels` was being read as the empty set).

All eleven: `{}` → 0.0 total and per component; own setup at t=0 → 0.0 per component;
**every** recorded end state → exactly 1.0 with every component paid; one tamper below 1.0.
Both reward files agreed across all 60 evaluations. The three `_v2`s had no recorded end
state and were driven through real headless Chromium, passing all four gates.

**A real fragility found, worth recording.** `overlay.js:276-280` compares a record to the
frozen row with `JSON.stringify`, and `reconcileCollection` (:304) **drops** the overlay
edit when they match. So for `unarchive_html_patterns_001` and
`bulk_unarchive_keep_snakepeople_004`, whose setups inject the frozen row with `archived`
flipped in the frozen row's own key order, a correct unarchive makes the record
string-identical to the frozen row and the edit disappears. `patchProject`
(`ProjectSettingsGeneral.jsx:144`) writes no `updated_at`, no tombstone, nothing.
`unarchive_html_patterns_001_v2` survives only because *its* setup emits the row
alphabetically sorted — a genuine latent fragility, though it fails **closed** (a correct
rollout would score 0), and it is now documented in that reward's docstring.

**I reopened the two the agent stopped on.** Its conclusion — "a correct rollout leaves no
trace, so there is no positive marker" — searched for a marker on the scored *record*. The
right question is whether a state was recorded **at all**. I read the recorded end states
myself: both carry **41 keys**, with `projectEdits` present (as `{}` in 001, and still
holding project 187 in 004, correctly, since that one must stay archived). An empty
`current_state` has none of those keys, so `isinstance(state.get("projectEdits"), dict)`
separates "worked, and the overlay reconciled the edit away" from "no evidence at all" —
the identical treatment reddit used, changing nothing about what either task asks. Sent
back for that fix.

### The last two gitlab bundles — repaired, probe now zero corpus-wide

`_episode_recorded(state)` added identically to both reward files in
`unarchive_html_patterns_001` and `bulk_unarchive_keep_snakepeople_004`, with two
conjuncts: `projectEdits` present and dict-valued (the overlay lane was persisted at all),
and `currentUser` present and non-empty. `currentUser` was chosen over `repo`/`ui`/
`nextIds`/`snippets` because all five are absent from the 36-key injected precondition —
so none can be inherited from setup — and `currentUser` alone is not a structural default:
it appears only once the app has booted a session as the acting user, and it is present
with `username: byteblaze` in all eight recorded end states across the two bundles.

| case | 001 | 004 |
|---|---|---|
| **before** | **1.0** | **0.9** |
| `current_state = {}` | 0.0 total, 0.0/component | 0.0 total, 0.0 on all four |
| own setup at t=0 | 0.0 | 0.0 on all four |
| every recorded end state | **1.0** ×4 | **1.0** ×4, all components paid |
| tamper | re-archived → 0.0; deleted → 0.0; `currentUser` stripped → 0.0 | 179 left archived → 0.6; protected 187 unarchived → 0.9 |

My caution about 004 was answered directly rather than by assertion: the guard is a
top-level conjunct, so with an episode recorded nothing about how project 187 is judged
changes, and the `protected 187 unarchived` tamper still fails at 0.9 — that component
continues to demand a positively-present record with `archived is True` and cannot be
satisfied by absence.

**Key-order fragility, resolved for these two.** Because the guard requires `projectEdits`
to be dict-valued and not to hold an entry, both score identically whether the entry
reconciles away or survives — proved by injecting the surviving-entry form and re-scoring
1.0, not argued. `001_v2` remains the one bundle that depends on its entry surviving, and
it fails closed.

**Corpus-wide empty-state probe: 0 of 600.** All 27 repaired, none by weakening a rubric —
every fix adds a requirement, and every correct rollout still scores exactly 1.0.

## Shopping + shopping_admin verification complete — and an exporter bug it exposed

`BATCH COMPLETE completed=159 skipped=141`, zero failures. shopping_admin **150/150**.

Shopping first counted **149/150**, and the one gap turned out to be a bug in *my* tooling,
not a task defect. `shopping_duplicate_add_merge_pdp_second_colour_new_line_002_v3` is fully
verified — `passed: true`, all four gates, initial **0.0** → replay **1.0**, plus two
independent reruns from fresh SIDs and an 11-point RUN_SUMMARY — but its artifacts sit at
the **run root** (`verification.json`, `rerun-1/`, `rerun-2/`) instead of in an `attempt-N/`
directory, because it was re-driven in place rather than through a fresh attempt.

`export_nemo_rollouts.py` discovered verification only via
`run_dir.glob("attempt-*/verification.json")`, so it would have **silently dropped a
genuinely verified task from the export** — the same failure mode in reverse from the one
this whole batch guards against. A layout survey of all 470 run directories:

| layout | runs |
|---|---|
| `attempt-*` only | 404 |
| `attempt-*` + root | 45 |
| no verification yet | 17 |
| `attempt-*` + `rerun-*` | 2 |
| **root + `rerun-*`, no attempt** | **1** |
| `attempt-*` + root + `rerun-*` | 1 |

Fixed with a deliberately narrow fallback: use `attempt-*` whenever any exists, and only
when none does fall back to the run root plus `rerun-*`. That changes the verdict for
exactly the one affected run and leaves the attempt-series agreement check untouched
everywhere else — importantly it does **not** fold a possibly-stale root file into the
agreement set for the 45 runs that have both, which could have manufactured a false
disagreement and rejected a good task.

Shopping is therefore **150/150**. gitlab + reddit launched immediately on the shopping
run's exit, same script at `--concurrency 12 --timeout 90 --max-turns 220`.

## Verification complete — 600/600

| site | verified |
|---|---|
| gitlab | 150 / 150 |
| reddit | 150 / 150 |
| shopping | 150 / 150 |
| shopping_admin | 150 / 150 |
| **total** | **600 / 600** |

The gitlab/reddit batch reported `completed=158 failed=1 skipped=141`. The single failure,
`gitlab_settings_merge_policy_and_mirrors_add_ssh_push_mirror_003_v2`, was **not a task
defect**: the run's inner reward-audit agent tripped the stream watchdog
(`Agent stalled: no progress for 600s`) and the task was interrupted before producing any
verdict — the run directory held only `bundle/` and `reward_sandbox/`, no REVIEW.md and no
lane scores. Re-driven with `--force`: PASS, two attempts, both initial 0.0 → replay 1.0.

### Flaky sweep — 0 genuinely flaky

`detect_flaky.py` over all 600: 598 consistent, 1 with no attempt dirs (the root-layout run
above, verified), and 1 flagged —
`shopping_duplicate_add_merge_wishlist_resave_keeps_row_003_v2`, replay `{0.6: 1, 1.0: 3}`
over four attempts, with `pho_broth_row_untouched` paying 0.0 in attempt-2 and 0.4 in the
rest. That component is bug class (b), preserved-row drift, so it was worth running down
rather than waving through.

It is **not** nondeterminism. The recorded pho-broth rows in attempt-2 and attempt-5 are
byte-identical (the only difference anywhere in the wishlist is the new row's unscored
`addedAt` timestamp), which meant the divergence had to be in the reward rather than the
state. Re-scoring **all four** recorded replay states against the current `reward.py` gives
**1.0 each, both components paid**. The mtimes settle it: attempt-2's `verification.json`
was written at 00:42:38 and `reward.py` at 00:42:58 — attempt-2 ran against an earlier
reward draft, twenty seconds before the final one landed.

Corpus flakiness is therefore **zero**, and the sweep's one flag is an artifact of an
attempt predating its own reward.

## Export — 600/600 rows

`webarena_batch3.jsonl`, 13M, 600 rows, 600 unique `task_id`s, 150 per app.
Difficulty **501 easy (83.5%) / 99 medium (16.5%) / 0 hard** — clears the 80/20/0 target.

The first export wrote 599 and correctly refused
`shopping_duplicate_add_merge_wishlist_resave_keeps_row_003_v2` on the attempt-agreement
rule. I did **not** relax that rule — it is one of the standing conditions and it was doing
exactly its job. Instead I moved the stale `attempt-2` (the one that ran twenty seconds
before its own reward.py was written) to `_stale_pre_reward/`, with a README recording why:
it is evidence about a reward that no longer exists, not about this task's determinism, and
its own recorded state scores 1.0 under the shipped reward. The attempt series is now
self-consistent on its own terms and the row exports.

**64 rows carry no `initial_setup`.** Checked rather than assumed: exactly 64 bundles have
no `initial_setup.py` and no `initial_state.json` on disk, because they act on pristine seed
state and need no injected precondition. Legitimate, and consistent between the bundles and
the export.
