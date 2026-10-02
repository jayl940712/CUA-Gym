#!/usr/bin/env python3
"""Emit the batch-5 lane-23 reddit bundles (slug image_repost_cross_forum)."""
import json, os, re, unicodedata

ROOT = "/home/ubuntu/CUA-Gym/output/tasks/reddit"
BATCH = os.path.join(ROOT, "_batches", "image_repost_cross_forum")
APP = "webarena_reddit_mock"
ENV = "CUA_GYM_WEBARENA_REDDIT_URL"
PLACEHOLDER = "__CUA_GYM_WEBARENA_REDDIT_URL__"

ANALOGUES = {
    "eagle": 'Re-post the image of Bald Eagle from this forum to connecticut forum using the image URL and title "from /f/pics"',
    "turkey": 'Re-post the image of Thanksgiving turkey from this forum to funny forum using the image URL and title "from /f/pics"',
    "firework": 'Re-post the image of Firework from this forum to news forum using the image URL and title "from /f/pics"',
    "wife": 'Re-post the image of Wife\'s costume from this forum to funny forum using the image URL and title "from /f/pics"',
    "contest": 'Re-post the image of costume contest from this forum to funny forum using the image URL and title "from /f/pics"',
}
A = ANALOGUES


def slugify(title, maxlen=60):
    words = [w for w in re.split(r"[^\w]+", title.lower(), flags=re.UNICODE) if w]
    slug, ln = "", 0
    for w in words:
        add = ("-" + w) if ln > 0 else w
        ln += len(add)
        if ln > maxlen:
            break
        slug += add
    return slug or "-"


# --------------------------------------------------------------------------
# Injected records. Field set copied from the seeded pics rows (image posts
# carry id/forum/author/title/timestamp/lastActive/ranking/netScore/
# commentCount/image/imageWidth/imageHeight/slug/userFlag; link posts swap
# image* for url) and from createSubmission (AppContext.jsx:384).
# --------------------------------------------------------------------------
def image_row(sid, author, title, ts, last, score, comments, image, w, h, flag,
              forum="pics"):
    return {
        "id": sid, "forum": forum, "author": author, "title": title,
        "timestamp": ts, "lastActive": last, "ranking": score, "netScore": score,
        "commentCount": comments, "image": image, "imageWidth": w,
        "imageHeight": h, "slug": slugify(title), "userFlag": flag,
    }


def link_row(sid, author, title, url, ts, last, score, comments, flag, forum="pics"):
    return {
        "id": sid, "forum": forum, "author": author, "title": title, "url": url,
        "timestamp": ts, "lastActive": last, "ranking": score, "netScore": score,
        "commentCount": comments, "slug": slugify(title), "userFlag": flag,
    }


DISTRACTOR_007 = link_row(
    190001, "GriddleGossip",
    "Someone recreated the McDonald's Filet-O-Fish as an oil painting for a gallery show",
    "https://www.thetakeout.com/filet-o-fish-oil-painting-gallery-show",
    "2023-03-04T15:12:48+00:00", "2023-03-06T09:41:02+00:00", 5200, 143, "t3_11ip2qk")

TOPPOST_008 = image_row(
    190003, "trailmix_tabby", "My rescue kitten fell asleep in my hiking boot",
    "2023-03-12T18:04:11+00:00", "2023-03-15T02:20:57+00:00", 7600, 412,
    "237938149f59a0e16d372735c36c36071a8f91f08d62e7fd37cfe9036e53e5a9.png",
    720, 960, "t3_11q4x8d")

RIVAL_010 = image_row(
    190004, "sedationDentist",
    "the dentist lamp at my orthodontist is a dead ringer for a water buffalo",
    "2023-02-09T11:37:26+00:00", "2023-02-11T04:02:19+00:00", 3900, 118,
    "aae330997594c424ea65fb097bdc50022202f833201254ca9729d602af29c317.jpg",
    2000, 1500, "t3_10y7fzb")


