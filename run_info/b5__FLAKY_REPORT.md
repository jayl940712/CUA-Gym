# Flaky task report

Scanned 613 run directories: **597 consistent**, **5 flaky**, 11 with no attempts.

A task is flaky when its attempts disagree on the replay score, the
initial score, or the overall verdict. These ship as PASS today because
`task_is_complete()` only requires one passing attempt.

## contributor_honour_roll_008

replay scores: {None: 1, 1.0: 2} over 3 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.0 | None | yes | 0 |
| attempt-2 | 0.0 | 1.0 | yes | 0 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |

## find_mr_by_phrase_comment_005

replay scores: {1.0: 4, 0.0: 1} over 5 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.0 | 1.0 | yes | 0 |
| attempt-2 | 0.0 | 1.0 | yes | 0 |
| attempt-3 | 0.0 | 0.0 | **no** | 0 |
| attempt-4 | 0.0 | 1.0 | yes | 0 |
| attempt-5 | 0.0 | 1.0 | yes | 0 |

## find_mr_by_phrase_comment_009

replay scores: {0.0: 1, 1.0: 2} over 3 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.0 | 0.0 | **no** | 0 |
| attempt-2 | 0.0 | 1.0 | yes | 0 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |

## grant_access_top_repos_008

replay scores: {1.0: 3} over 3 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.15 | 1.0 | **no** | 0 |
| attempt-2 | 0.0 | 1.0 | yes | 0 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |

## template_project_staffed_004

replay scores: {1.0: 4} over 4 attempts

| attempt | initial | replay | passed | browser errors |
|---|---|---|---|---|
| attempt-1 | 0.0 | 1.0 | **no** | 2 |
| attempt-2 | 0.0 | 1.0 | **no** | 2 |
| attempt-3 | 0.0 | 1.0 | yes | 0 |
| attempt-4 | 0.0 | 1.0 | yes | 0 |
