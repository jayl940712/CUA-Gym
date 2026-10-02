#!/usr/bin/env python3
"""Generator for lane 30 (shopping_advsearch_bench). Writes 10 flat bundles."""
import json, os
from pathlib import Path

ROOT = Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output/tasks/shopping"
SLUG = "shopping_advsearch_bench"

APP = "webarena_shopping_mock"
ENV = "CUA_GYM_WEBARENA_SHOPPING_URL"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

HELPERS = '''
NUM_RE = re.compile(r"\\d+(?:\\.\\d+)?")


def _numbers(text):
    if not isinstance(text, str):
        return []
    return NUM_RE.findall(text.replace(",", ""))


def _collection(state, key):
    """items list under a {key: {"items": [...]}} node, or None when absent."""
    node = state.get(key) if isinstance(state, dict) else None
    if not isinstance(node, dict):
        return None
    items = node.get("items")
    return items if isinstance(items, list) else None


def _ids(items):
    out = []
    for entry in items or []:
        if isinstance(entry, dict):
            try:
                out.append(int(entry.get("productId")))
            except (TypeError, ValueError):
                out.append(None)
    return out


def _line(items, product_id):
    for entry in items or []:
        if isinstance(entry, dict):
            try:
                if int(entry.get("productId")) == product_id:
                    return entry
            except (TypeError, ValueError):
                continue
    return None


def _qty(entry):
    try:
        return int(entry.get("qty"))
    except (TypeError, ValueError, AttributeError):
        return None
'''

REWARD_TAIL = '''

def _current_state(evidence):
    apps = (evidence or {}).get("apps") or {}
    for key in ("shopping", "webarena_shopping_mock"):
        app = apps.get(key)
        if isinstance(app, dict):
            state = app.get("current_state")
            if isinstance(state, dict):
                return state
    return {}


def evaluate(evidence):
    state = _current_state(evidence)
    checks = score_state(state)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": DETAILS[name],
        }
        for name in COMPONENT_WEIGHTS
    ]
    return {
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }
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
        checks = score_state(state)
        total = 0.0
        for name in COMPONENT_WEIGHTS:
            if checks.get(name):
                total += COMPONENT_WEIGHTS[name]
            print("component " + name + ": " + ("1" if checks.get(name) else "0"))
        print("REWARD: " + str(round(total, 6)))
    except Exception as exc:  # noqa: BLE001
        print("reward error: " + repr(exc))
        print("REWARD: 0.0")


main()
'''

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{doc}

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

# POST /post?sid= with action "set" shallow-merges this object over
# createInitialData() server-side (vite.config.js:442-449) and writes the merged
# tree to BOTH the current state and the /go baseline, so only the top-level
# keys that change are listed. The literal is raw so no backslash escape is
# eaten by the Python parser before json.loads sees it.
STATE_PATCH = json.loads(r"""
{patch}
""")


def verify():
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": STATE_PATCH}},
        timeout=60,
    )
    response.raise_for_status()
    verify()


main()
'''

EMPTY_CART = {"cart": {"quoteId": 255, "items": []}}


def compare_seed():
    patch = dict(EMPTY_CART)
    patch["compareList"] = {"items": [
        {"productId": 15033, "sku": "B087QSCXGT",
         "name": "Uttermost Volterra Crackled Taupe-Gray Ceramic Table Lamp"},
        {"productId": 15787, "sku": "B08JLHHCM6",
         "name": ("NOZE Rustic Coat Rack Wall Mounted Shelf with 4 Hooks, Hanging "
                  "Entryway Organizer for Mug Coffee Cup, Holding Solid Wooden Shelf "
                  "with 2 Baskets for Kitchen Living Room, Bathroom and Bedroom")},
    ]}
    return patch


WISHLIST_SEED = {"wishlist": {"items": [
    {"wishlistItemId": 1, "productId": 18582, "sku": "B08G1CJRL7",
     "name": ("Neewer 90W Desk Mount LED Video Light C-Clamp Stand Kit with 2.4G "
              "Remote, Dimmable Bi-color 3200K-5600K CRI96+ Studio Light for "
              "Photography Video Conference Game Streaming YouTube"),
     "price": 209.49, "qty": 2, "description": "studio kit",
     "addedAt": "2023-05-01 09:12:44"},
    {"wishlistItemId": 2, "productId": 87100, "sku": "B08VWBFWXY",
     "name": ("Atlantic Furniture Metro Platform Bed with Footboard and Turbo "
              "Charger, Twin, Espresso"),
     "price": 794.33, "qty": 1, "description": "",
     "addedAt": "2023-05-02 18:03:10"},
]}, "nextWishlistItemId": 3}


TASKS = []


def task(**kw):
    TASKS.append(kw)


# ----------------------------------------------------------------- 001
task(
    task_id=f"{SLUG}_binoculars_floor_compare_swap_001",
    difficulty="hard", style="terse", shape=None,
    hard_criteria=["multi_mutation", "derived_target", "cross_section"],
    instruction=(
        "My binoculars budget starts at $400. Work out the cheapest product with "
        "\"binoculars\" in its name at or above that, then leave it as the only "
        "entry on my comparison list and the only line in my cart."
    ),
    criteria=[
        "compareList.items holds exactly one entry, productId 19604 (SLSFJLKJ 10X42 FMC Binoculars, $443.65)",
        "cart.items holds exactly one line, productId 19604, qty 1",
    ],
    setup_doc=(
        "Empties the cart and preloads the comparison list with two unrelated\n"
        "products, so the results-page Add to Compare must REPLACE what is there.\n"
        "addToCompare is a no-op on an already-listed product (AppContext.jsx:400),\n"
        "and the pristine compareList is empty (dataManager.js:143), so the\n"
        "remove-then-add branch of ComparePage/CompareBlock is unreachable without\n"
        "this injection."
    ),
    patch=compare_seed(),
    weights={"compare_list_is_only_cheapest_binocular": 0.5,
             "cart_is_only_cheapest_binocular": 0.5},
    details={
        "compare_list_is_only_cheapest_binocular":
            "compareList.items == [productId 19604] exactly",
        "cart_is_only_cheapest_binocular":
            "cart.items == [productId 19604, qty 1] exactly",
    },
    score_body='''
