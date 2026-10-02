import json, os, textwrap

ROOT = "/home/ubuntu/CUA-Gym/output/tasks/gitlab"
BATCH = os.path.join(ROOT, "_batches", "mention_participant_assign")
os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)

ME = 2330
AN_804 = "Assign the issue regarding flash alerts in dialog components to myself and tag primer to include them as a participant."
AN_446 = "Assign the issue regarding 404 errors in a11yproject to Roshanjossey."
AN_811 = "Assign the issue regarding 404 in a11yproject to myself."
AN_810 = "Assign all issues regarding flash alert in primer design guide repo to myself."
AN_447 = "Assign the issue regarding linking to an accessibility statement in a11y-webring.club to Rohan."

DECOY_TRUNC = {
    "id": 900101, "iid": 455, "project_id": 180, "author_id": 2384,
    "title": "Truncation page removed from docs but still linked in the navigation menu",
    "description": "Filed after a docs sweep: the truncation page is gone but the nav entry survives. Closing this one, the details are being tracked elsewhere.",
    "state": "closed", "assignee_ids": [], "label_ids": [], "milestone_id": None,
    "confidential": False, "discussion_locked": False, "due_date": None,
    "upvotes": 0, "downvotes": 0, "user_notes_count": 0,
    "created_at": "2022-12-05 11:04:19", "updated_at": "2022-12-14 09:31:02",
    "closed_at": "2022-12-14 09:31:02", "closed_by_id": 2383,
    "time_estimate": None, "total_time_spent": None,
}
DECOY_LINKT = {
    "id": 900101, "iid": 455, "project_id": 180, "author_id": 2383,
    "title": "Guidelines for link targets: should we ever use target=\"_blank\"?",
    "description": "Older write-up on link targets. Closed because the discussion moved on and nothing here was actionable any more.",
    "state": "closed", "assignee_ids": [], "label_ids": [], "milestone_id": None,
    "confidential": False, "discussion_locked": False, "due_date": None,
    "upvotes": 0, "downvotes": 0, "user_notes_count": 0,
    "created_at": "2022-06-18 15:22:07", "updated_at": "2022-08-02 08:40:55",
    "closed_at": "2022-08-02 08:40:55", "closed_by_id": 2383,
    "time_estimate": None, "total_time_spent": None,
}

T = []

T.append(dict(
    n="001", slug="broken_link_checker_a11yproject",
    issue=83685, iid=1521, project="a11yproject/a11yproject.com", pid=174,
    title="[Feature] Add a broken link checker to the CI/CD pipeline",
    assign=ME, mention="p2635", mention_display="Philip Wong",
    instruction="Someone filed an issue asking for a broken-link checker in the a11yproject CI pipeline. Put it on me, then leave a comment tagging whoever reported it so they stay in the loop.",
    style="terse", difficulty="hard", shape="retrieval_writeback",
    skills=["R6", "A1", "A8"], search="broken link checker",
    chain="R6 search the issue corpus for the broken-link-checker request -> A1 set that issue's assignee to me -> A8 comment on the same issue tagging the reporter's derived @handle",
    analogues=[AN_804, AN_811],
    hard=["derived_target", "ordering_dependency"],
    notes_extra=["The @handle is never stated: the reporter renders as the display name 'Philip Wong' in the issue header, and the agent must open /p2635 (or the users search scope) to read '@p2635'."],
    decoy=None,
))

T.append(dict(
    n="002", slug="truncation_nav_primer",
    issue=83791, iid=334, project="primer/design", pid=180,
    title="Truncation page has been removed, but not from navigation menu",
    assign=ME, mention="Roshanjossey", mention_display="Roshan Jossy",
    instruction="In primer/design there's a still-open issue about the truncation docs page being gone while the nav still links to it. Assign it to me and comment tagging @Roshanjossey as a participant.",
    style="terse", difficulty="hard", shape="mutation",
    skills=["R6", "A1", "A8"], search="truncation",
    chain="R6 search for the truncation-page report and discriminate the still-open one from the closed near-duplicate -> A1 assign it to me -> A8 comment on it tagging @Roshanjossey",
    analogues=[AN_804, AN_446],
    hard=["derived_target", "ordering_dependency"],
    notes_extra=["A closed near-duplicate is injected so 'truncation' returns two results; only the open one is the target, which forces the state predicate to be applied rather than the first hit clicked."],
    decoy=DECOY_TRUNC,
))

