#!/usr/bin/env python3
"""Batch-5 lane 10 author script - gitlab `stale_review_nudge` (R5 -> R4 -> A8).

Writes ten bundles under output/tasks/gitlab/<task_id>/ plus the batch folder
(GENERATION.md, index.json, replays/). Pure file emission; runs no validation.
"""
import json
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
SITE = ROOT / "output" / "tasks" / "gitlab"
BATCH = SITE / "_batches" / "stale_review_nudge"
REPLAYS = BATCH / "replays"

APP_DIR = "webarena_gitlab_mock"
URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_GITLAB_URL__"

HUB_COMMIT_NOTE = (
    "Grounded in hub/websites/webarena_gitlab_mock as served (dist/ built "
    "2026-08-17); every id below was read out of src/data/*.json."
)

ANALOGUE_ASSIGNED = "Go to the merge requests assigned to me"
ANALOGUE_REVIEW = "Go to the merge requests requiring my review"
ANALOGUE_COND = (
    'Reply on the merge request assigned to me for verification functions: if the last '
    'comment is from the author, reply "Thank you"; otherwise tag the author (e.g., @user) '
    'as a reminder.'
)
ANALOGUE_POST_LGTM = (
    'Post "lgtm" for the merge request related to semantic HTML post in '
    'a11yproject/a11yproject.com project'
)
ANALOGUE_POST_OCTO = (
    'Post "Thanks, working on reviews" for the merge request related to octovisuals page '
    'in primer/design project'
)
ANALOGUE_POST_FOCUS = (
    'Post "close because non reproducible" for the merge request related to focus edge '
    'cases in a11yproject/a11yproject.com project'
)

# ---------------------------------------------------------------------------
# The shared state fixture every initial_setup.py posts (createInitialData()).
# ---------------------------------------------------------------------------

SETUP_PREAMBLE = '''"""NeMo-Gym setup program for {task_id}.

{summary}

Self-contained: standard library plus `requests` (already in
cuagym/requirements.txt). Posts the FULL createInitialData() document so that
`initial_state` and `current_state` agree immediately after the set.
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "{url}"

BASE_STATE = json.loads(r"""
{{
  "currentUser": {{"id": 2330, "username": "byteblaze", "name": "Byte Blaze",
                  "email": "ericwbailey@fakegithub.com", "state": "active",
                  "created_at": "2023-03-23 07:30:04.033203", "location": "Boston, MA",
                  "organization": "@github ",
                  "bio": "Inclusive design and accessibility advocate. Accessibility and design systems wonk for @primer.",
                  "followers": 2, "following": 3, "feed_token": "TMN_bBn9Z48qVbUFZV45",
                  "status": null}},
  "snippets": [],
  "repo": {{"fileOverlay": {{}}, "treeOverlay": {{}}, "commitOverlay": {{}},
           "branchOverlay": {{}}, "tagOverlay": {{}}, "branchDeletions": {{}},
           "tagDeletions": {{}}, "forkOrigin": {{}}}},
  "ui": {{"notificationLevels": {{}}, "sidebarCollapsed": false, "dismissedAlerts": [],
         "preferences": {{"colorScheme": "light", "syntaxTheme": "white"}},
         "projectSettings": {{}}}},
  "nextIds": {{"project": 194, "group": 7, "issue": 83821, "mr": 139278, "note": 310827,
              "label": 1927, "milestone": 590, "member": 206}}
}}
""")

OVERLAY_TRIPLES = [
    ("newUsers", "userEdits", "deletedUsers"),
    ("newProjects", "projectEdits", "deletedProjects"),
    ("newGroups", "groupEdits", "deletedGroups"),
    ("newIssues", "issueEdits", "deletedIssues"),
    ("newMergeRequests", "mergeRequestEdits", "deletedMergeRequests"),
    ("newNotes", "noteEdits", "deletedNotes"),
    ("newLabels", "labelEdits", "deletedLabels"),
    ("newMilestones", "milestoneEdits", "deletedMilestones"),
    ("newMembers", "memberEdits", "deletedMembers"),
    ("newTodos", "todoEdits", "deletedTodos"),
    ("newStars", "starEdits", "deletedStars"),
    ("newFollows", "followEdits", "deletedFollows"),
]

INJECTION = json.loads(r"""
{injection}
""")


def build_state():
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_TRIPLES:
        state[created] = []
        state[edits] = {{}}
        state[deleted] = []
    for key, value in INJECTION.items():
        state[key] = value
    return state


def publish(state):
    response = requests.post(BASE_URL + "/post?sid=" + SID,
                             json={{"action": "set", "state": state}}, timeout=30)
    response.raise_for_status()
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    publish(build_state())


main()
'''


# ---------------------------------------------------------------------------
# Reward bodies. `RUBRIC` is shared verbatim by reward.py and nemo_reward.py.
# ---------------------------------------------------------------------------

