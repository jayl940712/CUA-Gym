#!/usr/bin/env python3
"""Batch-6 lane 36 generator -- shopping, R3 -> A2.

Chain: count the reviews on each candidate product that meet a stated rating
bound, use the count to pick which product the instruction means, then submit
the multi-field review form on that product's page.

Candidate sets are injected into `wishlist.items` or `compareList.items`, both
of which link straight to the PDP and are reachable from the header on every
page, so `start_path` is "/" for all ten tasks.

Run:  python3 scripts/_b6_lane36_gen.py
Writes: output/tasks/shopping/<task_id>/{task_instruction,task,nemo_task}.json
        output/tasks/shopping/<task_id>/{reward,nemo_reward,initial_setup}.py
        output/tasks/shopping/_batches/review_count_selected_product/...
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
DATA = os.path.join(ROOT, "hub/websites/webarena_shopping_mock/src/data")
OUT = os.path.join(ROOT, "output/tasks/shopping")
BATCH = os.path.join(OUT, "_batches/review_count_selected_product")

PRODUCTS = {p["id"]: p for p in json.load(open(os.path.join(DATA, "products.json")))}

ANALOGUE_TITLES = "Get all review titles with 2 stars or below for the product on the current page."
ANALOGUE_BRUSH = "Return the titles for reviews with 3 stars or below for brush from sephora"
ANALOGUE_NICK = "Return the customer nickname(s) who gave a rating of 3 stars or below for Chloe tank"
RATE_LAMP = ('Rate my recently purchased floor lamp with 5 stars using my nickname Emma Lopez, '
             'with the summary "Good purchase" and review "I like it"')
RATE_JIFFY = ('Rate my recently purchased Jiffy Mix with 4 stars using my nickname ShoppingEmma, '
              'with the summary "Good purchase" and review "I like it"')
RATE_PS3 = ('Rate my recently purchased PS3 accessory with 3 stars using my nickname GamingEmma, '
            'with the summary "Ok I guess" and review "Does the job"')
RATE_FOUNDATION = ('Rate my recently purchased Foundation For Mattress With Frame Set with 1 stars '
                   'using my nickname ShoppingEmma, with the summary "Very bad" and review "I hated it"')
RATE_SPEAKER = ('Rate my recently purchased Mini Wireless Bluetooth Speaker with 2 stars using my '
                'nickname SimpleEmma, with the summary "Very bad" and review "I hated it"')


def price(pid):
    p = PRODUCTS[pid]
    return p["specialPrice"] if p["specialPrice"] is not None else p["price"]


# --------------------------------------------------------------------------
# The ten tasks. `counts` records the verified per-candidate value of the
# stated predicate; `winner` is the unique satisfier.
# --------------------------------------------------------------------------
TASKS = [
    {
        "n": 1,
        "slug": "furniture_most_one_star",
        "surface": "wishlist",
        "candidates": [13531, 14779, 15417],
        "winner": 14779,
        "predicate": "number of reviews rated exactly 1 star",
        "counts": {13531: 2, 14779: 5, 15417: 1},
        "margin": 3,
        "totals": {13531: 12, 14779: 11, 15417: 10},
        "style": "terse",
        "shape": "mutation",
        "rating": 1,
        "nickname": "EmmaSF",
        "summary": "Same story here",
        "detail": "It lasted a month",
        "instruction": (
            "Whichever of the three furniture items on my wish list has the most 1-star reviews is "
            "the one I ended up with. Add my review there: 1 star, nickname EmmaSF, summary "
            "\"Same story here\", review \"It lasted a month\"."
        ),
        "group_noun": "furniture items on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_FOUNDATION],
        "derived_from": "review_my_purchase_kneeling_chair_003",
    },
    {
        "n": 2,
        "slug": "bedding_fewest_five_star",
        "surface": "wishlist",
        "candidates": [14482, 14535, 66708],
        "winner": 14482,
        "predicate": "number of reviews rated exactly 5 stars",
        "counts": {14482: 4, 14535: 10, 66708: 9},
        "margin": 5,
        "totals": {14482: 10, 14535: 10, 66708: 10},
        "style": "terse",
        "shape": "retrieval_writeback",
        "rating": 3,
        "nickname": "BeddingEmma",
        "summary": "Only 4 five-star reviews so far",
        "summary_is_derived": True,
        "detail": "Soft enough, thin though",
        "instruction": (
            "Of the three bedding items on my wish list, the one with the fewest 5-star reviews "
            "needs mine: 3 stars, nickname BeddingEmma, summary \"Only N five-star reviews so far\" "
            "with N that count, review \"Soft enough, thin though\"."
        ),
        "group_noun": "bedding items on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_PS3],
        "derived_from": None,
    },
    {
        "n": 3,
        "slug": "compare_most_four_star_plus",
        "surface": "compare",
        "candidates": [17339, 18082, 77464],
        "winner": 17339,
        "predicate": "number of reviews rated 4 stars or better",
        "counts": {17339: 5, 18082: 2, 77464: 3},
        "margin": 2,
        "totals": {17339: 5, 18082: 5, 77464: 5},
        "style": "terse",
        "shape": "mutation",
        "rating": 5,
        "nickname": "GadgetEmma",
        "summary": "Lives up to it",
        "detail": "Works exactly as described",
        "instruction": (
            "The three items on my compare list: whichever has the most reviews of 4 stars or "
            "better is the one I bought. Review it: 5 stars, nickname GadgetEmma, summary "
            "\"Lives up to it\", review \"Works exactly as described\"."
        ),
        "group_noun": "items on the compare list",
        "analogues": [ANALOGUE_BRUSH, RATE_LAMP],
        "derived_from": None,
    },
    {
        "n": 4,
        "slug": "grocery_most_low_star",
        "surface": "wishlist",
        "candidates": [20626, 21079, 21664],
        "winner": 21079,
        "predicate": "number of reviews rated 2 stars or below",
        "counts": {20626: 2, 21079: 4, 21664: 1},
        "margin": 2,
        "totals": {20626: 5, 21079: 5, 21664: 4},
        "style": "terse",
        "shape": "mutation",
        "rating": 1,
        "nickname": "SnackEmma",
        "summary": "Not for me",
        "detail": "Tossed most of it",
        "instruction": (
            "One of the three groceries on my wish list was a letdown -- the one with the most "
            "reviews at 2 stars or below. Leave 1 star there, nickname SnackEmma, summary "
            "\"Not for me\", review \"Tossed most of it\"."
        ),
        "group_noun": "groceries on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_SPEAKER],
        "derived_from": None,
    },
    {
        "n": 5,
        "slug": "pantry_most_five_star",
        "surface": "wishlist",
        "candidates": [21362, 22022, 22768],
        "winner": 22768,
        "predicate": "number of reviews rated exactly 5 stars",
        "counts": {21362: 6, 22022: 7, 22768: 10},
        "margin": 3,
        "totals": {21362: 7, 22022: 10, 22768: 10},
        "style": "explicit",
        "shape": "retrieval_writeback",
        "rating": 5,
        "nickname": "PantryEmma",
        "summary": "Worth the shelf space",
        "detail": "10 of us gave this five stars",
        "detail_is_derived": True,
        "instruction": (
            "Three pantry items sit on my wish list. Open each one's Reviews tab and count how many "
            "of its reviews are 5 stars. The one with the most 5-star reviews is the one I want to "
            "endorse, so submit a review on that product's page: 5 stars, nickname PantryEmma, "
            "summary \"Worth the shelf space\", and review text \"N of us gave this five stars\" "
            "with N replaced by the 5-star count you found on it. Leave the other two products "
            "unreviewed."
        ),
        "group_noun": "pantry items on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_JIFFY],
        "derived_from": None,
    },
    {
        "n": 6,
        "slug": "compare_most_three_star_or_less",
        "surface": "compare",
        "candidates": [11059, 27170, 95064],
        "winner": 95064,
        "predicate": "number of reviews rated 3 stars or below",
        "counts": {11059: 5, 27170: 0, 95064: 10},
        "margin": 5,
        "totals": {11059: 8, 27170: 10, 95064: 10},
        "style": "terse",
        "shape": "retrieval_writeback",
        "rating": 2,
        "nickname": "EmmaL",
        "summary": "Believe the reviews",
        "detail": "10 of them are 3 stars or worse",
        "detail_is_derived": True,
        "instruction": (
            "Of my three compare-list items, the one with most reviews at 3 stars or below gets "
            "mine: 2 stars, nickname EmmaL, summary \"Believe the reviews\", review \"N of them "
            "are 3 stars or worse\", N that count."
        ),
        "group_noun": "items on the compare list",
        "analogues": [ANALOGUE_BRUSH, RATE_SPEAKER],
        "derived_from": None,
    },
    {
        "n": 7,
        "slug": "oral_care_over_three_low_star",
        "surface": "wishlist",
        "candidates": [1419, 2105, 57936],
        "winner": 2105,
        "predicate": "number of reviews rated 2 stars or below",
        "counts": {1419: 2, 2105: 4, 57936: 1},
        "margin": 2,
        "totals": {1419: 6, 2105: 6, 57936: 4},
        "style": "terse",
        "shape": "mutation",
        "rating": 2,
        "nickname": "SmileEmma",
        "summary": "Read these first",
        "detail": "Did nothing for me",
        "instruction": (
            "Only one of the three oral-care items on my wish list has more than three reviews at 2 "
            "stars or below. I bought that one: 2 stars, nickname SmileEmma, summary "
            "\"Read these first\", review \"Did nothing for me\"."
        ),
        "group_noun": "oral-care items on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_PS3],
        "derived_from": None,
    },
    {
        "n": 8,
        "slug": "shoes_none_under_four_star",
        "surface": "wishlist",
        "candidates": [10270, 11284, 12283],
        "winner": 12283,
        "predicate": "number of reviews rated below 4 stars",
        "counts": {10270: 5, 11284: 5, 12283: 0},
        "margin": 5,
        "totals": {10270: 9, 11284: 6, 12283: 8},
        "style": "terse",
        "shape": "mutation",
        "rating": 5,
        "nickname": "ShoeEmma",
        "summary": "No complaints",
        "detail": "Comfortable from day one",
        "instruction": (
            "Exactly one of the three pairs of shoes on my wish list has no review under 4 stars. "
            "That is my favourite pair: give it 5 stars, nickname ShoeEmma, summary "
            "\"No complaints\", review \"Comfortable from day one\"."
        ),
        "group_noun": "pairs of shoes on the wish list",
        "analogues": [ANALOGUE_BRUSH, RATE_LAMP],
        "derived_from": None,
    },
    {
        "n": 9,
        "slug": "compare_hair_under_five_five_star",
        "surface": "compare",
        "candidates": [24, 1565, 3086],
        "winner": 3086,
        "predicate": "number of reviews rated exactly 5 stars",
        "counts": {24: 9, 1565: 10, 3086: 3},
        "margin": 6,
        "totals": {24: 11, 1565: 10, 3086: 10},
        "style": "explicit",
        "shape": "retrieval_writeback",
        "rating": 3,
        "nickname": "CurlEmma",
        "summary": "Fewer fans than the others",
        "detail": "Only 3 of these are 5 stars",
        "detail_is_derived": True,
        "instruction": (
            "Three hair-care products are on my compare list. Count the 5-star reviews on each: two "
            "of them have plenty and exactly one has fewer than five. That last one is the product "
            "I actually own, so submit my review on its page with 3 stars, nickname CurlEmma, "
            "summary \"Fewer fans than the others\", and review text \"Only N of these are 5 stars\" "
            "with N replaced by the 5-star count you counted on that product. Do not review the "
            "other two."
        ),
        "group_noun": "hair-care products on the compare list",
        "analogues": [ANALOGUE_NICK, RATE_PS3],
        "derived_from": None,
    },
    {
        "n": 10,
        "slug": "wall_art_zero_five_star",
        "surface": "wishlist",
        "candidates": [13734, 16285, 98867],
        "winner": 98867,
        "predicate": "number of reviews rated exactly 5 stars",
        "counts": {13734: 3, 16285: 8, 98867: 0},
        "margin": 3,
        "totals": {13734: 7, 16285: 9, 98867: 9},
        "style": "terse",
        "shape": "mutation",
        "rating": 1,
        "nickname": "ArtEmma",
        "summary": "Colours are off",
        "detail": "Nothing like the picture shown",
        "instruction": (
            "One of the three wall prints on my wish list has no 5-star review at all. That is the "
            "one I got: 1 star, nickname ArtEmma, summary \"Colours are off\", review \"Nothing "
            "like the picture shown\"."
        ),
        "group_noun": "wall prints on the wish list",
        "analogues": [ANALOGUE_TITLES, RATE_FOUNDATION],
        "derived_from": None,
    },
]

ADDED_AT = ["2023-05-02 09:14:11", "2023-05-04 18:02:47", "2023-05-06 11:37:20"]


def task_id(t):
    return "review_count_selected_product_%s_%03d" % (t["slug"], t["n"])


def wishlist_items(t):
    rows = []
    for idx, pid in enumerate(t["candidates"]):
        p = PRODUCTS[pid]
        rows.append({
            "wishlistItemId": idx + 1,
            "productId": pid,
            "sku": p["sku"],
            "name": p["name"],
            "price": price(pid),
            "qty": 1,
            "description": "",
            "addedAt": ADDED_AT[idx],
        })
    return rows


def compare_items(t):
    return [{"productId": pid, "sku": PRODUCTS[pid]["sku"], "name": PRODUCTS[pid]["name"]}
            for pid in t["candidates"]]


# --------------------------------------------------------------------------
# rubric text
# --------------------------------------------------------------------------
def components(t):
    if t.get("summary_is_derived"):
        return [
            ("single_review_on_the_derived_product", 0.4),
            ("star_rating_recorded", 0.2),
            ("nickname_and_body_recorded", 0.15),
            ("summary_carries_the_counted_value", 0.25),
        ]
    if t.get("detail_is_derived"):
        return [
            ("single_review_on_the_derived_product", 0.4),
            ("star_rating_recorded", 0.2),
            ("nickname_and_summary_recorded", 0.15),
            ("review_body_carries_the_counted_value", 0.25),
        ]
    return [
        ("single_review_on_the_derived_product", 0.4),
        ("star_rating_recorded", 0.2),
        ("nickname_and_summary_recorded", 0.2),
        ("review_body_recorded", 0.2),
    ]


def criteria(t):
    w = t["winner"]
    name = PRODUCTS[w]["name"]
    out = [
        "state.myReviews holds exactly one entry and its productId is %d (%s), the candidate whose "
        "%s is %d against %s." % (
            w, name, t["predicate"], t["counts"][w],
            " and ".join("%d for %d" % (t["counts"][p], p) for p in t["candidates"] if p != w)),
        "That entry's rating is exactly %d." % t["rating"],
        "That entry's nickname is '%s'." % t["nickname"],
        "That entry's title is '%s'." % t["summary"],
        "That entry's detail is '%s'." % t["detail"],
    ]
    if t.get("summary_is_derived"):
        out[3] += " The numeral in it is the counted value, so an agent that skipped the count fails it."
    if t.get("detail_is_derived"):
        out[4] += " The numeral in it is the counted value, so an agent that skipped the count fails it."
    return out


CHECK_BODY = '''
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
        return int(number) if float(number).is_integer() else None
    return None


def _norm(value):
    if not isinstance(value, str):
        return ""
    text = re.sub(r"\\s+", " ", value).strip().lower()
    return text.strip(" .!,;:")


def _target(state):
    rows = state.get("myReviews")
    if not isinstance(rows, list):
        return None
    rows = [row for row in rows if isinstance(row, dict)]
    if len(rows) != 1:
        return None
    row = rows[0]
    if _int(row.get("productId")) != PRODUCT_ID:
        return None
    return row


def _checks(state):
    row = _target(state)
    if row is None:
        return dict((name, False) for name in COMPONENT_WEIGHTS)
    return {
%s
    }
'''


def checks_dict(t):
    if t.get("summary_is_derived"):
        return (
            '        "single_review_on_the_derived_product": True,\n'
            '        "star_rating_recorded": _int(row.get("rating")) == RATING,\n'
            '        "nickname_and_body_recorded": (\n'
            '            _norm(row.get("nickname")) == _norm(NICKNAME)\n'
            '            and _norm(row.get("detail")) == _norm(DETAIL)\n'
            '        ),\n'
            '        "summary_carries_the_counted_value": _norm(row.get("title")) == _norm(SUMMARY),'
        )
    if t.get("detail_is_derived"):
        return (
            '        "single_review_on_the_derived_product": True,\n'
            '        "star_rating_recorded": _int(row.get("rating")) == RATING,\n'
            '        "nickname_and_summary_recorded": (\n'
            '            _norm(row.get("nickname")) == _norm(NICKNAME)\n'
            '            and _norm(row.get("title")) == _norm(SUMMARY)\n'
            '        ),\n'
            '        "review_body_carries_the_counted_value": _norm(row.get("detail")) == _norm(DETAIL),'
        )
    return (
        '        "single_review_on_the_derived_product": True,\n'
        '        "star_rating_recorded": _int(row.get("rating")) == RATING,\n'
        '        "nickname_and_summary_recorded": (\n'
        '            _norm(row.get("nickname")) == _norm(NICKNAME)\n'
        '            and _norm(row.get("title")) == _norm(SUMMARY)\n'
        '        ),\n'
        '        "review_body_recorded": _norm(row.get("detail")) == _norm(DETAIL),'
    )


def constants_block(t):
    return (
        'PRODUCT_ID = %d\n'
        'RATING = %d\n'
        'NICKNAME = %s\n'
        'SUMMARY = %s\n'
        'DETAIL = %s\n' % (
            t["winner"], t["rating"], json.dumps(t["nickname"]),
            json.dumps(t["summary"]), json.dumps(t["detail"])))


def weights_block(t):
    lines = ",\n".join('    "%s": %s' % (n, w) for n, w in components(t))
    return "COMPONENT_WEIGHTS = {\n%s,\n}\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n\n" % lines


def docstring(t, kind):
    tid = task_id(t)
    lines = ["Deterministic reward for %s." % tid] if kind == "local" else [
        "NeMo-Gym reward program for %s." % tid]
    lines.append("")
    lines.append("Success criteria:")
    for c in criteria(t):
        lines.append("  * %s" % c)
    lines.append("")
    if kind == "local":
        lines.append(
            "Only user-visible persisted state is inspected, and only `current_state`. The scored\n"
            "surface is `myReviews`, whose sole writer is `submitReview`\n"
            "(src/context/AppContext.jsx:427-447); it boots empty from `createInitialData()`\n"
            "(src/utils/dataManager.js:145), so an untouched episode and an empty state both score\n"
            "exactly 0.0 on every component.")
    else:
        lines.append(
            "Implements exactly the rubric of reward.py, reading `current_state` from\n"
            "GET /go?sid=... instead of a frozen evidence bundle, and printing REWARD: <float> on\n"
            "every output path including the error path.\n\n"
            "Self-contained: standard library plus requests, which is present in\n"
            "cuagym/requirements.txt.")
    return '"""%s\n"""\n' % "\n".join(lines)


def reward_py(t):
    return (
        docstring(t, "local")
        + "\nimport re\n\n"
        + constants_block(t)
        + "\n"
        + weights_block(t)
        + (CHECK_BODY % checks_dict(t))
        + '''

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
    )


def nemo_reward_py(t):
    return (
        docstring(t, "nemo")
        + "\nimport re\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\nBASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"\n\n'
        + constants_block(t)
        + "\n"
        + weights_block(t)
        + (CHECK_BODY % checks_dict(t))
        + '''

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
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        value = score_state(state)
    except Exception as exc:  # noqa: BLE001 - a scoring bug must still score
        print("reward scoring failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %s" % value)


main()
'''
    )


SETUP_DOC = '''"""NeMo-Gym setup program for {tid}.

