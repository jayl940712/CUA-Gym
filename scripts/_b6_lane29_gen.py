#!/usr/bin/env python3
"""Batch 6 - lane 29 - reddit - `two_hop_negative_comment_note`.

Generates 10 all-medium (R7 -> A7) bundles under
`output/tasks/reddit/<task_id>/`, plus the lane batch directory
`output/tasks/reddit/_batches/two_hop_negative_comment_note/`.

Skill chain, identical shape on all ten:
  R7  join a forum's Comments tab row to the commenter's profile, then count
      that user's own comments whose score is below zero on their Comments tab
  A7  carry the derived count into a persisted vessel - a private message body
      or a block reason

Every derived value in this file was computed directly from
hub/websites/webarena_reddit_mock/src/data/{comments,submissions}.json.
Run from the repo root:  python3 scripts/_b6_lane29_gen.py
"""

import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK = os.path.join(ROOT, "hub", "websites", "webarena_reddit_mock")
OUT = os.path.join(ROOT, "output", "tasks", "reddit")
SLUG = "two_hop_negative_comment_note"
BATCH = os.path.join(OUT, "_batches", SLUG)

CURRENT_USER = "MarvelsGrantMan136"

W27 = ("Tell me the count of comments that have received more downvotes than "
       "upvotes for the user who made the latest post on the Showerthoughts forum.")
W28 = ("Tell me the count of comments that have received more downvotes than "
       "upvotes for the user who made the latest post on the Worcester forum.")
W29 = ("Tell me the count of comments that have received more downvotes than "
       "upvotes for the user who made the latest post on the DIY forum.")
W30 = ("Tell me the count of comments that have received more downvotes than "
       "upvotes for the user who made the latest post on the space forum.")
W31 = ("Tell me the count of comments that have received more downvotes than "
       "upvotes for the user who made the latest post on the photoshopbattles forum.")
W491 = ('Notify Alexander Thomas in their most recent pending order with message '
        '"the order is ready to be shipped soon!"')
W528 = ('Fill out the contact us form with this refund message for the phone screen '
        'protector bought March 2023: "I need a refund. Order: <order_id>. Amount: '
        '<amount>. Reason: It broke after three days of use." Leave the filled form '
        'ready for review and do not submit it. Fill in the order id and amount '
        'information from my order history.')

INSPIRATION_IDS = ["webarena-27", "webarena-28", "webarena-29",
                   "webarena-30", "webarena-31"]

# --------------------------------------------------------------------------- #
# Injection payloads (tasks 007-010).                                          #
#                                                                              #
# Each record carries exactly the seven keys the frozen corpus rows carry and   #
# `addComment` (AppContext.jsx:450-478) writes: id, submission, author, body,   #
# netScore, timestamp, userFlag. Timestamps are 2023-04-02, after the corpus    #
# maximum (2023-03-31T23:59) and before the seeded fixture post (2023-06-12),   #
# so the anchor row tops its forum's fixed newest-first Comments tab and every  #
# injected row lands on page 1 of the author's Comments tab (timestamp DESC).   #
# --------------------------------------------------------------------------- #

INJECTIONS = {
    "007": [
        # Autarch_Kade, f/books. Seeded: 4 comments, scores -1/2/61/103.
        {"id": 3000101, "submission": 124108, "author": "Autarch_Kade",
         "body": "Not going to sugarcoat it: this one is a slog and the hype is unearned.",
         "netScore": -6, "timestamp": "2023-04-02T10:20:00+00:00", "userFlag": "t1_jq7a101"},
        {"id": 3000102, "submission": 103137, "author": "Autarch_Kade",
         "body": "Every recommendation thread turns into the same five books. Read something else.",
         "netScore": -3, "timestamp": "2023-04-02T09:45:00+00:00", "userFlag": "t1_jq7a102"},
        {"id": 3000103, "submission": 59421, "author": "Autarch_Kade",
         "body": "Their shipping estimates have been fine for me, for whatever that is worth.",
         "netScore": 0, "timestamp": "2023-04-02T09:10:00+00:00", "userFlag": "t1_jq7a103"},
    ],
    "008": [
        # HomicidalHushPuppy, f/pittsburgh. Seeded: 4 comments, scores -3/2/3/5.
        {"id": 3000201, "submission": 131907, "author": "HomicidalHushPuppy",
         "body": "Calling this art is generous. It is a wall with paint on it.",
         "netScore": -9, "timestamp": "2023-04-02T11:05:00+00:00", "userFlag": "t1_jq7b201"},
        {"id": 3000202, "submission": 132032, "author": "HomicidalHushPuppy",
         "body": "Nobody is listening through your lightbulbs. Please log off for a day.",
         "netScore": -2, "timestamp": "2023-04-02T10:30:00+00:00", "userFlag": "t1_jq7b202"},
        {"id": 3000203, "submission": 121942, "author": "HomicidalHushPuppy",
         "body": "If you cannot read the title yourself you probably should not be buying it.",
         "netScore": -5, "timestamp": "2023-04-02T09:55:00+00:00", "userFlag": "t1_jq7b203"},
        {"id": 3000204, "submission": 121936, "author": "HomicidalHushPuppy",
         "body": "The Penn Hills office was quick for me last spring, appointment or not.",
         "netScore": 0, "timestamp": "2023-04-02T09:20:00+00:00", "userFlag": "t1_jq7b204"},
    ],
    "009": [
        # nattarbox, f/CambridgeMA. Seeded: 4 comments, scores -2/18/46/55.
        {"id": 3000301, "submission": 118523, "author": "nattarbox",
         "body": "Or the city could stop inventing a new sticker design every single year.",
         "netScore": -7, "timestamp": "2023-04-02T12:00:00+00:00", "userFlag": "t1_jq7c301"},
        {"id": 3000302, "submission": 118507, "author": "nattarbox",
         "body": "It was quiet the last two Saturdays I went, so your mileage may vary.",
         "netScore": 0, "timestamp": "2023-04-02T11:25:00+00:00", "userFlag": "t1_jq7c302"},
    ],
    "010": [
        # DeliMcPickles, f/washingtondc. Seeded: 5 comments, scores -1/1/2/10/14.
        {"id": 3000401, "submission": 136674, "author": "DeliMcPickles",
         "body": "Four days and half the list is museums that close before you get there.",
         "netScore": -4, "timestamp": "2023-04-02T13:00:00+00:00", "userFlag": "t1_jq7d401"},
        {"id": 3000402, "submission": 136769, "author": "DeliMcPickles",
         "body": "The Metro is only cheaper because you are not counting the hours it costs you.",
         "netScore": -11, "timestamp": "2023-04-02T12:30:00+00:00", "userFlag": "t1_jq7d402"},
        {"id": 3000403, "submission": 136712, "author": "DeliMcPickles",
         "body": "Mine landed the same week, so the backlog may finally be clearing.",
         "netScore": 0, "timestamp": "2023-04-02T12:00:00+00:00", "userFlag": "t1_jq7d403"},
    ],
}


