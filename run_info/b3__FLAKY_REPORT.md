# Flaky task report

Scanned 600 run directories: **598 consistent**, **1 flaky**, 1 with no attempts.

A task is flaky when its attempts disagree on the replay score, the
initial score, or the overall verdict. These ship as PASS today because
`task_is_complete()` only requires one passing attempt.

## shopping_duplicate_add_merge_wishlist_resave_keeps_row_003_v2

replay scores: {0.6: 1, 1.0: 3} over 4 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-2 | 0.0 | 0.6 | **no** | 0 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |
| attempt-4 | 0.0 | 1.0 | yes | 0 |
| attempt-5 | 0.0 | 1.0 | yes | 0 |