T.append(dict(
    n="003", slug="img_self_closing_primer",
    issue=83774, iid=240, project="primer/design", pid=180,
    title="Add lint rule to ensure `<img>` is self closing",
    assign=ME, mention=None, mention_display=None,
    instruction="Find the issue asking for a lint rule that forces `<img>` tags to be self-closing, and assign it to me.",
    style="terse", difficulty="medium", shape="mutation",
    skills=["R6", "A1"], search="self closing",
    chain="R6 search the issue corpus for the self-closing <img> lint request -> A1 set that issue's assignee to me",
    analogues=[AN_811, AN_810],
    hard=[],
    notes_extra=[],
    decoy=None,
))

T.append(dict(
    n="004", slug="wcag_references_a11yproject",
    issue=83620, iid=1277, project="a11yproject/a11yproject.com", pid=174,
    title="Content: Checklist WCAG references should be changed for better accuracy",
    assign=ME, mention="mxmason", mention_display="EJ Mason",
    instruction="The a11yproject.com repository has an open issue reporting that the accessibility checklist cites the wrong WCAG success criteria and should be reviewed for accuracy. Locate that issue through the site search, make yourself (Byte Blaze) its assignee, and then post one comment on it that tags EJ Mason by their @username so that EJ Mason becomes a participant on the thread. EJ Mason's handle is not written anywhere in this instruction on purpose - look it up in the user directory.",
    style="explicit", difficulty="hard", shape="retrieval_writeback",
    skills=["R6", "A1", "A8"], search="WCAG references",
    chain="R6 search the issue corpus for the WCAG-references accuracy report -> A1 assign it to me -> R6 search the user directory for 'EJ Mason' to derive @mxmason -> A8 comment on the issue tagging that handle",
    analogues=[AN_804, AN_446],
    hard=["derived_target", "cross_page"],
    notes_extra=["Two distinct retrievals: the issue by title/description text, and the handle by display name in /search?scope=users (Search.jsx:81 matches u.name and u.username). 'EJ Mason' resolves to exactly one user, id 2332."],
    decoy=None,
))

T.append(dict(
    n="005", slug="cancel_button_guidelines_primer",
    issue=83782, iid=290, project="primer/design", pid=180,
    title="Improve cancel button guidelines",
    assign=ME, mention="abisubramanya27", mention_display="Abishek S",
    instruction="The primer design guide has an issue asking for better guidance on when to show a cancel button. Assign it to me and comment tagging @abisubramanya27 so they're pulled in as a participant.",
    style="terse", difficulty="hard", shape="mutation",
    skills=["R6", "A1", "A8"], search="cancel button",
    chain="R6 search for the cancel-button guidance request and reject the unrelated keycloak hit -> A1 assign it to me -> A8 comment tagging @abisubramanya27",
    analogues=[AN_804, AN_810],
    hard=["derived_target", "ordering_dependency"],
    notes_extra=["'cancel button' already has a real cross-project distractor in the seed: keycloak/keycloak issue 78009 'Cancel button on edit key provider not working'. No injection needed."],
    decoy=None,
))

T.append(dict(
    n="006", slug="primer_mobile_figma_links",
    issue=83788, iid=310, project="primer/design", pid=180,
    title="Link to Primer Mobile Figma library is broken",
    assign=None, mention="primer", mention_display="Primer",
    instruction="Someone reported that the Primer Mobile Figma library links in the docs are dead. Comment on that issue tagging @primer so they get pulled into the thread.",
    style="terse", difficulty="medium", shape="mutation",
    skills=["R6", "A8"], search="Primer Mobile Figma",
    chain="R6 search the issue corpus for the dead Primer Mobile Figma links report -> A8 comment on it tagging @primer",
    analogues=[AN_804],
    hard=[],
    notes_extra=[],
    decoy=None,
))

