"""Reward for __TASK_ID__ -- OpenStreetMap, family __FAMILY__.

Deterministic and self-contained: no network, no LLM judge, no clock. Every
number below was computed at authoring time from the same Nominatim and OSRM
services the website itself calls (scripts/_osm_common.py) and then frozen, so
scoring never depends on those services being up or unchanged.

Two components, and the second is GATED on the first:

  proof of work (0.4)  the episode really used the map. For a routing task that
                       means a /directions URL whose engine parameter is exactly
                       the intended one and whose two endpoints are within TOL
                       of the intended places; for a search task it means the
                       /search URL carries the place that was asked for; for an
                       info-page task it means the episode ended on the OSM
                       object's own /node|/way|/relation page, which cannot be
                       reached without finding the right result and opening it.
  reported (0.6)       the reported answer parses to the value the site renders.
                       GATED, so an agent that guesses without ever opening the
                       route scores 0.0 rather than 0.6.

Coordinates are compared with a tolerance rather than for equality on purpose.
Several place names have more than one Nominatim hit, and any reasonable pick
has to pass while a route in the wrong part of the city must not. TOL is 0.005
degrees, roughly 500 m.
"""

import re
import urllib.parse

APP = "map"
GATE = "__GATE__"
# (engine parameter, (from_lat, from_lon), (to_lat, to_lon)) -- any one match is
# enough. Families that compare two engines list both; families with two legs
# list whichever leg the agent may reasonably have ended on.
ACCEPTED_ROUTES = __ACCEPTED_ROUTES__
TOL = 0.005
SEARCH_NEEDLE = "__SEARCH_NEEDLE__"
# Acceptable info-page paths, e.g. ["/node/2095832605"]. The id is the OSM
# object's own, so landing here is proof the right result was opened.
INFO_PATHS = __INFO_PATHS__

CHECK = "__CHECK__"
EXPECTED_MINUTES = __EXPECTED_MINUTES__
EXPECTED_METRES = __EXPECTED_METRES__
METRE_TOL = __METRE_TOL__
# Word groups that let the answer name WHICH thing won a comparison. The answer
# must mention the expected group before it mentions any competing group, which
# is what stops "cycling is slower than walking, 0:25" scoring as if it had
# picked cycling.
LABEL_GROUPS = __LABEL_GROUPS__
EXPECTED_LABEL = __EXPECTED_LABEL__
# Injected with repr(): an OSM tag value can itself contain quotes
# ("Open only during baseball games" is a real opening_hours value), and
# pasting it into a quoted literal produced un-parseable Python.
EXPECTED_RENDERED = __EXPECTED_RENDERED__
# Ordered families ("visit these three in the best order") need the labels in
# the required sequence plus the total that closes the answer.
ORDER_LABELS = __ORDER_LABELS__
EXPECTED_TOTAL = __EXPECTED_TOTAL__
EXPECTED_COORDS = __EXPECTED_COORDS__
COORD_TOL = __COORD_TOL__
# The literal value of an OSM tag as the info page prints it, and how to compare
# it: phone numbers by digits, websites ignoring scheme/www/trailing slash,
# everything else by collapsed-whitespace casefold.
EXPECTED_TAG = __EXPECTED_TAG__
TAG_KIND = "__TAG_KIND__"

COMPONENT_WORK = "__COMPONENT_WORK__"
COMPONENT_ANSWER = "__COMPONENT_ANSWER__"


def _urls(app):
    value = app.get("final_urls")
    if isinstance(value, str):
        return [value]
    return [u for u in (value or []) if isinstance(u, str)]


def _route_pairs(url):
    """The engine and the two (lat, lon) endpoints of a /directions URL."""
    parts = urllib.parse.urlsplit(url)
    if "directions" not in parts.path:
        return "", []
    query = urllib.parse.parse_qs(parts.query)
    engine = (query.get("engine") or [""])[0]
    pairs = []
    for chunk in (query.get("route") or [""])[0].split(";"):
        bits = chunk.split(",")
        if len(bits) != 2:
            continue
        try:
            pairs.append((float(bits[0]), float(bits[1])))
        except ValueError:
            return engine, []
    return engine, pairs


def _near(got, want):
    return abs(got[0] - want[0]) <= TOL and abs(got[1] - want[1]) <= TOL


def _searched(url):
    parts = urllib.parse.urlsplit(url)
    if not parts.path.rstrip("/").endswith("/search"):
        return False
    query = (urllib.parse.parse_qs(parts.query).get("query") or [""])[0]
    return SEARCH_NEEDLE in _flat(query)


