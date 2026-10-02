#!/usr/bin/env python3
"""List tier-1 templates that are VERIFIED, for tier-2 instance-variant authoring.

A template qualifies only if its run directory satisfies all three conditions in
TASK3.md §9 — REVIEW.md carries `## Verdict: PASS`, at least one attempt reports
`verification.passed`, and every attempt agrees. That is the same standard
`export_nemo_rollouts.py` enforces, reused here so a broken template can never
spawn variants.

    python3 scripts/_b3_verified_templates.py <site> [--out FILE]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUNS = Path("output/runs")


def attempts(run_dir: Path) -> list[dict]:
    rows = []
    for path in sorted(run_dir.glob("attempt-*/verification.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        lanes = data.get("lanes", {})
        rows.append(
            {
                "passed": data.get("verification", {}).get("passed") is True,
                "initial": lanes.get("initial", {}).get("reward", {}).get("score"),
                "replay": lanes.get("replay", {}).get("reward", {}).get("score"),
            }
        )
    return rows


def verified(task_id: str) -> tuple[bool, str]:
    run_dir = RUNS / task_id
    if not run_dir.is_dir():
        return False, "no run directory"
    review = run_dir / "REVIEW.md"
    if not review.is_file():
        return False, "no REVIEW.md"
    if "## Verdict: PASS" not in review.read_text(encoding="utf-8", errors="replace"):
        return False, "REVIEW.md not PASS"
    rows = attempts(run_dir)
    if not rows:
        return False, "no attempts"
    if not any(r["passed"] for r in rows):
        return False, "no attempt passed"
    if (
        len({r["replay"] for r in rows}) > 1
        or len({r["initial"] for r in rows}) > 1
        or len({r["passed"] for r in rows}) > 1
    ):
        return False, "flaky - attempts disagree"
    return True, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("site")
    ap.add_argument("--out")
    args = ap.parse_args()

    root = Path("output/tasks") / args.site
    lines, skipped = [], []
    for path in sorted(root.glob("*/task_instruction.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        tid = data["task_id"]
        # A variant of a variant is not wanted; only instantiate tier-1 templates.
        manifest = json.loads((path.parent / "task.json").read_text(encoding="utf-8"))
        if (manifest.get("metadata") or {}).get("dedup_standard") == "instance_variant":
            continue
        ok, why = verified(tid)
        if ok:
            has_setup = (path.parent / "initial_setup.py").is_file()
            lines.append(
                f"{tid} | {data['difficulty']} | setup={'yes' if has_setup else 'none'} "
                f"| {data['task_instruction']}"
            )
        else:
            skipped.append(f"{tid} | {why}")

    body = "\n".join(lines) + ("\n" if lines else "")
    if args.out:
        Path(args.out).write_text(body or "(no verified templates yet)\n", encoding="utf-8")
    else:
        print(body, end="")
    print(f"{args.site}: {len(lines)} verified templates, {len(skipped)} not (yet) verified")
    for s in skipped[:10]:
        print("   skip:", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