T.append(dict(
    n="007", slug="spinner_size_guidelines_primer",
    issue=83793, iid=372, project="primer/design", pid=180,
    title="Spinners: Create guidelines for using the correct size in it's context",
    assign=ME, mention="maximedegreve", mention_display="Maxime De Greve",
    instruction="In primer/design there is an open issue asking for guidance on which spinner size to use in which context (sidebars, modals, body, lists). Find that issue, assign it to yourself, and then post one comment on it that tags the person who opened it, using their @username, so they are kept as a participant. Their handle is shown on their profile page - the issue header only shows their display name.",
    style="explicit", difficulty="hard", shape="retrieval_writeback",
    skills=["R6", "A1", "A8"], search="spinners",
    chain="R6 search the issue corpus for the spinner-size guidance request -> A1 assign it to me -> R9/R6 read the reporter off the issue header and open their profile to derive @maximedegreve -> A8 comment tagging that handle",
    analogues=[AN_804, AN_811],
    hard=["derived_target", "cross_page"],
    notes_extra=["The issue header renders the author's display name only (IssueDetail.jsx:163); '@username' appears on /:username (UserProfile.jsx:359) and in the users search scope (Search.jsx:319)."],
    decoy=None,
))

T.append(dict(
    n="008", slug="link_targets_primer",
    issue=83810, iid=85, project="primer/design", pid=180,
    title="Guidelines should document our take on link targets",
    assign=ME, mention="khiga8", mention_display="Kate Higa",
    instruction="primer/design has an open issue asking the guidelines to document our stance on link targets and target=\"_blank\". Assign it to me and comment tagging Kate Higa by her @handle.",
    style="terse", difficulty="hard", shape="retrieval_writeback",
    skills=["R6", "A1", "A8"], search="link targets",
    chain="R6 search for the link-targets guidance issue and pick the open one over the closed near-duplicate -> A1 assign it to me -> R6 resolve 'Kate Higa' to @khiga8 in the user directory -> A8 comment tagging that handle",
    analogues=[AN_804, AN_446],
    hard=["derived_target", "cross_page"],
    notes_extra=["A closed near-duplicate on link targets is injected, so the search returns two rows and the open-state predicate has to be applied.", "'Kate Higa' resolves to exactly one user, id 2386, handle khiga8."],
    decoy=DECOY_LINKT,
))

T.append(dict(
    n="009", slug="gulp_watch_windows_a11yproject",
    issue=83684, iid=1519, project="a11yproject/a11yproject.com", pid=174,
    title="`npm start` does not run `gulp-watch` (Windows)",
    assign=2264, mention="primer", mention_display="Primer",
    instruction="A contributor on Windows reported that `npm start` in a11yproject.com never runs `gulp-watch`, so the site is generated but never served with styles. Find that issue, set Roshan Jossy as its assignee, and then post one comment on it tagging @primer so that they are added as a participant on the thread.",
    style="explicit", difficulty="hard", shape="mutation",
    skills=["R6", "A1", "A8"], search="gulp-watch",
    chain="R6 search the issue corpus for the Windows gulp-watch report -> A1 set its assignee to Roshan Jossy -> A8 comment on the same issue tagging @primer",
    analogues=[AN_446, AN_447],
    hard=["derived_target", "ordering_dependency"],
    notes_extra=["The per-issue assignee dropdown offers all 2199 users, not just project members (components/issuable/Controls.jsx:47-62), so Roshan Jossy is selectable on a11yproject.com without an invite."],
    decoy=None,
))

T.append(dict(
    n="010", slug="node_install_empathy_prompts",
    issue=83732, iid=11, project="byteblaze/empathy-prompts", pid=183,
    title="Node >= v12 fails on install",
    assign=None, mention="esjay", mention_display="Wayne Elgin",
    instruction="Find the empathy-prompts issue about installs failing on Node v12 and up, and comment on it tagging the person who opened it by their @handle.",
    style="terse", difficulty="medium", shape="retrieval_writeback",
    skills=["R6", "A8"], search="fails on install",
    chain="R6 search the issue corpus for the Node v12 install failure -> R9 read its reporter and derive their @handle from the profile -> A8 comment on the issue tagging that handle",
    analogues=[AN_804],
    hard=[],
    notes_extra=["The reporter is shown as 'Wayne Elgin' in the issue header; '@esjay' is only on the profile page, so the tagged handle is a derived value written back into a comment."],
    decoy=None,
))

assert len(T) == 10

# ---------------------------------------------------------------- emitters --

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