def seeded_submissions():
    with open(os.path.join(MOCK, "src", "data", "submissions.json")) as fh:
        return {int(s["id"]): s for s in json.load(fh)}


def submission_edits_for(records, subs):
    """Mirror what `addComment` writes alongside the comment.

    AppContext.jsx:473-476 patches the parent submission's `commentCount` and
    `lastActive`. `submissionEdits[<id>]` REPLACES the frozen row on read
    (overlay.js resolveSubmission), so the edit carries the whole seeded record
    with only those two fields moved.
    """
    edits = {}
    for rec in sorted(records, key=lambda r: r["timestamp"]):
        sid = int(rec["submission"])
        base = dict(edits.get(str(sid)) or subs[sid])
        base["commentCount"] = int(base.get("commentCount") or 0) + 1
        base["lastActive"] = rec["timestamp"]
        edits[str(sid)] = base
    return edits


# --------------------------------------------------------------------------- #
# The ten tasks.                                                               #
# --------------------------------------------------------------------------- #

TASKS = [
    dict(n="001", slug="television_newest_comment_message", style="terse",
         vessel="message", forum="television", rank=1, rank_word="most recent",
         author="anasui1", count=1, total=3, zeros=0, pages=1,
         anchor_comment=2554985, anchor_ts="2023-03-31T22:18:45+00:00",
         neighbour="Lanky_Chemist_3773", neighbour_count=0,
         prefix="below-zero comments",
         instruction=(
             "Open f/television's Comments tab and take the author of the most "
             "recent comment. Count how many of that user's own comments score "
             "below zero, then send them a message reading exactly "
             "\"below-zero comments: N\"."),
         analogues=[W27, W528]),

    dict(n="002", slug="nyc_newest_comment_block", style="terse",
         vessel="block", forum="nyc", rank=1, rank_word="most recent",
         author="drpvn", count=1, total=10, zeros=0, pages=1,
         anchor_comment=2555233, anchor_ts="2023-03-31T22:23:08+00:00",
         neighbour="Henry2k", neighbour_count=0,
         prefix="downvoted comments",
         instruction=(
             "Whoever wrote the most recent comment in f/nyc has worn out my "
             "patience. Block them, reason exactly \"downvoted comments: N\", "
             "with N the number of their own comments scoring below zero."),
         analogues=[W30, W491]),

    dict(n="003", slug="worcesterma_newest_comment_paged", style="explicit",
         vessel="message", forum="WorcesterMA", rank=1, rank_word="most recent",
         author="mineinhusdson", count=1, total=42, zeros=2, pages=2,
         anchor_comment=2555253, anchor_ts="2023-03-31T22:23:27+00:00",
         neighbour="Plastic-Ad-4791", neighbour_count=0,
         prefix="comments below zero",
         instruction=(
             "Go to f/WorcesterMA and switch from Submissions to the Comments "
             "tab. That feed is fixed newest-first; take the byline of the very "
             "first row and open that user's profile. On their profile, open "
             "their Comments tab and page through every entry - there is more "
             "than one page - counting only the comments whose score is below "
             "zero. A comment sitting at exactly zero does not count. Then use "
             "the Send message item in the profile Toolbox and send that user a "
             "message whose whole body is \"comments below zero: N\", with N "
             "replaced by the number you counted."),
         analogues=[W28, W528]),

    dict(n="004", slug="jerseycity_third_comment_block", style="terse",
         vessel="block", forum="jerseycity", rank=3, rank_word="third most recent",
         author="EyesOnImprovement", count=2, total=2, zeros=0, pages=1,
         anchor_comment=2531064, anchor_ts="2023-03-31T14:25:21+00:00",
         neighbour="DirectorBeneficial48", neighbour_count=0,
         prefix="negative comment count",
         instruction=(
             "In f/jerseycity's Comments tab, the third most recent comment is "
             "by someone I want gone. Block that author with the reason exactly "
             "\"negative comment count: N\", N being how many of their comments "
             "score below zero."),
         analogues=[W29, W491]),

    dict(n="005", slug="maine_second_comment_message", style="terse",
         vessel="message", forum="Maine", rank=2, rank_word="second most recent",
         author="Guygan", count=1, total=5, zeros=1, pages=1,
         anchor_comment=2445900, anchor_ts="2023-03-29T12:49:48+00:00",
         neighbour="bigtencopy", neighbour_count=0,
         prefix="below-zero comments",
         instruction=(
             "Take the author of the second most recent comment in f/Maine. "
             "Count that user's own comments with a score below zero - a zero "
             "does not count - and message them exactly "
             "\"below-zero comments: N\"."),
         analogues=[W31, W528]),

    dict(n="006", slug="connecticut_second_comment_block", style="terse",
         vessel="block", forum="Connecticut", rank=2, rank_word="second most recent",
         author="satans_toast", count=1, total=3, zeros=0, pages=1,
         anchor_comment=2535946, anchor_ts="2023-03-31T15:58:58+00:00",
         neighbour="FoolsGold45", neighbour_count=0,
         prefix="downvoted comments",
         instruction=(
             "The second most recent comment in f/Connecticut is from a user I "
             "am blocking. Do it, and set the block reason to exactly "
             "\"downvoted comments: N\", where N counts their comments scoring "
             "below zero."),
         analogues=[W27, W491]),

    dict(n="007", slug="books_injected_spree_message", style="terse",
         vessel="message", forum="books", rank=1, rank_word="most recent",
         author="Autarch_Kade", count=3, total=7, zeros=1, pages=1,
         anchor_comment=3000101, anchor_ts="2023-04-02T10:20:00+00:00",
         neighbour="Autarch_Kade", neighbour_count=3,
         prefix="comments below zero",
         instruction=(
             "Someone has been on a downvoted streak in f/books. Take the author "
             "of that forum's most recent comment, count their comments scoring "
             "below zero, and message them exactly "
             "\"comments below zero: N\"."),
         analogues=[W29, W528]),

    dict(n="008", slug="pittsburgh_injected_spree_block", style="explicit",
         vessel="block", forum="pittsburgh", rank=1, rank_word="most recent",
         author="HomicidalHushPuppy", count=4, total=8, zeros=1, pages=1,
         anchor_comment=3000201, anchor_ts="2023-04-02T11:05:00+00:00",
         neighbour="HomicidalHushPuppy", neighbour_count=4,
         prefix="negative comment count",
         instruction=(
             "Open f/pittsburgh and click through to its Comments tab, which is "
             "ordered newest first. Follow the byline on the top row to that "
             "commenter's profile, open their Comments tab, and count how many "
             "of their comments have a score below zero; a comment sitting at "
             "exactly zero is not below zero and must not be counted. Then pick "
             "Block user from the profile Toolbox and submit the block with the "
             "Comment field set to exactly \"negative comment count: N\", where "
             "N is the number you counted."),
         analogues=[W30, W491]),

    dict(n="009", slug="cambridgema_injected_spree_message", style="terse",
         vessel="message", forum="CambridgeMA", rank=1, rank_word="most recent",
         author="nattarbox", count=2, total=6, zeros=1, pages=1,
         anchor_comment=3000301, anchor_ts="2023-04-02T12:00:00+00:00",
         neighbour="nattarbox", neighbour_count=2,
         prefix="below-zero comments",
         instruction=(
             "Whoever left the most recent comment in f/CambridgeMA is "
             "collecting downvotes. Message that user exactly "
             "\"below-zero comments: N\", where N is how many of their comments "
             "have a score below zero."),
         analogues=[W28, W528]),

    dict(n="010", slug="washingtondc_injected_spree_message", style="explicit",
         vessel="message", forum="washingtondc", rank=1, rank_word="most recent",
         author="DeliMcPickles", count=3, total=8, zeros=1, pages=1,
         anchor_comment=3000401, anchor_ts="2023-04-02T13:00:00+00:00",
         neighbour="DeliMcPickles", neighbour_count=3,
         prefix="comments below zero",
         instruction=(
             "Visit f/washingtondc and open the Comments tab next to "
             "Submissions. The feed is newest-first, so the top row is the "
             "forum's latest comment; click that commenter's name to reach "
             "their profile. On the profile, open the Comments tab and count "
             "the entries whose score is below zero - entries at exactly zero "
             "or above do not count. Finally choose Send message in the "
             "Toolbox and send that user a message whose entire body is "
             "\"comments below zero: N\", with N the count you arrived at."),
         analogues=[W31, W528]),
]


