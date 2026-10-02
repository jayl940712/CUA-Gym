# TASK_MAP.md — Generating and verifying OpenStreetMap RL tasks

You are running this end-to-end. Work through the phases in order. The decisions
below are already made; do not re-litigate them.

**This is the first map batch.** Six batches exist on disk and are read-only:

| Snapshot | Tasks | Sites |
|---|---|---|
| `webarena_08_18_batch_200/` | 198 | gitlab / reddit / shopping / shopping_admin |
| `webarena_08_19_batch_200/` | 199 | same four |
| `webarena_08_21_batch_600_easy/` | 600 | same four |
| `webarena_09_02_hard/` | 600 | same four |
| `webarena_09_04_skills/` | 600 | same four |
| `webarena_09_08_medium_600/` | 600 | same four |

**None of them contain a map task**, so there is no dedupe pressure from prior
batches. The constraint here is different and harder: the map site has **no
persisted state to assert**, so every reward shape from those six batches is
inapplicable. Read §4 and §5 before designing a single task.

**Target: 500 tasks, all `medium`, all on the map site.**

---

## 1. Why this batch is structurally different

Batches 1–6 scored **persisted state**: the agent mutated something, and the
reward read it back from the mock's `/go?sid=` endpoint. The map deployment is a
real OpenStreetMap Rails app. It has:

* **no `/go?sid=` endpoint** — it returns 404, and `cua_gym_web/state.py:_json`
  *raises* on a non-OK response, so a map task crashes before any reward runs
  unless the app is declared stateless (§3);
* **no meaningful mutation surface** — `/notes/new` is 404, diary and traces
  require an account, and **all 128 official map tasks are anonymous queries**,
  so login-based mutation tasks would be out of distribution;
* **no precondition injection** — there is no state to inject, so
  `initial_setup.py` does not apply and the dedupe/diversity levers from batch 5
  and 6 are unavailable.

The official corpus reflects this. Of 128 map tasks in
`webarena_benchmarks/webarena.jsonl` (`web_name` contains `"map"`):

| eval type | count | note |
|---|---|---|
| `string_match` | 94 | the agent reports an answer; 48 of these use `fuzzy_match`, **which is an LLM judge** |
| `program_html` | 29 | DOM/form state |
| `url_match` | 5 | final URL |

**We do not use an LLM judge anywhere.** §5 replaces `fuzzy_match` with pinned
values computed from the same services the site calls.

---

## 2. Infrastructure

| Service | URL | Notes |
|---|---|---|
| Website | `http://<OSM_HOST>:3000/` | OpenStreetMap Rails app |
| Nominatim (geocoding) | `http://<OSM_HOST>:8085/` | the Go button |
| OSRM car | `http://<OSM_HOST>:5000/` | |
| OSRM bike | `http://<OSM_HOST>:5001/` | |
| OSRM foot | `http://<OSM_HOST>:5002/` | |

**Coverage is the US northeast only.** Do not assume a famous name resolves —
verify every place string (§7.1). Pittsburgh/CMU, Boston/Cambridge, New Haven and
New York all resolve; anything outside the northeast probably does not.

Verified determinism (measure again if results look unstable):

* OSRM: **6/6 byte-identical** responses to repeated identical calls.
* Nominatim: **4/4 byte-identical** top hits.

Set the endpoint before running anything:

```bash
export CUA_GYM_WEBARENA_MAP_URL="http://<OSM_HOST>:3000"
```

The app spec in every `task.json` is:

```json
{"name": "webarena_map_mock", "source_name": "map",
 "base_url_env": "CUA_GYM_WEBARENA_MAP_URL", "start_path": "/",
 "initial_state": null, "golden_state": null, "stateless": true}
```

`webarena_map_mock` is the required naming convention (`MOCK_RE` in
`cua_gym_web/models.py`); it derives `CUA_GYM_WEBARENA_MAP_URL` automatically.
The name says "mock" but this is a real deployment — that is fine.

---

## 3. Harness changes that are ALREADY MADE

These are on disk. Do not re-implement them; do verify they are still present.

**Answer capture** — lets a reward score what the agent *reported*, which is
the dominant official family and impossible in batches 1–6:

1. `cua_gym_web/runner.py` — `BrowserLane.answer: str | None = None`.
2. `cua_gym_web/runner.py` (~line 195) — the replay's return value is now
   **kept**. It previously computed `await result` and discarded it.
3. `cua_gym_web/evidence.py` — `collect(..., answer=None)` emits
   `"agent_answer": answer or ""` at the top level of the evidence document.
