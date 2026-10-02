#!/usr/bin/env python3
"""Emit a tier-2 instance-variant authoring prompt for one site."""
import sys

site, count, extra = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "")
PORT = {"gitlab": 8001, "reddit": 8002, "shopping_admin": 8003, "shopping": 8004}[site]
APP = f"webarena_{site}_mock"

print(f"""Generate **{count} tier-2 instance variants** for the {site} mock (`{APP}`).

This is a different job from tier-1 authoring. You are **not** looking for new task
types. Every type has already been found and verified; you are producing additional
*instances* of them.

## What a variant is

Take a **verified** tier-1 template and re-instantiate it over a **different seeded
entity**: a different product, issue, forum, order, comment, project, customer. The
executed code path is identical by design. What changes is the entity the agent must
find and act on — which is the point, because it changes what the agent must perceive
and ground against.

- Output: `output/tasks/{site}/<task_id>/` (flat, same bundle shape as tier 1)
- Task IDs: `<template_task_id>_v2`, `_v3`, ... — keep the template id as the prefix so
  the lineage is obvious and ids cannot collide.
- Notes: `output/tasks/{site}/_batches/_tier2_variants/GENERATION.md` (append; do not
  overwrite a sibling's section).

## Required reading

1. `output/tier2/verified_{site}.txt` — the **only** templates you may instantiate.
   Each line is `task_id | difficulty | setup=yes|none | instruction`. A template
   absent from this file either failed verification or has not finished; do not touch
   it, and do not instantiate a variant of a variant.
2. The bundle directory of each template you pick — read its `task_instruction.json`,
   `task.json`, `initial_setup.py`, `reward.py`, `nemo_reward.py`, and its batch's
   `GENERATION.md`. The `GENERATION.md` states the template's precondition and the
   branch it unlocks; **your entity must satisfy that same precondition**.
3. `output/prior_inventory/{site}.txt` — all 100 prior tasks for this site.
4. `output/AUTHOR_BRIEF.md` — still binding for everything except test 2 (see below).

## The rules, and the one that is relaxed

- **Test 2 is waived *within this corpus only*.** "Same mutation, different entity" is
  exactly what you are producing, and it is not a duplicate for this tier.
- **Test 2 still applies against the 400 prior tasks.** Your variant must not land on
  an entity that `webarena_08_18_batch_200` or `webarena_08_19_batch_200` already used
  for that mutation. Check the prior inventory per variant.
- **Tests 1, 3 and 4 still apply in full** — no id collisions, no criteria that are a
  subset of a prior task's from an equivalent start state, no paraphrase of a prior
  instruction.
- Every variant carries, in `task.json` metadata:
  `"dedup_standard": "instance_variant"` and `"variant_of": "<template task_id>"`.
- **Weight your picks toward `easy` templates.** The corpus is at 76% easy against an
  80% target, so prefer easy templates unless a medium is the only one that fits.
- Spread across templates rather than piling variants onto one. If a template supports
  only one sensible alternative entity, take one and move on.

## The correctness risk, which is the whole job

A variant is only valid if the **new entity genuinely satisfies the template's
precondition**. This is where a careless variant breaks:

- if the template needs a product with a required option, the variant's product must
  have one (**0 of 4,884 seeded option groups are non-required**);
- if it needs an out-of-stock product, pick from the 261 that are;
- if it needs a forum with zero submissions, the seed has none — the setup must inject
  one, as the template's does;
- if it needs an order that is dummy-free, only **19 of 308** qualify;
- if the reward asserts an exact string, total or count, **recompute it for the new
  entity** — do not copy the template's expected value.

Re-derive every scored value from the seed for your entity. A variant that inherits the
template's expected value is broken, and it will fail verification rather than fail
quietly, but it wastes a verification slot.

## Load-bearing mock facts
{extra}
- Inline JSON fixtures with `json.loads(r\"\"\"...\"\"\")` — raw string, always; never
  quote that call verbatim inside a module docstring.
- Read `current_state`; never diff against `initial_state`.
- Never gate a reward component on "the record was edited" — gate on the value.
- Untouched initial state scores exactly 0.0 **per component**; correct completion 1.0.

## Before reporting done

```bash
python3 scripts/preflight_bundles.py output/tasks/{site} \\
  --prior-batch webarena_08_18_batch_200/tasks \\
  --prior-batch webarena_08_19_batch_200/tasks --quiet
```

Execute every `initial_setup.py` against a live throwaway sid ({site} is at
http://localhost:{PORT}); confirm `/go` shows `state_diff == {{}}` and
`initial_state == current_state`, and that the reward scores **0.0 per component** on
your own setup output.

**Drive a real chromium replay of every variant.** You may adapt the template's replay
driver — it is in that batch's notes directory — but you must actually run it against
your entity, because the whole failure mode of this tier is an entity that does not
satisfy the precondition. Report the per-variant replay scores.

Report honestly: if a template has no second entity that satisfies its precondition,
say so and move to another rather than forcing one.""")
