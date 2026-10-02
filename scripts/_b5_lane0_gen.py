#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 0 (gitlab / top_contributor_join_issue).

Emits ten schema-v2 bundles under output/tasks/gitlab/<task_id>/ plus the
batch's GENERATION.md, index.json, nemo_tasks.jsonl and golden replay drafts.

This file is authoring tooling, not a runtime artefact.
"""
import json
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
SITE = ROOT / "output/tasks/gitlab"
BATCH = SITE / "_batches/top_contributor_join_issue"
REPLAYS = BATCH / "replays"

APP_DIR = "webarena_gitlab_mock"
URL_TOKEN = "__CUA_GYM_WEBARENA_GITLAB_URL__"

A_USERNAME = ("Get the username(s) of the user(s) with the most commits to the "
              "primer/design project")
A_EMAILS = ("Get the email addresses of the top 3 contributors (by commit count) "
            "to Pytorch GAN repo")
A_FULLNAME = ("Tell me the full name, gitlab account name, location and email "
              "address of the contributor who has the most commits to branch php52")
A_CREATE = ('Create an issue in a11yproject repo with title "401 bad gateway". '
            "Assign the issue to Roshanjossey (you can invite users to the project "
            "if needed). Set due date to be the end of 2030")
A_EMAIL1 = ("Get the email address of the contributor who has the most commits to "
            "branch master in the current repository")
A_ASSIGN = "Assign the issue regarding 404 errors in a11yproject to Roshanjossey."
A_CREATE2 = ('Create an issue in my empathy-prompts repo with title "Integrating '
             'LLMs for better prompts". Assign the issue to Roshanjossey (you can '
             "invite users to the project if needed). Set due date to be the "
             "beginning of Q2 2033")

# ---------------------------------------------------------------------------
# Shared setup pieces
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
  "nextIds": {"project": 194, "group": 7, "issue": 83821, "mr": 139278, "note": 310827,
              "label": 1927, "milestone": 590, "member": 206}
}
"""

SETUP_PREAMBLE = '''"""NeMo-Gym setup program for %(task_id)s.

%(why)s

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
The full createInitialData() document is posted, so `initial_state` is the
complete injected baseline and no later diff is confused by a partial set.
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url_token)s"

BASE_STATE = json.loads(r"""%(base_state)s""")

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


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = json.loads(json.dumps(BASE_STATE))
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {}
        state[deleted] = []
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

'''


def star_setup(task_id, why, stars_json, project_edits_json, guard_project_ids):
    body = SETUP_PREAMBLE % {
        "task_id": task_id, "why": why, "url_token": URL_TOKEN,
        "base_state": BASE_STATE_JSON,
    }
    body += '''
# byteblaze's own star rows. `state.stars` is what /dashboard/projects/starred
# filters on (DashboardProjects.jsx:90).
INJECTED_STARS = json.loads(r"""%(stars)s""")

# ProjectOverview.toggleStar bumps the project's own star_count as well as
# appending the join row, and `sortProjects` / ProjectRow read star_count
# (pages/hooks.js:357, DashboardProjects.jsx:35). Writing the whole project
# record back through projectEdits keeps the rendered counts honest.
INJECTED_PROJECT_EDITS = json.loads(r"""%(edits)s""")

GUARD_PROJECT_IDS = %(guard)r


def main():
    state = build_state()
    ids = sorted(row["project_id"] for row in INJECTED_STARS)
    if ids != sorted(GUARD_PROJECT_IDS):
        raise SystemExit("fixture error: injected star set drifted from the design")
    state["newStars"] = INJECTED_STARS
    state["projectEdits"] = INJECTED_PROJECT_EDITS
    publish(state)


main()
''' % {"stars": stars_json, "edits": project_edits_json, "guard": guard_project_ids}
    return body


def member_setup(task_id, why, members_json, next_member_id):
    body = SETUP_PREAMBLE % {
        "task_id": task_id, "why": why, "url_token": URL_TOKEN,
        "base_state": BASE_STATE_JSON,
    }
    body += '''
# MembersTable.jsx:182 sets `canManage = ownAccess >= 40`, so the Invite
# members control renders only for a Maintainer or Owner of the source. On the
# pristine seed byteblaze holds no role on this project and the button is
# absent; this row is what makes the invite reachable.
INJECTED_MEMBERS = json.loads(r"""%(members)s""")

NEXT_MEMBER_ID = %(next_id)d


def main():
    state = build_state()
    for row in INJECTED_MEMBERS:
        if row["access_level"] < 40:
            raise SystemExit("fixture error: injected role cannot manage members")
        if row["id"] >= NEXT_MEMBER_ID:
            raise SystemExit("fixture error: injected member id collides with the counter")
    state["newMembers"] = INJECTED_MEMBERS
    state["nextIds"]["member"] = NEXT_MEMBER_ID
    publish(state)


main()
''' % {"members": members_json, "next_id": next_member_id}
    return body


# ---------------------------------------------------------------------------
# Reward template
# ---------------------------------------------------------------------------

REWARD_CORE = '''
COMPONENT_WEIGHTS = %(weights)s
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

PROJECT_ID = %(project_id)d
TITLE = %(title)r
HANDLE_NEEDLE = %(handle_needle)r
USER_ID = %(user_id)d
DUE_DATE = %(due_date)r
DETAIL_TOKENS = %(detail_tokens)r
DETAIL_NUMBERS = %(detail_numbers)r
INVITE_PROJECT_ID = %(invite_project)r
INVITE_USER_ID = %(invite_user)r
INVITE_ACCESS_LEVEL = %(invite_level)r


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _ids(value):
    out = []
    for item in _list(value):
        if isinstance(item, bool):
            continue
        if isinstance(item, int):
            out.append(item)
        elif isinstance(item, float) and float(item).is_integer():
            out.append(int(item))
        elif isinstance(item, str) and item.strip().isdigit():
            out.append(int(item.strip()))
    return out


def _new_issues(state):
    return [r for r in _list(_dict(state).get("newIssues")) if isinstance(r, dict)]


def _in_project(state):
    rows = []
    for row in _new_issues(state):
        pid = row.get("project_id")
        if isinstance(pid, str) and pid.strip().isdigit():
            pid = int(pid.strip())
        if pid == PROJECT_ID:
            rows.append(row)
    return rows


def _titled(state):
    return [r for r in _in_project(state) if _text(r.get("title")) == TITLE]


def _details_present(description):
    for token in DETAIL_TOKENS:
        if token not in description:
            return False
    for number in DETAIL_NUMBERS:
        if not re.search(r"(?<![0-9])" + re.escape(str(number)) + r"(?![0-9])", description):
            return False
    return True


def _invited(state):
    if INVITE_PROJECT_ID is None:
        return False
    for row in _list(_dict(state).get("newMembers")):
        if not isinstance(row, dict):
            continue
        if _text(row.get("source_type")).lower() != "project":
            continue
        source = row.get("source_id")
        user = row.get("user_id")
        level = row.get("access_level")
        if isinstance(source, str) and source.strip().isdigit():
            source = int(source.strip())
        if isinstance(user, str) and user.strip().isdigit():
            user = int(user.strip())
        if isinstance(level, str) and level.strip().isdigit():
            level = int(level.strip())
        if source == INVITE_PROJECT_ID and user == INVITE_USER_ID and level == INVITE_ACCESS_LEVEL:
            return True
    return False


def score_state(state):
    in_project = _in_project(state)
    titled = _titled(state)
    issue = titled[0] if len(titled) == 1 else None
    description = _text(issue.get("description")).lower() if issue is not None else ""
    assignees = _ids(issue.get("assignee_ids")) if issue is not None else []

    facts = {
%(facts)s
    }
    details = {
%(details)s
    }
    components = []
    for name in COMPONENT_WEIGHTS:
        ok = bool(facts.get(name))
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

REWARD_HEADER = '''"""Deterministic reward for %(task_id)s.

%(rubric)s

Reads `current_state` only. The scored writeback is the created issue record in
`newIssues` (NewIssue.jsx:63 `appendTo('issues', ...)`) together with its
`assignee_ids`%(extra_keys)s.
"""
import re
'''

REWARD_TAIL = '''

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

