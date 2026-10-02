#!/usr/bin/env python3
"""Emit the ten batch-6 reddit bundles for lane 15 (slug newest_thread_upvote).

Authoring-time generator only. Nothing here runs at episode time.
"""
import json
import os
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output/tasks/reddit"
BATCH = OUT / "_batches/newest_thread_upvote"
SLUG = "newest_thread_upvote"

# --------------------------------------------------------------------------- #
# Injected fixtures
# --------------------------------------------------------------------------- #

VERMONT_ROW = {
    "id": 200000,
    "forum": "vermont",
    "author": "BudsKind802",
    "title": "Town meeting moved to the Barre auditorium this year",
    "body": "The usual hall is being re-roofed, so Tuesday's meeting is at the "
            "auditorium on Seminary Hill. Doors at 6, warning is on the town site.",
    "timestamp": "2023-04-01T18:42:09+00:00",
    "lastActive": "2023-04-01T18:42:09+00:00",
    "ranking": 2,
    "netScore": 2,
    "commentCount": 0,
    "slug": "town-meeting-moved-to-the-barre-auditorium-this-year",
}

MUSIC_EDIT = {
    "35510": {
        "id": 35510,
        "forum": "Music",
        "author": "Private_Zannon",
        "title": "'Fame’ and ‘Flashdance’ singer Irene Cara has died aged 63.",
        "url": "https://www.nme.com/news/music/fame-and-flashdance-singer-irene-cara-has-died-aged-63-3356136",
        "timestamp": "2022-11-26T11:44:12+00:00",
        "lastActive": "2022-11-27T18:10:22+00:00",
        "ranking": 235,
        "netScore": 4195,
        "commentCount": 156,
        "slug": "fame-and-flashdance-singer-irene-cara-has-died-aged-63",
        "userFlag": "t3_z55mln",
    }
}

# --------------------------------------------------------------------------- #
# The lane
# --------------------------------------------------------------------------- #

