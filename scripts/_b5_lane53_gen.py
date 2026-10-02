#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 53 (shopping_admin / size_run_reprice).

Writes ten schema-v2 bundles plus GENERATION.md, replay drafts, index.json and
nemo_tasks.jsonl. Read-only against hub/.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE_DIR = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH_DIR = os.path.join(SITE_DIR, "_batches/size_run_reprice")
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

PRODUCTS = json.load(open(os.path.join(
    ROOT, "hub/websites/webarena_shopping_admin_mock/src/data/products.json")))
BY_ID = {p["entity_id"]: p for p in PRODUCTS}
BY_SKU = {p.get("sku"): p for p in PRODUCTS}

FIELDS = ("price", "qty", "is_in_stock", "status")


def line_rows(parent_sku):
    parent = BY_SKU[parent_sku]
    ids = [parent["entity_id"]] + list(parent.get("configurable_children", []))
    out = {}
    for pid in ids:
        row = BY_ID[pid]
        out[str(pid)] = {f: row.get(f) for f in FIELDS}
    return out


# --------------------------------------------------------------------------
# lane specification
# --------------------------------------------------------------------------

TASKS = []


def task(**kw):
    TASKS.append(kw)


task(
    task_id="size_run_reprice_sahara_size28_markdown_001",
    parent_sku="WP05",
    line_label="Sahara Leggings (WP05)",
    run_label="size 28",
    instruction=(
        "Sales are flat on the size 28 Sahara Leggings. Reduce the price of all "
        "three colours in that size by 12%."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "A6", "A5", "A4"],
    skill_chain=(
        "keyword-search the Products grid for the WP05 size-28 slice -> that "
        "variant set is the matched set -> compute 12% off the uniform $75 the "
        "grid shows -> bulk-apply the resulting absolute price to the three rows"
    ),
    analogues=["Reduce the price of size 28 Sahara leggings of all colors by 13.5%"],
    hard_criteria=["multi_mutation", "derived_target"],
    components=[
        ("wp05_28_blue_at_66_00", {"1841": {"price": 66.0}}, 0.34),
        ("wp05_28_gray_at_66_00", {"1842": {"price": 66.0}}, 0.33),
        ("wp05_28_red_at_66_00", {"1843": {"price": 66.0}}, 0.33),
    ],
    setup=None,
    search_hint="WP05-28",
    replay_prices={"1841": "66.00", "1842": "66.00", "1843": "66.00"},
    criteria=[
        "Product 1841 (WP05-28-Blue) sells at 66.00 in the merged catalogue view.",
        "Product 1842 (WP05-28-Gray) sells at 66.00.",
        "Product 1843 (WP05-28-Red) sells at 66.00.",
        "Every other WP05 row - the size 29 children and the configurable parent - still sells at its seeded 75.00.",
    ],
    notes=[
        "Derived value: the instruction never states $75 or $66. 75.00 x 0.88 = 66.00 exactly, so the bulk form's absolute #bulk-price accepts the arithmetic in one pass.",
        "Uniform seed price verified in src/data/products.json: 1841/1842/1843 are all price 75.0, which is what makes a single Update-attributes pass correct.",
    ],
)

task(
    task_id="size_run_reprice_diana_size29_uplift_002",
    parent_sku="WP06",
    line_label="Diana Tights (WP06)",
    run_label="size 29",
    instruction=(
        "Our size 29 Diana Tights are underpriced against the rest of the line. "
        "Raise the price of every colour in that size by 15%."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "A6", "A5", "A4"],
    skill_chain=(
        "keyword-search the Products grid for the WP06 size-29 slice -> the "
        "three colour variants are the matched set -> compute a 15% uplift on "
        "the uniform $59 -> bulk-apply the resulting price"
    ),
    analogues=["Increase the price of all blue running tshirts in extra small and small sizes by 23%"],
    hard_criteria=["multi_mutation", "derived_target"],
    components=[
        ("wp06_29_black_at_67_85", {"1851": {"price": 67.85}}, 0.34),
        ("wp06_29_blue_at_67_85", {"1852": {"price": 67.85}}, 0.33),
        ("wp06_29_orange_at_67_85", {"1853": {"price": 67.85}}, 0.33),
    ],
    setup=None,
    search_hint="WP06-29",
    replay_prices={"1851": "67.85", "1852": "67.85", "1853": "67.85"},
    criteria=[
        "Product 1851 (WP06-29-Black) sells at 67.85.",
        "Product 1852 (WP06-29-Blue) sells at 67.85.",
        "Product 1853 (WP06-29-Orange) sells at 67.85.",
        "Every other WP06 row - the size 28 children and the configurable parent - still sells at its seeded 59.00.",
    ],
    notes=[
        "59.00 x 1.15 = 67.85 exactly, so the derived figure has one two-decimal spelling.",
        "The whole WP06 line is uniform at 59.00, so an agent that repriced the size 28 run as well fails the scope gate on every component.",
    ],
)

