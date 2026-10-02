# Batch-2 author brief — read this in full before designing anything

You are authoring 10 tasks for **batch 2**. 200 verified tasks already exist in
`webarena_08_18_batch_200/tasks/`. That directory is **read-only reference** —
read it as much as you like, write nothing into it.

Follow `.claude/agents/task-author.md` in full. Everything below is *additional*
and is the part that actually breaks downstream if you get it wrong.

---

## 1. Difficulty — batch 2 skews hard

Your batch's split is **stated in your prompt**. It is normally
**1 easy / 4 medium / 5 hard**, but a *derived-target* batch ships
**0 easy / 5 medium / 5 hard** — see the note at the end of this section. The
mechanical gate checks the split and will bounce the batch if it is off.
`difficulty` is a claim about the *work*, not a label:

- **easy (1)** — one navigation plus one mutation on an entity named outright in
  the instruction. One success criterion, maybe two. No lookup, no ordering, no
  setup.
- **medium (4)** — 2–3 mutations, *or* one mutation gated on a lookup the agent
  must perform (find the entity matching a stated property, then act on it),
  *or* a single mutation across two pages of a form/wizard. Success has 3+
  independently-checkable criteria.
- **hard (5)** — must satisfy **at least two** of these five, and must record
  which ones in `task.json` `metadata.hard_criteria` using **exactly these
  slugs**:
  - `multi_mutation` — >=4 distinct mutations, or a chain where a later step
    depends on the result of an earlier one;
  - `derived_target` — which entity to act on is not stated and must be computed
    from the UI, with a *unique, deterministic* answer;
  - `cross_section` — the flow spans two or more distinct areas of the same app;
  - `exclusion_constraint` — something must be true *and* a named something else
    must remain untouched, and the reward scores the untouched part;
  - `shortcut_defeating` — the obvious one-step approximation (rename in place,
    edit instead of create-and-retire) must score strictly less than 1.0, and
    you must show in `GENERATION.md` what it scores.

Hard does **not** mean long, vague, or fiddly. Every hard task still needs a
single deterministic end state, exact-value ground truth, and a replay a browser
agent can actually drive. A task that is hard because the instruction is
ambiguous is a **bad task** — do not write it.

Record `difficulty` in **both** `task_instruction.json` and `task.json`
`metadata.difficulty`. They must agree exactly.

### Derived-target batches have no easy slot

A topic whose organising principle is "the instruction states a property, never
the entity" is structurally incapable of producing an easy task: easy requires
the entity to be **named outright** and forbids a lookup, while a single
mutation gated on a lookup is **medium** by definition. Two batch-2 authors
independently wrote an "easy" that was really a medium and flagged it; both were
relabelled upward.

If your prompt assigns a derived-target topic, write **5 medium / 5 hard** and
do not pad an easy slot. The site still reaches 5 easy / 20 medium / 25 hard
because its other batches carry the easy quota. **Never relabel a task downward
to fill a slot.** Relabelling upward, when the work genuinely exceeds the label,
is correct — say so in `GENERATION.md`.

## 2. Partial credit — mandatory shape for hard tasks

Every hard task ships `components` that pay out per completed sub-goal and sum
to exactly 1.0, with the untouched initial state still at exactly 0.0.

The gate reads the weights **statically out of the AST**, so `reward.py` must
declare them in a module-level table whose name contains `COMPONENT_WEIGHTS`:

```python
COMPONENT_WEIGHTS = {
    "label_created": 0.2,
    "milestone_created": 0.2,
    "issue_filed": 0.3,
    "neighbour_untouched": 0.3,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9
```

and then build `components` from that table rather than repeating literals:

```python
def evaluate(evidence):
    state = _current_state(evidence)
    checks = score_state(state)          # {name: bool}
    components = [
        {"name": name, "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
         "details": ...}
        for name in COMPONENT_WEIGHTS
    ]
    return {"score": round(sum(c["score"] for c in components), 6),
            "components": components}
```

`nemo_reward.py` must implement the **same** rubric and print
`REWARD: <float>` on **every** output path including its error path.

Medium and easy tasks are strongly encouraged to use the same shape. It is
required only for hard.

