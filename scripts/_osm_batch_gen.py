#!/usr/bin/env python3
"""Generate the 400-task OpenStreetMap batch: 150 easy + 250 medium.

Every value a reward enforces is computed HERE, at authoring time, from the same
Nominatim and OSRM services the website calls, and then frozen into the bundle.
The rewards make no network call, run no LLM, and read no clock.

Difficulty follows TASK_MAP.md section 6:

  easy    one hop. The instruction names everything the agent needs; the work is
          driving the UI and reading one value off the panel.
  medium  two dependent retrieval hops where the reported value is DERIVED --
          a difference, a total, or the winner of a comparison. It cannot be
          transcribed from the instruction and it cannot be read off a single
          route, so an agent that runs one route and stops scores the 0.4
          proof-of-work component and nothing else.

Families:

  easy    route_time          A->B on one engine, report the rendered time
          route_distance      A->B on one engine, report the rendered distance
          place_postcode      search one place, report its postcode
  medium  compare_modes       two engines, same pair; report the faster MODE and
                              its time
          time_gap            two engines, same pair; report the gap in minutes
          two_leg_time        A->B then B->C on different engines; total minutes
          two_leg_distance    A->B then B->C; total kilometres
          nearest_of_three    which of three places is the shortest trip from X

Quality gates applied before a candidate is accepted are in ACCEPT_* below; the
important ones are margin gates. A comparison whose two sides render the same
number does not test anything, and a total that happens to equal one of its own
legs can be answered without doing the second leg.

    python3 scripts/_osm_batch_gen.py --out output/map400/tasks/map
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _osm_common as C  # noqa: E402

TMPL = HERE / "_osm"
REWARD_TMPL = (TMPL / "reward_tmpl.py").read_text()
REPLAY_ROUTE_TMPL = (TMPL / "replay_route_tmpl.py").read_text()
REPLAY_SEARCH_TMPL = (TMPL / "replay_search_tmpl.py").read_text()

MODE_NAME = {"foot": "walking", "bike": "cycling", "car": "driving"}
MODE_WORDS = {
    "walking": ["walk", "walks", "walking", "walked", "foot"],
    "cycling": ["cycle", "cycling", "bike", "bikes", "biking", "bicycle"],
    "driving": ["drive", "driving", "drove", "car"],
}
ALL_MODE_GROUPS = [[name, words] for name, words in MODE_WORDS.items()]

# Distance windows keep a route long enough to be a real trip and short enough
# that the answer is a plausible one -- a 40 km "walk" is neither.
WINDOW = {"foot": (500, 6000), "bike": (800, 12000), "car": (1000, 25000)}
MIN_LEG_MINUTES = 3
MARGIN_MINUTES = 3

# Categories whose members carry proper names a person would type into a search
# box. Everything else in the pool stays available as routing endpoints but is
# not used as the SUBJECT of a lookup task.
LANDMARKS = {"university", "college", "museum", "library", "park", "stadium",
             "hospital", "theatre", "hotel", "train station", "zoo", "cinema",
             "sports centre"}

STOPWORDS = {"the", "and", "of", "for", "saint", "st", "north", "south", "east",
             "west", "new", "old", "center", "centre", "school", "park",
             "library", "museum", "hotel", "station", "hall", "house", "city",
             "county", "street", "avenue", "college", "university", "hospital",
             "theatre", "theater", "cinema", "stadium", "number", "building"}


class Routes:
    """Memoised OSRM lookups, so a place pair is never routed twice."""

    def __init__(self) -> None:
        self._cache: dict[tuple, tuple] = {}
        self.calls = 0

    def get(self, engine: str, a: dict, b: dict):
        key = (engine, a["lat"], a["lon"], b["lat"], b["lon"])
        if key not in self._cache:
            self.calls += 1
            self._cache[key] = C.osrm(engine, (a["lat"], a["lon"]),
                                      (b["lat"], b["lon"]))
        return self._cache[key]


def rendered(engine: str, a: dict, b: dict, routes: Routes) -> dict:
    duration, distance = routes.get(engine, a, b)
    return {
        "engine": engine,
        "seconds": duration,
        "metres_raw": distance,
        "clock": C.fmt_time(duration),
        "minutes": round(duration / 60),
        "distance": C.fmt_dist(distance),
        "metres": _parse_rendered(C.fmt_dist(distance)),
    }


def _parse_rendered(text: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(km|m)", text)
    value = float(match.group(1))
    return value * 1000.0 if match.group(2) == "km" else value


def metre_tolerance(metres: float) -> float:
    """Half the granularity the site renders at, so neighbours stay distinct."""
    if metres < 1000:
        return 5.0
    if metres < 10000:
        return 60.0
    return 600.0


def token_of(name: str, others: list[str]) -> str | None:
    """A word that identifies this place and appears in no competitor's name.

    "Appears in no competitor's name" is the part that matters, and checking it
    only against the tokens already chosen is not enough: "City of Albany Boxing
    Program" and "Albany Pump Station" get the distinct tokens "Program" and
    "Albany", yet the winning answer "City of Albany Boxing Program: 0:07"
    mentions "Albany" first and so reads as naming the loser. Two tasks scored
    0.4 on their own correct answer before this was checked against the full
    names.
    """
    words = [w for w in re.findall(r"[A-Za-z]{4,}", name)
             if w.lower() not in STOPWORDS]
    words.sort(key=len, reverse=True)
    for word in words:
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.I)
        if not any(pattern.search(other) for other in others):
            return word
    return None


def leading_label(text: str, groups: list) -> str:
    """The reward's _leading_label, so the generator can check its own output."""
    best_at, best = None, ""
    for label, words in groups:
        for word in words:
            hit = re.search(r"\b" + re.escape(word) + r"\b", text, re.I)
            if hit and (best_at is None or hit.start() < best_at):
                best_at, best = hit.start(), label
    return best


