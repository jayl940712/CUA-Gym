#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 9 — gitlab `contributor_honour_roll`.

Writes 10 bundles under output/tasks/gitlab/<task_id>/ plus the batch files.
Authoring only; runs no validation.
"""
import json
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output/tasks/gitlab"
BATCH = OUT / "_batches/contributor_honour_roll"
REPLAYS = BATCH / "replays"

ANALOGUE_317 = ("List the name and number of commits of the top 3 contributors to metaseq "
                "repo, ranked by the number of commits?")
ANALOGUE_314 = "Get the full names of the top 3 contributors (by commit count) to primer/design repo"
ANALOGUE_318 = "Get the last names of the top 3 contributors (by commit count) to 2019-nCov repo"
ANALOGUE_791 = ("Make a folder named car on the gimmiethat.space repo and include a file called "
                "urls.txt that consists of the links to the 5 most recent posts from the cars forum.")
ANALOGUE_563 = ("Create a private repository named fun_thing_to_do with a README file containing "
                "links to the 5 most active DIY posts from the DIY forum. Use the Web IDE to create "
                "the README. Structure it with the repository name as the main heading, \"Most Active "
                "DIY Threads\" as a subheading, and a bulleted list of the posts as markdown links "
                "(using their titles as link text) in the same order they appear on the forum. Commit "
                "to the default branch.")

# ---------------------------------------------------------------------------
# Shared code bodies
# ---------------------------------------------------------------------------

CORE = '''

def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _repo(state, bucket):
    return _dict(_dict(_dict(state).get("repo")).get(bucket))


def _body(state):
    """The committed body recorded under the file overlay key, or ""."""
    value = _repo(state, "fileOverlay").get(FILE_KEY)
    return value if isinstance(value, str) else ""


def _flat(text):
    """One normalised lower-case line per source line: CRLF folded, whitespace
    collapsed, digit grouping commas removed so 1,044 and 1044 compare equal."""
    folded = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    out = []
    for line in folded.split("\\n"):
        stripped = re.sub(r"(?<=\\d),(?=\\d\\d\\d)", "", line)
        out.append(re.sub(r"\\s+", " ", stripped).strip().lower())
    return out


def _needle(text):
    return re.escape(re.sub(r"\\s+", " ", str(text)).strip().lower())


def _row_index(lines, name, count):
    """Index of the first line naming `name` (and carrying `count`, if given)."""
    name_pat = _needle(name)
    for i, line in enumerate(lines):
        if not re.search(name_pat, line):
            continue
        if count is None:
            return i
        if re.search(r"(?<!\\d)" + str(count) + r"(?!\\d)", line):
            return i
    return -1


def _row_indexes(lines):
    return [_row_index(lines, entry[0], entry[1]) for entry in TOP_THREE]


def _branch_names(state, full_path):
    rows = _list(_repo(state, "branchOverlay").get(full_path))
    return sorted(str(row.get("name")) for row in rows if isinstance(row, dict))


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

EVAL_TAIL = '''

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

REWARD_DOC = '''"""Deterministic reward for {task_id}.

The contributors graph is the only surface in this mock that carries correct
per-author commit counts: src/pages/Contributors.jsx:132 sorts the frozen
per-project rows by commits descending and :158 renders "{{n}} commits ({{email}})".
/-/commits/:ref and /-/graphs/:ref/charts both read the 40-row-capped
commits.json and would give a different, wrong number.

The writeback lands in repo.fileOverlay["<full_path>:<ref>:<path>"] via
src/pages/NewFile.jsx:46 (or EditFile.jsx:49) -> src/components/create/mutations.js:229
commitToRepo -> :155 writeFiles. This reward reads that recorded body out of the
current state and checks the transferred names, the transferred numbers, and the
order they were written in. Nothing is diffed against a baseline and no
implementation trace is inspected.
"""
'''

NEMO_DOC = '''"""NeMo-Gym reward program for {task_id}.

Same rubric as reward.py, read from GET /go?sid=... instead of a frozen evidence
bundle. Prints REWARD: <float> on every output path.

Self-contained: standard library plus `requests`.
"""
'''

SETUP_HEAD = '''"""NeMo-Gym setup program for {task_id}.

{purpose}

Self-contained: standard library plus `requests`.
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
              "label": 1927, "milestone": 590, "member": 206}}
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


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {{}}
        state[deleted] = []
    return state


