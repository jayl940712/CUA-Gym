#!/usr/bin/env python3
"""Batch-6 lane 37 generator — shopping, R2 -> A4 (cancelled-month reorder).

Writes ten medium bundles under output/tasks/shopping/<task_id>/, plus the
lane GENERATION.md and replay drafts under
output/tasks/shopping/_batches/cancelled_month_reorder/.

Ground truth is computed here by replaying AppContext.jsx's `reorder`
(:598-635) over the mock's own seed (src/data/orders.json, products.json,
productOptions.json, cart.json), so every expected cart line is derived from
the handler, not guessed.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
DATA = os.path.join(ROOT, "hub/websites/webarena_shopping_mock/src/data")
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/cancelled_month_reorder")

ORDERS = {o["entityId"]: o for o in json.load(open(os.path.join(DATA, "orders.json")))}
PRODUCTS = {p["id"]: p for p in json.load(open(os.path.join(DATA, "products.json")))}
POPTS = json.load(open(os.path.join(DATA, "productOptions.json")))
CART = json.load(open(os.path.join(DATA, "cart.json")))


def final_price(p):
    return p["specialPrice"] if p.get("specialPrice") is not None else p["price"]


def get_options(pid):
    groups = POPTS.get(str(pid), [])
    return sorted(groups, key=lambda g: (g["sortOrder"], g["title"], g["optionId"]))


def sort_line_options(options, pid):
    if len(options) < 2:
        return options
    if not all(isinstance(o["optionId"], int) for o in options):
        return options
    so = {g["optionId"]: g.get("sortOrder", 0) for g in get_options(pid)}
    return sorted(options, key=lambda o: (so.get(o["optionId"], 0), o["optionId"]))


def reorder(order, cart_items):
    """Faithful replay of AppContext.jsx:598 reorder()."""
    items = [dict(i) for i in cart_items]
    for line in order["items"]:
        product = PRODUCTS.get(line["productId"])
        groups = get_options(line["productId"])
        options = []
        for o in line.get("options", []):
            grp = next((g for g in groups if g["title"] == o["label"]), None)
            val = None
            if grp:
                val = next((v for v in grp["values"] if v["title"] == o["value"]), None)
            options.append({
                "optionId": grp["optionId"] if grp else None,
                "optionTypeId": val["optionTypeId"] if val else None,
                "label": o["label"],
                "value": o["value"],
            })
        srt = sort_line_options(options, line["productId"])
        key = sorted([o["optionTypeId"] for o in srt], key=lambda x: (x is None, x))
        found = -1
        for idx, i in enumerate(items):
            k2 = sorted([o.get("optionTypeId") for o in i.get("options", [])],
                        key=lambda x: (x is None, x))
            if i["productId"] == line["productId"] and k2 == key:
                found = idx
                break
        if found >= 0:
            items[found] = dict(items[found])
            items[found]["qty"] = items[found]["qty"] + line["qtyOrdered"]
        else:
            items.append({
                "productId": line["productId"],
                "sku": line["sku"],
                "name": line["name"],
                "price": final_price(product) if product else line["price"],
                "qty": line["qtyOrdered"],
                "options": srt,
            })
    return items


def canon(items):
    """(productId, qty, ((label, value), ...)) sorted — the reward's shape."""
    out = []
    for i in items:
        pairs = tuple(sorted((o["label"], o["value"]) for o in i.get("options", [])))
        out.append((int(i["productId"]), int(i["qty"]), pairs))
    out.sort()
    return out


# --------------------------------------------------------------------------
# The injected lamp line for task 004: exactly what addToCart would have
# written for product 33239 with Color = Industrial Bronze.
LAMP_LINE = {
    "itemId": 557,
    "productId": 33239,
    "sku": "B072XS3F6W",
    "name": PRODUCTS[33239]["name"],
    "price": 169.99,
    "qty": 1,
    "options": [{"optionId": 25181, "optionTypeId": 160860,
                 "label": "Color", "value": "Industrial Bronze"}],
}

