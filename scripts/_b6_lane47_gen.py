#!/usr/bin/env python3
"""Batch-6 lane 47 generator - shopping_admin, skills R3 -> A7.

Emits ten bundles under output/tasks/shopping_admin/<task_id>/ plus the lane
batch directory output/tasks/shopping_admin/_batches/praise_count_description/
(GENERATION.md is written separately by hand; index.json, nemo_tasks.jsonl and
replays/ are written here).

Every task: count a stated subset of one product's customer reviews, then
replace that product's description with a sentence carrying the count.
Writeback: productDescriptionOverrides[<entity_id>] via setProductDescription
(AppContext.jsx:229), read back by getProductDescription (selectors.js:208)
into the #product-description textarea (ProductEdit.jsx:155, :1049-1057).
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE_DIR = os.path.join(ROOT, "output/tasks/shopping_admin")
LANE_DIR = os.path.join(SITE_DIR, "_batches/praise_count_description")
REPLAY_DIR = os.path.join(LANE_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

ANALOGUE_464 = (
    'Update the product description of Antonia Racer Tank to "{count} customer(s) love it!" '
    "where count is the number of reviews with 4 stars or above, or \"don't miss out on this "
    'amazing product" when there are no such reviews.'
)
ANALOGUE_543 = (
    "Update the product description of Bella Tank to highlight the real user positive reviews "
    "by quoting the comments"
)
ANALOGUE_545 = (
    "Update the description of Radiant Tee to highlight the real user positive reviews by "
    "quoting the comments"
)
ANALOGUE_546 = (
    "Update the description of Lucia Cross-Fit Bra to highlight the real user positive reviews "
    "by quoting the comments"
)
ANALOGUE_11 = (
    'Tell me the the number of reviews that our store received by far that mention term "disappointed"'
)
ANALOGUE_78 = "What is the total count of Approved reviews amongst all the reviews?"
ANALOGUE_344 = "How many reviews our shop received by far?"


def review(rid, pid, sku, name, status, stars, nickname, title, detail, created):
    status_id = {"Approved": 1, "Pending": 2, "Not Approved": 3}[status]
    return {
        "review_id": rid,
        "created_at": created,
        "entity_id": 1,
        "entity_pk_value": pid,
        "status_id": status_id,
        "status_code": status,
        "store_id": 1,
        "title": title,
        "detail": detail,
        "nickname": nickname,
        "customer_id": None,
        "sku": sku,
        "product_name": name,
        "ratings": [
            {
                "rating_id": 4,
                "rating_code": "Rating",
                "option_id": 15 + stars,
                "value": stars,
                "percent": stars * 20,
            }
        ],
        "rating_summary": float(stars),
    }


TASKS = [
    {
        "id": "praise_count_description_cruise_watch_star_total_001",
        "product_id": 39,
        "product": "Cruise Dual Analog Watch",
        "sku": "24-MG05",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            "Add up the star ratings on every customer review of the Cruise Dual Analog Watch, "
            "then replace that product's description with exactly "
            '"Total stars awarded by our customers: {sum}." with the total filled in.'
        ),
        "frame": r"Total stars awarded by our customers: \d+\.",
        "expected": "Total stars awarded by our customers: 13.",
        "value_component": "the_star_total_written_is_13",
        "seed_reviews": 4,
        "injections": [],
        "skill_chain": (
            "sum the star ratings recorded on one product's reviews -> compose the product "
            "description around that total"
        ),
        "derived_from": "quantify_the_praise_cora_parachute_pant_five_star_003",
        "analogues": [ANALOGUE_464, ANALOGUE_543],
        "inspiration_ids": ["webarena-464", "webarena-543"],
        "surface": (
            "Star values exist on one surface only - the review edit form's Summary Rating line "
            "(/admin/review/product/edit/id/<id>/, Reviews.jsx). Neither review grid nor the "
            "product page's Product Reviews table carries a rating column, so there is no second "
            "surface to disagree with."
        ),
        "notes": [
            "Entity 39 carries four seeded Approved reviews: 27 (5), 28 (4), 29 (2), 30 (2). "
            "Sum 13, and no other product-level aggregate on the site prints 13, so the figure "
            "has to come from the four review pages.",
            "A sum rather than a count: an agent that counts the reviews writes 4, one that "
            "counts the 4-star-plus reviews writes 2, and both score 0.0.",
        ],
    },
    {
        "id": "praise_count_description_josie_yoga_jacket_rating_range_002",
        "product_id": 1236,
        "product": "Josie Yoga Jacket",
        "sku": "WJ02",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            "Check the star rating on each customer review of the Josie Yoga Jacket, then set "
            'that product\'s description to exactly "Customer ratings range from {low} to {high} '
            'stars." using its lowest and highest review ratings.'
        ),
        "frame": r"Customer ratings range from \d+ to \d+ stars\.",
        "expected": "Customer ratings range from 2 to 5 stars.",
        "value_component": "the_rating_range_written_is_two_to_five",
        "seed_reviews": 4,
        "injections": [],
        "skill_chain": (
            "read the star rating on each of one product's reviews and take the range -> compose "
            "the product description around the low and high figures"
        ),
        "derived_from": "quantify_the_praise_chloe_compete_tank_share_002",
        "analogues": [ANALOGUE_464, ANALOGUE_545],
        "inspiration_ids": ["webarena-464", "webarena-545"],
        "surface": (
            "Review edit form Summary Rating only; the range is not printed anywhere on the site."
        ),
        "notes": [
            "Entity 1236 carries 205 (5), 206 (2), 207 (3), 208 (4). Low 2, high 5, both unique "
            "extremes with a one-star gap to the next value in each direction.",
            "Reports > Reviews > By Products prints a frozen average (ratingVoteAggregates) for "
            "this product and no min/max, so the report cannot answer the question.",
        ],
    },
    {
        "id": "praise_count_description_olivia_light_jacket_approved_only_003",
        "product_id": 1396,
        "product": "Olivia 1/4 Zip Light Jacket",
        "sku": "WJ12",
        "style": "explicit",
        "start_path": "/",
        "instruction": (
            "The Olivia 1/4 Zip Light Jacket listing needs an honest line of copy. Open that "
            "product in the catalogue and look at its Product Reviews section, where every review "
            "attached to it is listed with its moderation status. Count only the reviews whose "
            "status is Approved - the ones still sitting in Pending do not count. Then open the "
            "Content section, replace the product description with exactly "
            '"Backed by {n} approved customer review(s)." with that number substituted in, and '
            "save the product."
        ),
        "frame": r"Backed by \d+ approved customer review\(s\)\.",
        "expected": "Backed by 2 approved customer review(s).",
        "value_component": "the_approved_review_count_written_is_two",
        "seed_reviews": 3,
        "injections": [
            review(
                354, 1396, "WJ12", "Olivia 1/4 Zip Light Jacket", "Approved", 4, "Marguerite",
                "Light but warm enough",
                "Packs down to nothing in my bag and still keeps the wind off on morning walks.",
                "2023-05-02 10:12:33",
            ),
            review(
                355, 1396, "WJ12", "Olivia 1/4 Zip Light Jacket", "Approved", 2, "Ollie",
                "Zip sticks halfway",
                "The quarter zip catches halfway every single time I put it on, which spoils an "
                "otherwise nice jacket.",
                "2023-05-03 08:41:05",
            ),
        ],
        "skill_chain": (
            "count one product's reviews that carry the Approved status -> compose the product "
            "description around that count"
        ),
        "derived_from": "quantify_the_praise_bella_tank_approved_only_006",
        "analogues": [ANALOGUE_78, ANALOGUE_543],
        "inspiration_ids": ["webarena-78", "webarena-543"],
        "surface": (
            "The product page's Product Reviews table (ProductEdit.jsx:1754-1793), which prints a "
            "Status cell per row; the same five rows and statuses render on "
            "/admin/review/product/index/productId/1396/. No review is deleted in this task, so "
            "the raw-state table and the getReviews-filtered grid agree."
        ),
        "notes": [
            "Entity 1396 is the only seeded product whose whole review set is Pending (347, 349, "
            "351). The injection adds the two Approved rows, so the answer is 2 while the product "
            "shows 5 reviews - an agent that counts rows writes 5 and scores 0.0.",
            "Status is rendered on both review surfaces, so the discriminator needs no guesswork.",
        ],
    },
    {
        "id": "praise_count_description_electra_bra_top_love_it_004",
        "product_id": 1604,
        "product": "Electra Bra Top",
        "sku": "WB01",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            "Count the Electra Bra Top's customer reviews rated 4 stars or above, then set that "
            'product\'s description to exactly "{count} customer(s) love it!" with the count '
            "filled in."
        ),
        "frame": r"\d+ customer\(s\) love it!",
        "expected": "3 customer(s) love it!",
        "value_component": "the_four_star_plus_count_written_is_three",
        "seed_reviews": 4,
        "injections": [],
        "skill_chain": (
            "count one product's reviews at or above a stated star bound -> compose the product "
            "description around that count"
        ),
        "derived_from": "quantify_the_praise_antonia_racer_tank_love_it_001",
        "analogues": [ANALOGUE_464, ANALOGUE_546],
        "inspiration_ids": ["webarena-464", "webarena-546"],
        "surface": "Review edit form Summary Rating only.",
        "notes": [
            "Entity 1604 carries 316 (3), 317 (4), 318 (4), 319 (4). The bound at 4 excludes "
            "exactly one row, so 3 is the answer and 4 is the answer an agent that skips the "
            "ratings writes.",
            "Official 464's sentence frame, on a product batch 5 did not use, and without the "
            "conditional fallback branch - the branch is a third skill and this batch is exactly "
            "two.",
        ],
    },
    {
        "id": "praise_count_description_erica_sports_bra_below_three_005",
        "product_id": 1620,
        "product": "Erica Evercool Sports Bra",
        "sku": "WB02",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            "How many customer reviews of the Erica Evercool Sports Bra are rated below 3 stars? "
            'Replace that product\'s description with exactly "{n} review(s) sit below 3 stars." '
            "filling in that number."
        ),
        "frame": r"\d+ review\(s\) sit below 3 stars\.",
        "expected": "2 review(s) sit below 3 stars.",
        "value_component": "the_below_three_star_count_written_is_two",
        "seed_reviews": 4,
        "injections": [
            review(
                356, 1620, "WB02", "Erica Evercool Sports Bra", "Approved", 3, "Elnora",
                "Fine for low impact",
                "Fine for a walk or a yoga class, but I would not run in it. Sizing was true to "
                "the chart.",
                "2023-05-04 14:22:19",
            ),
        ],
        "skill_chain": (
            "count one product's reviews below a stated star bound -> compose the product "
            "description around that count"
        ),
        "derived_from": "quantify_the_praise_strike_endurance_tee_critical_005",
        "analogues": [ANALOGUE_464, ANALOGUE_546],
        "inspiration_ids": ["webarena-464", "webarena-546"],
        "surface": "Review edit form Summary Rating only.",
        "notes": [
            "Seed for entity 1620 is 320 (2), 321 (1), 322 (5), 323 (4). The injected 3-star row "
            "is the boundary distractor: 'below 3 stars' is 2, '3 stars or below' is 3.",
            "Task 010 in this lane asks the inclusive form on another product, so the pair "
            "teaches the boundary rather than a number.",
        ],
    },
    {
        "id": "praise_count_description_hera_hoodie_one_star_006",
        "product_id": 1060,
        "product": "Hera Pullover Hoodie",
        "sku": "WH02",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            "Count the one-star customer reviews on the Hera Pullover Hoodie, then replace that "
            'product\'s description with exactly "{n} one-star review(s) need a reply." using '
            "that number."
        ),
        "frame": r"\d+ one-star review\(s\) need a reply\.",
        "expected": "2 one-star review(s) need a reply.",
        "value_component": "the_one_star_count_written_is_two",
        "seed_reviews": 3,
        "injections": [
            review(
                357, 1060, "WH02", "Hera Pullover Hoodie", "Approved", 1, "Delma",
                "Fell apart in a month",
                "The seam under the arm opened up after about a month of ordinary wear. Very "
                "disappointing for the price.",
                "2023-05-05 11:26:40",
            ),
            review(
                358, 1060, "WH02", "Hera Pullover Hoodie", "Approved", 2, "Ronnie",
                "Sleeves are far too short",
                "The body fits me well but the sleeves stop above my wrists, so it is only good "
                "indoors.",
                "2023-05-06 09:58:12",
            ),
        ],
        "skill_chain": (
            "count one product's reviews at an exact star value -> compose the product "
            "description around that count"
        ),
        "derived_from": "quantify_the_praise_strike_endurance_tee_critical_005",
        "analogues": [ANALOGUE_464, ANALOGUE_545],
        "inspiration_ids": ["webarena-464", "webarena-545"],
        "surface": "Review edit form Summary Rating only.",
        "notes": [
            "Seed for entity 1060 is 188 (5), 189 (1), 190 (4). The injection adds one more "
            "1-star row and one 2-star row, so the exact-value answer is 2 while 'two stars or "
            "below' is 3 and the seed alone would say 1.",
            "The injected count moves away from the pristine seed, so a memorised seed answer is "
            "wrong.",
        ],
    },
    {
        "id": "praise_count_description_sybil_running_short_five_star_007",
        "product_id": 2003,
        "product": "Sybil Running Short",
        "sku": "WSH08",
        "style": "terse",
        "start_path": "/admin/catalog/product/",
        "instruction": (
            "Open the Sybil Running Short and read its reviews' star ratings. Set that product's "
            'description to exactly "Loved by {n} five-star reviewer(s)." where n is how many of '
            "its reviews carry a 5-star rating."
        ),
        "frame": r"Loved by \d+ five-star reviewer\(s\)\.",
        "expected": "Loved by 2 five-star reviewer(s).",
        "value_component": "the_five_star_count_written_is_two",
        "seed_reviews": 3,
        "injections": [],
        "skill_chain": (
            "count one product's reviews at the top star value -> compose the product description "
            "around that count"
        ),
        "derived_from": "quantify_the_praise_cora_parachute_pant_five_star_003",
        "analogues": [ANALOGUE_464, ANALOGUE_543],
        "inspiration_ids": ["webarena-464", "webarena-543"],
        "surface": "Review edit form Summary Rating only.",
        "notes": [
            "Entity 2003 carries 301 (5), 302 (4), 303 (5): the five-star count is 2 and the "
            "'4 stars or above' count is 3, so the exact bound matters.",
            "Starts on the Products grid rather than the dashboard, which is one of two non-root "
            "starts in this lane.",
        ],
    },
    {
        "id": "praise_count_description_diana_tights_cute_mentions_008",
        "product_id": 1854,
        "product": "Diana Tights",
        "sku": "WP06",
        "style": "terse",
        "start_path": "/",
        "instruction": (
            'How many Diana Tights reviews mention "cute" in the review body? Replace that '
            'product\'s description with exactly "{n} review(s) call these cute." carrying that '
            "number."
        ),
        "frame": r"\d+ review\(s\) call these cute\.",
        "expected": "2 review(s) call these cute.",
        "value_component": "the_cute_mention_count_written_is_two",
        "seed_reviews": 3,
        "injections": [],
        "skill_chain": (
            "count one product's reviews whose body carries a stated term -> compose the product "
            "description around that count"
        ),
        "derived_from": None,
        "analogues": [ANALOGUE_11, ANALOGUE_543],
        "inspiration_ids": ["webarena-11", "webarena-543"],
        "surface": (
            "The Reviews grid's Review column filter (LegacyReviewGrid.jsx:160 filters `detail`, "
            "case-insensitive substring) combined with the Product or SKU filter, which prints "
            "'N records found'; the same three bodies render in full in the product page's "
            "Product Reviews table."
        ),
        "notes": [
            "Entity 1854's bodies: 248 'These pants are so cute! ...', 249 'good for PJs but "
            "that's about it', 250 'These are my favorite pants. Super cute and soooo comfy.' - "
            "two hits, and no other occurrence of the substring in the three rows.",
            "Only 248 also carries the term in its Title, so a title-only reading gives 1 and a "
            "title-or-body reading gives 2; the instruction says review body, which is what the "
            "grid's Review filter matches.",
            "The grid's Review filter is substring and case-insensitive, so 'cute' inside a "
            "longer word would count - there is none in this product's reviews.",
        ],
    },
    {
        "id": "praise_count_description_prima_bra_top_approved_five_star_009",
        "product_id": 1652,
        "product": "Prima Compete Bra Top",
        "sku": "WB04",
        "style": "explicit",
        "start_path": "/",
        "instruction": (
            "Marketing wants a five-star claim on the Prima Compete Bra Top, but it has to be "
            "defensible. Work through every review attached to that product, checking both the "
            "moderation status shown beside it and the star rating recorded on the review itself. "
            "Count the reviews that are Approved and carry a 5-star rating; a review still in "
            "Pending does not count however many stars it has. Then replace the product's "
            'description with exactly "{n} five-star review(s) so far." with that count filled '
            "in, and save the product."
        ),
        "frame": r"\d+ five-star review\(s\) so far\.",
        "expected": "0 five-star review(s) so far.",
        "value_component": "the_approved_five_star_count_written_is_zero",
        "seed_reviews": 3,
        "injections": [
            review(
                359, 1652, "WB04", "Prima Compete Bra Top", "Pending", 5, "Verona",
                "Perfect for competition day",
                "Wore this through a whole meet and never had to adjust it once. Buying a second "
                "one in another colour.",
                "2023-05-07 09:03:44",
            ),
        ],
        "skill_chain": (
            "count one product's reviews that are Approved and at the top star value -> compose "
            "the product description around that count"
        ),
        "derived_from": "quantify_the_praise_zoe_tank_no_praise_fallback_004",
        "analogues": [ANALOGUE_464, ANALOGUE_78],
        "inspiration_ids": ["webarena-464", "webarena-78"],
        "surface": (
            "Status from the product page's Product Reviews table (or the Reviews grid's Status "
            "column), star value from the review edit form's Summary Rating line."
        ),
        "notes": [
            "Seed for entity 1652 is 327 (2), 328 (4), 329 (3) - no five-star row at all. The "
            "injected Pending five-star row satisfies every part of the predicate except status, "
            "so an agent that ignores the status writes 1 and scores 0.0.",
            "The correct answer is zero, which no amount of optimistic guessing produces: this is "
            "the lane's check that the count is genuinely read rather than assumed positive.",
            "No conditional fallback wording - a branch would be a third skill.",
        ],
    },
    {
        "id": "praise_count_description_autumn_pullie_three_or_below_010",
        "product_id": 1076,
        "product": "Autumn Pullie",
        "sku": "WH03",
        "style": "terse",
        "start_path": "/admin/review/product/index/",
        "instruction": (
            "Count the Autumn Pullie reviews rated 3 stars or below, then replace that product's "
            'description with exactly "{n} review(s) at 3 stars or below." carrying that number.'
        ),
        "frame": r"\d+ review\(s\) at 3 stars or below\.",
        "expected": "3 review(s) at 3 stars or below.",
        "value_component": "the_three_or_below_count_written_is_three",
        "seed_reviews": 3,
        "injections": [
            review(
                360, 1076, "WH03", "Autumn Pullie", "Approved", 3, "Loretta",
                "Nice colour, ordinary fabric",
                "The colour is exactly as pictured, but the fleece is thinner than I expected for "
                "the price.",
                "2023-05-08 16:47:52",
            ),
        ],
        "skill_chain": (
            "count one product's reviews at or below a stated star bound -> compose the product "
            "description around that count"
        ),
        "derived_from": "quantify_the_praise_strike_endurance_tee_critical_005",
        "analogues": [ANALOGUE_464, ANALOGUE_344],
        "inspiration_ids": ["webarena-464", "webarena-344"],
        "surface": "Review edit form Summary Rating only.",
        "notes": [
            "Seed for entity 1076 is 191 (4), 192 (3), 193 (2); the injected Approved 3-star row "
            "makes the inclusive answer 3 where the pristine seed would say 2.",
            "Inclusive counterpart to task 005's exclusive bound on another product.",
            "Starts on the Reviews grid, the second of two non-root starts in this lane.",
        ],
    },
]


# --------------------------------------------------------------------------- io

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)


def dump(path, obj):
    write(path, json.dumps(obj, indent=2) + "\n")


# ------------------------------------------------------------------ reward code

REWARD_HEAD = '''"""Deterministic reward for {tid}.

