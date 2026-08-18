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
2. Read the NeMo-Gym consumer contract before designing any output:
   - `cuagym/README.md`
   - `cuagym/schemas.py`
   - `cuagym/episode_code.py`
   - `cuagym/hub_apps.py`
   - `cuagym/data/example.jsonl`
3. Sample benchmark inspirations:

   ```bash
   python3 scripts/sample_webarena_inspirations.py \
     --source webarena_benchmarks/webarena.jsonl \
     --count 30 [--site <site>] [--keyword <topic>]
   ```

4. Read each target mock's authoritative:
   - `SCHEMA.md`
   - `ROUTES.md`
   - `assets/task_anchors*.json`
5. Inspect the implementation under `./hub/websites/<app>/`:
   - `src/context/` or the app's state store to see the real mutation handlers;
   - `src/utils/dataManager.*` to understand initialization and persistence;
   - `src/data/**/*.json` and other seed modules for real entity IDs, names,
     relationships, and baseline values;
   - relevant `src/pages/` and `src/components/` files to confirm the UI control,
     route, validation, and workflow actually exist;
   - `vite.config.*` only when the state API or file behavior affects setup.
6. Inspect the mock's default state and frozen data whenever exact identifiers,
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

## NeMo-Gym compatibility preflight

Every generated task must be consumable by `cuagym/` without runtime bundle
files:

- The task's `app_dir` must appear in `cuagym.hub_apps.APP_DIRS`.
- Every endpoint token used by setup/reward code must appear in
  `cuagym.hub_apps.PLACEHOLDER_MAP`.
- The current `CuaGymTaskInfo` schema supports exactly one `app_dir`. Generate
  only single-app NeMo rows; reject cross-app candidates rather than emitting an
  invalid row.
- If a requested `webarena_*_mock` is absent from `APP_DIRS` or has no endpoint
  placeholder, stop and report that `cuagym/hub_apps.py` must be regenerated
  against the current Hub. Never substitute a similarly named commercial mock.
- NeMo executes code strings from stdin in a scratch directory. No local bundle
  file, auxiliary state JSON, or sibling Python module is available at episode
  time.

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
├── task_instruction.json  # stable human-readable task contract
├── task.json
├── reward.py
├── requirements.txt       # optional; only for declared popular dependencies
├── initial_setup.py        # self-contained NeMo setup program
├── nemo_reward.py          # self-contained NeMo reward program
└── nemo_task.json          # ready-to-inline WebArenaTaskRow payload
```

These canonical files must remain in place after NeMo export. `nemo_task.json`
and `nemo_tasks.jsonl` contain inlined copies; they must never replace, rename,
truncate, or delete `task_instruction.json`, `task.json`, `initial_setup.py`,
`reward.py`, or `requirements.txt`.

Write `task_instruction.json` with at least:

```json
{
  "task_id": "<task-id>",
  "task_instruction": "<exact instruction shown to the rollout agent>",
  "app_dir": "<single NeMo app_dir>",
  "start_path": "<initial browser path>",
  "difficulty": "easy | medium | hard",
  "success_criteria": [
    "<exact observable browser-state requirement>"
  ]
}
```

Write `task.json` with:

- `schema_version: 2`
- unique `task_id`
- natural `instruction`
- explicit `apps`
- `reward_path: reward.py`
- optional `requirements_path: requirements.txt`
- declared `evidence`
- optional local `initial_state` paths only when the same state is also inlined
  into `initial_setup.py`
- `source_evaluator: {}`
- metadata including private `inspiration_ids`, difficulty, and authoring notes

For each task, spawn `reward-gen` with the task bundle path. Reward-gen must
write deterministic `reward.py` without seeing any golden replay.

### initial_setup.py

NeMo setup code must:

- be a single self-contained Python program;
- contain `__CUA_GYM_SID__`;
- use the exact `__CUA_GYM_<APP>_URL__` placeholder from `PLACEHOLDER_MAP`;
- inline any custom initial state as Python/JSON data;
- POST `{"action":"set","state":...}` to `/post?sid=...`;
- use no `/tmp` SID handoff, browser launch, `launch_gui`, or
  `google-chrome`;
- depend only on the standard library plus `requests`, which is present in
  `cuagym/requirements.txt`.

If pristine Hub default state is sufficient, `initial_setup` in the NeMo row may
be `null`.

### nemo_reward.py

NeMo reward code must:

- be a single self-contained Python program, with no local imports;
- contain the same SID and endpoint placeholders;
- GET `/go?sid=...` and deterministically inspect `initial_state`,
  `current_state`, and `state_diff`;
- print `REWARD: <float>` on its final output path;
- never use an LLM, semantic judge, browser process, screenshot scoring, agent
  answer, or undeclared environment data;
- depend only on the standard library plus `requests`.

`reward.py` and `nemo_reward.py` must implement the same rubric. The former is
used by local adversarial validation over immutable evidence; the latter is
inlined and executed by NeMo-Gym.

Never replace `reward.py` with the NeMo wrapper. Keep both source files, even
when their scoring logic is mechanically equivalent.

Per-task `requirements.txt` is authoring metadata only. NeMo-Gym does not install
it. A task is NeMo-ready only if its inlined setup/reward imports are already
available in `cuagym/requirements.txt`.

### nemo_task.json and aggregate JSONL

Write this exact row payload shape:

```json
{
  "task_payload": {
    "task_id": "<task-id>",
    "dataset": "cuagym",
    "dataset_version": "v1",
    "sites": ["<app_dir>"],
    "start_urls": [],
    "intent": "<instruction>",
    "eval": {
      "eval_types": ["string_match"],
      "reference_answers": null,
      "note": "unused — CUA-Gym reward code is authoritative"
    },
    "cuagym": {
      "bundle_id": "<task-id>",
      "app_dir": "<app_dir>",
      "initial_setup": "<contents of initial_setup.py or null>",
      "eval_reward_code": "<contents of nemo_reward.py>"
    }
  }
}
```

Inline the code contents as JSON strings. Also append every `nemo_task.json`
object as one line in:

```text
output/task_generation/<topic-slug>/nemo_tasks.jsonl
```

Validate every reward:

```bash
python3 -c "
from pathlib import Path
from cua_gym_web.reward import read_reward_requirements, validate_reward_source
p = Path('<task-dir>/reward.py')
r = Path('<task-dir>/requirements.txt')
allowed = read_reward_requirements(r if r.exists() else None)
validate_reward_source(p.read_text(), str(p), allowed)
print('PASS', p)
"
```

Finally write:

```text
output/task_generation/<topic-slug>/index.json
output/task_generation/<topic-slug>/GENERATION.md
output/task_generation/<topic-slug>/nemo_tasks.jsonl
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
- every bundle retains `task_instruction.json`, `task.json`,
  `initial_setup.py` (when setup is needed), `reward.py`, and optional
  `requirements.txt` after NeMo export;
- every reward passes static validation;
- every setup/reward program compiles after placeholder substitution;
- every NeMo row validates against `WebArenaTaskRow` +
  `CuaGymTaskInfo`;
- inlined setup contains no GUI launch or `/tmp` SID file;
- inlined reward contains `__CUA_GYM_SID__`, a resolvable app placeholder,
  `/go?sid=`, and `REWARD:`;
- no task relies on per-task files or dependencies at NeMo episode time;
- each task has an objective browser end state;
- the batch orchestrator can discover every bundle through `index.json`.
