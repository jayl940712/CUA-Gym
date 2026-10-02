#!/usr/bin/env python3
"""Batch-6 lane 9 (gitlab, R6 -> A3) bundle writer. Authoring tool only."""
import json
import os
import textwrap

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/gitlab")
BATCH = os.path.join(OUT, "_batches/phrase_search_grant_access")
REPLAYS = os.path.join(BATCH, "replays")

ROLE_NAME = {10: "Guest", 20: "Reporter", 30: "Developer", 40: "Maintainer", 50: "Owner"}

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

MEMBER_EDIT_180 = r"""{
  "203": {
    "id": 203,
    "source_type": "project",
    "source_id": 180,
    "user_id": 2330,
    "access_level": 40,
    "access_label": "Maintainer",
    "created_at": "2023-03-27 20:39:33.499757",
    "expires_at": null,
    "created_by_id": 2367
  }
}"""

PROJECT_EDIT_177 = r"""{
  "177": {
    "id": 177,
    "full_path": "xiaozi/solarized-prism-theme",
    "path": "solarized-prism-theme",
    "name": "solarized-prism-theme",
    "namespace": {"id": 2525, "path": "xiaozi", "name": "小子欠扁", "kind": "user"},
    "description": "Accessible light and dark syntax highlighting themes for prism.js",
    "visibility": "public",
    "star_count": 0,
    "forks_count": 1,
    "archived": false,
    "created_at": "2023-03-27 20:09:28.40426",
    "last_activity_at": "2023-03-27 20:09:28.40426",
    "default_branch": "master",
    "commit_count": 7,
    "repo_size": 104857,
    "open_issues_count": 0,
    "closed_issues_count": 0,
    "open_mrs_count": 0,
    "merged_mrs_count": 0,
    "closed_mrs_count": 0,
    "auto_devops_quick_link": true
  }
}"""

