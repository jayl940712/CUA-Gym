#!/usr/bin/env python3
"""Batch-6 lane 40 generator: shopping R4 -> A4, Nth-cheapest -> wish list.

Writes ten bundles under output/tasks/shopping/<task_id>/ plus the lane's
GENERATION.md, index.json, nemo_tasks.jsonl and replay drafts under
output/tasks/shopping/_batches/nth_cheapest_wishlist/.

Every ground-truth value here was computed offline from
hub/websites/webarena_shopping_mock/src/data/products.json using
isListable() (catalog.js:412) and finalPrice() (catalog.js:416) and the
price tie-break of sortProducts() (catalog.js:1104, id ASC in both
directions).  Margins at both the N-1/N and N/N+1 boundaries are recorded
in each task's metadata and in GENERATION.md.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/nth_cheapest_wishlist")
LANE = "nth_cheapest_wishlist"

APP_DIR = "webarena_shopping_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

# ---------------------------------------------------------------- catalogue --
P = {
    43907: ("B075RHS84G", 15.5, "Fiorucci, Salami Sliced Hard, 4 Ounce",
            "fiorucci-salami-sliced-hard-4-ounce"),
    89644: ("B09KN69C4Q", 9.99,
            "Anbee 2-Pack Protective Case Silicone Cover Non-Slip Stain Resistant Soft Sleeve Compatible with Oculus Quest 2 VR Headset Touch Controller",
            "anbee-2-pack-protective-case-silicone-cover-non-slip-stain-resistant-soft-sleeve-compatible-with-oculus-quest-2-vr-headset-touch-controller"),
    72802: ("B09HH162SB", 42.97,
            "COODENKEY 7 Piece Patio Furniture Sets Outdoor Garden Sectional Sofa,All-Weather PE Rattan Wicker Couch with Loveseat & Storage Box & Coffee Table & Removable Cushions, Beige",
            "coodenkey-7-piece-patio-furniture-sets-outdoor-garden-sectional-sofa-all-weather-pe-rattan-wicker-couch-with-loveseat-storage-box-coffee-table-removable-cushions-beige"),
    103557: ("B01MUA6T88", 13.95,
             "GramZero Chocolate Sugar Free Cake Mix 2-pack, Makes 2 - 13x9x2 Cakes, Stevia Sweetened",
             "gramzero-chocolate-sugar-free-cake-mix-2-pack-makes-2-13x9x2-cakes-stevia-sweetened"),
    71137: ("B08X65XQ7S", 13.99,
            "Oradrem Cotton Rope Plant Basket Modern Woven Basket for 6\" Flower Pot Floor Indoor Planters,Rustic Home Decor Storage Organizer H6 3/4\" x W6 1/2\"",
            "oradrem-cotton-rope-plant-basket-modern-woven-basket-for-6-flower-pot-floor-indoor-planters-rustic-home-decor-storage-organizer-h6-3-4-x-w6-1-2"),
    37738: ("B09NL389C7", 25.99,
            "Digital Camera Kids,Full Color 2.0\" LCD Display,Macaron Color,2 Inch,Built-in Carrying Strap,Small&Portable,19201080 Video Resolution,Christmas Birthday Gift for Girls Boys-#8",
            "digital-camera-kids-full-color-2-0-lcd-display-macaron-color-2-inch-built-in-carrying-strap-small-portable-19201080-video-resolution-christmas-birthday-gift-for-girls-boys-8"),
    87086: ("B09M43M8VG", 8.99,
            "Funny Kitchen Towels Fold in The Cheese Dish Towels Super Absorbent Flour Sack Towels with Sayings Perfect Housewarming Gift New Homeowner Present for Women Hostess New Home Set of 2 Hand Tea Towels",
            "funny-kitchen-towels-fold-in-the-cheese-dish-towels-super-absorbent-flour-sack-towels-with-sayings-perfect-housewarming-gift-new-homeowner-present-for-women-hostess-new-home-set-of-2-hand-tea-towels"),
    70199: ("B097YHDSVG", 56.99,
            "JERFYUT Cartoon Bedding Sets Twin Duvet Cover 3 Piece Cute Bed Set for Boys Girls Kid with 1 Duvet Cover + 2 Pillowcase,Bed Sheets",
            "jerfyut-cartoon-bedding-sets-twin-duvet-cover-3-piece-cute-bed-set-for-boys-girls-kid-with-1-duvet-cover-2-pillowcase-bed-sheets"),
    97687: ("B09KYCQPV4", 32.95,
            "INTIMO Peanuts Snoopy Joe Cool Tie Dye Lazy Mode Silk Touch Throw Blanket",
            "intimo-peanuts-snoopy-joe-cool-tie-dye-lazy-mode-silk-touch-throw-blanket"),
    77912: ("B09FL9XK65", 11.99,
            "Foluu for Google Pixel 6 Case, Pixel 6 2021 Wallet Case Canvas Flip/Folio Soft TPU Cover Bumper Kickstand Ultra Slim Strong Magnetic Closure Cover for Google Pixel 6 Case 2021 (Gray)",
            "foluu-for-google-pixel-6-case-pixel-6-2021-wallet-case-canvas-flip-folio-soft-tpu-cover-bumper-kickstand-ultra-slim-strong-magnetic-closure-cover-for-google-pixel-6-case-2021-gray"),
    # injection pool (never a target)
    97597: ("B002OTLNVA", 3.29,
            "A+D First Aid Ointment - Moisturizing Skin Protectant for Dry Cracked Hands, Elbows, heals and lips - Use After Hand Washing, Packaging May Vary, Multicolor – 1.5 oz Tube",
            "a-d-first-aid-ointment"),
    60605: ("B086V1BM9Q", 0.01,
            "VEKDONE Men's Gym Bodybuilding Stringer Tank Top Workout Sleeveless Muscle Cut Off Shirt Fitness Vests",
            "vekdone-men-s-gym-bodybuilding-stringer-tank-top"),
    19698: ("B084D1MRWQ", 0.99,
            "hudiemm0B Car Cassette Audio Converter, 3.5mm Jack Car AUX Cassette Tape Adapter Audio MP3 CD Phone Radio Converter",
            "hudiemm0b-car-cassette-audio-converter"),
    12969: ("B09PNPC2Q9", 1.76,
            "AODONG Gladiator Sandals for Women Lace up Tie up Dress Summer Flat Comfortable Open Toe Roman Strap Casual Beach Sandals",
            "aodong-gladiator-sandals-for-women"),
    97842: ("B004UC3F0G", 6.49, "Outsidepride Verbena Blue Vervain - 5000 Seeds",
            "outsidepride-verbena-blue-vervain-5000-seeds"),
}

STAMPS = ["2023-04-09 10:22:41", "2023-04-27 18:05:13", "2023-05-02 08:41:56",
          "2023-03-22 15:12:07", "2023-05-11 12:36:29"]

AN_CHAIR = "Add a chair to my wish list."
AN_ASC = "Pull up the page with all \"chairs\" listings sorted by ascending price."
AN_PS4 = "Go to the page showing PS4 accessories products sorted by ascending price"
AN_TIDE = ("Add Tide PODS Spring Meadow Scent HE Turbo Laundry Detergent Pacs, "
           "81 Count to my wish list")
AN_LEAST = ("View the product page for the least expensive shoe storage with a "
            "minimum storage capacity of 12 pairs.")
AN_ORCHID = ("Add 2 Hawaiian Bamboo Orchid Roots #zc50 - by Discount Hawaiian "
             "Gifts to my wish list")

# ------------------------------------------------------------------- tasks ---
# ordinal / price / gap_prev / gap_next were computed from the seed; see
# GENERATION.md for the full boundary table.
TASKS = [
    dict(
        num="001", slug="deli_counter_third_bargain", target=43907,
        category="Deli Meats & Cheeses", cat_id=273,
        nav=["Grocery & Gourmet Food", "Deli & Prepared Foods", "Deli Meats & Cheeses"],
        path="/grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses.html",
        pool_n=36, cat_n=36, ordinal=3, ordinal_word="third", price_filter=None,
        prev_id=82251, prev_price=11.67, next_id=79091, next_price=19.7,
        style="terse",
        instruction=("Sort the Deli Meats & Cheeses aisle by price and put the "
                     "third cheapest product in there on my wish list."),
        inject=[97842, 19698],
        analogues=[AN_TIDE, AN_ASC],
        derived_from="category_cheapest_to_cart_deli_counter_bargain_001",
    ),
    dict(
        num="002", slug="vr_fourth_cheapest_accessory", target=89644,
        category="Virtual Reality", cat_id=247,
        nav=["Video Games", "PC", "Virtual Reality"],
        path="/video-games/pc/virtual-reality.html",
        pool_n=55, cat_n=55, ordinal=4, ordinal_word="fourth", price_filter=None,
        prev_id=77880, prev_price=7.99, next_id=88634, next_price=12.74,
        style="terse",
        instruction=("In the Virtual Reality category, order the listing by "
                     "price and add the fourth cheapest item to my wish list."),
        inject=None,
        analogues=[AN_PS4, AN_CHAIR],
        derived_from="kids_bedding_price_superlative_vr_flagship_beside_saved_006",
    ),
    dict(
        num="003", slug="patio_third_cheapest_set", target=72802,
        category="Patio Furniture & Accessories", cat_id=50,
        nav=["Patio, Lawn & Garden", "Patio Furniture & Accessories"],
        path="/patio-lawn-garden/patio-furniture-accessories.html",
        pool_n=92, cat_n=92, ordinal=3, ordinal_word="third", price_filter=None,
        prev_id=99091, prev_price=23.93, next_id=69428, next_price=46.49,
        style="terse",
        instruction=("Browsing Patio Furniture & Accessories from cheapest "
                     "upwards, save the third listing to my wish list."),
        inject=[97597, 12969],
        analogues=[AN_CHAIR, AN_ASC],
        derived_from="kids_bedding_price_superlative_cheapest_patio_pick_002",
    ),
    dict(
        num="004", slug="cakes_fourth_cheapest_mix", target=103557,
        category="Cakes", cat_id=292,
        nav=["Grocery & Gourmet Food", "Breads & Bakery", "Cakes"],
        path="/grocery-gourmet-food/breads-bakery/cakes.html",
        pool_n=69, cat_n=69, ordinal=4, ordinal_word="fourth", price_filter=None,
        prev_id=78284, prev_price=11.09, next_id=49607, next_price=14.99,
        style="terse",
        instruction=("Line the Cakes category up by price, lowest first, and "
                     "wish-list the fourth one."),
        inject=None,
        analogues=[AN_ORCHID, AN_ASC],
        derived_from="kids_bedding_price_superlative_cake_price_extremes_004",
    ),
    dict(
        num="005", slug="planters_third_cheapest_basket", target=71137,
        category="Pots, Planters & Container Accessories", cat_id=191,
        nav=["Patio, Lawn & Garden", "Gardening & Lawn Care",
             "Pots, Planters & Container Accessories"],
        path="/patio-lawn-garden/gardening-lawn-care/pots-planters-container-accessories.html",
        pool_n=80, cat_n=80, ordinal=3, ordinal_word="third", price_filter=None,
        prev_id=88310, prev_price=10.99, next_id=67589, next_price=14.97,
        style="terse",
        instruction=("Sort Pots, Planters & Container Accessories by ascending "
                     "price and add the third cheapest product to my wish list."),
        inject=[19698, 12969],
        analogues=[AN_ORCHID, AN_PS4],
        derived_from="price_range_into_wishlist_note_pots_planters_cheapest_008",
    ),
    dict(
        num="006", slug="smartwatch_third_cheapest", target=37738,
        category="Smartwatches", cat_id=256,
        nav=["Electronics", "Wearable Technology", "Smartwatches"],
        path="/electronics/wearable-technology/smartwatches.html",
        pool_n=56, cat_n=56, ordinal=3, ordinal_word="third", price_filter=None,
        prev_id=75958, prev_price=23.99, next_id=99926, next_price=26.99,
        style="terse",
        instruction=("Put the third cheapest product in the Smartwatches "
                     "category on my wish list."),
        inject=None,
        analogues=[AN_TIDE, AN_LEAST],
        derived_from="category_cheapest_to_cart_budget_smartwatch_010",
    ),
    dict(
        num="007", slug="table_linens_fourth_cheapest", target=87086,
        category="Kitchen & Table Linens", cat_id=189,
        nav=["Home & Kitchen", "Kitchen & Dining", "Kitchen & Table Linens"],
        path="/home-kitchen/kitchen-dining/kitchen-table-linens.html",
        pool_n=112, cat_n=112, ordinal=4, ordinal_word="fourth", price_filter=None,
        prev_id=35384, prev_price=6.06, next_id=16646, next_price=9.95,
        style="terse",
        instruction=("Rank Kitchen & Table Linens from the lowest price up and "
                     "add the fourth item to my wish list."),
        inject=None,
        analogues=[AN_TIDE, AN_ASC],
        derived_from="category_cheapest_to_cart_table_linens_bargain_002",
    ),
    dict(
        num="008", slug="kids_bedding_band_50_fourth", target=70199,
        category="Kids' Bedding", cat_id=155,
        nav=["Home & Kitchen", "Bedding", "Kids' Bedding"],
        path="/home-kitchen/bedding/kids-bedding.html",
        pool_n=6, cat_n=100, ordinal=4, ordinal_word="fourth",
        price_filter=("50-60", "$50.00 - $59.99"),
        prev_id=71054, prev_price=54.99, next_id=99068, next_price=59.5,
        style="explicit",
        instruction=("Go to Home & Kitchen > Bedding > Kids' Bedding. In the "
                     "Shop By panel click the Price filter for $50.00 - $59.99, "
                     "sort those results by price in ascending order, and add "
                     "the fourth-cheapest of them to my wish list."),
        inject=[97597, 97842],
        analogues=[AN_ORCHID, AN_ASC],
        derived_from="facet_cell_single_result_kids_bedding_top_band_001",
    ),
    dict(
        num="009", slug="kids_bedding_band_30_fourth", target=97687,
        category="Kids' Bedding", cat_id=155,
        nav=["Home & Kitchen", "Bedding", "Kids' Bedding"],
        path="/home-kitchen/bedding/kids-bedding.html",
        pool_n=14, cat_n=100, ordinal=4, ordinal_word="fourth",
        price_filter=("30-40", "$30.00 - $39.99"),
        prev_id=73450, prev_price=31.76, next_id=31869, next_price=33.99,
        style="explicit",
        instruction=("Open Kids' Bedding under Home & Kitchen > Bedding, narrow "
                     "it with the Shop By > Price option $30.00 - $39.99, put "
                     "that shortlist in ascending price order, and save the "
                     "fourth-cheapest throw to my wish list."),
        inject=None,
        analogues=[AN_TIDE, AN_ASC],
        derived_from="kids_bedding_price_superlative_priciest_kids_throw_001",
    ),
    dict(
        num="010", slug="flip_cases_band_10_second", target=77912,
        category="Flip Cases", cat_id=232,
        nav=["Cell Phones & Accessories", "Cases, Holsters & Sleeves", "Flip Cases"],
        path="/cell-phones-accessories/cases-holsters-sleeves/flip-cases.html",
        pool_n=28, cat_n=47, ordinal=2, ordinal_word="second",
        price_filter=("10-20", "$10.00 - $19.99"),
        prev_id=77098, prev_price=10.99, next_id=76321, next_price=12.98,
        style="explicit",
        instruction=("Navigate to Cell Phones & Accessories > Cases, Holsters & "
                     "Sleeves > Flip Cases, apply the Shop By Price filter "
                     "$10.00 - $19.99, sort by price ascending, and add the "
                     "second-cheapest case in that band to my wish list."),
        inject=[60605, 97842],
        analogues=[AN_PS4, AN_LEAST],
        derived_from="facet_cell_single_result_fireplace_price_band_010",
    ),
]


# ------------------------------------------------------------------ helpers --
def wishlist_rows(ids):
    rows = []
    for n, pid in enumerate(ids):
        sku, price, name, _ = P[pid]
        rows.append({
            "wishlistItemId": n + 1,
            "productId": pid,
            "sku": sku,
            "name": name,
            "price": price,
            "qty": 1,
            "description": "",
            "addedAt": STAMPS[n % len(STAMPS)],
        })
    return rows


def scope_phrase(t):
    if t["price_filter"]:
        return "%s priced %s" % (t["category"], t["price_filter"][1])
    return t["category"]


def rubric_doc(t, tid):
    sku, price, name, _ = P[t["target"]]
    expected = list(t["inject"] or []) + [t["target"]]
    return (
        "  * wishlist.items holds exactly the products %s - the %s-cheapest\n"
        "    product of %s is id %d (%s, $%s)\n"
        "  * that row carries the catalog sku, name and price written by\n"
        "    addToWishlist (AppContext.jsx:324-346)\n"
        % (expected, t["ordinal_word"], scope_phrase(t), t["target"], sku, price)
    )


REWARD_BODY = '''
EXPECTED = json.loads(r"""
__FIXTURE__
""")

COMPONENT_WEIGHTS = {
    "wishlist_membership_is_exactly_expected": 0.5,
    "target_row_carries_catalog_fields": 0.5,
}


def _items(state):
    wishlist = state.get("wishlist")
    if not isinstance(wishlist, dict):
        return []
    items = wishlist.get("items")
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)]


def _pid(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and float(value).is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return None


def _price(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace("$", "").replace(",", "")
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _checks(state):
    items = _items(state)
    ids = sorted([p for p in [_pid(i.get("productId")) for i in items] if p is not None])
    membership = ids == sorted(EXPECTED["expected_product_ids"]) and len(ids) == len(items)
    target = None
    for item in items:
        if _pid(item.get("productId")) == EXPECTED["target"]["productId"]:
            target = item
    name = target.get("name") if target is not None else None
    sku = target.get("sku") if target is not None else None
    stored_price = _price(target.get("price")) if target is not None else None
    fields = (
        membership
        and target is not None
        and isinstance(sku, str) and sku.strip() == EXPECTED["target"]["sku"]
        and isinstance(name, str) and name.strip() == EXPECTED["target"]["name"]
        and stored_price is not None
        and abs(stored_price - EXPECTED["target"]["price"]) < 0.005
    )
    return {
        "wishlist_membership_is_exactly_expected": bool(membership),
        "target_row_carries_catalog_fields": bool(fields),
    }
'''


def reward_py(t, tid):
    sku, price, name, _ = P[t["target"]]
    fixture = json.dumps({
        "target": {"productId": t["target"], "sku": sku, "name": name, "price": price},
        "expected_product_ids": list(t["inject"] or []) + [t["target"]],
    }, indent=2, ensure_ascii=False)
    head = (
        '"""Deterministic reward for %s.\n\n'
        'Success criteria:\n%s\n'
        'Only user-visible persisted state is inspected, and only `current_state`.\n'
        'Ground truth is fixed by the frozen catalog of webarena_shopping_mock in\n'
        './hub/ (products.json + isListable/finalPrice, catalog.js:412/416) plus\n'
        "this bundle's own initial_setup.py where present.\n"
        '"""\n\nimport json\n' % (tid, rubric_doc(t, tid))
    )
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
    return head + REWARD_BODY.replace("__FIXTURE__", fixture) + tail