task(
    task_id="size_run_reprice_hollister_size_l_shelf_price_003",
    parent_sku="MH05",
    line_label="Hollister Backyard Sweatshirt (MH05)",
    run_label="size L",
    instruction=(
        "Put every colour of the size L Hollister Backyard Sweatshirt on the "
        "shelf at $47.50."
    ),
    style="terse",
    difficulty="medium",
    shape="mutation",
    skills=["R6", "A4"],
    skill_chain=(
        "keyword-search the Products grid for the MH05 size-L slice -> "
        "bulk-apply the stated shelf price to the three matched rows"
    ),
    analogues=["Reduce the price of green Hollister backyard sweatshirt in all sizes by $5"],
    hard_criteria=[],
    components=[
        ("mh05_l_green_at_47_50", {"120": {"price": 47.5}}, 0.34),
        ("mh05_l_red_at_47_50", {"121": {"price": 47.5}}, 0.33),
        ("mh05_l_white_at_47_50", {"122": {"price": 47.5}}, 0.33),
    ],
    setup=None,
    search_hint="MH05-L",
    replay_prices={"120": "47.50", "121": "47.50", "122": "47.50"},
    criteria=[
        "Product 120 (MH05-L-Green) sells at 47.50.",
        "Product 121 (MH05-L-Red) sells at 47.50.",
        "Product 122 (MH05-L-White) sells at 47.50.",
        "The other twelve MH05 children still sell at 52.00 and the configurable parent still carries no price of its own.",
    ],
    notes=[
        "Medium by derivation: two skills only - locate the size slice by text search, then one bulk apply of a value the instruction states.",
        "The MH05 parent (126) carries price null in the seed; the scope gate expects it to stay null, which it does unless the agent selects the parent into the bulk pass.",
    ],
)

task(
    task_id="size_run_reprice_sahara_size29_uneven_clearance_004",
    parent_sku="WP05",
    line_label="Sahara Leggings (WP05)",
    run_label="size 29",
    instruction=(
        "The size 29 Sahara Leggings are being cleared out. In Catalog > Products, "
        "find the three size 29 variants - Blue, Gray and Red - and take 10% off "
        "whatever each one currently sells for. The Red one was already marked "
        "down earlier in the month, so the three prices are not all the same: work "
        "from each variant's own current price rather than assuming one figure for "
        "the whole run. The size 28 variants and the Sahara Leggings parent record "
        "keep the price they have now."
    ),
    style="explicit",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "R9", "A5", "A4"],
    skill_chain=(
        "keyword-search the WP05 size-29 slice -> read each variant's own current "
        "price off the grid -> compute a 10% cut per variant -> apply the three "
        "different absolute prices"
    ),
    analogues=["Reduce the price of size 28 Sahara leggings of all colors by 13.5%"],
    hard_criteria=["multi_mutation", "derived_target", "shortcut_defeating"],
    components=[
        ("wp05_29_blue_at_67_50", {"1844": {"price": 67.5}}, 0.34),
        ("wp05_29_gray_at_67_50", {"1845": {"price": 67.5}}, 0.33),
        ("wp05_29_red_at_54_00", {"1846": {"price": 54.0}}, 0.33),
    ],
    setup={"productOverrides": {"1846": {"price": 60.0}}},
    injected=[
        "productOverrides[\"1846\"].price = 60.0 - WP05-29-Red carries an earlier markdown from 75.00, exactly the shape a bulk Update-attributes price pass writes (ProductGrid.jsx:490 sets only `price`).",
    ],
    search_hint="WP05-29",
    replay_prices={"1844": "67.50", "1845": "67.50", "1846": "54.00"},
    criteria=[
        "Product 1844 (WP05-29-Blue) sells at 67.50.",
        "Product 1845 (WP05-29-Gray) sells at 67.50.",
        "Product 1846 (WP05-29-Red) sells at 54.00, i.e. 10% off its injected 60.00 rather than off 75.00.",
        "The three size 28 children and the WP05 parent still sell at 75.00.",
    ],
    notes=[
        "The injection destroys the single-bulk-pass shortcut: a one-shot 67.50 over all three rows scores 0.67, never 1.0.",
        "The injected 60.00 pre-satisfies nothing - the rubric wants 54.00 on that row and leaves the other two at their seeded 75.00, so the untouched injected lane scores exactly 0.0.",
    ],
)

