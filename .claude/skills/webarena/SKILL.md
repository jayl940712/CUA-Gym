---
name: webarena
description: "How to author, import, execute, and verify WebArena tasks against CUA-Gym-Hub mocks using deterministic rewards and Playwright."
user-invocable: false
---

# WebArena Task Execution Guide

This skill is the source of truth for the root CUA-Gym task pipeline. It covers
only browser tasks targeting `hub/websites/webarena_*_mock`.

## 1. Existing tasks and new-task inspiration

For existing benchmark tasks, import the original task file:

```bash
python3 scripts/import_webarena_tasks.py /path/to/test.raw.json \
  --output output/webarena_tasks
```

The importer:

- accepts JSON arrays, `{tasks:[...]}`, and JSONL;
- preserves the original `eval` object;
- supports cross-site tasks when every site has a `webarena_*_mock`;
- excludes answer-only tasks without browser-visible writeback;
- compiles supported URL/DOM checks into deterministic `reward.py`;
- emits a versioned task bundle.

For genuinely new RL tasks, do not import benchmark rows. The task-author agent
uses `webarena_benchmarks/webarena.jsonl` only to study realistic question
patterns:

```bash
python3 scripts/sample_webarena_inspirations.py --count 30 --site gitlab
```

New questions must not copy or lightly paraphrase benchmark questions. Their
entities, workflows, initial state, and deterministic reward must be grounded in
the current Hub mocks. Retrieval patterns must be converted into observable
browser writebacks.

For each app, read its schema directly:

```text
hub/websites/<webarena_app>_mock/SCHEMA.md
hub/websites/<webarena_app>_mock/ROUTES.md
hub/websites/<webarena_app>_mock/assets/task_anchors*.json
```

Do not copy these schemas into `.claude`; Hub is authoritative.

## 2. Endpoint resolution

Task bundles contain environment-variable references, never deployment URLs:

```text
CUA_GYM_WEBARENA_GITLAB_URL
CUA_GYM_WEBARENA_REDDIT_URL
CUA_GYM_WEBARENA_SHOPPING_URL
CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL
CUA_GYM_WEBARENA_CLASSIFIEDS_URL
```

An optional endpoint JSON may map either those names or mock directory names:

```json
{
  "webarena_gitlab_mock": "https://gitlab-mock.example.test",
  "CUA_GYM_WEBARENA_REDDIT_URL": "https://reddit-mock.example.test"
}
```

Never persist deploy-all port numbers in a task.

## 3. Isolation

Both isolation layers are required:

- fresh Playwright `BrowserContext` isolates cookies, localStorage, cache,
  IndexedDB, and service workers;
- a unique backend SID isolates `.mock-states` and uploads.

Use separate SIDs for:

- `initial`: untouched no-op control;
- `oracle`: optional direct expected state;
- `replay`: known-correct Playwright UI execution;
- `rollout`: evaluated agent attempt.

For a cross-site task, use the same lane SID across all participating apps.
Never reuse one SID in concurrent contexts.

## 4. State API control plane

The generic runner, not the browser replay, uses:

| Operation | Effect |
|---|---|
| `POST /post?sid=...` with `action:set` | Replaces initial and current state |
| `action:set_current` | Replaces current while preserving initial |
| `GET /go?sid=...` | Returns initial, current, and state diff |
| `action:reset` | Destroys current, initial, and revision state |

Reset preserves uploads. Expired uploads require Hub cleanup tooling.

After `set`, require:

```text
initial_state == current_state
state_diff == {}
```

Server state wins over stale browser cache, but every normal run still uses a
fresh context.

## 5. Playwright replay contract

The replay contains only user actions:

```python
async def run(lane, task):
    gitlab = lane.page("gitlab")
    await gitlab.get_by_role("link", name="To-Do List").click()

    # Cross-site:
    # reddit = lane.page("reddit")
```

Forbidden inside a replay:

