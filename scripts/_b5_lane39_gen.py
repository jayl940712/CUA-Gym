# Authoring generator for lane 39 (shopping / address_book_move). Read-only w.r.t. hub/.
import json, os, textwrap

ROOT = "/home/ubuntu/CUA-Gym/output/tasks/shopping"
BATCH = os.path.join(ROOT, "_batches", "address_book_move")
REPLAYS = os.path.join(BATCH, "replays")
APP = "webarena_shopping_mock"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

AN_MOVE_CHI = "I recently moved, my address is 231 Willow Way, Suite 100, Chicago, IL, 60601, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."
AN_MOVE_BOS = "I recently moved, my address is 654 Aspen Road, House #3, Boston, MA, 02110, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."
AN_MOVE_PHI = "I recently moved, my address is 987 Sycamore Circle, Philadelphia, PA, 19102, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."
AN_MOVE_ATL = "I recently moved, my address is 111 Magnolia Path, Atlanta, GA, 30303, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."
AN_MOVE_SEA = "I recently moved, my address is 222 Redwood Rise, Suite 300, Seattle, WA, 98101, update my information on OneStopShopping accordingly. Make it my default shipping and billing address."
AN_DEL_OLD23 = "Change the delivery address for my oldest order in 2023 to 155 5th Street, San Francisco, CA."
AN_DEL_RECENT = "Change the delivery address for my most recent non canceled order to 4000 Forbes Ave, Pittsburgh, PA."
AN_DEL_SECOND = "Change the delivery address for my second most recent order to 6726 McPherson Blvd, Pittsburgh, PA."
AN_DEL_FIRST = "Change the delivery address for my first order ever to 3 Oxford St, Cambridge, MA."
AN_BILL_ORDER = "Show me the billing address for order number 00178."

SEED26 = {
    "id": 26, "firstname": "Emma", "lastname": "Lopez", "company": None,
    "street": ["101 S San Mateo Dr"], "city": "San Mateo", "region": "California",
    "regionId": 12, "postcode": "94010", "countryId": "US", "country": "United States",
    "telephone": "6505551212", "isDefaultBilling": True, "isDefaultShipping": True,
}


def addr(aid, street, city, region, region_id, postcode, phone,
         first="Emma", last="Lopez", company=None, billing=False, shipping=False):
    return {
        "id": aid, "firstname": first, "lastname": last, "company": company,
        "street": list(street), "city": city, "region": region, "regionId": region_id,
        "postcode": postcode, "countryId": "US", "country": "United States",
        "telephone": phone, "isDefaultBilling": billing, "isDefaultShipping": shipping,
    }


def order_addr(a):
    return {
        "firstname": a["firstname"], "lastname": a["lastname"],
        "street": "\n".join(a["street"]), "city": a["city"], "region": a["region"],
        "postcode": a["postcode"], "country_id": "US", "telephone": a["telephone"],
        "company": a["company"], "email": None,
    }


def order(entity_id, created_at, ship_addr, item_id, product_id, sku, name, price, qty=1,
          status="complete", state="complete"):
    subtotal = round(price * qty, 2)
    shipping = 5 * qty
    snap = order_addr(ship_addr)
    return {
        "entityId": entity_id,
        "incrementId": str(entity_id).zfill(9),
        "status": status,
        "state": state,
        "createdAt": created_at,
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
        "billingAddress": snap,
        "shippingAddress": snap,
        "items": [{
            "itemId": item_id, "productId": product_id, "sku": sku, "name": name,
            "price": price, "qtyOrdered": qty, "rowTotal": round(price * qty, 2),
            "productType": "simple", "options": [],
        }],
    }


LAMP = (15033, "B087QSCXGT", "Uttermost Volterra Crackled Taupe-Gray Ceramic Table Lamp", 250.8)
RACK = (15787, "B08JLHHCM6", "NOZE Rustic Coat Rack Wall Mounted Shelf with 4 Hooks, Hanging Entryway Organizer for Mug Coffee Cup, Holding Solid Wooden Shelf with 2 Baskets for Kitchen Living Room, Bathroom and Bedroom", 40.99)

# --------------------------------------------------------------------------
# Shared reward helper source (identical text in reward.py and nemo_reward.py)
# --------------------------------------------------------------------------
HELPERS = '''
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


def _customer(state):
    customer = state.get("customer")
    return customer if isinstance(customer, dict) else {}


def _addresses(state):
    rows = state.get("addresses")
    if not isinstance(rows, list):
        return []
    return [a for a in rows if isinstance(a, dict)]


def _address_ids(state):
    ids = []
    for a in _addresses(state):
        ids.append(_int(a.get("id")))
    return ids


def _address_by_id(state, address_id):
    for a in _addresses(state):
        if _int(a.get("id")) == address_id:
            return a
    return None


def _street(value):
    """Normalise a stored street to a single comma-joined string.

    The address form keeps two lines, `placeOrder` snapshots them joined by a
    newline, and a user may legitimately type the whole thing on line 1. All
    three collapse to the same canonical string here.
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
    return ", ".join(parts)


def _orders(state):
    rows = state.get("orders")
    if not isinstance(rows, list):
        return []
    return [o for o in rows if isinstance(o, dict)]


def _order_by_entity(state, entity_id):
    for o in _orders(state):
        if _int(o.get("entityId")) == entity_id:
            return o
    return None


def _cart_items(state):
    cart = state.get("cart")
    if not isinstance(cart, dict):
        return None
    items = cart.get("items")
    if not isinstance(items, list):
        return None
    return items


def _addr_matches(record, street, city, region, postcode, telephone):
    if not isinstance(record, dict):
        return False
    return (
        _street(record.get("street")) == street
        and _text(record.get("city")) == city
        and _text(record.get("region")) == region
        and _text(record.get("postcode")) == postcode
        and _text(record.get("telephone")) == telephone
        and _text(record.get("countryId")) == "US"
    )


def _order_ships_to(order, street, city, postcode, telephone):
    if not isinstance(order, dict):
        return False
    ship = order.get("shippingAddress")
    if not isinstance(ship, dict):
        return False
    return (
        _street(ship.get("street")) == street
        and _text(ship.get("city")) == city
        and _text(ship.get("postcode")) == postcode
        and _text(ship.get("telephone")) == telephone
    )


SEED_26 = {
    "street": "101 S San Mateo Dr",
    "city": "San Mateo",
    "region": "California",
    "postcode": "94010",
    "telephone": "6505551212",
}


def _seed_26_values_intact(state):
    record = _address_by_id(state, 26)
    return _addr_matches(
        record, SEED_26["street"], SEED_26["city"], SEED_26["region"],
        SEED_26["postcode"], SEED_26["telephone"],
    )
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
    try:
        checks = _checks(state)
    except Exception:
        checks = {}
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

NEMO_TAIL = '''

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


