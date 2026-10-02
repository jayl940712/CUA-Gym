#!/usr/bin/env python3
"""Builder for batch-6 lane 26 (reddit, R9 -> A1, named own post -> body/url line).

Writes ten bundles under output/tasks/reddit/<task_id>/ plus replay drafts and
the lane's nemo_tasks.jsonl / index.json.  Authoring tool only; no validation.
"""

import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/reddit")
LANE = os.path.join(OUT, "_batches/named_own_post_body_line")
REPLAYS = os.path.join(LANE, "replays")

ME = "MarvelsGrantMan136"

ANALOGUE_731 = ('Edit my post on Nvidia RTX 4090 by adding a line to the body '
                'that says "EDIT: This news aged well"')
ANALOGUE_732 = ('Edit my post on The Night Agent by adding a line to the body '
                'that says "Done watching, pretty cool!"')
ANALOGUE_733 = ('Edit my post on Star Trek Starfleet Academy series by adding a line '
                'to the body that says "Every watch makes me feel like a kid again"')
ANALOGUE_734 = ('Edit my post on Ted Lasso season 3 premiere by adding a line to the '
                'body that says "Done watching. I love the renew!"')
ANALOGUE_735 = ('Edit my post on Lord of the Rings season 2 cast announcement with the '
                'lowest vote count by adding a line to the body that says '
                '"The cast is amazing!"')

COMMON_NOTES = [
    "Post editing is author-only (EditSubmissionPage.jsx:51), so the entity pool is "
    "MarvelsGrantMan136's 46 seeded submissions.",
    "editSubmission (AppContext.jsx:426) routes through patchSubmission "
    "(src/utils/overlay.js:225), which writes submissionEdits[<id>] as the WHOLE "
    "resolved record ({...current, ...updates}), not a field patch.",
    "45 of the 46 own submissions ship with no body key at all, so the rubric is "
    "body == <the required line>, never <original> + <line>.  Submission 1 "
    "('Nvidia RTX 4090') is the single seeded-body exception and is also official "
    "webarena-731, so this lane never touches it.",
    "Every scored condition is a recorded VALUE.  A no-op save of the edit form, or "
    "an unconditional writer such as AccountPage's currentUser.email, earns nothing.",
    "Both reward programs read current_state only and never diff initial_state; "
    "reddit REPLACES on a partial `set`, so state_diff is never consulted.",
    "Grounded in hub/websites/webarena_reddit_mock; nothing under hub/ was modified.",
]

HOST_NOTE = ("The source site is rendered by Submission.jsx:146-148 through "
             "displayHost() (src/utils/format.js:144), which strips a leading 'www.'. "
             "The reward accepts the displayed host and the raw 'www.' host, because "
             "the same value is also readable verbatim in the edit form's URL field; "
             "both spell one site and no other candidate exists.")

TOPCOMMENT_NOTE = ("The first comment on a submission page is the highest-scored "
                   "top-level comment: buildTree (Comment.jsx:23-33) sorts each "
                   "sibling list by netScore DESC, id ASC.")


# --------------------------------------------------------------------------
# The ten tasks.
# --------------------------------------------------------------------------

def body_task(**kw):
    kw["kind"] = "body"
    return kw


