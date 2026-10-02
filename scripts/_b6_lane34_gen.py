#!/usr/bin/env python3
"""Batch-6 lane 34 generator -- shopping, R3 -> A4.

Chain: count/enumerate the products a stated price band returns inside one
category, then add every one of them to the cart or the wish list.

Every fact below was measured against
hub/websites/webarena_shopping_mock/src/data/{products,categories,listings}.json
during authoring (see GENERATION.md). Nothing here is executed against a
running mock -- this script only writes bundle files.
"""
import json
import os

ROOT = "/home/ubuntu/CUA-Gym/output/tasks/shopping"
BATCH = os.path.join(ROOT, "_batches", "price_cell_pair_to_cart")
REPLAYS = os.path.join(BATCH, "replays")

APP = "webarena_shopping_mock"

# The three seeded cart lines (src/data/cart.json). None of the targets below
# collides with them, so addToCart's product+options merge never fires.
SEED_CART = [(15033, 1), (15787, 1), (10617, 1)]

ANALOGUE_CART = ("Buy the highest rated product from the meat substitute category "
                 "within a budget between 100 and 200. Discard any items in your "
                 "cart if it is not empty.")
ANALOGUE_CART2 = ("Buy the highest rated product from the Ceiling light category "
                  "within a budget above 1000. Discard any items in your cart if it "
                  "is not empty.")
ANALOGUE_RANGE = "What is the price range of wireless earphone in the One Stop Market?"
ANALOGUE_RANGE2 = "What is the price range of Canon photo printer in the One Stop Market?"
ANALOGUE_WISH = ("Add Tide PODS Spring Meadow Scent HE Turbo Laundry Detergent Pacs, "
                 "81 Count to my wish list")
ANALOGUE_WISH2 = ("Add HONGJ Hawaiian Beach Outfits Set for Mens, Summer Tropical Tree "
                  "Printed Relaxed-fit Hawaii Shirts Shorts 2 Piece Suits to my wish list")

