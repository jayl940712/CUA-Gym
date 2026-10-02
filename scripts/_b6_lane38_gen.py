#!/usr/bin/env python3
"""Batch-6 lane 38 generator: shopping, R2 -> A10.

Writes 10 bundles under output/tasks/shopping/<task_id>/ plus the lane's
GENERATION.md and replay drafts. Reads the mock's seed data to resolve real
product ids, skus, names and catalog final prices.
"""
import json
import os
import textwrap

ROOT = "/home/ubuntu/CUA-Gym"
MOCK = os.path.join(ROOT, "hub/websites/webarena_shopping_mock")
OUT = os.path.join(ROOT, "output/tasks/shopping")
LANE = "window_order_reorder_checkout"
BATCH = os.path.join(OUT, "_batches", LANE)

PRODUCTS = {p["id"]: p for p in json.load(open(os.path.join(MOCK, "src/data/products.json")))}
SEED_ORDERS = json.load(open(os.path.join(MOCK, "src/data/orders.json")))
SEED_CART = json.load(open(os.path.join(MOCK, "src/data/cart.json")))

ADDRESS = {
    "firstname": "Emma", "lastname": "Lopez", "street": "101 S San Mateo Dr",
    "city": "San Mateo", "region": "California", "postcode": "94010",
    "country_id": "US", "telephone": "6505551212", "company": None, "email": None,
}

# Cart boots with 3 lines, one of which (10617) carries options.
BASE_CART = {15033: 1, 15787: 1, 10617: 1}

PLACED_ENTITY_ID = 200
PLACED_INCREMENT_ID = "000000200"


def final_price(pid):
    p = PRODUCTS[pid]
    return p["specialPrice"] if p.get("specialPrice") is not None else p["price"]


def line(item_id, pid, qty):
    p = PRODUCTS[pid]
    price = final_price(pid)
    return {
        "itemId": item_id,
        "productId": pid,
        "sku": p["sku"],
        "name": p["name"],
        "price": price,
        "qtyOrdered": qty,
        "rowTotal": round(price * qty, 2),
        "productType": "simple",
        "options": [],
    }


def order(entity_id, created, status, state, lines):
    subtotal = round(sum(l["rowTotal"] for l in lines), 2)
    qty = sum(l["qtyOrdered"] for l in lines)
    shipping = 5 * qty
    return {
        "entityId": entity_id,
        "incrementId": str(entity_id).zfill(9),
        "status": status,
        "state": state,
        "createdAt": created + " 12:00:00",
        "grandTotal": round(subtotal + shipping, 2),
        "subtotal": subtotal,
        "shippingAmount": shipping,
        "taxAmount": 0,
        "discountAmount": 0,
        "totalQtyOrdered": qty,
        "shippingDescription": "Flat Rate - Fixed",
        "customerEmail": "emma.lopez@gmail.com",
        "shippingMethod": "flatrate_flatrate",
        "paymentMethod": "checkmo",
        "paymentTitle": "Check / Money order",
        "billingAddress": dict(ADDRESS),
        "shippingAddress": dict(ADDRESS),
        "items": lines,
    }


# ---------------------------------------------------------------- lane spec

