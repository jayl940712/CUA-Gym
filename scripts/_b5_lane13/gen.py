#!/usr/bin/env python3
"""Generator for batch-5 lane 13 (gitlab / issue_url_digest)."""
import json
import os
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output" / "tasks" / "gitlab"
BATCH = OUT / "_batches" / "issue_url_digest"
REPLAYS = BATCH / "replays"

SINK = "byteblaze/gimmiethat.space"

ANALOGUE_URLS = "Make a folder named car on the gimmiethat.space repo and include a file called urls.txt that consists of the links to the 5 most recent posts from the cars forum."
ANALOGUE_REAL_SPACE = "Create a folder named real_space in gimmiethat.space repo. Within it, create a file named urls.txt that contains the URLs of the 5 most recent posts from the space?"
ANALOGUE_NEWS = "Create a folder named news in gimmiethat.space repo. Within it, create a file named urls.txt that contains the URLs of the 5 most recent posts from the news related subreddits?"
ANALOGUE_MOVIE = "Create a folder named moive_space in gimmiethat.space repo. Within it, create a file named urls.txt that contains the URLs of the 5 most recent posts from the movies?"
ANALOGUE_FUNNY = "Create a folder named funny_pic in gimmiethat.space repo. Within it, create a file named urls.txt that contains the URLs of the 5 most recent posts from the memes?"
ANALOGUE_LABEL_LIST = "Navigate to the page showing the list of open issues in the a11yproject/a11yproject.com repository that have labels related to help wanted"
ANALOGUE_NOLABEL = "Go to the list of all opened issues that don't have any labels for the current project"
ANALOGUE_RECENT_VIEW = "Open the issues page for the current project filtered to the most recent created open issues"
ANALOGUE_KEYCLOAK = "Navigate to the page showing the list of all issues in the keycloak/keycloak repository that have labels related to flaky-test"
ANALOGUE_OPENAPI = "Navigate to the page showing the list of not yet closed issues in the OpenAPITools/openapi-generator repository that have labels related to OpenAPI Generator CLI"

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
  "nextIds": {"project": 194, "group": 7, "issue": 83821, "mr": 139278, "note": 310827,
              "label": 1927, "milestone": 590, "member": 206}
}
"""

OVERLAY_BLOCK = '''OVERLAY_COLLECTIONS = [
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
'''


def issue_record(iid, rid, project_id, created, labels, title, author, body):
    return {
        "assignee_ids": [],
        "author_id": author,
        "closed_at": None,
        "closed_by_id": None,
        "confidential": False,
        "created_at": created,
        "due_date": None,
        "id": rid,
        "iid": iid,
        "label_ids": labels,
        "milestone_id": None,
        "project_id": project_id,
        "state": "opened",
        "title": title,
        "updated_at": created,
        "upvotes": 0,
        "user_notes_count": 0,
        "description": body,
    }


TASKS = []


def task(**kw):
    TASKS.append(kw)


# --------------------------------------------------------------------------
task(
    task_id="issue_url_digest_a11yproject_post_queue_001",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="a11yproject/a11yproject.com",
    facet="the `post` label, state opened, default created-date sort",
    folder="post-queue",
    branch=None,
    expected=[1536, 1533, 1530, 1529],
    next_iid=1526,
    instruction=(
        "Keep a running digest in gimmiethat.space: make a folder called post-queue "
        "holding urls.txt with the links to the four most recently created open issues "
        "labelled post on a11yproject/a11yproject.com, newest first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_LABEL_LIST],
    inspiration_ids=["webarena-791", "webarena-552", "webarena-102"],
    injection=[
        issue_record(1536, 83821, 174, "2023-03-27 09:12:44", [1758, 1776],
                     "[Post] HOWTO: Accessible data tables from scratch", 2366,
                     "A walkthrough of building a sortable data table that stays usable with a screen reader.\n\nCovers caption, scope, and the aria-sort pattern."),
        issue_record(1537, 83822, 174, "2023-03-28 14:05:11", [1756],
                     "Search results page drops the skip link", 2394,
                     "The skip-to-content link is missing on /search, so keyboard users have to tab through the whole header every time."),
    ],
    injection_note=[
        "newIssues adds two open a11yproject.com issues newer than every seeded row: #1536 (2023-03-27) carrying the `post` label, and #1537 (2023-03-28) carrying only `bug`. #1537 is the newest open issue in the project, so an agent that reads the unfiltered default list puts the wrong URL first; #1536 makes the frozen seed alone insufficient to answer. Neither touches repo.fileOverlay, which is all the rubric reads.",
        "nextIds.issue is raised to 83823 so an agent-created issue cannot collide with the injected ids.",
    ],
    next_issue_id=83823,
)

task(
    task_id="issue_url_digest_primer_docs_002",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="primer/design",
    facet="the `area: documentation` label, state opened, default created-date sort",
    folder="primer-docs",
    branch=None,
    expected=[435, 372, 316, 300, 295],
    next_iid=290,
    instruction=(
        "In gimmiethat.space, add primer-docs/urls.txt listing the links to the five "
        "newest open issues on primer/design that carry the area: documentation label, "
        "most recent first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_LABEL_LIST],
    inspiration_ids=["webarena-791", "webarena-553", "webarena-102"],
    injection=[
        issue_record(435, 83821, 180, "2023-02-20 08:15:03", [1839, 1847],
                     "Document the new spacing scale tokens", 2366,
                     "The spacing scale changed last release and the docs still show the old ramp. Needs a table of the new tokens and their pixel values."),
        issue_record(436, 83822, 180, "2023-03-02 10:41:52", [1866],
                     "Octicon svg sprite 404s on the docs site", 2394,
                     "Every octicon on the published docs renders as a broken image. The sprite path looks wrong after the last deploy."),
    ],
    injection_note=[
        "newIssues adds two open primer/design issues: #435 (2023-02-20) with `area: documentation` and `effort: low`, and #436 (2023-03-02) with only `type: bug`. #436 becomes the newest open issue overall and is a pure distractor; #435 becomes the newest documentation issue, so the answer is no longer readable off the frozen seed. Neither touches repo.fileOverlay.",
        "nextIds.issue is raised to 83823 so an agent-created issue cannot collide with the injected ids.",
    ],
    next_issue_id=83823,
)

task(
    task_id="issue_url_digest_keycloak_bug_sweep_003",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="keycloak/keycloak",
    facet="the `kind/bug` label, state opened, default created-date sort",
    folder="keycloak-bugs",
    branch=None,
    expected=[19185, 19183, 19164, 19162, 19160],
    next_iid=19117,
    instruction=(
        "I'm triaging keycloak. Create a keycloak-bugs folder in gimmiethat.space with "
        "a urls.txt holding links to the five most recently opened kind/bug issues in "
        "keycloak/keycloak, newest first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_KEYCLOAK],
    inspiration_ids=["webarena-791", "webarena-554", "webarena-104"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)

task(
    task_id="issue_url_digest_a11yproject_inbox_004",
    style="terse",
    difficulty="medium",
    skills=["R4", "A7"],
    hard_criteria=None,
    source="a11yproject/a11yproject.com",
    facet="the default open-issues view, created-date sort",
    folder="inbox",
    branch=None,
    expected=[1535, 1534, 1533, 1530, 1529],
    next_iid=1526,
    instruction=(
        "Make an inbox folder in my gimmiethat.space repo containing urls.txt with "
        "links to the five most recently created open issues on "
        "a11yproject/a11yproject.com, listed newest first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_RECENT_VIEW],
    inspiration_ids=["webarena-791", "webarena-555", "webarena-45"],
    injection=[
        issue_record(1534, 83821, 174, "2023-03-25 16:02:31", [1753],
                     "Contrast checker widget mis-reports AAA on large text", 2366,
                     "The widget applies the small-text threshold to 24px headings, so it reports AAA where the ratio only reaches AA."),
        issue_record(1535, 83822, 174, "2023-03-29 11:47:05", [1765, 1768],
                     "Add an RSS feed for the articles index", 2394,
                     "A feed would let readers follow new articles without checking the site. Eleventy has a plugin for this already."),
    ],
    injection_note=[
        "newIssues adds two open a11yproject.com issues, #1534 (2023-03-25) and #1535 (2023-03-29), both newer than every seeded row. The top of the default list is therefore not the frozen seed's top, so the digest cannot be produced from memorised seed data. Neither touches repo.fileOverlay.",
        "nextIds.issue is raised to 83823 so an agent-created issue cannot collide with the injected ids.",
    ],
    next_issue_id=83823,
)

task(
    task_id="issue_url_digest_primer_unlabelled_005",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="primer/design",
    facet="label None (no labels at all), state opened, default created-date sort",
    folder="triage",
    branch=None,
    expected=[385, 334, 310],
    next_iid=240,
    instruction=(
        "primer/design has open issues nobody has labelled yet. Put their three newest "
        "links, newest first, into triage/urls.txt on gimmiethat.space."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_NOLABEL],
    inspiration_ids=["webarena-791", "webarena-343", "webarena-552"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)

task(
    task_id="issue_url_digest_dynamorio_feature_branch_006",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7", "A2"],
    hard_criteria=["derived_target", "multi_mutation"],
    source="DynamoRIO/dynamorio",
    facet="the `Type-Feature` label, state opened, default created-date sort",
    folder="dynamorio",
    branch="feature-digest",
    expected=[5905, 5879, 5873, 5843, 5804],
    next_iid=5795,
    instruction=(
        "On a feature-digest branch of gimmiethat.space, commit dynamorio/urls.txt with "
        "links to the five newest open Type-Feature issues in DynamoRIO/dynamorio, "
        "newest first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_LABEL_LIST],
    inspiration_ids=["webarena-791", "webarena-102", "webarena-554"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)

task(
    task_id="issue_url_digest_openapi_enhancement_007",
    style="explicit",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="OpenAPITools/openapi-generator",
    facet="the `Enhancement: Feature` label, state opened, default created-date sort",
    folder="openapi-reqs",
    branch=None,
    expected=[14982, 14952, 14951, 14943, 14928],
    next_iid=14918,
    instruction=(
        "I keep a checked-in digest of upstream feature requests in my gimmiethat.space "
        "repo. On OpenAPITools/openapi-generator, look at the open issues carrying the "
        "\"Enhancement: Feature\" label and take the five that were created most recently. "
        "Then create a folder named openapi-reqs in byteblaze/gimmiethat.space and, "
        "inside it, a file called urls.txt whose contents are the links to those five "
        "issues, one per line, in the same newest-first order the issue list shows them. "
        "Do not list any other issue in that file."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_OPENAPI],
    inspiration_ids=["webarena-791", "webarena-105", "webarena-553"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)

task(
    task_id="issue_url_digest_capnproto_reading_list_008",
    style="explicit",
    difficulty="medium",
    skills=["R4", "A7"],
    hard_criteria=None,
    source="capnproto/capnproto",
    facet="the default open-issues view, created-date sort",
    folder="capnproto",
    branch=None,
    expected=[1646, 1643, 1623, 1622],
    next_iid=1602,
    instruction=(
        "byteblaze/gimmiethat.space is where I stash reading lists. Open the issue list "
        "of capnproto/capnproto and leave it on the default view of open issues sorted "
        "by creation date, newest first, then take the four issues at the top. Create a "
        "folder called capnproto in gimmiethat.space containing a file urls.txt whose "
        "body is the links to those four issues, one per line, in that order and with "
        "no other issue listed."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_RECENT_VIEW],
    inspiration_ids=["webarena-791", "webarena-45", "webarena-555"],
    injection=[
        issue_record(1646, 83821, 72, "2023-03-26 08:19:40", [663],
                     "kj::Promise deadlock when the event loop is drained twice", 620,
                     "Calling kj::EventLoop::run() again from inside a fulfiller wedges the loop. Minimal repro attached in the comments."),
    ],
    injection_note=[
        "newIssues adds one open capnproto/capnproto issue, #1646 (2023-03-26), newer than the seeded top row #1643. The head of the default list therefore differs from the frozen seed, so the correct four URLs cannot be recalled from seed data alone. It does not touch repo.fileOverlay.",
        "nextIds.issue is raised to 83822 so an agent-created issue cannot collide with the injected id.",
    ],
    next_issue_id=83822,
)

task(
    task_id="issue_url_digest_keycloak_wishlist_branch_009",
    style="explicit",
    difficulty="hard",
    skills=["R5", "R4", "A7", "A2"],
    hard_criteria=["derived_target", "multi_mutation"],
    source="keycloak/keycloak",
    facet="the `kind/enhancement` label, state opened, default created-date sort",
    folder="keycloak",
    branch="keycloak-wishlist",
    expected=[19190, 19166, 19115, 19067],
    next_iid=19056,
    instruction=(
        "I want this on a wishlist branch rather than on main. In keycloak/keycloak, "
        "filter the issue list down to the open issues labelled kind/enhancement and "
        "note the four that were created most recently, newest first. Then, in "
        "byteblaze/gimmiethat.space, commit a new file keycloak/urls.txt on a new branch "
        "named keycloak-wishlist, containing exactly those four issue links in that "
        "order, one per line."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_KEYCLOAK],
    inspiration_ids=["webarena-791", "webarena-104", "webarena-552"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)

task(
    task_id="issue_url_digest_dynamorio_help_wanted_010",
    style="terse",
    difficulty="hard",
    skills=["R5", "R4", "A7"],
    hard_criteria=["derived_target", "cross_section"],
    source="DynamoRIO/dynamorio",
    facet="the `help wanted` label, state opened, default created-date sort",
    folder="help-wanted",
    branch=None,
    expected=[5905, 5903, 5812, 5646, 5638],
    next_iid=5480,
    instruction=(
        "Add a help-wanted folder to gimmiethat.space with urls.txt inside it, listing "
        "the links to the five most recently created open issues tagged help wanted in "
        "DynamoRIO/dynamorio, newest first."
    ),
    analogues=[ANALOGUE_URLS, ANALOGUE_LABEL_LIST],
    inspiration_ids=["webarena-791", "webarena-102", "webarena-555"],
    injection=None,
    injection_note=None,
    next_issue_id=None,
)


# ---------------------------------------------------------------------------
# Reward source
# ---------------------------------------------------------------------------

REWARD_DOC = '''"""Deterministic reward for {task_id}.

