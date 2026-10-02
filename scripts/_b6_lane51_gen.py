#!/usr/bin/env python3
"""Batch-6 lane 51 generator - shopping_admin, skill pair R4 -> A10.

Chain: order the Sales grid on an ordinal (purchase date or grand total,
optionally inside a status/customer scope), then drive the single order that
ordinal names through a lifecycle transition (Cancel or Hold).

Writes bundles to output/tasks/shopping_admin/<task_id>/ and the batch
artefacts to output/tasks/shopping_admin/_batches/ordinal_order_cancel/.

Verified mechanism (see GENERATION.md for the full list):
  writer  hub/websites/webarena_shopping_admin_mock/src/pages/sales/
          OrderActionRoutes.jsx:64-73   (OrderCancel)  :78-107 (OrderHold)
          OrdersGrid.jsx:136-151 patchMany / :153-168 massCancel
  reader  selectors.js:114-137 getOrderGridRows merges patch.status
          OrdersGrid.jsx:298-309 the Status column renders orderStatusLabel(r.status)
  key     orderOverrides[<entity_id>].{state,status} (+ orderComments[<id>])
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "output", "tasks", "shopping_admin")
BATCH_DIR = os.path.join(SITE_DIR, "_batches", "ordinal_order_cancel")
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
BASE_ENV = "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

# --------------------------------------------------------------------------- #
# shared reward body (identical rubric in reward.py and nemo_reward.py)
# --------------------------------------------------------------------------- #

RUBRIC_HELPERS = '''
def _transitioned_ids(state, value):
    """Order ids the episode drove to `value` through `orderOverrides`.

    Every writer that performs this transition - OrderActionRoutes.OrderCancel /
    OrderHold and the orders-grid mass actions via patchMany - sets `state` and
    `status` together, so requiring both is the faithful test. The seeded
    corpus carries no overrides at all, so this set is exactly what the session
    transitioned.
    """
    overrides = state.get("orderOverrides")
    if not isinstance(overrides, dict):
        return set()
    found = set()
    for key, patch in overrides.items():
        if not isinstance(patch, dict):
            continue
        status = patch.get("status")
        stt = patch.get("state")
        if isinstance(status, str) and isinstance(stt, str):
            if status.strip() == value and stt.strip() == value:
                found.add(str(key))
    return found


def _checks(state):
    return {
        COMPONENT_NAME: _transitioned_ids(state, TRANSITION) == TARGET_IDS,
    }
'''

REWARD_TEMPLATE = '''"""Deterministic reward for {task_id}.

Success criteria:
{criteria_block}

Reads only `current_state` from the immutable evidence bundle; never diffs
against `initial_state`. Ground truth is fixed by the frozen seed of
webarena_shopping_admin_mock in ./hub/.
"""

TARGET_IDS = {target_ids!r}
TRANSITION = {transition!r}
COMPONENT_NAME = {component!r}

COMPONENT_WEIGHTS = {{COMPONENT_NAME: 1.0}}


def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {{}}

{helpers}

def evaluate(evidence):
    state = _state(evidence)
    checks = _checks(state)
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

NEMO_REWARD_TEMPLATE = '''"""NeMo-Gym reward program for {task_id}.

Implements exactly the rubric of reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{placeholder}"

TARGET_IDS = {target_ids!r}
TRANSITION = {transition!r}
COMPONENT_NAME = {component!r}

COMPONENT_WEIGHTS = {{COMPONENT_NAME: 1.0}}

{helpers}

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

# --------------------------------------------------------------------------- #
# initial_setup.py - read-modify-write, full document posted back
# --------------------------------------------------------------------------- #

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{rationale}

The injected patches are exactly what OrderActionRoutes.OrderHold writes
(OrderActionRoutes.jsx:84-104): `orderOverrides[<id>]` gains
`state`/`status`/`hold_before_state`/`hold_before_status`, and
`orderComments[<id>]` gains one `makeHistoryEntry({{status: 'holded'}})` row
(orderHelpers.js:485-496). Nothing else is touched, and `updated_at` is left
alone because the hold handler does not write it.

