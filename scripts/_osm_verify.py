#!/usr/bin/env python3
"""Verify map bundles against the live site, in parallel.

The batch orchestrator is not used here: it exists to have a sub-agent AUTHOR a
reward and a replay, and in this batch both are generated deterministically from
ground truth, so the only thing left to establish is the part a generator cannot
establish about itself -- that the frozen value is what the website actually
renders. That is exactly what a run of the two lanes shows:

    initial lane   no replay runs, so no answer is reported  -> must score 0.0
    replay lane    the replay reads the value OFF THE PAGE   -> must score 1.0

A replay that returns a different string than the reward expects scores 0.4, not
1.0, so a mismatch between the site and the frozen ground truth cannot pass.

It also avoids writing output/batch_status.json, which the orchestrator owns and
which still holds the previous batch's state.

    python3 scripts/_osm_verify.py output/map400/tasks/map \
            --runs output/map400/runs -c 8
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent


def verify(bundle: pathlib.Path, runs: pathlib.Path, timeout: int,
           label: str) -> dict:
    out = runs / bundle.name / label
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/run_webarena_task.py",
             str(bundle / "task.json"),
             "--replay", str(bundle / "golden_replay.py"),
             "--output", str(out), "--mode", "legacy"],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout,
        )
        (out / "stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (out / "stderr.txt").write_text(proc.stderr[-20000:], encoding="utf-8")
    except subprocess.TimeoutExpired:
        return {"task": bundle.name, "state": "timeout",
                "seconds": round(time.time() - started, 1)}

    result = {"task": bundle.name, "seconds": round(time.time() - started, 1)}
    verification = out / "verification.json"
    if not verification.is_file():
        result.update(state="no verification.json",
                      detail=proc.stderr.strip().splitlines()[-1:] or ["(no stderr)"])
        return result
    doc = json.loads(verification.read_text())
    lanes = doc.get("lanes") or {}
    initial = ((lanes.get("initial") or {}).get("reward") or {}).get("score")
    replay = ((lanes.get("replay") or {}).get("reward") or {}).get("score")
    # The answer the replay reported lives in the replay lane's evidence
    # document, not in verification.json, and it is worth carrying into the
    # report: it is the value the LIVE SITE rendered, so a passing row is
    # direct evidence that the frozen ground truth matches the site.
    answer = None
    replay_evidence = out / "replay-evidence.json"
    if replay_evidence.is_file():
        try:
            answer = json.loads(replay_evidence.read_text()).get("agent_answer")
        except ValueError:
            pass
    result.update(initial=initial, replay=replay, answer=answer)
    if initial == 0.0 and replay == 1.0:
        result["state"] = "pass"
    else:
        result["state"] = "fail"
        errors = ((lanes.get("replay") or {}).get("browser_errors") or [])
        result["detail"] = errors[:2]
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--runs", default="output/map400/runs")
    ap.add_argument("--label", default="attempt-1")
    ap.add_argument("-c", "--concurrency", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=900, help="Seconds per task")
    ap.add_argument("--only-failing", action="store_true",
                    help="Re-run only tasks whose previous label did not pass")
    ap.add_argument("--previous", default="",
                    help="Report JSON from an earlier pass, for --only-failing")
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    os.environ.setdefault("CUA_GYM_WEBARENA_MAP_URL", "http://18.116.12.228:3000")
    bundles = sorted(p.parent for p in pathlib.Path(args.root).glob("*/task.json"))
    if args.only_failing and args.previous:
        previous = json.loads(pathlib.Path(args.previous).read_text())
        keep = {r["task"] for r in previous if r["state"] != "pass"}
        bundles = [b for b in bundles if b.name in keep]

    runs = pathlib.Path(args.runs)
    results: list[dict] = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(verify, b, runs, args.timeout, args.label)
                   for b in bundles]
        for future in futures:
            result = future.result()
            results.append(result)
            done += 1
            if result["state"] != "pass":
                print(f"[{done}/{len(bundles)}] {result['state'].upper():<8} "
                      f"{result['task']}  initial={result.get('initial')} "
                      f"replay={result.get('replay')} "
                      f"answer={result.get('answer')!r} "
                      f"{result.get('detail', '')}", flush=True)
            elif done % 10 == 0:
                passed = sum(1 for r in results if r["state"] == "pass")
                print(f"[{done}/{len(bundles)}] {passed} passing", flush=True)

    report = pathlib.Path(args.report or (runs / f"report_{args.label}.json"))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    passed = sum(1 for r in results if r["state"] == "pass")
    print(f"\n{passed}/{len(results)} verified 0.0 -> 1.0   report: {report}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