The digest is written through the mock's file editor: NewFile.jsx:46 calls
commitToRepo (src/components/create/mutations.js:229), which calls writeFiles
(:155) and records the body under
repo.fileOverlay["<full_path>:<ref>:<path>"]. A slash in the file-name box is
all it takes to create the folder (NewFile.jsx header comment), so the folder
and the file are one commit.

The ordered list the body must carry comes off {source}'s issue list
({facet}). filterIssuables defaults state to "opened"
(src/pages/hooks.js:64) and sortIssuables defaults to created-date descending
(:343), so the wanted rows are the head of that filtered list.

Order is part of the answer: each expected issue URL is located by its first
character offset in the recorded body, and those offsets must strictly
increase. Only current_state is read; nothing is compared against a baseline
and no implementation trace is inspected.
"""
'''

REWARD_CORE = '''
FILE_KEY = "{file_key}"
SINK_PATH = "{sink}"
SOURCE_PATH = "{source}"
EXPECTED_IIDS = {expected}
NEXT_IID = {next_iid}
{branch_const}

def _dict(value):
    return value if isinstance(value, dict) else {{}}


def _list(value):
    return value if isinstance(value, list) else []


def _repo(state, bucket):
    return _dict(_dict(_dict(state).get("repo")).get(bucket))


def _body(state):
    """The committed digest body recorded under the file overlay key, or ""."""
    value = _repo(state, "fileOverlay").get(FILE_KEY)
    return value if isinstance(value, str) else ""


def _issue_pattern(iid):
    """Matches the issue's own path, so a bare path and a full URL both hit."""
    return re.escape("/" + SOURCE_PATH.lower() + "/-/issues/") + str(iid) + r"(?![0-9])"


