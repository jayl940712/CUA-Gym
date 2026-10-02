#!/usr/bin/env python3
"""Authoring generator for batch-6 lane 17 (reddit, R4 -> A7).

Reads hub seed data, recomputes every derived slice, and writes the ten
bundles. This file is authoring tooling; it is not shipped in a bundle and is
never executed at episode time.
"""
import collections
import datetime
import json
import os

ROOT = "/home/ubuntu/CUA-Gym"
SEED = os.path.join(ROOT, "hub/websites/webarena_reddit_mock/src/data/submissions.json")
OUT = os.path.join(ROOT, "output/tasks/reddit")
BATCH = os.path.join(OUT, "_batches/active_top_titles_bio")
SLUG = "active_top_titles_bio"

SUBS = json.load(open(SEED))
BY_ID = {s["id"]: s for s in SUBS}
BY_FORUM = collections.defaultdict(list)
for _s in SUBS:
    BY_FORUM[_s["forum"]].append(_s)


def _ts(rec):
    return datetime.datetime.fromisoformat(rec["lastActive"]).timestamp()


def active_order(forum, injection):
    rows = [dict(r) for r in BY_FORUM[forum]]
    if injection:
        for r in rows:
            if r["id"] == injection["id"]:
                r["lastActive"] = injection["lastActive"]
    return sorted(rows, key=lambda r: (-_ts(r), -r["id"]))


ANALOGUE_README_3 = (
    "Create a private repository named live_a_life with a README file containing "
    "links to the 3 most active DIY posts from the DIY forum. Use the Web IDE to "
    "create the README. Structure it with the repository name as the main heading, "
    "\"Most Active DIY Threads\" as a subheading, and a bulleted list of the posts "
    "as markdown links (using their titles as link text) in the same order they "
    "appear on the forum. Commit to the default branch."
)
ANALOGUE_README_5 = (
    "Create a private repository named fun_thing_to_do with a README file containing "
    "links to the 5 most active DIY posts from the DIY forum. Use the Web IDE to "
    "create the README. Structure it with the repository name as the main heading, "
    "\"Most Active DIY Threads\" as a subheading, and a bulleted list of the posts "
    "as markdown links (using their titles as link text) in the same order they "
    "appear on the forum. Commit to the default branch."
)
ANALOGUE_README_6 = (
    "Create a private repository named Awesome_DIY_ideas with a README file containing "
    "links to the 6 most active DIY posts from the DIY forum. Use the Web IDE to "
    "create the README. Structure it with the repository name as the main heading, "
    "\"Most Active DIY Threads\" as a subheading, and a bulleted list of the posts "
    "as markdown links (using their titles as link text) in the same order they "
    "appear on the forum. Commit to the default branch."
)
BIO_A = "Change my bio to \"I am a robot\" in the discussion forum"
BIO_B = "Change my bio to \"Seeking SDE positions\" in the discussion forum"
BIO_C = "Change my bio to \"Pro Python Developer with 20 years of Experience\" in the discussion forum"
BIO_D = "Change my bio to \"Freelance Web Developer\" in the discussion forum"
BIO_E = "Change my bio to \"Awesome Prompt Artist\" in the discussion forum"
POST_NOTICE = (
    "Post a notice in f/books titled \"book reading Meet up!\". Set post details to "
    "\"virtual meetup for book reading on March 15th\""
)

DERIVED = "active_posts_into_bio_diy_active_top3_001"

