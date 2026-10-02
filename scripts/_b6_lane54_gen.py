#!/usr/bin/env python3
"""Batch-6 lane 54 generator - shopping_admin, R10 -> A2.

Chain: run a Reports > Sales report over a stated window/period, read ONE
rendered cell out of the single interval it produces, then create a Marketing >
Cart Price Rule whose name or Discount Amount carries that derived value.

Writes 10 bundles to output/tasks/shopping_admin/report_winner_price_rule_*/
plus the lane batch directory (index.json, nemo_tasks.jsonl, GENERATION.md,
replays/).

Every figure below was computed with a Python port of
  hub/websites/webarena_shopping_admin_mock/src/components/reports/reportUtils.js
  + src/pages/reports/SalesReports.jsx + src/utils/formatters.js
and cross-checked against the three controls the mock documents in its own
source comments (Orders Jan-2022 = 11 / $1,591.89, Shipping 2022 = 215 /
$3,145.00, Bestsellers 2022-01 main-select top five).
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/report_winner_price_rule")
APP = "webarena_shopping_admin_mock"

GROUPS = {0: "NOT LOGGED IN", 1: "General", 2: "Wholesale", 3: "Retailer"}
SEEDED_RULE_IDS = [1, 2, 3, 4]

RULE_ANALOGUES = [
    'Create a new marketing cart price rule called "spring sale" for all registered customers that offers a 20 percent discount site-wide',
    'Create a new marketing cart price rule called "fall discount" for all registered customers that offers $10 discount for whole cart on checkout',
    'Create a new marketing cart price rule called "Mother\'s day sale" for all registered customers that offers 15% discount on checkout on all their cart',
    'Create a new marketing cart price rule called "Pride Month" for all registered customers that offers 45% off on all products',
    'Create a new marketing cart price rule called "Thanks giving sale" for all registered customers that offers $40 discount for whole cart on all their purchase',
]

TASKS = [
    {
        "id": "report_winner_price_rule_bestseller_hera_hoodie_apr2022_001",
        "style": "terse",
        "shape": "retrieval_writeback",
        "report": "Bestsellers Report",
        "report_path": "/admin/reports/report_sales/bestsellers/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/bestsellers/",
        "from": "4/1/2022",
        "to": "4/30/2022",
        "period": "month",
        "interval_label": "4/2022",
        "cell": "the Product cell of the top row",
        "rendered": "Hera Pullover Hoodie-XS-Green",
        "rendered_rows": "Hera Pullover Hoodie-XS-Green 2 / Quest Lumaflex™ Band 1 / Summit Watch 1 / Chaz Kangeroo Hoodie-S-Black 1 / Ajax Full-Zip Sweatshirt -XL-Red 1",
        "margin": "top row Order Quantity 2, runner-up 1 - margin 1, unique maximum",
        "derived": "name",
        "name": "Hera Pullover Hoodie-XS-Green Clearance",
        "groups": [1, 3],
        "action": "by_percent",
        "amount": "20",
        "coupon_code": None,
        "instruction": (
            "Run the Bestsellers Report for 4/1/2022 to 4/30/2022 with Period Month. "
            "Create a cart price rule for Main Website, groups General and Retailer, "
            "20 percent of product price discount, named the top row's product plus a "
            "space and Clearance."
        ),
        "analogue_report": "Get the top-1 best-selling product name(s) in 2022",
        "analogue_rule": RULE_ANALOGUES[0],
    },
    {
        "id": "report_winner_price_rule_bestseller_yoga_strap_jul2022_002",
        "style": "terse",
        "shape": "retrieval_writeback",
        "report": "Bestsellers Report",
        "report_path": "/admin/reports/report_sales/bestsellers/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/bestsellers/",
        "from": "7/1/2022",
        "to": "7/31/2022",
        "period": "month",
        "interval_label": "7/2022",
        "cell": "the Product cell of the top row",
        "rendered": "Sprite Yoga Strap 10 foot",
        "rendered_rows": "Sprite Yoga Strap 10 foot 2 / Sprite Stasis Ball 65 cm 1 / Sprite Stasis Ball 65 cm 1 / Sprite Stasis Ball 75 cm 1 / Didi Sport Watch 1",
        "margin": "top row Order Quantity 2, runner-up 1 - margin 1, unique maximum",
        "derived": "name",
        "name": "Sprite Yoga Strap 10 foot Bundle",
        "groups": [0, 1],
        "action": "cart_fixed",
        "amount": "10",
        "coupon_code": None,
        "instruction": (
            "Bestsellers Report, 7/1/2022 to 7/31/2022, Period Month. Create a cart price "
            "rule for Main Website, groups NOT LOGGED IN and General, fixed amount discount "
            "for whole cart of 10, named the top row's product plus a space and Bundle."
        ),
        "analogue_report": "Show the best sellers report from May 1, 2022 to May 31, 2023.",
        "analogue_rule": RULE_ANALOGUES[1],
    },
    {
        "id": "report_winner_price_rule_bestseller_dash_watch_janfeb2022_003",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "report": "Bestsellers Report",
        "report_path": "/admin/reports/report_sales/bestsellers/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/bestsellers/",
        "from": "1/1/2022",
        "to": "2/28/2022",
        "period": "year",
        "interval_label": "2022",
        "cell": "the Product cell of the top row",
        "rendered": "Dash Digital Watch",
        "rendered_rows": "Dash Digital Watch 3 / Sprite Stasis Ball 55 cm 2 / Sprite Yoga Strap 6 foot 2 / Sprite Yoga Strap 8 foot 2 / Impulse Duffle 1",
        "margin": "top row Order Quantity 3, runners-up 2 - margin 1, unique maximum",
        "derived": "name",
        "name": "Dash Digital Watch Winter Deal",
        "groups": [2, 3],
        "action": "by_fixed",
        "amount": "15",
        "coupon_code": None,
        "instruction": (
            "Open Reports > Products > Bestsellers and run the report from 1/1/2022 to "
            "2/28/2022 with Period set to Year, which renders a single 2022 interval. Note "
            "the product named on the top row. Then open Marketing > Cart Price Rules, click "
            "Add New Rule, and create a rule whose Rule Name is that product's name followed "
            "by a space and the words Winter Deal. Assign it to the Main Website and to the "
            "Wholesale and Retailer customer groups, leave it Active with Coupon set to No "
            "Coupon, and under Actions choose Fixed amount discount with a Discount Amount "
            "of 15. Save the rule."
        ),
        "analogue_report": "Get the top-1 best-selling product name(s) in 2022",
        "analogue_rule": RULE_ANALOGUES[2],
    },
    {
        "id": "report_winner_price_rule_bestseller_spring2023_leader_004",
        "style": "terse",
        "shape": "retrieval_writeback",
        "report": "Bestsellers Report",
        "report_path": "/admin/reports/report_sales/bestsellers/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/bestsellers/",
        "from": "2/1/2023",
        "to": "4/30/2023",
        "period": "year",
        "interval_label": "2023",
        "cell": "the Product cell of the top row",
        "rendered": "Sprite Yoga Strap 6 foot",
        "rendered_rows": "Sprite Yoga Strap 6 foot 4 / Sprite Stasis Ball 65 cm 2 / Sprite Stasis Ball 65 cm 2 / Gobi HeatTec® Tee-XS-Orange 2 / Hawkeye Yoga Short-36-Gray 2",
        "margin": "top row Order Quantity 4, runners-up 2 - margin 2, unique maximum",
        "derived": "name",
        "name": "Sprite Yoga Strap 6 foot Spring Push",
        "groups": [1],
        "action": "by_percent",
        "amount": "25",
        "coupon_code": None,
        "instruction": (
            "Bestsellers Report, 2/1/2023 to 4/30/2023, Period Year. Create a cart price rule "
            "for Main Website, group General, 25 percent of product price discount, named the "
            "top row's product plus a space and Spring Push."
        ),
        "analogue_report": "Get the top-2 best-selling product name(s) in 2023",
        "analogue_rule": RULE_ANALOGUES[3],
    },
    {
        "id": "report_winner_price_rule_bestseller_price_apr2023_005",
        "style": "terse",
        "shape": "retrieval_writeback",
        "report": "Bestsellers Report",
        "report_path": "/admin/reports/report_sales/bestsellers/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/bestsellers/",
        "from": "4/1/2023",
        "to": "4/30/2023",
        "period": "month",
        "interval_label": "4/2023",
        "cell": "the Price cell of the top row",
        "rendered": "$14.00",
        "rendered_rows": "Sprite Yoga Strap 6 foot $14.00 3 / Gobi HeatTec® Tee-XS-Orange $29.00 2 / Hawkeye Yoga Short-36-Gray $29.00 2 / Crown Summit Backpack $38.00 1 / Overnight Duffle $45.00 1",
        "margin": "top row Order Quantity 3, runners-up 2 - margin 1; its Price $14.00 differs from every other rendered Price on the interval",
        "derived": "amount",
        "name": "April Leader Cart Credit",
        "groups": [1, 2, 3],
        "action": "cart_fixed",
        "amount": "14",
        "coupon_code": None,
        "instruction": (
            "Bestsellers Report, 4/1/2023 to 4/30/2023, Period Month. Create cart price rule "
            "April Leader Cart Credit for Main Website, groups General, Wholesale and Retailer, "
            "fixed amount discount for whole cart equal to the top row's Price, digits only."
        ),
        "analogue_report": "Get the top-3 best-selling product name(s) in Jan 2023",
        "analogue_rule": RULE_ANALOGUES[4],
    },
    {
        "id": "report_winner_price_rule_orders_peak_month_count_2022_006",
        "style": "terse",
        "shape": "derived_target_mutation",
        "report": "Orders Report",
        "report_path": "/admin/reports/report_sales/sales/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/sales/",
        "from": "1/1/2022",
        "to": "12/31/2022",
        "period": "month",
        "interval_label": "2/2022",
        "cell": "the Orders cell on the 2/2022 row",
        "rendered": "16",
        "rendered_rows": "Orders by month 2022: 11, 16, 14, 8, 8, 13, 9, 8, 10, 4, 5, 10",
        "margin": "2/2022 at 16, runner-up 3/2022 at 14 - margin 2, unique maximum",
        "derived": "amount",
        "name": "Peak Season Thank You",
        "groups": [1, 3],
        "action": "by_percent",
        "amount": "16",
        "coupon_code": None,
        "instruction": (
            "Orders Report, 1/1/2022 to 12/31/2022, Period Month. Create cart price rule Peak "
            "Season Thank You for Main Website, groups General and Retailer, percent of product "
            "price discount equal to the highest monthly Orders count."
        ),
        "analogue_report": "Show the orders report from May 1, 2021 to March 31, 2022.",
        "analogue_rule": RULE_ANALOGUES[0],
    },
    {
        "id": "report_winner_price_rule_orders_items_peak_2023_007",
        "style": "explicit",
        "shape": "derived_target_mutation",
        "report": "Orders Report",
        "report_path": "/admin/reports/report_sales/sales/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/sales/",
        "from": "1/1/2023",
        "to": "5/31/2023",
        "period": "month",
        "interval_label": "1/2023",
        "cell": "the Sales Items cell on the 1/2023 row",
        "rendered": "47",
        "rendered_rows": "Sales Items by month 2023: 47, 16, 15, 30, 24",
        "margin": "1/2023 at 47, runner-up 4/2023 at 30 - margin 17, unique maximum",
        "derived": "amount",
        "name": "Volume Month Cart Credit",
        "groups": [1],
        "action": "cart_fixed",
        "amount": "47",
        "coupon_code": "VOLUME2023",
        "instruction": (
            "Open Reports > Sales > Orders and run the report from 1/1/2023 to 5/31/2023 with "
            "Period set to Month. Find the month whose Sales Items cell is the largest and note "
            "that number. Then open Marketing > Cart Price Rules and add a new rule named Volume "
            "Month Cart Credit for the Main Website and the General customer group, with Coupon "
            "set to Specific Coupon and the Coupon Code VOLUME2023. Under Actions choose Fixed "
            "amount discount for whole cart and set the Discount Amount to the Sales Items number "
            "you found. Save the rule."
        ),
        "analogue_report": "Show the sales order report for for last months (today is March 15, 2023).",
        "analogue_rule": RULE_ANALOGUES[1],
    },
    {
        "id": "report_winner_price_rule_orders_q1_2023_count_008",
        "style": "terse",
        "shape": "derived_target_mutation",
        "report": "Orders Report",
        "report_path": "/admin/reports/report_sales/sales/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/sales/",
        "from": "1/1/2023",
        "to": "3/31/2023",
        "period": "year",
        "interval_label": "2023",
        "cell": "the Orders cell of the single 2023 row",
        "rendered": "24",
        "rendered_rows": "single interval 2023: Orders 24, Sales Items 78, Sales Total $3,369.83, Sales Shipping $390.00",
        "margin": "one rendered row, so the Orders figure 24 is unique by construction; the full-year 2023 figure is 42, so a window mistake scores 0.0",
        "derived": "amount",
        "name": "Q1 2023 Recovery",
        "groups": [0, 1],
        "action": "by_percent",
        "amount": "24",
        "coupon_code": None,
        "instruction": (
            "Orders Report, 1/1/2023 to 3/31/2023, Period Year. Create cart price rule Q1 2023 "
            "Recovery for Main Website, groups NOT LOGGED IN and General, percent of product price "
            "discount equal to that row's Orders count."
        ),
        "analogue_report": "Show the sales order report for for last year (today is March 15, 2023).",
        "analogue_rule": RULE_ANALOGUES[3],
    },
    {
        "id": "report_winner_price_rule_orders_min_discount_2022_009",
        "style": "terse",
        "shape": "retrieval_writeback",
        "report": "Orders Report",
        "report_path": "/admin/reports/report_sales/sales/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/sales/",
        "from": "1/1/2022",
        "to": "12/31/2022",
        "period": "month",
        "interval_label": "6/2022",
        "cell": "the Sales Discount cell on the 6/2022 row",
        "rendered": "$20.96",
        "rendered_rows": "Sales Discount by month 2022: $43.85, $64.12, $68.14, $80.24, $0.00, $20.96, $89.96, $0.00, $0.00, $0.00, $43.41, $121.04",
        "margin": "smallest above $0.00 is 6/2022 at $20.96, next is 11/2022 at $43.41 - margin $22.45, unique minimum",
        "derived": "amount",
        "name": "Lean Discount Match",
        "groups": [1],
        "action": "cart_fixed",
        "amount": "20.96",
        "coupon_code": None,
        "instruction": (
            "Orders Report, 1/1/2022 to 12/31/2022, Period Month. Create cart price rule Lean "
            "Discount Match for Main Website, group General, fixed amount discount for whole cart "
            "equal to the smallest Sales Discount above $0.00, digits only."
        ),
        "analogue_report": "Show the orders report from May 1, 2021 to March 31, 2022.",
        "analogue_rule": RULE_ANALOGUES[4],
    },
    {
        "id": "report_winner_price_rule_shipping_min_month_2022_010",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "report": "Shipping Report",
        "report_path": "/admin/reports/report_sales/shipping/",
        "menu": "reports",
        "menu_href": "/admin/reports/report_sales/shipping/",
        "from": "1/1/2022",
        "to": "12/31/2022",
        "period": "month",
        "interval_label": "10/2022",
        "cell": "the Total Sales Shipping cell on the 10/2022 row",
        "rendered": "$125.00",
        "rendered_rows": "Total Sales Shipping by month 2022: $240.00, $320.00, $340.00, $290.00, $205.00, $400.00, $220.00, $280.00, $245.00, $125.00, $225.00, $255.00",
        "margin": "10/2022 at $125.00, next lowest 5/2022 at $205.00 - margin $80.00, unique minimum",
        "derived": "amount",
        "name": "Slow Month Shipping Rebate",
        "groups": [3],
        "action": "cart_fixed",
        "amount": "125",
        "coupon_code": "SLOWMONTH",
        "instruction": (
            "Open Reports > Sales > Shipping and run the report from 1/1/2022 to 12/31/2022 with "
            "Period set to Month. Find the month with the lowest Total Sales Shipping and note that "
            "amount. Then open Marketing > Cart Price Rules and add a new rule named Slow Month "
            "Shipping Rebate for the Main Website and the Retailer customer group, with Coupon set "
            "to Specific Coupon and the Coupon Code SLOWMONTH. Under Actions choose Fixed amount "
            "discount for whole cart and enter that amount as the Discount Amount, digits only "
            "without the dollar sign. Save the rule."
        ),
        "analogue_report": "Show the shipping report from August 5, 2022 to March 1, 2023.",
        "analogue_rule": RULE_ANALOGUES[4],
    },
]

ACTION_LABEL = {
    "by_percent": "Percent of product price discount",
    "by_fixed": "Fixed amount discount",
    "cart_fixed": "Fixed amount discount for whole cart",
    "buy_x_get_y": "Buy X get Y free (discount amount is Y)",
}


# --------------------------------------------------------------------------- #
# reward source                                                                #
# --------------------------------------------------------------------------- #

REWARD_BODY = '''
import json
from decimal import Decimal, InvalidOperation

EXPECTED = json.loads(r"""
__EXPECTED__
""")

COMPONENT_WEIGHTS = {
    "exactly_one_new_cart_price_rule": 0.30,
    "rule_identity_and_targeting_match": 0.30,
    "derived_report_value_written_exactly": 0.40,
}

SEEDED_RULE_IDS = [1, 2, 3, 4]


def _text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        return ("%d" % value) if float(value).is_integer() else ("%s" % value)
    if isinstance(value, str):
        return value.strip()
    return ""


def _amount(value):
    raw = _text(value).replace("$", "").replace(",", "").strip()
    if raw == "":
        return None
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _new_rule(state):
    rows = state.get("cartPriceRules")
    if not isinstance(rows, list) or len(rows) != 5:
        return None
    fresh = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        rid = _int(row.get("rule_id"))
        if rid is None:
            return None
        if rid not in SEEDED_RULE_IDS:
            fresh.append(row)
    if len(fresh) != 1:
        return None
    return fresh[0]


def _coupon_ok(state, rule):
    code = EXPECTED.get("coupon_code")
    if not code:
        return True
    rows = state.get("coupons")
    if not isinstance(rows, list) or len(rows) != 2:
        return False
    rid = _int(rule.get("rule_id"))
    mine = [c for c in rows if isinstance(c, dict) and _int(c.get("rule_id")) == rid]
    if len(mine) != 1:
        return False
    coupon = mine[0]
    return (
        _text(coupon.get("code")) == code
        and _int(coupon.get("is_primary")) == 1
        and _int(coupon.get("times_used")) == 0
    )


def _checks(state):
    empty = {
        "exactly_one_new_cart_price_rule": False,
        "rule_identity_and_targeting_match": False,
        "derived_report_value_written_exactly": False,
    }
    if not isinstance(state, dict):
        return empty
    rule = _new_rule(state)
    if rule is None:
        return empty

    name_ok = _text(rule.get("name")) == EXPECTED["name"]
    amount = _amount(rule.get("discount_amount"))
    amount_ok = amount is not None and amount == Decimal(EXPECTED["discount_amount"])

    if EXPECTED["derived"] == "name":
        derived_ok = name_ok
    else:
        derived_ok = amount_ok
    if not derived_ok:
        return empty

    groups = rule.get("customer_group_ids")
    groups_ok = False
    if isinstance(groups, list):
        parsed = [_int(g) for g in groups]
        if None not in parsed:
            groups_ok = sorted(parsed) == EXPECTED["customer_group_ids"]

    websites = rule.get("website_ids")
    websites_ok = False
    if isinstance(websites, list):
        parsed = [_int(w) for w in websites]
        websites_ok = parsed == [1]

    identity_ok = (
        name_ok
        and groups_ok
        and websites_ok
        and _int(rule.get("is_active")) == 1
        and _int(rule.get("coupon_type")) == EXPECTED["coupon_type"]
        and _int(rule.get("times_used")) == 0
        and isinstance(rule.get("coupons"), list)
        and len(rule.get("coupons")) == 0
        and _coupon_ok(state, rule)
    )

    action_ok = (
        amount_ok
        and _text(rule.get("simple_action")) == EXPECTED["simple_action"]
    )

    return {
        "exactly_one_new_cart_price_rule": True,
        "rule_identity_and_targeting_match": bool(identity_ok),
        "derived_report_value_written_exactly": bool(action_ok),
    }


def score_state(state):
    checks = _checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    return round(total, 6)
'''


def reward_py(task, expected_json):
    header = '"""Deterministic reward for %s.\n\n%s\n\nOnly user-visible persisted state is inspected, and only `current_state`.\nThe report figures are fixed by the frozen aggregates bundled with\nwebarena_shopping_admin_mock in ./hub/; this bundle injects no state.\n"""\n' % (
        task["id"],
        "\n".join("  * " + c for c in success_criteria(task)),
    )
    body = REWARD_BODY.replace("__EXPECTED__", expected_json)
    tail = '''

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
    return header + body + tail


def nemo_reward_py(task, expected_json):
    header = '"""NeMo-Gym reward program for %s.\n\nImplements exactly the rubric of reward.py, reading `current_state` from\nGET /go?sid=... instead of a frozen evidence bundle, and printing\nREWARD: <float> on every output path including the error path.\n\nSelf-contained: standard library plus requests, which is present in\ncuagym/requirements.txt.\n"""\n\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"\n' % task["id"]
    body = REWARD_BODY.replace("__EXPECTED__", expected_json)
    tail = '''

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
    return header + body + tail


def success_criteria(task):
    groups = ", ".join("%d (%s)" % (g, GROUPS[g]) for g in task["groups"])
    out = [
        "state.cartPriceRules holds exactly 5 rules - the 4 seeded rules (rule_id 1-4) plus exactly one new rule; the untouched seed has 4, so an empty episode scores 0.0",
        'the new rule\'s name is exactly "%s"%s'
        % (
            task["name"],
            " - the Product cell of the top row of the %s run from %s to %s at Period=%s"
            % (task["report"], task["from"], task["to"], task["period"])
            if task["derived"] == "name"
            else "",
        ),
        "the new rule's website_ids == [1], is_active == 1, coupon_type == %d and customer_group_ids == [%s]"
        % (task["coupon_type"], groups),
        'the new rule\'s simple_action is "%s" (%s) and its discount_amount equals %s numerically%s'
        % (
            task["action"],
            ACTION_LABEL[task["action"]],
            task["amount"],
            " - %s of the %s run from %s to %s at Period=%s, rendered %s"
            % (task["cell"], task["report"], task["from"], task["to"], task["period"], task["rendered"])
            if task["derived"] == "amount"
            else "",
        ),
    ]
    if task["coupon_code"]:
        out.append(
            'state.coupons holds exactly 2 rows and the one whose rule_id is the new rule carries code "%s", is_primary 1, times_used 0'
            % task["coupon_code"]
        )
    return out


def replay(task):
    groups = json.dumps([str(g) for g in task["groups"]])
    coupon_steps = ""
    if task["coupon_code"]:
        coupon_steps = (
            '    page.select_option("#coupon_type", "2")\n'
            '    page.fill("#coupon_code", %r)\n' % task["coupon_code"]
        )
    return '''"""Golden replay DRAFT for %(id)s.