def weights_block(weights):
    lines = ["COMPONENT_WEIGHTS = {"]
    for k, v in weights.items():
        lines.append('    "%s": %s,' % (k, v))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    return "\n".join(lines)


def write_reward(path, task_id, criteria, weights, checks_src):
    doc = '"""Deterministic reward for %s.\n\nSuccess criteria:\n%s\n\nOnly `current_state` is inspected; no diff against `initial_state` is taken.\nGround truth is fixed by the frozen seed of webarena_shopping_mock in ./hub/\nplus this bundle\'s own injected precondition where one exists.\n"""\n' % (
        task_id, "\n".join("  * " + c for c in criteria))
    src = doc + HELPERS + "\n\n" + weights_block(weights) + "\n\n\n" + checks_src + REWARD_TAIL
    open(path, "w").write(src)


def write_nemo_reward(path, task_id, weights, checks_src):
    doc = '"""NeMo-Gym reward program for %s.\n\nImplements exactly the rubric of reward.py, reading `current_state` from\nGET /go?sid=... and printing REWARD: <float> on every output path.\n\nSelf-contained: standard library plus requests.\n"""\n' % task_id
    head = doc + "\nimport sys\n\nimport requests\n\nSID = \"__CUA_GYM_SID__\"\nBASE_URL = \"%s\"\n" % PLACEHOLDER
    src = head + HELPERS + "\n\n" + weights_block(weights) + "\n\n\n" + checks_src + NEMO_TAIL
    open(path, "w").write(src)


SETUP_SIMPLE = '''"""NeMo-Gym setup program for {task_id}.

{why}

The state patch below is applied with the `set` verb, which the mock merges over
`createInitialData()` at the top level (vite.config.js:441) and writes to BOTH
the current state and the /go baseline.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{placeholder}"

STATE_PATCH = json.loads(r"""
{patch}
""")


def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": STATE_PATCH}},
        timeout=60,
    )
    response.raise_for_status()
    verify()


main()
'''

SETUP_ORDERS = '''"""NeMo-Gym setup program for {task_id}.

{why}

`orders` is a whole-array top-level key and the pristine seed holds 37 rows, so
the pristine document is read back from GET /go first and the injected rows are
prepended to it before the whole tree is written with the `set` verb.

Every injected order row follows the order-injection checklist: createdAt is
later than the tenth-newest seeded order so the row lands on page 1 of
/sales/order/history/, the UTC clock is pinned to 12:00:00 so the
America/New_York rendering cannot cross a day boundary, entityId is >= 190 with
both next-counters bumped past it, line itemIds start above the seeded maximum
of 544, productIds are real catalog rows, status/state are a coherent pair, and
shippingAmount == 5 * totalQtyOrdered with grandTotal == subtotal +
shippingAmount.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{placeholder}"

FIXTURE = json.loads(r"""
{patch}
""")


def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    seed = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    seed.raise_for_status()
    state = seed.json().get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: /go returned no initial_state", file=sys.stderr)
        raise SystemExit(1)

    state["addresses"] = FIXTURE["addresses"]
    state["nextAddressId"] = FIXTURE["nextAddressId"]
    customer = state.get("customer")
    if not isinstance(customer, dict):
        print("SETUP FAILED: /go returned no customer", file=sys.stderr)
        raise SystemExit(1)
    customer["defaultBilling"] = FIXTURE["defaultBilling"]
    customer["defaultShipping"] = FIXTURE["defaultShipping"]

    existing = state.get("orders")
    if not isinstance(existing, list):
        print("SETUP FAILED: /go returned no orders", file=sys.stderr)
        raise SystemExit(1)
    state["orders"] = FIXTURE["orders"] + existing
    state["nextOrderEntityId"] = FIXTURE["nextOrderEntityId"]
    state["nextOrderIncrementId"] = FIXTURE["nextOrderIncrementId"]

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()
    verify()


main()
'''

TASKS = []

CUSTOMER_BASE = {
    "id": 27, "email": "emma.lopez@gmail.com", "firstname": "Emma", "lastname": "Lopez",
    "dob": None, "gender": None, "groupId": 1, "createdAt": "2023-04-23 16:42:28",
    "defaultBilling": 26, "defaultShipping": 26, "assistanceAllowed": False,
}


def customer(billing, shipping):
    c = dict(CUSTOMER_BASE)
    c["defaultBilling"] = billing
    c["defaultShipping"] = shipping
    return c


def seed26(billing=True, shipping=True):
    r = dict(SEED26)
    r["street"] = list(SEED26["street"])
    r["isDefaultBilling"] = billing
    r["isDefaultShipping"] = shipping
    return r


# ---------------------------------------------------------------- fixtures
A27_SF_LETTERMAN = addr(27, ["1 Letterman Dr"], "San Francisco", "California", 12, "94129", "4155550119")
A28_OAKLAND = addr(28, ["2100 Franklin St"], "Oakland", "California", 12, "94612", "5105550188")

FIX_002 = {
    "addresses": [seed26(), A27_SF_LETTERMAN, A28_OAKLAND],
    "nextAddressId": 29,
    "defaultBilling": 26,
    "defaultShipping": 26,
    "orders": [
        order(191, "2023-06-14 12:00:00", A28_OAKLAND, 901, RACK[0], RACK[1], RACK[2], RACK[3]),
        order(190, "2023-06-02 12:00:00", A27_SF_LETTERMAN, 900, LAMP[0], LAMP[1], LAMP[2], LAMP[3]),
    ],
    "nextOrderEntityId": 192,
    "nextOrderIncrementId": 192,
}

