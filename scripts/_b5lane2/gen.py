# -*- coding: utf-8 -*-
"""Batch-5 lane 2 (gitlab / grant_access_top_repos) bundle generator."""
import json, os, textwrap

ROOT = "/home/ubuntu/CUA-Gym"
SRC = os.path.join(ROOT, "hub/websites/webarena_gitlab_mock/src/data")
OUT = os.path.join(ROOT, "output/tasks/gitlab")
BATCH = os.path.join(OUT, "_batches/grant_access_top_repos")

projects = json.load(open(os.path.join(SRC, "projects.json")))
contribs = json.load(open(os.path.join(SRC, "contributors.json")))

BB = [p for p in projects if p["full_path"].startswith("byteblaze/")]
RECOUNT = {}
for p in BB:
    rec = dict(p)
    rec["commit_count"] = contribs[p["full_path"]][p["default_branch"]]["total"]
    RECOUNT[str(p["id"])] = rec
RECOUNT_JSON = json.dumps(RECOUNT, ensure_ascii=False, indent=1, sort_keys=True)

NAME = {str(p["id"]): p["full_path"] for p in BB}

SEED_MEMBERS = [
    {"id": 187, "source_type": "project", "source_id": 179, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 189, "source_type": "project", "source_id": 181, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 190, "source_type": "project", "source_id": 182, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 191, "source_type": "project", "source_id": 183, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 192, "source_type": "project", "source_id": 184, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 204, "source_type": "project", "source_id": 184, "user_id": 168, "access_level": 30, "expires_at": None},
    {"id": 193, "source_type": "project", "source_id": 185, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 195, "source_type": "project", "source_id": 186, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 196, "source_type": "project", "source_id": 187, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 197, "source_type": "project", "source_id": 188, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 205, "source_type": "project", "source_id": 188, "user_id": 5, "access_level": 10, "expires_at": None},
    {"id": 198, "source_type": "project", "source_id": 189, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 199, "source_type": "project", "source_id": 190, "user_id": 2330, "access_level": 50, "expires_at": None},
    {"id": 202, "source_type": "project", "source_id": 193, "user_id": 2330, "access_level": 50, "expires_at": None},
]
SEED_MEMBERS_JSON = json.dumps(SEED_MEMBERS, indent=1)

BASELINE = {}
for row in SEED_MEMBERS:
    BASELINE.setdefault(str(row["source_id"]), {})[str(row["user_id"])] = row["access_level"]
ALL_BB_IDS = sorted(NAME.keys(), key=int)

# ---------------------------------------------------------------- setup code

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for {task_id}.

{summary}

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"

BASE_STATE = json.loads(r"""
{{
  "currentUser": {{"id": 2330, "username": "byteblaze", "name": "Byte Blaze",
                  "email": "ericwbailey@fakegithub.com", "state": "active",
                  "created_at": "2023-03-23 07:30:04.033203", "location": "Boston, MA",
                  "organization": "@github ",
                  "bio": "Inclusive design and accessibility advocate. Accessibility and design systems wonk for @primer.",
                  "followers": 2, "following": 3, "feed_token": "TMN_bBn9Z48qVbUFZV45", "status": null}},
  "snippets": [],
  "repo": {{"fileOverlay": {{}}, "treeOverlay": {{}}, "commitOverlay": {{}}, "branchOverlay": {{}},
           "tagOverlay": {{}}, "branchDeletions": {{}}, "tagDeletions": {{}}, "forkOrigin": {{}}}},
  "ui": {{"notificationLevels": {{}}, "sidebarCollapsed": false, "dismissedAlerts": [],
         "preferences": {{"colorScheme": "light", "syntaxTheme": "white"}},
         "projectSettings": {{}}}},
  "nextIds": {{"project": 194, "group": 7, "issue": 83821, "mr": 139278, "note": 310827,
              "label": 1927, "milestone": 590, "member": {next_member}}}
}}
""")

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

# byteblaze's twelve own project records, republished with `commit_count` set to
# the branch total the Contributors page reports for the project's default ref.
# The two surfaces disagree on the pristine seed (dotfiles 553 vs 552,
# a11y-webring.club 235 vs 137) and that disagreement reorders the ranking, so
# the recount is what makes "most commits" have one answer whichever surface the
# agent reads. `projectEdits` replaces the whole frozen record, so each entry is
# the complete project row with one field changed.
PROJECT_EDITS = json.loads(r"""
{recount}
""")

EXTRA_MEMBERS = json.loads(r"""
{extra_members}
""")


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {{}}
        state[deleted] = []
    state["projectEdits"] = PROJECT_EDITS
    state["newMembers"] = EXTRA_MEMBERS
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


def setup_code(task_id, summary, extra_members, next_member):
    return SETUP_TEMPLATE.format(
        task_id=task_id,
        summary=summary,
        recount=RECOUNT_JSON,
        extra_members=json.dumps(extra_members, indent=1),
        next_member=next_member,
    )


# --------------------------------------------------------------- reward code

