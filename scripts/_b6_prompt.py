#!/usr/bin/env python3
"""Emit an authoring-lane prompt from output/wave_plan.json.

Every lane prompt is generated, never typed. Batch 4 shipped six hand-written
prompts carrying a style split that was wrong for those lanes, and the authors
who trusted the prompt over the quota checker had to be repaired.

    python3 scripts/_b6_prompt.py 17
"""
import json
import sys
import pathlib
import textwrap

PLAN = json.loads(pathlib.Path("output/wave_plan.json").read_text())

TEMPLATE = """\
Author {n} new WebArena RL task bundles for the **{site}** mock, lane {index}.

Working directory: /home/ubuntu/CUA-Gym

## Read first, in this order

1. `output/BATCH6_CONTRACT.md` — what batch 5 is and what it overrides.
2. `docs/SKILL_TAXONOMY.md` — the R/A skill ids. Your lane is an assignment
   from this file.
3. `TASK4.md` sections 3, 5, 6, 7 — still binding: terse style, the
   `start_path` contract, click reachability, the ground rules.
4. `webarena_08_21_batch_600_easy/AUTHOR_BRIEF.md` — every environment finding
   from four batches. Binding where it does not conflict with the above.
5. **`output/CENSUS_ERRATA.md` — cells in the census that are KNOWN WRONG.**
   Read this before you trust any census claim. Three lanes have already been
   saved by a `CORRECTIONS.md` entry the census still contradicts. **When the
   census and CORRECTIONS disagree, CORRECTIONS wins.**
6. `webarena_09_04_skills/CORRECTIONS.md` — 122 verified findings from batch 5,
   plus `output/CORRECTIONS.md` for batch 6. All still apply.
7. `webarena_09_04_skills/census/{site}.md` — the feasibility study for your site: which
   skills this mock actually supports, with routes, handlers and tie margins.
   It is the most specific document you have. Trust it over your intuition,
   but verify any mechanism claim you are about to depend on.

## Your lane

{facts}

## Every task in this batch is `medium`, and medium is EXACT

**`metadata.difficulty` is `"medium"` for all ten of your tasks, and
`metadata.skills` has EXACTLY two entries: one retrieval, one action.**

Not "at least two". A three-skill task labelled medium is a hard task wearing
the wrong label, and the gate rejects it. There is no hard tier this round.

If a design needs a third step: **split it into two tasks, or drop the step.**
Dropping is usually better — an all-medium batch wants the retrieval to be the
interesting part, not the action count.

What still makes a medium worth solving:

* the **target is derived**, never named in the instruction;
* an agent that skipped the retrieval lands on the wrong entity and scores 0.0;
* the derived value has exactly one correct answer under the seed, with a
  margin you have checked yourself.

That third bullet does most of the work. Two skills is not an excuse for a
thin task — `R1 -> A4` ("add the cheapest thing in this category to my cart")
is medium and still requires a facet, a sort and a tie-free winner.

## The one rule that is new this round

**Choose the task by its skill chain, then find material to express it in.**
Batches 1–4 chose a topic and asked what could be done with it. That produced
tasks that look like WebArena tasks and train nothing WebArena tests.

Your chain above is the assignment. Every one of your {n} tasks must exercise
at least one of its skills, and collectively the lane must exercise all of them.

Compose naturally. The test is: **would a real person ever have this as one
errand?** `R8 -> A2` (find the right forum, then post there) passes. `R10 -> A6`
(run a sales report, then edit a size/colour matrix) fails — two unrelated
chores stapled together teach an agent nothing transferable. If your chain
resists a natural composition on some task, say so in GENERATION.md and write a
different task; do not staple.

## Reuse from batch 5 is allowed; repetition is not

`webarena_09_04_skills/` holds 600 verified tasks and four census reports. You
are expected to draw on them — entities, verified margins, injection recipes,
and the 122 findings in `CORRECTIONS.md` all still apply.

What you must not produce is a batch-5 task with a value swapped. The
difficulty change is your natural safeguard: batch 5 is 72% hard, so the
2-skill core of one of its chains is already a different task with a different
rubric. Where you reuse an entity, **change what is derived or what is
written** — not merely which row.

Record `metadata.derived_from` naming the batch-5 task yours is adjacent to,
or `null` for new ground. It is an honesty aid, not a restriction.

## Do NOT run validation code

Write the bundles and stop. Specifically, do not run:

* `scripts/preflight_bundles.py`
* `scripts/check_reachability.py`
* `scripts/empty_state_probe.py`
* `cua_gym_web.reward.validate_reward_source` or any reward import/exec probe
* any driver, replay, or Playwright analysis

Validation is a separate phase with its own agents and it will catch what you
miss. Running it inline was the largest single cost in batch 4's authoring wave
and it did not improve the bundles. Use Bash only to READ the mock source and
seed data.

## Output layout

Bundles: `output/tasks/{site}/<task_id>/` — one directory per task, named for
the task.

**The directory name MUST equal `task_id` exactly, and `task_id` MUST begin
with your lane slug `{slug}`.** The gate fails a bundle whose id and directory
disagree, and the lane-quota checker finds your bundles by globbing
`{slug}_*`, so an id that starts with anything else is invisible to it.

Valid:   `{slug}_001`, `{slug}_wcag_levels_a11yproject_001`
Invalid: `gitlab_{slug}_wcag_levels_001` (does not start with the slug)
Invalid: directory `{slug}_001` holding `task_id: "{slug}_wcag_001"`

A descriptive middle section is encouraged — it is how a reviewer tells ten
bundles apart — but keep the `_NNN` suffix, 001..{n:03d}.

Each bundle holds exactly these five files:

    task_instruction.json   task_id, task_instruction, app_dir, start_path,
                            difficulty, success_criteria
    task.json               the WebTaskManifest, incl. the metadata block below
    reward.py               evaluate(evidence) -> {"score", "components"}
    nemo_reward.py          the state-only twin; rubric parity with reward.py
    nemo_task.json          the NeMo-Gym rollout row

Plus `output/tasks/{site}/_batches/{slug}/GENERATION.md` and, for each task,
a golden replay draft at `output/tasks/{site}/_batches/{slug}/replays/<task_id>.py`.

### The metadata block, which the gate enforces

```json
"metadata": {
  "style": "terse",
  "difficulty": "medium",
  "shape": "retrieval_writeback",
  "skills": ["R2", "A7"],
  "skill_chain": "read the dated report -> write the figure into a CMS block",
  "derived_from": "<batch-5 task_id this is adjacent to, or null>",
  "official_analogues": ["<verbatim intent from webarena.jsonl>"],
  "injected_preconditions": ["<what state was written and why>"]
}
```

`official_analogues` is cross-checked against all 799 official intents. Quote
it **verbatim**; a paraphrase is rejected and an invented one is worse than
admitting the design has no analogue. The analogues suggested for your lane are
above — use them, or find better ones in `webarena_benchmarks/webarena.jsonl`.

## Non-negotiables (TASK4 S7, unchanged)

* Every reward reads `current_state` only. Never diff against `initial_state`.
* Terse rewards pay only for what the model MADE TRUE. Assert the exact
  resulting collection ("subscriptions are now exactly [X]"), never
  "Y was left untouched".
* Gate on the recorded VALUE, never on "the record was edited" — several
  handlers write unconditionally.
* Inline JSON fixtures as `json.loads(r\"\"\"...\"\"\")`. Raw string, always.
* `json.dumps` leaves bare `true`/`false`/`null` in Python source: it compiles
  and raises NameError at episode time. Write Python literals.
* Allowed imports are exactly: collections, datetime, decimal, fractions, json,
  math, re, statistics, urllib.parse. `hashlib` is NOT importable.
* `start_path` defaults to `"/"`. Every scored control must be reachable from
  it by clicking rendered links and buttons. No typed URLs in the replay. "The
  agent would waste turns finding it" is not a reason to deep-link — that
  navigation is the task.
* Never modify anything under `hub/`. Never edit `cuagym/hub_apps.py`.

## Use `initial_setup.py` to make the task harder, not just to fix data

A bundle may ship an `initial_setup.py` that writes the mock's session state
before the episode opens. It runs in BOTH the verification harness and the NeMo
training runtime (`cuagym/browser_worker.py:177`), so an injected precondition
exists when the agent is trained, not only when it is graded.

Reach for it deliberately. It is the cheapest way to raise difficulty:

* **Give a conditional branch something real to branch on.** A conditional over
  the fixed seed is theatre — the branch is identical every episode, so the
  agent memorises the answer instead of reading the state.
* **Plant a distractor** that satisfies every part of the filter but one. Turns
  a superlative from "eyeball the list" into "apply the predicate".
* **Set the margin.** A tie is unusable, a 10x gap is trivial. Choose it.
* **Break a tie that kills a whole family** — the "most controversial post"
  (~10-way tie at netScore 0 in nearly every forum) and gitlab's most-starred
  own project (two-way tie at 6) are both one injection away from usable.
* **Vary the injected precondition instead of the entity.** Swapping the entity
  leaves the reward shape identical; changing the precondition gives the same
  chain a different correct answer and a different rubric.

Three constraints:

1. **Never inject anything that pre-satisfies part of your rubric.** The initial
   lane runs `initial_setup.py` and must still score exactly 0.0, so this fails
   verification rather than shipping — but it wastes a whole verification round.
2. **Trace the read path first.** A writable key is not a key the page reads.
   Injecting gitlab `newStars` does not move any ranking (`hooks.js:357` sorts
   on `p.star_count`; write `projectEdits.<id>` instead), and gitlab's
   contributor data is behind no overlay at all.
3. **Stay plausible.** Would this state exist on the real site on an ordinary
   day? Three forum moderators, yes. One forum with 40,000 subscribers when
   every other has zero, no. And an injected record must sit where the page's
   own ordering will show it — check the default sort and the page size.

**Write every `initial_setup.py` as a read-modify-write.**

Do not spend time deciding whether your mock merges — five lanes have now read
`dataManager.js mergeOverDefaults` and concluded "it merges, a partial is safe".
**That function runs in the BROWSER.** It refills omitted keys as the SPA
renders, so the site looks fine. It has no effect on what `/go` returns, and
`/go` is what the reward reads.

Measured on gitlab: POST a one-key `set`, and `<sid>.json` on disk holds **1
key**, `/go` returns **1 key**, down from 41. gitlab and reddit REPLACE;
shopping and shopping_admin merge. You do not need to know which you are on if
you read-modify-write. A partial post on a replacing mock leaves the agent
looking at a working site while the reward reads an almost-empty document — the
replay passes and the rubric grades nothing. Use:

    GET  /go?sid=<sid>          -> full current_state
    mutate that document in place
    POST /post?sid=<sid>  {"action": "set", "state": <whole document>}

and fail loudly if `/go` returns neither `current_state` nor `initial_state`.
This is correct on all four mocks.

Record every injection in `metadata.injected_preconditions` (the gate requires
it whenever `initial_setup.py` is present) and explain the reasoning in
GENERATION.md.

## gitlab only: do not assume the default branch is `main`

**134 of the 175 seeded projects have a default branch that is NOT `main`**,
including four of byteblaze's own: `cloud-to-butt`, `timeit`,
`solarized-prism-theme` and `millennials-to-snake-people` are all `master`.

This is a silent scorer. `NewFile` takes `params.ref` verbatim and does not
validate it, so `/-/new/main` renders happily on a `master` repo — and the
commit then lands at `<full_path>:main:<file>`, an overlay key on a branch the
repo does not have. The file is invisible on the default branch, and a reward
keyed on the wrong ref scores a **correct** run 0.0.

Read `default_branch` out of `src/data/projects.json` for every repo you touch,
and key `repo.fileOverlay` on that value. If a task deliberately commits to a
non-default branch (the official corpus has several such intents), say so in
GENERATION.md so a reviewer does not read it as this bug.

## reddit only: "newest" has two defensible readings

`/f/<forum>/new` sorts by **id descending** (`listing.js:34`), not by timestamp.
Those two orders disagree at the head of **59 of the 95 forums**. In `f/DIY`
the `/new` head is id 119019 dated 2023-03-31 19:01, while id 118903 is dated
23:55 the same day — later, but lower id.

This matters because `Time.jsx:12` puts absolute datetimes in the `title` and
`datetime` attributes, so an agent that reads the timestamp and an agent that
takes the first row get **different posts**, and both are defensible readings
of "the newest post".

Draw targets only from the 36 forums where the two orders coincide, or phrase
the instruction so it names which order it means. Tabulate the margin either
way. The tightest coincident margin found so far is `newhaven` at 12 minutes /
1 id.

Related, same cause: `submissions.json` carries a `commentCount` that disagrees
with the number of rows in `comments.json` for at least one post (124607 says
6, holds 5). Score and comment count are also mutated by the episode's own
actions. Prefer author username or submission id as derived writeback content.

## Derived values must have exactly one right answer

Every superlative you use — cheapest, newest, most reviewed, best selling —
must be checked against the seed data **for ties**, and the margin recorded in
GENERATION.md. A three-way tie shipped in batch 4 and was caught independently
by four authors. The census report for your site lists known margins; verify
any you rely on.

## GENERATION.md

Record: the skill chain per task, the tie margins you checked, every mechanism
claim you verified in the source (with file:line), every candidate you
REJECTED and why, and anything in the census report or AUTHOR_BRIEF that you
found to be wrong. That last one is wanted — three prior briefs had claims
retracted by authors who checked, and they were right to.
"""