TASKS = [
    body_task(
        task_id="named_own_post_body_line_umbrella_academy_source_host_001",
        sub_id=113998,
        title="David Cross Joins the Final Season of 'The Umbrella Academy'",
        forum="television",
        slug="david-cross-joins-the-final-season-of-the-umbrella-academy",
        instruction=(
            "My post about David Cross joining the final season of The Umbrella "
            "Academy needs a credit line. Replace its body with a single line "
            "reading Source: <site>, where <site> is the source site shown on that "
            "post."
        ),
        accepted=["Source: deadline.com"],
        canonical="Source: deadline.com",
        derived="the source site shown on submission 113998 (deadline.com)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the source site displayed on my named Umbrella Academy "
                     "post -> set that post's body to the credit line naming it"),
        analogues=[ANALOGUE_732],
        inspiration=["webarena-732"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[HOST_NOTE,
               "Margin: 113998 is the only submission in the corpus whose title "
               "mentions The Umbrella Academy, and its link host deadline.com is a "
               "single value with no runner-up."],
    ),
    body_task(
        task_id="named_own_post_body_line_sue_baker_obit_source_host_002",
        sub_id=49197,
        title="Former ‘Top Gear’ Presenter and Motoring Journalist Sue Baker Dies at 67",
        forum="television",
        slug="former-top-gear-presenter-and-motoring-journalist-sue-baker",
        instruction=(
            "On my Sue Baker obituary post in f/television, set the body to exactly "
            "one line reading Credit: <site>, replacing <site> with the source site "
            "displayed on that post."
        ),
        accepted=["Credit: theguardian.com", "Credit: www.theguardian.com"],
        canonical="Credit: theguardian.com",
        derived="the source site shown on submission 49197 (theguardian.com)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the source site displayed on my named Sue Baker obituary "
                     "post -> set that post's body to the credit line naming it"),
        analogues=[ANALOGUE_733],
        inspiration=["webarena-733"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[HOST_NOTE,
               "Margin: 'Sue Baker' matches exactly one submission corpus-wide "
               "(49197); its host theguardian.com has no competing value."],
    ),
    body_task(
        task_id="named_own_post_body_line_last_of_us_posters_source_host_003",
        sub_id=49070,
        title="HBO’s “The Last of Us” Character Posters Reveal Nick Offerman, Storm Reid and More",
        forum="television",
        slug="hbo-s-the-last-of-us-character-posters-reveal-nick-offerman",
        instruction=(
            "I want the source attributed on my own post “HBO’s ‘The "
            "Last of Us’ Character Posters Reveal Nick Offerman, Storm Reid and "
            "More” in f/television. Every link post displays the site it links "
            "to next to its title. Open my post, read that site, then edit the post "
            "so its body is exactly one line reading Source: <site>, with <site> "
            "written exactly as the post displays it. Leave the title and the link "
            "itself as they are."
        ),
        accepted=["Source: bloody-disgusting.com"],
        canonical="Source: bloody-disgusting.com",
        derived="the source site shown on submission 49070 (bloody-disgusting.com)",
        style="explicit",
        shape="retrieval_writeback",
        skill_chain=("read the source site displayed on my named Last of Us posters "
                     "post -> set that post's body to the credit line naming it"),
        analogues=[ANALOGUE_734],
        inspiration=["webarena-734"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[HOST_NOTE,
               "Margin: five other submissions match 'Last of Us' but only 49070 is "
               "mine and matches 'Character Posters'; host bloody-disgusting.com "
               "carries no www prefix, so displayed and raw hosts coincide."],
    ),
    body_task(
        task_id="named_own_post_body_line_grogu_short_source_host_004",
        sub_id=49120,
        title="Studio Ghibli and Lucasfilm's 'Zen - Grogu and Dust Bunnies' Arrives on Disney+ Tomorrow, November 12",
        forum="television",
        slug="studio-ghibli-and-lucasfilm-s-zen-grogu-and-dust-bunnies",
        instruction=(
            "My Studio Ghibli 'Zen - Grogu and Dust Bunnies' post should say where "
            "the story came from: make its body exactly one line reading Source: "
            "<site>, using the source site shown on that post."
        ),
        accepted=["Source: ign.com", "Source: www.ign.com"],
        canonical="Source: ign.com",
        derived="the source site shown on submission 49120 (ign.com)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the source site displayed on my named Zen - Grogu post -> "
                     "set that post's body to the credit line naming it"),
        analogues=[ANALOGUE_732],
        inspiration=["webarena-732"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[HOST_NOTE,
               "Margin: 'Grogu' matches exactly one submission corpus-wide (49120); "
               "its host ign.com has no runner-up."],
    ),
    body_task(
        task_id="named_own_post_body_line_flower_moon_top_comment_005",
        sub_id=128382,
        title="Martin Scorsese’s ‘Killers of the Flower Moon’ Will Have World Premiere at Cannes Film Festival",
        forum="movies",
        slug="martin-scorsese-s-killers-of-the-flower-moon-will-have-world",
        instruction=(
            "My Killers of the Flower Moon Cannes premiere post deserves a credit "
            "line for its highest-scored comment: set that post's body to exactly "
            "one line reading Top comment by <username>."
        ),
        accepted=["Top comment by Xenomorph_kills",
                  "Top comment by u/Xenomorph_kills"],
        canonical="Top comment by Xenomorph_kills",
        derived="the author of the highest-scored comment on submission 128382 (Xenomorph_kills)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the author of the top-scored comment on my named Killers "
                     "of the Flower Moon post -> set that post's body to the credit "
                     "line naming them"),
        analogues=[ANALOGUE_733],
        inspiration=["webarena-733"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[TOPCOMMENT_NOTE,
               "Margin: comment 2521048 (Xenomorph_kills, 630) vs the runner-up "
               "top-level comment at 318 - a 312-point gap, no tie."],
    ),
    body_task(
        task_id="named_own_post_body_line_dead_to_me_top_comment_006",
        sub_id=49175,
        title="TVLine Performer of the Week: Christina Applegate in 'Dead to Me'",
        forum="television",
        slug="tvline-performer-of-the-week-christina-applegate-in-dead-to",
        instruction=(
            "On my TVLine Performer of the Week post about Christina Applegate, "
            "replace the body with one line reading Best comment: <username>, naming "
            "whoever wrote the highest-scored comment there."
        ),
        accepted=["Best comment: mikexmachina", "Best comment: u/mikexmachina"],
        canonical="Best comment: mikexmachina",
        derived="the author of the highest-scored comment on submission 49175 (mikexmachina)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the author of the top-scored comment on my named Christina "
                     "Applegate post -> set that post's body to the credit line "
                     "naming them"),
        analogues=[ANALOGUE_734],
        inspiration=["webarena-734"],
        derived_from="own_post_append_edit_tvline_series_retirement_notice_010",
        notes=[TOPCOMMENT_NOTE,
               "Margin: comment 686350 (mikexmachina, 851) vs the runner-up top-level "
               "comment at 545 - a 306-point gap, no tie.",
               "49175 was also touched by batch-5's TVLine retirement task, but there "
               "the body was a fixed sentence given in the instruction; here the body "
               "carries a value that only the comment listing supplies."],
    ),
    body_task(
        task_id="named_own_post_body_line_wilko_johnson_top_comment_007",
        sub_id=49068,
        title="Wilko Johnson, Legendary Guitarist and Actor Who Played Ser Ilyn Payne in ‘Game of Thrones’, Dies at 75",
        forum="television",
        slug="wilko-johnson-legendary-guitarist-and-actor-who-played-ser",
        instruction=(
            "My f/television post about the death of Wilko Johnson, the guitarist who "
            "played Ser Ilyn Payne, drew one comment that scored far above the rest. "
            "Open my post, see who wrote that highest-scored comment, and then edit "
            "the post so its body is exactly one line reading Top comment by "
            "<username>, with <username> replaced by that commenter's name. Do not "
            "change the title or the link."
        ),
        accepted=["Top comment by BordersRanger01", "Top comment by u/BordersRanger01"],
        canonical="Top comment by BordersRanger01",
        derived="the author of the highest-scored comment on submission 49068 (BordersRanger01)",
        style="explicit",
        shape="retrieval_writeback",
        skill_chain=("read the author of the top-scored comment on my named Wilko "
                     "Johnson post -> set that post's body to the credit line naming "
                     "them"),
        analogues=[ANALOGUE_735],
        inspiration=["webarena-735"],
        derived_from="own_post_append_edit_highest_scoring_post_overall_006",
        notes=[TOPCOMMENT_NOTE,
               "Margin: comment 630317 (BordersRanger01, 1179) vs 631391 "
               "(Malcolm_Ten, 894) - a 285-point gap, no tie.",
               "'Wilko' matches exactly one submission corpus-wide (49068)."],
    ),
    body_task(
        task_id="named_own_post_body_line_tokyo_vice_top_comment_008",
        sub_id=49007,
        title="'Tokyo Vice' Season 2 at HBO Max Casts Takayuki Suzuki",
        forum="television",
        slug="tokyo-vice-season-2-at-hbo-max-casts-takayuki-suzuki",
        instruction=(
            "My Tokyo Vice season 2 casting post should credit its best reply: set "
            "the post's body to exactly one line reading Best comment: <username>, "
            "naming whoever wrote the highest-scored comment on it."
        ),
        accepted=["Best comment: SprinklesCharming382",
                  "Best comment: u/SprinklesCharming382"],
        canonical="Best comment: SprinklesCharming382",
        derived="the author of the highest-scored comment on submission 49007 (SprinklesCharming382)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the author of the top-scored comment on my named Tokyo Vice "
                     "post -> set that post's body to the credit line naming them"),
        analogues=[ANALOGUE_732],
        inspiration=["webarena-732"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        notes=[TOPCOMMENT_NOTE,
               "Margin: comment 619749 (SprinklesCharming382, 913) vs the runner-up "
               "top-level comment at 138 - a 775-point gap, no tie.",
               "'Tokyo Vice' matches exactly one submission corpus-wide (49007)."],
    ),
    {
        "kind": "url",
        "task_id": "named_own_post_body_line_secret_invasion_link_fix_009",
        "sub_id": 135185,
        "title": "Marvel's 'Secret Invasion' Premieres June 21 on Disney+",
        "forum": "television",
        "slug": "marvel-s-secret-invasion-premieres-june-21-on-disney",
        "source_id": 135204,
        "expected_url": "https://www.vanityfair.com/hollywood/2023/03/secret-invasion-marvel-exclusive",
        "instruction": (
            "My f/television post \"Marvel's 'Secret Invasion' Premieres June 21 on "
            "Disney+\" links to the Disney+ series page, but I meant to link the same "
            "article I used for my other Secret Invasion post, the Samuel L. Jackson "
            "interview. Find that other post of mine, take the exact address it links "
            "to, and edit the June 21 post so its link points there instead. Leave "
            "its title alone."
        ),
        "derived": "the link address of my other Secret Invasion submission 135204",
        "style": "explicit",
        "shape": "mutation",
        "skill_chain": ("read the link address stored on my named Samuel L. Jackson "
                        "Secret Invasion post -> set the URL field of my June 21 "
                        "Secret Invasion post to it"),
        "analogues": [ANALOGUE_731],
        "inspiration": ["webarena-731"],
        "derived_from": None,
        "start_path": "/f/television/135185/marvel-s-secret-invasion-premieres-june-21-on-disney",
        "notes": [
            "A1 here is the URL field rather than the body: EditSubmissionPage.jsx:57 "
            "renders it for every non-image submission and validates it against "
            "^https?://\\S+$.",
            "Exactly two submissions corpus-wide match 'Secret Invasion' (135185, "
            "135204) and both are mine, so the source record is unambiguous; the "
            "target link (disneyplus.com) and the source link (vanityfair.com) are "
            "different values, so an agent that skips the lookup cannot land on it.",
            "start_path is the target submission's own permalink: the instruction "
            "names one specific record out of 8,012, which TASK4 S5.1 allows, and the "
            "source post is still reached by clicking (author link -> "
            "/user/MarvelsGrantMan136 -> that post).",
            "The reward normalises a trailing slash and surrounding whitespace only.",
        ],
    },
    body_task(
        task_id="named_own_post_body_line_orlando_brown_top_comment_010",
        sub_id=70734,
        title="‘That’s So Raven,‘ ‘Family Matters’ Star Orlando Brown Arrested for Domestic Violence",
        forum="television",
        slug="that-s-so-raven-family-matters-star-orlando-brown-arrested",
        instruction=(
            "My post about Orlando Brown's arrest has one comment scoring well above "
            "the others. Set that post's body to exactly one line reading Top comment "
            "by <username>, naming whoever wrote it."
        ),
        accepted=["Top comment by callmemacready", "Top comment by u/callmemacready"],
        canonical="Top comment by callmemacready",
        derived="the author of the highest-scored comment on submission 70734 after setup (callmemacready)",
        style="terse",
        shape="retrieval_writeback",
        skill_chain=("read the author of the top-scored comment on my named Orlando "
                     "Brown post -> set that post's body to the credit line naming "
                     "them"),
        analogues=[ANALOGUE_735],
        inspiration=["webarena-735"],
        derived_from="own_post_append_edit_creed_iii_poster_003",
        setup=True,
        injected=[
            "newComments = [comment 3000000 by callmemacready on submission 70734, "
            "netScore 641, top-level] and nextCommentId = 3000001. The pristine seed's "
            "top comment there is Billbrandicus at 390, so the injection MOVES the "
            "answer off the seed value: an agent that memorised the corpus writes the "
            "wrong username. Margin 641 vs 390 = 251, no tie.",
            "The injected record carries exactly the fields the seeded corpus uses "
            "(id, submission, author, body, netScore, timestamp, userFlag) and no "
            "parent key, which is how Comment.jsx:26 recognises a top-level comment. "
            "No votes entry is added, because the comment is another user's.",
            "commentCount is deliberately NOT bumped: submission 70734 already "
            "advertises 127 comments while the corpus holds 5, so leaving the counter "
            "alone is consistent with the seed and keeps the graded key "
            "submissionEdits['70734'] absent at t=0.",
        ],
        notes=[TOPCOMMENT_NOTE,
               "Margin after setup: injected comment 3000000 (callmemacready, 641) vs "
               "1025175 (Billbrandicus, 390) - a 251-point gap, no tie.",
               "'Orlando Brown' matches exactly one submission corpus-wide (70734)."],
    ),
]


