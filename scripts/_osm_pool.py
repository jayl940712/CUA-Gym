#!/usr/bin/env python3
"""Harvest a pool of place strings that provably resolve on THIS deployment.

TASK_MAP.md section 7.1 is the biggest authoring risk in this batch: a place
string that reads fine can return zero hits, or -- worse -- silently resolve
somewhere else entirely ("Cleveland Museum of Art" returns a museum in Boston
here). Hand-written place lists are therefore not trustworthy, so nothing is
hand-written: every entry below is discovered FROM the deployment and then
round-tripped through the exact query string a task will ask the agent to type.

    1. ask Nominatim "<category> in <city>" and keep the real POIs it returns
    2. build the task's query string from the POI's own name plus the city
    3. search that string and require the top hit to be the SAME osm object
    4. keep full-precision coordinates, the postcode, and the hit count

Step 3 is what makes the pool safe: it is the identical request the site makes
when the agent presses Go, so anything that survives it is reachable in the UI.

    python3 scripts/_osm_pool.py --out output/osm_pool.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _osm_common as C  # noqa: E402

# Metro areas inside the deployment's coverage. The viewbox spans roughly
# 39.4-46.2 N and 82.8-67.4 W, so Baltimore and Washington are OUT and are
# deliberately absent; Ohio's eastern half, Pennsylvania, New York and all of
# New England are in.
CITIES = [
    ("Pittsburgh", "Pennsylvania"), ("Philadelphia", "Pennsylvania"),
    ("Harrisburg", "Pennsylvania"), ("Scranton", "Pennsylvania"),
    ("Erie", "Pennsylvania"), ("Allentown", "Pennsylvania"),
    ("Cleveland", "Ohio"), ("Akron", "Ohio"), ("Youngstown", "Ohio"),
    ("Toledo", "Ohio"),
    ("Buffalo", "New York"), ("Rochester", "New York"),
    ("Syracuse", "New York"), ("Albany", "New York"), ("Ithaca", "New York"),
    ("Manhattan", "New York"), ("Brooklyn", "New York"),
    ("Boston", "Massachusetts"), ("Cambridge", "Massachusetts"),
    ("Worcester", "Massachusetts"), ("Springfield", "Massachusetts"),
    ("Providence", "Rhode Island"),
    ("New Haven", "Connecticut"), ("Hartford", "Connecticut"),
    ("Stamford", "Connecticut"),
    ("Portland", "Maine"), ("Burlington", "Vermont"),
    ("Manchester", "New Hampshire"), ("Portsmouth", "New Hampshire"),
    ("Newark", "New Jersey"), ("Princeton", "New Jersey"),
    ("Trenton", "New Jersey"), ("Jersey City", "New Jersey"),
    ("Wilmington", "Delaware"),
]

# Amenity classes that produce named, individually addressable POIs. Categories
# whose members are mostly unnamed (bench, parking) or wildly duplicated
# (bus stop) are excluded -- they cannot survive the round-trip check anyway.
CATEGORIES = [
    "university", "college", "hospital", "museum", "library", "park",
    "hotel", "theatre", "stadium", "supermarket", "pharmacy", "cafe",
    "restaurant", "school", "bank", "post office", "fire station",
    "police station", "train station", "cinema", "sports centre", "zoo",
]


def _name(display_name: str) -> str:
    return display_name.split(",")[0].strip()


def _ident(hit: dict) -> tuple:
    return (hit.get("osm_type"), hit.get("osm_id"))


def harvest_city(city: str, state: str) -> list[dict]:
    """Every POI in one city that survives the round-trip check."""
    found: dict[tuple, dict] = {}
    for category in CATEGORIES:
        try:
            hits = C.nominatim(f"{category} in {city}")
        except RuntimeError:
            continue
        for hit in hits:
            name = _name(hit.get("display_name", ""))
            # A name that is only a house number, or that carries a comma-free
            # street address, makes an ambiguous instruction. Require something
            # that reads like a proper noun.
            if len(name) < 4 or name[0].isdigit() or name.lower() == category:
                continue
            ident = _ident(hit)
            if ident in found:
                continue
            found[ident] = {
                "name": name,
                "query": f"{name}, {city}",
                "city": city,
                "state": state,
                "category": category,
                "osm": list(ident),
                "lat": float(hit["lat"]),
                "lon": float(hit["lon"]),
                "display_name": hit["display_name"],
                "postcode": (hit.get("address") or {}).get("postcode"),
            }
    # Round-trip: the query string a task will use must return THIS object first.
    kept = []
    for entry in found.values():
        try:
            hits = C.nominatim(entry["query"])
        except RuntimeError:
            continue
        if not hits or _ident(hits[0]) != tuple(entry["osm"]):
            continue
        entry["nominatim_hits"] = len(hits)
        # Re-read the coordinates from the round-trip hit: that is what the
        # site will actually route from, and it can differ in the last digits
        # from the category-search hit.
        entry["lat"] = float(hits[0]["lat"])
        entry["lon"] = float(hits[0]["lon"])
        entry["postcode"] = (hits[0].get("address") or {}).get("postcode")
        entry["display_name"] = hits[0]["display_name"]
        kept.append(entry)
    return kept


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="output/osm_pool.json")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    pool: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for city, entries in zip(
            [c for c, _ in CITIES],
            ex.map(lambda cs: harvest_city(*cs), CITIES),
        ):
            print(f"{city:<14} {len(entries):3} places", flush=True)
            pool.extend(entries)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pool, indent=1) + "\n", encoding="utf-8")
    print(f"\n{len(pool)} places -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
