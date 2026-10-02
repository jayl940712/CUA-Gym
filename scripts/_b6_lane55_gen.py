#!/usr/bin/env python3
"""Batch-6 lane 55 generator — shopping_admin, R1 -> A5.

Chain: read the Bestsellers report for a stated window, take its single
rank-1 product, and apply a stated arithmetic change to that product's
catalog price.

Everything the bundles assert is derived here, at authoring time, from the
frozen mock sources:

  hub/websites/webarena_shopping_admin_mock/src/components/reports/bestsellersAggregates.json
  hub/websites/webarena_shopping_admin_mock/src/data/products.json

`bestsellers_rows()` below is a line-for-line port of
`src/components/reports/reportUtils.js:213-320` (`bestsellersRows`), so the
five rows recorded in each bundle are the rows the page renders.

Run:  python3 scripts/_b6_lane55_gen.py
"""

import datetime
import json
import os
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK = os.path.join(ROOT, "hub/websites/webarena_shopping_admin_mock")
OUT_TASKS = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH_DIR = os.path.join(OUT_TASKS, "_batches/bestseller_price_bump")

AGG = json.load(open(os.path.join(MOCK, "src/components/reports/bestsellersAggregates.json")))
PRODUCTS = {p["entity_id"]: p for p in json.load(open(os.path.join(MOCK, "src/data/products.json")))}

APP_DIR = "webarena_shopping_admin_mock"
APP_URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"
REPORT_PATH = "/admin/reports/report_sales/bestsellers/"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# --------------------------------------------------------------- report port

def _scope(rows, store_id=1):
    return [r for r in rows if int(r["store_id"]) == int(store_id)]


def _d(text):
    return datetime.date(*map(int, text.split("-")))


def _period_key(period, period_type):
    s = str(period)[:10]
    if period_type == "year":
        return s[:4] + "-01-01"
    if period_type == "month":
        return s[:7] + "-01"
    return s


def _period_label(key, period_type):
    y, m, d = map(int, key.split("-"))
    if period_type == "year":
        return str(y)
    if period_type == "month":
        return "%d/%d" % (m, y)
    return "%s %d, %d" % (MONTHS[m - 1], d, y)


def _last_day(y, m):
    return (datetime.date(y + (m == 12), (m % 12) + 1, 1) - datetime.timedelta(days=1)).day


def _collect(rows, label):
    by = {}
    for r in rows:
        pid = r["product_id"]
        if pid in by:
            by[pid]["qty_ordered"] += float(r["qty_ordered"] or 0)
        else:
            by[pid] = {
                "__period": label(r), "product_id": pid, "product_name": r["product_name"],
                "product_price": r["product_price"], "qty_ordered": float(r["qty_ordered"] or 0),
            }
    return list(by.values())


