#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 37 (shopping / monthly_spend_logged).

Writes bundle files only. Runs no validation, imports nothing from cua_gym,
compiles nothing, drives no browser.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/monthly_spend_logged")
REPLAYS = os.path.join(BATCH, "replays")

APP_DIR = "webarena_shopping_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

ADDR = {
    "firstname": "Emma",
    "lastname": "Lopez",
    "street": "101 S San Mateo Dr",
    "city": "San Mateo",
    "region": "California",
    "postcode": "94010",
    "country_id": "US",
    "telephone": "6505551212",
    "company": None,
    "email": None,
}

PROD = {
    46971: ("B005IR33MM", "Kosher MRE Meat Meals Ready to Eat, Beef Cholent & Kugel (1 Pack) - Prepared Shabbos Food Fully Cooked, Shelf Stable Microwave Dinner – Travel, Military, Camping, Emergency Survival Protein Supply", 12.99),
    44056: ("B07BM1HBCF", "Whole Foods Market, Bread Batard Olive, 19 Ounce", 48.29),
    33239: ("B072XS3F6W", "Hugh Industrial Rustic Farmhouse Table Lamp with Nightlight LED 26\" High Bronze Metal Seeded Glass Off-White Drum Shade for Living Room Bedroom House Bedside Nightstand Office - Franklin Iron Works", 169.99),
    22906: ("B07ZG4X2X1", "Tea Drops Organic Citrus Ginger Tea - Bulk Pack of 20 Lightly Sweetened, Loose Leaf, Pressed Organic Tea - Herbal Citrus Ginger Tea Blend To Go - Iced or Hot Bagless Tea Gift", 22.99),
    21217: ("B001W6RGV2", "Boost Pudding, Chocolate, 5-Ounce Tins (Pack of 48)", 76.72),
    48588: ("B014PDWFY6", "O-Med Arbequina Extra Virgin Olive Oil - 1000 ML (33.8 Fl Oz)", 31.99),
    101186: ("B087QJN9W1", "IDweel iPhone SE 2020 Case with Tempered Glass Screen Protector, Hybrid 3 in 1 Shockproof Slim Heavy Duty Hard PC Cover Soft Silicone Rugged Bumper Full Body Case for iPhone SE 2nd Gen (Red)", 12.99),
    101771: ("B001GZI4LA", "Vidpro MP-10 Monopod", 6.28),
    87030: ("B07WN2FF9B", "Bornbridge Artificial Spiral Topiary Tree - Indoor / Outdoor Topiary Trees - Artificial Outdoor Plants (2 Pack, 4' Cypress)", 260.69),
    15033: ("B087QSCXGT", "Uttermost Volterra Crackled Taupe-Gray Ceramic Table Lamp", 250.8),
    2589: ("B07T253TZY", "Bath Pillow (Non Slip), Relaxing Bath Pillows for Tub Neck and Back Support, Luxury Bathtub Pillow Headrest Cushion, Bath Tub Pillow Neck Head, Bath Accessories Women, Spa Jacuzzi Hot Tub Pillow Rest", 24.95),
    4644: ("B07QX9DM7K", "Organic Island Deodorant Extra Strength Sensitive (with 1/3 the Baking Soda Deodorant) with Probiotics (2.5 oz stick) (1 stick)", 14.99),
    5145: ("B082ZTJGSN", "AiJia 11 Bamboo Handle Makeup Brush Tool Portable Set Concealer Beauty Makeup Complete Combination Send Linen Bag Makeup Brush (Color : Clear)", 52.51),
    73063: ("B00J8RZL7I", "Quoizel TF9404M Grove Park Tiffany Multi-Color Floor Lamp", 749.99),
    17822: ("B09MT3HC4F", "HP Envy X360 2-in-1 13.3\" FHD OLED Touch-Screen Laptop | 11th Generation Intel Core i7-1195G7 | 8GB DDR4 RAM | 512GB SSD | Backlit Keyboard | Fingerprint | Windows 11 Home | with USB3.0 HUB Bundle", 999.99),
}


def cents(value):
    return int(round(value * 100))


def make_order(entity_id, created_at, status, lines, first_item_id):
    """Build one orders[] row carrying every field the seed convention writes."""
    state = {"complete": "complete", "canceled": "canceled", "pending": "new"}[status]
    items = []
    item_id = first_item_id
    subtotal_c = 0
    qty_total = 0
    for product_id, qty in lines:
        sku, name, price = PROD[product_id]
        row_total_c = cents(price) * qty
        subtotal_c += row_total_c
        qty_total += qty
        items.append({
            "itemId": item_id,
            "productId": product_id,
            "sku": sku,
            "name": name,
            "price": round(price, 2),
            "qtyOrdered": qty,
            "rowTotal": round(row_total_c / 100.0, 2),
            "productType": "simple",
            "options": [],
        })
        item_id += 1
    shipping_c = 500 * qty_total
    return {
        "entityId": entity_id,
        "incrementId": "%09d" % entity_id,
        "status": status,
        "state": state,
        "createdAt": created_at,
        "grandTotal": round((subtotal_c + shipping_c) / 100.0, 2),
        "subtotal": round(subtotal_c / 100.0, 2),
        "shippingAmount": round(shipping_c / 100.0, 2),
        "taxAmount": 0,
        "discountAmount": 0,
        "totalQtyOrdered": qty_total,
        "shippingDescription": "Flat Rate - Fixed",
        "customerEmail": "emma.lopez@gmail.com",
        "shippingMethod": "flatrate_flatrate",
        "paymentMethod": "checkmo",
        "paymentTitle": "Check / Money order",
        "billingAddress": dict(ADDR),
        "shippingAddress": dict(ADDR),
        "items": items,
    }


