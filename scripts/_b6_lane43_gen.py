#!/usr/bin/env python3
"""Batch-6 lane 43 generator - shopping / described_need_to_wishlist (R8 -> A4).

Writes ten schema-v2 bundles under output/tasks/shopping/<task_id>/ plus the
lane's GENERATION.md and golden-replay drafts.

Every task: a paraphrased need that resolves to EXACTLY ONE listable product,
wish-listed. Rubric asserts the exact resulting wishlist collection.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/described_need_to_wishlist")

ANALOGUES = {
    "laundry": "Add a laundry detergent to my wish list.",
    "toothpaste": "Add a toothpaste to my wish list.",
    "chair": "Add a chair to my wish list.",
    "desk": "Add a white desk to my wish list.",
    "computer_desk": "Add a white computer desk to my wish list.",
}

INSPIRATION = ["webarena-511", "webarena-512", "webarena-513", "webarena-514", "webarena-515"]

TASKS = [
    {
        "id": "described_need_to_wishlist_damp_basement_dehumidifier_001",
        "pid": 34941,
        "sku": "B09HH9DTVG",
        "name": "Vellgoo Cordless Dehumidifier, Gun Safe Dehumidifier Rechargeable, Up to 180 Cubic Feet (55 sq. ft) 3.4oz Wireless Small Dehumidifiers for Home, Bathroom, Closet, Wardrobe, RV",
        "price": "40.99",
        "style": "terse",
        "shape": "retrieval_writeback",
        "query": "dehumidifier",
        "instruction": (
            "The basement is damp and the windows run with condensation every morning. "
            "Find something in the store that pulls the moisture out of the air, keep it "
            "under $45, and add that product to my wish list."
        ),
        "chain": "read the described damp-air problem -> resolve it to the only dehumidifier under $45 -> add that product to the wish list",
        "analogue": "laundry",
        "unique": (
            "Three listable products are dehumidifiers (34941 $40.99, 97955 $49.98, "
            "15569 $79.99, all in Heating, Cooling & Air Quality). Exactly one is under "
            "$45. Nearest rival is $8.99 away and the $45 threshold sits in a $9 gap."
        ),
        "reach": "Search 'dehumidifier' (uncaptured term): 3 full-strong hits, target is row 2 of page 1.",
    },
    {
        "id": "described_need_to_wishlist_noisy_street_sleep_fan_002",
        "pid": 32630,
        "sku": "B07M5N3KFQ",
        "name": "Honeywell Dreamweaver Sleep Black – Personal Fan with Pink Noise – USB Charging Port and On/Off Airflow for Use on Nightstand or Desk",
        "price": "39.98",
        "style": "terse",
        "shape": "mutation",
        "query": "personal fan",
        "instruction": (
            "The bedroom gets stuffy at night and the street outside is loud. Find the one "
            "fan this store sells that also produces noise to help you sleep, and put it on "
            "my wish list."
        ),
        "chain": "read the stuffy-and-noisy bedroom need -> resolve it to the only fan in the catalog that also emits sleep noise -> add that product to the wish list",
        "analogue": "chair",
        "unique": (
            "32630 is the ONLY listable product in the whole 22,460-row catalog whose name "
            "mentions pink noise, white noise, a sound machine or any sleep-sound feature. "
            "The other fans in Heating, Cooling & Air Quality (15786, 16950, 33449, 71216) "
            "move air only."
        ),
        "reach": "Search 'personal fan' (uncaptured): 1 full-strong hit, row 1. 'sleep fan' and 'noise fan' also return it at row 1.",
    },
    {
        "id": "described_need_to_wishlist_sugar_free_antacid_003",
        "pid": 32232,
        "sku": "B079JYG27H",
        "name": "TUMS Extra Strength Chewable Sugar Free Antacid Tablets for Heartburn Relief, Melon Berry, 80 Count",
        "price": "4.19",
        "style": "terse",
        "shape": "mutation",
        "query": "antacid",
        "instruction": (
            "Heartburn again after every dinner, and I'm diabetic. Pick me chewable tablets "
            "for it that contain no sugar, and save that product to my wish list."
        ),
        "chain": "read the heartburn-plus-diabetes need -> resolve it to the only sugar-free antacid in the catalog -> add that product to the wish list",
        "analogue": "toothpaste",
        "unique": (
            "Exactly two listable products treat heartburn (32232 and 14098; a regex over "
            "antacid / heartburn / acid indigestion / acid reducer / famotidine / omeprazole "
            "/ ranitidine / acid reflux returns those two and nothing else). Only 32232 is "
            "sugar free; 14098 is the sugared Ultra Strength assorted-fruit tub."
        ),
        "reach": "Search 'antacid' (uncaptured): 2 full-strong hits, target is row 2 of page 1. 'heartburn' returns the same pair.",
    },
    {
        "id": "described_need_to_wishlist_ear_camera_budget_tool_004",
        "pid": 97148,
        "sku": "B08VNKCSFV",
        "name": "Topicy Ear Wax Removal Tool,Ear Cleaner with Camera,1080P HD Ear Wax Remover Endoscope with Led Light,Wireless Otoscope",
        "price": "25.99",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "query": "ear wax removal tool",
        "instruction": (
            "I clean my ears with a pick and can never see what I am doing. Look through the "
            "store for an ear-cleaning tool that has a camera built into it so you can watch "
            "on a screen. More than one product does that, so take the one that costs less "
            "than $30. Add exactly that product to my wish list, and leave the wish list "
            "holding nothing else."
        ),
        "chain": "read the described 'cannot see inside my ear' need -> resolve it to the only camera ear-cleaning tool under $30 -> add that product to the wish list",
        "analogue": "toothpaste",
        "unique": (
            "Two listable products are ear-wax tools with a camera: 97148 ($25.99) and 97001 "
            "($49.99). No other otoscope / ear-endoscope row exists (the other 'ear ... "
            "camera' regex hits are car reverse cameras, phone cases and smartwatches). "
            "Exactly one is under $30, with a $24.00 margin."
        ),
        "reach": "Search 'ear wax removal tool' (uncaptured): 5 full-strong hits, target is row 5 of page 1.",
    },
    {
        "id": "described_need_to_wishlist_touchscreen_hygrometer_005",
        "pid": 67337,
        "sku": "B06XTPTG1J",
        "name": "ThermoPro TP55 Digital Hygrometer Indoor Thermometer Humidity Gauge with Jumbo Touchscreen and Backlight Temperature Humidity Monitor, 5s Fast Refresh",
        "price": "12.74",
        "style": "terse",
        "shape": "retrieval_writeback",
        "query": "hygrometer",
        "instruction": (
            "I want to know how damp the bedroom actually gets. Find a gauge that reads both "
            "temperature and humidity, has a touchscreen, and costs under $20, then add it to "
            "my wish list."
        ),
        "chain": "read the 'how damp is this room' need -> resolve it to the only touchscreen humidity gauge under $20 -> add that product to the wish list",
        "analogue": "chair",
        "unique": (
            "Three listable products are hygrometers: 17639 ($11.28, a digital alarm clock, "
            "no touchscreen), 67337 ($12.74, jumbo touchscreen) and 11193 ($23.79, "
            "touchscreen LCD). Exactly one satisfies touchscreen AND under $20."
        ),
        "reach": "Search 'hygrometer' (uncaptured): 3 full-strong hits, target is row 2 of page 1.",
    },
    {
        "id": "described_need_to_wishlist_self_watering_three_pack_006",
        "pid": 97810,
        "sku": "B0862FHNPB",
        "name": "Vanavazon 6 Inch Self Watering Planter Pots for Indoor Plants, 3 Pack African Violet Pots with Wick Rope-Grey",
        "price": "16.99",
        "style": "terse",
        "shape": "mutation",
        "query": "self watering planter",
        "instruction": (
            "We are away for a fortnight and the houseplants always die while we are gone. "
            "Find the indoor pots that water themselves, sold as a pack of three, and add "
            "that product to my wish list."
        ),
        "chain": "read the 'plants die while we are away' need -> resolve it to the only three-pack of self-watering indoor pots -> add that product to the wish list",
        "analogue": "desk",
        "unique": (
            "Five listable products self-water: 97810 (3 Pack), 31996 (Set of 2 wall "
            "planter plates), 69620 (single windowsill herb planter), 70215 (raised garden "
            "bed) and 71109 (single 20-inch pot). Exactly one is a three-pack of indoor pots."
        ),
        "reach": "Search 'self watering planter' (uncaptured): 5 full-strong hits, target is row 5 of page 1.",
    },
    {
        "id": "described_need_to_wishlist_cassette_to_usb_converter_007",
        "pid": 99856,
        "sku": "B09RWN7D8H",
        "name": "Gmossopy USB2.0 Portable Tape to PC Super Cassette To MP3 Audio Music CD Digital Player Converter Capture Recorder",
        "price": "9.43",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "query": "cassette converter",
        "instruction": (
            "I found a shoebox of old cassette tapes and I want them as MP3 files on my "
            "laptop. Search the store for a player that reads a cassette and sends the audio "
            "to a computer over USB. Two products do that; only one of them is under $15. "
            "Add exactly that product to my wish list and leave nothing else on the list."
        ),
        "chain": "read the 'digitise my old tapes' need -> resolve it to the only USB cassette-to-PC converter under $15 -> add that product to the wish list",
        "analogue": "computer_desk",
        "unique": (
            "Two listable products convert a cassette to a computer over USB: 99856 ($9.43) "
            "and 101174 ($22.99). 19698 ($0.99) is a car cassette-deck AUX adapter with a "
            "3.5 mm jack and no USB, and 77085 is a Sony iPod cassette adapter; neither "
            "reaches a PC. Exactly one of the two USB converters is under $15, margin $13.56."
        ),
        "reach": "Search 'cassette converter' (uncaptured): 3 full-strong hits, target is row 2 of page 1.",
    },
    {
        "id": "described_need_to_wishlist_battery_heated_blanket_008",
        "pid": 31262,
        "sku": "B09DC6BX5S",
        "name": "Portable Heated Blanket Battery Operated | Rechargeable Heating Electric Throws for Camping, Outdoors and Travel",
        "price": "146.90",
        "style": "terse",
        "shape": "mutation",
        "query": "heated blanket",
        "instruction": (
            "Mum sits out in the garden in the evenings and there is no socket out there. "
            "Find the heated blanket that runs on a battery rather than mains power, and add "
            "it to my wish list."
        ),
        "chain": "read the 'warmth where there is no power socket' need -> resolve it to the only battery-operated heated blanket -> add that product to the wish list",
        "analogue": "chair",
        "unique": (
            "Eight listable products are electric heated blankets or throws (97789, 97808, "
            "98392, 32062, 35424, 32238, 88331, 31262). 31262 is the only battery-operated / "
            "rechargeable one, and the only catalog row at all matching a battery-powered "
            "blanket regex; the two USB throws still need a powered port."
        ),
        "reach": "Search 'heated blanket' (uncaptured): 8 full-strong hits, target is row 1 of page 1. 'electric blanket' also returns it at row 1.",
    },
    {
        "id": "described_need_to_wishlist_no_bake_sugar_free_mix_009",
        "pid": 43917,
        "sku": "B01N10J04M",
        "name": "GramZero No-Bake Cheesecake Mix, Makes 2 Cheesecakes, No Sugar Added, Low Calorie, Stevia Sweetened",
        "price": "9.95",
        "style": "terse",
        "shape": "mutation",
        "query": "no bake",
        "instruction": (
            "A diabetic friend's birthday is Saturday and my oven has died. Find a dessert "
            "mix with no sugar added that sets without baking, and add it to my wish list."
        ),
        "chain": "read the 'sugar-free dessert, no oven' need -> resolve it to the only no-bake no-sugar-added dessert mix -> add that product to the wish list",
        "analogue": "toothpaste",
        "unique": (
            "Two listable products are no-bake mixes: 43917 (GramZero No-Bake Cheesecake "
            "Mix, No Sugar Added) and 22756 (Majka No-Bake Lactation Cookies Mix, not sugar "
            "free). The store's other no-sugar-added stevia mix, 103557, is a Chocolate Cake "
            "Mix that has to be baked. Exactly one row is both no-bake and no-sugar-added."
        ),
        "reach": "Search 'no bake' (uncaptured; 'no' is a stopword so the token is 'bake'): 12 full-strong hits fill page 1 and the target is row 9.",
    },
    {
        "id": "described_need_to_wishlist_budget_label_printer_010",
        "pid": 15930,
        "sku": "B09BDRTW41",
        "name": "BBGGJ Label Printer- Portable Bluetooth Thermal Label Maker Apply to Labeling, Shipping, Office, Cable, Barcode, Compatible with Android & iOS System",
        "price": "20.43",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "query": "label maker",
        "instruction": (
            "I am relabelling every cable and drawer in the office and need a small machine "
            "that prints stick-on labels. The store carries three of them; only one costs "
            "under $25. Put that one on my wish list, and make sure the wish list ends up "
            "holding just that product."
        ),
        "chain": "read the 'label everything in the office' need -> resolve it to the only label printer under $25 -> add that product to the wish list",
        "analogue": "desk",
        "unique": (
            "Three listable products are label printers: 15930 ($20.43), 68508 ($31.44) and "
            "35199 ($149.99), all in Office Products > Office Electronics. Exactly one is "
            "under $25, margin $11.01."
        ),
        "reach": "Search 'label maker' (uncaptured): 3 full-strong hits, target is row 1 of page 1.",
    },
]

REWARD_TMPL = '''"""Deterministic reward for {tid}.