def bestsellers_rows(period_type, frm, to, store_id=1, limit=5):
    """Port of reportUtils.js:213 bestsellersRows."""
    daily = _scope(AGG["bestsellers_daily"], store_id)
    table = "bestsellers_" + ("yearly" if period_type == "year" else "monthly" if period_type == "month" else "daily")
    main = _scope(AGG.get(table, []), store_id)

    def in_range(period, f, t):
        p = str(period)[:10]
        if f and p < f.isoformat():
            return False
        if t and p > t.isoformat():
            return False
        return True

    def boundary(bf, bt):
        rows = [r for r in daily if in_range(r["period"], bf, bt)]
        label = _period_key(bf.isoformat(), period_type)
        out = _collect(rows, lambda r: label)
        out.sort(key=lambda x: (-x["qty_ordered"], x["product_id"]))
        return out[:limit]

    unions = []
    main_from, main_to, main_disabled = frm, to, False
    if period_type == "year":
        if frm and (frm.month != 1 or frm.day != 1):
            dt_to = datetime.date(frm.year, 12, 31)
            if (not to) or dt_to < to:
                unions.append(boundary(frm, dt_to))
                main_from = datetime.date(frm.year + 1, 1, 1)
        if to and (to.month != 12 or to.day != 31):
            dt_from = datetime.date(to.year, 1, 1)
            if (not frm) or dt_from > frm:
                unions.append(boundary(dt_from, to))
                main_to = datetime.date(to.year - 1, 12, 31)
        if frm and to and frm.year == to.year:
            unions.append(boundary(frm, to))
            main_disabled = True
    elif period_type == "month":
        if frm and frm.day != 1:
            dt_to = datetime.date(frm.year, frm.month, _last_day(frm.year, frm.month))
            if (not to) or dt_to < to:
                unions.append(boundary(frm, dt_to))
                main_from = datetime.date(frm.year + (frm.month == 12), (frm.month % 12) + 1, 1)
        if to and to.day != _last_day(to.year, to.month):
            dt_from = datetime.date(to.year, to.month, 1)
            if (not frm) or dt_from > frm:
                unions.append(boundary(dt_from, to))
                main_to = datetime.date(to.year, to.month, 1) - datetime.timedelta(days=1)
        if frm and to and frm.year == to.year and frm.month == to.month:
            unions.append(boundary(frm, to))
            main_disabled = True

    out = []
    if not main_disabled:
        rows = [r for r in main if float(r["rating_pos"]) <= limit and in_range(r["period"], main_from, main_to)]
        by_period = {}
        for r in rows:
            by_period.setdefault(_period_key(r["period"], period_type), []).append(r)
        for key, group in by_period.items():
            out += _collect(group, lambda r, k=key: k)
    for u in unions:
        out += u
    out.sort(key=lambda a: (a["__period"], -a["qty_ordered"], a["product_id"]))
    return out