task(
    task_id="size_run_reprice_diana_size28_match_sahara_005",
    parent_sku="WP06",
    line_label="Diana Tights (WP06)",
    run_label="size 28",
    instruction=(
        "Price the size 28 Diana Tights to match what we charge for the size 28 "
        "Sahara Leggings, across all three colours."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "R9", "A6", "A4"],
    skill_chain=(
        "keyword-search the Sahara Leggings size-28 slice and read its price -> "
        "keyword-search the Diana Tights size-28 slice -> bulk-apply the price "
        "carried across from the first line"
    ),
    analogues=["Add new size 30 and 31 to all color variants of Diana Tights"],
    hard_criteria=["multi_mutation", "derived_target"],
    components=[
        ("wp06_28_black_at_75_00", {"1848": {"price": 75.0}}, 0.34),
        ("wp06_28_blue_at_75_00", {"1849": {"price": 75.0}}, 0.33),
        ("wp06_28_orange_at_75_00", {"1850": {"price": 75.0}}, 0.33),
    ],
    setup=None,
    search_hint="WP06-28",
    replay_prices={"1848": "75.00", "1849": "75.00", "1850": "75.00"},
    criteria=[
        "Product 1848 (WP06-28-Black) sells at 75.00.",
        "Product 1849 (WP06-28-Blue) sells at 75.00.",
        "Product 1850 (WP06-28-Orange) sells at 75.00.",
        "The size 29 Diana Tights children and the WP06 parent still sell at 59.00.",
    ],
    notes=[
        "Two distinct retrievals: the value comes off a second product line (WP05-28-*, uniform 75.00) that the instruction names but never prices.",
        "The action does not disturb its own retrieval premise - the WP05 rows this task reads are not the rows it writes.",
    ],
)

task(
    task_id="size_run_reprice_erika_size30_restock_and_cut_006",
    parent_sku="WSH12",
    line_label="Erika Running Short (WSH12)",
    run_label="size 30",
    instruction=(
        "Restock all three colours of the size 30 Erika Running Short to 240 "
        "units each and run that size at 20% off."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "A6", "A5", "A4"],
    skill_chain=(
        "keyword-search the WSH12 size-30 slice -> read the uniform $45 the grid "
        "shows -> compute 20% off -> bulk-apply the new price and the new "
        "quantity to the matched set in one pass"
    ),
    analogues=["We've received additional 378 brown Aero daily fitness tee in every size, please update the inventory. If previous stock exist, add to it. If it does not exist previously, also update stock status to in stock."],
    hard_criteria=["multi_mutation", "derived_target"],
    components=[
        ("wsh12_30_green_at_36_00_qty_240", {"2031": {"price": 36.0, "qty": 240.0}}, 0.34),
        ("wsh12_30_purple_at_36_00_qty_240", {"2032": {"price": 36.0, "qty": 240.0}}, 0.33),
        ("wsh12_30_red_at_36_00_qty_240", {"2033": {"price": 36.0, "qty": 240.0}}, 0.33),
    ],
    setup=None,
    search_hint="WSH12-30",
    replay_prices={"2031": "36.00", "2032": "36.00", "2033": "36.00"},
    replay_qty="240",
    criteria=[
        "Products 2031, 2032 and 2033 each sell at 36.00.",
        "Each of those three carries quantity 240.",
        "The other twelve WSH12 children and the WSH12 parent still sell at 45.00.",
    ],
    notes=[
        "45.00 x 0.80 = 36.00 exactly. The quantity is stated; the price is derived, which is what makes this retrieval_writeback.",
        "#bulk-qty writes qty and salable_quantity together (ProductGrid.jsx:491); the rubric grades qty only, so the per-product Edit route scores identically.",
    ],
)