TASKS = [
    dict(
        n=1, slug="nintendo_systems_100up_cart", target="cart", style="terse",
        instruction="Add every product in the Nintendo Systems category priced "
                    "$100.00 and above to my shopping cart.",
        cat_path="video-games/legacy-systems/nintendo-systems",
        cat_trail=["Video Games", "Legacy Systems", "Nintendo Systems"],
        facet_label="$100.00 and above", price_param="100-200",
        matched=[(100325, "amiibo aori", 156.85),
                 (74818, "Nintendo 2DS - Scarlet Red / White (Renewed)", 189.99)],
        options_free=True,
        margin="nearest non-match is $89.99 (ids 42331, 89756); nothing in the "
               "category is priced at or above $200, so the sidebar bucket "
               "'100-200' and the phrase '$100.00 and above' select the same two rows.",
        analogues=[ANALOGUE_CART, ANALOGUE_RANGE],
    ),
    dict(
        n=2, slug="deli_meats_100up_cart", target="cart", style="terse",
        instruction="Everything in Deli Meats & Cheeses priced $100.00 or more "
                    "should go into my shopping cart.",
        cat_path="grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses",
        cat_trail=["Grocery & Gourmet Food", "Deli & Prepared Foods", "Deli Meats & Cheeses"],
        facet_label="$100.00 and above", price_param="100-200",
        matched=[(90775, "Rays Country Ham - 16 lb. - Whole Bone-in Country Ham - "
                         "Blue Ridge Mountain Cured", 110.25),
                 (47884, "Serrano Ham Bone in from Spain 14.7 - 17 lb + Ham Stand + "
                         "Knife - Cured Spanish Jamon", 199.99)],
        options_free=True,
        margin="the nearest non-match is id 21425 at $99.99 -- one cent under the "
               "boundary, and excluded by the half-open filter v >= from && v < to "
               "(catalog.js:1167-1173). Category max is $199.99, so 'or more' and "
               "the captured 100-200 bucket agree.",
        analogues=[ANALOGUE_CART, ANALOGUE_RANGE],
    ),
    dict(
        n=3, slug="fresh_meal_kits_200up_cart", target="cart", style="explicit",
        instruction="I'm putting together a lobster night. Open Grocery & Gourmet "
                    "Food > Fresh Meal Kits, use the Shopping Options price filter "
                    "to select the $200.00 and above band, and add each product "
                    "that band lists to my shopping cart, one of each.",
        cat_path="grocery-gourmet-food/fresh-meal-kits",
        cat_trail=["Grocery & Gourmet Food", "Fresh Meal Kits"],
        facet_label="$200.00 and above", price_param="200-300",
        matched=[(80721, "Lobsterorder.com's Shore Score for 6", 269.99),
                 (91545, "Lobsterorder.com's Maine Downeast Feast", 289.99)],
        options_free=True,
        margin="nearest non-match is $107.99 (id 80034), a $92 gap; category max "
               "is $289.99 so nothing sits above the bucket.",
        analogues=[ANALOGUE_CART, ANALOGUE_RANGE2],
    ),
    dict(
        n=4, slug="playstation_200s_cart", target="cart", style="terse",
        instruction="Add every PlayStation Systems product that falls in the "
                    "$200.00 - $299.99 price band to my shopping cart.",
        cat_path="video-games/legacy-systems/playstation-systems",
        cat_trail=["Video Games", "Legacy Systems", "PlayStation Systems"],
        facet_label="$200.00 - $299.99", price_param="200-300",
        matched=[(19173, "Sony Playstation 3 160GB System (Renewed)", 247.99),
                 (17882, "Extreme Sim Racing Wheel Stand Cockpit SXT V2", 249.00)],
        options_free=True,
        margin="bounded on both sides: $199.99 (id 99661) below, $346.48 (id 77590) "
               "above. This is a middle bucket, so 'and above' phrasing would have "
               "been wrong and the band is stated as a closed range.",
        analogues=[ANALOGUE_CART, ANALOGUE_RANGE],
    ),
    dict(
        n=5, slug="mp3_accessories_400s_cart", target="cart", style="terse",
        instruction="In MP3 & MP4 Player Accessories, add every product in the "
                    "$400.00 - $499.99 price band to my shopping cart.",
        cat_path="electronics/portable-audio-video/mp3-mp4-player-accessories",
        cat_trail=["Electronics", "Portable Audio & Video", "MP3 & MP4 Player Accessories"],
        facet_label="$400.00 - $499.99", price_param="400-500",
        matched=[(19485, "Speaker Portable Wireless Bluetooth Speaker 20W", 487.95),
                 (41190, "ECOXGEAR SoundExtreme SEB26", 499.00)],
        options_free=False,
        margin="$383.98 (id 41297) below, $585.40 (id 43382) above -- a $16 and a "
               "$86 gap. Product 19485 carries one required option, so its tile "
               "Add to Cart navigates to the PDP (ProductGrid.jsx:63-66); the "
               "rubric therefore does not constrain options[].",
        analogues=[ANALOGUE_CART2, ANALOGUE_RANGE],
    ),
    dict(
        n=6, slug="kids_bedding_70s_wishlist", target="wishlist", style="terse",
        instruction="Save every Kids' Bedding product priced between $70.00 and "
                    "$79.99 to my wish list.",
        cat_path="home-kitchen/bedding/kids-bedding",
        cat_trail=["Home & Kitchen", "Bedding", "Kids' Bedding"],
        facet_label="$70.00 - $79.99", price_param="70-80",
        matched=[(31394, "SHOMPE Music Skull Comforter Sets Full Size", 75.99),
                 (15842, "Ambesonne Japanese Duvet Cover Set", 79.95)],
        options_free=False,
        margin="$69.99 (id 99157) below, $88.99 (id 67733) above. Kids' Bedding's "
               "nine captured buckets 3/21/31/14/15/6/7/2/1 each equal the seeded "
               "count exactly; this is the '2' bucket.",
        analogues=[ANALOGUE_WISH, ANALOGUE_RANGE],
    ),
    dict(
        n=7, slug="chairs_sofas_1000up_wishlist", target="wishlist", style="terse",
        instruction="Add every Chairs & Sofas product priced $1,000.00 and above "
                    "to my wish list.",
        cat_path="office-products/office-furniture-lighting/chairs-sofas",
        cat_trail=["Office Products", "Office Furniture & Lighting", "Chairs & Sofas"],
        facet_label="$1,000.00 and above", price_param="1000-2000",
        matched=[(36277, "LZQDM Office Chair-Ergonomic Office Desk Chair", 1489.88),
                 (68674, "WYH Computer Office Desk Office Chair Executive", 1811.68)],
        options_free=False,
        margin="nearest non-match is $884.60 (id 14536), a $115 gap; category max "
               "is $1,811.68. Both targets are reached through the price facet, "
               "whose filtered URL has no captured listing, so the "
               "CORRECTIONS #58 capture/pool gap cannot hide either row.",
        analogues=[ANALOGUE_WISH, ANALOGUE_RANGE2],
    ),
    dict(
        n=8, slug="competitive_swimwear_40s_wishlist", target="wishlist", style="explicit",
        instruction="I want to compare the mid-priced swim gear. Go to Clothing, "
                    "Shoes & Jewelry > Sport Specific Clothing > Competitive "
                    "Swimwear, narrow the Shopping Options price filter to the "
                    "$40.00 - $49.99 band, and put every product that band returns "
                    "on my wish list.",
        cat_path="clothing-shoes-jewelry/sport-specific-clothing/competitive-swimwear",
        cat_trail=["Clothing, Shoes & Jewelry", "Sport Specific Clothing", "Competitive Swimwear"],
        facet_label="$40.00 - $49.99", price_param="40-50",
        matched=[(12845, "LIULQF Men's Beach Pants Sports Shorts", 45.34),
                 (12561, "Swimwear Women Plus Size, Two-Piece Bikini Swimsuit", 48.53)],
        options_free=False,
        margin="$38.91 (id 25923) below, $64.26 (id 64294) above.",
        analogues=[ANALOGUE_WISH2, ANALOGUE_RANGE],
    ),
    dict(
        n=9, slug="fan_shop_footwear_40s_wishlist", target="wishlist", style="terse",
        instruction="In Sports & Outdoors > Fan Shop > Footwear, add every product "
                    "in the $40.00 - $49.99 price band to my wish list.",
        cat_path="sports-outdoors/fan-shop/footwear",
        cat_trail=["Sports & Outdoors", "Fan Shop", "Footwear"],
        facet_label="$40.00 - $49.99", price_param="40-50",
        matched=[(12753, "AIHOU Slippers for Women", 41.49),
                 (10565, "Auimank Fashionable Women's High-Heeled Fish Mouth Shoes", 42.09)],
        options_free=False,
        margin="$34.93 (id 28499) below, $61.38 (id 83290) above.",
        analogues=[ANALOGUE_WISH2, ANALOGUE_RANGE2],
    ),
    dict(
        n=10, slug="table_linens_140up_wishlist", target="wishlist", style="terse",
        instruction="Add every Kitchen & Table Linens product priced $140.00 or "
                    "more to my wish list.",
        cat_path="home-kitchen/kitchen-dining/kitchen-table-linens",
        cat_trail=["Home & Kitchen", "Kitchen & Dining", "Kitchen & Table Linens"],
        facet_label="$100.00 and above", price_param="100-200",
        matched=[(14760, "Purple Ultimate Seat Cushion", 149.00),
                 (15582, "Leather Moroccan Pouf", 180.00)],
        options_free=False,
        margin="the stated $140 threshold is NOT a sidebar bucket: the widest "
               "bucket is '$100.00 and above' with three rows, and id 32183 at "
               "$119.99 is the near-miss the agent must drop. Gap below the "
               "threshold is $20.01, and the category max is $180.",
        analogues=[ANALOGUE_WISH, ANALOGUE_RANGE2],
    ),
]