def decode_entities(text):
    return (text.replace("&trade;", "™").replace("&reg;", "®")
                .replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'"))


def us(text):
    """'2022-01-01' -> '1/1/2022' — the M/D/YYYY the DateInput parses."""
    y, m, d = map(int, text.split("-"))
    return "%d/%d/%d" % (m, d, y)


# ------------------------------------------------------------------ the lane

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def expected_price(seed, mode, delta):
    seed = Decimal(seed)
    if mode == "pct":
        raw = seed * (Decimal(1) + Decimal(delta) / Decimal(100))
    else:
        raw = seed + Decimal(delta)
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


SPEC = [
    {
        "n": 1, "slug": "year_2022_leader_up_23pct", "pid": 20,
        "period": "year", "from": "2022-01-01", "to": "2022-12-31",
        "mode": "pct", "delta": "23", "style": "terse", "start": "/",
        "shape": "retrieval_writeback",
        "derived_from": "promote_the_bestseller_2022_badge_units_001",
        "instruction": ("2022's best-selling product has been underpriced all year. "
                        "Raise its catalog price by 23%, rounding half up to the nearest cent."),
        "window_words": "the calendar year 2022",
        "period_stated": False,
    },
    {
        "n": 2, "slug": "year_2023_leader_cut_5_dollars", "pid": 33,
        "period": "year", "from": "2023-01-01", "to": "2023-12-31",
        "mode": "abs", "delta": "-5.00", "style": "terse", "start": "/",
        "shape": "mutation",
        "derived_from": "promote_the_bestseller_2023_named_leader_002",
        "instruction": ("Whatever sold the most units in 2023 is now overpriced against a "
                        "competitor. Cut exactly $5.00 off its catalog price."),
        "window_words": "the calendar year 2023",
        "period_stated": False,
    },
    {
        "n": 3, "slug": "april_2022_leader_up_12_5pct", "pid": 1046,
        "period": "month", "from": "2022-04-01", "to": "2022-04-30",
        "mode": "pct", "delta": "12.5", "style": "terse", "start": "/",
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": ("April 2022's best-selling product is due a rise. Increase its catalog "
                        "price by 12.5%, rounding half up to the nearest cent."),
        "window_words": "April 2022",
        "period_stated": False,
    },
    {
        "n": 4, "slug": "july_2022_leader_cut_15pct", "pid": 35,
        "period": "month", "from": "2022-07-01", "to": "2022-07-31",
        "mode": "pct", "delta": "-15", "style": "terse", "start": "/",
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": ("Put July 2022's top seller on a permanent markdown: reduce its catalog "
                        "price by 15%, rounding half up to the nearest cent."),
        "window_words": "July 2022",
        "period_stated": False,
    },
    {
        "n": 5, "slug": "jan_feb_2022_window_up_7_50", "pid": 40,
        "period": "year", "from": "2022-01-01", "to": "2022-02-28",
        "mode": "abs", "delta": "7.50", "style": "terse", "start": "/",
        "shape": "mutation",
        "derived_from": None,
        "instruction": ("Run Bestsellers over 1/1/2022 to 2/28/2022 with Period set to Year. "
                        "The product leading that interval is underpriced - add $7.50 to its "
                        "catalog price."),
        "window_words": "1/1/2022 to 2/28/2022 at Period Year",
        "period_stated": True,
    },
    {
        "n": 6, "slug": "autumn_2022_window_up_8pct", "pid": 18,
        "period": "year", "from": "2022-10-01", "to": "2022-11-30",
        "mode": "pct", "delta": "8", "style": "terse", "start": "/",
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": ("Check Bestsellers for 10/1/2022 through 11/30/2022 at Period Year. "
                        "Raise the leading product's catalog price by 8%, rounding half up to "
                        "the nearest cent."),
        "window_words": "10/1/2022 through 11/30/2022 at Period Year",
        "period_stated": True,
    },
    {
        "n": 7, "slug": "early_2023_to_apr15_up_7_5pct", "pid": 13,
        "period": "year", "from": "2023-01-01", "to": "2023-04-15",
        "mode": "pct", "delta": "7.5", "style": "explicit", "start": REPORT_PATH,
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": (
            "We are repricing this year's early winner. On the Bestsellers report set Period "
            "to Year, From to 1/1/2023 and To to 4/15/2023, then press Show Report: that "
            "single 2023 interval ranks products by order quantity. Take the product in the "
            "top row and increase its catalog price by 7.5%, rounded half up to the nearest "
            "cent. The other four ranked products keep the prices they have now."),
        "window_words": "1/1/2023 to 4/15/2023 at Period Year",
        "period_stated": True,
    },
    {
        "n": 8, "slug": "late_spring_2022_window_up_35pct", "pid": 23,
        "period": "year", "from": "2022-05-01", "to": "2022-06-15",
        "mode": "pct", "delta": "35", "style": "terse", "start": "/",
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": ("Between 5/1/2022 and 6/15/2022 one product outsold everything else "
                        "(Bestsellers, Period Year). Mark its catalog price up 35%, rounding "
                        "half up to the nearest cent."),
        "window_words": "5/1/2022 to 6/15/2022 at Period Year",
        "period_stated": True,
    },
    {
        "n": 9, "slug": "mid_jan_to_mar_2023_cut_3_25", "pid": 926,
        "period": "year", "from": "2023-01-15", "to": "2023-03-31",
        "mode": "abs", "delta": "-3.25", "style": "explicit", "start": REPORT_PATH,
        "shape": "mutation",
        "derived_from": None,
        "instruction": (
            "The buying team wants a small rebate on our strongest line of the late-winter "
            "push. On the Bestsellers report set Period to Year, From to 1/15/2023 and To to "
            "3/31/2023 and press Show Report; the interval that comes back is ranked by order "
            "quantity. Take exactly $3.25 off the catalog price of the product in the top row, "
            "and leave the other four ranked products priced as they are."),
        "window_words": "1/15/2023 to 3/31/2023 at Period Year",
        "period_stated": True,
    },
    {
        "n": 10, "slug": "feb_mar_2022_window_cut_12_5pct", "pid": 34,
        "period": "year", "from": "2022-02-06", "to": "2022-03-06",
        "mode": "pct", "delta": "-12.5", "style": "explicit", "start": REPORT_PATH,
        "shape": "retrieval_writeback",
        "derived_from": None,
        "instruction": (
            "Our February promo ran from 2/6/2022 to 3/6/2022 and one product carried it. On "
            "the Bestsellers report set Period to Year, From to 2/6/2022 and To to 3/6/2022 "
            "and press Show Report to see that window ranked by order quantity. Reduce the "
            "catalog price of the top-ranked product by 12.5%, rounded half up to the nearest "
            "cent. The four products below it keep their current prices."),
        "window_words": "2/6/2022 to 3/6/2022 at Period Year",
        "period_stated": True,
    },
]


