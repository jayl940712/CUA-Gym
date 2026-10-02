#!/usr/bin/env python3
"""Print a lane's authoritative assignment, for pasting into its prompt.

Exists because batch 4 shipped six lane prompts with "8 terse / 2 explicit"
hardcoded. The split is NOT uniform -- 30 lanes are 8T/2E and 30 are 7T/3E,
because 150 tasks per site at 75% terse is 112.5 and the remainder has to be
dealt across lanes. One lane caught the error itself by following the quota
checker; the others authored to the wrong split and needed a repair round.

Batch 5 adds the skill chain, which is the assignment that actually matters
now, and drops the difficulty quota, which no longer exists (difficulty is
derived from the chain and reported, not targeted).

Never type a lane's numbers by hand.

    python3 scripts/_b5_lane_facts.py 8 23 38
"""
import json
import sys
import pathlib
import textwrap

plan = json.loads(pathlib.Path("output/wave_plan.json").read_text())
for raw in sys.argv[1:]:
    i = int(raw)
    l = plan[i]
    print(f"lane {i}: {l['slug']} ({l['site']}, plan section {l['section']})")
    print(f"  skills     : {' -> '.join(l['skills'])}")
    print(f"  chain      : {l['chain']}")
    print(f"  entities   : {l['entities']}")
    print(f"  writeback  : {l['writeback']}")
    print(f"  tasks      : exactly {l['n']}")
    print(f"  style      : exactly {l['terse']} terse, {l['explicit']} explicit")
    print(f"  start_path : at least {l['root_min']} of {l['n']} at '/'")
    print(f"  shape      : at least {l['retrieval']} retrieval_writeback")
    print( "  difficulty : NOT a quota. Derived from each task's own chain --")
    print( "               2 skills = medium, 3+ with two retrievals or two")
    print( "               dependent actions = hard. Relabel down, never pad up.")
    print("  official analogues to cite verbatim in metadata:")
    for a in l["analogues"]:
        for line in textwrap.wrap(a, 92, initial_indent="    - ", subsequent_indent="      "):
            print(line)
    if l.get("notes"):
        print(f"  notes      : {l['notes']}")
    print()