def expected_body(task):
    return "%s: %d" % (task["prefix"], task["count"])


# --------------------------------------------------------------------------- #
# reward source                                                                #
# --------------------------------------------------------------------------- #

SHARED_HELPERS = '''
def _norm(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip().lower()
'''

MESSAGE_LOGIC = '''
def score_checks(state):
    raw = state.get("messages")
    threads = [row for row in raw if isinstance(row, dict)] if isinstance(raw, list) else []
    thread = threads[0] if len(threads) == 1 else None

    participants = set()
    messages = []
    if thread is not None:
        people = thread.get("participants")
        if isinstance(people, list):
            participants = set(_norm(p) for p in people if isinstance(p, str))
        rows = thread.get("messages")
        if isinstance(rows, list):
            messages = [m for m in rows if isinstance(m, dict)]

    addressed = (
        thread is not None
        and participants == set([_norm(CURRENT_USER), _norm(TARGET_USER)])
        and len(messages) == 1
        and _norm(messages[0].get("sender")) == _norm(CURRENT_USER)
    )
    body_ok = addressed and _norm(messages[0].get("body")) == _norm(EXPECTED_TEXT)

    return {
        "message_thread_to_derived_author": bool(addressed),
        "body_carries_derived_count": bool(body_ok),
    }
'''

BLOCK_LOGIC = '''
def _blocks(state):
    raw = state.get("blockedUsers")
    if not isinstance(raw, list):
        return None
    out = []
    for row in raw:
        if isinstance(row, dict):
            out.append((_norm(row.get("username")), _norm(row.get("comment"))))
        elif isinstance(row, str):
            out.append((_norm(row), ""))
        else:
            return None
    return out


def score_checks(state):
    rows = _blocks(state)
    if rows is None:
        rows = []
    only = rows[0] if len(rows) == 1 else None

    blocked = only is not None and only[0] == _norm(TARGET_USER)
    reason_ok = blocked and only[1] == _norm(EXPECTED_TEXT)

    return {
        "block_list_holds_only_derived_author": bool(blocked),
        "block_reason_carries_derived_count": bool(reason_ok),
    }
'''


def component_names(task):
    if task["vessel"] == "message":
        return ["message_thread_to_derived_author", "body_carries_derived_count"]
    return ["block_list_holds_only_derived_author", "block_reason_carries_derived_count"]


def fixture_block(task):
    fixture = {
        "current_user": CURRENT_USER,
        "target_user": task["author"],
        "expected_text": expected_body(task),
    }
    return json.dumps(fixture, indent=2)


