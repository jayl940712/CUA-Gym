#!/usr/bin/env python3
"""Batch-6 lane 32 generator — shopping / R5 -> A7.

Chain: derive a fully-seeded category's price spread from its price-sorted
listing, then type that figure into a wish-list row's comment box.

Writes ten bundles into output/tasks/shopping/<task_id>/ plus the batch
GENERATION.md, replay drafts, index.json and nemo_tasks.jsonl under
output/tasks/shopping/_batches/category_spread_wishlist_note/.

Nothing here touches hub/. Ground truth was computed by simulating
resolveListing() over src/data/{products,categories,listings}.json; the
figures are inlined below.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
TASKS = os.path.join(ROOT, "output", "tasks", "shopping")
BATCH = os.path.join(TASKS, "_batches", "category_spread_wishlist_note")
REPLAYS = os.path.join(BATCH, "replays")

APP_DIR = "webarena_shopping_mock"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_URL__"


def money(v):
    return "$%s" % ("{:,.2f}".format(v))


# --------------------------------------------------------------------------
# Lane material. Every category below is one of the 22 fully-seeded ones
# (seeded listable == categories.json dbProductCount), and every one of them
# renders its price minimum AND its price maximum in all nine browsing modes
# checked (default / price asc / price desc x 12 / 24 / 36 per page), so
# CORRECTIONS #58 does not bite. Verified head-of-page-1 identity under both
# price directions at every page size too, which covers the sorted captures of
# CORRECTIONS #61 (heating-cooling and mp3-mp4 are both in that set).
# --------------------------------------------------------------------------

TASKS_SPEC = [
    dict(
        n=1, slug="smartwatches_cheapest_row",
        category="Smartwatches", cat_id=256,
        path="/electronics/wearable-technology/smartwatches.html",
        n_items=56, low=22.49, high=299.00,
        low_runner=23.99, high_runner=249.99,
        target=19328, target_name="Padgene Bluetooth Smartwatch,Touchscreen Wrist Smart Phone Watch Sport",
        target_end="cheapest", mode="add", figure="range",
        style="terse",
        instruction=(
            "Add the cheapest smartwatch in the Smartwatches category to my wish list, "
            "then set that row's comment to the category's price range, formatted "
            "exactly as $low - $high."
        ),
        analogues=["What is the price range for products from ugreen?",
                   "Add a chair to my wish list."],
        setup=None,
    ),
    dict(
        n=2, slug="cakes_priciest_row",
        category="Cakes", cat_id=292,
        path="/grocery-gourmet-food/breads-bakery/cakes.html",
        n_items=69, low=5.19, high=425.88,
        low_runner=9.95, high_runner=215.17,
        target=47973, target_name="Cake Boss Coffee, Italian Rum Cake, 24 Count - SET OF 10",
        target_end="most expensive", mode="add", figure="range",
        style="terse",
        instruction=(
            "Put the most expensive item in Cakes on my wish list and set that row's "
            "comment to the whole category's price range, formatted exactly as "
            "$low - $high."
        ),
        analogues=["What is the price range of Canon photo printer in the One Stop Market?",
                   "Add a laundry detergent to my wish list."],
        setup=None,
    ),
    dict(
        n=3, slug="switch_top_price_on_cheapest_row",
        category="Nintendo Switch", cat_id=71,
        path="/video-games/nintendo-switch.html",
        n_items=51, low=3.66, high=189.00,
        low_runner=4.95, high_runner=139.95,
        target=77531, target_name="Nintendo Switch – OLED Model w/ Neon Red & Neon Blue Joy-Con",
        target_end="cheapest", mode="add", figure="high",
        style="terse",
        instruction=(
            "Add the cheapest Nintendo Switch product to my wish list and set that "
            "row's comment to what the category's most expensive product costs — "
            "the dollar amount and nothing else."
        ),
        analogues=["What is the price range for products from Amazon basic?",
                   "Add a white desk to my wish list."],
        setup=None,
    ),
    dict(
        n=4, slug="patio_furniture_priciest_row",
        category="Patio Furniture & Accessories", cat_id=50,
        path="/patio-lawn-garden/patio-furniture-accessories.html",
        n_items=92, low=17.99, high=3399.00,
        low_runner=23.93, high_runner=1967.25,
        target=36234, target_name="Sorrento 4-Piece L Resin Wicker Outdoor Patio Furniture Conversation Sofa Set",
        target_end="most expensive", mode="add", figure="range",
        style="terse",
        instruction=(
            "Wish-list the priciest item in Patio Furniture & Accessories, then set "
            "that row's comment to the category's price range, formatted exactly as "
            "$low - $high."
        ),
        analogues=["What is the price range for products from EYZUTAK?",
                   "Add a chair to my wish list."],
        setup=None,
    ),
    dict(
        n=5, slug="cell_phones_cheapest_row",
        category="Cell Phones", cat_id=70,
        path="/cell-phones-accessories/cell-phones.html",
        n_items=68, low=1.49, high=1729.00,
        low_runner=7.58, high_runner=979.98,
        target=43211, target_name="TracFone My Flip 2 4G LTE Prepaid Flip Phone (Locked) - Black - 4GB - Single SIM",
        target_end="cheapest", mode="add", figure="range",
        style="explicit",
        instruction=(
            "I want to keep an eye on what phones cost here. Open the Cell Phones "
            "category under Cell Phones & Accessories, work out which listed phone is "
            "the least expensive and which is the most expensive, and add the least "
            "expensive one to my wish list. Then go to My Wish List, type that "
            "category's full price range into that row's comment box as $low - $high "
            "— cheapest first, dearest second, both with a dollar sign and cents "
            "— and press Update Wish List so the note is saved."
        ),
        analogues=["What is the price range of wireless earphone in the One Stop Market?",
                   "Add a toothpaste to my wish list."],
        setup=None,
    ),
    dict(
        n=6, slug="virtual_reality_restated_note",
        category="Virtual Reality", cat_id=247,
        path="/video-games/pc/virtual-reality.html",
        n_items=55, low=2.39, high=1426.65,
        low_runner=7.08, high_runner=331.04,
        target=40622,
        target_name=("VR Link Cable 15ft,Compatible for Qculus Quest 2,Fast Charging & PC Data "
                     "Transfer Cable for VR Headset and Gaming PC"),
        target_end=None, mode="update", figure="range",
        style="terse",
        instruction=(
            "The note on my VR Link Cable wish-list row is out of date. Replace its "
            "comment with the Virtual Reality category's current price range, "
            "formatted exactly as $low - $high."
        ),
        analogues=["What is the price range for products from Perricone MD?",
                   "Add a white computer desk to my wish list."],
        setup=dict(
            rows=[dict(wishlistItemId=1, productId=40622, sku="B09165PG3J",
                       name=("VR Link Cable 15ft,Compatible for Qculus Quest 2,Fast Charging & PC "
                             "Data Transfer Cable for VR Headset and Gaming PC"),
                       price=7.08, qty=1,
                       description="range last checked before the summer sale - recheck",
                       addedAt="2023-04-18 11:07:52")],
            next_id=2,
            why=[
                "wishlist.items = one saved row, wishlistItemId 1 = product 40622 "
                "(VR Link Cable 15ft, $7.08, catalog sku B09165PG3J), carrying a stale "
                "free-text comment that names no figure, so the row's comment box "
                "renders and the rubric is not pre-satisfied.",
                "nextWishlistItemId = 2, so any later addToWishlist cannot mint a "
                "duplicate wishlistItemId.",
            ],
        ),
    ),
    dict(
        n=7, slug="heating_cooling_alongside_cake_note",
        category="Heating, Cooling & Air Quality", cat_id=43,
        path="/home-kitchen/heating-cooling-air-quality.html",
        n_items=85, low=1.07, high=2376.95,
        low_runner=3.02, high_runner=2299.00,
        target=13510,
        target_name="HOMCOM 43 Inch Wall-Mounted Stainless Steel Ventless Ethanol Fireplace",
        target_end="cheapest", mode="add", figure="range",
        style="terse",
        extra_ids=[90260],
        instruction=(
            "Add the cheapest item in Heating, Cooling & Air Quality to my wish list "
            "and set that row's comment to the category's price range, formatted "
            "exactly as $low - $high."
        ),
        analogues=["What is the price range of teeth grinding mouth guard in the One Stop Market?",
                   "Add a laundry detergent to my wish list."],
        setup=dict(
            rows=[dict(wishlistItemId=1, productId=90260, sku="B001DIH3A8",
                       name=("Katz Gluten Free Marble Loaf | Dairy Free, Nut Free, Soy Free, "
                             "Gluten Free | Kosher (1 Pack of 1 Loaf, 12 Ounce)"),
                       price=5.19, qty=1,
                       description="for the weekend bake",
                       addedAt="2023-05-02 08:44:19")],
            next_id=2,
            why=[
                "wishlist.items = one unrelated saved row, wishlistItemId 1 = product "
                "90260 (Katz Gluten Free Marble Loaf, $5.19), with its own short comment. "
                "It is a distractor: the wish-list page now renders two comment boxes and "
                "the agent must annotate the derived one.",
                "nextWishlistItemId = 2, so the product the agent adds takes "
                "wishlistItemId 2 and no id collides.",
            ],
        ),
    ),
    dict(
        n=8, slug="deli_floor_price_on_priciest_row",
        category="Deli Meats & Cheeses", cat_id=273,
        path="/grocery-gourmet-food/deli-prepared-foods/deli-meats-cheeses.html",
        n_items=36, low=6.51, high=199.99,
        low_runner=11.67, high_runner=110.25,
        target=47884,
        target_name="Serrano Ham Bone in from Spain 14.7 - 17 lb + Ham Stand + Knife - Cured Jamon",
        target_end="most expensive", mode="add", figure="low",
        style="terse",
        instruction=(
            "Wish-list the most expensive item in Deli Meats & Cheeses and set that "
            "row's comment to what the cheapest product in the same category costs "
            "— the dollar amount and nothing else."
        ),
        analogues=["What is the price range for products from sephora?",
                   "Add a chair to my wish list."],
        setup=None,
    ),
    dict(
        n=9, slug="pots_planters_restated_note",
        category="Pots, Planters & Container Accessories", cat_id=191,
        path="/patio-lawn-garden/gardening-lawn-care/pots-planters-container-accessories.html",
        n_items=80, low=8.99, high=197.52,
        low_runner=10.99, high_runner=183.95,
        target=86651, target_name="Elho Loft Urban Round High 42 Cherry Planter",
        target_end=None, mode="update", figure="range",
        style="explicit",
        instruction=(
            "My wish list already holds an Elho Loft Urban planter, and the comment on "
            "it is stale. Open Pots, Planters & Container Accessories under Patio, Lawn "
            "& Garden, find the cheapest and the most expensive product listed in that "
            "category, then go to My Wish List and replace that row's comment with the "
            "category's price range written as $low - $high — cheapest first, "
            "dearest second, both with a dollar sign and cents. Press Update Wish List "
            "to save it."
        ),
        analogues=["What is the price range for products from Amazon basic?",
                   "Add a white desk to my wish list."],
        setup=dict(
            rows=[dict(wishlistItemId=1, productId=86651, sku="B00BCY7GAU",
                       name="Elho Loft Urban Round High 42 Cherry Planter",
                       price=28.17, qty=1,
                       description="stale note - prices moved since I saved this",
                       addedAt="2023-03-27 16:02:40")],
            next_id=2,
            why=[
                "wishlist.items = one saved row, wishlistItemId 1 = product 86651 "
                "(Elho Loft Urban Round High 42 Cherry Planter, $28.17, sku B00BCY7GAU), "
                "a mid-priced member of the target category so its own price is neither "
                "end of the spread. Its comment is stale prose carrying no figure.",
                "nextWishlistItemId = 2.",
            ],
        ),
    ),
    dict(
        n=10, slug="mp3_accessories_top_price",
        category="MP3 & MP4 Player Accessories", cat_id=255,
        path="/electronics/portable-audio-video/mp3-mp4-player-accessories.html",
        n_items=54, low=0.99, high=585.40,
        low_runner=6.49, high_runner=499.00,
        target=19698,
        target_name="hudiemm0B Car Cassette Audio Converter, 3.5mm Jack Car AUX Cassette Tape Adapter",
        target_end="cheapest", mode="add", figure="high",
        style="terse",
        instruction=(
            "Add the cheapest MP3 & MP4 Player Accessories item to my wish list, then "
            "set that row's comment to the price of the category's most expensive item "
            "— the dollar amount and nothing else."
        ),
        analogues=["What is the price range for products from EYZUTAK?",
                   "Add a toothpaste to my wish list."],
        setup=None,
    ),
]


# --------------------------------------------------------------------------
# shared reward body
# --------------------------------------------------------------------------

REWARD_BODY = '''
import re
from decimal import Decimal, InvalidOperation

# A money token is either a dollar-prefixed number or a bare number written to
# two decimal places, so "15 ft" pasted out of a product name does not register
# as an amount and a bare year cannot either.
_MONEY_RE = re.compile(r"\\$\\s*\\d[\\d,]*(?:\\.\\d+)?|\\d[\\d,]*\\.\\d{2}")


def _amounts(text):
    """Money figures in the order they appear in the note."""
    found = []
    if not isinstance(text, str):
        return found
    for raw in _MONEY_RE.findall(text):
        cleaned = raw.replace("$", "").replace(",", "").strip()
        try:
            found.append(Decimal(cleaned))
        except (InvalidOperation, ValueError):
            continue
    return found


def _wishlist_rows(state):
    if not isinstance(state, dict):
        return []
    wishlist = state.get("wishlist")
    items = wishlist.get("items") if isinstance(wishlist, dict) else None
    if not isinstance(items, list):
        return []
    return [row for row in items if isinstance(row, dict)]


def _int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if float(value).is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        try:
            number = float(text)
        except ValueError:
            return None
        return int(number) if number.is_integer() else None
    return None


def _product_ids(state):
    found = set()
    for row in _wishlist_rows(state):
        product_id = _int(row.get("productId"))
        if product_id is not None:
            found.add(product_id)
    return found


def _note(state, product_id):
    for row in _wishlist_rows(state):
        if _int(row.get("productId")) == product_id:
            text = row.get("description")
            if isinstance(text, str) and text.strip():
                return text
            return None
    return None
'''


def reward_constants(spec):
    amounts = expected_amounts(spec)
    ids = expected_ids(spec)
    c1, c2 = component_names(spec)
    lines = []
    lines.append("COMPONENT_WEIGHTS = {")
    lines.append('    "%s": 0.4,' % c1)
    lines.append('    "%s": 0.6,' % c2)
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    lines.append("")
    lines.append("TARGET_PRODUCT_ID = %d" % spec["target"])
    lines.append("EXPECTED_AMOUNTS = [%s]" % ", ".join(
        'Decimal("%s")' % ("{:.2f}".format(a)) for a in amounts))
    lines.append("EXPECTED_PRODUCT_IDS = {%s}" % ", ".join(str(i) for i in sorted(ids)))
    lines.append("")
    lines.append("")
    lines.append("def _checks(state):")
    lines.append("    note = _note(state, TARGET_PRODUCT_ID)")
    lines.append("    amounts_ok = note is not None and _amounts(note) == EXPECTED_AMOUNTS")
    lines.append("    collection_ok = _product_ids(state) == EXPECTED_PRODUCT_IDS")
    lines.append("    results = {}")
    if spec["mode"] == "add":
        lines.append('    results["%s"] = collection_ok' % c1)
    else:
        lines.append('    results["%s"] = amounts_ok' % c1)
    lines.append('    results["%s"] = amounts_ok and collection_ok' % c2)
    lines.append("    return results")
    return "\n".join(lines)


def expected_amounts(spec):
    if spec["figure"] == "range":
        return [spec["low"], spec["high"]]
    if spec["figure"] == "high":
        return [spec["high"]]
    return [spec["low"]]


def expected_ids(spec):
    ids = set(spec.get("extra_ids") or [])
    ids.add(spec["target"])
    return ids


def component_names(spec):
    stem = spec["slug"]
    if spec["mode"] == "add":
        return ("wishlist_now_holds_the_derived_%s" % stem,
                "%s_figure_recorded_in_that_comment" % stem)
    return ("%s_figure_typed_into_the_saved_row" % stem,
            "wishlist_now_exactly_that_annotated_row" % ())


def figure_text(spec):
    if spec["figure"] == "range":
        return "%s - %s" % (money(spec["low"]), money(spec["high"]))
    if spec["figure"] == "high":
        return money(spec["high"])
    return money(spec["low"])


def figure_phrase(spec):
    if spec["figure"] == "range":
        return ("the %s price range %s (cheapest of %d listed products, dearest of them)"
                % (spec["category"], figure_text(spec), spec["n_items"]))
    if spec["figure"] == "high":
        return ("the highest price in %s, %s" % (spec["category"], figure_text(spec)))
    return ("the lowest price in %s, %s" % (spec["category"], figure_text(spec)))


def success_criteria(spec):
    ids = sorted(expected_ids(spec))
    id_text = ", ".join(str(i) for i in ids)
    amounts = ", ".join(money(a) for a in expected_amounts(spec))
    if spec["mode"] == "add":
        first = ("The wish list holds exactly the product ids %s, so the row the agent saved "
                 "is product %d (%s) — the %s of the %d products listed in %s."
                 % (id_text, spec["target"], spec["target_name"], spec["target_end"],
                    spec["n_items"], spec["category"]))
    else:
        first = ("The comment on the wish-list row for product %d (%s) reads the money "
                 "figures %s in that order — %s."
                 % (spec["target"], spec["target_name"], amounts, figure_phrase(spec)))
    second = ("The comment on the wish-list row for product %d carries exactly the money "
              "figures %s in that order, and the wish list holds exactly the product ids %s."
              % (spec["target"], amounts, id_text))
    return [first, second]


def docstring(task_id, spec):
    crit = success_criteria(spec)
    return (
        '"""Deterministic reward for %s.\n\n'
        'Success criteria:\n'
        '  * %s\n'
        '  * %s\n\n'
        'Ground truth is the price spread of the fully-seeded %s category\n'
        '(%d listable products, seeded count == categories.json dbProductCount):\n'
        'minimum %s (runner-up %s), maximum %s (runner-up %s). Both ends render in\n'
        'every browsing mode checked, and the catalog is a frozen ES import with no\n'
        'state overlay, so the figures cannot move mid-episode.\n\n'
        'Scoring reads current_state only, never a diff against initial_state, so an\n'
        'empty current_state scores 0.0 on every component.\n'
        '"""\n'
        % (task_id, crit[0], crit[1], spec["category"], spec["n_items"],
           money(spec["low"]), money(spec["low_runner"]),
           money(spec["high"]), money(spec["high_runner"]))
    )