# --------------------------------------------------------------------------
# File templates.
# --------------------------------------------------------------------------

BODY_RUBRIC = '''
ME = "MarvelsGrantMan136"

# Every value the rubric compares against, inlined as a raw-string JSON literal
# so the Python parser cannot rewrite an escape before json.loads sees it.
FIXTURE = json.loads(r"""{fixture}""")

TARGET_ID = str(FIXTURE["target_id"])
TARGET_TITLE = FIXTURE["target_title"]
ACCEPTED_BODIES = FIXTURE["accepted_bodies"]

# Submission 1 ("Nvidia RTX 4090") is the only one of my 46 seeded posts that
# already ships with a body, so it is never counted as a post that "carries the
# line" by accident.
SEEDED_BODY_ID = "1"

COMPONENT_WEIGHTS = {{
    "derived_line_on_target": 0.7,
    "line_confined_to_that_post": 0.3,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def _edits(state):
    value = state.get("submissionEdits") if isinstance(state, dict) else None
    return value if isinstance(value, dict) else {{}}


def _norm(value):
    if not isinstance(value, str):
        return ""
    return value.replace("\\r\\n", "\\n").replace("\\r", "\\n").strip()


def _deleted_ids(state):
    value = state.get("deletedSubmissions") if isinstance(state, dict) else None
    rows = value if isinstance(value, list) else []
    return set(str(row) for row in rows)


def _record(state, sid):
    row = _edits(state).get(str(sid))
    return row if isinstance(row, dict) else None


def _target_reads_the_line(state):
    """The named post now stores exactly the derived credit line, under its own title."""
    row = _record(state, TARGET_ID)
    if row is None:
        return False
    if TARGET_ID in _deleted_ids(state):
        return False
    if _norm(row.get("author")) != ME:
        return False
    if _norm(row.get("title")) != TARGET_TITLE:
        return False
    return _norm(row.get("body")) in ACCEPTED_BODIES


def _ids_carrying_the_line(state):
    """Every one of my submissions whose stored body is exactly the credit line."""
    found = set()
    for key, row in _edits(state).items():
        if not isinstance(row, dict):
            continue
        if str(key) == SEEDED_BODY_ID:
            continue
        if _norm(row.get("author")) != ME:
            continue
        if _norm(row.get("body")) in ACCEPTED_BODIES:
            found.add(str(key))
    return found


def score_checks(state):
    return {{
        "derived_line_on_target": _target_reads_the_line(state),
        "line_confined_to_that_post": _ids_carrying_the_line(state) == set([TARGET_ID]),
    }}


def _details(state, name):
    row = _record(state, TARGET_ID) or {{}}
    return (
        "component=" + name
        + " | target=" + TARGET_ID
        + " | stored body=" + json.dumps(_norm(row.get("body")), ensure_ascii=False)
        + " | stored title=" + json.dumps(_norm(row.get("title")), ensure_ascii=False)
        + " | ids carrying the line=" + json.dumps(sorted(_ids_carrying_the_line(state)))
    )
'''

