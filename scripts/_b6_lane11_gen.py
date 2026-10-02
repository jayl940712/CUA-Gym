#!/usr/bin/env python3
"""Batch-6 lane 11 (gitlab, R3 -> A2) bundle emitter.

Authoring tool only. Emits output/tasks/gitlab/<task_id>/ bundles plus the
lane's GENERATION.md, index.json, nemo_tasks.jsonl and replay drafts.
Runs no validation.
"""
import json
import os
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output" / "tasks" / "gitlab"
BATCH = OUT / "_batches" / "label_count_milestone"
REPLAYS = BATCH / "replays"

APP_URL_PLACEHOLDER = "__CUA_GYM_WEBARENA_GITLAB_URL__"

# ---------------------------------------------------------------------------
# Injection helpers
# ---------------------------------------------------------------------------

BASE_STATE_JSON = r"""
{
  "currentUser": {"id": 2330, "username": "byteblaze", "name": "Byte Blaze",
                  "email": "ericwbailey@fakegithub.com", "state": "active",
                  "created_at": "2023-03-23 07:30:04.033203", "location": "Boston, MA",
                  "organization": "@github ",
                  "bio": "Inclusive design and accessibility advocate. Accessibility and design systems wonk for @primer.",
                  "followers": 2, "following": 3, "feed_token": "TMN_bBn9Z48qVbUFZV45", "status": null},
  "snippets": [],
  "repo": {"fileOverlay": {}, "treeOverlay": {}, "commitOverlay": {}, "branchOverlay": {},
           "tagOverlay": {}, "branchDeletions": {}, "tagDeletions": {}, "forkOrigin": {}},
  "ui": {"notificationLevels": {}, "sidebarCollapsed": false, "dismissedAlerts": [],
         "preferences": {"colorScheme": "light", "syntaxTheme": "white"},
         "projectSettings": {}},
  "nextIds": {"project": 194, "group": 7, "issue": %(next_issue)d, "mr": 139278, "note": 310827,
              "label": 1927, "milestone": 590, "member": 206}
}
"""

OVERLAY_TUPLES = """OVERLAY_COLLECTIONS = [
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
]"""


def issue_row(iid, iid_no, project_id, author_id, title, label_id, state, created, closed=None):
    row = {
        "id": iid,
        "iid": iid_no,
        "project_id": project_id,
        "title": title,
        "description": "",
        "author_id": author_id,
        "state": state,
        "confidential": False,
        "due_date": None,
        "milestone_id": None,
        "assignee_ids": [],
        "label_ids": [label_id],
        "created_at": created,
        "updated_at": created,
        "closed_at": closed,
        "closed_by_id": author_id if state == "closed" else None,
        "upvotes": 0,
        "user_notes_count": 0,
        "issue_type": "issue",
    }
    return row


def build_injection(project_id, author_id, groups, first_id, first_iid):
    """groups: list of (label_id, state, [titles]).  Returns (rows, next_issue_id)."""
    rows = []
    cur_id = first_id
    cur_iid = first_iid
    day = 1
    for label_id, state, titles in groups:
        for title in titles:
            created = "2023-03-%02d 09:%02d:00" % (min(28, day), (cur_id % 50))
            closed = "2023-03-%02d 16:%02d:00" % (min(28, day + 1), (cur_id % 40)) if state == "closed" else None
            rows.append(issue_row(cur_id, cur_iid, project_id, author_id, title,
                                  label_id, state, created, closed))
            cur_id += 1
            cur_iid += 1
            day += 1
    return rows, cur_id


# ---------------------------------------------------------------------------
# The ten tasks
# ---------------------------------------------------------------------------

A11Y = dict(project_id=174, path="a11yproject/a11yproject.com", display="a11yproject.com")
PRIMER = dict(project_id=180, path="primer/design", display="primer / design")
EMPATHY = dict(project_id=183, path="byteblaze/empathy-prompts", display="empathy-prompts")
WEBRING = dict(project_id=179, path="byteblaze/a11y-webring.club", display="a11y-webring.club")
PATTERNS = dict(project_id=185, path="byteblaze/accessible-html-content-patterns",
                display="accessible-html-content-patterns")

STATE_WORD = {"opened": "open", "closed": "closed", "all": "open and closed"}

