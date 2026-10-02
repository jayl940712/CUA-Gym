#!/usr/bin/env python3
"""Track rewards that read `initial_state`, before AND after verification.

TASK4.md S7 is unconditional: "Every reward reads `current_state` only; never
diff against `initial_state`." Authors comply — but the *verification* pipeline
rewrites rewards (`web-orchestrator.md:48` spawns `reward-gen` to "author or
audit deterministic reward.py"), and it has been observed to reintroduce an
`initial_state` diff into a bundle an author had already repaired, then pass it.

So compliance must be measured on the FINAL artefact, after verification, not at
authoring time. This sweep reports both the source bundle and the run's own copy
so a divergence between them is visible.

    python3 scripts/_b4_s7_sweep.py
"""
from __future__ import annotations
import ast
import pathlib


def reads_initial_state(path: pathlib.Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    return any(
        isinstance(n, ast.Constant) and n.value == "initial_state"
        for n in ast.walk(tree)
    )


def main() -> int:
    bad_src, bad_run = [], []
    for reward in sorted(pathlib.Path("output/tasks").glob("*/*/reward.py")):
        if reads_initial_state(reward):
            bad_src.append(reward.parent.name)
    for reward in sorted(pathlib.Path("output/runs").glob("*/bundle/reward.py")):
        if reads_initial_state(reward):
            bad_run.append(reward.parent.parent.name)

    print(f"source bundles violating S7 : {len(bad_src)}")
    for name in bad_src:
        print(f"   {name}")
    print(f"verified run copies violating S7: {len(bad_run)}")
    for name in bad_run:
        print(f"   {name}")
    if bad_src or bad_run:
        print("\nRepair by asserting the exact end state (S0.3), never by deleting the")
        print("component, then RE-VERIFY. Do not edit a bundle whose run is live.")
    return 1 if (bad_src or bad_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