URL_RUBRIC = '''
ME = "MarvelsGrantMan136"

# Every value the rubric compares against, inlined as a raw-string JSON literal
# so the Python parser cannot rewrite an escape before json.loads sees it.
FIXTURE = json.loads(r"""{fixture}""")

TARGET_ID = str(FIXTURE["target_id"])
TARGET_TITLE = FIXTURE["target_title"]
EXPECTED_URL = FIXTURE["expected_url"]

COMPONENT_WEIGHTS = {{
    "target_link_now_points_to_the_other_article": 1.0,
}}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def _edits(state):
    value = state.get("submissionEdits") if isinstance(state, dict) else None
    return value if isinstance(value, dict) else {{}}


def _norm(value):
    if not isinstance(value, str):
        return ""
    return value.replace("\\r\\n", "\\n").replace("\\r", "\\n").strip()


def _norm_url(value):
    text = _norm(value)
    while text.endswith("/"):
        text = text[:-1]
    return text


def _deleted_ids(state):
    value = state.get("deletedSubmissions") if isinstance(state, dict) else None
    rows = value if isinstance(value, list) else []
    return set(str(row) for row in rows)


def _record(state, sid):
    row = _edits(state).get(str(sid))
    return row if isinstance(row, dict) else None


def _target_points_at_expected(state):
    """The named post now stores the other article's address, under its own title."""
    row = _record(state, TARGET_ID)
    if row is None:
        return False
    if TARGET_ID in _deleted_ids(state):
        return False
    if _norm(row.get("author")) != ME:
        return False
    if _norm(row.get("title")) != TARGET_TITLE:
        return False
    return _norm_url(row.get("url")) == _norm_url(EXPECTED_URL)


def score_checks(state):
    return {{
        "target_link_now_points_to_the_other_article": _target_points_at_expected(state),
    }}


def _details(state, name):
    row = _record(state, TARGET_ID) or {{}}
    return (
        "component=" + name
        + " | target=" + TARGET_ID
        + " | stored url=" + json.dumps(_norm(row.get("url")), ensure_ascii=False)
        + " | stored title=" + json.dumps(_norm(row.get("title")), ensure_ascii=False)
        + " | expected url=" + json.dumps(EXPECTED_URL)
    )
'''

