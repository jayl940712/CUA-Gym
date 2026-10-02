# Batch 5 — 600 skill-aligned WebArena RL tasks

Batch 5 inherits **all of TASK4.md** except where this file overrides it. Read
TASK4.md first; it is still the contract for style (S3), start_path (S5),
reachability (S6), the ground rules (S7) and the definition of done (S9).

Read `docs/SKILL_TAXONOMY.md` second. It is the reason this batch exists.

## What changed from batch 4, and why

Batch 4 hit every structural target — 600 authored, exact difficulty and style
splits, 95.7% root starts, 566 fully compliant. What it never checked was
whether the tasks exercise the **skills** the benchmark exercises. Alignment
was measured on intent shape and scoring style, both of which a task can match
while training nothing that transfers.

So batch 5 selects tasks by skill chain, and topic becomes only the material
the chain is expressed in.

### Override 1 — difficulty is derived, not quota'd

TASK4 S1 fixed 0 easy / 240 medium / 360 hard. **That quota is withdrawn.**
Difficulty now follows from the skill chain:

* **medium** — 2 skills, at least one retrieval and one action.
* **hard** — 3+ skills, and either two distinct retrievals or one retrieval
  feeding two dependent actions.

`preflight_bundles.py` enforces the agreement between `metadata.difficulty` and
`metadata.skills`. The resulting mix is **reported, not targeted**. Do not
pad a skill list to reach a label; relabel down instead. Aggregate and
bulk-action chains are naturally hard, single-field edits naturally medium, and
the corpus should show that honestly.

### Override 2 — non-duplication is relaxed

TASK4 S2b's four-part duplicate test is **withdrawn**. The objective is
training transfer to the WebArena test set, so resembling an official task is a
feature. Specifically:

* A task may closely resemble an **official benchmark** task. That is the point.
* A task may reuse a skill chain already used in batches 1–4 on a different
  entity or with a different composition.
* Still forbidden: a **duplicate `task_id`**, and a verbatim re-authoring of a
  prior bundle with only a value swapped. Those add rollouts, not coverage.

Skill coverage now matters more than novelty. If a skill is thin in the corpus,
write more of it even if the tasks look alike.

### Override 3 — every bundle records its skills

```json
"metadata": {
  "style": "terse",
  "difficulty": "hard",
  "skills": ["R2", "R3", "A7"],
  "skill_chain": "date-range report -> sum -> write the figure into a CMS block",
  "official_analogues": ["Show the shipping report from August 5, 2022 to March 1, 2023."]
}
```

`official_analogues` must quote a **real intent from
`webarena_benchmarks/webarena.jsonl`, verbatim**. The gate cross-checks against
all 799 indexed intents and rejects paraphrases and inventions. If you cannot
find one, the design is not in-distribution — change the design, do not invent
the citation.

## What is unchanged

* 600 tasks, **150 per site**, four sites, classifieds excluded.
* 450 terse / 150 explicit, balanced per site (TASK4 S3).
* >= 70% at `start_path: "/"`, no site below 60% (TASK4 S5).
* ~180 retrieval-writeback (TASK4 S3.5) — note this is now the *floor*, since
  R5 and R10 chains are retrieval-writeback by construction.
* Click-reachability gate (TASK4 S6), enforced in the orchestrator's agreement
  condition 12.
* Empty-state probe, 0.0 total and per component (TASK4 S9.5).
* Every reward reads `current_state` only.
* Inline JSON as `json.loads(r"""...""")`.
* Never modify `hub/`. Never edit `cuagym/hub_apps.py`. The three prior
  snapshots and `webarena_09_02_hard*` are read-only.

## Precondition injection via `initial_setup.py`

A bundle may ship an `initial_setup.py` that writes the mock's session state
document before the episode opens. This is not new machinery — batches 3 and 4
used it — but batch 5 uses it deliberately to recover skills the seed data
cannot otherwise express, so the rules need stating.