FIX_003 = {
    "addresses": [
        seed26(),
        addr(27, ["1200 Bryant St"], "Palo Alto", "California", 12, "94301", "6505550143"),
        addr(28, ["3400 N Halsted St"], "Chicago", "Illinois", 23, "60657", "7735550166"),
        addr(29, ["2100 Franklin St"], "Oakland", "California", 12, "94612", "5105550188"),
    ],
    "nextAddressId": 30,
    "customer": customer(26, 26),
}

FIX_006 = {
    "addresses": [
        seed26(),
        addr(27, ["1200 Bryant St"], "Palo Alto", "California", 12, "94301", "6505550143"),
        addr(28, ["1200 Bryant St"], "Palo Alto", "California", 12, "94031", "6505550143"),
    ],
    "nextAddressId": 29,
    "customer": customer(26, 26),
}

FIX_007 = {
    "addresses": [
        seed26(billing=True, shipping=False),
        addr(27, ["845 Market St"], "San Francisco", "California", 12, "94103", "4155550100", shipping=True),
    ],
    "nextAddressId": 28,
    "customer": customer(26, 27),
}

FIX_008 = {
    "addresses": [
        seed26(),
        addr(27, ["4820 Del Rio Rd"], "Sacramento", "California", 12, "95822", "9165550111", first="Robert"),
    ],
    "nextAddressId": 28,
    "customer": customer(26, 26),
}

FIX_009 = {
    "addresses": [
        seed26(),
        addr(27, ["600 Montgomery St"], "San Francisco", "California", 12, "94111", "4155550157"),
    ],
    "nextAddressId": 28,
    "customer": customer(26, 26),
}

A27_SEATTLE = addr(27, ["915 E Pine St"], "Seattle", "Washington", 62, "98122", "2065550134")
A28_AUSTIN = addr(28, ["1101 Red River St"], "Austin", "Texas", 57, "78701", "5125550178")

FIX_010 = {
    "addresses": [seed26(), A27_SEATTLE, A28_AUSTIN],
    "nextAddressId": 29,
    "defaultBilling": 26,
    "defaultShipping": 26,
    "orders": [
        order(191, "2023-06-21 12:00:00", A28_AUSTIN, 901, RACK[0], RACK[1], RACK[2], RACK[3]),
        order(190, "2023-06-05 12:00:00", A27_SEATTLE, 900, LAMP[0], LAMP[1], LAMP[2], LAMP[3]),
    ],
    "nextOrderEntityId": 192,
    "nextOrderIncrementId": 192,
}

CHECKS_001 = '''def _checks(state):
    record = _address_by_id(state, 26)
    customer = _customer(state)
    moved = (
        _address_ids(state) == [26]
        and _addr_matches(record, "3540 Wilshire Blvd, Suite 12", "Los Angeles",
                          "California", "90010", "6505551212")
        and _text(record.get("firstname")) == "Emma"
        and _text(record.get("lastname")) == "Lopez"
        and record.get("isDefaultBilling") is True
        and record.get("isDefaultShipping") is True
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 26
    )
    return {"address_on_file_now_los_angeles": moved}
'''

CHECKS_002 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    target = _address_by_id(state, 28)
    other = _address_by_id(state, 27)
    seed = _address_by_id(state, 26)
    customer = _customer(state)
    ids_ok = ids == [26, 27, 28]
    relocated = (
        ids_ok
        and _addr_matches(target, "812 Vermont St, Apt 3", "Los Angeles",
                          "California", "90014", "5105550188")
        and _addr_matches(other, "1 Letterman Dr", "San Francisco", "California",
                          "94129", "4155550119")
        and _seed_26_values_intact(state)
    )
    promoted = (
        ids_ok
        and isinstance(target, dict)
        and _int(customer.get("defaultBilling")) == 28
        and _int(customer.get("defaultShipping")) == 28
        and target.get("isDefaultBilling") is True
        and target.get("isDefaultShipping") is True
        and isinstance(seed, dict)
        and seed.get("isDefaultBilling") is False
        and seed.get("isDefaultShipping") is False
    )
    return {
        "order_destination_entry_now_los_angeles": relocated,
        "relocated_entry_is_both_defaults": promoted,
    }
'''

CHECKS_003 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    customer = _customer(state)
    pruned = (
        ids == [26, 27, 29]
        and _seed_26_values_intact(state)
        and _addr_matches(_address_by_id(state, 27), "1200 Bryant St", "Palo Alto",
                          "California", "94301", "6505550143")
        and _addr_matches(_address_by_id(state, 29), "2100 Franklin St", "Oakland",
                          "California", "94612", "5105550188")
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 26
    )
    return {"only_california_entries_remain": pruned}
'''

CHECKS_004 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    new = _address_by_id(state, 27)
    customer = _customer(state)
    saved = (
        ids == [26, 27]
        and _addr_matches(new, "77 Massachusetts Ave", "Cambridge", "Massachusetts",
                          "02139", "6505551212")
        and new.get("isDefaultBilling") is False
        and new.get("isDefaultShipping") is False
        and _seed_26_values_intact(state)
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 26
    )
    placed = _order_by_entity(state, 190)
    lines = []
    if isinstance(placed, dict) and isinstance(placed.get("items"), list):
        for item in placed["items"]:
            if isinstance(item, dict):
                lines.append(_int(item.get("productId")))
    shipped = (
        isinstance(placed, dict)
        and _order_ships_to(placed, "77 Massachusetts Ave", "Cambridge", "02139",
                            "6505551212")
        and _num(placed.get("grandTotal")) == 365.42
        and sorted(x for x in lines if x is not None) == [10617, 15033, 15787]
        and _cart_items(state) == []
    )
    return {
        "cambridge_entry_saved_without_defaults": saved,
        "cart_ordered_to_cambridge": shipped,
    }
'''

CHECKS_005 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    office = _address_by_id(state, 27)
    seed = _address_by_id(state, 26)
    customer = _customer(state)
    created = (
        ids == [26, 27]
        and _addr_matches(office, "425 Market St, Suite 2200", "San Francisco",
                          "California", "94105", "4155550188")
        and _text(office.get("company")) == "Vandelay Industries"
        and _seed_26_values_intact(state)
    )
    routed = (
        ids == [26, 27]
        and isinstance(office, dict)
        and isinstance(seed, dict)
        and _int(customer.get("defaultBilling")) == 27
        and _int(customer.get("defaultShipping")) == 26
        and office.get("isDefaultBilling") is True
        and office.get("isDefaultShipping") is False
        and seed.get("isDefaultBilling") is False
        and seed.get("isDefaultShipping") is True
    )
    return {
        "office_entry_created_with_company": created,
        "billing_default_moved_shipping_stayed": routed,
    }
'''

