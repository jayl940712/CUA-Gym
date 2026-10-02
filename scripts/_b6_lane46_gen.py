#!/usr/bin/env python3
"""Batch-6 lane 46 generator - shopping_admin, R5 -> A13.

Chain: filter the Products grid to one colour slice of a size/colour matrix,
read the Quantity column to find the slice's lowest-stocked variant, then act
conditionally - add the arriving units to whatever it already holds, and only
if it held nothing at all, also flip its Stock Status to In Stock.

Every fact below was read out of ./hub/websites/webarena_shopping_admin_mock:
  * is_in_stock is a STORED product field, not derived from qty
    (ProductEdit.jsx:143 reads it, :311 writes it, :859-866 renders the
    "Stock Status" select).
  * writer  productOverrides[<entity_id>]  (AppContext.jsx patchProduct, :218-227)
    reader  getProducts (selectors.js:164-180) -> ProductGrid.jsx:102
    reader  getProduct  (selectors.js:154-162) -> ProductEdit.jsx
  * Quantity column is filterType 'range' (ProductGrid.jsx:174-183); the hidden
    Color column is filterType 'select' (:265-275) and AdminGrid renders a
    filter for every column with a filterType regardless of visibility
    (AdminGrid.jsx:405-412).
  * product_listing page size is 200 (gridUtils.js GRID_PAGE_SIZES), so every
    matched slice here is a single page.
Run:  python3 scripts/_b6_lane46_gen.py
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
HUB = os.path.join(ROOT, "hub/websites/webarena_shopping_admin_mock")
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/conditional_restock_stock_status")
APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

PRODUCTS = json.load(open(os.path.join(HUB, "src/data/products.json")))
BY_ID = {p["entity_id"]: p for p in PRODUCTS}
OPTIONS = json.load(open(os.path.join(HUB, "src/data/attributeOptions.json")))
COLORS = OPTIONS["color"]
SIZES = OPTIONS["size"]
COLOR_ID = {v: int(k) for k, v in COLORS.items()}

ANALOGUE_768 = ("5 blue Cronus yoga pants with size 33 arrived, update the stock. "
                "If previous stock exist, add to it. If it does not exist previously, "
                "also update stock status to in stock.")
ANALOGUE_769 = ("We've received additional 378 brown Aero daily fitness tee in every size, "
                "please update the inventory. If previous stock exist, add to it. If it does "
                "not exist previously, also update stock status to in stock.")
ANALOGUE_770 = ("We've received additional 12 white Cora parachute pant of size 28 and 56 blue "
                "of size 29, update the inventory. If previous stock exist, add to it. If it "
                "does not exist previously, also update stock status to in stock.")
ANALOGUE_501 = "Mark all Taurus Elements Shell as out of stock"
ANALOGUE_504 = "Mark all Selene yoga hoodie as out of stock"


def family_rows(prefix):
    """Every simple variant of a family, plus its configurable parent."""
    variants = [p for p in PRODUCTS
                if p["sku"].split("-")[0] == prefix and p["type_id"] == "simple"]
    parent = [p for p in PRODUCTS
              if p["sku"] == prefix and p["type_id"] == "configurable"]
    return variants, (parent[0] if parent else None)


# --------------------------------------------------------------------------
# The ten tasks. `inject` maps entity_id -> {qty, is_in_stock?}; an entry with
# is_in_stock present is written as {qty, salable_quantity, is_in_stock},
# otherwise as {qty, salable_quantity} - exactly the two shapes the mock's own
# bulk "Update attributes" handler emits (ProductGrid.jsx:491, :496).
# --------------------------------------------------------------------------
TASKS = [
    {
        "n": 1,
        "slug": "cronus_blue_sold_out_size_25_units",
        "family": "MP12", "family_label": "Cronus Yoga Pant",
        "plural": "blue Cronus Yoga Pants", "colour": "Blue",
        "delivery": 25,
        "target": 872,
        "inject": {},
        "style": "terse", "shape": "mutation", "start_path": "/",
        "derived_from": "restock_shorted_variants_cronus_size33_delivery_010",
        "analogues": [ANALOGUE_768, ANALOGUE_501],
        "note": ("Pristine seed. Entity 872 / MP12-33-Blue is the only row of all 2,040 "
                 "with is_in_stock 0 and the only simple product with qty 0, so the "
                 "out-of-stock arm of the conditional exists with no injection at all."),
    },
    {
        "n": 2,
        "slug": "eos_blue_short_size_30_units",
        "family": "WH11", "family_label": "Eos V-Neck Hoodie",
        "plural": "blue Eos V-Neck Hoodies", "colour": "Blue",
        "delivery": 30,
        "target": 1182,
        "inject": {},
        "style": "terse", "shape": "retrieval_writeback", "start_path": "/",
        "derived_from": "restock_shorted_variants_eos_blue_run_levelled_009",
        "analogues": [ANALOGUE_768, ANALOGUE_769],
        "note": ("Pristine seed. WH11-S-Blue carries the seeded qty 3 against 100 on the "
                 "other four blue sizes, so the slice minimum is unique with a margin of 97 "
                 "and the conditional resolves the OTHER way from task 001 on identical "
                 "wording."),
    },
    {
        "n": 3,
        "slug": "troy_black_short_size_48_units",
        "family": "MSH09", "family_label": "Troy Yoga Short",
        "plural": "black Troy Yoga Shorts", "colour": "Black",
        "delivery": 48,
        "target": 986,
        "inject": {},
        "style": "terse", "shape": "retrieval_writeback", "start_path": "/",
        "derived_from": None,
        "analogues": [ANALOGUE_768, ANALOGUE_770],
        "note": "Pristine seed. MSH09-36-Black is seeded at 4 against 100; margin 96.",
    },
    {
        "n": 4,
        "slug": "minerva_blue_short_size_17_units",
        "family": "WS08", "family_label": "Minerva LumaTech V-Tee",
        "plural": "blue Minerva LumaTech V-Tees", "colour": "Blue",
        "delivery": 17,
        "target": 1478,
        "inject": {},
        "style": "terse", "shape": "retrieval_writeback", "start_path": "/",
        "derived_from": None,
        "analogues": [ANALOGUE_769, ANALOGUE_501],
        "note": "Pristine seed. WS08-XS-Blue is seeded at 3 against 100; margin 97.",
    },
    {
        "n": 5,
        "slug": "iris_red_short_size_36_units",
        "family": "WS03", "family_label": "Iris Workout Top",
        "plural": "red Iris Workout Tops", "colour": "Red",
        "delivery": 36,
        "target": 1415,
        "inject": {},
        "style": "explicit", "shape": "retrieval_writeback",
        "start_path": "/admin/catalog/product/",
        "derived_from": None,
        "analogues": [ANALOGUE_770, ANALOGUE_768],
        "note": ("Pristine seed. WS03-XS-Red is seeded at 14 against 100; margin 86. Its "
                 "stock reservation is -1, so Salable Quantity reads 15 and still ranks "
                 "lowest in the slice."),
    },
    {
        "n": 6,
        "slug": "caesar_gray_zeroed_size_45_units",
        "family": "MP01", "family_label": "Caesar Warm-Up Pant",
        "plural": "gray Caesar Warm-Up Pants", "colour": "Gray",
        "delivery": 45,
        "target": 729,
        "inject": {726: {"qty": 58}, 729: {"qty": 0, "is_in_stock": 0},
                   732: {"qty": 31}, 735: {"qty": 74}},
        "style": "terse", "shape": "mutation", "start_path": "/",
        "derived_from": "restock_shorted_variants_cronus_size33_delivery_010",
        "analogues": [ANALOGUE_768, ANALOGUE_504],
        "note": ("Injected slice 58 / 0 / 31 / 74. Unique minimum at MP01-33-Gray with a "
                 "margin of 31, and the zero row also carries is_in_stock 0 so the "
                 "conditional's second clause has real work to do."),
    },
    {
        "n": 7,
        "slug": "josie_blue_thin_size_54_units",
        "family": "WJ02", "family_label": "Josie Yoga Jacket",
        "plural": "blue Josie Yoga Jackets", "colour": "Blue",
        "delivery": 54,
        "target": 1228,
        "inject": {1222: {"qty": 52}, 1225: {"qty": 19}, 1228: {"qty": 6},
                   1231: {"qty": 88}, 1234: {"qty": 40}},
        "style": "terse", "shape": "retrieval_writeback", "start_path": "/",
        "derived_from": None,
        "analogues": [ANALOGUE_769, ANALOGUE_768],
        "note": ("Injected slice 52 / 19 / 6 / 88 / 40. Unique minimum at WJ02-M-Blue, "
                 "margin 13 over the runner-up, and it keeps its stock so the status "
                 "clause must NOT fire."),
    },
    {
        "n": 8,
        "slug": "autumn_purple_zeroed_size_80_units",
        "family": "WH03", "family_label": "Autumn Pullie",
        "plural": "purple Autumn Pullies", "colour": "Purple",
        "delivery": 80,
        "target": 1065,
        "inject": {1062: {"qty": 37}, 1065: {"qty": 0, "is_in_stock": 0},
                   1068: {"qty": 22}, 1071: {"qty": 61}, 1074: {"qty": 13}},
        "style": "terse", "shape": "mutation", "start_path": "/",
        "derived_from": None,
        "analogues": [ANALOGUE_768, ANALOGUE_770],
        "note": ("Injected slice 37 / 0 / 22 / 61 / 13. The runner-up sits at 13, so an "
                 "agent that eyeballs the slice instead of reading it lands on WH03-XL-Purple "
                 "and scores 0.0."),
    },
    {
        "n": 9,
        "slug": "zoltan_yellow_thin_size_39_units",
        "family": "MS06", "family_label": "Zoltan Gym Tee",
        "plural": "yellow Zoltan Gym Tees", "colour": "Yellow",
        "delivery": 39,
        "target": 538,
        "inject": {529: {"qty": 44}, 532: {"qty": 71}, 535: {"qty": 28},
                   538: {"qty": 11}, 541: {"qty": 96}},
        "style": "explicit", "shape": "retrieval_writeback", "start_path": "/",
        "derived_from": None,
        "analogues": [ANALOGUE_769, ANALOGUE_501],
        "note": ("Injected slice 44 / 71 / 28 / 11 / 96. Unique minimum at MS06-L-Yellow, "
                 "margin 17. No stock reservation touches this slice, so Quantity and "
                 "Salable Quantity rank identically."),
    },
    {
        "n": 10,
        "slug": "breathe_easy_white_zeroed_size_60_units",
        "family": "WT09", "family_label": "Breathe-Easy Tank",
        "plural": "white Breathe-Easy Tanks", "colour": "White",
        "delivery": 60,
        "target": 1804,
        "inject": {1798: {"qty": 26}, 1801: {"qty": 48},
                   1804: {"qty": 0, "is_in_stock": 0},
                   1807: {"qty": 15}, 1810: {"qty": 63}},
        "style": "terse", "shape": "mutation",
        "start_path": "/admin/catalog/product/",
        "derived_from": None,
        "analogues": [ANALOGUE_770, ANALOGUE_504],
        "note": ("Injected slice 26 / 48 / 0 / 15 / 63. Runner-up 15, margin 15; the zero "
                 "row carries is_in_stock 0 so the status clause fires."),
    },
]


def build(task):
    prefix = task["family"]
    variants, parent = family_rows(prefix)
    colour_id = COLOR_ID[task["colour"]]
    injections = task["inject"]

    def base_qty(pid):
        row = BY_ID[pid]
        patch = injections.get(pid) or {}
        return float(patch.get("qty", row["qty"]))

    def base_stock(pid):
        row = BY_ID[pid]
        patch = injections.get(pid) or {}
        return int(patch.get("is_in_stock", row["is_in_stock"]))

    slice_rows = [p for p in variants if p.get("color") == colour_id]
    assert slice_rows, prefix
    ranked = sorted(slice_rows, key=lambda p: (base_qty(p["entity_id"]), p["entity_id"]))
    target = BY_ID[task["target"]]
    assert ranked[0]["entity_id"] == task["target"], (prefix, ranked[0]["sku"])
    margin = base_qty(ranked[1]["entity_id"]) - base_qty(ranked[0]["entity_id"])
    assert margin > 0, (prefix, margin)

    prior = base_qty(task["target"])
    prior_stock = base_stock(task["target"])
    expected_qty = prior + task["delivery"]
    expected_stock = 1
    arm = "zero" if prior == 0 else "existing"
    if arm == "zero":
        assert prior_stock == 0, task["target"]
    else:
        assert prior_stock == 1, task["target"]

    # Scope: the whole family (every simple variant plus the configurable
    # parent). Untouched rows must keep the quantity and stock status they
    # start the episode with.
    scope = []
    for p in variants + ([parent] if parent else []):
        pid = p["entity_id"]
        if pid == task["target"]:
            continue
        scope.append({"id": pid, "sku": p["sku"],
                      "qty": base_qty(pid), "is_in_stock": base_stock(pid)})

    task_id = "conditional_restock_stock_status_%s_%03d" % (task["slug"], task["n"])
    size_label = SIZES[str(target["size"])]
    colour_lower = task["colour"].lower()

    if task["style"] == "terse":
        instruction = (
            "%d %s arrived. Add them to the %s size we're lowest on, and if that size "
            "had no stock at all, set its Stock Status to In Stock too."
            % (task["delivery"], task["plural"], colour_lower)
        )
    else:
        instruction = (
            "Open Catalog > Products and narrow the grid to the %s %s variants. "
            "Work out which %s size is carrying the least stock, then add the %d units "
            "that just arrived to whatever quantity that size already shows. If it had "
            "no stock at all beforehand, also switch its Stock Status to In Stock. "
            "Leave the rest of the %s line untouched."
            % (colour_lower, task["family_label"], colour_lower, task["delivery"],
               task["family_label"])
        )

    slice_desc = ", ".join(
        "%s %s (id %d, qty %s)" % (SIZES[str(p["size"])], task["colour"], p["entity_id"],
                                   _fmt(base_qty(p["entity_id"])))
        for p in ranked)

    return {
        "task": task,
        "task_id": task_id,
        "instruction": instruction,
        "target_id": task["target"],
        "target_sku": target["sku"],
        "target_name": _decode(target["name"]),
        "size_label": size_label,
        "prior_qty": prior,
        "prior_stock": prior_stock,
        "expected_qty": expected_qty,
        "expected_stock": expected_stock,
        "arm": arm,
        "margin": margin,
        "scope": scope,
        "slice_ids": [p["entity_id"] for p in ranked],
        "slice_desc": slice_desc,
        "colour_id": colour_id,
        "parent_id": parent["entity_id"] if parent else None,
    }


def _decode(name):
    return (name.replace("&trade;", "™").replace("&reg;", "®")
                .replace("&amp;", "&").strip())


def _fmt(value):
    return str(int(value)) if float(value).is_integer() else str(value)


# --------------------------------------------------------------------------
# emitters
# --------------------------------------------------------------------------
REWARD_BODY = '''
EXPECTED = json.loads(r"""
%(fixture)s
""")

COMPONENT_WEIGHTS = {
%(weights_block)s}


def _num(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _overrides(state):
    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        return {}
    return overrides


def _effective(state, entity_id, field, baseline):
    patch = _overrides(state).get(str(entity_id))
    if isinstance(patch, dict) and field in patch:
        return _num(patch.get(field))
    return float(baseline)


def _deleted(state):
    removed = state.get("deletedProductIds")
    if not isinstance(removed, list):
        return set()
    out = set()
    for value in removed:
        number = _num(value)
        if number is not None:
            out.add(int(number))
    return out


def _checks(state):
    target_id = EXPECTED["target_id"]
    removed = _deleted(state)
    scope_ok = target_id not in removed
    for row in EXPECTED["scope"]:
        if not scope_ok:
            break
        if int(row["id"]) in removed:
            scope_ok = False
            break
        qty_now = _effective(state, row["id"], "qty", row["qty"])
        stock_now = _effective(state, row["id"], "is_in_stock", row["is_in_stock"])
        if qty_now is None or stock_now is None:
            scope_ok = False
            break
        if abs(qty_now - float(row["qty"])) > 1e-6:
            scope_ok = False
            break
        if int(round(stock_now)) != int(row["is_in_stock"]):
            scope_ok = False
            break

    patch = _overrides(state).get(str(target_id))
    if not isinstance(patch, dict):
        patch = {}
    qty_now = _num(patch.get("qty"))
    salable_now = _num(patch.get("salable_quantity"))
    expected_qty = float(EXPECTED["expected_qty"])
    qty_ok = (
        qty_now is not None
        and salable_now is not None
        and abs(qty_now - expected_qty) <= 1e-6
        and abs(salable_now - expected_qty) <= 1e-6
    )
    stock_now = _effective(state, target_id, "is_in_stock", EXPECTED["prior_is_in_stock"])
    status_ok = (
        qty_ok
        and stock_now is not None
        and int(round(stock_now)) == int(EXPECTED["expected_is_in_stock"])
    )
    return {
%(returns_block)s    }
'''


def reward_py(spec):
    fixture = json.dumps({
        "target_id": spec["target_id"],
        "target_sku": spec["target_sku"],
        "prior_qty": spec["prior_qty"],
        "prior_is_in_stock": spec["prior_stock"],
        "expected_qty": spec["expected_qty"],
        "expected_is_in_stock": spec["expected_stock"],
        "scope": spec["scope"],
    }, indent=2)
    body = REWARD_BODY % {
        "fixture": fixture,
        "weights_block": spec["weights_block"],
        "returns_block": spec["returns_block"],
    }
    doc = (
        '"""Deterministic reward for %s.\n'
        "\n"
        "Success criteria:\n"
        "%s"
        "  * every other %s row resolves to the quantity and stock status it began\n"
        "    the episode with, which GATES the scored component(s) rather than paying\n"
        "    for restraint\n"
        "\n"
        "Only user-visible persisted state is inspected, and only `current_state`.\n"
        "Ground truth is fixed by the frozen product corpus of\n"
        "webarena_shopping_admin_mock in ./hub/ plus this bundle's own\n"
        "initial_setup.py where present.\n"
        '"""\n'
        "\n"
        "import json\n"
    ) % (spec["task_id"], spec["doc_criteria"], spec["task"]["family_label"])
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
    return doc + body + tail