# Half-widths of the map view a fitted route can leave behind, in degrees: a
# 1.5 km leg ends around zoom 17, a cross-city leg around zoom 13.
VIEW_SPANS = (0.005, 0.01, 0.02, 0.05)


def stable_under_moved_map(places: list[dict]) -> bool:
    """True if no place in the task re-geocodes elsewhere once the map moves.

    Ground truth uses the viewbox of a cold "/" load, but a task with more than
    one route fills the form again AFTER the first route has re-centred and
    zoomed the map, and Nominatim is biased by the current view. A name with two
    branches in one city then flips: "Raab Pharmacy, Trenton" is on South
    Clinton Avenue from a cold load and on Pennington Avenue once the map sits
    over North Trenton. A task built on that routes to the wrong pharmacy.

    Multi-hit names are not themselves disqualifying -- most keep the same top
    hit under any view, and rejecting all of them would throw away a third of
    the corpus for nothing. What is checked is the hit actually CHANGING.
    """
    for place in places:
        want = tuple(place["osm"])
        for anchor in places:
            if anchor["query"] == place["query"]:
                continue
            for span in VIEW_SPANS:
                if C.nominatim_local(place["query"], anchor["lat"],
                                     anchor["lon"], span) != want:
                    return False
    return True


def slugify(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower())).strip("_")


# --------------------------------------------------------------------------
# how the agent must format its answer
# --------------------------------------------------------------------------
# The episode ends when the agent calls the `terminate` tool, and the string in
# that call's `answer` field is the whole of what the reward sees (it arrives as
# CUA_GYM_AGENT_ANSWER). So the instruction has to state the exact form of that
# string, not merely ask for the value.
#
# The rewards parse tolerantly on purpose -- "0:25", "25 minutes" and "25" all
# read as 25 -- and that stays, because a precise prompt paired with a forgiving
# parser scores correct answers, while tightening both would fail an answer that
# is right but verbose. What the prompt buys is the case tolerance cannot fix:
# the parsers take the FIRST value they find, so "walking takes 20 minutes and
# cycling 12, so the difference is 8" reads as 20 and a correct answer scores
# zero. Telling the agent to put ONLY the value in `answer` removes that class.
TERMINATE = ('When you have the answer, call the `terminate` tool with '
             '`status` set to `"success"` and put the answer in its `answer` '
             'field. ')

