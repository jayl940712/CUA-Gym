#!/usr/bin/env python3
"""Batch-6 lane 53 generator: shopping_admin R10 -> A7.

Chain: configure a Sales/Products report over a stated window and period,
read one rendered cell out of it, and record that figure verbatim in a NEW
System > Other Settings > Custom Variable.

Every expected value in TASKS was computed with scripts/_b6_lane53_engine.py,
a line-for-line Python port of reportUtils.js + SalesReports.jsx + formatters.js,
validated against three figures the mock documents in its own source comments
(Shipping 2022 = 215 / $3,145.00, Orders 2022 = 116 / $15,475.46,
Orders Jan-2022 "Any" = 11 / $1,591.89).

Writes bundles to output/tasks/shopping_admin/<task_id>/ and lane artefacts to
output/tasks/shopping_admin/_batches/report_figure_custom_variable/.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
LANE = os.path.join(OUT, "_batches/report_figure_custom_variable")
APP = "webarena_shopping_admin_mock"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

SHIPPING = "/admin/reports/report_sales/shipping/"
ORDERS = "/admin/reports/report_sales/sales/"
BEST = "/admin/reports/report_sales/bestsellers/"
VARS = "/admin/admin/system_variable/"

A_SHIPPING = "Show the shipping report from August 5, 2022 to March 1, 2023."
A_ORDERS = "Show the orders report from May 1, 2021 to March 31, 2022."
A_LASTMONTH = "Show the sales order report for for last months (today is March 15, 2023)."
A_LASTYEAR = "Show the sales order report for for last year (today is March 15, 2023)."
A_BEST = "Show the best sellers report from May 1, 2022 to May 31, 2023."
A_BEST1 = "Get the top-1 best-selling product name(s) in 2022"
A_BEST2 = "Get the top-2 best-selling product name(s) in 2023"

TASKS = [
    {
        "id": "report_figure_custom_variable_shipping_peak_month_q4_2022_001",
        "style": "terse",
        "start_path": "/",
        "report": "shipping",
        "report_path": SHIPPING,
        "report_title": "Shipping Report",
        "date_from": "10/1/2022",
        "date_to": "12/31/2022",
        "period": "month",
        "status": None,
        "cell": "the Total Sales Shipping cell on the 12/2022 row",
        "code": "shipping_peak_month_q4_2022",
        "name": "Q4 Peak Shipping",
        "value": "$255.00",
        "instruction": (
            "Shipping Report, 10/1/2022 to 12/31/2022, Period Month. Save the Total Sales Shipping "
            "of the month with the most orders, exactly as rendered with $ and cents, as a new "
            "custom variable: code shipping_peak_month_q4_2022, name Q4 Peak Shipping, Plain Value."
        ),
        "rendered": "10/2022 = 9 orders / $125.00, 11/2022 = 14 / $225.00, 12/2022 = 16 / $255.00",
        "margin": "busiest month 12/2022 at 16 orders, runner-up 11/2022 at 14 - margin 2 orders, unique maximum",
        "derived_from": "shipping_revenue_ledger_quarterly_ledger_gap_009",
        "analogues": [A_SHIPPING, A_LASTMONTH],
    },
    {
        "id": "report_figure_custom_variable_shipping_busiest_month_h1_2023_002",
        "style": "explicit",
        "start_path": "/",
        "report": "shipping",
        "report_path": SHIPPING,
        "report_title": "Shipping Report",
        "date_from": "1/1/2023",
        "date_to": "6/30/2023",
        "period": "month",
        "status": None,
        "cell": "the Orders cell on the 1/2023 row",
        "code": "shipping_busiest_month_h1_2023",
        "name": "H1 2023 Busiest Shipping Month",
        "value": "21",
        "instruction": (
            "Open Reports > Sales > Shipping. Set From to 1/1/2023, To to 6/30/2023 and Period to "
            "Month, then press Show Report. Find the month row carrying the largest Orders count and "
            "note that count. Then go to System > Other Settings > Custom Variables, click Add New "
            "Variable, and save a variable whose Variable Code is shipping_busiest_month_h1_2023, "
            "whose Variable Name is H1 2023 Busiest Shipping Month, and whose Variable Plain Value is "
            "that count written as a bare number with no other characters."
        ),
        "rendered": "1/2023 = 21 orders, 2/2023 = 17, 3/2023 = 16, 4/2023 = 19, 5/2023 = 12 (June 2023 has no shipping rows and renders no interval)",
        "margin": "1/2023 at 21 orders, runner-up 4/2023 at 19 - margin 2 orders, unique maximum",
        "derived_from": "shipping_revenue_ledger_first_quarter_orders_003",
        "analogues": [A_SHIPPING],
    },
    {
        "id": "report_figure_custom_variable_orders_peak_month_h1_2022_003",
        "style": "terse",
        "start_path": "/",
        "report": "orders",
        "report_path": ORDERS,
        "report_title": "Orders Report",
        "date_from": "1/1/2022",
        "date_to": "6/30/2022",
        "period": "month",
        "status": None,
        "cell": "the Sales Total cell on the 2/2022 row",
        "code": "orders_peak_month_h1_2022",
        "name": "H1 Peak Sales",
        "value": "$2,125.68",
        "instruction": (
            "Orders Report, 1/1/2022 to 6/30/2022, Period Month. Store the Sales Total of the month "
            "with the most orders, exactly as rendered including $, comma and cents, as a new custom "
            "variable: code orders_peak_month_h1_2022, name H1 Peak Sales, Plain Value."
        ),
        "rendered": "1/2022 = 11 orders / $1,591.89, 2/2022 = 16 / $2,125.68, 3/2022 = 14 / $1,841.76, 4/2022 = 8 / $1,129.60, 5/2022 = 8 / $1,193.60, 6/2022 = 13 / $1,390.74",
        "margin": "2/2022 at 16 orders, runner-up 3/2022 at 14 - margin 2 orders, unique maximum",
        "derived_from": "publish_quarter_numbers_stronger_half_2022_005",
        "analogues": [A_ORDERS, A_LASTMONTH],
    },
    {
        "id": "report_figure_custom_variable_orders_quiet_month_q1_2023_004",
        "style": "explicit",
        "start_path": "/",
        "report": "orders",
        "report_path": ORDERS,
        "report_title": "Orders Report",
        "date_from": "1/1/2023",
        "date_to": "3/31/2023",
        "period": "month",
        "status": None,
        "cell": "the Sales Total cell on the 3/2023 row",
        "code": "orders_quiet_month_q1_2023",
        "name": "Q1 2023 Quietest Month Sales Total",
        "value": "$560.60",
        "instruction": (
            "Open Reports > Sales > Orders, set From to 1/1/2023, To to 3/31/2023 and Period to "
            "Month, and press Show Report. Identify the month row with the fewest orders and read its "
            "Sales Total. Then, under System > Other Settings > Custom Variables, add a new variable "
            "with Variable Code orders_quiet_month_q1_2023, Variable Name Q1 2023 Quietest Month "
            "Sales Total, and Variable Plain Value set to that Sales Total copied exactly as the "
            "report renders it, including the dollar sign and the two decimals."
        ),
        "rendered": "1/2023 = 12 orders / $2,060.23, 2/2023 = 7 / $749.00, 3/2023 = 5 / $560.60",
        "margin": "3/2023 at 5 orders, runner-up 2/2023 at 7 - margin 2 orders, unique minimum",
        "derived_from": "publish_quarter_numbers_q1_monthly_counts_008",
        "analogues": [A_ORDERS, A_LASTMONTH],
    },
    {
        "id": "report_figure_custom_variable_orders_sales_items_2023_005",
        "style": "terse",
        "start_path": "/",
        "report": "orders",
        "report_path": ORDERS,
        "report_title": "Orders Report",
        "date_from": "1/1/2023",
        "date_to": "12/31/2023",
        "period": "year",
        "status": None,
        "cell": "the Sales Items cell on the single 2023 row",
        "code": "orders_sales_items_2023",
        "name": "2023 Sales Items",
        "value": "132",
        "instruction": (
            "Orders Report, 1/1/2023 to 12/31/2023, Period Year. Store its Sales Items figure, digits "
            "only, as a new custom variable: code orders_sales_items_2023, name 2023 Sales Items, "
            "Plain Value."
        ),
        "rendered": "one interval row labelled 2023: Orders 42, Sales Items 132, Sales Total $5,873.48",
        "margin": "single interval; the window stays inside one calendar year so intervalsBetween emits exactly one bucket (CORRECTIONS #93)",
        "derived_from": "publish_quarter_numbers_ytd_sales_items_006",
        "analogues": [A_LASTYEAR, A_ORDERS],
    },
    {
        "id": "report_figure_custom_variable_orders_discount_peak_month_2022_006",
        "style": "terse",
        "start_path": "/",
        "report": "orders",
        "report_path": ORDERS,
        "report_title": "Orders Report",
        "date_from": "1/1/2022",
        "date_to": "12/31/2022",
        "period": "month",
        "status": None,
        "cell": "the Sales Discount cell on the 12/2022 row",
        "code": "orders_discount_peak_month_2022",
        "name": "Top Discount Month 2022",
        "value": "$121.04",
        "instruction": (
            "Orders Report, all of 2022, Period Month. Save the largest monthly Sales Discount, "
            "exactly as rendered with $ and cents, as a new custom variable: code "
            "orders_discount_peak_month_2022, name Top Discount Month 2022, Plain Value."
        ),
        "rendered": "12/2022 Sales Discount $121.04; the other eleven months read $43.85, $64.12, $68.14, $80.24, $0.00, $20.96, $89.96, $0.00, $0.00, $0.00, $43.41",
        "margin": "12/2022 at $121.04, runner-up 7/2022 at $89.96 - margin $31.08, unique maximum",
        "derived_from": "publish_quarter_numbers_shipping_line_2022_009",
        "analogues": [A_ORDERS, A_LASTMONTH],
    },
    {
        "id": "report_figure_custom_variable_orders_only_taxed_month_2022_007",
        "style": "terse",
        "start_path": "/",
        "report": "orders",
        "report_path": ORDERS,
        "report_title": "Orders Report",
        "date_from": "1/1/2022",
        "date_to": "12/31/2022",
        "period": "month",
        "status": None,
        "cell": "the Sales Tax cell on the 4/2022 row",
        "code": "orders_taxed_month_2022",
        "name": "2022 Sales Tax",
        "value": "$2.64",
        "instruction": (
            "Orders Report, all of 2022, Period Month. Exactly one month collected Sales Tax; save "
            "that figure, as rendered with $ and cents, as a new custom variable: code "
            "orders_taxed_month_2022, name 2022 Sales Tax, Plain Value."
        ),
        "rendered": "4/2022 Sales Tax $2.64; every other 2022 month renders $0.00",
        "margin": "4/2022 is the only non-zero Sales Tax cell in the whole year - eleven $0.00 rows, no tie",
        "derived_from": None,
        "analogues": [A_ORDERS, A_LASTMONTH],
    },
    {
        "id": "report_figure_custom_variable_bestseller_price_2023_008",
        "style": "terse",
        "start_path": BEST,
        "report": "bestsellers",
        "report_path": BEST,
        "report_title": "Bestsellers Report",
        "date_from": "1/1/2023",
        "date_to": "12/31/2023",
        "period": "year",
        "status": None,
        "cell": "the Price cell on the top row of the 2023 interval",
        "code": "bestseller_price_2023",
        "name": "2023 Bestseller Price",
        "value": "$14.00",
        "instruction": (
            "Run this Bestsellers Report for 1/1/2023 to 12/31/2023, Period Year. Save the Price on "
            "its top row, as rendered with $ and cents, as a new custom variable: code "
            "bestseller_price_2023, name 2023 Bestseller Price, Plain Value."
        ),
        "rendered": "2023 rows: Sprite Yoga Strap 6 foot $14.00 qty 4, Overnight Duffle $45.00 qty 3, Ida Workout Parachute Pant-29-Purple $38.40 qty 3, Impulse Duffle $74.00 qty 2, Sprite Stasis Ball 65 cm $27.00 qty 2",
        "margin": "top row qty 4, runner-up qty 3 - margin 1 unit, unique leader; the leader is the same product under the yearly table and under the boundary select, so the Price cell is $14.00 either way",
        "derived_from": "promote_the_bestseller_2023_named_leader_002",
        "analogues": [A_BEST, A_BEST2],
    },
    {
        "id": "report_figure_custom_variable_bestseller_apr_2022_product_009",
        "style": "terse",
        "start_path": "/",
        "report": "bestsellers",
        "report_path": BEST,
        "report_title": "Bestsellers Report",
        "date_from": "4/1/2022",
        "date_to": "4/30/2022",
        "period": "month",
        "status": None,
        "cell": "the Product cell on the top row of the 4/2022 interval",
        "code": "bestseller_apr_2022",
        "name": "April 2022 Bestseller",
        "value": "Hera Pullover Hoodie-XS-Green",
        "instruction": (
            "Bestsellers Report, 4/1/2022 to 4/30/2022, Period Month. Copy the product name on its "
            "top row exactly into a new custom variable: code bestseller_apr_2022, name April 2022 "
            "Bestseller, Plain Value."
        ),
        "rendered": "4/2022 rows: Hera Pullover Hoodie-XS-Green $48.00 qty 2, then Quest Lumaflex(tm) Band, Summit Watch, Chaz Kangeroo Hoodie-S-Black, Ajax Full-Zip Sweatshirt -XL-Red, all qty 1",
        "margin": "top row qty 2, four runners-up at qty 1 - margin 1 unit, unique leader, and the winner's name is plain ASCII with no HTML entity to decode",
        "derived_from": "promote_the_bestseller_2022_badge_units_001",
        "analogues": [A_BEST, A_BEST1],
    },
    {
        "id": "report_figure_custom_variable_bestsellers_q3_2022_units_010",
        "style": "explicit",
        "start_path": VARS,
        "report": "bestsellers",
        "report_path": BEST,
        "report_title": "Bestsellers Report",
        "date_from": "7/1/2022",
        "date_to": "9/30/2022",
        "period": "month",
        "status": None,
        "cell": "the Order Quantity cell on the Total row",
        "code": "bestsellers_q3_2022_units",
        "name": "Q3 2022 Bestseller Units",
        "value": "17",
        "instruction": (
            "We need the Q3 2022 top-five volume on record. Open Reports > Products > Bestsellers, "
            "set From to 7/1/2022, To to 9/30/2022 and Period to Month, and press Show Report. Read "
            "the Order Quantity on the grid's Total row at the foot of the table. Then come back "
            "here, click Add New Variable, and save Variable Code bestsellers_q3_2022_units, Variable "
            "Name Q3 2022 Bestseller Units, and Variable Plain Value equal to that number written as "
            "bare digits."
        ),
        "rendered": "three monthly intervals (7/2022, 8/2022, 9/2022) of five rows each; the tfoot Total row sums Order Quantity to 17",
        "margin": "the Total row is a single rendered cell, not a superlative - 6 + 5 + 6 = 17 across the three intervals, and no other cell on the page reads 17",
        "derived_from": "promote_the_bestseller_lumaflex_love_count_009",
        "analogues": [A_BEST, A_BEST1],
    },
]

SKILL_CHAIN = ("configure the report over the stated window and period and read the one cell it "
               "produces -> transfer that figure verbatim into a new custom variable")

MENU_ID = {"shipping": "reports", "orders": "reports", "bestsellers": "reports"}


# --------------------------------------------------------------- reward source

REWARD_HEAD = '''"""Deterministic reward for {tid}.

