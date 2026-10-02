#!/usr/bin/env python3
"""Batch-6 lane 39 generator: shopping R4 -> A11.

Writes ten bundles under output/tasks/shopping/<task_id>/ plus the lane's
GENERATION.md and replay drafts. Authoring tool only; runs no validation.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/order_address_into_book")
REPLAYS = os.path.join(BATCH, "replays")

APP_DIR = "webarena_shopping_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

# --------------------------------------------------------------------------
# Address pools. Target addresses are unique per task; decoy addresses are
# drawn from a disjoint pool so a decoy can never be mistaken for a target.
# Every region string is a verbatim US_REGIONS name (geo.js:5).
# --------------------------------------------------------------------------

TARGETS = {
    1: ("1712 Pinehurst Ct", "Ann Arbor", "Michigan", "48104", "7345550118"),
    2: ("940 Beacon Hill Rd", "Providence", "Rhode Island", "02906", "4015550143"),
    3: ("305 Alder Creek Ln", "Boise", "Idaho", "83702", "2085550177"),
    4: ("66 Harborview Ter", "Portland", "Maine", "04101", "2075550132"),
    5: ("2418 Sagebrush Loop", "Santa Fe", "New Mexico", "87501", "5055550194"),
    6: ("77 Copperfield Row", "Louisville", "Kentucky", "40202", "5025550126"),
    7: ("1350 Quarry Bend Dr", "Chattanooga", "Tennessee", "37402", "4235550109"),
    8: ("519 Marsh Wren Way", "Savannah", "Georgia", "31401", "9125550163"),
    9: ("84 Wintergreen Ave", "Burlington", "Vermont", "05401", "8025550187"),
    10: ("6201 Silver Sage Blvd", "Reno", "Nevada", "89501", "7755550151"),
}

DECOYS = [
    ("233 Foxglove St", "Madison", "Wisconsin", "53703", "6085550172"),
    ("1109 Trestle Bridge Rd", "Asheville", "North Carolina", "28801", "8285550138"),
    ("47 Kettle Pond Dr", "Concord", "New Hampshire", "03301", "6035550115"),
    ("8802 Prairie Rose Ct", "Wichita", "Kansas", "67202", "3165550149"),
    ("615 Cobblestone Walk", "Charleston", "South Carolina", "29401", "8435550196"),
    ("3020 Windmill Hill Rd", "Des Moines", "Iowa", "50309", "5155550183"),
    ("129 Lantern Cove Ln", "Anchorage", "Alaska", "99501", "9075550124"),
    ("4406 Chestnut Barrow Dr", "Tulsa", "Oklahoma", "74103", "9185550158"),
    ("71 Foundry Square", "Hartford", "Connecticut", "06103", "8605550171"),
    ("2755 Hollow Brook Rd", "Billings", "Montana", "59101", "4065550140"),
]


def addr_obj(tup):
    street, city, region, postcode, telephone = tup
    return {
        "firstname": "Emma",
        "lastname": "Lopez",
        "street": street,
        "city": city,
        "region": region,
        "postcode": postcode,
        "country_id": "US",
        "telephone": telephone,
        "company": None,
        "email": None,
    }


TERSE = "terse"
EXPLICIT = "explicit"

ANALOGUE_MOVED = {
    571: "I recently moved, my address is 231 Willow Way, Suite 100, Chicago, IL, 60601, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
    572: "I recently moved, my address is 654 Aspen Road, House #3, Boston, MA, 02110, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
    573: "I recently moved, my address is 987 Sycamore Circle, Philadelphia, PA, 19102, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
    574: "I recently moved, my address is 111 Magnolia Path, Atlanta, GA, 30303, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
    575: "I recently moved, my address is 222 Redwood Rise, Suite 300, Seattle, WA, 98101, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
}
A794 = "Change the delivery address for my most recent non canceled order to 4000 Forbes Ave, Pittsburgh, PA."
A795 = "Change the delivery address for my second most recent order to 6726 McPherson Blvd, Pittsburgh, PA."
A796 = "Change the delivery address for my oldest order in 2023 to 155 5th Street, San Francisco, CA."
A798 = "Change the delivery address for my most recent non canceled order to 77 Massachusetts Ave, Cambridge, MA."
A231 = "Get the order number of my most recent cancelled order"
A233 = "Get the order number of my most recent complete order"
A232 = "Get the order number of my most recent pending order"

# --------------------------------------------------------------------------
# Task table.
#   n, slug, target entityId, target incrementId, ordinal prose (for notes),
#   decoy entityIds, style, start_path, default flags (billing, shipping),
#   instruction, margin note, analogues, derived_from
# --------------------------------------------------------------------------

TASKS = [
    dict(
        n=1, slug="second_most_recent_order", order=189, inc="000000189",
        decoys=[170, 188, 187, 180], style=TERSE, start="/",
        flags=(True, True),
        ordinal="second most recent order (grid row 2 under sortedOrders full-timestamp desc)",
        instruction=(
            "My second most recent order shipped to an address that isn't in my "
            "address book. Add it there exactly as shown — street, city, state, "
            "ZIP, phone — and make it my default billing and shipping address."
        ),
        margin=("Positional ordinal. sortedOrders (utils/orders.js:33-35) is a "
                "full-timestamp descending sort, so the grid reads 170 "
                "(2023-05-18 03:39:44), then 189 (2023-05-02 17:21:19), then 188 "
                "(17:19:42), then 187 (17:16:43). Row 2 is 189 by a 1m37s margin "
                "over 188 and it also carries the highest increment id of the "
                "same-minute trio, so the two defensible readings agree. Ground "
                "truth is NOT built on the rendered date, which is 5/2/23 for all "
                "three."),
        analogues=[A795, ANALOGUE_MOVED[571]],
        derived_from="address_book_move_order_destination_relocation_002",
    ),
    dict(
        n=2, slug="oldest_cancelled_order", order=160, inc="000000160",
        decoys=[169, 173, 159, 168], style=TERSE, start="/",
        flags=(False, True),
        ordinal="oldest cancelled order",
        instruction=(
            "My oldest cancelled order went to an address I never saved. Add it to "
            "my address book exactly as shown, phone included, and make it my "
            "default shipping address. Leave billing on San Mateo."
        ),
        margin=("Cancelled orders ascending: 160 (2022-03-02 20:04:12), 173 "
                "(2022-03-10 12:03:09), 182 (2022-06-30). Margin to the next "
                "cancelled order is 7 days 16 hours. The genuinely oldest order "
                "overall is 169 (2022-03-02 11:01:12, Complete) and it renders the "
                "same day 3/2/22, so the Status column is the only discriminator "
                "— which is exactly the predicate the task asks for. 169 is "
                "injected with a decoy address so taking it scores 0.0."),
        analogues=[A231, ANALOGUE_MOVED[572]],
        derived_from=None,
    ),
    dict(
        n=3, slug="largest_grand_total", order=179, inc="000000179",
        decoys=[177, 188, 187, 176], style=EXPLICIT, start="/",
        flags=(True, True),
        ordinal="highest grand total of all 37 orders",
        instruction=(
            "Open my order history and find the order with the highest grand total "
            "of all my orders. Open it and read its shipping address. Then, in my "
            "address book, add a new address entry using that street, city, state, "
            "ZIP code and phone number, and mark it as both my default billing "
            "address and my default shipping address. Keep the existing San Mateo "
            "entry in place."
        ),
        margin=("Grand totals descending: 179 $2,890.53, 177 $2,126.32, 188 "
                "$2,004.99, 187 $1,004.99. Margin $764.21. 179 is Complete and is "
                "also the maximum among completed orders only, so the "
                "include-cancelled question does not change the answer and no "
                "scope hedge is needed. All 37 grand totals are distinct."),
        analogues=[ANALOGUE_MOVED[573], A794],
        derived_from=None,
    ),
    dict(
        n=4, slug="second_largest_grand_total", order=177, inc="000000177",
        decoys=[179, 188, 187, 176], style=TERSE, start="/",
        flags=(True, False),
        ordinal="second largest grand total, cancelled orders included",
        instruction=(
            "Cancelled orders count: find my second-biggest order by grand total. "
            "Save its shipping address as a new address book entry, exactly as "
            "shown including the phone, and make it my default billing address only."
        ),
        margin=("179 $2,890.53 then 177 $2,126.32 then 188 $2,004.99: the second "
                "place margin is $764.21 above and $121.33 below. 177 is Canceled, "
                "so the instruction states the scope explicitly — excluding "
                "cancelled orders would give 176 at $845.07 instead, and 176 also "
                "carries a decoy address so that reading scores 0.0."),
        analogues=[ANALOGUE_MOVED[574], A795],
        derived_from=None,
    ),
    dict(
        n=5, slug="cheapest_order", order=166, inc="000000166",
        decoys=[185, 184, 168, 174], style=TERSE, start="/sales/order/history/",
        flags=(False, False),
        ordinal="lowest grand total of all 37 orders",
        instruction=(
            "My cheapest order by grand total shipped somewhere not in my address "
            "book. Add that address as a new entry, exactly as shown with the "
            "phone. Keep San Mateo as my default for both billing and shipping."
        ),
        margin=("Grand totals ascending: 166 $17.99, 185 $18.99, 184 $20.49, 168 "
                "$24.86, 174 $32.47. Margin $1.00 — tight but tie-free, and "
                "the Order Total column is rendered on the grid so the comparison "
                "is a direct read rather than an estimate. 166 is Complete and is "
                "also the minimum over any status subset that contains it."),
        analogues=[ANALOGUE_MOVED[575], A798],
        derived_from=None,
    ),
    dict(
        n=6, slug="top_pending_order", order=188, inc="000000188",
        decoys=[187, 189, 179, 177], style=TERSE, start="/",
        flags=(True, True),
        ordinal="largest grand total among the three Pending orders",
        instruction=(
            "Of my three pending orders, the one with the largest grand total "
            "shipped to an unsaved address. Add it to my address book exactly as "
            "shown, phone included, and make it my default billing and shipping "
            "address."
        ),
        margin=("The Pending set is exactly {187 $1,004.99, 188 $2,004.99, 189 "
                "$754.99}. Winner 188 by $1,000.00. This is the disambiguator the "
                "author brief asks for: all three render 5/2/23, so the task keys "
                "on grand total rather than on date or increment id."),
        analogues=[A232, ANALOGUE_MOVED[571]],
        derived_from=None,
    ),
    dict(
        n=7, slug="second_latest_cancelled", order=156, inc="000000156",
        decoys=[170, 158, 177, 149], style=EXPLICIT, start="/",
        flags=(False, True),
        ordinal="second most recent cancelled order",
        instruction=(
            "Look through my cancelled orders and pick the second most recent one. "
            "Open that order and copy its shipping address into my address book as "
            "a new entry — same street, city, state, ZIP code and phone "
            "number. Set the new entry as my default shipping address, but leave "
            "101 S San Mateo Dr as my default billing address."
        ),
        margin=("Cancelled orders descending: 170 (2023-05-18), 156 (2023-02-24), "
                "158 (2023-02-11), 177 (2022-10-18). Second place is 156 with 83 "
                "days of clearance above and 13 days below. Note 170 is stored "
                "2023-05-18 03:39:44 UTC and renders 5/17/23 in America/New_York "
                "(format.js:4); that shift cannot reorder anything here because "
                "the gap to 156 is months."),
        analogues=[A231, ANALOGUE_MOVED[572]],
        derived_from=None,
    ),
    dict(
        n=8, slug="last_order_of_2022", order=154, inc="000000154",
        decoys=[184, 162, 174, 163], style=TERSE, start="/sales/order/history/",
        flags=(True, False),
        ordinal="most recent order placed in calendar year 2022",
        instruction=(
            "My last order of 2022 shipped to an address missing from my address "
            "book. Add it there exactly as shown, phone included, and make it my "
            "default billing address. Default shipping stays on San Mateo."
        ),
        margin=("2022 orders descending: 154 (2022-12-19 00:16:11), 184 "
                "(2022-12-14 12:13:41), 162 (2022-12-12). Margin 4 days 12 hours. "
                "154 is one of the five orders that render a day early — it "
                "prints 12/18/22 — but it stays inside December, so a "
                "MONTH/YEAR bucket is safe, which is what this ordinal uses. The "
                "next order above it is 163 on 1/17/23, unambiguously 2023."),
        analogues=[A796, ANALOGUE_MOVED[573]],
        derived_from=None,
    ),
    dict(
        n=9, slug="first_order_of_2023", order=163, inc="000000163",
        decoys=[154, 148, 157, 158], style=EXPLICIT, start="/",
        flags=(True, True),
        ordinal="oldest order placed in calendar year 2023",
        instruction=(
            "Find the first order I placed in 2023 — the oldest one dated in "
            "that year. Open it, read the shipping address, and add that address to "
            "my address book as a new entry with the same street, city, state, ZIP "
            "code and phone number. Make the new entry my default billing address "
            "and my default shipping address."
        ),
        margin=("2023 orders ascending: 163 (2023-01-17 02:25:53), 148 "
                "(2023-01-29 22:29:11), 157 (2023-02-09). Margin 12 days 20 hours. "
                "163 renders 1/16/23 rather than 1/17/23 under America/New_York, "
                "which keeps it inside January 2023 and does not move the "
                "ordinal. The nearest 2022 row is 154 on 12/18/22."),
        analogues=[A796, ANALOGUE_MOVED[574]],
        derived_from=None,
    ),
    dict(
        n=10, slug="latest_completed_order", order=180, inc="000000180",
        decoys=[166, 161, 170, 189], style=TERSE, start="/",
        flags=(False, True),
        ordinal="most recent order with status Complete",
        instruction=(
            "My most recent completed order went to an address that isn't saved. "
            "Add it to my address book exactly as shown, phone included, and make "
            "it my default shipping address; billing stays on San Mateo."
        ),
        margin=("Complete orders descending: 180 (2023-03-11 14:44:12), 166 "
                "(2023-03-11 02:01:11), 161 (2023-02-27). Stored margin 12h43m, "
                "and the rendered days differ too — 180 prints 3/11/23 while "
                "166 prints 3/10/23 under America/New_York — so both the "
                "timestamp reading and the rendered-date reading select 180. The "
                "rows above it, 170 (Canceled) and 189/188/187 (Pending), are "
                "excluded by the status predicate."),
        analogues=[A233, ANALOGUE_MOVED[575]],
        derived_from=None,
    ),
]

# --------------------------------------------------------------------------

SEED_26 = ("101 S San Mateo Dr", "San Mateo", "California", "94010", "6505551212")


def flag_prose(flags):
    b, s = flags
    if b and s:
        return "both default billing and default shipping"
    if s:
        return "default shipping only (billing stays on record 26)"
    if b:
        return "default billing only (shipping stays on record 26)"
    return "neither default (both stay on record 26)"


def success_criteria(t):
    street, city, region, postcode, phone = TARGETS[t["n"]]
    b, s = t["flags"]
    exp_b = 27 if b else 26
    exp_s = 27 if s else 26
    return [
        ("state.addresses holds exactly ids 26 and 27, and record 27 normalises to "
         "street \"%s\", city \"%s\", region \"%s\", postcode \"%s\" and telephone "
         "\"%s\" — the address order %s shipped to."
         % (street, city, region, postcode, phone, t["inc"])),
        ("Record 27 has isDefaultBilling %s and isDefaultShipping %s; "
         "customer.defaultBilling is %d and customer.defaultShipping is %d."
         % (str(b).lower(), str(s).lower(), exp_b, exp_s)),
        ("Record 26 still holds 101 S San Mateo Dr, San Mateo, California, 94010 "
         "with isDefaultBilling %s and isDefaultShipping %s."
         % (str(not b).lower(), str(not s).lower())),
    ]


REWARD_BODY = '''
EXPECTED_STREET = "{street}"
EXPECTED_CITY = "{city}"
EXPECTED_REGION = "{region}"
EXPECTED_POSTCODE = "{postcode}"
EXPECTED_PHONE_DIGITS = "{phone}"

NEW_ID = 27
SEED_ID = 26
EXPECT_NEW_BILLING_DEFAULT = {b}
EXPECT_NEW_SHIPPING_DEFAULT = {s}
EXPECT_CUSTOMER_BILLING = {cb}
EXPECT_CUSTOMER_SHIPPING = {cs}

SEED_STREET = "101 S San Mateo Dr"
SEED_CITY = "San Mateo"
SEED_REGION = "California"
SEED_POSTCODE = "94010"


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
    if float(number).is_integer():
        return int(number)
    return None


def _text(value):
    if isinstance(value, str):
        return " ".join(value.split()).casefold()
    return None


def _digits(value):
    if not isinstance(value, str):
        return None
    return re.sub(r"[^0-9]", "", value)


def _street(value):
    """Collapse a stored street to one canonical comma-joined lowercase string.

    The address book keeps two form lines in a list, order records keep a
    single newline-joined string, and a shopper may legitimately type the
    whole line into "Street Address: Line 1". All three collapse here.
    """
    if isinstance(value, list):
        raw = value
    elif isinstance(value, str):
        raw = value.split("\\n")
    else:
        raw = []
    parts = []
    for chunk in raw:
        if not isinstance(chunk, str):
            continue
        for piece in chunk.split(","):
            piece = " ".join(piece.split())
            if piece:
                parts.append(piece)
    return ", ".join(parts).casefold()


def _addresses(state):
    rows = state.get("addresses")
    if not isinstance(rows, list):
        return []
    return [a for a in rows if isinstance(a, dict)]


def _address_by_id(state, address_id):
    for a in _addresses(state):
        if _int(a.get("id")) == address_id:
            return a
    return None


def _address_ids(state):
    ids = []
    for a in _addresses(state):
        value = _int(a.get("id"))
        if value is not None:
            ids.append(value)
    return sorted(ids)


def _customer(state):
    customer = state.get("customer")
    if isinstance(customer, dict):
        return customer
    return {{}}


def _is_true(value):
    return value is True


def _is_false(value):
    return value is False or value is None


COMPONENT_WEIGHTS = {{
    "derived_order_address_saved": 0.6,
    "default_flags_as_instructed": 0.4,
}}


def _checks(state):
    ids = _address_ids(state)
    record = _address_by_id(state, NEW_ID)
    seed = _address_by_id(state, SEED_ID)
    customer = _customer(state)

    book_shape_ok = ids == [SEED_ID, NEW_ID] and isinstance(record, dict)

    saved = bool(
        book_shape_ok
        and _street(record.get("street")) == _street(EXPECTED_STREET)
        and _text(record.get("city")) == _text(EXPECTED_CITY)
        and _text(record.get("region")) == _text(EXPECTED_REGION)
        and _text(record.get("postcode")) == _text(EXPECTED_POSTCODE)
        and _digits(record.get("telephone")) == EXPECTED_PHONE_DIGITS
    )

    if EXPECT_NEW_BILLING_DEFAULT:
        new_billing_ok = isinstance(record, dict) and _is_true(record.get("isDefaultBilling"))
        seed_billing_ok = isinstance(seed, dict) and _is_false(seed.get("isDefaultBilling"))
    else:
        new_billing_ok = isinstance(record, dict) and _is_false(record.get("isDefaultBilling"))
        seed_billing_ok = isinstance(seed, dict) and _is_true(seed.get("isDefaultBilling"))

    if EXPECT_NEW_SHIPPING_DEFAULT:
        new_shipping_ok = isinstance(record, dict) and _is_true(record.get("isDefaultShipping"))
        seed_shipping_ok = isinstance(seed, dict) and _is_false(seed.get("isDefaultShipping"))
    else:
        new_shipping_ok = isinstance(record, dict) and _is_false(record.get("isDefaultShipping"))
        seed_shipping_ok = isinstance(seed, dict) and _is_true(seed.get("isDefaultShipping"))

    seed_intact = bool(
        isinstance(seed, dict)
        and _street(seed.get("street")) == _street(SEED_STREET)
        and _text(seed.get("city")) == _text(SEED_CITY)
        and _text(seed.get("region")) == _text(SEED_REGION)
        and _text(seed.get("postcode")) == _text(SEED_POSTCODE)
    )

    flags = bool(
        book_shape_ok
        and new_billing_ok
        and new_shipping_ok
        and seed_billing_ok
        and seed_shipping_ok
        and seed_intact
        and _int(customer.get("defaultBilling")) == EXPECT_CUSTOMER_BILLING
        and _int(customer.get("defaultShipping")) == EXPECT_CUSTOMER_SHIPPING
    )

    return {{
        "derived_order_address_saved": saved,
        "default_flags_as_instructed": flags,
    }}
'''


LOCAL_TAIL = '''

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


def evaluate(evidence):
    state = _state(evidence)
    try:
        checks = _checks(state)
    except Exception:
        checks = {}
    components = []
    for name in ("derived_order_address_saved", "default_flags_as_instructed"):
        ok = bool(checks.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": {"satisfied": ok},
        })
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
'''


NEMO_TAIL = '''

def score_state(state):
    checks = _checks(state)
    total = 0.0
    for name in ("derived_order_address_saved", "default_flags_as_instructed"):
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


def reward_py(t, task_id):
    street, city, region, postcode, phone = TARGETS[t["n"]]
    b, s = t["flags"]
    body = REWARD_BODY.format(
        street=street, city=city, region=region, postcode=postcode, phone=phone,
        b="True" if b else "False", s="True" if s else "False",
        cb=27 if b else 26, cs=27 if s else 26,
    )
    doc = '"""Deterministic reward for %s.\n\n' % task_id
    for line in success_criteria(t):
        doc += "  * %s\n" % line
    doc += (
        "\nOnly `current_state` is inspected; no diff against `initial_state` is\n"
        "taken. Ground truth is fixed by the frozen seed of webarena_shopping_mock\n"
        "in ./hub/ plus this bundle's injected order addresses.\n"
        '"""\n\n'
        "import re\n"
    )
    return doc + body + LOCAL_TAIL


