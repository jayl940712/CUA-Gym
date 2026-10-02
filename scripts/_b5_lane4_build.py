#!/usr/bin/env python3
"""Authoring generator for batch-5 lane 4 (gitlab / milestone_kickoff).

Emits the ten bundles, their replay drafts and the lane index. This is an
authoring tool, not validation: it writes files and runs nothing against a
server.
"""
import json
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym")
OUT = ROOT / "output" / "tasks" / "gitlab"
BATCH = OUT / "_batches" / "milestone_kickoff"
REPLAYS = BATCH / "replays"

APP_DIR = "webarena_gitlab_mock"
URL_TOKEN = "__CUA_GYM_WEBARENA_GITLAB_URL__"

A_590 = ('Create a milestone in the current repo with title "product launch" for the upcoming '
         'event of product launch starting on January 16, 2030 and ending on January 30, 2030')
A_591 = ('Create a milestone in the current repo with title "code review" for the upcoming '
         'practice of collective code review starting on January 16, 2030 and ending in 20 days '
         '(inclusive)')
A_592 = ('Create a milestone in the current repo with title "sensitive information" for the '
         'upcoming task of cleaning sensitive information starting on February 16, 2030 and '
         'ending in 20 days (inclusive)')
A_593 = ('Create a milestone in the current repo with title "all branches to main" for the '
         'upcoming task of merging all branches to main starting on March 15, 2044 and ending '
         'on March 30, 2044')
A_594 = ('Create a milestone in the current repo with title "zsh comprehensive support" for the '
         'upcoming task of adding a new branch for zsh comprehensive support starting on May 1, '
         '2044 and ending in 20 days (inclusive)')
A_658 = ('Create an issue in a11yproject repo with title "401 bad gateway". Assign the issue to '
         'Roshanjossey (you can invite users to the project if needed). Set due date to be the '
         'end of 2030')
A_659 = ('Create an issue in my empathy-prompts repo with title "Integrating LLMs for better '
         'prompts". Assign the issue to Roshanjossey (you can invite users to the project if '
         'needed). Set due date to be the beginning of Q2 2033')
A_660 = ('Create an issue in my dotfiles repo with title "add support for oh-my-zsh". Assign the '
         'issue to Abishek (you can invite users to the project if needed). Set due date to be '
         'July 18 2033')
A_808 = ('Create an issue in cloud-to-butt repo with title "Let\'s keep the project alive". '
         'Assign the issue to myself (you can invite users to the project if needed). Set due '
         'date to be the end of Q1 2033. Stay on the page after clicking on Create issue.')
A_809 = ('Create an issue in a11yproject repo with title "404 for many URLs". Assign the issue '
         'to myself (you can invite users to the project if needed). Set due date to be 2030-1-3. '
         'Stay on the page after clicking on Create issue.')
A_447 = ('Assign the issue regarding linking to an accessibility statement in a11y-webring.club '
         'to Rohan.')
A_446 = 'Assign the issue regarding 404 errors in a11yproject to Roshanjossey.'