**It runs in both runtimes.** `cua_gym_web/runner.py` executes it for
verification and `cuagym/browser_worker.py:177` executes it before a NeMo
rollout. An injected precondition therefore exists when the agent is trained,
not only when it is graded. Verified, because the opposite would produce tasks
that pass verification and are unsolvable in training.

**It can only reach session state.** Each mock persists a fixed set of
top-level keys — reddit 22, shopping 15, gitlab 41, shopping_admin 44. Anything
imported through a `staticData.js`-style module is bundled at build time and is
unreachable; that file says so itself: *"NOTHING in this file is part of the
session state that is POSTed to `/post?action=set_current`, diffed, and
returned by `/go`."* Most frozen corpora have a matching overlay key
(`productOverrides`, `issueEdits`, `submissionEdits`) and are patched through
it; `reportAggregates` on shopping_admin has none and is genuinely fixed.

**It adds data, never controls.** A missing button stays missing. The shopping
storefront has no cancel-order control anywhere in `pages/`, `components/` or
`context/`, and no amount of injection creates one.

### The worked example

Reddit's 95 seeded forums have no moderators, so forum editing 403s and
moderation was assessed as unreachable. `moderatorOf` is a state key and
`AppContext.jsx:309` gates on it. Injecting `moderatorOf: ["DIY"]` and driving
chromium:

    /f/DIY/edit        -> "Editing forum /f/DIY"   (403 lifted)
    /f/DIY/moderators  -> "Moderators for /f/DIY"  (renders)
    /f/books/edit      -> 403 Forbidden            (negative control)

The negative control is the point: the guard still discriminates, so this is a
genuine data gap rather than a broken gate.

### A writable key is not the same as a key the page reads

The failure mode to avoid is injecting into a real state key and having nothing
change, because the rendering path never consults it. Three verified examples,
all found while planning this batch:

* **gitlab star rankings.** `newStars` is a state key and injecting it looks
  like the way to break the two-way tie at 6 stars that makes "my most-starred
  repo" unusable. It does nothing to the ranking: `pages/hooks.js:357` sorts on
  `p.star_count`, and the `stars` array only drives "is this starred by me" and
  `/-/starrers`. The tie is broken by writing the project record back through
  `projectEdits.<id>` with an adjusted `star_count`.
* **gitlab contributors.** `getContributors()` (`utils/dataManager.js:656`)
  reads `chunk.contributors` from a bundled per-project file and applies **no
  state overlay whatsoever** — its `state` argument only resolves a fork to its
  origin. None of the 41 keys reaches it. Worse, `getCommits()` (`:509`) *does*
  honour `state.repo.commitOverlay`, so injecting commits **widens** the
  existing three-way disagreement between the overview, the Contributors page
  and Repository Analytics instead of closing it.
* **shopping_admin review averages.** On Reviews By Products the review *count*
  recomputes from `getReviews(state)` (`LegacyReports.jsx:721`) while the
  *average* columns come from the frozen `ratingVoteAggregates.json` (`:787`).
  A probe that added three reviews moved the count 4 -> 7 and left the average
  at 65.0000.

**So: trace the read path before designing around an injection, exactly as you
would before designing around a control.** A key in the persisted state
document is necessary and not sufficient.

### Live versus frozen is a per-view property, not a per-page one

On shopping_admin, six reports recompute from session state — Order Count,
Order Total, New Accounts, Ordered Products, Reviews By Products (counts) and
Reviews By Customers — while eight read the bundled `reportAggregates` and can
never move: Orders, Tax, Invoiced, Shipping, Refunded, Coupons, Product Views,
Bestsellers. Verified live: injecting reviews moved the Reviews By Products
count and left the Coupons report at "0 records found".

The live half is the more valuable one for task design, because a chain can
make the agent's **own earlier action** change the figure it must then read
back and record — a dependency the official corpus mostly lacks.

### Use injection to make tasks harder and more varied, not just to patch gaps

