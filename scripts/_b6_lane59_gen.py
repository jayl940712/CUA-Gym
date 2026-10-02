#!/usr/bin/env python3
"""Batch-6 lane 59 generator - shopping_admin R7 -> A8.

Chain: join a customer record to their orders through the admin grids, then
leave a comment on the order that join singles out.

Writes:
  output/tasks/shopping_admin/<task_id>/{task_instruction.json,task.json,
                                         reward.py,nemo_reward.py,nemo_task.json}
  output/tasks/shopping_admin/_batches/customer_join_order_comment/{GENERATION.md,
                                         index.json,nemo_tasks.jsonl,replays/*.py}

No validation is run here by design (see the lane brief).
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/customer_join_order_comment")
APP = "webarena_shopping_admin_mock"

ANALOGUES = [
    'Notify Alexander Thomas in their most recent pending order with message "the order is ready to be shipped soon!"',
    'Notify Jane Doe in their most recent pending order with message "sorry we are out of stock, please reorder"',
    'Notify Grace Nguyen in their most recent pending order with message "sorry we are bankrupt, please contact our customer service for refund"',
    'Notify Lily Potter in their most recent pending order with message "Thanks, your order is ready to be shipped!"',
]

INSPIRATION = ["webarena-491", "webarena-492", "webarena-493", "webarena-495"]

# --------------------------------------------------------------------------
# Every derived value below was recomputed from
# hub/websites/webarena_shopping_admin_mock/src/data/{orderGrid,customerGrid}.json
# and the margins are recorded in GENERATION.md.
# --------------------------------------------------------------------------

TASKS = [
    dict(
        num="001", slug="john_smith_top_complete",
        style="terse", shape="derived_target_mutation",
        join="phone", phone="2058812302",
        customer="John Smith", email="john.smith.xyz@gmail.com", cust_id=2,
        order_id="96", increment="000000096", status="complete",
        comment="Loyalty credit approved on this purchase.",
        notify=0,
        instruction=(
            "A shopper phoned about a loyalty credit and left only the number 2058812302. "
            "Find that customer, open their highest-value Complete order, and comment "
            "\"Loyalty credit approved on this purchase.\" on it."
        ),
        rule="highest grand total among that customer's Complete orders",
        margin="$209.40 (000000096) vs $180.40 (000000115); the customer's overall maximum is the CANCELED $211.80 order 000000068, so ignoring the status qualifier lands on the wrong order",
        replay_note="Customers > All Customers, Phone filter 2058812302 -> John Smith / john.smith.xyz@gmail.com; Sales > Orders, Bill-to Name 'John Smith' + Status Complete, sort Grand Total (Purchased) desc; head is 000000096.",
        grid_filters=[("billing_name", "John Smith"), ("status", "complete")],
        sort_col="grand_total", sort_desc=True,
    ),
    dict(
        num="002", slug="jennifer_white_top_canceled_count",
        style="explicit", shape="retrieval_writeback",
        join="phone", phone="2137418080",
        customer="Jennifer White", email="jennifer.white@yahoo.com", cust_id=26,
        order_id="72", increment="000000072", status="canceled",
        comment="Refund review: 8 orders on this account.",
        notify=0,
        instruction=(
            "Go to Customers > All Customers and find the account whose Phone is 2137418080. Then "
            "go to Sales > Orders and pull up every order that customer has placed. Open the most "
            "expensive of the ones that were Canceled and, in \"Notes for this Order\", submit the "
            "comment \"Refund review: N orders on this account.\" with N replaced by the total "
            "number of orders that customer has on file. Leave the Status dropdown as it is, leave "
            "\"Notify Customer by Email\" unticked and leave \"Visible on Storefront\" unticked."
        ),
        rule="highest grand total among that customer's Canceled orders; N is that customer's total order count",
        margin="$178.00 (000000072) vs $141.00 (000000135), margin $37.00; the overall maximum is the COMPLETE $232.84 order 000000169. Order count 8 is a count of a 1:1 filtered set, no tie possible.",
        replay_note="Customers > All Customers, Phone filter 2137418080 -> Jennifer White; Sales > Orders, Bill-to Name 'Jennifer White' shows '8 records found' (that is N), add Status Canceled and sort Grand Total (Purchased) desc; head is 000000072.",
        grid_filters=[("billing_name", "Jennifer White"), ("status", "canceled")],
        sort_col="grand_total", sort_desc=True,
    ),
    dict(
        num="003", slug="mary_martin_only_pending_notify",
        style="terse", shape="derived_target_mutation",
        join="phone", phone="3059876543",
        customer="Mary Martin", email="marym@gmail.com", cust_id=8,
        order_id="305", increment="000000305", status="pending",
        comment="Payment reminder sent to the customer today.",
        notify=1,
        instruction=(
            "3059876543 is all we have for a customer whose payment never cleared. Identify "
            "them, open their one Pending order, and post \"Payment reminder sent to the "
            "customer today.\" there with Notify Customer by Email ticked."
        ),
        rule="the customer's single Pending order",
        margin="exactly one of Mary Martin's 6 orders is Pending (000000305); the other five are 4 Complete and 1 Canceled",
        replay_note="Customers > All Customers, Phone filter 3059876543 -> Mary Martin; Sales > Orders, Bill-to Name 'Mary Martin' + Status Pending returns a single row, 000000305.",
        grid_filters=[("billing_name", "Mary Martin"), ("status", "pending")],
        sort_col=None, sort_desc=False,
    ),
    dict(
        num="004", slug="lily_potter_first_order_count",
        style="terse", shape="retrieval_writeback",
        join="phone", phone="7735555555",
        customer="Lily Potter", email="harrypotterfan1@gmail.com", cust_id=17,
        order_id="111", increment="000000111", status="canceled",
        comment="First of 11 orders from this customer.",
        notify=0,
        instruction=(
            "The shopper on 7735555555 is a long-standing customer. Open the very first order "
            "they ever placed and comment \"First of N orders from this customer.\", with N "
            "being their total number of orders."
        ),
        rule="earliest Purchase Date among all of that customer's orders; N is that customer's total order count",
        margin="2022-03-11 12:09:34 (000000111) vs 2022-03-22 04:29:13 (000000022), margin 11 days. Order count 11.",
        replay_note="Customers > All Customers, Phone filter 7735555555 -> Lily Potter; Sales > Orders, Bill-to Name 'Lily Potter' shows '11 records found' (that is N), sort Purchase Date ascending; head is 000000111.",
        grid_filters=[("billing_name", "Lily Potter")],
        sort_col="created_at", sort_desc=False,
    ),
    dict(
        num="005", slug="matt_baker_latest_order",
        style="terse", shape="derived_target_mutation",
        join="phone", phone="4045551234",
        customer="Matt Baker", email="matt.baker@yahoo.com", cust_id=13,
        order_id="125", increment="000000125", status="processing",
        comment="Courier escalation opened for this shipment.",
        notify=0,
        instruction=(
            "A courier escalation came in from the customer whose phone is 4045551234. Find "
            "them, open their newest order, and add the comment \"Courier escalation opened "
            "for this shipment.\""
        ),
        rule="latest Purchase Date among all of that customer's orders",
        margin="2023-05-24 12:28:12 (000000125) vs 2023-02-26 00:35:11 (000000089), margin 87 days",
        replay_note="Customers > All Customers, Phone filter 4045551234 -> Matt Baker; Sales > Orders, Bill-to Name 'Matt Baker', sort Purchase Date descending; head is 000000125.",
        grid_filters=[("billing_name", "Matt Baker")],
        sort_col="created_at", sort_desc=True,
    ),
    dict(
        num="006", slug="brian_smith_latest_complete",
        style="terse", shape="derived_target_mutation",
        join="phone", phone="7025551212",
        customer="Brian Smith", email="brian.smith@yahoo.com", cust_id=34,
        order_id="282", increment="000000282", status="complete",
        comment="Warranty window confirmed for this order.",
        notify=0,
        instruction=(
            "Someone calling from 7025551212 wants their warranty window confirmed. Find the "
            "account, open the most recent order of theirs that actually completed, and "
            "comment \"Warranty window confirmed for this order.\" on it."
        ),
        rule="latest Purchase Date among that customer's Complete orders",
        margin="2022-03-15 (000000282) vs 2022-01-17 (000000121), margin 57 days; the customer's newest order overall is the CANCELED 000000118 of 2023-05-07, so dropping the status qualifier picks the wrong order",
        replay_note="Customers > All Customers, Phone filter 7025551212 -> Brian Smith; Sales > Orders, Bill-to Name 'Brian Smith' + Status Complete, sort Purchase Date descending; head is 000000282.",
        grid_filters=[("billing_name", "Brian Smith"), ("status", "complete")],
        sort_col="created_at", sort_desc=True,
    ),
    dict(
        num="007", slug="bob_johnson_cheapest_complete",
        style="explicit", shape="derived_target_mutation",
        join="phone", phone="9721234567",
        customer="Bob Johnson", email="bob123@hotmail.com", cust_id=7,
        order_id="83", increment="000000083", status="complete",
        comment="Free-shipping goodwill applied to this order.",
        notify=0,
        instruction=(
            "Open Customers > All Customers and filter the Phone column on 9721234567 to see who "
            "the account belongs to. Then open Sales > Orders, restrict it to that customer's "
            "orders with a status of Complete, and sort by Grand Total to find their smallest "
            "completed order. On that order's page, type \"Free-shipping goodwill applied to this "
            "order.\" into the Comment box under \"Notes for this Order\" and press Submit Comment. "
            "Leave the Status dropdown where it is, and leave both \"Notify Customer by Email\" and "
            "\"Visible on Storefront\" unticked."
        ),
        rule="lowest grand total among that customer's Complete orders",
        margin="$28.00 (000000083) vs $34.00 (000000055), margin $6.00; the customer's cheapest order overall is the CANCELED $27.00 order 000000227, so an agent that skips the status filter lands on the wrong order",
        replay_note="Customers > All Customers, Phone filter 9721234567 -> Bob Johnson; Sales > Orders, Bill-to Name 'Bob Johnson' + Status Complete, sort Grand Total (Purchased) ascending; head is 000000083.",
        grid_filters=[("billing_name", "Bob Johnson"), ("status", "complete")],
        sort_col="grand_total", sort_desc=False,
    ),
    dict(
        num="008", slug="daniel_jackson_biggest_order_count",
        style="terse", shape="retrieval_writeback",
        join="phone", phone="2155556789",
        customer="Daniel Jackson", email="daniel.jackson@hotmail.com", cust_id=11,
        order_id="289", increment="000000289", status="canceled",
        comment="Highest of 9 orders placed by this customer.",
        notify=0,
        instruction=(
            "Find the customer on 2155556789, open the biggest order they have ever placed by "
            "total, and leave the comment \"Highest of N orders placed by this customer.\", "
            "with N being how many orders they have."
        ),
        rule="highest grand total among all of that customer's orders; N is that customer's total order count",
        margin="$194.50 (000000289) vs $94.00 (000000265), margin $100.50. Order count 9.",
        replay_note="Customers > All Customers, Phone filter 2155556789 -> Daniel Jackson; Sales > Orders, Bill-to Name 'Daniel Jackson' shows '9 records found' (that is N), sort Grand Total (Purchased) descending; head is 000000289.",
        grid_filters=[("billing_name", "Daniel Jackson")],
        sort_col="grand_total", sort_desc=True,
    ),
    dict(
        num="009", slug="order_15_owner_top_canceled",
        style="terse", shape="derived_target_mutation",
        join="order", seed_increment="000000015",
        customer="Sarah Miller", email="helloworld@yahoo.com", cust_id=5,
        order_id="39", increment="000000039", status="canceled",
        comment="Goodwill voucher issued after this cancellation.",
        notify=0,
        instruction=(
            "Order 000000015 was cancelled, and that shopper has cancelled on us before. Work "
            "out whose order it was, then comment \"Goodwill voucher issued after this "
            "cancellation.\" on the most expensive order they have ever had cancelled."
        ),
        rule="highest grand total among the Canceled orders of the customer who owns order 000000015",
        margin="$218.85 (000000039) vs $199.80 (000000101), margin $19.05; the customer's overall maximum is the COMPLETE $226.60 order 000000028, and the named order 000000015 is itself only $61.00",
        replay_note="Sales > Orders, keyword 000000015 -> open it -> Account Information names Sarah Miller / helloworld@yahoo.com; back to Sales > Orders, Bill-to Name 'Sarah Miller' + Status Canceled, sort Grand Total (Purchased) descending; head is 000000039.",
        grid_filters=[("billing_name", "Sarah Miller"), ("status", "canceled")],
        sort_col="grand_total", sort_desc=True,
    ),
    dict(
        num="010", slug="order_241_owner_latest_complete",
        style="explicit", shape="derived_target_mutation",
        join="order", seed_increment="000000241",
        customer="Alex Johnson", email="fitnessjunkie22@yahoo.com", cust_id=23,
        order_id="218", increment="000000218", status="complete",
        comment="Replacement dispatched against this order.",
        notify=0,
        instruction=(
            "Open Sales > Orders and look up order 000000241 to see which customer placed it. Then "
            "list all of that customer's orders, keep only the ones whose status is Complete, and "
            "sort them by Purchase Date so you can see which completed order is their most recent. "
            "Open that order and submit the comment \"Replacement dispatched against this order.\" "
            "in the \"Notes for this Order\" box. Do not change the Status dropdown, do not tick "
            "\"Notify Customer by Email\" and do not tick \"Visible on Storefront\"."
        ),
        rule="latest Purchase Date among the Complete orders of the customer who owns order 000000241",
        margin="2023-03-31 (000000218) vs 2023-01-29 (000000150), margin 61 days; that customer's newest order overall is the PENDING 000000301 of 2023-04-19",
        replay_note="Sales > Orders, keyword 000000241 -> open it -> Account Information names Alex Johnson / fitnessjunkie22@yahoo.com; back to Sales > Orders, Bill-to Name 'Alex Johnson' + Status Complete, sort Purchase Date descending; head is 000000218.",
        grid_filters=[("billing_name", "Alex Johnson"), ("status", "complete")],
        sort_col="created_at", sort_desc=True,
    ),
]

# --------------------------------------------------------------------------- reward


REWARD_BODY = '''TARGET_ORDER_ID = {order_id!r}
REQUIRED_COMMENT = {comment!r}
REQUIRED_NOTIFIED = {notify}
REQUIRED_VISIBLE_ON_FRONT = 0
ORIGINAL_STATUS = {status!r}
COMPONENT_NAME = {component!r}

COMPONENT_WEIGHTS = {{COMPONENT_NAME: 1.0}}


def _as_flag(value):
    """`makeHistoryEntry` stores 1/0; tolerate the JSON boolean twin."""
    if value is True:
        return 1
    if value is False or value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def _commented_order_ids(state):
    """Order ids that carry at least one comment in `orderComments`.

    `createInitialData()` declares `orderComments: {{}}` and no seeded order
    carries a `comments` array, so every key here was produced by the episode's
    own Submit Comment presses (OrderView.jsx CommentForm.submit).
    """
    comments = state.get("orderComments")
    if not isinstance(comments, dict):
        return {{}}
    found = {{}}
    for key, entries in comments.items():
        if isinstance(entries, list) and entries:
            found[str(key)] = entries
    return found


def _status_override(state, order_id):
    overrides = state.get("orderOverrides")
    if not isinstance(overrides, dict):
        return None
    patch = overrides.get(str(order_id))
    if not isinstance(patch, dict):
        return None
    value = patch.get("status")
    if value is None:
        return None
    return str(value).strip()


def _checks(state):
    commented = _commented_order_ids(state)
    only_target = set(commented) == {{TARGET_ORDER_ID}}
    entries = commented.get(TARGET_ORDER_ID) or []
    entry = entries[0] if len(entries) == 1 and isinstance(entries[0], dict) else None
    text_ok = entry is not None and str(entry.get("comment") or "").strip() == REQUIRED_COMMENT
    notified_ok = entry is not None and _as_flag(entry.get("is_customer_notified")) == REQUIRED_NOTIFIED
    front_ok = entry is not None and _as_flag(entry.get("is_visible_on_front")) == REQUIRED_VISIBLE_ON_FRONT
    entry_status_ok = entry is not None and str(entry.get("status") or "").strip() == ORIGINAL_STATUS
    override = _status_override(state, TARGET_ORDER_ID)
    status_kept = override is None or override == ORIGINAL_STATUS
    return {{
        "only_target_order_commented": only_target,
        "exactly_one_comment_entry": entry is not None,
        "comment_text_exact": text_ok,
        "notified_flag_exact": notified_ok,
        "storefront_flag_exact": front_ok,
        "entry_status_unchanged": entry_status_ok,
        "order_status_unchanged": status_kept,
    }}


def _satisfied(checks):
    for value in checks.values():
        if not value:
            return False
    return True
'''


def reward_py(t):
    component = "order_%s_carries_exactly_the_required_comment" % t["order_id"]
    body = REWARD_BODY.format(
        order_id=t["order_id"], comment=t["comment"], notify=t["notify"],
        status=t["status"], component=component,
    )
    return '''"""Deterministic reward for {tid}.