TARGET = 19604


def score_state(state):
    compare = _collection(state, "compareList")
    cart = _collection(state, "cart")
    line = _line(cart, TARGET) if cart is not None else None
    return {
        "compare_list_is_only_cheapest_binocular":
            compare is not None and _ids(compare) == [TARGET],
        "cart_is_only_cheapest_binocular":
            cart is not None and len(cart) == 1 and line is not None
            and _qty(line) == 1,
    }
''',
    notes=[
        "Derived target: advanced search Product Name=binoculars, Price from 400 -> 3 hits; "
        "cheapest is 19604 at $443.65, runner-up $3,749.99 (margin $3,306.34). Verified live "
        "on the results page ('3 items were found').",
        "Branch unlocked by the injected compareList pair: AppContext.jsx:412 removeFromCompare "
        "must run twice before the results-tile addToCompare (AppContext.jsx:398) produces the "
        "single-column table. On the pristine seed compareList is [] (dataManager.js:143) and "
        "the remove path never executes.",
        "Test 2/3 vs shopping_wishlist_compare_clear_and_rebuild_008 and "
        "shopping_last_row_removal_sole_compare_column_removed_003: those start ON the compare "
        "page with the entities named outright and use Clear All / a single Remove. Here the "
        "differing line is AdvancedSearchPage.jsx:385-395 (the advanced filter), which no prior "
        "shopping task reaches, and the agent must compose a form query to learn which product "
        "the task is about.",
    ],
)

# ----------------------------------------------------------------- 002
task(
    task_id=f"{SLUG}_microwave_floor_wishlist_tally_002",
    difficulty="hard", style="terse", shape="retrieval_writeback",
    hard_criteria=["derived_target", "multi_mutation", "cross_section"],
    instruction=(
        "Search the catalogue for products with \"microwave\" in the name costing "
        "$500 or more. Save the cheapest of them to my wish list, and put how many "
        "matches there were - just the number - in that saved item's comment."
    ),
    criteria=[
        "wishlist.items holds exactly one entry, productId 14431 (YJYDD Microwave Stand Industrial, $607.85)",
        "that entry's comment/description contains the match count 4 and no other number",
    ],
    setup_doc=None, patch=None,
    weights={"wishlist_holds_only_cheapest_microwave": 0.6,
             "comment_records_the_match_tally": 0.4},
    details={
        "wishlist_holds_only_cheapest_microwave":
            "wishlist.items == [productId 14431] exactly",
        "comment_records_the_match_tally":
            "that row's description carries the number 4 and no other number",
    },
    score_body='''
TARGET = 14431
TALLY = "4"


def score_state(state):
    wishlist = _collection(state, "wishlist")
    row = _line(wishlist, TARGET) if wishlist is not None else None
    only = wishlist is not None and _ids(wishlist) == [TARGET]
    comment = row.get("description") if isinstance(row, dict) else None
    return {
        "wishlist_holds_only_cheapest_microwave": only,
        "comment_records_the_match_tally":
            only and isinstance(comment, str) and _numbers(comment) == [TALLY],
    }
