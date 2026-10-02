#!/usr/bin/env python3
"""Bundle generator for batch-5 lane 18 (reddit / forum_choice_post_and_comment).

Authoring helper only. Writes 10 schema-v2 bundles plus replay drafts.
No validation is run from here.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SITE = os.path.join(ROOT, "output/tasks/reddit")
BATCH = os.path.join(SITE, "_batches/forum_choice_post_and_comment")
REPLAYS = os.path.join(BATCH, "replays")

AUTHOR = "MarvelsGrantMan136"

OFFICIAL = {}
with open(os.path.join(ROOT, "webarena_benchmarks/webarena.jsonl")) as fh:
    for line in fh:
        row = json.loads(line)
        OFFICIAL[row["id"]] = row["ques"]


def q(task_id):
    return OFFICIAL["webarena-%d" % task_id]


TASKS = [
    {
        "id": "forum_choice_post_and_comment_console_purchase_advice_001",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R8", "A2", "A8", "A12"],
        "instruction": (
            "Ask which console to buy, in a forum where I'd actually get an answer. "
            "Title it \"which console should I buy in 2024?\", details "
            "\"budget around $400\", then comment \"exclusives matter more than 4k\" "
            "on the new post."
        ),
        "forums": ["consoles"],
        "forum_label": "consoles",
        "title": "which console should I buy in 2024?",
        "body": "budget around $400",
        "comment": "exclusives matter more than 4k",
        "analogues": [600, 605],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_noise_cancelling_headphones_002",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R8", "A2"],
        "instruction": (
            "I need noise-cancelling over-ear headphones for a loud commute, under $250. "
            "Post that question in the most appropriate forum, titled "
            "\"noise-cancelling over-ear headphones under $250?\" with details "
            "\"train commute, two hours a day\"."
        ),
        "forums": ["headphones"],
        "forum_label": "headphones",
        "title": "noise-cancelling over-ear headphones under $250?",
        "body": "train commute, two hours a day",
        "comment": None,
        "analogues": [637, 635],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_moving_in_together_003",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R8", "A2", "A8", "A12"],
        "instruction": (
            "Ask for advice about moving in with my partner, in the forum for "
            "relationship questions. Title it \"is it too soon to move in together?\", "
            "details \"eight months in\", then comment "
            "\"we already split rent on nothing\" on it."
        ),
        "forums": ["relationship_advice"],
        "forum_label": "relationship_advice",
        "title": "is it too soon to move in together?",
        "body": "eight months in",
        "comment": "we already split rent on nothing",
        "analogues": [620],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_pittsburgh_driving_practice_004",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R8", "A2"],
        "instruction": (
            "New in Pittsburgh and looking for a driving instructor. Post that in "
            "whichever forum fits best, titled "
            "\"where do new drivers practise around Pittsburgh?\" with details "
            "\"never driven in snow\"."
        ),
        "forums": ["pittsburgh"],
        "forum_label": "pittsburgh",
        "title": "where do new drivers practise around Pittsburgh?",
        "body": "never driven in snow",
        "comment": None,
        "analogues": [602, 607],
        "setup": {"kind": "subscriptions", "subscriptions": ["food", "space"]},
    },
    {
        "id": "forum_choice_post_and_comment_emergency_fund_months_005",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R8", "A2", "A8", "A12"],
        "instruction": (
            "Ask how big an emergency fund should be, in the forum where I'd get a "
            "useful answer. Title it "
            "\"how many months should an emergency fund cover?\", details "
            "\"single income\", then comment \"rent is my biggest line\" on it."
        ),
        "forums": ["personalfinance"],
        "forum_label": "personalfinance",
        "title": "how many months should an emergency fund cover?",
        "body": "single income",
        "comment": "rent is my biggest line",
        "analogues": [635, 600],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_scaling_laws_discussion_006",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R8", "A2"],
        "instruction": (
            "Start a discussion about whether scaling laws still hold, in a relevant "
            "forum. Title it \"do scaling laws still hold in 2024?\" and set the "
            "details to \"your opinion\"."
        ),
        "forums": ["deeplearning", "machinelearning", "singularity"],
        "forum_label": "deeplearning, MachineLearning or singularity",
        "title": "do scaling laws still hold in 2024?",
        "body": "your opinion",
        "comment": None,
        "analogues": [625, 609],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_piranesi_book_writeup_007",
        "style": "explicit",
        "difficulty": "hard",
        "skills": ["R8", "A2", "A8", "A12"],
        "instruction": (
            "I have just finished reading Piranesi by Susanna Clarke and I want to "
            "write it up on the discussion site. Work out for yourself which of the "
            "site's forums is the one where people discuss books - the forum list "
            "reachable from the Forums link in the top navigation shows every one of "
            "them - and open the submit form for that forum. Give the post the title "
            "\"Piranesi by Susanna Clarke\" and put "
            "\"Strange, quiet, and I finished it in two sittings.\" in the post "
            "details field; leave the URL field empty so that it is a plain text "
            "post. Once the post has been created and you are looking at its page, "
            "add a comment on it that reads "
            "\"the ending recontextualises everything\". The comment has to be on the "
            "post you just created, not on any other thread."
        ),
        "forums": ["books"],
        "forum_label": "books",
        "title": "Piranesi by Susanna Clarke",
        "body": "Strange, quiet, and I finished it in two sittings.",
        "comment": "the ending recontextualises everything",
        "analogues": [610],
        "setup": None,
    },
    {
        "id": "forum_choice_post_and_comment_nyc_car_ownership_008",
        "style": "terse",
        "difficulty": "medium",
        "skills": ["R8", "A2"],
        "instruction": (
            "Post my question about whether I need a car after moving to New York "
            "City, in a forum where I'd get an answer. Title it "
            "\"do I need a car in NYC?\" with details "
            "\"moving to Queens in June\"."
        ),
        "forums": ["nyc"],
        "forum_label": "nyc",
        "title": "do I need a car in NYC?",
        "body": "moving to Queens in June",
        "comment": None,
        "analogues": [601, 606],
        "setup": {"kind": "subscriptions", "subscriptions": ["Documentaries", "gifs"]},
    },
    {
        "id": "forum_choice_post_and_comment_quiet_switches_repost_009",
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R9", "R8", "A2", "A8", "A12"],
        "instruction": (
            "I asked about quiet keyboard switches in the wrong forum. Repost it word "
            "for word in the forum where it belongs, with details "
            "\"open plan office, three desks\", then comment "
            "\"happy to lube them myself\" on the new post."
        ),
        "forums": ["mechanicalkeyboards"],
        "forum_label": "MechanicalKeyboards",
        "title": "which switches are quietest for a shared office?",
        "body": "open plan office, three desks",
        "comment": "happy to lube them myself",
        "analogues": [635, 605],
        "setup": {
            "kind": "misplaced_post",
            "host_forum": "gadgets",
            "post_title": "which switches are quietest for a shared office?",
            "post_body": "open plan office, three desks",
            "slug": "which-switches-are-quietest-for-a-shared-office",
        },
    },
    {
        "id": "forum_choice_post_and_comment_lasting_laptop_bag_010",
        "style": "explicit",
        "difficulty": "hard",
        "skills": ["R9", "R8", "A2", "A8", "A12"],
        "instruction": (
            "A while ago I posted a question about a laptop bag that would actually "
            "last, and I put it in a forum that was never going to answer it. Open my "
            "own profile from the user menu in the top navigation, find that "
            "submission of mine, and read its title. Then post the very same question "
            "again, reusing that title exactly as it is written, in the forum on this "
            "site whose whole purpose is products that are built to last a lifetime. "
            "Set the details of the new post to "
            "\"tired of replacing bags every eighteen months\" and leave the URL "
            "field empty. Finally, on the page of the post you have just created, "
            "leave a comment reading \"leather or ballistic nylon both fine\". Leave "
            "the original mis-filed post where it is."
        ),
        "forums": ["buyitforlife"],
        "forum_label": "BuyItForLife",
        "title": "a laptop backpack that will outlive the laptop?",
        "body": "tired of replacing bags every eighteen months",
        "comment": "leather or ballistic nylon both fine",
        "analogues": [638],
        "setup": {
            "kind": "misplaced_post",
            "host_forum": "technology",
            "post_title": "a laptop backpack that will outlive the laptop?",
            "post_body": "tired of replacing bags every eighteen months",
            "slug": "a-laptop-backpack-that-will-outlive-the-laptop",
        },
    },
]


def norm(value):
    return " ".join(str(value).split()).strip().lower()


def rubric_block(task):
    """Shared scoring source, identical in reward.py and nemo_reward.py."""
    min_id = 200001 if (task["setup"] or {}).get("kind") == "misplaced_post" else 0
    forums = json.dumps(sorted(task["forums"]))
    if task["comment"]:
        weights = (
            'COMPONENT_WEIGHTS = {\n'
            '    "post_in_target_forum": 0.35,\n'
            '    "post_title_and_details": 0.3,\n'
            '    "comment_on_new_post": 0.35,\n'
            '}\n'
        )
    else:
        weights = (
            'COMPONENT_WEIGHTS = {\n'
            '    "post_in_target_forum": 0.5,\n'
            '    "post_title_and_details": 0.5,\n'
            '}\n'
        )
    comment_key = norm(task["comment"]) if task["comment"] else ""
    lines = []
    lines.append('AUTHOR = "%s"' % AUTHOR.lower())
    lines.append('TARGET_FORUMS = json.loads(r"""%s""")' % forums)
    lines.append('TITLE_KEY = %r' % norm(task["title"]))
    lines.append('BODY_KEY = %r' % norm(task["body"]))
    lines.append('COMMENT_KEY = %r' % comment_key)
    lines.append('MIN_NEW_SUBMISSION_ID = %d' % min_id)
    lines.append('')
    lines.append(weights.rstrip('\n'))
    lines.append('')
    lines.append('''
def _norm(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip().lower()


def _rows(state, key):
    value = state.get(key) if isinstance(state, dict) else None
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _authored_posts(state):
    """Submissions this episode's agent created, ignoring any seeded baseline row."""
    out = []
    for row in _rows(state, "newSubmissions"):
        if _norm(row.get("author")) != AUTHOR:
            continue
        row_id = _as_int(row.get("id"))
        if row_id is None or row_id < MIN_NEW_SUBMISSION_ID:
            continue
        out.append(row)
    return out


