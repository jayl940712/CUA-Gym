"""Batch-6 lane 44 generator — shopping / R1 -> A7.

Chain: identify the single best-rated (>=5 reviews) or cheapest item under a
stated filter, then record a figure taken from that item (its price, its rating
percentage or its SKU) in the comment on a pre-seeded wish-list row.

The wish-list row is injected by initial_setup.py, which is what keeps the task
at EXACTLY two skills: the agent never adds anything to the wish list (that
would be A4), it only retrieves (R1) and writes the note (A7).

Ground truth was computed by scripts/_b6_lane44_analyze.py, which reimplements
resolveListing()/priceFacets() from
hub/websites/webarena_shopping_mock/src/utils/catalog.js against src/data/.

Writes:
  output/tasks/shopping/<task_id>/{task_instruction.json,task.json,reward.py,
                                   nemo_reward.py,nemo_task.json,initial_setup.py}
  output/tasks/shopping/_batches/flagship_price_survey_note/{GENERATION.md,
                                   index.json,nemo_tasks.jsonl,replays/*.py}
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/flagship_price_survey_note")

MARKET_SURVEY_PS4 = (
    "I am doing a market survey for one stop market, go to the product page "
    "for the most expensive PS4 accessories"
)
MARKET_SURVEY_SKIN = (
    "I am doing a market survey for one stop market, go to the product page "
    "for the most expensive skin care"
)
MARKET_SURVEY_HOUSE = (
    "I am doing a market survey for one stop market, go to the product page "
    "for the most expensive Household Supplies"
)
BEST_RATING_SHOE = (
    'Buy the best rating product from "Men"s shoe" category with at least 5 '
    "reviews and the product is least expensive. Choose any available variant."
)
BEST_RATING_SPEAKER = (
    'Buy the best rating product from "Home Audio Speaker" category with at '
    "least 5 reviews and the product is least expensive. Choose any available "
    "variant."
)
ADD_CHAIR = "Add a chair to my wish list."

# --------------------------------------------------------------------------
# The ten tasks.
#
# kind      : "money" | "percent" | "sku"  -- how the written figure is parsed
# seed      : the wish-list row injected by initial_setup.py (never the answer)
# target    : the derived product; NEVER named in the instruction
# --------------------------------------------------------------------------
TASKS = [
    dict(
        num="001",
        slug="cakes_top_rated_price",
        style="terse",
        kind="money",
        instruction=(
            "My wish list has a Sclafani Panettone Cake. In the Cakes category, "
            "find the best-rated product with at least 5 reviews, then set that "
            "row's comment to its price alone, formatted like $12.34."
        ),
        category="Cakes",
        nav="Grocery & Gourmet Food > Breads & Bakery > Cakes",
        path="/grocery-gourmet-food/breads-bakery/cakes.html",
        seed=dict(pid=102040, sku="B004J4LZL6", price=24.95, qty=1, note="",
                  name="Sclafani Panettone Cake in 2 lb. Box",
                  label="Sclafani Panettone Cake"),
        target=dict(pid=48759, rating=100, reviews=10, price=59.95,
                    sku="B07WMZHGYT",
                    name='Junior\'s Cheesecake 8" Raspberry Swirl Cheesecake (Serves 12-14)'),
        expected="$59.95",
        derivation=(
            "Cakes (category 292) holds 69 listable products. 27 of them carry "
            "5 or more reviews; the highest rating among those is 100% "
            "(product 48759, 10 reviews) against a runner-up of 95% (product "
            "22742) - a 5-point margin and no tie at rank 1. Its price is "
            "$59.95."
        ),
        gate_note=(
            "The >=5-review gate is load-bearing: products 102267 and 79140 "
            "also rate 100% on a single review each and would win without it. "
            "Both surfaces agree on their count (reviewCounts.json 1, "
            "products[].reviewsCount 1)."
        ),
        reach=("48759 renders on page 3 of the default (position) sort at 12 "
               "per page, page 1 at 36 per page, and page 1 under price "
               "descending; /grocery-gourmet-food/breads-bakery/cakes.html has "
               "no captured listing carrying product_list_order, so a price "
               "sort takes the derived-pool branch of resolveListing()."),
        analogues=[BEST_RATING_SHOE, ADD_CHAIR],
    ),
    dict(
        num="002",
        slug="flip_cases_top_rated_rating",
        style="terse",
        kind="percent",
        instruction=(
            "The comment on my FYY Leather Case with Mirror wish-list row is out "
            "of date. Replace it with the rating of the best-rated Flip Cases "
            "product that has at least 5 reviews - just the percentage, like 45%."
        ),
        category="Flip Cases",
        nav="Cell Phones & Accessories > Cases, Holsters & Sleeves > Flip Cases",
        path="/cell-phones-accessories/cases-holsters-sleeves/flip-cases.html",
        seed=dict(pid=39123, sku="B07GVMG4ZZ", price=18.99, qty=1,
                  note="check the price again before ordering",
                  name=("FYY Leather Case with Mirror for iPhone 6S Plus/iPhone 6 "
                        "Plus, Leather Wallet Flip Folio Case with Mirror and Wrist "
                        "Strap for iPhone 6S Plus/6 Plus Black"),
                  label="FYY Leather Case with Mirror"),
        target=dict(pid=76219, rating=97, reviews=12, price=30.99,
                    sku="B09C1PW8D8",
                    name=("SHIELDON Case for iPhone 13 5G, Genuine Leather Wallet "
                          "Case Magnetic Kickstand RFID Blocking")),
        expected="97%",
        derivation=(
            "Flip Cases (category 232) holds 47 listable products, 26 with 5 or "
            "more reviews. The best-rated of those is product 76219 at 97% over "
            "12 reviews; the runner-up is 93% (product 39429), a 4-point margin "
            "with no tie at rank 1."
        ),
        gate_note=(
            "Load-bearing gate: product 99966 rates 100% on 4 reviews and would "
            "win without it. Its tile count and its PDP Reviews-tab count are "
            "both 4, so the gate reads the same on either surface."
        ),
        reach=("76219 renders on page 3 of the default sort at 12 per page and "
               "page 1 at 36 per page. The only captures for this path are the "
               "unfiltered page 1 and ?p=3, neither of which carries a sort "
               "parameter."),
        analogues=[BEST_RATING_SPEAKER, ADD_CHAIR],
    ),
    dict(
        num="003",
        slug="deli_top_rated_price",
        style="explicit",
        kind="money",
        instruction=(
            "Open Grocery & Gourmet Food > Deli & Prepared Foods > Deli Meats & "
            "Cheeses and look at each product's star rating and review count. "
            "Ignore anything with fewer than 5 reviews. Whichever of the rest "
            "has the highest rating percentage, note what it costs: go to My "
            "Wish List, put that price - and nothing else, formatted like "
            "$12.34 - in the comment box on the VINCENZAS Hot Soppressata row, "
            "and press Update Wish List."
        ),
        category="Deli Meats & Cheeses",
        nav="Grocery & Gourmet Food > Deli & Prepared Foods > Deli Meats & Cheeses",
        path="/grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses.html",
        seed=dict(pid=49513, sku="B078842SQP", price=27.27, qty=1, note="",
                  name="VINCENZAS Hot Soppressata",
                  label="VINCENZAS Hot Soppressata"),
        target=dict(pid=91261, rating=95, reviews=12, price=48.95,
                    sku="B00H4GXO24",
                    name=("Molinari & Sons San Francisco Italian Dry Salami 3lb "
                          "Stick Molded Paper Wrapped")),
        expected="$48.95",
        derivation=(
            "Deli Meats & Cheeses (category 273) holds 36 listable products, 15 "
            "with 5 or more reviews. Best rating among them is 95% (product "
            "91261, 12 reviews) against 85% for the runner-up (product 79091) - "
            "a 10-point margin, the widest in the lane."
        ),
        gate_note=(
            "Load-bearing gate: products 79973 (100%, 3 reviews) and 80083 "
            "(100%, 1 review) outrank the winner and are excluded by it; tile "
            "and PDP counts agree for both."
        ),
        reach=("91261 renders on page 3 of the default sort at 12 per page and "
               "page 1 at 36 per page. The only capture for this path is the "
               "unfiltered page 1."),
        analogues=[BEST_RATING_SHOE, ADD_CHAIR],
    ),
    dict(
        num="004",
        slug="virtual_reality_top_rated_sku",
        style="terse",
        kind="sku",
        instruction=(
            "In Virtual Reality, find the best-rated item with 5 or more reviews "
            "and copy its SKU into the comment on my METORY Adjustable Ear Muffs "
            "wish-list row. Just the SKU code, nothing else."
        ),
        category="Virtual Reality",
        nav="Video Games > PC > Virtual Reality",
        path="/video-games/pc/virtual-reality.html",
        seed=dict(pid=17256, sku="B09SH2PZJ4", price=38.99, qty=1, note="",
                  name=("METORY Adjustable Ear Muffs & METORY Battery Pack for "
                        "Oculus Quest 2"),
                  label="METORY Adjustable Ear Muffs"),
        target=dict(pid=40622, rating=89, reviews=11, price=7.08,
                    sku="B09165PG3J",
                    name=("VR Link Cable 15ft,Compatible for Qculus Quest 2,Fast "
                          "Charging & PC Data Transfer")),
        expected="B09165PG3J",
        derivation=(
            "Virtual Reality (category 247) holds 55 listable products, 10 with "
            "5 or more reviews. Best rating is 89% (product 40622, 11 reviews) "
            "against 83% for the runner-up (product 89347) - a 6-point margin."
        ),
        gate_note=(
            "Load-bearing gate: product 18979 rates 100% on 2 reviews and is "
            "excluded by it. Tile and PDP counts agree."
        ),
        reach=("Virtual Reality has NO captured listing at all, so every page is "
               "a pure pool.slice(); 40622 renders on page 2 of the default sort "
               "at 12 per page and page 1 at 36 per page."),
        analogues=[BEST_RATING_SPEAKER, ADD_CHAIR],
    ),
    dict(
        num="005",
        slug="smartwatch_top_rated_rating",
        style="terse",
        kind="percent",
        instruction=(
            "Smartwatches: which product with at least 5 reviews carries the "
            "highest rating? Put that rating percentage, like 45%, in the "
            "comment on the Disney Boys' Touchscreen Smart Watch row of my wish "
            "list."
        ),
        category="Smartwatches",
        nav="Electronics > Wearable Technology > Smartwatches",
        path="/electronics/wearable-technology/smartwatches.html",
        seed=dict(pid=75958, sku="B07YT7VC43", price=23.99, qty=1, note="",
                  name="Disney Boys' Touchscreen Smart Watch with Plastic Strap",
                  label="Disney Boys' Touchscreen Smart Watch"),
        target=dict(pid=101046, rating=87, reviews=12, price=46.99,
                    sku="B09G2MFBVV",
                    name=("Smart Watch for Android Phones iPhone Compatible IP68 "
                          "Waterproof Smartwatch Touch Screen")),
        expected="87%",
        derivation=(
            "Smartwatches (category 256) holds 56 listable products, 17 with 5 "
            "or more reviews. Best rating is 87% (product 101046, 12 reviews); "
            "runner-up 82% (product 76181) - a 5-point margin."
        ),
        gate_note=(
            "Load-bearing gate: 100813 (100%, 3 reviews), 100171 and 74708 "
            "(100%, 1 review each) and 76866 (95%, 4 reviews) all outrank the "
            "winner and are all excluded by it. Every one of them reports the "
            "same count on the tile and on the Reviews tab."
        ),
        reach=("Smartwatches has NO captured listing at all; 101046 renders on "
               "page 5 of the default sort at 12 per page and page 2 at 36 per "
               "page."),
        analogues=[BEST_RATING_SPEAKER, ADD_CHAIR],
    ),
    dict(
        num="006",
        slug="planters_top_rated_price",
        style="terse",
        kind="money",
        instruction=(
            "Find the best-rated product with at least 5 reviews in Pots, "
            "Planters & Container Accessories and record its price in the "
            "comment on my Honeysuckle Planter wish-list row - the price alone, "
            "like $12.34."
        ),
        category="Pots, Planters & Container Accessories",
        nav="Patio, Lawn & Garden > Gardening & Lawn Care > Pots, Planters & Container Accessories",
        path="/patio-lawn-garden/gardening-lawn-care/pots-planters-container-accessories.html",
        seed=dict(pid=88290, sku="B072VM7YTZ", price=21.45, qty=1, note="",
                  name='Honeysuckle Planter, Patio Pot, 15" Vanilla',
                  label="Honeysuckle Planter"),
        target=dict(pid=16090, rating=100, reviews=10, price=29.99,
                    sku="B08LVQ6PYW",
                    name=("Planters Pots for Plants Indoor - 4+5.5+6.5 Inch "
                          "Ceramic Planters Bonsai Container")),
        expected="$29.99",
        derivation=(
            "Pots, Planters & Container Accessories (category 191) holds 80 "
            "listable products, 38 with 5 or more reviews. Best rating is 100% "
            "(product 16090, 10 reviews) against 97% for the runner-up (product "
            "86314) - a 3-point margin. Its price is $29.99."
        ),
        gate_note=(
            "The gate is DECORATIVE here: no other product in this category "
            "reaches 100% at any review count, so the winner is the same with "
            "or without it. Kept for consistency with the lane and because it "
            "matches the official phrasing; recorded as not load-bearing."
        ),
        reach=("16090 renders on page 1 of the default sort at 12 per page. The "
               "unfiltered page-1 capture for this path contains it, so the "
               "captured and derived branches agree on the first screen."),
        analogues=[BEST_RATING_SHOE, ADD_CHAIR],
    ),
    dict(
        num="007",
        slug="health_care_top_rated_price",
        style="explicit",
        kind="money",
        instruction=(
            "I am comparing what the top-reviewed health items cost. Go to "
            "Health & Household > Health Care, check each product's rating and "
            "its review count, and discard every product with fewer than 5 "
            "reviews. Take the highest-rated one that is left and read its "
            "price. Then open My Wish List, type that price - just the amount, "
            "formatted like $12.34 - into the comment box on the Spenco Men's "
            "Tribal Elite Sandal row, and click Update Wish List."
        ),
        category="Health Care",
        nav="Health & Household > Health Care",
        path="/health-household/health-care.html",
        seed=dict(pid=15620, sku="B017USSGJQ", price=39.99, qty=1, note="",
                  name="Spenco Men's Tribal Elite Sandal",
                  label="Spenco Men's Tribal Elite Sandal"),
        target=dict(pid=35132, rating=98, reviews=8, price=24.99,
                    sku="B09HRMXKCR",
                    name=("Cocorrína Scented Candle Gift Set for Men "
                          "Fireplace|Wood|Vanilla Scented Aromatherapy Candles")),
        expected="$24.99",
        derivation=(
            "Health Care (category 47) holds 86 listable products, 35 with 5 or "
            "more reviews. Best rating is 98% (product 35132, 8 reviews) against "
            "93% for the runner-up (product 71534) - a 5-point margin."
        ),
        gate_note=(
            "Load-bearing gate: products 98731 and 36976 both rate 100% on a "
            "single review and are excluded by it; tile and PDP counts agree "
            "for both."
        ),
        reach=("35132 renders on page 1 of the default sort at 12 per page - it "
               "is inside this path's captured page-1 listing - and on page 2 at "
               "36 per page."),
        analogues=[BEST_RATING_SHOE, MARKET_SURVEY_SKIN],
    ),
    dict(
        num="008",
        slug="mp3_accessories_top_rated_sku",
        style="terse",
        kind="sku",
        instruction=(
            "MP3 & MP4 Player Accessories: take the best-rated product with at "
            "least 5 reviews and put its SKU, on its own, in the comment on my "
            "Bem HL2331B Band Bluetooth Speaker wish-list row."
        ),
        category="MP3 & MP4 Player Accessories",
        nav="Electronics > Portable Audio & Video > MP3 & MP4 Player Accessories",
        path="/electronics/portable-audio-video/mp3-mp4-player-accessories.html",
        seed=dict(pid=19817, sku="B00KDGBT8S", price=25.61, qty=1, note="",
                  name="Bem HL2331B Band Bluetooth Speaker (Black)",
                  label="Bem HL2331B Band Bluetooth Speaker"),
        target=dict(pid=42180, rating=92, reviews=12, price=57.26,
                    sku="B07LC6VRD6",
                    name=("Bluetooth Car Adapter FM Transmitter, V-Proof Car "
                          "Wireless Radio Transmitter Adapter")),
        expected="B07LC6VRD6",
        derivation=(
            "MP3 & MP4 Player Accessories (category 255) holds 54 listable "
            "products, 21 with 5 or more reviews. Best rating is 92% (product "
            "42180, 12 reviews) against 88% for the runner-up (product 77654) - "
            "a 4-point margin."
        ),
        gate_note=(
            "The gate is DECORATIVE here: no product in the category rates above "
            "92% at any review count, so the winner does not depend on it. "
            "Recorded as not load-bearing."
        ),
        reach=("42180 renders on page 3 of the default sort at 12 per page and "
               "page 1 at 36 per page. This path's only sorted capture is p=3 "
               "with product_list_order=name, which no price or default browse "
               "produces."),
        analogues=[BEST_RATING_SPEAKER, ADD_CHAIR],
    ),
    dict(
        num="009",
        slug="kids_bedding_band_floor_price",
        style="explicit",
        kind="money",
        instruction=(
            "Go to Home & Kitchen > Bedding > Kids' Bedding and use the Shop By "
            "> Price filter for $60.00 - $69.99. Of the items in that band find "
            "the cheapest one and read its price. Then open My Wish List, set "
            "the comment on the Disney Frozen 2 - North Remembers row to that "
            "price alone, formatted like $12.34, and click Update Wish List."
        ),
        category="Kids' Bedding",
        nav="Home & Kitchen > Bedding > Kids' Bedding",
        path="/home-kitchen/bedding/kids-bedding.html?price=60-70",
        seed=dict(pid=69323, sku="B082BTW2YG", price=17.99, qty=1, note="",
                  name=('Disney Frozen 2 - North Remembers Silk Touch Throw '
                        'Blanket, 46" x 60"'),
                  label="Disney Frozen 2 - North Remembers"),
        target=dict(pid=97398, rating=None, reviews=None, price=60.99,
                    sku="B07K9XHC3H",
                    name=("Mi Zone Kids Cozy Comforter Set, Colorful Fun Design "
                          "All Season Children Bedding Girls Bedroom Decor, "
                          "Twin, Tessa White with Colorful Tassel 3 Piece")),
        expected="$60.99",
        derivation=(
            "The $60.00 - $69.99 sidebar cell on Kids' Bedding advertises 7 "
            "items and the seeded pool holds exactly 7 (verified against the "
            "captured facet block, which is what priceFacets() returns here). "
            "Cheapest is $60.99 (product 97398); the next is $62.99 - a $2.00 "
            "margin and a unique minimum. The band's ceiling is $69.99, so the "
            "answer is not the round number an agent could guess from the "
            "label."
        ),
        gate_note=(
            "Price filters are half-open, v >= from && v < to "
            "(catalog.js:1167-1173), so the band is $60.00 up to but excluding "
            "$70.00."
        ),
        reach=("Seven items fit on one page at every page size, so every member "
               "of the cell renders whatever sort the agent uses. The only "
               "captures for the filtered URL carry product_list_order=price "
               "AND product_list_dir=desc; that capture holds all 7 ids, so the "
               "captured and derived branches list the same set."),
        analogues=[MARKET_SURVEY_PS4, ADD_CHAIR],
    ),
    dict(
        num="010",
        slug="table_linens_top_band_floor_price",
        style="terse",
        kind="money",
        instruction=(
            "Kitchen & Table Linens has a $100.00 and above price filter. "
            "Replace the stale comment on my Pimpernel Antique Roses Collection "
            "Placemats wish-list row with the price of the cheapest item in that "
            "band - just the amount, like $12.34."
        ),
        category="Kitchen & Table Linens",
        nav="Home & Kitchen > Kitchen & Dining > Kitchen & Table Linens",
        path="/home-kitchen/kitchen-dining/kitchen-table-linens.html?price=100-200",
        seed=dict(pid=70206, sku="B000RH4NIQ", price=40.00, qty=1,
                  note="ordered these already?",
                  name="Pimpernel Antique Roses Collection Placemats - Set of 4",
                  label="Pimpernel Antique Roses Collection Placemats"),
        target=dict(pid=32183, rating=None, reviews=None, price=119.99,
                    sku="B07QY272R3",
                    name=("NECAUX Custom Multisize 1.5mm Thick Clear PVC Table "
                          "Cover Protector - 60 x 120 Inch Rectangular Vinyl "
                          "Heat Resistant Table Pads")),
        expected="$119.99",
        derivation=(
            "Kitchen & Table Linens shows two price cells, $0.00 - $99.99 (109) "
            "and $100.00 and above (3). The seeded pool reproduces both counts "
            "exactly: 109 and 3. Inside the top cell the prices are $119.99, "
            "$149.00 and $180.00, so the cheapest is $119.99 with a $29.01 "
            "margin and no tie."
        ),
        gate_note=(
            "The $100.00 and above link is ?price=100-200, and no seeded product "
            "in this category is priced at $200.00 or more, so the half-open "
            "upper bound excludes nothing."
        ),
        reach=("Three items fit on one page at every page size and under every "
               "sort, so the cell is fully visible however the agent browses."),
        analogues=[MARKET_SURVEY_HOUSE, ADD_CHAIR],
    ),
]

# --------------------------------------------------------------------------

SETUP_TMPL = '''"""NeMo-Gym setup program for {task_id}.