ANSWER_SPEC = {
    "route_time": (
        TERMINATE + 'The `answer` field must contain only the travel time, '
        'written exactly as the "Time:" value on the directions panel, in '
        '`H:MM` form -- for example `0:25`. Do not add units, place names, or '
        'any explanation.'),
    "route_distance": (
        TERMINATE + 'The `answer` field must contain only the distance, '
        'written exactly as the "Distance:" value on the directions panel, '
        'including its unit and with no space before it -- for example `1.7km`, '
        'or `450m` for a distance under one kilometre. Do not add any other '
        'text.'),
    "place_postcode": (
        TERMINATE + 'The `answer` field must contain only the five digits of '
        'the postcode -- for example `15213`. Do not include the street, the '
        'city, or any explanation.'),
    "compare_modes": (
        TERMINATE + 'The `answer` field must contain exactly `<mode>: <time>`, '
        'where `<mode>` is the single word `__MODE1__` or `__MODE2__` and '
        '`<time>` is that route\'s travel time in `H:MM` form as the site '
        'shows it -- for example `__MODE1__: 0:25`. Name only the faster mode; '
        'do not mention the slower one or its time.'),
    "time_gap": (
        TERMINATE + 'The `answer` field must contain only the difference, as a '
        'whole number of minutes, digits only -- for example `8`. Do not '
        'include the two individual travel times, the word "minutes", or any '
        'explanation.'),
    "two_leg_time": (
        TERMINATE + 'The `answer` field must contain only the total, as a '
        'whole number of minutes, digits only -- for example `37`. Do not '
        'include the two individual leg times, the word "minutes", or any '
        'explanation.'),
    "two_leg_distance": (
        TERMINATE + 'The `answer` field must contain only the total distance '
        'in kilometres, to one decimal place, followed by a space and `km` -- '
        'for example `4.9 km`. Do not include the two individual leg distances '
        'or any explanation.'),
    "nearest_of_three": (
        TERMINATE + 'The `answer` field must contain exactly `<place>: '
        '<time>`, where `<place>` is that place\'s name exactly as written in '
        'this task but WITHOUT the city that follows the comma, and `<time>` '
        'is its travel time in `H:MM` form as the site shows it -- for example '
        '`Heinz Hall: 0:07`. Name only the closest place; do not mention the '
        'other two.'),
}


def answer_spec(family: str, modes: tuple = ()) -> str:
    spec = ANSWER_SPEC[family]
    for index, mode in enumerate(modes, start=1):
        spec = spec.replace(f"__MODE{index}__", mode)
    return spec


# --------------------------------------------------------------------------
# family builders. Each returns a spec dict or None if a quality gate failed.
# --------------------------------------------------------------------------

def _base(spec_id, family, difficulty, instruction, places, extra):
    return {"slug": spec_id, "family": family, "difficulty": difficulty,
            "instruction": instruction, "places": places, **extra}


def build_route_leg(engine, a, b, ask, routes):
    main = rendered(engine, a, b, routes)
    if main["minutes"] < MIN_LEG_MINUTES:
        return None
    low, high = WINDOW[engine]
    if not low <= main["metres_raw"] <= high:
        return None
    # Margin: the other two engines must render a DIFFERENT value, or the task
    # does not test the engine choice at all.
    others = {}
    for other in C.ENG_PORT:
        if other == engine:
            continue
        alt = rendered(other, a, b, routes)
        others[other] = alt["clock"] if ask == "time" else alt["distance"]
    mine = main["clock"] if ask == "time" else main["distance"]
    if mine in others.values():
        return None
    return main, others


def family_route(engine, a, b, ask, routes):
    built = build_route_leg(engine, a, b, ask, routes)
    if built is None:
        return None
    main, others = built
    slug = f"osm_{'time' if ask == 'time' else 'dist'}_{C.VERB[engine]}_" \
           f"{slugify(a['name'])[:24]}_to_{slugify(b['name'])[:24]}"
    noun = "total travel time" if ask == "time" else "route distance"
    example = "0:25" if ask == "time" else "1.7km"
    instruction = (
        f"On the map site, get directions from {a['query']} to {b['query']} "
        f"using the {C.ENG_LABEL[engine]} routing engine and read the {noun} "
        f"off the directions panel. " + answer_spec(f"route_{ask}")
    )
    return _base(slug, f"route_{ask}", "easy", instruction, [a, b], {
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[engine], "label": MODE_NAME[engine]}],
        "combine": ('readings[0]["clock"]' if ask == "time"
                    else 'readings[0]["distance"]'),
        "gate": "route",
        "accepted": [(C.ENG_PARAM[engine], a, b)],
        "check": "clock" if ask == "time" else "distance",
        "expected_minutes": main["minutes"] if ask == "time" else -1,
        "expected_metres": main["metres"] if ask == "distance" else -1.0,
        "metre_tol": metre_tolerance(main["metres"]),
        "label_groups": [],
        "expected_label": "",
        "expected_rendered": main["clock"] if ask == "time" else main["distance"],
        "margins": {"other_engines": others},
    })