def wish_item(item_id, product_id, qty, added_at):
    sku, name, price = PROD[product_id]
    return {
        "wishlistItemId": item_id,
        "productId": product_id,
        "sku": sku,
        "name": name,
        "price": round(price, 2),
        "qty": qty,
        "description": "",
        "addedAt": added_at,
    }


# --------------------------------------------------------------------------
# Injected precondition sets
# --------------------------------------------------------------------------

APRIL_SET_A = [
    make_order(190, "2023-04-05 12:00:00", "complete", [(46971, 1), (44056, 1)], 900),
    make_order(191, "2023-04-12 12:00:00", "canceled", [(33239, 1)], 910),
    make_order(192, "2023-04-21 12:00:00", "complete", [(22906, 1), (21217, 1), (48588, 1)], 920),
]

APRIL_SET_B = [
    make_order(193, "2023-04-03 12:00:00", "complete", [(101186, 1), (101771, 1)], 930),
    make_order(194, "2023-04-09 12:00:00", "complete", [(87030, 1)], 940),
    make_order(195, "2023-04-17 12:00:00", "canceled", [(15033, 1)], 950),
    make_order(196, "2023-04-28 12:00:00", "complete", [(2589, 1), (4644, 1), (5145, 1)], 960),
]

WISHLIST_A = [
    wish_item(1, 73063, 1, "2023-05-22 14:31:07"),
    wish_item(2, 87030, 1, "2023-05-24 09:12:44"),
]

WISHLIST_B = [
    wish_item(1, 17822, 1, "2023-05-27 18:04:19"),
]


# --------------------------------------------------------------------------
# Reward source
# --------------------------------------------------------------------------

CORE = r'''
import re
from decimal import Decimal, InvalidOperation

# A "money token" is either a dollar-prefixed number or a bare number written to
# two decimal places. A bare year such as 2023 is neither, so a message that
# names its month does not accidentally register the year as an amount.
_MONEY_RE = re.compile(r"\$\s*\d[\d,]*(?:\.\d+)?|\d[\d,]*\.\d{2}")


def _amounts(text):
    found = set()
    if not isinstance(text, str):
        return found
    for raw in _MONEY_RE.findall(text):
        cleaned = raw.replace("$", "").replace(",", "").strip()
        try:
            value = Decimal(cleaned)
        except (InvalidOperation, ValueError):
            continue
        try:
            found.add(value.quantize(Decimal("0.01")))
        except (InvalidOperation, ValueError):
            continue
    return found


def _submissions(state):
    if not isinstance(state, dict):
        return []
    rows = state.get("contactSubmissions")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _sole_comment(state):
    rows = _submissions(state)
    if len(rows) != 1:
        return None
    comment = rows[0].get("comment")
    if not isinstance(comment, str) or not comment.strip():
        return None
    return comment


def _wishlist_rows(state):
    if not isinstance(state, dict):
        return []
    wishlist = state.get("wishlist")
    items = wishlist.get("items") if isinstance(wishlist, dict) else None
    if not isinstance(items, list):
        return []
    return [row for row in items if isinstance(row, dict)]


def _int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if float(value).is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            return None
        return int(number) if number.is_integer() else None
    return None


def _item_ids(state):
    found = set()
    for row in _wishlist_rows(state):
        item_id = _int(row.get("wishlistItemId"))
        if item_id is not None:
            found.add(item_id)
    return found


def _note(state, item_id):
    for row in _wishlist_rows(state):
        if _int(row.get("wishlistItemId")) == item_id:
            text = row.get("description")
            if isinstance(text, str) and text.strip():
                return text
            return None
    return None
'''


def checks_contact_single(names):
    return (
        "def _checks(state):\n"
        "    comment = _sole_comment(state)\n"
        "    results = {}\n"
        '    results["%s"] = comment is not None\n'
        '    results["%s"] = comment is not None and _amounts(comment) == EXPECTED_AMOUNTS\n'
        "    return results\n" % (names[0], names[1])
    )


def checks_contact_labelled(names):
    return (
        "def _checks(state):\n"
        "    comment = _sole_comment(state)\n"
        "    lowered = comment.lower() if comment is not None else \"\"\n"
        "    results = {}\n"
        '    results["%s"] = comment is not None\n'
        '    results["%s"] = comment is not None and REQUIRED_PHRASE in lowered\n'
        '    results["%s"] = comment is not None and _amounts(comment) == EXPECTED_AMOUNTS\n'
        "    return results\n" % (names[0], names[1], names[2])
    )


def checks_wishlist_single(names):
    return (
        "def _checks(state):\n"
        "    note = _note(state, TARGET_ITEM_ID)\n"
        "    results = {}\n"
        '    results["%s"] = note is not None\n'
        '    results["%s"] = (\n'
        "        note is not None\n"
        "        and _amounts(note) == EXPECTED_AMOUNTS\n"
        "        and _item_ids(state) == EXPECTED_ITEM_IDS\n"
        "    )\n"
        "    return results\n" % (names[0], names[1])
    )