TASKS = [
    # ------------------------------------------------------------------ 001
    dict(
        num="001", kind="ms_issue", project_id=193, project_path="byteblaze/dotfiles",
        style="terse", difficulty="hard", shape="mutation",
        skills=["R2", "A2", "A12"],
        skill_chain="resolve 'the end of Q3 2032' to a date -> create the milestone with that "
                    "window -> create the kickoff issue on that same milestone, assigned, with "
                    "the same computed date as its due date",
        analogues=[A_594, A_660],
        hard_criteria=["multi_mutation", "cross_section"],
        instruction=('On my dotfiles repo add a milestone "shell rewrite" running from July 1 '
                     '2032 to the end of Q3 2032, then file issue "Draft the shell rewrite plan" '
                     "on it, assigned to Abishek S, due the milestone's last day."),
        milestone=dict(title="shell rewrite", start="2032-07-01", due="2032-09-30"),
        issue=dict(title="Draft the shell rewrite plan", due="2032-09-30",
                   assignee_id=5, assignee_name="Abishek S"),
        inspiration_ids=["webarena-594", "webarena-660"],
        notes=[
            "End of Q3 2032 = 2032-09-30. That one computed date feeds both the milestone's "
            "due_date and the issue's due_date, which is what makes this a hard chain rather "
            "than two stapled forms.",
            "byteblaze/dotfiles (project 193) carries zero seeded milestones, so the milestone "
            "must be created (src/data/milestones.json has no row for any byteblaze/* project).",
            "The issue's Milestone dropdown lists state.milestones for the project "
            "(NewIssue.jsx:51), so the milestone genuinely has to exist first.",
        ],
    ),
    # ------------------------------------------------------------------ 002
    dict(
        num="002", kind="ms_issue", project_id=179, project_path="byteblaze/a11y-webring.club",
        style="terse", difficulty="hard", shape="retrieval_writeback",
        skills=["R2", "R4", "A2", "A12"],
        skill_chain="resolve 'the whole of Q2 2033' to a start/due pair -> create the milestone "
                    "-> read the newest open issue to identify its reporter -> create the "
                    "kickoff issue on that milestone, assigned to that reporter, due the "
                    "computed end date",
        analogues=[A_590, A_447],
        hard_criteria=["multi_mutation", "derived_target", "cross_section"],
        instruction=('a11y-webring.club needs a milestone "statement support" covering the whole '
                     'of Q2 2033, plus an issue "Plan accessibility statement support" on that '
                     "milestone, due the day it ends and assigned to whoever opened the repo's "
                     "newest open issue."),
        milestone=dict(title="statement support", start="2033-04-01", due="2033-06-30"),
        issue=dict(title="Plan accessibility statement support", due="2033-06-30",
                   assignee_id=2366, assignee_name="Rohan Kumar"),
        inspiration_ids=["webarena-590", "webarena-447"],
        notes=[
            "Derived assignee: project 179 has exactly four open issues; the newest is #71 "
            "(created 2023-02-02) by Seirdy / Rohan Kumar (user 2366). Next newest is #39 at "
            "2023-01-22, an 11-day margin, and the issue list's default sort is created_date "
            "newest-first (hooks.js:267), so the answer is read straight off page one.",
            "Q2 2033 = 2033-04-01 .. 2033-06-30.",
        ],
    ),
    # ------------------------------------------------------------------ 003
    dict(
        num="003", kind="ms", project_id=184, project_path="byteblaze/gimmiethat.space",
        style="terse", difficulty="medium", shape="mutation",
        skills=["R2", "A2"],
        skill_chain="resolve 'ending in 20 days (inclusive)' against the stated start date -> "
                    "create the milestone with that window",
        analogues=[A_592, A_591],
        hard_criteria=None,
        instruction=('Add a milestone to my gimmiethat.space repo titled "storage cleanup" for '
                     "the upcoming storage cleanup starting on April 3, 2031 and ending in 20 "
                     "days (inclusive)."),
        milestone=dict(title="storage cleanup", start="2031-04-03", due="2031-04-23"),
        inspiration_ids=["webarena-592", "webarena-591"],
        notes=[
            "'ending in 20 days (inclusive)' follows the official convention exactly: "
            "webarena-591 starts 2030-01-16 and its reference due date is Feb 5 2030 "
            "(start + 20), webarena-592 starts 2030-02-16 for Mar 8 2030, webarena-594 starts "
            "2044-05-01 for May 21 2044. So 2031-04-03 + 20 = 2031-04-23.",
        ],
    ),
    # ------------------------------------------------------------------ 004
    dict(
        num="004", kind="issue", project_id=187,
        project_path="byteblaze/millennials-to-snake-people",
        style="terse", difficulty="medium", shape="retrieval_writeback",
        skills=["R4", "A12"],
        skill_chain="read the repo's most recent open issue to identify its reporter -> create "
                    "the new issue and assign it to that person with the stated due date",
        analogues=[A_808, A_446],
        hard_criteria=None,
        instruction=("File an issue in my millennials-to-snake-people repo titled \"Triage the "
                     "Stadia breakage report\", due March 31, 2033, and assign it to the person "
                     "who reported that repo's most recent open issue."),
        issue=dict(title="Triage the Stadia breakage report", due="2033-03-31",
                   assignee_id=2397, assignee_name="J K"),
        inspiration_ids=["webarena-808", "webarena-446"],
        notes=[
            "Project 187 has four open issues. The newest is #37 (2021-02-03) by TheOkayJK / "
            "J K (user 2397); the runner-up is #29 at 2019-03-31, a 22-month margin.",
            "All four open rows fit on page one (20 per page), so the ordinal read needs no "
            "pagination.",
        ],
    ),
    # ------------------------------------------------------------------ 005
    dict(
        num="005", kind="ms_issue", project_id=186,
        project_path="byteblaze/a11y-syntax-highlighting",
        style="explicit", difficulty="hard", shape="retrieval_writeback",
        skills=["R2", "A2", "A12"],
        skill_chain="read the existing milestone's end date off the Milestones page -> add a day "
                    "and add thirty more to get the new window -> create the follow-up milestone "
                    "-> create the kickoff issue on it, assigned, due on the new window's first "
                    "day",
        analogues=[A_593, A_659],
        hard_criteria=["multi_mutation", "derived_target", "cross_section"],
        instruction=(
            "The a11y-syntax-highlighting repo already has a milestone called \"v1.0 polish\" "
            "and I want the follow-up scheduled back-to-back with it. Open that repo's "
            "Milestones page and read when v1.0 polish finishes. Then create a new milestone "
            "titled \"v1.1 polish\" whose start date is the day immediately after v1.0 polish "
            "ends, and whose due date is exactly 30 days after that start date. Once it exists, "
            "file an issue in the same repo titled \"Plan the v1.1 polish work\", put it on the "
            "v1.1 polish milestone, assign it to Kenton Varda, and set its due date to the "
            "milestone's start date. Leave the v1.0 polish milestone itself alone."),
        milestone=dict(title="v1.1 polish", start="2033-02-19", due="2033-03-21"),
        issue=dict(title="Plan the v1.1 polish work", due="2033-02-19",
                   assignee_id=620, assignee_name="Kenton Varda"),
        injected_milestones=[
            dict(id=601, iid=1, project_id=186, title="v1.0 polish",
                 description="Ship the last round of v1.0 contrast fixes.",
                 state="active", start_date="2033-01-09", due_date="2033-02-18",
                 created_at="2023-03-27 20:19:04.539980",
                 updated_at="2023-03-27 20:19:04.539980"),
        ],
        next_milestone_id=610,
        injected_preconditions=[
            "newMilestones: one active milestone 'v1.0 polish' (id 601, iid 1) on project 186 "
            "byteblaze/a11y-syntax-highlighting, running 2033-01-09 to 2033-02-18. No byteblaze/* "
            "project has a seeded milestone (src/data/milestones.json holds 0 rows for project "
            "ids 179-193), so without this injection there is nothing on the site for the new "
            "window to be computed from and the date would have to be stated in the instruction.",
            "nextIds.milestone bumped 590 -> 610 so the milestone the agent creates cannot "
            "collide with the injected id 601 (overlayShape.js SEED_NEXT_IDS.milestone = 590).",
        ],
        inspiration_ids=["webarena-593", "webarena-659"],
        notes=[
            "Derived window: 2033-02-18 + 1 = 2033-02-19 start; +30 days = 2033-03-21 due "
            "(February 2033 has 28 days).",
            "The injection pre-satisfies nothing: the rubric only ever looks at milestones whose "
            "id is not 601, and at a new issue that must carry the NEW milestone's id.",
            "MilestonesList.jsx:84 renders the row's date range, so the end date of v1.0 polish "
            "is legible without opening the milestone.",
        ],
    ),
    # ------------------------------------------------------------------ 006
    dict(
        num="006", kind="ms_issue", project_id=189, project_path="byteblaze/cloud-to-butt",
        style="terse", difficulty="hard", shape="mutation",
        skills=["R2", "A2", "A12"],
        skill_chain="resolve 'ending in 20 days (inclusive)' to a due date -> create the "
                    "milestone with that window -> create the kickoff issue on it, self-assigned, "
                    "carrying the same computed date",
        analogues=[A_591, A_808],
        hard_criteria=["multi_mutation", "cross_section"],
        instruction=('Time to revive cloud-to-butt. Create a milestone "keep-alive push" '
                     "starting September 5, 2031 and ending in 20 days (inclusive), then open "
                     '"Line up the keep-alive contributors" on it, assigned to me, due the '
                     "milestone's end date."),
        milestone=dict(title="keep-alive push", start="2031-09-05", due="2031-09-25"),
        issue=dict(title="Line up the keep-alive contributors", due="2031-09-25",
                   assignee_id=2330, assignee_name="Byte Blaze"),
        inspiration_ids=["webarena-591", "webarena-808"],
        notes=[
            "2031-09-05 + 20 = 2031-09-25, the official 'ending in 20 days (inclusive)' "
            "convention (webarena-591/592/594 reference answers).",
            "'assigned to me' is byteblaze, user 2330 (src/data/current_user.json); the form has "
            "an 'Assign to me' link (Controls.jsx:266) as well as the picker.",
        ],
    ),
    # ------------------------------------------------------------------ 007
    dict(
        num="007", kind="ms_issue", project_id=183, project_path="byteblaze/empathy-prompts",
        style="terse", difficulty="hard", shape="retrieval_writeback",
        skills=["R2", "R4", "A2", "A12"],
        skill_chain="resolve Q4 2033 to a start/due pair -> create the milestone -> read the "
                    "newest open issue not authored by me to identify its reporter -> create the "
                    "kickoff issue on that milestone, assigned to that reporter, due the "
                    "quarter's first day",
        analogues=[A_659, A_447],
        hard_criteria=["multi_mutation", "derived_target", "cross_section"],
        instruction=('Set up Q4 2033 on empathy-prompts: milestone "prompt refresh" spanning that '
                     'whole quarter, and issue "Collect new empathy prompts" on it, due the '
                     "quarter's first day, assigned to the reporter of the newest open issue I "
                     "didn't file."),
        milestone=dict(title="prompt refresh", start="2033-10-01", due="2033-12-31"),
        issue=dict(title="Collect new empathy prompts", due="2033-10-01",
                   assignee_id=2392, assignee_name="Greg Stucky"),
        inspiration_ids=["webarena-659", "webarena-447"],
        notes=[
            "Project 183 has six open issues; the newest is #18 (2021-06-02) by Byte Blaze "
            "himself, so the predicate 'not filed by me' selects #15 (2020-12-10) by "
            "PhilosAccounting / Greg Stucky (user 2392). The next candidate is #11 at "
            "2019-08-15, a 16-month margin. #18 is the deliberate near-miss.",
            "Q4 2033 = 2033-10-01 .. 2033-12-31.",
        ],
    ),
    # ------------------------------------------------------------------ 008
    dict(
        num="008", kind="ms", project_id=188, project_path="byteblaze/solarized-prism-theme",
        style="terse", difficulty="medium", shape="mutation",
        skills=["R2", "A2"],
        skill_chain="resolve 'the last day of that year' against the stated start -> create the "
                    "milestone with that window",
        analogues=[A_590, A_593],
        hard_criteria=None,
        instruction=('My solarized-prism-theme repo needs a milestone titled "theme contrast '
                     'pass" that starts on November 6, 2034 and runs to the last day of that '
                     "year."),
        milestone=dict(title="theme contrast pass", start="2034-11-06", due="2034-12-31"),
        inspiration_ids=["webarena-590", "webarena-593"],
        notes=[
            "Last day of 2034 = 2034-12-31, the same 'end of <year>' resolution the official "
            "webarena-658 reference answer uses (Dec 31, 2030).",
        ],
    ),
    # ------------------------------------------------------------------ 009
    dict(
        num="009", kind="issue", project_id=174, project_path="a11yproject/a11yproject.com",
        style="terse", difficulty="medium", shape="retrieval_writeback",
        skills=["R9", "A12"],
        skill_chain="look up the assignee recorded on a named issue -> create the new issue and "
                    "assign it to that same person with the stated due date",
        analogues=[A_658, A_446],
        hard_criteria=None,
        instruction=('In a11yproject.com file an issue titled "Re-check the ARIA-LIVE howto '
                     'links", due at the end of 2030, and assign it to whoever is already '
                     "assigned issue #1533 there."),
        issue=dict(title="Re-check the ARIA-LIVE howto links", due="2030-12-31",
                   assignee_id=2264, assignee_name="Roshan Jossy"),
        inspiration_ids=["webarena-658", "webarena-446"],
        notes=[
            "Issue #1533 on project 174 is the newest open issue (2023-03-22) and carries "
            "exactly one assignee, Roshan Jossy (user 2264) - so the lookup has a single "
            "answer and the row sits on page one of the open tab.",
            "'end of 2030' resolves to 2030-12-31, matching the official webarena-658 "
            "reference answer 'Dec 31, 2030'.",
        ],
    ),
    # ------------------------------------------------------------------ 010
    dict(
        num="010", kind="ms_issue", project_id=190, project_path="byteblaze/timeit",
        style="explicit", difficulty="hard", shape="retrieval_writeback",
        skills=["R1", "R2", "A2", "A12"],
        skill_chain="pick the existing milestone that ends last -> add a day to get the new "
                    "start, resolve 'the last day of 2032' to get the new due date -> create the "
                    "milestone -> create the kickoff issue on it, assigned, due the new "
                    "milestone's first day",
        analogues=[A_593, A_659],
        hard_criteria=["multi_mutation", "derived_target", "cross_section"],
        instruction=(
            "The timeit repo has a couple of hardening milestones on it already. Go to its "
            "Milestones page and find the one that finishes last. Create a new milestone titled "
            "\"1.0 hardening\" that starts the day right after that one ends and is due on the "
            "last day of 2032. Then file an issue in timeit titled \"Lock the 1.0 hardening "
            "scope\", attach it to the 1.0 hardening milestone, assign it to Dave Greene, and "
            "give it a due date equal to the new milestone's start date. Do not change the two "
            "milestones that were already there."),
        milestone=dict(title="1.0 hardening", start="2032-04-16", due="2032-12-31"),
        issue=dict(title="Lock the 1.0 hardening scope", due="2032-04-16",
                   assignee_id=2365, assignee_name="Dave Greene"),
        injected_milestones=[
            dict(id=620, iid=1, project_id=190, title="0.8 hardening",
                 description="Stabilise the timer core.", state="active",
                 start_date="2032-01-10", due_date="2032-02-20",
                 created_at="2023-03-27 20:35:31.072805",
                 updated_at="2023-03-27 20:35:31.072805"),
            dict(id=621, iid=2, project_id=190, title="0.9 hardening",
                 description="Second hardening pass before 1.0.", state="active",
                 start_date="2032-03-01", due_date="2032-04-15",
                 created_at="2023-03-27 20:35:31.072805",
                 updated_at="2023-03-27 20:35:31.072805"),
        ],
        next_milestone_id=630,
        injected_preconditions=[
            "newMilestones: two active milestones on project 190 byteblaze/timeit - '0.8 "
            "hardening' (id 620, iid 1, 2032-01-10..2032-02-20) and '0.9 hardening' (id 621, "
            "iid 2, 2032-03-01..2032-04-15). No byteblaze/* project has a seeded milestone, so "
            "without this there is no superlative to resolve. '0.8 hardening' is the distractor: "
            "it satisfies every part of the description except finishing last, by a 55-day "
            "margin.",
            "nextIds.milestone bumped 590 -> 630 so the agent's milestone cannot collide with "
            "the injected ids 620/621.",
        ],
        inspiration_ids=["webarena-593", "webarena-659"],
        notes=[
            "Superlative margin: 0.9 hardening ends 2032-04-15, 0.8 hardening ends 2032-02-20 - "
            "55 days apart, no tie. New start = 2032-04-16; new due = 2032-12-31.",
            "The action does not disturb its own retrieval premise: creating a third milestone "
            "never changes which of the two injected ones ends last, so the answer is stable "
            "throughout the episode.",
        ],
    ),
]

