# OpenStreetMap HARD batch — 400 tasks

Delivered 2026-09-10 against `http://18.116.12.228:3000`.
Bundles: `output/maphard/tasks/map/` · Rollout rows: `webarena_map_hard_400.jsonl`

Built because the first map batch (`output/map400/`, `webarena_map_400.jsonl`)
measured **88%** and was too easy. That batch's diagnosis is section 1.

## 1. Why the first batch was easy

All eight of its families exercised ONE skill. Every task named its endpoints as
exact resolvable strings, named the routing engine as the literal dropdown label
("Bicycle (OSRM) routing engine"), and put the answer on the same
`Distance: … Time: …` line. Its `medium` tier ran that identical loop two or
three times.

The definition was the mistake: `medium` was "two dependent retrieval hops", but
both hops were the same trivial action with different inputs. **Dependency is not
difficulty when the dependent step is free.**

Reading the 128 official map tasks in `webarena_benchmarks/webarena.jsonl`, the
axes it used none of were: unnamed endpoints reached through a category search,
threshold enumeration over a result set, attributes instead of routes, optimal
ordering, and colloquial modes. Two UI surfaces went completely untouched — the
category-search result list, and the `/node|/way/<id>` object page with its OSM
tag table.

## 2. The corpus

| family | n | tier | routes | surfaces | the lever |
|---|---:|:---:|---:|---:|---|
| `nearest_of_five` | 60 | 3 | 5 | 2 | destination **not named** — search a category, route all five results, rank |
| `count_within_minutes` | 50 | 3 | 5 | 2 | route all five, count those inside a bound |
| `nearest_then_attribute` | 45 | 3 | 5 | 3 | rank five, then open the winner's object page for a tag |
| `optimal_order` | 45 | 3 | 3 | 1 | three stops, six orders, report order **and** total |
| `fastest_of_three_modes` | 45 | 2 | 3 | 1 | all three engines, not two |
| `reachable_within` | 45 | 2 | 1 | 1 | yes/no against a bound, plus the actual time |
| `poi_attribute` | 65 | 1 | 0 | 1 | search → click result → read `phone`/`website`/`opening_hours`/`operator`/`cuisine` |
| `poi_coordinates` | 45 | 1 | 0 | 1 | `Location:` in DD format |

"routes" is how many separate routings the golden replay performs; "surfaces" is
how many distinct UI surfaces it visits (directions panel / search list / object
page). Both are mechanical counts, not difficulty measurements.

**Tiers: 200 at tier 3, 90 at tier 2, 110 at tier 1.** 28 cities, no duplicate
instructions, no duplicate ids. Three levers apply across every family: the mode
is colloquial ("by car", never "Car (OSRM)"), the ranking families never name the
destination, and most answers come from somewhere other than the Distance/Time
line.

`poi_coordinates` is restricted to **nodes**: ways and relations render their tag
table but no single `Location:` line, so a task built on one would have no answer
on screen.

Ranking families use the **first five** results rather than all ten. Ten
candidates is fifty-odd actions before the agent starts reasoning, and a task
that fails on a turn limit measures the limit, not the agent.

## 3. Gates — all 400

| gate | result |
|---|---|
| reward source purity | **400/400** |
| click-reachability | **400/400** |
| empty-episode probe | **400/400** |
| negative controls, six scenarios each | **400/400** |
| viewbox stability of every re-geocoding task | **200/200** |
| live verification, initial 0.0 → replay 1.0 | **400/400** |
| training reward reproduces the verified score under the rollout's own execution model | **400/400** |
| JSONL ↔ on-disk consistency | **400/400**, 0 drift |

Replay time: median 25 s, p95 47 s, max 49 s.

The negative-control table gained three scenarios for the new shapes: opening the
**wrong** object page scores 0.0, stopping at the search results without opening
anything scores 0.0, and for `optimal_order` both "right order, wrong total" and
"right total, wrong order" score 0.4.

## 4. Defects found and fixed

**A quoted tag value produced un-parseable Python.** `"Open only during baseball
games"` is a real `opening_hours` value, quotes included; pasted into a
triple-quoted literal it made four consecutive quotes. Constants are now injected
with `repr()`, which is safe for any content. Caught by gate 1.

**Three `optimal_order` tasks were view-unstable.** Same class as MAP-4 in the
first batch: retyping a bare place string after the map has moved can resolve a
different object. Notably the ranking families had **zero** such failures — they
type the full display name the results list shows, which pins the object far more
tightly. The check now runs for `optimal_order` too; the three were replaced.

**HTML collapses whitespace, so a candidate-list assertion misfired.** `"East
Side -  Post Office"` carries a doubled space in OSM data; rendered, it has one.
The replay's check that the site still lists the ground-truth candidates compared
literally and reported a mismatch that was not one. It now collapses whitespace
on both sides. This was the single failure in the first live pass (399/400); the
fix was applied to the template and all 155 ranking replays were re-verified,
155/155.

**The training-reward checker pinned a fixed attempt label**, so a task whose
passing run was `attempt-2` read as missing evidence. It now falls back to the
most recent attempt.

## 5. Honest limits

* **I have not measured a pass rate.** There is no agent harness in this
  workspace; 88% is your measurement of the first batch. Everything above is
  difficulty *by construction* plus mechanical proxies. The `difficulty_tier`
  field exists so a measured sample can be reweighted without regenerating.
* **If tier 3 is still too easy**, the strongest untapped dials are: raise the
  candidate count from five to ten, chain a third surface onto more families, and
  stop naming the anchor's city.
* Verification ran in `legacy` mode, as every batch since batch 5 has.
* No `fuzzy_match` anywhere; 48 of the 128 official map tasks use an LLM judge
  and none of that is replicated.
* Coverage is northeast-only, and the same four data-poor cities are absent.
* The harness edits under `cuagym/` and `cua_gym_web/` remain uncommitted.