TASKS = [
    dict(
        n=1,
        tid=SLUG + "_todayilearned_new_head_001",
        forum="todayilearned",
        target=135879,
        direction=1,
        style="terse",
        instruction=(
            "f/todayilearned moves fast. Work out which submission in that forum "
            "was posted most recently and give it an upvote."
        ),
        chain="open f/todayilearned and order it by New -> take the head row (135879) -> upvote it",
        analogues=["Upvote the newest post in books forum"],
        insp=["webarena-404", "webarena-405"],
        derived_from="newest_post_upvote_reply_tifu_vote_only_005",
        margin=("135879 posted 2023-03-31T22:23:30, the runner-up 135878 at "
                "2023-03-31T21:30:01 -- 53m29s clear. f/todayilearned is one of the "
                "35 forums whose id order and timestamp order agree at the head, so "
                "'most recently posted' and 'first row of /new' name the same post."),
        setup=None,
        near_miss=135878,
    ),
    dict(
        n=2,
        tid=SLUG + "_hartford_second_newest_002",
        forum="Hartford",
        target=119706,
        direction=1,
        style="terse",
        instruction=(
            "In f/Hartford, upvote the second-newest submission -- not the newest "
            "one, the post that went up directly before it."
        ),
        chain="open f/Hartford ordered by New -> take the SECOND row (119706) -> upvote it",
        analogues=["Upvote the newest post in DIY forum"],
        insp=["webarena-405", "webarena-408"],
        derived_from="newest_post_upvote_reply_stamfordct_explicit_009",
        margin=("Rows 1-3 of f/Hartford are 119707 (2023-03-31T20:57:59), 119706 "
                "(2023-03-29T22:30:58) and 119705 (2023-03-29T04:01:45) under BOTH "
                "id DESC and timestamp DESC. Target is rank 2; the gap to rank 1 is "
                "1d22h27m and to rank 3 is 18h29m. An agent that stops at the newest "
                "post lands on 119707 and scores 0.0."),
        setup=None,
        near_miss=119707,
    ),
    dict(
        n=3,
        tid=SLUG + "_monitor_oldest_thread_003",
        forum="monitor",
        target=21887,
        direction=1,
        style="explicit",
        instruction=(
            "f/monitor is a tiny forum and I am doing some archaeology in it. Look "
            "at every submission the forum holds and work out which one was posted "
            "earliest -- the oldest thread in the forum, judged by its posting date "
            "and not by where it happens to sit in a listing. Upvote that one post. "
            "Do not vote on any of the forum's other submissions, and in particular "
            "do not upvote the newest one by mistake."
        ),
        chain="open f/monitor (6 rows, one page) -> read each row's posting date -> "
              "take the earliest (21887) -> upvote it",
        analogues=["Upvote the newest post in explain like im 5 forum"],
        insp=["webarena-408"],
        derived_from=None,
        margin=("f/monitor holds 6 submissions, so the whole forum fits on one "
                "listing page (PER_PAGE 25). By timestamp they are 21887 "
                "2022-10-25T18:01:19, 42493 2022-11-03T19:19:05, 107539 "
                "2023-02-22T02:59:39, 107540 2023-02-27T19:49:24, 128354 "
                "2023-03-06T19:48:30 and 128355 2023-03-30T15:45:09. The oldest "
                "is 21887, clear of the next by 9 days 1h17m, and it is also the "
                "lowest id so the two readings agree. The newest, 128355, is the "
                "distractor the instruction warns about."),
        setup=None,
        near_miss=128355,
    ),
    dict(
        n=4,
        tid=SLUG + "_nottheonion_head_downvote_004",
        forum="nottheonion",
        target=130362,
        direction=-1,
        style="terse",
        instruction=(
            "The most recently posted submission in f/nottheonion is a rehash of a "
            "story that already ran last year. Downvote it."
        ),
        chain="open f/nottheonion ordered by New -> take the head row (130362) -> downvote it",
        analogues=["Upvote the newest post in DIY forum",
                   "Thumbs down the top 1 post ever in gadgets."],
        insp=["webarena-405", "webarena-714"],
        derived_from="newest_post_upvote_reply_worldnews_thank_author_003",
        margin=("130362 posted 2023-03-31T22:17:22, runner-up 130361 at "
                "2023-03-31T09:58:13 -- 12h19m09s clear, and f/nottheonion is in the "
                "clean 35 so id DESC and timestamp DESC agree at the head. Direction "
                "matters: the rubric wants -1, so an upvote scores 0.0."),
        setup=None,
        near_miss=130361,
    ),
    dict(
        n=5,
        tid=SLUG + "_jokes_runner_up_ever_005",
        forum="Jokes",
        target=119950,
        direction=-1,
        style="terse",
        instruction=(
            "f/Jokes has an all-time leaderboard and the post sitting second on it "
            "is a straight repost. Downvote that post."
        ),
        chain="open f/Jokes and read the all-time score ordering -> take rank 2 (119950) -> downvote it",
        analogues=["Thumbs down the top 2 post ever in history forum."],
        insp=["webarena-715"],
        derived_from="top_ever_post_downvote_science_runner_up_002",
        margin=("f/Jokes by netScore DESC: 119862 at 12708, 119950 at 9174, 77340 at "
                "8369. Rank 2 is 119950, 3534 below rank 1 and 805 above rank 3 -- "
                "no tie anywhere near the boundary the task uses. An agent that "
                "takes the leader scores 0.0."),
        setup=None,
        near_miss=119862,
    ),
    dict(
        n=6,
        tid=SLUG + "_showerthoughts_third_ever_006",
        forum="Showerthoughts",
        target=79688,
        direction=-1,
        style="terse",
        instruction=(
            "Give a downvote to the post with the third-highest score of all time "
            "in f/Showerthoughts."
        ),
        chain="open f/Showerthoughts and read the all-time score ordering -> take rank 3 (79688) -> downvote it",
        analogues=["Thumbs down the top 3 post ever in books."],
        insp=["webarena-716"],
        derived_from="top_ever_post_downvote_food_third_highest_003",
        margin=("f/Showerthoughts by netScore DESC: 15572 at 7286, 122241 at 6985, "
                "79688 at 6657, 57587 at 5701. Rank 3 is 79688, 328 below rank 2 and "
                "956 above rank 4. Checked at the rank the task actually uses, per "
                "CORRECTIONS #26 -- a clean rank-1 margin would not have licensed "
                "this."),
        setup=None,
        near_miss=122241,
    ),
    dict(
        n=7,
        tid=SLUG + "_deeplearning_top_ever_007",
        forum="deeplearning",
        target=124993,
        direction=1,
        style="terse",
        instruction=(
            "The highest-scoring post of all time in f/deeplearning is still worth "
            "boosting. Upvote it."
        ),
        chain="open f/deeplearning and read the all-time score ordering -> take rank 1 (124993) -> upvote it",
        analogues=["Thumbs down the top 1 post ever in gadgets.",
                   "Upvote the newest post in the deep learning forum"],
        insp=["webarena-714", "webarena-407"],
        derived_from="top_ever_post_downvote_space_all_time_leader_001",
        margin=("f/deeplearning by netScore DESC: 124993 at 173, 82403 at 168, 60308 "
                "at 149. The tightest top-ever margin in this lane, 5 points, but "
                "the seed carries no tie in any of the 95 forums at rank 1 and both "
                "scores render as plain integers."),
        setup=None,
        near_miss=82403,
    ),
    dict(
        n=8,
        tid=SLUG + "_vermont_injected_head_008",
        forum="vermont",
        target=200000,
        direction=1,
        style="terse",
        instruction=(
            "Something new landed in f/vermont today. Upvote whichever submission "
            "in that forum is the most recent one."
        ),
        chain="open f/vermont ordered by New -> take the head row (the injected 200000) -> upvote it",
        analogues=["Upvote the newest post in books forum"],
        insp=["webarena-404"],
        derived_from="newest_post_upvote_reply_consoles_dreamcast_001",
        margin=("The injected row 200000 is dated 2023-04-01T18:42:09, 1d18h53m47s "
                "after the seeded head 136081 (2023-03-30T23:48:22), and its id is "
                "the highest in the forum, so id DESC and timestamp DESC still "
                "agree. The correct answer is NOT the seeded head, so an agent that "
                "recalls f/vermont's pristine newest post scores 0.0."),
        setup="vermont",
        near_miss=136081,
    ),
    dict(
        n=9,
        tid=SLUG + "_music_top_ever_demoted_009",
        forum="Music",
        target=35510,
        direction=-1,
        style="explicit",
        instruction=(
            "f/Music is not ranking things sensibly at the moment, so do not trust "
            "the order the forum opens in. What I want is the single submission in "
            "f/Music with the highest score of all time -- read that off the "
            "all-time ordering, not off the forum's default page. Downvote that "
            "post. Leave every other submission in f/Music alone, and do not "
            "downvote whatever happens to be sitting at the top of the default page."
        ),
        chain="open f/Music, switch to the all-time score ordering -> take rank 1 "
              "(35510, demoted to page 2 of the default order) -> downvote it",
        analogues=["Thumbs down the top 1 post ever in gadgets.",
                   "Thumbs down the top 5 post ever in technology."],
        insp=["webarena-714", "webarena-718"],
        derived_from="top_ever_post_downvote_books_score_shift_leader_009",
        margin=("f/Music by netScore DESC: 35510 at 4195, 56626 at 3459, 35516 at "
                "3080 -- rank 1 clear by 736. After the injection 35510's `ranking` "
                "is 235, which sits between the 39th (242) and 40th/41st (227, 227) "
                "ranking values in the forum, so it lands at position 40 of the "
                "default order: page 2, since a listing page holds 25 rows. The "
                "default page-1 leader becomes 56626, which is the distractor."),
        setup="music",
        near_miss=56626,
    ),
    dict(
        n=10,
        tid=SLUG + "_wallstreetbets_head_010",
        forum="wallstreetbets",
        target=136620,
        direction=1,
        style="terse",
        instruction=(
            "Two posts went up in f/wallstreetbets minutes apart. Upvote whichever "
            "of the forum's submissions is the more recent of the two."
        ),
        chain="open f/wallstreetbets ordered by New -> take the head row (136620) -> upvote it",
        analogues=["Upvote the newest post in DIY forum"],
        insp=["webarena-405"],
        derived_from="newest_post_upvote_reply_memes_misclick_flip_002",
        margin=("136620 posted 2023-03-31T23:14:32, 136619 at 2023-03-31T23:06:18 -- "
                "8m14s apart, the tightest ordinal margin in the lane. Both rows "
                "render the same relative time string, so the discriminator is the "
                "New ordering (id DESC) or the absolute datetime in Time.jsx's "
                "title/datetime attributes; f/wallstreetbets is in the clean 35, so "
                "those two agree."),
        setup=None,
        near_miss=136619,
    ),
]