Click-only: after the initial landing on `start_path` there is no page.goto(),
no constructed URL and no go_back() to a URL that was never clicked.

Task: %(instruction)s

Derived answer (computed offline with a Python port of reportUtils.js /
SalesReports.jsx / formatters.js - NOT given to the agent):
  %(report)s, From %(from)s, To %(to)s, Period %(period)s
  single rendered interval: %(interval_label)s
  rendered rows: %(rows)s
  target cell: %(cell)s -> %(rendered)s
  margin: %(margin)s
  written as: rule name %(name)r, simple_action %(action)r, discount_amount %(amount)r

Reachability notes verified while authoring:
  * "/" redirects to /admin/admin/dashboard/ (App.jsx:624). Rail items with a
    submenu are <a href="#" class="menu-item"> and pin their flyout on click
    (AdminSidebar.jsx:67-99, id="menu-<section>").
  * Reports flyout: Sales > Orders /admin/reports/report_sales/sales/ and
    Shipping /admin/reports/report_sales/shipping/ (adminMenu.js:176-179),
    Products > Bestsellers /admin/reports/report_sales/bestsellers/
    (adminMenu.js:196).
  * Marketing flyout: Promotions > Cart Price Rules
    /admin/sales_rule/promo_quote/ (adminMenu.js:81).
  * Report filter ids are the source's verbatim: #sales_report_from,
    #sales_report_to, #sales_report_period_type, submit #filter_form_submit
    (ReportPage.jsx:116-166). A bare load renders an empty grid because
    `applied` requires a From or To (ReportPage.jsx:61).
  * Cart Price Rules grid -> "Add New Rule" is id="add" (Marketing.jsx:103).
    The form controls are #rule_name, #website_ids, #customer_group_ids,
    #coupon_type, #coupon_code, #simple_action, #discount_amount and the
    primary button #save (Marketing.jsx:328-560).
  * The write lands in state.cartPriceRules via save() (Marketing.jsx:239-261),
    which is the same key the Cart Price Rules grid renders from
    (Marketing.jsx:57).
