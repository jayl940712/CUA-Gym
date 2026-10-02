#!/usr/bin/env python3
"""Build output/wave_plan.json — the 60 batch-5 authoring lanes.

Batch 4's plan dealt difficulty quotas to every lane. Batch 5 does not: the
contract derives difficulty from the skill chain and reports the resulting mix
instead of targeting one (`output/BATCH5_CONTRACT.md`, override 1). So a lane
row here carries the things that still *are* corpus requirements — the style
split, the root-start floor, the retrieval-writeback count — plus the skill
chain the lane is assigned, which is new and is the point of the batch.

The style split does not divide evenly. 150 tasks per site at 75% is 112.5
terse, so two sites carry 113/37 and two carry 112/38, summing to exactly
450/150. Within a site, 15 lanes of 10 cannot each be 7.5 terse, so lanes are
dealt 8 or 7 to hit the site total exactly. Every lane's numbers are explicit
rather than derived at check time, because batch 4 shipped six lane prompts
with a hardcoded split that was wrong for that lane.

    python3 scripts/_b5_wave_plan.py --topics output/topics.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SITES = ("gitlab", "reddit", "shopping", "shopping_admin")

TASKS_PER_LANE = 10
LANES_PER_SITE = 15
RETRIEVAL_PER_LANE = 3
ROOT_MIN_PER_LANE = 7  # 70% of 10, the batch floor

# Terse totals per site; 113+113+112+112 = 450, explicit 37+37+38+38 = 150.
STYLE_SPLIT = {"gitlab": 113, "reddit": 113, "shopping": 112, "shopping_admin": 112}

RETRIEVAL_SKILLS = {f"R{i}" for i in range(1, 11)}
ACTION_SKILLS = {f"A{i}" for i in range(1, 14)}
ALL_SKILLS = RETRIEVAL_SKILLS | ACTION_SKILLS

REQUIRED_TOPIC_KEYS = ("slug", "skills", "chain", "entities", "writeback", "analogues")


def terse_per_lane(site_terse_total: int) -> list[int]:
    """Deal `site_terse_total` terse slots across 15 lanes of 10 tasks."""
    eights = site_terse_total - 7 * LANES_PER_SITE
    if not 0 <= eights <= LANES_PER_SITE:
        raise ValueError(f"cannot deal {site_terse_total} terse across {LANES_PER_SITE} lanes")
    return [8] * eights + [7] * (LANES_PER_SITE - eights)


def validate_topic(site: str, index: int, topic: dict) -> list[str]:
    problems = []
    for key in REQUIRED_TOPIC_KEYS:
        if not topic.get(key):
            problems.append(f"{site}[{index}] missing {key!r}")
    skills = topic.get("skills") or []
    unknown = [s for s in skills if s not in ALL_SKILLS]
    if unknown:
        problems.append(f"{site}[{index}] unknown skill id(s) {unknown}")
    if skills and not any(s in RETRIEVAL_SKILLS for s in skills):
        problems.append(f"{site}[{index}] skill chain {skills} names no retrieval skill")
    if skills and not any(s in ACTION_SKILLS for s in skills):
        problems.append(f"{site}[{index}] skill chain {skills} names no action skill")
    return problems


def build(topics: dict[str, list[dict]]) -> tuple[list[dict], list[str]]:
    plan: list[dict] = []
    problems: list[str] = []
    for site in SITES:
        site_topics = topics.get(site) or []
        if len(site_topics) != LANES_PER_SITE:
            problems.append(
                f"{site}: got {len(site_topics)} topics, need exactly {LANES_PER_SITE}"
            )
            continue
        for index, (topic, terse) in enumerate(
            zip(site_topics, terse_per_lane(STYLE_SPLIT[site]))
        ):
            problems.extend(validate_topic(site, index, topic))
            plan.append({
                "site": site,
                "slug": topic["slug"],
                "section": index + 1,
                "n": TASKS_PER_LANE,
                "terse": terse,
                "explicit": TASKS_PER_LANE - terse,
                "root_min": ROOT_MIN_PER_LANE,
                "retrieval": RETRIEVAL_PER_LANE,
                "skills": topic["skills"],
                "chain": topic["chain"],
                "entities": topic["entities"],
                "writeback": topic["writeback"],
                "analogues": topic["analogues"],
                "notes": topic.get("notes", ""),
            })
    return plan, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topics", default="output/topics.json")
    parser.add_argument("--out", default="output/wave_plan.json")
    args = parser.parse_args()

    topics = json.loads(Path(args.topics).read_text(encoding="utf-8"))
    plan, problems = build(topics)
    if problems:
        print("TOPIC PLAN IS NOT USABLE:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    Path(args.out).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    totals = {
        "lanes": len(plan),
        "tasks": sum(l["n"] for l in plan),
        "terse": sum(l["terse"] for l in plan),
        "explicit": sum(l["explicit"] for l in plan),
        "retrieval": sum(l["retrieval"] for l in plan),
        "root_min": sum(l["root_min"] for l in plan),
    }
    print(json.dumps(totals, indent=2))

    expected = {"lanes": 60, "tasks": 600, "terse": 450, "explicit": 150,
                "retrieval": 180, "root_min": 420}
    bad = {k: (totals[k], v) for k, v in expected.items() if totals[k] != v}
    if bad:
        print(f"\nPLAN DOES NOT MEET BATCH-5 TARGETS (got, want): {bad}")
        return 1

    # Skill coverage is the point of the batch, so report it at plan time --
    # a skill absent here can only be absent from the corpus, and that is much
    # cheaper to fix now than after 600 bundles exist.
    covered = {s for lane in plan for s in lane["skills"]}
    missing = sorted(ALL_SKILLS - covered, key=lambda s: (s[0], int(s[1:])))
    print(f"\nwrote {args.out}: totals match the batch-5 contract")
    print(f"skill coverage {len(covered)}/{len(ALL_SKILLS)}")
    if missing:
        print(
            f"NOT COVERED BY ANY LANE: {missing}\n"
            "Each of these is a benchmark skill no batch-5 task will train. If a "
            "mock genuinely cannot support one, that belongs in the final report "
            "as a finding; if it can, reassign a lane."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