Plants the candidate set the retrieval runs over: the {count} products below are
written into `{key}` so the instruction's "{noun}" resolves to exactly them.
Every one is a real seeded product; each row carries every field the mock's own
handler writes ({handler}), so the page renders
them exactly as an agent-added row would.

Why this injection exists: without it the instruction has no candidate set, and
the seeded {key} is empty ({empty_note}).
The three candidates were chosen so that the stated predicate ({predicate}) has
one satisfier with a margin of {margin} -- {counts} -- and so that neither the
largest nor the smallest total review count picks the winner by accident.

Nothing here pre-satisfies the rubric: `myReviews` is written empty, and the
rubric pays only for the review the agent submits.

The whole state document is read back from GET /go?sid=... and POSTed intact
(read-modify-write), so no key can be lost whatever the mock's merge semantics.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_SHOPPING_URL__"

# Raw string so that no backslash escape is eaten by the Python parser before
# json.loads sees it: several seeded product names contain quote characters.
ITEMS = json.loads(r"""
{items}
""")


def main():
    base = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    base.raise_for_status()
    payload = base.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not state:
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not state:
        print("SETUP FAILED: /go returned no usable state document", file=sys.stderr)
        raise SystemExit(1)
    if "customer" not in state or "myReviews" not in state:
        print("SETUP FAILED: state document is missing seeded keys", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
{mutate}
    state["myReviews"] = []
    if not isinstance(state.get("nextReviewId"), int):
        state["nextReviewId"] = 400000

    post = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    post.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    verified = check.json()
    current = verified.get("current_state") or {{}}
    if len(current.get("{key}", {{}}).get("items", [])) != {count}:
        print("SETUP FAILED: candidate set not present after set", file=sys.stderr)
        raise SystemExit(1)
    if current.get("myReviews") != []:
        print("SETUP FAILED: myReviews is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if verified.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


main()
'''


def setup_py(t):
    if t["surface"] == "wishlist":
        items = wishlist_items(t)
        key = "wishlist"
        handler = "addToWishlist, src/context/AppContext.jsx:324-345"
        empty_note = "src/data/wishlist.json ships {\"items\": []}"
        mutate = ('    state["wishlist"] = {"items": ITEMS}\n'
                  '    state["nextWishlistItemId"] = %d\n' % (len(items) + 1))
    else:
        items = compare_items(t)
        key = "compareList"
        handler = "addToCompare, src/context/AppContext.jsx:398-410"
        empty_note = "createInitialData() sets compareList to {\"items\": []}"
        mutate = '    state["compareList"] = {"items": ITEMS}\n'
    counts = ", ".join("%d has %d" % (p, t["counts"][p]) for p in t["candidates"])
    return SETUP_DOC.format(
        tid=task_id(t), count=len(items), key=key, noun=t["group_noun"],
        handler=handler, empty_note=empty_note, predicate=t["predicate"],
        margin=t["margin"], counts=counts,
        items=json.dumps(items, indent=1, ensure_ascii=True),
        mutate=mutate)


def injected_preconditions(t):
    key = "wishlist.items" if t["surface"] == "wishlist" else "compareList.items"
    return [
        "%s is set to the three seeded candidates %s, each row carrying every field the mock's own "
        "handler writes, so the instruction's \"%s\" resolves to exactly this set." % (
            key, t["candidates"], t["group_noun"]),
        "The candidates were chosen so that %s is unique: %s (margin %d), and so that the winner is "
        "neither the uniquely most-reviewed nor the uniquely least-reviewed candidate." % (
            t["predicate"], ", ".join("%d for %d" % (t["counts"][p], p) for p in t["candidates"]),
            t["margin"]),
        "myReviews is written empty, so nothing in the rubric is pre-satisfied.",
    ]


def notes(t):
    w = t["winner"]
    out = [
        "Chain: open each of the three candidates from %s, count on each PDP's Reviews tab how many "
        "reviews meet the stated bound, and submit the review form on the single product that "
        "satisfies the predicate." % (
            "the wish list" if t["surface"] == "wishlist" else "the compare list"),
        "Tie margin, verified against src/data/reviews.json: %s; the winner is %d with a margin of "
        "%d." % (", ".join("product %d -> %d" % (p, t["counts"][p]) for p in t["candidates"]),
                 w, t["margin"]),
        "De-dup check on each candidate: no two of its reviews share (title, detail, rating), which "
        "catches both the census's duplicate class and CORRECTIONS #77's self-concatenated-nickname "
        "class, so the count has exactly one defensible value. No candidate carries a null-rating "
        "review either (689 such rows exist across 355 products in the seed).",
        "Surface agreement, checked per candidate: products[].reviewsCount (grid tile), "
        "reviewCounts.json (PDP tab label) and the number of bodies in reviews.json are equal, so a "
        "count read off any surface agrees. Totals: %s." % (
            ", ".join("%d -> %d" % (p, t["totals"][p]) for p in t["candidates"])),
        "Paging: the PDP Reviews tab shows 10 per page (src/pages/ProductPage.jsx:18), so "
        "candidates with more than 10 reviews (%s) need the review pager." % (
            ", ".join(str(p) for p in t["candidates"] if t["totals"][p] > 10) or "none here"),
        "Writeback: myReviews[] + nextReviewId via submitReview (src/context/AppContext.jsx:"
        "427-447), which records productId, a plain 1-5 Number rating, nickname, title (the form's "
        "Summary field), detail and createdAt.",
        "Reachability from '/': the header renders My Wish List on every page "
        "(src/components/Header.jsx:30) and the Compare Products link "
        "(src/components/Header.jsx:64), both list pages link each row to the PDP "
        "(src/pages/WishlistPage.jsx:72, src/pages/ComparePage.jsx:49), and the review form is "
        "inside the PDP Reviews tab.",
        "The rubric asserts the exact resulting collection - myReviews is exactly one entry, on the "
        "derived product - so an agent that reviews two candidates or the wrong candidate scores "
        "0.0 and nothing is paid for leaving anything alone.",
        "Grounded in webarena_shopping_mock @ hub/websites/webarena_shopping_mock; nothing under "
        "hub/ was modified.",
        "Both reward programs read the live session document only, never initial_state or "
        "state_diff.",
    ]
    if t.get("summary_is_derived") or t.get("detail_is_derived"):
        field = "title (Summary)" if t.get("summary_is_derived") else "detail (Review)"
        out.insert(2, "Retrieval writeback: the counted value itself is written into the review's "
                      "%s, so an agent that guesses the product without counting cannot produce the "
                      "string." % field)
    return out


def task_json(t):
    tid = task_id(t)
    return {
        "schema_version": 2,
        "task_id": tid,
        "instruction": t["instruction"],
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
            "style": t["style"],
            "difficulty": "medium",
            "shape": t["shape"],
            "skills": ["R3", "A2"],
            "skill_chain": "count each candidate's reviews that meet the stated rating bound -> "
                           "submit the review form on the product the count selects",
            "derived_from": t["derived_from"],
            "official_analogues": t["analogues"],
            "topic": "review_count_selected_product -- a count over a rating-filtered review set "
                     "picks the product, then the multi-field review form is submitted on it",
            "inspiration_ids": ["webarena-163", "webarena-225", "webarena-585", "webarena-587",
                                "webarena-589"],
            "injected_preconditions": injected_preconditions(t),
            "authoring_notes": notes(t),
        },
    }


def instruction_json(t):
    return {
        "task_id": task_id(t),
        "task_instruction": t["instruction"],
        "app_dir": "webarena_shopping_mock",
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": criteria(t),
    }


def nemo_task_json(t, setup_src, reward_src):
    return {
        "task_payload": {
            "task_id": task_id(t),
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_shopping_mock"],
            "start_urls": [],
            "intent": t["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task_id(t),
                "app_dir": "webarena_shopping_mock",
                "initial_setup": setup_src,
                "eval_reward_code": reward_src,
            },
        }
    }


REPLAY = '''"""Golden replay draft - {tid}.

Click-only from "/": every navigation follows a rendered link, button or form
control. The only page.goto is the initial landing.

Intent: {intent}

Route: / -> header "{entry}" -> each of the three candidate rows in turn ->
"Reviews" tab -> read every review's star fill, paging where the product has
more than ten -> back to the list through the header -> on the winning product
({winner}, {winner_name}) fill the review form and submit.

Mock facts this driver respects:
  * the star radios are 1x1 and opacity:0 (globals.css); the visible target is
    the <label>, and DOM order is ASCENDING (ProductPage.jsx:284-293), so
    label[for="Rating_5"] really is five stars.
  * the Reviews tab pane is only mounted once #tab-label-reviews-title is
    clicked (ProductPage.jsx:333).
  * the tab pages at 10 (ProductPage.jsx:18) and the pager writes ?review_page.
  * a review's own rating is rendered as a percentage: Rating.jsx:44 puts
    title="80%" on div.rating-result, so the driver reads the title and divides
    by 20 rather than counting star glyphs. A review with no vote renders no
    .review-ratings block at all (ProductPage.jsx:351) - none of these
    candidates has one, and the driver would count it as None either way.

Predicate: {predicate}. Verified counts: {counts}. Winner: {winner}.
"""

CANDIDATES = {candidates}
EXPECTED_COUNTS = {counts_map}
WINNER = {winner}
RATING = {rating}
NICKNAME = {nickname}
SUMMARY = {summary}
DETAIL = {detail}


def _open_list(page):
    page.get_by_role("link", name="{entry}").first.click()
    page.wait_for_load_state("networkidle")


def _open_candidate(page, index):
    """Open the index-th product of the rendered list by its own link."""
    _open_list(page)
    page.locator("{row_selector}").nth(index).click()
    page.wait_for_load_state("networkidle")


def _review_ratings(page):
    """Every review's rating on the current Reviews tab page, as 1-5 ints."""
    page.locator("#tab-label-reviews-title").click()
    page.wait_for_selector("ol.review-items li.review-item")
    out = []
    while True:
        for item in page.locator("ol.review-items li.review-item").all():
            meta = item.locator("div.review-ratings div.rating-result")
            if meta.count() == 0:
                out.append(None)
                continue
            title = meta.first.get_attribute("title") or ""
            digits = "".join(c for c in title if c.isdigit())
            out.append(round(int(digits) / 20) if digits else None)
        nxt = page.locator("div.review-toolbar li.pages-item-next a.action.next")
        if nxt.count() == 0:
            break
        nxt.first.click()
        page.wait_for_load_state("networkidle")
        # The pager navigates with a query change; re-assert the Reviews pane.
        if page.locator("ol.review-items li.review-item").count() == 0:
            page.locator("#tab-label-reviews-title").click()
            page.wait_for_selector("ol.review-items li.review-item")
    return out


def _submit_review(page, stars, nickname, summary, detail):
    page.locator("#tab-label-reviews-title").click()
    page.locator('label[for="Rating_%d"]' % stars).click()
    assert page.locator("div.review-control-vote").first.get_attribute(
        "data-rating") == str(stars)
    page.locator("#nickname_field").fill(nickname)
    page.locator("#summary_field").fill(summary)
    page.locator("#review_field").fill(detail)
    page.get_by_role("button", name="Submit Review", exact=True).click()
    page.wait_for_load_state("networkidle")


def run(page, base_url):
    page.goto(base_url + "/")

    counted = {{}}
    for index, product_id in enumerate(CANDIDATES):
        _open_candidate(page, index)
        ratings = _review_ratings(page)
        counted[product_id] = sum(1 for r in ratings if {predicate_expr})
    assert counted == EXPECTED_COUNTS, counted

    winner = {select_expr}
    assert winner == WINNER, winner

    _open_candidate(page, CANDIDATES.index(WINNER))
    _submit_review(page, RATING, NICKNAME, SUMMARY, DETAIL)
'''

PREDICATE_EXPR = {
    "number of reviews rated exactly 1 star": "r == 1",
    "number of reviews rated exactly 5 stars": "r == 5",
    "number of reviews rated 4 stars or better": "r is not None and r >= 4",
    "number of reviews rated 2 stars or below": "r is not None and r <= 2",
    "number of reviews rated 3 stars or below": "r is not None and r <= 3",
    "number of reviews rated below 4 stars": "r is not None and r < 4",
}


def replay_py(t):
    mode = "min" if t["counts"][t["winner"]] == min(t["counts"].values()) else "max"
    select = "%s(counted, key=lambda k: counted[k])" % mode
    entry = "My Wish List" if t["surface"] == "wishlist" else "Compare Products"
    row_selector = (
        "div.products-grid.wishlist ol.product-items li.product-item strong.product-item-name a"
        if t["surface"] == "wishlist"
        else "table#product-comparison td.cell.product.info strong.product-item-name a")
    return REPLAY.format(
        tid=task_id(t), intent=t["instruction"], entry=entry,
        winner=t["winner"], winner_name=PRODUCTS[t["winner"]]["name"][:60],
        predicate=t["predicate"],
        counts=", ".join("%d -> %d" % (p, t["counts"][p]) for p in t["candidates"]),
        candidates=repr(t["candidates"]), counts_map=repr(t["counts"]),
        rating=t["rating"], nickname=json.dumps(t["nickname"]),
        summary=json.dumps(t["summary"]), detail=json.dumps(t["detail"]),
        row_selector=row_selector,
        predicate_expr=PREDICATE_EXPR[t["predicate"]], select_expr=select)


def write(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def main():
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    rows = []
    for t in TASKS:
        tid = task_id(t)
        d = os.path.join(OUT, tid)
        os.makedirs(d, exist_ok=True)
        setup_src = setup_py(t)
        reward_src = nemo_reward_py(t)
        write(os.path.join(d, "task_instruction.json"),
              json.dumps(instruction_json(t), indent=2) + "\n")
        write(os.path.join(d, "task.json"), json.dumps(task_json(t), indent=2) + "\n")
        write(os.path.join(d, "reward.py"), reward_py(t))
        write(os.path.join(d, "nemo_reward.py"), reward_src)
        write(os.path.join(d, "initial_setup.py"), setup_src)
        row = nemo_task_json(t, setup_src, reward_src)
        write(os.path.join(d, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
        write(os.path.join(BATCH, "replays", tid + ".py"), replay_py(t))
        index["tasks"].append({"task_id": tid, "path": "%s/task.json" % tid})
        rows.append(json.dumps(row))
    write(os.path.join(BATCH, "index.json"), json.dumps(index, indent=2) + "\n")
    write(os.path.join(BATCH, "nemo_tasks.jsonl"), "\n".join(rows) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