def _authored_comments(state):
    out = []
    for row in _rows(state, "newComments"):
        if _norm(row.get("author")) != AUTHOR:
            continue
        out.append(row)
    return out
'''.strip('\n'))
    lines.append('')
    lines.append('')
    if task["comment"]:
        lines.append('''
def score_checks(state):
    posts = _authored_posts(state)
    post = posts[0] if len(posts) == 1 else None
    in_forum = post is not None and _norm(post.get("forum")) in TARGET_FORUMS
    text_ok = (
        post is not None
        and TITLE_KEY in _norm(post.get("title"))
        and BODY_KEY in _norm(post.get("body"))
    )
    comment_ok = False
    if in_forum and text_ok:
        post_id = _as_int(post.get("id"))
        comments = _authored_comments(state)
        if len(comments) == 1 and post_id is not None:
            comment = comments[0]
            comment_ok = (
                _as_int(comment.get("submission")) == post_id
                and COMMENT_KEY in _norm(comment.get("body"))
            )
    return {
        "post_in_target_forum": bool(in_forum),
        "post_title_and_details": bool(in_forum and text_ok),
        "comment_on_new_post": bool(comment_ok),
    }
'''.strip('\n'))
    else:
        lines.append('''
def score_checks(state):
    posts = _authored_posts(state)
    post = posts[0] if len(posts) == 1 else None
    in_forum = post is not None and _norm(post.get("forum")) in TARGET_FORUMS
    text_ok = (
        post is not None
        and TITLE_KEY in _norm(post.get("title"))
        and BODY_KEY in _norm(post.get("body"))
    )
    return {
        "post_in_target_forum": bool(in_forum),
        "post_title_and_details": bool(in_forum and text_ok),
    }