OVERLAY_TUPLES = '''OVERLAY_COLLECTIONS = [
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


def component_weights(t):
    if t["assign"] is not None and t["mention"] is not None:
        return {"issue_assigned": 0.5, "mention_comment_posted": 0.5}
    if t["assign"] is not None:
        return {"issue_assigned": 1.0}
    return {"mention_comment_posted": 1.0}


def scoring_source(t):
    w = component_weights(t)
    lines = []
    lines.append("COMPONENT_WEIGHTS = {")
    for k, v in w.items():
        lines.append("    %s: %s," % (json.dumps(k), repr(v)))
    lines.append("}")
    lines.append("assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9")
    lines.append("")
    lines.append("TARGET_ISSUE_ID = %d" % t["issue"])
    if t["assign"] is not None:
        lines.append("ASSIGNEE_ID = %d" % t["assign"])
    if t["mention"] is not None:
        lines.append("MENTION_HANDLE = %s" % json.dumps(t["mention"].lower()))
        lines.append("COMMENT_AUTHOR_ID = %d" % ME)
        lines.append("")
        lines.append('MENTION_RE = re.compile(r"@([A-Za-z0-9][A-Za-z0-9._-]*)")')
    lines.append("")
    lines.append('''

def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _issue_records(state):
    """Every issue record the agent could have written: created rows plus
    overlay edits of frozen rows. Reads current_state only."""
    out = []
    for rec in _list(_dict(state).get("newIssues")):
        if isinstance(rec, dict):
            out.append(rec)
    for rec in _dict(_dict(state).get("issueEdits")).values():
        if isinstance(rec, dict):
            out.append(rec)
    return out


def _assignee_ids(rec):
    return [str(x) for x in _list(_dict(rec).get("assignee_ids"))]
'''.strip("\n"))
    lines.append("")
    if t["assign"] is not None:
        lines.append('''

def _check_assigned(state):
    target = None
    holders = set()
    for rec in _issue_records(state):
        ids = _assignee_ids(rec)
        if str(ASSIGNEE_ID) in ids:
            holders.add(str(rec.get("id")))
        if str(rec.get("id")) == str(TARGET_ISSUE_ID):
            target = rec
    want = set([str(TARGET_ISSUE_ID)])
    if target is None:
        return False, "no written issue record for id %s; issues now assigned to %s == %s" % (
            TARGET_ISSUE_ID, ASSIGNEE_ID, sorted(holders))
    ok = _assignee_ids(target) == [str(ASSIGNEE_ID)] and holders == want
    return ok, "issue %s assignee_ids == %s; issues now assigned to %s == %s (want exactly %s)" % (
        TARGET_ISSUE_ID, _assignee_ids(target), ASSIGNEE_ID, sorted(holders), sorted(want))
'''.strip("\n"))
        lines.append("")
    if t["mention"] is not None:
        lines.append('''

def _check_comment(state):
    mine = []
    for note in _list(_dict(state).get("newNotes")):
        if not isinstance(note, dict):
            continue
        if note.get("system"):
            continue
        if str(note.get("author_id")) != str(COMMENT_AUTHOR_ID):
            continue
        mine.append(note)
    if len(mine) != 1:
        return False, "new non-system comments written by user %s == %d (want exactly 1)" % (
            COMMENT_AUTHOR_ID, len(mine))
    note = mine[0]
    if str(note.get("noteable_type")) != "Issue" or str(note.get("noteable_id")) != str(TARGET_ISSUE_ID):
        return False, "the new comment sits on %s %s, not on Issue %s" % (
            note.get("noteable_type"), note.get("noteable_id"), TARGET_ISSUE_ID)
    body = note.get("body")
    mentions = set()
    for handle in MENTION_RE.findall(str(body if body is not None else "")):
        mentions.add(handle.lower())
    want = set([MENTION_HANDLE])
    return mentions == want, "handles tagged in the new comment on issue %s == %s (want exactly %s)" % (
        TARGET_ISSUE_ID, sorted(mentions), sorted(want))
'''.strip("\n"))
        lines.append("")
    lines.append('''

def score_state(state):
    checks = {}
    details = {}
''')
    if t["assign"] is not None:
        lines.append('    ok, why = _check_assigned(state)\n    checks["issue_assigned"] = ok\n    details["issue_assigned"] = why')
    if t["mention"] is not None:
        lines.append('    ok, why = _check_comment(state)\n    checks["mention_comment_posted"] = ok\n    details["mention_comment_posted"] = why')
    lines.append('''    components = []
    for name in COMPONENT_WEIGHTS:
        hit = bool(checks.get(name))
        components.append({
            "name": name,
            "score": COMPONENT_WEIGHTS[name] if hit else 0.0,
            "details": details.get(name, ""),
        })
    return components