Success criteria:
  * System > Other Settings > Custom Variables holds exactly one record, whose
    Variable Code is "{code}" and whose Variable Name is "{name}"
  * that record's Variable Plain Value is exactly "{value}" - {cellsrc}
    of the {title} run from {dfrom} to {dto} at Period={period}

Only user-visible persisted state is inspected, and only `current_state`.
The figure is fixed by the frozen report aggregates bundled with
webarena_shopping_admin_mock in ./hub/; this bundle injects no state.
"""

import json

EXPECTED = json.loads(r"""
{expected_json}
""")

COMPONENT_WEIGHTS = {{
    "custom_variable_created_with_requested_code_and_name": 0.4,
    "plain_value_equals_report_figure": 0.6,
}}


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


def _sole_variable(state):
    config = state.get("systemConfig")
    if not isinstance(config, dict):
        return None
    rows = config.get("variables")
    if not isinstance(rows, list) or len(rows) != 1:
        return None
    row = rows[0]
    if not isinstance(row, dict):
        return None
    return row


def _checks(state):
    row = _sole_variable(state)
    if row is None:
        return {{
            "custom_variable_created_with_requested_code_and_name": False,
            "plain_value_equals_report_figure": False,
        }}
    identity_ok = (
        _text(row.get("code")) == EXPECTED["code"]
        and _text(row.get("name")) == EXPECTED["name"]
    )
    value_ok = identity_ok and _text(row.get("plain_value")) == EXPECTED["plain_value"]
    return {{
        "custom_variable_created_with_requested_code_and_name": bool(identity_ok),
        "plain_value_equals_report_figure": bool(value_ok),
    }}
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

NEMO_HEAD = '''"""NeMo-Gym reward program for {tid}.

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
BASE_URL = "{placeholder}"