Success criteria:
  * `orderComments` carries exactly one commented order, {inc} (entity_id {oid}).
  * That order holds exactly one comment entry, whose text is {comment!r}.
  * is_customer_notified == {notify} and is_visible_on_front == 0 on that entry.
  * The order's status is still {status!r} (entry status and orderOverrides).

Reads only `current_state` from the immutable evidence bundle; never diffs
against `initial_state`. Ground truth is fixed by the frozen seed of
webarena_shopping_admin_mock in ./hub/.
"""

{body}

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {{}}


def evaluate(evidence):
    state = _state(evidence)
    checks = _checks(state)
    satisfied = _satisfied(checks)
    components = [{{
        "name": COMPONENT_NAME,
        "score": COMPONENT_WEIGHTS[COMPONENT_NAME] if satisfied else 0.0,
        "details": dict(checks),
    }}]
    total = 0.0
    for component in components:
        total += component["score"]
    return {{"score": round(total, 6), "components": components}}
'''.format(tid=t["task_id"], inc=t["increment"], oid=t["order_id"],
           comment=t["comment"], notify=t["notify"], status=t["status"], body=body)


def nemo_reward_py(t):
    component = "order_%s_carries_exactly_the_required_comment" % t["order_id"]
    body = REWARD_BODY.format(
        order_id=t["order_id"], comment=t["comment"], notify=t["notify"],
        status=t["status"], component=component,
    )
    return '''"""NeMo-Gym reward program for {tid}.

