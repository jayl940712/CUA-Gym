#!/usr/bin/env python3
"""Batch-6 lane 50 generator - shopping_admin, R6 -> A5.

Chain: find the reviewed product by searching review CONTENT (the Review column
filter on Marketing > User Content > All Reviews, LegacyReviewGrid.jsx:160 via
`contains`, case-insensitive substring on `detail`), then apply a stated
percentage to the price of one size row or one colour column of that product's
variant run.

Writes ten bundles under output/tasks/shopping_admin/<task_id>/ plus the lane
GENERATION.md and one golden-replay draft per task.

Run:  python3 scripts/_b6_lane50_gen.py
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "output" / "tasks" / "shopping_admin"
BATCH = TASKS / "_batches" / "variant_run_pct_reprice"
REPLAYS = BATCH / "replays"

APP_DIR = "webarena_shopping_admin_mock"
PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

ANALOGUE_PRICE_PCT = "Reduce the price of size 28 Sahara leggings of all colors by 13.5%"
ANALOGUE_PRICE_PCT2 = "Increase the price of all blue running tshirts in extra small and small sizes by 23%"
ANALOGUE_PRICE_ABS = "Reduce the price of green Hollister backyard sweatshirt in all sizes by $5"
ANALOGUE_PRICE_ABS2 = "Increase the price of white Ingrid Running with size L and above by $17"
ANALOGUE_REVIEW_TERM = (
    'Tell me the the number of reviews that our store received by far that mention term "disappointed"'
)
ANALOGUE_REVIEW_MENTION = (
    "Get name(s) of reviewer(s) who mention ear cups being small for the product on the current page"
)

INSPIRATION_IDS = ["webarena-777", "webarena-778", "webarena-780", "webarena-563", "webarena-599"]


# --------------------------------------------------------------------------
# Seed facts, all read out of hub/websites/webarena_shopping_admin_mock/src/data
# at authoring time. `family` holds every member of the configurable line -
# the parent and every child - with its seeded price.
# --------------------------------------------------------------------------

TASKS_SPEC = [
    {
        "n": 1,
        "slug": "helios_blue_column",
        "search_hits": 16,
        "sku": "MS05",
        "product": "Helios EverCool(TM) Tee",
        "parent": 462,
        "base": "24.00",
        "pct": "-12.5",
        "new": "21.00",
        "run_label": "the Blue colour column (all five sizes)",
        "run": [(448, "MS05-XS-Blue"), (451, "MS05-S-Blue"), (454, "MS05-M-Blue"),
                (457, "MS05-L-Blue"), (460, "MS05-XL-Blue")],
        "rest": [447, 449, 450, 452, 453, 455, 456, 458, 459, 461, 462],
        "review_id": 77,
        "phrase": "look like I got stuck in the rain",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "One approved customer review praises not looking \"like I got stuck in the rain\". "
            "Find the product that review is on and cut every Blue variant of it by 12.5%, "
            "rounded to the nearest cent."
        ),
        "distractor": {
            "sku": "MS07",
            "product_name": "Deion Long-Sleeve EverCool&trade; Tee",
            "title": "Dry after a downpour session",
            "detail": (
                "Ran six miles in a drizzle and still felt dry underneath. I did not end up soaked "
                "the way I do in cotton, so nobody could tell I had been out in the rain at all."
            ),
            "nickname": "Roselyn",
            "value": 4,
        },
    },
    {
        "n": 2,
        "slug": "antonia_size_m_uplift",
        "search_hits": 16,
        "sku": "WT08",
        "product": "Antonia Racer Tank",
        "parent": 1796,
        "base": "34.00",
        "pct": "+5",
        "new": "35.70",
        "run_label": "the size M row (all three colours)",
        "run": [(1787, "WT08-M-Black"), (1788, "WT08-M-Purple"), (1789, "WT08-M-Yellow")],
        "rest": [1781, 1782, 1783, 1784, 1785, 1786, 1790, 1791, 1792, 1793, 1794, 1795, 1796],
        "review_id": 337,
        "phrase": "zero support and absolutely no modesty",
        "style": "terse",
        "shape": "derived_set_mutation",
        "instruction": (
            "A customer review complains of \"zero support and absolutely no modesty\". "
            "Take the reviewed product's size M variants up 5% in every colour, "
            "rounded to the nearest cent."
        ),
        "distractor": None,
    },
    {
        "n": 3,
        "slug": "miko_size_xl_markdown",
        "search_hits": 16,
        "sku": "WH04",
        "product": "Miko Pullover Hoodie",
        "parent": 1092,
        "base": "69.00",
        "pct": "-10",
        "new": "62.10",
        "run_label": "the size XL row (all three colours)",
        "run": [(1089, "WH04-XL-Blue"), (1090, "WH04-XL-Orange"), (1091, "WH04-XL-Purple")],
        "rest": [1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1092],
        "review_id": 194,
        "phrase": "Can you please make this with long sleeves",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "A reviewer asks \"Can you please make this with long sleeves\". "
            "Mark that product's size XL variants down 10% in every colour, "
            "rounded to the nearest cent."
        ),
        "distractor": None,
    },
    {
        "n": 4,
        "slug": "kratos_size34_clearance",
        "search_hits": 13,
        "sku": "MP05",
        "product": "Kratos Gym Pant",
        "parent": 789,
        "base": "57.00",
        "pct": "-20",
        "new": "45.60",
        "run_label": "the size 34 row (all three colours)",
        "run": [(783, "MP05-34-Black"), (784, "MP05-34-Blue"), (785, "MP05-34-Green")],
        "rest": [777, 778, 779, 780, 781, 782, 786, 787, 788, 789],
        "review_id": 66,
        "phrase": "more like half a draw string",
        "style": "terse",
        "shape": "derived_set_mutation",
        "instruction": (
            "A review grumbles that the drawstring is \"more like half a draw string\". "
            "Clear that product's size 34 run out: 20% off all three colours, "
            "rounded to the nearest cent."
        ),
        "distractor": None,
    },
    {
        "n": 5,
        "slug": "radiant_orange_uplift",
        "search_hits": 16,
        "sku": "WS12",
        "product": "Radiant Tee",
        "parent": 1556,
        "base": "22.00",
        "pct": "+25",
        "new": "27.50",
        "run_label": "the Orange colour column (all five sizes)",
        "run": [(1542, "WS12-XS-Orange"), (1545, "WS12-S-Orange"), (1548, "WS12-M-Orange"),
                (1551, "WS12-L-Orange"), (1554, "WS12-XL-Orange")],
        "rest": [1541, 1543, 1544, 1546, 1547, 1549, 1550, 1552, 1553, 1555, 1556],
        "review_id": 281,
        "phrase": "buttons are too small and hurt my fingers",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "A review says the \"buttons are too small and hurt my fingers\". "
            "Put every Orange variant of that product up 25%, all sizes, "
            "rounded to the nearest cent."
        ),
        "distractor": {
            "sku": "WS02",
            "product_name": "Gabrielle Micro Sleeve Top",
            "title": "Fiddly in cold weather",
            "detail": (
                "Lovely drape and the fabric washes well. My one gripe is the placket: the buttons "
                "are too small for me to manage once my hands are cold after an early run."
            ),
            "nickname": "Corrine",
            "value": 3,
        },
    },
    {
        "n": 6,
        "slug": "lando_size_l_markdown",
        "search_hits": 16,
        "sku": "MJ08",
        "product": "Lando Gym Jacket",
        "parent": 334,
        "base": "99.00",
        "pct": "-20",
        "new": "79.20",
        "run_label": "the size L row (all three colours)",
        "run": [(328, "MJ08-L-Blue"), (329, "MJ08-L-Gray"), (330, "MJ08-L-Green")],
        "rest": [319, 320, 321, 322, 323, 324, 325, 326, 327, 331, 332, 333, 334],
        "review_id": 47,
        "phrase": "easy to take apart when you want to wear the quilted part",
        "style": "terse",
        "shape": "derived_set_mutation",
        "instruction": (
            "One review calls a product \"easy to take apart when you want to wear the quilted part\". "
            "Take 20% off its size L variants in all colours, rounded to the nearest cent."
        ),
        "distractor": None,
    },
    {
        "n": 7,
        "slug": "electra_gray_column",
        "search_hits": 17,
        "sku": "WB01",
        "product": "Electra Bra Top",
        "parent": 1604,
        "base": "39.00",
        "pct": "-10",
        "new": "35.10",
        "run_label": "the Gray colour column (all five sizes)",
        "run": [(1590, "WB01-XS-Gray"), (1593, "WB01-S-Gray"), (1596, "WB01-M-Gray"),
                (1599, "WB01-L-Gray"), (1602, "WB01-XL-Gray")],
        "rest": [1589, 1591, 1592, 1594, 1595, 1597, 1598, 1600, 1601, 1603, 1604],
        "review_id": 317,
        "phrase": "no irritation or chafing",
        "style": "terse",
        "shape": "retrieval_writeback",
        "instruction": (
            "A customer review reports \"no irritation or chafing\". "
            "Discount every Gray variant of that product by 10%, all sizes, "
            "rounded to the nearest cent."
        ),
        "distractor": {
            "sku": "WB03",
            "product_name": "Celeste Sports Bra",
            "title": "Held up over ten miles",
            "detail": (
                "Wore this for a ten mile trail run in humid weather and there was no chafing at all, "
                "even under a pack strap. Sizing runs a touch small, so order up."
            ),
            "nickname": "Marguerita",
            "value": 5,
        },
    },
    {
        "n": 8,
        "slug": "hawkeye_size33_uplift",
        "search_hits": 13,
        "sku": "MSH05",
        "product": "Hawkeye Yoga Short",
        "parent": 937,
        "base": "29.00",
        "pct": "+10",
        "new": "31.90",
        "run_label": "the size 33 row (all three colours)",
        "run": [(928, "MSH05-33-Black"), (929, "MSH05-33-Blue"), (930, "MSH05-33-Gray")],
        "rest": [925, 926, 927, 931, 932, 933, 934, 935, 936, 937],
        "review_id": 112,
        "phrase": "weird toes",
        "style": "terse",
        "shape": "derived_set_mutation",
        "instruction": (
            "A reviewer dislikes the \"weird toes\" on one of our products. "
            "Raise that product's size 33 variants by 10% across all three colours, "
            "rounded to the nearest cent."
        ),
        "distractor": None,
    },
    {
        "n": 9,
        "slug": "juno_size_s_markdown",
        "search_hits": 16,
        "sku": "WJ06",
        "product": "Juno Jacket",
        "parent": 1380,
        "base": "77.00",
        "pct": "-15",
        "new": "65.45",
        "run_label": "the size S row (all three colours)",
        "run": [(1368, "WJ06-S-Blue"), (1369, "WJ06-S-Green"), (1370, "WJ06-S-Purple")],
        "rest": [1365, 1366, 1367, 1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380],
        "review_id": 218,
        "phrase": "it blocks the wind",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "instruction": (
            "Merchandising is running a markdown off the back of customer feedback. Open Marketing > "
            "User Content > All Reviews and filter the Review column on the phrase \"it blocks the wind\" "
            "to work out which product the reviewer meant - the instruction deliberately does not name it. "
            "Then, in Catalog > Products, reduce the price of that product's size S variants - all three "
            "colours - by 15% off what they sell for today, rounded to the nearest cent, half up. Every "
            "other size of that line, and the configurable parent, must still sell at its current price."
        ),
        "distractor": {
            "sku": "WJ10",
            "product_name": "Nadia Elements Shell",
            "title": "Good on an exposed ridge",
            "detail": (
                "Took this up an exposed ridge in March. It blocks wind and light rain nicely and packs "
                "down to nothing, though the hood is a little shallow for a helmet."
            ),
            "nickname": "Delmar",
            "value": 4,
        },
    },
    {
        "n": 10,
        "slug": "strike_black_column",
        "search_hits": 16,
        "sku": "MS08",
        "product": "Strike Endurance Tee",
        "parent": 622,
        "base": "39.00",
        "pct": "+20",
        "new": "46.80",
        "run_label": "the Black colour column (all five sizes)",
        "run": [(607, "MS08-XS-Black"), (610, "MS08-S-Black"), (613, "MS08-M-Black"),
                (616, "MS08-L-Black"), (619, "MS08-XL-Black")],
        "rest": [608, 609, 611, 612, 614, 615, 617, 618, 620, 621, 622],
        "review_id": 88,
        "phrase": "revealing my bra",
        "style": "explicit",
        "shape": "retrieval_writeback",
        "instruction": (
            "A supplier price rise has to be passed on, and the buying team picked the line by customer "
            "feedback rather than by name. In Marketing > User Content > All Reviews, filter the Review "
            "column on the phrase \"revealing my bra\" to identify the product. Then, in Catalog > "
            "Products, increase the price of that product's Black variants - every size - by 20% over "
            "what they sell for now, rounded to the nearest cent, half up. The other colours of that "
            "line and the configurable parent keep the price they have."
        ),
        "distractor": {
            "sku": "MS01",
            "product_name": "Aero Daily Fitness Tee",
            "title": "Sheer when it gets wet",
            "detail": (
                "Fine for the gym but it turns sheer and revealing once you have sweated through it, "
                "so I keep it for solo sessions and wear the darker colour to class."
            ),
            "nickname": "Odell",
            "value": 2,
        },
    },
]

# Product entity ids for the distractor targets, from src/data/products.json.
DISTRACTOR_PRODUCT_IDS = {
    "MS07": 606,
    "WS02": 1412,
    "WB03": 1636,
    "WJ10": 1348,
    "MS01": 558,
}

RATING_OPTION = {1: 16, 2: 17, 3: 18, 4: 19, 5: 20}


def money(text: str) -> float:
    return float(Decimal(text))


def component_key(sku: str, price: str) -> str:
    return "%s_at_%s" % (sku.lower().replace("-", "_"), price.replace(".", "_"))


def weights_for(count: int) -> list:
    if count == 3:
        return [0.34, 0.33, 0.33]
    if count == 5:
        return [0.2, 0.2, 0.2, 0.2, 0.2]
    raise SystemExit("unexpected run size %d" % count)


def build_reward_tables(spec):
    run = spec["run"]
    weights = weights_for(len(run))
    new_price = money(spec["new"])
    base_price = money(spec["base"])
    comp_weights, comp_targets, comp_details = {}, {}, {}
    for (pid, sku), weight in zip(run, weights):
        key = component_key(sku, spec["new"])
        comp_weights[key] = weight
        comp_targets[key] = {str(pid): {"price": new_price}}
        comp_details[key] = (
            "product %d (%s) price == %s, and no other member of the %s line moved"
            % (pid, sku, spec["new"], spec["sku"])
        )
    seed_rows = {}
    for pid, _sku in run:
        seed_rows[str(pid)] = {"price": base_price}
    scope = {}
    for pid in spec["rest"]:
        seed_rows[str(pid)] = {"price": base_price}
        scope[str(pid)] = {"price": base_price}
    return comp_weights, comp_targets, comp_details, seed_rows, scope


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
    (selectors.js:164-179), and the Price column renders exactly that merged
    value (ProductGrid.jsx:167-173). A deleted row returns the DELETED sentinel
    and can never satisfy a component.
    """
    key = str(product_id)
    if int(key) in _deleted(state):
        return DELETED
    override = _as_dict(_as_dict(_as_dict(state).get("productOverrides")).get(key))
    if field in override:
        return _num(override.get(field))
    return _num(_as_dict(SEED_ROWS.get(key)).get(field))


