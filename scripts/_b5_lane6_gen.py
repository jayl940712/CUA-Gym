#!/usr/bin/env python3
"""Batch-5 lane 6 authoring generator: gitlab template_project_staffed.

Emits the 10 bundles under output/tasks/gitlab/template_project_staffed_NNN/.
Reads nothing from the running hub; every constant below was read out of
hub/websites/webarena_gitlab_mock/src/ during authoring.
"""
import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
OUT = os.path.join(ROOT, "output/tasks/gitlab")
BATCH = os.path.join(OUT, "_batches/template_project_staffed")
REPLAYS = os.path.join(BATCH, "replays")

# ---- official intents, quoted verbatim out of the benchmark ---------------
OFFICIAL = {}
with open(os.path.join(ROOT, "webarena_benchmarks/webarena.jsonl"), encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            row = json.loads(line)
            OFFICIAL[row["id"]] = row["ques"]

# ---- templates (src/components/create/templates.js) ----------------------
TEMPLATES = {
    "android": ("Android", "A ready-to-go template for use with Android apps"),
    "express": ("NodeJS Express", "Includes an MVC structure to help you get started"),
    "jekyll": ("Pages/Jekyll",
               "Example Jekyll site using GitLab Pages: https://pages.gitlab.io/jekyll"),
    "plainhtml": ("Pages/Plain HTML",
                  "Example plain HTML site using GitLab Pages: https://pages.gitlab.io/plain-html"),
    "iosswift": ("iOS (Swift)", "A ready-to-go template for use with iOS Swift apps"),
    "rails": ("Ruby on Rails",
              "Includes an MVC structure, Gemfile, Rakefile, along with many others, "
              "to help you get started"),
    "gatsby": ("Pages/Gatsby", "Everything you need to create a GitLab Pages site using Gatsby"),
    "hugo": ("Pages/Hugo", "Everything you need to create a GitLab Pages site using Hugo"),
    "dotnetcore": (".NET Core",
                   "A .NET Core console application template, customizable for any .NET Core project"),
    "gomicro": ("Go Micro", "Go Micro is a framework for micro service development"),
}

ROLE = {"Guest": 10, "Reporter": 20, "Developer": 30, "Maintainer": 40}

# ---- the ten tasks -------------------------------------------------------
TASKS = [
 dict(
  n=1, slug="kiosk_android_shell", tmpl="android", style="terse",
  instruction=("Set up a private project under byteblaze called kiosk_android_shell, "
               "scaffolded from the built-in template for a native Android app, and give "
               "vinta and convexegg Developer access."),
  members=[("vinta", 278, "Developer"), ("convexegg", 43, "Developer")],
  inspiration=["webarena-748", "webarena-753"],
  analogues=["webarena-748", "webarena-753"],
  match="Android is the only built-in row whose blurb names Android apps; "
        "Kotlin Native Linux targets Linux programs, not phones.",
 ),
 dict(
  n=2, slug="orders_api_gateway", tmpl="express", style="terse",
  instruction=("Under byteblaze, create a private project named orders_api_gateway from the "
               "built-in template that scaffolds an Express MVC app, then give lahwaacz and "
               "Seirdy Reporter access to it."),
  members=[("lahwaacz", 1842, "Reporter"), ("Seirdy", 2366, "Reporter")],
  inspiration=["webarena-749", "webarena-754"],
  analogues=["webarena-749", "webarena-754"],
  match="'NodeJS Express' is the only row naming Express; Ruby on Rails and Spring also say "
        "'MVC structure' but neither mentions Express.",
 ),
 dict(
  n=3, slug="a11y_handbook_site", tmpl="jekyll", style="terse",
  instruction=("Start a private project called a11y_handbook_site under byteblaze from the "
               "built-in template for a Jekyll site published on GitLab Pages, and invite "
               "primer and abisubramanya27 as Guests."),
  members=[("primer", 2367, "Guest"), ("abisubramanya27", 5, "Guest")],
  inspiration=["webarena-751", "webarena-756"],
  analogues=["webarena-751", "webarena-756"],
  match="Two Jekyll rows exist. 'Pages/Jekyll' is the GitLab Pages one; 'Netlify/Jekyll' says "
        "it uses Netlify for CI/CD instead of GitLab, so 'published on GitLab Pages' picks one.",
 ),
 dict(
  n=4, slug="launch_notes_index", tmpl="plainhtml", style="terse",
  instruction=("Create launch_notes_index under byteblaze as a private project built from the "
               "template for a plain HTML site published on GitLab Pages, and make vinta a "
               "Maintainer on it."),
  members=[("vinta", 278, "Maintainer")],
  inspiration=["webarena-750", "webarena-755"],
  analogues=["webarena-750", "webarena-755"],
  match="'Pages/Plain HTML' versus 'Netlify/Plain HTML'; the GitLab Pages wording disambiguates.",
 ),
 dict(
  n=5, slug="field_survey_ios", tmpl="iosswift", style="terse",
  instruction=("Set up field_survey_ios under byteblaze as a private project scaffolded from "
               "the built-in template for a Swift iOS app, and give trotzig and feuerrot "
               "Developer access."),
  members=[("trotzig", 1147, "Developer"), ("feuerrot", 737, "Developer")],
  inspiration=["webarena-748", "webarena-746"],
  analogues=["webarena-748", "webarena-746"],
  match="'iOS (Swift)' is the only Swift row in the 30-row gallery.",
 ),
 dict(
  n=6, slug="grant_tracker_rails", tmpl="rails", style="terse",
  instruction=("Under byteblaze, start a private project called grant_tracker_rails from the "
               "built-in template whose scaffold ships a Gemfile and Rakefile, then add edewit "
               "as Maintainer and jelly as Reporter."),
  members=[("edewit", 1853, "Maintainer"), ("jelly", 1846, "Reporter")],
  inspiration=["webarena-747", "webarena-742"],
  analogues=["webarena-747", "webarena-742"],
  match="Ruby on Rails is the only blurb naming a Gemfile and a Rakefile.",
 ),
 dict(
  n=7, slug="webring_relaunch", tmpl="gatsby", style="terse",
  instruction=("Start a private project under byteblaze called webring_relaunch, scaffolded "
               "from the built-in template for a Gatsby GitLab Pages site, and give it the "
               "same collaborators and roles that byteblaze/a11y-webring.club already has, "
               "apart from me."),
  members=[("Seirdy", 2366, "Maintainer"), ("lahwaacz", 1842, "Developer"),
           ("vinta", 278, "Guest")],
  inspiration=["webarena-745", "webarena-751"],
  analogues=["webarena-745", "webarena-751"],
  match="'Pages/Gatsby' is the only Gatsby row.",
  inject=dict(project_id=179, project_path="byteblaze/a11y-webring.club",
              rows=[(206, 2366, 40, "Maintainer", "2023-04-02 09:14:21.552104"),
                    (207, 1842, 30, "Developer", "2023-04-11 16:02:48.310772"),
                    (208, 278, 10, "Guest", "2023-05-06 11:47:05.918330")],
              next_member=209),
 ),
 dict(
  n=8, slug="prompt_gallery_hugo", tmpl="hugo", style="explicit",
  instruction=("byteblaze/empathy-prompts already has exactly the collaborators I want on my "
               "next site. Under byteblaze, create a new private project named "
               "prompt_gallery_hugo using the built-in project template for a Hugo site "
               "published with GitLab Pages - pick it from the template gallery on the "
               "new-project page rather than starting from a blank project. Once the project "
               "exists, open its Members page and invite exactly the same people that "
               "byteblaze/empathy-prompts lists, each at the same maximum role they hold "
               "there. byteblaze is already the owner of the new project, so only the other "
               "collaborators need inviting."),
  members=[("primer", 2367, "Developer"), ("trotzig", 1147, "Reporter")],
  inspiration=["webarena-745", "webarena-750"],
  analogues=["webarena-745", "webarena-750"],
  match="'Pages/Hugo' versus 'Netlify/Hugo'; the GitLab Pages wording disambiguates.",
  inject=dict(project_id=183, project_path="byteblaze/empathy-prompts",
              rows=[(206, 2367, 30, "Developer", "2023-03-14 08:21:36.114820"),
                    (207, 1147, 20, "Reporter", "2023-05-19 13:55:02.770415")],
              next_member=208),
 ),
 dict(
  n=9, slug="dotnet_batch_runner", tmpl="dotnetcore", style="explicit",
  instruction=("I need a scratch repository for a .NET Core command-line tool. Under the "
               "byteblaze namespace, create a project called dotnet_batch_runner and "
               "initialise it from the matching built-in project template rather than from a "
               "blank repository, so that its description and its first commit both come from "
               "the template. Its visibility must be Private, and the finished project must "
               "live at byteblaze/dotnet_batch_runner."),
  members=[],
  inspiration=["webarena-752", "webarena-754"],
  analogues=["webarena-752", "webarena-754"],
  match="'.NET Core' is the only row describing a .NET Core console application.",
 ),
 dict(
  n=10, slug="edge_metrics_gomicro", tmpl="gomicro", style="terse",
  instruction=("Create a private repository under byteblaze called edge_metrics_gomicro using "
               "the built-in template for a Go microservice framework."),
  members=[],
  inspiration=["webarena-753", "webarena-752"],
  analogues=["webarena-753", "webarena-752"],
  match="'Go Micro' is the only Go row and its blurb names micro service development.",
 ),
]

OWNER_ID = 2330

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

REWARD_HELPERS = '''

def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _whole(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if float(value).is_integer() else None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.lstrip("-").isdigit():
            return int(stripped)
    return None


def _created_project(state):
    """The project record the agent created at FULL_PATH, or None."""
    for row in _list(_dict(state).get("newProjects")):
        if isinstance(row, dict) and _text(row.get("full_path")) == FULL_PATH:
            return row
    return None


def _commit_titles(state):
    """Commit subjects recorded on the created project's default branch."""
    repo = _dict(_dict(state).get("repo"))
    rows = _list(_dict(repo.get("commitOverlay")).get(COMMIT_KEY))
    return [_text(row.get("title")) for row in rows if isinstance(row, dict)]


def _granted(state, project_id):
    """(user_id, access_level) pairs granted on the created project, owner aside."""
    pairs = set()
    for row in _list(_dict(state).get("newMembers")):
        if not isinstance(row, dict):
            continue
        if _text(row.get("source_type")) != "project":
            continue
        if _whole(row.get("source_id")) != project_id:
            continue
        user_id = _whole(row.get("user_id"))
        if user_id is None or user_id == OWNER_USER_ID:
            continue
        pairs.add((user_id, _whole(row.get("access_level"))))
    return pairs


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


def score_block(has_members):
    body = '''

def score_state(state):
    project = _created_project(state)
    project_id = _whole(project.get("id")) if isinstance(project, dict) else None
    titles = _commit_titles(state)
'''
    if has_members:
        body += '''    granted = _granted(state, project_id) if project_id is not None else set()
'''
    body += '''
    checks = {
        "project_created_private": bool(project)
            and _text(project.get("name")) == PROJECT_NAME
            and _text(project.get("visibility")) == VISIBILITY,
        "scaffolded_from_template": bool(project)
            and _text(project.get("description")) == TEMPLATE_BLURB
            and COMMIT_TITLE in titles,
'''
    if has_members:
        body += '''        "members_granted_exactly": project_id is not None
            and granted == EXPECTED_MEMBERS,
'''
    body += '''    }
    details = {
        "project_created_private": "newProjects[full_path=%s] == %r"
                                   % (FULL_PATH, project),
        "scaffolded_from_template": "description == %r; commitOverlay[%s] titles == %r"
                                    % (_text(project.get("description")) if project else None,
                                       COMMIT_KEY, titles),
'''
    if has_members:
        body += '''        "members_granted_exactly": "granted == %r, expected %r"
                                   % (sorted(granted), sorted(EXPECTED_MEMBERS)),
'''
    body += '''    }
    return _build(checks, details)
'''
    return body


def constants(task, tmpl_name, blurb, expected):
    lines = []
    if expected:
        weights = {"project_created_private": 0.3,
                   "scaffolded_from_template": 0.3,
                   "members_granted_exactly": 0.4}
    else:
        weights = {"project_created_private": 0.5,
                   "scaffolded_from_template": 0.5}
    lines.append("COMPONENT_WEIGHTS = {")
    for k, v in weights.items():
        lines.append('    "%s": %s,' % (k, v))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    lines.append("")
    lines.append('FULL_PATH = "byteblaze/%s"' % task["slug"])
    lines.append('PROJECT_NAME = "%s"' % task["slug"])
    lines.append('VISIBILITY = "private"')
    lines.append('TEMPLATE_BLURB = %r' % blurb)
    lines.append('COMMIT_TITLE = "Initialized from \'%s\' project template"' % tmpl_name)
    lines.append('COMMIT_KEY = FULL_PATH + ":main"')
    lines.append("OWNER_USER_ID = %d" % OWNER_ID)
    if expected:
        pairs = ", ".join("(%d, %d)" % p for p in expected)
        lines.append("EXPECTED_MEMBERS = {%s}" % pairs)
    return "\n".join(lines) + "\n"


def reward_source(task, tid, tmpl_name, blurb, expected):
    doc = ('"""Deterministic reward for %s.\n\n'
           'NewProject.jsx submit() -> mutations.js createProject() appends the project to\n'
           'newProjects, copies the chosen template blurb onto project.description, and writes\n'
           'the scaffold commit "Initialized from \'<Template>\' project template" into\n'
           'repo.commitOverlay["<full_path>:main"]. MembersTable.jsx invite() ->\n'
           'mutations.js addMembers() appends one newMembers row per invitee.\n\n'
           'Only current_state is read, and only user-visible persisted records.\n"""\n'
           % tid)
    return (doc + "\n" + constants(task, tmpl_name, blurb, expected)
            + score_block(bool(expected)) + REWARD_HELPERS + '''

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(component["score"] for component in components), 6)
    return {"score": _clamp(float(total)), "components": components}
