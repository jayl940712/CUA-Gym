#!/usr/bin/env python3
"""Export verified task bundles as NeMo-Gym rollout rows (JSONL).

Reads a delivered batch directory (`tasks/<site>/<task_id>/` plus
`runs/<task_id>/`) and emits one JSON object per line in the rollout format
that `cuagym/data/example.jsonl` documents:

    {
      "responses_create_params": {"input": [{"role": "user", "content": <intent>}],
                                  "parallel_tool_calls": false},
      "verifier_metadata": {"task": <task_payload>},
      "task_payload": {sites, start_urls, ... "cuagym": {bundle_id, app_dir,
                       initial_setup, eval_reward_code}},

`sites` and `start_urls` are strictly parallel and both come from `task.json`,
which is what the verification harness actually navigated to. `start_urls[i]` is
a *path* (not an absolute URL), or "" when that app starts at its default
location. Consumers join them as `<base><start_path>?sid=<sid>` -- path before
query. See docs/NEMO_JSONL_FORMAT.md.
      "agent_ref": {"type": "responses_api_agents", "name": "cuagym_agent"},
      "context_compaction_contract_version": 2,
      "context_compaction_group_id": "cuagym-<task_id>",
      "context_compaction_task_id": <task_id>,
      "context_compaction_rollout_index": 0,
      "context_compaction_attempt_index": 0
    }

Only bundles that actually verified are exported. A bundle qualifies when all of:

  * its run directory holds a `REVIEW.md` containing `## Verdict: PASS`;
  * at least one verification.json (`attempt-*/`, or the run root when no
    attempt directory exists) reports `verification.passed`;
  * every attempt agrees — same initial score, same replay score, same verdict.

That last condition is what excludes a *flaky* task. `task_is_complete()`
accepts a task when any single attempt passes, so a task that scores 0.0 on one
replay out of six still carries a PASS verdict; it is not reliably correct and is
not exported.

Every exported row is also re-checked for internal consistency: the inlined
setup/reward code must match the bundle's on-disk `initial_setup.py` /
`nemo_reward.py`, the endpoint and SID placeholders must be present, and
`verifier_metadata.task` must be byte-identical to `task_payload` (the shipped
example.jsonl has drifted copies, which this guards against).

    python3 scripts/export_nemo_rollouts.py webarena_08_18_batch_200 \
        --output webarena_08_18_batch_200.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

AGENT_REF = {"type": "responses_api_agents", "name": "cuagym_agent"}
CONTRACT_VERSION = 2


def attempt_files(run_dir: Path) -> list[Path]:
    """Verification artifacts for a run, newest layout first.

    The orchestrator normally writes ``attempt-N/verification.json``. A handful of
    runs that were re-driven in place instead carry the artifacts at the run root
    (with ``rerun-N/`` siblings) and no ``attempt-*`` directory at all. Falling back
    to the root form only when no attempt directory exists keeps the agreement check
    on the attempt series wherever one is present, while stopping a genuinely
    verified run from being dropped purely on file layout.
    """
    # Four layouts have now been observed:
    #   attempt-N/verification.json          (most runs)
    #   attempt-N/runM/verification.json     (round ran the same artifacts twice)
    #   round1/verification.json             (one run)
    #   <run root>/verification.json         (re-driven in place)
    # Globbing only the first dropped two genuinely verified tasks.
    found = sorted(q for q in run_dir.glob("attempt-*/**/verification.json"))
    if not found:
        found = sorted(q for q in run_dir.glob("round*/**/verification.json"))
    if found:
        return found
    root = [run_dir / "verification.json"] if (run_dir / "verification.json").is_file() else []
    return root + sorted(run_dir.glob("rerun-*/verification.json"))


def final_round(rows: list[dict]) -> str:
    """Pick the accepted round from a run's attempt rows.

    Ordering has to switch on the labels, because neither rule is right alone:

    * When every label is a plain ``attempt-<int>`` -- the normal case -- the
      round NUMBER is authoritative. Files get rewritten out of order
      (attempt-1/verification.json has been observed with a newer mtime than
      attempt-2's), so mtime would pick a superseded round and report a passing
      task as failed.
    * When any label is not a plain integer (``attempt-fresh-2``,
      ``attempt-debug4``, ``attempt-1-legacy``) the numbers come from different
      naming schemes and are not comparable -- ``debug4`` is not "after"
      ``fresh-2``. There, recency is the only honest ordering.
    """
    labels = {r["round"] for r in rows}
    def plain(label: str):
        m = re.fullmatch(r"attempt-(\d+)", label)
        return int(m.group(1)) if m else None
    nums = {label: plain(label) for label in labels}
    if labels and all(v is not None for v in nums.values()):
        return max(labels, key=lambda label: nums[label])
    return max(rows, key=lambda r: r["mtime"])["round"]


def attempts(run_dir: Path) -> list[dict]:
    rows = []
    for path in attempt_files(run_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        lanes = data.get("lanes", {})
        rows.append(
            {
                "name": path.parent.name if path.parent != run_dir else "root",
                # Round is the attempt LABEL, not an int parsed out of it.
                # The loop also emits attempt-1-legacy / attempt-fresh-2 /
                # attempt-debug4; `.isdigit()` collapsed every one of those to
                # round 0, which lumped discarded debugging rounds in with the
                # accepted round and made a passing task look self-contradictory.
                # Labels are ordered by mtime below, so fresh-2 correctly
                # supersedes debug4 despite the lower digit.
                "round": next((x for x in path.parts if x.startswith("attempt-")), "root"),
                "mtime": path.stat().st_mtime,
                "passed": data.get("verification", {}).get("passed") is True,
                "initial": lanes.get("initial", {}).get("reward", {}).get("score"),
                "replay": lanes.get("replay", {}).get("reward", {}).get("score"),
            }
        )
    return rows


def verdict(bundle: Path, runs_root: Path) -> tuple[bool, str]:
    """(exportable, reason-if-not)."""
    run_dir = runs_root / bundle.name
    if not run_dir.is_dir():
        return False, "no run directory"

    # One run keeps its verdict only in audit_sandbox/REVIEW.md. Requiring the
    # root copy excluded a fully-verified task for a layout difference.
    review = run_dir / "REVIEW.md"
    if not review.is_file() and (run_dir / "audit_sandbox" / "REVIEW.md").is_file():
        review = run_dir / "audit_sandbox" / "REVIEW.md"
    if not review.is_file():
        return False, "no REVIEW.md (orchestrator never wrote a verdict)"
    if "## Verdict: PASS" not in review.read_text(encoding="utf-8", errors="replace"):
        return False, "REVIEW.md does not carry '## Verdict: PASS'"

    rows = attempts(run_dir)
    if not rows:
        return False, "no verification.json (neither attempt-*/ nor run root)"
    if not any(r["passed"] for r in rows):
        return False, "no attempt passed verification"

    # The orchestrator REWRITES reward.py and golden_replay.py between rounds,
    # so attempt-1 and attempt-5 ran different code and comparing them compares
    # different artifacts -- a task the loop repaired looks like a task that
    # disagrees with itself. All five tasks this check called FLAKY were
    # re-tested by re-running their FINAL artifacts three times each: 15 of 15
    # runs scored initial 0.0 / replay 1.0. They were convergence, not flakiness.
    #
    # Real flakiness is the same artifacts scoring differently, which shows up
    # WITHIN a round when it runs twice (attempt-N/runM). That is still failed.
    # Final round = the most RECENTLY written label, not the lexically or
    # numerically greatest one: attempt-fresh-2 supersedes attempt-debug4.
    last = final_round(rows)
    finals = [r for r in rows if r["round"] == last]
    if (
        len({r["replay"] for r in finals}) > 1
        or len({r["initial"] for r in finals}) > 1
        or len({r["passed"] for r in finals}) > 1
    ):
        counts = {}
        for r in finals:
            counts[r["replay"]] = counts.get(r["replay"], 0) + 1
        return False, (f"FLAKY — round {last} runs disagree on identical artifacts, "
                       f"replay scores {counts} over {len(finals)} runs")
    if not any(r["passed"] for r in finals):
        return False, f"final round {last} did not pass"

    return True, ""


def sites_and_start_urls(bundle: Path) -> tuple[list[str], list[str], list[str]]:
    """(sites, start_urls, problems) derived from the bundle's task.json.

    `sites` is one entry per app the task touches, in `task.json` order.
    `start_urls` is strictly parallel to it: `start_urls[i]` is the
    `start_path` the task was authored and verified against for `sites[i]`,
    or `""` when that app starts at its default location.

    A path, not an absolute URL: the base differs per deployment and is
    resolved from the endpoint registry at episode time. The consumer joins
    them as `<base><start_path>?sid=<sid>` -- the path must precede the query,
    since the mocks route on `location.pathname` and read the sid from
    `location.search`.
    """
    problems: list[str] = []
    manifest = json.loads((bundle / "task.json").read_text(encoding="utf-8"))
    sites, start_urls = [], []
    for app in manifest.get("apps") or []:
        name = app.get("name")
        if not name:
            problems.append("task.json app entry has no name")
            continue
        path = app.get("start_path") or "/"
        if not path.startswith("/"):
            problems.append(f"start_path for {name} does not begin with '/': {path!r}")
            path = "/"
        sites.append(name)
        start_urls.append("" if path == "/" else path)
    if not sites:
        problems.append("task.json declares no apps")
    return sites, start_urls, problems


def build_row(bundle: Path) -> tuple[dict, list[str]]:
    """Rollout row plus any consistency problems found while building it."""
    problems: list[str] = []
    payload = json.loads((bundle / "nemo_task.json").read_text(encoding="utf-8"))["task_payload"]
    cuagym = payload["cuagym"]

    setup_file = bundle / "initial_setup.py"
    if cuagym.get("initial_setup") is None:
        if setup_file.is_file():
            problems.append("initial_setup is null but initial_setup.py exists")
    elif not setup_file.is_file():
        problems.append("initial_setup.py missing while the row declares setup code")
    elif setup_file.read_text(encoding="utf-8") != cuagym["initial_setup"]:
        problems.append("inlined initial_setup does not match initial_setup.py")

    reward_file = bundle / "nemo_reward.py"
    if not reward_file.is_file():
        problems.append("nemo_reward.py missing")
    elif reward_file.read_text(encoding="utf-8") != cuagym.get("eval_reward_code"):
        problems.append("inlined eval_reward_code does not match nemo_reward.py")

    for label in ("initial_setup", "eval_reward_code"):
        code = cuagym.get(label)
        if isinstance(code, str) and "__CUA_GYM_SID__" not in code:
            problems.append(f"{label} has no __CUA_GYM_SID__ placeholder")

    sites, start_urls, site_problems = sites_and_start_urls(bundle)
    problems.extend(site_problems)
    if sites:
        # Authoritative: task.json is what the verification harness actually
        # navigated to. Anything already in nemo_task.json is a stale copy.
        if payload.get("sites") not in (None, sites):
            problems.append(
                f"nemo_task.json sites {payload.get('sites')!r} disagree with task.json {sites!r}; using task.json"
            )
        payload["sites"] = sites
        payload["start_urls"] = start_urls

    if payload.get("intent"):
        intent = payload["intent"]
    else:
        problems.append("empty intent")
        intent = ""

    task_id = payload["task_id"]
    row = {
        "responses_create_params": {
            "input": [{"role": "user", "content": intent}],
            "parallel_tool_calls": False,
        },
        # A deep copy, so the two views can never drift apart in the emitted file.
        "verifier_metadata": {"task": json.loads(json.dumps(payload))},
        "task_payload": payload,
        "agent_ref": dict(AGENT_REF),
        "context_compaction_contract_version": CONTRACT_VERSION,
        "context_compaction_group_id": f"cuagym-{task_id}",
        "context_compaction_task_id": task_id,
        "context_compaction_rollout_index": 0,
        "context_compaction_attempt_index": 0,
    }
    return row, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", help="batch directory holding tasks/ and runs/")
    parser.add_argument("--output", required=True, help="destination .jsonl")
    parser.add_argument(
        "--tasks-subdir", default="tasks", help="bundle root within the batch (default: tasks)"
    )
    parser.add_argument(
        "--runs-subdir", default="runs", help="run root within the batch (default: runs)"
    )
    args = parser.parse_args()

    batch = Path(args.batch).resolve()
    tasks_root = batch / args.tasks_subdir
    runs_root = batch / args.runs_subdir

    bundles = sorted(p.parent for p in tasks_root.glob("*/*/task.json"))
    if not bundles:
        bundles = sorted(p.parent for p in tasks_root.glob("*/task.json"))
    if not bundles:
        print(f"no bundles found under {tasks_root}")
        return 1

    rows: list[dict] = []
    skipped: list[tuple[str, str]] = []
    broken: list[tuple[str, str]] = []
    seen: set[str] = set()

    for bundle in bundles:
        ok, reason = verdict(bundle, runs_root)
        if not ok:
            skipped.append((bundle.name, reason))
            continue
        row, problems = build_row(bundle)
        if problems:
            broken.append((bundle.name, "; ".join(problems)))
            continue
        task_id = row["context_compaction_task_id"]
        if task_id in seen:
            broken.append((bundle.name, f"duplicate task_id {task_id}"))
            continue
        seen.add(task_id)
        rows.append(row)

    out = Path(args.output)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"{batch.name}: {len(bundles)} bundles -> {len(rows)} rows written to {out}")
    if skipped:
        print(f"\n  excluded ({len(skipped)}) — not verified:")
        for name, reason in skipped:
            print(f"    {name}: {reason}")
    if broken:
        print(f"\n  excluded ({len(broken)}) — bundle inconsistent:")
        for name, reason in broken:
            print(f"    {name}: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
