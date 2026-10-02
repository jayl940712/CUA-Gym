#!/usr/bin/env python3
"""Batch-6 lane 31 generator: shopping, R5 -> A10 (category listing -> checkout).

Writes ten schema-v2 bundles under output/tasks/shopping/<task_id>/ plus the
lane's GENERATION.md and golden-replay drafts. Kept OUTSIDE the batch directory
on purpose (two reddit lanes lost their generators to a bulk delete).

Every task is medium and declares exactly two skills: R5 (faceted category
navigation) feeding A10 (place the order). The target product is always derived
from a price ordering the agent has to produce on the category page; it is never
named in the instruction.

All entity facts below were measured against
hub/websites/webarena_shopping_mock/src/data/{products,categories,productOptions}.json
with catalog.js's own isListable()/finalPrice() rules, and the price sort
tie-break (id ascending, catalog.js:1104).
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output", "tasks", "shopping")
BATCH = os.path.join(OUT, "_batches", "category_winner_checkout")
REPLAYS = os.path.join(BATCH, "replays")

SEEDED_CART = [
    {"productId": 15033, "sku": "B087QSCXGT", "qty": 1, "price": 250.8},
    {"productId": 15787, "sku": "B08JLHHCM6", "qty": 1, "price": 40.99},
    {"productId": 10617, "sku": "B09LQTV3RX", "qty": 1, "price": 58.63},
]

ANALOGUE_MEAT = ("Buy the highest rated product from the meat substitute category "
                 "within a budget between 100 and 200. Discard any items in your cart "
                 "if it is not empty.")
ANALOGUE_CEILING = ("Buy the highest rated product from the Ceiling light category "
                    "within a budget above 1000. Discard any items in your cart if it "
                    "is not empty.")
ANALOGUE_NS = ("Buy the highest rated product from the NS switch category within a "
               "budget under 60. Discard any items in your cart if it is not empty.")
ANALOGUE_BEAUTY = ("Buy the highest rated product from the Beauty & Personal Care "
                   "category within a budget under 20. Discard any items in your cart "
                   "if it is not empty.")
ANALOGUE_MEN = ("Buy the highest rated product from the Men clothing category within "
                "a budget above 50 but under 129.99. Discard any items in your cart if "
                "it is not empty.")

TASKS = [
    {
        "id": "category_winner_checkout_cheapest_deli_meat_001",
        "derived_phrase": 'cheapest listed product',
        "style": "terse",
        "instruction": ("Buy the cheapest item One Stop Market lists in its Deli Meats & "
                        "Cheeses category and take it all the way through checkout."),
        "category": "Deli Meats & Cheeses",
        "cat_id": 273,
        "url_path": "grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses",
        "nav": ["Grocery & Gourmet Food", "Deli & Prepared Foods", "Deli Meats & Cheeses"],
        "pool": 36,
        "target": {"productId": 47533, "sku": "B091FZR71C", "qty": 1, "price": 6.51,
                   "name": "Coppa Capicola- SLICED 3 packages"},
        "link_text": "Coppa Capicola",
        "runner_up": "id 11704-class runner-up at $11.67",
        "margin": "$5.16 (next cheapest in the category is $11.67)",
        "order": "asc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_MEAT, ANALOGUE_BEAUTY],
        "inspiration": ["webarena-506", "webarena-792"],
        "derived_from": "clear_cart_then_buy_top_rated_deli_007",
        "notes": [
            "Deli Meats & Cheeses (category 273) is fully seeded: 36 listable products "
            "== categories.json dbProductCount 36, so the price ordering the grid shows "
            "is the ordering a human would compute on the real page.",
            "Winner id 47533 at $6.51; the runner-up is $11.67, a $5.16 margin, and no "
            "other listable product in the category shares $6.51.",
            "Batch 5's deli task derived the RATING superlative; this one derives the "
            "price minimum and grades a single-line order instead of a cleared cart.",
        ],
    },
    {
        "id": "category_winner_checkout_budget_desk_chair_002",
        "derived_phrase": 'cheapest listed product',
        "style": "terse",
        "instruction": ("I need a desk chair and I am broke. Order the least expensive "
                        "product in the Chairs & Sofas category and put the order through."),
        "category": "Chairs & Sofas",
        "cat_id": 183,
        "url_path": "office-products/office-furniture-lighting/chairs-sofas",
        "nav": ["Office Products", "Office Furniture & Lighting", "Chairs & Sofas"],
        "pool": 63,
        "target": {"productId": 32684, "sku": "B07ZNNJW9S", "qty": 1, "price": 25.21,
                   "name": "KaiMeng Ribbed Office Desk Mid Back Computer Chair Height "
                           "Adjustable Conference Executive Task Swivel PU Leather (Grey)"},
        "link_text": "KaiMeng Ribbed Office Desk Mid Back Computer Chair",
        "margin": "$11.78 (next cheapest is $36.99)",
        "order": "asc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_CEILING, ANALOGUE_MEN],
        "inspiration": ["webarena-507", "webarena-793"],
        "derived_from": None,
        "notes": [
            "Chairs & Sofas (183) is fully seeded: 63 listable == dbProductCount 63.",
            "Winner id 32684 at $25.21 against a $36.99 runner-up; no tie at $25.21.",
            "CORRECTIONS #58 applies to this category under the DEFAULT sort (4 of 63 "
            "rows render on no page at 12/page). The instruction implies a price "
            "ordering, and a sorted category URL has no captured listing, so "
            "resolveListing() falls through to pool.slice() and the winner is tile 1.",
        ],
    },
    {
        "id": "category_winner_checkout_dearest_nintendo_system_003",
        "derived_phrase": 'most expensive listed product',
        "style": "terse",
        "instruction": ("Order the most expensive product in the Nintendo Systems "
                        "category and complete the checkout for it."),
        "category": "Nintendo Systems",
        "cat_id": 233,
        "url_path": "video-games/legacy-systems/nintendo-systems",
        "nav": ["Video Games", "Legacy Systems", "Nintendo Systems"],
        "pool": 48,
        "target": {"productId": 74818, "sku": "B085B9Q33S", "qty": 1, "price": 189.99,
                   "name": "Nintendo 2DS - Scarlet Red / White (Renewed)"},
        "link_text": "Nintendo 2DS - Scarlet Red",
        "margin": "$33.14 (next dearest is $156.85)",
        "order": "desc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_NS, ANALOGUE_CEILING],
        "inspiration": ["webarena-508", "webarena-507"],
        "derived_from": None,
        "notes": [
            "Nintendo Systems (233) is fully seeded: 48 listable == dbProductCount 48.",
            "Winner id 74818 at $189.99 against $156.85; no tie.",
            "The category's rating superlative is a verified TIE (89115/89401 at 100%), "
            "which is why the derived property here is price, not rating.",
        ],
    },
    {
        "id": "category_winner_checkout_dearest_switch_bundle_004",
        "derived_phrase": 'most expensive listed product',
        "style": "terse",
        "instruction": ("Splurge for me: buy the priciest thing One Stop Market sells in "
                        "the Nintendo Switch category and place the order."),
        "category": "Nintendo Switch",
        "cat_id": 71,
        "url_path": "video-games/nintendo-switch",
        "nav": ["Video Games", "Nintendo Switch"],
        "pool": 51,
        "target": {"productId": 101755, "sku": "B09MJQ8428", "qty": 1, "price": 189.0,
                   "name": "Nintendo 2020 Newest - Mario Kart Live: Home Circuit - Mario "
                           "Set Edition - Holiday Family Gaming Bundle for Nintendo "
                           "Switch, Nintendo Switch Lite - RED (Renewed)"},
        "link_text": "Mario Kart Live: Home Circuit",
        "margin": "$49.05 (next dearest is $139.95)",
        "order": "desc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_NS, ANALOGUE_MEAT],
        "inspiration": ["webarena-508", "webarena-506"],
        "derived_from": None,
        "notes": [
            "Nintendo Switch (71) is fully seeded: 51 listable == dbProductCount 51.",
            "Winner id 101755 at $189.00 against $139.95; no tie.",
            "The category carries several captured price-facet URLs but none with a sort "
            "parameter, so a price-sorted page is derived from the seed pool.",
        ],
    },
    {
        "id": "category_winner_checkout_cheapest_patio_line_005",
        "derived_phrase": 'cheapest listed product',
        "style": "terse",
        "instruction": ("Order the cheapest product in the Patio Furniture & Accessories "
                        "category and carry it through to a placed order."),
        "category": "Patio Furniture & Accessories",
        "cat_id": 50,
        "url_path": "patio-lawn-garden/patio-furniture-accessories",
        "nav": ["Patio, Lawn & Garden", "Patio Furniture & Accessories"],
        "pool": 92,
        "target": {"productId": 34421, "sku": "B08MQMB5GD", "qty": 1, "price": 17.99,
                   "name": "Synthetic Rattan Woven Material, Plastic Rattan Furniture for "
                           "Weaving and Repairing Tables and Chairs, Storage Basket, Ect "
                           "(500 G)"},
        "link_text": "Synthetic Rattan Woven Material",
        "margin": "$5.94 (next cheapest is $23.93)",
        "order": "asc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_BEAUTY, ANALOGUE_MEN],
        "inspiration": ["webarena-792", "webarena-793"],
        "derived_from": None,
        "notes": [
            "Patio Furniture & Accessories (50) is fully seeded: 92 listable == "
            "dbProductCount 92. CORRECTIONS #63: the rendered nav label is the full "
            "'Patio Furniture & Accessories', not the census's abbreviation.",
            "Winner id 34421 at $17.99 against $23.93; no tie.",
        ],
    },
    {
        "id": "category_winner_checkout_cheapest_flip_case_006",
        "derived_phrase": 'cheapest listed product',
        "style": "terse",
        "instruction": ("Buy the cheapest case in the Flip Cases category and finish the "
                        "checkout so the order is placed."),
        "category": "Flip Cases",
        "cat_id": 232,
        "url_path": "cell-phones-accessories/cases-holsters-sleeves/flip-cases",
        "nav": ["Cell Phones & Accessories", "Cases, Holsters & Sleeves", "Flip Cases"],
        "pool": 47,
        "target": {"productId": 76561, "sku": "B087314JM4", "qty": 1, "price": 6.99,
                   "name": "Asuwish Compatible with iPhone Xs X 10 10s Wallet Case "
                           "Tempered Glass Screen Protector Leather Flip Cover Card "
                           "Holder Phone Cases"},
        "link_text": "Asuwish Compatible with iPhone Xs X 10 10s Wallet Case",
        "margin": "$3.00 (next cheapest is $9.99)",
        "order": "asc",
        "position": 1,
        "clear_cart": True,
        "analogues": [ANALOGUE_BEAUTY, ANALOGUE_NS],
        "inspiration": ["webarena-792", "webarena-508"],
        "derived_from": None,
        "notes": [
            "Flip Cases (232) is fully seeded: 47 listable == dbProductCount 47.",
            "Winner id 76561 at $6.99 against $9.99. The category's MAXIMUM is a 4-cent "
            "margin ($59.99 vs $59.95), so only the minimum is usable here.",
        ],
    },
    {
        "id": "category_winner_checkout_dearest_audio_under_100_007",
        "derived_phrase": 'dearest product still under the $100 ceiling',
        "style": "terse",
        "instruction": ("My budget stops at $100. Order the most expensive MP3 & MP4 "
                        "Player Accessories product that still comes in under $100 and "
                        "place the order."),
        "category": "MP3 & MP4 Player Accessories",
        "cat_id": 255,
        "url_path": "electronics/portable-audio-video/mp3-mp4-player-accessories",
        "nav": ["Electronics", "Portable Audio & Video", "MP3 & MP4 Player Accessories"],
        "pool": 54,
        "target": {"productId": 41839, "sku": "B07ND6TMTX", "qty": 1, "price": 79.95,
                   "name": "MEE audio Matrix Cinema ANC Bluetooth Wireless Active Noise "
                           "Cancelling Headphones with aptX Low Latency, CinemaEAR Audio "
                           "Enhancement, and Active Noise Cancellation"},
        "link_text": "MEE audio Matrix Cinema ANC",
        "margin": ("$20.00 below the winner ($59.95) and $38.35 above it ($118.30 is the "
                   "cheapest product over the ceiling), so the ceiling is unambiguous"),
        "order": "desc",
        "position": 11,
        "clear_cart": True,
        "analogues": [ANALOGUE_MEN, ANALOGUE_NS],
        "inspiration": ["webarena-793", "webarena-508"],
        "derived_from": None,
        "notes": [
            "MP3 & MP4 Player Accessories (255) is fully seeded: 54 listable == "
            "dbProductCount 54.",
            "Winner id 41839 at $79.95; the runner-up under the ceiling is $59.95 and the "
            "cheapest product over it is $118.30, so nothing sits in $79.95-$100.00 and "
            "the answer is stable under either reading of 'under $100'.",
            "The budget is load-bearing: the unconstrained category maximum is id 43382 "
            "at $585.40, so an agent that skips the ceiling buys the wrong product.",
            "The only captured listing with a sort parameter for this category is "
            "?p=3&product_list_order=name, which a price sort never reaches.",
        ],
    },
    {
        "id": "category_winner_checkout_cheapest_plant_over_100_008",
        "derived_phrase": 'cheapest product at or above the $100 floor',
        "style": "terse",
        "instruction": ("A $100 plant voucher has to be used in one go. Order the cheapest "
                        "product in Plants, Seeds & Bulbs that costs $100 or more."),
        "category": "Plants, Seeds & Bulbs",
        "cat_id": 179,
        "url_path": "patio-lawn-garden/gardening-lawn-care/plants-seeds-bulbs",
        "nav": ["Patio, Lawn & Garden", "Gardening & Lawn Care", "Plants, Seeds & Bulbs"],
        "pool": 59,
        "target": {"productId": 14510, "sku": "B06Y28CQPY", "qty": 1, "price": 102.99,
                   "name": "Little GEM Magnolia, Live Plant, Includes Special Blend "
                           "Fertilizer & Planting Guide (4-5 FT)"},
        "link_text": "Little GEM Magnolia",
        "margin": ("$6.98 to the next qualifying product ($109.97); the dearest product "
                   "below the floor is $69.95, so the floor cannot be misread"),
        "order": "desc",
        "position": 3,
        "clear_cart": True,
        "analogues": [ANALOGUE_MEAT, ANALOGUE_CEILING],
        "inspiration": ["webarena-506", "webarena-507"],
        "derived_from": None,
        "notes": [
            "Plants, Seeds & Bulbs (179) is fully seeded: 59 listable == dbProductCount 59.",
            "CORRECTIONS #54: the census flags this category's cheapest product as a "
            "sub-$0.30 margin; it is actually $0.50. This task does not use the category "
            "minimum at all - the derived value is the cheapest product at or above $100.",
            "Winner id 14510 at $102.99, next qualifier $109.97, nearest non-qualifier "
            "$69.95.",
        ],
    },
    {
        "id": "category_winner_checkout_dearest_planter_with_cart_009",
        "derived_phrase": 'most expensive listed product',
        "style": "explicit",
        "instruction": ("My shopping cart already holds three items and I want them to "
                        "ship in the same parcel as one more thing, so please leave the "
                        "existing lines exactly as they are. Work out which product in "
                        "the Pots, Planters & Container Accessories category is the most "
                        "expensive one One Stop Market sells there, add a single unit of "
                        "it to the cart, and then complete the checkout so a real order "
                        "is placed for all four items."),
        "category": "Pots, Planters & Container Accessories",
        "cat_id": 191,
        "url_path": "patio-lawn-garden/gardening-lawn-care/pots-planters-container-accessories",
        "nav": ["Patio, Lawn & Garden", "Gardening & Lawn Care",
                "Pots, Planters & Container Accessories"],
        "pool": 80,
        "target": {"productId": 16457, "sku": "B08KYC8TKK", "qty": 1, "price": 197.52,
                   "name": "26IN Whiskey Barrel Fountain and Planter W/ WT LED"},
        "link_text": "26IN Whiskey Barrel Fountain and Planter",
        "margin": "$13.57 (next dearest is $183.95)",
        "order": "desc",
        "position": 1,
        "clear_cart": False,
        "analogues": [ANALOGUE_CEILING, ANALOGUE_MEAT],
        "inspiration": ["webarena-507", "webarena-506"],
        "derived_from": None,
        "notes": [
            "Pots, Planters & Container Accessories (191) is fully seeded: 80 listable == "
            "dbProductCount 80. CORRECTIONS #63: this is the rendered nav label; the "
            "census abbreviates it to 'Pots & Planters'.",
            "Winner id 16457 at $197.52 against $183.95; no tie.",
            "No initial_setup: the pristine three-line cart (554/555/556) is the "
            "precondition, and placeOrder copies every cart line into the order, so the "
            "graded collection is the three seeded products plus the derived planter.",
            "CORRECTIONS #69: there is no bulk empty-cart control, and this task "
            "deliberately does not ask for one - removing lines would be a third skill.",
        ],
    },
    {
        "id": "category_winner_checkout_cheapest_party_cake_over_100_010",
        "derived_phrase": 'cheapest cake at or above the $100 floor',
        "style": "explicit",
        "instruction": ("There are already three items sitting in my cart and they should "
                        "go out on the same order, so do not take anything out of it. For "
                        "the office party I want one large cake, and the rule is that it "
                        "has to cost at least $100 while still being the cheapest cake in "
                        "the Cakes category that meets that floor. Add one of that cake to "
                        "the cart and place the order for all four items."),
        "category": "Cakes",
        "cat_id": 292,
        "url_path": "grocery-gourmet-food/breads-bakery/cakes",
        "nav": ["Grocery & Gourmet Food", "Breads & Bakery", "Cakes"],
        "pool": 69,
        "target": {"productId": 49382, "sku": "B07Q86P1WR", "qty": 1, "price": 157.99,
                   "name": "Sweet Street Iced Chocolate Thunder 3 Layer Cake 4 lb "
                           "(14 Slice) Pack of 2"},
        "link_text": "Sweet Street Iced Chocolate Thunder",
        "margin": ("$57.18 to the next qualifying cake ($215.17); the dearest cake below "
                   "the floor is $75.90"),
        "order": "desc",
        "position": 3,
        "clear_cart": False,
        "analogues": [ANALOGUE_MEAT, ANALOGUE_MEN],
        "inspiration": ["webarena-506", "webarena-793"],
        "derived_from": "clear_cart_then_buy_top_rated_cake_003",
        "notes": [
            "Cakes (292) is fully seeded: 69 listable == dbProductCount 69.",
            "Winner id 49382 at $157.99; next qualifier $215.17, dearest non-qualifier "
            "$75.90 - a wide band either side of the floor.",
            "Batch 5's cake task derived the rating superlative and cleared the cart; "
            "here the derived property is a price floor and the seeded cart ships with "
            "the order, so the rubric is a four-line collection, not a one-line one.",
            "No initial_setup - the pristine cart is the precondition.",
        ],
    },
]


# --------------------------------------------------------------------------
# templates
# --------------------------------------------------------------------------

REWARD_TEMPLATE = '''"""Deterministic reward for {task_id}.

