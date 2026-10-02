#!/usr/bin/env python3
"""Build the OpenStreetMap pilot bundles.

Ground truth is computed here, at authoring time, from the same Nominatim and
OSRM services the website itself calls, then frozen into each reward as a
literal. The rewards make no network calls and contain no LLM judging.

Reproducing what the UI renders takes three steps, and skipping any of them
produces a wrong answer:

  1. Nominatim top hit, requested WITH the same ``viewbox`` the site sends. The
     viewbox biases results toward the current map view and can change which hit
     comes first, so omitting it can geocode to a different place entirely.
  2. Keep FULL precision. The 3-decimal pair in the ``?route=`` URL parameter is
     display only -- a network capture shows the site calling OSRM with
     ``-71.0966272383055,42.3582529;...``. Rounding first produced 0:18 and
     1.8km where the site renders 0:17 and 1.7km.
  3. OSRM with the site's own query string
     (``overview=false&geometries=polyline&steps=true``), then its formatters,
     transcribed from its JS bundle:
        formatTime(s):     m=round(s/60); h=m//60; m-=h*60 -> "h:mm"
        formatDistance(m): <1000 -> "{round(m)}m"
                           <10000 -> "{m/1000:.1f}km"
                           else -> "{round(m/1000)}km"
"""
from __future__ import annotations
import json, pathlib, urllib.request, urllib.parse

H = "18.116.12.228"
# The viewbox the site sends from a cold "/" load (#map=7/42.896/-75.108). Every
# task starts at "/", so this is deterministic.
VIEWBOX = ("-82.79296875000001,39.402244340292775,"
           "-67.41210937500001,46.20264638061019")
ENG_PORT  = {"car": 5000, "bike": 5001, "foot": 5002}
ENG_PARAM = {"car": "fossgis_osrm_car", "bike": "fossgis_osrm_bike", "foot": "fossgis_osrm_foot"}
ENG_LABEL = {"car": "Car (OSRM)", "bike": "Bicycle (OSRM)", "foot": "Foot (OSRM)"}
VERB      = {"car": "drive", "bike": "cycle", "foot": "walk"}

def nom(q):
    u = (f"http://{H}:8085/search?q={urllib.parse.quote(q)}&format=json"
         f"&viewbox={urllib.parse.quote(VIEWBOX)}")
    return json.load(urllib.request.urlopen(u, timeout=25))

def coord(q):
    r = nom(q)
    if not r:
        raise SystemExit(f"Nominatim returned nothing for {q!r} -- do not build a task on it")
    return (float(r[0]["lat"]), float(r[0]["lon"]), r[0]["display_name"], len(r))

def osrm(engine, a, b):
    u = (f"http://{H}:{ENG_PORT[engine]}/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}"
         f"?overview=false&geometries=polyline&steps=true")
    d = json.load(urllib.request.urlopen(u, timeout=30))["routes"][0]
    return d["duration"], d["distance"]

def fmt_time(s):
    m = round(s / 60); h = m // 60; m -= h * 60
    return f"{h}:{m:02d}"

def fmt_dist(m):
    if m < 1000:  return f"{round(m)}m"
    if m < 10000: return f"{m/1000.0:.1f}km"
    return f"{round(m/1000)}km"

SPECS = [
    ("osm_route_time_walk_cmu_to_pitt",        "foot", "Carnegie Mellon University",            "University of Pittsburgh", "time"),
    ("osm_route_time_drive_cmu_to_chatham",    "car",  "Carnegie Mellon University",            "Chatham University",       "time"),
    ("osm_route_time_bike_mit_to_harvard",     "bike", "Massachusetts Institute of Technology", "Harvard University",       "time"),
    ("osm_route_distance_walk_cmu_to_chatham", "foot", "Carnegie Mellon University",            "Chatham University",       "distance"),
]