SKILL_CHAIN = ("R3 enumerate the products one stated price band returns inside a "
               "category -> A4 add each of them to %s")


# --------------------------------------------------------------------------- #
# reward source                                                                #
# --------------------------------------------------------------------------- #

CART_BODY = '''
COMPONENT = "cart_lines_now_exactly_expected"
COMPONENT_WEIGHTS = {COMPONENT: 1.0}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

# (productId, qty) for every line the cart must hold when the episode ends:
# the three seeded lines 554/555/556 plus the two the price band returns.
# addToCart merges by productId + the set of chosen optionTypeIds
# (AppContext.jsx:251-281), so a correct run appends two new lines at qty 1 and
# leaves the seeded three at qty 1 -- five lines, five distinct products.
EXPECTED_LINES = json.loads(r"""__EXPECTED__""")


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _cart_lines(state):
    """Every cart line as a sorted (productId, qty) pair list.

    Options are deliberately not read: two of the ten targets in this lane carry
    required custom options, so the option values a correct run stores depend on
    which variant the agent picked. Line identity and quantity are what the
    instruction determines.
    """
    lines = []
    for item in _list(_dict(_dict(state).get("cart")).get("items")):
        if not isinstance(item, dict):
            continue
        pid = _int(item.get("productId"))
        qty = _int(item.get("qty"))
        lines.append((pid, qty))
    return sorted(lines, key=lambda pair: (pair[0] is None, pair[0], pair[1]))


def score_state(state):
    """The exact resulting cart collection, and nothing else.

    A run that added only one of the two matched products, added a product the
    band does not return, changed a quantity, or removed a seeded line lands on
    a different collection and scores 0.0. So does an untouched session, whose
    cart holds three lines.
    """
    want = sorted((_int(row.get("productId")), _int(row.get("qty")))
                  for row in EXPECTED_LINES)
    got = _cart_lines(state)
    ok = bool(got == want)
    return [{
        "name": COMPONENT,
        "score": COMPONENT_WEIGHTS[COMPONENT] if ok else 0.0,
        "details": "cart lines (productId, qty) == %r (want exactly %r)" % (got, want),
    }]
'''