def reward_source(task):
    names = component_names(task)
    logic = MESSAGE_LOGIC if task["vessel"] == "message" else BLOCK_LOGIC
    return '''"""Deterministic reward for %(tid)s.

The recipient and the number written into the vessel are both products of a
two-hop join the instruction never spells out: the byline on a row of
/f/%(forum)s/comments, then the below-zero row count on that user's own
Comments tab. Both components are positive statements about what the agent made
true, so an untouched episode scores exactly 0.0.

Scored off current_state only; nothing is diffed against initial_state.
"""

import json

FIXTURE = json.loads(r"""%(fixture)s""")

CURRENT_USER = FIXTURE["current_user"]
TARGET_USER = FIXTURE["target_user"]
EXPECTED_TEXT = FIXTURE["expected_text"]

COMPONENT_WEIGHTS = {
    "%(c0)s": 0.4,
    "%(c1)s": 0.6,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

%(helpers)s
%(logic)s

def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    app = None
    if isinstance(apps, dict):
        for key in ("reddit", "webarena_reddit_mock"):
            candidate = apps.get(key)
            if isinstance(candidate, dict):
                app = candidate
                break
    state = app.get("current_state") if isinstance(app, dict) else None
    if not isinstance(state, dict):
        state = {}

    checks = score_checks(state)
    components = []
    total = 0.0
    for name in ("%(c0)s", "%(c1)s"):
        satisfied = bool(checks.get(name))
        earned = COMPONENT_WEIGHTS[name] if satisfied else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": "%%s=%%s" %% (name, satisfied),
        })
    return {"score": round(total, 6), "components": components}
''' % dict(tid=task["task_id"], forum=task["forum"], fixture=fixture_block(task),
           c0=names[0], c1=names[1], helpers=SHARED_HELPERS, logic=logic)


def nemo_reward_source(task):
    names = component_names(task)
    logic = MESSAGE_LOGIC if task["vessel"] == "message" else BLOCK_LOGIC
    return '''"""NeMo-Gym reward program for %(tid)s.

Same rubric as reward.py. Reads current_state from GET /go?sid=... and prints
REWARD: <float> on every output path. Standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

FIXTURE = json.loads(r"""%(fixture)s""")

CURRENT_USER = FIXTURE["current_user"]
TARGET_USER = FIXTURE["target_user"]
EXPECTED_TEXT = FIXTURE["expected_text"]

COMPONENT_WEIGHTS = {
    "%(c0)s": 0.4,
    "%(c1)s": 0.6,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

%(helpers)s
%(logic)s

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name in ("%(c0)s", "%(c1)s"):
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    print("COMPONENTS: " + json.dumps(
        dict((key, bool(value)) for key, value in checks.items()), sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
''' % dict(tid=task["task_id"], fixture=fixture_block(task),
           c0=names[0], c1=names[1], helpers=SHARED_HELPERS, logic=logic)


# --------------------------------------------------------------------------- #
# initial_setup source                                                         #
# --------------------------------------------------------------------------- #

SETUP_TEMPLATE = '''"""NeMo-Gym initial setup for %(tid)s.

Read-modify-write against the reddit mock's state API: GET /go?sid=..., mutate
the WHOLE document, POST it back with {"action":"set","state":<document>}.
reddit REPLACES on a partial `set`, so a partial post would leave the reward
reading a near-empty state; posting the full document is correct regardless.

What is injected, and why:
  * %(ncount)d comments authored by %(author)s, appended to `newComments`
    (consumed by overlay.mergeComments). The newest of them is timestamped
    after the whole frozen corpus, so it becomes the top row of
    /f/%(forum)s/comments and is what the two-hop join has to resolve.
  * %(negcount)d of them score below zero and exactly one sits at netScore 0, so
    "below zero" and "zero or below" give different answers and the predicate
    has to actually be applied.
  * The parent submissions are patched through `submissionEdits` with
    commentCount + 1 and lastActive moved to the new comment's timestamp,
    which is what AppContext.addComment writes alongside a real comment. Each
    edit carries the full seeded record because a submissionEdits entry
    REPLACES the frozen row on read.

Nothing here touches `messages` or `blockedUsers`, the two vessels the rubric
scores, so the injected lane still scores exactly 0.0 before the agent acts.

Standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

NEW_COMMENTS = json.loads(r"""%(comments)s""")

SUBMISSION_EDITS = json.loads(r"""%(edits)s""")

NEXT_COMMENT_ID = 3000500


def main():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()

    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        raise RuntimeError("/go returned neither current_state nor initial_state")

    existing = state.get("newComments")
    if not isinstance(existing, list):
        existing = []
    seen = set(str(row.get("id")) for row in existing if isinstance(row, dict))
    for record in NEW_COMMENTS:
        if str(record["id"]) not in seen:
            existing.append(record)
            seen.add(str(record["id"]))
    state["newComments"] = existing

    edits = state.get("submissionEdits")
    if not isinstance(edits, dict):
        edits = {}
    for key in SUBMISSION_EDITS:
        edits[key] = SUBMISSION_EDITS[key]
    state["submissionEdits"] = edits

    next_id = state.get("nextCommentId")
    if not isinstance(next_id, int) or next_id < NEXT_COMMENT_ID:
        state["nextCommentId"] = NEXT_COMMENT_ID

    posted = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=180,
    )
    posted.raise_for_status()
    print("SETUP_OK " + str(len(NEW_COMMENTS)) + " comments injected")


try:
    main()
except Exception as exc:
    print("SETUP_ERROR: " + repr(exc))
    sys.exit(1)
'''


def setup_source(task, subs):
    records = INJECTIONS[task["n"]]
    edits = submission_edits_for(records, subs)
    return SETUP_TEMPLATE % dict(
        tid=task["task_id"],
        author=task["author"],
        forum=task["forum"],
        ncount=len(records),
        negcount=len([r for r in records if r["netScore"] < 0]),
        comments=json.dumps(records, indent=2),
        edits=json.dumps(edits, indent=2, sort_keys=True),
    )


# --------------------------------------------------------------------------- #
# replay draft                                                                 #
# --------------------------------------------------------------------------- #