REWARD_BODY = '''
COMPONENT_WEIGHTS = json.loads(r"""
{weights}
""")
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

# The frozen `members.json` rows that sit on byteblaze's own twelve projects.
# Inlined because the reward only ever sees the persisted overlay document; the
# effective membership of a project is these rows (minus `deletedMembers`, with
# `memberEdits` applied) plus the matching `newMembers` rows.
SEED_MEMBERS = json.loads(r"""
{seed_members}
""")

# component -> {{project_id, project, members: {{user_id: access_level}}, expires}}
TARGETS = json.loads(r"""
{targets}
""")

# project_id -> {{user_id: access_level}} that must still describe the project.
BASELINE = json.loads(r"""
{baseline}
""")

# user ids that must hold no membership on any of byteblaze's own projects.
ABSENT_USERS = json.loads(r"""
{absent_users}
""")
ABSENT_COMPONENT = {absent_component!r}
BASELINE_COMPONENT = {baseline_component!r}
BYTEBLAZE_PROJECT_IDS = json.loads(r"""
{all_ids}
""")


def _dict(value):
    return value if isinstance(value, dict) else {{}}


def _list(value):
    return value if isinstance(value, list) else []


def _member_rows(state):
    """Every membership record the persisted state currently describes."""
    edits = _dict(state.get("memberEdits"))
    deleted = set(str(key) for key in _list(state.get("deletedMembers")))
    rows = []
    for row in SEED_MEMBERS:
        key = str(row.get("id"))
        if key in deleted:
            continue
        replacement = edits.get(key)
        rows.append(replacement if isinstance(replacement, dict) else row)
    for row in _list(state.get("newMembers")):
        if not isinstance(row, dict):
            continue
        key = str(row.get("id"))
        if key in deleted:
            continue
        replacement = edits.get(key)
        rows.append(replacement if isinstance(replacement, dict) else row)
    return rows


def _level(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _access(rows, project_id):
    """user_id -> (access_level, expires_at) for one project."""
    out = {{}}
    for row in rows:
        if str(row.get("source_type")) != "project":
            continue
        if str(row.get("source_id")) != str(project_id):
            continue
        level = _level(row.get("access_level"))
        if level is None:
            continue
        expires = row.get("expires_at")
        expires = "" if expires is None else str(expires).strip()
        out[str(row.get("user_id"))] = (level, expires)
    return out


def _matches(actual, wanted_levels, wanted_expires):
    if set(actual.keys()) != set(wanted_levels.keys()):
        return False
    for uid, level in wanted_levels.items():
        got = actual.get(uid)
        if got is None or got[0] != int(level):
            return False
        if got[1] != str(wanted_expires.get(uid, "")):
            return False
    return True


def _holds(actual, wanted_levels, wanted_expires):
    """The listed users hold the listed levels; other members are not consulted."""
    for uid, level in wanted_levels.items():
        got = actual.get(uid)
        if got is None or got[0] != int(level):
            return False
        if got[1] != str(wanted_expires.get(uid, "")):
            return False
    return True


def _levels_only(actual):
    return dict((uid, pair[0]) for uid, pair in actual.items())


def score_state(state):
    state = _dict(state)
    rows = _member_rows(state)

    checks = {{}}
    details = {{}}
    target_ids = set()
    for spec in TARGETS:
        pid = str(spec["project_id"])
        target_ids.add(pid)
        actual = _access(rows, pid)
        if spec.get("exact", True):
            ok = _matches(actual, spec["members"], spec.get("expires") or {{}})
        else:
            ok = _holds(actual, spec["members"], spec.get("expires") or {{}})
        checks[spec["component"]] = ok
        details[spec["component"]] = "%s access is %r, wanted %r with expiry %r" % (
            spec["project"], _levels_only(actual), spec["members"],
            spec.get("expires") or {{}})

    every_target_ok = bool(TARGETS) and all(
        checks[spec["component"]] for spec in TARGETS)

    if ABSENT_COMPONENT:
        holders = []
        for pid in BYTEBLAZE_PROJECT_IDS:
            access = _access(rows, pid)
            for uid in ABSENT_USERS:
                if str(uid) in access:
                    holders.append("%s@%s" % (uid, pid))
        checks[ABSENT_COMPONENT] = not holders
        details[ABSENT_COMPONENT] = "remaining memberships: %r" % (sorted(holders),)

    if BASELINE_COMPONENT:
        drifted = []
        for pid, wanted in BASELINE.items():
            if pid in target_ids:
                continue
            actual = _levels_only(_access(rows, pid))
            if actual != dict((k, int(v)) for k, v in wanted.items()):
                drifted.append(pid)
        checks[BASELINE_COMPONENT] = every_target_ok and not drifted
        details[BASELINE_COMPONENT] = "projects off their baseline: %r" % (sorted(drifted),)

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

REWARD_TEMPLATE = '''"""Deterministic reward for {task_id}.

{rubric}

Membership writes land in the gitlab mock's overlay keys (SCHEMA.md /
src/utils/overlayShape.js:48): `addMembers` (components/create/mutations.js:363)
appends to `newMembers`, the Max-role dropdown (pages/MembersTable.jsx:219)
rewrites a frozen row into `memberEdits` or a created row in place, and Remove
member (:227) appends to `deletedMembers`. Scored against `current_state` only.
"""
import json

