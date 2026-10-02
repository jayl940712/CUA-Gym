# TASK4.md — Generate and verify 600 *new* WebArena RL tasks (batch 4, hard-weighted, benchmark-aligned)

You are running this end-to-end in one session. Work through the phases in
order. Do not ask clarifying questions; the decisions below are already made.

**This is the fourth batch.** Three batches already exist on disk and are
read-only:

| Snapshot | Tasks | Mix |
|---|---|---|
| `webarena_08_18_batch_200/` | 198 verified | mixed |
| `webarena_08_19_batch_200/` | 199 verified | mixed |
| `webarena_08_21_batch_600_easy/` | 600 verified | 83.5% easy |

Everything you generate must be additional to and materially different from all
**three**. That is **997 tasks already spent**, and it is the single biggest
constraint on this batch.

Two things make batch 4 different from everything before it:

1. **The mix inverts again: 0% easy / 40% medium / 60% hard.** Batch 3 was
   easy-weighted by request; this one is the opposite. There is no easy quota to
   fall back on.
2. **75% of the batch adopts a new, WebArena-aligned style** — terse
   instructions, no do-not-touch lists, and rewards that pay only for what the
   model *accomplished*. §3 is the contract for this and is the most important
   section in the document. Read it before designing a single task.
3. **Tasks start at the site's landing page by default.** `start_path: "/"` is
   the norm now, not the exception; ≥70% of the batch must start there. Batch 3
   had 20 of 600. §5.1 — this is a hard requirement, not a preference.

---

## 1. Objective

1. **Generate 600 new verifiable browser RL tasks** — 150 each for
   `webarena_gitlab_mock`, `webarena_reddit_mock`, `webarena_shopping_mock`,
   and `webarena_shopping_admin_mock` — at the difficulty mix
   **0% easy / 40% medium / 60% hard** (240 medium, 360 hard).
2. **Split by style: 450 terse (§3) / 150 explicit (§3.4).** Hold the ratio
   within each site, not just corpus-wide: 112–113 terse and 37–38 explicit per
   site.
3. **Start at least 420 of them (70%) at the site root**, no site below 60% —
   see §5.1.
4. **Verify every one of them** through the `orchestrator` agent — deterministic
   reward generation, a Playwright golden replay, and an independent reward audit.
5. **Export the verified set** as a NeMo-Gym rollout JSONL.

A task counts as delivered only when *verified*, and this batch adds a
**fourth** verification condition that no previous batch had — click
reachability, §6. Read §9 for the full definition of done.

**Two tiers again, and expect the split to be different this time.** Batch 3
delivered 282 templates plus 318 instance variants. Hard tasks are more
composable than easy ones — a hard task chains several mutations, so the space of
distinct chains is much larger than the space of distinct single mutations. Aim
for **at least 400 tier-1 templates** before falling back to variants, and say so
honestly in the final report if you land under that. Tier-2 variants carry
`metadata.dedup_standard: "instance_variant"` and `metadata.variant_of`.

---

## 2. Environment facts (verified through 2026-09-01 — trust these, do not re-derive)

**Hub deployment.** Five mocks under tmux session `cua-gym-hub`, one window each:

| Port | app_dir | Endpoint env var | In scope? |
|---|---|---|---|
| 8000 | `webarena_classifieds_mock` | `CUA_GYM_WEBARENA_CLASSIFIEDS_URL` | **no** |
| 8001 | `webarena_gitlab_mock` | `CUA_GYM_WEBARENA_GITLAB_URL` | yes — 150 |
| 8002 | `webarena_reddit_mock` | `CUA_GYM_WEBARENA_REDDIT_URL` | yes — 150 |
| 8003 | `webarena_shopping_admin_mock` | `CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL` | yes — 150 |
| 8004 | `webarena_shopping_mock` | `CUA_GYM_WEBARENA_SHOPPING_URL` | yes — 150 |

Classifieds must keep working but generate **no** tasks for it. It is also absent
from official WebArena, so excluding it moves us *toward* the benchmark, not away.
There is no map or wikipedia mock in `hub/websites/`, so those two official sites
are out of reach — do not attempt to simulate them.

**Never modify anything under `hub/`.** If a mock behaves oddly, that is a fact
about the environment to design around, not a bug to fix. Record it and move on.
**Do not edit `cuagym/hub_apps.py`.**

**`output/` is in `.gitignore`** and starts empty. Do not `git add -f` it.

**Harness scripts, all committed and current:**