READERS = '''

# --------------------------------------------------------------------------
# Readers over webarena_gitlab_mock persisted state (SCHEMA.md).
# Only `current_state` is ever inspected, and only user-visible records:
# NotesTimeline.postComment appends the comment to `newNotes`.
# --------------------------------------------------------------------------

CURRENT_USER_ID = 2330


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _norm(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip().lower()


def _my_mr_notes(state):
    """Every merge-request comment `byteblaze` posted this session."""
    out = []
    for note in _list(_dict(state).get("newNotes")):
        if not isinstance(note, dict):
            continue
        if note.get("noteable_type") != "MergeRequest":
            continue
        if str(note.get("author_id")) != str(CURRENT_USER_ID):
            continue
        out.append(note)
    return out


def _notes_on(state, mr_id):
    return [n for n in _my_mr_notes(state) if str(n.get("noteable_id")) == str(mr_id)]


def _commented_mr_ids(state):
    return sorted({str(n.get("noteable_id")) for n in _my_mr_notes(state)})


def _bodies_on(state, mr_id):
    return [_norm(n.get("body")) for n in _notes_on(state, mr_id)]


def _any_body(state, mr_id, needles, forbidden=()):
    for body in _bodies_on(state, mr_id):
        if all(_norm(n) in body for n in needles) and not any(_norm(f) in body for f in forbidden):
            return True
    return False


def _build(checks, details):
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = bool(checks.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": details.get(name, ""),
        })
    return components


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
'''

