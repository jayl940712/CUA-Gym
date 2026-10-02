# OpenStreetMap batch — 400 tasks (150 easy, 250 medium)

Delivered 2026-09-08 against `http://18.116.12.228:3000`.
Bundles: `output/map400/tasks/map/` · Rollout rows: `webarena_map_400.jsonl`

## 1. Corpus

| difficulty | family | count | what the agent must produce |
|---|---|---:|---|
| easy | `route_time` | 65 | one route, report the rendered time |
| easy | `route_distance` | 45 | one route, report the rendered distance |
| easy | `place_postcode` | 40 | one search, report the postcode |
| medium | `compare_modes` | 60 | two engines, report the faster **mode and its time** |
| medium | `nearest_of_three` | 55 | three routes, report the **winning place and its time** |
| medium | `time_gap` | 50 | two engines, report the **difference** in minutes |
| medium | `two_leg_time` | 45 | two routes, report the **total** minutes |
| medium | `two_leg_distance` | 40 | two routes, report the **total** kilometres |

**827 distinct places across 28 cities**, Pittsburgh to Portland ME. Engine mix:
foot 263, bike 211, car 191. Zero duplicate instructions, zero duplicate ids.

`medium` follows TASK_MAP.md section 6: **two dependent retrieval hops whose
reported value is derived and appears nowhere in the instruction.** Every medium
answer is a difference, a total, or the winner of a comparison, so an agent that
runs one route and stops earns the 0.4 proof-of-work component and nothing more.
The four pilot bundles in `osm_pilot/` are **not** part of this batch.

## 2. Ground truth

Computed at authoring time from the same Nominatim and OSRM services the site
calls, then frozen as literals. No reward makes a network call, runs an LLM, or
reads a clock. 1,617 OSRM calls and ~4,000 geocodes back the batch.

Nothing is hand-written. The place pool was **harvested from the deployment**
(`_osm_pool.py`: "<category> in <city>", then round-tripped through the exact
query string the task asks the agent to type) and filtered against the city's own
geocoded position (`_osm_pool_filter.py`). That filter matters: an early version
matched on the state name appearing in the address and silently deleted every
Pittsburgh and Philadelphia place, because Pennsylvania addresses render as
"Pittsburgh, Allegheny County, 15222, United States" with no state at all.

## 3. Gates — all 400

| gate | result |
|---|---|
| reward source purity (no network, no subprocess, no dynamic code) | **400/400** |
| click-reachability (replays click, never `goto`) | **400/400** |
| empty-episode probe (nothing pays at t=0) | **400/400** |
| negative controls, six scenarios each (section 4) | **400/400** |
| viewbox stability of every re-geocoding task | **140/140** |
| live verification, initial 0.0 → replay 1.0 | **400/400** |
| independent second live pass (flake screen) | **400/400**, 0 disagreements |
| third live pass, after the answer-contract rewrite (section 3a) | **400/400** |
| training reward reproduces the verified score under the rollout's own execution model | **400/400** |
| JSONL ↔ on-disk consistency | **400/400**, 0 drift |

Median 20 s per task, p95 28 s, max 30 s.

**What live verification actually proves.** The golden replay reads its answer
**off the page** and never sees the frozen ground truth. If the computed value
disagreed with what the site renders, the replay returns a different string and
the task scores 0.4, not 1.0. A 1.0 is therefore direct evidence that the frozen
value matches the site — the one property a self-consistent generator cannot
establish about itself.

## 3a. The answer contract in every instruction

The episode ends with a `terminate` tool call, and the string in that call's
`answer` field is the whole of what the reward sees (it arrives as
`CUA_GYM_AGENT_ANSWER`). Every instruction therefore names the tool, states
`status="success"`, and specifies the exact form of that string with a literal
example and a targeted prohibition:

| family | `answer` must be | example |
|---|---|---|
| `route_time` | the time in `H:MM`, nothing else | `0:25` |
| `route_distance` | the distance with its unit, no space | `1.7km` / `450m` |
| `place_postcode` | five digits only | `15213` |
| `compare_modes` | `<mode>: <H:MM>`, faster mode only | `walking: 0:25` |
| `nearest_of_three` | `<place>: <H:MM>`, winner only, no city suffix | `Heinz Hall: 0:07` |
| `time_gap` | whole minutes, digits only | `8` |
| `two_leg_time` | whole minutes, digits only | `37` |
| `two_leg_distance` | kilometres to one decimal + ` km` | `4.9 km` |

This closed a class of **correct answers scoring 0.4**. The parsers take the
first value they find, so on a `time_gap` task whose answer is 14:

```
"14"                                              -> 1.0
"14 minutes"                                      -> 1.0
"The difference is 14 minutes."                   -> 1.0
"The bike route takes 26 minutes and the car 12,
 so 14."                                          -> 0.4   <- correct, scored wrong
```