''',
    notes=[
        "Derived values: Product Name=microwave, Price from 500 -> '4 items were found' "
        "(verified live); cheapest hit 14431 at $607.85, runner-up $758.48 (margin $150.63). "
        "Neither the product nor the count 4 appears in the instruction.",
        "Chain: addToWishlist from the results tile (AppContext.jsx:324) creates the row with "
        "description '', and WishlistPage.updateAll -> updateWishlistItem (AppContext.jsx:347, "
        "WishlistPage.jsx:42-52) then writes the tally onto the row the first step created.",
        "Test 2/3 vs shopping_wishlist_compare_update_qty_comment_004 and "
        "shopping_audit_writeback_shopping_wishlist_price_memo_001: those edit a comment on a "
        "SEEDED wish-list row and the value is a price the row itself prints. Here the wish list "
        "starts empty, the row must first be created from an advanced-search result, and the "
        "written value is the result-set cardinality rendered only at "
        "AdvancedSearchPage.jsx:483 - a string no prior shopping task reads.",
    ],
)

# ----------------------------------------------------------------- 003
task(
    task_id=f"{SLUG}_microscope_ceiling_price_review_003",
    difficulty="medium", style="terse", shape="retrieval_writeback",
    hard_criteria=None,
    instruction=(
        "Among products with \"microscope\" in the name priced $300 or under, give "
        "the most expensive one a five-star review, and use that product's own "
        "price as the review summary."
    ),
    criteria=[
        "myReviews holds exactly one review, productId 17326 (AmScope SE401Z-P, $276.88)",
        "that review's rating is 5",
        "that review's title (Summary) carries the number 276.88 and no other number",
    ],
    setup_doc=None, patch=None,
    weights={"five_star_review_on_dearest_microscope": 0.6,
             "summary_records_that_products_price": 0.4},
    details={
        "five_star_review_on_dearest_microscope":
            "myReviews == exactly one entry, productId 17326, rating 5",
        "summary_records_that_products_price":
            "that review's title carries 276.88 and no other number",
    },
    score_body='''
TARGET = 17326
PRICE = "276.88"


def score_state(state):
    reviews = state.get("myReviews") if isinstance(state, dict) else None
    if not isinstance(reviews, list) or len(reviews) != 1:
        return {"five_star_review_on_dearest_microscope": False,
                "summary_records_that_products_price": False}
    review = reviews[0]
    if not isinstance(review, dict):
        return {"five_star_review_on_dearest_microscope": False,
                "summary_records_that_products_price": False}
    try:
        product_ok = int(review.get("productId")) == TARGET
    except (TypeError, ValueError):
        product_ok = False
    try:
        rating_ok = int(review.get("rating")) == 5
    except (TypeError, ValueError):
        rating_ok = False
    placed = product_ok and rating_ok
    title = review.get("title")
    return {
        "five_star_review_on_dearest_microscope": placed,
        "summary_records_that_products_price":
            placed and isinstance(title, str) and _numbers(title) == [PRICE],
    }
''',
    notes=[
        "Derived target: Product Name=microscope, Price to 300 -> '7 items were found' "
        "(verified live); dearest hit 17326 at $276.88, runner-up $124.02 (margin $152.86). "
        "The scored summary value is that price, which the instruction never states.",
        "Medium, not hard: one mutation (submitReview, AppContext.jsx:427) whose target AND "
        "whose written value must both be derived from a search the agent composes.",
        "17326 carries zero seeded reviews, so the PDP renders 'Be the first to review this "
        "product' (ProductPage.jsx:621) rather than 'Add Your Review' (:615) - the review form "
        "is behind that link, verified live.",
        "Test 2/3 vs shopping_derived_target_shopping_review_cheapest_order_product_003 and the "
        "prepopulated_review_log family: those derive from an ORDER's lines or from an existing "
        "review log. The differing line is AdvancedSearchPage.jsx:393 (the price[to] upper-bound "
        "predicate), and the agent's work is composing a ceiling query rather than reading an order.",
    ],
)

# ----------------------------------------------------------------- 004
task(
    task_id=f"{SLUG}_dishwasher_description_pair_compare_004",
    difficulty="hard", style="terse", shape=None,
    hard_criteria=["multi_mutation", "derived_target", "cross_section"],
    instruction=(
        "Find every product priced $700 or more whose description mentions "
        "\"dishwasher safe\". Line them all up on my comparison list, then put the "
        "cheapest of them in my cart."
    ),
    criteria=[
        "compareList.items holds exactly productIds 66370 and 67381",
        "cart.items holds exactly one line, productId 66370 (XHZC Cutlery Set, $1,081.88), qty 1",
    ],
    setup_doc=(
        "Empties the cart so the required end state - one line, the cheaper of the\n"
        "two description matches - is exactly specifiable. Nothing else is changed;\n"
        "the pristine compare list is already empty (dataManager.js:143)."
    ),
    patch=dict(EMPTY_CART),
    weights={"compare_holds_both_dishwasher_safe_matches": 0.5,
             "cart_holds_the_cheaper_match": 0.5},
    details={
        "compare_holds_both_dishwasher_safe_matches":
            "compareList productIds == {66370, 67381}",
        "cart_holds_the_cheaper_match":
            "cart.items == [productId 66370, qty 1] exactly",
    },
    score_body='''
PAIR = [66370, 67381]
CHEAPER = 66370


