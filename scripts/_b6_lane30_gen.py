#!/usr/bin/env python3
"""Batch-6 lane 30 generator — shopping, R5 -> A4 (price-band facet cell -> cart).

Emits ten schema-v2 bundles under output/tasks/shopping/<task_id>/ plus the
lane's GENERATION.md and golden-replay drafts.

Every target was enumerated by scripts/_b6_lane30_probe.py, which reimplements
catalog.js resolveListing()/priceFacets() against src/data/. Facet cell counts
in the sidebar (source captures) equal the derived pool for every cell used
here, and none of the faceted URLs is an exact capture, so the grid comes from
`pool.slice()` and the target renders on page 1 at 12/24/36 per page.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/price_band_cell_to_cart")
REPLAYS = os.path.join(BATCH, "replays")

APP = "webarena_shopping_mock"

# The three lines the shopping mock's cart boots with (src/data/cart.json).
SEEDED = [
    (15033, "B087QSCXGT"),
    (15787, "B08JLHHCM6"),
    (10617, "B09LQTV3RX"),
]

ANALOGUE_MAKEUP = 'Open the "makeup remover" category page filtered to price from $20.00 to $29.99'
ANALOGUE_DENTAL = 'Open the "children dental care" category page filtered to price to $200 and above'
ANALOGUE_WOMEN = 'Open the "women shoes" category page filtered to under $100'
ANALOGUE_MEN = 'Open the "men shoes" category page filtered to under $10'
ANALOGUE_TABS = "Add the product with the lowest per unit price from my open tabs to the shopping cart"
ANALOGUE_MEAT = (
    "Buy the highest rated product from the meat substitute category within a budget "
    "between 100 and 200. Discard any items in your cart if it is not empty."
)


def line(item_id, product_id, sku, name, price, qty=1):
    """A cart line in addToCart's convention (AppContext.jsx:251-277).

    addToCart pushes itemId/productId/sku/name/price/qty/options and nothing
    else — the seeded rows additionally carry `rowTotal`, which the handler
    never writes and no renderer reads (CartPage.jsx:35 recomputes).
    """
    return {
        "itemId": item_id,
        "productId": product_id,
        "sku": sku,
        "name": name,
        "price": price,
        "qty": qty,
        "options": [],
    }


TASKS = [
    {
        "id": "price_band_cell_to_cart_cakes_hundred_band_001",
        "instruction": (
            "Sorting out dessert for the office party. In the Cakes category use the "
            "Shop By price filter to open the $100.00 - $199.99 band, then add the "
            "single cake it lists to my shopping cart."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "start_path": "/",
        "category": "Cakes",
        "category_path": "/grocery-gourmet-food/breads-bakery/cakes.html",
        "facet_label": "$100.00 - $199.99",
        "facet_param": "100-200",
        "nav": ["Grocery & Gourmet Food", "Breads & Bakery", "Cakes"],
        "targets": [
            {
                "id": 49382,
                "sku": "B07Q86P1WR",
                "name": "Sweet Street Iced Chocolate Thunder 3 Layer Cake 4 lb (14 Slice) Pack of 2",
                "price": 157.99,
                "qty_rule": "at_least_one",
            }
        ],
        "setup": None,
        "derived_from": "facet_cell_single_result_cakes_over_400_002",
        "analogues": [ANALOGUE_MAKEUP, ANALOGUE_TABS],
        "notes": [
            "Category 292 Grocery & Gourmet Food > Breads & Bakery > Cakes, 69 seeded "
            "listable products == categories.json dbProductCount 69, one of the 22 "
            "fully-seeded categories.",
            "The captured Price facet for /grocery-gourmet-food/breads-bakery/cakes.html "
            "advertises 66 / 1 / 1 / 1 for $0.00-$99.99, $100.00-$199.99, "
            "$200.00-$299.99 and $400.00 and above; each source count equals the "
            "derived pool count exactly.",
            "?price=100-200 yields exactly one product, id 49382 at $157.99 "
            "(catalog.js:1167-1173, v >= 100 && v < 200). No tie is possible in a "
            "one-row cell.",
            "The faceted URL is not an exact capture, so items come from pool.slice() "
            "and the single row renders on page 1 at every allowed page size — the "
            "CORRECTIONS #58 capture/derive gap cannot bite here.",
            "49382 has no entry in productOptions.json, so ProductGrid.jsx:63-66 does "
            "not divert the tile Add to Cart to the PDP; either route adds the line.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_virtual_reality_lone_bucket_002",
        "instruction": (
            "In the Virtual Reality category exactly one price bucket in the Shop By "
            "sidebar shows a single item. Open that bucket and put the product it "
            "returns in my cart."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "start_path": "/",
        "category": "Virtual Reality",
        "category_path": "/video-games/pc/virtual-reality.html",
        "facet_label": "$1,000.00 and above",
        "facet_param": "1000-",
        "nav": ["Video Games", "PC", "Virtual Reality"],
        "targets": [
            {
                "id": 74694,
                "sku": "B098K2KCCP",
                "name": (
                    "ZNBJJWCP Original VR 3D Immersive Virtual Reality Glasses Cardboard "
                    "VR Box Headset for 5.0-6.0 inch Smartphone"
                ),
                "price": 1426.65,
                "qty_rule": "at_least_one",
            }
        ],
        "setup": "empty_cart",
        "derived_from": None,
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_MEAT],
        "notes": [
            "Category 247 Video Games > PC > Virtual Reality, 55 seeded listable "
            "products == dbProductCount 55.",
            "CORRECTIONS #41: Virtual Reality has no source capture, so priceFacets() "
            "takes the DERIVED branch (catalog.js:1284-1305). span = 1426.65 - 2.39 "
            "= 1424.26, STEPS picks 500, giving two buckets: $0.00 - $499.99 (54 items) "
            "and $1,000.00 and above (1 item, href price=1000-). Exactly one bucket "
            "carries the count 1, so 'the bucket with a single item' has one reading.",
            "Target 74694 at $1,426.65, no productOptions entry.",
            "initial_setup empties the cart so the resulting collection is exactly one "
            "line; it injects nothing the rubric pays for.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_mp3_three_hundred_band_003",
        "instruction": (
            "I want the portable speaker that sits in the $300 bracket. Open Electronics > "
            "Portable Audio & Video > MP3 & MP4 Player Accessories, then in the Shop By > "
            "Price block in the left sidebar click the '$300.00 - $399.99' band. Exactly "
            "one product survives that filter. Add that product to my shopping cart at "
            "quantity 1, either from its tile or from its own product page, and leave the "
            "three items already in my cart alone."
        ),
        "style": "explicit",
        "shape": "retrieval_writeback",
        "start_path": "/",
        "category": "MP3 & MP4 Player Accessories",
        "category_path": "/electronics/portable-audio-video/mp3-mp4-player-accessories.html",
        "facet_label": "$300.00 - $399.99",
        "facet_param": "300-400",
        "nav": ["Electronics", "Portable Audio & Video", "MP3 & MP4 Player Accessories"],
        "targets": [
            {
                "id": 41297,
                "sku": "B09Q3BQQ3V",
                "name": (
                    "WDBBY 50W Music Column Portable Smart Tweeter Bluetooth Speaker Deep "
                    "Bass Subwoofer Wireless Soundbar Audio System"
                ),
                "price": 383.98,
                "qty_rule": "at_least_one",
            }
        ],
        "setup": None,
        "derived_from": None,
        "analogues": [ANALOGUE_MAKEUP, ANALOGUE_TABS],
        "notes": [
            "Category 255, 54 seeded listable == dbProductCount 54. Captured Price "
            "facet: 44 / 6 / 1 / 2 / 1 for $0.00-$99.99, $100.00-$199.99, "
            "$300.00-$399.99, $400.00-$499.99, $500.00 and above; all five source "
            "counts equal the derived pool.",
            "CORRECTIONS #61 lists mp3-mp4-player-accessories as carrying a SORTED "
            "capture (p=3 name). That capture's listingKey includes "
            "product_list_order/p, so it is not consulted for "
            "?price=300-400; the faceted page is derived.",
            "Target 41297 at $383.98, no productOptions entry.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_playstation_top_band_004",
        "instruction": (
            "Under Video Games > Legacy Systems > PlayStation Systems, open the highest "
            "price band the Shop By sidebar offers and add the one product it lists to "
            "my cart."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "start_path": "/video-games.html",
        "category": "PlayStation Systems",
        "category_path": "/video-games/legacy-systems/playstation-systems.html",
        "facet_label": "$400.00 and above",
        "facet_param": "400-500",
        "nav": ["Legacy Systems", "PlayStation Systems"],
        "targets": [
            {
                "id": 37971,
                "sku": "B009DD2RJ2",
                "name": "Sony PlayStation Vita Sapphire Blue 3G/Wi-Fi PCH-1100 Ab04",
                "price": 400.28,
                "qty_rule": "at_least_one",
            }
        ],
        "setup": "empty_cart",
        "derived_from": None,
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_MEAT],
        "notes": [
            "Category 226, 176 seeded listable == dbProductCount 176. Captured Price "
            "facet: 169 / 3 / 2 / 1 / 1; the last bucket is labelled "
            "'$400.00 and above' and its href carries price=400-500 (a source quirk "
            "preserved verbatim, the same shape as kids-bedding's 80-90).",
            "The highest band is unique — there is exactly one bucket below no other "
            "— and it holds exactly one product, id 37971 at $400.28. The next band "
            "down ($300.00 - $399.99) holds 77590 at $346.48, so an agent that clicks "
            "one row too high carts a different product and scores 0.0.",
            "37971 has no productOptions entry.",
            "start_path is the Video Games department page; Legacy Systems and "
            "PlayStation Systems are rendered descendants of it in the NavBand and in "
            "the page's own category facet.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_meal_kit_hundred_band_005",
        "instruction": (
            "Stocking the freezer. In Fresh Meal Kits open the $100.00 - $199.99 price "
            "band and add two units of the only product listed there to my shopping cart."
        ),
        "style": "terse",
        "shape": "mutation",
        "start_path": "/",
        "category": "Fresh Meal Kits",
        "category_path": "/grocery-gourmet-food/fresh-meal-kits.html",
        "facet_label": "$100.00 - $199.99",
        "facet_param": "100-200",
        "nav": ["Grocery & Gourmet Food", "Fresh Meal Kits"],
        "targets": [
            {
                "id": 80034,
                "sku": "B07GXF3PBP",
                "name": (
                    "Elements Meals | Broccoli Cinnamon Pork | 10-Pack | Healthy Freeze "
                    "Dried Meals | Whole30 Approved | Delicious, Backpacking and "
                    "Camping Food | High Protein"
                ),
                "price": 107.99,
                "qty_rule": "exactly_two",
            }
        ],
        "setup": None,
        "derived_from": "facet_cell_single_result_meal_kit_over_200_cheaper_008",
        "analogues": [ANALOGUE_MAKEUP, ANALOGUE_TABS],
        "notes": [
            "Category 85, 98 seeded listable == dbProductCount 98. Captured Price "
            "facet: 95 / 1 / 2 for $0.00-$99.99, $100.00-$199.99, $200.00 and above.",
            "?price=100-200 returns exactly id 80034 at $107.99.",
            "CORRECTIONS #61 flags fresh-meal-kits as holding sorted captures (name "
            "asc, and p=5 name). Those keys carry product_list_order, so the "
            "?price=100-200 URL misses them and renders the derived pool.",
            "Quantity 2 is asked for explicitly and the rubric requires qty == 2 "
            "exactly, so adding the line once scores 0.0 on both components. "
            "addToCart merges by product+options (AppContext.jsx:257-266), so "
            "pressing Add to Cart twice reaches the same end state as typing 2 in "
            "the PDP qty box — both are accepted.",
            "80034 has no productOptions entry.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_deli_hundred_plus_pair_006",
        "instruction": (
            "Putting together a charcuterie order. Filter Deli Meats & Cheeses to the "
            "$100.00 and above price band and add every product it lists to my cart."
        ),
        "style": "terse",
        "shape": "mutation",
        "start_path": "/",
        "category": "Deli Meats & Cheeses",
        "category_path": "/grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses.html",
        "facet_label": "$100.00 and above",
        "facet_param": "100-200",
        "nav": ["Grocery & Gourmet Food", "Deli & Prepared Foods", "Deli Meats & Cheeses"],
        "targets": [
            {
                "id": 47884,
                "sku": "B074DKNVPL",
                "name": (
                    "Serrano Ham Bone in from Spain 14.7 - 17 lb + Ham Stand + Knife - "
                    "Cured Spanish Jamon Made with Mediterranean Sea Salt & NO "
                    "Nitrates or Nitrites All Natural - GMO Free and Gluten Free"
                ),
                "price": 199.99,
                "qty_rule": "at_least_one",
            },
            {
                "id": 90775,
                "sku": "B07DFBCKHK",
                "name": (
                    "Rays Country Ham - 16 lb. - Whole Bone-in Country Ham - Blue Ridge "
                    "Mountain Cured"
                ),
                "price": 110.25,
                "qty_rule": "at_least_one",
            },
        ],
        "setup": None,
        "derived_from": "facet_cell_single_result_deli_over_100_dearer_007",
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_TABS],
        "notes": [
            "Category 273, 36 seeded listable == dbProductCount 36. Captured Price "
            "facet: 34 / 2 for $0.00-$99.99 and $100.00 and above (href price=100-200).",
            "The cell holds exactly two products, 47884 ($199.99) and 90775 ($110.25), "
            "and the rubric requires BOTH. Batch 5 used the same cell with an extra R1 "
            "step ('the dearer of the pair'); this is the two-skill bulk form, so the "
            "written state differs — two new lines rather than one.",
            "Neither product has a productOptions entry, so both tile buttons add "
            "directly.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_nintendo_hundred_plus_pair_007",
        "instruction": (
            "In the Nintendo Systems category, open the $100.00 and above price band "
            "and put everything it lists into my shopping cart."
        ),
        "style": "terse",
        "shape": "mutation",
        "start_path": "/",
        "category": "Nintendo Systems",
        "category_path": "/video-games/legacy-systems/nintendo-systems.html",
        "facet_label": "$100.00 and above",
        "facet_param": "100-200",
        "nav": ["Video Games", "Legacy Systems", "Nintendo Systems"],
        "targets": [
            {
                "id": 74818,
                "sku": "B085B9Q33S",
                "name": "Nintendo 2DS - Scarlet Red / White (Renewed)",
                "price": 189.99,
                "qty_rule": "at_least_one",
            },
            {
                "id": 100325,
                "sku": "B01G6LXS0A",
                "name": "amiibo aori",
                "price": 156.85,
                "qty_rule": "at_least_one",
            },
        ],
        "setup": "empty_cart",
        "derived_from": "facet_cell_single_result_nintendo_over_100_cheaper_009",
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_MEAT],
        "notes": [
            "Category 233, 48 seeded listable == dbProductCount 48. Captured Price "
            "facet: 46 / 2, second bucket labelled '$100.00 and above', href "
            "price=100-200.",
            "Both rows of the cell are required: 74818 ($189.99) and 100325 ($156.85). "
            "Batch 5 asked for the cheaper of the pair (a three-skill chain); this is "
            "the two-skill bulk form over the same cell, on an emptied cart, so both "
            "the derived value and the resulting collection differ.",
            "Neither product carries required options.",
            "initial_setup empties the cart, which pre-satisfies nothing: the rubric "
            "pays only for the two lines the agent adds.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_playstation_pair_two_hundred_008",
        "instruction": (
            "I am shopping for a retro console setup. Go to Video Games > Legacy Systems > "
            "PlayStation Systems and use the Shop By > Price block in the left sidebar to "
            "narrow the listing to the '$200.00 - $299.99' band. Two products survive that "
            "filter. Add both of them to my shopping cart, each at quantity 1, and leave "
            "the three items already sitting in the cart exactly as they are."
        ),
        "style": "explicit",
        "shape": "mutation",
        "start_path": "/",
        "category": "PlayStation Systems",
        "category_path": "/video-games/legacy-systems/playstation-systems.html",
        "facet_label": "$200.00 - $299.99",
        "facet_param": "200-300",
        "nav": ["Video Games", "Legacy Systems", "PlayStation Systems"],
        "targets": [
            {
                "id": 17882,
                "sku": "B07SLB9N56",
                "name": (
                    "Extreme Sim Racing Wheel Stand Cockpit SXT V2 Racing Simulator - "
                    "Racing Wheel Stand Black Edition For Logitech G25, G27, G29, "
                    "G920, Thrustmaster And Fanatec - Heavy Dutty and Foldable"
                ),
                "price": 249.0,
                "qty_rule": "at_least_one",
            },
            {
                "id": 19173,
                "sku": "B07D9VTVXM",
                "name": "Sony Playstation 3 160GB System (Renewed)",
                "price": 247.99,
                "qty_rule": "at_least_one",
            },
        ],
        "setup": None,
        "derived_from": None,
        "analogues": [ANALOGUE_MAKEUP, ANALOGUE_WOMEN],
        "notes": [
            "Category 226. Captured Price facet 169 / 3 / 2 / 1 / 1; the "
            "$200.00 - $299.99 cell holds exactly 17882 ($249.00) and 19173 ($247.99).",
            "The neighbouring cells are one product each ($300.00-$399.99 -> 77590, "
            "$400.00 and above -> 37971) and three products ($100.00-$199.99), so a "
            "misread band produces a disjoint product set and scores 0.0.",
            "Neither target carries required options.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_meal_kit_top_band_pair_009",
        "instruction": (
            "In Fresh Meal Kits, open the top price band in the Shop By sidebar and add "
            "everything listed under it to my cart."
        ),
        "style": "terse",
        "shape": "mutation",
        "start_path": "/grocery-gourmet-food.html",
        "category": "Fresh Meal Kits",
        "category_path": "/grocery-gourmet-food/fresh-meal-kits.html",
        "facet_label": "$200.00 and above",
        "facet_param": "200-300",
        "nav": ["Fresh Meal Kits"],
        "targets": [
            {
                "id": 80721,
                "sku": "B08Y2SH9F1",
                "name": (
                    "Lobsterorder.com's Shore Score for 6. 6 Live Maine Lobsters, 3lbs "
                    "Maine Steamers, 6 Servings New England Clam Chowder, 6 Maine "
                    "Whoopie Pies"
                ),
                "price": 269.99,
                "qty_rule": "at_least_one",
            },
            {
                "id": 91545,
                "sku": "B08Y2VQ3WK",
                "name": (
                    "Lobsterorder.com's Maine Downeast Feast. 6 Live Maine Lobsters "
                    "(1.25 - 1.35lbs ea), 3lbs Fresh Scallops, 64 ounces New England "
                    "Clam Chowder, 6 Maine Made Whoopie Pies"
                ),
                "price": 289.99,
                "qty_rule": "at_least_one",
            },
        ],
        "setup": "distractor_meal_kit",
        "derived_from": "facet_cell_single_result_meal_kit_over_200_cheaper_008",
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_TABS],
        "notes": [
            "Category 85. Captured Price facet: 95 / 1 / 2. The last bucket is "
            "'$200.00 and above' (href price=200-300) and holds 80721 ($269.99) and "
            "91545 ($289.99); both are required.",
            "initial_setup plants product 80034 ($107.99) — the sole occupant of the "
            "band directly below — as a fourth cart line. An agent that opens the "
            "$100.00 - $199.99 bucket instead finds the item it would add already in "
            "the cart, and the two required lines are still missing, so the run scores "
            "0.0. The distractor satisfies every part of the predicate except the band.",
            "The injected line uses addToCart's field set (no rowTotal) and takes "
            "itemId from the document's own nextCartItemId, which is then incremented, "
            "so a subsequent add cannot mint a duplicate itemId.",
            "start_path is the Grocery & Gourmet Food department page; Fresh Meal Kits "
            "is a direct child rendered both in the NavBand and in that page's Category "
            "facet.",
        ],
    },
    {
        "id": "price_band_cell_to_cart_kids_bedding_lone_bucket_010",
        "instruction": (
            "One price bucket in Kids' Bedding's Shop By sidebar shows just a single "
            "item next to it. Open that bucket and add the item to my shopping cart."
        ),
        "style": "terse",
        "shape": "retrieval_writeback",
        "start_path": "/",
        "category": "Kids' Bedding",
        "category_path": "/home-kitchen/bedding/kids-bedding.html",
        "facet_label": "$80.00 and above",
        "facet_param": "80-90",
        "nav": ["Home & Kitchen", "Bedding", "Kids' Bedding"],
        "targets": [
            {
                "id": 67733,
                "sku": "B09NRSHPN6",
                "name": (
                    "Disney Parks Homestead Collection Hidden Mickey Reversible Woven "
                    "Throw Blanket 60\" X 72\""
                ),
                "price": 88.99,
                "qty_rule": "at_least_one",
            }
        ],
        "setup": None,
        "derived_from": "facet_cell_single_result_kids_bedding_top_band_001",
        "analogues": [ANALOGUE_DENTAL, ANALOGUE_MEN],
        "notes": [
            "Category 155, 100 seeded listable == dbProductCount 100. The captured "
            "Price facet reproduces the source exactly: 3 / 21 / 31 / 14 / 15 / 6 / 7 "
            "/ 2 / 1. Exactly one bucket shows the count 1 — '$80.00 and above', whose "
            "href is ?price=80-90 (a source quirk kept verbatim) — so the retrieval "
            "has one reading. The runner-up bucket shows 2.",
            "Batch 5 named the band in the instruction ('$80-plus') and scored an "
            "emptied cart; here the band itself is what must be derived from the "
            "sidebar counts and the seeded three-line cart stays in play, so both the "
            "retrieval and the asserted collection differ.",
            "CORRECTIONS #61 lists kids-bedding as holding sorted captures (price "
            "desc, name desc). Those keys carry product_list_order/dir; ?price=80-90 "
            "matches none of them, so the filtered grid is derived and 67733 is the "
            "only tile.",
            "67733 has no productOptions entry.",
        ],
    },
]


# --------------------------------------------------------------------------
# rubric text
# --------------------------------------------------------------------------

def qty_phrase(rule):
    return "quantity exactly 2" if rule == "exactly_two" else "quantity 1 or more"


def expected_other_lines(task):
    """(product_id, sku, label) for every non-target line the cart must hold."""
    if task["setup"] == "empty_cart":
        return []
    rows = [(pid, sku, "seeded") for pid, sku in SEEDED]
    if task["setup"] == "distractor_meal_kit":
        rows.append((80034, "B07GXF3PBP", "injected"))
    return rows


def success_criteria(task):
    others = expected_other_lines(task)
    target_bits = ", ".join(
        'productId %d (sku %s, "%s", $%s) at %s'
        % (t["id"], t["sku"], t["name"], t["price"], qty_phrase(t["qty_rule"]))
        for t in task["targets"]
    )
    if others:
        other_bits = ", ".join("%d" % pid for pid, _sku, _lab in others)
        collection = (
            "state.cart.items holds exactly %d lines: the pre-existing line(s) for "
            "product(s) %s, each still present exactly once, plus one new line per "
            "target product and nothing else."
            % (len(others) + len(task["targets"]), other_bits)
        )
    else:
        collection = (
            "state.cart.items holds exactly %d line(s) — one per target product — "
            "and no other product id appears in the cart."
            % len(task["targets"])
        )
    return [
        "The cart carries one line for each product returned by the "
        "%s price band of the %s category: %s."
        % (task["facet_label"], task["category"], target_bits),
        collection,
    ]


# --------------------------------------------------------------------------
# reward source
# --------------------------------------------------------------------------

REWARD_HELPERS = '''
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
    number = _num(value)
    if number is None:
        return None
    return int(number) if float(number).is_integer() else None


def _text(value):
    return value.strip() if isinstance(value, str) else None


def _cart_lines(state):
    cart = state.get("cart") if isinstance(state, dict) else None
    items = cart.get("items") if isinstance(cart, dict) else None
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)]


def _product_ids(state):
    found = []
    for row in _cart_lines(state):
        pid = _int(row.get("productId"))
        if pid is not None:
            found.append(pid)
    return found


def _target_line_ok(state, spec):
    """Exactly one line for this product, carrying the catalog sku and qty."""
    matches = [
        row for row in _cart_lines(state)
        if _int(row.get("productId")) == spec["product_id"]
    ]
    if len(matches) != 1:
        return False
    row = matches[0]
    if _text(row.get("sku")) != spec["sku"]:
        return False
    qty = _int(row.get("qty"))
    if qty is None:
        return False
    if spec["qty_rule"] == "exactly_two":
        return qty == 2
    return qty >= 1


def _targets_added(state):
    for spec in TARGETS:
        if not _target_line_ok(state, spec):
            return False
    return True


def _cart_is_expected_collection(state):
    """The cart is exactly the expected multiset of product ids, one line each."""
    ids = _product_ids(state)
    if len(ids) != len(_cart_lines(state)):
        return False
    if len(ids) != len(EXPECTED_PRODUCT_IDS):
        return False
    for pid in EXPECTED_PRODUCT_IDS:
        if ids.count(pid) != 1:
            return False
    return True


def _checks(state):
    added = _targets_added(state)
    return {
        "band_products_in_cart": added,
        "cart_matches_expected_collection": added and _cart_is_expected_collection(state),
    }
'''


def targets_json(task):
    rows = [
        {
            "product_id": t["id"],
            "sku": t["sku"],
            "qty_rule": t["qty_rule"],
        }
        for t in task["targets"]
    ]
    return json.dumps(rows, indent=1)


def expected_ids(task):
    ids = [pid for pid, _sku, _lab in expected_other_lines(task)]
    ids += [t["id"] for t in task["targets"]]
    return ids


def reward_header(task):
    others = expected_other_lines(task)
    lines = [
        '"""Deterministic reward for %s.' % task["id"],
        "",
        "Success criteria (1.0 requires both components):",
    ]
    for t in task["targets"]:
        lines.append(
            "  * state.cart.items holds exactly one line for product %d (sku %s, $%s),"
            % (t["id"], t["sku"], t["price"])
        )
        lines.append(
            "    the %s cell of the %s category, at %s."
            % (task["facet_label"], task["category"], qty_phrase(t["qty_rule"]))
        )
    if others:
        lines.append(
            "  * the cart's other lines are exactly product(s) %s, one line each, and"
            % ", ".join(str(pid) for pid, _s, _l in others)
        )
        lines.append("    no further product id appears.")
    else:
        lines.append(
            "  * no other product id appears in the cart; the resulting collection is"
        )
        lines.append("    exactly the band's products.")
    lines += [
        "",
        "Reads current state only. Every product id, sku and price below was measured",
        "directly from the frozen catalog in",
        "hub/websites/webarena_shopping_mock/src/data/products.json, and the price cell",
        "was enumerated against the captured facet block in src/data/listings.json.",
        '"""',
        "",
    ]
    return "\n".join(lines)


