#!/usr/bin/env python3
"""Author-side emitter for batch-5 lane 17 (reddit / bulk_vote_author_in_forum).

Writes bundle files only. It runs no gate, no reward probe, no browser, and
imports nothing from cua_gym_web or cuagym. Its whole job is to keep
nemo_task.json byte-identical to the sibling nemo_reward.py / initial_setup.py,
which cannot be done reliably by hand.
"""

import json
import os
import re
import unicodedata

ROOT = "/home/ubuntu/CUA-Gym"
SEED = os.path.join(ROOT, "hub/websites/webarena_reddit_mock/src/data/submissions.json")
OUT = os.path.join(ROOT, "output/tasks/reddit")
BATCH = os.path.join(OUT, "_batches/bulk_vote_author_in_forum")
REPLAYS = os.path.join(BATCH, "replays")

APP = "webarena_reddit_mock"
ENV = "CUA_GYM_WEBARENA_REDDIT_URL"
ME = "MarvelsGrantMan136"
SEEDED_VOTE = {"1": 1}

SUBS = json.load(open(SEED))
BY_ID = {str(s["id"]): s for s in SUBS}


def pair(author, forum):
    rows = [s for s in SUBS if s["author"] == author and s["forum"] == forum]
    rows.sort(key=lambda s: s["id"])
    return rows


def slugify(title, max_length=60):
    words = [w for w in re.split(r"[^\w]+", title, flags=re.UNICODE) if w]
    words = [w.lower() for w in words]
    slug, ln = "", 0
    for w in words:
        add = ("-" + w) if ln > 0 else w
        ln += len(add)
        if ln > max_length:
            break
        slug += add
    return slug or "-"


# --------------------------------------------------------------------------
# matched sets
# --------------------------------------------------------------------------
GADGETS = [str(s["id"]) for s in pair("chrisdh79", "gadgets")]
UPLIFT = [str(s["id"]) for s in pair("Sariel007", "UpliftingNews")]
HISTORY = [str(s["id"]) for s in pair("marketrent", "history")]
SCIENCE = [str(s["id"]) for s in pair("giuliomagnifico", "science")]
SCIENCE_LOW = [i for i in SCIENCE if BY_ID[i]["netScore"] < 10]
GIFS = [str(s["id"]) for s in pair("lnfinity", "gifs")]
NEWS = [str(s["id"]) for s in pair("Hrekires", "news")]
IAMA = [str(s["id"]) for s in pair("UniversityofBath", "IAmA")]
PHIL = [str(s["id"]) for s in pair("IAI_Admin", "philosophy")]
GADGETS_HIGH = [i for i in GADGETS if BY_ID[i]["netScore"] > 3000]
GADGETS_LOW = [i for i in GADGETS if BY_ID[i]["netScore"] < 100]

NEWS_PRE_DOWN = ["43572", "43781", "129794", "129816"]

DISTRACTOR_TITLE = (
    "We’re the Institute for Mathematical Innovation at the University of "
    "Bath and we model epidemics — ask us anything!"
)
DISTRACTOR = {
    "id": 200000,
    "forum": "science",
    "author": "UniversityofBath",
    "title": DISTRACTOR_TITLE,
    "url": "https://www.bath.ac.uk/announcements/imi-epidemic-modelling-ama/",
    "timestamp": "2023-03-29T11:12:04+00:00",
    "lastActive": "2023-03-29T11:12:04+00:00",
    "ranking": 141,
    "netScore": 141,
    "commentCount": 9,
    "slug": slugify(DISTRACTOR_TITLE),
    "userFlag": "t3_1264ab3",
}


def expected(votes_map):
    out = dict(SEEDED_VOTE)
    out.update(votes_map)
    return out


def uniform(ids, choice):
    return {i: choice for i in ids}


# --------------------------------------------------------------------------
# reward source assembly
# --------------------------------------------------------------------------
HELPERS = '''
def _votes(state):
    """The agent's submission votes, as `{submission id: +1 | -1}`.

    `vote()` deletes a key when a vote is retracted, so an id that carries no
    value is simply absent. Anything that is not a plain +1/-1 integer is
    ignored rather than trusted.
    """
    votes = state.get("votes") if isinstance(state, dict) else None
    bucket = votes.get("submissions") if isinstance(votes, dict) else None
    out = {}
    if isinstance(bucket, dict):
        for key, value in bucket.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            num = int(value)
            if num in (1, -1):
                out[str(key)] = num
    return out


def _all_at(votes, ids, choice):
    return all(votes.get(str(i)) == choice for i in ids)


def _none_of(votes, ids):
    return all(str(i) not in votes for i in ids)


def _subscriptions(state):
    value = state.get("subscriptions") if isinstance(state, dict) else None
    if not isinstance(value, list):
        return []
    return sorted(str(v).strip().lower() for v in value if str(v).strip())
'''

MESSAGE_HELPER = '''
def _message_carries_count(state):
    """A private message from me to the target author whose only number is N.

    ComposeMessagePage stores a thread as
    `{id, participants: [sender, receiver], messages: [{id, sender, body, timestamp}]}`,
    so the receiver is read off `participants` and the body off the message row.
    Requiring every integer in the body to be N is what stops "I upvoted 100 of
    your 13 posts" from passing on a substring match.
    """
    threads = state.get("messages") if isinstance(state, dict) else None
    if not isinstance(threads, list):
        return False
    for thread in threads:
        if not isinstance(thread, dict):
            continue
        participants = thread.get("participants")
        names = []
        if isinstance(participants, list):
            names = [str(p).strip().lower() for p in participants]
        if MESSAGE_TO.lower() not in names:
            continue
        rows = thread.get("messages")
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get("sender") or "").strip() != ME:
                continue
            body = row.get("body")
            if not isinstance(body, str):
                continue
            numbers = [int(n) for n in re.findall(r"\\d+", body)]
            if numbers and set(numbers) == set([EXPECTED_COUNT]):
                return True
    return False
'''