TASKS = [
    {
        "n": 1,
        "name": "yonkers_active_top3_bio",
        "forum": "yonkers",
        "count": 3,
        "vessel": "bio",
        "style": "terse",
        "start_path": "/",
        "injection": None,
        "instruction": (
            "Sort f/yonkers by Active and rewrite my biography as the titles of the "
            "top 3 posts under that sort, one per line, numbered 1 to 3, most "
            "recently active first."
        ),
        "analogues": [ANALOGUE_README_3, BIO_A],
    },
    {
        "n": 2,
        "name": "stamfordct_active_top4_bio",
        "forum": "StamfordCT",
        "count": 4,
        "vessel": "bio",
        "style": "terse",
        "start_path": "/",
        "injection": {"id": 122542, "lastActive": "2023-03-31T22:10:44+00:00"},
        "instruction": (
            "In f/StamfordCT switch the listing to Active, then set my biography to "
            "the titles of the first 4 posts shown, one per line, numbered 1 to 4, "
            "in that order."
        ),
        "analogues": [ANALOGUE_README_3, BIO_B],
    },
    {
        "n": 3,
        "name": "tifu_active_top5_bio",
        "forum": "tifu",
        "count": 5,
        "vessel": "bio",
        "style": "explicit",
        "start_path": "/",
        "injection": None,
        "instruction": (
            "I want my profile to advertise what is busiest in f/tifu right now. "
            "Open the f/tifu forum, change the listing sort from Hot to Active, and "
            "read the first five posts in the order the Active listing shows them. "
            "Then open my own profile, click Edit biography, and replace the "
            "existing biography text entirely with those five titles: one title per "
            "line, each line prefixed with its rank as \"1. \", \"2. \", \"3. \", "
            "\"4. \" and \"5. \", keeping the Active order. Save the biography."
        ),
        "analogues": [ANALOGUE_README_5, BIO_C],
    },
    {
        "n": 4,
        "name": "worcesterma_active_top3_bio",
        "forum": "WorcesterMA",
        "count": 3,
        "vessel": "bio",
        "style": "terse",
        "start_path": "/",
        "injection": {"id": 123030, "lastActive": "2023-03-31T23:35:12+00:00"},
        "instruction": (
            "Open f/WorcesterMA, sort it by Active, and make my biography the titles "
            "of the top 3 posts there, one per line, numbered 1 to 3, in the order "
            "the listing shows them."
        ),
        "analogues": [ANALOGUE_README_3, BIO_D],
    },
    {
        "n": 5,
        "name": "philadelphia_active_top3_bio",
        "forum": "philadelphia",
        "count": 3,
        "vessel": "bio",
        "style": "terse",
        "start_path": "/",
        "injection": None,
        "instruction": (
            "Sort f/philadelphia by Active, then replace my biography with the "
            "titles of its top 3 posts under that sort, one per line, numbered 1 to "
            "3, in that order."
        ),
        "analogues": [ANALOGUE_README_3, BIO_E],
    },
    {
        "n": 6,
        "name": "listentothis_active_top4_bio",
        "forum": "listentothis",
        "count": 4,
        "vessel": "bio",
        "style": "terse",
        "start_path": "/",
        "injection": {"id": 106435, "lastActive": "2023-03-31T20:05:00+00:00"},
        "instruction": (
            "In f/listentothis switch the sort to Active and rewrite my biography as "
            "the titles of the first 4 posts listed, one per line, numbered 1 to 4, "
            "in that order."
        ),
        "analogues": [ANALOGUE_README_3, BIO_A],
    },
    {
        "n": 7,
        "name": "history_active_top4_bio",
        "forum": "history",
        "count": 4,
        "vessel": "bio",
        "style": "explicit",
        "start_path": "/",
        "injection": None,
        "instruction": (
            "I want my profile to show which f/history threads people are still "
            "talking about. Go to the f/history forum, use the sort control to "
            "switch the listing from Hot to Active, and note the first four posts in "
            "the order they appear. Then open my own profile, click Edit biography, "
            "and replace whatever is there with those four titles: one title per "
            "line, each line prefixed with its rank as \"1. \", \"2. \", \"3. \" and "
            "\"4. \", in the Active order. Save the biography."
        ),
        "analogues": [ANALOGUE_README_6, BIO_B],
    },
    {
        "n": 8,
        "name": "askscience_active_top3_message_smita16",
        "forum": "askscience",
        "count": 3,
        "vessel": "dm",
        "recipient": "smita16",
        "style": "terse",
        "start_path": "/user/smita16",
        "injection": None,
        "instruction": (
            "Sort f/askscience by Active, then send smita16 a private message whose "
            "body is the titles of the top 3 posts under that sort, one per line, "
            "numbered 1 to 3, in that order."
        ),
        "analogues": [ANALOGUE_README_3, BIO_A],
    },
    {
        "n": 9,
        "name": "rhodeisland_active_top3_message_getfreecash",
        "forum": "RhodeIsland",
        "count": 3,
        "vessel": "dm",
        "recipient": "GetFreeCash",
        "style": "terse",
        "start_path": "/user/GetFreeCash",
        "injection": None,
        "instruction": (
            "Send GetFreeCash a private message listing the titles of the top 3 posts "
            "in f/RhodeIsland under the Active sort, one per line, numbered 1 to 3, "
            "in that order."
        ),
        "analogues": [ANALOGUE_README_3, BIO_C],
    },
    {
        "n": 10,
        "name": "columbiamd_active_top3_roundup_post",
        "forum": "ColumbiaMD",
        "count": 3,
        "vessel": "post",
        "post_title": "Active thread roundup",
        "style": "terse",
        "start_path": "/",
        "injection": {"id": 118547, "lastActive": "2023-03-31T20:40:00+00:00"},
        "instruction": (
            "Switch f/ColumbiaMD to the Active sort, then post there under the title "
            "\"Active thread roundup\", with a body listing the top 3 titles under "
            "that sort, one per line, numbered 1 to 3, in order."
        ),
        "analogues": [ANALOGUE_README_3, POST_NOTICE],
    },
]

