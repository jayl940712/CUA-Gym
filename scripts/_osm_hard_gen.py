#!/usr/bin/env python3
"""Generate the hard OpenStreetMap batch: 400 tasks across eight families.

The first map batch scored 88% because every family exercised ONE skill. Each
task named its endpoints as exact, resolvable strings, named the routing engine
as the literal dropdown label, and put the answer on the same Distance/Time line.
Its "medium" tier ran that identical loop two or three times, which is
repetition, not difficulty.

Every family here adds a lever the first batch has none of:

  nearest_of_five        the destination is NOT named -- a category and an
                         anchor are, so the agent must run the site's category
                         search and route each of the results it lists
  count_within_minutes   the same, plus a threshold: route them all, count the
                         ones inside the bound
  nearest_then_attribute the same, then open the winner's own object page
  poi_attribute          the answer is an OSM tag on the object page, reached by
                         searching and clicking through -- a surface the first
                         batch never touches
  poi_coordinates        the Location line on that page, in DD format
  optimal_order          three stops, six possible orders, report the best order
                         AND its total
  fastest_of_three_modes all three engines, not two
  reachable_within       a yes/no judgement against a bound, plus the time

Three levers apply across all of them: the mode is named colloquially ("by car",
never "Car (OSRM)"), ranking families never name the destination, and most
answers come from somewhere other than the Distance/Time line.

Ranking families use the FIRST FIVE results rather than all ten. Ten candidates
is fifty-odd actions before the agent starts reasoning, and tasks that fail on a
turn limit measure the limit, not the agent.

    python3 scripts/_osm_hard_gen.py --out output/maphard/tasks/map
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import re
import sys
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _osm_common as C  # noqa: E402

TMPL = HERE / "_osm"
REWARD_TMPL = (TMPL / "reward_tmpl2.py").read_text()
REPLAY_INFO = (TMPL / "replay_info_tmpl.py").read_text()
REPLAY_RANK = (TMPL / "replay_rank_tmpl.py").read_text()
REPLAY_ROUTE = (TMPL / "replay_route_tmpl.py").read_text()

MODE_NAME = {"foot": "walking", "bike": "cycling", "car": "driving"}
MODE_PHRASE = {"foot": "on foot", "bike": "by bicycle", "car": "by car"}
MODE_WORDS = {
    "walking": ["walk", "walks", "walking", "walked", "foot"],
    "cycling": ["cycle", "cycling", "bike", "bikes", "biking", "bicycle"],
    "driving": ["drive", "driving", "drove", "car"],
}
ALL_MODE_GROUPS = [[name, words] for name, words in MODE_WORDS.items()]
YES_NO_GROUPS = [["yes", ["yes"]], ["no", ["no"]]]

CATEGORIES = ["cafes", "restaurants", "pharmacies", "hotels", "supermarkets",
              "libraries", "museums", "parks", "banks", "hospitals",
              "post offices", "fire stations", "cinemas", "theatres", "schools"]
# Anchors have to be places a person would name in a search: proper nouns with a
# single Nominatim hit.
ANCHOR_CATEGORIES = {"university", "college", "museum", "library", "park",
                     "stadium", "hospital", "theatre", "hotel", "train station",
                     "zoo", "cinema"}
TAG_PHRASE = {
    "phone": "the phone number listed for it",
    "website": "the website listed for it",
    "opening_hours": "its opening hours, exactly as the page lists them",
    "operator": "the operator listed for it",
    "cuisine": "the cuisine listed for it",
}
TAG_KIND = {"phone": "phone", "website": "website"}

WINDOW = {"foot": (300, 6000), "bike": (500, 14000), "car": (700, 30000)}
MIN_LEG_MINUTES = 2
MARGIN_MINUTES = 3
RANK_MARGIN_MINUTES = 2
CANDIDATE_COUNT = 5

STOPWORDS = {"the", "and", "of", "for", "saint", "st", "north", "south", "east",
             "west", "new", "old", "center", "centre", "school", "park",
             "library", "museum", "hotel", "station", "hall", "house", "city",
             "county", "street", "avenue", "college", "university", "hospital",
             "theatre", "theater", "cinema", "stadium", "number", "building",
             "cafe", "coffee", "restaurant", "pharmacy", "bank", "inn"}


class Routes:
    """Memoised OSRM lookups, so a place pair is never routed twice."""

    def __init__(self) -> None:
        self._cache: dict[tuple, tuple] = {}
        self.calls = 0

    def get(self, engine, a, b):
        key = (engine, round(a[0], 7), round(a[1], 7), round(b[0], 7), round(b[1], 7))
        if key not in self._cache:
            self.calls += 1
            self._cache[key] = C.osrm(engine, a, b)
        return self._cache[key]


def rendered(engine, a, b, routes):
    duration, distance = routes.get(engine, a, b)
    return {"engine": engine, "seconds": duration, "metres_raw": distance,
            "clock": C.fmt_time(duration), "minutes": round(duration / 60),
            "distance": C.fmt_dist(distance)}


def search(query: str) -> list:
    """The site's own search, issued exactly as the site issues it."""
    return C.nominatim(query)