LIVE_HELPER = '''
def _live_session(state):
    """True only for a real reddit session document.

    This rubric's headline accomplishment is a REMOVAL, and an absence is
    trivially true of an empty state -- so both components are first gated on
    markers that only a genuine episode carries:

      * the seed's own vote on submission 1, which this task never asks the
        agent to touch, so a correct run still has it; and
      * the /f/UpliftingNews forum row the matched set was scoped to.

    An empty or partial state has neither, so nothing pays.
    """
    if _votes(state).get("1") != 1:
        return False
    rows = state.get("forums") if isinstance(state, dict) else None
    if not isinstance(rows, list):
        return False
    for row in rows:
        if isinstance(row, dict) and str(row.get("name") or "").strip().lower() == FORUM.lower():
            return True
    return False
'''

EVALUATE = '''
def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    app = None
    if isinstance(apps, dict):
        for candidate in ("reddit", "webarena_reddit_mock"):
            found = apps.get(candidate)
            if isinstance(found, dict):
                app = found
                break
    state = app.get("current_state") if isinstance(app, dict) else None
    if not isinstance(state, dict):
        state = {}

    checks = score_checks(state)
    components = []
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        satisfied = bool(checks.get(name))
        earned = weight if satisfied else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": "%s -> %s | votes.submissions=%s" % (
                name, satisfied, json.dumps(_votes(state), sort_keys=True)
            ),
        })
    return {"score": round(total, 6), "components": components}
'''

NEMO_MAIN = '''
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
    for name, weight in COMPONENT_WEIGHTS.items():
        if checks.get(name):
            total += weight
    print("COMPONENTS: " + json.dumps(
        dict((k, bool(v)) for k, v in checks.items()), sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''


def pydict(mapping):
    body = ",\n".join('    "%s": %d' % (k, v) for k, v in mapping.items())
    return "{\n" + body + ",\n}"


def pylist(ids):
    body = ",\n".join('    "%s"' % i for i in ids)
    return "[\n" + body + ",\n]"


def weights_block(weights):
    body = ",\n".join('    "%s": %s' % (k, v) for k, v in weights.items())
    return "COMPONENT_WEIGHTS = {\n" + body + ",\n}\n"


def build_reward(task, nemo):
    """Assemble reward.py (nemo=False) or nemo_reward.py (nemo=True)."""
    doc = task["reward_doc"] if not nemo else task["nemo_doc"]
    parts = ['"""' + doc + '\n"""\n\n']
    imports = ["import json"]
    if task.get("needs_re"):
        imports.append("import re")
    if nemo:
        imports.append("import sys")
        imports.append("")
        imports.append("import requests")
    parts.append("\n".join(imports) + "\n\n")
    if nemo:
        parts.append('SID = "__CUA_GYM_SID__"\n')
        parts.append('BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"\n\n')
    parts.append('ME = "%s"\n' % ME)
    parts.append(task["constants"])
    parts.append("\n" + weights_block(task["weights"]))
    if not nemo:
        parts.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n")
    parts.append("\n" + HELPERS.lstrip("\n"))
    if task.get("needs_live"):
        parts.append("\n\n" + LIVE_HELPER.lstrip("\n"))
    if task.get("needs_re"):
        parts.append("\n\n" + MESSAGE_HELPER.lstrip("\n"))
    parts.append("\n\n" + task["score_checks"].lstrip("\n"))
    parts.append("\n\n" + (NEMO_MAIN if nemo else EVALUATE).lstrip("\n"))
    return "".join(parts)


SETUP_HEAD = '''"""{doc}
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

{fixtures}

def main():
    # Clear anything left on this sid, so the document being patched is always
    # the pristine `createInitialData()` baseline and a rerun cannot stack a
    # second injection on top of an already-seeded session.
    requests.post(BASE_URL + "/post?sid=" + SID, json={{"action": "reset"}}, timeout=60)

    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    state = probe.json().get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)
    if not isinstance(state.get("votes"), dict):
        print("SETUP FAILED: baseline carries no votes map", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
{patch}
    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial and current state disagree after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''


def vote_setup(doc, injected):
    fixtures = 'PRE_EXISTING_VOTES = json.loads(r"""%s""")\n' % json.dumps(
        injected, sort_keys=True
    )
    patch = """    votes = dict(state.get("votes") or {})
    submissions = dict(votes.get("submissions") or {})
    for key in PRE_EXISTING_VOTES:
        if key in submissions:
            print("SETUP FAILED: baseline already votes on " + key, file=sys.stderr)
            raise SystemExit(1)
    submissions.update(PRE_EXISTING_VOTES)
    votes["submissions"] = submissions
    state["votes"] = votes

"""
    return SETUP_HEAD.format(doc=doc, fixtures=fixtures, patch=patch)


def distractor_setup(doc):
    fixtures = (
        'DISTRACTOR = json.loads(r"""%s""")\n' % json.dumps(DISTRACTOR, sort_keys=True)
    )
    patch = """    created = list(state.get("newSubmissions") or [])
    if created:
        print("SETUP FAILED: baseline already carries created submissions", file=sys.stderr)
        raise SystemExit(1)
    created.append(DISTRACTOR)
    state["newSubmissions"] = created
    state["nextSubmissionId"] = max(
        int(state.get("nextSubmissionId") or 200000), int(DISTRACTOR["id"]) + 1
    )
    forums = []
    for row in state.get("forums") or []:
        row = dict(row)
        if str(row.get("name")).lower() == str(DISTRACTOR["forum"]).lower():
            row["submissionCount"] = int(row.get("submissionCount") or 0) + 1
        forums.append(row)
    state["forums"] = forums