Seeds the wish list with a single saved row - {seed_label} (product {seed_pid})
- so the episode is exactly two skills: the agent retrieves the derived item and
writes the note, and never has to add anything to the wish list. The comment on
that row is {note_desc}, so the post-setup state scores 0.0 on the rubric.

WishlistPage.jsx renders no textarea and no Update button at all while the list
is empty, so seeding the row is also what makes the writeback control exist.

The pristine session document is read back from GET /go?sid= first and the
patched document is POSTed whole, so no top-level key is dropped whichever way
the state API treats a partial set. The inlined fixture is a raw string
literal, so no escape is eaten by the Python parser before the JSON decoder
sees it.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

WISHLIST_ITEMS = json.loads(r"""
{items_json}
""")


def main():
    read = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    read.raise_for_status()
    payload = read.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not state:
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: no session document to patch", file=sys.stderr)
        raise SystemExit(1)
    state = json.loads(json.dumps(state))
    state["wishlist"] = {{"items": WISHLIST_ITEMS}}
    highest = 0
    for row in WISHLIST_ITEMS:
        if row["wishlistItemId"] > highest:
            highest = row["wishlistItemId"]
    state["nextWishlistItemId"] = highest + 1
    written = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    written.raise_for_status()
    print("SETUP OK")


main()
'''

RUBRIC_TMPL = '''import re
from decimal import Decimal, InvalidOperation