def extratags(query: str) -> dict:
    url = (f"http://{C.H}:8085/search?q={urllib.parse.quote(query)}&format=json"
           f"&extratags=1&viewbox={urllib.parse.quote(C.VIEWBOX)}")
    hits = C._get(url, timeout=25)
    return hits[0] if hits else {}


def ident(hit) -> tuple:
    return (hit.get("osm_type"), hit.get("osm_id"))


def info_path(hit) -> str:
    return f"/{hit['osm_type']}/{hit['osm_id']}"


def round_trips(display_name: str, want: tuple) -> bool:
    hits = search(display_name)
    return bool(hits) and ident(hits[0]) == want


def token_of(name: str, others: list[str]) -> str | None:
    words = [w for w in re.findall(r"[A-Za-z]{4,}", name)
             if w.lower() not in STOPWORDS]
    words.sort(key=len, reverse=True)
    for word in words:
        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.I)
        if not any(pattern.search(other) for other in others):
            return word
    return None


def tokens_for(names: list[str], extra_excluded: list[str]) -> dict | None:
    out = {}
    for name in names:
        others = [n for n in names if n != name] + extra_excluded
        token = token_of(name, others)
        if token is None:
            return None
        out[name] = token
    return out


def leading_label(text: str, groups: list) -> str:
    best_at, best = None, ""
    for label, words in groups:
        for word in words:
            hit = re.search(r"\b" + re.escape(word) + r"\b", text, re.I)
            if hit and (best_at is None or hit.start() < best_at):
                best_at, best = hit.start(), label
    return best


# Half-widths of the map view a fitted route can leave behind, in degrees.
VIEW_SPANS = (0.005, 0.01, 0.02, 0.05)