task(
    task_id="size_run_reprice_prima_size_xs_discontinue_007",
    parent_sku="WB04",
    line_label="Prima Compete Bra Top (WB04)",
    run_label="size XS",
    instruction=(
        "The size XS Prima Compete Bra Top is being discontinued: drop all three "
        "colours to $14.99 and switch them off in the catalogue."
    ),
    style="terse",
    difficulty="medium",
    shape="mutation",
    skills=["R6", "A4"],
    skill_chain=(
        "keyword-search the WB04 size-XS slice -> one bulk pass setting the "
        "stated clearance price and the Disabled status on the matched set"
    ),
    analogues=["Mark all Gobi HeatTec Tee as out of stock"],
    hard_criteria=[],
    components=[
        ("wb04_xs_blue_at_14_99_disabled", {"1637": {"price": 14.99, "status": 2}}, 0.34),
        ("wb04_xs_purple_at_14_99_disabled", {"1638": {"price": 14.99, "status": 2}}, 0.33),
        ("wb04_xs_yellow_at_14_99_disabled", {"1639": {"price": 14.99, "status": 2}}, 0.33),
    ],
    setup=None,
    scope_fields=["status"],
    search_hint="WB04-XS",
    replay_prices={"1637": "14.99", "1638": "14.99", "1639": "14.99"},
    replay_status="2",
    criteria=[
        "Products 1637, 1638 and 1639 each sell at 14.99.",
        "Each of those three is Disabled (status 2).",
        "The other twelve WB04 children and the WB04 parent still sell at 24.00 and are still Enabled.",
    ],
    notes=[
        "Medium by derivation: R6 to locate the slice, A4 to apply. Both fields go in one Update-attributes submission, so this is one action, not two.",
        "The value is stated, so this is not retrieval_writeback.",
    ],
)

task(
    task_id="size_run_reprice_chloe_size_m_uplift_and_restock_008",
    parent_sku="WT06",
    line_label="Chloe Compete Tank (WT06)",
    run_label="size M",
    instruction=(
        "We are taking the size M Chloe Compete Tank up 8% across all three "
        "colours - work the new figure out from what it sells for now. One of "
        "those three colours has run its stock down to zero and shows as out of "
        "stock; put 150 units back on that one and set it back to In Stock. The "
        "other two size M colours keep the stock they already have, and no other "
        "size of the tank changes price."
    ),
    style="explicit",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "R9", "A5", "A4"],
    skill_chain=(
        "keyword-search the WT06 size-M slice -> read the uniform price and spot "
        "which colour is at zero stock -> compute the 8% uplift -> apply the "
        "price to the run and the restock to the one sold-out variant"
    ),
    analogues=["5 blue Cronus yoga pants with size 33 arrived, update the stock. If previous stock exist, add to it. If it does not exist previously, also update stock status to in stock."],
    hard_criteria=["multi_mutation", "derived_target", "shortcut_defeating"],
    components=[
        ("wt06_m_blue_at_42_12", {"1755": {"price": 42.12}}, 0.25),
        ("wt06_m_red_at_42_12", {"1756": {"price": 42.12}}, 0.25),
        ("wt06_m_yellow_at_42_12", {"1757": {"price": 42.12}}, 0.25),
        ("wt06_m_red_restocked_to_150_in_stock", {"1756": {"qty": 150.0, "is_in_stock": 1}}, 0.25),
    ],
    stock_scope={"1755": {"qty": 100.0, "is_in_stock": 1},
                 "1757": {"qty": 100.0, "is_in_stock": 1}},
    setup={"productOverrides": {"1756": {"qty": 0.0, "salable_quantity": 0.0, "is_in_stock": 0}}},
    injected=[
        "productOverrides[\"1756\"] = {qty: 0.0, salable_quantity: 0.0, is_in_stock: 0} - WT06-M-Red has sold out. qty and salable_quantity move together exactly as #bulk-qty writes them (ProductGrid.jsx:491) and is_in_stock 0 matches the Stock Status bulk field, so the row is internally consistent on the grid and on its own edit form.",
    ],
    search_hint="WT06-M",
    replay_prices={"1755": "42.12", "1756": "42.12", "1757": "42.12"},
    replay_restock=("1756", "150"),
    criteria=[
        "Products 1755, 1756 and 1757 each sell at 42.12.",
        "Product 1756 (WT06-M-Red) carries quantity 150 and is In Stock.",
        "Products 1755 and 1757 still carry quantity 100 and are still In Stock.",
        "The other twelve WT06 children and the WT06 parent still sell at 39.00.",
    ],
    notes=[
        "39.00 x 1.08 = 42.12 exactly.",
        "Shortcut defeated: a single bulk pass carrying both the price and qty 150 lands 150 units on all three colours, which fails the restock component's stock gate and caps the run at 0.75.",
        "The injection sets stock, never price, so the untouched injected lane scores exactly 0.0.",
    ],
)

