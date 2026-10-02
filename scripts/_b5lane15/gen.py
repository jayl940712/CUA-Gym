#!/usr/bin/env python3
"""Batch-5 lane 15 bundle generator -- reddit / newest_post_upvote_reply.

Writes ten bundles under output/tasks/reddit/<task_id>/ plus the lane's
GENERATION.md, index.json, nemo_tasks.jsonl and replay drafts under
output/tasks/reddit/_batches/newest_post_upvote_reply/.

Nothing here validates; it only emits files.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE = os.path.join(ROOT, "output/tasks/reddit")
BATCH = os.path.join(SITE, "_batches/newest_post_upvote_reply")
REPLAYS = os.path.join(BATCH, "replays")

APP_DIR = "webarena_reddit_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_REDDIT_URL__"
USER = "MarvelsGrantMan136"
SEED_VOTE = {"1": 1}

ANALOGUE_404 = "Upvote the newest post in books forum"
ANALOGUE_405 = "Upvote the newest post in DIY forum"
ANALOGUE_406 = "Upvote the newest post in futurology forum"
ANALOGUE_407 = "Upvote the newest post in the deep learning forum"
ANALOGUE_408 = "Upvote the newest post in explain like im 5 forum"
ANALOGUE_650 = 'Reply to the post on this page with my comment "I am a big fan of the bookorg"'
ANALOGUE_651 = 'Reply to the post on this page with my comment "Yeah, pittsburgh traffic, you know..."'
ANALOGUE_652 = 'Reply to the post on this page with my comment "???"'
ANALOGUE_599 = 'Subscribe to the "machine learning" forum from the page of the newest post in that forum.'


# --------------------------------------------------------------------------
# reward source
# --------------------------------------------------------------------------

REWARD_BODY = '''
def _norm_text(value):
    """Whitespace-folded text, so a trailing newline in a textarea is not a miss."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _vote_ledger(state):
    """`votes.submissions` as {id string: non-zero int}.

    This is exactly what Vote.jsx:23-31 renders the three-valued form class
    from, so it is the user-visible record of which arrow is lit.
    """
    votes = state.get("votes")
    votes = votes if isinstance(votes, dict) else {}
    rows = votes.get("submissions")
    rows = rows if isinstance(rows, dict) else {}
    ledger = {}
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


def _agent_comments(state):
    rows = state.get("newComments")
    rows = rows if isinstance(rows, list) else []
    return [row for row in rows if isinstance(row, dict)]


def _comment_key(row):
    """(submission id, folded body) for a top-level reply by the seeded user.

    Returns None for anything else -- another author, a reply nested under a
    comment, or a malformed row -- which is what makes the collection
    assertion below exact rather than merely "contains".
    """
    try:
        sid = int(row.get("submission"))
    except (TypeError, ValueError):
        return None
    if _norm_text(row.get("author")) != COMMENT_AUTHOR:
        return None
    if row.get("parent") is not None:
        return None
    return (sid, _norm_text(row.get("body")))


def _replies_match(state):
    """The agent's comment collection is EXACTLY the replies the task asked for."""
    got = []
    for row in _agent_comments(state):
        key = _comment_key(row)
        if key is None:
            return False
        got.append(key)
    want = sorted(
        (int(row["submission"]), _norm_text(row["body"])) for row in EXPECTED_COMMENTS
    )
    return sorted(got) == want


def score_checks(state):
    ledger = _vote_ledger(state)
    values = {
        "exact_ledger": ledger == _expected_ledger(),
        "targeted_votes": all(ledger.get(str(i)) == 1 for i in TARGET_VOTE_IDS),
        "replies": _replies_match(state),
    }
    return dict((name, values[CHECK_FOR[name]]) for name in COMPONENT_WEIGHTS)


def score_details(state):
    ledger = _vote_ledger(state)
    bodies = [_comment_key(row) for row in _agent_comments(state)]
    return "votes.submissions=%s | agent comments=%s" % (
        json.dumps(ledger, sort_keys=True),
        json.dumps([list(b) if b else None for b in bodies], sort_keys=True),
    )
'''


def reward_py(task):
    header = '"""Deterministic reward for %s.\n\n%s\n\nScored off the live session state only. The rubric never diffs a baseline:\nevery component is a positive statement about the collection the episode\nends with, so a key that returns to its seeded value cannot leak credit.\n"""\n' % (
        task["task_id"],
        task["reward_note"],
    )
    consts = _reward_constants(task)
    tail = '''

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
    return header + "\nimport json\n\n" + consts + REWARD_BODY + tail