def _clamp(value):
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value
''')
    return "\n".join(lines)


def reward_py(t):
    head = '"""Deterministic reward for %s.\n\n%s\n\nReads the frozen evidence bundle; current_state only.\n"""\n' % (
        t["task_id"], t["reward_doc"])
    return head + "import re\n\n\n" + scoring_source(t) + '''

def evaluate(evidence):
    apps = _dict(_dict(evidence).get("apps"))
    state = _dict(_dict(apps.get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''


def nemo_reward_py(t):
    head = '"""NeMo-Gym reward program for %s.\n\n%s\n\nGET /go?sid=... and print REWARD: <float> on every output path.\n"""\n' % (
        t["task_id"], t["reward_doc"])
    return head + "import re\nimport sys\n\nimport requests\n\nSID = \"__CUA_GYM_SID__\"\nBASE_URL = \"__CUA_GYM_WEBARENA_GITLAB_URL__\"\n\n\n" + scoring_source(t) + '''

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


def setup_py(t):
    decoy = t["decoy"]
    head = ('"""NeMo-Gym setup program for %s.\n\n%s\n\n'
            'Self-contained: standard library plus requests (in cuagym/requirements.txt).\n"""\n'
            % (t["task_id"], t["setup_doc"]))
    body = 'import json\nimport sys\n\nimport requests\n\nSID = "__CUA_GYM_SID__"\nBASE_URL = "__CUA_GYM_WEBARENA_GITLAB_URL__"\n\n'
    body += 'BASE_STATE = json.loads(r"""%s""")\n\n' % BASE_STATE_JSON
    body += OVERLAY_TUPLES + "\n"
    body += 'INJECTED_ISSUES = json.loads(r"""%s""")\n\n' % json.dumps([decoy], indent=2)
    body += '''

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
    return head + body


def replay_py(t):
    lines = []
    lines.append('"""Golden replay draft for %s.' % t["task_id"])
    lines.append("")
    lines.append("Click-only after the landing page: navbar search -> Issues scope pill%s ->" % (
        " -> Open status filter" if t["decoy"] else ""))
    lines.append("the result row -> the issue's sidebar and comment box. No page.goto() after")
    lines.append("the initial load, no constructed URL.")
    lines.append('"""')
    lines.append("SEARCH_TERM = %s" % json.dumps(t["search"]))
    lines.append("TITLE = %s" % json.dumps(t["title"]))
    if t["mention"]:
        lines.append("HANDLE = %s" % json.dumps("@" + t["mention"]))
        lines.append("COMMENT = %s" % json.dumps("@%s could you keep an eye on this one? Adding you as a participant." % t["mention"]))
    lines.append("")
    lines.append("")
    lines.append("def run(page, base_url, sid):")
    lines.append('    page.goto("%s/?sid=%s" % (base_url.rstrip("/"), sid))')
    lines.append('    page.wait_for_selector("#search")')
    lines.append("")
    lines.append("    # 1. locate the issue from the front door")
    lines.append('    page.fill("#search", SEARCH_TERM)')
    lines.append('    page.press("#search", "Enter")')
    lines.append('    page.wait_for_selector(\'[data-testid="search-filter"]\')')
    lines.append('    page.click(\'[data-testid="search-filter"] a:has-text("Issues")\')')
    lines.append('    page.wait_for_selector(".search-results")')
    if t["decoy"]:
        lines.append("    # the injected closed near-duplicate also matches; filter to Open")
        lines.append('    page.check("#state-opened")')
        lines.append('    page.click(\'button:has-text("Apply")\')')
        lines.append('    page.wait_for_selector(".search-results")')
    lines.append('    page.click(\'.search-results a:has-text("%s")\' % TITLE)')
    lines.append('    page.wait_for_selector(\'[data-testid="assignee-block-container"]\')')
    lines.append("")
    if t["assign"] == ME:
        lines.append("    # 2. assign myself through the sidebar's own shortcut")
        lines.append('    page.click(\'[data-testid="assign-yourself"]\')')
        lines.append('    page.wait_for_timeout(300)')
    elif t["assign"] is not None:
        lines.append("    # 2. assign the named user through the sidebar dropdown")
        lines.append('    page.click(\'[data-testid="assignee-block-container"] [data-testid="edit-button"]\')')
        lines.append('    page.fill(\'[data-qa-selector="dropdown_input_field"]\', %s)' % json.dumps(t["mention_display"] if False else "Roshan Jossy"))
        lines.append('    page.click(\'button.dropdown-item:has-text("Roshan Jossy")\')')
        lines.append('    page.wait_for_timeout(300)')
    if t["mention"]:
        lines.append("")
        if t["shape"] == "retrieval_writeback":
            lines.append("    # 3. derive the handle: click the person's name, read @handle, click back")
            lines.append("    #    (the profile is reached by clicking a rendered link, so returning")
            lines.append("    #     to the issue with go_back() stays inside the clicked history)")
            lines.append('    # expected handle: %s' % ("@" + t["mention"]))
        lines.append("    # post the comment that tags them")
        lines.append('    page.fill(\'[data-qa-selector="comment_field"]\', COMMENT)')
        lines.append('    page.click(\'[data-qa-selector="comment_button"]\')')
        lines.append('    page.wait_for_timeout(500)')
    lines.append("")
    lines.append("")
    lines.append("# Issue route the search result lands on: /%s/-/issues/%d" % (t["project"], t["iid"]))
    return "\n".join(lines) + "\n"


def success_criteria(t):
    out = []
    if t["assign"] is not None:
        out.append(
            "current_state records issue id %d (%s #%d, \"%s\") with assignee_ids exactly [%d], "
            "and %d is the assignee of exactly that one issue across current_state.issueEdits and current_state.newIssues."
            % (t["issue"], t["project"], t["iid"], t["title"], t["assign"], t["assign"]))
    if t["mention"] is not None:
        out.append(
            "current_state.newNotes holds exactly one non-system note authored by user 2330 (byteblaze); "
            "its noteable_type is \"Issue\" and its noteable_id is %d." % t["issue"])
        out.append(
            "That note's body tags exactly one handle, @%s (%s), and no other @handle."
            % (t["mention"], t["mention_display"]))
    return out


def write_bundle(t):
    d = os.path.join(ROOT, t["task_id"])
    os.makedirs(d, exist_ok=True)
    instr = t["instruction"]

    ti = {
        "task_id": t["task_id"],
        "task_instruction": instr,
        "app_dir": "webarena_gitlab_mock",
        "start_path": "/",
        "difficulty": t["difficulty"],
        "success_criteria": success_criteria(t),
    }
    open(os.path.join(d, "task_instruction.json"), "w").write(json.dumps(ti, indent=2) + "\n")

    meta = {
        "style": t["style"],
        "difficulty": t["difficulty"],
        "shape": t["shape"],
        "skills": t["skills"],
        "skill_chain": t["chain"],
        "official_analogues": t["analogues"],
        "hard_criteria": t["hard"],
        "topic": "gitlab search-then-assign-then-mention",
        "inspiration_ids": ["webarena-804", "webarena-446", "webarena-811", "webarena-810", "webarena-447"],
        "authoring_notes": t["notes"],
    }
    if t["decoy"]:
        meta["injected_preconditions"] = t["injected"]

    manifest = {
        "schema_version": 2,
        "task_id": t["task_id"],
        "instruction": instr,
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
    open(os.path.join(d, "task.json"), "w").write(json.dumps(manifest, indent=2) + "\n")
    open(os.path.join(d, "reward.py"), "w").write(reward_py(t))
    nr = nemo_reward_py(t)
    open(os.path.join(d, "nemo_reward.py"), "w").write(nr)
    setup = None
    if t["decoy"]:
        setup = setup_py(t)
        open(os.path.join(d, "initial_setup.py"), "w").write(setup)

    row = {"task_payload": {
        "task_id": t["task_id"],
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": ["webarena_gitlab_mock"],
        "start_urls": [],
        "intent": instr,
        "eval": {"eval_types": ["string_match"], "reference_answers": None,
                 "note": "unused - CUA-Gym reward code is authoritative"},
        "cuagym": {
            "bundle_id": t["task_id"],
            "app_dir": "webarena_gitlab_mock",
            "initial_setup": setup,
            "eval_reward_code": nr,
        },
    }}
    open(os.path.join(d, "nemo_task.json"), "w").write(json.dumps(row, indent=2) + "\n")
    open(os.path.join(BATCH, "replays", t["task_id"] + ".py"), "w").write(replay_py(t))
    return row


for t in T:
    t["task_id"] = "mention_participant_assign_%s_%s" % (t["slug"], t["n"])
    doc_bits = ["Target: issue %d = %s #%d %r." % (t["issue"], t["project"], t["iid"], t["title"])]
    if t["assign"] is not None:
        doc_bits.append("Assignee the task asks for: user %d." % t["assign"])
    if t["mention"] is not None:
        doc_bits.append("Handle the comment must tag: @%s (%s)." % (t["mention"], t["mention_display"]))
    doc_bits.append("IssueDetail.jsx:103 patch -> AppContext.jsx:300 updateIn writes the whole issue")
    doc_bits.append("record into current_state.issueEdits[<id>]; NotesTimeline.jsx:321 postComment")
    doc_bits.append("appends the comment into current_state.newNotes. The rubric asserts the exact")
    doc_bits.append("resulting values, never 'the record was touched'.")
    t["reward_doc"] = "\n".join(doc_bits)
    notes = [
        "Grounded in hub/websites/webarena_gitlab_mock as served.",
        "R6 mechanism: pages/Search.jsx:76 matches issue title and description across the whole corpus; there is no notes scope, so the described symptom is in the issue's own title/description.",
        "A1 mechanism: pages/IssueDetail.jsx:422 assign-yourself and :438 the assignee UserSelect both call patch({assignee_ids: [...]}), which lands in issueEdits.<id>.",
        "A8 mechanism: pages/NotesTimeline.jsx:321 postComment appends to newNotes with author_id = currentUser.id and system false.",
        "The per-issue assignee dropdown offers all 2199 users (components/issuable/Controls.jsx:47-62), unlike the members-only bulk sidebar.",
        "Reachable from '/': navbar search box (#search, components/layout/Navbar.jsx:285) -> /search -> Issues scope pill -> result link -> issue detail. No typed URL.",
        "Reward asserts the exact resulting collection: the set of issues assigned to the target user across issueEdits + newIssues is exactly {%d}, so assigning extra issues scores 0." % t["issue"],
    ]
    notes.extend(t["notes_extra"])
    t["notes"] = notes
    if t["decoy"]:
        t["setup_doc"] = (
            "Plants one closed near-duplicate issue (id %d, %s #%d) in %s so the search\n"
            "for the described symptom returns two rows and only one of them is open.\n"
            "It satisfies every part of the filter except the state, which is exactly the\n"
            "predicate the instruction turns on. It is unassigned, carries no comment and\n"
            "no @mention, so it pre-satisfies no part of the rubric and the untouched lane\n"
            "still scores exactly 0.0." % (t["decoy"]["id"], t["project"], t["decoy"]["iid"], t["project"]))
        t["injected"] = [
            "newIssues: one closed issue id %d, iid %d, project_id %d (%s), title %r, author_id %d, "
            "assignee_ids [], user_notes_count 0. Its iid is above every seeded iid in the project, "
            "and its id is above SEED_NEXT_IDS.issue (83821), so AppContext.allocateId cannot mint a collision."
            % (t["decoy"]["id"], t["decoy"]["iid"], t["decoy"]["project_id"], t["project"],
               t["decoy"]["title"], t["decoy"]["author_id"]),
            "Why: on the pristine seed the search term returns exactly one row, so the open/closed "
            "predicate in the instruction is free. The decoy makes the agent read the state badge.",
            "It carries no assignee and no note, so no rubric component is pre-satisfied.",
        ]

rows = [write_bundle(t) for t in T]

with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")

open(os.path.join(BATCH, "index.json"), "w").write(json.dumps({
    "schema_version": 2,
    "tasks": [{"task_id": t["task_id"], "path": "../../%s/task.json" % t["task_id"]} for t in T],
}, indent=2) + "\n")

print("terse", sum(1 for t in T if t["style"] == "terse"), "explicit", sum(1 for t in T if t["style"] == "explicit"))
print("hard", sum(1 for t in T if t["difficulty"] == "hard"), "medium", sum(1 for t in T if t["difficulty"] == "medium"))
print("rw", sum(1 for t in T if t["shape"] == "retrieval_writeback"))
for t in T:
    print(t["task_id"], len(t["instruction"].split()), t["style"])
