#!/usr/bin/env python3
"""Sample diverse WebArena questions as inspiration for new RL tasks."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "webarena_benchmarks" / "webarena.jsonl"
SUPPORTED_SITES = {
    "classifieds",
    "gitlab",
    "reddit",
    "shopping",
    "shopping_admin",
}


def read_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if isinstance(value, dict):
                rows.append(value)
    return rows


def sample_rows(
    rows: list[dict[str, Any]],
    *,
    count: int,
    sites: set[str],
    eval_types: set[str],
    keyword: str,
    seed: int,
) -> list[dict[str, Any]]:
    keyword = keyword.casefold()
    candidates = []
    for row in rows:
        row_sites = {str(site) for site in row.get("web_name") or []}
        row_types = {str(kind) for kind in (row.get("eval") or {}).get("eval_types") or []}
        question = str(row.get("ques") or "")
        if not row_sites or not row_sites <= SUPPORTED_SITES:
            continue
        if sites and not row_sites & sites:
            continue
        if eval_types and not row_types & eval_types:
            continue
        if keyword and keyword not in question.casefold():
            continue
        candidates.append(row)

    rng = random.Random(seed)
    buckets: dict[tuple[tuple[str, ...], tuple[str, ...]], deque[dict[str, Any]]] = {}
    grouped: dict[tuple[tuple[str, ...], tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        key = (
            tuple(sorted(str(site) for site in row.get("web_name") or [])),
            tuple(sorted(str(kind) for kind in (row.get("eval") or {}).get("eval_types") or [])),
        )
        grouped[key].append(row)
    for key, values in grouped.items():
        rng.shuffle(values)
        buckets[key] = deque(values)

    selected = []
    keys = sorted(buckets)
    while keys and len(selected) < count:
        next_keys = []
        for key in keys:
            if buckets[key] and len(selected) < count:
                selected.append(buckets[key].popleft())
            if buckets[key]:
                next_keys.append(key)
        keys = next_keys
    return selected


def summarize(row: dict[str, Any]) -> dict[str, Any]:
    evaluator = row.get("eval") or {}
    eval_types = list(evaluator.get("eval_types") or [])
    return {
        "source_id": row.get("id"),
        "sites": row.get("web_name") or [],
        "question": row.get("ques") or "",
        "evaluator_types": eval_types,
        "requires_observable_writeback": "string_match" in eval_types,
        "has_dom_assertions": bool(evaluator.get("program_html")),
        "has_url_assertion": bool(evaluator.get("reference_url")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--site", action="append", default=[])
    parser.add_argument("--eval-type", action="append", default=[])
    parser.add_argument("--keyword", default="")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    selected = sample_rows(
        read_rows(args.source),
        count=max(0, args.count),
        sites=set(args.site),
        eval_types=set(args.eval_type),
        keyword=args.keyword,
        seed=args.seed,
    )
    result = {
        "source": str(Path(args.source)),
        "count": len(selected),
        "examples": [summarize(row) for row in selected],
    }
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