# --------------------------------------------------------------------------
# Shared source fragments
# --------------------------------------------------------------------------

READERS = '''

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
    return _text(value).lower()


def _created_milestones(state):
    rows = [m for m in _list(_dict(state).get("newMilestones")) if isinstance(m, dict)]
    return [m for m in rows
            if m.get("project_id") == PROJECT_ID and m.get("id") not in INJECTED_MILESTONE_IDS]


def _created_issues(state):
    rows = [i for i in _list(_dict(state).get("newIssues")) if isinstance(i, dict)]
    return [i for i in rows if i.get("project_id") == PROJECT_ID]


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

EVALUATE = '''

def evaluate(evidence):
    state = _dict(_dict(_dict(_dict(evidence).get("apps")).get("gitlab")).get("current_state"))
    components = score_state(state)
    total = round(sum(c["score"] for c in components), 6)
    return {"score": _clamp(float(total)), "components": components}
'''

NEMO_MAIN = '''

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


def constants(t):
    lines = ['PROJECT_ID = %d' % t["project_id"]]
    injected = tuple(m["id"] for m in t.get("injected_milestones") or ())
    lines.append('INJECTED_MILESTONE_IDS = %r' % (injected,))
    ms = t.get("milestone")
    if ms:
        lines.append('MILESTONE_TITLE = %r' % ms["title"].lower())
        lines.append('MILESTONE_START = %r' % ms["start"])
        lines.append('MILESTONE_DUE = %r' % ms["due"])
    iss = t.get("issue")
    if iss:
        lines.append('ISSUE_TITLE = %r' % iss["title"].lower())
        lines.append('ISSUE_DUE = %r' % iss["due"])
        lines.append('ASSIGNEE_ID = %d' % iss["assignee_id"])
    return "\n".join(lines)


