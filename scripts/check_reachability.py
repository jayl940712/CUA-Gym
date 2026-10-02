#!/usr/bin/env python3
"""Click-reachability gate over golden replays (TASK4.md S6).

Batch 3 had four verification conditions and all four tested the *reward*: the
initial lane scores 0.0, the replay lane scores 1.0, the attempts agree, the
verdict is PASS. None of them asked whether the task was solvable **through the
UI**. That is exactly how `reddit_co_moderator_standdown_second_page_seat_002`
shipped: its Remove button sat on page 2 of a moderator table that renders no
pager at all, and the golden replay got there with
`page.goto(_next_page_url(page.url))` -- a URL no user could ever click to. It
scored a clean 0.0 -> 1.0 and was unsolvable by any agent.

What proves reachability
------------------------

A complete proof has two halves, and they live in different places:

* **The controls actually work.** Proved by *executing* the replay: the
  orchestrator runs `initial_setup.py` against a fresh sid, the runner lands the
  lane on `start_path` (`cua_gym_web/runner.py:279` -- verified, the runner does
  the `goto` itself, so a correct replay needs no navigation of its own), the
  replay drives the flow and the reward scores exactly 1.0. That half is already
  covered by Phase 3 verification.

* **Only clicks were used to get there.** *Not* covered by execution -- a typed
  URL executes perfectly. That is this script's job, and it is a static
  property, so it can be decided by reading the replay.

So: a replay that scores 1.0 **and** passes this check is reachable end to end.
Neither half alone is sufficient, which is why batch 3's gate missed the defect.

What counts as typing a URL
---------------------------

* `goto()` -- the agent has no address bar. The runner has already landed the
  page, so any `goto` in a replay is navigation the agent could not perform.
* URL-assembly helpers (`urljoin`, `urlsplit`, ...) and reads of `page.url` that
  feed navigation -- deriving a destination is not clicking to it.
* `new_page()` / `new_context()` -- a fresh page starts blank and can only be
  pointed somewhere by URL.
* `go_back()` **when the replay also navigates by URL**. Back is ordinarily
  safe: if every history entry was reached by clicking, returning to one is a
  click the agent could make. It stops being safe once a typed URL is in the
  history, because back may then land on a page that was never clickable. This
  is decidable: no `goto` in the file => every entry came from a click.

`reload()` is allowed -- it re-fetches the current URL and needs no address bar.

Waivers
-------

S6 permits a `goto` that "proves the same destination is clickable and documents
why the goto is a shortcut for an already-proven path". Mark such a line:

    # REACHABILITY-OK: <reason>

The reason is mandatory; a bare marker does not count. Waivers are reported so
they can be audited rather than silently trusted.

Usage
-----

    python3 scripts/check_reachability.py output/runs
    python3 scripts/check_reachability.py output/runs/<task_id> --quiet
    python3 scripts/check_reachability.py <dir> --expect-fail <task_id>
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

# Playwright navigation the agent cannot perform: it has no address bar.
URL_NAV = {"goto"}

# A blank page can only be pointed somewhere by URL.
PAGE_FACTORY = {"new_page", "new_context"}

# History navigation: safe only when no typed URL is in the history.
HISTORY_NAV = {"go_back", "go_forward"}

# Helpers whose only use in a replay is assembling a URL to navigate to.
URL_HELPERS = {"urljoin", "urlsplit", "urlunsplit", "urlparse", "urlunparse", "quote_plus"}

WAIVER = "REACHABILITY-OK:"


class Finding:
    __slots__ = ("line", "kind", "message")

    def __init__(self, line: int, kind: str, message: str) -> None:
        self.line = line
        self.kind = kind
        self.message = message

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}"


def waiver_reason(lines: list[str], lineno: int) -> str | None:
    """The documented reason on, or immediately above, a line -- if any.

    A bare `# REACHABILITY-OK:` with no reason is deliberately not a waiver: S6
    requires the replay to *document* why the destination is already proven
    clickable.
    """
    for index in (lineno - 1, lineno - 2):
        if 0 <= index < len(lines) and WAIVER in lines[index]:
            reason = lines[index].partition(WAIVER)[2].strip()
            if reason:
                return reason
    return None


def scan(code: str) -> tuple[list[Finding], list[str]]:
    """Return (findings, waivers) for one replay source."""
    lines = code.splitlines()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [Finding(getattr(exc, "lineno", 0) or 0, "parse",
                        f"golden_replay.py does not parse: {exc}")], []

    findings: list[Finding] = []
    waivers: list[str] = []
    url_nav_lines: list[int] = []

    for node in ast.walk(tree):
        # import urljoin / from urllib.parse import urlsplit
        if isinstance(node, ast.alias):
            base = (node.asname or node.name).split(".")[-1]
            if base in URL_HELPERS:
                findings.append(Finding(
                    getattr(node, "lineno", 0),
                    "url_assembly",
                    f"imports {base!r}, a URL-assembly helper; a replay that builds "
                    "URLs is deriving destinations, not clicking to them",
                ))
            continue

        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        attr = node.func.attr

        if attr in URL_NAV:
            reason = waiver_reason(lines, node.lineno)
            if reason:
                waivers.append(f"line {node.lineno}: {reason}")
            else:
                url_nav_lines.append(node.lineno)
                findings.append(Finding(
                    node.lineno, "url_nav",
                    "goto() navigates by URL, but the runner already landed the lane "
                    "on start_path and the agent has no address bar. Reach the page by "
                    "clicking, or add `# REACHABILITY-OK: <reason>` proving the "
                    "destination is already clickable",
                ))
        elif attr in PAGE_FACTORY:
            findings.append(Finding(
                node.lineno, "new_page",
                f"{attr}() opens a blank page, which can only be pointed somewhere by "
                "URL; drive the lane's existing page instead",
            ))
        elif attr in HISTORY_NAV:
            # Recorded now, judged below: back is only unsafe once a typed URL
            # can be in the history.
            findings.append(Finding(node.lineno, "history_nav", f"{attr}()"))

    # `page.url` read anywhere in a replay that also navigates by URL means the
    # destination was computed from the current location rather than clicked.
    if url_nav_lines:
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "url" and isinstance(node.ctx, ast.Load):
                findings.append(Finding(
                    node.lineno, "derived_url",
                    "reads `page.url` in a replay that also navigates by URL, so the "
                    "destination was derived from the current location, not clicked to",
                ))
                break

    # Resolve the history-nav findings: safe iff nothing typed a URL.
    resolved: list[Finding] = []
    for finding in findings:
        if finding.kind != "history_nav":
            resolved.append(finding)
            continue
        if url_nav_lines:
            resolved.append(Finding(
                finding.line, "history_nav",
                f"{finding.message} after a URL navigation (line {url_nav_lines[0]}); "
                "back may return to a page that was never clickable",
            ))
        # else: every history entry was reached by clicking -- allowed.
    resolved.sort(key=lambda f: f.line)
    return resolved, waivers


def find_replay(run_dir: Path) -> Path | None:
    direct = run_dir / "golden_replay.py"
    if direct.is_file():
        return direct
    nested = sorted(run_dir.glob("**/golden_replay.py"))
    return nested[0] if nested else None


def check_target(target: Path) -> tuple[list[str], list[str]]:
    """Scan one replay, given either its file or its run directory."""
    replay = target if target.is_file() else find_replay(target)
    if replay is None:
        return ["no golden_replay.py — reachability is unproven"], []
    findings, waivers = scan(replay.read_text(encoding="utf-8", errors="replace"))
    return [str(f) for f in findings], waivers


def collect_targets(roots: list[str]) -> list[Path]:
    """Replay sources under `roots`.

    Two layouts exist and both must work, because a silent "nothing to check"
    is worse than a failure: it exits 0 and reads as a pass.

    * **Verification layout** — `output/runs/<task_id>/golden_replay.py`, what
      the orchestrator produces.
    * **Authoring layout** — `_batches/<slug>/replays/<task_id>.py`, what a lane
      writes while drafting. Authors are told to check this directory, so it has
      to be understood or the instruction is a no-op.
    """
    targets: list[Path] = []
    for raw in roots:
        root = Path(raw).resolve()
        if not root.is_dir():
            if root.is_file() and root.suffix == ".py":
                targets.append(root)
            else:
                print(f"warning: {root} is not a directory", file=sys.stderr)
            continue
        # A single run directory.
        if find_replay(root) is not None and root.name != "runs":
            targets.append(root)
            continue
        # A directory of loose replay .py files (authoring layout).
        loose = sorted(p for p in root.glob("*.py") if p.name != "__init__.py")
        if loose:
            targets.extend(loose)
            continue
        # Otherwise a parent of run directories.
        targets.extend(sorted(p for p in root.iterdir() if p.is_dir()))
    return list(dict.fromkeys(targets))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("roots", nargs="+", help="output/runs, or single run directories")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    parser.add_argument("--json", dest="json_out", help="write the full report here")
    parser.add_argument(
        "--expect-fail",
        action="append",
        default=[],
        metavar="TASK_ID",
        help="task_id that MUST fail; proves the checker still discriminates",
    )
    args = parser.parse_args()

    runs = collect_targets(args.roots)
    report: dict[str, dict] = {}
    failed: list[str] = []
    waived: list[str] = []

    for run_dir in runs:
        problems, waivers = check_target(run_dir)
        name = run_dir.stem if run_dir.is_file() else run_dir.name
        report[name] = {"problems": problems, "waivers": waivers}
        if problems:
            failed.append(name)
            print(f"UNREACHABLE {name}")
            for problem in problems:
                print(f"     - {problem}")
        else:
            if waivers:
                waived.append(name)
            if not args.quiet:
                print(f"REACHABLE   {name}")
        for waiver in waivers:
            print(f"     ~ waived {waiver}")

    if not runs:
        print(
            f"NOTHING TO CHECK under {', '.join(args.roots)} — no golden_replay.py and "
            "no loose replay .py files were found.\n"
            "This is reported as a FAILURE on purpose: an empty scan that exits 0 reads "
            "as a pass, and reachability would then be silently unproven."
        )
        return 1

    passed = len(runs) - len(failed)
    print(f"\n{passed}/{len(runs)} replays reach every scored control by clicking")
    if waived:
        print(f"{len(waived)} carry documented goto waivers — audit them: {', '.join(sorted(waived))}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    status = 1 if failed else 0
    for task_id in args.expect_fail:
        if report.get(task_id, {}).get("problems"):
            print(f"OK: {task_id} failed as expected — the checker discriminates")
        elif task_id not in report:
            print(f"BROKEN CHECKER: {task_id} was expected to fail but was not scanned")
            status = 2
        else:
            print(f"BROKEN CHECKER: {task_id} was expected to fail and passed")
            status = 2
    return status


if __name__ == "__main__":
    raise SystemExit(main())
