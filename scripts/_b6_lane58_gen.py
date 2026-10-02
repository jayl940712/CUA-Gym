#!/usr/bin/env python3
"""Batch-6 lane 58 generator — shopping_admin, R2 -> A11.

Chain: locate the single order inside a stated absolute date window on the
Sales > Orders grid, then correct that order's billing or shipping address.

Writes ten bundles under output/tasks/shopping_admin/window_order_address_fix_*,
plus the batch GENERATION.md, index.json, nemo_tasks.jsonl and replay drafts.

Reads hub seed data only to derive ground truth; writes nothing under hub/.
"""

import datetime
import json
import os
import textwrap

ROOT = "/home/ubuntu/CUA-Gym"
HUB = os.path.join(ROOT, "hub/websites/webarena_shopping_admin_mock")
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/window_order_address_fix")
APP_DIR = "webarena_shopping_admin_mock"
URL_TOKEN = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

REGION_ID = {
    "Arizona": 4, "California": 12, "Colorado": 13, "District of Columbia": 16,
    "Florida": 18, "Georgia": 19, "Idaho": 22, "Illinois": 23,
    "Massachusetts": 32, "Minnesota": 34, "Texas": 57,
}

ORDERS = {o["entity_id"]: o for o in json.load(open(os.path.join(HUB, "src/data/orders.json")))}
GRID = json.load(open(os.path.join(HUB, "src/data/orderGrid.json")))


# --------------------------------------------------------------------------
# task table
# --------------------------------------------------------------------------

TASKS = [
    dict(
        n=1, slug="apr2022_boise_relocation", order=112, addr_type="billing",
        win=("2022-04-11", "2022-04-14"), win_text="4/11/2022 and 4/14/2022",
        style="terse", shape="retrieval_writeback", start="/",
        changes=dict(street=["1420 Fremont Street"], city="Boise",
                     region="Idaho", postcode="83702"),
        instruction=(
            "Exactly one order was placed between 4/11/2022 and 4/14/2022. That "
            "customer has moved: change the billing address on it to 1420 Fremont "
            "Street, Boise, ID 83702. Leave the name and phone alone."),
    ),
    dict(
        n=2, slug="may2022_wilshire_suite", order=219, addr_type="shipping",
        win=("2022-05-23", "2022-05-27"), win_text="5/23/2022 and 5/27/2022",
        style="explicit", shape="derived_target_mutation", start="/",
        changes=dict(street=["700 Wilshire Boulevard", "Suite 410"],
                     postcode="90017"),
        instruction=(
            "Open Sales > Orders and use the Purchase Date filter to list orders "
            "placed between 5/23/2022 and 5/27/2022; exactly one row comes back. "
            "Open that order and edit its shipping address so that Street Address "
            "line 1 reads 700 Wilshire Boulevard, line 2 reads Suite 410, and the "
            "Zip/Postal Code reads 90017. City, state, name and phone stay as they "
            "are."),
    ),
    dict(
        n=3, slug="jul2022_tempe_city_zip", order=7, addr_type="billing",
        win=("2022-07-14", "2022-07-18"), win_text="7/14/2022 and 7/18/2022",
        style="terse", shape="retrieval_writeback", start="/",
        changes=dict(city="Tempe", postcode="85281"),
        instruction=(
            "Only one order falls between 7/14/2022 and 7/18/2022, and its billing "
            "address has the wrong city. Correct it to Tempe, AZ 85281. The street "
            "line stays as it is."),
    ),
    dict(
        n=4, slug="aug2022_atlanta_move", order=190, addr_type="shipping",
        win=("2022-08-10", "2022-08-13"), win_text="8/10/2022 and 8/13/2022",
        style="terse", shape="derived_target_mutation", start="/admin/sales/order/",
        changes=dict(street=["2115 Peachtree Road"], city="Atlanta",
                     region="Georgia", postcode="30309", telephone="4045550163"),
        instruction=(
            "One order sits between 8/10/2022 and 8/13/2022. Redirect it: its "
            "shipping address becomes 2115 Peachtree Road, Atlanta, GA 30309, phone "
            "4045550163."),
    ),
    dict(
        n=5, slug="sep2022_pacific_avenue", order=44, addr_type="billing",
        win=("2022-09-04", "2022-09-09"), win_text="9/4/2022 and 9/9/2022",
        style="terse", shape="retrieval_writeback", start="/",
        changes=dict(street=["1900 Pacific Avenue"]),
        instruction=(
            "A single order was placed between 9/4/2022 and 9/9/2022. The street on "
            "its billing address is wrong: it should read 1900 Pacific Avenue. "
            "Everything else on that address stays put."),
    ),
    dict(
        n=6, slug="sep2022_minneapolis_move", order=254, addr_type="shipping",
        win=("2022-09-13", "2022-09-17"), win_text="9/13/2022 and 9/17/2022",
        style="terse", shape="derived_target_mutation", start="/",
        changes=dict(street=["1201 Nicollet Mall"], city="Minneapolis",
                     region="Minnesota", postcode="55403"),
        instruction=(
            "Find the one order placed between 9/13/2022 and 9/17/2022 and move its "
            "shipping address to 1201 Nicollet Mall, Minneapolis, MN 55403. Keep the "
            "name and phone number."),
    ),
    dict(
        n=7, slug="oct2022_brickell_apartment", order=31, addr_type="billing",
        win=("2022-10-12", "2022-10-25"), win_text="10/12/2022 and 10/25/2022",
        style="explicit", shape="retrieval_writeback", start="/",
        changes=dict(street=["88 Brickell Bay Drive", "Apartment 3106"],
                     postcode="33131"),
        instruction=(
            "In Sales > Orders, filter Purchase Date from 10/12/2022 to 10/25/2022 — "
            "one order matches. Open it and edit its billing address: Street Address "
            "line 1 becomes 88 Brickell Bay Drive, line 2 becomes Apartment 3106, and "
            "the Zip/Postal Code becomes 33131. Leave city, state, name and phone "
            "untouched."),
    ),
    dict(
        n=8, slug="nov2022_cambridge_phone", order=166, addr_type="shipping",
        win=("2022-10-30", "2022-11-04"), win_text="10/30/2022 and 11/4/2022",
        style="terse", shape="derived_target_mutation", start="/",
        changes=dict(telephone="6175550188"),
        instruction=(
            "Between 10/30/2022 and 11/4/2022 we took exactly one order. The phone "
            "number on its shipping address is wrong — replace it with 6175550188 and "
            "change nothing else."),
    ),
    dict(
        n=9, slug="feb2023_washington_dc_move", order=105, addr_type="billing",
        win=("2023-02-04", "2023-02-08"), win_text="2/4/2023 and 2/8/2023",
        style="explicit", shape="retrieval_writeback", start="/admin/sales/order/",
        changes=dict(street=["4400 Wisconsin Avenue NW", "Unit 12"],
                     city="Washington", region="District of Columbia",
                     postcode="20016", telephone="2025550119"),
        instruction=(
            "Use the Orders grid's Purchase Date filter to find the single order "
            "placed between 2/4/2023 and 2/8/2023, then edit that order's billing "
            "address. Street Address line 1 is 4400 Wisconsin Avenue NW and line 2 is "
            "Unit 12; the city is Washington, the state is District of Columbia, the "
            "Zip/Postal Code is 20016 and the phone number is 2025550119. The name "
            "stays as it is."),
    ),
    dict(
        n=10, slug="may2023_santa_barbara", order=230, addr_type="shipping",
        win=("2023-05-16", "2023-05-22"), win_text="5/16/2023 and 5/22/2023",
        style="terse", shape="retrieval_writeback", start="/",
        changes=dict(street=["955 Coast Village Road"], city="Santa Barbara",
                     postcode="93108"),
        instruction=(
            "Exactly one order was placed between 5/16/2023 and 5/22/2023. Update its "
            "shipping address to 955 Coast Village Road, Santa Barbara, CA 93108, "
            "leaving the name and phone as they are."),
    ),
]