{blurb}

Scored off the app's current session state only. The untouched session scores
0.0: the seeded order history stops at entity id 189, so no order 000000190
exists until the agent completes a checkout, and an agent that buys the wrong
product places an order whose lines do not match.
"""

import json

SPEC = json.loads(r"""{spec_json}""")

COMPONENT_WEIGHTS = {{
    "order_000000190_placed": 0.3,
    "{lines_component}": 0.7,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

WANT_LINES = sorted(
    (
        int(row["productId"]),
        str(row["sku"]).strip().upper(),
        int(row["qty"]),
        round(float(row["price"]), 2),
    )
    for row in SPEC["expected_lines"]
)


def _as_int(value):
    try:
        return int(float(str(value).strip()))
    except Exception:
        return None


def _num(value):
    try:
        return float(str(value).strip())
    except Exception:
        return None


def _orders(state):
    rows = state.get("orders") if isinstance(state, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _session_orders(state):
    """Orders minted during the episode: the seed stops at entity id 189."""
    out = []
    for row in _orders(state):
        entity = _as_int(row.get("entityId"))
        if entity is not None and entity >= SPEC["first_session_entity_id"]:
            out.append(row)
    return out


def _the_order(state):
    placed = _session_orders(state)
    if len(placed) != 1:
        return None
    order = placed[0]
    if str(order.get("incrementId") or "").strip() != SPEC["increment_id"]:
        return None
    if _as_int(order.get("entityId")) != SPEC["first_session_entity_id"]:
        return None
    return order


def _placed(state):
    return _the_order(state) is not None


def _lines_exact(state):
    order = _the_order(state)
    if order is None:
        return False
    rows = order.get("items")
    if not isinstance(rows, list) or len(rows) != len(WANT_LINES):
        return False
    got = []
    for row in rows:
        if not isinstance(row, dict):
            return False
        pid = _as_int(row.get("productId"))
        qty = _as_int(row.get("qtyOrdered"))
        price = _num(row.get("price"))
        if pid is None or qty is None or price is None:
            return False
        got.append((pid, str(row.get("sku") or "").strip().upper(), qty, round(price, 2)))
    return sorted(got) == WANT_LINES


def score_checks(state):
    return {{
        "order_000000190_placed": _placed(state),
        "{lines_component}": _lines_exact(state),
    }}


def _summary(state):
    placed = _session_orders(state)
    seen = []
    for order in placed:
        for row in order.get("items") or []:
            if isinstance(row, dict):
                seen.append((_as_int(row.get("productId")), _as_int(row.get("qtyOrdered"))))
    return "session_orders=%d ordered_lines=%r expected_lines=%r" % (
        len(placed), sorted(seen, key=lambda v: str(v)), WANT_LINES)


def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    app = None
    if isinstance(apps, dict):
        for candidate_key in ("shopping", "webarena_shopping_mock"):
            candidate = apps.get(candidate_key)
            if isinstance(candidate, dict):
                app = candidate
                break
    state = app.get("current_state") if isinstance(app, dict) else None
    if not isinstance(state, dict):
        state = {{}}

    checks = score_checks(state)
    summary = _summary(state)
    components = []
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        satisfied = bool(checks.get(name))
        earned = COMPONENT_WEIGHTS[name] if satisfied else 0.0
        total += earned
        components.append({{
            "name": name,
            "score": round(earned, 6),
            "details": "component=%s satisfied=%s %s" % (name, satisfied, summary),
        }})
    return {{"score": round(total, 6), "components": components}}
'''


NEMO_REWARD_TEMPLATE = '''"""NeMo-Gym reward program for {task_id}.