REWARD_TMPL = r'''"""Reward for __TASK_ID__ -- OpenStreetMap route lookup.

Deterministic and self-contained: no network, no LLM, no clock. Ground truth was
computed at authoring time from the same Nominatim/OSRM services the site calls
(see scripts/_osm_pilot_gen.py) and is frozen below.

Two components, and the second is GATED on the first:

  routed_*  (0.4)  the final URL is a /directions page whose engine parameter is
                   exactly __ENGINE_PARAM__ and whose two route endpoints are
                   within __TOL__ degrees of the intended places. This is the
                   proof-of-work: an agent that guesses the answer without
                   routing cannot satisfy it.
  reported_*(0.6)  the reported answer parses to the value the site renders.
                   Gated on routed_*, so guessing scores 0.0 rather than 0.6.

The endpoint check uses a tolerance rather than string equality on purpose:
several of these place names have more than one Nominatim hit (Carnegie Mellon
has three), and any reasonable pick should pass while a route from the wrong
city must not.
"""

import re
import urllib.parse

ENGINE_PARAM = "__ENGINE_PARAM__"
FROM_LL = (__FROM_LAT__, __FROM_LON__)
TO_LL = (__TO_LAT__, __TO_LON__)
TOL = __TOL__
ASK = "__ASK__"
EXPECTED_RENDERED = "__ANSWER__"
EXPECTED_MINUTES = __EXP_MIN__
EXPECTED_METRES = __EXP_M__
APP = "map"

COMPONENT_ROUTED = "routed_with___ENGINE___between_the_named_places"
COMPONENT_ANSWER = "reported_the___ASK___the_site_renders"


def _urls(app):
    value = app.get("final_urls")
    if isinstance(value, str):
        return [value]
    return [u for u in (value or []) if isinstance(u, str)]


def _route_pairs(url):
    """The two (lat, lon) endpoints in a /directions URL, or []."""
    parts = urllib.parse.urlsplit(url)
    if "directions" not in parts.path:
        return [], ""
    query = urllib.parse.parse_qs(parts.query)
    engine = (query.get("engine") or [""])[0]
    raw = (query.get("route") or [""])[0]
    pairs = []
    for chunk in raw.split(";"):
        bits = chunk.split(",")
        if len(bits) != 2:
            continue
        try:
            pairs.append((float(bits[0]), float(bits[1])))
        except ValueError:
            return [], engine
    return pairs, engine


def _near(got, want, tol):
    return abs(got[0] - want[0]) <= tol and abs(got[1] - want[1]) <= tol


def _minutes(text):
    """Minutes stated by the agent, or None. Deterministic, no fuzzy matching."""
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
    bare = re.fullmatch(r"\s*(\d+)\s*", text)
    return int(bare.group(1)) if bare else None


def _metres(text):
    km = re.search(r"\b(\d+(?:\.\d+)?)\s*k(?:m|ilomet(?:er|re)s?)\b", text, re.I)
    if km:
        return float(km.group(1)) * 1000.0
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:m|met(?:er|re)s?)\b", text, re.I)
    if m:
        return float(m.group(1))
    return None


def evaluate(evidence):
    apps = evidence.get("apps") or {}
    app = apps.get(APP) or apps.get("webarena_map_mock") or {}
    answer = (evidence.get("agent_answer") or "").strip()

    routed = False
    for url in _urls(app):
        pairs, engine = _route_pairs(url)
        if engine != ENGINE_PARAM or len(pairs) != 2:
            continue
        if _near(pairs[0], FROM_LL, TOL) and _near(pairs[1], TO_LL, TOL):
            routed = True
            break

    answered = False
    if routed and answer:
        if ASK == "time":
            got = _minutes(answer)
            answered = got is not None and got == EXPECTED_MINUTES
        else:
            got = _metres(answer)
            answered = got is not None and abs(got - EXPECTED_METRES) <= 50.0

    components = [
        {"name": COMPONENT_ROUTED, "score": 0.4 if routed else 0.0,
         "details": {"satisfied": routed}},
        {"name": COMPONENT_ANSWER, "score": 0.6 if answered else 0.0,
         "details": {"satisfied": answered, "expected_rendered": EXPECTED_RENDERED}},
    ]
    return {"score": round(sum(c["score"] for c in components), 6),
            "components": components}
'''


NEMO_TMPL = """#!/usr/bin/env python3
\"\"\"NeMo rollout reward for __TASK_ID__.

Same rubric as reward.py, reading the two inputs from where the rollout worker
puts them: the agent's terminate(answer=...) arrives as CUA_GYM_AGENT_ANSWER
(cuagym/browser_worker.py:303) and the visited URLs come from the page. Keeping
the parsing byte-identical to reward.py is what stops a task verifying one way
and training another.
\"\"\"
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reward as _r

def main():
    answer = (os.environ.get("CUA_GYM_AGENT_ANSWER") or "").strip()
    urls = json.loads(os.environ.get("CUA_GYM_FINAL_URLS") or "[]")
    evidence = {
        "agent_answer": answer,
        "apps": {"map": {"final_urls": urls, "final_text": "", "current_state": {}}},
    }
    result = _r.evaluate(evidence)
    print("REWARD: %s" % result["score"])

main()
"""


