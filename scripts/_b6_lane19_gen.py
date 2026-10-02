#!/usr/bin/env python3
"""Authoring generator for batch-6 lane 19 -- reddit, R5 -> A9, slug `all_time_top_downvote`.

Regenerates all ten bundles from the mock's own seed data. Kept in scripts/ so a
repeat of the 2026-09-01 output/tasks/reddit bulk-rewrite is recoverable.

    python3 scripts/_b6_lane19_gen.py

Writes:
    output/tasks/reddit/<task_id>/{task_instruction,task,nemo_task}.json
    output/tasks/reddit/<task_id>/{reward,nemo_reward}.py
    output/tasks/reddit/<task_id>/initial_setup.py          (tasks 1-6 only)
    output/tasks/reddit/_batches/all_time_top_downvote/{index.json,nemo_tasks.jsonl}
    output/tasks/reddit/_batches/all_time_top_downvote/replays/<task_id>.py

This script only READS hub/ seed data. It never writes under hub/.
"""
import json
import pathlib

ROOT = pathlib.Path("/home/ubuntu/CUA-Gym/output/tasks/reddit")
BATCH = ROOT / "_batches" / "all_time_top_downvote"
REPLAYS = BATCH / "replays"
SEED_PATH = pathlib.Path(
    "/home/ubuntu/CUA-Gym/hub/websites/webarena_reddit_mock/src/data/submissions.json")

SEED = json.loads(SEED_PATH.read_text())
BY_ID = {s["id"]: s for s in SEED}

# Verbatim official intents (webarena.jsonl), used only in metadata.
A714 = "Thumbs down the top 1 post ever in gadgets."
A715 = "Thumbs down the top 2 post ever in history forum."
A717 = "Thumbs down the top 4 post ever in movies."
A404 = "Upvote the newest post in books forum"
A596 = 'Subscribe to the "books" forum from the page of the all time top post in that forum.'
A598 = ('Subscribe to the "pittsburgh" forum from the page of the all time most '
        'commented post in that forum.')