def family_postcode(a, routes):
    if not a.get("postcode") or not re.fullmatch(r"\d{5}", a["postcode"]):
        return None
    slug = f"osm_postcode_{slugify(a['city'])}_{slugify(a['name'])[:32]}"
    instruction = (
        f"On the map site, search for {a['query']} and read the five-digit "
        f"postcode out of the search result for it. "
        + answer_spec("place_postcode")
    )
    return _base(slug, "place_postcode", "easy", instruction, [a], {
        "legs": [], "combine": "", "query": a["query"],
        "gate": "search",
        "search_needle": re.sub(r"[^a-z0-9]+", " ", a["name"].lower()).strip(),
        "accepted": [],
        "check": "postcode",
        "expected_minutes": -1, "expected_metres": -1.0, "metre_tol": 0.0,
        "label_groups": [], "expected_label": "",
        "expected_rendered": a["postcode"],
        "margins": {"nominatim_hits": a["nominatim_hits"]},
    })


def family_compare(e1, e2, a, b, routes):
    r1, r2 = rendered(e1, a, b, routes), rendered(e2, a, b, routes)
    if min(r1["minutes"], r2["minutes"]) < MIN_LEG_MINUTES:
        return None
    if abs(r1["minutes"] - r2["minutes"]) < MARGIN_MINUTES:
        return None
    for engine, reading in ((e1, r1), (e2, r2)):
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
    fast, slow = sorted((r1, r2), key=lambda r: r["minutes"])
    winner = MODE_NAME[fast["engine"]]
    # Same self-check as the nearest family: the expected answer has to resolve
    # to the winner under the reward's own reading rule.
    if leading_label(f"{winner}: {fast['clock']}", ALL_MODE_GROUPS) != winner:
        return None
    slug = f"osm_faster_{C.VERB[e1]}_{C.VERB[e2]}_" \
           f"{slugify(a['name'])[:22]}_to_{slugify(b['name'])[:22]}"
    instruction = (
        f"On the map site, compare the {C.ENG_LABEL[e1]} and {C.ENG_LABEL[e2]} "
        f"routes from {a['query']} to {b['query']} and work out which is "
        f"faster. " + answer_spec("compare_modes", (MODE_NAME[e1], MODE_NAME[e2]))
    )
    return _base(slug, "compare_modes", "medium", instruction, [a, b], {
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[slow["engine"]],
                  "label": MODE_NAME[slow["engine"]]},
                 {"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[fast["engine"]],
                  "label": MODE_NAME[fast["engine"]]}],
        "combine": ('"%s: %s" % (min(readings, key=lambda r: r["minutes"])["label"], '
                    'min(readings, key=lambda r: r["minutes"])["clock"])'),
        "gate": "route",
        "accepted": [(C.ENG_PARAM[e1], a, b), (C.ENG_PARAM[e2], a, b)],
        "check": "labelled_clock",
        "expected_minutes": fast["minutes"], "expected_metres": -1.0,
        "metre_tol": 0.0,
        "label_groups": ALL_MODE_GROUPS,
        "expected_label": winner,
        "expected_rendered": f"{winner}: {fast['clock']}",
        "margins": {"faster_minutes": fast["minutes"],
                    "slower_minutes": slow["minutes"],
                    "gap_minutes": slow["minutes"] - fast["minutes"]},
    })


def family_gap(e1, e2, a, b, routes):
    r1, r2 = rendered(e1, a, b, routes), rendered(e2, a, b, routes)
    if min(r1["minutes"], r2["minutes"]) < MIN_LEG_MINUTES:
        return None
    for engine, reading in ((e1, r1), (e2, r2)):
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
    gap = abs(r1["minutes"] - r2["minutes"])
    if gap < MARGIN_MINUTES:
        return None
    # The gap must not coincide with either leg's own time, or an agent that
    # ran one route and reported it would score as if it had run both.
    if gap in (r1["minutes"], r2["minutes"]):
        return None
    # Both derivations of the gap must agree: subtracting the two displayed
    # minute values, and rounding the raw difference. If they differ by a minute
    # the task has two defensible answers and only one of them scores.
    if gap != round(abs(r1["seconds"] - r2["seconds"]) / 60):
        return None
    slug = f"osm_gap_{C.VERB[e1]}_{C.VERB[e2]}_" \
           f"{slugify(a['name'])[:22]}_to_{slugify(b['name'])[:22]}"
    instruction = (
        f"On the map site, look up the {C.ENG_LABEL[e1]} route and the "
        f"{C.ENG_LABEL[e2]} route from {a['query']} to {b['query']}, and work "
        f"out how many whole minutes longer the slower of the two takes. "
        + answer_spec("time_gap")
    )
    slow, fast = sorted((r1, r2), key=lambda r: -r["minutes"])
    return _base(slug, "time_gap", "medium", instruction, [a, b], {
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[fast["engine"]],
                  "label": MODE_NAME[fast["engine"]]},
                 {"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[slow["engine"]],
                  "label": MODE_NAME[slow["engine"]]}],
        "combine": ('str(max(r["minutes"] for r in readings) '
                    '- min(r["minutes"] for r in readings))'),
        "gate": "route",
        "accepted": [(C.ENG_PARAM[e1], a, b), (C.ENG_PARAM[e2], a, b)],
        "check": "minutes",
        "expected_minutes": gap, "expected_metres": -1.0, "metre_tol": 0.0,
        "label_groups": [], "expected_label": "",
        "expected_rendered": str(gap),
        "margins": {"leg_minutes": [r1["minutes"], r2["minutes"]],
                    "gap_minutes": gap},
    })