ANALOGUE_MILESTONE_A = ("Create a milestone in the current repo with title \"product launch\" for the "
                        "upcoming event of product launch starting on January 16, 2030 and ending on "
                        "January 30, 2030")
ANALOGUE_MILESTONE_B = ("Create a milestone in the current repo with title \"all branches to main\" for "
                        "the upcoming task of merging all branches to main starting on March 15, 2044 "
                        "and ending on March 30, 2044")
ANALOGUE_LABEL_A = ("Go to the list of all opened issues that has the label bugs for the current project")
ANALOGUE_LABEL_B = ("Navigate to the page showing the list of open issues in the a11yproject/a11yproject.com "
                    "repository that have labels related to help wanted")

TASKS = []


def T(**kw):
    TASKS.append(kw)


T(
    task_id="label_count_milestone_bug_debt_a11yproject_001",
    project=A11Y, label="bug", state="closed", count=58,
    milestone="bug debt audit", start="2033-01-09", due="2033-02-10",
    style="terse",
    instruction=("On the a11yproject.com repo, count the closed issues labelled bug on its issue list, "
                 "then add a milestone \"bug debt audit\" running January 9 2033 to February 10 2033 whose "
                 "description is that number and nothing else."),
    injection=None,
    derived_from="label_triage_bulk_wcag_levels_a11yproject_001",
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-590", "webarena-102"],
    seed_note="Seed: 58 of the 61 issues carrying label 'bug' (id 1756) in project 174 are closed; 3 are open.",
)

T(
    task_id="label_count_milestone_claimed_sweep_a11yproject_002",
    project=A11Y, label="claimed", state="opened", count=20,
    milestone="claimed issue sweep", start="2033-03-06", due="2033-04-07",
    style="terse",
    instruction=("In a11yproject.com, count the open issues carrying the claimed label on its issue list, "
                 "then create a milestone \"claimed issue sweep\" from March 6 2033 to April 7 2033 and put "
                 "that number, alone, in its description."),
    injection=None,
    derived_from="label_triage_bulk_wcag_levels_a11yproject_001",
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-591", "webarena-103"],
    seed_note="Seed: label 'claimed' (id 1758) in project 174 has 20 open and 46 closed issues.",
)

T(
    task_id="label_count_milestone_docs_census_primer_003",
    project=PRIMER, label="area: documentation", state="all", count=20,
    milestone="documentation label census", start="2033-05-02", due="2033-06-02",
    style="explicit",
    instruction=("I want a record of how much documentation work primer / design has accumulated. Open that "
                 "project's issue list, filter it to the label \"area: documentation\", and read the All tab's "
                 "counter, which covers open and closed issues together. Then create a milestone in the same "
                 "project titled \"documentation label census\", with start date 2033-05-02 and due date "
                 "2033-06-02, and write that counter's number, and only that number, into the milestone "
                 "description. Do not use the issue count printed on the project card - it is a stored "
                 "counter and disagrees with the list."),
    injection=None,
    derived_from=None,
    analogues=[ANALOGUE_MILESTONE_B, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-592", "webarena-104"],
    seed_note="Seed: label 'area: documentation' (id 1839) in project 180 has 15 open + 5 closed = 20.",
)

_p4_rows, _p4_next = build_injection(
    180, 2383,
    [(1833, "opened", [
        "Colour contrast of the muted text token fails AA",
        "Focus ring is clipped inside overflow containers",
        "Dialog does not return focus to its trigger",
        "Autocomplete results are not announced by screen readers",
        "Skip link is hidden behind the sticky header",
        "Tooltip content is unreachable by keyboard",
        "Form error summary lacks a live region",
        "Icon-only buttons ship without accessible names",
     ]),
     (1833, "closed", [
        "Breadcrumb separator is read aloud as a word",
        "Radio group misses a fieldset legend",
     ]),
     (1839, "opened", [
        "Document the spacing scale tokens",
        "Add usage guidance for the banner component",
        "Rewrite the contribution page intro",
     ])],
    83821, 433)

T(
    task_id="label_count_milestone_a11y_backlog_primer_004",
    project=PRIMER, label="area: accessibility", state="opened", count=13,
    milestone="accessibility backlog burn-down", start="2033-07-04", due="2033-08-04",
    style="terse",
    instruction=("Count the open issues labelled \"area: accessibility\" on primer / design's issue list, then "
                 "add a milestone \"accessibility backlog burn-down\" there running July 4 2033 to August 4 "
                 "2033 with just that number as its description."),
    injection=dict(rows=_p4_rows, next_issue=_p4_next, author=2383),
    derived_from=None,
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_B],
    inspiration_ids=["webarena-593", "webarena-105"],
    seed_note=("Seed 5 open; setup adds 8 open + 2 closed on 'area: accessibility' (1833) and 3 open on "
               "'area: documentation' (1839). Correct answer 13; the closed tab reads 4 and the docs "
               "label reads 18."),
)

