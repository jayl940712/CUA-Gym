#!/usr/bin/env python3
"""Batch-6 lane 52 generator - shopping_admin, chain R4 -> A4.

Writes ten bundles under output/tasks/shopping_admin/<task_id>/ plus the batch
directory output/tasks/shopping_admin/_batches/pending_queue_bulk_approve/.

Every task: take an ordinal slice of the Pending Reviews queue (the slice key is
never named as an entity), then apply ONE bulk action - Update Status ->
Approved / Not Approved, or Delete - to exactly that slice.

Verified mechanism (file:line, hub/websites/webarena_shopping_admin_mock):
  writer  Update Status  src/pages/reviews/Reviews.jsx:147-158  (setState reviews[].status_id/status_code)
  writer  Delete         src/pages/reviews/Reviews.jsx:139-142 -> src/context/AppContext.jsx:303-308 (deletedReviewIds)
  reader  status label   src/pages/reviews/Reviews.jsx:100      (reviewStatusLabel(r.status_id))
  reader  pending filter src/pages/reviews/Reviews.jsx:125      (Number(r.status_id) === 2)
  reader  rows source    src/pages/reviews/Reviews.jsx:124 -> src/utils/selectors.js:252-259 (getReviews drops deletedReviewIds)
  grid    page size 20   src/components/reviews/LegacyReviewGrid.jsx:94
  grid    default sort   src/components/reviews/LegacyReviewGrid.jsx:92, :213-218 (created_at DESC via reviewRank)
  grid    Select All     src/components/reviews/LegacyReviewGrid.jsx:261-262 (all MATCHES, not just the page)
  menu    Pending path   src/components/layout/adminMenu.js:119
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "output", "tasks", "shopping_admin")
BATCH_DIR = os.path.join(SITE_DIR, "_batches", "pending_queue_bulk_approve")
REPLAY_DIR = os.path.join(BATCH_DIR, "replays")

APP_DIR = "webarena_shopping_admin_mock"
BASE_ENV = "CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL__"

SEEDED_PENDING = [347, 349, 351, 352, 353]

# review_id -> star rating on the seeded pending rows (src/data/reviews.json)
SEEDED_STARS = {347: 5, 349: 3, 351: 1, 352: 4, 353: 1}


def inj(rid, created_at, pid, sku, pname, nickname, title, stars, detail):
    return {
        "review_id": rid,
        "created_at": created_at,
        "entity_id": 1,
        "entity_pk_value": pid,
        "status_id": 2,
        "status_code": "Pending",
        "store_id": 1,
        "title": title,
        "detail": detail,
        "nickname": nickname,
        "customer_id": None,
        "sku": sku,
        "product_name": pname,
        "ratings": [{
            "rating_id": 4,
            "rating_code": "Rating",
            "option_id": 15 + stars,
            "value": stars,
            "percent": stars * 20,
        }],
        "rating_summary": float(stars),
    }


TASKS = []


def task(**kw):
    TASKS.append(kw)


task(
    tid="pending_queue_bulk_approve_top_three_rated_001",
    style="terse",
    shape="retrieval_writeback",
    start_path="/",
    instruction=(
        "Only our strongest feedback should go live. Open Marketing > Pending Reviews and "
        "approve the three highest-rated reviews sitting in that queue. Every other pending "
        "review stays pending."
    ),
    criterion="the three highest star ratings in the pending queue",
    mode="status",
    target_status=1,
    targets=[347, 352, 354],
    injected=[
        inj(354, "2023-04-18 15:22:41", 62, "MH01", "Chaz Kangeroo Hoodie", "Marcus Webb",
            "Best hoodie I own", 5,
            "Third winter with this hoodie and it still looks new. The fleece lining has not "
            "pilled at all and the kangaroo pocket is deep enough for a phone and keys."),
        inj(355, "2023-04-17 11:08:55", 78, "MH02", "Teton Pullover Hoodie", "Priya N.",
            "Runs small", 2,
            "Ordered my usual size and could barely pull it over my shoulders. The fabric is "
            "fine but the cut is nowhere near true to size, so budget for an exchange."),
        inj(356, "2023-04-16 09:31:02", 158, "MH07", "Hero Hoodie", "dan_the_man",
            "Colour faded fast", 2,
            "Looked sharp for about three washes and then the black went a washed-out grey. "
            "Stitching is holding up but I would not buy it again at this price."),
    ],
    margin="ranks 1-3 are 5/5/4 stars, rank 4 is 3 stars - a one-star boundary gap; ratings render only on the review edit form (Reviews.jsx:337-339 Summary Rating), so the grid alone cannot answer it.",
    derived_from="review_purge_then_report_circe_four_star_approve_010",
    analogues=["Approve reviews with four stars or higher to display in our store."],
)

task(
    tid="pending_queue_bulk_approve_lowest_three_rated_purge_002",
    style="terse",
    shape="retrieval_writeback",
    start_path="/",
    instruction=(
        "Trim the moderation backlog: delete the three lowest-rated reviews in the Pending "
        "Reviews queue. Nothing else in that queue may change."
    ),
    criterion="the three lowest star ratings in the pending queue",
    mode="delete",
    target_status=None,
    targets=[351, 353, 354],
    injected=[
        inj(354, "2023-04-18 17:44:19", 94, "MH03", "Bruno Compete Hoodie", "Lena Ortiz",
            "Not for me", 2,
            "The hood sits oddly and the sleeves bunch at the wrist whenever I raise my arms. "
            "It is warm enough, but I have stopped reaching for it on the way out."),
        inj(355, "2023-04-17 08:12:37", 190, "MH09", "Abominable Hoodie", "Trevor Hail",
            "Warm and light", 5,
            "Exactly what I wanted for early morning runs - light enough to carry once I warm "
            "up and warm enough to start out in. The thumbholes are a nice touch."),
    ],
    margin="ranks 1-3 are 1/1/2 stars, rank 4 is 3 stars - a one-star boundary gap. The injected 5-star row is a near-miss distractor for a 'delete everything pending' sweep.",
    derived_from="review_purge_then_report_olivia_jacket_count_001",
    analogues=["Delete all pending reviews with less than 4 stars"],
)

task(
    tid="pending_queue_bulk_approve_three_newest_003",
    style="explicit",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "From the admin dashboard, open Marketing > User Content > Pending Reviews. The queue "
        "lists a Created column. Work out which three pending reviews were submitted most "
        "recently, tick those three row checkboxes, choose Update Status in the Actions "
        "control, set Status to Approved and press Submit. Every older pending review must "
        "still read Pending afterwards."
    ),
    criterion="the three most recent Created timestamps in the pending queue",
    mode="status",
    target_status=1,
    targets=[351, 352, 353],
    injected=[
        inj(354, "2023-04-18 13:05:44", 542, "MS06", "Zoltan Gym Tee", "Colin Reeve",
            "Decent gym tee", 3,
            "Does the job for circuit sessions and dries quickly, but the neckline stretched "
            "out within a month. Fine as a spare, not as a favourite."),
        inj(355, "2023-04-17 16:29:10", 526, "MS03", "Balboa Persistence Tee", "Maya Idris",
            "Holds up well", 4,
            "Twenty washes in and the print has not cracked. Slightly boxy through the body "
            "but that is a fit preference rather than a fault."),
    ],
    margin="rank 3 is 2023-04-24 18:49:50 and rank 4 is 18:44:16 - a five-minute gap; the two injected rows are dated 2023-04-17/18, days older, so an agent that mistakes the grid tail for the head lands outside the slice.",
    derived_from="review_purge_then_report_full_queue_sweep_006",
    analogues=["Approve reviews with four stars or higher to display in our store."],
)

task(
    tid="pending_queue_bulk_approve_two_oldest_purge_004",
    style="terse",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "Feedback that has sat in moderation this long is no longer worth publishing. Delete "
        "the two oldest reviews in the Pending Reviews queue and leave the rest of the queue "
        "exactly as it is."
    ),
    criterion="the two earliest Created timestamps in the pending queue",
    mode="delete",
    target_status=None,
    targets=[355, 356],
    injected=[
        inj(354, "2023-04-18 08:05:12", 558, "MS01", "Aero Daily Fitness Tee", "Gus Whitfield",
            "Fits as expected", 3,
            "No complaints and no surprises. True to size, breathes well on the bike, and the "
            "colour is the same shade as the photograph."),
        inj(355, "2023-04-17 11:20:03", 622, "MS08", "Strike Endurance Tee", "Rina Patel",
            "Seams came loose", 2,
            "A shoulder seam started unravelling after the second wash and the hem is already "
            "curling. Comfortable while it lasted, which was not long."),
        inj(356, "2023-04-16 19:45:58", 654, "MT02", "Tristan Endurance Tank", "Ben Okoro",
            "Great for summer", 4,
            "Cut is generous through the chest and it never clings when the temperature "
            "climbs. Would happily buy a second one in another colour."),
    ],
    margin="ranks 1-2 oldest are 2023-04-16 and 2023-04-17; the next oldest is 2023-04-18 - a full day of separation, and the near-miss row is itself injected so the slice cannot be guessed as 'the injected ones'.",
    derived_from=None,
    analogues=["Delete all pending reviews with less than 4 stars"],
)

task(
    tid="pending_queue_bulk_approve_first_two_nicknames_005",
    style="terse",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "Sort the Pending Reviews queue by Nickname. The two reviews whose nicknames come "
        "first alphabetically are spam - set both of them to Not Approved. Everything else in "
        "the queue stays pending."
    ),
    criterion="the two alphabetically first nicknames in the pending queue",
    mode="status",
    target_status=3,
    targets=[354, 355],
    injected=[
        inj(354, "2023-04-18 10:14:26", 670, "MT03", "Primo Endurance Tank", "Aaron Blake",
            "Cheap fabric", 2,
            "Feels thinner than the photographs suggest and it went see-through in the sun. "
            "Cut is fine, material is not what I expected at this price."),
        inj(355, "2023-04-17 12:47:31", 158, "MH07", "Hero Hoodie", "Abby Cortez",
            "Arrived damaged", 3,
            "There was a small tear along the cuff when the parcel arrived. Support sorted it "
            "quickly, so three stars for the product and none of that is its fault."),
        inj(356, "2023-04-16 20:03:49", 62, "MH01", "Chaz Kangeroo Hoodie", "Zed Novak",
            "Excellent buy", 5,
            "Heavier than the usual gym hoodie in a good way. Keeps its shape after washing "
            "and the pocket does not sag once you put something in it."),
    ],
    margin="'Aaron Blake' and 'Abby Cortez' precede every other pending nickname under BOTH a case-insensitive collation (the grid's, LegacyReviewGrid.jsx:230) and a raw ASCII one, so the slice is collation-proof; rank 3 is 'customer'/'Emma' depending on collation and is outside the slice either way.",
    derived_from=None,
    analogues=["Delete all pending negative reviews"],
)

task(
    tid="pending_queue_bulk_approve_first_two_titles_purge_006",
    style="explicit",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "Open Marketing > User Content > Pending Reviews and click the Title column header to "
        "order the queue alphabetically. The two reviews whose titles come first in that "
        "A-to-Z order are duplicate submissions we do not want to keep: tick those two rows, "
        "choose Delete in the Actions control and press Submit. Every other pending review "
        "must remain in the queue."
    ),
    criterion="the two alphabetically first Titles in the pending queue",
    mode="delete",
    target_status=None,
    targets=[353, 354],
    injected=[
        inj(354, "2023-04-18 14:36:07", 254, "MH13", "Marco Lightweight Active Hoodie",
            "Nadia P.", "Excellent value", 4,
            "Half the price of the branded equivalent and it has survived a winter of "
            "commuting. The zip pull is flimsy but everything else is solid."),
        inj(355, "2023-04-17 09:58:44", 270, "MJ01", "Beaumont Summit Kit", "Owen Reyes",
            "Very average", 3,
            "It is fine. Nothing about the fit or the fabric stands out either way, and I "
            "would probably pick something else next time for the same money."),
        inj(356, "2023-04-16 18:22:15", 414, "MJ03", "Montana Wind Jacket", "Kelly Sun",
            "Just fine", 3,
            "Blocks the wind as advertised and packs down small. It is noisy when you move, "
            "which gets old on a long walk, but nothing is actually wrong with it."),
    ],
    margin="'Bad!' then 'Excellent value', with 'Good but not perfect' at rank 3 - the boundary is E vs G. Every pending title but one starts with an uppercase letter and the lowercase one (\"won't recommand\") sorts last under both collations, so the slice is collation-proof.",
    derived_from=None,
    analogues=["Delete all pending negative reviews for Circe Hooded Ice Fleece"],
)

task(
    tid="pending_queue_bulk_approve_first_sku_pair_007",
    style="terse",
    shape="bulk_mutation",
    start_path="/admin/review/product/index/",
    instruction=(
        "Two pending reviews share the SKU that comes first alphabetically across the pending "
        "queue, and both have been vetted. Approve exactly those two. Every other pending "
        "review stays pending."
    ),
    criterion="the two pending rows carrying the alphabetically first SKU",
    mode="status",
    target_status=1,
    targets=[354, 355],
    injected=[
        inj(354, "2023-04-18 12:00:31", 62, "MH01", "Chaz Kangeroo Hoodie", "Sofia Lund",
            "Comfortable and roomy", 4,
            "Roomy through the shoulders without looking oversized, and the fleece is soft "
            "straight out of the bag. Sleeves are a touch long on me."),
        inj(355, "2023-04-17 15:41:09", 62, "MH01", "Chaz Kangeroo Hoodie", "Hugo Barnes",
            "Good but the zip sticks", 3,
            "Warm, well cut and washes well, but the zip catches halfway up every single "
            "time. Worth it on sale, less so at full price."),
        inj(356, "2023-04-16 10:27:53", 1428, "WS03", "Iris Workout Top", "Marta Vinh",
            "Nice top", 4,
            "Light, holds its shape and the straps stay put through a full class. The colour "
            "is a little brighter in person than on screen."),
    ],
    margin="pending SKUs are MH01 x2, WH12 x2, WJ12 x3, WS03 - MH01 precedes WH12 on the first character, so the slice is exactly the two MH01 rows and no third row shares that SKU.",
    derived_from=None,
    analogues=["Approve reviews with four stars or higher to display in our store."],
)

task(
    tid="pending_queue_bulk_approve_second_and_third_newest_008",
    style="terse",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "In Pending Reviews, approve the second- and third-most-recently-submitted reviews. "
        "The single newest pending review and everything older than those two must still read "
        "Pending."
    ),
    criterion="ranks 2 and 3 by Created, newest first, in the pending queue",
    mode="status",
    target_status=1,
    targets=[351, 352],
    injected=[
        inj(354, "2023-04-18 07:19:44", 1108, "WH05", "Selene Yoga Hoodie", "Iris Kwan",
            "Soft but thin", 3,
            "Lovely against the skin and perfect for the studio, but there is no warmth in it "
            "at all once you step outside. Sizing is spot on."),
        inj(355, "2023-04-17 21:03:26", 1268, "WJ04", "Ingrid Running Jacket", "Paul Mensah",
            "Keeps the wind out", 4,
            "Cuts the wind on the river path and packs into its own pocket. The reflective "
            "trim is smaller than the listing photo suggests."),
    ],
    margin="an interior slice: rank 1 (18:55:10) is excluded by two minutes and rank 4 (18:44:16) by five minutes from rank 3 (18:49:50). Approving the newest as well, or approving the top three, both score 0.0.",
    derived_from="review_purge_then_report_full_queue_sweep_006",
    analogues=["Approve reviews with four stars or higher to display in our store."],
)

task(
    tid="pending_queue_bulk_approve_two_lowest_rated_reject_009",
    style="explicit",
    shape="retrieval_writeback",
    start_path="/admin/review/product/index/",
    instruction=(
        "You are looking at the All Reviews grid. Switch to Marketing > User Content > Pending "
        "Reviews, open each queued review with its Edit link and read the Summary Rating on "
        "the form, because the grid does not show it. Find the two lowest-rated pending "
        "reviews, select those two rows, choose Update Status in the Actions control, set "
        "Status to Not Approved and submit. Every other pending review must still read Pending."
    ),
    criterion="the two lowest star ratings in the pending queue",
    mode="status",
    target_status=3,
    targets=[351, 353],
    injected=[
        inj(354, "2023-04-18 16:50:12", 622, "MS08", "Strike Endurance Tee", "Rowan Frost",
            "Does the job", 3,
            "Comfortable enough for a gym session and the fabric wicks well, but it creases "
            "badly in the wash and never quite hangs straight afterwards."),
        inj(355, "2023-04-17 13:11:57", 1044, "WH01", "Mona Pullover Hoodlie", "Tessa Ng",
            "Cosy and warm", 4,
            "Exactly the weight I wanted for autumn walks. The pocket is a little shallow, "
            "otherwise I would have given it the full five."),
    ],
    margin="ranks 1-2 are both 1 star and rank 3 is 3 stars - a two-star boundary gap, and no injected row is below 3, so the slice is the seeded pair and an agent that guesses 'the newest two' or 'the injected two' scores 0.0.",
    derived_from="review_purge_then_report_helios_remoderated_005",
    analogues=["Delete all pending reviews with less than 4 stars"],
)

task(
    tid="pending_queue_bulk_approve_last_two_nicknames_purge_010",
    style="terse",
    shape="bulk_mutation",
    start_path="/",
    instruction=(
        "Sort the Pending Reviews queue by Nickname descending: the top two rows are bot "
        "accounts. Delete exactly those two reviews and leave the rest of the queue alone."
    ),
    criterion="the two alphabetically last nicknames in the pending queue",
    mode="delete",
    target_status=None,
    targets=[354, 355],
    injected=[
        inj(354, "2023-04-18 11:33:08", 190, "MH09", "Abominable Hoodie", "zoe kestrel",
            "buy this now", 5,
            "buy this now best hoodie ever best price ever five stars from me and all my "
            "friends who also bought it and loved it too."),
        inj(355, "2023-04-17 19:26:41", 78, "MH02", "Teton Pullover Hoodie", "yusuf malik",
            "amazing amazing", 5,
            "amazing amazing amazing product amazing seller amazing delivery amazing price "
            "five stars five stars five stars buy it today."),
        inj(356, "2023-04-16 08:44:22", 526, "MS03", "Balboa Persistence Tee", "Amelia Frost",
            "Solid everyday tee", 4,
            "Wears well under a shirt and has not shrunk. The neckline is a little high for "
            "my taste but it is a good basic at the price."),
    ],
    margin="'zoe kestrel' and 'yusuf malik' come last under both the grid's case-insensitive collation and raw ASCII (both are lowercase and after 's'); rank 3 descending is 'seam miller', so the slice is collation-proof and the third injected row sorts first, not last.",
    derived_from=None,
    analogues=["Delete all pending negative reviews"],
)


# --------------------------------------------------------------------------- #
# derived facts and cross-checks


def universe(t):
    return sorted(SEEDED_PENDING + [r["review_id"] for r in t["injected"]])


def stars_map(t):
    m = dict(SEEDED_STARS)
    for r in t["injected"]:
        m[r["review_id"]] = int(r["ratings"][0]["value"])
    return m


def check(t):
    uni = universe(t)
    tgt = t["targets"]
    assert len(set(tgt)) == len(tgt), t["tid"]
    assert set(tgt) <= set(uni), t["tid"]
    assert set(tgt) != set(uni), t["tid"]
    assert t["mode"] in ("status", "delete"), t["tid"]
    if t["mode"] == "status":
        assert t["target_status"] in (1, 3), t["tid"]
    ids = [r["review_id"] for r in t["injected"]]
    assert ids == sorted(ids), t["tid"]
    dates = [r["created_at"] for r in t["injected"]]
    # id ascending must be created_at descending: reviewRank() ranks unknown ids
    # by id (reviewDefaultOrder.js:70), and every injected row is older than the
    # oldest seeded review (2023-04-19 16:15:10), so Created renders monotone.
    assert dates == sorted(dates, reverse=True), t["tid"]
    for d in dates:
        assert d < "2023-04-19 16:15:10", t["tid"]
    if t["style"] == "terse":
        assert len(t["instruction"].split()) <= 40, (t["tid"], len(t["instruction"].split()))


for _t in TASKS:
    check(_t)

assert len(TASKS) == 10
assert sum(1 for t in TASKS if t["style"] == "terse") == 7
assert sum(1 for t in TASKS if t["style"] == "explicit") == 3
assert sum(1 for t in TASKS if t["start_path"] == "/") >= 7
assert sum(1 for t in TASKS if t["shape"] == "retrieval_writeback") >= 3
assert len({t["tid"] for t in TASKS}) == 10


# --------------------------------------------------------------------------- #
# reward source


def scoring_block(t):
    """The shared rubric body: identical text in reward.py and nemo_reward.py."""
    uni = universe(t)
    tgt = sorted(t["targets"])
    rest = sorted(set(uni) - set(tgt))
    lines = []
    lines.append("PENDING_UNIVERSE = %r" % (set(uni),))
    lines.append("TARGET_IDS = %r" % (set(tgt),))
    lines.append("UNTARGETED_IDS = %r" % (set(rest),))
    if t["mode"] == "status":
        lines.append("TARGET_STATUS = %d" % t["target_status"])
    lines.append("")
    lines.append('''

def _reviews(state):
    rows = state.get("reviews")
    return rows if isinstance(rows, list) else []


def _deleted_ids(state):
    out = set()
    raw = state.get("deletedReviewIds")
    if not isinstance(raw, list):
        return out
    for value in raw:
        try:
            out.add(int(value))
        except (TypeError, ValueError):
            continue
    return out


def _status_map(state):
    """review_id -> status_id over the whole persisted `reviews` array."""
    out = {}
    for row in _reviews(state):
        if not isinstance(row, dict):
            continue
        try:
            rid = int(row.get("review_id"))
        except (TypeError, ValueError):
            continue
        try:
            out[rid] = int(row.get("status_id"))
        except (TypeError, ValueError):
            out[rid] = -1
    return out
'''.strip("\n"))
    lines.append("")
    lines.append("")
    if t["mode"] == "status":
        lines.append('''
def _scope_ok(state):
    """Gate ANDed into every paid component (CORRECTIONS #84/#110).

    Nothing outside the pending queue may move: no review may be deleted, and
    every review that was not in the queue must still be Approved. An over-broad
    sweep therefore scores 0.0 rather than a docked partial.
    """
    if _deleted_ids(state):
        return False
    statuses = _status_map(state)
    for rid in PENDING_UNIVERSE:
        if rid not in statuses:
            return False
    for rid, status in statuses.items():
        if rid in PENDING_UNIVERSE:
            continue
        if status != 1:
            return False
    return True


def _checks(state):
    scope = _scope_ok(state)
    statuses = _status_map(state)
    moved = set(rid for rid in PENDING_UNIVERSE if statuses.get(rid) == TARGET_STATUS)
    still_pending = set(rid for rid in PENDING_UNIVERSE if statuses.get(rid) == 2)
    no_stray_status = all(
        statuses.get(rid) in (2, TARGET_STATUS) for rid in PENDING_UNIVERSE
    )
    return {
        "targeted_rows_hold_the_required_status": scope and moved == TARGET_IDS,
        "queue_now_holds_exactly_the_untargeted_rows": (
            scope and no_stray_status and still_pending == UNTARGETED_IDS
        ),
    }
'''.strip("\n"))
    else:
        lines.append('''
def _scope_ok(state):
    """Gate ANDed into every paid component (CORRECTIONS #84/#110).

    Only pending-queue rows may be deleted, and no review's status may be
    edited: this task is a delete, so any status flip - inside the queue or
    outside it - is out of scope and costs everything.
    """
    for rid in _deleted_ids(state):
        if rid not in PENDING_UNIVERSE:
            return False
    statuses = _status_map(state)
    for rid in PENDING_UNIVERSE:
        if statuses.get(rid) != 2:
            return False
    for rid, status in statuses.items():
        if rid in PENDING_UNIVERSE:
            continue
        if status != 1:
            return False
    return True


def _checks(state):
    scope = _scope_ok(state)
    deleted = _deleted_ids(state)
    survivors = set(rid for rid in PENDING_UNIVERSE if rid not in deleted)
    return {
        "deleted_rows_are_exactly_the_derived_slice": scope and deleted == TARGET_IDS,
        "queue_now_holds_exactly_the_untargeted_rows": scope and survivors == UNTARGETED_IDS,
    }
'''.strip("\n"))
    lines.append("")
    lines.append("")
    if t["mode"] == "status":
        first = "targeted_rows_hold_the_required_status"
    else:
        first = "deleted_rows_are_exactly_the_derived_slice"
    lines.append("COMPONENT_WEIGHTS = {")
    lines.append("    %r: 0.6," % first)
    lines.append("    'queue_now_holds_exactly_the_untargeted_rows': 0.4,")
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    return "\n".join(lines)


def reward_py(t):
    action = {
        1: "Update Status -> Approved",
        3: "Update Status -> Not Approved",
    }.get(t.get("target_status") or 0, "Delete")
    header = '''"""Deterministic reward for {tid}.

Chain: R4 (ordinal slice of the Pending Reviews queue) -> A4 ({action} applied
to exactly that slice).

Slice rule: {criterion}.
Resulting collection asserted exactly - target ids {tgt}, the rest of the queue
{rest} untouched at Pending.

Reads only `current_state` from the immutable evidence bundle; never diffs
against `initial_state`. Ground truth is fixed by the frozen seed of
webarena_shopping_admin_mock in ./hub/ plus this bundle's initial_setup.py.
"""
'''.format(
        tid=t["tid"],
        action=action,
        criterion=t["criterion"],
        tgt=sorted(t["targets"]),
        rest=sorted(set(universe(t)) - set(t["targets"])),
    )
    body = '''

def _state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


'''
    tail = '''

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
    return header + body + scoring_block(t) + "\n" + tail


def nemo_reward_py(t):
    header = '''"""NeMo-Gym reward program for {tid}.

Same rubric, same component names and weights as reward.py; the scoring block
below is copied verbatim from it. Reads state from GET /go?sid=... and prints
``REWARD: <float>`` on every output path, including error paths.

**Only ``current_state`` is read.** Nothing is diffed against ``initial_state``.

Self-contained: standard library plus requests.
"""

import sys

import requests

sid = "__CUA_GYM_SID__"
BASE_URL = "{url}"

'''.format(tid=t["tid"], url=URL_PLACEHOLDER)
    tail = '''

def score_state(current_state):
    checks = _checks(current_state)
    components = [
        {
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0,
            "details": {"satisfied": bool(checks.get(name))},
        }
        for name in COMPONENT_WEIGHTS
    ]
    return round(sum(c["score"] for c in components), 6), components


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + sid, timeout=60)
        response.raise_for_status()
        payload = response.json()
        current_state = payload.get("current_state")
        if not isinstance(current_state, dict):
            current_state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    try:
        score, _components = score_state(current_state)
    except Exception as exc:  # noqa: BLE001 - scoring must never crash silently
        print("reward scoring failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    print("REWARD: %s" % float(score))


main()
'''
    return header + scoring_block(t) + "\n" + tail


# --------------------------------------------------------------------------- #
# setup source


def setup_py(t):
    rows = json.dumps(t["injected"], indent=2)
    ids = [r["review_id"] for r in t["injected"]]
    return '''"""NeMo-Gym setup program for {tid}.

Injects {n} additional Pending reviews into `state.reviews` so the ordinal slice
this task names is decided by data the agent has to read, not by the five seeded
pending rows an agent could memorise. Every injected row carries the full field
set the seed uses (entity_id/entity_pk_value/status_id/status_code/store_id/
title/detail/nickname/customer_id/sku/product_name/ratings/rating_summary), for
a real product id and SKU, and its `ratings` option_id follows the seed's own
rating_id 4 mapping (option 16..20 for 1..5 stars, src/data/ratings.json).

Ordering safety: `reviewRank()` (src/components/reviews/reviewDefaultOrder.js:70)
ranks ids it has never measured AFTER every seeded row, so injected rows always
render at the tail of the Created-descending grid. Each injected `created_at` is
therefore older than the oldest seeded review (2023-04-19 16:15:10), and ids
ascend as dates descend, which keeps the rendered Created column monotone - no
contradiction is visible on one screen.

Nothing is approved, rejected or deleted here, so the untouched lane scores
exactly 0.0.

Read-modify-write: GET /go, mutate the whole document, POST it back.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

SEEDED_PENDING = {{347, 349, 351, 352, 353}}
INJECTED_IDS = {ids}

INJECTED = json.loads(r"""{rows}""")


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
    if not isinstance(reviews, list) or len(reviews) != 351:
        fail("expected the pristine 351-row reviews seed")
    pending = set(
        int(r.get("review_id")) for r in reviews if int(r.get("status_id", 0)) == 2
    )
    if pending != SEEDED_PENDING:
        fail("expected the pristine pending set {{347, 349, 351, 352, 353}}")
    existing = set(int(r.get("review_id")) for r in reviews)
    for rid in INJECTED_IDS:
        if rid in existing:
            fail("injected review id %s already exists" % rid)
    if state.get("deletedReviewIds") != []:
        fail("expected an empty deletedReviewIds key")

    state["reviews"] = list(reviews) + INJECTED

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=120,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    after = result.get("current_state")
    if not isinstance(after, dict):
        fail("GET /go returned no current_state after the write")
    rows = after.get("reviews")
    if not isinstance(rows, list) or len(rows) != 351 + len(INJECTED_IDS):
        fail("reviews did not grow by the injected rows")
    now_pending = set(
        int(r.get("review_id")) for r in rows if int(r.get("status_id", 0)) == 2
    )
    if now_pending != SEEDED_PENDING | set(INJECTED_IDS):
        fail("the pending queue is not the seeded rows plus the injected rows")
    if after.get("deletedReviewIds") != []:
        fail("deletedReviewIds is not empty after the write")
    print("SETUP OK")


main()
'''.format(tid=t["tid"], n=len(t["injected"]), url=URL_PLACEHOLDER, ids=ids, rows=rows)


# --------------------------------------------------------------------------- #
# bundle files


def success_criteria(t):
    uni = sorted(universe(t))
    tgt = sorted(t["targets"])
    rest = sorted(set(uni) - set(tgt))
    if t["mode"] == "status":
        label = "Approved (status_id 1)" if t["target_status"] == 1 else "Not Approved (status_id 3)"
        return [
            "The pending queue after setup is reviews %s." % (uni,),
            "reviews rows %s - and only those - now hold %s." % (tgt, label),
            "reviews rows %s are still Pending (status_id 2)." % (rest,),
            "deletedReviewIds is still empty and every review outside the queue is still Approved.",
        ]
    return [
        "The pending queue after setup is reviews %s." % (uni,),
        "deletedReviewIds is exactly %s." % (tgt,),
        "reviews rows %s are still present and still Pending (status_id 2)." % (rest,),
        "No review's status_id was edited, inside the queue or outside it.",
    ]


def task_instruction_json(t):
    return {
        "task_id": t["tid"],
        "task_instruction": t["instruction"],
        "app_dir": APP_DIR,
        "start_path": t["start_path"],
        "difficulty": "medium",
        "success_criteria": success_criteria(t),
    }


def task_json(t):
    action_note = {
        1: "bulk Update Status -> Approved",
        3: "bulk Update Status -> Not Approved",
    }.get(t.get("target_status") or 0, "bulk Delete")
    return {
        "schema_version": 2,
        "task_id": t["tid"],
        "instruction": t["instruction"],
        "apps": [
            {
                "name": APP_DIR,
                "source_name": "shopping_admin",
                "base_url_env": BASE_ENV,
                "start_path": t["start_path"],
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
            "style": t["style"],
            "difficulty": "medium",
            "shape": t["shape"],
            "skills": ["R4", "A4"],
            "skill_chain": "take the ordinal slice of the Pending Reviews queue the instruction describes (%s) -> %s over exactly that slice" % (t["criterion"], action_note),
            "derived_from": t["derived_from"],
            "official_analogues": t["analogues"],
            "topic": "pending_queue_bulk_approve",
            "lane": 52,
            "inspiration_ids": ["webarena-771", "webarena-772", "webarena-773", "webarena-774"],
            "authoring_notes": [
                "Writer: src/pages/reviews/Reviews.jsx:147-158 (Update Status -> reviews[].status_id/status_code) and :139-142 -> src/context/AppContext.jsx:303-308 (Delete -> deletedReviewIds).",
                "Reader: the same key. src/pages/reviews/Reviews.jsx:100 prints reviewStatusLabel(r.status_id) and :125 filters Number(r.status_id) === 2 over getReviews(state) (src/utils/selectors.js:252-259, which drops deletedReviewIds).",
                "Pending Reviews grid: default sort created_at DESC (LegacyReviewGrid.jsx:92, :213-218), page size 20 (:94). The queue is %d rows, so the whole matched set is on one page and 'Select Visible' and 'Select All' coincide here; Select All (:261-262) selects all MATCHES either way." % len(universe(t)),
                "Tie margin: %s" % t["margin"],
                "Star ratings are not a Reviews grid column and there is no rating filter (LegacyReviewGrid.jsx:415-434); the value lives on the edit form's Summary Rating (Reviews.jsx:337-339), which is what forces the retrieval on the rating tasks.",
            ],
            "injected_preconditions": [
                "state.reviews gains %d additional Pending rows (ids %s) on real seeded products, each with the full seeded field set and a rating_id 4 option_id from src/data/ratings.json." % (
                    len(t["injected"]), [r["review_id"] for r in t["injected"]]),
                "Every injected created_at is older than the oldest seeded review (2023-04-19 16:15:10) and ids ascend as dates descend, because reviewRank() (reviewDefaultOrder.js:70) puts unmeasured ids after every seeded row - so the rendered Created column stays monotone.",
                "Nothing is approved, rejected or deleted by the setup: the untouched lane scores 0.0.",
            ],
        },
    }


def nemo_task_json(t, setup_src, reward_src):
    return {
        "task_payload": {
            "task_id": t["tid"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": t["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": t["tid"],
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": reward_src,
            },
        }
    }


def replay_draft(t):
    uni = sorted(universe(t))
    tgt = sorted(t["targets"])
    if t["mode"] == "status":
        act = "update_status"
        status_value = str(t["target_status"])
        label = "Approved" if t["target_status"] == 1 else "Not Approved"
        action_steps = [
            'Tick the row checkbox "#id_<review_id>" for each of %s.' % tgt,
            'Select "update_status" in "#reviewGrid_massaction-select".',
            'Select "%s" (value "%s") in "#status".' % (label, status_value),
            'Press the Submit button (data-ui-id="widget-button-5").',
        ]
    else:
        act = "delete"
        action_steps = [
            'Tick the row checkbox "#id_<review_id>" for each of %s.' % tgt,
            'Select "delete" in "#reviewGrid_massaction-select".',
            'Press the Submit button (data-ui-id="widget-button-5").',
        ]
    steps = [
        'Land on start_path "%s".' % t["start_path"],
        "Click Marketing in the left rail, then Pending Reviews under User Content (adminMenu.js:119).",
        "The queue holds %d rows after setup: %s. Page size is 20 (LegacyReviewGrid.jsx:94), so the whole queue is on page 1." % (len(uni), uni),
        "Derive the slice: %s." % t["criterion"],
    ]
    if "rated" in t["criterion"] or "star" in t["criterion"]:
        steps.append(
            "Ratings are NOT a grid column. Open each queued review through its Edit link and "
            "read the Summary Rating field (Reviews.jsx:337-339), then click Back "
            '("#back") - do not press Save Review, which would rewrite the row.'
        )
    steps.extend(action_steps)
    steps.append(
        "Confirm the grid: the remaining Pending Reviews queue is exactly %s."
        % sorted(set(uni) - set(tgt))
    )
    body = '''"""Golden replay draft for {tid}.

DRAFT ONLY - written during authoring, not executed. The verification phase owns
the real replay. Navigation is click-only from start_path "{sp}"; no page.goto()
after the initial landing.

Route notes taken from source (hub/websites/webarena_shopping_admin_mock/src):
  * "/" redirects to /admin/admin/dashboard/ (App.jsx:624).
  * Left rail: components/layout/adminMenu.js - Marketing > User Content >
    Pending Reviews (:119), All Reviews (:118).
  * Row checkbox id is "id_<review_id>" (LegacyReviewGrid.jsx:507).
  * Mass action controls: "#reviewGrid_massaction-select" (:318), the hidden
    Status select "#status" (:338, rendered on cold load), Submit
    data-ui-id="widget-button-5" (:346).
  * Row-selection helper "#reviewGrid_massaction-mass-select" (:360) - note that
    "selectAll" takes every MATCHED row (:261-262) while "selectVisible" takes
    the current page only (:264). Both coincide here: the queue fits one page.
  * Review edit form: "#back", "#save_button", "#delete"; Summary Rating is a
    read-only field (Reviews.jsx:337-339). The mass action is the intended path;
    the per-review Save is not.

Expected end state: {mode} applied to exactly {tgt}.
"""

MASS_ACTION = {act!r}

STEPS = {steps!r}
'''.format(
        tid=t["tid"],
        sp=t["start_path"],
        mode=("Update Status" if t["mode"] == "status" else "Delete"),
        tgt=tgt,
        act=act,
        steps=steps,
    )
    return body


# --------------------------------------------------------------------------- #


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def main():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    nemo_rows = []
    index = {"schema_version": 2, "tasks": []}
    for t in TASKS:
        bundle = os.path.join(SITE_DIR, t["tid"])
        setup_src = setup_py(t)
        reward_src = nemo_reward_py(t)
        write(os.path.join(bundle, "task_instruction.json"),
              json.dumps(task_instruction_json(t), indent=2) + "\n")
        write(os.path.join(bundle, "task.json"),
              json.dumps(task_json(t), indent=2) + "\n")
        write(os.path.join(bundle, "reward.py"), reward_py(t))
        write(os.path.join(bundle, "nemo_reward.py"), reward_src)
        write(os.path.join(bundle, "initial_setup.py"), setup_src)
        row = nemo_task_json(t, setup_src, reward_src)
        write(os.path.join(bundle, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
        nemo_rows.append(json.dumps(row))
        write(os.path.join(REPLAY_DIR, t["tid"] + ".py"), replay_draft(t))
        index["tasks"].append({"task_id": t["tid"], "path": "../../%s/task.json" % t["tid"]})

    write(os.path.join(BATCH_DIR, "nemo_tasks.jsonl"), "\n".join(nemo_rows) + "\n")
    write(os.path.join(BATCH_DIR, "index.json"), json.dumps(index, indent=2) + "\n")

    # a compact table for GENERATION.md
    for t in TASKS:
        print(t["tid"], t["style"], t["shape"], t["mode"], t["targets"],
              universe(t), stars_map(t))


if __name__ == "__main__":
    main()