"""
    return SETUP_HEAD.format(doc=doc, fixtures=fixtures, patch=patch)


# --------------------------------------------------------------------------
# task definitions
# --------------------------------------------------------------------------
TASKS = []


def add(**kw):
    TASKS.append(kw)


def const_block(**named):
    lines = []
    for key, value in named.items():
        if isinstance(value, dict):
            lines.append("%s = %s\n" % (key, pydict(value)))
        elif isinstance(value, list):
            lines.append("%s = %s\n" % (key, pylist(value)))
        elif isinstance(value, str):
            lines.append('%s = "%s"\n' % (key, value))
        else:
            lines.append("%s = %r\n" % (key, value))
    return "".join(lines)


TWO_COMPONENT = """
def score_checks(state):
    votes = _votes(state)
    return {
        "%(a)s": _all_at(votes, MATCHED_IDS, %(choice)d),
        "%(b)s": votes == EXPECTED_VOTES,
    }
"""


def two_component_task(name_a, choice):
    return TWO_COMPONENT % {
        "a": name_a,
        "b": "vote_map_is_exactly_the_matched_set",
        "choice": choice,
    }


# ---- 001 -----------------------------------------------------------------
add(
    task_id="bulk_vote_author_in_forum_chrisdh79_gadgets_upvote_001",
    instruction=(
        "chrisdh79 is my favourite source in /f/gadgets. Upvote every "
        "submission chrisdh79 has posted in that forum."
    ),
    difficulty="medium",
    style="terse",
    shape="bulk_mutation",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope the /f/gadgets listing (or chrisdh79's own submissions page) to "
        "chrisdh79 -> that scoped set is the matched set -> click the upvote "
        "arrow on every row of it"
    ),
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "Like all submissions created by Don_Gato1 in forum nyc",
    ],
    constants=const_block(
        MATCHED_IDS=GADGETS, EXPECTED_VOTES=expected(uniform(GADGETS, 1))
    ),
    weights={"all_matched_submissions_upvoted": 0.7,
             "vote_map_is_exactly_the_matched_set": 0.3},
    score_checks=two_component_task("all_matched_submissions_upvoted", 1),
    criteria=[
        "votes.submissions records +1 for each of the 19 chrisdh79 submissions "
        "filed in /f/gadgets (ids " + ", ".join(GADGETS) + ").",
        "votes.submissions is exactly those 19 ids at +1 plus the seeded vote "
        "on submission 1, so no other submission carries a vote.",
    ],
    notes=[
        "19 chrisdh79 submissions in /f/gadgets, counted over the frozen seed "
        "corpus; chrisdh79 has 20 more submissions in other forums, so the "
        "forum scope is load-bearing.",
        "Voting changes netScore and therefore hot/top order, but the matched "
        "set is selected by author, which no vote disturbs.",
    ],
)

# ---- 002 -----------------------------------------------------------------
SCORE_002 = """
def score_checks(state):
    votes = _votes(state)
    return {
        "all_matched_submissions_upvoted": _all_at(votes, MATCHED_IDS, 1),
        "vote_map_is_exactly_the_matched_set": votes == EXPECTED_VOTES,
        "subscriptions_are_now_exactly_upliftingnews":
            _subscriptions(state) == [FORUM.lower()],
    }
"""
add(
    task_id="bulk_vote_author_in_forum_sariel007_upliftingnews_subscribe_002",
    instruction=(
        "Sariel007's UpliftingNews posts are consistently good news. Upvote "
        "every submission Sariel007 has posted in /f/UpliftingNews, and "
        "subscribe to that forum."
    ),
    difficulty="medium",
    style="terse",
    shape="bulk_mutation",
    skills=["R5", "A4", "A9", "A3"],
    skill_chain=(
        "scope /f/UpliftingNews to Sariel007 -> upvote every row of that "
        "matched set -> subscribe to the forum the set was scoped to"
    ),
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        'Subscribe to the "books" forum from the page of the all time top post in that forum.',
    ],
    constants=const_block(
        FORUM="UpliftingNews",
        MATCHED_IDS=UPLIFT,
        EXPECTED_VOTES=expected(uniform(UPLIFT, 1)),
    ),
    weights={"all_matched_submissions_upvoted": 0.45,
             "vote_map_is_exactly_the_matched_set": 0.25,
             "subscriptions_are_now_exactly_upliftingnews": 0.3},
    score_checks=SCORE_002,
    criteria=[
        "votes.submissions records +1 for each of the 16 Sariel007 submissions "
        "in /f/UpliftingNews (ids " + ", ".join(UPLIFT) + ").",
        "votes.submissions is exactly those 16 ids at +1 plus the seeded vote "
        "on submission 1.",
        "subscriptions is exactly [\"UpliftingNews\"].",
    ],
    notes=[
        "Sariel007 has 22 submissions site-wide and 16 of them are in "
        "UpliftingNews, so the forum scope decides six rows.",
        "subscribe() also increments forums[].subscriberCount; the rubric "
        "gates on the subscriptions list, which is what the sidebar renders.",
    ],
)

# ---- 003 -----------------------------------------------------------------
add(
    task_id="bulk_vote_author_in_forum_marketrent_history_downvote_003",
    instruction=(
        "marketrent keeps filling /f/history with the same recycled links. "
        "Downvote every submission marketrent has posted in that forum."
    ),
    difficulty="medium",
    style="terse",
    shape="bulk_mutation",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope the /f/history listing to marketrent -> that scoped set is the "
        "matched set -> click the downvote arrow on every row of it"
    ),
    analogues=[
        "DisLike all submissions created by RickyDontLoseThat in forum massachusetts",
        "DisLike all submissions created by AdamCannon in forum UpliftingNews",
    ],
    constants=const_block(
        MATCHED_IDS=HISTORY, EXPECTED_VOTES=expected(uniform(HISTORY, -1))
    ),
    weights={"all_matched_submissions_downvoted": 0.7,
             "vote_map_is_exactly_the_matched_set": 0.3},
    score_checks=two_component_task("all_matched_submissions_downvoted", -1),
    criteria=[
        "votes.submissions records -1 for each of the 14 marketrent "
        "submissions in /f/history (ids " + ", ".join(HISTORY) + ").",
        "votes.submissions is exactly those 14 ids at -1 plus the seeded vote "
        "on submission 1.",
    ],
    notes=[
        "marketrent has 28 submissions site-wide, 14 of them in history.",
        "Downvoting drops netScore by 1 per row; nothing in the selection "
        "predicate reads netScore, so the premise survives the action.",
    ],
)

# ---- 004 -----------------------------------------------------------------
SCORE_004 = """
def score_checks(state):
    votes = _votes(state)
    return {
        "low_scoring_science_submissions_upvoted": _all_at(votes, MATCHED_IDS, 1),
        "vote_map_is_exactly_the_matched_set": votes == EXPECTED_VOTES,
    }
