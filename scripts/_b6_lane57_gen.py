#!/usr/bin/env python3
"""Batch-6 lane 57 generator - shopping_admin R9 -> A6 (named product -> variant wizard).

Writes ten bundles under output/tasks/shopping_admin/<task_id>/ plus the batch
directory output/tasks/shopping_admin/_batches/named_product_variant_wizard/.

Every value below was read out of
hub/websites/webarena_shopping_admin_mock/src/data/products.json and
productAttributes.json; see GENERATION.md for the mechanism citations.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE_DIR = os.path.join(ROOT, "output", "tasks", "shopping_admin")
BATCH_DIR = os.path.join(SITE_DIR, "_batches", "named_product_variant_wizard")
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

SIZE = {
    "XS": 166, "S": 167, "M": 168, "L": 169, "XL": 170,
    "28": 171, "29": 172, "30": 173, "31": 174, "32": 175,
    "33": 176, "34": 177, "36": 178, "38": 179,
}
COLOR = {
    "Black": 49, "Blue": 50, "Brown": 51, "Gray": 52, "Green": 53,
    "Lavender": 54, "Multi": 55, "Orange": 56, "Purple": 57, "Red": 58,
    "White": 59, "Yellow": 60,
}

ANALOGUE_SIZES = "Add new size 30 and 31 to all color variants of Diana Tights"
ANALOGUE_COLOR_S = "Add a new color option brown to the size S of Phoebe Zipper Sweatshirt"
ANALOGUE_COLOR_SM = "Add a new color blue to size S and M of Frankie Sweatshirt"
ANALOGUE_XXS = "Add a new size XXS to blue and purple Nona Fitness Tank"


def combos(parent_name, parent_sku, sizes, colors, price, qty, attr_set):
    """Expected generated children, in the wizard's own naming convention."""
    rows = []
    for s in sizes:
        for c in colors:
            rows.append({
                "sku_size_first": "%s-%s-%s" % (parent_sku, s, c),
                "sku_color_first": "%s-%s-%s" % (parent_sku, c, s),
                "name_size_first": "%s-%s-%s" % (parent_name, s, c),
                "name_color_first": "%s-%s-%s" % (parent_name, c, s),
                "size": SIZE[s],
                "color": COLOR[c],
                "price": price,
                "qty": qty,
                "status": 1,
                "type_id": "simple",
                "attribute_set_id": attr_set,
            })
    return rows


# Seeded axes per parent, read from products.json: the option ids openWizard
# pre-ticks (ProductEdit.jsx:521-535). The replay must leave these ticked.
SEED_AXES = {
    "1826": {"size": ["28", "29"], "color": ["Blue", "Purple", "Red"]},
    "1935": {"size": ["28", "29", "30", "31", "32"], "color": ["Gray", "Orange", "Yellow"]},
    "815": {"size": ["32", "33", "34", "36"], "color": ["Black", "Blue", "Purple"]},
    "937": {"size": ["32", "33", "34", "36"], "color": ["Black", "Blue", "Gray"]},
    "1896": {"size": ["28", "29"], "color": ["Blue", "Gray", "Green"]},
    "763": {"size": ["32", "33", "34", "36"], "color": ["Blue", "Green", "Red"]},
    "94": {"size": ["XS", "S", "M", "L", "XL"], "color": ["Black", "Blue", "Green"]},
    "1875": {"size": ["28", "29"], "color": ["Black", "Blue", "Purple"]},
    "142": {"size": ["XS", "S", "M", "L", "XL"], "color": ["Black", "Blue", "Purple"]},
    "1983": {"size": ["28", "29", "30", "31", "32"], "color": ["Blue", "Purple", "Yellow"]},
}

TASKS = []


def add(task_id, instruction, style, shape, parent_id, parent_sku, parent_name,
        seeded_children, expected, criteria, notes, analogues, derived_from,
        injection=None, ref=None):
    TASKS.append({
        "task_id": task_id,
        "instruction": instruction,
        "style": style,
        "shape": shape,
        "parent_id": str(parent_id),
        "parent_sku": parent_sku,
        "parent_name": parent_name,
        "seeded_children": seeded_children,
        "expected": expected,
        "criteria": criteria,
        "notes": notes,
        "analogues": analogues,
        "derived_from": derived_from,
        "injection": injection,
        "ref": ref,
    })


