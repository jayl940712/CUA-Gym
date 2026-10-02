# Census errata — read this BEFORE trusting a census cell

`webarena_09_04_skills/census/*.md` are the four site feasibility studies. They
remain the best single source on what each mock supports. But they were written
**before** 122 findings were verified against them, and **they were never
back-corrected**. A cell can therefore be confidently wrong in a way that
`CORRECTIONS.md` already refutes.

This file lists cells known to be stale. It is not exhaustive — treat every
census claim as a strong prior, not a fact.

## gitlab

| census says | actually | evidence |
|---|---|---|
| topic-6 writeback is `repo.fileOverlay.<fp>:main:LICENSE`, entities `cloud-to-butt`, `timeit`, `solarized-prism-theme` (census:272) | **all three of those repos are `master`.** **only 41 of 175 projects are on `main`** — 126 are `master` and seven are on something else entirely (`develop` x2, `A1_A2_A3`, `ver3`, `development`, `6.x`, `6.2`, `lib`), so a binary main/master check still fails. `NewFile` takes `params.ref` verbatim, so `/-/new/main` renders on a `master` repo and the commit lands on a branch that does not exist | CORRECTIONS #15. A reward keyed on the census cell scores a **correct** run 0.0 |
| R8 templates: "Android/NodeJS/Jekyll/HTML" — 5 choices, no near-duplicates (census:114, :273) | **30 templates.** `templates.js` header: *"Exactly 30 rows … the Built-in tab counter reads 30"*. Twelve sit in near-duplicate pairs (five GitLab-Pages/Netlify pairs; `Spring` vs `Gitpod/Spring Petclinic`; `Serverless Framework/JS` vs `Tencent Serverless Framework/NextjsSSR`). `blank` is **not a template** — it is a separate pane `#blank_project` | B6-1 |
| "13 licences, no near-duplicates" | true of licence identity, **too strong about discriminating text**: `Exhibit A` and `Secondary License` appear in BOTH EPL 2.0 and MPL 2.0; `heirs and successors` in BOTH CC0 and The Unlicense | B6-3 |
| state-tab counters are computed pre-filter and never move with the filter | **false — the badges ARE filter-aware.** `IssuablesList.jsx:888`'s `counts` is dead code; the rendered path is `issuableStateCounts` (`hooks.js:39-50`) | CORRECTIONS #10 |
| `facebook/metaseq` as a fork upstream | **does not exist.** MetaSeq is `root/metaseq` (id 33) | CORRECTIONS #22 |
| SCHEMA.md record counts | stale by ~30x on issues/MRs (19,705 / 23,236 real) | CORRECTIONS #8 |

## reddit

| census says | actually |
|---|---|
| "'newest' never ties (ids unique)" | true of ids and **misses the real ambiguity**: `/f/X/new` sorts by id DESC, and id order disagrees with timestamp order at the head of **59 of 95 forums**. All three entities the census hands out are in the ambiguous set (CORRECTIONS #21/#37) |
| `?t=day` trap is "a genuine multi-step faceted-nav skill" | on the pristine seed **Hot order == Top order in 94/95 forums**, so the agent walks around it. An unhardened R5 claim is unearned (CORRECTIONS #25/#29) |
| own-post edit "append to the existing body" | **45 of 46 own submissions have no `body` key** (CORRECTIONS #23) |
| ~5 usable entities for the negative-comment join | **1,065 authors** have >=1 below-zero comment; the census missed `/f/{forum}/comments` entirely (CORRECTIONS #33) |
| "seven forums under 100 submissions" | **fourteen**, with `BridgeportCT` (4) missing from the middle (CORRECTIONS #46) |

## shopping

| census says | actually |
|---|---|
| flagship rating winner 99336 (DUOREST D2) | **renders on no page under the default sort** — 4 of 63 rows fall into the gap between a captured page-1 and a derived page-2 (CORRECTIONS #58) |
| Kids' Bedding `?price=20-30` is a three-way tie | **four-way** — 86962 is also listable at $29.99 (CORRECTIONS #40) |
| address edit exposes `#primary_billing`/`#primary_shipping` | **both checkboxes are replaced by a static message div** when the book holds one row, which the seed does (CORRECTIONS #65) |
| margin flags | Plants/Seeds is $0.50 (flagged, isn't tight); Fresh Meal Kits is $0.34 (unflagged, is tight) (CORRECTIONS #54) |

## shopping_admin

| census says | actually |
|---|---|
| Order Total top-1 `avidreader99@yahoo.com` $1,644.48, "the safest superlative on the site" | **$1,464.48**, and **unreachable** — no period configuration renders an all-history per-customer total (CORRECTIONS #92) |
| Order Count: Grace Nguyen 10 -> 7 | **not renderable**; rows group per interval, so her 2023 row is 5 (CORRECTIONS #87) |
| Custom Variables "create / edit / delete" | **create-only** — no edit route is registered (CORRECTIONS #76) |
| `setUi` / `ui.dismissedAlerts` | correct for gitlab, absent on shopping_admin (CORRECTIONS #1) |

## Partial-`set` semantics — MEASURED, and the source reading is a trap

**Four separate batch-6 lanes read gitlab's source and concluded "shallow-merge".
They were describing the CLIENT. Measured on the running mock:**

    pristine /go current_state                     41 keys
    POST {"action":"set","state":{"newStars":[…]}}
    /go current_state                               1 key
    /go initial_state                               1 key
    <sid>.json on disk                              1 key
    <sid>.initial.json on disk                      1 key

| mock | what `/go` returns after a partial `set` |
|---|---|
| **gitlab** | **REPLACES** — 41 keys -> 1 |
| **reddit** | **REPLACES** |
| shopping | shallow-merges |
| shopping_admin | shallow-merges |

**Why four careful readers got it wrong.** `dataManager.js:242 mergeOverDefaults`
is real and does merge — but it runs in the **browser**, refilling omitted keys
from `createInitialData()` as the SPA renders. The **state API**
(`vite.config.js:388`) writes the posted object verbatim to both files; only
`set_current` with `merge: true` (`:428`) merges server-side.

So after a partial `set` on gitlab or reddit:

* the **agent** sees a fully working site (client merge), and the replay passes;
* the **reward** reads `/go` and gets the partial, because evidence is built
  from `/go`.

*A lane cannot detect this by driving its own task.* Only a direct `/go` read
finds it — which is why it is recorded here rather than left to source reading.

**Always write `initial_setup.py` as a read-modify-write** — GET `/go`, mutate
the full document, POST it back. Correct on all four mocks, and immune to this
entire question.

## Tooling: `grep` lies about two files

    hub/websites/webarena_gitlab_mock/src/components/create/mutations.js
    hub/websites/webarena_reddit_mock/src/utils/markdown.js

Both contain NUL bytes -> `file` reports `data` -> ugrep suppresses matches and
exits **1**, indistinguishable from "not found". `mutations.js` holds every
gitlab creation handler, so a grep-based "that handler does not exist" verdict
about project/fork/commit/member operations is worthless. Use `grep -a` or read
the file in Python.

## The general rule

Three separate batch-6 lanes have now been saved by a `CORRECTIONS.md` entry
that the census still contradicts. **When the census and CORRECTIONS disagree,
CORRECTIONS wins** — it was verified later and against the running mock.