def build(spec):
    rows = bestsellers_rows(spec["period"], _d(spec["from"]), _d(spec["to"]))
    intervals = sorted({r["__period"] for r in rows})
    assert len(intervals) == 1, (spec["slug"], intervals)
    assert len(rows) >= 2, spec["slug"]
    top = rows[0]
    assert top["product_id"] == spec["pid"], (spec["slug"], top["product_id"])
    margin = top["qty_ordered"] - rows[1]["qty_ordered"]
    assert margin >= 1, (spec["slug"], margin)

    target = PRODUCTS[spec["pid"]]
    assert target["type_id"] == "simple", spec["slug"]
    assert target.get("special_price") in (None, ""), spec["slug"]
    seed = money(target["price"])
    new_price = expected_price(seed, spec["mode"], spec["delta"])
    assert new_price != seed, spec["slug"]

    scope = []
    for r in rows[1:]:
        p = PRODUCTS[r["product_id"]]
        scope.append({
            "id": int(r["product_id"]),
            "sku": p["sku"],
            "name": decode_entities(p["name"]),
            "price": float(p["price"]),
        })

    return {
        "task_id": "bestseller_price_bump_%s_%03d" % (spec["slug"], spec["n"]),
        "spec": spec,
        "rows": rows,
        "interval_label": _period_label(intervals[0], spec["period"]),
        "margin": margin,
        "target": {
            "id": int(spec["pid"]),
            "sku": target["sku"],
            "name": decode_entities(target["name"]),
            "seed_price": str(seed),
            "expected_price": str(new_price),
            "qty": top["qty_ordered"],
        },
        "runner_up": {
            "id": int(rows[1]["product_id"]),
            "name": decode_entities(rows[1]["product_name"]),
            "qty": rows[1]["qty_ordered"],
        },
        "scope": scope,
    }


# --------------------------------------------------------------- file bodies

def expected_block(task):
    return json.dumps({
        "target_id": task["target"]["id"],
        "target_sku": task["target"]["sku"],
        "target_name": task["target"]["name"],
        "seed_price": task["target"]["seed_price"],
        "mode": task["spec"]["mode"],
        "delta": task["spec"]["delta"],
        "expected_price": task["target"]["expected_price"],
        "scope": task["scope"],
    }, indent=2)


RUBRIC = '''
COMPONENT_WEIGHTS = {
    "bestseller_catalog_price_is_the_derived_value": 1.0,
}


def _expected_price():
    """The instruction's arithmetic, applied with the instruction's rounding
    rule: nearest cent, half up. Decimal, never float."""
    seed = Decimal(EXPECTED["seed_price"])
    if EXPECTED["mode"] == "pct":
        raw = seed * (Decimal(1) + Decimal(EXPECTED["delta"]) / Decimal(100))
    else:
        raw = seed + Decimal(EXPECTED["delta"])
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _num(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "").replace("$", "")
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _overrides(state):
    overrides = state.get("productOverrides")
    if isinstance(overrides, dict):
        return overrides
    return {}


def _deleted(state):
    removed = state.get("deletedProductIds")
    out = set()
    if isinstance(removed, list):
        for value in removed:
            number = _num(value)
            if number is not None:
                out.add(int(number))
    return out


def _effective_price(state, entity_id, seed_price):
    patch = _overrides(state).get(str(entity_id))
    if isinstance(patch, dict) and "price" in patch:
        return _num(patch.get("price"))
    return float(seed_price)


def _checks(state):
    target_id = int(EXPECTED["target_id"])
    removed = _deleted(state)

    # Gate: the report's other four ranked rows still carry the prices they
    # had, and none of the five rows was deleted. Never a paid component.
    scope_ok = target_id not in removed
    for row in EXPECTED["scope"]:
        if not scope_ok:
            break
        if int(row["id"]) in removed:
            scope_ok = False
            break
        now = _effective_price(state, row["id"], row["price"])
        if now is None or abs(now - float(row["price"])) > 1e-6:
            scope_ok = False
            break

    wanted = _expected_price()
    actual = _effective_price(state, target_id, EXPECTED["seed_price"])
    price_ok = False
    if actual is not None:
        price_ok = abs(Decimal(repr(actual)) - wanted) <= Decimal("0.0001")

    return {
        "bestseller_catalog_price_is_the_derived_value": bool(scope_ok and price_ok),
    }
'''