def render_reward(task):
    parts = [reward_header(task)]
    parts.append("import json\n")
    parts.append('TARGETS = json.loads(r"""\n%s\n""")\n' % targets_json(task))
    parts.append(
        "EXPECTED_PRODUCT_IDS = %s\n" % json.dumps(expected_ids(task))
    )
    parts.append(
        "COMPONENT_WEIGHTS = {\n"
        '    "band_products_in_cart": 0.6,\n'
        '    "cart_matches_expected_collection": 0.4,\n'
        "}\n"
    )
    parts.append(REWARD_HELPERS)
    parts.append('''

def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state")
    if not isinstance(state, dict):
        state = {}
    checks = _checks(state)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {"satisfied": bool(checks.get(name))},
        }
        for name in COMPONENT_WEIGHTS
    ]
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
''')
    return "\n".join(parts)


def render_nemo_reward(task):
    header = (
        '"""NeMo-Gym reward program for %s.\n'
        "\n"
        "Implements the same rubric as reward.py, reading the live session state from\n"
        "GET /go?sid=... instead of a frozen evidence bundle, and printing\n"
        "REWARD: <float> on every output path.\n"
        "\n"
        "Self-contained: standard library plus requests (in cuagym/requirements.txt).\n"
        '"""\n' % task["id"]
    )
    parts = [header]
    parts.append("import json\nimport sys\n\nimport requests\n")
    parts.append('SID = "__CUA_GYM_SID__"\nBASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n')
    parts.append('TARGETS = json.loads(r"""\n%s\n""")\n' % targets_json(task))
    parts.append("EXPECTED_PRODUCT_IDS = %s\n" % json.dumps(expected_ids(task)))
    parts.append(
        "COMPONENT_WEIGHTS = {\n"
        '    "band_products_in_cart": 0.6,\n'
        '    "cart_matches_expected_collection": 0.4,\n'
        "}\n"
    )
    parts.append(REWARD_HELPERS)
    parts.append('''

def score_state(current):
    """Returns (score, components). Exactly 0.0 on the untouched cart."""
    if not isinstance(current, dict):
        current = {}
    checks = _checks(current)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {"satisfied": bool(checks.get(name))},
        }
        for name in COMPONENT_WEIGHTS
    ]
    return round(sum(c["score"] for c in components), 6), components


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current_state") or {}
        if not isinstance(current, dict):
            current = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    score, _components = score_state(current)
    print("REWARD: %s" % score)


main()
''')
    return "\n".join(parts)