ANALOGUES = [
    "Modify the billing address of order #299 to 456 Oak Avenue, Apartment 5B, New York, NY, 10001",
    "Modify the billing address of order #65 to 789 Pine Lane, San Francisco, CA, 94102",
    "Modify the billing address of order #301 to 321 Birch Boulevard, Suite 200, Dallas, TX, 75201",
    "Modify the billing address of order #300 to 987 Cedar Court, Los Angeles, CA, 90012",
    "Modify the billing address of order #125 to 654 Elm Drive, Apartment 12, Miami, FL, 33101",
    "Change the delivery address for my oldest order in 2023 to 155 5th Street, San Francisco, CA.",
]

INSPIRATIONS = ["webarena-538", "webarena-539", "webarena-540", "webarena-541",
                "webarena-542", "webarena-362", "webarena-796"]


# --------------------------------------------------------------------------
# ground truth derivation
# --------------------------------------------------------------------------

def d(s):
    return datetime.date(*map(int, s.split("-")))


def window_report(win):
    """Rows the created_at filter matches, plus render-shift safety facts."""
    lo, hi = win
    inside = [r for r in GRID if lo <= r["created_at"][:10] <= hi]
    # nearest stored order-day strictly outside on each side
    before = max((r["created_at"][:10] for r in GRID if r["created_at"][:10] < lo), default=None)
    after = min((r["created_at"][:10] for r in GRID if r["created_at"][:10] > hi), default=None)
    after_rows = [r for r in GRID if after and r["created_at"][:10] == after]
    # a row renders one day EARLY when its UTC hour < 5 (America/New_York)
    after_min_render = None
    if after_rows:
        after_min_render = min(
            (d(r["created_at"][:10]) - datetime.timedelta(days=1)).isoformat()
            if int(r["created_at"][11:13]) < 5 else r["created_at"][:10]
            for r in after_rows)
    return dict(inside=inside, before=before, after=after,
                after_min_render=after_min_render,
                gap_before=(d(lo) - d(before)).days if before else None,
                gap_after=(d(after) - d(hi)).days if after else None)


