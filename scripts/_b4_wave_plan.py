#!/usr/bin/env python3
"""Build output/wave_plan.json — the 60 authoring lanes and their exact quotas.

Corpus targets (TASK4.md S1): 600 tasks, 150 per site, 15 topics per site, 10
tasks per topic.

    difficulty  0 easy / 240 medium / 360 hard   -> 4M / 6H per lane
    style       450 terse / 150 explicit         -> see STYLE_SPLIT below
    start_path  >= 420 (70%) at "/"              -> >= 7 per lane
    shape       ~180 retrieval_writeback (30%)   -> 3 per lane

The style split does not divide evenly: 150 tasks per site at 75% is 112.5
terse. So two sites carry 113 terse / 37 explicit and two carry 112 / 38, which
sums to exactly 450 / 150. Within a site the same rounding recurs — 15 lanes of
10 cannot each be 7.5 terse — so lanes are dealt 8 terse or 7 terse to hit the
site total exactly. Every lane's numbers are therefore explicit rather than
derived at check time, and `check_lane_quota.py` holds each lane to its own row.

    python3 scripts/_b4_wave_plan.py --slugs output/topic_slugs.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SITES = ("gitlab", "reddit", "shopping", "shopping_admin")

TASKS_PER_LANE = 10
LANES_PER_SITE = 15
MEDIUM_PER_LANE = 4
HARD_PER_LANE = 6
RETRIEVAL_PER_LANE = 3
ROOT_MIN_PER_LANE = 7  # 70% of 10, the batch floor

# Terse totals per site; 113+113+112+112 = 450, explicit 37+37+38+38 = 150.
STYLE_SPLIT = {"gitlab": 113, "reddit": 113, "shopping": 112, "shopping_admin": 112}


def terse_per_lane(site_terse_total: int) -> list[int]:
    """Deal `site_terse_total` terse slots across 15 lanes of 10 tasks.

    Lanes get 8 or 7 terse so the site total lands exactly: 113 = 8*8 + 7*7,
    112 = 7*8 + 8*7. Anything else would leave the corpus split unreachable.
    """
    eights = site_terse_total - 7 * LANES_PER_SITE
    if not 0 <= eights <= LANES_PER_SITE:
        raise ValueError(f"cannot deal {site_terse_total} terse across {LANES_PER_SITE} lanes")
    return [8] * eights + [7] * (LANES_PER_SITE - eights)


def build(slugs: dict[str, list[str]]) -> list[dict]:
    plan: list[dict] = []
    for site in SITES:
        site_slugs = slugs.get(site) or []
        if len(site_slugs) != LANES_PER_SITE:
            raise SystemExit(
                f"{site}: got {len(site_slugs)} slugs, need exactly {LANES_PER_SITE}. "
                "If the topic plan honestly supports fewer, say so and rebalance "
                "deliberately rather than letting the builder guess."
            )
        for index, (slug, terse) in enumerate(zip(site_slugs, terse_per_lane(STYLE_SPLIT[site]))):
            plan.append({
                "site": site,
                "slug": slug,
                "section": index + 1,
                "n": TASKS_PER_LANE,
                "medium": MEDIUM_PER_LANE,
                "hard": HARD_PER_LANE,
                "terse": terse,
                "explicit": TASKS_PER_LANE - terse,
                "root_min": ROOT_MIN_PER_LANE,
                "retrieval": RETRIEVAL_PER_LANE,
            })
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slugs", default="output/topic_slugs.json",
                        help="JSON mapping site -> list of 15 topic slugs")
    parser.add_argument("--out", default="output/wave_plan.json")
    args = parser.parse_args()

    slugs = json.loads(Path(args.slugs).read_text(encoding="utf-8"))
    plan = build(slugs)
    Path(args.out).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    totals = {
        "lanes": len(plan),
        "tasks": sum(l["n"] for l in plan),
        "medium": sum(l["medium"] for l in plan),
        "hard": sum(l["hard"] for l in plan),
        "terse": sum(l["terse"] for l in plan),
        "explicit": sum(l["explicit"] for l in plan),
        "retrieval": sum(l["retrieval"] for l in plan),
        "root_min": sum(l["root_min"] for l in plan),
    }
    print(json.dumps(totals, indent=2))

    expected = {"lanes": 60, "tasks": 600, "medium": 240, "hard": 360,
                "terse": 450, "explicit": 150, "retrieval": 180, "root_min": 420}
    bad = {k: (totals[k], v) for k, v in expected.items() if totals[k] != v}
    if bad:
        print(f"\nPLAN DOES NOT MEET TASK4 TARGETS (got, want): {bad}")
        return 1
    print(f"\nwrote {args.out}: totals match TASK4.md exactly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