def _position(low, iid):
    found = re.search(_issue_pattern(iid), low)
    return found.start() if found else -1


{branch_fn}def score_state(state):
    body = _body(state)
    low = body.lower()
    positions = [_position(low, iid) for iid in EXPECTED_IIDS]
    found = all(p >= 0 for p in positions)
    ordered = found and all(positions[i] < positions[i + 1]
                            for i in range(len(positions) - 1))
    extra = _position(low, NEXT_IID)
    limited = found and extra < 0
    checks = {{
        "digest_file_committed": bool(body.strip()),
        "all_issue_links_present": found,
        "links_newest_first": ordered,
        "slice_stops_at_n": limited,
    }}
    details = {{
        "digest_file_committed": "fileOverlay[%s] holds %d characters" % (FILE_KEY, len(body)),
        "all_issue_links_present": "character offset per expected issue %r: %r" % (EXPECTED_IIDS, positions),
        "links_newest_first": "character offset per expected issue %r: %r" % (EXPECTED_IIDS, positions),
        "slice_stops_at_n": "offset of the next-ranked issue %r: %r" % (NEXT_IID, extra),
    }}
{branch_check}    return _build(checks, details)


def _build(checks, details):
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = bool(checks.get(name))
        components.append({{
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if ok else 0.0,
            "details": details.get(name, ""),
        }})
    return components


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
'''

BRANCH_FN = '''def _branch_present(state):
    rows = _list(_repo(state, "branchOverlay").get(SINK_PATH))
    for row in rows:
        if isinstance(row, dict) and str(row.get("name")) == BRANCH_NAME:
            return True
    return False