TASKS = [
    dict(
        n=1, slug="a11yproject_community_effort",
        pid=174, full_path="a11yproject/a11yproject.com",
        phrase="community-driven effort to make digital accessibility easier",
        grants=[(620, "kentonv", "Kenton Varda", 30), (278, "vinta", "Vinta Chen", 30)],
        style="terse", shape="retrieval_writeback",
        instruction=("Search the projects for the one described as a community-driven effort to make "
                     "digital accessibility easier, then invite kentonv and vinta to it as Developers."),
        setup=None, derived_from=None,
    ),
    dict(
        n=2, slug="webring_practitioners",
        pid=179, full_path="byteblaze/a11y-webring.club",
        phrase="webring for digital accessibility practitioners",
        grants=[(7, "aklsh", "Akilesh Kannan", 20), (2365, "davepgreene", "Dave Greene", 20)],
        style="terse", shape="retrieval_writeback",
        instruction=("Find my repo whose description calls it a webring for digital accessibility "
                     "practitioners, then add aklsh and davepgreene there as Reporters."),
        setup=None, derived_from=None,
    ),
    dict(
        n=3, slug="need_some_space",
        pid=184, full_path="byteblaze/gimmiethat.space",
        phrase="I need some space",
        grants=[(2348, "panicsteve", "Steven Frank", 40)],
        style="terse", shape="retrieval_writeback",
        instruction=("One of my repos has the description \"I need some space.\" and nothing else. "
                     "Track it down and give panicsteve Maintainer access on it."),
        setup=None, derived_from=None,
    ),
    dict(
        n=4, slug="html5_doctor_element_index",
        pid=185, full_path="byteblaze/accessible-html-content-patterns",
        phrase="HTML5 Doctor Element Index",
        grants=[(1842, "lahwaacz", "Jakub Klinkovsky", 10), (278, "vinta", "Vinta Chen", 10)],
        style="explicit", shape="retrieval_writeback",
        instruction=("Use the search box in the top navigation bar to find the project whose description "
                     "mentions the full HTML5 Doctor Element Index. Open that project, go to Project "
                     "information > Members, and invite the users lahwaacz and vinta with the Guest role."),
        setup=None, derived_from=None,
    ),
    dict(
        n=5, slug="snake_people_extension",
        pid=187, full_path="byteblaze/millennials-to-snake-people",
        phrase="Snake People",
        grants=[(2347, "xiaozi", "Xiaozi", 30), (2367, "primer", "Primer", 30)],
        style="terse", shape="retrieval_writeback",
        instruction=("Search for the project about replacing occurrences of 'Millennials' with 'Snake "
                     "People' and grant xiaozi and primer Developer access on it."),
        setup=None, derived_from=None,
    ),
    dict(
        n=6, slug="computer_setup_dotfiles",
        pid=193, full_path="byteblaze/dotfiles",
        phrase="Computer setup",
        grants=[(620, "kentonv", "Kenton Varda", 40)],
        style="terse", shape="retrieval_writeback",
        instruction=("Find the repo of mine whose description is just \"Computer setup\", then give "
                     "kentonv Maintainer access there."),
        setup=None, derived_from=None,
    ),
    dict(
        n=7, slug="personal_website_repo",
        pid=182, full_path="byteblaze/ericwbailey.website",
        phrase="Repo for my personal website",
        grants=[(5, "abisubramanya27", "Abishek S", 40), (168, "yjlou", "yjlou", 40)],
        style="terse", shape="mutation",
        instruction=("Find my repo whose description says it is the repo for my personal website, then "
                     "add abisubramanya27 and yjlou to it as Maintainers."),
        setup=None, derived_from=None,
    ),
    dict(
        n=8, slug="rails_time_tracking_tool",
        pid=190, full_path="byteblaze/timeit",
        phrase="Rails implementation of time tracking tool",
        grants=[(7, "aklsh", "Akilesh Kannan", 30), (278, "vinta", "Vinta Chen", 30),
                (2365, "davepgreene", "Dave Greene", 30)],
        style="explicit", shape="mutation",
        instruction=("Search GitLab for the project described as a Rails implementation of a time "
                     "tracking tool. Two projects match, so pick the one that lives in my own byteblaze "
                     "namespace. Open its Members page and invite aklsh, vinta and davepgreene, all "
                     "with the Developer role."),
        setup=None, derived_from=None,
    ),
    dict(
        n=9, slug="primer_design_guidelines",
        pid=180, full_path="primer/design",
        phrase="Primer Design Guidelines",
        grants=[(2365, "davepgreene", "Dave Greene", 20), (620, "kentonv", "Kenton Varda", 20)],
        style="explicit", shape="mutation",
        instruction=("Find the project whose description is exactly \"Primer Design Guidelines\" using "
                     "the search box in the top navigation bar. Open its Members page and invite "
                     "davepgreene and kentonv there with the Reporter role."),
        setup="member_edit_180",
        derived_from="conditional_thread_reply_datatable_guidelines_primer_002",
    ),
    dict(
        n=10, slug="accessible_syntax_themes",
        pid=186, full_path="byteblaze/a11y-syntax-highlighting",
        phrase="Accessible light and dark syntax highlighting themes",
        grants=[(2348, "panicsteve", "Steven Frank", 10), (5, "abisubramanya27", "Abishek S", 10)],
        style="terse", shape="mutation",
        instruction=("Two projects are described as accessible light and dark syntax highlighting "
                     "themes. Take the one in my own namespace and invite panicsteve and "
                     "abisubramanya27 to it as Guests."),
        setup="project_edit_177",
        derived_from=None,
    ),
]

ANALOGUES = [
    "Invite Benoit Blanchon and Abishek S as collaborator(s) to my HTML5 markup extention repo",
    "Add the following users to repo a11y-webring.club as developer: \"abisubramanya27\" and \"lahwaacz\"",
    "Add the following users to repo millennials-to-snake-people as reporter: \"yjlou\" and \"a11yproject\"",
    "Invite Jakub K, Alex Dills, Alex Hutnik and Benoit Blanchon as collaborator(s) to my time tracking tool project repo",
]