PUNCT_JSON = """{
  "\\u2018": "'", "\\u2019": "'", "\\u201a": "'", "\\u201b": "'",
  "\\u201c": "\\"", "\\u201d": "\\"", "\\u201e": "\\"",
  "\\u2013": "-", "\\u2014": "-", "\\u2212": "-", "\\u2010": "-",
  "\\u00a0": " ", "\\u2026": "..."
}"""

SHARED_HELPERS = '''
PUNCT = json.loads(r"""%s""")


def _map_punct(text):
    return "".join(PUNCT.get(ch, ch) for ch in text)


def _flat(raw):
    """Whole value, punctuation-normalised, whitespace-collapsed, lowercased."""
    if not isinstance(raw, str):
        return ""
    return re.sub(r"\\s+", " ", _map_punct(raw)).strip().lower()


MARKER = re.compile(r"^\\s*(?:\\d{1,2}\\s*[\\.\\)\\-:]\\s*|[-*+\\u2022]\\s+)")


def _lines(raw):
    """Non-empty content lines with any list marker removed."""
    if not isinstance(raw, str):
        return []
    out = []
    for line in _map_punct(raw).replace("\\r", "\\n").split("\\n"):
        stripped = MARKER.sub("", line)
        if not stripped.strip():
            stripped = line
        cleaned = re.sub(r"\\s+", " ", stripped).strip().lower()
        if cleaned:
            out.append(cleaned)
    return out


EXPECTED_NORM = [_flat(entry) for entry in EXPECTED]


def _entries_in_order(raw):
    """Every expected title occurs in the value, in the required order."""
    flat = _flat(raw)
    if not flat:
        return False
    cursor = 0
    for entry in EXPECTED_NORM:
        found = flat.find(entry, cursor)
        if found < 0:
            return False
        cursor = found + len(entry)
    return True


def _is_exactly_the_list(raw):
    """The value is those titles, one per line, in order, and nothing else."""
    return _lines(raw) == EXPECTED_NORM
''' % PUNCT_JSON


def vessel_reader(task):
    v = task["vessel"]
    if v == "bio":
        return '''
def _candidates(state):
    """The recorded biography (updateBio, AppContext.jsx:622)."""
    user = state.get("currentUser") if isinstance(state, dict) else None
    if not isinstance(user, dict):
        return []
    value = user.get("biography")
    return [value] if isinstance(value, str) else []
'''
    if v == "dm":
        return '''
RECIPIENT = "%s"


def _candidates(state):
    """Bodies of messages in a thread whose participants include RECIPIENT."""
    threads = state.get("messages") if isinstance(state, dict) else None
    if not isinstance(threads, list):
        return []
    out = []
    for thread in threads:
        if not isinstance(thread, dict):
            continue
        participants = thread.get("participants")
        if not isinstance(participants, list):
            continue
        names = [p.lower() for p in participants if isinstance(p, str)]
        if RECIPIENT.lower() not in names:
            continue
        messages = thread.get("messages")
        if not isinstance(messages, list):
            continue
        for message in messages:
            if isinstance(message, dict) and isinstance(message.get("body"), str):
                out.append(message["body"])
    return out
''' % task["recipient"]
    return '''
FORUM = "%s"
POST_TITLE = "%s"


def _candidates(state):
    """Bodies of agent-created submissions in FORUM titled POST_TITLE."""
    created = state.get("newSubmissions") if isinstance(state, dict) else None
    if not isinstance(created, list):
        return []
    want = _flat(POST_TITLE)
    out = []
    for record in created:
        if not isinstance(record, dict):
            continue
        forum = record.get("forum")
        if not isinstance(forum, str) or forum.strip().lower() != FORUM.lower():
            continue
        if _flat(record.get("title")) != want:
            continue
        body = record.get("body")
        out.append(body if isinstance(body, str) else "")
    return out
''' % (task["forum"], task["post_title"])