## 3. Do not duplicate batch 1

Read all 50 lines of your site's batch-1 inventory before designing anything.
It is in your prompt and also at `output/batch1_inventory/<site>.txt`.

A candidate is a **duplicate** — reject and replace it — if any of these hold:

1. Its `task_id` collides with a batch-1 `task_id`, or anything already in
   `output/tasks/`.
2. It exercises the same *primary mutation* on the same *primary entity* as a
   batch-1 task, with only the entity instance, field value, or wording changed.
   "Rename forum X" vs "rename forum Y" is a duplicate. So is "add product Z to
   cart" vs "add product W to cart", and "hold order 000000002" vs "hold order
   000000005".
3. Its success criteria are a subset of a batch-1 task's success criteria.
   Extending a batch-1 flow with one extra trivial step does not make it new.
4. Its instruction is a paraphrase of a batch-1 instruction (same verbs, same
   nouns, reordered).

You **may** re-touch an entity type batch 1 touched — the mocks are finite — but
only when the *shape* of the work is new: a different handler, a different
multi-step composition, a cross-cutting constraint, a lookup that determines
which entity to act on, or an ordering requirement batch 1 never imposed.

## 4. Lessons from batch 1 — inherit these, do not rediscover them

These are already-paid-for findings.

- **reddit** `moderates()` reads only `state.moderatorOf` (`AppContext.jsx:308`),
  which is **empty** on the pristine seed. Any moderator-only route on a seeded
  forum needs `moderatorOf` injected in `initial_setup.py` or it 403s.
- **reddit** `ForumDeletePage` allows deletion only when
  `admin || (moderates(forum) && submissionCount == 0)`, and no seeded forum has
  zero submissions. `forums` is a single state key — setups must read the
  pristine seed from `/go`, patch it, and `set` the whole state back.
- **shopping**: "choose a shipping method" is not a real choice (one pre-checked
  Flat Rate row). **Never assert `cart.items` after Place Order** — it empties
  the cart. `submitReview` stores the star rating as a plain 1–5 Number and the
  form's "summary" field as `title`.
- **shopping_admin**: the category-tree Delete uses the mock's only native
  `window.confirm` (`src/pages/catalog/CategoryPage.jsx:201`); reddit message
  delete also confirms. Replay drivers must accept the dialog.
- **shopping_admin** `applied_at` is wall-clock — assert only "became a non-empty
  stamp", which usefully also enforces create-then-apply ordering.
- **gitlab**: group milestones are read-only rollups; there is no
  `/dashboard/labels` route; label delete deliberately does **not** rewrite
  `issues[].label_ids` (milestone delete does); import-project is notice-only and
  transfer-project renders `disabled`.
- **Known-unsupported, already rejected — do not spend time on them**:
  Invite-a-group, Remove-a-group-share, Import-members, Import Tax Rates (needs
  a client-side file upload), review edit/delete on the storefront, reddit user
  flair (`userFlag` has only a `(none)` option), confirm-account-deletion.

### Findings from batch-2 authors (already paid for — do not rediscover)

- **gitlab** `ui.dismissedAlerts` is seeded (`src/utils/initialState.js:92`) but
  **never written** — no `setUi` writer exists anywhere in `src/`, and no banner
  in this mock is dismissible. Dead surface.
- **gitlab** `ProfileKeys.addKey()` allocates `id = list.length + 1`, which
  collides once two or more SSH keys exist, and `removeKey` filters by id — so a
  collision deletes two rows. Seed exactly one key if you touch SSH keys.