TASKS = [
    # --- Top ever + All time, `ranking` demoted so Hot != Top -----------------
    dict(
        n=1, slug="aww_all_time_leader", forum="aww", sid=58888, choice=-1,
        facet="top", style="terse", inject=5112, runner=21699, hotpos=37,
        instruction=("In the aww forum, work out which submission holds the highest "
                     "score of all time and give that one a thumbs down from my account."),
        analogues=[A714, A596],
    ),
    dict(
        n=2, slug="memes_all_time_leader", forum="memes", sid=41616, choice=-1,
        facet="top", style="terse", inject=6222, runner=41321, hotpos=37,
        instruction=("The memes forum's all-time score leader needs a downvote from me. "
                     "Find whichever submission that is and thumbs it down."),
        analogues=[A714, A715],
    ),
    dict(
        n=3, slug="art_all_time_leader_upvote", forum="Art", sid=10111, choice=1,
        facet="top", style="terse", inject=9056, runner=27594, hotpos=37,
        instruction=("Find the submission with the biggest all-time score in the Art "
                     "forum and give it my upvote."),
        analogues=[A404, A596],
    ),
    dict(
        n=4, slug="gifs_all_time_leader", forum="gifs", sid=19936, choice=-1,
        facet="top", style="terse", inject=8105, runner=23874, hotpos=37,
        instruction=("Whichever post in the gifs forum has the highest score anyone "
                     "there has ever managed, thumbs it down for me."),
        analogues=[A714, A717],
    ),
    dict(
        n=5, slug="oldschoolcool_all_time_leader_upvote", forum="OldSchoolCool",
        sid=35802, choice=1, facet="top", style="explicit", inject=2254,
        runner=19214, hotpos=37,
        instruction=(
            "I want to show some appreciation in the OldSchoolCool forum. Open that "
            "forum's listing and reorder it by the top-scoring posts rather than the "
            "default view. The Top link starts on a 24-hour window that shows nothing, "
            "so widen the time range to All time. Upvote whichever submission comes out "
            "on top of that all-time ordering. Leave every other post's vote alone."),
        analogues=[A404, A596],
    ),
    dict(
        n=6, slug="photoshopbattles_all_time_leader", forum="photoshopbattles",
        sid=45340, choice=-1, facet="top", style="terse", inject=10397,
        runner=27320, hotpos=38,
        instruction=("photoshopbattles has one submission that outscores every other post "
                     "ever made there. Locate it and register a thumbs down on it from "
                     "my account."),
        analogues=[A714, A717],
    ),
    # --- Most commented + All time; no injection needed -----------------------
    dict(
        n=7, slug="jerseycity_most_discussed", forum="jerseycity", sid=127188,
        choice=-1, facet="most_commented", style="terse", inject=None,
        runner=156, hotpos=63,
        instruction=("Somewhere in the jerseycity forum is the post that has drawn more "
                     "comments than any other in its history. Find it and thumbs it down."),
        analogues=[A598, A714],
    ),
    dict(
        n=8, slug="pennsylvania_most_discussed", forum="Pennsylvania", sid=36068,
        choice=-1, facet="most_commented", style="terse", inject=None,
        runner=214, hotpos=63,
        instruction=("The Pennsylvania forum's most-discussed submission of all time - the "
                     "one carrying the largest comment count - needs my downvote. Go and "
                     "cast it."),
        analogues=[A598, A715],
    ),
    dict(
        n=9, slug="maine_most_discussed_upvote", forum="Maine", sid=99973, choice=1,
        facet="most_commented", style="explicit", inject=None, runner=201, hotpos=70,
        instruction=(
            "Over in the Maine forum I want to acknowledge the discussion that got people "
            "talking the most. Put that forum's listing on the most-commented ordering and "
            "widen the time range to All time, because the default 24-hour window comes "
            "back empty. Upvote the submission holding the largest comment count of all "
            "time there, and do not vote on anything else."),
        analogues=[A598, A404],
    ),
    dict(
        n=10, slug="nyc_most_discussed", forum="nyc", sid=66106, choice=-1,
        facet="most_commented", style="terse", inject=None, runner=223, hotpos=69,
        instruction=("Find the nyc forum's all-time most commented submission and put a "
                     "thumbs down on it for me."),
        analogues=[A598, A717],
    ),
]

FACET_LABEL = {"top": "Top", "most_commented": "Most commented"}
VOTE_WORD = {-1: "downvote", 1: "upvote"}


def task_id(t):
    return "all_time_top_downvote_%s_%03d" % (t["slug"], t["n"])


def comp_names(t):
    return ("%s_%s_target_%sd" % (t["forum"].lower(), t["facet"], VOTE_WORD[t["choice"]]),
            "vote_ledger_is_exactly_target_%s" % VOTE_WORD[t["choice"]])