WEIGHTS = {
    "ms_issue": ('COMPONENT_WEIGHTS = {\n'
                 '    "milestone_window_exact": 0.35,\n'
                 '    "kickoff_issue_on_that_milestone": 0.35,\n'
                 '    "kickoff_assignee_and_due_date": 0.3,\n'
                 '}\n'
                 'assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n'),
    "ms": ('COMPONENT_WEIGHTS = {\n'
           '    "milestone_created_with_title": 0.4,\n'
           '    "milestone_window_exact": 0.6,\n'
           '}\n'
           'assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n'),
    "issue": ('COMPONENT_WEIGHTS = {\n'
              '    "issue_filed_with_title": 0.4,\n'
              '    "issue_assigned_to_target_user": 0.35,\n'
              '    "issue_due_date_exact": 0.25,\n'
              '}\n'
              'assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n'),
}

SCORE_MS_ISSUE = '''

def score_state(state):
    milestones = _created_milestones(state)
    milestone = _one(milestones)
    milestone_ok = (milestone is not None
                    and _norm(milestone.get("title")) == MILESTONE_TITLE
                    and _text(milestone.get("start_date")) == MILESTONE_START
                    and _text(milestone.get("due_date")) == MILESTONE_DUE)

    issues = _created_issues(state)
    issue = _one(issues)
    linked = bool(milestone_ok
                  and issue is not None
                  and _norm(issue.get("title")) == ISSUE_TITLE
                  and issue.get("milestone_id") == milestone.get("id"))

    assignees = _list(issue.get("assignee_ids")) if issue is not None else []
    assigned = bool(linked
                    and assignees == [ASSIGNEE_ID]
                    and _text(issue.get("due_date")) == ISSUE_DUE)

    checks = {
        "milestone_window_exact": milestone_ok,
        "kickoff_issue_on_that_milestone": linked,
        "kickoff_assignee_and_due_date": assigned,
    }
    details = {
        "milestone_window_exact":
            "milestones created on project %d == %r" % (
                PROJECT_ID,
                [(m.get("title"), m.get("start_date"), m.get("due_date")) for m in milestones]),
        "kickoff_issue_on_that_milestone":
            "issues created on project %d == %r; milestone id == %r" % (
                PROJECT_ID,
                [(i.get("title"), i.get("milestone_id")) for i in issues],
                milestone.get("id") if milestone is not None else None),
        "kickoff_assignee_and_due_date":
            "assignee_ids == %r, due_date == %r" % (
                assignees, issue.get("due_date") if issue is not None else None),
    }
    return _build(checks, details)
'''