'''

BRANCH_CHECK = '''    checks["digest_branch_created"] = _branch_present(state)
    details["digest_branch_created"] = "branchOverlay[%s] carries %r: %r" % (
        SINK_PATH, BRANCH_NAME, checks["digest_branch_created"])
'''

REWARD_TAIL = '''

APP_KEYS = ("gitlab", "webarena_gitlab_mock")


def _app_state(evidence):
    """The gitlab app's current state, under either key the harness may use."""
    apps = _dict(_dict(evidence).get("apps"))
    for key in APP_KEYS:
        if key in apps:
            return _dict(_dict(apps.get(key)).get("current_state"))
    return {}


def evaluate(evidence):
    state = _app_state(evidence)
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

NEMO_DOC = '''"""NeMo-Gym reward program for {task_id}.

Same rubric as reward.py, read from GET /go?sid=... instead of a frozen
evidence bundle. Prints REWARD: <float> on every output path.

Self-contained: standard library plus requests.
"""
'''

NEMO_TAIL = '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)
        response.raise_for_status()
        payload = response.json()
        state = _dict(payload.get("current_state"))
        components = score_state(state)
        total = _clamp(round(sum(c["score"] for c in components), 6))
    except Exception as exc:
        print("reward error: %r" % (exc,), file=sys.stderr)
        print("REWARD: 0.0")
        return
    for component in components:
        print("%s: %s" % (component["name"], component["score"]))
    print("REWARD: %s" % float(total))


