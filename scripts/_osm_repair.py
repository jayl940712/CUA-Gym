#!/usr/bin/env python3
"""Replace map bundles that failed verification or the viewbox audit.

A full regeneration would be the wrong move here: it reshuffles the sampling
stream and so invalidates the 391 bundles that already verified against the live
site, forcing every one of them through verification again to prove something
already proved. This replaces only the condemned bundles, sampling from the same
pool with the same rules -- now including stable_under_moved_map(), which is what
condemned most of them -- and skipping anything already in the batch.

    python3 scripts/_osm_repair.py output/map400/tasks/map \
        --drop osm_twoleg_time_... --drop osm_nearest_...
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _osm_batch_gen as G  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--drop", action="append", default=[],
                    help="task_id to remove and replace; repeatable")
    ap.add_argument("--drop-file", default="",
                    help="JSON list of {task, problems} rows to drop")
    ap.add_argument("--pool", default="output/osm_pool_clean.json")
    ap.add_argument("--seed", type=int, default=20260909)
    ap.add_argument("--attempts", type=int, default=300)
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    drop = list(args.drop)
    if args.drop_file:
        drop += [r["task"] for r in json.loads(
            pathlib.Path(args.drop_file).read_text()) if r.get("problems")]
    drop = sorted(set(drop))

    wanted: collections.Counter = collections.Counter()
    for task_id in drop:
        bundle = root / task_id
        if not bundle.is_dir():
            print(f"  (already gone: {task_id})")
            continue
        family = json.loads((bundle / "task.json").read_text())["metadata"]["family"]
        wanted[family] += 1
        shutil.rmtree(bundle)
        print(f"  dropped {task_id}  [{family}]")

    if not wanted:
        print("nothing to replace")
        return 0

    # Rebuild the constraints the batch was generated under, from what SURVIVED,
    # so replacements cannot re-use a pair the corpus is already leaning on.
    existing = {p.parent.name for p in root.glob("*/task.json")}
    pair_uses: collections.Counter = collections.Counter()
    subject_uses: collections.Counter = collections.Counter()
    for manifest in root.glob("*/task.json"):
        places = json.loads(manifest.read_text())["metadata"]["places"]
        queries = [p["query"] for p in places]
        for x in queries:
            for y in queries:
                if x < y:
                    pair_uses[(x, y)] += 1
        subject_uses[queries[0]] += 1

    pool = json.loads(pathlib.Path(args.pool).read_text())
    by_city: dict[str, list] = collections.defaultdict(list)
    for entry in pool:
        by_city[entry["city"]].append(entry)
    cities = sorted(by_city)
    rng = random.Random(args.seed)
    routes = G.Routes()

    made = 0
    for family, count in wanted.items():
        done = 0
        misses = 0
        cycle = 0
        while done < count and misses < args.attempts * count:
            city = cities[cycle % len(cities)]
            cycle += 1
            places = by_city[city]
            misses += 1
            if len(places) < 4:
                continue
            spec = G.attempt(family, places, rng, routes)
            if spec is None or spec["slug"] in existing:
                continue
            keys = [tuple(sorted((x["query"], y["query"])))
                    for x in spec["places"] for y in spec["places"]
                    if x["query"] < y["query"]]
            if any(pair_uses[k] >= 2 for k in keys):
                continue
            if subject_uses[spec["places"][0]["query"]] >= 4:
                continue
            for k in keys:
                pair_uses[k] += 1
            subject_uses[spec["places"][0]["query"]] += 1
            spec["city"] = city
            existing.add(spec["slug"])
            G.write_bundle(root, spec)
            print(f"  built   {spec['slug']}  [{family}]  expected="
                  f"{spec['expected_rendered']!r}")
            done += 1
            made += 1
        if done < count:
            print(f"  WARNING: {family} replaced only {done} of {count}")

    print(f"\n{made} replacement bundles built; {len(list(root.glob('*/task.json')))} "
          f"bundles now in {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