task(
    task_id="size_run_reprice_ingrid_size_l_rebate_009",
    parent_sku="WJ04",
    line_label="Ingrid Running Jacket (WJ04)",
    run_label="size L",
    instruction=(
        "Our supplier has cut what we pay for the Ingrid Running Jacket and we "
        "are passing $6.50 of it on to customers, but only on the size L run. In "
        "Catalog > Products, find the three size L variants - Orange, Red and "
        "White - and reduce each one's price by $6.50 from what it currently "
        "shows. Sizes XS, S, M and XL keep the price they have now, and so does "
        "the Ingrid Running Jacket parent record."
    ),
    style="explicit",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "A6", "A5", "A4"],
    skill_chain=(
        "keyword-search the WJ04 size-L slice -> that variant set is the matched "
        "set -> subtract $6.50 from the price the grid shows -> bulk-apply the "
        "resulting absolute price"
    ),
    analogues=["Increase the price of white Ingrid Running with size L and above by $17"],
    hard_criteria=["multi_mutation", "derived_target"],
    components=[
        ("wj04_l_orange_at_77_50", {"1262": {"price": 77.5}}, 0.34),
        ("wj04_l_red_at_77_50", {"1263": {"price": 77.5}}, 0.33),
        ("wj04_l_white_at_77_50", {"1264": {"price": 77.5}}, 0.33),
    ],
    setup=None,
    search_hint="WJ04-L",
    replay_prices={"1262": "77.50", "1263": "77.50", "1264": "77.50"},
    criteria=[
        "Products 1262, 1263 and 1264 each sell at 77.50.",
        "The other twelve WJ04 children still sell at 84.00.",
        "The WJ04 parent record still sells at 84.00.",
    ],
    notes=[
        "84.00 - 6.50 = 77.50. The current price is never stated, so the figure is derived.",
        "The official analogue works over 'size L and above'; this lane deliberately uses the single L run so the matched set is the text-search slice rather than an ordinal range.",
    ],
)

task(
    task_id="size_run_reprice_phoebe_size_m_enabled_only_010",
    parent_sku="WH07",
    line_label="Phoebe Zipper Sweatshirt (WH07)",
    run_label="size M",
    instruction=(
        "Take 20% off the size M Phoebe Zipper Sweatshirt - only the colours that "
        "are still enabled."
    ),
    style="terse",
    difficulty="hard",
    shape="retrieval_writeback",
    skills=["R6", "A13", "A5", "A4"],
    skill_chain=(
        "keyword-search the WH07 size-M slice -> apply the enabled/disabled "
        "predicate to pick the matched subset -> compute 20% off the price the "
        "grid shows -> bulk-apply it to that subset only"
    ),
    analogues=["Reduce the price of yellow shirts from Gwyn Endurance in all sizes below L by 15%"],
    hard_criteria=["derived_target", "shortcut_defeating"],
    components=[
        ("wh07_m_gray_at_47_20", {"1121": {"price": 47.2}}, 0.5),
        ("wh07_m_white_at_47_20", {"1123": {"price": 47.2}}, 0.5),
    ],
    setup={"productOverrides": {"1122": {"status": 2}}},
    injected=[
        "productOverrides[\"1122\"].status = 2 - WH07-M-Purple has been discontinued. That is exactly the patch the grid's own 'Change status / Disable' mass action writes (ProductGrid.jsx:473), so the row is a plausible ordinary-day record and renders as Disabled in the grid's Status column.",
    ],
    search_hint="WH07-M",
    replay_prices={"1121": "47.20", "1123": "47.20"},
    criteria=[
        "Product 1121 (WH07-M-Gray) sells at 47.20.",
        "Product 1123 (WH07-M-White) sells at 47.20.",
        "Product 1122 (WH07-M-Purple), the disabled colour, still sells at 59.00.",
        "The other twelve WH07 children and the WH07 parent still sell at 59.00.",
    ],
    notes=[
        "59.00 x 0.80 = 47.20 exactly.",
        "The matched set is genuinely derived: an agent that selected all three size M rows repriced the disabled one, fails the scope gate and scores 0.0.",
        "The injection changes status only. The rubric grades price only, so the injected lane scores exactly 0.0 before the agent acts.",
    ],
)


