# CUA-Gym WebArena

CUA-Gym WebArena is a browser-only pipeline for importing and verifying
existing WebArena tasks against the self-contained mock applications in
[CUA-Gym-Hub](https://github.com/xlang-ai/CUA-Gym-Hub).

It uses Playwright and shared remote mock deployments. It does not require
OSWorld, desktop applications, virtual machines, Aliyun, SSH, or root access.

## Architecture

Each task is evaluated in isolated browser/backend lanes:

```text
initial SID  + fresh BrowserContext → untouched control
oracle SID   + fresh BrowserContext → optional direct expected state
replay SID   + fresh BrowserContext → known-correct Playwright UI execution
rollout SID  + fresh BrowserContext → evaluated agent attempt
```

Browser contexts isolate cookies, localStorage, cache, IndexedDB, and service
workers. SIDs isolate server-side state and uploads. Cross-site tasks use the
same lane SID across all participating mocks.

Every task is scored by deterministic Python `reward.py` over immutable browser
evidence. No LLM, semantic judge, or network call runs during evaluation.

## Install

```bash
git clone --recurse-submodules https://github.com/xlang-ai/CUA-Gym
cd CUA-Gym
pip install -e ".[dev]"
playwright install chromium
cp .env.example .env
```

Configure shared deployments in `.env`:

```bash
CUA_GYM_WEBARENA_GITLAB_URL=https://gitlab-mock.example.com
CUA_GYM_WEBARENA_REDDIT_URL=https://reddit-mock.example.com
CUA_GYM_WEBARENA_SHOPPING_URL=https://shopping-mock.example.com
CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL=https://shopping-admin-mock.example.com
CUA_GYM_WEBARENA_CLASSIFIEDS_URL=https://classifieds-mock.example.com
```

An endpoint-registry JSON can be supplied instead of environment variables.
Task bundles never contain deployment URLs.

## Choose the task workflow

There are two different entry points:

| Goal | Import WebArena tasks? | Input to the agent pipeline |
|---|---:|---|
| Run existing WebArena benchmark tasks | Yes, once | `output/webarena_tasks/<task-id>/task.json` |
| Create a new RL task | No | `output/task_generation/<task-id>/task.json` |

The importer is only a compiler for existing raw WebArena data. It normalizes
site names and routes, filters unsupported tasks, and generates deterministic
`reward.py`. It does not create new questions and does not run the browser.

For a new RL task, skip importing and author the schema-v2 bundle directly:

```text
output/task_generation/<task-id>/
├── task.json
└── reward.py
```

Then launch the full agent pipeline with:

```bash
python3 scripts/batch_orchestrator.py \
  output/task_generation/<task-id>/task.json \
  --concurrency 1
```

The current pipeline validates and iterates an authored task bundle. It does not
yet generate the initial task question from a natural-language prompt.

## Import existing tasks

The importer accepts WebArena JSON arrays, `{tasks:[...]}`, and JSONL:

```bash
python3 scripts/import_webarena_tasks.py \
  /path/to/webarena/config_files/test.raw.json \
  --output output/webarena_tasks
```

For VisualWebArena task files:

```bash
python3 scripts/import_webarena_tasks.py \
  /path/to/test_classifieds.raw.json \
  --id-prefix visualwebarena \
  --output output/visualwebarena_tasks
```

Only tasks whose complete site set is available under
`hub/websites/webarena_*_mock` are imported. Cross-site tasks are retained when
all their sites are supported. URL/DOM checks are compiled into `reward.py`.
Answer-only and unsupported tasks are reported in `index.json` instead of being
silently converted.

Each imported task becomes:

```text
output/webarena_tasks/<task-id>/task.json
output/webarena_tasks/<task-id>/reward.py
```

The manifest preserves source metadata, declares immutable observations, and
replaces deployment URLs with environment-variable references.

## Author a new task

A new task bundle contains `task.json` and deterministic `reward.py`.
State-based rewards do not need extra evidence declarations:

```json
{
  "schema_version": 2,
  "task_id": "gitlab_issue_001",
  "instruction": "Create an issue titled 'CUA verification issue' in the project.",
  "apps": [{
    "name": "webarena_gitlab_mock",
    "source_name": "gitlab",
    "base_url_env": "CUA_GYM_WEBARENA_GITLAB_URL",
    "start_path": "/byteblaze/a11y-syntax-highlighting/-/issues"
  }],
  "reward_path": "reward.py",
  "evidence": [],
  "source_evaluator": {}
}
```

`reward.py` reads immutable initial/final state:

```python
def evaluate(evidence):
    app = evidence["apps"]["gitlab"]
    added = app["current_state"].get("newIssues", [])
    matches = [issue for issue in added if issue.get("title") == "CUA verification issue"]
    score = 1.0 if len(matches) == 1 else 0.0
    return {
        "score": score,
        "components": [{"name": "issue_created", "score": score}]
    }
```

Retrieval tasks must require an observable writeback, such as saving the
retrieved value in a named comment, note, or form field.

## Known-correct Playwright replay

A replay performs the task through the visible UI:

```python
async def run(lane, task):
    gitlab = lane.page("gitlab")
    await gitlab.get_by_role("link", name="To-Do List").click()

```

Run it:

```bash
python3 scripts/run_webarena_task.py \
  output/webarena_tasks/webarena-44/task.json \
  --replay output/runs/webarena-44/golden_replay.py \
  --output output/runs/webarena-44/attempt-1
```

If Playwright's bundled browser is unavailable, pass
`--browser-executable /path/to/chromium`.

The runner:

1. reads pristine default state from each mock;
2. establishes an isolated initial lane;
3. requires `reward.py` to score untouched evidence exactly `0.0`;
4. establishes a separate replay lane;
5. executes the Playwright actions;
6. waits for browser state writes to stabilize;
7. freezes state, final URLs, HTML/text, and declared DOM observations;
8. runs deterministic `reward.py` in a restricted subprocess;
9. captures screenshots, state diffs, and a Playwright trace;
10. destroys all session state in `finally`.

Run artifacts are private because they contain ephemeral SIDs:

```text
output/runs/<task-id>/<attempt>/
├── verification.json
├── initial-evidence.json
├── replay-evidence.json
├── initial-states.json
├── replay-states.json
├── replay-trace.zip
└── screenshots/
```

## Agent workflow

The root `.claude/` system contains four WebArena-only agents:

| Agent | Responsibility |
|---|---|
| `orchestrator` | Coordinates reward generation, replay, and audit |
| `golden-browser` | Creates and reruns deterministic Playwright actions |
| `reward-gen` | Authors deterministic Python rewards from task requirements |
| `reward-audit` | Audits reward behavior without seeing replay source |

Batch execution:

```bash
python3 scripts/batch_orchestrator.py \
  output/webarena_tasks/index.json \
  --endpoints endpoints.json \
  --concurrency 3
```

The separate `hub/.claude/` system remains responsible for developing and
testing mock applications. It is not the task-execution pipeline.

## State API

The generic runner uses the Hub API as a privileged control plane:

| Endpoint | Purpose |
|---|---|
| `POST /post?sid=...`, `action:set` | Establish initial and current state |
| `action:set_current` | Establish optional oracle state |
| `GET /go?sid=...` | Read initial, current, and state diff |
| `action:reset` | Destroy current, initial, and revision state |

Playwright replays must not call these endpoints or mutate browser storage.

Reset preserves uploaded files. Use Hub's session cleanup tooling for expired
uploads.

## Legacy and hardened sessions

Legacy mode is currently the default and uses `?sid=<opaque_sid>`.

Hardened mode can be selected with:

```bash
python3 scripts/run_webarena_task.py task.json \
  --mode hardened \
  --admin-token "$CUA_GYM_ADMIN_TOKEN"
```

Hardened execution uses a one-time launch URL and HttpOnly cookie. Its contract
must be tested independently before adversarial remote deployment.

## Verification

```bash
pytest
ruff check cua_gym_web scripts tests
python3 -m compileall -q cua_gym_web scripts tests
```

Hub state-contract tests remain under `hub/shared/`.

## Verifiable-task requirement

Tasks must produce deterministic browser state. Existing `url_match` and
`program_html` tasks can be compiled automatically. Answer-only `string_match`
and visual `page_image_query` tasks are excluded.

To use a retrieval task, rewrite it to require a browser-visible writeback. For
example, ask the agent to save the retrieved value in a named issue comment,
dashboard note, form field, or other exact state that `reward.py` can verify.

## Citation

```bibtex
@misc{wang2026cuagymscalingverifiabletraining,
  title={CUA-Gym: Scaling Verifiable Training Environments and Tasks for Computer-Use Agents},
  author={Bowen Wang and Dunjie Lu and Junli Wang and Tianyi Bai and Shixuan Liu and Zhipeng Zhang and Haiquan Wang and Hao Hu and Tianbao Xie and Shuai Bai and Dayiheng Liu and Que Shen and Junyang Lin and Tao Yu},
  year={2026},
  eprint={2605.25624},
  archivePrefix={arXiv},
  primaryClass={cs.AI}
}
```