def reward_py(task):
    t = task["target"]
    return '''"""Deterministic reward for %(task_id)s.

Success criteria:
  * the catalog price of product %(pid)d (%(sku)s, "%(name)s") -
    the single rank-1 row of the Bestsellers report for %(window)s -
    now resolves to $%(new)s, which is $%(seed)s %(op)s, rounded
    half up to the nearest cent
  * the other four products ranked in that same interval still resolve to the
    prices they held, which GATES the scored component rather than paying for
    restraint

Only user-visible persisted state is inspected, and only `current_state`.
Ground truth is fixed by the frozen product corpus and the frozen bestsellers
aggregates of webarena_shopping_admin_mock in ./hub/.
"""

import json
from decimal import Decimal, ROUND_HALF_UP

EXPECTED = json.loads(r"""
%(expected)s
""")

%(rubric)s

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
''' % {
        "task_id": task["task_id"],
        "pid": t["id"], "sku": t["sku"], "name": t["name"],
        "window": task["spec"]["window_words"],
        "new": t["expected_price"], "seed": t["seed_price"],
        "op": op_words(task["spec"]),
        "expected": expected_block(task),
        "rubric": RUBRIC,
    }


def nemo_reward_py(task):
    t = task["target"]
    return '''"""NeMo-Gym reward program for %(task_id)s.

Implements exactly the rubric of reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys
from decimal import Decimal, ROUND_HALF_UP

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(placeholder)s"

EXPECTED = json.loads(r"""
%(expected)s
""")

%(rubric)s

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
        payload = response.json()
        state = payload.get("current_state") or {}
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:
        print("reward read failed: %%s" %% exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        value = score_state(state)
    except Exception as exc:
        print("reward scoring failed: %%s" %% exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %%s" %% value)


main()
''' % {
        "task_id": task["task_id"],
        "placeholder": APP_URL_PLACEHOLDER,
        "expected": expected_block(task),
        "rubric": RUBRIC,
    }


def op_words(spec):
    delta = Decimal(spec["delta"])
    if spec["mode"] == "pct":
        verb = "raised by" if delta > 0 else "reduced by"
        return "%s %s%%" % (verb, abs(delta).normalize())
    verb = "plus" if delta > 0 else "minus"
    return "%s $%s" % (verb, abs(delta).quantize(Decimal("0.01")))


def instruction_json(task):
    spec, t = task["spec"], task["target"]
    return {
        "task_id": task["task_id"],
        "task_instruction": spec["instruction"],
        "app_dir": APP_DIR,
        "start_path": spec["start"],
        "difficulty": "medium",
        "success_criteria": [
            ('product %d (%s, "%s") - the single rank-1 row of the Bestsellers report '
             'for %s, at order quantity %g against %g for the runner-up - resolves to '
             'catalog price $%s' % (t["id"], t["sku"], t["name"], spec["window_words"],
                                    t["qty"], task["runner_up"]["qty"], t["expected_price"])),
            ("$%s is $%s %s, rounded half up to the nearest cent"
             % (t["expected_price"], t["seed_price"], op_words(spec))),
            ("the other four products ranked in that interval (%s) still resolve to their "
             "current catalog prices; this GATES the scored component, so a sweep across the "
             "ranked list scores 0.0 rather than a docked partial"
             % ", ".join("%d %s" % (r["id"], r["sku"]) for r in task["scope"])),
        ],
    }