REPLAY_TEMPLATE = '''"""Golden replay DRAFT for %(tid)s.

Not executed at authoring time. Every hop below is a rendered control reached by
clicking from start_path "/":

  1. site nav "Forums" -> the forum index (paged by offset segment)
  2. the f/%(forum)s card link
  3. the "Comments" tab in ListNav (ListNav.jsx:167-174) -> /f/%(forum)s/comments
  4. row %(rank)d's author byline (CommentRow.jsx:102-104) -> /user/%(author)s
  5. the profile "Comments" tab (UserNav.jsx) -> /user/%(author)s/comments
  6. page with the "Next" pager while one exists (%(pages)d page(s) here) and
     count rows whose vote score is below zero -> %(count)d
  7. sidebar Toolbox -> "%(tool_label)s" (UserSidebar.jsx:38-42)
  8. fill %(field)s with "%(text)s" and submit

Derived facts, checked against src/data/comments.json:
  anchor comment id %(anchor)d, timestamp %(anchor_ts)s
  %(author)s: %(total)d comments total, %(count)d below zero, %(zeros)d at exactly zero
"""

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
SID = "REPLACE_ME"
FORUM = "%(forum)s"
AUTHOR = "%(author)s"
TEXT = "%(text)s"


def run(page):
    page.goto("%%s/?sid=%%s" %% (BASE_URL, SID))
    page.get_by_role("link", name="Forums").first.click()
    # Page the forum index by its offset segments until the card is rendered.
    while page.get_by_role("link", name=FORUM, exact=True).count() == 0:
        page.get_by_role("link", name="Next").first.click()
    page.get_by_role("link", name=FORUM, exact=True).first.click()
    page.get_by_role("link", name="Comments", exact=True).first.click()

    row = page.locator("article.comment").nth(%(rank_index)d)
    row.locator("h1.comment__info a").first.click()

    page.get_by_role("link", name="Comments", exact=True).first.click()
    # Count below-zero rows across every page of the profile Comments tab.
    below = 0
    while True:
        for i in range(page.locator("article.comment").count()):
            score = page.locator("article.comment span.vote__net-score").nth(i).inner_text()
            if score.replace("\\u2212", "-").strip().startswith("-"):
                below += 1
        nxt = page.get_by_role("link", name="Next")
        if nxt.count() == 0:
            break
        nxt.first.click()
    assert below == %(count)d, below

    page.get_by_role("link", name="%(tool_label)s").first.click()
    page.fill("%(field)s", TEXT)
    page.get_by_role("button", name="%(submit_label)s").first.click()
    page.wait_for_timeout(500)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        run(page)
        browser.close()


if __name__ == "__main__":
    main()
'''


def replay_source(task):
    if task["vessel"] == "message":
        tool_label, field, submit_label = "Send message", "#message_body", "Send"
    else:
        tool_label, field, submit_label = "Block user", "#user_block_comment", "Block"
    return REPLAY_TEMPLATE % dict(
        tid=task["task_id"], forum=task["forum"], author=task["author"],
        rank=task["rank"], rank_index=task["rank"] - 1, pages=task["pages"],
        count=task["count"], total=task["total"], zeros=task["zeros"],
        anchor=task["anchor_comment"], anchor_ts=task["anchor_ts"],
        text=expected_body(task), tool_label=tool_label, field=field,
        submit_label=submit_label)


# --------------------------------------------------------------------------- #
# bundle assembly                                                              #
# --------------------------------------------------------------------------- #

def success_criteria(task):
    text = expected_body(task)
    join = ("%s is the author of the %s comment rendered by /f/%s/comments, a "
            "feed fixed newest-first (timestamp DESC, id DESC); comment id %d, "
            "%s." % (task["author"], task["rank_word"], task["forum"],
                     task["anchor_comment"], task["anchor_ts"]))
    count = ("%d is the number of %s's own comments with a score below zero, "
             "counted over %d comment rows on /user/%s/comments (%d page(s)); "
             "%d of that user's comments sit at exactly zero and must not be "
             "counted." % (task["count"], task["author"], task["total"],
                           task["author"], task["pages"], task["zeros"]))
    if task["vessel"] == "message":
        first = ("messages holds exactly one thread, its participants are "
                 "exactly %s and %s, and it holds exactly one message sent by "
                 "%s." % (CURRENT_USER, task["author"], CURRENT_USER))
        second = ("That message's body, whitespace-collapsed and compared "
                  "case-insensitively, is exactly \"%s\"." % text)
    else:
        first = ("blockedUsers holds exactly one row and its username is %s."
                 % task["author"])
        second = ("That row's comment, whitespace-collapsed and compared "
                  "case-insensitively, is exactly \"%s\"." % text)
    return [first, second, join, count]