WISH_BODY = '''
COMPONENT = "wishlist_now_exactly_expected"
COMPONENT_WEIGHTS = {COMPONENT: 1.0}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

# Every productId the wish list must hold when the episode ends. The wish list
# boots empty (src/data/wishlist.json is {"items": []}), so this collection is
# exactly the set the stated price band returns.
EXPECTED_PRODUCT_IDS = json.loads(r"""__EXPECTED__""")


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _wishlist_ids(state):
    """Sorted productIds on the wish list.

    Quantity is not read: `addToWishlist` from a tile stores qty 1 while the PDP
    passes the qty box through (ProductPage.jsx:811), and the instruction says
    nothing about how many of each. Membership is what the retrieval determines.
    """
    ids = []
    for item in _list(_dict(_dict(state).get("wishlist")).get("items")):
        if not isinstance(item, dict):
            continue
        ids.append(_int(item.get("productId")))
    return sorted(ids, key=lambda pid: (pid is None, pid))


def score_state(state):
    """The exact resulting wish-list collection, and nothing else.

    Missing one of the two matched products, carrying a near-miss from the
    neighbouring price bucket, or leaving the wish list empty all score 0.0.
    """
    want = sorted(_int(pid) for pid in EXPECTED_PRODUCT_IDS)
    got = _wishlist_ids(state)
    ok = bool(got == want)
    return [{
        "name": COMPONENT,
        "score": COMPONENT_WEIGHTS[COMPONENT] if ok else 0.0,
        "details": "wishlist productIds == %r (want exactly %r)" % (got, want),
    }]
'''

TAIL_LOCAL = '''

def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    app = apps.get("shopping")
    if not isinstance(app, dict):
        app = apps.get("webarena_shopping_mock")
    if not isinstance(app, dict):
        for value in apps.values():
            if isinstance(value, dict) and "current_state" in value:
                app = value
                break
    state = _dict(_dict(app).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

TAIL_NEMO = '''

