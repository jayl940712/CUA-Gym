import json, os, textwrap

ROOT = "/home/ubuntu/CUA-Gym/output/tasks/shopping_admin"
BATCH = os.path.join(ROOT, "_batches", "shipping_revenue_ledger")
REPLAYS = os.path.join(BATCH, "replays")
APP = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

AN_SHIP = "Show the shipping report from August 5, 2022 to March 1, 2023."
AN_ORD = "Show the orders report from May 1, 2021 to March 31, 2022."
AN_LAST_YEAR = "Show the sales order report for for last year (today is March 15, 2023)."
AN_THIS_YEAR = "Show the tax report for for this year (today is March 15, 2023)."
AN_Q1 = "Show the refund report for for Q1 (today is March 15, 2023)."
AN_MONTHS = "Show the sales order report for for last months (today is March 15, 2023)."
AN_45 = "Show the sales order report for over the last 45 days (today is March 15, 2023)."

LIMITATION = (
    "Acknowledged indirect-grading limitation (docs/SKILL_TAXONOMY.md): the report "
    "configuration skill is exercised but graded through the written figure, so an "
    "agent that reaches the same number by another route still scores 1.0. Mitigated "
    "because the figure is a SUM over the store_id=0 slice of "
    "reportAggregatesOrder.json shipping_aggregated_order (258 rows in scope, 516 in "
    "the file) and the Shipping Report is the only surface in the mock that renders it."
)