- **gitlab** `resetFeedToken()` uses a native `window.confirm`.
- **gitlab** derivations that look usable but are **dead on this seed**:
  `upvotes` is `0` on all 19,705 issues and `draft` is `false` on all 23,236
  merge requests (so `?sort=popularity` is inert and "the only draft MR" does not
  exist); **no project has `archived: true`**; milestone due dates are
  near-degenerate (four of a11yproject's six share `2019-12-31`). The *labels page*
  shows no per-label issue counts — but the issue-list **tab badges are
  filter-aware** (see below), so a label count IS readable. An earlier version of
  this brief said otherwise; that claim was wrong and is retracted.
- **gitlab** `NewFile`'s "Start a new merge request" checkbox is **inert** —
  `FileEditor` passes `startMr`, but `NewFile.commit()` never uses it, so no MR is
  created. Changing the target branch *does* create the branch, so the file-editor
  route is still usable for branch work. No task may depend on that checkbox.
- **gitlab** a tag records `{name, sha, date, message}` with **no ref**, and a
  freshly cut branch shares its parent's head sha — so "the tag was cut from branch
  X" is genuinely unobservable. Score the tag's name and message instead.
- **gitlab** the MR detail page has **no to-do control** — `IssueDetail.jsx` has
  `[data-testid="sidebar-todo"]`, `MergeRequestDetail.jsx` does not.
- **shopping** `publishInitialState()`
  (`src/utils/dataManager.js:210`) is exported but **never called anywhere in
  `src/`**. SCHEMA.md 2.3's claim that the app republishes a corrected `/go`
  baseline after a partial inject does **not** hold in the shipped tree: after
  the first browser mutation, `state_diff` reports defaulted keys as phantom
  changes. **Read `current_state`, never diff against `initial_state`.** This is
  the safest reward shape on every mock, not just shopping.
- **shopping** the review form's star radios are **unclickable directly** —
  `Rating_5`'s Luma sprite label intercepts pointer events for every lower star. A
  replay driver must click `label.rating-N` (or `check(..., force=True)`). This
  cost one batch a replay failure before it was diagnosed.
- **shopping** `saveAddress` is **asymmetric**: ticking a default box writes
  `customer.default*` *and* clears that flag on every other record, while leaving
  it unticked writes `false` onto the saved record only and leaves the pointer
  alone. That asymmetry is what makes "the other default must not move"
  checkable. It also means **no task should demote a default**: unticking leaves
  `isDefaultShipping: false` on a record `customer.defaultShipping` still points
  at, and the Address Book still renders it as the default — a self-contradictory
  end state.
- **shopping** `AddressEditPage` stores an empty Company as `null`, not `""`
  (`company: form.company.trim() || null`), so a Company reward must compare
  trimmed text and must not treat `null` as an empty-string match.
- **shopping** `ComparePage` prices resolve from the catalog at render time, not
  from the stored compare record; `reorder` re-prices from `finalPrice(product)`
  rather than the historical order line, so any arithmetic over a reorder must
  first confirm the products carry no `specialPrice`.
  `/<url_key>.html?review_page=1` deep-links the Reviews tab.
- **shopping** order-view line items render as `<strong>`, not links
  (`OrderViewPage.jsx`) — reaching a PDP from an order needs the SKU column plus
  search. Say so in the instruction if your flow requires it.
- **reddit** forum sidebars show only `subscriberCount`, which is `0` everywhere
  in the seed, so any busiest/quietest-forum derivation must route through
  `/forums`.
- **reddit** `forumRenames` is applied only at **materialization** — a rename does
  *not* rewrite `newSubmissions[].forum`. This asymmetry is what lets a rubric tell
  a genuine republication apart from a rename-in-place, and it will bite any reward
  that keys off `submission.forum`.
- **reddit** `createForum` writes tags in a **second `editForum` pass**, and a forum
  created with an empty Tags box has **no `tags` key at all** (not `[]`). It also
  auto-subscribes and auto-mods the creator, so any exact-set assertion on
  `subscriptions` / `moderatorOf` after a creation step must include the new forum.
- **reddit** number rendering is **not uniform**, which decides whether an audited
  value has one defensible string: `formatScore` is ungrouped, but
  `submissionCountLabel` groups — so a four-digit *forum count* has two defensible
  renderings while a four-digit *score* has one. Negative scores render with
  **U+2212 MINUS**, not a hyphen, so any negative extreme is inherently ambiguous.
  Pick facts whose rendering is unambiguous.
- **reddit** the forum settings and appearance forms unconditionally write `tags`
  / `backgroundImageMode` / `suggestedTheme`, **none of which exists on any seeded
  forum** — so the *absence* of those keys is an exact "this form was never saved"
  detector. That is the constructive flip side of the no-op-save rule above: when a
  handler writes unconditionally, absence becomes an exact untouched test.
- **reddit** `vote()` is the only writer that can create a
  `submissionEdits`/`commentEdits` entry on an otherwise-untouched record, so
  "no overlay entry" is an exact untouched test for vote tasks.
- **reddit** `ForumEditPage` unconditionally writes `tags: []` on save (note the
  contrast with `createForum`, which omits the key entirely when Tags is empty).
- **reddit** `addComment` **auto-upvotes the agent's own comment**, so any
  "no votes were cast" assertion must whitelist it.
- **reddit** a submission's `url` is never rendered as text — only as the title
  `href` plus a domain chip — so "copy the link somewhere" is unsolvable.

Native `window.confirm` sites found so far: the admin category tree
(`src/pages/catalog/CategoryPage.jsx:201`), reddit message delete, and gitlab
`resetFeedToken()`. A replay driver must accept the dialog.

- **shopping_admin** **`customers.json` rows DO carry a `name` key** — all 70 of
  them. An earlier batch-2 note claimed otherwise; that claim is **wrong and
  retracted**. Do not use `"name" not in row` as a never-saved detector: it makes a
  *correct* replay score 0.7. The real detectors are `assistance_allowed` /
  `sendemail_store_id`, which `CustomerEdit.save()` writes and which are absent from
  every seed row, plus the seeded `updated_at`. (Two seeded customers are still both
  named "Jane Smith", entities 10 and 15, so keying on the name remains wrong for a
  different reason.)
- **`hashlib` is NOT in `cua_gym_web.reward.ALLOWED_IMPORTS`.** The allowed set is
  exactly: `collections`, `datetime`, `decimal`, `fractions`, `json`, `math`, `re`,
  `statistics`, `urllib.parse`. For content equality on a large body, inline your own
  fingerprint (e.g. a 64-bit FNV-1a `length:digest`) rather than importing a hash.
- **shopping_admin** the sticky header overlays `#block_is_active` — toggle it with a
  keypress, not a click.
- **shopping_admin** SCHEMA.md **overstates the Tax Rule form**: it claims Save
  Rule writes `taxConfig.calculations`, but the form carries only Name / Priority /
  Calculate Off Subtotal Only / Sort Order (`SystemForms.jsx:244-345`) and never
  links a rate. Do not build a task on tax-rule/rate linkage.

### A no-op save is a real state mutation — gate on the VALUE, not on "was edited"

The single most dangerous reward bug found in batch 2, and it is not
site-specific. Several save handlers write unconditionally:

- gitlab `ProjectSettingsGeneral.saveNaming` always writes `topics: []` (no
  seeded project carries `topics`);
- gitlab `NewLabel`'s edit branch always rewrites `updated_at`;
- reddit `ForumEditPage` unconditionally writes `tags: []`.

So `projectEdits.<id>` / `labelEdits.<id>` / the forum record **appear in the
diff even when the agent changed nothing**. A rubric that asks "was this record
edited?" hands out partial credit to an agent that merely opened a form and
pressed Save. One author's first cut leaked 0.2-0.4 that way and caught it only
by driving the probe in a browser.

**Never gate a component on "the record was touched". Always gate it on the
recorded value being exactly right** — and for an exclusion constraint, on the
neighbour's *values* still being exactly what they were.

### gitlab `issuableStateCounts` is filter-aware

`IssuableListBody`'s local `counts` object is pre-filter, which reads as "a label
filter does not change the tab badges" — but `IssuesList` / `MergeRequestsList`
pass `hooks.js issuableStateCounts(rows, q, indexes)`, which re-filters with
`state` forced to `all`. So "how many issues carry label L" is a **readable
badge**, not a manual row count. Related: the Branches and Tags pages carry no
counts at all — the overview `.project-stats` row is the only place they render;
the new-issue label multi-select keeps its menu open by design and overlays the
Create issue button; and the MR title is only reachable via
`[data-qa-selector="title_content"]`.

### Systemic issue 2 — permanently gated, do not reintroduce it

`json.dumps` emits bare `true` / `false` / `null` into Python source. Those are
valid Python *identifiers*, so the program compiles cleanly, passes every static
check, and then raises `NameError` the moment NeMo runs the episode. Inline JSON
fixtures with `json.loads("""…""")`, never `json.dumps`. The gate AST-scans both
episode programs for this.

### Systemic issue 3 — inline JSON escapes eaten by a non-raw string literal

The sibling of issue 2, found in batch 2. A fixture inlined as
`json.loads("""...""")` has its backslash escapes rewritten **by the Python
parser** before `json.loads` ever sees them. A fixture's `\\b` collapses to
`\b`, which JSON then reads as a backspace — so the program compiles, the JSON
often still parses, and the value is silently wrong. In the case that found this,
a cart rule's `conditions_serialized` broke `json.loads` outright at episode time.

**Always prefix an inlined JSON literal with `r`:** `json.loads(r"""...""")`.

*Generation trap while doing this:* do not quote that call **verbatim inside a
module docstring** — the inner triple quote closes the docstring and every bundle
then fails the gate with `initial_setup does not compile`. One author lost a full
pass to exactly this. Describe the rule in prose, or use single quotes, in any
docstring.
The gate now evaluates every `json.loads()` string literal, reports one that does
not parse, and reports a non-raw literal containing a backslash.

**Execute every `initial_setup.py` you write against a live throwaway sid**
before you call the batch done — `compile()` is not enough. After the POST,
`GET /go?sid=` must show `state_diff == {}` and `initial_state == current_state`.

### Flakiness — a flaky task is a failed task

Batch 1 shipped one flaky task (`shopping_wishlist_compare_direct_add_url_006`,
replay 1.0x5 / 0.0x1). Batch-2 rewards must **not** depend on timing, on
ordering the UI does not guarantee, or on add-to-cart-by-URL races. If a reward
could score differently on two identical correct runs, redesign it.

## 5. Non-negotiables that break downstream

- **One app per task.** `CuaGymTaskInfo` carries exactly one `app_dir`. Reject
  cross-site candidates rather than emitting an invalid row.
- The untouched initial state must score exactly `0.0`; a correct completion
  must score exactly `1.0`.
- `reward.py` and `nemo_reward.py` must implement the *same* rubric.
- Setup and reward code must be self-contained single programs using only the
  standard library plus `requests`, must contain `__CUA_GYM_SID__` and the exact
  `__CUA_GYM_WEBARENA_<APP>_URL__` placeholder from `PLACEHOLDER_MAP`, must hit
  `/post?sid=` and `/go?sid=` respectively.
- If pristine hub state suffices, `initial_setup` may be `null` in the NeMo row
  and `initial_setup.py` must then be **absent**.
- **Never modify anything under `./hub/`.** It is authoritative and read-only.
  If a task cannot be expressed against the mock as it exists, throw the task
  away and write a different one. Never weaken a reward to make it pass.
- Benchmark rows in `webarena_benchmarks/webarena.jsonl` are **inspiration
  only** — sample with `scripts/sample_webarena_inspirations.py`. Never copy or
  lightly paraphrase a benchmark question, entity combination, or reference
  answer. Record `inspiration_ids` in `task.json` metadata, never in the
  user-facing instruction.
- Retrieval-shaped ideas must be rewritten as an observable writeback.

## 6. Output layout

Write bundles **flat** under `output/tasks/<site>/<task_id>/`, one directory per
task (the batch orchestrator globs `<site>/*/task.json`). Your `GENERATION.md`
and `index.json` go under `output/tasks/<site>/_batches/<topic-slug>/` so they do
not pollute the bundle glob.

Each bundle carries: `task_instruction.json`, `task.json`, `reward.py`,
`nemo_reward.py`, `nemo_task.json`, `initial_setup.py` (only when setup is
non-null), and optionally `requirements.txt`.

## 7. Self-check before you report done

Run the gate yourself and paste the result into your final report:

```bash
python3 scripts/preflight_bundles.py output/tasks/<site> \
  --prior-batch webarena_08_18_batch_200/tasks --quiet
```

(Your batch is graded on the whole site directory, so a non-empty site from an
earlier batch may already be present — only your own 10 bundles are yours to
fix.) Report honestly: if a topic cannot yield 10 genuinely distinct tasks, say
so rather than padding.