CHECKS_006 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    survivors = []
    for a in _addresses(state):
        if _int(a.get("id")) in (27, 28):
            survivors.append(a)
    kept = survivors[0] if len(survivors) == 1 else None
    deduped = (
        ids in ([26, 27], [26, 28])
        and kept is not None
        and _addr_matches(kept, "1200 Bryant St", "Palo Alto", "California",
                          "94301", "6505550143")
        and _seed_26_values_intact(state)
    )
    kept_id = _int(kept.get("id")) if isinstance(kept, dict) else None
    seed = _address_by_id(state, 26)
    customer = _customer(state)
    promoted = (
        deduped
        and _int(customer.get("defaultShipping")) == kept_id
        and kept.get("isDefaultShipping") is True
        and _int(customer.get("defaultBilling")) == 26
        and isinstance(seed, dict)
        and seed.get("isDefaultBilling") is True
        and seed.get("isDefaultShipping") is False
    )
    return {
        "wrong_zip_copy_removed": deduped,
        "correct_copy_is_default_shipping": promoted,
    }
'''

CHECKS_007 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    record = _address_by_id(state, 27)
    seed = _address_by_id(state, 26)
    customer = _customer(state)
    frame = (
        ids == [26, 27]
        and isinstance(record, dict)
        and isinstance(seed, dict)
        and _text(record.get("city")) == "San Francisco"
        and _text(record.get("region")) == "California"
        and _text(record.get("postcode")) == "94103"
        and _seed_26_values_intact(state)
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 27
        and record.get("isDefaultShipping") is True
        and record.get("isDefaultBilling") is False
        and seed.get("isDefaultBilling") is True
        and seed.get("isDefaultShipping") is False
    )
    unit = frame and _street(record.get("street")) == "845 Market St, Apt 4B"
    phone = frame and _text(record.get("telephone")) == "4155550142"
    return {
        "unit_line_added_to_default_shipping": unit,
        "phone_updated_on_default_shipping": phone,
    }
'''

CHECKS_008 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    parents = _address_by_id(state, 27)
    customer = _customer(state)
    placed = _order_by_entity(state, 190)
    ship = placed.get("shippingAddress") if isinstance(placed, dict) else None
    ok = (
        ids == [26, 27]
        and _seed_26_values_intact(state)
        and _addr_matches(parents, "4820 Del Rio Rd", "Sacramento", "California",
                          "95822", "9165550111")
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 26
        and isinstance(placed, dict)
        and isinstance(ship, dict)
        and _order_ships_to(placed, "4820 Del Rio Rd", "Sacramento", "95822",
                            "9165550111")
        and _text(ship.get("firstname")) == "Robert"
        and _num(placed.get("grandTotal")) == 365.42
        and _cart_items(state) == []
    )
    return {"cart_ordered_to_parents_address": ok}
'''

CHECKS_009 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    home = _address_by_id(state, 26)
    other = _address_by_id(state, 27)
    customer = _customer(state)
    denver = (
        ids == [26, 27]
        and _addr_matches(home, "1550 Wewatta St, Unit 710", "Denver", "Colorado",
                          "80202", "6505551212")
        and home.get("isDefaultBilling") is True
        and home.get("isDefaultShipping") is True
        and _int(customer.get("defaultBilling")) == 26
        and _int(customer.get("defaultShipping")) == 26
    )
    placed = _order_by_entity(state, 190)
    shipped = (
        isinstance(placed, dict)
        and _order_ships_to(placed, "1550 Wewatta St, Unit 710", "Denver", "80202",
                            "6505551212")
        and _num(placed.get("grandTotal")) == 365.42
        and _cart_items(state) == []
    )
    preserved = (
        denver
        and _addr_matches(other, "600 Montgomery St", "San Francisco", "California",
                          "94111", "4155550157")
        and other.get("isDefaultBilling") is False
        and other.get("isDefaultShipping") is False
    )
    return {
        "default_entry_now_denver": denver,
        "cart_ordered_to_denver": shipped,
        "second_entry_untouched_beside_denver_default": preserved,
    }
'''

CHECKS_010 = '''def _checks(state):
    ids = sorted(i for i in _address_ids(state) if i is not None)
    austin = _address_by_id(state, 28)
    seattle = _address_by_id(state, 27)
    seed = _address_by_id(state, 26)
    customer = _customer(state)
    book_ok = (
        ids == [26, 27, 28]
        and _seed_26_values_intact(state)
        and _addr_matches(seattle, "915 E Pine St", "Seattle", "Washington",
                          "98122", "2065550134")
        and _addr_matches(austin, "1101 Red River St", "Austin", "Texas",
                          "78701", "5125550178")
    )
    promoted = (
        book_ok
        and isinstance(seed, dict)
        and _int(customer.get("defaultShipping")) == 28
        and _int(customer.get("defaultBilling")) == 26
        and austin.get("isDefaultShipping") is True
        and seed.get("isDefaultShipping") is False
        and seed.get("isDefaultBilling") is True
    )
    placed = _order_by_entity(state, 192)
    shipped = (
        isinstance(placed, dict)
        and _order_ships_to(placed, "1101 Red River St", "Austin", "78701",
                            "5125550178")
        and _num(placed.get("grandTotal")) == 365.42
        and _cart_items(state) == []
    )
    return {
        "cart_ordered_to_austin": shipped,
        "austin_entry_is_default_shipping": promoted,
    }
'''

