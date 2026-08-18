#!/usr/bin/env python3
"""Run one normalized WebArena task through isolated Playwright lanes."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cua_gym_web.models import WebTaskManifest  # noqa: E402
from cua_gym_web.registry import EndpointRegistry  # noqa: E402
from cua_gym_web.runner import WebTaskRunner, load_replay  # noqa: E402
from cua_gym_web.state import SessionMode  # noqa: E402


async def run(args: argparse.Namespace) -> int:
    task_path = Path(args.task).resolve()
    task = WebTaskManifest.read(task_path)
    registry = EndpointRegistry.from_sources(args.endpoints)
    replay = load_replay(args.replay) if args.replay else None
    mode = SessionMode(args.mode)
    admin_token = args.admin_token or os.getenv("CUA_GYM_ADMIN_TOKEN")
    output = (
        Path(args.output)
        if args.output
        else PROJECT_ROOT / "output" / "runs" / task.task_id
    )
    runner = WebTaskRunner(
        task,
        registry,
        task_dir=task_path.parent,
        output_dir=output,
        mode=mode,
        admin_token=admin_token,
        headless=not args.headed,
        browser_executable=args.browser_executable,
    )
    report = await runner.run(replay)
    print(json.dumps(report["verification"], indent=2))
    print(f"Artifacts: {output}")
    return 0 if report["verification"]["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", help="Path to normalized task.json")
    parser.add_argument(
        "--endpoints",
        help="Optional JSON mapping mock names or CUA_GYM_*_URL keys to base URLs",
    )
    parser.add_argument(
        "--replay",
        help="Python module defining async run(lane, task) for known-correct UI actions",
    )
    parser.add_argument("--output", help="Run artifact directory")
    parser.add_argument(
        "--mode", choices=("legacy", "hardened"), default="legacy"
    )
    parser.add_argument("--admin-token", help="Admin token for hardened mode")
    parser.add_argument("--headed", action="store_true", help="Show Chromium")
    parser.add_argument("--browser-executable")
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
