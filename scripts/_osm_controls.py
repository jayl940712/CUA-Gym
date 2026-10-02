#!/usr/bin/env python3
"""Negative controls for the map batch (TASK_MAP.md section 5.1).

Passing verification proves a reward CAN reach 1.0. It says nothing about what
else reaches 1.0, and the property that matters most here cannot be observed
from a passing run at all: an agent that states the right answer without ever
opening the route must score 0.0, not 0.6. So every bundle is scored against a
synthetic evidence document for each scenario below and the whole table has to
match, exactly.

    right answer + the intended route      1.0
    right answer, never routed             0.0   <- the anti-guessing property
    routed, wrong answer                   0.4
    routed with the wrong engine           0.0
    right answer, route in another city    0.0
    empty episode                          0.0

    python3 scripts/_osm_controls.py output/map400/tasks/map
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import sys

SITE = "http://18.116.12.228:3000"


def load_reward(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(f"r_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence(urls, answer):
    return {"schema_version": 1, "task_id": "control", "instruction": "",
            "lane": "control", "agent_answer": answer,
            "apps": {"map": {"initial_state": {}, "current_state": {},
                             "state_diff": {}, "final_urls": urls,
                             "final_html": "", "final_text": ""}},
            "observations": []}


def route_url(engine, frm, to):
    return (f"{SITE}/directions?engine={engine}"
            f"&route={frm[0]:.3f}%2C{frm[1]:.3f}%3B{to[0]:.3f}%2C{to[1]:.3f}"
            f"#map=14/{frm[0]:.4f}/{frm[1]:.4f}")


def wrong_answers(module) -> list[str]:
    """Answers that are wrong in exactly one way each."""
    expected = module.EXPECTED_RENDERED
    if module.CHECK == "coords":
        lat, lon = module.EXPECTED_COORDS
        # A tenth of a degree is ~11 km -- a different part of the city, not a
        # rounding difference.
        return [f"{lat + 0.1:.7f}, {lon:.7f}", f"{lat:.7f}, {lon + 0.1:.7f}"]
    if module.CHECK == "tag":
        return ["not the value that is on the page at all"]
    if module.CHECK == "ordered":
        labels = [label for label, _ in module.ORDER_LABELS]
        total = module.EXPECTED_TOTAL
        wrong_order = [labels[1], labels[0]] + labels[2:]
        return [" > ".join(labels) + f": {total + 9}",      # right order, wrong total
                " > ".join(wrong_order) + f": {total}"]     # right total, wrong order
    if module.CHECK == "postcode":
        return [str((int(expected) + 11) % 100000).zfill(5)]
    if module.CHECK in ("clock", "minutes"):
        minutes = module.EXPECTED_MINUTES + 7
        return [f"{minutes // 60}:{minutes % 60:02d}", str(minutes)]
    if module.CHECK == "labelled_clock":
        label, clock = expected.split(": ", 1)
        hours, mins = (int(x) for x in clock.split(":"))
        shifted = hours * 60 + mins + 7
        other = next(name for name, _ in module.LABEL_GROUPS if name != label)
        return [f"{label}: {shifted // 60}:{shifted % 60:02d}",   # right thing, wrong time
                f"{other}: {clock}"]                              # right time, wrong thing
    return ["%.1f km" % ((module.EXPECTED_METRES + 5000) / 1000.0)]


def check(bundle: pathlib.Path) -> list[str]:
    module = load_reward(bundle / "reward.py")
    right = module.EXPECTED_RENDERED
    problems = []

    def score(urls, answer):
        return module.evaluate(evidence(urls, answer))["score"]

    if module.GATE == "info":
        path = module.INFO_PATHS[0]
        good = [f"{SITE}{path}"]
        # The comparable mistake for a lookup is opening the wrong object.
        kind, _, number = path.strip("/").partition("/")
        wrong_work = [f"{SITE}/{kind}/{int(number) + 7}"]
        # And stopping at the search results without opening anything.
        far_work = [f"{SITE}/search?query=whatever#map=19/40.0/-75.0"]
    elif module.GATE == "search":
        good = [f"{SITE}/search?query={module.SEARCH_NEEDLE.replace(' ', '%20')}"
                f"#map=19/40.0/-75.0"]
        # "wrong engine" has no analogue for a lookup: the comparable mistake is
        # searching for something else, so that is what is substituted.
        wrong_work = [f"{SITE}/search?query=somewhere%20else#map=7/42.8/-75.1"]
        far_work = [f"{SITE}/"]
    else:
        engine, frm, to = module.ACCEPTED_ROUTES[0]
        good = [route_url(engine, frm, to)]
        other = next((e for e in ("fossgis_osrm_car", "fossgis_osrm_bike",
                                  "fossgis_osrm_foot")
                      if e not in {r[0] for r in module.ACCEPTED_ROUTES}), None)
        wrong_work = [route_url(other, frm, to)] if other else []
        # Same engine, both endpoints displaced by two degrees -- another city.
        far_work = [route_url(engine, (frm[0] + 2, frm[1] + 2),
                              (to[0] + 2, to[1] + 2))]

    if (got := score(good, right)) != 1.0:
        problems.append(f"right answer + intended work scored {got}, need 1.0")
    if (got := score([], right)) != 0.0:
        problems.append(f"right answer without ever working scored {got}, need 0.0")
    if (got := score([f"{SITE}/"], right)) != 0.0:
        problems.append(f"right answer on the landing page scored {got}, need 0.0")
    for bad in wrong_answers(module):
        if (got := score(good, bad)) != 0.4:
            problems.append(f"work done, wrong answer {bad!r} scored {got}, need 0.4")
    if wrong_work and (got := score(wrong_work, right)) != 0.0:
        problems.append(f"wrong engine/search scored {got}, need 0.0")
    if (got := score(far_work, right)) != 0.0:
        problems.append(f"work in another city scored {got}, need 0.0")
    if (got := score([], "")) != 0.0:
        problems.append(f"empty episode scored {got}, need 0.0")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    bundles = sorted(p.parent for p in pathlib.Path(args.root).glob("*/reward.py"))
    failures = 0
    for bundle in bundles:
        problems = check(bundle)
        if problems:
            failures += 1
            print(f"FAIL {bundle.name}")
            for problem in problems:
                print(f"     - {problem}")
        elif not args.quiet:
            print(f"ok   {bundle.name}")
    print(f"\n{len(bundles) - failures}/{len(bundles)} bundles pass every "
          f"negative control")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
