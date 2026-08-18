"""Compile deterministic Classic WebArena URL/DOM checks into ``reward.py``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .reward import validate_reward_source

SUPPORTED_EVALUATORS = {"url_match", "program_html"}


def evidence_requests(evaluator: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "name": f"program_html_{index}",
            "index": index,
            "url": entry.get("url", "last"),
            "locator": entry.get("locator", ""),
            "prep_actions": entry.get("prep_actions", []),
        }
        for index, entry in enumerate(evaluator.get("program_html") or [])
        if isinstance(entry, dict)
    )


def validate_compilable_evaluator(evaluator: dict[str, Any]) -> None:
    eval_types = set(evaluator.get("eval_types") or [])
    unsupported = eval_types - SUPPORTED_EVALUATORS
    if unsupported:
        raise ValueError(
            "deterministic reward compiler does not support: "
            + ", ".join(sorted(unsupported))
        )


_REWARD_TEMPLATE = '''"""Generated deterministic reward for an imported WebArena task."""

import re
import urllib.parse


SPEC = __SPEC__


def _clean(value):
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    return text.casefold()


def _groups(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [[value]]
    groups = []
    for item in value:
        if isinstance(item, list):
            groups.append([str(part) for part in item])
        else:
            groups.append(str(item).split(" |OR| "))
    return groups


def _path(reference):
    value = re.sub(r"__[A-Z0-9_]+__", "", str(reference), count=1)
    parsed = urllib.parse.urlsplit(value)
    return urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))


def _route(url):
    parsed = urllib.parse.urlsplit(str(url))
    query = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if key != "sid"
    ]
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunsplit(("", "", path, urllib.parse.urlencode(sorted(query)), ""))


def _url_score(evidence):
    references = [
        part.strip()
        for candidate in (
            SPEC.get("reference_url")
            if isinstance(SPEC.get("reference_url"), list)
            else [SPEC.get("reference_url")]
        )
        for part in str(candidate or "").split(" |OR| ")
        if part.strip()
    ]
    candidates = [
        url
        for app in evidence.get("apps", {}).values()
        for url in app.get("final_urls", [])
    ]
    rule = SPEC.get("url_note", "GOLD in PRED")
    for reference in references:
        expected = _route(_path(reference))
        expected_parts = urllib.parse.urlsplit(expected)
        expected_query = urllib.parse.parse_qs(expected_parts.query)
        for candidate in candidates:
            actual = _route(candidate)
            actual_parts = urllib.parse.urlsplit(actual)
            if rule == "EXACT":
                matched = actual == expected
            else:
                actual_query = urllib.parse.parse_qs(actual_parts.query)
                matched = expected_parts.path in actual_parts.path and all(
                    any(
                        expected_value in actual_value
                        for expected_value in expected_values
                        for actual_value in actual_query.get(key, [])
                    )
                    for key, expected_values in expected_query.items()
                )
            if matched:
                return 1.0, {"expected": expected, "actual": actual}
    return 0.0, {"references": references, "candidates": candidates}


def _compare_numeric(actual, condition):
    match = re.fullmatch(r"\\s*(<=|>=|==|<|>)\\s*(-?\\d+(?:\\.\\d+)?)\\s*", condition)
    if not match:
        return False
    operator, expected = match.group(1), float(match.group(2))
    return {
        "<=": actual <= expected,
        ">=": actual >= expected,
        "==": abs(actual - expected) <= 1e-8,
        "<": actual < expected,
        ">": actual > expected,
    }[operator]


def _required_score(required, content):
    normalized = _clean(content)
    score = 1.0
    details = []
    for kind in ("must_include", "exact_match", "must_exclude"):
        for alternatives in _groups(required.get(kind)):
            if kind == "exact_match":
                passed = any(normalized == _clean(value) for value in alternatives)
            elif kind == "must_exclude":
                passed = all(_clean(value) not in normalized for value in alternatives)
            else:
                passed = any(_clean(value) in normalized for value in alternatives)
            score *= float(passed)
            details.append({"check": kind, "expected": alternatives, "passed": passed})
    for alternatives in _groups(required.get("required_values")):
        try:
            actual = float(str(content).replace(",", "").strip())
        except ValueError:
            passed = False
        else:
            passed = any(_compare_numeric(actual, value) for value in alternatives)
        score *= float(passed)
        details.append({"check": "required_values", "expected": alternatives, "passed": passed})
    return score if details else 0.0, details


def _program_html_score(evidence):
    observations = evidence.get("observations", [])
    score = 1.0
    details = []
    for index, target in enumerate(SPEC.get("program_html") or []):
        candidates = [
            item
            for item in observations
            if item.get("index") == index and not item.get("error")
        ]
        candidate_scores = [
            _required_score(target.get("required_contents") or {}, item.get("content", ""))
            for item in candidates
        ]
        best_score, best_details = max(candidate_scores, default=(0.0, []), key=lambda item: item[0])
        score *= best_score
        details.append({
            "target": index,
            "score": best_score,
            "checks": best_details,
            "observation_count": len(candidates),
        })
    return score, details


def evaluate(evidence):
    components = []
    final_score = 1.0
    eval_types = SPEC.get("eval_types") or []
    if "url_match" in eval_types:
        score, details = _url_score(evidence)
        final_score *= score
        components.append({"type": "url_match", "score": score, "details": details})
    if "program_html" in eval_types:
        score, details = _program_html_score(evidence)
        final_score *= score
        components.append({"type": "program_html", "score": score, "details": details})
    if not components:
        final_score = 0.0
    return {"score": final_score, "components": components}
'''


def render_reward(evaluator: dict[str, Any]) -> str:
    validate_compilable_evaluator(evaluator)
    source = _REWARD_TEMPLATE.replace(
        "__SPEC__", repr(json.loads(json.dumps(evaluator, ensure_ascii=False)))
    )
    validate_reward_source(source, "generated reward.py")
    return source


def write_reward(path: str | Path, evaluator: dict[str, Any]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_reward(evaluator), encoding="utf-8")
    return destination