# --------------------------------------------------------------------------
# setup source
# --------------------------------------------------------------------------

SETUP_TAIL = '''

def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    document = payload.get("current_state")
    if not isinstance(document, dict):
        document = payload.get("initial_state")
    if not isinstance(document, dict):
        print("SETUP FAILED: /go returned no readable state document", file=sys.stderr)
        raise SystemExit(1)
    cart = document.get("cart")
    if not isinstance(cart, dict) or not isinstance(cart.get("items"), list):
        print("SETUP FAILED: cart.items is not readable", file=sys.stderr)
        raise SystemExit(1)

    document = mutate(document)

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": document},
        timeout=60,
    )
    posted.raise_for_status()
    verify()


main()
'''

SETUP_EMPTY = '''
def mutate(document):
    """Empty the shopping cart, leaving every other session key untouched.

    Read-modify-write over the whole document returned by /go: the shopping
    mock shallow-merges a partial `set` (vite.config.js:441-449), but posting
    the complete document is correct under either behaviour and is what the
    reward reads back.

    The stored aggregates are recomputed even though nothing renders them --
    CartPage.jsx:35 and Header.jsx:209 both sum the lines -- so that no screen
    can show a total contradicting an empty basket.
    """
    cart = dict(document.get("cart") or {})
    cart["items"] = []
    cart["itemsCount"] = 0
    cart["itemsQty"] = 0
    cart["subtotal"] = 0
    cart["grandTotal"] = 0
    document["cart"] = cart
    return document
'''