def _matches(state, wanted):
    for product_id, fields in wanted.items():
        for field, value in fields.items():
            got = _field(state, product_id, field)
            if got is DELETED or got is None:
                return False
            if abs(got - float(value)) > 1e-6:
                return False
    return True


def _scope_ok(state):
    """Every line member outside the run still sells at its seeded price.

    This earns no credit of its own; it only gates the outcome components, so an
    agent that repriced the whole line scores zero rather than being paid for
    restraint (CORRECTIONS #84/#110).
    """
    for product_id, fields in SCOPE.items():
        for field, value in fields.items():
            got = _field(state, product_id, field)
            if got is DELETED or got is None:
                return False
            if abs(got - float(value)) > 1e-6:
                return False
    return True


def score_state(state):
    in_scope = _scope_ok(state)
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = in_scope and _matches(state, COMPONENT_TARGETS[name])
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": COMPONENT_DETAILS[name],
        })
    return round(sum(c["score"] for c in components), 6), components
'''


def reward_header(spec, comp_weights, comp_targets, comp_details, seed_rows, scope):
    return "".join([
        "COMPONENT_WEIGHTS = json.loads(r\"\"\"%s\"\"\")\n" % json.dumps(comp_weights, indent=2),
        "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n\n",
        "COMPONENT_TARGETS = json.loads(r\"\"\"%s\"\"\")\n\n" % json.dumps(comp_targets, indent=2),
        "COMPONENT_DETAILS = json.loads(r\"\"\"%s\"\"\")\n\n" % json.dumps(comp_details, indent=2),
        "# Frozen seed prices for the whole %s line, read out of\n"
        "# src/data/products.json at authoring time.\n" % spec["sku"],
        "SEED_ROWS = json.loads(r\"\"\"%s\"\"\")\n\n" % json.dumps(seed_rows, indent=2),
        "# Every line member outside the repriced run, with the price the\n"
        "# catalogue must still render for it.\n",
        "SCOPE = json.loads(r\"\"\"%s\"\"\")\n" % json.dumps(scope, indent=2),
    ])


def docline(spec):
    return (
        "Review %d on %s (%s) is the only row whose Review text contains %r, so the\n"
        "run to reprice is %s of that line: %s.\n"
        "Seed price %s, %s%% -> %s exactly (no rounding is required).\n"
        % (
            spec["review_id"], spec["product"], spec["sku"], spec["phrase"],
            spec["run_label"],
            ", ".join("%d %s" % (pid, sku) for pid, sku in spec["run"]),
            spec["base"], spec["pct"], spec["new"],
        )
    )


def write_reward(path, spec, tables):
    comp_weights, comp_targets, comp_details, seed_rows, scope = tables
    text = (
        '"""Deterministic offline reward for %s.\n\n%s\nOnly current_state is read.\n"""\n\n'
        "import json\n\n" % (spec["task_id"], docline(spec))
    )
    text += reward_header(spec, comp_weights, comp_targets, comp_details, seed_rows, scope)
    text += REWARD_BODY
    text += '''

