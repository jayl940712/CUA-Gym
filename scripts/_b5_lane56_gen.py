#!/usr/bin/env python3
"""Bundle generator for batch-5 lane 56 (shopping_admin / phone_lookup_address_fix).

Authoring helper only. Writes bundles under
output/tasks/shopping_admin/<task_id>/ plus the lane's GENERATION.md and
replay drafts. Runs no validation.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE_DIR = os.path.join(ROOT, "output", "tasks", "shopping_admin")
BATCH_DIR = os.path.join(SITE_DIR, "_batches", "phone_lookup_address_fix")
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

# --------------------------------------------------------------------------
# shared reward body pieces
# --------------------------------------------------------------------------

ADDR_HELPERS = '''
def _norm(value):
    if value is None:
        return ""
    return str(value).strip()


def _street_list(value):
    if isinstance(value, list):
        return [_norm(part) for part in value if _norm(part) != ""]
    if isinstance(value, str):
        return [_norm(part) for part in value.split("\\n") if _norm(part) != ""]
    return []


def _override_row(state, address_id):
    overrides = state.get("orderAddressOverrides")
    if not isinstance(overrides, dict):
        return None
    row = overrides.get(str(address_id))
    if isinstance(row, dict):
        return row
    return None


def _identity_ok(row, want):
    for field in ("firstname", "lastname", "telephone"):
        if _norm(row.get(field)) != _norm(want.get(field)):
            return False
    return True


def _street_ok(row, want):
    return _street_list(row.get("street")) == [_norm(p) for p in want.get("street", [])]


def _locale_ok(row, want):
    for field in ("city", "region", "postcode", "country_id"):
        if _norm(row.get(field)) != _norm(want.get(field)):
            return False
    raw = row.get("region_id")
    try:
        found = int(str(raw).strip())
    except (TypeError, ValueError):
        return False
    return found == int(want.get("region_id"))


def _full_ok(state, address_id):
    row = _override_row(state, address_id)
    if row is None:
        return False
    want = EXPECTED_ADDRESSES[str(address_id)]
    return _identity_ok(row, want) and _street_ok(row, want) and _locale_ok(row, want)


def _part_ok(state, address_id, part):
    row = _override_row(state, address_id)
    if row is None:
        return False
    want = EXPECTED_ADDRESSES[str(address_id)]
    if not _identity_ok(row, want):
        return False
    if part == "street":
        return _street_ok(row, want)
    return _locale_ok(row, want)
'''

CUSTOMER_HELPERS = '''
def _norm(value):
    if value is None:
        return ""
    return str(value).strip()


def _customer_addresses(state, entity_id):
    rows = state.get("customers")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("entity_id")) == str(entity_id):
            addresses = row.get("addresses")
            if isinstance(addresses, list):
                return addresses
            return None
    return None


def _sole_address(state):
    addresses = _customer_addresses(state, CUSTOMER_ENTITY_ID)
    if addresses is None or len(addresses) != 1:
        return None
    row = addresses[0]
    if isinstance(row, dict):
        return row
    return None


def _identity_ok(row):
    for field in ("firstname", "lastname", "telephone"):
        if _norm(row.get(field)) != _norm(EXPECTED_ADDRESS.get(field)):
            return False
    return True


def _street_ok(row):
    return _norm(row.get("street")) == _norm(EXPECTED_ADDRESS.get("street"))


def _locale_ok(row):
    for field in ("city", "region", "postcode", "country_id"):
        if _norm(row.get(field)) != _norm(EXPECTED_ADDRESS.get(field)):
            return False
    return True
'''

STATE_READER = '''
def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}
'''

EVALUATE_TAIL = '''
def evaluate(evidence):
    state = _state(evidence)
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


def json_fixture(obj):
    text = json.dumps(obj, indent=2, ensure_ascii=True)
    assert "\\" not in text, "fixture must contain no backslash escapes"
    return 'json.loads(r"""%s""")' % text


def reward_sources(task):
    """Return (reward_py, nemo_reward_py) for one task."""
    tid = task["task_id"]
    criteria = "\n".join("  * %s" % c for c in task["success_criteria"])
    weights = task["weights"]
    weight_lines = ",\n".join(
        "    %r: %s" % (name, value) for name, value in weights)
    checks_body = task["checks_body"]

    if task["family"] == "order_address":
        fixture = "EXPECTED_ADDRESSES = %s" % json_fixture(task["expected"])
        helpers = ADDR_HELPERS
        extra_consts = ""
    else:
        fixture = "EXPECTED_ADDRESS = %s" % json_fixture(task["expected"])
        helpers = CUSTOMER_HELPERS
        extra_consts = "CUSTOMER_ENTITY_ID = %d\n" % task["customer_entity_id"]

    common = (
        "\n" + fixture + "\n\n" + extra_consts + "\n"
        + "COMPONENT_WEIGHTS = {\n" + weight_lines + ",\n}\n"
        + "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n"
        + helpers + "\n\ndef _checks(state):\n" + checks_body + "\n"
    )

    reward = (
        '"""Deterministic reward for %s.\n\nSuccess criteria:\n%s\n\n'
        'Reads only `current_state` from the immutable evidence bundle; it never\n'
        'diffs against `initial_state`. Ground truth is fixed by the frozen seed of\n'
        'webarena_shopping_admin_mock in ./hub/ plus this bundle\'s own setup.\n"""\n'
        "\nimport json\n"
        % (tid, criteria)
        + STATE_READER
        + common
        + EVALUATE_TAIL
    )

    nemo = (
        '"""NeMo-Gym reward program for %s.\n\nImplements exactly the rubric of reward.py, reading `current_state` from\n'
        'GET /go?sid=... instead of a frozen evidence bundle, and printing\n'
        'REWARD: <float> on every output path including the error path.\n\n'
        'Self-contained: standard library plus requests, which is present in\n'
        'cuagym/requirements.txt.\n"""\n'
        "\nimport json\nimport sys\n\nimport requests\n\n"
        'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n'
        % (tid, URL_PLACEHOLDER)
        + common
        + NEMO_TAIL
    )
    return reward, nemo


SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {tid}.

{why}

The replacement customer row is inlined as a raw triple-quoted JSON literal and
parsed with json.loads, so no JavaScript literal ever reaches Python source and
no backslash escape is eaten by the Python parser.

shopping_admin's `set` verb is a TOP-LEVEL shallow merge over
createInitialData() (vite.config.js:371-377), so posting only `customers` leaves
every other seeded key intact, and it rewrites the /go baseline too.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

CUSTOMER_ENTITY_ID = {entity_id}
EXPECTED_SEED_EMAIL = "{email}"

REPLACEMENT_ROW = json.loads(r"""{row}""")


def fail(message):
    sys.stderr.write("SETUP FAILED: %s\\n" % (message,))
    raise SystemExit(1)


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    seed = probe.json().get("current_state")
    if not isinstance(seed, dict):
        fail("current_state is not an object")
    customers = seed.get("customers")
    if not isinstance(customers, list) or len(customers) != 70:
        fail("expected 70 seeded customers")

    replaced = 0
    patched = []
    for row in customers:
        if isinstance(row, dict) and str(row.get("entity_id")) == str(CUSTOMER_ENTITY_ID):
            if row.get("email") != EXPECTED_SEED_EMAIL:
                fail("customer %s is not %s" % (CUSTOMER_ENTITY_ID, EXPECTED_SEED_EMAIL))
            patched.append(REPLACEMENT_ROW)
            replaced += 1
        else:
            patched.append(row)
    if replaced != 1:
        fail("expected exactly one customer row to replace")

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": {{"customers": patched}}}},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    if result.get("state_diff") != {{}}:
        fail("state_diff is not empty after set")
    if result.get("initial_state") != result.get("current_state"):
        fail("initial_state != current_state after set")
    current = result.get("current_state")
    if not isinstance(current, dict):
        fail("current_state is not an object after set")
    if current.get("orderAddressOverrides") != {{}}:
        fail("orderAddressOverrides must start empty")
    print("SETUP OK")


