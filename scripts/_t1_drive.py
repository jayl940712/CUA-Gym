#!/usr/bin/env python3
"""Drive lane-30 golden replays against fresh sids and print per-task scores."""
import asyncio, importlib.util, json, sys, types, uuid
from pathlib import Path
import requests

ROOT = Path("/home/ubuntu/CUA-Gym")
sys.path.insert(0, str(ROOT))
import cuagym.hub_apps as hub_apps
for n, m in (("resources_servers", types.ModuleType("resources_servers")),
             ("resources_servers.cuagym", types.ModuleType("resources_servers.cuagym"))):
    m.__path__ = []
    sys.modules.setdefault(n, m)
sys.modules.setdefault("resources_servers.cuagym.hub_apps", hub_apps)
from cuagym.episode_code import substitute

BASE = "http://localhost:8004"
TASKS = ROOT / "output/tasks/shopping"
REPLAYS = TASKS / "_batches/shopping_advsearch_bench/replays"


class Lane:
    def __init__(self, page): self._page = page
    def page(self, name=None):
        if name in (None, "shopping", "webarena_shopping_mock"): return self._page
        raise KeyError(name)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evidence_for(state, urls, html, text):
    blank = {"initial_state": {}, "current_state": state, "state_diff": {},
             "final_urls": urls, "final_html": html, "final_text": text}
    return {"schema_version": 1, "task_id": "x", "instruction": "", "lane": "golden",
            "apps": {"shopping": blank, "webarena_shopping_mock": blank},
            "observations": []}


async def drive(bundle, pw, round_id):
    task_id = bundle.name
    sid = f"t1-{round_id}-{uuid.uuid4().hex[:8]}"
    setup = bundle / "initial_setup.py"
    if setup.is_file():
        code = substitute(setup.read_text(), sid=sid, hub_base_url="http://localhost", base_port=8000)
        exec(compile(code, str(setup), "exec"), {"__name__": "__main__"})
    reward = load(bundle / "reward.py", f"rw_{task_id}")

    pre = requests.get(f"{BASE}/go?sid={sid}", timeout=60).json()
    pre_score = reward.evaluate(evidence_for(pre.get("current_state") or {}, [], "", ""))["score"]

    browser = await pw.chromium.launch()
    ctx = await browser.new_context()
    page = await ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.goto(f"{BASE}/?sid={sid}", wait_until="domcontentloaded")
    replay = load(REPLAYS / f"{task_id}.py", f"rp_{task_id}")
    try:
        await replay.run(Lane(page), None)
        failure = None
    except Exception as exc:  # noqa: BLE001
        failure = f"{type(exc).__name__}: {exc}"
    await page.wait_for_timeout(2500)
    urls, html, text = [page.url], await page.content(), await page.locator("body").inner_text()
    await browser.close()

    import subprocess
    nemo = substitute((bundle / "nemo_reward.py").read_text(), sid=sid,
                      hub_base_url="http://localhost", base_port=8000)
    out = subprocess.run([sys.executable, "-c", nemo], capture_output=True, text=True)
    nemo_score = [l for l in out.stdout.splitlines() if l.startswith("REWARD:")]

    post = requests.get(f"{BASE}/go?sid={sid}", timeout=60).json()
    result = reward.evaluate(evidence_for(post.get("current_state") or {}, urls, html, text))
    return {"task_id": task_id, "sid": sid, "initial": pre_score,
            "replay": result["score"], "failure": failure,
            "nemo": nemo_score,
            "components": {c["name"]: c["score"] for c in result["components"]},
            "page_errors": errors[:3]}


async def main():
    from playwright.async_api import async_playwright
    only = sys.argv[2:] or None
    round_id = sys.argv[1]
    bundles = sorted(p for p in TASKS.glob("shopping_advsearch_bench_*") if p.is_dir())
    if only:
        bundles = [b for b in bundles if any(o in b.name for o in only)]
    async with async_playwright() as pw:
        for b in bundles:
            r = await drive(b, pw, round_id)
            flag = "OK " if (r["initial"] == 0.0 and r["replay"] == 1.0 and not r["failure"]) else "BAD"
            print(f"{flag} {r['task_id']:62s} initial={r['initial']} replay={r['replay']} nemo={r['nemo']}")
            if flag == "BAD":
                print("     failure:", r["failure"])
                print("     components:", r["components"])
                if r["page_errors"]:
                    print("     page errors:", r["page_errors"])

asyncio.run(main())