def checks_wishlist_pair(names):
    return (
        "def _checks(state):\n"
        "    note = _note(state, TARGET_ITEM_ID)\n"
        "    amounts = _amounts(note) if note is not None else set()\n"
        "    in_scope = (\n"
        "        note is not None\n"
        "        and amounts <= EXPECTED_AMOUNTS\n"
        "        and _item_ids(state) == EXPECTED_ITEM_IDS\n"
        "    )\n"
        "    results = {}\n"
        '    results["%s"] = note is not None\n'
        '    results["%s"] = in_scope and MONTH_TOTAL in amounts\n'
        '    results["%s"] = in_scope and TOP_ORDER in amounts\n'
        "    return results\n" % (names[0], names[1], names[2])
    )


CHECK_BUILDERS = {
    "contact_single": checks_contact_single,
    "contact_labelled": checks_contact_labelled,
    "wishlist_single": checks_wishlist_single,
    "wishlist_pair": checks_wishlist_pair,
}


def constants_block(task):
    lines = []
    amounts = ", ".join('Decimal("%s")' % a for a in task["amounts"])
    lines.append("EXPECTED_AMOUNTS = {%s}" % amounts)
    if "phrase" in task:
        lines.append('REQUIRED_PHRASE = "%s"' % task["phrase"])
    if "target_item_id" in task:
        lines.append("TARGET_ITEM_ID = %d" % task["target_item_id"])
        lines.append("EXPECTED_ITEM_IDS = {%s}" % ", ".join(str(i) for i in task["item_ids"]))
    if task["kind"] == "wishlist_pair":
        lines.append('MONTH_TOTAL = Decimal("%s")' % task["month_total"])
        lines.append('TOP_ORDER = Decimal("%s")' % task["top_order"])
    return "\n".join(lines)


def weights_block(task):
    body = "\n".join('    "%s": %s,' % (n, w) for n, w in task["components"])
    return "COMPONENT_WEIGHTS = {\n%s\n}\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9" % body


def reward_py(task):
    doc = ["Deterministic reward for %s." % task["task_id"], "", "Success criteria:"]
    for line in task["success_criteria"]:
        doc.append("  * %s" % line)
    doc += [
        "",
        "Scoring reads current_state only, never a diff against initial_state, so an",
        "empty current_state scores 0.0 on every component and a key that returns to",
        "its pristine value cannot fabricate a miss.",
        "",
        "Ground truth is arithmetic over the seeded (and, where a setup injects them,",
        "the injected) orders of webarena_shopping_mock. Order records are immutable",
        "on the storefront: there is no cancel, status or order-total control anywhere",
        "in pages/, components/ or context/, so the figure cannot move mid-episode.",
    ]
    names = [n for n, _ in task["components"]]
    return (
        '"""%s\n"""\n' % "\n".join(doc)
        + CORE
        + "\n\n"
        + weights_block(task)
        + "\n\n"
        + constants_block(task)
        + "\n\n\n"
        + CHECK_BUILDERS[task["kind"]](names)
        + '''

def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state") if isinstance(app.get("current_state"), dict) else {}
    checks = _checks(state)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {"satisfied": bool(checks.get(name))},
        }
        for name in COMPONENT_WEIGHTS
    ]
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
'''
    )


def nemo_reward_py(task):
    names = [n for n, _ in task["components"]]
    doc = [
        "NeMo-Gym reward program for %s." % task["task_id"],
        "",
        "Implements exactly the rubric of reward.py, reading current_state from",
        "GET /go?sid=... instead of a frozen evidence bundle, and printing",
        "REWARD: <float> on every output path including the error path.",
        "",
        "Self-contained: standard library plus requests, which is present in",
        "cuagym/requirements.txt.",
    ]
    return (
        '"""%s\n"""\n' % "\n".join(doc)
        + "\nimport sys\n\nimport requests\n"
        + CORE
        + '\nSID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % URL_PLACEHOLDER
        + weights_block(task)
        + "\n\n"
        + constants_block(task)
        + "\n\n\n"
        + CHECK_BUILDERS[task["kind"]](names)
        + '''

def score_state(state):
    checks = _checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    return round(total, 6)


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        payload = response.json()
        state = payload.get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        value = score_state(state)
    except Exception as exc:
        print("reward scoring failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %s" % value)


main()
'''
    )


SETUP_HEAD = '''"""NeMo-Gym setup program for %(task_id)s.

%(purpose)s

The pristine session document is read back from GET /go?sid= first and the
patched document is POSTed whole, so no top-level key is dropped by the
server-side merge. The inlined fixture is a raw string literal, so no escape is
eaten by the Python parser before the JSON decoder sees it.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url)s"

'''