def address_of(order_id, addr_type):
    for a in ORDERS[order_id]["addresses"]:
        if a["address_type"] == addr_type:
            return a
    raise SystemExit("no %s address on order %s" % (addr_type, order_id))


def expected_record(seed, changes):
    """The record OrderAddressEdit.save() writes for this edit.

    save() (OrderAddressEdit.jsx:151-179) posts all fifteen form fields. Every
    field the agent does not touch keeps its pre-populated seed value, and the
    optional name fields the seed omits post as empty strings. `region` is
    recomputed from the selected `region_id` because the US region list is
    non-empty, so it is always the option label.
    """
    street = changes.get("street")
    if street is None:
        raw = seed["street"]
        street = raw if isinstance(raw, list) else str(raw).split("\n")
    street = [s for s in street if s != ""]
    region = changes.get("region", seed["region"])
    return {
        "prefix": "",
        "firstname": seed["firstname"],
        "middlename": "",
        "lastname": seed["lastname"],
        "suffix": "",
        "company": "",
        "street": street,
        "city": changes.get("city", seed["city"]),
        "country_id": "US",
        "region": region,
        "region_id": REGION_ID[region],
        "postcode": changes.get("postcode", seed["postcode"]),
        "vat_id": "",
        "telephone": changes.get("telephone", seed["telephone"]),
        "fax": "",
    }


def build(task):
    order = ORDERS[task["order"]]
    seed = address_of(task["order"], task["addr_type"])
    rep = window_report(task["win"])
    if len(rep["inside"]) != 1 or rep["inside"][0]["entity_id"] != task["order"]:
        raise SystemExit("window %s does not isolate order %s (got %s)" % (
            task["win"], task["order"], [r["entity_id"] for r in rep["inside"]]))
    hour = int(order["created_at"][11:13])
    if hour < 5:
        raise SystemExit("order %s renders a day early" % task["order"])
    if rep["after_min_render"] and rep["after_min_render"] <= task["win"][1]:
        raise SystemExit("a later order renders inside window %s" % (task["win"],))
    task = dict(task)
    task["task_id"] = "window_order_address_fix_%s_%03d" % (task["slug"], task["n"])
    task["order_row"] = order
    task["seed_address"] = seed
    task["address_id"] = str(seed["entity_id"])
    task["expected"] = expected_record(seed, task["changes"])
    task["report"] = rep
    return task


# --------------------------------------------------------------------------
# file bodies
# --------------------------------------------------------------------------

REWARD_TMPL = '''"""Deterministic reward for {task_id}.

Success criteria:
  * `orderAddressOverrides` holds exactly one key, the order-address id {address_id}
    ({addr_type} address of order {increment_id}, the only order whose stored
    Purchase Date falls between {win_lo} and {win_hi}).
  * That record equals the address the Edit Order Address form writes for the
    requested correction, field for field.

Reads only `current_state` from the immutable evidence bundle; never diffs
against `initial_state`. Ground truth is fixed by the frozen seed of
webarena_shopping_admin_mock in ./hub/.
"""

import json

ADDRESS_ID = "{address_id}"
COMPONENT_NAME = "{component}"
COMPONENT_WEIGHTS = {{COMPONENT_NAME: 1.0}}

EXPECTED = json.loads(r"""
{expected_json}
""")


def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {{}}


def _street(value):
    """Normalise `street` to a list of trimmed lines.

    The seeded order addresses store `street` as a plain string while
    OrderAddressEdit.save() writes a list, so both shapes have to compare.
    """
    if isinstance(value, list):
        parts = [str(v).strip() for v in value]
    else:
        parts = [p.strip() for p in str(value if value is not None else "").split("\\n")]
    return [p for p in parts if p != ""]


def _matches(record):
    if not isinstance(record, dict):
        return False
    if _street(record.get("street")) != _street(EXPECTED["street"]):
        return False
    if str(record.get("region_id", "")).strip() != str(EXPECTED["region_id"]):
        return False
    for key in ("prefix", "firstname", "middlename", "lastname", "suffix",
                "company", "city", "country_id", "region", "postcode",
                "vat_id", "telephone", "fax"):
        got = record.get(key)
        got = "" if got is None else str(got).strip()
        if got != EXPECTED[key]:
            return False
    return True


def _checks(state):
    overrides = state.get("orderAddressOverrides")
    if not isinstance(overrides, dict):
        return {{COMPONENT_NAME: False}}
    keys = set(str(k) for k in overrides)
    ok = keys == {{ADDRESS_ID}} and _matches(overrides.get(ADDRESS_ID))
    return {{COMPONENT_NAME: bool(ok)}}


def evaluate(evidence):
    checks = _checks(_state(evidence))
    components = []
    for name in COMPONENT_WEIGHTS:
        satisfied = bool(checks.get(name))
        components.append({{
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if satisfied else 0.0,
            "details": {{"satisfied": satisfied}},
        }})
    total = 0.0
    for component in components:
        total += component["score"]
    return {{"score": round(total, 6), "components": components}}
'''