EVAL_TAIL = '''


def _app(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app
    return {}


def evaluate(evidence):
    app = _app(evidence)
    state = app.get("current_state") if isinstance(app.get("current_state"), dict) else {}
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


def build_reward(task_id, spec):
    return docstring(task_id, spec) + REWARD_BODY + "\n\n" + reward_constants(spec) + EVAL_TAIL


def build_nemo_reward(task_id, spec):
    head = (
        '"""NeMo-Gym reward program for %s.\n\n'
        'Implements exactly the rubric of reward.py, reading current_state from\n'
        'GET /go?sid=... instead of a frozen evidence bundle, and printing\n'
        'REWARD: <float> on every output path including the error path.\n\n'
        'Self-contained: standard library plus requests, which is present in\n'
        'cuagym/requirements.txt.\n'
        '"""\n\n'
        'import sys\n\n'
        'import requests\n'
        % task_id
    )
    consts = (
        '\nSID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n\n' % PLACEHOLDER
    )
    return head + REWARD_BODY + "\n" + consts + reward_constants(spec) + NEMO_TAIL


def build_setup(task_id, spec):
    setup = spec["setup"]
    rows = json.dumps(setup["rows"], indent=1)
    return (
        '"""NeMo-Gym setup program for %s.\n\n'
        'Pre-seeds the wish list so the free-text comment box that\n'
        'WishlistPage.jsx:76-82 renders per row exists before the episode opens.\n'
        'The pristine data/wishlist.json is an empty items array, and the page\n'
        'emits no form, no textarea and no Update button at all while the list is\n'
        'empty.\n\n'
        'The pristine session document is read back from GET /go?sid= first and the\n'
        'patched document is POSTed whole, so no top-level key is dropped. The\n'
        'inlined fixture is a raw string literal, so no escape is eaten by the\n'
        'Python parser before the JSON decoder sees it.\n\n'
        'Self-contained: standard library plus requests, which is present in\n'
        'cuagym/requirements.txt.\n'
        '"""\n\n'
        'import json\n'
        'import sys\n\n'
        'import requests\n\n'
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n\n'
        'INJECTED_WISHLIST = json.loads(r"""\n%s\n""")\n\n'
        'NEXT_WISHLIST_ITEM_ID = %d\n\n\n'
        'def main():\n'
        '    read = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)\n'
        '    read.raise_for_status()\n'
        '    payload = read.json()\n'
        '    state = payload.get("current_state")\n'
        '    if not isinstance(state, dict) or not state:\n'
        '        state = payload.get("initial_state")\n'
        '    if not isinstance(state, dict):\n'
        '        print("SETUP FAILED: no session document to patch", file=sys.stderr)\n'
        '        raise SystemExit(1)\n'
        '    state = json.loads(json.dumps(state))\n'
        '    state["wishlist"] = {"items": INJECTED_WISHLIST}\n'
        '    state["nextWishlistItemId"] = NEXT_WISHLIST_ITEM_ID\n'
        '    written = requests.post(\n'
        '        BASE_URL + "/post?sid=" + SID,\n'
        '        json={"action": "set", "state": state},\n'
        '        timeout=60,\n'
        '    )\n'
        '    written.raise_for_status()\n'
        '    print("SETUP OK")\n\n\n'
        'main()\n'
        % (task_id, PLACEHOLDER, rows, setup["next_id"])
    )


def skill_chain(spec):
    if spec["mode"] == "add":
        return ("sort the %s category listing by price to read its cheapest and dearest "
                "rows -> save the %s one to the wish list and type %s into that row's "
                "comment box, then press Update Wish List"
                % (spec["category"], spec["target_end"], figure_text(spec)))
    return ("sort the %s category listing by price to read its cheapest and dearest rows "
            "-> retype the saved wish-list row's comment as %s and press Update Wish List"
            % (spec["category"], figure_text(spec)))


def authoring_notes(spec):
    notes = [
        ("Ground truth recomputed from src/data/products.json by simulating "
         "resolveListing(): %s holds %d listable products, minimum %s (runner-up %s, "
         "margin %s) and maximum %s (runner-up %s, margin %s). Both extremes are unique "
         "— exactly one product at each price."
         % (spec["category"], spec["n_items"], money(spec["low"]), money(spec["low_runner"]),
            money(spec["low_runner"] - spec["low"]), money(spec["high"]),
            money(spec["high_runner"]), money(spec["high"] - spec["high_runner"]))),
        ("Reachability re-checked against CORRECTIONS #58: both extreme products render "
         "in all nine browsing modes (default / price asc / price desc at 12, 24 and 36 "
         "per page) on %s, and page 1 under price asc/desc leads with the minimum/maximum "
         "at every page size, so the captured-listing branch of resolveListing agrees "
         "with the derived pool here." % spec["path"]),
        ("The instruction never names a price, so an agent that skips the listing "
         "retrieval cannot write the comment; both reward components depend on a "
         "derived value or a derived product, so a skipper scores 0.0."),
    ]
    if spec["mode"] == "update":
        notes.append(
            "The injected comment is prose with no digits in it, so the untouched "
            "injected state scores 0.0 and nothing in the rubric is pre-satisfied.")
    if spec.get("extra_ids"):
        notes.append(
            "The pre-seeded row is a distractor from an unrelated category; the rubric "
            "states the resulting collection positively, so deleting it to simplify the "
            "page costs 1.0 rather than being rewarded.")
    return notes


def build_task_json(task_id, spec):
    apps = [{
        "name": APP_DIR,
        "source_name": "shopping",
        "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_URL",
        "start_path": "/",
        "initial_state": None,
        "golden_state": None,
    }]
    meta = {
        "style": spec["style"],
        "difficulty": "medium",
        "shape": "retrieval_writeback",
        "skills": ["R5", "A7"],
        "skill_chain": skill_chain(spec),
        "derived_from": "price_range_into_wishlist_note",
        "official_analogues": spec["analogues"],
        "topic": "category_spread_wishlist_note",
        "batch": "batch-6 lane 32 (shopping / R5 -> A7)",
        "lane": "category_spread_wishlist_note",
        "inspiration_ids": ["webarena-226", "webarena-229", "webarena-513"],
        "authoring_notes": authoring_notes(spec),
        "injected_preconditions": (spec["setup"]["why"] if spec["setup"] else []),
    }
    return {
        "schema_version": 2,
        "task_id": task_id,
        "instruction": spec["instruction"],
        "apps": apps,
        "reward_path": "reward.py",
        "requirements_path": None,
        "evidence": [],
        "source_evaluator": {},
        "source": "webarena",
        "metadata": meta,
    }


def build_replay(task_id, spec):
    figure = figure_text(spec)
    direction = "descending" if spec.get("target_end") == "most expensive" else "ascending"
    toggle = "yes" if direction == "descending" else "no"
    return (
        '"""Golden replay draft for %s.\n\n'
        'Click path, no typed URLs after the landing page:\n'
        '  1. land on "/"\n'
        '  2. nav band -> %s (%s)\n'
        '  3. Sort By select#sorter -> "price"; toggle a[data-role="direction-switcher"]\n'
        '     to reach %s order (needed here: %s). The control advertises the direction\n'
        '     it will switch TO, so assert on the rendered price column, never on the\n'
        '     control label.\n'
        '  4. read the first tile of the price-ascending page (%s) and of the\n'
        '     price-descending page (%s)\n'
        '  5. %s\n'
        '  6. header link "My Wish List"\n'
        '  7. fill textarea.product-item-comment on that row with "%s"\n'
        '  8. click button.action.update.primary ("Update Wish List")\n'
        '"""\n\n'
        'FIGURE = "%s"\n'
        'CATEGORY = "%s"\n'
        'CATEGORY_PATH = "%s"\n'
        'TARGET_PRODUCT_ID = %d\n'
        'TARGET_PRODUCT_NAME = "%s"\n\n\n'
        'def run(page):\n'
        '    """Draft only — golden-browser owns the final selectors."""\n'
        '    raise NotImplementedError("replay draft")\n'
        % (task_id, spec["category"], spec["path"], direction, toggle,
           money(spec["low"]), money(spec["high"]),
           ("tile action a.towishlist on the %s row (product %d)"
            % (spec["target_end"], spec["target"])) if spec["mode"] == "add"
           else "the row is already on the wish list — nothing to add",
           figure, figure, spec["category"], spec["path"], spec["target"],
           spec["target_name"].replace('"', '\\"'))
    )


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = []
    nemo_rows = []
    for spec in TASKS_SPEC:
        task_id = "category_spread_wishlist_note_%s_%03d" % (spec["slug"], spec["n"])
        bundle = os.path.join(TASKS, task_id)
        os.makedirs(bundle, exist_ok=True)

        reward = build_reward(task_id, spec)
        nemo_reward = build_nemo_reward(task_id, spec)
        setup_src = build_setup(task_id, spec) if spec["setup"] else None

        with open(os.path.join(bundle, "reward.py"), "w") as fh:
            fh.write(reward)
        with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
            fh.write(nemo_reward)
        if setup_src is not None:
            with open(os.path.join(bundle, "initial_setup.py"), "w") as fh:
                fh.write(setup_src)

        ti = {
            "task_id": task_id,
            "task_instruction": spec["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success_criteria(spec),
        }
        with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
            json.dump(ti, fh, indent=2)
            fh.write("\n")

        task = build_task_json(task_id, spec)
        with open(os.path.join(bundle, "task.json"), "w") as fh:
            json.dump(task, fh, indent=2)
            fh.write("\n")

        row = {
            "task_payload": {
                "task_id": task_id,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": [APP_DIR],
                "start_urls": [],
                "intent": spec["instruction"],
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": task_id,
                    "app_dir": APP_DIR,
                    "initial_setup": setup_src,
                    "eval_reward_code": nemo_reward,
                },
            }
        }
        with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
            json.dump(row, fh, indent=2)
            fh.write("\n")
        nemo_rows.append(row)

        with open(os.path.join(REPLAYS, task_id + ".py"), "w") as fh:
            fh.write(build_replay(task_id, spec))

        index.append({"task_id": task_id, "path": "../../%s/task.json" % task_id})

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({"schema_version": 2, "tasks": index}, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")
    print("wrote %d bundles" % len(index))


main()