"""
add(
    task_id="bulk_vote_author_in_forum_giuliomagnifico_science_low_score_004",
    instruction=(
        "giuliomagnifico's quieter science write-ups deserve a nudge. In "
        "/f/science, upvote every submission by giuliomagnifico that currently "
        "sits under 10 points."
    ),
    difficulty="hard",
    style="terse",
    shape="retrieval_writeback",
    skills=["R5", "R3", "A4", "A9"],
    skill_chain=(
        "scope /f/science to giuliomagnifico -> filter that set by the score "
        "shown on each row (under 10 points) -> upvote every row that survives "
        "the filter"
    ),
    hard_criteria=["derived_target", "multi_mutation"],
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "Thumbs down the top 1 post ever in gadgets.",
    ],
    constants=const_block(
        MATCHED_IDS=SCIENCE_LOW, EXPECTED_VOTES=expected(uniform(SCIENCE_LOW, 1))
    ),
    weights={"low_scoring_science_submissions_upvoted": 0.6,
             "vote_map_is_exactly_the_matched_set": 0.4},
    score_checks=SCORE_004,
    criteria=[
        "votes.submissions records +1 for each giuliomagnifico submission in "
        "/f/science scoring under 10 (ids " + ", ".join(SCIENCE_LOW) + ").",
        "votes.submissions is exactly those 7 ids at +1 plus the seeded vote "
        "on submission 1, so the seven high-scoring giuliomagnifico science "
        "posts carry no vote.",
    ],
    notes=[
        "14 giuliomagnifico submissions in science; 7 score under 10 "
        "(0, 2, 3, 4, 4, 5, 5) and the other 7 score 3026 or more, so the "
        "threshold has a margin of 3021 and no row is ambiguous.",
        "Action-vs-premise: an upvote lifts each matched row by exactly 1, so "
        "the highest matched row moves 5 -> 6 and stays under 10; the "
        "predicate that selected the set is still true afterwards.",
    ],
)

# ---- 005 -----------------------------------------------------------------
SCORE_005 = """
def score_checks(state):
    votes = _votes(state)
    return {
        "all_gifs_submissions_by_lnfinity_upvoted": _all_at(votes, MATCHED_IDS, 1),
        "vote_map_is_exactly_the_matched_set": votes == EXPECTED_VOTES,
        "message_to_lnfinity_carries_the_count": _message_carries_count(state),
    }