_p5_rows, _p5_next = build_injection(
    183, 2330,
    [(1883, "opened", [
        "Group the prompts by theme on the index",
        "Add a print stylesheet for the prompt cards",
        "Offer a dark colour scheme",
        "Let visitors shuffle the prompt order",
        "Add permalinks to individual prompts",
        "Surface a random prompt on the home page",
        "Translate the prompt set into Spanish",
        "Add an RSS feed of new prompts",
        "Show the source citation under each prompt",
     ]),
     (1883, "closed", [
        "Increase the card line height",
        "Collapse long prompt notes by default",
        "Add a copy-to-clipboard control",
     ]),
     (1885, "opened", [
        "Prompt: designing for intermittent connectivity",
        "Prompt: designing for screen magnification",
        "Prompt: designing for one-handed use",
        "Prompt: designing for shared devices",
     ])],
    83821, 19)

T(
    task_id="label_count_milestone_enhancement_grooming_empathy_005",
    project=EMPATHY, label="[Type] Enhancement", state="opened", count=12,
    milestone="enhancement grooming", start="2033-09-05", due="2033-10-06",
    style="explicit",
    instruction=("My empathy-prompts repo has drifted. Go to its issue list, filter to the label "
                 "\"[Type] Enhancement\", and read how many issues the Open tab reports under that filter. "
                 "Then create a milestone in empathy-prompts titled \"enhancement grooming\", starting "
                 "2033-09-05 and due 2033-10-06, and set its description to that count on its own, with no "
                 "other digits in the text."),
    injection=dict(rows=_p5_rows, next_issue=_p5_next, author=2330),
    derived_from="milestone_kickoff_001",
    analogues=[ANALOGUE_MILESTONE_B, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-594", "webarena-102"],
    seed_note=("Seed 3 open; setup adds 9 open + 3 closed on '[Type] Enhancement' (1883) and 4 open on "
               "'[Type] Prompt' (1885). Correct answer 12; closed reads 9, All reads 21."),
)

_p6_rows, _p6_next = build_injection(
    179, 2330,
    [(1816, "opened", [
        "Let members opt out of the random redirect",
        "Add a JSON endpoint for the member list",
        "Show the last-checked date beside each site",
        "Support multiple feeds per member",
        "Add a members-only changelog page",
        "Allow members to set a preferred display name",
        "Add an OPML export of every member feed",
     ]),
     (1816, "closed", [
        "Add a previous/next ring navigation widget",
        "Publish the ring badge as an SVG",
     ]),
     (1811, "opened", [
        "Add site: tempertemper.net",
        "Add site: hidde.blog",
        "Add site: sarasoueidan.com",
     ])],
    83821, 89)

T(
    task_id="label_count_milestone_feature_triage_webring_006",
    project=WEBRING, label="feature", state="opened", count=11,
    milestone="feature request triage", start="2034-02-01", due="2034-02-28",
    style="terse",
    instruction=("Count the open issues labelled feature on a11y-webring.club's issue list, then create a "
                 "milestone \"feature request triage\" in that repo running February 1 2034 to February 28 "
                 "2034 whose description is that number and nothing else."),
    injection=dict(rows=_p6_rows, next_issue=_p6_next, author=2330),
    derived_from="label_triage_bulk_wcag_levels_a11yproject_001",
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-590", "webarena-103"],
    seed_note=("Seed 4 open; setup adds 7 open + 2 closed on 'feature' (1816) and 3 open on 'addition' "
               "(1811). Correct answer 11; closed reads 2, All reads 13."),
)

T(
    task_id="label_count_milestone_help_wanted_retro_a11yproject_007",
    project=A11Y, label="help wanted", state="all", count=29,
    milestone="help wanted retrospective", start="2034-04-03", due="2034-05-05",
    style="terse",
    instruction=("On a11yproject.com's issue list, count every issue labelled help wanted, open and closed "
                 "together, then add a milestone \"help wanted retrospective\" running April 3 2034 to May 5 "
                 "2034 with only that number in its description."),
    injection=None,
    derived_from=None,
    analogues=[ANALOGUE_MILESTONE_B, ANALOGUE_LABEL_B],
    inspiration_ids=["webarena-591", "webarena-105"],
    seed_note="Seed: label 'help wanted' (id 1768) in project 174 has 4 open + 25 closed = 29.",
)

T(
    task_id="label_count_milestone_styling_archive_a11yproject_008",
    project=A11Y, label="styling", state="closed", count=23,
    milestone="styling cleanup archive", start="2034-06-05", due="2034-07-07",
    style="terse",
    instruction=("Count the closed issues labelled styling on a11yproject.com's issue list, then create a "
                 "milestone \"styling cleanup archive\" in that repo from June 5 2034 to July 7 2034, its "
                 "description being that number alone."),
    injection=None,
    derived_from=None,
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-592", "webarena-102"],
    seed_note="Seed: label 'styling' (id 1782) in project 174 has 1 open and 23 closed issues.",
)

_p9_rows, _p9_next = build_injection(
    183, 2330,
    [(1882, "opened", [
        "Prompt cards overlap on narrow viewports",
        "The index page returns a 404 for trailing slashes",
        "Card shadows render as black blocks in Safari",
        "The footer link to the licence is broken",
        "Long prompt titles overflow their container",
        "The favicon fails to load over HTTPS",
     ]),
     (1882, "closed", [
        "Duplicate prompt appears twice in the list",
        "Build fails when a prompt file has no front matter",
        "The sitemap omits the about page",
        "Typo in the introduction paragraph",
     ]),
     (1873, "opened", [
        "Review the prompt set before the conference",
        "Refresh the screenshots in the readme",
     ])],
    83821, 19)

T(
    task_id="label_count_milestone_bug_queue_empathy_009",
    project=EMPATHY, label="[Type] Bug", state="opened", count=7,
    milestone="bug queue reset", start="2034-08-07", due="2034-09-08",
    style="explicit",
    instruction=("Open the issue list of my empathy-prompts repo and filter it to the label \"[Type] Bug\". "
                 "Read the number the Open tab shows under that filter - not the issue count on the project "
                 "card, which is a stored figure. Then create a milestone in empathy-prompts titled \"bug "
                 "queue reset\" with start date 2034-08-07 and due date 2034-09-08, and make its description "
                 "exactly that number."),
    injection=dict(rows=_p9_rows, next_issue=_p9_next, author=2330),
    derived_from="milestone_kickoff_001",
    analogues=[ANALOGUE_MILESTONE_B, ANALOGUE_LABEL_A],
    inspiration_ids=["webarena-593", "webarena-104"],
    seed_note=("Seed 1 open; setup adds 6 open + 4 closed on '[Type] Bug' (1882) and 2 open on "
               "'[Priority] High' (1873). Correct answer 7; closed reads 4, All reads 11."),
)

_p10_rows, _p10_next = build_injection(
    185, 2330,
    [(1906, "opened", [
        "Pattern: accessible description list",
        "Pattern: disclosure widget",
        "Pattern: table with a sticky header row",
        "Pattern: figure with a long description",
        "Pattern: breadcrumb trail",
        "Pattern: definition tooltip",
        "Pattern: inline citation",
        "Pattern: pull quote",
        "Pattern: keyboard shortcut legend",
     ]),
     (1906, "closed", [
        "Pattern: skip navigation link",
        "Pattern: visually hidden heading",
     ]),
     (1902, "opened", [
        "Pattern: form field with helper text",
        "Pattern: required field indicator",
        "Pattern: error summary block",
     ])],
    83821, 8)

T(
    task_id="label_count_milestone_submission_review_patterns_010",
    project=PATTERNS, label="[Status] Submitted", state="opened", count=9,
    milestone="submission review sprint", start="2034-10-02", due="2034-11-03",
    style="terse",
    instruction=("Count the open issues labelled \"[Status] Submitted\" on the issue list of my "
                 "accessible-html-content-patterns repo, then add a milestone \"submission review sprint\" "
                 "there running October 2 2034 to November 3 2034 whose description is that number alone."),
    injection=dict(rows=_p10_rows, next_issue=_p10_next, author=2330),
    derived_from=None,
    analogues=[ANALOGUE_MILESTONE_A, ANALOGUE_LABEL_B],
    inspiration_ids=["webarena-594", "webarena-105"],
    seed_note=("Seed 0 open / 1 closed; setup adds 9 open + 2 closed on '[Status] Submitted' (1906) and 3 "
               "open on '[Status] Accepted' (1902). Correct answer 9; closed reads 3, All reads 12."),
)

assert len(TASKS) == 10

# ---------------------------------------------------------------------------
# Code templates
# ---------------------------------------------------------------------------

REWARD_BODY = '''
COMPONENT_WEIGHTS = {
    "milestone_created_with_dictated_window": 0.5,
    "filtered_issue_count_recorded": 0.5,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

PROJECT_ID = %(project_id)d
MILESTONE_TITLE = %(title_repr)s
START_DATE = %(start_repr)s
DUE_DATE = %(due_repr)s
EXPECTED_COUNT = %(count)d


def score_state(state):
    created = _created_milestones(state)
    milestone = _one(created)

    window_ok = bool(milestone is not None
                     and _norm(milestone.get("title")) == _norm(MILESTONE_TITLE)
                     and _text(milestone.get("start_date")) == START_DATE
                     and _text(milestone.get("due_date")) == DUE_DATE)

    numbers = _ints(milestone.get("description")) if milestone is not None else []
    count_ok = bool(milestone is not None and numbers == [EXPECTED_COUNT])

    checks = {
        "milestone_created_with_dictated_window": window_ok,
        "filtered_issue_count_recorded": count_ok,
    }
    details = {
        "milestone_created_with_dictated_window":
            "milestones created on project %%d == %%r" %% (
                PROJECT_ID,
                [(m.get("title"), m.get("start_date"), m.get("due_date")) for m in created]),
        "filtered_issue_count_recorded":
            "description integers == %%r, expected exactly [%%d]" %% (numbers, EXPECTED_COUNT),
    }
    return _build(checks, details)


# --------------------------------------------------------------------------
# Readers over the webarena_gitlab_mock overlay state (SCHEMA.md).
# Only user-visible persisted records are inspected, always from current_state.
# --------------------------------------------------------------------------


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _norm(value):
    return re.sub(r"\\s+", " ", _text(value)).lower()


def _ints(value):
    found = re.findall(r"\\d+", _text(value))
    return sorted(set(int(n) for n in found))


def _created_milestones(state):
    rows = [m for m in _list(_dict(state).get("newMilestones")) if isinstance(m, dict)]
    return [m for m in rows if m.get("project_id") == PROJECT_ID]


def _one(rows):
    return rows[0] if len(rows) == 1 else None


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

REWARD_TAIL = '''

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


def rubric_doc(t):
    return (
        "Rubric (both files share it):\n"
        "  1. newMilestones holds EXACTLY ONE row for project %d, titled %r,\n"
        "     with start_date %s and due_date %s.\n"
        "  2. That milestone's description carries exactly one distinct integer\n"
        "     and it is %d - the number of %s issues labelled %r that project's\n"
        "     issue list reports under the label filter.\n"
        "\n"
        "%s\n"
        "\n"
        "Handler: NewMilestone.jsx:64 appends to state.milestones, which the\n"
        "overlay persists as newMilestones (overlayShape.js). The untouched\n"
        "lane has newMilestones == [] and scores 0.0.\n"
        % (t["project_id_"], t["milestone"], t["start"], t["due"], t["count"],
           STATE_WORD[t["state"]], t["label"], t["seed_note"])
    )


def render_reward(t, nemo):
    head = '"""%s reward for %s.\n\n%s"""\n' % (
        "NeMo-Gym" if nemo else "Deterministic", t["task_id"], rubric_doc(t))
    if nemo:
        head += "import re\nimport sys\n\nimport requests\n\n"
        head += 'SID = "__CUA_GYM_SID__"\nBASE_URL = "%s"\n' % APP_URL_PLACEHOLDER
    else:
        head += "import re\n"
    body = REWARD_BODY % dict(
        project_id=t["project_id_"],
        title_repr=repr(t["milestone"]),
        start_repr=repr(t["start"]),
        due_repr=repr(t["due"]),
        count=t["count"],
    )
    return head + body + (NEMO_TAIL if nemo else REWARD_TAIL)


SETUP_TEMPLATE = '''"""NeMo-Gym setup program for %(task_id)s.

Plants the precondition that makes the count a live read rather than a fact
memorised from the frozen corpus: %(setup_summary)s

Nothing here touches state.milestones - newMilestones stays empty, so the
untouched lane scores exactly 0.0. nextIds.issue is raised to %(next_issue)d so an
id the agent's own work might allocate cannot collide with an injected row.

Self-contained: standard library plus requests (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(app_url)s"

BASE_STATE = json.loads(r"""%(base_state)s""")

%(overlay)s

INJECTED_ISSUES = json.loads(r"""%(rows)s""")


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {}
        state[deleted] = []
    state["newIssues"] = INJECTED_ISSUES
    return state


def publish(state):
    response = requests.post(BASE_URL + "/post?sid=" + SID,
                             json={"action": "set", "state": state}, timeout=30)
    response.raise_for_status()
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
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


def render_setup(t):
    inj = t["injection"]
    return SETUP_TEMPLATE % dict(
        task_id=t["task_id"],
        setup_summary=t["seed_note"],
        next_issue=inj["next_issue"],
        app_url=APP_URL_PLACEHOLDER,
        base_state=BASE_STATE_JSON % dict(next_issue=inj["next_issue"]),
        overlay=OVERLAY_TUPLES,
        rows=json.dumps(inj["rows"], indent=2),
    )


REPLAY_TEMPLATE = '''#!/usr/bin/env python3
"""Golden replay DRAFT for %(task_id)s.

Click-only: after the single landing navigation to start_path every step goes
through a rendered link, button or form control. No page.goto() and no
constructed URL (TASK4 S6).

Route: / -> the %(project_path)s row -> Project information -> Labels ->
the %(label)r row's "Issues" link (LabelsList.jsx:74 emits
?label_name[]=<title>) -> %(tab_note)s -> read the state-tab badge
(IssuesList.jsx:35 -> hooks.js:39-50, filter-aware) -> Issues -> Milestones ->
New milestone -> fill title/dates/description -> Create milestone.
"""
import pathlib
import re
import subprocess
import sys
import uuid

import requests
from playwright.sync_api import sync_playwright

BUNDLE = pathlib.Path("/home/ubuntu/CUA-Gym/output/tasks/gitlab/%(task_id)s")
BASE = "http://localhost:8001"
PROJECT = "%(project_path)s"
LABEL = %(label_repr)s
TAB = "%(tab)s"
EXPECTED = %(count)d


def sub(code, sid):
    return code.replace("__CUA_GYM_SID__", sid).replace(
        "__CUA_GYM_WEBARENA_GITLAB_URL__", BASE)


def run_setup(sid):
    setup = BUNDLE / "initial_setup.py"
    if not setup.is_file():
        requests.get(BASE + "/go?sid=" + sid, timeout=30)
        return
    done = subprocess.run([sys.executable, "-c", sub(setup.read_text(), sid)],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def score(sid):
    done = subprocess.run(
        [sys.executable, "-c", sub((BUNDLE / "nemo_reward.py").read_text(), sid)],
        capture_output=True, text=True)
    found = re.search(r"REWARD: ([0-9.]+)", done.stdout)
    return float(found.group(1)) if found else -1.0


def settle(page):
    page.wait_for_timeout(900)


def open_project(page):
    page.click('a[href="/%%s"]' %% PROJECT)
    settle(page)


def read_count(page):
    """Labels page -> the label's Issues link -> the state tab badge."""
    open_project(page)
    page.get_by_role("link", name="Project information").first.click()
    settle(page)
    page.get_by_role("link", name="Labels").first.click()
    settle(page)
    row = page.locator("li.label-list-item", has_text=LABEL).first
    row.get_by_role("link", name="Issues").first.click()
    settle(page)
    if TAB != "opened":
        page.locator("#state-" + TAB).click()
        settle(page)
    badge = page.locator("#state-" + TAB + " .gl-tab-counter-badge").first
    value = int(badge.inner_text().strip())
    assert value == EXPECTED, "badge read %%d, expected %%d" %% (value, EXPECTED)
    return value


def create_milestone(page, count):
    page.locator('a.shortcuts-issues[href="/%%s/-/issues"]' %% PROJECT).first.click()
    settle(page)
    page.click('a[href="/%%s/-/milestones"]' %% PROJECT)
    settle(page)
    page.click('a[title="New milestone"]')
    settle(page)
    page.fill("#milestone_title", %(title_repr)s)
    page.fill("#milestone_start_date", %(start_repr)s)
    page.fill("#milestone_due_date", %(due_repr)s)
    page.fill("#milestone_description", str(count))
    page.click('[data-qa-selector="create_milestone_button"]')
    settle(page)


def main():
    sid = "replay-%(suffix)s-" + uuid.uuid4().hex[:8]
    run_setup(sid)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(BASE + "/?sid=" + sid, wait_until="networkidle")
        settle(page)
        count = read_count(page)
        create_milestone(page, count)
        browser.close()
    print("score:", score(sid))


main()
'''


def render_replay(t):
    tab = t["state"]
    tab_note = ("the list lands on the Open tab" if tab == "opened"
                else "click the %s tab" % ("Closed" if tab == "closed" else "All"))
    return REPLAY_TEMPLATE % dict(
        task_id=t["task_id"],
        project_path=t["project"]["path"],
        label=t["label"],
        label_repr=repr(t["label"]),
        tab=tab,
        tab_note=tab_note,
        count=t["count"],
        title_repr=repr(t["milestone"]),
        start_repr=repr(t["start"]),
        due_repr=repr(t["due"]),
        suffix=t["task_id"][-3:],
    )


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------


def success_criteria(t):
    return [
        "newMilestones holds exactly one agent-created row for project %d (%s), titled '%s'."
        % (t["project_id_"], t["project"]["path"], t["milestone"]),
        "That milestone's start_date is %s and its due_date is %s." % (t["start"], t["due"]),
        ("That milestone's description contains exactly one distinct integer, %d - the number of %s "
         "issues labelled '%s' the project's issue list reports under that label filter."
         % (t["count"], STATE_WORD[t["state"]], t["label"])),
    ]


def authoring_notes(t):
    notes = [
        "Grounded in hub/websites/webarena_gitlab_mock as served by the hub (dist/, built 2026-08-17).",
        ("Retrieval surface: the issue list's state-tab badges are filter-aware. IssuesList.jsx:35 calls "
         "issuableStateCounts(rows, q, indexes); hooks.js:39-50 re-runs filterIssuables with state forced "
         "to 'all' and counts by state, so every filter except state itself is honoured. "
         "IssuablesList.jsx:888's `counts` object is dead code and is NOT what renders "
         "(CORRECTIONS #10)."),
        ("Two disagreeing surfaces, so the instruction names one: projects.json.open_issues_count is a "
         "stored counter (CORRECTIONS #20) and the project card renders it. The rubric is graded against "
         "the ISSUE LIST, which is what the instruction points at."),
        ("Click path from '/': the dashboard lists all 14 projects byteblaze belongs to on one page "
         "(DashboardProjects.jsx PER_PAGE 20), including %s. Project information -> Labels gives a per-label "
         "'Issues' link that carries ?label_name[]=<title> (LabelsList.jsx:74); Issues -> Milestones -> "
         "New milestone reaches the creation form. Sidebar children only appear once the section's own page "
         "is open." % t["project"]["path"]),
        ("Writeback: NewMilestone.jsx:64 appendTo('milestones') -> AppContext.jsx:296 -> the overlay records "
         "the row in newMilestones; nextIds.milestone seeds at 590 (overlayShape.js) so the created id "
         "cannot collide with the 589 frozen milestones."),
        ("Milestone form fields verified: milestone[title], milestone[start_date], milestone[due_date] "
         "(type=date, so 'YYYY-MM-DD'), milestone[description]. All four are dictated, keeping the action "
         "a plain A2 form fill rather than drifting into A7."),
        ("Skip-the-retrieval check: the count component is 0.5 of the reward and no part of the instruction "
         "names the number, so an agent that creates the milestone without reading the badge scores at most "
         "0.5 and cannot reach 1.0."),
        t["seed_note"],
    ]
    if t["project_id_"] == 174:
        notes.append("a11yproject/a11yproject.com carries 6 frozen milestones; they live in the frozen "
                     "corpus, not in newMilestones, so 'exactly one created milestone' is unambiguous.")
    else:
        notes.append("This project carries zero seeded milestones (only 32 of 175 do), so the milestone "
                     "list starts on its empty state and the milestone must be created.")
    return notes


def injected_preconditions(t):
    inj = t["injection"]
    if inj is None:
        return None
    opened = sum(1 for r in inj["rows"] if r["state"] == "opened")
    closed = sum(1 for r in inj["rows"] if r["state"] == "closed")
    return [
        ("newIssues: %d issue rows appended to project %d (%s), %d opened and %d closed, ids %d-%d, iids "
         "%d-%d, author_id %d, each carrying the full field set NewIssue.jsx:63 writes (id, iid, project_id, "
         "title, description, author_id, state, confidential, due_date, milestone_id, assignee_ids, "
         "label_ids, created_at, updated_at, closed_at, closed_by_id, upvotes, user_notes_count, "
         "issue_type)."
         % (len(inj["rows"]), t["project_id_"], t["project"]["path"], opened, closed,
            inj["rows"][0]["id"], inj["rows"][-1]["id"], inj["rows"][0]["iid"], inj["rows"][-1]["iid"],
            inj["author"])),
        ("Why: %s The injected set moves the correct answer off the frozen-corpus value, so the badge has "
         "to be read during the episode." % t["seed_note"]),
        ("Distractors: rows carrying the same label in the other state, and rows carrying a neighbouring "
         "label of the same project, so an agent that reads the wrong tab or the wrong label lands on a "
         "different number."),
        ("nextIds.issue raised to %d so no injected id collides with an allocation made during the episode."
         % inj["next_issue"]),
        "Nothing is written to state.milestones / newMilestones, so the untouched lane still scores 0.0.",
    ]


def emit():
    BATCH.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    index = {"schema_version": 2, "tasks": []}
    jsonl_lines = []

    for t in TASKS:
        t["project_id_"] = t["project"]["project_id"]
        d = OUT / t["task_id"]
        d.mkdir(parents=True, exist_ok=True)

        instruction = t["instruction"]
        (d / "task_instruction.json").write_text(json.dumps({
            "task_id": t["task_id"],
            "task_instruction": instruction,
            "app_dir": "webarena_gitlab_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": success_criteria(t),
        }, indent=2) + "\n")

        metadata = {
            "style": t["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R3", "A2"],
            "skill_chain": ("R3 count the %s issues carrying the label %r on %s's issue list -> A2 create "
                            "the milestone %r in the same project with the dictated window and that count "
                            "as its description"
                            % (STATE_WORD[t["state"]], t["label"], t["project"]["path"], t["milestone"])),
            "derived_from": t["derived_from"],
            "official_analogues": t["analogues"],
            "topic": "gitlab label count -> cleanup milestone",
            "inspiration_ids": t["inspiration_ids"],
            "authoring_notes": authoring_notes(t),
        }
        inj = injected_preconditions(t)
        if inj is not None:
            metadata["injected_preconditions"] = inj

        (d / "task.json").write_text(json.dumps({
            "schema_version": 2,
            "task_id": t["task_id"],
            "instruction": instruction,
            "apps": [{
                "name": "webarena_gitlab_mock",
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

        (d / "reward.py").write_text(render_reward(t, nemo=False))
        nemo_reward = render_reward(t, nemo=True)
        (d / "nemo_reward.py").write_text(nemo_reward)

        setup_code = None
        if t["injection"] is not None:
            setup_code = render_setup(t)
            (d / "initial_setup.py").write_text(setup_code)

        row = {"task_payload": {
            "task_id": t["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": instruction,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": t["task_id"],
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup_code,
                "eval_reward_code": nemo_reward,
            },
        }}
        (d / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n")
        jsonl_lines.append(json.dumps(row))

        (REPLAYS / (t["task_id"] + ".py")).write_text(render_replay(t))
        index["tasks"].append({"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]})

    (BATCH / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    (BATCH / "nemo_tasks.jsonl").write_text("\n".join(jsonl_lines) + "\n")
    print("wrote %d bundles" % len(TASKS))


emit()
