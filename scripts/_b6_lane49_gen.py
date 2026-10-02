#!/usr/bin/env python3
"""Batch-6 lane 49 generator: shopping_admin R6 -> A6.

Ten all-medium bundles. Retrieval: find the configurable family by text search
inside injected content (a pending product review, or the storefront Search
Terms log). Action: extend that family's size x colour matrix through the
Configurations wizard.

Verified mechanism (read-only, hub source):
  * ProductEdit.jsx:591  generateConfigurations()
      -> AppContext.jsx:236 addProduct   writes state.newProducts
      -> AppContext.jsx:219 patchProduct writes state.productOverrides[parent]
  * readers: selectors.js:164-178 getProducts (newProducts + productOverrides),
             selectors.js:154-161 getProduct (parent's configurable_children),
             ProductEdit.jsx:485-487 `variants` renders that same list.
  * persistence: AppContext.jsx:167-174 setState -> dataManager saveState
                 -> /post?action=set_current.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOCK = ROOT / "hub/websites/webarena_shopping_admin_mock"
OUT = ROOT / "output/tasks/shopping_admin"
BATCH = OUT / "_batches/family_variant_matrix_extend"

APP_DIR = "webarena_shopping_admin_mock"
URL_TOKEN = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

PRODUCTS = json.loads((MOCK / "src/data/products.json").read_text())
BY_ID = {p["entity_id"]: p for p in PRODUCTS}
AO = json.loads((MOCK / "src/data/attributeOptions.json").read_text())
SIZE = {int(k): v for k, v in AO["size"].items()}
COLOR = {int(k): v for k, v in AO["color"].items()}
SIZE_ID = {v: k for k, v in SIZE.items()}
COLOR_ID = {v: k for k, v in COLOR.items()}

ANALOGUE_MATRIX_SIZE = "Add new size 30 and 31 to all color variants of Diana Tights"
ANALOGUE_MATRIX_COLOR = "Add a new color option brown to the size S of Phoebe Zipper Sweatshirt"
ANALOGUE_MATRIX_COLOR2 = "Add a new color blue to size S and M of Frankie Sweatshirt"
ANALOGUE_MATRIX_SIZE2 = "Add a new size XXS to blue and purple Nona Fitness Tank"
ANALOGUE_REVIEW = (
    'Tell me the the number of reviews that our store received by far that '
    'mention term "disappointed"'
)
ANALOGUE_SEARCH = "Get the top 1 search term(s) in my store"
ANALOGUE_SEARCH2 = "Get the top 3 search terms that match available products in the store."


def family(parent_id):
    parent = BY_ID[parent_id]
    kids = [BY_ID[c] for c in parent["configurable_children"]]
    return parent, kids


def expected_rows(parent_id, add_size=None, add_color=None):
    """The exact rows generateConfigurations() creates for this extension."""
    parent, kids = family(parent_id)
    sibling = kids[0]
    sizes = []
    colors = []
    for k in kids:
        if k["size"] not in sizes:
            sizes.append(k["size"])
        if k["color"] not in colors:
            colors.append(k["color"])
    if add_size is not None:
        new_sizes, new_colors = [SIZE_ID[add_size]], colors
    else:
        new_sizes, new_colors = sizes, [COLOR_ID[add_color]]
    rows = []
    for s in new_sizes:
        for c in new_colors:
            suffix = "%s-%s" % (SIZE[s], COLOR[c])
            rows.append({
                "sku": "%s-%s" % (parent["sku"], suffix),
                "name": "%s-%s" % (parent["name"], suffix),
                "size": s,
                "color": c,
                "price": float(sibling["price"]),
                "qty": float(sibling["qty"]),
                "status": 1,
                "type_id": "simple",
                "attribute_set_id": int(parent["attribute_set_id"]),
            })
    return rows


# --------------------------------------------------------------------------
# The ten tasks. `carrier` is the injected retrieval material.
# --------------------------------------------------------------------------

TASKS = [
    {
        "id": "family_variant_matrix_extend_pending_review_waist_38_geo_001",
        "parent": 763, "add_size": "38",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "A pending review from Deshawn asks us to stock a waist size this line "
            "does not run. Add that size to the product he reviewed, in every colour "
            "the line already comes in."
        ),
        "carrier": "review",
        "review": {
            "review_id": 401,
            "created_at": "2023-04-24 19:12:44",
            "nickname": "Deshawn",
            "title": "Please run a bigger waist",
            "detail": (
                "I wear these joggers all winter and they are the warmest pair I own. "
                "The trouble is that 36 is the biggest waist you make and I need a 38. "
                "Please add a 38 to this line in the colours you already offer."
            ),
            "value": 4,
        },
        "analogues": [ANALOGUE_MATRIX_SIZE, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_pending_review_size_30_emma_002",
        "parent": 1826, "add_size": "30",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "Marisol's review is waiting in the pending queue and asks for a size we "
            "do not currently run. Give the product she reviewed that size in every "
            "colour it already comes in."
        ),
        "carrier": "review",
        "review": {
            "review_id": 402,
            "created_at": "2023-04-24 19:16:02",
            "nickname": "Marisol",
            "title": "One size short of perfect",
            "detail": (
                "These are the only leggings that fit me properly, but the run stops "
                "at a 29. Could you please add a 30? I would happily take it in any of "
                "the colours you already stock."
            ),
            "value": 4,
        },
        "analogues": [ANALOGUE_MATRIX_SIZE, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_pending_review_waist_38_hawkeye_003",
        "parent": 937, "add_size": "38",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "Rudyard has left a pending review asking for a waist we do not stock. "
            "Extend the line he reviewed with that size, in each colour it already "
            "comes in."
        ),
        "carrier": "review",
        "review": {
            "review_id": 403,
            "created_at": "2023-04-24 19:20:31",
            "nickname": "Rudyard",
            "title": "Bigger waist please",
            "detail": (
                "Great short for hot yoga, but the size run stops at 36 and I take a "
                "38. Add a 38 and I will buy one in each colour you already make."
            ),
            "value": 5,
        },
        "analogues": [ANALOGUE_MATRIX_SIZE, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_pending_review_black_gwen_004",
        "parent": 1951, "add_color": "Black",
        "style": "terse", "shape": "derived_target_mutation",
        "instruction": (
            "Priya's pending review asks for a colour we do not make in that line. "
            "Add it to the product she reviewed, in every size the line already runs."
        ),
        "carrier": "review",
        "review": {
            "review_id": 404,
            "created_at": "2023-04-24 19:24:09",
            "nickname": "Priya",
            "title": "Needs a black option",
            "detail": (
                "The fit is spot on and I already own two pairs, but blue, grey and "
                "orange are the only choices. Please make these in black as well, in "
                "the whole size run."
            ),
            "value": 4,
        },
        "analogues": [ANALOGUE_MATRIX_COLOR, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_pending_review_red_bruno_005",
        "parent": 94, "add_color": "Red",
        "style": "terse", "shape": "derived_target_mutation",
        "instruction": (
            "Teodoro's pending review asks for a colour that hoodie line does not come "
            "in. Add it to the product he reviewed, across every size it already runs."
        ),
        "carrier": "review",
        "review": {
            "review_id": 405,
            "created_at": "2023-04-24 19:28:55",
            "nickname": "Teodoro",
            "title": "Where is the red one",
            "detail": (
                "Warmest hoodie in my drawer. My club colour is red though, and you "
                "only sell it in black, blue and green. Please make a red one in every "
                "size you already offer."
            ),
            "value": 4,
        },
        "analogues": [ANALOGUE_MATRIX_COLOR2, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_pending_review_green_arcadio_006",
        "parent": 1015, "add_color": "Green",
        "style": "explicit", "shape": "derived_target_mutation",
        "instruction": (
            "One of the reviews waiting in the Pending Reviews queue was left by "
            "Bernadette, and it asks for a colour we do not currently make in that "
            "line. Open the configurable product her review is about and use its "
            "Configurations wizard to generate that colour in every size the product "
            "already runs. Leave the wizard's bulk price and quantity steps on Skip so "
            "the new variants inherit the line's existing $20.00 price and 100 units of "
            "stock, and do not change any of the twelve variants that are already there."
        ),
        "carrier": "review",
        "review": {
            "review_id": 406,
            "created_at": "2023-04-24 19:33:18",
            "nickname": "Bernadette",
            "title": "Add green to the range",
            "detail": (
                "I bought these for my son's team and they wear green. You only list "
                "black, blue and red. A green version in the same waist run would sell "
                "out here in a week."
            ),
            "value": 5,
        },
        "analogues": [ANALOGUE_MATRIX_COLOR, ANALOGUE_REVIEW],
    },
    {
        "id": "family_variant_matrix_extend_zero_result_query_38_zeppelin_007",
        "parent": 828, "add_size": "38",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "Our busiest storefront search that came back with no results is asking for "
            "a size we do not run. Add that size to the line it names, in every colour "
            "the line already comes in."
        ),
        "carrier": "search_terms",
        "terms": [
            {"query_id": 101, "query_text": "zeppelin yoga pant 38",
             "num_results": 0, "popularity": 24},
            {"query_id": 102, "query_text": "zeppelin yoga pant 34",
             "num_results": 3, "popularity": 31},
        ],
        "analogues": [ANALOGUE_MATRIX_SIZE, ANALOGUE_SEARCH],
    },
    {
        "id": "family_variant_matrix_extend_zero_result_query_33_bess_008",
        "parent": 1983, "add_size": "33",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "The most-used query in the store's search log that returned zero results "
            "wants a size we do not stock. Create it for the line it names, in all of "
            "that line's existing colours."
        ),
        "carrier": "search_terms",
        "terms": [
            {"query_id": 103, "query_text": "bess yoga short size 33",
             "num_results": 0, "popularity": 22},
            {"query_id": 104, "query_text": "bess yoga short size 31",
             "num_results": 5, "popularity": 29},
        ],
        "analogues": [ANALOGUE_MATRIX_SIZE2, ANALOGUE_SEARCH],
    },
    {
        "id": "family_variant_matrix_extend_zero_result_query_gray_thorpe_009",
        "parent": 815, "add_color": "Gray",
        "style": "explicit", "shape": "derived_target_mutation",
        "instruction": (
            "Open the store's Search Terms log. The most-used query there that returned "
            "zero results is asking for a colour we do not currently offer in that pant "
            "line. Open the configurable product the query names and use its "
            "Configurations wizard to generate the missing colour in every size the pant "
            "already runs, leaving the bulk price and quantity steps on Skip so the four "
            "new variants inherit the line's $68.00 price and 100 units of stock. The "
            "twelve existing variants must stay exactly as they are."
        ),
        "carrier": "search_terms",
        "terms": [
            {"query_id": 105, "query_text": "gray thorpe track pant",
             "num_results": 0, "popularity": 26},
            {"query_id": 106, "query_text": "black thorpe track pant",
             "num_results": 12, "popularity": 33},
        ],
        "analogues": [ANALOGUE_MATRIX_COLOR, ANALOGUE_SEARCH2],
    },
    {
        "id": "family_variant_matrix_extend_zero_result_query_purple_artemis_010",
        "parent": 1967, "add_color": "Purple",
        "style": "terse", "shape": "retrieval_writeback",
        "instruction": (
            "The most-used storefront query that returned nothing is after a colour we "
            "do not offer in that line. Generate it for the product the query names, in "
            "every size the line already runs."
        ),
        "carrier": "search_terms",
        "terms": [
            {"query_id": 107, "query_text": "artemis running short purple",
             "num_results": 0, "popularity": 23},
            {"query_id": 108, "query_text": "artemis running short orange",
             "num_results": 15, "popularity": 30},
        ],
        "analogues": [ANALOGUE_MATRIX_COLOR2, ANALOGUE_SEARCH2],
    },
]


# --------------------------------------------------------------------------
# templates
# --------------------------------------------------------------------------

REWARD_BODY = '''
COMPONENT_WEIGHTS = {
    "variants_generated": 0.6,
    "family_matrix_extended": 0.4
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

COMPONENT_DETAILS = {
    "variants_generated": %(detail_a)s,
    "family_matrix_extended": %(detail_b)s
}

PARENT_ID = %(parent_id)r
SEEDED_CHILDREN = json.loads(r"""%(seeded)s""")
EXPECTED = json.loads(r"""%(expected)s""")


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


def _overrides(state):
    value = state.get("productOverrides")
    if isinstance(value, dict):
        return value
    return {}


def _scope_ok(state):
    """Gate, not a paid component: the work stayed inside this one family.

    ANDed into every paid component, so an over-broad sweep scores 0.0 outright
    instead of collecting partial credit for the part it got right.
    """
    deleted = set()
    for value in (state.get("deletedProductIds") or []):
        n = _int(value)
        if n is not None:
            deleted.add(n)
    if deleted & (set(SEEDED_CHILDREN) | set([int(PARENT_ID)])):
        return False
    for key, patch in _overrides(state).items():
        if not isinstance(patch, dict):
            return False
        n = _int(key)
        if n is not None and n in set(SEEDED_CHILDREN):
            return False
        if _txt(key) != PARENT_ID and "configurable_children" in patch:
            return False
    return True


def _variants_ok(state):
    want = {}
    for row in EXPECTED:
        want[row["sku"]] = row
    made = _rows(state.get("newProducts"))
    if sorted(_txt(r.get("sku")) for r in made) != sorted(want):
        return False, []
    ids = []
    for row in made:
        spec = want[_txt(row.get("sku"))]
        if _txt(row.get("name")) != spec["name"]:
            return False, []
        if _int(row.get("size")) != int(spec["size"]):
            return False, []
        if _int(row.get("color")) != int(spec["color"]):
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
    return True, ids


def _parent_ok(state, new_ids):
    if not new_ids:
        return False
    patch = _overrides(state).get(PARENT_ID)
    if not isinstance(patch, dict):
        return False
    children = patch.get("configurable_children")
    if not isinstance(children, list):
        return False
    resolved = []
    for child in children:
        value = _int(child)
        if value is None:
            return False
        resolved.append(value)
    if len(resolved) != len(SEEDED_CHILDREN) + len(EXPECTED):
        return False
    if set(resolved) != set(SEEDED_CHILDREN) | set(new_ids):
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
        "family_matrix_extended": bool(scope and variants_ok and _parent_ok(state, new_ids)),
    }
    components = []
    for name in COMPONENT_WEIGHTS:
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": COMPONENT_DETAILS[name],
        })
    return round(sum(c["score"] for c in components), 6), components
'''

REWARD_HEAD = '''"""Deterministic offline reward for %(tid)s.

Reads the episode's current browser state only. The rubric asserts the EXACT
resulting variant collection for the %(pname)s configurable parent -- every
generated option-value combination with its own SKU, name, size and colour
option ids, price, quantity, status, type and attribute set -- so a matrix that
gained a combination nobody asked for scores 0.0 rather than partial credit,
and an untouched store scores 0.0 because the expected set is non-empty.

Scope is a gate rather than a paid component (output/CORRECTIONS.md #84/#110):
touching another family, deleting a seeded variant or rewriting one of the
existing rows takes the whole score to 0.0 and pays nothing on its own.
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

NEMO_HEAD = '''"""NeMo-Gym reward program for %(tid)s.

Same rubric as reward.py, read from the state API instead of an evidence
bundle: GET /go?sid=..., inspect current_state, print REWARD: <float> on every
output path. Self-contained -- standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url_token)s"
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

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for %(tid)s.

Plants the retrieval material this task derives its target from: %(what)s.
Nothing here touches newProducts or productOverrides, so the injected state
scores exactly 0.0 under this bundle's rubric.

Written as a read-modify-write (output/CORRECTIONS.md B6-9): GET /go for the
whole document, append the row(s), POST the whole document back. Correct
whether the mock merges or replaces a partial `set`.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url_token)s"

COLLECTION = "%(collection)s"
KEY_FIELD = "%(key_field)s"
NEW_ROWS = json.loads(r"""%(rows)s""")


def fail(message):
    sys.stderr.write("SETUP FAILED: %%s\\n" %% (message,))
    raise SystemExit(1)


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    payload = probe.json()
    document = payload.get("current_state")
    if not isinstance(document, dict):
        document = payload.get("initial_state")
    if not isinstance(document, dict):
        fail("/go returned no usable state document")

    rows = document.get(COLLECTION)
    if not isinstance(rows, list) or not rows:
        fail("the live document carries no %%s collection" %% (COLLECTION,))

    known = set()
    for row in rows:
        if isinstance(row, dict):
            known.add(str(row.get(KEY_FIELD)))
    merged = list(rows)
    for row in NEW_ROWS:
        if str(row.get(KEY_FIELD)) in known:
            fail("injected %%s id collides with a seeded row" %% (COLLECTION,))
        merged.append(row)
    document[COLLECTION] = merged

    if document.get("newProducts"):
        fail("newProducts must start empty")

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": document},
        timeout=180,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    if result.get("state_diff") != {}:
        fail("state_diff is not empty after set")
    current = result.get("current_state")
    if not isinstance(current, dict):
        fail("current_state is not an object")
    if len(current.get(COLLECTION) or []) != len(merged):
        fail("the injected row(s) did not land in %%s" %% (COLLECTION,))
    if current.get("newProducts") != []:
        fail("newProducts must start empty")
    print("SETUP OK")


main()
'''


def build_review(task, parent):
    r = task["review"]
    value = int(r["value"])
    return [{
        "review_id": r["review_id"],
        "created_at": r["created_at"],
        "entity_id": 1,
        "entity_pk_value": parent["entity_id"],
        "status_id": 2,
        "status_code": "Pending",
        "store_id": 1,
        "title": r["title"],
        "detail": r["detail"],
        "nickname": r["nickname"],
        "customer_id": None,
        "sku": parent["sku"],
        "product_name": parent["name"],
        "ratings": [{
            "rating_id": 4,
            "rating_code": "Rating",
            "option_id": 15 + value,
            "value": value,
            "percent": value * 20,
        }],
        "rating_summary": float(value),
    }]


def build_terms(task):
    rows = []
    for t in task["terms"]:
        rows.append({
            "query_id": t["query_id"],
            "query_text": t["query_text"],
            "num_results": t["num_results"],
            "popularity": t["popularity"],
            "redirect": None,
            "store_id": 1,
            "display_in_terms": 1,
            "updated_at": "2023-04-24 20:%02d:%02d" % (t["query_id"] % 60, 11),
        })
    return rows


def replay_source(task, parent, rows, add_label, axis):
    steps = []
    if task["carrier"] == "review":
        steps = [
            "page.click('text=Marketing')",
            "page.click('text=All Reviews')",
            "# filter the Nickname column for %s, open its Edit link," % task["review"]["nickname"],
            "# read the product the review is about, then click through to it",
        ]
    else:
        steps = [
            "page.click('text=Marketing')",
            "page.click('text=Search Terms')",
            "# filter Results to 0-0, sort Uses descending, read the winning query text",
            "page.click('text=Catalog')",
            "page.click('text=Products')",
            "# keyword-search the product name the query named, open the parent row",
        ]
    body = "\n".join("    %s" % s for s in steps)
    return '''"""Golden replay draft for %(tid)s.

Not executed by the author (batch-6 authoring runs no validation). The
verification phase drives this path with golden-browser and rewrites it.

Path, click-only from '/':
  Dashboard -> %(carrier_path)s -> the derived product -> Configurations
  -> Edit Configurations -> wizard step 1 (Size and Color are pre-checked from
  the parent's configurable_attributes, ProductEdit.jsx:519) -> Next
  -> step 2: tick %(axis)s %(label)s -> Next -> step 3 leave both bulk modes on
  Skip -> Next -> step 4 Summary shows %(count)d rows -> Generate Products.

Expected end state: %(count)d new simple products %(skus)s, and product
%(pid)s's configurable_children grows from %(seeded)d to %(total)d ids.
"""


def replay(page, base_url):
    page.goto(base_url + "/")
%(steps)s
    page.click("#configurable_products_button")
    page.click("#wizard_next")
    page.check("input[name=\\"configurable[%(code)s][]\\"][value=\\"%(optid)s\\"]")
    page.click("#wizard_next")
    page.click("#wizard_next")
    page.click("#generate_configurations")
''' % {
        "tid": task["id"],
        "carrier_path": "Marketing > All Reviews" if task["carrier"] == "review"
                        else "Marketing > Search Terms",
        "axis": axis,
        "label": add_label,
        "count": len(rows),
        "skus": ", ".join(r["sku"] for r in rows),
        "pid": parent["entity_id"],
        "seeded": len(parent["configurable_children"]),
        "total": len(parent["configurable_children"]) + len(rows),
        "steps": body,
        "code": "size" if axis == "size" else "color",
        "optid": SIZE_ID[add_label] if axis == "size" else COLOR_ID[add_label],
    }


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    (BATCH / "replays").mkdir(parents=True, exist_ok=True)
    index = []
    nemo_lines = []

    for task in TASKS:
        tid = task["id"]
        parent, kids = family(task["parent"])
        add_size = task.get("add_size")
        add_color = task.get("add_color")
        axis = "size" if add_size else "color"
        add_label = add_size or add_color
        rows = expected_rows(task["parent"], add_size=add_size, add_color=add_color)
        seeded = list(parent["configurable_children"])
        bundle = OUT / tid
        bundle.mkdir(parents=True, exist_ok=True)

        detail_a = json.dumps(
            "newProducts is exactly the %d generated variant(s) for %s: %s, each with "
            "the matching name, size and colour option ids, price %.2f, quantity %.1f, "
            "status 1, type simple and attribute set %d"
            % (len(rows), parent["name"], ", ".join(r["sku"] for r in rows),
               rows[0]["price"], rows[0]["qty"], rows[0]["attribute_set_id"])
        )
        detail_b = json.dumps(
            "productOverrides['%d'].configurable_children is the %d seeded children "
            "plus the %d generated ids, and configurable_attributes is still size and "
            "color" % (parent["entity_id"], len(seeded), len(rows))
        )
        body = REWARD_BODY % {
            "detail_a": detail_a,
            "detail_b": detail_b,
            "parent_id": str(parent["entity_id"]),
            "seeded": json.dumps(seeded, indent=2),
            "expected": json.dumps(rows, indent=2),
        }
        reward = (REWARD_HEAD % {"tid": tid, "pname": parent["name"]}) + body + REWARD_TAIL
        nemo_reward = (NEMO_HEAD % {"tid": tid, "url_token": URL_TOKEN}) + body + NEMO_TAIL
        (bundle / "reward.py").write_text(reward)
        (bundle / "nemo_reward.py").write_text(nemo_reward)

        if task["carrier"] == "review":
            inject_rows = build_review(task, parent)
            collection, key_field = "reviews", "review_id"
            what = ("one Pending product review (id %d, nickname %s) against %s, the "
                    "only pending review that asks the store to stock a missing "
                    "%s" % (inject_rows[0]["review_id"], task["review"]["nickname"],
                            parent["name"], axis))
            injected = [
                "reviews += one Pending review id %d by %s on product %d (%s), asking "
                "for %s %s. It is the retrieval material: without reading it the family "
                "and the missing option value are both unknown."
                % (inject_rows[0]["review_id"], task["review"]["nickname"],
                   parent["entity_id"], parent["sku"], axis, add_label),
                "Nothing is written to newProducts or productOverrides, so the injected "
                "state scores 0.0 under this rubric.",
            ]
        else:
            inject_rows = build_terms(task)
            collection, key_field = "searchTerms", "query_id"
            what = ("two storefront search-log rows -- the zero-result query %r at %d "
                    "uses, and a higher-use distractor %r that DID return results"
                    % (inject_rows[0]["query_text"], inject_rows[0]["popularity"],
                       inject_rows[1]["query_text"]))
            injected = [
                "searchTerms += %r (num_results 0, popularity %d) -- the target. The "
                "only zero-result query in the seed is 'nike' at 3 uses, so the "
                "superlative wins by %d uses with no tie."
                % (inject_rows[0]["query_text"], inject_rows[0]["popularity"],
                   inject_rows[0]["popularity"] - 3),
                "searchTerms += %r (num_results %d, popularity %d) -- a distractor that "
                "is the most-used query in the whole log and fails only the zero-result "
                "clause, so an agent that sorts on Uses without filtering Results lands "
                "on the wrong option value."
                % (inject_rows[1]["query_text"], inject_rows[1]["num_results"],
                   inject_rows[1]["popularity"]),
                "Nothing is written to newProducts or productOverrides, so the injected "
                "state scores 0.0 under this rubric.",
            ]

        setup = SETUP_TEMPLATE % {
            "tid": tid,
            "what": what,
            "url_token": URL_TOKEN,
            "collection": collection,
            "key_field": key_field,
            "rows": json.dumps(inject_rows, indent=2),
        }
        (bundle / "initial_setup.py").write_text(setup)

        criteria = [
            "state.newProducts is exactly %d row(s): %s -- each type simple, attribute "
            "set %d, price %.2f, quantity %.1f, status 1, size option %s and colour "
            "option %s."
            % (len(rows), ", ".join(r["sku"] for r in rows),
               rows[0]["attribute_set_id"], rows[0]["price"], rows[0]["qty"],
               "/".join(sorted({str(r["size"]) for r in rows})),
               "/".join(sorted({str(r["color"]) for r in rows}))),
            "productOverrides['%d'].configurable_children holds the %d seeded child ids "
            "plus the %d newly generated ids, and configurable_attributes is still "
            "['size', 'color']."
            % (parent["entity_id"], len(seeded), len(rows)),
            "No other product family gains variants, none of %s's %d seeded variants is "
            "edited or deleted, and no other configurable parent's children change."
            % (parent["name"], len(seeded)),
        ]
        (bundle / "task_instruction.json").write_text(json.dumps({
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": criteria,
        }, indent=2) + "\n")

        chain = (
            "text-search the %s for the row the instruction describes -> read the "
            "product family and the missing %s option off it -> open that parent's "
            "Configurations wizard and generate %s %s across the line's existing %s"
            % ("pending-review queue" if task["carrier"] == "review" else "storefront search log",
               axis, axis, add_label,
               "colours" if axis == "size" else "sizes")
        )
        manifest = {
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
            "metadata": {
                "style": task["style"],
                "difficulty": "medium",
                "shape": task["shape"],
                "skills": ["R6", "A6"],
                "skill_chain": chain,
                "derived_from": ("tights_size_matrix_aeon_capri_size30_001" if axis == "size"
                                 else "tights_size_matrix_sylvia_colour_parity_009"),
                "official_analogues": task["analogues"],
                "injected_preconditions": injected,
                "topic": "family_variant_matrix_extend",
                "lane": 49,
                "inspiration_ids": ["webarena-551", "webarena-547", "webarena-11", "webarena-41"],
                "authoring_notes": [
                    "Wizard mechanism verified in source: generateConfigurations "
                    "(ProductEdit.jsx:591) calls addProduct (AppContext.jsx:236 -> "
                    "state.newProducts) once per pending combination and patchProduct "
                    "(AppContext.jsx:219 -> state.productOverrides[parent]) for the "
                    "child list; both keys are read back by getProducts/getProduct "
                    "(selectors.js:154-178), which is what the Current Variations table "
                    "at ProductEdit.jsx:1089-1128 renders.",
                    "%s (%s, entity %d) carries %d seeded children over sizes %s and "
                    "colours %s, all at $%.2f and %.0f units, so the wizard's Skip "
                    "price/quantity path has one unambiguous outcome."
                    % (parent["name"], parent["sku"], parent["entity_id"], len(seeded),
                       "/".join(dict.fromkeys(SIZE[k["size"]] for k in kids)),
                       "/".join(dict.fromkeys(COLOR[k["color"]] for k in kids)),
                       rows[0]["price"], rows[0]["qty"]),
                    "%s %s is NOT in the family's seeded matrix (checked against all "
                    "%d children), so the untouched store cannot score above 0.0, and "
                    "the option value already exists on attribute %s, so no attribute "
                    "round-trip is needed (CORRECTIONS #82)."
                    % (axis, add_label, len(seeded), "144 (Size)" if axis == "size" else "93 (Color)"),
                    "Parent disjoint from batch-5's tights_size_matrix ten.",
                ],
            },
        }
        (bundle / "task.json").write_text(json.dumps(manifest, indent=2) + "\n")

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
                "initial_setup": setup,
                "eval_reward_code": nemo_reward,
            },
        }}
        (bundle / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n")
        nemo_lines.append(json.dumps(row))

        (BATCH / "replays" / ("%s.py" % tid)).write_text(
            replay_source(task, parent, rows, add_label, axis))
        index.append({"task_id": tid, "path": "../../%s/task.json" % tid})

    (BATCH / "nemo_tasks.jsonl").write_text("\n".join(nemo_lines) + "\n")
    (BATCH / "index.json").write_text(
        json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    print("wrote %d bundles" % len(index))


if __name__ == "__main__":
    main()
