#!/usr/bin/env python3
"""Reject rewards that pay out on an empty `current_state` (TASK4.md S9.5).

"Absence is not evidence of success" — the most expensive lesson of batch 3,
which shipped 27 rewards that scored above zero against `{}`, 18 of them a full
1.0. Two causes, both invisible to every static check:

* a helper falls back to the frozen seed row when the state is missing, so the
  reward grades the *seed* and the seed already satisfies the rubric;
* a check reads a missing key as success — `if "archived" not in project` is
  true for a project that does not exist at all.

Either way the reward pays an agent that did nothing, which is precisely the
behaviour reinforcement learning will find and exploit.

So: build the evidence document the runner would build (`cua_gym_web/evidence.py:118`
— same keys, same nesting, every value empty), call `evaluate()`, and require
**0.0 total and 0.0 for every component**. The per-component requirement matters
independently: a reward can total 0.0 while a component quietly pays, and that
component becomes free credit the moment a sibling component fires.

The full document shape is reproduced deliberately rather than passing a bare
`{}`. A reward that reads `final_text` and raises KeyError on a truncated
document has not demonstrated the S9.5 defect, and reporting it as one would
send an author hunting a bug that is not there.

A reward that *raises* is still reported: on this document an exception almost
always means the same missing guard, and a reward that cannot grade an empty
episode cannot grade a failed one either.

    python3 scripts/empty_state_probe.py output/tasks
    python3 scripts/empty_state_probe.py output/tasks/gitlab/<task_id>
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_evaluate(reward_path: Path):
    spec = importlib.util.spec_from_file_location(
        f"_empty_probe_{reward_path.parent.name}", reward_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {reward_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "evaluate", None)


def empty_evidence(manifest: dict) -> dict:
    """The runner's evidence document with every state emptied.

    Mirrors `cua_gym_web/evidence.py:118`. Apps are keyed by `source_name`; the
    mock `name` is added as an alias so a reward that looks itself up either way
    still finds an (empty) entry rather than falling through to a default.
    """
    apps: dict[str, dict] = {}
    for app in manifest.get("apps") or []:
        blank = {
            "initial_state": {},
            "current_state": {},
            "state_diff": {},
            "final_urls": [],
            "final_html": "",
            "final_text": "",
        }
        for key in (app.get("source_name"), app.get("name")):
            if key:
                apps[key] = blank
    return {
        "schema_version": 1,
        "task_id": manifest.get("task_id"),
        "instruction": manifest.get("instruction"),
        "lane": "empty-state-probe",
        # An episode that answered nothing. A reward that pays out on this is
        # exactly the S9.5 defect, so the probe must supply the key rather than
        # let reward code hit a KeyError and look like a different bug.
        "agent_answer": "",
        "apps": apps,
        "observations": [],
    }


def probe(bundle: Path) -> list[str]:
    try:
        manifest = json.loads((bundle / "task.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"task.json is unreadable: {exc}"]

    reward_path = bundle / manifest.get("reward_path", "reward.py")
    if not reward_path.is_file():
        return [f"missing {reward_path.name}"]

    try:
        evaluate = load_evaluate(reward_path)
    except Exception as exc:  # noqa: BLE001
        return [f"reward.py failed to import: {type(exc).__name__}: {exc}"]
    if evaluate is None:
        return ["reward.py defines no evaluate()"]

    try:
        result = evaluate(empty_evidence(manifest))
    except Exception as exc:  # noqa: BLE001
        return [
            f"evaluate() raised on an empty current_state: {type(exc).__name__}: {exc}"
            " — a reward that cannot grade an empty episode cannot grade a failed one"
        ]

    if not isinstance(result, dict):
        return [f"evaluate() returned {type(result).__name__}, expected a dict"]

    problems: list[str] = []
    try:
        score = float(result.get("score") or 0.0)
    except (TypeError, ValueError):
        return [f"evaluate() returned a non-numeric score {result.get('score')!r}"]
    if abs(score) > 1e-9:
        problems.append(
            f"scores {score} on an empty current_state; must be exactly 0.0 (S9.5)"
        )
    for component in result.get("components") or []:
        if not isinstance(component, dict):
            continue
        try:
            value = float(component.get("score") or 0.0)
        except (TypeError, ValueError):
            continue
        if abs(value) > 1e-9:
            problems.append(
                f"component {component.get('name')!r} pays {value} on an empty "
                "current_state; require a positive marker only a real episode produces"
            )
    return problems


def collect_bundles(roots: list[str]) -> list[Path]:
    bundles: list[Path] = []
    for raw in roots:
        root = Path(raw).resolve()
        if (root / "task.json").is_file():
            bundles.append(root)
            continue
        for pattern in ("*/task.json", "*/*/task.json"):
            bundles.extend(sorted(p.parent for p in root.glob(pattern)))
    return list(dict.fromkeys(bundles))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("roots", nargs="+")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    parser.add_argument("--json", dest="json_out", help="write the full report here")
    args = parser.parse_args()

    bundles = collect_bundles(args.roots)
    report: dict[str, list[str]] = {}
    failed = 0
    full_marks = 0

    for bundle in bundles:
        problems = probe(bundle)
        report[bundle.name] = problems
        if problems:
            failed += 1
            if any("scores 1.0" in p for p in problems):
                full_marks += 1
            print(f"PAYS-ON-EMPTY {bundle.name}")
            for problem in problems:
                print(f"     - {problem}")
        elif not args.quiet:
            print(f"clean         {bundle.name}")

    print(f"\n{len(bundles) - failed}/{len(bundles)} rewards score 0.0 on an empty current_state")
    if full_marks:
        print(f"{full_marks} of the failures award a FULL 1.0 for doing nothing")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