TASKS = [
 dict(
  n=1, key="rainbow_lobster_aww",
  diff="medium", style="terse", skills=["R6", "A7"],
  chain="search /f/pics for the rainbow-lobster photo -> read the image URL off the "
        "expanded post -> carry it into a new submission in /f/aww",
  analogues=[A["eagle"]],
  instruction='In /f/pics there is a photo of a tropical rainbow lobster. Re-post that '
              'image to the aww forum using the image\'s own URL, with the title "from /f/pics".',
  src_id=89308, src_title="The tropical “Rainbow Lobster” (Panulirus ornatus)",
  src_author="fluffy_squidtooth",
  image="d3333ad4839961f9f765b514279fc0730c9c7fee194ecd3fd069e3f15ef86234.jpg",
  dests=["aww"], title="from /f/pics", body_author=None,
  setup_rows=[], variant="single",
  notes="Search probe over the seeded corpus: the token-AND substring matcher in "
        "SearchPage.jsx:65-78 returns exactly one submission and zero comments for "
        "'rainbow lobster', so the target is unambiguous.",
 ),
 dict(
  n=2, key="romanian_pizza_food",
  diff="medium", style="terse", skills=["R6", "A7"],
  chain="search /f/pics for the Romanian pizza parlour photo -> read its image URL -> "
        "carry it into a new submission in /f/food",
  analogues=[A["turkey"]],
  instruction='Someone posted a photo of a Romanian pizza parlor in /f/pics. Re-post that '
              'image to the food forum using its image URL, titled "x-post from /f/pics".',
  src_id=67179, src_title="Just A Romanian Pizza Parlor.", src_author="StinkyPoopsAlot",
  image="ae76c9d3121b83c91176990b94e9b3d67dc7c9b444ac3571fea5634e37bfc788.jpg",
  dests=["food"], title="x-post from /f/pics", body_author=None,
  setup_rows=[], variant="single",
  notes="'romanian pizza' returns exactly one submission and no comments.",
 ),
 dict(
  n=3, key="top_ever_pics_food",
  diff="hard", style="terse", skills=["R4", "R9", "A7", "A2"],
  chain="rank /f/pics by score to pick out the single highest-scoring post ever -> read "
        "its image URL and its byline off the post page -> compose a submission in "
        "/f/food carrying both",
  analogues=[A["turkey"], A["contest"]],
  hard_criteria=["derived_target", "cross_section"],
  instruction='Find the highest-scoring post of all time in /f/pics; it is an image post. '
              'Re-post that image to the food forum with the title "from /f/pics" and the '
              "original poster's username in the body.",
  src_id=45604, src_title="A Trejo Thanksgiving.", src_author="DinoRoman",
  image="2e4fa0a328e653a97a7d07046291c298ef5b4e0d0c73a287f317ca86a8e8685f.jpg",
  dests=["food"], title="from /f/pics", body_author="DinoRoman",
  setup_rows=[], variant="single_body",
  notes="Tie check: /f/pics top-ever is 45604 at netScore 7522, runner-up 110715 at "
        "7502 - margin 20, no tie. The action creates a post in /f/food and cannot "
        "move the /f/pics ranking that selected the target.",
 ),
 dict(
  n=4, key="petra_puppy_aww",
  diff="medium", style="explicit", skills=["R6", "A7"],
  chain="search /f/pics for the Petra puppy photo -> read its image URL -> file a new "
        "submission in /f/aww carrying that URL",
  analogues=[A["eagle"]],
  instruction=(
    "A photo in /f/pics shows a puppy posing in front of Petra. Find that post, take the "
    "address of the picture it displays, and re-publish it in the aww forum: open the "
    "submit form, choose aww, set the title to exactly \"Spotted in /f/pics\", and put the "
    "picture's address in the URL field. The submit form only accepts a full web address "
    "beginning with http:// or https://, so make sure what you paste is one."),
  src_id=45628, src_title="A Puppy Posed For Me In Front Of Petra",
  src_author="los_krompiros",
  image="6ee37fb218ee800920f0ded1e6c90b3087cc2a8459ffa9a672cec055fb3f2c01.jpg",
  dests=["aww"], title="Spotted in /f/pics", body_author=None,
  setup_rows=[], variant="single",
  notes="'puppy petra' returns exactly one submission. Explicit style: the instruction "
        "names the http(s) requirement, which is the one thing about this flow a "
        "competent user could NOT work out before the form rejects them.",
 ),
 dict(
  n=5, key="pizza_stone_moon_mildlyinteresting",
  diff="medium", style="terse", skills=["R6", "A7"],
  chain="search /f/pics for the worn pizza-stone photo -> read its image URL -> carry it "
        "into a new submission in /f/mildlyinteresting",
  analogues=[A["firework"]],
  instruction='/f/pics has a photo of a pizza stone that ended up looking like the moon. '
              'Re-post that image into the mildlyinteresting forum by its image URL, with '
              'the title "from /f/pics".',
  src_id=45586, src_title="After five years of use my pizza stone looks like the moon.",
  src_author="chestertravis",
  image="8e051f883e2da450758bed5d0760b24b039dd618566d52be9c0ff6c8f75c71b8.jpg",
  dests=["mildlyinteresting"], title="from /f/pics", body_author=None,
  setup_rows=[], variant="single",
  notes="'pizza stone' returns two submissions, only one of them in /f/pics; "
        "'pizza stone moon' returns exactly one.",
 ),
 dict(
  n=6, key="mona_lisa_dual_repost",
  diff="hard", style="terse", skills=["R6", "A7", "A2"],
  chain="search /f/pics for the Etch A Sketch Mona Lisa -> read its image URL once -> "
        "file that same URL as two separate submissions, in /f/Art and in "
        "/f/mildlyinteresting",
  analogues=[A["contest"], A["wife"]],
  hard_criteria=["multi_mutation", "cross_section"],
  instruction='Someone in /f/pics etched the Mona Lisa on an Etch A Sketch. Re-post that '
              'image to both the Art forum and the mildlyinteresting forum, each titled '
              '"from /f/pics".',
  src_id=45680, src_title="It took 30+ hours for me to etch a sketch the Mona Lisa [OC]",
  src_author="Pikajane",
  image="c1dfd44a4ab4e3c3196c10f3c9d115c8df06e80b1f9a1cd3dd65ba703ec78866.jpg",
  dests=["Art", "mildlyinteresting"], title="from /f/pics", body_author=None,
  setup_rows=[], variant="dual",
  notes="'mona lisa' returns one submission plus one comment; the submission is the "
        "/f/pics target. One retrieval feeds two independent creations.",
 ),
 dict(
  n=7, key="filet_o_fish_photo_not_link",
  diff="hard", style="terse", skills=["R6", "R9", "A7", "A2"],
  chain="search /f/pics for the Filet-O-Fish oil painting -> reject the higher-ranked "
        "link post and keep the image post -> read its image URL and byline -> compose a "
        "submission in /f/food carrying both",
  analogues=[A["turkey"], A["eagle"]],
  hard_criteria=["derived_target", "cross_section"],
  instruction="In /f/pics there is an image post of an oil painting of a McDonald's "
              'Filet-O-Fish. Re-post that image to the food forum, title "from /f/pics", '
              "and name its original poster in the body.",
  src_id=25017, src_title="My oil painting of McDonald’s Filet-O-Fish",
  src_author="NoahVerrier",
  image="00d2341392f787ba15960934bea08a81090053c0ac17458c37c743a2eacb9f66.jpg",
  dests=["food"], title="from /f/pics", body_author="NoahVerrier",
  setup_rows=[DISTRACTOR_007], variant="single_body",
  injected=["newSubmissions gains one seeded-shaped LINK post in /f/pics, id 190001 by "
            "GriddleGossip at netScore 5200, whose title also carries the tokens 'oil "
            "painting' and 'Filet-O-Fish'. Search orders title hits by netScore DESC "
            "(SearchPage.jsx:72-77), so the distractor is the FIRST result and the "
            "image post the agent needs is the second. It has no image, so an agent "
            "that grabs the top hit transfers an external news URL and scores 0."],
  notes="Distractor scores 5200 vs the target's 4056 - the wrong record is deliberately "
        "ranked above the right one. Nothing injected satisfies any component: the "
        "rubric needs a NEW row in /f/food titled 'from /f/pics'.",
 ),
 dict(
  n=8, key="injected_top_ever_dual_repost",
  diff="hard", style="terse", skills=["R4", "A7", "A2"],
  chain="rank /f/pics by score to find the single highest-scoring post -> read its image "
        "URL -> file that URL as two separate submissions, in /f/aww and in /f/funny",
  analogues=[A["contest"], A["firework"]],
  hard_criteria=["multi_mutation", "derived_target"],
  instruction='/f/pics currently has one post scoring higher than any other. Re-post its '
              'image to both the aww forum and the funny forum, each with the title '
              '"from /f/pics".',
  src_id=190003, src_title=TOPPOST_008["title"], src_author="trailmix_tabby",
  image=TOPPOST_008["image"],
  dests=["aww", "funny"], title="from /f/pics", body_author=None,
  setup_rows=[TOPPOST_008], variant="dual",
  injected=["newSubmissions gains one seeded-shaped IMAGE post in /f/pics, id 190003 by "
            "trailmix_tabby at netScore 7600 (ranking 7600, matching the seed's "
            "ranking==netScore convention), which displaces 'A Trejo Thanksgiving.' "
            "(7522) as the forum's highest-scoring post. Margin 78. The injection "
            "changes the correct answer for an otherwise-identical chain rather than "
            "swapping the entity."],
  notes="Injected top post at 7600 vs the seeded leader 7522 - margin 78. ranking is "
        "set equal to netScore so the record is also on page 1 of the default (hot) "
        "/f/pics view, per the census ordering rule.",
 ),
 dict(
  n=9, key="pride_parade_credit_oldschoolcool",
  diff="medium", style="explicit", skills=["R6", "R9", "A7"],
  chain="search /f/pics for the 1973 Pride Parade photo -> read its image URL and its "
        "byline -> file a submission in /f/OldSchoolCool carrying the URL and crediting "
        "the poster",
  analogues=[A["eagle"], A["wife"]],
  instruction=(
    "There is a photo in /f/pics of parents of LGBT children at the first Pride Parade in "
    "1973. I want it in the OldSchoolCool forum with credit. Find the post, take the "
    "address of the picture it displays, then use the submit form to create a post in "
    "OldSchoolCool whose title is exactly \"from /f/pics\", whose URL field holds that "
    "picture's address, and whose body names the person who originally posted it. The URL "
    "field rejects anything that is not a full http:// or https:// address."),
  src_id=131480, src_title="Parents of LGBT children at the first Pride Parade, 1973",
  src_author="Heretostay59",
  image="a70457e4ff490d1a950e4a8329e3f274566259a67ed6c9c73387210241686496.jpg",
  dests=["OldSchoolCool"], title="from /f/pics", body_author="Heretostay59",
  setup_rows=[], variant="single_body",
  notes="'pride parade' returns two submissions, one of them in /f/pics; "
        "'pride parade 1973' returns exactly one. Three skills but only one real "
        "retrieval chain (the byline is on the page already opened), so it is labelled "
        "medium rather than padded up to hard.",
 ),
 dict(
  n=10, key="water_buffalo_lamp_higher_score",
  diff="hard", style="explicit", skills=["R6", "R1", "A7", "A2"],
  chain="search /f/pics for the dentist-lamp photos -> compare the two hits' scores to "
        "pick the higher one -> read that post's image URL -> file it as a submission in "
        "/f/mildlyinteresting",
  analogues=[A["contest"], A["turkey"]],
  hard_criteria=["derived_target", "cross_section"],
  instruction=(
    "Two different people have posted a photo in /f/pics of a dentist lamp that looks like "
    "a water buffalo. Find both, decide which of the two has the higher score, and re-post "
    "that one - and only that one - to the mildlyinteresting forum: title exactly "
    "\"from /f/pics\", and the URL field set to the address of the picture that post "
    "displays."),
  src_id=190004, src_title=RIVAL_010["title"], src_author="sedationDentist",
  image=RIVAL_010["image"],
  dests=["mildlyinteresting"], title="from /f/pics", body_author=None,
  setup_rows=[RIVAL_010], variant="single",
  injected=["newSubmissions gains one seeded-shaped IMAGE post in /f/pics, id 190004 by "
            "sedationDentist at netScore 3900, titled so that it matches the same "
            "search tokens as the seeded 'this dentist lamp kind of looks like a water "
            "buffalo' (89341, netScore 3255). The seed has exactly one such photo, so "
            "the comparison the task asks for does not exist without the injection; "
            "the margin is set at 645, wide enough to be unambiguous."],
  notes="Margin 3900 vs 3255 = 645. The higher-scoring record is the injected one, so "
        "the correct image URL cannot be reached from the frozen seed alone.",
 ),
]