def facts(index: int, lane: dict) -> str:
    lines = [
        f"skills     : {' -> '.join(lane['skills'])}",
        f"chain      : {lane['chain']}",
        f"entities   : {lane['entities']}",
        f"writeback  : {lane['writeback']}",
        f"tasks      : exactly {lane['n']}",
        f"style      : exactly {lane['terse']} terse, {lane['explicit']} explicit",
        f"start_path : at least {lane['root_min']} of {lane['n']} at '/'",
        f"shape      : at least {lane['retrieval']} retrieval_writeback",
        "difficulty : ALL TEN are `medium`, and medium is EXACTLY two skills --",
        "             one retrieval, one action. Not `at least two`. A 3-skill",
        "             task labelled medium is a hard task with the wrong label",
        "             and the gate rejects it. There is no hard tier this round:",
        "             if a design needs a third step, split it or drop the step.",
        "analogues  :",
    ]
    for a in lane["analogues"]:
        lines += textwrap.wrap(a, 86, initial_indent="  - ", subsequent_indent="    ")
    if lane.get("notes"):
        lines += textwrap.wrap("notes      : " + lane["notes"], 86,
                               subsequent_indent="             ")
    return "\n".join(lines)


for raw in sys.argv[1:]:
    i = int(raw)
    lane = PLAN[i]
    # NOT .format(): the brief contains literal JSON braces ({"action": "set"},
    # {"score", "components"}, the metadata block) and .format() reads every one
    # of them as a field. It raised KeyError and printed a traceback instead of
    # a brief -- silently, because the exit code stayed 0 through the pipe.
    text = TEMPLATE
    for key, value in (("{index}", str(i)), ("{site}", lane["site"]),
                       ("{slug}", lane["slug"]), ("{n:03d}", f"{lane['n']:03d}"),
                       ("{n}", str(lane["n"])), ("{facts}", facts(i, lane))):
        text = text.replace(key, value)
    print(text)
    print("\n" + "=" * 78 + "\n")