TASKS = [
 dict(
  task_id="address_book_move_relocate_address_on_file_001",
  style="terse", difficulty="medium", shape="direct_mutation",
  skills=["R9", "A11"],
  skill_chain="locate the address record the account files under -> replace street/city/region/zip on it",
  analogues=[AN_MOVE_CHI],
  hard_criteria=[],
  instruction="I've moved. Update my address on file to 3540 Wilshire Blvd, Suite 12, Los Angeles, California, 90010.",
  criteria=[
    'state.addresses is exactly one record, id 26, whose street normalises to "3540 Wilshire Blvd, Suite 12", city "Los Angeles", region "California", postcode "90010", countryId "US", telephone "6505551212", firstname "Emma", lastname "Lopez".',
    'That record still carries isDefaultBilling true and isDefaultShipping true, and customer.defaultBilling and customer.defaultShipping both equal 26.',
  ],
  weights={"address_on_file_now_los_angeles": 1.0},
  checks=CHECKS_001, setup=None, fixture=None,
  notes=[
    "Pristine seed. The address book holds exactly one record, so AddressEditPage.jsx:15 sets isOnly and the two default checkboxes are REPLACED by div.message.info - nothing about the defaults is tickable and nothing about them is scored beyond their (unchanged) end value, folded into the single conjunctive component.",
    "Street is compared through a comma-joining normaliser, so 'Suite 12' on line 2 and '3540 Wilshire Blvd, Suite 12' on line 1 both pass.",
  ],
 ),
 dict(
  task_id="address_book_move_order_destination_relocation_002",
  style="terse", difficulty="hard", shape="retrieval_writeback",
  skills=["R4", "R9", "A11"],
  skill_chain="pick the most recent order -> read the address it shipped to -> edit that address-book record and make it both defaults",
  analogues=[AN_DEL_RECENT, AN_MOVE_BOS],
  hard_criteria=["derived_target", "cross_page"],
  instruction="I moved again. The address my most recent order shipped to is now 812 Vermont St, Apt 3, Los Angeles, California, 90014 - update that entry and make it my default for both billing and shipping.",
  criteria=[
    'state.addresses holds exactly ids 26, 27, 28; record 28 normalises to street "812 Vermont St, Apt 3", city "Los Angeles", region "California", postcode "90014", telephone "5105550188".',
    'Record 27 is still 1 Letterman Dr, San Francisco, California, 94129 and record 26 is still 101 S San Mateo Dr, San Mateo, California, 94010.',
    'customer.defaultBilling and customer.defaultShipping both equal 28; record 28 has both default flags true and record 26 has both false.',
  ],
  weights={"order_destination_entry_now_los_angeles": 0.6,
           "relocated_entry_is_both_defaults": 0.4},
  checks=CHECKS_002, setup="orders", fixture=FIX_002,
  notes=[
    "The order grid carries no Ship To column (OrderHistoryPage.jsx:44-49), so the destination is only readable by opening the newest order's View Order page - a genuine two-hop retrieval.",
    "The action cannot destroy its own premise: order addresses are snapshots written by placeOrder and saveAddress never rewrites them, so re-deriving 'the most recent order's destination' after the edit still names record 28.",
  ],
 ),
 dict(
  task_id="address_book_move_out_of_state_entry_pruned_003",
  style="terse", difficulty="medium", shape="retrieval_writeback",
  skills=["R9", "A11"],
  skill_chain="scan the address book for the one entry outside the home state -> delete that record",
  analogues=[AN_MOVE_PHI],
  hard_criteria=[],
  instruction="Everything I keep in my address book should be somewhere in California, and exactly one entry isn't. Delete that one.",
  criteria=[
    'state.addresses holds exactly ids 26, 27, 29 - the Chicago, Illinois record 28 is gone.',
    'Records 26, 27 and 29 still hold their exact seeded values and customer.defaultBilling and customer.defaultShipping both equal 26.',
  ],
  weights={"only_california_entries_remain": 1.0},
  checks=CHECKS_003, setup="simple", fixture=FIX_003,
  notes=[
    "AddressBookPage.jsx:79-84 renders the Delete link only for entries that are neither the default billing nor the default shipping address, so the Illinois record is injected as an additional entry and is genuinely deletable.",
    "The State column of #additional-addresses-table (AddressBookPage.jsx:73) makes the predicate readable without opening any edit form; Illinois is the unique non-California value.",
  ],
 ),
 dict(
  task_id="address_book_move_checkout_one_off_destination_004",
  style="terse", difficulty="medium", shape="retrieval_writeback",
  skills=["R9", "A11", "A10"],
  skill_chain="read the phone number already on file -> add a new checkout address carrying it -> place the cart's order to that address",
  analogues=[AN_MOVE_BOS],
  hard_criteria=[],
  instruction="Check out what's in my cart, but ship it to 77 Massachusetts Ave, Cambridge, Massachusetts, 02139. It's a one-off, so don't make it either default, and put my usual phone number on it.",
  criteria=[
    'state.addresses holds exactly ids 26 and 27; record 27 normalises to street "77 Massachusetts Ave", city "Cambridge", region "Massachusetts", postcode "02139", telephone "6505551212", with both default flags false.',
    'Record 26 is unchanged and customer.defaultBilling and customer.defaultShipping both still equal 26.',
    'A new order with entityId 190 exists whose shippingAddress is the Cambridge address, whose grandTotal is 365.42 and whose lines are productIds 10617, 15033 and 15787; cart.items is empty.',
  ],
  weights={"cambridge_entry_saved_without_defaults": 0.4,
           "cart_ordered_to_cambridge": 0.6},
  checks=CHECKS_004, setup=None, fixture=None,
  notes=[
    "Pristine seed; the cart already holds the three seeded lines 554/555/556 (subtotal 350.42 + 15.00 flat rate = 365.42).",
    "The telephone is the derived value: it is never stated and must be read off the existing address record or any past order. CheckoutPage.jsx:11-14 starts the Ship Here modal from an EMPTY_ADDRESS, so nothing pre-fills it.",
    "CheckoutPage.jsx:114-130 saves the new card with isDefaultBilling and isDefaultShipping false and then selects it, and placeOrder (AppContext.jsx:513) honours that selection over customer.defaultShipping.",
    "First and last name are deliberately NOT scored - the modal starts them empty and the instruction does not dictate them.",
  ],
 ),
 dict(
  task_id="address_book_move_office_billing_default_005",
  style="explicit", difficulty="medium", shape="direct_mutation",
  skills=["R9", "A11"],
  skill_chain="read which record currently holds each default -> create a second address and move only the billing default onto it",
  analogues=[AN_MOVE_SEA],
  hard_criteria=[],
  instruction="I want my invoices to go to my office from now on, but parcels should still come to the house. In the Address Book, use Add New Address to create a second entry: First Name Emma, Last Name Lopez, Company Vandelay Industries, Street Address: Line 1 425 Market St, Street Address: Line 2 Suite 2200, City San Francisco, State/Province California, Zip 94105, Phone Number 4155550188. Tick \"Use as my default billing address\", leave \"Use as my default shipping address\" unticked, and save. My San Mateo address must stay in the book and must remain my default shipping address.",
  criteria=[
    'state.addresses holds exactly ids 26 and 27; record 27 normalises to street "425 Market St, Suite 2200", city "San Francisco", region "California", postcode "94105", telephone "4155550188", company "Vandelay Industries".',
    'Record 26 still holds 101 S San Mateo Dr, San Mateo, California, 94010.',
    'customer.defaultBilling is 27 and customer.defaultShipping is 26; record 27 has isDefaultBilling true / isDefaultShipping false and record 26 has isDefaultBilling false / isDefaultShipping true.',
  ],
  weights={"office_entry_created_with_company": 0.5,
           "billing_default_moved_shipping_stayed": 0.5},
  checks=CHECKS_005, setup=None, fixture=None,
  notes=[
    "Pristine seed. On /customer/address/new/ the isOnly guard (AddressEditPage.jsx:15) is false because `existing` is null, so BOTH default checkboxes render even though the book holds a single address.",
    "This exercises the documented asymmetry of saveAddress (AppContext.jsx:471-481): ticking billing repoints customer.defaultBilling and clears isDefaultBilling everywhere else, while leaving shipping unticked writes false onto the new record only and leaves customer.defaultShipping alone.",
    "AddressEditPage.jsx:53 stores an empty Company as null, so the company is compared as trimmed text and never as an empty string.",
  ],
 ),
 dict(
  task_id="address_book_move_duplicate_zip_typo_cleanup_006",
  style="terse", difficulty="medium", shape="retrieval_writeback",
  skills=["R9", "A11"],
  skill_chain="compare the two duplicate entries to find the wrong ZIP -> delete that copy and promote the survivor to default shipping",
  analogues=[AN_MOVE_ATL],
  hard_criteria=[],
  instruction="My Palo Alto address got saved twice and one copy has the wrong ZIP - the right one is 94301. Delete the bad copy and make the good one my default shipping address.",
  criteria=[
    'Exactly two address records remain: record 26, and exactly one of records 27 / 28 whose street is "1200 Bryant St", city "Palo Alto", region "California", postcode "94301", telephone "6505550143".',
    'customer.defaultShipping equals the surviving Palo Alto record id and that record has isDefaultShipping true.',
    'customer.defaultBilling is still 26, record 26 still holds its seeded values with isDefaultBilling true and isDefaultShipping false.',
  ],
  weights={"wrong_zip_copy_removed": 0.5,
           "correct_copy_is_default_shipping": 0.5},
  checks=CHECKS_006, setup="simple", fixture=FIX_006,
  notes=[
    "Both duplicates are injected as additional (non-default) entries so both carry a Delete link - the UI does not pre-select the answer, the ZIP comparison does.",
    "The rubric keys on the surviving record's VALUES, not on which id survived, so an agent that instead deletes 27 and corrects 28's ZIP reaches the same graded end state. Both routes are honest readings of the errand.",
    "Ordering matters in practice: promoting a record to default shipping removes its Delete link (AddressBookPage.jsx:13-15), so promoting the wrong copy first strands the task.",
  ],
 ),
 dict(
  task_id="address_book_move_unit_number_and_mobile_007",
  style="explicit", difficulty="medium", shape="direct_mutation",
  skills=["R9", "A11"],
  skill_chain="identify which record is the default shipping address -> edit its second street line and phone number in place",
  analogues=[AN_MOVE_PHI],
  hard_criteria=[],
  instruction="My building has just added unit numbers and I've changed my mobile. Open the Address Book, find the entry that is currently my default shipping address, and press Change Shipping Address to edit it. Put Apt 4B in Street Address: Line 2 and change the Phone Number to 4155550142. Leave Street Address: Line 1, City, State/Province and Zip exactly as they are, do not add or delete any address, and leave my default billing address where it is.",
  criteria=[
    'The default shipping record (id 27) normalises to street "845 Market St, Apt 4B" and its telephone is exactly "4155550142".',
    'Record 27 still holds city "San Francisco", region "California", postcode "94103".',
    'state.addresses still holds exactly ids 26 and 27, record 26 still holds its seeded San Mateo values, customer.defaultBilling is 26 and customer.defaultShipping is 27.',
  ],
  weights={"unit_line_added_to_default_shipping": 0.5,
           "phone_updated_on_default_shipping": 0.5},
  checks=CHECKS_007, setup="simple", fixture=FIX_007,
  notes=[
    "The injection splits the two defaults across two records - billing on 26, shipping on 27 - so 'my default shipping address' is a real lookup rather than 'the only address'.",
    "Both components carry the preservation clauses conjunctively rather than paying for them separately, so the injected baseline scores exactly 0.0.",
    "Saving record 27 with the shipping box left ticked re-writes customer.defaultShipping to 27 (already true) and does not disturb customer.defaultBilling, which stays 26.",
  ],
 ),
 dict(
  task_id="address_book_move_ship_cart_to_relatives_008",
  style="terse", difficulty="medium", shape="direct_mutation",
  skills=["R9", "A10"],
  skill_chain="find the address-book entry that is not in the account holder's own name -> place the cart's order to it",
  analogues=[AN_DEL_FIRST],
  hard_criteria=[],
  instruction="Order everything in my cart, but send it to my parents - theirs is the only entry in my address book that isn't in my own first name. Leave my defaults alone.",
  criteria=[
    'A new order with entityId 190 exists whose shippingAddress is 4820 Del Rio Rd, Sacramento, 95822, telephone 9165550111, firstname "Robert", and whose grandTotal is 365.42.',
    'cart.items is empty.',
    'state.addresses still holds exactly ids 26 and 27 with their injected values, and customer.defaultBilling and customer.defaultShipping both still equal 26.',
  ],
  weights={"cart_ordered_to_parents_address": 1.0},
  checks=CHECKS_008, setup="simple", fixture=FIX_008,
  notes=[
    "CheckoutPage.jsx:27 preselects customer.defaultShipping, so the agent must actively click the second shipping-address card; placeOrder (AppContext.jsx:513) then honours the selection over the default.",
    "Single conjunctive component: the address book is asserted as an exact collection rather than paid for separately, so an untouched episode scores 0.0.",
  ],
 ),
 dict(
  task_id="address_book_move_denver_relocation_then_checkout_009",
  style="explicit", difficulty="hard", shape="direct_mutation",
  skills=["R9", "A11", "A10"],
  skill_chain="find the record the account defaults to -> rewrite it to the new city -> check out so the order snapshots the new address",
  analogues=[AN_MOVE_CHI, AN_DEL_RECENT],
  hard_criteria=["derived_target", "ordering_dependency"],
  instruction="We've moved to Denver. In the Address Book, find the entry that is currently both my default billing and my default shipping address and edit that entry in place: Street Address: Line 1 1550 Wewatta St, Street Address: Line 2 Unit 710, City Denver, State/Province Colorado, Zip 80202. Keep my phone number as it is and keep that entry as both defaults. Then check out the items already in my cart so the order ships to the new Denver address. Do not add a new address entry, and do not change the other entry in my address book.",
  criteria=[
    'Record 26 normalises to street "1550 Wewatta St, Unit 710", city "Denver", region "Colorado", postcode "80202", telephone "6505551212", with both default flags true and customer.defaultBilling and customer.defaultShipping both 26.',
    'A new order with entityId 190 exists whose shippingAddress is the Denver address and whose grandTotal is 365.42; cart.items is empty.',
    'state.addresses still holds exactly ids 26 and 27, and record 27 is still 600 Montgomery St, San Francisco, California, 94111 with both default flags false.',
  ],
  weights={"default_entry_now_denver": 0.4,
           "cart_ordered_to_denver": 0.4,
           "second_entry_untouched_beside_denver_default": 0.2},
  checks=CHECKS_009, setup="simple", fixture=FIX_009,
  notes=[
    "Genuine ordering dependency: placeOrder snapshots the address at checkout time (AppContext.jsx:526-539), so an agent that checks out before editing the record ships to San Mateo and loses the second component permanently - the order address is read-only afterwards (OrderViewPage.jsx:80-89).",
    "The third component includes the Denver clause, so it is false on the injected baseline and the untouched lane scores exactly 0.0 despite being a preservation-flavoured component in the explicit set.",
  ],
 ),
 dict(
  task_id="address_book_move_latest_destination_becomes_default_010",
  style="terse", difficulty="hard", shape="retrieval_writeback",
  skills=["R4", "R9", "A11", "A10"],
  skill_chain="pick the most recent order -> read where it shipped -> order the cart to that same address and promote it to default shipping",
  analogues=[AN_DEL_RECENT, AN_MOVE_SEA],
  hard_criteria=["derived_target", "cross_page"],
  instruction="Send what's in my cart to the same place my most recent order went, and make that address my default shipping address from now on.",
  criteria=[
    'A new order with entityId 192 exists whose shippingAddress is 1101 Red River St, Austin, 78701, telephone 5125550178, and whose grandTotal is 365.42; cart.items is empty.',
    'customer.defaultShipping is 28 and record 28 has isDefaultShipping true.',
    'customer.defaultBilling is still 26, record 26 keeps its seeded values with isDefaultBilling true and isDefaultShipping false, and state.addresses still holds exactly ids 26, 27, 28 with their injected values.',
  ],
  weights={"cart_ordered_to_austin": 0.5,
           "austin_entry_is_default_shipping": 0.5},
  checks=CHECKS_010, setup="orders", fixture=FIX_010,
  notes=[
    "Two injected orders, 000000190 to Seattle and 000000191 to Austin, both dated 12:00:00Z in June 2023 so they sit at the head of page 1 and cannot day-shift under America/New_York.",
    "The premise survives the action: the order the agent places also ships to Austin, so re-deriving 'my most recent order' at any point still returns the Austin destination.",
    "nextOrderEntityId and nextOrderIncrementId are both bumped to 192, so the placed order is entityId 192 / incrementId 000000192 and no id collides.",
  ],
 ),
]