def evaluate(evidence):
    apps = _as_dict(_as_dict(evidence).get("apps"))
    app = _as_dict(apps.get("shopping_admin")) or _as_dict(apps.get("webarena_shopping_admin_mock"))
    state = app.get("current_state")
    if not isinstance(state, dict):
        state = {}
    score, components = score_state(state)
    return {"score": score, "components": components}
'''
    path.write_text(text, encoding="utf-8")
    return text


def write_nemo_reward(path, spec, tables):
    comp_weights, comp_targets, comp_details, seed_rows, scope = tables
    text = (
        '"""NeMo-Gym reward program for %s.\n\n%s\nRubric parity with reward.py. Reads the live current_state from the state API.\n"""\n\n'
        "import json\nimport sys\n\nimport requests\n\n"
        'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n\n' % (spec["task_id"], docline(spec), PLACEHOLDER)
    )
    text += reward_header(spec, comp_weights, comp_targets, comp_details, seed_rows, scope)
    text += REWARD_BODY
    text += '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    score, _components = score_state(state)
    print("REWARD: %s" % score)


main()
'''
    path.write_text(text, encoding="utf-8")
    return text


SETUP_TEMPLATE = '''"""Injected precondition for {task_id}.

Appends one extra APPROVED customer review to `state.reviews` on {d_product}
({d_sku}). Its text shares the vocabulary of the phrase the instruction quotes
but does NOT contain that phrase, so an agent that filters the Review column on
a two-word fragment sees two candidate products and has to read the full quote;
an agent that filters on the quoted phrase still sees exactly one row.

Read-modify-write: GET /go, mutate the whole document, POST it back. The record
carries every field a seeded review row carries and the same field convention
the in-app review handler writes (Reviews.jsx:534-551), so it renders on the
grid and on its own edit form.

Nothing here touches productOverrides, so the untouched injected lane still
scores exactly 0.0.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{placeholder}"

DISTRACTOR = json.loads(r"""{distractor}""")


def fail(message):
    print("initial_setup failed: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        fail("/go returned neither a current nor a baseline state document")

    reviews = state.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        fail("state.reviews is missing or empty; refusing to post a truncated document")

    marker = DISTRACTOR["detail"]
    if not any(str(row.get("detail")) == marker for row in reviews if isinstance(row, dict)):
        next_id = 1
        for row in reviews:
            if isinstance(row, dict):
                try:
                    next_id = max(next_id, int(row.get("review_id") or 0) + 1)
                except (TypeError, ValueError):
                    continue
        record = dict(DISTRACTOR)
        record["review_id"] = next_id
        reviews = list(reviews) + [record]
    state["reviews"] = reviews

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    posted.raise_for_status()


main()
'''