| Script | What it does |
|---|---|
| `scripts/preflight_bundles.py` | the mechanical gate; `--prior-batch` (repeatable), `--difficulty-split E:M:H` |
| `scripts/near_dup_scan.py` | advisory near-duplicate triage |
| `scripts/detect_flaky.py` | cross-attempt consistency sweep |
| `scripts/export_nemo_rollouts.py` | emits verified bundles as rollout JSONL |

`scripts/export_nemo_rollouts.py` now derives `sites` and `start_urls` from
`task.json` — see `docs/NEMO_JSONL_FORMAT.md`, which is binding for the export
format.

---

## 2b. The three prior batches

**Read `webarena_08_21_batch_600_easy/AUTHOR_BRIEF.md` in full before designing
anything.** It carries every environment finding from three batches and is
binding. Where it and this document disagree, this document wins.

Build a prior-task inventory first (Phase 1) covering all three snapshots. 997
tasks is enough that you cannot hold them in your head; you need the file.

### The non-duplication rule

A new task duplicates a prior one if **any** of these holds:

1. **Same `task_id`.** Ids are globally unique across all four batches.
2. **Same primary mutation on the same entity**, with only instance, value, or
   wording changed.
3. **Its success criteria are a subset of a prior task's**, *and* the start state
   is materially equivalent.
4. **It is a paraphrase** — same goal, same controls, different sentence.

**The operative test is an AND, not an OR:** a different line of code must
execute **and** the agent's work must differ. Satisfying only one is a duplicate.

**Batch 4 has a structural advantage here.** A hard task chains 3+ mutations, and
a chain differs from a prior task if *any* link differs. Do not use that as a
licence for lazy composition: gluing two batch-3 easies together is a duplicate
of both unless the composition itself creates a new dependency — one step's
output constraining the next.

---

## 3. The WebArena-aligned style — 450 of the 600

This is the section that makes batch 4 different. It comes from a direct
comparison against `webarena_benchmarks/webarena.jsonl` (812 official tasks).

| | official WebArena | our batches 1–3 |
|---|---|---|
| intent length | mean 18 words, median 16 | mean 89, median 82 |
| instruction content | goal only | goal + click path + do-not-touch list |
| scoring | 50% `program_html`, 40% `string_match`, 8% `url_match` | 100% state-based |
| reward shape | binary | weighted components, incl. preservation |

### 3.1 Terse instructions

Target **25–40 words**. State the goal. Do **not** state:

- which page or control to use, or the click path;
- what must remain untouched;
- values the model can derive from the site itself.

Do still state anything genuinely unknowable from the UI — an external fact the
task depends on ("the vendor's new contact address is X"). The test is: *could a
competent user work this out by looking at the site?* If yes, leave it out.

**Compare.** Batch 3, 71 words:

> Two forums are on my subscribed list, wallstreetbets and LifeProTips, and
> wallstreetbets is also sitting on my hidden-forums list. I am done with
> wallstreetbets entirely, so go to /f/wallstreetbets and press Unsubscribe in
> its sidebar. It has to remain on my hidden-forums page afterwards — do not
> touch Unhide — and my LifeProTips subscription must be left alone.

Batch 4, 12 words:

> I'm done with wallstreetbets — unsubscribe from it, but keep it hidden.

### 3.2 Rewards pay for accomplishment, never for inaction

**Every weighted component must name something the model made true that was not
true at t=0.** A component that pays because something *did not change* is
forbidden in the terse set.

This kills the batch-3 pattern:

```python
COMPONENT_WEIGHTS = {
    "unsubscribed": 0.5,
    "hidden_entry_survived": 0.3,          # FORBIDDEN — pays for inaction
    "other_subscription_untouched": 0.2,   # FORBIDDEN — pays for inaction
}
```

### 3.3 Assert exact end-state, not preserved-vs-changed

Dropping preservation components raises an obvious question: what stops a model
from achieving the goal destructively — deleting every other branch so the target
becomes default? Official WebArena tolerates this, because `program_html` only
inspects named elements. **We do not**, because reinforcing destructive
shortcuts is actively harmful in training.

The resolution is the *shape* of the assertion, not an extra component. Assert
the **exact resulting collection or record**:

```python
COMPONENT_WEIGHTS = {"subscriptions_now_exactly_lifeprotips": 1.0}
# subscriptions == ["LifeProTips"]  -- one positive statement of the end state.
# A model that deleted LifeProTips fails it. Nothing is paid for restraint.
```