WHY = {
 "address_book_move_out_of_state_entry_pruned_003":
   "Injects a four-entry address book whose sole non-California record (id 28, Chicago,\nIllinois) is an additional, non-default entry, so AddressBookPage renders a Delete\nlink for it. The pristine seed holds a single address and deleteAddress\n(AppContext.jsx:491) has nothing to act on.",
 "address_book_move_duplicate_zip_typo_cleanup_006":
   "Injects a three-entry address book in which the Palo Alto address appears twice,\nonce with the correct ZIP 94301 and once with a transposed 94031. Both copies are\nadditional, non-default entries, so both are deletable and the UI does not give the\nanswer away.",
 "address_book_move_unit_number_and_mobile_007":
   "Injects a two-entry address book with the billing default on record 26 and the\nshipping default on record 27, so 'my default shipping address' is a real lookup.\nOn the pristine single-address seed the AddressEditPage isOnly guard also hides both\ndefault checkboxes.",
 "address_book_move_ship_cart_to_relatives_008":
   "Injects a second address held in a different person's name (Robert Lopez,\nSacramento) as a non-default entry, so the checkout shipping-address picker\n(CheckoutPage.jsx:410-428) renders two cards and the default is not the answer.",
 "address_book_move_denver_relocation_then_checkout_009":
   "Injects a second, non-default address so that 'the entry that is currently both my\ndefault billing and my default shipping address' selects one record out of two\nrather than naming the only one.",
 "address_book_move_order_destination_relocation_002":
   "Injects a three-entry address book plus two recent orders, one shipped to each of\nthe two additional entries, so the most recent order names exactly one address-book\nrecord to edit.",
 "address_book_move_latest_destination_becomes_default_010":
   "Injects a three-entry address book plus two recent orders, shipped to Seattle and\n(more recently) Austin, so the most recent order's destination is a genuine two-hop\nlookup and the promotion target is derived rather than named.",
}


