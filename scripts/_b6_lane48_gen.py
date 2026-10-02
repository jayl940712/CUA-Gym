#!/usr/bin/env python3
"""Batch-6 lane 48 bundle generator — shopping_admin, R3 -> A4.

Writes ten `matched_review_set_purge_*` bundles under
output/tasks/shopping_admin/, plus GENERATION.md and replay drafts under
output/tasks/shopping_admin/_batches/matched_review_set_purge/.

Nothing here validates anything; it only emits files.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/shopping_admin")
BATCH = os.path.join(OUT, "_batches/matched_review_set_purge")
SEED = os.path.join(ROOT, "hub/websites/webarena_shopping_admin_mock/src/data/reviews.json")

APP_DIR = "webarena_shopping_admin_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

SEED_REVIEWS = json.load(open(SEED))
SEED_TOTAL = len(SEED_REVIEWS)                       # 351
SEED_PENDING = sorted(r["review_id"] for r in SEED_REVIEWS if r["status_id"] == 2)
SEED_TITLES = {r["title"] for r in SEED_REVIEWS}
SEED_DETAILS = {r["detail"] for r in SEED_REVIEWS}
SEED_NICKS = {r["nickname"] for r in SEED_REVIEWS}

PRODUCTS = {
    "cruise": (39, "24-MG05", "Cruise Dual Analog Watch"),
    "iris": (1428, "WS03", "Iris Workout Top"),
    "josie": (1236, "WJ02", "Josie Yoga Jacket"),
    "electra": (1604, "WB01", "Electra Bra Top"),
    "helios": (676, "MT04", "Helios Endurance Tank"),
    "fusion": (6, "24-MB02", "Fusion Backpack"),
    "olivia": (1396, "WJ12", "Olivia 1/4 Zip Light Jacket"),
    "circe": (1210, "WH12", "Circe Hooded Ice Fleece"),
}


def row(rid, product, stars, title, detail, nickname, when, status=2):
    pk, sku, name = PRODUCTS[product]
    return {
        "review_id": rid,
        "created_at": when,
        "entity_id": 1,
        "entity_pk_value": pk,
        "status_id": status,
        "status_code": "Pending" if status == 2 else ("Approved" if status == 1 else "Not Approved"),
        "store_id": 1,
        "title": title,
        "detail": detail,
        "nickname": nickname,
        "customer_id": None,
        "sku": sku,
        "product_name": name,
        "ratings": [{
            "rating_id": 4,
            "rating_code": "Rating",
            "option_id": 15 + stars,
            "value": stars,
            "percent": 20 * stars,
        }],
        "rating_summary": float(stars),
    }


# --------------------------------------------------------------- injections

INJ_005 = [
    row(354, "cruise", 5, "Keeps perfect time",
        "Keeps perfect time after three weeks on my wrist and the strap has not stretched at all.",
        "Marguerite Bell", "2023-05-02 09:12:41"),
    row(355, "cruise", 4, "Dial is easier to read than I expected",
        "The dial is easier to read at a glance than I expected from the photos, even in low light.",
        "Ignacio Duarte", "2023-05-02 10:03:17"),
    row(356, "cruise", 2, "Clasp pops open",
        "The clasp pops open when I put a jacket on, which is not what I want from a daily watch.",
        "Rosalind Achebe", "2023-05-02 11:44:05"),
    row(357, "cruise", 3, "Fine, nothing special",
        "It is a fine watch for the money, nothing special, and the second hand ticks a little loudly.",
        "Terrence Okafor", "2023-05-03 08:21:36"),
    row(358, "cruise", 5, "Second one I have bought",
        "This is the second one I have bought, the first went to my brother and he wears it daily.",
        "Delphine Marchetti", "2023-05-03 12:55:02"),
    row(359, "iris", 4, "Straps stay put through a class",
        "The straps stay put through an entire class and the fabric dries out fast afterwards.",
        "Beatriz Salgado", "2023-05-03 14:09:58"),
]

INJ_006 = [
    row(354, "cruise", 5, "Bought it after seeing it on a friend",
        "Bought this after seeing it on a friend and it has been on my wrist every day since.",
        "Marisol Vega", "2023-05-04 09:31:12"),
    row(355, "josie", 5, "Warm without being bulky",
        "Warm without being bulky, which is exactly what I wanted for the walk to the studio.",
        "Marisol Vega", "2023-05-04 09:38:44"),
    row(356, "helios", 4, "Holds up to repeated washing",
        "Holds up to repeated washing with no pilling so far, and the colour has not faded.",
        "Marisol Vega", "2023-05-04 09:47:20"),
    row(357, "electra", 3, "Sizing runs small",
        "Sizing runs small through the band, so order one size up if you are between sizes.",
        "Dwayne Ferris", "2023-05-04 15:12:03"),
    row(358, "iris", 4, "Good for hot studio sessions",
        "Good for hot studio sessions, it breathes far better than the top it replaced.",
        "Priya Raman", "2023-05-05 08:26:49"),
]

INJ_007 = [
    row(354, "cruise", 2, "Strap smells of solvent",
        "The strap smelled strongly of solvent out of the box and took a week to air out.",
        "Corinne Baptiste", "2023-05-06 09:14:22"),
    row(355, "josie", 2, "Zip catches on the lining",
        "The zip catches on the lining about half the time, which makes it awkward to take off.",
        "Emeka Nwosu", "2023-05-06 10:02:55"),
    row(356, "helios", 3, "Decent but the hem rides up",
        "Decent tank for the price but the hem rides up whenever I raise my arms overhead.",
        "Sunniva Halvorsen", "2023-05-06 11:37:41"),
    row(357, "electra", 1, "Seam split on the first wear",
        "The seam under the arm split on the very first wear and I had to send it straight back.",
        "Ximena Ocampo", "2023-05-06 16:48:09"),
]

INJ_008 = [
    row(354, "fusion", 5, "Carries a full week of kit",
        "Carries a full week of kit and the shoulder padding has not flattened out yet.",
        "Roderick Vance", "2023-05-07 09:05:11", status=1),
    row(355, "fusion", 4, "Water bottle pocket finally fits",
        "The water bottle pocket finally fits a wide bottle, which the older model never did.",
        "Anneke Vermeer", "2023-05-07 09:52:38", status=1),
    row(356, "fusion", 2, "Zipper pull snapped",
        "The zipper pull on the main compartment snapped inside two months of school runs.",
        "Idris Balogun", "2023-05-07 13:24:56", status=1),
    row(357, "fusion", 5, "Third one in the house",
        "This is the third one in our house and it is the only bag my kids do not destroy.",
        "Lucia Fontaine", "2023-05-08 08:17:29", status=1),
]

INJ_009 = [
    row(354, "josie", 4, "Cuffs stay down over gloves",
        "The cuffs stay down over gloves on a cold morning, which is why I keep reaching for it.",
        "Solveig Kristiansen", "2023-05-09 09:22:14"),
    row(355, "electra", 5, "Support without a wire",
        "Real support without a wire anywhere near it, and it survived a half marathon already.",
        "Nadira Haddad", "2023-05-09 10:41:07"),
    row(356, "helios", 3, "Fabric is thinner than the photos suggest",
        "The fabric is thinner than the photos suggest, fine indoors but not for a windy run.",
        "Bartholomew Quinn", "2023-05-09 12:03:52"),
    row(357, "helios", 4, "Cool on a long ride",
        "Stayed cool on a long ride in July heat and rinsed clean without holding any odour.",
        "Yusra Abdallah", "2023-05-09 15:38:26"),
]

INJ_010 = [
    row(354, "olivia", 4, "Pockets are deep enough for a phone",
        "The pockets are deep enough for a phone, which almost no jacket in this price range manages.",
        "Ottoline Faraday", "2023-05-10 09:11:33"),
    row(355, "olivia", 2, "Sleeves are cut short",
        "The sleeves are cut short on me and the cuff sits well above the wrist bone.",
        "Kwabena Mensah", "2023-05-10 10:26:04"),
    row(356, "circe", 5, "Hood actually stays up",
        "The hood actually stays up in a stiff wind instead of blowing back every few steps.",
        "Marcelline Dubois", "2023-05-10 11:49:47"),
    row(357, "circe", 3, "Fleece sheds a little",
        "The fleece sheds a little onto darker layers for the first few wears, then settles down.",
        "Tobias Lindqvist", "2023-05-10 13:15:29"),
    row(358, "josie", 4, "Light enough for spring",
        "Light enough for spring evenings and it packs down small into a gym bag.",
        "Henrike Vogel", "2023-05-11 08:44:18"),
    row(359, "josie", 2, "Colour is duller in person",
        "The colour is noticeably duller in person than on screen, which was a letdown.",
        "Paolo Ferraro", "2023-05-11 09:37:55"),
]


def audit(rows):
    """Duplicate audit over an injected fixture, against itself and the seed."""
    problems = []
    for r in rows:
        if r["title"] in SEED_TITLES:
            problems.append("title collides with seed: " + r["title"])
        if r["detail"] in SEED_DETAILS:
            problems.append("detail collides with seed: " + r["detail"][:40])
        if r["nickname"] in SEED_NICKS:
            problems.append("nickname collides with seed: " + r["nickname"])
    # class 1: relaxed key excluding nickname
    keys = {}
    for r in rows:
        k = (r["entity_pk_value"], r["title"], r["detail"], r["ratings"][0]["value"])
        keys.setdefault(k, []).append(r["review_id"])
    for k, v in keys.items():
        if len(v) > 1:
            problems.append("relaxed-key duplicate: %s" % (v,))
    # class 2: self-concatenated nickname
    nicks = sorted({r["nickname"] for r in rows} | SEED_NICKS)
    for a in {r["nickname"] for r in rows}:
        if len(a) % 2 == 0 and a and a[: len(a) // 2] == a[len(a) // 2:]:
            problems.append("self-concatenated nickname: " + a)
        for b in nicks:
            if a != b and a == b + b:
                problems.append("nickname %s is %s doubled" % (a, b))
    # class 3: null rating
    for r in rows:
        if not r["ratings"] or r["ratings"][0].get("value") in (None, ""):
            problems.append("null rating on %s" % r["review_id"])
    return problems


# ------------------------------------------------------------------- tasks

def T(**kw):
    return kw


TASKS = [
    T(
        task_id="matched_review_set_purge_busiest_pending_product_001",
        style="terse", shape="retrieval_writeback",
        instruction=(
            "Two products have reviews waiting in moderation. Whichever of the two has more "
            "waiting, delete every pending review of that product from the Pending Reviews grid."
        ),
        injection=None,
        delete={347, 349, 351},
        status_targets={}, extra_pending=[],
        criteria=[
            "state.deletedReviewIds is exactly [347, 349, 351] - the three pending reviews of "
            "Olivia 1/4 Zip Light Jacket, the busier of the two queued products.",
            "No review's status_id changed: 352 and 353 are still Pending (2) and every other "
            "review is still Approved (1), and state.reviews still holds 351 rows.",
        ],
        chain="count the pending reviews per product in the moderation queue -> mass-delete the "
              "whole queue of the product with more of them",
        analogues=["Delete all pending negative reviews for Circe Hooded Ice Fleece"],
        derived_from="review_purge_then_report_olivia_jacket_count_001",
        notes=[
            "Pending queue is 5 rows over 2 products: Olivia 1/4 Zip Light Jacket (1396) has 347, "
            "349, 351; Circe Hooded Ice Fleece (1210) has 352, 353. Margin 3 vs 2, no tie.",
            "deleteReviews (AppContext.jsx:303-306) writes deletedReviewIds; getReviews "
            "(selectors.js:252-259) filters it and Reviews.jsx:124 renders from getReviews.",
            "The target product is never named, so an agent that skips the count and purges Circe "
            "scores 0.0.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_sub_four_star_queue_002",
        style="terse", shape="bulk_mutation",
        instruction=(
            "In the Pending Reviews grid, delete every review that rated the product below four "
            "stars. Reviews rated four or five stars must stay pending."
        ),
        injection=None,
        delete={349, 351, 353},
        status_targets={}, extra_pending=[],
        criteria=[
            "state.deletedReviewIds is exactly [349, 351, 353] - the 3-star, 1-star and 1-star "
            "pending reviews.",
            "347 and 352 are still Pending (2), every other review is still Approved (1), and "
            "state.reviews still holds 351 rows.",
        ],
        chain="read the star rating of each of the five queued reviews -> mass-delete the "
              "sub-four-star ones",
        analogues=["Delete all pending reviews with less than 4 stars"],
        derived_from="review_purge_then_report_olivia_jacket_count_001",
        notes=[
            "Stars: 347=5, 349=3, 351=1, 352=4, 353=1. The grid carries no rating column and no "
            "rating filter (LegacyReviewGrid.jsx:414-436), so each of the five must be opened.",
            "Batch 5's adjacent task purged only the Olivia rows and then wrote a report figure; "
            "this one is the whole queue and grades only the resulting collection.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_four_star_approvals_003",
        style="terse", shape="bulk_mutation",
        instruction=(
            "Reviews waiting in moderation that gave four or more stars belong in the store. "
            "Approve exactly those from the Pending Reviews grid; leave the rest pending."
        ),
        injection=None,
        delete=set(),
        status_targets={347: 1, 352: 1}, extra_pending=[],
        criteria=[
            "Reviews 347 and 352 are now Approved (status_id 1).",
            "349, 351 and 353 are still Pending (2), every other review is still Approved, "
            "state.deletedReviewIds is empty and state.reviews still holds 351 rows.",
        ],
        chain="read the star rating of each queued review -> mass Update Status the four-star-plus "
              "ones to Approved",
        analogues=["Approve reviews with four stars or higher to display in our store."],
        derived_from="review_purge_then_report_circe_four_star_approve_010",
        notes=[
            "Update Status is the only mass action that takes a second argument "
            "(LegacyReviewGrid.jsx:271 -> Reviews.jsx:147-158); a blank Status select no-ops.",
            "347 is 5 stars and 352 is 4 stars; 349 (3), 351 (1) and 353 (1) stay pending.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_disappointed_keyword_004",
        style="explicit", shape="bulk_mutation",
        instruction=(
            "Open Marketing > All Reviews and filter the Review column on the word disappointed to "
            "see how many reviews mention it. Then use the grid's Update Status mass action to set "
            "exactly those reviews to Not Approved. Delete nothing."
        ),
        injection=None,
        delete=set(),
        status_targets={37: 3, 146: 3, 168: 3, 172: 3, 351: 3, 353: 3}, extra_pending=[],
        criteria=[
            "Reviews 37, 146, 168, 172, 351 and 353 - the six whose Review text contains "
            "'disappointed' - are all Not Approved (status_id 3).",
            "Every other review is unchanged (347, 349 and 352 still Pending, the rest Approved), "
            "state.deletedReviewIds is empty and state.reviews still holds 351 rows.",
        ],
        chain="count the reviews whose body mentions 'disappointed' -> mass Update Status that "
              "matched set to Not Approved",
        analogues=[
            'Tell me the the number of reviews that our store received by far that mention term "disappointed"'
        ],
        derived_from=None,
        notes=[
            "The Review-column filter is a case-insensitive substring on `detail` only (LegacyReviewGrid.jsx:160, `contains` at :70), and the match count renders as `N records found` at :374. All six "
            "hits carry the word in `detail` and none in `title`, so the filtered set is exactly "
            "the intended set; 'disappoint' as a prefix matches the same six rows.",
            "Six rows at the default page size of 20 (LegacyReviewGrid.jsx:94), so the matched set "
            "is one page and Select All == Select Visible here.",
            "Four of the six are Approved and two are Pending, so an agent that works only from "
            "the Pending queue lands on 2 of 6 and scores 0.0.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_queue_over_two_005",
        style="terse", shape="retrieval_writeback",
        instruction=(
            "The moderation queue spans several products. For each product with more than two "
            "reviews waiting, approve all of that product's pending reviews. Every other queued "
            "review stays pending."
        ),
        injection=INJ_005,
        delete=set(),
        status_targets={347: 1, 349: 1, 351: 1, 354: 1, 355: 1, 356: 1, 357: 1, 358: 1},
        extra_pending=[354, 355, 356, 357, 358, 359],
        criteria=[
            "Reviews 354-358 (Cruise Dual Analog Watch, 5 waiting) and 347, 349, 351 "
            "(Olivia 1/4 Zip Light Jacket, 3 waiting) are all Approved (status_id 1).",
            "352, 353 (Circe, 2 waiting) and 359 (Iris Workout Top, 1 waiting) are still Pending, "
            "every seeded Approved review is unchanged, deletedReviewIds is empty and "
            "state.reviews holds 357 rows.",
        ],
        chain="count the pending reviews per product -> mass Update Status the queues above the "
              "threshold to Approved",
        analogues=["Approve reviews with four stars or higher to display in our store."],
        derived_from=None,
        notes=[
            "Injected queue: Cruise 5, Olivia 3, Circe 2, Iris 1 - the >2 boundary falls cleanly "
            "between 3 and 2, so the matched set is exactly Cruise + Olivia.",
            "11 queued rows at page size 20: one page, and Select All selects every filtered row "
            "across pages anyway (LegacyReviewGrid.jsx:260-266).",
            "An agent that approves only the biggest queue (Cruise) scores 0.0.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_repeat_reviewer_006",
        style="terse", shape="bulk_mutation",
        instruction=(
            "One shopper has several reviews stuck in the moderation queue; everyone else has one. "
            "Delete every queued review from that shopper, using the Pending Reviews grid."
        ),
        injection=INJ_006,
        delete={354, 355, 356},
        status_targets={}, extra_pending=[354, 355, 356, 357, 358],
        criteria=[
            "state.deletedReviewIds is exactly [354, 355, 356] - the three queued reviews signed "
            "Marisol Vega.",
            "Every other review keeps its status (347, 349, 351, 352, 353, 357, 358 Pending, the "
            "rest Approved) and state.reviews holds 356 rows.",
        ],
        chain="count queued reviews per nickname -> mass-delete the whole set left by the one "
              "repeat nickname",
        analogues=["Delete all reviews from the scammer Arden"],
        derived_from=None,
        notes=[
            "Marisol Vega appears 3 times in the queue (354 Cruise, 355 Josie, 356 Helios); the "
            "other 7 queued nicknames appear once each, including the five seeded ones.",
            "The nickname is never stated, so the retrieval is the whole task: the Nickname column "
            "must be read or sorted before anything is selected.",
            "Marisol Vega's three rows carry three different products, titles and bodies, so the "
            "matched set holds no content duplicate under any de-dup key.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_one_star_queue_007",
        style="terse", shape="bulk_mutation",
        instruction=(
            "Delete every review in the moderation queue that gave the product a single star. "
            "The rest of the queue stays exactly as it is."
        ),
        injection=INJ_007,
        delete={351, 353, 357},
        status_targets={}, extra_pending=[354, 355, 356, 357],
        criteria=[
            "state.deletedReviewIds is exactly [351, 353, 357] - the three one-star reviews in "
            "the queue.",
            "347, 349, 352, 354, 355 and 356 are still Pending, every other review is still "
            "Approved, and state.reviews holds 355 rows.",
        ],
        chain="read the star rating of every queued review -> mass-delete the one-star ones",
        analogues=["Delete all pending negative reviews"],
        derived_from=None,
        notes=[
            "Queue after injection is 9 rows with stars 5, 3, 1, 4, 1, 2, 2, 3, 1. The two-star "
            "rows (354, 355) are deliberate near-misses for an agent that reads 'negative' as "
            "'below three'.",
            "Ratings live only on the edit form, so all nine rows must be opened; nine is small "
            "enough for that to be reasonable.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_top_reviewed_product_008",
        style="explicit", shape="retrieval_writeback",
        instruction=(
            "Open Reports > Reviews > By Products and find the product with the highest review "
            "count. Then, in Marketing > All Reviews, use the Update Status mass action to set "
            "every review of that product, and only that product, to Not Approved."
        ),
        injection=INJ_008,
        delete=set(),
        status_targets={3: 3, 4: 3, 5: 3, 354: 3, 355: 3, 356: 3, 357: 3},
        extra_pending=[],
        criteria=[
            "All seven reviews of Fusion Backpack (3, 4, 5, 354, 355, 356, 357) are Not Approved "
            "(status_id 3).",
            "The five seeded pending reviews are still Pending, every other review is still "
            "Approved, deletedReviewIds is empty and state.reviews holds 355 rows.",
        ],
        chain="read the per-product review counts in Reports > Reviews > By Products -> mass "
              "Update Status the whole review set of the top product to Not Approved",
        analogues=["Delete all negative reviews for Sybil running short"],
        derived_from=None,
        notes=[
            "ProductReviewsReportBody recomputes review_cnt from getReviews(state) "
            "(LegacyReports.jsx:801-826) and the grid opens on review_cnt DESC (:877-878), so the "
            "winner is row 1. Its 'Show Reviews' link goes to "
            "/admin/review/product/index/productId/6/ (:862), which is the click path to the "
            "matched set.",
            "Injection lifts Fusion Backpack from 3 reviews to 7; the next-highest products sit at "
            "4 (nine of them), so the margin is 3 and the maximum is unique.",
            "The Average / Average (Approved) columns come from the frozen ratingVoteAggregates "
            "and are deliberately not graded.",
            "Seven rows under the productId pre-filter: one page at the default page size of 20.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_single_pending_products_009",
        style="terse", shape="retrieval_writeback",
        instruction=(
            "Some products have exactly one review waiting in moderation. Approve those single "
            "waiting reviews from the Pending Reviews grid and leave every larger backlog alone."
        ),
        injection=INJ_009,
        delete=set(),
        status_targets={354: 1, 355: 1},
        extra_pending=[354, 355, 356, 357],
        criteria=[
            "Reviews 354 (Josie Yoga Jacket) and 355 (Electra Bra Top) - the only two products "
            "with exactly one queued review - are Approved (status_id 1).",
            "347, 349, 351, 352, 353, 356 and 357 are still Pending, every other review is still "
            "Approved, deletedReviewIds is empty and state.reviews holds 355 rows.",
        ],
        chain="count queued reviews per product -> mass Update Status every single-row queue to "
              "Approved",
        analogues=["Approve reviews with four stars or higher to display in our store."],
        derived_from=None,
        notes=[
            "Queue after injection: Olivia 3, Circe 2, Helios 2, Josie 1, Electra 1. The count==1 "
            "predicate matches exactly two rows and the nearest non-match sits at 2.",
            "Approving by product is the natural moderation errand here; the two target rows are "
            "not adjacent under the grid's default order, so the count has to be done.",
        ],
    ),
    T(
        task_id="matched_review_set_purge_smallest_pending_backlog_010",
        style="terse", shape="retrieval_writeback",
        instruction=(
            "Several products have reviews waiting in moderation. Find the one with the smallest "
            "backlog and delete that product's pending reviews. Everything else in the queue stays."
        ),
        injection=INJ_010,
        delete={358, 359},
        status_targets={}, extra_pending=[354, 355, 356, 357, 358, 359],
        criteria=[
            "state.deletedReviewIds is exactly [358, 359] - the two queued reviews of Josie Yoga "
            "Jacket, the smallest backlog.",
            "347, 349, 351, 352, 353, 354, 355, 356 and 357 are still Pending, every other review "
            "is still Approved, and state.reviews holds 357 rows.",
        ],
        chain="count the pending reviews per product -> mass-delete the smallest product queue",
        analogues=["Delete all pending negative reviews for Circe Hooded Ice Fleece"],
        derived_from=None,
        notes=[
            "Injection deliberately inflates the two seeded queues (Olivia 3->5, Circe 2->4) so "
            "the seed's own smallest backlog is no longer the answer; Josie Yoga Jacket enters at "
            "2. Margin 2 vs 4, unique minimum.",
            "An agent that remembers Circe as the small queue, or that acts without counting, "
            "scores 0.0.",
        ],
    ),
]


# ------------------------------------------------------------------ writers

REWARD_HEAD = '''"""{kind} for {task_id}.