This is a genuine constraint on task design, not a formatting rule: **a task is
only suitable for the terse set if its correct end state is exactly specifiable.**
If the honest reward would need "…and forty other things unchanged", the task
belongs in the explicit set (§3.4) or should not be written.

Where a task genuinely has several accomplishments, split the weight across them
— each still a positive end-state assertion:

```python
COMPONENT_WEIGHTS = {
    "mainline_branch_created": 0.3,
    "default_branch_is_mainline": 0.4,
    "master_branch_gone": 0.3,   # allowed: a deletion the task asked for
}
```

Note the third: a deletion the task *requested* is an accomplishment. A deletion
that merely *didn't happen* is not.

### 3.4 The explicit set — 150 of the 600

Batches 1–3's style, unchanged: fuller instructions, preservation components
permitted. Use it for tasks whose end state cannot be exactly specified, and for
the hardest chains where an unguided instruction would be ambiguous rather than
merely difficult.

Every bundle records which set it belongs to:

```json
"metadata": { "style": "terse" }      // or "explicit"
```

The gate checks the 450/150 split and the per-site balance.

### 3.5 Retrieval-then-writeback

40% of official WebArena is answer-retrieval scored by string match. Our
verification harness cannot supply an agent answer — `cua_gym_web/importer.py:152`
rejects such tasks outright as *"answer-only task has no verifiable browser
writeback"* — so a pure answer task **cannot be verified** and must not be
written.

(For the record, the NeMo *runtime* does support it: `terminate(status, answer)`
feeds `CUA_GYM_AGENT_ANSWER` into the reward program at
`cuagym/browser_worker.py:303`. Only the verification side is missing. Do not
attempt to add it in this batch.)

Capture the retrieval skill instead by requiring the model to **find a derived
fact and then record it in the UI**, so the answer lands in persisted state:

- find the highest-rated product in a category, then add *that* product to a list;
- find which of a user's forums has the most subscribers, then post there;
- read a total off an order, then enter it in a refund field.

The scored value must be **derived, not given** — never state it in the
instruction. **Target ~30% of the batch (about 180 tasks) as
retrieval-then-writeback**, spread across all four sites, and label them
`metadata.shape: "retrieval_writeback"`.

Design warning: the derived value must have exactly one correct answer under the
seeded data. Check for ties before you write the rubric — "highest-rated" is
ambiguous if two products share a rating, and a model that picks the other one is
right.

---

## 4. Difficulty — 240 medium, 360 hard

Batch 3 was 83.5% easy, so **the corpus has almost no hard examples and this
batch is where they come from.** Do not let hard tasks drift into medium; the
gate counts labels but only you can police the substance.

**Medium** — two or three dependent mutations, or one mutation whose target must
be derived. A single form save is *not* medium in this batch.

**Hard** — must satisfy **at least two** of the five hard criteria (as batches
2–3; `preflight_bundles.py` enforces the count):

1. **Multi-entity** — three or more distinct records mutated.
2. **Derived target** — the entity to act on is identified by a property that
   must be computed from the page, not named in the instruction.
3. **Ordering dependency** — steps must occur in a specific order because an
   earlier step unlocks or constrains a later one.
4. **Cross-page** — the work spans three or more distinct pages.
5. **Conditional branch** — what to do depends on state the agent must first read.

**Relabel upward, never downward.** If a task you called hard turns out to
satisfy only one criterion, it is medium — fix the label, not the criterion count.
Batch 3 lost time to two authors independently mislabelling derived-target tasks;
that direction of error is the acceptable one.

**Difficulty labels assume the task's `start_path`.** See §5.

---

## 5. `start_path` — a contract, new in this batch

Batch 3 shipped 600 tasks with no guidance on `start_path` at all. It is required
by the schema, so every author filled it in; nobody was told what a good value
was. That produced at least one task whose scored control was **unreachable** from
its own start page. This section exists so that cannot recur.

### 5.1 The default is the site root. Deviating requires a reason.

**Write `start_path: "/"` unless you can state, in the bundle's authoring notes,
why the task cannot work from the landing page.** This reverses the batch-3
default, where a deep link was the unexamined norm and only 20 of 600 tasks
started at the root.

**Target: at least 70% of the batch (≥ 420 tasks) starts at `/`,** and no site
below 60%. The gate reports the distribution per site; a wave that comes in under
it must justify each deep start individually or rework the tasks.

Three reasons this is the right default for batch 4, in order of weight:

1. **It restores the navigation the task is supposed to test.** Batches 1–3
   average 3.4 URL segments — the deepest hands over project, branch, two
   directories and a filename. That is the entire locate-the-thing half of the
   work, given away for free. A hard-weighted batch should not be giving it away.
2. **It makes the difficulty label mean one thing.** Today the verification
   harness honours `start_path` (`cua_gym_web/runner.py:277`) while the NeMo
   runtime hardcodes the root (`cuagym/browser_worker.py:195`), so a deep-start
   task is verified under conditions it will never be rolled out in — easier when
   graded, harder in use. **With `start_path: "/"` the two agree exactly**, and a
   task labelled hard is hard in both. This alone is worth the constraint.
3. **It is closer to the benchmark in the way that matters.** Official WebArena
   supplies a `start_url` too, but its intents demand real search within the site.
   Starting at the root and requiring the model to find its way is nearer to that
   than starting on the answer's own page.

**What counts as a legitimate reason to deviate.** A deep `start_path` is fine
when the task's *subject* is a specific record that the instruction names and the
model could not otherwise be expected to locate unambiguously — a particular order
number among 308, a specific submission among 8,012. Even then, prefer the record's
main page over a sub-form: for a task about order 24, start at the order-24 page,
never at its credit-memo form.

**What does not count:** "the agent would waste turns finding it", "the site
search is awkward", or "the replay is shorter this way". Those are the task.

### 5.2 The rules that apply whatever the start path

1. **The scored control must be reachable from `start_path` by following links
   and buttons that actually render**, with no typed URLs. Verify this, §6.
   Starting at the root makes this check longer, not weaker — the whole path from
   landing page to control must be clickable.
2. **"The control is off-page" is a legitimate difficulty lever only if a click
   path to that page exists.** Batch 3's
   `reddit_co_moderator_standdown_second_page_seat_002` put the Remove button on
   page 2 of a paginated table that renders **no pager at all** — reachable only
   by typing `/f/<forum>/moderators/2`. That is not difficulty, it is a dead end.
3. `start_path` is the page a competent user would begin from. Never a
   deep-linked sub-form they would have to pass through another page to reach.
4. **Difficulty is relative to the start page.** A task is `hard` from where it
   starts, not in the abstract. Moving a start path shallower can turn a medium
   into a hard, and that is a legitimate way to hit this batch's mix — but relabel
   it, do not leave the old label in place.

**Expect this to cost you.** Root starts make replays longer, reachability checks
slower, and some otherwise-good task ideas unworkable because the entity cannot be
found from the landing page by clicking. That is the intended trade: a task that
cannot be reached from the front door is a task the model cannot solve in a
rollout either. Drop it and record it.

---

## 6. The click-reachability gate — new, and mandatory

Three of the four verification conditions in batch 3 tested the *reward*. None
tested whether the task was **solvable through the UI**. That is how the
moderators task shipped: it passed initial 0.0 → replay 1.0, because the golden
replay reached page 2 with `page.goto(_next_page_url(page.url))` — a constructed
URL no user could click to.

**For every task, before it counts as verified:**

1. Run the task's own `initial_setup.py` against a fresh sid.
2. Open `start_path`.
3. Reach and operate every scored control **using only rendered links, buttons,
   and form controls**. No `page.goto()`. No URL construction. No `go_back()` to
   a URL that was never clicked to.

**The golden replay must itself satisfy this.** A replay containing `page.goto()`
after the initial landing is a failed reachability check unless the replay proves
the same destination is clickable and documents why the `goto` is a shortcut for
an already-proven path. Prefer clicking.

If a control turns out to be unreachable, **fix the task, not the check** — move
the start path, pick a different entity, or drop the task. Do not add a typed URL
to the replay and call it verified. Record every task dropped for this reason in
the final report; that count is a finding about the mocks and is wanted.

Write this as a reusable script, `scripts/check_reachability.py`, so it can be
run over a whole batch and re-run later against batches 1–3.

---

## 7. Ground rules

- **Authoring concurrency ≤ 4. Verification concurrency ≤ 12.**
- `--timeout 90 --max-turns 220` for verification. Batch 2 lost a task to the
  120-turn default; batch 4's tasks are longer, so 220 is a floor, not a target.
- **Never relax a reward, delete an agreement condition, or mark a task verified
  on a partial result.** If a task cannot be made to pass honestly, drop it and
  say so.
- **Never modify `hub/`.** Never edit `cuagym/hub_apps.py`.
- The three prior snapshots are **read-only**.
- **Do not commit anything under `output/`.**
- Every reward reads `current_state` only; never diff against `initial_state`.
- Gate on the **recorded value**, never on "the record was edited" — several
  handlers write unconditionally.