SEED_PRODUCT_ID = {seed_pid}
EXPECTED_KIND = "{kind}"
EXPECTED_TEXT = "{expected}"

_MONEY_RE = re.compile(r"^\\$?\\s*([0-9][0-9,]*\\.[0-9]{{2}})$")
_PERCENT_RE = re.compile(r"^([0-9]{{1,3}})\\s*%(?:\\s*of\\s*100)?$", re.IGNORECASE)
_SKU_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _wishlist_row(state):
    if not isinstance(state, dict):
        return None
    wishlist = state.get("wishlist")
    if not isinstance(wishlist, dict):
        return None
    items = wishlist.get("items")
    if not isinstance(items, list):
        return None
    for row in items:
        if not isinstance(row, dict):
            continue
        try:
            pid = int(row.get("productId"))
        except (TypeError, ValueError):
            continue
        if pid == SEED_PRODUCT_ID:
            return row
    return None


def _note_matches(text):
    """True only when the comment is EXACTLY the derived figure.

    Nothing else on the page carries this value, and the instruction asks for
    the figure alone, so an agent that pasted a whole product name or a range
    scores 0.0 rather than partial credit.
    """
    if not isinstance(text, str):
        return False
    cleaned = " ".join(text.split())
    if not cleaned:
        return False
    if EXPECTED_KIND == "money":
        found = _MONEY_RE.match(cleaned)
        if not found:
            return False
        try:
            written = Decimal(found.group(1).replace(",", ""))
            wanted = Decimal(EXPECTED_TEXT.replace("$", "").replace(",", ""))
        except (InvalidOperation, ValueError):
            return False
        return written == wanted
    if EXPECTED_KIND == "percent":
        found = _PERCENT_RE.match(cleaned)
        if not found:
            return False
        try:
            written = int(found.group(1))
            wanted = int(EXPECTED_TEXT.replace("%", "").strip())
        except (TypeError, ValueError):
            return False
        return written == wanted
    if not _SKU_RE.match(cleaned):
        return False
    return cleaned.upper() == EXPECTED_TEXT.upper()


