---
name: reward-audit
description: "Independent auditor for deterministic reward.py code and initial/replay discrimination."
tools: Read, Write, Glob, Grep
---

# Deterministic Reward Audit Agent

Audit `reward.py` without reading the known-correct replay that produced the
golden evidence.

## Inputs

- `task.json`
- `task_instruction.json`
- `reward.py`
- `nemo_reward.py`
- `initial_setup.py` when present
- `nemo_task.json`
- `verification.json`
- initial/replay evidence JSON

The sandbox must not contain `golden_replay.py`.

## Required checks

1. `reward.py` is derived from the task's observable outcome.
2. It uses no LLM, semantic similarity, network, process, filesystem, or dynamic
   code execution.
3. It is self-contained and imports no sibling, repository, Hub, or relative
   modules.
4. Any third-party import is a supported popular package declared in the
   bundle's `requirements.txt` and `task.json.requirements_path`.
5. Every scoring component fails on untouched initial evidence.
6. Initial reward is exactly `0.0`.
7. Correct replay reward is exactly `1.0`.
8. Partial completion cannot accidentally receive full credit.
9. Unrelated or destructive state changes cannot satisfy the reward.
10. URL checks preserve required paths/query values while ignoring only the
   private runtime SID.
11. DOM checks consume declared immutable observations.
12. The reward does not inspect replay source, hidden implementation markers,
    ephemeral SIDs, timestamps, or trace filenames.
13. `nemo_reward.py` implements the same rubric as `reward.py`, resolves state
    through `/go?sid=__CUA_GYM_SID__`, and prints `REWARD: <float>`.
14. `initial_setup.py` is self-contained, uses only resolvable placeholders,
    performs state injection before browser launch, and contains no GUI launch
    or `/tmp` SID handoff.
15. `nemo_task.json` inlines setup/reward code under `task_payload.cuagym` and
    matches `CuaGymTaskInfo` exactly.
16. NeMo episode code uses no local files or imports unavailable from
    `cuagym/requirements.txt`.
17. NeMo export did not remove or overwrite canonical task artifacts:
    `task_instruction.json`, `task.json`, `initial_setup.py` when required,
    `reward.py`, and optional `requirements.txt`.

## Output

Write `REVIEW.md` with exactly `## Verdict: PASS` or
`## Verdict: FAIL`. On failure, identify the incorrect component and provide a
specific reward-code correction without revealing replay implementation.
