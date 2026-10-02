# Batch 6 — corrections

Continues `webarena_09_04_skills/CORRECTIONS.md` (findings 1–122). All 122 of
those still apply; numbering here restarts at B6-1 to keep the batches
distinguishable.

## B6-1. A batch-5 finding was reported, relayed, and never recorded — and batch 6 paid for it

The gitlab mock ships **30 built-in project templates**, not 5.
`components/create/templates.js` says so in its own header (*"Exactly 30 rows …
the Built-in tab counter reads 30"*), `NewProject.jsx` maps all 30 and prints
`TEMPLATES.length` into the tab badge, and the names are present in the
**served** `dist/assets/index-C5f24-KF.js`, not merely in `src/`.

**And there are near-duplicates**, which the census explicitly denied: five
GitLab-Pages/Netlify pairs (Jekyll, Hugo, Plain HTML, GitBook, Hexo), plus
`Spring` vs `Gitpod/Spring Petclinic`, and `Serverless Framework/JS` vs
`Tencent Serverless Framework/NextjsSSR`. So **naming a framework alone does
not identify a template for 12 of the 30 rows.**

Also: `blank` is listed among the choices and is **not a template** — it is a
separate pane (`#blank_project`). Official `webarena-747`'s "blank template" is
therefore not an R8 retrieval at all.

**The process failure is the point.** A batch-5 lane found the 30-template
count, reported it in its completion message, and I summarised it to the user —
but never wrote it into `CORRECTIONS.md`. The census kept saying five, the
batch-6 topic allocation inherited "5 choices, no near-duplicates … no tie
exposure at all", and a batch-6 lane spent its own time rediscovering it.

*A finding that lives only in a completion message and a chat summary is a
finding that will be rediscovered. Persist it where the next batch reads, or it
does not exist.* I am auditing the batch-5 lane reports for other findings that
were relayed but never recorded.

## B6-2. `createProject` discards the description when a template is chosen

`templatePayload` has already substituted the template's own blurb, so the
description textarea is ignored (`mutations.js:272`). That makes the recorded
description a **drift-proof template fingerprint**, and a rubric can gate every
component on it.

Consequence worth copying: gating on the fingerprint means an agent that skips
the gallery and picks a neighbouring row scores **0.0**, not partial credit.
Batch 5's equivalent task paid 0.5 in that case, which rewarded landing near
the answer.

## B6-3. Licence discriminating text has two-way ties the census denied

"13 licences, no near-duplicates" is right about licence *identity* and too
strong about the text an instruction discriminates on. `Exhibit A` and
`Secondary License` appear in **both** EPL 2.0 and MPL 2.0; `heirs and
successors` in **both** CC0 and The Unlicense. A lane scanned all 13 `content`
bodies in `licenses.js`, found the collisions, and re-routed onto
`Agreement Steward` / `Larger Work` / the CC0 fallback grant / `Affirmer`.

## B6-4. gitlab's partial-`set` REPLACES — and two lanes disagreed about it

**WITHDRAWN AND REVERSED.** This entry first recorded gitlab as shallow-merging,
on one lane's source reading. A second lane read the same code and concluded the
opposite. I settled it on the running mock:

    pristine /go current_state          41 keys
    POST {"action":"set","state":{"newStars":[...]}}
    after                               1 key
    keys LOST from current_state        40

**gitlab REPLACES**, exactly like reddit. A partial `set` becomes the entire
state.

*Why the disagreement is instructive, and why it is dangerous.* The
shallow-merge reading was not careless — `dataManager.js:242 mergeOverDefaults`
really does `toCore({...defaults, ...custom})` and re-merges `repo`/`ui`/
`nextIds` key-wise at `:247-249`. But that is the **client** merging over
defaults as it renders. The **state API** (`vite.config.js:388`) writes the
posted object verbatim to both `<sid>.json` and `<sid>.initial.json`; only
`set_current` with an explicit `merge: true` (`:428`) merges server-side.

So after a partial `set` on gitlab: **the agent sees a working site and the
reward sees an almost-empty state.** The two layers disagree, and a reward
reading `current_state` — which TASK4 S7 mandates — gets the partial.

**Final table:**

| mock | `{"action":"set"}` |
|---|---|
| **gitlab** | **REPLACES** (measured, 41 keys -> 1) |
| **reddit** | **REPLACES** (measured) |
| shopping | shallow-merges over `createInitialData()` |
| shopping_admin | shallow-merges over `createInitialData()` |

Two of four replace. **Read `vite.config.js` for your own mock, and prefer
posting the full document read back from `/go` regardless** — it is correct
under either behaviour.

## B6-5. CORRECTIONS #22's file:line was wrong (the conclusion was right)

`ForkProject.jsx:13` is the `ANCHORS:` source comment, not a rendered header.
MetaSeq really is `root/metaseq` (id 33, confirmed in `src/data/projects.json`);
the header comes from `usePageChrome` at `:63-67` via `useProject()`.

A correction can carry a wrong citation and a right conclusion. Cite the line
you actually read.

## B6-6. `census/gitlab.md:279` still lists `facebook/metaseq`

Superseded by CORRECTIONS #22 and never amended in the census file — the same
back-propagation failure as B6-1 and the `:main:LICENSE` cell. This is now the
**third** census cell found to contradict a verified finding, which is why
`output/CENSUS_ERRATA.md` exists and is in every lane brief's read list.

## B6-7. `default_branch` has NINE distinct values, not two

CORRECTIONS #15 and every brief derived from it discuss `main` vs `master`. A
lane found `OptimalBits/bull` is **`develop`**; counting the whole seed gives:

    master 126 · main 41 · develop 2 · A1_A2_A3 1 · ver3 1
    development 1 · 6.x 1 · 6.2 1 · lib 1

**Only 41 of 175 projects are on `main`, and seven are on something that is
neither `main` nor `master`.**

The correct instruction has never been "check whether it is master" — it is
**read `default_branch` from `src/data/projects.json` for the specific repo**,
which is what the finding always said. But a brief that names two values invites
a binary check, and a binary check silently fails on the third.

## B6-8. gitlab partial-`set`: three independent measurements agree

Lanes 4, 5 and my own probe all measured **REPLACES** (41 keys -> 1). Lane 2's
shallow-merge reading was the outlier and its task has been sent back.

Recording the count because the disagreement was resolved by *measuring the
running mock*, not by re-reading the source more carefully — three agents read
the same files and two got it right for reasons that looked identical to the one
that got it wrong. The client-side `mergeOverDefaults` is real; it simply is not
the layer `/go` reports.

## B6-9. "A writable key is not a merged key, and the module that merges is not always the module that persists"

The lane that got gitlab's merge semantics wrong wrote the general form itself,
and it is better than mine. `mergeOverDefaults` is real code that really merges;
what was wrong was **which process runs it**. It is the client re-merging over
defaults as the SPA renders, not the state API persisting.

The failure is invisible to every check short of reading `/go` directly:

* the client merge **repairs the site for the agent**, so the replay is green;
* `/go` hands the reward a five-key document, so the rubric grades a near-empty
  state.

A lane cannot catch this by driving its own task. Only a direct `/go` read
finds it.

**The recipe that is correct on all four mocks regardless of semantics:**

    GET  /go?sid=<sid>          -> full current_state
    mutate that document in place
    POST /post?sid=<sid>  {"action": "set", "state": <whole document>}

with a loud failure if `/go` returns neither `current_state` nor
`initial_state`, rather than posting a truncated document. This is now the
required shape for every batch-6 `initial_setup.py`.

## B6-10. An `issueEdits` record REPLACES the frozen row — it does not patch it

`overlay.mergeCollection` (`utils/overlay.js:236`) serves an `issueEdits` record
**verbatim in place of** the seeded row and does **not** splice the lazily-loaded
description back on.

So an injected edit that carries only the fields it means to change **blanks the
issue page** and drops the row out of description search. An injection must
carry the full seeded row with only the intended fields altered.

Same family as `projectEdits` being a full record replacement (`overlay.js:238`)
and the four-lane `mergeOverDefaults` confusion: **on this mock, "edit" overlays
are replacements, and the merging that does happen happens somewhere other than
where you are looking.**

## B6-11. gitlab partial-`set`: final tally

Six lanes plus two direct probes have now weighed in. **REPLACES** — lanes 4, 5,
10 and both probes (41 keys -> 1, on disk and via `/go`). **"shallow-merges"** —
lanes 2, 3, 8, 9, all describing the client-side `mergeOverDefaults`.

No delivered bundle was harmed: every batch-6 `initial_setup.py` already posts a
full document, including all four lanes that reported the wrong semantics. The
habit protected the batch from the misunderstanding, which is the argument for
mandating the habit rather than relying on the understanding.

## B6-12. "byteblaze owns zero milestones" is true only of the `byteblaze/*` namespace

`a11yproject/a11yproject.com` — which he maintains and which appears on his
dashboard — carries **six frozen milestones** (ids 584-589, iids 1-6). They sit
in the frozen corpus rather than `newMilestones`, so "exactly one CREATED
milestone" remains unambiguous; but a task asserting "the project now has
exactly one milestone" would be **wrong** there.

The original claim was scoped correctly and read as if it were global. Scope a
claim to the namespace it was measured in.

## B6-13. CRITICAL TOOLING — `grep` silently finds NOTHING in two mock source files

`grep` (this box ships **ugrep 7.8.4** as `/usr/bin/grep`) returns **zero
matches** for strings that are plainly present in:

    hub/websites/webarena_gitlab_mock/src/components/create/mutations.js   (2 NUL bytes)
    hub/websites/webarena_reddit_mock/src/utils/markdown.js                (1 NUL byte)

Each contains embedded `\x00`, so `file` classifies them as **`data`** rather
than text and ugrep suppresses matches as binary. It exits **1** — the same as
"not found" — so the failure is indistinguishable from a genuine absence.

**Why this matters more than a normal tooling annoyance.** `mutations.js` is the
gitlab mock's entire creation/mutation module. It defines:

    deriveSlug, makeSha, dbStamp, gitStamp, ownedNamespaces, pathTaken,
    writeFiles, commitToRepo, deleteFile, createProject, addMembers,
    createGroup, forkProject

**Every one of those handlers is invisible to `grep`.** Any lane or census that
grepped for `createProject`, `forkProject`, `commitToRepo` or `addMembers` and
concluded "no such handler / ABSENT" was lied to by the tool. Standing rule 6
("grep for the reference, not the definition") assumed grep works.

**Workarounds, in order of preference:**

* `grep -a` (treat binary as text) — verified, recovers the match;
* read the file in Python and search the string;
* `rg` if available.

*Audit note:* the batch-5 censuses recorded `A2` (multi-field creation),
`A3` (membership) and `A7` (file commit) as **SUPPORTED** on gitlab with correct
`mutations.js` line citations, so their authors evidently read the file rather
than relying on grep. No delivered finding is known to rest on a false-negative
grep of these two files — but the failure mode is silent, so absence of evidence
is weak here. **Any future "handler is absent" claim about gitlab creation or
reddit markdown must be confirmed by reading the file.**

## B6-14. gitlab renders a LOS ANGELES date in `title` and UTC in `datetime`

`TimeAgo.jsx:16` puts an `America/Los_Angeles`-converted date in the `title`
attribute (`format.js:72-86`) while the `datetime` attribute stays **UTC**
(`:90`). For any issue created before 08:00 UTC the two name **different
calendar days**, so a date derived from `created_at` is ambiguous by
construction — an agent reading the tooltip and an agent reading the DOM
attribute get different answers.

A lane screened every candidate anchor and rejected five of byteblaze's issues
on this; roughly a third are disqualified as date anchors.

**The asymmetry that rescues it:** `formatDate` on a *date-only* value
(`due_date`, milestone `start_date`/`due_date`) does **not** shift. So date
arithmetic anchored on a due date is safe where the same arithmetic anchored on
a timestamp is not.

Third mock found with a rendered-date/stored-date split, after shopping's
`America/New_York` five-order shift and reddit's relative-time rendering. **Assume
every mock renders dates in a timezone that is not UTC until you have checked.**

## B6-15. A topic's `notes` contradicted its own skill assignment

`wave_plan.json[12].notes` said "the window must be stated in the instruction and
computed by the agent" for a lane assigned **`R2 -> A2`**. A stated window is not
a retrieval, so following the note would have produced `skills == ["A2"]` and
failed the gate.

The topics builder wrote a plausible sentence that contradicts the pair it had
just assigned. The lane followed the assignment and recorded the conflict.
*When a topic's prose and its `skills` disagree, the `skills` are the
assignment* — the prose is a suggestion about how to express it.

## B6-16. The Hot==Top collapse is PER-FORUM and does NOT hold site-wide

CORRECTIONS #25 records that Hot order equals Top order in 94 of 95 forums.
That is a per-forum statement. **Site-wide it is false**: the fixture submission
`1` carries the epoch `ranking` 1686590745, so `/all/hot` row 1 is submission 1
while `/all/top?t=all` row 1 is 41616. **A site-wide top-ever retrieval is
genuinely forced on the pristine seed, with no injection.**

Three more site-wide listings rejected by the same lane:
* `/all/active` row 1 is the current user's **own** fixture post (`lastActive`
  2023-06-12, after the entire corpus) — a "most recently active" task would
  have the agent message itself;
