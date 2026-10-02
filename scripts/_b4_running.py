#!/usr/bin/env python3
"""Refresh output/prior_inventory/_running_<site>.txt from what has landed.

Authoring lanes run concurrently, so a lane's prompt is written before its
siblings finish. These files are how a lane sees what landed after its own
prompt was composed, and are the only thing standing between two concurrent
lanes and a duplicate pair.

    python3 scripts/_b4_running.py
"""
import json
import pathlib

for site in ("gitlab", "reddit", "shopping", "shopping_admin"):
    root = pathlib.Path("output/tasks") / site
    lines = []
    for path in sorted(root.glob("*/task_instruction.json")):
        d = json.loads(path.read_text())
        meta = json.loads((path.parent / "task.json").read_text()).get("metadata") or {}
        lines.append(
            f"{d['task_id']} | {d.get('difficulty')} | {meta.get('style')} | "
            f"shape={meta.get('shape', '-')} | start={d.get('start_path')} | "
            f"{' '.join(str(d.get('task_instruction', '')).split())}"
        )
    out = pathlib.Path("output/prior_inventory") / f"_running_{site}.txt"
    out.write_text("\n".join(lines) + ("\n" if lines else ""))
    print(f"{site}: {len(lines)}")