SETUP_DISTRACTOR = '''
# The distractor line, written in addToCart's own field set
# (AppContext.jsx:262-270): itemId / productId / sku / name / price / qty /
# options, and no rowTotal, which that handler never writes.
DISTRACTOR = json.loads(r"""
{
 "productId": 80034,
 "sku": "B07GXF3PBP",
 "name": "Elements Meals | Broccoli Cinnamon Pork | 10-Pack | Healthy Freeze Dried Meals | Whole30 Approved | Delicious, Backpacking and Camping Food | High Protein",
 "price": 107.99,
 "qty": 1,
 "options": []
}
""")


def mutate(document):
    """Append the $107.99 meal kit -- the sole occupant of the price band one
    step below the target band -- to the seeded three-line cart.

    It satisfies every part of the errand except the band, so an agent that
    opens the wrong bucket finds its candidate already carted and still adds
    neither required line. Nothing here is paid for by the rubric: the two
    products the band returns are absent.

    Read-modify-write over the whole /go document. itemId is taken from the
    session's own allocator and the allocator is bumped, so a later add cannot
    mint a duplicate itemId.
    """
    cart = dict(document.get("cart") or {})
    items = [row for row in list(cart.get("items") or [])
             if not (isinstance(row, dict) and row.get("productId") == DISTRACTOR["productId"])]
    next_id = document.get("nextCartItemId")
    if not isinstance(next_id, int):
        next_id = 557
    row = dict(DISTRACTOR)
    row["itemId"] = next_id
    items.append(row)
    document["nextCartItemId"] = next_id + 1

    quantity = 0
    total = 0.0
    for entry in items:
        if not isinstance(entry, dict):
            continue
        qty = entry.get("qty") or 0
        price = entry.get("price") or 0
        quantity += qty
        total += float(price) * float(qty)
    cart["items"] = items
    cart["itemsCount"] = len(items)
    cart["itemsQty"] = quantity
    cart["subtotal"] = round(total, 2)
    cart["grandTotal"] = round(total, 2)
    document["cart"] = cart
    return document
'''