* `/all/new` row 1 (137402) is authored by `[deleted]` — no resolvable
  recipient;
* `/f/X/active` is independent of `ranking`, and the Active head differs from
  the Hot head in **87 of the 88 forums with >= 30 rendered rows** (only
  `f/MachineLearning` coincides, again via the fixture). So `/active` is the
  cheapest way to force an R5 without injecting anything.

## B6-17. There is not one negative-score submission, and a negative score is unquotable

`min(netScore)` over all 8,012 rows is **0**. So "most controversial" is a tie at
the global floor rather than merely a ~10-way tie, and any injection fixing it
would create the site's only negative post — implausible under the
one-screen-contradiction rule.

Separately: `Vote.jsx:54-56` renders a negative score as **U+2212 plus a second
hidden U+2212**, so a value copied from the page never matches an ASCII-hyphen
rubric. Comment scores *can* be negative (1,065 authors have at least one), so
this bites the comment lanes: **never require an agent to reproduce a negative
number verbatim.**

## B6-18. `forums[].submissionCount` is stale but INTERNALLY CONSISTENT

AskReddit reports 10,041 against 97 rendered rows — the usual stored-aggregate
gap. Unlike the user and comment cases, though, `ForumsIndexPage.jsx:66-68`
sorts on the **same stored field** `ForumCard` prints, so ranking by it and
reading it off the card agree with each other. The number is wrong about the
seed and right about itself.

*The stored-aggregate rule needs this refinement: ask not only whether the
aggregate disagrees with the list, but whether anything the task depends on
reads the list at all.*

## B6-19 — reddit search: correct citations, and a comment hit is actionable in place

Verified by lane 25 against `hub/websites/webarena_reddit_mock/src/pages/SearchPage.jsx`.

* The matcher is `SearchPage.jsx:46-57`, `MAX_RESULTS` is `:43`, and the selection
  function `runSearch` is `:68-90`. Earlier briefs cited `:45-60` for the matcher;
  that range is wrong and an author following it reads the wrong function.