TASKS = [
    dict(
        num="001", slug="last_year_total", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="compute last calendar year from a stated today -> configure the Shipping Report over that window -> transfer the Total Sales Shipping total into a new custom variable",
        analogues=[AN_SHIP, AN_LAST_YEAR],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Our shipping costs for last year need logging (today is 9 January 2023). "
            "Create a custom variable with code shipping_revenue_last_year, name "
            "Shipping Revenue Last Year, and the year's Total Sales Shipping as its "
            "plain value."
        ),
        window="1/1/2022 to 12/31/2022, Order Status left at Any",
        figures="Total Sales Shipping = $3,145.00 (215 orders)",
        expected=[dict(code="shipping_revenue_last_year", name="Shipping Revenue Last Year",
                       fields={"plain_value": 3145.0})],
        weights=[("last_year_variable_created", 0.3), ("last_year_shipping_total_recorded", 0.7)],
        notes="R2 is a genuine step: the instruction names no dates, only 'last year' plus a stated today.",
    ),
    dict(
        num="002", slug="last_year_orders_and_total", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="compute last calendar year from a stated today -> configure the Shipping Report -> transfer BOTH totals-row measures into one new custom variable",
        analogues=[AN_SHIP, AN_LAST_YEAR],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Today is 4 January 2024. Log last year's shipping figures in a new custom "
            "variable: code shipping_last_year_summary, name Shipping Last Year Summary, "
            "the order count as the plain value and Total Sales Shipping as the HTML value."
        ),
        window="1/1/2023 to 12/31/2023, Order Status left at Any",
        figures="Orders = 85, Total Sales Shipping = $1,270.00",
        expected=[dict(code="shipping_last_year_summary", name="Shipping Last Year Summary",
                       fields={"plain_value": 85.0, "html_value": 1270.0})],
        weights=[("summary_variable_created", 0.25), ("last_year_figures_recorded", 0.75)],
        notes="Two measures from one totals row land in two different form fields.",
    ),
    dict(
        num="003", slug="first_quarter_orders", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="expand 'first quarter of 2023' into a date window -> configure the Shipping Report -> transfer the totals-row order count into a new custom variable",
        analogues=[AN_SHIP, AN_Q1],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Record how many orders the shipping report totals for the first quarter of "
            "2023 in a new custom variable, code shipping_orders_2023_q1, name Shipping "
            "Orders 2023 Q1, with the count as its plain value."
        ),
        window="1/1/2023 to 3/31/2023, Order Status left at Any",
        figures="Orders = 54 (Total Sales Shipping $815.00)",
        expected=[dict(code="shipping_orders_2023_q1", name="Shipping Orders 2023 Q1",
                       fields={"plain_value": 54.0})],
        weights=[("quarter_variable_created", 0.3), ("quarter_order_count_recorded", 0.7)],
        notes="Quarter-boundary arithmetic; the count is the totals row, not the 'records found' line.",
    ),
    dict(
        num="004", slug="half_year_gap", style="explicit", difficulty="hard",
        skills=["R2", "R10", "R3", "A7"],
        skill_chain="expand two half-year windows -> configure and read the Shipping Report twice -> subtract -> transfer the difference into a new custom variable",
        analogues=[AN_SHIP, AN_ORD],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Finance wants to see how much shipping revenue fell away over the back half "
            "of 2022. In the Magento admin open Reports > Sales > Shipping and run the "
            "report twice: once from 1 January 2022 to 30 June 2022, and once from 1 July "
            "2022 to 31 December 2022, leaving Order Status on Any both times. Take the "
            "Total Sales Shipping figure out of each report's totals row. Then go to "
            "System > Other Settings > Custom Variables, add a new variable with Variable "
            "Code shipping_2022_half_gap and Variable Name Shipping 2022 Half Gap, and put "
            "the amount by which the first half exceeded the second into its Variable "
            "Plain Value. Do not create any other custom variable."
        ),
        window="1/1/2022-6/30/2022 then 7/1/2022-12/31/2022, Order Status Any",
        figures="H1 $1,795.00 minus H2 $1,350.00 = $445.00",
        expected=[dict(code="shipping_2022_half_gap", name="Shipping 2022 Half Gap",
                       fields={"plain_value": 445.0})],
        weights=[("gap_variable_created", 0.3), ("half_year_gap_recorded", 0.7)],
        notes="R3 is real here: the agent sums/subtracts across two report runs; no single window renders 445.",
    ),
    dict(
        num="005", slug="completed_only_2022", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="expand 'last year' style calendar window -> configure the Shipping Report with Order Status Specified = Complete -> transfer the total into a new custom variable",
        analogues=[AN_SHIP, AN_THIS_YEAR],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Only orders in the Complete status count for the 2022 carrier reconciliation. "
            "Record their "
            "Total Sales Shipping from the shipping report in a new custom variable: code "
            "shipping_complete_2022, name Shipping Complete 2022, figure as the plain value."
        ),
        window="1/1/2022 to 12/31/2022, Order Status = Specified, statuses = Complete",
        figures="Total Sales Shipping = $1,740.00 (115 orders); the unfiltered figure is $3,145.00",
        expected=[dict(code="shipping_complete_2022", name="Shipping Complete 2022",
                       fields={"plain_value": 1740.0})],
        weights=[("complete_variable_created", 0.3), ("completed_shipping_total_recorded", 0.7)],
        notes="Exercises the two-control status filter (show_order_statuses=Specified plus the multiselect). The unfiltered 2022 figure differs, so a skipped filter scores 0.",
    ),
    dict(
        num="006", slug="net_of_cancellations", style="explicit", difficulty="hard",
        skills=["R2", "R10", "R3", "A7"],
        skill_chain="expand the 2022 window -> run the Shipping Report unfiltered and canceled-only -> subtract -> transfer the net figure into a new custom variable",
        analogues=[AN_SHIP, AN_ORD],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Unlike the other sales reports, the Shipping Report applies no canceled-order "
            "exclusion, so its 2022 headline overstates what we actually collected. In the "
            "Magento admin open Reports > Sales > Shipping and work out the 2022 Total "
            "Sales Shipping for orders that were NOT canceled: run 1 January 2022 to 31 "
            "December 2022 with Order Status on Any, then run the same window with Order "
            "Status set to Specified and Canceled selected, and subtract the second total "
            "from the first. Selecting every specified status except Canceled instead is "
            "equally acceptable and gives the same number. Record that number under System "
            "> Other Settings > Custom Variables as a new variable with Variable Code "
            "shipping_net_2022, Variable Name Shipping Net 2022, and the amount as its "
            "Variable Plain Value. Add no other custom variable."
        ),
        window="1/1/2022-12/31/2022 with Any, then the same window with Specified = Canceled",
        figures="$3,145.00 minus $1,400.00 = $1,745.00 (116 non-canceled orders)",
        expected=[dict(code="shipping_net_2022", name="Shipping Net 2022",
                       fields={"plain_value": 1745.0})],
        weights=[("net_variable_created", 0.3), ("net_shipping_total_recorded", 0.7)],
        notes="Two independent report configurations feed one subtraction; both documented routes yield 1745.00 exactly.",
    ),
    dict(
        num="007", slug="may_window_total", style="terse", difficulty="medium",
        skills=["R10", "A7"],
        skill_chain="configure the Shipping Report over a stated window -> transfer its Total Sales Shipping into a new custom variable",
        analogues=[AN_SHIP, AN_MONTHS],
        hard_criteria=[],
        instruction=(
            "Run the shipping report from 5/1/2022 to 5/31/2022 and save its Total Sales "
            "Shipping in a new custom variable with code shipping_may_2022 and name "
            "Shipping May 2022, as the plain value."
        ),
        window="5/1/2022 to 5/31/2022, Order Status left at Any",
        figures="Total Sales Shipping = $205.00 (15 orders)",
        expected=[dict(code="shipping_may_2022", name="Shipping May 2022",
                       fields={"plain_value": 205.0})],
        weights=[("may_variable_created", 0.3), ("may_shipping_total_recorded", 0.7)],
        notes="Dates are given, so there is no R2 step; two skills, honestly medium.",
    ),
    dict(
        num="008", slug="february_window_orders", style="terse", difficulty="medium",
        skills=["R10", "A7"],
        skill_chain="configure the Shipping Report over a stated window -> transfer its totals-row order count into a new custom variable",
        analogues=[AN_SHIP, AN_45],
        hard_criteria=[],
        instruction=(
            "Run the shipping report from 2/1/2023 to 2/28/2023 and record the number of "
            "orders it totals in a new custom variable, code shipping_feb_2023_orders, "
            "name Shipping Feb 2023 Orders, as the plain value."
        ),
        window="2/1/2023 to 2/28/2023, Order Status left at Any",
        figures="Orders = 17 (Total Sales Shipping $220.00)",
        expected=[dict(code="shipping_feb_2023_orders", name="Shipping Feb 2023 Orders",
                       fields={"plain_value": 17.0})],
        weights=[("february_variable_created", 0.3), ("february_order_count_recorded", 0.7)],
        notes="Dates given; two skills, medium. The totals-row Orders figure is 17 and the interval count is 13 - a 'records found' misread scores 0.",
    ),
    dict(
        num="009", slug="quarterly_ledger_gap", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="read the existing quarterly ledger to see which quarter is missing -> expand Q4 2022 into a date window -> configure the Shipping Report -> append the figure as a new custom variable",
        analogues=[AN_SHIP, AN_Q1],
        hard_criteria=["derived_target", "ordering_dependency", "cross_page"],
        instruction=(
            "Our quarterly shipping ledger is missing its last entry for 2022. Add it as a "
            "new custom variable with code shipping_q4_2022, name Shipping Q4 2022, and "
            "that quarter's Total Sales Shipping as the plain value."
        ),
        window="10/1/2022 to 12/31/2022, Order Status left at Any",
        figures="Total Sales Shipping = $605.00 (39 orders)",
        expected=[dict(code="shipping_q4_2022", name="Shipping Q4 2022",
                       fields={"plain_value": 605.0})],
        preserved=[
            dict(code="shipping_q1_2022", plain_value=900.0),
            dict(code="shipping_q2_2022", plain_value=895.0),
            dict(code="shipping_q3_2022", plain_value=745.0),
        ],
        inject=True,
        weights=[("q4_entry_added", 0.4), ("quarterly_ledger_completed", 0.6)],
        notes="Injection supplies the three earlier quarters, so 'the missing one' is a real read of state rather than a fixed answer, and the sink array is no longer empty (nextId() returns 4).",
    ),
    dict(
        num="010", slug="two_year_revenue_pair", style="terse", difficulty="hard",
        skills=["R2", "R10", "A7"],
        skill_chain="expand two calendar-year windows -> configure and read the Shipping Report twice -> write one custom variable per year",
        analogues=[AN_SHIP, AN_ORD],
        hard_criteria=["multi_entity", "derived_target", "ordering_dependency"],
        instruction=(
            "Set up a two-year shipping revenue record: one custom variable per year, "
            "codes shipping_revenue_2022 and shipping_revenue_2023, names Shipping Revenue "
            "2022 and Shipping Revenue 2023, each carrying that year's Total Sales Shipping "
            "as its plain value."
        ),
        window="1/1/2022-12/31/2022 and 1/1/2023-12/31/2023, Order Status left at Any",
        figures="2022 = $3,145.00, 2023 = $1,270.00",
        expected=[
            dict(code="shipping_revenue_2022", name="Shipping Revenue 2022",
                 fields={"plain_value": 3145.0}),
            dict(code="shipping_revenue_2023", name="Shipping Revenue 2023",
                 fields={"plain_value": 1270.0}),
        ],
        weights=[("both_year_variables_created", 0.3), ("both_year_totals_recorded", 0.7)],
        notes="Two separate records mutated (multi_entity) from two separate report runs.",
    ),
]


