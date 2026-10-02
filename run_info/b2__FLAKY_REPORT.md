# Flaky task report

Scanned 200 run directories: **200 consistent**, **0 flaky**, 0 with no attempts.

A task is flaky when its attempts disagree on the replay score, the
initial score, or the overall verdict. These ship as PASS today because
`task_is_complete()` only requires one passing attempt.

No disagreement found.