* **A comment hit on `/search` carries its own Reply control** — `CommentRow.jsx:140-160`,
  posting `parent=<comment id>` at `:74` — and its own context link to
  `/f/<forum>/<id>` at `:30`. So replying to a searched comment does **not** require
  opening the thread first. The prior guidance ("the only in-app route to a post page
  is the comment-count link") is true for submission hits and incomplete for comment
  hits.
* "Clicking a title navigates off-site" is not universal: for **image** posts the title
  points at `/submission_images/<file>`. Still not the post page, but the failure mode
  differs from an external link.
* Served-bundle check: `site-nav-search` and `.site-nav__search{display:flex}` (no
  mobile-only media query) are both present in `dist/`, so the search box is genuinely
  clickable from `/` even though `SiteNav.jsx` in `src/` is newer than the build.

Rejected by that lane and worth not re-attempting: any **count over search results**
(the 50-result cap truncates silently), `Bread & Circus` (stored `&amp;` vs rendered `&`),
and `Laverne & Shirley` / `pause on giant AI experiments` (two-way ties that cannot be
broken without adding a second retrieval skill, which batch 6 forbids).

## B6-20 — reddit short-URL `<kbd>` is live in the served build; `/{id}` is not click-reachable

Verified by lane 27 against `hub/websites/webarena_reddit_mock/dist/assets/index-DkKlva4C.js`.

* `submission-meta__short-url` renders as ``<kbd class="submission-meta__short-url">{origin}/{id}</kbd>``
  and **is present in the served bundle**, not only in `src/`. Same for `site-nav-search`,
  `site-nav__search-input`, `aria-label="Submit"`, `submission__forum`, `submission__nav`,
  `submission_title` / `submission_body` / `submission_forum`, and `Create submission`.
* **Do not identify a submission by its short URL / `/{id}`.** Route #36 `/{id}` exists
  (`ROUTES.md:157`) but reaching it requires typing a URL, which TASK4 S6 forbids, and
  `runSearch` matches `title + body` only — it never matches an id. There is therefore no
  click path from `/` to a submission identified solely by a number. Use the short-URL
  number as a **derived output** instead; that exercises the same element while staying
  reachable.

## B6-21 — reddit author counts: site-wide is NOT in-forum

Recomputed by lane 28 from `src/data/submissions.json` the way `UserPage.jsx:41`
renders (author match + `visibility !== 'trashed'`, paged 25, id DESC).

| author | site-wide | in-forum |
|---|---|---|
| chrisdh79 | 39 | 19 in f/gadgets |
| marketrent | 28 | 14 in f/history |
| giuliomagnifico | 15 | 14 in f/science |
| lnfinity | 16 | 13 in f/gifs |
| Sariel007 | 22 | 16 in f/UpliftingNews |
| Hrekires | 11 stored / **10 rendered** | — |

A brief that quotes a site-wide count next to a forum name and an author who posted
in it reads as an in-forum count and ships a wrong answer. State the scope every time.

Two further findings from the same lane:

* **No seeded submission carries a `visibility` key at all**, so `UserPage.jsx:41`'s
  trashed predicate is inert on the pristine corpus. Any task that depends on trashing
  must inject the key first.
* The submission-page comment textarea has **no `id`** — it is `aria-label="Comment"`
  (`SubmissionPage.jsx:140`), unlike every other form field on the site. Replay authors
  selecting by id will miss it.

## B6-22 — reddit `commentCount` is unusable as a derivable figure (6,475 of 8,012 wrong)

Measured by lane 26 against `submissions.json` + `comments.json`.

AUTHOR_BRIEF says the advertised `commentCount` disagrees with the actual comment rows
"for at least one post (124607 says 6, holds 5)". That understates it by three orders of
magnitude: **6,475 of 8,012 submissions disagree**, frequently by an order of magnitude —
49007 advertises 189 over 5 rows, 28380 advertises 182 over 0, 21988 advertises 61 over 0.
Among MarvelsGrantMan136's 46 own posts, **all 29 with a nonzero count disagree**.

**No task may derive, assert, or write back a submission's comment count from either
surface.** The rendered listing and the stored field are both wrong relative to each other
and there is no third arbiter. Use the top *commenter* (read off the rendered thread)
instead of the comment *count* — same page, same retrieval, well-defined answer.

Confirmed correct in the same pass: `ranking == netScore` for 8,011 of 8,012;
`submissionEdits` is whole-record replacement; the edit path is author-only at
`EditSubmissionPage.jsx:51`; MarvelsGrantMan136's 46 posts are 43 link + 2 image + 1 body.

## B6-23 — shopping Price facets are exact in ALL 22 safe categories, not just two

Enumerated by lane 34 across every Price facet in the 22 fully-seeded categories.

* **All 20 that have a captured listing reproduce their bucket counts exactly against
  the seeded pool** — Table Linens 109/3, PlayStation 169/3/2/1/1, Swimwear 20/28/3/1/2/1,
  MP3 44/6/1/2/1, and so on. The prior guidance that kids-bedding and flip-cases are "the
  two safe facet playgrounds" understates the available surface by an order of magnitude.
* The remaining two (Virtual Reality, Smartwatches) have **no capture** and fall through to
  `priceFacets()`'s derived branch, which buckets the seeded pool directly and is therefore
  exact by construction: 54/1 and 32/13/1/5/4/1.

**CORRECTIONS #42's "9 two-result cells" is confirmed** (independently re-derived) but it is
a ceiling on **sidebar buckets only**, not on two-result *bands*. A stated threshold inside
a wider bucket yields better tasks: a $140 threshold inside "$100.00 and above" on Table
Linens returns three rows of which one must be dropped, so clicking the facet and stopping
scores 0.0.

**Three of the nine cells have a non-match one cent below the boundary** — Deli Meats $99.99
(id 21425), PlayStation $199.99 (id 99661), Kids' Bedding $69.99 (id 99157). Harmless under
the half-open `v >= from && v < to` when the instruction quotes the facet's own label, but
**any "around $100" phrasing on those cells is unscorable.**

## B6-24 — CORRECTIONS #58 is wider than recorded: 8 categories hide a price extreme

Measured by lane 32 across the 21 usable safe categories. #58 names only Chairs & Sofas
and Exercise & Fitness. Under the **default (position) sort**, the capture-vs-derived gap
hides a price extreme in **eight**:

| category | end hidden | page size |
|---|---|---|
| Kids' Bedding | max $88.99 | 12 |
| Kitchen & Table Linens | min | 12 |
| Flip Cases | **both ends** | 12 |
| Chairs & Sofas | min | 36 |
| Health Care | min | 12 |
| Competitive Swimwear | min | 36 |
| fan-shop Footwear | min | 12 |
| Exercise & Fitness | max $129.00 | 12 |

**Kids' Bedding and Exercise & Fitness are entities the lane briefs hand out by name.**
A min/max/Nth-extreme task on any of the eight has two defensible answers under the default
sort and must be dropped — or the instruction must put the agent on a **price sort**, under
which all 21 are gap-free at 12/24/36.

## B6-25 — `priceFacets` serves the CAPTURED block verbatim; agreement with the pool is not automatic

`catalog.js:1271-1283` (lane 33). Whenever an anchor capture exists, `priceFacets` returns
the captured Price block **verbatim**, so a sidebar cell can advertise a source count that
the seeded grid cannot render. **Any task quoting a facet count > 1 must verify
`count == |pool|` for that specific cell** rather than trusting the sidebar. Where no
capture exists the function buckets the seeded pool directly and is exact by construction.

Corollary (lane 33): census §4.3's "only the 22 fully-seeded categories are safe" is about
**whole-category superlatives**. A facet cell whose source count and derived pool both equal
**1** is equally deterministic in a partially seeded category — there is no page 2 and the
two numbers cannot disagree. Census §7 topic 2 is a **sample, not an enumeration**: a scan
of every captured listing for `count == 1 && |pool| == 1 && no exact capture` yields **36+
usable single-result cells store-wide**, including Video Projectors, Cheese, Mirrors,
Posters & Prints, Basic Cases, Wine and Men's Shave — departments the census never lists.

## B6-26 — two more abbreviated shopping category names

Beyond CORRECTIONS #63's two: category **255** renders "MP3 & MP4 Player Accessories"
(census says "MP3/MP4 Accessories") and category **43** renders "Heating, Cooling & Air
Quality" (census says "Heating/Cooling & Air Quality"). An instruction quoting the census
name will not match the rendered link text.

## B6-27 — shopping order-history extras

From lane 35, alongside a full recomputation of the month table (every census cell matched
exactly; grand total $14,605.40 over 25/9/3):

* `OrderHistoryPage.jsx:10` exposes `LIMITS = [10, 20, 50]` via `#order-limiter`, so all
  37 orders are reachable on **one rendered page** with no `?p=` URL. The "grid pages at 10"
  guidance describes only the default.
* **`totalQtyOrdered == len(items)` for all 37 seeded orders** (every line has
  `qtyOrdered == 1`), so "per item" and "per line" coincide in the seed. Undocumented, and
  a task must not lean on the distinction.

## B6-28 — CONFLICT on price-sorted listings: resolve per category before using one

Two lanes measured the same surface and disagree. **Both findings are recorded; neither is
settled. Any lane using a price extreme must re-derive for its own category.**

* **Lane 32:** under either price sort, all 21 usable safe categories are gap-free at
  page sizes 12/24/36 (see B6-24). Its remedy for the eight default-sort gaps is "put the
  agent on a price sort".
* **Lane 31:** the property that makes a superlative safe is **not** "fully seeded"
  (census §4.3) but **"the sorted URL has no capture"** — a different property the census
  never states. It re-derived `listingKey(path, query, ALL_KEYS)` over `listings.json`.
  Critically, `Toolbar.jsx:113-125` navigates with **`product_list_order` alone and no
  `dir`**, so selecting "Price" on **heating-cooling-air-quality** or
  **competitive-swimwear** lands *exactly* on those categories' captured keys. Lane 31
  calls those two **unusable, not merely risky** — which is a counterexample to lane 32's
  blanket claim.
* Five categories have a **sorted capture** (`product_list_dir=desc&product_list_order=price`).
  **kids-bedding is one of them**, so building a maximum task on it via a price sort lands
  on a captured listing — even though the lane briefs hand kids-bedding out by name with
  `$88.99 ($79.95)` as a clean extreme. Lane 31 excluded it.

**Procedure:** before relying on any price extreme, compute `listingKey` for the exact URL
the Toolbar will navigate to (order param, no dir) and confirm no capture matches. Do not
rely on either lane's summary.

Also from lane 31: census §4.3's Nintendo Switch cheapest (77531 at $3.66) is the **OLED
console mispriced in the source data** — genuine, but a replay screenshot of it will look
like a bug to a reviewer.

## B6-29 — reddit: per-forum Comments tabs give 40 usable anchors, not ~5

Confirms CORRECTIONS #33 with a measurement (lane 29). Ranks 1–6 of the 95 per-forum
`/f/{forum}/comments` tabs give **40** `(forum, rank)` anchors whose author has ≥1
below-zero comment and ≤60 comments total. **Row 1 alone across all 95 forums gives only 3**
— which is where the census's "~5 usable entities" comes from, and why it looks true if you
only test rank 1.

Two related facts: the firehose sort key is `(timestamp, id)` DESC with unique ids, so a
named ordinal always resolves to exactly one row; and `f/DIY` is in the **ambiguous** set —
its `/new` head is id 119019 at 2023-03-31T19:01 while the latest-*timestamped* submission
is 23:55. Of the four forums the briefs offer for a newest-post join, only `lakewood`,
`Newark` and `WorcesterMA` have coincident id-order and timestamp-order heads.

## B6-30 — the #58 capture gap structurally CANNOT reach a price-facet cell

Mechanism, from lane 30. `resolveListing` consults `capturedListing(path, query)` on the
full `ALL_KEYS` key, and **`price` is part of that key**. A `?price=` URL therefore has a
different key from the bare category URL, so unless the *faceted* URL was itself captured,
`exact` is null and the grid is 100% `pool.slice()` — the capture/page-2 gap never opens.

This resolves the B6-28 conflict **for facet-cell tasks specifically** (it says nothing
about whole-category superlatives, where the conflict stands):

* The **only** faceted category captures in all of `listings.json` are Nintendo Switch
  `?price=0-100` and `?price=100-200`. Avoid those two; every other facet cell is safe.
* CORRECTIONS #61's five sorted-capture categories are harmless for facet cells by the same
  mechanism — their keys carry `product_list_order`/`dir`/`p`. kids-bedding,
  fresh-meal-kits and mp3-mp4-player-accessories were used safely on this basis.

## B6-31 — "$X and above" facet labels usually link to a BOUNDED price param

Not the one-off the census records. Five cells labelled "$X and above" link to a bounded
param preserved from the source capture: kids-bedding `80-90`, deli `100-200`, nintendo
`100-200`, PlayStation `400-500`, meal kits `200-300`. **Only the derived branch (Virtual
Reality) emits a genuinely open `1000-`.**

Anyone who rewrites an "and above" label into `X-` lands on a **different page** than the
one the agent reaches by clicking. Read the anchor's actual `href`; never reconstruct it
from the label.

## B6-32 — single-result cells: 19, and 8 of them carry required options

Lane 30's independent enumeration: **19** single-result cells (CORRECTIONS #42 says 18; the
difference is PlayStation, which contributes two — `300-400` and `400-500`) and exactly
**9** two-result cells across 12 categories. Flip Cases confirmed floor-3.