{notes}

The rubric is a single exact-set statement over the review collection: the
matched set has moved and nothing else has. It is false on the untouched
start state and false on any over-broad sweep.
"""
'''

REWARD_BODY = '''
COMPONENT_WEIGHTS = {{
    "{component}": 1.0,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

COMPONENT_DETAILS = {{
    "{component}": "{details}",
}}

EXPECTED_DELETED = {deleted}
EXPECTED_TOTAL = {total}
# review_id -> the status_id that review must carry at the end. Any review not
# listed here must be Approved (1).
EXPECTED_STATUS = {status_map}


def _as_dict(value):
    return value if isinstance(value, dict) else {{}}


def _rows(value):
    return [r for r in value if isinstance(r, dict)] if isinstance(value, list) else []


def _int(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _deleted_ids(state):
    out = set()
    raw = _as_dict(state).get("deletedReviewIds")
    if isinstance(raw, list):
        for value in raw:
            number = _int(value)
            if number is not None:
                out.add(number)
    return out


def _collection_matches(state):
    reviews = _rows(_as_dict(state).get("reviews"))
    if len(reviews) != EXPECTED_TOTAL:
        return False
    seen = set()
    for review in reviews:
        review_id = _int(review.get("review_id"))
        if review_id is None or review_id in seen:
            return False
        seen.add(review_id)
        if _int(review.get("status_id")) != EXPECTED_STATUS.get(review_id, 1):
            return False
    if _deleted_ids(state) != EXPECTED_DELETED:
        return False
    return True


def _components(passed):
    name = "{component}"
    components = [{{
        "name": name,
        "score": COMPONENT_WEIGHTS[name] if passed else 0.0,
        "details": COMPONENT_DETAILS[name],
    }}]
    return round(sum(c["score"] for c in components), 6), components


def score_state(state):
    return _components(_collection_matches(state))
'''

REWARD_TAIL_LOCAL = '''

def evaluate(evidence):
    apps = _as_dict(_as_dict(evidence).get("apps"))
    app = _as_dict(apps.get("shopping_admin")) or _as_dict(apps.get("webarena_shopping_admin_mock"))
    if not app:
        for value in apps.values():
            if isinstance(value, dict) and isinstance(value.get("current_state"), dict):
                app = value
                break
    state = _as_dict(app).get("current_state")
    if not isinstance(state, dict):
        state = {}
    score, components = score_state(state)
    return {"score": score, "components": components}
'''

REWARD_TAIL_NEMO = '''

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
    score, _unused = score_state(state)
    print("REWARD: %s" % score)


main()
'''

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{blurb}

Read-modify-write: GET /go, append the injected reviews to the full state
document, POST the whole document back. Nothing here pre-satisfies any part of
the rubric - every injected row lands Pending (or Approved, where stated) and
deletedReviewIds stays empty, so the untouched lane scores exactly 0.0.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

NEW_REVIEWS = json.loads(r"""{rows}""")


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
    if not isinstance(state, dict):
        fail("GET /go returned neither current_state nor initial_state")

    reviews = state.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != {seed_total}:
        fail("expected the pristine {seed_total}-row reviews seed")
    if state.get("deletedReviewIds") != []:
        fail("expected an empty deletedReviewIds")
    existing = set()
    for review in reviews:
        if isinstance(review, dict):
            existing.add(int(review.get("review_id")))
    for review in NEW_REVIEWS:
        if int(review["review_id"]) in existing:
            fail("review id %s already exists" % review["review_id"])

    state["reviews"] = list(reviews) + NEW_REVIEWS

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=120,
    )
    posted.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    current = result.get("current_state")
    if not isinstance(current, dict) or len(current.get("reviews") or []) != {new_total}:
        fail("state did not take: reviews is not {new_total} rows after set")
    print("SETUP OK")


main()
'''


def build(task):
    tid = task["task_id"]
    inj = task["injection"] or []
    total = SEED_TOTAL + len(inj)
    pending = set(SEED_PENDING) | set(task["extra_pending"])
    status_map = {}
    for rid in sorted(pending):
        status_map[rid] = 2
    for rid, value in task["status_targets"].items():
        status_map[rid] = value
    # injected rows that are seeded Approved stay Approved -> not in the map
    status_map = {k: v for k, v in sorted(status_map.items()) if v != 1}

    component = "matched_review_set_resolved"
    details = task["criteria"][0].replace('"', "'")

    notes_block = "\n".join(task["notes"])
    head_local = REWARD_HEAD.format(
        kind="Deterministic offline reward", task_id=tid, notes=notes_block)
    head_nemo = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Same rubric as reward.py: one exact-set statement over the review\n"
        "collection, read from GET /go?sid=... . Standard library plus requests.\n"
        '"""\n\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n'
        % (tid, URL_PLACEHOLDER)
    )

    status_literal = "{" + ", ".join("%d: %d" % (k, v) for k, v in status_map.items()) + "}"
    deleted_literal = ("set()" if not task["delete"]
                       else "{" + ", ".join(str(i) for i in sorted(task["delete"])) + "}")
    body = REWARD_BODY.format(
        component=component,
        details=details,
        deleted=deleted_literal,
        total=total,
        status_map=status_literal,
    )

    reward = head_local + body + REWARD_TAIL_LOCAL
    nemo_reward = head_nemo + body + REWARD_TAIL_NEMO

    setup = None
    if inj:
        setup = SETUP_TEMPLATE.format(
            task_id=tid,
            blurb=task["notes"][0],
            url=URL_PLACEHOLDER,
            rows=json.dumps(inj, indent=2),
            seed_total=SEED_TOTAL,
            new_total=total,
        )

    injected_pre = []
    if inj:
        injected_pre.append(
            "Appended %d review rows (ids %d-%d) to state.reviews: %s. %s"
            % (
                len(inj),
                min(r["review_id"] for r in inj),
                max(r["review_id"] for r in inj),
                ", ".join(sorted({r["product_name"] for r in inj})),
                task["notes"][0],
            )
        )

    task_json = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
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
        "metadata": {
            "style": task["style"],
            "difficulty": "medium",
            "shape": task["shape"],
            "skills": ["R3", "A4"],
            "skill_chain": task["chain"],
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "injected_preconditions": injected_pre,
            "topic": "matched_review_set_purge",
            "batch": "batch6",
            "lane": 48,
            "inspiration_ids": ["webarena-771", "webarena-772", "webarena-773",
                                "webarena-774", "webarena-775", "webarena-790",
                                "webarena-11", "webarena-77"],
            "authoring_notes": task["notes"],
        },
    }

    instruction_json = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": APP_DIR,
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": task["criteria"],
    }

    nemo_task = {
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
                "initial_setup": setup,
                "eval_reward_code": nemo_reward,
            },
        }
    }

    return {
        "task_json": task_json,
        "instruction_json": instruction_json,
        "reward": reward,
        "nemo_reward": nemo_reward,
        "setup": setup,
        "nemo_task": nemo_task,
        "total": total,
        "status_map": status_map,
    }