COMPONENT_WEIGHTS = {{
    "wishlist_note_carries_derived_figure": 1.0,
}}


def _checks(state):
    row = _wishlist_row(state)
    note = row.get("description") if isinstance(row, dict) else None
    return {{
        "wishlist_note_carries_derived_figure": row is not None and _note_matches(note),
    }}
'''

REWARD_TMPL = '''"""Deterministic reward for {task_id}.

Success criterion:
  * the wish-list row for product {seed_pid} ({seed_label}) carries a comment
    that is exactly {expected!r} - {expected_desc}.

{derivation}

Scoring reads current_state only, never a diff against initial_state, so an
empty current_state scores 0.0 and a value that happens to match its pristine
form cannot fabricate a miss. The seeded comment is {note_desc}, so the
post-setup state scores 0.0.

The catalog is static reference data and never enters session state
(dataManager.js createInitialData), so the derived figure cannot move during
the episode.
"""

{rubric}

def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {{}}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state") if isinstance(app.get("current_state"), dict) else {{}}
    checks = _checks(state)
    components = [
        {{
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {{"satisfied": bool(checks.get(name))}},
        }}
        for name in COMPONENT_WEIGHTS
    ]
    return {{
        "score": round(sum(c["score"] for c in components), 6),
        "components": components,
    }}