Success criteria:
  * productDescriptionOverrides holds exactly one key, "{key}" ({product}).
  * That description is exactly the sentence the task specifies, in the required
    form.
  * The figure it carries is the one derived from the product's own customer
    reviews: {expected}

Reads only the post-episode state out of the immutable evidence bundle. Ground
truth is fixed by the review corpus of webarena_shopping_admin_mock in ./hub/
(reviews.json, product entity {key}){setup_clause}.
"""

import re

TARGET_KEY = "{key}"
TAG_RE = re.compile(r"<[^>]*>")
WS_RE = re.compile(r"\\s+")
FRAME_RE = re.compile(r"{frame}")
EXACT_RE = re.compile(r"{exact}")
'''

REWARD_BODY = '''

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


def _overlay(state):
    value = state.get("productDescriptionOverrides")
    return value if isinstance(value, dict) else {}


def _plain(text):
    if not isinstance(text, str):
        return ""
    out = TAG_RE.sub(" ", text)
    out = out.replace("&nbsp;", " ").replace("&amp;", "&")
    out = out.replace("&#39;", "'").replace("&quot;", '"')
    out = out.replace("\\u2019", "'").replace("\\u2018", "'")
    out = out.replace("\\u201c", '"').replace("\\u201d", '"')
    out = out.replace("\\u2013", "-").replace("\\u2014", "-").replace("\\u2212", "-")
    return WS_RE.sub(" ", out).strip()


COMPONENT_WEIGHTS = {
    "only_the_target_product_description_rewritten_in_the_required_form": 0.3,
    "__VALUE_COMPONENT__": 0.7,
}


def _checks(state):
    overlay = _overlay(state)
    text = _plain(overlay.get(TARGET_KEY))
    sole = set(overlay.keys()) == {TARGET_KEY}
    return {
        "only_the_target_product_description_rewritten_in_the_required_form":
            bool(sole and FRAME_RE.fullmatch(text)),
        "__VALUE_COMPONENT__": bool(sole and EXACT_RE.fullmatch(text)),
    }
'''

REWARD_TAIL = '''

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

NEMO_REWARD_HEAD = '''"""NeMo-Gym reward program for {tid}.

