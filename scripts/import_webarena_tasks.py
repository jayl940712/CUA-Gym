#!/usr/bin/env python3
"""Import supported tasks from WebArena JSON or JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cua_gym_web.importer import discover_supported_mocks, import_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_file", help="Path to a WebArena JSON array or JSONL")
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "output" / "webarena_tasks"),
        help="Directory for normalized task manifests",
    )
    parser.add_argument(
        "--hub-root",
        default=str(PROJECT_ROOT / "hub"),
        help="CUA-Gym-Hub checkout used to discover supported webarena_* mocks",
    )
    parser.add_argument(
        "--id-prefix",
        default="webarena",
        help="Prefix for numeric task IDs, e.g. webarena or visualwebarena",
    )
    args = parser.parse_args()

    supported = discover_supported_mocks(args.hub_root)
    manifests = import_jsonl(
        args.task_file, args.output, supported, id_prefix=args.id_prefix
    )
    print(f"Imported {len(manifests)} tasks for {len(supported)} WebArena mocks")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