def emit(task):
    tid = task["task_id"]
    d = os.path.join(ROOT, tid)
    os.makedirs(d, exist_ok=True)

    setup_src = None
    if task["setup"] == "simple":
        patch = {
            "addresses": task["fixture"]["addresses"],
            "nextAddressId": task["fixture"]["nextAddressId"],
            "customer": task["fixture"]["customer"],
        }
        setup_src = SETUP_SIMPLE.format(
            task_id=tid, why=WHY[tid], placeholder=PLACEHOLDER,
            patch=json.dumps(patch, indent=1))
    elif task["setup"] == "orders":
        f = task["fixture"]
        patch = {
            "addresses": f["addresses"], "nextAddressId": f["nextAddressId"],
            "defaultBilling": f["defaultBilling"], "defaultShipping": f["defaultShipping"],
            "orders": f["orders"], "nextOrderEntityId": f["nextOrderEntityId"],
            "nextOrderIncrementId": f["nextOrderIncrementId"],
        }
        setup_src = SETUP_ORDERS.format(
            task_id=tid, why=WHY[tid], placeholder=PLACEHOLDER,
            patch=json.dumps(patch, indent=1))
    if setup_src is not None:
        open(os.path.join(d, "initial_setup.py"), "w").write(setup_src)
    elif os.path.exists(os.path.join(d, "initial_setup.py")):
        os.remove(os.path.join(d, "initial_setup.py"))

    write_reward(os.path.join(d, "reward.py"), tid, task["criteria"],
                 task["weights"], task["checks"])
    write_nemo_reward(os.path.join(d, "nemo_reward.py"), tid, task["weights"], task["checks"])

    ti = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": APP,
        "start_path": "/",
        "difficulty": task["difficulty"],
        "success_criteria": task["criteria"],
    }
    open(os.path.join(d, "task_instruction.json"), "w").write(json.dumps(ti, indent=2) + "\n")

    metadata = {
        "style": task["style"],
        "difficulty": task["difficulty"],
        "shape": task["shape"],
        "skills": task["skills"],
        "skill_chain": task["skill_chain"],
        "official_analogues": task["analogues"],
        "hard_criteria": task["hard_criteria"],
        "topic": "shopping storefront address book relocation",
        "lane": "address_book_move",
        "inspiration_ids": ["webarena-571", "webarena-572", "webarena-573",
                            "webarena-574", "webarena-575", "webarena-794",
                            "webarena-796", "webarena-797", "webarena-362"],
        "authoring_notes": task["notes"],
    }
    if setup_src is not None:
        metadata["injected_preconditions"] = task["injected"]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [{
            "name": APP,
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
    }
    open(os.path.join(d, "task.json"), "w").write(json.dumps(manifest, indent=2) + "\n")

    row = {"task_payload": {
        "task_id": tid,
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP],
        "start_urls": [],
        "intent": task["instruction"],
        "eval": {"eval_types": ["string_match"], "reference_answers": None,
                 "note": "unused - CUA-Gym reward code is authoritative"},
        "cuagym": {
            "bundle_id": tid,
            "app_dir": APP,
            "initial_setup": setup_src,
            "eval_reward_code": open(os.path.join(d, "nemo_reward.py")).read(),
        },
    }}
    open(os.path.join(d, "nemo_task.json"), "w").write(json.dumps(row, indent=2) + "\n")
    return row


