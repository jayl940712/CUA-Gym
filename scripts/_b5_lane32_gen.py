#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 32 (shopping / category_cheapest_to_cart).

Emits the ten bundles under output/tasks/shopping/<task_id>/.
Read-only with respect to hub/.
"""
import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/category_cheapest_to_cart")
REPLAYS = os.path.join(BATCH, "replays")

SEEDED = [
    (554, 15033, "B087QSCXGT", 250.8),
    (555, 15787, "B08JLHHCM6", 40.99),
    (556, 10617, "B09LQTV3RX", 58.63),
]

# ---------------------------------------------------------------------------
# shared reward source
# ---------------------------------------------------------------------------

HELPERS = '''
SEEDED_PRODUCT_IDS = [15033, 15787, 10617]


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
    for line in _cart_lines(state):
        pid = _int(line.get("productId"))
        if pid is not None:
            found.append(pid)
    return found


def _seeded_lines_present(state):
    """Every seeded cart line still sits in the cart exactly once."""
    ids = _product_ids(state)
    for pid in SEEDED_PRODUCT_IDS:
        if ids.count(pid) != 1:
            return False
    return True


def _cart_confined_to(state, allowed):
    ids = _product_ids(state)
    if len(ids) != len(_cart_lines(state)):
        return False
    for pid in ids:
        if pid not in allowed:
            return False
    return True


def _target_line_ok(state, product_id, sku):
    """Exactly one cart line for this product, carrying the catalog sku."""
    matches = []
    for line in _cart_lines(state):
        if _int(line.get("productId")) == product_id:
            matches.append(line)
    if len(matches) != 1:
        return False
    line = matches[0]
    qty = _int(line.get("qty"))
    if qty is None or qty < 1:
        return False
    return _text(line.get("sku")) == sku


def _absent(state, product_id):
    return product_id not in _product_ids(state)
'''

EVALUATE_TAIL = '''

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
'''

NEMO_TAIL = '''

def _fetch_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    return state if isinstance(state, dict) else {}


def main():
    try:
        state = _fetch_state()
    except Exception as exc:  # noqa: BLE001 - reward must always emit a score
        print("reward error: " + str(exc))
        print("REWARD: 0.0")
        return
    checks = _checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
        print("component " + name + ": " + str(bool(checks.get(name))))
    print("REWARD: " + str(round(total, 6)))


main()
'''


def weights_block(weights):
    lines = ["COMPONENT_WEIGHTS = {"]
    for name, value in weights:
        lines.append('    "%s": %s,' % (name, value))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    return "\n".join(lines)


def checks_multi(targets):
    """targets: list of (component_name, product_id, sku)."""
    allowed = sorted(set(SEEDED_PRODUCT_IDS_LIST + [t[1] for t in targets]))
    body = ["", "", "ALLOWED_PRODUCT_IDS = %s" % (allowed,), "", "", "def _checks(state):"]
    body.append("    base = _seeded_lines_present(state) and _cart_confined_to(state, ALLOWED_PRODUCT_IDS)")
    body.append("    return {")
    for name, pid, sku in targets:
        body.append('        "%s": base and _target_line_ok(state, %d, "%s"),' % (name, pid, sku))
    body.append("    }")
    return "\n".join(body)


def checks_swap(target, sku, injected_pid, drop_name, add_name):
    allowed = sorted(set(SEEDED_PRODUCT_IDS_LIST + [target]))
    body = ["", "", "ALLOWED_PRODUCT_IDS = %s" % (allowed,), "", "", "def _checks(state):"]
    body.append("    return {")
    body.append('        "%s": _seeded_lines_present(state) and _absent(state, %d),' % (drop_name, injected_pid))
    body.append(
        '        "%s": (_seeded_lines_present(state)'
        "\n                 and _cart_confined_to(state, ALLOWED_PRODUCT_IDS)"
        '\n                 and _target_line_ok(state, %d, "%s")),' % (add_name, target, sku)
    )
    body.append("    }")
    return "\n".join(body)


SEEDED_PRODUCT_IDS_LIST = [15033, 15787, 10617]


# ---------------------------------------------------------------------------
# task definitions
# ---------------------------------------------------------------------------

TASKS = []


def add(**kw):
    TASKS.append(kw)


add(
    task_id="category_cheapest_to_cart_deli_counter_bargain_001",
    instruction=(
        "I'm putting together a cheap cold-cut platter. Find the least expensive "
        "product in the Deli Meats & Cheeses range and add it to my shopping cart."
    ),
    style="terse",
    difficulty="medium",
    skills=["R1", "A4"],
    skill_chain="sort Deli Meats & Cheeses by price ascending -> take the cheapest tile -> add that product to the cart",
    analogues=[
        "View the product page for the least expensive shoe storage with a minimum storage capacity of 12 pairs.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=[],
    targets=[("cheapest_deli_item_carted", 47533, "B091FZR71C")],
    weights=[("cheapest_deli_item_carted", 1.0)],
    criteria=[
        "state.cart.items holds exactly four lines: the three seeded lines (products 15033, 15787, 10617) "
        "and one new line for product 47533 (sku B091FZR71C, \"Coppa Capicola- SLICED 3 packages\", $6.51) "
        "at quantity 1 or more.",
    ],
    notes=[
        "Category 273 Grocery & Gourmet Food > Deli & Prepared Foods > Deli Meats & Cheeses, urlPath "
        "grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses, 36 seeded listable products == "
        "categories.json dbProductCount 36, so the seed superlative equals the one a human computes on the page.",
        "Cheapest $6.51 (id 47533); runner-up $11.67 (id 82251). Margin $5.16, no tie.",
        "47533 carries no entry in productOptions.json, so ProductGrid.jsx:63-66 does not divert the tile "
        "Add to Cart to the PDP; either route adds the line.",
    ],
)

add(
    task_id="category_cheapest_to_cart_table_linens_bargain_002",
    instruction=(
        "My dining table needs protecting and I don't want to overspend. Put the "
        "cheapest Kitchen & Table Linens product in the store into my shopping cart."
    ),
    style="terse",
    difficulty="medium",
    skills=["R1", "A4"],
    skill_chain="sort Kitchen & Table Linens by price ascending -> take the cheapest tile -> add that product to the cart",
    analogues=[
        "View the product page for the least expensive ssd hard drive with a minimum storage capacity of 1TB.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=[],
    targets=[("cheapest_linen_carted", 14578, "B09R1VF1LR")],
    weights=[("cheapest_linen_carted", 1.0)],
    criteria=[
        "state.cart.items holds exactly four lines: the three seeded lines and one new line for product "
        "14578 (sku B09R1VF1LR, KOECPS clear table protector, $4.02) at quantity 1 or more.",
    ],
    notes=[
        "Category 189, urlPath home-kitchen/kitchen-dining/kitchen-table-linens, 112 seeded listable == "
        "dbProductCount 112.",
        "Cheapest $4.02 (id 14578); runner-up $5.99 (id 97577). Margin $1.97, no tie.",
        "14578 has no custom options.",
    ],
)

add(
    task_id="category_cheapest_to_cart_legacy_nintendo_003",
    instruction=(
        "Retro night on a budget: add the single cheapest item in the Nintendo "
        "Systems range under Video Games' Legacy Systems to my shopping cart."
    ),
    style="terse",
    difficulty="medium",
    skills=["R1", "A4"],
    skill_chain="sort Nintendo Systems by price ascending -> take the cheapest tile -> add that product to the cart",
    analogues=[
        "Go to the page showing PS4 accessories products sorted by ascending price",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=[],
    targets=[("cheapest_legacy_nintendo_carted", 39600, "B01GU9NZS8")],
    weights=[("cheapest_legacy_nintendo_carted", 1.0)],
    criteria=[
        "state.cart.items holds exactly four lines: the three seeded lines and one new line for product "
        "39600 (sku B01GU9NZS8, the Animal Crossing Amiibo card, $0.89) at quantity 1 or more.",
    ],
    notes=[
        "Category 233, urlPath video-games/legacy-systems/nintendo-systems, 48 seeded listable == "
        "dbProductCount 48.",
        "Cheapest $0.89 (id 39600); runner-up $3.99 (id 100726). Margin $3.10, no tie.",
        "The sibling PlayStation Systems category is deliberately NOT used anywhere in this lane: it has an "
        "exact two-way tie at $0.99 (ids 19114 and 99844).",
    ],
)

add(
    task_id="category_cheapest_to_cart_mp3_adapter_004",
    instruction=(
        "My car stereo needs an adapter and money is tight. Add the lowest-priced "
        "MP3 & MP4 Player Accessories item to my shopping cart."
    ),
    style="terse",
    difficulty="medium",
    skills=["R1", "A4"],
    skill_chain="sort MP3 & MP4 Player Accessories by price ascending -> take the cheapest tile -> add that product to the cart",
    analogues=[
        "Go to the page showing competitive swimwear products sorted by ascending price",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=[],
    targets=[("cheapest_mp3_accessory_carted", 19698, "B084D1MRWQ")],
    weights=[("cheapest_mp3_accessory_carted", 1.0)],
    criteria=[
        "state.cart.items holds exactly four lines: the three seeded lines and one new line for product "
        "19698 (sku B084D1MRWQ, hudiemm0B car cassette audio converter, $0.99) at quantity 1 or more.",
    ],
    notes=[
        "Category 255, urlPath electronics/portable-audio-video/mp3-mp4-player-accessories, 54 seeded "
        "listable == dbProductCount 54.",
        "Cheapest $0.99 (id 19698); runner-up $6.49 (id 41449). Margin $5.50, no tie.",
        "No captured listing exists for this path, so resolveListing falls through to the derived pool for "
        "every query - the price sort is pure seed ordering.",
    ],
)

add(
    task_id="category_cheapest_to_cart_office_and_balcony_005",
    instruction=(
        "I'm furnishing a home office and a balcony as cheaply as possible. Cart "
        "the least expensive Chairs & Sofas product and the least expensive Patio "
        "Furniture & Accessories product."
    ),
    style="terse",
    difficulty="hard",
    skills=["R5", "R1", "A4"],
    skill_chain=(
        "navigate two separate category listings -> sort each by price ascending -> "
        "take each cheapest tile -> add both products to the cart"
    ),
    analogues=[
        "Pull up the page with all \"chairs\" listings sorted by ascending price.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=["derived_target", "cross_page", "multi_entity"],
    targets=[
        ("cheapest_office_seat_carted", 32684, "B07ZNNJW9S"),
        ("cheapest_patio_item_carted", 34421, "B08MQMB5GD"),
    ],
    weights=[("cheapest_office_seat_carted", 0.5), ("cheapest_patio_item_carted", 0.5)],
    criteria=[
        "state.cart.items holds a line for product 32684 (sku B07ZNNJW9S, KaiMeng ribbed office chair, "
        "$25.21) at quantity 1 or more.",
        "state.cart.items holds a line for product 34421 (sku B08MQMB5GD, synthetic rattan woven material, "
        "$17.99) at quantity 1 or more.",
        "No cart line exists for any product other than those two and the three seeded lines, and each "
        "seeded line is still present exactly once.",
    ],
    notes=[
        "Chairs & Sofas is category 183 (office-products/office-furniture-lighting/chairs-sofas), 63 seeded "
        "listable == dbProductCount 63; cheapest $25.21 id 32684, runner-up $36.99 id 68782, margin $11.78.",
        "Patio Furniture & Accessories is category 50 (patio-lawn-garden/patio-furniture-accessories), 92 "
        "seeded listable == dbProductCount 92; cheapest $17.99 id 34421, runner-up $23.93 id 99091, "
        "margin $5.94.",
        "Neither product carries custom options.",
    ],
)

add(
    task_id="category_cheapest_to_cart_phone_and_case_006",
    instruction=(
        "Get me the cheapest phone OneStopMarket sells in Cell Phones, plus the "
        "cheapest Flip Case to go with it. Both into my shopping cart, please."
    ),
    style="terse",
    difficulty="hard",
    skills=["R5", "R1", "A4"],
    skill_chain=(
        "navigate the Cell Phones and Flip Cases listings -> sort each by price ascending -> "
        "take each cheapest tile -> add both products to the cart"
    ),
    analogues=[
        "Pull up the page with all \"iphone 12 phone case\" listings sorted by price.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=["derived_target", "cross_page", "multi_entity"],
    targets=[
        ("cheapest_phone_carted", 43211, "B08J4KW31M"),
        ("cheapest_flip_case_carted", 76561, "B087314JM4"),
    ],
    weights=[("cheapest_phone_carted", 0.5), ("cheapest_flip_case_carted", 0.5)],
    criteria=[
        "state.cart.items holds a line for product 43211 (sku B08J4KW31M, TracFone My Flip 2, $1.49) at "
        "quantity 1 or more.",
        "state.cart.items holds a line for product 76561 (sku B087314JM4, Asuwish iPhone Xs wallet case, "
        "$6.99) at quantity 1 or more.",
        "No cart line exists for any product other than those two and the three seeded lines, and each "
        "seeded line is still present exactly once.",
    ],
    notes=[
        "Cell Phones is category 70 (cell-phones-accessories/cell-phones), 68 seeded listable == "
        "dbProductCount 68; cheapest $1.49 id 43211, runner-up $7.58 id 101266, margin $6.09.",
        "Flip Cases is category 232 (cell-phones-accessories/cases-holsters-sleeves/flip-cases), 47 seeded "
        "listable == dbProductCount 47; cheapest $6.99 id 76561, runner-up $9.99 (ids 17092 and 74655 tie "
        "for SECOND place - the minimum itself is unique). Margin $3.00.",
        "Both winners are option-free; the two $9.99 runners-up do carry required options, which is why the "
        "reward never has to reason about a runner-up's options.",
    ],
)

add(
    task_id="category_cheapest_to_cart_heater_swap_007",
    instruction=(
        "The space heater in my cart is not the cheapest thing in Heating, Cooling "
        "& Air Quality. Take it out and cart whatever actually is cheapest there."
    ),
    style="terse",
    difficulty="hard",
    skills=["R5", "R1", "A4"],
    skill_chain=(
        "read the cart -> navigate Heating, Cooling & Air Quality -> sort by price ascending -> "
        "remove the wrong line and add the cheapest product"
    ),
    analogues=[
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        "Buy the highest rated product from the Beauty & Personal Care category within a budget under 20. Discard any items in your cart if it is not empty.",
    ],
    hard_criteria=["derived_target", "cross_page"],
    swap=dict(target=13510, sku="B08FRS4SQR", injected=87880),
    weights=[("wrong_heater_removed", 0.4), ("cheapest_heating_item_carted", 0.6)],
    criteria=[
        "No cart line references product 87880 (the injected Comfort Zone CZ2018 space heater) any more, "
        "and the three seeded lines are still present.",
        "state.cart.items holds a line for product 13510 (sku B08FRS4SQR, HOMCOM 43 inch wall-mounted "
        "ethanol fireplace heater, $1.07) at quantity 1 or more, and the cart holds no product other than "
        "13510 and the three seeded lines.",
    ],
    injection=dict(
        item_id=557,
        product_id=87880,
        sku="B07Z6N7LJY",
        name="Comfort Zone CZ2018 Infrared Cabinet Space Heater, Quartz, 1500-Watt, Digital with Remote Control, Black",
        price=3.02,
        options=[],
        next_cart_item_id=558,
        description=(
            "A fourth cart line for product 87880 (the $3.02 Comfort Zone space heater, the runner-up in "
            "Heating, Cooling & Air Quality) is injected at itemId 557 with nextCartItemId bumped to 558."
        ),
    ),
    notes=[
        "Heating, Cooling & Air Quality is category 43 (home-kitchen/heating-cooling-air-quality), 85 "
        "seeded listable == dbProductCount 85; cheapest $1.07 id 13510, runner-up $3.02 id 87880, "
        "margin $1.95.",
        "listings.json DOES carry an exact capture for this path with product_list_order=price and no dir; "
        "its first three ids are 13510, 87880, 15786, which is exactly the seed's ascending order, so the "
        "capture and the derived pool agree and the first tile is 13510 either way.",
        "The injected line is the runner-up, so the distractor satisfies 'a heater in this category' and "
        "fails only the superlative. It pre-satisfies no part of the rubric: 87880 must be removed and "
        "13510 must be added, so the untouched injected lane scores 0.0.",
    ],
)

add(
    task_id="category_cheapest_to_cart_kids_blanket_swap_008",
    instruction=(
        "A Pink Minnie Mouse fleece blanket is sitting in my shopping cart, added "
        "from the Kids' Bedding category. I have decided I only want the single "
        "least expensive product that category sells, so remove the Minnie Mouse "
        "blanket from the cart and put the cheapest Kids' Bedding product in its "
        "place. The three items that were in the cart before the blanket - the "
        "table lamp, the coat rack and the bodysuit - must be left exactly as "
        "they are."
    ),
    style="explicit",
    difficulty="hard",
    skills=["R5", "R1", "A4"],
    skill_chain=(
        "read the cart -> navigate Kids' Bedding -> sort by price ascending -> "
        "remove the named line and add the cheapest product"
    ),
    analogues=[
        "View the product page for the least expensive shoe storage with a minimum storage capacity of 12 pairs.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=["derived_target", "cross_page"],
    swap=dict(target=67025, sku="B07SLP4SN8", injected=72918),
    weights=[("minnie_blanket_removed", 0.4), ("cheapest_kids_bedding_carted", 0.6)],
    criteria=[
        "No cart line references product 72918 (the injected Pink Minnie Mouse fleece blanket) any more, "
        "and the three seeded lines are still present.",
        "state.cart.items holds a line for product 67025 (sku B07SLP4SN8, Disney The Lion King kids fleece "
        "blanket, $7.59) at quantity 1 or more, and the cart holds no product other than 67025 and the "
        "three seeded lines.",
    ],
    injection=dict(
        item_id=557,
        product_id=72918,
        sku="B09F62BQMH",
        name="UPD, Inc U.P.D., Inc. Pink Minnie Mouse Fleece Blanket - Warm and Cozy Disney Minnie Fleece Throw Blanket, Soft Minnie Mouse Plush Throw Snuggle Blanket Size 45x60 Inch, B09F62BQMH, MultiColor, L",
        price=14.7,
        options=[],
        next_cart_item_id=558,
        description=(
            "A fourth cart line for product 72918 (the $14.70 Pink Minnie Mouse fleece blanket, the sixth "
            "cheapest Kids' Bedding product) is injected at itemId 557 with nextCartItemId bumped to 558."
        ),
    ),
    notes=[
        "Kids' Bedding is category 155 (home-kitchen/bedding/kids-bedding), 100 seeded listable == "
        "dbProductCount 100; cheapest $7.59 id 67025, runner-up $9.99 (ids 67437 and 88083 tie for second) "
        "so the minimum is unique with a $2.40 margin.",
        "listings.json carries a capture for this path at product_list_order=price with dir=desc only; the "
        "ascending query has no exact capture, so the ascending page is the derived pool and its first "
        "tile is 67025.",
        "The distractor is deliberately option-free (72918) so the injected record needs no options[] and "
        "can carry every field addToCart writes: itemId, productId, sku, name, price, qty, options.",
    ],
)

add(
    task_id="category_cheapest_to_cart_video_game_sweep_009",
    instruction=(
        "I am doing a bargain sweep of the Video Games department. For each of "
        "these three ranges - Virtual Reality, Nintendo Systems under Legacy "
        "Systems, and Nintendo Switch - work out which single product is the least "
        "expensive one listed, and add that product to my shopping cart. Three new "
        "lines in total, and the three items already in the cart must be left "
        "alone. The Nintendo Switch winner has a required Color option, so pick "
        "whichever colour you like when you add it."
    ),
    style="explicit",
    difficulty="hard",
    skills=["R5", "R1", "A4"],
    skill_chain=(
        "navigate three Video Games listings -> sort each by price ascending -> "
        "take each cheapest tile -> add all three products to the cart"
    ),
    analogues=[
        "Go to the page showing PS4 accessories products sorted by ascending price",
        "Buy the best rating product from \"Men\"s shoe\" category with at least 5 reviews and the product is least expensive. Choose any available variant.",
    ],
    hard_criteria=["derived_target", "multi_entity", "cross_page"],
    targets=[
        ("cheapest_vr_carted", 43290, "B099RTD42D"),
        ("cheapest_legacy_nintendo_carted", 39600, "B01GU9NZS8"),
        ("cheapest_switch_item_carted", 77531, "B098RL6SBJ"),
    ],
    weights=[
        ("cheapest_vr_carted", 0.34),
        ("cheapest_legacy_nintendo_carted", 0.33),
        ("cheapest_switch_item_carted", 0.33),
    ],
    criteria=[
        "state.cart.items holds a line for product 43290 (sku B099RTD42D, Nurtery VR carrying case, $2.39) "
        "at quantity 1 or more.",
        "state.cart.items holds a line for product 39600 (sku B01GU9NZS8, Animal Crossing Amiibo card, "
        "$0.89) at quantity 1 or more.",
        "state.cart.items holds a line for product 77531 (sku B098RL6SBJ, Nintendo Switch OLED Model, "
        "$3.66) at quantity 1 or more, with any Color chosen.",
        "No cart line exists for any product other than those three and the three seeded lines, and each "
        "seeded line is still present exactly once.",
    ],
    notes=[
        "Virtual Reality is category 247 (video-games/pc/virtual-reality), 55 seeded listable == "
        "dbProductCount 55; cheapest $2.39 id 43290, runner-up $7.08 id 40622, margin $4.69.",
        "Nintendo Systems is category 233, cheapest $0.89 id 39600, runner-up $3.99 id 100726, "
        "margin $3.10.",
        "Nintendo Switch is category 71 (video-games/nintendo-switch), 51 seeded listable == "
        "dbProductCount 51; cheapest $3.66 id 77531, runner-up $4.95 id 40855, margin $1.29.",
        "77531 carries a required Color option (optionId 52069, values White / Neon Blue and Red), so its "
        "tile Add to Cart navigates to the PDP instead of adding (ProductGrid.jsx:63-66). The reward scores "
        "the line's productId, sku and qty only and never the chosen colour.",
    ],
)

add(
    task_id="category_cheapest_to_cart_budget_smartwatch_010",
    instruction=(
        "Add the cheapest smartwatch in the store's Smartwatches range to my "
        "shopping cart - any colour is fine."
    ),
    style="terse",
    difficulty="medium",
    skills=["R1", "A4"],
    skill_chain="sort Smartwatches by price ascending -> take the cheapest tile -> add that product to the cart through its product page",
    analogues=[
        "View the product page for the least expensive ssd hard drive with a minimum storage capacity of 1TB.",
        "Add the product with the lowest per unit price from my open tabs to the shopping cart",
    ],
    hard_criteria=[],
    targets=[("cheapest_smartwatch_carted", 19328, "B01HYDGJ6Y")],
    weights=[("cheapest_smartwatch_carted", 1.0)],
    criteria=[
        "state.cart.items holds exactly four lines: the three seeded lines and one new line for product "
        "19328 (sku B01HYDGJ6Y, Padgene bluetooth smartwatch, $22.49) at quantity 1 or more, with any "
        "Color chosen.",
    ],
    notes=[
        "Smartwatches is category 256 (electronics/wearable-technology/smartwatches), 56 seeded listable == "
        "dbProductCount 56; cheapest $22.49 id 19328, runner-up $23.99 id 75958, margin $1.50.",
        "19328 carries a required Color option (optionId 11704, seven values), so the tile Add to Cart "
        "silently navigates to the PDP (ProductGrid.jsx:63-66). The task must be completed from the product "
        "page, and the reward scores productId / sku / qty only, never the colour.",
        "No captured listing exists for this path.",
    ],
)


# ---------------------------------------------------------------------------
# emitters
# ---------------------------------------------------------------------------

REWARD_DOC = '''"""Deterministic reward for {task_id}.