'''

NEMO_REWARD_TMPL = '''"""NeMo-Gym reward program for {task_id}.

Implements exactly the rubric of reward.py, reading current_state from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import sys

import requests

{rubric}
SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"


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
        payload = response.json()
        state = payload.get("current_state")
        if not isinstance(state, dict):
            state = {{}}
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

REPLAY_TMPL = '''"""Golden replay draft for {task_id}.

Click-only from start_path "/": the nav band renders the whole 301-category
descendant tree in the DOM (Header.jsx:302-345), so {category} is reachable by
clicking; the header carries a "My Wish List" link (Header.jsx:29-32) on every
page. No page.goto after the initial landing, no constructed URL.

Retrieval (R1): {retrieval}
Action (A7): replace the comment on the pre-seeded {seed_label} row and press
Update Wish List - updateAll() (WishlistPage.jsx:43-52) only calls
updateWishlistItem when the draft differs from the stored value.

DRAFT: the derived figure below is the authored ground truth ({expected}).
golden-browser must re-derive it from the rendered listing rather than trusting
this constant.
"""

DERIVED_VALUE = "{expected}"
NAV_TRAIL = {nav!r}
LISTING_PATH = {path!r}


def run(page, base_url):
    page.goto(base_url + "/")

    # 1. Retrieval (R1) - walk the nav band down the trail in NAV_TRAIL and
    #    survey the listing. Raise the page size with the "Show N per page"
    #    limiter (Toolbar.jsx:180-198) rather than typing a ?p= URL, and use
    #    the "Sort By" select plus the direction switcher for price order.
    #    The direction switcher advertises the direction it will switch TO
    #    (Toolbar.jsx:79-82) - never assert on its label.
    for crumb in [part.strip() for part in NAV_TRAIL.split(">")]:
        page.get_by_role("link", name=crumb, exact=True).first.click()
        page.wait_for_load_state("networkidle")

{retrieval_steps}
    # 2. Action (A7) - the wish list already holds the row; the textarea only
    #    exists because initial_setup.py seeded it.
    page.get_by_role("link", name="My Wish List").first.click()
    page.wait_for_load_state("networkidle")

    row = page.locator("li.product-item", has_text={seed_label!r}).first
    box = row.locator("textarea.product-item-comment")
    box.fill("")
    box.fill(DERIVED_VALUE)
    page.get_by_role("button", name="Update Wish List").first.click()
    page.wait_for_load_state("networkidle")
'''

RETRIEVAL_STEPS_RATING = '''    # Survey every tile's rating percentage and review count. Set the limiter
    # to 36 and page through; ignore any product with fewer than 5 reviews and
    # keep the highest rating percentage among the rest.
    page.select_option("#limiter", "36")
    page.wait_for_load_state("networkidle")

'''

RETRIEVAL_STEPS_BAND = '''    # Click the Shop By > Price cell {band!r} in the layered navigation
    # (LayeredNav.jsx:84-128), then read the prices of the few items it lists.
    page.get_by_role("link", name={band!r}).first.click()
    page.wait_for_load_state("networkidle")

'''


def write(path, text):
    with open(path, "w") as handle:
        handle.write(text)


def build():
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index_rows = []
    nemo_rows = []

    for task in TASKS:
        task_id = "flagship_price_survey_note_%s_%s" % (task["slug"], task["num"])
        bundle = os.path.join(OUT, task_id)
        os.makedirs(bundle, exist_ok=True)
        seed = task["seed"]
        target = task["target"]
        note_desc = ("empty" if not seed["note"]
                     else "a stale non-numeric note (%r)" % seed["note"])
        expected_desc = {
            "money": "the price of the derived product, dollar sign and two decimals",
            "percent": "the rating percentage of the derived product",
            "sku": "the SKU of the derived product",
        }[task["kind"]]

        items = [{
            "wishlistItemId": 1,
            "productId": seed["pid"],
            "sku": seed["sku"],
            "name": seed["name"],
            "price": seed["price"],
            "qty": seed["qty"],
            "description": seed["note"],
            "addedAt": "2023-06-01 14:22:05",
        }]
        setup = SETUP_TMPL.format(
            task_id=task_id,
            seed_label=seed["label"],
            seed_pid=seed["pid"],
            note_desc=note_desc,
            items_json=json.dumps(items, indent=1),
        )
        write(os.path.join(bundle, "initial_setup.py"), setup)

        rubric = RUBRIC_TMPL.format(
            seed_pid=seed["pid"], kind=task["kind"], expected=task["expected"])
        write(os.path.join(bundle, "reward.py"), REWARD_TMPL.format(
            task_id=task_id, seed_pid=seed["pid"], seed_label=seed["label"],
            expected=task["expected"], expected_desc=expected_desc,
            derivation=task["derivation"], note_desc=note_desc, rubric=rubric))
        write(os.path.join(bundle, "nemo_reward.py"), NEMO_REWARD_TMPL.format(
            task_id=task_id, rubric=rubric))

        success = [
            ("The wish-list row for product %d (%s) has a comment that is "
             "exactly \"%s\"." % (seed["pid"], seed["label"], task["expected"])),
            ("That figure comes from product %d, %s: %s" % (
                target["pid"], target["name"], task["derivation"])),
        ]
        write(os.path.join(bundle, "task_instruction.json"), json.dumps({
            "task_id": task_id,
            "task_instruction": task["instruction"],
            "app_dir": "webarena_shopping_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success,
        }, indent=2) + "\n")

        manifest = {
            "schema_version": 2,
            "task_id": task_id,
            "instruction": task["instruction"],
            "apps": [{
                "name": "webarena_shopping_mock",
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
                "skills": ["R1", "A7"],
                "skill_chain": (
                    "identify the single %s under a stated filter in %s -> write "
                    "that item's %s into the comment on the pre-seeded wish-list "
                    "row and press Update Wish List" % (
                        ("cheapest item" if target["rating"] is None
                         else "best-rated item with at least 5 reviews"),
                        task["category"],
                        {"money": "price", "percent": "rating percentage",
                         "sku": "SKU"}[task["kind"]])),
                "derived_from": "category_spread_wishlist_note_cakes_priciest_row_002",
                "official_analogues": task["analogues"],
                "topic": "flagship_price_survey_note",
                "batch": "batch-6 lane 44 (shopping / R1 -> A7)",
                "lane": "flagship_price_survey_note",
                "inspiration_ids": ["webarena-509", "webarena-510", "webarena-238",
                                    "webarena-513"],
                "authoring_notes": [
                    task["derivation"],
                    task["gate_note"],
                    "Reachability (CORRECTIONS #58): " + task["reach"],
                    ("The instruction never names the derived product or its "
                     "figure, so an agent that skips the survey cannot fill the "
                     "comment; the single rubric component is the figure itself, "
                     "so a near-miss scores 0.0, not partial credit."),
                ],
                "injected_preconditions": [
                    ("Seeds wishlist.items with one row - product %d, %s, "
                     "wishlistItemId 1, description %s - and sets "
                     "nextWishlistItemId to 2. Without it the wish list is empty "
                     "and WishlistPage.jsx renders no comment textarea at all, "
                     "so the A7 control would not exist; with it the task is "
                     "exactly two skills, because the agent never adds anything "
                     "to the list. The seeded comment does not contain the "
                     "derived figure, so the post-setup state scores 0.0."
                     % (seed["pid"], seed["name"],
                        "empty" if not seed["note"] else repr(seed["note"]))),
                ],
            },
        }
        write(os.path.join(bundle, "task.json"), json.dumps(manifest, indent=2) + "\n")

        nemo_row = {"task_payload": {
            "task_id": task_id,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_shopping_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task_id,
                "app_dir": "webarena_shopping_mock",
                "initial_setup": setup,
                "eval_reward_code": open(
                    os.path.join(bundle, "nemo_reward.py")).read(),
            },
        }}
        write(os.path.join(bundle, "nemo_task.json"),
              json.dumps(nemo_row, indent=2) + "\n")
        nemo_rows.append(json.dumps(nemo_row))
        index_rows.append({"task_id": task_id, "path": "%s/task.json" % task_id})

        if target["rating"] is None:
            band = ("$60.00 - $69.99" if "kids" in task["slug"]
                    else "$100.00 and above")
            steps = RETRIEVAL_STEPS_BAND.format(band=band)
            retrieval = ("apply the %s price cell, then take the cheapest of the "
                         "items it lists." % band)
        else:
            steps = RETRIEVAL_STEPS_RATING
            retrieval = ("page through the category, discard every product with "
                         "fewer than 5 reviews and take the highest rating "
                         "percentage among the rest.")
        write(os.path.join(BATCH, "replays", task_id + ".py"), REPLAY_TMPL.format(
            task_id=task_id, category=task["category"], retrieval=retrieval,
            seed_label=seed["label"], expected=task["expected"],
            nav=task["nav"], path=task["path"], retrieval_steps=steps))

    write(os.path.join(BATCH, "index.json"), json.dumps(
        {"schema_version": 2, "tasks": index_rows}, indent=2) + "\n")
    write(os.path.join(BATCH, "nemo_tasks.jsonl"), "\n".join(nemo_rows) + "\n")
    print("wrote %d bundles" % len(TASKS))


build()