PICS_TOP_SEEDED = 7522


# --------------------------------------------------------------------------
# Reward source
# --------------------------------------------------------------------------
COMMON = '''
def _rows(state):
    """Every agent-visible submission record created during the episode."""
    value = state.get("newSubmissions") if isinstance(state, dict) else None
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _url_points_at(value, filename):
    """True when `value` is an absolute http(s) address for that image file.

    The rendered href on the source post is the RELATIVE path
    /submission_images/<file> while the submit form only accepts
    ^https?://, so the recorded value must be the promoted absolute form.
    The origin is deliberately not pinned: the hub serves reddit on a
    different host:port in the verification harness and in a NeMo rollout.
    """
    raw = _text(value)
    lowered = raw.lower()
    if not (lowered.startswith("http://") or lowered.startswith("https://")):
        return False
    path = raw
    for sep in ("?", "#"):
        cut = path.find(sep)
        if cut != -1:
            path = path[:cut]
    return path.lower().endswith("/submission_images/" + filename.lower())


def _filed(rows, forum, title):
    out = []
    for row in rows:
        if _text(row.get("forum")).lower() != forum.lower():
            continue
        if _text(row.get("title")) != title:
            continue
        out.append(row)
    return out


def _carried(rows, forum, title, filename):
    return [r for r in _filed(rows, forum, title) if _url_points_at(r.get("url"), filename)]
'''

