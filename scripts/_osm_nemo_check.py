#!/usr/bin/env python3
"""Prove each bundle's TRAINING reward reproduces its VERIFIED score.

Verification never executes nemo_reward.py, so nothing in the normal gate chain
looks at it. That gap hid a fatal defect: the file imported a sibling reward.py
and used __file__, but cuagym/episode_code.py::run_code pipes the source to
`python -` in an empty temporary directory, where __file__ is undefined and no
sibling exists. Every map task would have verified at 1.0 and crashed at
rollout.

So this runs each nemo_reward.py the way the rollout runs it -- same invocation,
same empty cwd, same allowlisted environment -- feeding it the replay lane's own
answer and final URLs, and requires:

    REWARD: 1.0   on the replay evidence   (matches verification)
    REWARD: 0.0   on an empty episode      (no answer, no URLs)

    python3 scripts/_osm_nemo_check.py output/map400 --label attempt-2
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# cuagym/episode_code.py::_ENV_ALLOWLIST -- the rollout child gets nothing else.
ENV_ALLOWLIST = ("PATH", "LANG", "LC_ALL", "TZ", "HOME", "TMPDIR",
                 "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")


def run_like_rollout(source: str, answer: str, urls: list, scratch: str) -> str:
    env = {name: os.environ[name] for name in ENV_ALLOWLIST if name in os.environ}
    env["CUA_GYM_AGENT_ANSWER"] = answer
    env["CUA_GYM_FINAL_URLS"] = json.dumps(urls)
    proc = subprocess.run([sys.executable, "-"], input=source, env=env,
                          cwd=scratch, capture_output=True, text=True,
                          timeout=120)
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith("REWARD:"):
            return line.split(":", 1)[1].strip()
    return f"NO REWARD LINE (rc={proc.returncode}) {proc.stderr.strip()[-200:]}"


def check(bundle: pathlib.Path, runs: pathlib.Path, label: str) -> list[str]:
    import tempfile
    source = (bundle / "nemo_reward.py").read_text(encoding="utf-8")
    # A task repaired after a failed round has its passing evidence under a
    # later attempt, so fall back to the most recent one rather than insisting
    # on a fixed label -- pinning attempt-1 reported a healthy task as missing.
    evidence_file = runs / bundle.name / label / "replay-evidence.json"
    if not evidence_file.is_file():
        found = sorted((runs / bundle.name).glob("attempt-*/replay-evidence.json"),
                       key=lambda q: q.stat().st_mtime)
        if not found:
            return [f"{bundle.name}: no replay evidence under {runs / bundle.name}"]
        evidence_file = found[-1]
    evidence = json.loads(evidence_file.read_text())
    answer = evidence.get("agent_answer") or ""
    urls = (evidence.get("apps", {}).get("map", {}) or {}).get("final_urls") or []

    problems = []
    with tempfile.TemporaryDirectory(prefix="cuagym-run-") as scratch:
        got = run_like_rollout(source, answer, urls, scratch)
        if got != "1.0":
            problems.append(f"{bundle.name}: replay evidence scored {got}, need 1.0")
        empty = run_like_rollout(source, "", [], scratch)
        if empty != "0.0":
            problems.append(f"{bundle.name}: empty episode scored {empty}, need 0.0")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("batch")
    ap.add_argument("--tasks-subdir", default="tasks/map")
    ap.add_argument("--label", default="attempt-2")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    batch = pathlib.Path(args.batch)
    runs = batch / "runs"
    bundles = sorted(p.parent for p in (batch / args.tasks_subdir).glob("*/task.json"))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda b: check(b, runs, args.label), bundles))

    failures = [p for problems in results for p in problems]
    for problem in failures[:20]:
        print("FAIL", problem)
    ok = sum(1 for problems in results if not problems)
    print(f"\n{ok}/{len(bundles)} training rewards reproduce the verified score "
          f"under the rollout's own execution model")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