SCORER = '''
def score_checks(state):
    best = (False, False)
    for raw in _candidates(state):
        ordered = _entries_in_order(raw)
        exact = bool(ordered and _is_exactly_the_list(raw))
        if (exact, ordered) > (best[1], best[0]):
            best = (ordered, exact)
    return {
        ORDER_COMPONENT: best[0],
        EXACT_COMPONENT: best[1],
    }
'''


def vessel_phrase(task):
    v = task["vessel"]
    if v == "bio":
        return "currentUser.biography"
    if v == "dm":
        return "a private-message body in a thread with %s" % task["recipient"]
    return 'the body of the new f/%s submission titled "%s"' % (task["forum"], task["post_title"])


def build(task):
    order = active_order(task["forum"], task["injection"])
    top = order[: task["count"]]
    runner = order[task["count"]]
    titles = [r["title"] for r in top]
    margin = int(_ts(top[-1]) - _ts(runner))
    hot = sorted(BY_FORUM[task["forum"]], key=lambda r: (-r["ranking"], -r["id"]))
    hot_titles = [r["title"] for r in hot[: task["count"]]]
    task_id = "%s_%s_%03d" % (SLUG, task["name"], task["n"])
    return {
        "task": task,
        "task_id": task_id,
        "titles": titles,
        "runner": runner,
        "margin": margin,
        "hot_titles": hot_titles,
        "top": top,
    }


def reward_py(b):
    t = b["task"]
    expected = json.dumps(b["titles"], ensure_ascii=False, indent=2)
    doc = (
        '"""Deterministic reward for %s.\n\n'
        "The agent reads f/%s under the Active sort (listing.js:34 orders it by\n"
        "lastActive DESC, id DESC), takes rows 1-%d in order, and records those\n"
        "titles in %s.\n\n"
        "Both components are positive statements about the value the agent\n"
        "recorded. Nothing is paid for a record being left alone, and nothing is\n"
        "read but the app's current state. The pristine session holds no such\n"
        "value, so an untouched run scores 0.0.\n"
        '"""\n'
    ) % (b["task_id"], t["forum"], t["count"], vessel_phrase(t))
    return (
        doc
        + "\nimport json\nimport re\n\nEXPECTED = json.loads(r\"\"\"%s\"\"\")\n\n"
        "ORDER_COMPONENT = \"titles_recorded_in_active_order\"\n"
        "EXACT_COMPONENT = \"value_is_exactly_the_ordered_titles\"\n\n"
        "COMPONENT_WEIGHTS = {\n    ORDER_COMPONENT: 0.6,\n    EXACT_COMPONENT: 0.4,\n}\n"
        "assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n"
        % expected
        + SHARED_HELPERS
        + vessel_reader(t)
        + SCORER
        + '''

def _details(state, name, satisfied):
    recorded = [_flat(raw) for raw in _candidates(state)]
    return "component=%s satisfied=%s expected=%r recorded=%r" % (
        name, satisfied, EXPECTED_NORM, recorded,
    )


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
        state = {}

    checks = score_checks(state)
    components = []
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        satisfied = bool(checks.get(name))
        earned = weight if satisfied else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": _details(state, name, satisfied),
        })
    return {"score": round(total, 6), "components": components}
'''
    )