EVALUATE = '''

def _details(state, name):
    rows = _rows(state)
    return "newSubmissions=%d row(s); forums=%r; titles=%r; urls=%r; check=%s" % (
        len(rows),
        [_text(r.get("forum")) for r in rows],
        [_text(r.get("title")) for r in rows],
        [_text(r.get("url")) for r in rows],
        name,
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
        earned = weight if checks.get(name) else 0.0
        total += earned
        components.append({
            "name": name,
            "score": round(earned, 6),
            "details": _details(state, name),
        })
    return {"score": round(total, 6), "components": components}
'''

NEMO_MAIN = '''

def main():
    try:
        response = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
        response.raise_for_status()
        state = response.json().get("current_state")
        if not isinstance(state, dict):
            state = {}
    except Exception as exc:
        print("REWARD_ERROR: " + repr(exc))
        print("REWARD: 0.0")
        return

    checks = score_checks(state)
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        if checks.get(name):
            total += weight
    print("COMPONENTS: " + json.dumps({k: bool(v) for k, v in checks.items()},
                                      sort_keys=True))
    print("REWARD: " + str(round(total, 6)))


try:
    main()
except Exception as exc:
    print("REWARD_ERROR: " + repr(exc))
    print("REWARD: 0.0")
    sys.exit(0)
'''


