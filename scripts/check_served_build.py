#!/usr/bin/env python3
"""Warn when a mock's `src/` is newer than the `dist/` actually being served.

The hub runs `vite preview`, which serves the **prebuilt `dist/`** directory.
It does not read `src/`. So a source file edited after the last build is
invisible to every agent, every replay and every rollout — while still being
perfectly readable by an authoring agent doing its research.

That gap produced a concrete near-miss while planning batch 5. A census read
`Comment.jsx` in `src/`, found no moderator branch, and separately reported
that "Mod trash" appears in the user menu — a claim true of `src/` and false of
the served bundle, where the string occurs zero times. Source-reading is the
main research method for authoring, so this failure mode is always available.

**The served build is the environment.** Do not rebuild `dist/` to close the
gap: `hub/` is read-only by contract (TASK4 S2/S7), and more importantly the
training rollouts serve the same `dist/`, so authoring against a rebuilt bundle
would produce tasks that do not match the deployment agents actually see. Treat
a newer `src/` as a fact to design around, exactly as TASK4 S2 says.

Exit 0 when every mock's dist is at least as new as its src, 1 otherwise. The
listed files are the ones whose source changes are NOT live.

    python3 scripts/check_served_build.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HUB = Path("hub/websites")
SITES = (
    "webarena_gitlab_mock",
    "webarena_reddit_mock",
    "webarena_shopping_mock",
    "webarena_shopping_admin_mock",
)
# Build noise and test residue, not application source.
IGNORE = (".pytest_cache", "__pycache__", "node_modules", ".vite")

SOURCE_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".html"}


def stale_sources(site: Path) -> list[Path]:
    dist = site / "dist"
    if not dist.is_dir():
        return []
    built = dist.stat().st_mtime
    out = []
    for path in (site / "src").rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORE for part in path.parts):
            continue
        if path.stat().st_mtime > built:
            out.append(path)
    return sorted(out)


def main() -> int:
    problems = 0
    for name in SITES:
        site = HUB / name
        if not site.is_dir():
            print(f"warning: {site} not found", file=sys.stderr)
            continue
        stale = stale_sources(site)
        if not stale:
            print(f"ok    {name}: served dist is current")
            continue
        problems += 1
        print(f"STALE {name}: {len(stale)} source file(s) newer than the served dist")
        for path in stale:
            print(f"    - {path.relative_to(site)}")
        print("      Changes in these files are NOT live. Verify any claim that")
        print("      depends on them against the running app, not against src/.")
    if problems:
        print(
            f"\n{problems} mock(s) are serving a build older than their source.\n"
            "This is reported, not fixed: `hub/` is read-only and the training\n"
            "rollouts serve the same dist, so the served build is the ground truth."
        )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