def score_state(state):
    compare = _collection(state, "compareList")
    cart = _collection(state, "cart")
    line = _line(cart, CHEAPER) if cart is not None else None
    return {
        "compare_holds_both_dishwasher_safe_matches":
            compare is not None and sorted(_ids(compare)) == sorted(PAIR),
        "cart_holds_the_cheaper_match":
            cart is not None and len(cart) == 1 and line is not None
            and _qty(line) == 1,
    }
''',
    notes=[
        "Derived targets: Description='dishwasher safe', Price from 700 -> '2 items were found' "
        "(verified live): 66370 at $1,081.88 and 67381 at $1,381.00, margin $299.12.",
        "This is the only task in the lane driven by the Description predicate "
        "(AdvancedSearchPage.jsx:389, matching getDescription(p.id)), which also switches on the "
        "descriptions chunk gate at AdvancedSearchPage.jsx:314-316 - a code path no name/price "
        "search touches.",
        "Test 2/3 vs shopping_wishlist_compare_shortlist_010 (price-bucket facet on a category "
        "page) and shopping_duplicate_add_merge_compare_tiles_no_repeat_column_004: those build "
        "a compare list from a category listing or the home page with the products named. Here "
        "the products are identified only by a phrase inside their description text, which is "
        "not searchable anywhere else in the mock.",
    ],
)

# ----------------------------------------------------------------- 005
task(
    task_id=f"{SLUG}_projector_band_extremes_split_005",
    difficulty="hard", style="terse", shape=None,
    hard_criteria=["derived_target", "multi_mutation", "cross_section"],
    instruction=(
        "My projector budget runs from $900 to $20,000. Of the products with "
        "\"projector\" in the name inside that band, put the cheapest in my cart and "
        "save the dearest to my wish list."
    ),
    criteria=[
        "cart.items holds exactly one line, productId 18710 (BLLXMX Office Presentation Digital Projector, $947.09), qty 1",
        "wishlist.items holds exactly one entry, productId 40872 (QFWCJ 4K Short Throw Projector, $17,774.32)",
    ],
    setup_doc=(
        "Empties the cart so 'the cheapest in my cart' is an exactly specifiable end\n"
        "state. The pristine wish list is already empty (src/data/wishlist.json)."
    ),
    patch=dict(EMPTY_CART),
    weights={"cart_holds_cheapest_in_band_projector": 0.5,
             "wishlist_holds_dearest_in_band_projector": 0.5},
    details={
        "cart_holds_cheapest_in_band_projector":
            "cart.items == [productId 18710, qty 1] exactly",
        "wishlist_holds_dearest_in_band_projector":
            "wishlist.items == [productId 40872] exactly",
    },
    score_body='''
CHEAPEST = 18710
DEAREST = 40872


def score_state(state):
    cart = _collection(state, "cart")
    wishlist = _collection(state, "wishlist")
    line = _line(cart, CHEAPEST) if cart is not None else None
    return {
        "cart_holds_cheapest_in_band_projector":
            cart is not None and len(cart) == 1 and line is not None
            and _qty(line) == 1,
        "wishlist_holds_dearest_in_band_projector":
            wishlist is not None and _ids(wishlist) == [DEAREST],
    }
''',
    notes=[
        "Derived targets: Product Name=projector, Price 900-20000 -> '62 items were found' "
        "(verified live). Cheapest 18710 $947.09 vs $995.00 (margin $47.91); dearest 40872 "
        "$17,774.32 vs $16,211.44 (margin $1,562.88).",
        "62 hits is 6 pages at the default limit, so this is the one task in the lane that "
        "forces the advanced-result toolbar: the sorter (AdvancedSearchPage.jsx:233-241, only "
        "Product Name and Price exist) plus the direction switcher (:243-254). Both bounds are "
        "stated deliberately - see the priceKeysUnbalanced finding in GENERATION.md.",
        "Test 2/3 vs shopping_derived_target_shopping_wishlist_price_triage_003 and "
        "shopping_audit_writeback_shopping_budget_compare_sweep_009: those derive extremes from "
        "a collection that already exists in state. Here both extremes come out of a query the "
        "agent composes, and the two extremes are split across two different collections.",
    ],
)

# ----------------------------------------------------------------- 006
task(
    task_id=f"{SLUG}_tripod_band_reviewed_split_006",
    difficulty="medium", style="terse", shape=None,
    hard_criteria=None,
    instruction=(
        "Exactly two products have \"tripod\" in the name and cost between $300 and "
        "$400. One of them carries customer reviews and the other does not. Put the "
        "reviewed one on my comparison list and the other in my cart."
    ),
    criteria=[
        "compareList.items holds exactly one entry, productId 19076 (Canon PowerShot SX620 HS, $359.99, 3 reviews)",
        "cart.items holds exactly one line, productId 90000 (NCRD Selfie Stick Bluetooth, $336.40), qty 1",
    ],
    setup_doc=(
        "Empties the cart so 'the other in my cart' is an exactly specifiable end\n"
        "state. The pristine compare list is already empty (dataManager.js:143)."
    ),
    patch=dict(EMPTY_CART),
    weights={"compare_holds_the_reviewed_tripod": 0.5,
             "cart_holds_the_unreviewed_tripod": 0.5},
    details={
        "compare_holds_the_reviewed_tripod":
            "compareList.items == [productId 19076] exactly",
        "cart_holds_the_unreviewed_tripod":
            "cart.items == [productId 90000, qty 1] exactly",
    },
    score_body='''