**8 of the 19 single-result targets carry required options** and are unusable for a
tile-route task without pinning an `optionTypeId` in the instruction, because tile
Add-to-Cart silently navigates to the PDP (`ProductGrid.jsx:63-66`). Check
`productOptions` for your target before writing a one-click add.

## B6-33 — shopping A10 is fully scorable; the census's "PARTIAL" is misleading

`census/shopping.md` §2 marks A10 PARTIAL because there is no cancel/status-change control.
True but misleading (lane 38): **`placeOrder` (`AppContext.jsx:513`) is a genuine persisted
lifecycle transition** — it pushes onto `orders[]`, empties `cart.items`, and bumps
`nextOrderIncrementId`/`nextOrderEntityId`. Single call site `CheckoutPage.jsx:73`, wired to
the Place Order button at `CheckoutPage.jsx:486-488`. It is terminal for 12 official
templates and fully readable from `/go`.

Everything else in the checkout wizard — `step` (`CheckoutPage.jsx:26`), the selected address
card, the shipping radio — is React `useState` and **never reaches `/go`**, so no rubric may
touch it. `reorder` (`AppContext.jsx:598`) writes only `cart.items`, so reorder-without-checkout
correctly scores 0.0.

**`CartPage.jsx` contains `data-role="proceed-to-checkout"` twice**: once at :392-403 inside a
JSX comment quoting the source HTML, once as the real rendered button at :405-409. A
grep-only reading can cite the comment by mistake.

## B6-34 — `reorder` merges on the optionTypeId list ONLY

Refinement from lane 37. `reorder`'s merge key is the **`optionTypeId` list**; the option
`label`/`value` text is copied but never compared. Two lines whose options resolve to `null`
optionTypeIds would therefore merge. Not triggered in the seed — all 29 option groups across
the orders examined resolve, and every line's `finalPrice` equals its stored order price, so
`reorder`'s `line.price` fallback never fires — but it matters to any task that injects order
lines with unresolved options.

Independently confirmed by lane 37: the seeded cart is products 15033, 15787, 10617 at qty 1;
order 000000170 merges all three lines to three rows at qty 2; the five day-shifted orders are
**185, 154, 163, 166, 170**; `clearCart` is defined at `AppContext.jsx:316` and referenced by
no component.

**Contamination note:** "reorder my cancelled May 2023 order" resolves to seeded order 170,
which is the gold entity of official `webarena-437`. Two lanes independently declined it.

## B6-35 — shopping address book: writer and reader agree (this one is clean)

Lane 39, recorded because the *opposite* is the site's most repeated defect and future lanes
should not re-derive it.

* Key: `state.addresses`, plus `state.nextAddressId`, `state.customer.defaultBilling`,
  `state.customer.defaultShipping`.
* **Writer:** `AppContext.jsx:461-489` (`saveAddress`) — appends with `id = nextAddressId`,
  bumps it, and on a true flag sets `customer.defaultBilling`/`defaultShipping` and rewrites
  that flag to `a.id === id` on every row.
* **Reader:** `AddressBookPage.jsx:11-13` (defaults) and `:53-83` (Additional Address Entries);
  `AccountDashboard.jsx:13-14` reads the same pair. **Written key == rendered key.**
* `AddressEditPage.jsx:14`: `isOnly = state.addresses.length <= 1 && !!existing`, so
  `/customer/address/new/` keeps `#primary_billing` / `#primary_shipping` present but
  unchecked (`:30-31`).

**All 37 seeded orders carry the same address** (101 S San Mateo Dr — CORRECTIONS #66
confirmed), so any "copy the order's address into the book" task scores 1.0 untouched unless
addresses are injected first.

## B6-36 — two shopping order-grid traps for ordinal tasks

1. **The three pending orders are separable on a rendered column.** Earlier guidance said they
   "differ only by increment id"; they also differ by **grand total** — $754.99 / $2,004.99 /
   $1,004.99 — and the grid renders that column. A pending-order ordinal can key on it.
2. **`sortedOrders` places order 160 ABOVE 169 on the shared date 3/2/22 even though 169 is
   older.** So "my oldest order" read off the grid's bottom-to-top position is wrong; the
   grid's bottom row is the true oldest. Any unqualified "oldest order" task is ambiguous.

All 37 `grandTotal` values are distinct; the tightest pair anywhere is $77.66 vs $77.96.

## B6-37 — RESOLUTION of the B6-28 price-sort conflict: lane 31 was right, with a direction refinement

Lane 40 settled it by rebuilding `listingKey(path, query, ALL_KEYS)` over all **1,554** rows of
`listings.json` and looking up the exact key `select#sorter` produces (order param, **no dir**,
`Toolbar.jsx:113-125`) plus the `dir=asc` variant, for every category it intended to use.

**Lane 31 is correct and lane 32's blanket "all 21 are gap-free under a price sort" is wrong.**
`competitive-swimwear` and `heating-cooling-air-quality` **do** match `?product_list_order=price`
and are unusable for a price ordinal. Both were dropped on this evidence.

**New refinement neither lane had — the hazard is direction-specific.** Every kids-bedding
sorted capture carries `product_list_dir=desc` (the bare page *and* all nine price buckets).
There is **no** capture with `order=price` and no dir, which is exactly what the sorter emits.
So **kids-bedding is unusable for a DESCENDING price ordinal and safe ascending.** Neither the
census nor CORRECTIONS stated this; treat every "sorted capture" category as direction-specific
until checked.

**Procedure that works** (use this, not a summary): rebuild `listingKey` over `listings.json`,
look up the exact key the Toolbar emits for your URL, and confirm no capture matches. When none
does, `resolveListing()` takes `pool.slice()` (`catalog.js:1213`) and #58's gap cannot apply.
Verified clean by this method: deli-meats-cheeses, virtual-reality, patio-furniture-accessories,
cakes, pots-planters-container-accessories, smartwatches, kitchen-table-linens, kids-bedding
(ascending, incl. `price=50-60` and `price=30-40`), flip-cases (incl. `price=10-20`).

## B6-38 — census §4.3's "(2nd)" column is a rank-1 runner-up, and interior gaps are tighter than flagged

Confirms CORRECTIONS #26 concretely (lane 40). Kids' Bedding reads "$7.59 (9.99)" but ranks
**2/3 tie at $9.99, 4/5 tie at $12.99, 7/8/9 tie at $14.99** — the parenthesised figure says
nothing about whether an Nth-cheapest is tie-free for N > 2.

Census margin flags understate again: **Fresh Meal Kits' interior gaps are $0.06–$0.20, not the
$0.34 flagged.** Any Nth-cheapest task must check the gap at BOTH the N-1/N and N/N+1
boundaries itself.

The pristine wish list is **empty**: `src/data/wishlist.json` is `{"items": []}` and
`createInitialData()` (`dataManager.js:142,161`) sets `wishlist.items: []`,
`nextWishlistItemId: 1`.

## B6-39 — 689 reviews carry `rating: null` and render with NO stars (found nowhere else)

Measured by lane 36 over the full corpus. Rating distribution:
5★ 43,364 / 1★ 10,347 / 4★ 10,228 / 3★ 7,058 / 2★ 4,692 / **null 689**, the nulls spread over
**355 products**.

A null-rating row renders with **no `.review-ratings` block at all**
(`ProductPage.jsx:349-355`), so it is neither "≤2 stars" nor "≥4 stars". **Any rating-bounded
count over a product holding one has two defensible answers**, and **no de-dup key finds it** —
this is a third corruption class, independent of the two already recorded. Filter on it
explicitly before writing any rating predicate.

**The genuinely usable review pool is far smaller than "6,044 reviewed products" suggests:**
only **1,894** products pass all of (listable, three-surface agreement, null-free,
relaxed-key-clean, 3–14 reviews).

Two rendering facts for replay authors:

* **`Rating.jsx:44` renders a PERCENTAGE**, not star glyphs — `title="80%"` on
  `div.rating-result`. A replay that counts star elements finds nothing; read the title and
  divide by 20.
* **`ratingPercent` (`catalog.js:556-568`) re-derives the tile rating as soon as `myReviews`
  has an entry**, so submitting a review changes the wish-list tile's stars. Harmless for a
  rubric keyed on `myReviews`; **fatal to any rubric keyed on a displayed average.**