def task_json(task):
    spec, t = task["spec"], task["target"]
    rows_note = "; ".join(
        "%s %s qty %g" % (decode_entities(r["product_name"]), r["product_id"], r["qty_ordered"])
        for r in task["rows"])
    return {
        "schema_version": 2,
        "task_id": task["task_id"],
        "instruction": spec["instruction"],
        "apps": [{
            "name": APP_DIR,
            "source_name": "shopping_admin",
            "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
            "start_path": spec["start"],
            "initial_state": None,
            "golden_state": None,
        }],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": {
            "style": spec["style"],
            "difficulty": "medium",
            "shape": spec["shape"],
            "skills": ["R1", "A5"],
            "skill_chain": (
                "read the Bestsellers report for %s and take its single rank-1 product -> "
                "apply the stated arithmetic to that product's catalog price"
                % spec["window_words"]),
            "derived_from": spec["derived_from"],
            "official_analogues": OFFICIAL_ANALOGUES[spec["mode"]],
            "topic": "bestseller_price_bump",
            "lane": "bestseller_price_bump",
            "batch": "batch-6 lane 55 (shopping_admin / R1 -> A5)",
            "surface": (
                "/admin/reports/report_sales/bestsellers/ (Period, From, To, Show Report) -> "
                "/admin/catalog/product/ keyword search -> row Edit -> "
                "/admin/catalog/product/edit/id/%d/ Price field -> Save" % t["id"]),
            "inspiration_ids": ["webarena-0", "webarena-3", "webarena-6",
                                "webarena-458", "webarena-461", "webarena-782"],
            "authoring_notes": [
                ("Pristine seed; no injection. reportAggregates / bestsellersAggregates are "
                 "bundled ES imports outside the 44 persisted state keys, so the report cannot "
                 "be injected - the retrieval is varied by interval and row selection instead."),
                ("Rendered interval: the report returns exactly one interval, %s, holding %d "
                 "rows. Rank 1 is %s (entity %d) at qty %g; the runner-up is %s (entity %d) at "
                 "qty %g, so the margin is %g and rank 1 is tie-free."
                 % (task["interval_label"], len(task["rows"]), t["name"], t["id"], t["qty"],
                    task["runner_up"]["name"], task["runner_up"]["id"],
                    task["runner_up"]["qty"], task["margin"])),
                "Full rendered ranking: %s." % rows_note,
                ("Period/From/To reach one interval by reportUtils.js:213-320: %s"
                 % branch_note(spec)),
                ("Price writer: ProductEdit.jsx:351 sets patch.price and calls patchProduct, "
                 "which writes state.productOverrides[<entity_id>].price "
                 "(AppContext.jsx:218-227). Price reader: ProductGrid.jsx:167-174 renders "
                 "formatCurrency(r.price) over getProducts(state) (ProductGrid.jsx:102), and "
                 "getProducts merges the same productOverrides patch (selectors.js:164-179). "
                 "Written key == rendered key."),
                ("Entity %d is a simple product with special_price null, so the edit form shows "
                 "one price field and the instruction is unambiguous about which price moves. "
                 "Configurable parents, whose price the form refuses to write "
                 "(ProductEdit.jsx:349-350), are not used as targets anywhere in this lane."),
                ("Arithmetic: $%s %s = $%s exactly, under the instruction's stated rule of "
                 "nearest cent, half up. The reward re-derives it with decimal.Decimal and "
                 "ROUND_HALF_UP, never a float, so the graded number and the rendered number "
                 "cannot drift apart. The seed price $%s is not already the target value."
                 % (t["seed_price"], op_words(spec), t["expected_price"], t["seed_price"])),
                ("Alternative-route check: recomputing the window from src/data/orders.json "
                 "over non-canceled orders reproduces the same rank-1 product, so the LIVE "
                 "Ordered Products report (LegacyReports.jsx:541-560, which also drops canceled "
                 "orders) agrees with the frozen Bestsellers aggregate. Counting canceled "
                 "orders in would give a different winner, which is why the instruction points "
                 "at the bestseller reading rather than at raw order lines."),
                ("Scope is a GATE, not a paid component: the four other ranked rows must still "
                 "resolve to their current prices, so repricing the whole ranked list scores "
                 "0.0. Nothing pays for restraint (TASK4 S3.2/S3.3)."),
            ],
            "hard_criteria": [],
            "has_initial_setup": False,
            "injected_preconditions": [],
        },
    }


