# Batch 6 — 600 all-medium skill-aligned WebArena RL tasks

Inherits **everything** from `webarena_09_04_skills/BATCH5_CONTRACT.md` and
TASK4.md except where overridden here. Read the batch-5 contract first; read
`docs/SKILL_TAXONOMY.md` second; read `webarena_09_04_skills/CORRECTIONS.md`
third — it holds 122 verified findings and every one of them still applies.

## Override 1 — every task is `medium`, and medium has an exact definition

**600 medium, 0 easy, 0 hard.**

A medium is **exactly two skills: one retrieval feeding one action.**
`metadata.skills` must have length 2, one `R*` and one `A*`. The gate enforces
this (`--medium-is-exactly-two`).

That is stricter than batch 5, where medium meant "at least two". A 3-skill
chain labelled medium is a hard task wearing the wrong label, and the point of
an all-medium batch is that the difficulty is genuinely uniform.

If a design needs a third step, **split it into two tasks or drop the step.**
Do not relabel it hard — there is no hard tier in this batch.

## Override 2 — the (R, A) pair is the unit of assignment

Batch 5 assigned each lane a multi-step *chain* and let topic supply the
material. With only two skills there is no chain to speak of, so batch 6
assigns each lane a specific **(retrieval, action) pair** plus a site.

This is the organising principle and it is what keeps 600 same-difficulty tasks
from collapsing into each other. Batch 5's 147 clean mediums used 45 distinct
pairs, very unevenly — `R5 -> A4` fifteen times, most pairs once or twice.
Batch 6 spreads deliberately across the feasible space.

## Override 3 — reuse is allowed, repetition is not

Topic overlap with batch 5 is explicitly fine. What is not fine:

* a duplicate `task_id` (ids are globally unique across all six batches);
* a task that is batch 5's task with a value swapped;
* reproducing an official benchmark intent verbatim (train/test contamination).

**The natural safeguard is the difficulty change itself:** batch 5 is 72% hard,
and truncating a 3-skill chain to its 2-skill core produces a genuinely
different task with a different rubric. Where you reuse a batch-5 entity, change
what is derived or what is written — not merely which row.

Every bundle records `metadata.derived_from` naming the batch-5 task it is
adjacent to, or `null` if it is new ground. That is an honesty aid, not a
restriction.

## Unchanged from batch 5

* 600 tasks, 150 per site; classifieds excluded.
* 450 terse / 150 explicit, balanced per site.
* >= 70% at `start_path: "/"`.
* `metadata.skills` / `skill_chain` / `official_analogues` (verbatim,
  cross-checked against all 799 official intents) / `injected_preconditions`.
* Click-reachability (S6), empty-state 0.0 (S9.5), `current_state` only (S7),
  `json.loads(r"""...""")` for fixtures, no `hashlib`.
* Injection is a design tool: break ties, plant distractors, set margins, make
  a retrieval genuinely necessary.
* **Authors run no validation code.** Write the bundles and stop.

## The 13 rules that cost the most in batch 5

Carried verbatim into every lane brief, because each was learned expensively:

1. Directory name == `task_id`, and `task_id` starts with the lane slug, no site prefix.
2. A module docstring's closing triple-quote needs a newline before the first import.
3. Terse intents cap at 40 words. Count them.
4. An injected record carries EVERY field the real handler writes, in the handler's convention.
5. Assume any stored aggregate disagrees with its rendered list until checked — and check the domain of the disagreement.
6. Grep for the *reference*, not the definition. Three lanes found writable keys the render path never reads. **And know that `grep` silently finds NOTHING in two mock files** — `webarena_gitlab_mock/src/components/create/mutations.js` (the entire gitlab creation module: `createProject`, `forkProject`, `commitToRepo`, `addMembers`, `writeFiles`, `createGroup` …) and `webarena_reddit_mock/src/utils/markdown.js`. Both contain NUL bytes, so `file` calls them `data` and ugrep suppresses matches, **exiting 1 exactly like "not found"**. Use `grep -a`, or read the file in Python, before concluding any handler is absent.
7. Resolve entities against `src/data/`, not against the benchmark string, and use the exact rendered name.
8. Treat every census list as a sample, never an enumeration.
9. Ask whether an agent that SKIPPED the retrieval would still succeed — and whether the UNTOUCHED state scores 1.0.
10. A finding can be right with the wrong mechanism, and the wrong mechanism implies the wrong remedy.
11. Read the mock's `vite.config.js` before a partial `set`: reddit REPLACES, shopping and shopping_admin shallow-merge.
12. Prefer structural ordering dependencies over narrated ones.
13. An injection must not create a contradiction visible on one screen.