REVIEWED = 19076
UNREVIEWED = 90000


def score_state(state):
    compare = _collection(state, "compareList")
    cart = _collection(state, "cart")
    line = _line(cart, UNREVIEWED) if cart is not None else None
    return {
        "compare_holds_the_reviewed_tripod":
            compare is not None and _ids(compare) == [REVIEWED],
        "cart_holds_the_unreviewed_tripod":
            cart is not None and len(cart) == 1 and line is not None
            and _qty(line) == 1,
    }
''',
    notes=[
        "Derived split: Product Name=tripod, Price 300-400 -> '2 items were found' (verified "
        "live). 19076 renders a Rating row and '3 Reviews'; 90000 has ratingSummary null and "
        "reviewsCount 0, so ReviewsSummary returns null (ProductGrid.jsx:36) and its tile shows "
        "no rating element at all. The discriminator is the presence/absence of a DOM node.",
        "Medium: two mutations, both determined by one derivation the agent must run.",
        "Test 2/3 vs shopping_derived_target_shopping_best_rated_of_three_to_cart_004: there the "
        "three products are named outright in the instruction and their ratings are compared on "
        "their PDPs. Here neither product is named, the candidate set comes from "
        "AdvancedSearchPage.jsx:385-395, and the discriminator is rated-vs-unrated rather than "
        "which rating is higher.",
    ],
)

# ----------------------------------------------------------------- 007
task(
    task_id=f"{SLUG}_speaker_band_qty_tally_007",
    difficulty="medium", style="terse", shape="retrieval_writeback",
    hard_criteria=None,
    instruction=(
        "Count the products with \"bluetooth speaker\" in the name priced between "
        "$200 and $500, then make the cheapest of them the only line in my cart, at "
        "a quantity equal to that count."
    ),
    criteria=[
        "cart.items holds exactly one line, productId 17531 (Herdio 5.25 Inches 200 Watts Patio Bluetooth Speaker, $299.98)",
        "that line's qty is 11, the number of matches",
    ],
    setup_doc=(
        "Empties the cart so 'the only line in my cart' is an exactly specifiable\n"
        "end state and the derived quantity is the sole value under test."
    ),
    patch=dict(EMPTY_CART),
    weights={"cart_holds_only_cheapest_in_band_speaker": 0.5,
             "cart_quantity_equals_the_match_tally": 0.5},
    details={
        "cart_holds_only_cheapest_in_band_speaker":
            "cart.items == [productId 17531] exactly",
        "cart_quantity_equals_the_match_tally":
            "that line's qty == 11",
    },
    score_body='''
TARGET = 17531
TALLY = 11


def score_state(state):
    cart = _collection(state, "cart")
    line = _line(cart, TARGET) if cart is not None else None
    only = cart is not None and len(cart) == 1 and line is not None
    return {
        "cart_holds_only_cheapest_in_band_speaker": only,
        "cart_quantity_equals_the_match_tally": only and _qty(line) == TALLY,
    }