def constants_block(t):
    expected = len(t["setup_rows"]) + len(t["dests"])
    lines = [
        'TARGET_IMAGE = %r' % t["image"],
        'REPOST_TITLE = %r' % t["title"],
        'EXPECTED_NEW_ROWS = %d' % expected,
    ]
    if t["variant"] == "dual":
        lines.append('DEST_FIRST = %r' % t["dests"][0])
        lines.append('DEST_SECOND = %r' % t["dests"][1])
    else:
        lines.append('DEST_FORUM = %r' % t["dests"][0])
    if t["body_author"]:
        lines.append('ORIGINAL_POSTER = %r' % t["body_author"])
    return "\n".join(lines)


def weights_and_checks(t):
    if t["variant"] == "dual":
        a, b = t["dests"]
        n1 = "repost_filed_in_%s" % a.lower()
        n2 = "repost_filed_in_%s" % b.lower()
        n3 = "new_submissions_are_exactly_the_two_reposts"
        weights = {n1: 0.3, n2: 0.3, n3: 0.4}
        checks = (
            "def score_checks(state):\n"
            "    rows = _rows(state)\n"
            "    first = _carried(rows, DEST_FIRST, REPOST_TITLE, TARGET_IMAGE)\n"
            "    second = _carried(rows, DEST_SECOND, REPOST_TITLE, TARGET_IMAGE)\n"
            "    return {\n"
            "        %r: len(first) >= 1,\n"
            "        %r: len(second) >= 1,\n"
            "        %r: (len(rows) == EXPECTED_NEW_ROWS\n"
            "             and len(first) == 1 and len(second) == 1),\n"
            "    }\n" % (n1, n2, n3)
        )
        return weights, checks
    if t["variant"] == "single_body":
        n1 = "new_submissions_hold_exactly_one_repost_in_%s" % t["dests"][0].lower()
        n2 = "repost_url_is_the_pics_image"
        n3 = "repost_body_credits_the_original_poster"
        weights = {n1: 0.3, n2: 0.4, n3: 0.3}
        checks = (
            "def score_checks(state):\n"
            "    rows = _rows(state)\n"
            "    filed = _filed(rows, DEST_FORUM, REPOST_TITLE)\n"
            "    carried = _carried(rows, DEST_FORUM, REPOST_TITLE, TARGET_IMAGE)\n"
            "    credited = [r for r in carried\n"
            "                if ORIGINAL_POSTER.lower() in _text(r.get(\"body\")).lower()]\n"
            "    return {\n"
            "        %r: len(rows) == EXPECTED_NEW_ROWS and len(filed) == 1,\n"
            "        %r: len(carried) >= 1,\n"
            "        %r: len(credited) >= 1,\n"
            "    }\n" % (n1, n2, n3)
        )
        return weights, checks
    n1 = "new_submissions_hold_exactly_one_repost_in_%s" % t["dests"][0].lower()
    n2 = "repost_url_is_the_pics_image"
    weights = {n1: 0.4, n2: 0.6}
    checks = (
        "def score_checks(state):\n"
        "    rows = _rows(state)\n"
        "    filed = _filed(rows, DEST_FORUM, REPOST_TITLE)\n"
        "    carried = _carried(rows, DEST_FORUM, REPOST_TITLE, TARGET_IMAGE)\n"
        "    return {\n"
        "        %r: len(rows) == EXPECTED_NEW_ROWS and len(filed) == 1,\n"
        "        %r: len(carried) >= 1,\n"
        "    }\n" % (n1, n2)
    )
    return weights, checks


def weights_src(weights):
    body = "\n".join("    %r: %s," % (k, v) for k, v in weights.items())
    return "COMPONENT_WEIGHTS = {\n%s\n}" % body


def reward_py(task_id, t):
    weights, checks = weights_and_checks(t)
    doc = (
        '"""Deterministic reward for %s.\n\n'
        "The scored fact is the URL recorded on the submission(s) the agent created:\n"
        "the source photo's rendered href is a site-relative /submission_images/<file>\n"
        "path, and the submit form rejects anything that does not match ^https?://,\n"
        "so a correct run records the promoted absolute address of that exact file.\n"
        "The origin is not pinned because the hub's host:port differs between the\n"
        "verification harness and a NeMo rollout.\n\n"
        "Every component names something the run made true and is read out of\n"
        "current_state alone. Nothing is gated on 'a record was touched': the\n"
        "collection assertion states the exact resulting set of created submissions,\n"
        "so a destructive or scattergun run scores strictly less than 1.0.\n"
        '"""\n' % task_id
    )
    return (doc + "\n" + constants_block(t) + "\n\n" + weights_src(weights)
            + "\nassert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9\n"
            + COMMON + "\n\n" + checks + EVALUATE)


