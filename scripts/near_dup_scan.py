#!/usr/bin/env python3
"""Triage near-duplicates between a new task batch and an already-shipped one.

Token overlap is a *triage signal*, not a verdict: it surfaces candidate pairs
cheaply so a human (or the orchestrating agent) can read each flagged pair
against the four duplicate tests in TASK2.md 2b and record a judgement. It
never rejects a bundle on its own.

    python3 scripts/near_dup_scan.py \
        --new output/tasks/gitlab \
        --prior webarena_08_18_batch_200/tasks/gitlab \
        --threshold 0.45
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Words that carry no discriminating signal: they appear in nearly every
# instruction on these mocks, so counting them inflates every pair alike.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "into", "is", "it", "its", "must", "my", "of", "on", "one",
    "or", "so", "that", "the", "then", "there", "this", "to", "two", "up",
    "want", "was", "with", "you", "your", "i", "me", "we", "us", "do", "does",
    "not", "no", "new", "page", "open", "go", "click", "use", "using", "make",
    "sure", "should", "will", "when", "after", "before", "each", "all", "any",
    "admin", "magento", "gitlab", "store", "forum", "post", "product", "order",
}

WORD = re.compile(r"[a-z0-9_]+")


def tokens(text: str) -> set[str]:
    return {w for w in WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 2}


def bundle_tokens(path: Path) -> tuple[str, str, set[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    blob = " ".join(
        [data.get("task_instruction", "")] + list(data.get("success_criteria") or [])
    )
    return data.get("task_id", path.parent.name), data.get("task_instruction", ""), tokens(blob)


def load(root: Path) -> list[tuple[str, str, set[str]]]:
    out = []
    for path in sorted(root.glob("*/task_instruction.json")):
        try:
            out.append(bundle_tokens(path))
        except Exception as exc:  # noqa: BLE001
            print(f"WARN unreadable {path}: {exc}")
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new", required=True, help="new batch site directory")
    parser.add_argument("--prior", required=True, help="prior batch site directory")
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--top", type=int, default=3, help="nearest N prior tasks to show")
    args = parser.parse_args()

    new = load(Path(args.new))
    prior = load(Path(args.prior))
    if not new:
        print(f"no bundles under {args.new}")
        return 0

    flagged = 0
    for task_id, instruction, toks in new:
        scored = sorted(
            ((jaccard(toks, ptoks), pid, pinstr) for pid, pinstr, ptoks in prior),
            reverse=True,
        )[: args.top]
        if scored and scored[0][0] >= args.threshold:
            flagged += 1
            print(f"\nFLAG {task_id}  (max overlap {scored[0][0]:.2f})")
            print(f"  new:   {instruction[:200]}")
            for score, pid, pinstr in scored:
                print(f"  {score:.2f} {pid}")
                print(f"         {pinstr[:200]}")

    print(
        f"\n{flagged}/{len(new)} new bundles flagged at threshold {args.threshold} "
        f"against {len(prior)} prior bundles."
    )
    print("Flagged pairs need a written adjudication in PROGRESS.md; overlap alone is not a verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
