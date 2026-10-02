#!/usr/bin/env python3
"""Shared OpenStreetMap ground-truth helpers for the map batch.

Everything here talks to the SAME Nominatim/OSRM services the website itself
calls, with the same parameters, so a value computed here is the value the UI
renders. See TASK_MAP.md sections 4 and 7 for why each detail matters; the two
that bite hardest are the viewbox on geocoding and keeping full coordinate
precision when routing.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

H = "18.116.12.228"
SITE = f"http://{H}:3000"

# The viewbox the site sends from a cold "/" load (#map=7/42.896/-75.108).
# Every task starts at "/", so this is deterministic.
VIEWBOX = ("-82.79296875000001,39.402244340292775,"
           "-67.41210937500001,46.20264638061019")

ENG_PORT = {"car": 5000, "bike": 5001, "foot": 5002}
ENG_PARAM = {"car": "fossgis_osrm_car", "bike": "fossgis_osrm_bike",
             "foot": "fossgis_osrm_foot"}
ENG_LABEL = {"car": "Car (OSRM)", "bike": "Bicycle (OSRM)", "foot": "Foot (OSRM)"}
VERB = {"car": "drive", "bike": "cycle", "foot": "walk"}
GERUND = {"car": "driving", "bike": "cycling", "foot": "walking"}
# Words a reward accepts as naming each engine. Used by the comparison families,
# where the answer has to say WHICH mode won, not just a number.
MODE_WORDS = {
    "car": ("car", "drive", "driving", "drove"),
    "bike": ("bike", "bicycle", "cycle", "cycling", "biking"),
    "foot": ("foot", "walk", "walking", "on foot"),
}


def _get(url: str, timeout: int = 30):
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as fh:
                return json.load(fh)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue
    raise RuntimeError(f"three failed attempts: {url}")


def nominatim(query: str) -> list:
    """Top hits for a place string, requested exactly as the site requests them."""
    url = (f"http://{H}:8085/search?q={urllib.parse.quote(query)}&format=json"
           f"&addressdetails=1&viewbox={urllib.parse.quote(VIEWBOX)}")
    return _get(url, timeout=25)


def nominatim_local(query: str, lat: float, lon: float, span: float):
    """Top hit's OSM identity under a view centred on (lat, lon).

    Used to check that a place still resolves to the same object after an
    earlier route has moved the map -- see stable_under_moved_map().
    """
    viewbox = f"{lon - span},{lat - span},{lon + span},{lat + span}"
    url = (f"http://{H}:8085/search?q={urllib.parse.quote(query)}&format=json"
           f"&viewbox={urllib.parse.quote(viewbox)}")
    hits = _get(url, timeout=25)
    return (hits[0].get("osm_type"), hits[0].get("osm_id")) if hits else None


def osrm(engine: str, a, b):
    """(duration_s, distance_m) for a->b, using the site's own query string.

    Coordinates go in at FULL precision. The 3-decimal pair in the ?route= URL
    parameter is display only; rounding before routing shifts the rendered
    answer by a minute and a hundred metres.
    """
    url = (f"http://{H}:{ENG_PORT[engine]}/route/v1/driving/"
           f"{a[1]},{a[0]};{b[1]},{b[0]}"
           f"?overview=false&geometries=polyline&steps=true")
    doc = _get(url, timeout=40)
    routes = doc.get("routes") or []
    if not routes:
        raise RuntimeError(f"no {engine} route between {a} and {b}")
    return routes[0]["duration"], routes[0]["distance"]


def fmt_time(seconds: float) -> str:
    """The site's formatTime, transcribed from its JS bundle."""
    m = round(seconds / 60)
    h = m // 60
    m -= h * 60
    return f"{h}:{m:02d}"


def fmt_dist(metres: float) -> str:
    """The site's formatDistance, transcribed from its JS bundle."""
    if metres < 1000:
        return f"{round(metres)}m"
    if metres < 10000:
        return f"{metres / 1000.0:.1f}km"
    return f"{round(metres / 1000)}km"