Injection entered this batch as a repair tool — a way to reach skills the seed
could not express. It is more valuable as a **design** tool, and lanes are
expected to use it that way. Seven things it buys that the seed alone cannot:

1. **Real conditional branches (A13).** A conditional over a fixed seed is
   theatre: the branch is the same every episode, so the agent learns the
   answer rather than the check. Inject the discriminating state and the agent
   genuinely has to read before it acts. This is the single biggest gain, and
   A13 is 1-2% of the official corpus precisely because it is hard to author.
2. **Distractors.** A near-miss entity that satisfies every part of the filter
   but one turns a superlative from "eyeball the list" into "apply the
   predicate". Raises difficulty with no change to the UI and no change to the
   instruction.
3. **Controlled margins.** A tie is unusable and a 10x gap is trivial. Injection
   sets the margin deliberately — close enough to require reading, wide enough
   to be unambiguous. Record the margin either way.
4. **Multi-entity setups (hard criterion 1).** Three or more records to mutate,
   arranged so they are genuinely distinct rather than three clicks on one page.
5. **Ordering dependencies (hard criterion 3).** Arrange state so step N really
   does unlock step N+1, instead of the ordering being merely suggested by the
   sentence.
6. **Instance variation that changes the answer.** Batches 1-4 varied instances
   by swapping the entity, which leaves the reward shape identical. Varying the
   *injected precondition* gives the same chain a different correct answer and
   a different rubric, which is a much stronger form of diversity for the same
   authoring effort.
7. **Tie-breaking that reopens whole families.** Reddit's "most controversial"
   is a ~10-way tie at netScore 0 in nearly every forum and gitlab's
   "most-starred own project" is a two-way tie at 6. Both are dead as seeded and
   both are one injection away from usable.

**The constraint that makes this safe.** An injected precondition must never
pre-satisfy any part of the rubric. This is already enforced structurally —
TASK4 S9.3 requires the initial lane, which runs `initial_setup.py` first, to
score **exactly 0.0** — so a task that injects part of its own answer fails
verification rather than shipping. Note this is a *stronger* guarantee than the
empty-state probe (S9.5), which only proves the reward does not pay on `{}`.
Both apply.

A second-order benefit worth naming: because the precondition is injected
rather than seeded, the frozen seed alone cannot satisfy the rubric. That
closes the batch-3 failure where a helper fell back to the seed row and graded
the seed.

**What it must not become.** Injection that reshapes the site into something
the live WebArena deployment never looks like trains behaviour that fails on
the real evaluation. The test is unchanged: would this state be plausible on
the real site on an ordinary day? Three forum moderators, yes. A forum with
40,000 subscribers when every other forum has zero, no.

### Partial-`set` semantics differ PER MOCK — check yours

Verified on reddit: posting `{"action": "set", "state": {"moderatorOf": ["DIY"]}}`
does not merge into the seeded document — it *becomes* the initial state. A
single forum rename afterwards then reported all 22 top-level keys as changed,
because every other key had been established as absent.

Two consequences:

* **`state_diff` is unusable after a partial set.** Anything reading it grades
  noise.
* **Seed the full state document in `initial_setup.py`**, or write the reward so
  it only ever reads `current_state`.

**But this is reddit's behaviour, not a universal one.** On the shopping mock,
`{"action": "set"}` really is a top-level shallow merge over
`createInitialData()` (`vite.config.js:441-449`), so a partial patch there is
safe and leaves the rest of the seed intact.

All four are now measured:

| mock | `{"action":"set"}` behaviour |
|---|---|
| reddit | **REPLACES** — `initial_state` becomes the partial object |
| shopping | shallow-merges over `createInitialData()` (`vite.config.js:441-449`) |
| shopping_admin | shallow-merges over `createInitialData()` (`vite.config.js:371-377`) |
| gitlab | unmeasured — check before relying on it |