NEMO_HEADER = '''"""NeMo-Gym reward program for %(task_id)s.

Same rubric as reward.py, read from GET /go?sid=... instead of a frozen
evidence bundle. Prints REWARD: <float> on every output path.

Self-contained: standard library plus `requests`.
"""
import re
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url_token)s"
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


def render_core(spec):
    facts_src = "\n".join("        %r: %s," % (name, expr)
                          for name, expr in spec["facts"])
    details_src = "\n".join("        %r: %s," % (name, expr)
                            for name, expr in spec["details"])
    return REWARD_CORE % {
        "weights": json.dumps(spec["weights"], indent=4).replace("\n", "\n"),
        "project_id": spec["project_id"],
        "title": spec["title"],
        "handle_needle": spec["handle_needle"],
        "user_id": spec["user_id"],
        "due_date": spec.get("due_date", ""),
        "detail_tokens": spec.get("detail_tokens", []),
        "detail_numbers": spec.get("detail_numbers", []),
        "invite_project": spec.get("invite_project"),
        "invite_user": spec.get("invite_user"),
        "invite_level": spec.get("invite_level"),
        "facts": facts_src,
        "details": details_src,
    }


def write_bundle(spec):
    d = SITE / spec["task_id"]
    d.mkdir(parents=True, exist_ok=True)

    core = render_core(spec)
    reward = (REWARD_HEADER % {"task_id": spec["task_id"], "rubric": spec["rubric"],
                               "extra_keys": spec.get("extra_keys", "")}) + core + REWARD_TAIL
    nemo = (NEMO_HEADER % {"task_id": spec["task_id"], "url_token": URL_TOKEN}) + core + NEMO_TAIL
    (d / "reward.py").write_text(reward)
    (d / "nemo_reward.py").write_text(nemo)

    setup_src = spec.get("setup")
    if setup_src:
        (d / "initial_setup.py").write_text(setup_src)
    else:
        p = d / "initial_setup.py"
        if p.exists():
            p.unlink()

    (d / "task_instruction.json").write_text(json.dumps({
        "task_id": spec["task_id"],
        "task_instruction": spec["instruction"],
        "app_dir": APP_DIR,
        "start_path": "/",
        "difficulty": spec["difficulty"],
        "success_criteria": spec["success_criteria"],
    }, indent=2) + "\n")

    metadata = {
        "style": spec["style"],
        "difficulty": spec["difficulty"],
        "shape": "retrieval_writeback",
        "skills": spec["skills"],
        "skill_chain": spec["skill_chain"],
        "official_analogues": spec["analogues"],
        "topic": "gitlab top contributor join issue",
        "inspiration_ids": spec["inspiration_ids"],
        "authoring_notes": spec["notes"],
    }
    if spec["difficulty"] == "hard":
        metadata["hard_criteria"] = spec["hard_criteria"]
    if setup_src:
        metadata["injected_preconditions"] = spec["injected"]

    (d / "task.json").write_text(json.dumps({
        "schema_version": 2,
        "task_id": spec["task_id"],
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
        "task_id": spec["task_id"],
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [APP_DIR],
        "start_urls": [],
        "intent": spec["instruction"],
        "eval": {"eval_types": ["string_match"], "reference_answers": None,
                 "note": "unused - CUA-Gym reward code is authoritative"},
        "cuagym": {
            "bundle_id": spec["task_id"],
            "app_dir": APP_DIR,
            "initial_setup": setup_src if setup_src else None,
            "eval_reward_code": nemo,
        },
    }}
    (d / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n")
    (REPLAYS / (spec["task_id"] + ".py")).write_text(spec["replay"])
    return row


# ---------------------------------------------------------------------------
# Fixture builders that read the seed corpus at AUTHORING time and inline the
# result into initial_setup.py. Nothing is read at episode time.
# ---------------------------------------------------------------------------

SEED = ROOT / "hub/websites/webarena_gitlab_mock/src/data/projects.json"
_PROJECTS = {p["id"]: p for p in json.loads(SEED.read_text())}


def star_fixture(project_ids, stamp):
    stars = [{"project_id": pid, "user_id": 2330, "created_at": stamp}
             for pid in project_ids]
    edits = {}
    for pid in project_ids:
        rec = dict(_PROJECTS[pid])
        rec["star_count"] = rec["star_count"] + 1
        edits[str(pid)] = rec
    return (json.dumps(stars, indent=2, ensure_ascii=True),
            json.dumps(edits, indent=2, ensure_ascii=True))


TITLE_FACT = ("issue_created_with_exact_title", "issue is not None")
TITLE_DETAIL = ('issue_created_with_exact_title',
                '"newIssues rows on project %d == %d; rows with the exact title == %d"'
                ' % (PROJECT_ID, len(in_project), len(titled))')
HANDLE_FACT = ("handle_recorded_in_description",
               "issue is not None and HANDLE_NEEDLE in description")
HANDLE_DETAIL = ("handle_recorded_in_description",
                 '"looked for %r in %r" % (HANDLE_NEEDLE, description)')
ASSIGN_FACT = ("assigned_to_top_committer",
               "issue is not None and assignees == [USER_ID]")
ASSIGN_DETAIL = ("assigned_to_top_committer",
                 '"assignee_ids == %r, wanted [%d]" % (assignees, USER_ID)')


def replay(task_id, steps):
    body = ['"""Golden replay draft for %s.' % task_id,
            "",
            "Click-only: after the initial goto of start_path every navigation is a",
            "click on a rendered link or button. No constructed URLs.",
            '"""',
            "",
            "",
            "def run(page, base_url):",
            "    page.goto(base_url + \"/\")",
            "    page.wait_for_load_state(\"networkidle\")",
            ""]
    body += ["    " + line for line in steps]
    body += ["", "    page.wait_for_timeout(500)", ""]
    return "\n".join(body)


def nav_to_project(project_name, full_path):
    return [
        '# --- locate the project from the landing page (navbar search) -------',
        'page.fill("#search", %r)' % project_name,
        'page.press("#search", "Enter")',
        'page.wait_for_load_state("networkidle")',
        'page.click("a[href=\'/%s\']")' % full_path,
        'page.wait_for_load_state("networkidle")',
    ]


def nav_to_contributors():
    return [
        '# --- Repository -> Contributors (sub-items only show inside the section)',
        'page.click("a.shortcuts-tree")',
        'page.wait_for_load_state("networkidle")',
        'page.click("a:has-text(\'Contributors\')")',
        'page.wait_for_load_state("networkidle")',
        '# the first contributor card is the top committer (Contributors.jsx:127)',
    ]


def nav_to_user(display_name, handle):
    return [
        '# --- join the display name to an account through the Users scope ----',
        'page.fill("#search", %r)' % display_name,
        'page.press("#search", "Enter")',
        'page.wait_for_load_state("networkidle")',
        'page.click("a:has-text(\'Users\')")',
        'page.wait_for_load_state("networkidle")',
        'page.click("a[href=\'/%s\']")' % handle,
        'page.wait_for_load_state("networkidle")',
    ]


def nav_new_issue(project_name, full_path):
    return [
        '# --- back to the project, Issues -> New issue -----------------------',
        'page.fill("#search", %r)' % project_name,
        'page.press("#search", "Enter")',
        'page.wait_for_load_state("networkidle")',
        'page.click("a[href=\'/%s\']")' % full_path,
        'page.wait_for_load_state("networkidle")',
        'page.click("a.shortcuts-issues")',
        'page.wait_for_load_state("networkidle")',
        'page.click("[data-qa-selector=\'new_issue_link\'], a:has-text(\'New issue\')")',
        'page.wait_for_load_state("networkidle")',
    ]


def fill_issue(title, description, handle, due=None):
    steps = [
        'page.fill("#issue_title", %r)' % title,
        'page.fill("#issue_description", %r)' % description,
        '# assignee picker offers every user (Controls.jsx:47-62)',
        'page.click(".js-assignee-search")',
        'page.fill("input[placeholder=\'Search users\']", %r)' % handle,
        'page.click(".dropdown-menu-user li:has-text(\'@%s\')")' % handle,
    ]
    if due:
        steps.append('page.fill("#issuable-due-date", %r)' % due)
    steps += [
        'page.click("[data-qa-selector=\'issuable_create_button\']")',
        'page.wait_for_load_state("networkidle")',
    ]
    return steps


SPECS = []


def base_spec(**kw):
    spec = {
        "style": "terse",
        "difficulty": "hard",
        "skills": ["R4", "R7", "A12"],
        "hard_criteria": ["derived_target", "cross_section"],
        "inspiration_ids": ["webarena-308", "webarena-658"],
    }
    spec.update(kw)
    return spec


# --- 001  mathjax/MathJax -> Davide P. Cervone 2101 (next 121) -> @dpvc ------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_001",
    instruction=(
        "MathJax's build documentation is stale. Open an issue on mathjax/MathJax "
        "titled \"Refresh the build documentation\", @-mention the GitLab handle of "
        "the repository's leading committer on master in the description, and assign "
        "the issue to that person."),
    project_id=65,
    title="Refresh the build documentation",
    handle_needle="@dpvc",
    user_id=512,
    weights={"issue_created_with_exact_title": 0.3,
             "handle_recorded_in_description": 0.35,
             "assigned_to_top_committer": 0.35},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("mathjax/MathJax's Contributors page for master ranks Davide P. Cervone "
            "first with 2101 commits against 121 for the runner-up (margin 1980). "
            "That display name resolves through /search?scope=users to the single "
            "account @dpvc, user id 512."),
    success_criteria=[
        "newIssues holds exactly one record for project 65 titled 'Refresh the build documentation'.",
        "That record's description contains the handle '@dpvc'.",
        "That record's assignee_ids is exactly [512].",
    ],
    skill_chain=("rank the Contributors page for master -> take the top committer's "
                 "display name -> join it to a GitLab account through the Users "
                 "search scope -> create an issue whose description carries that "
                 "handle and whose assignee is that account"),
    analogues=[A_USERNAME, A_CREATE],
    notes=[
        "Contributors.jsx:127 sorts authors by commits descending, so the first card is the answer.",
        "Margin 2101 vs 121; no tie. The name 'Davide P. Cervone' matches exactly one users.json row.",
        "Contributor emails never join to users.json (0 of 3460 rows), so the display name is the only key.",
        "No initial_setup: pristine hub state already has newIssues empty, so the initial lane scores 0.0.",
    ],
    replay=replay("top_contributor_join_issue_001",
                  nav_to_project("MathJax", "mathjax/MathJax")
                  + nav_to_contributors()
                  + ['# top card reads "Davide P. Cervone" / "2101 commits (dpvc@union.edu)"']
                  + nav_to_user("Davide P. Cervone", "dpvc")
                  + nav_new_issue("MathJax", "mathjax/MathJax")
                  + fill_issue("Refresh the build documentation",
                               "@dpvc is the leading committer on master - please refresh the build documentation.",
                               "dpvc")),
))

# --- 002  OpenAPITools/openapi-generator -> William Cheng -> @wing328 --------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_002",
    instruction=(
        "openapi-generator still has nobody owning its release checklist. File an "
        "issue on that project titled \"Release checklist owner: @handle\", with "
        "@handle replaced by the GitLab username of the project's top committer on "
        "master, and assign the issue to them."),
    project_id=58,
    title="Release checklist owner: @wing328",
    handle_needle="@wing328",
    user_id=393,
    weights={"issue_created_in_project": 0.2,
             "title_carries_top_committer_handle": 0.45,
             "assigned_to_top_committer": 0.35},
    facts=[("issue_created_in_project", "len(in_project) == 1"),
           ("title_carries_top_committer_handle", "issue is not None"),
           ASSIGN_FACT],
    details=[("issue_created_in_project",
              '"newIssues rows on project %d == %d" % (PROJECT_ID, len(in_project))'),
             ("title_carries_top_committer_handle",
              '"rows titled %r == %d" % (TITLE, len(titled))'),
             ASSIGN_DETAIL],
    rubric=("openapi-generator's Contributors page for master ranks William Cheng "
            "first with 2059 commits against 182 (margin 1877). The name resolves to "
            "the single account @wing328, user id 393, so the only correct title is "
            "'Release checklist owner: @wing328'."),
    success_criteria=[
        "Exactly one record in newIssues has project_id 58.",
        "That record's title is exactly 'Release checklist owner: @wing328'.",
        "That record's assignee_ids is exactly [393].",
    ],
    skill_chain=("rank the Contributors page -> top committer's display name -> join "
                 "to an account via the Users search scope -> the joined handle is "
                 "the issue title, and the same account is the assignee"),
    analogues=[A_USERNAME, A_CREATE2],
    notes=[
        "The derived value lands in the title rather than the body, so a wrong join scores 0.2 at most.",
        "Margin 2059 vs 182. 'William Cheng' matches exactly one users.json row (id 393).",
        "openapi-generator carries 3476 open issues, so the New issue button is on the populated list header (IssuablesList.jsx:190).",
    ],
    replay=replay("top_contributor_join_issue_002",
                  nav_to_project("openapi-generator", "OpenAPITools/openapi-generator")
                  + nav_to_contributors()
                  + ['# top card reads "William Cheng" / "2059 commits (wing328hk@gmail.com)"']
                  + nav_to_user("William Cheng", "wing328")
                  + nav_new_issue("openapi-generator", "OpenAPITools/openapi-generator")
                  + fill_issue("Release checklist owner: @wing328",
                               "Assigning the release checklist to the project's top committer.",
                               "wing328")),
))

# --- 003  OptimalBits/bull (default branch develop) -> @manast ---------------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_003",
    instruction=(
        "Jobs are stalling in OptimalBits/bull. Open an issue there titled \"Stalled "
        "job triage\", name the repository's top committer by their GitLab username "
        "in the description, assign the issue to them, and set its due date to "
        "2030-03-31."),
    project_id=75,
    title="Stalled job triage",
    handle_needle="manast",
    user_id=84,
    due_date="2030-03-31",
    weights={"issue_created_with_exact_title": 0.2,
             "handle_recorded_in_description": 0.3,
             "assigned_to_top_committer": 0.3,
             "due_date_set_to_2030_03_31": 0.2},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT,
           ("due_date_set_to_2030_03_31",
            "issue is not None and _text(issue.get(\"due_date\")) == DUE_DATE")],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL,
             ("due_date_set_to_2030_03_31",
              '"due_date == %r, wanted %r" % (_text(issue.get("due_date")) if issue is not None else None, DUE_DATE)')],
    rubric=("bull's default branch is develop, and its Contributors page for develop "
            "ranks Manuel Astudillo first with 965 commits against 60 (margin 905). "
            "The name resolves to @manast, user id 84. The due date is stated in the "
            "instruction and is stored by DateField as a plain YYYY-MM-DD string."),
    success_criteria=[
        "newIssues holds exactly one record for project 75 titled 'Stalled job triage'.",
        "That record's description contains 'manast'.",
        "That record's assignee_ids is exactly [84].",
        "That record's due_date is exactly '2030-03-31'.",
    ],
    skill_chain=("rank the Contributors page for the default branch develop -> top "
                 "committer -> join the name to @manast -> create the issue carrying "
                 "that handle, assigned to that account, with the stated due date"),
    analogues=[A_EMAIL1, A_CREATE],
    notes=[
        "bull's default_branch is 'develop', so the sidebar Contributors link lands on /-/graphs/develop - the only ref contributors.json carries for this project.",
        "Margin 965 vs 60 (semantic-release-bot). 'Manuel Astudillo' matches exactly one users.json row.",
        "The handle check accepts the bare username because the instruction asks for the username, not an @-mention.",
    ],
    replay=replay("top_contributor_join_issue_003",
                  nav_to_project("bull", "OptimalBits/bull")
                  + nav_to_contributors()
                  + ['# top card reads "Manuel Astudillo" / "965 commits (manuel@optimalbits.com)"']
                  + nav_to_user("Manuel Astudillo", "manast")
                  + nav_new_issue("bull", "OptimalBits/bull")
                  + fill_issue("Stalled job triage",
                               "Top committer on develop is manast - please take a look at the stalled jobs.",
                               "manast", due="2030-03-31")),
))

# --- 004  DynamoRIO/dynamorio -> Derek Bruening -> @derekbruening (id 2188) --
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_004",
    skills=["R4", "R7", "R9", "A12"],
    instruction=(
        "Open an issue on DynamoRIO/dynamorio titled \"Maintainer sign-off needed\". "
        "In the description record both the GitLab username and the numeric User ID "
        "shown on the profile of the repository's top committer on master, then "
        "assign the issue to them."),
    project_id=160,
    title="Maintainer sign-off needed",
    handle_needle="derekbruening",
    user_id=2188,
    detail_numbers=[2188],
    weights={"issue_created_with_exact_title": 0.2,
             "handle_recorded_in_description": 0.25,
             "profile_user_id_recorded": 0.25,
             "assigned_to_top_committer": 0.3},
    facts=[TITLE_FACT, HANDLE_FACT,
           ("profile_user_id_recorded",
            "issue is not None and _details_present(description)"),
           ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL,
             ("profile_user_id_recorded",
              '"looked for tokens %r and standalone numbers %r in %r" % (DETAIL_TOKENS, DETAIL_NUMBERS, description)'),
             ASSIGN_DETAIL],
    rubric=("dynamorio's Contributors page for master ranks Derek Bruening first with "
            "3470 commits against 426 (margin 3044). The name joins to @derekbruening, "
            "and UserProfile.jsx:362 is the only surface that renders 'User ID: 2188', "
            "so the profile hop cannot be skipped."),
    success_criteria=[
        "newIssues holds exactly one record for project 160 titled 'Maintainer sign-off needed'.",
        "That record's description contains 'derekbruening'.",
        "That record's description contains the standalone number 2188.",
        "That record's assignee_ids is exactly [2188].",
    ],
    skill_chain=("rank Contributors -> top committer's name -> join to an account -> "
                 "read the User ID off that profile -> create the issue whose "
                 "description carries handle and User ID, assigned to that account"),
    analogues=[A_FULLNAME, A_CREATE],
    notes=[
        "Margin 3470 vs 426 (zhaoqin). 'Derek Bruening' matches exactly one users.json row.",
        "User ID is rendered only on /:username (UserProfile.jsx:362) - the search result card shows name and @handle only, so this component forces the third page.",
        "2188 is also the assignee id, but the description check is a standalone-number regex, which cannot be satisfied by the assignee field.",
    ],
    replay=replay("top_contributor_join_issue_004",
                  nav_to_project("dynamorio", "DynamoRIO/dynamorio")
                  + nav_to_contributors()
                  + ['# top card reads "Derek Bruening" / "3470 commits (bruening@google.com)"']
                  + nav_to_user("Derek Bruening", "derekbruening")
                  + ['# profile header renders "User ID: 2188"']
                  + nav_new_issue("dynamorio", "DynamoRIO/dynamorio")
                  + fill_issue("Maintainer sign-off needed",
                               "Top committer on master: @derekbruening (User ID: 2188).",
                               "derekbruening")),
))

# --- 005  cppmap/cppmap.docs -> Ryo Suzuki -> @Reputeless -------------------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_005",
    instruction=(
        "cppmap/cppmap.docs has no contribution guide. Open an issue there titled "
        "\"Add a CONTRIBUTING guide\", @-mention the GitLab handle of its top "
        "committer on master in the description, and assign the issue to that "
        "person."),
    project_id=70,
    title="Add a CONTRIBUTING guide",
    handle_needle="@reputeless",
    user_id=595,
    weights={"issue_created_with_exact_title": 0.3,
             "handle_recorded_in_description": 0.35,
             "assigned_to_top_committer": 0.35},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("cppmap.docs' Contributors page for master ranks Ryo Suzuki first with 484 "
            "commits against 19 (margin 465). The second card is literally named "
            "'Reputeless', which is also the top committer's GitLab username - the "
            "join has to go through the name, not the card ordering."),
    success_criteria=[
        "newIssues holds exactly one record for project 70 titled 'Add a CONTRIBUTING guide'.",
        "That record's description contains the handle '@Reputeless' (case-insensitive).",
        "That record's assignee_ids is exactly [595].",
    ],
    skill_chain=("rank Contributors -> 'Ryo Suzuki' -> join through the Users search "
                 "scope to @Reputeless -> create the issue carrying that handle and "
                 "assign it to that account"),
    analogues=[A_USERNAME, A_CREATE2],
    notes=[
        "Built-in distractor: the runner-up contributor row (19 commits) is named 'Reputeless', which is the WINNER's username. An agent that reads the wrong card still lands on the right handle only by accident; an agent that assigns the runner-up row's identity has nowhere to go, because no users.json row is named 'Reputeless'.",
        "Margin 484 vs 19. 'Ryo Suzuki' matches exactly one users.json row (id 595).",
        "Handle comparison is lower-cased, so '@Reputeless' and '@reputeless' both pay.",
    ],
    replay=replay("top_contributor_join_issue_005",
                  nav_to_project("cppmap.docs", "cppmap/cppmap.docs")
                  + nav_to_contributors()
                  + ['# top card reads "Ryo Suzuki" / "484 commits (reputeless+github@gmail.com)"',
                     '# second card is a different email row named "Reputeless" (19 commits)']
                  + nav_to_user("Ryo Suzuki", "Reputeless")
                  + nav_new_issue("cppmap.docs", "cppmap/cppmap.docs")
                  + fill_issue("Add a CONTRIBUTING guide",
                               "@Reputeless is the top committer on master - could you add a contribution guide?",
                               "Reputeless")),
))

# --- 006  koush/AndroidAsync -> Koushik Dutta -> @koush (explicit) ----------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_006",
    style="explicit",
    skills=["R4", "R7", "R9", "A12"],
    instruction=(
        "We need a maintainer contact recorded against koush/AndroidAsync. Starting "
        "from the GitLab landing page, find that project and open its Contributors "
        "page (the Repository section of the project sidebar, then Contributors), "
        "and read off the contributor with the highest commit count on master. "
        "Search GitLab with the Users scope for that person's display name, open "
        "their profile, and note both their @handle and the location shown in the "
        "profile header. Then create a new issue on koush/AndroidAsync with the "
        "title \"Maintainer contact\" whose description contains that @handle and "
        "that location string, and set the issue's assignee to the same account. "
        "Leave the project's existing issues, labels and members as they are."),
    project_id=145,
    title="Maintainer contact",
    handle_needle="@koush",
    user_id=1912,
    detail_tokens=["seattle, wa"],
    weights={"issue_created_with_exact_title": 0.2,
             "handle_recorded_in_description": 0.25,
             "profile_location_recorded": 0.25,
             "assigned_to_top_committer": 0.3},
    facts=[TITLE_FACT, HANDLE_FACT,
           ("profile_location_recorded",
            "issue is not None and _details_present(description)"),
           ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL,
             ("profile_location_recorded",
              '"looked for tokens %r in %r" % (DETAIL_TOKENS, description)'),
             ASSIGN_DETAIL],
    rubric=("AndroidAsync's Contributors page for master ranks Koushik Dutta first "
            "with 809 commits against 44 for the next row (margin 765; the runner-up "
            "row is a second email for the same person, so the display name is "
            "unambiguous either way). The name joins to @koush, user id 1912, whose "
            "profile header renders the location 'Seattle, WA'."),
    success_criteria=[
        "newIssues holds exactly one record for project 145 titled 'Maintainer contact'.",
        "That record's description contains '@koush'.",
        "That record's description contains 'Seattle, WA' (case-insensitive).",
        "That record's assignee_ids is exactly [1912].",
    ],
    skill_chain=("rank Contributors -> top committer -> join the name to an account "
                 "-> read the location off that profile -> create an issue whose "
                 "description carries handle and location, assigned to that account"),
    analogues=[A_FULLNAME, A_CREATE],
    notes=[
        "Explicit style: the click path is spelled out because the profile-header location is easy to confuse with the organization line, and the census records that sidebar sub-items are invisible until the section's own page is open.",
        "The handle equals the namespace here, which would make the join guessable - the location component is what forces the real profile hop, since /search?scope=users renders only name and @handle.",
        "Margin 809 vs 44; both top rows are 'Koushik Dutta' (GitLab groups contributors by email, Contributors.jsx:20-22), so 'who' is unambiguous.",
    ],
    replay=replay("top_contributor_join_issue_006",
                  nav_to_project("AndroidAsync", "koush/AndroidAsync")
                  + nav_to_contributors()
                  + ['# top card reads "Koushik Dutta" / "809 commits (koushd@gmail.com)"']
                  + nav_to_user("Koushik Dutta", "koush")
                  + ['# profile header renders the location "Seattle, WA"']
                  + nav_new_issue("AndroidAsync", "koush/AndroidAsync")
                  + fill_issue("Maintainer contact",
                               "Maintainer is @koush, based in Seattle, WA.",
                               "koush")),
))

# --- 007  sweet-js/sweet-core -> Tim Disney -> @disnet, invite then file -----
_MEMBERS_007 = json.dumps([{
    "id": 206,
    "source_type": "project",
    "source_id": 124,
    "user_id": 2330,
    "access_level": 40,
    "access_label": "Maintainer",
    "created_at": "2023-03-28 09:11:02.117430",
    "expires_at": None,
    "created_by_id": 1395,
}], indent=2, ensure_ascii=True)

SPECS.append(base_spec(
    task_id="top_contributor_join_issue_007",
    skills=["R4", "R7", "A3", "A12"],
    hard_criteria=["derived_target", "multi_mutation", "cross_section"],
    instruction=(
        "sweet-js/sweet-core is mine to maintain now, and its top committer on "
        "master holds no role there. Invite that person as a Reporter, then open an "
        "issue titled \"Restore release automation\" mentioning their GitLab handle "
        "in the description and assigned to them."),
    project_id=124,
    title="Restore release automation",
    handle_needle="disnet",
    user_id=1409,
    invite_project=124,
    invite_user=1409,
    invite_level=20,
    weights={"top_committer_invited_as_reporter": 0.3,
             "issue_created_with_exact_title": 0.15,
             "handle_recorded_in_description": 0.2,
             "assigned_to_top_committer": 0.35},
    facts=[("top_committer_invited_as_reporter", "_invited(state)"),
           TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[("top_committer_invited_as_reporter",
              '"newMembers == %r" % (_list(_dict(state).get("newMembers")),)'),
             TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("sweet-core's Contributors page for master ranks Tim Disney first with "
            "1771 commits against 96 (margin 1675). The name joins to @disnet, user "
            "id 1409, who holds no member row on the project. The rubric wants a "
            "project-124 newMembers row for user 1409 at access_level 20 (Reporter) "
            "plus the issue, assigned to the same account."),
    success_criteria=[
        "newMembers contains a project row for source_id 124, user_id 1409, access_level 20.",
        "newIssues holds exactly one record for project 124 titled 'Restore release automation'.",
        "That record's description contains 'disnet'.",
        "That record's assignee_ids is exactly [1409].",
    ],
    skill_chain=("rank Contributors -> top committer -> join the name to @disnet -> "
                 "grant that account Reporter on the project -> file an issue "
                 "carrying the handle and assigned to the same account"),
    analogues=[A_USERNAME, A_CREATE],
    inspiration_ids=["webarena-308", "webarena-658", "webarena-660"],
    injected=[
        "newMembers: byteblaze (user 2330) as Maintainer (access_level 40, member id 206) on sweet-js/sweet-core (project 124), with nextIds.member advanced to 207. MembersTable.jsx:182 gates the Invite members control on `ownAccess >= 40`, and on the pristine seed byteblaze holds no role on this project, so the invite half of the task would be unreachable without it.",
        "Nothing in the rubric is pre-satisfied: the injected row is byteblaze's own, while every scored fact concerns user 1409 (@disnet) and the created issue, both absent at t=0.",
    ],
    setup=member_setup(
        "top_contributor_join_issue_007",
        ("Grants byteblaze the Maintainer role on sweet-js/sweet-core (project 124) so\n"
         "that the project's Members page renders its Invite members control. The seed\n"
         "gives that project a single Owner (@sweet-js, user 1395) and byteblaze no\n"
         "role at all, which makes `canManage` false and hides the button."),
        _MEMBERS_007, 207),
    notes=[
        "Margin 1771 vs 96 (Nathan Faubion). 'Tim Disney' matches exactly one users.json row (id 1409).",
        "The invite role select offers levels 10..max(ownAccess,10) (MembersTable.jsx:181), so Maintainer-40 exposes Guest through Maintainer, including the Reporter the task wants.",
        "The invite candidate list excludes existing members (MembersTable.jsx:193), and 1409 holds no row on project 124, so @disnet is offered.",
        "Ordering: the assignee picker offers all users regardless of membership (Controls.jsx:47-62), so the invite is a genuine separate mutation and not a prerequisite the form would satisfy for free.",
    ],
    replay=replay("top_contributor_join_issue_007",
                  nav_to_project("sweet-core", "sweet-js/sweet-core")
                  + nav_to_contributors()
                  + ['# top card reads "Tim Disney" / "1771 commits (tim@disnetdev.com)"']
                  + nav_to_user("Tim Disney", "disnet")
                  + nav_to_project("sweet-core", "sweet-js/sweet-core")
                  + ['# --- Project information -> Members, then invite --------------------',
                     'page.click("a.shortcuts-project-information")',
                     'page.wait_for_load_state("networkidle")',
                     'page.click("a:has-text(\'Members\')")',
                     'page.wait_for_load_state("networkidle")',
                     'page.click("button:has-text(\'Invite members\')")',
                     'page.fill("input[placeholder*=\'Search\']", "disnet")',
                     'page.click("li:has-text(\'@disnet\')")',
                     'page.select_option("select", label="Reporter")',
                     'page.click("button:has-text(\'Invite\')")',
                     'page.wait_for_load_state("networkidle")']
                  + ['page.click("a.shortcuts-issues")',
                     'page.wait_for_load_state("networkidle")',
                     'page.click("[data-qa-selector=\'new_issue_link\'], a:has-text(\'New issue\')")',
                     'page.wait_for_load_state("networkidle")']
                  + fill_issue("Restore release automation",
                               "disnet is the top committer on master - inviting them to restore the release automation.",
                               "disnet")),
))

# --- 008  starred-list leader -> PyAV-Org/PyAV -> Mike Boers -> @mikeboers ---
_STARS_008, _EDITS_008 = star_fixture([136, 160, 70], "2023-03-28 11:04:19.552108")

SPECS.append(base_spec(
    task_id="top_contributor_join_issue_008",
    skills=["R1", "R4", "R7", "A12"],
    hard_criteria=["derived_target", "cross_section"],
    instruction=(
        "Open an issue on whichever project on my starred list carries the most "
        "stars, titled \"Codec matrix refresh\", with the GitLab handle of that "
        "project's leading committer on its default branch in the description. "
        "Assign the issue to that person."),
    project_id=136,
    title="Codec matrix refresh",
    handle_needle="mikeboers",
    user_id=1696,
    weights={"issue_created_with_exact_title": 0.3,
             "handle_recorded_in_description": 0.35,
             "assigned_to_top_committer": 0.35},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("After the injection byteblaze's starred list holds six projects: "
            "PyAV-Org/PyAV 40, DynamoRIO/dynamorio 31, a11yproject/a11yproject.com "
            "21, byteblaze/empathy-prompts 6, cppmap/cppmap.docs 5 and "
            "byteblaze/accessible-html-content-patterns 1. PyAV wins by 9. Its "
            "Contributors page for main ranks Mike Boers first with 709 commits "
            "against 221, and that name joins to @mikeboers, user id 1696."),
    success_criteria=[
        "newIssues holds exactly one record for project 136 (PyAV-Org/PyAV) titled 'Codec matrix refresh'.",
        "That record's description contains 'mikeboers'.",
        "That record's assignee_ids is exactly [1696].",
    ],
    skill_chain=("superlative over the starred list by star count -> that project's "
                 "Contributors page -> top committer's name -> join to @mikeboers -> "
                 "issue on that project carrying the handle and assigned to them"),
    analogues=[A_USERNAME, A_CREATE2],
    inspiration_ids=["webarena-308", "webarena-659"],
    injected=[
        "newStars: byteblaze (user 2330) starring PyAV-Org/PyAV (136), DynamoRIO/dynamorio (160) and cppmap/cppmap.docs (70). The seed gives byteblaze only three starred projects, two of which are his own, so 'the most-starred project on my starred list' is otherwise a thin and uninteresting choice.",
        "projectEdits for the same three projects, each with star_count incremented by one. ProjectOverview.toggleStar bumps star_count as well as appending the star row, and ProjectRow/sortProjects read star_count - newStars alone would leave the rendered counts one short of the truth.",
        "Nothing in the rubric is pre-satisfied: newIssues is empty at t=0 and no issue or assignment is injected.",
    ],
    setup=star_setup(
        "top_contributor_join_issue_008",
        ("Stars three public projects for byteblaze so that 'the most-starred project on\n"
         "my starred list' has a real spread to compute over: PyAV-Org/PyAV lands at 40\n"
         "stars, DynamoRIO/dynamorio at 31 and cppmap/cppmap.docs at 5, against the\n"
         "seeded a11yproject.com 21, empathy-prompts 6 and accessible-html-content-\n"
         "patterns 1. The winning margin is 9."),
        _STARS_008, _EDITS_008, [136, 160, 70]),
    notes=[
        "Margin at the top of the starred list is 9 (40 vs 31); the winner is not the alphabetically or chronologically first row, so it must actually be computed.",
        "PyAV's own contributor margin is 709 vs 221 (Jeremy Laine). 'Mike Boers' matches exactly one users.json row (id 1696).",
        "The handle @mikeboers is not derivable from the namespace 'PyAV-Org', so the join cannot be short-circuited.",
        "The starred tab is reachable from '/' through the Starred projects tab in the dashboard tab strip; all six rows fit one 20-row page and each row renders its star count.",
    ],
    replay=replay("top_contributor_join_issue_008",
                  ['# --- starred list from the dashboard tab strip ----------------------',
                   'page.click("a:has-text(\'Starred projects\')")',
                   'page.wait_for_load_state("networkidle")',
                   '# rows: PyAV 40, dynamorio 31, a11yproject.com 21, empathy-prompts 6, cppmap.docs 5, accessible-html-content-patterns 1',
                   'page.click("a[href=\'/PyAV-Org/PyAV\']")',
                   'page.wait_for_load_state("networkidle")']
                  + nav_to_contributors()
                  + ['# top card reads "Mike Boers" / "709 commits (github@mikeboers.com)"']
                  + nav_to_user("Mike Boers", "mikeboers")
                  + nav_new_issue("PyAV", "PyAV-Org/PyAV")
                  + fill_issue("Codec matrix refresh",
                               "Leading committer on main is mikeboers - please refresh the codec matrix.",
                               "mikeboers")),
))

# --- 009  starred-list leader -> BoltsFramework/Bolts-ObjC -> @nlutsenko -----
_STARS_009, _EDITS_009 = star_fixture([104, 112, 130], "2023-03-28 15:47:52.910044")

SPECS.append(base_spec(
    task_id="top_contributor_join_issue_009",
    skills=["R1", "R4", "R7", "A12"],
    hard_criteria=["derived_target", "cross_section"],
    instruction=(
        "The most-starred project on my starred list needs a deprecation notice. "
        "Open an issue there titled \"Deprecation notice owner\" whose description "
        "carries the GitLab handle of its leading committer on the default branch, "
        "and assign the issue to them."),
    project_id=104,
    title="Deprecation notice owner",
    handle_needle="nlutsenko",
    user_id=918,
    weights={"issue_created_with_exact_title": 0.3,
             "handle_recorded_in_description": 0.35,
             "assigned_to_top_committer": 0.35},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("After the injection byteblaze's starred list holds six projects: "
            "BoltsFramework/Bolts-ObjC 33, a11yproject/a11yproject.com 21, "
            "stripe-contrib/pagerbot 18, pwr-Solaar/Solaar 12, "
            "byteblaze/empathy-prompts 6 and "
            "byteblaze/accessible-html-content-patterns 1. Bolts-ObjC wins by 12. "
            "Its Contributors page for main ranks Nikita Lutsenko first with 112 "
            "commits, and that name joins to @nlutsenko, user id 918."),
    success_criteria=[
        "newIssues holds exactly one record for project 104 (BoltsFramework/Bolts-ObjC) titled 'Deprecation notice owner'.",
        "That record's description contains 'nlutsenko'.",
        "That record's assignee_ids is exactly [918].",
    ],
    skill_chain=("superlative over the starred list by star count -> Contributors of "
                 "the winner -> top committer's name -> join to @nlutsenko -> issue "
                 "on that project carrying the handle and assigned to them"),
    analogues=[A_USERNAME, A_CREATE],
    inspiration_ids=["webarena-308", "webarena-658"],
    injected=[
        "newStars: byteblaze (user 2330) starring BoltsFramework/Bolts-ObjC (104), stripe-contrib/pagerbot (112) and pwr-Solaar/Solaar (130). This is the same chain as task 008 with a different injected precondition, so the correct project, handle, assignee and title all differ.",
        "projectEdits for the same three projects with star_count incremented by one, matching what ProjectOverview.toggleStar would have written.",
        "Nothing in the rubric is pre-satisfied: no issue, no assignment and no membership is injected.",
    ],
    setup=star_setup(
        "top_contributor_join_issue_009",
        ("Stars three public projects for byteblaze so that the starred list has a real\n"
         "ranking to compute over: BoltsFramework/Bolts-ObjC lands at 33 stars,\n"
         "stripe-contrib/pagerbot at 18 and pwr-Solaar/Solaar at 12, against the seeded\n"
         "a11yproject.com 21, empathy-prompts 6 and accessible-html-content-patterns 1.\n"
         "The winning margin is 12."),
        _STARS_009, _EDITS_009, [104, 112, 130]),
    notes=[
        "Same skill chain as 008 with a different injected precondition, which is the batch-5 preferred form of instance variation: the reward constants, the correct project and the correct account all change.",
        "Starred-list margin 33 vs 21. Bolts-ObjC's top two contributor rows are both 'Nikita Lutsenko' (112 and 78, two emails), so the display name is unambiguous; the next distinct name is David Poll at 30.",
        "'Nikita Lutsenko' matches exactly one users.json row (id 918), and @nlutsenko is not derivable from the namespace 'BoltsFramework'.",
    ],
    replay=replay("top_contributor_join_issue_009",
                  ['# --- starred list from the dashboard tab strip ----------------------',
                   'page.click("a:has-text(\'Starred projects\')")',
                   'page.wait_for_load_state("networkidle")',
                   '# rows: Bolts-ObjC 33, a11yproject.com 21, pagerbot 18, Solaar 12, empathy-prompts 6, accessible-html-content-patterns 1',
                   'page.click("a[href=\'/BoltsFramework/Bolts-ObjC\']")',
                   'page.wait_for_load_state("networkidle")']
                  + nav_to_contributors()
                  + ['# top card reads "Nikita Lutsenko" / "112 commits (...)"']
                  + nav_to_user("Nikita Lutsenko", "nlutsenko")
                  + nav_new_issue("Bolts-ObjC", "BoltsFramework/Bolts-ObjC")
                  + fill_issue("Deprecation notice owner",
                               "Handing the deprecation notice to nlutsenko, the leading committer on main.",
                               "nlutsenko")),
))

# --- 010  checkstyle/checkstyle, contributor named outright (medium) --------
SPECS.append(base_spec(
    task_id="top_contributor_join_issue_010",
    style="explicit",
    difficulty="medium",
    skills=["R7", "A12"],
    instruction=(
        "Roman Ivanov is our contact on the checkstyle project, but I only have his "
        "display name, not his GitLab account. Find the account that belongs to that "
        "name using the global search box with the Users scope, then create an issue "
        "on checkstyle/checkstyle titled \"Static analysis rollout\". Its description "
        "must mention his GitLab @handle, and the issue must be assigned to his "
        "account. Start from the GitLab landing page and leave the project's existing "
        "issues and members alone."),
    project_id=144,
    title="Static analysis rollout",
    handle_needle="@romani",
    user_id=1905,
    weights={"issue_created_with_exact_title": 0.3,
             "handle_recorded_in_description": 0.35,
             "assigned_to_top_committer": 0.35},
    facts=[TITLE_FACT, HANDLE_FACT, ASSIGN_FACT],
    details=[TITLE_DETAIL, HANDLE_DETAIL, ASSIGN_DETAIL],
    rubric=("'Roman Ivanov' matches exactly one users.json row, @romani, user id "
            "1905. Search.jsx:82 matches the Users scope on name or username, so the "
            "display name is a sufficient key; the handle is not derivable from the "
            "namespace 'checkstyle'."),
    success_criteria=[
        "newIssues holds exactly one record for project 144 titled 'Static analysis rollout'.",
        "That record's description contains '@romani'.",
        "That record's assignee_ids is exactly [1905].",
    ],
    skill_chain=("join a display name to a GitLab account through the Users search "
                 "scope -> create an issue whose description carries that handle and "
                 "whose assignee is that account"),
    analogues=[A_USERNAME, A_ASSIGN],
    inspiration_ids=["webarena-308", "webarena-446"],
    notes=[
        "Deliberately medium: two skills, one retrieval and one action. The contributor is named outright, so the ordinal hop (R4) is absent and the label is not padded up.",
        "'Roman Ivanov' is also checkstyle's real top committer (1436 vs 682), so the entity is consistent with the rest of the lane, but the task never asks the agent to rank anything.",
        "Explicit style because the Users scope has to be named - the default search scope is projects (Search.jsx:51) and a bare name search lands on an empty project list.",
    ],
    replay=replay("top_contributor_join_issue_010",
                  nav_to_user("Roman Ivanov", "romani")
                  + nav_new_issue("checkstyle", "checkstyle/checkstyle")
                  + fill_issue("Static analysis rollout",
                               "Rolling out static analysis with @romani.",
                               "romani")),
))


GENERATION_MD = """# Batch 5, lane 0 - gitlab / `top_contributor_join_issue`

Ten bundles under `output/tasks/gitlab/top_contributor_join_issue_001..010`.

Assigned chain: **R4 -> R7 -> A12** - rank the Contributors page, take the top
committer's display name, join that name to a GitLab account, then create an
issue in the project that carries the joined handle and is assigned to that
account. Every task exercises at least one of those three, and the lane as a
whole exercises all three (R4 in 001-009, R7 in all ten, A12 in all ten).

## The composition test

*Would a real person ever have this as one errand?* Yes: "before I lean on this
repo, work out who actually maintains it, then file the request against them" is
one continuous piece of maintainer work. The retrieval and the action share a
subject - the same repository and the same person - which is what separates it
from a stapled chain.

## Task table

| id | project | derived answer | style | difficulty | skills | setup |
|---|---|---|---|---|---|---|
| 001 | mathjax/MathJax | Davide P. Cervone -> `@dpvc` (512) | terse | hard | R4,R7,A12 | - |
| 002 | OpenAPITools/openapi-generator | William Cheng -> `@wing328` (393) | terse | hard | R4,R7,A12 | - |
| 003 | OptimalBits/bull (`develop`) | Manuel Astudillo -> `@manast` (84) | terse | hard | R4,R7,A12 | - |
| 004 | DynamoRIO/dynamorio | Derek Bruening -> `@derekbruening`, User ID 2188 | terse | hard | R4,R7,R9,A12 | - |
| 005 | cppmap/cppmap.docs | Ryo Suzuki -> `@Reputeless` (595) | terse | hard | R4,R7,A12 | - |
| 006 | koush/AndroidAsync | Koushik Dutta -> `@koush`, `Seattle, WA` | explicit | hard | R4,R7,R9,A12 | - |
| 007 | sweet-js/sweet-core | Tim Disney -> `@disnet` (1409), invited Reporter | terse | hard | R4,R7,A3,A12 | `newMembers` |
| 008 | starred leader -> PyAV-Org/PyAV | Mike Boers -> `@mikeboers` (1696) | terse | hard | R1,R4,R7,A12 | `newStars` + `projectEdits` |
| 009 | starred leader -> BoltsFramework/Bolts-ObjC | Nikita Lutsenko -> `@nlutsenko` (918) | terse | hard | R1,R4,R7,A12 | `newStars` + `projectEdits` |
| 010 | checkstyle/checkstyle | Roman Ivanov -> `@romani` (1905) | explicit | medium | R7,A12 | - |

Splits: **8 terse / 2 explicit**, **10/10 at `start_path: "/"`**, **10/10
`retrieval_writeback`**, difficulty **9 hard / 1 medium** (derived, not quota'd -
010 is honestly two skills and is labelled medium rather than padded).

## Tie margins checked against the seed

Every superlative was recomputed from `src/data/by-project/<id>.json`
(`contributors`) and `src/data/projects.json`, not from the census table.

| superlative | winner | margin | note |
|---|---|---|---|
| top committer, mathjax/MathJax `master` | Davide P. Cervone 2101 | 1980 vs 121 | |
| top committer, openapi-generator `master` | William Cheng 2059 | 1877 vs 182 | |
| top committer, bull `develop` | Manuel Astudillo 965 | 905 vs 60 | `develop` is the default branch and the only ref with contributor data |
| top committer, dynamorio `master` | Derek Bruening 3470 | 3044 vs 426 | |
| top committer, cppmap.docs `master` | Ryo Suzuki 484 | 465 vs 19 | runner-up row is named `Reputeless`, the winner's own username |
| top committer, AndroidAsync `master` | Koushik Dutta 809 | 765 vs the same person's second email row; 799 vs the next distinct name | |
| top committer, sweet-core `master` | Tim Disney 1771 | 1675 vs 96 | |
| top committer, PyAV `main` | Mike Boers 709 | 488 vs 221 | |
| top committer, Bolts-ObjC `main` | Nikita Lutsenko 112 | 34 vs the same person's second row; 82 vs the next distinct name | |
| top committer, checkstyle `master` | Roman Ivanov 1436 | 754 vs 682 | named outright in 010, so the margin is informational |
| starred list by stars, task 008 | PyAV-Org/PyAV 40 | 9 vs dynamorio 31 | post-injection |
| starred list by stars, task 009 | BoltsFramework/Bolts-ObjC 33 | 12 vs a11yproject.com 21 | post-injection |

Every display name used was checked to match **exactly one** row in
`users.json`; 82 of the 175 projects have a name-joinable top contributor under
that uniqueness test.

## Does the action destroy its own retrieval premise?

No. The action writes `newIssues`, `newMembers` and (in 007) nothing else;
`contributors.json` is a frozen bundled import with no state overlay
(`utils/dataManager.js:656`), and `star_count` is not touched by creating an
issue. So the ranking that selected the target is identical before and after the
mutation, and re-deriving it at any point yields the same answer.

## Mechanism claims verified in source

* `pages/NewIssue.jsx:56-84` - the create handler. `appendTo('issues', {...})`
  with `assignee_ids: assigneeId ? [assigneeId] : []`, `due_date: dueDate || null`
  and `id = allocateId('issue')`. The record lands in `newIssues`
  (`utils/overlayShape.js:43`) and the counter floor is `nextIds.issue` 83821
  (`overlayShape.js:98`).
* `pages/Contributors.jsx:127` - `authors` is sorted by `commits` descending, so
  the first card is the top committer; `:158` renders `"{n} commits ({email})"`.
* `components/issuable/Controls.jsx:47-62` `assignableUsers` - members first,
  then the whole user directory, with a source comment saying restricting to
  members would break the anchored tasks. The assignee picker searches on
  `"{name} {username}"` (`:227`).
* `pages/Search.jsx:82` - the Users scope matches `name` or `username`. There is
  no notes scope, and the default scope is `projects` (`:51`), which is why 010
  names the scope explicitly.
* `pages/UserProfile.jsx:362` - `User ID: {id}` is rendered only on the profile,
  not on the search result card (`Search.jsx:308-322` shows name and `@handle`).
  `:377-390` renders location and organization.
* `components/layout/ProjectSidebar.jsx:24-34` - Repository's own href is
  `/-/tree/:ref` and Contributors is `/-/graphs/:ref`, matching the census's
  probed two-click gesture.
* `pages/IssuablesList.jsx:190` and `:862` - the *New issue* button is
  unconditional and also renders on the empty-state panel, which matters for the
  six target projects whose `open_issues_count` is 0.
* `pages/MembersTable.jsx:181-182` - `roleOptions` is levels 10..max(ownAccess,10)
  and `canManage = ownAccess >= 40`; `:193` excludes existing members from the
  invite candidate list; `components/create/mutations.js:363` `addMembers` writes
  `{id, source_type, source_id, user_id, access_level, access_label, created_at,
  expires_at, created_by_id}`.
* `pages/DashboardProjects.jsx:90` - the starred tab filters `state.stars` by
  `user_id`; `:35` renders `project.star_count` per row; `pages/hooks.js:357`
  sorts on the same field. This is why 008/009 write `projectEdits` as well as
  `newStars`.
* `components/issuable/Controls.jsx:368-383` - `DateField` is `<input type=date>`
  and stores a plain `YYYY-MM-DD` string, which is what 003 grades.

## Precondition injections, and why

* **007 - `newMembers`.** byteblaze holds no role on sweet-js/sweet-core, so
  `canManage` is false and the *Invite members* control does not render at all.
  One Maintainer row for byteblaze makes the A3 half reachable. It injects the
  *rights*, so the task is evidence of granting a role given rights, not of
  acquiring them; recorded in `metadata.injected_preconditions`.
* **008 / 009 - `newStars` + `projectEdits`.** The seed starts byteblaze with
  three starred projects, two of them his own, so a superlative over that list is
  thin. Injecting three more gives a six-row list with a real spread and a margin
  chosen deliberately (9 and 12). Crucially these two tasks are the *same* chain
  with a *different precondition*: the correct project, handle, assignee and
  title all differ, which is the form of variation batch 5 asks for over swapping
  the entity in an otherwise identical rubric.
* None of the three injections touches anything the rubric scores. `newIssues`
  is empty at t=0 in all ten bundles, and 007's injected member row is
  byteblaze's own while the scored row is `@disnet`'s.

## Rejected candidates

* **"How many commits does the top contributor have?"** - dropped. Three surfaces
  disagree (overview 553, Contributors 552, Repository Analytics 40 for
  `byteblaze/dotfiles`), so no exact total is defensible. No task in this lane
  grades a commit count; commit counts are only used to establish *rank*.
* **"How many followers does the top contributor have?"** (official 787) -
  dropped. `follows.json` has five rows and every non-byteblaze profile shows 0.
* **`a11yproject/a11yproject.com`** - dropped as an entity. Eric Bailey appears
  twice on Contributors (422 + 410, two emails) because GitLab groups by email,
  not by user. Fine for "who", but it makes the top card's *identity* look
  ambiguous to an agent, and there was no reason to take the risk with 82 clean
  projects available.
* **"Record the top contributor's email address"** (official 784/315) - dropped.
  Contributor emails are the real commit addresses while `users.json` was
  anonymised to `@fakegithub.com`, so an email writeback would be gradable but
  would teach the agent to read a field that never joins to anything.
* **A conditional (A13) branch on whether the top committer is already a project
  member** - dropped. It is expressible (the seed splits cleanly: `@kahun`,
  `@dehenne`, `@koush`, `@kkroening` are members of their own projects, while
  `@dpvc`, `@wing328`, `@manast`, `@Reputeless`, `@KATT`, `@derekbruening`,
  `@disnet`, `@romani` are not) but the honest branch is "if they are already a
  member, do nothing", and a component that pays for inaction is forbidden in the
  terse set. 007 keeps the useful half - the invite - unconditionally.
* **`capnproto/capnproto`** - not used. Its row margin really is 40, but see the
  correction below.

## Corrections to the census / brief

1. **`capnproto/capnproto`'s margin is not 40.** The brief and
   `output/census/gitlab.md` §4.2 record "Kenton Varda 884 vs 844 (margin only
   40) - prefer the wide-margin rows". The 844 row is *also Kenton Varda* (a
   second email), as is the 502 row. The next **distinct** contributor is Harris
   Hancock at 73, so the margin for "who is the top contributor" is 811, and by
   grouped commits it is 2230 vs 73. The 40 figure is a row margin for a question
   ("which email") the census itself says not to ask. The warning is therefore
   pointed at the wrong hazard: capnproto is a perfectly safe *name* target and
   an unsafe *email* target, exactly like a11yproject.
   The same applies to `koush/AndroidAsync` (809 and 44 are both Koushik Dutta)
   and `BoltsFramework/Bolts-ObjC` (112 and 78 are both Nikita Lutsenko), which
   this lane uses in 006 and 009.
2. **83 name-joinable top contributors is 82** under a strict test. Requiring the
   top contributor's display name to match *exactly one* `users.json` row leaves
   82 of 175 projects. The difference does not matter for a ten-task lane, but
   the stricter number is the one a reward can rely on.
3. **`SEED_NEXT_IDS.issue` is 83821**, not anything derivable from SCHEMA.md.
   Confirmed at `src/utils/overlayShape.js:98`.

## Known limitation, recorded per the taxonomy

The R7 join is graded indirectly: an agent that guesses the handle without ever
opening `/search?scope=users` still scores. Mitigated by choosing handles that
are **not** derivable from the project namespace in eight of the ten tasks
(`dpvc`, `wing328`, `manast`, `Reputeless`, `disnet`, `mikeboers`, `nlutsenko`,
`romani`); 006 uses a namespace-equal handle and closes the gap with a
profile-only location component, and 004 does the same with a profile-only User
ID. This is not fully closed and is not claimed to be.
"""


def main():
    BATCH.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in SPECS:
        if spec.get("invite_project") is not None:
            spec["extra_keys"] = " and, for the invite half, the `newMembers` row"
        rows.append(write_bundle(spec))

    (BATCH / "index.json").write_text(json.dumps({
        "schema_version": 2,
        "tasks": [{"task_id": s["task_id"], "path": "../../%s/task.json" % s["task_id"]}
                  for s in SPECS],
    }, indent=2) + "\n")
    with (BATCH / "nemo_tasks.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    (BATCH / "GENERATION.md").write_text(GENERATION_MD)
    print("wrote %d bundles" % len(rows))


main()
