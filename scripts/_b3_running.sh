#!/bin/bash
# Regenerate the running batch-3 inventory for a site, for pasting into author prompts.
site="$1"
out="output/prior_inventory/_batch3_running_${site}.txt"
python3 - "$site" "$out" <<'PY'
import json, glob, sys
site, out = sys.argv[1], sys.argv[2]
lines=[]
for f in sorted(glob.glob(f'output/tasks/{site}/*/task_instruction.json')):
    d=json.load(open(f))
    lines.append(f"{d['task_id']} | {d['difficulty']} | {d['task_instruction']}")
open(out,'w').write(('\n'.join(lines)+'\n') if lines else '(no batch-3 bundles accepted for this site yet)\n')
print(f"{out}: {len(lines)} bundles")
PY
