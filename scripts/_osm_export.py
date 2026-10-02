#!/usr/bin/env python3
"""Export verified map bundles as NeMo-Gym rollout rows (JSONL).

Same row shape as scripts/export_nemo_rollouts.py -- see docs/NEMO_JSONL_FORMAT.md
-- with two differences forced by the site rather than chosen:

  * `cuagym.external_base_url` is set. The OpenStreetMap deployment is not a hub
    mock, so it has no entry in hub_apps.APP_DIRS and no consecutive port to
    resolve; browser_worker.reset() opens this URL directly instead.
  * `eval_reward_code` carries no `__CUA_GYM_SID__` placeholder. There is no sid
    to scope: the site has no per-session state, which is the whole reason these
    tasks are scored from the reported answer and the final URL.

Only bundles that actually verified against the live site are exported, read
from the verification report that scripts/_osm_verify.py writes.

    python3 scripts/_osm_export.py output/map400 \
        --report output/map400/runs/report_attempt-1.json \
        --output webarena_map_400.jsonl
"""
from __future__ import annotations

import argparse
import json
import pathlib

AGENT_REF = {"type": "responses_api_agents", "name": "cuagym_agent"}
CONTRACT_VERSION = 2
EVAL_STUB = {"eval_types": ["string_match"], "reference_answers": None,
             "note": "unused - CUA-Gym reward code is authoritative"}
SITE_URL = "http://18.116.12.228:3000"


def payload_for(bundle: pathlib.Path) -> dict:
    manifest = json.loads((bundle / "task.json").read_text(encoding="utf-8"))
    app = manifest["apps"][0]
    reward_code = (bundle / "nemo_reward.py").read_text(encoding="utf-8")
    start_path = app.get("start_path") or "/"
    return {
        "task_id": manifest["task_id"],
        "dataset": "cuagym",
        "dataset_version": "v1",
        "sites": [app["name"]],
        # Parallel to `sites`, and a PATH rather than an absolute URL, exactly as
        # the hub batches emit it. "" means "this app's default location".
        "start_urls": ["" if start_path == "/" else start_path],
        "intent": manifest["instruction"],
        "eval": dict(EVAL_STUB),
        "cuagym": {
            "bundle_id": manifest["task_id"],
            "app_dir": app["name"],
            "external_base_url": SITE_URL,
            "initial_setup": None,
            "eval_reward_code": reward_code,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("batch")
    ap.add_argument("--report", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--tasks-subdir", default="tasks/map")
    args = ap.parse_args()

    batch = pathlib.Path(args.batch)
    verified = {r["task"] for r in json.loads(pathlib.Path(args.report).read_text())
                if r["state"] == "pass"}

    rows, skipped = [], []
    for bundle in sorted(p.parent for p in
                         (batch / args.tasks_subdir).glob("*/task.json")):
        if bundle.name not in verified:
            skipped.append(bundle.name)
            continue
        payload = payload_for(bundle)
        task_id = payload["task_id"]
        # Written into the bundle from the same object that goes into the JSONL,
        # so the two cannot drift -- four batch-6 bundles shipped an inlined copy
        # that had gone stale against the on-disk reward.
        (bundle / "nemo_task.json").write_text(
            json.dumps({"task_payload": payload}, indent=1) + "\n", encoding="utf-8")
        rows.append({
            "responses_create_params": {
                "input": [{"role": "user", "content": payload["intent"]}],
                "parallel_tool_calls": False,
            },
            "verifier_metadata": {"task": json.loads(json.dumps(payload))},
            "task_payload": payload,
            "agent_ref": dict(AGENT_REF),
            "context_compaction_contract_version": CONTRACT_VERSION,
            "context_compaction_group_id": f"cuagym-{task_id}",
            "context_compaction_task_id": task_id,
            "context_compaction_rollout_index": 0,
            "context_compaction_attempt_index": 0,
        })

    out = pathlib.Path(args.output)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                   encoding="utf-8")
    print(f"{len(rows)} rows -> {out}")
    if skipped:
        print(f"{len(skipped)} bundles were not exported (not verified): "
              + ", ".join(skipped[:10]) + ("..." if len(skipped) > 10 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
