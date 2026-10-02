"""Golden replay for __TASK_ID__ (family __FAMILY__).

Clicks and types only -- no goto, no URL assembly. Submits the site's own search
box, which is the Nominatim-backed "Go" the task asks about, and reads the
postcode out of the rendered result rather than out of the task's ground truth.

Returns the answer string, which runner.py records as `agent_answer`.

The search box, like every other control on this site, exists twice (a mobile
copy and a desktop copy) and the first one is hidden, so the selector is
:visible.
"""

import re

QUERY = __QUERY__


async def run(lane, task):
    page = lane.page()
    await page.wait_for_timeout(2500)

    box = page.locator("#query:visible").first
    await box.fill(QUERY)
    await page.wait_for_timeout(400)
    await box.press("Enter")

    text = ""
    for _ in range(45):
        await page.wait_for_timeout(1000)
        text = await page.locator("#sidebar_content").first.inner_text()
        if "Results from" in text and len(text.splitlines()) > 2:
            break

    # The first result line carries the full Nominatim display name, and the
    # postcode is the five-digit component of it.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        match = re.search(r"\b(\d{5})\b", line)
        if match and "," in line:
            return match.group(1)
    raise AssertionError("no postcode in the search results; sidebar was: "
                         + text[:300])
