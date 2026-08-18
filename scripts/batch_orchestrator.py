#!/usr/bin/env python3
"""Run normalized WebArena tasks through the browser-only orchestrator."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATUS_FILE = PROJECT_ROOT / "output" / "batch_status.json"
LOG_DIR = PROJECT_ROOT / "output" / "logs"
DEFAULT_RUN_DIR = PROJECT_ROOT / "output" / "runs"


def load_env(path: Path = PROJECT_ROOT / ".env") -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.removeprefix("export ")
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ[key.strip()] = value.strip().strip("'\"")


def load_status() -> dict[str, Any]:
    if not STATUS_FILE.is_file():
        return {}
    return json.loads(STATUS_FILE.read_text(encoding="utf-8"))


def save_status(status: dict[str, Any]) -> None:
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATUS_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(STATUS_FILE)


def task_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw).resolve()
        if path.is_dir():
            paths.extend(sorted(path.glob("*/task.json")))
            continue
        if path.name == "index.json":
            index = json.loads(path.read_text(encoding="utf-8"))
            paths.extend(path.parent / entry["path"] for entry in index.get("tasks", []))
            continue
        paths.append(path)
    unique = list(dict.fromkeys(paths))
    for path in unique:
        if not path.is_file():
            raise FileNotFoundError(f"task manifest not found: {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("schema_version") != 2 or not value.get("apps"):
            raise ValueError(f"not a web-native task manifest: {path}")
        reward = path.parent / value.get("reward_path", "reward.py")
        if not reward.is_file():
            raise FileNotFoundError(f"reward.py not found for {path}: {reward}")
        if value.get("requirements_path"):
            requirements = path.parent / value["requirements_path"]
            if not requirements.is_file():
                raise FileNotFoundError(
                    f"requirements file not found for {path}: {requirements}"
                )
    return unique


def passing_verification(run_dir: Path) -> Path | None:
    for path in sorted(run_dir.glob("**/verification.json"), reverse=True):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if value.get("verification", {}).get("passed") is True:
            return path
    return None


def task_is_complete(run_dir: Path) -> bool:
    if passing_verification(run_dir) is None:
        return False
    return any(
        "## Verdict: PASS" in path.read_text(errors="ignore")
        for path in run_dir.glob("**/REVIEW.md")
    )


async def run_task(
    task_path: Path,
    semaphore: asyncio.Semaphore,
    status: dict[str, Any],
    args: argparse.Namespace,
) -> str:
    task = json.loads(task_path.read_text(encoding="utf-8"))
    task_id = str(task["task_id"])
    run_dir = Path(args.output).resolve() / task_id
    if task_is_complete(run_dir) and not args.force:
        return "skipped"

    async with semaphore:
        started = datetime.now()
        status[task_id] = {
            "status": "running",
            "task": str(task_path),
            "apps": [app["name"] for app in task["apps"]],
            "started_at": started.isoformat(),
        }
        save_status(status)
        print(f"[{started:%H:%M:%S}] START {task_id}", flush=True)

        if args.dry_run:
            status[task_id]["status"] = "dry_run"
            save_status(status)
            return "dry_run"

        run_dir.mkdir(parents=True, exist_ok=True)
        prompt = (
            "Validate this imported WebArena task with the browser-only pipeline.\n\n"
            f"Task manifest: {task_path}\n"
            f"Endpoint registry: {Path(args.endpoints).resolve() if args.endpoints else '(environment variables)'}\n"
            f"Output directory: {run_dir}\n"
            f"Session mode: {args.mode}\n\n"
            "Execute the complete workflow from .claude/agents/web-orchestrator.md. "
            "Do not create VMs and do not ask clarifying questions."
        )
        command = [
            "claude",
            "--agent",
            "orchestrator",
            "-p",
            prompt,
            "--max-turns",
            str(args.max_turns),
            "--output-format",
            "stream-json",
            "--verbose",
            "--allowedTools",
            "Agent,Bash,Read,Write,Edit,Glob,Grep",
        ]
        if args.model:
            command.extend(["--model", args.model])
        if args.dangerously_skip_permissions:
            command.extend(["--permission-mode", "dontAsk"])

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOG_DIR / f"{task_id}.jsonl"
        error_path = LOG_DIR / f"{task_id}.stderr.log"
        result = "failed"
        try:
            with log_path.open("w") as log, error_path.open("w") as error:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=log,
                    stderr=error,
                    cwd=PROJECT_ROOT,
                )
                try:
                    await asyncio.wait_for(process.wait(), timeout=args.timeout * 60)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    result = "timeout"
                else:
                    result = "completed" if task_is_complete(run_dir) else "failed"
                    status[task_id]["exit_code"] = process.returncode
        except Exception as exc:
            result = "error"
            status[task_id]["error"] = str(exc)

        finished = datetime.now()
        status[task_id].update(
            {
                "status": result,
                "finished_at": finished.isoformat(),
                "duration_seconds": round((finished - started).total_seconds()),
            }
        )
        save_status(status)
        print(f"[{finished:%H:%M:%S}] {result.upper():9s} {task_id}", flush=True)
        return result


async def async_main(args: argparse.Namespace) -> int:
    load_env()
    paths = task_paths(args.inputs)
    if args.task_id:
        paths = [
            path
            for path in paths
            if json.loads(path.read_text(encoding="utf-8"))["task_id"] == args.task_id
        ]
    if not paths:
        print("No matching WebArena task manifests.")
        return 0
    status = load_status()
    semaphore = asyncio.Semaphore(args.concurrency)
    results = await asyncio.gather(
        *(run_task(path, semaphore, status, args) for path in paths)
    )
    counts = Counter(results)
    print(
        "BATCH COMPLETE "
        + " ".join(f"{name}={count}" for name, count in sorted(counts.items()))
    )
    return 1 if any(name in counts for name in ("failed", "error", "timeout")) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        nargs="+",
        help="task.json, index.json, or normalized task directory",
    )
    parser.add_argument("--endpoints", help="Endpoint registry JSON")
    parser.add_argument("--output", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--mode", choices=("legacy", "hardened"), default="legacy")
    parser.add_argument("--task-id")
    parser.add_argument("-c", "--concurrency", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=90, help="Minutes per task")
    parser.add_argument("--max-turns", type=int, default=120)
    parser.add_argument("--model")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--dangerously-skip-permissions", action="store_true")
    return asyncio.run(async_main(parser.parse_args()))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda _sig, _frame: sys.exit(130))
    raise SystemExit(main())