Use the **relaxed** de-dup key `(title, detail, rating)` — deliberately excluding `nickname`,
which is where the self-concatenation corruption lives — plus an explicit `a == b+b` nickname
scan. Lane 36 found two self-concatenation hits among 30 audited candidates (products 20764
and 27421).

## B6-40 — storefront order addresses are NOT editable; A11 must retarget the address book

Established by lane 41 and independently corroborated by the benchmark.

`state.orders` has exactly **one** writer in the app — `placeOrder` (`AppContext.jsx:588`),
which prepends. **Nothing mutates an existing order.** `OrderViewPage.jsx` only renders
`shippingAddress` (:82) and `billingAddress` (:90) and offers Reorder (:129) / Print (:132).

The benchmark agrees: `webarena-794` carries `fuzzy_match: "N/A"` with the `string_note`
"The shipping address cannot be changed after an order is placed in the website", and the
order-address-edit intents `webarena-538..542` are **shopping_admin**, not storefront.

So any storefront A11 must target the **address book**, not the order.

Two shapes that silently break rubrics:

* **Order addresses store `street` as a newline-joined STRING; book records store a LIST.**
  A rubric comparing them without normalising never matches.
* **A billing address differing from shipping is a state `placeOrder` cannot itself produce**
  (`AppContext.jsx:571-572` writes one object into both). It renders fine and is usable as a
  deliberate injected distractor, but a reviewer will otherwise read it as an inconsistency.

CORRECTIONS #55 re-confirmed: shipping method and payment title are **constant across all 37
orders**, so neither is ever a valid derived value.

## B6-41 — shopping storefront search does NOT match review bodies

Established with file:line by lane 42, contradicting the framing in several lane briefs
("find a product via review text").

`buildSearchCorpus()` (`catalog.js:1023-1039`) builds one record per listable product whose
only field is ``strong: `${p.name} ${p.sku} ${urlWords}`.toLowerCase()``. `searchSeed()`
(`catalog.js:1063-1088`) scores that at `W_STRONG=5` (`:851`) and, for the weak tier, the
sharded **description** inverted index in `src/searchindex/` (`catalog.js:140-216`,
`W_WEAK=1` at `:852`). The declared searchable-attribute list at `catalog.js:843-849` is
sku / name / description / short_description / url_key / manufacturer / color.

**Review bodies are searchable by no route.** `reviews.json` is read only by `reviewIndex`
(`catalog.js:508-518`), feeding `seededReviews` / `reviewsForProduct` (`:520`, `:551`), which
serve the PDP Reviews tab and `/review/product/listAjax`. Any R6 grounded on review text must
be re-grounded as a PDP-Reviews-tab read over an injected candidate set.

## B6-42 — two cart/wish-list rubric hazards

1. **`WishlistPage`'s own Add-to-Cart button ALSO REMOVES the wish-list row**
   (`WishlistPage.jsx:34-40`); the PDP button does not. Recorded nowhere before. So a rubric
   asserting "the item is still on the wish list after being carted" is **scoring a path, not
   an outcome** — it fails a correct run that used the wish-list button. Score the cart only,
   or pin the path in the instruction.
2. **Seeded cart lines carry a `rowTotal` key that `addToCart` never writes**
   (`src/data/cart.json` vs `AppContext.jsx:262-270`), and `CartPage.jsx:35,232` ignores
   `rowTotal`, computing from `price * qty`. **A whole-dict cart comparison fails a correct
   run** on the seeded rows. Normalise to `(productId, qty, options)`.

## B6-43 — the wish-list heart has NO required-options redirect (my brief was wrong)

`ProductGrid.jsx:63-66` is `AddToCartButton`, and it does redirect to the PDP when a product
has required options. **`TileActions`' heart (`ProductGrid.jsx:98-118`) has no such check** —
it calls `addToWishlist(product)` directly, as does the PDP anchor (`ProductPage.jsx:797-816`,
which validates only `#qty`). **Required-option products are not a hazard for a wish-list
lane.** Several batch-6 briefs, including mine, warned otherwise.

## B6-44 — shopping search scoring is computable offline; two tokenizer traps

From lane 43, with the mechanism worked out rather than assumed.

`buildSearchCorpus` (`catalog.js:1026-1038`) builds one strong field per listable product:
`name + " " + sku + " " + urlKey.replace(/-/g," ")`. `searchSeed` (`catalog.js:1063-1088`)
awards `W_STRONG = 5` (`:849`) on a strong hit, else `W_WEAK = 1` (`:850`) from the sharded
description index. Tokens are OR-ed, word-boundary and plural tolerant
(`tokenMatcher :872-878`), stopwords dropped (`:838-840`), minimum 3 chars (`:894-896`),
sorted score DESC then **`id` ASCENDING** (`:1084`).

**Useful consequence:** for a query whose every token appears in the target's name, the
full-strong group scores `5n` and nothing weak-only or mixed (max `5(n-1)+1`) can outrank it.
So **page 1 of an uncaptured search is exactly the full-strong group in id order — computable
offline.** There are 134 captured `q` values in `listings.json`; check yours against them, and
if uncaptured, `resolveListing` takes `pool.slice()` and #58 cannot bite.

**Two tokenizer traps that intuition gets wrong:**
* **No stemming across compounds.** `?q=cake mix` returns 18 rows and does **not** include a
  product named *Cheesecake* — `\b` makes `cake` and `cheesecake` disjoint.
* **`no` is a stopword**, so `?q=no bake` scores the single token `bake`.

Also: `census/shopping.md:131`'s "answer set is open — score against an enumerated id set" is
a property of the questions the census chose, not of the site. Ten uniquely-satisfiable
described-need tasks were built without touching a facet.

## B6-45 — shopping_admin stock status is STORED, and 149 seeded rows already disagree with qty

Lane 46, with the full render path read rather than inferred.

**Stored, not derived.** `ProductEdit.jsx:143` reads `Number(p.is_in_stock) === 1` into the
form; `:311` writes `is_in_stock: form.is_in_stock ? 1 : 0`; `:859-866` renders the Stock
Status select `name="product[quantity_and_stock_status][is_in_stock]"`. Bulk path at
`ProductGrid.jsx:496`. **Nothing computes it from `qty`.**

**The flag/quantity disagreement is not rare and needs no injection: 149 configurable/bundle/
grouped parents ship `qty 0` with `is_in_stock 1`.** This is load-bearing for any
lowest-stock derivation, because a parent can tie a real variant at 0. The remedy that works:
facet on **colour** — parents carry no `color`, so `String(r.color ?? '')` never matches a
colour filter and they drop out of the slice.

**Writer/reader (same key, confirmed):** writer `patchProduct` →
`state.productOverrides[String(id)]` (`AppContext.jsx:218-227`); readers `getProducts`
(`selectors.js:164-180`) → `ProductGrid.jsx:102`, and `getProduct` (`selectors.js:154-162`)
→ `ProductEdit.jsx`.

**Filters are wired, including hidden ones.** `qty` is `filterType:'range'`
(`ProductGrid.jsx:174-183`); `color` is a **hidden** `filterType:'select'` (`:265-275`).
`AdminGrid.filterableColumns` is built from every column carrying a `filterType`
**irrespective of visibility** (`AdminGrid.jsx:405-412`), and the panel mounts eagerly, hidden
by CSS (`:573-582`) — so `[name="color"]` resolves cold. `applyGridState(rows, columns, …)`
(`AdminGrid.jsx:216`) receives all columns.

**Page size for `product_listing` is 200**, not 20: `gridUtils.js`'s `defaultPageSizeFor`
overrides `ProductGrid.jsx:597`'s `defaultPageSize={20}` (CORRECTIONS #89 confirmed verbatim).
A 4–5 row matched set never spans pages, so "select all on page" vs "select all matches" does
not arise.

CORRECTIONS #74 is true but understated: **872 is also the only *simple* product at `qty 0`.**

## B6-46 — census §4.5's rating table is a sample; #58 has a second rating-winner casualty

From lane 44, which reimplemented `resolveListing`/`priceFacets` in Python to check rather
than read off the census.

* **Four more clean rating winners with ≥3-point margins** exist beyond census §4.5's list:
  Pots/Planters 16090 (100%, 10 pts), Health Care 35132 (98%, 8), MP3 accessories 42180
  (92%, 12), Cell Phones 89636 (87%, 12).
* **CORRECTIONS #58 has a second casualty among rating winners:** Heating/Cooling's winner
  **35921** also renders on no page under the default sort at 12/page. #58 names only 99336
  and Exercise & Fitness. (The same analyzer independently reproduced the 99336 result.)
* **Third abbreviated category name**, after CORRECTIONS #63's two and B6-26's two: category
  **273** renders as **"Deli & Prepared Foods"**, not "Deli, Prepared Foods".

Confirmed rather than corrected: kids-bedding 3/21/31/14/15/6/7/2/1 and flip-cases 3/28/10/3/3
each equal the seeded pool cell-for-cell; flip-cases has no cell under three; census §4.3
maxima and runner-ups reproduce exactly. Kids-bedding's
`price=60-70&order=price&dir=desc` capture holds all 7 ids of that cell, so captured and
derived branches agree there.

## B6-47 — an empty wish list renders NO textarea, which silently forces a third skill

`WishlistPage.jsx:57-59` renders no textarea when the list is empty, and the pristine wish
list **is** empty. So any "write a note on a wish-list item" task must **inject a wish-list
row first** — otherwise the agent has to add an item (A4) before it can write, and the task is
three skills, not two.

