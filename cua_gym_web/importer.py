"""Import the original WebArena JSONL into web-native task manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .compiler import evidence_requests, write_reward
from .models import AppSpec, WebTaskManifest, source_to_mock


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def discover_supported_mocks(hub_root: str | Path) -> set[str]:
    websites = Path(hub_root) / "websites"
    if not websites.is_dir():
        raise FileNotFoundError(f"Hub websites directory not found: {websites}")
    return {
        path.name
        for path in websites.glob("webarena_*_mock")
        if path.is_dir() and (path / "SCHEMA.md").is_file()
    }


def start_path_for(source_name: str, raw_urls: list[Any]) -> str:
    placeholder = f"__{source_name.upper()}__"
    for raw in raw_urls:
        if not isinstance(raw, str) or placeholder not in raw:
            continue
        path = raw.replace(placeholder, "", 1)
        return path if path.startswith("/") else f"/{path}" if path else "/"
    return "/"


def import_row(
    row: dict[str, Any],
    supported_mocks: set[str],
    source_file: str,
    id_prefix: str = "webarena",
) -> WebTaskManifest | None:
    source_names = [
        str(value)
        for value in as_list(row.get("web_name") or row.get("sites"))
        if value
    ]
    if not source_names:
        return None
    mock_names = [source_to_mock(source) for source in source_names]
    if any(mock not in supported_mocks for mock in mock_names):
        return None

    raw_urls = as_list(row.get("web") or row.get("start_url"))
    apps = tuple(
        AppSpec.for_source(source, start_path_for(source, raw_urls))
        for source in source_names
    )
    raw_task_id = row.get("id")
    if raw_task_id in (None, ""):
        raw_task_id = row.get("task_id")
        task_id = f"{id_prefix}-{raw_task_id}" if raw_task_id not in (None, "") else ""
    else:
        task_id = str(raw_task_id)
    instruction = str(
        row.get("ques")
        or row.get("question")
        or row.get("intent")
        or ""
    ).strip()
    if not task_id or not instruction:
        return None
    metadata = {
        "source_file": source_file,
        "source_web": row.get("web"),
        "source_web_name": row.get("web_name"),
        "source_sites": row.get("sites"),
        "source_start_url": row.get("start_url"),
        "require_reset": row.get("require_reset"),
        "intent_template_id": row.get("intent_template_id"),
    }
    return WebTaskManifest(
        task_id=task_id,
        instruction=instruction,
        apps=apps,
        source_evaluator=dict(row.get("eval") or {}),
        evidence=evidence_requests(dict(row.get("eval") or {})),
        source=id_prefix,
        metadata=metadata,
    )


def read_tasks(path: str | Path) -> Iterable[dict[str, Any]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = None
    if isinstance(value, list):
        for index, row in enumerate(value, 1):
            if not isinstance(row, dict):
                raise ValueError(f"{source}: item {index} is not a JSON object")
            yield row
        return
    if isinstance(value, dict):
        rows = value.get("tasks")
        if rows is None:
            yield value
            return
        if not isinstance(rows, list):
            raise ValueError(f"{source}: tasks must be an array")
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                raise ValueError(f"{source}: item {index} is not a JSON object")
            yield row
        return

    with source.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{source}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{source}:{line_number}: expected a JSON object")
            yield value


def import_jsonl(
    source: str | Path,
    output_dir: str | Path,
    supported_mocks: set[str],
    id_prefix: str = "webarena",
) -> list[WebTaskManifest]:
    source_path = Path(source)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    manifests: list[WebTaskManifest] = []
    skipped = 0
    skipped_by_reason: dict[str, int] = {}
    for row in read_tasks(source_path):
        eval_types = set((row.get("eval") or {}).get("eval_types") or [])
        unsupported = eval_types - {"url_match", "program_html"}
        if unsupported:
            if "string_match" in unsupported:
                reason = "answer-only task has no verifiable browser writeback"
            else:
                reason = "unsupported evaluator: " + ",".join(sorted(unsupported))
            skipped_by_reason[reason] = skipped_by_reason.get(reason, 0) + 1
            skipped += 1
            continue
        manifest = import_row(
            row, supported_mocks, str(source_path), id_prefix=id_prefix
        )
        if manifest is None:
            skipped_by_reason["unsupported site or invalid task"] = (
                skipped_by_reason.get("unsupported site or invalid task", 0) + 1
            )
            skipped += 1
            continue
        task_dir = destination / manifest.task_id
        manifest.write(task_dir / "task.json")
        write_reward(task_dir / manifest.reward_path, manifest.source_evaluator)
        manifests.append(manifest)

    index = {
        "schema_version": 2,
        "source": str(source_path),
        "task_count": len(manifests),
        "skipped_count": skipped,
        "skipped_by_reason": skipped_by_reason,
        "tasks": [
            {"task_id": task.task_id, "path": f"{task.task_id}/task.json"}
            for task in manifests
        ],
    }
    (destination / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifests
