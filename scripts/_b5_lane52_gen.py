#!/usr/bin/env python3
"""Author lane 52 (shopping_admin / retire_product_line) bundles.

Writes 10 bundles under output/tasks/shopping_admin/<task_id>/ plus the
batch GENERATION.md and replay drafts. No validation is run here.
"""

import json
import os
import textwrap

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/retire_product_line")
REPLAYS = os.path.join(BATCH, "replays")

APP = "webarena_shopping_admin_mock"
SOURCE = "shopping_admin"
ENV = "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

# ----------------------------------------------------------------- id sets
HOLLISTER_CHILDREN = list(range(111, 126))
HOLLISTER_PARENT = 126
TETON_CHILDREN = list(range(63, 78))
TETON_PARENT = 78
RYKER_CREW = list(range(463, 479))          # 463..477 children + 478 parent
RYKER_VNECK = list(range(559, 575))
HELIOS_EVERCOOL = list(range(447, 463))
HELIOS_TANK = list(range(671, 677))
TAURUS_ALL = list(range(335, 351))
TAURUS_YELLOW = [337, 340, 343, 346, 349]
SELENE_CHILDREN = list(range(1093, 1108))
SELENE_PARENT = 1108
CHLOE_ALL = list(range(1749, 1765))
GOBI_ALL = list(range(431, 447))
GOBI_BLACK = [431, 434, 437, 440, 443]
GOBI_REST = [i for i in GOBI_ALL if i not in GOBI_BLACK]
KARMEN_ALL = list(range(1813, 1820))
KARMEN_29 = [1816, 1817, 1818]
AEON_ALL = list(range(1855, 1862))
CORA_ALL = list(range(1834, 1841))


def pylist(ids):
    return "[" + ", ".join(str(i) for i in ids) + "]"


# ------------------------------------------------------------- code blocks
HELPERS = '''

def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _overrides(state):
    return _dict(_dict(state).get("productOverrides"))


def _field(state, product_id, key):
    row = _dict(_overrides(state).get(str(product_id)))
    if key not in row:
        return None
    value = row.get(key)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _all_field(state, ids, key, wanted):
    return all(_field(state, pid, key) == wanted for pid in ids)


def _disabled_within(state, ids):
    return sorted(pid for pid in ids if _field(state, pid, "status") == 2)


def _build(checks, details):
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = bool(checks.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": details.get(name, ""),
        })
    return components


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
'''

LOCAL_TAIL = '''

def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    state = _dict(_dict(apps.get("shopping_admin")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

NEMO_TAIL = '''

def main():
    try:
        url = BASE_URL.rstrip("/") + "/go?sid=" + SID
        payload = requests.get(url, timeout=60).json()
        state = payload.get("current_state") if isinstance(payload, dict) else None
        components = score_state(_dict(state))
        total = round(sum(c["score"] for c in components), 6)
        for component in components:
            sys.stderr.write("%s: %s\\n" % (component["name"], component["details"]))
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write("reward error: %r\\n" % (exc,))
        print("REWARD: 0.0")
        return 0
    print("REWARD: %s" % (_clamp(float(total)),))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def setup_program(task_id, prose, patch_json):
    return (
        '"""NeMo-Gym setup program for %s.\n\n%s\n\nSelf-contained: standard library plus requests\n(present in cuagym/requirements.txt). Posts a partial {"action": "set"}\nstate, which webarena_shopping_admin_mock merges shallowly over\ncreateInitialData() (vite.config.js:371-378), so the other 43 seeded keys\nkeep their pristine values.\n"""\n'
        % (task_id, prose)
        + "\nimport json\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER
        + 'STATE_PATCH = json.loads(r"""\n%s\n""")\n\n\n' % patch_json
        + "def main():\n"
        "    url = BASE_URL.rstrip(\"/\") + \"/post?sid=\" + SID\n"
        "    response = requests.post(\n"
        "        url,\n"
        "        json={\"action\": \"set\", \"state\": STATE_PATCH},\n"
        "        timeout=60,\n"
        "    )\n"
        "    response.raise_for_status()\n"
        "    sys.stderr.write(\"initial_setup ok: %s\\n\" % (response.status_code,))\n"
        "    return 0\n\n\n"
        "if __name__ == \"__main__\":\n"
        "    sys.exit(main())\n"
    )


def reward_files(task_id, doc, consts, score_body, weights, extra=""):
    weight_src = "COMPONENT_WEIGHTS = {\n" + "".join(
        '    "%s": %s,\n' % (k, v) for k, v in weights
    ) + "}\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n"

    local = (
        '"""Deterministic reward for %s.\n\n%s\n\nReads the frozen evidence bundle and inspects current_state only.\n"""\n'
        % (task_id, doc)
        + "\n" + extra + weight_src + "\n" + consts + HELPERS + "\n\n" + score_body + LOCAL_TAIL
    )
    nemo = (
        '"""NeMo-Gym reward program for %s.\n\n%s\n\nGETs /go?sid=... and prints REWARD: <float> on every output path.\n"""\n'
        % (task_id, doc)
        + "\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER
        + extra + weight_src + "\n" + consts + HELPERS + "\n\n" + score_body + NEMO_TAIL
    )
    return local, nemo


TASKS = []


def add(**kw):
    TASKS.append(kw)


# ============================================================== task 001
add(
    task_id="retire_product_line_hollister_sweatshirt_takedown_001",
    instruction=(
        "Quality complaints have piled up on the Hollister Backyard Sweatshirt. "
        "Take that line off the site: the configurable product itself and every "
        "one of its size and colour variants must read Disabled in the catalogue."
    ),
    style="terse",
    difficulty="medium",
    shape="mutation",
    skills=["R6", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search the Products grid for the Hollister family -> A4 select "
        "the whole matched set -> A10 run Change status / Disable over it"
    ),
    analogues=["Disable Teton pullover hoodie from the site, they are facing some quality issues."],
    hard_criteria=None,
    criteria=[
        "current_state.productOverrides holds status == 2 for every one of the 15 MH05 child products, entity_ids 111-125.",
        "current_state.productOverrides holds status == 2 for the MH05 configurable parent, entity_id 126.",
    ],
    weights=[("hollister_child_variants_disabled", 0.7), ("hollister_parent_disabled", 0.3)],
    consts="CHILDREN = %s\nPARENT = %d\n" % (pylist(HOLLISTER_CHILDREN), HOLLISTER_PARENT),
    doc=(
        "Products grid keyword search for 'hollister' matches exactly the 16 MH05 rows\n"
        "(15 simple children 111-125 plus configurable parent 126). ProductGrid.jsx:473\n"
        "dispatches Change status / Disable to patchProduct(id, {status: 2}), which\n"
        "AppContext.jsx:219 records as state.productOverrides[id].status = 2."
    ),
    score_body=(
        "def score_state(state):\n"
        "    children_ok = _all_field(state, CHILDREN, \"status\", 2)\n"
        "    parent_ok = _field(state, PARENT, \"status\") == 2\n"
        "    missing = [pid for pid in CHILDREN if _field(state, pid, \"status\") != 2]\n"
        "    checks = {\n"
        "        \"hollister_child_variants_disabled\": children_ok,\n"
        "        \"hollister_parent_disabled\": parent_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"hollister_child_variants_disabled\": \"child rows not disabled: %r\" % (missing,),\n"
        "        \"hollister_parent_disabled\": \"parent %d status override == %r\" % (PARENT, _field(state, PARENT, \"status\")),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Reachable from '/': the dashboard redirect (App.jsx:624) then left rail Catalog > Products (adminMenu.js:52), the grid's keyword search box (AdminGrid.jsx:420-431), Options > Select All (AdminGrid.jsx:874-914), Actions > Change status / Disable (AdminGrid.jsx:744-775).",
        "product_listing default page size is 200 (gridUtils.js GRID_PAGE_SIZES), so all 16 matched rows sit on one page and no paging is needed.",
        "The keyword engine (gridUtils.js matchesKeyword) scans every declared column including the hidden url_key, so 'hollister' matches name, sku and url_key on all 16 rows and nothing else in the 2040-row catalogue.",
        "Graded on the mutated SET, not on a value: 15 child ids plus the parent.",
    ],
)

# ============================================================== task 002
teton_patch = json.dumps(
    {"productOverrides": {str(i): {"status": 2} for i in TETON_CHILDREN + [TETON_PARENT]}},
    indent=1,
)
add(
    task_id="retire_product_line_teton_hoodie_relaunch_002",
    instruction=(
        "The Teton Pullover Hoodie fault has been fixed at the supplier and the "
        "line goes back on sale today. Every Teton Pullover Hoodie record in the "
        "catalogue must read Enabled again."
    ),
    style="terse",
    difficulty="hard",
    shape="mutation",
    skills=["R6", "R5", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search the Products grid for the Teton family -> R5 narrow the "
        "grid with the Status = Disabled filter to see the pulled rows -> A4 select "
        "the matched set -> A10 run Change status / Enable over it"
    ),
    analogues=["Disable Teton pullover hoodie from the site, they are facing some quality issues."],
    hard_criteria=["multi_mutation", "shortcut_defeating"],
    criteria=[
        "current_state.productOverrides holds status == 1 for every one of the 15 MH02 child products, entity_ids 63-77.",
        "current_state.productOverrides holds status == 1 for the MH02 configurable parent, entity_id 78.",
    ],
    weights=[("teton_child_variants_enabled", 0.7), ("teton_parent_enabled", 0.3)],
    consts="CHILDREN = %s\nPARENT = %d\n" % (pylist(TETON_CHILDREN), TETON_PARENT),
    doc=(
        "initial_setup.py disables all 16 MH02 rows (63-77 children, 78 parent) through\n"
        "productOverrides, the state key selectors.js:166-180 merges over each seed row.\n"
        "The agent finds them with the grid keyword search plus the Status = Disabled\n"
        "filter and runs Change status / Enable, which ProductGrid.jsx:465 dispatches to\n"
        "patchProduct(id, {status: 1}). The rubric pays only for status == 1 recorded in\n"
        "current_state.productOverrides, which the injected lane never satisfies."
    ),
    score_body=(
        "def score_state(state):\n"
        "    children_ok = _all_field(state, CHILDREN, \"status\", 1)\n"
        "    parent_ok = _field(state, PARENT, \"status\") == 1\n"
        "    missing = [pid for pid in CHILDREN if _field(state, pid, \"status\") != 1]\n"
        "    checks = {\n"
        "        \"teton_child_variants_enabled\": children_ok,\n"
        "        \"teton_parent_enabled\": parent_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"teton_child_variants_enabled\": \"child rows not enabled: %r\" % (missing,),\n"
        "        \"teton_parent_enabled\": \"parent %d status override == %r\" % (PARENT, _field(state, PARENT, \"status\")),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=(
        "Disables the whole Teton Pullover Hoodie line (MH02: entity_ids 63-77 plus\n"
        "configurable parent 78) by writing status 2 into productOverrides, the same\n"
        "key ProductGrid's Change status mass action writes. A line pulled for a\n"
        "supplier fault is an ordinary Magento state and it renders consistently:\n"
        "all 16 rows show Status = Disabled on the Products grid.\n\n"
        "Nothing in the rubric is pre-satisfied - the rubric pays only for status 1,\n"
        "so the injected lane scores exactly 0.0.",
        teton_patch,
    ),
    injections=[
        "productOverrides: {\"63\"..\"78\": {\"status\": 2}} - all 15 MH02 child variants and the MH02 configurable parent start Disabled.",
        "Why: the pristine seed has every product at status 1, so a re-enable task would be pre-satisfied and unobservable. The injection is what makes the Status = Disabled facet meaningful and gives the lifecycle transition a real starting point.",
        "The injection writes only status; is_in_stock, qty and price stay at their seeded values, so no other rubric surface is touched and the initial lane scores exactly 0.0.",
    ],
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Reachable from '/': Catalog > Products (adminMenu.js:52), keyword search 'teton', Filters panel Status = Disabled (ProductGrid.jsx STATUS_OPTIONS, filterValue String(r.status)), Options > Select All, Actions > Change status / Enable.",
        "shortcut_defeating: enabling only the configurable parent from its own edit page scores 0.3 of 1.0.",
        "multi_mutation: 16 distinct patchProduct writes.",
        "The action does not disturb its own retrieval premise - the family is named in the instruction, not derived from a ranking the action would move.",
    ],
)

# ============================================================== task 003
add(
    task_id="retire_product_line_ryker_crew_neck_only_003",
    instruction=(
        "We are retiring the Ryker LumaTech Tee (Crew-neck) for quality reasons. "
        "Searching the Products grid for \"Ryker\" brings back two different tees - "
        "the Crew-neck line (SKU prefix MS09) and the V-neck line (SKU prefix MS02) - "
        "and only the Crew-neck one is affected. Disable the Crew-neck configurable "
        "product and all fifteen of its size/colour variants. The V-neck line is "
        "unaffected and every one of its records must still be Enabled when you are done."
    ),
    style="explicit",
    difficulty="hard",
    shape="mutation",
    skills=["R6", "R5", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search 'ryker', which matches two families -> R5 narrow the grid "
        "by name or SKU so only the MS09 Crew-neck rows match -> A4 select that matched "
        "set -> A10 run Change status / Disable over it"
    ),
    analogues=["Disable Ryker Tee Crew Neck from the site, they are facing some quality issues."],
    hard_criteria=["multi_mutation", "shortcut_defeating"],
    criteria=[
        "current_state.productOverrides holds status == 2 for all 16 MS09 Crew-neck rows, entity_ids 463-478.",
        "None of the 16 MS02 V-neck rows, entity_ids 559-574, carries a productOverrides status of 2; if any of them does, both scored components are gated to zero.",
        "Across the 32 rows a 'Ryker' keyword search returns, the set now disabled is exactly the 16 Crew-neck entity_ids.",
    ],
    weights=[
        ("crew_neck_child_variants_disabled", 0.7),
        ("crew_neck_parent_disabled", 0.3),
    ],
    consts=(
        "CREW_CHILDREN = %s\nCREW_PARENT = %d\nVNECK = %s\n"
        % (pylist(RYKER_CREW[:-1]), RYKER_CREW[-1], pylist(RYKER_VNECK))
    ),
    doc=(
        "A keyword search for 'ryker' matches 32 rows: MS09 Ryker LumaTech Tee\n"
        "(Crew-neck), entity_ids 463-478, and MS02 Ryker LumaTech Tee (V-neck),\n"
        "entity_ids 559-574. Only the MS09 set may end up disabled. Change status /\n"
        "Disable writes productOverrides[id].status = 2 (ProductGrid.jsx:473 ->\n"
        "AppContext.jsx:219).\n\n"
        "The V-neck line is a SCOPE GATE, not a paid component: touching it zeroes both\n"
        "scored components rather than earning anything. Every weight therefore pays\n"
        "only for a row the agent actually disabled, so an empty current_state scores\n"
        "exactly 0.0 (TASK4 S9.5, CORRECTIONS.md finding 84)."
    ),
    score_body=(
        "def score_state(state):\n"
        "    # Scope gate: the MS02 V-neck line is out of scope. Disabling any of it\n"
        "    # zeroes the whole rubric instead of paying a component for leaving it\n"
        "    # alone, so nothing here pays on an empty current_state.\n"
        "    vneck_hit = _disabled_within(state, VNECK)\n"
        "    scope_ok = len(vneck_hit) == 0\n"
        "    crew_ok = bool(scope_ok and _all_field(state, CREW_CHILDREN, \"status\", 2))\n"
        "    parent_ok = bool(scope_ok and _field(state, CREW_PARENT, \"status\") == 2)\n"
        "    checks = {\n"
        "        \"crew_neck_child_variants_disabled\": crew_ok,\n"
        "        \"crew_neck_parent_disabled\": parent_ok,\n"
        "    }\n"
        "    gate = \"in scope\" if scope_ok else (\"OUT OF SCOPE, MS02 rows disabled: %r\" % (vneck_hit,))\n"
        "    details = {\n"
        "        \"crew_neck_child_variants_disabled\": \"%s; MS09 child rows not disabled: %r\"\n"
        "            % (gate, [pid for pid in CREW_CHILDREN if _field(state, pid, \"status\") != 2]),\n"
        "        \"crew_neck_parent_disabled\": \"%s; MS09 parent %d status override == %r\" % (gate, CREW_PARENT, _field(state, CREW_PARENT, \"status\")),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Verified against src/data/products.json: 'ryker' matches 32 rows spanning two configurable families, MS09 (463-478) and MS02 (559-574). The seed itself supplies the distractor, so no injection is needed.",
        "The V-neck line is enforced as a SCOPE GATE over both components, not as a paid component (TASK4 S9.5 / CORRECTIONS.md finding 84): a component that pays because the distractor was left alone also pays on an empty current_state, which is why the earlier 0.4-weighted 'v_neck_sixteen_rows_enabled' component was removed.",
        "shortcut_defeating: selecting all 32 search hits and disabling them scores 0.0, because the gate fails and takes both components with it.",
        "Reachable from '/': Catalog > Products, keyword search, Filters > Name contains 'Crew' or SKU contains 'MS09', Options > Select All, Actions > Change status / Disable.",
        "Names carry an HTML entity in the seed ('Ryker LumaTech&trade; Tee'); selectors.js decodeNamed decodes it before the grid renders and before the keyword engine sees it, so 'ryker' and 'crew' both match on the rendered text.",
    ],
)

# ============================================================== task 004
add(
    task_id="retire_product_line_helios_endurance_tank_pull_004",
    instruction=(
        "The Helios Endurance Tank is being pulled from the range. Every product "
        "record in that line must end up Disabled and Out of Stock."
    ),
    style="terse",
    difficulty="hard",
    shape="mutation",
    skills=["R6", "R5", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search 'helios', which returns two Helios families -> R5 narrow the "
        "grid to the MT04 Endurance Tank rows -> A4 select that set and open Update "
        "attributes -> A10 apply Status = Disabled and Stock Status = Out of Stock"
    ),
    analogues=[
        "Disable Helios Endurance Tank from the site, they are facing some quality issues.",
        "Mark all Gobi HeatTec Tee as out of stock",
    ],
    hard_criteria=["multi_mutation", "shortcut_defeating"],
    criteria=[
        "Across the 22 rows a 'Helios' keyword search returns, the set carrying a productOverrides status of 2 is exactly the six MT04 entity_ids 671-676.",
        "current_state.productOverrides holds is_in_stock == 0 for all six MT04 rows, entity_ids 671-676.",
    ],
    weights=[
        ("helios_disabled_set_is_exactly_endurance_tank", 0.5),
        ("endurance_tank_rows_out_of_stock", 0.5),
    ],
    consts=(
        "ENDURANCE_TANK = %s\nHELIOS_SEARCH_HITS = %s\n"
        % (pylist(HELIOS_TANK), pylist(HELIOS_EVERCOOL + HELIOS_TANK))
    ),
    doc=(
        "A keyword search for 'helios' matches 22 rows: MS05 Helios EverCool Tee\n"
        "(447-462) and MT04 Helios Endurance Tank (671-676). Only the six MT04 rows may\n"
        "end up disabled, so the first component asserts the exact resulting collection\n"
        "rather than paying for anything left alone. The Update attributes form\n"
        "(ProductGrid.jsx:527-577) writes status and is_in_stock through\n"
        "applyBulkAttributes -> patchProduct (:498); the per-product edit form writes the\n"
        "same two fields (ProductEdit.jsx:308/311), so either route scores."
    ),
    score_body=(
        "def score_state(state):\n"
        "    disabled = _disabled_within(state, HELIOS_SEARCH_HITS)\n"
        "    exact = disabled == sorted(ENDURANCE_TANK)\n"
        "    stock_ok = _all_field(state, ENDURANCE_TANK, \"is_in_stock\", 0)\n"
        "    checks = {\n"
        "        \"helios_disabled_set_is_exactly_endurance_tank\": exact,\n"
        "        \"endurance_tank_rows_out_of_stock\": stock_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"helios_disabled_set_is_exactly_endurance_tank\": \"disabled Helios rows == %r (want %r)\" % (disabled, sorted(ENDURANCE_TANK)),\n"
        "        \"endurance_tank_rows_out_of_stock\": \"rows not out of stock: %r\"\n"
        "            % ([pid for pid in ENDURANCE_TANK if _field(state, pid, \"is_in_stock\") != 0],),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Verified against src/data/products.json: 'helios' matches 22 rows across two configurable families - MS05 Helios EverCool Tee (447-462) and MT04 Helios Endurance Tank (671-676). The distractor is seeded, not injected.",
        "Terse style, so the exactness requirement is written as one positive statement about the resulting collection (TASK4 S3.3) rather than as an untouched-neighbour component.",
        "shortcut_defeating: disabling all 22 Helios hits scores 0.0 on the first component and at most 0.5 overall.",
        "The Update attributes reset at ProductGrid.jsx:481 omits is_in_stock, so a stale Out of Stock selection can leak into a later bulk edit in the same episode; the rubric names both target fields explicitly on the six MT04 rows, so a leak onto other rows would only be visible through the first component's exact-set check.",
        "Reachable from '/': Catalog > Products, keyword search, Filters > SKU contains 'MT04' (or Name contains 'Endurance'), Options > Select All, Actions > Update attributes, then #bulk-status and #bulk-stock-status and Save.",
    ],
)

# ============================================================== task 005
add(
    task_id="retire_product_line_taurus_yellow_dye_recall_005",
    instruction=(
        "A dye recall covers only the yellow colourway of the Taurus Elements Shell. "
        "Disable every yellow Taurus Elements Shell variant."
    ),
    style="terse",
    difficulty="hard",
    shape="mutation",
    skills=["R6", "R5", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search 'taurus' for the MJ09 family -> R5 apply the grid's Color = "
        "Yellow filter to cut the family down to the five affected sizes -> A4 select "
        "them -> A10 run Change status / Disable"
    ),
    analogues=[
        "Reduce the price of green Hollister backyard sweatshirt in all sizes by $5",
        "Disable Cora Pant from the site, they are facing some quality issues.",
    ],
    hard_criteria=["multi_mutation", "shortcut_defeating"],
    criteria=[
        "current_state.productOverrides holds status == 2 for the five yellow MJ09 variants, entity_ids 337, 340, 343, 346 and 349.",
        "Across the 16 rows of the MJ09 family, the set now carrying a productOverrides status of 2 is exactly those five yellow entity_ids.",
    ],
    weights=[
        ("yellow_taurus_variants_disabled", 0.6),
        ("taurus_disabled_set_is_exactly_yellow", 0.4),
    ],
    consts="YELLOW = %s\nFAMILY = %s\n" % (pylist(TAURUS_YELLOW), pylist(TAURUS_ALL)),
    doc=(
        "MJ09 Taurus Elements Shell has 15 child variants in Blue, White and Yellow plus\n"
        "configurable parent 350 whose own color is null. The five yellow children are\n"
        "337, 340, 343, 346 and 349 (color option 60). The grid's Color filter is a\n"
        "hidden-by-default column with filterValue String(r.color), so Color = Yellow\n"
        "combined with the 'taurus' keyword isolates exactly those five rows.\n"
        "Change status / Disable writes productOverrides[id].status = 2."
    ),
    score_body=(
        "def score_state(state):\n"
        "    yellow_ok = _all_field(state, YELLOW, \"status\", 2)\n"
        "    disabled = _disabled_within(state, FAMILY)\n"
        "    exact = disabled == sorted(YELLOW)\n"
        "    checks = {\n"
        "        \"yellow_taurus_variants_disabled\": yellow_ok,\n"
        "        \"taurus_disabled_set_is_exactly_yellow\": exact,\n"
        "    }\n"
        "    details = {\n"
        "        \"yellow_taurus_variants_disabled\": \"yellow rows not disabled: %r\"\n"
        "            % ([pid for pid in YELLOW if _field(state, pid, \"status\") != 2],),\n"
        "        \"taurus_disabled_set_is_exactly_yellow\": \"disabled MJ09 rows == %r (want %r)\" % (disabled, sorted(YELLOW)),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Colour split verified in src/data/products.json: MJ09 has Blue 5, White 5, Yellow 5 and a parent with color null. Yellow is attributeOptions.color id 60.",
        "shortcut_defeating: disabling the whole 16-row family scores 0.6 of 1.0.",
        "multi_mutation: five distinct patchProduct writes.",
        "Reachable from '/': Catalog > Products, keyword search 'taurus', Filters panel > Color = Yellow (the Color filter renders even though the column is hidden by default - it is in ProductGrid FILTER_ORDER), Options > Select All, Actions > Change status / Disable.",
    ],
)

# ============================================================== task 006
search_terms_patch = json.dumps(
    {
        "searchTerms": [
            {"query_id": 1, "query_text": "Joust Bag", "num_results": 10, "popularity": 4,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-24 19:24:09"},
            {"query_id": 5, "query_text": "MT02-M-Gray", "num_results": 115, "popularity": 1,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-19 21:53:43"},
            {"query_id": 9, "query_text": "WP10", "num_results": 1, "popularity": 1,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-23 22:16:22"},
            {"query_id": 11, "query_text": "hollister", "num_results": 1, "popularity": 19,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-24 19:23:28"},
            {"query_id": 13, "query_text": "Antonia Racer Tank", "num_results": 23, "popularity": 2,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-24 19:09:46"},
            {"query_id": 19, "query_text": "nike", "num_results": 0, "popularity": 3,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-04-24 19:24:34"},
            {"query_id": 25, "query_text": "tanks", "num_results": 23, "popularity": 1,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-05-31 20:41:43"},
            {"query_id": 27, "query_text": "selene yoga hoodie", "num_results": 16, "popularity": 31,
             "redirect": None, "store_id": 1, "display_in_terms": 1, "updated_at": "2023-05-30 11:14:52"},
        ]
    },
    indent=1,
)
add(
    task_id="retire_product_line_top_search_term_stockout_006",
    instruction=(
        "Our shoppers' single most-searched term names a line we can no longer "
        "source. Find that top search term and mark every product record it names "
        "as Out of Stock."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R1", "R6", "A4", "A10"],
    skill_chain=(
        "R1 read the Search Terms report and take the single most-hit query -> R6 "
        "keyword-search the Products grid for the family that query names -> A4 select "
        "the whole matched set -> A10 apply Stock Status = Out of Stock to it"
    ),
    analogues=[
        "Get the top 1 search term(s) in my store",
        "Mark all Selene yoga hoodie as out of stock",
    ],
    hard_criteria=["derived_target", "multi_mutation"],
    criteria=[
        "current_state.productOverrides holds is_in_stock == 0 for all 15 WH05 child variants, entity_ids 1093-1107.",
        "current_state.productOverrides holds is_in_stock == 0 for the WH05 configurable parent, entity_id 1108.",
    ],
    weights=[("selene_child_variants_out_of_stock", 0.7), ("selene_parent_out_of_stock", 0.3)],
    consts="CHILDREN = %s\nPARENT = %d\n" % (pylist(SELENE_CHILDREN), SELENE_PARENT),
    doc=(
        "initial_setup.py adds one search term, 'selene yoga hoodie' with 31 hits, so the\n"
        "top query by Hits is that one and not the seeded 'hollister' (19). The Search\n"
        "Terms report is live from state.searchTerms (Marketing.jsx:826) and defaults to\n"
        "ID descending, so the agent has to sort on Hits to read the superlative. The\n"
        "named family is WH05 Selene Yoga Hoodie, entity_ids 1093-1108. Marking the set\n"
        "Out of Stock writes productOverrides[id].is_in_stock = 0 through\n"
        "applyBulkAttributes (ProductGrid.jsx:487-502) or the product edit form."
    ),
    score_body=(
        "def score_state(state):\n"
        "    children_ok = _all_field(state, CHILDREN, \"is_in_stock\", 0)\n"
        "    parent_ok = _field(state, PARENT, \"is_in_stock\") == 0\n"
        "    checks = {\n"
        "        \"selene_child_variants_out_of_stock\": children_ok,\n"
        "        \"selene_parent_out_of_stock\": parent_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"selene_child_variants_out_of_stock\": \"child rows still in stock: %r\"\n"
        "            % ([pid for pid in CHILDREN if _field(state, pid, \"is_in_stock\") != 0],),\n"
        "        \"selene_parent_out_of_stock\": \"parent %d is_in_stock override == %r\" % (PARENT, _field(state, PARENT, \"is_in_stock\")),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=(
        "Republishes state.searchTerms as the seven seeded rows plus one more:\n"
        "query_id 27, 'selene yoga hoodie', 16 results, 31 hits, dated 2023-05-30.\n"
        "A product-name query at the head of the search-term table is exactly what\n"
        "the seed already looks like ('Antonia Racer Tank' is a seeded term), so\n"
        "this stays inside the live site's envelope.\n\n"
        "Why: on the pristine seed the top term is 'hollister' at 19 hits. The\n"
        "injection makes the derived answer 'selene yoga hoodie' instead, so the\n"
        "correct target cannot be memorised from the frozen corpus, and the margin\n"
        "is a deliberate 12 hits (31 vs 19).\n\n"
        "The injection touches no product record, so nothing in the rubric is\n"
        "pre-satisfied and the initial lane scores exactly 0.0.",
        search_terms_patch,
    ),
    injections=[
        "searchTerms: the seven seeded rows plus query_id 27, query_text 'selene yoga hoodie', num_results 16, popularity 31, store_id 1, display_in_terms 1, updated_at '2023-05-30 11:14:52'.",
        "Why: on the pristine seed the top term is 'hollister' (19 hits), which points at a different family. Varying the precondition rather than the entity gives this chain a different correct answer and defeats memorisation of the frozen seed.",
        "Margin is 31 vs 19 hits - close enough that the ranking must be read, wide enough to be unambiguous. num_results 16 matches the number of catalogue rows the query really returns, so the row does not contradict itself on screen.",
        "No productOverrides is written, so every rubric component is false at t=0.",
    ],
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Read path traced: SearchTermsReport (Marketing.jsx:824-866) renders rows straight from state.searchTerms, so the injected row is visible; the Dashboard's Top Search Terms panel reads the same key (Dashboard.jsx:62-72) and stays consistent.",
        "Default sort on that report is query_id descending (Marketing.jsx defaultSort='query_id', defaultDir='desc'), so the agent must click the Hits column to get the superlative - the report is genuinely the only place this ranking exists.",
        "The action (marking products out of stock) does not touch state.searchTerms, so the retrieval premise survives the mutation.",
        "Reachable from '/': left rail Reports > Search Terms (adminMenu.js:163) or Marketing > Search Terms, sort by Hits, then Catalog > Products, keyword search, Options > Select All, Actions > Update attributes, #bulk-stock-status = Out of Stock, Save.",
        "Known limitation of the retrieval-writeback shape: an agent that already knew the Selene family would score without reading the report. The injection is what keeps that from being learnable from the seed.",
    ],
)

# ============================================================== task 007
add(
    task_id="retire_product_line_chloe_takedown_logged_007",
    instruction=(
        "The Chloe Compete Tank is being discontinued. Disable the whole line - the "
        "configurable product and every one of its size/colour variants - and then "
        "log the takedown under System > Other Settings > Custom Variables: add a new "
        "custom variable with Variable Code line_retirement_log and Variable Name "
        "Line Retirement Log, and put the number of product records you disabled, "
        "digits only, in its Variable Plain Value field."
    ),
    style="explicit",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "R3", "A4", "A10", "A7"],
    skill_chain=(
        "R6 keyword-search the Products grid for the Chloe Compete Tank family -> A4 "
        "select the matched set -> A10 run Change status / Disable -> R3 count the rows "
        "the grid reported as updated -> A7 write that count into a new custom variable"
    ),
    analogues=[
        "Disable Cora Pant from the site, they are facing some quality issues.",
        "Get the top 1 search term(s) in my store",
    ],
    hard_criteria=["derived_target", "multi_mutation"],
    criteria=[
        "current_state.productOverrides holds status == 2 for all 16 WT06 rows, entity_ids 1749-1764.",
        "current_state.systemConfig.variables holds exactly one row whose code is line_retirement_log, and its name is Line Retirement Log.",
        "That row's plain_value contains the single number 16 and no other number.",
    ],
    weights=[
        ("chloe_line_disabled", 0.5),
        ("retirement_variable_created", 0.2),
        ("logged_count_is_sixteen", 0.3),
    ],
    consts=(
        "FAMILY = %s\nVARIABLE_CODE = \"line_retirement_log\"\n"
        "VARIABLE_NAME = \"line retirement log\"\nEXPECTED_COUNT = \"16\"\n"
        % pylist(CHLOE_ALL)
    ),
    doc=(
        "WT06 Chloe Compete Tank is entity_ids 1749-1764 (15 children plus the\n"
        "configurable parent), so the derived count is 16 and it is never stated in the\n"
        "instruction. Disabling writes productOverrides[id].status = 2. The custom\n"
        "variable lands in state.systemConfig.variables through useSystemCollection\n"
        "('variables','variable_id').add (RecordForm.jsx:27-43, Tools.jsx:1005-1007);\n"
        "the seeded array is empty, so a single new row is an unambiguous diff."
    ),
    score_body=(
        "def score_state(state):\n"
        "    disabled_ok = _all_field(state, FAMILY, \"status\", 2)\n"
        "    rows = _list(_dict(_dict(state).get(\"systemConfig\")).get(\"variables\"))\n"
        "    matches = []\n"
        "    for row in rows:\n"
        "        if not isinstance(row, dict):\n"
        "            continue\n"
        "        if str(row.get(\"code\", \"\")).strip().lower() == VARIABLE_CODE:\n"
        "            matches.append(row)\n"
        "    created = bool(\n"
        "        len(matches) == 1\n"
        "        and str(matches[0].get(\"name\", \"\")).strip().lower() == VARIABLE_NAME\n"
        "    )\n"
        "    digits = []\n"
        "    if len(matches) == 1:\n"
        "        digits = re.findall(r\"\\d+\", str(matches[0].get(\"plain_value\", \"\")))\n"
        "    count_ok = bool(created and digits == [EXPECTED_COUNT])\n"
        "    checks = {\n"
        "        \"chloe_line_disabled\": disabled_ok,\n"
        "        \"retirement_variable_created\": created,\n"
        "        \"logged_count_is_sixteen\": count_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"chloe_line_disabled\": \"WT06 rows not disabled: %r\"\n"
        "            % ([pid for pid in FAMILY if _field(state, pid, \"status\") != 2],),\n"
        "        \"retirement_variable_created\": \"rows with that code == %d\" % (len(matches),),\n"
        "        \"logged_count_is_sixteen\": \"numbers found in plain_value == %r (want ['16'])\" % (digits,),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    extra_import="import re\n",
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "systemConfig.variables is seeded [] (src/data/systemConfig.json), so the writeback slot is unambiguous; the record shape written by the form is {variable_id, code, name, html_value, plain_value}.",
        "The derived value is 16 and the instruction never states it; the agent must count what it disabled (the grid's own message reads 'A total of 16 record(s) have been updated.').",
        "Reachable from '/': Catalog > Products, keyword search 'chloe compete', Options > Select All, Actions > Change status / Disable; then System > Other Settings > Custom Variables (adminMenu.js:56), Add New Variable (#add), fields #rf_code, #rf_name, #rf_plain_value, Save.",
        "The count is graded from the digits in plain_value, so '16' and '16 records' both score while '15' or an empty field do not.",
    ],
)

# ============================================================== task 008
gobi_patch = json.dumps(
    {"productOverrides": {str(i): {"status": 2} for i in GOBI_BLACK}},
    indent=1,
)
add(
    task_id="retire_product_line_gobi_takedown_finish_008",
    instruction=(
        "Someone started pulling the Gobi HeatTec Tee line and stopped halfway. "
        "Finish the job: every product record in that line must end up Disabled and "
        "Out of Stock."
    ),
    style="terse",
    difficulty="hard",
    shape="mutation",
    skills=["R6", "R5", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search 'gobi' for the MS04 family -> R5 use the Status filter to "
        "see which rows are still Enabled -> A4 select the family -> A10 disable the "
        "remainder and apply Stock Status = Out of Stock across the whole line"
    ),
    analogues=[
        "Mark all Gobi HeatTec Tee as out of stock",
        "Disable Cora Pant from the site, they are facing some quality issues.",
    ],
    hard_criteria=["multi_mutation", "shortcut_defeating"],
    criteria=[
        "current_state.productOverrides holds status == 2 for the eleven MS04 rows that started Enabled: 432, 433, 435, 436, 438, 439, 441, 442, 444, 445 and 446.",
        "current_state.productOverrides holds is_in_stock == 0 for all 16 MS04 rows, entity_ids 431-446.",
    ],
    weights=[
        ("gobi_remaining_live_rows_disabled", 0.5),
        ("gobi_line_all_out_of_stock", 0.5),
    ],
    consts="FAMILY = %s\nSTILL_LIVE = %s\n" % (pylist(GOBI_ALL), pylist(GOBI_REST)),
    doc=(
        "initial_setup.py disables the five black MS04 children (431, 434, 437, 440, 443),\n"
        "leaving ten coloured children plus configurable parent 446 enabled - a half-done\n"
        "takedown. The first component pays only for the eleven rows the agent must turn\n"
        "off; the second pays for the stock-status change across all sixteen, which the\n"
        "injection never touches. Both are false at t=0."
    ),
    score_body=(
        "def score_state(state):\n"
        "    live_ok = _all_field(state, STILL_LIVE, \"status\", 2)\n"
        "    stock_ok = _all_field(state, FAMILY, \"is_in_stock\", 0)\n"
        "    checks = {\n"
        "        \"gobi_remaining_live_rows_disabled\": live_ok,\n"
        "        \"gobi_line_all_out_of_stock\": stock_ok,\n"
        "    }\n"
        "    details = {\n"
        "        \"gobi_remaining_live_rows_disabled\": \"rows not disabled: %r\"\n"
        "            % ([pid for pid in STILL_LIVE if _field(state, pid, \"status\") != 2],),\n"
        "        \"gobi_line_all_out_of_stock\": \"rows not out of stock: %r\"\n"
        "            % ([pid for pid in FAMILY if _field(state, pid, \"is_in_stock\") != 0],),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=(
        "Disables the five black MS04 Gobi HeatTec Tee children (entity_ids 431,\n"
        "434, 437, 440, 443) through productOverrides, leaving the ten orange and\n"
        "red children plus configurable parent 446 Enabled. A half-finished\n"
        "takedown is an ordinary state for a real store and it renders without\n"
        "contradiction: the Products grid simply shows five Disabled rows and\n"
        "eleven Enabled ones inside the same family.\n\n"
        "The injection writes status only. The rubric pays for the eleven rows\n"
        "that start Enabled and for is_in_stock across the whole line, neither of\n"
        "which the injection satisfies, so the initial lane scores exactly 0.0.",
        gobi_patch,
    ),
    injections=[
        "productOverrides: {\"431\", \"434\", \"437\", \"440\", \"443\": {\"status\": 2}} - the five black MS04 variants start Disabled, so the family is half retired.",
        "Why: it gives the Status facet something real to discriminate and makes the matched set the agent must act on a subset it has to read rather than the whole family it is told about. Varying the precondition rather than the entity changes the correct answer for the same chain.",
        "It pre-satisfies nothing: component one is scoped to the eleven rows that start Enabled and component two is scoped to is_in_stock, which the injection never writes.",
    ],
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Colour split verified in src/data/products.json: MS04 has Black 5 (431, 434, 437, 440, 443), Orange 5, Red 5 and configurable parent 446 with color null.",
        "shortcut_defeating: marking the family Out of Stock without finishing the disable scores 0.5 of 1.0, and vice versa.",
        "Reachable from '/': Catalog > Products, keyword search 'gobi', Filters > Status = Enabled to see what is left, Options > Select All, Actions > Change status / Disable, then re-select and Actions > Update attributes > #bulk-stock-status = Out of Stock.",
        "Because AdminGrid clears the selection whenever the query string changes (AdminGrid.jsx:190), the two mass actions must be run as two separate select-then-apply passes.",
    ],
)

# ============================================================== task 009
add(
    task_id="retire_product_line_karmen_size_29_run_009",
    instruction=(
        "The size 29 run of the Karmen Yoga Pant is being discontinued because it "
        "fits badly. Disable every size 29 variant of that pant."
    ),
    style="terse",
    difficulty="medium",
    shape="mutation",
    skills=["R6", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search the Products grid down to the size 29 rows of the Karmen "
        "Yoga Pant -> A4 select that matched set -> A10 run Change status / Disable"
    ),
    analogues=["Disable Karmen yoga pants from the site, they are facing some quality issues."],
    hard_criteria=None,
    criteria=[
        "current_state.productOverrides holds status == 2 for the three size 29 WP01 variants, entity_ids 1816, 1817 and 1818.",
        "Across the seven rows of the WP01 family, the set now carrying a productOverrides status of 2 is exactly those three entity_ids.",
    ],
    weights=[
        ("karmen_size_29_variants_disabled", 0.6),
        ("karmen_disabled_set_is_exactly_size_29", 0.4),
    ],
    consts="SIZE_29 = %s\nFAMILY = %s\n" % (pylist(KARMEN_29), pylist(KARMEN_ALL)),
    doc=(
        "WP01 Karmen Yoga Pant has six children across sizes 28 and 29 in Black, Gray and\n"
        "White plus configurable parent 1819. The size 29 rows are 1816 (WP01-29-Black),\n"
        "1817 (WP01-29-Gray) and 1818 (WP01-29-White); a keyword search for\n"
        "'Karmen Yoga Pant-29' matches exactly those three rendered names.\n"
        "Change status / Disable writes productOverrides[id].status = 2."
    ),
    score_body=(
        "def score_state(state):\n"
        "    run_ok = _all_field(state, SIZE_29, \"status\", 2)\n"
        "    disabled = _disabled_within(state, FAMILY)\n"
        "    exact = disabled == sorted(SIZE_29)\n"
        "    checks = {\n"
        "        \"karmen_size_29_variants_disabled\": run_ok,\n"
        "        \"karmen_disabled_set_is_exactly_size_29\": exact,\n"
        "    }\n"
        "    details = {\n"
        "        \"karmen_size_29_variants_disabled\": \"size 29 rows not disabled: %r\"\n"
        "            % ([pid for pid in SIZE_29 if _field(state, pid, \"status\") != 2],),\n"
        "        \"karmen_disabled_set_is_exactly_size_29\": \"disabled WP01 rows == %r (want %r)\" % (disabled, sorted(SIZE_29)),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Size lives on the child rows' rendered name only ('Karmen Yoga Pant-29-Black'); there is no size column or size filter on this grid, so the sub-run has to be picked out of the family by name.",
        "Terse style, so the exactness requirement is one positive statement about the resulting collection rather than an untouched-neighbour component.",
        "Relabelled DOWN to medium on purpose: this is one retrieval feeding one composite mass action, not two distinct retrievals.",
        "Reachable from '/': Catalog > Products, keyword search, per-row #idscheck1816/1817/1818 or Options > Select All on a narrowed search, Actions > Change status / Disable.",
    ],
)

# ============================================================== task 010
add(
    task_id="retire_product_line_cheaper_pant_line_retired_010",
    instruction=(
        "We are dropping one of our two women's bottoms lines and keeping the other. "
        "Compare the catalogue price of the Cora Parachute Pant against the Aeon Capri, "
        "and retire whichever of the two sells for less: disable that line's "
        "configurable product and all six of its size/colour variants. The other line "
        "stays on sale, so none of its records may end up Disabled."
    ),
    style="explicit",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "R1", "A4", "A10"],
    skill_chain=(
        "R6 keyword-search the Products grid for each of the two named families -> R1 "
        "take the cheaper of the two list prices -> A4 select every row of the losing "
        "family -> A10 run Change status / Disable over it"
    ),
    analogues=[
        "Disable Cora Pant from the site, they are facing some quality issues.",
        "Mark all Aeon capri as out of stock",
    ],
    hard_criteria=["derived_target", "shortcut_defeating"],
    criteria=[
        "current_state.productOverrides holds status == 2 for all seven WP07 Aeon Capri rows, entity_ids 1855-1861.",
        "None of the seven WP04 Cora Parachute Pant rows, entity_ids 1834-1840, carries a productOverrides status of 2.",
        "Across the fourteen rows of the two families, the set now disabled is exactly the seven Aeon Capri entity_ids.",
    ],
    weights=[
        ("aeon_capri_line_disabled", 0.6),
        ("disabled_set_across_both_lines_is_exactly_aeon", 0.4),
    ],
    consts="AEON = %s\nCORA = %s\nBOTH = %s\n" % (pylist(AEON_ALL), pylist(CORA_ALL), pylist(sorted(AEON_ALL + CORA_ALL))),
    doc=(
        "WP04 Cora Parachute Pant lists at $75.00 on all seven rows; WP07 Aeon Capri\n"
        "lists at $48.00 on all seven. The cheaper line is therefore the Aeon Capri,\n"
        "entity_ids 1855-1861, with a $27.00 margin and no tie anywhere in either family.\n"
        "Change status / Disable writes productOverrides[id].status = 2."
    ),
    score_body=(
        "def score_state(state):\n"
        "    aeon_ok = _all_field(state, AEON, \"status\", 2)\n"
        "    disabled = _disabled_within(state, BOTH)\n"
        "    exact = disabled == sorted(AEON)\n"
        "    checks = {\n"
        "        \"aeon_capri_line_disabled\": aeon_ok,\n"
        "        \"disabled_set_across_both_lines_is_exactly_aeon\": exact,\n"
        "    }\n"
        "    details = {\n"
        "        \"aeon_capri_line_disabled\": \"Aeon rows not disabled: %r\"\n"
        "            % ([pid for pid in AEON if _field(state, pid, \"status\") != 2],),\n"
        "        \"disabled_set_across_both_lines_is_exactly_aeon\": \"disabled rows across both lines == %r (want %r)\" % (disabled, sorted(AEON)),\n"
        "    }\n"
        "    return _build(checks, details)\n"
    ),
    setup=None,
    injections=None,
    notes=[
        "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
        "Tie check: every WP04 row is 75.0 and every WP07 row is 48.0 in src/data/products.json, so the comparison has a $27.00 margin and exactly one right answer. Both parents carry a non-null price, unlike MH05 whose parent price is null.",
        "The instruction never names the target line - it names the comparison. That is the derived_target.",
        "shortcut_defeating: disabling both lines scores 0.6 of 1.0; disabling the Cora line instead scores 0.0.",
        "The mutation does not move the price comparison that selected the target, so the retrieval premise survives the action.",
        "Reachable from '/': Catalog > Products, keyword search 'cora' then 'aeon' (or 'pant' plus the Price column), Options > Select All, Actions > Change status / Disable.",
    ],
)


# ------------------------------------------------------------------ write
def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


index_entries = []
ONLY = os.environ.get("LANE52_ONLY")
for t in TASKS:
    tid = t["task_id"]
    if ONLY and tid != ONLY:
        index_entries.append({"task_id": tid, "path": "%s/task.json" % tid, "row": json.loads(open(os.path.join(OUT, tid, "nemo_task.json"), encoding="utf-8").read())})
        continue
    bundle = os.path.join(OUT, tid)
    os.makedirs(bundle, exist_ok=True)

    local, nemo = reward_files(tid, t["doc"], t["consts"], t["score_body"], t["weights"], t.get("extra_import", ""))
    write(os.path.join(bundle, "reward.py"), local)
    write(os.path.join(bundle, "nemo_reward.py"), nemo)

    setup_code = None
    if t.get("setup"):
        prose, patch = t["setup"]
        setup_code = setup_program(tid, prose, patch)
        write(os.path.join(bundle, "initial_setup.py"), setup_code)

    write(os.path.join(bundle, "task_instruction.json"), json.dumps({
        "task_id": tid,
        "task_instruction": t["instruction"],
        "app_dir": APP,
        "start_path": "/",
        "difficulty": t["difficulty"],
        "success_criteria": t["criteria"],
    }, indent=2, ensure_ascii=False) + "\n")

    metadata = {
        "style": t["style"],
        "difficulty": t["difficulty"],
        "shape": t["shape"],
        "skills": t["skills"],
        "skill_chain": t["skill_chain"],
        "official_analogues": t["analogues"],
    }
    if t.get("hard_criteria"):
        metadata["hard_criteria"] = t["hard_criteria"]
    if t.get("injections"):
        metadata["injected_preconditions"] = t["injections"]
    metadata["topic"] = "shopping_admin retire a product line"
    metadata["lane"] = "retire_product_line"
    metadata["inspiration_ids"] = ["webarena-005", "webarena-020", "webarena-501", "webarena-085"]
    metadata["authoring_notes"] = t["notes"]

    write(os.path.join(bundle, "task.json"), json.dumps({
        "schema_version": 2,
        "task_id": tid,
        "instruction": t["instruction"],
        "apps": [{
            "name": APP,
            "source_name": SOURCE,
            "base_url_env": ENV,
            "start_path": "/",
            "initial_state": None,
            "golden_state": None,
        }],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": metadata,
    }, indent=2, ensure_ascii=False) + "\n")

    row = {"task_payload": {
        "task_id": tid,
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP],
        "start_urls": [],
        "intent": t["instruction"],
        "eval": {
            "eval_types": ["string_match"],
            "reference_answers": None,
            "note": "unused - CUA-Gym reward code is authoritative",
        },
        "cuagym": {
            "bundle_id": tid,
            "app_dir": APP,
            "initial_setup": setup_code,
            "eval_reward_code": nemo,
        },
    }}
    write(os.path.join(bundle, "nemo_task.json"), json.dumps(row, indent=2, ensure_ascii=False) + "\n")
    index_entries.append({"task_id": tid, "path": "%s/task.json" % tid, "row": row})

os.makedirs(BATCH, exist_ok=True)
with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w", encoding="utf-8") as handle:
    for entry in index_entries:
        handle.write(json.dumps(entry["row"], ensure_ascii=False) + "\n")

write(os.path.join(BATCH, "index.json"), json.dumps({
    "schema_version": 2,
    "tasks": [{"task_id": e["task_id"], "path": "../../%s/task.json" % e["task_id"]} for e in index_entries],
}, indent=2) + "\n")

print("wrote %d bundles" % len(TASKS))
for t in TASKS:
    print(" ", t["task_id"], t["style"], t["difficulty"], t["shape"], len(t["instruction"].split()), "words")