EXPECTED = json.loads(r"""
{expected_json}
""")

COMPONENT_WEIGHTS = {{
    "custom_variable_created_with_requested_code_and_name": 0.4,
    "plain_value_equals_report_figure": 0.6,
}}


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


def _sole_variable(state):
    config = state.get("systemConfig")
    if not isinstance(config, dict):
        return None
    rows = config.get("variables")
    if not isinstance(rows, list) or len(rows) != 1:
        return None
    row = rows[0]
    if not isinstance(row, dict):
        return None
    return row


def _checks(state):
    row = _sole_variable(state)
    if row is None:
        return {{
            "custom_variable_created_with_requested_code_and_name": False,
            "plain_value_equals_report_figure": False,
        }}
    identity_ok = (
        _text(row.get("code")) == EXPECTED["code"]
        and _text(row.get("name")) == EXPECTED["name"]
    )
    value_ok = identity_ok and _text(row.get("plain_value")) == EXPECTED["plain_value"]
    return {{
        "custom_variable_created_with_requested_code_and_name": bool(identity_ok),
        "plain_value_equals_report_figure": bool(value_ok),
    }}
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

REPLAY = '''"""Golden replay DRAFT for {tid}.

Click-only: after the initial landing on `start_path` there is no page.goto(),
no constructed URL and no go_back() to a URL that was never clicked.

Task: {instruction}

Derived answer (computed offline with scripts/_b6_lane53_engine.py, a port of
reportUtils.js / SalesReports.jsx / formatters.js - NOT given to the agent):
  {title}, From {dfrom}, To {dto}, Period {period}{statusline}
  rendered: {rendered}
  target cell: {cell}
  value written: {value!r}
  margin: {margin}

Reachability notes verified while authoring:
  * "/" redirects to /admin/admin/dashboard/ (App.jsx:624). Rail items with a
    submenu are <a href="#" class="menu-item"> and pin their flyout on click
    (AdminSidebar.jsx:84-99).
  * Reports flyout carries Sales > Orders / Shipping (adminMenu.js:174-179) and
    Products > Bestsellers (adminMenu.js:196).
  * System flyout carries Other Settings > Custom Variables (adminMenu.js:305).
  * Report filter control ids are the source's verbatim: #sales_report_from,
    #sales_report_to, #sales_report_period_type, #sales_report_show_order_statuses,
    #sales_report_order_statuses, and the submit button #filter_form_submit
    (ReportPage.jsx:110-190). A bare page load renders an empty grid because
    `applied` requires a From or To (ReportPage.jsx:61).
  * Custom Variables grid button is #add (Tools.jsx:35-40) and routes to
    /admin/admin/system_variable/new/ (App.jsx:434). The form's inputs are
    #rf_code, #rf_name, #rf_html_value, #rf_plain_value (RecordForm.jsx:100-105)
    and the primary button is #save (RecordForm.jsx:234).
  * The write lands in state.systemConfig.variables via
    useSystemCollection('variables','variable_id').add (RecordForm.jsx:27-43,
    Tools.jsx:1005-1007), which is the same key CustomVariables renders from
    (Tools.jsx:29). The seed for that key is [] (data/systemConfig.json).
"""

CODE = {code!r}
NAME = {name!r}
VALUE = {value!r}


def run(page, base_url, sid):
    # start_path = {start_path!r}
{nav_report}
    # R10 - configure the report window and period, then run it.
    page.fill("#sales_report_from", {dfrom!r})
    page.fill("#sales_report_to", {dto!r})
    page.select_option("#sales_report_period_type", {period!r})
{status_steps}    page.click("#filter_form_submit")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("table.data-grid tbody tr")

{nav_vars}
    # A7 - transfer the figure into a brand-new custom variable.
    page.click("#add")
    page.wait_for_selector("#rf_code")
    page.fill("#rf_code", CODE)
    page.fill("#rf_name", NAME)
    page.fill("#rf_plain_value", VALUE)
    page.click("#save")
    page.wait_for_load_state("networkidle")
'''