# --------------------------------------------------------------------------- 001
add(
    "named_product_variant_wizard_emma_next_size_up_001",
    "Emma Leggings (WP02) tops out at its largest waist size. Extend it one "
    "step up - the next waist value the Size attribute offers - in every "
    "colour it already runs, at the line's usual price and stock.",
    "terse", "mutation",
    1826, "WP02", "Emma Leggings",
    [1820, 1821, 1822, 1823, 1824, 1825],
    combos("Emma Leggings", "WP02", ["30"], ["Blue", "Purple", "Red"], 42.0, 100.0, 10),
    [
        "newProducts holds exactly three generated rows: WP02-30-Blue, WP02-30-Purple and "
        "WP02-30-Red, each simple, attribute set 10, size option 173, price 42.00, quantity 100, "
        "status 1.",
        "productOverrides['1826'].configurable_children is exactly {1820..1825} plus the three "
        "generated entity ids, with configurable_attributes still size and color.",
    ],
    [
        "R9: the pant runs 28 and 29 only; the next waist value on Size (attribute 144) above 29 "
        "is 30 (option id 173). An agent that guesses 31 or XL scores 0.0.",
        "A6: Configurations wizard, price/quantity left on Skip so the rows inherit the sibling's "
        "42.00 / 100 (ProductEdit.jsx:605-610).",
    ],
    [ANALOGUE_SIZES],
    "tights_size_matrix_aeon_capri_size30_001",
)

# --------------------------------------------------------------------------- 002
add(
    "named_product_variant_wizard_maxima_size_above_run_002",
    "Maxima Drawstring Short (WSH02) needs one more waist size on top of the "
    "run it already carries - the next value up in the Size attribute. "
    "Generate it in all three of its colours, at the usual price and stock.",
    "terse", "mutation",
    1935, "WSH02", "Maxima Drawstring Short",
    [1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929,
     1930, 1931, 1932, 1933, 1934],
    combos("Maxima Drawstring Short", "WSH02", ["33"], ["Gray", "Orange", "Yellow"],
           28.0, 100.0, 10),
    [
        "newProducts holds exactly WSH02-33-Gray, WSH02-33-Orange and WSH02-33-Yellow, each "
        "simple, attribute set 10, size option 176, price 28.00, quantity 100, status 1.",
        "productOverrides['1935'].configurable_children is exactly the fifteen seeded ids plus "
        "the three generated ids.",
    ],
    [
        "R9: the short runs 28-32; the next Size value above 32 is 33 (option 176). 34/36/38 all "
        "exist as options, so only reading the run gives the answer.",
    ],
    [ANALOGUE_SIZES],
    "tights_size_matrix_fiona_size33_priced_006",
)

# --------------------------------------------------------------------------- 003
add(
    "named_product_variant_wizard_thorpe_size_below_run_003",
    "Thorpe Track Pant (MP07) starts at its smallest stocked waist. Add the "
    "next waist size down that the Size attribute offers, in each colour the "
    "pant comes in, keeping the line's price and stock.",
    "terse", "mutation",
    815, "MP07", "Thorpe Track Pant",
    [803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814],
    combos("Thorpe Track Pant", "MP07", ["31"], ["Black", "Blue", "Purple"], 68.0, 100.0, 10),
    [
        "newProducts holds exactly MP07-31-Black, MP07-31-Blue and MP07-31-Purple, each simple, "
        "attribute set 10, size option 174, price 68.00, quantity 100, status 1.",
        "productOverrides['815'].configurable_children is exactly {803..814} plus the three "
        "generated ids.",
    ],
    [
        "R9: the pant runs 32/33/34/36; the Size option immediately below 32 is 31 (option 174). "
        "The downward direction is what makes it a read rather than a guess - 28/29/30 also exist.",
    ],
    [ANALOGUE_SIZES],
    None,
)

# --------------------------------------------------------------------------- 004
add(
    "named_product_variant_wizard_hawkeye_top_of_size_run_004",
    "Hawkeye Yoga Short (MSH05) is going one size bigger. Generate the next "
    "waist value the Size attribute lists above the largest it stocks today, "
    "in every colour it already offers, at the usual price and quantity.",
    "terse", "mutation",
    937, "MSH05", "Hawkeye Yoga Short",
    [925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936],
    combos("Hawkeye Yoga Short", "MSH05", ["38"], ["Black", "Blue", "Gray"], 29.0, 100.0, 10),
    [
        "newProducts holds exactly MSH05-38-Black, MSH05-38-Blue and MSH05-38-Gray, each simple, "
        "attribute set 10, size option 179, price 29.00, quantity 100, status 1.",
        "productOverrides['937'].configurable_children is exactly {925..936} plus the three "
        "generated ids.",
    ],
    [
        "R9: the short runs 32/33/34/36 and 36 is its largest; the Size attribute has no 37, so "
        "the next listed value is 38 (option 179). An agent assuming +1 lands on a value that "
        "does not exist and cannot generate anything.",
    ],
    [ANALOGUE_SIZES],
    None,
)

# --------------------------------------------------------------------------- 005 (explicit)
add(
    "named_product_variant_wizard_deirdre_two_sizes_up_005",
    "Deirdre Relaxed-Fit Capri (WP12) is only stocked in its two smallest "
    "waist sizes. Open the product's Configurations wizard and generate the "
    "next two waist values the Size attribute lists above the largest it "
    "currently carries, in each of the three colours the capri already comes "
    "in. Leave the wizard's bulk price and quantity steps on Skip so the six "
    "new variants inherit the line's $63.00 and 100 units, and leave the six "
    "existing variants exactly as they are.",
    "explicit", "mutation",
    1896, "WP12", "Deirdre Relaxed-Fit Capri",
    [1890, 1891, 1892, 1893, 1894, 1895],
    combos("Deirdre Relaxed-Fit Capri", "WP12", ["30", "31"], ["Blue", "Gray", "Green"],
           63.0, 100.0, 10),
    [
        "newProducts holds exactly the six rows WP12-{30,31}-{Blue,Gray,Green}, each simple, "
        "attribute set 10, price 63.00, quantity 100, status 1, size options 173 and 174.",
        "productOverrides['1896'].configurable_children is exactly {1890..1895} plus the six "
        "generated ids.",
    ],
    [
        "R9: reads the capri's run (28, 29) and the Size option list; the two values above 29 are "
        "30 and 31.",
        "Explicit style states the wizard route and the Skip radios, but never the two sizes.",
    ],
    [ANALOGUE_SIZES],
    "tights_size_matrix_karmen_run_30_31_002",
)

# --------------------------------------------------------------------------- 006
add(
    "named_product_variant_wizard_geo_two_sizes_below_006",
    "Geo Insulated Jogging Pant (MP03) is being extended downwards by two "
    "waist sizes - the two Size values immediately below the smallest it "
    "stocks. Generate them in all three colours, price and stock unchanged.",
    "terse", "mutation",
    763, "MP03", "Geo Insulated Jogging Pant",
    [751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762],
    combos("Geo Insulated Jogging Pant", "MP03", ["30", "31"], ["Blue", "Green", "Red"],
           51.0, 100.0, 10),
    [
        "newProducts holds exactly the six rows MP03-{30,31}-{Blue,Green,Red}, each simple, "
        "attribute set 10, price 51.00, quantity 100, status 1.",
        "productOverrides['763'].configurable_children is exactly {751..762} plus the six "
        "generated ids.",
    ],
    [
        "R9: the pant runs 32/33/34/36; the two Size values below 32 are 31 and 30 (174, 173).",
    ],
    [ANALOGUE_SIZES],
    None,
)

# --------------------------------------------------------------------------- 007 (explicit, rw)
add(
    "named_product_variant_wizard_bruno_red_at_teton_price_007",
    "Bruno Compete Hoodie (MH03) comes in black, blue and green today. Using "
    "the product's Configurations wizard, generate a red variant in each of "
    "its five sizes. The red run is being priced to match the Teton Pullover "
    "Hoodie (MH02), so look that price up and apply it as a single price to "
    "all of the new SKUs; leave the quantity step on Skip. The fifteen "
    "existing variants keep their own price.",
    "explicit", "retrieval_writeback",
    94, "MH03", "Bruno Compete Hoodie",
    [79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93],
    combos("Bruno Compete Hoodie", "MH03", ["XS", "S", "M", "L", "XL"], ["Red"],
           70.0, 100.0, 9),
    [
        "newProducts holds exactly MH03-{XS,S,M,L,XL}-Red, each simple, attribute set 9, colour "
        "option 58, quantity 100, status 1, and price 70.00 - the MH02 price, not MH03's own "
        "63.00.",
        "productOverrides['94'].configurable_children is exactly {79..93} plus the five "
        "generated ids.",
    ],
    [
        "R9: MH02 Teton Pullover Hoodie is priced 70.00 on the parent row and on all fifteen of "
        "its children, so the lookup has a single answer. Margin against the wizard default "
        "(MH03's own 63.00) is $7.00, so an agent that skips the lookup scores 0.0.",
    ],
    [ANALOGUE_COLOR_SM],
    None,
)

# --------------------------------------------------------------------------- 008 (terse, rw)
add(
    "named_product_variant_wizard_carina_green_at_cora_price_008",
    "Carina Basic Capri (WP09) is adding a green run in both of its waist "
    "sizes. Price the two new variants to match Cora Parachute Pant (WP04) "
    "and leave their stock at the level the rest of the line runs.",
    "terse", "retrieval_writeback",
    1875, "WP09", "Carina Basic Capri",
    [1869, 1870, 1871, 1872, 1873, 1874],
    combos("Carina Basic Capri", "WP09", ["28", "29"], ["Green"], 75.0, 100.0, 10),
    [
        "newProducts holds exactly WP09-28-Green and WP09-29-Green, simple, attribute set 10, "
        "colour option 53, quantity 100, status 1, price 75.00 - Cora's price, not Carina's 51.00.",
        "productOverrides['1875'].configurable_children is exactly {1869..1874} plus the two "
        "generated ids.",
    ],
    [
        "R9: WP04 Cora Parachute Pant is 75.00 on the parent and on all six children. Margin "
        "against the wizard default (51.00) is $24.00.",
    ],
    [ANALOGUE_COLOR_S],
    None,
)

# --------------------------------------------------------------------------- 009 (terse, rw, inj)
add(
    "named_product_variant_wizard_stark_white_match_stock_009",
    "Stark Fundamental Hoodie (MH06) is adding a white run. Create the white "
    "variant for every size it stocks, holding the same number of units the L "
    "Purple is carrying today, and at the line's usual price.",
    "terse", "retrieval_writeback",
    142, "MH06", "Stark Fundamental Hoodie",
    [127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141],
    combos("Stark Fundamental Hoodie", "MH06", ["XS", "S", "M", "L", "XL"], ["White"],
           42.0, 45.0, 9),
    [
        "newProducts holds exactly MH06-{XS,S,M,L,XL}-White, simple, attribute set 9, colour "
        "option 59, price 42.00, status 1, and quantity 45 - the injected MH06-L-Purple figure, "
        "not the wizard's inherited 100.",
        "productOverrides['142'].configurable_children is exactly {127..141} plus the five "
        "generated ids.",
        "productOverrides['138'] still records quantity 45 (the injected precondition is not "
        "disturbed).",
    ],
    [
        "R9: quantity is read off the Current Variations row for MH06-L-Purple, which the "
        "injection puts at 45 while every other variant sits at 100. Margin 55 units.",
        "The wizard's sibling default is variants[0] = 127 (XS-Black, qty 100), so Skip scores "
        "0.0 (ProductEdit.jsx:599, 605-610).",
    ],
    [ANALOGUE_COLOR_SM],
    "tights_size_matrix_mimi_size30_and_retire_010",
    injection={"product_id": "138", "sku": "MH06-L-Purple", "qty": 45.0},
    ref={"product_id": "138", "qty": 45.0},
)

# --------------------------------------------------------------------------- 010 (explicit, rw, inj)
add(
    "named_product_variant_wizard_bess_gray_match_stock_010",
    "Bess Yoga Short (WSH05) is picking up a gray run. Using the "
    "Configurations wizard, generate a gray variant for each of the five "
    "waist sizes it already offers. Stock every new variant with the same "
    "quantity the 31 Purple shows in the variations table, applying it as a "
    "single quantity to all of the new SKUs, and leave the price step on Skip "
    "so they inherit the line's $28.00. The fifteen existing variants stay as "
    "they are.",
    "explicit", "retrieval_writeback",
    1983, "WSH05", "Bess Yoga Short",
    [1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977,
     1978, 1979, 1980, 1981, 1982],
    combos("Bess Yoga Short", "WSH05", ["28", "29", "30", "31", "32"], ["Gray"],
           28.0, 60.0, 10),
    [
        "newProducts holds exactly WSH05-{28,29,30,31,32}-Gray, simple, attribute set 10, colour "
        "option 52, price 28.00, status 1, and quantity 60 - the injected WSH05-31-Purple figure, "
        "not the inherited 100.",
        "productOverrides['1983'].configurable_children is exactly {1968..1982} plus the five "
        "generated ids.",
        "productOverrides['1978'] still records quantity 60.",
    ],
    [
        "R9: WSH05-31-Purple is injected at 60 units; every other variant is 100. Margin 40 units.",
        "Sibling default is variants[0] = 1968 (28-Blue, qty 100), so a Skip run scores 0.0.",
    ],
    [ANALOGUE_XXS],
    None,
    injection={"product_id": "1978", "sku": "WSH05-31-Purple", "qty": 60.0},
    ref={"product_id": "1978", "qty": 60.0},
)


# --------------------------------------------------------------------------- codegen

REWARD_BODY = '''
COMPONENT_WEIGHTS = {
    "variants_generated": 0.65,
    "parent_matrix_updated": 0.35,
}

COMPONENT_DETAILS = {
    "variants_generated": __DETAIL_VARIANTS__,
    "parent_matrix_updated": __DETAIL_PARENT__,
}

PARENT_ID = __PARENT_ID__
SEEDED_CHILDREN = set(json.loads(r"""__SEEDED__"""))
EXPECTED = json.loads(r"""__EXPECTED__""")
REF_ID = __REF_ID__
REF_QTY = __REF_QTY__


def _rows(value):
    if isinstance(value, list):
        return [r for r in value if isinstance(r, dict)]
    return []


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
    n = _num(value)
    if n is None:
        return None
    return int(round(n))


def _txt(value):
    if isinstance(value, str):
        return value.strip()
    return ""


def _scope_ok(state):
    """Gate, never a paid component: the run must not have deleted products, and
    an injected reference row must still hold the figure the task derives from."""
    deleted = state.get("deletedProductIds")
    if deleted is None:
        deleted = []
    if not isinstance(deleted, list) or len(deleted) > 0:
        return False
    if REF_ID is not None:
        overrides = state.get("productOverrides")
        if not isinstance(overrides, dict):
            return False
        patch = overrides.get(REF_ID)
        if not isinstance(patch, dict):
            return False
        qty = _num(patch.get("qty"))
        if qty is None or abs(qty - REF_QTY) > 0.0005:
            return False
    return True


def _variants_ok(state):
    """newProducts is EXACTLY the expected generated collection."""
    created = _rows(state.get("newProducts"))
    if len(created) != len(EXPECTED):
        return False, []
    want = {}
    for spec in EXPECTED:
        want[(int(spec["size"]), int(spec["color"]))] = spec
    ids = []
    seen = set()
    for row in created:
        key = (_int(row.get("size")), _int(row.get("color")))
        spec = want.get(key)
        if spec is None or key in seen:
            return False, []
        seen.add(key)
        sku = _txt(row.get("sku"))
        if sku not in (spec["sku_size_first"], spec["sku_color_first"]):
            return False, []
        name = _txt(row.get("name"))
        if name not in (spec["name_size_first"], spec["name_color_first"]):
            return False, []
        price = _num(row.get("price"))
        if price is None or abs(price - float(spec["price"])) > 0.005:
            return False, []
        qty = _num(row.get("qty"))
        if qty is None or abs(qty - float(spec["qty"])) > 0.0005:
            return False, []
        if _int(row.get("status")) != int(spec["status"]):
            return False, []
        if _txt(row.get("type_id")) != spec["type_id"]:
            return False, []
        if _int(row.get("attribute_set_id")) != int(spec["attribute_set_id"]):
            return False, []
        entity_id = _int(row.get("entity_id"))
        if entity_id is None:
            return False, []
        ids.append(entity_id)
    if len(set(ids)) != len(EXPECTED):
        return False, []
    if set(ids) & SEEDED_CHILDREN:
        return False, []
    return True, ids


def _parent_ok(state, new_ids):
    if not new_ids:
        return False
    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        return False
    patch = overrides.get(PARENT_ID)
    if not isinstance(patch, dict):
        return False
    children = patch.get("configurable_children")
    if not isinstance(children, list):
        return False
    resolved = set()
    for child in children:
        value = _int(child)
        if value is None:
            return False
        resolved.add(value)
    if len(children) != len(resolved):
        return False
    if resolved != SEEDED_CHILDREN | set(new_ids):
        return False
    attributes = patch.get("configurable_attributes")
    if attributes is None:
        attributes = ["size", "color"]
    if not isinstance(attributes, list):
        return False
    if set(_txt(a) for a in attributes) != set(["size", "color"]):
        return False
    return True


def score_state(state):
    if not isinstance(state, dict):
        state = {}
    scope = _scope_ok(state)
    variants_ok, new_ids = _variants_ok(state)
    checks = {
        "variants_generated": bool(scope and variants_ok),
        "parent_matrix_updated": bool(scope and variants_ok and _parent_ok(state, new_ids)),
    }
    components = []
    total = 0.0
    for name in ("variants_generated", "parent_matrix_updated"):
        value = COMPONENT_WEIGHTS[name] if checks[name] else 0.0
        total += value
        components.append({
            "name": name,
            "score": value,
            "details": COMPONENT_DETAILS[name],
        })
    return round(total, 6), components
'''

REWARD_HEADER = '''"""Deterministic offline reward for __TASK_ID__.

Reads current_state only; nothing is diffed against initial_state. The rubric asserts the
EXACT resulting collection of generated variants for the __PARENT_NAME__ configurable parent,
so an over-generated matrix, a wrong option value, a wrong price or a wrong quantity all score
0.0 rather than partial credit, and an untouched state scores 0.0 because newProducts is empty.

_scope_ok is a GATE on both paid components, never a component of its own: nothing is paid for
leaving records alone, and everything is lost for disturbing them.
"""

import json
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

NEMO_HEADER = '''"""NeMo-Gym reward program for __TASK_ID__.

Same rubric as reward.py. Reads current_state from GET /go?sid=... and prints
REWARD: <float> on every output path. Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"
'''

NEMO_TAIL = '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        payload = response.json()
        state = payload.get("current_state")
        if not isinstance(state, dict):
            state = {}
        score, components = score_state(state)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write("reward error: %s\\n" % (exc,))
        print("REWARD: 0.0")
        return
    for component in components:
        sys.stderr.write("%s: %s\\n" % (component["name"], component["score"]))
    print("REWARD: %s" % (score,))


main()
'''

SETUP_TEMPLATE = '''"""NeMo-Gym initial setup for __TASK_ID__.

Injects the precondition the retrieval reads: __SKU__ is put on __QTY__ units while
every other variant of the line stays at 100, so the quantity the new variants must
carry exists on the page and is not the wizard's inherited default.

Read-modify-write: GET /go, mutate the whole document, POST it back. Correct whether
the mock merges or replaces a partial set.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

PRODUCT_ID = "__PRODUCT_ID__"
PATCH = json.loads(r"""__PATCH__""")


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        sys.stderr.write("setup error: /go returned neither current_state nor initial_state\\n")
        raise SystemExit(1)

    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        overrides = {}
    existing = overrides.get(PRODUCT_ID)
    if not isinstance(existing, dict):
        existing = {}
    merged = dict(existing)
    merged.update(PATCH)
    overrides[PRODUCT_ID] = merged
    state["productOverrides"] = overrides

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    posted.raise_for_status()
    print("setup ok: productOverrides[%s] = %s" % (PRODUCT_ID, json.dumps(PATCH)))