REWARD_TMPL = '''"""Deterministic reward for {tid}.

Pays for submission {sid} -- the {basis},
{margin_prose} -- carrying the current user's {voteword}, and for the submission
vote ledger ending as exactly the seeded upvote on submission 1 plus that one
{voteword}.

Scored strictly off `current_state`. Nothing is compared against the episode
baseline, because a vote that is cast and then retracted leaves the ledger
entirely (AppContext.jsx:329-333 deletes the key rather than storing 0) and a
baseline diff would grade that as work.
"""

import json

EXPECTED_LEDGER = json.loads(r"""{ledger}""")

TARGET_ID = "{sid}"
TARGET_CHOICE = {choice}

COMPONENT_WEIGHTS = {{
    "{c1}": 0.7,
    "{c2}": 0.3
}}


def _submission_votes(state):
    """`votes.submissions` as {{id: choice}}, with retracted/zero rows dropped."""
    votes = state.get("votes") if isinstance(state, dict) else None
    bucket = votes.get("submissions") if isinstance(votes, dict) else None
    out = {{}}
    if isinstance(bucket, dict):
        for key, value in bucket.items():
            try:
                choice = int(value)
            except (TypeError, ValueError):
                continue
            if choice:
                out[str(key)] = choice
    return out


def score_checks(state):
    ledger = _submission_votes(state)
    voted = ledger.get(TARGET_ID) == TARGET_CHOICE
    return {{
        "{c1}": voted,
        "{c2}": voted and ledger == EXPECTED_LEDGER,
    }}


def evaluate(evidence):
    apps = evidence.get("apps") if isinstance(evidence, dict) else None
    app = None
    if isinstance(apps, dict):
        for candidate_key in ("reddit", "webarena_reddit_mock"):
            candidate = apps.get(candidate_key)
            if isinstance(candidate, dict):
                app = candidate
                break
    state = app.get("current_state") if isinstance(app, dict) else None
    if not isinstance(state, dict):
        state = {{}}

    checks = score_checks(state)
    components = []
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        satisfied = bool(checks.get(name))
        earned = weight if satisfied else 0.0
        total += earned
        components.append({{
            "name": name,
            "score": round(earned, 6),
            "details": "%s=%s" % (name, satisfied),
        }})
    return {{"score": round(total, 6), "components": components}}
'''

NEMO_REWARD_TMPL = '''"""NeMo-Gym reward program for {tid}.

Implements the same rubric as reward.py, reading `current_state` from
GET /go?sid=... instead of a frozen evidence bundle, and printing
`REWARD: <float>` on every output path including the error path.

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

EXPECTED_LEDGER = json.loads(r"""{ledger}""")

TARGET_ID = "{sid}"
TARGET_CHOICE = {choice}

COMPONENT_WEIGHTS = {{
    "{c1}": 0.7,
    "{c2}": 0.3
}}


def _submission_votes(state):
    """`votes.submissions` as {{id: choice}}, with retracted/zero rows dropped."""
    votes = state.get("votes") if isinstance(state, dict) else None
    bucket = votes.get("submissions") if isinstance(votes, dict) else None
    out = {{}}
    if isinstance(bucket, dict):
        for key, value in bucket.items():
            try:
                choice = int(value)
            except (TypeError, ValueError):
                continue
            if choice:
                out[str(key)] = choice
    return out


def score_checks(state):
    ledger = _submission_votes(state)
    voted = ledger.get(TARGET_ID) == TARGET_CHOICE
    return {{
        "{c1}": voted,
        "{c2}": voted and ledger == EXPECTED_LEDGER,
    }}


def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {{}}
    except Exception as exc:  # every path must still emit a score
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        if checks.get(name):
            total += weight
    print("COMPONENTS: " + json.dumps({{k: bool(v) for k, v in checks.items()}}, sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:  # noqa: BLE001
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''

SETUP_TMPL = '''"""NeMo-Gym setup program for {tid}.

Demotes submission {sid}'s `ranking` from {orig} to {inject} so it leaves page 1 of
f/{forum}'s default Hot listing -- it lands at position {hotpos} of {total}, i.e. page 2
at `PER_PAGE = 25` (listing.js:24) -- while its `netScore`, and therefore its
position on the all-time Top listing, is left exactly as seeded.

Why this is needed: the pristine seed sets `ranking == netScore` on 8,011 of the
8,012 submissions (CORRECTIONS #24/#25), so /f/X and /f/X/top?t=all render the
same rows in the same order in 94 of the 95 forums, and a top-ever task can be
solved without ever opening the sort menu or the time menu. With the demotion the
target is off Hot page 1 and only the Top + All time view puts it at row 1. Real
Postmill hotness decays with age, so a high-scoring older post sitting around
position {hotpos} of Hot is the ordinary case on the live site.

The record is republished WHOLE through `submissionEdits`, because
`overlay.mergeSubmissions` (utils/overlay.js:105) serves `edits[id]` verbatim in
place of the frozen row rather than patching it -- a partial record would blank
the post. It uses the corpus convention (`ranking` on the score scale), not the
epoch-seconds convention `createSubmission` writes, because the row stands in for
pre-existing corpus content.

Read-modify-write: GET /go?sid=, mutate the full document, POST it all back.
reddit REPLACES state on a partial `set`, so a partial post would leave the agent
on a working site while the reward read an almost-empty document.

Self-contained: standard library plus `requests` (in cuagym/requirements.txt).
"""

