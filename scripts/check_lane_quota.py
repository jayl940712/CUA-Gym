#!/usr/bin/env python3
"""Hold one authoring lane to its own row of output/wave_plan.json.

`preflight_bundles.py` checks that each *bundle* is well formed, and reports the
distribution over a whole site directory. Neither catches the failure that
actually costs the most: a lane that satisfied every per-bundle rule and still
delivered the wrong **mix**.

That failure is invisible bundle-by-bundle. A lane assigned 8 terse / 2 explicit
that writes 10 terse produces ten individually valid bundles, and the shortfall
only surfaces as a corpus-level miss once the other 59 lanes are done — by which
point the agent that wrote it is long gone and the fix means re-authoring tasks
from a cold start. Checking immediately, while the author is still live and
still holds the topic in context, is perhaps twenty times cheaper.

    python3 scripts/check_lane_quota.py <lane_index>

Exit 0 when the lane conforms, 1 when it does not. The failure text is written
to be handed straight back to the authoring agent as a repair brief, so it says
what to do rather than only what is wrong.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PLAN = Path("output/wave_plan.json")


def lane_bundles(lane: dict) -> list[Path]:
    root = Path("output/tasks") / lane["site"]
    return sorted(p.parent for p in root.glob(f"{lane['slug']}_*/task.json"))


def audit(lane: dict) -> tuple[list[str], dict]:
    bundles = lane_bundles(lane)
    difficulty: Counter[str] = Counter()
    style: Counter[str] = Counter()
    roots = 0
    retrieval = 0
    deep: list[str] = []

    for bundle in bundles:
        try:
            instruction = json.loads((bundle / "task_instruction.json").read_text())
            meta = json.loads((bundle / "task.json").read_text()).get("metadata") or {}
        except Exception:  # noqa: BLE001 — malformed bundles are the gate's job
            continue
        difficulty[instruction.get("difficulty")] += 1
        style[meta.get("style")] += 1
        if meta.get("shape") == "retrieval_writeback":
            retrieval += 1
        if instruction.get("start_path") == "/":
            roots += 1
        else:
            deep.append(f"{bundle.name} -> {instruction.get('start_path')!r}")

    observed = {
        "delivered": len(bundles),
        "medium": difficulty["medium"],
        "hard": difficulty["hard"],
        "easy": difficulty["easy"],
        "terse": style["terse"],
        "explicit": style["explicit"],
        "root_starts": roots,
        "retrieval_writeback": retrieval,
        "deep_starts": deep,
    }

    problems: list[str] = []
    if len(bundles) != lane["n"]:
        problems.append(
            f"delivered {len(bundles)} bundles, assigned {lane['n']}. If the topic "
            "genuinely cannot yield that many distinct medium/hard tasks, say so "
            "explicitly in GENERATION.md — but do not leave the shortfall silent."
        )
    if difficulty["easy"]:
        problems.append(
            f"{difficulty['easy']} bundle(s) labelled `easy`; batch 4 has no easy quota. "
            "Relabel upward only if the work genuinely exceeds the label, otherwise "
            "deepen the task into a real medium (2-3 dependent mutations, or one "
            "mutation whose target must be derived)."
        )
    if difficulty["medium"] != lane["medium"] or difficulty["hard"] != lane["hard"]:
        problems.append(
            f"difficulty is {difficulty['medium']}M/{difficulty['hard']}H, assigned "
            f"{lane['medium']}M/{lane['hard']}H. Relabel upward only where the work "
            "genuinely exceeds the label; otherwise rewrite the task. Do not move the "
            "label to fit the quota — a hard task must satisfy >= 2 hard_criteria and "
            "be a chain, where step N's output constrains step N+1."
        )
    if style["terse"] != lane["terse"] or style["explicit"] != lane["explicit"]:
        problems.append(
            f"style is {style['terse']}T/{style['explicit']}E, assigned "
            f"{lane['terse']}T/{lane['explicit']}E. This is a corpus requirement: the "
            "batch must land 450 terse / 150 explicit and a terse-only lane cannot be "
            "compensated for elsewhere. An explicit task is not a worse task — it is "
            "the right shape for a chain whose honest end state cannot be exactly "
            "specified without 'and N other things unchanged'."
        )
    stray = sum(v for k, v in style.items() if k not in ("terse", "explicit"))
    if stray:
        problems.append(f"{stray} bundle(s) carry no valid task.json metadata.style")
    if roots < lane["root_min"]:
        problems.append(
            f"only {roots} of {len(bundles)} start at '/', assigned at least "
            f"{lane['root_min']}. Deep starts: " + "; ".join(deep) + ". Note that "
            "'the agent would waste turns finding it' is explicitly NOT a valid reason "
            "— that navigation is the task."
        )
    if retrieval != lane["retrieval"]:
        problems.append(
            f"{retrieval} retrieval-writeback bundles, assigned {lane['retrieval']}. "
            "The scored value must be DERIVED from the site, never stated in the "
            "instruction, and must have exactly one correct answer under the seed — "
            "check for ties and record the margin."
        )
    notes = Path("output/tasks") / lane["site"] / "_batches" / lane["slug"] / "GENERATION.md"
    if not notes.is_file():
        problems.append(f"missing {notes}")
    return problems, observed


def summarise(index: int, lane: dict, observed: dict) -> str:
    return (
        f"lane {index} {lane['slug']}: delivered={observed['delivered']}/{lane['n']} "
        f"difficulty={observed['medium']}M/{observed['hard']}H "
        f"(want {lane['medium']}M/{lane['hard']}H) "
        f"style={observed['terse']}T/{observed['explicit']}E "
        f"(want {lane['terse']}T/{lane['explicit']}E) "
        f"root={observed['root_starts']} (want >={lane['root_min']}) "
        f"retrieval={observed['retrieval_writeback']} (want {lane['retrieval']})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", type=int, nargs="?", help="lane index; omit for all")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args()

    plan = json.loads(PLAN.read_text())
    indexes = [args.lane] if args.lane is not None else range(len(plan))

    failed = []
    payload = []
    for index in indexes:
        lane = plan[index]
        problems, observed = audit(lane)
        print(summarise(index, lane, observed))
        for problem in problems:
            print(f"  QUOTA - {problem}")
        payload.append({"lane": lane, "index": index, "observed": observed,
                        "problems": problems})
        if problems:
            failed.append(index)

    if args.lane is None:
        print(f"\n{len(plan) - len(failed)}/{len(plan)} lanes conform to their quota")
        if failed:
            print("off quota:", failed)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