SEED_CART = CART["items"]

CUSTOMER_ADDR_ORDERS = None

# --------------------------------------------------------------------------
# Ten task specs. Every one is R2 -> A4: derive WHICH order was cancelled in a
# stated window, then reorder it.

TASKS = [
    {
        "id": "cancelled_month_reorder_june2022_makeup_kit_001",
        "target": 182,
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "In June 2022 I cancelled an order and I have changed my mind about it. "
            "Find that cancelled order in my order history and put everything it "
            "contained back into my shopping cart."
        ),
        "window": "June 2022",
        "flip": None,
        "cart_inject": None,
        "derived_from": "reorder_cancelled_item_nail_dryer_checkout_007",
        "notes": [
            "June 2022 holds exactly one order in the seed, 000000182 (2022-06-30 23:09:02 UTC), "
            "and it is cancelled - so the month alone resolves the target with no product hint. "
            "The batch-5 neighbour reached the same order through a product description (R6) and "
            "then checked out (A10); this is the two-skill temporal core with a different rubric.",
            "23:09:02 UTC renders 6/30/22 in America/New_York (format.js:4), inside the stated month.",
        ],
    },
    {
        "id": "cancelled_month_reorder_may2022_bed_frame_002",
        "target": 181,
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "I cancelled my one and only May 2022 order. Dig it out of my order "
            "history and get every item that was on it back into my shopping cart."
        ),
        "window": "May 2022",
        "flip": 181,
        "cart_inject": None,
        "derived_from": None,
        "notes": [
            "May 2022 has exactly one order in the seed (000000181) and it is COMPLETE, so the "
            "pristine month has no answer. initial_setup.py flips it to canceled/canceled, which "
            "makes the window resolvable and gives the family an answer the seed cannot memorise.",
        ],
    },
    {
        "id": "cancelled_month_reorder_aug2022_tunic_top_003",
        "target": 172,
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "Three of my orders were placed in August 2022 and I cancelled one of "
            "them. Restore the full contents of that cancelled order into my "
            "shopping cart."
        ),
        "window": "August 2022",
        "flip": None,
        "cart_inject": None,
        "derived_from": "reorder_cancelled_item_summer2022_care_package_008",
        "notes": [
            "August 2022 holds 000000165, 000000155 (both complete) and 000000172 (canceled), so "
            "the status read is what discriminates - an agent that takes the first August row gets "
            "000000165 and scores 0.0.",
        ],
    },
    {
        "id": "cancelled_month_reorder_feb2023_first_half_merge_004",
        "target": 158,
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "I cancelled an order in the first half of February 2023, before the "
            "15th. Put everything that was on that order back into my shopping cart."
        ),
        "window": "1-14 February 2023",
        "flip": None,
        "cart_inject": LAMP_LINE,
        "derived_from": "reorder_cancelled_item_feb2023_lamp_colour_swap_004",
        "notes": [
            "February 2023 has TWO cancellations - 000000158 (2/11) and 000000156 (2/24) - so the "
            "half-month window is what picks the target; a 13-day margin, and neither order is one "
            "of the five that render a day early (185/154/163/166/170).",
            "initial_setup.py plants one unit of the same lamp (product 33239, Color = Industrial "
            "Bronze, optionTypeId 160860) in the cart, so reorder takes the MERGE branch "
            "(AppContext.jsx:614-616) and the correct end state is that line at qty 2, not a fourth "
            "cart row. The injection cannot pre-satisfy the rubric: it writes qty 1, the rubric "
            "wants qty 2.",
        ],
    },
    {
        "id": "cancelled_month_reorder_feb2023_late_foundation_005",
        "target": 156,
        "style": "explicit",
        "shape": "mutation",
        "instruction": (
            "I cancelled two separate orders in February 2023. The one I want back "
            "is the later of the two - it was cancelled after the 20th of the month, "
            "not the one from earlier in February. Open my account's order history, "
            "identify that later cancelled order by its date, and use its Reorder "
            "action so that everything it contained is added to my shopping cart on "
            "top of the three items already sitting there. Do not place the order or "
            "go through checkout - stopping at the cart is enough."
        ),
        "window": "20-28 February 2023",
        "flip": None,
        "cart_inject": None,
        "derived_from": "reorder_cancelled_item_feb2023_box_spring_003",
        "notes": [
            "000000156 renders 2/24/23 and 000000158 renders 2/11/23, so 'after the 20th' has a "
            "13-day margin. The batch-5 neighbour named the product (R6); this one is purely "
            "temporal and stops at the cart.",
        ],
    },
    {
        "id": "cancelled_month_reorder_sep2022_wall_art_006",
        "target": 175,
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "One of my two September 2022 orders ended up cancelled. Work out which "
            "one that was and put every item from it back into my shopping cart."
        ),
        "window": "September 2022",
        "flip": 175,
        "cart_inject": None,
        "derived_from": None,
        "notes": [
            "September 2022 holds 000000175 (9/1) and 000000179 (9/29), both complete in the seed. "
            "initial_setup.py cancels 000000175, so the month has exactly one cancellation and the "
            "second order is a live distractor that satisfies the date filter but not the status.",
            "000000179 is the larger order ($2,890.53), so an agent that grabs the more memorable "
            "September row scores 0.0.",
        ],
    },
    {
        "id": "cancelled_month_reorder_nov2022_olive_oil_007",
        "target": 183,
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "November 2022 has three orders on my account and one of them was "
            "cancelled. Get the contents of that cancelled order back into my "
            "shopping cart."
        ),
        "window": "November 2022",
        "flip": 183,
        "cart_inject": None,
        "derived_from": None,
        "notes": [
            "November 2022 holds 000000183 (11/11), 000000171 (11/20) and 000000164 (11/26), all "
            "complete in the seed. initial_setup.py cancels 000000183, leaving two same-month "
            "distractors and a unique answer.",
        ],
    },
    {
        "id": "cancelled_month_reorder_jan2023_topiary_008",
        "target": 148,
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "I placed two orders in January 2023 and cancelled one of them. Find the "
            "cancelled one and put both of the products it listed back into my "
            "shopping cart."
        ),
        "window": "January 2023",
        "flip": 148,
        "cart_inject": None,
        "derived_from": None,
        "notes": [
            "January 2023 holds 000000163 (1/17, four lines) and 000000148 (1/29, two lines), both "
            "complete in the seed; initial_setup.py cancels 000000148. The instruction's 'two "
            "products' is a property of the answer the agent can confirm, not a way to find it - "
            "the status still has to be read, since 000000163 has four lines.",
            "000000163 is one of the five orders that render a day early (1/17 -> 1/16/23), which "
            "is harmless here: the month bucket is unaffected.",
        ],
    },
    {
        "id": "cancelled_month_reorder_mar2023_phone_case_009",
        "target": 180,
        "style": "explicit",
        "shape": "mutation",
        "instruction": (
            "There are two orders on my account from March 2023 and exactly one of "
            "them carries the Canceled status. Go to My Orders in my account, read "
            "the status column to work out which March 2023 order was cancelled, and "
            "use that order's Reorder action so all five of its line items are added "
            "to my shopping cart alongside the three items already in it. Keep the "
            "options each line was ordered with, and stop at the cart rather than "
            "placing a new order."
        ),
        "window": "March 2023",
        "flip": 180,
        "cart_inject": None,
        "derived_from": None,
        "notes": [
            "March 2023 holds 000000166 and 000000180, both complete in the seed and both stored on "
            "2023-03-11; initial_setup.py cancels 000000180. 000000166 renders 3/10/23 because of "
            "the America/New_York shift, so the two rows are not even same-day on screen - but the "
            "task keys on status, not day, which is the safe axis.",
        ],
    },
    {
        "id": "cancelled_month_reorder_apr2022_peanut_puffs_010",
        "target": 168,
        "style": "explicit",
        "shape": "retrieval_writeback",
        "instruction": (
            "Back in April 2022 I placed two orders and later cancelled one of them; "
            "the other one went through fine. Open my order history, find the April "
            "2022 order whose status is Canceled, and reorder it so its item joins "
            "the three products already in my shopping cart. The April 2022 orders "
            "are not on the first page of the history grid, so page through or raise "
            "the rows-per-page first. Leave the cart there - no checkout."
        ),
        "window": "April 2022",
        "flip": 168,
        "cart_inject": None,
        "derived_from": "reorder_cancelled_item_april2023_injected_checkout_009",
        "notes": [
            "April 2022 holds 000000159 (4/5) and 000000168 (4/27), both complete in the seed - the "
            "month is one of the two the census flags as having no cancellation. initial_setup.py "
            "cancels 000000168, so the window resolves to a single order and 000000159 is a live "
            "same-month distractor.",
            "The batch-5 neighbour injected two whole new April 2023 rows and required checkout; "
            "this flips an existing April 2022 row and stops at the cart.",
        ],
    },
]