main()
'''


def weights(cfg):
    if cfg["branch"]:
        return [
            ("digest_branch_created", 0.15),
            ("digest_file_committed", 0.1),
            ("all_issue_links_present", 0.35),
            ("links_newest_first", 0.25),
            ("slice_stops_at_n", 0.15),
        ]
    return [
        ("digest_file_committed", 0.15),
        ("all_issue_links_present", 0.4),
        ("links_newest_first", 0.3),
        ("slice_stops_at_n", 0.15),
    ]


def weights_block(cfg):
    rows = "".join('    "%s": %s,\n' % (n, w) for n, w in weights(cfg))
    return "COMPONENT_WEIGHTS = {\n%s}\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n" % rows


def file_key(cfg):
    ref = cfg["branch"] or "main"
    return "%s:%s:%s/urls.txt" % (SINK, ref, cfg["folder"])


def reward_core(cfg):
    return REWARD_CORE.format(
        file_key=file_key(cfg),
        sink=SINK,
        source=cfg["source"],
        expected=repr(cfg["expected"]),
        next_iid=cfg["next_iid"],
        branch_const=('BRANCH_NAME = "%s"\n' % cfg["branch"]) if cfg["branch"] else "",
        branch_check=BRANCH_CHECK if cfg["branch"] else "",
        branch_fn=BRANCH_FN if cfg["branch"] else "",
    )


def reward_source(cfg):
    doc = REWARD_DOC.format(task_id=cfg["task_id"], source=cfg["source"], facet=cfg["facet"])
    return doc + "import re\n\n" + weights_block(cfg) + reward_core(cfg) + REWARD_TAIL


def nemo_reward_source(cfg):
    doc = NEMO_DOC.format(task_id=cfg["task_id"])
    head = (doc + "import re\nimport sys\n\nimport requests\n\n"
            'SID = "__CUA_GYM_SID__"\n'
            'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n\n')
    return head + weights_block(cfg) + reward_core(cfg) + NEMO_TAIL


# ---------------------------------------------------------------------------
# initial_setup.py
# ---------------------------------------------------------------------------

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{why}

Nothing here writes repo.fileOverlay, repo.treeOverlay, repo.commitOverlay or
repo.branchOverlay, which is all the rubric reads, so the untouched lane still
scores exactly 0.0.

Self-contained: standard library plus requests (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"

BASE_STATE = json.loads(r"""{base_state}""")

{overlay_block}
EXTRA_ISSUES = json.loads(r"""{extra}""")

NEXT_ISSUE_ID = {next_issue_id}


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {{}}
        state[deleted] = []
    state["newIssues"] = EXTRA_ISSUES
    next_ids = dict(BASE_STATE["nextIds"])
    next_ids["issue"] = NEXT_ISSUE_ID
    state["nextIds"] = next_ids
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
        print("SETUP FAILED: the two published snapshots disagree", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


def main():
    publish(build_state())


main()
'''


