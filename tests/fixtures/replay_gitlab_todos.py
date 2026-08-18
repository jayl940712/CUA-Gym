"""Known-correct replay for the WebArena 'check my todos' smoke task."""


async def run(lane, _task):
    page = lane.page("gitlab")
    await page.goto(
        f"{lane.endpoints['gitlab'].base_url}/dashboard/todos?sid={lane.sid}",
        wait_until="domcontentloaded",
    )