ANALOGUES = [
    "I previously ordered a mattress foundation around Feb or March 2023 and later cancelled. Can you reorder it for me? Complete the checkout process.",
    "I previously ordered a table lamp in May 2023 and later cancelled. Can you reorder it for me? Complete the checkout process.",
    "I previously ordered a TV stand sometime around sep 2022 and later cancelled. Can you reorder it for me? Complete the checkout process.",
    "I previously ordered a cat t-shirt during 2022 and later cancelled. Can you reorder it for me? Complete the checkout process.",
    "I previously ordered a make up removal kit during summer 2022 and later cancelled. Can you reorder it for me? Complete the checkout process.",
]
INSPIRATION_IDS = ["webarena-436", "webarena-437", "webarena-438", "webarena-439", "webarena-440"]


# --------------------------------------------------------------------------
# Reward source templates.

REWARD_HELPERS = '''
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


def _opts(raw):
    """Sorted (label, value) pairs for one cart line, or None if malformed."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return None
    pairs = []
    for option in raw:
        if not isinstance(option, dict):
            return None
        label = _text(option.get("label"))
        value = _text(option.get("value"))
        if label is None or value is None:
            return None
        pairs.append((label, value))
    pairs.sort()
    return tuple(pairs)


def _cart_lines(state):
    """[(productId, qty, ((label, value), ...)), ...] sorted, or None."""
    if not isinstance(state, dict):
        return None
    cart = state.get("cart")
    if not isinstance(cart, dict):
        return None
    items = cart.get("items")
    if not isinstance(items, list):
        return None
    lines = []
    for item in items:
        if not isinstance(item, dict):
            return None
        product_id = _int(item.get("productId"))
        qty = _int(item.get("qty"))
        options = _opts(item.get("options"))
        if product_id is None or qty is None or options is None:
            return None
        lines.append((product_id, qty, options))
    lines.sort()
    return lines


COMPONENT_WEIGHTS = {
    "reordered_lines_present": 0.5,
    "cart_is_exactly_expected": 0.5,
}


def _checks(state):
    lines = _cart_lines(state)
    if lines is None:
        return {"reordered_lines_present": False, "cart_is_exactly_expected": False}
    present = True
    for line in NEW_LINES:
        if line not in lines:
            present = False
    exact = sorted(lines) == sorted(EXPECTED_CART)
    return {
        "reordered_lines_present": bool(present),
        "cart_is_exactly_expected": bool(exact),
    }
'''