Success criterion (exact resulting collection, TASK4 S3.3):

  * state.wishlist.items holds EXACTLY ONE row;
  * that row's productId is {pid} and its sku is "{sku}" -- the single
    listable product that satisfies every attribute stated in the
    instruction;
  * its qty is a whole number >= 1.

The wish list boots empty (src/data/wishlist.json is {{"items": []}}), so
the untouched state scores 0.0, and an agent that skipped the retrieval and
wish-listed a neighbouring product scores 0.0 rather than partial credit.

Reads `current_state` only. Never diffs against `initial_state`.
"""

import json

TARGET = json.loads(r"""
{{
 "productId": {pid},
 "sku": "{sku}",
 "name": {name_json},
 "price": "{price}"
}}
""")


def _num(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _int(value):
    number = _num(value)
    if number is None:
        return None
    return int(number) if float(number).is_integer() else None


def _text(value):
    return value.strip() if isinstance(value, str) else None


def _wishlist_rows(state):
    if not isinstance(state, dict):
        return []
    wishlist = state.get("wishlist")
    items = wishlist.get("items") if isinstance(wishlist, dict) else None
    if not isinstance(items, list):
        return []
    return [row for row in items if isinstance(row, dict)]


def _wishlist_is_exactly_target(state):
    rows = _wishlist_rows(state)
    if len(rows) != 1:
        return False
    row = rows[0]
    if _int(row.get("productId")) != TARGET["productId"]:
        return False
    if _text(row.get("sku")) != TARGET["sku"]:
        return False
    qty = _int(row.get("qty"))
    if qty is None or qty < 1:
        return False
    return True


COMPONENT_WEIGHTS = {{
    "wishlist_is_exactly_the_described_product": 1.0,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def _checks(state):
    return {{
        "wishlist_is_exactly_the_described_product": _wishlist_is_exactly_target(state),
    }}


def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {{}}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state")
    if not isinstance(state, dict):
        state = {{}}
    checks = _checks(state)
    components = [
        {{
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {{"satisfied": bool(checks.get(name))}},
        }}
        for name in COMPONENT_WEIGHTS
    ]
    return {{
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }}
'''

NEMO_TMPL = '''"""NeMo-Gym reward program for {tid}.

