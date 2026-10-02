#!/usr/bin/env python3
"""Batch-6 lane 42 (shopping, R6 -> A4) bundle generator.

Chain: read a product's customer reviews for a described complaint, then add the
product the complaint points at to the cart or the wish list.

The candidate set is INJECTED (wish list / cart / compare list) rather than
browsed, because the storefront quick search does not index review text --
`buildSearchCorpus()` (src/utils/catalog.js:1023-1039) scores name + sku +
url_key as the strong field and the sharded description index as the weak one.
Reviews are reachable only through the PDP Reviews tab.

Writes bundles under output/tasks/shopping/<task_id>/.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
HUB = os.path.join(ROOT, "hub/websites/webarena_shopping_mock/src/data")
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches", "review_text_match_to_cart")

APP = "webarena_shopping_mock"
ENV = "CUA_GYM_WEBARENA_SHOPPING_URL"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

SEEDED_CART = [
    (15033, 1, ()),
    (15787, 1, ()),
    (10617, 1, (("Color", "Blue"), ("Size", "Large"))),
]

products = {p["id"]: p for p in json.load(open(os.path.join(HUB, "products.json")))}


def P(pid):
    p = products[pid]
    return {"id": p["id"], "sku": p["sku"], "name": p["name"], "urlKey": p["urlKey"],
            "price": p["price"]}


TASKS = [
    dict(
        task_id="review_text_match_to_cart_earbud_shock_wishlist_001",
        style="terse",
        surface="wishlist",
        writeback="cart",
        order=[19989, 88572, 100715, 89020],
        target=100715,
        instruction=(
            "Four pairs of earphones are saved on my wish list. One of them has a review "
            "from a buyer who got an electric shock from the right earpiece. Put that pair "
            "in my cart."
        ),
        chain="read the Reviews tab of each earphone on the wish list for the electric-shock complaint -> add the matching pair to the cart",
        snippet="Getting shocked",
        review="[1 star, David] 'Very disappointed' - Right ear shorting out. Getting shocked, no noise reduction.",
        analogues=[
            "Get name(s) of reviewer(s) who mention ear cups being small for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from="low_star_reviewer_names_corsair_headset_004",
        notes=[
            "Predicate 'a reviewer got an electric shock' matches exactly one review row in the whole 76,378-row corpus (review on product 100715, nickname David). Within the injected four, 100715 has 1 matching row and 19989 / 88572 / 89020 have 0.",
            "No candidate's NAME contains shock/shorting, so a name-matching agent cannot skip the Reviews tab.",
            "All four candidates are listable and carry no required product options, so the PDP and tile Add to Cart both write a plain options-free line (ProductGrid.jsx:63-66 would otherwise redirect).",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_charger_phone_case_002",
        style="terse",
        surface="cart",
        writeback="wishlist",
        order=[38423, 101874, 74319, 76726],
        target=74319,
        instruction=(
            "I put four chargers in my cart to compare. Reviewers say one of them will not "
            "charge a phone that still has its case on. Save that one to my wish list."
        ),
        chain="read the Reviews tab of each charger sitting in the cart for the phone-case complaint -> add the matching charger to the wish list",
        snippet="if you use a case it may not work",
        review="[1 star, Gene Avorio] 'A case of no case' - ... Unfortunately if you use a case it may not work. ... It will not charge my phone.",
        analogues=[
            "Get name(s) of reviewer(s) who mention price being unfair for the product on the current page",
            "Add a laundry detergent to my wish list.",
        ],
        derived_from="low_star_reviewer_names_wallet_case_charging_010",
        notes=[
            "'case' appears in 2 review rows on 74319 (Akashya Smith and Gene Avorio) and in 0 rows on 38423 / 76726 / 101874. The exact snippet 'if you use a case it may not work' is 1 row / 1 product corpus-wide.",
            "No candidate NAME contains the word case.",
            "The four candidates are appended to the three seeded cart lines (554/555/556), which are a lamp, a coat rack and lingerie -- none of them a charger, so 'the four chargers in my cart' is unambiguous.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_dimmer_switch_wishlist_003",
        style="terse",
        surface="wishlist",
        writeback="cart",
        order=[68842, 36604, 86880, 97540],
        target=86880,
        instruction=(
            "My wish list has four light fittings on it. Exactly one has a reviewer "
            "complaining the dimmer switch does nothing. Add that fitting to my shopping "
            "cart."
        ),
        chain="read the Reviews tab of each light fitting on the wish list for the broken-dimmer complaint -> add the matching fitting to the cart",
        snippet="dimmed switch does not work",
        review="[3 stars, Tp.] 'Dimmer switch doesn't work' - Received this today. Only one brightness, dimmed switch does not work.",
        analogues=[
            "Get name(s) of reviewer(s) who mention print quality explicitly with a rating of 3 or less stars for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from="low_star_reviewer_names_hdmi_extractor_sound_006",
        notes=[
            "Deliberate name trap: candidate 68842 is 'Light It! By Fulcrum, LED Wireless Motion Sensor Wall Sconce with Dimmer and Adjustable Timer' -- the only candidate whose NAME says Dimmer -- and it has 0 review rows mentioning a dimmer. The target 86880 has 1. An agent that pattern-matches the title instead of opening the Reviews tab scores 0.0.",
            "Corpus-wide the snippet 'dimmed switch does not work' is 1 row / 1 product.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_royal_blue_pillow_compare_004",
        style="terse",
        surface="compare",
        writeback="cart",
        order=[36314, 71229, 97792, 99055],
        target=99055,
        instruction=(
            "I am comparing four throw pillows. One has a reviewer saying the fabric turned "
            "out royal blue instead of the shade advertised. Add that one to my cart."
        ),
        chain="read the Reviews tab of each pillow on the comparison list for the wrong-shade-of-blue complaint -> add the matching pillow to the cart",
        snippet="More of a royal blue",
        review="[2 stars, Theresa A Rickman] 'NOT navy!' - The pillows were nice but NOT navy. More of a royal blue. Sending back!",
        analogues=[
            "Get name(s) of reviewer(s) who mention complain of the customer service for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from=None,
        notes=[
            "The instruction says 'royal blue', not 'navy', on purpose: 99055's own NAME contains 'Navy Blue', so a navy-worded predicate would be answerable from the comparison table alone. 'royal blue' appears in 0 candidate names and in exactly 1 review row corpus-wide (19 rows / 13 products match the looser regex, none of them another candidate).",
            "Compare Products is site chrome (Header.jsx:64) and its link loses the `no-display` class as soon as compareList is non-empty, so the injected list is reachable from '/' in one click.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_stale_energy_bars_005",
        style="explicit",
        surface="wishlist",
        writeback="cart",
        order=[86783, 73080, 15265, 97002],
        target=15265,
        instruction=(
            "I saved four snack bars to my wish list while I made up my mind. Open each of "
            "them and read the customer reviews on the product page. Exactly one of the four "
            "has a reviewer who says the bars turned up close to their expiry date and tasted "
            "old and stale. Add that product to my shopping cart at quantity 1."
        ),
        chain="read the Reviews tab of each snack bar on the wish list for the near-expiry complaint -> add the matching bar to the cart",
        snippet="almost expired and just tasted old",
        review="[2 stars, flux] 'Almost expired and taste pretty bad/old.' - ... these were hard, almost expired and just tasted old.",
        analogues=[
            "Get name(s) of reviewer(s) who mention price being unfair for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from="low_star_reviewer_names_nilla_wafers_cookies_007",
        notes=[
            "Distractor 86783 is also a CLIF bar, so brand matching does not separate the four. 'expired' appears in 1 row on 15265 and 0 rows on 73080 / 86783 / 97002; the snippet 'almost expired and just tasted old' is 1 row / 1 product corpus-wide.",
            "The other three all have taste complaints ('too sweet', 'dry and dull', 'sickening sweetness'), so only the specific near-expiry wording discriminates.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_unknown_part_battery_006",
        style="terse",
        surface="cart",
        writeback="wishlist",
        order=[75964, 19763, 18392, 99510],
        target=19763,
        instruction=(
            "My cart has four phone-repair parts in it. One of them has a review where the "
            "phone reported an unknown part after it was fitted. Save that one to my wish list."
        ),
        chain="read the Reviews tab of each repair part in the cart for the 'unknown part' warning -> add the matching part to the wish list",
        snippet="unknown part",
        review="[1 star, luisluis] 'Battery not functioning as expected' - ... a message showed in the iphone as “unknown part” ...",
        analogues=[
            "Get name(s) of reviewer(s) who mention good fingerprint resistant for the product on the current page",
            "Add a laundry detergent to my wish list.",
        ],
        derived_from="low_star_reviewer_names_psp_battery_009",
        notes=[
            "'unknown part' matches exactly 1 review row across all 76,378 rows, and that row is on 19763. Candidate 99510 is also an iPhone replacement battery with a professional tool kit, so product type does not separate them -- only the review does.",
            "Nickname 'luisluis' on the target is a self-concatenated nickname of the class CORRECTIONS #77 describes; harmless here because the rubric scores product identity, never a nickname set.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_faux_flower_buds_007",
        style="terse",
        surface="wishlist",
        writeback="cart",
        order=[14012, 97603, 35899, 86024],
        target=86024,
        instruction=(
            "Four artificial plant items sit on my wish list. One of them drew a review "
            "complaining that the buds fall off. Add that one to my cart."
        ),
        chain="read the Reviews tab of each artificial plant on the wish list for the falling-buds complaint -> add the matching item to the cart",
        snippet="buds fall off",
        review="[3 stars, bob perkins] 'buds fall off' - not worth the trouble",
        analogues=[
            "Get name(s) of reviewer(s) who mention under water photo for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from=None,
        notes=[
            "'buds' appears in 1 review row on 86024 and 0 rows on 14012 / 35899 / 97603; the snippet 'buds fall off' is 1 row / 1 product corpus-wide. No candidate name contains 'bud'.",
            "The complaint is the review TITLE, so it is legible on the first page of the Reviews tab without opening anything further; all four candidates have <= 5 reviews, well inside the 10-per-page window (ProductPage.jsx:18).",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_laptop_wont_close_compare_008",
        style="explicit",
        surface="compare",
        writeback="wishlist",
        order=[100348, 19367, 75108, 17077],
        target=75108,
        instruction=(
            "My comparison list holds four laptop accessories. Visit each product page and "
            "read its customer reviews. Exactly one of the four has a reviewer who says their "
            "laptop no longer closes fully once the item is fitted. Add that product to my "
            "wish list."
        ),
        chain="read the Reviews tab of each laptop accessory on the comparison list for the lid-won't-close complaint -> add the matching accessory to the wish list",
        snippet="my computer doesn’t fully close",
        review="[4 stars, Alma] 'Doesn’t close completely leaving the computer on while seemingly asleep' - It’s bulky so my computer doesn’t fully close ...",
        analogues=[
            "Get name(s) of reviewer(s) who mention ear cups being small for the product on the current page",
            "Add a white desk to my wish list.",
        ],
        derived_from=None,
        notes=[
            "The comparison page has no wish-list control (ComparePage.jsx renders AddToCartButton and Remove Product only), so the writeback has to be made from the PDP -- which is exactly where the reviews are. The product-name links at ComparePage.jsx:47-49 make that path clickable from '/'.",
            "The lid-won't-close predicate hits 1 row on 75108 and 0 rows on 100348 / 17077 / 19367; the snippet is 1 row / 1 product corpus-wide.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_prints_arrived_bent_009",
        style="terse",
        surface="wishlist",
        writeback="cart",
        order=[97142, 15449, 15575, 15717],
        target=15575,
        instruction=(
            "There are four art prints on my wish list. One has a review saying they arrived "
            "bent because of the paper envelope they were shipped in. Put that print in my cart."
        ),
        chain="read the Reviews tab of each art print on the wish list for the bent-in-shipping complaint -> add the matching print to the cart",
        snippet="shipped in a paper envelope",
        review="[3 stars, Shelle] 'Not at all packaged well for shipping.' - These arrived all bent. They were shipped in a paper envelope that was placed in a bubble mailer.",
        analogues=[
            "Get name(s) of reviewer(s) who mention print quality explicitly with a rating of 3 or less stars for the product on the current page",
            "Add the product with the lowest per unit price from my open tabs to the shopping cart",
        ],
        derived_from="low_star_reviewer_names_boat_shoe_leather_003",
        notes=[
            "'bent' / 'paper envelope' match 1 row on 15575 and 0 rows on 15449 / 15717 / 97142; the snippet 'shipped in a paper envelope' is 1 row / 1 product corpus-wide.",
            "Two distractors carry packaging PRAISE ('sturdy card stock not flimsy paper', 'nice thick quality paper'), which is what makes the paper wording require reading rather than keyword spotting.",
        ],
    ),
    dict(
        task_id="review_text_match_to_cart_mirror_three_orders_010",
        style="explicit",
        surface="cart",
        writeback="wishlist",
        order=[58692, 51428, 49878, 53105],
        target=49878,
        instruction=(
            "There are four vanity mirrors sitting in my cart. Open each of them and read the "
            "customer reviews on the product page. One reviewer says they had to order their "
            "mirror three separate times before a working one finally arrived. Save that "
            "mirror to my wish list."
        ),
        chain="read the Reviews tab of each mirror in the cart for the ordered-it-three-times account -> add the matching mirror to the wish list",
        snippet="Had to purchase this mirror 3 separate times",
        review="[5 stars, Katelann] 'Third times the charm' - Had to purchase this mirror 3 separate times. The first time it shipped to the wrong shipping station. ...",
        analogues=[
            "Get name(s) of reviewer(s) who mention complain of the customer service for the product on the current page",
            "Add a chair to my wish list.",
        ],
        derived_from="low_star_reviewer_names_body_wash_lather_005",
        notes=[
            "The discriminating review is a 5-star one, so a rating filter does not find it -- the text has to be read. 51428 and 58692 both carry arrived-broken / stopped-working complaints, which is why the predicate is the re-ordering account rather than a generic defect.",
            "'3 separate times / three times / third time' matches 1 row on 49878 and 0 rows on 51428 / 53105 / 58692; the snippet is 1 row / 1 product corpus-wide.",
        ],
    ),
]

# --------------------------------------------------------------------------


def cart_lines_literal(target):
    lines = list(SEEDED_CART) + [(target, 1, ())]
    return sorted(lines)


def py_lines(lines):
    return "[" + ", ".join(
        "(%d, %d, (%s))" % (
            pid, qty,
            ", ".join("(%r, %r)" % (a, b) for a, b in opts) + ("," if len(opts) == 1 else ""),
        )
        for pid, qty, opts in lines
    ) + "]"


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
    if float(number).is_integer():
        return int(number)
    return None


def _text(value):
    if isinstance(value, str):
        return value.strip()
    return None


def _opts(raw):
    """Sorted (label, value) pairs for one cart line, or None if malformed."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return None
    pairs = []
    for option in raw:
        if not isinstance(option, dict):
            return None
        label = _text(option.get("label"))
        value = _text(option.get("value"))
        if label is None or value is None:
            return None
        pairs.append((label, value))
    pairs.sort()
    return tuple(pairs)