SCORE_MS = '''

def score_state(state):
    milestones = _created_milestones(state)
    milestone = _one(milestones)
    titled = bool(milestone is not None and _norm(milestone.get("title")) == MILESTONE_TITLE)
    window = bool(titled
                  and _text(milestone.get("start_date")) == MILESTONE_START
                  and _text(milestone.get("due_date")) == MILESTONE_DUE)

    checks = {
        "milestone_created_with_title": titled,
        "milestone_window_exact": window,
    }
    detail = "milestones created on project %d == %r" % (
        PROJECT_ID,
        [(m.get("title"), m.get("start_date"), m.get("due_date")) for m in milestones])
    details = {
        "milestone_created_with_title": detail,
        "milestone_window_exact": detail,
    }
    return _build(checks, details)
'''

SCORE_ISSUE = '''

def score_state(state):
    issues = _created_issues(state)
    issue = _one(issues)
    titled = bool(issue is not None and _norm(issue.get("title")) == ISSUE_TITLE)

    assignees = _list(issue.get("assignee_ids")) if issue is not None else []
    assigned = bool(titled and assignees == [ASSIGNEE_ID])
    dated = bool(titled and _text(issue.get("due_date")) == ISSUE_DUE)

    checks = {
        "issue_filed_with_title": titled,
        "issue_assigned_to_target_user": assigned,
        "issue_due_date_exact": dated,
    }
    details = {
        "issue_filed_with_title":
            "issues created on project %d == %r" % (
                PROJECT_ID, [i.get("title") for i in issues]),
        "issue_assigned_to_target_user": "assignee_ids == %r" % (assignees,),
        "issue_due_date_exact":
            "due_date == %r" % (issue.get("due_date") if issue is not None else None,),
    }
    return _build(checks, details)
'''