def setup_py(task):
    fixture_lines = []
    body_lines = []
    if task.get("orders"):
        fixture_lines.append(
            'INJECTED_ORDERS = json.loads(r"""\n%s\n""")\n' % json.dumps(task["orders"], indent=1)
        )
        fixture_lines.append("NEXT_ORDER_ID = %d\n" % task["next_order_id"])
        body_lines.append("    existing = state.get(\"orders\")")
        body_lines.append("    if not isinstance(existing, list):")
        body_lines.append("        existing = []")
        body_lines.append("    injected_ids = set()")
        body_lines.append("    for row in INJECTED_ORDERS:")
        body_lines.append("        injected_ids.add(row[\"entityId\"])")
        body_lines.append("    kept = []")
        body_lines.append("    for row in existing:")
        body_lines.append("        if isinstance(row, dict) and row.get(\"entityId\") in injected_ids:")
        body_lines.append("            continue")
        body_lines.append("        kept.append(row)")
        body_lines.append("    state[\"orders\"] = kept + INJECTED_ORDERS")
        body_lines.append("    state[\"nextOrderEntityId\"] = NEXT_ORDER_ID")
        body_lines.append("    state[\"nextOrderIncrementId\"] = NEXT_ORDER_ID")
    if task.get("wishlist"):
        fixture_lines.append(
            'INJECTED_WISHLIST = json.loads(r"""\n%s\n""")\n' % json.dumps(task["wishlist"], indent=1)
        )
        fixture_lines.append("NEXT_WISHLIST_ITEM_ID = %d\n" % task["next_wishlist_id"])
        body_lines.append("    state[\"wishlist\"] = {\"items\": INJECTED_WISHLIST}")
        body_lines.append("    state[\"nextWishlistItemId\"] = NEXT_WISHLIST_ITEM_ID")
    head = SETUP_HEAD % {
        "task_id": task["task_id"],
        "purpose": task["setup_purpose"],
        "url": URL_PLACEHOLDER,
    }
    return (
        head
        + "\n".join(fixture_lines)
        + '''

def main():
    read = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    read.raise_for_status()
    payload = read.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not state:
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: no session document to patch", file=sys.stderr)
        raise SystemExit(1)
    state = json.loads(json.dumps(state))
'''
        + "\n".join(body_lines)
        + '''
    written = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    written.raise_for_status()
    print("SETUP OK")


main()
'''
    )


# --------------------------------------------------------------------------
# The ten tasks
# --------------------------------------------------------------------------

LANE = "monthly_spend_logged"