def branch_note(spec):
    if spec["period"] == "month":
        return ("From is the 1st and To is the month end, and both fall in the same month, so "
                "the main select is disabled and one boundary select over bestsellers_daily "
                "renders a single interval. Period=Year over the same dates renders the same "
                "five rows, so the Period choice cannot change the answer here.")
    if spec["from"].endswith("-01-01") and spec["to"].endswith("-12-31"):
        return ("From 1/1 and To 12/31 of one calendar year: neither boundary branch fires, the "
                "same-year clause pushes one boundary select over bestsellers_daily and "
                "disables the main select, so the whole year renders as one interval.")
    return ("From and To stay inside one calendar year, so both partial-period branches are "
            "skipped (their dtTo/dtFrom guards fail) and the same-year clause emits exactly one "
            "boundary select over bestsellers_daily - one interval, five rows. CORRECTIONS #94's "
            "vanishing-year trap needs a range that STRADDLES a year boundary and is avoided by "
            "construction here.")


OFFICIAL_ANALOGUES = {
    "pct": [
        "Get the top-1 best-selling product name(s) in 2022",
        "Increase the price of the product on the current page by 10%",
        "Reduce the price of the product on the current page by 15%",
    ],
    "abs": [
        "Get the top-2 best-selling product name(s) in 2023",
        "Reduce the price of the product on the current page by $5",
        "Increase the price of the product on the current page by $11.5",
    ],
}


