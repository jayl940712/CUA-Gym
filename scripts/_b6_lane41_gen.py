#!/usr/bin/env python3
"""Batch-6 lane 41 generator - shopping, R9 -> A11.

Emits ten bundles under output/tasks/shopping/<task_id>/ plus the lane
directory output/tasks/shopping/_batches/named_order_address_correct/.

Chain: read the billing or shipping address off the order named by its
increment id, then correct the address-book record to it.

A placed order's address is NOT editable on the storefront (the only writer of
`orders` is placeOrder, AppContext.jsx:588, which prepends; nothing mutates an
existing order), which webarena-794's own note confirms.  A11 therefore lands
on saveAddress (AppContext.jsx:461).
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(ROOT, "output", "tasks", "shopping")
LANE_DIR = os.path.join(TASKS_DIR, "_batches", "named_order_address_correct")
REPLAY_DIR = os.path.join(LANE_DIR, "replays")

APP = "webarena_shopping_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

SEED_26 = {
    "id": 26,
    "firstname": "Emma",
    "lastname": "Lopez",
    "company": None,
    "street": ["101 S San Mateo Dr"],
    "city": "San Mateo",
    "region": "California",
    "regionId": 12,
    "postcode": "94010",
    "countryId": "US",
    "country": "United States",
    "telephone": "6505551212",
    "isDefaultBilling": True,
    "isDefaultShipping": True,
}

SEED_ORDER_ADDRESS = {
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


def order_address(firstname="Emma", lastname="Lopez", street="", city="", region="",
                  postcode="", telephone="", company=None):
    return {
        "firstname": firstname,
        "lastname": lastname,
        "street": street,
        "city": city,
        "region": region,
        "postcode": postcode,
        "country_id": "US",
        "telephone": telephone,
        "company": company,
        "email": None,
    }


def book_address(address_id, street, city, region, region_id, postcode, telephone,
                 firstname="Emma", lastname="Lopez", company=None,
                 billing=False, shipping=False):
    return {
        "id": address_id,
        "firstname": firstname,
        "lastname": lastname,
        "company": company,
        "street": street,
        "city": city,
        "region": region,
        "regionId": region_id,
        "postcode": postcode,
        "countryId": "US",
        "country": "United States",
        "telephone": telephone,
        "isDefaultBilling": billing,
        "isDefaultShipping": shipping,
    }


HELPERS = r'''
def _norm(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int):
        return str(value)
    return ""


def _street(row):
    raw = row.get("street")
    if isinstance(raw, list):
        parts = raw
    elif isinstance(raw, str):
        parts = raw.split("\n")
    else:
        parts = []
    out = []
    for part in parts:
        text = _norm(part)
        if text:
            out.append(text)
    return out


def _rows(state):
    rows = state.get("addresses")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _ids(state):
    out = []
    for row in _rows(state):
        try:
            out.append(int(row.get("id")))
        except (TypeError, ValueError):
            out.append(-1)
    return sorted(out)


def _by_id(state, address_id):
    for row in _rows(state):
        try:
            if int(row.get("id")) == address_id:
                return row
        except (TypeError, ValueError):
            continue
    return {}


def _other(state):
    """The single address-book record that is not the seeded id 26."""
    found = []
    for row in _rows(state):
        try:
            if int(row.get("id")) != 26:
                found.append(row)
        except (TypeError, ValueError):
            found.append(row)
    if len(found) == 1:
        return found[0]
    return {}


def _customer(state):
    customer = state.get("customer")
    return customer if isinstance(customer, dict) else {}


def _seeded_26(state):
    row = _by_id(state, 26)
    return (
        _street(row) == ["101 S San Mateo Dr"]
        and _norm(row.get("city")) == "San Mateo"
        and _norm(row.get("region")) == "California"
        and _norm(row.get("postcode")) == "94010"
        and _norm(row.get("telephone")) == "6505551212"
    )


def _record(row):
    """One address-book row normalised to a comparable tuple."""
    try:
        row_id = int(row.get("id"))
    except (TypeError, ValueError):
        row_id = -1
    return (
        row_id,
        _norm(row.get("firstname")),
        _norm(row.get("lastname")),
        _norm(row.get("company")),
        tuple(_street(row)),
        _norm(row.get("city")),
        _norm(row.get("region")),
        _norm(row.get("postcode")),
        _norm(row.get("telephone")),
        row.get("isDefaultBilling") is True,
        row.get("isDefaultShipping") is True,
    )


def _book(state):
    """The exact resulting address book, ids included."""
    return sorted(_record(row) for row in _rows(state))


def _book_new(state):
    """The exact resulting address book with agent-minted ids canonicalised.

    A record the agent creates gets whatever id nextAddressId hands out, so its
    id carries no ground truth; every other field of every record still does.
    """
    out = []
    for row in _rows(state):
        record = _record(row)
        if record[0] != 26:
            record = (-1,) + record[1:]
        out.append(record)
    return sorted(out)


def _fields(row, street, city, region, postcode, telephone):
    return (
        _street(row) == street
        and _norm(row.get("city")) == city
        and _norm(row.get("region")) == region
        and _norm(row.get("postcode")) == postcode
        and _norm(row.get("telephone")) == telephone
    )
'''

REWARD_HEAD = '''"""Deterministic reward for {task_id}.

Success criteria:
{criteria_block}