def nav_to(path, menu_id, indent="    "):
    return (
        '%spage.click("#menu-%s > a.menu-item")\n'
        '%spage.click(\'#menu-%s a[href*="%s"]\')\n'
        '%spage.wait_for_load_state("networkidle")\n'
    ) % (indent, menu_id, indent, menu_id, path, indent)


def build(task):
    tid = task["id"]
    bundle = os.path.join(OUT, tid)
    os.makedirs(bundle, exist_ok=True)

    expected = {
        "code": task["code"],
        "name": task["name"],
        "plain_value": task["value"],
        "report": task["report_title"],
        "from": task["date_from"],
        "to": task["date_to"],
        "period": task["period"],
        "cell": task["cell"],
    }
    expected_json = json.dumps(expected, indent=2, ensure_ascii=True)

    criteria = [
        'state.systemConfig.variables holds exactly one record - the seed for that key is [], '
        'so an untouched episode scores 0.0',
        'that record\'s code reads "%s" and its name reads "%s"' % (task["code"], task["name"]),
        'that record\'s plain_value equals "%s" exactly - %s of the %s run from %s to %s at '
        'Period=%s; the field must EQUAL the figure, not contain it' % (
            task["value"], task["cell"], task["report_title"],
            task["date_from"], task["date_to"], task["period"]),
    ]

    with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
        json.dump({
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP,
            "start_path": task["start_path"],
            "difficulty": "medium",
            "success_criteria": criteria,
        }, fh, indent=2)
        fh.write("\n")

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [{
            "name": APP,
            "source_name": "shopping_admin",
            "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
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
            "skills": ["R10", "A7"],
            "skill_chain": SKILL_CHAIN,
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "topic": "report_figure_custom_variable",
            "lane": "report_figure_custom_variable",
            "batch": "batch-6 lane 53 (shopping_admin / R10 -> A7)",
            "surface": "%s (filter form #sales_report_from / #sales_report_to / "
                       "#sales_report_period_type -> #filter_form_submit) -> %s -> #add -> "
                       "/admin/admin/system_variable/new/ (#rf_code, #rf_name, #rf_plain_value, #save)"
                       % (task["report_path"], VARS),
            "inspiration_ids": ["webarena-0", "webarena-6", "webarena-260", "webarena-262",
                                "webarena-264", "webarena-266"],
            "authoring_notes": [
                "Pristine seed - no initial_setup.py. The three usable report families "
                "(Orders, Shipping, Bestsellers) are bundled ES imports outside the 44 "
                "persisted state keys (SalesReports.jsx:12-14), so no injection can reach "
                "them; difficulty is varied by interval, column and row selection instead.",
                "Rendered figures were derived with a Python port of reportUtils.js + "
                "SalesReports.jsx + formatters.js, validated against three controls the mock "
                "documents in its own comments: Shipping 2022 = 215 orders / $3,145.00 "
                "(reportUtils.js:341-347), Orders 2022 = 116 / $15,475.46, and Orders "
                "January 2022 with Order Status Any = 11 / $1,591.89 (reportUtils.js:334-338).",
                "%s report, %s to %s, Period=%s. Rendered: %s" % (
                    task["report_title"], task["date_from"], task["date_to"],
                    task["period"], task["rendered"]),
                "Tie margin: %s" % task["margin"],
                "Writeback vessel persists AND is read back: CustomVariableForm's onSave calls "
                "useSystemCollection('variables','variable_id').add (Tools.jsx:1005-1007), which "
                "writes state.systemConfig.variables (RecordForm.jsx:31-37); the CustomVariables "
                "grid renders from state?.systemConfig?.variables (Tools.jsx:29). The key is "
                "declared in the baseline as [] (dataManager.js:280-281 + data/systemConfig.json), "
                "so one new row is an unambiguous diff.",
                "Custom Variables are CREATE-ONLY on this mock (CORRECTIONS #76): App.jsx "
                "registers only :356 index and :434 new, and the grid passes no rowHref. The "
                "append shape is therefore the only authorable one, and 'exactly one record' is a "
                "clean exact-collection assertion.",
                "The rubric asserts the field EQUALS the derived string (CORRECTIONS #23), never "
                "original + value, and pays only for what the agent made true.",
                "No year-boundary straddle anywhere in this lane: every Period=Year window stays "
                "inside one calendar year, so intervalsBetween emits exactly one bucket "
                "(CORRECTIONS #93) and the silent-drop trap of CORRECTIONS #94 is avoided.",
            ],
            "hard_criteria": [],
            "has_initial_setup": False,
            "injected_preconditions": [],
        },
    }
    with open(os.path.join(bundle, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    cellsrc = task["cell"]
    reward = REWARD_HEAD.format(
        tid=tid, code=task["code"], name=task["name"], value=task["value"],
        cellsrc=cellsrc, title=task["report_title"], dfrom=task["date_from"],
        dto=task["date_to"], period=task["period"], expected_json=expected_json,
    ) + REWARD_TAIL
    with open(os.path.join(bundle, "reward.py"), "w") as fh:
        fh.write(reward)

    nemo = NEMO_HEAD.format(tid=tid, placeholder=PLACEHOLDER,
                            expected_json=expected_json) + NEMO_TAIL
    with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
        fh.write(nemo)

    row = {
        "task_payload": {
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
                "initial_setup": None,
                "eval_reward_code": nemo,
            },
        }
    }
    with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2)
        fh.write("\n")

    # ---- replay draft
    on_report = task["start_path"] == task["report_path"]
    on_vars = task["start_path"] == VARS
    nav_report = "" if on_report else nav_to(task["report_path"], "reports")
    nav_vars = "" if on_vars else nav_to(VARS, "system")
    if on_vars:
        nav_vars = ""
    status_steps = ""
    if task["status"]:
        status_steps = (
            '    page.select_option("#sales_report_show_order_statuses", "1")\n'
            '    page.select_option("#sales_report_order_statuses", %r)\n' % task["status"]
        )
    statusline = ""
    if task["status"]:
        statusline = ", Order Status Specified = %s" % ", ".join(task["status"])
    if on_vars:
        # start on Custom Variables: go to the report, then come back.
        nav_report = nav_to(task["report_path"], "reports")
        nav_vars = nav_to(VARS, "system")
    replay = REPLAY.format(
        tid=tid, instruction=task["instruction"], title=task["report_title"],
        dfrom=task["date_from"], dto=task["date_to"], period=task["period"],
        statusline=statusline, rendered=task["rendered"], cell=task["cell"],
        value=task["value"], margin=task["margin"], code=task["code"],
        name=task["name"], start_path=task["start_path"],
        nav_report=nav_report, nav_vars=nav_vars, status_steps=status_steps,
    )
    with open(os.path.join(LANE, "replays", "%s.py" % tid), "w") as fh:
        fh.write(replay)

    return row


def main():
    os.makedirs(os.path.join(LANE, "replays"), exist_ok=True)
    rows = [build(t) for t in TASKS]
    with open(os.path.join(LANE, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    with open(os.path.join(LANE, "index.json"), "w") as fh:
        json.dump({
            "schema_version": 2,
            "tasks": [{"task_id": t["id"], "path": "../../%s/task.json" % t["id"]} for t in TASKS],
        }, fh, indent=2)
        fh.write("\n")
    for t in TASKS:
        words = len(t["instruction"].split())
        print("%-64s %-8s %-3d words  start=%s  value=%r" % (
            t["id"], t["style"], words, t["start_path"], t["value"]))


if __name__ == "__main__":
    main()