def family_two_leg(e1, e2, a, b, c, ask, routes):
    r1 = rendered(e1, a, b, routes)
    r2 = rendered(e2, b, c, routes)
    for engine, reading in ((e1, r1), (e2, r2)):
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
    if min(r1["minutes"], r2["minutes"]) < MIN_LEG_MINUTES:
        return None

    if ask == "time":
        total = r1["minutes"] + r2["minutes"]
        # Both derivations must agree, and the total must not equal either leg,
        # so the second leg cannot be skipped.
        if total != round((r1["seconds"] + r2["seconds"]) / 60):
            return None
        if total in (r1["minutes"], r2["minutes"]):
            return None
        combine = 'str(sum(r["minutes"] for r in readings))'
        check, exp_min, exp_m = "minutes", total, -1.0
        tol = 0.0
        expected = str(total)
        ask_text = ("Add the two travel times together. "
                    + answer_spec("two_leg_time"))
    else:
        total_metres = r1["metres"] + r2["metres"]
        if total_metres < 1500:
            return None
        # The agent adds the two DISPLAYED distances. That sum must round to the
        # same one-decimal kilometre value as the true total, or the task again
        # has two defensible answers.
        if round(total_metres / 1000.0, 1) != round(
                (r1["metres_raw"] + r2["metres_raw"]) / 1000.0, 1):
            return None
        combine = '"%.1f km" % (sum(r["metres"] for r in readings) / 1000.0)'
        check, exp_min, exp_m = "distance", -1, total_metres
        tol = metre_tolerance(total_metres)
        expected = "%.1f km" % (total_metres / 1000.0)
        ask_text = ("Add the two distances together. "
                    + answer_spec("two_leg_distance"))

    if not stable_under_moved_map([a, b, c]):
        return None
    slug = (f"osm_twoleg_{ask}_{slugify(a['name'])[:16]}_"
            f"{slugify(b['name'])[:16]}_{slugify(c['name'])[:16]}")
    instruction = (
        f"On the map site, travel from {a['query']} to {b['query']} using the "
        f"{C.ENG_LABEL[e1]} routing engine, then from {b['query']} to "
        f"{c['query']} using the {C.ENG_LABEL[e2]} routing engine. {ask_text}"
    )
    return _base(slug, f"two_leg_{ask}", "medium", instruction, [a, b, c], {
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[e1], "label": "leg1"},
                 {"from": b["query"], "to": c["query"],
                  "engine_label": C.ENG_LABEL[e2], "label": "leg2"}],
        "combine": combine,
        "gate": "route",
        # Either leg is acceptable proof of work: which one is on screen at the
        # end depends on the order the agent worked in, and the derived total is
        # what carries the correctness.
        "accepted": [(C.ENG_PARAM[e1], a, b), (C.ENG_PARAM[e2], b, c)],
        "check": check, "expected_minutes": exp_min, "expected_metres": exp_m,
        "metre_tol": tol,
        "label_groups": [], "expected_label": "",
        "expected_rendered": expected,
        "margins": {"leg1": [r1["clock"], r1["distance"]],
                    "leg2": [r2["clock"], r2["distance"]]},
    })