def nemo_task_json(task, reward_code):
    spec = task["spec"]
    return {
        "task_payload": {
            "task_id": task["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": spec["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task["task_id"],
                "app_dir": APP_DIR,
                "initial_setup": None,
                "eval_reward_code": reward_code,
            },
        }
    }


def replay_py(task):
    spec, t = task["spec"], task["target"]
    ranking = "\n".join(
        "      %d. %s (entity %d) qty %g"
        % (i + 1, decode_entities(r["product_name"]), r["product_id"], r["qty_ordered"])
        for i, r in enumerate(task["rows"]))
    if spec["start"] == "/":
        nav = ('    # start_path = "/" -> /admin/admin/dashboard/ (App.jsx:624).\n'
               '    page.click("#menu-reports > a.menu-item")\n'
               '    page.click(\'#menu-reports a[href*="/admin/reports/report_sales/bestsellers/"]\')\n'
               '    page.wait_for_selector("#filter_form")\n')
    else:
        nav = ('    # start_path = "%s" - the report is the subject of the task.\n'
               '    page.wait_for_selector("#filter_form")\n' % spec["start"])
    return '''"""Golden replay DRAFT for %(task_id)s.

Click-only: after the initial landing on `start_path` there is no page.goto(),
no constructed URL and no go_back() to a URL that was never clicked.

Task: %(instruction)s

Derived answer (computed offline from bestsellersAggregates.json and
products.json, NOT given to the agent): entity %(pid)d "%(name)s" (%(sku)s).

Bestsellers, Period=%(period)s, From %(from_us)s, To %(to_us)s renders ONE
interval, "%(interval)s", holding %(nrows)d rows:
%(ranking)s
    Margin at rank 1: %(margin)g order(s).

Price arithmetic: $%(seed)s %(op)s = $%(new)s (nearest cent, half up).

Reachability notes verified while authoring:
  * "/" redirects to /admin/admin/dashboard/ (App.jsx:624); the left rail item
    pins its flyout on click (AdminSidebar.jsx:12-16) and the Reports flyout
    carries the Bestsellers link (adminMenu.js:196), the Catalog flyout the
    Products link (adminMenu.js:52).
  * The filter form is #filter_form with #sales_report_period_type,
    #sales_report_from, #sales_report_to and the #filter_form_submit
    "Show Report" button (ReportPage.jsx:112-166). Dates are typed M/D/YYYY
    (formatters.js parseShortDate) - there are no relative-date presets.
  * A bare report load renders an empty grid: `applied` requires a from-or-to
    date, so Show Report must actually be pressed.
  * The products grid has a keyword search input (AdminGrid.jsx:420-431) and a
    per-row a[aria-label="Edit <name>"] link (ProductGrid.jsx:441-446).
  * The price field is input[name="product[price]"] (ProductEdit.jsx:737-748)
    and Save is #save-button (ProductEdit.jsx:464).
"""

TARGET_ID = %(pid)d
TARGET_NAME = %(name_repr)s
NEW_PRICE = "%(new)s"


def run(page, base_url, sid):
%(nav)s
    # R1 - configure the report window and read the rank-1 row.
    page.select_option("#sales_report_period_type", "%(period_value)s")
    page.fill("#sales_report_from", "%(from_us)s")
    page.fill("#sales_report_to", "%(to_us)s")
    page.click("#filter_form_submit")
    page.wait_for_selector("#bestsellersReportGrid tbody tr")

    # A5 - reprice that product in the catalog.
    page.click("#menu-catalog > a.menu-item")
    page.click('#menu-catalog a[href*="/admin/catalog/product/"]')
    page.wait_for_selector("input.data-grid-search-control")
    page.fill("input.data-grid-search-control", TARGET_NAME)
    page.press("input.data-grid-search-control", "Enter")
    page.wait_for_selector('a[aria-label="Edit %%s"]' %% TARGET_NAME)
    page.click('a[aria-label="Edit %%s"]' %% TARGET_NAME)
    page.wait_for_selector('input[name="product[price]"]')
    page.fill('input[name="product[price]"]', NEW_PRICE)
    page.click("#save-button")
    page.wait_for_selector("div.message-success, .message.message-success")
''' % {
        "task_id": task["task_id"],
        "instruction": spec["instruction"],
        "pid": t["id"], "name": t["name"], "name_repr": repr(t["name"]), "sku": t["sku"],
        "period": spec["period"].capitalize(), "period_value": spec["period"],
        "from_us": us(spec["from"]), "to_us": us(spec["to"]),
        "interval": task["interval_label"], "nrows": len(task["rows"]),
        "ranking": ranking, "margin": task["margin"],
        "seed": t["seed_price"], "new": t["expected_price"], "op": op_words(spec),
        "nav": nav,
    }


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def main():
    tasks = [build(s) for s in SPEC]
    ids = [t["target"]["id"] for t in tasks]
    assert len(set(ids)) == 10, ids
    assert len({t["task_id"] for t in tasks}) == 10

    os.makedirs(os.path.join(BATCH_DIR, "replays"), exist_ok=True)
    rows_jsonl = []
    index = {"schema_version": 2, "tasks": []}

    for task in tasks:
        bundle = os.path.join(OUT_TASKS, task["task_id"])
        write(os.path.join(bundle, "task_instruction.json"),
              json.dumps(instruction_json(task), indent=2) + "\n")
        write(os.path.join(bundle, "task.json"),
              json.dumps(task_json(task), indent=2) + "\n")
        write(os.path.join(bundle, "reward.py"), reward_py(task))
        nemo_code = nemo_reward_py(task)
        write(os.path.join(bundle, "nemo_reward.py"), nemo_code)
        row = nemo_task_json(task, nemo_code)
        write(os.path.join(bundle, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
        rows_jsonl.append(json.dumps(row))
        write(os.path.join(BATCH_DIR, "replays", task["task_id"] + ".py"), replay_py(task))
        index["tasks"].append({
            "task_id": task["task_id"],
            "path": "../../%s/task.json" % task["task_id"],
        })

    write(os.path.join(BATCH_DIR, "index.json"), json.dumps(index, indent=2) + "\n")
    write(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "\n".join(rows_jsonl) + "\n")

    for task in tasks:
        s = task["spec"]
        print("%-58s pid=%-5d %s %s..%s  $%s -> $%s  margin=%g  %s/%s" % (
            task["task_id"], task["target"]["id"], s["period"], s["from"], s["to"],
            task["target"]["seed_price"], task["target"]["expected_price"],
            task["margin"], s["style"], s["shape"]))
    return tasks


if __name__ == "__main__":
    main()
