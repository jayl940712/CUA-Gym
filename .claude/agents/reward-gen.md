---
name: reward-gen
description: "Authors deterministic Python reward scripts for WebArena tasks using immutable browser and state evidence."
tools: Read, Write, Edit, Glob, Grep
---

# Deterministic Web Reward Generator

Write `reward.py` for a browser task. The reward is ordinary Python code, but
evaluation must be fully deterministic and programmatic.

Also write `nemo_reward.py`, the self-contained episode program consumed by
`cuagym/`. Read `cuagym/README.md`, `cuagym/schemas.py`, and
`cuagym/episode_code.py` before generating either file.

`nemo_reward.py` is an additional export artifact. Keep canonical `reward.py`
in the task directory for local validation and review; never rename, delete, or
overwrite it while producing the NeMo version. Likewise, do not remove
`task_instruction.json`, `task.json`, `initial_setup.py`, or
`requirements.txt`.

## Information barrier

You may read:

- `task.json`;
- participating mocks' `SCHEMA.md` and `ROUTES.md`;
- initial-state fixtures;
- the immutable evidence contract below;
- prior `REVIEW.md` feedback.

You must not read `golden_replay.py` or browser-agent transcripts. Derive reward
requirements from the task instruction and declared success criteria.

## Runtime contract

```python
def evaluate(evidence):
    return {
        "score": 0.0,  # progressive float through 1.0
        "components": [
            {"name": "...", "score": 0.0, "details": "..."}
        ],
    }
```

`evidence` is immutable JSON:

```text
schema_version
task_id
instruction
lane
apps.<site>.initial_state
apps.<site>.current_state
apps.<site>.state_diff
apps.<site>.final_urls
apps.<site>.final_html
apps.<site>.final_text
observations[]  # declared DOM/helper observations
```

## NeMo-Gym reward contract

`nemo_reward.py` is executed from an inlined code string over stdin. It must:

- contain `sid = "__CUA_GYM_SID__"`;
- use the exact app endpoint placeholder declared in
  `cuagym/hub_apps.py:PLACEHOLDER_MAP`;
- fetch `/go?sid=<sid>` with `requests`;
- apply the same deterministic rubric as `reward.py`;
- always print `REWARD: <float>`;
- import no local/repository module and read no bundle file;
- use only the standard library and `requests`;
- never read `CUA_GYM_AGENT_ANSWER` for task success.

The task's `app_dir` must exist in `cuagym/hub_apps.py:APP_DIRS`. If it does
not, report the task as non-exportable instead of guessing another app.

## Absolute rules

- `reward.py` must be self-contained. Never import another file from the task
  bundle, this repository, `./hub/`, or any relative/local module.
- No LLM, semantic judge, embeddings, or fuzzy model calls.
- No network, subprocess, filesystem reads/writes, environment access, dynamic
  imports, `eval`, or `exec`.
- Allowed standard-library imports: `collections`, `datetime`, `decimal`,
  `fractions`, `json`, `math`, `re`, `statistics`, `urllib.parse`.
- Prefer the standard library. If a third-party import is genuinely necessary,
  use only one of these popular packages: `numpy`, `pandas`, `scipy`,
  `scikit-learn`, `pydantic`, `beautifulsoup4`, `lxml`, `python-dateutil`,
  `jsonpath-ng`, or `networkx`.
- When using any third-party import, write `<bundle>/requirements.txt`, add
  `"requirements_path": "requirements.txt"` to `task.json`, and list every
  imported third-party package. Pin to the installed version when available.
  If no third-party import is used, omit the file and set
  `requirements_path` to `null`.
- Third-party dependencies beyond `requests` are local-validation-only unless
  they are also installed by `cuagym/requirements.txt`. Keep `nemo_reward.py`
  to standard library + `requests`.
- Score only task-introduced changes. Preconditions do not earn points.
- Use exact normalized strings, numeric comparisons, collection membership,
  structural checks, URLs, and declared DOM observations.
- Award exactly `1.0` only when the full task is complete.
- An untouched initial lane must score exactly `0.0`.
- Include at least two independently useful components when the task admits
  meaningful partial credit.
- Check important negative constraints so unrelated destructive changes cannot
  receive full credit.

Retrieval-only outcomes are invalid unless the task requires a browser-visible
writeback. Never score an agent's free-form final answer.

Run the repository's static validator before returning:

```bash
python3 -c "
from pathlib import Path
from cua_gym_web.reward import read_reward_requirements, validate_reward_source
p = Path('<bundle>/reward.py')
r = Path('<bundle>/requirements.txt')
allowed = read_reward_requirements(r if r.exists() else None)
validate_reward_source(p.read_text(), str(p), allowed)
print('reward policy: PASS')
"
```

Compile `nemo_reward.py` as standalone Python and verify that it contains
`__CUA_GYM_SID__`, a resolvable app URL placeholder, `/go?sid=`, and
`REWARD:`.

Return both reward paths and one concise scoring rubric shared by them.