def stable_under_moved_map(places: list[dict]) -> bool:
    """True if no place re-geocodes elsewhere once an earlier route moved the map.

    Only families that retype a BARE place string need this. The ranking
    families type the full display name the results list shows, which pins the
    object far more tightly -- and indeed none of the 155 ranking tasks failed
    this audit while three of the 45 ordering tasks did.
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
# the answer contract, restated for the new families
# --------------------------------------------------------------------------
TERMINATE = ('When you have the answer, call the `terminate` tool with '
             '`status` set to `"success"` and put the answer in its `answer` '
             'field. ')

ANSWER_SPEC = {
    "nearest_of_five": (
        TERMINATE + 'The `answer` field must contain exactly `<place>: <time>`, '
        'where `<place>` is that place\'s name as the results list shows it, '
        'up to but not including the first comma, and `<time>` is its travel '
        'time in `H:MM` form -- for example `Temple of Zeus: 0:07`. Name only '
        'the closest place; do not mention any of the others.'),
    "count_within_minutes": (
        TERMINATE + 'The `answer` field must contain only the count, digits '
        'only -- for example `3`. Do not list the places, their travel times, '
        'or any explanation.'),
    "nearest_then_attribute": (
        TERMINATE + 'The `answer` field must contain only __TAGDESC__, copied '
        'exactly as the object page shows it. Do not include the place name, '
        'the travel time, or any explanation.'),
    "poi_attribute": (
        TERMINATE + 'The `answer` field must contain only __TAGDESC__, copied '
        'exactly as the object page shows it. Do not add a label, the place '
        'name, or any explanation.'),
    "poi_coordinates": (
        TERMINATE + 'The `answer` field must contain only the coordinates in DD '
        '(decimal degrees) form, latitude first, as `<lat>, <lon>` -- for '
        'example `40.4424191, -79.9397388`. Do not add N/S/E/W letters, degree '
        'symbols, the place name, or any explanation.'),
    "optimal_order": (
        TERMINATE + 'The `answer` field must contain exactly the three places '
        'in the order you would visit them, separated by ` > `, then a colon '
        'and the total travel time as a whole number of minutes -- for example '
        '`Hunt Library > Heinz Hall > PNC Park: 47`. Use each place\'s name as '
        'written in this task, without the city that follows the comma.'),
    "fastest_of_three_modes": (
        TERMINATE + 'The `answer` field must contain exactly `<mode>: <time>`, '
        'where `<mode>` is the single word `walking`, `cycling` or `driving` '
        'and `<time>` is that route\'s travel time in `H:MM` form -- for '
        'example `driving: 0:08`. Name only the fastest mode; do not mention '
        'the other two.'),
    "reachable_within": (
        TERMINATE + 'The `answer` field must contain exactly `<yes or no>: '
        '<time>`, where `<time>` is the actual travel time in `H:MM` form -- '
        'for example `yes: 0:12`. Nothing else.'),
}


def answer_spec(family: str, tag_description: str = "") -> str:
    return ANSWER_SPEC[family].replace("__TAGDESC__", tag_description)


def base(slug, family, tier, instruction, extra):
    return {"slug": slug, "family": family, "difficulty": "hard",
            "tier": tier, "instruction": instruction, **extra}


# --------------------------------------------------------------------------
# family builders
# --------------------------------------------------------------------------

def family_poi_coordinates(place, routes):
    """Search a place, open its object page, read the Location line."""
    # Only nodes carry a Location line; ways and relations render tags but no
    # single coordinate, so a task built on one would have no answer on screen.
    if place["osm"][0] != "node":
        return None
    hits = search(place["query"])
    if not hits or ident(hits[0]) != tuple(place["osm"]):
        return None
    lat, lon = float(hits[0]["lat"]), float(hits[0]["lon"])
    path = info_path(hits[0])
    instruction = (
        f"On the map site, search for {place['query']}, open its object page "
        f"from the results, and read off its position. "
        + answer_spec("poi_coordinates"))
    return base(f"osmh_coords_{slugify(place['name'])[:34]}", "poi_coordinates",
                1, instruction, {
        "replay": "info", "query": place["query"], "info_path": path,
        "read": "location", "tag_key": "",
        "gate": "info", "info_paths": [path], "accepted": [],
        "check": "coords", "expected_coords": (lat, lon), "coord_tol": 1e-4,
        "expected_rendered": f"{lat}, {lon}",
        "places": [place], "margins": {"osm": path},
    })


def family_poi_attribute(place, routes, rng):
    hits = search(place["query"])
    if not hits or ident(hits[0]) != tuple(place["osm"]):
        return None
    full = extratags(place["query"])
    tags = full.get("extratags") or {}
    usable = [k for k in TAG_PHRASE if tags.get(k) and len(str(tags[k])) >= 4]
    if not usable:
        return None
    key = rng.choice(usable)
    value = str(tags[key]).strip()
    path = info_path(hits[0])
    instruction = (
        f"On the map site, search for {place['query']}, open its object page "
        f"from the results, and find {TAG_PHRASE[key]}. "
        + answer_spec("poi_attribute", TAG_PHRASE[key]))
    return base(f"osmh_{key}_{slugify(place['name'])[:30]}", "poi_attribute",
                1, instruction, {
        "replay": "info", "query": place["query"], "info_path": path,
        "read": "tag", "tag_key": key,
        "gate": "info", "info_paths": [path], "accepted": [],
        "check": "tag", "expected_tag": value,
        "tag_kind": TAG_KIND.get(key, "text"),
        "expected_rendered": value,
        "places": [place], "margins": {"tag": key, "osm": path},
    })


def _candidates(anchor, category, engine, routes):
    """The first five search results, routed from the anchor."""
    hits = search(f"{category} near {anchor['query']}")[:CANDIDATE_COUNT]
    if len(hits) < CANDIDATE_COUNT:
        return None
    names = [h["display_name"].split(",")[0].strip() for h in hits]
    if len(set(names)) != CANDIDATE_COUNT:
        return None
    rows = []
    for hit, name in zip(hits, names):
        # The agent types what the list shows, so that string has to resolve
        # back to this same object -- bare names only manage it 60% of the time.
        if not round_trips(hit["display_name"], ident(hit)):
            return None
        reading = rendered(engine, (anchor["lat"], anchor["lon"]),
                           (float(hit["lat"]), float(hit["lon"])), routes)
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
        if reading["minutes"] < MIN_LEG_MINUTES:
            return None
        rows.append({"name": name, "display_name": hit["display_name"],
                     "hit": hit, "reading": reading})
    return rows


def family_nearest_of_five(anchor, category, engine, routes):
    rows = _candidates(anchor, category, engine, routes)
    if rows is None:
        return None
    order = sorted(rows, key=lambda r: r["reading"]["minutes"])
    if order[1]["reading"]["minutes"] - order[0]["reading"]["minutes"] < RANK_MARGIN_MINUTES:
        return None
    names = [r["name"] for r in rows]
    tokens = tokens_for(names, [anchor["name"], anchor["city"]])
    if tokens is None:
        return None
    groups = [[r["name"], [tokens[r["name"]]]] for r in rows]
    winner = order[0]
    expected = f"{winner['name']}: {winner['reading']['clock']}"
    if leading_label(expected, groups) != winner["name"]:
        return None
    instruction = (
        f"On the map site, search for \"{category} near {anchor['query']}\". "
        f"Of the first five places the results list, work out which is the "
        f"shortest trip {MODE_PHRASE[engine]} from {anchor['query']}. "
        + answer_spec("nearest_of_five"))
    return base(
        f"osmh_nearest_{slugify(category)[:12]}_{slugify(anchor['name'])[:24]}",
        "nearest_of_five", 3, instruction, {
        "replay": "rank", "search_query": f"{category} near {anchor['query']}",
        "anchor": anchor["query"], "engine_label": C.ENG_LABEL[engine],
        "candidates": [{"name": r["name"], "route_to": r["display_name"]}
                       for r in rows],
        "combine": ('"%s: %s" % (min(readings, key=lambda r: r["minutes"])["label"], '
                    'min(readings, key=lambda r: r["minutes"])["clock"])'),
        "then_info": None,
        "gate": "route", "info_paths": [],
        "accepted": [(C.ENG_PARAM[engine], anchor,
                      {"lat": float(r["hit"]["lat"]), "lon": float(r["hit"]["lon"])})
                     for r in rows],
        "check": "labelled_clock", "expected_minutes": winner["reading"]["minutes"],
        "label_groups": groups, "expected_label": winner["name"],
        "expected_rendered": expected,
        "places": [anchor], "margins": {
            "minutes": {r["name"]: r["reading"]["minutes"] for r in rows},
            "gap_to_second": order[1]["reading"]["minutes"] - order[0]["reading"]["minutes"]},
    })


def family_count_within(anchor, category, engine, routes, rng):
    rows = _candidates(anchor, category, engine, routes)
    if rows is None:
        return None
    minutes = sorted(r["reading"]["minutes"] for r in rows)
    # A threshold that splits the five, and sits clear of every candidate so a
    # one-minute rendering difference cannot change the count.
    options = [t for t in range(min(minutes), max(minutes) + 1)
               if all(abs(t - m) >= 2 for m in minutes)
               and 1 <= sum(1 for m in minutes if m <= t) <= 4]
    if not options:
        return None
    threshold = rng.choice(options)
    count = sum(1 for m in minutes if m <= threshold)
    instruction = (
        f"On the map site, search for \"{category} near {anchor['query']}\". "
        f"Of the first five places the results list, how many can be reached "
        f"from {anchor['query']} in {threshold} minutes or less "
        f"{MODE_PHRASE[engine]}? "
        + answer_spec("count_within_minutes"))
    return base(
        f"osmh_count_{slugify(category)[:12]}_{slugify(anchor['name'])[:22]}",
        "count_within_minutes", 3, instruction, {
        "replay": "rank", "search_query": f"{category} near {anchor['query']}",
        "anchor": anchor["query"], "engine_label": C.ENG_LABEL[engine],
        "candidates": [{"name": r["name"], "route_to": r["display_name"]}
                       for r in rows],
        "combine": f'str(sum(1 for r in readings if r["minutes"] <= {threshold}))',
        "then_info": None,
        "gate": "route", "info_paths": [],
        "accepted": [(C.ENG_PARAM[engine], anchor,
                      {"lat": float(r["hit"]["lat"]), "lon": float(r["hit"]["lon"])})
                     for r in rows],
        "check": "minutes", "expected_minutes": count,
        "expected_rendered": str(count),
        "places": [anchor],
        "margins": {"threshold": threshold, "minutes": minutes, "count": count},
    })


def family_nearest_then_attribute(anchor, category, engine, routes, rng):
    rows = _candidates(anchor, category, engine, routes)
    if rows is None:
        return None
    order = sorted(rows, key=lambda r: r["reading"]["minutes"])
    if order[1]["reading"]["minutes"] - order[0]["reading"]["minutes"] < RANK_MARGIN_MINUTES:
        return None
    winner = order[0]
    tags = (winner["hit"].get("extratags") or {})
    if not tags:
        tags = (extratags(winner["display_name"]).get("extratags") or {})
    usable = [k for k in TAG_PHRASE if tags.get(k) and len(str(tags[k])) >= 4]
    if not usable:
        return None
    key = rng.choice(usable)
    value = str(tags[key]).strip()
    path = info_path(winner["hit"])
    instruction = (
        f"On the map site, search for \"{category} near {anchor['query']}\". "
        f"Of the first five places the results list, find the one that is the "
        f"shortest trip {MODE_PHRASE[engine]} from {anchor['query']}, then open "
        f"that place's object page and find {TAG_PHRASE[key]}. "
        + answer_spec("nearest_then_attribute", TAG_PHRASE[key]))
    return base(
        f"osmh_rankattr_{key}_{slugify(anchor['name'])[:22]}",
        "nearest_then_attribute", 3, instruction, {
        "replay": "rank", "search_query": f"{category} near {anchor['query']}",
        "anchor": anchor["query"], "engine_label": C.ENG_LABEL[engine],
        "candidates": [{"name": r["name"], "route_to": r["display_name"]}
                       for r in rows],
        "combine": '""',
        "then_info": {"query": winner["display_name"], "path": path, "tag": key},
        "gate": "info", "info_paths": [path], "accepted": [],
        "check": "tag", "expected_tag": value,
        "tag_kind": TAG_KIND.get(key, "text"),
        "expected_rendered": value,
        "places": [anchor], "margins": {
            "winner": winner["name"], "tag": key,
            "minutes": {r["name"]: r["reading"]["minutes"] for r in rows}},
    })


def family_optimal_order(start, stops, engine, routes):
    """Three stops from a start: which visiting order is quickest?"""
    import itertools
    points = {p["query"]: (p["lat"], p["lon"]) for p in [start] + list(stops)}
    totals = {}
    for order in itertools.permutations(stops):
        legs = []
        previous = start
        for stop in order:
            legs.append(rendered(engine, points[previous["query"]],
                                 points[stop["query"]], routes))
            previous = stop
        low, high = WINDOW[engine]
        if any(not low <= leg["metres_raw"] <= high for leg in legs):
            return None
        if any(leg["minutes"] < MIN_LEG_MINUTES for leg in legs):
            return None
        by_display = sum(leg["minutes"] for leg in legs)
        by_raw = round(sum(leg["seconds"] for leg in legs) / 60)
        # Two defensible totals means two defensible answers.
        if by_display != by_raw:
            return None
        totals[tuple(s["query"] for s in order)] = by_display
    ranked = sorted(totals.items(), key=lambda kv: kv[1])
    if ranked[1][1] - ranked[0][1] < MARGIN_MINUTES:
        return None

    if not stable_under_moved_map([start] + list(stops)):
        return None
    best_order = [next(s for s in stops if s["query"] == q) for q in ranked[0][0]]
    names = [s["name"] for s in stops]
    tokens = tokens_for(names, [start["name"], start["city"]])
    if tokens is None:
        return None
    order_labels = [[s["name"], [tokens[s["name"]]]] for s in best_order]
    expected = " > ".join(s["name"] for s in best_order) + f": {ranked[0][1]}"
    listed = ", ".join(f'"{s["query"]}"' for s in stops[:-1])
    instruction = (
        f"On the map site, you are starting at \"{start['query']}\" and need to "
        f"visit {listed} and \"{stops[-1]['query']}\", travelling "
        f"{MODE_PHRASE[engine]}. Work out the order of visits that makes the "
        f"total travel time shortest. " + answer_spec("optimal_order"))
    return base(
        f"osmh_order_{slugify(start['name'])[:20]}_{slugify(best_order[0]['name'])[:18]}",
        "optimal_order", 3, instruction, {
        "replay": "route",
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[engine], "label": b["name"]}
                 for a, b in zip([start] + best_order[:-1], best_order)],
        "combine": ('" > ".join(r["label"] for r in readings) + ": " '
                    '+ str(sum(r["minutes"] for r in readings))'),
        "gate": "route", "info_paths": [],
        "accepted": [(C.ENG_PARAM[engine], a, b)
                     for a in [start] + list(stops) for b in [start] + list(stops)
                     if a["query"] != b["query"]],
        "check": "ordered", "order_labels": order_labels,
        "expected_total": ranked[0][1],
        "expected_rendered": expected,
        "places": [start] + list(stops),
        "margins": {"totals": {" > ".join(k): v for k, v in ranked},
                    "gap_to_second": ranked[1][1] - ranked[0][1]},
    })


def family_fastest_of_three(a, b, routes):
    readings = {engine: rendered(engine, (a["lat"], a["lon"]), (b["lat"], b["lon"]),
                                 routes) for engine in ("foot", "bike", "car")}
    for engine, reading in readings.items():
        low, high = WINDOW[engine]
        if not low <= reading["metres_raw"] <= high:
            return None
        if reading["minutes"] < MIN_LEG_MINUTES:
            return None
    order = sorted(readings.values(), key=lambda r: r["minutes"])
    if order[1]["minutes"] - order[0]["minutes"] < MARGIN_MINUTES:
        return None
    winner = MODE_NAME[order[0]["engine"]]
    expected = f"{winner}: {order[0]['clock']}"
    if leading_label(expected, ALL_MODE_GROUPS) != winner:
        return None
    instruction = (
        f"On the map site, work out whether walking, cycling or driving is the "
        f"fastest way to get from {a['query']} to {b['query']}. "
        + answer_spec("fastest_of_three_modes"))
    return base(
        f"osmh_fastest_{slugify(a['name'])[:22]}_{slugify(b['name'])[:22]}",
        "fastest_of_three_modes", 2, instruction, {
        "replay": "route",
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[r["engine"]],
                  "label": MODE_NAME[r["engine"]]} for r in reversed(order)],
        "combine": ('"%s: %s" % (min(readings, key=lambda r: r["minutes"])["label"], '
                    'min(readings, key=lambda r: r["minutes"])["clock"])'),
        "gate": "route", "info_paths": [],
        "accepted": [(C.ENG_PARAM[e], a, b) for e in ("foot", "bike", "car")],
        "check": "labelled_clock", "expected_minutes": order[0]["minutes"],
        "label_groups": ALL_MODE_GROUPS, "expected_label": winner,
        "expected_rendered": expected,
        "places": [a, b],
        "margins": {m: readings[e]["minutes"] for e, m in MODE_NAME.items()},
    })


def family_reachable_within(a, b, engine, routes, rng):
    reading = rendered(engine, (a["lat"], a["lon"]), (b["lat"], b["lon"]), routes)
    low, high = WINDOW[engine]
    if not low <= reading["metres_raw"] <= high:
        return None
    if reading["minutes"] < MIN_LEG_MINUTES:
        return None
    # The bound sits close enough to the real time that the question cannot be
    # answered by intuition, but far enough that a minute of rendering slack
    # cannot flip it.
    offsets = [d for d in range(MARGIN_MINUTES, 9)]
    offset = rng.choice(offsets) * rng.choice((-1, 1))
    threshold = reading["minutes"] + offset
    if threshold < 2:
        return None
    verdict = "yes" if reading["minutes"] <= threshold else "no"
    expected = f"{verdict}: {reading['clock']}"
    instruction = (
        f"On the map site, decide whether you can get from {a['query']} to "
        f"{b['query']} {MODE_PHRASE[engine]} in {threshold} minutes or less, "
        f"and note how long the trip actually takes. "
        + answer_spec("reachable_within"))
    return base(
        f"osmh_within_{threshold}_{slugify(a['name'])[:20]}_{slugify(b['name'])[:20]}",
        "reachable_within", 2, instruction, {
        "replay": "route",
        "legs": [{"from": a["query"], "to": b["query"],
                  "engine_label": C.ENG_LABEL[engine], "label": MODE_NAME[engine]}],
        "combine": (f'("yes" if readings[0]["minutes"] <= {threshold} else "no")'
                    ' + ": " + readings[0]["clock"]'),
        "gate": "route", "info_paths": [],
        "accepted": [(C.ENG_PARAM[engine], a, b)],
        "check": "labelled_clock", "expected_minutes": reading["minutes"],
        "label_groups": YES_NO_GROUPS, "expected_label": verdict,
        "expected_rendered": expected,
        "places": [a, b],
        "margins": {"threshold": threshold, "actual_minutes": reading["minutes"],
                    "slack": abs(offset)},
    })


# --------------------------------------------------------------------------
# bundle writing
# --------------------------------------------------------------------------

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

APP_SPEC = {
    "name": "webarena_map_mock", "source_name": "map",
    "base_url_env": "CUA_GYM_WEBARENA_MAP_URL", "start_path": "/",
    "initial_state": None, "golden_state": None, "stateless": True,
}


def nemo_source(reward_source: str, spec: dict) -> str:
    opening = reward_source.index('"""')
    closing = reward_source.index('"""', opening + 3) + 3
    header = (NEMO_HEADER.replace("__TASK_ID__", spec["slug"])
              .replace("__FAMILY__", spec["family"]))
    return header + reward_source[closing:].lstrip("\n") + NEMO_TAIL