def render_setup(task):
    kind = task["setup"]
    if kind is None:
        return None
    if kind == "empty_cart":
        body = SETUP_EMPTY
        blurb = (
            "Empties the shopping cart so the resulting collection asserted by the "
            "reward is exactly the products the price band returns. Nothing the rubric "
            "pays for is written."
        )
        imports = "import sys\n\nimport requests\n"
    else:
        body = SETUP_DISTRACTOR
        blurb = (
            "Plants product 80034 ($107.99), the only occupant of the price band one "
            "step below the target band, as an extra cart line. It matches every part "
            "of the errand except the band, turning 'click the last bucket' into "
            "'read the bucket labels'. The two products the target band returns are "
            "not written."
        )
        imports = "import json\nimport sys\n\nimport requests\n"
    header = (
        '"""NeMo-Gym setup program for %s.\n'
        "\n"
        "%s\n"
        "\n"
        "Written as a read-modify-write over GET /go?sid=... : the whole session\n"
        "document is read back, mutated in place and POSTed to /post?sid=... with\n"
        '{"action": "set"}, which is correct whether the mock merges or replaces.\n'
        "\n"
        "Self-contained: standard library plus requests (in cuagym/requirements.txt).\n"
        '"""\n' % (task["id"], blurb)
    )
    return "".join([
        header,
        "\n",
        imports,
        "\n",
        'SID = "__CUA_GYM_SID__"\n',
        'BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n',
        body,
        SETUP_TAIL,
    ])