# --------------------------------------------------------------------------
# code emitters
# --------------------------------------------------------------------------

REWARD_HELPERS = '''

def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _num(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _deleted(state):
    out = set()
    raw = _as_dict(state).get("deletedProductIds")
    if isinstance(raw, list):
        for item in raw:
            number = _num(item)
            if number is not None:
                out.add(int(number))
    return out


def _field(state, product_id, field):
    """The value the catalogue renders for one product field.

    getProducts merges state.productOverrides[id] over the seeded row
    (selectors.js:166-180), so the effective value is the override when the key
    is present and the frozen seed value otherwise. Deleted rows return the
    DELETED sentinel and can never satisfy a component.
    """
    key = str(product_id)
    if int(key) in _deleted(state):
        return DELETED
    override = _as_dict(_as_dict(_as_dict(state).get("productOverrides")).get(key))
    if field in override:
        return _num(override.get(field))
    return _num(_as_dict(SEED_ROWS.get(key)).get(field))


def _matches(state, wanted):
    for product_id, fields in wanted.items():
        for field, value in fields.items():
            got = _field(state, product_id, field)
            if got is DELETED or got is None:
                return False
            if abs(got - float(value)) > 1e-6:
                return False
    return True


def _scope_ok(state):
    """Nothing outside the matched set moved.

    This earns no credit of its own - it only gates the outcome components, so
    an agent that repriced the whole product line scores zero rather than being
    paid for restraint.
    """
    for product_id, fields in SCOPE.items():
        for field, value in fields.items():
            got = _field(state, product_id, field)
            if got is DELETED:
                return False
            if value is None:
                if got is not None:
                    return False
            elif got is None or abs(got - float(value)) > 1e-6:
                return False
    return True


def score_state(state):
    in_scope = _scope_ok(state)
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = in_scope and _matches(state, COMPONENT_TARGETS[name])
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": COMPONENT_DETAILS[name],
        })
    return round(sum(c["score"] for c in components), 6), components
'''


def emit_constants(spec):
    """SEED_ROWS / SCOPE / COMPONENT_* literals shared by both reward twins."""
    rows = line_rows(spec["parent_sku"])
    target_ids = set()
    for _name, wanted, _w in spec["components"]:
        target_ids.update(wanted)

    scope = {}
    for pid, row in rows.items():
        if pid in target_ids:
            continue
        scope[pid] = {"price": row["price"]}
        for extra in spec.get("scope_fields") or ():
            scope[pid][extra] = row[extra]
    for pid, fields in (spec.get("stock_scope") or {}).items():
        scope.setdefault(pid, {})
        scope[pid].update(fields)

    weights = {name: w for name, _t, w in spec["components"]}
    targets = {name: t for name, t, _w in spec["components"]}
    details = {}
    for name, wanted, _w in spec["components"]:
        parts = []
        for pid, fields in wanted.items():
            for field, value in fields.items():
                parts.append("product %s %s == %s" % (pid, field, value))
        details[name] = (
            ", ".join(parts)
            + ", and no row outside the "
            + spec["run_label"]
            + " "
            + spec["line_label"]
            + " run moved"
        )

    out = []
    out.append("COMPONENT_WEIGHTS = json.loads(r\"\"\"%s\"\"\")" % json.dumps(weights, indent=2))
    out.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    out.append("")
    out.append("COMPONENT_TARGETS = json.loads(r\"\"\"%s\"\"\")" % json.dumps(targets, indent=2))
    out.append("")
    out.append("COMPONENT_DETAILS = json.loads(r\"\"\"%s\"\"\")" % json.dumps(details, indent=2))
    out.append("")
    out.append("# Frozen seed rows for the whole %s line, read out of" % spec["line_label"])
    out.append("# src/data/products.json at authoring time.")
    out.append("SEED_ROWS = json.loads(r\"\"\"%s\"\"\")" % json.dumps(rows, indent=2))
    out.append("")
    out.append("# Every line member outside the matched set, with the value the")
    out.append("# catalogue must still show for it.")
    out.append("SCOPE = json.loads(r\"\"\"%s\"\"\")" % json.dumps(scope, indent=2))
    out.append("")
    out.append("DELETED = object()")
    return "\n".join(out)