# --------------------------------------------------------------------------- #
# Templates
# --------------------------------------------------------------------------- #

REWARD_HEAD = '''"""{kind} for {tid}.

{blurb}

{margin}

Scored off the live session document only -- the rubric never diffs a baseline.
The single component is a positive statement about the collection the episode
ends with: `votes.submissions` must be EXACTLY the seeded vote plus this task's
own vote, so an agent that sprays votes across the listing scores 0.0 and an
untouched session scores 0.0 as well.
"""
'''

REWARD_BODY = '''
# The whole submission-vote ledger this episode must end with.
# `createInitialData()` seeds {{"1": 1}} from currentUser.json submissionVotes,
# so the task's own vote on {target} is the only addition.
EXPECTED_VOTES = json.loads(r"""{expected}""")

# The derived target and the row an agent that skipped the retrieval would hit.
TARGET_ID = "{target}"
NEAR_MISS_ID = "{near_miss}"

COMPONENT_WEIGHTS = {{
    "{component}": 1.0,
}}


def _vote_ledger(state):
    """`votes.submissions` as {{id string: non-zero int}}.

    This is exactly what Vote.jsx reads to pick the form's three-valued class
    ("vote" / "vote vote--user-upvoted" / "vote vote--user-downvoted"), so it is
    the user-visible record of which arrow is lit.
    """
    votes = state.get("votes")
    votes = votes if isinstance(votes, dict) else {{}}
    rows = votes.get("submissions")
    rows = rows if isinstance(rows, dict) else {{}}
    ledger = {{}}
    for key, raw in rows.items():
        try:
            num = int(raw)
        except (TypeError, ValueError):
            continue
        if num:
            ledger[str(key)] = num
    return ledger


def _expected_ledger():
    return dict((str(k), int(v)) for k, v in EXPECTED_VOTES.items())


def score_checks(state):
    ledger = _vote_ledger(state)
    return {{"{component}": ledger == _expected_ledger()}}


def score_details(state):
    ledger = _vote_ledger(state)
    return "votes.submissions=%s | target %s=%s | near miss %s=%s" % (
        json.dumps(ledger, sort_keys=True),
        TARGET_ID, json.dumps(ledger.get(TARGET_ID)),
        NEAR_MISS_ID, json.dumps(ledger.get(NEAR_MISS_ID)),
    )
'''