# --------------------------------------------------------------------------
# manifests
# --------------------------------------------------------------------------

def injected_preconditions(task):
    if task["setup"] == "empty_cart":
        return [
            "cart.items: [] (itemsCount/itemsQty/subtotal/grandTotal zeroed to match) "
            "- the mock boots with three seeded lines (554-556); emptying the basket "
            "lets the rubric assert the exact resulting collection instead of a count, "
            "and pre-satisfies no component."
        ]
    if task["setup"] == "distractor_meal_kit":
        return [
            "cart.items: the three seeded lines (554-556) plus a fourth line for "
            "product 80034 (sku B07GXF3PBP, $107.99, qty 1, itemId taken from "
            "nextCartItemId, which is bumped) - the sole occupant of the price band "
            "directly below the target band. It is the distractor that makes the agent "
            "read the bucket labels rather than guess; neither product the target band "
            "returns is written."
        ]
    return None


def render_task_json(task):
    meta = {
        "style": task["style"],
        "difficulty": "medium",
        "shape": task["shape"],
        "skills": ["R5", "A4"],
        "skill_chain": (
            "open the %s category and click the %s price cell in the Shop By sidebar "
            "-> add the product(s) that cell returns to the shopping cart"
            % (task["category"], task["facet_label"])
        ),
        "derived_from": task["derived_from"],
        "official_analogues": task["analogues"],
        "topic": "price_band_cell_to_cart",
        "batch": "batch-6 lane 30 (shopping / R5 -> A4)",
        "lane_skill_chain": "R5 -> A4",
        "inspiration_ids": ["webarena-282", "webarena-283", "webarena-431"],
        "authoring_notes": task["notes"],
    }
    injected = injected_preconditions(task)
    if injected:
        meta["injected_preconditions"] = injected
    return {
        "schema_version": 2,
        "task_id": task["id"],
        "instruction": task["instruction"],
        "apps": [
            {
                "name": APP,
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
                "start_path": task["start_path"],
                "initial_state": None,
                "golden_state": None,
            }
        ],
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": meta,
    }