def build_distractor(spec):
    d = spec["distractor"]
    pid = DISTRACTOR_PRODUCT_IDS[d["sku"]]
    return {
        "review_id": 0,
        "created_at": "2023-05-08 10:24:%02d" % (10 + spec["n"]),
        "entity_id": 1,
        "entity_pk_value": pid,
        "status_id": 1,
        "status_code": "Approved",
        "store_id": 1,
        "title": d["title"],
        "detail": d["detail"],
        "nickname": d["nickname"],
        "customer_id": None,
        "sku": d["sku"],
        "product_name": d["product_name"],
        "ratings": [{
            "rating_id": 4,
            "rating_code": "Rating",
            "option_id": RATING_OPTION[d["value"]],
            "value": d["value"],
            "percent": d["value"] * 20,
        }],
        "rating_summary": float(d["value"]),
    }


REPLAY_TEMPLATE = '''"""Golden replay draft for {task_id}.

Click-only from the site root. Marketing > All Reviews, filter the Review
column on the quoted phrase to learn which product the review is on, then
Catalog > Products, keyword-search the line, tick the {count} rows of {run_label},
Actions > Update attributes, set the bulk Price, Save.

Derivation: review {review_id} is the only row whose Review text contains
{phrase!r}; it names {product} ({sku}). Seed price {base}, {pct}% -> {new}.
No page.goto after the landing.
"""


def run(page, base_url):
    page.goto(base_url + "/")

    # --- R6: find the product by searching review content -----------------
    page.get_by_role("link", name="Marketing").first.click()
    page.get_by_role("link", name="All Reviews", exact=True).first.click()
    page.wait_for_selector("#reviewGrid")
    detail_filter = page.locator("#reviewGrid_filter_detail")
    detail_filter.fill({phrase!r})
    detail_filter.press("Enter")
    page.wait_for_timeout(400)
    # The single surviving row prints the product name and its SKU.
    assert page.locator("td.col-sku").first.inner_text().strip() == {sku!r}

    # --- A5: apply the percentage to the run ------------------------------
    page.get_by_role("link", name="Catalog").first.click()
    page.get_by_role("link", name="Products", exact=True).first.click()
    page.wait_for_selector("table.data-grid")
    search = page.locator("input.data-grid-search-control")
    search.fill({sku!r})
    search.press("Enter")
    page.wait_for_timeout(400)
{checks}
    page.locator("button.action-select").click()
    page.get_by_text("Update attributes", exact=True).click()
    page.locator("#bulk-price").fill({new!r})
    page.get_by_role("button", name="Save").click()
    page.wait_for_timeout(400)
'''