REWARD_TAIL_LOCAL = '''

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
    detail = score_details(state)

    components = []
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        satisfied = bool(checks.get(name))
        earned = COMPONENT_WEIGHTS[name] if satisfied else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": "%s=%s | %s" % (name, satisfied, detail),
        })
    return {"score": round(total, 6), "components": components}
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
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        if checks.get(name):
            total += COMPONENT_WEIGHTS[name]
    print("COMPONENTS: " + json.dumps(
        dict((k, bool(v)) for k, v in checks.items()), sort_keys=True))
    print("DETAILS: " + score_details(state))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {tid}.

{blurb}

Read-modify-write, per batch-6 rule B6-9: GET /go, mutate the document that
comes back, POST the WHOLE document. reddit's `{{"action": "set"}}` REPLACES the
stored state, so a partial post would leave the agent looking at a working site
while the reward read an almost-empty document.

Nothing here pre-satisfies the rubric: the rubric grades `votes.submissions`,
and this program does not touch that map.

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

{fixture}


def load_state():
    response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    response.raise_for_status()
    payload = response.json()
    state = payload.get("current_state")
    if not isinstance(state, dict):
        state = payload.get("initial_state")
    if not isinstance(state, dict):
        print("SETUP FAILED: /go returned neither current_state nor initial_state",
              file=sys.stderr)
        raise SystemExit(1)
    return dict(state)


def publish(state):
    response = requests.post(BASE_URL + "/post?sid=" + SID,
                             json={{"action": "set", "state": state}}, timeout=60)
    response.raise_for_status()
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    state = load_state()
{mutate}
    publish(state)


main()
'''