**Reddit is the odd one out**, and it is the mock the original finding came
from, which is why the rule read as universal. Note that even where the merge
is safe it is *shallow*: a nested key like `systemConfig.variables` still
requires re-posting `systemConfig` whole, so read it back from `/go` and patch
rather than inlining a partial object.

The safe course is unchanged regardless of which mock you are on: TASK4 S7
already requires every reward to read `current_state` only and never diff
against `initial_state`, so a conforming reward is immune to this by
construction. It is recorded because the failure is silent, it looks
like a reward bug rather than a setup bug, and the natural way to write an
injection — patch the one key you care about — is exactly the way that triggers
it.

### The action must not destroy its own retrieval premise

New hazard, and it is specific to the live-report family — which is the family
this batch most wants to build, so read it before designing one.

When the agent's action changes the very figure the task asks it to derive, the
derived target can stop being derivable. Worked example, verified against the
seed:

> "Cancel the pending orders of the customer with the most non-canceled orders,
> then record their new order count."

Grace Nguyen leads with 10 non-canceled orders at a **margin of 1**. Cancelling
her three pending orders (65, 307, 308) drops her to 7 — and the leaderboard
she was identified by now has a **three-way tie at 9**. An agent that re-derives
"the top customer" at any point after acting gets a different, ambiguous answer,
and a reward that re-derives it grades something the instruction never asked
for.

The fix is not to abandon the shape. It is to **name the entity in the
instruction whenever the action changes the ranking that selected it**, and to
move the derivation to something the action does not disturb. The chain stays
`A10 -> R10 -> R3 -> A7`; only the selection step changes.

**Check for this whenever the chain's action and its retrieval touch the same
collection.** Ask: after step N executes, is step N-1's answer still the same?
If not, either pin the target by name or pick a different derived value. Record
the check in GENERATION.md — this is not visible in any static gate, and a
verification run will happily pass a replay that hardcodes the right answer.

### Three rules for using it

1. **Stay inside the live site's capability envelope.** Real Postmill has forum
   moderators and the real byteblaze moderates forums, so injecting that moves
   us toward the benchmark. Inventing state the live site never has trains
   behaviour that fails on the actual evaluation — the exact opposite of the
   point of this batch.
2. **An injected record must be plausible against the ordering the page
   applies**, not merely against its schema (TASK4 S10.6). A batch-3 post dated
   2023-01-17 landed on page two of a profile that pages at 25 by recency and
   was genuinely invisible to the agent.
3. **Record what was injected and why**, in `GENERATION.md` and in
   `metadata.injected_preconditions`. Injection changes what the task is
   evidence of: with moderator rights injected, the task measures moderation
   given rights, not the acquisition of rights. That is legitimate and it must
   not be silent.

## Authoring rules carried over from batch 4 because they worked

1. **Authors run no validation code.** Do not run `preflight_bundles.py`,
   the reward validator, `check_reachability.py`, or any driver analysis while
   authoring. Write the bundle and stop. Validation is a separate phase and
   running it inline was the single largest cost in batch 4's authoring wave.
2. **Authoring concurrency 12**, verification concurrency 12.
3. **Never modify a bundle that has a live verification run directory.** The one
   genuine `failed` entry in batch 4 came from exactly this.
4. Read a lane's quota from `_b5_lane_facts.py`, never from a hardcoded number
   in the prompt. Batch 4 shipped six prompts with the wrong split.
5. Verdict status comes from the status script, never from `grep '^## Verdict'`
   — a bare heading matches and reports a real PASS as unresolved.

## Composition standard

The taxonomy's rule, restated because it is the thing most likely to be
violated at scale:

> `R8 -> A2` — find the right forum, then create a well-formed post there — is
> a real errand. `R10 -> A6` — run a sales report, then edit a size/colour
> matrix — is two unrelated chores stapled together, and an agent that learns it
> learns nothing transferable.

**The test: would a real person ever have this as one errand?** If the two
halves share no subject, the chain is artificial. Say so in GENERATION.md and
write a different one.
