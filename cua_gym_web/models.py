"""Versioned manifests for WebArena tasks and browser runs."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
MOCK_RE = re.compile(r"^webarena_[A-Za-z0-9_-]+_mock$")
SID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def source_to_mock(source_name: str) -> str:
    """Convert a WebArena ``web_name`` into its Hub mock directory name."""
    normalized = source_name.strip().lower().replace("-", "_")
    if not normalized:
        raise ValueError("WebArena site name cannot be empty")
    return f"webarena_{normalized}_mock"


def endpoint_env_name(mock_name: str) -> str:
    if not MOCK_RE.fullmatch(mock_name):
        raise ValueError(f"invalid WebArena mock name: {mock_name!r}")
    stem = mock_name.removeprefix("webarena_").removesuffix("_mock").upper()
    return f"CUA_GYM_WEBARENA_{stem}_URL"


@dataclass(frozen=True)
class AppSpec:
    """One WebArena mock participating in a task."""

    name: str
    source_name: str
    base_url_env: str
    start_path: str = "/"
    initial_state: str | None = None
    golden_state: str | None = None

    def __post_init__(self) -> None:
        if not MOCK_RE.fullmatch(self.name):
            raise ValueError(f"invalid WebArena mock name: {self.name!r}")
        if not self.start_path.startswith("/"):
            raise ValueError(f"start_path must begin with '/': {self.start_path!r}")

    @classmethod
    def for_source(cls, source_name: str, start_path: str = "/") -> "AppSpec":
        name = source_to_mock(source_name)
        return cls(
            name=name,
            source_name=source_name,
            base_url_env=endpoint_env_name(name),
            start_path=start_path or "/",
        )


@dataclass(frozen=True)
class WebTaskManifest:
    """Portable, deployment-independent representation of a WebArena task."""

    task_id: str
    instruction: str
    apps: tuple[AppSpec, ...]
    source_evaluator: dict[str, Any] = field(default_factory=dict)
    reward_path: str = "reward.py"
    requirements_path: str | None = None
    evidence: tuple[dict[str, Any], ...] = ()
    schema_version: int = SCHEMA_VERSION
    source: str = "webarena"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"unsupported schema_version {self.schema_version}; expected {SCHEMA_VERSION}"
            )
        if not self.task_id.strip():
            raise ValueError("task_id cannot be empty")
        if not self.instruction.strip():
            raise ValueError("instruction cannot be empty")
        if not self.apps:
            raise ValueError("a WebArena task must reference at least one app")
        if Path(self.reward_path).is_absolute() or ".." in Path(self.reward_path).parts:
            raise ValueError("reward_path must stay inside the task bundle")
        if self.requirements_path and (
            Path(self.requirements_path).is_absolute()
            or ".." in Path(self.requirements_path).parts
        ):
            raise ValueError("requirements_path must stay inside the task bundle")
        names = [app.name for app in self.apps]
        if len(names) != len(set(names)):
            raise ValueError(f"task contains duplicate apps: {names}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WebTaskManifest":
        apps = tuple(AppSpec(**app) for app in value.get("apps", []))
        return cls(
            schema_version=value.get("schema_version", SCHEMA_VERSION),
            task_id=str(value["task_id"]),
            instruction=str(value["instruction"]),
            apps=apps,
            source_evaluator=dict(
                value.get("source_evaluator") or value.get("evaluator") or {}
            ),
            reward_path=str(value.get("reward_path") or "reward.py"),
            requirements_path=(
                str(value["requirements_path"])
                if value.get("requirements_path")
                else None
            ),
            evidence=tuple(
                dict(item) for item in value.get("evidence", []) if isinstance(item, dict)
            ),
            source=str(value.get("source") or "webarena"),
            metadata=dict(value.get("metadata") or {}),
        )

    @classmethod
    def read(cls, path: str | Path) -> "WebTaskManifest":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


@dataclass(frozen=True)
class Lane:
    """A browser/backend isolation lane within one task run."""

    name: str
    sid: str

    def __post_init__(self) -> None:
        if self.name not in {"initial", "oracle", "replay", "rollout"}:
            raise ValueError(f"unknown lane: {self.name!r}")
        if not SID_RE.fullmatch(self.sid):
            raise ValueError(f"invalid SID: {self.sid!r}")


@dataclass
class EvaluationResult:
    """Progressive result returned by deterministic ``reward.py``."""

    score: float
    components: list[dict[str, Any]]

    def __post_init__(self) -> None:
        self.score = max(0.0, min(1.0, float(self.score)))

    @property
    def passed(self) -> bool:
        return self.score == 1.0

    def to_dict(self) -> dict[str, Any]:
        return {"score": self.score, "passed": self.passed, "components": self.components}