def nemo_reward_py(spec):
    fixture = json.dumps({
        "target_id": spec["target_id"],
        "target_sku": spec["target_sku"],
        "prior_qty": spec["prior_qty"],
        "prior_is_in_stock": spec["prior_stock"],
        "expected_qty": spec["expected_qty"],
        "expected_is_in_stock": spec["expected_stock"],
        "scope": spec["scope"],
    }, indent=2)
    body = REWARD_BODY % {
        "fixture": fixture,
        "weights_block": spec["weights_block"],
        "returns_block": spec["returns_block"],
    }
    head = (
        '"""NeMo-Gym reward program for %s.\n'
        "\n"
        "Implements exactly the rubric of reward.py, reading `current_state`\n"
        "from GET /go?sid=... instead of a frozen evidence bundle, and printing\n"
        "REWARD: <float> on every output path including the error path.\n"
        "\n"
        "Self-contained: standard library plus requests, which is present in\n"
        "cuagym/requirements.txt.\n"
        '"""\n'
        "\n"
        "import json\n"
        "import sys\n"
        "\n"
        "import requests\n"
        "\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n'
    ) % (spec["task_id"], URL_PLACEHOLDER)
    tail = '''

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
    return head + body + tail


def setup_py(spec):
    injections = spec["task"]["inject"]
    payload = {}
    for pid in sorted(injections):
        patch = injections[pid]
        entry = {"qty": patch["qty"], "salable_quantity": patch["qty"]}
        if "is_in_stock" in patch:
            entry["is_in_stock"] = patch["is_in_stock"]
        payload[str(pid)] = entry
    lines = "\n".join(
        "#   %s -> %s (%s, seeded qty %s / is_in_stock %d)"
        % (pid, json.dumps(payload[pid]), BY_ID[int(pid)]["sku"],
           _fmt(BY_ID[int(pid)]["qty"]), BY_ID[int(pid)]["is_in_stock"])
        for pid in payload)
    return (
        '"""NeMo-Gym setup program for %(task_id)s.\n'
        "\n"
        "Spreads realistic stock levels across the %(colour_lower)s %(family)s slice so\n"
        "the grid actually has to be read: the slice minimum is unique with a margin\n"
        "of %(margin)s, and none of the injected values is the answer the task asks\n"
        "for, so the untouched session still scores exactly 0.0.\n"
        "\n"
        "Each injected patch carries the same field set the mock's own bulk\n"
        '"Update attributes" handler writes (ProductGrid.jsx:491, :496):\n'
        "{qty, salable_quantity} for a plain restock and\n"
        "{qty, salable_quantity, is_in_stock} for a row that has run out.\n"
        "\n"
        "Written as a read-modify-write: GET /go, mutate the whole document, POST it\n"
        "back. Correct on every mock regardless of whether a partial `set` merges or\n"
        "replaces (output/CENSUS_ERRATA.md).\n"
        "\n"
        "Self-contained: standard library plus requests, which is present in\n"
        "cuagym/requirements.txt.\n"
        '"""\n'
        "\n"
        "import json\n"
        "import sys\n"
        "\n"
        "import requests\n"
        "\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%(url)s"\n'
        "\n"
        "# entity_id -> patch, merged into state.productOverrides:\n"
        "%(lines)s\n"
        "PRODUCT_OVERRIDES = json.loads(r\"\"\"\n"
        "%(payload)s\n"
        "\"\"\")\n"
        "\n"
        "\n"
        "def load_state():\n"
        '    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        "    response.raise_for_status()\n"
        "    payload = response.json()\n"
        '    state = payload.get("current_state")\n'
        "    if not isinstance(state, dict):\n"
        '        state = payload.get("initial_state")\n'
        "    if not isinstance(state, dict):\n"
        '        print("SETUP FAILED: /go returned neither current_state nor initial_state",\n'
        "              file=sys.stderr)\n"
        "        raise SystemExit(1)\n"
        "    return state\n"
        "\n"
        "\n"
        "def main():\n"
        "    state = load_state()\n"
        '    overrides = state.get("productOverrides")\n'
        "    if not isinstance(overrides, dict):\n"
        "        overrides = {}\n"
        "    for entity_id, patch in PRODUCT_OVERRIDES.items():\n"
        "        current = overrides.get(entity_id)\n"
        "        if not isinstance(current, dict):\n"
        "            current = {}\n"
        "        merged = dict(current)\n"
        "        merged.update(patch)\n"
        "        overrides[entity_id] = merged\n"
        '    state["productOverrides"] = overrides\n'
        "\n"
        "    response = requests.post(\n"
        '        BASE_URL + "/post?sid=" + SID,\n'
        '        json={"action": "set", "state": state},\n'
        "        timeout=60,\n"
        "    )\n"
        "    response.raise_for_status()\n"
        "\n"
        '    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        "    check.raise_for_status()\n"
        "    payload = check.json()\n"
        '    current = payload.get("current_state") or {}\n'
        '    saved = current.get("productOverrides") or {}\n'
        "    for entity_id, patch in PRODUCT_OVERRIDES.items():\n"
        "        row = saved.get(entity_id)\n"
        "        if not isinstance(row, dict):\n"
        '            print("SETUP FAILED: override %%s missing" %% entity_id, file=sys.stderr)\n'
        "            raise SystemExit(1)\n"
        "        for field, value in patch.items():\n"
        "            if float(row.get(field)) != float(value):\n"
        '                print("SETUP FAILED: %%s.%%s not persisted" %% (entity_id, field),\n'
        "                      file=sys.stderr)\n"
        "                raise SystemExit(1)\n"
        '    if payload.get("state_diff") != {}:\n'
        '        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)\n'
        "        raise SystemExit(1)\n"
        '    print("SETUP OK")\n'
        "\n"
        "\n"
        "main()\n"
    ) % {
        "task_id": spec["task_id"],
        "colour_lower": spec["task"]["colour"].lower(),
        "family": spec["task"]["family_label"],
        "margin": _fmt(spec["margin"]),
        "url": URL_PLACEHOLDER,
        "lines": lines,
        "payload": json.dumps(payload, indent=2),
    }


def replay_py(spec):
    task = spec["task"]
    steps = []
    if spec["arm"] == "zero":
        steps.append(
            '    page.select_option(\n'
            '        \'select[name="product[quantity_and_stock_status][is_in_stock]"]\', "1")\n')
    return '''"""Golden replay DRAFT for %(task_id)s.

Click-only: after the initial landing on `start_path` there is no page.goto(),
no constructed URL and no go_back() to a URL that was never clicked.

Task: %(instruction)s

Derived answer (computed offline from src/data/products.json plus this bundle's
initial_setup.py, NOT given to the agent): product %(target_id)d
"%(target_name)s" (%(target_sku)s), the %(colour)s slice's unique minimum.
Slice, ascending: %(slice_desc)s
Margin over the runner-up: %(margin)s units.
Prior quantity %(prior_qty)s + %(delivery)d arriving = %(expected_qty)s;
prior is_in_stock %(prior_stock)d -> %(expected_stock)d.

Reachability notes verified while authoring:
  * "/" redirects to /admin/admin/dashboard/ (App.jsx:624). The left rail item
    #menu-catalog is <a href="#"> and pins its flyout on click
    (AdminSidebar.jsx:12-16); the flyout carries the Products link
    (adminMenu.js:52 -> /admin/catalog/product/).
  * The filters panel is rendered eagerly and hidden with CSS
    (AdminGrid.jsx:573-582), and filterableColumns covers every column with a
    filterType regardless of visibility (AdminGrid.jsx:405-412) - so
    [name="color"] and [name="sku"] both resolve.
  * product_listing's page size is 200 (gridUtils.js GRID_PAGE_SIZES), not the
    20 ProductGrid passes as defaultPageSize, so a %(slice_size)d-row slice is
    one page and no paging is needed.
  * The row Edit link is a[aria-label="Edit <name>"] (ProductGrid.jsx:441-446).
  * Stock Status is a stored field: ProductEdit.jsx:143 seeds the select from
    the record and :311 writes is_in_stock back through patchProduct. It is NOT
    derived from qty, so it has to be set explicitly.
"""