def _cart_lines(state):
    """[(productId, qty, ((label, value), ...)), ...] sorted, or None."""
    if not isinstance(state, dict):
        return None
    cart = state.get("cart")
    if not isinstance(cart, dict):
        return None
    items = cart.get("items")
    if not isinstance(items, list):
        return None
    lines = []
    for item in items:
        if not isinstance(item, dict):
            return None
        product_id = _int(item.get("productId"))
        qty = _int(item.get("qty"))
        options = _opts(item.get("options"))
        if product_id is None or qty is None or options is None:
            return None
        lines.append((product_id, qty, options))
    lines.sort()
    return lines


def _wishlist_lines(state):
    """[(productId, qty), ...] sorted, or None."""
    if not isinstance(state, dict):
        return None
    wishlist = state.get("wishlist")
    if not isinstance(wishlist, dict):
        return None
    items = wishlist.get("items")
    if not isinstance(items, list):
        return None
    lines = []
    for item in items:
        if not isinstance(item, dict):
            return None
        product_id = _int(item.get("productId"))
        qty = _int(item.get("qty"))
        if product_id is None or qty is None:
            return None
        lines.append((product_id, qty))
    lines.sort()
    return lines
'''


def cart_checks_block(target):
    expected = py_lines(cart_lines_literal(target))
    return (
        'COMPONENT_WEIGHTS = json.loads(r"""\n'
        '{"target_line_in_cart": 0.5, "cart_is_exactly_expected": 0.5}\n'
        '""")\n\n'
        "TARGET_LINE = (%d, 1, ())\n\n"
        "EXPECTED_CART = %s\n\n\n"
        "def _checks(state):\n"
        "    lines = _cart_lines(state)\n"
        "    if lines is None:\n"
        '        return {"target_line_in_cart": False, "cart_is_exactly_expected": False}\n'
        "    return {\n"
        '        "target_line_in_cart": TARGET_LINE in lines,\n'
        '        "cart_is_exactly_expected": lines == sorted(EXPECTED_CART),\n'
        "    }\n"
    ) % (target, expected)


def wishlist_checks_block(target):
    return (
        'COMPONENT_WEIGHTS = json.loads(r"""\n'
        '{"target_on_wishlist": 0.5, "wishlist_is_exactly_expected": 0.5}\n'
        '""")\n\n'
        "TARGET_ROW = (%d, 1)\n\n"
        "EXPECTED_WISHLIST = [(%d, 1)]\n\n\n"
        "def _checks(state):\n"
        "    rows = _wishlist_lines(state)\n"
        "    if rows is None:\n"
        '        return {"target_on_wishlist": False, "wishlist_is_exactly_expected": False}\n'
        "    return {\n"
        '        "target_on_wishlist": TARGET_ROW in rows,\n'
        '        "wishlist_is_exactly_expected": rows == sorted(EXPECTED_WISHLIST),\n'
        "    }\n"
    ) % (target, target)


def criteria_for(task):
    tgt = P(task["target"])
    if task["writeback"] == "cart":
        exp = cart_lines_literal(task["target"])
        return [
            "state.cart.items contains a line for product %d (%s) at qty 1 with no options."
            % (tgt["id"], tgt["name"][:60]),
            "state.cart.items is exactly %s as (productId, qty, sorted option label/value pairs): "
            "the three seeded quote lines plus the one product the reviews identify."
            % (py_lines(exp),),
        ]
    return [
        "state.wishlist.items contains product %d (%s) at qty 1." % (tgt["id"], tgt["name"][:60]),
        "state.wishlist.items is exactly [(%d, 1)] as (productId, qty) - the single product the "
        "reviews identify and nothing else." % (tgt["id"],),
    ]


def reward_source(task, nemo):
    tgt = P(task["target"])
    crit = criteria_for(task)
    head_doc = (
        '"""%s for %s.\n\n'
        "Success criteria:\n"
        "  * %s\n"
        "  * %s\n\n"
        "The target product is derived from the customer reviews on the product pages\n"
        "(%s), never named in the instruction. Only user-visible persisted\n"
        "state is inspected, and only the current state: the end state is asserted\n"
        'positively against frozen constants.\n"""\n'
    ) % (
        "NeMo-Gym reward program" if nemo else "Deterministic reward",
        task["task_id"],
        crit[0],
        crit[1],
        task["snippet"].replace("\\", ""),
    )
    body = REWARD_HELPERS
    block = (cart_checks_block(task["target"]) if task["writeback"] == "cart"
             else wishlist_checks_block(task["target"]))
    if nemo:
        src = head_doc + "\nimport json\nimport sys\n\nimport requests\n\n"
        src += 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER
        src += body + "\n\n" + block + "\n\n"
        src += (
            "def _fetch_state():\n"
            '    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
            "    response.raise_for_status()\n"
            "    payload = response.json()\n"
            '    state = payload.get("current_state")\n'
            "    if isinstance(state, dict):\n"
            "        return state\n"
            "    return {}\n\n\n"
            "def main():\n"
            "    try:\n"
            "        state = _fetch_state()\n"
            "        checks = _checks(state)\n"
            "        total = 0.0\n"
            "        for name in COMPONENT_WEIGHTS:\n"
            "            if checks.get(name):\n"
            "                total += COMPONENT_WEIGHTS[name]\n"
            "    except Exception as exc:\n"
            '        print("reward error: %s" % (exc,), file=sys.stderr)\n'
            '        print("REWARD: 0.0")\n'
            "        return\n"
            '    print("REWARD: %s" % (round(total, 6),))\n\n\n'
            "main()\n"
        )
        return src
    src = head_doc + "\nimport json\n\n" + body + "\n\n" + block + "\n\n"
    src += (
        "def _state(evidence):\n"
        '    apps = evidence.get("apps") if isinstance(evidence, dict) else None\n'
        "    if isinstance(apps, dict):\n"
        "        for app in apps.values():\n"
        '            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):\n'
        '                return app["current_state"]\n'
        "    return {}\n\n\n"
        "def evaluate(evidence):\n"
        "    state = _state(evidence)\n"
        "    checks = _checks(state)\n"
        "    components = []\n"
        "    for name in COMPONENT_WEIGHTS:\n"
        "        ok = bool(checks.get(name))\n"
        "        components.append({\n"
        '            "name": name,\n'
        '            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,\n'
        '            "details": {"satisfied": ok},\n'
        "        })\n"
        "    total = 0.0\n"
        "    for component in components:\n"
        '        total += component["score"]\n'
        '    return {"score": round(total, 6), "components": components}\n'
    )
    return src


def setup_source(task):
    order = task["order"]
    if task["surface"] == "wishlist":
        rows = [{"wishlistItemId": i + 1, "productId": P(pid)["id"], "sku": P(pid)["sku"],
                 "name": P(pid)["name"], "price": P(pid)["price"], "qty": 1,
                 "description": "", "addedAt": "2023-05-0%d 09:1%d:00" % (i + 1, i)}
                for i, pid in enumerate(order)]
        fixture = json.dumps({"items": rows}, indent=1)
        mutate = (
            "    state[\"wishlist\"] = {\"items\": FIXTURE[\"items\"]}\n"
            "    state[\"nextWishlistItemId\"] = %d\n" % (len(order) + 1)
        )
        guard = (
            '    if not isinstance(state.get("cart"), dict):\n'
            '        print("SETUP FAILED: state carries no cart", file=sys.stderr)\n'
            "        raise SystemExit(1)\n"
        )
    elif task["surface"] == "cart":
        rows = [{"itemId": 557 + i, "productId": P(pid)["id"], "sku": P(pid)["sku"],
                 "name": P(pid)["name"], "price": P(pid)["price"], "qty": 1, "options": []}
                for i, pid in enumerate(order)]
        fixture = json.dumps({"items": rows}, indent=1)
        mutate = (
            '    cart = state.get("cart")\n'
            "    if not isinstance(cart, dict) or not isinstance(cart.get(\"items\"), list):\n"
            '        print("SETUP FAILED: state carries no cart items list", file=sys.stderr)\n'
            "        raise SystemExit(1)\n"
            '    planted = set()\n'
            '    for row in FIXTURE["items"]:\n'
            '        planted.add(row["itemId"])\n'
            '    kept = []\n'
            '    for row in cart["items"]:\n'
            '        if isinstance(row, dict) and row.get("itemId") in planted:\n'
            '            continue\n'
            '        kept.append(row)\n'
            '    cart["items"] = kept + FIXTURE["items"]\n'
            '    state["cart"] = cart\n'
            '    state["nextCartItemId"] = %d\n'
            '    state["wishlist"] = {"items": []}\n'
            '    state["nextWishlistItemId"] = 1\n' % (557 + len(order))
        )
        guard = ""
    else:
        rows = [{"productId": P(pid)["id"], "sku": P(pid)["sku"], "name": P(pid)["name"]}
                for pid in order]
        fixture = json.dumps({"items": rows}, indent=1)
        mutate = (
            '    state["compareList"] = {"items": FIXTURE["items"]}\n'
            '    state["wishlist"] = {"items": []}\n'
            '    state["nextWishlistItemId"] = 1\n'
        )
        guard = (
            '    if not isinstance(state.get("cart"), dict):\n'
            '        print("SETUP FAILED: state carries no cart", file=sys.stderr)\n'
            "        raise SystemExit(1)\n"
        )

    why = {
        "wishlist": "the pristine wish list is empty (data/wishlist.json), so without this "
                    "there is no candidate set at all",
        "cart": "the pristine cart holds only the three seeded quote lines 554/555/556, none "
                "of which is a candidate, so without this there is no candidate set at all",
        "compare": "the pristine comparison list is empty and the header link carries "
                   "no-display, so without this there is no candidate set and no way in",
    }[task["surface"]]
    doc = (
        '"""NeMo-Gym setup program for %s.\n\n'
        "Plants the %s candidate set the retrieval runs over: four same-category products\n"
        "of which exactly one carries the review complaint the instruction describes.\n"
        "%s.\n\n"
        "Written as a read-modify-write: GET /go, mutate the WHOLE state document, POST it\n"
        "back with the set action. That is correct whether the mock's state API replaces or\n"
        "shallow-merges, and it is what /go returns to the reward.\n\n"
        "Self-contained: standard library plus requests, which is present in\n"
        'cuagym/requirements.txt.\n"""\n'
    ) % (task["task_id"], task["surface"], why)

    src = doc + "\nimport json\nimport sys\n\nimport requests\n\n"
    src += 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % PLACEHOLDER
    src += 'FIXTURE = json.loads(r"""\n%s\n""")\n\n\n' % fixture
    src += (
        "def read_state():\n"
        '    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        "    response.raise_for_status()\n"
        "    payload = response.json()\n"
        '    state = payload.get("current_state")\n'
        "    if not isinstance(state, dict):\n"
        '        state = payload.get("initial_state")\n'
        "    if not isinstance(state, dict):\n"
        '        print("SETUP FAILED: /go returned neither current_state nor initial_state",\n'
        "              file=sys.stderr)\n"
        "        raise SystemExit(1)\n"
        "    return state\n\n\n"
        "def verify():\n"
        '    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        "    check.raise_for_status()\n"
        "    payload = check.json()\n"
        '    if payload.get("state_diff") != {}:\n'
        '        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)\n'
        "        raise SystemExit(1)\n"
        '    if payload.get("initial_state") != payload.get("current_state"):\n'
        '        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)\n'
        "        raise SystemExit(1)\n"
        '    print("SETUP OK")\n\n\n'
        "def main():\n"
        "    state = read_state()\n"
    )
    src += guard + mutate
    src += (
        "    response = requests.post(\n"
        '        BASE_URL + "/post?sid=" + SID,\n'
        '        json={"action": "set", "state": state},\n'
        "        timeout=60,\n"
        "    )\n"
        "    response.raise_for_status()\n"
        "    verify()\n\n\n"
        "main()\n"
    )
    return src


SURFACE_WHY = {
    "wishlist": "wishlist.items: four %s seeded onto the pristine (empty) wish list, exactly one of which carries the review complaint the instruction describes; nextWishlistItemId advanced to 5 in the addToWishlist convention (AppContext.jsx:324-346)",
    "cart": "cart.items: four %s appended to the three seeded quote lines 554/555/556 with itemIds 557-560 in the addToCart line convention (AppContext.jsx:251-281), exactly one of which carries the review complaint; nextCartItemId advanced to 561, wishlist reset empty so the scored collection starts at zero",
    "compare": "compareList.items: four %s in the addToCompare record shape {productId, sku, name} (AppContext.jsx:398-410), exactly one of which carries the review complaint; the pristine compare list is empty, so the Header 'Compare Products' link is otherwise no-display",
}

KIND = {
    "review_text_match_to_cart_earbud_shock_wishlist_001": "earphone products",
    "review_text_match_to_cart_charger_phone_case_002": "phone chargers",
    "review_text_match_to_cart_dimmer_switch_wishlist_003": "light fittings",
    "review_text_match_to_cart_royal_blue_pillow_compare_004": "throw pillows",
    "review_text_match_to_cart_stale_energy_bars_005": "snack bars",
    "review_text_match_to_cart_unknown_part_battery_006": "phone-repair parts",
    "review_text_match_to_cart_faux_flower_buds_007": "artificial plant items",
    "review_text_match_to_cart_laptop_wont_close_compare_008": "laptop accessories",
    "review_text_match_to_cart_prints_arrived_bent_009": "art prints",
    "review_text_match_to_cart_mirror_three_orders_010": "vanity mirrors",
}


def replay_source(task):
    tgt = P(task["target"])
    entry = {
        "wishlist": "the header 'My Wish List' link (Header.jsx:30)",
        "cart": "the header cart link `.action.showcart` (Header.jsx:236)",
        "compare": "the header 'Compare Products' link (Header.jsx:64)",
    }[task["surface"]]
    act = ("the PDP 'Add to Cart' button #product-addtocart-button"
           if task["writeback"] == "cart"
           else "the PDP 'Add to Wish List' anchor a.action.towishlist (ProductPage.jsx:797)")
    lines = [
        '"""Golden replay draft for %s.' % task["task_id"],
        "",
        "Click path, no typed URLs after the landing page:",
        "  1. start at '/'",
        "  2. open the candidate collection from %s" % entry,
        "  3. for each of the four candidate products, click its name link to open the PDP,",
        "     then click the reviews link in .product-reviews-summary (ProductPage.jsx:611,",
        "     setTab('reviews')) and read the review bodies -- all four candidates have <= 5",
        "     reviews, inside the 10-per-page window (ProductPage.jsx:18)",
        "  4. the discriminating review is:",
        "         %s" % task["review"],
        "     which appears on product %d (%s)" % (tgt["id"], tgt["name"][:70]),
        "  5. on that product's PDP, click %s" % act,
        "",
        "Expected end state:",
    ]
    for c in criteria_for(task):
        lines.append("  * %s" % c)
    lines += ['"""', "", "from playwright.sync_api import sync_playwright  # noqa: F401", "",
              "# Draft only: the golden-browser agent drives this path and records the",
              "# concrete selectors. Nothing here is executed during authoring.",
              "CANDIDATES = %r" % (task["order"],),
              "TARGET_PRODUCT_ID = %d" % tgt["id"],
              "TARGET_URL_KEY = %r" % tgt["urlKey"],
              ""]
    return "\n".join(lines)


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = []
    rows = []
    for task in TASKS:
        tid = task["task_id"]
        d = os.path.join(OUT, tid)
        os.makedirs(d, exist_ok=True)
        crit = criteria_for(task)

        instruction = {
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": crit,
        }
        setup = setup_source(task)
        reward = reward_source(task, nemo=False)
        nreward = reward_source(task, nemo=True)

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
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
            "metadata": {
                "style": task["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R6", "A4"],
                "skill_chain": task["chain"],
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "injected_preconditions": [
                    SURFACE_WHY[task["surface"]] % KIND[tid],
                ],
                "topic": "shopping storefront: find the product a review complaint points at, then add it to a collection",
                "inspiration_ids": ["webarena-297", "webarena-298", "webarena-301", "webarena-127"],
                "authoring_notes": task["notes"] + [
                    "Storefront quick search does NOT index review text: buildSearchCorpus() "
                    "(src/utils/catalog.js:1023-1039) scores name + sku + url_key strongly and "
                    "the sharded description index weakly, and nothing reads reviews.json. The "
                    "candidate set is therefore injected and read through the PDP Reviews tab "
                    "rather than found by ?q=.",
                    "CORRECTIONS #58 does not apply: no candidate is reached through a category "
                    "listing, so the captured-page-1 / derived-page-2 gap in resolveListing() "
                    "cannot hide one.",
                    "The reward asserts the exact resulting collection, never a count "
                    "(CORRECTIONS #79), and scores product identity rather than a nickname set, "
                    "so the duplicate-content and self-concatenated-nickname classes are "
                    "irrelevant to it.",
                ],
            },
            "initial_setup_path": "initial_setup.py",
        }

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {"eval_types": ["string_match"], "reference_answers": None,
                     "note": "unused - CUA-Gym reward code is authoritative"},
            "cuagym": {"bundle_id": tid, "app_dir": APP,
                       "initial_setup": setup, "eval_reward_code": nreward},
        }}

        open(os.path.join(d, "task_instruction.json"), "w").write(
            json.dumps(instruction, indent=2) + "\n")
        open(os.path.join(d, "task.json"), "w").write(json.dumps(manifest, indent=2) + "\n")
        open(os.path.join(d, "initial_setup.py"), "w").write(setup)
        open(os.path.join(d, "reward.py"), "w").write(reward)
        open(os.path.join(d, "nemo_reward.py"), "w").write(nreward)
        open(os.path.join(d, "nemo_task.json"), "w").write(json.dumps(row, indent=2) + "\n")
        open(os.path.join(BATCH, "replays", tid + ".py"), "w").write(replay_source(task))
        index.append({"task_id": tid, "path": "%s/task.json" % tid})
        rows.append(row)

    open(os.path.join(BATCH, "index.json"), "w").write(
        json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
