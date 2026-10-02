#!/usr/bin/env python3
"""Hold one batch-5 authoring lane to its row of output/wave_plan.json.

Differs from batch 4's `check_lane_quota.py` in two ways that follow from the
contract: there is no difficulty quota to enforce (difficulty is derived from
the skill chain and reported, not targeted), and there IS a skill assignment to
enforce, which batch 4 had no concept of.

The failure this catches is invisible bundle-by-bundle. A lane assigned the
`R2 -> R3 -> A7` chain that quietly writes ten `R9 -> A1` tasks produces ten
individually valid bundles; the skill shortfall only surfaces once all 60 lanes
are done, by which point the author is gone and the fix is a cold re-author.

    python3 scripts/_b5_lane_quota.py <lane_index>

Exit 0 when the lane conforms. The failure text is written to be handed
straight back to the authoring agent as a repair brief.
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
    skill_use: Counter[str] = Counter()
    roots = 0
    retrieval = 0
    deep: list[str] = []
    off_chain: list[str] = []
    no_analogue: list[str] = []

    assigned = set(lane["skills"])

    for bundle in bundles:
        try:
            instruction = json.loads((bundle / "task_instruction.json").read_text())
            meta = json.loads((bundle / "task.json").read_text()).get("metadata") or {}
        except Exception:  # noqa: BLE001 — malformed bundles are the gate's job
            continue
        difficulty[instruction.get("difficulty")] += 1
        style[meta.get("style")] += 1
        skills = meta.get("skills") or []
        skill_use.update(skills)
        # A lane may extend its chain, but it must actually contain it. A task
        # sharing no skill with its lane is in the wrong lane.
        if not (set(skills) & assigned):
            off_chain.append(f"{bundle.name} -> {skills}")
        if not (meta.get("official_analogues") or []):
            no_analogue.append(bundle.name)
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
        "skill_use": dict(skill_use),
    }

    problems: list[str] = []
    if len(bundles) != lane["n"]:
        problems.append(
            f"delivered {len(bundles)} bundles, assigned {lane['n']}. If the chain "
            "genuinely cannot yield that many distinct tasks, say so explicitly in "
            "GENERATION.md — but do not leave the shortfall silent."
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

    # Skill assignment. Every skill the lane was given must appear somewhere in
    # its ten tasks, or the corpus loses coverage no other lane restores.
    unused = sorted(assigned - set(skill_use))
    if unused:
        problems.append(
            f"lane skills {sorted(assigned)} but no bundle exercises {unused}. These "
            "are the skills this lane exists to cover; if the mock cannot support one, "
            "record that in GENERATION.md rather than dropping it silently."
        )
    if off_chain:
        problems.append(
            "bundle(s) share no skill with the lane's assigned chain: "
            + "; ".join(off_chain)
        )
    if no_analogue:
        problems.append(
            f"{len(no_analogue)} bundle(s) carry no metadata.official_analogues: "
            + ", ".join(no_analogue[:5])
        )

    if roots < lane["root_min"]:
        problems.append(
            f"only {roots} of {len(bundles)} start at '/', assigned at least "
            f"{lane['root_min']}. Deep starts: " + "; ".join(deep) + ". Note that "
            "'the agent would waste turns finding it' is explicitly NOT a valid reason "
            "— that navigation is the task."
        )
    if retrieval < lane["retrieval"]:
        problems.append(
            f"{retrieval} retrieval-writeback bundles, assigned at least "
            f"{lane['retrieval']}. The scored value must be DERIVED from the site, "
            "never stated in the instruction, and must have exactly one correct answer "
            "under the seed — check for ties and record the margin."
        )
    if difficulty["easy"]:
        problems.append(
            f"{difficulty['easy']} bundle(s) labelled `easy`. Difficulty is derived "
            "from the skill chain this round: a task with one retrieval and one action "
            "is `medium`. If it truly has neither, it does not belong in this batch."
        )
    notes = Path("output/tasks") / lane["site"] / "_batches" / lane["slug"] / "GENERATION.md"
    if not notes.is_file():
        problems.append(f"missing {notes}")
    return problems, observed


def summarise(index: int, lane: dict, observed: dict) -> str:
    return (
        f"lane {index} {lane['slug']}: delivered={observed['delivered']}/{lane['n']} "
        f"style={observed['terse']}T/{observed['explicit']}E "
        f"(want {lane['terse']}T/{lane['explicit']}E) "
        f"difficulty={observed['medium']}M/{observed['hard']}H (derived) "
        f"root={observed['root_starts']} (want >={lane['root_min']}) "
        f"retrieval={observed['retrieval_writeback']} (want >={lane['retrieval']}) "
        f"skills={sorted(observed['skill_use'])}"
    )


def orphan_bundles(plan: list[dict]) -> dict[str, list[str]]:
    """Bundles on disk that no lane's glob will ever match.

    This closes a hole that cost a lane. `preflight_bundles.py` accepts a bundle
    whose directory equals its `task_id` -- which is the rule -- and this file
    finds a lane's bundles by globbing `<slug>_*`. A lane that named its
    directories `<site>_<slug>_...` satisfies the first and is invisible to the
    second, so its ten bundles passed the gate while the lane audit reported
    `delivered=0/10`.

    A shortfall that is really a naming error looks exactly like a lane that
    wrote nothing, and the natural response to the latter -- re-run the lane --
    would have produced twenty bundles under one topic. So orphans are reported
    separately and loudly rather than folded into the per-lane counts.
    """
    slugs = {lane["slug"] for lane in plan}
    sites = {lane["site"] for lane in plan}
    orphans: dict[str, list[str]] = {}
    for site in sorted(sites):
        root = Path("output/tasks") / site
        if not root.is_dir():
            continue
        for bundle in sorted(p.parent for p in root.glob("*/task.json")):
            if not any(bundle.name.startswith(f"{slug}_") for slug in slugs):
                orphans.setdefault(site, []).append(bundle.name)
    return orphans


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", type=int, nargs="?", help="lane index; omit for all")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args()

    plan = json.loads(PLAN.read_text())
    indexes = [args.lane] if args.lane is not None else range(len(plan))

    failed = []
    payload = []
    corpus_skills: Counter[str] = Counter()
    for index in indexes:
        lane = plan[index]
        problems, observed = audit(lane)
        print(summarise(index, lane, observed))
        for problem in problems:
            print(f"  QUOTA - {problem}")
        corpus_skills.update(observed["skill_use"])
        payload.append({"lane": lane, "index": index, "observed": observed,
                        "problems": problems})
        if problems:
            failed.append(index)

    if args.lane is None:
        orphans = orphan_bundles(plan)
        if orphans:
            total = sum(len(v) for v in orphans.values())
            print(
                f"\nORPHANED: {total} bundle(s) match no lane slug and are invisible "
                "to every per-lane count above."
            )
            for site, names in orphans.items():
                print(f"  {site}:")
                for name in names[:12]:
                    print(f"    - {name}")
                if len(names) > 12:
                    print(f"    ... and {len(names) - 12} more")
            print(
                "  A lane whose directories do not start with its slug reports "
                "delivered=0 while its work sits right here. Rename the directories "
                "(and the task_id inside each, which must match) rather than "
                "re-running the lane -- re-running would double-staff the topic."
            )
            failed.append(-1)
        print(f"\n{len(plan) - len([f for f in failed if f >= 0])}/{len(plan)} lanes conform to their quota")
        off = [f for f in failed if f >= 0]
        if off:
            print("off quota:", off)
        print("\ncorpus skill coverage (tasks exercising each skill):")
        for skill, count in sorted(corpus_skills.items(),
                                   key=lambda kv: (kv[0][0], int(kv[0][1:]))):
            print(f"  {skill:>3} {count}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
