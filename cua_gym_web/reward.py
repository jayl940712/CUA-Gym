"""Restricted execution contract for deterministic web reward scripts."""

from __future__ import annotations

import ast
import asyncio
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .models import EvaluationResult

ALLOWED_IMPORTS = {
    "collections",
    "datetime",
    "decimal",
    "fractions",
    "json",
    "math",
    "re",
    "statistics",
    "urllib.parse",
}
FORBIDDEN_CALLS = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "globals",
    "input",
    "locals",
    "open",
}
FORBIDDEN_ATTRIBUTES = {
    "connect",
    "open",
    "popen",
    "remove",
    "rename",
    "request",
    "rmdir",
    "system",
    "unlink",
    "urlopen",
    "write_bytes",
    "write_text",
}
RESULT_PREFIX = "__CUA_REWARD__"


class RewardValidationError(ValueError):
    pass


class RewardExecutionError(RuntimeError):
    pass


def validate_reward_source(source: str, path: str = "reward.py") -> None:
    """Reject network, process, filesystem, and dynamic-code capabilities."""
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise RewardValidationError(f"{path} is not valid Python: {exc}") from exc

    has_evaluate = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_evaluate |= node.name == "evaluate"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_IMPORTS:
                    raise RewardValidationError(
                        f"{path} imports forbidden module {alias.name!r}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module not in ALLOWED_IMPORTS:
                raise RewardValidationError(
                    f"{path} imports from forbidden module {module!r}"
                )
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                raise RewardValidationError(
                    f"{path} calls forbidden function {node.func.id!r}"
                )
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in FORBIDDEN_ATTRIBUTES
            ):
                raise RewardValidationError(
                    f"{path} calls forbidden attribute {node.func.attr!r}"
                )
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise RewardValidationError(
                f"{path} accesses forbidden dunder attribute {node.attr!r}"
            )
        elif isinstance(node, ast.Name) and node.id.startswith("__"):
            raise RewardValidationError(
                f"{path} accesses forbidden dunder name {node.id!r}"
            )
    if not has_evaluate:
        raise RewardValidationError(f"{path} must define evaluate(evidence)")


_WRAPPER = r"""
import importlib.util
import inspect
import json
import sys

reward_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("_cua_task_reward", reward_path)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load reward module")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
evidence = json.loads(sys.stdin.read())
result = module.evaluate(evidence)
if inspect.isawaitable(result):
    raise TypeError("reward evaluate() must be synchronous")
if isinstance(result, (int, float)):
    result = {"score": float(result), "components": []}
if not isinstance(result, dict):
    raise TypeError("reward evaluate() must return float or dict")
print("__CUA_REWARD__" + json.dumps(result, ensure_ascii=False))
"""


class PythonRewardRunner:
    """Execute trusted generated rewards with a narrow static capability policy."""

    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    async def evaluate(
        self, reward_path: str | Path, evidence: dict[str, Any]
    ) -> EvaluationResult:
        path = Path(reward_path).resolve()
        source = path.read_text(encoding="utf-8")
        validate_reward_source(source, str(path))
        return await asyncio.to_thread(self._run, path, evidence)

    def _run(
        self, reward_path: Path, evidence: dict[str, Any]
    ) -> EvaluationResult:
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8",
        }
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-c", _WRAPPER, str(reward_path)],
                input=json.dumps(evidence, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                env=environment,
                cwd=reward_path.parent,
                check=False,
                preexec_fn=self._resource_limits if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired as exc:
            raise RewardExecutionError(
                f"{reward_path} exceeded {self.timeout_seconds:.1f}s"
            ) from exc
        if process.returncode:
            raise RewardExecutionError(
                f"{reward_path} failed with exit {process.returncode}: "
                f"{process.stderr[-2000:]}"
            )
        result_line = next(
            (
                line.removeprefix(RESULT_PREFIX)
                for line in reversed(process.stdout.splitlines())
                if line.startswith(RESULT_PREFIX)
            ),
            None,
        )
        if result_line is None:
            raise RewardExecutionError(f"{reward_path} produced no reward result")
        try:
            value = json.loads(result_line)
            score = float(value["score"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise RewardExecutionError(
                f"{reward_path} returned an invalid reward object"
            ) from exc
        if not 0.0 <= score <= 1.0:
            raise RewardExecutionError(
                f"{reward_path} returned score outside [0, 1]: {score}"
            )
        components = value.get("components") or value.get("details") or []
        if not isinstance(components, list):
            components = [{"details": str(components)}]
        return EvaluationResult(score=score, components=components)

    def _resource_limits(self) -> None:
        import resource

        cpu_seconds = max(1, math.ceil(self.timeout_seconds))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        memory = 256 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