def comp_name(username, level):
    return "%s_is_%s_on_target" % (username, ROLE_NAME[level].lower())


def weights(grants):
    names = [comp_name(u, lv) for _, u, _, lv in grants]
    exact = "target_membership_additions_exact"
    if len(grants) == 1:
        w = {names[0]: 0.7, exact: 0.3}
    elif len(grants) == 2:
        w = {names[0]: 0.4, names[1]: 0.4, exact: 0.2}
    else:
        w = {names[0]: 0.25, names[1]: 0.25, names[2]: 0.25, exact: 0.25}
    return w, exact


REWARD_BODY = '''
COMPONENT_WEIGHTS = {weights}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

TARGET_PROJECT_ID = {pid}
TARGET_FULL_PATH = {full_path!r}
GRANTS = {grants}
GRANT_COMPONENTS = {grant_components}
EXACT_COMPONENT = {exact!r}


def _dict(value):
    return value if isinstance(value, dict) else {{}}


def _list(value):
    return value if isinstance(value, list) else []


def _level(row):
    raw = _dict(row).get("access_level")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return -1


def _target_rows(state):
    """Every agent-created member row on the derived target project.

    MembersTable.jsx:198 invite -> mutations.js:363 addMembers appends one row
    per invited user; overlayShape.js maps the members collection to
    `newMembers`, so the persisted state carries the rows directly. Reads
    current_state only.
    """
    rows = []
    for row in _list(_dict(state).get("newMembers")):
        if not isinstance(row, dict):
            continue
        if str(row.get("source_type")) != "project":
            continue
        if str(row.get("source_id")) != str(TARGET_PROJECT_ID):
            continue
        rows.append(row)
    return rows


def score_state(state):
    state = _dict(state)
    rows = _target_rows(state)

    checks = {{}}
    details = {{}}
    for index in range(len(GRANTS)):
        user_id, level = GRANTS[index]
        name = GRANT_COMPONENTS[index]
        mine = [r for r in rows if str(r.get("user_id")) == str(user_id)]
        checks[name] = bool(len(mine) == 1 and _level(mine[0]) == level)
        details[name] = "rows for user %s on project %s == %d, levels == %r (want exactly 1 at %d)" % (
            user_id, TARGET_PROJECT_ID, len(mine), [_level(r) for r in mine], level)

    got = sorted([(str(r.get("user_id")), _level(r)) for r in rows])
    want = sorted([(str(u), int(l)) for u, l in GRANTS])
    checks[EXACT_COMPONENT] = bool(got == want)
    details[EXACT_COMPONENT] = "member additions on %s (project %s) == %r (want %r)" % (
        TARGET_FULL_PATH, TARGET_PROJECT_ID, got, want)

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

LOCAL_TAIL = '''

def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    app = apps.get("gitlab")
    if not isinstance(app, dict):
        app = apps.get("webarena_gitlab_mock")
    if not isinstance(app, dict):
        for value in apps.values():
            if isinstance(value, dict) and "current_state" in value:
                app = value
                break
    state = _dict(_dict(app).get("current_state"))
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
    except Exception as exc:
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{purpose}