LOCAL_TAIL = '''

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

NEMO_TAIL = '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''


def single_target_rubric(mr_id, mr_label, phrase, mention, forbidden, names):
    """Rubric for the nine one-comment tasks."""
    posted, worded, exact = names
    weights = {posted: 0.4, worded: 0.3, exact: 0.3}
    src = [
        "COMPONENT_WEIGHTS = {",
        '    "%s": 0.4,' % posted,
        '    "%s": 0.3,' % worded,
        '    "%s": 0.3,' % exact,
        "}",
        "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9",
        "",
        "TARGET_MR_ID = %d          # %s" % (mr_id, mr_label),
        "REQUIRED_PHRASE = %r" % phrase,
        "REQUIRED_MENTION = %r" % mention,
        "FORBIDDEN = %r" % (tuple(forbidden),),
        "",
        "",
        "def score_state(state):",
        "    posted = _notes_on(state, TARGET_MR_ID)",
        "    commented = _commented_mr_ids(state)",
        "    needles = [REQUIRED_PHRASE]",
        "    if REQUIRED_MENTION:",
        "        needles.append(REQUIRED_MENTION)",
        "    checks = {",
        '        "%s": bool(posted),' % posted,
        '        "%s": _any_body(state, TARGET_MR_ID, needles, FORBIDDEN),' % worded,
        '        "%s": commented == [str(TARGET_MR_ID)],' % exact,
        "    }",
        "    details = {",
        '        "%s": "notes byteblaze posted on merge request %%d == %%r" %% (TARGET_MR_ID, _bodies_on(state, TARGET_MR_ID)),'
        % posted,
        '        "%s": "required %%r + %%r, forbidden %%r; bodies == %%r" %% (REQUIRED_PHRASE, REQUIRED_MENTION, FORBIDDEN, _bodies_on(state, TARGET_MR_ID)),'
        % worded,
        '        "%s": "merge requests byteblaze commented on == %%r, expected [%%r]" %% (commented, str(TARGET_MR_ID)),'
        % exact,
        "    }",
        "    return _build(checks, details)",
    ]
    return weights, "\n".join(src)


def pair_target_rubric(pairs, phrase, names):
    """Rubric for the two-comment task."""
    first, second, exact = names
    weights = {first: 0.3, second: 0.3, exact: 0.4}
    src = [
        "COMPONENT_WEIGHTS = {",
        '    "%s": 0.3,' % first,
        '    "%s": 0.3,' % second,
        '    "%s": 0.4,' % exact,
        "}",
        "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9",
        "",
        "TARGETS = [",
    ]
    for mr_id, mention, label in pairs:
        src.append("    (%d, %r),   # %s" % (mr_id, mention, label))
    src += [
        "]",
        "REQUIRED_PHRASE = %r" % phrase,
        "",
        "",
        "def score_state(state):",
        "    commented = _commented_mr_ids(state)",
        "    ok = []",
        "    for mr_id, mention in TARGETS:",
        "        ok.append(_any_body(state, mr_id, [REQUIRED_PHRASE, mention]))",
        "    checks = {",
        '        "%s": ok[0],' % first,
        '        "%s": ok[1],' % second,
        '        "%s": commented == sorted(str(t[0]) for t in TARGETS),' % exact,
        "    }",
        "    details = {",
        '        "%s": "bodies on %%d == %%r" %% (TARGETS[0][0], _bodies_on(state, TARGETS[0][0])),' % first,
        '        "%s": "bodies on %%d == %%r" %% (TARGETS[1][0], _bodies_on(state, TARGETS[1][0])),' % second,
        '        "%s": "merge requests byteblaze commented on == %%r, expected %%r" %% (commented, sorted(str(t[0]) for t in TARGETS)),'
        % exact,
        "    }",
        "    return _build(checks, details)",
    ]
    return weights, "\n".join(src)


def reward_files(task_id, docstring, rubric_src):
    local = '"""%s\n"""\n\n%s\n%s%s' % (docstring, rubric_src, READERS, LOCAL_TAIL)
    nemo_head = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Same rubric as reward.py, read from GET /go?sid=... instead of a frozen\n"
        "evidence bundle. Prints REWARD: <float> on every output path.\n\n"
        "Self-contained: standard library plus `requests`.\n"
        '"""\n'
        "import sys\n\n"
        "import requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n\n' % (task_id, URL_PLACEHOLDER)
    )
    nemo = "%s\n%s\n%s%s" % (nemo_head, rubric_src, READERS, NEMO_TAIL)
    return local, nemo


# ---------------------------------------------------------------------------
# The ten tasks.
# ---------------------------------------------------------------------------

P = "stale_review_nudge_"

NOTE_INJECT_005 = {
    "newNotes": [
        {
            "id": 900101,
            "noteable_type": "MergeRequest",
            "noteable_id": 72551,
            "project_id": 174,
            "author_id": 2328,
            "body": "Thanks for taking the time on all of those suggestions - I have pushed every one of them, so this should be ready for another look whenever you get a moment.",
            "system": False,
            "discussion_id": "seed-72551-followup",
            "type": None,
            "created_at": "2022-10-05 08:30:12",
            "updated_at": "2022-10-05 08:30:12",
            "resolved_at": None,
            "resolved_by_id": None,
        }
    ]
}

NOTE_INJECT_006 = {
    "newNotes": [
        {
            "id": 900201,
            "noteable_type": "MergeRequest",
            "noteable_id": 72409,
            "project_id": 174,
            "author_id": 2332,
            "body": "Coming back to this one - the WCAG level column still needs a decision before it can be merged. Could we settle that this week?",
            "system": False,
            "discussion_id": "seed-72409-followup",
            "type": None,
            "created_at": "2023-03-29 10:12:44",
            "updated_at": "2023-03-29 10:12:44",
            "resolved_at": None,
            "resolved_by_id": None,
        }
    ]
}

MR_139245 = {
    "assignee_ids": [],
    "author_id": 2368,
    "created_at": "2023-03-23 14:46:57",
    "draft": False,
    "id": 139245,
    "iid": 450,
    "label_ids": [],
    "merge_status": "can_be_merged",
    "merged_at": None,
    "merged_by_id": None,
    "milestone_id": None,
    "project_id": 180,
    "reviewer_ids": [],
    "source_branch": "octovisuals-page",
    "source_project_id": 180,
    "squash": False,
    "state": "opened",
    "target_branch": "main",
    "title": "Octovisuals Page",
    "updated_at": "2021-08-11 09:26:14",
    "user_notes_count": 2,
    "description": (
        "### Summary\r\nCreating a page to link out to our internal Octovisuals docs. "
        "The agreed upon IA was documented in the Octovisuals channel in slack but "
        "looks like the following:\r\n\r\n![image](/uploads/"
        "0ab14c09d786170defec1d6df29c65cb/"
        "227240840-7b16971c-4047-42a1-81b4-4ba23680db6d.png)\r\n"
    ),
}

MR_EDIT_INJECT_008 = {"mergeRequestEdits": {"139245": MR_139245}}


TASKS = [
    # ---------------------------------------------------------------- 001
    dict(
        n="001",
        slug="assigned_open_stalest_nudge",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="filter the dashboard merge-request list to assigned-to-me and Open -> "
              "sort by Updated date oldest-first and take row one -> comment there "
              "@-mentioning that merge request's author",
        analogues=[ANALOGUE_ASSIGNED, ANALOGUE_POST_LGTM],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "Of the merge requests assigned to me that are still open, one has gone "
            'longest without an update. Comment there with "Any update on this?" and '
            "@-mention whoever opened it."
        ),
        mr_id=138783,
        mr_label="byteblaze/a11y-webring.club!40 'Add verification functions'",
        phrase="Any update on this?",
        mention="@davepgreene",
        forbidden=(),
        names=("nudge_comment_posted_on_stalest_assigned_mr",
               "nudge_comment_names_the_mr_author",
               "comment_set_is_exactly_the_stalest_assigned_mr"),
        criteria=[
            "newNotes holds a byteblaze comment whose noteable_type is MergeRequest and "
            "noteable_id is 138783 (byteblaze/a11y-webring.club!40).",
            'That comment body contains "Any update on this?" and "@davepgreene".',
            "138783 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "Assigned-to-me AND state=opened is exactly three merge requests: "
            "a11yproject/a11yproject.com!1270 (updated 2023-03-27 23:21:22.709901), "
            "!1485 (23:19:39.525795) and byteblaze/a11y-webring.club!40 "
            "(23:14:48.4197). Oldest-updated is !40, id 138783.",
            "Margin over the runner-up is 4m51s of updated_at; hooks.js sortIssuables "
            "'updated_asc' orders on the exact timestamp, so the list position is "
            "deterministic even though both rows render as the same relative TimeAgo.",
            "Author of !40 is davepgreene (user 2365), so the derived mention is "
            "@davepgreene. It is never stated in the instruction.",
            "Posting a comment does not rewrite updated_at (NotesTimeline.postComment "
            "only bumps user_notes_count), so the action cannot destroy its own "
            "retrieval premise.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 002
    dict(
        n="002",
        slug="review_queue_stalest_bump",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="filter the dashboard merge-request list to reviewer=me and Open -> sort "
              "by Updated date oldest-first and take row one -> comment there "
              "@-mentioning the merge request's author",
        analogues=[ANALOGUE_REVIEW, ANALOGUE_POST_LGTM],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "Among the merge requests waiting on my review, the still-open one that has "
            'gone longest without an update needs chasing. Post "Bumping this for '
            'review." there and @-mention its author.'
        ),
        mr_id=72551,
        mr_label="a11yproject/a11yproject.com!1472 'How to: Article how to make an accessible nav'",
        phrase="Bumping this for review.",
        mention="@jimbateson",
        forbidden=(),
        names=("bump_comment_posted_on_stalest_review_request",
               "bump_comment_names_the_mr_author",
               "comment_set_is_exactly_the_stalest_review_request"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72551 "
            "(a11yproject/a11yproject.com!1472).",
            'That comment body contains "Bumping this for review." and "@jimbateson".',
            "72551 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "reviewer_ids contains 2330 on 159 merge requests, of which exactly five "
            "are opened: !1472 (2023-03-23 07:43:13.800501), !1490 (08:20:57.781405), "
            "!1265 (08:46:44.486898), !1280 (08:46:54.471362) and !1270 "
            "(2023-03-27 23:21:22.709901).",
            "Oldest-updated is !1472, id 72551, margin 37m44s over !1490.",
            "Author of !1472 is jimbateson (user 2328) -> derived mention @jimbateson.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 003
    dict(
        n="003",
        slug="review_queue_freshest_pickup",
        style="explicit",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="filter the dashboard merge-request list to reviewer=me and Open -> sort "
              "by Updated date newest-first and take row one -> comment there "
              "@-mentioning the merge request's author",
        analogues=[ANALOGUE_REVIEW, ANALOGUE_POST_LGTM],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "I want to restart my review work with whatever moved most recently. Open "
            "the dashboard list of merge requests that are waiting for my review, keep "
            "the Open state filter, and sort by Updated date with the most recently "
            "updated first. Open the merge request sitting at the top of that list and "
            'post a single comment on it reading "Picking this up next." that also '
            "@-mentions, by GitLab handle, the person who opened that merge request. "
            "Leave every other merge request in the queue without a comment."
        ),
        mr_id=72409,
        mr_label="a11yproject/a11yproject.com!1270 'feat: add WCAG levels'",
        phrase="Picking this up next.",
        mention="@aguscha333",
        forbidden=(),
        names=("pickup_comment_posted_on_freshest_review_request",
               "pickup_comment_names_the_mr_author",
               "comment_set_is_exactly_the_freshest_review_request"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72409 "
            "(a11yproject/a11yproject.com!1270).",
            'That comment body contains "Picking this up next." and "@aguscha333".',
            "72409 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "Most recently updated of the five open review requests is !1270 "
            "(2023-03-27 23:21:22.709901); the runner-up !1280 is 2023-03-23 "
            "08:46:54.471362, a margin of 4 days 14 hours.",
            "Author of !1270 is aguscha333 (user 2331) -> derived mention @aguscha333. "
            "Note the MR was later reassigned by Roshanjossey, so 'who opened it' and "
            "'who touched it last' are genuinely different people here.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 004
    dict(
        n="004",
        slug="review_queue_quietest_offer",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R1", "A8"],
        chain="filter the dashboard merge-request list to reviewer=me and Open -> pick "
              "the row with the smallest comment count -> comment there @-mentioning "
              "the merge request's author",
        analogues=[ANALOGUE_REVIEW, ANALOGUE_POST_FOCUS],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "One open merge request in my review queue has barely been discussed. Find "
            'the one with the fewest comments and post "Happy to look at this - '
            'anything blocking?" there, @-mentioning its author.'
        ),
        mr_id=72404,
        mr_label="a11yproject/a11yproject.com!1265 'Fix card focus edge cases'",
        phrase="Happy to look at this - anything blocking?",
        mention="@mxmason",
        forbidden=(),
        names=("offer_comment_posted_on_quietest_review_request",
               "offer_comment_names_the_mr_author",
               "comment_set_is_exactly_the_quietest_review_request"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72404 "
            "(a11yproject/a11yproject.com!1265).",
            'That comment body contains "Happy to look at this - anything blocking?" '
            'and "@mxmason".',
            "72404 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "user_notes_count across the five open review requests: !1472=50, "
            "!1490=26, !1280=22, !1270=17, !1265=1. Minimum is !1265 with a margin "
            "of 16 over the next-quietest row.",
            "IssuablesList.jsx:822 renders row.user_notes_count in the "
            "[data-testid=issuable-comments] control, so the count is readable "
            "straight off the filtered list without opening anything.",
            "Author of !1265 is mxmason (user 2332) -> derived mention @mxmason.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 005
    dict(
        n="005",
        slug="conditional_thanks_stalest_review",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "R9", "A13", "A8"],
        chain="filter to reviewer=me and Open -> sort by Updated date oldest-first and "
              "take row one -> read who wrote that thread's newest comment -> branch on "
              "whether it is the merge request's author -> post the branch's comment",
        analogues=[ANALOGUE_COND, ANALOGUE_REVIEW],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "In my review queue, take the open merge request that has gone longest "
            "without an update. If its newest comment came from the person who opened "
            'it, comment "Thank you"; otherwise comment with just an @-mention of that '
            "person."
        ),
        mr_id=72551,
        mr_label="a11yproject/a11yproject.com!1472 - injected last note is by its author",
        phrase="Thank you",
        mention="",
        forbidden=("@jimbateson",),
        names=("thanks_comment_posted_on_stalest_review_request",
               "correct_conditional_branch_was_taken",
               "comment_set_is_exactly_the_stalest_review_request"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72551 "
            "(a11yproject/a11yproject.com!1472).",
            'That comment body contains "Thank you" and does not mention @jimbateson - '
            "the author-wrote-last branch.",
            "72551 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "Same R5+R4 selection as 002 (72551 is the oldest-updated open review "
            "request, margin 37m44s), but the writeback is decided by a state read.",
            "On the pristine seed the newest note on !1472 is byteblaze's own "
            "suggestion of 2022-10-01 16:14:41, so the seed branch is 'tag the "
            "author'. The setup appends note 900101, authored by jimbateson (2328, the "
            "MR author) at 2022-10-05 08:30:12, which flips the branch to \"Thank "
            "you\". A conditional over the fixed seed would be theatre; this one has "
            "to be read.",
            "NotesTimeline defaults to oldest-first with filter 'all' "
            "(NotesTimeline.jsx:190-191), so the injected note is the bottom entry of "
            "the timeline and its author name plus @handle render at :150-156.",
        ],
        setup=dict(
            injection=NOTE_INJECT_005,
            summary=(
                "Appends one seeded-looking user note to a11yproject/a11yproject.com!1472\n"
                "(merge request id 72551), authored by jimbateson - the merge request's own\n"
                "author - and dated after every existing note on that thread. That decides\n"
                "which arm of the task's conditional is correct; without it the branch would\n"
                "be a constant of the frozen seed."
            ),
            preconditions=[
                "newNotes: one note id 900101 on merge request 72551, author_id 2328 "
                "(jimbateson, who opened !1472), created_at 2022-10-05 08:30:12, "
                "system false. It becomes the newest comment on the thread and flips "
                "the A13 branch from 'tag the author' (the seed's answer) to 'reply "
                "Thank you'.",
                "Nothing in the rubric is pre-satisfied: every scored note must carry "
                "author_id 2330, and this one carries 2328.",
            ],
        ),
    ),
    # ---------------------------------------------------------------- 006
    dict(
        n="006",
        slug="conditional_reminder_busiest_assigned",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R1", "R9", "A13", "A8"],
        chain="filter to assigned-to-me and Open -> pick the row with the largest "
              "comment count -> read who wrote that thread's newest comment -> branch "
              "on whether it is the merge request's author -> post the branch's comment",
        analogues=[ANALOGUE_COND, ANALOGUE_ASSIGNED],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "Of the merge requests assigned to me, take the open one with the most "
            "comments. If its newest comment came from the person who opened it, "
            'comment "Thank you"; otherwise comment with just an @-mention of them.'
        ),
        mr_id=72409,
        mr_label="a11yproject/a11yproject.com!1270 - injected last note is NOT by its author",
        phrase="@aguscha333",
        mention="",
        forbidden=(),
        names=("reminder_comment_posted_on_busiest_assigned_mr",
               "reminder_comment_tags_the_mr_author",
               "comment_set_is_exactly_the_busiest_assigned_mr"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72409 "
            "(a11yproject/a11yproject.com!1270).",
            'That comment body contains "@aguscha333" - the tag-the-author branch.',
            "72409 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "Assigned-to-me AND opened is three rows; user_notes_count is 17 on !1270 "
            "and 0 on both !1485 and !40, so the superlative has a margin of 17 and no "
            "tie.",
            "The setup appends note 900201 authored by mxmason (2332) at 2023-03-29 "
            "10:12:44 - later than every seeded note or event on that thread, and NOT "
            "by the MR's author aguscha333 - so the branch resolves to 'tag the "
            "author'. This is the opposite arm from bundle 005, driven by a different "
            "injected precondition rather than a different entity.",
            "The injected note does not move user_notes_count (that field is only "
            "written by postComment), so the comment-count superlative that selected "
            "the MR is unchanged by the injection and unchanged by the agent's own "
            "comment ordering.",
        ],
        setup=dict(
            injection=NOTE_INJECT_006,
            summary=(
                "Appends one user note to a11yproject/a11yproject.com!1270 (merge request id\n"
                "72409) authored by mxmason - deliberately NOT the merge request's author -\n"
                "and dated after every seeded note and system event on that thread, so the\n"
                "task's conditional resolves to the tag-the-author arm."
            ),
            preconditions=[
                "newNotes: one note id 900201 on merge request 72409, author_id 2332 "
                "(mxmason), created_at 2023-03-29 10:12:44, system false. It is the "
                "newest comment on the thread and is not by aguscha333, who opened the "
                "merge request, so the A13 branch is 'tag the author'.",
                "Nothing in the rubric is pre-satisfied: scored notes must carry "
                "author_id 2330, and this one carries 2332.",
            ],
        ),
    ),
    # ---------------------------------------------------------------- 007
    dict(
        n="007",
        slug="own_open_mr_status_note",
        style="terse",
        difficulty="medium",
        shape="mutation",
        skills=["R5", "A8"],
        chain="filter the dashboard merge-request list to author=me and Open -> the "
              "single surviving row is the target -> post a status comment on it",
        analogues=[ANALOGUE_ASSIGNED, ANALOGUE_POST_LGTM],
        hard_criteria=None,
        instruction=(
            "I have exactly one merge request of my own still open on this instance. "
            'Find it and post the comment "Still relevant - rebasing this week." on it.'
        ),
        mr_id=72135,
        mr_label="a11yproject/a11yproject.com!1071 'Add color utility classes'",
        phrase="Still relevant - rebasing this week.",
        mention="",
        forbidden=(),
        names=("status_comment_posted_on_my_open_mr",
               "status_comment_carries_the_requested_text",
               "comment_set_is_exactly_my_open_mr"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 72135 "
            "(a11yproject/a11yproject.com!1071).",
            'That comment body contains "Still relevant - rebasing this week.".',
            "72135 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "byteblaze authored 309 merge requests; 307 are merged and 1 is closed, so "
            "author=byteblaze AND state=opened leaves exactly one row, !1071 id 72135. "
            "The instruction states the cardinality, never the merge request.",
            "The navbar search box's dropdown carries 'Merge requests I've created' "
            "(Navbar.jsx:319 -> /dashboard/merge_requests/?author_username=byteblaze), "
            "so the filter is one click from the landing page.",
            "Medium, not hard: one faceted retrieval feeding one action. The skill list "
            "was deliberately not padded to reach a hard label.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 008
    dict(
        n="008",
        slug="primer_design_stalest_open_chase",
        style="terse",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="open primer/design's merge-request list and keep the Open state -> sort "
              "by Updated date oldest-first and take row one -> comment there "
              "@-mentioning the merge request's author",
        analogues=[ANALOGUE_POST_OCTO, ANALOGUE_REVIEW],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "In primer/design, find the open merge request that has gone longest "
            'without an update, and comment "This one has gone stale - is it still '
            'wanted?" there, @-mentioning whoever opened it.'
        ),
        mr_id=139245,
        mr_label="primer/design!450 'Octovisuals Page' (updated_at moved by setup)",
        phrase="This one has gone stale - is it still wanted?",
        mention="@JoshBowdenConcepts",
        forbidden=(),
        names=("chase_comment_posted_on_stalest_primer_mr",
               "chase_comment_names_the_mr_author",
               "comment_set_is_exactly_the_stalest_primer_mr"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 139245 "
            "(primer/design!450).",
            'That comment body contains "This one has gone stale - is it still '
            'wanted?" and "@JoshBowdenConcepts".',
            "139245 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "primer/design has 16 open merge requests - one page at the 20-row "
            "first_page_size, so no pagination is involved.",
            "On the pristine seed the oldest-updated open row is !191 (2021-12-10 "
            "18:18:35, mperrotti). The setup rewrites !450's updated_at to "
            "2021-08-11 09:26:14, which makes !450 the answer with a margin of about "
            "four months. Varying the injected precondition rather than the entity is "
            "what gives this bundle a different correct answer and a different rubric "
            "from the seed-only members of the lane.",
            "The project's 295 merged merge requests reach back to 2018-11-09, so an "
            "agent that drops the Open state filter lands on !12 instead - the seed "
            "supplies the distractor for free and no extra injection was needed.",
            "Author of !450 is JoshBowdenConcepts (user 2368) -> derived mention "
            "@JoshBowdenConcepts.",
        ],
        setup=dict(
            injection=MR_EDIT_INJECT_008,
            summary=(
                "Rewrites primer/design!450 (merge request id 139245) through\n"
                "mergeRequestEdits with updated_at moved back to 2021-08-11, making it the\n"
                "project's least recently updated OPEN merge request. mergeRequestEdits\n"
                "replaces the record wholesale (overlay.js mergeCollection), so the full row\n"
                "including its description is written back unchanged apart from that field."
            ),
            preconditions=[
                "mergeRequestEdits['139245']: the complete primer/design!450 record "
                "with updated_at changed from 2023-03-24 19:00:20 to 2021-08-11 "
                "09:26:14. Every other field, including the seeded description, is "
                "written back verbatim. This makes !450 rather than !191 the stalest "
                "open merge request in the project, so the reward grades the "
                "post-injection answer.",
                "Nothing in the rubric is pre-satisfied: the record carries "
                "user_notes_count 2 from the seed and no note authored by byteblaze "
                "exists on it, while every scored note must sit in newNotes with "
                "author_id 2330.",
            ],
        ),
    ),
    # ---------------------------------------------------------------- 009
    dict(
        n="009",
        slug="review_queue_two_oldest_ping",
        style="explicit",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="filter to reviewer=me and Open -> sort by Updated date oldest-first and "
              "take the top two rows -> comment on each, @-mentioning that row's own "
              "author",
        analogues=[ANALOGUE_REVIEW, ANALOGUE_POST_LGTM],
        hard_criteria=["derived_target", "multi_mutation"],
        instruction=(
            "Two things in my review queue have been sitting untouched longer than "
            "anything else. On the dashboard list of merge requests where I am the "
            "reviewer, keep the Open state filter and sort by Updated date with the "
            "oldest first, then take the top two rows. On each of them post one "
            'comment reading "Ping - this is still in my review queue." that also '
            "@-mentions, by GitLab handle, the person who opened that particular merge "
            "request. Do not comment on anything else in the queue."
        ),
        pairs=[
            (72551, "@jimbateson", "a11yproject/a11yproject.com!1472, updated 2023-03-23 07:43:13.800501"),
            (72565, "@erikkroes", "a11yproject/a11yproject.com!1490, updated 2023-03-23 08:20:57.781405"),
        ],
        phrase="Ping - this is still in my review queue.",
        names=("ping_comment_posted_on_oldest_review_request",
               "ping_comment_posted_on_second_oldest_review_request",
               "comment_set_is_exactly_the_two_oldest_review_requests"),
        criteria=[
            'newNotes holds a byteblaze comment on merge request 72551 containing '
            '"Ping - this is still in my review queue." and "@jimbateson".',
            'newNotes holds a byteblaze comment on merge request 72565 containing '
            '"Ping - this is still in my review queue." and "@erikkroes".',
            "72551 and 72565 are the only merge requests byteblaze commented on this "
            "session.",
        ],
        notes=[
            "Open review requests in updated_asc order: !1472 (07:43:13.800501), "
            "!1490 (08:20:57.781405), !1265 (08:46:44.486898), !1280 "
            "(08:46:54.471362), !1270 (2023-03-27 23:21:22.709901). The rank-2/rank-3 "
            "boundary is 25m47s and the two picks differ from the rest by exact "
            "timestamps, so 'the top two' is unambiguous.",
            "Authors are jimbateson (2328) and erikkroes (2327): two DIFFERENT derived "
            "mentions, so an agent cannot carry one handle across both comments.",
        ],
        setup=None,
    ),
    # ---------------------------------------------------------------- 010
    dict(
        n="010",
        slug="primer_design_reviewed_but_stalled",
        style="explicit",
        difficulty="hard",
        shape="retrieval_writeback",
        skills=["R5", "R4", "A8"],
        chain="open primer/design's merge-request list, keep Open and add Reviewer=Any "
              "-> sort by Updated date oldest-first and take row one -> comment there "
              "@-mentioning the merge request's author",
        analogues=[ANALOGUE_POST_OCTO, ANALOGUE_REVIEW],
        hard_criteria=["derived_target", "cross_section"],
        instruction=(
            "In primer/design I only care about merge requests that already have a "
            "reviewer on them. Open the project's merge request list, keep the Open "
            "state filter, add a Reviewer filter set to Any, and sort by Updated date "
            "with the oldest first. Open the merge request that comes out on top and "
            'post a comment there reading "Reviewer assigned but no movement - can we '
            'close the loop?" that also @-mentions, by GitLab handle, the person who '
            "opened it."
        ),
        mr_id=139101,
        mr_label="primer/design!294 '[WIP] Single page component docs prototype'",
        phrase="Reviewer assigned but no movement - can we close the loop?",
        mention="@langermank",
        forbidden=(),
        names=("stalled_review_comment_posted_on_target_mr",
               "stalled_review_comment_names_the_mr_author",
               "comment_set_is_exactly_the_stalled_primer_mr"),
        criteria=[
            "newNotes holds a byteblaze comment on merge request id 139101 "
            "(primer/design!294).",
            'That comment body contains "Reviewer assigned but no movement - can we '
            'close the loop?" and "@langermank".',
            "139101 is the only merge request byteblaze commented on this session.",
        ],
        notes=[
            "Eleven of primer/design's 16 open merge requests carry a non-empty "
            "reviewer_ids. In updated_asc order the first is !294 (2023-01-31 "
            "13:23:27); the runner-up !113 is 2023-03-27 20:12:54.402634, a margin of "
            "about 8 weeks.",
            "Without the Reviewer=Any facet the answer would be !191 (2021-12-10, no "
            "reviewer), so the facet genuinely changes the answer rather than "
            "decorating the instruction.",
            "searchTokens.js:241 puts the Reviewer token on the project "
            "merge-request bar and filterIssuables reads reviewer_id=Any "
            "(hooks.js:143-148), so 'Any' is a real, clickable filter value.",
            "Author of !294 is langermank (user 2372) -> derived mention @langermank.",
        ],
        setup=None,
    ),
]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build():
    index = []
    nemo_rows = []
    for spec in TASKS:
        task_id = P + spec["slug"] + "_" + spec["n"]
        bundle = SITE / task_id
        docstring = (
            "Deterministic reward for %s.\n\n"
            "The agent's comment lands in `newNotes` "
            "(pages/NotesTimeline.jsx:326 appendTo('notes')), carrying "
            "noteable_type 'MergeRequest', the merge request's global id and "
            "author_id 2330. The rubric names the resulting collection: which "
            "merge request was commented on, what the comment says, and that the "
            "set of merge requests byteblaze commented on is exactly the derived "
            "target." % task_id
        )
        if "pairs" in spec:
            weights, rubric = pair_target_rubric(spec["pairs"], spec["phrase"], spec["names"])
        else:
            weights, rubric = single_target_rubric(
                spec["mr_id"], spec["mr_label"], spec["phrase"],
                spec["mention"], spec["forbidden"], spec["names"],
            )
        local_reward, nemo_reward = reward_files(task_id, docstring, rubric)
        write(bundle / "reward.py", local_reward)
        write(bundle / "nemo_reward.py", nemo_reward)

        setup_code = None
        if spec["setup"]:
            setup_code = SETUP_PREAMBLE.format(
                task_id=task_id,
                summary=spec["setup"]["summary"],
                url=URL_PLACEHOLDER,
                injection=json.dumps(spec["setup"]["injection"], indent=2),
            )
            write(bundle / "initial_setup.py", setup_code)

        write(bundle / "task_instruction.json", json.dumps({
            "task_id": task_id,
            "task_instruction": spec["instruction"],
            "app_dir": APP_DIR,
            "start_path": "/",
            "difficulty": spec["difficulty"],
            "success_criteria": spec["criteria"],
        }, indent=2) + "\n")

        metadata = {
            "difficulty": spec["difficulty"],
            "style": spec["style"],
            "shape": spec["shape"],
            "skills": spec["skills"],
            "skill_chain": spec["chain"],
            "official_analogues": spec["analogues"],
            "topic": "gitlab stale review nudge",
            "batch": "batch5-lane10",
            "inspiration_ids": ["webarena-156", "webarena-357", "webarena-415",
                                "webarena-389", "webarena-390", "webarena-391"],
            "authoring_notes": [HUB_COMMIT_NOTE] + spec["notes"],
        }
        if spec.get("hard_criteria"):
            metadata["hard_criteria"] = spec["hard_criteria"]
        if spec["setup"]:
            metadata["injected_preconditions"] = spec["setup"]["preconditions"]

        write(bundle / "task.json", json.dumps({
            "schema_version": 2,
            "task_id": task_id,
            "instruction": spec["instruction"],
            "apps": [{
                "name": APP_DIR,
                "source_name": "gitlab",
                "base_url_env": "CUA_GYM_WEBARENA_GITLAB_URL",
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
            "task_id": task_id,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": spec["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": task_id,
                "app_dir": APP_DIR,
                "initial_setup": setup_code,
                "eval_reward_code": nemo_reward,
            },
        }}
        write(bundle / "nemo_task.json", json.dumps(row, indent=2) + "\n")
        nemo_rows.append(row)
        index.append({"task_id": task_id, "path": "%s/task.json" % task_id})
        spec["task_id"] = task_id
        spec["weights"] = weights

    write(BATCH / "index.json", json.dumps(
        {"schema_version": 2, "tasks": index}, indent=2) + "\n")
    write(BATCH / "nemo_tasks.jsonl",
          "".join(json.dumps(r) + "\n" for r in nemo_rows))
    return TASKS


if __name__ == "__main__":
    for spec in build():
        print(spec["task_id"], spec["difficulty"], spec["style"], spec["shape"])