SCORERS = {"ms_issue": SCORE_MS_ISSUE, "ms": SCORE_MS, "issue": SCORE_ISSUE}


def rubric_prose(t):
    lines = []
    if t.get("milestone"):
        ms = t["milestone"]
        lines.append("Milestone: newMilestones must hold exactly one row for project %d that the"
                     % t["project_id"])
        lines.append("agent created, titled %r with start_date %s and due_date %s."
                     % (ms["title"], ms["start"], ms["due"]))
    if t.get("issue"):
        iss = t["issue"]
        lines.append("Issue: newIssues must hold exactly one row for that project, titled %r,"
                     % iss["title"])
        lines.append("with assignee_ids == [%d] (%s) and due_date %s."
                     % (iss["assignee_id"], iss["assignee_name"], iss["due"]))
        if t["kind"] == "ms_issue":
            lines.append("Its milestone_id must equal the id of the milestone the agent just")
            lines.append("created, which is only offered by NewIssue.jsx's Milestone picker once")
            lines.append("that milestone exists.")
    return "\n".join(lines)


def reward_source(t, nemo):
    head = ['"""%s reward for %s.' % ("NeMo-Gym" if nemo else "Deterministic", task_id(t)), ""]
    head.append(rubric_prose(t))
    head.append("")
    if nemo:
        head.append("Same rubric as reward.py, read from GET /go?sid=... instead of a frozen")
        head.append("evidence bundle. Prints REWARD: <float> on every output path.")
        head.append("")
        head.append("Self-contained: standard library plus `requests`.")
    else:
        head.append("Handlers: NewMilestone.jsx:64 appends to state.milestones (persisted as")
        head.append("newMilestones); NewIssue.jsx:63 appends to state.issues (persisted as")
        head.append("newIssues) carrying assignee_ids, due_date and milestone_id.")
    head.append('"""')
    parts = ["\n".join(head) + "\n"]
    if nemo:
        parts.append("import sys\n\nimport requests\n\n"
                     'SID = "__CUA_GYM_SID__"\n'
                     'BASE_URL = "%s"\n' % URL_TOKEN)
    parts.append("\n" + WEIGHTS[t["kind"]])
    parts.append("\n" + constants(t) + "\n")
    parts.append(SCORERS[t["kind"]])
    parts.append(READERS)
    parts.append(NEMO_MAIN if nemo else EVALUATE)
    return "".join(parts)