def setup_source(cfg):
    why = "\n".join(cfg["injection_note"])
    return SETUP_TEMPLATE.format(
        task_id=cfg["task_id"],
        why=why,
        base_state=BASE_STATE_JSON,
        overlay_block=OVERLAY_BLOCK,
        extra="\n" + json.dumps(cfg["injection"], indent=2, ensure_ascii=True) + "\n",
        next_issue_id=cfg["next_issue_id"],
    )


# ---------------------------------------------------------------------------
# manifests
# ---------------------------------------------------------------------------

def success_criteria(cfg):
    key = file_key(cfg)
    ref = cfg["branch"] or "main"
    urls = ", ".join("/%s/-/issues/%d" % (cfg["source"], i) for i in cfg["expected"])
    out = []
    if cfg["branch"]:
        out.append(
            'repo.branchOverlay["%s"] carries a branch named "%s".' % (SINK, cfg["branch"]))
    out.append('repo.fileOverlay["%s"] holds a non-empty committed body.' % key)
    out.append("That body carries the issue path of every one of %s." % urls)
    out.append("Those paths appear in exactly that order, newest-created issue first.")
    out.append(
        "The next-ranked issue /%s/-/issues/%d does not appear in the body."
        % (cfg["source"], cfg["next_iid"]))
    out.append("The digest is committed on ref %s of %s." % (ref, SINK))
    return out


def notes(cfg):
    out = [
        "Ground truth read from src/data/issues_index.json for %s: the rows with "
        "state 'opened' under %s, ordered by created_at descending exactly as "
        "src/pages/hooks.js:343 orders the default list. Expected iids in order: %r; "
        "the next-ranked row is %d."
        % (cfg["source"], cfg["facet"], cfg["expected"], cfg["next_iid"]),
        "Tie check: every created_at in the selected window is distinct to the second, "
        "so both the ordering and the N/N+1 boundary have exactly one answer.",
        "Writeback: repo.fileOverlay['%s'] via src/components/create/mutations.js:229 "
        "commitToRepo -> :155 writeFiles, reached from the repository tree's "
        "Add-to-tree menu (RepoTree.jsx:399) or the project overview '+' menu. A slash "
        "in the file-name box creates the folder (NewFile.jsx header comment)." % file_key(cfg),
        "The state-tab counters on the issue list are computed BEFORE the filter is "
        "applied (IssuablesList.jsx:888-893, filterIssuables at :895), so nothing in "
        "this task can be read off a tab badge; the agent must read the rendered rows, "
        "20 per page.",
        "The action cannot destroy its own retrieval premise: the digest is committed "
        "into byteblaze/gimmiethat.space, and the list it is derived from belongs to "
        "%s, which the commit does not touch." % cfg["source"],
        "URL form is not graded strictly: the reward locates each issue by its path "
        "'/%s/-/issues/<iid>', which both a bare path and a fully qualified URL "
        "contain." % cfg["source"],
    ]
    if cfg["branch"]:
        out.append(
            "The branch is created by typing it into the file editor's Target Branch "
            "field (FileEditor.jsx:249), which sets newBranch and reaches writeFiles "
            "with createBranch. The editor's 'Start a new merge request' checkbox is "
            "inert in this mock and nothing here depends on it.")
    return out


def build_task_json(cfg):
    meta = {
        "style": cfg["style"],
        "difficulty": cfg["difficulty"],
        "shape": "retrieval_writeback",
        "skills": cfg["skills"],
        "skill_chain": (
            "filter %s's issue list to the open rows under %s and let it sort by "
            "created date descending -> take the %d most recent rows in list order -> "
            "compose their URLs, order preserved, into %s/urls.txt committed on %s of "
            "byteblaze/gimmiethat.space"
            % (cfg["source"], cfg["facet"], len(cfg["expected"]), cfg["folder"],
               cfg["branch"] or "main")),
        "official_analogues": cfg["analogues"],
        "topic": "gitlab issue-URL digest",
        "inspiration_ids": cfg["inspiration_ids"],
        "authoring_notes": notes(cfg),
    }
    if cfg["hard_criteria"]:
        meta["hard_criteria"] = cfg["hard_criteria"]
    if cfg["injection"]:
        meta["injected_preconditions"] = cfg["injection_note"]
    return {
        "schema_version": 2,
        "task_id": cfg["task_id"],
        "instruction": cfg["instruction"],
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
        "metadata": meta,
    }


def build_instruction_json(cfg):
    return {
        "task_id": cfg["task_id"],
        "task_instruction": cfg["instruction"],
        "app_dir": "webarena_gitlab_mock",
        "start_path": "/",
        "difficulty": cfg["difficulty"],
        "success_criteria": success_criteria(cfg),
    }