Only user-visible persisted state is inspected, and only `current_state`.
Ground truth is fixed by the frozen seed of webarena_shopping_mock in ./hub/
plus this bundle's own initial_setup.py.  Gated on the recorded VALUE, never on
"the record was edited": saveAddress (src/context/AppContext.jsx:461) writes
`state.addresses` and `state.customer.defaultBilling` / `defaultShipping`
unconditionally on every save, and those are exactly the keys the Address Book
page reads back (src/pages/AddressBookPage.jsx:11-14).
"""

'''

REWARD_TAIL = '''

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


def evaluate(evidence):
    state = _state(evidence)
    checks = _checks(state)
    components = []
    for name in COMPONENT_WEIGHTS:
        satisfied = bool(checks.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if satisfied else 0.0,
            "details": {"satisfied": satisfied},
        })
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
'''

NEMO_REWARD_HEAD = '''"""NeMo-Gym reward program for {task_id}.

Implements exactly the rubric of reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

'''

NEMO_REWARD_TAIL = '''

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
        state = response.json().get("current_state") or {}
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

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{rationale}

Written as a read-modify-write: GET /go?sid= returns the whole current state
document, the orders array (and, where needed, the address book) is mutated in
place, and the COMPLETE document is POSTed back.  That is correct whether the
state API merges or replaces, and it cannot silently truncate the 15-key state.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

# Raw string so no backslash escape is eaten by the Python parser before
# json.loads sees it: order addresses store `street` as a single newline-joined
# string, exactly as placeOrder writes it (AppContext.jsx:530).
ORDER_PATCH = json.loads(r"""
{order_patch}
""")

ADDRESS_PATCH = json.loads(r"""
{address_patch}
""")