Rubric parity with reward.py: state.wishlist.items must hold exactly one
row, naming product {pid} with sku "{sku}" and a whole-number qty >= 1.

Reads `current_state` from GET /go?sid=... and prints `REWARD: <float>` on
every output path. Self-contained: standard library plus requests, which is
present in cuagym/requirements.txt.
"""

import json
import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

TARGET = json.loads(r"""
{{
 "productId": {pid},
 "sku": "{sku}",
 "name": {name_json},
 "price": "{price}"
}}
""")


def _num(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _int(value):
    number = _num(value)
    if number is None:
        return None
    return int(number) if float(number).is_integer() else None


def _text(value):
    return value.strip() if isinstance(value, str) else None


def _wishlist_rows(state):
    if not isinstance(state, dict):
        return []
    wishlist = state.get("wishlist")
    items = wishlist.get("items") if isinstance(wishlist, dict) else None
    if not isinstance(items, list):
        return []
    return [row for row in items if isinstance(row, dict)]


def _wishlist_is_exactly_target(state):
    rows = _wishlist_rows(state)
    if len(rows) != 1:
        return False
    row = rows[0]
    if _int(row.get("productId")) != TARGET["productId"]:
        return False
    if _text(row.get("sku")) != TARGET["sku"]:
        return False
    qty = _int(row.get("qty"))
    if qty is None or qty < 1:
        return False
    return True


COMPONENT_WEIGHTS = {{
    "wishlist_is_exactly_the_described_product": 1.0,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def _checks(state):
    return {{
        "wishlist_is_exactly_the_described_product": _wishlist_is_exactly_target(state),
    }}


def _fetch_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    return state if isinstance(state, dict) else {{}}


def main():
    try:
        state = _fetch_state()
    except Exception as exc:  # noqa: BLE001 - reward must always emit a score
        print("reward error: " + str(exc))
        print("REWARD: 0.0")
        return
    checks = _checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
        print("component " + name + ": " + str(bool(checks.get(name))))
    print("REWARD: " + str(round(total, 6)))


main()
'''

REPLAY_TMPL = '''"""Golden replay draft - {tid}.