def nemo_reward_py(t, tid):
    sku, price, name, _ = P[t["target"]]
    fixture = json.dumps({
        "target": {"productId": t["target"], "sku": sku, "name": name, "price": price},
        "expected_product_ids": list(t["inject"] or []) + [t["target"]],
    }, indent=2, ensure_ascii=False)
    head = (
        '"""NeMo-Gym reward program for %s.\n\n'
        'Implements exactly the rubric of reward.py, reading `current_state`\n'
        'from GET /go?sid=... instead of a frozen evidence bundle, and printing\n'
        'REWARD: <float> on every output path including the error path.\n\n'
        'Self-contained: standard library plus requests, which is present in\n'
        'cuagym/requirements.txt.\n'
        '"""\n\nimport json\nimport sys\n\nimport requests\n\n'
        'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n' % (tid, URL_PLACEHOLDER)
    )
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
    return head + REWARD_BODY.replace("__FIXTURE__", fixture) + tail


SETUP_TMPL = '''"""NeMo-Gym setup program for %(tid)s.

Pre-seeds the customer's wish list with two already-saved products so the
errand is "add the one I picked to the list I already keep" rather than
"start a list". Neither injected row is the task's target and neither sits
in %(category)s, so the untouched session still scores exactly 0.0.

Written as a read-modify-write: GET /go, mutate the whole document, POST it
back. Correct on every mock regardless of whether a partial `set` merges or
replaces (output/CENSUS_ERRATA.md).

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url)s"

# Every field addToWishlist (AppContext.jsx:324-346) writes, in its own
# convention: wishlistItemId, productId, sku, name, price, qty, description,
# addedAt. nextWishlistItemId is advanced past the injected rows so a fresh
# add cannot collide with one.
WISHLIST_ITEMS = json.loads(r"""
%(items)s
""")
NEXT_WISHLIST_ITEM_ID = %(next_id)d


def load_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: /go returned neither current_state nor initial_state",
              file=sys.stderr)
        raise SystemExit(1)
    return state


def main():
    state = load_state()
    wishlist = state.get("wishlist")
    if not isinstance(wishlist, dict):
        wishlist = {}
    wishlist["items"] = WISHLIST_ITEMS
    state["wishlist"] = wishlist
    state["nextWishlistItemId"] = NEXT_WISHLIST_ITEM_ID

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    current = payload.get("current_state") or {}
    saved = (current.get("wishlist") or {}).get("items")
    if not isinstance(saved, list) or len(saved) != len(WISHLIST_ITEMS):
        print("SETUP FAILED: wish list was not persisted", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


main()
'''