REWARD_TAIL = '''

def _current_state(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    if isinstance(apps, dict):
        for key in ("reddit", "webarena_reddit_mock"):
            app = apps.get(key)
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
        for app in apps.values():
            if isinstance(app, dict) and isinstance(app.get("current_state"), dict):
                return app["current_state"]
    return {}


def evaluate(evidence):
    state = _current_state(evidence)
    checks = score_checks(state)
    components = []
    total = 0.0
    for name in COMPONENT_WEIGHTS:
        earned = COMPONENT_WEIGHTS[name] if checks.get(name) else 0.0
        total += earned
        components.append(
            {
                "name": name,
                "score": round(earned, 6),
                "details": _details(state, name),
            }
        )
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
    print(
        "COMPONENTS: "
        + json.dumps(dict((k, bool(v)) for k, v in checks.items()), sort_keys=True)
    )
    print("DETAILS: " + _details(state, "all"))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''


SETUP_010 = '''"""NeMo-Gym setup program for named_own_post_body_line_orlando_brown_top_comment_010.

Plants one top-level comment on submission 70734 ('That's So Raven,' 'Family
Matters' Star Orlando Brown Arrested for Domestic Violence) scoring 641, above
the pristine seed's top comment there (Billbrandicus, 390).  That MOVES the
answer the task derives: an agent that memorised the corpus credits the wrong
user, and only reading the live comment listing gets it right.

The injected record carries exactly the fields the seeded corpus uses and no
`parent` key, which is how Comment.jsx:26 treats a comment as top-level, and
`nextCommentId` advances the way addComment (AppContext.jsx) advances it.
`commentCount` is deliberately left alone: 70734 already advertises 127
comments over a 5-row corpus, so bumping it would be the odd change, and the
graded key submissionEdits["70734"] must not exist at t=0.

Reads the pristine baseline from GET /go?sid=, replaces the whole top-level
session document, and republishes it with the "set" action -- reddit REPLACES
on a partial set, so a one-key post would leave the reward reading an almost
empty document.

Self-contained: standard library plus requests.
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

INJECTED_COMMENTS = json.loads(r"""[
  {
    "id": 3000000,
    "submission": 70734,
    "author": "callmemacready",
    "body": "Grew up watching him on That's So Raven. Genuinely hope he gets real help this time, not another news cycle.",
    "netScore": 641,
    "timestamp": "2022-12-23T18:02:11+00:00",
    "userFlag": "t1_j1e9k2m"
  }
]""")

NEXT_COMMENT_ID = 3000001


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    baseline = probe.json().get("initial_state")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)
    if baseline.get("newComments"):
        print("SETUP FAILED: baseline already carries agent comments", file=sys.stderr)
        raise SystemExit(1)
    if baseline.get("submissionEdits"):
        print("SETUP FAILED: baseline already carries submission edits", file=sys.stderr)
        raise SystemExit(1)

    state = dict(baseline)
    state["newComments"] = json.loads(json.dumps(INJECTED_COMMENTS))
    state["nextCommentId"] = NEXT_COMMENT_ID

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
    current = payload.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: no current state after set", file=sys.stderr)
        raise SystemExit(1)
    planted = current.get("newComments")
    if not isinstance(planted, list) or len(planted) != 1:
        print("SETUP FAILED: injected comment did not stick", file=sys.stderr)
        raise SystemExit(1)
    if planted[0].get("author") != "callmemacready" or planted[0].get("netScore") != 641:
        print("SETUP FAILED: injected comment came back altered", file=sys.stderr)
        raise SystemExit(1)
    if current.get("submissionEdits"):
        print("SETUP FAILED: setup must not pre-write submissionEdits", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''


def reward_source(task):
    if task["kind"] == "body":
        fixture = json.dumps(
            {
                "target_id": task["sub_id"],
                "target_title": task["title"],
                "accepted_bodies": task["accepted"],
            },
            indent=2,
            ensure_ascii=False,
        )
        rubric = BODY_RUBRIC.format(fixture=fixture)
    else:
        fixture = json.dumps(
            {
                "target_id": task["sub_id"],
                "target_title": task["title"],
                "expected_url": task["expected_url"],
            },
            indent=2,
            ensure_ascii=False,
        )
        rubric = URL_RUBRIC.format(fixture=fixture)

    head = (
        '"""Deterministic reward for %s.\n\n'
        "%s\n\n"
        "Scored strictly off `current_state`; nothing is diffed against\n"
        "`initial_state`, and no component pays for something being left alone --\n"
        "every one compares a recorded value, so a no-op save of the edit form\n"
        'scores nothing.\n"""\n\nimport json\n'
        % (task["task_id"], task["skill_chain"])
    )
    return head + rubric + REWARD_TAIL


