# Corrections to inherited findings — batch 5

Every claim below was verified at source by a batch-5 census agent and
contradicts something batches 1–4 recorded as fact. TASK4.md S10 says to treat
any mechanism claim as unverified until you have read the handler yourself;
this file is what that instruction produced when actually followed.

## shopping_admin

1. **`setUi` / `ui.dismissedAlerts` does not exist *in shopping_admin* — but
   the batch-4 finding was about gitlab, and there it is correct.** Withdrawn
   as a correction; recorded as a mis-attribution.

   In `webarena_shopping_admin_mock` the census is right: `AppContext.jsx` is
   351 lines, line 344 sits inside `useApp()`, `grep -rn setUi src/` returns
   five hits that are all `setUiSelectOpen`/`setUiSelectQuery` local `useState`
   in `AdminGrid.jsx:176-177`, and no `ui` key appears among the 44 persisted
   state keys.

   In `webarena_gitlab_mock`, every part of the original claim checks out:
   `src/context/AppContext.jsx:344` is literally
   `const setUi = useCallback((patch) => {`, `grep -rn setUi src/` returns
   **27** hits, and the persisted `ui` object carries
   `dismissedAlerts`, `notificationLevels`, `preferences`, `projectSettings`,
   `sidebarCollapsed`.

   *Consequence: `ui.dismissedAlerts` is usable on gitlab and unusable on
   shopping_admin. The batch-4 note failed only by not naming its site, and
   this file initially compounded that by calling it fabricated on the strength
   of a census that had been pointed at the other mock.*

2. **The CMS toggle interception is real, the mechanism was wrong, and the
   selector is wrong for one of the two pages.** The 1x1 input is not an overlay
   — it *is* `#block_is_active`, deliberately shrunk so Playwright's
   actionability check accepts it (`adminForm.css:164-180`). The bug is a
   missing containing block: `CmsBlocks.jsx:178` and `CmsPages.jsx:340` hand-roll
   `.admin__field-toggle`, which has zero CSS rules anywhere, instead of
   `.admin__actions-switch { position: relative }`. So the checkbox lands at the
   document origin under `.admin__menu-wrap { z-index: 700 }`.
   *Consequence: the remedy `label[for="block_is_active"]` is correct on Blocks,
   but Pages uses `page_is_active` — `label[for="page_is_active"]`. The
   `<span class="admin__actions-switch-label">` pill is a span, not a label, and
   is not a click target in either form.*

## shopping

3. **`SCHEMA.md`'s corpus counts are stale by roughly 2x.** It documents 11,358
   products and 32,594 reviews; the seed holds **22,721 products** (22,460
   listable under `isListable()`, `utils/catalog.js:118`) and **76,378 reviews**
   across 6,044 products. Any task sized against the documented figures is
   sized against the wrong corpus.

4. **The star-rating finding is confirmed in mechanism and refuted in
   consequence.** `globals.css:719` does stack five 1x1 `opacity:0` inputs, but
   `globals.css:720-724` gives each `<label>` `font-size:20px` and
   `content:'\2605'` — five real, clickable 20px stars.
   *Consequence: the widget is usable. Click `label[for="Rating_N"]`, never the
   input. DOM order is ascending `Rating_1..Rating_5`, so the fifth radio is
   five stars — the opposite of Luma's visual reversal, and a positional replay
   is correct here.*

## Method note