Implements exactly the rubric of reward.py, reading the post-episode state from
GET /go?sid=... instead of a frozen evidence bundle, and printing
REWARD: <float> on every output path including the error path.

Self-contained: standard library plus requests, which is present in
cuagym/requirements.txt.
"""

import re
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

TARGET_KEY = "{key}"
TAG_RE = re.compile(r"<[^>]*>")
WS_RE = re.compile(r"\\s+")
FRAME_RE = re.compile(r"{frame}")
EXACT_RE = re.compile(r"{exact}")
'''

NEMO_REWARD_BODY = '''

def _overlay(state):
    value = state.get("productDescriptionOverrides")
    return value if isinstance(value, dict) else {}


def _plain(text):
    if not isinstance(text, str):
        return ""
    out = TAG_RE.sub(" ", text)
    out = out.replace("&nbsp;", " ").replace("&amp;", "&")
    out = out.replace("&#39;", "'").replace("&quot;", '"')
    out = out.replace("\\u2019", "'").replace("\\u2018", "'")
    out = out.replace("\\u201c", '"').replace("\\u201d", '"')
    out = out.replace("\\u2013", "-").replace("\\u2014", "-").replace("\\u2212", "-")
    return WS_RE.sub(" ", out).strip()


COMPONENT_WEIGHTS = {
    "only_the_target_product_description_rewritten_in_the_required_form": 0.3,
    "__VALUE_COMPONENT__": 0.7,
}


def _checks(state):
    overlay = _overlay(state)
    text = _plain(overlay.get(TARGET_KEY))
    sole = set(overlay.keys()) == {TARGET_KEY}
    return {
        "only_the_target_product_description_rewritten_in_the_required_form":
            bool(sole and FRAME_RE.fullmatch(text)),
        "__VALUE_COMPONENT__": bool(sole and EXACT_RE.fullmatch(text)),
    }


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

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {tid}.

{summary}

The fixture is inlined as a raw triple-quoted JSON literal and parsed with
json.loads, so no JavaScript literal reaches Python source and no backslash
escape is eaten by the Python parser. Standard library plus requests only.

The state document is read back from GET /go, mutated in place and posted whole,
which is correct whether the mock merges a partial `set` or replaces with it.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

NEW_REVIEWS = json.loads(r"""{fixture}""")

SEEDED_REVIEW_COUNT = 351
TARGET_PRODUCT_ID = {pid}
SEEDED_TARGET_REVIEW_COUNT = {seeded}


def fail(message):
    print("SETUP FAILED: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    got = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    got.raise_for_status()
    payload = got.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not state:
        fail("GET /go returned neither current_state nor initial_state")

    reviews = state.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != SEEDED_REVIEW_COUNT:
        fail("expected the pristine 351-row review corpus")

    seeded_ids = set()
    on_target = 0
    for row in reviews:
        seeded_ids.add(str(row.get("review_id")))
        if str(row.get("entity_pk_value")) == str(TARGET_PRODUCT_ID):
            on_target += 1
    if on_target != SEEDED_TARGET_REVIEW_COUNT:
        fail("the target product does not carry its seeded review set")
    for row in NEW_REVIEWS:
        if str(row.get("review_id")) in seeded_ids:
            fail("an injected review id collides with a seeded row")

    overrides = state.get("productDescriptionOverrides")
    if isinstance(overrides, dict) and str(TARGET_PRODUCT_ID) in overrides:
        fail("the target product already carries a description override")

    document = dict(state)
    document["reviews"] = list(reviews) + NEW_REVIEWS

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": document}},
        timeout=60,
    )
    response.raise_for_status()
    print("SETUP OK")


main()
'''

REPLAY_TEMPLATE = '''"""Golden replay draft for {tid}.