4. `cua_gym_web/runner.py::_evaluate_lane` — passes `answer=lane.answer`.
5. `scripts/empty_state_probe.py` — synthesises `"agent_answer": ""`.

**Stateless-app support** — required or map tasks crash:

6. `cua_gym_web/models.py` — `AppSpec.stateless: bool = False`.
7. `cua_gym_web/runner.py` — a stateless app gets no `StateClient`, no `?sid=`
   on its URL, a synthetic `SessionHandle`, and empty state dicts in evidence.

**The NeMo rollout side is unchanged and must stay unchanged.**
`cuagym/browser_worker.py:260` already captures `terminate(answer=...)` and
`:303` already passes it as `CUA_GYM_AGENT_ANSWER`. That path worked before this
batch; only the verification side was missing.

**How the answer flows:**

| | verification | training rollout |
|---|---|---|
| driver | `cua_gym_web/runner.py` | `cuagym/browser_worker.py` |
| answer source | `golden_replay.run()` return value | agent's `terminate(answer=…)` |
| reward reads | `evidence["agent_answer"]` | `os.environ["CUA_GYM_AGENT_ANSWER"]` |
| reward file | `reward.py` → `evaluate(evidence)` | `nemo_reward.py` → prints `REWARD: <n>` |

**Both channels must normalise identically** (`or ""` then `.strip()`), or a task
verifies one way and trains another. `reward.py` **cannot** `import os` —
`ALLOWED_IMPORTS` in `cua_gym_web/reward.py` is exactly `{collections, datetime,
decimal, fractions, json, math, re, statistics, urllib.parse}`. It does not need
to; the answer is in the evidence document.

**The initial lane never runs a replay**, so `agent_answer` is `""` there and an
answer-scored reward reads 0.0 automatically. That is what preserves the
initial-0.0 / replay-1.0 discrimination with no special-casing.

Regression status after these edits: 24/24 tests in `tests/` pass, all 600
batch-6 rewards still score 0.0 on empty state, and a shipped gitlab task
re-verified 0.0 → 1.0.

---

## 4. Ground truth — the procedure, and two wrong turns to avoid

**Compute every answer offline from Nominatim + OSRM at authoring time, then
freeze it into the reward as a literal.** The reward makes no network call.

Reproducing what the UI renders takes four steps. Skipping any one produces a
wrong answer that the reward will then enforce.

**Step 1 — geocode WITH the site's `viewbox`.** The site biases Nominatim to the
current map view. From a cold `/` load (`#map=7/42.896/-75.108`) the viewbox is:

```
-82.79296875000001,39.402244340292775,-67.41210937500001,46.20264638061019
```

Omitting it can select a different top hit, i.e. a different place entirely.

**Step 2 — keep FULL precision.** ✗ *Wrong turn:* the `?route=` parameter in the
URL bar shows 3 decimals (`40.444,-79.943`), which looks authoritative. It is
**display only**. A network capture shows the site calling OSRM with
`-71.0966272383055,42.3582529;…`. Rounding first produced `0:18` and `1.8km`
where the site renders `0:17` and `1.7km`.

**Step 3 — call OSRM with the site's own query string:**

```
/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false&geometries=polyline&steps=true
```

The `/driving/` path segment is fixed regardless of engine; the engine is chosen
by **port** (5000 car / 5001 bike / 5002 foot).

**Step 4 — format with the site's own functions**, transcribed from its JS
bundle (`/assets/index.debug-*.js`):

```python
def fmt_time(s):                       # formatTime
    m = round(s / 60); h = m // 60; m -= h * 60
    return f"{h}:{m:02d}"

def fmt_dist(m):                       # formatDistance
    if m < 1000:  return f"{round(m)}m"
    if m < 10000: return f"{m/1000.0:.1f}km"
    return f"{round(m/1000)}km"
```

Working reference implementation: **`scripts/_osm_pilot_gen.py`**. Reuse it.

**Validation rule:** before shipping any task, confirm the computed string equals
what the live site renders. All four pilot tasks were checked this way.

---

## 5. Reward shape

Two components. **The second is gated on the first.** No LLM, no fuzzy matching.

```
routed_*    0.4   the final URL is a /directions page whose `engine` parameter
                  is exactly the intended one, and whose two route endpoints are
                  within TOL (0.005° ≈ 500 m) of the intended places.
reported_*  0.6   the reported answer parses to the pinned value.
                  GATED on routed_*, so guessing scores 0.0 rather than 0.6.
```

Why each choice:

* **Tolerance, not string equality, on coordinates.** Several place names have
  multiple Nominatim hits (Carnegie Mellon has three). Any reasonable pick must
  pass; a route from the wrong city must not.