def fail(message):
    print("SETUP FAILED: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    state = response.json().get("current_state")
    if not isinstance(state, dict):
        fail("/go returned no current_state")

    orders = state.get("orders")
    if not isinstance(orders, list) or len(orders) < 37:
        fail("seeded order list not readable")

    patched = 0
    for order in orders:
        if not isinstance(order, dict):
            continue
        key = str(order.get("entityId"))
        if key in ORDER_PATCH:
            order["billingAddress"] = ORDER_PATCH[key]["billingAddress"]
            order["shippingAddress"] = ORDER_PATCH[key]["shippingAddress"]
            patched += 1
    if patched != len(ORDER_PATCH):
        fail("expected to patch %d orders, patched %d" % (len(ORDER_PATCH), patched))
    state["orders"] = orders

    if ADDRESS_PATCH.get("addresses") is not None:
        state["addresses"] = ADDRESS_PATCH["addresses"]
        state["nextAddressId"] = ADDRESS_PATCH["nextAddressId"]
        customer = state.get("customer")
        if not isinstance(customer, dict):
            fail("customer record not readable")
        customer["defaultBilling"] = ADDRESS_PATCH["defaultBilling"]
        customer["defaultShipping"] = ADDRESS_PATCH["defaultShipping"]
        state["customer"] = customer

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    posted.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        fail("state_diff is not empty after set")
    if payload.get("initial_state") != payload.get("current_state"):
        fail("initial_state != current_state after set")
    print("SETUP OK")


main()
'''


# --------------------------------------------------------------------------
# The ten tasks
# --------------------------------------------------------------------------

def T(**kw):
    return kw


TASKS = []

# ---- 001 -----------------------------------------------------------------
A176 = order_address(street="1420 SE Ankeny St\nApt 5", city="Portland",
                     region="Oregon", postcode="97214", telephone="5035550137")
TASKS.append(T(
    id="named_order_address_correct_portland_move_from_order_176_001",
    style="terse",
    start_path="/",
    instruction=(
        "My address book still shows my old San Mateo address. Order 000000176 went to "
        "the place I live now - update the entry to match that order's shipping address "
        "exactly, phone number included."
    ),
    criteria=[
        'Address record 26 normalises to street ["1420 SE Ankeny St", "Apt 5"], city "Portland", region "Oregon", postcode "97214".',
        'state.addresses is exactly one record: id 26, Emma Lopez, no company, street ["1420 SE Ankeny St", "Apt 5"], San Mateo replaced by city "Portland", region "Oregon", postcode "97214", telephone "5035550137", both default flags true - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"176": {"billingAddress": A176, "shippingAddress": A176}},
    address_patch=None,
    rationale=(
        "Order 000000176 (page 2 of /sales/order/history/) is re-addressed to a Portland "
        "street that appears nowhere else in the corpus.  Every one of the 37 seeded "
        "orders otherwise ships to the address that is already the only record in the "
        "book (CORRECTIONS #66), so without this injection the untouched state would "
        "score 1.0 and the retrieval would be pointless."
    ),
    injected=[
        "orders: 000000176 billing and shipping address replaced with Emma Lopez, 1420 SE Ankeny St / Apt 5, Portland, Oregon, 97214, telephone 5035550137",
    ],
    weights=[("record_26_is_the_portland_address", 0.6),
             ("address_book_is_exactly_the_portland_record", 0.4)],
    checks='''    row = _by_id(state, 26)
    customer = _customer(state)
    expected = [
        (26, "Emma", "Lopez", "", ("1420 SE Ankeny St", "Apt 5"), "Portland",
         "Oregon", "97214", "5035550137", True, True),
    ]
    return {
        "record_26_is_the_portland_address": (
            _street(row) == ["1420 SE Ankeny St", "Apt 5"]
            and _norm(row.get("city")) == "Portland"
            and _norm(row.get("region")) == "Oregon"
            and _norm(row.get("postcode")) == "97214"
        ),
        "address_book_is_exactly_the_portland_record": (
            _book(state) == expected
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Change the delivery address for my most recent non canceled order to 4000 Forbes Ave, Pittsburgh, PA."],
    derived_from="address_book_move_relocate_address_on_file_001",
    chain="read the shipping address printed on the order named 000000176 -> edit the single address-book record in place to that address",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    # Order 000000176 is on page 2 of the 10-per-page history grid.
    page.click(".pages a.page:has-text('2')")
    page.click("tr:has-text('000000176') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click(".box-address-billing a.action.edit")
    page.fill("#street_1", "1420 SE Ankeny St")
    page.fill("#street_2", "Apt 5")
    page.fill("#city", "Portland")
    page.select_option("#region_id", label="Oregon")
    page.fill("#zip", "97214")
    page.fill("#telephone", "5035550137")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))

# ---- 002 -----------------------------------------------------------------
A161_BILL = order_address(street="150 Washington Ave\nSuite 210", city="Santa Fe",
                          region="New Mexico", postcode="87501",
                          telephone="5055550164", company="Harlan & Voss CPAs")
TASKS.append(T(
    id="named_order_address_correct_accountant_billing_entry_161_002",
    style="terse",
    start_path="/",
    instruction=(
        "Order 000000161 was billed to my accountant's office rather than to me. Add that "
        "billing address to my address book as a second entry and make it my default "
        "billing address. Parcels still come to San Mateo."
    ),
    criteria=[
        'A second address record exists for Emma Lopez, company "Harlan & Voss CPAs", street ["150 Washington Ave", "Suite 210"], city "Santa Fe", region "New Mexico", postcode "87501", telephone "5055550164".',
        'customer.defaultBilling is that record\'s id and its isDefaultBilling is true.',
        'state.addresses is exactly two records: record 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, isDefaultBilling false / isDefaultShipping true; plus the Santa Fe office record with isDefaultBilling true / isDefaultShipping false. customer.defaultShipping is 26.',
    ],
    order_patch={"161": {"billingAddress": A161_BILL,
                         "shippingAddress": dict(SEED_ORDER_ADDRESS)}},
    address_patch=None,
    rationale=(
        "Order 000000161 (page 1) is given a billing address that differs from its "
        "shipping address, which stays on the seeded San Mateo values.  The shipping box "
        "is therefore a live distractor: an agent that reads the wrong box on the order "
        "view copies the address it already has and scores 0.0."
    ),
    injected=[
        "orders: 000000161 billingAddress replaced with Emma Lopez, Harlan & Voss CPAs, 150 Washington Ave / Suite 210, Santa Fe, New Mexico, 87501, telephone 5055550164; its shippingAddress is left on the seeded San Mateo values as a distractor",
    ],
    weights=[("new_record_is_the_santa_fe_office", 0.5),
             ("company_recorded_and_default_billing_moved", 0.3),
             ("address_book_is_exactly_san_mateo_plus_the_santa_fe_office", 0.2)],
    checks='''    row = _other(state)
    customer = _customer(state)
    office = _fields(row, ["150 Washington Ave", "Suite 210"], "Santa Fe",
                     "New Mexico", "87501", "5055550164")
    try:
        row_id = int(row.get("id"))
    except (TypeError, ValueError):
        row_id = -1
    return {
        "new_record_is_the_santa_fe_office": office,
        "company_recorded_and_default_billing_moved": (
            office
            and _norm(row.get("company")) == "Harlan & Voss CPAs"
            and customer.get("defaultBilling") == row_id
            and row.get("isDefaultBilling") is True
        ),
        "address_book_is_exactly_san_mateo_plus_the_santa_fe_office": (
            _book_new(state) == [
                (-1, "Emma", "Lopez", "Harlan & Voss CPAs",
                 ("150 Washington Ave", "Suite 210"), "Santa Fe", "New Mexico",
                 "87501", "5055550164", True, False),
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", False, True),
            ]
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "I recently moved, my address is 231 Willow Way, Suite 100, Chicago, IL, 60601, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."],
    derived_from="address_book_move_office_billing_default_005",
    chain="read the billing address printed on the order named 000000161 -> add it to the address book as a new record and make it the default billing address",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click("tr:has-text('000000161') a.action.view")
    page.wait_for_selector(".box-order-billing-address")
    page.click("a:has-text('Address Book')")
    page.click("button[role='add-address']")
    page.fill("#company", "Harlan & Voss CPAs")
    page.fill("#telephone", "5055550164")
    page.fill("#street_1", "150 Washington Ave")
    page.fill("#street_2", "Suite 210")
    page.fill("#city", "Santa Fe")
    page.select_option("#region_id", label="New Mexico")
    page.fill("#zip", "87501")
    page.check("#primary_billing")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, #additional-addresses-table")''',
))

# ---- 003 -----------------------------------------------------------------
A168 = order_address(street="101 S San Mateo Dr", city="San Mateo", region="California",
                     postcode="94402", telephone="6505551212")
TASKS.append(T(
    id="named_order_address_correct_zip_typo_from_order_168_003",
    style="explicit",
    start_path="/",
    instruction=(
        "The ZIP code saved on my address book entry is wrong. Open My Account, go to My "
        "Orders, page through to order 000000168 and open it with View Order, and read the "
        "Zip/Postal Code printed in its Shipping Address block. Then go to the Address "
        "Book, press Change Billing Address, and change only the Zip/Postal Code field to "
        "that value. Leave Street Address, City, State/Province, Phone Number and my name "
        "exactly as they are, and do not add or delete any address entry."
    ),
    criteria=[
        'Address record 26 postcode is exactly "94402".',
        'state.addresses is exactly one record: id 26, Emma Lopez, no company, street ["101 S San Mateo Dr"], city "San Mateo", region "California", postcode "94402", telephone "6505551212", both default flags true - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"168": {"billingAddress": A168, "shippingAddress": A168}},
    address_patch=None,
    rationale=(
        "Order 000000168 (page 4 of the history grid) keeps the seeded street, city, "
        "state and phone and carries a different ZIP, 94402.  That makes the ZIP the only "
        "derived value on the page and gives the correction a single unambiguous target; "
        "94402 appears nowhere else in the state, so it cannot be guessed."
    ),
    injected=[
        "orders: 000000168 billing and shipping postcode changed from 94010 to 94402, every other address field left on the seeded values",
    ],
    weights=[("zip_corrected_to_94402", 0.6),
             ("address_book_is_exactly_the_94402_san_mateo_record", 0.4)],
    checks='''    row = _by_id(state, 26)
    customer = _customer(state)
    return {
        "zip_corrected_to_94402": _norm(row.get("postcode")) == "94402",
        "address_book_is_exactly_the_94402_san_mateo_record": (
            _book(state) == [
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94402", "6505551212", True, True),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Show me the order date for order number 148."],
    derived_from="address_book_move_duplicate_zip_typo_cleanup_006",
    chain="read the Zip/Postal Code off the shipping address of the order named 000000168 -> correct that one field on the address-book record",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    # 000000168 sits on page 4 of the 10-per-page grid (37 rows).
    page.click(".pages a.page:has-text('4')")
    page.click("tr:has-text('000000168') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click(".box-address-billing a.action.edit")
    page.fill("#zip", "94402")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))

# ---- 004 -----------------------------------------------------------------
A179_SHIP = order_address(firstname="Robert", lastname="Lopez",
                          street="3711 N Campbell Ave", city="Tucson",
                          region="Arizona", postcode="85719", telephone="5205550118")
TASKS.append(T(
    id="named_order_address_correct_parents_gift_order_179_004",
    style="terse",
    start_path="/",
    instruction=(
        "Order 000000179 was a gift I sent to my parents. Add the address it shipped to "
        "into my address book exactly as printed, under their name, and leave my default "
        "billing and shipping address alone."
    ),
    criteria=[
        'A second address record exists for Robert Lopez, street ["3711 N Campbell Ave"], city "Tucson", region "Arizona", postcode "85719", telephone "5205550118", with both of its default flags false.',
        'state.addresses is exactly two records: the Tucson record above with both default flags false, plus record 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, both default flags true - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"179": {"billingAddress": dict(SEED_ORDER_ADDRESS),
                         "shippingAddress": A179_SHIP}},
    address_patch=None,
    rationale=(
        "Order 000000179 (page 3) keeps Emma's own billing address and ships to a "
        "differently-named Tucson address.  The billing box is the distractor; the "
        "recipient name is part of the derived value, so an agent that copies only the "
        "street misses the firstname component."
    ),
    injected=[
        "orders: 000000179 shippingAddress replaced with Robert Lopez, 3711 N Campbell Ave, Tucson, Arizona, 85719, telephone 5205550118; its billingAddress stays on the seeded San Mateo values",
    ],
    weights=[("parents_record_added_with_their_name", 0.6),
             ("address_book_is_exactly_san_mateo_plus_the_tucson_record", 0.4)],
    checks='''    row = _other(state)
    customer = _customer(state)
    parents = (
        _fields(row, ["3711 N Campbell Ave"], "Tucson", "Arizona", "85719",
                "5205550118")
        and _norm(row.get("firstname")) == "Robert"
        and _norm(row.get("lastname")) == "Lopez"
    )
    return {
        "parents_record_added_with_their_name": parents,
        "address_book_is_exactly_san_mateo_plus_the_tucson_record": (
            _book_new(state) == [
                (-1, "Robert", "Lopez", "", ("3711 N Campbell Ave",), "Tucson",
                 "Arizona", "85719", "5205550118", False, False),
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", True, True),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Get the shipping method for order number 187."],
    derived_from="address_book_move_ship_cart_to_relatives_008",
    chain="read the shipping address printed on the order named 000000179 -> add it to the address book as a non-default second record",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click(".pages a.page:has-text('3')")
    page.click("tr:has-text('000000179') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click("button[role='add-address']")
    page.fill("#firstname", "Robert")
    page.fill("#lastname", "Lopez")
    page.fill("#telephone", "5205550118")
    page.fill("#street_1", "3711 N Campbell Ave")
    page.fill("#city", "Tucson")
    page.select_option("#region_id", label="Arizona")
    page.fill("#zip", "85719")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, #additional-addresses-table")''',
))

# ---- 005 -----------------------------------------------------------------
A163 = order_address(street="2870 W State St", city="Boise", region="Idaho",
                     postcode="83702", telephone="2085550172")
BOISE_STALE = book_address(27, ["1409 W Bannock St"], "Boise", "Idaho", 22,
                           "83702", "2085550172")
TASKS.append(T(
    id="named_order_address_correct_boise_street_fix_order_163_005",
    style="terse",
    start_path="/",
    instruction=(
        "The Boise entry in my address book has the wrong street on it. Order 000000163 "
        "went to the right one - fix that entry to match, and leave the rest of the entry "
        "and my defaults as they are."
    ),
    criteria=[
        'The Boise address record (id 27) street normalises to exactly ["2870 W State St"].',
        'state.addresses is exactly two records: id 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, both default flags true; and id 27, Emma Lopez, no company, ["2870 W State St"], Boise, Idaho, 83702, 2085550172, both default flags false - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"163": {"billingAddress": A163, "shippingAddress": A163}},
    address_patch={"addresses": [dict(SEED_26), BOISE_STALE], "nextAddressId": 28,
                   "defaultBilling": 26, "defaultShipping": 26},
    rationale=(
        "A second, non-default Boise record is planted with a street that no order uses, "
        "and order 000000163 (page 2) is re-addressed to the corrected Boise street.  The "
        "planted record is what makes the Address Book page show two entries, so the "
        "default checkboxes render on the edit form (AddressEditPage.jsx:14 isOnly is "
        "false with two records) and the agent must leave them alone."
    ),
    injected=[
        "addresses: seeded record 26 kept as both defaults, plus non-default record 27 Emma Lopez, 1409 W Bannock St, Boise, Idaho, 83702, telephone 2085550172; nextAddressId 28",
        "orders: 000000163 billing and shipping address replaced with 2870 W State St, Boise, Idaho, 83702, telephone 2085550172",
    ],
    weights=[("boise_street_corrected", 0.6),
             ("address_book_is_exactly_san_mateo_plus_the_west_state_st_record", 0.4)],
    checks='''    row = _by_id(state, 27)
    customer = _customer(state)
    return {
        "boise_street_corrected": _street(row) == ["2870 W State St"],
        "address_book_is_exactly_san_mateo_plus_the_west_state_st_record": (
            _book(state) == [
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", True, True),
                (27, "Emma", "Lopez", "", ("2870 W State St",), "Boise", "Idaho",
                 "83702", "2085550172", False, False),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Change the delivery address for my oldest order in 2023 to 155 5th Street, San Francisco, CA."],
    derived_from="address_book_move_unit_number_and_mobile_007",
    chain="read the street line off the shipping address of the order named 000000163 -> correct the street on the matching address-book record",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click(".pages a.page:has-text('2')")
    page.click("tr:has-text('000000163') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click("#additional-addresses-table tr:has-text('Boise') a.action.edit")
    page.fill("#street_1", "2870 W State St")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, #additional-addresses-table")''',
))

# ---- 006 -----------------------------------------------------------------
A158 = order_address(street="101 S San Mateo Dr\nSuite 310", city="San Mateo",
                     region="California", postcode="94010", telephone="6505551212",
                     company="Lopez Design Co.")
TASKS.append(T(
    id="named_order_address_correct_company_and_suite_order_158_006",
    style="terse",
    start_path="/",
    instruction=(
        "My address book entry is missing the company name and the suite line that order "
        "000000158 shipped with. Add both of those to the entry, copied exactly, and leave "
        "everything else on it unchanged."
    ),
    criteria=[
        'Address record 26 carries company "Lopez Design Co." and street ["101 S San Mateo Dr", "Suite 310"].',
        'state.addresses is exactly one record: id 26, Emma Lopez, company "Lopez Design Co.", street ["101 S San Mateo Dr", "Suite 310"], city "San Mateo", region "California", postcode "94010", telephone "6505551212", both default flags true - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"158": {"billingAddress": A158, "shippingAddress": A158}},
    address_patch=None,
    rationale=(
        "Order 000000158 (page 1) keeps the seeded street, city, state, ZIP and phone and "
        "adds a company line and a second street line.  The two added strings are the only "
        "derived values; neither exists anywhere else in the state."
    ),
    injected=[
        "orders: 000000158 billing and shipping address gains company 'Lopez Design Co.' and street line 2 'Suite 310'; all other fields stay on the seeded values",
    ],
    weights=[("company_and_suite_added", 0.6),
             ("address_book_is_exactly_the_suite_310_record", 0.4)],
    checks='''    row = _by_id(state, 26)
    customer = _customer(state)
    added = (
        _norm(row.get("company")) == "Lopez Design Co."
        and _street(row) == ["101 S San Mateo Dr", "Suite 310"]
    )
    return {
        "company_and_suite_added": added,
        "address_book_is_exactly_the_suite_310_record": (
            _book(state) == [
                (26, "Emma", "Lopez", "Lopez Design Co.",
                 ("101 S San Mateo Dr", "Suite 310"), "San Mateo", "California",
                 "94010", "6505551212", True, True),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Get the shipping method for order number 187."],
    derived_from="account_and_newsletter_studio_address_from_order_006",
    chain="read the company line and second street line off the order named 000000158 -> add both to the address-book record",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click("tr:has-text('000000158') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click(".box-address-billing a.action.edit")
    page.fill("#company", "Lopez Design Co.")
    page.fill("#street_2", "Suite 310")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))

# ---- 007 -----------------------------------------------------------------
A154 = order_address(street="905 W Riverside Ave\nApt 12", city="Spokane",
                     region="Washington", postcode="99201", telephone="5095550188")
SPOKANE_STALE = book_address(27, ["905 W Riverside Ave", "Apt 12"], "Spokane",
                             "Washington", 62, "99201", "5095550110")
TASKS.append(T(
    id="named_order_address_correct_spokane_phone_order_154_007",
    style="terse",
    start_path="/sales/order/history/",
    instruction=(
        "The Spokane entry in my address book still carries an old phone number. Order "
        "000000154 went out with my current one - correct that entry so the phone matches, "
        "and change nothing else."
    ),
    criteria=[
        'The Spokane address record (id 27) telephone is exactly "5095550188".',
        'state.addresses is exactly two records: id 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, both default flags true; and id 27, Emma Lopez, no company, ["905 W Riverside Ave", "Apt 12"], Spokane, Washington, 99201, telephone "5095550188", both default flags false - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"154": {"billingAddress": A154, "shippingAddress": A154}},
    address_patch={"addresses": [dict(SEED_26), SPOKANE_STALE], "nextAddressId": 28,
                   "defaultBilling": 26, "defaultShipping": 26},
    rationale=(
        "The planted Spokane record matches order 000000154 (page 2) on every field except "
        "the telephone, so the only thing the order tells the agent is the phone number.  "
        "5095550188 and the stale 5095550110 differ in their last four digits, which is a "
        "clean read off the order view's `T:` line."
    ),
    injected=[
        "addresses: seeded record 26 kept as both defaults, plus non-default record 27 Emma Lopez, 905 W Riverside Ave / Apt 12, Spokane, Washington, 99201 with the STALE telephone 5095550110; nextAddressId 28",
        "orders: 000000154 billing and shipping address set to the same Spokane address with the CURRENT telephone 5095550188",
    ],
    weights=[("spokane_phone_updated", 0.6),
             ("address_book_is_exactly_san_mateo_plus_the_5095550188_spokane_record", 0.4)],
    checks='''    row = _by_id(state, 27)
    customer = _customer(state)
    return {
        "spokane_phone_updated": _norm(row.get("telephone")) == "5095550188",
        "address_book_is_exactly_san_mateo_plus_the_5095550188_spokane_record": (
            _book(state) == [
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", True, True),
                (27, "Emma", "Lopez", "", ("905 W Riverside Ave", "Apt 12"),
                 "Spokane", "Washington", "99201", "5095550188", False, False),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Tell me the email address, name, phone number of the customer who has the most cancellations in the history"],
    derived_from="account_and_newsletter_phone_from_order_007",
    chain="read the telephone printed on the order named 000000154 -> correct the phone number on the matching address-book record",
    replay='''    page.goto(base_url + "/sales/order/history/")
    page.click(".pages a.page:has-text('2')")
    page.click("tr:has-text('000000154') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click("#additional-addresses-table tr:has-text('Spokane') a.action.edit")
    page.fill("#telephone", "5095550188")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, #additional-addresses-table")''',
))

# ---- 008 -----------------------------------------------------------------
A172 = order_address(street="612 Williamson St", city="Madison", region="Wisconsin",
                     postcode="53703", telephone="6085550193")
TASKS.append(T(
    id="named_order_address_correct_madison_new_default_order_172_008",
    style="explicit",
    start_path="/",
    instruction=(
        "I have moved to the place order 000000172 was delivered to. From My Account open "
        "My Orders, page through to order 000000172, open it with View Order and read its "
        "Shipping Address block. Then go to the Address Book, press Add New Address, and "
        "enter that street, city, State/Province, Zip/Postal Code and Phone Number exactly "
        "as the order prints them, keeping First Name Emma and Last Name Lopez. Tick both "
        "'Use as my default billing address' and 'Use as my default shipping address', "
        "then save. Keep the San Mateo entry in the book."
    ),
    criteria=[
        'A second address record exists for Emma Lopez, street ["612 Williamson St"], city "Madison", region "Wisconsin", postcode "53703", telephone "6085550193".',
        'customer.defaultBilling and customer.defaultShipping are both that record\'s id and both of its default flags are true.',
        'state.addresses is exactly two records: the Madison record above with both default flags true, plus record 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, with both default flags now false.',
    ],
    order_patch={"172": {"billingAddress": A172, "shippingAddress": A172}},
    address_patch=None,
    rationale=(
        "Order 000000172 (page 3, a canceled order, so it is not reachable by any "
        "'most recent order' shortcut) is re-addressed to a Madison street that exists "
        "nowhere else.  Adding rather than editing keeps the default checkboxes on the "
        "form: AddressEditPage.jsx:14 makes isOnly false for /customer/address/new/ even "
        "on a one-record book, because it also requires an existing record."
    ),
    injected=[
        "orders: 000000172 billing and shipping address replaced with Emma Lopez, 612 Williamson St, Madison, Wisconsin, 53703, telephone 6085550193",
    ],
    weights=[("madison_record_created", 0.5),
             ("both_defaults_moved_to_it", 0.3),
             ("address_book_is_exactly_demoted_san_mateo_plus_the_madison_record", 0.2)],
    checks='''    row = _other(state)
    customer = _customer(state)
    madison = _fields(row, ["612 Williamson St"], "Madison", "Wisconsin", "53703",
                      "6085550193")
    try:
        row_id = int(row.get("id"))
    except (TypeError, ValueError):
        row_id = -1
    return {
        "madison_record_created": (
            madison
            and _norm(row.get("firstname")) == "Emma"
            and _norm(row.get("lastname")) == "Lopez"
        ),
        "both_defaults_moved_to_it": (
            madison
            and customer.get("defaultBilling") == row_id
            and customer.get("defaultShipping") == row_id
            and row.get("isDefaultBilling") is True
            and row.get("isDefaultShipping") is True
        ),
        "address_book_is_exactly_demoted_san_mateo_plus_the_madison_record": (
            _book_new(state) == [
                (-1, "Emma", "Lopez", "", ("612 Williamson St",), "Madison",
                 "Wisconsin", "53703", "6085550193", True, True),
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", False, False),
            ]
        ),
    }''',
    analogues=["I recently moved, my address is 231 Willow Way, Suite 100, Chicago, IL, 60601, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
               "Show me the billing address for order number 00178."],
    derived_from="account_and_newsletter_chicago_move_keeps_phone_003",
    chain="read the shipping address printed on the order named 000000172 -> create that address-book record and make it the default for billing and shipping",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click(".pages a.page:has-text('3')")
    page.click("tr:has-text('000000172') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click("button[role='add-address']")
    page.fill("#telephone", "6085550193")
    page.fill("#street_1", "612 Williamson St")
    page.fill("#city", "Madison")
    page.select_option("#region_id", label="Wisconsin")
    page.fill("#zip", "53703")
    page.check("#primary_billing")
    page.check("#primary_shipping")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))

# ---- 009 -----------------------------------------------------------------
A187_BILL = order_address(street="44 Pearl St\nUnit 2", city="Burlington",
                          region="Vermont", postcode="05401", telephone="8025550126")
TASKS.append(T(
    id="named_order_address_correct_burlington_billing_order_187_009",
    style="terse",
    start_path="/",
    instruction=(
        "Order 000000187 is billed to where I actually live now, even though it ships "
        "somewhere else. Replace my address book entry with that order's billing address, "
        "phone number included."
    ),
    criteria=[
        'Address record 26 normalises to street ["44 Pearl St", "Unit 2"], city "Burlington", region "Vermont", postcode "05401".',
        'state.addresses is exactly one record: id 26, Emma Lopez, no company, street ["44 Pearl St", "Unit 2"], city "Burlington", region "Vermont", postcode "05401", telephone "8025550126", both default flags true - and customer.defaultBilling and customer.defaultShipping are both 26.',
    ],
    order_patch={"187": {"billingAddress": A187_BILL,
                         "shippingAddress": dict(SEED_ORDER_ADDRESS)}},
    address_patch=None,
    rationale=(
        "Order 000000187 is one of the three pending orders that all render 5/2/23 and "
        "differ only by increment id, so naming the increment id is the only way to "
        "resolve it - and the instruction does exactly that.  Its shipping address stays "
        "on the seeded San Mateo values, so the shipping box is a distractor that scores "
        "0.0 if copied."
    ),
    injected=[
        "orders: 000000187 billingAddress replaced with Emma Lopez, 44 Pearl St / Unit 2, Burlington, Vermont, 05401, telephone 8025550126; its shippingAddress stays on the seeded San Mateo values as a distractor",
    ],
    weights=[("record_26_is_the_burlington_address", 0.6),
             ("address_book_is_exactly_the_burlington_record", 0.4)],
    checks='''    row = _by_id(state, 26)
    customer = _customer(state)
    return {
        "record_26_is_the_burlington_address": (
            _street(row) == ["44 Pearl St", "Unit 2"]
            and _norm(row.get("city")) == "Burlington"
            and _norm(row.get("region")) == "Vermont"
            and _norm(row.get("postcode")) == "05401"
        ),
        "address_book_is_exactly_the_burlington_record": (
            _book(state) == [
                (26, "Emma", "Lopez", "", ("44 Pearl St", "Unit 2"), "Burlington",
                 "Vermont", "05401", "8025550126", True, True),
            ]
            and customer.get("defaultBilling") == 26
            and customer.get("defaultShipping") == 26
        ),
    }''',
    analogues=["Show me the billing address for order number 00178.",
               "Get the order number of my most recent pending order"],
    derived_from="address_book_move_order_destination_relocation_002",
    chain="read the billing address printed on the order named 000000187 -> replace the single address-book record with it",
    replay='''    page.goto(base_url + "/")
    page.click("li.link.my-account a, a:has-text('My Account')")
    page.click("a:has-text('My Orders')")
    page.click("tr:has-text('000000187') a.action.view")
    page.wait_for_selector(".box-order-billing-address")
    page.click("a:has-text('Address Book')")
    page.click(".box-address-billing a.action.edit")
    page.fill("#street_1", "44 Pearl St")
    page.fill("#street_2", "Unit 2")
    page.fill("#city", "Burlington")
    page.select_option("#region_id", label="Vermont")
    page.fill("#zip", "05401")
    page.fill("#telephone", "8025550126")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))

# ---- 010 ----------------------------------------------------------------
A165 = order_address(street="18 Broadway St\nApt 3B", city="Asheville",
                     region="North Carolina", postcode="28801", telephone="8285550164")
ASHEVILLE_STALE = book_address(27, ["18 Broadway St", "Apt 3B"], "Asheville",
                               "North Carolina", 44, "28801", "8285550119")
TASKS.append(T(
    id="named_order_address_correct_asheville_promote_order_165_010",
    style="explicit",
    start_path="/customer/address/",
    instruction=(
        "I now live at the Asheville entry in my address book, and its phone number is out "
        "of date. Open My Orders, find order 000000165, open it with View Order and read "
        "the phone number printed under its Shipping Address. Then come back to the "
        "Address Book, press Edit on the Asheville entry, replace the Phone Number with "
        "that one, tick both 'Use as my default billing address' and 'Use as my "
        "default shipping address', and save. Leave the street, city, state and ZIP "
        "as they are, "
        "and keep the San Mateo entry in the book."
    ),
    criteria=[
        'The Asheville address record (id 27) telephone is exactly "8285550164".',
        'state.addresses is exactly two records: id 26, Emma Lopez, no company, "101 S San Mateo Dr", San Mateo, California, 94010, 6505551212, with both default flags now false; and id 27, Emma Lopez, no company, ["18 Broadway St", "Apt 3B"], Asheville, North Carolina, 28801, telephone "8285550164", with both default flags true - and customer.defaultBilling and customer.defaultShipping are both 27.',
    ],
    order_patch={"165": {"billingAddress": A165, "shippingAddress": A165}},
    address_patch={"addresses": [dict(SEED_26), ASHEVILLE_STALE], "nextAddressId": 28,
                   "defaultBilling": 26, "defaultShipping": 26},
    rationale=(
        "With two records in the book AddressEditPage.jsx:14 evaluates isOnly false, so "
        "both default checkboxes render on the edit form for record 27 - the CORRECTIONS "
        "#65 trap (a one-record book replaces both checkboxes with a static message div) "
        "does not apply here, and the injection is what makes the tick performable.  The "
        "order supplies only the phone number; everything else on the record already "
        "matches, so the retrieval has exactly one derived value."
    ),
    injected=[
        "addresses: seeded record 26 kept as both defaults, plus non-default record 27 Emma Lopez, 18 Broadway St / Apt 3B, Asheville, North Carolina, 28801 with the STALE telephone 8285550119; nextAddressId 28",
        "orders: 000000165 billing and shipping address set to the same Asheville address with the CURRENT telephone 8285550164",
    ],
    weights=[("asheville_phone_updated", 0.5),
             ("asheville_is_now_both_defaults", 0.5)],
    checks='''    row = _by_id(state, 27)
    customer = _customer(state)
    return {
        "asheville_phone_updated": _norm(row.get("telephone")) == "8285550164",
        "asheville_is_now_both_defaults": (
            _book(state) == [
                (26, "Emma", "Lopez", "", ("101 S San Mateo Dr",), "San Mateo",
                 "California", "94010", "6505551212", False, False),
                (27, "Emma", "Lopez", "", ("18 Broadway St", "Apt 3B"), "Asheville",
                 "North Carolina", "28801", "8285550164", True, True),
            ]
            and customer.get("defaultBilling") == 27
            and customer.get("defaultShipping") == 27
        ),
    }''',
    analogues=["I recently moved, my address is 654 Aspen Road, House #3, Boston, MA, 02110, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
               "Show me the billing address for order number 00178."],
    derived_from="account_and_newsletter_default_from_newest_order_002",
    chain="read the telephone printed on the order named 000000165 -> correct that phone on the matching address-book record and promote it to default billing and shipping",
    replay='''    page.goto(base_url + "/customer/address/")
    page.click("a:has-text('My Orders')")
    page.click(".pages a.page:has-text('3')")
    page.click("tr:has-text('000000165') a.action.view")
    page.wait_for_selector(".box-order-shipping-address")
    page.click("a:has-text('Address Book')")
    page.click("#additional-addresses-table tr:has-text('Asheville') a.action.edit")
    page.fill("#telephone", "8285550164")
    page.check("#primary_billing")
    page.check("#primary_shipping")
    page.click("button[data-action='save-address']")
    page.wait_for_selector(".message.success, .box-address-billing")''',
))


# --------------------------------------------------------------------------
# Emission
# --------------------------------------------------------------------------

def weights_block(weights):
    lines = ["COMPONENT_WEIGHTS = {"]
    for name, value in weights:
        lines.append('    "%s": %s,' % (name, value))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    return "\n".join(lines)


def checks_block(task):
    return "def _checks(state):\n" + task["checks"] + "\n"


def write(path, text):
    with open(path, "w") as handle:
        handle.write(text)


def build():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []

    for task in TASKS:
        tid = task["id"]
        bundle = os.path.join(TASKS_DIR, tid)
        os.makedirs(bundle, exist_ok=True)

        criteria_block = "\n".join("  * " + c for c in task["criteria"])

        core = (
            HELPERS.strip("\n")
            + "\n\n\n"
            + weights_block(task["weights"])
            + "\n\n\n"
            + checks_block(task)
        )

        reward = (
            REWARD_HEAD.format(task_id=tid, criteria_block=criteria_block)
            + core
            + REWARD_TAIL
        )
        write(os.path.join(bundle, "reward.py"), reward)

        nemo_reward = (
            NEMO_REWARD_HEAD.format(task_id=tid, url=URL_PLACEHOLDER)
            + core
            + NEMO_REWARD_TAIL
        )
        write(os.path.join(bundle, "nemo_reward.py"), nemo_reward)

        order_patch = json.dumps(task["order_patch"], indent=1, sort_keys=True)
        address_patch = json.dumps(
            task["address_patch"] if task["address_patch"] else {"addresses": None},
            indent=1, sort_keys=True)
        setup = SETUP_TEMPLATE.format(
            task_id=tid,
            rationale=task["rationale"],
            url=URL_PLACEHOLDER,
            order_patch=order_patch,
            address_patch=address_patch,
        )
        write(os.path.join(bundle, "initial_setup.py"), setup)

        instruction = {
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP,
            "start_path": task["start_path"],
            "difficulty": "medium",
            "success_criteria": task["criteria"],
        }
        write(os.path.join(bundle, "task_instruction.json"),
              json.dumps(instruction, indent=2) + "\n")

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
            "apps": [{
                "name": APP,
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                "start_path": task["start_path"],
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
                "skills": ["R9", "A11"],
                "skill_chain": task["chain"],
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "injected_preconditions": task["injected"],
                "lane": "named_order_address_correct",
                "batch": 6,
                "topic": "shopping storefront: correcting the address book from an order named by increment id",
                "inspiration_ids": ["webarena-362", "webarena-358", "webarena-571", "webarena-794"],
                "authoring_notes": [
                    "A placed order's address is NOT editable on the storefront: the only writer of state.orders is placeOrder (src/context/AppContext.jsx:588), which prepends a new order and never mutates an existing one. webarena-794's own string_note says the same. A11 therefore lands on saveAddress (src/context/AppContext.jsx:461).",
                    "Writer/reader parity checked: saveAddress writes state.addresses (AppContext.jsx:484) and customer.defaultBilling / defaultShipping (AppContext.jsx:474, :478); AddressBookPage.jsx:11-14 reads exactly those three keys back, and AddressEditPage.jsx:12 re-reads state.addresses.",
                    "Order line items are <strong>, not links (OrderViewPage.jsx:27); no step in this task needs an order-to-PDP click.",
                    "Every scored control is reachable from start_path by clicking: header top-links 'My Account' -> AccountNav (components/AccountNav.jsx:9,:14) carries 'My Orders' and 'Address Book'; the history grid's 'View Order' link is OrderHistoryPage.jsx:60 and its pager is Toolbar.Pager.",
                    "Gated on the recorded VALUE, never on 'the record was edited': saveAddress writes unconditionally on every save.",
                    "The reward reads current_state only.",
                ],
            },
        }
        write(os.path.join(bundle, "task.json"), json.dumps(manifest, indent=2) + "\n")

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP,
                "initial_setup": setup,
                "eval_reward_code": nemo_reward,
            },
        }}
        write(os.path.join(bundle, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
        rows.append(json.dumps(row))

        replay = (
            '"""Golden replay draft - %s.\n\n'
            'start_path "%s". Click-only navigation from start_path.\n'
            '"""\n\n\n'
            'def replay(page, base_url):\n%s\n'
        ) % (tid, task["start_path"], task["replay"])
        write(os.path.join(REPLAY_DIR, tid + ".py"), replay)

        index["tasks"].append({"task_id": tid, "path": "%s/task.json" % tid})

    write(os.path.join(LANE_DIR, "index.json"), json.dumps(index, indent=2) + "\n")
    write(os.path.join(LANE_DIR, "nemo_tasks.jsonl"), "\n".join(rows) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    build()