Known-correct path, starting at "/" and using only rendered controls:
  1. type the need's product words into the header search box (#search) and
     submit the form with Enter;
  2. on the result grid click the product title link of the ONE product that
     satisfies every stated attribute;
  3. on the product page click a.action.towishlist.

Expected end state: wishlist.items == [{{productId: {pid}, sku: "{sku}", qty: 1}}].
No typed URLs; no deep links.
"""

SEARCH_QUERY = {query_json}
TARGET_NAME = {name_json}
TARGET_ID = {pid}
TARGET_SKU = "{sku}"


def run(page, base_url):
    page.goto(base_url + "/")
    page.wait_for_selector("#search")
    page.fill("#search", SEARCH_QUERY)
    page.press("#search", "Enter")
    page.wait_for_selector("li.product-item, .product-item")
    link = page.locator("a.product-item-link", has_text=TARGET_NAME[:60]).first
    link.click()
    page.wait_for_selector("a.action.towishlist")
    page.click("a.action.towishlist")
    page.wait_for_timeout(500)
'''


def bundle(spec):
    tid = spec["id"]
    d = os.path.join(OUT, tid)
    os.makedirs(d, exist_ok=True)
    name_json = json.dumps(spec["name"])
    query_json = json.dumps(spec["query"])

    fmt = dict(
        tid=tid,
        pid=spec["pid"],
        sku=spec["sku"],
        price=spec["price"],
        name_json=name_json,
        query_json=query_json,
    )

    reward = REWARD_TMPL.format(**fmt)
    nemo_reward = NEMO_TMPL.format(**fmt)

    criteria = [
        (
            "state.wishlist.items holds exactly one row; that row's productId is %d "
            "and its sku is \"%s\" (%s, $%s), and its qty is a whole number >= 1."
            % (spec["pid"], spec["sku"], spec["name"], spec["price"])
        ),
        (
            "No other product is left on the wish list: the collection is exactly "
            "[%d]." % spec["pid"]
        ),
    ]

    ti = {
        "task_id": tid,
        "task_instruction": spec["instruction"],
        "app_dir": "webarena_shopping_mock",
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": criteria,
    }

    task = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": spec["instruction"],
        "apps": [
            {
                "name": "webarena_shopping_mock",
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
            }
        ],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": {
            "style": spec["style"],
            "difficulty": "medium",
            "shape": spec["shape"],
            "skills": ["R8", "A4"],
            "skill_chain": spec["chain"],
            "derived_from": "semantic_need_to_wishlist_power_strip_006",
            "official_analogues": [ANALOGUES[spec["analogue"]]],
            "injected_preconditions": [],
            "hard_criteria": [],
            "topic": "described_need_to_wishlist",
            "batch": "batch-6 lane 43 (shopping / described_need_to_wishlist)",
            "lane_skill_chain": "R8 -> A4",
            "inspiration_ids": INSPIRATION,
            "target_product_id": spec["pid"],
            "target_sku": spec["sku"],
            "target_name": spec["name"],
            "target_price": spec["price"],
            "authoring_notes": [
                "Uniqueness: " + spec["unique"],
                "Click reachability: " + spec["reach"],
                "The wish list boots empty (src/data/wishlist.json is {\"items\": []}), "
                "so the untouched state scores 0.0 and the rubric can assert the exact "
                "resulting collection rather than a count.",
                "addToWishlist (AppContext.jsx:324-346) records productId, sku, name, "
                "finalPrice, qty, description and addedAt; the reward gates on the "
                "recorded productId/sku/qty values, not on 'a row was written'.",
                "The tile wish-list heart (ProductGrid.jsx:98-118) calls addToWishlist "
                "directly and does NOT redirect to the PDP on required options - only "
                "AddToCartButton (ProductGrid.jsx:63-66) does - so both the grid heart "
                "and the PDP anchor (ProductPage.jsx:797-816) are valid click paths.",
            ],
        },
    }

    nemo = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_shopping_mock"],
            "start_urls": [],
            "intent": spec["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": "webarena_shopping_mock",
                "initial_setup": None,
                "eval_reward_code": nemo_reward,
            },
        }
    }

    with open(os.path.join(d, "task_instruction.json"), "w") as f:
        json.dump(ti, f, indent=2)
        f.write("\n")
    with open(os.path.join(d, "task.json"), "w") as f:
        json.dump(task, f, indent=2)
        f.write("\n")
    with open(os.path.join(d, "reward.py"), "w") as f:
        f.write(reward)
    with open(os.path.join(d, "nemo_reward.py"), "w") as f:
        f.write(nemo_reward)
    with open(os.path.join(d, "nemo_task.json"), "w") as f:
        json.dump(nemo, f, indent=2)
        f.write("\n")

    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as f:
        f.write(REPLAY_TMPL.format(**fmt))

    return nemo


def main():
    os.makedirs(BATCH, exist_ok=True)
    rows = [bundle(spec) for spec in TASKS]
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump(
            {
                "schema_version": 2,
                "tasks": [
                    {"task_id": s["id"], "path": "../../" + s["id"] + "/task.json"}
                    for s in TASKS
                ],
            },
            f,
            indent=2,
        )
        f.write("\n")
    print("wrote %d bundles" % len(rows))


main()
