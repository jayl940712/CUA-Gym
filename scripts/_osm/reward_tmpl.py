"""Reward for __TASK_ID__ -- OpenStreetMap, family __FAMILY__.

Deterministic and self-contained: no network, no LLM judge, no clock. Every
number below was computed at authoring time from the same Nominatim and OSRM
services the website itself calls (scripts/_osm_common.py) and then frozen, so
scoring never depends on those services being up or unchanged.

Two components, and the second is GATED on the first:

  proof of work (0.4)  the episode really used the map. For a routing task that
                       means a /directions URL whose engine parameter is exactly
                       the intended one and whose two endpoints are within TOL
                       of the intended places; for a lookup task it means the
                       /search URL carries the place that was asked for.
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
EXPECTED_RENDERED = "__EXPECTED_RENDERED__"

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
