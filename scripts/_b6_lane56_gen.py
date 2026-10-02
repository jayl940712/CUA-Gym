#!/usr/bin/env python3
"""Batch-6 lane 56 generator — shopping_admin, R1 -> A10.

Writes ten `superlative_product_disable_*` bundles under
output/tasks/shopping_admin/, plus the lane batch directory
(GENERATION.md is written by hand, index.json / nemo_tasks.jsonl / replays here).

Every task: exactly two skills (R1 retrieval superlative + A10 lifecycle
transition), difficulty medium, start_path "/".

Verified mechanism (hub/websites/webarena_shopping_admin_mock):
  writer  src/pages/catalog/ProductGrid.jsx:470-476  mass action
          'Change status / Disable' -> patchProduct(id, {status: 2})
  writer  src/pages/catalog/ProductGrid.jsx:487-502  applyBulkAttributes
          -> patch.status (:492) / patch.is_in_stock (:496) -> patchProduct (:498)
  handler src/context/AppContext.jsx:219-227 patchProduct
          -> state.productOverrides[String(id)] (shallow merge)
  key     src/utils/dataManager.js:353 productOverrides: {}
  reader  src/utils/selectors.js:164-179 getProducts merges productOverrides
          over the static products corpus
  reader  src/pages/catalog/ProductGrid.jsx:102 rows = getProducts(state)
          and :205-213 Status column render productStatusLabel(r.status)
  label   src/utils/formatters.js:149-151  1 -> Enabled, anything else -> Disabled
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
TASK_ROOT = os.path.join(ROOT, "output", "tasks", "shopping_admin")
LANE = "superlative_product_disable"
BATCH_DIR = os.path.join(TASK_ROOT, "_batches", LANE)
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

DISABLE_ANALOGUES = [
    "Disable Teton pullover hoodie from the site, they are facing some quality issues.",
    "Disable Ryker Tee Crew Neck from the site, they are facing some quality issues.",
    "Disable Helios Endurance Tank from the site, they are facing some quality issues.",
    "Disable Cora Pant from the site, they are facing some quality issues.",
    "Disable Karmen yoga pants from the site, they are facing some quality issues.",
]
STOCK_ANALOGUES = [
    "Mark all Taurus Elements Shell as out of stock",
    "Mark all Gobi HeatTec Tee as out of stock",
    "Mark all rocco gym tank as out of stock",
    "Mark all Selene yoga hoodie as out of stock",
    "Mark all Aeon capri as out of stock",
]

MJ08 = list(range(319, 335))          # Lando Gym Jacket, 15 variants + parent 334
MS02 = list(range(559, 575))          # Ryker LumaTech Tee (V-neck), 15 + parent 574
MS09 = list(range(463, 479))          # Ryker LumaTech Tee (Crew-neck) — must stay Enabled
MT04 = list(range(671, 677))          # Helios Endurance Tank, 5 variants + parent 676
MS05 = list(range(447, 463))          # Helios EverCool Tee — must stay Enabled
WH07_CHILDREN = list(range(1115, 1130))

# Injected cycle-count for task 010. Minimum 2 on 1127 (WH07-XL-Gray),
# runner-up 11 on 1121 (WH07-M-Gray): margin 9, no tie anywhere in the family.
PHOEBE_COUNT = {
    1115: 41, 1116: 33, 1117: 58, 1118: 27, 1119: 60,
    1120: 46, 1121: 11, 1122: 52, 1123: 38, 1124: 25,
    1125: 44, 1126: 31, 1127: 2, 1128: 36, 1129: 22,
}

TASKS = [
    {
        "id": "superlative_product_disable_priciest_bag_supplier_hold_001",
        "style": "terse",
        "shape": "retrieval_writeback",
        "mode": "status",
        "targets": [4],
        "instruction": (
            "A supplier hold has landed on the single most expensive bag we list. "
            "In Catalog > Products, filter to the Bag attribute set, work out which "
            "row that is, and disable it."
        ),
        "criteria": [
            "current_state.productOverrides[\"4\"].status == 2 (24-MB05 Wayfarer Messenger Bag, the Bag attribute set's highest price once the injected update is applied).",
            "Entity 4 is the only product in current_state.productOverrides carrying status == 2.",
            "current_state.deletedProductIds is empty; no product was deleted instead of disabled.",
        ],
        "chain": (
            "R1 filter the Products grid to the Bag attribute set and sort Price "
            "descending to take the single dearest bag -> A10 run Change status / "
            "Disable on that one row"
        ),
        "derived_from": None,
        "analogues": [DISABLE_ANALOGUES[0], DISABLE_ANALOGUES[3]],
        "inspiration_ids": ["webarena-453", "webarena-456"],
        "setup": "bag_price",
        "injected": [
            "productOverrides[\"4\"] = {\"price\": 89.0} — a price rise on 24-MB05 "
            "Wayfarer Messenger Bag (seed $45.00). It makes the Bag attribute set's "
            "dearest row 24-MB05 at $89.00 rather than the seed's 24-UB02 Impulse "
            "Duffle at $74.00, so an agent answering from memory of the pristine "
            "catalogue scores 0.0. Margin $15.00 over Impulse Duffle; no tie.",
        ],
        "notes": [
            "Tie check: with the injection the Bag set (attribute_set_id 15, 14 rows) reads 89, 74, 59, 45, 45, 45, 45, 38, 36, 34, 33, 32, 32, 32 — rank 1 is unique with a $15.00 margin.",
            "Bags are simple products with no variants, so a single-row price override creates no on-screen contradiction.",
            "The disable does not remove the row from the Bag filter, so the retrieval premise survives the action.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("open_filters", None),
            ("select_attribute_set", "Bag"),
            ("apply_filters", None),
            ("sort_desc", "price"),
            ("comment", "14 records found; row 1 is 24-MB05 Wayfarer Messenger Bag at $89.00 (entity 4)."),
            ("check_rows", [4]),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_priciest_configurable_line_pull_002",
        "style": "terse",
        "shape": "derived_set_mutation",
        "mode": "status",
        "targets": MJ08,
        "instruction": (
            "Our vendor has pulled the most expensive configurable product line in "
            "the catalogue. Find it under Catalog > Products and disable all 16 of "
            "its rows: the configurable product itself and its 15 size/colour variants."
        ),
        "criteria": [
            "current_state.productOverrides carries status == 2 for entity_ids 319-334, the MJ08 Lando Gym Jacket configurable product and its fifteen variants.",
            "No other entity_id in current_state.productOverrides carries status == 2.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 filter the Products grid to Type = Configurable Product and sort "
            "Price descending to take the dearest configurable line -> A10 select "
            "that line's 16 rows and run Change status / Disable"
        ),
        "derived_from": "retire_product_line_hollister_sweatshirt_takedown_001",
        "analogues": [DISABLE_ANALOGUES[0], DISABLE_ANALOGUES[4]],
        "inspiration_ids": ["webarena-453", "webarena-457"],
        "setup": None,
        "injected": [],
        "notes": [
            "Tie check: among the 147 configurable rows the price ladder is MJ08 99.00, WJ04 84.00, MP08 82.00 — rank 1 is unique with a $15.00 margin.",
            "MH05's parent price is null; ProductGrid sortValue is Number(r.price ?? 0) (ProductGrid.jsx:174), so the three null-price rows sink to the bottom of a descending price sort and cannot be mistaken for the maximum.",
            "All 16 MJ08 rows carry price 99.00, so the family reads consistently on one screen.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("open_filters", None),
            ("select_type", "Configurable Product"),
            ("apply_filters", None),
            ("sort_desc", "price"),
            ("comment", "147 records found; row 1 is MJ08 Lando Gym Jacket at $99.00."),
            ("clear_filters", None),
            ("keyword_search", "lando"),
            ("comment", "16 records found: entity_ids 319-334."),
            ("select_all_matching", None),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_dearest_yoga_strap_retire_003",
        "style": "terse",
        "shape": "retrieval_writeback",
        "mode": "status",
        "targets": [35],
        "instruction": (
            "We are dropping the priciest strap in the Sprite Yoga Strap attribute "
            "set. Find that product in Catalog > Products and disable it."
        ),
        "criteria": [
            "current_state.productOverrides[\"35\"].status == 2 (24-WG087 Sprite Yoga Strap 10 foot, $21.00, the dearest of the three Sprite Yoga Strap rows).",
            "Entity 35 is the only product in current_state.productOverrides carrying status == 2.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 filter the Products grid to the Sprite Yoga Strap attribute set and "
            "take the highest-priced of its three rows -> A10 run Change status / "
            "Disable on that row"
        ),
        "derived_from": None,
        "analogues": [DISABLE_ANALOGUES[0], DISABLE_ANALOGUES[3]],
        "inspiration_ids": ["webarena-453", "webarena-456"],
        "setup": None,
        "injected": [],
        "notes": [
            "Tie check: attribute_set_id 13 holds exactly three rows — 24-WG087 10 foot $21.00, 24-WG086 8 foot $17.00, 24-WG085 6 foot $14.00. Rank 1 is unique with a $4.00 margin.",
            "The grouped product 'Set of Sprite Yoga Straps' (entity 46) sits in the Gear attribute set, not this one, so the filter cannot pick it up.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("open_filters", None),
            ("select_attribute_set", "Sprite Yoga Strap"),
            ("apply_filters", None),
            ("sort_desc", "price"),
            ("comment", "3 records found; row 1 is 24-WG087 Sprite Yoga Strap 10 foot at $21.00 (entity 35)."),
            ("check_rows", [35]),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_bestseller_2022_sellout_004",
        "style": "terse",
        "shape": "retrieval_writeback",
        "mode": "stock",
        "targets": [20],
        "instruction": (
            "Our number-one seller for calendar year 2022 has sold out with no "
            "restock date. Run the Bestsellers report for that year, then mark the "
            "product at the top of it Out of Stock in the catalogue."
        ),
        "criteria": [
            "current_state.productOverrides[\"20\"].is_in_stock == 0 (24-UG01 Quest Lumaflex(TM) Band, the 2022 Bestsellers rank-1 row at quantity 5).",
            "Entity 20 is the only product in current_state.productOverrides carrying is_in_stock == 0.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 configure Reports > Products > Bestsellers for 1/1/2022-12/31/2022 "
            "and read the rank-1 product -> A10 mark that product Out of Stock from "
            "the Products grid"
        ),
        "derived_from": "promote_the_bestseller",
        "analogues": [STOCK_ANALOGUES[0], STOCK_ANALOGUES[1]],
        "inspiration_ids": ["webarena-0", "webarena-501", "webarena-502"],
        "setup": None,
        "injected": [],
        "notes": [
            "Tie check, both branches of bestsellersRows: with Period=Year and a from/to inside one year, reportUtils.js:265-267 sets mainDisabled and aggregates bestsellers_daily; with a multi-year range the bestsellers_yearly table is used instead. Both give Quest Lumaflex(TM) Band at 5 with a three-way tie at 4 below it — margin 1, rank 1 unique, and the answer is the same either way.",
            "Dashboard leak check (CORRECTIONS #107): the landing Bestsellers tile (Dashboard.jsx:74-110) aggregates bestsellers_yearly across ALL years at store 0 and pins the order qty desc, price desc, id — its first row is Sprite Stasis Ball 65 cm, NOT the 2022 winner. An agent that shortcuts to the dashboard tile lands on the wrong product and scores 0.0.",
            "The Bestsellers report reads frozen aggregates, so marking the winner out of stock does not move the ranking that selected it.",
            "Keyword 'lumaflex' in the Products grid returns three rows (Quest Lumaflex Band 20, Pursuit Lumaflex Tone Band 18, Harmony Lumaflex Strength Band Kit 23) — a seeded distractor the agent must resolve on the exact name.",
        ],
        "replay": [
            ("open_report", ("Reports", "Bestsellers")),
            ("fill_report_dates", ("1/1/2022", "12/31/2022", "Year")),
            ("show_report", None),
            ("comment", "Row 1 is Quest Lumaflex(TM) Band, Order Quantity 5."),
            ("open_products_grid", None),
            ("keyword_search", "Quest Lumaflex"),
            ("check_rows", [20]),
            ("mass_action", "Update attributes"),
            ("bulk_stock", "Out of Stock"),
        ],
    },
    {
        "id": "superlative_product_disable_dearest_low_stock_row_hold_005",
        "style": "terse",
        "shape": "retrieval_writeback",
        "mode": "stock",
        "targets": [1182],
        "instruction": (
            "Everything holding between 1 and 19 units is under a stock recount. The "
            "most expensive of those rows is being pulled off sale until the count "
            "clears. Mark that one product Out of Stock."
        ),
        "criteria": [
            "current_state.productOverrides[\"1182\"].is_in_stock == 0 (WH11-S-Blue Eos V-Neck Hoodie-S-Blue, $54.00, quantity 3).",
            "Entity 1182 is the only product in current_state.productOverrides carrying is_in_stock == 0.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 apply the Products grid Quantity range filter 1-19 and take the "
            "highest-priced of the four matching rows -> A10 mark that product Out "
            "of Stock through the Update attributes bulk form"
        ),
        "derived_from": "restock_shorted_variants",
        "analogues": [STOCK_ANALOGUES[2], STOCK_ANALOGUES[4]],
        "inspiration_ids": ["webarena-503", "webarena-505"],
        "setup": None,
        "injected": [],
        "notes": [
            "CORRECTIONS #72b: 'fewer than N units' is the wrong phrasing here. 150 rows sit at quantity 0 (every configurable parent plus the bundle and grouped rows) and several of them price below $54, so an unbounded 'fewer than 20' has a different answer. The instruction states a LOWER BOUND of 1, which the grid's inclusive numeric range filter (gridUtils.js:184-192) matches exactly.",
            "Tie check: quantity 1-19 returns exactly four rows — WH11-S-Blue $54.00 (qty 3), WS08-XS-Blue $32.00 (qty 3), WS03-XS-Red $29.00 (qty 14), MSH09-36-Black $24.00 (qty 4). Rank 1 unique with a $22.00 margin.",
            "Marking the row out of stock leaves its Quantity at 3, so it stays inside the filter that selected it.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("open_filters", None),
            ("fill_range", ("qty", "1", "19")),
            ("apply_filters", None),
            ("sort_desc", "price"),
            ("comment", "4 records found; row 1 is WH11-S-Blue at $54.00 (entity 1182)."),
            ("check_rows", [1182]),
            ("mass_action", "Update attributes"),
            ("bulk_stock", "Out of Stock"),
        ],
    },
    {
        "id": "superlative_product_disable_ryker_cheaper_line_consolidation_006",
        "style": "explicit",
        "shape": "derived_set_mutation",
        "mode": "status",
        "targets": MS02,
        "instruction": (
            "Searching the Products grid for \"Ryker\" returns two different LumaTech "
            "tees: the Crew-neck line, SKU prefix MS09, and the V-neck line, SKU "
            "prefix MS02. We are consolidating onto whichever of the two carries the "
            "higher list price, so the cheaper line comes off the site. Compare the "
            "two prices, then disable all 16 catalogue rows of the cheaper line - its "
            "configurable product and all 15 size/colour variants. Every row of the "
            "other line must still read Enabled when you are done."
        ),
        "criteria": [
            "current_state.productOverrides carries status == 2 for entity_ids 559-574, the MS02 Ryker LumaTech Tee (V-neck) configurable product and its fifteen variants.",
            "No entity_id in 463-478 (the MS09 Crew-neck line) carries status == 2, and no other product does either.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 keyword-search 'ryker', read the two list prices the 32 hits split "
            "into and take the cheaper line -> A10 select that line's 16 rows and run "
            "Change status / Disable"
        ),
        "derived_from": "retire_product_line_ryker_crew_neck_only_003",
        "analogues": [DISABLE_ANALOGUES[1], DISABLE_ANALOGUES[0]],
        "inspiration_ids": ["webarena-454", "webarena-453"],
        "setup": None,
        "injected": [],
        "notes": [
            "CORRECTIONS #90 turned into a seeded distractor rather than avoided: 'ryker' matches 32 rows across MS09 and MS02. Sweeping all 32 scores 0.0, not a docked partial, because the rubric is a single exact-set statement over the disabled set.",
            "Tie check: every MS02 row is $28.00 and every MS09 row is $32.00, including both configurable parents. Margin $4.00, no tie.",
            "Batch 5's ryker task NAMED the Crew-neck line as the target. Here the target is derived from the price comparison and it is the other line, so the correct answer set is disjoint from the batch-5 task's.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("keyword_search", "ryker"),
            ("comment", "32 records found: MS09 rows at $32.00 and MS02 rows at $28.00. MS02 is the cheaper line."),
            ("open_filters", None),
            ("fill_text", ("sku", "MS02")),
            ("apply_filters", None),
            ("comment", "16 records found: entity_ids 559-574."),
            ("select_all_matching", None),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_helios_dearer_line_pull_007",
        "style": "terse",
        "shape": "derived_set_mutation",
        "mode": "status",
        "targets": MT04,
        "instruction": (
            "A search for \"Helios\" in Catalog > Products returns two lines at "
            "different list prices. The dearer one has a fabric fault: disable all "
            "six of its catalogue rows and leave the cheaper line enabled."
        ),
        "criteria": [
            "current_state.productOverrides carries status == 2 for entity_ids 671-676, the MT04 Helios Endurance Tank configurable product and its five variants.",
            "No entity_id in 447-462 (the MS05 Helios EverCool Tee line) carries status == 2, and no other product does either.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 keyword-search 'helios', read the two list prices the 22 hits split "
            "into and take the dearer line -> A10 select that line's six rows and run "
            "Change status / Disable"
        ),
        "derived_from": "retire_product_line_helios_endurance_tank_pull_004",
        "analogues": [DISABLE_ANALOGUES[2], DISABLE_ANALOGUES[0]],
        "inspiration_ids": ["webarena-455", "webarena-453"],
        "setup": None,
        "injected": [],
        "notes": [
            "CORRECTIONS #90 as a seeded distractor: 'helios' matches 22 rows — MS05 Helios EverCool Tee (16 rows, $24.00) and MT04 Helios Endurance Tank (6 rows, $32.00). Disabling all 22 scores 0.0.",
            "Tie check: uniform $24.00 against uniform $32.00, margin $8.00, no tie.",
            "The batch-5 helios task named the Endurance Tank and required Disabled AND Out of Stock. Here the line is derived from the price split and only the status transition is graded.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("keyword_search", "helios"),
            ("comment", "22 records found: MS05 rows at $24.00 and MT04 rows at $32.00. MT04 is the dearer line."),
            ("open_filters", None),
            ("fill_text", ("sku", "MT04")),
            ("apply_filters", None),
            ("comment", "6 records found: entity_ids 671-676."),
            ("select_all_matching", None),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_most_reviewed_watch_recall_008",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "mode": "status",
        "targets": [39],
        "instruction": (
            "Reports > Products Reviews lists every reviewed product beside its review "
            "count. One of the watches we sell has attracted more customer reviews "
            "than any other watch, and its vendor has just issued a recall on it. "
            "Filter that report's Product column to the watches, read off the single "
            "watch with the highest review count, then open Catalog > Products and "
            "disable that product. No other product may end up Disabled."
        ),
        "criteria": [
            "current_state.productOverrides[\"39\"].status == 2 (24-MG05 Cruise Dual Analog Watch, 4 reviews, the highest count among the nine watches).",
            "Entity 39 is the only product in current_state.productOverrides carrying status == 2.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 filter the Product Reviews Report's Product column to 'watch' and take "
            "the row with the largest Reviews count -> A10 disable that product from "
            "the Products grid"
        ),
        "derived_from": "quantify_the_praise",
        "analogues": [DISABLE_ANALOGUES[0], DISABLE_ANALOGUES[3]],
        "inspiration_ids": ["webarena-453", "webarena-456"],
        "setup": None,
        "injected": [],
        "notes": [
            "Tie check: the nine products whose name contains 'Watch' hold review counts 4 (Cruise Dual Analog Watch), 3, 3, 3, 3, 2, 2, 2 — rank 1 unique, margin 1 over a four-way tie at 3.",
            "The Reviews column of ProductReviewsReport is computed live from getReviews(state) (LegacyReports.jsx:806-812); the Average columns come from a frozen aggregate and are NOT graded (census §6 item 29).",
            "B6-39 does not bite: 689 reviews carry rating null, but the graded quantity here is a COUNT of review rows, not a rating-bounded predicate.",
            "The report's defaultSort is review_cnt desc (LegacyReports.jsx:875), so the filtered grid puts the answer in row 1 without further sorting.",
        ],
        "replay": [
            ("open_report", ("Reports", "Products Reviews")),
            ("fill_text", ("name", "watch")),
            ("legacy_search", None),
            ("comment", "9 records found; row 1 is 24-MG05 Cruise Dual Analog Watch, Reviews 4 (entity 39)."),
            ("open_products_grid", None),
            ("keyword_search", "Cruise Dual Analog Watch"),
            ("check_rows", [39]),
            ("mass_action", "Change status / Disable"),
        ],
    },
    {
        "id": "superlative_product_disable_top_ordered_2023_backorder_009",
        "style": "terse",
        "shape": "retrieval_writeback",
        "mode": "stock",
        "targets": [33],
        "instruction": (
            "Our most-ordered item of 2023 has gone on back-order. Run Reports > "
            "Products Ordered for calendar year 2023, take the product at the top of "
            "the list, and mark it Out of Stock in the catalogue."
        ),
        "criteria": [
            "current_state.productOverrides[\"33\"].is_in_stock == 0 (24-WG085 Sprite Yoga Strap 6 foot, Ordered Quantity 4 for 2023).",
            "Entity 33 is the only product in current_state.productOverrides carrying is_in_stock == 0.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 configure the Ordered Products Report for 1/1/2023-12/31/2023 and take "
            "the rank-1 SKU -> A10 mark that product Out of Stock from the Products grid"
        ),
        "derived_from": None,
        "analogues": [STOCK_ANALOGUES[1], STOCK_ANALOGUES[3]],
        "inspiration_ids": ["webarena-502", "webarena-504", "webarena-6"],
        "setup": None,
        "injected": [],
        "notes": [
            "Tie check: OrderedProductsReport (LegacyReports.jsx:541-575) sums qty_ordered over non-canceled orders with parent_item_id IS NULL. For 2023 the ladder is 24-WG085 4, then 3 (WP03-29-Purple, 24-WB07), then a long tail at 2 — rank 1 unique, margin 1.",
            "The report reads the static S.orders corpus, not getOrders(state), so the episode's own mutation cannot move the ranking.",
            "The report's SKU column gives 24-WG085 directly, which resolves to exactly one Products-grid row.",
        ],
        "replay": [
            ("open_report", ("Reports", "Ordered")),
            ("fill_legacy_dates", ("1/1/2023", "12/31/2023", "Year")),
            ("legacy_refresh", None),
            ("comment", "Row 1 is Sprite Yoga Strap 6 foot, SKU 24-WG085, Ordered Quantity 4."),
            ("open_products_grid", None),
            ("keyword_search", "24-WG085"),
            ("check_rows", [33]),
            ("mass_action", "Update attributes"),
            ("bulk_stock", "Out of Stock"),
        ],
    },
    {
        "id": "superlative_product_disable_phoebe_cycle_count_writeoff_010",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "mode": "stock",
        "targets": [1127],
        "instruction": (
            "Last night's cycle count on the Phoebe Zipper Sweatshirt has been posted "
            "to the catalogue. Of its fifteen size/colour variants, the one left "
            "holding the fewest units has been written off as damaged stock - ignore "
            "the configurable product row itself, which always shows a quantity of 0. "
            "Open Catalog > Products, find the Phoebe Zipper Sweatshirt variant with "
            "the lowest Quantity, and mark that single record Out of Stock. The other "
            "fourteen variants must stay In Stock."
        ),
        "criteria": [
            "current_state.productOverrides[\"1127\"].is_in_stock == 0 (WH07-XL-Gray Phoebe Zipper Sweatshirt-XL-Gray, quantity 2 after the injected cycle count).",
            "Entity 1127 is the only product in current_state.productOverrides carrying is_in_stock == 0.",
            "current_state.deletedProductIds is empty.",
        ],
        "chain": (
            "R1 filter the Products grid to the Phoebe Zipper Sweatshirt family and "
            "take the variant with the lowest Quantity -> A10 mark that one record "
            "Out of Stock through the Update attributes bulk form"
        ),
        "derived_from": "restock_shorted_variants",
        "analogues": [STOCK_ANALOGUES[3], STOCK_ANALOGUES[4]],
        "inspiration_ids": ["webarena-504", "webarena-505"],
        "setup": "phoebe_count",
        "injected": [
            "productOverrides[\"1115\"]..[\"1129\"] each gain {\"qty\": N, "
            "\"salable_quantity\": N} for the fifteen WH07 variants: 41, 33, 58, 27, "
            "60, 46, 11, 52, 38, 25, 44, 31, 2, 36, 22 in entity_id order. The seed "
            "has all fifteen at 100, which is a fifteen-way tie and no answer at all. "
            "The injection sets a unique minimum of 2 on WH07-XL-Gray (1127) with a "
            "margin of 9 over WH07-M-Gray (1121) at 11.",
            "qty and salable_quantity are written together so the grid's Quantity "
            "column and its Salable Quantity column (ProductGrid.jsx:83-90, minus the "
            "static reservations for WH07-S-Gray / WH07-S-White / WH07-M-White, one "
            "each) agree on the same screen. No status or is_in_stock key is injected, "
            "so the untouched lane scores exactly 0.0.",
        ],
        "notes": [
            "Ambiguity closed in the prompt: the configurable parent WH07 (entity 1130) carries qty 0.0, lower than any child. The instruction excludes it explicitly rather than relying on the agent's reading of 'variant'.",
            "The default Products-grid sort is qty ascending, so the injected rows are visible without extra work; the family is reached by keyword 'phoebe' (16 rows, WH07 only — no collision).",
            "Marking the row out of stock does not change its Quantity, so the minimum that selected it is unchanged.",
        ],
        "replay": [
            ("open_products_grid", None),
            ("keyword_search", "phoebe"),
            ("comment", "16 records found; the parent WH07 (1130) shows Quantity 0 and is excluded by the prompt."),
            ("sort_asc", "qty"),
            ("comment", "Lowest variant Quantity is 2 on WH07-XL-Gray (entity 1127); next is 11 on WH07-M-Gray."),
            ("check_rows", [1127]),
            ("mass_action", "Update attributes"),
            ("bulk_stock", "Out of Stock"),
        ],
    },
]


# --------------------------------------------------------------- reward source

REWARD_CORE = '''
COMPONENT_WEIGHTS = {
    "%(component)s": 1.0,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

# The transition key this task grades, and the value the handler writes.
#   Change status / Disable        -> productOverrides[id].status = 2
#   Update attributes / Out of Stock -> productOverrides[id].is_in_stock = 0
TRANSITION_KEY = "%(key)s"
TRANSITION_VALUE = %(value)d

# The exact set of entity_ids the derived superlative selects.
EXPECTED = %(expected)r

# Entity 872 (MP12-33-Blue Cronus Yoga Pant-33-Blue) is the one row that ships
# is_in_stock = 0 in the seeded catalogue. It is excluded so that an incidental
# re-save of that row is not read as a transition the agent performed.
SEED_OUT_OF_STOCK = [872]


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _transitioned(state):
    """entity_ids whose productOverrides patch records the graded transition."""
    found = []
    for key, patch in _dict(_dict(state).get("productOverrides")).items():
        if not isinstance(patch, dict):
            continue
        if TRANSITION_KEY not in patch:
            continue
        pid = _int(key)
        if pid is None:
            continue
        if TRANSITION_KEY == "is_in_stock" and pid in SEED_OUT_OF_STOCK:
            continue
        if _int(patch.get(TRANSITION_KEY)) == TRANSITION_VALUE:
            found.append(pid)
    return sorted(set(found))


def _deleted(state):
    out = []
    for raw in _list(_dict(state).get("deletedProductIds")):
        pid = _int(raw)
        if pid is not None:
            out.append(pid)
    return sorted(set(out))


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def score_state(state):
    """Single exact-set statement, gated on nothing having been deleted.

    CORRECTIONS #84/#110: the "nothing else moved" requirement is a GATE folded
    into the one paid component, not a component of its own -- a component whose
    truth condition is the absence of a mutation is true on the empty state.
    EXPECTED is non-empty, so this component is false on an untouched lane.
    """
    moved = _transitioned(state)
    deleted = _deleted(state)
    ok = (moved == sorted(EXPECTED)) and not deleted
    detail = "%(key)s == %(value)d on %%r (want %%r); deletedProductIds == %%r" %% (
        moved, sorted(EXPECTED), deleted,
    )
    return [{
        "name": "%(component)s",
        "score": COMPONENT_WEIGHTS["%(component)s"] if ok else 0.0,
        "details": detail,
    }]
'''


def reward_py(task, header):
    core = REWARD_CORE % {
        "component": task["component"],
        "key": task["key"],
        "value": task["value"],
        "expected": sorted(task["targets"]),
    }
    return (
        '"""%s\n\nReads the frozen evidence bundle and inspects current_state only.\n"""\n'
        % header
        + core
        + '''

def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    state = _dict(_dict(apps.get("shopping_admin")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''
    )


def nemo_reward_py(task, header):
    core = REWARD_CORE % {
        "component": task["component"],
        "key": task["key"],
        "value": task["value"],
        "expected": sorted(task["targets"]),
    }
    return (
        '"""%s\n\nGETs /go?sid=... and prints REWARD: <float> on every output path.\n"""\n'
        % header
        + '\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n'
        % URL_PLACEHOLDER
        + core
        + '''

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
    )


# ---------------------------------------------------------------- setup source

SETUP_HEAD = '''"""NeMo-Gym setup program for %(task_id)s.