The note vessel does persist: `wishlist.items[].description` via `updateWishlistItem`
(`AppContext.jsx:347-357`), driven by `updateAll` (`WishlistPage.jsx:43-52`) from the textarea
at `:76-82`.

## B6-48 — the review-corpus corruption findings are STOREFRONT-ONLY; shopping_admin has its own, clean corpus

**My error, caught by lane 47.** Several batch-6 lane briefs handed shopping_admin authors the
review-corruption figures measured on `webarena_shopping_mock`. **They do not apply.**

Everything in B6-39 and the duplicate-class findings — 22,721 products / 76,378 reviews /
6,181 duplicate rows / 689 null ratings / 149 `reviewsCount` mismatches / `reviewCounts.json` /
`ProductPage.jsx` / `Rating.jsx` / `catalog.js` / `myReviews` / products 47884, 20764, 27421 —
belongs to the **39.6 MB storefront corpus**. None of those files exists on the admin mock.

**`webarena_shopping_admin_mock/src/data/reviews.json` is 215 KB: 351 rows over 127 products.**
Lane 47 ran all four audits on it anyway and it is **clean** — zero relaxed-key duplicates,
zero self-concatenated nicknames, zero null ratings, corpus-wide.

Admin-specific facts to use instead:

* `products.json` carries **no `reviewsCount` field at all**. `reviewSummaries.json` disagrees
  with the bodies on 2 of 127 products (1396, 1210) and is imported at `staticData.js:48` but
  **read by no component** — it is not a rendered surface.
* Status split is **346/5/0**; `disappointed` matches 6 rows (37/146/168/172/351/353).
* **Neither the review grid nor `ProductReviews` has a rating column**
  (`LegacyReviewGrid.jsx:414-436`; `ProductEdit.jsx:1775`), so the **review edit form**
  (`/admin/review/product/edit/id/<id>/`, `Summary Rating`) is the only surface carrying star
  values. The Reviews grid's Review-column filter (`LegacyReviewGrid.jsx:160`) is a
  case-insensitive substring on `detail`, with `N records found` at `:374`.
* Reports > Reviews > By Products ignores status and its averages are frozen — unusable.

**Description writer/reader agree:** writer `AppContext.jsx:229-233` →
`productDescriptionOverrides[String(productId)]`; reader `selectors.js:208-214`
(`getProductDescription`), consumed at `ProductEdit.jsx:155` into `#product-description`
(`:1049-1057`); Save is `#save-button` (`:464`). **`ProductEdit.jsx:390` writes unconditionally
on any existing-product save**, so a rubric must fullmatch the expected text — a no-edit Save
must score 0.0.

Also: **B6-13's NUL-byte `grep` failure is confined to the two gitlab/reddit files it names.**
`grep` behaves normally on every shopping_admin source.

## B6-49 — shopping_admin bulk actions all persist; "Update attributes" IS implemented

Mapped by lane 45; use this instead of re-deriving.

Mass actions declared at `ProductGrid.jsx:452-485` — `delete` (:457), `status_enable` (:465),
`status_disable` (:473), `update_attributes` (:482). **All four persist.** The in-page bulk
form `ProductGrid.jsx:527-577` → `applyBulkAttributes` (`:487-502`) → **`patchProduct`
(`:498`)**.

* **Writers:** `patchProduct` (`AppContext.jsx:219-227`) → `productOverrides[<id>]`;
  `deleteProducts` (`AppContext.jsx:240-245`) → `deletedProductIds`. Both persisted
  (`dataManager.js:353`, `:359`).
* **Readers:** `getProducts` (`selectors.js:164-181`) merges the override over the seed row,
  and the grid renders those same keys — `price` (`ProductGrid.jsx:167-174`), `qty` (`:175-183`),
  `salable_quantity` (`:83-90`, `:184-192`), `status` (`:204-213`), `visibility` (`:193-203`).
* **One exception:** `is_in_stock` is writable from the bulk form but is **not a Products-grid
  column**. Its only reader is `ProductEdit.jsx:143`, rendered as the Stock Status select at
  `:862-865`. Still user-visible and still what official 501–505 mutate — but do not expect to
  see it on the grid.

**The quantity filter is genuinely wired:** `filterType: 'range'` (`ProductGrid.jsx:176-178`);
`AdminGrid.jsx:674-704` renders `#filter-product_listing-qty` / `-qty-to` behind
`[data-action="grid-filter-expand"]`, committed by `[data-action="grid-filter-apply"]` (`:731`);
predicate `matchesFilter` (`gridUtils.js:179-194`), applied in `applyGridState` (`:212-226`).

**`selectAll()` (`AdminGrid.jsx:319`) and `selectAllOnPage()` (`:317`) resolve identically**
whenever the matched set fits one page — and with `GRID_PAGE_SIZES.product_listing = 200`,
small sets always do, so the instruction need not choose.

## B6-50 — three shopping_admin seed facts that change task design

1. **A fourth pristine low-qty anchor exists that the briefs omit: id 1415 `WS03-XS-Red`,
   qty 14** (alongside WH11-S-Blue 3, WS08-XS-Blue 3, MSH09-36-Black 4).
2. **`WS03-XS-Red` carries a NEGATIVE stock reservation (`-1`)**, so `salableQuantity()`
   (`ProductGrid.jsx:83-90`) renders `Default Stock: 15` against `Quantity 14.0000`. **Any
   "most units left" superlative over a band containing it has two defensible readings.**
3. **`status_enable` is a dead action on the pristine seed — all 2,040 products are
   `status: 1`.** A task exercising Enable must inject disabled rows first; otherwise a quarter
   of the grid's action surface is unexercisable.

CORRECTIONS #72a (sort route dead, filter route live), #72b (lower bound mandatory) and #89
all confirmed as stated.

## B6-51 — CORRECTIONS #88 IS WRONG: the Orders grid DOES have a Pending status filter

Lane 51, verified in **both** source and the served bundle.

`ORDER_STATUS_FILTER_OPTIONS` (`OrdersGrid.jsx:64-78`) lists 12 options **including
`{value:"pending", label:"Pending"}`**, and the same array appears twice verbatim in the
served bundle `dist/assets/index-DCS3ZT0D.js` (as `z6=[...]` and `iv=[...]`). **The advice in
#88 to route around it via keyword / date / total-range filters is unnecessary.**

Likely cause of the error: `orderStatuses.json` has no row whose *state* is `pending` (Pending
maps to state `new`). CORRECTIONS #106 records that correctly for the **comment box**; #88
appears to have generalised it from the status table to the grid's filter vocabulary, which
are **independent lists**.

**Related seed inconsistency:** the Pending orders disagree with themselves on `state` —
301–308 are `status:'pending' / state:'new'`, but **65 and 299 are
`status:'pending' / state:'pending'`**. Any injection fabricating `hold_before_state` must read
the specific order rather than assume `'new'`.

## B6-52 — shopping_admin order cancel/hold: persists, but only 12 orders are eligible

Writer and reader agree on `orderOverrides[<entity_id>].{state,status}`.

* **Writers:** `OrderActionRoutes.jsx:64-73` (`OrderCancel`), Hold at `:84-104` — both also write
  `orderComments[<id>]`. Bulk: `OrdersGrid.jsx:135-152` `patchMany`, `:154-165` `massCancel`,
  `:167-185` `massHold`.
* **Reader:** `getOrderGridRows` (`selectors.js:115-137`) merges `patch.status`; the Status
  column that renders and filters it is `OrdersGrid.jsx:296-308`. Order view via `getOrder`
  (`selectors.js:41-64`).
* **Controls:** `OrderView.jsx:250-262` `#order-view-cancel-button` (in-DOM confirm modal,
  `ConfirmModal.jsx`); `:291-301` `#order-view-hold-button` (no modal).

**`canCancel` (`orderHelpers.js:214-220`) leaves only 12 eligible orders — 10 Pending +
2 Processing.** Every complete/canceled/closed order is dead. The census's blanket "A10
partial" is too pessimistic: cancel/hold is narrow, not unimplemented.

**Sort:** default `{field:'created_at', direction:'desc'}` (`OrdersGrid.jsx:413`);
`created_at` declares no `sortValue`/`compare`, so `defaultCompare` (`gridUtils.js:200-206`)
falls to `localeCompare(..., {numeric:true, sensitivity:'base'})`. Fixed-width
`YYYY-MM-DD HH:MM:SS` makes lexicographic == chronological, **all 12 open orders have distinct
timestamps**, and `America/New_York` crosses no day boundary for any of them — so the
storefront's date traps do not apply to this grid.

Pending grand totals are **all ten distinct**: 219.40 / 215.00 / 210.00 / 192.40 / 183.50 /
179.40 / 175.40 / 101.20 / 91.00 / 76.40; tightest pair is **$4.00** (175.40 vs 179.40).
There is a **fifth** official cancel analogue beyond the four the briefs list: `Cancel order 305`
(webarena-474).

## B6-53 — the configurations wizard persists on the spot; there is no Save step

Lane 49. The path label "Configurations wizard → Generate Products → **Save**"
(from `stateTracker.js:130`) **overstates it**: `generateConfigurations`
(`ProductEdit.jsx:591`, terminal button `#generate_configurations` at `:1208`) writes and
persists immediately. There is no staged buffer, and **a replay ending at
`#generate_configurations` is complete.**

