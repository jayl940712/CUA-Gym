# Flaky task report

Scanned 200 run directories: **199 consistent**, **1 flaky**, 0 with no attempts.

A task is flaky when its attempts disagree on the replay score, the
initial score, or the overall verdict. These ship as PASS today because
`task_is_complete()` only requires one passing attempt.

## shopping_wishlist_compare_direct_add_url_006

replay scores: {1.0: 5, 0.0: 1} over 6 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.0 | 1.0 | yes | 0 |
| attempt-2 | 0.0 | 1.0 | yes | 0 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |
| attempt-4 | 0.0 | 0.0 | **no** | 0 |
| attempt-5 | 0.0 | 1.0 | yes | 0 |
| attempt-6 | 0.0 | 1.0 | yes | 0 |