main()
'''

REPLAY_TEMPLATE = '''"""Golden replay DRAFT - __TASK_ID__

Not executed during authoring. start_path is "/", and every control below is reached by
clicking rendered links and buttons only: no page.goto() after the initial landing, no
constructed URL.

Route from the landing page:
  left rail  Catalog -> Products
  grid       "Search by keyword" -> type "__SEARCH__" -> Enter
             (product_listing pages at 200 rows, so the parent is on page 1)
  grid row   click Edit on the row whose Type reads "Configurable Product" (SKU __PARENT_SKU__)
  form       scroll to the "Configurations" section
  button     #configurable_products_button ("Edit Configurations") opens
             div.modal-slide._show[data-role="configurable-wizard"]

Retrieval performed before the wizard:
__RETRIEVAL__

Wizard, in order:
  step 1  Size and Color arrive pre-ticked from the parent's configurable_attributes
          (openWizard, ProductEdit.jsx:521-535). Press #wizard_next.
  step 2  tick input[name="configurable[size][]"] / input[name="configurable[color][]"] by
          value (the value attribute IS the option_id) so exactly the sets below are ticked.
          Press #wizard_next.
  step 3  __STEP3__
          Press #wizard_next.
  step 4  the summary lists the pending combinations only. Press #generate_configurations.

Expected banner: "Product Configurations. __N__ product(s) have been generated."
"""

START_PATH = "/"

SIZE_VALUES_TO_TICK = __SIZES__     # option ids, existing run plus anything new
COLOR_VALUES_TO_TICK = __COLORS__   # option ids

EXPECTED_NEW_SKUS = __SKUS__

NOTES = __NOTES__
'''


def render(template, mapping):
    out = template
    for key, value in mapping.items():
        out = out.replace(key, value)
    return out


def build_reward(task, nemo):
    detail_variants = json.dumps(
        "newProducts holds exactly the expected generated variants for %s: right size and colour "
        "option ids, SKU, name, price, quantity, status, type and attribute set."
        % task["parent_name"])
    detail_parent = json.dumps(
        "productOverrides['%s'].configurable_children is exactly the seeded children plus the "
        "newly generated ids, with configurable_attributes still size and color."
        % task["parent_id"])
    ref = task["ref"]
    body = render(REWARD_BODY, {
        "__DETAIL_VARIANTS__": detail_variants,
        "__DETAIL_PARENT__": detail_parent,
        "__PARENT_ID__": json.dumps(task["parent_id"]),
        "__SEEDED__": json.dumps(task["seeded_children"], indent=2),
        "__EXPECTED__": json.dumps(task["expected"], indent=2),
        "__REF_ID__": json.dumps(ref["product_id"]) if ref else "None",
        "__REF_QTY__": repr(float(ref["qty"])) if ref else "None",
    })
    if nemo:
        head = render(NEMO_HEADER, {"__TASK_ID__": task["task_id"]})
        return head + body + NEMO_TAIL
    head = render(REWARD_HEADER, {
        "__TASK_ID__": task["task_id"],
        "__PARENT_NAME__": task["parent_name"],
    })
    return head + body + REWARD_TAIL


def build_setup(task):
    inj = task["injection"]
    patch = {"qty": inj["qty"], "salable_quantity": inj["qty"]}
    return render(SETUP_TEMPLATE, {
        "__TASK_ID__": task["task_id"],
        "__SKU__": inj["sku"],
        "__QTY__": str(int(inj["qty"])),
        "__PRODUCT_ID__": inj["product_id"],
        "__PATCH__": json.dumps(patch, indent=2),
    })


def build_replay(task):
    sizes = sorted({int(r["size"]) for r in task["expected"]})
    colors = sorted({int(r["color"]) for r in task["expected"]})
    axes = SEED_AXES[task["parent_id"]]
    seeded_sizes = [SIZE[s] for s in axes["size"]]
    seeded_colors = [COLOR[c] for c in axes["color"]]
    tick_sizes = sorted(set(sizes) | set(seeded_sizes))
    tick_colors = sorted(set(colors) | set(seeded_colors))
    if task["injection"]:
        retrieval = ("  read the Quantity cell of %s in the Current Variations table on this same\n"
                     "  page (the injected figure; every other row reads 100)."
                     % task["injection"]["sku"])
    elif task["shape"] == "retrieval_writeback":
        retrieval = ("  open Catalog > Products in a fresh search for the reference product named in\n"
                     "  the instruction, read its Price column, then come back to this parent.")
    else:
        retrieval = ("  read the Size values already used in the Current Variations table, and the\n"
                     "  full Size option list rendered by wizard step 2, to fix the value to add.")
    price_mode = "leave both radios on Skip (the default)."
    if task["shape"] == "retrieval_writeback" and not task["injection"]:
        price_mode = ('choose "Apply single price to all SKUs" and type the looked-up price into\n'
                      '          input[name="bulk[price][value]"]; leave Quantity on Skip.')
    elif task["injection"]:
        price_mode = ('leave Price on Skip; choose "Apply single quantity to each SKUs" and type the\n'
                      '          looked-up quantity into input[name="bulk[qty][value]"].')
    return render(REPLAY_TEMPLATE, {
        "__TASK_ID__": task["task_id"],
        "__SEARCH__": task["parent_name"],
        "__PARENT_SKU__": task["parent_sku"],
        "__RETRIEVAL__": retrieval,
        "__STEP3__": price_mode,
        "__N__": str(len(task["expected"])),
        "__SIZES__": json.dumps(tick_sizes),
        "__COLORS__": json.dumps(tick_colors),
        "__SKUS__": json.dumps([r["sku_size_first"] for r in task["expected"]], indent=4),
        "__NOTES__": json.dumps(task["notes"], indent=4),
    })


def build_task_json(task):
    meta = {
        "style": task["style"],
        "difficulty": "medium",
        "shape": task["shape"],
        "skills": ["R9", "A6"],
        "skill_chain": (
            "look the named configurable product up and read the attribute the payload is "
            "derived from -> drive the Configurations wizard to generate exactly the missing "
            "option-value combinations"),
        "derived_from": task["derived_from"],
        "official_analogues": task["analogues"],
        "topic": "shopping_admin named product -> variant wizard",
        "inspiration_ids": ["webarena-547", "webarena-548", "webarena-550", "webarena-551"],
        "authoring_notes": task["notes"] + [
            "Wizard persistence verified in source: generateConfigurations "
            "(ProductEdit.jsx:596-650) calls addProduct (AppContext.jsx:236-238 -> "
            "state.newProducts) and patchProduct (AppContext.jsx:218-227 -> "
            "state.productOverrides[<parent>]); the Current Variations table reads them back "
            "through getProducts (selectors.js:164-180) and getProduct (selectors.js:154-162) "
            "via allProducts (ProductEdit.jsx:102) and variants (:486-488).",
            "pendingCombos (ProductEdit.jsx:560-572) filters out combinations that already "
            "exist, and the requested combination is absent from the seed, so an untouched "
            "state scores 0.0 and the action cannot be already satisfied.",
        ],
    }
    if task["injection"]:
        meta["injected_preconditions"] = [
            "productOverrides['%s'] sets qty and salable_quantity of %s to %s (the bulk "
            "attribute-update convention, ProductGrid.jsx:491), so the derived quantity exists "
            "on the page and differs from the wizard's inherited 100."
            % (task["injection"]["product_id"], task["injection"]["sku"],
               int(task["injection"]["qty"]))
        ]
    return {
        "schema_version": 2,
        "task_id": task["task_id"],
        "instruction": task["instruction"],
        "apps": [{
            "name": "webarena_shopping_admin_mock",
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
        "metadata": meta,
    }


def main():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []
    for task in TASKS:
        d = os.path.join(SITE_DIR, task["task_id"])
        os.makedirs(d, exist_ok=True)

        with open(os.path.join(d, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": task["task_id"],
                "task_instruction": task["instruction"],
                "app_dir": "webarena_shopping_admin_mock",
                "start_path": "/",
                "difficulty": "medium",
                "success_criteria": task["criteria"],
            }, fh, indent=2)
            fh.write("\n")

        with open(os.path.join(d, "task.json"), "w") as fh:
            json.dump(build_task_json(task), fh, indent=2)
            fh.write("\n")

        reward = build_reward(task, nemo=False)
        with open(os.path.join(d, "reward.py"), "w") as fh:
            fh.write(reward)
        nemo_reward = build_reward(task, nemo=True)
        with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward)

        setup_src = None
        if task["injection"]:
            setup_src = build_setup(task)
            with open(os.path.join(d, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        row = {"task_payload": {
            "task_id": task["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_shopping_admin_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task["task_id"],
                "app_dir": "webarena_shopping_admin_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward,
            },
        }}
        with open(os.path.join(d, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        rows.append(row)

        with open(os.path.join(REPLAY_DIR, task["task_id"] + ".py"), "w") as fh:
            fh.write(build_replay(task))

        index["tasks"].append({"task_id": task["task_id"],
                               "path": "../../%s/task.json" % task["task_id"]})

    with open(os.path.join(BATCH_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