def nemo_reward_py(task):
    header = '"""NeMo-Gym reward program for %s.\n\n%s\n\nSame rubric as reward.py, reading the live session document from\nGET /go?sid= instead of a frozen evidence bundle. Prints REWARD: on every\noutput path including the error path.\n\nSelf-contained: standard library plus requests.\n"""\n' % (
        task["task_id"],
        task["reward_note"],
    )
    consts = _reward_constants(task)
    tail = '''

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
    imports = "\nimport json\nimport sys\n\nimport requests\n\nSID = \"__CUA_GYM_SID__\"\nBASE_URL = \"%s\"\n\n" % URL_PLACEHOLDER
    return header + imports + consts + REWARD_BODY + tail


def _reward_constants(task):
    lines = []
    lines.append("COMMENT_AUTHOR = %r\n\n" % USER)
    lines.append(
        "# The whole submission-vote ledger this episode must end with. The seeded\n"
        "# session already carries {\"1\": 1} (currentUser.json submissionVotes), so the\n"
        "# task's own upvote is the only addition.\n"
    )
    lines.append('EXPECTED_VOTES = json.loads(r"""%s""")\n\n' % json.dumps(task["expected_votes"], sort_keys=True))
    lines.append("# The submissions whose up arrow must be lit for this agent.\n")
    lines.append('TARGET_VOTE_IDS = json.loads(r"""%s""")\n\n' % json.dumps(task["target_vote_ids"]))
    lines.append(
        "# The agent-authored comment collection this episode must end with:\n"
        "# one top-level reply per named submission, body compared exactly after\n"
        "# whitespace folding.\n"
    )
    lines.append('EXPECTED_COMMENTS = json.loads(r"""%s""")\n\n' % json.dumps(task["expected_comments"]))
    lines.append("COMPONENT_WEIGHTS = {\n")
    for name, weight in task["components"]:
        lines.append("    %r: %s,\n" % (name, weight))
    lines.append("}\n\n")
    lines.append("CHECK_FOR = {\n")
    for name, _ in task["components"]:
        lines.append("    %r: %r,\n" % (name, task["check_for"][name]))
    lines.append("}\n\n")
    return "".join(lines)


# --------------------------------------------------------------------------
# initial_setup source
# --------------------------------------------------------------------------

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{note}

Reads the pristine baseline from GET /go?sid=, replaces the whole top-level
session document, and republishes it with the "set" action, so the episode
baseline is this task's own starting state. Patching a single key instead
would make the baseline that partial object and turn every other key into a
reported change.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

# The submission-vote ledger the episode must OPEN with. The pristine seed
# ships {{"1": 1}}; this adds the misplaced vote the errand is about.
INJECTED_SUBMISSION_VOTES = json.loads(r"""{votes}""")


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    baseline = probe.json().get("initial_state")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)

    votes = baseline.get("votes")
    if not isinstance(votes, dict) or not isinstance(votes.get("submissions"), dict):
        print("SETUP FAILED: baseline carries no vote ledger", file=sys.stderr)
        raise SystemExit(1)
    if baseline.get("newComments"):
        print("SETUP FAILED: baseline already carries agent comments", file=sys.stderr)
        raise SystemExit(1)

    state = dict(baseline)
    state["votes"] = {{
        "submissions": dict(INJECTED_SUBMISSION_VOTES),
        "comments": dict(votes.get("comments") or {{}}),
    }}

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
    current = payload.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: no current state after set", file=sys.stderr)
        raise SystemExit(1)
    if current.get("votes", {{}}).get("submissions") != dict(INJECTED_SUBMISSION_VOTES):
        print("SETUP FAILED: injected vote ledger did not stick", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''


def setup_py(task):
    return SETUP_TEMPLATE.format(
        task_id=task["task_id"],
        note=task["setup_note"],
        url=URL_PLACEHOLDER,
        votes=json.dumps(task["injected_votes"], sort_keys=True),
    )


# --------------------------------------------------------------------------
# replay draft
# --------------------------------------------------------------------------

REPLAY_TEMPLATE = '''"""Golden replay draft - {task_id}.

Click-only from "/": every navigation follows a rendered link or button, with
no page.goto after the initial landing and no constructed URLs.

Route: / -> nav "Forums" -> sort dropdown "Name" -> numbered pager -> the forum
card link -> the forum's sort dropdown "New" -> the top row's comment link ->
the submission page.

Two mock facts the driver has to respect:
  * currentUser.submissionLinkDestination is "url", so a URL or image post's
    title anchor points off-site (Submission.jsx:76-81). Enter the thread
    through the "N comments" link in .submission__nav instead.
  * the sort control is a button-toggled dropdown (ListNav.jsx:12-41), so the
    menu item is only clickable after the toggle is pressed.
"""