def reward_py(spec, expected, new_lines, criteria):
    doc = "\n".join("  * " + c for c in criteria)
    return (
        '"""Deterministic reward for %s.\n\n'
        'Success criteria:\n%s\n\n'
        'Only user-visible persisted state is inspected, and only `current_state`:\n'
        'the end state is asserted positively against constants derived by replaying\n'
        "the mock's own reorder handler over its seed, never diffed against\n"
        '`initial_state`.\n'
        '"""\n'
        '%s\n'
        'NEW_LINES = %r\n\n'
        'EXPECTED_CART = %r\n\n\n'
        'def _state(evidence):\n'
        '    apps = evidence.get("apps") if isinstance(evidence, dict) else None\n'
        '    if isinstance(apps, dict):\n'
        '        for app in apps.values():\n'
        '            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):\n'
        '                return app["current_state"]\n'
        '    return {}\n\n\n'
        'def evaluate(evidence):\n'
        '    state = _state(evidence)\n'
        '    checks = _checks(state)\n'
        '    components = []\n'
        '    for name in COMPONENT_WEIGHTS:\n'
        '        ok = bool(checks.get(name))\n'
        '        components.append({\n'
        '            "name": name,\n'
        '            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,\n'
        '            "details": {"satisfied": ok},\n'
        '        })\n'
        '    total = 0.0\n'
        '    for component in components:\n'
        '        total += component["score"]\n'
        '    return {"score": round(total, 6), "components": components}\n'
        % (spec["id"], doc, REWARD_HELPERS, new_lines, expected)
    )