TARGET_ID = %(target_id)d
TARGET_NAME = %(target_name_repr)s
EXPECTED_QTY = "%(expected_qty)s"


def run(page, base_url, sid):
    # start_path = %(start_path_repr)s
%(nav)s
    # R5 - narrow the grid to one colour slice of the family.
    page.click('[data-action="grid-filter-expand"]')
    page.fill('[data-part="filter-form"] [name="sku"]', "%(sku_prefix)s-")
    page.select_option('[data-part="filter-form"] [name="color"]', "%(colour_id)d")
    page.click('[data-action="grid-filter-apply"]')
    page.wait_for_load_state("networkidle")

    # The Quantity column is what "lowest on" is read from.
    page.wait_for_selector('a[aria-label="Edit %%s"]' %% TARGET_NAME)
    page.click('a[aria-label="Edit %%s"]' %% TARGET_NAME)
    page.wait_for_selector('input[name="product[quantity_and_stock_status][qty]"]')

    # A13 - add the delivery to whatever was already on hand.
    page.fill('input[name="product[quantity_and_stock_status][qty]"]', EXPECTED_QTY)
%(steps)s    page.click("#save-button")
    page.wait_for_selector("div.message-success, .message.message-success")
''' % {
        "task_id": spec["task_id"],
        "instruction": spec["instruction"],
        "target_id": spec["target_id"],
        "target_name": spec["target_name"],
        "target_name_repr": repr(spec["target_name"]),
        "target_sku": spec["target_sku"],
        "colour": task["colour"],
        "slice_desc": spec["slice_desc"],
        "margin": _fmt(spec["margin"]),
        "prior_qty": _fmt(spec["prior_qty"]),
        "delivery": task["delivery"],
        "expected_qty": _fmt(spec["expected_qty"]),
        "prior_stock": spec["prior_stock"],
        "expected_stock": spec["expected_stock"],
        "slice_size": len(spec["slice_ids"]),
        "start_path_repr": repr(task["start_path"]),
        "nav": ("    # already on the Products grid.\n"
                if task["start_path"] != "/" else
                '    page.click("#menu-catalog > a.menu-item")\n'
                '    page.click(\'#menu-catalog a[href*="/admin/catalog/product/"]\')\n'
                '    page.wait_for_load_state("networkidle")\n'),
        "sku_prefix": task["family"],
        "colour_id": spec["colour_id"],
        "steps": "".join(steps),
    }


def main():
    specs = []
    for task in TASKS:
        spec = build(task)
        # Rubric shape.
        #
        # On the ZERO arm the flag has to MOVE (0 -> 1), so "the flag reads 1" is
        # something the agent made true and can stand as its own paid component.
        #
        # On the EXISTING arm the correct end state leaves the flag at 1, so a
        # standalone flag component would be satisfied by an agent that did
        # nothing - the shape TASK4 S3.2 forbids for a terse task. There the flag
        # is folded into a single exact-collection assertion over the target
        # row's whole resulting tuple (qty, salable_quantity, is_in_stock), which
        # is S3.3's "assert the exact resulting collection" and is false on an
        # untouched session because the expected qty is not the prior qty.
        #
        # The accepted set is identical either way; only the 0.6 partial-credit
        # rung disappears, so the folded form is strictly stronger.
        qty_only = "target_quantity_is_prior_stock_plus_delivery"
        tuple_all = "target_row_stock_tuple_is_exactly_expected"
        flip = "target_stock_status_flipped_to_in_stock"
        if spec["arm"] == "zero":
            spec["single"] = False
            spec["weights_block"] = ('    "%s": 0.6,\n    "%s": 0.4,\n'
                                     % (qty_only, flip))
            spec["returns_block"] = (
                '        "%s": bool(scope_ok and qty_ok),\n'
                '        "%s": bool(scope_ok and status_ok),\n' % (qty_only, flip))
            spec["components"] = [(qty_only, 0.6), (flip, 0.4)]
            spec["doc_criteria"] = (
                "  * productOverrides[%d] records qty and salable_quantity of %s -\n"
                "    the %s it held for %s plus the %d that arrived\n"
                "  * that row's is_in_stock has moved from 0 to 1\n"
                % (spec["target_id"], _fmt(spec["expected_qty"]),
                   _fmt(spec["prior_qty"]), spec["target_sku"],
                   spec["task"]["delivery"]))
        else:
            spec["single"] = True
            spec["weights_block"] = '    "%s": 1.0,\n' % tuple_all
            spec["returns_block"] = (
                '        "%s": bool(scope_ok and status_ok),\n' % tuple_all)
            spec["components"] = [(tuple_all, 1.0)]
            spec["doc_criteria"] = (
                "  * the resulting tuple on productOverrides[%d] is exactly\n"
                "    (qty %s, salable_quantity %s, is_in_stock 1) - the %s it held\n"
                "    for %s plus the %d that arrived, with the flag it must end on\n"
                % (spec["target_id"], _fmt(spec["expected_qty"]),
                   _fmt(spec["expected_qty"]), _fmt(spec["prior_qty"]),
                   spec["target_sku"], spec["task"]["delivery"]))
        specs.append(spec)

    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []

    for spec in specs:
        task = spec["task"]
        tid = spec["task_id"]
        bundle = os.path.join(OUT, tid)
        os.makedirs(bundle, exist_ok=True)

        has_setup = bool(task["inject"])
        if spec["single"]:
            criteria = [
                ("productOverrides[%d] (%s, %s) resolves to exactly qty %s, "
                 "salable_quantity %s and is_in_stock 1 - the %s it held plus the %d "
                 "that arrived, on a row that was already in stock so the "
                 "conditional's second clause must not fire"
                 % (spec["target_id"], spec["target_sku"], spec["target_name"],
                    _fmt(spec["expected_qty"]), _fmt(spec["expected_qty"]),
                    _fmt(spec["prior_qty"]), task["delivery"])),
            ]
        else:
            criteria = [
                ("productOverrides[%d] (%s, %s) records qty %s and salable_quantity %s - "
                 "the %s it held plus the %d that arrived"
                 % (spec["target_id"], spec["target_sku"], spec["target_name"],
                    _fmt(spec["expected_qty"]), _fmt(spec["expected_qty"]),
                    _fmt(spec["prior_qty"]), task["delivery"])),
                ("that row's is_in_stock has moved from 0 to 1, because it began the "
                 "episode holding nothing and flagged Out of Stock"),
            ]
        criteria.append(
            "every other %s row resolves to the quantity and stock status it began the "
            "episode with; this GATES the scored component(s), so an over-broad edit "
            "scores 0.0 rather than a docked partial" % task["family_label"])

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": tid,
                "task_instruction": spec["instruction"],
                "app_dir": APP_DIR,
                "start_path": task["start_path"],
                "difficulty": "medium",
                "success_criteria": criteria,
            }, fh, indent=2)
            fh.write("\n")

        injected = []
        for pid in sorted(task["inject"]):
            patch = task["inject"][pid]
            row = BY_ID[pid]
            injected.append(
                "productOverrides['%d'] = {qty: %s, salable_quantity: %s%s} - %s, seeded "
                "qty %s / is_in_stock %d%s"
                % (pid, _fmt(patch["qty"]), _fmt(patch["qty"]),
                   ", is_in_stock: %d" % patch["is_in_stock"] if "is_in_stock" in patch else "",
                   _decode(row["name"]), _fmt(row["qty"]), row["is_in_stock"],
                   "; this is the derived target and the branch-decider"
                   if pid == spec["target_id"] else ""))

        notes = [
            task["note"],
            ("Stock status is a STORED field on this mock, not derived from quantity: "
             "ProductEdit.jsx:143 seeds the Stock Status select from the record's "
             "is_in_stock, :311 writes it back and :859-866 renders it. The Products grid "
             "has no stock-status column at all, so the branch can only be resolved by "
             "opening the row - which is what makes the conditional real."),
            ("Writer and reader are the same key: patchProduct writes "
             "state.productOverrides[<entity_id>] (AppContext.jsx:218-227); getProducts "
             "(selectors.js:164-180) merges it for the grid and getProduct "
             "(selectors.js:154-162) for the edit form."),
            ("R5 is genuinely clickable: the Quantity column is filterType 'range' "
             "(ProductGrid.jsx:174-183) and the hidden Color column is filterType 'select' "
             "(ProductGrid.jsx:265-275); AdminGrid builds its filter panel from every "
             "column with a filterType, visible or not (AdminGrid.jsx:405-412), and "
             "renders the panel eagerly (:573-582)."),
            ("Slice ascending by Quantity: %s. Unique minimum, margin %s units over the "
             "runner-up." % (spec["slice_desc"], _fmt(spec["margin"]))),
            ("The colour filter also removes the configurable parent from the slice - "
             "parents carry no color option, so String(r.color ?? '') is '' and never "
             "matches. That matters because every parent in this catalogue sits at qty 0 "
             "and would otherwise tie or beat the intended minimum."),
            ("product_listing's page size is 200 (gridUtils.js GRID_PAGE_SIZES, which wins "
             "over ProductGrid's defaultPageSize={20} - CORRECTIONS #89), so this "
             "%d-row slice renders as one page and 'select all on page' never arises."
             % len(spec["slice_ids"])),
            ("Salable Quantity ranks the slice identically to Quantity here: the largest "
             "reservation touching any row in scope is 3 and the minimum's margin is %s, "
             "so an agent reading either column gets the same answer."
             % _fmt(spec["margin"])),
            ("Both UI paths write the same fields: ProductEdit's Save sets qty, "
             "salable_quantity and is_in_stock (ProductEdit.jsx:311, :351-353) and the "
             "grid's bulk Update attributes sets qty + salable_quantity and, when chosen, "
             "is_in_stock (ProductGrid.jsx:491, :496). The rubric therefore asserts all "
             "three and is path-independent."),
            (("The rubric is a SINGLE exact-collection component worth 1.0: the target "
              "row's resulting tuple (qty, salable_quantity, is_in_stock) must equal "
              "(%s, %s, 1). The stock flag is folded in rather than scored separately "
              "because this row is already in stock, and a standalone flag component "
              "would be satisfied by an agent that did nothing (TASK4 S3.2). The "
              "accepted set is unchanged; only the partial-credit rung is gone, which "
              "makes it strictly stricter."
              % (_fmt(spec["expected_qty"]), _fmt(spec["expected_qty"])))
             if spec["single"] else
             ("Two paid components: 0.6 for the resulting quantity and 0.4 for the "
              "stock flag having MOVED from 0 to 1. The flag is paid separately only "
              "because on this arm the agent has to change it; the component is gated "
              "on the quantity component so it cannot pay on an untouched session.")),
            ("Scope is expressed as a GATE over the rest of the %s line, never as a paid "
             "component (CORRECTIONS #84/#110): a sweep across the family scores 0.0 "
             "rather than a docked partial, and nothing pays for restraint."
             % task["family_label"]),
        ]

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": spec["instruction"],
            "apps": [{
                "name": APP_DIR,
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
                "shape": task["shape"],
                "skills": ["R5", "A13"],
                "skill_chain": (
                    "filter the Products grid to one colour slice of the %s size/colour "
                    "matrix and read off the size carrying the least stock -> add the "
                    "delivery to that row's quantity and, only if it held nothing, also "
                    "flip its Stock Status to In Stock" % task["family_label"]),
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "topic": "conditional_restock_stock_status",
                "lane": "conditional_restock_stock_status",
                "batch": "batch-6 lane 46 (shopping_admin / R5 -> A13)",
                "surface": ("/admin/catalog/product/ filters panel ([name=\"sku\"], "
                            "[name=\"color\"]) -> row Edit link -> "
                            "/admin/catalog/product/edit/id/%d/ Quantity and Stock Status"
                            % spec["target_id"]),
                "inspiration_ids": ["webarena-768", "webarena-769", "webarena-770",
                                    "webarena-501", "webarena-504"],
                "authoring_notes": notes,
                "hard_criteria": [],
                "has_initial_setup": has_setup,
                "injected_preconditions": injected,
            },
        }
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
            fh.write("\n")

        reward_src = reward_py(spec)
        nemo_src = nemo_reward_py(spec)
        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_src)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_src)

        setup_src = setup_py(spec) if has_setup else None
        if setup_src is not None:
            with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        row = {"task_payload": {
            "task_id": tid,
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
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": nemo_src,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        rows.append(row)

        with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as fh:
            fh.write(replay_py(spec))

        index["tasks"].append({"task_id": tid, "path": "../../%s/task.json" % tid})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    for spec in specs:
        words = len(spec["instruction"].split())
        print("%-64s %-9s %-8s arm=%-8s target=%-5d %s -> %s  margin=%s  words=%d"
              % (spec["task_id"], spec["task"]["style"], spec["task"]["shape"],
                 spec["arm"], spec["target_id"], _fmt(spec["prior_qty"]),
                 _fmt(spec["expected_qty"]), _fmt(spec["margin"]), words))


main()