Read-modify-write: the full document from GET /go is patched in place and
posted back, which is correct whether the mock merges or replaces a partial
`set`. Fixtures are inlined as raw triple-quoted JSON and parsed with
json.loads, so no JavaScript literal reaches Python source. Standard library
plus requests only.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{placeholder}"

ORDER_PATCHES = json.loads(r"""{order_patches}""")

ORDER_HISTORY = json.loads(r"""{order_history}""")


def fail(message):
    print("SETUP FAILED: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    got = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    got.raise_for_status()
    payload = got.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        fail("GET /go returned neither current_state nor initial_state")

    overrides = state.get("orderOverrides")
    if not isinstance(overrides, dict):
        fail("state carries no orderOverrides map")
    comments = state.get("orderComments")
    if not isinstance(comments, dict):
        fail("state carries no orderComments map")
    for key in ORDER_PATCHES:
        if key in overrides:
            fail("order " + key + " already carries a session override")

    overrides = dict(overrides)
    comments = dict(comments)
    for key, patch in ORDER_PATCHES.items():
        overrides[key] = patch
    for key, rows in ORDER_HISTORY.items():
        comments[key] = list(rows) + list(comments.get(key) or [])
    state["orderOverrides"] = overrides
    state["orderComments"] = comments

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()
    print("SETUP OK")


main()
'''


def hold_patch(before_state, before_status):
    return {
        "state": "holded",
        "status": "holded",
        "hold_before_state": before_state,
        "hold_before_status": before_status,
    }


def hold_history(stamp):
    return [{
        "created_at": stamp,
        "status": "holded",
        "comment": "",
        "is_customer_notified": 0,
        "is_visible_on_front": 0,
        "entity_name": "order",
    }]


# --------------------------------------------------------------------------- #
# the ten tasks
# --------------------------------------------------------------------------- #

TASKS = [
    {
        "id": "ordinal_order_cancel_oldest_pending_001",
        "instruction": (
            "One order has been sitting in Pending longer than any other. "
            "Cancel it."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "transition": "canceled",
        "targets": ["301"],
        "target_label": "000000301 (Alex Johnson, Apr 19 2023 7:41:16 PM ET)",
        "criteria": [
            "orderOverrides drives exactly order 301 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "sort the Sales grid ascending on Purchase Date inside the Pending "
            "status filter -> cancel the single oldest row"
        ),
        "analogues": ["Cancel order 301"],
        "derived_from": "cancel_then_order_count_grace_pending_sweep_001",
        "notes": [
            "Pending purchase dates ascending: 301 23:41:16, 302 23:41:29, "
            "303 23:41:42 (all 2023-04-19 UTC). Margin to the runner-up is 13 "
            "seconds and the grid renders seconds, so the ordinal is exact.",
            "An agent that cancels the newest Pending order (299) scores 0.0.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Filters > Status = Pending > Apply Filters, then "
            "click the Purchase Date header once to sort ascending; the first "
            "row is 000000301."
        ),
    },
    {
        "id": "ordinal_order_cancel_newest_pending_002",
        "instruction": "Cancel the most recently placed order that is still Pending.",
        "style": "terse",
        "shape": "retrieval_writeback",
        "transition": "canceled",
        "targets": ["299"],
        "target_label": "000000299 (Sarah Miller, May 31 2023 2:55:09 AM ET)",
        "criteria": [
            "orderOverrides drives exactly order 299 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending under the default Purchase Date "
            "descending sort -> cancel the top row"
        ),
        "analogues": ["Cancel order 299"],
        "derived_from": "cancel_then_order_count_grace_newest_pending_002",
        "notes": [
            "Newest Pending is 299 at 2023-05-31 06:55:09 UTC; runner-up 65 is "
            "2023-05-28 10:43:55. Margin 2 days 20 hours.",
            "The Orders grid default sort is created_at DESC "
            "(OrdersGrid.jsx:396), so the target is the first Pending row.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Filters > Status = Pending > Apply Filters; the "
            "default created_at DESC sort puts 000000299 on top."
        ),
    },
    {
        "id": "ordinal_order_cancel_second_newest_pending_003",
        "instruction": (
            "We are working through the Pending backlog newest first. The very "
            "newest one can wait - cancel the second most recent Pending order "
            "instead."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "transition": "canceled",
        "targets": ["65"],
        "target_label": "000000065 (Grace Nguyen, May 28 2023 6:43:55 AM ET)",
        "criteria": [
            "orderOverrides drives exactly order 65 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending, read the Purchase Date ordering "
            "-> cancel the second row"
        ),
        "analogues": ["Cancel order 299"],
        "derived_from": "cancel_then_order_count_grace_newest_pending_002",
        "notes": [
            "Pending newest-first: 299 (05-31), 65 (05-28), 308 (04-19 "
            "23:42:37). Second place is 65 with 3 days of clearance on either "
            "side.",
            "An agent that stops at the top row cancels 299 and scores 0.0.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Status = Pending, default date-descending sort; "
            "take row two (000000065)."
        ),
    },
    {
        "id": "ordinal_order_cancel_newest_pending_after_holds_004",
        "instruction": "Cancel the newest order that is still showing as Pending.",
        "style": "terse",
        "shape": "retrieval_writeback",
        "transition": "canceled",
        "targets": ["308"],
        "target_label": "000000308 (Grace Nguyen, Apr 19 2023 7:42:37 PM ET)",
        "criteria": [
            "orderOverrides drives exactly order 308 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending - which no longer contains the "
            "two May orders - and cancel the newest remaining row"
        ),
        "analogues": ["Cancel order 302"],
        "derived_from": "cancel_then_order_count_grace_newest_pending_002",
        "notes": [
            "The two May Pending orders (299, 65) are on hold in this session, "
            "so they are On Hold in the Status column and drop out of the "
            "Pending filter. The newest Pending row becomes 308 at 2023-04-19 "
            "23:42:37, 12 seconds ahead of 307.",
            "This is the memorisation trap for the family: the seed answer "
            "(299) scores 0.0 here.",
        ],
        "setup": {
            "rationale": (
                "Puts the two May Pending orders (000000299 and 000000065) on "
                "hold before the episode opens, so the newest Pending order is "
                "no longer the seed's 299. An agent that recalls the seed "
                "answer instead of reading the grid lands on a row the Pending "
                "filter no longer shows."
            ),
            "patches": {
                "299": hold_patch("pending", "pending"),
                "65": hold_patch("pending", "pending"),
            },
            "history": {
                "299": hold_history("2023-06-01 09:14:22"),
                "65": hold_history("2023-06-01 09:15:03"),
            },
            "declared": [
                "orderOverrides['299'] = holded/holded with "
                "hold_before_state=hold_before_status='pending', plus one "
                "orderComments['299'] holded history row - the exact shape "
                "OrderHold writes.",
                "orderOverrides['65'] = the same, hold_before 'pending'.",
                "Nothing canceled is injected, so the rubric's canceled set is "
                "empty at t=0 and the initial lane scores 0.0.",
            ],
        },
        "replay_note": (
            "Sales > Orders, Status = Pending; 299 and 65 are absent (On Hold), "
            "so the top row is 000000308."
        ),
    },
    {
        "id": "ordinal_order_cancel_second_largest_total_005",
        "instruction": (
            "Cancel the Pending order with the second-highest Grand Total "
            "(Purchased)."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "transition": "canceled",
        "targets": ["304"],
        "target_label": "000000304 (Alexander Thomas, $215.00)",
        "criteria": [
            "orderOverrides drives exactly order 304 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending, sort descending on Grand Total "
            "(Purchased) -> cancel the second row"
        ),
        "analogues": ["Cancel order 305"],
        "derived_from": "cancel_then_order_count_grace_high_value_pending_004",
        "notes": [
            "Pending totals descending: 299 $219.40, 304 $215.00, 65 $210.00. "
            "Second place clears its neighbours by $4.40 and $5.00.",
            "All ten Pending grand totals are distinct; the tightest pair in "
            "the whole Pending set is $175.40 vs $179.40 ($4.00).",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Status = Pending, click Grand Total (Purchased) "
            "twice for descending; row two is 000000304."
        ),
    },
    {
        "id": "ordinal_order_cancel_hold_second_smallest_total_006",
        "instruction": (
            "Finance has opened a review of our low-value Pending orders and "
            "wants one of them frozen while they look at it. It is not the "
            "cheapest Pending order they care about but the one directly above "
            "it - the Pending order with the second-lowest Grand Total "
            "(Purchased). Put that order on hold."
        ),
        "style": "explicit",
        "shape": "retrieval_writeback",
        "transition": "holded",
        "targets": ["305"],
        "target_label": "000000305 (Mary Martin, $91.00)",
        "criteria": [
            "orderOverrides drives exactly order 305 to state and status holded.",
            "No other order carries an On Hold override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending, sort ascending on Grand Total "
            "(Purchased) -> put the second row on hold"
        ),
        "analogues": ["Get the order number of my most recent on hold order"],
        "derived_from": None,
        "notes": [
            "Pending totals ascending: 301 $76.40, 305 $91.00, 307 $101.20. "
            "Second place clears its neighbours by $14.60 and $10.20.",
            "Hold is the other A10 transition on this mock and writes the same "
            "orderOverrides shape (OrderActionRoutes.jsx:84-104); the Hold "
            "button carries no confirm modal.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Status = Pending, sort Grand Total (Purchased) "
            "ascending; row two (000000305) > View > Hold."
        ),
    },
    {
        "id": "ordinal_order_cancel_second_oldest_pending_after_hold_007",
        "instruction": (
            "Our Pending queue needs trimming from the back. Cancel the "
            "second-oldest order still sitting in Pending."
        ),
        "style": "terse",
        "shape": "derived_target_mutation",
        "transition": "canceled",
        "targets": ["303"],
        "target_label": "000000303 (Lily Potter, Apr 19 2023 7:41:42 PM ET)",
        "criteria": [
            "orderOverrides drives exactly order 303 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Pending - the seed's oldest row is now On "
            "Hold - sort ascending on Purchase Date and cancel the second row"
        ),
        "analogues": ["Cancel order 302"],
        "derived_from": "cancel_then_order_count_grace_pending_sweep_001",
        "notes": [
            "With 301 on hold the Pending queue starts 302 (23:41:29), 303 "
            "(23:41:42), 304 (23:41:55), so the second-oldest is 303.",
            "Without the injection the answer would be 302; with it, an agent "
            "that ignores the Status column scores 0.0.",
        ],
        "setup": {
            "rationale": (
                "Puts the seed's oldest Pending order (000000301) on hold "
                "before the episode opens, shifting the whole Pending ordinal "
                "by one. The task's answer therefore cannot be recalled from "
                "the pristine corpus."
            ),
            "patches": {"301": hold_patch("new", "pending")},
            "history": {"301": hold_history("2023-05-02 14:37:41")},
            "declared": [
                "orderOverrides['301'] = holded/holded with "
                "hold_before_state='new' and hold_before_status='pending' - "
                "order 301's seeded state/status pair - plus one "
                "orderComments['301'] holded history row.",
                "No canceled override is injected, so the rubric is unsatisfied "
                "at t=0.",
            ],
        },
        "replay_note": (
            "Sales > Orders, Status = Pending, Purchase Date ascending; 301 is "
            "absent (On Hold) so row two is 000000303."
        ),
    },
    {
        "id": "ordinal_order_cancel_hold_oldest_open_008",
        "instruction": (
            "Put our oldest still-open order on hold - open meaning it is "
            "neither Complete, Closed nor Canceled."
        ),
        "style": "terse",
        "shape": "derived_target_mutation",
        "transition": "holded",
        "targets": ["300"],
        "target_label": "000000300 (Grace Nguyen, Processing, Apr 19 2023 7:41:07 PM ET)",
        "criteria": [
            "orderOverrides drives exactly order 300 to state and status holded.",
            "No other order carries an On Hold override.",
        ],
        "skill_chain": (
            "isolate the twelve open orders across two status values on the "
            "Sales grid -> put the oldest of them on hold"
        ),
        "analogues": ["Go to the list of orders that are on hold"],
        "derived_from": None,
        "notes": [
            "The seed's open set is exactly 10 Pending + 2 Processing; the "
            "oldest is 300 at 2023-04-19 23:41:07, nine seconds ahead of 301.",
            "The scope spans two status values, so a single Status filter is "
            "not enough - the agent has to look at both queues.",
            "An agent that only reads the Pending queue holds 301 and scores 0.0.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders. Take the Pending and the Processing queues in "
            "turn, each sorted ascending on Purchase Date: Pending starts at "
            "000000301 (Apr 19 2023 7:41:16 PM ET), Processing at 000000300 "
            "(7:41:07 PM ET). 000000300 is the older of the two, so it is the "
            "oldest open order overall > View > Hold."
        ),
    },
    {
        "id": "ordinal_order_cancel_newest_processing_009",
        "instruction": (
            "Cancel the most recently placed order that is still in Processing."
        ),
        "style": "terse",
        "shape": "derived_target_mutation",
        "transition": "canceled",
        "targets": ["125"],
        "target_label": "000000125 (Matt Baker, May 24 2023 8:28:12 AM ET)",
        "criteria": [
            "orderOverrides drives exactly order 125 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "filter the Sales grid to Processing -> cancel the newest of the "
            "two rows"
        ),
        "analogues": ["Cancel order 302"],
        "derived_from": None,
        "notes": [
            "Processing holds exactly 125 (2023-05-24 12:28:12) and 300 "
            "(2023-04-19 23:41:07); margin 34 days.",
            "125 sits at row 125 of the id sequence but near the top under the "
            "date sort, so the retrieval is a status filter plus an ordinal, "
            "not an id lookup.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, Filters > Status = Processing > Apply Filters; "
            "the default date-descending sort puts 000000125 on top."
        ),
    },
    {
        "id": "ordinal_order_cancel_grace_oldest_pending_010",
        "instruction": (
            "Grace Nguyen (avidreader99@yahoo.com) has phoned in to withdraw "
            "the oldest of the orders she still has sitting in Pending. Find "
            "her Pending orders in Sales, work out which of them she placed "
            "first, and cancel that one from its order page."
        ),
        "style": "explicit",
        "shape": "derived_target_mutation",
        "transition": "canceled",
        "targets": ["307"],
        "target_label": "000000307 (Grace Nguyen, Apr 19 2023 7:42:25 PM ET, $101.20)",
        "criteria": [
            "orderOverrides drives exactly order 307 to state and status canceled.",
            "No other order carries a canceled override.",
        ],
        "skill_chain": (
            "narrow the Sales grid to Grace Nguyen's Pending rows -> cancel the "
            "earliest of them"
        ),
        "analogues": ["Cancel order 307"],
        "derived_from": "cancel_then_order_count_grace_pending_sweep_001",
        "notes": [
            "Grace Nguyen owns 15 orders; three are Pending - 307 (04-19 "
            "23:42:25), 308 (04-19 23:42:37) and 65 (05-28). The oldest is 307, "
            "12 seconds ahead of 308.",
            "Her Processing order 300 (04-19 23:41:07) is older still and is "
            "the distractor the Pending scope removes.",
            "Bill-to Name 'Grace Nguyen' maps 1:1 onto "
            "avidreader99@yahoo.com across the whole grid, so the name is "
            "unambiguous.",
        ],
        "setup": None,
        "replay_note": (
            "Sales > Orders, keyword search 'Grace Nguyen' (or Bill-to Name "
            "filter) plus Status = Pending, sort Purchase Date ascending; row "
            "one is 000000307."
        ),
    },
]


# --------------------------------------------------------------------------- #
# emitters
# --------------------------------------------------------------------------- #

def component_name(task):
    ids = "_and_".join(task["targets"])
    verb = "canceled" if task["transition"] == "canceled" else "on_hold"
    return "orders_%s_are_exactly_%s" % (verb, ids)


def reward_source(task):
    criteria = "\n".join("  * " + line for line in task["criteria"])
    return REWARD_TEMPLATE.format(
        task_id=task["id"],
        criteria_block=criteria,
        target_ids=set(task["targets"]),
        transition=task["transition"],
        component=component_name(task),
        helpers=RUBRIC_HELPERS,
    )


def nemo_reward_source(task):
    return NEMO_REWARD_TEMPLATE.format(
        task_id=task["id"],
        placeholder=PLACEHOLDER,
        target_ids=set(task["targets"]),
        transition=task["transition"],
        component=component_name(task),
        helpers=RUBRIC_HELPERS,
    )


def setup_source(task):
    setup = task["setup"]
    if not setup:
        return None
    return SETUP_TEMPLATE.format(
        task_id=task["id"],
        rationale=setup["rationale"],
        placeholder=PLACEHOLDER,
        order_patches=json.dumps(setup["patches"], indent=2),
        order_history=json.dumps(setup["history"], indent=2),
    )


def replay_source(task):
    target = task["targets"][0]
    action = task["transition"]
    lines = [
        '"""Golden replay draft for %s.' % task["id"],
        "",
        "Click-only after the landing page: admin rail > Sales > Orders, then the",
        "grid's own filter/sort controls, then the row's View link and the order",
        "view's lifecycle button. No page.goto() after the initial load and no",
        "constructed URL.",
        "",
        "Retrieval: %s" % task["replay_note"],
        'Expected target: order entity_id %s - %s' % (target, task["target_label"]),
        '"""',
        "",
        "TARGET_ID = %r" % target,
        "TRANSITION = %r" % action,
        "",
        "",
        "def run(page, base_url, sid):",
        '    page.goto("%s/?sid=%s" % (base_url.rstrip("/"), sid))',
        '    page.wait_for_selector("#menu-sales")',
        "",
        "    # 1. admin rail -> Sales -> Orders",
        '    page.click("#menu-sales")',
        '    page.click(\'#menu-sales .submenu a:has-text("Orders")\')',
        '    page.wait_for_selector(\'[data-grid-id="sales_order_grid"] table.data-grid\')',
        "",
        "    # 2. the retrieval, driven through the grid's own controls",
        "    #    (see the module docstring for the ordinal this resolves)",
    ]
    search = task.get("replay_search")
    if search:
        lines += [
            '    page.fill(".data-grid-search-control", %r)' % search,
            '    page.click(".data-grid-search-control-wrap .action-submit")',
            "    page.wait_for_timeout(300)",
        ]
    scope = task.get("filter_status")
    if scope:
        lines += [
            '    page.click(\'[data-action="grid-filter-expand"]\')',
            '    page.select_option("#filter-sales_order_grid-status", %r)' % scope,
            '    page.click(\'[data-action="grid-filter-apply"]\')',
            "    page.wait_for_timeout(300)",
        ]
    for column, clicks in task.get("replay_sort", []):
        for _ in range(clicks):
            lines += [
                '    page.click("th.col-%s")' % column,
                "    page.wait_for_timeout(200)",
            ]
    lines += [
        "",
        "    # 3. open the derived row and drive the transition",
        '    page.click(\'tr:has(#idscheck%s) a.action-menu-item\' % TARGET_ID)',
        '    page.wait_for_selector("#order_status")',
    ]
    if action == "canceled":
        lines += [
            '    page.click("#order-view-cancel-button")',
            '    page.wait_for_selector(".modal-popup.confirm._show")',
            '    page.click(".modal-popup.confirm._show .action-primary.action-accept")',
        ]
    else:
        lines += [
            '    page.click("#order-view-hold-button")',
        ]
    lines += [
        "    page.wait_for_timeout(500)",
        "",
        "",
        "# Route the View link lands on:"
        " /admin/sales/order/view/order_id/%s/" % target,
        "# Cancel posts through /admin/sales/order/cancel/order_id/<id>/ ;"
        " Hold through /hold/.",
        "# The Cancel button opens the in-DOM Magento confirm modal"
        " (ConfirmModal.jsx); Hold does not.",
        "",
    ]
    return "\n".join(lines)


def bundle(task):
    task_id = task["id"]
    out_dir = os.path.join(SITE_DIR, task_id)
    os.makedirs(out_dir, exist_ok=True)

    setup_code = setup_source(task)

    instruction = " ".join(task["instruction"].split())

    task_instruction = {
        "task_id": task_id,
        "task_instruction": instruction,
        "app_dir": APP_DIR,
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": task["criteria"],
    }

    metadata = {
        "style": task["style"],
        "difficulty": "medium",
        "shape": task["shape"],
        "skills": ["R4", "A10"],
        "skill_chain": task["skill_chain"],
        "derived_from": task["derived_from"],
        "official_analogues": task["analogues"],
        "injected_preconditions": (task["setup"]["declared"] if task["setup"] else []),
        "topic": "ordinal_order_cancel",
        "lane": 51,
        "inspiration_ids": [
            "webarena-470", "webarena-471", "webarena-472", "webarena-473",
            "webarena-474", "webarena-680",
        ],
        "authoring_notes": task["notes"],
    }

    manifest = {
        "schema_version": 2,
        "task_id": task_id,
        "instruction": instruction,
        "apps": [
            {
                "name": APP_DIR,
                "source_name": "shopping_admin",
                "base_url_env": BASE_ENV,
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
        "metadata": metadata,
    }
    if setup_code is not None:
        manifest["setup_path"] = "initial_setup.py"

    nemo_row = {
        "task_payload": {
            "task_id": task_id,
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
                "bundle_id": task_id,
                "app_dir": APP_DIR,
                "initial_setup": setup_code,
                "eval_reward_code": nemo_reward_source(task),
            },
        }
    }

    write(os.path.join(out_dir, "task_instruction.json"),
          json.dumps(task_instruction, indent=2) + "\n")
    write(os.path.join(out_dir, "task.json"),
          json.dumps(manifest, indent=2) + "\n")
    write(os.path.join(out_dir, "reward.py"), reward_source(task))
    write(os.path.join(out_dir, "nemo_reward.py"), nemo_reward_source(task))
    write(os.path.join(out_dir, "nemo_task.json"),
          json.dumps(nemo_row, indent=1) + "\n")
    if setup_code is not None:
        write(os.path.join(out_dir, "initial_setup.py"), setup_code)

    write(os.path.join(REPLAY_DIR, task_id + ".py"), replay_source(task))
    return nemo_row


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def main():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    rows = []
    for task in TASKS:
        rows.append(bundle(task))

    index = {
        "schema_version": 2,
        "tasks": [
            {"task_id": t["id"], "path": "%s/task.json" % t["id"]} for t in TASKS
        ],
    }
    write(os.path.join(BATCH_DIR, "index.json"), json.dumps(index, indent=2) + "\n")
    write(
        os.path.join(BATCH_DIR, "nemo_tasks.jsonl"),
        "".join(json.dumps(row) + "\n" for row in rows),
    )
    print("wrote %d bundles" % len(TASKS))


# Per-task replay plumbing.
#
# The Orders grid opens on created_at DESC (OrdersGrid.jsx:396) and
# AdminGrid.toggleSort (:290-295) sends a fresh column to ASC and flips the
# current column ASC -> DESC. So one click on Purchase Date gives ascending,
# and two clicks on a Grand Total column give descending.
_FILTER_STATUS = {
    "ordinal_order_cancel_newest_processing_009": "processing",
    # 008 ranks across two status values. The draft opens on the Processing
    # queue - two rows - and the note records that the Pending queue's oldest
    # row (000000301, 23:41:16) has to be compared against it; 000000300 at
    # 23:41:07 wins by nine seconds.
    "ordinal_order_cancel_hold_oldest_open_008": "processing",
}
_SEARCH = {
    "ordinal_order_cancel_grace_oldest_pending_010": "Grace Nguyen",
}
_SORT_PLAN = {
    "ordinal_order_cancel_oldest_pending_001": [("created_at", 1)],
    "ordinal_order_cancel_second_largest_total_005": [("grand_total", 2)],
    "ordinal_order_cancel_hold_second_smallest_total_006": [("grand_total", 1)],
    "ordinal_order_cancel_second_oldest_pending_after_hold_007": [("created_at", 1)],
    "ordinal_order_cancel_hold_oldest_open_008": [("created_at", 1)],
    "ordinal_order_cancel_grace_oldest_pending_010": [("created_at", 1)],
}
for _t in TASKS:
    _t["filter_status"] = _FILTER_STATUS.get(_t["id"], "pending")
    _t["replay_sort"] = _SORT_PLAN.get(_t["id"], [])
    _t["replay_search"] = _SEARCH.get(_t["id"])


if __name__ == "__main__":
    main()