VERMONT_MUTATE = '''    rows = state.get("newSubmissions")
    rows = list(rows) if isinstance(rows, list) else []
    rows = [r for r in rows if str(r.get("id")) != str(INJECTED_ROW["id"])]
    rows.append(INJECTED_ROW)
    state["newSubmissions"] = rows

    # Keep the id allocator ahead of the injected row so a post the agent
    # creates during the episode cannot collide with it.
    try:
        nxt = int(state.get("nextSubmissionId"))
    except (TypeError, ValueError):
        nxt = 200000
    state["nextSubmissionId"] = max(nxt, int(INJECTED_ROW["id"]) + 1)

    # The forum card's stored submissionCount is already a live-site total that
    # disagrees with the rendered rows, but keep it moving in the right
    # direction so nothing on one screen contradicts itself.
    forums = state.get("forums")
    if isinstance(forums, list):
        bumped = []
        for forum in forums:
            row = dict(forum) if isinstance(forum, dict) else forum
            if isinstance(row, dict) and str(row.get("name")).lower() == "vermont":
                try:
                    row["submissionCount"] = int(row.get("submissionCount") or 0) + 1
                except (TypeError, ValueError):
                    pass
            bumped.append(row)
        state["forums"] = bumped
'''

MUSIC_MUTATE = '''    edits = state.get("submissionEdits")
    edits = dict(edits) if isinstance(edits, dict) else {}
    for key, record in DEMOTED.items():
        edits[key] = dict(record)
    state["submissionEdits"] = edits
'''

VERMONT_BLURB = (
    "A fresh post lands in f/vermont, dated after every seeded row in the "
    "forum and carrying a higher id than any of them, so the forum's New "
    "ordering and its timestamp ordering still agree. The point is that the "
    "correct answer is no longer f/vermont's pristine head (136081): an agent "
    "that answers from memory of the seed rather than from the page scores 0.0."
)

MUSIC_BLURB = (
    "f/Music's all-time leader 35510 is republished through `submissionEdits` "
    "with its `ranking` lowered from 4195 to 235 and its `netScore` left at "
    "4195. On the pristine seed `ranking == netScore` for 8,011 of 8,012 rows, "
    "so the default ordering and the all-time ordering are the same list "
    "(CORRECTIONS #25) and the retrieval is decoration. After the demotion "
    "35510 sits at position 40 of the default order -- page 2 -- while 56626 "
    "leads page 1, so the agent has to reach the all-time ordering to find it."
)


def dumps(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False)