* **Writers:** `addProduct` (`AppContext.jsx:236-238` → `state.newProducts`, one row per pending
  combination, called at `ProductEdit.jsx:639`) and `patchProduct` (`AppContext.jsx:219-226` →
  `state.productOverrides[<parent>].{configurable_attributes, configurable_children}`,
  `:640-646`).
* **Readers of those same keys:** `getProducts` (`selectors.js:164-178`) and `getProduct`
  (`:154-161`), feeding `variants` (`ProductEdit.jsx:485-487`) and the Current Variations table
  (`:1089-1128`). Persisted via `setState` (`AppContext.jsx:167-174`) → `saveState` →
  `/post?action=set_current`.

**Admin keyword search:** `matchesKeyword` (`gridUtils.js:132-138`), invoked at
`AdminGrid.jsx:216` with the **full 37-column array**; per column it uses `col.searchValue(row)`
or `row[col.id]`. Contributing product columns are `entity_id`, `name`, `sku`, `url_key`
(`ProductGrid.jsx:251-253`, no `searchValue`), plus the rendered type / attribute-set / price /
qty / visibility / status / `Main Website` / formatted `updated_at`. **Every other hidden column
declares `searchValue: () => ''`.**

**Two families are unsafe for wizard tasks** because their seeded quantity is non-uniform, which
makes the wizard's Skip inheritance depend on `configurable_children[0]`: **MP12 Cronus {0,100}**
and **MSH09 Troy {4,100}**.

CORRECTIONS #83 (complete matrices) and #90 (keyword collisions) both reproduced; 147
configurables are all `['size','color']`.

## B6-54 — shopping_admin price fields: it is `special_price`, and it is not null throughout

Lane 50, all four points measured.

1. **The field is `special_price`, not `specialPrice`.** A reward keyed on the camelCase
   spelling several briefs used reads **nothing, silently**.
2. **"specialPrice is null throughout" is over-general** — six products carry one: ids
   **2, 10, 11, 16, 41, 42**. None is in an apparel line, so apparel-line conclusions survive,
   but the blanket claim does not.
3. **A configurable parent's price is not generally null.** CORRECTIONS #86 is right about MH05
   (126), but **only three products in the entire seed have a null price**. A scope gate over
   parents should assert a *value*, not absence.
4. **`MH05` — the entity several briefs lead with — has ZERO reviews**, so it cannot carry any
   review-content retrieval.

There is **no `finalPrice`** on this mock; the graded key is `price`. Writers: single
`ProductEdit.jsx:351` (`patch.price` in `buildPatch`, saved `:389`); bulk `ProductGrid.jsx:490`
in `applyBulkAttributes`, applied `:502`. Both land in
`AppContext.jsx:218-227` → `productOverrides[<id>].price`. Reader: `getProducts`
(`selectors.js:164-179`) merges the override; `ProductGrid.jsx:167-173` renders
`formatCurrency(r.price)` from it.

**Catalog keyword collision worth knowing:** a `WB01` query returns **17** rows, not 16 — the
extra is product 8 `24-WB01` Voyage Yoga Bag. Product-*name* queries return 16.

## B6-55 — a cross-report figure mix-up in the briefs, and a blank-not-zero column

Lane 53 ported the report pipeline to Python and reproduced every census figure it used —
Shipping 2022 215/$3,145.00, Shipping 2023 85/$1,270.00, Orders 2022 116/$15,475.46, Orders
2023 42/$5,873.48, plus three in-source controls including Jan-2022 Any = 11/$1,591.89.

**One brief figure does not reproduce and must not be used:** the note
"Order Count 2022 … 36 rows / 116 orders / **$13,695.82**". The Orders Report's 2022 Sales
Total is **$15,475.46**. Two different reports' quantities were quoted as if they were one —
exactly the cross-report mix-up CORRECTIONS #87 warns about.

**Shipping 2023's `Total Shipping` column renders BLANK, not `$0.00`** (an all-NULL `sqlSum`
group). A reward expecting `$0.00` there would never match.

**The custom-variable vessel persists and is read back.** Writer: `CustomVariableForm.onSave`
→ `useSystemCollection('variables','variable_id').add` (`Tools.jsx:1005-1007`), whose `write`
sets `systemConfig.variables` (`RecordForm.jsx:31-37`). Reader: the `CustomVariables` grid
renders `state?.systemConfig?.variables || []` (`Tools.jsx:29`) — same key. Baseline is `[]`
(`dataManager.js:280-281` + `src/data/systemConfig.json`), so an untouched state scores 0.0.

`ReportGrid` genuinely renders a `tfoot` Total row (`ReportPage.jsx:363-375`), so a
whole-report total is a legitimate single rendered cell. Keep every Period=Year window inside
one calendar year or CORRECTIONS #94's silent-drop trap fires.

## B6-56 — injected reviews always render at the TAIL of the Created-descending grid

**In neither the census nor AUTHOR_BRIEF, and a live hazard for any lane that injects reviews.**
Found by lane 52.

`reviewRank()` (`src/components/reviews/reviewDefaultOrder.js:70`) ranks **unmeasured ids as
`351 + id`**. So an injected review renders at the **tail** of the Created-descending grid
however recent its `created_at`. A naive injection puts the newest review at the *bottom* of a
"Created ↓" list, and any "newest pending review" task then answers wrongly.

**Workaround that works:** invert the injection dates — make every injected `created_at` older
than the oldest seeded review (**2023-04-19 16:15:10**), with ids ascending as dates descend, so
the rendered column stays monotone.

**A lane needing an injected row at the HEAD of that queue cannot get one this way at all.**

Also: **`Reviews.jsx:148` early-returns on a blank status** — choosing Update Status and pressing
Submit without setting `#status` mutates nothing. `#status` is rendered on cold load and merely
hidden (`LegacyReviewGrid.jsx:335-345`), so it is reachable but easy for a replay to skip.

Confirmed again: the admin corpus is 351 reviews / 346 Approved / 5 Pending / 0 Not Approved.
Review grid page size is 20 (`LegacyReviewGrid.jsx:94`); `selectAll` (`:261-262`) selects all
matches across pages while `selectVisible` (`:264`) selects only the slice — they coincide only
when the matched set fits one page.

## B6-57 — the Dashboard answers "best seller" from `/`, and Shipping cannot rank carriers

Lane 54, the Bestsellers analogue of CORRECTIONS #107.

**`Dashboard.jsx:29` defaults to the Bestsellers tab**, and `:74-112` renders an all-time top
five whose row 1 is `Sprite Stasis Ball 65 cm`. **A naive "which product sold best" task is
answerable from `/` without opening any report** — the retrieval is not forced. Avoid all five
panel names, or target a row the panel does not show (using the panel's third row makes a
panel-copying agent score 0.0).

**Shipping cannot rank carriers.** The report has real data (516 rows), but
`shipping_description` is `Flat Rate - Fixed` in **516 of 516 rows** — it can only rank
intervals.

**The cart-price-rule surface persists.** Writer `save()` (`Marketing.jsx:239-261`, record
literal `:206-237`) → `state.cartPriceRules` (+ `state.coupons` at `:245-258`). Reader
`CartPriceRules()` (`Marketing.jsx:57-58`), grid `:118-122`, edit form `:190-192`;
`stateTracker.js:156-157` agrees; seeded by `dataManager.js:261-263`. Note `discount_amount`
is **stored as a string** (`:219`), so compare as `Decimal` after stripping `$` and `,`.

The brief's suggested entity — top search term `hollister` — is a **Search Terms** retrieval,
not one of the three live reports, and CORRECTIONS #107 already shows the Dashboard answers it.

## B6-58 — entity-name trap: WP05 is "Sahara Leggings", not "Sahara Tights"

Lane 57. Several briefs list the entity as "Sahara WP05 (1847)" glossed as *Sahara Tights*; the
seeded name is **Sahara Leggings**. A keyword search for "Sahara Tights" returns **nothing**.
Same family as CORRECTIONS #90's `Chloe Tank` / `Cora Pant` trap — check the seeded `name`
before quoting an entity in an instruction.

Confirmed in the same pass: CORRECTIONS #80 (147 configurables), #82, #83 (complete matrices),
#86 (entity 126 `price: null`), B6-45's `patchProduct`/`getProducts` writer-reader pair, and the
200-row `product_listing` page size. **CORRECTIONS #81's step-1 disappearance of Size only
applies when a task saves the Size attribute** — a wizard task that does not save it will not
see the missing row, so do not read its absence as a bug.

Useful seed constants for wizard payloads: **quantity is 100.0 on 1,842 of 1,847 seeded child
rows**, so any injected non-100 quantity is unique on its line and makes a clean derived target.
MH02 Teton is 70.00 on the parent and all 15 children; WP04 Cora is 75.00 on the parent and all 6.

## B6-59 — Bestsellers superlatives: 24 usable winners, but NAME uniqueness is the real constraint

Lane 55, over all windows inside 2022/2023.

* **"Both are safe at rank 1 and only at rank 1" is far too narrow** — **24 distinct products
  hold a tie-free rank 1** over some window inside 2022/2023, not just the two calendar-year
  figures the briefs quote.