def reward_py(spec):
    head = '"""Deterministic offline reward for %s.\n\n%s\n\nOnly current_state is read; nothing is diffed against initial_state.\n"""\n' % (
        spec["task_id"],
        "\n".join(spec["criteria"]),
    )
    body = [head, "import json", "", emit_constants(spec), REWARD_HELPERS.rstrip(), "", ""]
    body.append('''def evaluate(evidence):
    apps = _as_dict(_as_dict(evidence).get("apps"))
    app = _as_dict(apps.get("shopping_admin")) or _as_dict(apps.get("webarena_shopping_admin_mock"))
    state = app.get("current_state")
    if not isinstance(state, dict):
        state = {}
    score, components = score_state(state)
    return {"score": score, "components": components}
''')
    return "\n".join(body)


def nemo_reward_py(spec):
    head = '"""NeMo-Gym reward program for %s.\n\n%s\n\nRubric parity with reward.py. Reads current_state from the state API only.\n"""\n' % (
        spec["task_id"],
        "\n".join(spec["criteria"]),
    )
    body = [
        head,
        "import json",
        "import sys",
        "",
        "import requests",
        "",
        'SID = "__CUA_GYM_SID__"',
        'BASE_URL = "%s"' % URL_PLACEHOLDER,
        "",
        emit_constants(spec),
        REWARD_HELPERS.rstrip(),
        "",
        "",
        '''def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    score, _components = score_state(state)
    print("REWARD: %s" % score)


main()
''',
    ]
    return "\n".join(body)


def setup_py(spec):
    patch = spec["setup"]
    if not patch:
        return None
    overrides = patch["productOverrides"]
    guard = {}
    rows = line_rows(spec["parent_sku"])
    for pid in overrides:
        guard[pid] = rows[pid]
    head = (
        '"""NeMo-Gym setup program for %s.\n\n'
        "Injects the precondition this task branches on. shopping_admin's `set`\n"
        "action is merged over createInitialData() by the app itself\n"
        "(vite.config.js:104-107), so a partial top-level patch is safe here and\n"
        "leaves the other 43 state keys at their seeded values.\n\n"
        "The fixture is inlined as a raw triple-quoted JSON literal parsed with\n"
        "json.loads, so no JavaScript literal reaches Python source and no escape\n"
        "is eaten by the Python parser.\n\n"
        'Self-contained: standard library plus requests.\n"""\n'
    ) % spec["task_id"]
    parts = [
        head,
        "import json",
        "import sys",
        "",
        "import requests",
        "",
        'SID = "__CUA_GYM_SID__"',
        'BASE_URL = "%s"' % URL_PLACEHOLDER,
        "",
        "PATCH = json.loads(r\"\"\"%s\"\"\")" % json.dumps(patch, indent=2),
        "",
        "# The seeded values of the rows being patched, checked before the POST so",
        "# an unexpected baseline fails loudly instead of silently shifting the",
        "# task's ground truth.",
        "SEED_GUARD = json.loads(r\"\"\"%s\"\"\")" % json.dumps(guard, indent=2),
        "",
        '''
def fail(message):
    print("SETUP FAILED: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    state = response.json().get("current_state")
    if not isinstance(state, dict):
        fail("GET /go returned no current_state")
    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        fail("expected a productOverrides object in the pristine state")
    for product_id in PATCH["productOverrides"]:
        if product_id in overrides:
            fail("product " + product_id + " already carries an override")

    post = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": PATCH},
        timeout=60,
    )
    post.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    if result.get("state_diff") != {}:
        fail("state_diff is not empty after set")
    if result.get("initial_state") != result.get("current_state"):
        fail("initial_state != current_state after set")
    print("SETUP OK")


main()
''',
    ]
    return "\n".join(parts)