NEMO_REWARD_TMPL = '''"""NeMo-Gym reward program for {task_id}.

Implements exactly the rubric of reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url_token}"

ADDRESS_ID = "{address_id}"
COMPONENT_NAME = "{component}"
COMPONENT_WEIGHTS = {{COMPONENT_NAME: 1.0}}

EXPECTED = json.loads(r"""
{expected_json}
""")


def _street(value):
    if isinstance(value, list):
        parts = [str(v).strip() for v in value]
    else:
        parts = [p.strip() for p in str(value if value is not None else "").split("\\n")]
    return [p for p in parts if p != ""]


def _matches(record):
    if not isinstance(record, dict):
        return False
    if _street(record.get("street")) != _street(EXPECTED["street"]):
        return False
    if str(record.get("region_id", "")).strip() != str(EXPECTED["region_id"]):
        return False
    for key in ("prefix", "firstname", "middlename", "lastname", "suffix",
                "company", "city", "country_id", "region", "postcode",
                "vat_id", "telephone", "fax"):
        got = record.get(key)
        got = "" if got is None else str(got).strip()
        if got != EXPECTED[key]:
            return False
    return True


def score_state(state):
    overrides = state.get("orderAddressOverrides")
    if not isinstance(overrides, dict):
        return 0.0
    keys = set(str(k) for k in overrides)
    if keys != {{ADDRESS_ID}}:
        return 0.0
    if not _matches(overrides.get(ADDRESS_ID)):
        return 0.0
    return round(COMPONENT_WEIGHTS[COMPONENT_NAME], 6)


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state") or {{}}
        if not isinstance(state, dict):
            state = {{}}
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

SETUP_TMPL = '''"""NeMo-Gym setup program for {task_id}.

Two writes, both read-modify-write over the whole session document:

1. `orderOverrides["{order_id}"]` gets the order's own seeded `updated_at`
   back. That is a value-for-value no-op on every rendered surface — the only
   readers of `orderOverrides` are selectors.js:48 (order view) and
   selectors.js:117 (grid), and both receive the identical timestamp — but it
   makes the grid's `if (!patch) return row` short circuit fall through, so
   the address the agent saves also reaches the grid's Billing/Shipping
   Address columns instead of leaving the order view and the grid disagreeing.
2. `orderAddressOverrides` is pinned empty, so the post-setup state scores
   exactly 0.0.

The pristine session document is read back from GET /go?sid= first and the
patched document is POSTed whole, so no top-level key is dropped whichever way
the state API treats a partial set.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url_token}"

ORDER_ID = "{order_id}"
SEEDED_UPDATED_AT = "{updated_at}"


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

    overrides = state.get("orderOverrides")
    if not isinstance(overrides, dict):
        overrides = {{}}
    patch = overrides.get(ORDER_ID)
    if not isinstance(patch, dict):
        patch = {{}}
    patch = dict(patch)
    patch["updated_at"] = SEEDED_UPDATED_AT
    overrides[ORDER_ID] = patch
    state["orderOverrides"] = overrides
    state["orderAddressOverrides"] = {{}}

    written = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    written.raise_for_status()
    print("SETUP OK")


main()
'''

REPLAY_TMPL = '''"""Golden replay draft for {task_id}.

Click-only after the landing page: admin rail > Sales > Orders, the grid's own
Filters panel for the Purchase Date window, the matched row's View link, the
Address Information block's Edit link, then the address form. No page.goto()
after the initial load and no constructed URL.