import json
import sys

import requests

SID = "__CUA_GYM_SID__"
BASE_URL = "__CUA_GYM_WEBARENA_REDDIT_URL__"

SUBMISSION_EDITS = json.loads(r"""{edits}""")


def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    payload = probe.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)
    if state.get("submissionEdits"):
        print("SETUP FAILED: baseline submissionEdits is not empty", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
    state["submissionEdits"] = SUBMISSION_EDITS

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={{"action": "set", "state": state}},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    verify = check.json()
    current = verify.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: /go returned no current_state", file=sys.stderr)
        raise SystemExit(1)
    edited = (current.get("submissionEdits") or {{}}).get("{sid}")
    if not isinstance(edited, dict) or edited.get("ranking") != {inject}:
        print("SETUP FAILED: ranking demotion did not persist", file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''

REPLAY_TMPL = '''"""Golden replay draft for {tid}.

Click-only path from `/`:
  front page -> site-nav "Forums" -> "Alphabetical" tab (ForumsNav.jsx; /forums/all
  lists all 95 forums with no pagination -- f/{forum} is not on page 1 of the
  default by-submissions index) -> the "{forum}" link -> sort dropdown
  "{facet_label}" (the link carries the source's default ?t=day, which returns zero
  rows because the corpus ends 2023-03-31) -> time dropdown "All time" -> the
  {voteword} arrow on row 1.

Row 1 of /f/{forum}/{facet}?t=all is submission {sid}. No page.goto(), no typed URL.
"""

import re


async def run(lane, task):
    page = lane.page("reddit")

    await page.get_by_role("link", name="Forums", exact=True).click()
    await page.wait_for_load_state("networkidle")

    await page.get_by_role("link", name="Alphabetical", exact=True).click()
    await page.wait_for_load_state("networkidle")

    await page.get_by_role("link", name="{forum}", exact=True).click()
    await page.wait_for_load_state("networkidle")

    # Sort dropdown -> {facet_label}. The link carries ?t=day, so the listing is empty.
    await page.get_by_role("button", name=re.compile(r"^Sort by:")).click()
    await page.get_by_role("link", name="{facet_label}", exact=True).click()
    await page.wait_for_load_state("networkidle")

    # Time dropdown -> All time.
    await page.get_by_role("button", name=re.compile(r"^From:")).click()
    await page.get_by_role("link", name="All time", exact=True).click()
    await page.wait_for_load_state("networkidle")

    first_submission = page.locator("article.submission").first
    await first_submission.get_by_role("button", name="{votebtn}").click()

    await page.wait_for_selector(
        "article.submission:first-of-type form.{voteclass}",
        state="attached",
    )
'''


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    rows = []
    index = []

    for t in TASKS:
        tid = task_id(t)
        d = ROOT / tid
        row = BY_ID[t["sid"]]
        c1, c2 = comp_names(t)
        ledger = json.dumps({"1": 1, str(t["sid"]): t["choice"]}, indent=2, sort_keys=True)
        voteword = VOTE_WORD[t["choice"]]

        if t["facet"] == "top":
            basis = ("all-time score leader in f/%s at %s points"
                     % (t["forum"], row["netScore"]))
            margin_prose = ("%s clear of the runner-up at %s"
                            % (row["netScore"] - t["runner"], t["runner"]))
        else:
            basis = ("all-time most-commented submission in f/%s at %s comments"
                     % (t["forum"], row["commentCount"]))
            margin_prose = ("%s comments clear of the runner-up at %s"
                            % (row["commentCount"] - t["runner"], t["runner"]))

        fmt = dict(tid=tid, sid=t["sid"], basis=basis, margin_prose=margin_prose,
                   voteword=voteword, ledger=ledger, choice=t["choice"], c1=c1, c2=c2)
        write(d / "reward.py", REWARD_TMPL.format(**fmt))
        write(d / "nemo_reward.py", NEMO_REWARD_TMPL.format(**fmt))

        setup_src = None
        if t["inject"] is not None:
            total = sum(1 for s in SEED if s["forum"] == t["forum"])
            rec = dict(row)
            rec["ranking"] = t["inject"]
            edits = json.dumps({str(t["sid"]): rec}, indent=2, ensure_ascii=False)
            setup_src = SETUP_TMPL.format(
                tid=tid, sid=t["sid"], orig=row["ranking"], inject=t["inject"],
                forum=t["forum"], hotpos=t["hotpos"], total=total, edits=edits)
            write(d / "initial_setup.py", setup_src)

        # ---- task_instruction.json
        if t["facet"] == "top":
            crit0 = ("votes.submissions['%s'] is %s: submission %s, the all-time score "
                     "leader in f/%s at %s points, carries the current user's %s."
                     % (t["sid"], t["choice"], t["sid"], t["forum"], row["netScore"],
                        voteword))
        else:
            crit0 = ("votes.submissions['%s'] is %s: submission %s, the all-time "
                     "most-commented post in f/%s at %s comments, carries the current "
                     "user's %s."
                     % (t["sid"], t["choice"], t["sid"], t["forum"], row["commentCount"],
                        voteword))
        crit1 = ("votes.submissions is exactly {'1': 1, '%s': %s} -- the seeded upvote on "
                 "submission 1 plus the one %s the errand asked for, and no other "
                 "submission vote." % (t["sid"], t["choice"], voteword))
        write(d / "task_instruction.json", json.dumps({
            "task_id": tid,
            "task_instruction": t["instruction"],
            "app_dir": "webarena_reddit_mock",
            "start_path": "/",
            "difficulty": "medium",
            "success_criteria": [crit0, crit1],
        }, indent=2) + "\n")

        # ---- task.json
        if t["inject"] is not None:
            injected = [
                ("submissionEdits['%s'] -- the f/%s all-time score leader, republished "
                 "whole with ranking lowered from %s to %s so it sits at position %s of "
                 "the Hot listing instead of position 1. netScore, title, author, "
                 "timestamps, image and comment count are untouched. Corpus convention "
                 "(score-scale integer, CORRECTIONS #24), not the epoch-seconds "
                 "convention createSubmission writes, because the row stands in for "
                 "pre-existing corpus content."
                 % (t["sid"], t["forum"], row["ranking"], t["inject"], t["hotpos"])),
                ("Why: the pristine seed sets ranking == netScore on 8,011 of 8,012 rows, "
                 "so /f/%s and /f/%s/top?t=all render identical orderings and the sort "
                 "and time facets would be behaviourally invisible. With the demotion the "
                 "target is off Hot page 1 (25 rows) and only Top + All time reaches it "
                 "at row 1." % (t["forum"], t["forum"])),
            ]
            chain = ("open the forum from the front door -> switch the listing sort to Top "
                     "and the time range from the link's default ?t=day (zero rows, corpus "
                     "ends 2023-03-31) to All time -> %s the row it puts first" % voteword)
        else:
            injected = []
            chain = ("open the forum from the front door -> switch the listing sort to "
                     "Most commented and the time range from the link's default ?t=day "
                     "(zero rows, corpus ends 2023-03-31) to All time -> %s the row it "
                     "puts first" % voteword)

        if t["facet"] == "top":
            derived_note = ("netScore %s vs %s for the runner-up"
                            % (row["netScore"], t["runner"]))
        else:
            derived_note = ("commentCount %s vs %s for the runner-up"
                            % (row["commentCount"], t["runner"]))

        notes = [
            "Target derived, never named: %s %r, %s." % (t["sid"], row["title"],
                                                         derived_note),
            ("Reachability from '/': site-nav Forums -> Alphabetical tab (/forums/all, "
             "all 95 forums, no pagination) -> %s -> sort dropdown '%s' (lands on ?t=day, "
             "zero rows) -> time dropdown 'All time' -> row-1 %s arrow. f/%s is not on "
             "page 1 of the default /forums index, so the Alphabetical tab is the click "
             "path." % (t["forum"], FACET_LABEL[t["facet"]], voteword, t["forum"])),
        ]
        if t["inject"] is None:
            notes.append(
                "R5 is forced without injection here: most_commented orders on "
                "commentCount (listing.js:37), a field independent of `ranking`, and "
                "submission %s sits at position %s of f/%s's default Hot listing -- off "
                "page 1. An agent that never touches the sort or time controls cannot "
                "see it." % (t["sid"], t["hotpos"], t["forum"]))
        else:
            notes.append(
                "Action-vs-premise: the %s moves netScore by 1, still far clear of the "
                "runner-up, so the superlative the instruction names is still true "
                "afterwards. The reward keys on the fixed id regardless." % voteword)

        write(d / "task.json", json.dumps({
            "schema_version": 2,
            "task_id": tid,
            "instruction": t["instruction"],
            "apps": [{
                "name": "webarena_reddit_mock",
                "source_name": "reddit",
                "base_url_env": "CUA_GYM_WEBARENA_REDDIT_URL",
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
                "style": t["style"],
                "difficulty": "medium",
                "shape": "retrieval_writeback",
                "skills": ["R5", "A9"],
                "skill_chain": chain,
                "derived_from": "top_ever_post_downvote_space_all_time_leader_001",
                "official_analogues": t["analogues"],
                "inspiration_ids": ["webarena-714", "webarena-715", "webarena-717",
                                    "webarena-404", "webarena-596", "webarena-598"],
                "topic": "all-time listing superlative reached through the sort + "
                         "time-range facets, then voted on",
                "authoring_notes": notes,
                "injected_preconditions": injected,
            },
        }, indent=2) + "\n")

        # ---- nemo_task.json
        payload = {
            "task_payload": {
                "task_id": tid,
                "dataset": "cuagym",
                "dataset_version": "v1",
                "sites": ["webarena_reddit_mock"],
                "start_urls": [],
                "intent": t["instruction"],
                "eval": {
                    "eval_types": ["string_match"],
                    "reference_answers": None,
                    "note": "unused - CUA-Gym reward code is authoritative",
                },
                "cuagym": {
                    "bundle_id": tid,
                    "app_dir": "webarena_reddit_mock",
                    "initial_setup": setup_src,
                    "eval_reward_code": (d / "nemo_reward.py").read_text(),
                },
            }
        }
        write(d / "nemo_task.json", json.dumps(payload, indent=2) + "\n")
        rows.append(json.dumps(payload))

        write(REPLAYS / (tid + ".py"), REPLAY_TMPL.format(
            tid=tid, forum=t["forum"], facet=t["facet"],
            facet_label=FACET_LABEL[t["facet"]], sid=t["sid"], voteword=voteword,
            votebtn="Downvote" if t["choice"] == -1 else "Upvote",
            voteclass="vote--user-downvoted" if t["choice"] == -1 else "vote--user-upvoted",
        ))

        index.append({"task_id": tid, "path": tid + "/task.json"})

    write(BATCH / "nemo_tasks.jsonl", "\n".join(rows) + "\n")
    write(BATCH / "index.json",
          json.dumps({"schema_version": 2, "tasks": index}, indent=2) + "\n")
    print("wrote %d bundles" % len(index))
    for i in index:
        print("  " + i["task_id"])


if __name__ == "__main__":
    main()
