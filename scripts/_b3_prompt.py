#!/usr/bin/env python3
"""Emit a batch-3 task-author prompt for one topic. Keeps 45+ launches consistent."""
import sys
site, slug, plan_section, split, extra = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], (sys.argv[5] if len(sys.argv)>5 else "")
PORT = {"gitlab":8001,"reddit":8002,"shopping_admin":8003,"shopping":8004}[site]
APP  = f"webarena_{site}_mock"
e,m = split.split(":")[0], split.split(":")[1]
print(f"""Generate {int(e)+int(m)} new RL tasks for topic **`{slug}`** in the {site} mock.

Sites: {site} (`{APP}` only — one app per task)
Output: `output/tasks/{site}/<task_id>/` (flat, one directory per task)
Notes/index: `output/tasks/{site}/_batches/{slug}/`
Task ID prefix: `{site}_{slug}_`
**Difficulty: exactly {e} easy, {m} medium, 0 hard.**

## FIRST, read these in full, in this order

1. `output/AUTHOR_BRIEF.md` — binding. Read §0 ("What is different about batch 3"):
   novelty comes from the **injected precondition**, not the entity instance, and
   there is a rule for when injection counts.
2. **`output/topic_plans/{site}.md`, section `{plan_section}`** — your topic was
   planned by an agent that read the whole mock source. It names the handlers, state
   keys, injected preconditions and the guard at each `file:line`. Read the
   document's preamble and cross-cutting notes too, then work from your section.
   **Verify every line reference yourself** — a prior batch found the plan's line
   numbers wrong on one surface. Trust the source, not the doc.
3. `output/prior_inventory/{site}.txt` — **all 100 lines** of prior {site} tasks.
4. `output/prior_inventory/_batch3_running_{site}.txt` — batch-3 {site} bundles
   already accepted. These are equally off limits. Sibling batches may land more in
   the same directory while you work; do not collide with them and do not modify
   their bundles.
5. `.claude/agents/task-author.md`, `.claude/skills/webarena/SKILL.md`,
   `hub/websites/{APP}/SCHEMA.md`, `ROUTES.md`.

Reference bundle shape:
`webarena_08_18_batch_200/task_generation/gitlab-workflows/gitlab_triage_backlog_001/`.
Both `webarena_08_1[89]_batch_200/` directories are READ-ONLY.

## The two duplicate tests that matter

- **Test 2** — same primary mutation on the same primary entity with only the
  entity instance, field value or wording changed is a **duplicate**, injected or
  not. Vary the *branch*, never the instance.
- **Test 3 (corrected for batch 3)** — criteria being a subset of a prior task's
  only counts as a duplicate when the task **also starts from a materially
  equivalent state**. A precondition is material when it changes which branch
  executes, which controls render, or what the agent must do.

**The operative test, applied consistently across this batch: does a different line
of code actually execute — AND does the agent's work differ?** Both halves are
required.

- One bundle was rejected for claiming a wildcard protected-branch rule was novel:
  the handler stores the name verbatim with no conditional, so no line differed.
  If you cannot name the differing line, the task is a duplicate.
- A differing line is **not sufficient on its own**. A shopping author correctly
  rejected the billing/shipping mirrors of two of its own tasks even though they
  execute different lines (`AppContext.jsx:477-480` vs `:472-476`), because the
  agent's route, controls and reasoning were identical — that is the field value
  changing, which test 2 names explicitly. Hold yourself to that standard.

For **every** task, state in `GENERATION.md`: the injected precondition, the exact
branch or control it unlocks with `file:line`, and the test-2/test-3 check against
the specific prior tasks that touch the same surface.

## Load-bearing facts
{extra}
- Inline JSON fixtures with `json.loads(r\"\"\"...\"\"\")` — raw string, always. Do not
  quote that call verbatim inside a module docstring; the inner triple quote closes
  the docstring and every bundle then fails the gate.
- Read `current_state`; never diff against `initial_state`. A key that returns to
  its pristine baseline leaves `state_diff` entirely.
- **Never gate a reward component on "the record was edited" — gate on the recorded
  value.** Several handlers write unconditionally.
- Untouched initial state scores exactly 0.0, correct completion exactly 1.0.
  `reward.py` and `nemo_reward.py` implement the same rubric; the reward prints
  `REWARD: <float>` on every path including its error path. Medium tasks ship
  `components` summing to exactly 1.0 in a module-level `COMPONENT_WEIGHTS`.

## Before reporting done

Run and paste:

```bash
python3 scripts/preflight_bundles.py output/tasks/{site} \\
  --prior-batch webarena_08_18_batch_200/tasks \\
  --prior-batch webarena_08_19_batch_200/tasks --quiet
```

(The site directory holds sibling batches too; only your own bundles are yours to
fix. Check your own split is {e} easy / {m} medium.)

**Tooling hazard — NUL bytes defeat grep.** `hub/websites/webarena_gitlab_mock/src/components/create/mutations.js`
contains NUL bytes (offsets 3445, 7320), so plain `grep` treats it as binary and
**silently matches nothing**. Use `grep -a`. If any "no writer exists" or "nothing
reads this" conclusion rests on a grep, re-run it with `-a` before trusting it.

**Replay hazard — the sticky navbar.** On gitlab's issue/MR list views the sticky
`header.navbar` overlays the row checkboxes: `.check()` times out and
`.check(force=True)` **silently clicks the navbar**, so the box never toggles and the
run posts no mutation while appearing to succeed. Focus the input and press Space.
This cost a sibling a failed run.

**Replay boot race — this cost a sibling two failed runs.** `wait_until="networkidle"`
is NOT sufficient: `AppProvider`'s boot awaits `fetchServerState(sid)` and its
deferred chunks *after* the page reports idle, so a click fired at idle can land
before the app has state and produce a run that posts `set_current` and no mutation
at all. Add a settle delay plus an explicit `wait_for_selector` on a control your
flow needs, per navigation.

Execute every `initial_setup.py` against a live throwaway sid ({site} is at
http://localhost:{PORT}) and confirm `/go` shows `state_diff == {{}}` and
`initial_state == current_state`. **Drive a real chromium replay of each flow, twice
from fresh sids, and hard-assert the branch claims in the replay** (assert the
control is absent/disabled/present as your precondition claims) rather than assuming
them. Report honestly rather than padding: if the topic yields fewer than {e} clean
easy tasks, say so and deliver what it supports.""")