* **Exact match on the `engine` parameter.** That is the whole point of a
  walking-vs-driving task.
* **The `#map=…` fragment is excluded.** It moves with pan and zoom.
* **`final_html` is unusable for form fields.** Verified: the live input value
  `'40.444, -79.944'` does **not** appear in `page.content()` — the tag carries no
  `value=` attribute. The official `program_html` locators therefore cannot be
  ported. Use `final_urls`.
* **Answer parsing is deterministic**: `\d+:\d{2}`, then `Nh Nm`, then `N min`,
  then a bare integer; distances accept km or m within 50 m. No similarity
  scoring.

Reference reward: `osm_pilot/tasks/map/*/reward.py`.

### 5.1 Negative controls are mandatory

Passing is not evidence the reward discriminates. Every task must produce this
table before shipping (see the pilot for the harness):

| scenario | required |
|---|---|
| right answer + right route | **1.00** |
| **right answer, never routed** | **0.00** ← the anti-gaming property |
| routed, wrong answer | 0.40 |
| wrong engine | 0.00 |
| right answer, route in another city | 0.00 |
| empty episode | 0.00 |

### 5.2 Margin discipline

Compute what the **other two engines** would render. If the intended answer
collides with either, **drop the task** — it does not test the engine choice.
One pilot candidate was dropped this way (foot 840 m vs bike 837 m, a 3 m gap).

---

## 6. What `medium` means here

Batches 1–6 defined medium as one retrieval + one action. Map tasks have no
action, so that rule does not transfer. For this batch:

> **medium = two dependent retrieval hops, where hop 1's result is required to
> perform hop 2, and the reported value is DERIVED — it never appears in the
> instruction.**

**The four pilot tasks do not meet this bar.** They dictate both endpoints
("route from CMU to Univ of Pittsburgh"), so the agent transcribes two names into
a form. They exist to prove the *mechanism*, not the difficulty. Treat them as
`easy` reference implementations and do not count them toward the 500.

| | example | verdict |
|---|---|---|
| ✗ dictated | "Walk from CMU to Univ of Pittsburgh; report the time." | easy — no retrieval |
| ✓ derived endpoint | "Walk from CMU to the nearest cafe; report the time." | medium — hop 1 finds the cafe, hop 2 routes to it |
| ✓ derived comparison | "Is it faster to walk or cycle from X to Y? Report the faster time." | medium — two routes, then a comparison |
| ✓ derived attribute | "Find the university nearest to <landmark>; report its postcode." | medium — locate, then read an attribute |
| ✗ three hops | "Find the nearest cafe to the nearest library to X…" | too hard for this batch — split it |

Buildable official families (use these as templates —
`webarena_benchmarks/webarena.jsonl`, filter `web_name` contains `map`):

| family | official ids | buildable? |
|---|---|---|
| travel time A→B | 52–56 | yes, if an endpoint is derived |
| compare walk vs drive | 16–20 | yes — needs the reported answer |
| nearest amenity to X | 57–61 | yes, with §7.1 care |
| zip code / full address of X | 70–73, 7–10 | yes — search URL + reported answer |
| reachable within N minutes? | 36–40 | yes — reported yes/no + the route |
| multi-leg ("first walk, then drive") | 80–84 | yes, but verify both legs appear |

---

## 7. Traps that cost real time

**7.1 Nominatim phrasing is fragile — this is the single biggest authoring risk.**
`"starbucks on Craig Street"` — the exact wording of official webarena-52 —
returns **zero results** here, while `"Starbucks Craig Street Pittsburgh"`
returns exactly one. **Verify every place string resolves to the intended single
hit before building a task on it.** Record the hit count in metadata.

**7.2 Every control exists twice.** A mobile copy and a desktop copy share the
same id/name, and the first is hidden. `#query`, `route_from`, `route_to`,
`select.routing_engines` and the Directions link all return `count()==2`.
**Always use `:visible`**, e.g. `page.locator("#query:visible").first`.

**7.3 Clicking Directions re-renders the sidebar.** Wait for
`[name='route_from']:visible` before filling. Filling too early silently loses
the value, Go submits an empty form, and no route renders.

**7.4 Typing a place name triggers geocoding that REWRITES the field** to the
full display name (`"Carnegie Mellon University, Schenley Drive Extension, …
15213, United States"`). Allow it to settle before clicking Go.

**7.5 The distance contains a period.** A regex like `Distance:\s*([^.]+)\.`
fails on `1.9km`. Use:

```python
re.search(r"Distance:\s*(.+?)\.\s+Time:\s*(\d+:\d{2})", text)
```