def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''


def doc(task, nemo):
    surface = "cart" if task["target"] == "cart" else "wish list"
    lines = [
        '"""',
        "Deterministic reward for %s." % task["task_id"],
        "",
        "Two skills (R3 -> A4), so this task is medium: one enumeration of the set a",
        "stated price band returns inside one category, feeding one add-every-match",
        "action on the %s." % surface,
        "",
        "The whole rubric is the exact resulting %s collection, so an agent that" % surface,
        "guessed, that added only one of the matched products, or that picked up a",
        "neighbouring price bucket scores exactly 0.0 -- and so does an untouched",
        "session.",
        "",
        "Margin: " + task["margin"],
        "",
        "Reads current_state only.",
        "",
        ("Reads GET /go?sid=... and prints REWARD: <float> on every output path."
         if nemo else
         "Reads the frozen evidence bundle handed to evaluate()."),
        '"""',
        "",
    ]
    return "\n".join(lines)


def reward_source(task, nemo):
    if task["target"] == "cart":
        expected = json.dumps(
            [{"productId": pid, "qty": qty} for pid, qty in
             sorted(SEED_CART + [(pid, 1) for pid, _n, _p in task["matched"]])],
            indent=2)
        body = CART_BODY.replace("__EXPECTED__", expected)
    else:
        expected = json.dumps(sorted(pid for pid, _n, _p in task["matched"]))
        body = WISH_BODY.replace("__EXPECTED__", expected)

    head = doc(task, nemo)
    if nemo:
        head += (
            "import json\n"
            "import sys\n"
            "\n"
            "import requests\n"
            "\n"
            'SID = "__CUA_GYM_SID__"\n'
            'BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n'
        )
    else:
        head += "import json\n"
    return head + body + (TAIL_NEMO if nemo else TAIL_LOCAL)


# --------------------------------------------------------------------------- #
# replay draft                                                                 #
# --------------------------------------------------------------------------- #

def replay_source(task):
    surface = "shopping cart" if task["target"] == "cart" else "wish list"
    trail = task["cat_trail"]
    steps = []
    for name in trail:
        steps.append('    page.get_by_role("link", name=%r, exact=True).first.click()\n'
                     '    page.wait_for_load_state("networkidle")' % name)
    nav = "\n".join(steps)

    if task["target"] == "cart":
        if task["options_free"]:
            act = (
                '    # every match is option-free, so the tile button adds directly\n'
                '    count = page.locator("li.product-item").count()\n'
                '    for index in range(count):\n'
                '        page.locator("li.product-item").nth(index).hover()\n'
                '        page.locator("li.product-item").nth(index).get_by_role(\n'
                '            "button", name="Add to Cart").first.click()\n'
                '        page.wait_for_load_state("networkidle")')
        else:
            act = (
                '    # at least one match carries a required option, so the tile button\n'
                '    # navigates to the PDP (ProductGrid.jsx:63-66); go through the PDP\n'
                '    # for every row, choose the first value of each required option and\n'
                '    # add at the default quantity of 1.\n'
                '    for index in range(page.locator("li.product-item").count()):\n'
                '        page.locator("li.product-item a.product-item-link").nth(index).click()\n'
                '        page.wait_for_load_state("networkidle")\n'
                '        for sel in page.locator(".product-options-wrapper select").all():\n'
                '            sel.select_option(index=1)\n'
                '        page.get_by_role("button", name="Add to Cart").first.click()\n'
                '        page.wait_for_load_state("networkidle")\n'
                '        page.go_back()\n'
                '        page.wait_for_load_state("networkidle")')
    else:
        act = (
            '    # the tile heart works whether or not the product has options\n'
            '    for index in range(page.locator("li.product-item").count()):\n'
            '        page.locator("li.product-item a.action.towishlist").nth(index).click()\n'
            '        page.wait_for_load_state("networkidle")')

    extra = ""
    if task["n"] == 10:
        extra = (
            '\n    # the $140 threshold is not a bucket: the "$100.00 and above"\n'
            '    # facet returns three rows and the $119.99 one must be skipped, so\n'
            '    # the loop above is replaced by two explicit tile clicks.\n')
        act = (
            '    for name in ("Purple Ultimate Seat Cushion", "Leather Moroccan Pouf"):\n'
            '        row = page.locator("li.product-item", has_text=name).first\n'
            '        row.locator("a.action.towishlist").first.click()\n'
            '        page.wait_for_load_state("networkidle")')

    return (
        "# Golden replay DRAFT for %s.\n"
        "# Not executed during authoring. Clicks only -- no typed URLs.\n"
        "# Retrieval: nav band -> %s -> Shopping Options > Price > %s\n"
        "# Writeback: %s\n"
        "# Expected matches: %s\n"
        "\n"
        "def run(page, base):\n"
        "    page.goto(base + \"/\")\n"
        "%s\n"
        "    page.locator(\"#narrow-by-list a:has-text(%r)\").first.click()\n"
        "    page.wait_for_load_state(\"networkidle\")\n"
        "%s%s\n"
    ) % (
        task["task_id"],
        " > ".join(trail),
        task["facet_label"],
        surface,
        ", ".join("%d (%s)" % (pid, name) for pid, name, _p in task["matched"]),
        nav,
        task["facet_label"],
        extra,
        act,
    )


