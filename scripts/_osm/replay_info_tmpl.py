"""Golden replay for __TASK_ID__ (family __FAMILY__).

Clicks and types only -- no goto, no URL assembly. Searches the site, opens the
matching result's own OSM object page, and reads the answer out of what that
page renders.

The result is clicked BY HREF rather than by position or by name. The search
list puts a Nominatim credit link first and a "More results" link last, so
positional indexing is off by one and silently picks the wrong row; matching the
href is exact, and it is also precisely what the reward's proof-of-work gate
checks, so the replay and the reward cannot disagree about which object was
meant.

Returns the answer string, which runner.py records as `agent_answer`.
"""

import re

QUERY = __QUERY__
INFO_PATH = __INFO_PATH__
READ = __READ__          # "location" or "tag"
TAG_KEY = __TAG_KEY__


async def run(lane, task):
    page = lane.page()
    await page.wait_for_timeout(2500)

    box = page.locator("#query:visible").first
    await box.fill(QUERY)
    await page.wait_for_timeout(400)
    await box.press("Enter")

    link = page.locator(f'#sidebar_content a[href="{INFO_PATH}"]')
    await link.first.wait_for(state="visible", timeout=45000)
    await link.first.click()

    for _ in range(45):
        await page.wait_for_timeout(1000)
        if page.url.rstrip("/").endswith(INFO_PATH):
            break
    else:
        raise AssertionError(f"never landed on {INFO_PATH}; url is {page.url}")

    text = ""
    for _ in range(20):
        await page.wait_for_timeout(500)
        text = await page.locator("#sidebar_content").first.inner_text()
        if "Tags" in text or "Location:" in text:
            break

    if READ == "location":
        match = re.search(r"Location:\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", text)
        if not match:
            raise AssertionError("no Location line on the object page; page was: "
                                 + text[:300])
        return f"{match.group(1)}, {match.group(2)}"

    # The tag table renders one "key<TAB>value" row per tag.
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].strip() == TAG_KEY:
            return parts[1].strip()
    raise AssertionError(f"no {TAG_KEY!r} row in the tag table; page was: "
                         + text[:400])