{body}

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {{"score": _clamp(float(total)), "components": components}}
'''

NEMO_TEMPLATE = '''"""NeMo-Gym reward program for {task_id}.

Same rubric as reward.py, read from GET /go?sid=... instead of a frozen
evidence bundle. Prints REWARD: <float> on every output path.

Self-contained: standard library plus `requests`.
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"

{body}

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {{}}
    except Exception as exc:  # noqa: BLE001 - a failed read must still score
        print("reward read failed: %s" % exc, file=sys.stderr)
        print("REWARD: 0.0")
        return
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''


def reward_pair(task_id, rubric, weights, targets, absent_users, absent_component,
                baseline_component):
    body = REWARD_BODY.format(
        weights=json.dumps(weights, indent=1),
        seed_members=SEED_MEMBERS_JSON,
        targets=json.dumps(targets, indent=1),
        baseline=json.dumps(BASELINE, indent=1, sort_keys=True),
        absent_users=json.dumps(absent_users),
        absent_component=absent_component,
        baseline_component=baseline_component,
        all_ids=json.dumps(ALL_BB_IDS),
    )
    return (REWARD_TEMPLATE.format(task_id=task_id, rubric=rubric, body=body),
            NEMO_TEMPLATE.format(task_id=task_id, body=body))


# ------------------------------------------------------------------ tasks

def member_row(mid, pid, uid, level, label):
    return {"id": mid, "source_type": "project", "source_id": pid, "user_id": uid,
            "access_level": level, "access_label": label,
            "created_at": "2023-04-28 09:12:44.113004", "expires_at": None,
            "created_by_id": 2330}


OWNER = {"2330": 50}


def owner_plus(*pairs):
    out = dict(OWNER)
    for uid, lvl in pairs:
        out[str(uid)] = lvl
    return out


RECOUNT_NOTE = (
    "projectEdits for byteblaze's twelve own projects, each republishing the "
    "frozen record with commit_count set to the Contributors-page branch total "
    "(1615/552/188/150/137/108/45/23/22/8/7/3). On the pristine seed the project "
    "record and the Contributors page disagree (dotfiles 553 vs 552, "
    "a11y-webring.club 235 vs 137) and that disagreement reorders the top three, "
    "so the recount is what gives 'most commits' a single answer on both "
    "surfaces. It grants nobody any access and so pre-satisfies no component."
)

A576 = 'Add the following users to repo a11y-webring.club as developer: "abisubramanya27" and "lahwaacz"'
A577 = 'Add the following users to my GitHub timeline item management extension as maintainer: "abisubramanya27" and "lahwaacz"'
A578 = 'Add the following users to repo millennials-to-snake-people as reporter: "yjlou" and "a11yproject"'
A579 = 'Add the following users to my time tracking tool as guest: "yjlou"'
A526 = "Star the top three most stared repos in Gitlab"
A523 = "Star the top five most stared repos in Gitlab"
A480 = "Invite yjlou as collaborator(s) to solarized-prism-theme repo"
A567 = "Invite Jakub Klinkovský and Benoît Blanchon as collaborator(s) to gimmiethat.space repo"
A169 = "Tell me the full names of the repositories where I made contributions and they got the most stars?"

TASKS = []

# --- 001 -------------------------------------------------------------------
TASKS.append(dict(
    n="001",
    instruction=("Two contractors start on my busiest code tomorrow. Add vinta and lahwaacz "
                 "as Developers on the three byteblaze repositories that have the most commits."),
    difficulty="hard", style="terse", shape="retrieval_writeback",
    skills=["R1", "R4", "A4", "A3"],
    skill_chain=("rank byteblaze's twelve own repos by commit count -> take the top three -> "
                 "apply the same membership grant across that matched set -> invite two users "
                 "at Developer on each"),
    hard_criteria=["multi_mutation", "derived_target"],
    analogues=[A576, A526],
    weights={"ericwbailey_website_developers_added": 0.34,
             "dotfiles_developers_added": 0.33,
             "accessible_html_patterns_developers_added": 0.33},
    targets=[
        dict(component="ericwbailey_website_developers_added", project_id=182,
             project="byteblaze/ericwbailey.website",
             members=owner_plus((278, 30), (1842, 30)), expires={}),
        dict(component="dotfiles_developers_added", project_id=193,
             project="byteblaze/dotfiles",
             members=owner_plus((278, 30), (1842, 30)), expires={}),
        dict(component="accessible_html_patterns_developers_added", project_id=185,
             project="byteblaze/accessible-html-content-patterns",
             members=owner_plus((278, 30), (1842, 30)), expires={}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total, so the overview and the Contributors page "
                   "agree on the ranking. Top three become ericwbailey.website 1615, dotfiles 552 "
                   "and accessible-html-content-patterns 188, ahead of empathy-prompts at 150."),
    rubric=("The recount makes byteblaze's three most-committed repos ericwbailey.website (1615), "
            "dotfiles (552) and accessible-html-content-patterns (188). Each of those three must "
            "end up with exactly byteblaze as Owner plus vinta (278) and lahwaacz (1842) as "
            "Developers (access_level 30) with no expiry."),
    criteria=[
        "byteblaze/ericwbailey.website membership is exactly byteblaze Owner, vinta Developer, lahwaacz Developer.",
        "byteblaze/dotfiles membership is exactly byteblaze Owner, vinta Developer, lahwaacz Developer.",
        "byteblaze/accessible-html-content-patterns membership is exactly byteblaze Owner, vinta Developer, lahwaacz Developer.",
    ],
    notes=[
        "Ranking margin: third place accessible-html-content-patterns 188 versus fourth empathy-prompts 150, margin 38; all twelve recounted values are distinct.",
        "Route: / -> project row -> Project information -> /activity -> Members -> Invite members. Sidebar children do not appear on hover; the section link must be clicked first.",
    ],
))

# --- 002 -------------------------------------------------------------------
TASKS.append(dict(
    n="002",
    instruction=("I'm handing my three quietest byteblaze repositories, the ones with the fewest "
                 "commits, over to davepgreene. Make him a Maintainer on each of them."),
    difficulty="hard", style="terse", shape="retrieval_writeback",
    skills=["R1", "R4", "A4", "A3"],
    skill_chain=("rank byteblaze's own repos by commit count -> take the bottom three -> apply "
                 "one membership grant across that matched set -> invite davepgreene at Maintainer"),
    hard_criteria=["multi_mutation", "derived_target"],
    analogues=[A577, A526],
    weights={"gimmiethat_space_maintainer_added": 0.34,
             "solarized_prism_theme_maintainer_added": 0.33,
             "remove_board_movement_maintainer_added": 0.33},
    targets=[
        dict(component="gimmiethat_space_maintainer_added", project_id=184,
             project="byteblaze/gimmiethat.space",
             members=owner_plus((168, 30), (2365, 40)), expires={}),
        dict(component="solarized_prism_theme_maintainer_added", project_id=188,
             project="byteblaze/solarized-prism-theme",
             members=owner_plus((5, 10), (2365, 40)), expires={}),
        dict(component="remove_board_movement_maintainer_added", project_id=181,
             project="byteblaze/remove-board-movement-events-from-the-github-issue-timeline",
             members=owner_plus((2365, 40)), expires={}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total. The three lowest are gimmiethat.space 3, "
                   "solarized-prism-theme 7 and remove-board-movement-events-... 8, clear of "
                   "timeit at 22."),
    rubric=("The three lowest recounted commit totals are gimmiethat.space (3), "
            "solarized-prism-theme (7) and remove-board-movement-events-from-the-github-issue-"
            "timeline (8). Each must end with davepgreene (2365) at Maintainer (40) alongside "
            "its existing membership: yjlou stays a Developer on gimmiethat.space and "
            "abisubramanya27 stays a Guest on solarized-prism-theme."),
    criteria=[
        "byteblaze/gimmiethat.space membership is exactly byteblaze Owner, yjlou Developer, davepgreene Maintainer.",
        "byteblaze/solarized-prism-theme membership is exactly byteblaze Owner, abisubramanya27 Guest, davepgreene Maintainer.",
        "byteblaze/remove-board-movement-events-from-the-github-issue-timeline membership is exactly byteblaze Owner and davepgreene Maintainer.",
    ],
    notes=[
        "Ranking margin: third-lowest is 8 versus fourth-lowest timeit at 22, margin 14. The bottom three are identical before and after the recount, so the injection only removes the surface disagreement.",
        "Two of the three repositories already carry a second member, so the exact-set assertion also rejects a run that clears the table before inviting.",
    ],
))

# --- 003 -------------------------------------------------------------------
TASKS.append(dict(
    n="003",
    instruction=("yjlou needs to read whichever of my private byteblaze repositories has the most "
                 "commits. Add him there as a Reporter."),
    difficulty="medium", style="terse", shape="retrieval_writeback",
    skills=["R1", "A3"],
    skill_chain=("filter byteblaze's own repos to the private ones -> take the one with the most "
                 "commits -> grant yjlou Reporter there"),
    hard_criteria=None,
    analogues=[A578],
    weights={"accessible_html_patterns_reporter_added": 1.0},
    targets=[
        dict(component="accessible_html_patterns_reporter_added", project_id=185,
             project="byteblaze/accessible-html-content-patterns",
             members=owner_plus((168, 20)), expires={}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total. The three private ones are then "
                   "accessible-html-content-patterns 188, solarized-prism-theme 7 and "
                   "gimmiethat.space 3."),
    rubric=("Among byteblaze's three private projects the most-committed is "
            "accessible-html-content-patterns (188, against 7 and 3). It must end with exactly "
            "byteblaze as Owner and yjlou (168) as Reporter (access_level 20)."),
    criteria=[
        "byteblaze/accessible-html-content-patterns membership is exactly byteblaze Owner and yjlou Reporter.",
    ],
    notes=[
        "Margin inside the private subset is 181 commits, and the subset is read off the lock icon on the dashboard project rows.",
        "The distractor is the instance-wide leader: ericwbailey.website has 1615 commits but is public, so the predicate has to be applied rather than the list eyeballed.",
    ],
))

# --- 004 -------------------------------------------------------------------
TASKS.append(dict(
    n="004",
    instruction=(
        "Abishek S, username abisubramanya27, is taking over maintenance of the three byteblaze "
        "repositories that carry the fewest commits, so work out which three those are and make "
        "sure he holds the Developer role on all three of them. He is already listed on one of "
        "them at a lower role; the invite picker will not offer a user who is already a member, "
        "so raise that one from the project's members table instead of trying to invite him "
        "again. Nobody else's role may change: yjlou keeps his Developer row, and my own Owner "
        "rows on every project must be left exactly as they are."),
    difficulty="hard", style="explicit", shape="retrieval_writeback",
    skills=["R1", "R4", "A13", "A3"],
    skill_chain=("rank byteblaze's own repos by commit count -> take the bottom three -> read "
                 "each project's members table -> invite where he is absent, promote in place "
                 "where he is already a Guest"),
    hard_criteria=["multi_mutation", "derived_target", "exclusion_constraint"],
    analogues=[A576, A526],
    weights={"gimmiethat_space_developer_granted": 0.25,
             "remove_board_movement_developer_granted": 0.25,
             "solarized_prism_theme_role_raised": 0.25,
             "other_projects_membership_unchanged": 0.25},
    targets=[
        dict(component="gimmiethat_space_developer_granted", project_id=184,
             project="byteblaze/gimmiethat.space",
             members=owner_plus((168, 30), (5, 30)), expires={}),
        dict(component="remove_board_movement_developer_granted", project_id=181,
             project="byteblaze/remove-board-movement-events-from-the-github-issue-timeline",
             members=owner_plus((5, 30)), expires={}),
        dict(component="solarized_prism_theme_role_raised", project_id=188,
             project="byteblaze/solarized-prism-theme",
             members=owner_plus((5, 30)), expires={}),
    ],
    baseline_component="other_projects_membership_unchanged",
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total, fixing the bottom three at gimmiethat.space 3, "
                   "solarized-prism-theme 7 and remove-board-movement-events-... 8."),
    rubric=("The bottom three by recounted commits are gimmiethat.space (3), "
            "solarized-prism-theme (7) and remove-board-movement-events-from-the-github-issue-"
            "timeline (8). abisubramanya27 (5) is a seeded Guest on solarized-prism-theme "
            "(members.json row 205), so that one is a Max-role change writing memberEdits['205'] "
            "while the other two are invites. Every other byteblaze project must still show its "
            "seeded membership."),
    criteria=[
        "byteblaze/gimmiethat.space membership is exactly byteblaze Owner, yjlou Developer, abisubramanya27 Developer.",
        "byteblaze/remove-board-movement-events-from-the-github-issue-timeline membership is exactly byteblaze Owner and abisubramanya27 Developer.",
        "byteblaze/solarized-prism-theme membership is exactly byteblaze Owner and abisubramanya27 Developer (raised from Guest).",
        "Every other byteblaze project still shows exactly its seeded membership.",
    ],
    notes=[
        "The conditional branch is real seed data, not an injection: abisubramanya27 is already a Guest on solarized-prism-theme, and MembersTable.jsx:186 filters existing members out of the invite picker, so the agent must read the table before choosing a control.",
        "Bottom-three margin 8 versus 22.",
    ],
))

# --- 005 -------------------------------------------------------------------
TASKS.append(dict(
    n="005",
    instruction=("Add a11yproject and westurner as Reporters on the byteblaze repository with the "
                 "second-highest commit count."),
    difficulty="medium", style="terse", shape="retrieval_writeback",
    skills=["R4", "A3"],
    skill_chain=("order byteblaze's own repos by commit count -> take the second one -> invite "
                 "two users there at Reporter"),
    hard_criteria=None,
    analogues=[A578],
    weights={"dotfiles_reporters_added": 1.0},
    targets=[
        dict(component="dotfiles_reporters_added", project_id=193,
             project="byteblaze/dotfiles",
             members=owner_plus((2325, 20), (561, 20)), expires={}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total, so second place is dotfiles at 552 behind "
                   "ericwbailey.website at 1615."),
    rubric=("Second by recounted commits is dotfiles (552), behind ericwbailey.website (1615) and "
            "ahead of accessible-html-content-patterns (188). It must end with exactly byteblaze "
            "as Owner plus a11yproject (2325) and westurner (561) at Reporter (20)."),
    criteria=[
        "byteblaze/dotfiles membership is exactly byteblaze Owner, a11yproject Reporter, westurner Reporter.",
    ],
    notes=[
        "Ordinal margin: 1615 / 552 / 188, so first, second and third are unambiguous on both the overview and the Contributors page after the recount.",
        "Both invitees can be added in one Invite members submission; the modal's token selector accepts several users per submit.",
    ],
))

# --- 006 -------------------------------------------------------------------
TASKS.append(dict(
    n="006",
    instruction=("Three auditors need Reporter access, expiring 2024-06-30, on my three "
                 "most-committed public byteblaze repositories. Add convexegg, patrickhlauke and "
                 "westurner to each of them."),
    difficulty="hard", style="terse", shape="retrieval_writeback",
    skills=["R1", "R4", "A4", "A3"],
    skill_chain=("filter byteblaze's own repos to the public ones -> rank by commit count -> take "
                 "the top three -> grant the same three users Reporter with an expiry across that set"),
    hard_criteria=["multi_mutation", "derived_target"],
    analogues=[A578, A523],
    weights={"ericwbailey_website_auditors_added": 0.34,
             "dotfiles_auditors_added": 0.33,
             "empathy_prompts_auditors_added": 0.33},
    targets=[
        dict(component="ericwbailey_website_auditors_added", project_id=182,
             project="byteblaze/ericwbailey.website",
             members=owner_plus((43, 20), (119, 20), (561, 20)),
             expires={"43": "2024-06-30", "119": "2024-06-30", "561": "2024-06-30"}),
        dict(component="dotfiles_auditors_added", project_id=193,
             project="byteblaze/dotfiles",
             members=owner_plus((43, 20), (119, 20), (561, 20)),
             expires={"43": "2024-06-30", "119": "2024-06-30", "561": "2024-06-30"}),
        dict(component="empathy_prompts_auditors_added", project_id=183,
             project="byteblaze/empathy-prompts",
             members=owner_plus((43, 20), (119, 20), (561, 20)),
             expires={"43": "2024-06-30", "119": "2024-06-30", "561": "2024-06-30"}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total. Among the nine public ones the top three are "
                   "ericwbailey.website 1615, dotfiles 552 and empathy-prompts 150, with "
                   "a11y-webring.club next at 137."),
    rubric=("accessible-html-content-patterns (188) is private, so the three most-committed public "
            "projects are ericwbailey.website (1615), dotfiles (552) and empathy-prompts (150). "
            "Each must end with byteblaze as Owner plus convexegg (43), patrickhlauke (119) and "
            "westurner (561) at Reporter (20), every one of them carrying expires_at 2024-06-30."),
    criteria=[
        "byteblaze/ericwbailey.website membership is exactly byteblaze Owner plus convexegg, patrickhlauke and westurner as Reporters expiring 2024-06-30.",
        "byteblaze/dotfiles membership is exactly byteblaze Owner plus convexegg, patrickhlauke and westurner as Reporters expiring 2024-06-30.",
        "byteblaze/empathy-prompts membership is exactly byteblaze Owner plus convexegg, patrickhlauke and westurner as Reporters expiring 2024-06-30.",
    ],
    notes=[
        "The private distractor is deliberate: accessible-html-content-patterns outranks empathy-prompts on commits but fails the public predicate. Public third-place margin is 150 versus 137.",
        "The expiry field is the invite modal's optional date input, written straight through to expires_at by addMembers.",
    ],
))

# --- 007 -------------------------------------------------------------------
TASKS.append(dict(
    n="007",
    instruction=("Add lahwaacz as a Guest on whichever byteblaze repository has the fewest commits."),
    difficulty="medium", style="terse", shape="retrieval_writeback",
    skills=["R1", "A3"],
    skill_chain=("find the byteblaze repo with the lowest commit count -> invite lahwaacz there at Guest"),
    hard_criteria=None,
    analogues=[A579],
    weights={"gimmiethat_space_guest_added": 1.0},
    targets=[
        dict(component="gimmiethat_space_guest_added", project_id=184,
             project="byteblaze/gimmiethat.space",
             members=owner_plus((168, 30), (1842, 10)), expires={}),
    ],
    extra_members=[], next_member=206,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total; the minimum is gimmiethat.space at 3, with "
                   "solarized-prism-theme next at 7."),
    rubric=("The lowest recounted commit count is gimmiethat.space (3), ahead of "
            "solarized-prism-theme (7). It must end with exactly byteblaze as Owner, the seeded "
            "yjlou Developer row, and lahwaacz (1842) at Guest (10)."),
    criteria=[
        "byteblaze/gimmiethat.space membership is exactly byteblaze Owner, yjlou Developer, lahwaacz Guest.",
    ],
    notes=[
        "Minimum margin 3 versus 7.",
        "Guest is the invite modal's default selection, so this task is also the one that checks an agent does not disturb a correct default. The exact-set assertion still rejects yjlou being removed.",
    ],
))

# --- 008 -------------------------------------------------------------------
TASKS.append(dict(
    n="008",
    instruction=("yjlou has left the team. Drop his access from my byteblaze repositories, and "
                 "give lahwaacz the role yjlou held, on the repository where he held it."),
    difficulty="hard", style="terse", shape="retrieval_writeback",
    skills=["R7", "R9", "A3"],
    skill_chain=("scan the members tables of byteblaze's own repos for yjlou -> read the access "
                 "level he holds there -> remove him -> grant lahwaacz that same level on that "
                 "same repo"),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[A480, A579],
    weights={"yjlou_access_revoked": 0.4, "lahwaacz_took_over_gimmiethat_space": 0.6},
    targets=[
        dict(component="lahwaacz_took_over_gimmiethat_space", project_id=184,
             project="byteblaze/gimmiethat.space",
             members=owner_plus((1842, 30)), expires={}),
    ],
    absent_users=[168],
    absent_component="yjlou_access_revoked",
    extra_members=None, next_member=None,
    setup_summary=None,
    rubric=("yjlou (168) holds exactly one membership on byteblaze's own projects: Developer (30) "
            "on gimmiethat.space, members.json row 204. He must hold none of them afterwards, and "
            "gimmiethat.space must end with exactly byteblaze as Owner and lahwaacz (1842) at the "
            "same Developer level."),
    criteria=[
        "yjlou holds no membership on any byteblaze-owned project.",
        "byteblaze/gimmiethat.space membership is exactly byteblaze Owner and lahwaacz Developer.",
    ],
    notes=[
        "No injection: the seed already places yjlou on exactly one byteblaze project, so both the target repo and the role are derived from the site.",
        "The role is never stated in the instruction, which is what makes an agent that guesses Guest score 0.4 rather than 1.0.",
    ],
))

# --- 009 -------------------------------------------------------------------
TASKS.append(dict(
    n="009",
    instruction=(
        "Access review. Jakub Klinkovsky, username lahwaacz, is being promoted to Maintainer "
        "across the three byteblaze repositories with the highest commit counts, so identify "
        "those three and give him the Maintainer role on each. He already sits on one of them at "
        "a lower role, and the invite dialog will not list a user who is already a member, so "
        "raise that one from the project's members table. No other membership may move, and my "
        "own Owner rows must stay exactly as they are."),
    difficulty="hard", style="explicit", shape="retrieval_writeback",
    skills=["R1", "R4", "A13", "A3"],
    skill_chain=("rank byteblaze's own repos by commit count -> take the top three -> read each "
                 "members table -> invite at Maintainer where he is absent, raise the Max role "
                 "where he already holds Reporter"),
    hard_criteria=["multi_mutation", "derived_target", "exclusion_constraint"],
    analogues=[A577, A526],
    weights={"ericwbailey_website_maintainer_granted": 0.25,
             "accessible_html_patterns_maintainer_granted": 0.25,
             "dotfiles_role_raised_to_maintainer": 0.25,
             "other_projects_membership_unchanged": 0.25},
    targets=[
        dict(component="ericwbailey_website_maintainer_granted", project_id=182,
             project="byteblaze/ericwbailey.website",
             members=owner_plus((1842, 40)), expires={}),
        dict(component="accessible_html_patterns_maintainer_granted", project_id=185,
             project="byteblaze/accessible-html-content-patterns",
             members=owner_plus((1842, 40)), expires={}),
        dict(component="dotfiles_role_raised_to_maintainer", project_id=193,
             project="byteblaze/dotfiles",
             members=owner_plus((1842, 40)), expires={}),
    ],
    baseline_component="other_projects_membership_unchanged",
    extra_members=[member_row(206, 193, 1842, 20, "Reporter")],
    next_member=207,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total, and seats lahwaacz as a Reporter on "
                   "byteblaze/dotfiles so one of the three top repositories needs a role change "
                   "rather than an invite."),
    rubric=("Top three by recounted commits: ericwbailey.website (1615), dotfiles (552) and "
            "accessible-html-content-patterns (188). lahwaacz (1842) is injected as a Reporter on "
            "dotfiles, so that project needs the Max-role dropdown while the other two need "
            "invites. Each of the three must end with exactly byteblaze as Owner and lahwaacz at "
            "Maintainer (40); every other byteblaze project keeps its seeded membership."),
    criteria=[
        "byteblaze/ericwbailey.website membership is exactly byteblaze Owner and lahwaacz Maintainer.",
        "byteblaze/dotfiles membership is exactly byteblaze Owner and lahwaacz Maintainer, raised from the injected Reporter row.",
        "byteblaze/accessible-html-content-patterns membership is exactly byteblaze Owner and lahwaacz Maintainer.",
        "Every other byteblaze project still shows exactly its seeded membership.",
    ],
    notes=[
        "The injected Reporter row is a created record, so the promotion is reconciled in place inside newMembers rather than into memberEdits; the reward reads the effective level either way.",
        "The injection does not pre-satisfy anything: Reporter is 20 and every component demands 40.",
    ],
))

# --- 010 -------------------------------------------------------------------
TASKS.append(dict(
    n="010",
    instruction=("Everyone who can reach my most-committed byteblaze repository should have the "
                 "same access on my second-most-committed one. Make that true."),
    difficulty="hard", style="terse", shape="retrieval_writeback",
    skills=["R1", "R4", "R9", "A3"],
    skill_chain=("rank byteblaze's own repos by commit count -> take the first and the second -> "
                 "read the first one's members table for who holds what -> reproduce those roles "
                 "on the second"),
    hard_criteria=["derived_target", "cross_section"],
    analogues=[A567, A169],
    weights={"dotfiles_grants_vinta_developer": 0.3,
             "dotfiles_grants_westurner_reporter": 0.3,
             "dotfiles_access_list_mirrors_source": 0.4},
    targets=[
        dict(component="dotfiles_grants_vinta_developer", project_id=193,
             project="byteblaze/dotfiles", exact=False,
             members={"278": 30}, expires={}),
        dict(component="dotfiles_grants_westurner_reporter", project_id=193,
             project="byteblaze/dotfiles", exact=False,
             members={"561": 20}, expires={}),
        dict(component="dotfiles_access_list_mirrors_source", project_id=193,
             project="byteblaze/dotfiles",
             members=owner_plus((278, 30), (561, 20)), expires={}),
    ],
    extra_members=[member_row(206, 182, 278, 30, "Developer"),
                   member_row(207, 182, 561, 20, "Reporter")],
    next_member=208,
    setup_summary=("Republishes byteblaze's twelve project records with commit_count set to the "
                   "Contributors-page branch total, and seats vinta as a Developer and westurner "
                   "as a Reporter on byteblaze/ericwbailey.website so the top repository has an "
                   "access list worth copying."),
    rubric=("First and second by recounted commits are ericwbailey.website (1615) and dotfiles "
            "(552). ericwbailey.website is seeded with byteblaze Owner plus an injected vinta "
            "(278) Developer and westurner (561) Reporter. dotfiles must end with exactly those "
            "same three: byteblaze Owner, vinta Developer, westurner Reporter. The two components "
            "split the two roles the agent has to reproduce; both read the same exact end set, so "
            "copying one role and inventing the other pays nothing."),
    criteria=[
        "byteblaze/dotfiles membership is exactly byteblaze Owner, vinta Developer, westurner Reporter.",
        "vinta's level on dotfiles is Developer, matching ericwbailey.website.",
        "westurner's level on dotfiles is Reporter, matching ericwbailey.website.",
    ],
    notes=[
        "The roles are never stated in the instruction; they are read off the source project's Max role column, so an agent that invites both at one level scores 0.",
        "Import from a project (MembersTable.jsx:740) reproduces the source list in one submission and is an equally correct route. The seed alone cannot exercise it, because byteblaze is the only member of every project he owns; the injection is what makes that control live.",
    ],
))


# ------------------------------------------------------------------ writer

INSPIRATION = ["webarena-576", "webarena-577", "webarena-578", "webarena-579",
               "webarena-480", "webarena-567", "webarena-526", "webarena-523",
               "webarena-169"]

index_rows = []
nemo_rows = []

for t in TASKS:
    task_id = "grant_access_top_repos_%s" % t["n"]
    bundle = os.path.join(OUT, task_id)
    os.makedirs(bundle, exist_ok=True)

    reward_src, nemo_src = reward_pair(
        task_id, t["rubric"], t["weights"], t["targets"],
        t.get("absent_users") or [], t.get("absent_component") or "",
        t.get("baseline_component") or "")

    setup_src = None
    if t.get("extra_members") is not None:
        setup_src = setup_code(task_id, t["setup_summary"], t["extra_members"],
                               t["next_member"])

    with open(os.path.join(bundle, "reward.py"), "w") as fh:
        fh.write(reward_src)
    with open(os.path.join(bundle, "nemo_reward.py"), "w") as fh:
        fh.write(nemo_src)
    setup_path = os.path.join(bundle, "initial_setup.py")
    if setup_src is None:
        if os.path.exists(setup_path):
            os.remove(setup_path)
    else:
        with open(setup_path, "w") as fh:
            fh.write(setup_src)

    instruction = {
        "task_id": task_id,
        "task_instruction": t["instruction"],
        "app_dir": "webarena_gitlab_mock",
        "start_path": "/",
        "difficulty": t["difficulty"],
        "success_criteria": t["criteria"],
    }
    with open(os.path.join(bundle, "task_instruction.json"), "w") as fh:
        json.dump(instruction, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    injected = []
    if setup_src is not None:
        injected.append(RECOUNT_NOTE)
        for row in t["extra_members"]:
            injected.append(
                "newMembers row id %d: user %d on project %d at access_level %d (%s) "
                "- seats the pre-existing membership the task's branch depends on, "
                "at a level no component accepts."
                % (row["id"], row["user_id"], row["source_id"], row["access_level"],
                   row["access_label"]))

    metadata = {
        "style": t["style"],
        "difficulty": t["difficulty"],
        "shape": t["shape"],
        "skills": t["skills"],
        "skill_chain": t["skill_chain"],
        "official_analogues": t["analogues"],
        "topic": "gitlab grant access top repos",
        "inspiration_ids": INSPIRATION,
        "authoring_notes": t["notes"] + [
            "Hub source: hub/websites/webarena_gitlab_mock. Invite members modal "
            "MembersTable.jsx:319-390 -> mutations.js addMembers (:363) writes "
            "newMembers; Max role dropdown MembersTable.jsx:219 -> updateIn writes "
            "memberEdits or the created row in place; Remove member :227 writes "
            "deletedMembers.",
            "byteblaze is Owner (access_level 50) on all twelve of his own projects, "
            "so canManageMembers is true and the Invite members button renders "
            "(MembersTable.jsx:118).",
        ],
    }
    if t.get("hard_criteria"):
        metadata["hard_criteria"] = t["hard_criteria"]
    if injected:
        metadata["injected_preconditions"] = injected

    manifest = {
        "schema_version": 2,
        "task_id": task_id,
        "instruction": t["instruction"],
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
    }
    with open(os.path.join(bundle, "task.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    row = {"task_payload": {
        "task_id": task_id,
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": ["webarena_gitlab_mock"],
        "start_urls": [],
        "intent": t["instruction"],
        "eval": {
            "eval_types": ["string_match"],
            "reference_answers": None,
            "note": "unused \u2014 CUA-Gym reward code is authoritative",
        },
        "cuagym": {
            "bundle_id": task_id,
            "app_dir": "webarena_gitlab_mock",
            "initial_setup": setup_src,
            "eval_reward_code": nemo_src,
        },
    }}
    with open(os.path.join(bundle, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    index_rows.append({"task_id": task_id, "path": "%s/task.json" % task_id})
    nemo_rows.append(row)

os.makedirs(BATCH, exist_ok=True)
with open(os.path.join(BATCH, "index.json"), "w") as fh:
    json.dump({"schema_version": 2, "tasks": index_rows}, fh, indent=2)
    fh.write("\n")
with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
    for row in nemo_rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")

print("wrote %d bundles" % len(TASKS))