def place_meta(p: dict) -> dict:
    return {"query": p["query"], "name": p["name"], "city": p.get("city", ""),
            "resolved": p.get("display_name", ""),
            "nominatim_hits": p.get("nominatim_hits"),
            "latlon": [p["lat"], p["lon"]], "osm": p.get("osm")}


def write_bundle(root: pathlib.Path, spec: dict) -> pathlib.Path:
    directory = root / spec["slug"]
    directory.mkdir(parents=True, exist_ok=True)

    accepted = [(engine, (round(a["lat"], 3), round(a["lon"], 3)),
                 (round(b["lat"], 3), round(b["lon"], 3)))
                for engine, a, b in spec.get("accepted", [])]
    reward = (REWARD_TMPL
              .replace("__TASK_ID__", spec["slug"])
              .replace("__FAMILY__", spec["family"])
              .replace("__GATE__", spec["gate"])
              .replace("__ACCEPTED_ROUTES__", repr(accepted))
              .replace("__INFO_PATHS__", repr(spec.get("info_paths", [])))
              .replace("__SEARCH_NEEDLE__", spec.get("search_needle", ""))
              .replace("__CHECK__", spec["check"])
              .replace("__EXPECTED_MINUTES__", repr(spec.get("expected_minutes", -1)))
              .replace("__EXPECTED_METRES__", repr(float(spec.get("expected_metres", -1.0))))
              .replace("__METRE_TOL__", repr(float(spec.get("metre_tol", 0.0))))
              .replace("__LABEL_GROUPS__", repr(spec.get("label_groups", [])))
              .replace("__EXPECTED_LABEL__", repr(spec.get("expected_label", "")))
              .replace("__ORDER_LABELS__", repr(spec.get("order_labels", [])))
              .replace("__EXPECTED_TOTAL__", repr(spec.get("expected_total", -1)))
              .replace("__EXPECTED_COORDS__", repr(spec.get("expected_coords", (0.0, 0.0))))
              .replace("__COORD_TOL__", repr(spec.get("coord_tol", 0.0001)))
              .replace("__EXPECTED_TAG__", repr(spec.get("expected_tag", "")))
              .replace("__TAG_KIND__", spec.get("tag_kind", "text"))
              .replace("__EXPECTED_RENDERED__", repr(spec["expected_rendered"]))
              .replace("__COMPONENT_WORK__",
                       {"info": "opened_the_objects_own_page",
                        "search": "searched_for_the_place",
                        "route": "routed_the_intended_trip_on_the_map"}[spec["gate"]])
              .replace("__COMPONENT_ANSWER__", "reported_" + spec["family"]))
    (directory / "reward.py").write_text(reward, encoding="utf-8")
    (directory / "nemo_reward.py").write_text(nemo_source(reward, spec),
                                              encoding="utf-8")

    if spec["replay"] == "info":
        replay = (REPLAY_INFO
                  .replace("__QUERY__", repr(spec["query"]))
                  .replace("__INFO_PATH__", repr(spec["info_path"]))
                  .replace("__READ__", repr(spec["read"]))
                  .replace("__TAG_KEY__", repr(spec["tag_key"])))
    elif spec["replay"] == "rank":
        replay = (REPLAY_RANK
                  .replace("__SEARCH_QUERY__", repr(spec["search_query"]))
                  .replace("__ANCHOR__", repr(spec["anchor"]))
                  .replace("__CANDIDATES__", json.dumps(spec["candidates"], indent=4))
                  .replace("__ENGINE_LABEL__", repr(spec["engine_label"]))
                  .replace("__THEN_INFO__", repr(spec["then_info"]))
                  .replace("__COMBINE__", spec["combine"]))
    else:
        replay = (REPLAY_ROUTE
                  .replace("__LEGS__", json.dumps(spec["legs"], indent=4))
                  .replace("__COMBINE__", spec["combine"]))
    replay = replay.replace("__TASK_ID__", spec["slug"]).replace("__FAMILY__",
                                                                 spec["family"])
    (directory / "golden_replay.py").write_text(replay, encoding="utf-8")

    manifest = {
        "schema_version": 2, "task_id": spec["slug"],
        "instruction": spec["instruction"], "apps": [dict(APP_SPEC)],
        "reward_path": "reward.py", "requirements_path": None,
        "evidence": [], "source_evaluator": {},
        "source": "openstreetmap-batch-hard-400",
        "metadata": {
            "site": "map", "family": spec["family"],
            "difficulty": "hard", "difficulty_tier": spec["tier"],
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
        "task_id": spec["slug"], "instruction": spec["instruction"],
        "difficulty": "hard", "start_path": "/",
        "success_criteria": (
            f"The episode ends with the intended work visible on the map and "
            f"the reported answer is {spec['expected_rendered']!r}."),
    }, indent=1) + "\n", encoding="utf-8")
    return directory


