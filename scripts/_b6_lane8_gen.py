#!/usr/bin/env python3
"""Authoring generator for batch-6 gitlab lane 8 (top_starred_bulk_star).

Writes ten bundles under output/tasks/gitlab/. Reads the mock seed to build the
projectEdits injections; performs no validation of the emitted bundles.
"""
import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SEED = os.path.join(ROOT, "hub/websites/webarena_gitlab_mock/src/data/projects.json")
OUT = os.path.join(ROOT, "output/tasks/gitlab")
BATCH = os.path.join(OUT, "_batches/top_starred_bulk_star")

PROJECTS = {p["id"]: p for p in json.load(open(SEED))}

# ---------------------------------------------------------------------------
# Lane plan. `edits` = injected star_count per project id (full record written
# back through projectEdits). `targets` = the project ids the task must star.
# `rank_note` documents the resulting Explore > Most stars head and margins.
# ---------------------------------------------------------------------------
TASKS = [
    {
        "n": "001",
        "slug": "top_starred_bulk_star_keycloak_surge_001",
        "style": "terse",
        "edits": {143: 68, 72: 64, 135: 60},
        "targets": [143, 72, 135],
        "kind": "prefix",
        "instruction": (
            "GitLab's Explore listing can rank every public project by stars. "
            "Star the three projects sitting at the very top of that ranking."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_001",
        "ranking": "keycloak/keycloak 68, capnproto/capnproto 64, wireservice/csvkit 60, then umano/AndroidSlidingUpPanel 55",
        "margins": "68>64 (4), 64>60 (4), top-3 boundary 60>55 (5)",
    },
    {
        "n": "002",
        "slug": "top_starred_bulk_star_pyod_mathjax_002",
        "style": "terse",
        "edits": {139: 63, 65: 59},
        "targets": [139, 65],
        "kind": "prefix",
        "instruction": (
            "I want to follow this instance's two biggest repositories. "
            "Star the two public projects that carry the highest star counts on GitLab."
        ),
        "analogues": ["Star the top one most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_002",
        "ranking": "yzhao062/pyod 63, mathjax/MathJax 59, then umano/AndroidSlidingUpPanel 55",
        "margins": "63>59 (4), top-2 boundary 59>55 (4)",
    },
    {
        "n": "003",
        "slug": "top_starred_bulk_star_runners_up_bull_003",
        "style": "explicit",
        "edits": {75: 70, 111: 64, 132: 60},
        "targets": [111, 132],
        "kind": "window",
        "instruction": (
            "The Explore section of GitLab can list public projects ordered by how many stars "
            "they have. I already know about the single most-starred project and I do not want "
            "that one on my list. Star the two projects that come immediately after it in that "
            "ranking - second place and third place - and leave the leader unstarred."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_003",
        "ranking": "OptimalBits/bull 70 (leader, excluded), Arachni/arachni 64, youfou/wxpy 60, then umano/AndroidSlidingUpPanel 55",
        "margins": "leader 70>64 (6), 64>60 (4), window boundary 60>55 (5)",
    },
    {
        "n": "004",
        "slug": "top_starred_bulk_star_primer_trio_004",
        "style": "terse",
        "edits": {129: 66, 172: 62, 73: 58},
        "targets": [129, 172, 73],
        "kind": "prefix",
        "instruction": (
            "I want this instance's three biggest repositories on my starred list. "
            "Work out which public projects hold the highest star counts and star each of them."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_004",
        "ranking": "donnemartin/system-design-primer 66, firstcontributions/first-contributions 62, zhongyang219/TrafficMonitor 58, then umano/AndroidSlidingUpPanel 55",
        "margins": "66>62 (4), 62>58 (4), top-3 boundary 58>55 (3)",
    },
    {
        "n": "005",
        "slug": "top_starred_bulk_star_window_wechat_005",
        "style": "explicit",
        "edits": {123: 72, 116: 68, 60: 64, 80: 60},
        "targets": [116, 60, 80],
        "kind": "window",
        "instruction": (
            "Under Explore, GitLab can rank public projects by star count. The project sitting at "
            "the very top of that ranking is already on my radar, so skip it. Star the next three "
            "projects below it instead - the ones in second, third and fourth place - and do not "
            "star the leader itself."
        ),
        "analogues": ["Star the top four most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_005",
        "ranking": "geeeeeeeeek/electronic-wechat 72 (leader, excluded), verekia/js-stack-from-scratch 68, facebook/buck 64, pwxcoo/chinese-xinhua 60, then umano/AndroidSlidingUpPanel 55",
        "margins": "leader 72>68 (4), 68>64 (4), 64>60 (4), window boundary 60>55 (5)",
    },
    {
        "n": "006",
        "slug": "top_starred_bulk_star_autojump_pair_006",
        "style": "terse",
        "edits": {134: 65, 119: 61},
        "targets": [134, 119],
        "kind": "prefix",
        "instruction": (
            "Star the top two public projects in GitLab's star ranking - the leader and the "
            "runner-up. Nothing further down the list."
        ),
        "analogues": ["Star the top one most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_006",
        "ranking": "wting/autojump 65, http-party/node-http-proxy 61, then umano/AndroidSlidingUpPanel 55",
        "margins": "65>61 (4), top-2 boundary 61>55 (6)",
    },
    {
        "n": "007",
        "slug": "top_starred_bulk_star_pyav_trio_007",
        "style": "terse",
        "edits": {81: 69, 136: 65, 58: 61},
        "targets": [81, 136, 58],
        "kind": "prefix",
        "instruction": (
            "Star the podium of this GitLab instance: the three public projects with the most "
            "stars. Nothing below third place."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_007",
        "ranking": "harvitronix/five-video-classification-methods 69, PyAV-Org/PyAV 65, OpenAPITools/openapi-generator 61, then umano/AndroidSlidingUpPanel 55",
        "margins": "69>65 (4), 65>61 (4), top-3 boundary 61>55 (6)",
    },
    {
        "n": "008",
        "slug": "top_starred_bulk_star_runners_up_covid_008",
        "style": "explicit",
        "edits": {121: 71, 66: 66, 104: 62},
        "targets": [66, 104],
        "kind": "window",
        "instruction": (
            "GitLab's Explore area can sort public projects by star count. Whichever project holds "
            "first place there is not for me - skip it. Star the second- and third-most-starred "
            "public projects instead, and leave the top one alone."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_008",
        "ranking": "covid19india/covid19india-react 71 (leader, excluded), kahun/awesome-sysadmin 66, BoltsFramework/Bolts-ObjC 62, then umano/AndroidSlidingUpPanel 55",
        "margins": "leader 71>66 (5), 66>62 (4), window boundary 62>55 (7)",
    },
    {
        "n": "009",
        "slug": "top_starred_bulk_star_administrate_trio_009",
        "style": "terse",
        "edits": {113: 67, 145: 63, 86: 59},
        "targets": [113, 145, 86],
        "kind": "prefix",
        "instruction": (
            "Three public repositories lead this GitLab instance on stars. "
            "Add all three of them to my starred projects."
        ),
        "analogues": ["Star the top three most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_009",
        "ranking": "thoughtbot/administrate 67, koush/AndroidAsync 63, eriklindernoren/PyTorch-GAN 59, then umano/AndroidSlidingUpPanel 55",
        "margins": "67>63 (4), 63>59 (4), top-3 boundary 59>55 (4)",
    },
    {
        "n": "010",
        "slug": "top_starred_bulk_star_xlsxwriter_pair_010",
        "style": "terse",
        "edits": {99: 64, 122: 60},
        "targets": [99, 122],
        "kind": "prefix",
        "instruction": (
            "Add the two most-starred public projects on this GitLab to my starred list. "
            "Only those two."
        ),
        "analogues": ["Star the top one most stared repos in Gitlab"],
        "derived_from": "star_top3_record_bio_010",
        "ranking": "mk-j/PHP_XLSXWriter 64, facebook/create-react-app 60, then umano/AndroidSlidingUpPanel 55",
        "margins": "64>60 (4), top-2 boundary 60>55 (5)",
    },
]

SEED_STARRED = [174, 183, 185]

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


def project_edits(edits):
    out = {}
    for pid, count in sorted(edits.items()):
        rec = dict(PROJECTS[pid])
        rec["star_count"] = count
        out[str(pid)] = rec
    return out


def setup_source(task):
    edits = project_edits(task["edits"])
    doc = (
        '"""NeMo-Gym setup program for %s.\n\n'
        'Sets the star ranking this task derives its target set from.\n'
        'Explore > Most stars (sort=stars_desc, pages at 20) then reads:\n'
        '  %s.\n'
        'Margins: %s.\n\n'
        'Mechanism: pages/hooks.js:357 sortProjects ranks "stars_desc" on\n'
        'p.star_count, so the ranking can only be moved through projectEdits.<id>;\n'
        'the injected value is a COMPLETE project record with one field changed,\n'
        'which is exactly what overlayShape.js stores for an edited frozen row.\n\n'
        'Nothing about byteblaze\'s own stars is touched - the seeded star rows\n'
        '(projects 174, 183, 185) stand, none of them is a target here, and no\n'
        'target project is starred at t=0, so the rubric is not pre-satisfied.\n\n'
        'Self-contained: standard library plus requests (in cuagym/requirements.txt).\n"""\n'
    ) % (task["slug"], task["ranking"], task["margins"])
    body = (
        "import json\n"
        "import sys\n\n"
        "import requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n\n'
        'BASE_STATE = json.loads(r"""%s""")\n\n' % BASE_STATE_JSON
        + OVERLAY_BLOCK
        + '\n# projectEdits: "<project id>" -> the full frozen project record with an\n'
        "# adjusted star_count. Every other field is byte-identical to\n"
        "# src/data/projects.json, so nothing else on the project page changes.\n"
        'INJECTED_PROJECT_EDITS = json.loads(r"""%s""")\n\n\n'
        % json.dumps(edits, indent=2, sort_keys=True)
        + "def build_state():\n"
        '    """Full createInitialData() shape, so the client-side merge is a no-op."""\n'
        "    state = dict(BASE_STATE)\n"
        "    for created, edits_key, deleted in OVERLAY_COLLECTIONS:\n"
        "        state[created] = []\n"
        "        state[edits_key] = {}\n"
        "        state[deleted] = []\n"
        '    state["projectEdits"] = INJECTED_PROJECT_EDITS\n'
        "    return state\n\n\n"
        "def publish(state):\n"
        '    response = requests.post(BASE_URL + "/post?sid=" + SID,\n'
        '                             json={"action": "set", "state": state}, timeout=30)\n'
        "    response.raise_for_status()\n"
        '    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)\n'
        "    check.raise_for_status()\n"
        "    payload = check.json()\n"
        '    if payload.get("state_diff") != {}:\n'
        '        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)\n'
        "        raise SystemExit(1)\n"
        '    if payload.get("initial_state") != payload.get("current_state"):\n'
        '        print("SETUP FAILED: initial_state != current_state after set", file=sys.stderr)\n'
        "        raise SystemExit(1)\n"
        '    print("SETUP OK")\n\n\n'
        "def main():\n"
        "    publish(build_state())\n\n\n"
        "main()\n"
    )
    return doc + body


RUBRIC_BODY = '''

COMPONENT_WEIGHTS = {
    "%(component)s": 1.0,
}
assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9

USER_ID = 2330
# byteblaze's three seeded star rows (src/data/stars.json): projects 174, 183, 185.
SEED_STARRED = json.loads(r"""%(seed)s""")
# [project_id, "<namespace>/<project>"] for every project the ranking selects.
TARGETS = json.loads(r"""%(targets)s""")
COMPONENT = "%(component)s"


def score_state(state):
    owned = _star_set(state)
    required = set(int(pid) for pid in SEED_STARRED)
    for row in TARGETS:
        required.add(int(row[0]))
    ok = owned == required
    detail = (
        "byteblaze's starred project ids are now %%r; this task requires exactly %%r "
        "(the three seeded stars plus %%s)" %% (
            sorted(owned), sorted(required),
            ", ".join("%%s (id %%d)" %% (row[1], int(row[0])) for row in TARGETS)))
    return _build({COMPONENT: ok}, {COMPONENT: detail})


# --------------------------------------------------------------------------
# Readers over webarena_gitlab_mock's persisted overlay state, current_state
# only. A star click (pages/ProjectOverview.jsx:262 toggleStar, button :322)
# appends {project_id, user_id, created_at} to state.stars, which the overlay
# records as `newStars`; an unstar of a frozen row lands in `deletedStars` as
# "<project_id>:<user_id>" (overlayShape.js recordKey).
# --------------------------------------------------------------------------


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _star_set(state):
    owned = set(int(pid) for pid in SEED_STARRED)
    for key in _list(_dict(state).get("deletedStars")):
        parts = str(key).split(":")
        if len(parts) == 2 and parts[1] == str(USER_ID):
            try:
                owned.discard(int(parts[0]))
            except ValueError:
                continue
    for rec in _list(_dict(state).get("newStars")):
        if not isinstance(rec, dict):
            continue
        if str(rec.get("user_id")) != str(USER_ID):
            continue
        try:
            owned.add(int(rec.get("project_id")))
        except (TypeError, ValueError):
            continue
    return owned


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


def component_name(task):
    return "starred_projects_now_exactly_seed_plus_top_%d_ranked" % len(task["targets"])


def rubric(task):
    targets = [[pid, PROJECTS[pid]["full_path"]] for pid in task["targets"]]
    return RUBRIC_BODY % {
        "component": component_name(task),
        "seed": json.dumps(SEED_STARRED),
        "targets": json.dumps(targets),
    }


def reward_source(task):
    head = (
        '"""Deterministic reward for %s.\n\n'
        "The Explore > Most stars ranking this bundle's initial_setup.py installs:\n"
        "  %s.\n"
        "Margins: %s.\n"
        "Star clicks add +1 to each selected project, which moves no boundary.\n\n"
        "One all-or-nothing component: the star rows byteblaze owns at the end must\n"
        "be exactly the three seeded ones plus the ranked target set. Starring one\n"
        "project too many or too few scores 0.0. current_state only.\n"
        '"""\n'
        "import json\n"
    ) % (task["slug"], task["ranking"], task["margins"])
    tail = '''

def _current_state(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    for key in ("gitlab", "webarena_gitlab_mock"):
        if key in apps:
            return _dict(_dict(apps[key]).get("current_state"))
    for value in apps.values():
        state = _dict(_dict(value).get("current_state"))
        if state:
            return state
    return {}


def evaluate(evidence):
    components = score_state(_current_state(evidence))
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''
    return head + rubric(task) + tail


def nemo_reward_source(task):
    head = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Same rubric as reward.py, read from GET /go?sid=... instead of a frozen\n"
        "evidence bundle. Prints REWARD: <float> on every output path.\n\n"
        "Self-contained: standard library plus requests (in cuagym/requirements.txt).\n"
        '"""\n'
        "import json\n"
        "import sys\n\n"
        "import requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n'
    ) % task["slug"]
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
    total = round(sum(c["score"] for c in components), 6)
    print("REWARD: %.6f" % _clamp(float(total)))


main()
'''
    return head + rubric(task) + tail


def criteria(task):
    out = []
    for pid in task["targets"]:
        out.append("byteblaze now stars project %d (%s)." % (pid, PROJECTS[pid]["full_path"]))
    required = sorted(set(SEED_STARRED) | set(task["targets"]))
    out.append("byteblaze's starred project set is now exactly %s." % (required,))
    if task["kind"] == "window":
        leader = max(task["edits"].items(), key=lambda kv: kv[1])[0]
        out.append(
            "The top-ranked project %s (id %d) is NOT starred by byteblaze."
            % (PROJECTS[leader]["full_path"], leader))
    return out


def notes(task):
    leader = max(task["edits"].items(), key=lambda kv: kv[1])[0]
    base = [
        "Grounded in the served webarena_gitlab_mock build; every id, full_path and star_count "
        "was read from src/data/projects.json and src/data/stars.json.",
        "Ranking after this bundle's injection: %s. Margins: %s." % (task["ranking"], task["margins"]),
        "Star control: pages/ProjectOverview.jsx:322 button -> toggleStar() :262, which appends "
        "{project_id, user_id, created_at} to state.stars and increments projects[].star_count; "
        "/go records that as newStars plus projectEdits.<id>. The reward reads the star join rows "
        "only, so the injected projectEdits entries never pre-satisfy it.",
        "Ranking source: pages/hooks.js:357 sortProjects orders 'stars_desc' on p.star_count, NOT "
        "on the stars array, so newStars alone would move nothing and projectEdits.<id> is the only "
        "injection channel that does. ProjectOverview.jsx:192 reads the same field, so the project "
        "page and Explore agree.",
        "Scope: pages/ExploreProjects.jsx:44 drops visibility === 'private'; the Most stars tab "
        "additionally drops star_count === 0; ProjectsNav.jsx:170 filterArchived hides archived rows "
        "by default. Every injected project is public, unarchived and already had stars, so 'on "
        "GitLab' in the instruction means exactly the list the Explore ranking shows.",
        "Action-vs-premise check: each star click adds +1 to a selected project's star_count. "
        "Re-deriving the ranking after every click leaves both the membership and the order of the "
        "selected window unchanged (see the margins above), so the instruction never has to name a "
        "project and the retrieval skill survives the action.",
        "byteblaze (user 2330) starts with exactly three star rows - projects 174, 183 and 185 - and "
        "none of them is a target or the injected leader, so no target's button reads 'Unstar' at "
        "t=0 and the required end set is a strict superset of the seed.",
        "start_path '/': the root renders DashboardProjects with the primary tab strip "
        "(ProjectsNav.jsx:95) whose Explore tab reaches /explore; the secondary strip there "
        "(ExploreProjects.jsx:72) reaches /explore/projects/starred, which sorts stars_desc by "
        "default and pages at 20. Project rows link to /<full_path> "
        "(DashboardProjects.jsx:46). Every scored control is click-reachable.",
        "Rubric is all-or-nothing on the exact resulting star set, so an agent that mis-reads the "
        "rank boundary - one project too many or too few - scores exactly 0.0 rather than partial "
        "credit.",
    ]
    if task["kind"] == "window":
        base.append(
            "This is an ordinal WINDOW, not a prefix: the leader %s (id %d, %d stars) is excluded, "
            "so an agent that stars the top of the list fails the exact-set component."
            % (PROJECTS[leader]["full_path"], leader, task["edits"][leader]))
    return base


def injected(task):
    rows = []
    for pid, count in sorted(task["edits"].items(), key=lambda kv: -kv[1]):
        rows.append(
            "projectEdits['%d'] = the full src/data/projects.json record for %s with star_count "
            "raised from %d to %d." % (pid, PROJECTS[pid]["full_path"],
                                       PROJECTS[pid]["star_count"], count))
    rows.append(
        "Purpose: the pristine Most-stars head has a top-2 boundary margin of 1 (52 vs 51) and "
        "ties at 42 and 39 further down, and its top-3 is already the answer to a batch-5 task. "
        "The injection installs a different, tie-free head with every boundary margin >= 3.")
    rows.append(
        "Nothing in the rubric is pre-satisfied: the injection touches projectEdits only, and the "
        "reward reads byteblaze's star join rows (newStars / deletedStars over the seeded "
        "174/183/185), which the injection leaves untouched.")
    return rows


def replay_source(task):
    order = sorted(task["edits"].items(), key=lambda kv: -kv[1])
    ranked = [pid for pid, _ in order]
    lines = []
    lines.append('"""Golden replay draft for %s.' % task["slug"])
    lines.append("")
    lines.append("Click-only after the landing page: primary tab Explore -> secondary tab")
    lines.append("Most stars -> the ranked project row -> the Star button, repeated per target.")
    lines.append("page.go_back() only ever returns to /explore/projects/starred, which was")
    lines.append("reached by clicking.")
    lines.append("")
    lines.append("Ranking installed by initial_setup.py: %s." % task["ranking"])
    lines.append('"""')
    lines.append("TARGETS = [")
    for pid in task["targets"]:
        lines.append('    ("%s", %d),  # rank %d'
                     % (PROJECTS[pid]["name"], pid, ranked.index(pid) + 1))
    lines.append("]")
    lines.append("")
    lines.append("")
    lines.append("def run(page, base_url, sid):")
    lines.append('    page.goto("%s/?sid=%s" % (base_url.rstrip("/"), sid))')
    lines.append('    page.wait_for_selector(".project-row")')
    lines.append("")
    lines.append("    # 1. front door -> Explore -> Most stars (sort=stars_desc by default)")
    lines.append('    page.click(\'a[href="/explore"]\')')
    lines.append('    page.wait_for_selector(".project-row")')
    lines.append('    page.click(\'a[href="/explore/projects/starred"]\')')
    lines.append('    page.wait_for_selector(".project-row")')
    lines.append("")
    lines.append("    # 2. star each ranked target, returning to the ranking between visits")
    lines.append("    for name, pid in TARGETS:")
    lines.append('        page.click(\'.project-row a.text-plain:has(.project-name:text-is("%s"))\' % name)')
    lines.append('        page.wait_for_selector(".project-repo-buttons")')
    lines.append('        page.click(\'.project-repo-buttons button:has-text("Star")\')')
    lines.append('        page.wait_for_selector(\'.project-repo-buttons button:has-text("Unstar")\')')
    lines.append("        page.go_back()")
    lines.append('        page.wait_for_selector(".project-row")')
    lines.append("")
    lines.append("")
    lines.append("# End state: byteblaze's stars == %s"
                 % sorted(set(SEED_STARRED) | set(task["targets"])))
    return "\n".join(lines) + "\n"


def main():
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = []
    nemo_rows = []
    for task in TASKS:
        slug = task["slug"]
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)

        setup = setup_source(task)
        reward = reward_source(task)
        nemo_reward = nemo_reward_source(task)

        ti = {
            "task_id": slug,
            "task_instruction": task["instruction"],
            "app_dir": "webarena_gitlab_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": criteria(task),
        }
        manifest = {
            "schema_version": 2,
            "task_id": slug,
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
            "metadata": {
                "style": task["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R4", "A4"],
                "skill_chain": (
                    "order the public project list by stars and take the stated ordinal window -> "
                    "star every project in that window"),
                "derived_from": task["derived_from"],
                "official_analogues": task["analogues"],
                "topic": "gitlab star ranking, bulk star over a ranked set",
                "batch": "batch6-gitlab-lane8-top_starred_bulk_star",
                "inspiration_ids": ["webarena-523", "webarena-525", "webarena-526", "webarena-527"],
                "injected_preconditions": injected(task),
                "authoring_notes": notes(task),
            },
        }

        open(os.path.join(d, "task_instruction.json"), "w").write(json.dumps(ti, indent=2) + "\n")
        open(os.path.join(d, "task.json"), "w").write(json.dumps(manifest, indent=2) + "\n")
        open(os.path.join(d, "reward.py"), "w").write(reward)
        open(os.path.join(d, "nemo_reward.py"), "w").write(nemo_reward)
        open(os.path.join(d, "initial_setup.py"), "w").write(setup)

        row = {"task_payload": {
            "task_id": slug,
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
                "bundle_id": slug,
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup,
                "eval_reward_code": nemo_reward,
            },
        }}
        open(os.path.join(d, "nemo_task.json"), "w").write(json.dumps(row, indent=2) + "\n")
        nemo_rows.append(row)
        index.append({"task_id": slug, "path": "%s/task.json" % slug})

        open(os.path.join(BATCH, "replays", slug + ".py"), "w").write(replay_source(task))

    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in nemo_rows:
            fh.write(json.dumps(row) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        fh.write(json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