def build(task):
    tid = task["tid"]
    d = OUT / tid
    d.mkdir(parents=True, exist_ok=True)

    target = str(task["target"])
    direction = task["direction"]
    verb = "upvote" if direction == 1 else "downvote"
    component = "vote_ledger_now_seed_plus_%s_%s" % (verb + "d", target)
    expected = json.dumps({"1": 1, target: direction})

    blurb = ("The entity is derived, never named: %s. The vote itself is one "
             "click, so the whole task is the retrieval, and the near miss %s "
             "is what an agent that skipped it records instead."
             % (task["chain"], task["near_miss"]))

    body = REWARD_BODY.format(expected=expected, target=target,
                              near_miss=task["near_miss"], component=component)

    reward = (REWARD_HEAD.format(kind="Deterministic reward", tid=tid,
                                 blurb=blurb, margin=task["margin"])
              + "\nimport json\n" + body + REWARD_TAIL_LOCAL)
    (d / "reward.py").write_text(reward)

    nemo_head = REWARD_HEAD.format(
        kind="NeMo-Gym reward program", tid=tid, blurb=blurb, margin=task["margin"])
    nemo = (nemo_head
            + "\nimport json\nimport sys\n\nimport requests\n\n"
              'SID = "__CUA_GYM_SID__"\n'
              'BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"\n'
            + body + REWARD_TAIL_NEMO)
    (d / "nemo_reward.py").write_text(nemo)

    setup_src = None
    injected = []
    if task["setup"] == "vermont":
        setup_src = SETUP_TEMPLATE.format(
            tid=tid, blurb=VERMONT_BLURB,
            fixture='INJECTED_ROW = json.loads(r"""\n%s\n""")' % dumps(VERMONT_ROW),
            mutate=VERMONT_MUTATE)
        injected = [
            "newSubmissions gains one row, id 200000, forum vermont, author "
            "BudsKind802, dated 2023-04-01T18:42:09 -- later than every seeded "
            "row in the forum and higher-id than all of them, so /new's id DESC "
            "and the timestamp ordering agree on it.",
            "Ranking convention: corpus-lookalike, so ranking == netScore == 2 "
            "(CORRECTIONS #24). The epoch-seconds convention is NOT used, "
            "because this row stands in for another user's ordinary post, not "
            "for something the current user just submitted.",
            "nextSubmissionId is advanced past 200000 so an agent-created post "
            "cannot collide with the injected id; f/vermont's stored "
            "submissionCount is incremented for on-screen consistency.",
            "votes.submissions is untouched, so the rubric is not pre-satisfied: "
            "the injected row starts with no vote from the current user.",
        ]
    elif task["setup"] == "music":
        setup_src = SETUP_TEMPLATE.format(
            tid=tid, blurb=MUSIC_BLURB,
            fixture='DEMOTED = json.loads(r"""\n%s\n""")' % dumps(MUSIC_EDIT),
            mutate=MUSIC_MUTATE)
        injected = [
            "submissionEdits[\"35510\"] republishes f/Music's all-time leader as "
            "the FULL record patchSubmission writes, with ranking lowered 4195 "
            "-> 235 and netScore left at 4195.",
            "235 sits between the 39th ranking value in the forum (242) and the "
            "40th/41st (227), so 35510 lands at position 40 of the default "
            "ordering -- page 2 at 25 rows per page -- while the all-time "
            "ordering still puts it first.",
            "This is what makes the retrieval load-bearing: on the pristine seed "
            "the default order and the all-time order are the same list in 94 of "
            "95 forums (CORRECTIONS #25), so without the demotion an agent could "
            "reach 35510 without ever reading a score ordering.",
            "votes.submissions is untouched, so the rubric is not pre-satisfied.",
        ]

    if setup_src is not None:
        (d / "initial_setup.py").write_text(setup_src)
    elif (d / "initial_setup.py").exists():
        os.remove(d / "initial_setup.py")

    success = [
        'votes.submissions["%s"] == %d, so the %s arrow on submission %s is lit '
        'for MarvelsGrantMan136.' % (target, direction, verb.replace("vote", ""),
                                     target),
        'votes.submissions is exactly {"1": 1, "%s": %d} -- the seeded vote on '
        'submission 1 plus this task\'s vote and nothing else.' % (target, direction),
        'The near miss %s carries no vote from this user.' % task["near_miss"],
    ]

    (d / "task_instruction.json").write_text(json.dumps({
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": "webarena_reddit_mock",
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": success,
    }, indent=2) + "\n")

    notes = [
        "Target derived, never named: the instruction states the ordering and "
        "the ordinal only. Winner %s; near miss %s." % (target, task["near_miss"]),
        "Tie margin: " + task["margin"],
        "Writeback: AppContext.vote() sets votes.submissions[\"%s\"] = %d and "
        "Vote.jsx renders the form class from that map. The rubric asserts the "
        "exact resulting ledger, so a destructive sweep of votes across the "
        "listing scores 0.0." % (target, direction),
        "Reddit submission titles are external links (Submission.jsx:120-126); "
        "the vote form renders on the listing row itself, so the replay votes "
        "from the listing and never clicks a title.",
        "start_path '/' -- the front page is an empty Featured-forums shell on "
        "the seed (0 subscriptions), and the route to the forum is the Forums "
        "nav link plus the numbered pagination on /forums.",
        "Difficulty medium: exactly two skills, R4 then A9.",
    ]

    (d / "task.json").write_text(json.dumps({
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
            "topic": "reddit ordinal selection in a forum listing, then a vote",
            "style": task["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R4", "A9"],
            "skill_chain": task["chain"],
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "injected_preconditions": injected,
            "hard_criteria": [],
            "inspiration_ids": task["insp"],
            "authoring_notes": notes,
        },
    }, indent=2) + "\n")

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
                "initial_setup": setup_src,
                "eval_reward_code": nemo,
            },
        }
    }
    (d / "nemo_task.json").write_text(json.dumps(row, indent=1) + "\n")
    return row