"""
add(
    task_id="bulk_vote_author_in_forum_lnfinity_gifs_upvote_and_dm_005",
    instruction=(
        "Upvote every submission lnfinity has posted in /f/gifs, then message "
        "lnfinity to tell them how many of their gif posts you just upvoted. "
        "Give the count as a numeral."
    ),
    difficulty="hard",
    style="terse",
    shape="retrieval_writeback",
    skills=["R5", "R3", "A4", "A9", "A7"],
    skill_chain=(
        "scope /f/gifs to lnfinity -> upvote every row of that matched set -> "
        "count the same set -> carry the count into a private message to its "
        "author"
    ),
    hard_criteria=["derived_target", "multi_mutation"],
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "Tell me the count of comments that have received more downvotes than "
        "upvotes for the user who made the latest post on the DIY forum.",
    ],
    constants=const_block(
        MESSAGE_TO="lnfinity",
        EXPECTED_COUNT=len(GIFS),
        MATCHED_IDS=GIFS,
        EXPECTED_VOTES=expected(uniform(GIFS, 1)),
    ),
    needs_re=True,
    weights={"all_gifs_submissions_by_lnfinity_upvoted": 0.35,
             "vote_map_is_exactly_the_matched_set": 0.25,
             "message_to_lnfinity_carries_the_count": 0.4},
    score_checks=SCORE_005,
    criteria=[
        "votes.submissions records +1 for each of the 13 lnfinity submissions "
        "in /f/gifs (ids " + ", ".join(GIFS) + ").",
        "votes.submissions is exactly those 13 ids at +1 plus the seeded vote "
        "on submission 1.",
        "messages holds a thread whose participants include lnfinity, "
        "carrying a message sent by MarvelsGrantMan136 whose body contains the "
        "numeral 13 and no other number.",
    ],
    notes=[
        "lnfinity has 16 submissions site-wide and 13 in gifs, so the count "
        "written into the message is only correct if the forum scope was "
        "applied - the instruction never states it.",
        "ComposeMessagePage.jsx writes messages[] threads as "
        "{id, participants, messages:[{id, sender, body, timestamp}]}; the "
        "rubric reads exactly those fields.",
    ],
)

# ---- 006 -----------------------------------------------------------------
add(
    task_id="bulk_vote_author_in_forum_hrekires_news_flip_downvotes_006",
    instruction=(
        "I was too harsh on Hrekires. Every submission they have posted in "
        "/f/news should end up upvoted by me, including the ones I already "
        "downvoted."
    ),
    difficulty="medium",
    style="terse",
    shape="bulk_mutation",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope /f/news to Hrekires -> that scoped set is the matched set -> "
        "leave every row of it at an upvote, flipping the rows that already "
        "carry my downvote"
    ),
    analogues=[
        "Like all submissions created by Hrekires in forum news",
        "DisLike all submissions created by Hrekires in forum news",
    ],
    constants=const_block(
        MATCHED_IDS=NEWS, EXPECTED_VOTES=expected(uniform(NEWS, 1))
    ),
    weights={"all_matched_submissions_upvoted": 0.7,
             "vote_map_is_exactly_the_matched_set": 0.3},
    score_checks=two_component_task("all_matched_submissions_upvoted", 1),
    setup=vote_setup(
        "NeMo-Gym setup program for "
        "bulk_vote_author_in_forum_hrekires_news_flip_downvotes_006.\n\n"
        "Plants four pre-existing downvotes on Hrekires submissions in /f/news "
        "(43572, 43781, 129794, 129816). Without them the task is a plain "
        "bulk upvote over a clean slate; with them four of the ten rows render "
        "as `vote vote--user-downvoted` and have to be flipped rather than "
        "simply clicked, which is a different observation for the agent and a "
        "different starting map for the rubric.\n\n"
        "All four still score at least 2 after the injected downvote, so no "
        "row is pushed negative - the live corpus contains no negatively "
        "scored submission and this keeps the state inside that envelope.\n\n"
        "The pristine baseline is read back from the state API and the whole "
        "document is republished with the set action, so the episode baseline "
        "is a complete state object rather than a partial one.\n\n"
        "Self-contained: standard library plus requests.",
        {i: -1 for i in NEWS_PRE_DOWN},
    ),
    injected=[
        "votes.submissions: {\"43572\": -1, \"43781\": -1, \"129794\": -1, "
        "\"129816\": -1} - four of the ten Hrekires /f/news submissions start "
        "carrying my downvote, so the correct run has to flip them, not just "
        "add votes. None of the four is pre-set to the +1 the rubric pays for.",
    ],
    criteria=[
        "votes.submissions records +1 for each of the 10 Hrekires submissions "
        "in /f/news (ids " + ", ".join(NEWS) + "), including the four that "
        "started at -1.",
        "votes.submissions is exactly those 10 ids at +1 plus the seeded vote "
        "on submission 1.",
    ],
    notes=[
        "Hrekires has exactly 10 submissions site-wide and all 10 are in news, "
        "so /user/Hrekires/submissions is a single page and the forum scope is "
        "trivially satisfied - the difficulty here is the flip, not the scope.",
        "vote() maps old=-1, choice=+1 to next=+1 in one click, so a flip is a "
        "single press of the up arrow.",
    ],
)

# ---- 007 -----------------------------------------------------------------
add(
    task_id="bulk_vote_author_in_forum_universityofbath_iama_scoped_007",
    instruction=(
        "UniversityofBath runs the AMAs I actually read. Upvote every "
        "submission UniversityofBath has posted in /f/IAmA, and only the ones "
        "filed in that forum."
    ),
    difficulty="medium",
    style="terse",
    shape="retrieval_writeback",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope UniversityofBath's submissions to /f/IAmA -> that scoped set is "
        "the matched set -> upvote every row of it and nothing else"
    ),
    analogues=[
        "Like all submissions created by UniversityofBath in forum IAmA",
        "Like all submissions created by CameronKelsey in forum earthporn",
    ],
    constants=const_block(
        MATCHED_IDS=IAMA, EXPECTED_VOTES=expected(uniform(IAMA, 1))
    ),
    weights={"all_matched_submissions_upvoted": 0.7,
             "vote_map_is_exactly_the_matched_set": 0.3},
    score_checks=two_component_task("all_matched_submissions_upvoted", 1),
    setup=distractor_setup(
        "NeMo-Gym setup program for "
        "bulk_vote_author_in_forum_universityofbath_iama_scoped_007.\n\n"
        "Plants one near-miss submission: a UniversityofBath post filed in "
        "/f/science rather than /f/IAmA. On the pristine seed all eight of "
        "this author's submissions are in IAmA, so the forum scope in the "
        "instruction costs nothing and the task degenerates into 'upvote this "
        "author'. With the distractor present the agent must actually apply "
        "the forum predicate.\n\n"
        "Placement obeys the ordering of the page the distractor has to be "
        "visible on: /user/UniversityofBath/submissions sorts id DESC "
        "(components/user/userPaging.js), and id 200000 is above every seeded "
        "id, so the record lands at the top of page one rather than off the "
        "end of it.\n\n"
        "The record carries every field createSubmission writes plus the url "
        "and userFlag the frozen corpus uses, forums[science].submissionCount "
        "is incremented the way the handler increments it, and "
        "nextSubmissionId is advanced past the injected id. No vote is "
        "recorded for it, because the author is not the current user.\n\n"
        "Self-contained: standard library plus requests."
    ),
    injected=[
        "newSubmissions: one full submission record (id 200000) authored by "
        "UniversityofBath in /f/science - a distractor that satisfies the "
        "author half of the filter and fails the forum half. It sits at the "
        "top of /user/UniversityofBath/submissions because that page sorts id "
        "DESC.",
        "forums[science].submissionCount incremented by 1 and nextSubmissionId "
        "advanced to 200001, mirroring what createSubmission writes alongside "
        "a new post.",
    ],
    criteria=[
        "votes.submissions records +1 for each of the 8 UniversityofBath "
        "submissions in /f/IAmA (ids " + ", ".join(IAMA) + ").",
        "votes.submissions is exactly those 8 ids at +1 plus the seeded vote "
        "on submission 1, so the injected /f/science submission by the same "
        "author carries no vote.",
    ],
    notes=[
        "The injected record is the only thing separating this from a plain "
        "author-wide upvote; the rubric's exact-map component is what makes "
        "the distractor cost something.",
    ],
)

# ---- 008 -----------------------------------------------------------------
add(
    task_id="bulk_vote_author_in_forum_iai_admin_philosophy_paged_008",
    instruction=(
        "IAI_Admin is by far the most prolific poster in /f/philosophy and I "
        "want to back the whole run. Work through the forum, or through "
        "IAI_Admin's own submissions listing, and upvote every single "
        "submission IAI_Admin has filed in /f/philosophy. There are more of "
        "them than fit on one listing page, so keep following the pager until "
        "you have covered all of them. Submissions by other authors in "
        "/f/philosophy are not part of this, and neither is anything outside "
        "that forum."
    ),
    difficulty="medium",
    style="explicit",
    shape="bulk_mutation",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope /f/philosophy to IAI_Admin, paging past the 25-row listing "
        "boundary -> that scoped set is the matched set -> upvote every row of "
        "it"
    ),
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "Like all submissions created by Don_Gato1 in forum nyc",
    ],
    constants=const_block(
        MATCHED_IDS=PHIL, EXPECTED_VOTES=expected(uniform(PHIL, 1))
    ),
    weights={"all_matched_submissions_upvoted": 0.7,
             "vote_map_is_exactly_the_matched_set": 0.3},
    score_checks=two_component_task("all_matched_submissions_upvoted", 1),
    criteria=[
        "votes.submissions records +1 for each of the 27 IAI_Admin "
        "submissions in /f/philosophy (ids " + ", ".join(PHIL) + ").",
        "votes.submissions is exactly those 27 ids at +1 plus the seeded vote "
        "on submission 1.",
    ],
    notes=[
        "All 27 IAI_Admin submissions are in philosophy, and every listing on "
        "the site pages at 25 (utils/listing.js PER_PAGE, "
        "components/user/userPaging.js), so this set is the one in the lane "
        "that genuinely crosses a page boundary. The explicit style is used so "
        "the paging requirement is stated rather than left as a trap.",
    ],
)

# ---- 009 -----------------------------------------------------------------
SCORE_009 = """
def score_checks(state):
    votes = _votes(state)
    return {
        "high_scoring_gadget_posts_upvoted": _all_at(votes, UPVOTE_IDS, 1),
        "low_scoring_gadget_posts_downvoted": _all_at(votes, DOWNVOTE_IDS, -1),
        "vote_map_is_exactly_the_two_matched_sets": votes == EXPECTED_VOTES,
    }