"""

RULE_NAME = %(name)r
DISCOUNT_AMOUNT = %(amount)r


def run(page, base_url, sid):
    # start_path = '/'
    page.click("#menu-reports > a.menu-item")
    page.click('#menu-reports a[href*="%(menu_href)s"]')
    page.wait_for_load_state("networkidle")

    # R10 - configure the window and period, then run the report.
    page.fill("#sales_report_from", %(from)r)
    page.fill("#sales_report_to", %(to)r)
    page.select_option("#sales_report_period_type", %(period)r)
    page.click("#filter_form_submit")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("table.data-grid tbody tr")

    # A2 - create the cart price rule named for / valued from that cell.
    page.click("#menu-marketing > a.menu-item")
    page.click('#menu-marketing a[href*="/admin/sales_rule/promo_quote/"]')
    page.wait_for_load_state("networkidle")
    page.click("#add")
    page.wait_for_selector("#rule_name")
    page.fill("#rule_name", RULE_NAME)
    page.select_option("#website_ids", ["1"])
    page.select_option("#customer_group_ids", %(groups)s)
%(coupon)s    page.select_option("#simple_action", %(action)r)
    page.fill("#discount_amount", DISCOUNT_AMOUNT)
    page.click("#save")
    page.wait_for_load_state("networkidle")
''' % {
        "id": task["id"],
        "instruction": task["instruction"],
        "report": task["report"],
        "from": task["from"],
        "to": task["to"],
        "period": task["period"],
        "interval_label": task["interval_label"],
        "rows": task["rendered_rows"],
        "cell": task["cell"],
        "rendered": task["rendered"],
        "margin": task["margin"],
        "name": task["name"],
        "action": task["action"],
        "amount": task["amount"],
        "menu_href": task["menu_href"],
        "groups": groups,
        "coupon": coupon_steps,
    }


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []

    for task in TASKS:
        task["coupon_type"] = 2 if task["coupon_code"] else 1
        bundle = os.path.join(OUT, task["id"])
        os.makedirs(bundle, exist_ok=True)

        expected = {
            "name": task["name"],
            "derived": task["derived"],
            "discount_amount": task["amount"],
            "simple_action": task["action"],
            "customer_group_ids": sorted(task["groups"]),
            "coupon_type": task["coupon_type"],
            "coupon_code": task["coupon_code"],
            "report": task["report"],
            "from": task["from"],
            "to": task["to"],
            "period": task["period"],
            "cell": task["cell"],
            "rendered": task["rendered"],
        }
        expected_json = json.dumps(expected, indent=2, ensure_ascii=False)

        crit = success_criteria(task)

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": task["id"],
                "task_instruction": task["instruction"],
                "app_dir": APP,
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": crit,
            }, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

        manifest = {
            "schema_version": 2,
            "task_id": task["id"],
            "instruction": task["instruction"],
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
                "style": task["style"],
                "difficulty": "medium",
                "shape": task["shape"],
                "skills": ["R10", "A2"],
                "skill_chain": "run the %s over the stated window and period and read the ranked cell it renders -> create a cart price rule carrying that value" % task["report"],
                "derived_from": None,
                "official_analogues": [task["analogue_report"], task["analogue_rule"]],
                "topic": "report_winner_price_rule",
                "lane": "report_winner_price_rule",
                "batch": "batch-6 lane 54 (shopping_admin / R10 -> A2)",
                "surface": "%s (filter #sales_report_from / #sales_report_to / #sales_report_period_type -> #filter_form_submit) -> /admin/sales_rule/promo_quote/ -> #add -> /admin/sales_rule/promo_quote/new/ (#rule_name, #website_ids, #customer_group_ids, #coupon_type, #simple_action, #discount_amount, #save)" % task["report_path"],
                "inspiration_ids": ["webarena-0", "webarena-4", "webarena-699", "webarena-700", "webarena-703", "webarena-709", "webarena-710", "webarena-713"],
                "authoring_notes": [
                    "Pristine seed - no initial_setup.py. reportAggregates / bestsellersAggregates / reportAggregatesOrder are bundled ES imports (SalesReports.jsx:12-14, staticData.js:29+50), outside the 44 persisted state keys, so no injection can reach the reports; difficulty is varied by interval, column and row selection instead.",
                    "Retrieval: %s, From %s, To %s, Period=%s. Single rendered interval %s. Rendered rows: %s. Target cell: %s -> %s." % (task["report"], task["from"], task["to"], task["period"], task["interval_label"], task["rendered_rows"], task["cell"], task["rendered"]),
                    "Tie margin checked by hand: %s" % task["margin"],
                    "Writeback vessel persists AND is read back: save() writes state.cartPriceRules (and state.coupons) at Marketing.jsx:239-261, which is the same key the Cart Price Rules grid renders from at Marketing.jsx:57 and the edit form reads at Marketing.jsx:190. stateTracker.js:156 lists the same paths.",
                    "The seed holds 4 cart price rules (data/cartPriceRules.json, rule_id 1-4: 'Buy 3 tee shirts and get the 4th free', 'Spend $50 or more - shipping is free!', '20% OFF Ever $200-plus purchase!*', rule 4). None carries this rule's name, action or amount, so the untouched state scores exactly 0.0.",
                    "Every component is gated on the DERIVED value, so an agent that skips the report and guesses scores 0.0 rather than partial credit (batch-6 CORRECTIONS B6-2).",
                    "The Dashboard's default Bestsellers tab (Dashboard.jsx:74-112) renders an ALL-TIME top five whose row 1 is Sprite Stasis Ball 65 cm; none of this lane's derived answers is that string, so the landing page cannot answer any of these tasks.",
                    "Period=Year windows all stay inside one calendar year, so exactly one interval renders (CORRECTIONS #93) and the silent year-straddle drop of CORRECTIONS #94 is avoided.",
                    "discount_amount is persisted as a string (Marketing.jsx:219); the rubric compares it as a Decimal after stripping $ and thousands separators, so '20', '20.00' and '$20.00' all pass and '21' does not.",
                ],
                "hard_criteria": [],
                "has_initial_setup": False,
                "injected_preconditions": [],
            },
        }
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_py(task, expected_json))
        nemo = nemo_reward_py(task, expected_json)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo)

        row = {"task_payload": {
            "task_id": task["id"],
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
                "bundle_id": task["id"],
                "app_dir": APP,
                "initial_setup": None,
                "eval_reward_code": nemo,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        rows.append(row)

        with open(os.path.join(BATCH, "replays", task["id"] + ".py"), "w") as fh:
            fh.write(replay(task))

        index["tasks"].append({"task_id": task["id"], "path": "../../%s/task.json" % task["id"]})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