# --------------------------------------------------------------------------- #
# bundle writer                                                                #
# --------------------------------------------------------------------------- #

def success_criteria(task):
    ids = sorted(pid for pid, _n, _p in task["matched"])
    if task["target"] == "cart":
        lines = sorted(SEED_CART + [(pid, 1) for pid in ids])
        return [
            "current_state.cart.items is exactly %d lines, one per product, with "
            "(productId, qty) == %s." % (len(lines), lines),
            "The two products the %s price band returns in %s are productIds %s; "
            "both are present at qty 1."
            % (task["facet_label"], task["cat_trail"][-1], ids),
            "An untouched session scores 0.0: the seeded cart holds only the three "
            "lines 554/555/556 (productIds 15033, 15787, 10617).",
            "Adding a product outside the band, missing one match, or altering a "
            "seeded line's quantity scores 0.0.",
        ]
    return [
        "current_state.wishlist.items holds exactly the productIds %s, one entry "
        "each." % ids,
        "Those are the two products the %s price band returns in %s."
        % (task["facet_label"], task["cat_trail"][-1]),
        "An untouched session scores 0.0: the wish list boots empty.",
        "Any extra product on the wish list, including the neighbouring price "
        "bucket's near-miss, scores 0.0.",
    ]


def notes(task):
    ids = sorted(pid for pid, _n, _p in task["matched"])
    out = [
        "Cell verified by enumerating src/data/products.json under isListable() "
        "(status==1 && visibility>=4 && inStock) over descendantIds(%s): the band "
        "returns exactly 2 rows, productIds %s." % (task["cat_trail"][-1], ids),
        "Margin: " + task["margin"],
        "The captured Price facet on %s.html advertises the same count the seeded "
        "pool produces for every bucket in this category, so the sidebar number "
        "and the rendered grid agree." % task["cat_path"],
        "Price filter semantics are half-open, v >= from && v < to "
        "(catalog.js:1167-1173); the band boundaries above were checked against "
        "that, not against a closed reading.",
        "The filtered URL has no exact captured listing, so resolveListing falls "
        "through to pool.slice() and both matches render on page 1 at every "
        "allowed page size (12/24/36) -- CORRECTIONS #58's capture/pool gap "
        "cannot apply.",
        "No initial_setup: the pristine seed already carries the retrieval and "
        "every plausible injection would have placed a member of the asserted "
        "collection into the initial state.",
    ]
    if task["target"] == "cart":
        out.append(
            "addToCart merges by productId + optionTypeId set (AppContext.jsx:"
            "251-281). None of the matched products is one of the three seeded "
            "cart products, so the correct end state is five lines at qty 1, not "
            "a merged three.")
        if task["options_free"]:
            out.append(
                "Neither match carries a required custom option, so the tile Add "
                "to Cart button adds directly instead of navigating to the PDP "
                "(ProductGrid.jsx:63-66), and both stored lines have options == [].")
        else:
            out.append(
                "At least one match carries a required custom option, so its tile "
                "Add to Cart navigates to the PDP (ProductGrid.jsx:63-66). The "
                "rubric grades productId and qty only, because the chosen option "
                "value is not determined by the instruction.")
    else:
        out.append(
            "addToWishlist is idempotent on productId (AppContext.jsx:324-346), so "
            "a double click cannot produce a duplicate row and the rubric's exact "
            "collection is stable.")
    if task["n"] == 10:
        out.append(
            "This is the lane's one non-bucket band: the sidebar's widest cell is "
            "'$100.00 and above' (3 rows) and the $140 threshold drops id 32183 at "
            "$119.99. An agent that clicks the facet and stops scores 0.0.")
    return out


