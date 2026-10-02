# Batch 5 — 600 skill-aligned WebArena RL tasks

**All 600 authored, all 600 verified, all 600 exported.** No shortfall.

`webarena_09_04_skills.jsonl` — 600 rows, validated.

## What made this batch different

Batches 1–4 selected tasks by **topic** and measured alignment on intent shape
and scoring style. A task can match both and exercise nothing the benchmark
exercises. Batch 5 selects by **skill chain**, derived by reading all 583
distinct in-scope intent templates in `webarena_benchmarks/webarena.jsonl`
(686 instances: gitlab 193, shopping 165, shopping_admin 153, reddit 95).

`docs/SKILL_TAXONOMY.md` defines 10 retrieval and 13 action skills, each
grounded in named official tasks. Every bundle records the skills it
exercises, the chain, and a **verbatim** official analogue — cross-checked at
gate time against all 799 indexed intents, so a paraphrase or invention fails.

## Delivered

| | gitlab | reddit | shopping | shopping_admin | total |
|---|---|---|---|---|---|
| bundles | 150 | 150 | 150 | 150 | **600** |
| verified | 150 | 150 | 150 | 150 | **600** |
| exported | 150 | 150 | 150 | 150 | **600** |

* **difficulty** 0 easy / 168 medium / 432 hard — *derived from chain shape,
  not quota'd*. Multiple lanes relabelled **down** rather than pad a skill list;
  two declined to relabel down when doing so would have gutted the task.
* **style** 450 terse / 150 explicit — exact, and exact per site.
  Terse intents mean 28.7 words, median 29, max 40 (official mean is 18).
* **start_path** 596 of 600 at `/` (99.3%; floor was 420). The four deep starts
  are category listing pages that are the task's own subject (S5.1).
* **retrieval-writeback** 487 (target ~180).
* **injected preconditions** 210 bundles.
* **skill coverage 23/23** — no skill unrepresented.

Retrieval: R1 131 · R2 64 · R3 127 · R4 168 · R5 190 · R6 88 · R7 59 · R8 40 · R9 144 · R10 67
Action: A1 64 · A2 95 · A3 40 · A4 171 · A5 12 · A6 19 · A7 216 · A8 88 · A9 51 · A10 65 · A11 25 · A12 40 · A13 39

A5 (12) and A6 (19) are low because both are **absent from three of the four
mocks** — they exist only on shopping_admin. A13 (39) is deliberately scarce:
it is 1–2% of the official corpus and is the hardest skill to author honestly.

## Verification — every S9 condition, all 600

| condition | result |
|---|---|
| S9.1 `## Verdict: PASS` | 600/600 |
| S9.2 attempts agree (final round) | 600/600 |
| S9.3 initial 0.0 / replay 1.0 | 600/600 |
| S9.4 click-reachability | **600/600** |
| S9.5 reward scores 0.0 on `{}` | 600/600 |
| static gate | 600/600 |

**Reachability is 600/600 against batch 4's 594/600**, on replays written fresh
by `golden-browser` under the S6 gate with automatic reroute.

`detect_flaky.py` flagged 5 tasks. All 5 were run down to a cause as S9 requires:
each task's **final** artifacts were re-run three times, **15 of 15 runs stable**
at initial 0.0 / replay 1.0. All five were convergence, not flakiness — the
script compares scores across adversarial rounds, and the orchestrator rewrites
`reward.py` and `golden_replay.py` between rounds, so different attempts ran
different code. Fixed in the export's own verdict logic.

## The verification loop did real work

* `reward.py` was **rewritten by the loop in 31 of 284 measured runs (11%)**.
  One example: an author matched contributor names by bare substring, so
  `Vikas` would match inside `Vikash`; `reward-gen` anchored the pattern with
  `\b`, documented why, and pushed it back to the canonical bundle.
* `grant_access_top_repos_008` round 1 had the **initial lane score 0.15** — a
  S9.3 violation no static gate can see. Rounds 2–3 score 0.0. Caught and fixed
  unprompted.
* 271 runs settled in 2 rounds; 6 took 3, 4 took 4, one 5, one 6.

## Honest notes

* **12 shopping tasks failed first time and all 12 passed on retry.** They were
  flaky, not unreachable — my hypothesis that a capture-vs-derived pagination
  gap made their targets unreachable was **wrong**, and retrying before dropping
  them saved 12 tasks.
* **The three empty-state repairs were nearly lost.** I held them out of the
  wave to fix, they were repaired and re-probed clean, and I failed to re-queue
  them. Found by enumerating tasks with no run directory that were never queued
  — a completion percentage is a ratio over the queue and cannot show work
  missing from the queue itself.
* **One run's REVIEW.md was never copied out of `audit_sandbox/`.** I confirmed
  the audit had genuinely run (12 sections, `## Verdict: PASS`, four
  verification copies at 0.0/1.0) before copying it to the run root. Artifact
  placement, not verdict manufacture.
* **Three no-op `initial_setup.py` stubs** were documentation placeholders;
  `initial_setup: null` was correct and my first repair wrongly inlined them.
  Reverted, stubs archived as `.noop_documented`.

## Findings

`output/CORRECTIONS.md` — **122 verified findings**, each traced to source.
Roughly half are cases where an inherited claim was *right about the mechanism
and wrong about the consequence*, which implies the wrong remedy. Five census
enumerations proved **incomplete rather than wrong**, twice understating what a
site supports. Six distinct progress-reader defects, all sharing one shape:
correct about the file read, wrong about what its absence meant.