def replay_py(spec):
    lines = []
    lines.append('"""Golden replay draft for %s.' % spec["task_id"])
    lines.append("")
    lines.append("Click-only from the site root: left rail Catalog > Products, keyword")
    lines.append("search for the size run, tick the matched rows, Actions > Update")
    lines.append("attributes, fill the bulk form, Save. No page.goto after the landing.")
    lines.append('"""')
    lines.append("")
    lines.append("")
    lines.append("def run(page, base_url):")
    lines.append("    page.goto(base_url + \"/\")")
    lines.append("    page.get_by_role(\"link\", name=\"Catalog\").first.click()")
    lines.append("    page.get_by_role(\"link\", name=\"Products\", exact=True).first.click()")
    lines.append("    page.wait_for_selector(\"table.data-grid\")")
    lines.append("")
    groups = {}
    for pid, price in spec["replay_prices"].items():
        groups.setdefault(price, []).append(pid)
    for price, ids in groups.items():
        lines.append("    search = page.locator(\"input.data-grid-search-control\")")
        lines.append("    search.fill(%r)" % spec["search_hint"])
        lines.append("    search.press(\"Enter\")")
        lines.append("    page.wait_for_timeout(400)")
        for pid in ids:
            lines.append("    page.locator(\"#idscheck%s\").check()" % pid)
        lines.append("    page.locator(\"button.action-select\").click()")
        lines.append("    page.get_by_text(\"Update attributes\", exact=True).click()")
        lines.append("    page.locator(\"#bulk-price\").fill(%r)" % price)
        if spec.get("replay_qty"):
            lines.append("    page.locator(\"#bulk-qty\").fill(%r)" % spec["replay_qty"])
        if spec.get("replay_status"):
            lines.append("    page.locator(\"#bulk-status\").select_option(%r)" % spec["replay_status"])
        lines.append("    page.get_by_role(\"button\", name=\"Save\").click()")
        lines.append("    page.wait_for_timeout(400)")
        lines.append("")
    if spec.get("replay_restock"):
        pid, qty = spec["replay_restock"]
        lines.append("    search = page.locator(\"input.data-grid-search-control\")")
        lines.append("    search.fill(%r)" % spec["search_hint"])
        lines.append("    search.press(\"Enter\")")
        lines.append("    page.wait_for_timeout(400)")
        lines.append("    page.locator(\"#idscheck%s\").check()" % pid)
        lines.append("    page.locator(\"button.action-select\").click()")
        lines.append("    page.get_by_text(\"Update attributes\", exact=True).click()")
        lines.append("    page.locator(\"#bulk-qty\").fill(%r)" % qty)
        lines.append("    page.locator(\"#bulk-stock-status\").select_option(\"1\")")
        lines.append("    page.get_by_role(\"button\", name=\"Save\").click()")
        lines.append("    page.wait_for_timeout(400)")
        lines.append("")
    return "\n".join(lines)


def task_json(spec, has_setup):
    metadata = {
        "style": spec["style"],
        "difficulty": spec["difficulty"],
        "shape": spec["shape"],
        "skills": spec["skills"],
        "skill_chain": spec["skill_chain"],
        "official_analogues": spec["analogues"],
        "hard_criteria": spec["hard_criteria"],
        "topic": "size-run repricing",
        "lane": "size_run_reprice",
        "inspiration_ids": ["webarena-778", "webarena-777", "webarena-780", "webarena-551", "webarena-769"],
        "authoring_notes": spec["notes"],
    }
    if has_setup:
        metadata["injected_preconditions"] = spec["injected"]
    return {
        "schema_version": 2,
        "task_id": spec["task_id"],
        "instruction": spec["instruction"],
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
        "metadata": metadata,
    }


def main():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []
    for spec in TASKS:
        bundle = os.path.join(SITE_DIR, spec["task_id"])
        os.makedirs(bundle, exist_ok=True)
        setup_src = setup_py(spec)

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump({
                "task_id": spec["task_id"],
                "task_instruction": spec["instruction"],
                "app_dir": APP_DIR,
                "start_path": "/",
                "difficulty": spec["difficulty"],
                "success_criteria": spec["criteria"],
            }, fh, indent=2)
            fh.write("\n")

        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(task_json(spec, setup_src is not None), fh, indent=2)
            fh.write("\n")

        reward_src = reward_py(spec)
        nemo_src = nemo_reward_py(spec)
        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_src)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_src)
        if setup_src is not None:
            with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        row = {"task_payload": {
            "task_id": spec["task_id"],
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
                "bundle_id": spec["task_id"],
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": nemo_src,
            },
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        rows.append(row)

        with open(os.path.join(REPLAY_DIR, spec["task_id"] + ".py"), "w") as fh:
            fh.write(replay_py(spec))

        index["tasks"].append({"task_id": spec["task_id"],
                               "path": "../../%s/task.json" % spec["task_id"]})

    with open(os.path.join(BATCH_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