def publish(state):
    response = requests.post(BASE_URL + "/post?sid=" + SID,
                             json={{"action": "set", "state": state}}, timeout=30)
    response.raise_for_status()
    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=30)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {{}}:
        print("SETUP FAILED: state diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("current_state") != payload.get("initial_state"):
        print("SETUP FAILED: baseline and current disagree after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


REPO_OVERLAY = json.loads(r"""{overlay}""")


def main():
    state = build_state()
    state["repo"].update(REPO_OVERLAY)
    publish(state)


main()
'''


def py_literal(value, indent=0):
    """A Python literal for the constants block (never JS true/false/null)."""
    pad = " " * indent
    if value is None:
        return "None"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        inner = ", ".join(py_literal(v) for v in value)
        return "[" + inner + "]"
    raise TypeError(type(value))


def constants_block(task):
    lines = ["", "COMPONENT_WEIGHTS = {"]
    for name, weight in task["weights"].items():
        lines.append('    "%s": %s,' % (name, weight))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    lines.append("")
    lines.append("FILE_KEY = %s" % py_literal(task["file_key"]))
    lines.append("TOP_THREE = [")
    for name, count in task["top_three"]:
        lines.append("    [%s, %s]," % (py_literal(name), py_literal(count)))
    lines.append("]")
    lines.append("NEXT_CONTRIBUTOR = %s" % py_literal(task["fourth"]))
    if task.get("combined_total") is not None:
        lines.append("COMBINED_TOTAL = %s" % py_literal(task["combined_total"]))
    if task.get("branch") is not None:
        lines.append("BRANCH_OWNER = %s" % py_literal(task["branch_owner"]))
        lines.append("BRANCH_NAME = %s" % py_literal(task["branch"]))
    if task.get("stale_names"):
        lines.append("STALE_NAMES = %s" % py_literal(task["stale_names"]))
    lines.append("")
    return "\n".join(lines) + "\n"


def score_block(task):
    """score_state() specialised to the components this task declares."""
    weights = task["weights"]
    body = ['', '', 'def score_state(state):', '    body = _body(state)',
            '    lines = _flat(body)', '    joined = " ".join(lines)',
            '    idx = _row_indexes(lines)',
            '    found = all(i >= 0 for i in idx)',
            '    ordered = found and idx[0] < idx[1] and idx[1] < idx[2]',
            '    limited = found and not re.search(_needle(NEXT_CONTRIBUTOR), joined)']
    if task.get("combined_total") is not None:
        body.append('    summed = found and bool(re.search('
                    'r"(?<!\\d)" + str(COMBINED_TOTAL) + r"(?!\\d)", joined))')
    if task.get("branch") is not None:
        body.append('    on_branch = BRANCH_NAME in _branch_names(state, BRANCH_OWNER)')
    if task.get("stale_names"):
        body.append('    replaced = found and not any('
                    're.search(_needle(n), joined) for n in STALE_NAMES)')
    body.append('    checks = {')
    for name in weights:
        if name in ("roll_file_committed", "roll_file_committed_on_branch"):
            body.append('        "%s": bool(body.strip()),' % name)
        elif name in ("top_three_named_with_counts", "top_three_named"):
            body.append('        "%s": found,' % name)
        elif name == "ranked_highest_first":
            body.append('        "%s": ordered,' % name)
        elif name == "roll_limited_to_top_three":
            body.append('        "%s": limited,' % name)
        elif name == "combined_commits_recorded":
            body.append('        "%s": summed,' % name)
        elif name == "branch_created":
            body.append('        "%s": on_branch,' % name)
        elif name == "stale_entries_replaced":
            body.append('        "%s": replaced,' % name)
        else:
            raise KeyError(name)
    body.append('    }')
    body.append('    details = {')
    for name in weights:
        if name in ("roll_file_committed", "roll_file_committed_on_branch"):
            body.append('        "%s": "fileOverlay[%%s] holds %%d characters" '
                        '%% (FILE_KEY, len(body)),' % name)
        elif name in ("top_three_named_with_counts", "top_three_named"):
            body.append('        "%s": "line index per ranked contributor: %%r" %% (idx,),' % name)
        elif name == "ranked_highest_first":
            body.append('        "%s": "line index per ranked contributor: %%r" %% (idx,),' % name)
        elif name == "roll_limited_to_top_three":
            body.append('        "%s": "next-ranked contributor %%r present: %%r" '
                        '%% (NEXT_CONTRIBUTOR, bool(re.search(_needle(NEXT_CONTRIBUTOR), joined))),' % name)
        elif name == "combined_commits_recorded":
            body.append('        "%s": "combined total %%r present: %%r" '
                        '%% (COMBINED_TOTAL, summed),' % name)
        elif name == "branch_created":
            body.append('        "%s": "branchOverlay[%%s] == %%r" '
                        '%% (BRANCH_OWNER, _branch_names(state, BRANCH_OWNER)),' % name)
        elif name == "stale_entries_replaced":
            body.append('        "%s": "superseded names %%r still present: %%r" '
                        '%% (STALE_NAMES, [n for n in STALE_NAMES if re.search(_needle(n), joined)]),' % name)
    body.append('    }')
    body.append('    return _build(checks, details)')
    return "\n".join(body) + "\n"


def reward_py(task):
    return (REWARD_DOC.format(task_id=task["task_id"])
            + "import re\n"
            + constants_block(task)
            + score_block(task)
            + CORE
            + EVAL_TAIL)


def nemo_reward_py(task):
    return (NEMO_DOC.format(task_id=task["task_id"])
            + "import re\nimport sys\n\nimport requests\n\n"
            + 'SID = "__CUA_GYM_SID__"\n'
            + 'BASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n'
            + constants_block(task)
            + score_block(task)
            + CORE
            + NEMO_TAIL)


def setup_py(task):
    return SETUP_HEAD.format(task_id=task["task_id"], purpose=task["setup_purpose"],
                             overlay=json.dumps(task["setup_overlay"], indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# The ten tasks
# ---------------------------------------------------------------------------

HARD_A = {"roll_file_committed": 0.2, "top_three_named_with_counts": 0.45,
          "ranked_highest_first": 0.2, "roll_limited_to_top_three": 0.15}
HARD_SUM = {"roll_file_committed": 0.15, "top_three_named_with_counts": 0.4,
            "ranked_highest_first": 0.15, "combined_commits_recorded": 0.15,
            "roll_limited_to_top_three": 0.15}
HARD_BRANCH = {"branch_created": 0.15, "roll_file_committed_on_branch": 0.15,
               "top_three_named_with_counts": 0.4, "ranked_highest_first": 0.15,
               "roll_limited_to_top_three": 0.15}
HARD_STALE = {"top_three_named_with_counts": 0.45, "ranked_highest_first": 0.2,
              "stale_entries_replaced": 0.2, "roll_limited_to_top_three": 0.15}
MEDIUM_NAMES = {"roll_file_committed": 0.35, "top_three_named": 0.4,
                "ranked_highest_first": 0.15, "roll_limited_to_top_three": 0.1}

STALE_NVIDIA = ("# Contributors\n\nThanks to everyone who has helped keep the patch working.\n\n"
                "- reloxx13 - 20 commits\n- Daedalus - 10 commits\n- JustCryen - 5 commits\n\n"
                "Refresh this list from the repository's contributor statistics whenever it drifts.\n")

EXEMPLAR_PYAV = ("# PyAV-Org/PyAV\n\nTop contributors by commit count:\n\n"
                 "1. Mike Boers - 709 commits\n2. Jeremy Laine - 221 commits\n"
                 "3. Mark Reid - 55 commits\n")

TASKS = [
    {
        "n": "001", "slug": "fontello",
        "project": "fontello/fontello", "ref": "master", "path": "CONTRIBUTORS.md",
        "top_three": [["Aleksey V. Zapparov", 957], ["Vitaly Puzrin", 814], ["Roman I Shmelev", 153]],
        "fourth": "Dervus Grim",
        "style": "terse", "difficulty": "hard", "weights": HARD_A,
        "hard_criteria": ["derived_target", "shortcut_defeating"],
        "instruction": (
            "Publish a contributor honour roll for fontello/fontello: commit a new "
            "CONTRIBUTORS.md on its default branch listing the repo's three biggest "
            "committers, highest first, each with their exact commit count."),
        "analogues": [ANALOGUE_317, ANALOGUE_314],
        "extra_notes": ["Shortcut check: pasting the whole 15-row contributor list scores 0.85 because roll_limited_to_top_three fails; committing the three names without their counts scores 0.2, only roll_file_committed."],
    },
    {
        "n": "002", "slug": "node_http_proxy",
        "project": "http-party/node-http-proxy", "ref": "master", "path": "CREDITS.md",
        "top_three": [["indexzero", 227], ["Jarrett Cruger", 114], ["yawnt", 108]],
        "fourth": "cronopio",
        "style": "terse", "difficulty": "hard", "weights": HARD_A,
        "hard_criteria": ["derived_target", "shortcut_defeating"],
        "instruction": (
            "http-party/node-http-proxy needs a credits file. Commit CREDITS.md to its "
            "default branch naming the three contributors with the most commits, one per "
            "line in rank order, each line carrying that contributor's commit count."),
        "analogues": [ANALOGUE_317],
        "extra_notes": ["Shortcut check: pasting the whole 15-row contributor list scores 0.85 because roll_limited_to_top_three fails; committing the three names without their counts scores 0.2, only roll_file_committed."],
    },
    {
        "n": "003", "slug": "purelayout",
        "project": "PureLayout/PureLayout", "ref": "master", "path": "docs/CREDITS.md",
        "top_three": [["Tyler Fox", 146], ["Samford", 21], ["Kemar White", 16]],
        "fourth": "Anton Domashnev", "combined_total": 183,
        "style": "explicit", "difficulty": "hard", "weights": HARD_SUM,
        "hard_criteria": ["derived_target", "shortcut_defeating"],
        "instruction": (
            "The PureLayout/PureLayout repository needs a credits page. Open its "
            "contributors graph and read off the three contributors with the highest "
            "commit counts, then commit a new file docs/CREDITS.md on the default branch. "
            "Give it one markdown list item per contributor, ordered from most commits to "
            "fewest, each item holding that contributor's name and their commit count, and "
            "close with a line stating how many commits the three of them account for in "
            "total. Only those three belong on the page."),
        "analogues": [ANALOGUE_317, ANALOGUE_563],
        "extra_notes": ["The combined total is a sum the agent must compute; it is printed nowhere on the site. The page's own \"N commits by M contributors\" line is deliberately NOT graded, because the project overview reports a different total for the same repo and both renderings are defensible."],
    },
    {
        "n": "004", "slug": "maximum_awesome",
        "project": "square/maximum-awesome", "ref": "docs-credits", "path": "CONTRIBUTORS.md",
        "branch": "docs-credits", "branch_owner": "square/maximum-awesome",
        "top_three": [["Brian Donovan", 29], ["Sebastian Dahlgren", 23], ["Riley Strong", 15]],
        "fourth": "Sean Sorrell",
        "style": "terse", "difficulty": "hard", "weights": HARD_BRANCH,
        "hard_criteria": ["derived_target", "multi_mutation"],
        "instruction": (
            "On square/maximum-awesome, commit a CONTRIBUTORS.md to a new branch called "
            "docs-credits holding the repo's top three committers in rank order, highest "
            "first, each with their exact commit count."),
        "analogues": [ANALOGUE_317],
        "extra_notes": ["Changing the Target Branch field on the file editor (FileEditor.jsx:247) sets newBranch, and writeFiles(opts.createBranch) appends the row to repo.branchOverlay (mutations.js:236). The inert Start-a-new-merge-request checkbox is not graded. Shortcut check: committing to master instead of the new branch scores 0.0, because the graded overlay key is ref-scoped.", "Ref divergence is DELIBERATE: this project's projects.json default_branch is master, and docs-credits is the branch the instruction asks for. It is not the /-/new/main slip, where a reward keys a non-existent ref and fails a correct run."],
    },
    {
        "n": "005", "slug": "electronic_wechat",
        "project": "geeeeeeeeek/electronic-wechat", "ref": "master", "path": "CONTRIBUTORS.md",
        "top_three": [["Zhongyi Tong", 87], ["Ji Yang", 28], ["Cool Bear", 17]],
        "fourth": "arrowrowe", "combined_total": 132,
        "style": "terse", "difficulty": "hard", "weights": HARD_SUM,
        "hard_criteria": ["derived_target", "shortcut_defeating"],
        "instruction": (
            "Commit CONTRIBUTORS.md to the default branch of geeeeeeeeek/electronic-wechat "
            "listing its three leading committers highest first with their commit counts, "
            "then a closing line giving those three counts added together."),
        "analogues": [ANALOGUE_317],
        "extra_notes": ["The combined total is a sum the agent must compute; it is printed nowhere on the site. The page's own \"N commits by M contributors\" line is deliberately NOT graded, because the project overview reports a different total for the same repo and both renderings are defensible."],
    },
    {
        "n": "006", "slug": "nvidia_patch",
        "project": "keylase/nvidia-patch", "ref": "master", "path": "CONTRIBUTORS.md",
        "top_three": [["Snawoot", 304], ["Vladislav Yarmak", 99], ["Jai Luthra", 40]],
        "fourth": "Alexey Strekalovskiy",
        "stale_names": ["reloxx13", "Daedalus", "JustCryen"],
        "style": "terse", "difficulty": "hard", "weights": HARD_STALE,
        "hard_criteria": ["derived_target", "shortcut_defeating"],
        "instruction": (
            "The CONTRIBUTORS.md checked into keylase/nvidia-patch is out of date. Replace "
            "its contents with the repository's current top three committers, highest "
            "first, each with their exact commit count."),
        "analogues": [ANALOGUE_317, ANALOGUE_318],
        "extra_notes": ["The injected roll is the distractor: an agent that copies it scores 0.0. Every component is conjoined with the three correct rows being present, so the untouched injected state scores exactly 0.0 including roll_limited_to_top_three."],
        "setup_purpose": (
            "Puts an out-of-date CONTRIBUTORS.md on keylase/nvidia-patch:master. It names\n"
            "three genuine but lower-ranked contributors (reloxx13, Daedalus, JustCryen)\n"
            "with their real commit counts, so the file is a plausible stale artefact and a\n"
            "real distractor: an agent that trusts it instead of reading the contributors\n"
            "graph scores zero. It contains none of the top three, so the rubric is\n"
            "untouched at t=0."),
        "setup_overlay": {
            "fileOverlay": {"keylase/nvidia-patch:master:CONTRIBUTORS.md": STALE_NVIDIA},
            "treeOverlay": {"keylase/nvidia-patch:master": [
                {"path": "CONTRIBUTORS.md", "type": "blob", "mode": "100644",
                 "size": len(STALE_NVIDIA.encode("utf-8")), "sha": "a41c7b02"}]},
        },
        "injected": [
            "repo.fileOverlay['keylase/nvidia-patch:master:CONTRIBUTORS.md'] — a stale roll "
            "naming reloxx13 (20), Daedalus (10) and JustCryen (5), the 5th/6th/8th ranked "
            "contributors, with their real counts. Distractor: it is wrong in exactly the way "
            "a neglected credits file is wrong, and it names none of the top three, so no part "
            "of the rubric is pre-satisfied.",
            "repo.treeOverlay['keylase/nvidia-patch:master'] — the matching blob row, so the "
            "file renders in the repository tree and its Edit control is click-reachable.",
        ],
    },
    {
        "n": "007", "slug": "learnopencv_to_gimmiethat",
        "project": "abisubramanya27/learnopencv", "ref": "master",
        "sink": "byteblaze/gimmiethat.space", "path": "credits/learnopencv.md",
        "top_three": [["Satya Mallick", 119], ["vishwesh5", 101], ["Vikas", 53]],
        "fourth": "Sunita Nayak",
        "style": "terse", "difficulty": "hard", "weights": HARD_A,
        "hard_criteria": ["derived_target", "cross_section"],
        "instruction": (
            "My gimmiethat.space repo keeps a credits folder. Add credits/learnopencv.md "
            "there for abisubramanya27/learnopencv: its three biggest committers in rank "
            "order, each with their exact commit count."),
        "analogues": [ANALOGUE_791, ANALOGUE_317],
        "extra_notes": ["Two projects in one errand: the numbers are read on the source project's contributors graph and committed into byteblaze/gimmiethat.space, whose own contributor data is irrelevant. The graded overlay key names the sink repo, so writing the file into the source repo scores 0.0."],
        "setup_purpose": (
            "Creates the credits/ folder in byteblaze/gimmiethat.space with one existing\n"
            "page, credits/pyav.md, so the convention the instruction refers to actually\n"
            "exists on the site. It covers a different project (PyAV-Org/PyAV) and carries\n"
            "none of the graded names or numbers."),
        "setup_overlay": {
            "fileOverlay": {"byteblaze/gimmiethat.space:main:credits/pyav.md": EXEMPLAR_PYAV},
            "treeOverlay": {"byteblaze/gimmiethat.space:main": [
                {"path": "credits/pyav.md", "type": "blob", "mode": "100644",
                 "size": len(EXEMPLAR_PYAV.encode("utf-8")), "sha": "5b90de11"}]},
        },
        "injected": [
            "repo.fileOverlay['byteblaze/gimmiethat.space:main:credits/pyav.md'] plus the "
            "matching treeOverlay row — an existing credits page for a different project, so "
            "the 'credits folder' the instruction names is real and browsable. It holds none "
            "of learnopencv's contributors or counts, so the rubric is untouched at t=0.",
        ],
    },
    {
        "n": "008", "slug": "boommenu_to_gimmiethat",
        "project": "Nightonke/BoomMenu", "ref": "master",
        "sink": "byteblaze/gimmiethat.space", "path": "credits/boommenu.md",
        "top_three": [["Nightonke", 80], ["Weiping Huang", 75], ["Gpack", 4]],
        "fourth": "Zahan Safallwa",
        "style": "explicit", "difficulty": "hard", "weights": HARD_A,
        "hard_criteria": ["derived_target", "cross_section"],
        "instruction": (
            "I want a credits page for Nightonke/BoomMenu kept in my own repository. Open "
            "that project's contributors graph, note the three people with the most commits "
            "and how many commits each of them has, then go to byteblaze/gimmiethat.space "
            "and commit a new file at credits/boommenu.md on its default branch. Write the "
            "three of them as a markdown list, most commits first, each line carrying the "
            "name and the commit count, and include nobody else."),
        "analogues": [ANALOGUE_791, ANALOGUE_317],
        "extra_notes": ["Two projects in one errand: the numbers are read on the source project's contributors graph and committed into byteblaze/gimmiethat.space, whose own contributor data is irrelevant. The graded overlay key names the sink repo, so writing the file into the source repo scores 0.0."],
    },
    {
        "n": "009", "slug": "tutorials",
        "project": "eugenp/tutorials", "ref": "master", "path": "MAINTAINERS.md",
        "top_three": [["johnA1331", None], ["Krzysiek", None], ["Asjad J", None]],
        "fourth": "edizor",
        "style": "terse", "difficulty": "medium", "weights": MEDIUM_NAMES,
        "instruction": (
            "Commit MAINTAINERS.md to the default branch of eugenp/tutorials naming its "
            "three most prolific committers, one per line, most commits first."),
        "analogues": [ANALOGUE_314],
        "extra_notes": ["Names only, so the chain is R4 -> A7 and the task is a medium by derivation, not a padded hard. The counts still decide the order the agent must reproduce."],
        "skills": ["R4", "A7"],
        "skill_chain": ("ordinal selection over the contributors graph -> compose the three "
                        "names, in rank order, into a committed file"),
    },
    {
        "n": "010", "slug": "gcc",
        "project": "gcc-mirror/gcc", "ref": "master", "path": "docs/TOP_COMMITTERS.md",
        "top_three": [["Ju-Zhe Zhong", None], ["Jakub Jelinek", None], ["Jonathan Wakely", None]],
        "fourth": "Richard Biener",
        "style": "explicit", "difficulty": "medium", "weights": MEDIUM_NAMES,
        "instruction": (
            "gcc-mirror/gcc needs a short note recording who is currently doing the most "
            "work on it. Open the project's contributors graph, take the three contributors "
            "with the highest commit counts, and commit a new file docs/TOP_COMMITTERS.md on "
            "the default branch containing just their names, one per line, ordered from the "
            "most commits down to the fewest. Do not list anyone else."),
        "analogues": [ANALOGUE_314],
        "extra_notes": ["Names only, so the chain is R4 -> A7 and the task is a medium by derivation, not a padded hard. The counts still decide the order the agent must reproduce."],
        "skills": ["R4", "A7"],
        "skill_chain": ("ordinal selection over the contributors graph -> compose the three "
                        "names, in rank order, into a committed file"),
    },
]

INSPIRATION = ["webarena-314", "webarena-317", "webarena-318", "webarena-563",
               "webarena-786", "webarena-791"]



# Real commit counts and the next-ranked contributor's count, used for the
# recorded tie margins (names-only tasks grade names, but the ranking they must
# reproduce still comes from these numbers).
RANK_FACTS = {
    "001": ([957, 814, 153], 82),
    "002": ([227, 114, 108], 79),
    "003": ([146, 21, 16], 8),
    "004": ([29, 23, 15], 9),
    "005": ([87, 28, 17], 6),
    "006": ([304, 99, 40], 22),
    "007": ([119, 101, 53], 34),
    "008": ([80, 75, 4], 2),
    "009": ([883, 355, 244], 216),
    "010": ([395, 376, 356], 322),
}


def authoring_notes(task):
    notes = [
        "Ground truth read from src/data/contributors.json for %s ref %s, which is what "
        "src/pages/Contributors.jsx renders at /-/graphs/%s after sorting by commits "
        "descending (Contributors.jsx:132)." % (task["project"], task["ref"], task["ref"]),
        "Tie check: the top three commit counts are %s and the next contributor has %s, so "
        "both the ordering and the top-three boundary are unambiguous." % (
            task["margin_counts"], task["margin_next"]),
        "Writeback: repo.fileOverlay[%r] via mutations.js:229 commitToRepo, reached through "
        "the repository tree's Add-to-tree menu (RepoTree.jsx:405) or the project overview's "
        "'+' menu (ProjectOverview.jsx:414). No typed URL is needed from '/'." % task["file_key"],
        "Commit counts are pinned to /-/graphs/:ref; /-/commits/:ref and "
        "/-/graphs/:ref/charts read the 40-row-capped commits.json and report a different, "
        "wrong number.",
    ]
    notes.extend(task.get("extra_notes", []))
    return notes



REPLAY_TEMPLATE = """#!/usr/bin/env python3
\"\"\"Golden replay draft for {task_id} ({project}).

Click-only from '/': no page.goto after the landing page, no constructed URL.
Path: landing -> navbar search -> project -> sidebar Repository -> Contributors
      -> read the ranked cards -> sidebar Files -> Add-to-tree -> New file
      -> commit.

Selectors verified against the mock's source:
  navbar search input          Navbar.jsx:284   #search
  project result row           Search.jsx:300   ProjectRow link to /<full_path>
  sidebar Repository section   ProjectSidebar.jsx:24  a.shortcuts-tree
  sidebar Contributors child   ProjectSidebar.jsx:31  href .../-/graphs/<ref>
  contributor card             Contributors.jsx:161   h4 = name,
                                                      p  = "N commits (email)"
  Add-to-tree menu             RepoTree.jsx:399  button[aria-label='Add to tree']
  New file item                RepoTree.jsx:405
  editor fields                FileEditor.jsx:177/227/237/247/271
                               #file_name #editor #commit_message #branch_name
                               #commit-changes
\"\"\"
import re
import subprocess
import sys
import pathlib

import requests
from playwright.sync_api import sync_playwright

BUNDLE = pathlib.Path("/home/ubuntu/CUA-Gym/output/tasks/gitlab/{task_id}")
BASE = "http://localhost:8001"
SID = "{task_id}-golden"

EXPECTED_ROWS = {expected_rows}
FILE_PATH = "{file_path}"
COMMIT_MESSAGE = "{commit_message}"
TARGET_BRANCH = {target_branch}
BODY = \"\"\"{body}\"\"\"


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

    # 1. find the project through the navbar search box (a form control, not a URL)
    page.fill("#search", "{search_term}")
    page.press("#search", "Enter")
    page.wait_for_load_state("networkidle")
    page.click("a[href^='/{project}']")
    page.wait_for_load_state("networkidle")

    # 2. sidebar Repository -> its default page -> Contributors
    page.click("a.shortcuts-tree")
    page.wait_for_load_state("networkidle")
    page.click("a:has-text('Contributors')")
    page.wait_for_load_state("networkidle")

    # 3. read the ranked contributor cards; these are the numbers being transferred
    cards = page.locator(".contributors-charts .col-lg-6")
    for i, (name, count) in enumerate(EXPECTED_ROWS):
        card = cards.nth(i)
        assert name in card.inner_text(), (i, name, card.inner_text()[:120])
        if count is not None:
            assert re.search(r"(?<!\\d)%d(?!\\d)" % count, card.inner_text()), (i, count)

{sink_hop}
    # 4. back into the file tree and open the new-file editor by clicking
    page.click("a:has-text('Files')")
    page.wait_for_load_state("networkidle")
    page.click("button[aria-label='Add to tree']")
    page.click("a.dropdown-item:has-text('New file')")
    page.wait_for_selector("#file_name")

    # 5. compose and commit
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
"""

SINK_HOP = """    # 3b. hop to the sink repository: it is byteblaze's own, so it is listed on
    #     the landing page. Click the GitLab logo home link, then the project.
    page.click("a.gl-navbar-brand, a[href='/']")
    page.wait_for_load_state("networkidle")
    page.click("a[href^='/byteblaze/gimmiethat.space']")
    page.wait_for_load_state("networkidle")
    page.click("a.shortcuts-tree")
    page.wait_for_load_state("networkidle")
"""

REPLAY_BODIES = {
    "001": "# Contributors\n\n1. Aleksey V. Zapparov - 957 commits\n2. Vitaly Puzrin - 814 commits\n3. Roman I Shmelev - 153 commits\n",
    "002": "# Credits\n\n1. indexzero - 227 commits\n2. Jarrett Cruger - 114 commits\n3. yawnt - 108 commits\n",
    "003": "# Credits\n\n- Tyler Fox - 146 commits\n- Samford - 21 commits\n- Kemar White - 16 commits\n\nCombined: 183 commits\n",
    "004": "# Contributors\n\n1. Brian Donovan - 29 commits\n2. Sebastian Dahlgren - 23 commits\n3. Riley Strong - 15 commits\n",
    "005": "# Contributors\n\n1. Zhongyi Tong - 87 commits\n2. Ji Yang - 28 commits\n3. Cool Bear - 17 commits\n\nCombined: 132 commits\n",
    "006": "# Contributors\n\n1. Snawoot - 304 commits\n2. Vladislav Yarmak - 99 commits\n3. Jai Luthra - 40 commits\n",
    "007": "# abisubramanya27/learnopencv\n\n1. Satya Mallick - 119 commits\n2. vishwesh5 - 101 commits\n3. Vikas - 53 commits\n",
    "008": "# Nightonke/BoomMenu\n\n1. Nightonke - 80 commits\n2. Weiping Huang - 75 commits\n3. Gpack - 4 commits\n",
    "009": "# Maintainers\n\n1. johnA1331\n2. Krzysiek\n3. Asjad J\n",
    "010": "# Top committers\n\n1. Ju-Zhe Zhong\n2. Jakub Jelinek\n3. Jonathan Wakely\n",
}


def write_replay(task):
    rows = "[" + ", ".join(
        "(%r, %s)" % (name, "None" if count is None else count)
        for name, count in task["top_three"]) + "]"
    text = REPLAY_TEMPLATE.format(
        task_id=task["task_id"],
        project=task["project"],
        search_term=task["project"].split("/")[-1],
        expected_rows=rows,
        file_path=task["path"],
        commit_message="Add " + task["path"].split("/")[-1],
        target_branch=("None" if task.get("branch") is None else '"%s"' % task["branch"]),
        body=REPLAY_BODIES[task["n"]],
        sink_hop=(SINK_HOP if task.get("sink") else ""),
    )
    (REPLAYS / (task["task_id"] + ".py")).write_text(text, encoding="utf-8")


def success_criteria(task):
    key = task["file_key"]
    names = ", ".join("%s (%s)" % (n, c) if c is not None else n for n, c in task["top_three"])
    out = []
    if task.get("branch") is not None:
        out.append("repo.branchOverlay[\"%s\"] contains a branch named \"%s\"."
                   % (task["branch_owner"], task["branch"]))
    out.append("repo.fileOverlay[\"%s\"] holds a non-empty committed body." % key)
    if task["top_three"][0][1] is None:
        out.append("That body names, on separate lines, %s." % names)
    else:
        out.append("That body carries each of %s on a line holding both the name and that "
                   "exact commit count." % names)
    out.append("Those three lines appear highest-commit first.")
    if task.get("combined_total") is not None:
        out.append("The body also records the combined commit total %d." % task["combined_total"])
    if task.get("stale_names"):
        out.append("None of the superseded names %s remains in the body."
                   % ", ".join(task["stale_names"]))
    out.append("The next-ranked contributor \"%s\" does not appear in the body." % task["fourth"])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPLAYS.mkdir(parents=True, exist_ok=True)
    index = []
    rows = []
    for task in TASKS:
        task["task_id"] = "contributor_honour_roll_%s" % task["n"]
        counts, next_count = RANK_FACTS[task["n"]]
        task["margin_counts"] = "/".join(str(c) for c in counts)
        task["margin_next"] = str(next_count)
        sink = task.get("sink", task["project"])
        sink_ref = "main" if sink == "byteblaze/gimmiethat.space" else task["ref"]
        task["sink_full_path"] = sink
        task["sink_ref"] = sink_ref
        task["file_key"] = "%s:%s:%s" % (sink, sink_ref, task["path"])
        task.setdefault("skills", ["R4", "R3", "A7"])
        task.setdefault("skill_chain",
                        "ordinal selection of the top three rows on the contributors graph -> "
                        "read each one's commit count off the same page -> compose both into a "
                        "markdown list committed as a new file")
        bundle = OUT / task["task_id"]
        bundle.mkdir(parents=True, exist_ok=True)

        instr = {
            "task_id": task["task_id"],
            "task_instruction": task["instruction"],
            "app_dir": "webarena_gitlab_mock",
            "start_path": "/",
            "difficulty": task["difficulty"],
            "success_criteria": success_criteria(task),
        }
        (bundle / "task_instruction.json").write_text(
            json.dumps(instr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        metadata = {
            "style": task["style"],
            "difficulty": task["difficulty"],
            "shape": "retrieval_writeback",
            "skills": task["skills"],
            "skill_chain": task["skill_chain"],
            "official_analogues": task["analogues"],
            "topic": "gitlab contributor honour roll",
            "inspiration_ids": INSPIRATION,
            "authoring_notes": authoring_notes(task),
        }
        if task["difficulty"] == "hard":
            metadata["hard_criteria"] = task["hard_criteria"]
        if task.get("injected"):
            metadata["injected_preconditions"] = task["injected"]

        manifest = {
            "schema_version": 2,
            "task_id": task["task_id"],
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
        (bundle / "task.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        (bundle / "reward.py").write_text(reward_py(task), encoding="utf-8")
        nemo_code = nemo_reward_py(task)
        (bundle / "nemo_reward.py").write_text(nemo_code, encoding="utf-8")

        setup_code = None
        if task.get("setup_overlay"):
            setup_code = setup_py(task)
            (bundle / "initial_setup.py").write_text(setup_code, encoding="utf-8")

        row = {"task_payload": {
            "task_id": task["task_id"],
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": ["webarena_gitlab_mock"],
            "start_urls": [],
            "intent": task["instruction"],
            "eval": {"eval_types": ["string_match"], "reference_answers": None,
                     "note": "unused - CUA-Gym reward code is authoritative"},
            "cuagym": {
                "bundle_id": task["task_id"],
                "app_dir": "webarena_gitlab_mock",
                "initial_setup": setup_code,
                "eval_reward_code": nemo_code,
            },
        }}
        (bundle / "nemo_task.json").write_text(
            json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_replay(task)
        rows.append(row)
        index.append({"task_id": task["task_id"], "path": "../../%s/task.json" % task["task_id"]})

    BATCH.mkdir(parents=True, exist_ok=True)
    (BATCH / "index.json").write_text(
        json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n", encoding="utf-8")
    with (BATCH / "nemo_tasks.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("wrote %d bundles" % len(TASKS))


if __name__ == "__main__":
    main()