**7.6 Answers live in the DOM, not in pixels.** Everything scoreable —
addresses, postcodes, distances, durations, turn-by-turn steps — is text inside
`#sidebar_content`. Screenshots work and are readable, but are **not required**
for these families. Vision only matters for genuinely spatial judgments.

**7.7 Reachability still applies.** Replays must click, never `goto`. The runner
already lands the lane on `start_path`. Deep-linking `/directions?engine=…` works
in a browser but fails `scripts/check_reachability.py`.

---

## 8. Authoring workflow

**Per task:**

1. Choose a family (§6) and a northeast entity. Verify it resolves (§7.1).
2. Compute ground truth via `scripts/_osm_pilot_gen.py` (§4).
3. Check margins against the other two engines (§5.2).
4. Write the bundle: `task.json`, `task_instruction.json`, `reward.py`,
   `nemo_reward.py`, `golden_replay.py`.
5. The replay must **return** the answer string (§3).

**Gates, in order:**

```bash
# 1. click-reachability
python3 scripts/check_reachability.py <bundle>/golden_replay.py --quiet

# 2. nothing pays on an empty episode
python3 scripts/empty_state_probe.py <tasks_root> --quiet

# 3. reward purity: no network, no subprocess, no dynamic code
python3 -c "from cua_gym_web.reward import validate_reward_source as v; \
            v(open('<bundle>/reward.py').read())"

# 4. end-to-end verification against the live site
export CUA_GYM_WEBARENA_MAP_URL="http://<OSM_HOST>:3000"
python3 scripts/run_webarena_task.py <bundle>/task.json \
        --replay <bundle>/golden_replay.py --output <out> --mode legacy
#    require: initial 0.0, replay 1.0

# 5. negative controls (§5.1)
```

At scale, drive verification with `scripts/batch_orchestrator.py`. Two settings
learned the hard way in batch 6:

```bash
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
python3 scripts/batch_orchestrator.py <tasks_root> --mode hardened \
        -c 10 --timeout 45 --dangerously-skip-permissions
```

* Without the env var, verification sub-agents are killed at a 600 s background
  wait ceiling — **exit code 0, no verdict**, which reads as a task defect.
* `--mode hardened` **silently falls back to legacy** because
  `CUA_GYM_ADMIN_TOKEN` is empty in `.env`. Batches 5 and 6 both ran legacy; this
  is the accepted baseline, not a regression. Do not chase it.

Status and export:

```bash
python3 scripts/_b5_status.py --failures      # all five verification conditions
python3 scripts/detect_flaky.py               # then re-run final artifacts 3x
python3 scripts/export_nemo_rollouts.py <batch_dir> --output <name>.jsonl
```

`_b5_status.py` and `export_nemo_rollouts.py` were fixed in batch 6 to order
attempt rounds correctly (numeric when every label is a plain `attempt-<int>`,
by mtime otherwise) and to accept a verdict in `audit_sandbox/REVIEW.md`. Keep
those fixes.

---

## 9. Reference implementation

| Path | What |
|---|---|
| `scripts/_osm_pilot_gen.py` | ground-truth computation + bundle writer |
| `osm_pilot/tasks/map/osm_route_time_walk_cmu_to_pitt/` | foot, time, `0:25` |
| `osm_pilot/tasks/map/osm_route_time_drive_cmu_to_chatham/` | car, time, `0:04` |
| `osm_pilot/tasks/map/osm_route_time_bike_mit_to_harvard/` | bike, time, `0:17` |
| `osm_pilot/tasks/map/osm_route_distance_walk_cmu_to_chatham/` | foot, distance, `1.7km` |

All four verify 0.0 → 1.0 against the live site and pass all negative controls.
They are `easy` by §6 and are reference material, not batch content.

---

## 10. Definition of done

1. **500 tasks**, all `medium` per §6, all on `webarena_map_mock`.
2. Every place string verified to resolve (§7.1), hit count recorded.
3. Every ground-truth value confirmed against the live site (§4).
4. Every task passes all five gates in §8, including negative controls.
5. Flake screen: any task flagged gets its **final artifacts** re-run 3× and must
   score 0.0 / 1.0 every time. Batch 5 and 6 both found every flag to be
   convergence, not flakiness — check, do not assume.
6. Export to `<name>.jsonl` with 500/500 rows.
7. A `FINAL_REPORT.md` recording the corpus, the gates, anything found wrong in
   this document, and any task family that had to be dropped and why.

**Rules carried over from batches 1–6, non-negotiable:**

* Never relax a reward, delete an agreement condition, or mark a task verified on
  a partial result.