DRAFT ONLY - written during authoring, not executed. The verification phase owns
the real replay. Navigation is click-only from start_path "{start}"; no
page.goto() after the initial landing.

Route notes taken from source:
  * "/" redirects to /admin/admin/dashboard/.
  * Left rail (src/components/layout/adminMenu.js): Catalog > Products (:52),
    Marketing > User Content > All Reviews (:118).
  * Products grid: the "Search by keyword" box narrows the 2040-row catalogue;
    each row carries an Edit link to /admin/catalog/product/edit/id/<entity_id>/.
    Beware the 15 configurable children named "<Name>-<size>-<colour>" - the
    reviews and the graded description belong to the parent row, entity {pid}.
  * Product edit page: collapsible sections are buttons carrying their own title.
    "Product Reviews" (ProductEdit.jsx:1462) lists ID / Status / Title / Nickname
    / Review with a per-row Edit link and an "All Reviews" link to
    /admin/review/product/index/productId/{pid}/. It shows NO star rating - that
    is why each review has to be opened when the predicate is star-based.
  * Review edit form (Reviews.jsx): "Summary Rating" reads "<n> star(s)" and the
    Detailed Rating table has the matching "#Rating_<n>" radio checked. "#back"
    returns to the review grid.
  * Product description: expand the "Content" section, clear and retype
    "#product-description", then press "#save-button" and expect
    "You saved the product."