def nemo_reward_py(t, task_id):
    street, city, region, postcode, phone = TARGETS[t["n"]]
    b, s = t["flags"]
    body = REWARD_BODY.format(
        street=street, city=city, region=region, postcode=postcode, phone=phone,
        b="True" if b else "False", s="True" if s else "False",
        cb=27 if b else 26, cs=27 if s else 26,
    )
    doc = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Implements exactly the rubric of reward.py, reading `current_state` from\n"
        "GET /go?sid=... and printing REWARD: <float> on every output path.\n\n"
        "Self-contained: standard library plus requests.\n"
        '"""\n\n'
        "import re\n"
        "import sys\n\n"
        "import requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n'
    ) % (task_id, URL_PLACEHOLDER)
    return doc + body + NEMO_TAIL


SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

Rewrites the shipping AND billing address of five seeded orders so that the
address the task asks for is genuinely derivable only from the right one.

Order {inc} — {ordinal} — is given {street}, {city}. Four
near-miss orders ({decoy_list}) are given four different, equally
unsaved addresses, so an agent that picks the wrong row copies the wrong
address and scores 0.0. Without this, all 37 seeded orders ship to the single
address already on file (101 S San Mateo Dr) and the untouched state would
satisfy the rubric outright.

state.addresses is left pristine: the book still holds only record 26, so
/customer/address/new/ renders both the #primary_billing and #primary_shipping
checkboxes UNCHECKED (AddressEditPage.jsx:14 isOnly is false for a create, and
lines 30-31 default both flags to false when the book is non-empty). Nothing in
the rubric is pre-satisfied.