The prohibitions are specific to each family for that reason — `time_gap` says
"do not include the two individual travel times", naming the exact numbers that
would otherwise be parsed instead.

**The rewards were deliberately NOT tightened to match.** A precise prompt with a
forgiving parser scores correct answers; tightening both would fail answers that
are right but verbose. Nor was the parser made cleverer: a "take the last number"
heuristic would let a wrong answer pass whenever the true value happens to appear
as one of the leg times. Residual risk, stated plainly: an agent that ignores the
format instruction and lists both times still scores 0.4. That is a compliance
failure, not a scoring bug.

The wording lives in one function, `answer_spec()` in `_osm_batch_gen.py`, which
`_osm_reprompt.py` also calls — so a regenerated batch and this corpus cannot
disagree. Example values are generic and never a task's own answer.

## 4. Reward shape

Two components, the second **gated** on the first:

```
proof of work  0.4   a /directions URL with exactly the intended engine and both
                     endpoints within 0.005 deg (~500 m); or, for a lookup, the
                     /search URL carrying the place that was asked for
reported       0.6   the answer parses to the pinned value -- GATED, so guessing
                     without opening the route scores 0.0, not 0.6
```

Every bundle is scored against synthetic evidence for six scenarios and the whole
table must match exactly:

| scenario | required |
|---|---|
| right answer + intended work | 1.00 |
| **right answer, never routed** | **0.00** |
| right answer, landing page only | 0.00 |
| work done, wrong answer | 0.40 |
| wrong engine / wrong search | 0.00 |
| work in another city | 0.00 |
| empty episode | 0.00 |

Coordinates use a tolerance rather than equality (several names have multiple
hits); the `engine` parameter is matched exactly, since that is the whole point
of a walking-vs-driving task; the `#map=` fragment is ignored because it moves
with pan and zoom.

Margin gates, applied before a candidate is accepted: comparisons need a ≥3 min
separation; a gap or total must not coincide with either leg (or one leg answers
it); both derivations of a derived value — from the displayed minutes and from
the raw seconds — must agree, or the task has two defensible answers.

## 5. Defects found

Five, all recorded in `output/CORRECTIONS.md` as MAP-1..MAP-5. Two were latent
harness defects that would have shipped silently:

**MAP-1 — the rollout worker never supplied final URLs.** `browser_worker.py`
passed only `CUA_GYM_AGENT_ANSWER` and `CUA_GYM_AGENT_STATUS`. Every URL-gated
task would have verified at 1.0 and trained at 0.0. Fixed by passing the
episode's open-tab URLs as `CUA_GYM_FINAL_URLS`.

**MAP-2 — an off-hub site could not be opened.** `reset()` resolves the site
through `hub_apps.APP_DIRS` by index and appends `?sid=`; a real Rails app has
neither. Fixed with an optional `CuaGymTaskInfo.external_base_url`. `hub_apps.py`
was not touched, and hub tasks take a byte-identical path.

**MAP-6 — the training reward was not self-contained.** `nemo_reward.py`
imported a sibling `reward.py` via `__file__`, but `run_code` pipes the source to
`python -` in an empty temp directory where `__file__` does not exist. Every map
task would have crashed at rollout. It is now reward.py's own source with an
entry point appended, and `_osm_nemo_check.py` runs all 400 under the rollout's
exact execution model. **Nothing in the normal gate chain looks at this file** —
that is the gap worth closing for future batches.

The other three (site quirks and generator bugs) are MAP-3 stale OSRM hints,
MAP-4 view-dependent geocoding, MAP-5 ambiguous winner tokens.

## 6. Honest notes

* **Verification ran in `legacy` mode**, as batches 5 and 6 did — `--mode
  hardened` falls back silently because `CUA_GYM_ADMIN_TOKEN` is empty. Accepted
  baseline, not a regression.
* **`webarena_map_mock` is a real deployment, not a mock.** The name is required
  by `MOCK_RE` in `cua_gym_web/models.py`. There is no seeded state and no reset:
  if the underlying OSM data changes, frozen answers go stale. Re-run
  `_osm_verify.py` to detect that; every failure would surface as 0.4, not 1.0.
* **No `fuzzy_match` anywhere.** 48 of the 128 official map tasks use an LLM
  judge; none of that is replicated. All parsing is syntactic.
* **The batch is not a superset of the official map corpus.** Families needing
  free-text address comparison or spatial judgement were not built, because they
  cannot be scored deterministically from the DOM.
* **Coverage is northeast-only** and thinner than the city list suggests:
  Cleveland, Akron, Youngstown and Toledo hold almost no POI data and were
  dropped; New Haven contributes only 7 tasks.
* **The two harness edits are uncommitted working-tree changes.** A branch or
  reset loses them, and map tasks then fail in ways whose cause is not obvious
  from the error.