def nemo_reward_py(spec, expected, new_lines, criteria):
    doc = "\n".join("  * " + c for c in criteria)
    return (
        '"""NeMo-Gym reward program for %s.\n\n'
        'Implements exactly the rubric of reward.py:\n%s\n\n'
        'Reads `current_state` from GET /go?sid=... instead of a frozen evidence\n'
        'bundle and prints REWARD: <float> on every output path, including errors.\n'
        'Self-contained: standard library plus requests.\n'
        '"""\n\n'
        'import sys\n\n'
        'import requests\n\n'
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n'
        '%s\n'
        'NEW_LINES = %r\n\n'
        'EXPECTED_CART = %r\n\n\n'
        'def score_state(state):\n'
        '    checks = _checks(state)\n'
        '    total = 0.0\n'
        '    for name in COMPONENT_WEIGHTS:\n'
        '        if checks.get(name):\n'
        '            total += COMPONENT_WEIGHTS[name]\n'
        '    return round(total, 6)\n\n\n'
        'def main():\n'
        '    try:\n'
        '        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        '        response.raise_for_status()\n'
        '        payload = response.json()\n'
        '        state = payload.get("current_state")\n'
        '        if not isinstance(state, dict):\n'
        '            state = {}\n'
        '    except Exception as exc:\n'
        '        print("reward read failed: %%s" %% exc, file=sys.stderr)\n'
        '        print("REWARD: 0.0")\n'
        '        return\n'
        '    try:\n'
        '        value = score_state(state)\n'
        '    except Exception as exc:\n'
        '        print("reward scoring failed: %%s" %% exc, file=sys.stderr)\n'
        '        print("REWARD: 0.0")\n'
        '        return\n'
        '    print("REWARD: %%s" %% value)\n\n\n'
        'main()\n'
        % (spec["id"], doc, REWARD_HELPERS, new_lines, expected)
    )


SETUP_HEAD = '''"""NeMo-Gym setup program for {tid}.

{why}

Written as a read-modify-write: GET /go, mutate the WHOLE state document, POST
it back with {{"action": "set", ...}}. That is correct whether the mock's state
API replaces or shallow-merges, and it is what /go returns to the reward.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

'''