# --------------------------------------------------------------------------
# sampling
# --------------------------------------------------------------------------

QUOTA = [
    ("poi_attribute", 65), ("nearest_of_five", 60), ("count_within_minutes", 50),
    ("poi_coordinates", 45), ("nearest_then_attribute", 45),
    ("optimal_order", 45), ("fastest_of_three_modes", 45),
    ("reachable_within", 45),
]


def attempt(family, places, anchors, rng, routes):
    engine = rng.choice(["foot", "bike", "car"])
    if family == "poi_coordinates":
        return family_poi_coordinates(rng.choice(places), routes)
    if family == "poi_attribute":
        return family_poi_attribute(rng.choice(places), routes, rng)
    if family == "nearest_of_five":
        if not anchors:
            return None
        return family_nearest_of_five(rng.choice(anchors),
                                      rng.choice(CATEGORIES), engine, routes)
    if family == "count_within_minutes":
        if not anchors:
            return None
        return family_count_within(rng.choice(anchors), rng.choice(CATEGORIES),
                                   engine, routes, rng)
    if family == "nearest_then_attribute":
        if not anchors:
            return None
        return family_nearest_then_attribute(rng.choice(anchors),
                                             rng.choice(CATEGORIES), engine,
                                             routes, rng)
    if family == "optimal_order":
        start, *stops = rng.sample(places, 4)
        return family_optimal_order(start, stops, engine, routes)
    if family == "fastest_of_three_modes":
        a, b = rng.sample(places, 2)
        return family_fastest_of_three(a, b, routes)
    if family == "reachable_within":
        a, b = rng.sample(places, 2)
        return family_reachable_within(a, b, engine, routes, rng)
    raise ValueError(family)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", default="output/osm_pool_clean.json")
    ap.add_argument("--out", default="output/maphard/tasks/map")
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--attempts-per-task", type=int, default=60)
    ap.add_argument("--only", default="", help="build a single family")
    ap.add_argument("--limit", type=int, default=0, help="cap each quota")
    args = ap.parse_args()

    pool = json.loads(pathlib.Path(args.pool).read_text())
    by_city: dict[str, list] = collections.defaultdict(list)
    for entry in pool:
        by_city[entry["city"]].append(entry)
    cities = sorted(by_city)
    rng = random.Random(args.seed)
    routes = Routes()
    root = pathlib.Path(args.out)
    root.mkdir(parents=True, exist_ok=True)

    specs, seen = [], set()
    subject_uses: collections.Counter = collections.Counter()
    quota = [(f, args.limit or n) for f, n in QUOTA
             if not args.only or f == args.only]

    for family, want in quota:
        made = misses = cycle = 0
        while made < want and misses < want * args.attempts_per_task:
            city = cities[cycle % len(cities)]
            cycle += 1
            misses += 1
            places = by_city[city]
            if len(places) < 5:
                continue
            anchors = [p for p in places
                       if p["category"] in ANCHOR_CATEGORIES
                       and p["nominatim_hits"] == 1]
            try:
                spec = attempt(family, places, anchors, rng, routes)
            except RuntimeError:
                continue
            if spec is None or spec["slug"] in seen:
                continue
            subject = spec["places"][0]["query"]
            if subject_uses[subject] >= 3:
                continue
            subject_uses[subject] += 1
            spec["city"] = city
            seen.add(spec["slug"])
            specs.append(spec)
            made += 1
        print(f"{family:<24} {made:3}/{want}   (osrm calls {routes.calls})",
              flush=True)
        if made < want:
            print(f"  WARNING: {family} came up {want - made} short", flush=True)

    for spec in specs:
        write_bundle(root, spec)
    index = [{"task_id": s["slug"], "family": s["family"], "city": s["city"],
              "tier": s["tier"], "expected": s["expected_rendered"],
              "instruction": s["instruction"]} for s in specs]
    # The batch layout is <batch>/tasks/map; when --out points somewhere else
    # (a pilot directory, say) the index belongs beside the bundles instead of
    # two levels up, which may not even be writable.
    index_dir = (root.parent.parent if root.parts[-2:] == ("tasks", "map")
                 else root)
    (index_dir / "index.json").write_text(
        json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"\n{len(specs)} bundles -> {root}")
    print("families:", dict(collections.Counter(s["family"] for s in specs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