Target: {product} (entity {pid}). Expected description: {expected}

Steps:
{steps_doc}
"""

STEPS = {steps!r}
'''


def steps_for(task):
    pid = task["product_id"]
    product = task["product"]
    start = task["start_path"]
    steps = []
    if start == "/":
        steps.append('Land on "/" (redirects to /admin/admin/dashboard/).')
        steps.append("Click Catalog in the left rail, then Products.")
    elif start == "/admin/catalog/product/":
        steps.append('Land on "/admin/catalog/product/" (the Products grid).')
    else:
        steps.append('Land on "/admin/review/product/index/" (the Reviews grid).')
        steps.append(
            'Filter the Product column for "%s" and press Search to see only that '
            "product's reviews." % product
        )
        steps.append(
            "Click Catalog in the left rail, then Products, to reach the product itself."
        )
    if start != "/admin/review/product/index/":
        steps.append(
            'Type "%s" into the grid\'s Search by keyword box and search.' % product
        )
    else:
        steps.append(
            'Type "%s" into the grid\'s Search by keyword box and search.' % product
        )
    steps.append(
        "Click Edit on the %s row - the parent, not a -size-colour child - to open "
        "/admin/catalog/product/edit/id/%d/." % (product, pid)
    )
    steps.append(
        'Expand the "Product Reviews" section and note the review ids and statuses listed there.'
    )
    steps.append(
        'Open each listed review with its row Edit link, read the "Summary Rating" line '
        '(or the checked "#Rating_<n>" radio), then click "#back".'
    )
    steps.append("Apply the task's predicate to those reviews and take the figure it asks for.")
    steps.append("Return to the product edit page for %s via Catalog > Products." % product)
    steps.append(
        'Expand the "Content" section, clear "#product-description" and type: %s'
        % task["expected"]
    )
    steps.append('Press "#save-button" and confirm the "You saved the product." message.')
    return steps


def build(task):
    tid = task["id"]
    key = str(task["product_id"])
    bundle = os.path.join(SITE_DIR, tid)
    has_setup = bool(task["injections"])
    exact = "".join(
        ("\\" + ch) if ch in ".^$*+?()[]{}|\\" else ch for ch in task["expected"]
    )

    setup_clause = (
        " together with the precondition this bundle's initial_setup.py injects"
        if has_setup
        else ""
    )

    reward = (
        REWARD_HEAD.format(
            tid=tid,
            key=key,
            product=task["product"],
            expected=task["expected"],
            frame=task["frame"],
            exact=exact,
            setup_clause=setup_clause,
        )
        + REWARD_BODY.replace("__VALUE_COMPONENT__", task["value_component"])
        + REWARD_TAIL
    )
    write(os.path.join(bundle, "reward.py"), reward)

    nemo_reward = (
        NEMO_REWARD_HEAD.format(
            tid=tid, url=URL_PLACEHOLDER, key=key, frame=task["frame"], exact=exact
        )
        + NEMO_REWARD_BODY.replace("__VALUE_COMPONENT__", task["value_component"])
    )
    write(os.path.join(bundle, "nemo_reward.py"), nemo_reward)

    setup_source = None
    if has_setup:
        summary = "Injected precondition: " + "; ".join(
            "review %d on %s (%d) - %s at %d star(s)"
            % (r["review_id"], task["product"], task["product_id"], r["status_code"],
               int(r["rating_summary"]))
            for r in task["injections"]
        ) + "."
        setup_source = SETUP_TEMPLATE.format(
            tid=tid,
            summary=summary,
            url=URL_PLACEHOLDER,
            fixture=json.dumps(task["injections"], indent=2),
            pid=task["product_id"],
            seeded=task["seed_reviews"],
        )
        write(os.path.join(bundle, "initial_setup.py"), setup_source)

    injected = [
        "Review %d on %s (%d): %s, %d star(s), nickname %s."
        % (r["review_id"], task["product"], task["product_id"], r["status_code"],
           int(r["rating_summary"]), r["nickname"])
        for r in task["injections"]
    ]

    dump(
        os.path.join(bundle, "task_instruction.json"),
        {
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": APP_DIR,
            "start_path": task["start_path"],
            "difficulty": "medium",
            "success_criteria": [
                'productDescriptionOverrides holds exactly one key, "%s" (%s).'
                % (key, task["product"]),
                "That description is the sentence the task specifies, in the required form.",
                'The figure it carries is the one derived from the product\'s own reviews: "%s".'
                % task["expected"],
            ],
        },
    )

    dump(
        os.path.join(bundle, "task.json"),
        {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
            "apps": [
                {
                    "name": APP_DIR,
                    "source_name": "shopping_admin",
                    "base_url_env": "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL",
                    "start_path": task["start_path"],
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
                "skills": ["R3", "A7"],
                "skill_chain": task["skill_chain"],
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "topic": "praise count description",
                "batch": "batch6",
                "lane": 47,
                "inspiration_ids": task["inspiration_ids"],
                "review_surface": task["surface"],
                "authoring_notes": task["notes"],
                "injected_preconditions": injected,
            },
        },
    )

    payload = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_source,
                "eval_reward_code": nemo_reward,
            },
        }
    }
    dump(os.path.join(bundle, "nemo_task.json"), payload)

    steps = steps_for(task)
    steps_doc = "\n".join("  %d. %s" % (i + 1, s) for i, s in enumerate(steps))
    write(
        os.path.join(REPLAY_DIR, tid + ".py"),
        REPLAY_TEMPLATE.format(
            tid=tid,
            start=task["start_path"],
            pid=task["product_id"],
            product=task["product"],
            expected=task["expected"],
            steps_doc=steps_doc,
            steps=steps,
        ),
    )
    return payload


def main():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    rows = []
    for task in TASKS:
        rows.append(build(task))
    dump(
        os.path.join(LANE_DIR, "index.json"),
        {
            "schema_version": 2,
            "tasks": [
                {"task_id": t["id"], "path": "%s/task.json" % t["id"]} for t in TASKS
            ],
        },
    )
    write(
        os.path.join(LANE_DIR, "nemo_tasks.jsonl"),
        "".join(json.dumps(r) + "\n" for r in rows),
    )
    print("wrote %d bundles" % len(TASKS))


main()