def setup_py(t, tid):
    rows = wishlist_rows(t["inject"])
    return SETUP_TMPL % {
        "tid": tid,
        "url": URL_PLACEHOLDER,
        "category": t["category"],
        "items": json.dumps(rows, indent=2, ensure_ascii=False),
        "next_id": len(rows) + 1,
    }


REPLAY_TMPL = '''"""Golden replay DRAFT for %(tid)s.

Click-only: after the initial landing on `start_path` there is no page.goto(),
no constructed URL and no go_back() to a URL that was never clicked.

Task: %(instruction)s

Derived answer (computed offline from src/data/products.json, NOT given to the
agent): product %(pid)d "%(pname)s" at $%(pprice)s - the %(ordinal_word)s
cheapest of %(scope)s (%(pool_n)d products in scope).
Boundary margins: rank %(prev_rank)d id %(prev_id)d $%(prev_price)s
(gap $%(gap_prev)s) and rank %(next_rank)d id %(next_id)d $%(next_price)s
(gap $%(gap_next)s).

Reachability notes verified while authoring:
  * NavBand (components/Header.jsx:316-345) renders the whole category tree in
    the DOM and hides submenus with CSS hover only, so a nested category link
    is clickable without hovering.
  * Sorting is <select id="sorter"> (Toolbar.jsx:113-125). Selecting "price"
    navigates to ?product_list_order=price; a category page's default direction
    is ascending (defaultListDir, catalog.js:1126), so no direction click is
    needed. Never assert on the direction switcher's label - it advertises the
    direction it would switch TO (Toolbar.jsx:79-82).
  * No captured listing exists for this path with product_list_order set, so
    resolveListing() falls through to pool.slice() over the seed-derived sorted
    pool (catalog.js:1213) and CORRECTIONS #58's page-1 capture gap cannot
    apply. Rank %(ordinal)d is on page 1 at the default 12 per page.
  * The tile heart is `a.action.towishlist` inside
    div[data-role="add-to-links"] (ProductGrid.jsx:98-118) and calls
    addToWishlist(product) directly - unlike Add to Cart it never redirects to
    the PDP for products with required options (ProductGrid.jsx:63-66).
"""

TARGET_ID = %(pid)d
TARGET_NAME = %(pname_repr)s
NAV_PATH = %(nav)s
%(filter_line)s

def run(page, base_url, sid):
    # start_path = '/'; the harness has already landed there.
    for label in NAV_PATH:
        page.click("nav.navigation a:has(span:text-is(\\"%%s\\"))" %% label)
        page.wait_for_load_state("networkidle")
%(filter_block)s
    # Sort by price; a category listing defaults to ascending.
    page.select_option("select#sorter", "price")
    page.wait_for_load_state("networkidle")

    tiles = page.locator("li.product-item")
    target = tiles.nth(%(index)d)
    assert TARGET_NAME[:40] in target.inner_text(), target.inner_text()
    target.locator("a.action.towishlist").click()
    page.wait_for_selector("div.message.success")
'''