Retrieval: Purchase Date from {win_lo_us} to {win_hi_us} returns exactly one row,
order {increment_id} ({customer}, stored {created_at} UTC).
Action: {addr_type} address id {address_id} -> the corrected record.
"""

ADDRESS_ID = "{address_id}"
ORDER_ID = "{order_id}"


def run(page, base_url, sid):
    page.goto("%s{start}?sid=%s" % (base_url.rstrip("/"), sid))
    page.wait_for_selector("#menu-sales")

    # 1. admin rail -> Sales -> Orders
    page.click("#menu-sales")
    page.click('#menu-sales .submenu a:has-text("Orders")')
    page.wait_for_selector('[data-grid-id="sales_order_grid"] table.data-grid')

    # 2. the retrieval: the Purchase Date window, typed into the grid's own
    #    range filter (both inputs are plain type="text" on this mock)
    page.click('[data-action="grid-filter-expand"]')
    page.fill("#filter-sales_order_grid-created_at-from", "{win_lo_us}")
    page.fill("#filter-sales_order_grid-created_at-to", "{win_hi_us}")
    page.click('[data-action="grid-filter-apply"]')
    page.wait_for_timeout(300)

    # 3. open the single matched row, then its {addr_type} address
    page.click('tr:has(#idscheck%s) a.action-menu-item' % ORDER_ID)
    page.wait_for_selector(".order-{addr_type}-address")
    page.click('.order-{addr_type}-address a.sales-order-edit-link')
    page.wait_for_selector("#street_0")

    # 4. the edit
{edit_lines}
    page.click("#save")
    page.wait_for_timeout(500)


# Address Edit link: /admin/sales/order/address/address_id/{address_id}/
# Writer  patchOrderAddress  AppContext.jsx:209 -> state.orderAddressOverrides
# Reader  getOrderAddress    selectors.js:145   -> the form
# Reader  getOrder           selectors.js:53-59 -> order.addresses, rendered by
#         AddressInformation OrderBlocks.jsx:192-228 on the order view.
'''


def us_date(iso):
    y, m, dd = iso.split("-")
    return "%d/%d/%s" % (int(m), int(dd), y)


def edit_lines(task):
    lines = []
    ch = task["changes"]
    exp = task["expected"]
    if "street" in ch:
        lines.append('    page.fill("#street_0", %r)' % exp["street"][0])
        lines.append('    page.fill("#street_1", %r)'
                     % (exp["street"][1] if len(exp["street"]) > 1 else ""))
    if "city" in ch:
        lines.append('    page.fill("#city", %r)' % exp["city"])
    if "region" in ch:
        lines.append('    page.select_option("#region_id", %r)' % str(exp["region_id"]))
    if "postcode" in ch:
        lines.append('    page.fill("#postcode", %r)' % exp["postcode"])
    if "telephone" in ch:
        lines.append('    page.fill("#telephone", %r)' % exp["telephone"])
    return "\n".join(lines)


def write(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(body)


def emit(task):
    tid = task["task_id"]
    bundle = os.path.join(OUT, tid)
    order = task["order_row"]
    seed = task["seed_address"]
    expected_json = json.dumps(task["expected"], indent=1)
    component = "order_address_%s_is_exactly_the_corrected_record" % task["address_id"]
    win_lo, win_hi = task["win"]

    reward = REWARD_TMPL.format(
        task_id=tid, address_id=task["address_id"], addr_type=task["addr_type"],
        increment_id=order["increment_id"], win_lo=win_lo, win_hi=win_hi,
        component=component, expected_json=expected_json)
    nemo_reward = NEMO_REWARD_TMPL.format(
        task_id=tid, url_token=URL_TOKEN, address_id=task["address_id"],
        component=component, expected_json=expected_json)
    setup = SETUP_TMPL.format(
        task_id=tid, url_token=URL_TOKEN, order_id=str(task["order"]),
        updated_at=order["updated_at"])

    criteria = [
        "state.orderAddressOverrides holds exactly one key, \"%s\" - the %s address of "
        "order %s, the only order whose Purchase Date falls between %s and %s."
        % (task["address_id"], task["addr_type"], order["increment_id"],
           us_date(win_lo), us_date(win_hi)),
        "That record reads street %s, city %s, region %s (region_id %d), postcode %s, "
        "country_id US, telephone %s, firstname %s, lastname %s, and empty prefix, "
        "middlename, suffix, company, vat_id and fax."
        % (task["expected"]["street"], task["expected"]["city"],
           task["expected"]["region"], task["expected"]["region_id"],
           task["expected"]["postcode"], task["expected"]["telephone"],
           task["expected"]["firstname"], task["expected"]["lastname"]),
        "No other order address carries an override.",
    ]

    instruction = " ".join(task["instruction"].split())

    write(os.path.join(bundle, "reward.py"), reward)
    write(os.path.join(bundle, "nemo_reward.py"), nemo_reward)
    write(os.path.join(bundle, "initial_setup.py"), setup)
    write(os.path.join(bundle, "task_instruction.json"), json.dumps({
        "task_id": tid,
        "task_instruction": instruction,
        "app_dir": APP_DIR,
        "start_path": task["start"],
        "difficulty": "medium",
        "success_criteria": criteria,
    }, indent=2) + "\n")

    rep = task["report"]
    notes = [
        "Window %s..%s (stored dates) matches exactly one grid row: order %s. The "
        "nearest stored order-day before the window is %s (%d days clear) and after "
        "is %s (%d days clear)."
        % (win_lo, win_hi, order["increment_id"], rep["before"], rep["gap_before"],
           rep["after"], rep["gap_after"]),
        "gridUtils.compareDates (gridUtils.js:162-170) compares the STORED "
        "`created_at` string, inclusive at both ends, so the matched set is timezone "
        "free. The grid RENDERS America/New_York (formatters.js:41-46), which puts a "
        "row a day early when its UTC hour is below 5. Order %s is stored at %s UTC "
        "(hour %s), so its rendered Purchase Date is the same calendar day, and the "
        "first order after the window renders no earlier than %s."
        % (order["increment_id"], order["created_at"], order["created_at"][11:13],
           rep["after_min_render"]),
        "Writer patchOrderAddress AppContext.jsx:209 -> state.orderAddressOverrides["
        "\"%s\"]; readers getOrderAddress selectors.js:145 (the form) and getOrder "
        "selectors.js:53-59, whose merged addresses AddressInformation "
        "OrderBlocks.jsx:192-228 renders on the order view. Same key, verified."
        % task["address_id"],
        "The instruction never names the order, so an agent that skips the date "
        "window has no way to reach address %s and scores 0.0."
        % task["address_id"],
    ]

    write(os.path.join(bundle, "task.json"), json.dumps({
        "schema_version": 2,
        "task_id": tid,
        "instruction": instruction,
        "apps": [{
            "name": APP_DIR,
            "source_name": "shopping_admin",
            "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
            "start_path": task["start"],
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
            "shape": task["shape"],
            "skills": ["R2", "A11"],
            "skill_chain": (
                "filter the Sales > Orders grid to the Purchase Date window %s-%s, "
                "which returns a single order -> correct that order's %s address"
                % (us_date(win_lo), us_date(win_hi), task["addr_type"])),
            "derived_from": None,
            "official_analogues": ANALOGUES[:2] if task["addr_type"] == "billing"
                                  else [ANALOGUES[2], ANALOGUES[5]],
            "injected_preconditions": [
                "orderOverrides[\"%s\"].updated_at set to the order's own seeded value "
                "%s. A value-for-value no-op on every surface, present only so "
                "getOrderGridRows' `if (!patch) return row` short circuit "
                "(selectors.js:117) falls through and the saved address also reaches "
                "the grid's hidden Billing/Shipping Address columns; without it the "
                "order view and the grid disagree (CORRECTIONS #91)."
                % (task["order"], order["updated_at"]),
                "orderAddressOverrides pinned to {} so the post-setup state scores 0.0.",
            ],
            "topic": "window_order_address_fix",
            "lane": 58,
            "inspiration_ids": INSPIRATIONS,
            "authoring_notes": notes,
        },
    }, indent=2) + "\n")

    nemo = {"task_payload": {
        "task_id": tid,
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP_DIR],
        "start_urls": [],
        "intent": instruction,
        "eval": {
            "eval_types": ["string_match"],
            "reference_answers": None,
            "note": "unused - CUA-Gym reward code is authoritative",
        },
        "cuagym": {
            "bundle_id": tid,
            "app_dir": APP_DIR,
            "initial_setup": setup,
            "eval_reward_code": nemo_reward,
        },
    }}
    write(os.path.join(bundle, "nemo_task.json"), json.dumps(nemo, indent=2) + "\n")

    replay = REPLAY_TMPL.format(
        task_id=tid, win_lo_us=us_date(win_lo), win_hi_us=us_date(win_hi),
        increment_id=order["increment_id"],
        customer="%s %s" % (seed["firstname"], seed["lastname"]),
        created_at=order["created_at"], addr_type=task["addr_type"],
        address_id=task["address_id"], order_id=str(task["order"]),
        start=task["start"], edit_lines=edit_lines(task))
    write(os.path.join(BATCH, "replays", tid + ".py"), replay)
    return nemo


def main():
    built = [build(t) for t in TASKS]
    rows = [emit(t) for t in built]

    write(os.path.join(BATCH, "index.json"), json.dumps({
        "schema_version": 2,
        "tasks": [{"task_id": t["task_id"], "path": "%s/task.json" % t["task_id"]}
                  for t in built],
    }, indent=2) + "\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    # ---- GENERATION.md -------------------------------------------------
    lines = []
    for t in built:
        rep = t["report"]
        lines.append(
            "| `%s` | %s | %s..%s | %s | %s / addr %s | %s d before, %s d after |"
            % (t["task_id"], t["style"], us_date(t["win"][0]), us_date(t["win"][1]),
               t["order_row"]["increment_id"], t["addr_type"], t["address_id"],
               rep["gap_before"], rep["gap_after"]))
    write(os.path.join(BATCH, "GENERATION.md"), GENERATION.format(
        table="\n".join(lines)))
    print("wrote %d bundles" % len(built))
    for t in built:
        print(" ", t["task_id"], t["order_row"]["increment_id"], t["addr_type"],
              t["address_id"], t["report"]["gap_before"], t["report"]["gap_after"])


GENERATION = """# Lane 58 — `window_order_address_fix` (shopping_admin, R2 -> A11)