''',
    notes=[
        "Derived values: Product Name='bluetooth speaker', Price 200-500 -> '11 items were "
        "found' (verified live); cheapest 17531 at $299.98, runner-up $309.80 (margin $9.82 - "
        "small, which is why the instruction says 'the cheapest' and never a threshold). The "
        "scored quantity 11 is the result-set cardinality and appears nowhere in the instruction.",
        "The tile Add to Cart always adds qty 1 (ProductGrid.jsx:65), so the count must reach "
        "state either through the PDP qty box (ProductPage.jsx:507-515, ceiling 10000) or "
        "through CartPage's Update Shopping Cart -> updateCartQty (AppContext.jsx:282).",
        "Test 2/3 vs shopping_audit_writeback_shopping_saved_and_compared_counts_004 (a count "
        "written into a review body) and shopping_wishlist_compare_saved_to_cart_005 (a "
        "hand-given qty on a seeded wish-list row): the differing line is "
        "AdvancedSearchPage.jsx:483 producing the count, and the differing work is that the "
        "quantity itself is the retrieved answer rather than a number the instruction supplies.",
    ],
)

# ----------------------------------------------------------------- 008
task(
    task_id=f"{SLUG}_cutting_board_cart_line_swap_008",
    difficulty="hard", style="explicit", shape=None,
    hard_criteria=["multi_mutation", "derived_target", "exclusion_constraint",
                   "cross_section"],
    instruction=(
        "My One Stop Market shopping cart holds three lines: the Uttermost Volterra "
        "Crackled Taupe-Gray Ceramic Table Lamp, the NOZE Rustic Coat Rack, and a "
        "Plus Size Lingerie bodysuit that was added by mistake. Swap that third line "
        "out for a chopping board. Use the storefront's Advanced Search (the link is "
        "in the page footer): put \"cutting board\" in Product Name, leave SKU and "
        "both description boxes empty, and enter 60 in the first Price box so the "
        "results are everything from $60 upward. Two products come back - add the "
        "cheaper of the two to the cart at quantity 1. Then open the shopping cart "
        "and remove the Plus Size Lingerie bodysuit line. The Uttermost table lamp "
        "and the NOZE coat rack lines must both survive at quantity 1 with their "
        "options untouched, and my wish list, comparison list and orders must stay "
        "empty of any change."
    ),
    criteria=[
        "cart.items contains a line for productId 48825 (The Ultimate Gourmet Cutting Board, $68.55) at qty 1",
        "cart.items no longer contains productId 10617 (the bodysuit line)",
        "cart.items still contains productId 15033 at qty 1 and productId 15787 at qty 1, and holds exactly three lines",
    ],
    setup_doc=None, patch=None,
    weights={"cutting_board_line_added": 0.4,
             "bodysuit_line_retired": 0.3,
             "surviving_cart_is_exactly_lamp_and_coat_rack": 0.3},
    details={
        "cutting_board_line_added":
            "cart holds productId 48825 at qty 1",
        "bodysuit_line_retired":
            "cart holds a positive number of lines and none of them is productId 10617",
        "surviving_cart_is_exactly_lamp_and_coat_rack":
            "cart holds exactly three lines: 15033 qty 1, 15787 qty 1 and 48825",
    },
    score_body='''
BOARD = 48825
BODYSUIT = 10617
LAMP = 15033
COAT_RACK = 15787


def score_state(state):
    cart = _collection(state, "cart")
    if cart is None:
        return {"cutting_board_line_added": False,
                "bodysuit_line_retired": False,
                "surviving_cart_is_exactly_lamp_and_coat_rack": False}
    ids = _ids(cart)
    board = _line(cart, BOARD)
    lamp = _line(cart, LAMP)
    rack = _line(cart, COAT_RACK)
    board_ok = board is not None and _qty(board) == 1
    return {
        "cutting_board_line_added": board_ok,
        "bodysuit_line_retired": board_ok and BODYSUIT not in ids,
        "surviving_cart_is_exactly_lamp_and_coat_rack":
            board_ok and sorted(ids) == sorted([LAMP, COAT_RACK, BOARD])
            and lamp is not None and _qty(lamp) == 1
            and rack is not None and _qty(rack) == 1,
    }
''',
    notes=[
        "Derived target: Product Name='cutting board', Price from 60 -> 2 hits, 48825 at $68.55 "
        "and 22284 at $129.99 (margin $61.44). The instruction gives the query, never the answer.",
        "Explicit because the cart is NOT emptied by a setup: the honest end state needs 'and "
        "the two seeded lines survive exactly, options included', which is the "
        "and-N-other-things-unchanged shape S3.3 reserves for the explicit set. The bodysuit "
        "line carries two custom options (Size Large / Color Blue), which is why removing it is "
        "the interesting arm.",
        "Every component is gated on the positive marker board_ok, so an empty current_state and "
        "a do-nothing episode both score 0.0 on all three components rather than passing "
        "'bodysuit not present' vacuously.",
        "Test 2/3 vs shopping_drifted_cart_lines_dead_row_dropped_before_checkout_002 and "
        "shopping_last_row_removal_park_then_purge_cart_line_005: those remove a cart line the "
        "instruction names and add nothing derived. The differing line is "
        "AdvancedSearchPage.jsx:385-395; the differing work is that the replacement product is "
        "unknown until the agent runs the query.",
    ],
)

# ----------------------------------------------------------------- 009
task(
    task_id=f"{SLUG}_bookcase_wishlist_retire_009",
    difficulty="hard", style="explicit", shape=None,
    hard_criteria=["derived_target", "multi_mutation", "shortcut_defeating",
                   "exclusion_constraint"],
    instruction=(
        "Two things are saved on my One Stop Market wish list: a Neewer 90W Desk "
        "Mount LED Video Light at quantity 2 with the comment \"studio kit\", and an "
        "Atlantic Furniture Metro Platform Bed at quantity 1. I want a bookcase "
        "instead of whichever of them is the expensive one. Open Advanced Search "
        "from the page footer, put \"bookcase\" in Product Name, 500 in the first "
        "Price box and 1000 in the second, leaving every other box empty, and save "
        "the cheapest of the results to my wish list with the heart action. Then "
        "go to My Wish List and remove "
        "whichever of the two originally-saved items costs more than that new "
        "bookcase does. The other original must stay exactly as it is - same "
        "quantity 2, same \"studio kit\" comment - and do not put anything in my "
        "cart or on my comparison list."
    ),
    criteria=[
        "wishlist.items contains productId 15291 (W&X Multi-Functional Storage Shelf, $563.99)",
        "wishlist.items no longer contains productId 87100 (Atlantic Furniture bed, $794.33)",
        "wishlist.items still contains productId 18582 at qty 2 with comment \"studio kit\", and holds exactly two entries",
    ],
    setup_doc=(
        "Seeds the wish list with two priced rows so 'remove whichever costs more\n"
        "than the new one' is a real comparison. The pristine wish list is empty\n"
        "(src/data/wishlist.json), so WishlistPage's row-remove branch\n"
        "(WishlistPage.jsx:100-104 -> AppContext.jsx:358) and the price column at\n"
        ":75 are both unreachable without this injection."
    ),
    patch=WISHLIST_SEED,
    weights={"cheapest_bookcase_saved": 0.4,
             "dearer_saved_item_retired": 0.3,
             "surviving_wish_list_is_exactly_light_and_bookcase": 0.3},
    details={
        "cheapest_bookcase_saved":
            "wishlist holds productId 15291",
        "dearer_saved_item_retired":
            "the bookcase is saved and productId 87100 is gone",
        "surviving_wish_list_is_exactly_light_and_bookcase":
            "wishlist holds exactly 18582 (qty 2, comment 'studio kit') and 15291",
    },
    score_body='''