def replay_py(t, tid):
    sku, price, name, _ = P[t["target"]]
    prev_rank = t["ordinal"] - 1
    next_rank = t["ordinal"] + 1
    if t["price_filter"]:
        filter_line = 'PRICE_BAND = "%s"\n' % t["price_filter"][1]
        filter_block = (
            '\n    # Shop By > Price facet (LayeredNav.jsx:84-128).\n'
            '    page.click("dd.filter-options-content a:has-text(\\"%s\\")")\n'
            '    page.wait_for_load_state("networkidle")\n' % t["price_filter"][1]
        )
    else:
        filter_line = ""
        filter_block = ""
    return REPLAY_TMPL % {
        "tid": tid,
        "instruction": t["instruction"],
        "pid": t["target"],
        "pname": name.replace('"', "'")[:120],
        "pname_repr": repr(name),
        "pprice": price,
        "ordinal": t["ordinal"],
        "ordinal_word": t["ordinal_word"],
        "scope": scope_phrase(t),
        "pool_n": t["pool_n"],
        "prev_rank": prev_rank,
        "prev_id": t["prev_id"],
        "prev_price": t["prev_price"],
        "gap_prev": round(price - t["prev_price"], 2),
        "next_rank": next_rank,
        "next_id": t["next_id"],
        "next_price": t["next_price"],
        "gap_next": round(t["next_price"] - price, 2),
        "nav": repr(t["nav"]),
        "filter_line": filter_line,
        "filter_block": filter_block,
        "index": t["ordinal"] - 1,
    }