INJECTED = {
 "address_book_move_order_destination_relocation_002": [
   "addresses replaced with three records: seeded 26 (San Mateo, both defaults), 27 (1 Letterman Dr, San Francisco, CA 94129), 28 (2100 Franklin St, Oakland, CA 94612); nextAddressId 29.",
   "orders prepended with 000000190 (2023-06-02 12:00:00Z, shipped to record 27) and 000000191 (2023-06-14 12:00:00Z, shipped to record 28); nextOrderEntityId and nextOrderIncrementId both 192.",
 ],
 "address_book_move_out_of_state_entry_pruned_003": [
   "addresses replaced with four records: seeded 26 (both defaults), 27 Palo Alto CA, 28 Chicago IL (the single out-of-state entry), 29 Oakland CA; nextAddressId 30.",
 ],
 "address_book_move_duplicate_zip_typo_cleanup_006": [
   "addresses replaced with three records: seeded 26 (both defaults) plus two non-default copies of 1200 Bryant St, Palo Alto - record 27 with the correct ZIP 94301 and record 28 with the transposed 94031; nextAddressId 29.",
 ],
 "address_book_move_unit_number_and_mobile_007": [
   "addresses replaced with two records: 26 (San Mateo) holding only the billing default and 27 (845 Market St, San Francisco, CA 94103) holding only the shipping default; customer.defaultBilling 26, customer.defaultShipping 27; nextAddressId 28.",
 ],
 "address_book_move_ship_cart_to_relatives_008": [
   "addresses replaced with two records: seeded 26 (both defaults) and non-default 27 in another name (Robert Lopez, 4820 Del Rio Rd, Sacramento, CA 95822); nextAddressId 28.",
 ],
 "address_book_move_denver_relocation_then_checkout_009": [
   "addresses replaced with two records: seeded 26 (both defaults) and non-default 27 (600 Montgomery St, San Francisco, CA 94111); nextAddressId 28.",
 ],
 "address_book_move_latest_destination_becomes_default_010": [
   "addresses replaced with three records: seeded 26 (both defaults), 27 (915 E Pine St, Seattle, WA 98122), 28 (1101 Red River St, Austin, TX 78701); nextAddressId 29.",
   "orders prepended with 000000190 (2023-06-05 12:00:00Z, shipped to record 27) and 000000191 (2023-06-21 12:00:00Z, shipped to record 28); nextOrderEntityId and nextOrderIncrementId both 192.",
 ],
}

for t in TASKS:
    t["injected"] = INJECTED.get(t["task_id"], [])

os.makedirs(BATCH, exist_ok=True)
os.makedirs(REPLAYS, exist_ok=True)
rows = [emit(t) for t in TASKS]
with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
index = {"schema_version": 2,
         "tasks": [{"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]}
                   for t in TASKS]}
open(os.path.join(BATCH, "index.json"), "w").write(json.dumps(index, indent=2) + "\n")
print("wrote", len(rows), "bundles")