* The scored value must be **derived, never dictated**.
* Check tie margins yourself and record them.
* Never modify anything under `hub/`.
* Prior batch snapshots are read-only.
* Write generators to `scripts/`, never inside the batch directory — two batch-6
  lanes lost their work to a bulk delete under the output tree.


---

## 11. STATUS — a 400-task batch is built (read this first)

**`output/map400/` holds 400 verified tasks (150 easy, 250 medium)**, delivered
2026-09-08. Read `output/map400/FINAL_REPORT.md` before building more; it records
the corpus, every gate, and six defects. The generator is reusable:

| script | what it does |
|---|---|
| `scripts/_osm_common.py` | Nominatim/OSRM access with the site's own parameters, and its formatters |
| `scripts/_osm_pool.py` | harvests places FROM the deployment and round-trips each query string |
| `scripts/_osm_pool_filter.py` | drops mislocated, chain-named and out-of-extract places |
| `scripts/_osm_batch_gen.py` | eight task families, margin gates, bundle writer |
| `scripts/_osm_controls.py` | the section 5.1 negative-control table, all six scenarios |
| `scripts/_osm_viewbox_audit.py` | catches tasks whose later geocodes flip when the map moves |
| `scripts/_osm_verify.py` | parallel live verification (initial 0.0 / replay 1.0) |
| `scripts/_osm_nemo_check.py` | runs the TRAINING reward the way the rollout runs it |
| `scripts/_osm_repair.py` | drops and replaces condemned bundles without regenerating the batch |
| `scripts/_osm_export.py` | rollout JSONL |

**Six corrections to this document, learned by building the batch.** All six are
written up in `output/CORRECTIONS.md` as MAP-1..MAP-6.

1. **Section 3 was wrong that "the NeMo rollout side is unchanged and must stay
   unchanged."** It needed two changes or nothing could train:
   `browser_worker.py` now passes `CUA_GYM_FINAL_URLS` (nothing set it, so every
   URL-gated reward would have trained at 0.0), and `CuaGymTaskInfo` gained an
   optional `external_base_url` (an off-hub site has no `APP_DIRS` entry, so
   `app_port` raised before the episode began). `hub_apps.py` was not touched.
2. **`nemo_reward.py` must be SELF-CONTAINED.** `run_code` pipes it to `python -`
   in an empty temp dir: `__file__` is undefined and there is no sibling module.
   Build it from `reward.py`'s own source. **No existing gate loads this file** —
   run `_osm_nemo_check.py`.
3. **Geocoding is view-dependent across legs.** Any task that fills the
   Directions form twice re-geocodes under a MOVED map and can resolve a
   different branch of the same name. Probe several view widths — a single wide
   probe misses the tight-view flips. Multi-hit names are not themselves the
   defect; 47 of 140 contained one and only one task actually flipped.
4. **The site poisons its own routing with stale OSRM hints.** Refilling the form
   momentarily makes both endpoints identical; the degenerate query's `hints` get
   cached and the real request returns 400 `NoRoute`. Retrying does not help.
   **Clear both fields before refilling.**
5. **Distinct tokens do not make an unambiguous answer** — a competitor's token
   can sit inside the winner's own name. Check tokens against full names and
   replay the reward's reading rule over the expected answer at authoring time.
6. **Do not hand-write place lists.** Harvest them from the deployment and
   round-trip every query string. Also: do not filter on the state name appearing
   in an address — Pennsylvania addresses omit it, and that rule silently deleted
   every Pittsburgh and Philadelphia place.

**7. Every instruction must carry an answer-format contract.** The reward sees
only the `answer` string of the agent's `terminate` call, and the parsers take
the first value they find — so "the bike route takes 26 minutes and the car 12,
so 14" scores 0.4 on a task whose answer is 14. Name the tool, state
`status="success"`, give the exact string form with a literal generic example,
and forbid the specific extra values that would be parsed instead. Do NOT tighten
the parser to match: keep the prompt precise and the parser forgiving. The
wording lives in `_osm_batch_gen.answer_spec()`.

**Difficulty definitions used, since section 6 only defined `medium`:**

* `easy` — one hop; the instruction names everything, the work is driving the UI
  and reading one value.
* `medium` — two dependent hops and a **derived** value: a difference, a total,
  or the winner of a comparison. Never transcribable from the instruction, never
  readable off a single route.

To extend the batch to 500, run `_osm_batch_gen.py` with larger quotas and a new
seed, then the gate chain in section 8 **plus** `_osm_viewbox_audit.py` and
`_osm_nemo_check.py`.