Ten `medium` bundles, each **exactly two skills**: `R2` (temporal filter on the
Sales > Orders grid) feeding `A11` (order address / contact record edit).

## The chain

Sales > Orders -> Filters -> Purchase Date `from`/`to` -> the window returns
**exactly one row** -> View -> Address Information -> Edit -> correct the
address -> Save Order Address.

The order is **never named**. The instruction states an absolute M/D/YYYY window
and nothing else that identifies the row, so an agent that skips the retrieval
cannot reach the address id the rubric grades and scores 0.0. The new address
text is dictated, exactly as the five official analogues `webarena-538..542`
dictate theirs — see "The brief's 'derived value' instruction" below.

| task | style | window | order | address | isolation |
|---|---|---|---|---|---|
{table}

## Mechanism claims verified in source

* **Writer.** `patchOrderAddress` — `src/context/AppContext.jsx:209-217` —
  merges into `state.orderAddressOverrides[String(addressId)]`. Its single call
  site is `OrderAddressEdit.save()` at `src/pages/sales/OrderAddressEdit.jsx:160`,
  behind the `#save` button at `:207-216`.
* **Readers, same key.** `getOrderAddress` — `src/utils/selectors.js:145-150` —
  serves the form. `getOrder` — `src/utils/selectors.js:53-59` — merges the
  override into `order.addresses`, and `AddressInformation`
  (`src/components/sales/OrderBlocks.jsx:192-228`) renders those merged rows on
  the order view, mounted at `src/pages/sales/OrderView.jsx:130`. **The address
  edit persists and is visible.** The `Edit` links at `OrderBlocks.jsx:205` and
  `:218` are the click path to
  `/admin/sales/order/address/address_id/<entity_id>/`.