def render_nemo_task(task, setup_code, reward_code):
    return {
        "task_payload": {
            "task_id": task["id"],
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
                "bundle_id": task["id"],
                "app_dir": APP,
                "initial_setup": setup_code,
                "eval_reward_code": reward_code,
            },
        }
    }


# --------------------------------------------------------------------------
# replay draft
# --------------------------------------------------------------------------

def render_replay(task):
    nav = "\n".join(
        '    link = page.get_by_role("link", name=%r, exact=True).first\n'
        "    await link.hover()\n"
        "    await link.click()\n"
        '    await page.wait_for_load_state("networkidle")\n' % name
        for name in task["nav"]
    )
    adds = []
    for t in task["targets"]:
        needle = t["name"][:32]
        qty = 2 if t["qty_rule"] == "exactly_two" else 1
        adds.append(
            "    # Add product %d (%s, $%s) from its tile. It carries no required\n"
            "    # options, so ProductGrid.jsx:63-66 does not divert to the PDP.\n"
            "    tile = page.locator(\".product-item\").filter(\n"
            "        has=page.get_by_text(%r)\n"
            "    ).first\n"
            '    await tile.get_by_role("button", name="Add to Cart").click()\n'
            '    await page.get_by_text("You added").first.wait_for(state="visible", timeout=15000)\n'
            % (t["id"], t["sku"], t["price"], needle)
        )
        if qty == 2:
            adds.append(
                "    # Quantity 2 is required. The tile button does not navigate for a\n"
                "    # product with no required options, so the filtered grid is still\n"
                "    # on screen; addToCart merges by product+options\n"
                "    # (AppContext.jsx:257-266), so a second press lands qty == 2 on the\n"
                "    # same line rather than appending a second one.\n"
                '    await tile.get_by_role("button", name="Add to Cart").click()\n'
                "    await page.wait_for_timeout(500)\n"
            )
    return (
        "# Golden replay DRAFT for %s.\n"
        "#\n"
        "# Clicks only rendered links and buttons, starting from %s.\n"
        "# Nav band: %s\n"
        "# Facet cell: %s (%s?price=%s)\n"
        "async def run(lane, task):\n"
        '    page = lane.page("shopping")\n'
        "\n"
        "%s"
        "\n"
        "    # Shop By > Price: click the facet cell. This is a rendered <a>\n"
        "    # (LayeredNav.jsx:112-118), not a typed URL.\n"
        '    await page.get_by_role("link", name=%r).first.click()\n'
        '    await page.wait_for_load_state("networkidle")\n'
        "\n"
        "%s"
        % (
            task["id"],
            task["start_path"],
            " -> ".join(task["nav"]),
            task["facet_label"],
            task["category_path"],
            task["facet_param"],
            nav,
            task["facet_label"],
            "\n".join(adds),
        )
    )


