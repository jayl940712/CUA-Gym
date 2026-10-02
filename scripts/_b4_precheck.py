#!/usr/bin/env python3
"""Refuse to launch a lane that already has output (TASK4 batch-4 guard).

Added after a real incident: the Claude Code process restarted mid-launch, the
round was re-issued, and lanes 2/3/4 were each authored by TWO agents. Lane 4
ended with 20 bundles under one slug and genuine content collisions (two tasks
sharing subject and destination) -- 10 had to be withdrawn.

`preflight_bundles.py` cannot catch this: both sets are individually valid and
their task_ids differ, so nothing collides. Only the lane's *bundle count*
reveals it, which is why this check is by lane rather than by bundle.

    python3 scripts/_b4_precheck.py 2 3 4      # exit 1 if any already has output
"""
import json
import pathlib
import sys

plan = json.loads(pathlib.Path("output/wave_plan.json").read_text())

# A lane that was launched but whose agent has not yet written anything looks
# identical on disk to a lane that was never launched. That gap is exactly how
# lanes 2/3/4 got double-staffed, so the ledger is consulted first.
LEDGER = pathlib.Path("output/launched_lanes.json")
launched = set(json.loads(LEDGER.read_text())) if LEDGER.is_file() else set()

problems = 0
for raw in sys.argv[1:]:
    i = int(raw)
    lane = plan[i]
    root = pathlib.Path("output/tasks") / lane["site"]
    n = len(list(root.glob(f"{lane['slug']}_*/task.json")))
    if i in launched and not n:
        problems += 1
        print(f"REFUSE lane {i} {lane['slug']}: already LAUNCHED (in output/launched_lanes.json)")
        print("       but has written nothing yet — its agent is still reading.")
        print("       Re-launching would double-staff the lane. Wait, or resume that agent.")
    elif n:
        problems += 1
        print(f"REFUSE lane {i} {lane['slug']}: already has {n} bundle(s).")
        print("       Launching would create a second parallel set under one slug.")
        print("       If the previous agent died, resume it or repair in place —")
        print("       do not re-launch the lane from scratch.")
    else:
        print(f"ok     lane {i} {lane['slug']}: empty, safe to launch")
sys.exit(1 if problems else 0)