Written as a read-modify-write: GET /go, mutate the whole document, POST it
back with action "set". Self-contained: standard library plus requests, which
is present in cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url_placeholder}"

# Raw string: order records store `street` as a single string in the
# sales_order_address convention (firstname/lastname/street/city/region/
# postcode/country_id/telephone/company/email), which is exactly what the
# 37 seeded orders carry and what OrderAddressCard renders.
ORDER_ADDRESSES = json.loads(r"""
{addr_json}
""")


def main():
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

    orders = state.get("orders")
    if not isinstance(orders, list) or len(orders) < 37:
        print("SETUP FAILED: seeded order list not readable", file=sys.stderr)
        raise SystemExit(1)

    patched = set()
    for order in orders:
        if not isinstance(order, dict):
            continue
        key = str(order.get("entityId"))
        replacement = ORDER_ADDRESSES.get(key)
        if replacement is None:
            continue
        order["shippingAddress"] = json.loads(json.dumps(replacement))
        order["billingAddress"] = json.loads(json.dumps(replacement))
        patched.add(key)

    missing = sorted(set(ORDER_ADDRESSES) - patched)
    if missing:
        print("SETUP FAILED: order ids not found: %s" % ",".join(missing),
              file=sys.stderr)
        raise SystemExit(1)

    state["orders"] = orders

    post = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    post.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    verified = check.json()
    if verified.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if verified.get("initial_state") != verified.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set",
              file=sys.stderr)
        raise SystemExit(1)
    current = verified.get("current_state") or {{}}
    book = current.get("addresses")
    if not isinstance(book, list) or len(book) != 1:
        print("SETUP FAILED: address book is not the single seeded record",
              file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


main()
'''


def setup_py(t, task_id):
    street, city, region, postcode, phone = TARGETS[t["n"]]
    mapping = {str(t["order"]): addr_obj(TARGETS[t["n"]])}
    offset = (t["n"] * 3) % len(DECOYS)
    for i, dec in enumerate(t["decoys"]):
        mapping[str(dec)] = addr_obj(DECOYS[(offset + i) % len(DECOYS)])
    return SETUP_TEMPLATE.format(
        task_id=task_id,
        inc=t["inc"],
        ordinal=t["ordinal"],
        street=street,
        city=city,
        decoy_list=", ".join("%09d" % d for d in t["decoys"]),
        url_placeholder=URL_PLACEHOLDER,
        addr_json=json.dumps(mapping, indent=1),
    )


REPLAY_TEMPLATE = '''"""Golden replay DRAFT for {task_id}.

Draft only — the golden-browser agent owns the verified version.

Route notes read off the mock source:
  * "/" -> header account link -> /customer/account/ -> sidebar "My Orders"
    -> /sales/order/history/ (OrderHistoryPage.jsx, 10 rows per page, the
    limiter select #order-limiter offers 10/20/50 so all 37 rows fit one page).
  * the row's "View Order" link goes to /sales/order/view/order_id/<entityId>/
    where OrderViewPage.jsx renders .box-order-shipping-address.
  * sidebar "Address Book" -> /customer/address/ -> button[role=add-address]
    -> /customer/address/new/ with #firstname #lastname #telephone #street_1
    #street_2 #country #region_id #city #zip, checkboxes #primary_billing and
    #primary_shipping, and button[data-action=save-address].

Target order : {inc} ({ordinal})
Address       : {street}, {city}, {region} {postcode}, T {phone}
Defaults      : {flags}
"""

TARGET_ORDER_ENTITY_ID = {entity}
TARGET_INCREMENT_ID = "{inc}"
ADDRESS = {{
    "firstname": "Emma",
    "lastname": "Lopez",
    "telephone": "{phone}",
    "street_1": "{street}",
    "city": "{city}",
    "region": "{region}",
    "postcode": "{postcode}",
}}
SET_DEFAULT_BILLING = {b}
SET_DEFAULT_SHIPPING = {s}


def replay(page, base_url):
    page.goto(base_url + "{start}")
    # 1. reach the order grid by clicking (no typed URLs)
    page.click("text=My Account")
    page.click("text=My Orders")
    page.select_option("#order-limiter", "50")
    # 2. RETRIEVAL (R4): resolve the ordinal on the rendered grid, then open it
    row = page.locator("#my-orders-table tbody tr", has_text=TARGET_INCREMENT_ID)
    row.locator("a.action.view").click()
    # 3. read .box-order-shipping-address (values asserted above)
    page.wait_for_selector(".box-order-shipping-address address")
    # 4. ACTION (A11): create the address book entry
    page.click("text=Address Book")
    page.click("button[role=add-address]")
    page.fill("#telephone", ADDRESS["telephone"])
    page.fill("#street_1", ADDRESS["street_1"])
    page.select_option("#region_id", ADDRESS["region"])
    page.fill("#city", ADDRESS["city"])
    page.fill("#zip", ADDRESS["postcode"])
    if SET_DEFAULT_BILLING:
        page.check("#primary_billing")
    if SET_DEFAULT_SHIPPING:
        page.check("#primary_shipping")
    page.click("button[data-action=save-address]")
    page.wait_for_selector("#additional-addresses-table, .block-addresses-default")
'''


def replay_py(t, task_id):
    street, city, region, postcode, phone = TARGETS[t["n"]]
    b, s = t["flags"]
    return REPLAY_TEMPLATE.format(
        task_id=task_id, inc=t["inc"], ordinal=t["ordinal"], entity=t["order"],
        street=street, city=city, region=region, postcode=postcode, phone=phone,
        flags=flag_prose(t["flags"]), start=t["start"],
        b="True" if b else "False", s="True" if s else "False",
    )


def build():
    os.makedirs(REPLAYS, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []
    for t in TASKS:
        task_id = "order_address_into_book_%s_%03d" % (t["slug"], t["n"])
        d = os.path.join(OUT, task_id)
        os.makedirs(d, exist_ok=True)
        street, city, region, postcode, phone = TARGETS[t["n"]]
        b, s = t["flags"]

        ti = {
            "task_id": task_id,
            "task_instruction": t["instruction"],
            "app_dir": APP_DIR,
            "start_path": t["start"],
            "difficulty": "medium",
            "success_criteria": success_criteria(t),
        }
        with open(os.path.join(d, "task_instruction.json"), "w") as f:
            json.dump(ti, f, indent=2)
            f.write("\n")

        injected = [
            ("Order %s (%s) has its shippingAddress and billingAddress rewritten to "
             "%s, %s, %s %s, telephone %s. This is the derived target: on the "
             "pristine seed all 37 orders ship to the one address already in the "
             "book, so nothing would be derivable and the untouched state would "
             "score 1.0 (CORRECTIONS #66)."
             % (t["inc"], t["ordinal"], street, city, region, postcode, phone)),
            ("Four near-miss orders (entityIds %s) get four other unsaved addresses "
             "so the ordinal actually has to be resolved: an agent that opens the "
             "wrong row copies a decoy and scores 0.0."
             % ", ".join(str(x) for x in t["decoys"])),
            ("state.addresses, customer.defaultBilling and customer.defaultShipping "
             "are left exactly as seeded (record 26 only, both defaults on 26), so "
             "no part of the rubric is pre-satisfied and "
             "/customer/address/new/ renders both default checkboxes unchecked."),
        ]

        manifest = {
            "schema_version": 2,
            "task_id": task_id,
            "instruction": t["instruction"],
            "apps": [
                {
                    "name": APP_DIR,
                    "source_name": "shopping",
                    "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                    "start_path": t["start"],
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
                "style": t["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R4", "A11"],
                "skill_chain": (
                    "resolve the %s on the order grid -> save that order's shipping "
                    "address as a new address book entry with %s"
                    % (t["ordinal"], flag_prose(t["flags"]))
                ),
                "derived_from": t["derived_from"],
                "official_analogues": t["analogues"],
                "topic": "shopping storefront order history and address book",
                "lane": "order_address_into_book",
                "inspiration_ids": [
                    "webarena-571", "webarena-572", "webarena-573", "webarena-574",
                    "webarena-575", "webarena-794", "webarena-795", "webarena-796",
                    "webarena-798", "webarena-231", "webarena-232", "webarena-233",
                ],
                "injected_preconditions": injected,
                "authoring_notes": [
                    "Writer: saveAddress, AppContext.jsx:461-489 - appends to "
                    "state.addresses using nextAddressId (27 on the pristine seed), "
                    "bumps nextAddressId, and on a true default flag sets "
                    "customer.defaultBilling/defaultShipping and clears that flag "
                    "on every other row.",
                    "Reader: AddressBookPage.jsx:11-13 renders Default Billing, "
                    "Default Shipping and the Additional Address Entries table "
                    "straight out of state.addresses plus customer.defaultBilling / "
                    "customer.defaultShipping; AccountDashboard.jsx:13-14 reads the "
                    "same two keys. The written key and the rendered key are the "
                    "same key.",
                    "Create, not edit: AddressEditPage.jsx:14 sets isOnly only when "
                    "the book has <=1 row AND an existing record is being edited, so "
                    "/customer/address/new/ still renders #primary_billing and "
                    "#primary_shipping (CORRECTIONS #65). Editing record 26 would "
                    "render a static message div instead and is pre-satisfied.",
                    "Ordinal margin: " + t["margin"],
                    "Both billingAddress and shippingAddress are set to the same "
                    "value on every injected order, matching the seed convention, so "
                    "'shipping address' is unambiguous on the order view page.",
                    "The reward normalises street across the list/newline/one-line "
                    "spellings, casefolds city, region and postcode, and compares "
                    "telephone on digits only; countryId and the pre-filled "
                    "firstname/lastname are deliberately not scored.",
                ],
            },
        }
        with open(os.path.join(d, "task.json"), "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")

        with open(os.path.join(d, "reward.py"), "w") as f:
            f.write(reward_py(t, task_id))
        with open(os.path.join(d, "nemo_reward.py"), "w") as f:
            f.write(nemo_reward_py(t, task_id))
        setup_src = setup_py(t, task_id)
        with open(os.path.join(d, "initial_setup.py"), "w") as f:
            f.write(setup_src)

        row = {
            "task_payload": {
                "task_id": task_id,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": [APP_DIR],
                "start_urls": [],
                "intent": t["instruction"],
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": task_id,
                    "app_dir": APP_DIR,
                    "initial_setup": setup_src,
                    "eval_reward_code": nemo_reward_py(t, task_id),
                },
            }
        }
        with open(os.path.join(d, "nemo_task.json"), "w") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
        rows.append(row)

        with open(os.path.join(REPLAYS, task_id + ".py"), "w") as f:
            f.write(replay_py(t, task_id))

        index["tasks"].append({"task_id": task_id, "path": "%s/task.json" % task_id})
        t["_id"] = task_id

    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(rows))


if __name__ == "__main__":
    build()