Implements exactly the rubric of reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

{body}

def score_state(state):
    checks = _checks(state)
    if _satisfied(checks):
        return round(COMPONENT_WEIGHTS[COMPONENT_NAME], 6)
    return 0.0


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
'''.format(tid=t["task_id"], body=body)


# --------------------------------------------------------------------------- replay


def replay_py(t):
    lines = []
    lines.append('"""Golden replay draft for %s.' % t["task_id"])
    lines.append("")
    lines.append("Click-only after the landing page: admin rail, then each grid's own")
    lines.append("filter/sort controls, then the row's View link and the order view's")
    lines.append('"Notes for this Order" form. No page.goto() after the initial load.')
    lines.append("")
    lines.append("Retrieval: %s" % t["replay_note"])
    lines.append("Expected target: order entity_id %s - %s (%s, status %s)"
                 % (t["order_id"], t["increment"], t["customer"], t["status"]))
    lines.append('"""')
    lines.append("")
    lines.append("TARGET_ID = %r" % t["order_id"])
    lines.append("COMMENT = %r" % t["comment"])
    lines.append("NOTIFY = %d" % t["notify"])
    lines.append("")
    lines.append("")
    lines.append("def run(page, base_url, sid):")
    lines.append('    page.goto("%s/?sid=%s" % (base_url.rstrip("/"), sid))')
    lines.append('    page.wait_for_selector("#menu-sales")')
    lines.append("")
    if t["join"] == "phone":
        lines.append("    # 1. the customer half of the join: Customers > All Customers,")
        lines.append("    #    Phone filter %s -> %s (%s)" % (t["phone"], t["customer"], t["email"]))
        lines.append('    page.click("#menu-customers")')
        lines.append('    page.click(\'#menu-customers .submenu a:has-text("All Customers")\')')
        lines.append('    page.wait_for_selector(\'[data-grid-id="customer_listing"] table.data-grid\')')
        lines.append('    page.click(\'[data-grid-id="customer_listing"] [data-action="grid-filter-expand"]\')')
        lines.append('    page.fill("#filter-customer_listing-billing_telephone", %r)' % t["phone"])
        lines.append('    page.click(\'[data-grid-id="customer_listing"] [data-action="grid-filter-apply"]\')')
        lines.append("    page.wait_for_timeout(300)")
        lines.append('    page.wait_for_selector(\'td:has-text("%s")\')' % t["customer"])
    else:
        lines.append("    # 1. the order half of the join: look up %s and read its customer" % t["seed_increment"])
        lines.append('    page.click("#menu-sales")')
        lines.append('    page.click(\'#menu-sales .submenu a:has-text("Orders")\')')
        lines.append('    page.wait_for_selector(\'[data-grid-id="sales_order_grid"] table.data-grid\')')
        lines.append('    page.fill(".data-grid-search-control", %r)' % t["seed_increment"])
        lines.append('    page.click(".data-grid-search-control-wrap .action-submit")')
        lines.append("    page.wait_for_timeout(300)")
        lines.append('    page.click("table.data-grid tbody tr a.action-menu-item")')
        lines.append('    page.wait_for_selector("#order_status")')
        lines.append("    # Account Information names %s (%s)" % (t["customer"], t["email"]))
    lines.append("")
    lines.append("    # 2. the orders half of the join, driven through the grid's own controls")
    lines.append('    page.click("#menu-sales")')
    lines.append('    page.click(\'#menu-sales .submenu a:has-text("Orders")\')')
    lines.append('    page.wait_for_selector(\'[data-grid-id="sales_order_grid"] table.data-grid\')')
    lines.append('    page.click(\'[data-grid-id="sales_order_grid"] [data-action="grid-filter-expand"]\')')
    for field, value in t["grid_filters"]:
        if field == "status":
            lines.append('    page.select_option("#filter-sales_order_grid-status", %r)' % value)
        else:
            lines.append('    page.fill("#filter-sales_order_grid-%s", %r)' % (field, value))
    lines.append('    page.click(\'[data-grid-id="sales_order_grid"] [data-action="grid-filter-apply"]\')')
    lines.append("    page.wait_for_timeout(300)")
    if t["sort_col"]:
        lines.append('    page.click("th.col-%s")   # ascending' % t["sort_col"])
        lines.append("    page.wait_for_timeout(200)")
        if t["sort_desc"]:
            lines.append('    page.click("th.col-%s")   # descending' % t["sort_col"])
            lines.append("    page.wait_for_timeout(200)")
    lines.append("")
    lines.append("    # 3. open the derived row and leave the comment")
    lines.append("    page.click('tr:has(#idscheck%s) a.action-menu-item' % TARGET_ID)")
    lines.append('    page.wait_for_selector("#history_comment")')
    lines.append('    page.fill("#history_comment", COMMENT)')
    if t["notify"]:
        lines.append('    page.check("#history_notify")')
    lines.append('    page.click(\'button[title="Submit Comment"]\')')
    lines.append('    page.wait_for_selector(".note-list-item")')
    lines.append("    page.wait_for_timeout(400)")
    lines.append("")
    lines.append("")
    lines.append("# Comment writer: OrderView.jsx:395-429 -> state.orderComments[<entity_id>].")
    lines.append("# Comment reader: selectors.js:140-142 getOrderComments -> OrderView.jsx:42 ->")
    lines.append("#   StatusHistoryNoteList at OrderView.jsx:500, and fullOrderHistory")
    lines.append("#   (orderHelpers.js:407) -> NoteList/CommentsBlock on the Comments History tab.")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- writer


def main():
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = []
    nemo_rows = []

    for t in TASKS:
        t["task_id"] = "customer_join_order_comment_%s_%s" % (t["slug"], t["num"])
        bundle = os.path.join(OUT, t["task_id"])
        os.makedirs(bundle, exist_ok=True)

        instr = t["instruction"]

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": t["task_id"],
                "task_instruction": instr,
                "app_dir": APP,
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": [
                    "orderComments carries exactly one commented order: %s (entity_id %s)."
                    % (t["increment"], t["order_id"]),
                    "That order holds exactly one comment entry whose comment text is exactly \"%s\"."
                    % t["comment"],
                    "The entry's is_customer_notified is %d and is_visible_on_front is 0."
                    % t["notify"],
                    "The order's status is still \"%s\" - the entry records it and no "
                    "orderOverrides status change exists for it." % t["status"],
                ],
            }, fh, indent=2)
            fh.write("\n")

        join_desc = (
            "read the customer record identified by phone %s out of Customers, then join it to "
            "that customer's orders in Sales > Orders -> comment on the order the join singles out"
            % t.get("phone")
            if t["join"] == "phone" else
            "read the owner of order %s off its order page, then join that customer back to their "
            "full order history in Sales > Orders -> comment on the order the join singles out"
            % t.get("seed_increment")
        )

        notes = [
            "Derived target: %s (entity_id %s), by %s." % (t["increment"], t["order_id"], t["rule"]),
            "Margin: %s." % t["margin"],
            "Join key: %s. The orders grid exposes no telephone column and no telephone filter "
            "(OrdersGrid.jsx:250-386), so the phone number cannot be resolved inside Sales at all; "
            "the customer record must be read first."
            % ("customers.billing_telephone %s" % t["phone"] if t["join"] == "phone"
               else "the customer named on order %s" % t.get("seed_increment")),
            "billing_name '%s' maps 1:1 onto customer entity_id %s across all 308 grid rows, so "
            "filtering Bill-to Name after the join is unambiguous." % (t["customer"], t["cust_id"]),
            "Writeback: OrderView.jsx CommentForm.submit (:395-429) appends to "
            "state.orderComments[<entity_id>]; the same key is read back by getOrderComments "
            "(selectors.js:140-142) into StatusHistoryNoteList (OrderView.jsx:500) and into "
            "fullOrderHistory (orderHelpers.js:407) for the Comments History tab.",
            "Status dropdown and both checkboxes are pinned by the instruction and asserted by the "
            "reward, so an unrequested status change or notify tick scores 0.0.",
        ]

        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump({
                "schema_version": 2,
                "task_id": t["task_id"],
                "instruction": instr,
                "apps": [{
                    "name": APP,
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
                "metadata": {
                    "style": t["style"],
                    "difficulty": "medium",
                    "shape": t["shape"],
                    "skills": ["R7", "A8"],
                    "skill_chain": join_desc,
                    "derived_from": None,
                    "official_analogues": ANALOGUES,
                    "injected_preconditions": [],
                    "topic": "customer_join_order_comment",
                    "lane": 59,
                    "inspiration_ids": INSPIRATION,
                    "authoring_notes": notes,
                },
            }, fh, indent=2)
            fh.write("\n")

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_py(t))
        nemo_code = nemo_reward_py(t)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_code)

        row = {"task_payload": {
            "task_id": t["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": instr,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": t["task_id"],
                "app_dir": APP,
                "initial_setup": None,
                "eval_reward_code": nemo_code,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=1)
            fh.write("\n")
        nemo_rows.append(row)

        with open(os.path.join(BATCH, "replays", "%s.py" % t["task_id"]), "w") as fh:
            fh.write(replay_py(t))

        index.append({"task_id": t["task_id"], "path": "%s/task.json" % t["task_id"]})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({"schema_version": 2, "tasks": index}, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")

    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
