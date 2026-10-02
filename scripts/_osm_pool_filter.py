#!/usr/bin/env python3
"""Reduce the harvested pool to places that are safe to build tasks on.

The round-trip check in _osm_pool.py proves a query string resolves to a
specific OSM object. It does NOT prove the object is where its city label says:
"Wilmington Post Office, Wilmington" round-trips cleanly to a post office in
Wilmington, New York, 700 km from the Delaware city the label claims. Pairing
that with a Delaware place would produce a nine-hour "walk across town".

Three filters, all of them about task quality rather than about resolvability:

  geography  the hit must sit within 0.5 degrees of the city itself, where the
             city's position is geocoded here rather than averaged from the
             harvest -- an average over contaminated entries moves with the
             contamination. Matching on the state NAME appearing in the address
             does not work: Pennsylvania addresses render as "Pittsburgh,
             Allegheny County, 15222, United States" with no state at all, and
             that filter silently deleted every Pittsburgh and Philadelphia
             place in the pool.
  chains     a name that occurs more than three times across the pool is a
             brand, not a landmark. Which branch the agent lands on is then a
             coin flip that the coordinate check would score as failure.
  ambiguity  keep the hit count, and prefer low counts downstream.

    python3 scripts/_osm_pool_filter.py --in output/osm_pool.json \
                                        --out output/osm_pool_clean.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _osm_common as C  # noqa: E402

MIN_PER_CITY = 30
MAX_SAME_NAME = 3
MAX_DEGREES_FROM_CENTRE = 0.5


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", default="output/osm_pool.json")
    ap.add_argument("--out", dest="dst", default="output/osm_pool_clean.json")
    args = ap.parse_args()

    pool = json.loads(pathlib.Path(args.src).read_text())
    dropped = collections.Counter()

    # 1./2. within half a degree of the city's own geocoded position
    centres = {}
    for city, state in {(e["city"], e["state"]) for e in pool}:
        hits = C.nominatim(f"{city}, {state}")
        # A city outside the extract does not geocode at all. Its harvested
        # entries are then whatever same-named place elsewhere the search found,
        # so the whole city goes.
        if hits:
            centres[city] = (float(hits[0]["lat"]), float(hits[0]["lon"]))

    near = []
    for e in pool:
        if e["city"] not in centres:
            dropped["city not in the extract"] += 1
            continue
        lat0, lon0 = centres[e["city"]]
        if (abs(e["lat"] - lat0) <= MAX_DEGREES_FROM_CENTRE
                and abs(e["lon"] - lon0) <= MAX_DEGREES_FROM_CENTRE):
            near.append(e)
        else:
            dropped["far from city centre"] += 1

    # 3. brands, not landmarks
    name_counts = collections.Counter(e["name"] for e in near)
    kept = []
    for e in near:
        if name_counts[e["name"]] > MAX_SAME_NAME:
            dropped["chain name"] += 1
            continue
        kept.append(e)

    # 4. cities with too little data to pair within
    by_city = collections.Counter(e["city"] for e in kept)
    thin = {c for c, n in by_city.items() if n < MIN_PER_CITY}
    final = [e for e in kept if e["city"] not in thin]
    dropped["thin city"] = len(kept) - len(final)

    for e in final:
        e["centre"] = list(centres[e["city"]])

    pathlib.Path(args.dst).write_text(json.dumps(final, indent=1) + "\n",
                                      encoding="utf-8")
    print(f"{len(pool)} harvested -> {len(final)} usable")
    for reason, n in dropped.most_common():
        print(f"  dropped {n:5}  {reason}")
    print("  thin cities:", ", ".join(sorted(thin)) or "none")
    counts = collections.Counter(e["city"] for e in final)
    print("\n" + "  ".join(f"{c}:{n}" for c, n in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