* **The form's write set.** `save()` posts all fifteen fields
  (`OrderAddressEdit.jsx:160-176`). Untouched fields keep their pre-populated
  seed value; the six optional name/company/VAT/fax fields the seed omits post
  as `""`; `region` is recomputed from the selected `region_id` because the US
  region list is non-empty (`:157-159`), so it is always the option label from
  `US_REGIONS` (`src/components/sales/directoryData.js`). Every rubric asserts
  the full fifteen-key record.
* **Street shape.** The seed stores `street` as a plain **string**
  (`src/data/orders.json`); `save()` writes a **list** of non-empty lines. Both
  rewards normalise both sides (`_street`).
* **Validation.** `validate()` (`:131-149`) requires firstname, lastname,
  street[0], country_id, region_id (US is in `REGION_REQUIRED_COUNTRIES`), city
  and telephone. Every dictated address supplies all of them.

## The admin Orders grid: sort, date rendering, filtering

* **Default sort** is `{{field: 'created_at', direction: 'desc'}}` —
  `src/pages/sales/OrdersGrid.jsx:413`. `created_at` declares no `sortValue` and
  no `compare`, so `applyGridState` falls through to `defaultCompare`
  (`src/utils/gridUtils.js:200-206`): `Number()` is `NaN` on
  `"2022-04-13 15:27:30"`, so it ends at
  `localeCompare(..., {{numeric: true, sensitivity: 'base'}})`. The format is
  fixed-width `YYYY-MM-DD HH:MM:SS`, so that ordering is chronological. No task
  here depends on the sort — the window returns one row.
* **The date filter compares the STORED string.** `compareDates`
  (`gridUtils.js:162-170`) slices `created_at[:10]` and compares it against
  `toIsoDate(from)` / `toIsoDate(to)`, **inclusive at both ends**. `toIsoDate`
  (`:149-160`) accepts both `M/D/YYYY` and ISO, so the M/D/YYYY the instruction
  states is exactly what the filter uses. The matched set is therefore
  timezone-free and exact.
* **Rendering is NOT.** `formatDateTime` (`src/utils/formatters.js:41-46`) goes
  through `tzParts`, which is `America/New_York` (`:10`). Any row stored with a
  UTC hour below 5 renders **a day earlier** than it filters. This is a real
  hazard on this grid across the full 308-row corpus — e.g. order 000000284 is
  stored `2023-05-01 00:42:12` and renders `Apr 30, 2023`; recomputing every row
  against `America/New_York` with DST gives **59 of the 308 grid rows rendering a
  day earlier than they filter**. Every target here was
  screened to a UTC hour >= 5 (lowest used: 06:07:31, order 000000105), and every
  window's end is at least one day clear of the earliest possible rendered date
  of the next stored order-day, so the filtered set and the rendered set agree.