def family_nearest(engine, origin, candidates, routes):
    readings = []
    for place in candidates:
        reading = rendered(engine, origin, place, routes)
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
        if reading["minutes"] < MIN_LEG_MINUTES:
            return None
        readings.append((place, reading))
    readings.sort(key=lambda pair: pair[1]["minutes"])
    if readings[1][1]["minutes"] - readings[0][1]["minutes"] < MARGIN_MINUTES:
        return None

    if not stable_under_moved_map([origin] + list(candidates)):
        return None
    tokens = {}
    for place, _ in readings:
        # The city is excluded as well as the competitors' names: a token
        # equal to the city ("Burlington Fire Department Station 1" ->
        # "Burlington") is one the agent could type while naming any of the
        # three places.
        others = [other["name"] for other, _ in readings
                  if other["query"] != place["query"]] + [place["city"]]
        token = token_of(place["name"], others)
        if token is None:
            return None
        tokens[place["query"]] = token

    winner, best = readings[0]
    groups = [[place["name"], [tokens[place["query"]]]] for place, _ in readings]
    # The reward reads the answer with _leading_label. Check here that the
    # answer this task expects actually resolves to the winner under that rule,
    # rather than trusting that distinct tokens imply an unambiguous answer.
    if leading_label(f"{winner['name']}: {best['clock']}", groups) != winner["name"]:
        return None
    # Each place string already ends in ", <City>", so a plain comma-separated
    # list reads as six places rather than three. Quote them.
    names = ", ".join(f'"{p["query"]}"' for p in candidates[:-1])
    slug = f"osm_nearest_{C.VERB[engine]}_{slugify(origin['name'])[:20]}_" \
           f"{slugify(winner['name'])[:20]}"
    instruction = (
        f"On the map site, work out which of {names} or "
        f"\"{candidates[-1]['query']}\" is the shortest {C.ENG_LABEL[engine]} "
        f"trip from \"{origin['query']}\". "
        + answer_spec("nearest_of_three")
    )
    return _base(slug, "nearest_of_three", "medium", instruction,
                 [origin] + list(candidates), {
        "legs": [{"from": origin["query"], "to": place["query"],
                  "engine_label": C.ENG_LABEL[engine], "label": place["name"]}
                 for place, _ in reversed(readings)],
        "combine": ('"%s: %s" % (min(readings, key=lambda r: r["minutes"])["label"], '
                    'min(readings, key=lambda r: r["minutes"])["clock"])'),
        "gate": "route",
        "accepted": [(C.ENG_PARAM[engine], origin, place)
                     for place, _ in readings],
        "check": "labelled_clock",
        "expected_minutes": best["minutes"], "expected_metres": -1.0,
        "metre_tol": 0.0,
        "label_groups": groups,
        "expected_label": winner["name"],
        "expected_rendered": f"{winner['name']}: {best['clock']}",
        "margins": {"minutes": [r["minutes"] for _, r in readings],
                    "tokens": tokens},
    })


# --------------------------------------------------------------------------
# bundle writing
# --------------------------------------------------------------------------

# The rollout reward is a SELF-CONTAINED program. cuagym/episode_code.py runs it
# by piping the source to `python -` in an empty temporary directory, so there is
# no sibling reward.py to import and `__file__` is not even defined. The pilot's
# version did `sys.path.insert(0, dirname(__file__)); import reward` and would
# have raised NameError on every rollout while verifying perfectly -- verification
# never runs this file. It is therefore built by taking reward.py's own source and
# appending the entry point below, so the two cannot score differently.
NEMO_HEADER = '''"""NeMo rollout reward for __TASK_ID__ (family __FAMILY__).

Identical rubric and identical code to the bundle's reward.py -- this file IS
that source with a rollout entry point appended, so verification and training
cannot drift apart.

The two inputs come from where cuagym/browser_worker.py puts them: the agent's
terminate(answer=...) as CUA_GYM_AGENT_ANSWER, and the episode's open tabs as
CUA_GYM_FINAL_URLS. Self-contained: standard library only, and it prints
REWARD: <float> on every path, including failure.
"""
'''

NEMO_TAIL = '''

# --- rollout entry point -------------------------------------------------
import json
import os


def _main():
    answer = (os.environ.get("CUA_GYM_AGENT_ANSWER") or "").strip()
    try:
        urls = json.loads(os.environ.get("CUA_GYM_FINAL_URLS") or "[]")
    except ValueError:
        urls = []
    if not isinstance(urls, list):
        urls = []
    evidence = {
        "agent_answer": answer,
        "apps": {"map": {"final_urls": urls, "final_text": "",
                         "current_state": {}, "initial_state": {},
                         "state_diff": {}}},
    }
    print("REWARD: %s" % evaluate(evidence)["score"])


try:
    _main()
except Exception as exc:  # noqa: BLE001 -- a crash must not read as a silent 0
    print("REWARD: 0.0")
    raise SystemExit("rollout reward failed: %s: %s" % (type(exc).__name__, exc))
'''


def nemo_source(reward_source: str, spec: dict) -> str:
    """reward.py's source, its docstring swapped, plus the rollout entry point."""
    opening = reward_source.index('"""')
    closing = reward_source.index('"""', opening + 3) + 3
    body = reward_source[closing:].lstrip("\n")
    header = (NEMO_HEADER.replace("__TASK_ID__", spec["slug"])
              .replace("__FAMILY__", spec["family"]))
    return header + body + NEMO_TAIL


