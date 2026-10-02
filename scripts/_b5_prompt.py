#!/usr/bin/env python3
"""Emit an authoring-lane prompt from output/wave_plan.json.

Every lane prompt is generated, never typed. Batch 4 shipped six hand-written
prompts carrying a style split that was wrong for those lanes, and the authors
who trusted the prompt over the quota checker had to be repaired.

    python3 scripts/_b5_prompt.py 17
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

1. `output/BATCH5_CONTRACT.md` — what batch 5 is and what it overrides.
2. `docs/SKILL_TAXONOMY.md` — the R/A skill ids. Your lane is an assignment
   from this file.
3. `TASK4.md` sections 3, 5, 6, 7 — still binding: terse style, the
   `start_path` contract, click reachability, the ground rules.
4. `webarena_08_21_batch_600_easy/AUTHOR_BRIEF.md` — every environment finding
   from four batches. Binding where it does not conflict with the above.
5. `output/census/{site}.md` — the feasibility study for your site: which
   skills this mock actually supports, with routes, handlers and tie margins.
   It is the most specific document you have. Trust it over your intuition,
   but verify any mechanism claim you are about to depend on.

## Your lane

{facts}

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
    reward.py               evaluate(evidence) -> {{"score", "components"}}
    nemo_reward.py          the state-only twin; rubric parity with reward.py
    nemo_task.json          the NeMo-Gym rollout row

Plus `output/tasks/{site}/_batches/{slug}/GENERATION.md` and, for each task,
a golden replay draft at `output/tasks/{site}/_batches/{slug}/replays/<task_id>.py`.

### The metadata block, which the gate enforces

```json
"metadata": {{
  "style": "terse",
  "difficulty": "hard",
  "shape": "retrieval_writeback",
  "skills": ["R2", "R3", "A7"],
  "skill_chain": "date-range report -> sum -> write the figure into a CMS block",
  "official_analogues": ["<verbatim intent from webarena.jsonl>"],
  "hard_criteria": ["derived_target", "ordering_dependency"]
}}
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
        "difficulty : NOT a quota this round. Derive it per task: 2 skills =",
        "             medium; 3+ with two distinct retrievals or one retrieval",
        "             feeding two dependent actions = hard. Relabel DOWN if a",
        "             task falls short. Never pad a skill list to reach a label.",
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
    print(TEMPLATE.format(index=i, site=lane["site"], slug=lane["slug"],
                          n=lane["n"], facts=facts(i, lane)))
    print("\n" + "=" * 78 + "\n")