# --------------------------------------------------------------------------
# initial_setup.py
# --------------------------------------------------------------------------

SETUP_TEMPLATE = '''"""NeMo-Gym setup program for %(task_id)s.

%(why)s

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""
import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "%(url_token)s"

BASE_STATE = json.loads(r"""
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
              "label": 1927, "milestone": %(next_milestone)d, "member": 206}
}
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

# byteblaze owns no seeded milestone anywhere (src/data/milestones.json has no
# row for project ids 179-193), so the milestone(s) this task reads from have to
# be injected. iid is per-project max + 1 counting from zero, and
# nextIds.milestone clears every injected id.
INJECTED_MILESTONES = json.loads(r"""
%(milestones)s
""")


def build_state():
    """Full createInitialData() shape, so the client-side merge is a no-op."""
    state = dict(BASE_STATE)
    for created, edits, deleted in OVERLAY_COLLECTIONS:
        state[created] = []
        state[edits] = {}
        state[deleted] = []
    state["newMilestones"] = INJECTED_MILESTONES
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
        print("SETUP FAILED: baseline and current disagree after set", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


publish(build_state())
'''


def task_id(t):
    return "milestone_kickoff_%s" % t["num"]


def success_criteria(t):
    out = []
    pid = t["project_id"]
    if t.get("milestone"):
        ms = t["milestone"]
        out.append("newMilestones holds exactly one agent-created row for project %d "
                   "(%s), titled %r." % (pid, t["project_path"], ms["title"]))
        out.append("That milestone's start_date is %s and its due_date is %s."
                   % (ms["start"], ms["due"]))
    if t.get("issue"):
        iss = t["issue"]
        out.append("newIssues holds exactly one row for project %d (%s), titled %r."
                   % (pid, t["project_path"], iss["title"]))
        if t["kind"] == "ms_issue":
            out.append("That issue's milestone_id equals the id of the milestone created above.")
        out.append("That issue's assignee_ids is exactly [%d] (%s) and its due_date is %s."
                   % (iss["assignee_id"], iss["assignee_name"], iss["due"]))
    return out


def build(t):
    tid = task_id(t)
    bundle = OUT / tid
    bundle.mkdir(parents=True, exist_ok=True)

    instruction = t["instruction"]
    inst = {
        "task_id": tid,
        "task_instruction": instruction,
        "app_dir": APP_DIR,
        "start_path": "/",
        "difficulty": t["difficulty"],
        "success_criteria": success_criteria(t),
    }
    (bundle / "task_instruction.json").write_text(json.dumps(inst, indent=2) + "\n")

    meta = {
        "difficulty": t["difficulty"],
        "topic": "gitlab milestone kickoff",
        "style": t["style"],
        "shape": t["shape"],
        "skills": t["skills"],
        "skill_chain": t["skill_chain"],
        "official_analogues": t["analogues"],
        "inspiration_ids": t["inspiration_ids"],
        "authoring_notes": [
            "Grounded in hub/websites/webarena_gitlab_mock as served by the hub.",
            "start_path '/': the dashboard lists all 14 of byteblaze's projects on one page "
            "(DashboardProjects.jsx PER_PAGE 20), and Milestones is reached by clicking the "
            "project, then Issues, then Milestones (the sidebar's children only appear once "
            "the section's own page is open).",
        ] + t["notes"],
    }
    if t.get("hard_criteria"):
        meta["hard_criteria"] = t["hard_criteria"]
    if t.get("injected_preconditions"):
        meta["injected_preconditions"] = t["injected_preconditions"]

    manifest = {
        "schema_version": 2,
        "task_id": tid,
        "instruction": instruction,
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
        "metadata": meta,
    }
    (bundle / "task.json").write_text(json.dumps(manifest, indent=2) + "\n")

    (bundle / "reward.py").write_text(reward_source(t, nemo=False))
    (bundle / "nemo_reward.py").write_text(reward_source(t, nemo=True))

    setup_src = None
    if t.get("injected_milestones"):
        why = ("Injects %d pre-existing milestone(s) into newMilestones for %s so the task has a "
               "real date to compute from." % (len(t["injected_milestones"]), t["project_path"]))
        setup_src = SETUP_TEMPLATE % {
            "task_id": tid,
            "why": why,
            "url_token": URL_TOKEN,
            "next_milestone": t["next_milestone_id"],
            "milestones": json.dumps(t["injected_milestones"], indent=2),
        }
        (bundle / "initial_setup.py").write_text(setup_src)

    row = {
        "task_payload": {
            "task_id": tid,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP_DIR],
            "start_urls": [],
            "intent": instruction,
            "eval": {
                "eval_types": ["string_match"],
                "reference_answers": None,
                "note": "unused - CUA-Gym reward code is authoritative",
            },
            "cuagym": {
                "bundle_id": tid,
                "app_dir": APP_DIR,
                "initial_setup": setup_src,
                "eval_reward_code": (bundle / "nemo_reward.py").read_text(),
            },
        }
    }
    (bundle / "nemo_task.json").write_text(json.dumps(row, indent=2) + "\n")
    return row