APP_SPEC = {
    "name": "webarena_map_mock",
    "source_name": "map",
    "base_url_env": "CUA_GYM_WEBARENA_MAP_URL",
    "start_path": "/",
    "initial_state": None,
    "golden_state": None,
    # A real OpenStreetMap deployment, not a CUA-Gym mock: it has no /go?sid=
    # state API, so the runner must not build a StateClient for it.
    "stateless": True,
}


def place_meta(p: dict) -> dict:
    return {"query": p["query"], "name": p["name"], "city": p["city"],
            "resolved": p["display_name"], "nominatim_hits": p["nominatim_hits"],
            "latlon": [p["lat"], p["lon"]], "osm": p["osm"]}


def write_bundle(root: pathlib.Path, spec: dict) -> pathlib.Path:
    directory = root / spec["slug"]
    directory.mkdir(parents=True, exist_ok=True)

    # The reward matches the pair the site DISPLAYS in ?route=, which is rounded
    # to three decimals; routing itself used full precision.
    accepted = [
        (engine, (round(a["lat"], 3), round(a["lon"], 3)),
         (round(b["lat"], 3), round(b["lon"], 3)))
        for engine, a, b in spec["accepted"]
    ]
    reward = (REWARD_TMPL
              .replace("__TASK_ID__", spec["slug"])
              .replace("__FAMILY__", spec["family"])
              .replace("__GATE__", spec["gate"])
              .replace("__ACCEPTED_ROUTES__", repr(accepted))
              .replace("__SEARCH_NEEDLE__", spec.get("search_needle", ""))
              .replace("__CHECK__", spec["check"])
              .replace("__EXPECTED_MINUTES__", repr(spec["expected_minutes"]))
              .replace("__EXPECTED_METRES__", repr(float(spec["expected_metres"])))
              .replace("__METRE_TOL__", repr(float(spec["metre_tol"])))
              .replace("__LABEL_GROUPS__", repr(spec["label_groups"]))
              .replace("__EXPECTED_LABEL__", repr(spec["expected_label"]))
              .replace("__EXPECTED_RENDERED__", spec["expected_rendered"])
              .replace("__COMPONENT_WORK__",
                       "searched_for_the_place" if spec["gate"] == "search"
                       else "routed_the_intended_trip_on_the_map")
              .replace("__COMPONENT_ANSWER__", "reported_" + spec["family"]))
    (directory / "reward.py").write_text(reward, encoding="utf-8")
    (directory / "nemo_reward.py").write_text(nemo_source(reward, spec),
                                              encoding="utf-8")

    if spec["gate"] == "search":
        replay = (REPLAY_SEARCH_TMPL
                  .replace("__TASK_ID__", spec["slug"])
                  .replace("__FAMILY__", spec["family"])
                  .replace("__QUERY__", repr(spec["query"])))
    else:
        replay = (REPLAY_ROUTE_TMPL
                  .replace("__TASK_ID__", spec["slug"])
                  .replace("__FAMILY__", spec["family"])
                  .replace("__LEGS__", json.dumps(spec["legs"], indent=4))
                  .replace("__COMBINE__", spec["combine"]))
    (directory / "golden_replay.py").write_text(replay, encoding="utf-8")

    manifest = {
        "schema_version": 2,
        "task_id": spec["slug"],
        "instruction": spec["instruction"],
        "apps": [dict(APP_SPEC)],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "openstreetmap-batch-400",
        "metadata": {
            "site": "map",
            "family": spec["family"],
            "difficulty": spec["difficulty"],
            "shape": "answer_with_url_evidence",
            "expected_rendered": spec["expected_rendered"],
            "places": [place_meta(p) for p in spec["places"]],
            "margins": spec["margins"],
            "ground_truth_source":
                "nominatim :8085 with the site's viewbox, OSRM :5000/:5001/:5002 "
                "at full precision, formatted with the site's own formatTime and "
                "formatDistance",
        },
    }
    (directory / "task.json").write_text(json.dumps(manifest, indent=1) + "\n",
                                         encoding="utf-8")
    (directory / "task_instruction.json").write_text(json.dumps({
        "task_id": spec["slug"],
        "instruction": spec["instruction"],
        "difficulty": spec["difficulty"],
        "start_path": "/",
        "success_criteria": (
            f"The episode ends with the intended work visible on the map "
            f"({'the search for the named place' if spec['gate'] == 'search' else 'the intended route and routing engine'}) "
            f"and the reported answer is {spec['expected_rendered']!r}."
        ),
    }, indent=1) + "\n", encoding="utf-8")
    return directory


# --------------------------------------------------------------------------
# sampling
# --------------------------------------------------------------------------