Two of these four ("no `setUi` writer exists", "the star widget is not a Luma
sprite") were themselves *corrections* recorded during batch 4, and both were
wrong in the part that mattered. The pattern is that a claim gets refined
enough to sound verified while the operative consequence is never tested. The
census format used this round — verdict, route, handler file:line, two entity
examples, tie margin — exists to make that failure mode harder.

## reddit

5. **`ForumEditPage` always writing `tags: []` is STALE for this revision.** The
   field is seeded from the forum at `ForumEditPage.jsx:55` and split on save at
   `:77`. Verified by live probe: saving `alpha, beta` produced
   `tags: ["alpha","beta"]` in `/go` `current_state`.
   *The general advice it was attached to remains independently correct, for a
   different handler: `AccountPage` really does write `currentUser.email` on
   every submit whether or not it changed (`SCHEMA.md:296`), so gate rewards on
   the recorded value, never on "a write happened".*

6. **`DeleteSubmissionPage.jsx:30` forbidding deletion of another user's post is
   CONFIRMED** — both by reading the guard and by loading
   `/f/DIY/119019/-/delete`, which returns `403 Forbidden`.
   `EditSubmissionPage.jsx:51` is the same.
   *Consequence, which batch 4 did not draw: moderation is effectively
   unreachable as a skill on this site. Forum editing 403s unless you moderate
   the forum (`ForumEditPage.jsx:42`), all 95 seeded forums have zero
   moderators, and the only forums an agent can moderate are ones it just
   created — which contain nobody else's content to moderate.*

7. **The `PreferencesPage` sort finding is confirmed in fact and wrong in its
   conclusion.** `PreferencesPage.jsx:95-99` does offer only `hot|new|active`.
   But that control is the **front-page default-sort preference**, and upstream
   Postmill's own form offers exactly those three; no official task sets it. The
   "top post ever" tasks use the **listing** sort `/f/{f}/top`, which exists and
   works (`listing.js:36`, probed at `/f/DIY/top?t=all`). Nothing about the
   official corpus is contradicted.
   *This was recorded in batch 4 as "no Top sort option exists", which reads as
   a capability gap and is not one.*

## Method note, extended

Five of the seven corrections above are corrections **to batch-4 corrections**.
The recurring failure is not sloppiness about the mechanism — batch 4 usually
read the right file — it is that the *consequence* was inferred rather than
tested. "The input is 1x1 and invisible" is true and does not imply the widget
is unclickable. "The sort dropdown lacks Top" is true and does not imply top
sorting is unavailable. The remedy this round was requiring each census to name
a route, a handler `file:line`, two entity examples and a tie margin, and where
possible to drive a live browser; the reddit census did drive one, and it is
the report that overturned the most.

## gitlab

8. **`SCHEMA.md`'s corpus sizes are stale by roughly 30x on the big tables.** It
   documents 613 issues, 729 merge requests, 1,133 users, 630 labels and 202
   milestones. The seed actually holds **19,705 issues, 23,236 merge requests,
   2,199 users, 1,254 labels and 343 milestones** (175 projects, 183 members,
   569 stars, 5 follows and 7 todos *are* correct). A round-20 expansion was
   never written back into the doc.
   *Consequence: no task may be sized off SCHEMA.md's record counts.*

9. **`commits.json` is capped at 40 rows per ref, and three pages disagree
   about the same repo's commit count.** `byteblaze/dotfiles:main` holds 40 of a
   real 553. `ProjectOverview.jsx:213` documents the cap, but
   `RepoAnalytics.jsx:53` aggregates `getCommits()` anyway — so
   `/-/graphs/main/charts` reports "40 Commits, 1 Author", `/-/graphs/main`
   reports "552 commits by 2 contributors", and the overview reports 553.
   *Consequence: any commit-count task must be pinned to the Contributors page
   (`/-/graphs/:ref`), which reads `contributors.json` and is the only correct
   one.*

10. **WITHDRAWN — the issue-list state-tab counters ARE filter-aware.** This
    entry previously claimed the opposite, on the census's authority, and it was
    wrong. Verified at source:

    * `IssuablesList.jsx:888` does compute a `counts` object from unfiltered
      rows — but nothing references it. It is dead code, and it is what the
      census read.
    * The rendered badges come from `IssuesList.jsx:35`,
      `const counts = issuableStateCounts(rows, q, indexes)`, passed to
      `StateTabs` at `:40`. `hooks.js:39-50` implements that by re-running
      `filterIssuables` with `state` forced to `all` and then counting by state,
      so every filter except `state` itself is honoured. `MergeRequestsList.jsx`
      is the same.

    *Consequence: "how many open issues carry label X" CAN be read off the
    badge, and a batch-2 note saying so — which batch 4 retracted — was correct
    all along.*

    This entry is left in place rather than deleted because the failure is
    instructive: the census found a variable with the expected name at a
    plausible line and never checked whether anything used it. Three layers of
    correction later, the original claim was right. **Grep for the reference,
    not just the definition.**

## Two more stale-documentation findings, same shape

Note that findings 3, 8 and 9 are all the same failure: a mock's own `SCHEMA.md`
describing a corpus that a later round replaced. Three of the four sites are
affected (shopping ~2x, gitlab ~30x, and gitlab's commit cap). The reddit census
found the equivalent trap in the rendered UI rather than the docs — forum cards
show the source database's `submissionCount` (news: 3,322) while the listing
holds 113 rows, so "how many posts are in f/X" has two defensible answers.

**Standing rule for batch 5: size every task against the JSON in `src/data/`,
never against `SCHEMA.md` and never against a rendered count.**

## Environment: the hub serves `dist/`, not `src/`

11. **The mocks run under `vite preview`, which serves the prebuilt `dist/`
    directory and never reads `src/`.** All five have been running since
    2026-08-17; `dist/` was built the same day. Two mocks have source files
    edited on 2026-09-02 whose changes are therefore **not live**:

    * `webarena_gitlab_mock/src/components/layout/routeContext.js`
    * `webarena_reddit_mock/src/components/Sidebars.jsx`
    * `webarena_reddit_mock/src/components/layout/SiteNav.jsx`
    * `webarena_reddit_mock/src/pages/ForumModeratorsPage.jsx`

    shopping and shopping_admin are clean — their `dist` is newer than their
    `src`, so source-reading is sound for those two.

    *How it surfaced:* the reddit census read `src/` and reported that "Mod
    trash" appears in the user menu. The string occurs **zero** times in the
    served bundle. It caught its own error; the general form would not always
    be caught, because source-reading is the primary research method for
    authoring.

    *Resolution — do not rebuild.* `hub/` is read-only by contract, and more
    importantly the training rollouts serve the same `dist/`, so authoring
    against a rebuilt bundle would produce tasks that do not match what agents
    actually see. The served build is the ground truth, exactly as TASK4 S2
    says: a mock's behaviour is a fact to design around, not a bug to fix.
    `scripts/check_served_build.py` reports the gap so it cannot go silent.

    *Standing rule:* a claim read from `src/` is only as good as the build. Any
    claim touching the four files above must be verified against the running
    app.

12. **The stale build is not cosmetic — it breaks click-reachability on gitlab
    Settings.** Re-probing §4.4 against the served bundle (sids `census44`-`e`)
    found that clicking **Settings** on a project lands on the legacy
    `/:ns/:proj/edit` route, and the sidebar section that expands there is
    **Repository**, not Settings. So `/-/settings/repository`,
    `/-/settings/ci_cd`, `/-/hooks` and `/-/settings/access_tokens` are **not
    directly click-reachable**. They are recoverable only by a four-hop detour
    through an incidental "Merge requests" link in the General page body, which
    lands on a `/-/` route and makes the section resolve correctly. Probed both
    ends: on `/-/settings/merge_requests` all eight panes are visible, on
    `/edit` none are.

    A URL-derived section resolver failing on the one legacy route outside
    `/-/` is precisely the job of `routeContext.js` — the un-served file. So the
    fix exists in `src/` and is not deployed.

    *Consequence: author against the broken behaviour.* Under TASK4 S6 a task
    whose scored control sits behind that detour is not reachable, and batch 4
    lost 190 tasks to exactly this class of defect. The casualty is small — one
    optional `ui.projectSettings` writeback variant, dropped — because no
    proposed topic depends on a Settings pane.

13. **GitLab's sidebar sub-items do not appear on hover.** Thirteen hover pairs
    all returned `child_visible: false`. The working gesture is: click the
    section link, land on its default page, then click the child. Also
    **CI/CD Analytics and Repository Analytics live under *Analytics*, not
    *CI/CD*** — from `/-/pipelines` only `Jobs` renders and `charts` does not.
    The census's original flat-sidebar description was a `src/`-reading error
    and is corrected.

    *This is the general lesson of findings 11-13: reachability is a property of
    the served build and of the gesture, and neither can be read out of source.*

14. **Reddit forum deletion is not available to moderators, retracting a census
    claim.** `ForumDeletePage.jsx:32-34` implements `Forum::userCanDelete()`,
    which permits deletion **only when `submissionCount === 0`**. Probed:
    `/f/DIY/delete` with `moderatorOf` set returns **403**. The census had
    described forum delete as "the largest observable diff on the site,
    cascading ~96 submissions" on the strength of `ROUTES.md` rather than the
    guard, and withdrew it on re-check.

    *The big-diff shape survives as forum **rename**, driven end to end: all 96
    DIY submissions follow, `forumRenames: [{from: DIY, to: DIYRenamed}]` is
    written, and `/f/DIY` stops resolving.*

    Also dropped on the same pass: `add_moderator` is `ROLE_ADMIN`
    (`ForumModeratorsPage.jsx:55`, probed 403, no link rendered), so A3-grant is
    unavailable on reddit; `/trash` is a permanent empty state because nothing
    can be trashed into it; and `suggestedTheme` is a dead control whose select
    has exactly one option.

    *Note the shape of this one: it was not caused by the stale build. It was a
    documentation-over-source reading, the same failure as findings 3, 8 and 9.*

15. **Most gitlab projects do not default to `main`.** 134 of 175 have a
    different `default_branch`, including four of byteblaze's twelve —
    `cloud-to-butt`, `timeit`, `solarized-prism-theme` and
    `millennials-to-snake-people` are all `master`. The gitlab census gave the
    file writeback key as `repo.fileOverlay['<full_path>:main:LICENSE']` and
    cited a live probe of `/byteblaze/cloud-to-butt/-/new/main`, which does
    render — but only because `NewFile` takes `params.ref` verbatim without
    validating it. The commit then lands on a branch the repo does not have and
    is invisible on the default branch.

    *Consequence: a reward built on the census key scores a **correct** run
    0.0.* Found by a lane that checked rather than inherited; the delivered
    corpus was swept and no other bundle carries the defect.

16. **The gitlab dashboard's "Personal" tab does not narrow to byteblaze.** It
    filters `namespace.kind === 'user'`, and every seeded namespace is
    `kind: "user"` — including `a11yproject` (2500) and `primer` (2548). A task
    phrased "my projects" that expects that tab to scope the list is wrong.

17. **`a11yproject/a11yproject.com` renders an "Add LICENSE" chip although it
    has a licence**, because the file is named `LICENSE-APLv2` and
    `ProjectOverview`'s `/^licen[cs]e(\\.\\w+)?$/i` test rejects it. Any
    "which of my repos lacks a licence" derivation must account for it.

18. **The gitlab bulk `Subscriptions` field is write-only — never grade it.**
    `IssuablesList.jsx:657` writes `patch.subscribed`, but `IssueDetail.jsx:136`
    and `MergeRequestDetail.jsx:180` both derive the rendered toggle from
    `state.ui.unsubscribed`. A bulk Subscribe therefore mutates persisted state
    that **no page renders**, so a reward gating on it would pass while the
    agent's work is invisible — and an agent doing the visible thing instead
    would fail. A lane dropped a subscription task over this.

19. **`byteblaze/a11y-webring.club` is unusable for bulk-triage chains.** All
    four of its open issues are already assigned to byteblaze, so any assignee
    component is pre-satisfied at t=0, and the project has exactly one member,
    so the members-only bulk assignee select offers nobody else. The census
    named it as the anchor project for that topic. The only three
    label-carrying projects with more than one member are `primer/design`,
    `a11yproject/a11yproject.com` and
    `opensourcediversity/opensourcediversity.org`.

20. **`projects.json.open_issues_count` is a stored counter, not a list length,
    and the two diverge by an order of magnitude.** `OpenAPITools/openapi-generator`
    reports 3,476 open issues while only **243** of its issues exist in
    `issues_index.json`; keycloak is 1,604 vs 128; `a11yproject.com` is 40 vs 30.

    *Consequence: the site-wide "most open issues" RANKING survives — the
    ordering is unchanged — but any task grading the COUNT is graded against a
    number no page can render from its own rows. Rank on the counter if you
    must; never ask the agent to reproduce it.*

    This is the same class as finding 9 (three surfaces, three commit counts)
    and the reddit forum-card `submissionCount` trap: a stored aggregate and a
    rendered list disagreeing. It is now the most repeated defect shape in the
    four mocks — **assume any stored count disagrees with its list until
    checked.**

21. **Reddit's "newest" is ambiguous in 59 of 95 forums.** `/f/<forum>/new`
    sorts by **id descending** (`listing.js:34`), not by timestamp, and the two
    orders disagree at the head of 59 forums. `f/DIY`'s `/new` head is id
    119019 at 2023-03-31 19:01, while id 118903 is dated 23:55 — later in time,
    lower in id. Because `Time.jsx:12` exposes absolute datetimes in the `title`
    and `datetime` attributes, both readings are available to an agent and both
    are defensible.

    The reddit census asserted "'newest' never ties", which is true of ids and
    misses this entirely — and all three entities it handed out (`f/DIY 119019`,
    `f/space 134164`, `f/Futurology 119517`) sit in the ambiguous set.

    *Only 36 forums have the two orders coincide at the head.* Draw from those,
    or name the intended order in the instruction.

22. **`facebook/metaseq` does not exist in the gitlab mock.** MetaSeq is
    `root/metaseq` (project id 33); the `facebook` namespace holds only `buck`
    (60) and `create-react-app` (122). The census and the derived lane facts
    both named `facebook/metaseq` as a fork upstream — inherited from the
    official intent text, which refers to the real GitHub path.

    The mock itself was never wrong: `pages/ForkProject.jsx:13` already renders
    the header as `root/metaseq`. Only the documents derived from the benchmark
    carried the error.

    *General form: an official intent names entities as they exist on the real
    site. The mock's namespaces do not always match. Resolve every entity
    against `src/data/`, not against the benchmark string.*

23. **45 of the reddit user's 46 own submissions have no `body` key at all** —
    43 are link posts and 2 are image posts. The census and the derived lane
    brief described the own-post edit chain as "append the stated `EDIT:` line
    to the existing body, preserving the original", which is impossible for all
    but one post.

    The single exception is submission `1` ("Nvidia RTX 4090", body
    `Crazy device for ML!`) — which is precisely the post that lane must avoid,
    because it IS official `webarena-731`.

    *The official corpus agrees with the data rather than with our brief:*
    `webarena-731` is the only one of the five R9→A1 edit tasks scored
    `must_include` on both the original and the appended line; `732`, `733`,
    `734` and `735` are all `exact_match` on the new line alone. So the correct
    rubric is `body == <the line>`, not `<original> + <the line>` — which is
    what the ten bundles now assert.

    *General form: when a brief and the seed disagree, check what the OFFICIAL
    task actually scores. Twice now it has sided with the data.*

24. **Reddit submissions have TWO legitimate `ranking` conventions, and copying
    the wrong one puts an injected post above the entire corpus.**

    * **Seeded corpus rows: `ranking == netScore`.** Verified across `f/science`
      (91397: 16886/16886, 112582: 16453/16453, 47614: 11634/11634) and holding
      for 8,011 of the 8,012 seeded submissions.
    * **Rows `createSubmission` writes: `ranking` is epoch seconds.** Submission
      `1` carries `1686590745` — the census's only `ranking` datum, and it is
      this second convention.

    The hazard is that the census presents the epoch value as *the* example. An
    author injecting a row meant to look like part of the seed, who copies it,
    produces a post that sorts above all 8,012 on `hot`.

    *Which is correct depends on what the row simulates.* A record standing in
    for pre-existing corpus content takes `ranking == netScore`; a record
    standing in for something the user posted themselves takes the epoch value,
    because that is what the handler would really have written. Say which in
    `metadata.injected_preconditions`.

    Swept the delivered reddit bundles: 12 injected rows use the netScore
    convention, 2 use epoch — those 2 simulate a prior user post, which is the
    case where epoch is right, and are being confirmed with their author.

25. **On the pristine reddit seed, the Top listing and the Hot listing are the
    same list.** Because `ranking == netScore` holds for all 8,012 seeded
    submissions (finding 24), the full Hot ordering equals the full Top ordering
    in **94 of the 95 forums** — `f/MachineLearning` differs only because of the
    fixture submission `1`.

    *Consequence, and it is a consequence about task quality rather than
    correctness:* `/f/X/top?t=all` renders exactly what `/f/X` renders, in the
    same order. So the `?t=day`-returns-zero-rows trap that the census documents
    at length is a trap the agent **walks around** — it can ignore the time
    filter entirely, never touch the sort control, and still land on the right
    post. The R5 faceted-navigation skill the lane exists to train is
    unobservable in the reward.

    This is the failure mode the batch-5 contract was written against: a task
    that looks like it exercises a skill, scores as if it does, and does not.
    Nothing static detects it — the reward is correct, the replay passes, the
    tie audit is clean.

    *The fix is injection used as a design tool:* nine bundles republish the
    target through `submissionEdits` with `ranking` lowered to roughly position
    40 of Hot — page 2, since listings page at 25 — while leaving `netScore`
    untouched. The Top and Hot orders now differ, so the agent must actually use
    the sort control and the time filter to find the target.

    **Generalise this: after designing a chain, ask whether an agent that
    skipped the retrieval step would still succeed.** If yes, the retrieval is
    decoration. That question is worth asking of every R5 and R10 task in the
    batch.

26. **Every census tie audit is rank-1 only, and none of them say so.** The
    reddit census's "most commented ties in exactly four forums" is true of the
    TOP spot. `f/history` carries a three-way tie at 206 across ranks **2-4**,
    which is invisible to a rank-1 audit and silently kills any "top 3 most
    commented" task.

    *Consequence: a clean top-1 margin does not license a top-N task.* Check
    rank N against rank N+1 for the exact slice the task uses. Two lanes have
    now been bitten by this from different directions — one found
    `kkroening/ffmpeg-python`'s rank-3/rank-4 boundary tied at 5 commits while
    its top-1 margin was wide.

27. **Injecting `votes.comments` moves no rendered score or ordering.**
    `Vote.jsx` reads the votes map only through `commentVote`/`submissionVote`
    to choose the form's CSS class; the displayed number and `buildTree`'s
    `netScore DESC` ordering both come from the record's own `netScore`. The
    reddit census's injectable-keys table presents `votes` as the way to create
    pre-existing votes, which is true of the *highlight state* and false of
    everything an ordinal derivation depends on.

    *To move a comment's rank, replace the whole record through
    `commentEdits[<id>]`, which `overlay.resolveComment:210` and
    `mergeComments:120` do consume.* Third instance of "a writable key is not
    the key the page reads" — after gitlab `newStars` (ranking reads
    `star_count`) and gitlab contributors (no overlay at all).

28. **`deletedForums` tombstones a forum NAME, not an id.** `overlay.js:97,116`
    keeps dropping submissions whose forum matches a tombstoned name, so
    delete-then-recreate-under-the-same-name leaves the new first post present
    in `newSubmissions` and **invisible in every view**. Found by a lane that
    rejected the shape rather than shipping it.

29. **R5 on reddit is frequently NOT forced, and skill claims must be audited
    against that.** Following from finding 25 (Hot ordering == Top ordering on
    the pristine seed in 94 of 95 forums): a task that names a superlative and
    claims R5 may be solvable from the default forum page without ever touching
    the sort control or the time filter.

    Two lanes reached this independently and handled it differently, both
    correctly:
    * one **injected** a lowered `ranking` to push the target to page 2 of Hot,
      making the sort genuinely necessary and keeping the R5 claim honest;
    * the other **dropped the R5 claim** on the two tasks where it was not
      forced, relabelling them R4-only.

    *Validation action: every reddit bundle claiming R5 must be checked against
    the question "would an agent that ignored the sort control still land on
    the right row?" A claim that fails that test is a metadata error, not a task
    error — the task still works, it just does not train what it says it does.*

30. **The reddit image-repost flow is fully click-reachable, resolving a
    census "not drive-verified" item.** `currentUser.submissionLinkDestination`
    is `"url"` in the seed, so `Submission.jsx:71-77` points an image post's
    **title link** at `/submission_images/<file>` directly. Clicking the title
    navigates to the picture and the address bar then holds the absolute URL, so
    the `^https?://` promotion needs no typed or constructed URL.

    Two corollaries: for image posts the permalink page is NOT reachable via the
    title (use the comment-count link in `nav.submission__nav`), and the census
    cited the validator at `EditSubmissionPage.jsx:70` while this flow actually
    executes `SubmitPage.jsx:121-124` — the two agree, but the justification
    pointed at a handler the flow never runs.

    Also: all 2,748 files in `dist/submission_images/` are referenced by a
    seeded post. There are no spares, so an injected image post must reuse a
    file.

31. **`users[].submissionCount` is a live-site total that disagrees with the
    rendered rows for every user** — chrisdh79 424 vs 39, Wagamaga 248 vs 14.
    The dangerous one is **Hrekires: 11 stored vs 10 rendered**. A one-apart gap
    survives a spot check, produces a plausible-looking wrong answer, and would
    fail every correct agent.

    Ground truth for any post-count derivation is the row count computed the way
    `UserPage.jsx:41` computes it — never the stored field.

    This is the seventh instance of the stored-aggregate-vs-rendered-list
    pattern across all four mocks (gitlab commit_count x3 surfaces,
    open_issues_count 3476 vs 243, reddit forum submissionCount 3322 vs 113,
    reddit commentCount 6 vs 5, shopping dbProductCount 21796 vs 4398, and now
    this). **It is the single most repeated defect in the batch.**

32. **Reddit `/forums` uses numbered `OffsetPagination`, not the "More" cursor
    pager** used by submission listings. A replay reusing the listing pager's
    selector finds nothing there. Both expose `a[rel="next"]`, which is the
    portable choice.

33. **The reddit census missed a whole click-reachable surface: the per-forum
    comment firehose `/f/{forum}/comments`.** Registered at `src/App.jsx:124`,
    reached by a rendered **Comments** tab (`ListNav.jsx:167-174`), fixed
    newest-first (`CommentsFirehosePage.jsx:33-36`), every row carrying an
    author byline (`CommentRow.jsx:103`).

    *Consequence: the census's "~5 usable entities" ceiling for the
    block-a-user topic was a property of ONE join — newest-post-author — not of
    the site.* R7 only needs a two-hop byline. Corpus-wide, **1,065 authors have
    at least one below-zero comment** and 53 have two or more within a single
    25-row page. The binding constraint on that topic is click-reachability,
    not entity supply.

    The lane delivered ten honest tasks across eight distinct entities with no
    padding, against a brief that had offered it permission to report a
    shortfall. Worth recording as the counter-example to the batch's general
    pattern: not every census limit is real, and the way to find out is to look
    for a surface the census never enumerated.

34. **The reddit "78-way tie on forum creation date" is not a tie at all — but
    the superlative is still dead, for a different reason.** The 78 forums share
    the *date* `2022-10-01`; their stored timestamps differ to the second
    (`UpliftingNews` 00:01:03, `worldnews` 00:02:03, ...) and `sortForums`
    compares the full ISO string, so the ordering is deterministic and there is
    no data tie.

    What actually kills it is **rendering**: `ForumCard` renders name,
    subscriber count and `submissionCountLabel` and **never renders a creation
    date**. The only signal available to an agent is last-position-in-sort.

    *Same verdict, different cause — and the distinction matters, because a data
    tie is fixable by injection while an unrendered field is not.* An author who
    trusted the census's stated reason might have "fixed" it by injecting
    distinct timestamps and produced a task that is still unsolvable.

    This is the batch's recurring shape one more time: the finding was right,
    the mechanism behind it was wrong, and the wrong mechanism implies the wrong
    remedy.

35. **A task whose retrieval is "the most recently created X" cannot have the
    agent create X.** `createForum` stamps `created: nowIso()`, so anything the
    agent makes during the episode becomes the answer to the question it was
    asked. A lane caught this in its own design and pinned the injected vessel
    to a fixed past date instead.

    Same family as the action-destroys-its-own-retrieval-premise rule, but
    sharper: here the action does not merely disturb the ranking, it *becomes*
    the top of it.

36. **Reddit submission titles are EXTERNAL links, so clicking one leaves the
    app.** `Submission.jsx:120-126` renders the title as a plain `<a href>` to
    the off-site URL whenever the post has one. The in-app route to a post's own
    page is the **comment-count link** in `.submission__nav`.

    Not mentioned anywhere in the census's click-reachability section, and it
    matters for every reddit replay: a draft that clicks the title to reach a
    submission page navigates off-site and the run fails. All reddit replay
    drafts use the nav link.

    Note the interaction with finding 30: for *image* posts the title link
    points at `/submission_images/<file>` because
    `currentUser.submissionLinkDestination` is `"url"` — which is exactly what
    makes the image-repost flow work. Same mechanism, opposite consequence
    depending on post type.

37. **The "newest" ambiguity is now measured three times independently and the
    counts converge.** Three lanes reached it separately — one before being
    warned — and agree: **59 of the 95 forums** have their highest-id submission
    differ from their latest-timestamped one; only **35-36** are clean. The
    lanes report 36, 36 and 35, a boundary case not worth resolving since no
    task sits on it.

    All three of the entities the census hands out for "newest" tasks
    (`f/DIY 119019`, `f/space 134164`, `f/Futurology 119517`) are in the
    ambiguous set, and the census cites the DIY row with no caveat.

    *Recorded because the convergence is the point: three agents, three routes,
    one answer. Contrast the single-source claims elsewhere in this file that
    later needed withdrawing.*

38. **Partial-`set` semantics differ between mocks, and I generalised the
    reddit behaviour too far.** On reddit, posting
    `{"action": "set", "state": {"key": ...}}` makes `initial_state` **that
    partial object** rather than merging into the seed. I wrote that into the
    batch-5 contract as a general rule. It is not one.

    On shopping, the same call is a top-level **shallow merge** over
    `createInitialData()` (`vite.config.js:441-449`), so a partial patch is safe
    and the rest of the seed survives.

    *Read your own mock's `vite.config.js` before writing a partial `set`.* The
    contract now says so. A conforming reward is immune either way, because
    TASK4 S7 already forbids reading `initial_state` — which is the second time
    in this batch that an existing rule has silently protected against a hazard
    nobody had named.

39. **A captured listing page bypasses the derived pool entirely.** The census
    justified price-sort safety with "`resolveListing()` sorts the seeded pool
    before slicing" — true in general, and NOT the mechanism on a page the
    source capture recorded. For those, `resolveListing` returns
    `exact.productIds` verbatim (`catalog.js:1207-1219`) and the derived pool is
    never consulted.

    On kids-bedding price-descending the two agree (captured head id 67733 ==
    seed-derived maximum), so nothing is broken. But the claim as written would
    mislead any author building something page- or count-sensitive on a captured
    URL, where the seed-derived reasoning simply does not apply.

40. **The shopping census's Kids' Bedding `?price=20-30` tie is FOUR-way, not
    three.** It lists 31798, 35795 and 66784 at $29.99; **86962 is also
    listable there at the same price.** The "do not use that cell" verdict
    stands — the incompleteness does not change it — but an author who took the
    id list as exhaustive and tried to disambiguate by excluding three products
    would still have shipped an ambiguous task.

41. **Two of the 22 "safe" shopping categories have no source capture at all.**
    Virtual Reality (247) and Smartwatches (256) get their sidebar buckets from
    `priceFacets()`'s **derived** branch rather than from a recorded capture.
    The counts are still exact against the seeded pool, but it is a different
    code path than the census's "verified against the source capture" claim
    covers, which holds for the other 20.

42. **Single-result facet cells are not scarce.** The census offered two
    examples and the lane brief treated them as the available pool. A lane
    enumerated the space properly and found **18 single-result and 9 two-result
    price cells across 12 of the 22 safe categories**.

    It also found that Flip Cases — named as one of the two safest facet
    playgrounds — has **no cell smaller than three products** (3/28/10/3/3) and
    cannot express a single-result task at all.

    Second instance of a census ceiling being a property of the examples chosen
    rather than of the site, after the reddit comment-firehose finding. Both
    were found by enumerating the space instead of trusting the sample.

43. **The shopping census's category table is read as product counts and is
    actually category IDs.** "Kids' Bedding (155)", "Kitchen & Table Linens
    (189)", "Flip Cases (232)" are category identifiers; the real seeded counts
    are **100, 112 and 47**. In context — a table whose neighbouring column IS a
    count — the parenthesised number reads as a size.

    *Anyone sizing a "go to page N" or "count the items" task off those figures
    is out by 1.5x to 4x.* Not a wrong claim, but a formatting choice that
    reliably misleads, which is worth the same weight.

44. **Confirmed independently: shopping's `/post` shallow-merges.** A second
    lane verified `{...createInitialData(), ...newState}` at
    `vite.config.js:442-445`, so a partial patch yields a complete 15-key
    document. Finding 38 stands: the reddit replace-semantics I generalised into
    the contract are reddit's alone.

45. **Some ordering dependencies are structural rather than narrated, and those
    are the good ones.** `WishlistPage.jsx` emits no form, textarea or Update
    button at all while the list is empty — so on a "add the item, then annotate
    it" task the comment box does not exist until the product has been added.
    The agent cannot do the steps out of order even if it wants to.

    Contrast an ordering dependency that exists only because the sentence says
    "first ... then ...". A lane made the same point about a reddit forum's
    `moderationLogPublic` checkbox, which `CreateForumPage` never renders — it
    is reachable only at `/f/<name>/edit`, which exists only because creating
    the forum seated the user as moderator. Prefer structural dependencies when
    claiming `ordering_dependency` as a hard criterion.

46. **"Seven reddit forums under 100 submissions" is wrong — there are
    fourteen, and `BridgeportCT` (4) is missing from the census list
    entirely.** It sits between WaterburyCT (2) and monitor (6), so any task
    with a threshold above 4 built on the census list ships with a member
    missing from its ground truth — four of one lane's ten tasks. The census
    also omits the entire 55-76 band (arlingtonva 55, Documentaries 59,
    listentothis 62, ManchesterNH 62, Hartford 71, LowellMA 76). "Under 100" is
    a 14-forum errand, not a 7-forum one.

    Third instance of a census enumeration being incomplete rather than wrong,
    after the four-way-not-three-way price tie and the ~5-vs-1,065 entity pool.
    **Treat every census list as a sample, never as an enumeration.**

47. **There is no ascending submission sort on the reddit forum index.**
    `sortForums` (`ForumsIndexPage.jsx:52-67`) offers five orderings and
    `by_submissions` is DESC-only with no direction toggle. Ascending is reached
    by paging to the **tail** — 95 forums at 25 per page is 4 pages. A lane
    whose chain said "sort ascending" navigates to page 4 instead, which is a
    legitimate and slightly harder R5.

48. **An injection must not create a contradiction visible on one screen.**
    A lane rejected the obvious way to widen its matched set — raising a forum's
    seeded `submissionCount` from 1 to 418 — because the card count and the
    rendered listing are *equal* for every forum below 50 submissions, so the
    inflated card would sit next to a listing that disproves it.

    It injected a brand-new empty forum instead, where the card ("No
    submissions") and the listing agree.

    *This is the sharpest statement yet of the plausibility rule in the batch-5
    contract.* "Would this state exist on the real site" is the test; "does any
    single screen refute it" is how you check.

    Note the corollary the same lane established: the documented
    stored-vs-rendered disagreement (news 3,322 card vs 113 rows) appears only
    well ABOVE that range. Below 50 the two agree exactly — Paterson 1/1,
    BridgeportCT 4/4, coolgithubprojects 45/45. Even the batch's most repeated
    defect has a domain of validity worth checking before designing around it.

49. **ESCALATION — reddit `commentCount` disagrees with the comment rows for
    6,475 of 8,012 submissions (81%), not "at least one".** I recorded this
    earlier from a single example (124607 stores 6, holds 5) and stated it far
    too weakly. The gaps are often large: 118568 stores 16 and holds 2; 119707
    stores 12 and holds 2.

    *The operative rule is therefore much stronger than "prefer author or id as
    the derived value": **no reddit task may branch on, count, or write back a
    comment count from either surface.*** Not the stored field, not the rendered
    one.

    This is the eighth and worst instance of the stored-aggregate pattern, and
    the only one where my own recorded version of the finding would have let a
    defective task through.

50. **The "tightest coincident margin" figure was wrong and would have steered
    target selection.** I recorded `newhaven` at "12 minutes / 1 id" as the
    tightest case among the 36 coincident forums. Measured across all 36:
    `newhaven` is 11m18s, but **`f/aww` is 3m51s**, `f/dataisbeautiful` 5m11s,
    `f/wallstreetbets` 8m14s and `f/memes` 9m52s. An author picking targets by
    my number would have chosen the wrong forums.

51. **A seed-only conditional on reddit is 88/95 solvable by always taking one
    branch.** Closing the census's open question: across the 95 forums the
    "did the original poster reply in their own thread" predicate is TRUE for 7
    and FALSE for 88 — and only 7 of the 29 coincident-order forums are TRUE.

    *So an A13 task built on the pristine seed is not a conditional at all; it is
    a fixed action with a decorative if-clause.* This is the concrete proof of
    the batch-5 contract's claim that conditionals over a fixed seed are
    theatre, and it is why the whole lane injects its branch state.

    The lane's design is the reference implementation: **two matched pairs
    injecting a comment row with identical id, parent, netScore and timestamp,
    differing only in the AUTHOR**, so the same submission resolves opposite
    ways across two tasks and memorising the entity buys nothing. Branch
    distribution 5 upvote / 5 reply, all injected, none inherited.

52. **Shopping order-view line items are `<strong>`, not links
    (`OrderViewPage.jsx:27`) — there is no clickable order-to-PDP path.** Any
    chain that reads an order then acts on the product must route through the
    header quick search on the SKU or name. A replay that expects to click a
    line item fails, and under TASK4 S6 a task assuming that click is not
    reachable at all.

53. **`nextReviewId` seeds at 400000, not 1** (`dataManager.js:145`). No
    delivered reward keys on `reviewId`, but one that did would fail a correct
    run. Same class as the gitlab `nextIds.milestone` check — verify the seed
    counter before asserting on any generated id.

54. **Two margin flags in the shopping census §4.3 are wrong in both
    directions.** Plants, Seeds & Bulbs is marked as a sub-$0.30 margin and is
    actually **$0.50** ($6.49 vs $6.99). Fresh Meal Kits carries no warning and
    is **$0.34** ($1.50 vs $1.84) — narrower than the one that was flagged. The
    warnings are correct for Health Care ($0.10) and fan-shop Footwear ($0.23).

    A false warning costs a usable category; a missing one ships a brittle task.
    Both were found by a lane recomputing rather than reading.

55. **My own brief proposed a "derived" value that is constant across the whole
    corpus.** I suggested order 187's shipping method as a retrieval anchor for
    a shopping lane. **All 37 orders carry `shippingDescription: "Flat Rate -
    Fixed"` and `paymentTitle: "Check / Money order"`** — so an agent that never
    opened an order scores full marks.

    The lane caught it with rule 9 ("would an agent that skipped the retrieval
    still succeed?"), rejected it, and recorded the rejection. This is the test
    working on its author, which is the strongest evidence it is worth keeping.

56. **The shopping page-1 cutoff timestamp I propagated is a mash-up of two
    rows.** Both the census and my lane briefs state that the ten newest seeded
    orders end at `000000157, 2023-02-09 18:50:18`. Order 157 is stored at
    `2023-02-09 07:06:57`; the `18:50:18` stamp belongs to order **158**
    (2023-02-11). The true page-1 boundary is `createdAt > 2023-02-09 07:06:57`.

    The quoted figure is *later* than the truth, so anything injected under the
    stated rule still lands on page 1 — the error is conservative and nothing
    shipped is wrong. But it must not be trusted for a boundary case, which is
    exactly what an injection-placement rule is for.

57. **Third independent confirmation that shopping's `/post` shallow-merges**
    (`vite.config.js:441`, `{...createInitialData(), ...newState}` followed by
    `writeInitialStateUnconditional`). Finding 38 is settled: the
    replace-semantics I generalised into the contract from reddit are reddit's
    alone.

58. **CRITICAL — some seeded shopping products render on NO page under the
    default sort, and one of them is a census headline winner.**
    `resolveListing()` prefers a captured page-1 listing (`catalog.js:1142` +
    `listingKey()`), while page 2 falls through to `pool.slice()`. The two
    sources are not consistent, so products can fall into the gap between them:
    **4 of 63 in Chairs & Sofas at 12/page, 11 at 36/page.**

    **Product 99336 (DUOREST D2, 100%, 6 reviews) — the census's flagship
    entity for the top-rated-with-minimum-reviews topic — is one of them.** It
    cannot be found by ordinary browsing on the default sort. Sorting by price
    or name reveals it, so a task naming it has two defensible answers depending
    on how the agent browses.

    This is a TASK4 S6 reachability failure of a kind no static gate detects and
    no tie audit would surface: the entity is real, listable, uniquely
    maximal, and unreachable. The same defect killed Exercise & Fitness at
    12/page.

    *The lane dropped the entity and re-checked every shipped winner in six
    browsing modes.* **Validation action: any shopping task whose target is
    selected by browsing a category must be confirmed reachable in the browsing
    mode the instruction implies — not merely present in the seed.**

59. **Two more shopping rating-tie categories the census omits.** Patio
    Furniture (50) has a **four-way tie at 92%** (three-way at floors 6-12), and
    PlayStation Systems (226) a **three-way tie at 100%** at floor 5. Neither
    appears in the census's rating-tie list, which named only Kids' Bedding,
    Nintendo Switch and Nintendo Systems.

    Also: **fan-shop Footwear (153) has zero products with >= 5 reviews**, a
    property the census attributes only to Competitive Swimwear.

    Fourth instance of a census enumeration being incomplete rather than wrong.

60. **The shopping cart's three seeded lines are the SAME three products as
    cancelled order 000000170, so reordering it takes the merge branch.**
    Line 556's stored `optionTypeId`s (23919/23922) are exactly what `reorder`
    rebuilds from `{Size: Large, Color: Blue}`, so all three lines merge rather
    than append: the result is a **three-row cart at quantity 2**, not a six-row
    cart.

    *Any rubric of the form "the cart now holds N+M lines" grades the wrong
    shape on that order.* The lane asserts the doubled quantities instead.

    Worth generalising: when a task adds items to a collection that already
    holds something, check whether the handler merges or appends before writing
    a count-shaped rubric. The batch's terse contract (S3.3) already prefers
    asserting the exact resulting collection over counting, and this is a case
    where counting is not merely weaker but wrong.

61. **The captured-listing priority order is higher than the census implies,
    and five of the 22 "safe" categories have SORTED captures.**
    `resolveListing` consults `capturedListing(path, query)` (`catalog.js:720`)
    FIRST, and that key includes `product_list_order` / `product_list_dir`
    (`ALL_KEYS`, `catalog.js:664`). `listings.json` holds 9 captures with
    order+dir and no facet, plus ~25 more with order and a page/limit param.

    Affected safe categories: kids-bedding (price desc, name desc),
    competitive-swimwear (price asc), fresh-meal-kits (name asc; p=5 name),
    heating-cooling-air-quality (price asc), mp3-mp4-player-accessories
    (p=3 name). On those exact URLs the grid renders the capture's ids, not
    `pool.slice()`.

    The census's *conclusion* survives — kids-bedding's price-desc capture leads
    with 67733, the seed maximum — but its stated mechanism ("resolveListing
    sorts the seeded pool before slicing") is not what runs there. Combined with
    finding 58, this is the second time the capture-vs-derived split has
    produced a real hazard.

62. **`sortProducts`'s price tie-break is `id` ASCENDING in both sort
    directions** — `sign * (finalPrice(a) - finalPrice(b)) || a.id - b.id`
    (`catalog.js:1104`). The census treats price ties only as "avoid", which is
    the right advice, but this is what decides a tied superlative if one is ever
    relied on.

63. **Two shopping category names in the census are abbreviated and will not
    match the rendered nav.** Category 191 is seeded as "Pots, Planters &
    Container Accessories" (census: "Pots & Planters") and category 50 as
    "Patio Furniture & Accessories" (census: "Patio Furniture"). The NavBand
    renders the full string, so a selector or an instruction written from the
    census text misses.

64. **Product-Name-order superlatives were dropped by a lane on reproducibility
    grounds**, not because they are wrong: `sortProducts` uses JS
    `localeCompare`, whose ordering the lane could not reproduce deterministically
    from Python to compute ground truth. Recorded as a real limit on what can be
    author-verified offline, and a good instance of declining a task rather than
    guessing its answer.

65. **The shopping census's A11 row is wrong about the seed, and the error is
    doubly fatal.** It states the edit form for seed address 26 exposes
    `#primary_billing` / `#primary_shipping`. `AddressEditPage.jsx:15` computes
    `isOnly = state.addresses.length <= 1 && !!existing`, and lines 175-200
    replace **both checkboxes with a `<div class="message info">`**. With one
    seeded address, editing record 26 renders no default checkbox at all.

    So the nominal chain "tick both default flags" is (a) unperformable on the
    pristine seed and (b) pre-satisfied anyway, since record 26 already IS both
    defaults. Note the `&& !!existing`: `/customer/address/new/` *does* render
    both boxes on a one-address book, which is what makes the create-flow
    variant work with no injection.

66. **All 37 seeded shopping orders ship to the identical address.** So the
    obvious retrieval-writeback for the address topic — "copy order 000000178's
    billing address into the book", the shape of official `webarena-362` —
    derives a value that is already the only record on file, and would score the
    **untouched state 1.0**.

    TASK4 S9.3 would have caught it at verification (the initial lane must score
    exactly 0.0), but only after a full run. The lane caught it at design and
    injected differently-addressed orders instead.

67. **Six semantic-need categories are dead in the shopping seed, none of them
    recorded anywhere.** There is **no yoga mat** (all four `yoga mat` matches
    are flip-flops with foam soles), **no hand sanitiser** (all eight rows are
    empty refill bottles), no rain umbrella, no cat litter, no electric kettle
    and no bathroom scale. A lane found these by enumerating rather than
    sampling, and added four clean ones the census omits (power strips 33, air
    purifiers 12, sunscreens 29, dishwasher detergents 5).

68. **Do not enumerate an accepted-answer set from a captured search page.**
    The captured page for `laundry detergent` contains rows that are not laundry
    detergents — OxiClean stain remover (72399) and two dishwasher detergents.
    Enumerating from the capture is wrong in both directions. Enumerate from
    `products.json`, then check the capture against it.

69. **`clearCart` exists in `AppContext.jsx` and is referenced by no
    component.** A grep across `src/` outside the context file returns nothing,
    which confirms the three-separate-clicks finding by the strongest available
    evidence: the bulk path is not merely unrendered, it is unwired.

70. **Confirmed independently: `deleteAddress` leaves a dangling default
    pointer.** `AppContext.jsx:491-493` removes the address row but does not
    clear `customer.defaultBilling` / `defaultShipping`, so deleting a record
    that is a default leaves the pointer aimed at nothing. A lane restricted its
    delete task to a non-default entry rather than shipping the dangling state.

    Also confirmed by a second lane: the A11 checkbox finding (65) reproduces
    exactly — `AddressEditPage.jsx:16`, `isOnly = addresses.length <= 1 &&
    !!existing`, both checkboxes swapped for a static `message info` div.

71. **The newsletter finding was incomplete in a way that mattered.** The
    census records only that a boolean is stored. It does not record that the
    **off** arm is equally gradeable (`SimpleAccountPages.jsx:8-16`) — which is
    what lets an unsubscribe task be distinct from the subscribe one, on a
    surface the census had written off as a single bit.

    Fifth instance of a census entry being incomplete rather than wrong, and the
    second time the incompleteness understated what the site supports.

72. **150 of 2,040 shopping_admin stock rows carry `qty: 0.0`, and two census
    claims break on them.**

    a. §7(a) says an injected qty-10 row "sorts to the FRONT" under the grid's
       `qty ASC` default. It does not — every configurable/grouped/bundle parent
       is qty 0, so a qty-10 row lands around **page 8** at the 20-row default.
       Right conclusion (the injection is usable), wrong mechanism: the
       reachable route is the Quantity **range filter**, not the sort.

    b. The tie-audit row advising "phrase it as products with **fewer than 5
       units** (3-item set)" is wrong under a literal reading — that predicate
       also matches all 150 qty-0 rows, and they are all `is_in_stock: 1`, so
       adding "in stock" does not rescue it. Every task in that lane states a
       range with a **lower bound** (1-5, 3-3, 1-14).

    This is the sixth "right finding, wrong mechanism" in the file, and the
    third time the wrong mechanism would have led to a wrong remedy.

73. **The bulk-form `is_in_stock` leak is narrower than recorded.**
    `ProductGrid.jsx:100` initialises `bulk.is_in_stock` to `''`, so the stale
    selection from the `:481` reset survives only between two bulk edits within
    a single page mount — not across a fresh load. Worth knowing before
    designing a task around the leak or around avoiding it.

74. **Entity 872 / MP12-33-Blue is the only row of all 2,040 with
    `is_in_stock: 0`.** That single fact makes the official conditional "if it
    does not exist previously, also update stock status to in stock" (A13)
    expressible over the **pristine seed**, with no injection — which matters
    because A13 is the scarcest skill in the corpus and every other instance of
    it in this batch had to be manufactured.

75. **Partial-`set` semantics measured for three of four mocks: reddit is the
    outlier.** shopping (`vite.config.js:441-449`) and shopping_admin
    (`vite.config.js:371-377`) both shallow-merge over `createInitialData()`;
    only reddit replaces `initial_state` with the partial object. gitlab is
    still unmeasured.

    The original finding came from reddit, which is exactly why I generalised it
    wrongly — the one mock that behaves unusually was the one that surfaced the
    behaviour. Contract now carries the full table.

    Caveat that survives the merge: it is **shallow**. A nested key such as
    `systemConfig.variables` still needs `systemConfig` re-posted whole, so read
    it back from `/go` and patch rather than inlining a partial object.

76. **shopping_admin Custom Variables are CREATE-ONLY — the edit and delete
    arms are dead code.** `stateTracker.js:195` and the census both describe
    "create / edit / delete", but `App.jsx` registers only
    `/admin/admin/system_variable` (`:356`) and `.../new` (`:434`). There is no
    `edit/id/:id` route, and `CustomVariables` (`Tools.jsx:26-53`) passes no
    `rowHref`, so grid rows are not links. The `existing` / `update` / `remove`
    branches of `CustomVariableForm` are unreachable.

    A lane rejected a "fill in the pre-seeded placeholder variable" task on
    this and replaced it with an append shape. Another instance of rule 6 —
    grep for the reference, not the definition — this time finding a whole
    CRUD surface that is only a C.

77. **There is a second shopping review-duplicate class that escapes the
    census's own de-dup key.** The census defines duplicates as identical
    product + title + detail + nickname + rating (6,181 rows across 3,570
    products). Product 47884's reviews 289238 and 289222 share title, detail and
    rating and differ **only in that one nickname is the other
    self-concatenated** — `Guillermo RamasGuillermo Ramas` against
    `Guillermo Ramas`.

    Because the key includes `nickname`, that pair is not counted as a
    duplicate. But the rendered *name set* for the product has no single
    defensible answer, so the census's "3 reviews at <=2 stars" for 47884 is
    misleading and the product is unusable for a name-set task.

    *A lane's candidate filter now rejects any product containing such a group.*
    The general lesson: a de-dup key that includes the field the corruption
    lives in will not find the corruption.

78. **A word-match predicate can be clean and still ambiguous.** Product 89473
    (CORSAIR HS80) passes a "mentions wireless" text filter cleanly, but
    reviewer `Mike S.` uses the word only incidentally, about *other* headsets —
    so "mentions wireless" and "complains it isn't wireless" return different
    name sets. The lane demoted it to a rating-only task.

    Worth pairing with finding 58: both are cases where the entity satisfies
    every mechanical check and the *task* is still ill-posed.

79. **Nine of ten products a lane audited carry duplicate content pairs, and on
    six the duplicated row is a low-star row.** So a COUNT-shaped rubric would
    have had two defensible answers on eight of its ten tasks. Every rubric in
    that lane scores a **set of nicknames** instead, which makes the duplication
    inert.

    Third independent arrival at the same conclusion: TASK4 S3.3's "assert the
    exact resulting collection" is not merely a style preference — on this seed
    it is frequently the only correct shape.

80. **shopping_admin has 147 configurable products, not the five the census
    names** — every one carrying `configurable_attributes: ["size","color"]`,
    all supported identically by the wizard. A lane used ten distinct parents
    with no reuse.

    **Sixth instance of a census ceiling being a property of the sample rather
    than of the site.** The pattern is now consistent enough to state as a rule
    of its own: when a census names N entities for a topic, the real count is
    routinely an order of magnitude higher, and finding out costs one query.

81. **A wizard trap that will look like a broken task to a reviewer.**
    `SOURCE_FRONTEND_INPUT` (`attributeSwatches.js:22-26`) maps
    `size -> 'swatch_text'`, with two consequences:

    a. the visible add-option control on the Size attribute is
       `#add_new_swatch_text_option_button`, **not** `#add_new_option_button`,
       which renders `display: none`;
    b. saving Size writes `frontend_input: 'swatch_text'` into
       `productAttributeOverrides["144"]`, after which `configCandidates`
       (`ProductEdit.jsx:510-513`, filtering `=== 'select'`) **drops Size from
       the wizard's step-1 table**.

    Generation still works, because `openWizard` pre-seeds `wizard.attrs` from
    the parent's `configurable_attributes` and step 2 renders from
    `attributeByCode`. *A reviewer must not read the missing step-1 row as a
    failed task.*

82. **"Add sizes 30 and 31 to all colour variants" is a SINGLE-page wizard
    task, not a two-page round trip.** Sizes 30 and 31 already exist as Size
    option values (ids 173/174, `productAttributes.json` attribute 144, 20
    options). Only the extended top sizes (XXS/XXL/XXXL) are genuinely absent —
    which is exactly why official 549/550 are the two-page tasks and 551 is not.
    My lane brief carried the warning onto the case it does not apply to.

83. **All 147 configurables have a COMPLETE size x colour matrix**, so
    "fill the hole in the matrix" has no seeded material at all. Every
    variant-matrix task must add a new value to one axis rather than complete an
    existing one.

84. **DESIGN TECHNIQUE — make "nothing else moved" a GATE on the outcome
    components, never a paid component.** This resolves a genuine tension in the
    batch-5 style contract.

    S3.2 forbids paying for inaction: a component that scores because something
    did *not* change is banned from the terse set. S3.3 asks for the exact
    resulting collection to be asserted, which for a price-run task means the
    rest of the line must not have moved. Those pull against each other whenever
    the "exact collection" is too large to enumerate.

    A lane's answer: compute a `_scope_ok` predicate over the untouched rows and
    use it to **gate** the outcome components rather than to award any credit.
    An over-broad reprice then scores **0.0** — not "0.8 minus a preservation
    component" — while no component pays for restraint. The agent gets nothing
    for leaving things alone, and everything is lost for disturbing them.

    That is exactly the shape S3.3 asks for, expressed for a case where the
    collection cannot be listed. Recommended for any future bulk-mutation task.

85. **Choose percentages that land on <= 2 decimals.** A lane declined to reuse
    the official 13.5% figure because the resulting 64.875 has **two defensible
    roundings**, and a reward has to pick one. Small, mechanical, and exactly the
    kind of thing that produces an unfixable dispute between a correct agent and
    a correct rubric.

86. **MH05's parent (entity 126) carries `price: null`, not a number** — unlike
    every other configurable parent in its lane. The census does state this, and
    it is easy to skim past; a reward assuming a numeric parent price fails a
    correct run. Related to finding 62's point that parents are rendered
    `disabled` and excluded from the patch: parent rows are a different shape
    from their children in more than one way.

87. **"Grace Nguyen's Order Count row is 10, and cancelling drops it to 7" is
    not renderable — that number appears on no screen.** I put this figure in
    several lane briefs and in the census's R7 discussion.

    `CustomerOrdersLike` groups rows **per interval** (`LegacyReports.jsx:359-376`
    plus `buildGroups`), and the Period select offers only Day / Month / Year
    (`:127-131`). Grace's 15 orders straddle 2022 and 2023, so a two-year run at
    Year period yields **two rows of 5**, never one row of 10; the `<tfoot>`
    totals sum across all customers, not within one.

    *The real figure is her 2023 row: **5**, moving to 2 when all three pending
    orders are cancelled.* The lane scoped every read-back to a single interval
    and reproduced the file's own documented 2022 control (36 rows / 116 orders)
    to prove its re-implementation.

    This is the third "the number you want is not on any page" defect, after the
    gitlab commit-count triple-disagreement and `open_issues_count` 3,476 vs 243
    — and the second time it was **my** brief carrying the bad figure.

88. **The shopping_admin Orders grid has no "Pending" status filter.**
    `OrdersGrid.jsx:304` passes `ORDER_STATUS_FILTER_OPTIONS`
    (`reportUtils.js:322-332`): canceled, closed, complete, fraud, holded,
    payment_review, paypal_canceled_reversal, paypal_reversed, processing.
    `AdminGrid.jsx:605-617` renders `col.options` verbatim and appends nothing.

    The census's R5 row implies pending is filterable. It is not — and pending is
    the status most of the order-lifecycle topics target. The lane routed R5
    through the keyword search (`gridUtils.js:132-138`, which searches hidden
    columns), the Purchase Date range filter and the Grand Total range filter
    instead.

    A neat consequence it exploited: *Suspected Fraud* **is** in that list, so
    injecting a fraud-status order buys a filterable queue that pending cannot
    offer — turning finding 9's dead `fraud` status into a usable surface.

89. **`GRID_PAGE_SIZES` overrides the `defaultPageSize` prop.**
    `ProductGrid.jsx` passes `defaultPageSize={20}`, but
    `gridUtils.js defaultPageSizeFor` gives `GRID_PAGE_SIZES` priority and maps
    `product_listing` to **200**. Favourable in the case that surfaced it (a
    32-row family fits one page), but any lane reasoning "16 rows against a page
    size of 20, so paging is a risk" is computing against the wrong number.

    Same shape as findings 5 and 61 — a prop or a general mechanism that a more
    specific lookup silently pre-empts.

90. **Two official product-family names collide with a second family under the
    grid's keyword search.** `ryker` matches **32** rows (MS09 Crew-neck AND MS02
    V-neck); `helios` matches **22** (MS05 EverCool Tee AND MT04 Endurance Tank).
    A reward grading "all the `helios` hits" would grade 22 rows where the right
    answer is 6.

    Also: "Cora Pant" is really *Cora Parachute Pant* — the same trap as the
    already-documented `Chloe Tank` / *Chloe Compete Tank* case, which means
    that trap is a family rather than a one-off. **Search an official name
    against the seed before treating it as identifying.**

    The lane's response is the better one: it turned both collisions into seeded
    **distractors** (tasks 003 and 004) rather than avoiding the names. A
    collision that defeats a careless agent is difficulty; one that defeats the
    rubric is a bug. The difference is whether the instruction disambiguates.

91. **MOCK BUG — an edited order address renders on the order view but NOT in
    the orders grid.** `selectors.js getOrderGridRows` reads the
    **`orderOverrides`** patch and short-circuits before address overrides are
    applied:

    ```js
    const patch = state?.orderOverrides?.[String(row.entity_id)]
    if (!patch) return row     // returns BEFORE orderAddressOverrides is consulted
    ```

    So `orderAddressOverrides` reaches the grid's Billing/Shipping Address
    columns **only when the same order also carries an unrelated
    `orderOverrides` patch.** Edit an address alone and the order view shows the
    new value while the grid still shows the old one.

    My lane brief named `orderAddressOverrides[address_id]` as the A11 writeback
    with no caveat. The lane dropped a candidate ("copy shipping onto billing
    within one order") rather than ship a task whose correct end state is a
    **two-screen contradiction**, and any future lane grading an address through
    a grid column will hit this.

    *Note what this is: the mutation-side mirror of finding 48.* That rule says
    an INJECTION must not create a contradiction visible on one screen. This is
    a case where the mock's own write path creates one, so the same test has to
    be applied to the task's END STATE, not only to its preconditions.

    Under TASK4 S2 this is a fact to design around, not a bug to fix — `hub/` is
    read-only.

92. **The census's "safest superlative on the site" is wrong twice, found
    independently by two lanes.** It states: *Order Total report top-1 =
    `avidreader99@yahoo.com` at $1,644.48, margin $212.04.*

    a. **Arithmetically wrong.** Recomputing `orderReportAmount` /
       `customerOrderRows` over the seed gives **$1,464.48** (customer 18:
       $773.68 + $690.80), with the runner-up at $1,277.00 — margin **$187.48**.
       The published figure looks like a transposition of 1,464.48.
    b. **Unreachable, which matters more.** `buildGroups` emits only the buckets
       `intervalsBetween(from, to, period)` produces (`LegacyReports.jsx:398-411`),
       `periodKey` truncates to day/month/year only (`reportUtils.js:51-56`), and
       the Period select offers exactly those three. **No configuration produces
       a single bucket spanning 2022 and 2023**, so no row anywhere prints an
       all-history per-customer total.

    Same defect kills the Order Count anchor (finding 87): the all-history count
    of 10 exists in the seed and on no screen. Standing rule 15 exactly —
    present, uniquely maximal, unreachable.

93. **The rescue, and it is worth knowing:** `intervalsBetween` steps a `year`
    period one calendar year at a time, so **any From/To that stays inside one
    calendar year renders a single interval.** `1/1/2023`-`3/31/2023` at
    Period=Year is one ranked table covering exactly Q1.

    That recovers clean single-interval superlatives with real margins — April
    2023 count: Grace Nguyen 4, margin 2; 2023 total: Sarah Miller $846.80,
    margin $156.00 — including the exact target the broken anchor was reaching
    for, obtained honestly.

94. **TRAP — a window that straddles a year boundary but is shorter than a year
    SILENTLY DROPS the later orders.** `6/1/2022`-`5/31/2023` at Period=Year
    emits only the `2022-01-01` interval, and every 2023 order in range simply
    does not appear. No error, no empty state, just a plausible-looking table
    that is missing half its data.

    This is the most dangerous single mechanism found in the batch: it produces
    a *wrong answer that looks right* rather than a visible failure. No task
    uses such a window.

95. **The Order Count/Total reports render the customer NAME, not the email** —
    so the census's "2022 top customer, margin 3, safe" line is arithmetically
    correct and unusable for an email-valued task, because two seeded customers
    are named Jane Smith.

96. **A full credit-memo refund produces a NEGATIVE report contribution.**
    `orderReportAmount` subtracts the refund and the order discount separately,
    so a fully-refunded order 000000028 reads **-$50.40**. All injected refunds
    in the batch are partial.

97. **HAZARD — after a review delete, the product page still lists the deleted
    row while every other surface has dropped it.** `ProductReviews`
    (`ProductEdit.jsx:1756`) reads **raw `state.reviews`**, whereas every other
    review surface goes through `getReviews(state)`, which filters
    `deletedReviewIds` (`selectors.js:252-259`).

    So after a delete: the Reviews grid and Reviews-By-Products have dropped the
    row, and the product page's own "Product Reviews" section still shows it.
    Two rendered lists of one collection, disagreeing.

    *Fatal for any delete-then-count chain that lets the agent reach the count
    via the product page.* Directly relevant to the review-purge lane, which is
    being asked to confirm its replays route through the grid and the report
    rather than through `ProductEdit`.

98. **There is a SECOND per-product review list the census never mentions.**
    `ProductReviews` renders under the product page's "Product Reviews" section
    (`ProductEdit.jsx:1462`, table at `:1754-1793`) with columns
    ID / Status / Title / Nickname / Review / Action. It also has no rating
    column, so DO-NOT-ATTEMPT #20's conclusion is strengthened — but this is the
    most natural click path to a product's reviews and the census does not
    record that it exists.

99. **`setProductDescription` is unconditional on an existing-product save**
    (`ProductEdit.jsx:390`); only the new-product branch at `:382` is guarded by
    `if (form.description)`. So opening a product and pressing Save with no edit
    writes the seeded description into the overlay and creates a real diff.

    Textbook TASK4 S7 "gate on the recorded value, never on the record being
    edited" — the lane's components fullmatch a sentence frame rather than
    checking the key exists.

100. **`bestsellersRows` has TWO rendering paths for the same year, and they
     could disagree.** A from/to inside one calendar year takes the same-year
     branch (`reportUtils.js:265-269`), disables the main select and returns a
     boundary select over `bestsellers_daily`; a multi-year range instead reads
     `bestsellers_yearly` by `rating_pos`.

     A lane recomputed both rather than assuming: they **agree at rank 1** for
     2022 (entity 20, qty 5) and 2023 (entity 33, qty 4). Recorded because the
     agreement is a fact about this seed, not a property of the code — a
     different seed could put the two paths in conflict, and nothing would
     signal it.

     Note the shape: this is the *inverse* of finding 94, where two year-period
     configurations silently disagreed. Same mechanism family, opposite outcome,
     and only measurement distinguishes them.

101. **A frozen aggregate cross-checked against the live data and matching is
     worth recording too.** The same lane recomputed all three graded bestseller
     figures from `orders.json` (non-canceled, by calendar year) and matched the
     bundled aggregate exactly: 24-UG01/2022 = 5, 24-WG085/2023 = 4,
     24-WB07/2023 = 3.

     That closes an alternative-route risk as well as a correctness one: the
     live Ordered Products report gives the same number, so an agent taking
     either path lands on the same answer. **Standing rule 5 has a negative
     case, and this is it** — the aggregate/list divergence is pervasive but not
     universal, and the only way to know which you have is to check.

102. **When two surfaces disagree, the INSTRUCTION must name the one it means.**
     Following finding 97, a lane audited its own ten instructions against the
     `ProductReviews` / `getReviews` split. Nine already named the surface
     ("in Reports", "Reports > Reviews > By Products"). One did not — it read
     *"whose Plain Value is the two products' combined review count"*, which an
     agent could reasonably satisfy from each product's own page, reading the
     **stale** 6 and 5 instead of the correct 5 and 4. Reworded to "...their
     combined review count **in Reports**".

     The rubric was never wrong; the instruction was under-specified in exactly
     the place the mock is inconsistent. *A terse instruction may omit the click
     path — S3.1 requires it — but it may not omit which of two disagreeing
     surfaces is authoritative.*

103. **The stale-review trap is worse than a stale count.** The product page's
     review rows link to `/admin/review/product/edit/id/<id>/`, so an agent can
     navigate from a product to a review it has **already deleted**; `getReview`
     returns `null` for it (`selectors.js:262`) and the edit page renders
     "Rating isn't Available". Confusing to an agent, harmless to a rubric that
     grades `deletedReviewIds`.

104. **The batch-level `nemo_tasks.jsonl` is not consumed by anything.**
     `export_nemo_rollouts.py:162` reads each bundle's own `nemo_task.json`
     (`["task_payload"]`) and never opens the per-lane aggregate. A lane declined
     to hand-transcribe ten multi-kilobyte escaped-JSON lines on exactly this
     reasoning, and it was correct — the aggregate adds corruption risk with no
     information gain.

     *The per-bundle `nemo_task.json` files are authoritative.* Note also
     `export_nemo_rollouts.py:189-192`: the export derives `sites` and
     `start_urls` from `task.json` and explicitly treats any copy already in
     `nemo_task.json` as stale, warning on disagreement. So even the fields the
     aggregate would carry are re-derived at export time.

105. **The shopping_admin review-to-customer join is not merely weak — it is
     completely dead on the seed.** All six `disappointed` reviews fail: five
     have `customer_id: null`, and the sixth (review 351 -> customer 70, Emma
     Lopez) points at a customer with **zero orders**, so the seed's single
     surviving link is itself a dead end. The nickname route fails too —
     Wilbur / Ricky / Lasandra / Aiko match no customer, "Hannah Lim" matches a
     customer with no orders, "Emma" is ambiguous.

     A lane injected **both** `customer_id` and `nickname = customers.name`, and
     both halves are load-bearing for different reasons: `customer_id` is what
     `CustomerEdit.jsx:154-156` and the By Customers report filter on, but
     `ReviewEdit` renders "Posted By" from `review.nickname` and never renders
     the customer at all. So `customer_id` alone would be a writable key that no
     page reads *in the direction the task needs* — finding 27's pattern again,
     now appearing as a reason to inject two fields rather than one.

106. **`orderStatuses.json` has no `state: "pending"` row**, so `#history_status`
     renders **zero options** on pending orders. Inert where no reward scores
     `entry.status`, and fatal to any task that tries to change an order's
     status from the comment box.

107. **The Dashboard's Top Search Terms panel answers a "top search term" task
     without opening the report.** `Dashboard.jsx:67-72` renders the ranking
     directly, so for a naive top-term task **the Search Terms report is not the
     only route** — an agent can read the answer off the landing page and never
     exercise R1/R10 at all. Standing rule 9 in the wild, on a surface no census
     enumerated.

     The panel filters `num_results > 0`, which cuts two ways. It means a
     zero-result-query task has a genuinely exclusive route through the report.
     And it means an injection that patches a term's result count to 0 drops it
     from the panel *and* the report consistently — no one-screen contradiction,
     satisfying finding 48.

108. **A repaired task should be checked against rule 9 as hard as an original
     one.** The `easy`/no-retrieval bundle was rebuilt around the predicate
     "queries returning ten or more products", resolving to `Joust Bag`
     (4 hits / 10 results, margin 2, no tie). What makes the repair sound rather
     than cosmetic: the **unfiltered** leader `hollister` (19 hits) returns only
     1 product and is excluded by the predicate — so an agent that skips the
     retrieval names the wrong rule and scores 0.0.

     A repair that merely adds a retrieval id to the metadata would have passed
     the gate and trained nothing.

109. **When success is an ABSENCE, no component name saves you — the empty
     state satisfies every removal at once.** Three of 600 rewards paid on `{}`,
     and the hardest was a vote *retraction*: the task's whole point is that
     something is gone, and on `{}` everything is gone.

     The handler decides which fix is available. `AppContext.jsx:329-333`
     computes `next = 0` and then **`delete votes[bucket][key]`** — it removes
     the key rather than zeroing it, so there is no `0` value to gate on and
     key-absence is unavoidable. My suggested "require the key present with
     value 0" was therefore not an option, and the lane said so rather than
     bending the task to fit the advice.

     The working fix is a **`_live_session` marker gating the whole rubric** —
     here, the seed's own untouched vote (`votes.submissions["1"] == 1`, on a
     submission the task never asks the agent to touch) plus a `forums` row for
     the scoped forum. Empty state fails the marker and scores 0.0; the
     post-setup baseline passes the marker and fails the outcome components;
     only a correct run scores 1.0.

     **Gate every component, not just the leaking one.** The lane gated both,
     because the second happened to fail on `{}` for an incidental reason and
     would have become a trap for whoever edited the expected map next.

     *Rule for any removal-shaped task: check the handler first. If the removal
     leaves a zero, gate on the zero. If it deletes the key, gate the whole
     rubric on a positive marker elsewhere in the document.*

110. **A DISTRACTOR CAN NEVER CARRY WEIGHT OF ITS OWN.** A component whose
     truth condition is the *absence* of a mutation — "the neighbouring line is
     still enabled", "the other issues keep their labels" — is true on `{}` by
     construction. That is not a bug in the component; it is what the component
     means.

     So a distractor must be expressed as a **gate**, never as a paid slice:

     ```python
     vneck_hit = _disabled_within(state, VNECK)
     scope_ok  = len(vneck_hit) == 0
     crew_ok   = bool(scope_ok and _all_field(state, CREW_CHILDREN, "status", 2))
     parent_ok = bool(scope_ok and _field(state, CREW_PARENT, "status") == 2)
     ```

     The remaining weights (0.7 / 0.3) pay only for rows the agent actually
     wrote `status: 2` onto, so `{}` scores 0.0 on every component.

     **The fix made the task stricter, not looser** — disabling all 32 `ryker`
     hits now scores **0.0** instead of 0.6, because the gate withdraws both
     components rather than docking one. That is the correct penalty for
     defeating the distractor, and it is what the old shape got wrong.

     Consequence for metadata: `exclusion_constraint` had to come off the
     `hard_criteria` list. The exclusion is still *enforced*, but that slug
     asserts it is *scored*, and it no longer is. An alternative correct shape,
     used by a sibling bundle, is a single exact-set statement
     (`disabled_set_across_both_lines_is_exactly_aeon`) — false on `{}` because
     the expected set is non-empty, which is exactly S3.3's "assert the exact
     resulting collection".

111. **Lanes writing scratch fixtures to bare `/tmp/<generic-name>.json`
     collided with each other.** One lane's `/tmp/fixtures.json` was overwritten
     by a different lane's reddit data between its authoring run and a later
     repair; the repair crashed on the foreign content.

     That lane's bundles were unaffected — they were emitted before the clobber
     and every matched-set constant had been hand-verified against
     `src/data/issues_index.json` — and it regenerated the fixture into a private
     path. But the hazard is real and silent in the general case: a lane that
     computed ground truth *from* a clobbered fixture would produce tasks whose
     expected answers are simply wrong.

     It is not silent at the batch level, because a wrong expected answer makes
     the replay lane score something other than 1.0 and verification fails the
     task. So the blast radius is wasted verification rounds, not shipped
     defects. Confirmed after the fact: no surviving generator under
     `scripts/_b5*` references a generic `/tmp` path.

     *Rule for future batches: parallel lanes must write scratch under a
     lane-private directory. The harness already provides one per job; a shared
     `/tmp` is a race by construction when 20 agents run at once.*

## Batch-5 gate status after repairs

* static gate: **600/600**
* empty-state probe (S9.5): **600/600** score exactly 0.0 on `{}`
* style split: **450 terse / 150 explicit**, exact
* start_path `/`: **596/600 (99.3%)**, floor is 420
* retrieval-writeback: **487**, target ~180
* difficulty: **0 easy / 168 medium / 432 hard**, derived from chain shape

112. **TASK4 S9.2 read literally makes the orchestrator's own retry loop
     self-defeating.** The condition is "at least one attempt reports
     `verification.passed`, and **all attempts agree** on initial score, replay
     score, and verdict". But the orchestrator runs **up to three adversarial
     rounds** by design (`web-orchestrator.md:11`), so an early round that failed
     and was superseded would count as permanent disagreement — no task that
     ever needed a retry could be verified.

     The first run to need a retry exposed this: `contributor_honour_roll_008`
     had attempt-1 produce no replay score, attempts 2 and 3 both score exactly
     1.0, and a clean `## Verdict: PASS`. Under the literal reading it fails.

     **What S9.2 is actually guarding against is flakiness** — the same replay
     scoring *differently* on two complete runs. So:

     * a round that produced **no score** is an incomplete round, not a
       dissenting one, and is excluded from the agreement set;
     * a round that produced a **different** score is real disagreement and
       still fails;
     * at least one complete round must remain, or the task is unverified.

     `scripts/_b5_status.py` implements that distinction with the reasoning
     inline. Note this is a *reader* fix, not a relaxation of the bar: nothing
     about the required 0.0/1.0 scores or the PASS verdict changed.

113. **The `## Verdict` grep trap is real in this corpus, and the regex handles
     it.** REVIEW.md files contain a bare `## Verdict` heading on one line and
     `## Verdict: PASS` on the next. Batch 4's `grep -m1 '^## Verdict'` matched
     the heading and reported a genuine PASS as unresolved. Confirmed across all
     completed runs: anchored regex `^##\s*Verdict:\s*PASS\s*$` matches the
     right line every time — 29/29 with no false negatives.

114. **Comparing scores ACROSS adversarial rounds is invalid — the artifacts
     change between them.** This is the correct reading of S9.2 and it took two
     iterations of my own status reader to get right.

     `web-orchestrator.md:11-12` routes replay failures back to `golden-browser`
     and scoring failures back to `reward-gen`, then re-runs. So attempt-1 and
     attempt-5 executed **different `reward.py` and different
     `golden_replay.py`**. A task that was repaired mid-loop therefore looks
     like a task that disagrees with itself.

     Three runs were misreported this way:

     | task | rounds (replay) | reading |
     |---|---|---|
     | `find_mr_by_phrase_comment_005` | 1.0, 1.0, **0.0**, 1.0, 1.0 | mid-loop revision, recovered |
     | `find_mr_by_phrase_comment_009` | **0.0**, 1.0, 1.0 | repaired after round 1 |
     | `grant_access_top_repos_008` | initial **0.15**, 0.0, 0.0 | S9.3 violation found and fixed by the loop |

     All three carry `## Verdict: PASS` and `status: completed, exit_code: 0` in
     `batch_status.json` — the orchestrator accepted them, correctly.

     **The accepted state is the FINAL round.** S9.2's "all attempts agree" is
     about *flakiness* — the same artifacts scoring differently — and that is
     what `detect_flaky.py` measures by re-running the final artifacts. Judging
     the union of rounds conflates repair with instability.

     Note `grant_access_top_repos_008` is the loop working exactly as designed:
     round 1's reward paid **0.15 at t=0**, an S9.3 violation, and the
     adversarial loop caught and fixed it without any intervention from me. That
     is a defect the static gates cannot see, found and repaired automatically.

115. **A run the orchestrator abandons is indistinguishable on disk from one
     still in flight.** `top_contributor_join_issue_004` stopped after
     attempt-1 with initial evidence and screenshots written but **no
     `verification.json` and no `REVIEW.md`** — exactly the file set a healthy
     mid-flight run has. My status reader counted it as in-progress and would
     have done so forever.

     `batch_status.json` is the only place the difference is recorded
     (`status: failed`), so the reader now consults it. Note the entry carries
     `exit_code: 0` alongside `status: failed`, so exit code alone is not a
     usable signal either — 0 non-zero exits across 157 completed runs while one
     of them had failed.

     *This is the third distinct way a progress check has misreported this batch*
     — after the bare `## Verdict` heading and the cross-round score comparison.
     All three shared a shape: a check that was correct about the file it read
     and wrong about what that file's absence or presence meant.

     Requeued at concurrency 1 alongside the main wave (11 total, under the 12
     cap). 900s to failure with other runs completing at 1293s, so it was not a
     wall-clock limit; `--timeout` is 90 *minutes*.

116. **Load average is the wrong saturation signal for this workload —
     throughput is.** Load climbed steadily to **24.6 on 4 cores** and I nearly
     cut concurrency on the strength of it, because batch 4 died at 13.49.

     The measurements that mattered:

     * **200 chrome-headless processes, none older than 20 minutes** — churn,
       not a leak. Headless chromium spawns ~11 helpers per browser, so 10
       concurrent tasks fully accounts for it.
     * **Completions per 15-minute window, flat over three hours:**
       17, 20, 17, 14, 16, 18, 23, 18, 17, 20, 23. No degradation whatsoever.
     * 20 GB memory still available.

     Linux load average counts processes in uninterruptible sleep, so a swarm of
     short-lived page loads inflates it without indicating saturation. Batch 4's
     13.49 was genuinely oversubscribed — **two** orchestrators totalling 14
     concurrent Playwright — and the distinguishing evidence there would have
     been falling throughput, not the load number itself.

     *Rule: before reacting to load on a browser-automation batch, measure
     completions per unit time. If throughput is flat, the load figure is noise.*

117. **REPEAT OF A BATCH-4 MISTAKE: do not edit `batch_status.json` while the
     orchestrator is running.** I relabelled a stale `failed` entry to
     `superseded_by_retry`; the orchestrator holds the structure in memory and
     rewrote the file wholesale on its next flush, discarding the edit. Batch 4
     recorded this exact failure and I did it again.

     The entry is cosmetic — the run itself carries `## Verdict: PASS`, two
     attempts with initial 0.0 / replay 1.0, and a reachable golden replay. The
     authoritative signal is the run directory, not the status file.

     *Rule: `batch_status.json` is owned by the running orchestrator. Read it,
     never write it, until the batch is complete.*

118. **Verification runs come in two on-disk layouts, and a reader that assumes
     one misreports the other.** Most runs write
     `attempt-N/verification.json` and a root `golden_replay.py`. At least one
     writes `attempt-N/runM/verification.json` and
     `attempt-N/golden_replay.py`.

     The nested `runM` form is not a defect — it is the round executing **the
     same artifacts twice**, which is precisely the cross-run agreement S9.2
     asks for. `top_ever_post_downvote_askscience_conditional_runner_up_006`
     scored initial 0.0 / replay 1.0 in **both** runs of its round: a clean
     flakiness check. My reader, looking only at a verification.json's immediate
     parent, reported it as "no attempt-N/verification.json", and then as "no
     golden_replay.py".

     Both fixed by walking ancestors for the `attempt-N` component and falling
     back to the accepted round's replay. **Fourth distinct progress-reader
     defect in this batch**, and the same shape as the other three: correct
     about the file it read, wrong about what its absence meant.

     Worth stating plainly: every one of these four was found because a number
     looked slightly wrong and I opened the underlying files. A monitoring
     script that is never distrusted is indistinguishable from one that is
     correct.

119. **The three empty-state repairs were never re-queued for verification.**
     I excluded them from the 597-task wave while they were being fixed, all
     three were repaired and re-probed clean, and I then failed to add them
     back. They sat unverified for three hours and would have been missing from
     the final corpus.

     Found by asking a different question than "how many passed" — enumerating
     tasks that have no run directory AND are not currently in flight, then
     splitting that set by whether they were ever queued. 274 unverified, of
     which exactly **3 had never been queued at all**.

     *A completion percentage cannot show you work that was never started.*
     Every progress figure in this batch has been a ratio over the queue; none
     of them would ever have revealed a task missing from the queue itself.

120. **One run's `REVIEW.md` was never copied out of `audit_sandbox/`.**
     `web-orchestrator.md` step 11 says "Copy its `REVIEW.md` into the run
     output"; for `new_forum_sidebar_curation_histbits_top_post_pin_008` that
     copy did not happen, so the run looked unverified under S9.1 while being
     verified in every other respect.

     What was actually there, checked before acting:
     * `audit_sandbox/REVIEW.md` — a complete audit, twelve numbered sections
       covering static capability, both lanes, partial-credit guardrails, URL/DOM
       handling and hidden-signal inspection, ending `## Verdict: PASS`
     * four `verification.json` copies, all initial **0.0** / replay **1.0**,
       `passed: true`
     * `golden_replay.py` passing the click-reachability gate

     I copied the existing audit to the run root. **That is artifact placement,
     not verdict manufacture** — the audit ran, reached PASS on its own, and I
     wrote nothing into it. Exactly one run of 600 was affected.

121. **A THIRD run layout exists: `round1/golden_replay.py`.** After
     `attempt-N/` and `attempt-N/runM/`, one run put the accepted replay under
     `round1/`. Rather than enumerate layouts as they surface, the reader now
     takes the run-root copy if present and otherwise the most recently written
     `golden_replay.py` anywhere under the run.

     Fifth and sixth progress-reader defects. The lesson has stopped being about
     any individual layout: **a checker that hard-codes where an artifact lives
     will keep finding new places it does not.**

122. **`detect_flaky.py` flags 5 tasks, and all 5 are convergence, not
     flakiness — proven by re-running the final artifacts.** The script compares
     scores ACROSS adversarial attempts, which is the same error finding 114
     identified in my own reader: the orchestrator rewrites `reward.py` and
     `golden_replay.py` between rounds, so different attempts ran different code.

     TASK4 S9 requires every flag be run down to a cause, so I re-ran each
     task's **final** artifacts three times each, with endpoints exported:

     | task | attempts as flagged | final artifacts, 3 runs |
     |---|---|---|
     | `contributor_honour_roll_008` | replay None, 1.0, 1.0 | 0.0 / 1.0 x3 |
     | `find_mr_by_phrase_comment_005` | 1.0, 1.0, **0.0**, 1.0, 1.0 | 0.0 / 1.0 x3 |
     | `find_mr_by_phrase_comment_009` | **0.0**, 1.0, 1.0 | 0.0 / 1.0 x3 |
     | `grant_access_top_repos_008` | initial **0.15**, 0.0, 0.0 | 0.0 / 1.0 x3 |
     | `template_project_staffed_004` | 2 browser errors, then 0 | 0.0 / 1.0 x3 |

     **15 of 15 runs stable.** What the report actually captured is the loop
     doing its job: a reward paying 0.15 at t=0 and being fixed, a replay
     failing and being rewritten, browser errors being resolved.

     *The script is not wrong to surface these — a human should look. It is
     wrong to call them flaky.* A stability check has to re-run one set of
     artifacts, not compare two.