"""
EXPECTED_009 = expected(
    dict(list(uniform(GADGETS_HIGH, 1).items()) + list(uniform(GADGETS_LOW, -1).items()))
)
add(
    task_id="bulk_vote_author_in_forum_chrisdh79_gadgets_split_009",
    instruction=(
        "I am tidying up how I have voted on chrisdh79's gadget posts. Inside "
        "/f/gadgets only, upvote every submission of theirs that currently "
        "shows more than 3000 points, and downvote every submission of theirs "
        "that currently shows fewer than 100 points. The chrisdh79 posts whose "
        "scores fall between those two thresholds should end up with no vote "
        "from me at all, and posts by other authors, or by chrisdh79 in other "
        "forums, are outside the scope of this."
    ),
    difficulty="hard",
    style="explicit",
    shape="retrieval_writeback",
    skills=["R5", "R3", "A4", "A9"],
    skill_chain=(
        "scope /f/gadgets to chrisdh79 -> split that set by the score on each "
        "row into an above-3000 band and a below-100 band -> apply the upvote "
        "arrow to the first band and the downvote arrow to the second"
    ),
    hard_criteria=["derived_target", "multi_mutation"],
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "DisLike all submissions created by PatientBuilder499 in forum videos",
    ],
    constants=const_block(
        UPVOTE_IDS=GADGETS_HIGH,
        DOWNVOTE_IDS=GADGETS_LOW,
        EXPECTED_VOTES=EXPECTED_009,
    ),
    weights={"high_scoring_gadget_posts_upvoted": 0.35,
             "low_scoring_gadget_posts_downvoted": 0.35,
             "vote_map_is_exactly_the_two_matched_sets": 0.3},
    score_checks=SCORE_009,
    criteria=[
        "votes.submissions records +1 for each chrisdh79 /f/gadgets submission "
        "scoring above 3000 (ids " + ", ".join(GADGETS_HIGH) + ").",
        "votes.submissions records -1 for each chrisdh79 /f/gadgets submission "
        "scoring below 100 (ids " + ", ".join(GADGETS_LOW) + ").",
        "votes.submissions is exactly those two bands plus the seeded vote on "
        "submission 1, so the seven mid-band chrisdh79 gadget posts carry no "
        "vote.",
    ],
    notes=[
        "Bands over the 19 chrisdh79 gadgets rows: above 3000 is "
        "7666/6758/4359/4280/3382/3174/3092 (7 rows, nearest excluded row "
        "2019, margin 1073); below 100 is 52/2/0/0/0 (5 rows, nearest excluded "
        "row 167, margin 115). Seven rows sit in the untouched middle.",
        "Action-vs-premise: +1 on 3092 keeps it above 3000 and -1 on 52 keeps "
        "it below 100, so neither band's own action moves a row across its own "
        "threshold.",
    ],
)

# ---- 010 -----------------------------------------------------------------
SCORE_010 = """
def score_checks(state):
    votes = _votes(state)
    # Both components are gated on _live_session: a retraction is scored by
    # absence, and absence is free on an empty state (TASK4 S9.5).
    live = _live_session(state)
    return {
        "upvotes_on_sariel007_upliftingnews_posts_cleared":
            live and _none_of(votes, MATCHED_IDS),
        "vote_map_is_exactly_the_seeded_single_vote":
            live and votes == EXPECTED_VOTES,
    }