BOOKCASE = 15291
DEARER = 87100
KEEPER = 18582
KEEPER_COMMENT = "studio kit"


def score_state(state):
    wishlist = _collection(state, "wishlist")
    if wishlist is None:
        return {"cheapest_bookcase_saved": False,
                "dearer_saved_item_retired": False,
                "surviving_wish_list_is_exactly_light_and_bookcase": False}
    ids = _ids(wishlist)
    saved = BOOKCASE in ids
    keeper = _line(wishlist, KEEPER)
    comment = keeper.get("description") if isinstance(keeper, dict) else None
    return {
        "cheapest_bookcase_saved": saved,
        "dearer_saved_item_retired": saved and DEARER not in ids,
        "surviving_wish_list_is_exactly_light_and_bookcase":
            saved and sorted(ids) == sorted([KEEPER, BOOKCASE])
            and keeper is not None and _qty(keeper) == 2
            and isinstance(comment, str) and comment.strip() == KEEPER_COMMENT,
    }
''',
    notes=[
        "Derived target: Product Name=bookcase, Price 500-1000 -> 7 hits on one page; cheapest "
        "15291 at $563.99, runner-up $579.00 (margin $15.01). An upper bound is stated because "
        "a one-sided price query cannot be paged - see the priceKeysUnbalanced finding in "
        "GENERATION.md. The removal target is then derived a second "
        "time by comparing $563.99 against the two saved prices ($209.49 keeps, $794.33 goes).",
        "shortcut_defeating: the obvious shortcut - clear the wish list and save only the "
        "bookcase - scores 0.4 + 0.3 = 0.7, because the third component requires the Neewer row "
        "to still be present at qty 2 with its comment. Removing the wrong row scores 0.4.",
        "15291 carries required custom options, so its tile Add to Cart would redirect to the "
        "PDP (ProductGrid.jsx:64-67); the heart action addToWishlist has no such guard "
        "(AppContext.jsx:324), which is why the instruction names the heart.",
        "Test 2/3 vs shopping_wishlist_compare_triage_009 and "
        "shopping_wishlist_compare_remove_saved_003: those remove a wish-list row the instruction "
        "names. Here the row to remove is decided by a price comparison against a product that "
        "does not exist in state until the agent's own search produces it - the two steps are "
        "dependent, not concatenated.",
    ],
)

# ----------------------------------------------------------------- 010
task(
    task_id=f"{SLUG}_telescope_floor_sole_hit_trio_010",
    difficulty="medium", style="terse", shape=None,
    hard_criteria=None,
    instruction=(
        "Exactly one product has \"telescope\" in its name and costs $500 or more. "
        "I want three of it: that product at quantity three, as the only line in my "
        "cart."
    ),
    criteria=[
        "cart.items holds exactly one line, productId 18990 (AWJ Telescope 70Mm Aperture, $638.99)",
        "that line's qty is 3",
    ],
    setup_doc=(
        "Empties the cart so 'the only line in my cart' is an exactly specifiable\n"
        "end state."
    ),
    patch=dict(EMPTY_CART),
    weights={"cart_holds_only_the_sole_telescope": 0.6,
             "cart_quantity_is_three": 0.4},
    details={
        "cart_holds_only_the_sole_telescope":
            "cart.items == [productId 18990] exactly",
        "cart_quantity_is_three": "that line's qty == 3",
    },
    score_body='''
TARGET = 18990


def score_state(state):
    cart = _collection(state, "cart")
    line = _line(cart, TARGET) if cart is not None else None
    only = cart is not None and len(cart) == 1 and line is not None
    return {
        "cart_holds_only_the_sole_telescope": only,
        "cart_quantity_is_three": only and _qty(line) == 3,
    }
