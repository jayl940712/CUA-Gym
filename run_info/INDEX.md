# run_info — one place for every batch's run-level documents

**These are copies.** Every original is still where it was; nothing was moved or
deleted. Several of these files are the only record a read-only snapshot carries
about itself, so removing them from their batch would leave it undocumented.

Naming is `<batch-key>__<ORIGINAL_NAME>`, which keeps two batches' identically
named reports apart while leaving the original filename readable.

Per-bundle artifacts are deliberately excluded: the thousands of `REVIEW.md`,
`SCHEMA.md` and `GENERATION.md` files under `tasks/` and `runs/` document single
tasks, not runs.

`MANIFEST.json` holds the machine-readable source -> copy mapping.

| copy | came from | batch |
|---|---|---|
| `b1__TASK.md` | `TASK.md` | Batch 1 |
| `b1__PROGRESS.md` | `webarena_08_18_batch_200/PROGRESS.md` | Batch 1 |
| `b1__FLAKY_REPORT.md` | `webarena_08_18_batch_200/FLAKY_REPORT.md` | Batch 1 |
| `b2__TASK2.md` | `TASK2.md` | Batch 2 |
| `b2__AUTHOR_BRIEF.md` | `webarena_08_19_batch_200/AUTHOR_BRIEF.md` | Batch 2 |
| `b2__PROGRESS.md` | `webarena_08_19_batch_200/PROGRESS.md` | Batch 2 |
| `b2__FLAKY_REPORT.md` | `webarena_08_19_batch_200/FLAKY_REPORT.md` | Batch 2 |
| `b3__TASK3.md` | `TASK3.md` | Batch 3 |
| `b3__AUTHOR_BRIEF.md` | `webarena_08_21_batch_600_easy/AUTHOR_BRIEF.md` | Batch 3 |
| `b3__PROGRESS.md` | `webarena_08_21_batch_600_easy/PROGRESS.md` | Batch 3 |
| `b3__FLAKY_REPORT.md` | `webarena_08_21_batch_600_easy/FLAKY_REPORT.md` | Batch 3 |
| `b4__TASK4.md` | `TASK4.md` | Batch 4 |
| `b5__BATCH5_CONTRACT.md` | `webarena_09_04_skills/BATCH5_CONTRACT.md` | Batch 5 |
| `b5__FINAL_REPORT.md` | `webarena_09_04_skills/FINAL_REPORT.md` | Batch 5 |
| `b5__CORRECTIONS.md` | `webarena_09_04_skills/CORRECTIONS.md` | Batch 5 |
| `b5__FLAKY_REPORT.md` | `webarena_09_04_skills/FLAKY_REPORT.md` | Batch 5 |
| `b6__BATCH6_CONTRACT.md` | `webarena_09_08_medium_600/BATCH6_CONTRACT.md  *(+1 identical copy)*` | Batch 6 |
| `b6__FINAL_REPORT.md` | `webarena_09_08_medium_600/FINAL_REPORT.md  *(+1 identical copy)*` | Batch 6 |
| `b6__CORRECTIONS.md` | `webarena_09_08_medium_600/CORRECTIONS.md` | Batch 6 |
| `b6__FLAKY_REPORT.md` | `webarena_09_08_medium_600/FLAKY_REPORT.md  *(+1 identical copy)*` | Batch 6 |
| `b6__CENSUS_ERRATA.md` | `webarena_09_08_medium_600/CENSUS_ERRATA.md  *(+1 identical copy)*` | Batch 6 |
| `b6map__CORRECTIONS.md` | `output/CORRECTIONS.md` | Batch 6 + map (shared findings log) |
| `map__TASK_MAP.md` | `TASK_MAP.md` | Map batches |
| `map400__FINAL_REPORT.md` | `output/map400/FINAL_REPORT.md` | Map batch 1 |
| `maphard__FINAL_REPORT.md` | `output/maphard/FINAL_REPORT.md` | Map batch 2 |

## Notes

* **Batch 4 (`webarena_09_02_hard`) has no run documents of its own.** Only its
  spec, `TASK4.md`, survives — there is no final report, no flaky report and no
  corrections log for those 600 tasks. That is a genuine gap in the record, not
  an omission here.
* `b6map__CORRECTIONS.md` is the superset: batch 6's corrections plus the six
  MAP-1..MAP-6 findings from the map batches. `b6__CORRECTIONS.md` is the batch-6
  snapshot alone. They are not duplicates of each other.
* Four batch-6 documents existed byte-identically in both `output/` and the
  snapshot; each was copied once and both origins are recorded above.
* `map__TASK_MAP.md` covers BOTH map batches. The batch directories themselves
  carry only their `FINAL_REPORT.md`.
* The `TASK*.md` series is tracked in git (commit `ab41bcd`) with deployment
  hosts replaced by placeholders; the copies here reflect that committed state.
  Everything else is untracked and exists only on this disk.
