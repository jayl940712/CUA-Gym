#!/usr/bin/env python3
"""Compact batch-4 progress view. `_b4_status.py [lane ...]` or no args for all."""
import json, sys, pathlib, subprocess
plan = json.load(open("output/wave_plan.json"))
lanes = [int(a) for a in sys.argv[1:]] or range(len(plan))
started = 0
for i in lanes:
    l = plan[i]
    root = pathlib.Path("output/tasks")/l["site"]
    bundles = sorted(p.parent for p in root.glob(f"{l['slug']}_*/task.json"))
    if not bundles and len(list(lanes)) > 8:
        continue
    started += 1
    notes = root/"_batches"/l["slug"]/"GENERATION.md"
    reps = list((root/"_batches"/l["slug"]/"replays").glob("*.py")) if (root/"_batches"/l["slug"]/"replays").is_dir() else []
    rc = subprocess.run(["python3","scripts/check_lane_quota.py",str(i)],capture_output=True,text=True)
    ok = "OK " if rc.returncode == 0 else "..."
    print(f"{ok} lane {i:2d} {l['slug'][:42]:42s} {len(bundles):2d}/10 bundles  "
          f"{len(reps):2d} replays  notes={'y' if notes.is_file() else 'n'}")
print(f"\nlanes with output: {started}/{len(plan)}   "
      f"total bundles: {sum(1 for p in pathlib.Path('output/tasks').glob('*/*/task.json'))}/600")