* **Page size is 200** (`GRID_PAGE_SIZES.sales_order_grid`, `gridUtils.js:35-39`,
  which overrides `OrdersGrid.jsx:414`'s `defaultPageSize={{20}}`). A one-row
  result never paginates.
* Filter controls are `[name="created_at[from]"]` / `[name="created_at[to]"]`,
  ids `#filter-sales_order_grid-created_at-from` / `-to`, plain `type="text"`
  (`AdminGrid.jsx:674-703`, `name` attributes at `:687` and `:697`), inside the
  eagerly-mounted, CSS-hidden panel (`:578`) opened by `[data-action="grid-filter-expand"]` and applied by
  `[data-action="grid-filter-apply"]`.

## Isolation margins (checked, not quoted)

The 308-row corpus spans 2022-01-08 to 2023-05-31 over 220 distinct order-days.
Each window above was chosen so that:

1. exactly one stored `created_at[:10]` falls inside it — recomputed in the
   generator, which aborts if the count is not 1 or the row is not the intended
   order;
2. the nearest stored order-day outside the window is 1 day clear before the
   start and 2 days clear after the end for every task (the table's last column
   gives the measured gaps). One day is enough on the leading side because the
   America/New_York render shift only ever moves a row *earlier*, i.e. further
   away from the window; two days on the trailing side is what covers a shift
   *into* the window's last day;
3. the target's UTC hour is >= 5, so its rendered Purchase Date equals its
   stored date;
4. the earliest rendered date of the first order-day after the window is still
   strictly after the window's end, so no row appears inside the window on
   screen while being excluded by the filter.

Only 22 order-days in the whole corpus are single-order days with >= 3 clear days
on both sides; ten of those were used, and 299 / 65 / 301 / 300 / 125 were
excluded outright because they are the gold entities of `webarena-538..542`.

## The brief's "derived value" instruction, and why the value is dictated

The lane brief asks for the corrected address itself to be derived from
somewhere on the site. **That cannot be done inside a two-skill budget.** Any
on-site source for a replacement address is a second retrieval (`R9` on a
customer record, or `R7` across orders), which makes the task three skills and
the batch-6 gate rejects it. Two candidate rescues were examined and rejected:

* *"copy the billing address onto the shipping address of the same order"* —
  **all seeded orders carry identical billing and shipping addresses** (checked
  across the corpus, e.g. order 000000001's addresses 1 and 2 are field-for-field
  equal), so the untouched state already satisfies it and it scores 1.0 cold.
  This is the same candidate batch 5 dropped, and it is dead for a second reason.
* *deriving the phone from the customer grid* — a second retrieval, same gate
  failure.

The requirement the brief is actually protecting — "an agent skipping the
retrieval must score 0.0" — is met by the **target** being derived. The rubric
keys on one order-address entity id that appears nowhere in the instruction, and
the five official analogues dictate their addresses the same way.

## Injected precondition, and the mock bug it works around

`initial_setup.py` (one per task, varying by order) writes the target order's
**own seeded `updated_at`** back into `orderOverrides[<order_id>]`, and pins
`orderAddressOverrides` to `{{}}`.

CORRECTIONS #91 is confirmed here: `getOrderGridRows` (`selectors.js:115-121`)
reads the `orderOverrides` patch and short-circuits with `if (!patch) return row`
**before** `orderAddressOverrides` is consulted at `:123`, so an address edit
alone never reaches the grid's Billing/Shipping Address columns. The injected
patch makes `patch` truthy, so `:123-134` runs and the grid picks the new
address up — the correct end state is then consistent on every screen, which is
what the census note demands. Because the injected value is identical to the
seeded one and the only two readers of `orderOverrides` are `selectors.js:48`
and `:117`, the injection changes nothing an agent or a reviewer can see, and it
pre-satisfies no part of the rubric.

Two further defences against the same bug: no task edits `firstname` or
`lastname` (Bill-to Name / Ship-to Name are **visible** grid columns, unlike
Billing/Shipping Address which are `defaultVisible: false`,
`OrdersGrid.jsx:383-384`), and no rubric reads a grid column.

## Rejected candidates

* **Injecting extra orders into a window as distractors.** `orderAddressIndex`
  (`src/utils/staticData.js:79-85`) is built from the **frozen** `orders.json`
  only, so an order injected through `state.newOrders` renders in the grid and
  on its own order view but its Address Information `Edit` link resolves to
  `NotFound` (`getOrderAddress` returns `null`, `OrderAddressEdit.jsx:95`). A
  distractor an agent can click into a dead page is worse than no distractor.
* **Month-wide windows.** No month in the corpus holds fewer than 9 orders, so a
  month window needs a second discriminator and therefore a third skill.
* **Single-day windows on 2022-10-04, 2022-10-07, 2022-11-23, 2023-05-01,
  2022-04-16.** Isolated, but their orders are stored at UTC 02:28, 01:58,
  01:11, 00:42 and 01:38 and render a **day early**; the filter would match them
  and the screen would show a date outside the stated window.
* **Orders 299, 65, 301, 300, 125.** Gold entities of `webarena-538..542`;
  excluded to avoid train/test contamination even though they are the lane's
  named anchors.
* **A window straddling 2022/2023.** Not needed here, but noted: CORRECTIONS #94
  applies to the Reports period logic, not to this grid filter — the grid filter
  is a plain string comparison and handles a year-straddling window correctly.

## Corrections to the brief and the census

* **CORRECTIONS #88 is wrong, and the coordinator's retraction is confirmed
  independently.** `ORDER_STATUS_FILTER_OPTIONS` (`OrdersGrid.jsx:65-78`, declared at `:64`) holds
  twelve statuses **including** `{{value: 'pending', label: 'Pending'}}`, plus
  `pending_payment` and `pending_paypal`. No routing around it is needed.
* **The coordinator's "America/New_York crosses no day boundary" is true only of
  the twelve open orders, not of the grid.** Over all 308 rows, every order
  stored with a UTC hour below 5 renders a day early — order 000000284
  (`2023-05-01 00:42:12` -> `Apr 30, 2023`) is one of **59**. A lane
  picking day windows must screen the hour, which this one did.
* **The census's "orders with address-edit routes: 299, 65, 301, 300, 125" reads
  as an enumeration and is a sample.** `orderAddressIndex`
  (`staticData.js:79-85`) indexes **every** address of **every** seeded order:
  all 308 orders carry both a billing and a shipping address, so 616 address-edit
  routes resolve. This is what made a ten-task lane possible without reusing a
  benchmark gold entity.
* **The brief's storefront hazards do not transfer.** The storefront's five
  day-early orders and its `sortedOrders` 160-above-169 defect are properties of
  `webarena_shopping_mock`'s own grid; this grid has a different comparator
  (`defaultCompare`) and a **stored-string** date filter. The day-early *class*
  of bug does recur here, as recorded above, but with different rows and only in
  rendering, never in filtering.
"""


main()