* **The binding constraint is catalogue NAME uniqueness, which no census or brief mentions.**
  The Bestsellers report renders only the product *name*. Entity 29 (9/2022) has a tie-free
  rank 1, but **three products share the name "Sprite Stasis Ball 65 cm"** (27/28/29, all
  $27.00), so the action target is unresolvable. Same for the "55 cm" family. **Check that the
  winner's name is unique in the catalogue, not just that its quantity is unique.**
* **CORRECTIONS #101 extended:** recomputing all ten windows from `orders.json` over
  **non-canceled** orders reproduces the frozen aggregate exactly, so the live Ordered Products
  route agrees (`LegacyReports.jsx:551`). **Including canceled orders changes the winner in 7 of
  10 windows** — the status filter is load-bearing, not cosmetic.

**A rounding rule that disagrees with itself across implementations:** −7.5% on $29.00 = 26.825
rounds **down** in float (26.824999999999996) and **up** under `Decimal` + `ROUND_HALF_UP`.
Prefer percentages whose result is an exact binary float (e.g. 48.375, 14.875) for any task that
states half-up rounding.

`special_price` is null and `type_id` is `"simple"` on all ten targets used, so only one price
renders and `ProductEdit.jsx:349-350`'s configurable-parent refusal never applies.

## B6-60 — CORRECTION TO B6-52: the "no day boundary" claim covers only the 12 OPEN orders

**My error when relaying B6-52.** Lane 51 measured that `America/New_York` crosses no day
boundary — but **only across the 12 cancel-eligible orders**. I generalised it to the whole
grid when briefing lane 58, which recomputed it with DST over all **308** grid rows and found
**59 orders render a day earlier than they filter** (e.g. 000000284, stored
`2023-05-01 00:42:12`, renders `Apr 30, 2023`).

**Day windows on the admin order grid are usable, but the UTC hour must be screened.** A target
whose UTC hour is ≥ 5 renders on its stored date; below that it can shift.

The grid's *sort* and its *filter* behave differently and both matter:
* **Sort:** `defaultSort {field:'created_at', direction:'desc'}` (`OrdersGrid.jsx:413`); no
  `sortValue`/`compare`, so `defaultCompare` (`gridUtils.js:200-206`) → `localeCompare`, which is
  chronological on fixed-width `YYYY-MM-DD HH:MM:SS`. Rendering is `formatDateTime`
  (`formatters.js:41-46`) via `tzParts` in `America/New_York` (`:10`).
* **Filter is timezone-free and clean:** `compareDates` (`gridUtils.js:162-170`) compares the
  **stored** `created_at[:10]` string, inclusive at both ends, accepting M/D/YYYY via `toIsoDate`
  (`:149-160`).

## B6-61 — 616 order-address edit routes resolve, and injected orders cannot be A11 targets

Lane 58, and it is what makes an address lane possible without touching benchmark gold entities.

* The census's "orders with address-edit routes: 299, 65, 301, 300, 125" is **a sample, not an
  enumeration**. `orderAddressIndex` (`staticData.js:79-85`) indexes **every** address of every
  seeded order, and all 308 orders carry both — so **616 address-edit routes resolve**.
* **Injected orders cannot be A11 targets.** `orderAddressIndex` is built from the frozen
  `orders.json` only, so a `newOrders` row's Edit link renders `NotFound`.
* Writer: `patchOrderAddress` (`AppContext.jsx:209-217`) → `orderAddressOverrides[String(addressId)]`;
  sole call site `OrderAddressEdit.save()` (`OrderAddressEdit.jsx:160`) behind `#save` (`:207-216`).
  Readers: `getOrderAddress` (`selectors.js:145-150`) and `getOrder` (`:53-59`), rendered by
  `AddressInformation` (`OrderBlocks.jsx:192-228`), mounted at `OrderView.jsx:130`; the Edit links
  at `OrderBlocks.jsx:205`/`:218` are the click path.
* **CORRECTIONS #91 confirmed:** `getOrderGridRows` short-circuits at `selectors.js:117`
  (`if (!patch) return row`) *before* the address merge at `:123`. Writing the order's own seeded
  `updated_at` into `orderOverrides` is a value-for-value no-op that makes the short circuit fall
  through, so a saved address also reaches the hidden Billing/Shipping Address columns.
* **All seeded orders carry field-identical billing and shipping addresses**, so any
  "copy billing onto shipping" task scores **1.0 untouched**.

## B6-62 — `#history_status` empties on `state:"pending"`, NOT on status Pending

Lane 59 narrowed a claim that was steering lanes away from usable orders.

`statusOptions` filters on **`order.state`**, not `order.status` (`OrderView.jsx:391-394`), and
`orderStatuses.json` does carry `{status:"pending", state:"new"}`. **Eight of the ten Pending
orders (301–308) are `state:"new"` and render one correctly preselected option.** Only
**000000065 and 000000299** are `state:"pending"` and render an empty select.

So "the status dropdown has zero options on a pending order" is false in general — it is true
for exactly two orders. (This is the same `status` vs `state` conflation behind B6-51's wrong
#88 entry.)

## B6-63 — shopping_admin order/customer set: the real numbers, and three dead join keys

Recomputed by lane 59 from `orderGrid.json` / `customerGrid.json`. **The storefront figures the
briefs quote for orientation do not transfer.**

* **308 orders**, status mix **153 complete / 142 canceled / 10 pending / 2 processing /
  1 closed**.
* **36 of 70 customers have orders; 0 orphans.**
* **April 2023 is NOT empty here — it holds 26 orders**, nine of them in a 2023-04-19
  23:41–23:42 cluster. (The empty-April fact is storefront-only.)

**Dead join keys — do not build a retrieval on these:**
* **Customer DOB and gender are non-null for 1 of 70 customers.**
* **36 of 70 `created_at` values render as the same date** under `formatDate`.
* **ZIP / city / state are not a real join**: `orderGrid.billing_address` is
  `street,city,region,postcode` and hidden columns are still filterable
  (`AdminGrid.jsx:405-412`), so an address key is answerable inside the Orders grid alone.

**Telephone IS a real join key:** `OrdersGrid.jsx:250-386` enumerates every `sales_order_grid`
column, visible and hidden, and **there is no telephone column and no telephone filter anywhere
in Sales** — so a phone number forces a hop through Customers > All Customers
(`CustomerGrid.jsx:79-84`).

**The Customers grid has no clickable row** and its Action column ships hidden
(`CustomerGrid.jsx:268-282`, no `rowHref`), so there is no rendered link from that grid to a
customer page until the Columns control is used. A lane planning "filter customers, then click
through" has no click path.

**Order comments persist:** writer `CommentForm.submit` (`OrderView.jsx:395-429`) →
`state.orderComments[String(entity_id)]` at `:415`, key declared `dataManager.js:345`. Readers
`getOrderComments` (`selectors.js:140-142`) → `OrderView.jsx:42` → `StatusHistoryNoteList`
(`:500`, rendered `OrderBlocks.jsx:468-491`), and `fullOrderHistory`
(`orderHelpers.js:407-424`) → Comments History tab (`OrderView.jsx:179-188`,
`OrderCommentsHistory.jsx:31`).

## B6-64 — the capture/listingKey hazard does NOT exist on shopping_admin

Lane 56, and this is a finding rather than a skipped check. `listings.json`, `resolveListing`,
`catalog.js pool.slice()` and the `product_list_order` Toolbar are **all in
`webarena_shopping_mock`**. `webarena_shopping_admin_mock/src/data/` contains **no listings file
and no capture layer**: every admin superlative runs through `gridUtils.applyGridState` over
`getProducts(state)`, or `reportUtils.bestsellersRows`, or the two legacy report bodies.

**B6-37's kids-bedding / competitive-swimwear / heating-cooling-air-quality hazard has no
analogue on this site.** The two admin equivalents to check instead are
`GRID_PAGE_SIZES.product_listing = 200` (boundary splits) and the **inclusive** `{from,to}`
numeric range semantics at `gridUtils.js:179-197`.

## B6-65 — three Dashboard leaks and a Bestsellers branch nobody documented

1. **`bestsellersRows` does NOT read `bestsellers_yearly` for a single-calendar-year request.**
   `reportUtils.js:265-268` sets `mainDisabled` and unions a `boundarySelect` over
   **`bestsellers_daily`**. Documented nowhere. Rank 1 happens to agree under both paths, but
   **a task grading a quantity off that report must re-derive under the branch it will actually
   trigger.**
2. **The Dashboard search-term leak is total, not a caveat.** `Dashboard.jsx:67-72` renders the
   ranked Top Search Terms panel on `/`, so `hollister` is answered **before any navigation**.
   Search-term retrievals are not forceable.
3. **The Dashboard Bestsellers tile DISAGREES with the Bestsellers report at rank 1** — the tile
   reads store 0 across all years (`Dashboard.jsx:76-77`, first row Sprite Stasis Ball 65 cm)
   while the report reads store 1 (`reportUtils.js:213`). This is usable as a deliberate trap:
   an agent shortcutting to the tile scores 0.0. It is also a hazard if you assume they agree.

**CORRECTIONS #72b confirmed:** "fewer than 20 units" is unusable as a filter — **150 rows sit at
qty 0**, several priced below $54. State a lower bound of 1.

Seed baseline: all 2,040 rows are `status: 1`, and **exactly one row has `is_in_stock: 0`**
(entity 872).