"""
add(
    task_id="bulk_vote_author_in_forum_sariel007_upliftingnews_retract_010",
    instruction=(
        "I over-committed to Sariel007. Clear the upvotes I left on every "
        "submission they have posted in /f/UpliftingNews."
    ),
    difficulty="medium",
    style="terse",
    shape="retrieval_writeback",
    skills=["R5", "A4", "A9"],
    skill_chain=(
        "scope /f/UpliftingNews to Sariel007 -> that scoped set is the matched "
        "set -> retract my vote on every row of it by pressing the arrow that "
        "is already active"
    ),
    analogues=[
        "Like all submissions created by ThetaGang_wsb in forum wallstreetbets",
        "DisLike all submissions created by AdamCannon in forum UpliftingNews",
    ],
    constants=const_block(
        FORUM="UpliftingNews",
        MATCHED_IDS=UPLIFT,
        EXPECTED_VOTES=dict(SEEDED_VOTE),
    ),
    needs_live=True,
    weights={"upvotes_on_sariel007_upliftingnews_posts_cleared": 0.7,
             "vote_map_is_exactly_the_seeded_single_vote": 0.3},
    score_checks=SCORE_010,
    setup=vote_setup(
        "NeMo-Gym setup program for "
        "bulk_vote_author_in_forum_sariel007_upliftingnews_retract_010.\n\n"
        "Plants an upvote on all sixteen Sariel007 submissions in "
        "/f/UpliftingNews. Nothing in the app ever produces this state on its "
        "own, and it is what turns the lane's bulk-vote chain into a bulk "
        "retraction: every matched row renders with its up arrow already "
        "active, and the correct action is to press that same arrow again so "
        "vote() maps old=+1, choice=+1 to next=0 and deletes the entry.\n\n"
        "It cannot pre-satisfy the rubric: the rubric pays only when those "
        "sixteen ids are absent from votes.submissions, and the injection is "
        "exactly the state where all sixteen are present.\n\n"
        "The pristine baseline is read back from the state API and the whole "
        "document is republished with the set action, so the episode baseline "
        "is a complete state object rather than a partial one.\n\n"
        "Self-contained: standard library plus requests.",
        {i: 1 for i in UPLIFT},
    ),
    injected=[
        "votes.submissions: +1 on all sixteen Sariel007 submissions in "
        "/f/UpliftingNews (" + ", ".join(UPLIFT) + "). Nothing in the app "
        "writes this state, so the retraction chain is unreachable without it; "
        "it is the exact inverse of what the rubric pays for.",
    ],
    criteria=[
        "None of the 16 Sariel007 /f/UpliftingNews submissions (ids "
        + ", ".join(UPLIFT) + ") appears in votes.submissions any more.",
        "votes.submissions is exactly {\"1\": 1} - the one vote the seed "
        "ships - so no other submission gained or lost a vote.",
    ],
    notes=[
        "Retraction is the one vote transition the seed cannot reach without "
        "an injection, and it is a real errand: undoing a batch of votes.",
        "Injecting votes without a matching submissionEdits netScore bump "
        "leaves the displayed score unchanged. That is unobservable to the "
        "agent - a seeded netScore already folds in the corpus's own votes, so "
        "there is no rendered figure the agent could compare against.",
    ],
)


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------
def reward_doc(task, nemo):
    lines = [
        "%s reward for %s."
        % ("NeMo-Gym" if nemo else "Deterministic", task["task_id"]),
        "",
        "Skill chain: %s." % task["skill_chain"],
        "",
        "Scored strictly off the live session state's current view: every "
        "component compares a recorded vote value against a frozen table of "
        "ids computed from the seeded corpus. Nothing is diffed against a "
        "baseline, because a retracted vote leaves the diff entirely.",
        "",
        "No component pays for a record merely having been touched: vote() "
        "writes unconditionally, so each check reads the value that ended up "
        "in votes.submissions.",
    ]
    if nemo:
        lines += [
            "",
            "Same rubric as reward.py, reading current state from GET /go "
            "instead of a frozen evidence bundle, and printing REWARD: <float> "
            "on every output path including the error path.",
            "",
            "Self-contained: standard library plus requests.",
        ]
    out = []
    for entry in lines:
        if entry:
            out.extend(_wrap(entry))
        else:
            out.append("")
    return "\n".join(out)


def _wrap(paragraph, width=78):
    words = paragraph.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def replay_draft(task):
    body = [
        "# Golden replay DRAFT for %s" % task["task_id"],
        "#",
        "# Click-only: start at '/', reach the forum through the Forums index",
        "# (or an author byline), and operate the rendered vote forms. No",
        "# page.goto() after the initial landing, no constructed URLs.",
        "#",
        "# Intent: %s" % task["instruction"],
        "#",
        "# Steps:",
        "#   1. Land on '/'.",
        "#   2. Click 'Forums' in the site nav.",
    ]
    body += ["#   3. %s" % line for line in task["replay_steps"]]
    body.append("")
    body.append("# The vote control is `div.submission__vote form` on every")
    body.append("# listing row; 25 of them render per page.")
    body.append("")
    return "\n".join(body) + "\n"


REPLAY_STEPS = {
    "bulk_vote_author_in_forum_chrisdh79_gadgets_upvote_001": [
        "Page the forums index until the 'gadgets' card is visible and click it.",
        "Click a chrisdh79 byline to open /user/chrisdh79/submissions.",
        "For each row whose forum chip reads 'gadgets', click its up arrow.",
        "Follow the 'More' pager to page 2 and repeat.",
        "Expect 19 rows voted; votes.submissions gains 19 entries at +1.",
    ],
    "bulk_vote_author_in_forum_sariel007_upliftingnews_subscribe_002": [
        "Open the 'UpliftingNews' forum from the forums index.",
        "Click the sidebar 'Subscribe' button.",
        "Click a Sariel007 byline to open their submissions listing.",
        "Click the up arrow on every row whose forum chip reads 'UpliftingNews'.",
        "Expect 16 votes at +1 and subscriptions == ['UpliftingNews'].",
    ],
    "bulk_vote_author_in_forum_marketrent_history_downvote_003": [
        "Open the 'history' forum from the forums index.",
        "Click a marketrent byline to open their submissions listing.",
        "Click the down arrow on every row whose forum chip reads 'history'.",
        "Expect 14 votes at -1.",
    ],
    "bulk_vote_author_in_forum_giuliomagnifico_science_low_score_004": [
        "Open the 'science' forum from the forums index.",
        "Click a giuliomagnifico byline to open their submissions listing.",
        "Read the point count rendered on each row filed in 'science'.",
        "Click the up arrow only on the rows showing fewer than 10 points.",
        "Expect 7 votes at +1 and the seven 3000+ rows left unvoted.",
    ],
    "bulk_vote_author_in_forum_lnfinity_gifs_upvote_and_dm_005": [
        "Open the 'gifs' forum from the forums index.",
        "Click an lnfinity byline to open their submissions listing.",
        "Click the up arrow on every row whose forum chip reads 'gifs'; count them.",
        "Click 'Send message' in the profile sidebar.",
        "Type a body containing the numeral 13 and no other number; click Send.",
    ],
    "bulk_vote_author_in_forum_hrekires_news_flip_downvotes_006": [
        "Open the 'news' forum from the forums index.",
        "Click a Hrekires byline to open their submissions listing (10 rows, one page).",
        "Click the up arrow on every row, including the four rendering as",
        "   'vote vote--user-downvoted'.",
        "Expect all 10 entries at +1.",
    ],
    "bulk_vote_author_in_forum_universityofbath_iama_scoped_007": [
        "Open the 'IAmA' forum from the forums index.",
        "Click a UniversityofBath byline to open their submissions listing.",
        "Skip the top row, which is filed in 'science', and up-arrow the 8",
        "   rows whose forum chip reads 'IAmA'.",
        "Expect 8 votes at +1 and no vote on id 200000.",
    ],
    "bulk_vote_author_in_forum_iai_admin_philosophy_paged_008": [
        "Open the 'philosophy' forum from the forums index.",
        "Click an IAI_Admin byline to open their submissions listing.",
        "Up-arrow all 25 rows on page 1, click 'More', up-arrow the last 2.",
        "Expect 27 votes at +1.",
    ],
    "bulk_vote_author_in_forum_chrisdh79_gadgets_split_009": [
        "Open the 'gadgets' forum from the forums index.",
        "Click a chrisdh79 byline to open their submissions listing.",
        "For rows filed in 'gadgets': up-arrow those above 3000 points,",
        "   down-arrow those below 100 points, leave the rest alone.",
        "Follow the pager to page 2 and repeat.",
        "Expect 7 entries at +1 and 5 at -1.",
    ],
    "bulk_vote_author_in_forum_sariel007_upliftingnews_retract_010": [
        "Open the 'UpliftingNews' forum from the forums index.",
        "Click a Sariel007 byline to open their submissions listing.",
        "For each row filed in 'UpliftingNews' whose up arrow already renders",
        "   as active, click that same arrow again to retract.",
        "Expect votes.submissions to be exactly {'1': 1}.",
    ],
}

for task in TASKS:
    task["replay_steps"] = REPLAY_STEPS[task["task_id"]]
    task["reward_doc"] = reward_doc(task, False)
    task["nemo_doc"] = reward_doc(task, True)

for task in TASKS:
    tid = task["task_id"]
    bundle = os.path.join(OUT, tid)

    reward = build_reward(task, False)
    nemo_reward = build_reward(task, True)
    setup = task.get("setup")

    write(os.path.join(bundle, "reward.py"), reward)
    write(os.path.join(bundle, "nemo_reward.py"), nemo_reward)
    if setup:
        write(os.path.join(bundle, "initial_setup.py"), setup)

    instruction = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": APP,
        "start_path": "/",
        "difficulty": task["difficulty"],
        "success_criteria": task["criteria"],
    }
    write(
        os.path.join(bundle, "task_instruction.json"),
        json.dumps(instruction, indent=2, ensure_ascii=False) + "\n",
    )

    metadata = {
        "style": task["style"],
        "difficulty": task["difficulty"],
        "shape": task["shape"],
        "skills": task["skills"],
        "skill_chain": task["skill_chain"],
        "official_analogues": task["analogues"],
        "topic": "bulk_vote_author_in_forum",
        "lane": 17,
        "inspiration_ids": ["webarena-reddit-023..032"],
        "authoring_notes": task["notes"]
        + [
            "Grounded in webarena_reddit_mock @ hub/websites/webarena_reddit_mock; "
            "matched-set ids were computed over src/data/submissions.json.",
            "vote() is src/context/AppContext.jsx:321 - it writes "
            "votes.submissions[id] and patches netScore into the overlay; the "
            "rubric reads only the vote map.",
            "Both reward programs read the current state view only.",
        ],
    }
    if task.get("hard_criteria"):
        metadata["hard_criteria"] = task["hard_criteria"]
    if task.get("injected"):
        metadata["injected_preconditions"] = task["injected"]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [
            {
                "name": APP,
                "source_name": "reddit",
                "base_url_env": ENV,
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
    write(
        os.path.join(bundle, "task.json"),
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused — CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP,
                "initial_setup": setup,
                "eval_reward_code": nemo_reward,
            },
        }
    }
    write(
        os.path.join(bundle, "nemo_task.json"),
        json.dumps(row, indent=2, ensure_ascii=False) + "\n",
    )

    write(os.path.join(REPLAYS, tid + ".py"), replay_draft(task))

index = {
    "schema_version": 2,
    "tasks": [{"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]}
              for t in TASKS],
}
write(os.path.join(BATCH, "index.json"), json.dumps(index, indent=2) + "\n")

with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w", encoding="utf-8") as handle:
    for task in TASKS:
        path = os.path.join(OUT, task["task_id"], "nemo_task.json")
        handle.write(json.dumps(json.load(open(path)), ensure_ascii=False) + "\n")

print("wrote %d bundles" % len(TASKS))
for t in TASKS:
    words = len(t["instruction"].split())
    print("  %-62s %-8s %-8s %-22s %2dw%s" % (
        t["task_id"], t["difficulty"], t["style"], t["shape"], words,
        "  +setup" if t.get("setup") else ""))
print("matched set sizes:",
      {"gadgets": len(GADGETS), "uplift": len(UPLIFT), "history": len(HISTORY),
       "science_low": len(SCIENCE_LOW), "gifs": len(GIFS), "news": len(NEWS),
       "iama": len(IAMA), "phil": len(PHIL),
       "gadgets_high": len(GADGETS_HIGH), "gadgets_low": len(GADGETS_LOW)})
print("distractor slug:", DISTRACTOR["slug"])