def build(task, subs):
    tid = "%s_%s_%s" % (SLUG, task["slug"], task["n"])
    task["task_id"] = tid
    directory = os.path.join(OUT, tid)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

    injected = task["n"] in INJECTIONS
    text = expected_body(task)

    if task["style"] == "terse":
        words = len(task["instruction"].split())
        assert words <= 40, (tid, words)

    with open(os.path.join(directory, "task_instruction.json"), "w") as fh:
        json.dump({
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": "webarena_reddit_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success_criteria(task),
        }, fh, indent=2)
        fh.write("\n")

    if injected:
        records = INJECTIONS[task["n"]]
        negatives = [r for r in records if r["netScore"] < 0]
        zeros = [r for r in records if r["netScore"] == 0]
        preconditions = [
            "newComments: %d comments authored by %s appended through the "
            "overlay (overlay.js mergeComments). The newest, id %d at %s, is "
            "later than the whole frozen corpus, so it becomes row 1 of "
            "/f/%s/comments and is the anchor the join must resolve."
            % (len(records), task["author"], records[0]["id"],
               records[0]["timestamp"], task["forum"]),
            "%d of the injected comments score below zero, raising %s's "
            "below-zero total from the seeded 1 to %d - the answer is set by "
            "the injection, not memorisable from the pristine seed."
            % (len(negatives), task["author"], task["count"]),
            "%d injected comment sits at netScore 0 exactly, so an agent that "
            "counts 'zero or below' writes %d and scores 0.0."
            % (len(zeros), task["count"] + task["zeros"]),
            "submissionEdits: the %d parent submissions are replaced by their "
            "full seeded records with commentCount + 1 and lastActive moved to "
            "the injected timestamp, matching what AppContext.addComment "
            "(:473-476) writes alongside a real comment."
            % len(set(r["submission"] for r in records)),
            "Neither `messages` nor `blockedUsers` is touched, so the injected "
            "lane still scores exactly 0.0 before the agent acts.",
        ]
    else:
        preconditions = []

    notes = [
        "Skill chain (exactly two skills, R7 retrieval -> A7 action): %s."
        % ("byline of the %s comment on /f/%s/comments -> that user's profile "
           "Comments tab -> count of their own below-zero comments -> carry the "
           "count into a %s"
           % (task["rank_word"], task["forum"],
              "private message body" if task["vessel"] == "message"
              else "block reason")),
        "Writeback vessel: %s. createInitialData() seeds both messages: [] and "
        "blockedUsers: [] (dataManager.js:95-97), so an untouched episode "
        "scores exactly 0.0 on both components."
        % ("messages[0].messages[0].body, appended by ComposeMessagePage.jsx:61"
           if task["vessel"] == "message"
           else "blockedUsers[0].comment, appended by AppContext.blockUser:661 "
                "from the BlockUserPage #user_block_comment textarea"),
        "Click path from '/': site nav Forums -> forum index (offset paging) -> "
        "f/%s -> the Comments tab rendered by ListNav.jsx:167-174 -> the row's "
        "author byline (CommentRow.jsx:102-104) -> the profile Comments tab "
        "(UserNav.jsx) -> Toolbox '%s' (UserSidebar.jsx:38-42). Every hop is a "
        "rendered control; nothing is typed."
        % (task["forum"], "Send message" if task["vessel"] == "message"
           else "Block user"),
        "The /f/{forum}/comments firehose is fixed newest-first with no sort "
        "control (CommentsFirehosePage.jsx), sorting timestamp DESC then id "
        "DESC, so the ordinal in the instruction is a total order with no tie "
        "and none of the /new id-vs-timestamp ambiguity that afflicts the "
        "newest-post join.",
        "Retrieval is forced: neither %s nor %d appears in the instruction. An "
        "agent that skips the join messages/blocks the wrong user and scores "
        "0.0; an agent that finds the user but does not page the Comments tab "
        "writes the wrong integer and forfeits 0.6."
        % (task["author"], task["count"]),
        "Margin: the neighbouring row of /f/%s/comments is by %s, whose "
        "below-zero total is %d, so an off-by-one row read changes both the "
        "recipient and the number."
        % (task["forum"], task["neighbour"], task["neighbour_count"]),
        "Predicate margin: %s has %d comments at exactly zero, so 'below zero' "
        "(%d) and 'zero or below' (%d) are different answers."
        % (task["author"], task["zeros"], task["count"],
           task["count"] + task["zeros"]),
        "CORRECTIONS #49 / #31: no stored aggregate is used. The count is a row "
        "count computed the way /user/{n}/comments renders it, and no "
        "submission commentCount or users[].commentCount is read or written "
        "back.",
        "CORRECTIONS B6-17: the agent writes a COUNT, a non-negative integer, "
        "never a negative score - Vote.jsx:54-56 renders U+2212 plus a hidden "
        "second U+2212 and could never match an ASCII rubric.",
        "Both reward programs read current_state only, never initial_state or "
        "state_diff.",
        "Inspirations informed shape only; no benchmark intent, entity "
        "combination or reference answer is reused verbatim.",
    ]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [{
            "name": "webarena_reddit_mock",
            "source_name": "reddit",
            "base_url_env": "CUA_GYM_WEBARENA_REDDIT_URL",
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
            "skills": ["R7", "A7"],
            "skill_chain": (
                "join the %s row of /f/%s/comments to its author, count that "
                "user's below-zero comments on their profile Comments tab -> "
                "write the count into a %s"
                % (task["rank_word"], task["forum"],
                   "private message" if task["vessel"] == "message"
                   else "block reason")),
            "derived_from": "block_user_with_negative_count_diy_newest_poster_001",
            "official_analogues": task["analogues"],
            "injected_preconditions": preconditions,
            "topic": SLUG,
            "inspiration_ids": INSPIRATION_IDS,
            "authoring_notes": notes,
        },
    }
    with open(os.path.join(directory, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(directory, "reward.py"), "w") as fh:
        fh.write(reward_source(task))
    with open(os.path.join(directory, "nemo_reward.py"), "w") as fh:
        fh.write(nemo_reward_source(task))

    setup_code = None
    if injected:
        setup_code = setup_source(task, subs)
        with open(os.path.join(directory, "initial_setup.py"), "w") as fh:
            fh.write(setup_code)

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_reddit_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": "webarena_reddit_mock",
                "initial_setup": setup_code,
                "eval_reward_code": nemo_reward_source(task),
            },
        }
    }
    with open(os.path.join(directory, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2)
        fh.write("\n")

    with open(os.path.join(BATCH, "replays", tid + ".py"), "w") as fh:
        fh.write(replay_source(task))

    return tid, row, text


def main():
    subs = seeded_submissions()
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)

    index = {"schema_version": 2, "tasks": []}
    rows = []
    summary = []
    for task in TASKS:
        tid, row, text = build(task, subs)
        index["tasks"].append({"task_id": tid, "path": tid + "/task.json"})
        rows.append(row)
        summary.append((tid, task, text))

    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")

    with open(os.path.join(BATCH, "GENERATION.md"), "w") as fh:
        fh.write(generation_md(summary))

    for tid, _task, _text in summary:
        print(tid)