QUOTA = [
    ("route_time", 65), ("route_distance", 45), ("place_postcode", 40),
    ("compare_modes", 60), ("time_gap", 50), ("two_leg_time", 45),
    ("two_leg_distance", 40), ("nearest_of_three", 55),
]
ENGINE_PAIRS = [("foot", "bike"), ("foot", "car"), ("bike", "car")]


def attempt(family, city_places, rng, routes):
    engine = rng.choice(["foot", "bike", "car"])
    if family == "route_time":
        a, b = rng.sample(city_places, 2)
        return family_route(engine, a, b, "time", routes)
    if family == "route_distance":
        a, b = rng.sample(city_places, 2)
        return family_route(engine, a, b, "distance", routes)
    if family == "place_postcode":
        candidates = [p for p in city_places if p["category"] in LANDMARKS
                      and p.get("postcode")]
        if not candidates:
            return None
        return family_postcode(rng.choice(candidates), routes)
    if family == "compare_modes":
        e1, e2 = rng.choice(ENGINE_PAIRS)
        a, b = rng.sample(city_places, 2)
        return family_compare(e1, e2, a, b, routes)
    if family == "time_gap":
        e1, e2 = rng.choice(ENGINE_PAIRS)
        a, b = rng.sample(city_places, 2)
        return family_gap(e1, e2, a, b, routes)
    if family in ("two_leg_time", "two_leg_distance"):
        e1, e2 = rng.choice(ENGINE_PAIRS)
        if rng.random() < 0.5:
            e1, e2 = e2, e1
        a, b, c = rng.sample(city_places, 3)
        return family_two_leg(e1, e2, a, b, c,
                              "time" if family.endswith("time") else "distance",
                              routes)
    if family == "nearest_of_three":
        origin, *candidates = rng.sample(city_places, 4)
        return family_nearest(engine, origin, candidates, routes)
    raise ValueError(family)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", default="output/osm_pool_clean.json")
    ap.add_argument("--out", default="output/map400/tasks/map")
    ap.add_argument("--seed", type=int, default=20260908)
    ap.add_argument("--attempts-per-task", type=int, default=40)
    args = ap.parse_args()

    pool = json.loads(pathlib.Path(args.pool).read_text())
    by_city: dict[str, list] = defaultdict(list)
    for entry in pool:
        by_city[entry["city"]].append(entry)
    cities = sorted(by_city)
    rng = random.Random(args.seed)
    routes = Routes()

    root = pathlib.Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    specs: list[dict] = []
    seen_slugs: set[str] = set()
    # An unordered place pair may anchor at most two tasks in the whole batch,
    # so the corpus does not quietly become a hundred variations on one street.
    pair_uses: Counter = Counter()
    subject_uses: Counter = Counter()
    tally: Counter = Counter()

    for family, quota in QUOTA:
        made = 0
        city_cycle = 0
        misses = 0
        while made < quota and misses < quota * args.attempts_per_task:
            city = cities[city_cycle % len(cities)]
            city_cycle += 1
            places = by_city[city]
            if len(places) < 4:
                continue
            spec = attempt(family, places, rng, routes)
            misses += 1
            if spec is None or spec["slug"] in seen_slugs:
                continue
            keys = [tuple(sorted((x["query"], y["query"])))
                    for x in spec["places"] for y in spec["places"]
                    if x["query"] < y["query"]]
            if any(pair_uses[k] >= 2 for k in keys):
                continue
            subject = spec["places"][0]["query"]
            if subject_uses[subject] >= 4:
                continue
            for k in keys:
                pair_uses[k] += 1
            subject_uses[subject] += 1
            spec["city"] = city
            seen_slugs.add(spec["slug"])
            specs.append(spec)
            tally[(family, city)] += 1
            made += 1
        print(f"{family:<18} {made:3}/{quota}   (osrm calls so far {routes.calls})",
              flush=True)
        if made < quota:
            print(f"  WARNING: {family} came up {quota - made} short", flush=True)

    for spec in specs:
        write_bundle(root, spec)

    index = [{"task_id": s["slug"], "family": s["family"], "city": s["city"],
              "difficulty": s["difficulty"], "expected": s["expected_rendered"],
              "instruction": s["instruction"]} for s in specs]
    (root.parent.parent / "index.json").write_text(
        json.dumps(index, indent=1) + "\n", encoding="utf-8")

    print(f"\n{len(specs)} bundles -> {root}")
    print("difficulty:", dict(Counter(s["difficulty"] for s in specs)))
    print("cities:", dict(Counter(s["city"] for s in specs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
