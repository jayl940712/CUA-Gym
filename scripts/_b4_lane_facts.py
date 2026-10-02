#!/usr/bin/env python3
"""Print a lane's authoritative quota, for pasting into its prompt.

Added after I hardcoded "8 terse / 2 explicit" into six lane prompts. The split
is NOT uniform: 30 lanes are 8T/2E and 30 are 7T/3E, because 150 tasks per site
at 75% terse is 112.5 and the remainder has to be dealt across lanes. Lane 37
caught the error itself and followed `check_lane_quota.py`, which was right, but
an agent that trusts the prompt instead fails its quota and needs a repair round.

Never type a lane's numbers by hand again — read them from here.

    python3 scripts/_b4_lane_facts.py 8 23 38
"""
import json
import sys
import pathlib

plan = json.loads(pathlib.Path("output/wave_plan.json").read_text())
for raw in sys.argv[1:]:
    i = int(raw)
    l = plan[i]
    print(f"lane {i}: {l['slug']} ({l['site']}, plan section {l['section']})")
    print(f"  difficulty : exactly {l['medium']} medium, {l['hard']} hard, 0 easy")
    print(f"  style      : exactly {l['terse']} terse, {l['explicit']} explicit")
    print(f"  start_path : at least {l['root_min']} of {l['n']} at '/'")
    print(f"  shape      : exactly {l['retrieval']} retrieval_writeback")
