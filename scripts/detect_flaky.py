#!/usr/bin/env python3
"""Flag tasks whose replay attempts disagree.

`task_is_complete()` accepts a task when ANY attempt passes, so a task that
scores 1.0 on five attempts and 0.0 on a sixth ships as PASS with no record
that it ever flaked. This sweep reads the verification artifacts already on
disk and reports every task where the attempts do not agree.

Read-only: writes a single report file, touches nothing else.
"""

import json
import sys
from collections import Counter
from pathlib import Path

RUNS = Path("output/runs")
REPORT = Path("output/FLAKY_REPORT.md")


def attempts(run_dir):
    rows = []
    for path in sorted(run_dir.glob("attempt-*/verification.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        lanes = data.get("lanes", {})
        rows.append(
            {
                "name": path.parent.name,
                "passed": data.get("verification", {}).get("passed") is True,
                "initial": lanes.get("initial", {}).get("reward", {}).get("score"),
                "replay": lanes.get("replay", {}).get("reward", {}).get("score"),
                "errors": sum(len(l.get("browser_errors", [])) for l in lanes.values()),
            }
        )
    return rows


def main():
    flaky, clean, empty = [], 0, 0
    for run_dir in sorted(p for p in RUNS.iterdir() if p.is_dir()):
        rows = attempts(run_dir)
        if not rows:
            empty += 1
            continue
        replay = {r["replay"] for r in rows}
        initial = {r["initial"] for r in rows}
        verdicts = {r["passed"] for r in rows}
        if len(replay) > 1 or len(initial) > 1 or len(verdicts) > 1:
            flaky.append((run_dir.name, rows))
        else:
            clean += 1

    lines = [
        "# Flaky task report",
        "",
        f"Scanned {clean + len(flaky) + empty} run directories: "
        f"**{clean} consistent**, **{len(flaky)} flaky**, {empty} with no attempts.",
        "",
        "A task is flaky when its attempts disagree on the replay score, the",
        "initial score, or the overall verdict. These ship as PASS today because",
        "`task_is_complete()` only requires one passing attempt.",
        "",
    ]
    if not flaky:
        lines += ["No disagreement found.", ""]
    for name, rows in flaky:
        counts = Counter(r["replay"] for r in rows)
        lines += [
            f"## {name}",
            "",
            f"replay scores: {dict(counts)} over {len(rows)} attempts",
            "",
            "| attempt | initial | replay | passed | browser errors |",
            "|---|---|---|---|---|",
        ]
        for r in rows:
            lines.append(
                f"| {r['name']} | {r['initial']} | {r['replay']} | "
                f"{'yes' if r['passed'] else '**no**'} | {r['errors']} |"
            )
        lines.append("")

    REPORT.write_text("\n".join(lines))
    print("\n".join(lines[:6]))
    print(f"report written to {REPORT}")
    return 1 if flaky else 0


sys.exit(main())
