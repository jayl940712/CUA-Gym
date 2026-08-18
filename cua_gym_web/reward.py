"""Restricted execution contract for deterministic web reward scripts."""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile
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
POPULAR_REQUIREMENTS = {
    "beautifulsoup4": {"bs4"},
    "jsonpath-ng": {"jsonpath_ng"},
    "lxml": {"lxml"},
    "networkx": {"networkx"},
    "numpy": {"numpy"},
    "pandas": {"pandas"},
    "pydantic": {"pydantic"},
    "python-dateutil": {"dateutil"},
    "scikit-learn": {"sklearn"},
    "scipy": {"scipy"},
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


def read_reward_requirements(path: str | Path | None) -> set[str]:
    """Return import roots declared by a small popular-package allowlist."""
    if path is None:
        return set()
    requirements_path = Path(path)
    if not requirements_path.is_file():
        raise RewardValidationError(
            f"declared requirements file does not exist: {requirements_path}"
        )
    import_roots: set[str] = set()
    for line_number, raw_line in enumerate(
        requirements_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-", "git+", "http://", "https://")):
            raise RewardValidationError(
                f"{requirements_path}:{line_number}: URLs and pip options are forbidden"
            )
        match = re.fullmatch(
            r"([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?"
            r"(?:\s*(?:==|>=|<=|~=|>|<|!=)\s*[A-Za-z0-9_.+!-]+)?",
            line,
        )
        if not match:
            raise RewardValidationError(
                f"{requirements_path}:{line_number}: invalid requirement {line!r}"
            )
        package = match.group(1).casefold().replace("_", "-")
        if package not in POPULAR_REQUIREMENTS:
            raise RewardValidationError(
                f"{requirements_path}:{line_number}: unsupported package {package!r}; "
                f"allowed: {', '.join(sorted(POPULAR_REQUIREMENTS))}"
            )
        import_roots.update(POPULAR_REQUIREMENTS[package])
    return import_roots


def validate_reward_source(
    source: str,
    path: str = "reward.py",
    allowed_third_party: set[str] | None = None,
) -> None:
    """Reject network, process, filesystem, and dynamic-code capabilities."""
    allowed_imports = ALLOWED_IMPORTS | (allowed_third_party or set())

    def import_allowed(module: str) -> bool:
        return any(
            module == allowed or module.startswith(f"{allowed}.")
            for allowed in allowed_imports
        )
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
                if not import_allowed(alias.name):
                    raise RewardValidationError(
                        f"{path} imports forbidden module {alias.name!r}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if not import_allowed(module):
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
        self,
        reward_path: str | Path,
        evidence: dict[str, Any],
        requirements_path: str | Path | None = None,
    ) -> EvaluationResult:
        path = Path(reward_path).resolve()
        requirements = (
            Path(requirements_path).resolve() if requirements_path is not None else None
        )
        allowed_third_party = read_reward_requirements(requirements)
        source = path.read_text(encoding="utf-8")
        validate_reward_source(source, str(path), allowed_third_party)
        missing = sorted(
            module
            for module in allowed_third_party
            if importlib.util.find_spec(module) is None
        )
        if missing:
            raise RewardExecutionError(
                f"reward dependencies are not installed: {', '.join(missing)}. "
                f"Install them with: python3 -m pip install -r {requirements}"
            )
        return await asyncio.to_thread(self._run, path, evidence)

    def _run(
        self, reward_path: Path, evidence: dict[str, Any]
    ) -> EvaluationResult:
        environment = {
            "HOME": os.environ.get("HOME", ""),
            "PATH": os.environ.get("PATH", ""),
            "PYTHONHASHSEED": "0",
            "PYTHONIOENCODING": "utf-8",
        }
        try:
            with tempfile.TemporaryDirectory(prefix="cua-reward-") as scratch:
                process = subprocess.run(
                    [sys.executable, "-c", _WRAPPER, str(reward_path)],
                    input=json.dumps(evidence, ensure_ascii=False),
                    text=True,
                    capture_output=True,
                    timeout=self.timeout_seconds,
                    env=environment,
                    cwd=scratch,
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
        memory = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