def build(t):
    tid = "%s_%s_%s" % (LANE, t["slug"], t["num"])
    d = os.path.join(OUT, tid)
    os.makedirs(d, exist_ok=True)
    sku, price, name, _ = P[t["target"]]
    expected_ids = list(t["inject"] or []) + [t["target"]]

    success = [
        ("wishlist.items contains exactly the products %s - the %s-cheapest "
         "product of %s is id %d (%s, $%s)"
         % (expected_ids, t["ordinal_word"], scope_phrase(t), t["target"], sku, price)),
        ("the row for product %d carries sku %s, the catalog product name and "
         "price %s, as written by addToWishlist" % (t["target"], sku, price)),
    ]

    with open(os.path.join(d, "task_instruction.json"), "w") as f:
        json.dump({
            "task_id": tid,
            "task_instruction": t["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success,
        }, f, indent=2, ensure_ascii=False)
        f.write("\n")

    notes = [
        ("%s (category %d) is one of the 22 fully-seeded categories: %d seeded "
         "listable products, equal to the source's dbProductCount, so an "
         "ordinal computed on the seed equals the one a human computes on the "
         "page. The ordinal here is taken over %d products in scope."
         % (t["category"], t["cat_id"], t["cat_n"], t["pool_n"])),
        ("Target id %d at $%s is rank %d by ascending finalPrice. Boundary "
         "margins: rank %d id %d $%s (gap $%s below) and rank %d id %d $%s "
         "(gap $%s above). Both are strict, so the ordinal has exactly one "
         "answer and does not depend on sortProducts' id tie-break "
         "(catalog.js:1104)."
         % (t["target"], price, t["ordinal"], t["ordinal"] - 1, t["prev_id"],
            t["prev_price"], round(price - t["prev_price"], 2), t["ordinal"] + 1,
            t["next_id"], t["next_price"], round(t["next_price"] - price, 2))),
        ("specialPrice is null on all 22,460 listable products, so finalPrice() "
         "(catalog.js:416) is the base price and the toolbar's Price sort is "
         "exact over the seed."),
        ("listingKey(path, query, ALL_KEYS) (catalog.js:649-664) was computed "
         "for the exact URL select#sorter navigates to - the order param with "
         "NO dir (Toolbar.jsx:113-125) - and for the dir=asc variant; neither "
         "matches any row in listings.json. resolveListing() therefore falls "
         "through to pool.slice() (catalog.js:1213), the CORRECTIONS #58 "
         "page-1 capture gap cannot apply, and rank %d renders on page 1 at "
         "the default 12 per page. (competitive-swimwear and "
         "heating-cooling-air-quality DO match on that key and are excluded "
         "from this lane.)" % t["ordinal"]),
        ("The tile heart a.action.towishlist (ProductGrid.jsx:98-118) calls "
         "addToWishlist (AppContext.jsx:324-346) directly; unlike Add to Cart "
         "(ProductGrid.jsx:63-66) it never redirects for required options. The "
         "PDP control (ProductPage.jsx:797-816) reaches the same handler."),
        ("The reward asserts the exact resulting wish-list membership plus the "
         "catalog sku/name/price on the target row, and reads current_state "
         "only. The wish list boots empty (data/wishlist.json), so the "
         "untouched session scores 0.0."),
    ]
    if t["price_filter"]:
        notes.append(
            "Price facet semantics are half-open, v >= from && v < to "
            "(catalog.js:1167-1173). priceFacets (catalog.js:1271-1283) returns "
            "the captured Price block verbatim when an anchor exists; the %s "
            "bucket is one of those captured buckets and its count reproduces "
            "capture exactly (count == |pool| == %d), so the shortlist an "
            "agent sees is the shortlist the ordinal was computed over."
            % (t["price_filter"][1], t["pool_n"]))

    meta = {
        "style": t["style"],
        "difficulty": "medium",
        "shape": "retrieval_writeback",
        "skills": ["R4", "A4"],
        "skill_chain": ("order %s by ascending price and take the row at the "
                        "stated ordinal position -> add exactly that product to "
                        "the wish list" % scope_phrase(t)),
        "derived_from": t["derived_from"],
        "official_analogues": t["analogues"],
        "topic": "nth_cheapest_wishlist",
        "lane": LANE,
        "batch": "batch-6 lane 40 (shopping / R4 -> A4)",
        "surface": "%s category listing toolbar (select#sorter) -> tile a.action.towishlist -> /wishlist/" % t["category"],
        "inspiration_ids": ["webarena-465", "webarena-513", "webarena-324", "webarena-351"],
        "authoring_notes": notes,
        "hard_criteria": [],
        "has_initial_setup": bool(t["inject"]),
    }
    if t["inject"]:
        meta["injected_preconditions"] = [
            "wishlist.items pre-seeded with productId %d (%s, $%s), description empty"
            % (pid, P[pid][2][:56], P[pid][1]) for pid in t["inject"]
        ] + ["nextWishlistItemId set to %d so a fresh add cannot collide"
             % (len(t["inject"]) + 1)]

    with open(os.path.join(d, "task.json"), "w") as f:
        json.dump({
            "schema_version": 2,
            "task_id": tid,
            "instruction": t["instruction"],
            "apps": [{
                "name": APP_DIR,
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
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
        }, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(os.path.join(d, "reward.py"), "w") as f:
        f.write(reward_py(t, tid))
    with open(os.path.join(d, "nemo_reward.py"), "w") as f:
        f.write(nemo_reward_py(t, tid))

    setup_src = None
    if t["inject"]:
        setup_src = setup_py(t, tid)
        with open(os.path.join(d, "initial_setup.py"), "w") as f:
            f.write(setup_src)

    with open(os.path.join(d, "nemo_reward.py")) as f:
        reward_src = f.read()

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": t["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": reward_src,
            },
        }
    }
    with open(os.path.join(d, "nemo_task.json"), "w") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)
        f.write("\n")

    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as f:
        f.write(replay_py(t, tid))

    return tid, row


def main():
    os.makedirs(BATCH, exist_ok=True)
    ids = []
    rows = []
    for t in TASKS:
        tid, row = build(t)
        ids.append(tid)
        rows.append(row)
    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump({"schema_version": 2,
                   "tasks": [{"task_id": i, "path": "../../%s/task.json" % i} for i in ids]},
                  f, indent=2)
        f.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("\n".join(ids))


main()
