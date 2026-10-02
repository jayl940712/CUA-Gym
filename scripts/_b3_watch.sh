#!/bin/bash
# Wake the coordinator when the batch finishes, or early if a systemic failure appears.
# Systemic = 3+ tasks in a non-completed terminal state.
cd /home/ubuntu/CUA-Gym
while true; do
  if ! pgrep -f batch_orchestrator.py >/dev/null 2>&1; then
    echo "REASON=batch_exited"
    break
  fi
  bad=$(python3 - <<'PY' 2>/dev/null
import json,os,collections
p='output/batch_status.json'
if os.path.exists(p):
    d=json.load(open(p)); t=d.get('tasks',d)
    c=collections.Counter(v.get('status') for v in t.values() if isinstance(v,dict))
    print(sum(v for k,v in c.items() if k in ('failed','timeout','error')))
else: print(0)
PY
)
  if [ "${bad:-0}" -ge 3 ]; then
    echo "REASON=systemic_failures bad=$bad"
    break
  fi
  sleep 120
done
echo "=== final status ==="
python3 - <<'PY'
import json,os,collections
p='output/batch_status.json'
d=json.load(open(p)); t=d.get('tasks',d)
c=collections.Counter(v.get('status') for v in t.values() if isinstance(v,dict))
print("tracked:",len(t),dict(c))
bad=[k for k,v in t.items() if isinstance(v,dict) and v.get('status') not in ('completed','dry_run','running')]
for k in bad[:20]: print("  NOT COMPLETED:",k,t[k].get('status'),t[k].get('exit_code'))
PY
tail -2 output/batch_run.log