def build(task):
    task["task_id"] = "price_cell_pair_to_cart_%s_%03d" % (task["slug"], task["n"])
    bundle = os.path.join(ROOT, task["task_id"])
    os.makedirs(bundle, exist_ok=True)

    surface = "the shopping cart" if task["target"] == "cart" else "the wish list"

    instruction = task["instruction"]

    ti = {
        "task_id": task["task_id"],
        "task_instruction": instruction,
        "app_dir": APP,
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": success_criteria(task),
    }

    manifest = {
        "schema_version": 2,
        "task_id": task["task_id"],
        "instruction": instruction,
        "apps": [{
            "name": APP,
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
        "metadata": {
            "style": task["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R3", "A4"],
            "skill_chain": SKILL_CHAIN % surface,
            "derived_from": None,
            "official_analogues": task["analogues"],
            "injected_preconditions": [],
            "hard_criteria": [],
            "topic": "shopping enumerate a price-band cell, then add every match "
                     "to a collection",
            "lane": "price_cell_pair_to_cart",
            "batch": "batch6",
            "inspiration_ids": task["inspiration_ids"],
            "authoring_notes": notes(task),
        },
    }

    with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
        json.dump(ti, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(bundle, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(bundle, "reward.py"), "w") as fh:
        fh.write(reward_source(task, nemo=False))
    nemo_reward = reward_source(task, nemo=True)
    with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
        fh.write(nemo_reward)

    row = {"task_payload": {
        "task_id": task["task_id"],
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP],
        "start_urls": [],
        "intent": instruction,
        "eval": {
            "eval_types": ["string_match"],
            "reference_answers": None,
            "note": "unused - CUA-Gym reward code is authoritative",
        },
        "cuagym": {
            "bundle_id": task["task_id"],
            "app_dir": APP,
            "initial_setup": None,
            "eval_reward_code": nemo_reward,
        },
    }}
    with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2)
        fh.write("\n")

    os.makedirs(REPLAYS, exist_ok=True)
    with open(os.path.join(REPLAYS, task["task_id"] + ".py"), "w") as fh:
        fh.write(replay_source(task))
    return row


INSPIRATION = {
    "cart": ["webarena-506", "webarena-507", "webarena-508", "webarena-124", "webarena-226"],
    "wishlist": ["webarena-465", "webarena-467", "webarena-511", "webarena-126", "webarena-229"],
}


def main():
    os.makedirs(BATCH, exist_ok=True)
    rows = []
    for task in TASKS:
        task["inspiration_ids"] = INSPIRATION[task["target"]]
        rows.append(build(task))
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    index = {"schema_version": 2,
             "tasks": [{"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]}
                       for t in TASKS]}
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    for task in TASKS:
        words = len(task["instruction"].split())
        print("%-58s %-8s %-8s %d words" % (task["task_id"], task["style"],
                                            task["target"], words))


if __name__ == "__main__":
    main()
