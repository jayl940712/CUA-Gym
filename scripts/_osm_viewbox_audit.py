#!/usr/bin/env python3
"""Find tasks whose later geocodes flip when the map has already moved.

Ground truth is computed with the viewbox of a COLD "/" load, because that is
where every episode starts. But a task with more than one route geocodes again
after the first route has re-centred and zoomed the map, and Nominatim is biased
by the current view. A place name with two branches in the same city can then
resolve to the OTHER branch on the second leg.

That is not hypothetical: "Raab Pharmacy, Trenton" resolves to South Clinton
Avenue from a cold load and to Pennington Avenue once the map sits over North
Trenton, and the task built on it routed to the wrong pharmacy and scored 0.0.

Being a multi-hit name is NOT the defect -- 47 of 140 re-geocoding tasks contain
one and all but that single task verified. The defect is the top hit actually
CHANGING, so that is what is measured here: every place in the task is re-queried
under a local viewbox centred on each of the other places, and must come back as
the same OSM object.

    python3 scripts/_osm_viewbox_audit.py output/map400/tasks/map
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _osm_common as C  # noqa: E402

# Families that fill the Directions form a second time, after the first route
# has moved the map. Single-route families geocode once, from the cold view.
RE_GEOCODING = {"two_leg_time", "two_leg_distance", "nearest_of_three",
                # hard batch: these fill the Directions form repeatedly, so the
                # anchor and each stop are geocoded again under a moved map.
                "optimal_order", "nearest_of_five", "count_within_minutes",
                "nearest_then_attribute"}
# Half-widths of the local view, in degrees, spanning what the site can leave
# behind after fitting a route: a 1.5 km leg ends at zoom 17 (~0.005 deg) and a
# cross-city leg at zoom 13 (~0.05 deg). A single wide probe is not enough --
# tried at 0.05 alone, this audit MISSED the Raab Pharmacy task that had already
# failed verification, because that flip only happens on a tight view. Every
# width is probed and any flip condemns the task.
SPANS = (0.005, 0.01, 0.02, 0.05)


def local_hit(query: str, lat: float, lon: float, span: float):
    viewbox = f"{lon - span},{lat - span},{lon + span},{lat + span}"
    url = (f"http://{C.H}:8085/search?q={urllib.parse.quote(query)}&format=json"
           f"&viewbox={urllib.parse.quote(viewbox)}")
    with urllib.request.urlopen(url, timeout=25) as fh:
        hits = json.load(fh)
    return (hits[0].get("osm_type"), hits[0].get("osm_id")) if hits else None


def audit(bundle: pathlib.Path):
    manifest = json.loads((bundle / "task.json").read_text())
    meta = manifest["metadata"]
    if meta["family"] not in RE_GEOCODING:
        return None
    places = meta["places"]
    problems = []
    for place in places:
        want = tuple(place["osm"])
        for anchor in places:
            if anchor["query"] == place["query"]:
                continue
            for span in SPANS:
                got = local_hit(place["query"], *anchor["latlon"], span)
                if got != want:
                    problems.append(
                        f"{place['query']!r} resolves elsewhere when the map "
                        f"sits over {anchor['query']!r} (view +/-{span} deg)")
                    break
            if problems:
                break
    return {"task": manifest["task_id"], "family": meta["family"],
            "problems": problems}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    bundles = sorted(p.parent for p in pathlib.Path(args.root).glob("*/task.json"))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = [r for r in pool.map(audit, bundles) if r is not None]

    unstable = [r for r in rows if r["problems"]]
    for row in unstable:
        print(f"UNSTABLE {row['task']}")
        for problem in row["problems"]:
            print(f"         - {problem}")
    print(f"\n{len(rows) - len(unstable)}/{len(rows)} re-geocoding tasks are "
          f"stable under a moved map")
    if args.report:
        pathlib.Path(args.report).write_text(json.dumps(rows, indent=1) + "\n",
                                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