def _flat(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _minutes(text):
    """Minutes stated by the agent, or None. Purely syntactic, no similarity."""
    clock = re.search(r"\b(\d+)\s*:\s*(\d{2})\b", text)
    if clock:
        return int(clock.group(1)) * 60 + int(clock.group(2))
    hm = re.search(r"\b(\d+)\s*h(?:ours?|rs?)?\b[^\d]{0,6}(\d+)\s*m", text, re.I)
    if hm:
        return int(hm.group(1)) * 60 + int(hm.group(2))
    only_h = re.search(r"\b(\d+)\s*(?:hours?|hrs?)\b", text, re.I)
    only_m = re.search(r"\b(\d+)\s*(?:minutes?|mins?|m)\b", text, re.I)
    if only_h and not only_m:
        return int(only_h.group(1)) * 60
    if only_m:
        return int(only_m.group(1))
    bare = re.search(r"\b(\d+)\b", text)
    return int(bare.group(1)) if bare else None


def _metres(text):
    km = re.search(r"\b(\d+(?:\.\d+)?)\s*k(?:m|ilomet(?:er|re)s?)\b", text, re.I)
    if km:
        return float(km.group(1)) * 1000.0
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:m|met(?:er|re)s?)\b", text, re.I)
    if m:
        return float(m.group(1))
    plain = re.search(r"\b(\d+(?:\.\d+)?)\b", text)
    return float(plain.group(1)) * 1000.0 if plain else None


def _norm_text(value):
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _norm_phone(value):
    return re.sub(r"\D", "", value)


def _norm_site(value):
    value = re.sub(r"^https?://", "", value.strip().casefold())
    return re.sub(r"^www\.", "", value).rstrip("/")


def _tag_matches(answer):
    """The expected tag value must APPEAR in the answer, not equal it.

    The agent is asked for one value but may reasonably echo the label with it
    ("opening hours: We-Su 10:00-17:00"), and rejecting that would fail a
    correct read of the page. Containment of the normalised expected value is
    strict enough: these strings are long and specific.
    """
    if TAG_KIND == "phone":
        expected, got = _norm_phone(EXPECTED_TAG), _norm_phone(answer)
    elif TAG_KIND == "website":
        expected, got = _norm_site(EXPECTED_TAG), _norm_site(answer)
    else:
        expected, got = _norm_text(EXPECTED_TAG), _norm_text(answer)
    return bool(expected) and expected in got


def _coords_match(answer):
    """Any adjacent pair of decimal numbers in the answer may be the coordinate."""
    numbers = [float(n) for n in re.findall(r"-?\d+\.\d+", answer)]
    for first, second in zip(numbers, numbers[1:]):
        if (abs(first - EXPECTED_COORDS[0]) <= COORD_TOL
                and abs(second - EXPECTED_COORDS[1]) <= COORD_TOL):
            return True
    return False


def _ordered_matches(answer):
    """Labels named in the required order, and the total closing the answer."""
    previous = -1
    for _, words in ORDER_LABELS:
        best = None
        for word in words:
            hit = re.search(r"\b" + re.escape(word) + r"\b", answer, re.I)
            if hit and (best is None or hit.start() < best):
                best = hit.start()
        if best is None or best <= previous:
            return False
        previous = best
    tail = re.search(r":\s*(\d+)\s*$", answer.strip())
    return bool(tail) and int(tail.group(1)) == EXPECTED_TOTAL


def _leading_label(text):
    """Which LABEL_GROUPS entry the answer names first, or ""."""
    best_at, best = None, ""
    for label, words in LABEL_GROUPS:
        for word in words:
            hit = re.search(r"\b" + re.escape(word) + r"\b", text, re.I)
            if hit and (best_at is None or hit.start() < best_at):
                best_at, best = hit.start(), label
    return best


def evaluate(evidence):
    apps = evidence.get("apps") or {}
    app = apps.get(APP) or apps.get("webarena_map_mock") or {}
    answer = (evidence.get("agent_answer") or "").strip()

    worked = False
    for url in _urls(app):
        if GATE == "info":
            if urllib.parse.urlsplit(url).path.rstrip("/") in INFO_PATHS:
                worked = True
                break
            continue
        if GATE == "search":
            if _searched(url):
                worked = True
                break
            continue
        engine, pairs = _route_pairs(url)
        if len(pairs) != 2:
            continue
        for want_engine, want_from, want_to in ACCEPTED_ROUTES:
            if (engine == want_engine and _near(pairs[0], tuple(want_from))
                    and _near(pairs[1], tuple(want_to))):
                worked = True
                break
        if worked:
            break

    answered = False
    if worked and answer:
        if CHECK == "postcode":
            answered = bool(re.search(r"\b" + re.escape(EXPECTED_RENDERED) + r"\b", answer))
        elif CHECK == "clock":
            answered = _minutes(answer) == EXPECTED_MINUTES
        elif CHECK == "labelled_clock":
            answered = (_leading_label(answer) == EXPECTED_LABEL
                        and _minutes(answer) == EXPECTED_MINUTES)
        elif CHECK == "minutes":
            answered = _minutes(answer) == EXPECTED_MINUTES
        elif CHECK == "tag":
            answered = _tag_matches(answer)
        elif CHECK == "coords":
            answered = _coords_match(answer)
        elif CHECK == "ordered":
            answered = _ordered_matches(answer)
        else:  # distance
            got = _metres(answer)
            answered = got is not None and abs(got - EXPECTED_METRES) <= METRE_TOL

    components = [
        {"name": COMPONENT_WORK, "score": 0.4 if worked else 0.0,
         "details": {"satisfied": worked}},
        {"name": COMPONENT_ANSWER, "score": 0.6 if answered else 0.0,
         "details": {"satisfied": answered, "expected": EXPECTED_RENDERED}},
    ]
    return {"score": round(sum(c["score"] for c in components), 6),
            "components": components}