- `/post`, `/go`, or `/state` requests;
- localStorage/sessionStorage mutation;
- importing Hub data modules;
- editing mock files;
- jumping directly to a result route instead of performing the requested flow.

Prefer accessible locators. Avoid positional selectors and sleeps.

## 6. Deterministic reward.py

Every task bundle contains `reward.py`:

```python
def evaluate(evidence):
    initial = evidence["apps"]["gitlab"]["initial_state"]
    current = evidence["apps"]["gitlab"]["current_state"]
    # Perform exact structural checks and return progressive credit.
    return {"score": 0.0, "components": []}
```

Reward execution is offline and deterministic. It may inspect:

- initial/current state and state diff for every app;
- final browser URLs;
- final page HTML and visible text;
- declared DOM/helper observations.

It may not use an LLM, semantic similarity, network, subprocesses, filesystem,
environment variables, dynamic imports, or free-form agent answers.

`reward.py` must be self-contained and may not import local files from the task
bundle, repository, or Hub. Prefer the standard library. If a supported popular
third-party package is necessary, declare it in that task's `requirements.txt`
and set `task.json.requirements_path`. The runner executes from a separate
scratch directory so undeclared sibling imports cannot resolve.

An imported URL or `program_html` evaluator is compiled into an equivalent
Python reward. Answer-only `string_match` tasks are excluded because they do not
produce browser state. To use a retrieval task, rewrite its instruction so the
agent writes the result into an exact, observable browser field or entity.

Rewards are checked against both lanes:

```text
reward(initial evidence) == 0.0
reward(correct replay evidence) == 1.0
```

## 7. Write-drain and immutable evidence

Before running reward.py, the runner:

1. waits for browser-triggered persistence;
2. polls `/go` until current state is stable;
3. captures screenshots;
4. freezes state, final URLs, HTML/text, and declared observations as JSON;
5. executes reward.py in an isolated Python subprocess with a static capability
   policy and timeout;
6. saves a Playwright trace for replay lanes.

The accepted replay must pass twice from fresh SIDs.

## 8. NeMo-Gym export contract

NeMo-Gym does not mount task bundle files. Export each task as a
`WebArenaTaskRow` whose `task_payload.cuagym` field contains:

```text
bundle_id
app_dir
initial_setup       # inlined Python string or null
eval_reward_code    # inlined Python string
```

Both programs use `__CUA_GYM_SID__` and endpoint placeholders from
`cuagym/hub_apps.py`. Setup POSTs initial state and never launches a browser.
Reward GETs `/go?sid=...`, calculates a deterministic float, and prints
`REWARD: <float>`.

Before export:

- read `cuagym/README.md`, `schemas.py`, `episode_code.py`, and `hub_apps.py`;
- require exactly one app, because `CuaGymTaskInfo` has one `app_dir`;
- require the app and endpoint placeholder to exist in `hub_apps.py`;
- inline all required data—no local imports, sibling files, or auxiliary JSON;
- use only dependencies installed by `cuagym/requirements.txt`;
- validate the row using `WebArenaTaskRow` and `CuaGymTaskInfo`.

Current `cuagym/hub_apps.py` must be regenerated before exporting a
`webarena_*_mock` that it does not list. Never map it to a similarly named
non-WebArena mock.

## 9. Legacy and hardened mode

Legacy mode is the default:

```text
https://mock.example/path?sid=<opaque_sid>
```

Hardened mode uses an admin setup call, a one-time launch URL, an HttpOnly
cookie, and `sid=__cua_session__` in browser URLs. Never expose its real SID or
admin token to the browser agent.

Hardened mode must pass its own contract matrix before being used for
adversarial remote evaluation.

## 10. Run command

```bash
python3 scripts/run_webarena_task.py output/webarena_tasks/<id>/task.json \
  --replay output/runs/<id>/golden_replay.py \
  --output output/runs/<id>/attempt-1
```

Success requires:

- initial lane score exactly `0.0`;
- replay score exactly `1.0`;
- no browser errors;
- cleanup completion.
