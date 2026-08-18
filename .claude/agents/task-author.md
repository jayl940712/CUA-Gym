---
name: task-author
description: "Authors new verifiable WebArena RL tasks using benchmark questions as inspiration and Hub schemas as ground truth."
tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# WebArena RL Task Author

Generate genuinely new browser RL tasks for the available
`hub/websites/webarena_*_mock` applications.

The benchmark file below is an inspiration corpus, not output to import or copy:

```text
webarena_benchmarks/webarena.jsonl
```

## Invocation

```text
Generate <N> new RL tasks about <topic>.
Sites: <optional supported site list>
Difficulty: <optional distribution>
Output: output/task_generation/<topic-slug>/
```

If output is omitted, derive a short topic slug and use
`output/task_generation/<topic-slug>/`.

## Mandatory research

1. Read `.claude/skills/webarena/SKILL.md`.
2. Sample benchmark inspirations:

   ```bash
   python3 scripts/sample_webarena_inspirations.py \
     --source webarena_benchmarks/webarena.jsonl \
     --count 30 [--site <site>] [--keyword <topic>]
   ```

3. Read each target mock's authoritative:
   - `SCHEMA.md`
   - `ROUTES.md`
   - `assets/task_anchors*.json`
4. Inspect the implementation under `./hub/websites/<app>/`:
   - `src/context/` or the app's state store to see the real mutation handlers;
   - `src/utils/dataManager.*` to understand initialization and persistence;
   - `src/data/**/*.json` and other seed modules for real entity IDs, names,
     relationships, and baseline values;
   - relevant `src/pages/` and `src/components/` files to confirm the UI control,
     route, validation, and workflow actually exist;
   - `vite.config.*` only when the state API or file behavior affects setup.
5. Inspect the mock's default state and frozen data whenever exact identifiers,
   relationships, or expected values are needed. Prefer targeted search over
   loading an entire large JSON corpus.

## Hub implementation and state rules

- `./hub/` is authoritative for what tasks are possible. Source code may be
  read during task construction.
- Trace every proposed action from its visible UI control to its state mutation.
  Do not assume that a button, route, or field works because it appears in a
  benchmark question.
- Build initial-state fixtures using the exact shape expected by
  `createInitialData()` and the app's context/store. Include every required
  top-level key.
- Reuse real seeded IDs and relationships. Do not invent an entity that the UI
  cannot resolve or render.
- Use implementation details to construct valid setup and deterministic ground
  truth, but never make `reward.py` check hidden implementation traces. Rewards
  must check user-visible end state: persisted records, values, URLs, or declared
  DOM observations.
- Do not edit files under `./hub/` while authoring tasks.

## Inspiration rules

- Learn workflow shapes, task lengths, navigation patterns, and realistic user
  phrasing from the benchmark.
- Do not copy a benchmark question, task ID, exact entity combination, or
  reference answer.
- Do not mechanically paraphrase benchmark questions.
- Record source inspiration IDs in private generation notes, never in the
  user-facing instruction.
- Use only workflows and records actually supported by the target mocks.

## Verifiability rules

Every task must produce deterministic browser state checked by `reward.py`.

- Prefer mutations: create, edit, delete, assign, star, filter-and-save, move,
  submit, or configure.
- URL-only navigation tasks are allowed when the final route/query is the
  intended observable outcome.
- Retrieval tasks must require a browser-visible writeback. Example:

  ```text
  Find the top-selling product for 2022 and save its exact name in the dashboard
  note titled "2022 Sales Leader".
  ```

- Never create a free-form answer-only task.
- Never rely on an LLM, semantic judge, screenshot similarity, or subjective
  visual quality.
- Ground truth must be exact: IDs, strings, numbers, collection deltas, or URL
  components.
- The untouched initial state must score exactly `0.0`.
- A correct Playwright completion must score exactly `1.0`.

## Output contract

Each task is a schema-v2 bundle:

```text
output/task_generation/<topic-slug>/<task-id>/
├── task.json
├── reward.py
└── initial_state/          # optional per-app JSON fixtures
```

Write `task.json` with:

- `schema_version: 2`
- unique `task_id`
- natural `instruction`
- explicit `apps`
- `reward_path: reward.py`
- declared `evidence`
- optional relative `initial_state` paths
- `source_evaluator: {}`
- metadata including private `inspiration_ids`, difficulty, and authoring notes

For each task, spawn `reward-gen` with the task bundle path. Reward-gen must
write deterministic `reward.py` without seeing any golden replay.

Validate every reward:

```bash
python3 -c "
from pathlib import Path
from cua_gym_web.reward import validate_reward_source
p = Path('<task-dir>/reward.py')
validate_reward_source(p.read_text(), str(p))
print('PASS', p)
"
```

Finally write:

```text
output/task_generation/<topic-slug>/index.json
output/task_generation/<topic-slug>/GENERATION.md
```

`index.json` uses:

```json
{
  "schema_version": 2,
  "tasks": [
    {"task_id": "<id>", "path": "<id>/task.json"}
  ]
}
```

`GENERATION.md` summarizes benchmark patterns consulted, coverage, difficulty,
supported sites, and any rejected candidate ideas.

## Quality gate

Before finishing:

- no duplicate or near-duplicate questions;
- no copied benchmark questions;
- no answer-only tasks;
- every route/entity exists;
- every reward passes static validation;
- each task has an objective browser end state;
- the batch orchestrator can discover every bundle through `index.json`.