%(why)s

Written as a read-modify-write: GET /go?sid=..., mutate the whole current_state
document in place, POST it back with {"action": "set"}. That is correct whether
the mock merges or replaces a partial set (output/CENSUS_ERRATA.md), and it is
what /go -- the surface the reward reads -- will report.

products.json is a STATIC bulk corpus, not a state key; the only way to move a
product field is the productOverrides sparse overlay (dataManager.js:352-353,
merged by selectors.js getProducts at :164-179).

Injects no `status` and no `is_in_stock`, so the untouched lane still scores 0.0.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url)s"

INJECTED = json.loads(r"""%(payload)s""")


def fail(message):
    sys.stderr.write("SETUP FAILED: %%s\\n" %% (message,))
    raise SystemExit(1)


def main():
    probe = requests.get(BASE_URL.rstrip("/") + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    body = probe.json()
    if not isinstance(body, dict):
        fail("/go did not return an object")
    state = body.get("current_state")
    if not isinstance(state, dict):
        state = body.get("initial_state")
    if not isinstance(state, dict):
        fail("/go returned neither current_state nor initial_state")

    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        fail("productOverrides is missing from the boot state")
    if overrides:
        fail("productOverrides is not pristine: %%r" %% (sorted(overrides),))

    merged = {}
    for key, patch in INJECTED.items():
        if "status" in patch or "is_in_stock" in patch:
            fail("injection must never pre-satisfy the rubric")
        merged[key] = dict(patch)
    if len(merged) != %(count)d:
        fail("expected %(count)d injected rows, built %%d" %% (len(merged),))

    state["productOverrides"] = merged

    response = requests.post(
        BASE_URL.rstrip("/") + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL.rstrip("/") + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    current = result.get("current_state")
    if not isinstance(current, dict):
        fail("current_state is not an object after set")
    written = current.get("productOverrides")
    if not isinstance(written, dict) or len(written) != %(count)d:
        fail("productOverrides did not persist: %%r" %% (written,))
    for key, patch in merged.items():
        got = written.get(key)
        if not isinstance(got, dict):
            fail("productOverrides[%%s] missing after set" %% (key,))
        for field, value in patch.items():
            if got.get(field) != value:
                fail("productOverrides[%%s][%%s] == %%r, want %%r" %% (key, field, got.get(field), value))
        if "status" in got or "is_in_stock" in got:
            fail("productOverrides[%%s] leaked a graded key" %% (key,))
    if current.get("deletedProductIds") != []:
        fail("deletedProductIds must start empty")
    print("SETUP OK")


main()
'''


def setup_py(task):
    kind = task["setup"]
    if kind is None:
        return None
    if kind == "bag_price":
        payload = {"4": {"price": 89.0}}
        why = (
            "Raises 24-MB05 Wayfarer Messenger Bag from its seeded $45.00 to $89.00 so\n"
            "that the Bag attribute set's dearest row is derived from the live grid rather\n"
            "than recalled from the pristine catalogue, where 24-UB02 Impulse Duffle leads\n"
            "at $74.00. Margin after the injection: $15.00, no tie."
        )
    elif kind == "phoebe_count":
        payload = {}
        for pid in WH07_CHILDREN:
            n = float(PHOEBE_COUNT[pid])
            payload[str(pid)] = {"qty": n, "salable_quantity": n}
        why = (
            "Posts a cycle count over the fifteen WH07 Phoebe Zipper Sweatshirt variants.\n"
            "The seed has all fifteen at quantity 100 - a fifteen-way tie with no answer -\n"
            "so the injection sets a unique minimum of 2 on WH07-XL-Gray (1127) with a\n"
            "margin of 9 over WH07-M-Gray (1121) at 11. qty and salable_quantity move\n"
            "together so the grid's two quantity columns agree on one screen."
        )
    else:
        raise ValueError(kind)
    return SETUP_HEAD % {
        "task_id": task["id"],
        "why": why,
        "url": URL_PLACEHOLDER,
        "payload": json.dumps(payload, indent=2, sort_keys=True),
        "count": len(payload),
    }


# --------------------------------------------------------------------- replays

REPLAY_HELPERS = '''BASE = "http://localhost:8003"   # CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL
SID = "REPLACE_ME"


def landing(page):
    page.goto("%s/?sid=%s" % (BASE, SID))
    page.wait_for_selector("nav.admin__menu-wrap")


def open_products_grid(page):
    """Left rail -> Catalog -> Products. No constructed URL (TASK4 S6)."""
    page.click("li.level-0 a.menu-item:has-text('Catalog')")
    page.click("div.submenu li.level-2 a:has-text('Products')")
    page.wait_for_selector("table.data-grid")


def open_report(page, group, leaf):
    page.click("li.level-0 a.menu-item:has-text('%s')" % group)
    page.click("div.submenu li.level-2 a:has-text('%s')" % leaf)
    page.wait_for_selector("h1")


def keyword_search(page, keyword):
    box = page.locator("input.data-grid-search-control")
    box.fill(keyword)
    box.press("Enter")
    page.wait_for_selector("span.admin__data-grid-records-count")


def open_filters(page):
    page.click("button[data-action='grid-filter-expand']")


def apply_filters(page):
    page.click("button[data-action='grid-filter-apply']")
    page.wait_for_selector("span.admin__data-grid-records-count")


def clear_filters(page):
    page.click("button[data-action='grid-filter-reset']")
    page.wait_for_selector("span.admin__data-grid-records-count")


def sort_by(page, column, direction):
    page.click("th[data-sort='%s'] span" % column)
    if direction == "desc":
        page.click("th[data-sort='%s'] span" % column)
    page.wait_for_selector("table.data-grid tbody tr")


def check_rows(page, ids):
    for pid in ids:
        page.check("#idscheck%d" % pid)


def select_all_matching(page):
    page.click("div.data-grid-multicheck-select button.action-select")
    page.click("div.data-grid-multicheck-select span.action-menu-item:has-text('Select All')")


def mass_action(page, label):
    page.click("div.admin__data-grid-action-select-wrap button.action-select")
    page.click(
        "div.admin__data-grid-action-select-wrap span.action-menu-item:has-text(\\"%s\\")"
        % label
    )
    page.wait_for_timeout(250)


def bulk_stock(page, label):
    """The Update attributes mass action opens an in-page form (ProductGrid.jsx:527-577)."""
    page.wait_for_selector("#bulk-stock-status")
    page.select_option("#bulk-stock-status", label="In Stock" if label == "In Stock" else "Out of Stock")
    page.click("form.admin__form-section button.action-primary")
    page.wait_for_timeout(250)
'''

REPLAY_STEPS = {
    "open_products_grid": lambda a: "    open_products_grid(page)",
    "open_report": lambda a: "    open_report(page, %r, %r)" % (a[0], a[1]),
    "keyword_search": lambda a: "    keyword_search(page, %r)" % (a,),
    "open_filters": lambda a: "    open_filters(page)",
    "apply_filters": lambda a: "    apply_filters(page)",
    "clear_filters": lambda a: "    clear_filters(page)",
    "sort_desc": lambda a: "    sort_by(page, %r, 'desc')" % (a,),
    "sort_asc": lambda a: "    sort_by(page, %r, 'asc')" % (a,),
    "check_rows": lambda a: "    check_rows(page, %r)" % (a,),
    "select_all_matching": lambda a: "    select_all_matching(page)",
    "mass_action": lambda a: "    mass_action(page, %r)" % (a,),
    "bulk_stock": lambda a: "    bulk_stock(page, %r)" % (a,),
    "comment": lambda a: "    # %s" % (a,),
    "select_attribute_set": lambda a: (
        "    page.select_option(\"select[name='attribute_set_id']\", label=%r)" % (a,)
    ),
    "select_type": lambda a: "    page.select_option(\"select[name='type_id']\", label=%r)" % (a,),
    "fill_text": lambda a: "    page.fill(\"input[name='%s']\", %r)" % (a[0], a[1]),
    "fill_range": lambda a: (
        "    page.fill(\"input[name='%s[from]']\", %r)\n"
        "    page.fill(\"input[name='%s[to]']\", %r)" % (a[0], a[1], a[0], a[2])
    ),
    "fill_report_dates": lambda a: (
        "    page.select_option('#sales_report_period_type', label=%r)\n"
        "    page.fill('#sales_report_from', %r)\n"
        "    page.fill('#sales_report_to', %r)" % (a[2], a[0], a[1])
    ),
    "show_report": lambda a: "    page.click('#filter_form_submit')\n    page.wait_for_selector('table.data-grid')",
    "fill_legacy_dates": lambda a: (
        "    page.select_option('#gridProductsSold_report_period', label=%r)\n"
        "    page.fill('#gridProductsSold_period_date_from', %r)\n"
        "    page.fill('#gridProductsSold_period_date_to', %r)" % (a[2], a[0], a[1])
    ),
    "legacy_refresh": lambda a: "    page.click(\"button:has-text('Refresh')\")\n    page.wait_for_selector('table.data-grid')",
    "legacy_search": lambda a: "    page.click('#widget-button-2')\n    page.wait_for_selector('table.data-grid')",
}


def replay_py(task):
    lines = []
    for name, arg in task["replay"]:
        lines.append(REPLAY_STEPS[name](arg))
    body = "\n".join(lines)
    return (
        '"""Golden replay draft for %s.\n\n'
        "Click-only from start_path \"/\" (TASK4 S6): the landing navigation is the only\n"
        "goto, and every scored control is reached by clicking rendered links and buttons.\n\n"
        "Derived target: %s\n"
        '"""\n\n%s\n\ndef run(page):\n    landing(page)\n%s\n'
        % (task["id"], task["target_note"], REPLAY_HELPERS, body)
    )


# ------------------------------------------------------------------- emission

def build():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    nemo_lines = []

    for task in TASKS:
        task["key"] = "status" if task["mode"] == "status" else "is_in_stock"
        task["value"] = 2 if task["mode"] == "status" else 0
        task["component"] = (
            "exactly_the_derived_rows_are_disabled"
            if task["mode"] == "status"
            else "exactly_the_derived_rows_are_out_of_stock"
        )
        task["target_note"] = "entity_ids %s -> %s = %d" % (
            sorted(task["targets"]), task["key"], task["value"],
        )

        tdir = os.path.join(TASK_ROOT, task["id"])
        os.makedirs(tdir, exist_ok=True)

        r_header = "Deterministic reward for %s.\n\n%s" % (task["id"], task["notes"][0])
        n_header = "NeMo-Gym reward program for %s.\n\n%s" % (task["id"], task["notes"][0])

        with open(os.path.join(tdir, "reward.py"), "w") as fh:
            fh.write(reward_py(task, r_header))
        with open(os.path.join(tdir, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward_py(task, n_header))

        setup_src = setup_py(task)
        if setup_src is not None:
            with open(os.path.join(tdir, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        instruction = {
            "task_id": task["id"],
            "task_instruction": task["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": task["criteria"],
        }
        with open(os.path.join(tdir, "task_instruction.json"), "w") as fh:
            json.dump(instruction, fh, indent=2)
            fh.write("\n")

        manifest = {
            "schema_version": 2,
            "task_id": task["id"],
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
                "skills": ["R1", "A10"],
                "skill_chain": task["chain"],
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "injected_preconditions": task["injected"],
                "topic": "shopping_admin superlative product then status transition",
                "lane": LANE,
                "inspiration_ids": task["inspiration_ids"],
                "authoring_notes": [
                    "Grounded in hub/websites/webarena_shopping_admin_mock as served.",
                    "Writer: ProductGrid.jsx:470-476 (Change status / Disable) and :487-502 (Update attributes) -> patchProduct AppContext.jsx:219-227 -> state.productOverrides.",
                    "Reader: selectors.js:164-179 getProducts merges productOverrides over the static corpus; ProductGrid.jsx:102 consumes it and :205-213 renders the Status column through productStatusLabel (formatters.js:149-151).",
                    "Rubric is a single exact-set statement gated on deletedProductIds being empty (CORRECTIONS #84/#110): an over-broad sweep scores 0.0, not a docked partial.",
                ] + task["notes"],
            },
        }
        if setup_src is not None:
            manifest["apps"][0]["initial_state"] = None
        with open(os.path.join(tdir, "task.json"), "w") as fh:
            json.dump(manifest, fh, indent=2)
            fh.write("\n")

        row = {"task_payload": {
            "task_id": task["id"],
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
                "bundle_id": task["id"],
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward_py(task, n_header),
            },
        }}
        with open(os.path.join(tdir, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        nemo_lines.append(json.dumps(row))

        with open(os.path.join(REPLAY_DIR, task["id"] + ".py"), "w") as fh:
            fh.write(replay_py(task))

        index["tasks"].append({"task_id": task["id"], "path": "%s/task.json" % task["id"]})

    with open(os.path.join(BATCH_DIR, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "w") as fh:
        fh.write("\n".join(nemo_lines) + "\n")

    print("wrote %d bundles" % (len(TASKS),))


if __name__ == "__main__":
    build()
