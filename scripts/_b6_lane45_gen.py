#!/usr/bin/env python3
"""Batch-6 lane 45 generator: shopping_admin R5 -> A4.

Chain: filter the Catalog > Products grid by a Quantity RANGE, then apply one
bulk action to exactly the rows the filter matched.

Verified mechanism (read at authoring time, nothing under hub/ modified):
  * quantity range filter  ProductGrid.jsx:176-183 (filterType 'range')
                           gridUtils.js:179-194   (matchesFilter numeric range)
                           AdminGrid.jsx:674-704  (#filter-product_listing-qty[-to])
  * mass actions           ProductGrid.jsx:452-485 (delete / status_enable /
                           status_disable / update_attributes)
  * bulk attribute form    ProductGrid.jsx:527-577 -> applyBulkAttributes :487-502
                           -> patchProduct :498
  * writer                 AppContext.jsx:219-227  patchProduct -> productOverrides
                           AppContext.jsx:240-245  deleteProducts -> deletedProductIds
  * reader                 selectors.js:164-181    getProducts merges the override
                           over the seed row; ProductGrid columns render
                           r.qty (:179), r.price (:170), r.status (:209),
                           r.visibility (:198), r.salable_quantity (:83-90).
                           r.is_in_stock is read by ProductEdit.jsx:143 and
                           rendered as the Stock Status select at :862-865.
  * page size              gridUtils.js:35-51 GRID_PAGE_SIZES['product_listing']
                           = 200, overriding ProductGrid's defaultPageSize=20.
  * select all matches     AdminGrid.jsx:319 selectAll() -> result.allMatching
"""

import json
import os
import shutil

ROOT = "/home/ubuntu/CUA-Gym"
MOCK = os.path.join(ROOT, "hub/websites/webarena_shopping_admin_mock")
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/qty_range_bulk_attributes")
APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

with open(os.path.join(MOCK, "src/data/products.json")) as fh:
    PRODUCTS = {int(r["entity_id"]): r for r in json.load(fh)}

FIELDS = ("price", "qty", "salable_quantity", "status", "visibility", "is_in_stock")


def seed(pid):
    row = PRODUCTS[int(pid)]
    return {f: float(row[f]) for f in FIELDS}


# --------------------------------------------------------------------------- specs

TASKS = [
    {
        "id": "qty_range_bulk_attributes_nearly_empty_out_of_stock_001",
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "In Catalog > Products, filter the grid on Quantity from 1 to 5 and mark every "
            "product the filter returns as Out of Stock. Nothing outside that filtered set "
            "may change."
        ),
        "injection": {},
        "qty_range": (1, 5),
        "matched": [986, 1182, 1478],
        "changed": {986: {"is_in_stock": 0.0}, 1182: {"is_in_stock": 0.0}, 1478: {"is_in_stock": 0.0}},
        "scope": {
            986: {"qty": 4.0, "salable_quantity": 4.0},
            1182: {"qty": 3.0, "salable_quantity": 3.0},
            1478: {"qty": 3.0, "salable_quantity": 3.0},
            1415: {"is_in_stock": 1.0, "qty": 14.0, "salable_quantity": 14.0},
            872: {"is_in_stock": 0.0, "qty": 0.0, "salable_quantity": 0.0},
        },
        "guarded": ["is_in_stock", "qty", "salable_quantity"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> bulk Update attributes sets Stock Status = Out of Stock on exactly the matched rows",
        "criteria": [
            "Products 986, 1182 and 1478 each carry stock status Out of Stock.",
            "Their quantities are still 4, 3 and 3.",
            "No other product's stock status or quantity moved, and nothing was deleted.",
        ],
        "notes": [
            "Pristine seed: the only rows with a Quantity between 1 and 5 are 986 (4), 1182 (3) and 1478 (3).",
            "The lower bound of 1 is load-bearing: 150 configurable/bundle/grouped parents carry qty 0.0 and are all is_in_stock 1 (CORRECTIONS #72b).",
            "1415 sits at 14 and 872 at 0, both just outside the band, and both are gated in scope.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_restock_low_runners_to_sixty_002",
        "style": "explicit",
        "shape": "mutation",
        "instruction": (
            "A replenishment order lands tomorrow and the warehouse wants every short line "
            "brought up to a flat 60 units. Open Catalog > Products, expand the Filters panel, "
            "set the Quantity filter from 1 to 14 and apply it. Select all the rows that come "
            "back and use Actions > Update attributes to set their Quantity to 60. Products "
            "outside that filtered set keep the quantity they have now."
        ),
        "injection": {},
        "qty_range": (1, 14),
        "matched": [986, 1182, 1415, 1478],
        "changed": {
            986: {"qty": 60.0, "salable_quantity": 60.0},
            1182: {"qty": 60.0, "salable_quantity": 60.0},
            1415: {"qty": 60.0, "salable_quantity": 60.0},
            1478: {"qty": 60.0, "salable_quantity": 60.0},
        },
        "scope": {872: {"qty": 0.0, "salable_quantity": 0.0}},
        "guarded": ["qty", "salable_quantity"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> bulk Update attributes sets Quantity = 60 on exactly the matched rows",
        "criteria": [
            "Products 986, 1182, 1415 and 1478 each show Quantity 60 and Salable Quantity 60.",
            "Product 872 still shows Quantity 0.",
            "No other product's quantity moved, and nothing was deleted.",
        ],
        "notes": [
            "Pristine seed: the qty domain is {0, 3, 4, 14, 100}, so 1-14 matches exactly four rows.",
            "872 is the qty-0 simple product that a 0-14 filter would wrongly sweep in; it is gated.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_single_digit_lines_disabled_003",
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "Anything down to single digits comes off sale until it is restocked. In "
            "Catalog > Products, filter on Quantity from 1 to 9 and disable every product "
            "the filter returns. Leave every other product enabled."
        ),
        "injection": {
            15: {"qty": 7, "salable_quantity": 7},
            17: {"qty": 9, "salable_quantity": 9},
            21: {"qty": 8, "salable_quantity": 8},
            19: {"qty": 16, "salable_quantity": 16},
            22: {"qty": 11, "salable_quantity": 11},
        },
        "qty_range": (1, 9),
        "matched": [15, 17, 21, 986, 1182, 1478],
        "changed": {p: {"status": 2.0} for p in (15, 17, 21, 986, 1182, 1478)},
        "scope": {
            19: {"status": 1.0},
            22: {"status": 1.0},
            1415: {"status": 1.0},
            872: {"status": 1.0},
        },
        "guarded": ["status"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> Actions > Change status / Disable on exactly the matched rows",
        "criteria": [
            "Products 15, 17, 21, 986, 1182 and 1478 are Disabled.",
            "Products 19, 22, 1415 and 872 are still Enabled.",
            "No other product's status moved, and nothing was deleted.",
        ],
        "notes": [
            "Injected Gear stock: 15 -> 7, 17 -> 9, 21 -> 8 are inside the band; 22 -> 11 and 19 -> 16 are the boundary distractors.",
            "Seeded 986 (4), 1182 (3) and 1478 (3) join the matched set; 1415 (14) and every qty-0 parent stay out.",
            "All 2040 seeded products are status 1, so the untouched lane scores 0.0 by construction.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_scarcity_price_top_of_band_004",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "Scarcity pricing. In Catalog > Products, filter on Quantity from 20 to 35, then "
            "reprice every product in that filtered group to the highest price already showing "
            "in the group. No product outside the group is repriced."
        ),
        "injection": {
            1: {"qty": 28, "salable_quantity": 28},
            4: {"qty": 31, "salable_quantity": 31},
            9: {"qty": 24, "salable_quantity": 24},
            3: {"qty": 37, "salable_quantity": 37},
            11: {"qty": 19, "salable_quantity": 19},
        },
        "qty_range": (20, 35),
        "matched": [1, 4, 9],
        "changed": {1: {"price": 45.0}, 9: {"price": 45.0}},
        "scope": {4: {"price": 45.0}, 3: {"price": 38.0}, 11: {"price": 33.0}},
        "guarded": ["price"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> read the highest price in the matched group -> bulk Update attributes writes that absolute price back onto the group",
        "criteria": [
            "Products 1 and 9 sell at $45.00.",
            "Product 4 still sells at $45.00.",
            "Products 3 and 11 still sell at $38.00 and $33.00, and no other product was repriced.",
        ],
        "notes": [
            "Matched prices are 34.00 (id 1), 45.00 (id 4) and 32.00 (id 9). The maximum 45.00 is unique with an 11.00 margin over the runner-up.",
            "Id 4 already holds the derived price, so it carries no component weight and sits in the scope gate instead; the untouched lane scores 0.0.",
            "Distractors 3 (qty 37) and 11 (qty 19) bracket the band and carry prices that a sloppy sweep would overwrite.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_trial_line_deletion_005",
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "The trial lines we never reordered are the only stock between 15 and 18 units. "
            "In Catalog > Products, filter on Quantity from 15 to 18 and delete every product "
            "the filter returns. No other product record is removed."
        ),
        "injection": {
            8: {"qty": 16, "salable_quantity": 16},
            10: {"qty": 15, "salable_quantity": 15},
            14: {"qty": 18, "salable_quantity": 18},
            12: {"qty": 19, "salable_quantity": 19},
            5: {"qty": 14, "salable_quantity": 14},
        },
        "qty_range": (15, 18),
        "matched": [8, 10, 14],
        "changed": {8: {"__deleted__": 1.0}, 10: {"__deleted__": 1.0}, 14: {"__deleted__": 1.0}},
        "scope": {
            12: {"qty": 19.0, "salable_quantity": 19.0, "status": 1.0},
            5: {"qty": 14.0, "salable_quantity": 14.0, "status": 1.0},
            1415: {"qty": 14.0, "salable_quantity": 14.0, "status": 1.0},
        },
        "guarded": ["qty", "salable_quantity", "status", "price", "visibility", "is_in_stock"],
        "allowed_deleted": [8, 10, 14],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> Actions > Delete on exactly the matched rows",
        "criteria": [
            "Products 8, 10 and 14 are deleted.",
            "No other product id appears in the deleted list.",
            "Products 12, 5 and 1415 keep the quantity and status they had.",
        ],
        "notes": [
            "Injected bag stock: 8 -> 16, 10 -> 15, 14 -> 18 inside the band; 12 -> 19 and 5 -> 14 are the one-unit-outside distractors.",
            "Seeded 1415 also sits at 14 and is a second lower-boundary distractor that needs no injection.",
            "Deletion is scored on deletedProductIds, so partial credit survives while an over-broad sweep fails the subset gate.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_thin_stock_hidden_from_catalog_006",
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "Stock is too thin to advertise. In Catalog > Products, filter on Quantity from 15 "
            "to 20 and set every matching product's Visibility to Not Visible Individually. "
            "Every other product keeps the visibility it has."
        ),
        "injection": {
            37: {"qty": 16, "salable_quantity": 16},
            39: {"qty": 18, "salable_quantity": 18},
            43: {"qty": 20, "salable_quantity": 20},
            41: {"qty": 22, "salable_quantity": 22},
            36: {"qty": 14, "salable_quantity": 14},
        },
        "qty_range": (15, 20),
        "matched": [37, 39, 43],
        "changed": {37: {"visibility": 1.0}, 39: {"visibility": 1.0}, 43: {"visibility": 1.0}},
        "scope": {41: {"visibility": 4.0}, 36: {"visibility": 4.0}, 1415: {"visibility": 1.0}},
        "guarded": ["visibility"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> bulk Update attributes sets Visibility = Not Visible Individually on exactly the matched rows",
        "criteria": [
            "Products 37, 39 and 43 are Not Visible Individually.",
            "Products 41 and 36 are still Catalog, Search.",
            "No other product's visibility moved, and nothing was deleted.",
        ],
        "notes": [
            "Injected watch stock: 37 -> 16, 39 -> 18, 43 -> 20 inside the band; 41 -> 22 and 36 -> 14 bracket it.",
            "The three targets are seeded visibility 4, so the untouched lane scores 0.0; 1415 (qty 14, visibility 1) would be a free pass if the band were widened downward, so it is gated.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_backorder_landed_reenable_007",
        "style": "explicit",
        "shape": "mutation",
        "instruction": (
            "The backorder shipment has been booked in and the lines it refilled can go back on "
            "sale. Open Catalog > Products, expand the Filters panel, set the Quantity filter "
            "from 45 to 70 and apply it. Select every row the filter returns and use "
            "Actions > Change status > Enable. Anything still disabled outside that quantity "
            "band stays disabled."
        ),
        "injection": {
            2: {"qty": 55, "salable_quantity": 55, "status": 2},
            6: {"qty": 62, "salable_quantity": 62, "status": 2},
            13: {"qty": 48, "salable_quantity": 48, "status": 2},
            7: {"qty": 12, "salable_quantity": 12, "status": 2},
            20: {"qty": 74, "salable_quantity": 74, "status": 2},
        },
        "qty_range": (45, 70),
        "matched": [2, 6, 13],
        "changed": {2: {"status": 1.0}, 6: {"status": 1.0}, 13: {"status": 1.0}},
        "scope": {7: {"status": 2.0}, 20: {"status": 2.0}},
        "guarded": ["status"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> Actions > Change status / Enable on exactly the matched rows",
        "criteria": [
            "Products 2, 6 and 13 are Enabled.",
            "Products 7 and 20 are still Disabled.",
            "No other product's status moved, and nothing was deleted.",
        ],
        "notes": [
            "Five products are injected as Disabled with a partial restock: 2 -> 55, 6 -> 62, 13 -> 48 are inside the band; 7 -> 12 (still short) and 20 -> 74 (over the band) must stay disabled.",
            "Every seeded product is status 1, so the only Disabled rows on the grid are the five injected ones - the retrieval is what separates the three that qualify.",
            "The untouched lane leaves 2, 6 and 13 at status 2 and scores 0.0.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_level_low_shelf_to_top_008",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "Even out the short shelf. In Catalog > Products, filter on Quantity from 1 to 13, "
            "then raise every product in that filtered group to the highest Quantity showing in "
            "the group. Nothing outside the group changes."
        ),
        "injection": {
            16: {"qty": 5, "salable_quantity": 5},
            18: {"qty": 8, "salable_quantity": 8},
            22: {"qty": 13, "salable_quantity": 13},
            23: {"qty": 17, "salable_quantity": 17},
        },
        "qty_range": (1, 13),
        "matched": [16, 18, 22, 986, 1182, 1478],
        "changed": {
            p: {"qty": 13.0, "salable_quantity": 13.0} for p in (16, 18, 986, 1182, 1478)
        },
        "scope": {
            22: {"qty": 13.0, "salable_quantity": 13.0},
            23: {"qty": 17.0, "salable_quantity": 17.0},
            1415: {"qty": 14.0, "salable_quantity": 14.0},
            872: {"qty": 0.0, "salable_quantity": 0.0},
        },
        "guarded": ["qty", "salable_quantity"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> read the highest Quantity in the matched group -> bulk Update attributes writes that absolute quantity back onto the group",
        "criteria": [
            "Products 16, 18, 986, 1182 and 1478 each show Quantity 13 and Salable Quantity 13.",
            "Product 22 still shows Quantity 13.",
            "Products 23, 1415 and 872 keep 17, 14 and 0, and no other quantity moved.",
        ],
        "notes": [
            "Matched quantities are 5, 8, 13, 4, 3, 3. The maximum 13 is unique with a 5-unit margin over the runner-up 8.",
            "The upper bound is 13 rather than 14 on purpose: seeded 1415 carries a NEGATIVE stock reservation (-1), so its Salable Quantity renders 15 against a Quantity of 14 and it would be an ambiguous maximum.",
            "Id 22 already holds the derived value, so it carries no component weight and sits in the scope gate; the untouched lane scores 0.0.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_price_match_bottom_of_band_009",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "Price-match promotion. In Catalog > Products, filter on Quantity from 30 to 50 and "
            "drop every product in that filtered group to the lowest price already showing in "
            "the group. No product outside the group is repriced."
        ),
        "injection": {
            5: {"qty": 34, "salable_quantity": 34},
            11: {"qty": 44, "salable_quantity": 44},
            38: {"qty": 39, "salable_quantity": 39},
            44: {"qty": 52, "salable_quantity": 52},
            3: {"qty": 27, "salable_quantity": 27},
        },
        "qty_range": (30, 50),
        "matched": [5, 11, 38],
        "changed": {5: {"price": 33.0}, 38: {"price": 33.0}},
        "scope": {11: {"price": 33.0}, 44: {"price": 92.0}, 3: {"price": 38.0}},
        "guarded": ["price"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> read the lowest price in the matched group -> bulk Update attributes writes that absolute price back onto the group",
        "criteria": [
            "Products 5 and 38 sell at $33.00.",
            "Product 11 still sells at $33.00.",
            "Products 44 and 3 still sell at $92.00 and $38.00, and no other product was repriced.",
        ],
        "notes": [
            "Matched prices are 45.00 (id 5), 33.00 (id 11) and 54.00 (id 38). The minimum 33.00 is unique with a 12.00 margin over the runner-up.",
            "Id 11 already holds the derived price, so it carries no component weight; the untouched lane scores 0.0.",
            "Distractors 44 (qty 52) and 3 (qty 27) bracket the band.",
        ],
    },
    {
        "id": "qty_range_bulk_attributes_damaged_pallet_write_off_010",
        "style": "terse",
        "shape": "mutation",
        "instruction": (
            "A damaged pallet writes off a whole quantity band. In Catalog > Products, filter on "
            "Quantity from 21 to 26, then set those products' Quantity to 0 and mark them Out of "
            "Stock. Nothing outside that band changes."
        ),
        "injection": {
            12: {"qty": 21, "salable_quantity": 21},
            40: {"qty": 22, "salable_quantity": 22},
            42: {"qty": 25, "salable_quantity": 25},
            44: {"qty": 27, "salable_quantity": 27},
            41: {"qty": 20, "salable_quantity": 20},
        },
        "qty_range": (21, 26),
        "matched": [12, 40, 42],
        "changed": {
            p: {"qty": 0.0, "salable_quantity": 0.0, "is_in_stock": 0.0} for p in (12, 40, 42)
        },
        "scope": {
            44: {"qty": 27.0, "salable_quantity": 27.0, "is_in_stock": 1.0},
            41: {"qty": 20.0, "salable_quantity": 20.0, "is_in_stock": 1.0},
            872: {"qty": 0.0, "salable_quantity": 0.0, "is_in_stock": 0.0},
            1415: {"qty": 14.0, "salable_quantity": 14.0, "is_in_stock": 1.0},
        },
        "guarded": ["qty", "salable_quantity", "is_in_stock"],
        "allowed_deleted": [],
        "derived_from": None,
        "skill_chain": "quantity-range filter on the Products grid -> one bulk Update attributes submit sets Quantity = 0 and Stock Status = Out of Stock on exactly the matched rows",
        "criteria": [
            "Products 12, 40 and 42 each show Quantity 0 and stock status Out of Stock.",
            "Products 44 and 41 keep 27 and 20 units and stay In Stock.",
            "No other product's quantity or stock status moved, and nothing was deleted.",
        ],
        "notes": [
            "Injected stock: 12 -> 21, 40 -> 22, 42 -> 25 inside the band; 44 -> 27 and 41 -> 20 sit one unit outside each edge.",
            "872 is the one seeded product already Out of Stock; it is gated so it can never be mistaken for a matched row.",
            "applyBulkAttributes (ProductGrid.jsx:487-502) writes qty, salable_quantity and is_in_stock from a single submit, so this is one bulk action, not two.",
        ],
    },
]

ANALOGUES = {
    "qty_range_bulk_attributes_nearly_empty_out_of_stock_001": [
        "Give me the SKU of the products that have 1-3 units left",
        "Mark all Aeon capri as out of stock",
    ],
    "qty_range_bulk_attributes_restock_low_runners_to_sixty_002": [
        "Give me the product names and the sizes of the products that have 2-3 units left",
        "5 blue Cronus yoga pants with size 33 arrived, update the stock. If previous stock exist, add to it. If it does not exist previously, also update stock status to in stock.",
    ],
    "qty_range_bulk_attributes_single_digit_lines_disabled_003": [
        "Give me the material of the products that have 3 units left",
        "Disable Cora Pant from the site, they are facing some quality issues.",
    ],
    "qty_range_bulk_attributes_scarcity_price_top_of_band_004": [
        "Give me the SKU of the products that have 10 units left",
        "Increase the price of white Ingrid Running with size L and above by $17",
    ],
    "qty_range_bulk_attributes_trial_line_deletion_005": [
        "Give me the SKU of the products that have 1-3 units left",
        "Delete all pending reviews with less than 4 stars",
    ],
    "qty_range_bulk_attributes_thin_stock_hidden_from_catalog_006": [
        "Give me the product names and the sizes of the products that have 2-3 units left",
        "Disable Helios Endurance Tank from the site, they are facing some quality issues.",
    ],
    "qty_range_bulk_attributes_backorder_landed_reenable_007": [
        "Give me the name of the products that have 0 units left",
        "Disable Teton pullover hoodie from the site, they are facing some quality issues.",
    ],
    "qty_range_bulk_attributes_level_low_shelf_to_top_008": [
        "Give me the SKU of the products that have 1-3 units left",
        "We've received additional 378 brown Aero daily fitness tee in every size, please update the inventory. If previous stock exist, add to it. If it does not exist previously, also update stock status to in stock.",
    ],
    "qty_range_bulk_attributes_price_match_bottom_of_band_009": [
        "Give me the SKU of the products that have 10 units left",
        "Reduce the price of green Hollister backyard sweatshirt in all sizes by $5",
    ],
    "qty_range_bulk_attributes_damaged_pallet_write_off_010": [
        "Give me the name of the products that have 0 units left",
        "Mark all Taurus Elements Shell as out of stock",
    ],
}

INSPIRATIONS = {
    "qty_range_bulk_attributes_nearly_empty_out_of_stock_001": ["webarena-187", "webarena-505"],
    "qty_range_bulk_attributes_restock_low_runners_to_sixty_002": ["webarena-186", "webarena-768"],
    "qty_range_bulk_attributes_single_digit_lines_disabled_003": ["webarena-185", "webarena-456"],
    "qty_range_bulk_attributes_scarcity_price_top_of_band_004": ["webarena-183", "webarena-780"],
    "qty_range_bulk_attributes_trial_line_deletion_005": ["webarena-187", "webarena-774"],
    "qty_range_bulk_attributes_thin_stock_hidden_from_catalog_006": ["webarena-186", "webarena-455"],
    "qty_range_bulk_attributes_backorder_landed_reenable_007": ["webarena-184", "webarena-453"],
    "qty_range_bulk_attributes_level_low_shelf_to_top_008": ["webarena-187", "webarena-769"],
    "qty_range_bulk_attributes_price_match_bottom_of_band_009": ["webarena-183", "webarena-777"],
    "qty_range_bulk_attributes_damaged_pallet_write_off_010": ["webarena-184", "webarena-501"],
}

FIELD_LABEL = {
    "price": "price",
    "qty": "quantity",
    "salable_quantity": "salable quantity",
    "status": "status",
    "visibility": "visibility",
    "is_in_stock": "stock status",
    "__deleted__": "deletion",
}


def weights(names):
    n = len(names)
    base = 100 // n
    rem = 100 - base * n
    out = {}
    for i, name in enumerate(names):
        out[name] = round((base + (1 if i < rem else 0)) / 100.0, 4)
    return out


def raw_json(obj, indent=2):
    return json.dumps(obj, indent=indent, sort_keys=True)


def component_name(pid, fields):
    if "__deleted__" in fields:
        return "product_%s_deleted" % pid
    tag = "_".join(sorted(fields))
    return "product_%s_%s" % (pid, tag)


REWARD_BODY = '''
DELETED = object()


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

    getProducts merges state.productOverrides[id] over the frozen seed row
    (selectors.js:164-181), so the effective value is the override when the key
    is present and the seed value otherwise. A deleted row returns the DELETED
    sentinel and can never satisfy a component.
    """
    key = str(product_id)
    if int(key) in _deleted(state):
        return DELETED
    override = _as_dict(_as_dict(_as_dict(state).get("productOverrides")).get(key))
    if field in override:
        return _num(override.get(field))
    return _num(_as_dict(SEED_ROWS.get(key)).get(field))


def _matches(state, wanted):
    deleted = _deleted(state)
    for product_id, fields in wanted.items():
        for field, value in fields.items():
            if field == "__deleted__":
                if int(product_id) not in deleted:
                    return False
                continue
            got = _field(state, product_id, field)
            if got is DELETED or got is None:
                return False
            if abs(got - float(value)) > 1e-6:
                return False
    return True


def _scope_ok(state):
    """Nothing outside the matched set moved.

    This earns no credit of its own - it gates every paid component, so an agent
    that swept the whole catalogue scores zero rather than being paid for the
    rows it happened to get right.
    """
    if not _deleted(state).issubset(set(int(x) for x in ALLOWED_DELETED)):
        return False
    for product_id, fields in SCOPE.items():
        for field, value in fields.items():
            got = _field(state, product_id, field)
            if got is DELETED or got is None:
                return False
            if abs(got - float(value)) > 1e-6:
                return False
    known = set(str(k) for k in KNOWN_IDS)
    overrides = _as_dict(_as_dict(state).get("productOverrides"))
    for key, override in overrides.items():
        if str(key) in known:
            continue
        if not isinstance(override, dict):
            continue
        for field in GUARDED_FIELDS:
            if field in override:
                return False
    return True


def score_state(state):
    in_scope = _scope_ok(state)
    components = []
    for name in COMPONENT_ORDER:
        ok = in_scope and _matches(state, COMPONENT_TARGETS[name])
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": COMPONENT_DETAILS[name],
        })
    return round(sum(c["score"] for c in components), 6), components
'''


def build_reward_head(spec, comp_weights, comp_targets, comp_details, seed_rows):
    order = list(comp_weights.keys())
    return (
        "COMPONENT_ORDER = json.loads(r\"\"\"%s\"\"\")\n\n"
        "COMPONENT_WEIGHTS = json.loads(r\"\"\"%s\"\"\")\n"
        "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n\n"
        "COMPONENT_TARGETS = json.loads(r\"\"\"%s\"\"\")\n\n"
        "COMPONENT_DETAILS = json.loads(r\"\"\"%s\"\"\")\n\n"
        "# Frozen seed values read out of src/data/products.json at authoring time.\n"
        "SEED_ROWS = json.loads(r\"\"\"%s\"\"\")\n\n"
        "# Values that must still hold for rows OUTSIDE the paid set. Gate only.\n"
        "SCOPE = json.loads(r\"\"\"%s\"\"\")\n\n"
        "# Fields the correct bulk action writes. No product outside KNOWN_IDS may\n"
        "# carry any of them in productOverrides.\n"
        "GUARDED_FIELDS = json.loads(r\"\"\"%s\"\"\")\n\n"
        "KNOWN_IDS = json.loads(r\"\"\"%s\"\"\")\n\n"
        "ALLOWED_DELETED = json.loads(r\"\"\"%s\"\"\")\n"
        % (
            raw_json(order),
            raw_json(comp_weights),
            raw_json(comp_targets),
            raw_json(comp_details),
            raw_json(seed_rows),
            raw_json(spec["_scope_json"]),
            raw_json(spec["guarded"]),
            raw_json(sorted(spec["_known"])),
            raw_json(sorted(spec["allowed_deleted"])),
        )
    )


SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{why}

Read-modify-write: GET /go, patch productOverrides in the full document, POST the
whole document back with action=set. Correct whether the mock merges or replaces.

Nothing the rubric pays for is pre-satisfied, so the untouched lane scores 0.0.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url_placeholder}"

INJECTION = json.loads(r"""{injection}""")


def fail(message):
    print("SETUP FAILED: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    got = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    got.raise_for_status()
    payload = got.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        fail("GET /go returned neither current_state nor initial_state")

    overrides = state.get("productOverrides")
    if not isinstance(overrides, dict):
        fail("current_state carries no productOverrides map")
    if overrides != {{}}:
        fail("expected a pristine empty productOverrides map")
    if state.get("deletedProductIds") != []:
        fail("expected a pristine empty deletedProductIds list")

    merged = dict(overrides)
    for product_id, patch in INJECTION.items():
        row = dict(merged.get(product_id) or {{}})
        row.update(patch)
        merged[product_id] = row
    state["productOverrides"] = merged

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    posted.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    current = result.get("current_state")
    if not isinstance(current, dict):
        fail("GET /go returned no current_state after set")
    written = current.get("productOverrides")
    if not isinstance(written, dict):
        fail("productOverrides missing after set")
    for product_id, patch in INJECTION.items():
        row = written.get(product_id)
        if not isinstance(row, dict):
            fail("no override written for product " + product_id)
        for key, value in patch.items():
            if row.get(key) != value:
                fail("override mismatch for product %s field %s" % (product_id, key))
    if result.get("state_diff") != {{}}:
        fail("state_diff is not empty after set")
    print("SETUP OK")


main()
'''


def main():
    if os.path.isdir(BATCH):
        shutil.rmtree(BATCH)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)

    index_rows = []
    nemo_rows = []

    for spec in TASKS:
        tid = spec["id"]
        bundle = os.path.join(OUT, tid)
        os.makedirs(bundle, exist_ok=True)

        changed = spec["changed"]
        scope = spec["scope"]

        # every id whose guarded fields are accounted for
        known = set(str(p) for p in changed) | set(str(p) for p in scope)
        known |= set(str(p) for p in spec["injection"])
        spec["_known"] = known
        spec["_scope_json"] = {str(p): {k: float(v) for k, v in f.items()} for p, f in scope.items()}

        seed_rows = {}
        for pid in sorted(int(x) for x in known):
            seed_rows[str(pid)] = seed(pid)

        comp_targets = {}
        comp_details = {}
        names = []
        for pid in sorted(changed):
            fields = changed[pid]
            name = component_name(pid, fields)
            names.append(name)
            comp_targets[name] = {str(pid): {k: float(v) for k, v in fields.items()}}
            if "__deleted__" in fields:
                comp_details[name] = (
                    "product %s is in deletedProductIds, and no row outside the matched "
                    "quantity band was touched" % pid
                )
            else:
                bits = ", ".join(
                    "%s == %s" % (FIELD_LABEL[k], ("%g" % float(v))) for k, v in sorted(fields.items())
                )
                comp_details[name] = (
                    "product %s %s, and no row outside the matched quantity band was touched"
                    % (pid, bits)
                )
        comp_weights = weights(names)

        head = build_reward_head(spec, comp_weights, comp_targets, comp_details, seed_rows)
        criteria_block = "\n".join(spec["criteria"])

        reward_src = (
            '"""Deterministic offline reward for %s.\n\n%s\n\n'
            "Only current_state is read; nothing is diffed against initial_state.\n"
            '"""\n\nimport json\n\n%s\n%s\n\ndef evaluate(evidence):\n'
            '    apps = _as_dict(_as_dict(evidence).get("apps"))\n'
            '    app = _as_dict(apps.get("shopping_admin")) or _as_dict(apps.get("%s"))\n'
            '    state = app.get("current_state")\n'
            "    if not isinstance(state, dict):\n"
            "        state = {}\n"
            "    score, components = score_state(state)\n"
            '    return {"score": score, "components": components}\n'
            % (tid, criteria_block, head, REWARD_BODY, APP_DIR)
        )

        nemo_reward_src = (
            '"""NeMo-Gym reward program for %s.\n\n%s\n\n'
            "Rubric parity with reward.py. Reads current_state from the state API only.\n"
            '"""\n\nimport json\nimport sys\n\nimport requests\n\n'
            'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n%s\n%s\n\ndef main():\n'
            "    try:\n"
            '        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
            "        response.raise_for_status()\n"
            '        state = response.json().get("current_state")\n'
            "        if not isinstance(state, dict):\n"
            "            state = {}\n"
            "    except Exception as exc:  # noqa: BLE001 - a failed read must still score\n"
            '        print("reward read failed: %%s" %% exc, file=sys.stderr)\n'
            '        print("REWARD: 0.0")\n'
            "        return\n"
            "    score, _components = score_state(state)\n"
            '    print("REWARD: %%s" %% score)\n\n\nmain()\n'
            % (tid, criteria_block, URL_PLACEHOLDER, head, REWARD_BODY)
        )

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward_src)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward_src)

        setup_src = None
        if spec["injection"]:
            injection = {str(p): v for p, v in spec["injection"].items()}
            setup_src = SETUP_TEMPLATE.format(
                task_id=tid,
                why="\n".join(spec["notes"]),
                url_placeholder=URL_PLACEHOLDER,
                injection=raw_json(injection),
            )
            with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        instruction = spec["instruction"]

        task_instruction = {
            "task_id": tid,
            "task_instruction": instruction,
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": spec["criteria"],
        }
        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump(task_instruction, fh, indent=2)
            fh.write("\n")

        injected_pre = []
        if spec["injection"]:
            for pid in sorted(spec["injection"]):
                patch = spec["injection"][pid]
                bits = ", ".join("%s=%s" % (k, v) for k, v in sorted(patch.items()))
                injected_pre.append(
                    "productOverrides.%s -> %s (%s)" % (pid, bits, PRODUCTS[pid]["name"].strip())
                )
            injected_pre.append(
                "Purpose: populate the %d-%d quantity band with a controlled matched set plus "
                "boundary distractors, so the filter is the only way to identify the rows."
                % (spec["qty_range"][0], spec["qty_range"][1])
            )

        task = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": instruction,
            "apps": [
                {
                    "name": APP_DIR,
                    "source_name": "shopping_admin",
                    "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
                    "start_path": "/",
                    "initial_state": None,
                    "golden_state": None,
                }
            ],
            "reward_path": "reward.py",
            "requirements_path": None,
            "evidence": [],
            "source_evaluator": {},
            "source": "webarena",
            "metadata": {
                "style": spec["style"],
                "difficulty": "medium",
                "shape": spec["shape"],
                "skills": ["R5", "A4"],
                "skill_chain": spec["skill_chain"],
                "derived_from": spec["derived_from"],
                "official_analogues": ANALOGUES[tid],
                "injected_preconditions": injected_pre,
                "topic": "quantity-range filter then bulk attribute update",
                "lane": "qty_range_bulk_attributes",
                "inspiration_ids": INSPIRATIONS[tid],
                "authoring_notes": spec["notes"],
            },
        }
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(task, fh, indent=2)
            fh.write("\n")

        nemo = {
            "task_payload": {
                "task_id": tid,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": [APP_DIR],
                "start_urls": [],
                "intent": instruction,
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": tid,
                    "app_dir": APP_DIR,
                    "initial_setup": setup_src,
                    "eval_reward_code": nemo_reward_src,
                },
            }
        }
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(nemo, fh, indent=2)
            fh.write("\n")
        nemo_rows.append(nemo)
        index_rows.append({"task_id": tid, "path": "../../%s/task.json" % tid})

        write_replay(spec, comp_targets)

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({"schema_version": 2, "tasks": index_rows}, fh, indent=2)
        fh.write("\n")
    print("wrote %d bundles" % len(TASKS))


REPLAY_HEADER = '''"""Golden replay DRAFT for {task_id}.

Click-only from `/`: the left rail (adminMenu.js:45-57) reaches Catalog >
Inventory > Products, so no page.goto() beyond the landing navigation.

Grid facts this drives against:
  * filter panel toggle   [data-action="grid-filter-expand"]   (AdminGrid.jsx:440)
  * quantity range inputs #filter-product_listing-qty / -qty-to (AdminGrid.jsx:683-703)
  * apply                 [data-action="grid-filter-apply"]     (AdminGrid.jsx:731)
  * mass action menu      button.action-select[title="Select Items"] (AdminGrid.jsx:746)
  * per-row checkbox      #idscheck<entity_id>                  (AdminGrid.jsx:968-974)
  * page size is 200 for product_listing (gridUtils.js:35-51), and every matched
    set in this lane is <= 7 rows, so the whole match is on page 1 and
    "Select All" and "Select All on This Page" resolve to the same rows.

NOT VERIFIED BY THE AUTHOR - this is the draft the golden-browser agent drives
and corrects.
"""

BASE = "http://localhost:8003"

MATCHED = {matched}


def run(page, sid):
    page.on("dialog", lambda d: d.accept())
    page.goto(BASE + "/?sid=" + sid)
    page.wait_for_load_state("networkidle")

    # Catalog > Products
    page.click("text=Catalog")
    page.click("a:has-text('Products')")
    page.wait_for_load_state("networkidle")

    # Quantity range filter {lo} - {hi}
    page.click("[data-action='grid-filter-expand']")
    page.fill("#filter-product_listing-qty", "{lo}")
    page.fill("#filter-product_listing-qty-to", "{hi}")
    page.click("[data-action='grid-filter-apply']")
    page.wait_for_load_state("networkidle")

    # tick exactly the matched rows
    for pid in MATCHED:
        page.check("#idscheck%d" % pid)

'''

REPLAY_TAIL_MASS = '''    page.click("button.action-select[title='Select Items']")
    page.click("span.action-menu-item:has-text('{label}')")
    page.wait_for_load_state("networkidle")
'''

REPLAY_TAIL_BULK = '''    page.click("button.action-select[title='Select Items']")
    page.click("span.action-menu-item:has-text('Update attributes')")
    page.wait_for_selector("#bulk-price")
{fills}    page.click("button.action-primary:has-text('Save')")
    page.wait_for_load_state("networkidle")
'''


def write_replay(spec, comp_targets):
    tid = spec["id"]
    lo, hi = spec["qty_range"]
    body = REPLAY_HEADER.format(
        task_id=tid, matched=repr(sorted(spec["matched"])), lo=lo, hi=hi
    )

    changed_fields = {}
    for fields in spec["changed"].values():
        changed_fields.update(fields)

    if "__deleted__" in changed_fields:
        body += REPLAY_TAIL_MASS.format(label="Delete")
    elif set(changed_fields) == {"status"} and float(list(changed_fields.values())[0]) == 2.0:
        body += REPLAY_TAIL_MASS.format(label="Change status / Disable")
    elif set(changed_fields) == {"status"} and float(list(changed_fields.values())[0]) == 1.0:
        body += REPLAY_TAIL_MASS.format(label="Change status / Enable")
    else:
        fills = ""
        if "price" in changed_fields:
            fills += '    page.fill("#bulk-price", "%.2f")\n' % float(changed_fields["price"])
        if "qty" in changed_fields:
            fills += '    page.fill("#bulk-qty", "%d")\n' % int(float(changed_fields["qty"]))
        if "visibility" in changed_fields:
            fills += '    page.select_option("#bulk-visibility", "%d")\n' % int(
                float(changed_fields["visibility"])
            )
        if "is_in_stock" in changed_fields:
            fills += '    page.select_option("#bulk-stock-status", "%d")\n' % int(
                float(changed_fields["is_in_stock"])
            )
        body += REPLAY_TAIL_BULK.format(fills=fills)

    with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as fh:
        fh.write(body)


main()