# --------------------------------------------------------------------------
# Replay drafts
# --------------------------------------------------------------------------

REPLAY_HEAD = '''#!/usr/bin/env python3
"""Golden replay DRAFT for %(task_id)s.

Click-only: after the single landing navigation to start_path every step goes
through a rendered link, button or form control. No page.goto() and no
constructed URL (TASK4 S6).

Route taken: / -> the project row -> Issues -> Milestones -> New milestone
-> Issues -> New issue.
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


def open_issues(page):
    if PROJECT not in page.url:
        open_project(page)
    page.locator('a.shortcuts-issues[href="/%%s/-/issues"]' %% PROJECT).first.click()
    settle(page)


def open_milestones(page):
    open_issues(page)
    page.click('a[href="/%%s/-/milestones"]' %% PROJECT)
    settle(page)


def pick(page, toggle_selector, query, option_text):
    page.click(toggle_selector)
    settle(page)
    box = page.locator('input[data-qa-selector="dropdown_input_field"]').last
    box.fill(query)
    page.wait_for_timeout(400)
    page.locator("button.dropdown-item", has_text=option_text).first.click()
    settle(page)
'''

REPLAY_MILESTONE = '''

def create_milestone(page):
    open_milestones(page)
    page.click('a[title="New milestone"]')
    settle(page)
    page.fill("#milestone_title", %(ms_title)r)
    page.fill("#milestone_start_date", %(ms_start)r)
    page.fill("#milestone_due_date", %(ms_due)r)
    page.click('[data-qa-selector="create_milestone_button"]')
    settle(page)
'''

REPLAY_ISSUE = '''

def create_issue(page):
    open_issues(page)
    page.get_by_role("link", name="New issue").first.click()
    settle(page)
    page.fill("#issue_title", %(issue_title)r)
    pick(page, ".js-assignee-search", %(assignee_query)r, %(assignee_name)r)
%(milestone_pick)s    page.fill("#issuable-due-date", %(issue_due)r)
    page.click('[data-qa-selector="issuable_create_button"]')
    settle(page)
'''

REPLAY_MAIN = '''

def main():
    sid = "replay-%(num)s-" + uuid.uuid4().hex[:8]
    run_setup(sid)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(BASE + "/?sid=" + sid, wait_until="networkidle")
        settle(page)
%(body)s        browser.close()
    print("score:", score(sid))


main()
'''


def replay(t):
    tid = task_id(t)
    parts = [REPLAY_HEAD % {"task_id": tid, "project_path": t["project_path"]}]
    body = []
    if t.get("milestone"):
        ms = t["milestone"]
        parts.append(REPLAY_MILESTONE % {"ms_title": ms["title"], "ms_start": ms["start"],
                                         "ms_due": ms["due"]})
        body.append("        create_milestone(page)\n")
    if t.get("issue"):
        iss = t["issue"]
        milestone_pick = ""
        if t["kind"] == "ms_issue":
            milestone_pick = ('    pick(page, ".issue-milestone .dropdown-menu-toggle", %r, %r)\n'
                              % (t["milestone"]["title"], t["milestone"]["title"]))
        parts.append(REPLAY_ISSUE % {
            "issue_title": iss["title"],
            "assignee_query": iss["assignee_name"],
            "assignee_name": iss["assignee_name"],
            "milestone_pick": milestone_pick,
            "issue_due": iss["due"],
        })
        body.append("        create_issue(page)\n")
    parts.append(REPLAY_MAIN % {"num": t["num"], "body": "".join(body)})
    REPLAYS.mkdir(parents=True, exist_ok=True)
    (REPLAYS / (tid + ".py")).write_text("".join(parts))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    BATCH.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in TASKS:
        rows.append(build(t))
        replay(t)
    with (BATCH / "nemo_tasks.jsonl").open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    index = {"schema_version": 2,
             "tasks": [{"task_id": task_id(t), "path": "../../%s/task.json" % task_id(t)}
                       for t in TASKS]}
    (BATCH / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    print("wrote %d bundles" % len(rows))


main()