def task_id(t):
    return "shipping_revenue_ledger_%s_%s" % (t["slug"], t["num"])


REWARD_BODY = '''
import json
import re

COMPONENT_WEIGHTS = json.loads(r"""__WEIGHTS__""")
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

COMPONENT_DETAILS = json.loads(r"""__DETAILS__""")

EXPECTED = json.loads(r"""__EXPECTED__""")
PRESERVED = json.loads(r"""__PRESERVED__""")

CREATED_KEY = "__CREATED_KEY__"
RECORDED_KEY = "__RECORDED_KEY__"
TOLERANCE = 0.005


def _key(value):
    return re.sub(r"\\s+", " ", str("" if value is None else value)).strip().casefold()


def _number(value):
    """First signed decimal in a rendered figure: $3,145.00 / 3145 / 215 orders."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").replace("$", " ").replace("USD", " ").replace("usd", " ")
    found = re.search(r"-?\\d+(?:\\.\\d+)?", text)
    if not found:
        return None
    try:
        return float(found.group(0))
    except ValueError:
        return None


def _variable_rows(state):
    if not isinstance(state, dict):
        return []
    config = state.get("systemConfig")
    if not isinstance(config, dict):
        return []
    rows = config.get("variables")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _unique_row(rows, code):
    wanted = _key(code)
    hits = [row for row in rows if _key(row.get("code")) == wanted]
    if len(hits) != 1:
        return None
    return hits[0]


def _components(checks):
    components = []
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        ok = bool(checks.get(name))
        value = COMPONENT_WEIGHTS[name] if ok else 0.0
        total += value
        components.append({
            "name": name,
            "score": round(value, 6),
            "details": COMPONENT_DETAILS.get(name, ""),
        })
    return round(total, 6), components


def score_state(state):
    rows = _variable_rows(state)

    created = True
    for spec in EXPECTED:
        row = _unique_row(rows, spec["code"])
        if row is None or _key(row.get("name")) != _key(spec["name"]):
            created = False

    figures_ok = True
    for spec in EXPECTED:
        row = _unique_row(rows, spec["code"])
        if row is None:
            figures_ok = False
            continue
        for field in spec["fields"]:
            got = _number(row.get(field))
            want = float(spec["fields"][field])
            if got is None or abs(got - want) > TOLERANCE:
                figures_ok = False

    preserved_ok = True
    for spec in PRESERVED:
        row = _unique_row(rows, spec["code"])
        if row is None:
            preserved_ok = False
            continue
        got = _number(row.get("plain_value"))
        want = float(spec["plain_value"])
        if got is None or abs(got - want) > TOLERANCE:
            preserved_ok = False

    wanted_codes = sorted([_key(spec["code"]) for spec in EXPECTED]
                          + [_key(spec["code"]) for spec in PRESERVED])
    actual_codes = sorted([_key(row.get("code")) for row in rows])
    collection_ok = actual_codes == wanted_codes

    checks = {
        CREATED_KEY: created,
        RECORDED_KEY: bool(created and figures_ok and preserved_ok and collection_ok),
    }
    return _components(checks)
'''