''')


def nemo_reward_source(task, tid, tmpl_name, blurb, expected):
    head = ('"""NeMo-Gym reward program for %s.\n\n'
            'Same rubric as reward.py, read from GET /go?sid=... rather than a frozen\n'
            'evidence bundle. Prints REWARD: <float> on every output path.\n\n'
            'Self-contained: standard library plus requests.\n"""\n'
            'import sys\n\nimport requests\n\n'
            'SID = "__CUA_GYM_SID__"\n'
            'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n\n' % tid)
    tail = '''

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
    total = round(sum(component["score"] for component in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''
    return (head + constants(task, tmpl_name, blurb, expected)
            + score_block(bool(expected)) + REWARD_HELPERS + tail)


def setup_source(task, tid):
    inj = task["inject"]
    rows = [{"id": rid, "source_type": "project", "source_id": inj["project_id"],
             "user_id": uid, "access_level": lvl, "access_label": label,
             "created_at": created, "expires_at": None, "created_by_id": OWNER_ID}
            for (rid, uid, lvl, label, created) in inj["rows"]]
    return ('"""NeMo-Gym setup program for %s.\n\n'
            'Gives %s a real collaborator roster. The seeded project has\n'
            'byteblaze as its only member, so "staff the new project like that one" has no\n'
            'answer to read without this injection. Nothing here touches the project the task\n'
            'asks the agent to create, so the untouched lane still scores 0.0.\n\n'
            'Self-contained: standard library plus requests.\n"""\n'
            'import json\nimport sys\n\nimport requests\n\n'
            'SID = "__CUA_GYM_SID__"\n'
            'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n\n'
            'BASE_STATE = json.loads(r"""%s""")\n\n'
            '%s\n\n'
            'SOURCE_PROJECT_ID = %d\n'
            'NEXT_MEMBER_ID = %d\n\n'
            'INJECTED_MEMBERS = json.loads(r"""%s""")\n\n\n'
            'def build_state():\n'
            '    """Full createInitialData() shape, so the client-side merge is a no-op."""\n'
            '    state = dict(BASE_STATE)\n'
            '    for created, edits, deleted in OVERLAY_COLLECTIONS:\n'
            '        state[created] = []\n'
            '        state[edits] = {}\n'
            '        state[deleted] = []\n'
            '    for row in INJECTED_MEMBERS:\n'
            '        if row["source_id"] != SOURCE_PROJECT_ID:\n'
            '            raise SystemExit("fixture error: member row on the wrong project")\n'
            '    state["newMembers"] = INJECTED_MEMBERS\n'
            '    state["nextIds"] = dict(BASE_STATE["nextIds"])\n'
            '    state["nextIds"]["member"] = NEXT_MEMBER_ID\n'
            '    return state\n\n\n'
            'def publish(state):\n'
            '    response = requests.post(BASE_URL + "/post?sid=" + SID,\n'
            '                             json={"action": "set", "state": state}, timeout=30)\n'
            '    response.raise_for_status()\n'
            '    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)\n'
            '    check.raise_for_status()\n'
            '    payload = check.json()\n'
            '    if payload.get("state_diff") != {}:\n'
            '        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)\n'
            '        raise SystemExit(1)\n'
            '    print("SETUP OK")\n\n\n'
            'def main():\n'
            '    publish(build_state())\n\n\n'
            'main()\n'
            % (tid, inj["project_path"], BASE_STATE_JSON, OVERLAY_TUPLES,
               inj["project_id"], inj["next_member"],
               json.dumps(rows, indent=2)))


def main():
    os.makedirs(REPLAYS, exist_ok=True)
    index = []
    nemo_lines = []

    for task in TASKS:
        tid = "template_project_staffed_%03d" % task["n"]
        bundle = os.path.join(OUT, tid)
        os.makedirs(bundle, exist_ok=True)
        tmpl_name, blurb = TEMPLATES[task["tmpl"]]
        expected = sorted((uid, ROLE[role]) for (_u, uid, role) in task["members"])
        full_path = "byteblaze/" + task["slug"]

        if task["members"]:
            skills = (["R8", "R7", "A2", "A3", "A12"] if "inject" in task
                      else ["R8", "A2", "A3", "A12"])
            difficulty = "hard"
            hard_criteria = ["derived_target", "multi_mutation", "cross_section"]
        else:
            skills = ["R8", "A2"]
            difficulty = "medium"
            hard_criteria = None

        if "inject" in task:
            chain = ("read the described stack -> pick that row in the built-in template "
                     "gallery -> create the private project under byteblaze -> read the "
                     "roster of a named sibling project -> grant each of those users the "
                     "same role on the project just created")
        elif task["members"]:
            chain = ("read the described stack -> pick that row in the built-in template "
                     "gallery -> create the private project under byteblaze -> open the "
                     "new project's Members page and grant the named users their roles")
        else:
            chain = ("read the described stack -> pick the matching row in the built-in "
                     "template gallery -> create the private project under byteblaze from it")

        criteria = [
            "newProjects holds a project with full_path '%s', name '%s' and visibility "
            "'private'." % (full_path, task["slug"]),
            "That project's description is the '%s' template blurb and "
            "repo.commitOverlay['%s:main'] carries the commit \"Initialized from '%s' "
            "project template\"." % (tmpl_name, full_path, tmpl_name),
        ]
        if task["members"]:
            listed = ", ".join("%s at %s" % (u, r) for (u, _i, r) in task["members"])
            criteria.append(
                "The members of that project, byteblaze's owner row aside, are exactly: %s."
                % listed)

        instruction_doc = {
            "task_id": tid,
            "task_instruction": task["instruction"],
            "app_dir": "webarena_gitlab_mock",
            "start_path": "/",
            "difficulty": difficulty,
            "success_criteria": criteria,
        }

        notes = [
            "Grounded in hub/websites/webarena_gitlab_mock as served (dist/, built 2026-08-17).",
            "Template match: %s" % task["match"],
            "createProject (src/components/create/mutations.js:272) writes the project into "
            "newProjects with description = templatePayload().description = the template "
            "blurb, and commitToRepo writes \"Initialized from '%s' project template\" into "
            "repo.commitOverlay['%s:main']. The blank-project pane renders no description "
            "field (NewProject.jsx fields({withDescription:false})), so the blurb cannot be "
            "typed in by an agent that skipped the gallery." % (tmpl_name, full_path),
            "Click path from '/': navbar '+' (data-qa-selector=new_menu_toggle) -> "
            "'New project/repository' -> 'Create from template' card -> 'Use template' on the "
            "matching row -> fill Project name, tick Private, 'Create project'.",
        ]
        if task["members"]:
            notes.append(
                "addMembers (mutations.js:363) appends one newMembers row per invitee; the "
                "invite modal is reached from the created project's page via Project "
                "information -> Members (sidebar sub-items need the parent clicked first) or "
                "via the navbar '+' -> 'Invite members'. The role <select> defaults to Guest.")
            notes.append(
                "byteblaze's own Owner row is also written into newMembers by createProject; "
                "the rubric excludes user 2330 and asserts the remaining grant set exactly, "
                "so an over-invite scores 0 on that component.")
        if "inject" in task:
            notes.append(
                "byteblaze's dashboard lists 14 projects on a single page (PER_PAGE=20), so "
                "the source project is reachable from '/' without paging. The 175-row "
                "pagination trap applies to /explore/projects, not /dashboard/projects.")

        metadata = {
            "style": task["style"],
            "difficulty": difficulty,
            "shape": "retrieval_writeback",
            "skills": skills,
            "skill_chain": chain,
            "official_analogues": [OFFICIAL[i] for i in task["analogues"]],
            "topic": "gitlab template project creation and staffing",
            "inspiration_ids": task["inspiration"],
            "authoring_notes": notes,
        }
        if hard_criteria:
            metadata["hard_criteria"] = hard_criteria
        if "inject" in task:
            inj = task["inject"]
            metadata["injected_preconditions"] = [
                "newMembers: %d collaborator rows on %s (project id %d) at %s - the seeded "
                "project has byteblaze as its only member, so the 'staff it like that one' "
                "retrieval has nothing to read on the pristine seed."
                % (len(inj["rows"]), inj["project_path"], inj["project_id"],
                   ", ".join("%s" % lbl for (_i, _u, _l, lbl, _c) in inj["rows"])),
                "nextIds.member raised to %d so the injected ids cannot collide with rows the "
                "agent creates (mutations.js addMembers takes ids off nextIds.member)."
                % inj["next_member"],
            ]

        manifest = {
            "schema_version": 2,
            "task_id": tid,
            "instruction": task["instruction"],
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

        reward = reward_source(task, tid, tmpl_name, blurb, expected)
        nemo_reward = nemo_reward_source(task, tid, tmpl_name, blurb, expected)
        setup = setup_source(task, tid) if "inject" in task else None

        with open(os.path.join(bundle, "task_instruction.json"), "w", encoding="utf-8") as fh:
            json.dump(instruction_doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(bundle, "task.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(os.path.join(bundle, "reward.py"), "w", encoding="utf-8") as fh:
            fh.write(reward)
        with open(os.path.join(bundle, "nemo_reward.py"), "w", encoding="utf-8") as fh:
            fh.write(nemo_reward)
        if setup is not None:
            with open(os.path.join(bundle, "initial_setup.py"), "w", encoding="utf-8") as fh:
                fh.write(setup)
        else:
            stale = os.path.join(bundle, "initial_setup.py")
            if os.path.exists(stale):
                os.remove(stale)

        row = {"task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {"eval_types": ["string_match"], "reference_answers": None,
                     "note": "unused - CUA-Gym reward code is authoritative"},
            "cuagym": {"bundle_id": tid, "app_dir": "webarena_gitlab_mock",
                       "initial_setup": setup, "eval_reward_code": nemo_reward},
        }}
        with open(os.path.join(bundle, "nemo_task.json"), "w", encoding="utf-8") as fh:
            json.dump(row, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        nemo_lines.append(json.dumps(row, ensure_ascii=False))
        index.append({"task_id": tid, "path": "../../%s/task.json" % tid})

        write_replay(task, tid, tmpl_name)

    with open(os.path.join(BATCH, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"schema_version": 2, "tasks": index}, fh, indent=2)
        fh.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(nemo_lines) + "\n")
    print("wrote %d bundles" % len(TASKS))


REPLAY_HEAD = '''# -*- coding: utf-8 -*-
"""Golden replay DRAFT for %s.

Click-only: after the single landing goto on start_path '/', every step is a
click or a form fill on a rendered control. No page.goto(), no constructed URL.
Not executed during authoring - the verification phase drives and repairs it.
"""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001"


def open_new_project(page):
    """Navbar '+' -> New project/repository -> Create from template pane."""
    page.click("[data-qa-selector='new_menu_toggle']")
    page.click("[data-qa-selector='global_new_project_link']")
    page.wait_for_selector(".new-namespace-panel-grid")
    page.click("a[href='#create_from_template']")
    page.wait_for_selector("#built-in")


def use_template(page, key):
    page.click("[data-testid='use_template_%%s']" %% key)
    page.wait_for_selector("#project_name")


def fill_and_create(page, name):
    page.fill("#project_name", name)
    page.check("#project_visibility_level_0")          # Private
    page.click("[data-qa-selector='project_create_button']")
    page.wait_for_selector(".project-home-panel, .home-panel-description-markdown")


def open_members(page):
    """Sidebar: Project information must be clicked before its children render."""
    page.click("a[href$='/activity']")
    page.wait_for_load_state("networkidle")
    page.click("#js-onboarding-members-link")
    page.wait_for_selector("[data-qa-selector='invite_members_button']")


def invite(page, usernames, level):
    page.click("[data-qa-selector='invite_members_button']")
    page.wait_for_selector("#invite-members-search")
    for username in usernames:
        page.fill("#invite-members-search", username)
        page.wait_for_selector(".dropdown-menu.show .dropdown-item")
        page.click(".dropdown-menu.show li button.dropdown-item")
    page.select_option("#invite-members-role", str(level))
    page.click("[data-qa-selector='invite_button']")
    page.wait_for_timeout(800)


def replay(page, sid):
    page.goto(BASE + "/?sid=" + sid, wait_until="networkidle")
'''

REPLAY_TAIL = '''

def main(sid):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        replay(page, sid)
        browser.close()


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
'''


def write_replay(task, tid, tmpl_name):
    body = REPLAY_HEAD % tid
    if "inject" in task:
        inj = task["inject"]
        body += ('    # Read the roster to copy: dashboard row -> project -> Members.\n'
                 '    page.click("a[href=\'/%s\']")\n'
                 '    page.wait_for_load_state("networkidle")\n'
                 '    open_members(page)\n'
                 '    roster = page.inner_text("table.members-table, table.gl-table")\n'
                 '    for handle in %r:\n'
                 '        assert handle in roster, handle\n'
                 % (inj["project_path"], [u for (u, _i, _r) in task["members"]]))
    body += ('    open_new_project(page)\n'
             '    use_template(page, "%s")   # %s\n'
             '    fill_and_create(page, "%s")\n' % (task["tmpl"], tmpl_name, task["slug"]))
    if task["members"]:
        by_role = {}
        for (username, _uid, role) in task["members"]:
            by_role.setdefault(role, []).append(username)
        body += '    open_members(page)\n'
        for role, names in by_role.items():
            body += '    invite(page, %r, %d)   # %s\n' % (names, ROLE[role], role)
    body += REPLAY_TAIL
    with open(os.path.join(REPLAYS, tid + ".py"), "w", encoding="utf-8") as fh:
        fh.write(body)


main()