# each injected spec: (entityId, date, status, state, [(productId, qty), ...], role)
TASKS = [
    dict(
        n="001", slug="last3days_cancelled", style="terse", today="6/12/2023",
        window="the last three days (2023-06-09 .. 2023-06-12)",
        instruction=("Today is 6/12/2023. One of the orders I placed in the last three days "
                     "was cancelled. Reorder it and complete the checkout."),
        inject=[
            (190, "2023-06-11", "complete", "complete", [(17822, 1)], "in-window, wrong status"),
            (191, "2023-06-10", "canceled", "canceled", [(5537, 1), (56052, 2)], "TARGET"),
            (192, "2023-06-06", "canceled", "canceled", [(21777, 1)], "right status, six days back - outside"),
        ],
        target=191,
        chain="R2 read the order grid dates and resolve 'the last three days' relative to 6/12/2023 -> A10 reorder that order and place it through checkout",
    ),
    dict(
        n="002", slug="two_weeks_cancelled", style="terse", today="6/20/2023",
        window="the past two weeks (2023-06-06 .. 2023-06-20)",
        instruction=("Today is 6/20/2023. Exactly one order from the past two weeks was "
                     "cancelled. Please reorder it and complete the checkout."),
        inject=[
            (190, "2023-06-16", "complete", "complete", [(28527, 1)], "in-window, wrong status"),
            (191, "2023-06-09", "canceled", "canceled", [(34883, 2), (39763, 1)], "TARGET"),
            (192, "2023-06-02", "canceled", "canceled", [(44056, 1)], "right status, 18 days back - outside"),
        ],
        target=191,
        chain="R2 resolve 'the past two weeks' against 6/20/2023 over the order grid -> A10 reorder the one cancelled row and place the order",
    ),
    dict(
        n="003", slug="past_month_fulfilled", style="terse", today="6/12/2023",
        window="the past month (2023-05-12 .. 2023-06-12)",
        instruction=("Today is 6/12/2023. I have one fulfilled order from the past month. "
                     "Reorder it for me and complete the checkout."),
        inject=[
            (190, "2023-05-25", "complete", "complete", [(15787, 1), (47308, 2)], "TARGET - line 15787 merges with a seeded cart line"),
            (191, "2023-06-05", "canceled", "canceled", [(48459, 1)], "in-window, wrong status"),
            (192, "2023-05-06", "complete", "complete", [(48588, 1)], "right status, 37 days back - outside"),
        ],
        target=190,
        chain="R2 resolve 'the past month' against 6/12/2023 over the order grid -> A10 reorder the single Complete row and place the order",
    ),
    dict(
        n="004", slug="four_months_processing", style="explicit", today="6/12/2023",
        window="the past four months (2023-02-12 .. 2023-06-12)",
        instruction=("Today is 6/12/2023. Look through my order history for the past four "
                     "months and find the single order that is still Processing. Reorder "
                     "that order, then go through checkout and place the order."),
        inject=[
            (190, "2023-06-05", "processing", "processing", [(37460, 1), (40070, 2)], "TARGET"),
            (191, "2023-06-08", "complete", "complete", [(41049, 1)], "in-window, wrong status"),
            (192, "2023-02-03", "processing", "processing", [(43531, 1)], "right status, four months and nine days back - outside"),
        ],
        target=190,
        chain="R2 resolve 'the past four months' against 6/12/2023 over the order grid -> A10 reorder the single Processing row and place the order",
    ),
    dict(
        n="005", slug="ten_days_on_hold", style="terse", today="6/15/2023",
        window="the last ten days (2023-06-05 .. 2023-06-15)",
        instruction=("Today is 6/15/2023. One order I placed in the last ten days is on "
                     "hold. Reorder it and complete the checkout."),
        inject=[
            (190, "2023-06-06", "On Hold", "holded", [(70964, 1), (77389, 3)], "TARGET"),
            (191, "2023-06-12", "complete", "complete", [(77846, 1)], "in-window, wrong status"),
            (192, "2023-06-01", "On Hold", "holded", [(78245, 1)], "right status, fourteen days back - outside"),
        ],
        target=190,
        chain="R2 resolve 'the last ten days' against 6/15/2023 over the order grid -> A10 reorder the single On Hold row and place the order",
    ),
    dict(
        n="006", slug="this_month_cancelled", style="terse", today="6/26/2023",
        window="earlier this month (2023-06-01 .. 2023-06-26)",
        instruction=("Today is 6/26/2023. Reorder the only order I placed earlier this "
                     "month that was cancelled, and complete the checkout."),
        inject=[
            (190, "2023-06-18", "canceled", "canceled", [(79869, 2), (87064, 1)], "TARGET"),
            (191, "2023-06-22", "complete", "complete", [(88837, 1)], "in-window, wrong status"),
            (192, "2023-05-29", "canceled", "canceled", [(91401, 1)], "right status, previous month - outside"),
        ],
        target=190,
        chain="R2 resolve 'earlier this month' against 6/26/2023 over the order grid -> A10 reorder the single cancelled June row and place the order",
    ),
    dict(
        n="007", slug="last_month_pending", style="explicit", today="7/3/2023",
        window="last month, i.e. all of June 2023",
        instruction=("Today is 7/3/2023. Exactly one of the orders I placed last month is "
                     "still pending. Open my order history, reorder that order, and then "
                     "complete the checkout so the new order is placed."),
        inject=[
            (190, "2023-06-14", "pending", "new", [(100492, 1), (101441, 2)], "TARGET"),
            (191, "2023-06-20", "complete", "complete", [(101771, 1)], "in-window, wrong status"),
            (192, "2023-07-01", "pending", "new", [(102028, 1)], "right status, THIS month - outside"),
        ],
        target=190,
        chain="R2 resolve 'last month' against 7/3/2023 over the order grid -> A10 reorder the single Pending June row and place the order",
    ),
    dict(
        n="008", slug="five_days_cancelled", style="terse", today="6/12/2023",
        window="the past five days (2023-06-07 .. 2023-06-12)",
        instruction=("Today is 6/12/2023. One of my orders from the past five days was "
                     "cancelled. Reorder it and complete the checkout."),
        inject=[
            (190, "2023-06-08", "canceled", "canceled", [(103562, 2), (2589, 1)], "TARGET"),
            (191, "2023-06-10", "complete", "complete", [(2345, 1)], "in-window, wrong status"),
            (192, "2023-06-03", "canceled", "canceled", [(4644, 1)], "right status, nine days back - outside"),
        ],
        target=190,
        chain="R2 resolve 'the past five days' against 6/12/2023 over the order grid -> A10 reorder the single cancelled row and place the order",
    ),
    dict(
        n="009", slug="two_months_ago_only", style="terse", today="6/12/2023",
        window="the calendar month two months before June 2023, i.e. April 2023",
        instruction=("Today is 6/12/2023. I placed exactly one order two months ago. "
                     "Reorder it and complete the checkout."),
        inject=[
            (190, "2023-04-14", "complete", "complete", [(5145, 1), (6556, 1)], "TARGET - the only April 2023 order in the whole history"),
            (191, "2023-05-14", "complete", "complete", [(11617, 2)], "one month ago, not two - off-by-one distractor"),
        ],
        target=190,
        chain="R2 count back two calendar months from 6/12/2023 and find the only order in that month -> A10 reorder it and place the order",
    ),
    dict(
        n="010", slug="two_months_fulfilled", style="explicit", today="6/26/2023",
        window="the past two months (2023-04-26 .. 2023-06-26)",
        instruction=("Today is 6/26/2023. Among my orders from the past two months there "
                     "is exactly one that has been fulfilled. Reorder that order and "
                     "complete the checkout to place it."),
        inject=[
            (190, "2023-06-10", "complete", "complete", [(12141, 1), (15919, 1)], "TARGET"),
            (191, "2023-04-20", "complete", "complete", [(19994, 1)], "right status, two months and six days back - outside"),
            (192, "2023-06-15", "canceled", "canceled", [(21217, 1)], "in-window, wrong status"),
        ],
        target=190,
        chain="R2 resolve 'the past two months' against 6/26/2023 over the order grid -> A10 reorder the single Complete row and place the order",
    ),
]