{steps}
'''


def replay_py(task):
    steps = ['def run(page, base_url):', '    page.goto(base_url + "/")', '']
    for forum, page_no, sub_id, body in task["replay_targets"]:
        steps.append('    # ---- f/%s: newest submission is %s ----' % (forum, sub_id))
        steps.append('    page.get_by_role("link", name="Forums", exact=True).first.click()')
        steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('')
        steps.append('    # Sort the forum index by Name, then walk the numbered pager.')
        steps.append('    page.locator("button.dropdown__toggle").first.click()')
        steps.append('    page.locator("li.dropdown--expanded ul.dropdown__menu")'
                     '.get_by_role("link", name="Name", exact=True).first.click()')
        steps.append('    page.wait_for_load_state("networkidle")')
        if page_no > 1:
            steps.append('    page.get_by_role("link", name="Page %d", exact=True).first.click()' % page_no)
            steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('    page.get_by_role("link", name="%s", exact=True).first.click()' % forum)
        steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('')
        steps.append('    # Switch the listing from Hot to New; /new is id DESC (listing.js:34),')
        steps.append('    # so row 0 is the newest submission. No ?t= is involved on this sort.')
        steps.append('    page.locator("button.dropdown__toggle").first.click()')
        steps.append('    page.locator("li.dropdown--expanded ul.dropdown__menu")'
                     '.get_by_role("link", name="New", exact=True).first.click()')
        steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('')
        steps.append('    # Open the thread through the comment-count link, never the title anchor.')
        steps.append('    page.locator("article.submission").first.locator("nav.submission__nav a").first.click()')
        steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('')
        if task["votes_in_replay"]:
            steps.append('    page.locator("div.submission__vote form button.vote__up").first.click()')
            steps.append('    page.wait_for_timeout(300)')
            steps.append('')
        if body is not None:
            steps.append('    page.locator("form.comment-form textarea").fill(')
            steps.append('        %r' % body)
            steps.append('    )')
            steps.append('    page.get_by_role("button", name="Post", exact=True).click()')
            steps.append('    page.wait_for_timeout(500)')
            steps.append('')
        steps.append('    page.get_by_role("link", name="Forums", exact=True).first.click()')
        steps.append('    page.wait_for_load_state("networkidle")')
        steps.append('')
    return REPLAY_TEMPLATE.format(task_id=task["task_id"], steps="\n".join(steps).rstrip() + "\n")


# --------------------------------------------------------------------------
# task definitions
# --------------------------------------------------------------------------

def vote_reply_components():
    return [("vote_ledger_now_seed_plus_newest_post", 0.5),
            ("reply_posted_on_newest_post", 0.5)]


TASKS = []


def add(**kw):
    TASKS.append(kw)


add(
    task_id="newest_post_upvote_reply_consoles_dreamcast_001",
    instruction=(
        "In f/consoles, upvote the newest post and reply to it with exactly: "
        "Still have my Dreamcast hooked up."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "A9", "A8"],
    skill_chain=(
        "open f/consoles sorted by New -> take the top (newest) submission -> "
        "upvote that submission -> post a top-level reply on the same submission"
    ),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[ANALOGUE_404, ANALOGUE_650],
    inspiration_ids=["webarena-404", "webarena-650"],
    expected_votes={"1": 1, "124591": 1},
    target_vote_ids=["124591"],
    expected_comments=[{"submission": 124591, "body": "Still have my Dreamcast hooked up."}],
    components=vote_reply_components(),
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "The target is derived: f/consoles sorted by New puts submission 124591\n"
        "('What consoles have you owned/had throughout your life?', 2023-03-30) at\n"
        "the top, one clear id ahead of 124590. The vote component asserts the whole\n"
        "resulting ledger, so voting on a neighbouring row instead scores zero and a\n"
        "spray of votes cannot buy the point."
    ),
    replay_targets=[("consoles", 1, 124591, "Still have my Dreamcast hooked up.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "Target verified against src/data/submissions.json: f/consoles newest by id "
        "(124591) is also newest by timestamp, so /new and a human reading of "
        "'newest' agree.",
        "Entered through the comment-count link because 124591 is a self post; the "
        "title anchor is internal here, but the replay uses the same route for every "
        "task in the lane.",
    ],
)

add(
    task_id="newest_post_upvote_reply_memes_misclick_flip_002",
    instruction=(
        "I hit the wrong arrow on the newest post in f/memes. Turn that downvote into "
        "an upvote, then reply to the post with exactly: Sorry about the misclick."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "A9", "A8"],
    skill_chain=(
        "open f/memes sorted by New -> take the top (newest) submission, which is "
        "carrying my downvote -> flip that vote to an upvote -> reply on the same post"
    ),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[ANALOGUE_406, ANALOGUE_651],
    inspiration_ids=["webarena-406", "webarena-651"],
    expected_votes={"1": 1, "127991": 1},
    target_vote_ids=["127991"],
    expected_comments=[{"submission": 127991, "body": "Sorry about the misclick."}],
    components=vote_reply_components(),
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "The episode opens with votes.submissions['127991'] == -1, so the vote form on\n"
        "f/memes' newest post renders 'vote vote--user-downvoted' (Vote.jsx:27-31).\n"
        "The component pays only for the ledger ending at exactly {'1': 1,\n"
        "'127991': 1} -- the injected -1 satisfies no part of it."
    ),
    replay_targets=[("memes", 2, 127991, "Sorry about the misclick.")],
    votes_in_replay=True,
    setup=dict(
        injected_votes={"1": 1, "127991": -1},
        note=(
            "Seeds votes.submissions['127991'] = -1: a standing DOWNVOTE on the newest\n"
            "post in f/memes, which is the situation the errand is about. Clicking the up\n"
            "arrow from -1 runs the flip branch of AppContext.jsx:321 (delta 2), a branch\n"
            "the pristine seed can never reach because its only vote is on submission 1.\n"
            "In envelope: the seed itself ships a pre-existing submission vote."
        ),
        preconditions=[
            "votes.submissions['127991'] = -1 -- a standing downvote on f/memes' newest "
            "post, so the task is a vote FLIP (Vote.jsx renders vote--user-downvoted) "
            "rather than a fresh upvote. The pristine seed only ever carries "
            "votes.submissions = {'1': 1}, so this branch is otherwise unreachable.",
        ],
    ),
    notes=[
        "The injected -1 pre-satisfies nothing: the rubric demands +1 on the same id.",
        "netScore still renders 3 on the row because injecting a vote does not write "
        "submissionEdits; clicking up then writes netScore 5 through the overlay. "
        "Neither figure is scored.",
    ],
)

add(
    task_id="newest_post_upvote_reply_worldnews_thank_author_003",
    instruction=(
        "Upvote the newest post in f/worldnews, then reply to it thanking its author, "
        "in exactly this form with USERNAME replaced by that author's username: "
        "Thanks for posting this, USERNAME."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "R9", "A9", "A8"],
    skill_chain=(
        "open f/worldnews sorted by New -> take the top submission -> read its byline "
        "for the author's username -> upvote the submission -> reply carrying that "
        "username into the comment body"
    ),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[ANALOGUE_405, ANALOGUE_650],
    inspiration_ids=["webarena-405", "webarena-650"],
    expected_votes={"1": 1, "137394": 1},
    target_vote_ids=["137394"],
    expected_comments=[{"submission": 137394,
                        "body": "Thanks for posting this, Additional-Force-795."}],
    components=vote_reply_components(),
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "Two derived facts land in state: which submission was voted (137394, the top\n"
        "of f/worldnews' New listing) and the username on its byline\n"
        "(Additional-Force-795), which must be transferred verbatim into the comment\n"
        "body. Neither value appears in the instruction."
    ),
    replay_targets=[("worldnews", 4, 137394, "Thanks for posting this, Additional-Force-795.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "137394 is a URL post, so its title anchor is external "
        "(Submission.jsx:76-81); the thread is reached through the comment-count link.",
        "The author string is unaffected by both of the agent's own mutations, so the "
        "action cannot destroy its own retrieval premise.",
    ],
)

add(
    task_id="newest_post_upvote_reply_listentothis_post_id_004",
    instruction=(
        "Upvote the newest post in f/listentothis, then reply to it with exactly this "
        "line, with NNNN replaced by that post's own submission id: Bookmarking post NNNN."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "R9", "A9", "A8"],
    skill_chain=(
        "open f/listentothis sorted by New -> take the top submission -> read its own "
        "numeric id off the permalink or short URL -> upvote it -> reply carrying that "
        "id into the comment body"
    ),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[ANALOGUE_407, ANALOGUE_652],
    inspiration_ids=["webarena-407", "webarena-652"],
    expected_votes={"1": 1, "127272": 1},
    target_vote_ids=["127272"],
    expected_comments=[{"submission": 127272, "body": "Bookmarking post 127272."}],
    components=vote_reply_components(),
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "The recorded body has to carry the submission's own id (127272), which the\n"
        "agent can only read off the thread URL or the sidebar's short URL kbd\n"
        "(Sidebars.jsx:172). Voting the right post but writing the wrong number keeps\n"
        "only the vote half of the credit."
    ),
    replay_targets=[("listentothis", 2, 127272, "Bookmarking post 127272.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "127272 is a Spotify URL post, so the thread is entered via the comment link.",
        "The id is immutable under both mutations, unlike score or comment count.",
    ],
)

add(
    task_id="newest_post_upvote_reply_tifu_vote_only_005",
    instruction="Give the newest post in f/tifu an upvote.",
    style="terse",
    difficulty="medium",
    skills=["R4", "A9"],
    skill_chain="open f/tifu sorted by New -> take the top submission -> upvote it",
    hard_criteria=None,
    analogues=[ANALOGUE_408],
    inspiration_ids=["webarena-408"],
    expected_votes={"1": 1, "135514": 1},
    target_vote_ids=["135514"],
    expected_comments=[],
    components=[("vote_ledger_now_seed_plus_newest_post", 1.0)],
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger"},
    reward_note=(
        "One mutation, but the entity is derived: f/tifu's New listing is id DESC, so\n"
        "135514 is the row to act on and 135513 is the near miss. The whole ledger is\n"
        "asserted, so an agent that upvotes several rows to be safe scores zero."
    ),
    replay_targets=[("tifu", 4, 135514, None)],
    votes_in_replay=True,
    setup=None,
    notes=[
        "Two skills only (one retrieval, one action), so this is medium by the batch-5 "
        "rule; it was not padded up with a comment it does not need.",
    ],
)

add(
    task_id="newest_post_upvote_reply_aww_reply_only_006",
    instruction=(
        "Reply to the newest post in f/aww with exactly: Menace behaviour, ten out of ten."
    ),
    style="terse",
    difficulty="medium",
    skills=["R4", "A8"],
    skill_chain=(
        "open f/aww sorted by New -> take the top submission -> post a top-level reply "
        "on it"
    ),
    hard_criteria=None,
    analogues=[ANALOGUE_652],
    inspiration_ids=["webarena-652"],
    expected_votes={"1": 1},
    target_vote_ids=[],
    expected_comments=[{"submission": 123755, "body": "Menace behaviour, ten out of ten."}],
    components=[("reply_posted_on_newest_post", 1.0)],
    check_for={"reply_posted_on_newest_post": "replies"},
    reward_note=(
        "The comment collection must end as exactly one top-level reply, by the seeded\n"
        "user, on submission 123755 -- the top of f/aww's New listing -- with that body.\n"
        "A reply left on the wrong thread, or an extra scattergun comment, fails it."
    ),
    replay_targets=[("aww", 1, 123755, "Menace behaviour, ten out of ten.")],
    votes_in_replay=False,
    setup=None,
    notes=[
        "123755 is an image post: its title anchor points at /submission_images/..., so "
        "the comment-count link is the only in-site route into the thread.",
        "No vote component -- the task never asks for one, and paying for an untouched "
        "ledger would be paying for inaction.",
    ],
)

add(
    task_id="newest_post_upvote_reply_askscience_move_vote_007",
    instruction=(
        "My upvote in f/askscience is sitting on the second-newest post. Move it onto "
        "the newest one, then reply there with exactly: Voting on the right thread this time."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "A9", "A8"],
    skill_chain=(
        "open f/askscience sorted by New -> read the top two rows to tell the newest "
        "from the second-newest -> retract the vote on the second -> upvote the first -> "
        "reply on the first"
    ),
    hard_criteria=["derived_target", "multi_mutation"],
    analogues=[ANALOGUE_404, ANALOGUE_650],
    inspiration_ids=["webarena-404", "webarena-650"],
    expected_votes={"1": 1, "123497": 1},
    target_vote_ids=["123497"],
    expected_comments=[{"submission": 123497,
                        "body": "Voting on the right thread this time."}],
    components=[("vote_ledger_now_only_the_newest_post", 0.5),
                ("reply_posted_on_newest_post", 0.5)],
    check_for={"vote_ledger_now_only_the_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "Three mutations, and the first two are on different records: retract the\n"
        "injected upvote on 123496 (clicking a lit up arrow sets the choice back to 0\n"
        "and deletes the key, AppContext.jsx:321-333) and upvote 123497. The retraction\n"
        "is a removal the instruction asked for, so scoring it is not paying for\n"
        "inaction."
    ),
    replay_targets=[("askscience", 1, 123497, "Voting on the right thread this time.")],
    votes_in_replay=True,
    setup=dict(
        injected_votes={"1": 1, "123496": 1},
        note=(
            "Seeds votes.submissions['123496'] = 1 -- a standing upvote on f/askscience's\n"
            "SECOND-newest post ('Is there any consensus on the length of long-COVID?').\n"
            "That is the misplaced vote the errand exists to correct, and it forces the\n"
            "agent to distinguish rows 0 and 1 of the New listing rather than acting on\n"
            "whatever it lands on first."
        ),
        preconditions=[
            "votes.submissions['123496'] = 1 -- an upvote parked on f/askscience's "
            "second-newest submission. It is the distractor AND the thing that has to be "
            "retracted; it satisfies no part of the rubric, which requires the ledger to "
            "end as {'1': 1, '123497': 1}.",
        ],
    ),
    notes=[
        "Margin: 123497 (2023-03-31 13:37) vs 123496 (2023-03-30 21:18) -- one id apart "
        "and about 16 hours apart, close enough to require reading, unambiguous either way.",
        "The replay must retract on 123496 before or after upvoting 123497; order does "
        "not matter to the handler, only the end ledger is scored.",
    ],
)

add(
    task_id="newest_post_upvote_reply_two_city_forums_008",
    instruction=(
        "Upvote the newest post in both f/newhaven and f/LowellMA, and reply to each of "
        "them with exactly: Following this thread."
    ),
    style="terse",
    difficulty="hard",
    skills=["R4", "A9", "A8"],
    skill_chain=(
        "open f/newhaven sorted by New -> take its newest submission -> upvote and reply "
        "-> repeat the same ordinal pick on f/LowellMA"
    ),
    hard_criteria=["derived_target", "multi_mutation"],
    analogues=[ANALOGUE_405, ANALOGUE_650],
    inspiration_ids=["webarena-405", "webarena-650"],
    expected_votes={"1": 1, "129127": 1, "120403": 1},
    target_vote_ids=["129127", "120403"],
    expected_comments=[
        {"submission": 129127, "body": "Following this thread."},
        {"submission": 120403, "body": "Following this thread."},
    ],
    components=[("vote_ledger_now_seed_plus_both_newest_posts", 0.5),
                ("replies_posted_on_both_newest_posts", 0.5)],
    check_for={"vote_ledger_now_seed_plus_both_newest_posts": "exact_ledger",
               "replies_posted_on_both_newest_posts": "replies"},
    reward_note=(
        "Four mutations across two forums: the ledger must end as the seed plus 129127\n"
        "and 120403, and the comment collection as exactly those two top-level replies.\n"
        "Doing one forum and stopping earns nothing, because both components are\n"
        "collection-level assertions."
    ),
    replay_targets=[("newhaven", 3, 129127, "Following this thread."),
                    ("LowellMA", 2, 120403, "Following this thread.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "Both forums' newest-by-id post is also newest-by-timestamp (129127 "
        "2023-03-31 12:56; 120403 2023-03-31 22:41), so the ordinal never argues with "
        "the visible dates.",
        "Two identical bodies on two different submissions: the reward sorts "
        "(submission, body) pairs, so it discriminates on which threads were replied to.",
    ],
)

add(
    task_id="newest_post_upvote_reply_stamfordct_explicit_009",
    instruction=(
        "I want to back the most recent thing posted in the StamfordCT forum. Starting "
        "from the front page, open the list of forums and find StamfordCT. On the forum "
        "page, use the sort control to switch the listing from Hot to New, so the most "
        "recently submitted post sits at the top of the list, and open that post's own "
        "page. Upvote it with the up arrow beside its score, then use the comment box at "
        "the bottom of the page to post a top-level reply whose body is exactly: "
        "Kickball sounds great, count me in. That post must be the only submission you "
        "add a vote to -- do not vote on any of the other rows in the listing on your way "
        "there, and leave the vote that is already on my own Nvidia RTX 4090 post alone."
    ),
    style="explicit",
    difficulty="hard",
    skills=["R4", "A9", "A8"],
    skill_chain=(
        "open f/StamfordCT sorted by New -> take the top submission -> upvote it -> "
        "post a top-level reply on the same submission, with no other submission vote "
        "added"
    ),
    hard_criteria=["derived_target", "exclusion_constraint", "cross_section"],
    analogues=[ANALOGUE_599, ANALOGUE_650],
    inspiration_ids=["webarena-599", "webarena-650"],
    expected_votes={"1": 1, "122557": 1},
    target_vote_ids=["122557"],
    expected_comments=[{"submission": 122557, "body": "Kickball sounds great, count me in."}],
    components=[("newest_post_upvoted", 0.4),
                ("reply_posted_on_newest_post", 0.4),
                ("vote_ledger_now_seed_plus_newest_post", 0.2)],
    check_for={"newest_post_upvoted": "targeted_votes",
               "reply_posted_on_newest_post": "replies",
               "vote_ledger_now_seed_plus_newest_post": "exact_ledger"},
    reward_note=(
        "Explicit set, so the containment clause is scored separately: 0.4 for the up\n"
        "arrow being lit on 122557, 0.4 for the reply, and 0.2 for the whole ledger\n"
        "ending as the seeded {'1': 1} plus that one vote. The seeded vote on submission\n"
        "1 is named in the instruction, so leaving it is an instructed end state rather\n"
        "than an unstated preservation trap."
    ),
    replay_targets=[("StamfordCT", 4, 122557, "Kickball sounds great, count me in.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "122557 'Come Play Kickball!' is a self post, newest by id and by timestamp in "
        "f/StamfordCT (2023-03-31 19:17 vs 122556 at 05:59).",
        "Explicit style chosen because the containment clause cannot be expressed as a "
        "pure accomplishment statement without naming the seeded vote.",
    ],
)

add(
    task_id="newest_post_upvote_reply_coolgithub_credit_line_010",
    instruction=(
        "From the front page, open the list of forums and go to coolgithubprojects. "
        "Switch that forum's listing sort from Hot to New; the submission at the top of "
        "the New listing is the one this errand is about. Open its page, upvote it, and "
        "then post one top-level reply on it. The reply body must read exactly "
        "'Saved: post ID by AUTHOR.' with ID replaced by that submission's own numeric "
        "id, which you can read off its page address or its short URL in the sidebar, "
        "and AUTHOR replaced by the username shown on its byline. Post exactly one "
        "comment and add exactly one submission upvote."
    ),
    style="explicit",
    difficulty="hard",
    skills=["R4", "R9", "A9", "A8"],
    skill_chain=(
        "open f/coolgithubprojects sorted by New -> take the top submission -> read its "
        "id and its author off the page -> upvote it -> compose a reply that carries "
        "both derived values"
    ),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[ANALOGUE_406, ANALOGUE_650],
    inspiration_ids=["webarena-406", "webarena-650"],
    expected_votes={"1": 1, "124607": 1},
    target_vote_ids=["124607"],
    expected_comments=[{"submission": 124607,
                        "body": "Saved: post 124607 by EatSleepCodeDelete."}],
    components=vote_reply_components(),
    check_for={"vote_ledger_now_seed_plus_newest_post": "exact_ledger",
               "reply_posted_on_newest_post": "replies"},
    reward_note=(
        "Two retrievals feed one composed string: the submission id (124607) and the\n"
        "byline username (EatSleepCodeDelete). Both are stable under the episode's own\n"
        "mutations, unlike the score and the comment count, so the derived answer cannot\n"
        "drift while the agent works."
    ),
    replay_targets=[("coolgithubprojects", 1, 124607,
                     "Saved: post 124607 by EatSleepCodeDelete.")],
    votes_in_replay=True,
    setup=None,
    notes=[
        "REJECTED first draft of this task used 'how many comments it had before you "
        "replied'. The forum row label reads 6 comments (submission.commentCount) while "
        "the thread renders 5 seeded comment rows, so the derived number would have had "
        "two defensible answers. Replaced with id + author.",
        "124607 is a GitHub URL post, so the thread is reached through the "
        "comment-count link rather than the title anchor.",
    ],
)


# --------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------

def success_criteria(task):
    out = []
    ledger = json.dumps(task["expected_votes"], sort_keys=True)
    if any(name.startswith("vote_ledger") for name, _ in task["components"]):
        out.append(
            "votes.submissions ends as exactly %s -- the seeded vote on submission 1 "
            "plus the submission vote(s) this task asks for, and nothing else." % ledger
        )
    if any(name == "newest_post_upvoted" for name, _ in task["components"]):
        out.append(
            "votes.submissions carries the value 1 for submission %s, so its vote form "
            "renders as 'vote vote--user-upvoted'." % ", ".join(task["target_vote_ids"])
        )
    if task["expected_comments"]:
        pieces = ["submission %s with the body %r" % (c["submission"], c["body"])
                  for c in task["expected_comments"]]
        out.append(
            "newComments holds exactly %d top-level comment(s) authored by %s: %s."
            % (len(task["expected_comments"]), USER, "; ".join(pieces))
        )
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = []
    rows = []

    for task in TASKS:
        tid = task["task_id"]
        bundle = os.path.join(SITE, tid)
        os.makedirs(bundle, exist_ok=True)

        instruction = " ".join(task["instruction"].split())

        write(os.path.join(bundle, "task_instruction.json"), json.dumps({
            "task_id": tid,
            "task_instruction": instruction,
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": task["difficulty"],
            "success_criteria": success_criteria(task),
        }, indent=2) + "\n")

        metadata = {
            "style": task["style"],
            "difficulty": task["difficulty"],
            "shape": "retrieval_writeback",
            "skills": task["skills"],
            "skill_chain": task["skill_chain"],
            "official_analogues": task["analogues"],
            "topic": "newest_post_upvote_reply -- ordinal pick on a forum's New "
                     "listing, then vote and/or reply on that same submission",
            "inspiration_ids": task["inspiration_ids"],
            "authoring_notes": task["notes"] + [
                "Grounded in webarena_reddit_mock @ hub/websites/webarena_reddit_mock; "
                "nothing under hub/ was modified.",
                "Both reward programs read the live session document only and never "
                "diff a baseline.",
                "'Newest' is the top row of /f/{forum}/new, which is id DESC "
                "(src/utils/listing.js:34); submission ids are unique so the ordinal "
                "never ties.",
            ],
        }
        if task["hard_criteria"]:
            metadata["hard_criteria"] = task["hard_criteria"]
        if task["setup"]:
            metadata["injected_preconditions"] = task["setup"]["preconditions"]

        write(os.path.join(bundle, "task.json"), json.dumps({
            "schema_version": 2,
            "task_id": tid,
            "instruction": instruction,
            "apps": [{
                "name": APP_DIR,
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
            "metadata": metadata,
        }, indent=2) + "\n")

        write(os.path.join(bundle, "reward.py"), reward_py(task))
        write(os.path.join(bundle, "nemo_reward.py"), nemo_reward_py(task))

        setup_text = None
        if task["setup"]:
            setup_text = setup_py({
                "task_id": tid,
                "setup_note": task["setup"]["note"],
                "injected_votes": task["setup"]["injected_votes"],
            })
            write(os.path.join(bundle, "initial_setup.py"), setup_text)

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": instruction,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_text,
                "eval_reward_code": nemo_reward_py(task),
            },
        }}
        write(os.path.join(bundle, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
        rows.append(json.dumps(row))

        write(os.path.join(REPLAYS, tid + ".py"), replay_py(task))
        index.append({"task_id": tid, "path": "../../%s/task.json" % tid})

    write(os.path.join(BATCH, "index.json"),
          json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    write(os.path.join(BATCH, "nemo_tasks.jsonl"), "\n".join(rows) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