def nemo_reward_py(b):
    t = b["task"]
    expected = json.dumps(b["titles"], ensure_ascii=False, indent=2)
    doc = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Same rubric as reward.py, reading the app's current state from\n"
        "GET /go?sid= instead of a frozen evidence bundle, and printing\n"
        "`REWARD: <float>` on every output path including the error path.\n\n"
        "Self-contained: standard library plus `requests`.\n"
        '"""\n'
    ) % b["task_id"]
    return (
        doc
        + "\nimport json\nimport re\nimport sys\n\nimport requests\n\n"
        "SID = \"__CUA_GYM_SID__\"\n"
        "BASE_URL = \"__CUA_GYM_WEBARENA_REDDIT_URL__\"\n\n"
        "EXPECTED = json.loads(r\"\"\"%s\"\"\")\n\n"
        "ORDER_COMPONENT = \"titles_recorded_in_active_order\"\n"
        "EXACT_COMPONENT = \"value_is_exactly_the_ordered_titles\"\n\n"
        "COMPONENT_WEIGHTS = {\n    ORDER_COMPONENT: 0.6,\n    EXACT_COMPONENT: 0.4,\n}\n"
        % expected
        + SHARED_HELPERS
        + vessel_reader(t)
        + SCORER
        + '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:  # every path must still emit a score
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        if checks.get(name):
            total += weight
    print("COMPONENTS: " + json.dumps(
        {key: bool(value) for key, value in checks.items()}, sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''
    )


def setup_py(b):
    t = b["task"]
    inj = t["injection"]
    record = dict(BY_ID[inj["id"]])
    record["lastActive"] = inj["lastActive"]
    edits = {str(inj["id"]): record}
    doc = (
        '"""NeMo-Gym setup program for %s.\n\n'
        "Republishes frozen submission %d (f/%s, %r) through `submissionEdits`\n"
        "with `lastActive` moved to %s and every other field left at its seeded\n"
        "value -- exactly the record shape `patchSubmission` writes\n"
        "(src/utils/overlay.js:238). The effect is the one a fresh comment has:\n"
        "the thread rises in the Active listing (listing.js:34 sorts on\n"
        "lastActive DESC) while Hot, New and Top are untouched, so the correct\n"
        "answer differs from the pristine seed and cannot be memorised.\n\n"
        "Read-modify-write: the pristine document is fetched from /go, only this\n"
        "one key is changed, and the whole object is posted back, because reddit\n"
        "REPLACES state on a partial `set`.\n\n"
        "Self-contained: standard library plus `requests`.\n"
        '"""\n'
    ) % (b["task_id"], inj["id"], t["forum"], record["title"], inj["lastActive"])
    return (
        doc
        + "\nimport json\nimport sys\n\nimport requests\n\n"
        "SID = \"__CUA_GYM_SID__\"\n"
        "BASE_URL = \"__CUA_GYM_WEBARENA_REDDIT_URL__\"\n\n"
        "SUBMISSION_EDITS = json.loads(r\"\"\"%s\"\"\")\n"
        % json.dumps(edits, ensure_ascii=False, indent=2)
        + '''

def main():
    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    payload = probe.json()
    state = payload.get("current_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        state = payload.get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        print("SETUP FAILED: no baseline document to patch", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
    existing = state.get("submissionEdits")
    merged = dict(existing) if isinstance(existing, dict) else {}
    merged.update(SUBMISSION_EDITS)
    state["submissionEdits"] = merged

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    result = check.json()
    current = result.get("current_state")
    if not isinstance(current, dict):
        print("SETUP FAILED: /go returned no current_state", file=sys.stderr)
        raise SystemExit(1)
    for key in SUBMISSION_EDITS:
        if key not in (current.get("submissionEdits") or {}):
            print("SETUP FAILED: submissionEdits missing " + key, file=sys.stderr)
            raise SystemExit(1)
    print("SETUP OK")


if __name__ == "__main__":
    main()
'''
    )


def replay_py(b):
    t = b["task"]
    lines = "\\n".join(
        "%d. %s" % (i + 1, title.replace("\\", "\\\\").replace('"', '\\"'))
        for i, title in enumerate(b["titles"])
    )
    header = (
        "# Golden replay DRAFT for %s.\n"
        "# Not executed during authoring. Clicks only -- no typed URLs.\n"
        "# Retrieval: f/%s -> sort control -> Active -> read rows 1-%d.\n"
        "# Writeback: %s\n\n"
        "VALUE = \"%s\"\n\n"
    ) % (b["task_id"], t["forum"], t["count"], vessel_phrase(t), lines)

    nav = (
        "def run(page, base):\n"
        "    page.goto(base + \"%s\")\n"
        "    page.get_by_role(\"link\", name=\"Forums\").first.click()\n"
        "    page.get_by_role(\"link\", name=\"Alphabetical\").first.click()\n"
        "    page.get_by_role(\"link\", name=\"%s\", exact=True).first.click()\n"
        "    page.get_by_role(\"link\", name=\"Active\", exact=True).first.click()\n"
        "    page.wait_for_load_state(\"networkidle\")\n"
    ) % (t["start_path"], t["forum"])

    if t["vessel"] == "bio":
        tail = (
            "    page.get_by_role(\"button\", name=\"MarvelsGrantMan136\").first.click()\n"
            "    page.get_by_role(\"link\", name=\"Profile\").first.click()\n"
            "    page.get_by_role(\"link\", name=\"Edit biography\").first.click()\n"
            "    field = page.locator(\"#user_biography_biography\")\n"
            "    field.fill(VALUE)\n"
            "    page.get_by_role(\"button\", name=\"Save\").first.click()\n"
            "    page.wait_for_load_state(\"networkidle\")\n"
        )
    elif t["vessel"] == "dm":
        tail = (
            "    # back to the profile the episode started on\n"
            "    while page.locator(\"a:has-text('Send message')\").count() == 0:\n"
            "        page.go_back()\n"
            "        page.wait_for_load_state(\"networkidle\")\n"
            "    page.get_by_role(\"link\", name=\"Send message\").first.click()\n"
            "    page.locator(\"#message_body\").fill(VALUE)\n"
            "    page.get_by_role(\"button\", name=\"Send\").first.click()\n"
            "    page.wait_for_load_state(\"networkidle\")\n"
        )
    else:
        tail = (
            "    page.get_by_role(\"link\", name=\"Submit\").first.click()\n"
            "    page.locator(\"#submission_title\").fill(\"%s\")\n"
            "    page.locator(\"#submission_body\").fill(VALUE)\n"
            "    page.locator(\"#submission_forum\").select_option(label=\"%s\")\n"
            "    page.get_by_role(\"button\", name=\"Create submission\").first.click()\n"
            "    page.wait_for_load_state(\"networkidle\")\n"
        ) % (t["post_title"], t["forum"])
    return header + nav + tail


def notes(b):
    t = b["task"]
    out = [
        "f/%s Active slice recomputed from src/data/submissions.json: rows 1-%d are ids %s; "
        "row %d is id %d at %s, a %d-second margin below the scored slice, so the ordinal "
        "selection is unambiguous."
        % (
            t["forum"],
            t["count"],
            ", ".join(str(r["id"]) for r in b["top"]),
            t["count"] + 1,
            b["runner"]["id"],
            b["runner"]["lastActive"],
            b["margin"],
        ),
        "Shortcut defeated: the default Hot listing's first %d titles are %r, a different "
        "list, so an agent that never touches the sort control scores 0.0."
        % (t["count"], b["hot_titles"]),
        "Grounded in webarena_reddit_mock @ hub/websites/webarena_reddit_mock; the Active "
        "ordering is listing.js:34 (lastActive DESC, id DESC) and /f/<forum>/active carries "
        "no ?t= interval, so no time filter applies.",
        "The cited README analogues write the derived list into a GITLAB repo. CuaGymTaskInfo "
        "carries one app_dir and the reddit mock has no cross-origin access, so the vessel is "
        "re-pointed at a reddit surface; the retrieval half is unchanged. The deviation is "
        "recorded in GENERATION.md.",
        "Both reward programs read the app's current state only and gate on the recorded "
        "value, never on 'the field was edited'.",
    ]
    if t["injection"]:
        rec = BY_ID[t["injection"]["id"]]
        out.insert(
            1,
            "Precondition injected: submission %d (%r) is republished through submissionEdits "
            "with lastActive %s -> %s. lastActive is never rendered (Time.jsx shows timestamp), "
            "so no screen contradicts itself; the only observable is row position, and the "
            "pristine-seed answer is now wrong."
            % (rec["id"], rec["title"], rec["lastActive"], t["injection"]["lastActive"]),
        )
    return out


def write(b):
    t = b["task"]
    d = os.path.join(OUT, b["task_id"])
    os.makedirs(d, exist_ok=True)

    crit = [
        "%s records the %d f/%s Active titles in order: %s."
        % (vessel_phrase(t).capitalize(), t["count"], t["forum"], json.dumps(b["titles"], ensure_ascii=False)),
        "Split into non-empty lines with any '1.'-style marker removed, that value is exactly "
        "those %d titles in that order and nothing else." % t["count"],
        "Comparison normalises typographic punctuation and collapses whitespace; a different "
        "set of titles, a different order, or the inclusion of row %d (%r) scores below 1.0."
        % (t["count"] + 1, b["runner"]["title"]),
    ]
    with open(os.path.join(d, "task_instruction.json"), "w") as fh:
        json.dump(
            {
                "task_id": b["task_id"],
                "task_instruction": t["instruction"],
                "app_dir": "webarena_reddit_mock",
                "start_path": t["start_path"],
                "difficulty": "medium",
                "success_criteria": crit,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    manifest = {
        "schema_version": 2,
        "task_id": b["task_id"],
        "instruction": t["instruction"],
        "apps": [
            {
                "name": "webarena_reddit_mock",
                "source_name": "reddit",
                "base_url_env": "CUA_GYM_WEBARENA_REDDIT_URL",
                "start_path": t["start_path"],
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
            "style": t["style"],
            "difficulty": "medium",
            "shape": "retrieval_writeback",
            "skills": ["R4", "A7"],
            "skill_chain": (
                "read the titles of the top %d posts of f/%s under the Active ordering -> "
                "compose them, in that order, into %s"
            )
            % (t["count"], t["forum"], vessel_phrase(t)),
            "derived_from": DERIVED,
            "official_analogues": t["analogues"],
            "injected_preconditions": (
                [
                    "submissionEdits[%d]: f/%s submission %r republished with lastActive=%s "
                    "(all other seed fields unchanged) so the Active ordering, and therefore "
                    "the correct answer, differs from the pristine seed."
                    % (
                        t["injection"]["id"],
                        t["forum"],
                        BY_ID[t["injection"]["id"]]["title"],
                        t["injection"]["lastActive"],
                    )
                ]
                if t["injection"]
                else []
            ),
            "topic": SLUG,
            "surface": "f/%s, sort Active" % t["forum"],
            "inspiration_ids": ["webarena-563", "webarena-564", "webarena-399", "webarena-403"],
            "authoring_notes": notes(b),
        },
    }
    with open(os.path.join(d, "task.json"), "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(os.path.join(d, "reward.py"), "w") as fh:
        fh.write(reward_py(b))
    nemo_reward = nemo_reward_py(b)
    with open(os.path.join(d, "nemo_reward.py"), "w") as fh:
        fh.write(nemo_reward)

    setup_src = None
    if t["injection"]:
        setup_src = setup_py(b)
        with open(os.path.join(d, "initial_setup.py"), "w") as fh:
            fh.write(setup_src)

    row = {
        "task_payload": {
            "task_id": b["task_id"],
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
                "bundle_id": b["task_id"],
                "app_dir": "webarena_reddit_mock",
                "initial_setup": setup_src,
                "eval_reward_code": nemo_reward,
            },
        }
    }
    with open(os.path.join(d, "nemo_task.json"), "w") as fh:
        json.dump(row, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    with open(os.path.join(BATCH, "replays", b["task_id"] + ".py"), "w") as fh:
        fh.write(replay_py(b))
    return row


def main():
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    built = [build(t) for t in TASKS]
    rows = [write(b) for b in built]
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(os.path.join(BATCH, "index.json"), "w") as fh:
        json.dump(
            {
                "schema_version": 2,
                "tasks": [
                    {"task_id": b["task_id"], "path": "../../%s/task.json" % b["task_id"]}
                    for b in built
                ],
            },
            fh,
            indent=2,
        )
        fh.write("\n")
    for b in built:
        print(
            b["task_id"],
            "| n=%d margin=%ds" % (b["task"]["count"], b["margin"]),
            "| runner=%r" % b["runner"]["title"],
        )
        print("   titles:", json.dumps(b["titles"], ensure_ascii=False))
        print("   words:", len(b["task"]["instruction"].split()), b["task"]["style"])


if __name__ == "__main__":
    main()