def nemo_reward_py(task_id, t):
    weights, checks = weights_and_checks(t)
    doc = (
        '"""NeMo-Gym reward program for %s.\n\n'
        "Same rubric as reward.py, reading current_state from GET /go?sid=... and\n"
        "printing REWARD: <float> on every output path including the error path.\n"
        "Self-contained: standard library plus requests.\n"
        '"""\n' % task_id
    )
    head = (
        "\nimport json\nimport sys\n\nimport requests\n\n"
        'SID = "__CUA_GYM_SID__"\n'
        'BASE_URL = "%s"\n\n' % PLACEHOLDER
    )
    return (doc + head + constants_block(t) + "\n\n" + weights_src(weights) + "\n"
            + COMMON + "\n\n" + checks + NEMO_MAIN)


def setup_py(task_id, t):
    rows = t["setup_rows"]
    fixture = json.dumps(rows, indent=2, ensure_ascii=False)
    doc = (
        '"""NeMo-Gym setup program for %s.\n\n'
        "Reads the pristine baseline from GET /go?sid=, appends the injected\n"
        "submission record(s) to the newSubmissions overlay, and republishes the\n"
        "whole state document with the 'set' action so the episode baseline is the\n"
        "task's own starting state rather than a partial patch.\n\n"
        "The injected record carries exactly the field set the seeded /f/pics rows\n"
        "carry, and its ranking equals its netScore, matching the convention in\n"
        "8011 of the 8012 seeded submissions - so it sorts onto page one of the\n"
        "forum's default view as well as of its top-of-all-time view.\n\n"
        "The fixture is parsed from a raw-string JSON literal, so no bare JS\n"
        "literal and no parser-eaten escape can reach the program namespace.\n\n"
        "Self-contained: standard library plus requests.\n"
        '"""\n' % task_id
    )
    return (
        doc
        + "\nimport json\nimport sys\n\nimport requests\n\n"
        + 'SID = "__CUA_GYM_SID__"\n'
        + 'BASE_URL = "%s"\n\n' % PLACEHOLDER
        + 'INJECTED_SUBMISSIONS = json.loads(r"""\n' + fixture + '\n""")\n\n'
        + '''
def main():
    # Clear anything left on this sid so the baseline patched below is always
    # createInitialData() -- the pristine seed -- and a rerun on a reused sid
    # starts a clean episode instead of stacking a second injection.
    requests.post(BASE_URL + "/post?sid=" + SID, json={"action": "reset"}, timeout=60)

    probe = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    probe.raise_for_status()
    state = probe.json().get("initial_state")
    if not isinstance(state, dict) or not isinstance(state.get("forums"), list):
        print("SETUP FAILED: no pristine baseline to patch", file=sys.stderr)
        raise SystemExit(1)
    if state.get("newSubmissions"):
        print("SETUP FAILED: baseline newSubmissions is not empty", file=sys.stderr)
        raise SystemExit(1)

    state = dict(state)
    state["newSubmissions"] = [dict(row) for row in INJECTED_SUBMISSIONS]

    response = requests.post(
        BASE_URL + "/post?sid=" + SID,
        json={"action": "set", "state": state},
        timeout=60,
    )
    response.raise_for_status()

    check = requests.get(BASE_URL + "/go?sid=" + SID, timeout=60)
    check.raise_for_status()
    payload = check.json()
    if payload.get("state_diff") != {}:
        print("SETUP FAILED: state_diff is not empty after set", file=sys.stderr)
        raise SystemExit(1)
    if payload.get("initial_state") != payload.get("current_state"):
        print("SETUP FAILED: baseline and current state disagree after set",
              file=sys.stderr)
        raise SystemExit(1)
    print("SETUP OK")


main()
'''
    )


def success_criteria(t):
    dests = t["dests"]
    expected = len(t["setup_rows"]) + len(dests)
    out = []
    if len(dests) == 2:
        out.append(
            "newSubmissions holds a submission in /f/%s whose title is exactly %r and "
            "whose url is an absolute http(s) address ending in "
            "/submission_images/%s." % (dests[0], t["title"], t["image"]))
        out.append(
            "newSubmissions holds a submission in /f/%s whose title is exactly %r and "
            "whose url is that same absolute image address."
            % (dests[1], t["title"], ))
        out.append(
            "newSubmissions holds exactly %d row(s) in total: one repost in /f/%s, one "
            "in /f/%s%s." % (expected, dests[0], dests[1],
                             " and the record present before the episode began"
                             if t["setup_rows"] else ""))
    else:
        out.append(
            "newSubmissions holds exactly %d row(s) in total, exactly one of which is in "
            "/f/%s with the title %r%s."
            % (expected, dests[0], t["title"],
               " (the other row was present before the episode began)"
               if t["setup_rows"] else ""))
        out.append(
            "That submission's url is an absolute http:// or https:// address whose path "
            "ends in /submission_images/%s - the picture displayed by submission %d in "
            "/f/pics." % (t["image"], t["src_id"]))
        if t["body_author"]:
            out.append(
                "That submission's body names %s, the user who posted the original."
                % t["body_author"])
    return out