REWARD_TAIL = '''

def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    apps = apps if isinstance(apps, dict) else {}
    app = apps.get("shopping_admin")
    if not isinstance(app, dict):
        app = apps.get("webarena_shopping_admin_mock")
    if not isinstance(app, dict):
        app = {}
    state = app.get("current_state")
    if not isinstance(state, dict):
        state = {}
    score, components = score_state(state)
    return {"score": score, "components": components}
'''

NEMO_TAIL = '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # a failed read must still print a score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    score, _components = score_state(state)
    print("REWARD: %s" % score)


main()
'''


SETUP_009 = '''"""NeMo-Gym setup program for shipping_revenue_ledger_quarterly_ledger_gap_009.

Seeds a partial quarterly shipping ledger into systemConfig.variables: the three
2022 quarters that were already logged, and nothing for the fourth. The pristine
seed leaves that array empty, so without this injection "the missing entry" would
be a fixed answer the agent could produce without reading anything.

Nothing here pre-satisfies the rubric. The rubric wants a fourth row whose code is
shipping_q4_2022 and whose plain value is the Shipping Report's Q4 2022 Total Sales
Shipping figure; the injected rows are Q1, Q2 and Q3 only.

On this mock a `set` is a TOP-LEVEL shallow merge over createInitialData()
(vite.config.js:372), which means posting systemConfig replaces that object whole
rather than merging into it. So the pristine systemConfig is read back from /go and
re-posted entire with only the variables sub-key changed.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

EXPECTED_TOP_LEVEL_KEYS = 44
EXPECTED_SYSTEM_CONFIG_KEYS = 26

LEDGER = json.loads(r"""[
  {
    "variable_id": 1,
    "code": "shipping_q1_2022",
    "name": "Shipping Q1 2022",
    "html_value": "",
    "plain_value": "900.00"
  },
  {
    "variable_id": 2,
    "code": "shipping_q2_2022",
    "name": "Shipping Q2 2022",
    "html_value": "",
    "plain_value": "895.00"
  },
  {
    "variable_id": 3,
    "code": "shipping_q3_2022",
    "name": "Shipping Q3 2022",
    "html_value": "",
    "plain_value": "745.00"
  }
]""")


def fail(message):
    print("SETUP FAILED: %s" % message, file=sys.stderr)
    raise SystemExit(1)


def read():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    state = read().get("current_state")
    if not isinstance(state, dict):
        fail("GET /go returned no current_state")

    system_config = state.get("systemConfig")
    if not isinstance(system_config, dict):
        fail("systemConfig is missing from the state document")
    if len(system_config) != EXPECTED_SYSTEM_CONFIG_KEYS:
        fail("systemConfig holds %d sub-keys, expected %d"
             % (len(system_config), EXPECTED_SYSTEM_CONFIG_KEYS))
    if system_config.get("variables") != []:
        fail("expected the pristine empty systemConfig.variables array")

    whole = dict(system_config)
    whole["variables"] = LEDGER

    post = requests.post(BASE_URL + "/post?sid=" + SID,
                         json={"action": "set", "state": {"systemConfig": whole}},
                         timeout=60)
    post.raise_for_status()

    after = read()
    if after.get("state_diff") != {}:
        fail("state_diff is not empty after set")
    if after.get("initial_state") != after.get("current_state"):
        fail("initial_state != current_state after set")
    current = after.get("current_state") or {}
    if len(current) != EXPECTED_TOP_LEVEL_KEYS:
        fail("%d top-level keys after set, expected %d"
             % (len(current), EXPECTED_TOP_LEVEL_KEYS))
    written = current.get("systemConfig")
    if not isinstance(written, dict) or len(written) != EXPECTED_SYSTEM_CONFIG_KEYS:
        fail("systemConfig collapsed after set")
    if written.get("variables") != LEDGER:
        fail("systemConfig.variables did not round-trip")
    print("SETUP OK")


main()
'''


def build_reward(t, nemo):
    weights = {name: w for name, w in t["weights"]}
    created_key, recorded_key = t["weights"][0][0], t["weights"][1][0]
    codes = ", ".join(s["code"] for s in t["expected"])
    details = {
        created_key: ("custom variable(s) %s exist exactly once each in "
                      "systemConfig.variables with the requested Variable Name" % codes),
        recorded_key: ("systemConfig.variables is now exactly the expected ledger and every "
                       "requested field carries the Shipping Report figure (%s)" % t["figures"]),
    }
    expected = [dict(code=s["code"], name=s["name"], fields=s["fields"]) for s in t["expected"]]
    preserved = t.get("preserved", [])

    header = '"""%s reward for %s.\n\n%s\n\nRubric: %s\nReads current_state only; nothing is diffed against initial_state.\n\n%s\n"""\n' % (
        "NeMo-Gym" if nemo else "Deterministic offline",
        task_id(t),
        t["skill_chain"],
        "Shipping Report window %s -> %s -> systemConfig.variables" % (t["window"], t["figures"]),
        LIMITATION,
    )
    body = REWARD_BODY
    body = body.replace("__WEIGHTS__", json.dumps(weights, indent=2))
    body = body.replace("__DETAILS__", json.dumps(details, indent=2))
    body = body.replace("__EXPECTED__", json.dumps(expected, indent=2))
    body = body.replace("__PRESERVED__", json.dumps(preserved, indent=2))
    body = body.replace("__CREATED_KEY__", created_key)
    body = body.replace("__RECORDED_KEY__", recorded_key)

    if nemo:
        preamble = '\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n' % URL_PLACEHOLDER
        return header + preamble + body + NEMO_TAIL
    return header + body + REWARD_TAIL


REPLAY_TEMPLATE = '''"""Golden replay draft: {tid}

