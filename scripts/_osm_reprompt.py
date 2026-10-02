#!/usr/bin/env python3
"""Rewrite every bundle's instruction with an explicit answer-format contract.

The episode ends with a `terminate` tool call and the reward sees ONLY that
call's `answer` string. The original instructions asked for the right value but
never said what the string had to look like, which left a class of correct
answers scoring zero: the parsers take the first value they find, so "walking
takes 20 minutes and cycling 12, so the difference is 8" reads as 20.

The wording comes from _osm_batch_gen.answer_spec(), the same function the
generator now uses, so a re-generated batch and this corpus cannot disagree.
Nothing else in the bundle changes -- reward.py, nemo_reward.py and
golden_replay.py are untouched -- but the tasks are re-verified afterwards
anyway, so that what ships is exactly what was verified.

    python3 scripts/_osm_reprompt.py output/map400/tasks/map
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _osm_batch_gen as G  # noqa: E402
import _osm_common as C  # noqa: E402

LABEL_TO_ENGINE = {label: engine for engine, label in C.ENG_LABEL.items()}


def legs_of(bundle: pathlib.Path) -> list[dict]:
    """The replay's LEGS list -- the artifact that actually drives the form."""
    source = (bundle / "golden_replay.py").read_text(encoding="utf-8")
    match = re.search(r"^LEGS = (\[.*?^\])", source, re.S | re.M)
    return json.loads(match.group(1)) if match else []


def instruction_for(bundle: pathlib.Path, manifest: dict) -> str:
    meta = manifest["metadata"]
    family = meta["family"]
    places = meta["places"]
    legs = legs_of(bundle)
    labels = [leg["engine_label"] for leg in legs]

    if family in ("route_time", "route_distance"):
        ask = "time" if family == "route_time" else "distance"
        noun = "total travel time" if ask == "time" else "route distance"
        a, b = places
        return (f"On the map site, get directions from {a['query']} to "
                f"{b['query']} using the {labels[0]} routing engine and read "
                f"the {noun} off the directions panel. "
                + G.answer_spec(f"route_{ask}"))

    if family == "place_postcode":
        return (f"On the map site, search for {places[0]['query']} and read the "
                f"five-digit postcode out of the search result for it. "
                + G.answer_spec("place_postcode"))

    if family == "compare_modes":
        a, b = places
        # LEGS run slower-first, so recover the pair in the order the original
        # instruction named them rather than in outcome order.
        modes = [G.MODE_NAME[LABEL_TO_ENGINE[label]] for label in labels]
        e1, e2 = sorted(labels, key=lambda label: ("Foot", "Bicycle", "Car")
                        .index(label.split()[0]))
        m1 = G.MODE_NAME[LABEL_TO_ENGINE[e1]]
        m2 = G.MODE_NAME[LABEL_TO_ENGINE[e2]]
        assert set(modes) == {m1, m2}
        return (f"On the map site, compare the {e1} and {e2} routes from "
                f"{a['query']} to {b['query']} and work out which is faster. "
                + G.answer_spec("compare_modes", (m1, m2)))

    if family == "time_gap":
        a, b = places
        e1, e2 = sorted(labels, key=lambda label: ("Foot", "Bicycle", "Car")
                        .index(label.split()[0]))
        return (f"On the map site, look up the {e1} route and the {e2} route "
                f"from {a['query']} to {b['query']}, and work out how many "
                f"whole minutes longer the slower of the two takes. "
                + G.answer_spec("time_gap"))

    if family in ("two_leg_time", "two_leg_distance"):
        a, b, c = places
        ask = "time" if family.endswith("time") else "distance"
        tail = ("Add the two travel times together. " + G.answer_spec("two_leg_time")
                if ask == "time" else
                "Add the two distances together. " + G.answer_spec("two_leg_distance"))
        return (f"On the map site, travel from {a['query']} to {b['query']} "
                f"using the {labels[0]} routing engine, then from {b['query']} "
                f"to {c['query']} using the {labels[1]} routing engine. {tail}")

    if family == "nearest_of_three":
        origin, *candidates = places
        names = ", ".join(f'"{p["query"]}"' for p in candidates[:-1])
        return (f'On the map site, work out which of {names} or '
                f'"{candidates[-1]["query"]}" is the shortest {labels[0]} '
                f'trip from "{origin["query"]}". '
                + G.answer_spec("nearest_of_three"))

    raise ValueError(family)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    args = ap.parse_args()

    changed = 0
    for manifest_file in sorted(pathlib.Path(args.root).glob("*/task.json")):
        bundle = manifest_file.parent
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        instruction = instruction_for(bundle, manifest)
        if instruction == manifest["instruction"]:
            continue
        manifest["instruction"] = instruction
        manifest_file.write_text(json.dumps(manifest, indent=1) + "\n",
                                 encoding="utf-8")
        side = bundle / "task_instruction.json"
        doc = json.loads(side.read_text(encoding="utf-8"))
        doc["instruction"] = instruction
        side.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        changed += 1
    print(f"{changed} instructions rewritten with an explicit answer contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