- Inline JSON fixtures as `json.loads(r"""...""")` — raw string, always.

---

## 8. Phases

**Phase 1 — Preflight (serial).** Confirm all four endpoints respond. Build the
997-task prior inventory. Read `AUTHOR_BRIEF.md`. Write
`scripts/check_reachability.py` and prove it on three known-good batch-3 bundles
and on `reddit_co_moderator_standdown_second_page_seat_002`, which it must
**fail**. Extend `preflight_bundles.py` with the §3 checks: `metadata.style`
present and the 450/150 split held; terse bundles have intents ≤ 40 words; terse
bundles carry no component whose name or logic encodes preservation.

**Phase 2 — Generate (≤ 4 concurrent).** Per site, per topic. Every bundle passes
the gate before the wave reports done. Every wave reports its terse/explicit
split, difficulty split, and retrieval-writeback count.

**Phase 3 — Verify (≤ 12 concurrent).** `scripts/batch_orchestrator.py`,
resumable. Then `detect_flaky.py`, then the empty-state probe (§9), then
reachability over the whole batch.

**Phase 4 — Export.** `scripts/export_nemo_rollouts.py`, per
`docs/NEMO_JSONL_FORMAT.md`.

---

## 9. Definition of done

A task is **verified** only when all of:

1. `REVIEW.md` carries `## Verdict: PASS`;
2. at least one attempt reports `verification.passed`, and **all attempts agree**
   on initial score, replay score, and verdict;
3. the initial lane scores **exactly 0.0** and the replay lane **exactly 1.0**;
4. **the click-reachability check passes** (§6) — new in this batch;
5. **the reward scores 0.0 on an empty `current_state`.** Batch 3 shipped 27
   rewards that paid out on `{}`, 18 of them a full 1.0, because a helper fell
   back to the frozen seed row or read absence as success. Probe every reward
   with `initial_state = current_state = {}` and require 0.0 total *and* 0.0 per
   component.

Plus, batch-wide:

- 600 bundles, 150 per site, gate green;
- difficulty **0 easy / 240 medium / 360 hard**;
- style **450 terse / 150 explicit**, balanced per site;
- **≥ 420 tasks (70%) with `start_path: "/"`, no site under 60%** — report the
  per-site distribution and justify every deep start that remains;
- ~180 retrieval-writeback;
- `detect_flaky.py` clean, or every flag run down to a cause and explained;
- export written and validated.

**Report honestly.** If the batch lands at 560 verified because 40 tasks failed
reachability, that is a better outcome than 600 with typed-URL replays. State the
shortfall, the reason, and what you would need to close it.

---

## 10. Inherited findings — do not rediscover these

`webarena_08_21_batch_600_easy/AUTHOR_BRIEF.md` is the full list and is binding.
The ones that cost the most:

1. **`json.dumps` leaves bare `true`/`false`/`null` in Python source** — compiles,
   passes static checks, `NameError` at episode time. Gated by `js_literal_names()`.
2. **A non-raw literal eats a JSON fixture's backslash escapes** before
   `json.loads` sees them, often silently. Always `json.loads(r"""...""")`.
   Gated by `broken_inline_json()`.
3. **A no-op save is a real mutation.** gitlab `saveNaming` always writes
   `topics: []`; reddit `ForumEditPage` always writes `tags: []`. Gate on the
   value.
4. **A name read but never bound passes every static check** and fires only on a
   correct replay. Gated by `unbound_names()` — a batch-3 variant shipped with an
   undefined `SEEDED_ORDER_COUNT` and scored a clean 0.0 at t=0.
5. **Absence is not evidence of success** — see §9.5. The most expensive lesson of
   batch 3.
6. **An injected record must be plausible against the *ordering* a page applies**,
   not just its schema. A batch-3 post dated 2023-01-17 landed on page two of a
   profile that pages at 25 by recency, and was genuinely invisible.
7. **`/go`'s `initial_state` is the pristine seed**, not a browser mirror — the
   server computes `initialState || defaultState` and `GoPage.jsx` is shadowed by
   `server.middlewares.use('/go', …)`. Read `current_state`.
8. **Verify in a browser, not offline.** Every finding that mattered in batches
   2–4 surfaced in a real chromium replay.

Treat any *mechanism* claim — including in this document — as unverified until
you have read the handler yourself. Two claims in batch 2's brief and one in
batch 3's were retracted after authors checked the source and were right to.