main()
'''


def build_setup(task):
    row_json = json.dumps(task["setup_row"], indent=2, ensure_ascii=True)
    assert "\\" not in row_json
    return SETUP_TEMPLATE.format(
        tid=task["task_id"],
        why=task["setup_why"],
        url=URL_PLACEHOLDER,
        entity_id=task["setup_row"]["entity_id"],
        email=task["setup_row"]["email"],
        row=row_json,
    )


# --------------------------------------------------------------------------
# per-task data
# --------------------------------------------------------------------------

def order_addr(first, last, street, city, region, region_id, postcode, phone):
    return {
        "firstname": first,
        "lastname": last,
        "street": street,
        "city": city,
        "region": region,
        "region_id": region_id,
        "postcode": postcode,
        "country_id": "US",
        "telephone": phone,
    }


def customer_row(entity_id, email, first, last, created_at, addresses,
                 default_billing, default_shipping, billing_full,
                 shipping_full, phone, group_id=1):
    return {
        "entity_id": entity_id,
        "website_id": 1,
        "email": email,
        "group_id": group_id,
        "store_id": 1,
        "created_at": created_at,
        "updated_at": created_at,
        "is_active": 1,
        "created_in": "Default Store View",
        "firstname": first,
        "lastname": last,
        "default_billing": default_billing,
        "default_shipping": default_shipping,
        "disable_auto_group_change": 0,
        "name": "%s %s" % (first, last),
        "billing_full": billing_full,
        "shipping_full": shipping_full,
        "billing_telephone": phone,
        "addresses": addresses,
    }


def cust_addr(entity_id, parent_id, first, last, street, city, region,
              region_id, postcode, phone, created_at):
    return {
        "entity_id": entity_id,
        "parent_id": parent_id,
        "firstname": first,
        "lastname": last,
        "street": street,
        "city": city,
        "region": region,
        "region_id": region_id,
        "postcode": postcode,
        "country_id": "US",
        "telephone": phone,
        "created_at": created_at,
    }


TASKS = []

# ---------------------------------------------------------------- 001
t1_addr = order_addr("John", "Smith", ["4275 Magnolia Ridge Drive"],
                     "Homewood", "Alabama", 1, "35209", "2058812302")
TASKS.append({
    "task_id": "phone_lookup_address_fix_johnsmith_account_sync_001",
    "family": "order_address",
    "style": "terse",
    "difficulty": "hard",
    "shape": "retrieval_writeback",
    "skills": ["R9", "R7", "A11"],
    "skill_chain": "reverse-look-up the phone number in the customer grid -> join to that customer's most recent order -> copy the address now on their account onto that order's billing address",
    "official_analogues": [
        "Find the customer name and email with phone number +1 2058812302",
        "Modify the billing address of order #299 to 456 Oak Avenue, Apartment 5B, New York, NY, 10001",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "A shopper phoned from 2058812302 about a parcel sent to their old house. The address on their account is already the right one - bring the billing address on their most recent order into line with it.",
    "expected": {"18": t1_addr},
    "weights": [
        ("order_billing_street_now_matches_account", 0.5),
        ("order_billing_city_state_zip_now_match_account", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'order_billing_street_now_matches_account': _part_ok(state, '18', 'street'),\n"
        "        'order_billing_city_state_zip_now_match_account': _part_ok(state, '18', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['18'] - the billing address of order 000000009 - has street exactly ['4275 Magnolia Ridge Drive'].",
        "That same override records city Homewood, region Alabama, region_id 1, postcode 35209, country_id US.",
        "The recipient on that address is still John Smith on telephone 2058812302.",
    ],
    "setup_why": "John Smith's account address book already holds the new Homewood address; only the order still carries the old Birmingham one, which is what the agent has to reconcile.",
    "setup_row": customer_row(
        2, "john.smith.xyz@gmail.com", "John", "Smith", "2023-04-19 21:44:57",
        [cust_addr(2, 2, "John", "Smith", "4275 Magnolia Ridge Drive",
                   "Homewood", "Alabama", 1, "35209", "2058812302",
                   "2023-04-19 21:44:57")],
        2, 2,
        "4275 Magnolia Ridge Drive Homewood Alabama 35209",
        "4275 Magnolia Ridge Drive Homewood Alabama 35209",
        "2058812302"),
    "injected_preconditions": [
        "customers[entity_id=2].addresses[0] now reads 4275 Magnolia Ridge Drive, Homewood, Alabama 35209 (region_id 1), with billing_full and shipping_full recomputed the way CustomerEdit.saveAddress builds billing_full (CustomerEdit.jsx:708-716). billing_telephone is unchanged at 2058812302 so the customer-grid keyword search still finds the row.",
    ],
    "notes": [
        "Order 000000009 (2023-05-07 22:41:05) is John Smith's most recent of 13 orders; the runner-up is 000000096 on 2023-01-16, a margin of 111 days.",
        "Billing address entity_id 18, shipping 17 (orders.json). OrderBlocks.jsx:205 renders the Edit link next to Billing Address, so the form is reachable by clicking.",
        "The seeded phone is stored unformatted as 2058812302; the instruction quotes it unformatted so the grid keyword search (gridUtils.js:131-137, substring, case-insensitive) matches on the Phone column.",
        "Keyword 2058812302 matches exactly one of the 70 customer-grid rows across every declared column.",
    ],
})

# ---------------------------------------------------------------- 002
t2_addr = order_addr("Jane", "Doe", ["88 Shadyside Terrace"], "Pittsburgh",
                     "Pennsylvania", 51, "15232", "4123671901")
TASKS.append({
    "task_id": "phone_lookup_address_fix_janedoe_shipping_sync_002",
    "family": "order_address",
    "style": "terse",
    "difficulty": "hard",
    "shape": "retrieval_writeback",
    "skills": ["R9", "R7", "A11"],
    "skill_chain": "reverse-look-up the phone number -> join to that customer's newest order -> copy the account's current address onto that order's shipping address",
    "official_analogues": [
        "Find the customer name and email with phone number 2137418080",
        "Modify the billing address of order #65 to 789 Pine Lane, San Francisco, CA, 94102",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "The customer on 4123671901 has relocated, but their newest order is still routed to the old place. Set that order's shipping address to whatever address their account now holds.",
    "expected": {"603": t2_addr},
    "weights": [
        ("order_shipping_street_now_matches_account", 0.5),
        ("order_shipping_city_state_zip_now_match_account", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'order_shipping_street_now_matches_account': _part_ok(state, '603', 'street'),\n"
        "        'order_shipping_city_state_zip_now_match_account': _part_ok(state, '603', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['603'] - the shipping address of order 000000302 - has street exactly ['88 Shadyside Terrace'].",
        "That same override records city Pittsburgh, region Pennsylvania, region_id 51, postcode 15232, country_id US.",
        "The recipient on that address is still Jane Doe on telephone 4123671901.",
    ],
    "setup_why": "Jane Doe's account address book already carries her Pittsburgh address; her open order 000000302 still ships to Miami, which is the discrepancy the agent has to close.",
    "setup_row": customer_row(
        3, "jane.doe@hotmail.com", "Jane", "Doe", "2023-04-19 21:45:01",
        [cust_addr(3, 3, "Jane", "Doe", "88 Shadyside Terrace", "Pittsburgh",
                   "Pennsylvania", 51, "15232", "4123671901",
                   "2023-04-19 21:45:01")],
        3, 3,
        "88 Shadyside Terrace Pittsburgh Pennsylvania 15232",
        "88 Shadyside Terrace Pittsburgh Pennsylvania 15232",
        "4123671901"),
    "injected_preconditions": [
        "customers[entity_id=3].addresses[0] now reads 88 Shadyside Terrace, Pittsburgh, Pennsylvania 15232 with region_id 51, and billing_full / shipping_full are rebuilt to match. billing_telephone stays 4123671901 so the phone lookup is unaffected.",
    ],
    "notes": [
        "Order 000000302 (2023-04-19 23:41:29) is Jane Doe's most recent of 12; the runner-up is 000000116 on 2023-03-21, a margin of 30 days.",
        "Shipping address entity_id 603, billing 604. The Edit link beside Shipping Address is OrderBlocks.jsx:218.",
        "region_id is set to 51 in the injected row so the account card and the order form agree on Pennsylvania; the customer AddressForm has no region_id control, so a hand edit through that form would have left it stale.",
    ],
})

# ---------------------------------------------------------------- 003
t3_addr_s = order_addr("Grace", "Nguyen", ["412 Beacon Street"], "Boston",
                       "Massachusetts", 32, "02115", "6175555555")
t3_addr_b = dict(t3_addr_s)
TASKS.append({
    "task_id": "phone_lookup_address_fix_grace_both_addresses_003",
    "family": "order_address",
    "style": "terse",
    "difficulty": "hard",
    "shape": "retrieval_writeback",
    "skills": ["R9", "R7", "A11"],
    "skill_chain": "reverse-look-up the phone number -> join to that customer's latest order -> copy the account address onto both the billing and the shipping record of that order",
    "official_analogues": [
        "Find the customer name and email with phone number 2065555555",
        "Modify the billing address of order #65 to 789 Pine Lane, San Francisco, CA, 94102",
    ],
    "hard_criteria": ["derived_target", "multi_mutation"],
    "instruction": "Caller 6175555555 has a new home address on file with us. Their latest order still shows the old one on both the billing and the shipping side - correct both to the address on the account.",
    "expected": {"129": t3_addr_s, "130": t3_addr_b},
    "weights": [
        ("order_shipping_address_now_matches_account", 0.5),
        ("order_billing_address_now_matches_account", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'order_shipping_address_now_matches_account': _full_ok(state, '129'),\n"
        "        'order_billing_address_now_matches_account': _full_ok(state, '130'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['129'] - the shipping address of order 000000065 - reads 412 Beacon Street, Boston, Massachusetts, region_id 32, 02115, US.",
        "orderAddressOverrides['130'] - the billing address of the same order - reads the same address.",
        "Both records still name Grace Nguyen on telephone 6175555555.",
    ],
    "setup_why": "Grace Nguyen's account address book already holds the Beacon Street address; order 000000065 still carries the Harvard Square one on both sides.",
    "setup_row": customer_row(
        18, "avidreader99@yahoo.com", "Grace", "Nguyen", "2023-04-19 21:45:51",
        [cust_addr(18, 18, "Grace", "Nguyen", "412 Beacon Street", "Boston",
                   "Massachusetts", 32, "02115", "6175555555",
                   "2023-04-19 21:45:51")],
        18, 18,
        "412 Beacon Street Boston Massachusetts 02115",
        "412 Beacon Street Boston Massachusetts 02115",
        "6175555555"),
    "injected_preconditions": [
        "customers[entity_id=18].addresses[0] now reads 412 Beacon Street, Boston, Massachusetts 02115 (region_id 32, the same state as the seeded address, so no other field goes stale). billing_full and shipping_full are rebuilt; billing_telephone is unchanged at 6175555555.",
    ],
    "notes": [
        "Order 000000065 (2023-05-28 10:43:55) is Grace Nguyen's most recent of 15; the runner-up is 000000308 on 2023-04-19, a margin of 38 days.",
        "Shipping address entity_id 129, billing 130. Both Edit links render on the order view (OrderBlocks.jsx:205 and :218).",
        "The two writes are independent patchOrderAddress calls (AppContext.jsx:209), so the components genuinely split.",
    ],
})

# ---------------------------------------------------------------- 004
t4_addr = order_addr("Lily", "Potter", ["55 Sheridan Road"], "Evanston",
                     "Illinois", 23, "60202", "7735555555")
TASKS.append({
    "task_id": "phone_lookup_address_fix_lily_latest_complete_004",
    "family": "order_address",
    "style": "terse",
    "difficulty": "hard",
    "shape": "state_mutation",
    "skills": ["R9", "R5", "A11"],
    "skill_chain": "reverse-look-up the phone number -> filter that customer's orders down to the completed ones and take the most recent -> edit that order's billing address",
    "official_analogues": [
        "Find the customer name and email with phone number +1 2058812302",
        "Modify the billing address of order #301 to 321 Birch Boulevard, Suite 200, Dallas, TX, 75201",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "The shopper reachable on 7735555555 says the invoice for her most recent completed order carries the wrong billing address. Change it to 55 Sheridan Road, Evanston, Illinois 60202.",
    "expected": {"364": t4_addr},
    "weights": [
        ("completed_order_billing_street_updated", 0.5),
        ("completed_order_billing_city_state_zip_updated", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'completed_order_billing_street_updated': _part_ok(state, '364', 'street'),\n"
        "        'completed_order_billing_city_state_zip_updated': _part_ok(state, '364', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['364'] - the billing address of order 000000182 - has street exactly ['55 Sheridan Road'].",
        "That override records city Evanston, region Illinois, region_id 23, postcode 60202, country_id US.",
        "The recipient is still Lily Potter on telephone 7735555555.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "Lily Potter (customer 17, harrypotterfan1@gmail.com) has 11 orders. Her most recent is 000000136 on 2023-05-24 but it is Canceled; the most recent Complete one is 000000182 on 2023-04-28, and the next Complete is 000000021 on 2022-09-23 - a 7-month margin.",
        "The status predicate is load bearing: an agent that ignores it edits address 272 and scores 0.0.",
        "Status is not a column on the customer Orders tab, so the readable route is Sales > Orders with the email as keyword; that grid does carry Status and sorts created_at DESC (OrdersGrid.jsx:413).",
        "Billing address entity_id 364, shipping 363.",
    ],
})

# ---------------------------------------------------------------- 005
t5_addr = order_addr("Brian", "Smith",
                     ["456 Las Vegas Blvd S", "Suite 300"], "Las Vegas",
                     "Nevada", 39, "89109", "7025551212")
TASKS.append({
    "task_id": "phone_lookup_address_fix_brian_suite_line_005",
    "family": "order_address",
    "style": "terse",
    "difficulty": "medium",
    "shape": "state_mutation",
    "skills": ["R9", "A11"],
    "skill_chain": "attribute look-up on a named order -> edit the shipping address record it points at",
    "official_analogues": [
        "Show me the billing address for order number 00178.",
        "Modify the billing address of order #301 to 321 Birch Boulevard, Suite 200, Dallas, TX, 75201",
    ],
    "hard_criteria": [],
    "instruction": "Order 000000118 came back undelivered because the suite number was missing. Add Suite 300 as the second street line of its shipping address, leaving the first line as it is.",
    "expected": {"235": t5_addr},
    "weights": [
        ("shipping_address_carries_both_street_lines", 1.0),
    ],
    "checks_body": (
        "    return {\n"
        "        'shipping_address_carries_both_street_lines': _full_ok(state, '235'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['235'] - the shipping address of order 000000118 - has street exactly ['456 Las Vegas Blvd S', 'Suite 300'].",
        "City Las Vegas, region Nevada, region_id 39, postcode 89109 and country_id US are all recorded on that override.",
        "The recipient is still Brian Smith on telephone 7025551212.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "OrderAddressEdit.save() builds street as [street0, street1] with empty entries dropped, so a two-line street is exactly what the second input produces.",
        "Order 000000118 belongs to Brian Smith (customer 34); shipping address entity_id 235, billing 236. The order is reachable from Sales > Orders by keyword 000000118.",
        "Two skills only - a named record plus one edit - so this is medium and was not padded upward.",
    ],
})

# ---------------------------------------------------------------- 006
t6_addr = {
    "firstname": "Jennifer",
    "lastname": "White",
    "street": "1450 Kettner Boulevard",
    "city": "San Diego",
    "region": "California",
    "postcode": "92101",
    "country_id": "US",
    "telephone": "2137418080",
}
TASKS.append({
    "task_id": "phone_lookup_address_fix_jennifer_account_move_006",
    "family": "customer_address",
    "customer_entity_id": 26,
    "style": "terse",
    "difficulty": "medium",
    "shape": "state_mutation",
    "skills": ["R9", "A11"],
    "skill_chain": "reverse-look-up the phone number in the customer grid -> edit the stored address on that customer's account",
    "official_analogues": [
        "Find the customer name and email with phone number 2137418080",
        "I recently moved, my address is 231 Willow Way, Suite 100, Chicago, IL, 60601, update my information on OneStopShopping accordingly. Make it my default shipping and billing address.",
    ],
    "hard_criteria": [],
    "instruction": "The customer whose phone number is 2137418080 has moved across town. Update the address stored on their account to 1450 Kettner Boulevard, San Diego, California 92101.",
    "expected": t6_addr,
    "weights": [
        ("account_address_is_now_the_san_diego_record", 1.0),
    ],
    "checks_body": (
        "    row = _sole_address(state)\n"
        "    ok = (\n"
        "        row is not None\n"
        "        and _identity_ok(row)\n"
        "        and _street_ok(row)\n"
        "        and _locale_ok(row)\n"
        "    )\n"
        "    return {'account_address_is_now_the_san_diego_record': ok}"
    ),
    "success_criteria": [
        "customers[entity_id=26] holds exactly one address record.",
        "That record reads 1450 Kettner Boulevard, San Diego, California 92101, country_id US.",
        "It still names Jennifer White on telephone 2137418080.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "Jennifer White is customer 26; her single seeded address is 789 W Olympic Blvd, Los Angeles, California 90015, region_id 12.",
        "The move stays inside California on purpose: CustomerEdit's AddressForm has no region_id control (CustomerEdit.jsx:781-784 edits `region` as free text only), so a cross-state move would leave region_id pointing at the old state. Keeping California means region_id 12 stays truthful and the rubric never has to grade a stale field.",
        "The writeback is state.customers via updateCollectionItem (AppContext.jsx:270), not orderAddressOverrides - this is the lane's second A11 surface.",
        "Two skills only: medium, honestly labelled.",
    ],
})

# ---------------------------------------------------------------- 007
t7_addr = order_addr("Bob", "Jones", ["2100 Ross Avenue"], "Dallas", "Texas",
                     57, "75201", "2141918677")
TASKS.append({
    "task_id": "phone_lookup_address_fix_bobjones_largest_order_007",
    "family": "order_address",
    "style": "explicit",
    "difficulty": "hard",
    "shape": "state_mutation",
    "skills": ["R9", "R1", "A11"],
    "skill_chain": "reverse-look-up the phone number -> take the single largest order by order total among that customer's orders -> edit its shipping address",
    "official_analogues": [
        "Find the customer name and email with phone number 2065555555",
        "Modify the billing address of order #125 to 654 Elm Drive, Apartment 12, Miami, FL, 33101",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "A customer is disputing a delivery on his most expensive order with us - the one with the highest order total of all the orders on his account. Look him up by his phone number, 2141918677, open that order, and correct its shipping address to 2100 Ross Avenue, Dallas, Texas 75201. Keep the recipient name and the phone number on that address exactly as they are, and do not touch the billing address of that order or any of his other orders.",
    "expected": {"385": t7_addr},
    "weights": [
        ("largest_order_shipping_street_updated", 0.5),
        ("largest_order_shipping_city_state_zip_updated", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'largest_order_shipping_street_updated': _part_ok(state, '385', 'street'),\n"
        "        'largest_order_shipping_city_state_zip_updated': _part_ok(state, '385', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['385'] - the shipping address of order 000000193 - has street exactly ['2100 Ross Avenue'].",
        "That override records city Dallas, region Texas, region_id 57, postcode 75201, country_id US.",
        "The recipient is still Bob Jones on telephone 2141918677.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "Bob Jones is customer 4 (bbjones@gmail.com) with 10 orders. The maximum grand total is 224.40 on 000000193; the runner-up is 188.00 (000000073 and 000000288 tie there, but neither is the maximum), so the superlative is unique with a margin of 36.40.",
        "Order Total is a rendered column both on the customer's Orders tab (CustomerEdit.jsx:566) and on Sales > Orders, so the superlative is readable either way.",
        "Shipping address entity_id 385, billing 386.",
    ],
})

# ---------------------------------------------------------------- 008
t8_addr = order_addr("Mary", "Martin", ["1601 Collins Avenue"],
                     "Miami Beach", "Florida", 18, "33140", "3059876543")
TASKS.append({
    "task_id": "phone_lookup_address_fix_marymartin_pending_008",
    "family": "order_address",
    "style": "terse",
    "difficulty": "hard",
    "shape": "state_mutation",
    "skills": ["R9", "R5", "A11"],
    "skill_chain": "reverse-look-up the phone number -> filter that customer's orders to the one still Pending -> edit its billing address",
    "official_analogues": [
        "Find the customer name and email with phone number 2137418080",
        "Modify the billing address of order #300 to 987 Cedar Court, Los Angeles, CA, 90012",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "The caller on 3059876543 wants the billing address on her one still-pending order corrected to 1601 Collins Avenue, Miami Beach, Florida 33140.",
    "expected": {"610": t8_addr},
    "weights": [
        ("pending_order_billing_street_updated", 0.5),
        ("pending_order_billing_city_state_zip_updated", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'pending_order_billing_street_updated': _part_ok(state, '610', 'street'),\n"
        "        'pending_order_billing_city_state_zip_updated': _part_ok(state, '610', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['610'] - the billing address of order 000000305 - has street exactly ['1601 Collins Avenue'].",
        "That override records city Miami Beach, region Florida, region_id 18, postcode 33140, country_id US.",
        "The recipient is still Mary Martin on telephone 3059876543.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "Mary Martin is customer 8 (marym@gmail.com) with 6 orders: four Complete, one Canceled, and exactly one Pending - 000000305 of 2023-04-19. The predicate picks out a single row with no tie.",
        "That pending order is also her most recent, so the two readings of 'her open order' agree; the instruction still names the predicate it means.",
        "Billing address entity_id 610, shipping 609. The postcode moves 33139 -> 33140 so the ZIP is a genuinely changed value rather than a no-op.",
    ],
})

# ---------------------------------------------------------------- 009
t9_addr_a = order_addr("Adam", "Garcia", ["915 Boren Avenue"], "Seattle",
                       "Washington", 62, "98104", "2065555555")
t9_addr_b = dict(t9_addr_a)
TASKS.append({
    "task_id": "phone_lookup_address_fix_adamgarcia_may_orders_009",
    "family": "order_address",
    "style": "explicit",
    "difficulty": "hard",
    "shape": "state_mutation",
    "skills": ["R9", "R2", "A11"],
    "skill_chain": "reverse-look-up the phone number -> select that customer's orders inside a named month -> edit the billing address on each of them",
    "official_analogues": [
        "Find the customer name and email with phone number 2065555555",
        "Modify the billing address of order #299 to 456 Oak Avenue, Apartment 5B, New York, NY, 10001",
    ],
    "hard_criteria": ["derived_target", "multi_mutation"],
    "instruction": "A customer moved house at the end of April 2023, and every order he placed during May 2023 still shows his old billing address. His phone number is 2065555555. Find him, work out which of his orders fall in May 2023, and on each of those orders change the billing address to 915 Boren Avenue, Seattle, Washington 98104. Keep the recipient name and the phone number unchanged on both, and leave the shipping addresses of those orders alone.",
    "expected": {"568": t9_addr_a, "512": t9_addr_b},
    "weights": [
        ("may_first_order_billing_address_updated", 0.5),
        ("may_second_order_billing_address_updated", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'may_first_order_billing_address_updated': _full_ok(state, '568'),\n"
        "        'may_second_order_billing_address_updated': _full_ok(state, '512'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['568'] - the billing address of order 000000284 - reads 915 Boren Avenue, Seattle, Washington, region_id 62, 98104, US.",
        "orderAddressOverrides['512'] - the billing address of order 000000256 - reads the same address.",
        "Both records still name Adam Garcia on telephone 2065555555.",
    ],
    "setup_why": None,
    "setup_row": None,
    "injected_preconditions": [],
    "notes": [
        "Adam Garcia is customer 25 (gamingpro456@gmail.com) with 6 orders. Exactly two fall in May 2023: 000000284 on 2023-05-01 and 000000256 on 2023-05-14. His other four are 2022, so the month predicate has a clean boundary of over four months on either side.",
        "Billing address entity_ids 568 and 512; shipping 567 and 511 are deliberately out of scope.",
        "Purchase date renders with a full timestamp on both the customer Orders tab and Sales > Orders, so the month is readable without a date filter.",
    ],
})

# ---------------------------------------------------------------- 010
t10_addr = order_addr("Sarah", "Miller", ["1 Ferry Building"],
                      "San Francisco", "California", 12, "94111", "5107819902")
TASKS.append({
    "task_id": "phone_lookup_address_fix_sarahmiller_default_billing_010",
    "family": "order_address",
    "style": "explicit",
    "difficulty": "hard",
    "shape": "retrieval_writeback",
    "skills": ["R9", "R7", "A11"],
    "skill_chain": "reverse-look-up the phone number -> pick the account's default billing address out of two stored addresses -> copy it onto the billing address of that customer's most recent order",
    "official_analogues": [
        "Find the customer name and email with phone number +1 2058812302",
        "Modify the billing address of order #299 to 456 Oak Avenue, Apartment 5B, New York, NY, 10001",
    ],
    "hard_criteria": ["derived_target", "cross_section"],
    "instruction": "A customer rang from 5107819902 to say the invoice on her most recent order carries an out-of-date address. Her account now stores two addresses, and the one that counts is the default billing address shown on her Customer View page. Copy that address - street, city, state and ZIP - onto the billing address of her most recent order. Do not change the recipient name or the phone number on it, and leave that order's shipping address alone.",
    "expected": {"598": t10_addr},
    "weights": [
        ("latest_order_billing_street_matches_default_billing", 0.5),
        ("latest_order_billing_city_state_zip_match_default_billing", 0.5),
    ],
    "checks_body": (
        "    return {\n"
        "        'latest_order_billing_street_matches_default_billing': _part_ok(state, '598', 'street'),\n"
        "        'latest_order_billing_city_state_zip_match_default_billing': _part_ok(state, '598', 'locale'),\n"
        "    }"
    ),
    "success_criteria": [
        "orderAddressOverrides['598'] - the billing address of order 000000299 - has street exactly ['1 Ferry Building'].",
        "That override records city San Francisco, region California, region_id 12, postcode 94111, country_id US.",
        "The recipient is still Sarah Miller on telephone 5107819902.",
    ],
    "setup_why": "Sarah Miller's account now stores two addresses - the old Oakland one and a new San Francisco one that is her default billing and shipping address. The Oakland row is the distractor: it satisfies every part of the filter except being the default.",
    "setup_row": customer_row(
        5, "helloworld@yahoo.com", "Sarah", "Miller", "2023-04-19 21:45:07",
        [
            cust_addr(5, 5, "Sarah", "Miller", "321 Maple Avenue", "Oakland",
                      "California", 12, "94602", "5107819902",
                      "2023-04-19 21:45:07"),
            cust_addr(71, 5, "Sarah", "Miller", "1 Ferry Building",
                      "San Francisco", "California", 12, "94111",
                      "5107819902", "2023-05-30 09:12:44"),
        ],
        71, 71,
        "1 Ferry Building San Francisco California 94111",
        "1 Ferry Building San Francisco California 94111",
        "5107819902"),
    "injected_preconditions": [
        "customers[entity_id=5] now carries two addresses: the seeded Oakland record (address entity_id 5) and a new San Francisco record (address entity_id 71), with default_billing and default_shipping both repointed at 71 and billing_full / shipping_full rebuilt from it. billing_telephone is unchanged at 5107819902.",
        "The Oakland row is a deliberate distractor - same customer, same state, same phone - so the agent has to read which record the account treats as default rather than take the first row of the Addresses tab.",
    ],
    "notes": [
        "The default is readable: the Customer View tab renders a 'Default Billing Address' card resolved through customer.default_billing (CustomerEdit.jsx:345-346, 378-392). The Addresses tab table itself carries no default marker, which is why the instruction names the Customer View page.",
        "Order 000000299 (2023-05-31 06:55:09) is Sarah Miller's most recent of 15; the runner-up is 000000156 on 2023-04-28, a margin of 33 days.",
        "Address entity_id 71 is used rather than the 6 that CustomerEdit.saveAddress would allocate (max within the customer + 1), because seeded customer-address ids are globally unique 1..70 and 6 already belongs to customer 6. Nothing in the UI or the rubric reads the id.",
        "Billing address entity_id 598, shipping 597.",
    ],
})


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

REPLAY_TEMPLATE = '''"""Golden replay DRAFT for {tid}.

Not executed during authoring. Every step below is a click on a rendered
control; there is no page.goto after the initial landing on start_path "/".

Route: {route}
"""

