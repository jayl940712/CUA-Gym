#!/usr/bin/env python3
"""One honest progress read for the batch-5 verification wave.

Batch 4 lost time to three ad-hoc checks in a row that each gave a misleading
answer -- an empty scan exiting 0, a JSON read against the wrong key path, and
a `grep '^## Verdict'` that matched a bare heading. This prints the whole
picture from the real files so no single number has to be trusted alone.

    python3 scripts/_b5_status.py [--runs output/runs] [--failures]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PASS_LINE = re.compile(r"^##\s*Verdict:\s*PASS\s*$", re.M)


def attempt_no(vj: Path) -> str:
    """Round LABEL for a verification.json, "" if it is not under an attempt.

    Two layouts occur and both are legitimate:
      attempt-N/verification.json           -- one verification per round
      attempt-N/runM/verification.json      -- the round ran the SAME artifacts
                                               twice, which is the cross-run
                                               agreement S9.2 actually asks for
    So the round number has to be found by walking ancestors, not by reading
    the immediate parent. Reading only the parent reported a healthy two-run
    round as "no attempt-N/verification.json".

    Rounds are not always named `attempt-<int>`. The loop also produces
    `attempt-1-legacy`, `attempt-fresh-2`, `attempt-debug4` and similar when it
    re-runs under a different mode or while chasing a broken replay. Those are
    real rounds holding a real verification.json, and rejecting them made two
    fully-passing runs report as "no attempt-N/verification.json" -- the same
    class of under-count this function was already fixed for twice.

    This returns the LABEL, not a number, because numbers drawn from different
    naming schemes are not comparable: parsing an integer out of each would rank
    `attempt-debug4` above `attempt-fresh-2` even though `fresh-2` ran later,
    and so pick a discarded debugging round as the accepted final state. Callers
    order rounds by recency instead (see `audit`).
    """
    for part in vj.parts:
        if part.startswith("attempt-"):
            return part
    return ""


def scores(run: Path) -> list[dict]:
    """Every attempt's (initial, replay, passed) triple, from verification.json."""
    out = []
    for vj in sorted(run.glob("**/verification.json")):
        try:
            doc = json.loads(vj.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        lanes = doc.get("lanes") or {}
        try:
            mtime = vj.stat().st_mtime
        except OSError:
            mtime = 0.0
        out.append({
            "round": attempt_no(vj),
            "mtime": mtime,
            "initial": ((lanes.get("initial") or {}).get("reward") or {}).get("score"),
            "replay": ((lanes.get("replay") or {}).get("reward") or {}).get("score"),
            "passed": bool(doc.get("passed") or (doc.get("verification") or {}).get("passed")),
        })
    return out


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


def audit(run: Path) -> tuple[str, list[str]]:
    """Return (state, problems). state is one of pass/fail/running."""
    problems: list[str] = []
    # The audit writes REVIEW.md at the run root in almost every run, but at
    # least one leaves it only in audit_sandbox/. Treating that as "still
    # running" hid a fully-passing task behind a permanent in-flight count.
    review = run / "REVIEW.md"
    if not review.is_file() and (run / "audit_sandbox" / "REVIEW.md").is_file():
        review = run / "audit_sandbox" / "REVIEW.md"
    attempts = scores(run)

    # A run writes verification.json before REVIEW.md, and golden_replay.py
    # before either. Treating any of those intermediate states as a failure
    # reports in-flight work as broken -- which it did on the first read.
    if not review.is_file():
        return "running", []

    if not review.is_file():
        problems.append("no REVIEW.md")
    elif not PASS_LINE.search(review.read_text(encoding="utf-8", errors="replace")):
        problems.append("REVIEW.md has no '## Verdict: PASS' line")

    if not attempts:
        problems.append("no verification.json")
    else:
        # The orchestrator REVISES reward.py and golden_replay.py between
        # adversarial rounds (web-orchestrator.md:11-12 routes failures back to
        # reward-gen / golden-browser). So attempt-1 and attempt-5 ran DIFFERENT
        # code, and comparing their scores compares two different artifacts --
        # a task that was repaired mid-loop looks like a task that disagrees
        # with itself. Three runs were misreported this way before this was
        # understood.
        #
        # The accepted state is the FINAL round. S9.2's "all attempts agree" is
        # about flakiness -- the same artifacts scoring differently -- and that
        # is what detect_flaky.py measures, by re-running the final artifacts.
        rounds = [a for a in attempts if a["round"]]
        if not rounds:
            problems.append("no attempt-N/verification.json")
        else:
            # Final round = the most RECENT label, not the highest number.
            # attempt-fresh-2 supersedes attempt-debug4 despite the lower digit.
            last = final_round(rounds)
            finals = [a for a in rounds if a["round"] == last]
            for key, want in (("initial", 0.0), ("replay", 1.0)):
                vals = {a[key] for a in finals if a[key] is not None}
                if not vals:
                    problems.append(f"final round {last} produced no {key} score")
                elif len(vals) > 1:
                    # Same artifacts, different score: this IS flakiness.
                    problems.append(
                        f"final round {last} runs disagree on {key}: {sorted(vals, key=str)}"
                    )
                elif next(iter(vals)) != want:
                    problems.append(
                        f"final round {last} {key} lane scored {next(iter(vals))!r}, need {want}"
                    )

    # S9.4 -- the golden replay must reach every scored control by clicking.
    # Most runs leave it at the run root; one layout leaves it under the round
    # that produced it (attempt-N/golden_replay.py). Prefer the root copy, else
    # take the highest-numbered round's, so the gate always inspects the replay
    # that was actually accepted.
    # Three layouts have been observed for where the accepted replay lands:
    #   <run>/golden_replay.py            (most runs)
    #   <run>/attempt-N/golden_replay.py
    #   <run>/round1/golden_replay.py
    # Rather than enumerate layouts as they appear, take the root copy if there
    # is one and otherwise the most recently written copy anywhere in the run.
    replay = run / "golden_replay.py"
    if not replay.is_file():
        found = [q for q in run.rglob("golden_replay.py") if "__pycache__" not in q.parts]
        if found:
            replay = max(found, key=lambda q: q.stat().st_mtime)
    if replay.is_file():
        rc = subprocess.run([sys.executable, "scripts/check_reachability.py", str(replay),
                             "--quiet"], capture_output=True, text=True)
        if rc.returncode:
            problems.append("golden_replay fails the click-reachability gate (S9.4)")
    elif not problems:
        problems.append("no golden_replay.py")

    return ("pass" if not problems else "fail"), problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default="output/runs")
    ap.add_argument("--failures", action="store_true", help="list every failing run")
    args = ap.parse_args()

    # A task the orchestrator gave up on has no REVIEW.md, which is
    # indistinguishable on disk from a task still running. batch_status.json is
    # the only place that difference is recorded, so it has to be consulted --
    # otherwise a dead run is reported as in-flight forever.
    status_file = Path("output/batch_status.json")
    orch_failed: set[str] = set()
    if status_file.is_file():
        try:
            for entry in json.loads(status_file.read_text()).values():
                if entry.get("status") in ("failed", "error", "timeout"):
                    orch_failed.add(Path(entry["task"]).parent.name)
        except Exception:  # noqa: BLE001
            pass

    root = Path(args.runs)
    # Skip archived attempts (".failed1", ".retry_*") -- they are kept for
    # forensics and are not live runs.
    runs = sorted(p for p in root.iterdir()
                  if p.is_dir() and not p.name.startswith(".")
                  and ".failed" not in p.name) if root.is_dir() else []
    tally = {"pass": 0, "fail": 0, "running": 0}
    failures: list[tuple[str, list[str]]] = []
    for run in runs:
        state, problems = audit(run)
        if run.name in orch_failed and state == "running":
            state = "fail"
            problems = [f"orchestrator marked this task failed (batch_status.json)"]
        tally[state] += 1
        if state == "fail":
            failures.append((run.name, problems))

    total = 600
    print(f"runs started {len(runs)}/{total} | "
          f"PASS {tally['pass']} | FAIL {tally['fail']} | in-flight {tally['running']} | "
          f"not started {total - len(runs)}")

    if failures:
        from collections import Counter
        kinds = Counter(p.split(":")[0][:58] for _, ps in failures for p in ps)
        print("\nfailure causes:")
        for kind, n in kinds.most_common(8):
            print(f"  {n:4}  {kind}")
    if args.failures:
        for name, ps in failures:
            print(f"\nFAIL {name}")
            for p in ps:
                print(f"     - {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