Click path (no typed URLs after the landing page):
  /  -> dashboard
  left rail "Reports" -> Sales > "Shipping"
  fill #sales_report_from / #sales_report_to{status_note} -> "Show Report"
  read the <tfoot class="totals"> row
  left rail "System" -> Other Settings > "Custom Variables" -> "Add New Variable"
  fill Variable Code / Variable Name / value field(s) -> "Save"

Window(s): {window}
Expected figures: {figures}
"""

import re

from playwright.async_api import expect


async def open_shipping_report(page):
    await page.locator("#menu-reports > a.menu-item").click()
    await page.locator("#menu-reports .submenu").get_by_role(
        "link", name="Shipping", exact=True).click()
    await expect(page.get_by_role("heading", name="Shipping Report")).to_be_visible()


async def run_report(page, date_from, date_to, statuses=None):
    await open_shipping_report(page)
    await page.locator("#sales_report_from").fill(date_from)
    await page.locator("#sales_report_to").fill(date_to)
    if statuses:
        await page.locator("#sales_report_show_order_statuses").select_option("1")
        await page.locator("#sales_report_order_statuses").select_option(statuses)
    await page.locator("#filter_form_submit").click()
    totals = page.locator("#shippingReportGrid_table tfoot tr.totals th")
    await expect(totals.first).to_have_text("Total")
    orders = (await totals.nth(2).inner_text()).strip()
    revenue = (await totals.nth(3).inner_text()).strip()
    return orders, revenue


async def open_new_variable_form(page):
    await page.locator("#menu-system > a.menu-item").click()
    await page.locator("#menu-system .submenu").get_by_role(
        "link", name="Custom Variables", exact=True).click()
    await expect(page.get_by_role("heading", name="Custom Variables")).to_be_visible()
    await page.get_by_role("button", name="Add New Variable").click()
    await expect(page.get_by_role("heading", name="New Custom Variable")).to_be_visible()


async def save_variable(page, code, name, plain_value=None, html_value=None):
    await page.get_by_label("Variable Code").fill(code)
    await page.get_by_label("Variable Name").fill(name)
    if html_value is not None:
        await page.get_by_label("Variable HTML Value").fill(html_value)
    if plain_value is not None:
        await page.get_by_label("Variable Plain Value").fill(plain_value)
    await page.get_by_role("button", name="Save", exact=True).click()
    await expect(page.get_by_role("heading", name="Custom Variables")).to_be_visible()
    await expect(page.get_by_text(code, exact=False).first).to_be_visible()


async def run(lane, task):
    page = lane.page("shopping_admin")
    await expect(page).to_have_url(re.compile(r"/admin/admin/dashboard"))

{steps}
'''


def replay_steps(t):
    num = t["num"]
    if num == "001":
        return ('    orders, revenue = await run_report(page, "1/1/2022", "12/31/2022")\n'
                '    assert revenue == "$3,145.00", revenue\n'
                '    assert orders == "215", orders\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_revenue_last_year",\n'
                '                        "Shipping Revenue Last Year", plain_value=revenue)\n')
    if num == "002":
        return ('    orders, revenue = await run_report(page, "1/1/2023", "12/31/2023")\n'
                '    assert orders == "85", orders\n'
                '    assert revenue == "$1,270.00", revenue\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_last_year_summary",\n'
                '                        "Shipping Last Year Summary",\n'
                '                        plain_value=orders, html_value=revenue)\n')
    if num == "003":
        return ('    orders, revenue = await run_report(page, "1/1/2023", "3/31/2023")\n'
                '    assert orders == "54", orders\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_orders_2023_q1",\n'
                '                        "Shipping Orders 2023 Q1", plain_value=orders)\n')
    if num == "004":
        return ('    _, first_half = await run_report(page, "1/1/2022", "6/30/2022")\n'
                '    assert first_half == "$1,795.00", first_half\n'
                '    _, second_half = await run_report(page, "7/1/2022", "12/31/2022")\n'
                '    assert second_half == "$1,350.00", second_half\n\n'
                '    gap = money(first_half) - money(second_half)\n'
                '    assert abs(gap - 445.0) < 0.005, gap\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_2022_half_gap",\n'
                '                        "Shipping 2022 Half Gap",\n'
                '                        plain_value="%.2f" % gap)\n')
    if num == "005":
        return ('    orders, revenue = await run_report(page, "1/1/2022", "12/31/2022",\n'
                '                                       statuses=["complete"])\n'
                '    assert revenue == "$1,740.00", revenue\n'
                '    assert orders == "115", orders\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_complete_2022",\n'
                '                        "Shipping Complete 2022", plain_value=revenue)\n')
    if num == "006":
        return ('    _, gross = await run_report(page, "1/1/2022", "12/31/2022")\n'
                '    assert gross == "$3,145.00", gross\n'
                '    _, canceled = await run_report(page, "1/1/2022", "12/31/2022",\n'
                '                                   statuses=["canceled"])\n'
                '    assert canceled == "$1,400.00", canceled\n\n'
                '    net = money(gross) - money(canceled)\n'
                '    assert abs(net - 1745.0) < 0.005, net\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_net_2022", "Shipping Net 2022",\n'
                '                        plain_value="%.2f" % net)\n')
    if num == "007":
        return ('    orders, revenue = await run_report(page, "5/1/2022", "5/31/2022")\n'
                '    assert revenue == "$205.00", revenue\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_may_2022", "Shipping May 2022",\n'
                '                        plain_value=revenue)\n')
    if num == "008":
        return ('    orders, revenue = await run_report(page, "2/1/2023", "2/28/2023")\n'
                '    assert orders == "17", orders\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_feb_2023_orders",\n'
                '                        "Shipping Feb 2023 Orders", plain_value=orders)\n')
    if num == "009":
        return ('    # The injected ledger already carries Q1-Q3 2022; Q4 is the gap.\n'
                '    orders, revenue = await run_report(page, "10/1/2022", "12/31/2022")\n'
                '    assert revenue == "$605.00", revenue\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_q4_2022", "Shipping Q4 2022",\n'
                '                        plain_value="%.2f" % money(revenue))\n')
    if num == "010":
        return ('    _, revenue_2022 = await run_report(page, "1/1/2022", "12/31/2022")\n'
                '    assert revenue_2022 == "$3,145.00", revenue_2022\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_revenue_2022",\n'
                '                        "Shipping Revenue 2022", plain_value=revenue_2022)\n\n'
                '    _, revenue_2023 = await run_report(page, "1/1/2023", "12/31/2023")\n'
                '    assert revenue_2023 == "$1,270.00", revenue_2023\n\n'
                '    await open_new_variable_form(page)\n'
                '    await save_variable(page, "shipping_revenue_2023",\n'
                '                        "Shipping Revenue 2023", plain_value=revenue_2023)\n')
    raise AssertionError(t["num"])


MONEY_HELPER = '''

def money(text):
    """'$3,145.00' -> 3145.0"""
    return float(str(text).replace("$", "").replace(",", "").strip())
'''


def success_criteria(t):
    out = []
    for spec in t["expected"]:
        fields = ", ".join(
            "%s reads %s" % (field, ("%.2f" % spec["fields"][field]).rstrip("0").rstrip(".")
                             if field != "plain_value" or spec["fields"][field] % 1
                             else "%g" % spec["fields"][field])
            for field in spec["fields"])
        out.append("systemConfig.variables holds exactly one row with code '%s', name '%s', and %s."
                   % (spec["code"], spec["name"], fields))
    codes = [s["code"] for s in t["expected"]] + [s["code"] for s in t.get("preserved", [])]
    out.append("systemConfig.variables is exactly the set of codes %s - no extra and no missing row."
               % ", ".join("'%s'" % c for c in codes))
    for spec in t.get("preserved", []):
        out.append("The pre-existing ledger row '%s' still reads %g." % (spec["code"], spec["plain_value"]))
    return out


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    nemo_rows = []

    for t in TASKS:
        tid = task_id(t)
        d = os.path.join(ROOT, tid)
        os.makedirs(d, exist_ok=True)

        instruction = " ".join(t["instruction"].split())

        with open(os.path.join(d, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": tid,
                "task_instruction": instruction,
                "app_dir": APP,
                "start_path": "/",
                "difficulty": t["difficulty"],
                "success_criteria": success_criteria(t),
            }, fh, indent=2)
            fh.write("\n")

        metadata = {
            "style": t["style"],
            "difficulty": t["difficulty"],
            "shape": "retrieval_writeback",
            "skills": t["skills"],
            "skill_chain": t["skill_chain"],
            "official_analogues": t["analogues"],
            "hard_criteria": t["hard_criteria"],
            "topic": "shipping_revenue_ledger",
            "batch": "batch5_lane49",
            "lane": "shipping_revenue_ledger",
            "inspiration_ids": ["webarena-710", "webarena-707", "webarena-709", "webarena-706"],
            "report_window": t["window"],
            "derived_figures": t["figures"],
            "graded_limitation": LIMITATION,
            "authoring_notes": t["notes"],
        }
        if t.get("inject"):
            metadata["injected_preconditions"] = [
                "systemConfig.variables seeded with three custom variables - "
                "shipping_q1_2022 (900.00), shipping_q2_2022 (895.00), shipping_q3_2022 (745.00) - "
                "the 2022 quarterly shipping ledger with its fourth quarter missing. "
                "The pristine seed leaves the array empty (src/data/systemConfig.json:115)."
            ]
            metadata["injected_precondition"] = metadata["injected_preconditions"][0]
            metadata["branch_unlocked"] = (
                "useSystemCollection('variables','variable_id').add over a NON-empty "
                "collection (components/system/RecordForm.jsx:36-37): nextId() returns 4 "
                "rather than 1, and the Custom Variables grid renders real rows the agent "
                "must read to see which quarter is missing."
            )

        with open(os.path.join(d, "task.json"), "w") as fh:
            json.dump({
                "schema_version": 2,
                "task_id": tid,
                "instruction": instruction,
                "apps": [{
                    "name": APP,
                    "source_name": "shopping_admin",
                    "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
                    "start_path": "/",
                    "initial_state": None,
                    "golden_state": None,
                }],
                "evidence": [],
                "reward_path": "reward.py",
                "requirements_path": None,
                "source": "webarena",
                "source_evaluator": {},
                "metadata": metadata,
            }, fh, indent=2)
            fh.write("\n")

        reward = build_reward(t, nemo=False)
        nemo_reward = build_reward(t, nemo=True)
        with open(os.path.join(d, "reward.py"), "w") as fh:
            fh.write(reward)
        with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward)

        setup = None
        if t.get("inject"):
            setup = SETUP_009
            with open(os.path.join(d, "initial_setup.py"), "w") as fh:
                fh.write(setup)

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": instruction,
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
        with open(os.path.join(d, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        nemo_rows.append(row)

        steps = replay_steps(t)
        replay = REPLAY_TEMPLATE.format(
            tid=tid, window=t["window"], figures=t["figures"],
            status_note=(" / #sales_report_show_order_statuses + #sales_report_order_statuses"
                         if t["num"] in ("005", "006") else ""),
            steps=steps)
        if "money(" in steps:
            replay = replay.replace("\nasync def open_shipping_report", MONEY_HELPER + "\nasync def open_shipping_report")
        with open(os.path.join(REPLAYS, tid + ".py"), "w") as fh:
            fh.write(replay)

        index["tasks"].append({"task_id": tid, "path": "../../%s/task.json" % tid})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