def nemo_reward_source(task):
    if task["kind"] == "body":
        fixture = json.dumps(
            {
                "target_id": task["sub_id"],
                "target_title": task["title"],
                "accepted_bodies": task["accepted"],
            },
            indent=2,
            ensure_ascii=False,
        )
        rubric = BODY_RUBRIC.format(fixture=fixture)
    else:
        fixture = json.dumps(
            {
                "target_id": task["sub_id"],
                "target_title": task["title"],
                "expected_url": task["expected_url"],
            },
            indent=2,
            ensure_ascii=False,
        )
        rubric = URL_RUBRIC.format(fixture=fixture)

    head = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Implements the same rubric as reward.py, reading `current_state` from\n"
        "GET /go?sid=... instead of a frozen evidence bundle, and printing\n"
        "`REWARD: <float>` on every output path including the error path.\n\n"
        'Self-contained: standard library plus `requests`.\n"""\n\n'
        "import json\n"
        "import sys\n\n"
        "import requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"\n'
        % task["task_id"]
    )
    return head + rubric + NEMO_TAIL


def success_criteria(task):
    if task["kind"] == "body":
        return [
            'submissionEdits["%d"] exists, its author is MarvelsGrantMan136, its title '
            "is still exactly %s, and its body is exactly %s (the derived value is %s)."
            % (task["sub_id"], json.dumps(task["title"], ensure_ascii=False),
               json.dumps(task["canonical"], ensure_ascii=False), task["derived"]),
            "Submission %d is not listed in deletedSubmissions." % task["sub_id"],
            "The set of my submissions whose stored body is that credit line is exactly "
            "{%d} - it landed on that post and on no other." % task["sub_id"],
        ]
    return [
        'submissionEdits["%d"] exists, its author is MarvelsGrantMan136, its title is '
        "still exactly %s, and its url is exactly %s (ignoring a trailing slash)."
        % (task["sub_id"], json.dumps(task["title"], ensure_ascii=False),
           json.dumps(task["expected_url"])),
        "Submission %d is not listed in deletedSubmissions." % task["sub_id"],
    ]