'''.strip('\n'))
    return "\n".join(lines)


REWARD_TAIL = '''

def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    app = None
    if isinstance(apps, dict):
        for candidate_key in ("reddit", "webarena_reddit_mock"):
            candidate = apps.get(candidate_key)
            if isinstance(candidate, dict):
                app = candidate
                break
    state = app.get("current_state") if isinstance(app, dict) else None
    if not isinstance(state, dict):
        state = {}

    checks = score_checks(state)
    components = []
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        satisfied = bool(checks.get(name))
        earned = COMPONENT_WEIGHTS[name] if satisfied else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": "%s=%s" % (name, satisfied),
        })
    return {"score": round(total, 6), "components": components}
'''

NEMO_TAIL = '''

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
    for name in COMPONENT_WEIGHTS:
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
'''


def reward_py(task):
    doc = (
        '"""Deterministic reward for %s.\n\n'
        'One retrieval (which of the 95 forums the question belongs in) feeding the\n'
        'creation of the post%s. Every component is a positive statement about what\n'
        'the agent made true, and each later component is gated on the earlier one,\n'
        'so an untouched episode scores exactly 0.0.\n\n'
        'Scored strictly off current_state; nothing is diffed against initial_state.\n'
        '"""\n'
    ) % (task["id"], " and of the comment on that post" if task["comment"] else "")
    return doc + "\nimport json\n\n" + rubric_block(task) + "\n" + REWARD_TAIL


def nemo_reward_py(task):
    doc = (
        '"""NeMo-Gym reward program for %s.\n\n'
        'Same rubric as reward.py, reading current_state from GET /go?sid=... and\n'
        'printing REWARD: <float> on every output path including the error path.\n\n'
        'Self-contained: standard library plus requests (in cuagym/requirements.txt).\n'
        '"""\n'
    ) % task["id"]
    head = (
        doc
        + "\nimport json\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\n'
        + 'BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"\n\n'
    )
    return head + rubric_block(task) + "\n" + NEMO_TAIL


SETUP_HEAD = '''"""NeMo-Gym setup program for {task_id}.

{summary}

Reads the pristine baseline from GET /go?sid=, replaces only the top-level
session keys this task needs, and republishes the whole state document with the
set action, so the episode baseline is this task's own starting state rather
than a partial object. Fixtures are parsed from raw-string JSON literals, so no
bare JS literal and no parser-eaten escape can reach the program namespace.

Self-contained: standard library plus requests (in cuagym/requirements.txt).
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

'''

SETUP_TAIL = '''

def publish(state):
    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def baseline():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    state = probe.json().get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)
    if state.get("newSubmissions") or state.get("newComments"):
        print("SETUP FAILED: baseline already carries agent content", file=sys.stderr)
        raise SystemExit(1)
    return dict(state)


if __name__ == "__main__":
    main()
'''


def setup_subscriptions(task):
    subs = task["setup"]["subscriptions"]
    summary = (
        "Subscribes the current user to %s so that the landing page is a real\n"
        "listing instead of the empty Featured forums shell a pristine seed shows.\n"
        "Neither forum is the forum this task's post belongs in, so nothing about\n"
        "the answer is given away and no part of the rubric is pre-satisfied."
        % " and ".join("f/" + s for s in subs)
    )
    body = (
        'SUBSCRIPTIONS = json.loads(r"""%s""")\n\n\n'
        'def main():\n'
        '    state = baseline()\n'
        '    if state.get("subscriptions"):\n'
        '        print("SETUP FAILED: baseline already has subscriptions", file=sys.stderr)\n'
        '        raise SystemExit(1)\n'
        '    wanted = set(name.lower() for name in SUBSCRIPTIONS)\n'
        '    state["subscriptions"] = list(SUBSCRIPTIONS)\n'
        '    state["forums"] = [\n'
        '        dict(row, subscriberCount=(row.get("subscriberCount") or 0) + 1)\n'
        '        if str(row.get("name", "")).lower() in wanted else row\n'
        '        for row in state["forums"]\n'
        '    ]\n'
        '    publish(state)\n'
    ) % json.dumps(subs, indent=2)
    return SETUP_HEAD.format(task_id=task["id"], summary=summary) + body + SETUP_TAIL


def setup_misplaced(task):
    s = task["setup"]
    record = {
        "id": 200000,
        "forum": s["host_forum"],
        "author": AUTHOR,
        "title": s["post_title"],
        "timestamp": "2023-04-02T09:14:31+00:00",
        "lastActive": "2023-04-02T09:14:31+00:00",
        "ranking": 1680426871,
        "netScore": 1,
        "commentCount": 0,
        "slug": s["slug"],
        "body": s["post_body"],
    }
    summary = (
        "Plants one earlier submission by the current user, mis-filed in f/%s, with\n"
        "every field createSubmission (AppContext.jsx:384) writes: id, forum, author,\n"
        "title, timestamp, lastActive, ranking, netScore, commentCount, slug and body,\n"
        "plus the self-upvote in votes.submissions and the host forum's incremented\n"
        "submissionCount, and nextSubmissionId advanced past it. Its id is the highest\n"
        "on the site and its timestamp is later than the corpus, so it is the first row\n"
        "on the profile overview and on /user/<name>/submissions, both of which page at\n"
        "25. It carries the title the agent must reuse; it is in the wrong forum and\n"
        "has no comment, so it satisfies no part of the rubric."
    ) % s["host_forum"]
    body = (
        'MISPLACED_POST = json.loads(r"""%s""")\n\n\n'
        'def main():\n'
        '    state = baseline()\n'
        '    if (state.get("nextSubmissionId") or 0) != 200000:\n'
        '        print("SETUP FAILED: unexpected nextSubmissionId", file=sys.stderr)\n'
        '        raise SystemExit(1)\n'
        '    host = str(MISPLACED_POST["forum"]).lower()\n'
        '    state["newSubmissions"] = [MISPLACED_POST]\n'
        '    state["nextSubmissionId"] = 200001\n'
        '    votes = dict(state.get("votes") or {})\n'
        '    submission_votes = dict(votes.get("submissions") or {})\n'
        '    submission_votes[str(MISPLACED_POST["id"])] = 1\n'
        '    votes["submissions"] = submission_votes\n'
        '    votes["comments"] = dict(votes.get("comments") or {})\n'
        '    state["votes"] = votes\n'
        '    state["forums"] = [\n'
        '        dict(row, submissionCount=(row.get("submissionCount") or 0) + 1)\n'
        '        if str(row.get("name", "")).lower() == host else row\n'
        '        for row in state["forums"]\n'
        '    ]\n'
        '    publish(state)\n'
    ) % json.dumps(record, indent=2)
    return SETUP_HEAD.format(task_id=task["id"], summary=summary) + body + SETUP_TAIL


def success_criteria(task):
    out = [
        "newSubmissions holds exactly one submission authored by %s%s, and its forum "
        "is %s." % (
            AUTHOR,
            " with an id above the mis-filed baseline post (200000)"
            if (task["setup"] or {}).get("kind") == "misplaced_post" else "",
            task["forum_label"],
        ),
        "That submission's title contains \"%s\" and its body contains \"%s\"."
        % (task["title"], task["body"]),
    ]
    if task["comment"]:
        out.append(
            "newComments holds exactly one comment authored by %s, its submission is "
            "the id of that new post, and its body contains \"%s\"."
            % (AUTHOR, task["comment"])
        )
    return out


def hard_criteria(task):
    if task["difficulty"] != "hard":
        return []
    crit = ["derived_target", "ordering_dependency"]
    if (task["setup"] or {}).get("kind") == "misplaced_post":
        crit.append("cross_page")
    return crit


def injected(task):
    setup = task["setup"]
    if not setup:
        return []
    if setup["kind"] == "subscriptions":
        return [
            "subscriptions = %s (and each of those forum rows' subscriberCount raised "
            "by 1). Turns the landing page from the empty Featured forums shell into a "
            "real subscribed listing; neither forum is the task's target forum."
            % json.dumps(setup["subscriptions"])
        ]
    return [
        "newSubmissions holds one earlier submission by %s (id 200000, f/%s, title "
        "\"%s\", body \"%s\", timestamp 2023-04-02T09:14:31+00:00, ranking 1680426871, "
        "netScore 1, commentCount 0, slug \"%s\"), with votes.submissions[\"200000\"]=1, "
        "f/%s submissionCount +1 and nextSubmissionId advanced to 200001. It is the "
        "record the agent must read the title off; it is in the wrong forum and has no "
        "comment, so it pre-satisfies no component."
        % (AUTHOR, setup["host_forum"], setup["post_title"], setup["post_body"],
           setup["slug"], setup["host_forum"]),
        "Ranking convention: this row simulates a submission the USER made, so ranking "
        "follows createSubmission's epoch-seconds convention (AppContext.jsx:397, "
        "ranking = Math.floor(Date.now()/1000)) rather than the seeded corpus's "
        "ranking == netScore. Verified over src/data/submissions.json: 8011 of 8012 "
        "seeded rows have ranking == netScore, and the single exception is submission 1 "
        "(ranking 1686590745), which is the one createSubmission-shaped row in the seed. "
        "Matching netScore here would be the unfaithful choice. Consequence, and it is "
        "intended: on the host forum's default hot listing (SORT_FIELDS.hot = ranking "
        "DESC, listing.js:33) the row sorts above every seeded post, exactly as "
        "submission 1 does in f/MachineLearning. The task never routes through the host "
        "forum - the agent reads the title off its own profile, which sorts by id and "
        "timestamp - and the instruction already says the old forum is the wrong one, so "
        "a conspicuous position there cannot mislead the forum choice.",
    ]


def authoring_notes(task):
    notes = [
        "Skill chain: R8 (choose, from the 95 forums, the one whose NAME says the "
        "question belongs there) -> A2 (multi-field submit form)%s."
        % (" -> A8/A12 (comment on the submission just created, which cannot exist "
           "before it)" if task["comment"] else ""),
        "Forum matching on this mock can only be done on the forum NAME: "
        "title == description == name for all 95 rows of src/data/forums.json and "
        "sidebar is an opaque t5_* token, so no task here may require reading a "
        "description.",
        "Handlers traced: createSubmission at "
        "hub/websites/webarena_reddit_mock/src/context/AppContext.jsx:384 appends to "
        "newSubmissions via overlay.addSubmission (src/utils/overlay.js:259); "
        "addComment at AppContext.jsx:450 appends to newComments via "
        "overlay.addComment (overlay.js:263).",
        "Click path from /: nav Submit -> #submission_forum select (all 95 forums, "
        "sorted by name) -> #submission_title / #submission_body -> Create submission, "
        "which redirects to /f/<forum>/<id>/<slug>%s. No typed URL is required."
        % (" where the comment textarea and its Post button render "
           "(SubmissionPage.jsx:140-150)" if task["comment"] else ""),
        "Inspirations informed shape only. No benchmark question, entity combination "
        "or reference answer was reused verbatim in the instruction.",
        "Both reward programs read current_state only, never state_diff.",
    ]
    if len(task["forums"]) > 1:
        notes.append(
            "Accepted forum set mirrors the official gold for this subject, which is "
            "itself an OR over the same forums."
        )
    return notes


def write(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def replay_draft(task):
    forum = task["forums"][0]
    lines = [
        '"""Golden replay DRAFT for %s.' % task["id"],
        "",
        "Not executed during authoring. Every step is a click or a form control",
        "reachable from start_path '/'; there is no page.goto after the landing page.",
        '"""',
        "",
        "TARGET_FORUM = %r" % forum,
        "TITLE = %r" % task["title"],
        "BODY = %r" % task["body"],
        "COMMENT = %r" % (task["comment"] or ""),
        "",
        "",
        "def run(page):",
        "    # start_path '/' has already been opened by the harness",
    ]
    if (task["setup"] or {}).get("kind") == "misplaced_post":
        lines += [
            "    # 1. read the mis-filed post's title off my own profile",
            "    page.click('a[href^=\"/user/MarvelsGrantMan136\"]')",
            "    page.click('a:has-text(\"Submissions\")')",
            "    old_title = page.inner_text('article h1 a, .submission__title >> nth=0').strip()",
            "    assert old_title.lower() == TITLE.lower(), old_title",
        ]
    lines += [
        "    # 2. open the submit form from the top navigation",
        "    page.click('a[href^=\"/submit\"]')",
        "    # 3. pick the forum the question actually belongs in",
        "    page.select_option('#submission_forum', label=TARGET_FORUM)",
        "    page.fill('#submission_title', TITLE)",
        "    page.fill('#submission_body', BODY)",
        "    page.click('form button:has-text(\"Create submission\")')",
        "    page.wait_for_url('**/f/%s/**')" % forum,
    ]
    if task["comment"]:
        lines += [
            "    # 4. comment on the post that was just created",
            "    page.fill('form textarea', COMMENT)",
            "    page.click('form button:has-text(\"Post\")')",
            "    page.wait_for_url('**/comment/**')",
        ]
    return "\n".join(lines) + "\n"