Success criteria:
{criteria_block}

Reads `current_state` only. Ground truth is the frozen catalog of
webarena_shopping_mock: every product id, sku and price below was measured
directly from src/data/products.json and src/data/categories.json.
"""
'''

NEMO_DOC = '''"""NeMo-Gym reward program for {task_id}.

Implements exactly the rubric of reward.py against `current_state` from
GET /go?sid=..., and prints `REWARD: <float>` on every output path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""
'''


def write(path, text):
    with open(path, "w") as handle:
        handle.write(text)


def build_checks(task):
    if "swap" in task:
        swap = task["swap"]
        names = [w[0] for w in task["weights"]]
        return checks_swap(swap["target"], swap["sku"], swap["injected"], names[0], names[1])
    return checks_multi(task["targets"])


def emit(task):
    tid = task["task_id"]
    directory = os.path.join(OUT, tid)
    os.makedirs(directory, exist_ok=True)

    criteria_block = "\n".join("  * " + c for c in task["criteria"])
    checks_src = build_checks(task)
    weights_src = weights_block(task["weights"])

    reward_src = (
        REWARD_DOC.format(task_id=tid, criteria_block=criteria_block)
        + HELPERS
        + "\n\n"
        + weights_src
        + "\n"
        + checks_src
        + "\n"
        + EVALUATE_TAIL
    )
    write(os.path.join(directory, "reward.py"), reward_src)

    nemo_src = (
        NEMO_DOC.format(task_id=tid)
        + "\nimport requests\n"
        + '\nSID = "__CUA_GYM_SID__"\n'
        + 'BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n'
        + HELPERS
        + "\n\n"
        + weights_src
        + "\n"
        + checks_src
        + "\n"
        + NEMO_TAIL
    )
    write(os.path.join(directory, "nemo_reward.py"), nemo_src)

    setup_src = None
    if "injection" in task:
        inj = task["injection"]
        items = []
        for item_id, product_id, sku, price in SEEDED:
            items.append(
                {
                    "itemId": item_id,
                    "productId": product_id,
                    "sku": sku,
                    "name": SEED_NAMES[product_id],
                    "qty": 1,
                    "price": price,
                    "options": SEED_OPTIONS[product_id],
                }
            )
        items.append(
            {
                "itemId": inj["item_id"],
                "productId": inj["product_id"],
                "sku": inj["sku"],
                "name": inj["name"],
                "qty": 1,
                "price": inj["price"],
                "options": inj["options"],
            }
        )
        patch = {"cart": {"quoteId": 255, "items": items}, "nextCartItemId": inj["next_cart_item_id"]}
        patch_json = json.dumps(patch, indent=2)
        setup_src = SETUP_TEMPLATE.format(
            task_id=tid, description=inj["description"], patch=patch_json
        )
        write(os.path.join(directory, "initial_setup.py"), setup_src)

    instruction = task["instruction"]

    write(
        os.path.join(directory, "task_instruction.json"),
        json.dumps(
            {
                "task_id": tid,
                "task_instruction": instruction,
                "app_dir": "webarena_shopping_mock",
                "start_path": "/",
                "difficulty": task["difficulty"],
                "success_criteria": task["criteria"],
            },
            indent=2,
        )
        + "\n",
    )

    metadata = {
        "style": task["style"],
        "difficulty": task["difficulty"],
        "shape": "retrieval_writeback",
        "skills": task["skills"],
        "skill_chain": task["skill_chain"],
        "official_analogues": task["analogues"],
        "hard_criteria": task["hard_criteria"],
        "topic": "category_cheapest_to_cart",
        "batch": "batch-5 lane 32 (shopping / category_cheapest_to_cart)",
        "lane_skill_chain": "R5 -> R1 -> A4",
        "inspiration_ids": task["inspiration_ids"],
        "authoring_notes": task["notes"],
    }
    if "injection" in task:
        metadata["injected_preconditions"] = [task["injection"]["description"]]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": instruction,
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
        "metadata": metadata,
    }
    write(os.path.join(directory, "task.json"), json.dumps(manifest, indent=2) + "\n")

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_shopping_mock"],
            "start_urls": [],
            "intent": instruction,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": "webarena_shopping_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_src,
            },
        }
    }
    write(os.path.join(directory, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
    return row


SEED_NAMES = {
    15033: "Uttermost Volterra Crackled Taupe-Gray Ceramic Table Lamp",
    15787: "NOZE Rustic Coat Rack Wall Mounted Shelf with 4 Hooks, Hanging Entryway Organizer for Mug Coffee Cup, Holding Solid Wooden Shelf with 2 Baskets for Kitchen Living Room, Bathroom and Bedroom",
    10617: "Plus Size Lingerie for Women Sexy for Sex Naughty Eyelash Lace Bodysuit Naughty Mesh One Piece Teddy Bodysuit Outfits",
}
SEED_OPTIONS = {
    15033: [],
    15787: [],
    10617: [
        {"optionId": 4348, "label": "Size", "optionTypeId": 23919, "value": "Large"},
        {"optionId": 4349, "label": "Color", "optionTypeId": 23922, "value": "Blue"},
    ],
}

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{description}

The whole cart is rewritten, seeded lines included, so the injected line sits
in a cart that is otherwise byte-identical to the pristine seed.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

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

INSPIRATION = {
    "category_cheapest_to_cart_deli_counter_bargain_001": ["webarena-284", "webarena-431"],
    "category_cheapest_to_cart_table_linens_bargain_002": ["webarena-286", "webarena-431"],
    "category_cheapest_to_cart_legacy_nintendo_003": ["webarena-351", "webarena-431"],
    "category_cheapest_to_cart_mp3_adapter_004": ["webarena-353", "webarena-431"],
    "category_cheapest_to_cart_office_and_balcony_005": ["webarena-324", "webarena-431"],
    "category_cheapest_to_cart_phone_and_case_006": ["webarena-328", "webarena-431"],
    "category_cheapest_to_cart_heater_swap_007": ["webarena-431", "webarena-792"],
    "category_cheapest_to_cart_kids_blanket_swap_008": ["webarena-284", "webarena-431"],
    "category_cheapest_to_cart_video_game_sweep_009": ["webarena-351", "webarena-509"],
    "category_cheapest_to_cart_budget_smartwatch_010": ["webarena-286", "webarena-431"],
}


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    rows = []
    for task in TASKS:
        task["inspiration_ids"] = INSPIRATION[task["task_id"]]
        rows.append(emit(task))
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    index = {
        "schema_version": 2,
        "tasks": [{"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]} for t in TASKS],
    }
    with open(os.path.join(BATCH, "index.json"), "w") as handle:
        handle.write(json.dumps(index, indent=2) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