def setup_py(spec):
    flip = spec["flip"]
    inject = spec["cart_inject"]
    if flip is None and inject is None:
        return None
    parts = [SETUP_HEAD.format(tid=spec["id"], why=spec["setup_why"])]
    if flip is not None:
        parts.append("CANCEL_ENTITY_ID = %d\n" % flip)
    if inject is not None:
        parts.append(
            "# Exactly the line shape addToCart writes (AppContext.jsx:266-274).\n"
            "INJECTED_CART_LINE = json.loads(r\"\"\"\n%s\n\"\"\")\n\n"
            "NEXT_CART_ITEM_ID = %d\n"
            % (json.dumps(inject, indent=1), inject["itemId"] + 1)
        )
    body = '''

def read_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: /go returned neither current_state nor initial_state",
              file=sys.stderr)
        raise SystemExit(1)
    return state


def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    state = read_state()
'''
    if flip is not None:
        body += '''    orders = state.get("orders")
    if not isinstance(orders, list):
        print("SETUP FAILED: state carries no orders list", file=sys.stderr)
        raise SystemExit(1)
    hits = 0
    for order in orders:
        if isinstance(order, dict) and order.get("entityId") == CANCEL_ENTITY_ID:
            order["status"] = "canceled"
            order["state"] = "canceled"
            hits += 1
    if hits != 1:
        print("SETUP FAILED: expected exactly one order to cancel, saw %s" % hits,
              file=sys.stderr)
        raise SystemExit(1)
'''
    if inject is not None:
        body += '''    cart = state.get("cart")
    if not isinstance(cart, dict) or not isinstance(cart.get("items"), list):
        print("SETUP FAILED: state carries no cart.items list", file=sys.stderr)
        raise SystemExit(1)
    items = [i for i in cart["items"]
             if not (isinstance(i, dict) and i.get("itemId") == INJECTED_CART_LINE["itemId"])]
    items.append(json.loads(json.dumps(INJECTED_CART_LINE)))
    cart["items"] = items
    state["cart"] = cart
    state["nextCartItemId"] = NEXT_CART_ITEM_ID
'''
    body += '''    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()
    verify()


main()
'''
    parts.append(body)
    return "".join(parts)


REPLAY = '''"""Golden replay draft for {tid}.

Clicks only: landing page -> My Account (header) -> My Orders (account nav) ->
{limiter}find the {window} row whose Status reads "Canceled" -> its Reorder
action. No typed URLs after the initial landing.
"""

import os

from playwright.sync_api import sync_playwright

BASE = os.environ["CUA_GYM_WEBARENA_SHOPPING_URL"]
SID = os.environ["CUA_GYM_SID"]
TARGET_INCREMENT = "{increment}"


def run(page):
    page.goto(BASE + "/?sid=" + SID)
    page.get_by_role("link", name="My Account").first.click()
    page.get_by_role("link", name="My Orders").first.click()
{limiter_code}    row = page.locator("#my-orders-table tbody tr", has_text=TARGET_INCREMENT).first
    row.wait_for()
    assert "Canceled" in row.inner_text()
    row.get_by_role("link", name="Reorder").click()
    page.wait_for_url("**/checkout/cart/**")


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    run(page)
    browser.close()
'''

LIMITER_CODE = ('    page.select_option("#order-limiter", "50")\n'
                '    page.wait_for_timeout(500)\n')

