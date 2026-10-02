"""Golden replay for __TASK_ID__ (family __FAMILY__).

Clicks and types only. Runs the site's own category search, checks that the
places it lists are the ones this task was built on, then routes to each of them
in turn and derives the answer from what the panel renders.

Two details this is built around, both learned the hard way:

* The candidate list is ASSERTED against the page, not assumed. If the site's
  search returns something other than what ground truth was computed from, the
  replay fails loudly here instead of silently scoring a stale answer. The
  comparison collapses whitespace first: OSM names can carry doubled spaces
  ("East Side -  Post Office" is a real one) and HTML rendering collapses them,
  so a literal check reports a mismatch that is not one.
* Each leg CLEARS both route fields before filling them. Typing a new origin
  while the old destination is still present momentarily makes the endpoints
  identical; the site fires a degenerate A->A route, caches OSRM's snapping
  hints from it, and the real request then comes back 400 NoRoute. Retrying does
  not help -- the cached hints persist.

Returns the answer string, which runner.py records as `agent_answer`.
"""

import re

SEARCH_QUERY = __SEARCH_QUERY__
ANCHOR = __ANCHOR__
CANDIDATES = __CANDIDATES__       # [{"name": ..., "route_to": ...}, ...]
ENGINE_LABEL = __ENGINE_LABEL__
THEN_INFO = __THEN_INFO__         # None, or {"path": ..., "tag": ...}


def _minutes(clock):
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def _metres(rendered):
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(km|m)", rendered.strip(), re.I)
    if not match:
        raise AssertionError(f"unparseable distance from the site: {rendered!r}")
    value = float(match.group(1))
    return value * 1000.0 if match.group(2).lower() == "km" else value


def _flat(text):
    return re.sub(r"\s+", " ", text)


async def _back_to_search(page):
    """Restore the search box after routing.

    The directions panel REPLACES the search box, and there is no visible link
    back: the only two a.switch_link elements on the page are both hidden and
    both point at /directions. The panel's own close button is the way back --
    the FIRST visible button.btn-close, not the last (the last one belongs to
    another dismissable and leaves the panel up).
    """
    if await page.locator("#query:visible").count():
        return
    await page.locator("button.btn-close:visible").first.click()
    await page.locator("#query:visible").first.wait_for(state="visible",
                                                        timeout=30000)
    await page.wait_for_timeout(800)


async def _search(page, query):
    await _back_to_search(page)
    box = page.locator("#query:visible").first
    await box.fill(query)
    await page.wait_for_timeout(400)
    await box.press("Enter")
    text = ""
    for _ in range(45):
        await page.wait_for_timeout(1000)
        text = await page.locator("#sidebar_content").first.inner_text()
        if "Results from" in text and len(text.splitlines()) > 3:
            break
    return text


async def _route(page, frm, to, previous_url):
    origin = page.locator("[name='route_from']:visible").first
    destination = page.locator("[name='route_to']:visible").first
    await origin.fill("")
    await destination.fill("")
    await page.wait_for_timeout(1200)
    await origin.fill(frm)
    await page.wait_for_timeout(500)
    await destination.fill(to)
    await page.wait_for_timeout(500)
    await page.locator("select.routing_engines:visible").first.select_option(
        label=ENGINE_LABEL)
    await page.wait_for_timeout(500)
    await page.locator(
        "input[type=submit][value=Go]:visible, .routing_go:visible"
    ).first.click()

    text = ""
    for _ in range(45):
        await page.wait_for_timeout(1000)
        text = await page.locator("#sidebar_content").first.inner_text()
        if "Distance:" in text and page.url != previous_url:
            break
    match = re.search(r"Distance:\s*(.+?)\.\s+Time:\s*(\d+:\d{2})", text)
    if not match:
        raise AssertionError(f"no Distance/Time line for {to!r}; sidebar was: "
                             + text[:200])
    return match.group(1).strip(), match.group(2).strip(), page.url


async def run(lane, task):
    page = lane.page()
    await page.wait_for_timeout(2500)

    listing = _flat(await _search(page, SEARCH_QUERY))
    missing = [c["name"] for c in CANDIDATES if _flat(c["name"]) not in listing]
    if missing:
        raise AssertionError(
            "the site's search no longer lists " + ", ".join(missing)
            + "; ground truth is stale. Listing was: " + listing[:400])

    await page.locator(
        "a.switch_link:visible, a[href='/directions']:visible").first.click()
    await page.locator("[name='route_from']:visible").first.wait_for(
        state="visible", timeout=30000)
    await page.wait_for_timeout(1200)

    readings = []
    previous_url = page.url
    for candidate in CANDIDATES:
        distance, clock, previous_url = await _route(
            page, ANCHOR, candidate["route_to"], previous_url)
        readings.append({"label": candidate["name"], "clock": clock,
                         "minutes": _minutes(clock), "distance": distance,
                         "metres": _metres(distance)})

    if THEN_INFO:
        text = await _search(page, THEN_INFO["query"])
        link = page.locator(f'#sidebar_content a[href="{THEN_INFO["path"]}"]')
        await link.first.wait_for(state="visible", timeout=45000)
        await link.first.click()
        for _ in range(45):
            await page.wait_for_timeout(1000)
            if page.url.rstrip("/").endswith(THEN_INFO["path"]):
                break
        else:
            raise AssertionError(f"never landed on {THEN_INFO['path']}")
        for _ in range(20):
            await page.wait_for_timeout(500)
            text = await page.locator("#sidebar_content").first.inner_text()
            if "Tags" in text:
                break
        for line in text.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0].strip() == THEN_INFO["tag"]:
                return parts[1].strip()
        raise AssertionError(f"no {THEN_INFO['tag']!r} row; page was: " + text[:400])

    return __COMBINE__
