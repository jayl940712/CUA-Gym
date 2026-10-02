"""Golden replay for __TASK_ID__ (family __FAMILY__).

Clicks only -- no goto, no URL assembly. The runner has already landed the lane
on "/", so this drives the Directions form from there.

Returns the answer string. runner.py stores a replay's return value on the lane
and evidence.py puts it in the document as `agent_answer`, mirroring the agent's
terminate(status, answer) at rollout time. The initial lane runs no replay, so
it reports nothing and an answer-scored reward reads 0.0 there.

The answer is READ OFF THE PAGE and then combined arithmetically -- it is never
copied from the task's ground truth. That is deliberate: it makes a passing
verification evidence that the frozen value really is what the site renders,
which is the one thing a self-consistent generator cannot prove about itself.

Four behaviours this sequence is built around, each found by instrumenting a
real run rather than by reading the markup:

* Every control exists TWICE (mobile copy + desktop copy) and the first is
  hidden, so every selector is :visible.
* Clicking Directions re-renders the sidebar, so we wait for the From field to
  become visible before touching it.
* Typing a place name kicks off geocoding, and OSM then REWRITES the field to
  the full display name. The waits below let that settle; clicking Go
  mid-geocode submits a half-built form and no route renders at all.
* Submitting a second leg leaves the PREVIOUS route on screen for a moment, so
  each leg waits for the URL to change before it trusts the panel.
* A second leg must CLEAR both fields before it fills them. Typing the new
  origin while the old destination is still present momentarily makes the two
  endpoints identical, and the site fires a degenerate A->A route for that
  state. OSRM answers it with snapping `hints`, the site caches them, and the
  real request then reuses hints that pin both waypoints to the same node --
  OSRM replies 400 NoRoute and the panel says "Couldn't find a route between
  those two places". Retrying does not help; the cached hints persist. Clearing
  first suppresses the degenerate query, and the leg issues exactly one clean
  request. This was diagnosed from the wire, not guessed: four two-leg tasks
  failed this way and the 400 response body reads {"code":"NoRoute"}.
"""

import re

# Executed in order. The last leg is the one the reward's proof-of-work gate is
# written against, so ordering here is part of the task, not a detail.
LEGS = __LEGS__


async def _leg(page, frm, to, engine_label, previous_url, refill, first):
    if refill:
        origin = page.locator("[name='route_from']:visible").first
        destination = page.locator("[name='route_to']:visible").first
        if not first:
            await origin.fill("")
            await destination.fill("")
            await page.wait_for_timeout(1200)
        await origin.fill(frm)
        await page.wait_for_timeout(400)
        await destination.fill(to)
        await page.wait_for_timeout(400)
    await page.locator("select.routing_engines:visible").first.select_option(
        label=engine_label
    )
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
        raise AssertionError(
            f"no Distance/Time line for {frm!r} -> {to!r} by {engine_label}; "
            "sidebar was: " + text[:200]
        )
    return match.group(1).strip(), match.group(2).strip(), page.url


def _minutes(clock):
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def _metres(rendered):
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(km|m)", rendered.strip(), re.I)
    if not match:
        raise AssertionError(f"unparseable distance from the site: {rendered!r}")
    value = float(match.group(1))
    return value * 1000.0 if match.group(2).lower() == "km" else value


async def run(lane, task):
    page = lane.page()
    await page.wait_for_timeout(2500)

    await page.locator(
        "a.switch_link:visible, a[href='/directions']:visible"
    ).first.click()
    await page.locator("[name='route_from']:visible").first.wait_for(
        state="visible", timeout=30000
    )
    await page.wait_for_timeout(1200)

    readings = []
    previous_url = page.url
    last_pair = None
    for index, leg in enumerate(LEGS):
        pair = (leg["from"], leg["to"])
        distance, clock, previous_url = await _leg(
            page, leg["from"], leg["to"], leg["engine_label"], previous_url,
            refill=(pair != last_pair), first=(index == 0),
        )
        last_pair = pair
        readings.append({"label": leg["label"], "distance": distance,
                         "clock": clock, "minutes": _minutes(clock),
                         "metres": _metres(distance)})

    return __COMBINE__