TASKS = [
    {
        "task_id": "monthly_spend_logged_aug2022_net_of_cancels_001",
        "instruction": "Add up what my August 2022 orders actually cost me, leaving out anything I cancelled, and send that dollar total to the store through Contact Us. Put only the amount in the message.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "contact_single",
        "amounts": ["75.98"],
        "components": [("contact_message_submitted", 0.3), ("august_2022_net_spend_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {75.98} - the sum of the two non-cancelled August 2022 orders, 000000165 $36.99 and 000000155 $38.99.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to August 2022 -> sum the grand totals of the orders that are not cancelled -> submit that figure through the Contact Us form",
        "analogues": ["How much I spend in July 2022 on shopping at One Stop Market?"],
        "hard_criteria": ["derived_target", "cross_page"],
        "notes": [
            "August 2022 holds three orders: 000000165 $36.99 complete, 000000155 $38.99 complete, 000000172 $77.66 canceled. Non-cancelled sum 75.98; gross sum 153.64. The exclusion is load-bearing - an agent that ignores the Status column gets 153.64 and scores 0.7 less.",
            "Status is a column on /sales/order/history/ (OrderHistoryPage.jsx:49, :59), so no per-order drill-in is required for this one.",
            "Month bucketing only. Order 000000172 stores 2022-08-12 14:02:32 and none of the five timezone-shifted orders (185, 154, 163, 166, 170) falls in August 2022.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_oct2022_all_statuses_002",
        "instruction": "I am reconciling last year's card statement. In My Orders, take every order dated October 2022 - include the cancelled one, because the charge still shows on the statement - and add up the Order Total column for that month. Then open Contact Us from the site footer and submit one message reading \"October 2022 order total: <amount>\", with <amount> written as a dollar figure such as $1,234.56. Actually submit the form rather than leaving it filled in, and put no other numbers in the message.",
        "style": "explicit",
        "difficulty": "hard",
        "kind": "contact_labelled",
        "amounts": ["3336.22"],
        "phrase": "october 2022 order total",
        "components": [
            ("contact_message_submitted", 0.25),
            ("message_labelled_for_october_2022", 0.25),
            ("october_2022_gross_total_recorded", 0.5),
        ],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "The comment contains the label \"October 2022 order total\" (case-insensitive).",
            "The comment's set of money figures is exactly {3336.22} - the grand totals of all four October 2022 orders, 000000185 $18.99, 000000177 $2,126.32, 000000178 $345.84 and 000000176 $845.07.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to October 2022 -> sum every order's grand total including the cancelled one -> submit a labelled Contact Us message carrying that figure",
        "analogues": ["How much did I spend on shopping at One Stop Market on November 2022? They gave me a 20% discount on the total amount for orders exceeding $200 in cash"],
        "hard_criteria": ["derived_target", "cross_page"],
        "notes": [
            "This is the deliberate counterpart to task 001: it says in so many words that cancelled orders COUNT, and the answer 3336.22 differs from the non-cancelled sum 1209.90.",
            "Order 000000185 stores 2022-10-04 03:06:56 and renders 10/3/22 under America/New_York (format.js:4). It stays inside October either way, which is why this lane buckets by month and never by day.",
            "Explicit style because the message has a required label and the include-the-cancelled-order rule is an external accounting decision the site cannot tell the agent.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_feb2023_cancelled_refund_003",
        "instruction": "Some of my February 2023 orders were cancelled. Total those cancelled orders up, shipping included, and ask the store through Contact Us to confirm that refund amount. Put only the dollar figure in the message.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "contact_single",
        "amounts": ["406.53"],
        "components": [("contact_message_submitted", 0.3), ("feb_2023_cancelled_refund_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {406.53} - the grand totals of the two cancelled February 2023 orders, 000000158 $174.99 and 000000156 $231.54.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to February 2023 -> sum the grand totals of the cancelled orders only -> submit that refund figure through Contact Us",
        "analogues": ["How much refund I should expect from my order cancelled in Feb 2023, including shipping fee"],
        "hard_criteria": ["derived_target", "cross_page"],
        "notes": [
            "February 2023 holds four orders; the two cancelled ones are 000000158 $174.99 and 000000156 $231.54 (sum 406.53). The two complete ones sum to 947.50 and the month gross is 1354.03, so all three readings are distinct and the status filter is load-bearing.",
            "\"Shipping included\" is satisfied by the grand total as printed, since grandTotal == subtotal + shippingAmount with tax and discount zero on all 37 seeded orders. It rules out the subtotal-only reading of 396.53.",
            "No setup: both target orders are on page 1 of /sales/order/history/ in the pristine seed.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_sep2022_note_on_wishlist_lamp_004",
        "instruction": "Total what September 2022 cost me across all my orders, then write that dollar amount into the comment box on the Quoizel floor lamp row of my wish list and save it.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "wishlist_single",
        "amounts": ["3024.38"],
        "target_item_id": 1,
        "item_ids": [1, 2],
        "components": [("comment_written_on_the_lamp_row", 0.3), ("september_2022_total_recorded", 0.7)],
        "success_criteria": [
            "The wish-list row with wishlistItemId 1 (product 73063, Quoizel TF9404M Grove Park Tiffany Multi-Color Floor Lamp) has a non-empty description.",
            "That description's set of money figures is exactly {3024.38} - the September 2022 order totals 000000175 $133.85 and 000000179 $2,890.53 - and the wish list still holds exactly the two saved rows, wishlistItemId 1 and 2.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to September 2022 -> sum both orders' grand totals -> type the figure into that wish-list row's comment box and press Update Wish List",
        "analogues": ["How much I spend in March 2023 on shopping at One Stop Market?"],
        "hard_criteria": ["derived_target", "cross_page"],
        "setup_purpose": "Pre-seeds the wish list with two saved home-furnishing products so the free-text comment box that WishlistPage.jsx:76-82 renders per row has a row to live on. The pristine data/wishlist.json is an empty items array, so without this the A7 writeback surface does not render at all.",
        "wishlist": WISHLIST_A,
        "next_wishlist_id": 3,
        "injected_preconditions": [
            "wishlist.items = two rows: wishlistItemId 1 = product 73063 Quoizel TF9404M Grove Park Tiffany Multi-Color Floor Lamp ($749.99), wishlistItemId 2 = product 87030 Bornbridge Artificial Spiral Topiary Tree ($260.69). Both descriptions are the empty string.",
            "nextWishlistItemId = 3, so a later addToWishlist cannot mint a duplicate id.",
        ],
        "notes": [
            "September 2022 has no cancelled order, so \"across all my orders\" and \"the ones that stuck\" agree at 3024.38 and the phrasing carries no hidden filter.",
            "The two injected wish-list rows are both real catalog products (products.json ids 73063 and 87030) at their catalog prices, so the row renders its image, rating and price exactly as an organically saved row would.",
            "The reward states the resulting collection positively - the description value AND the exact item-id set - so deleting the other row to make the target easier to find scores 0.7 less rather than being rewarded.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_dec22_vs_jan23_gap_005",
        "instruction": "Which cost me more overall, December 2022 or January 2023, and by how much? Message the store through Contact Us naming that month and the gap between the two totals - no other figures.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "contact_labelled",
        "amounts": ["369.48"],
        "phrase": "january",
        "components": [
            ("contact_message_submitted", 0.2),
            ("pricier_month_named_january", 0.3),
            ("monthly_gap_recorded", 0.5),
        ],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "The comment names January (case-insensitive), the month with the larger total.",
            "The comment's set of money figures is exactly {369.48} - January 2023's $572.88 minus December 2022's $203.40.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to two named months -> sum each month and subtract -> submit the winning month and the difference through Contact Us",
        "analogues": ["How much I spend each month from Jan to the end of March 2023 on shopping at One Stop Market? Give me the dollar amount for each month separately."],
        "hard_criteria": ["derived_target", "ordering_dependency"],
        "notes": [
            "December 2022 = four complete orders, 32.47 + 53.29 + 20.49 + 97.15 = 203.40. January 2023 = two complete orders, 132.24 + 440.64 = 572.88. Difference 369.48, and neither month contains a cancelled order so the comparison has one reading.",
            "Order 000000154 stores 2022-12-19 00:16:11 and renders 12/18/22, and 000000163 stores 2023-01-17 02:25:53 and renders 1/16/23. Both stay inside their month, which is exactly why the question is asked by month.",
            "Ordering dependency: both month sums must exist before the subtraction, and the subtraction before the message.",
            "The reward requires the money-token set to be exactly {369.48}, so pasting both month totals alongside the gap does not score. The instruction says \"no other figures\".",
        ],
    },
    {
        "task_id": "monthly_spend_logged_nov2022_shipping_share_006",
        "instruction": "I want to know what delivery alone cost me in November 2022. Go to My Orders, open each order dated November 2022 in turn, and read the Shipping & Handling line on the order view. Add those shipping charges together and ignore the merchandise subtotals and the grand totals. Then use the Contact Us link in the site footer and submit one message containing just that shipping total, written as a dollar figure.",
        "style": "explicit",
        "difficulty": "hard",
        "kind": "contact_single",
        "amounts": ["45.00"],
        "components": [("contact_message_submitted", 0.3), ("november_2022_shipping_total_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {45.00} - the Shipping & Handling lines of 000000183 $10.00, 000000171 $15.00 and 000000164 $20.00.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to November 2022 -> drill into each order view and sum only its Shipping & Handling line -> submit that figure through Contact Us",
        "analogues": ["How much I spent on cooking and food shopping during March 2022? Include shipping fee for each item is $5."],
        "hard_criteria": ["derived_target", "cross_page"],
        "notes": [
            "The order grid shows date, total and status only (OrderHistoryPage.jsx:41-71); the Shipping & Handling row exists only on /sales/order/view/order_id/:id/ (OrderViewPage.jsx tfoot). So this task genuinely spans five pages: landing, My Account, My Orders, three order views and Contact Us.",
            "November 2022 is three complete orders with quantities 2, 3 and 4. Shipping is $5.00 per item on all 37 seeded orders (shippingAmount == 5 * totalQtyOrdered), giving 10 + 15 + 20 = 45.00. The month gross is 403.18 and the subtotal sum 358.18, both distinct from the answer.",
            "Explicit style because \"shipping only, not the totals\" needs saying unambiguously; a terse version would read as the ordinary month-spend question.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_mar2023_merchandise_only_007",
        "instruction": "For my March 2023 expense claim I can only claim goods, not delivery. In My Orders, open every order dated March 2023 and read its Subtotal line - the figure above Shipping & Handling. Add those subtotals together, then submit that number through the Contact Us form in the footer as a single dollar amount, with no other figures in the message.",
        "style": "explicit",
        "difficulty": "hard",
        "kind": "contact_single",
        "amounts": ["53.31"],
        "components": [("contact_message_submitted", 0.3), ("mar_2023_merchandise_subtotal_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {53.31} - the Subtotal lines of 000000166 $12.99 and 000000180 $40.32.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to March 2023 -> drill into each order view and sum only its Subtotal line -> submit that figure through Contact Us",
        "analogues": ["How much I spent on food-related shopping during March 2023? Include shipping fee for each item is $5."],
        "hard_criteria": ["derived_target", "cross_page"],
        "notes": [
            "March 2023 holds 000000166 (grand 17.99, subtotal 12.99, one item) and 000000180 (grand 65.32, subtotal 40.32, five items). Merchandise-only sum 53.31; month gross 83.31; shipping 30.00. All three readings differ, so the drill-in is load-bearing and an agent that sums the grid column scores 0.7 less.",
            "Order 000000166 stores 2023-03-11 02:01:11 and renders 3/10/23, and 000000180 stores 2023-03-11 14:44:12 and renders 3/11/23. Both are March, so the month bucket is safe; a day-level version of this question would not be.",
            "Subtotal is only rendered in the order-view tfoot, never on the grid.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_april2023_injected_net_008",
        "instruction": "April 2023 - total up what I actually paid that month, leaving out anything that got cancelled, and send the figure to the store through Contact Us. Amount only, please.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "contact_single",
        "amounts": ["217.98"],
        "components": [("contact_message_submitted", 0.3), ("april_2023_net_spend_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {217.98} - the grand totals of the two non-cancelled April 2023 orders, 000000190 $71.28 and 000000192 $146.70.",
        ],
        "skills": ["R2", "R3", "A7"],
        "skill_chain": "filter the order grid to April 2023 -> sum the grand totals of the orders that are not cancelled -> submit that figure through Contact Us",
        "analogues": ["Today is 6/12/2023. Tell me how many fulfilled orders I have over the past month, and the total amount of money I spent."],
        "hard_criteria": ["derived_target", "cross_page"],
        "setup_purpose": "Fills the April 2023 gap in the seeded order history with three orders, one of them cancelled and deliberately the largest of the three, so that the status filter changes the answer instead of being decoration.",
        "orders": APRIL_SET_A,
        "next_order_id": 193,
        "injected_preconditions": [
            "orders gains three April 2023 rows: 000000190 2023-04-05 complete $71.28, 000000191 2023-04-12 canceled $174.99, 000000192 2023-04-21 complete $146.70.",
            "nextOrderEntityId and nextOrderIncrementId are both bumped to 193 so a later placeOrder cannot mint a duplicate increment id.",
        ],
        "notes": [
            "April 2023 is empty in the pristine seed, which is why official 106 ('How much I spend on 4/19/2023 ...') has a zero answer there. This task does not port 106 - it authors a new instance of the month-spend shape over injected data, and the values are not memorisable from the seed.",
            "Injection checklist: createdAt all later than 2023-02-09 18:50:18 so every row lands on page 1 of the 10-per-page grid; UTC clocks pinned to 12:00:00 (08:00 EDT) so no row can shift a calendar day under America/New_York; entityIds 190-192 above the seeded maximum 189; order line itemIds 900-922 above the seeded maximum 544; every productId resolves in products.json; status/state pairs are only (complete,complete) and (canceled,canceled), both of which the seed already holds; shippingAmount == 5 * totalQtyOrdered and grandTotal == subtotal + shippingAmount on every injected row.",
            "The distractor is the shape of the injection, not an extra entity: the cancelled order is the biggest of the three, so an agent that skips the Status column reports 392.97 and loses the value component.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_april2023_injected_top_and_total_009",
        "instruction": "Work out what all my April 2023 orders came to together, and which single order that month was the largest. Note both dollar figures in the comment on the HP Envy laptop row of my wish list.",
        "style": "terse",
        "difficulty": "hard",
        "kind": "wishlist_pair",
        "amounts": ["658.21", "265.69"],
        "month_total": "658.21",
        "top_order": "265.69",
        "target_item_id": 1,
        "item_ids": [1],
        "components": [
            ("comment_written_on_the_laptop_row", 0.3),
            ("april_2023_month_total_recorded", 0.35),
            ("largest_april_order_recorded", 0.35),
        ],
        "success_criteria": [
            "The wish-list row with wishlistItemId 1 (product 17822, HP Envy X360 2-in-1 laptop) has a non-empty description.",
            "That description carries the April 2023 month total 658.21, carries no money figure other than 658.21 and 265.69, and the wish list still holds exactly one row.",
            "That description carries the largest single April 2023 order total 265.69, carries no money figure other than 658.21 and 265.69, and the wish list still holds exactly one row.",
        ],
        "skills": ["R2", "R3", "R4", "A7"],
        "skill_chain": "filter the order grid to April 2023 -> sum all four grand totals and separately pick the maximum one -> write both figures into that wish-list row's comment box and press Update Wish List",
        "analogues": ["Today is 6/12/2023. Tell me how many fulfilled orders I have over the past month, and the total amount of money I spent."],
        "hard_criteria": ["derived_target", "ordering_dependency"],
        "setup_purpose": "Fills the April 2023 gap with four orders whose maximum has a clear but not trivial margin, and pre-seeds a single wish-list row so the free-text comment box has a home. This is a different injected precondition from task 008, not a different entity: the month has a different size, a different total and a different correct answer.",
        "orders": APRIL_SET_B,
        "next_order_id": 197,
        "wishlist": WISHLIST_B,
        "next_wishlist_id": 2,
        "injected_preconditions": [
            "orders gains four April 2023 rows: 000000193 2023-04-03 complete $29.27, 000000194 2023-04-09 complete $265.69, 000000195 2023-04-17 canceled $255.80, 000000196 2023-04-28 complete $107.45.",
            "nextOrderEntityId and nextOrderIncrementId are both bumped to 197.",
            "wishlist.items = one row, wishlistItemId 1 = product 17822 HP Envy X360 2-in-1 laptop ($999.99), description empty; nextWishlistItemId = 2.",
        ],
        "notes": [
            "Margin on the superlative: $265.69 versus $255.80, a $9.89 gap and no tie. Deliberately close enough that the grid has to be read rather than eyeballed, and the runner-up is the cancelled order so 'the largest order' and 'the largest order I paid for' differ - the instruction says the largest order, full stop, and the month total likewise includes everything.",
            "Month total 29.27 + 265.69 + 255.80 + 107.45 = 658.21. The non-cancelled sum 402.41 is a different number, so the include-everything reading is checkable.",
            "Same injection checklist as task 008: page-1 placement, 12:00:00Z clocks, entityIds 193-196, line itemIds 930-962, real productIds, coherent status/state, shipping 5 per item and grandTotal == subtotal + shippingAmount.",
            "The two value components share a scope guard (no money figure outside {658.21, 265.69} and the wish list still exactly one row), so partial credit is available for getting one figure right without letting an agent paste every order total into the box.",
        ],
    },
    {
        "task_id": "monthly_spend_logged_pending_orders_total_010",
        "instruction": "I still have orders sitting at Pending. Add up their totals and chase the store through Contact Us about when they will ship, quoting that combined amount as the only figure in the message.",
        "style": "terse",
        "difficulty": "medium",
        "kind": "contact_single",
        "amounts": ["3764.97"],
        "components": [("contact_message_submitted", 0.3), ("pending_orders_total_recorded", 0.7)],
        "success_criteria": [
            "state.contactSubmissions holds exactly one submission and its comment is non-empty.",
            "That comment's set of money figures is exactly {3764.97} - the grand totals of the three pending orders 000000187 $1,004.99, 000000188 $2,004.99 and 000000189 $754.99.",
        ],
        "skills": ["R3", "A7"],
        "skill_chain": "read the Status column across the order grid and sum the pending rows -> quote that figure in a submitted Contact Us message",
        "analogues": ["Tell me the total cost of my latest pending order?"],
        "hard_criteria": [],
        "notes": [
            "Two skills only - a status filter and a sum feeding one writeback, with no temporal component - so this is medium by the batch-5 derivation rule, not hard. It is not padded up to three skills.",
            "The seed holds exactly three pending orders, all on page 1 of the grid, totalling 3764.97. Their largest single total is 2004.99 and the May 2023 month gross is 4130.39, so neither near-miss reading collides with the answer.",
            "The three pending orders all render 5/2/23 and differ only by minutes, so this task deliberately asks for their sum rather than for 'the latest pending order', which the displayed date cannot resolve.",
        ],
    },
]


REPLAY_HEADER = '''"""Golden replay draft for %(task_id)s.

Click-only: after the initial goto of start_path there is no page.goto and no
URL construction. My Account is a header link, My Orders is an AccountNav link
in the account sidebar, View Order is an anchor in the grid's Action column,
Contact Us is a footer link on every full-chrome page and My Wish List is a
header link.
"""

START_PATH = '/'


def run(page, base_url):
    page.goto(base_url + START_PATH)
'''

REPLAY_TO_ORDERS = """    page.click('ul.header.links a:has-text("My Account")')
    page.click('a:has-text("My Orders")')
    page.wait_for_selector('#my-orders-table')
"""

REPLAY_CONTACT = """    page.click('footer a:has-text("Contact Us")')
    page.wait_for_selector('#contact-form')
    page.fill('#comment', %s)
    page.click('#contact-form button[type="submit"]')
    page.wait_for_selector('div.message')
"""

REPLAY_WISHLIST = """    page.click('ul.header.links a:has-text("My Wish List")')
    page.wait_for_selector('textarea.product-item-comment')
    page.fill('li.product-item:nth-of-type(%d) textarea.product-item-comment', %s)
    page.click('button.action.update.primary')
    page.wait_for_selector('div.message')
"""

REPLAY_DRILL = """    page.click('#my-orders-table tr:has-text("%s") a.action.view')
    page.wait_for_selector('table.table-order-items tfoot')
    page.click('a:has-text("My Orders")')
    page.wait_for_selector('#my-orders-table')
"""


def replay_src(task):
    body = REPLAY_HEADER % {"task_id": task["task_id"]}
    body += REPLAY_TO_ORDERS
    for increment in task.get("drill_ins", []):
        body += REPLAY_DRILL % increment
    if task["kind"].startswith("contact"):
        body += REPLAY_CONTACT % repr(task["replay_text"])
    else:
        body += REPLAY_WISHLIST % (1, repr(task["replay_text"]))
    return body


REPLAY_TEXT = {
    "monthly_spend_logged_aug2022_net_of_cancels_001": "$75.98",
    "monthly_spend_logged_oct2022_all_statuses_002": "October 2022 order total: $3,336.22",
    "monthly_spend_logged_feb2023_cancelled_refund_003": "Please confirm my refund of $406.53.",
    "monthly_spend_logged_sep2022_note_on_wishlist_lamp_004": "September 2022 spend: $3,024.38",
    "monthly_spend_logged_dec22_vs_jan23_gap_005": "January was the pricier month, by $369.48.",
    "monthly_spend_logged_nov2022_shipping_share_006": "$45.00",
    "monthly_spend_logged_mar2023_merchandise_only_007": "$53.31",
    "monthly_spend_logged_april2023_injected_net_008": "$217.98",
    "monthly_spend_logged_april2023_injected_top_and_total_009": "April 2023 came to $658.21 in total; the largest single order was $265.69.",
    "monthly_spend_logged_pending_orders_total_010": "My pending orders come to $3,764.97 - when will they ship?",
}

DRILL_INS = {
    "monthly_spend_logged_nov2022_shipping_share_006": ["000000183", "000000171", "000000164"],
    "monthly_spend_logged_mar2023_merchandise_only_007": ["000000166", "000000180"],
}


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    rows = []
    index = []
    for task in TASKS:
        task["replay_text"] = REPLAY_TEXT[task["task_id"]]
        task["drill_ins"] = DRILL_INS.get(task["task_id"], [])
        bundle = os.path.join(OUT, task["task_id"])
        os.makedirs(bundle, exist_ok=True)

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": task["task_id"],
                "task_instruction": task["instruction"],
                "app_dir": APP_DIR,
                "start_path": "/",
                "difficulty": task["difficulty"],
                "success_criteria": task["success_criteria"],
            }, fh, indent=2)
            fh.write("\n")

        metadata = {
            "style": task["style"],
            "difficulty": task["difficulty"],
            "shape": "retrieval_writeback",
            "skills": task["skills"],
            "skill_chain": task["skill_chain"],
            "official_analogues": task["analogues"],
            "topic": LANE,
            "batch": "batch-5 lane 37 (shopping / R2 -> R3 -> A7)",
            "lane": LANE,
            "inspiration_ids": [],
            "authoring_notes": task["notes"],
            "hard_criteria": task["hard_criteria"],
        }
        if task.get("injected_preconditions"):
            metadata["injected_preconditions"] = task["injected_preconditions"]

        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump({
                "schema_version": 2,
                "task_id": task["task_id"],
                "instruction": task["instruction"],
                "apps": [{
                    "name": APP_DIR,
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
                "metadata": metadata,
            }, fh, indent=2)
            fh.write("\n")

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_py(task))
        nemo_reward = nemo_reward_py(task)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward)

        setup_src = None
        setup_path = os.path.join(bundle, "initial_setup.py")
        if task.get("orders") or task.get("wishlist"):
            setup_src = setup_py(task)
            with open(setup_path, "w") as fh:
                fh.write(setup_src)
        elif os.path.exists(setup_path):
            os.remove(setup_path)

        row = {"task_payload": {
            "task_id": task["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task["task_id"],
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        rows.append(row)
        index.append({"task_id": task["task_id"], "path": "../../%s/task.json" % task["task_id"]})

        with open(os.path.join(REPLAYS, task["task_id"] + ".py"), "w") as fh:
            fh.write(replay_src(task))

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({"schema_version": 2, "tasks": index}, fh, indent=2)
        fh.write("\n")
    print("wrote %d bundles" % len(TASKS))


main()