Same rubric as reward.py, reading the app's current session state from
GET /go?sid= instead of a frozen evidence bundle, and printing the reward on
every output path including the error path.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

SPEC = json.loads(r"""{spec_json}""")

COMPONENT_WEIGHTS = {{
    "order_000000190_placed": 0.3,
    "{lines_component}": 0.7,
}}

WANT_LINES = sorted(
    (
        int(row["productId"]),
        str(row["sku"]).strip().upper(),
        int(row["qty"]),
        round(float(row["price"]), 2),
    )
    for row in SPEC["expected_lines"]
)


def _as_int(value):
    try:
        return int(float(str(value).strip()))
    except Exception:
        return None


def _num(value):
    try:
        return float(str(value).strip())
    except Exception:
        return None


def _orders(state):
    rows = state.get("orders") if isinstance(state, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _session_orders(state):
    out = []
    for row in _orders(state):
        entity = _as_int(row.get("entityId"))
        if entity is not None and entity >= SPEC["first_session_entity_id"]:
            out.append(row)
    return out


def _the_order(state):
    placed = _session_orders(state)
    if len(placed) != 1:
        return None
    order = placed[0]
    if str(order.get("incrementId") or "").strip() != SPEC["increment_id"]:
        return None
    if _as_int(order.get("entityId")) != SPEC["first_session_entity_id"]:
        return None
    return order


def _placed(state):
    return _the_order(state) is not None


def _lines_exact(state):
    order = _the_order(state)
    if order is None:
        return False
    rows = order.get("items")
    if not isinstance(rows, list) or len(rows) != len(WANT_LINES):
        return False
    got = []
    for row in rows:
        if not isinstance(row, dict):
            return False
        pid = _as_int(row.get("productId"))
        qty = _as_int(row.get("qtyOrdered"))
        price = _num(row.get("price"))
        if pid is None or qty is None or price is None:
            return False
        got.append((pid, str(row.get("sku") or "").strip().upper(), qty, round(price, 2)))
    return sorted(got) == WANT_LINES


def score_checks(state):
    return {{
        "order_000000190_placed": _placed(state),
        "{lines_component}": _lines_exact(state),
    }}


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {{}}
    except Exception as exc:
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    print("COMPONENTS: " + json.dumps(
        {{key: bool(value) for key, value in checks.items()}}, sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''


SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

Empties the seeded shopping cart (quote lines 554 / 555 / 556) so the errand is
exactly one retrieval feeding one checkout: without this the placed order would
also carry a table lamp, a coat rack and a bodysuit, and CORRECTIONS #69 records
that there is no bulk empty-cart control, so asking the agent to clear them
would add a third skill this batch does not allow.

Written as a read-modify-write: GET /go, mutate the whole state document, POST
it back with action "set". Nothing else is touched - orders, addresses, wishlist
and every next* counter are re-posted exactly as read - and an empty cart
pre-satisfies no part of the rubric, which grades the resulting order row.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

FALLBACK_CART = json.loads(r"""{{"quoteId": 255, "items": []}}""")


def _read_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not state:
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not state:
        print("SETUP FAILED: /go returned no usable state document", file=sys.stderr)
        raise SystemExit(1)
    return state


def main():
    state = dict(_read_state())

    orders = state.get("orders")
    if not isinstance(orders, list) or len(orders) < 37:
        print("SETUP FAILED: seeded order history not readable", file=sys.stderr)
        raise SystemExit(1)

    cart = state.get("cart")
    cart = dict(cart) if isinstance(cart, dict) else dict(FALLBACK_CART)
    cart["items"] = []
    state["cart"] = cart

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    current = payload.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: /go returned no current state after set", file=sys.stderr)
        raise SystemExit(1)
    lines = (current.get("cart") or {{}}).get("items")
    if lines != []:
        print("SETUP FAILED: cart is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(current.get("orders"), list) or len(current["orders"]) < 37:
        print("SETUP FAILED: order history lost during set", file=sys.stderr)
        raise SystemExit(1)
    for row in current["orders"]:
        if isinstance(row, dict) and str(row.get("incrementId") or "") == "000000190":
            print("SETUP FAILED: order 000000190 already exists", file=sys.stderr)
            raise SystemExit(1)
    print("SETUP OK")


main()
'''


REPLAY_TEMPLATE = '''"""Golden replay draft for {task_id}.

Click-only after the initial goto of start_path: no page.goto, no URL
construction. The category is reached through the nav band (Header.jsx NavBand
renders the whole descendant tree in the DOM, CSS-hover only), the price
ordering through the toolbar's #sorter select and, where the target is the
maximum, the a[data-role="direction-switcher"] control - never asserted on by
its label, which advertises the direction it would switch TO (Toolbar.jsx:79-82).
The product is opened from its tile link and added from the PDP rather than from
the tile, because a tile Add to Cart silently navigates when a product has
required options (ProductGrid.jsx:63-66); this target has none, but the PDP path
is stable either way.

Expected position after the sort: {position} at 36 per page ({order}ending price).
"""

START_PATH = '/'

NAV = {nav!r}
PRODUCT_LINK_TEXT = {link_text!r}


def _open_category(page):
    for label in NAV:
        page.click('nav.navigation a:has(span:text-is("%s"))' % label)
        page.wait_for_timeout(300)


def _sort_by_price(page):
    page.select_option('#sorter', 'price')
    page.wait_for_timeout(400)
    page.select_option('#limiter', '36')
    page.wait_for_timeout(400)
{direction_click}    page.wait_for_selector('li.product-item')


def _checkout(page):
    page.click('a.action.showcart')
    page.click('button[data-role="proceed-to-checkout"]')
    page.click('button.action.primary.large:has-text("Next")')
    page.click('button.action.primary.checkout:has-text("Place Order")')
    page.wait_for_timeout(800)


def run(page, base_url):
    page.goto(base_url + START_PATH)
    _open_category(page)
    _sort_by_price(page)
    page.click('li.product-item a.product-item-link:has-text("%s")' % PRODUCT_LINK_TEXT)
    page.wait_for_selector('#product-addtocart-button')
    page.click('#product-addtocart-button')
    page.wait_for_timeout(600)
    _checkout(page)
'''


def build(task):
    tid = task["id"]
    bundle = os.path.join(OUT, tid)
    os.makedirs(bundle, exist_ok=True)

    expected = [dict(task["target"])]
    if not task["clear_cart"]:
        expected = [dict(row) for row in SEEDED_CART] + expected
    expected_lines = [
        {"productId": r["productId"], "sku": r["sku"], "qty": r["qty"], "price": r["price"]}
        for r in expected
    ]

    lines_component = ("order_lines_are_exactly_the_derived_product"
                       if task["clear_cart"]
                       else "order_lines_are_exactly_the_four_wanted_products")

    spec = {
        "increment_id": "000000190",
        "first_session_entity_id": 190,
        "expected_lines": expected_lines,
    }
    spec_json = json.dumps(spec, indent=2)

    blurb = (
        "The agent navigates to the %s category, orders the grid by price, and buys the "
        "product the instruction describes without naming: id %d (%s) at $%s. Components "
        "assert that exactly one session order exists, that it is 000000190, and that its "
        "lines are exactly %s."
        % (task["category"], task["target"]["productId"], task["target"]["sku"],
           ("%.2f" % task["target"]["price"]),
           ("that one product"
            if task["clear_cart"]
            else "the three cart lines the customer already had plus that product"))
    )

    with open(os.path.join(bundle, "reward.py"), "w") as fh:
        fh.write(REWARD_TEMPLATE.format(
            task_id=tid, blurb=blurb, spec_json=spec_json,
            lines_component=lines_component))

    with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
        fh.write(NEMO_REWARD_TEMPLATE.format(
            task_id=tid, spec_json=spec_json, lines_component=lines_component))

    setup_src = None
    if task["clear_cart"]:
        setup_src = SETUP_TEMPLATE.format(task_id=tid)
        with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
            fh.write(setup_src)

    if task["clear_cart"]:
        criteria = [
            "orders holds exactly one row with entityId >= 190, and it carries "
            "incrementId 000000190 and entityId 190.",
            "That order's items are exactly one line: productId %d, sku %s, qtyOrdered "
            "%d, price %.2f."
            % (task["target"]["productId"], task["target"]["sku"], task["target"]["qty"],
               task["target"]["price"]),
        ]
    else:
        criteria = [
            "orders holds exactly one row with entityId >= 190, and it carries "
            "incrementId 000000190 and entityId 190.",
            "That order's items are exactly four lines - productId 15033 / 15787 / 10617 "
            "at qtyOrdered 1 each, plus productId %d (sku %s) at qtyOrdered 1 and price "
            "%.2f."
            % (task["target"]["productId"], task["target"]["sku"], task["target"]["price"]),
        ]

    instruction_doc = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": "webarena_shopping_mock",
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": criteria,
    }
    with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
        json.dump(instruction_doc, fh, indent=2)
        fh.write("\n")

    injected = []
    if task["clear_cart"]:
        injected = [
            "cart.items: [] - the pristine cart holds seeded quote lines 554/555/556 "
            "(table lamp, coat rack, bodysuit) and placeOrder ships every cart line, so "
            "an untouched cart would put three unrelated products into the graded order. "
            "There is no bulk empty-cart control (CORRECTIONS #69), so clearing it in the "
            "episode would be a third skill; the setup supplies the empty cart instead.",
            "Nothing else is written: orders, addresses, customer, wishlist, compareList "
            "and all five next* counters are re-posted exactly as GET /go returned them, "
            "so nextOrderIncrementId stays at 190 and no part of the rubric is "
            "pre-satisfied.",
        ]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [
            {
                "name": "webarena_shopping_mock",
                "source_name": "shopping",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
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
            "style": task["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R5", "A10"],
            "skill_chain": (
                "browse the nav band to %s and order the grid by price to derive the "
                "%s -> add that product and place the order through checkout"
                % (task["category"], task.get("derived_phrase", "target product"))
            ),
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "topic": "category_winner_checkout",
            "surface": (
                "/%s.html category listing (sorted by price), product page, "
                "/checkout/cart/, /checkout/" % task["url_path"]
            ),
            "inspiration_ids": task["inspiration"],
            "injected_preconditions": injected,
            "authoring_notes": task["notes"] + [
                "Tie margin: %s." % task["margin"],
                "The target carries no required custom options in productOptions.json, so "
                "the PDP Add to Cart succeeds without an option selection and the order "
                "line stores options: [].",
                "placeOrder (AppContext.jsx:513) mints incrementId 000000190 from the "
                "seeded nextOrderIncrementId 190 (dataManager.js createInitialData), "
                "copies every cart line into order items[] and empties the cart in the "
                "same reducer.",
                "The reward gates on the recorded productId / sku / qtyOrdered / price of "
                "the order lines, never on 'an order was placed', and it requires exactly "
                "one order above entity id 189 so a wrong purchase followed by a right one "
                "does not score.",
                "Both reward programs read the app current session state only.",
            ],
        },
    }
    with open(os.path.join(bundle, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(bundle, "nemo_reward.py")) as fh:
        nemo_reward_src = fh.read()

    row = {
        "task_payload": {
            "task_id": tid,
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
                "bundle_id": tid,
                "app_dir": "webarena_shopping_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward_src,
            },
        }
    }
    with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2)
        fh.write("\n")

    direction_click = ""
    if task["order"] == "desc":
        direction_click = (
            "    page.click('a[data-role=\"direction-switcher\"]')\n"
            "    page.wait_for_timeout(400)\n"
        )
    with open(os.path.join(REPLAYS, tid + ".py"), "w") as fh:
        fh.write(REPLAY_TEMPLATE.format(
            task_id=tid, nav=task["nav"], link_text=task["link_text"],
            position=task["position"], order=task["order"],
            direction_click=direction_click))

    return row


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    rows = [build(task) for task in TASKS]
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({
            "schema_version": 2,
            "tasks": [{"task_id": t["id"], "path": "../../%s/task.json" % t["id"]}
                      for t in TASKS],
        }, fh, indent=2)
        fh.write("\n")
    print("wrote %d bundles" % len(rows))


if __name__ == "__main__":
    main()