def build_nemo_task(cfg, setup_code, reward_code):
    return {
        "task_payload": {
            "task_id": cfg["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": cfg["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": cfg["task_id"],
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup_code,
                "eval_reward_code": reward_code,
            },
        }
    }


# ---------------------------------------------------------------------------
# golden replay drafts
# ---------------------------------------------------------------------------

REPLAY_TEMPLATE = '''#!/usr/bin/env python3
"""Golden replay draft for {task_id}.

Click-only from '/': the single page.goto() is the landing on start_path.
Every later navigation follows a link, button or form control the page renders.

Path: landing -> navbar search -> {source} -> sidebar Issues
      -> {filter_hint} -> read the top {count} row links
      -> landing -> byteblaze/gimmiethat.space -> sidebar Repository -> Files
      -> Add to tree -> New file -> commit.

Selectors verified against the mock's source:
  navbar search input      Navbar.jsx    #search
  project result row       Search.jsx    link to /<full_path>
  sidebar Issues           ProjectSidebar.jsx  a.shortcuts-issues
  row label chip           IssuablesList.jsx:802  labelFilterUrl(...) link
  issue row title link     IssuablesList.jsx:772  [data-qa-selector=issuable_title_link]
  sidebar Repository       ProjectSidebar.jsx  a.shortcuts-tree
  Add-to-tree menu         RepoTree.jsx:399  button[aria-label='Add to tree']
  New file item            RepoTree.jsx:405
  editor fields            FileEditor.jsx:180/229/238/249/271
                           #file_name #editor #commit_message #branch_name
                           #commit-changes
"""
import pathlib
import re
import subprocess
import sys

import requests
from playwright.sync_api import sync_playwright

BUNDLE = pathlib.Path("/home/ubuntu/CUA-Gym/output/tasks/gitlab/{task_id}")
BASE = "http://localhost:8001"
SID = "{task_id}-golden"

SOURCE_PATH = "{source}"
SEARCH_TERM = "{search_term}"
LABEL_FILTER = {label_filter!r}
EXPECTED_IIDS = {expected}
FILE_PATH = "{folder}/urls.txt"
TARGET_BRANCH = {branch!r}
COMMIT_MESSAGE = "Add {folder}/urls.txt"

BODY = "\\n".join("%s/%s/-/issues/%d" % (BASE, SOURCE_PATH, iid)
                  for iid in EXPECTED_IIDS) + "\\n"


def sub(code):
    return code.replace("__CUA_GYM_SID__", SID).replace(
        "__CUA_GYM_WEBARENA_GITLAB_URL__", BASE)


def run_setup():
    setup = BUNDLE / "initial_setup.py"
    if not setup.is_file():
        requests.get(BASE + "/go?sid=" + SID, timeout=30)
        return
    done = subprocess.run([sys.executable, "-c", sub(setup.read_text())],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def score():
    done = subprocess.run(
        [sys.executable, "-c", sub((BUNDLE / "nemo_reward.py").read_text())],
        capture_output=True, text=True)
    found = re.search(r"REWARD: ([0-9.]+)", done.stdout)
    return float(found.group(1)) if found else -1.0


def flow(page):
    page.goto(BASE + "/?sid=" + SID, wait_until="networkidle")

    # 1. find the source project through the navbar search box
    page.fill("#search", SEARCH_TERM)
    page.press("#search", "Enter")
    page.wait_for_load_state("networkidle")
    page.click("a[href='/%s']" % SOURCE_PATH)
    page.wait_for_load_state("networkidle")

    # 2. sidebar Issues -> the default list is state=opened, sort=created_date
    page.click("a.shortcuts-issues")
    page.wait_for_load_state("networkidle")

    # 3. narrow the list. A rendered label chip on any row IS the filter link
    #    (IssuablesList.jsx:802), so no URL has to be typed.
{filter_step}
    # 4. confirm the head of the list is the slice being transferred
    links = page.locator("[data-qa-selector='issuable_title_link']")
    hrefs = [links.nth(i).get_attribute("href") for i in range(len(EXPECTED_IIDS))]
    for href, iid in zip(hrefs, EXPECTED_IIDS):
        assert href.endswith("/-/issues/%d" % iid), (href, iid)

    # 5. hop to the sink repo, which is byteblaze's own and listed on '/'
    page.click("a.gl-navbar-brand, a[href='/']")
    page.wait_for_load_state("networkidle")
    page.click("a[href^='/byteblaze/gimmiethat.space']")
    page.wait_for_load_state("networkidle")
    page.click("a.shortcuts-tree")
    page.wait_for_load_state("networkidle")

    # 6. new-file editor: the slash in FILE_PATH creates the folder
    page.click("button[aria-label='Add to tree']")
    page.click("a.dropdown-item:has-text('New file')")
    page.wait_for_selector("#file_name")
    page.fill("#file_name", FILE_PATH)
    page.fill("#editor", BODY)
    page.fill("#commit_message", COMMIT_MESSAGE)
    if TARGET_BRANCH is not None:
        page.fill("#branch_name", TARGET_BRANCH)
    page.click("#commit-changes")
    page.wait_for_load_state("networkidle")


def main():
    run_setup()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        flow(page)
        browser.close()
    print("score:", score())


main()
'''

FILTER_CLICK = '''    chip = page.locator("a.gl-label-link[href*='label_name']",
                        has_text=LABEL_FILTER).first
    chip.click()
    page.wait_for_load_state("networkidle")

'''

FILTER_NONE_TOKEN = '''    # "no labels at all" is the token bar's Label = None option
    page.click("[data-testid='filtered-search-input'], .gl-filtered-search-term input")
    page.click("[data-testid='filtered-search-suggestion']:has-text('Label')")
    page.click("[data-testid='filtered-search-suggestion']:has-text('=')")
    page.click("[data-testid='filtered-search-suggestion']:has-text('None')")
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")

'''

FILTER_DEFAULT = '''    # no facet beyond the default: state=opened, sort=created_date descending
    # (src/pages/hooks.js:64 and :343) is what the page already renders.

'''


def replay_source(cfg):
    if cfg["facet"].startswith("label None"):
        step, hint, label = FILTER_NONE_TOKEN, "token bar Label = None", None
    elif cfg["facet"].startswith("the `"):
        label = cfg["facet"].split("`")[1]
        step, hint = FILTER_CLICK, "click the %s label chip" % label
    else:
        step, hint, label = FILTER_DEFAULT, "keep the default open-issues view", None
    return REPLAY_TEMPLATE.format(
        task_id=cfg["task_id"],
        source=cfg["source"],
        search_term=cfg["source"].split("/")[-1],
        label_filter=label,
        expected=repr(cfg["expected"]),
        folder=cfg["folder"],
        branch=cfg["branch"],
        count=len(cfg["expected"]),
        filter_hint=hint,
        filter_step=step,
    )


# ---------------------------------------------------------------------------
# emit
# ---------------------------------------------------------------------------

def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    rows = []
    index = []
    for cfg in TASKS:
        bundle = OUT / cfg["task_id"]
        bundle.mkdir(parents=True, exist_ok=True)
        reward = reward_source(cfg)
        nemo_reward = nemo_reward_source(cfg)
        compile(reward, cfg["task_id"] + "/reward.py", "exec")
        compile(nemo_reward, cfg["task_id"] + "/nemo_reward.py", "exec")
        (bundle / "reward.py").write_text(reward)
        (bundle / "nemo_reward.py").write_text(nemo_reward)
        setup_code = None
        if cfg["injection"]:
            setup_code = setup_source(cfg)
            compile(setup_code, cfg["task_id"] + "/initial_setup.py", "exec")
            (bundle / "initial_setup.py").write_text(setup_code)
        (bundle / "task.json").write_text(
            json.dumps(build_task_json(cfg), indent=2, ensure_ascii=False) + "\n")
        (bundle / "task_instruction.json").write_text(
            json.dumps(build_instruction_json(cfg), indent=2, ensure_ascii=False) + "\n")
        row = build_nemo_task(cfg, setup_code, nemo_reward)
        (bundle / "nemo_task.json").write_text(
            json.dumps(row, indent=2, ensure_ascii=False) + "\n")
        rows.append(json.dumps(row, ensure_ascii=False))
        (REPLAYS / (cfg["task_id"] + ".py")).write_text(replay_source(cfg))
        index.append({"task_id": cfg["task_id"], "path": "../../%s/task.json" % cfg["task_id"]})
    (BATCH / "nemo_tasks.jsonl").write_text("\n".join(rows) + "\n")
    (BATCH / "index.json").write_text(
        json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    words = [(c["task_id"], len(c["instruction"].split()), c["style"]) for c in TASKS]
    for t, n, s in words:
        print("%-52s %-8s %d words" % (t, s, n))


main()