Self-contained: standard library plus requests (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"

BASE_STATE = json.loads(r"""{base_state}""")

OVERLAY_COLLECTIONS = [
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

INJECTED = json.loads(r"""{injected}""")

INJECT_KEY = "{inject_key}"


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {{}}
        state[deleted] = []
    state[INJECT_KEY] = INJECTED
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

SETUP_SPECS = {
    "member_edit_180": dict(
        key="memberEdits", payload=MEMBER_EDIT_180,
        purpose=(
            "Raises byteblaze's existing seeded membership on primer/design (project 180,\n"
            "member row id 203) from Developer (30) to Maintainer (40) by replacing the frozen\n"
            "member record through the memberEdits overlay.\n\n"
            "Why: MembersTable.jsx:182 computes `canManage = ownAccess >= 40` and renders the\n"
            "Invite members control only when it is true. On the pristine seed byteblaze is a\n"
            "Developer on primer/design, so the control does not exist and the task would be\n"
            "unperformable. Bumping one seeded row to Maintainer is the minimum precondition\n"
            "that opens it, and it is an ordinary state for a long-standing Primer contributor.\n\n"
            "Nothing in the rubric is pre-satisfied: the rubric reads `newMembers` only, and\n"
            "this injection writes `memberEdits`. `newMembers` stays empty, so the untouched\n"
            "lane scores exactly 0.0."
        ),
        note=("memberEdits['203'] replaces the frozen member row for byteblaze on primer/design "
              "with the same record at access_level 40 / access_label Maintainer, so "
              "MembersTable.jsx:182 canManage becomes true and the Invite members button renders."),
    ),
    "project_edit_177": dict(
        key="projectEdits", payload=PROJECT_EDIT_177,
        purpose=(
            "Plants a search distractor. projectEdits['177'] replaces the frozen record for\n"
            "xiaozi/solarized-prism-theme with the same project carrying the description\n"
            "\"Accessible light and dark syntax highlighting themes for prism.js\".\n\n"
            "Why: Search.jsx:74 matches a project on name, full_path or description, so the\n"
            "phrase in the instruction now returns TWO rows -- the distractor and the real\n"
            "target byteblaze/a11y-syntax-highlighting (project 186). The agent has to apply\n"
            "the namespace predicate rather than take the first hit. On the pristine seed the\n"
            "phrase is unique and the retrieval is a single click.\n\n"
            "Nothing in the rubric is pre-satisfied: the rubric reads `newMembers` only, and\n"
            "this injection writes `projectEdits`. The untouched lane scores exactly 0.0."
        ),
        note=("projectEdits['177'] rewrites xiaozi/solarized-prism-theme's description to the same "
              "phrase the instruction quotes, so the projects-scope search returns two candidates "
              "and only the byteblaze-namespace one is correct."),
    ),
}


REPLAY_TEMPLATE = '''"""Golden replay DRAFT for {task_id}.

Chain: navbar search for the phrase -> projects scope -> open the derived
project -> Project information -> Members -> Invite members -> role select ->
Invite.

Not executed by the author (batch-6 contract: authors run no validation code).
"""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001"
SID = "REPLACE_ME"
PHRASE = {phrase!r}
FULL_PATH = {full_path!r}
INVITEES = {invitees!r}
ROLE_VALUE = "{role_value}"


def run(page):
    page.goto(BASE + "/?sid=" + SID)

    # --- R6: phrase search in the navbar, projects scope --------------------
    box = page.locator("#search, input[name='search']").first
    box.click()
    box.fill(PHRASE)
    box.press("Enter")
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Projects", exact=False).first.click()
    page.wait_for_load_state("networkidle")

    # Click the row whose full path is the derived target.
    page.get_by_role("link", name=FULL_PATH, exact=False).first.click()
    page.wait_for_load_state("networkidle")

    # --- A3: Project information -> Members ---------------------------------
    # Sidebar sub-items never appear on hover: click the section, land on
    # /activity, then click the child (census gitlab.md 4.4).
    page.get_by_role("link", name="Project information").first.click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("link", name="Members").first.click()
    page.wait_for_load_state("networkidle")

    page.locator("[data-qa-selector='invite_members_button']").click()
    for username in INVITEES:
        page.locator("#invite-members-search").fill(username)
        page.locator("ul.dropdown-menu.show li button.dropdown-item").first.click()
    # Native <select>, not the button+<ul> used by the per-row Max role control.
    page.select_option("#invite-members-role", ROLE_VALUE)
    page.get_by_role("button", name="Invite").last.click()
    page.wait_for_timeout(500)


with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page()
    run(pg)
    browser.close()
'''


def build(task):
    tid = "phrase_search_grant_access_%s_%03d" % (task["slug"], task["n"])
    d = os.path.join(OUT, tid)
    os.makedirs(d, exist_ok=True)
    grants = task["grants"]
    w, exact = weights(grants)
    grant_components = [comp_name(u, lv) for _, u, _, lv in grants]
    role_levels = sorted(set(lv for _, _, _, lv in grants))
    assert len(role_levels) == 1, tid
    level = role_levels[0]

    body = REWARD_BODY.format(
        weights=json.dumps(w, indent=4).replace("\n}", "\n}"),
        pid=task["pid"],
        full_path=task["full_path"],
        grants=repr([(uid, lv) for uid, _, _, lv in grants]),
        grant_components=repr(grant_components),
        exact=exact,
    )

    doc_common = (
        "The target project is DERIVED: the instruction quotes a phrase that appears in exactly\n"
        "one project's title/description (Search.jsx:74 matches name, full_path and description),\n"
        "and never names the project. %s (project %d) is the only match%s.\n\n"
        "Mechanism: MembersTable.jsx:198 invite -> mutations.js:363 addMembers appends one member\n"
        "row per invited user; overlayShape.js:48 persists them as `newMembers`. The rubric reads\n"
        "current_state only and asserts the resulting rows, never that something was left alone."
        % (task["full_path"], task["pid"],
           " once the namespace predicate is applied" if task["setup"] == "project_edit_177"
           else (" in the byteblaze namespace" if task["n"] in (8,) else ""))
    )

    local_doc = ('"""\nDeterministic reward for %s.\n\n%s\n\nReads the frozen evidence bundle handed to evaluate().\n"""\n'
                 % (tid, doc_common))
    nemo_doc = ('"""\nDeterministic reward for %s.\n\n%s\n\nReads GET /go?sid=... and prints REWARD: <float> on every output path.\n"""\n'
                % (tid, doc_common))

    with open(os.path.join(d, "reward.py"), "w") as f:
        f.write(local_doc + body + LOCAL_TAIL)

    with open(os.path.join(d, "nemo_reward.py"), "w") as f:
        f.write(nemo_doc
                + "import sys\n\nimport requests\n\n"
                + 'SID = "__CUA_GYM_SID__"\n'
                + 'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n'
                + body + NEMO_TAIL)

    setup_src = None
    injections = []
    if task["setup"]:
        spec = SETUP_SPECS[task["setup"]]
        setup_src = SETUP_TEMPLATE.format(
            task_id=tid, purpose=spec["purpose"],
            base_state=BASE_STATE_JSON, injected=spec["payload"], inject_key=spec["key"])
        with open(os.path.join(d, "initial_setup.py"), "w") as f:
            f.write(setup_src)
        injections = [spec["note"]]

    role_label = ROLE_NAME[level]
    criteria = []
    for uid, un, name, lv in grants:
        criteria.append(
            "current_state.newMembers holds exactly one row with source_type \"project\", source_id %d "
            "and user_id %d (@%s), at access_level %d (%s)." % (task["pid"], uid, un, lv, ROLE_NAME[lv]))
    criteria.append(
        "The complete set of member rows added to project %d (%s) is exactly %s."
        % (task["pid"], task["full_path"],
           ", ".join("user %d at level %d" % (uid, lv) for uid, _, _, lv in grants)))

    ti = {
        "task_id": tid,
        "task_instruction": task["instruction"],
        "app_dir": "webarena_gitlab_mock",
        "start_path": "/",
        "difficulty": "medium",
        "success_criteria": criteria,
    }
    with open(os.path.join(d, "task_instruction.json"), "w") as f:
        json.dump(ti, f, indent=2)
        f.write("\n")

    notes = [
        "Phrase uniqueness checked against all 175 rows of src/data/projects.json using Search.jsx:74's "
        "own predicate (name OR full_path OR description, case-insensitive substring): %r resolves to %s."
        % (task["phrase"], task["full_path"]),
        "MembersTable.jsx:182 gates the Invite members control on canManage = ownAccess >= 40. " + (
            "byteblaze (user 2330) is Maintainer (40) on a11yproject/a11yproject.com via seeded member "
            "row 194, so the control renders." if task["pid"] == 174 else
            "byteblaze (user 2330) is only Developer (30) on primer/design in the pristine seed, so "
            "initial_setup.py raises member row 203 to Maintainer (40) to open the control." if task["pid"] == 180 else
            "byteblaze (user 2330) is Owner (50) on this project of his own, so the control renders."),
        "The invite-modal role control is a native <select id=\"invite-members-role\"> "
        "(MembersTable.jsx:572) with values 10/20/30/40/50; the per-row Max role control is a "
        "button+<ul> Dropdown and is NOT used by this task.",
        "Invitee candidacy verified: MembersTable.jsx:186 excludes existing members, and none of %s is "
        "already a member of project %d in src/data/members.json."
        % (", ".join("@" + u for _, u, _, _ in grants), task["pid"]),
        "Click path from '/': navbar search box -> /search?scope=projects -> the project row -> sidebar "
        "Project information (lands on /activity) -> Members -> Invite members. Sidebar sub-items never "
        "appear on hover, so the two-click gesture is required.",
        "An agent that skips the search cannot know which project to open; the instruction names no "
        "project, so the untouched state and every wrong-project run score 0.0.",
    ]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": task["instruction"],
        "apps": [
            {
                "name": "webarena_gitlab_mock",
                "source_name": "gitlab",
                "base_url_env": "CUA_GYM_WEBARENA_GITLAB_URL",
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
        "metadata": {
            "style": task["style"],
            "difficulty": "medium",
            "shape": task["shape"],
            "skills": ["R6", "A3"],
            "skill_chain": (
                "R6 find the project by the quoted phrase through the navbar search (projects scope) "
                "-> A3 open that project's Members page and invite %s at %s"
                % (" and ".join("@" + u for _, u, _, _ in grants), role_label)),
            "derived_from": task["derived_from"],
            "official_analogues": ANALOGUES,
            "injected_preconditions": injections,
            "topic": "gitlab phrase search then membership grant",
            "lane": "phrase_search_grant_access",
            "inspiration_ids": ["webarena-107", "webarena-108", "webarena-111", "webarena-182"],
            "authoring_notes": notes,
        },
    }
    if task["setup"]:
        manifest["initial_setup_path"] = "initial_setup.py"
    with open(os.path.join(d, "task.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(os.path.join(d, "nemo_reward.py")) as f:
        nemo_reward_src = f.read()

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward_src,
            },
        }
    }
    with open(os.path.join(d, "nemo_task.json"), "w") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)
        f.write("\n")

    os.makedirs(REPLAYS, exist_ok=True)
    with open(os.path.join(REPLAYS, tid + ".py"), "w") as f:
        f.write(REPLAY_TEMPLATE.format(
            task_id=tid, phrase=task["phrase"], full_path=task["full_path"],
            invitees=[u for _, u, _, _ in grants], role_value=str(level)))

    return tid, row


def main():
    os.makedirs(BATCH, exist_ok=True)
    rows = []
    ids = []
    for t in TASKS:
        tid, row = build(t)
        ids.append(tid)
        rows.append(row)
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump({"schema_version": 2,
                   "tasks": [{"task_id": i, "path": "../../%s/task.json" % i} for i in ids]},
                  f, indent=2)
        f.write("\n")
    for i in ids:
        print(i)


main()
