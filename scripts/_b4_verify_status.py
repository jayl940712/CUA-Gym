#!/usr/bin/env python3
"""Audit verified runs against TASK4.md S9's definition of done.

Written after three ad-hoc grep checks in a row gave misleading answers: an
empty scan that exited 0, a JSON read against the wrong key path that made
"all attempts agree" vacuously true, and a `grep -m1 '^## Verdict'` that
matched a bare section heading and reported a PASS as unresolved. The bar is
specific enough that it deserves one honest implementation.

A task is verified only when ALL hold (S9):
  1. REVIEW.md contains a line `## Verdict: PASS`
  2. at least one attempt reports verification.passed
  3. ALL attempts agree on initial score, replay score, and verdict
  4. initial scores exactly 0.0 and replay exactly 1.0
  5. no browser errors in either lane
(Reachability is S9.4 and is checked separately by check_reachability.py;
 empty-state is S9.5, checked by empty_state_probe.py.)

    python3 scripts/_b4_verify_status.py [--runs output/runs] [--verbose]
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

PASS_LINE = re.compile(r"^##\s*Verdict:\s*PASS\s*$", re.M)


def audit(run: Path) -> tuple[bool, list[str]]:
    problems: list[str] = []
    review = run / "REVIEW.md"
    if not review.is_file():
        return False, ["no REVIEW.md"]
    if not PASS_LINE.search(review.read_text(encoding="utf-8", errors="replace")):
        problems.append("REVIEW.md has no '## Verdict: PASS' line")

    attempts = sorted(run.glob("attempt-*/verification.json"))
    if not attempts:
        return False, problems + ["no attempt-*/verification.json"]

    sigs, passed_any = set(), False
    for f in attempts:
        try:
            v = json.loads(f.read_text())
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{f.parent.name}: unreadable ({exc})")
            continue
        lanes = v.get("lanes") or {}
        init = ((lanes.get("initial") or {}).get("reward") or {}).get("score")
        rep = ((lanes.get("replay") or {}).get("reward") or {}).get("score")
        # A killed run can leave a verification.json with null scores. That is
        # an incomplete run, not a passing one -- keep it out of the pass set
        # rather than letting it crash the audit or read as agreement.
        if init is None or rep is None:
            problems.append(f"{f.parent.name}: null score(s) — run did not complete")
            continue
        errs = len((lanes.get("initial") or {}).get("browser_errors") or []) + \
               len((lanes.get("replay") or {}).get("browser_errors") or [])
        passed_any |= bool((v.get("verification") or {}).get("passed"))
        sigs.add((init, rep))
        if errs:
            problems.append(f"{f.parent.name}: {errs} browser error(s)")
    if not passed_any:
        problems.append("no attempt reports verification.passed")
    if len(sigs) > 1:
        problems.append(f"attempts disagree: {sorted(sigs)}")
    elif sigs and sigs != {(0.0, 1.0)}:
        problems.append(f"scores are {sorted(sigs)}, require exactly (0.0, 1.0)")
    return not problems, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs", default="output/runs")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    runs = sorted(p for p in Path(args.runs).iterdir() if p.is_dir())
    good, bad = [], []
    for run in runs:
        ok, problems = audit(run)
        (good if ok else bad).append(run.name)
        if not ok:
            print(f"NOT-VERIFIED {run.name}")
            for p in problems:
                print(f"     - {p}")
        elif args.verbose:
            print(f"verified     {run.name}")
    print(f"\n{len(good)}/{len(runs)} runs meet the S9 bar "
          f"(PASS verdict, attempts agree, initial 0.0 -> replay 1.0, no browser errors)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