def generation_md(summary):
    lines = []
    a = lines.append
    a("# Batch 6 - lane 29 - reddit - `two_hop_negative_comment_note`\n")
    a("10 bundles. Assigned pair **R7 -> A7**: resolve a two-hop join from a")
    a("row of a forum's Comments tab to that commenter's profile, count how many")
    a("of their own comments score below zero, and carry the count into a")
    a("persisted vessel (a private message body or a block reason).\n")
    a("`metadata.skills` is exactly `[\"R7\", \"A7\"]` on all ten. There is no")
    a("third step: the count is part of the join's second hop, and the write is")
    a("the single action.\n")
    a("## Split\n")
    a("| | |")
    a("|---|---|")
    a("| bundles | 10 |")
    a("| difficulty | **10 medium**, exactly two skills each |")
    a("| style | **7 terse** (001, 002, 004, 005, 006, 007, 009) / **3 explicit** (003, 008, 010) |")
    a("| shape | **10 retrieval_writeback** |")
    a("| `start_path: \"/\"` | **10 / 10** |")
    a("| ships `initial_setup.py` | 4 (007, 008, 009, 010) |")
    a("| writeback vessel | 6 private message, 4 block reason |")
    a("| terse word counts | %s (cap 40) |"
      % ", ".join(str(len(t["instruction"].split()))
                  for _i, t, _x in summary if t["style"] == "terse"))
    a("")
    a("## Per-task table\n")
    a("| id | style | anchor row | derived author | comments | below zero | at zero | pages | vessel | written string |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for tid, t, text in summary:
        a("| `%s` | %s | `/f/%s/comments` row %d | `%s` | %d | **%d** | %d | %d | %s | `%s` |"
          % (tid, t["style"], t["forum"], t["rank"], t["author"], t["total"],
             t["count"], t["zeros"], t["pages"],
             "message" if t["vessel"] == "message" else "block reason", text))
    a("")
    a("## Why this join, and not the official one\n")
    a("The official phrasing (webarena-27..31) joins on *the author of the")
    a("newest post*. On this seed that join is answer-degenerate - 85 of 95")
    a("forums return 0 - and it inherits reddit's `/f/X/new` ambiguity, where")
    a("id-DESC order and timestamp order disagree at the head of 59 of 95")
    a("forums.\n")
    a("This lane joins on the **per-forum comment firehose** `/f/{forum}/comments`")
    a("instead (registered at `App.jsx:124`, reached by the rendered `Comments`")
    a("tab at `ListNav.jsx:167-174`, ordered `timestamp DESC, id DESC` with no")
    a("sort control at all - `CommentsFirehosePage.jsx` `COMMENT_SORT`). That")
    a("ordering is a **total order with no tie**, so the ordinal in each")
    a("instruction picks exactly one row, and every row carries an author byline")
    a("link (`CommentRow.jsx:102-104`). Same skill, no ambiguity, and a much")
    a("larger entity pool.\n")
    a("## Mechanism claims verified in source\n")
    a("* `/f/{forum}/comments` registered - `App.jsx:124`.")
    a("* `Comments` tab rendered on every forum listing - `ListNav.jsx:167-174`,")
    a("  href built at `ListingPage.jsx:184`.")
    a("* Firehose order and 25-row cursor - `CommentsFirehosePage.jsx`")
    a("  (`COMMENT_SORT`, `paginateComments`).")
    a("* Comment row byline link to `/user/{author}` - `CommentRow.jsx:102-104`.")
    a("* Profile `Comments` tab - `UserNav.jsx` `TABS`; rows sorted")
    a("  `timestamp DESC, id DESC`, 25/page - `UserPage.jsx:50-64` +")
    a("  `userPaging.js`.")
    a("* Score rendered per row on the profile tab - `UserCommentRow.jsx`")
    a("  imports `Vote`.")
    a("* Toolbox `Send message` / `Block user` on another user's profile -")
    a("  `UserSidebar.jsx:38-42`.")
    a("* Message persistence - `ComposeMessagePage.jsx:44-62` appends")
    a("  `{id, participants, messages:[{id, sender, body, timestamp}]}` to")
    a("  `state.messages`.")
    a("* Block persistence - `AppContext.blockUser` (`:661`) appends")
    a("  `{username, timestamp, comment}` to `state.blockedUsers`; the textarea")
    a("  is `#user_block_comment` (`BlockUserPage.jsx`).")
    a("* Empty baselines - `dataManager.js:95-97` seeds `blockedUsers: []` and")
    a("  `messages: []`.")
    a("* `newComments` / `submissionEdits` are consumed on read -")
    a("  `overlay.js mergeComments` / `mergeSubmissions`; a `submissionEdits`")
    a("  entry REPLACES the frozen row, so each injected edit carries the whole")
    a("  seeded record.")
    a("* `/go` falls back to `createInitialData()` when no state file exists")
    a("  (`vite.config.js` `/go` handler), so the read-modify-write setup works")
    a("  on a pristine sid.")
    a("* Served bundle is `dist/assets/index-DkKlva4C.js`, built 2026-08-17")
    a("  23:52. Every source file this lane depends on is dated 21:18, i.e.")
    a("  older than the build, so every claim above is live.\n")
    a("## Tie and margin checks\n")
    a("All counts below were computed directly over `src/data/comments.json`")
    a("(24,149 rows) and `src/data/submissions.json` (8,012 rows).\n")
    a("* **Anchor uniqueness.** The firehose sort key is `(timestamp, id)`")
    a("  descending. Ids are unique, so the ordinal named in each instruction")
    a("  resolves to exactly one row - there is no tie to break.")
    a("* **Neighbour margin.** For each non-injected task the adjacent firehose")
    a("  row is by a *different* author whose below-zero total is 0, so a")
    a("  one-row slip changes both the recipient and the number:")
    for tid, t, _x in summary:
        if t["n"] in INJECTIONS:
            continue
        a("  * `%s` row %d = %s (%d below zero); neighbour %s (%d)."
          % (t["forum"], t["rank"], t["author"], t["count"],
             t["neighbour"], t["neighbour_count"]))
    a("* **Predicate margin.** Six of the ten targets own at least one comment")
    a("  at exactly netScore 0, so 'below zero' and 'zero or below' are")
    a("  different integers and the agent has to apply the strict predicate:")
    for tid, t, _x in summary:
        if t["zeros"]:
            a("  * `%s`: %d below zero vs %d at-or-below zero."
              % (t["author"], t["count"], t["count"] + t["zeros"]))
    a("* **Paging.** `003` (`mineinhusdson`, 42 comments) is the only two-page")
    a("  target, and both of that user's zero-score comments sit at positions 32")
    a("  and 36 - page 2. An agent that stops after page 1 sees neither the")
    a("  second page nor the distractors.")
    a("* **Guessability.** Four targets answer 1, two answer 2, two answer 3,")
    a("  one answers 4. The count alone is never sufficient: it is worth 0.6 and")
    a("  is only reachable through a component (0.4) that requires the correct")
    a("  derived author.\n")
    a("## Injections (007-010)\n")
    a("Each injected bundle appends 2-4 `newComments` rows for the target")
    a("author, dated 2023-04-02 - after the corpus maximum")
    a("(2023-03-31T23:59) and before the seeded fixture post (2023-06-12).")
    a("The newest of them becomes row 1 of the forum's Comments tab, which is")
    a("what the join resolves; the rest raise the below-zero count and plant a")
    a("netScore-0 distractor.\n")
    a("Rationale, per the contract's guidance on using setup to raise")
    a("difficulty rather than to repair data:\n")
    a("* **The answer stops being a property of the pristine seed.** Without")
    a("  injection the below-zero count for almost every reachable author is 1,")
    a("  which a model can learn to emit without reading anything. 007-010")
    a("  answer 3, 4, 2 and 3.")
    a("* **The distractor makes the predicate real.** Exactly one injected row")
    a("  per task sits at netScore 0, so 'zero or below' produces a different,")
    a("  wrong integer.")
    a("* **Plausibility.** A user having a bad week in one forum is an ordinary")
    a("  state; nothing on any single screen contradicts anything else, and the")
    a("  parent submissions are patched exactly the way `addComment` patches")
    a("  them (`commentCount + 1`, `lastActive` moved).")
    a("* **Nothing pre-satisfies the rubric.** `messages` and `blockedUsers` are")
    a("  untouched, so the injected lane scores 0.0 before the agent acts.\n")
    a("Every setup program is a read-modify-write (`GET /go` -> mutate the whole")
    a("document -> `POST {\"action\":\"set\",\"state\": <document>}`), because")
    a("reddit REPLACES on a partial `set`.\n")
    a("## Rejected candidates\n")
    a("* **The official newest-post join, as written.** Answer-degenerate (0 for")
    a("  85 of 95 forums) and ambiguous at the head of 59 forums. Rejected in")
    a("  favour of the firehose anchor.")
    a("* **`f/DIY` -> `ziostraccette`.** The lane brief lists this as one of the")
    a("  four non-trivial newest-post joins. It is a fine join, but `f/DIY`'s")
    a("  `/new` head (id 119019, 2023-03-31T19:01) is **not** the forum's")
    a("  latest-timestamped submission, so 'the newest post' has two defensible")
    a("  readings there. Rejected as an anchor.")
    a("* **`f/MechanicalKeyboards` / `f/philadelphia` -> `AutoModerator`** (20")
    a("  below zero out of 490 comments, twenty pages) and **`f/BridgeportCT` /")
    a("  `f/yonkers` -> `[deleted]`** (3,096 comments, and not a resolvable")
    a("  recipient anyway). Infeasible to page inside an episode.")
    a("* **`f/nyc` row 5 and `f/Connecticut` row 4**, both `[deleted]`: no")
    a("  profile to message or block. Every ordinal used in this lane was")
    a("  checked to be a real, resolvable, non-self user.")
    a("* **Writing back a negative score verbatim.** `Vote.jsx:54-56` renders")
    a("  U+2212 plus a hidden second U+2212, so a copied value can never match")
    a("  an ASCII-hyphen rubric (CORRECTIONS B6-17). Every writeback here is a")
    a("  non-negative count.")
    a("* **Writing back a submission's comment count** - forbidden by")
    a("  CORRECTIONS #49 (stored `commentCount` disagrees with the rendered rows")
    a("  for 81% of submissions). Not used, in either direction.")
    a("* **`users[].commentCount` / `negativeCommentCount` as ground truth** -")
    a("  writable keys that change no pixel, and stale for every user")
    a("  (CORRECTIONS #31). Every count here is a rendered row count.")
    a("* **A third step** (e.g. also updating the biography, or also subscribing")
    a("  to the forum). Dropped rather than relabelled: batch 6 medium is")
    a("  exactly two skills.\n")
    a("## Census / brief claims found wrong\n")
    a("* The census's \"~5 usable entities for the negative-comment join\" is")
    a("  confirmed wrong, and `CENSUS_ERRATA` / CORRECTIONS #33 are right: with")
    a("  the firehose anchor, ranks 1-6 of the 95 per-forum Comments tabs alone")
    a("  yield **40** (forum, rank) anchors whose author has at least one")
    a("  below-zero comment and at most 60 comments total. The binding")
    a("  constraint is click-reachability, exactly as the brief says.")
    a("* **The lane brief's DIY entity is not safe as written.** The brief")
    a("  offers `DIY -> ziostraccette` among 'the non-trivial ones' for the")
    a("  newest-post join without flagging that `f/DIY` is in the ambiguous set")
    a("  the same brief warns about two paragraphs later (id head 119019 at")
    a("  19:01 vs the timestamp head at 23:55 on 2023-03-31). Of the four")
    a("  offered, only `lakewood`, `Newark` and `WorcesterMA` have coincident")
    a("  id-order and timestamp-order heads. This lane avoids the newest-post")
    a("  join entirely, but the brief's list should be corrected.")
    a("* Otherwise the brief matched the source everywhere it was checked:")
    a("  reddit replaces on partial `set`, the firehose exists and is fixed")
    a("  newest-first, profile sidebars carry no aggregate counts, and both")
    a("  writeback vessels seed empty.\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