PAGE1 = {170, 189, 188, 187, 180, 166, 161, 156, 158, 157}


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    summary = []
    for spec in TASKS:
        order = json.loads(json.dumps(ORDERS[spec["target"]]))
        cart_items = [dict(i) for i in SEED_CART]
        if spec["cart_inject"]:
            cart_items.append(dict(spec["cart_inject"]))
        expected = canon(reorder(order, cart_items))
        before = canon(cart_items)
        new_lines = [line for line in expected if line not in before]
        assert new_lines, spec["id"]
        assert expected != before, spec["id"]

        criteria = [
            "state.cart.items is exactly the %d lines listed in EXPECTED_CART: "
            "each (productId, qty, sorted option label/value pairs) and nothing else."
            % len(expected),
            "Those lines include %s, which is what reordering cancelled order %s "
            "adds to the pre-existing cart."
            % (", ".join("product %d at qty %d" % (p, q) for p, q, _ in new_lines),
               order["incrementId"]),
        ]

        spec["setup_why"] = " ".join(spec["notes"])
        d = os.path.join(OUT, spec["id"])
        os.makedirs(d, exist_ok=True)

        with open(os.path.join(d, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": spec["id"],
                "task_instruction": spec["instruction"],
                "app_dir": "webarena_shopping_mock",
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": criteria,
            }, fh, indent=2)
            fh.write("\n")

        setup = setup_py(spec)
        if setup:
            with open(os.path.join(d, "initial_setup.py"), "w") as fh:
                fh.write(setup)

        injected = []
        if spec["flip"] is not None:
            injected.append(
                "orders[entityId=%d] status/state flipped complete -> canceled, so the "
                "%s window has exactly one cancellation and the retrieval has a unique "
                "answer that the pristine seed does not contain."
                % (spec["flip"], spec["window"]))
        if spec["cart_inject"] is not None:
            injected.append(
                "cart.items gains one unit of product %d (Color = Industrial Bronze, "
                "optionTypeId 160860) and nextCartItemId becomes %d, so reorder takes the "
                "merge branch and the correct end state is that line at qty 2."
                % (spec["cart_inject"]["productId"], spec["cart_inject"]["itemId"] + 1))

        manifest = {
            "schema_version": 2,
            "task_id": spec["id"],
            "instruction": spec["instruction"],
            "apps": [{
                "name": "webarena_shopping_mock",
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                "start_path": "/",
                "initial_state": None,
                "golden_state": None,
            }],
            "reward_path": "reward.py",
            "requirements_path": None,
            "evidence": [],
            "source_evaluator": {},
            "source": "webarena",
            "metadata": {
                "style": spec["style"],
                "difficulty": "medium",
                "shape": spec["shape"],
                "skills": ["R2", "A4"],
                "skill_chain": (
                    "find the order cancelled in %s from the order history -> "
                    "reorder it into the shopping cart" % spec["window"]),
                "derived_from": spec["derived_from"],
                "official_analogues": ANALOGUES[:2],
                "injected_preconditions": injected,
                "topic": "shopping storefront: reorder the order cancelled in a stated window",
                "inspiration_ids": INSPIRATION_IDS,
                "authoring_notes": spec["notes"] + [
                    "Ground truth computed by replaying AppContext.jsx:598 reorder() over "
                    "orders.json/products.json/productOptions.json/cart.json; every line of "
                    "order %s resolves in the catalog, so no line falls back to line.price."
                    % order["incrementId"],
                ],
            },
        }
        if setup:
            manifest["initial_setup_path"] = "initial_setup.py"
        with open(os.path.join(d, "task.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
            fh.write("\n")

        rw = reward_py(spec, expected, new_lines, criteria)
        with open(os.path.join(d, "reward.py"), "w") as fh:
            fh.write(rw)
        nrw = nemo_reward_py(spec, expected, new_lines, criteria)
        with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
            fh.write(nrw)

        row = {"task_payload": {
            "task_id": spec["id"],
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
                "bundle_id": spec["id"],
                "app_dir": "webarena_shopping_mock",
                "initial_setup": setup,
                "eval_reward_code": nrw,
            },
        }}
        with open(os.path.join(d, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")

        needs_limiter = spec["target"] not in PAGE1
        with open(os.path.join(BATCH, "replays", spec["id"] + ".py"), "w") as fh:
            fh.write(REPLAY.format(
                tid=spec["id"],
                increment=order["incrementId"],
                window=spec["window"],
                limiter=("raise rows-per-page to 50 -> " if needs_limiter else ""),
                limiter_code=(LIMITER_CODE if needs_limiter else ""),
            ))

        summary.append({
            "task_id": spec["id"],
            "order": order["incrementId"],
            "window": spec["window"],
            "style": spec["style"],
            "shape": spec["shape"],
            "setup": bool(setup),
            "expected": expected,
            "new_lines": new_lines,
            "words": len(spec["instruction"].split()),
        })

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({
            "schema_version": 2,
            "tasks": [{"task_id": s["task_id"], "path": s["task_id"] + "/task.json"}
                      for s in summary],
        }, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for s in summary:
            row = json.load(open(os.path.join(OUT, s["task_id"], "nemo_task.json")))
            fh.write(json.dumps(row) + "\n")

    with open(os.path.join(BATCH, "expected_carts.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    for s in summary:
        print(s["task_id"], s["order"], s["style"], s["shape"],
              "setup" if s["setup"] else "-", s["words"], "words")
        print("   expected:", s["expected"])


main()