def build(task):
    tid = task["task_id"]
    d = os.path.join(OUT, tid)
    os.makedirs(d, exist_ok=True)
    start_path = task.get("start_path", "/")

    instr = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": "webarena_reddit_mock",
        "start_path": start_path,
        "difficulty": "medium",
        "success_criteria": success_criteria(task),
    }
    with open(os.path.join(d, "task_instruction.json"), "w") as fh:
        json.dump(instr, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [
            {
                "name": "webarena_reddit_mock",
                "source_name": "reddit",
                "base_url_env": "CUA_GYM_WEBARENA_REDDIT_URL",
                "start_path": start_path,
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
            "shape": task["shape"],
            "skills": ["R9", "A1"],
            "skill_chain": task["skill_chain"],
            "derived_from": task["derived_from"],
            "official_analogues": task["analogues"],
            "inspiration_ids": task["inspiration"],
            "lane": "named_own_post_body_line",
            "topic": ("attribute lookup on one of my own reddit submissions, then a "
                      "single-field edit of that submission"),
            "authoring_notes": task["notes"] + COMMON_NOTES,
            "injected_preconditions": task.get("injected", []),
        },
    }
    with open(os.path.join(d, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    with open(os.path.join(d, "reward.py"), "w") as fh:
        fh.write(reward_source(task))
    nemo_code = nemo_reward_source(task)
    with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
        fh.write(nemo_code)

    setup_code = None
    if task.get("setup"):
        setup_code = SETUP_010
        with open(os.path.join(d, "initial_setup.py"), "w") as fh:
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
                "eval_reward_code": nemo_code,
            },
        }
    }
    with open(os.path.join(d, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return row


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    rows = []
    for task in TASKS:
        rows.append(build(task))
    with open(os.path.join(LANE, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    index = {
        "schema_version": 2,
        "tasks": [
            {"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]}
            for t in TASKS
        ],
    }
    with open(os.path.join(LANE, "index.json"), "w") as fh:
        json.dump(index, fh, indent=2)
        fh.write("\n")
    print("wrote %d bundles" % len(rows))


if __name__ == "__main__":
    main()