''',
    notes=[
        "Derived target: Product Name=telescope, Price from 500 -> '1 item were found' (verified "
        "live), product 18990 at $638.99. 35 further telescopes exist below $500, so the price "
        "bound is doing real work and the answer is unique by construction.",
        "Medium: two dependent mutations - the line must exist before its quantity can be three "
        "(or the PDP qty box must be set before the add). A single tile Add to Cart scores 0.6.",
        "Test 2/3 vs shopping_blocked_form_recovery_pdp_qty_ceiling_bulk_add_003_v3 and "
        "shopping_duplicate_add_merge_tile_button_repeat_adds_008_v3: both start on a PDP or a "
        "search-result URL for a NAMED product. Here the differing line is "
        "AdvancedSearchPage.jsx:392 (the price[from] lower bound), and the agent must first "
        "establish which product the sentence is about.",
    ],
)


def build(t):
    d = OUT / t["task_id"]
    d.mkdir(parents=True, exist_ok=True)

    weights = t["weights"]
    assert abs(sum(weights.values()) - 1.0) < 1e-9, t["task_id"]

    header = (
        '"""Deterministic reward for %s.\n\n'
        'Reads the storefront current_state only; never the baseline.\n"""\n\n'
        "import re\n" % t["task_id"]
    )
    weights_src = "COMPONENT_WEIGHTS = " + json.dumps(weights, indent=4) + "\n"
    weights_src += "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n\n"
    weights_src += "DETAILS = " + json.dumps(t["details"], indent=4) + "\n"
    body = header + HELPERS + "\n" + weights_src + t["score_body"] + REWARD_TAIL
    (d / "reward.py").write_text(body, encoding="utf-8")

    nemo_header = (
        '"""NeMo-Gym reward program for %s.\n\n'
        'Same rubric as reward.py. Reads /go current_state only.\n"""\n\n'
        "import re\n\nimport requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n' % (t["task_id"], URL_PLACEHOLDER)
    )
    nemo = nemo_header + HELPERS + "\n" + weights_src + t["score_body"] + NEMO_TAIL
    (d / "nemo_reward.py").write_text(nemo, encoding="utf-8")

    setup_code = None
    if t["patch"] is not None:
        setup_code = SETUP_TEMPLATE.format(
            task_id=t["task_id"], doc=t["setup_doc"], url=URL_PLACEHOLDER,
            patch=json.dumps(t["patch"], indent=1),
        )
        (d / "initial_setup.py").write_text(setup_code, encoding="utf-8")
    else:
        if (d / "initial_setup.py").exists():
            (d / "initial_setup.py").unlink()

    instruction_doc = {
        "task_id": t["task_id"],
        "task_instruction": t["instruction"],
        "app_dir": APP,
        "start_path": "/",
        "difficulty": t["difficulty"],
        "success_criteria": t["criteria"],
    }
    (d / "task_instruction.json").write_text(
        json.dumps(instruction_doc, indent=2) + "\n", encoding="utf-8")

    metadata = {
        "difficulty": t["difficulty"],
        "style": t["style"],
        "topic": "shopping storefront advanced-search benches",
        "batch": SLUG,
        "inspiration_ids": t.get("inspiration_ids", ["webarena-125", "webarena-263"]),
        "authoring_notes": t["notes"],
    }
    if t["shape"]:
        metadata["shape"] = t["shape"]
    if t["hard_criteria"]:
        metadata["hard_criteria"] = t["hard_criteria"]

    manifest = {
        "schema_version": 2,
        "task_id": t["task_id"],
        "instruction": t["instruction"],
        "apps": [{
            "name": APP,
            "source_name": "shopping",
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
    }
    (d / "task.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    row = {"task_payload": {
        "task_id": t["task_id"],
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP],
        "start_urls": [],
        "intent": t["instruction"],
        "eval": {"eval_types": ["string_match"], "reference_answers": None,
                 "note": "unused - CUA-Gym reward code is authoritative"},
        "cuagym": {
            "bundle_id": t["task_id"],
            "app_dir": APP,
            "initial_setup": setup_code,
            "eval_reward_code": (d / "nemo_reward.py").read_text(encoding="utf-8"),
        },
    }}
    (d / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main():
    rows = [build(t) for t in TASKS]
    batch = OUT / "_batches" / SLUG
    batch.mkdir(parents=True, exist_ok=True)
    with (batch / "nemo_tasks.jsonl").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    (batch / "index.json").write_text(json.dumps({
        "schema_version": 2,
        "tasks": [{"task_id": t["task_id"], "path": f"../../{t['task_id']}/task.json"}
                  for t in TASKS],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} bundles")
    for t in TASKS:
        words = len(t["instruction"].split())
        print(f"  {t['task_id']:60s} {t['difficulty']:6s} {t['style']:8s} {words:3d}w "
              f"{t['shape'] or '-'}")


main()