# --------------------------------------------------------------------------

def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []
    for task in TASKS:
        bundle = os.path.join(OUT, task["id"])
        os.makedirs(bundle, exist_ok=True)

        instruction = {
            "task_id": task["id"],
            "task_instruction": task["instruction"],
            "app_dir": APP,
            "start_path": task["start_path"],
            "difficulty": "medium",
            "success_criteria": success_criteria(task),
        }
        reward = render_reward(task)
        nemo_reward = render_nemo_reward(task)
        setup = render_setup(task)

        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump(instruction, fh, indent=2)
            fh.write("\n")
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(render_task_json(task), fh, indent=2)
            fh.write("\n")
        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward)
        setup_path = os.path.join(bundle, "initial_setup.py")
        if setup is None:
            if os.path.exists(setup_path):
                os.remove(setup_path)
        else:
            with open(setup_path, "w") as fh:
                fh.write(setup)
        row = render_nemo_task(task, setup, nemo_reward)
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        rows.append(row)

        with open(os.path.join(REPLAYS, task["id"] + ".py"), "w") as fh:
            fh.write(render_replay(task))

        index["tasks"].append({"task_id": task["id"], "path": task["id"] + "/task.json"})

        words = len(task["instruction"].split())
        print("%-58s %-8s %-20s start=%-28s words=%d setup=%s"
              % (task["id"], task["style"], task["shape"], task["start_path"], words,
                 task["setup"]))
        if task["style"] == "terse" and words > 40:
            raise SystemExit("TERSE OVER CAP: %s (%d words)" % (task["id"], words))

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