def replay_draft(task_id, t):
    dests = t["dests"]
    q = "'"
    L = []
    L.append('"""Golden replay DRAFT for ' + task_id + '.')
    L.append("")
    L.append("Click-only. The episode opens at '/' and every control below is reached by")
    L.append("following a rendered link, button or form control; the single page.goto is")
    L.append("the initial landing the harness performs anyway.")
    L.append("")
    L.append("How the absolute image URL is obtained, and why no URL is ever typed or")
    L.append("constructed: currentUser.submissionLinkDestination is 'url' in the seed")
    L.append("(src/data/currentUser.json), so Submission.jsx:71-77 points a post's TITLE")
    L.append("link at the media itself. For an image post that href is the site-relative")
    L.append("'/submission_images/<file>' (Submission.jsx:50), rendered as a plain")
    L.append("external anchor, so clicking the title is a real navigation to the picture")
    L.append("and the browser resolves the origin. page.url is then the absolute http(s)")
    L.append("address that SubmitPage.jsx:121-124 accepts, and page.go_back() returns to")
    L.append("the listing the click came from. The post's own permalink page stays")
    L.append("reachable through the comment-count link in nav.submission__nav.")
    L.append('"""')
    L.append("")
    L.append('BASE = "__CUA_GYM_WEBARENA_REDDIT_URL__"')
    L.append('SID = "__CUA_GYM_SID__"')
    L.append('IMAGE_PATH = "/submission_images/' + t["image"] + '"')
    L.append("")
    L.append("")
    L.append("def run(page):")
    L.append('    page.goto(BASE + "/?sid=" + SID)')
    if t["skills"][0] == "R4":
        L.append("    # / -> Forums -> f/pics, then the sort menu. Top lands on ?t=day,")
        L.append("    # which renders zero rows (the corpus ends 2023-03-31), so the time")
        L.append("    # dropdown must be moved to All time before the ranking is readable.")
        L.append('    page.click("a[href^=' + q + '/forums' + q + ']")')
        L.append('    page.click("a[href^=' + q + '/f/pics' + q + ']")')
        L.append('    page.click("a:has-text(' + q + 'Top' + q + ')")')
        L.append('    page.click("a:has-text(' + q + 'All time' + q + ')")')
        L.append('    row = page.locator("article.submission").first')
    else:
        L.append("    # / -> nav search box. See the bundle's authoring notes for the")
        L.append("    # result count this query was checked against.")
        L.append('    page.fill("input[name=' + q + 'q' + q + ']", ' + repr(t.get("query")) + ')')
        L.append('    page.press("input[name=' + q + 'q' + q + ']", "Enter")')
        L.append('    row = page.locator("article.submission").filter(')
        L.append('        has_text=' + repr(t["src_title"][:26]) + ').first')
    if t["body_author"]:
        L.append("    # The byline is on the listing row itself; no extra page is needed.")
        L.append('    poster = row.locator("a.submission__submitter").inner_text().strip()')
        L.append('    assert poster == ' + repr(t["body_author"]))
    L.append("    # Clicking the title navigates to the picture; the address bar then")
    L.append("    # holds the absolute form of the relative href the page rendered.")
    L.append('    row.locator("a.submission__link").click()')
    L.append("    image_url = page.url")
    L.append("    assert IMAGE_PATH in image_url")
    L.append('    assert image_url.startswith("http://") or image_url.startswith("https://")')
    L.append("    page.go_back()")
    for i, dest in enumerate(dests):
        L.append('    page.click("a[href^=' + q + '/submit' + q + ']")')
        L.append('    page.fill("#submission_url", image_url)')
        L.append('    page.fill("#submission_title", ' + repr(t["title"]) + ')')
        if t["body_author"]:
            L.append('    page.fill("#submission_body", poster)')
        L.append('    page.select_option("#submission_forum", ' + repr(dest) + ')')
        L.append('    page.click("button:has-text(' + q + 'Create submission' + q + ')")')
        L.append('    page.wait_for_selector("article.submission--expanded")')
        if i + 1 < len(dests):
            L.append('    page.click("a[href^=' + q + '/?sid' + q + ']")')
    return "\n".join(L) + "\n"