# ------------------------------------------------------------------ replays

REPLAY_PRELUDE = '''"""Golden replay draft for {task_id}.

{blurb}

Click path: {path}
"""

from __future__ import annotations


async def _open_pending_grid(page):
    await page.get_by_role("link", name="Marketing", exact=True).click()
    await page.get_by_role("link", name="Pending Reviews", exact=True).click()
    await page.get_by_role("heading", name="Pending Reviews", exact=True).wait_for()


async def _open_all_reviews(page):
    await page.get_by_role("link", name="Marketing", exact=True).click()
    await page.get_by_role("link", name="All Reviews", exact=True).click()
    await page.get_by_role("heading", name="Reviews", exact=True).wait_for()


async def _read_rating(page, review_id):
    """Open one review's edit form by ROW, never by position, and read its star.

    The row is addressed through its own checkbox id (`#id_<review_id>`); the
    Edit link is taken from that same row. Star radios on the form are
    `#Rating_1` .. `#Rating_5`, and the checked one is the review's rating.
    Nothing here depends on where the row sits in the grid: injected reviews
    rank as `351 + id` (reviewDefaultOrder.js:70-73) and therefore always
    render at the TAIL of `Created DESC`, whatever their timestamp says.
    """
    row = page.locator("tr", has=page.locator("#id_%s" % review_id))
    await row.get_by_role("link", name="Edit").click()
    star = page.locator('input[name="ratings[4]"]:checked')
    await star.wait_for()
    await page.go_back()


async def _apply_mass_action(page, review_ids, action, status=None):
    for review_id in review_ids:
        await page.locator("#id_%s" % review_id).check()
    await page.locator("#reviewGrid_massaction-select").select_option(action)
    if status is not None:
        await page.locator("#status").select_option(status)
    await page.locator('[data-ui-id="widget-button-5"]').click()


async def run(lane, task):
    page = lane.page("shopping_admin")
'''


def replay(task, built):
    tid = task["task_id"]
    delete = sorted(task["delete"])
    status_targets = task["status_targets"]
    lines = []
    if tid.endswith("_004"):
        lines.append("    await _open_all_reviews(page)")
        lines.append('    await page.locator(\'[name="detail"]\').fill("disappointed")')
        lines.append("    await page.locator('[data-action=\"grid-filter-apply\"]').click()")
        lines.append("    await page.locator(\"#id_37\").wait_for()")
    elif tid.endswith("_008"):
        lines.append('    await page.get_by_role("link", name="Reports", exact=True).click()')
        lines.append('    await page.get_by_role("link", name="By Products", exact=True).click()')
        lines.append('    await page.get_by_role("heading", name="Product Reviews Report", exact=True).wait_for()')
        lines.append("    # The report grid opens on review_cnt DESC (LegacyReports.jsx:877-878),")
        lines.append("    # so Fusion Backpack (7) is the top row. Click its Show Reviews link by")
        lines.append("    # HREF, not by position: this grid is ordered by the count, but nothing")
        lines.append("    # in the replay should depend on where a row happens to sit.")
        lines.append("    await page.locator('a[href*=\"/admin/review/product/index/productId/6/\"]').first.click()")
        lines.append("    await page.locator(\"#id_3\").wait_for()")
    elif tid.endswith(("_002", "_003", "_007")):
        lines.append("    await _open_pending_grid(page)")
        lines.append("    # Open each queued review's edit form to read its star rating,")
        lines.append("    # then return to the Pending Reviews grid.")
        lines.append("    await _open_pending_grid(page)")
    else:
        lines.append("    await _open_pending_grid(page)")
        lines.append("    # Count the queued rows per product / per nickname off the grid columns.")

    if delete:
        lines.append("    await _apply_mass_action(page, %r, \"delete\")" % delete)
    if status_targets:
        target_status = sorted(set(status_targets.values()))[0]
        ids = sorted(status_targets)
        lines.append(
            "    await _apply_mass_action(page, %r, \"update_status\", status=%r)"
            % (ids, str(target_status))
        )
    lines.append('    await page.get_by_text("record(s) have been").first.wait_for()')

    path = {
        "_004": "Marketing > All Reviews, Review filter, Update Status",
        "_008": "Reports > Reviews > By Products > Show Reviews, Update Status",
    }.get(tid[-4:], "Marketing > Pending Reviews, mass action")
    return REPLAY_PRELUDE.format(task_id=tid, blurb=task["notes"][0], path=path) + "\n".join(lines) + "\n"


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)

    audit_report = []
    for task in TASKS:
        if task["injection"]:
            problems = audit(task["injection"])
            audit_report.append((task["task_id"], problems))
            if problems:
                raise SystemExit("duplicate audit failed for %s: %s" % (task["task_id"], problems))
        else:
            audit_report.append((task["task_id"], []))

    rows = []
    index = []
    for task in TASKS:
        built = build(task)
        tid = task["task_id"]
        d = os.path.join(OUT, tid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "task.json"), "w") as fh:
            json.dump(built["task_json"], fh, indent=2)
            fh.write("\n")
        with open(os.path.join(d, "task_instruction.json"), "w") as fh:
            json.dump(built["instruction_json"], fh, indent=2)
            fh.write("\n")
        with open(os.path.join(d, "reward.py"), "w") as fh:
            fh.write(built["reward"])
        with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
            fh.write(built["nemo_reward"])
        if built["setup"]:
            with open(os.path.join(d, "initial_setup.py"), "w") as fh:
                fh.write(built["setup"])
        with open(os.path.join(d, "nemo_task.json"), "w") as fh:
            json.dump(built["nemo_task"], fh, indent=2)
            fh.write("\n")
        with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as fh:
            fh.write(replay(task, built))
        rows.append(json.dumps(built["nemo_task"]))
        index.append({"task_id": tid, "path": "../../%s/task.json" % tid})
        words = len(task["instruction"].split())
        print("%-58s %-8s words=%2d total=%d deleted=%s status=%s"
              % (tid, task["style"], words, built["total"],
                 sorted(task["delete"]) or "-", built["status_map"]))

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        fh.write("\n".join(rows) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump({"schema_version": 2, "tasks": index}, fh, indent=2)
        fh.write("\n")
    print("seed pending:", SEED_PENDING, "seed total:", SEED_TOTAL)


if __name__ == "__main__":
    main()