STEPS = {steps}
'''


CUSTOMER_GRID_STEPS = [
    "Land on '/' (Dashboard).",
    "Click the left-rail 'Customers' menu, then the 'All Customers' item.",
    "Type the phone number into the grid's 'Search by keyword' box and submit the form.",
    "The grid narrows to one row; read the Name and Email cells.",
]

OPEN_CUSTOMER_STEPS = [
    "Tick that row's select checkbox, open the 'Actions' menu above the grid and click 'Edit' "
    "(the Action column ships hidden, so the mass action is the rendered route to the edit page).",
]

ORDER_GRID_STEPS = [
    "Click the left-rail 'Sales' menu, then the 'Orders' item.",
    "Type the customer's email into the grid's 'Search by keyword' box and submit; "
    "the Customer Email column is searched even though it is hidden by default.",
]

ROUTES = {
    "phone_lookup_address_fix_johnsmith_account_sync_001": (
        "/ -> Customers > All Customers (keyword 2058812302) -> Edit customer -> "
        "Addresses tab (read the account address) -> Orders tab -> order 000000009 -> "
        "Billing Address 'Edit' -> Save Order Address",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Addresses' tab and read the stored address: 4275 Magnolia Ridge Drive, Homewood, Alabama 35209.",
            "Open the 'Orders' tab; the newest Purchased timestamp is 2023-05-07 22:41:05 on 000000009. Click that order link.",
            "On the order view click 'Edit' next to Billing Address.",
            "Replace Street Address line 1 with '4275 Magnolia Ridge Drive', City with 'Homewood', "
            "leave the State/Province select on Alabama, and set Zip/Postal Code to '35209'.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_janedoe_shipping_sync_002": (
        "/ -> Customers > All Customers (keyword 4123671901) -> Edit customer -> "
        "Addresses tab -> Orders tab -> order 000000302 -> Shipping Address 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Addresses' tab and read: 88 Shadyside Terrace, Pittsburgh, Pennsylvania 15232.",
            "Open the 'Orders' tab; the newest Purchased timestamp is 2023-04-19 23:41:29 on 000000302. Click that order link.",
            "On the order view click 'Edit' next to Shipping Address.",
            "Set street line 1 to '88 Shadyside Terrace', City 'Pittsburgh', State/Province 'Pennsylvania', Zip '15232'.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_grace_both_addresses_003": (
        "/ -> Customers > All Customers (keyword 6175555555) -> Edit customer -> "
        "Addresses tab -> Orders tab -> order 000000065 -> Shipping 'Edit' -> Save -> "
        "Billing 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Addresses' tab and read: 412 Beacon Street, Boston, Massachusetts 02115.",
            "Open the 'Orders' tab; the newest Purchased timestamp is 2023-05-28 10:43:55 on 000000065. Click that order link.",
            "Click 'Edit' next to Shipping Address; set street '412 Beacon Street', City 'Boston', "
            "State/Province 'Massachusetts', Zip '02115'; click 'Save Order Address'. "
            "The form returns to the order view.",
            "Click 'Edit' next to Billing Address; enter the same four values; click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_lily_latest_complete_004": (
        "/ -> Customers > All Customers (keyword 7735555555) -> Sales > Orders "
        "(keyword harrypotterfan1@gmail.com) -> order 000000182 -> Billing 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + ORDER_GRID_STEPS + [
            "The grid is sorted Purchase Date descending. The newest row is 000000136 with status Canceled; "
            "the newest row with status Complete is 000000182 (2023-04-28 22:47:27). Click its 'View' link.",
            "Click 'Edit' next to Billing Address.",
            "Set street line 1 '55 Sheridan Road', City 'Evanston', State/Province 'Illinois', Zip '60202'.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_brian_suite_line_005": (
        "/ -> Sales > Orders (keyword 000000118) -> order view -> Shipping 'Edit' -> Save",
        [
            "Land on '/' (Dashboard).",
            "Click the left-rail 'Sales' menu, then the 'Orders' item.",
            "Type '000000118' into the grid's 'Search by keyword' box and submit.",
            "Click the 'View' link on the single remaining row.",
            "Click 'Edit' next to Shipping Address.",
            "Leave the first street input as '456 Las Vegas Blvd S' and type 'Suite 300' into the second street input.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_jennifer_account_move_006": (
        "/ -> Customers > All Customers (keyword 2137418080) -> Edit customer -> "
        "Addresses tab -> Edit -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Addresses' tab and click 'Edit' on the single address row.",
            "Set Street Address '1450 Kettner Boulevard', City 'San Diego', "
            "State/Province 'California', Zip/Postal Code '92101'.",
            "Click 'Save' on the address form.",
        ]),
    "phone_lookup_address_fix_bobjones_largest_order_007": (
        "/ -> Customers > All Customers (keyword 2141918677) -> Edit customer -> "
        "Orders tab (read Order Total) -> order 000000193 -> Shipping 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Orders' tab and compare the Order Total column across the ten rows; "
            "the maximum is $224.40 on 000000193. Click that order link.",
            "Click 'Edit' next to Shipping Address.",
            "Set street line 1 '2100 Ross Avenue', City 'Dallas', State/Province 'Texas', Zip '75201'.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_marymartin_pending_008": (
        "/ -> Customers > All Customers (keyword 3059876543) -> Sales > Orders "
        "(keyword marym@gmail.com) -> order 000000305 -> Billing 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + ORDER_GRID_STEPS + [
            "Six rows render with a Status column; exactly one reads Pending - 000000305. Click its 'View' link.",
            "Click 'Edit' next to Billing Address.",
            "Set street line 1 '1601 Collins Avenue', City 'Miami Beach', State/Province 'Florida', Zip '33140'.",
            "Click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_adamgarcia_may_orders_009": (
        "/ -> Customers > All Customers (keyword 2065555555) -> Edit customer -> "
        "Orders tab -> order 000000284 -> Billing 'Edit' -> Save -> back to the Orders tab -> "
        "order 000000256 -> Billing 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "Open the 'Orders' tab and read the Purchased column: two rows fall in May 2023 - "
            "000000284 (2023-05-01 00:42:12) and 000000256 (2023-05-14 05:22:46).",
            "Click 000000284; click 'Edit' next to Billing Address; set street '915 Boren Avenue', "
            "City 'Seattle', State/Province 'Washington', Zip '98104'; click 'Save Order Address'.",
            "Navigate back to the customer through Customers > All Customers and the same keyword search, "
            "open the Orders tab and click 000000256.",
            "Click 'Edit' next to Billing Address; enter the same four values; click 'Save Order Address'.",
        ]),
    "phone_lookup_address_fix_sarahmiller_default_billing_010": (
        "/ -> Customers > All Customers (keyword 5107819902) -> Edit customer -> "
        "Customer View tab (read Default Billing Address) -> Orders tab -> order 000000299 -> "
        "Billing 'Edit' -> Save",
        CUSTOMER_GRID_STEPS + OPEN_CUSTOMER_STEPS + [
            "The edit page opens on the 'Customer View' tab; read the 'Default Billing Address' card - "
            "1 Ferry Building, San Francisco, California, 94111. The Addresses tab lists the Oakland "
            "record first, which is the distractor.",
            "Open the 'Orders' tab; the newest Purchased timestamp is 2023-05-31 06:55:09 on 000000299. "
            "Click that order link.",
            "Click 'Edit' next to Billing Address.",
            "Set street line 1 '1 Ferry Building', City 'San Francisco', State/Province 'California', Zip '94111'.",
            "Click 'Save Order Address'.",
        ]),
}

for _task in TASKS:
    _route, _steps = ROUTES[_task["task_id"]]
    _task["route"] = _route
    _task["replay"] = _steps


def write(path, text):
    with open(path, "w") as handle:
        handle.write(text)


def main():
    index = {"schema_version": 2, "tasks": []}
    nemo_rows = []
    for task in TASKS:
        tid = task["task_id"]
        bundle = os.path.join(SITE_DIR, tid)
        os.makedirs(bundle, exist_ok=True)

        reward_py, nemo_py = reward_sources(task)
        write(os.path.join(bundle, "reward.py"), reward_py)
        write(os.path.join(bundle, "nemo_reward.py"), nemo_py)

        setup_text = None
        if task.get("setup_row"):
            setup_text = build_setup(task)
            write(os.path.join(bundle, "initial_setup.py"), setup_text)

        write(os.path.join(bundle, "task_instruction.json"), json.dumps({
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": task["difficulty"],
            "success_criteria": task["success_criteria"],
        }, indent=2) + "\n")

        metadata = {
            "style": task["style"],
            "difficulty": task["difficulty"],
            "shape": task["shape"],
            "skills": task["skills"],
            "skill_chain": task["skill_chain"],
            "official_analogues": task["official_analogues"],
            "hard_criteria": task["hard_criteria"],
            "topic": "phone_lookup_address_fix",
            "lane": 56,
            "inspiration_ids": [
                "webarena-208", "webarena-209", "webarena-210",
                "webarena-538", "webarena-539", "webarena-540",
                "webarena-541", "webarena-542",
            ],
            "authoring_notes": task["notes"],
        }
        if task["injected_preconditions"]:
            metadata["injected_preconditions"] = task["injected_preconditions"]

        write(os.path.join(bundle, "task.json"), json.dumps({
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
            "apps": [{
                "name": APP_DIR,
                "source_name": "shopping_admin",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
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
        }, indent=2) + "\n")

        row = {"task_payload": {
            "task_id": tid,
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
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_text,
                "eval_reward_code": nemo_py,
            },
        }}
        write(os.path.join(bundle, "nemo_task.json"),
              json.dumps(row, indent=2) + "\n")
        nemo_rows.append(row)

        write(os.path.join(REPLAY_DIR, tid + ".py"), REPLAY_TEMPLATE.format(
            tid=tid, route=task["route"],
            steps=json.dumps(task["replay"], indent=4)))

        index["tasks"].append({"task_id": tid, "path": "%s/task.json" % tid})

    write(os.path.join(BATCH_DIR, "index.json"),
          json.dumps(index, indent=2) + "\n")
    with open(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "w") as handle:
        for row in nemo_rows:
            handle.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