QUERIES = {
    1: "rainbow lobster", 2: "romanian pizza", 4: "puppy petra",
    5: "pizza stone moon", 6: "mona lisa", 7: "filet-o-fish oil painting",
    9: "pride parade 1973", 10: "dentist lamp water buffalo",
}


def main():
    os.makedirs(BATCH, exist_ok=True)
    os.makedirs(os.path.join(BATCH, "replays"), exist_ok=True)
    index = []
    rows = []
    for t in TASKS:
        t.setdefault("query", QUERIES.get(t["n"]))
        task_id = "image_repost_cross_forum_%s_%03d" % (t["key"], t["n"])
        d = os.path.join(ROOT, task_id)
        os.makedirs(d, exist_ok=True)

        if t["style"] == "terse":
            words = len(t["instruction"].split())
            assert words <= 40, (task_id, words)

        inst = {
            "task_id": task_id,
            "task_instruction": t["instruction"],
            "app_dir": APP,
            "start_path": "/",
            "difficulty": t["diff"],
            "success_criteria": success_criteria(t),
        }
        meta = {
            "style": t["style"],
            "difficulty": t["diff"],
            "shape": "retrieval_writeback",
            "skills": t["skills"],
            "skill_chain": t["chain"],
            "official_analogues": t["analogues"],
            "inspiration_ids": ["webarena-615", "webarena-616", "webarena-617",
                                "webarena-618", "webarena-619"],
            "topic": "image_repost_cross_forum",
            "authoring_notes": [
                "Grounded in webarena_reddit_mock @ hub/websites/webarena_reddit_mock.",
                "Inspirations informed shape only; entities, destination forums, titles "
                "and expected values are all different from the official rows.",
                "Mechanism verified in source: Submission.jsx:50 renders the image href "
                "as the relative /submission_images/<file>, while SubmitPage.jsx:121-124 "
                "rejects a non-empty URL that does not match ^https?://[^\\s]+$. The "
                "agent must promote the relative path to an absolute address.",
                "createSubmission (AppContext.jsx:384) stores the URL verbatim on the "
                "new record in newSubmissions, which is what both rewards read.",
                "Reachability: currentUser.submissionLinkDestination is 'url' "
                "(src/data/currentUser.json), so Submission.jsx:71-77 makes an image "
                "post's TITLE link point at /submission_images/<file> itself. Clicking "
                "that title is a real navigation to the picture, which is how the agent "
                "obtains the absolute URL without typing or constructing one; the post's "
                "own page stays reachable through the comment-count link in "
                "nav.submission__nav.",
                "Both reward programs read current_state only and never diff against "
                "the episode baseline.",
                t["notes"],
            ],
        }
        if t["diff"] == "hard":
            meta["hard_criteria"] = t["hard_criteria"]
        if t["setup_rows"]:
            meta["injected_preconditions"] = t["injected"]

        manifest = {
            "schema_version": 2,
            "task_id": task_id,
            "instruction": t["instruction"],
            "apps": [{
                "name": APP,
                "source_name": "reddit",
                "base_url_env": ENV,
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

        rw = reward_py(task_id, t)
        nr = nemo_reward_py(task_id, t)
        st = setup_py(task_id, t) if t["setup_rows"] else None

        with open(os.path.join(d, "task_instruction.json"), "w") as f:
            json.dump(inst, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(os.path.join(d, "task.json"), "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(os.path.join(d, "reward.py"), "w") as f:
            f.write(rw)
        with open(os.path.join(d, "nemo_reward.py"), "w") as f:
            f.write(nr)
        if st is not None:
            with open(os.path.join(d, "initial_setup.py"), "w") as f:
                f.write(st)
        else:
            p = os.path.join(d, "initial_setup.py")
            if os.path.exists(p):
                os.unlink(p)

        row = {"task_payload": {
            "task_id": task_id,
            "dataset": "cuagym",
            "dataset_version": "v1",
            "sites": [APP],
            "start_urls": [],
            "intent": t["instruction"],
            "eval": {"eval_types": ["string_match"], "reference_answers": None,
                     "note": "unused - CUA-Gym reward code is authoritative"},
            "cuagym": {"bundle_id": task_id, "app_dir": APP,
                       "initial_setup": st, "eval_reward_code": nr},
        }}
        with open(os.path.join(d, "nemo_task.json"), "w") as f:
            json.dump(row, f, indent=2, ensure_ascii=False)
            f.write("\n")
        rows.append(row)

        with open(os.path.join(BATCH, "replays", task_id + ".py"), "w") as f:
            f.write(replay_draft(task_id, t))

        index.append({"task_id": task_id, "path": "../../%s/task.json" % task_id})

    with open(os.path.join(BATCH, "index.json"), "w") as f:
        json.dump({"schema_version": 2, "tasks": index}, f, indent=2)
        f.write("\n")
    with open(os.path.join(BATCH, "nemo_tasks.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote %d bundles" % len(TASKS))


main()