REPLAY = '''"""Golden replay DRAFT for {tid}.

Click-only from '/'. No page.goto after the initial landing.
Chain: Forums nav -> {forum} -> {route} -> {act} the derived row {target}.

Reddit submission titles are EXTERNAL links (Submission.jsx:120-126), so this
replay never clicks a title. The vote form renders on the listing row itself.
"""


def run(page, base_url):
    page.goto(base_url + "/")

    # 1. front page is an empty Featured-forums shell on the seed; the Forums
    #    index is the rendered route to any forum.
    page.click("nav a:has-text('Forums')")

    # 2. /forums is 25 rows a page with numbered OffsetPagination. f/{forum}
    #    sits on page {page_no} of the default by-submissions ordering; the
    #    by-name ordering in the Sort dropdown is an equally clickable route.
{pager}
    page.click("a[href='/f/{forum}']")

{sortnav}
    # 4. {act} the derived row. `.submission__vote form` is the vote widget;
    #    the {arrow} button is `button.vote__{arrowcls}`.
    row = page.locator("article.submission", has=page.locator(
        "a[href*='/f/{forum}/{target}/']")).first
    row.locator("button.vote__{arrowcls}").click()

    # the form class flips to 'vote vote--user-{cls}' and
    # votes.submissions["{target}"] becomes {direction}.
'''


def replay(task):
    tid = task["tid"]
    forum = task["forum"]
    target = task["target"]
    up = task["direction"] == 1
    pages = {"todayilearned": 1, "Hartford": 4, "monitor": 4, "nottheonion": 2,
             "Jokes": 1, "Showerthoughts": 1, "deeplearning": 4, "vermont": 3,
             "Music": 1, "wallstreetbets": 1}
    page_no = pages[forum]
    pager = ("" if page_no == 1
             else "    page.click(\"nav.pagination a[aria-label='Page %d']\")\n" % page_no)

    if "second-newest" in task["chain"] or "SECOND" in task["chain"]:
        route = "Sort: New, row 2"
        sortnav = ("    # 3. Sort dropdown -> New (id DESC). The target is the SECOND row.\n"
                   "    page.click(\"button[aria-label^='Sort by']\")\n"
                   "    page.click(\"a:has-text('New')\")\n\n")
    elif "ordered by New" in task["chain"]:
        route = "Sort: New, head row"
        sortnav = ("    # 3. Sort dropdown -> New (id DESC, listing.js:34).\n"
                   "    page.click(\"button[aria-label^='Sort by']\")\n"
                   "    page.click(\"a:has-text('New')\")\n\n")
    elif "one page" in task["chain"]:
        route = "all 6 rows on one page, read the datetime attributes"
        sortnav = ("    # 3. no sort needed: 6 rows fit one page. The oldest posting\n"
                   "    #    date is read from the <time> title/datetime attributes.\n\n")
    else:
        route = "Sort: Top, All time"
        sortnav = ("    # 3. Sort dropdown -> Top, then the time dropdown -> All time.\n"
                   "    page.click(\"button[aria-label^='Sort by']\")\n"
                   "    page.click(\"a:has-text('Top')\")\n"
                   "    page.click(\"button[aria-label^='Links from']\")\n"
                   "    page.click(\"a:has-text('All time')\")\n\n")

    src = REPLAY.format(
        tid=tid, forum=forum, route=route, target=target,
        act="upvote" if up else "downvote",
        arrow="up" if up else "down",
        arrowcls="up" if up else "down",
        cls="upvoted" if up else "downvoted",
        direction=1 if up else -1,
        page_no=page_no, pager=pager, sortnav=sortnav)
    (BATCH / "replays" / (tid + ".py")).write_text(src)


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    (BATCH / "replays").mkdir(parents=True, exist_ok=True)
    rows = []
    for task in TASKS:
        rows.append(build(task))
        replay(task)
    with (BATCH / "nemo_tasks.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    (BATCH / "index.json").write_text(json.dumps({
        "schema_version": 2,
        "tasks": [{"task_id": t["tid"], "path": t["tid"] + "/task.json"}
                  for t in TASKS],
    }, indent=2) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