def build():
    root = pathlib.Path("osm_pilot/tasks/map")
    root.mkdir(parents=True, exist_ok=True)
    written = []
    for slug, eng, fq, tq, ask in SPECS:
        A = coord(fq)
        B = coord(tq)
        dur, dist = osrm(eng, A[:2], B[:2])
        answer = fmt_time(dur) if ask == "time" else fmt_dist(dist)

        # Margin discipline: the other two engines must RENDER a different
        # string, or the task does not actually test the engine choice.
        others = {}
        for e2 in ENG_PORT:
            if e2 == eng:
                continue
            d2, s2 = osrm(e2, A[:2], B[:2])
            others[e2] = fmt_time(d2) if ask == "time" else fmt_dist(s2)
        if answer in others.values():
            raise SystemExit(f"{slug}: answer {answer} collides with {others} -- drop it")

        exp_min = (round(dur / 60) if ask == "time" else -1)
        exp_m = (round(dist, 3) if ask == "distance" else -1.0)
        noun = "walking time" if ask == "time" else "distance"
        instruction = (
            f"Using the {ENG_LABEL[eng]} routing engine, find the route from "
            f"{fq} to {tq}. Report the {'total travel time' if ask=='time' else 'route distance'} "
            f"exactly as the site states it."
        )

        reward = (REWARD_TMPL
                  .replace("__TASK_ID__", slug)
                  .replace("__ENGINE_PARAM__", ENG_PARAM[eng])
                  .replace("__ENGINE__", eng)
                  # The reward matches against the pair the site DISPLAYS in
                  # ?route=, which is rounded to 3dp; routing used full precision.
                  .replace("__FROM_LAT__", repr(round(A[0], 3))).replace("__FROM_LON__", repr(round(A[1], 3)))
                  .replace("__TO_LAT__", repr(round(B[0], 3))).replace("__TO_LON__", repr(round(B[1], 3)))
                  .replace("__TOL__", "0.005")
                  .replace("__ASK__", ask)
                  .replace("__ANSWER__", answer)
                  .replace("__EXP_MIN__", str(exp_min))
                  .replace("__EXP_M__", str(exp_m)))

        d = root / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "reward.py").write_text(reward, encoding="utf-8")
        (d / "nemo_reward.py").write_text(NEMO_TMPL.replace("__TASK_ID__", slug), encoding="utf-8")
        manifest = {
            "schema_version": 2,
            "task_id": slug,
            "instruction": instruction,
            "apps": [{
                "name": "webarena_map_mock",
                "source_name": "map",
                "base_url_env": "CUA_GYM_WEBARENA_MAP_URL",
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
                "stateless": True,
            }],
            "reward_path": "reward.py",
            "requirements_path": None,
            "evidence": [],
            "source_evaluator": {},
            "source": "openstreetmap-pilot",
            "metadata": {
                "style": "explicit",
                "difficulty": "medium",
                "shape": "answer_with_url_evidence",
                "engine": eng,
                "expected_rendered": answer,
                "other_engine_renderings": others,
                "from_place": {"query": fq, "resolved": A[2], "nominatim_hits": A[3], "latlon": list(A[:2])},
                "to_place": {"query": tq, "resolved": B[2], "nominatim_hits": B[3], "latlon": list(B[:2])},
                "ground_truth_source": "nominatim :8085 top hit rounded to 3dp, OSRM :%d, site formatters" % ENG_PORT[eng],
                "raw": {"duration_s": dur, "distance_m": dist},
            },
        }
        (d / "task.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        (d / "task_instruction.json").write_text(json.dumps({
            "task_id": slug, "instruction": instruction, "difficulty": "medium",
            "start_path": "/",
            "success_criteria": (
                f"The final page is a /directions route using engine {ENG_PARAM[eng]} between "
                f"the two named places, and the reported answer is the {noun} the site renders: {answer}."
            ),
        }, indent=1) + "\n", encoding="utf-8")
        written.append((slug, ENG_LABEL[eng], answer, others, A[3], B[3]))
    return written


if __name__ == "__main__":
    for row in build():
        print("%-42s %-15s answer=%-8s others=%s hits=%d/%d" % row)