def main() -> None:
    BATCH.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    nemo_lines = []

    for spec in TASKS_SPEC:
        if spec["distractor"]:
            detail = spec["distractor"]["detail"].lower()
            if spec["phrase"].lower() in detail:
                raise SystemExit("%s distractor contains the quoted phrase" % spec["slug"])
        if money(spec["new"]) == money(spec["base"]):
            raise SystemExit("%s target equals the seed price" % spec["slug"])
        expected = (Decimal(spec["base"]) * (Decimal("100") + Decimal(spec["pct"])) / Decimal("100"))
        if expected != Decimal(spec["new"]):
            raise SystemExit("%s arithmetic: %s != %s" % (spec["slug"], expected, spec["new"]))
        spec["task_id"] = "variant_run_pct_reprice_%s_%03d" % (spec["slug"], spec["n"])
        bundle = TASKS / spec["task_id"]
        bundle.mkdir(parents=True, exist_ok=True)
        tables = build_reward_tables(spec)

        if spec["style"] == "terse":
            words = len(spec["instruction"].split())
            if words > 40:
                raise SystemExit("%s terse instruction is %d words" % (spec["task_id"], words))

        criteria = [
            "Product %d (%s) sells at %s." % (pid, sku, spec["new"]) for pid, sku in spec["run"]
        ]
        criteria.append(
            "Every other %s row - the other %d variants and the configurable parent %d - still sells at %s."
            % (spec["sku"], len(spec["rest"]) - 1, spec["parent"], spec["base"])
        )

        (bundle / "task_instruction.json").write_text(json.dumps({
            "task_id": spec["task_id"],
            "task_instruction": spec["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": criteria,
        }, indent=2) + "\n", encoding="utf-8")

        injected = []
        setup_text = None
        if spec["distractor"]:
            distractor = build_distractor(spec)
            setup_text = SETUP_TEMPLATE.format(
                task_id=spec["task_id"],
                placeholder=PLACEHOLDER,
                d_product=distractor["product_name"],
                d_sku=distractor["sku"],
                distractor=json.dumps(distractor, indent=2),
            )
            (bundle / "initial_setup.py").write_text(setup_text, encoding="utf-8")
            injected.append(
                "reviews += one approved review (id max+1) on %s (%s, product %d) whose text shares "
                "the vocabulary of the quoted phrase but not the phrase itself - a distractor for an "
                "agent that filters the Review column on a fragment instead of the full quote. "
                "Full-document read-modify-write; productOverrides is untouched, so the injected lane "
                "still scores 0.0."
                % (distractor["product_name"], distractor["sku"], distractor["entity_pk_value"])
            )

        reward_text = write_reward(bundle / "reward.py", spec, tables)
        nemo_reward_text = write_nemo_reward(bundle / "nemo_reward.py", spec, tables)

        metadata = {
            "style": spec["style"],
            "difficulty": "medium",
            "shape": spec["shape"],
            "skills": ["R6", "A5"],
            "skill_chain": (
                "filter the Reviews grid's Review column on the quoted phrase to learn which "
                "product it is about -> apply %s%% to the seeded price of %s and write the result "
                "onto every member of that run" % (spec["pct"], spec["run_label"])
            ),
            "derived_from": "size_run_reprice_sahara_size28_markdown_001",
            "official_analogues": [
                ANALOGUE_PRICE_PCT2 if spec["pct"].startswith("+") else ANALOGUE_PRICE_PCT,
                ANALOGUE_REVIEW_TERM,
                ANALOGUE_REVIEW_MENTION,
            ],
            "topic": "variant-run percentage repricing",
            "lane": "variant_run_pct_reprice",
            "inspiration_ids": INSPIRATION_IDS,
            "authoring_notes": [
                "Price writer: ProductEdit.jsx:351 patch.price -> :389 patchProduct -> "
                "AppContext.jsx:218-227 productOverrides[<id>].price; bulk writer "
                "ProductGrid.jsx:490 applyBulkAttributes -> the same patchProduct.",
                "Price reader: selectors.js:164-179 getProducts merges productOverrides over the "
                "frozen row and ProductGrid.jsx:167-173 renders formatCurrency(r.price) from it, so "
                "the graded key is the key the Price column shows.",
                "special_price is null for every member of this line (only 6 products in the whole "
                "seed carry one: 2, 10, 11, 16, 41, 42), so there is exactly one price on screen.",
                "Arithmetic: %s x %s%% = %s exactly at two decimals, so nearest-cent and any other "
                "defensible rounding agree." % (spec["base"], spec["pct"], spec["new"]),
                "Review-content retrieval: LegacyReviewGrid.jsx:160 filters `detail` through "
                "`contains` (:70-71, case-insensitive substring). The quoted phrase matches exactly "
                "one of the 351 seeded reviews (review %d)." % spec["review_id"],
                "Catalog keyword search: gridUtils.js:132-138 matches any column's searchValue "
                "over every declared column, visible or not; the keyword '%s' returns %d rows." % (
                    spec["sku"], spec["search_hits"]),
            ],
        }
        if injected:
            metadata["injected_preconditions"] = injected

        manifest = {
            "schema_version": 2,
            "task_id": spec["task_id"],
            "instruction": spec["instruction"],
            "apps": [{
                "name": APP_DIR,
                "source_name": "shopping_admin",
                "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
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
        (bundle / "task.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        row = {"task_payload": {
            "task_id": spec["task_id"],
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
                "bundle_id": spec["task_id"],
                "app_dir": APP_DIR,
                "initial_setup": setup_text,
                "eval_reward_code": nemo_reward_text,
            },
        }}
        (bundle / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        nemo_lines.append(json.dumps(row))

        checks = "\n".join(
            '    page.locator("#idscheck%d").check()' % pid for pid, _sku in spec["run"]
        )
        (REPLAYS / (spec["task_id"] + ".py")).write_text(REPLAY_TEMPLATE.format(
            task_id=spec["task_id"], count=len(spec["run"]), run_label=spec["run_label"],
            review_id=spec["review_id"], phrase=spec["phrase"], product=spec["product"],
            sku=spec["sku"], base=spec["base"], pct=spec["pct"], new=spec["new"], checks=checks,
        ), encoding="utf-8")

        index["tasks"].append({"task_id": spec["task_id"], "path": "../../%s/task.json" % spec["task_id"]})
        assert reward_text  # keep the local bound; the file is the artefact

    (BATCH / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (BATCH / "nemo_tasks.jsonl").write_text("\n".join(nemo_lines) + "\n", encoding="utf-8")
    print("wrote %d bundles" % len(TASKS_SPEC))


if __name__ == "__main__":
    main()