index = {"schema_version": 2, "tasks": []}
nemo_rows = []

for task in TASKS:
    d = os.path.join(SITE, task["id"])
    os.makedirs(d, exist_ok=True)

    setup_src = None
    if task["setup"]:
        if task["setup"]["kind"] == "subscriptions":
            setup_src = setup_subscriptions(task)
        else:
            setup_src = setup_misplaced(task)
        write(os.path.join(d, "initial_setup.py"), setup_src)

    write(os.path.join(d, "reward.py"), reward_py(task))
    nemo_src = nemo_reward_py(task)
    write(os.path.join(d, "nemo_reward.py"), nemo_src)

    write(os.path.join(d, "task_instruction.json"), json.dumps({
        "task_id": task["id"],
        "task_instruction": task["instruction"],
        "app_dir": "webarena_reddit_mock",
        "start_path": "/",
        "difficulty": task["difficulty"],
        "success_criteria": success_criteria(task),
    }, indent=2) + "\n")

    metadata = {
        "style": task["style"],
        "difficulty": task["difficulty"],
        "shape": "retrieval_writeback",
        "skills": task["skills"],
        "skill_chain": (
            "read the question's subject -> pick the forum whose name says it "
            "belongs there -> submit the post there"
            + (" -> comment on the post just created" if task["comment"] else "")
        ),
        "official_analogues": [q(i) for i in task["analogues"]],
        "hard_criteria": hard_criteria(task),
        "topic": "forum_choice_post_and_comment",
        "inspiration_ids": ["webarena-%d" % i for i in task["analogues"]],
        "authoring_notes": authoring_notes(task),
    }
    if task["setup"]:
        metadata["injected_preconditions"] = injected(task)

    write(os.path.join(d, "task.json"), json.dumps({
        "schema_version": 2,
        "task_id": task["id"],
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
        "metadata": metadata,
    }, indent=2) + "\n")

    row = {"task_payload": {
        "task_id": task["id"],
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
            "bundle_id": task["id"],
            "app_dir": "webarena_reddit_mock",
            "initial_setup": setup_src,
            "eval_reward_code": nemo_src,
        },
    }}
    write(os.path.join(d, "nemo_task.json"), json.dumps(row, indent=2) + "\n")
    nemo_rows.append(row)

    write(os.path.join(REPLAYS, task["id"] + ".py"), replay_draft(task))
    index["tasks"].append({"task_id": task["id"], "path": task["id"] + "/task.json"})

write(os.path.join(BATCH, "index.json"), json.dumps(index, indent=2) + "\n")
with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
    for row in nemo_rows:
        fh.write(json.dumps(row) + "\n")

print("wrote %d bundles" % len(TASKS))
for task in TASKS:
    words = len(task["instruction"].split())
    print("%-62s %-8s %-6s %2d words" % (
        task["id"], task["style"], task["difficulty"], words))