ANALOGUES_REORDER = [
    "I previously ordered a mattress foundation around Feb or March 2023 and later cancelled. Can you reorder it for me? Complete the checkout process.",
    "I previously ordered a make up removal kit during summer 2022 and later cancelled. Can you reorder it for me? Complete the checkout process.",
]
ANALOGUES_WINDOW = [
    "Today is 6/12/2023. Tell me how many fulfilled orders I have over the past month, and the total amount of money I spent.",
    "Today is 6/12/2023. Tell me how many fulfilled orders I have over the past four month, and the total amount of money I spent.",
]


def build(task):
    item_id = 900
    injected = []
    target_lines = None
    for eid, date, status, state, prods, role in task["inject"]:
        lines = []
        for pid, qty in prods:
            lines.append(line(item_id, pid, qty))
            item_id += 1
        o = order(eid, date, status, state, lines)
        injected.append(o)
        if eid == task["target"]:
            target_lines = prods
    assert target_lines is not None
    expected = dict(BASE_CART)
    for pid, qty in target_lines:
        expected[pid] = expected.get(pid, 0) + qty
    return injected, expected


SETUP_TMPL = '''"""NeMo-Gym setup program for {task_id}.

Injects the order-history precondition this task's relative date window reads.

The pristine shopping seed ends on 2023-05-18 and holds 37 orders, so every
window this lane states -- "the last three days", "the past month", "last
month" -- is empty or degenerate as seeded, and the retrieval has nothing to
resolve. This program appends {n_inject} orders so that the stated window
contains EXACTLY ONE order matching the stated status, with at least one
distractor that satisfies the status but falls outside the window and at least
one that falls inside the window with a different status.

Injected rows follow the seeded order convention exactly: entityId >= 190 with
both nextOrderEntityId and nextOrderIncrementId bumped to 200 so a later
placeOrder cannot mint a duplicate increment id; line itemIds >= 900 (the
seeded maximum is 544); createdAt pinned to 12:00:00 UTC so the store timezone
America/New_York (07:00 EST / 08:00 EDT) cannot shift the rendered day in
either direction; shippingAmount == 5 * totalQtyOrdered and grandTotal ==
subtotal + shippingAmount with tax and discount zero, which every seeded order
satisfies; every productId is a real catalog row and every price is that row's
catalog final price.

The injection writes only `orders`, `nextOrderEntityId` and
`nextOrderIncrementId`. It does not touch `cart`, and it creates no order with
entityId {placed_id}, so an untouched run after setup scores exactly 0.0.

Read-modify-write: the whole document is fetched from GET /go?sid=, patched in
place and republished with the "set" action, which is correct whether the mock
merges or replaces.

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

INJECTED_ORDERS = json.loads(r"""{injected_json}""")

NEXT_ORDER_ENTITY_ID = {placed_id}
NEXT_ORDER_INCREMENT_ID = {placed_id}


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    payload = probe.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("orders"), list):
        print("SETUP FAILED: no baseline document to patch", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
    existing = state["orders"]
    taken = set()
    for row in existing:
        if isinstance(row, dict):
            taken.add(row.get("entityId"))
    for row in INJECTED_ORDERS:
        if row["entityId"] in taken:
            print("SETUP FAILED: entityId %r already present" % (row["entityId"],), file=sys.stderr)
            raise SystemExit(1)

    state["orders"] = [json.loads(json.dumps(row)) for row in INJECTED_ORDERS] + list(existing)
    state["nextOrderEntityId"] = NEXT_ORDER_ENTITY_ID
    state["nextOrderIncrementId"] = NEXT_ORDER_INCREMENT_ID

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    after = check.json()
    current = after.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: /go returned no current_state", file=sys.stderr)
        raise SystemExit(1)
    ids = set()
    for row in current.get("orders") or []:
        if isinstance(row, dict):
            ids.add(row.get("entityId"))
    for row in INJECTED_ORDERS:
        if row["entityId"] not in ids:
            print("SETUP FAILED: injected order %r missing after set" % (row["entityId"],), file=sys.stderr)
            raise SystemExit(1)
    if current.get("nextOrderEntityId") != NEXT_ORDER_ENTITY_ID:
        print("SETUP FAILED: nextOrderEntityId not applied", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''

RUBRIC_TMPL = '''COMPONENT_WEIGHTS = {{
    'reordered_order_placed_with_exact_lines': 1.0,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

COMPONENT = 'reordered_order_placed_with_exact_lines'

# placeOrder (AppContext.jsx:513) mints the new order at prev.nextOrderEntityId,
# which initial_setup.py pinned to {placed_id}, and stringifies the same number
# into incrementId. It also empties the cart and stamps status/state
# pending/new.
EXPECTED_ENTITY_ID = {placed_id}
EXPECTED_INCREMENT_ID = '{placed_increment}'

# productId -> total ordered quantity on the placed order. The cart boots with
# three seeded lines ({base_cart_desc}), and `reorder`
# (AppContext.jsx:598) MERGES a reordered line into an existing cart line with
# the same product and the same chosen options rather than appending, so this
# map is the merged result, not a concatenation.
EXPECTED_LINES = json.loads(r"""{expected_json}""")

EXPECTED_TOTAL_QTY = {expected_qty}

# 37 seeded orders + {n_inject} injected by initial_setup.py + the one placed.
EXPECTED_ORDER_COUNT = {expected_order_count}


def _dict(value):
    return value if isinstance(value, dict) else {{}}


def _list(value):
    return value if isinstance(value, list) else []


def _num(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def score_state(state):
    """Score the single thing the episode had to make true.

    All-or-nothing on the resulting order record, so a run that reordered the
    wrong row (wrong item multiset), reordered twice (doubled quantities),
    stopped at the cart, or never touched the site all score exactly 0.0.
    Nothing is paid for leaving anything alone.
    """
    state = _dict(state)
    orders = [o for o in _list(state.get("orders")) if isinstance(o, dict)]

    placed = None
    for row in orders:
        if _num(row.get("entityId")) == EXPECTED_ENTITY_ID:
            placed = row
            break

    reasons = []
    ok = True
    if placed is None:
        ok = False
        reasons.append("no order with entityId %d" % EXPECTED_ENTITY_ID)
    else:
        if str(placed.get("incrementId")) != EXPECTED_INCREMENT_ID:
            ok = False
            reasons.append("incrementId %r != %r" % (placed.get("incrementId"), EXPECTED_INCREMENT_ID))
        if str(placed.get("status")) != "pending" or str(placed.get("state")) != "new":
            ok = False
            reasons.append("status/state %r/%r != 'pending'/'new'"
                           % (placed.get("status"), placed.get("state")))
        got = {{}}
        for item in _list(placed.get("items")):
            if not isinstance(item, dict):
                ok = False
                reasons.append("malformed order line")
                continue
            pid = _num(item.get("productId"))
            qty = _num(item.get("qtyOrdered"))
            if pid is None or qty is None:
                ok = False
                reasons.append("order line without productId/qtyOrdered")
                continue
            got[str(pid)] = got.get(str(pid), 0) + qty
        want = {{}}
        for key in EXPECTED_LINES:
            want[str(key)] = int(EXPECTED_LINES[key])
        if got != want:
            ok = False
            reasons.append("item multiset %r != %r" % (got, want))
        if _num(placed.get("totalQtyOrdered")) != EXPECTED_TOTAL_QTY:
            ok = False
            reasons.append("totalQtyOrdered %r != %d"
                           % (placed.get("totalQtyOrdered"), EXPECTED_TOTAL_QTY))

    if len(orders) != EXPECTED_ORDER_COUNT:
        ok = False
        reasons.append("orders holds %d rows, want %d" % (len(orders), EXPECTED_ORDER_COUNT))

    cart_items = _list(_dict(state.get("cart")).get("items"))
    if len(cart_items) != 0:
        ok = False
        reasons.append("cart still holds %d line(s)" % len(cart_items))

    return [{{
        "name": COMPONENT,
        "score": COMPONENT_WEIGHTS[COMPONENT] if ok else 0.0,
        "details": "ok" if ok else "; ".join(reasons),
    }}]


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
'''

REWARD_TMPL = '''"""
Deterministic reward for {task_id}.

Two skills (R2 -> A10), so this task is medium: one relative-date window over
the order-history grid feeding one lifecycle transition (reorder, then place
the order through checkout).

The window is {window}. Exactly one order in the
seeded-plus-injected history satisfies it together with the stated status; the
setup plants one same-status order OUTSIDE the window and one in-window order
with a different status, so an agent that skips the date arithmetic lands on a
different item set and scores exactly 0.0.

Reads current_state only.

Reads the frozen evidence bundle handed to evaluate().
"""

import json

{rubric}

def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    app = apps.get("shopping")
    if not isinstance(app, dict):
        app = apps.get("webarena_shopping_mock")
    if not isinstance(app, dict):
        for value in apps.values():
            if isinstance(value, dict) and "current_state" in value:
                app = value
                break
    state = _dict(_dict(app).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {{"score": _clamp(float(total)), "components": components}}
'''

NEMO_REWARD_TMPL = '''"""
Deterministic reward for {task_id}.

Two skills (R2 -> A10), so this task is medium: one relative-date window over
the order-history grid feeding one lifecycle transition (reorder, then place
the order through checkout).

The window is {window}. Exactly one order in the
seeded-plus-injected history satisfies it together with the stated status; the
setup plants one same-status order OUTSIDE the window and one in-window order
with a different status, so an agent that skips the date arithmetic lands on a
different item set and scores exactly 0.0.

Reads current_state only.

Reads GET /go?sid=... and prints REWARD: <float> on every output path.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

{rubric}

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {{}}
    except Exception as exc:
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''

REPLAY_TMPL = '''"""Golden replay DRAFT for {task_id}.

Click-only. The episode lands on `/` and every later page is reached by
clicking a rendered link or button. No page.goto() after the landing, no URL
construction.

Route:
    /  ->  header 'My Account'  ->  /customer/account/
       ->  account sidebar 'My Orders'  ->  /sales/order/history/
       ->  the 'Reorder' link on the row for order {target_increment}
           ({target_date}, {target_status})  ->  /checkout/cart/
       ->  'Proceed to Checkout'  ->  /checkout/
       ->  'Next' (shipping step)  ->  /checkout/#payment
       ->  'Place Order'  ->  /checkout/onepage/success/

Requires initial_setup.py: the seeded history ends 2023-05-18, so the stated
window is empty without the injected orders.

R2 -> A10 chain: {chain}

Derivation the replay hard-codes (the agent must derive it):
{derivation}
"""


def reorder_row(page, increment_id):
    """The order grid renders one <tr> per order with the increment id in
    td.col.id and a per-row Reorder link (OrderHistoryPage.jsx:66)."""
    row = 'table#my-orders-table tbody tr:has(td.col.id:text-is("%s"))' % increment_id
    page.wait_for_selector(row)
    page.click(row + ' >> a.action.order')


def run(page):
    page.click('header a:text-is("My Account")')
    page.wait_for_selector('.sidebar a:text-is("My Orders")')
    page.click('.sidebar a:text-is("My Orders")')
    page.wait_for_selector('table#my-orders-table')

    reorder_row(page, "{target_increment}")

    page.wait_for_selector('button[data-role="proceed-to-checkout"]')
    page.click('button[data-role="proceed-to-checkout"]')

    page.wait_for_selector('#shipping')
    page.click('#shipping button.action.primary.large.button')

    page.wait_for_selector('#payment button.action.primary.checkout')
    page.click('#payment button.action.primary.checkout')

    page.wait_for_url('**/checkout/onepage/success/**')
'''


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    rows = []
    summary = []

    for task in TASKS:
        task_id = "%s_%s_%s" % (LANE, task["slug"], task["n"])
        injected, expected = build(task)
        n_inject = len(injected)
        expected_qty = sum(expected.values())
        expected_order_count = len(SEED_ORDERS) + n_inject + 1
        target = [o for o in injected if o["entityId"] == task["target"]]
        target = target[0]

        bundle = os.path.join(OUT, task_id)
        os.makedirs(bundle, exist_ok=True)

        setup = SETUP_TMPL.format(
            task_id=task_id,
            n_inject=n_inject,
            placed_id=PLACED_ENTITY_ID,
            injected_json=json.dumps(injected, indent=1),
        )

        base_cart_desc = ", ".join(
            "%d x%d" % (pid, qty) for pid, qty in sorted(BASE_CART.items()))
        rubric = RUBRIC_TMPL.format(
            placed_id=PLACED_ENTITY_ID,
            placed_increment=PLACED_INCREMENT_ID,
            base_cart_desc=base_cart_desc,
            expected_json=json.dumps({str(k): v for k, v in sorted(expected.items())}, indent=1),
            expected_qty=expected_qty,
            n_inject=n_inject,
            expected_order_count=expected_order_count,
        )
        reward = REWARD_TMPL.format(task_id=task_id, window=task["window"], rubric=rubric)
        nemo_reward = NEMO_REWARD_TMPL.format(
            task_id=task_id, window=task["window"], rubric=rubric)

        derivation = "\n".join(
            "    %s (%s, %s): %s" % (o["incrementId"], o["createdAt"][:10], o["status"], role)
            for o, (_, _, _, _, _, role) in zip(injected, task["inject"]))

        replay = REPLAY_TMPL.format(
            task_id=task_id,
            target_increment=target["incrementId"],
            target_date=target["createdAt"][:10],
            target_status=target["status"],
            chain=task["chain"],
            derivation=derivation,
        )

        success = [
            ("current_state.orders holds exactly %d rows and one of them has entityId %d "
             "with incrementId \"%s\"." % (expected_order_count, PLACED_ENTITY_ID, PLACED_INCREMENT_ID)),
            ("That order's status/state is pending/new, its totalQtyOrdered is %d, and its "
             "items collapse to exactly the productId -> quantity map %s."
             % (expected_qty, json.dumps({str(k): v for k, v in sorted(expected.items())}))),
            "current_state.cart.items is empty.",
            ("An untouched run after initial_setup.py scores 0.0: the injection writes only "
             "orders, nextOrderEntityId and nextOrderIncrementId, and creates no order %d."
             % PLACED_ENTITY_ID),
            ("A run that reordered any other row in the history produces a different item "
             "multiset and scores 0.0."),
        ]

        task_instruction = {
            "task_id": task_id,
            "task_instruction": task["instruction"],
            "app_dir": "webarena_shopping_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success,
        }

        manifest = {
            "schema_version": 2,
            "task_id": task_id,
            "instruction": task["instruction"],
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
                "style": task["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R2", "A10"],
                "skill_chain": task["chain"],
                "derived_from": None,
                "official_analogues": ANALOGUES_REORDER + ANALOGUES_WINDOW,
                "injected_preconditions": [
                    ("orders[] gains %d rows dated %s, all pinned to 12:00:00 UTC so "
                     "America/New_York cannot shift the rendered day; entityIds %s, line "
                     "itemIds from 900. The pristine history ends 2023-05-18, so the stated "
                     "window '%s' is empty as seeded and the retrieval has nothing to resolve."
                     % (n_inject,
                        ", ".join(o["createdAt"][:10] for o in injected),
                        ", ".join(str(o["entityId"]) for o in injected),
                        task["window"])),
                    ("nextOrderEntityId and nextOrderIncrementId both set to %d, past every "
                     "injected entityId, so placeOrder cannot mint a duplicate increment id "
                     "and the placed order's identity is deterministic."
                     % PLACED_ENTITY_ID),
                    ("Distractors: %s. Nothing injected pre-satisfies the rubric -- cart is "
                     "left pristine and no order %d is created."
                     % ("; ".join("%s %s" % (o["incrementId"], role)
                                  for o, (_, _, _, _, _, role) in zip(injected, task["inject"])
                                  if role != "TARGET"),
                        PLACED_ENTITY_ID)),
                ],
                "hard_criteria": [],
                "topic": "shopping date-window an order in my history, then reorder it and check out",
                "lane": LANE,
                "batch": "batch6",
                "inspiration_ids": [
                    "webarena-47", "webarena-49", "webarena-50",
                    "webarena-436", "webarena-437", "webarena-438",
                    "webarena-439", "webarena-440",
                ],
                "authoring_notes": [
                    "Target: order %s, %s, status %r. Window: %s."
                    % (target["incrementId"], target["createdAt"][:10], target["status"], task["window"]),
                    "placeOrder (hub/websites/webarena_shopping_mock/src/context/AppContext.jsx:513) "
                    "is the terminal write: it pushes the new order onto orders[], empties "
                    "cart.items and bumps nextOrderEntityId/nextOrderIncrementId. The checkout "
                    "wizard's step state is React useState only; nothing before Place Order "
                    "persists, so the rubric asserts the placed record.",
                    "reorder (AppContext.jsx:598) merges a line into an existing cart line "
                    "keyed on productId plus the sorted optionTypeId list, so the expected "
                    "collection is the merged multiset, not a concatenation.",
                    "Shipping is $5.00 per item (utils/orders.js flatRateShipping) and "
                    "CheckoutPage.jsx:73 passes it through, so every injected row satisfies "
                    "shippingAmount == 5 * totalQtyOrdered like all 37 seeded rows.",
                    "Every injected productId is a real catalog row and the line price is that "
                    "row's finalPrice (catalog.js:416), so the order view and the PDP agree.",
                ],
            },
        }

        nemo = {
            "task_payload": {
                "task_id": task_id,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": ["webarena_shopping_mock"],
                "start_urls": [],
                "intent": task["instruction"],
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": task_id,
                    "app_dir": "webarena_shopping_mock",
                    "initial_setup": setup,
                    "eval_reward_code": nemo_reward,
                },
            }
        }

        open(os.path.join(bundle, "task_instruction.json"), "w").write(
            json.dumps(task_instruction, indent=2) + "\n")
        open(os.path.join(bundle, "task.json"), "w").write(json.dumps(manifest, indent=2) + "\n")
        open(os.path.join(bundle, "initial_setup.py"), "w").write(setup)
        open(os.path.join(bundle, "reward.py"), "w").write(reward)
        open(os.path.join(bundle, "nemo_reward.py"), "w").write(nemo_reward)
        open(os.path.join(bundle, "nemo_task.json"), "w").write(json.dumps(nemo, indent=2) + "\n")
        open(os.path.join(BATCH, "replays", task_id + ".py"), "w").write(replay)

        rows.append(nemo)
        summary.append(dict(
            task_id=task_id, style=task["style"], today=task["today"],
            window=task["window"], target=target["incrementId"],
            target_date=target["createdAt"][:10], target_status=target["status"],
            expected=expected, expected_qty=expected_qty,
            order_count=expected_order_count, chain=task["chain"],
            inject=task["inject"], instruction=task["instruction"],
        ))

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    index = {"schema_version": 2, "tasks": [
        {"task_id": s["task_id"], "path": s["task_id"] + "/task.json"} for s in summary]}
    open(os.path.join(BATCH, "index.json"), "w").write(json.dumps(index, indent=2) + "\n")

    return summary


if __name__ == "__main__":
    for s in main():
        print(s["task_id"], s["style"], "->", s["target"], s["target_date"],
              s["target_status"], s["expected"], "qty", s["expected_qty"],
              "orders", s["order_count"])
